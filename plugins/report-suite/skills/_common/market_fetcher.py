"""yfinance market data fetcher — 실시간 가격·재무 fetch.

LLM이 placeholder data로 가격을 fabricate하는 문제를 차단하기 위해,
**모든 분석은 본 모듈을 통해 실제 yfinance API에서 시장 데이터를 가져와야 함**.

CRITICAL: stocks.json의 market_data 필드는 반드시 본 모듈로 채울 것.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

CACHE_DIR = Path.home() / ".cache" / "market_fetcher"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_fresh(path: Path, ttl_hours: int = 6) -> bool:
    """Default 6h cache — intraday 가격 변동 반영."""
    if not path.exists():
        return False
    age = time.time() - path.stat().st_mtime
    return age < ttl_hours * 3600


def fetch_market_data(ticker: str, ttl_hours: int = 6) -> dict:
    """단일 ticker에 대한 실시간 market data fetch.

    Returns:
        {
            "ticker": "000660.KS",
            "name": "SK hynix Inc.",
            "current_price": 1409000.0,
            "currency": "KRW",
            "forward_pe": 8.5,
            "trailing_pe": 11.5,
            "beta": 1.45,
            "return_1m_pct": 12.5,
            "return_3m_pct": 28.5,
            "return_6m_pct": 55.5,
            "return_1y_pct": 95.5,
            "volatility_annualized_pct": 38.5,
            "market_cap_local_bn": 207000.0,
            "market_cap_usd_bn": 159.2,
            "ev_ebitda": 6.5,
            "div_yield_pct": 0.35,
            "pb": 2.85,
            "fetched_at": "2026-05-04T10:30:00",
            "fetched_via": "yfinance v1.3.0 (live)",
            "as_of_date": "2026-05-04"
        }
    """
    cache_path = CACHE_DIR / f"{ticker.replace('.', '_').replace('/', '_')}.json"
    if _cache_fresh(cache_path, ttl_hours):
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    try:
        import yfinance as yf
        import numpy as np
    except ImportError:
        print(f"[market] yfinance not installed — install: pip install --break-system-packages yfinance")
        return {}

    try:
        from datetime import date, timedelta
        t = yf.Ticker(ticker)
        info = t.info or {}

        # Use explicit start/end dates to avoid period='1y' edge cases (split-off stocks etc.)
        end_d = date.today() + timedelta(days=1)  # +1 to include today
        start_d = end_d - timedelta(days=400)  # ~13 months for safe 1Y window
        hist = t.history(start=start_d.isoformat(), end=end_d.isoformat(), auto_adjust=True)
        if len(hist) == 0:
            print(f"[market] no history for {ticker}")
            return {}

        # Latest price
        current_price = float(hist["Close"].iloc[-1])
        as_of_date = hist.index[-1].strftime("%Y-%m-%d")
        currency = info.get("currency", "USD")

        # Returns — using DATE-based lookup (not row index), which handles missing days robustly
        latest_ts = hist.index[-1]

        def _price_at(days_ago: int) -> Optional[float]:
            """Find closest trading day to (latest - days_ago)."""
            target = latest_ts - timedelta(days=days_ago)
            # Find closest index <= target
            try:
                hist_subset = hist[hist.index <= target]
                if len(hist_subset) == 0:
                    return None
                return float(hist_subset["Close"].iloc[-1])
            except Exception:
                return None

        def _ret_days(days_ago: int) -> Optional[float]:
            past = _price_at(days_ago)
            if past and past > 0:
                return round((current_price / past - 1) * 100, 2)
            return None

        ret_1m = _ret_days(30)
        ret_3m = _ret_days(91)
        ret_6m = _ret_days(182)
        ret_1y = _ret_days(365)

        # SANITY CHECK: trading history < 365 days means stock didn't exist 1Y ago
        # Mark suspicious 1Y if data starts < 1Y ago (e.g. Sandisk Feb 2025 spin-off)
        days_of_history = (latest_ts - hist.index[0]).days
        if days_of_history < 365 and ret_1y is not None:
            # Don't report misleading 1Y return for split-off stocks
            print(f"[market] {ticker}: only {days_of_history}d of history (< 1Y) — suppressing 1Y return")
            ret_1y = None

        # Sanity warning for extreme returns
        if ret_1y is not None and abs(ret_1y) > 1000:
            print(f"[market] WARNING {ticker}: 1Y return {ret_1y:+.0f}% — likely data anomaly")

        # Volatility (annualized) — use full history
        returns = hist["Close"].pct_change().dropna()
        vol_annual = float(returns.std() * np.sqrt(252) * 100) if len(returns) > 30 else None

        # Market cap conversion
        mc = info.get("marketCap")
        usd_rate = 1.0
        if currency == "KRW":
            usd_rate = 1300
        elif currency == "JPY":
            usd_rate = 150
        elif currency == "EUR":
            usd_rate = 0.92
        elif currency == "GBP":
            usd_rate = 0.79

        result = {
            "ticker": ticker,
            "name": info.get("longName") or info.get("shortName") or ticker,
            "current_price": round(current_price, 2),
            "currency": currency,
            "forward_pe": round(info.get("forwardPE"), 2) if info.get("forwardPE") else None,
            "trailing_pe": round(info.get("trailingPE"), 2) if info.get("trailingPE") else None,
            "beta": round(info.get("beta"), 2) if info.get("beta") else None,
            "return_1m_pct": ret_1m,
            "return_3m_pct": ret_3m,
            "return_6m_pct": ret_6m,
            "return_1y_pct": ret_1y,
            "volatility_annualized_pct": round(vol_annual, 2) if vol_annual else None,
            "market_cap_local_bn": round(mc / 1e9, 2) if mc else None,
            "market_cap_usd_bn": round(mc / usd_rate / 1e9, 2) if mc else None,
            "ev_ebitda": round(info.get("enterpriseToEbitda"), 2) if info.get("enterpriseToEbitda") else None,
            # yfinance v1.3.0+ returns dividendYield AS PERCENT directly (e.g. 0.23 = 0.23%).
            # Verified: SK하이닉스 dividendRate 3000원 / price 1411000 = 0.213% ≈ dividendYield 0.23
            # No multiplication needed.
            "div_yield_pct": round(info.get("dividendYield"), 2) if info.get("dividendYield") else 0,
            "pb": round(info.get("priceToBook"), 2) if info.get("priceToBook") else None,
            "fetched_at": datetime.now().isoformat(timespec="seconds"),
            "fetched_via": f"yfinance {yf.__version__} (live)",
            "as_of_date": as_of_date,
        }

        cache_path.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
    except Exception as e:
        print(f"[market] fetch failed for {ticker}: {e}")
        return {}


def build_stocks_json(tickers: list[str], output_path: Path,
                      thesis_alignments: Optional[dict] = None) -> dict:
    """Top N tickers에 대한 실제 yfinance fetch + stocks.json 저장.

    Returns: {ticker: market_data} dict
    """
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from ticker_resolver import resolve_ticker  # type: ignore

    stocks = []
    fetched: dict[str, dict] = {}
    for ticker in tickers:
        print(f"[market] fetching {ticker}...")
        data = fetch_market_data(ticker)
        if not data:
            print(f"  ✗ failed — skipping")
            continue
        info = resolve_ticker(ticker)
        stock_entry = {
            "ticker": ticker,
            "name": info.get("kr") or data.get("name", ticker),
            "exchange": _exchange_from_ticker(ticker),
            "thesis_alignment": (thesis_alignments or {}).get(ticker, "high"),
            "market_data": data,
        }
        stocks.append(stock_entry)
        fetched[ticker] = data
        print(f"  ✓ {ticker}: {data['current_price']:,.0f} {data['currency']} ({data['as_of_date']})")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(stocks, ensure_ascii=False, indent=2))
    print(f"\n[market] saved {output_path} ({len(stocks)} stocks)")
    return fetched


def _exchange_from_ticker(ticker: str) -> str:
    if ticker.endswith(".KS"):
        return "KOSPI"
    if ticker.endswith(".KQ"):
        return "KOSDAQ"
    if ticker.endswith(".T"):
        return "TSE"
    if ticker.endswith(".HK"):
        return "HKEX"
    if ticker.endswith(".HE"):
        return "Helsinki"
    if ticker.endswith(".L"):
        return "LSE"
    return "NYSE/NASDAQ"


def validate_stocks_json(stocks_path: Path, max_age_hours: int = 24) -> tuple[bool, list[str]]:
    """stocks.json의 market_data가 실제 fetch된 데이터인지 검증.

    Returns: (passed, errors)
    """
    if not stocks_path.exists():
        return False, ["stocks.json missing"]

    errors = []
    try:
        stocks = json.loads(stocks_path.read_text())
    except Exception as e:
        return False, [f"malformed JSON: {e}"]

    for s in stocks:
        ticker = s.get("ticker", "?")
        m = s.get("market_data", {})
        fv = m.get("fetched_via", "")
        if "yfinance" not in fv.lower() or "(live)" not in fv.lower():
            errors.append(f"{ticker}: market_data.fetched_via NOT live yfinance — got '{fv}'")
        fetched_at = m.get("fetched_at")
        if fetched_at:
            try:
                age_hours = (datetime.now() - datetime.fromisoformat(fetched_at)).total_seconds() / 3600
                if age_hours > max_age_hours:
                    errors.append(f"{ticker}: stale data ({age_hours:.1f}h old, max {max_age_hours}h)")
            except Exception:
                pass
        else:
            errors.append(f"{ticker}: no fetched_at timestamp")

    return len(errors) == 0, errors


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        tickers = sys.argv[1:]
        print(f"=== Live yfinance fetch for {len(tickers)} tickers ===\n")
        for t in tickers:
            d = fetch_market_data(t)
            if d:
                print(f"  {t}: {d['current_price']:,.2f} {d['currency']} | "
                       f"1Y {d.get('return_1y_pct', 'N/A')}% | "
                       f"vol {d.get('volatility_annualized_pct', 'N/A')}% | "
                       f"as_of {d['as_of_date']}")
