"""GitHub REST API 클라이언트 — repo 생성, 파일 push, release.

API doc: https://docs.github.com/en/rest

Setup:
  1. Personal Access Token 발급: https://github.com/settings/tokens
     - Scope: repo (full control of private repositories)
  2. .env에 추가:
     GITHUB_TOKEN=ghp_...
     GITHUB_OWNER=DrugnSafety
     GITHUB_REPO=stock-analysis  (없으면 첫 sync 시 자동 생성)
"""
from __future__ import annotations

import base64
import json
import os
from pathlib import Path
from typing import Optional


def _read_env_key(key: str) -> Optional[str]:
    v = os.environ.get(key)
    if v:
        return v
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    candidates = [Path.cwd() / ".env"]
    if project_dir:
        candidates.append(Path(project_dir) / ".env")
    candidates.append(Path(__file__).resolve().parent.parent.parent.parent / ".env")
    for env_path in candidates:
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.strip().startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def get_token() -> Optional[str]:
    return _read_env_key("GITHUB_TOKEN")


def get_owner() -> Optional[str]:
    return _read_env_key("GITHUB_OWNER")


def get_repo() -> Optional[str]:
    return _read_env_key("GITHUB_REPO") or "stock-analysis"


def get_status() -> dict:
    return {
        "token_configured": get_token() is not None,
        "owner": get_owner(),
        "repo": get_repo(),
    }


def _headers() -> dict:
    token = get_token()
    if not token:
        raise RuntimeError("GITHUB_TOKEN not set in .env")
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "stock-analysis-sync/0.1.0",
    }


def repo_exists(owner: str, repo: str) -> bool:
    import requests
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=_headers(), timeout=15)
    return r.status_code == 200


def create_repo(repo: str, description: str = "", private: bool = True) -> dict:
    """Create new private repo under authenticated user."""
    import requests
    body = {
        "name": repo,
        "description": description or "주식 분석 시스템 — 13명 페르소나 패널 + 5Y/5Q US-GAAP 재무 분석",
        "private": private,
        "auto_init": True,  # creates initial README + main branch
        "license_template": "mit",
    }
    r = requests.post("https://api.github.com/user/repos", headers=_headers(), json=body, timeout=20)
    r.raise_for_status()
    return r.json()


def ensure_repo() -> dict:
    """Idempotent: create repo if not exists, return repo info."""
    owner = get_owner()
    repo = get_repo()
    if not owner or not repo:
        raise RuntimeError("GITHUB_OWNER and GITHUB_REPO must be set in .env")
    if repo_exists(owner, repo):
        import requests
        r = requests.get(f"https://api.github.com/repos/{owner}/{repo}", headers=_headers(), timeout=15)
        return r.json()
    print(f"[github] creating new private repo: {owner}/{repo}")
    return create_repo(repo)


def get_file_sha(owner: str, repo: str, path: str, branch: str = "main") -> Optional[str]:
    """Get SHA of existing file for update. Returns None if not exists."""
    import requests
    r = requests.get(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        params={"ref": branch},
        headers=_headers(), timeout=15
    )
    if r.status_code == 200:
        return r.json().get("sha")
    return None


def put_file(owner: str, repo: str, path: str, content_bytes: bytes,
             message: str, branch: str = "main") -> dict:
    """Create or update a file in the repo. Idempotent via sha."""
    import requests
    body = {
        "message": message,
        "content": base64.b64encode(content_bytes).decode("ascii"),
        "branch": branch,
    }
    existing_sha = get_file_sha(owner, repo, path, branch)
    if existing_sha:
        body["sha"] = existing_sha

    r = requests.put(
        f"https://api.github.com/repos/{owner}/{repo}/contents/{path}",
        headers=_headers(), json=body, timeout=30,
    )
    r.raise_for_status()
    return r.json()


def push_file(local_path: Path, repo_path: str, commit_message: str) -> dict:
    """Push a single local file to GitHub repo."""
    owner = get_owner()
    repo = get_repo()
    if not local_path.exists():
        raise FileNotFoundError(str(local_path))
    return put_file(owner, repo, repo_path, local_path.read_bytes(), commit_message)


def push_text(content: str, repo_path: str, commit_message: str) -> dict:
    """Push string content as a file."""
    owner = get_owner()
    repo = get_repo()
    return put_file(owner, repo, repo_path, content.encode("utf-8"), commit_message)


# ============== CLI ==============
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="GitHub API client")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("ensure-repo")

    pp = sub.add_parser("push")
    pp.add_argument("local_path")
    pp.add_argument("repo_path")
    pp.add_argument("--message", default="auto: sync from analysis")

    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps(get_status(), indent=2))
    elif args.cmd == "ensure-repo":
        info = ensure_repo()
        print(f"Repo: {info['html_url']}")
        print(f"Default branch: {info.get('default_branch', 'main')}")
        print(f"Private: {info.get('private')}")
    elif args.cmd == "push":
        result = push_file(Path(args.local_path), args.repo_path, args.message)
        print(f"Pushed: {result.get('content', {}).get('html_url', 'unknown')}")
