#!/usr/bin/env python3
"""Arena 결과 → consensus JSON 빌더 (LLM 미사용)."""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


def load_worker(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        d = json.load(open(path, encoding="utf-8"))
        if d.get("_pending"):
            return None
        return d
    except Exception:
        return None


def build_extract_consensus(arena_dir: Path) -> dict:
    workers = {}
    for name in ["claude", "openai", "gemini"]:
        d = load_worker(arena_dir / f"{name}.json")
        if d is not None:
            workers[name] = d

    # ticker별로 어느 worker가 발견했는지 매핑
    ticker_finders: dict[str, list[str]] = defaultdict(list)
    company_data: dict[str, dict] = {}

    for w_name, w_data in workers.items():
        for c in w_data.get("companies", []):
            t = c.get("ticker") or f"_NULL_{c.get('name_kr', c.get('name_en', '?'))}"
            ticker_finders[t].append(w_name)
            # 첫 발견자의 데이터 보존, 다른 worker도 발견 시 명시 추가
            if t not in company_data:
                company_data[t] = {
                    "ticker": c.get("ticker"),
                    "name_kr": c.get("name_kr"),
                    "name_en": c.get("name_en"),
                    "exchange": c.get("exchange"),
                    "country": c.get("country"),
                    "sector": c.get("sector"),
                    "industry": c.get("industry"),
                    "in_hashtag": c.get("in_hashtag", False),
                    "mentioned_explicitly": c.get("mentioned_explicitly", False),
                    "rationales": {w_name: c.get("rationale", "")},
                }
            else:
                company_data[t]["rationales"][w_name] = c.get("rationale", "")

    # 합집합 + 분류
    n_models = len(workers)
    union, consensus_all, majority, single = [], [], [], []
    for t, finders in ticker_finders.items():
        item = {**company_data[t], "found_by": finders, "consensus_score": len(finders) / max(n_models, 1)}
        union.append(item)
        if len(finders) == n_models:
            consensus_all.append(item)
        elif len(finders) >= 2:
            majority.append(item)
        else:
            single.append(item)

    # ETF / 산업도 동일 방식으로
    etfs_finders: dict[str, list[str]] = defaultdict(list)
    etf_data: dict[str, dict] = {}
    for w_name, w_data in workers.items():
        for e in w_data.get("etfs", []):
            t = e.get("ticker") or f"_NULL_{e.get('name', '?')}"
            etfs_finders[t].append(w_name)
            if t not in etf_data:
                etf_data[t] = {**e, "rationales": {w_name: e.get("rationale", "")}}
            else:
                etf_data[t]["rationales"][w_name] = e.get("rationale", "")

    etf_union = [{**etf_data[t], "found_by": f, "consensus_score": len(f) / max(n_models, 1)}
                 for t, f in etfs_finders.items()]

    industries_finders: dict[str, list[str]] = defaultdict(list)
    industry_data: dict[str, dict] = {}
    for w_name, w_data in workers.items():
        for ind in w_data.get("industries", []):
            key = ind.get("name") or ind.get("name_en") or "?"
            industries_finders[key].append(w_name)
            if key not in industry_data:
                industry_data[key] = {**ind, "outlooks": {w_name: ind.get("outlook")}}
            else:
                industry_data[key]["outlooks"][w_name] = ind.get("outlook")

    ind_union = [{**industry_data[k], "found_by": f, "consensus_score": len(f) / max(n_models, 1)}
                 for k, f in industries_finders.items()]

    # 비용 집계
    cost_summary = {"total_usd": 0.0}
    for w_name, w_data in workers.items():
        cost = w_data.get("extraction_meta", {}).get("estimated_cost_usd", 0)
        cost_summary[f"{w_name}_usd"] = cost
        cost_summary["total_usd"] += cost
    cost_summary["total_usd"] = round(cost_summary["total_usd"], 4)

    blog_url = next((w.get("post_meta", {}).get("url") for w in workers.values()
                     if w.get("post_meta")), "")

    union.sort(key=lambda x: -x["consensus_score"])
    consensus_all.sort(key=lambda x: x.get("ticker") or "")

    return {
        "type": "extract",
        "built_at": datetime.now(KST).isoformat(),
        "blog_url": blog_url,
        "models_run": list(workers.keys()),
        "extraction_consensus": {
            "all_companies_union": union,
            "consensus_3of3": consensus_all,
            "majority_2of3": majority,
            "single_model": single,
            "summary": {
                "n_models_run": n_models,
                "total_unique": len(union),
                "consensus_count": len(consensus_all),
                "majority_count": len(majority),
                "single_count": len(single),
            },
        },
        "industries_consensus": ind_union,
        "etfs_consensus": etf_union,
        "cost_summary": cost_summary,
    }


def build_analyze_consensus(arena_dir: Path) -> dict:
    workers = {}
    for name in ["claude", "openai", "gemini"]:
        d = load_worker(arena_dir / f"{name}.json")
        if d is not None:
            workers[name] = d

    if not workers:
        return {"error": "No worker results found", "models_run": []}

    # ticker는 모든 worker가 동일해야 함
    ticker = next(iter(workers.values())).get("ticker")

    verdicts = {}
    perspectives_score = defaultdict(dict)
    bull_theses, bear_theses = [], []
    for w_name, w_data in workers.items():
        v = w_data.get("verdict")
        c = w_data.get("confidence", 0)
        verdicts[w_name] = {
            "verdict": v,
            "confidence": c,
            "horizon": w_data.get("horizon"),
            "model_used": w_data.get("_meta", {}).get("model_used", w_name),
        }
        ap = w_data.get("agent_perspectives", {})
        for role in ["fundamentals", "technical", "news", "sentiment"]:
            perspectives_score[role][w_name] = (ap.get(role, {}) or {}).get("score")
        if ap.get("bull_thesis"):
            bull_theses.append((w_name, ap["bull_thesis"]))
        if ap.get("bear_thesis"):
            bear_theses.append((w_name, ap["bear_thesis"]))

    # Verdict counter
    verdict_counter = Counter(v["verdict"] for v in verdicts.values())
    most_common = verdict_counter.most_common(1)[0]
    weighted_verdict = most_common[0]
    agreement_count = most_common[1]

    if agreement_count == len(verdicts):
        agreement_level = "high (전원 합의)"
    elif agreement_count >= 2:
        agreement_level = "medium (다수)"
    else:
        agreement_level = "low (분열)"

    # Confidence 가중평균
    matching = [v["confidence"] for v in verdicts.values() if v["verdict"] == weighted_verdict]
    weighted_confidence = round(sum(matching) / max(len(matching), 1), 3) if matching else 0

    # Perspectives spread
    perspectives_diff = {}
    for role, scores in perspectives_score.items():
        vals = [s for s in scores.values() if isinstance(s, (int, float))]
        spread = (max(vals) - min(vals)) if vals else 0
        perspectives_diff[role] = {
            **{k: v for k, v in scores.items()},
            "spread": spread,
        }

    cost_summary = {"total_usd": 0.0}
    for w_name, w_data in workers.items():
        cost = w_data.get("_meta", {}).get("estimated_cost_usd", 0)
        cost_summary[f"{w_name}_usd"] = cost
        cost_summary["total_usd"] += cost
    cost_summary["total_usd"] = round(cost_summary["total_usd"], 4)

    return {
        "type": "analyze",
        "built_at": datetime.now(KST).isoformat(),
        "ticker": ticker,
        "models_run": list(workers.keys()),
        "verdicts": verdicts,
        "weighted_verdict": weighted_verdict,
        "weighted_confidence": weighted_confidence,
        "agreement_level": agreement_level,
        "agreement_breakdown": dict(verdict_counter),
        "perspectives_diff": perspectives_diff,
        "bull_theses_by_model": bull_theses,
        "bear_theses_by_model": bear_theses,
        "cost_summary": cost_summary,
    }


def main():
    parser = argparse.ArgumentParser(description="Build consensus from arena directory")
    parser.add_argument("arena_dir")
    parser.add_argument("--type", choices=["extract", "analyze"], required=True)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    arena_dir = Path(args.arena_dir)
    if args.type == "extract":
        result = build_extract_consensus(arena_dir)
    else:
        result = build_analyze_consensus(arena_dir)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[consensus] {args.type} 결과 저장: {args.output}")
    if args.type == "extract":
        s = result["extraction_consensus"]["summary"]
        print(f"  총 {s['total_unique']}개 ticker (consensus={s['consensus_count']}, "
              f"majority={s['majority_count']}, single={s['single_count']})")
    else:
        print(f"  ticker: {result['ticker']}")
        print(f"  agreement: {result['agreement_level']}")
        print(f"  weighted verdict: {result['weighted_verdict']} (conf {result['weighted_confidence']})")


if __name__ == "__main__":
    main()
