"""Evidence Retriever — Phase 7 절차 A (외부 근거 강화 / AMEET-style Evidence Layer).

목적
----
기존 deep_research가 LLM 추론으로 채우던 산업·경쟁·카탈리스트·리스크 맥락을,
**출처 URL이 박힌 외부 1차 자료**로 수집·정규화하여 evidence/{ticker}.json 으로 격리 저장한다.
이후 deep_research / build_combined 파이프라인이 이 evidence를 anchor로 사용한다.

설계 원칙
--------
1. **무료 소스만** (사용자 bigdata.com 계정 없음). 소스 우선순위:
     ① WebSearch hits (agent 주입)  → breadth backbone
     ② SEC EDGAR full-text (EFTS)   → 미국 1차 공시
     ③ news-integration / DART      → 기존 plugin 재사용
   bigdata.com 구독 확보 시 `register_source()` 로 소스 ⓪ prepend 만 하면 됨 (pluggable).

2. **모든 evidence record 는 source_url 필수.** URL 없는 항목은 evidence 가 아니라 'assertion'으로
   분류되어 fact-check(절차 B) 단계에서 ⚠️ 플래그 대상이 된다.

3. WebSearch 는 agent(Claude)의 도구이므로 Python 에서 직접 호출 불가 →
   agent 가 검색 결과를 `WebSearchHit` 리스트로 주입하는 구조(`from_websearch_hits`).
   SEC/news/DART 는 Python-callable HTTP 라 모듈이 직접 fetch.

사용 예
------
    from evidence_retriever import EvidenceRetriever, WebSearchHit

    er = EvidenceRetriever("BTU", exchange="NYSE")
    er.add_websearch_hits([
        WebSearchHit(category="catalyst", claim="...", value="...",
                     source_url="https://...", publisher="...", date="2026-05-05",
                     impact="+"),
        ...
    ])
    er.fetch_sec_efts(forms=["8-K", "10-Q"])     # graceful: 네트워크 없으면 skip
    er.write(pipeline_dir / "evidence")           # evidence/BTU.json
    audit = er.audit_deep_research(deep_research_dict)   # 무출처 항목 진단
"""
from __future__ import annotations

import json
import re
import sys
import urllib.parse
import urllib.request
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Optional

EVIDENCE_SCHEMA_VERSION = "1.0"

VALID_CATEGORIES = {
    "industry",     # 산업 구조·시장규모
    "competitor",   # 경쟁 구도
    "catalyst",     # 향후 이벤트
    "risk",         # 리스크
    "financials",   # 재무·실적
    "valuation",    # 밸류에이션·애널리스트
    "macro",        # 거시·정책
    "esg",          # ESG·규제
}


@dataclass
class WebSearchHit:
    """Agent(WebSearch)가 주입하는 1건의 근거."""
    category: str
    claim: str                      # 핵심 주장(한국어 가능)
    value: str                      # 정량 값/요지 ("met-coal $207/t", "FY met 10.3-11.3Mt")
    source_url: str                 # 필수 — 검증 원문 링크
    publisher: str = ""             # 매체/기관 ("EIA", "SEC 8-K", "Argus")
    date: str = ""                  # ISO yyyy-mm-dd (가능하면)
    impact: str = "?"               # +, -, ?, ○
    retrieved_via: str = "websearch"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _norm_url(u: str) -> str:
    """dedup 용 URL 정규화 (query·fragment·trailing slash 제거)."""
    try:
        p = urllib.parse.urlsplit(u.strip())
        path = p.path.rstrip("/")
        return f"{p.netloc}{path}".lower()
    except Exception:
        return u.strip().lower()


