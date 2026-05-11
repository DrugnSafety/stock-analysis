#!/usr/bin/env python3
"""Blogger Registry — yaml 로드 + 라우팅 헬퍼."""
import argparse
import json
import sys
from pathlib import Path


def find_registry_path() -> Path:
    """registry.yaml 위치 탐색 (workspace 기준)."""
    cwd = Path.cwd()
    for ancestor in [cwd] + list(cwd.parents)[:5]:
        candidate = ancestor / "plugins" / "blogger-registry" / "registry.yaml"
        if candidate.exists():
            return candidate
    raise SystemExit("registry.yaml 미발견")


def load_yaml_simple(path: Path) -> dict:
    """간단 YAML 파서 (PyYAML 없이) — registry.yaml 형식 한정."""
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except ImportError:
        # Fallback — 매우 단순한 파서
        text = path.read_text(encoding="utf-8")
        # 외부 dependency 회피용 단순 변환은 제한적이라 PyYAML 권장
        raise SystemExit("PyYAML 필요: pip install pyyaml")


def list_bloggers(reg: dict, only_enabled: bool = True) -> list[dict]:
    out = []
    for bid, b in (reg.get("bloggers") or {}).items():
        if only_enabled and not b.get("enabled", True):
            continue
        out.append({**b, "blog_id": bid})
    return out


def get_blogger(reg: dict, blog_id: str) -> dict | None:
    return (reg.get("bloggers") or {}).get(blog_id)


def get_paths(reg: dict, blog_id: str) -> dict:
    """블로거별 ledger·posts 경로 (workspace 기준 상대)."""
    defaults = reg.get("defaults", {})
    ledger_tpl = defaults.get("ledger_dir", ".analysis-log/bloggers/{blog_id}/ledger.jsonl")
    posts_tpl = defaults.get("posts_dir", ".analysis-log/bloggers/{blog_id}/posts")
    return {
        "blog_id": blog_id,
        "ledger": ledger_tpl.format(blog_id=blog_id),
        "posts_dir": posts_tpl.format(blog_id=blog_id),
        "panel_dir": f".analysis-log/bloggers/{blog_id}/persona_panel",
        "debate_dir": f".analysis-log/bloggers/{blog_id}/debates",
        "arena_dir": f".analysis-log/bloggers/{blog_id}/arena",
    }


def main():
    parser = argparse.ArgumentParser(description="Registry loader")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list")
    p_get = sub.add_parser("get")
    p_get.add_argument("blog_id")
    p_paths = sub.add_parser("paths")
    p_paths.add_argument("blog_id")
    p_init = sub.add_parser("init-dirs")
    p_init.add_argument("--all", action="store_true")
    p_init.add_argument("--blog-id")

    args = parser.parse_args()
    reg_path = find_registry_path()
    reg = load_yaml_simple(reg_path)

    if args.cmd == "list":
        bloggers = list_bloggers(reg)
        print(f"# {len(bloggers)} bloggers (enabled)")
        for b in bloggers:
            print(f"  {b['blog_id']:18s} | {b.get('nickname', '?'):10s} | "
                  f"weight_kr={b.get('trust_weight_kr', 1.0)} | {b.get('blog_name', '')[:50]}")

    elif args.cmd == "get":
        b = get_blogger(reg, args.blog_id)
        if not b:
            raise SystemExit(f"미등록: {args.blog_id}")
        print(json.dumps(b, ensure_ascii=False, indent=2))

    elif args.cmd == "paths":
        paths = get_paths(reg, args.blog_id)
        print(json.dumps(paths, ensure_ascii=False, indent=2))

    elif args.cmd == "init-dirs":
        bloggers = list_bloggers(reg) if args.all else (
            [{"blog_id": args.blog_id}] if args.blog_id else []
        )
        if not bloggers:
            raise SystemExit("--all 또는 --blog-id 필요")
        for b in bloggers:
            paths = get_paths(reg, b["blog_id"])
            for p in [paths["ledger"], paths["posts_dir"], paths["panel_dir"],
                      paths["debate_dir"], paths["arena_dir"]]:
                target = Path(p)
                if p.endswith("ledger.jsonl"):
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.touch(exist_ok=True)
                else:
                    target.mkdir(parents=True, exist_ok=True)
            print(f"[init] {b['blog_id']} dirs created")


if __name__ == "__main__":
    main()
