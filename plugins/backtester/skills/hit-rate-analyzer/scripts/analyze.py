#!/usr/bin/env python3
"""Hit Rate Analyzer — backtest 결과 → 적중률·alpha·calibration."""
import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


def normalize_verdict(v: str) -> str:
    """다양한 verdict 표현을 BUY/HOLD/SELL로 통일."""
    if not v:
        return "UNKNOWN"
    v_lower = v.lower()
    if "bull" in v_lower or "buy" in v_lower:
        return "BUY"
    if "bear" in v_lower or "sell" in v_lower:
        return "SELL"
    if "hold" in v_lower or "neutral" in v_lower:
        return "HOLD"
    return "UNKNOWN"


def is_hit(verdict_norm: str, raw_return_pct: float, t_buy: float, t_hold: float, t_sell: float) -> bool:
    if verdict_norm == "BUY":
        return raw_return_pct >= t_buy
    if verdict_norm == "SELL":
        return raw_return_pct <= t_sell
    if verdict_norm == "HOLD":
        return -t_hold <= raw_return_pct <= t_hold
    return False


def calc_calibration(verdicts_with_data: list) -> dict:
    """confidence bucket별 적중률 + ECE."""
    buckets = [
        ("80-100", 0.80, 1.01),
        ("60-80", 0.60, 0.80),
        ("40-60", 0.40, 0.60),
        ("0-40", 0.0, 0.40),
    ]
    out = []
    weighted_calibration_error = 0.0
    total = len(verdicts_with_data)
    if total == 0:
        return {"buckets": [], "ece": 0, "brier_score": 0}

    brier_sum = 0.0
    for label, lo, hi in buckets:
        items = [v for v in verdicts_with_data
                 if lo <= v.get("confidence", 0) < hi]
        if not items:
            out.append({"range": label, "n": 0, "predicted": 0, "actual": 0})
            continue
        avg_conf = sum(v.get("confidence", 0) for v in items) / len(items)
        actual_rate = sum(1 for v in items if v.get("hit")) / len(items)
        bucket_ce = abs(avg_conf - actual_rate) * len(items) / total
        weighted_calibration_error += bucket_ce
        # Brier — per item, but rough averaging
        for v in items:
            outcome = 1 if v.get("hit") else 0
            brier_sum += (v.get("confidence", 0) - outcome) ** 2

        out.append({
            "range": label,
            "n": len(items),
            "predicted": round(avg_conf, 3),
            "actual": round(actual_rate, 3),
        })

    return {
        "buckets": out,
        "ece": round(weighted_calibration_error, 4),
        "brier_score": round(brier_sum / max(total, 1), 4),
    }


