---
name: historical-blog-collector
description: 메르 블로그(blog.naver.com/ranto28)의 과거 글 메타데이터(title, url, published_at)를 일괄 수집한다. 페이징·기간 필터·sampling 지원. 본문은 lazy load (수집은 메타만, 분석 시점에 본문 fetch). 30개 글 수집에 ~10초.
---

# Historical Blog Collector

## 역할

backtest 대상이 될 메르 블로그 과거 글들의 **메타데이터만 일괄 수집**.

본문은 수집하지 않음 — backtest 실행 시 individual 글 단위로 lazy fetch.

## 사용

```bash
# 2024-01-01 ~ 2026-04-01 메타데이터 수집
python skills/historical-blog-collector/scripts/collect_meru.py \
    --start-date 2024-01-01 \
    --end-date 2026-04-01 \
    --output /tmp/meru_historical.json

# 월별 첫 글만 sampling (30개월 → 30개)
python skills/historical-blog-collector/scripts/collect_meru.py \
    --start-date 2024-01-01 \
    --sample monthly_first \
    --output /tmp/meru_monthly.json

# 키워드 필터
python skills/historical-blog-collector/scripts/collect_meru.py \
    --keyword "원유,정유,조선" \
    --output /tmp/meru_energy.json
```

## 출력 스키마

```json
{
  "blog_id": "ranto28",
  "blogger_name": "메르",
  "collected_at": "2026-04-28T...",
  "filters": {"start_date": "2024-01-01", "end_date": "2026-04-01", "sample": "monthly_first"},
  "n_posts": 30,
  "posts": [
    {
      "log_no": "224264942275",
      "url": "https://blog.naver.com/ranto28/224264942275",
      "title": "캐나다산 원유가 대안이 될 수 있을까?",
      "published_at": "2026-04-28",
      "category": "경제·투자",
      "preview": "본문 처음 200자 (옵션)"
    }
  ]
}
```

## Sampling 전략

| 옵션 | 설명 |
|---|---|
| `all` | 기간 내 모든 글 |
| `monthly_first` | 월별 첫 글 |
| `monthly_last` | 월별 마지막 글 |
| `weekly_random` | 주별 랜덤 1개 (재현성을 위해 seed) |
| `top_engaged` | 댓글·조회수 상위 N% |

`top_engaged`는 추가 정보 fetch 필요해 시간 더 소요.

## 메르 블로그 페이징 구조 (참조)

메르 블로그 list page URL 패턴:
```
https://m.blog.naver.com/PostList.naver?blogId=ranto28&from=postList&categoryNo=0&currentPage=N
```

각 page는 약 5-10개 글 표시. 30개월치 = 약 30-60 page 페이지네이션 필요. 한 번에 collect 시 ~30-60초.

## 캐싱

기간이 겹치면 기존 결과를 incremental update:

```bash
python skills/historical-blog-collector/scripts/collect_meru.py \
    --start-date 2025-01-01 \
    --update-existing /tmp/meru_historical.json
```

→ 새 글만 fetch + 기존 파일 merge.

## 주의

- 네이버 robots.txt 준수 (인용 분석 목적, 본문 재생성 금지)
- Rate limiting: 1초당 max 2 요청 (본 collector는 자동 조절)
- 메르 블로그 본문은 저작권 — 분석 결과만 보존, 본문 자체는 캐시하지 않음
