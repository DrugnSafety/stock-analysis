#!/usr/bin/env python3
"""Risk Manager — 변동성·상관관계 기반 포지션 한도 계산."""
import argparse
import json
import math
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


KST = timezone(timedelta(hours=9))


def vol_multiplier(annualized_vol: float) -> float:
    """ai-hedge-fund 공식 재현."""
    if annualized_vol < 0.15:
        return 1.25
    if annualized_vol < 0.30:
        return 1.0 - (annualized_vol - 0.15) * 0.5
    if annualized_vol < 0.50:
        return 0.75 - (annualized_vol - 0.30) * 0.5
    return 0.50


def corr_multiplier(avg_corr: float) -> float:
    if avg_corr >= 0.80:
        return 0.70
    if avg_corr >= 0.60:
        return 0.85
    if avg_corr >= 0.40:
        return 1.00
    if avg_corr >= 0.20:
        return 1.05
    return 1.10


def fetch_history(ticker: str, end_date: str, window_days: int = 90):
    """end_date 직전 window_days만큼 일별 종가."""
    import yfinance as yf
    from datetime import datetime as _dt, timedelta as _td

    end = _dt.strptime(end_date, "%Y-%m-%d")
    start = (end - _td(days=window_days * 2 + 30)).strftime("%Y-%m-%d")  # 충분한 buffer
    end_p1 = (end + _td(days=2)).strftime("%Y-%m-%d")

    try:
        df = yf.Ticker(ticker).history(start=start, end=end_p1, auto_adjust=False)
        if df.empty:
            return None
        df = df.sort_index()
        # end 이전까지만
        if df.index.tz:
            df = df[df.index <= end.replace(tzinfo=df.index.tz)]
        else:
            df = df[df.index <= end]
        if len(df) < 20:
            return None
        return df["Close"]
    except Exception as e:
        print(f"  fetch_history({ticker}, {end_date}) error: {e}", file=sys.stderr)
        return None


def calc_volatility_metrics(prices, window_days: int = 60) -> dict:
    """daily volatility · annualized · percentile."""
    if prices is None or len(prices) < 21:
        return {"data_points": 0, "annualized_volatility": None}

    returns = prices.pct_change().dropna()
    rolling_window = min(window_days, len(returns))
    daily_vol = returns.tail(rolling_window).std()
    annualized = daily_vol * math.sqrt(252)

    # percentile of latest vol vs historical 5-day rolling
    if len(returns) >= 30:
        rolling_5d = returns.rolling(5).std().dropna()
        if len(rolling_5d) > 0:
            recent = returns.tail(5).std()
            pct = (rolling_5d < recent).sum() / len(rolling_5d) * 100
        else:
            pct = None
    else:
        pct = None

    return {
        "daily_volatility": round(float(daily_vol), 5),
        "annualized_volatility": round(float(annualized), 4),
        "volatility_percentile": round(float(pct), 1) if pct is not None else None,
        "data_points": rolling_window,
    }


def calc_correlation_metrics(target_prices, active_position_prices: dict) -> dict:
    """ticker의 가격 시계열과 active position들의 평균/최대 상관."""
    if not active_position_prices:
        return {
            "avg_correlation_with_active": None,
            "max_correlation_with_active": None,
            "active_positions": [],
        }

    target_returns = target_prices.pct_change().dropna()
    correlations = {}
    for t, p in active_position_prices.items():
        if p is None:
            continue
        p_returns = p.pct_change().dropna()
        # align
        common = target_returns.index.intersection(p_returns.index)
        if len(common) < 10:
            continue
        corr = target_returns.loc[common].corr(p_returns.loc[common])
        if corr is not None and not math.isnan(corr):
            correlations[t] = round(float(corr), 3)

    if not correlations:
        return {
            "avg_correlation_with_active": None,
            "max_correlation_with_active": None,
            "active_positions": list(active_position_prices.keys()),
            "per_ticker": {},
        }

    avg_corr = sum(correlations.values()) / len(correlations)
    max_corr = max(correlations.values())
    return {
        "avg_correlation_with_active": round(avg_corr, 3),
        "max_correlation_with_active": round(max_corr, 3),
        "active_positions": list(correlations.keys()),
        "per_ticker": correlations,
    }


