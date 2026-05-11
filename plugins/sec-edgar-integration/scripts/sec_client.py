"""SEC EDGAR Open Data API client — 미국 상장사 공시·재무제표 자동 fetch.

API base: https://data.sec.gov / https://www.sec.gov/cgi-bin/browse-edgar
- API key 불필요
- User-Agent header 필수 (이메일 주소 포함 권장)
- Rate limit: 10 req/sec
- Free, unlimited

Endpoints:
  /submissions/CIK{cik}.json          — 회사 메타 + recent filings
  /api/xbrl/companyfacts/CIK{cik}.json — XBRL 재무 facts
  /api/xbrl/companyconcept/CIK{cik}/us-gaap/{tag}.json — 단일 concept

Cache:
  ~/.cache/sec_edgar/ — ticker_cik_map.json (TTL 30일),
  filings_{ticker}.json (24h), facts_{ticker}.json (7일)
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cache" / "sec_edgar"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Note: User-Agent must be ASCII (latin-1 compatible) per HTTP/SEC spec
DEFAULT_UA = "stock-analysis-system/1.0 (mingyu.kang@research.local)"


def _user_agent() -> str:
    """Return User-Agent header value. Required by SEC."""
    ua = os.environ.get("SEC_USER_AGENT")
    if ua:
        return ua

    # Try .env file
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    candidates = [Path.cwd() / ".env"]
    if project_dir:
        candidates.append(Path(project_dir) / ".env")
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / ".env")

    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.strip().startswith("SEC_USER_AGENT="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return DEFAULT_UA


def _request(url: str, timeout: int = 20) -> dict | None:
    """Make SEC API request with required User-Agent."""
    import requests
    try:
        r = requests.get(url, headers={
            "User-Agent": _user_agent(),
            "Accept-Encoding": "gzip, deflate",
            "Host": "data.sec.gov" if "data.sec.gov" in url else "www.sec.gov",
        }, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[sec] request failed: {e}")
        return None


def _cache_fresh(path: Path, ttl_hours: int = 24) -> bool:
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl_hours * 3600


# ── Ticker → CIK lookup ────────────────────────────────────────────────
_TICKER_MAP_CACHE: dict | None = None


def _load_ticker_map() -> dict:
    """Download SEC ticker.txt → CIK mapping (cached 30 days)."""
    global _TICKER_MAP_CACHE
    if _TICKER_MAP_CACHE is not None:
        return _TICKER_MAP_CACHE

    cache_path = CACHE_DIR / "ticker_cik_map.json"
    if _cache_fresh(cache_path, ttl_hours=24 * 30):
        _TICKER_MAP_CACHE = json.loads(cache_path.read_text())
        return _TICKER_MAP_CACHE

    # Fetch from SEC
    data = _request("https://www.sec.gov/files/company_tickers.json")
    if not data:
        return {}

    # Format: {"0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}, ...}
    mapping = {}
    for entry in data.values():
        ticker = entry.get("ticker", "").upper()
        cik = str(entry.get("cik_str", "")).zfill(10)  # CIK with leading zeros
        title = entry.get("title", "")
        if ticker and cik:
            mapping[ticker] = {"cik": cik, "title": title}

    cache_path.write_text(json.dumps(mapping, ensure_ascii=False, indent=2))
    _TICKER_MAP_CACHE = mapping
    return mapping


def get_cik(ticker: str) -> Optional[str]:
    """Map ticker → 10-digit CIK (with leading zeros)."""
    ticker = ticker.strip().upper()
    mapping = _load_ticker_map()
    if ticker in mapping:
        return mapping[ticker]["cik"]
    return None


def get_company_info(ticker: str) -> Optional[dict]:
    """Get full SEC submissions JSON for ticker."""
    cik = get_cik(ticker)
    if not cik:
        return None
    return _request(f"https://data.sec.gov/submissions/CIK{cik}.json")


# ── Disclosure list ────────────────────────────────────────────────────
def fetch_disclosures(ticker: str, lookback_days: int = 365) -> list[dict]:
    """Fetch SEC filings for ticker (last 1 year by default)."""
    cache_path = CACHE_DIR / f"filings_{ticker.replace('.', '_')}.json"
    if _cache_fresh(cache_path, ttl_hours=24):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    info = get_company_info(ticker)
    if not info:
        return []

    cutoff = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    items: list[dict] = []
    recent = info.get("filings", {}).get("recent", {})
    if not recent:
        return []

    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    accessions = recent.get("accessionNumber", [])
    primary_docs = recent.get("primaryDocument", [])
    primary_descriptions = recent.get("primaryDocDescription", [])

    cik = info.get("cik", "")
    cik_padded = str(cik).zfill(10)

    for i, form in enumerate(forms):
        date = dates[i] if i < len(dates) else ""
        if date < cutoff:
            continue
        access = accessions[i] if i < len(accessions) else ""
        doc = primary_docs[i] if i < len(primary_docs) else ""
        descr = primary_descriptions[i] if i < len(primary_descriptions) else ""

        # Construct primary doc URL
        access_clean = access.replace("-", "")
        doc_url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{access_clean}/{doc}" if access and doc else ""

        items.append({
            "date": date,
            "type": "공시",
            "category": form,
            "headline": _format_headline(form, descr),
            "summary": f"Form {form}{' — ' + descr if descr else ''} · 접수번호: {access}",
            "source": "SEC EDGAR",
            "rcept_no": access,
            "url": doc_url,
            "impact": _classify_impact(form, descr),
        })

    items.sort(key=lambda x: x.get("date", ""), reverse=True)
    cache_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    return items


def _format_headline(form: str, descr: str) -> str:
    """Generate readable headline from SEC form code."""
    form_names = {
        "10-K": "사업보고서 (Annual Report)",
        "10-Q": "분기보고서 (Quarterly Report)",
        "8-K": "주요사항보고서 (Current Report)",
        "DEF 14A": "주주총회 위임장 (Proxy Statement)",
        "S-1": "유가증권신고서 (Registration Statement)",
        "S-3": "추가 발행 신고서 (Shelf Registration)",
        "SC 13D": "5%+ 보유 신고서",
        "SC 13G": "5%+ 보유 신고서 (Passive)",
        "4": "임원·5%주주 거래신고서 (Insider Trading)",
        "3": "임원 신규 보고",
        "5": "임원 연간 보고",
        "144": "제한주식 매도 통보",
        "ARS": "Annual Report to Shareholders",
    }
    base = form_names.get(form, f"Form {form}")
    if descr and descr != form:
        return f"{base} — {descr}"
    return base


def _classify_impact(form: str, descr: str) -> str:
    """Classify SEC filing into +/-/○ based on form + description."""
    name = (form + " " + (descr or "")).upper()

    pos_kw = ["BUYBACK", "REPURCHASE", "DIVIDEND INCREASE", "ACQUISITION", "MERGER",
              "EARNINGS BEAT", "GUIDANCE RAISE", "NEW PRODUCT", "PARTNERSHIP",
              "10-K", "10-Q"]  # 10-K/10-Q itself is neutral but factual
    neg_kw = ["DEFAULT", "BANKRUPTCY", "RESIGNATION", "CEO RESIGNATION", "GOING CONCERN",
              "MATERIAL WEAKNESS", "DELISTING", "EARNINGS MISS", "GUIDANCE CUT",
              "DILUTION", "SECONDARY OFFERING"]

    # Insider trading (Form 4) — 매수면 +, 매도면 -
    if form == "4":
        if "PURCHASE" in name or "ACQUISITION" in name:
            return "+"
        if "SALE" in name or "DISPOSITION" in name:
            return "-"
        return "○"

    for kw in pos_kw:
        if kw in name:
            return "+" if kw not in ("10-K", "10-Q") else "○"
    for kw in neg_kw:
        if kw in name:
            return "-"
    return "○"


# ── Financial statements (10-K XBRL) ──────────────────────────────────
def fetch_financial_5y(ticker: str) -> dict:
    """Fetch 5-year P&L + BS via SEC XBRL companyfacts API."""
    cache_path = CACHE_DIR / f"facts_{ticker.replace('.', '_')}.json"
    if _cache_fresh(cache_path, ttl_hours=24 * 7):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    cik = get_cik(ticker)
    if not cik:
        return {}

    facts = _request(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json")
    if not facts:
        return {}

    us_gaap = facts.get("facts", {}).get("us-gaap", {})

    # Extract P&L 5Y annual
    pl_5y = []
    revenues = _extract_concept_annual(us_gaap, [
        "Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
        "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet"
    ])
    op_incomes = _extract_concept_annual(us_gaap, [
        "OperatingIncomeLoss", "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"
    ])
    net_incomes = _extract_concept_annual(us_gaap, [
        "NetIncomeLoss", "ProfitLoss"
    ])

    # Build 5-year series
    years = sorted(set(list(revenues.keys()) + list(op_incomes.keys()) + list(net_incomes.keys())), reverse=True)[:5]
    years.sort()

    for year in years:
        rev = revenues.get(year, 0)
        op = op_incomes.get(year, 0)
        ni = net_incomes.get(year, 0)
        pl_5y.append({
            "year": year,
            "revenue": rev / 1e6,  # convert to millions USD
            "op_income": op / 1e6,
            "op_margin": round((op / rev * 100), 1) if rev else 0,
            "net_income": ni / 1e6,
            "net_margin": round((ni / rev * 100), 1) if rev else 0,
        })

    # BS snapshot — latest year
    bs_snapshot = {}
    if pl_5y:
        latest_year = pl_5y[-1]["year"]
        bs_snapshot = {
            "total_assets": (_extract_concept_at_year(us_gaap, ["Assets"], latest_year) or 0) / 1e6,
            "total_liab": (_extract_concept_at_year(us_gaap, ["Liabilities"], latest_year) or 0) / 1e6,
            "equity": (_extract_concept_at_year(us_gaap, ["StockholdersEquity"], latest_year) or 0) / 1e6,
            "cash": (_extract_concept_at_year(us_gaap, ["CashAndCashEquivalentsAtCarryingValue"], latest_year) or 0) / 1e6,
            "debt": (_extract_concept_at_year(us_gaap, ["LongTermDebt", "LongTermDebtNoncurrent"], latest_year) or 0) / 1e6,
        }

    # Cash flow summary
    cf_summary = {}
    ocfs = _extract_concept_annual(us_gaap, ["NetCashProvidedByUsedInOperatingActivities"])
    capex = _extract_concept_annual(us_gaap, ["PaymentsToAcquirePropertyPlantAndEquipment"])
    if ocfs:
        recent_ocfs = sorted([(y, v) for y, v in ocfs.items()], reverse=True)[:5]
        cf_summary = {
            "ocf_5y_avg": sum(v for _, v in recent_ocfs) / max(len(recent_ocfs), 1) / 1e6,
            "fcf_5y_avg": (sum(v for _, v in recent_ocfs) -
                            sum(capex.get(y, 0) for y, _ in recent_ocfs)) /
                           max(len(recent_ocfs), 1) / 1e6,
            "capex_intensity": (sum(capex.get(y, 0) for y, _ in recent_ocfs) /
                                  max(sum(revenues.get(y, 1) for y, _ in recent_ocfs), 1)),
        }

    result = {
        "pl_5y": pl_5y,
        "bs_snapshot": bs_snapshot,
        "cf_summary": cf_summary,
        "source": "SEC EDGAR (10-K XBRL companyfacts)",
        "currency": "USD (millions)",
        "fetched_at": datetime.now().isoformat(),
    }
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def _extract_concept_annual(us_gaap: dict, concept_names: list[str]) -> dict[int, float]:
    """Extract annual values for the named concepts. Returns {year: value}."""
    for name in concept_names:
        if name not in us_gaap:
            continue
        units = us_gaap[name].get("units", {})
        # Prefer USD
        for unit_key in ("USD", "USD/shares"):
            if unit_key not in units:
                continue
            yearly: dict[int, float] = {}
            for entry in units[unit_key]:
                if entry.get("form") != "10-K":
                    continue
                fp = entry.get("fp")
                if fp != "FY":  # full year only
                    continue
                year = entry.get("fy")
                val = entry.get("val")
                if year and val is not None:
                    yearly[year] = val
            if yearly:
                return yearly
    return {}


def _extract_concept_at_year(us_gaap: dict, concept_names: list[str], year: int) -> Optional[float]:
    annual = _extract_concept_annual(us_gaap, concept_names)
    return annual.get(year)


# ── Public summary ──────────────────────────────────────────────────────
def get_status() -> dict:
    """Diagnostic — SEC EDGAR ready check."""
    ua = _user_agent()
    return {
        "configured": True,  # no API key needed
        "user_agent": ua,
        "using_default_ua": ua == DEFAULT_UA,
        "cache_dir": str(CACHE_DIR),
        "ticker_cik_cached": (CACHE_DIR / "ticker_cik_map.json").exists(),
        "api_endpoint": "https://data.sec.gov",
        "rate_limit": "10 req/sec",
        "api_key_required": False,
    }


if __name__ == "__main__":
    import sys
    print("SEC EDGAR status:", json.dumps(get_status(), ensure_ascii=False, indent=2))

    if len(sys.argv) > 1:
        tk = sys.argv[1]
        cik = get_cik(tk)
        print(f"\n{tk} → CIK: {cik}")
        if cik:
            disc = fetch_disclosures(tk)
            print(f"Filings (1Y): {len(disc)} items")
            for d in disc[:5]:
                print(f"  {d['date']} {d['impact']} {d['headline'][:80]}")
