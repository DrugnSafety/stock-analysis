#!/usr/bin/env python3
"""Sentiment Analyst — News & Social Mood Quantification.

Computes sentiment score (-1.0 ~ +1.0) from existing news_disclosures NEWS_TIMELINE
+ deep_research news + impact flags (+/0/-). Deterministic aggregation.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _impact_to_score(impact: str) -> float:
    """+/++/0/○/-/-- → score in -1.0 ~ +1.0."""
    return {
        "++": 1.0, "+": 0.6, "0": 0.0, "○": 0.0,
        "-": -0.6, "--": -1.0,
    }.get(impact.strip() if impact else "0", 0.0)


def compute_sentiment(ticker: str, pipeline_dir: Path) -> dict:
    deep_path = pipeline_dir / "deep_research" / f"{ticker}.json"
    if not deep_path.exists():
        return {"ticker": ticker, "error": "deep_research not found"}

    deep = json.loads(deep_path.read_text(encoding="utf-8"))
    news_all = deep.get("industry", {}).get("news", [])
    catalysts = deep.get("catalysts", [])

    # Combine news + catalysts as sentiment signals
    items_30d = []
    items_90d = []
    items_365d = []
    today = datetime.now().date()

    for item in news_all + catalysts:
        date_str = item.get("date", "")
        if not date_str:
            continue
        try:
            # Parse YYYY-MM-DD or YYYY-MM or YYYY-QN
            if "Q" in date_str:
                yr = int(date_str.split("-")[0])
                dt = datetime(yr, 6, 30).date()
            elif len(date_str) >= 10:
                dt = datetime.strptime(date_str[:10], "%Y-%m-%d").date()
            elif len(date_str) == 7:
                dt = datetime.strptime(date_str, "%Y-%m").date()
            else:
                continue
        except Exception:
            continue

        days_ago = (today - dt).days
        impact = item.get("impact") or item.get("expected_impact") or "0"
        score = _impact_to_score(impact)
        record = {"date": date_str, "headline": item.get("headline") or item.get("event", "-"), "score": score}
        if days_ago <= 365:
            items_365d.append(record)
        if days_ago <= 90:
            items_90d.append(record)
        if days_ago <= 30:
            items_30d.append(record)

    def _avg(items):
        return round(sum(i["score"] for i in items) / len(items), 3) if items else 0.0

    score_30d = _avg(items_30d)
    score_90d = _avg(items_90d)
    score_365d = _avg(items_365d)

    # Trend: 30d vs 90d
    trend = round(score_30d - score_90d, 3)

    positive_drivers = sorted(
        [i for i in items_30d if i["score"] > 0.5],
        key=lambda x: -x["score"]
    )[:3]
    negative_drivers = sorted(
        [i for i in items_30d if i["score"] < -0.3],
        key=lambda x: x["score"]
    )[:3]

    # Calibration check (simple heuristic — overheat warning if very high)
    overheat_warn = "high sentiment (>0.7) + crowded trade risk — contrarian alert" if score_30d > 0.7 else "no overheat signal"

    return {
        "ticker": ticker,
        "as_of": today.isoformat(),
        "news_sentiment_30d": score_30d,
        "news_sentiment_90d": score_90d,
        "news_sentiment_365d": score_365d,
        "combined_score": round((score_30d * 0.5 + score_90d * 0.3 + score_365d * 0.2), 3),
        "trend_30d_vs_90d": trend,
        "n_items_30d": len(items_30d),
        "n_items_90d": len(items_90d),
        "confidence": "high" if len(items_30d) >= 5 else "medium" if len(items_30d) >= 2 else "low",
        "key_drivers_positive": [{"date": p["date"], "headline": p["headline"]} for p in positive_drivers],
        "key_drivers_negative": [{"date": n["date"], "headline": n["headline"]} for n in negative_drivers],
        "calibration_check": overheat_warn,
        "generated_at": datetime.now().isoformat() + "+09:00",
        "source": "Sentiment Analyst v0.1 (specialist-agents plugin) — deterministic aggregation of news impact flags",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pipeline-dir", required=True)
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--output-dir", default=None)
    args = p.parse_args()

    pdir = Path(args.pipeline_dir)
    odir = Path(args.output_dir or (pdir / "sentiment"))
    odir.mkdir(parents=True, exist_ok=True)

    for ticker in args.tickers:
        result = compute_sentiment(ticker, pdir)
        out = odir / f"{ticker}_score.json"
        out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
        s30 = result.get("news_sentiment_30d", 0)
        n30 = result.get("n_items_30d", 0)
        print(f"OK {ticker}: 30d sentiment {s30:+.2f} (n={n30}) trend {result.get('trend_30d_vs_90d', 0):+.2f}")


if __name__ == "__main__":
    main()
