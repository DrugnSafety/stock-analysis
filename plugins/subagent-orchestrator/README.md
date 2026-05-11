# Subagent Orchestrator Plugin

LangGraph 없이도 multi-agent workflow(cycle, conditional branching, parallel)를 구현하는 plugin. **Anthropic Task tool(subagent spawning)을 LangGraph node 대체**로 활용.

## 핵심 원칙

| LangGraph 개념 | 이 plugin의 대응 |
|---|---|
| StateGraph | 부모 Claude가 JSON dict로 state 관리 |
| Node | Subagent (Task tool) |
| Edge | 부모의 인라인 reasoning 또는 helper script |
| Conditional edge | 부모가 직접 if/else 판단 |
| Cycle | 같은 subagent를 이전 결과를 input으로 재호출 |
| Checkpoint | state JSON 파일 직렬화 |
| Parallel nodes | single message에 multiple Task call |

**장점**: 외부 API 키 불필요, 추가 dependency 없음, 각 subagent 독립 컨텍스트.

## 3개 Skill

| Skill | 역할 | 시간 |
|---|---|---|
| **debate-orchestrator** | Bull(Druckenmiller) ↔ Bear(Buffett) ↔ Skeptic round-robin 토론 cycle | 2-3 round |
| **refinement-orchestrator** | thesis confidence < 0.5 자동 보강 (re-fetch + re-extract) | 1-2 iteration |
| **pipeline-orchestrator** | 메르 글 → 13 personas + thesis-first → risk + portfolio 통합 subagent 흐름 | 1 run |

## 명령

| 명령 | 사용 |
|---|---|
| `/sa-debate <TICKER>` | 단일 종목에 대한 Bull-Bear-Skeptic 토론 cycle |
| `/sa-refine <BLOG_URL>` | thesis-first 결과의 약한 thesis 자동 보강 |
| `/sa-pipeline <BLOG_URL>` | 풀 파이프라인 (subagent 13명 + thesis + risk + portfolio) |

## 출력 형식

기존 plugin들과 동일한 ledger.jsonl 스키마로 결과 누적 → backtester가 그대로 적중률 측정.

## 실행 흐름 (간략)

```
사용자 → /sa-debate 000660.KS
   ↓
부모 Claude (Cowork 세션):
   1. state 초기화 (JSON)
   2. Round 1: Task spawn × 3 (Bull, Bear, Skeptic) ← single message, 병렬
   3. 결과 받음 → state.bull_history.append(...)
   4. convergence_score 계산 (helper script)
   5. score < 0.85 AND round < 3 → Round 2 (Task spawn × 3, 이전 round 결과 input)
   6. 합의 도달 또는 max_round → Consolidator subagent
   7. Final verdict + reasoning → ledger 누적
   ↓
사용자에게 결과 표시
```

## 의존성

```
# 추가 dependency 없음 (Anthropic Task tool은 빌트인)
# 기존 yfinance, weasyprint 등만 사용
```

## 라이선스 / 출처

LangGraph(Apache 2.0)의 개념을 차용했지만 코드 의존성은 0. 본 plugin은 자체 구현.
ai-hedge-fund(MIT)의 페르소나 prompt 패턴은 `plugins/investor-personas/`의 SKILL.md 그대로 활용.
