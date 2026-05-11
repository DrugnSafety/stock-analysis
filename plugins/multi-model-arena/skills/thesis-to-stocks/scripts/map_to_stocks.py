#!/usr/bin/env python3
"""Thesis → Stocks 매핑 + 점수 계산."""
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
from extract_theses import call_openai, parse_json

KST = timezone(timedelta(hours=9))


MAGNITUDE = {"++": 1.0, "+": 0.5, "0": 0.0, "-": -0.5, "--": -1.0}
STANCE_WEIGHT = {"support": 1.0, "neutral": 0.0, "rebut": -1.0}
IMPORTANCE_WEIGHT = {"core": 1.0, "supporting": 0.5, "aside": 0.0}


MAPPING_SYSTEM = """You are an analyst mapping investment claims (theses) to stocks.

For each candidate stock, evaluate exposure to each thesis using these magnitudes:
  ++ : strong positive (direct beneficiary)
  +  : weak positive (indirect beneficiary)
  0  : irrelevant
  -  : weak negative
  -- : strong negative

Rules:
1. Be specific — a 1-line rationale per (stock, thesis) pair
2. Most pairs are 0 — only mark non-zero when there's a real economic linkage
3. Korean & global stocks both supported
4. If a thesis is about a REGION/POLICY (e.g., "Korea removed tariff"), only stocks operating in that region/sector get + or -
5. If a thesis is about a TECHNOLOGY/PRODUCT (e.g., "Panamax sized tankers needed"), only stocks making/operating that exact thing get +

Output ONLY valid JSON."""


MAPPING_USER_TEMPLATE = """Theses (with their evaluations):
{theses_block}

Candidate stocks:
{stocks_block}

Required JSON schema:
{{
  "stocks": [
    {{
      "ticker": "...",
      "exposures": {{
        "{example_claim_id}": {{"sign": "++|+|0|-|--", "rationale": "1-line"}},
        ...
      }}
    }}
  ]
}}

Output JSON only."""


def compute_score(thesis_aggregates: list[dict], stock_exposures: dict[str, dict]) -> tuple[float, list[str], list[str]]:
    """주어진 thesis 평가와 종목 노출도로 점수 계산."""
    score = 0.0
    drivers = []
    risks = []

    by_id = {a["claim_id"]: a for a in thesis_aggregates}

    for cid, exp in stock_exposures.items():
        if cid not in by_id:
            continue
        agg = by_id[cid]
        thesis = agg.get("claim", "")
        importance = agg.get("importance", "core")  # default core
        # Some pipelines store importance under thesis level
        sign = exp.get("sign", "0")
        magnitude = MAGNITUDE.get(sign, 0.0)
        if magnitude == 0:
            continue

        weighted_stance = agg["aggregate"].get("weighted_stance", "neutral")
        weighted_conf = agg["aggregate"].get("weighted_confidence", 0)
        stance_w = STANCE_WEIGHT.get(weighted_stance, 0)
        importance_w = IMPORTANCE_WEIGHT.get(importance, 1.0)

        contribution = magnitude * stance_w * weighted_conf * importance_w
        score += contribution

        if contribution > 0.3:
            drivers.append(f"{cid}: {sign} ({contribution:+.2f})")
        elif contribution < -0.3:
            risks.append(f"{cid}: {sign} ({contribution:+.2f})")

    return round(score, 3), drivers, risks


def call_mapping_llm(thesis_data: dict, eval_aggregates: list[dict], candidate_stocks: list[dict]) -> dict:
    """LLM에 thesis-stock 노출도 매핑 요청."""
    load_env()
    cfg = get_model_config()
    api_key = get_key("OPENAI_API_KEY", required=True)

    theses_block = "\n".join([
        f"- [{a['claim_id']}] ({a['aggregate']['weighted_stance']} "
        f"{int(a['aggregate']['weighted_confidence']*100)}%) "
        f"{a['claim']}"
        for a in eval_aggregates
    ])

    stocks_block = "\n".join([
        f"- {s.get('name_kr') or s.get('name_en', '?')} ({s.get('ticker', 'NULL')}) — "
        f"{s.get('industry', '?')}"
        for s in candidate_stocks
    ])

    example_claim_id = eval_aggregates[0]["claim_id"] if eval_aggregates else "T01"

    user = MAPPING_USER_TEMPLATE.format(
        theses_block=theses_block,
        stocks_block=stocks_block,
        example_claim_id=example_claim_id,
    )

    start = time.time()
    content, usage, used = call_openai(
        api_key, cfg["openai"]["model"], cfg["openai"]["fallback"],
        cfg["openai"]["reasoning_effort"], MAPPING_SYSTEM, user
    )
    elapsed = time.time() - start

    result = parse_json(content)
    return {**result, "_meta": {"model_used": used, "elapsed_seconds": round(elapsed, 2),
                                 "prompt_tokens": usage.get("prompt_tokens", 0),
                                 "completion_tokens": usage.get("completion_tokens", 0)}}


