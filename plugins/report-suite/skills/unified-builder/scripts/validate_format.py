#!/usr/bin/env python3
"""Format validator — analysis 디렉토리가 canonical format을 따르는지 검증.

Usage:
  python validate_format.py .analysis-log/bloggers/{blogger}/{date}_{slug}

Exit code:
  0 — all required files present, valid schema
  1 — missing required files or invalid schema
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    "meta.json",
    "thesis_list.json",
    "thesis_eval/all_aggregate.json",
    "stocks.json",
    "persona_panel/_all_aggregates.json",
    "risk_limits.json",
    "decisions.json",
    "portfolio.json",
]

REQUIRED_PERSONAS = [
    "warren-buffett", "charlie-munger", "peter-lynch", "cathie-wood",
    "michael-burry", "nassim-taleb", "ben-graham", "bill-ackman",
    "mohnish-pabrai", "phil-fisher", "rakesh-jhunjhunwala",
    "stanley-druckenmiller", "aswath-damodaran",
]


def check(condition: bool, message: str) -> bool:
    """Assert + log."""
    if condition:
        print(f"  ✓ {message}")
    else:
        print(f"  ✗ {message}")
    return condition


def validate(pipeline_dir: Path) -> tuple[int, int]:
    """Returns (passed, total) check counts."""
    passed = 0
    total = 0

    print(f"\n=== Validating {pipeline_dir.name} ===")

    # 1. Required files
    print("\n[1/5] Required top-level files")
    for fname in REQUIRED_FILES:
        total += 1
        if check((pipeline_dir / fname).exists(), f"{fname}"):
            passed += 1

    # 2. Theses ≥ 5
    print("\n[2/5] Thesis list")
    theses_path = pipeline_dir / "thesis_list.json"
    if theses_path.exists():
        try:
            data = json.loads(theses_path.read_text())
            theses = data.get("theses", [])
            total += 1
            if check(len(theses) >= 5, f"thesis count ≥ 5 (got {len(theses)})"):
                passed += 1
            total += 1
            core_theses = [t for t in theses if t.get("importance") == "core"]
            if check(len(core_theses) >= 3, f"core theses ≥ 3 (got {len(core_theses)})"):
                passed += 1
        except json.JSONDecodeError:
            print(f"  ✗ thesis_list.json malformed JSON")
            total += 1

    # 3. Stocks ≥ 3
    print("\n[3/5] Stocks list")
    stocks_path = pipeline_dir / "stocks.json"
    tickers: list[str] = []
    if stocks_path.exists():
        try:
            stocks = json.loads(stocks_path.read_text())
            tickers = [s.get("ticker") for s in stocks if s.get("ticker")]
            total += 1
            if check(len(tickers) >= 3, f"stock count ≥ 3 (got {len(tickers)})"):
                passed += 1
            total += 1
            has_market_data = all("market_data" in s for s in stocks)
            if check(has_market_data, "all stocks have market_data field"):
                passed += 1
            # NEW: validate live yfinance fetch (not LLM placeholder)
            total += 1
            live_fetch_count = sum(
                1 for s in stocks
                if "yfinance" in (s.get("market_data", {}).get("fetched_via", "") or "").lower()
                and "(live)" in (s.get("market_data", {}).get("fetched_via", "") or "").lower()
            )
            if check(live_fetch_count >= len(tickers) * 0.6,
                      f"market_data is live yfinance ({live_fetch_count}/{len(tickers)} stocks)"):
                passed += 1
        except json.JSONDecodeError:
            print(f"  ✗ stocks.json malformed JSON")
            total += 1

    # 4. Persona panels for each ticker
    print("\n[4/5] Persona panels (13명 per ticker)")
    panel_dir = pipeline_dir / "persona_panel"
    for ticker in tickers[:5]:  # check top 5
        ticker_dir = panel_dir / ticker
        total += 1
        agg_exists = (ticker_dir / "aggregate.json").exists()
        if check(agg_exists, f"{ticker}/aggregate.json"):
            passed += 1
        if agg_exists:
            try:
                agg = json.loads((ticker_dir / "aggregate.json").read_text())
                persona_results = agg.get("persona_results", {})
                missing = [p for p in REQUIRED_PERSONAS if p not in persona_results]
                total += 1
                if check(not missing, f"{ticker}: 13명 페르소나 모두 존재"):
                    passed += 1
                else:
                    print(f"      missing: {missing}")
            except json.JSONDecodeError:
                print(f"  ✗ {ticker}/aggregate.json malformed")

    # 5. Combined PDF reports
    print("\n[5/5] Combined PDF reports (Layer 1)")
    combined_dir = pipeline_dir / "reports" / "combined"
    total += 1
    if check(combined_dir.exists(), "reports/combined/ exists"):
        passed += 1
    if combined_dir.exists():
        pdfs = list(combined_dir.glob("*_combined.pdf"))
        total += 1
        if check(len(pdfs) >= 3, f"≥ 3 combined PDFs (got {len(pdfs)})"):
            passed += 1
        # Naming convention: {idx}_{ticker}_{name}_combined.pdf
        total += 1
        proper_naming = all(p.name[0].isdigit() and "_combined.pdf" in p.name for p in pdfs)
        if check(proper_naming, "PDF naming follows {idx}_{ticker}_{name}_combined.pdf"):
            passed += 1

    # Optional: Layer 2 overview
    print("\n[bonus] Layer 2 multi-format overview")
    overview_dir = pipeline_dir / "reports" / "overview"
    if overview_dir.exists():
        for fmt in ("md", "pdf", "pptx"):
            f = overview_dir / f"overview.{fmt}"
            total += 1
            if check(f.exists(), f"overview.{fmt}"):
                passed += 1
    else:
        print("  ⚠ overview/ 디렉토리 없음 (권장 — build_overview.py 실행)")

    return passed, total


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("pipeline_dir")
    args = parser.parse_args()

    pipeline_dir = Path(args.pipeline_dir)
    if not pipeline_dir.exists():
        print(f"Error: {pipeline_dir} does not exist")
        sys.exit(1)

    passed, total = validate(pipeline_dir)

    pct = (passed / total * 100) if total else 0
    print(f"\n=== Summary: {passed}/{total} checks passed ({pct:.0f}%) ===")

    if passed == total:
        print("✓ Format VALIDATED — canonical format 일치")
        sys.exit(0)
    else:
        print(f"✗ {total - passed} check(s) FAILED — canonical format 미준수")
        print("  → REPORT_FORMAT_STANDARD.md 참조해서 누락 항목 보완")
        sys.exit(1)


if __name__ == "__main__":
    main()
