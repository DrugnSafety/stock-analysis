---
name: quant-anchor-report
description: R1 정량 anchor 보고서 (Fundamentals + 4-Analyst 평가 + Risk metrics + 데이터 태깅 요약)를 PDF로 생성한다. 페르소나 lens 적용 전 순수 정량 anchor를 체계적으로 정리. metric glossary (Forward PE·Beta·Volatility 해석 가이드) 포함. 사용자가 "R1 보고서", "정량 anchor", "quant anchor" 등을 언급하면 트리거.
---

# R1: Quant Anchor Report Builder

## 호출

```bash
python3 plugins/report-suite/skills/quant-anchor-report/scripts/build_r1.py \
  --meta meta.json --stocks stocks.json \
  --thesis thesis_list.json --eval-dir thesis_eval/ \
  --risk-limits risk_limits.json --output R1.pdf
```

## 섹션
1. Fundamentals (PE, Beta, 변동성, 1M/3M/1Y 수익률) + 비교 차트
2. 4-Analyst (Macro/Industry/Empirical/Counter) 평가 — thesis × stance heatmap
3. Risk Metrics — 변동성·vol_multiplier·position 한도
4. 데이터 태깅 요약 — [actual]/[inference]/[assumption] 분포
5. 학습용 metric glossary (Forward PE·Beta·Volatility 해석)
