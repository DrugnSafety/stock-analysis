#!/usr/bin/env python3
"""부모 Claude가 호출하는 state helper 스크립트들.

debate-orchestrator의 절차에서 호출되는 작은 단일-목적 명령어들.
"""
import argparse
import json
import sys
from pathlib import Path

# Common utils import
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "_common"))

from state_utils import (
    init_debate_state, save_state, load_state, append_round, finalize, KST
)
from convergence import calc_convergence, should_continue
from datetime import datetime


def cmd_init(args):
    """state 초기화."""
    state = init_debate_state(
        ticker=args.ticker,
        max_rounds=args.max_rounds,
        convergence_threshold=args.convergence_threshold,
    )
    save_state(state, args.output)
    print(f"[init] {args.ticker} debate state saved: {args.output}")


def cmd_append(args):
    """round 결과 누적."""
    state = load_state(args.state)
    state["round"] = state.get("round", 0) + 1

    for role, path in [("bull", args.bull), ("bear", args.bear),
                       ("skeptic", args.skeptic)]:
        if not path:
            continue
        try:
            with open(path, encoding="utf-8") as f:
                txt = f.read().strip()
            # JSON 또는 ```json 블록 처리
            if txt.startswith("```"):
                txt = txt.split("```", 2)[1]
                if txt.startswith("json"):
                    txt = txt[4:]
                txt = txt.rsplit("```", 1)[0]
            result = json.loads(txt)
            append_round(state, role, result)
            print(f"  appended {role}: verdict={result.get('verdict', '?')} "
                  f"conf={result.get('confidence', 0)}")
        except Exception as e:
            print(f"  [WARN] {role} append failed: {e}")

    score = calc_convergence(state)
    state["convergence_score"] = score
    save_state(state, args.state)
    print(f"[append] round={state['round']}, convergence={score}")


def cmd_check(args):
    """다음 round 진행 여부."""
    state = load_state(args.state)
    cont, reason = should_continue(state)
    state["convergence_score"] = state.get("convergence_score") or calc_convergence(state)
    save_state(state, args.state)

    result = {
        "continue": cont,
        "reason": reason,
        "current_round": state.get("round"),
        "max_rounds": state.get("max_rounds"),
        "convergence_score": state.get("convergence_score"),
        "next_action": "round_" + str(state.get("round", 0) + 1) if cont else "consolidate",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_finalize(args):
    """최종 verdict 저장 + ledger append."""
    state = load_state(args.state)
    if args.consolidator:
        with open(args.consolidator, encoding="utf-8") as f:
            txt = f.read().strip()
        if txt.startswith("```"):
            txt = txt.split("```", 2)[1]
            if txt.startswith("json"):
                txt = txt[4:]
            txt = txt.rsplit("```", 1)[0]
        consol = json.loads(txt)
        state["final_verdict"] = consol.get("final_verdict")
        state["final_confidence"] = consol.get("final_confidence")
        state["consolidation_reasoning"] = consol.get("consolidation_reasoning")
        state["final_data"] = consol

    state = finalize(state)
    save_state(state, args.state)

    # Ledger append
    if args.ledger:
        record = {
            "record_id": f"sa_debate_{state['ticker'].replace('.', '_')}_{datetime.now(KST).strftime('%Y%m%d_%H%M')}",
            "date": datetime.now(KST).strftime("%Y-%m-%d"),
            "ticker": state["ticker"],
            "verdict": state.get("final_verdict") or "UNKNOWN",
            "confidence": state.get("final_confidence") or 0,
            "source": "subagent-debate",
            "persona": "consolidated",
            "blog_url": "",
            "rounds": state.get("round"),
            "convergence_score": state.get("convergence_score"),
            "subagent_spawns": state.get("total_subagent_spawns"),
        }
        Path(args.ledger).parent.mkdir(parents=True, exist_ok=True)
        with open(args.ledger, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        print(f"[finalize] ledger appended: {args.ledger}")

    print(f"[finalize] final_verdict={state.get('final_verdict')} "
          f"conf={state.get('final_confidence')}")


def main():
    parser = argparse.ArgumentParser(description="Debate state helpers")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init")
    p_init.add_argument("--ticker", required=True)
    p_init.add_argument("--max-rounds", type=int, default=3)
    p_init.add_argument("--convergence-threshold", type=float, default=0.85)
    p_init.add_argument("--output", required=True)

    p_app = sub.add_parser("append")
    p_app.add_argument("--state", required=True)
    p_app.add_argument("--bull")
    p_app.add_argument("--bear")
    p_app.add_argument("--skeptic")

    p_chk = sub.add_parser("check")
    p_chk.add_argument("--state", required=True)

    p_fin = sub.add_parser("finalize")
    p_fin.add_argument("--state", required=True)
    p_fin.add_argument("--consolidator", help="consolidator subagent output JSON")
    p_fin.add_argument("--ledger", help="ledger.jsonl path to append")

    args = parser.parse_args()
    if args.cmd == "init":
        cmd_init(args)
    elif args.cmd == "append":
        cmd_append(args)
    elif args.cmd == "check":
        cmd_check(args)
    elif args.cmd == "finalize":
        cmd_finalize(args)


if __name__ == "__main__":
    main()
