---
name: sec-disclosure-fetch
description: 미국 상장사 ticker (예: BTU, NVDA, AAPL)의 최근 12개월 SEC EDGAR 공시 (10-K/10-Q/8-K/Form 4)를 자동 fetch한다. CIK 자동 매핑, 공시 type별 영향도 태깅 (+/-/○) 포함. API 키 불필요. 사용자가 "SEC 공시", "EDGAR filings", "10-K", "8-K" 등을 언급하면 트리거.
---

# SEC EDGAR 공시 자동 fetch

## 사용법

```python
from sec_client import fetch_disclosures, get_cik, get_status

# 1. 상태 확인
print(get_status())

# 2. ticker → CIK
cik = get_cik("BTU")  # → "0001064728"

# 3. 1년 공시 fetch (cached 24h)
items = fetch_disclosures("BTU", lookback_days=365)
for item in items[:5]:
    print(f"{item['date']} {item['impact']} {item['headline']}")
```

## 출력 형식

```json
[
  {
    "date": "2026-04-22",
    "type": "공시",
    "category": "10-Q",
    "headline": "분기보고서 (Quarterly Report)",
    "summary": "Form 10-Q · 접수번호: 0001064728-26-000045",
    "source": "SEC EDGAR",
    "rcept_no": "0001064728-26-000045",
    "url": "https://www.sec.gov/Archives/edgar/data/1064728/...",
    "impact": "○"
  }
]
```

## 영향도 분류 룰

- **+ (긍정)**: Buyback, Repurchase, Dividend Increase, Acquisition, Merger, Earnings Beat, Insider Purchase
- **- (부정)**: Default, Bankruptcy, Resignation, Going Concern, Material Weakness, Earnings Miss, Insider Sale
- **○ (중립)**: 10-K, 10-Q (기본 의무 공시 — 자체는 neutral)

## API 키 — 불필요

SEC EDGAR는 API 키가 필요 없습니다. 단, **User-Agent header**는 필수입니다:

```bash
# .env 파일에 (선택 — 기본값 사용 가능)
SEC_USER_AGENT=YourName/1.0 (your-email@example.com)
```

기본값은 `stock-analysis-system/1.0 (mingyu.kang@research.local)` — 이미 ASCII 안전.

## 캐시

- ticker→CIK map: `~/.cache/sec_edgar/ticker_cik_map.json` — 30일 TTL
- per-ticker filings: `~/.cache/sec_edgar/filings_{ticker}.json` — 24시간 TTL

## Rate Limit

10 req/sec. 일반 사용에서 도달 불가능.

## 자동 통합

`report-suite/_common/news_disclosures.py`에 wired — 미국 종목 보고서 생성 시 SEC EDGAR 자동 fetch.
