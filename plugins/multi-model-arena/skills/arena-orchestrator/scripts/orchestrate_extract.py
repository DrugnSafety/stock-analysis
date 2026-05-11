#!/usr/bin/env python3
"""Arena Orchestrator — 종목 추출 병렬 실행."""
import argparse
import concurrent.futures
import json
import subprocess
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))
PLUGIN_ROOT = Path(__file__).resolve().parent.parent.parent.parent  # plugins/multi-model-arena/
SCRIPTS_DIR = PLUGIN_ROOT / "skills"


def run_worker(name: str, cmd: list, timeout: int) -> dict:
    """단일 worker 실행 + 결과 metadata 반환."""
    start = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        elapsed = time.time() - start
        if r.returncode == 0:
            return {"name": name, "status": "success", "elapsed_seconds": round(elapsed, 2),
                    "stdout": r.stdout[-2000:], "stderr": r.stderr[-500:]}
        else:
            return {"name": name, "status": "failed", "elapsed_seconds": round(elapsed, 2),
                    "returncode": r.returncode, "stdout": r.stdout[-2000:], "stderr": r.stderr[-2000:]}
    except subprocess.TimeoutExpired:
        return {"name": name, "status": "timeout", "elapsed_seconds": timeout}
    except Exception as e:
        return {"name": name, "status": "error", "error": str(e)[:500]}


def main():
    parser = argparse.ArgumentParser(description="Arena 종목 추출 병렬 실행")
    parser.add_argument("post_json")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--include", default="claude,openai,gemini",
                        help="실행할 worker, 콤마 구분")
    parser.add_argument("--blog-url")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    workers = [w.strip() for w in args.include.split(",")]
    blog_url_args = ["--blog-url", args.blog_url] if args.blog_url else []

    jobs = []  # (name, cmd, output_path)

    if "openai" in workers:
        jobs.append((
            "openai",
            [sys.executable, str(SCRIPTS_DIR / "openai-worker" / "scripts" / "extract_openai.py"),
             args.post_json, "--output", str(out_dir / "openai.json")] + blog_url_args,
            out_dir / "openai.json",
        ))

    if "gemini" in workers:
        jobs.append((
            "gemini",
            [sys.executable, str(SCRIPTS_DIR / "gemini-worker" / "scripts" / "extract_gemini.py"),
             args.post_json, "--output", str(out_dir / "gemini.json")] + blog_url_args,
            out_dir / "gemini.json",
        ))

    # Claude worker는 placeholder (사용자 세션의 Claude가 채움)
    if "claude" in workers:
        claude_placeholder = {
            "_pending": True,
            "instruction": (
                f"Claude (current Cowork session) should follow the stock-extractor SKILL.md "
                f"7원칙 to read {args.post_json}, perform extraction, and overwrite this file "
                f"with the JSON result. Output schema must match openai/gemini siblings."
            ),
            "post_json_path": args.post_json,
            "blog_url": args.blog_url or "",
        }
        with open(out_dir / "claude.json", "w", encoding="utf-8") as f:
            json.dump(claude_placeholder, f, ensure_ascii=False, indent=2)

    print(f"[arena] dispatching {len(jobs)} external workers (claude is in-session)...")
    print(f"        output: {out_dir}")

    results = []
    if jobs:
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(jobs)) as pool:
            futures = {pool.submit(run_worker, name, cmd, args.timeout): name
                       for name, cmd, _ in jobs}
            for fut in concurrent.futures.as_completed(futures):
                r = fut.result()
                print(f"[arena] {r['name']}: {r['status']} ({r.get('elapsed_seconds', '?')}s)")
                results.append(r)

    # Claude는 별도 처리 표시
    if "claude" in workers:
        results.append({
            "name": "claude",
            "status": "pending_session",
            "note": "Will be filled by current Cowork Claude session inline.",
        })

    # 비용 집계
    total_cost = 0.0
    for name, _cmd, path in jobs:
        if path.exists():
            try:
                d = json.load(open(path, encoding="utf-8"))
                cost = d.get("extraction_meta", {}).get("estimated_cost_usd", 0)
                total_cost += cost
            except Exception:
                pass

    orchestration = {
        "type": "extract",
        "started_at": datetime.now(KST).isoformat(),
        "input_post": args.post_json,
        "output_dir": str(out_dir),
        "workers_requested": workers,
        "results": results,
        "total_cost_usd_external": round(total_cost, 4),
    }
    with open(out_dir / "orchestration.json", "w", encoding="utf-8") as f:
        json.dump(orchestration, f, ensure_ascii=False, indent=2)

    print(f"[arena] 외부 worker 비용 합계: ${total_cost:.4f}")
    print(f"[arena] orchestration.json 저장")
    if "claude" in workers:
        print(f"[arena] ⚠️  claude.json은 Cowork Claude 세션이 채워야 합니다.")


if __name__ == "__main__":
    main()
