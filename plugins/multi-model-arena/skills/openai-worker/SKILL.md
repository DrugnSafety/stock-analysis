---
name: openai-worker
description: GPT-5.5(또는 o3 reasoning)를 사용해 메르 블로그 글에서 종목을 추출하거나 7-role multi-agent 분석을 수행하는 worker skill. naver-blog-investment의 stock-extractor·trading-analysis와 동일한 출력 스키마를 따라 다른 worker와 합의(consensus) 비교가 가능하다. 사용자가 "OpenAI로 분석", "GPT-5로 종목 추출", "GPT 분석", "OpenAI worker" 등을 언급하면 트리거된다. .env에 OPENAI_API_KEY가 설정되어 있어야 한다.
---

# OpenAI Worker

## 역할

OpenAI GPT-5.5 (또는 fallback gpt-4.1)를 사용해 다음 작업 수행:

1. **종목 추출**: 블로그 본문 → 회사·산업·ETF·티커 JSON
2. **7-role 분석**: 단일 ticker → BUY/HOLD/SELL verdict + 7개 관점 perspectives

출력 스키마는 `naver-blog-investment` plugin의 `stock-extractor`·`trading-analysis`와 **완전히 동일**하여 consensus-builder가 cross-model 비교를 수행할 수 있다.

## 사용

```bash
# 종목 추출
python skills/openai-worker/scripts/extract_openai.py /tmp/post.json --output /tmp/openai_stocks.json

# 단일 종목 분석
python skills/openai-worker/scripts/analyze_openai.py 439260.KS \
    --post /tmp/post.json \
    --market /tmp/market_439260_KS.json \
    --output /tmp/openai_analysis_439260.json
```

## reasoning 모드

`OPENAI_REASONING_EFFORT` 환경변수로 추론 깊이 조절:

| 값 | 적합한 작업 |
|---|---|
| `minimal` | 빠른 종목 추출 (PoC) |
| `medium` | 일반적 추출·간단 분석 |
| `high` (기본) | 7-role 분석, Bull/Bear thesis |

GPT-5.5의 reasoning mode가 가용하지 않으면 자동으로 일반 chat completion으로 fallback.

## 비용 안전장치

- 입력 토큰이 30,000 초과 시 **본문 요약 모드** 활성화 (Claude가 사전 요약)
- `ARENA_MAX_COST_USD` 환경변수로 1회 호출당 한도 제한
- 응답마다 usage(prompt_tokens, completion_tokens, cost) 메타데이터 기록

## 다른 worker와의 차이점

| 항목 | OpenAI worker | Gemini worker | Claude (인라인) |
|---|---|---|---|
| 학습 cutoff | OpenAI 정책에 따라 | Google 정책 | May 2025 |
| 한국어 품질 | 좋음 | 매우 좋음 | 매우 좋음 |
| 도구 호출 | Function calling | Function calling | 네이티브 (Cowork) |
| 비용 | 사용자 키 | 사용자 키 | Cowork plan |
| reasoning | reasoning_effort | thinking budget | extended thinking |

## 결과 JSON에 포함되는 메타

```json
{
  "ticker": "439260.KS",
  "verdict": "BUY",
  "confidence": 0.72,
  "agent_perspectives": { ... },
  "_meta": {
    "model_provider": "openai",
    "model_used": "gpt-5.5",
    "reasoning_effort": "high",
    "prompt_tokens": 4231,
    "completion_tokens": 1842,
    "estimated_cost_usd": 0.34,
    "elapsed_seconds": 28.5,
    "called_at": "2026-04-28T..."
  }
}
```
