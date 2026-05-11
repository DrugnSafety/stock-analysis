#!/usr/bin/env python3
"""Persona Panel 결과를 종합 — verdict 분포 / style-split / universal concerns / unique alpha."""
import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


PERSONA_CATEGORY = {
    "warren-buffett": "value",
    "charlie-munger": "value",
    "ben-graham": "value",
    "mohnish-pabrai": "value",
    "michael-burry": "value-contrarian",
    "peter-lynch": "growth",
    "cathie-wood": "growth",
    "phil-fisher": "growth",
    "stanley-druckenmiller": "macro",
    "bill-ackman": "activist",
    "nassim-taleb": "risk",
    "aswath-damodaran": "valuation",
    "rakesh-jhunjhunwala": "growth-em",
}


PERSONA_NAMES = {
    "warren-buffett": ("워런 버핏", "Warren Buffett"),
    "charlie-munger": ("찰리 멍거", "Charlie Munger"),
    "peter-lynch": ("피터 린치", "Peter Lynch"),
    "cathie-wood": ("캐시 우드", "Cathie Wood"),
    "michael-burry": ("마이클 버리", "Michael Burry"),
    "nassim-taleb": ("나심 탈레브", "Nassim Taleb"),
    "ben-graham": ("벤저민 그레이엄", "Ben Graham"),
    "bill-ackman": ("빌 애크먼", "Bill Ackman"),
    "mohnish-pabrai": ("모니시 파브라이", "Mohnish Pabrai"),
    "phil-fisher": ("필 피셔", "Phil Fisher"),
    "rakesh-jhunjhunwala": ("라케시 준준왈라", "Rakesh Jhunjhunwala"),
    "stanley-druckenmiller": ("스탠리 드러켄밀러", "Stanley Druckenmiller"),
    "aswath-damodaran": ("애스워드 다모다란", "Aswath Damodaran"),
}


def main():
    parser = argparse.ArgumentParser(description="패널 결과 종합")
    parser.add_argument("panel_dir")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    panel_dir = Path(args.panel_dir)
    persona_results = {}
    for path in panel_dir.glob("*.json"):
        if path.name in ("panel_summary.json", "aggregate.json"):
            continue
        try:
            d = json.load(open(path, encoding="utf-8"))
            persona_id = d.get("_meta", {}).get("persona_id", path.stem)
            persona_results[persona_id] = d
        except Exception:
            pass

    if not persona_results:
        print("결과가 없습니다.")
        return

    ticker = next(iter(persona_results.values())).get("ticker", "?")

    # Verdict 분포
    verdicts = [d.get("verdict", "neutral") for d in persona_results.values()]
    counter = Counter(verdicts)
    n = len(verdicts)
    distribution = {v: {"count": c, "pct": round(c / n * 100, 1)} for v, c in counter.items()}

    # Confidence 평균
    avg_conf = sum(d.get("confidence", 0) for d in persona_results.values()) / max(n, 1)

    # Style split
    style_groups = defaultdict(list)
    for pid, d in persona_results.items():
        cat = PERSONA_CATEGORY.get(pid, "other")
        style_groups[cat].append({"persona_id": pid,
                                  "verdict": d.get("verdict"),
                                  "confidence": d.get("confidence", 0)})

    style_summary = {}
    for cat, members in style_groups.items():
        cat_verdicts = Counter(m["verdict"] for m in members)
        style_summary[cat] = {
            "n_members": len(members),
            "members": members,
            "dominant": cat_verdicts.most_common(1)[0][0] if cat_verdicts else None,
        }

    # Universal concerns
    all_concerns = []
    for pid, d in persona_results.items():
        for c in (d.get("key_concerns", []) or []):
            all_concerns.append({"persona_id": pid, "concern": c})

    # Concern 단순 빈도 — 정확한 클러스터링은 NLP 필요. 여기선 핵심어 매칭.
    concern_themes = defaultdict(list)
    KEYWORDS = ["변동성", "valuation", "고평가", "CAPEX", "부채",
                "사이클", "환율", "정유", "단기", "차익실현",
                "리스크", "경쟁", "규제", "환경"]
    for c in all_concerns:
        text = c["concern"]
        for kw in KEYWORDS:
            if kw in text:
                concern_themes[kw].append(c)

    universal_concerns = []
    for theme, items in sorted(concern_themes.items(), key=lambda x: -len(x[1])):
        if len(items) >= max(3, n // 3):
            universal_concerns.append({
                "theme": theme,
                "frequency": len(items),
                "personas": list(set(it["persona_id"] for it in items)),
                "examples": [it["concern"] for it in items[:3]],
            })

    # Unique alpha (1-2 persona 단독)
    persona_unique = {}
    for pid, d in persona_results.items():
        for c in (d.get("key_opportunities", []) or []):
            # 단순 — 다른 페르소나의 opportunity와 키워드 겹침 적으면 unique
            persona_unique.setdefault(pid, []).append(c)

    # 결과
    aggregate = {
        "ticker": ticker,
        "aggregated_at": datetime.now(KST).isoformat(),
        "n_personas": n,
        "verdict_distribution": distribution,
        "average_confidence": round(avg_conf, 3),
        "style_split": style_summary,
        "universal_concerns": universal_concerns,
        "persona_results": {
            pid: {
                "verdict": d.get("verdict"),
                "confidence": d.get("confidence"),
                "horizon": d.get("horizon"),
                "key_concerns_top3": (d.get("key_concerns", []) or [])[:3],
                "key_opportunities_top3": (d.get("key_opportunities", []) or [])[:3],
                "uncertainty": d.get("uncertainty_acknowledged", ""),
                "persona_kr": PERSONA_NAMES.get(pid, ("?", "?"))[0],
                "persona_en": PERSONA_NAMES.get(pid, ("?", "?"))[1],
            }
            for pid, d in persona_results.items()
        },
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(aggregate, f, ensure_ascii=False, indent=2)

    print(f"\n=== {ticker} Persona Panel 종합 ===")
    print(f"  참여 페르소나: {n}")
    print(f"  Verdict 분포:")
    for v, info in distribution.items():
        print(f"    {v}: {info['count']} ({info['pct']}%)")
    print(f"  평균 confidence: {avg_conf:.2f}")
    print(f"  Universal concerns: {len(universal_concerns)}개 테마")
    for uc in universal_concerns[:5]:
        print(f"    [{uc['theme']}] {len(uc['personas'])}명 — {uc['examples'][0][:60]}")
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
