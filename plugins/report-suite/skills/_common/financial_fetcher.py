"""Financial data fetcher — auto-route to DART (KR), SEC EDGAR (US), or yfinance fallback.

Used by build_combined.py to populate Deep Research financials section.
Replaces hardcoded placeholder data with live API data when available.

Routing:
  - .KS / .KQ → DART (한국 전자공시)
  - Others (US-style ticker) → SEC EDGAR (미국 SEC)
  - Both: graceful fallback to placeholder if API call fails
"""
from __future__ import annotations

import sys
from pathlib import Path

_PLUGINS_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Try DART (Korean stocks)
_DART_AVAILABLE = False
try:
    _dart_path = _PLUGINS_ROOT / "dart-integration" / "scripts"
    if _dart_path.exists():
        sys.path.insert(0, str(_dart_path))
        from dart_client import fetch_financial_5y as _dart_fetch_fin  # type: ignore
        from dart_client import _is_available as _dart_is_available  # type: ignore
        _DART_AVAILABLE = True
except Exception:
    pass

# Try SEC EDGAR (US stocks)
_SEC_AVAILABLE = False
try:
    _sec_path = _PLUGINS_ROOT / "sec-edgar-integration" / "scripts"
    if _sec_path.exists():
        sys.path.insert(0, str(_sec_path))
        from sec_client import fetch_financial_5y as _sec_fetch_fin  # type: ignore
        from sec_client import get_cik as _sec_get_cik  # type: ignore
        _SEC_AVAILABLE = True
except Exception:
    pass


def fetch_financials_for_deep_research(ticker: str) -> dict:
    """Fetch financials for deep_research section.

    Auto-routing:
      - .KS / .KQ → DART
      - Others → SEC EDGAR
      - Both: empty dict if unavailable (caller uses placeholder)
    """
    is_kr = ticker.endswith((".KS", ".KQ"))
    is_us_style = (not is_kr) and (not "." in ticker or ticker.endswith((".N", ".OQ")))

    if is_kr and _DART_AVAILABLE and _dart_is_available():
        try:
            data = _dart_fetch_fin(ticker)
            if data and data.get("pl_5y"):
                return data
        except Exception as e:
            print(f"[fin] DART fetch failed for {ticker}: {e}")

    if is_us_style and _SEC_AVAILABLE:
        try:
            data = _sec_fetch_fin(ticker)
            if data and data.get("pl_5y"):
                return data
        except Exception as e:
            print(f"[fin] SEC fetch failed for {ticker}: {e}")

    return {}


def get_status() -> dict:
    return {
        "dart_available": _DART_AVAILABLE,
        "dart_active": _DART_AVAILABLE and _dart_is_available() if _DART_AVAILABLE else False,
        "sec_available": _SEC_AVAILABLE,
        "sec_active": _SEC_AVAILABLE,  # SEC needs no API key
    }
