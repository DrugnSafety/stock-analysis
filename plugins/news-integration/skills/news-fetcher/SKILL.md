---
name: news-fetcher
description: 미국 종목의 최근 1년 뉴스를 NewsAPI + Finnhub에서 자동 fetch한다. ticker + company_name으로 조회, 영향도 자동 분류 (+/-/○), 중복 제거. API 키 없으면 빈 결과 반환 (caller가 curated fallback). 사용자가 "뉴스 fetch", "news search", "company news" 등을 언급하면 트리거.
---

# 뉴스 자동 fetch (NewsAPI + Finnhub)

## 사용법

```python
from news_client import fetch_news, get_status

# 1. 상태 확인
print(get_status())
# {"newsapi_configured": True, "finnhub_configured": True, "any_active": True}

# 2. 1년 뉴스 fetch
items = fetch_news("BTU", company_name="Peabody Energy", lookback_days=365)
for it in items[:10]:
    print(f"{it['date']} {it['impact']} {it['headline']}")
```

## API 키 발급 (둘 다 무료)

### NewsAPI (https://newsapi.org)
1. https://newsapi.org/register — 회원가입 (이메일만)
2. Dashboard에서 API 키 복사
3. **Free tier**: 100 calls/day, 30일 lookback, en/ko 등 다국어

### Finnhub (https://finnhub.io)
1. https://finnhub.io/register — 회원가입
2. Dashboard → API Keys 복사
3. **Free tier**: 60 calls/min, 365일 lookback, 회사별 정확한 매핑

### .env 추가
```
NEWSAPI_KEY=...
FINNHUB_KEY=...
```

## 영향도 분류 룰

키워드 기반 (Phase 2에서 LLM 분류로 업그레이드 예정):

- **+ (긍정)**: BEAT, EXCEED, RAISE, ACQUIRE, BUYBACK, GROWTH, UPGRADE, AWARD, APPROVAL
- **- (부정)**: MISS, DOWNGRADE, LAWSUIT, BANKRUPTCY, RESIGN, RECALL, INVESTIGATION, LAYOFF
- **○ (중립)**: 그 외

## 중복 제거

같은 뉴스가 NewsAPI + Finnhub에 모두 있을 수 있음 → headline 첫 80자로 중복 제거.

## 캐시

per-ticker: `~/.cache/news_integration/news_{ticker}.json` — 24시간 TTL

## Graceful Fallback

API 키 미설정 시:
- `fetch_news()` → 빈 list 반환 (no error)
- caller (e.g. `news_disclosures.py`)가 curated fallback 사용

## 자동 통합

`report-suite/_common/news_disclosures.py`에 wired — 미국 종목 보고서 생성 시 자동 호출.