class EvidenceRetriever:
    """종목 1개에 대한 외부 근거 수집기."""

    def __init__(self, ticker: str, exchange: str = "", company: str = ""):
        self.ticker = ticker
        self.exchange = exchange
        self.company = company
        self._records: list[dict] = []
        self._seen: set[tuple[str, str]] = set()      # (category, norm_url+value)
        self._extra_sources: list[Callable[["EvidenceRetriever"], None]] = []

    # ── 소스 ① WebSearch hits (backbone) ──────────────────────────────
    def add_websearch_hits(self, hits: list[WebSearchHit]) -> int:
        added = 0
        for h in hits:
            if h.category not in VALID_CATEGORIES:
                # 모르는 카테고리는 버리지 않고 'industry'로 흡수 + 경고
                sys.stderr.write(f"[evidence] unknown category '{h.category}' → industry\n")
                h.category = "industry"
            if not h.source_url or not h.source_url.startswith("http"):
                sys.stderr.write(f"[evidence] SKIP (no url): {h.claim[:50]}\n")
                continue
            key = (h.category, _norm_url(h.source_url) + "|" + h.value[:40])
            if key in self._seen:
                continue
            self._seen.add(key)
            self._records.append(asdict(h))
            added += 1
        return added

    # ── 소스 ② SEC EDGAR full-text search (무료, python-callable) ──────
    def fetch_sec_efts(self, forms: Optional[list[str]] = None, limit: int = 10,
                       lookback_days: int = 400) -> int:
        """SEC EDGAR EFTS 전문검색. 네트워크/차단 시 graceful skip (0 반환).

        lookback_days: 최근 N일 공시만 (EFTS는 관련도순 반환이라 날짜필터로 구 공시 배제).
        """
        from datetime import timedelta
        forms = forms or ["8-K", "10-Q", "10-K"]
        today = datetime.now(timezone.utc).date()
        startdt = (today - timedelta(days=lookback_days)).isoformat()
        enddt = today.isoformat()
        q = urllib.parse.quote(f'"{self.company or self.ticker}"')
        url = (
            "https://efts.sec.gov/LATEST/search-index?q="
            + q + "&forms=" + ",".join(forms)
            + f"&startdt={startdt}&enddt={enddt}"
        )
        req = urllib.request.Request(
            url, headers={"User-Agent": "stock-analysis-evidence/1.0 (research@example.com)"}
        )
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode("utf-8"))
        except Exception as e:                       # noqa: BLE001 — graceful
            sys.stderr.write(f"[evidence] SEC EFTS skip ({type(e).__name__})\n")
            return 0
        hits = data.get("hits", {}).get("hits", []) or []
        # 날짜 내림차순 정렬 (EFTS 관련도순 → 최신 공시 우선)
        hits.sort(key=lambda h: h.get("_source", {}).get("file_date", ""), reverse=True)
        added = 0
        for hit in hits[:limit]:
            src = hit.get("_source", {})
            adsh = src.get("adsh", "").replace("-", "")
            cik = (src.get("ciks") or [""])[0]
            form = src.get("file_type", "?")
            date = src.get("file_date", "")
            link = (
                f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh}/"
                if cik and adsh else "https://www.sec.gov/cgi-bin/browse-edgar"
            )
            self._records.append({
                "category": "financials",
                "claim": f"{form} 공시 ({date})",
                "value": (src.get("display_names") or [""])[0],
                "source_url": link, "publisher": f"SEC {form}", "date": date,
                "impact": "?", "retrieved_via": "sec_efts",
            })
            added += 1
        return added

    # ── 소스 ③ DART (한국 종목 공시, 무료) ────────────────────────────
    def fetch_dart(self, lookback_days: int = 365, limit: int = 10) -> int:
        """한국(.KS/.KQ) 종목 DART 공시를 evidence record 로 정규화. graceful skip."""
        if not self.ticker.endswith((".KS", ".KQ")):
            return 0
        # dart-integration plugin 재사용 (one-off 금지 원칙)
        dart_scripts = (
            Path(__file__).resolve().parent.parent.parent.parent
            / "dart-integration" / "scripts"
        )
        if str(dart_scripts) not in sys.path:
            sys.path.insert(0, str(dart_scripts))
        try:
            from dart_client import fetch_disclosures   # type: ignore
        except Exception as e:                          # noqa: BLE001
            sys.stderr.write(f"[evidence] DART client import 실패: {e}\n")
            return 0
        try:
            items = fetch_disclosures(self.ticker, lookback_days=lookback_days) or []
        except Exception as e:                          # noqa: BLE001
            sys.stderr.write(f"[evidence] DART fetch skip ({type(e).__name__})\n")
            return 0
        items.sort(key=lambda x: x.get("date", ""), reverse=True)
        added = 0
        for d in items[:limit]:
            rcept = d.get("rcept_no")
            url = (f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={rcept}"
                   if rcept else "https://dart.fss.or.kr")
            self._records.append({
                "category": "financials",
                "claim": d.get("headline", d.get("category", "공시")),
                "value": d.get("summary", ""),
                "source_url": url,
                "publisher": "DART",
                "date": d.get("date", ""),
                "impact": d.get("impact", "?"),
                "retrieved_via": "dart",
            })
            added += 1
        return added

    # ── 소스 ⓪ pluggable (bigdata.com 등 향후 prepend) ────────────────
    def register_source(self, fn: Callable[["EvidenceRetriever"], None]) -> None:
        """추가 소스를 등록. fn(self) 안에서 self._records.append(...) 하면 됨."""
        self._extra_sources.append(fn)

    def run_registered_sources(self) -> None:
        for fn in self._extra_sources:
            try:
                fn(self)
            except Exception as e:                   # noqa: BLE001
                sys.stderr.write(f"[evidence] registered source 실패: {e}\n")

    # ── 출력 ──────────────────────────────────────────────────────────
    def to_dict(self) -> dict:
        by_cat: dict[str, list[dict]] = {}
        for rec in self._records:
            by_cat.setdefault(rec["category"], []).append(rec)
        return {
            "ticker": self.ticker,
            "exchange": self.exchange,
            "company": self.company,
            "schema_version": EVIDENCE_SCHEMA_VERSION,
            "retrieved_at": _now_iso(),
            "source_priority": ["websearch", "sec_efts", "news", "dart"],
            "counts": {k: len(v) for k, v in by_cat.items()},
            "total": len(self._records),
            "by_category": by_cat,
            "records": self._records,
        }

    def write(self, evidence_dir: Path) -> Path:
        evidence_dir.mkdir(parents=True, exist_ok=True)
        out = evidence_dir / f"{self.ticker}.json"
        out.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return out

    # ── deep_research 주입 / 감사 ─────────────────────────────────────
    def to_deep_research_news(self) -> list[dict]:
        """evidence → deep_research industry.news 포맷(URL 포함)으로 변환."""
        out = []
        for rec in self._records:
            if rec["category"] in ("catalyst", "macro", "industry", "esg", "valuation"):
                out.append({
                    "date": rec.get("date", ""),
                    "title": rec["claim"],
                    "source": rec.get("publisher", ""),
                    "url": rec["source_url"],            # ← 기존엔 없던 필드
                    "summary": rec["value"],
                    "impact_reason": rec.get("impact", "?"),
                })
        return sorted(out, key=lambda x: x.get("date", ""), reverse=True)

    @staticmethod
    def merge_into_deep(deep: dict, evidence_path: Path) -> dict:
        """evidence/{ticker}.json 을 deep_research dict 의 industry.news 에 병합(URL 포함).

        build 파이프라인이 호출. evidence 파일 없으면 deep 그대로 반환(graceful).
        - URL 있는 evidence news 를 기존 news **앞**에 prepend (출처 우선)
        - market_size 에 source 부재 시 evidence industry 출처로 보강
        - deep['_evidence'] 메타 기록 (주입 여부·건수)
        """
        if not deep or not evidence_path.exists():
            return deep
        try:
            ev = json.loads(evidence_path.read_text(encoding="utf-8"))
        except Exception:
            return deep
        by_cat = ev.get("by_category", {})
        ev_news = []
        for cat in ("catalyst", "macro", "industry", "esg", "valuation"):
            for r in by_cat.get(cat, []):
                if not r.get("source_url"):
                    continue
                ev_news.append({
                    "date": r.get("date", ""),
                    "title": r["claim"],
                    "source": r.get("publisher", ""),
                    "url": r["source_url"],
                    "summary": r.get("value", ""),
                    "impact_reason": r.get("impact", "?"),
                })
        ev_news.sort(key=lambda x: x.get("date", ""), reverse=True)
        ind = deep.setdefault("industry", {})
        existing = ind.get("news", []) or []
        # dedup by title prefix
        seen = {n.get("title", "")[:30] for n in ev_news}
        merged = ev_news + [n for n in existing if n.get("title", "")[:30] not in seen]
        ind["news"] = merged
        # market_size 출처 보강
        ms = ind.get("market_size")
        if isinstance(ms, dict) and not ms.get("source") and by_cat.get("industry"):
            ms["source"] = by_cat["industry"][0].get("source_url", "")
        deep["_evidence"] = {
            "injected": True,
            "evidence_total": ev.get("total", 0),
            "news_with_url": len(ev_news),
            "retrieved_at": ev.get("retrieved_at", ""),
        }
        return deep

    @staticmethod
    def annotate_scenarios(deep: dict, evidence_path: Path) -> dict:
        """scenarios.key_assumptions 각 가정에 뒷받침/반박 evidence 출처 배지 부착.

        bull 가정 + (+)evidence = ✓출처, bull 가정 + (-)evidence = ⚠반박.
        가정 문자열에 HTML 배지를 append (deep_research <li>{a}</li> 렌더와 호환).
        원본은 _key_assumptions_raw 에 보존. evidence 없으면 graceful.
        """
        if not deep or not evidence_path.exists():
            return deep
        try:
            ev = json.loads(evidence_path.read_text(encoding="utf-8"))
        except Exception:
            return deep
        recs = ev.get("records", [])
        pos = [r for r in recs if r.get("impact") == "+"]
        neg = [r for r in recs if r.get("impact") == "-"]

        def _tok(s: str) -> set:
            s = re.sub(r"[^\w가-힣% ]", " ", s.lower())
            return {t for t in s.split() if len(t) >= 2}

        def _best(atok: set, pool: list) -> Optional[dict]:
            best, score = None, 1   # 최소 2개 겹침
            for r in pool:
                ov = len(atok & (_tok(r.get("claim", "")) | _tok(r.get("value", ""))))
                if ov > score:
                    best, score = r, ov
            return best

        scen = deep.get("scenarios", {})
        annotated = 0
        for sc_name in ("bull", "base", "bear"):
            sc = scen.get(sc_name)
            if not isinstance(sc, dict):
                continue
            asms = sc.get("key_assumptions") or []
            if not asms or "_key_assumptions_raw" in sc:
                continue
            sc["_key_assumptions_raw"] = list(asms)
            new_asms = []
            for a in asms:
                atok = _tok(a)
                refute = _best(atok, neg)        # 반박 우선 표기
                support = _best(atok, pos)
                badge = ""
                if refute:
                    badge = (f' <a href="{refute["source_url"]}" '
                             f'style="color:#dc2626;font-size:7.5pt;text-decoration:none;">'
                             f'⚠반박:{refute.get("publisher","")}↗</a>')
                elif support:
                    badge = (f' <a href="{support["source_url"]}" '
                             f'style="color:#16a34a;font-size:7.5pt;text-decoration:none;">'
                             f'✓{support.get("publisher","")}↗</a>')
                if badge:
                    annotated += 1
                new_asms.append(a + badge)
            sc["key_assumptions"] = new_asms
        deep.setdefault("_evidence", {})["scenarios_annotated"] = annotated
        return deep

    @staticmethod
    def audit_deep_research(deep: dict) -> dict:
        """기존 deep_research의 무출처 주장 비율 진단 (절차 B 의 사전 단계)."""
        ind = deep.get("industry", {})
        news = ind.get("news", [])
        news_total = len(news)
        news_with_url = sum(1 for n in news if n.get("url"))
        ms = ind.get("market_size", {})
        ms_sourced = bool(ms.get("source") or ms.get("url"))
        meta = deep.get("research_meta", {})
        return {
            "news_total": news_total,
            "news_with_url": news_with_url,
            "news_unsourced_pct": round(100 * (news_total - news_with_url) / news_total, 1)
            if news_total else 0.0,
            "market_size_sourced": ms_sourced,
            "research_meta_empty": (not meta),
            "verdict": "LLM-generated (출처 미검증)" if news_with_url == 0
            else "부분 출처",
        }
