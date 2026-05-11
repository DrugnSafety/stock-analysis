#!/usr/bin/env python3
"""Push plugin source code + config files to GitHub repo (separate from analysis logs).

분석 결과(.analysis-log/)는 sync_analysis.py가 처리.
이 스크립트는 plugin 코드 자체(plugins/, commands/, .claude/, scripts/, CLAUDE.md, README.md, ...)를
GitHub에 push하여 코드 버전 관리.

사용법:
    python3 push_plugin_code.py                # 모든 plugin code push
    python3 push_plugin_code.py --plugins-only  # plugins/ 디렉토리만
    python3 push_plugin_code.py --dry-run       # push할 파일 목록만 표시
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Iterable

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from github_client import push_file, ensure_repo, get_token, get_owner, get_repo


# Files to ALWAYS push (top-level config + docs)
ROOT_FILES = [
    "README.md",
    "CLAUDE.md",
    "REPORT_FORMAT_STANDARD.md",
    "ENHANCEMENT_ROADMAP.md",
]

# Directories whose contents to push
PUSH_DIRS = [
    "plugins",
    "commands",
    ".claude",
    "scripts",
]

# Files/patterns to exclude
EXCLUDE_PATTERNS = [
    "__pycache__",
    ".pyc",
    ".DS_Store",
    ".pytest_cache",
    ".cache",
    "node_modules",
    ".env",  # NEVER push .env (contains secrets)
    ".env.bak",
    ".gitignore",  # We'll create a fresh one
    "stocks.json.placeholder_backup",
]


def should_exclude(path: Path) -> bool:
    s = path.as_posix()
    for pat in EXCLUDE_PATTERNS:
        if pat in s:
            return True
    return False


def collect_files(repo_root: Path, plugins_only: bool = False) -> list[Path]:
    """Walk and collect files to push."""
    files = []

    if not plugins_only:
        # Root files
        for f in ROOT_FILES:
            p = repo_root / f
            if p.exists() and not should_exclude(p):
                files.append(p)

    # Directories
    dirs_to_push = ["plugins"] if plugins_only else PUSH_DIRS
    for d in dirs_to_push:
        dir_path = repo_root / d
        if not dir_path.exists():
            continue
        for p in dir_path.rglob("*"):
            if p.is_file() and not should_exclude(p):
                # Skip binary/large files (>10MB)
                if p.stat().st_size > 10 * 1024 * 1024:
                    print(f"[skip] {p} too large ({p.stat().st_size / 1024 / 1024:.1f} MB)")
                    continue
                files.append(p)

    return files


def push_files(repo_root: Path, files: list[Path], dry_run: bool = False,
               delay_sec: float = 0.3) -> dict:
    """Push files one by one with rate-limit-friendly delay."""
    if not get_token():
        return {"status": "error", "reason": "GITHUB_TOKEN not set"}

    try:
        repo_info = ensure_repo()
    except Exception as e:
        return {"status": "error", "reason": f"ensure_repo failed: {e}"}

    success = []
    failed = []
    for i, p in enumerate(files, 1):
        rel = p.resolve().as_posix().replace(repo_root.resolve().as_posix() + "/", "")
        if dry_run:
            print(f"[dry-run {i}/{len(files)}] would push: {rel} ({p.stat().st_size} bytes)")
            continue
        try:
            push_file(p, rel, f"code: sync plugin code ({p.parent.name}/{p.name})")
            success.append(rel)
            print(f"[{i}/{len(files)}] ✓ {rel}")
            time.sleep(delay_sec)  # rate limit friendly
        except Exception as e:
            failed.append((rel, str(e)[:100]))
            print(f"[{i}/{len(files)}] ✗ {rel} — {e}")

    return {
        "status": "ok" if not failed else "partial",
        "repo": repo_info.get("html_url"),
        "success_count": len(success),
        "failed_count": len(failed),
        "failed_files": failed[:10],
    }


def main():
    p = argparse.ArgumentParser(description="Push plugin code to GitHub")
    p.add_argument("--repo-root", default=".", help="Repo root directory")
    p.add_argument("--plugins-only", action="store_true", help="Only push plugins/ dir")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--max-files", type=int, default=500, help="Cap on files per run")
    args = p.parse_args()

    repo_root = Path(args.repo_root).resolve()
    print(f"Repo root: {repo_root}")

    files = collect_files(repo_root, plugins_only=args.plugins_only)
    print(f"Found {len(files)} files to push")
    if len(files) > args.max_files:
        print(f"Capping at {args.max_files} (use --max-files to increase)")
        files = files[:args.max_files]

    result = push_files(repo_root, files, dry_run=args.dry_run)
    print(f"\n=== Result ===")
    print(f"Status: {result['status']}")
    if result.get("success_count"):
        print(f"Pushed: {result['success_count']}")
    if result.get("failed_count"):
        print(f"Failed: {result['failed_count']}")
        for rel, err in result.get("failed_files", []):
            print(f"  - {rel}: {err}")


if __name__ == "__main__":
    main()
