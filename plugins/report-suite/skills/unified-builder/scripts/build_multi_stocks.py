#!/usr/bin/env python3
"""Generate combined PDF reports for top N tickers from a single blog analysis.

Pipeline:
  1. Read full pipeline output (theses, evals, all stocks, all persona aggregates,
     decisions, portfolio).
  2. Pick top N tickers by signal_score (or specified list).
  3. For each ticker, generate ONE combined PDF (R1+R2+R3+Deep Research).
  4. Output naming: {idx}_{ticker_safe}_{company_kr}_combined.pdf

Usage:
  python build_multi_stocks.py \\
      --pipeline-dir .analysis-log/bloggers/doctordk/2026-04-29_lithium \\
      --output-dir .analysis-log/bloggers/doctordk/2026-04-29_lithium/reports \\
      --top-n 5
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent

sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))
from ticker_resolver import resolve_ticker  # type: ignore


def _safe_filename(name: str) -> str:
    """Convert a ticker/company name into a safe filename."""
    bad = '/\\:*?"<>|'
    out = name
    for c in bad:
        out = out.replace(c, "_")
    out = out.replace(" ", "_")
    return out[:80]


def select_top_tickers(decisions: list[dict], persona_aggregates: dict,
                        explicit: list[str] | None, top_n: int) -> list[str]:
    """Choose the top N tickers to generate combined reports for.

    Priority:
      1. Explicit list if provided.
      2. By |signal_score| from decisions (top conviction longs/shorts).
      3. By bull_count - bear_count from persona_aggregates.
    """
    if explicit:
        return explicit[:top_n]

    scored: list[tuple[str, float]] = []
    for d in decisions:
        t = d.get("ticker")
        if not t:
            continue
        score = abs(d.get("signal_score") or 0)
        scored.append((t, score))

    if not scored and persona_aggregates:
        for t, agg in persona_aggregates.items():
            d = agg.get("verdict_distribution", {})
            bull = d.get("lean_bullish", {}).get("count", 0)
            bear = d.get("lean_bearish", {}).get("count", 0)
            scored.append((t, abs(bull - bear)))

    scored.sort(key=lambda x: -x[1])
    return [t for t, _ in scored[:top_n]]


def build_combined_for_ticker(ticker: str, pipeline_dir: Path, output_path: Path,
                                meta_path: Path, deep_path: Path | None) -> bool:
    """Run build_combined.py for one ticker."""
    builder = SCRIPT_DIR / "build_combined.py"

    # Resolve files in pipeline_dir using common conventions
    persona_agg = pipeline_dir / "persona_panel" / ticker / "aggregate.json"
    persona_full = pipeline_dir / "persona_panel" / ticker
    persona_all = pipeline_dir / "persona_panel" / "_all_aggregates.json"

    if not persona_agg.exists():
        # Try fallback location
        for candidate in (pipeline_dir.glob("persona_panel*/" + ticker + "/aggregate.json")):
            persona_agg = candidate
            persona_full = candidate.parent
            break

    cmd = [
        sys.executable, str(builder),
        "--ticker", ticker,
        "--meta", str(meta_path),
        "--stocks", str(pipeline_dir / "stocks.json"),
        "--thesis", str(pipeline_dir / "thesis_list.json"),
        "--eval-dir", str(pipeline_dir / "thesis_eval"),
        "--risk-limits", str(pipeline_dir / "risk_limits.json"),
        "--decisions", str(pipeline_dir / "decisions.json"),
        "--portfolio", str(pipeline_dir / "portfolio.json"),
        "--output", str(output_path),
    ]
    if persona_agg.exists():
        cmd += ["--persona-aggregate", str(persona_agg)]
    if persona_full.exists() and persona_full.is_dir():
        cmd += ["--persona-full", str(persona_full)]
    if persona_all.exists():
        cmd += ["--persona-aggregates-all", str(persona_all)]
    if deep_path and deep_path.exists():
        cmd += ["--deep-research", str(deep_path)]

    print(f"  → building {output_path.name}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    [error] {result.stderr[:300]}")
        return False
    print(f"    {result.stdout.strip().splitlines()[-1] if result.stdout else ''}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Multi-stock combined report builder")
    parser.add_argument("--pipeline-dir", required=True, help="Dir with stocks.json/thesis_list.json/etc")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--top-n", type=int, default=5)
    parser.add_argument("--tickers", nargs="*", help="Explicit ticker list (overrides top-n)")
    parser.add_argument("--meta", help="meta.json — if not in pipeline-dir")
    args = parser.parse_args()

    pipeline_dir = Path(args.pipeline_dir).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load decisions / persona aggregates
    decisions_path = pipeline_dir / "decisions.json"
    decisions = []
    if decisions_path.exists():
        decisions = (json.loads(decisions_path.read_text()) or {}).get("decisions", [])

    persona_aggs_path = pipeline_dir / "persona_panel" / "_all_aggregates.json"
    persona_aggs = {}
    if persona_aggs_path.exists():
        persona_aggs = json.loads(persona_aggs_path.read_text())

    tickers = select_top_tickers(decisions, persona_aggs, args.tickers, args.top_n)
    if not tickers:
        print("[error] no tickers selected — check decisions.json or persona aggregates")
        sys.exit(1)

    meta_path = Path(args.meta) if args.meta else (pipeline_dir / "meta.json")
    if not meta_path.exists():
        # Synthesize a minimal meta
        meta_path = pipeline_dir / "_meta_auto.json"
        meta_path.write_text(json.dumps({
            "title": pipeline_dir.name,
            "date": "",
            "blog_url": "",
        }, ensure_ascii=False))

    deep_path = pipeline_dir / "deep_research.json"

    print(f"[multi-stock] generating combined PDFs for {len(tickers)} tickers")
    print(f"[multi-stock] target tickers: {', '.join(tickers)}")

    success = 0
    for idx, ticker in enumerate(tickers, 1):
        info = resolve_ticker(ticker)
        company_kr = info.get("kr", ticker)
        output_path = output_dir / f"{idx}_{_safe_filename(ticker)}_{_safe_filename(company_kr)}_combined.pdf"
        ticker_deep_path = pipeline_dir / "deep_research" / f"{ticker}.json"
        if not ticker_deep_path.exists():
            ticker_deep_path = deep_path
        if build_combined_for_ticker(ticker, pipeline_dir, output_path, meta_path, ticker_deep_path):
            success += 1

    print(f"\n[multi-stock] done: {success}/{len(tickers)} succeeded")
    for f in sorted(output_dir.glob("*_combined.pdf")):
        import os
        print(f"  {f.name} ({os.path.getsize(f):,} bytes)")


if __name__ == "__main__":
    main()
