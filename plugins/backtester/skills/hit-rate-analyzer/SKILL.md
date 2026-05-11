---
name: hit-rate-analyzer
description: backtest-engine의 결과(JSON)를 입력받아 적중률 매트릭스, 페르소나별·source별 성과, alpha vs 벤치마크, confidence calibration을 계산한다. LLM 미사용 — 순수 Python aggregation.
---

# Hit Rate Analyzer

## 산출 메트릭

### 1. Overall Hit Rate (Verdict 종류별)

```
1m horizon:
  BUY: 18 hits / 25 total (72.0%)   ← bullish 후 +5% 이상
  HOLD: 8 hits / 12 total (66.7%)   ← neutral 후 ±3% 이내
  SELL: 1 hit / 2 total (50.0%)     ← bearish 후 -5% 이하
```

### 2. Per-Source Hit Rate

각 verdict source의 적중률 비교:
```
thesis-first:    64% (18/28)
persona-panel:   67% (24/36)  ← 가장 우수
multi-model arena: 62% (16/26)
```

### 3. Per-Persona Hit Rate

13명 페르소나별 적중률:
```
Druckenmiller    72% (18/25)  conf 평균 0.78
Cathie Wood      68% (17/25)  conf 평균 0.65
Buffett          65% (15/23)  conf 평균 0.71
Lynch            61% (14/23)  conf 평균 0.68
...
```

### 4. Alpha vs Benchmarks

```
1m alpha:
  vs KOSPI: +4.2% (BUY 종목 평균)
  vs SPY:   +5.1%

3m alpha:
  vs KOSPI: +8.5%
  vs SPY:   +6.7%
```

### 5. Confidence Calibration

```
Bucket    실제 적중률   완벽 calibration
80%+      75%           예상 80%+         ← slight overconfidence
60-80%    62%           예상 60-80%       ← well calibrated
40-60%    51%           예상 40-60%       ← well calibrated
<40%      38%           예상 <40%
```

→ Brier score, ECE (Expected Calibration Error) 동시 산출.

### 6. Time-to-Hit (BUY only)

```
BUY 종목들의 +5% 도달 평균 일수:
  N일 내 hit 비율
  1주 내: 35%
  2주 내: 52%
  1개월 내: 72%
  3개월 내: 81%
  결과 hit 못함: 19%
```

## 사용

```bash
python skills/hit-rate-analyzer/scripts/analyze.py \
    /tmp/backtest_results.json \
    --output /tmp/hit_rate_summary.json

# 특정 horizon만
python skills/hit-rate-analyzer/scripts/analyze.py \
    /tmp/backtest_results.json \
    --horizon 3m \
    --output /tmp/3m_summary.json

# 임계값 커스텀
python skills/hit-rate-analyzer/scripts/analyze.py \
    /tmp/backtest_results.json \
    --buy-threshold 7.0 \
    --hold-band 4.0 \
    --sell-threshold -7.0
```

## 출력 스키마

```json
{
  "ran_at": "...",
  "n_verdicts_total": 39,
  "n_verdicts_with_data": 28,
  "thresholds": {"buy": 5.0, "hold_band": 3.0, "sell": -5.0},
  "horizons": {
    "1m": {
      "overall": {"BUY_hit": 18, "BUY_total": 25, "BUY_rate": 0.72, ...},
      "by_source": {"persona-panel": {...}, "thesis-first": {...}},
      "by_persona": {"warren-buffett": {...}, "cathie-wood": {...}},
      "alpha": {"vs_KOSPI_avg_pct": 4.2, "vs_SPY_avg_pct": 5.1},
      "calibration": {
        "buckets": [
          {"range": "80-100", "n": 12, "predicted": 0.85, "actual": 0.75},
          {"range": "60-80", "n": 18, "predicted": 0.70, "actual": 0.62}
        ],
        "ece": 0.08,
        "brier_score": 0.21
      }
    }
  }
}
```

## 권장 사용 흐름

1. backtest-engine으로 결과 생성
2. hit-rate-analyzer로 종합 메트릭 계산
3. backtest-report로 PDF 시각화
4. 4단계 후 다음 분석에 어느 페르소나·source 우선 사용할지 결정 (positive feedback loop)
