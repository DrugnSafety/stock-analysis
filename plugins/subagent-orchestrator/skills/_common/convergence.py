"""Bull-Bear 합의 점수 계산."""
import json
import sys


VERDICT_NUMERIC = {
    "BUY": 1.0, "buy": 1.0,
    "lean_bullish": 0.7,
    "HOLD": 0.0, "hold": 0.0, "neutral": 0.0,
    "lean_bearish": -0.7,
    "SELL": -1.0, "sell": -1.0,
    "UNKNOWN": 0.0,
}


def to_numeric(verdict: str) -> float:
    return VERDICT_NUMERIC.get(verdict, 0.0)


def calc_convergence(state: dict) -> float:
    """직전 round의 Bull/Bear/Skeptic stance를 종합한 합의 점수 (0-1).

    높을수록 의견 일치. 0.85 이상이면 토론 종료 권장.
    """
    bull = state.get("bull_history", [])
    bear = state.get("bear_history", [])
    skeptic = state.get("skeptic_history", [])

    if not bull or not bear:
        return 0.0

    last_bull = bull[-1]
    last_bear = bear[-1]

    # Verdict 일치도
    bv = to_numeric(last_bull.get("verdict", "UNKNOWN"))
    rv = to_numeric(last_bear.get("verdict", "UNKNOWN"))
    # 두 verdict가 같은 방향이고 차이가 작으면 합의 ↑
    verdict_alignment = 1.0 - abs(bv - rv) / 2.0  # 0-1

    # Confidence 평균
    bc = last_bull.get("confidence", 0.5)
    rc = last_bear.get("confidence", 0.5)
    avg_conf = (bc + rc) / 2

    # Round 안정성 — 직전 round 대비 변화 적으면 안정
    if len(bull) >= 2 and len(bear) >= 2:
        prev_bv = to_numeric(bull[-2].get("verdict", "UNKNOWN"))
        prev_rv = to_numeric(bear[-2].get("verdict", "UNKNOWN"))
        bull_change = abs(bv - prev_bv) / 2.0
        bear_change = abs(rv - prev_rv) / 2.0
        stability = 1.0 - (bull_change + bear_change) / 2
    else:
        stability = 0.5  # 첫 round는 중간

    # Skeptic의 합의 평가 (있으면)
    skeptic_score = 0.5
    if skeptic:
        last_sk = skeptic[-1]
        agreement = (last_sk.get("agreement_assessment", "") or "").lower()
        if "high" in agreement or "수렴" in agreement or "합의" in agreement:
            skeptic_score = 1.0
        elif "split" in agreement or "분열" in agreement:
            skeptic_score = 0.0
        elif "medium" in agreement or "부분" in agreement:
            skeptic_score = 0.5

    # 가중 평균
    score = (verdict_alignment * 0.40 +
             avg_conf * 0.20 +
             stability * 0.25 +
             skeptic_score * 0.15)

    return round(score, 3)


def should_continue(state: dict) -> tuple[bool, str]:
    """다음 round 진행 여부 판단."""
    if state.get("round", 0) >= state.get("max_rounds", 3):
        return False, f"max_rounds ({state['max_rounds']}) 도달 — 종료"
    score = calc_convergence(state)
    state["convergence_score"] = score
    if score >= state.get("convergence_threshold", 0.85):
        return False, f"convergence {score} >= threshold — 합의 도달"
    return True, f"convergence {score} < threshold — round {state['round']+1} 진행"


if __name__ == "__main__":
    if len(sys.argv) > 1:
        state = json.load(open(sys.argv[1]))
        cont, reason = should_continue(state)
        print(f"continue={cont}, reason={reason}")
        print(f"score={state.get('convergence_score')}")
