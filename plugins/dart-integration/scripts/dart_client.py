"""DART OpenAPI client — 한국 전자공시시스템 (Financial Supervisory Service).

API base: https://opendart.fss.or.kr/api
Free signup: https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do
Daily quota: 10,000 calls

Environment:
  DART_API_KEY — required for live API calls. If absent, returns mock fallback.

Cache:
  ~/.cache/dart_integration/ — corp_code map (XML, 7-day TTL),
  per-ticker disclosure cache (JSON, 24-hour TTL).
"""
from __future__ import annotations

import json
import os
import time
import zipfile
import io
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DART_API_BASE = "https://opendart.fss.or.kr/api"
CACHE_DIR = Path.home() / ".cache" / "dart_integration"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _api_key() -> Optional[str]:
    """Load DART_API_KEY from env or .env file.

    Resolution order:
      1. Environment variable DART_API_KEY
      2. .env file in CWD
      3. .env file in CLAUDE_PROJECT_DIR (if set)
      4. .env file in this script's project root (../../.. from plugin scripts/)
    """
    k = os.environ.get("DART_API_KEY")
    if k:
        return k

    # Try .env files in priority order
    candidates = [Path.cwd() / ".env"]

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if project_dir:
        candidates.append(Path(project_dir) / ".env")

    # Resolve project root relative to this script
    # plugins/dart-integration/scripts/dart_client.py → 3 levels up
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / ".env")

    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.strip().startswith("DART_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _is_available() -> bool:
    """Check if DART API key is configured.

    Override with SKIP_DART=1 environment variable to force-disable
    (useful when sandbox network is slow or for testing fallback paths).
    """
    if os.environ.get("SKIP_DART") in ("1", "true", "yes"):
        return False
    return _api_key() is not None


def _cache_path(name: str) -> Path:
    return CACHE_DIR / name


def _cache_fresh(path: Path, ttl_hours: int = 24) -> bool:
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl_hours * 3600


# ── corp_code lookup ────────────────────────────────────────────────────
def _download_corp_codes() -> Path:
    """Download DART corp_code XML (TTL: 7 days).

    Honors DART_DISABLE=1 (skip all calls) and DART_TIMEOUT (default 30, smaller for offline-friendly).
    """
    cache_xml = _cache_path("corp_codes.xml")
    if _cache_fresh(cache_xml, ttl_hours=24 * 7):
        return cache_xml

    if os.environ.get("DART_DISABLE", "").strip() in ("1", "true", "yes"):
        return cache_xml  # skip all DART calls — offline mode

    if not _is_available():
        return cache_xml  # may not exist

    import requests
    url = f"{DART_API_BASE}/corpCode.xml"
    timeout_s = int(os.environ.get("DART_TIMEOUT", "30"))
    try:
        r = requests.get(url, params={"crtfc_key": _api_key()}, timeout=timeout_s)
        r.raise_for_status()
        # Response is a ZIP file containing CORPCODE.xml
        z = zipfile.ZipFile(io.BytesIO(r.content))
        for name in z.namelist():
            if name.endswith(".xml"):
                cache_xml.write_bytes(z.read(name))
                return cache_xml
    except Exception as e:
        print(f"[dart] corp_code download failed: {e}")
    return cache_xml


def get_corp_code(ticker: str) -> Optional[str]:
    """Map ticker (005490.KS, 006400.KS) → DART corp_code (8-digit)."""
    # Strip exchange suffix
    base_ticker = ticker.replace(".KS", "").replace(".KQ", "")

    cache_xml = _download_corp_codes()
    if not cache_xml.exists():
        return None

    # Parse XML — find <list> with <stock_code> matching
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse(cache_xml)
        for entry in tree.getroot().findall("list"):
            stock_code = (entry.findtext("stock_code") or "").strip()
            if stock_code == base_ticker:
                return entry.findtext("corp_code", "").strip()
    except Exception as e:
        print(f"[dart] corp_code parse error: {e}")
    return None


# ── Disclosure list ────────────────────────────────────────────────────
def fetch_disclosures(ticker: str, lookback_days: int = 365) -> list[dict]:
    """Fetch 1-year disclosure list for ticker.

    Returns list of {date, type, category, headline, summary, source, impact}
    """
    cache_path = _cache_path(f"disclosures_{ticker.replace('.', '_')}.json")
    if _cache_fresh(cache_path, ttl_hours=24):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    if not _is_available():
        return []

    corp_code = get_corp_code(ticker)
    if not corp_code:
        print(f"[dart] no corp_code for {ticker}")
        return []

    end_date = datetime.now()
    start_date = end_date - timedelta(days=lookback_days)

    if os.environ.get("DART_DISABLE", "").strip() in ("1", "true", "yes"):
        return []  # skip all DART calls — offline mode

    import requests
    items: list[dict] = []
    timeout_s = int(os.environ.get("DART_TIMEOUT", "20"))
    try:
        url = f"{DART_API_BASE}/list.json"
        params = {
            "crtfc_key": _api_key(),
            "corp_code": corp_code,
            "bgn_de": start_date.strftime("%Y%m%d"),
            "end_de": end_date.strftime("%Y%m%d"),
            "page_count": 100,
        }
        r = requests.get(url, params=params, timeout=timeout_s)
        r.raise_for_status()
        data = r.json()
        if data.get("status") != "000":
            print(f"[dart] API error: {data.get('message')}")
            return []

        for d in data.get("list", []):
            items.append({
                "date": _format_date(d.get("rcept_dt")),
                "type": "공시",
                "category": d.get("report_nm", "")[:30],
                "headline": d.get("report_nm", ""),
                "summary": f"제출자: {d.get('flr_nm', '-')} · 접수번호: {d.get('rcept_no', '-')}",
                "source": "DART",
                "rcept_no": d.get("rcept_no"),
                "impact": _classify_impact(d.get("report_nm", "")),
            })
    except Exception as e:
        print(f"[dart] disclosure fetch failed: {e}")
        return []

    cache_path.write_text(json.dumps(items, ensure_ascii=False, indent=2))
    return items


def _format_date(yyyymmdd: str) -> str:
    if not yyyymmdd or len(yyyymmdd) != 8:
        return yyyymmdd or "-"
    return f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"


def _classify_impact(report_name: str) -> str:
    """Classify disclosure into +/-/○ based on report name keywords."""
    name = report_name or ""
    pos_kw = ["배당", "자기주식 매입", "자기주식취득", "신규시설투자", "주식분할",
               "신규수주", "사업양수", "특허취득", "임원선임", "M&A", "합병"]
    neg_kw = ["감자", "유상증자", "최대주주변경", "사임", "사장 사임", "퇴임", "감액손실",
               "주식병합", "임시주주총회 — 안건 부결", "자본잠식"]

    for kw in pos_kw:
        if kw in name:
            return "+"
    for kw in neg_kw:
        if kw in name:
            return "-"
    return "○"


# ── Financial statements ────────────────────────────────────────────────
def fetch_financial_5y(ticker: str) -> dict:
    """Fetch 5-year P&L + BS snapshot via DART finStatementsAll API.

    Returns: {pl_5y: [...], bs_snapshot: {...}, cf_summary: {...}}
    """
    cache_path = _cache_path(f"financials_{ticker.replace('.', '_')}.json")
    if _cache_fresh(cache_path, ttl_hours=24 * 7):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    if not _is_available():
        return {}

    if os.environ.get("DART_DISABLE", "").strip() in ("1", "true", "yes"):
        return {}  # skip all DART calls — offline mode

    corp_code = get_corp_code(ticker)
    if not corp_code:
        return {}

    import requests
    pl_5y: list[dict] = []
    bs_snapshot: dict = {}
    cf_summary: dict = {}
    current_year = datetime.now().year
    timeout_s = int(os.environ.get("DART_TIMEOUT", "20"))

    try:
        for year in range(current_year - 5, current_year):
            url = f"{DART_API_BASE}/fnlttSinglAcntAll.json"
            params = {
                "crtfc_key": _api_key(),
                "corp_code": corp_code,
                "bsns_year": str(year),
                "reprt_code": "11011",  # 사업보고서 (annual)
                "fs_div": "OFS",  # 별도 (CFS for consolidated)
            }
            r = requests.get(url, params=params, timeout=timeout_s)
            r.raise_for_status()
            data = r.json()
            if data.get("status") != "000":
                continue
            entries = data.get("list", [])
            if not entries:
                continue

            # Extract key items
            revenue = _extract_amount(entries, ["매출액", "수익(매출액)", "영업수익"])
            op_income = _extract_amount(entries, ["영업이익", "영업이익(손실)"])
            net_income = _extract_amount(entries, ["당기순이익", "당기순이익(손실)"])

            if revenue:
                op_margin = (op_income / revenue * 100) if (op_income and revenue) else 0
                net_margin = (net_income / revenue * 100) if (net_income and revenue) else 0
                pl_5y.append({
                    "year": year,
                    "revenue": revenue / 1e9,
                    "op_income": (op_income or 0) / 1e9,
                    "op_margin": round(op_margin, 1),
                    "net_income": (net_income or 0) / 1e9,
                    "net_margin": round(net_margin, 1),
                })

            # Latest year — also extract BS snapshot
            if year == current_year - 1:
                bs_snapshot = {
                    "total_assets": (_extract_amount(entries, ["자산총계"]) or 0) / 1e9,
                    "total_liab": (_extract_amount(entries, ["부채총계"]) or 0) / 1e9,
                    "equity": (_extract_amount(entries, ["자본총계"]) or 0) / 1e9,
                    "cash": (_extract_amount(entries, ["현금및현금성자산"]) or 0) / 1e9,
                    "debt": (_extract_amount(entries, ["장기차입금", "사채"]) or 0) / 1e9,
                }
    except Exception as e:
        print(f"[dart] financials fetch failed: {e}")

    result = {
        "pl_5y": pl_5y,
        "bs_snapshot": bs_snapshot,
        "cf_summary": cf_summary,
        "source": "DART (사업보고서 XBRL)",
        "fetched_at": datetime.now().isoformat(),
    }
    cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def _extract_amount(entries: list[dict], account_names: list[str]) -> Optional[float]:
    """Find the latest value for the named account."""
    for entry in entries:
        name = entry.get("account_nm", "")
        if any(an == name or an in name for an in account_names):
            try:
                amt = entry.get("thstrm_amount", "0").replace(",", "")
                return float(amt)
            except (ValueError, AttributeError):
                continue
    return None


# ── Public summary ──────────────────────────────────────────────────────
def get_status() -> dict:
    """Diagnostic — is DART configured?"""
    return {
        "configured": _is_available(),
        "cache_dir": str(CACHE_DIR),
        "corp_codes_cached": (CACHE_DIR / "corp_codes.xml").exists(),
        "api_endpoint": DART_API_BASE,
    }


if __name__ == "__main__":
    import sys
    print("DART status:", json.dumps(get_status(), ensure_ascii=False, indent=2))
    if not _is_available():
        print("\nDART_API_KEY not set. Add to .env:")
        print("  DART_API_KEY=your_key_here")
        print("Sign up at: https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do")
        sys.exit(0)

    if len(sys.argv) > 1:
        tk = sys.argv[1]
        cc = get_corp_code(tk)
        print(f"\n{tk} → corp_code: {cc}")
        disc = fetch_disclosures(tk)
        print(f"Disclosures (1Y): {len(disc)} items")
        for d in disc[:5]:
            print(f"  {d['date']} {d['impact']} {d['headline'][:80]}")
