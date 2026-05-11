#!/usr/bin/env python3
"""Thesis Evaluator — 각 thesis를 4명의 analyst가 평가."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "api-key-manager" / "scripts"))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "thesis-extractor" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config
from extract_theses import call_openai, call_gemini, parse_json

KST = timezone(timedelta(hours=9))


ANALYST_SYSTEMS = {
    "macro": """You are a Macro Analyst evaluating an investment-related claim.
Lens: macroeconomic policy, geopolitics, trade flows, central bank action, regulation.

For the given claim, assess:
- Does it align with macro environment? (support/neutral/rebut)
- What macro variables would strengthen vs weaken it?
- Cite specific policy/macro facts (with rough dates)

Be specific. Avoid generic statements like "depends on global conditions".
Output ONLY valid JSON in the exact schema requested.""",

    "industry": """You are an Industry Analyst evaluating an investment-related claim.
Lens: industry cycles, capex flows, competitive dynamics, supply-demand at firm level.

For the given claim, assess:
- Does it align with industry structure? (support/neutral/rebut)
- What firm-level evidence would strengthen vs weaken it?
- Cite specific company actions, capex announcements, market shares

Be specific. Mention real companies and concrete numbers when possible.
Output ONLY valid JSON.""",

    "empirical": """You are an Empirical Analyst evaluating an investment-related claim.
Lens: historical precedents, quantitative data, time-series, academic research.

For the given claim, assess:
- Is there historical/quantitative evidence supporting it? (support/neutral/rebut)
- What data series or past events make this likely vs unlikely?
- Note when data is insufficient — say "neutral, insufficient data" rather than guessing

Be rigorous. Don't extrapolate beyond what data supports.
Output ONLY valid JSON.""",

    "counter": """You are a Devil's Advocate / Counter-thesis Analyst.
Lens: deliberately seek the STRONGEST counter-argument to the claim.

For the given claim:
- What is the most powerful counter-argument? (default stance: rebut)
- What hidden assumptions, if violated, would make the claim wrong?
- What alternative hypotheses fit the same evidence?

Don't be polite. Steelman the opposition.
Output ONLY valid JSON.""",
}


EVAL_USER_TEMPLATE = """Claim to evaluate:

ID: {claim_id}
Claim: "{claim}"
Type: {type}
Importance: {importance}
Timeframe: {timeframe}
Supporting evidence in original text: "{evidence}"
Tags: {tags}

Required JSON schema:
{{
  "claim_id": "{claim_id}",
  "analyst": "{analyst}",
  "stance": "support | neutral | rebut",
  "confidence": 0.0,
  "rationale": "2-4 sentences explaining your assessment",
  "supporting_data": [
    {{"point": "specific fact", "source": "policy doc / report name / inference"}}
  ],
  "counter_evidence": [
    {{"point": "fact going against", "source": "..."}}
  ],
  "key_assumption": "the assumption that must hold for the claim to be true",
  "fragility_score": 0.0
}}

