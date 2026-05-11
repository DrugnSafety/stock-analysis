---
name: pipeline-orchestrator
description: 메르 블로그 글 1개를 입력받아 thesis-first → 13 personas panel → risk + portfolio까지 모든 단계를 subagent로 통합 실행하는 풀 파이프라인. 부모 Claude가 stage별 subagent들을 spawn하고 결과를 다음 stage에 연결. LangGraph의 multi-stage StateGraph를 subagent 패턴으로 대체.
---

# Pipeline Orchestrator (Full Subagent Pipeline)

## 역할

기존 5개 plugin (naver-blog-investment / multi-model-arena / investor-personas / trade-engine / backtester)을 **subagent로 통합**하여 LangGraph 같은 단일 워크플로 제공.

장점:
- 외부 API 키 불필요 (전부 Cowork plan)
- 추가 dependency 0
- 각 stage subagent 독립 컨텍스트로 cross-contamination 없음

## 7-Stage Pipeline

```
Stage 1: 본문 fetch     (no subagent — Python script)
   ↓
Stage 2: Thesis 추출    (1 subagent, claude-inline)
   ↓
Stage 3: 4-Analyst 평가 (N×4 subagents, parallel — N개 thesis × 4명 analyst)
   ↓
Stage 4: 종목 추출 + Risk Manager (Python scripts only)
   ↓
Stage 5: 13 Personas Panel (13 subagents, parallel)
   ↓
Stage 6: Portfolio Manager (Python script + 1 consolidator subagent)
   ↓
Stage 7: 결과 PDF + Ledger 누적
```

## 부모 Claude가 따를 절차

### Stage 1 — 본문 fetch (no subagent)

```bash
python plugins/backtester/skills/historical-blog-collector/scripts/fetch_post_body.py \
    {BLOG_URL} --output /tmp/post.json
```

### Stage 2 — Thesis 추출 (1 subagent)

```
Task (general-purpose):
  description: "메르 글 thesis 추출"
  prompt: """
    당신은 stock-extractor + thesis-extractor 역할.
    아래 메르 블로그 본문에서 8-12개의 핵심 thesis를 추출.
    각 thesis: claim_id (T01...), claim, type (factual/predictive/normative/conditional),
    importance (core/supporting/aside), timeframe, supporting_evidence, tags.

    {post.json content}

    Output JSON: {theses: [...], summary_one_liner: "..."}
  """

→ /tmp/thesis_list.json 저장
```

### Stage 3 — 4-Analyst 평가 (병렬)

각 core thesis에 대해 4 subagent (Macro / Industry / Empirical / Counter):

```
For each core thesis (보통 5-7개):
  Spawn 4 Tasks in single message:
    Task A: Macro Analyst (그 thesis가 거시경제·정책 관점에서 옳은가)
    Task B: Industry Analyst (산업·기업 관점)
    Task C: Empirical Analyst (정량·역사적 사례)
    Task D: Counter (가장 강한 반박)

  → 4 결과 → state.thesis_evaluations[claim_id] 누적
```

총 spawn: N theses × 4 analysts = ~24-28 subagents.

### Stage 4 — 종목 추출 + Risk Manager (no subagent)

```bash
# 종목 추출 (이미 thesis에 implicit하게 있거나 별도 분석)
# Python helper로 매핑

# Risk Manager
python plugins/trade-engine/skills/risk-manager/scripts/calc_limits.py \
    --ledger /tmp/preliminary_ledger.jsonl \
    --portfolio-value 1400000000 \
    --output /tmp/risk_limits.json
```

### Stage 5 — 13 Personas Panel (병렬 spawn)

```
Top 3-5 종목 각각에 대해:
  Spawn 13 Tasks in single message (한 페르소나 당 1 subagent):

  Task 1: Warren Buffett persona
    prompt: persona_loader.make_subagent_prompt(persona_id="warren-buffett",
              ticker={TICKER}, market_data=..., blog_context=...)
  Task 2: Charlie Munger
  Task 3: Peter Lynch
  ... (13 personas)

  → 13 결과 → state.persona_panel_results[ticker] = [...]
```

