---
name: codex-integration:codex-thesis-validator
description: >
  Claude의 thesis 평가에 대해 OpenAI o3·o4-mini·GPT-5의 second-opinion을 제공.
  multi-model-arena 패턴 확장 — Claude vs OpenAI 평가 일치율 측정 + cross-model consensus.

  트리거: "OpenAI 2nd opinion", "Codex thesis 검증", "GPT cross-validation".
version: 0.1.0
environment: Claude Code (preferred) or Cowork (with OPENAI_API_KEY)
---

# Codex Thesis Validator — Claude vs OpenAI Cross-Validation

## 목적
13 페르소나 + 4-Analyst (Claude 단일 모델) verdict의 **single-model bias**를 차단. OpenAI o3·o4-mini·GPT-5으로 동일 thesis를 재평가하여 cross-model consensus 측정.

## 사용 환경

| 환경 | 작동 방식 |
|---|---|
| **Claude Code (CLI)** | `codex` CLI subprocess 호출 — ChatGPT Pro 계정으로 인증, 별도 API key 불필요 |
| **Cowork (sandbox)** | OpenAI API 직접 호출 — `OPENAI_API_KEY` env 필요 |

## 입력
- ticker 또는 thesis_id
- `thesis_eval/all_aggregate.json` (Claude의 4-Analyst 결과)
- 사용할 OpenAI 모델 (`o3` | `o4-mini` | `gpt-5`)

## 출력 `cross_validation/{ticker}_openai.json`
```json
{
  "ticker": "010140.KS",
  "model": "o4-mini",
  "via": "codex_cli",
  "thesis_evaluations": [
    {
      "thesis_id": "T4",
      "openai_stance": "support",
      "openai_confidence": 0.78,
      "openai_rationale": "...",
      "claude_stance": "support",
      "claude_confidence": 0.66,
      "agreement": "high",
      "stance_match": true,
      "confidence_delta": +0.12
    }
  ],
  "aggregate": {
    "n_thesis": 15,
    "stance_agreement_pct": 86.7,  // 13/15 일치
    "avg_confidence_delta": +0.05,
    "interpretation": "OpenAI는 평균적으로 Claude보다 5%p 자신감 높음"
  }
}
```

## 권장 사용 패턴
1. **자동 cross-validation**: build_combined.py 직전 자동 실행 — stance disagreement > 30% 시 PDF에 ⚠️ 경고 표시
2. **수동 second-opinion**: 특정 thesis만 GPT-5로 deep review

## LangSmith 자동 트레이싱
`langsmith_wrapper.py`의 `@traced_call`로 자동 wrapping — LangSmith UI에서 "Claude vs OpenAI" 비교 가능.