def compute_limits(ticker: str, as_of: str, portfolio_value: float,
                   base_limit_pct: float = 0.20,
                   active_positions: list[str] = None,
                   vol_window: int = 60) -> dict:
    """단일 ticker × as_of_date 한도."""
    prices = fetch_history(ticker, as_of, window_days=vol_window + 30)
    if prices is None:
        return {
            "ticker": ticker, "as_of_date": as_of,
            "error": "price history unavailable",
        }

    current_price = float(prices.iloc[-1])
    vol_metrics = calc_volatility_metrics(prices, vol_window)
    vol_mult = vol_multiplier(vol_metrics.get("annualized_volatility") or 0.30)

    # Correlation
    active_prices = {}
    if active_positions:
        for ap in active_positions:
            if ap == ticker:
                continue
            active_prices[ap] = fetch_history(ap, as_of, window_days=vol_window + 30)
    corr_metrics = calc_correlation_metrics(prices, active_prices)
    corr_mult = corr_multiplier(corr_metrics.get("avg_correlation_with_active") or 0.0)

    combined_pct = base_limit_pct * vol_mult * corr_mult
    position_limit_value = portfolio_value * combined_pct
    max_qty = int(position_limit_value // current_price) if current_price > 0 else 0

    return {
        "ticker": ticker,
        "as_of_date": as_of,
        "current_price": round(current_price, 4),
        "portfolio_value": portfolio_value,
        "volatility_metrics": vol_metrics,
        "vol_multiplier": round(vol_mult, 3),
        "correlation_metrics": corr_metrics,
        "corr_multiplier": round(corr_mult, 3),
        "base_limit_pct": base_limit_pct,
        "combined_limit_pct": round(combined_pct, 4),
        "position_limit_value": round(position_limit_value, 2),
        "remaining_position_limit_value": round(position_limit_value, 2),
        "max_quantity": max_qty,
    }


def load_ledger(path: Path) -> list[dict]:
    txt = path.read_text(encoding="utf-8").strip()
    if txt.startswith("["):
        return json.loads(txt)
    out = []
    for line in txt.splitlines():
        line = line.strip()
        if line:
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return out


def main():
    parser = argparse.ArgumentParser(description="Risk Manager — position limits")
    parser.add_argument("--ticker", help="단일 ticker")
    parser.add_argument("--as-of", help="as_of_date (단일 ticker 모드)")
    parser.add_argument("--ledger", help="ledger.jsonl — batch 모드")
    parser.add_argument("--portfolio-value", type=float, default=1_000_000)
    parser.add_argument("--active-positions", default="", help="콤마 구분")
    parser.add_argument("--base-limit", type=float, default=0.20)
    parser.add_argument("--vol-window", type=int, default=60)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    active = [p.strip() for p in args.active_positions.split(",") if p.strip()]

    if args.ledger:
        records = load_ledger(Path(args.ledger))
        # unique (ticker, date) 쌍 추출
        unique_pairs = set()
        for r in records:
            t = r.get("ticker")
            d = r.get("date") or r.get("verdict_date")
            if t and d:
                unique_pairs.add((t, d))

        results = []
        for i, (t, d) in enumerate(sorted(unique_pairs), 1):
            print(f"[{i}/{len(unique_pairs)}] {t} @ {d}", file=sys.stderr)
            r = compute_limits(t, d, args.portfolio_value, args.base_limit,
                              active, args.vol_window)
            results.append(r)

        out = {
            "computed_at": datetime.now(KST).isoformat(),
            "portfolio_value": args.portfolio_value,
            "base_limit_pct": args.base_limit,
            "n_pairs": len(unique_pairs),
            "limits": results,
        }
    else:
        if not args.ticker or not args.as_of:
            raise SystemExit("--ticker와 --as-of 또는 --ledger 필요")
        out = compute_limits(args.ticker, args.as_of, args.portfolio_value,
                            args.base_limit, active, args.vol_window)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n[risk] saved: {args.output}")
    if "limits" in out:
        print(f"  처리: {len(out['limits'])}개 (ticker, date) 쌍")
        # Summary
        for r in out["limits"][:10]:
            if "error" in r:
                print(f"  {r['ticker']:12s} @ {r['as_of_date']}: ERROR")
                continue
            v = r['volatility_metrics'].get('annualized_volatility')
            v_str = f"{v*100:.0f}%" if v else "?"
            print(f"  {r['ticker']:12s} @ {r['as_of_date']}: vol={v_str}, "
                  f"limit={r['combined_limit_pct']*100:.1f}% "
                  f"(${r['position_limit_value']:,.0f}, max={r['max_quantity']}주)")


if __name__ == "__main__":
    main()
