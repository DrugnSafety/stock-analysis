"""News API client — NewsAPI.org + NewsAPI.ai + Finnhub aggregator.

Fetches 1-year news for ticker from multiple sources, deduplicates, classifies impact.

Setup (all optional, graceful fallback to curated data):
  - NewsAPI.org:   https://newsapi.org/register → 100 calls/day free, 30-day lookback
  - NewsAPI.ai:    https://newsapi.ai/register → 2000 tokens free, 1-year lookback, UUID key format
  - Finnhub:       https://finnhub.io/register → 60 calls/min free

Add to .env:
  NEWSAPI_KEY=...        # newsapi.org (32-char hex)
  NEWSAPI_AI_KEY=...     # newsapi.ai (UUID format)
  FINNHUB_KEY=...
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cache" / "news_integration"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _read_env_key(key: str) -> Optional[str]:
    """Load API key from env or .env file."""
    v = os.environ.get(key)
    if v:
        return v

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    candidates = [Path.cwd() / ".env"]
    if project_dir:
        candidates.append(Path(project_dir) / ".env")
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / ".env")

    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.strip().startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _newsapi_key() -> Optional[str]:
    return _read_env_key("NEWSAPI_KEY")


def _newsapi_ai_key() -> Optional[str]:
    """NewsAPI.ai (Event Registry) — UUID-format key."""
    return _read_env_key("NEWSAPI_AI_KEY")


def _finnhub_key() -> Optional[str]:
    return _read_env_key("FINNHUB_KEY")


def _cache_fresh(path: Path, ttl_hours: int = 24) -> bool:
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl_hours * 3600


# ── NewsAPI ────────────────────────────────────────────────────────────
def _fetch_newsapi(query: str, lookback_days: int) -> list[dict]:
    """Fetch news via NewsAPI everything endpoint."""
    key = _newsapi_key()
    if not key:
        return []

    import requests
    end_date = datetime.now()
    start_date = end_date - timedelta(days=min(lookback_days, 30))  # NewsAPI free tier limit

    try:
        r = requests.get("https://newsapi.org/v2/everything", params={
            "q": query,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "language": "en",
            "sortBy": "relevancy",
            "pageSize": 30,
            "apiKey": key,
        }, timeout=15)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[news] NewsAPI failed: {e}")
        return []

    items = []
    for art in data.get("articles", []):
        items.append({
            "date": (art.get("publishedAt") or "")[:10],
            "type": "뉴스",
            "category": art.get("source", {}).get("name", "News"),
            "headline": art.get("title", "")[:140],
            "summary": (art.get("description") or "")[:200],
            "source": f"NewsAPI · {art.get('source', {}).get('name', '-')}",
            "url": art.get("url", ""),
            "impact": _classify_news_impact(art.get("title", "") + " " + (art.get("description") or "")),
        })
    return items


# ── NewsAPI.ai (Event Registry) ───────────────────────────────────────
def _fetch_newsapi_ai(query: str, lookback_days: int) -> list[dict]:
    """Fetch news via NewsAPI.ai (Event Registry) — supports 1-year lookback (vs newsapi.org 30-day).

    API doc: https://eventregistry.org/documentation
    Endpoint: POST https://eventregistry.org/api/v1/article/getArticles
    Free tier: 2000 tokens, paid plans available.
    """
    key = _newsapi_ai_key()
    if not key:
        return []

    import requests
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    try:
        # POST body for getArticles
        body = {
            "action": "getArticles",
            "keyword": query,
            "lang": "eng",
            "articlesPage": 1,
            "articlesCount": 50,
            "articlesSortBy": "rel",  # relevance
            "dataType": ["news", "blog"],
            "dateStart": start_date.strftime("%Y-%m-%d"),
            "dateEnd": end_date.strftime("%Y-%m-%d"),
            "apiKey": key,
            "resultType": "articles",
            "includeArticleConcepts": False,
            "includeArticleCategories": False,
        }
        r = requests.post("https://eventregistry.org/api/v1/article/getArticles", json=body, timeout=25)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        print(f"[news] NewsAPI.ai failed: {e}")
        return []

    items = []
    articles_obj = data.get("articles", {})
    if isinstance(articles_obj, dict):
        results = articles_obj.get("results", [])
    elif isinstance(articles_obj, list):
        results = articles_obj
    else:
        results = []

    for art in results:
        title = art.get("title", "")
        body_t = art.get("body", "") or ""
        items.append({
            "date": (art.get("date") or art.get("dateTime") or "")[:10],
            "type": "뉴스",
            "category": (art.get("source") or {}).get("title", "NewsAPI.ai"),
            "headline": title[:140],
            "summary": body_t[:200],
            "source": f"NewsAPI.ai · {(art.get('source') or {}).get('title', '-')}",
            "url": art.get("url", ""),
            "impact": _classify_news_impact(title + " " + body_t),
        })
    return items


# ── Finnhub ────────────────────────────────────────────────────────────
def _fetch_finnhub(ticker: str, lookback_days: int) -> list[dict]:
    """Fetch news via Finnhub company-news endpoint."""
    key = _finnhub_key()
    if not key:
        return []

    import requests
    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    try:
        r = requests.get("https://finnhub.io/api/v1/company-news", params={
            "symbol": ticker,
            "from": start_date.strftime("%Y-%m-%d"),
            "to": end_date.strftime("%Y-%m-%d"),
            "token": key,
        }, timeout=15)
        r.raise_for_status()
        articles = r.json()
    except Exception as e:
        print(f"[news] Finnhub failed: {e}")
        return []

    items = []
    for art in articles[:50]:  # cap at 50
        # datetime is unix timestamp
        dt = datetime.fromtimestamp(art.get("datetime", 0))
        items.append({
            "date": dt.strftime("%Y-%m-%d"),
            "type": "뉴스",
            "category": art.get("category", "company"),
            "headline": art.get("headline", "")[:140],
            "summary": (art.get("summary") or "")[:200],
            "source": f"Finnhub · {art.get('source', '-')}",
            "url": art.get("url", ""),
            "impact": _classify_news_impact(art.get("headline", "") + " " + (art.get("summary") or "")),
        })
    return items


# ── Impact classifier ──────────────────────────────────────────────────
def _classify_news_impact(text: str) -> str:
    """Keyword-based classifier — replace with LLM in Phase 2."""
    text_upper = (text or "").upper()

    pos_kw = [
        "BEAT", "EXCEED", "RAISE", "RAISES", "HIGHER", "RECORD HIGH", "ALL-TIME HIGH",
        "ACQUIRE", "ACQUISITION", "MERGER", "PARTNERSHIP", "DEAL",
        "BUYBACK", "REPURCHASE", "DIVIDEND INCREASE", "SPECIAL DIVIDEND",
        "GROWTH", "STRONG", "PROFIT", "PROFITS", "EARNINGS BEAT",
        "UPGRADE", "OUTPERFORM", "OVERWEIGHT", "BUY RATING",
        "AWARD", "WINS", "CONTRACT", "EXPANSION", "NEW PRODUCT", "LAUNCH",
        "APPROVED", "APPROVAL", "PATENT",
    ]
    neg_kw = [
        "MISS", "MISSES", "FAIL", "DOWNGRADE", "UNDERPERFORM", "UNDERWEIGHT", "SELL RATING",
        "LOSS", "LOSSES", "PROFIT WARNING", "GUIDANCE CUT", "LOWERED",
        "INVESTIGATION", "PROBE", "FRAUD", "LAWSUIT", "SUED",
        "RECALL", "DEFECT", "SAFETY", "HACK", "BREACH",
        "BANKRUPTCY", "DEFAULT", "DELISTING", "GOING CONCERN", "LAYOFF", "LAYOFFS", "FIRED",
        "RESIGNATION", "RESIGNS", "STEPS DOWN", "OUSTED",
        "STRIKE", "WORKERS", "DISPUTE",
        "DROP", "PLUNGE", "TUMBLE", "CRASH", "FALLS",
    ]

    pos_count = sum(1 for kw in pos_kw if kw in text_upper)
    neg_count = sum(1 for kw in neg_kw if kw in text_upper)

    if pos_count > neg_count and pos_count > 0:
        return "+"
    elif neg_count > pos_count and neg_count > 0:
        return "-"
    return "○"


# ── Public API ─────────────────────────────────────────────────────────
def fetch_news(ticker: str, company_name: str = "", lookback_days: int = 365) -> list[dict]:
    """Fetch 1-year news for ticker.

    Order of preference: Finnhub (better) → NewsAPI → empty (let caller fallback).
    """
    cache_path = CACHE_DIR / f"news_{ticker.replace('.', '_')}.json"
    if _cache_fresh(cache_path, ttl_hours=24):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    items: list[dict] = []
    query = company_name if company_name else ticker

    # 1. Finnhub (preferred — better company filter)
    if _finnhub_key():
        finnhub_items = _fetch_finnhub(ticker, lookback_days)
        items.extend(finnhub_items)

    # 2. NewsAPI.ai (Event Registry) — 1-year lookback, supports keyword search
    if _newsapi_ai_key():
        ai_items = _fetch_newsapi_ai(query, lookback_days)
        items.extend(ai_items)

    # 3. NewsAPI.org (supplementary, 30-day cap)
    if _newsapi_key():
        newsapi_items = _fetch_newsapi(query, lookback_days)
        items.extend(newsapi_items)

    # Deduplicate by headline
    seen = set()
    deduped = []
    for it in items:
        h = it.get("headline", "")[:80]
        if h and h not in seen:
            seen.add(h)
            deduped.append(it)

    deduped.sort(key=lambda x: x.get("date", ""), reverse=True)
    if deduped:
        cache_path.write_text(json.dumps(deduped, ensure_ascii=False, indent=2))
    return deduped


def get_status() -> dict:
    return {
        "newsapi_configured": _newsapi_key() is not None,
        "newsapi_ai_configured": _newsapi_ai_key() is not None,
        "finnhub_configured": _finnhub_key() is not None,
        "any_active": (_newsapi_key() or _newsapi_ai_key() or _finnhub_key()) is not None,
        "cache_dir": str(CACHE_DIR),
    }


if __name__ == "__main__":
    import sys
    print("News integration status:", json.dumps(get_status(), ensure_ascii=False, indent=2))
    if len(sys.argv) > 1:
        items = fetch_news(sys.argv[1], company_name=sys.argv[2] if len(sys.argv) > 2 else "")
        print(f"\n{sys.argv[1]} news (1Y): {len(items)} items")
        for it in items[:8]:
            print(f"  {it['date']} {it['impact']} {it['headline'][:80]}")