def analyze_horizon(verdicts: list, horizon: str, t_buy: float, t_hold: float,
                     t_sell: float, benchmarks: list[str]) -> dict:
    """단일 horizon에 대한 종합 분석."""
    valid = []  # verdicts with sufficient data for this horizon
    for v in verdicts:
        h_result = v.get("results", {}).get(horizon, {})
        if not h_result.get("sufficient_data"):
            continue
        verdict_norm = normalize_verdict(v.get("verdict"))
        raw_return = h_result.get("raw_return_pct", 0)
        hit = is_hit(verdict_norm, raw_return, t_buy, t_hold, t_sell)
        valid.append({
            "ticker": v.get("ticker"),
            "verdict": verdict_norm,
            "verdict_raw": v.get("verdict"),
            "confidence": v.get("confidence", 0),
            "source": v.get("source", "unknown"),
            "persona": v.get("persona", v.get("_meta", {}).get("persona_id", "")),
            "raw_return_pct": raw_return,
            "hit": hit,
            "alpha": {b: h_result.get(f"alpha_{b}_pct") for b in benchmarks},
        })

    n_valid = len(valid)
    if n_valid == 0:
        return {"n_valid": 0, "note": "no verdicts with sufficient data for this horizon"}

    # Overall by verdict type
    by_verdict = defaultdict(lambda: {"hit": 0, "total": 0, "rates": []})
    for v in valid:
        by_verdict[v["verdict"]]["hit"] += 1 if v["hit"] else 0
        by_verdict[v["verdict"]]["total"] += 1
        by_verdict[v["verdict"]]["rates"].append(v["raw_return_pct"])

    overall = {}
    for vt, d in by_verdict.items():
        avg_return = sum(d["rates"]) / max(len(d["rates"]), 1)
        overall[f"{vt}_hit"] = d["hit"]
        overall[f"{vt}_total"] = d["total"]
        overall[f"{vt}_rate"] = round(d["hit"] / max(d["total"], 1), 3)
        overall[f"{vt}_avg_return_pct"] = round(avg_return, 2)

    # By source
    by_source = defaultdict(lambda: {"hit": 0, "total": 0})
    for v in valid:
        by_source[v["source"]]["hit"] += 1 if v["hit"] else 0
        by_source[v["source"]]["total"] += 1

    by_source_summary = {
        s: {"hit": d["hit"], "total": d["total"],
            "rate": round(d["hit"] / max(d["total"], 1), 3)}
        for s, d in by_source.items()
    }

    # By persona (only persona-panel source)
    by_persona = defaultdict(lambda: {"hit": 0, "total": 0, "confidences": [], "returns": []})
    for v in valid:
        if v["persona"]:
            by_persona[v["persona"]]["hit"] += 1 if v["hit"] else 0
            by_persona[v["persona"]]["total"] += 1
            by_persona[v["persona"]]["confidences"].append(v["confidence"])
            by_persona[v["persona"]]["returns"].append(v["raw_return_pct"])

    by_persona_summary = {}
    for p, d in by_persona.items():
        avg_conf = sum(d["confidences"]) / max(len(d["confidences"]), 1)
        avg_ret = sum(d["returns"]) / max(len(d["returns"]), 1)
        by_persona_summary[p] = {
            "hit": d["hit"],
            "total": d["total"],
            "rate": round(d["hit"] / max(d["total"], 1), 3),
            "avg_confidence": round(avg_conf, 3),
            "avg_return_pct": round(avg_ret, 2),
        }

    # Alpha (BUY 종목 평균)
    buy_verdicts = [v for v in valid if v["verdict"] == "BUY"]
    alpha_summary = {}
    for b in benchmarks:
        alphas = [v["alpha"].get(b) for v in buy_verdicts if v["alpha"].get(b) is not None]
        if alphas:
            alpha_summary[f"vs_{b}_avg_pct"] = round(sum(alphas) / len(alphas), 2)
            alpha_summary[f"vs_{b}_n"] = len(alphas)

    # Calibration
    cal = calc_calibration(valid)

    return {
        "n_valid": n_valid,
        "overall": overall,
        "by_source": by_source_summary,
        "by_persona": by_persona_summary,
        "alpha": alpha_summary,
        "calibration": cal,
    }


def main():
    parser = argparse.ArgumentParser(description="Hit rate analyzer")
    parser.add_argument("backtest_json")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--buy-threshold", type=float, default=5.0)
    parser.add_argument("--hold-band", type=float, default=3.0)
    parser.add_argument("--sell-threshold", type=float, default=-5.0)
    parser.add_argument("--horizon", help="단일 horizon만")
    args = parser.parse_args()

    with open(args.backtest_json, encoding="utf-8") as f:
        bt = json.load(f)

    verdicts = bt.get("verdicts", [])
    horizons = [args.horizon] if args.horizon else bt.get("horizons", [])
    benchmarks = bt.get("benchmarks", ["KOSPI", "SPY"])

    n_with_any_data = sum(
        1 for v in verdicts
        if any(h.get("sufficient_data") for h in v.get("results", {}).values())
    )

    summary = {
        "ran_at": datetime.now(KST).isoformat(),
        "input_path": args.backtest_json,
        "n_verdicts_total": len(verdicts),
        "n_verdicts_with_data": n_with_any_data,
        "thresholds": {
            "buy": args.buy_threshold,
            "hold_band": args.hold_band,
            "sell": args.sell_threshold,
        },
        "benchmarks": benchmarks,
        "horizons": {},
    }

    for h in horizons:
        summary["horizons"][h] = analyze_horizon(
            verdicts, h, args.buy_threshold, args.hold_band, args.sell_threshold,
            benchmarks
        )

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Console summary
    print(f"\n=== Hit Rate Summary ===")
    print(f"  총 verdict: {len(verdicts)}")
    print(f"  데이터 충분한 verdict: {n_with_any_data}")
    print()
    for h, hd in summary["horizons"].items():
        if hd.get("n_valid", 0) == 0:
            print(f"  [{h}] 데이터 없음 — {hd.get('note', '')}")
            continue
        print(f"  [{h}] (n={hd['n_valid']})")
        ov = hd["overall"]
        for vt in ["BUY", "HOLD", "SELL"]:
            if f"{vt}_total" in ov and ov[f"{vt}_total"]:
                print(f"    {vt}: {ov[f'{vt}_hit']}/{ov[f'{vt}_total']} "
                      f"({int(ov[f'{vt}_rate']*100)}%)")
        if hd.get("alpha"):
            for k, v in hd["alpha"].items():
                if "_avg_pct" in k:
                    print(f"    Alpha {k}: {v:+.2f}%")
        if hd.get("calibration", {}).get("ece") is not None:
            print(f"    ECE: {hd['calibration']['ece']}, "
                  f"Brier: {hd['calibration']['brier_score']}")

    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
