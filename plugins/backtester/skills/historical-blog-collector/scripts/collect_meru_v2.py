#!/usr/bin/env python3
"""메르 블로그 collector v2 — PostTitleListAsync.naver JSON API 활용.

이 endpoint는 JSON으로 logNo·title·addDate를 반환하므로 v1의 모바일 페이지
HTML 파싱(JS 렌더링 의존) 문제 회피.
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
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/126.0.0.0 Safari/537.36",
    "Referer": "https://blog.naver.com/ranto28",
}


def fetch_page(blog_id: str, page: int, count: int = 30) -> list[dict]:
    url = (f"https://blog.naver.com/PostTitleListAsync.naver?"
           f"blogId={blog_id}&viewdate=&currentPage={page}"
           f"&categoryNo=0&parentCategoryNo=&countPerPage={count}")
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    # 일부 title에 \\ 같은 escape가 깨져 들어와 strict 파싱 실패 → 직접 json.loads
    text = r.text
    try:
        data = json.loads(text, strict=False)
    except json.JSONDecodeError:
        # backslash 단독을 escape — naive cleaning
        cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', text)
        data = json.loads(cleaned, strict=False)
    if data.get("resultCode") != "S":
        return []

    out = []
    for p in data.get("postList", []):
        log_no = p.get("logNo", "")
        title_enc = p.get("title", "")
        title = urllib.parse.unquote_plus(title_enc.replace("+", " "))
        # space encoding을 + 로 한 case 추가 처리
        title = title.replace("+", " ")
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
    """addDate를 YYYY-MM-DD로 정규화."""
    raw = raw.strip()
    if not raw:
        return ""
    # "4시간 전", "11시간 전", "30분 전"
    m = re.match(r"(\d+)\s*(시간|분|일)\s*전", raw)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "시간":
            d = today - timedelta(hours=n)
        elif unit == "분":
            d = today - timedelta(minutes=n)
        else:  # 일
            d = today - timedelta(days=n)
        return d.strftime("%Y-%m-%d")

    # "어제", "그저께"
    if raw == "어제":
        return (today - timedelta(days=1)).strftime("%Y-%m-%d")
    if raw == "그저께":
        return (today - timedelta(days=2)).strftime("%Y-%m-%d")

    # "2026. 4. 28." or "2025. 10. 15."
    m = re.match(r"(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})", raw)
    if m:
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"

    return raw


def collect(blog_id: str, max_pages: int, count_per_page: int = 30,
            rate_limit_sec: float = 0.4) -> list[dict]:
    today = datetime.now(KST)
    posts = []
    seen = set()

    for page in range(1, max_pages + 1):
        try:
            items = fetch_page(blog_id, page, count_per_page)
        except Exception as e:
            print(f"[collector-v2] page {page} 실패: {e}", file=sys.stderr)
            break

        new_count = 0
        for it in items:
            if it["log_no"] in seen:
                continue
            seen.add(it["log_no"])
            it["published_at"] = normalize_date(it["raw_addDate"], today)
            posts.append(it)
            new_count += 1

        print(f"[collector-v2] page {page}: {new_count} new (total {len(posts)})",
              file=sys.stderr)

        if new_count == 0:
            break

        time.sleep(rate_limit_sec)

    return posts


def filter_by_date(posts: list[dict], start: str = "", end: str = "") -> list[dict]:
    out = []
    for p in posts:
        d = p.get("published_at", "")
        if not d or "전" in d:  # "X시간 전" 등 정규화 안 된 것 제외
            continue
        if start and d < start:
            continue
        if end and d > end:
            continue
        out.append(p)
    return out


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

    return posts_sorted


def main():
    parser = argparse.ArgumentParser(description="메르 블로그 collector v2 (JSON API)")
    parser.add_argument("--blog-id", default="ranto28")
    parser.add_argument("--start-date", default="")
    parser.add_argument("--end-date", default="")
    parser.add_argument("--keyword", default="")
    parser.add_argument("--sample", default="all",
                        choices=["all", "monthly_first", "monthly_last"])
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--count-per-page", type=int, default=30)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    print(f"[collector-v2] {args.blog_id} 수집 시작 "
          f"(max_pages={args.max_pages}, count={args.count_per_page})", file=sys.stderr)
    posts = collect(args.blog_id, args.max_pages, args.count_per_page)
    print(f"[collector-v2] 수집 완료: {len(posts)}개", file=sys.stderr)

    if args.start_date or args.end_date:
        posts = filter_by_date(posts, args.start_date, args.end_date)
    if args.keyword:
        kws = [k.strip() for k in args.keyword.split(",") if k.strip()]
        posts = filter_by_keyword(posts, kws)
    posts = sample_posts(posts, args.sample)

    posts.sort(key=lambda x: x.get("published_at", ""), reverse=True)

    result = {
        "blog_id": args.blog_id,
        "blogger_name": "메르",
        "collected_at": datetime.now(KST).isoformat(),
        "filters": {
            "start_date": args.start_date, "end_date": args.end_date,
            "keyword": args.keyword, "sample": args.sample,
        },
        "n_posts": len(posts),
        "posts": posts,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n[collector-v2] 저장: {args.output}")
    print(f"  최종 수집: {len(posts)}개")
    if posts:
        print(f"  최근: {posts[0].get('title', '')[:60]} ({posts[0].get('published_at', '')})")
        print(f"  과거: {posts[-1].get('title', '')[:60]} ({posts[-1].get('published_at', '')})")


if __name__ == "__main__":
    main()
