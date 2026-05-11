#!/usr/bin/env python3
"""Multi-Blogger Collector — registry의 어떤 블로거든 수집.

기존 collect_meru_v2.py를 일반화. registry.yaml에서 blog_id 자동 lookup.
"""
import argparse
import json
import re
import sys
import time
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests

KST = timezone(timedelta(hours=9))


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 Chrome/126.0",
    "Referer": "https://blog.naver.com/",
}


# Registry loader 재사용
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "registry-loader" / "scripts"))


def fetch_page(blog_id: str, page: int, count: int = 30) -> list[dict]:
    url = (f"https://blog.naver.com/PostTitleListAsync.naver?"
           f"blogId={blog_id}&viewdate=&currentPage={page}"
           f"&categoryNo=0&parentCategoryNo=&countPerPage={count}")
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    text = r.text
    try:
        data = json.loads(text, strict=False)
    except json.JSONDecodeError:
        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
        data = json.loads(cleaned, strict=False)
    if data.get("resultCode") != "S":
        return []

    out = []
    for p in data.get("postList", []):
        log_no = p.get("logNo", "")
        title = urllib.parse.unquote_plus(p.get("title", "").replace("+", " "))
        out.append({
            "log_no": log_no,
            "url": f"https://blog.naver.com/{blog_id}/{log_no}",
            "title": title.strip(),
            "raw_addDate": p.get("addDate", ""),
            "comment_count": int(str(p.get("commentCount", 0) or 0).replace(",", "")),
            "category_no": p.get("categoryNo", ""),
        })
    return out


def normalize_date(raw: str, today: datetime) -> str:
    raw = (raw or "").strip()
    if not raw:
        return ""
    m = re.match(r"(\d+)\s*(시간|분|일)\s*전", raw)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "시간":
            d = today - timedelta(hours=n)
        elif unit == "분":
            d = today - timedelta(minutes=n)
        else:
            d = today - timedelta(days=n)
        return d.strftime("%Y-%m-%d")
    if raw == "어제":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if raw == "그저께":
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")
    m = re.match(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})", raw)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    return raw


def collect(blog_id: str, max_pages: int = 30, count: int = 30, rate: float = 0.4) -> list[dict]:
    today = datetime.now(KST)
    posts = []
    seen = set()
    for page in range(1, max_pages + 1):
        try:
            items = fetch_page(blog_id, page, count)
        except Exception as e:
            print(f"  page {page} 실패: {e}", file=sys.stderr)
            break
        new_count = 0
        for it in items:
            if it["log_no"] in seen:
                continue
            seen.add(it["log_no"])
            it["published_at"] = normalize_date(it["raw_addDate"], today)
            posts.append(it)
            new_count += 1
        if new_count == 0:
            break
        time.sleep(rate)
    return posts


def filter_by_date(posts: list[dict], start: str = "", end: str = "") -> list[dict]:
    return [p for p in posts
            if (not p.get("published_at") or "전" in p.get("published_at", "")) is False
            and (not start or p.get("published_at", "") >= start)
            and (not end or p.get("published_at", "") <= end)]


def filter_by_keyword(posts: list[dict], keywords: list[str]) -> list[dict]:
    if not keywords:
        return posts
    return [p for p in posts if any(kw in p.get("title", "") for kw in keywords)]


def sample_posts(posts: list[dict], strategy: str) -> list[dict]:
    if strategy == "all":
        return posts
    posts_sorted = sorted(posts, key=lambda x: x.get("published_at", ""))
    if strategy == "monthly_first":
        seen_months = set()
        out = []
        for p in posts_sorted:
            d = p.get("published_at", "")
            if len(d) >= 7 and d[:7] not in seen_months:
                seen_months.add(d[:7])
                out.append(p)
        return out
    return posts_sorted


def main():
    parser = argparse.ArgumentParser(description="Multi-Blogger Collector")
    parser.add_argument("--blog-id", help="단일 블로거 (없으면 registry 모든 enabled)")
    parser.add_argument("--start-date", default="")
    parser.add_argument("--end-date", default="")
    parser.add_argument("--keyword", default="")
    parser.add_argument("--sample", default="all",
                        choices=["all", "monthly_first", "monthly_last"])
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--output-dir", default=".analysis-log/bloggers",
                        help="블로거별 hierarchy 사용. 또는 --output 으로 단일 파일")
    parser.add_argument("--output", help="단일 파일 출력 (blog_id 1개 모드)")
    args = parser.parse_args()

    from load_registry import find_registry_path, load_yaml_simple, list_bloggers

    reg = load_yaml_simple(find_registry_path())
    if args.blog_id:
        blog_ids = [args.blog_id]
    else:
        blog_ids = [b["blog_id"] for b in list_bloggers(reg)]

    print(f"[multi-collect] 대상 블로거 {len(blog_ids)}명: {', '.join(blog_ids)}", file=sys.stderr)

    all_results = {}
    for bid in blog_ids:
        print(f"\n[multi-collect] === {bid} ===", file=sys.stderr)
        posts = collect(bid, args.max_pages)
        if args.start_date or args.end_date:
            posts = filter_by_date(posts, args.start_date, args.end_date)
        if args.keyword:
            kws = [k.strip() for k in args.keyword.split(",") if k.strip()]
            posts = filter_by_keyword(posts, kws)
        posts = sample_posts(posts, args.sample)
        posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)

        result = {
            "blog_id": bid,
            "collected_at": datetime.now(KST).isoformat(),
            "filters": {"start_date": args.start_date, "end_date": args.end_date,
                        "sample": args.sample, "keyword": args.keyword},
            "n_posts": len(posts),
            "posts": posts,
        }
        all_results[bid] = result

        # 저장
        if args.output and len(blog_ids) == 1:
            out_path = Path(args.output)
        else:
            out_path = Path(args.output_dir) / bid / "history.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"  {len(posts)}개 글 저장: {out_path}")
        if posts:
            print(f"  최근: {posts[0].get('title', '')[:50]} ({posts[0].get('published_at', '')})")
            print(f"  과거: {posts[-1].get('title', '')[:50]} ({posts[-1].get('published_at', '')})")

    # Total summary
    total = sum(r["n_posts"] for r in all_results.values())
    print(f"\n[multi-collect] 완료 — {len(blog_ids)}명, 총 {total}개 글")


if __name__ == "__main__":
    main()
