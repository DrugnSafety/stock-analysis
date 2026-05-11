---
name: sec-financial-fetch
description: 미국 상장사의 SEC 10-K (annual report) XBRL 데이터에서 5년 P&L (매출·영업이익·순이익·OPM·NPM)과 BS snapshot (자산·부채·자본·현금·차입금), CF summary (OCF·FCF·CapEx)를 자동 파싱한다. us-gaap concept 매핑 자동. 사용자가 "SEC 재무", "10-K 재무제표", "5년 손익 미국" 등을 언급하면 트리거.
---

# SEC EDGAR XBRL 재무제표 자동 fetch

## 사용법

```python
from sec_client import fetch_financial_5y

fin = fetch_financial_5y("BTU")
# {
#   "pl_5y": [
#     {"year": 2021, "revenue": 3318, "op_income": 432, "op_margin": 13.0, ...},
#     ...
#   ],
#   "bs_snapshot": {"total_assets": 5807, "total_liab": 2225, ...},
#   "cf_summary": {"ocf_5y_avg": 714, "fcf_5y_avg": 401, ...},
#   "source": "SEC EDGAR (10-K XBRL companyfacts)",
#   "currency": "USD (millions)"
# }
```

## API 호출

SEC `/api/xbrl/companyfacts/CIK{cik}.json` endpoint 사용:
- 한 번의 API 호출로 모든 historical XBRL facts 획득
- us-gaap concept 자동 매핑

## 추출 항목

### Income Statement (P&L)
- **Revenues** (or `RevenueFromContractWithCustomerExcludingAssessedTax`, `SalesRevenueNet`)
- **OperatingIncomeLoss**
- **NetIncomeLoss**
- → 자동 계산: OPM, NPM

### Balance Sheet
- Assets (총자산)
- Liabilities (총부채)
- StockholdersEquity (자본)
- CashAndCashEquivalentsAtCarryingValue
- LongTermDebt / LongTermDebtNoncurrent

### Cash Flow
- NetCashProvidedByUsedInOperatingActivities (OCF)
- PaymentsToAcquirePropertyPlantAndEquipment (CapEx)
- → 자동 계산: FCF = OCF - CapEx, capex intensity

## 단위

- SEC API는 USD 단위로 반환 → script가 자동으로 millions ($1M) 단위로 변환
- 표준화된 출력은 미국식 (단위: million USD)

## yfinance 대비 우위

| 항목 | yfinance | SEC EDGAR |
|---|---|---|
| 매출·OPM | ✓ | ✓ + 사업부별 segment |
| 분기 신뢰성 | 일부 누락 | 100% (의무 공시) |
| 5년 historical | 일부 4년만 | 5+ 년 완전 |
| 자기주식 매입 history | × | ✓ (Form 4 + 10-K Item 5) |
| 사업부별 매출 | × | ✓ (Item 1) |
| 위험 요소 (Item 1A) | × | ✓ Risk Factors |
| 임원 보수 | × | ✓ (DEF 14A) |
| MD&A discussion | × | ✓ Item 7 |

## 캐시

- per-ticker facts: `~/.cache/sec_edgar/facts_{ticker}.json` — 7일 TTL

## 자동 통합

`report-suite/_common/financial_fetcher.py`의 `fetch_financials_for_deep_research()`가 미국 종목에 대해 자동 호출.
