#!/usr/bin/env python3
"""3종 보고서 통합 빌더 — 한 명령으로 R1·R2·R3 동시 생성."""
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent

R1 = PLUGIN_ROOT / "skills" / "quant-anchor-report" / "scripts" / "build_r1.py"
R2 = PLUGIN_ROOT / "skills" / "persona-panel-report" / "scripts" / "build_r2.py"
R3 = PLUGIN_ROOT / "skills" / "executive-summary" / "scripts" / "build_r3.py"


def main():
    parser = argparse.ArgumentParser(description="R1+R2+R3 통합 빌더")
    parser.add_argument("--meta", required=True, help="공통 meta JSON (title/date/blog_url 등)")
    parser.add_argument("--stocks", required=True, help="market_data 리스트 JSON")
    parser.add_argument("--thesis", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--persona-panel-dir", help="ticker별 panel dir")
    parser.add_argument("--persona-aggregates", help="ticker → aggregate.json dict")
    parser.add_argument("--risk-limits", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[unified] 3종 보고서 빌드 시작")

    # R1 — Quant Anchor
    print(f"\n[unified] R1. Quant Anchor Report 생성...")
    cmd_r1 = [sys.executable, str(R1),
              "--meta", args.meta,
              "--stocks", args.stocks,
              "--thesis", args.thesis,
              "--eval-dir", args.eval_dir,
              "--risk-limits", args.risk_limits,
              "--output", str(out_dir / "R1_quant.pdf")]
    subprocess.run(cmd_r1, check=False)

    # R2 — Persona Panel (per ticker)
    print(f"\n[unified] R2. Persona Panel Report 생성 (per ticker)...")
    if args.persona_panel_dir:
        panel_dir = Path(args.persona_panel_dir)
        for ticker_dir in panel_dir.iterdir():
            if not ticker_dir.is_dir():
                continue
            agg_path = ticker_dir / "aggregate.json"
            if not agg_path.exists():
                continue
            ticker = ticker_dir.name
            r2_meta = json.dumps({"ticker": ticker, "date": "", "subjects": ticker})
            r2_meta_path = out_dir / f"meta_{ticker}.json"
            r2_meta_path.write_text(r2_meta)
            cmd_r2 = [sys.executable, str(R2),
                      "--aggregate", str(agg_path),
                      "--full-results", str(ticker_dir),
                      "--thesis", args.thesis,
                      "--meta", str(r2_meta_path),
                      "--output", str(out_dir / f"R2_persona_{ticker}.pdf")]
            subprocess.run(cmd_r2, check=False)

    # R3 — Executive Summary
    print(f"\n[unified] R3. Executive Summary 생성...")
    cmd_r3 = [sys.executable, str(R3),
              "--thesis", args.thesis,
              "--eval-dir", args.eval_dir,
              "--decisions", args.decisions,
              "--portfolio", args.portfolio,
              "--output", str(out_dir / "R3_executive.pdf")]
    if args.persona_aggregates:
        cmd_r3 += ["--persona-aggregates", args.persona_aggregates]
    subprocess.run(cmd_r3, check=False)

    print(f"\n[unified] 완료 — {out_dir}")
    for f in sorted(out_dir.glob("*.pdf")):
        import os
        print(f"  {f.name} ({os.path.getsize(f):,} bytes)")


if __name__ == "__main__":
    main()
