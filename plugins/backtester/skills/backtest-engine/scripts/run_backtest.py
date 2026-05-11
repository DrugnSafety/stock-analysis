#!/usr/bin/env python3
"""Backtest Engine — verdict ledger에 사후 수익률 부여."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


HORIZON_DAYS = {
    "1w": 7, "2w": 14, "1m": 30, "3m": 90, "6m": 180, "12m": 365,
}

BENCHMARKS = {"KOSPI": "^KS11", "KOSDAQ": "^KQ11", "SPY": "SPY"}


def parse_horizons(s: str) -> list[str]:
    return [h.strip() for h in s.split(",") if h.strip() in HORIZON_DAYS]


def fetch_price(ticker: str, target_date: str, window_days: int = 5):
    """target_date 근처의 거래일 종가 fetch.
    target_date 이후 첫 거래일 우선 (entry는 +1, exit은 +0)."""
    import yfinance as yf
    from datetime import datetime as _dt, timedelta as _td

    try:
        td = _dt.strptime(target_date, "%Y-%m-%d")
    except ValueError:
        return None, None

    start = (td - _td(days=window_days)).strftime("%Y-%m-%d")
    end = (td + _td(days=window_days + 1)).strftime("%Y-%m-%d")

    try:
        df = yf.Ticker(ticker).history(start=start, end=end, auto_adjust=False)
        if df.empty:
            return None, None
        df = df.sort_index()
        # target_date 이상의 첫 거래일
        df = df[df.index >= td.replace(tzinfo=df.index.tz)] if df.index.tz else df[df.index >= td]
        if df.empty:
            return None, None
        first = df.iloc[0]
        return float(first["Close"]), first.name.strftime("%Y-%m-%d")
    except Exception as e:
        print(f"    fetch_price({ticker}, {target_date}) error: {e}", file=sys.stderr)
        return None, None


def compute_horizon(verdict_date: str, horizon: str) -> str:
    """verdict_date + horizon → exit target date."""
    from datetime import datetime as _dt, timedelta as _td
    td = _dt.strptime(verdict_date, "%Y-%m-%d")
    days = HORIZON_DAYS[horizon]
    return (td + _td(days=days)).strftime("%Y-%m-%d")


def is_horizon_reached(verdict_date: str, horizon: str, today: str) -> bool:
    target = compute_horizon(verdict_date, horizon)
    return target <= today


def backtest_one(verdict: dict, horizons: list[str], benchmarks: list[str],
                 today: str) -> dict:
    """단일 verdict에 대한 backtest."""
    ticker = verdict.get("ticker")
    vdate = verdict.get("date") or verdict.get("verdict_date")
    if not ticker or not vdate:
        return {**verdict, "error": "missing ticker or date"}

    # Entry price (verdict_date +1 거래일)
    from datetime import datetime as _dt, timedelta as _td
    entry_target = (_dt.strptime(vdate, "%Y-%m-%d") + _td(days=1)).strftime("%Y-%m-%d")
    entry_price, entry_actual = fetch_price(ticker, entry_target)

    if entry_price is None:
        return {**verdict, "error": f"entry price not available for {ticker} near {entry_target}"}

    results = {}
    for h in horizons:
        if not is_horizon_reached(vdate, h, today):
            results[h] = {"sufficient_data": False, "reason": "horizon not yet reached"}
            continue

        exit_target = compute_horizon(vdate, h)
        exit_price, exit_actual = fetch_price(ticker, exit_target)
        if exit_price is None:
            results[h] = {"sufficient_data": False, "reason": "exit price unavailable"}
            continue

        raw_return = (exit_price / entry_price - 1) * 100

        bench_results = {}
        for bname in benchmarks:
            byti = BENCHMARKS.get(bname, bname)
            be, _ = fetch_price(byti, entry_target)
            bx, _ = fetch_price(byti, exit_target)
            if be and bx:
                bench_return = (bx / be - 1) * 100
                bench_results[f"benchmark_{bname}_return_pct"] = round(bench_return, 3)
                bench_results[f"alpha_{bname}_pct"] = round(raw_return - bench_return, 3)

        results[h] = {
            "exit_date": exit_actual,
            "exit_price": exit_price,
            "raw_return_pct": round(raw_return, 3),
            **bench_results,
            "sufficient_data": True,
        }

    return {
        **verdict,
        "entry_price": entry_price,
        "entry_date": entry_actual,
        "results": results,
    }


def load_ledger(path: Path) -> list[dict]:
    """ledger.jsonl 또는 일반 JSON 모두 지원."""
    if not path.exists():
        return []
    txt = path.read_text(encoding="utf-8").strip()
    if not txt:
        return []

    # JSON array?
    if txt.startswith("["):
        return json.loads(txt)

    # JSONL
    records = []
    for line in txt.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def main():
    parser = argparse.ArgumentParser(description="Backtest engine")
    parser.add_argument("--ledger", required=True, help="JSONL 또는 JSON array")
    parser.add_argument("--horizons", default="1m,3m,6m,12m")
    parser.add_argument("--benchmark", default="KOSPI,SPY")
    parser.add_argument("--filter-source", help="특정 source만 (thesis-first/persona-panel/...)")
    parser.add_argument("--filter-ticker", help="특정 ticker만")
    parser.add_argument("--today", default="", help="기준일 (기본: 시스템 날짜)")
    parser.add_argument("--max-records", type=int, default=0,
                        help="처리 record 수 제한 (debug용)")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    today = args.today or datetime.now(KST).strftime("%Y-%m-%d")
    horizons = parse_horizons(args.horizons)
    benchmarks = [b.strip() for b in args.benchmark.split(",") if b.strip()]

    records = load_ledger(Path(args.ledger))
    # Filter — analysis records만 (verdict 있는 것)
    records = [r for r in records if r.get("verdict") or r.get("type") == "analysis"]
    # type="analysis" 형식의 ledger인 경우 verdict는 안에 있음
    for r in records:
        if "verdict" not in r and "type" in r:
            # naver-blog-investment ledger 형식 호환
            r["verdict"] = r.get("verdict") or r.get("data", {}).get("verdict")

    if args.filter_source:
        records = [r for r in records if r.get("source") == args.filter_source]
    if args.filter_ticker:
        records = [r for r in records if r.get("ticker") == args.filter_ticker]
    if args.max_records:
        records = records[:args.max_records]

    print(f"[backtest] {len(records)} verdicts × {len(horizons)} horizons "
          f"× {len(benchmarks)} benchmarks", file=sys.stderr)

    out = []
    for i, r in enumerate(records, 1):
        print(f"  [{i}/{len(records)}] {r.get('ticker')} verdict={r.get('verdict')} "
              f"date={r.get('date') or r.get('verdict_date')}", file=sys.stderr)
        result = backtest_one(r, horizons, benchmarks, today)
        out.append(result)
        time.sleep(0.2)  # rate limiting

    summary = {
        "ledger_path": args.ledger,
        "ran_at": datetime.now(KST).isoformat(),
        "today": today,
        "n_verdicts": len(out),
        "horizons": horizons,
        "benchmarks": benchmarks,
        "verdicts": out,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    n_hits_with_data = sum(
        1 for v in out
        for h in v.get("results", {}).values()
        if h.get("sufficient_data")
    )
    print(f"\n[backtest] 완료: {len(out)}개 verdict, "
          f"{n_hits_with_data}개 horizon 결과 수집")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
