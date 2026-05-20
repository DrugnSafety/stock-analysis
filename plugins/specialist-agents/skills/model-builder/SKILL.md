---
name: specialist-agents:model-builder
description: >
  Sales-side 스타일 financial model을 filings + 분석가 input으로부터 구축.
  Anthropic Model Builder Agent 템플릿(2026-05) + LangAlpha L/S Hedge Fund analyst 패턴.

  트리거: "재무모델 생성", "DCF 모델", "Reverse DCF", "Model Builder", "consensus model".
version: 0.1.0
based_on: Anthropic Financial Services Agents 2026-05 + LangAlpha
---

# Model Builder — Filings → DCF/Reverse-DCF/Scenario Model

## 목적
사용자 수동 valuation 모델링 대체. yfinance/DART/SEC live 데이터 + 페르소나 가정 input → DCF / Reverse-DCF / Bull-Base-Bear scenario 자동 생성.

## 입력
- ticker, current_price, sector
- (자동) 5Y P&L (yfinance/DART/SEC)
- (자동) 5Y BS·CF (yfinance/DART/SEC)
- (자동) peer multiples
- (option) 사용자 가정 (성장률·할인율·terminal multiple 등)

## 출력 `models/{ticker}_dcf.json`
```json
{
  "ticker": "010140.KS",
  "as_of": "2026-05-20",
  "current_price": 28550,
  "currency": "KRW",

  "dcf_baseline": {
    "method": "10Y FCFF + Terminal (Gordon Growth)",
    "assumptions": {
      "rev_cagr_5y": 0.08, "rev_cagr_5_10y": 0.04,
      "ebit_margin_terminal": 0.075,
      "wacc": 0.085, "terminal_growth": 0.025
    },
    "implied_share_price": 35200,
    "upside_pct": 23.3,
    "sensitivity": {
      "+1% WACC": -8.5, "-1% WACC": +10.2,
      "+1pp margin": +14.0, "-1pp margin": -13.5
    }
  },

  "reverse_dcf": {
    "embedded_assumption": "현재가 ₩28,550은 5Y rev CAGR 5.5% + EBIT margin 6.0% + WACC 8.5% gartar",
    "implied_growth_vs_consensus": "+0.5pp (페어 대비 0.5pp 낮음 — 시장 약간 보수적)"
  },

  "scenarios": {
    "bull": {"prob": 0.30, "target": 42000, "thesis": "FDC 본수주 + LNG cycle peak"},
    "base": {"prob": 0.50, "target": 35200, "thesis": "DCF baseline 충족"},
    "bear": {"prob": 0.20, "target": 22000, "thesis": "조선 cycle 정점 후 둔화"}
  },
  "expected_value": 33260,
  "expected_upside_pct": 16.5,

  "peer_multiple_check": {
    "current_ev_ebitda": 22.2, "peer_avg": 18.4,
    "current_fwd_pe": 16.3, "peer_avg": 19.5,
    "narrative": "EV/EBITDA premium (cycle peak); fwd PE 할인 (cyclical fear) — mixed signal"
  }
}
```

## 페르소나 통합
- **Damodaran (narrative valuation)**: DCF baseline + reverse-DCF + story-coherence check
- **Buffett/Munger (value)**: peer multiple + ROIC compounding check
- **Graham (deep value)**: NCAV/book value safety cushion
- **Druckenmiller (macro)**: cycle peak vs trough sensitivity

## LangAlpha L/S 통합
- Long candidate: Expected upside > +15%
- Short candidate: Expected upside < -10%
- Pair trade: Long FSLR / Short JinkoSolar (영업이익률 격차 30% vs 8%)
