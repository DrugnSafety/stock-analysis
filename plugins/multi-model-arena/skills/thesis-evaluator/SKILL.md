---
name: thesis-evaluator
description: 추출된 thesis 각각에 대해 4명의 analyst가 독립적으로 평가하는 skill. Macro Analyst(거시·정책), Industry Analyst(산업·기업 미시), Empirical Analyst(정량·역사적 사례), Counter-thesis Devil's Advocate(반박 가능성)이 같은 주장을 4개 lens로 평가하여 [지지/중립/반박] + 신뢰도 + rationale + counter-evidence를 제시. 단일 thesis도 4개 결과로 분해되어 합의 영역과 이견 영역을 식별 가능. 사용자가 "thesis 평가", "주장 검증", "4-analyst 평가", "메르 주장 맞는지", "validity check" 등을 언급하면 트리거된다.
---

# Thesis Evaluator

## 4-Analyst Lens

각 thesis는 다음 4명의 analyst가 독립적으로 평가:

### 1. Macro Analyst
- 거시경제·정책·지정학 관점
- "이 주장이 거시 환경 변화로 강화/약화될 수 있는가?"
- 데이터 소스: 정부 공식 발표, 중앙은행, 무역 통계, 지정학 리포트

### 2. Industry Analyst
- 산업·기업 미시 관점
- "이 주장이 산업 사이클·기업 capex·경쟁구도와 맞는가?"
- 데이터 소스: 업계 협회, 기업 공시, 산업 리포트

### 3. Empirical Analyst
- 정량 데이터·역사적 사례 관점
- "이 주장이 과거 데이터로 검증되는가? 비슷한 사례는?"
- 데이터 소스: 시계열 데이터, 학술 논문, 역사적 이벤트

### 4. Counter-thesis Devil's Advocate
- 의도적 반박 관점
- "이 주장의 가장 강한 반론은 무엇인가? 어떤 가정이 무너지면 틀리는가?"
- 데이터 소스: 반대 의견·소수자 의견·놓친 변수

## 평가 출력 (per analyst per thesis)

```json
{
  "claim_id": "T06",
  "analyst": "macro",
  "stance": "support | neutral | rebut",
  "confidence": 0.0-1.0,
  "rationale": "왜 그렇게 판단했는지 (2-4문장)",
  "supporting_data": [
    {"point": "데이터/사실", "source": "출처 또는 inference"}
  ],
  "counter_evidence": [
    {"point": "이 주장에 반하는 사실", "source": "..."}
  ],
  "key_assumption": "이 주장이 성립하려면 반드시 참이어야 하는 가정",
  "fragility_score": 0.0-1.0,
  "rationale_meta": {
    "model_used": "gpt-5.5 / gemini-3.1 / claude",
    "elapsed_seconds": 0
  }
}
```

## Aggregation (per thesis)

4명의 analyst 결과를 합쳐:

```json
{
  "claim_id": "T06",
  "claim": "Panamax 만재가 합리적 대안이 될 것",
  "evaluations": {
    "macro": {...},
    "industry": {...},
    "empirical": {...},
    "counter": {...}
  },
  "aggregate": {
    "support_count": 2,
    "neutral_count": 1,
    "rebut_count": 1,
    "weighted_stance": "support",
    "weighted_confidence": 0.62,
    "agreement_level": "medium",
    "key_disagreement": "Empirical은 데이터 부족으로 중립, Counter는 ship-to-ship transfer 대안 제시"
  }
}
```

## 4-Analyst가 같은 모델인가, 다른 모델인가?

**기본**: 같은 모델(예: gpt-5.5)이 4개의 다른 system prompt로 4번 호출.

**확장**: `--multi-model` 옵션 시:
- Macro: gpt-5.5 (광범위 거시 지식)
- Industry: gemini-3.1 (web grounding으로 산업 보고서 인용)
- Empirical: gpt-5.5 + reasoning=high (정량 추론)
- Counter: claude (의도적 대척점)

이 multi-model 모드는 더 풍부하지만 비용 4배.

## 사용

```bash
# Single-model 4-analyst (기본)
python skills/thesis-evaluator/scripts/evaluate_theses.py \
    /tmp/thesis_list.json \
    --output-dir /tmp/thesis_eval \
    --analysts macro,industry,empirical,counter

# Multi-model 4-analyst
python skills/thesis-evaluator/scripts/evaluate_theses.py \
    /tmp/thesis_list.json \
    --output-dir /tmp/thesis_eval \
    --multi-model
```

## 출력 파일 구조

```
thesis_eval/
├── T01_macro.json
├── T01_industry.json
├── T01_empirical.json
├── T01_counter.json
├── T01_aggregate.json
├── T02_macro.json
├── ...
└── all_aggregate.json    # 모든 thesis의 종합
```

## 핵심 규칙

- **데이터 기반**: 일반론이 아닌 구체적 사실·숫자·사례 제시
- **연역 vs 귀납 구분**: Empirical은 귀납, Macro는 연역적 추론 비중
- **Counter는 의도적**: 약한 반박은 금지, 가장 강한 반론을 찾을 것
- **Fragility score**: 이 주장이 깨질 가능성 (0=불변, 1=쉽게 깨짐)
- **Key assumption**: 명시되지 않은 전제도 노출
