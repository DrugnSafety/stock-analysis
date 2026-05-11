---
name: sa-debate
description: Subagent 기반 Bull-Bear-Skeptic 토론 cycle. LangGraph 없이도 Druckenmiller(Bull) vs Buffett(Bear) vs Skeptic의 round-robin 토론을 Anthropic Task tool subagent로 실행. 최대 3 round, convergence > 0.85 시 자동 종료. 외부 API 키 불필요.
---

# /sa-debate

## 사용법

```
/sa-debate <TICKER> [--max-rounds 3] [--convergence-threshold 0.85] [--blog-url URL]
```

## 부모 Claude (현재 세션)가 따를 절차

### Step 0: State 초기화 + 시장 데이터

```bash
TICKER="000660.KS"
WORK_DIR="/tmp/sa_debate_${TICKER//./_}"
mkdir -p "$WORK_DIR"
PLUG="/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/subagent-orchestrator"

python3 "$PLUG/skills/debate-orchestrator/scripts/state_helpers.py" init \
    --ticker "$TICKER" \
    --max-rounds 3 \
    --convergence-threshold 0.85 \
    --output "$WORK_DIR/state.json"

# 시장 데이터
python3 plugins/backtester/skills/historical-blog-collector/scripts/fetch_post_body.py \
    "$BLOG_URL" --output "$WORK_DIR/post.json"  # if blog_url 있을 때
```

### Step 1: Round 1 — 부모 Claude가 한 메시지에 3 Tasks 동시 spawn

부모 Claude는 다음 3개의 Task tool 호출을 단일 message에 작성:

```python
# 의사코드 — 실제로는 부모 Claude가 직접 Task tool 호출
import sys
sys.path.insert(0, "plugins/subagent-orchestrator/skills/_common")
from persona_loader import (
    make_subagent_prompt, SKEPTIC_SYSTEM, CONSOLIDATOR_SYSTEM
)

# Bull subagent prompt
bull_sys, bull_user = make_subagent_prompt(
    persona_id="stanley-druckenmiller",
    ticker="000660.KS",
    market_data=load("/tmp/market.json"),
    blog_context="...",
    round_num=1,
    opposite_arguments=None,
)

# Bear subagent prompt (Buffett)
bear_sys, bear_user = make_subagent_prompt(
    persona_id="warren-buffett",
    ticker="000660.KS",
    ...same...
)
```

Task spawning (한 메시지):

> Task 1 — `description: "Bull (Druckenmiller) round 1"`, `prompt: bull_sys + "\n\n" + bull_user`
>
> Task 2 — `description: "Bear (Buffett) round 1"`, `prompt: bear_sys + "\n\n" + bear_user`

Bull/Bear 결과 수신 후 Skeptic spawn:

> Task 3 — `description: "Skeptic round 1"`, `prompt: SKEPTIC_SYSTEM + "\n\n" + bull_result + bear_result`

3개 결과를 각각 `/tmp/sa_debate_*/round1_bull.json`, `round1_bear.json`, `round1_skeptic.json`에 저장.

### Step 2: 누적 + Convergence

```bash
python3 "$PLUG/skills/debate-orchestrator/scripts/state_helpers.py" append \
    --state "$WORK_DIR/state.json" \
    --bull "$WORK_DIR/round1_bull.json" \
    --bear "$WORK_DIR/round1_bear.json" \
    --skeptic "$WORK_DIR/round1_skeptic.json"

# Convergence check
python3 "$PLUG/skills/debate-orchestrator/scripts/state_helpers.py" check \
    --state "$WORK_DIR/state.json"
# 출력: {"continue": true/false, "next_action": "round_2 / consolidate", ...}
```

### Step 3: Round 2 (필요 시)

continue=true면 Round 2 spawn (이번엔 상대 의견 input 포함):

```python
# Bull round 2 — Bear 의견 input
bull_sys, bull_user = make_subagent_prompt(
    persona_id="stanley-druckenmiller",
    ticker="000660.KS",
    market_data=...,
    round_num=2,
    opposite_arguments=state["bear_history"],  # 직전 round 결과
)

# Bear round 2 — Bull 의견 input
bear_sys, bear_user = make_subagent_prompt(
    persona_id="warren-buffett",
    ...,
    opposite_arguments=state["bull_history"],
)
```

같은 spawn 패턴으로 3 Tasks. 결과 저장 후 append + check 반복.

### Step 4: Round 3 (필요 시)

같은 패턴 반복 (max_rounds 도달).

### Step 5: Final Consolidation

continue=false (또는 max_rounds 도달) 시 최종 1개 subagent:

```python
# Consolidator
consol_prompt = CONSOLIDATOR_SYSTEM + f"""

Full debate history:

Round 1:
- Bull: {state.bull_history[0]}
- Bear: {state.bear_history[0]}
- Skeptic: {state.skeptic_history[0]}

Round 2:
- Bull: {state.bull_history[1]}  (verdict updated? {state.bull_history[1].get('verdict_changed', False)})
- ...

Synthesize final verdict.
"""
```

> Task — `description: "Final consolidation"`, `prompt: consol_prompt`

결과 → `$WORK_DIR/consolidator.json` 저장.

### Step 6: Finalize + Ledger 누적

```bash
python3 "$PLUG/skills/debate-orchestrator/scripts/state_helpers.py" finalize \
    --state "$WORK_DIR/state.json" \
    --consolidator "$WORK_DIR/consolidator.json" \
    --ledger ".analysis-log/backtest_real/ledger.jsonl"
```

state.json의 final_verdict 등 업데이트되고 ledger.jsonl에 새 record append.

### Step 7: 사용자에게 결과 제시

```
🥊 Subagent Debate 완료 — 000660.KS

📊 진행: 2 round, 7 subagent spawn
📈 Convergence Score: 0.91 (high)

Round 1:
  🐂 Druckenmiller: lean_bullish (85%) — "AI capex tailwind, HBM monopoly"
  🐻 Buffett: neutral (60%) — "메모리 cyclical 정점 가능"
  🤔 Skeptic: agreement=split, key_question="AI capex 지속성?"

Round 2 (상대 의견 본 후):
  🐂 Druckenmiller: lean_bullish (82%, held) — "데이터센터 transformation으로 사이클 변형"
  🐻 Buffett: lean_bullish (65%, **changed**) — "Bull의 transformation 논거 수용"
  🤔 Skeptic: agreement=high, convergence_direction="toward bullish"

🏆 Final Verdict: lean_bullish (78%)
   Round 2에서 Bear가 Bull thesis 일부 수용 → 양측 lean_bullish 합의.
   Druckenmiller의 "데이터센터 transformation" 논거가 결정적.
   리스크: AI capex 둔화 시 verdict 약화.

📁 State: /tmp/sa_debate_000660_KS/state.json
📊 Ledger: .analysis-log/backtest_real/ledger.jsonl (record_id: sa_debate_000660_KS_...)
```

## 비용 / 시간

- 외부 API 비용: $0
- Cowork plan 사용량: 최대 10 subagent (3 round × 3 + 1 consolidator)
- 실행 시간: 2-5분 (subagent별 30초~1분)

## 다른 명령과의 연계

- `/sa-pipeline`이 완료되면 자동으로 흥미로운 종목 1-2개에 대해 `/sa-debate`를 권유
- `/sa-debate` 결과는 ledger에 누적 → backtester가 적중률 측정
