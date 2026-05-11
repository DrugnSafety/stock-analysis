---
name: sa-refine
description: thesis-first 또는 persona-panel 결과 중 confidence < 0.5인 약한 thesis를 자동 보강. 부모 Claude가 약한 thesis들을 식별 → 각 thesis에 대해 외부 데이터 fetch subagent + 재평가 subagent를 spawn → 결과 merge. 원본 결과보다 더 confident한 평가 도출.
---

# /sa-refine

## 사용법

```
/sa-refine [--thesis-list PATH] [--eval-dir PATH] [--min-confidence 0.5] [--max-iterations 2]
```

## 부모 Claude가 따를 절차

### Step 0: 약한 thesis 식별

```bash
PLUG="/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/subagent-orchestrator"
WORK="/tmp/sa_refine"
mkdir -p "$WORK"

python3 "$PLUG/skills/refinement-orchestrator/scripts/identify_weak.py" \
    --thesis-list /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --min-confidence 0.5 \
    --output "$WORK/weak_theses.json"
```

출력 예: `[{claim_id: "T06", current_confidence: 0.42, ...}]`

### Step 1: 각 약한 thesis에 대해 데이터 fetch subagent (병렬)

부모 Claude가 한 메시지에 N개 Task spawn:

```
For each weak thesis (보통 2-4개):
  Task (general-purpose):
    description: "T06 보강 데이터 수집"
    prompt: """
      당신은 investment researcher.

      약하게 평가된 thesis:
        Claim: "{claim text}"
        Current confidence: {0.42}
        Why weak: {agreement=split / 데이터 부족}

      이 thesis 검증을 위한 다음을 수행:
      1. 검색 키워드 3-5개 도출
      2. WebSearch tool로 각 키워드 검색 (최근 6개월)
      3. 핵심 사실 추출 (정량 데이터 우선)
      4. 데이터 태깅: [actual] / [inference] / [assumption]

      Output JSON:
      {
        "claim_id": "T06",
        "search_keywords": [...],
        "new_evidence": [
          {"source": "...", "fact": "...", "tag": "[actual]"},
          ...
        ],
        "thesis_strength_change": "strengthens | weakens | neutral",
        "summary": "핵심 결론 1-2 문장"
      }
    """
```

각 결과를 `$WORK/iter1_T06_fetch.json` 등에 저장.

### Step 2: 각 thesis에 대해 재평가 subagent (병렬)

```
For each weak thesis:
  Task (general-purpose):
    description: "T06 재평가"
    prompt: """
      Re-evaluate this thesis with new evidence.

      Original:
        Claim: "{claim}"
        Original confidence: {0.42}
        Original rationale: "{...}"

      ADDITIONAL EVIDENCE (from refinement):
      {new_evidence summary from Step 1}

      New evaluation tasks:
      - Did the new evidence change your assessment?
      - Updated stance: support / neutral / rebut?
      - Updated confidence (0-1)
      - Specifically cite which new fact tipped you

      Output JSON:
      {
        "claim_id": "T06",
        "updated_stance": "support | neutral | rebut",
        "updated_confidence": 0.0-1.0,
        "delta_confidence": +/-N (vs original),
        "key_new_facts_used": ["fact 1", "fact 2"],
        "rationale": "..."
      }
    """
```

### Step 3: Iteration 결정

```python
# 부모 Claude 직접 판단
still_weak = [t for t in updated_theses if t.updated_confidence < min_confidence]
if iteration < max_iterations and still_weak:
    # 다시 Step 1 (still_weak에 대해서만)
    iteration += 1
else:
    # 종료
```

### Step 4: 원본 결과와 merge

```bash
# 원본 thesis_eval/all_aggregate.json 백업
cp /tmp/thesis_eval/all_aggregate.json $WORK/original.json

# 각 약한 thesis의 평가를 update
python3 << EOF
import json
with open("$WORK/original.json") as f: orig = json.load(f)
# updated_theses의 결과로 aggregate.weighted_confidence 등 update
# (구현은 분석 결과에 따라)
with open("/tmp/thesis_eval/all_aggregate_refined.json", "w") as f:
    json.dump(orig, f, ensure_ascii=False, indent=2)
EOF
```

### Step 5: 결과 제시

```
🔬 Refinement 완료

원본 약한 thesis (3개):
  T06 confidence 0.42 → 0.71 (+0.29) ✨ "캐나다 정부 2026 Q1 추가 발표"가 결정적
  T08 confidence 0.45 → 0.55 (+0.10) "데이터 부족 — 추가 보강 어려움"
  T10 confidence 0.48 → 0.62 (+0.14) 

총 spawn: 6 subagents (3 fetch + 3 re-eval)
저장: /tmp/thesis_eval/all_aggregate_refined.json

다음 단계:
- thesis_to_stocks를 refined evaluation으로 재계산
- 또는 /sa-debate로 가장 흥미로운 thesis에 대해 토론
```

## 비용

| 단계 | Subagents |
|---|---|
| Iteration 1 (약한 thesis N=3) | 3 fetch + 3 re-eval = 6 |
| Iteration 2 (still weak M=1) | 1 + 1 = 2 |
| **Max** | **약 8-10 subagents** |

전부 Cowork plan.
