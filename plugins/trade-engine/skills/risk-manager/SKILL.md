---
name: risk-manager
description: ticker별 변동성·상관관계 기반 포지션 한도를 계산하는 skill. 60일 rolling stdev로 연환산 변동성 도출 후 변동성-조정 multiplier(저변동성 1.25× / 고변동성 0.50×) + 활성 포지션과의 상관관계 multiplier를 결합하여 portfolio value 대비 % 한도와 USD 한도를 동시 산출. ai-hedge-fund의 risk_manager.py 패턴.
---

# Risk Manager

## 산출

각 (ticker, as_of_date) 쌍에 대해:

```json
{
  "ticker": "005930.KS",
  "as_of_date": "2025-12-01",
  "current_price": 75200.0,
  "volatility_metrics": {
    "daily_volatility": 0.0145,
    "annualized_volatility": 0.230,
    "volatility_percentile": 65.0,
    "data_points": 60
  },
  "vol_multiplier": 0.96,
  "correlation_metrics": {
    "avg_correlation_with_active": 0.42,
    "max_correlation_with_active": 0.65,
    "active_positions": ["000660.KS"]
  },
  "corr_multiplier": 1.00,
  "base_limit_pct": 0.20,
  "combined_limit_pct": 0.192,
  "position_limit_value": 192000.0,
  "remaining_position_limit_value": 192000.0,
  "max_quantity": 2553
}
```

## 변동성 multiplier 공식 (ai-hedge-fund 재현)

```python
if annualized_volatility < 0.15:    multiplier = 1.25  # 저변동성 보너스
elif annualized_volatility < 0.30:  multiplier = 1.0 - (vol - 0.15) * 0.5
elif annualized_volatility < 0.50:  multiplier = 0.75 - (vol - 0.30) * 0.5
else:                                multiplier = 0.50  # 매우 고변동성 페널티
```

| 연환산 변동성 | Multiplier | 단일 종목 최대 한도 (base 20% 기준) |
|---|---|---|
| < 15% | 1.25 | 25.0% |
| 20% | 0.975 | 19.5% |
| 30% | 0.75 | 15.0% |
| 40% | 0.65 | 13.0% |
| 50% | 0.50 | 10.0% |
| 60%+ | 0.50 | 10.0% |

## 상관관계 multiplier

활성 포지션과의 일별 수익 평균 상관:

| avg_correlation | Multiplier | 의도 |
|---|---|---|
| ≥ 0.80 | 0.70 | 거의 동일 종목 — 큰 폭 감소 |
| 0.60-0.80 | 0.85 | 강한 상관 — 일부 감소 |
| 0.40-0.60 | 1.00 | 중립 |
| 0.20-0.40 | 1.05 | 약한 상관 — 약간 증가 |
| < 0.20 | 1.10 | 분산 — 보너스 |

## 사용

```bash
# Single ticker
python skills/risk-manager/scripts/calc_limits.py \
    --ticker 005930.KS \
    --as-of 2025-12-01 \
    --portfolio-value 1000000 \
    --output /tmp/risk_005930.json

# Batch — ledger의 모든 unique (ticker, date) 쌍
python skills/risk-manager/scripts/calc_limits.py \
    --ledger /path/to/ledger.jsonl \
    --portfolio-value 1000000 \
    --active-positions "" \
    --output /tmp/risk_limits_batch.json
```

## 옵션

| 인자 | 기본 | 설명 |
|---|---|---|
| `--base-limit` | 0.20 | 단일 종목 baseline 한도 (20%) |
| `--vol-window` | 60 | rolling stdev window (영업일) |
| `--active-positions` | "" | 콤마 구분 ticker — 상관관계 비교 대상 |
| `--currency-overlay` | none | "KRW", "USD" 중 — 외화 변동성 추가 |

## 한국 시장 특수성

- KRX 영업일 calendar (yfinance의 ^KS11 데이터로 추정)
- KRW 종목의 USD 변환은 별도 — 한도 계산은 종목 통화 기준
- Lot size 무시 (1주 단위 매매 가정)

## ai-hedge-fund 원본과의 차이

| 항목 | ai-hedge-fund | 본 skill |
|---|---|---|
| 가격 데이터 | financialdatasets.ai | yfinance |
| 활성 포지션 | LangGraph state | CLI 인자 또는 portfolio JSON |
| 출력 형식 | dict in state | JSON 파일 |
| Multi-ticker batch | one-by-one | ledger 일괄 |
