---
name: persona-panel
description: 단일 종목에 대해 13명 페르소나(또는 부분 선택) 전체 평가를 병렬 실행하고 결과를 매트릭스로 종합하는 skill. verdict 분포, style-split(가치파 vs 성장파), universal concern, unique alpha 자동 식별. PDF 리포트 생성. 사용자가 "13명 페르소나 평가", "persona panel", "투자자들의 의견", "원형 테이블 분석" 등을 언급하면 트리거.
---

# Persona Panel

## 역할

단일 ticker × N persona 병렬 평가:
- 기본: 13명 전부
- 부분 선택: `--include warren-buffett,peter-lynch,cathie-wood`
- 결과 종합: verdict 분포·style-split·universal concern·unique alpha

## 사용

```bash
# 13명 전체 패널 (Cowork bash sandbox에서는 --background 필요할 수 있음)
python skills/persona-panel/scripts/run_panel.py 267250.KS \
    --market /tmp/market_267250_KS.json \
    --post /tmp/post.json \
    --output-dir /tmp/panel_267250

# 부분 선택
python skills/persona-panel/scripts/run_panel.py 267250.KS \
    --market /tmp/market_267250_KS.json \
    --include warren-buffett,charlie-munger,peter-lynch,cathie-wood

# 종합
python skills/persona-panel/scripts/aggregate_panel.py \
    /tmp/panel_267250 \
    --output /tmp/panel_267250/aggregate.json

# 시각화 PDF
python skills/persona-panel/scripts/build_panel_pdf.py \
    /tmp/panel_267250/aggregate.json \
    --output /tmp/panel_267250/report.pdf
```

## Aggregation 로직

### 1. Verdict 분포

```
verdict 분포 (13명 기준):
  lean_bullish: 8 (61.5%)
  neutral: 4 (30.7%)
  lean_bearish: 1 (7.7%)
```

### 2. Style-Split 분석

페르소나를 4 category로 분류:
- **Value (보수적)**: Buffett, Munger, Graham, Pabrai, Burry
- **Growth (공격적)**: Cathie Wood, Peter Lynch, Phil Fisher, Druckenmiller
- **Activist/Catalyst**: Bill Ackman, Burry
- **Risk-aware/Quant**: Taleb, Damodaran, Jhunjhunwala

각 category 내 verdict 일치율 + category간 split 보고:
- "Value 5명 중 3명 bullish, Growth 4명 중 4명 bullish" → 합의 광범위
- "Value 5명 모두 bearish, Growth 4명 모두 bullish" → style-driven split

### 3. Universal Concern

모든 또는 거의 모든 페르소나가 짚는 공통 우려:
- key_concerns 필드를 cross-persona로 집계
- 빈도 ≥ 70% 우려 항목 추출

### 4. Unique Alpha

1-2 페르소나만 보는 기회/위험:
- 단일 페르소나의 unique key_opportunity 또는 key_concern
- "놓치기 쉬운 인사이트"로 강조

## PDF 리포트 구조

1. Cover: ticker + 13명 verdict 분포 차트
2. Persona-by-persona 표 (verdict, confidence, horizon, 1줄 코멘트)
3. Style-split 분석
4. Universal concerns
5. Unique alpha
6. 페르소나별 detail (5단계 결과)
7. Cost·시간 메타

## 비용

13명 × $0.05-0.20/persona = **$0.65-2.60/panel** (gpt-5.5 + reasoning=high 기준)

`--quick` 옵션 사용 시 reasoning_effort=medium + 4-stage 단축으로 ~$0.30-0.60/panel.
