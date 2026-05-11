---
name: dart-financial-fetch
description: 한국 상장사의 DART 사업보고서에서 5년 P&L (매출·영업이익·순이익·OPM·NPM)과 BS snapshot (자산·부채·자본·현금·차입금)을 자동 파싱한다. fnlttSinglAcntAll API 활용. yfinance 대비 한국 GAAP 정확성과 사업부별 segment 데이터 우수. DART_API_KEY 필요. 사용자가 "DART 재무", "5년 손익", "사업보고서 재무제표" 등을 언급하면 트리거.
---

# DART 재무제표 자동 fetch

## 사용법

```python
from dart_client import fetch_financial_5y

fin = fetch_financial_5y("005490.KS")
# {
#   "pl_5y": [
#     {"year": 2021, "revenue": 76332, "op_income": 9215, "op_margin": 12.1, ...},
#     ...
#   ],
#   "bs_snapshot": {"total_assets": 92000, "total_liab": 38000, ...},
#   "source": "DART (사업보고서 XBRL)"
# }
```

## API 호출

DART `fnlttSinglAcntAll.json` endpoint를 사용:
- 사업보고서 (reprt_code=11011, annual)
- 별도 (fs_div=OFS) 또는 연결 (fs_div=CFS)
- 매년 1회 호출 → 5년치는 5 calls

## 추출 항목

### Income Statement (P&L)
- 매출액 / 수익(매출액) / 영업수익
- 영업이익 / 영업이익(손실)
- 당기순이익 / 당기순이익(손실)
- → 자동 계산: OPM, NPM

### Balance Sheet
- 자산총계 / 부채총계 / 자본총계
- 현금및현금성자산
- 장기차입금 / 사채

## 단위

- DART API는 원 단위로 반환 → script가 자동으로 십억 (1e9) 단위로 변환
- 표준화된 출력은 한국식 (단위: 십억 KRW)

## yfinance 대비 우위

| 항목 | yfinance | DART |
|---|---|---|
| 매출·OPM | ✓ | ✓ + 사업부별 segment |
| 분기 신뢰성 | 일부 누락 | 100% (의무 공시) |
| 한국 GAAP 정확성 | 환산 시 오류 | 원본 |
| 자기주식 매입 | × | ✓ 실시간 |
| 사업부별 매출 | × | ✓ |
| 우발채무·약정 | × | ✓ |

## 자동 통합

`report-suite/_common/deep_research.py`의 financials placeholder가 DART 데이터로 자동 대체됩니다 (DART_API_KEY 활성 시).
