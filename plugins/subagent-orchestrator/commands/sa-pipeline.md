---
name: sa-pipeline
description: 메르 블로그 글 1개를 입력받아 thesis-first → 4-Analyst 평가 → 13 personas panel → risk + portfolio까지 모든 단계를 subagent로 통합 실행. 외부 API 키 불필요, 추가 dependency 0. 부모 Claude가 ~95개의 subagent를 multi-stage로 spawn하여 LangGraph 같은 흐름 구현.
---

# /sa-pipeline

## 사용법

```
/sa-pipeline <BLOG_URL> [--top-n-stocks 3] [--portfolio-value 1400000000] [--skip-personas]
```

## 부모 Claude가 따를 7-Stage 절차

### Stage 1: 본문 fetch (no subagent)

```bash
BLOG_URL="https://blog.naver.com/ranto28/{logNo}"
WORK="/tmp/sa_pipeline_$(date +%H%M%S)"
mkdir -p "$WORK"
PLUG="/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/subagent-orchestrator"

python3 plugins/backtester/skills/historical-blog-collector/scripts/fetch_post_body.py \
    "$BLOG_URL" --output "$WORK/post.json"
```

### Stage 2: Thesis 추출 (1 subagent)

```
Task (general-purpose):
  description: "메르 글 thesis 추출"
  prompt: |
    당신은 thesis-extractor.
    아래 메르 블로그 본문에서 8-12개의 핵심 thesis 추출.

    각 thesis: claim_id (T01...), claim, type (factual/predictive/normative/conditional),
    importance (core/supporting/aside), timeframe, supporting_evidence, tags.

    Body:
    {load /tmp/post.json content_text}

    Output JSON:
    {
      "summary_one_liner": "...",
      "theses": [...]
    }
```

→ `$WORK/thesis_list.json`

### Stage 3: 4-Analyst 평가 (~24 subagents, 병렬 batch)

For each core thesis (보통 5-7개):

부모 Claude가 한 메시지에 4 Tasks 동시:

```
Task A — Macro Analyst:
  description: "T{N} Macro 평가"
  prompt: <ANALYST_SYSTEMS["macro"]> + <thesis 정보>

Task B — Industry Analyst:
  prompt: <ANALYST_SYSTEMS["industry"]> + <thesis 정보>

Task C — Empirical Analyst:
  prompt: <ANALYST_SYSTEMS["empirical"]> + <thesis 정보>

Task D — Counter-thesis:
  prompt: <ANALYST_SYSTEMS["counter"]> + <thesis 정보>
```

(ANALYST_SYSTEMS는 multi-model-arena/skills/thesis-evaluator/scripts/evaluate_theses.py에 정의됨)

각 thesis 4 결과를 aggregate → `$WORK/thesis_eval/{cid}_aggregate.json`.

### Stage 4: 종목 매핑 + Risk Manager (no subagent)

```bash
# Stage 2의 thesis들에서 종목 매핑 (간이 LLM-free aggregation)
# 또는 별도 1 subagent for thesis_to_stocks

# Risk Manager
python3 plugins/trade-engine/skills/risk-manager/scripts/calc_limits.py \
    --ledger "$WORK/preliminary_ledger.jsonl" \
    --portfolio-value 1400000000 \
    --output "$WORK/risk_limits.json"
```

### Stage 5: 13 Personas Panel (병렬 13×N 종목)

Top N 종목 (기본 3) 각각에 대해:

```
For each ticker in top_n:
  Spawn 13 Tasks in single message:
    Task 1: warren-buffett
    Task 2: charlie-munger
    Task 3: peter-lynch
    Task 4: cathie-wood
    Task 5: michael-burry
    Task 6: nassim-taleb
    Task 7: ben-graham
    Task 8: bill-ackman
    Task 9: mohnish-pabrai
    Task 10: phil-fisher
    Task 11: rakesh-jhunjhunwala
    Task 12: stanley-druckenmiller
    Task 13: aswath-damodaran

  각 Task prompt: persona_loader.make_subagent_prompt(
    persona_id=...,
    ticker={TICKER},
    market_data=...,
    blog_context=<blog post>,
    round_num=1,
    opposite_arguments=None
  )
```

총 spawn: **3 종목 × 13 = 39 subagents** (한 메시지에 13개씩 3번).

각 결과를 `$WORK/persona_panel/{ticker}/{persona_id}.json`에 저장.

aggregate_panel.py로 종목별 verdict 분포·style-split·universal concerns 산출.

