---
name: debate-orchestrator
description: 단일 ticker에 대해 Bull(Druckenmiller) vs Bear(Buffett) vs Skeptic(Gemini-style) round-robin 토론 cycle을 subagent로 실행. 각 round마다 상대 의견을 input으로 주고 verdict 갱신 가능. 최대 N round 또는 합의(convergence > 0.85) 시 종료. LangGraph cycle을 subagent 패턴으로 대체. 사용자가 "토론", "Bull-Bear debate", "subagent로 분석", "/sa-debate" 등을 언급하면 트리거.
---

# Debate Orchestrator (Subagent 기반 Bull-Bear-Skeptic Cycle)

## 역할

LangGraph의 `StateGraph + cycle + conditional edge`를 **부모 Claude(현재 세션) + Task tool spawn 패턴**으로 대체.

각 round에서:
- **Bull subagent**: Druckenmiller persona, 가장 강한 매수 논거
- **Bear subagent**: Buffett persona, 가장 강한 매도/관망 논거
- **Skeptic subagent**: 양측의 약점·hidden assumption 분석

3개 subagent는 **한 메시지에 동시 spawn** (병렬). 결과를 state에 누적, convergence 점수 계산 후 다음 round 또는 종료.

## State Schema (JSON)

```json
{
  "type": "debate",
  "ticker": "000660.KS",
  "round": 0,
  "max_rounds": 3,
  "convergence_threshold": 0.85,
  "bull_history": [],
  "bear_history": [],
  "skeptic_history": [],
  "convergence_score": 0.0,
  "final_verdict": null,
  "total_subagent_spawns": 0
}
```

## 부모 Claude가 따를 절차

### Step 0: 사전 준비

```bash
# State 초기화
python plugins/subagent-orchestrator/skills/_common/state_utils_init.py \
    --type debate \
    --ticker {TICKER} \
    --output /tmp/debate_state.json

# 시장 데이터 fetch (yfinance)
python plugins/naver-blog-investment/skills/trading-analysis/scripts/market_data.py \
    {TICKER} --output /tmp/market_{TICKER}.json
```

(기존 plugin 사용 가능; 미존재 시 backtester의 fetch 함수 활용)

### Step 1: Round 1 — 초기 평가 (병렬 spawn)

부모 Claude는 한 메시지에 **3개의 Task tool 호출을 동시에** 작성:

```
Task 1 (subagent_type="general-purpose"):
  description: "Druckenmiller Bull 평가"
  prompt: persona_loader.make_subagent_prompt(
    persona_id="stanley-druckenmiller",
    ticker={TICKER},
    market_data=<load market_{TICKER}.json>,
    blog_context=<load blog post if any>,
    round_num=1,
    opposite_arguments=None  # 첫 round
  )
  → JSON {verdict, confidence, key_argument, rationale, ...}

Task 2 (subagent_type="general-purpose"):
  description: "Buffett Bear 평가"
  prompt: persona_loader.make_subagent_prompt(
    persona_id="warren-buffett",
    ticker={TICKER},
    market_data=...,
    round_num=1,
    opposite_arguments=None
  )
  → JSON

Task 3 (subagent_type="general-purpose"):
  description: "Skeptic 분석"
  prompt: SKEPTIC_SYSTEM_PROMPT (in persona_loader.py)
         + Round 1의 Bull과 Bear 결과를 placeholder로 넣음
  
  ※ Skeptic은 Bull/Bear 결과 본 후 호출하므로, 사실은 Round 1.5에 spawn.
    실용상 부모는 Bull과 Bear 먼저 spawn → 결과 받은 뒤 Skeptic spawn 순서.
```

### Step 2: 결과 누적 및 Convergence 계산

```bash
# state.json update (부모가 직접 JSON edit 또는 helper 호출)
python plugins/subagent-orchestrator/skills/_common/append_round.py \
    --state /tmp/debate_state.json \
    --bull <bull_result.json> \
    --bear <bear_result.json> \
    --skeptic <skeptic_result.json>

# Convergence 점수 계산
python plugins/subagent-orchestrator/skills/_common/convergence.py \
    /tmp/debate_state.json
# 출력 예: continue=True, reason="convergence 0.62 < threshold — round 2 진행"
```

### Step 3: Conditional Branching

부모 Claude가 직접 판단:

```
if continue == True:
    goto Step 4 (Round 2)
else:
    goto Step 5 (Consolidation)
```

### Step 4: Round 2+ — 상대 의견 본 후 재평가

같은 페르소나에 spawn하되, **이전 round의 상대 결과를 prompt에 포함**:

```
Task 1 (Bull, round 2):
  prompt: persona_loader.make_subagent_prompt(
    persona_id="stanley-druckenmiller",
    ticker={TICKER},
    round_num=2,
    opposite_arguments=state["bear_history"]  # ← Bear의 직전 round 결과
  )
  → "이전 round Bear가 X라고 했음. 이를 검토 후 verdict 갱신/유지"

Task 2 (Bear, round 2):
  opposite_arguments=state["bull_history"]
```

Step 2~3 반복.

### Step 5: Final Consolidation

부모 Claude가 최종 1개 subagent spawn:

```
Task (Consolidator):
  description: "토론 종합"
  prompt: CONSOLIDATOR_SYSTEM_PROMPT
         + 전체 round_history 요약
  → JSON {final_verdict, final_confidence, consolidation_reasoning, ...}
```

state["final_verdict"] 등 update + ledger.jsonl에 기록:

```bash
# ledger 추가 (backtester가 측정)
python plugins/subagent-orchestrator/skills/_common/ledger_writer.py \
    --state /tmp/debate_state.json \
    --output .analysis-log/backtest_real/ledger.jsonl
```

### Step 6: 사용자에게 결과 제시

```
🥊 Subagent Debate — {TICKER}

📊 진행: {N} round, 총 {state.total_subagent_spawns} subagent spawn
📈 Convergence: {state.convergence_score}

Round 1:
  🐂 Druckenmiller (Bull): {verdict} {conf}% — "{key_argument}"
  🐻 Buffett (Bear): {verdict} {conf}% — "{key_argument}"
  🤔 Skeptic: agreement={...}, key_question="..."

Round 2:
  🐂 Druckenmiller (updated/held): ...
  🐻 Buffett (updated/held): ...
  🤔 Skeptic: ...

🏆 Final Verdict: {final_verdict} ({final_confidence}%)
   {consolidation_reasoning}
```

## 비용 가이드

| 호출 | 단위 |
|---|---|
| Round 1 | 3 subagent (Bull + Bear + Skeptic) |
| Round 2 | 3 subagent |
| Round 3 (필요 시) | 3 subagent |
| Final consolidation | 1 subagent |
| **Total max** | **10 subagents** (Cowork plan 사용량) |

ARENA_MAX_COST_USD 같은 외부 비용 없음. Cowork plan만 소비.

## 비교 — LangGraph vs 본 Subagent 구현

| 항목 | LangGraph | 본 Subagent 구현 |
|---|---|---|
| 외부 API | OpenAI/Anthropic 키 필요 | ✅ Cowork plan |
| dependency | langgraph + langchain | ✅ 0 |
| 페르소나 prompt | hardcoded | ✅ SKILL.md 동적 주입 |
| Cycle | edge·conditional | ✅ 부모 if/else |
| Parallel | graph 정의 | ✅ single message multi-Task |
| Persistent state | ✅ SQLite | ❌ JSON 파일 (단순) |
| Long-running (>5분) | ✅ resume 자동 | ❌ 세션 단일 실행 |
