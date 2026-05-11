---
name: dart-disclosure-fetch
description: 한국 상장사 ticker (예: 005490.KS)의 최근 12개월 DART 공시를 자동 fetch한다. corp_code 자동 매핑, 공시 type별 영향도 태깅 (+/-/○) 포함. DART_API_KEY env 또는 .env 파일에 설정 필요. 사용자가 "DART 공시", "전자공시", "사업보고서", "공시 조회" 등을 언급하면 트리거.
---

# DART 공시 자동 fetch

## 사용법

```python
from dart_client import fetch_disclosures, get_status

# 0. 상태 확인
print(get_status())

# 1. 1년 공시 fetch (cached 24h)
items = fetch_disclosures("005490.KS", lookback_days=365)
for item in items[:5]:
    print(f"{item['date']} {item['impact']} {item['headline']}")
```

## 출력 형식

```json
[
  {
    "date": "2026-04-15",
    "type": "공시",
    "category": "주요사항보고서",
    "headline": "POSCO홀딩스, 아르헨티나 Salar 1단계 상업생산 개시",
    "summary": "제출자: POSCO홀딩스 · 접수번호: 20260415000123",
    "source": "DART",
    "rcept_no": "20260415000123",
    "impact": "+"
  }
]
```

## 영향도 분류 룰

- **+ (긍정)**: 배당, 자기주식 매입, 신규 시설 투자, 신규 수주, 임원 선임, M&A, 합병
- **- (부정)**: 감자, 유상증자, 최대주주 변경, 사임, 감액 손실, 자본 잠식
- **○ (중립)**: 그 외 모든 공시

## API 키 발급 (5분)

1. https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do 접속 → 회원가입
2. 로그인 후 https://opendart.fss.or.kr/mng/apiKeyManage.do → "인증키 신청"
3. API 키 (40자리) 복사
4. `.env` 파일에 추가:
   ```
   DART_API_KEY=your_key_here
   ```

## 캐시

- corp_code XML: `~/.cache/dart_integration/corp_codes.xml` — 7일 TTL
- per-ticker 공시: `~/.cache/dart_integration/disclosures_{ticker}.json` — 24시간 TTL
- 일일 quota: 10,000 calls (실제로 거의 도달 불가능)

## 자동 통합

이 skill은 `report-suite/_common/news_disclosures.py`에 자동 wiring되어 있어,
한국 종목 (.KS/.KQ) 보고서 생성 시 DART_API_KEY 있으면 자동 활성.
없으면 hardcoded curated data fallback (graceful degradation).
