#!/usr/bin/env python3
"""thesis_eval 결과에서 confidence < threshold 인 약한 thesis 식별."""
import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Identify weak theses")
    parser.add_argument("--thesis-list", required=True, help="thesis_list.json")
    parser.add_argument("--eval-dir", required=True, help="thesis_eval 디렉토리")
    parser.add_argument("--min-confidence", type=float, default=0.5)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    with open(args.thesis_list, encoding="utf-8") as f:
        theses = json.load(f).get("theses", [])

    eval_path = Path(args.eval_dir) / "all_aggregate.json"
    if not eval_path.exists():
        raise SystemExit(f"all_aggregate.json 미존재: {eval_path}")

    with open(eval_path, encoding="utf-8") as f:
        agg_data = json.load(f)

    aggregates = {a["claim_id"]: a for a in agg_data.get("aggregates", [])}
    weak = []

    for t in theses:
        cid = t.get("claim_id")
        agg = aggregates.get(cid, {})
        conf = (agg.get("aggregate") or {}).get("weighted_confidence", 0)
        agreement = (agg.get("aggregate") or {}).get("agreement_level", "")

        is_weak = False
        why = []
        if conf < args.min_confidence:
            is_weak = True
            why.append(f"confidence {conf} < {args.min_confidence}")
        if "split" in agreement.lower() or "low" in agreement.lower():
            is_weak = True
            why.append(f"agreement={agreement}")

        if is_weak:
            weak.append({
                "claim_id": cid,
                "claim": t.get("claim"),
                "type": t.get("type"),
                "importance": t.get("importance"),
                "current_confidence": conf,
                "current_stance": (agg.get("aggregate") or {}).get("weighted_stance"),
                "agreement_level": agreement,
                "why_weak": why,
                "supporting_evidence": t.get("supporting_evidence", "")[:600],
                "additional_evidence": [],
                "refinement_history": [],
            })

    out = {
        "min_confidence": args.min_confidence,
        "n_total_theses": len(theses),
        "n_weak": len(weak),
        "weak_theses": weak,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n[identify_weak] {len(weak)}/{len(theses)}개 thesis가 보강 대상")
    for w in weak:
        print(f"  [{w['claim_id']}] conf={w['current_confidence']:.2f} ({', '.join(w['why_weak'])})")
        print(f"    {w['claim'][:80]}")
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
