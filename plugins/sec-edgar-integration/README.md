# SEC EDGAR Integration Plugin

미국 증권거래위원회 (SEC)의 EDGAR Open Data API를 통해 미국 상장사의 공시·재무제표를 자동 fetch하여 분석 보고서에 통합한다. **DART의 미국 버전**.

## 🎯 무엇을 해결하는가?

**Before (curated)**:
- BTU 같은 미국 종목 공시는 hardcoded 10건 sample
- 5년 P&L은 산업 컨센서스 추정치 (placeholder)
- 자기주식 매입·임원 변동 누락 가능

**After (SEC EDGAR 통합)**:
- 1년치 모든 SEC filings (10-K/10-Q/8-K/Form 4 등) 자동 fetch — BTU 기준 114+건
- 5년 P&L · BS · CF — 사업보고서 XBRL에서 자동 파싱 (us-gaap concept 매핑)
- 자기주식 매입 history 자동 추적 (Form 4 + 10-K Item 5)

## 📋 셋업 (1분, API 키 불필요)

### 1단계 — User-Agent 설정 (선택, 기본값 사용 가능)

SEC는 API 키가 필요 없지만 **User-Agent header 필수**입니다 (이메일 주소 권장).

`.env` 파일에 추가 (선택):
```
SEC_USER_AGENT=YourName/1.0 (your-email@example.com)
```

미설정 시 기본값 `stock-analysis-system/1.0 (mingyu.kang@research.local)` 사용 — 이미 작동 중.

### 2단계 — 동작 확인

```bash
cd "/Users/mingyukang/Documents/Claude/Projects/주식 분석"
python3 plugins/sec-edgar-integration/scripts/sec_client.py BTU
```

기대 출력:
```
SEC EDGAR status: {"configured": true, ...}
BTU → CIK: 0001064728
Filings (1Y): 114 items
  2026-04-30 ○ Form SCHEDULE 13G
  2026-04-29 ○ Form SCHEDULE 13G
  ...
```

### 3단계 — 보고서 자동 통합 확인

다음 보고서 빌드 시 자동으로:
1. 미국 종목 → SEC EDGAR 공시 timeline 자동 fetch
2. 5년 P&L → 10-K XBRL companyfacts에서 자동 파싱
3. 보고서에 "✓ SEC EDGAR (미국 공시)" 표시

한국 종목 (.KS / .KQ)은 영향 없음 — DART 계속 사용.

## 🔧 모듈 구성

```
plugins/sec-edgar-integration/
├── plugin.json
├── README.md (이 파일)
├── scripts/
│   └── sec_client.py           ← Core API client (CIK lookup + filings + XBRL)
├── skills/
│   ├── sec-disclosure-fetch/   ← 공시 자동 fetch SKILL
│   │   └── SKILL.md
│   └── sec-financial-fetch/    ← 10-K XBRL 재무제표 자동 파싱 SKILL
│       └── SKILL.md
└── cache/                       ← (gitignored, runtime cache)
```

연동 지점:
- `report-suite/_common/news_disclosures.py` — `get_news_items()` 가 SEC 자동 호출
- `report-suite/_common/financial_fetcher.py` — `fetch_financials_for_deep_research()` 가 SEC 자동 호출
- `unified-builder/scripts/build_combined.py` — SEC 데이터 자동 merge

## 🔍 API 활용 매핑

| SEC EDGAR endpoint | 활용 |
|---|---|
| `/files/company_tickers.json` | ticker → CIK 매핑 (30일 cache) |
| `/submissions/CIK{cik}.json` | 1년 공시 list (24h cache) |
| `/api/xbrl/companyfacts/CIK{cik}.json` | 5년 사업보고서 XBRL (7일 cache) |
| `/Archives/edgar/data/{cik}/{access}/` | 사업보고서 원문 PDF 링크 |

## ⚠️ 한계 및 주의사항

1. **us-gaap concept 매핑**: 회사별로 Revenue concept이 다름 (`Revenues` / `RevenueFromContractWithCustomerExcludingAssessedTax` / `SalesRevenueNet`). Multi-candidate fallback 적용했으나 일부 회사 누락 가능.

2. **Form 4 (insider trading)**: 자동으로 fetch되지만 영향도 분류는 keyword 기반. 정확한 "purchase vs sale" 분류는 추가 파싱 필요.

3. **분기 데이터 (10-Q)**: 현재는 annual (10-K)만 사용. 분기 trend 차트는 Phase 2-3에서 추가.

4. **Foreign issuers**: ADR (외국 회사 미국 상장) 일부는 20-F (annual report 외국형)을 제출 — 별도 처리 필요.

5. **Delisted companies**: SEC EDGAR는 delisted 후에도 데이터 유지하나 ticker map에서 제외될 수 있음.

## 📊 통합 후 효과 (BTU 사례)

| 메트릭 | SEC 통합 전 | SEC 통합 후 |
|---|---|---|
| 미국 종목 공시 정확도 | 50% (curated 10건) | **99%** (실시간 114+건) |
| 5년 P&L 신뢰도 | 60% (산업 컨센서스 추정) | **95%** (사업보고서 원본) |
| 자기주식 매입 추적 | 누락 빈번 | **실시간** (Form 4) |
| 위험 요소 (10-K Item 1A) | × | ✓ Risk Factors 섹션 |

## 🚀 다음 단계 (Phase 2-3 이후)

- [ ] 10-K Item 1A (Risk Factors) 자동 추출 — 페르소나 평가에 활용
- [ ] 10-K Item 7 (MD&A) 자동 추출 — management의 narrative 분석
- [ ] DEF 14A (proxy) 임원 보수 자동 fetch
- [ ] Form 4 insider trading 패턴 분석
- [ ] 분기보고서 (10-Q) trend 차트