### Stage 6: Portfolio Manager + Consolidator (Python + 1 subagent)

```bash
python3 plugins/trade-engine/skills/portfolio-manager/scripts/make_decisions.py \
    --ledger "$WORK/full_ledger.jsonl" \
    --risk-limits "$WORK/risk_limits.json" \
    --output "$WORK/decisions.json"
```

선택적 Consolidator subagent — narrative reasoning:

```
Task — Consolidator:
  prompt: |
    종합:
    - 메르 글 thesis: {thesis_list}
    - 13 personas 의견: {panel results summary}
    - Trade decisions: {decisions.json}
    - Risk-adjusted position size 적용 결과

    사용자에게 친화적 narrative로 정리 (5-7 단락):
    1. 메르 글의 핵심 thesis 1-2개
    2. 13명 페르소나의 종합 (verdict 분포)
    3. 각 종목의 trade decision + reasoning
    4. 가장 중요한 risk 3개
    5. Skeptical view (가장 큰 우려)

    Output Markdown.
```

### Stage 7: 결과 PDF + Ledger

```bash
# Paper portfolio simulate
python3 plugins/trade-engine/skills/paper-portfolio/scripts/simulate.py \
    --decisions "$WORK/decisions.json" \
    --start-cash 1400000000 \
    --end-date $(date +%Y-%m-%d) \
    --output "$WORK/portfolio.json"

# PDF
python3 plugins/trade-engine/skills/paper-portfolio/scripts/build_report.py \
    "$WORK/portfolio.json" --output "$WORK/pipeline_report.pdf"

# 모든 verdict들 ledger.jsonl에 누적
python3 << EOF
import json
# thesis_eval 결과 + persona_panel 결과 → ledger record로 변환
# (구현 코드 생략 — record_id, date, ticker, verdict, confidence, source, persona)
EOF
```

### Stage 8: 사용자에게 결과 제시

```
🚀 Subagent Pipeline 완료

📰 글: "{제목}"
📊 단계 결과:
  Stage 1 (fetch): ✅
  Stage 2 (thesis 추출): ✅ {N}개 thesis
  Stage 3 (4-Analyst 평가): ✅ {N×4} subagents
  Stage 4 (종목 매핑 + risk): ✅ {M}개 종목
  Stage 5 (13 personas × top 3): ✅ 39 subagents
  Stage 6 (portfolio decision): ✅ {K}개 trade
  Stage 7 (PDF): ✅

🏆 Top 3 종목 trade decisions:
  267250.KS HD현대 — buy 1,055주 (₩1.06억) — signal +0.45
  009540.KS HD한국조선해양 — buy 286주 (₩1.54억) — signal +0.77
  439260.KS 대한조선 — buy 1,323주 (₩1.54억) — signal +0.78

📊 Persona Panel 합의도:
  HD현대: 7 lean_bullish / 4 neutral / 2 lean_bearish (medium)
  HD한국조선해양: 9 lean_bullish / 3 neutral / 1 lean_bearish (high)
  대한조선: 10 lean_bullish / 2 neutral / 1 lean_bearish (very high)

💰 비용: $0 외부 API (모든 subagent Cowork plan)
🤖 Total subagents: 95+

📁 결과:
  - State: /tmp/sa_pipeline_*/state.json
  - PDF: /tmp/sa_pipeline_*/pipeline_report.pdf
  - Ledger 누적: .analysis-log/backtest_real/ledger.jsonl
```

## 비용·시간

- 외부 API: $0
- Cowork plan subagent: 약 95개
- 실행 시간: 10-15분 (사용자가 한 메시지로 호출 → 부모 Claude가 multi-message로 stage별 진행)

## 옵션

| 인자 | 기본 | 설명 |
|---|---|---|
| `--top-n-stocks` | 3 | persona panel 적용할 상위 종목 수 |
| `--portfolio-value` | 1400000000 | KRW 기준 portfolio 값 |
| `--skip-personas` | false | 시간·비용 절감 (Stage 5 생략) |
| `--skip-paper` | false | Paper portfolio simulation 생략 |
| `--checkpoint` | true | 각 stage 후 state 저장 (실패 시 재개) |

## Checkpoint Resume

```
# Stage 5에서 실패한 경우
/sa-pipeline-resume /tmp/sa_pipeline_*/state.json
# 부모 Claude가 마지막 완료 stage 식별 → 그 다음부터 재시작
```
