---
name: backtest-report
description: Backtest 결과 (verdict 적중률, alpha, calibration, drawdown)를 PDF 보고서로 시각화한다. 히스토그램, 산포도, 시계열 차트 자동 생성. 사용자가 "백테스트 보고서", "적중률 PDF", "alpha 시각화" 등을 언급하면 트리거.
---

# Backtest 결과 시각화 PDF 생성

`scripts/build_report.py` — backtest_real/ledger.jsonl을 입력으로 받아 PDF 생성.

## 출력 섹션
1. 전체 적중률 (BUY/HOLD/SELL 별)
2. Time horizon별 분석 (1m/3m/6m/1y)
3. KOSPI/SPY benchmark 대비 alpha
4. 페르소나별 적중률 (calibration)
5. Drawdown 분포

## 호출

```bash
python3 plugins/backtester/skills/backtest-report/scripts/build_report.py \
  --ledger .analysis-log/backtest_real/ledger.jsonl \
  --output reports/backtest_summary.pdf
```
