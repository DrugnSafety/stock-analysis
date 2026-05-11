---
name: portfolio-manager
description: ledger의 verdict들을 종목별로 aggregate하여 (ticker, date)별 단일 trade decision(buy/sell/hold + quantity)을 산출. Risk Manager의 position 한도 내에서 결정. 페르소나별 가중치 적용 가능 (Phase C 결과 반영). LLM 미사용 — deterministic aggregation.
---

# Portfolio Manager

## 흐름

```
ledger.jsonl (verdict들)
    ↓
ticker × date 그룹화
    ↓
verdict aggregate (signal_score)
    ↓
risk_limits.json 결합
    ↓
trade_decision (action / quantity / confidence / reasoning)
```

## Verdict Aggregate — Signal Score

각 (ticker, date) 그룹에 대해:

```python
# 1. Verdict → numeric mapping
verdict_score = {
    "BUY": +1.0, "lean_bullish": +0.7,
    "HOLD": 0.0, "neutral": 0.0,
    "SELL": -1.0, "lean_bearish": -0.7,
    "UNKNOWN": 0.0,
}

# 2. 각 verdict에 confidence × persona_weight 가중
weighted_sum = Σ (verdict_score[v] × confidence × persona_weight)
total_weight = Σ (confidence × persona_weight)
signal_score = weighted_sum / total_weight  # in [-1, +1]
```

### 페르소나 가중치 (Phase C 결과 반영)

| 페르소나 | 한국 시장 가중 | 미국 시장 가중 |
|---|---|---|
| Druckenmiller | 1.5× | 1.2× |
| Lynch | 1.3× | 1.1× |
| Buffett | 0.7× | 1.2× |
| 기타 | 1.0× | 1.0× |
| thesis-first | 1.2× | 1.1× |

가중치는 `--weights-config` 옵션으로 override 가능. Phase C에서 더 많은 데이터로 calibrate되면 자동 갱신.

## Trade Decision 규칙

```python
if signal_score >= +0.7:    action, size_factor = "buy", 1.0    # 한도까지
elif signal_score >= +0.3:  action, size_factor = "buy", 0.5    # 한도의 50%
elif signal_score >= -0.3:  action, size_factor = "hold", 0
elif signal_score >= -0.7:  action, size_factor = "sell_partial", 0.5
else:                        action, size_factor = "sell_all", 1.0

target_value = position_limit_value × size_factor
target_quantity = floor(target_value / current_price)
```

현재 보유와의 차이로 실제 trade size 결정 (이미 보유 중이면 추가 매수 없음).

## 출력 스키마

```json
{
  "computed_at": "...",
  "decisions": [
    {
      "ticker": "005930.KS",
      "date": "2025-12-01",
      "n_verdicts": 4,
      "verdict_breakdown": {"HOLD": 1, "neutral": 1, "lean_bullish": 2},
      "signal_score": 0.42,
      "weighted_confidence": 0.62,
      "action": "buy",
      "size_factor": 0.5,
      "target_value": 96000,
      "target_quantity": 1280,
      "current_price": 75200,
      "position_limit_value": 192000,
      "reasoning": "신호 강도 0.42 (medium-bullish), 한도 50% 진입",
      "persona_contributions": {
        "warren-buffett": {"verdict": "neutral", "weight": 0.7, "score": 0},
        "peter-lynch": {"verdict": "lean_bullish", "weight": 1.3, "score": 0.91},
        "stanley-druckenmiller": {"verdict": "lean_bullish", "weight": 1.5, "score": 1.05},
        "thesis-first": {"verdict": "HOLD", "weight": 1.2, "score": 0}
      }
    }
  ]
}
```

## 사용

```bash
python skills/portfolio-manager/scripts/make_decisions.py \
    --ledger /path/to/ledger.jsonl \
    --risk-limits /tmp/risk_limits.json \
    --weights-config /tmp/persona_weights.json \
    --output /tmp/decisions.json
```

## ai-hedge-fund 원본과 비교

| 항목 | ai-hedge-fund | 본 skill |
|---|---|---|
| Aggregate | LLM 호출 | Deterministic (옵션 LLM) |
| Allowed actions | cash·margin 시뮬 | risk_limit + position 시뮬 |
| 출력 | LangGraph state | JSON 파일 |
| 페르소나 가중치 | 단일 가중 | 페르소나·시장별 가중 (Phase C 결과) |
