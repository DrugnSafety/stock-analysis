#!/usr/bin/env python3
"""Paper Portfolio — trade decisions를 시점별로 누적 시뮬레이션."""
import argparse
import json
import math
from datetime import datetime, timezone, timedelta
from pathlib import Path


KST = timezone(timedelta(hours=9))


def fetch_close(ticker: str, date: str, window_days: int = 5):
    import yfinance as yf
    from datetime import datetime as _dt, timedelta as _td

    td = _dt.strptime(date, "%Y-%m-%d")
    start = (td - _td(days=window_days)).strftime("%Y-%m-%d")
    end = (td + _td(days=window_days + 1)).strftime("%Y-%m-%d")

    try:
        df = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)
        if df.empty:
            return None
        df = df.sort_index()
        if df.index.tz:
            mask = df.index >= td.replace(tzinfo=df.index.tz)
        else:
            mask = df.index >= td
        sub = df[mask]
        if sub.empty:
            sub = df.tail(1)
        return float(sub.iloc[0]["Close"])
    except Exception:
        return None


def simulate(decisions: list[dict], start_cash: float, end_date: str,
             benchmarks: list[str] = None) -> dict:
    """시점별 trade 시뮬레이션."""
    benchmarks = benchmarks or []

    # Sort by date
    decisions_sorted = sorted(decisions, key=lambda x: x.get("date", ""))

    cash = start_cash
    positions = {}  # ticker → {qty, avg_cost, last_price}
    trade_log = []
    total_trades = 0
    total_buy_value = 0.0
    total_sell_value = 0.0

    for d in decisions_sorted:
        if "error" in d:
            continue
        ticker = d["ticker"]
        date = d["date"]
        action = d["action"]
        target_qty = d.get("target_quantity", 0)
        price = d.get("current_price", 0)
        if not price:
            continue

        current_qty = positions.get(ticker, {}).get("qty", 0)

        if action == "buy":
            # 추가 매수 = target - current (target만큼 보유 의도)
            add_qty = max(0, target_qty - current_qty)
            cost = add_qty * price
            if cost > cash:
                add_qty = int(cash // price)
                cost = add_qty * price
            if add_qty > 0:
                # 평단 업데이트
                if ticker not in positions:
                    positions[ticker] = {"qty": 0, "avg_cost": 0.0}
                old_qty = positions[ticker]["qty"]
                old_cost = positions[ticker]["avg_cost"] * old_qty
                new_qty = old_qty + add_qty
                new_avg = (old_cost + cost) / new_qty
                positions[ticker]["qty"] = new_qty
                positions[ticker]["avg_cost"] = new_avg
                cash -= cost
                total_buy_value += cost
                trade_log.append({
                    "date": date, "ticker": ticker, "action": "buy",
                    "qty": add_qty, "price": price, "cost": round(cost, 2),
                    "cash_after": round(cash, 2),
                })
                total_trades += 1
        elif action == "sell_all":
            if current_qty > 0:
                proceeds = current_qty * price
                cash += proceeds
                total_sell_value += proceeds
                trade_log.append({
                    "date": date, "ticker": ticker, "action": "sell_all",
                    "qty": current_qty, "price": price, "proceeds": round(proceeds, 2),
                    "cash_after": round(cash, 2),
                })
                positions.pop(ticker, None)
                total_trades += 1
        elif action == "sell_partial":
            sell_qty = current_qty // 2
            if sell_qty > 0:
                proceeds = sell_qty * price
                cash += proceeds
                positions[ticker]["qty"] -= sell_qty
                total_sell_value += proceeds
                trade_log.append({
                    "date": date, "ticker": ticker, "action": "sell_partial",
                    "qty": sell_qty, "price": price, "proceeds": round(proceeds, 2),
                    "cash_after": round(cash, 2),
                })
                total_trades += 1
        # hold는 아무 trade 없음

    # 최종 NAV @ end_date
    end_positions_value = 0.0
    final_positions = {}
    for ticker, pos in positions.items():
        last_price = fetch_close(ticker, end_date)
        if last_price is None:
            last_price = pos["avg_cost"]  # fallback
        market_value = pos["qty"] * last_price
        unrealized_pnl = market_value - pos["avg_cost"] * pos["qty"]
        end_positions_value += market_value
        final_positions[ticker] = {
            "qty": pos["qty"],
            "avg_cost": round(pos["avg_cost"], 2),
            "last_price": round(last_price, 2),
            "market_value": round(market_value, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
            "unrealized_return_pct": round((last_price / pos["avg_cost"] - 1) * 100, 2)
                                      if pos["avg_cost"] > 0 else 0,
        }

    final_nav = cash + end_positions_value
    total_return_pct = (final_nav / start_cash - 1) * 100

    # Benchmark 비교
    benchmark_returns = {}
    first_date = decisions_sorted[0]["date"] if decisions_sorted else end_date
    for b in benchmarks:
        ticker = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "SPY": "SPY"}.get(b, b)
        p_start = fetch_close(ticker, first_date)
        p_end = fetch_close(ticker, end_date)
        if p_start and p_end:
            bench_return = (p_end / p_start - 1) * 100
            benchmark_returns[b] = {
                "start_price": round(p_start, 2),
                "end_price": round(p_end, 2),
                "return_pct": round(bench_return, 3),
                "alpha_pct": round(total_return_pct - bench_return, 3),
            }

    return {
        "computed_at": datetime.now(KST).isoformat(),
        "start_cash": start_cash,
        "start_date": first_date,
        "end_date": end_date,
        "n_decisions": len(decisions_sorted),
        "total_trades": total_trades,
        "total_buy_value": round(total_buy_value, 2),
        "total_sell_value": round(total_sell_value, 2),
        "final_cash": round(cash, 2),
        "end_positions_value": round(end_positions_value, 2),
        "final_nav": round(final_nav, 2),
        "total_return_pct": round(total_return_pct, 3),
        "final_positions": final_positions,
        "trade_log": trade_log,
        "benchmark_comparison": benchmark_returns,
    }


def main():
    parser = argparse.ArgumentParser(description="Paper Portfolio simulation")
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--start-cash", type=float, default=1_000_000)
    parser.add_argument("--end-date", required=True)
    parser.add_argument("--benchmarks", default="KOSPI,SPY")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.decisions, encoding="utf-8") as f:
        d = json.load(f)
    benchmarks = [b.strip() for b in args.benchmarks.split(",") if b.strip()]

    result = simulate(d.get("decisions", []), args.start_cash, args.end_date, benchmarks)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n=== Paper Portfolio Result ===")
    print(f"  Start: ${result['start_cash']:,.0f} @ {result['start_date']}")
    print(f"  End:   ${result['final_nav']:,.2f} @ {result['end_date']}")
    print(f"  Total return: {result['total_return_pct']:+.2f}%")
    print(f"  Trades: {result['total_trades']}")
    print(f"  Cash: ${result['final_cash']:,.2f}")
    print(f"  Positions value: ${result['end_positions_value']:,.2f}")
    print()
    print("  Final Positions:")
    for t, p in result["final_positions"].items():
        print(f"    {t:12s} qty={p['qty']:>6} avg=${p['avg_cost']:>10,.2f} "
              f"last=${p['last_price']:>10,.2f} unrealized={p['unrealized_return_pct']:+.2f}%")
    print()
    print("  Benchmark Comparison:")
    for b, m in result["benchmark_comparison"].items():
        print(f"    {b}: {m['return_pct']:+.2f}% (alpha {m['alpha_pct']:+.2f}%)")
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
