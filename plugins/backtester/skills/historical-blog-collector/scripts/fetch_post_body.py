#!/usr/bin/env python3
"""메르 블로그 단일 글 본문 fetch (모바일 페이지 활용)."""
import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup

KST = timezone(timedelta(hours=9))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) "
                  "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1",
    "Referer": "https://m.blog.naver.com/",
}


def fetch_post(blog_id: str, log_no: str) -> dict:
    """모바일 페이지에서 본문 + 메타 추출."""
    url = f"https://m.blog.naver.com/{blog_id}/{log_no}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    html = r.text

    # 제목
    title_m = re.search(r'<meta\s+property="og:title"\s+content="([^"]+)"', html)
    title = title_m.group(1) if title_m else ""

    # 본문 영역 — SE3 또는 SE2 editor
    soup = BeautifulSoup(html, "html.parser")

    # SE 메인 본문 영역들
    body_text = ""
    for sel in [
        "div.se-main-container",  # SE3
        "div#postViewArea",         # 구버전
        "div.post_ct",              # 모바일
        "div#viewTypeSelector",
    ]:
        el = soup.select_one(sel)
        if el:
            body_text = el.get_text("\n", strip=False)
            break

    # 본문 정리
    if body_text:
        # 연속된 공백 줄 압축
        body_text = re.sub(r"\n\s*\n+", "\n\n", body_text).strip()

    # 게시일
    date_str = ""
    date_el = soup.select_one(".se_publishDate, .blog_date, .pcol2.pad_t1, time")
    if date_el:
        date_str = date_el.get_text(strip=True)
    if not date_str:
        m = re.search(r'"datePublished":"([^"]+)"', html)
        if m:
            date_str = m.group(1)

    return {
        "url": f"https://blog.naver.com/{blog_id}/{log_no}",
        "blog_id": blog_id,
        "log_no": log_no,
        "title": title,
        "author": "메르(ranto28)" if blog_id == "ranto28" else blog_id,
        "published_at": date_str,
        "content_text": body_text,
        "content_length": len(body_text),
        "fetched_at": datetime.now(KST).isoformat(),
    }


def main():
    parser = argparse.ArgumentParser(description="메르 블로그 본문 fetch")
    parser.add_argument("url", help="블로그 URL 또는 logNo")
    parser.add_argument("--blog-id", default="ranto28")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    # URL에서 logNo 추출
    m = re.search(r"/(\d{12,})(?:[?#]|$)", args.url)
    if m:
        log_no = m.group(1)
        m2 = re.search(r"blog\.naver\.com/([^/]+)/", args.url)
        blog_id = m2.group(1) if m2 else args.blog_id
    elif args.url.isdigit():
        log_no = args.url
        blog_id = args.blog_id
    else:
        raise SystemExit(f"URL에서 logNo 추출 실패: {args.url}")

    print(f"[fetch] {blog_id}/{log_no}", file=sys.stderr)
    result = fetch_post(blog_id, log_no)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"  제목: {result['title'][:80]}")
    print(f"  본문: {result['content_length']}자")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
