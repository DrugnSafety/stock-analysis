---
name: backtest-engine
description: verdict ledger를 입력받아 entry price·exit price·사후 수익률을 fetch하는 backtest 엔진. 단일 verdict source(thesis-first/persona/arena)뿐만 아니라 ledger 통합 처리 가능. yfinance로 주가 fetch, KOSPI(^KS11)·SPY 벤치마크 동시 처리. multi-horizon (1m/3m/6m/12m) 지원.
---

# Backtest Engine

## 역할

verdict들에 사후 수익률을 부여:
- entry_price = verdict 발행일 +1 거래일 종가
- exit_price = horizon 후 종가 (1m·3m·6m·12m 중 사용자 선택)
- benchmark_return = 같은 horizon 동안 KOSPI/SPY 수익률
- alpha = exit_return - benchmark_return

## 입력 — verdict ledger 형식

```jsonl
{"record_id":"e2d9...","date":"2026-04-28","ticker":"009540.KS","verdict":"BUY","confidence":0.71,"source":"thesis-first","persona":"","blog_url":"..."}
{"record_id":"...","date":"2026-04-28","ticker":"267250.KS","verdict":"lean_bullish","confidence":0.74,"source":"persona-panel","persona":"warren-buffett","blog_url":"..."}
```

`source` 필드:
- `thesis-first` — Thesis-First 7-Analyst pipeline
- `persona-panel` — investor-personas의 단일 페르소나 평가
- `multi-model-arena` — Claude+OpenAI+Gemini consensus
- `7-role` — naver-blog-investment의 trading-analysis

## 사용

```bash
# 모든 verdict에 대해 multi-horizon backtest
python skills/backtest-engine/scripts/run_backtest.py \
    --ledger /path/to/ledger.jsonl \
    --horizons 1m,3m,6m,12m \
    --benchmark KOSPI,SPY \
    --output /tmp/backtest_results.json

# 특정 source만
python skills/backtest-engine/scripts/run_backtest.py \
    --ledger ledger.jsonl \
    --filter-source persona-panel \
    --output /tmp/persona_backtest.json
```

## 출력 스키마

```json
{
  "ledger_path": "...",
  "ran_at": "2026-04-28T...",
  "n_verdicts": 39,
  "horizons": ["1m", "3m", "6m", "12m"],
  "verdicts": [
    {
      "record_id": "...",
      "ticker": "009540.KS",
      "verdict": "BUY",
      "confidence": 0.71,
      "source": "thesis-first",
      "persona": null,
      "verdict_date": "2026-04-28",
      "entry_price": 471000.0,
      "entry_date": "2026-04-29",
      "results": {
        "1m": {
          "exit_date": "2026-05-29",
          "exit_price": 502000.0,
          "raw_return_pct": 6.58,
          "benchmark_KOSPI_return_pct": 2.10,
          "alpha_KOSPI_pct": 4.48,
          "benchmark_SPY_return_pct": 1.50,
          "alpha_SPY_pct": 5.08,
          "data_points": 21,
          "sufficient_data": true
        },
        "3m": {...},
        "6m": {...},
        "12m": {"sufficient_data": false, "reason": "horizon not yet reached"}
      }
    }
  ]
}
```

## Hit 정의 (verdict 종류별)

| Verdict | "Hit" 기준 (1개월 horizon) |
|---|---|
| `BUY` / `lean_bullish` | raw_return ≥ +5% |
| `HOLD` / `neutral` | -3% ≤ raw_return ≤ +3% |
| `SELL` / `lean_bearish` | raw_return ≤ -5% |

threshold는 `--thresholds` 인자로 커스텀 가능. 다른 horizons는 자동 scaling (3m: ±10%, 12m: ±20% 권장).

## 데이터 결손 처리

- 미래 horizon (예: 12m이 아직 안 됨): `sufficient_data: false`로 마킹
- 종목 상장폐지: `delisted: true` 기록 후 마지막 거래일 종가로 처리
- yfinance에서 가격 못 fetch: `error` 필드 기록, hit 계산에서 제외

## ai-hedge-fund와 차이

ai-hedge-fund의 `BacktestEngine`은 **모의 거래 시뮬**(cash·position 관리). 본 엔진은 **사후 수익률 추적만** — 실제 trade decision은 별도 plugin(portfolio-manager)에서.
