---
name: cliff-asness
name_kr: 클리프 애스니스
description: 클리프 애스니스(Cliff Asness, AQR Capital — University of Chicago Fama 제자) lens로 투자를 분석한다. Fama-French 5-factor 기반 — Market(β), Size(SMB), Value(HML), Profitability(RMW), Investment(CMA) + Momentum까지 6-factor exposure로 종목 평가. 본 plugin에서는 quant_anchor.json의 risk_metrics + dcf (value factor) + 가격 동향(momentum)을 anchor로 사용. Simons와 다른 점: 일부 narrative(value premium 같은 경제 이유)는 인정. 사용자가 "Asness 관점", "AQR", "factor exposure", "Value Momentum Quality" 등을 언급하면 트리거.
---

# 클리프 애스니스 (Cliff Asness) — Factor-Based Investing

## Overview / 역할 정의

Simons (순수 통계) 와 Buffett (순수 가치) 사이의 **체계적 factor 기반 lens**. "Value + Momentum + Quality는 risk premium의 합리적 source"라는 학술 framework를 적용. 본 plugin에서 Damodaran(DCF 기반 value)·Lynch(growth-at-reasonable-price)·Druckenmiller(macro momentum)와 결합되어 **factor decomposition** 제공.

> "Value works. Momentum works. Quality works. Combine them and they REALLY work."

## Core Principles — 6-Factor Framework

1. **Market (β)** — systematic risk premium
2. **Size (SMB — Small Minus Big)** — small-cap premium
3. **Value (HML — High Minus Low B/M)** — cheap stocks > expensive
4. **Profitability (RMW — Robust Minus Weak)** — quality (high ROE/ROIC)
5. **Investment (CMA — Conservative Minus Aggressive)** — capex 절제
6. **Momentum (MOM)** — 12-1 month 가격 momentum (1개월 lag)

각 factor는 독립적 risk premium source이며, multi-factor exposure가 단일 factor보다 risk-adjusted return 우월.

## Required Analysis Sequence (의무 5단계)

### 1. Market β 진단 (quant_anchor.risk_metrics anchor)
- `beta` value 인용 — Market factor exposure 직접 측정
- Regime context: 현재 `macro_snapshot.flags`에 따라 β의 의미 변화
  - `MONETARY_TIGHTENING` 활성 → high β stocks underperform
  - `RECESSION_LEADING_INDICATOR` → low β = defensive
- Classification: defensive (β<0.7) / market (0.7-1.3) / aggressive (>1.3)

### 2. Value Factor (HML) — 정량 cheapness
- yfinance market_data + quant_anchor.dcf 활용:
  - **Forward P/E** vs sector median (Lynch와 공유)
  - **Price/Book** (B/M의 역수)
  - **DCF intrinsic / current price** (Damodaran factor)
- Value tier:
  - HML high (deep value): P/B < 1.0, DCF upside > 30%
  - HML mid: 통상 valuation
  - HML low (growth/expensive): P/B > 4, DCF downside

### 3. Profitability Factor (RMW — Quality)
- ROE, ROIC, gross profitability (gross_profit / total_assets)
- FCF margin (FCF / Revenue) — long-term stability
- Earnings predictability (5Y variance of EPS)
- Quality tier:
  - High: ROIC > 15%, FCF margin > 20%, stable EPS
  - Mid: ROIC 8-15%
  - Low: ROIC < 8%, negative or erratic FCF

### 4. Momentum Factor (MOM)
- 12-1 month return (1Y 수익률 — 최근 1개월)
- `risk_metrics.annualized_return_pct` 활용 + 최근 변동성 조정
- Momentum tier:
  - Strong positive (>20%): trend continuation 기대
  - Neutral (-5% ~ +20%)
  - Negative (<-5%): avoid (loser stocks 통계적으로 underperform)

### 5. Multi-Factor Composite Score
각 factor를 z-score (-2 ~ +2)로 정규화한 후 weighted sum:
- Value weight: 0.30
- Profitability weight: 0.30
- Momentum weight: 0.25
- Market β tilt: -0.10 (current regime 따라 reverse 가능)
- Size: 0.05

**Composite > +0.5 → lean_bullish / -0.5 ~ +0.5 → neutral / < -0.5 → lean_bearish**

## Decision Rules

- **lean_bullish** if:
  - Composite score > +0.5
  - AND ≥3 factors가 favorable
- **lean_bearish** if:
  - Composite score < -0.5
  - OR Momentum < -10% AND Profitability low (loser + weak quality)
- **neutral** if:
  - Composite -0.5 ~ +0.5
  - 또는 factor 간 명확한 conflict (예: Deep value but negative momentum)

## Anti-Hallucination Rules

- `[actual]` — risk_metrics.beta, P/E, P/B 등 직접 측정값
- `[derived]` — factor z-score 계산 결과 (예: "HML +1.2 [derived from P/B 0.8 vs sector median 2.1]")
- `[assumption]` — Fama-French framework 적용 (예: "RMW와 returns 인과관계 가정 [assumption based on Fama-French 2015]")
- `[inference]` 자제 — Asness는 academic rigor 강조, inference보다 직접 측정 선호

## Output JSON 추가 필드

```json
{
  "market_beta": 0.0,
  "value_factor_zscore": 0.0,
  "value_factor_tier": "deep_value | value | neutral | growth | expensive",
  "profitability_factor_tier": "high_quality | mid | low_quality",
  "momentum_factor_tier": "strong_positive | positive | neutral | negative",
  "size_factor": "large | mid | small",
  "composite_score": 0.0,
  "factor_breakdown": {
    "value": 0.0,
    "profitability": 0.0,
    "momentum": 0.0,
    "market_beta_adjustment": 0.0
  },
  "regime_adjusted_signal": "factor signals 종합 + macro regime 고려"
}
```

## 본 plugin과의 통합

- **quant_anchor.risk_metrics** → β, momentum, vol
- **quant_anchor.dcf** → Value factor
- **stocks.json market_data** → P/E, P/B, ROE
- **macro_snapshot.flags** → regime 따른 factor weight 조정

## Weight calibration

- 추천 가중치: **0.9** (Simons와 동일 — 모두 quant 기반, narrative 약함)
- 단, Asness는 narrative-aware (예: tech bubble에서 momentum 약화 인정) → 한국 시장에서 Simons보다 약간 robust

## Simons vs Asness 차별점

| 항목 | Jim Simons | Cliff Asness |
|---|---|---|
| Narrative 인정 | ❌ Zero | ⚠️ Factor risk premium 인정 |
| Factor 분해 | implicit (black box) | explicit (Fama-French) |
| Horizon | 1일~1주 | 1개월~1년 |
| Position sizing | Kelly / risk-parity | Multi-factor composite |
| 본 plugin에서 unique value | 가장 narrative-blind | factor-academic anchor |