Output JSON only."""


def evaluate_one(thesis: dict, analyst: str, provider: str, cfg: dict) -> dict:
    """Single (thesis, analyst, provider) evaluation."""
    user = EVAL_USER_TEMPLATE.format(
        claim_id=thesis.get("claim_id", "?"),
        claim=thesis.get("claim", ""),
        type=thesis.get("type", ""),
        importance=thesis.get("importance", ""),
        timeframe=thesis.get("timeframe", ""),
        evidence=thesis.get("supporting_evidence", "")[:1500],
        tags=thesis.get("tags", []),
        analyst=analyst,
    )
    system = ANALYST_SYSTEMS[analyst]

    start = time.time()
    if provider == "openai":
        key = get_key("OPENAI_API_KEY", required=True)
        content, usage, used = call_openai(
            key, cfg["openai"]["model"], cfg["openai"]["fallback"],
            cfg["openai"]["reasoning_effort"], system, user
        )
    else:
        key = get_key("GOOGLE_API_KEY", required=True)
        content, usage, used = call_gemini(
            key, cfg["google"]["model"], cfg["google"]["fallback"],
            cfg["google"]["deep_think"], system, user
        )
    elapsed = time.time() - start

    result = parse_json(content)
    result.setdefault("rationale_meta", {})
    result["rationale_meta"]["model_used"] = used
    result["rationale_meta"]["provider"] = provider
    result["rationale_meta"]["elapsed_seconds"] = round(elapsed, 2)
    result["rationale_meta"]["called_at"] = datetime.now(KST).isoformat()
    return result


def aggregate(thesis: dict, evals: dict[str, dict]) -> dict:
    stance_counts = {"support": 0, "neutral": 0, "rebut": 0}
    confidences = []
    for a, e in evals.items():
        s = e.get("stance", "neutral")
        if s in stance_counts:
            stance_counts[s] += 1
        confidences.append(e.get("confidence", 0))

    weighted = max(stance_counts, key=stance_counts.get)
    n = sum(stance_counts.values())
    if stance_counts[weighted] == n:
        agreement = "high (4/4)"
    elif stance_counts[weighted] >= 3:
        agreement = "medium-high (3/4)"
    elif stance_counts[weighted] == 2 and n == 4:
        agreement = "split (2/4)"
    else:
        agreement = "low"

    matching_conf = [e["confidence"] for e in evals.values()
                     if e.get("stance") == weighted]
    weighted_conf = round(sum(matching_conf) / max(len(matching_conf), 1), 3)

    # Disagreement summary
    disagreement_lines = []
    for a, e in evals.items():
        if e.get("stance") != weighted:
            disagreement_lines.append(f"{a}: {e.get('stance')} ({e.get('rationale', '')[:120]})")

    return {
        "claim_id": thesis.get("claim_id"),
        "claim": thesis.get("claim"),
        "evaluations": evals,
        "aggregate": {
            "support_count": stance_counts["support"],
            "neutral_count": stance_counts["neutral"],
            "rebut_count": stance_counts["rebut"],
            "weighted_stance": weighted,
            "weighted_confidence": weighted_conf,
            "agreement_level": agreement,
            "key_disagreement": " | ".join(disagreement_lines) if disagreement_lines else "",
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Thesis evaluator")
    parser.add_argument("thesis_json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--analysts", default="macro,industry,empirical,counter")
    parser.add_argument("--provider", choices=["openai", "gemini"], default="openai")
    parser.add_argument("--multi-model", action="store_true",
                        help="각 analyst를 다른 모델로 (macro/industry/empirical=openai, counter=gemini)")
    parser.add_argument("--include-supporting", action="store_true",
                        help="supporting thesis도 평가 (기본: core만)")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()

    with open(args.thesis_json, encoding="utf-8") as f:
        data = json.load(f)

    theses = data.get("theses", [])
    if not args.include_supporting:
        theses = [t for t in theses if t.get("importance") == "core"]

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    analysts = [a.strip() for a in args.analysts.split(",")]

    all_aggregates = []
    total_cost = 0.0

    for thesis in theses:
        cid = thesis.get("claim_id", "?")
        print(f"\n[thesis-eval] {cid}: {thesis.get('claim', '')[:80]}")
        evals = {}
        for analyst in analysts:
            if args.multi_model:
                provider = "gemini" if analyst == "counter" else "openai"
            else:
                provider = args.provider
            try:
                r = evaluate_one(thesis, analyst, provider, cfg)
                evals[analyst] = r
                with open(out_dir / f"{cid}_{analyst}.json", "w", encoding="utf-8") as f:
                    json.dump(r, f, ensure_ascii=False, indent=2)
                print(f"  [{analyst}] {r.get('stance', '?')} ({int(r.get('confidence', 0)*100)}%) — "
                      f"{r['rationale_meta'].get('elapsed_seconds')}s, {r['rationale_meta'].get('model_used')}")
            except Exception as e:
                print(f"  [{analyst}] FAILED: {str(e)[:200]}")
                evals[analyst] = {"analyst": analyst, "stance": "neutral", "confidence": 0,
                                  "error": str(e)[:300]}

        agg = aggregate(thesis, evals)
        with open(out_dir / f"{cid}_aggregate.json", "w", encoding="utf-8") as f:
            json.dump(agg, f, ensure_ascii=False, indent=2)
        all_aggregates.append(agg)
        print(f"  → AGGREGATE: {agg['aggregate']['weighted_stance']} "
              f"(conf {int(agg['aggregate']['weighted_confidence']*100)}%, "
              f"{agg['aggregate']['agreement_level']})")

    with open(out_dir / "all_aggregate.json", "w", encoding="utf-8") as f:
        json.dump({
            "post_meta": data.get("post_meta", {}),
            "evaluated_at": datetime.now(KST).isoformat(),
            "n_theses": len(theses),
            "analysts": analysts,
            "provider": args.provider,
            "multi_model": args.multi_model,
            "aggregates": all_aggregates,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n[thesis-eval] 완료: {len(theses)}개 thesis × {len(analysts)}명 analyst = "
          f"{len(theses) * len(analysts)}개 평가")
    print(f"  저장: {out_dir}/")


if __name__ == "__main__":
    main()
