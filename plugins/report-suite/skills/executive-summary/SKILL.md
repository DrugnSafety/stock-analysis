---
name: executive-summary
description: R3 의사결정 시트 (1-page Decision Sheet + Verdict 해석 가이드 + 핵심 위험 5개 + 모니터링 포인트)를 PDF로 생성한다. 한 페이지로 종목·액션·수량·금액·신호를 한눈에. 사용자가 "R3 보고서", "executive summary", "의사결정 시트" 등을 언급하면 트리거.
---

# R3: Executive Summary Builder

## 호출

```bash
python3 plugins/report-suite/skills/executive-summary/scripts/build_r3.py \
  --thesis thesis_list.json --eval-dir thesis_eval/ \
  --decisions decisions.json --portfolio portfolio.json \
  --persona-aggregates persona_aggregates.json --output R3.pdf
```

## 섹션
1. Cover — 1-page Decision Sheet (종목·액션·수량·금액·신호)
2. Verdict·Confidence 해석 가이드 (lean_bullish/neutral/lean_bearish 의미)
3. 메르의 핵심 주장 (요약)
4. 정량 검증 결과 — 사실 vs 가정
5. Persona Panel 합의도 (종목별)
6. 핵심 위험 5개 — 가장 먼저 무너질 가정
7. 모니터링 포인트 (verdict 뒤집을 신호)
8. 의사결정 가이드 (보고서 활용 방법)
