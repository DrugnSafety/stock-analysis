# DART Integration Plugin

한국 금융감독원 전자공시시스템 (DART) Open API를 통해 한국 상장사의 공시·재무제표를 자동 fetch하여 분석 보고서에 통합한다.

## 🎯 무엇을 해결하는가?

**Before (curated)**:
- 종목별 공시는 hardcoded sample 3-5건
- 5년 P&L은 산업 컨센서스 추정치 (placeholder)
- 새 공시는 수동으로 추가 필요

**After (DART 통합)**:
- 한국 종목의 모든 공시 자동 fetch (1년치, 24h cache)
- 5년 P&L · BS · 자기주식 매입 · 임원 변동 등 자동 추출
- 새 공시는 cache 만료 시 자동 갱신

## 📋 5분 셋업

### 1단계 — DART 회원가입 (무료)

브라우저에서 https://opendart.fss.or.kr/uss/umt/EgovMberInsertView.do 접속 → 회원가입

### 2단계 — API 인증키 발급

로그인 후 https://opendart.fss.or.kr/mng/apiKeyManage.do → "인증키 신청" 버튼 → 신청 완료

발급된 40자리 키 복사. 일일 quota 10,000 calls (개인용으로는 무한대).

### 3단계 — .env 파일에 키 추가

`/Users/mingyukang/Documents/Claude/Projects/주식 분석/.env` 파일에 추가:

```
DART_API_KEY=여기에_40자리_키_붙여넣기
```

### 4단계 — 동작 확인

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
python3 plugins/dart-integration/scripts/dart_client.py 005490.KS
```

출력 예:
```
DART status: {"configured": true, ...}
005490.KS → corp_code: 00126380
Disclosures (1Y): 47 items
  2026-04-15 + 사업보고서 (제 56 기)
  2026-04-02 + 자기주식취득 결정
  2026-03-20 ○ 임원·주요주주특정증권등소유상황보고서
  ...
```

### 5단계 — 보고서 자동 통합 확인

DART_API_KEY 설정 후 `build_combined.py` 실행하면 자동으로:

1. 한국 종목 (.KS / .KQ) — DART 공시 timeline 자동 fetch
2. 5년 P&L — DART 사업보고서 XBRL에서 자동 파싱
3. 보고서에 "✓ DART OpenAPI 연동 활성" 표시

미국 종목 (ALB, SQM 등)은 영향 없음 — curated data 계속 사용.

## 🔧 모듈 구성

```
plugins/dart-integration/
├── plugin.json
├── README.md (이 파일)
├── scripts/
│   └── dart_client.py          ← Core API client
├── skills/
│   ├── dart-disclosure-fetch/  ← 공시 자동 fetch SKILL
│   │   └── SKILL.md
│   └── dart-financial-fetch/   ← 재무제표 자동 파싱 SKILL
│       └── SKILL.md
└── cache/                       ← (gitignored, runtime cache)
```

연동 지점:
- `report-suite/_common/news_disclosures.py` — `get_news_items()` 가 DART 자동 호출
- `report-suite/_common/financial_fetcher.py` — `fetch_financials_for_deep_research()` 가 DART 자동 호출
- `unified-builder/scripts/build_combined.py` — DART 데이터 자동 merge

## 🔍 API 활용 매핑

| DART API endpoint | 활용 |
|---|---|
| `/corpCode.xml` | ticker → corp_code 매핑 (7일 cache) |
| `/list.json` | 1년 공시 list (24h cache) |
| `/fnlttSinglAcntAll.json` | 5년 사업보고서 재무제표 (7일 cache) |
| `/document.json` | 사업보고서 원문 PDF (선택) |
| `/majorstock.json` | 최대주주·5%이상 보유주주 (선택) |

## ⚠️ 한계 및 주의사항

1. **연결 vs 별도 재무제표**: 현재 별도(OFS) 우선. POSCO홀딩스 같은 holding company는 연결(CFS)이 더 적합. 추후 ticker별 자동 선택 로직 추가 예정.
2. **계정명 매핑 차이**: 회사별로 "매출액" / "영업수익" / "수익(매출액)" 등 명칭 다름. dart_client.py의 `_extract_amount()` 다중 후보 탐색.
3. **분기보고서 (3·6·9월)**: 현재는 사업보고서(annual)만 fetch. 분기 trend 필요 시 reprt_code=11013 추가 필요.
4. **외국 상장 한국 회사**: KOSDAQ 일부 종목은 corp_code XML에 stock_code 없음 — 누락 가능.
5. **ADR 매핑**: 삼성전자 ADR (SSNLF) 같은 경우 .KS ticker 사용 권장.

## 📊 통합 후 효과 (예상)

| 메트릭 | DART 통합 전 | DART 통합 후 |
|---|---|---|
| 한국 종목 공시 정확도 | 50% (curated sample) | **99%** (실시간) |
| 5년 P&L 신뢰도 | 60% (산업 컨센서스 추정) | **95%** (사업보고서 원본) |
| 분석 깊이 | yfinance only | yfinance + DART 사업부 segment |
| Update lag | 수동 갱신 (며칠) | 자동 24h cache refresh |
| 새 공시 누락 | 흔함 | 거의 없음 |

## 🚀 다음 단계 (Phase 2-2 이후)

- [ ] 분기보고서 (reprt_code=11013) trend chart 추가
- [ ] 사업부별 segment 매출 자동 추출 (POSCO 철강/리튬/양극재 분리)
- [ ] 자기주식 매입 timeline 별도 차트
- [ ] DART 공시 push 알림 (RSS 또는 polling)
- [ ] KIND (한국거래소) 공시 통합 (reg-tech 보완)
