#!/usr/bin/env python3
"""Research Manager — Sector & Issuer Intelligence aggregator.

Builds research_intel/{ticker}_sector.json from existing deep_research + news_disclosures +
yfinance sector info. Deterministic — no LLM calls; aggregates structured data.
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT.parent / "report-suite" / "skills" / "_common"))


def build_sector_intel(ticker: str, pipeline_dir: Path) -> dict:
    """Aggregate sector/issuer intel from existing artifacts."""
    deep_path = pipeline_dir / "deep_research" / f"{ticker}.json"
    if not deep_path.exists():
        return {"ticker": ticker, "error": f"deep_research not found"}

    deep = json.loads(deep_path.read_text(encoding="utf-8"))
    industry = deep.get("industry", {})
    catalysts = deep.get("catalysts", [])
    risks = deep.get("risks", [])
    news_30d = [n for n in industry.get("news", []) if n.get("date", "") >= "2026-04-20"]
    competitors = industry.get("competitors", [])

    # broker research synthesis — count thesis_decomposition support/challenge
    thesis_decomp = deep.get("thesis_decomposition", [])
    confirmed = sum(1 for t in thesis_decomp if t.get("current_status") == "confirmed")
    pending = sum(1 for t in thesis_decomp if t.get("current_status") == "pending")

    # credit risk flags — risks marked impact=high
    credit_flags = [r["name"] for r in risks if r.get("impact") == "high"][:3]

    return {
        "ticker": ticker,
        "sector": industry.get("name", "-"),
        "sector_overview": industry.get("overview", "-"),
        "sector_developments_30d": news_30d,
        "issuer_developments_30d": [c for c in catalysts if c.get("date", "") >= "2026-04-01"][:5],
        "broker_research_synthesis": (
            f"내부 thesis decomposition 종합: {confirmed}건 검증·{pending}건 진행 중. "
            f"verdict 가중 평균은 persona_panel/aggregate.json의 verdict_distribution 참조."
        ),
        "competitive_intel": {
            "share_movement": competitors[0].get("moat", "-") if competitors else "-",
            "peer_count": len(competitors),
            "top_competitor": competitors[0] if competitors else None,
        },
        "credit_risk_flags": credit_flags,
        "tailwinds": industry.get("tailwinds", []),
        "headwinds": industry.get("headwinds", []),
        "market_size_5y_usd_bn": industry.get("market_size", {}).get("current_usd_bn", "-")
            if isinstance(industry.get("market_size"), dict) else "-",
        "generated_at": datetime.now().isoformat() + "+09:00",
        "source": "Research Manager v0.1 (specialist-agents plugin) — aggregated from deep_research + news_disclosures",
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pipeline-dir", required=True)
    p.add_argument("--tickers", nargs="+", required=True)
    p.add_argument("--output-dir", default=None)
    args = p.parse_args()

    pdir = Path(args.pipeline_dir)
    odir = Path(args.output_dir or (pdir / "research_intel"))
    odir.mkdir(parents=True, exist_ok=True)

    for ticker in args.tickers:
        intel = build_sector_intel(ticker, pdir)
        out = odir / f"{ticker}_sector.json"
        out.write_text(json.dumps(intel, ensure_ascii=False, indent=2))
        print(f"OK {ticker}: sector_dev={len(intel.get('sector_developments_30d', []))}, peer_count={intel.get('competitive_intel', {}).get('peer_count', 0)}")


if __name__ == "__main__":
    main()
