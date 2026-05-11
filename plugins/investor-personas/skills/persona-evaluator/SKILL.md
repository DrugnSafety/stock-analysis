---
name: persona-evaluator
description: 단일 종목을 단일 페르소나(워런 버핏·캐시 우드 등 13명 중 1명)로 평가하는 skill. 해당 페르소나의 SKILL.md를 system prompt로 주입하여 OpenAI/Gemini/Claude로 호출 가능. 결과는 페르소나의 5단계 분석 시퀀스 + verdict + key concerns + opportunities + 데이터 태깅 포함 JSON. 사용자가 "버핏 관점에서 분석", "린치 lens", "X 페르소나 평가" 등을 언급하면 트리거된다.
---

# Persona Evaluator

## 역할

단일 (ticker, persona) 쌍을 평가:
1. 해당 페르소나의 SKILL.md를 로드 (system prompt로 주입)
2. ticker의 시장 데이터 + 블로그 컨텍스트(옵션)를 user prompt로 전달
3. LLM이 페르소나의 5단계 시퀀스를 따라 분석
4. 통일된 JSON 스키마로 출력

## 사용

```bash
# 단일 페르소나 평가 (OpenAI)
python skills/persona-evaluator/scripts/evaluate.py \
    267250.KS warren-buffett \
    --market /tmp/market_267250_KS.json \
    --post /tmp/post.json \
    --output /tmp/persona_eval_267250_buffett.json \
    --provider openai

# Gemini 사용
python skills/persona-evaluator/scripts/evaluate.py \
    267250.KS cathie-wood \
    --market /tmp/market_267250_KS.json \
    --provider gemini
```

## 출력 스키마

```json
{
  "ticker": "267250.KS",
  "persona_kr": "워런 버핏",
  "persona_en": "Warren Buffett",
  "evaluated_at": "2026-04-28T...",
  "verdict": "lean_bullish | lean_bearish | neutral",
  "confidence": 0.0,
  "horizon": "long_term | medium_term | short_term",
  "stage_results": [
    {
      "stage_num": 1,
      "stage_name": "Circle of competence",
      "passed": true,
      "rationale": "...",
      "data_tags": ["[actual] FY24 매출 ...", "[inference] ..."]
    }
  ],
  "key_concerns": [...],
  "key_opportunities": [...],
  "uncertainty_acknowledged": "어떤 가정이 깨지면 verdict가 뒤집히는가",
  "thesis_lens_applications": [
    {
      "claim_id": "T1",
      "claim_text": "추출된 thesis 원문 (요약)",
      "stance": "support | challenge | neutral",
      "rationale": "이 페르소나의 framework로 봤을 때 이 thesis가 왜 support/challenge인지 1-2줄"
    }
  ],
  "_meta": {
    "model_provider": "openai|gemini|claude",
    "model_used": "gpt-5.5",
    "elapsed_seconds": 0,
    "estimated_cost_usd": 0
  }
}
```

## thesis_lens_applications 필수 출력 (Phase 4 — 사용자 요청)

**절대 누락 금지**. 입력에 thesis_list.json이 포함된 경우 (블로그 분석 워크플로우):
- 모든 thesis를 페르소나의 framework로 평가
- 각 thesis에 대해 `support` (지지) / `challenge` (반박) / `neutral` (무관) 중 하나 명시
- 이 필드가 비어있으면 build_r2.py의 Thesis × Persona Matrix가 렌더링되지 않음

Standalone 분석 (블로그 글 없음, ticker만)에서만 빈 배열 `[]` 허용.

## Anti-Hallucination

- 모든 숫자에 `[actual]/[estimated]/[assumption]/[derived]/[unavailable]` 태깅 의무
- 페르소나의 5단계를 모두 거쳐야 (skip 금지)
- 페르소나의 능력범위 외 종목은 "outside circle of competence" 명시 후 종료
- **재무 분석 시 의무**: `/finance:financial-statements` (financial_statements_us_gaap.py 모듈) 출력을 무조건 활용
  - 5년 annual + 5분기 quarterly 데이터를 anchor로 사용
  - 페르소나가 임의로 만든 추정치보다 SEC EDGAR/DART 실측 데이터 우선
