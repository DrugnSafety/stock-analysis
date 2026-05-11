#!/usr/bin/env python3
"""Portfolio Manager — verdict aggregate → trade decision."""
import argparse
import json
import math
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path


KST = timezone(timedelta(hours=9))


VERDICT_SCORE = {
    "BUY": 1.0, "buy": 1.0,
    "lean_bullish": 0.7,
    "HOLD": 0.0, "hold": 0.0, "neutral": 0.0,
    "lean_bearish": -0.7,
    "SELL": -1.0, "sell": -1.0,
    "UNKNOWN": 0.0,
}


# Phase C 결과 반영 — 한국 시장 적합도
DEFAULT_WEIGHTS_KR = {
    "stanley-druckenmiller": 1.5,
    "peter-lynch": 1.3,
    "warren-buffett": 0.7,
    "thesis-first": 1.2,
    # 나머지: 1.0 (default)
}

DEFAULT_WEIGHTS_GLOBAL = {
    "stanley-druckenmiller": 1.2,
    "peter-lynch": 1.1,
    "warren-buffett": 1.2,
    "thesis-first": 1.1,
}


def is_kr_ticker(ticker: str) -> bool:
    return ticker.endswith(".KS") or ticker.endswith(".KQ")


def get_persona_weight(persona_or_source: str, is_kr: bool, custom: dict = None) -> float:
    """페르소나 또는 source의 가중치 반환."""
    if custom and persona_or_source in custom:
        return custom[persona_or_source]
    table = DEFAULT_WEIGHTS_KR if is_kr else DEFAULT_WEIGHTS_GLOBAL
    return table.get(persona_or_source, 1.0)


def aggregate_verdicts(group: list[dict], is_kr: bool, weights_config: dict = None) -> dict:
    """verdict 그룹 → signal_score + breakdown."""
    breakdown = defaultdict(int)
    weighted_sum = 0.0
    total_weight = 0.0
    contributions = {}

    for v in group:
        verdict = v.get("verdict", "UNKNOWN")
        confidence = v.get("confidence", 0.5)
        source = v.get("source", "unknown")
        persona = v.get("persona") or ""

        # weight key 결정 — persona 있으면 persona, 없으면 source
        weight_key = persona if persona else source
        weight = get_persona_weight(weight_key, is_kr, weights_config)

        score = VERDICT_SCORE.get(verdict, 0.0)
        contribution = score * confidence * weight
        weighted_sum += contribution
        total_weight += confidence * weight

        breakdown[verdict] += 1
        contributions[weight_key] = {
            "verdict": verdict,
            "confidence": confidence,
            "weight": weight,
            "score_contribution": round(contribution, 3),
        }

    signal_score = weighted_sum / total_weight if total_weight > 0 else 0.0
    weighted_conf = total_weight / sum(v.get("confidence", 0.5) for v in group) \
                    / max(len(group), 1) if group else 0.0

    return {
        "n_verdicts": len(group),
        "verdict_breakdown": dict(breakdown),
        "signal_score": round(signal_score, 4),
        "weighted_confidence": round(min(weighted_conf, 1.0), 3),
        "persona_contributions": contributions,
    }


def decide_action(signal_score: float) -> tuple[str, float, str]:
    """signal_score → (action, size_factor, reasoning)."""
    if signal_score >= 0.7:
        return "buy", 1.0, f"강한 매수 신호 ({signal_score:+.2f}), 한도까지 진입"
    if signal_score >= 0.3:
        return "buy", 0.5, f"중간 매수 신호 ({signal_score:+.2f}), 한도의 50% 진입"
    if signal_score >= -0.3:
        return "hold", 0.0, f"중립 신호 ({signal_score:+.2f}), 변경 없음"
    if signal_score >= -0.7:
        return "sell_partial", 0.5, f"중간 매도 신호 ({signal_score:+.2f}), 보유분 50% 청산"
    return "sell_all", 1.0, f"강한 매도 신호 ({signal_score:+.2f}), 보유분 전량 청산"


def make_decisions(ledger: list[dict], risk_limits: dict,
                   weights_config: dict = None) -> list[dict]:
    # Group by (ticker, date)
    groups = defaultdict(list)
    for r in ledger:
        t = r.get("ticker")
        d = r.get("date") or r.get("verdict_date")
        if t and d:
            groups[(t, d)].append(r)

    # Index limits by (ticker, date)
    limits_by_pair = {}
    for r in risk_limits.get("limits", []):
        if "error" not in r:
            limits_by_pair[(r["ticker"], r["as_of_date"])] = r

    decisions = []
    for (ticker, date), verdicts in sorted(groups.items()):
        agg = aggregate_verdicts(verdicts, is_kr_ticker(ticker), weights_config)
        action, size_factor, reasoning = decide_action(agg["signal_score"])

        risk = limits_by_pair.get((ticker, date))
        if not risk:
            decisions.append({
                "ticker": ticker, "date": date,
                **agg,
                "action": action,
                "error": "risk limit unavailable",
            })
            continue

        target_value = risk["position_limit_value"] * size_factor
        current_price = risk.get("current_price", 0)
        target_quantity = int(target_value // current_price) if current_price > 0 else 0

        decisions.append({
            "ticker": ticker,
            "date": date,
            **agg,
            "action": action,
            "size_factor": size_factor,
            "target_value": round(target_value, 2),
            "target_quantity": target_quantity,
            "current_price": current_price,
            "position_limit_value": risk["position_limit_value"],
            "annualized_volatility": risk.get("volatility_metrics", {}).get("annualized_volatility"),
            "reasoning": reasoning,
        })

    return decisions


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
    parser = argparse.ArgumentParser(description="Portfolio Manager — make trade decisions")
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--risk-limits", required=True)
    parser.add_argument("--weights-config", help="JSON 파일")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    ledger = load_ledger(Path(args.ledger))
    with open(args.risk_limits, encoding="utf-8") as f:
        risk_limits = json.load(f)

    weights_config = None
    if args.weights_config:
        with open(args.weights_config, encoding="utf-8") as f:
            weights_config = json.load(f)

    decisions = make_decisions(ledger, risk_limits, weights_config)

    out = {
        "computed_at": datetime.now(KST).isoformat(),
        "ledger_path": args.ledger,
        "risk_limits_path": args.risk_limits,
        "n_decisions": len(decisions),
        "decisions": decisions,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n=== Portfolio Manager — {len(decisions)} decisions ===")
    for d in decisions:
        if "error" in d:
            print(f"  {d['date']} {d['ticker']:12s} {d['action']:14s} ERROR: {d['error']}")
            continue
        print(f"  {d['date']} {d['ticker']:12s} signal={d['signal_score']:+.2f} "
              f"→ {d['action']:14s} qty={d['target_quantity']:>6}주 "
              f"(${d['target_value']:>10,.0f}, {d['n_verdicts']} verdicts)")
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
