#!/usr/bin/env python3
"""Arena Orchestrator — 7-role 분석 병렬 실행."""
import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent
SCRIPTS_DIR = PLUGIN_ROOT / "skills"


def run_worker(name: str, cmd: list, timeout: int) -> dict:
    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        if r.returncode == 0:
            return {"name": name, "status": "success", "elapsed_seconds": round(elapsed, 2),
                    "stdout": r.stdout[-1500:], "stderr": r.stderr[-500:]}
        else:
            return {"name": name, "status": "failed", "elapsed_seconds": round(elapsed, 2),
                    "returncode": r.returncode, "stdout": r.stdout[-1500:], "stderr": r.stderr[-1500:]}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "timeout", "elapsed_seconds": timeout}
    except Exception as e:
        return {"name": name, "status": "error", "error": str(e)[:500]}


def main():
    parser = argparse.ArgumentParser(description="Arena 7-role 분석 병렬 실행")
    parser.add_argument("ticker")
    parser.add_argument("--market", required=True)
    parser.add_argument("--post")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include", default="claude,openai,gemini")
    parser.add_argument("--blog-url")
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    workers = [w.strip() for w in args.include.split(",")]

    common_args = ["--market", args.market]
    if args.post:
        common_args += ["--post", args.post]
    if args.blog_url:
        common_args += ["--blog-url", args.blog_url]

    jobs = []
    if "openai" in workers:
        jobs.append((
            "openai",
            [sys.executable, str(SCRIPTS_DIR / "openai-worker" / "scripts" / "analyze_openai.py"),
             args.ticker, *common_args, "--output", str(out_dir / "openai.json")],
            out_dir / "openai.json",
        ))
    if "gemini" in workers:
        jobs.append((
            "gemini",
            [sys.executable, str(SCRIPTS_DIR / "gemini-worker" / "scripts" / "analyze_gemini.py"),
             args.ticker, *common_args, "--output", str(out_dir / "gemini.json")],
            out_dir / "gemini.json",
        ))

    if "claude" in workers:
        claude_placeholder = {
            "_pending": True,
            "instruction": (
                f"Claude (current Cowork session) should follow trading-analysis SKILL.md "
                f"to analyze ticker {args.ticker} using market data at {args.market} "
                f"(and post {args.post if args.post else 'N/A'}), then overwrite this file."
            ),
            "ticker": args.ticker,
            "market_path": args.market,
            "post_path": args.post or "",
            "blog_url": args.blog_url or "",
        }
        with open(out_dir / "claude.json", "w", encoding="utf-8") as f:
            json.dump(claude_placeholder, f, ensure_ascii=False, indent=2)

    print(f"[arena-analyze] {args.ticker} dispatching {len(jobs)} external workers...")

    results = []
    if jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            futures = {pool.submit(run_worker, name, cmd, args.timeout): name
                       for name, cmd, _ in jobs}
            for fut in concurrent.futures.as_completed(futures):
                r = fut.result()
                print(f"[arena-analyze] {r['name']}: {r['status']} ({r.get('elapsed_seconds', '?')}s)")
                results.append(r)

    if "claude" in workers:
        results.append({
            "name": "claude",
            "status": "pending_session",
        })

    # 비용 집계
    total_cost = 0.0
    for _name, _cmd, path in jobs:
        if path.exists():
            try:
                d = json.load(open(path, encoding="utf-8"))
                cost = d.get("_meta", {}).get("estimated_cost_usd", 0)
                total_cost += cost
            except Exception:
                pass

    orchestration = {
        "type": "analyze",
        "ticker": args.ticker,
        "started_at": datetime.now(KST).isoformat(),
        "output_dir": str(out_dir),
        "workers_requested": workers,
        "results": results,
        "total_cost_usd_external": round(total_cost, 4),
    }
    with open(out_dir / "orchestration.json", "w", encoding="utf-8") as f:
        json.dump(orchestration, f, ensure_ascii=False, indent=2)

    print(f"[arena-analyze] 외부 worker 비용: ${total_cost:.4f}")


if __name__ == "__main__":
    main()
