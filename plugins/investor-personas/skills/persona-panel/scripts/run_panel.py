#!/usr/bin/env python3
"""Persona Panel — 단일 종목 × N 페르소나 병렬 실행."""
import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
PERSONA_DIR = PLUGIN_ROOT / "personas"
EVALUATOR = PLUGIN_ROOT / "skills" / "persona-evaluator" / "scripts" / "evaluate.py"


ALL_PERSONAS = [
    "warren-buffett", "charlie-munger", "peter-lynch", "cathie-wood",
    "michael-burry", "nassim-taleb", "ben-graham", "bill-ackman",
    "mohnish-pabrai", "phil-fisher", "rakesh-jhunjhunwala",
    "stanley-druckenmiller", "aswath-damodaran",
]


def run_one(persona: str, args, out_dir: Path) -> dict:
    out_path = out_dir / f"{persona}.json"
    cmd = [sys.executable, str(EVALUATOR), args.ticker, persona,
           "--market", args.market, "--output", str(out_path),
           "--provider", args.provider]
    if args.post:
        cmd += ["--post", args.post]

    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=args.timeout)
        elapsed = time.time() - start
        if r.returncode == 0:
            return {"persona": persona, "status": "success", "elapsed": round(elapsed, 2)}
        return {"persona": persona, "status": "failed", "elapsed": round(elapsed, 2),
                "stderr": r.stderr[-1500:]}
    except subprocess.TimeoutExpired:
        return {"persona": persona, "status": "timeout", "elapsed": args.timeout}
    except Exception as e:
        return {"persona": persona, "status": "error", "error": str(e)[:500]}


def main():
    parser = argparse.ArgumentParser(description="단일 ticker × N 페르소나 패널")
    parser.add_argument("ticker")
    parser.add_argument("--market", required=True)
    parser.add_argument("--post")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include", help="콤마 구분 (기본: 13명 전부)")
    parser.add_argument("--provider", choices=["openai", "gemini"], default="openai")
    parser.add_argument("--max-workers", type=int, default=4,
                        help="병렬 호출 수 (rate limit 주의)")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    personas = ALL_PERSONAS if not args.include else [p.strip() for p in args.include.split(",")]
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[panel] {args.ticker} × {len(personas)} 페르소나 (max_workers={args.max_workers})")
    results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.max_workers) as pool:
        futures = {pool.submit(run_one, p, args, out_dir): p for p in personas}
        for fut in concurrent.futures.as_completed(futures):
            r = fut.result()
            results.append(r)
            status_icon = {"success": "✅", "failed": "❌", "timeout": "⏱️", "error": "💥"}.get(r["status"], "?")
            print(f"  {status_icon} {r['persona']}: {r['status']} ({r.get('elapsed', '?')}s)")

    # 비용 집계
    total_cost = 0.0
    for p in personas:
        path = out_dir / f"{p}.json"
        if path.exists():
            try:
                d = json.load(open(path, encoding="utf-8"))
                total_cost += d.get("_meta", {}).get("estimated_cost_usd", 0)
            except Exception:
                pass

    summary = {
        "ticker": args.ticker,
        "n_personas": len(personas),
        "results": results,
        "total_cost_usd": round(total_cost, 4),
    }
    with open(out_dir / "panel_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    success = sum(1 for r in results if r["status"] == "success")
    print(f"\n[panel] 완료: {success}/{len(personas)} 성공, ${total_cost:.4f}")


if __name__ == "__main__":
    main()
