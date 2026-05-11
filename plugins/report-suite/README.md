# Report Suite Plugin

블로거 글 1편 + 분석 시스템 결과를 입력받아 **3종 PDF 보고서**를 자동 생성:

| 보고서 | 페이지 | 대상 독자 | 핵심 내용 |
|---|---|---|---|
| **R1. Quant Anchor Report** | 10-15p | 정량 분석가 | Fundamentals + Technical + 거시 + 4-Analyst + Risk metrics |
| **R2. Persona Panel Report** | 15-20p | 투자 철학 비교 독자 | 13명 페르소나 5단계 + thesis × persona matrix + style-split |
| **R3. Executive Summary** | 5-8p | 의사결정자 | 메르 thesis + 정량 검증 + persona 합의 + trade decision + 한 페이지 결정 시트 |

3개 보고서가 **같은 데이터·결과**에서 다른 lens로 빌드됨. 사용자는 시간이 있으면 R1·R2·R3 모두 읽고, 시간이 없으면 R3만 봐도 결정 가능.

## Plugin 구조

```
plugins/report-suite/
├── plugin.json
├── README.md
├── skills/
│   ├── quant-anchor-report/      ← R1 builder
│   ├── persona-panel-report/     ← R2 builder
│   ├── executive-summary/         ← R3 builder
│   └── unified-builder/          ← 한 명령으로 3종 동시 생성
└── commands/
    └── report-suite.md
```

## 사용

```bash
# 한 번에 3개 보고서 모두 생성
python plugins/report-suite/skills/unified-builder/scripts/build_all.py \
    --thesis /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --persona-panel-dir /tmp/persona_panel \
    --risk-limits /tmp/risk_limits.json \
    --decisions /tmp/decisions.json \
    --portfolio /tmp/portfolio_history.json \
    --output-dir /tmp/reports

# → /tmp/reports/R1_quant.pdf, R2_personas.pdf, R3_executive.pdf
```

## 보고서 디자인 원칙

### R1. Quant Anchor Report
- **목적**: "데이터가 뭐라고 하는가?"
- **구조**:
  1. Cover (종목·날짜·핵심 메트릭 KPI)
  2. Fundamentals 섹션 (PE·PBR·ROE·FCF·부채)
  3. Technical 섹션 (이평·RSI·변동성·모멘텀)
  4. 거시 섹션 (KOSPI/SPY 동조성·환율·금리)
  5. 4-Analyst 평가 (Macro/Industry/Empirical/Counter — thesis별)
  6. Risk metrics (변동성-조정 한도·상관관계)
  7. 데이터 태깅 요약 (`[actual]` vs `[inference]` vs `[assumption]` 비율)

### R2. Persona Panel Report
- **목적**: "13명의 대가는 뭐라고 하는가?"
- **구조**:
  1. Cover (verdict 분포 차트)
  2. 13명 종합 표
  3. Style-split (가치파/성장파/매크로파/리스크파)
  4. **Thesis × Persona Matrix** (각 thesis에 대한 13명 stance — 핵심 추가)
  5. Universal concerns (다수 페르소나가 공통 우려)
  6. Unique alpha (1-2명만 본 인사이트)
  7. 페르소나별 상세 (5단계 분석 + narrative_vs_quant_resolution)

### R3. Executive Summary
- **목적**: "의사결정"
- **구조**:
  1. **한 페이지 결정 시트** (cover에 BUY/HOLD/SELL + qty + entry/exit)
  2. 메르 thesis 요약 (3-5 bullet)
  3. 정량 검증 결과 (사실 vs 가정 분리 표)
  4. Persona panel 합의도 (verdict 분포 + 이견 요약)
  5. Trade decision (risk-adjusted size)
  6. 핵심 위험 5개 (가장 먼저 무너질 가정)
  7. 다음 모니터링 포인트
