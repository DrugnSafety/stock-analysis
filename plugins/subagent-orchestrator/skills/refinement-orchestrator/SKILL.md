---
name: refinement-orchestrator
description: thesis-first 또는 persona-panel 결과 중 confidence < 0.5인 약한 thesis를 자동으로 재분석하여 보강하는 skill. 부모 Claude가 약한 thesis들을 식별 → 외부 데이터 fetch (뉴스·공시) subagent → 재평가 subagent를 차례로 spawn. LangGraph의 conditional refinement loop를 subagent로 대체.
---

# Refinement Orchestrator (저신뢰 thesis 자동 보강)

## 역할

LangGraph의 `conditional edge → re-evaluate` 패턴을 subagent로 구현.

흐름:
1. **약한 thesis 식별**: `confidence < 0.5` 또는 `agreement_level == "low"`인 thesis 선별
2. **외부 데이터 fetch subagent**: 해당 thesis 관련 최신 뉴스·공시 자동 검색
3. **재평가 subagent**: 추가 데이터를 받아 thesis 재평가
4. **반복**: 여전히 약하면 max_iterations까지 반복

## State Schema

```json
{
  "type": "refinement",
  "thesis_list_path": "...",
  "min_confidence": 0.5,
  "max_iterations": 2,
  "iteration": 0,
  "weak_theses": [
    {
      "claim_id": "T06",
      "claim": "...",
      "original_confidence": 0.42,
      "refinement_history": [],
      "current_confidence": 0.42,
      "additional_evidence": []
    }
  ]
}
```

## 부모 Claude가 따를 절차

### Step 0: 약한 thesis 식별

```bash
python plugins/subagent-orchestrator/skills/refinement-orchestrator/scripts/identify_weak.py \
    --thesis-list /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --min-confidence 0.5 \
    --output /tmp/weak_theses.json
```

출력: `weak_theses` 리스트 (claim_id, claim, current_confidence, why_weak).

### Step 1: 각 약한 thesis에 대해 데이터 fetch subagent

부모 Claude가 한 메시지에 N개 Task 동시 spawn (병렬):

```
For each weak thesis:
  Task (subagent_type="general-purpose"):
    description: "T06 보강 데이터 수집"
    prompt: """
      당신은 investment researcher입니다.
      다음 thesis가 confidence {0.42}로 약한 평가를 받았습니다:

      Claim: "{thesis claim}"
      Current rationale: "{previous reasoning}"

      이 thesis를 검증하기 위해 다음을 수행:
      1. 관련 최신 뉴스 키워드 3-5개 도출
      2. WebSearch tool로 각 키워드 검색
      3. 핵심 사실 추출 (정량 데이터 우선)
      4. 데이터 태깅: [actual] / [inference] / [assumption]

      Output JSON:
      {
        "claim_id": "T06",
        "search_keywords": [...],
        "new_evidence": [
          {"source": "...", "fact": "...", "tag": "[actual]/[inference]"}
        ],
        "summary": "이 thesis가 강화되는가, 약화되는가, 변동 없는가?"
      }
    """
```

→ 각 결과를 weak_theses[i].additional_evidence에 누적.

### Step 2: 재평가 subagent

각 thesis에 대해 추가 evidence를 input으로 새 평가:

```
For each weak thesis:
  Task (subagent_type="general-purpose"):
    description: "T06 재평가"
    prompt: """
      You are evaluating the following thesis with additional evidence
      that was not available in the previous round.

      Claim: "{thesis claim}"
      Original confidence: {0.42}
      Original rationale: "{...}"

      ADDITIONAL EVIDENCE (from refinement round):
      {new_evidence summary}

      Re-evaluate the thesis. Did the new evidence change your assessment?

      Output JSON:
      {
        "claim_id": "T06",
        "updated_stance": "support | neutral | rebut",
        "updated_confidence": 0.0-1.0,
        "delta_from_original": +/-N,
        "key_new_facts": [...],
        "rationale": "..."
      }
    """
```

### Step 3: Iteration 결정

```bash
python ... refinement_check.py --state /tmp/refine_state.json
```

```
if iteration < max_iterations AND any thesis still has confidence < min_confidence:
    goto Step 1 (다음 iteration)
else:
    goto Step 4
```

### Step 4: 결과 집계

기존 thesis_eval 결과에 refinement된 평가를 merge → 새 all_aggregate.json 생성:

```bash
python ... merge_refinements.py \
    --original /tmp/thesis_eval/all_aggregate.json \
    --refinements /tmp/refine_state.json \
    --output /tmp/thesis_eval_refined.json
```

### Step 5: 사용자에게 결과

```
🔬 Refinement 완료

원래 평가:
  T06 confidence 0.42 (약함)
  T08 confidence 0.45 (약함)

Iteration 1 후:
  T06 confidence 0.42 → 0.71 (+0.29) ← 신규 evidence: "캐나다 정부 2026 Q1 추가 inv 공시"
  T08 confidence 0.45 → 0.55 (+0.10) ← 변화 미미

Iteration 2:
  T06 confidence 0.71 (안정)
  T08 confidence 0.58 (still 약함)

총 spawn: 8 subagents (4 fetch + 4 re-eval)
저장: /tmp/thesis_eval_refined.json
```

## 비용

| Iteration | Subagents | 누적 |
|---|---|---|
| 1 | N(약한 thesis) × 2 | 8 (예: 4개 약한 thesis) |
| 2 | M × 2 | 12 |
| Max (2 iter) | up to 16 |

평균 thesis-first 1회 분석 후 약 2-3개의 thesis가 confidence < 0.5 → iteration 1만에 대부분 보강됨.
