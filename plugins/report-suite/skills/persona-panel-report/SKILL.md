---
name: persona-panel-report
description: R2 13명 페르소나 패널 보고서 (Buffett·Munger·Lynch·Wood·Burry·Taleb·Graham·Ackman·Pabrai·Fisher·Jhunjhunwala·Druckenmiller·Damodaran)를 PDF로 생성한다. 각 페르소나의 철학·5단계 framework·verdict + key concerns/opportunities + narrative vs quant resolution 포함. 사용자가 "R2 보고서", "13명 페르소나", "persona panel" 등을 언급하면 트리거.
---

# R2: Persona Panel Report Builder

## 호출

```bash
python3 plugins/report-suite/skills/persona-panel-report/scripts/build_r2.py \
  --aggregate persona_panel/{ticker}/aggregate.json \
  --full-results persona_panel/{ticker}/ \
  --thesis thesis_list.json --meta meta.json --output R2.pdf
```

## 섹션
1. Cover — verdict 분포 (매수/중립/매도) + 평균 신뢰도
2. 13 페르소나 종합 표
3. Style Split (value/growth/macro/contrarian)
4. Thesis × Persona Stance Matrix (heatmap)
5. Universal Concerns (다수 공통 우려)
6. 페르소나별 상세 — 철학 + 5단계 + reasoning + narrative vs quant