def main():
    parser = argparse.ArgumentParser(description="Thesis → stocks mapping")
    parser.add_argument("thesis_json")
    parser.add_argument("--eval-dir", required=True, help="thesis-evaluator 출력 디렉토리")
    parser.add_argument("--candidate-stocks", help="종목 후보 JSON (stocks.json 형식)")
    parser.add_argument("--exposures", help="이미 매핑된 exposures.json (LLM 호출 skip)")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    # 1. Thesis & 평가 결과 로드
    with open(args.thesis_json, encoding="utf-8") as f:
        thesis_data = json.load(f)

    eval_dir = Path(args.eval_dir)
    all_agg_path = eval_dir / "all_aggregate.json"
    if all_agg_path.exists():
        with open(all_agg_path, encoding="utf-8") as f:
            eval_data = json.load(f)
        aggregates = eval_data.get("aggregates", [])
    else:
        # 개별 *_aggregate.json 수집
        aggregates = []
        for p in sorted(eval_dir.glob("*_aggregate.json")):
            with open(p, encoding="utf-8") as f:
                aggregates.append(json.load(f))

    # importance 정보 보강
    by_cid = {t["claim_id"]: t for t in thesis_data.get("theses", [])}
    for agg in aggregates:
        cid = agg.get("claim_id")
        if cid in by_cid:
            agg["importance"] = by_cid[cid].get("importance", "core")

    # 2. 후보 종목 결정
    if args.candidate_stocks:
        with open(args.candidate_stocks, encoding="utf-8") as f:
            stocks_data = json.load(f)
        candidates = stocks_data.get("companies", [])
    else:
        print("⚠️  --candidate-stocks가 없어 매핑할 종목 후보가 없습니다.", file=sys.stderr)
        candidates = []

    # 3. Exposures 결정 (LLM 호출 또는 사전 입력)
    if args.exposures:
        with open(args.exposures, encoding="utf-8") as f:
            exposures_data = json.load(f)
    elif candidates:
        print(f"[map] LLM 호출: {len(aggregates)} thesis × {len(candidates)} stocks...")
        exposures_data = call_mapping_llm(thesis_data, aggregates, candidates)
    else:
        exposures_data = {"stocks": []}

    # 4. 점수 계산
    stocks_with_score = []
    for s in exposures_data.get("stocks", []):
        # 후보에서 메타 추가
        meta = next((c for c in candidates if c.get("ticker") == s.get("ticker")), {})
        score, drivers, risks = compute_score(aggregates, s.get("exposures", {}))
        stocks_with_score.append({
            "ticker": s.get("ticker"),
            "name_kr": meta.get("name_kr"),
            "name_en": meta.get("name_en"),
            "exposures": s.get("exposures", {}),
            "thesis_weighted_score": score,
            "primary_drivers": drivers,
            "primary_risks": risks,
        })

    stocks_with_score.sort(key=lambda x: -(x.get("thesis_weighted_score") or 0))

    result = {
        "post_meta": thesis_data.get("post_meta", {}),
        "built_at": datetime.now(KST).isoformat(),
        "scoring_method": "thesis_weighted_v1",
        "n_theses": len(aggregates),
        "n_stocks": len(stocks_with_score),
        "stocks": stocks_with_score,
        "ranking": [
            {"ticker": s["ticker"], "name_kr": s.get("name_kr"),
             "score": s["thesis_weighted_score"], "rank": i + 1}
            for i, s in enumerate(stocks_with_score)
        ],
    }

    if "_meta" in exposures_data:
        result["mapping_meta"] = exposures_data["_meta"]

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[map] 완료: {len(stocks_with_score)}개 종목, {len(aggregates)}개 thesis")
    print(f"\n=== Top 5 종목 (thesis-weighted score) ===")
    for s in stocks_with_score[:5]:
        print(f"  {s.get('name_kr') or s.get('name_en'):25s} | {s.get('ticker'):12s} | "
              f"score={s['thesis_weighted_score']:+.2f}  "
              f"drivers: {len(s['primary_drivers'])}, risks: {len(s['primary_risks'])}")
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
