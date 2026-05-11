#!/usr/bin/env python3
"""메르 블로그 과거 글 메타데이터 수집기."""
import argparse
import json
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

KST = timezone(timedelta(hours=9))
BLOG_ID = "ranto28"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://m.blog.naver.com/",
}


def fetch_post_list_page(blog_id: str, page: int = 1) -> list[dict]:
    """모바일 메르 블로그의 한 페이지에서 post 메타데이터 추출."""
    url = (f"https://m.blog.naver.com/PostList.naver?"
           f"blogId={blog_id}&from=postList&categoryNo=0&currentPage={page}")
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    posts = []
    # 모바일 페이지의 post 항목들
    items = soup.select("a.link__youOg, a.link, a[href*='/PostView']")
    seen_logs = set()

    for a in items:
        href = a.get("href", "")
        # logNo 추출
        m = re.search(r"logNo=(\d+)|/(\d{12,})(?:[?#]|$)", href)
        if not m:
            continue
        log_no = m.group(1) or m.group(2)
        if log_no in seen_logs:
            continue
        seen_logs.add(log_no)

        title_el = a.select_one(".tit_post, .title_post, strong")
        title = (title_el.get_text(strip=True) if title_el
                 else a.get_text(strip=True))[:200]
        if not title or "더보기" in title or "관리" in title:
            continue

        # 날짜 정보 시도
        date_str = ""
        parent = a.find_parent("li") or a.find_parent("div")
        if parent:
            date_el = parent.select_one(".date, .info_post .date, time")
            if date_el:
                date_str = date_el.get_text(strip=True)

        posts.append({
            "log_no": log_no,
            "url": f"https://blog.naver.com/{blog_id}/{log_no}",
            "title": title,
            "published_at": _normalize_date(date_str),
            "raw_date": date_str,
        })

    return posts


def _normalize_date(s: str) -> str:
    """'2026. 4. 28.' → '2026-04-28'."""
    if not s:
        return ""
    m = re.search(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})", s)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"
    return s


def collect_with_pagination(blog_id: str, max_pages: int = 50,
                            rate_limit_sec: float = 0.6) -> list[dict]:
    """페이징하여 가능한 모든 글 메타데이터 수집."""
    all_posts = []
    seen = set()

    for page in range(1, max_pages + 1):
        try:
            posts = fetch_post_list_page(blog_id, page)
        except requests.HTTPError as e:
            print(f"[collector] page {page} HTTP error: {e}", file=sys.stderr)
            if e.response.status_code == 403:
                # 봇 차단 — 페이지 시도 중단
                break
            continue
        except Exception as e:
            print(f"[collector] page {page} 실패: {e}", file=sys.stderr)
            continue

        new_count = 0
        for p in posts:
            if p["log_no"] not in seen:
                seen.add(p["log_no"])
                all_posts.append(p)
                new_count += 1

        print(f"[collector] page {page}: {new_count} new (total {len(all_posts)})",
              file=sys.stderr)

        if new_count == 0:
            # 페이지에 새 글 없음 → 끝 도달
            break

        time.sleep(rate_limit_sec)

    return all_posts


def filter_by_date(posts: list[dict], start: str = "", end: str = "") -> list[dict]:
    """published_at 범위로 필터."""
    out = []
    for p in posts:
        d = p.get("published_at", "")
        if not d:
            continue
        if start and d < start:
            continue
        if end and d > end:
            continue
        out.append(p)
    return out


def filter_by_keyword(posts: list[dict], keywords: list[str]) -> list[dict]:
    """제목에 키워드 포함 필터."""
    if not keywords:
        return posts
    return [p for p in posts if any(kw in p.get("title", "") for kw in keywords)]


def sample_posts(posts: list[dict], strategy: str) -> list[dict]:
    """sampling 전략 적용."""
    if strategy == "all":
        return posts

    posts_sorted = sorted(posts, key=lambda x: x.get("published_at", ""))

    if strategy == "monthly_first":
        seen_months = set()
        out = []
        for p in posts_sorted:
            d = p.get("published_at", "")
            if len(d) >= 7:
                ym = d[:7]
                if ym not in seen_months:
                    seen_months.add(ym)
                    out.append(p)
        return out

    if strategy == "monthly_last":
        by_month = {}
        for p in posts_sorted:
            d = p.get("published_at", "")
            if len(d) >= 7:
                by_month[d[:7]] = p
        return list(by_month.values())

    if strategy == "weekly_random":
        import random
        random.seed(42)
        by_week = {}
        for p in posts_sorted:
            d = p.get("published_at", "")
            if len(d) >= 10:
                try:
                    dt = datetime.strptime(d, "%Y-%m-%d")
                    key = f"{dt.year}-W{dt.isocalendar().week}"
                    by_week.setdefault(key, []).append(p)
                except ValueError:
                    pass
        return [random.choice(ps) for ps in by_week.values()]

    return posts_sorted


def main():
    parser = argparse.ArgumentParser(description="메르 블로그 과거 글 메타데이터 수집")
    parser.add_argument("--blog-id", default=BLOG_ID)
    parser.add_argument("--start-date", default="")
    parser.add_argument("--end-date", default="")
    parser.add_argument("--keyword", default="", help="콤마 구분 키워드")
    parser.add_argument("--sample", default="all",
                        choices=["all", "monthly_first", "monthly_last", "weekly_random"])
    parser.add_argument("--max-pages", type=int, default=50)
    parser.add_argument("--update-existing", help="기존 JSON 파일에 incremental 추가")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    print(f"[collector] {args.blog_id} 페이징 수집 시작 (max_pages={args.max_pages})",
          file=sys.stderr)
    posts = collect_with_pagination(args.blog_id, args.max_pages)
    print(f"[collector] 수집 완료: {len(posts)}개", file=sys.stderr)

    # 기존 파일 merge
    if args.update_existing and Path(args.update_existing).exists():
        with open(args.update_existing, encoding="utf-8") as f:
            existing = json.load(f)
        existing_logs = {p["log_no"] for p in existing.get("posts", [])}
        new_posts = [p for p in posts if p["log_no"] not in existing_logs]
        posts = existing.get("posts", []) + new_posts
        print(f"[collector] {len(new_posts)} new posts merged", file=sys.stderr)

    # 필터
    if args.start_date or args.end_date:
        posts = filter_by_date(posts, args.start_date, args.end_date)
    if args.keyword:
        keywords = [k.strip() for k in args.keyword.split(",") if k.strip()]
        posts = filter_by_keyword(posts, keywords)
    posts = sample_posts(posts, args.sample)

    posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    result = {
        "blog_id": args.blog_id,
        "blogger_name": "메르",
        "collected_at": datetime.now(KST).isoformat(),
        "filters": {
            "start_date": args.start_date,
            "end_date": args.end_date,
            "keyword": args.keyword,
            "sample": args.sample,
        },
        "n_posts": len(posts),
        "posts": posts,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[collector] 저장: {args.output}")
    print(f"  기간: {args.start_date or '전체'} ~ {args.end_date or '오늘'}")
    print(f"  Sampling: {args.sample}")
    print(f"  최종 수집: {len(posts)}개")
    if posts:
        print(f"  최근 글: {posts[0].get('title', '')[:60]} ({posts[0].get('published_at', '')})")
        print(f"  과거 글: {posts[-1].get('title', '')[:60]} ({posts[-1].get('published_at', '')})")


if __name__ == "__main__":
    main()