총 spawn: 5 종목 × 13 페르소나 = 65 subagents (한 메시지에 13개씩 5번).

### Stage 6 — Portfolio Manager (Python + 1 subagent)

Python script로 verdict aggregate → trade decision:

```bash
python plugins/trade-engine/skills/portfolio-manager/scripts/make_decisions.py \
    --ledger /tmp/full_ledger.jsonl \
    --risk-limits /tmp/risk_limits.json \
    --output /tmp/decisions.json
```

선택적으로 Consolidator subagent로 reasoning 보강:

```
Task (Consolidator):
  prompt: "다음 trade decisions에 대한 종합 reasoning + 위험 경고:
          {decisions.json}"
  → 사용자 친화적 narrative
```

### Stage 7 — 결과 + Ledger

```bash
# Paper portfolio simulation (선택)
python plugins/trade-engine/skills/paper-portfolio/scripts/simulate.py \
    --decisions /tmp/decisions.json \
    --start-cash 1400000000 \
    --end-date $(date +%Y-%m-%d) \
    --output /tmp/portfolio.json

# PDF
python plugins/trade-engine/skills/paper-portfolio/scripts/build_report.py \
    /tmp/portfolio.json --output /tmp/pipeline_report.pdf
```

state JSON에 모든 단계 결과 저장 → 사용자에게 결과 표시.

## State Schema (요약)

```json
{
  "type": "pipeline",
  "blog_url": "...",
  "stage": "stage_5_personas",
  "stages_completed": [
    {"stage": "stage_1_fetch", "completed_at": "..."},
    {"stage": "stage_2_thesis", "completed_at": "..."},
    ...
  ],
  "post_data": {...},
  "thesis_list": [...],
  "thesis_evaluations": {...},
  "persona_panel_results": {"267250.KS": [13 results], "439260.KS": [...]},
  "trade_decisions": [...],
  "errors": []
}
```

stage가 실패해도 state.json에 기록 → 부모 Claude가 그 stage부터 재실행 가능 (간이 checkpoint).

## 비용 추정

| Stage | Subagents | 누적 |
|---|---|---|
| Stage 2 (thesis) | 1 | 1 |
| Stage 3 (4-Analyst) | 24-28 | 25-29 |
| Stage 5 (Persona panel × 5종목) | 65 | 90-94 |
| Stage 6 (Consolidator) | 0-1 | 91-95 |
| **Total** | **~95 subagents** | |

전부 Cowork plan 사용량. 외부 API 비용 0.

## 비교 — LangGraph로 같은 워크플로

LangGraph로 구현 시:
- StateGraph 정의: 7 stages, 각 stage 안에 sub-graph
- 65개 persona는 fan-out edge로
- Conditional: signal 강도에 따라 portfolio_manager 분기
- Checkpoint로 stage별 resume

본 구현 vs LangGraph:
- ✅ 동일한 흐름 통제 가능
- ✅ Cowork plan으로 호출 (LangGraph는 OpenAI/Anthropic API 키 필요)
- ✅ dependency 0 (LangGraph는 ~30MB)
- ❌ Persistent 자동 resume 없음 (state JSON 수동 reload 필요)

## 실행 시간

- Stage 1 (fetch): ~2초
- Stage 2 (thesis): ~30초 (1 subagent)
- Stage 3 (4-Analyst, 병렬): ~60초 (한 메시지에 4개 spawn)
- Stage 4 (Python): ~5초
- Stage 5 (13 personas, 병렬): ~90초 per 종목 (5종목 = 7-8분)
- Stage 6 (Python + 1 subagent): ~30초
- Stage 7 (PDF): ~10초

**Total: 약 10-15분** (사용자가 한 메시지로 호출 → 부모 Claude가 multi-message로 진행).
