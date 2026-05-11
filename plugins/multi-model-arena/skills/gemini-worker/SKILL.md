---
name: gemini-worker
description: Google Gemini 3.1(또는 deep think 모드)을 사용해 메르 블로그 글에서 종목을 추출하거나 7-role multi-agent 분석을 수행하는 worker skill. naver-blog-investment의 stock-extractor·trading-analysis와 동일한 출력 스키마를 따라 multi-model arena의 cross-model 비교가 가능하다. Gemini는 1M token context와 web grounding 지원으로 메르 블로그 본문 전체를 잘라내지 않고 분석 가능. 사용자가 "Gemini로 분석", "Gemini 3.1", "Gemini worker", "구글 분석" 등을 언급하면 트리거된다. .env에 GOOGLE_API_KEY가 설정되어 있어야 한다.
---

# Gemini Worker

## 역할

Google Gemini 3.1 (또는 fallback gemini-2.5-pro)를 사용해 다음 작업 수행:

1. **종목 추출**: 블로그 본문 → 회사·산업·ETF·티커 JSON
2. **7-role 분석**: 단일 ticker → BUY/HOLD/SELL verdict + 7개 관점

OpenAI worker와 **동일한 출력 스키마**를 따른다.

## Gemini 차별 강점

| 강점 | 활용 |
|---|---|
| 1M token context | 본문 잘라내지 않고 전체 + 댓글 + 이전 글까지 한번에 |
| Web grounding | 신규 IPO·최근 실적 자동 검증 |
| Deep think mode | 7-role 분석 시 reasoning 깊이 향상 |
| 한국어 자연스러움 | 메르 글의 뉘앙스(예: "찐득한", "맑은") 잘 포착 |

## 사용

```bash
# 종목 추출
python skills/gemini-worker/scripts/extract_gemini.py /tmp/post.json --output /tmp/gemini_stocks.json

# 단일 종목 분석
python skills/gemini-worker/scripts/analyze_gemini.py 439260.KS \
    --post /tmp/post.json \
    --market /tmp/market_439260_KS.json \
    --output /tmp/gemini_analysis_439260.json
```

## Deep Think 모드

`GOOGLE_DEEP_THINK=true` 설정 시 Gemini의 thinking budget 자동 활성화:
- 7-role 분석에서 Bull/Bear thesis 더 정교화
- reasoning trace는 결과 JSON의 `_meta.thinking_summary`에 부분 저장

## Web Grounding (Optional)

`GOOGLE_USE_GROUNDING=true`로 활성화 시 Google Search 도구 호출 가능:
- 신규 IPO 종목 자동 검증
- 최근 뉴스·공시 자동 인용
- 비용은 Google 정책에 따름 (별도 grounding charge)

## 비용 안전장치

- 입력 토큰이 200,000 초과 시 본문 chunking
- `ARENA_MAX_COST_USD` 한도
- 응답마다 usage 메타데이터 기록

## 결과 메타

```json
{
  "_meta": {
    "model_provider": "google",
    "model_used": "gemini-3.1",
    "deep_think": true,
    "use_grounding": false,
    "input_tokens": 12000,
    "output_tokens": 2500,
    "thinking_tokens": 5000,
    "estimated_cost_usd": 0.18,
    "elapsed_seconds": 22.3,
    "grounding_sources": []
  }
}
```
