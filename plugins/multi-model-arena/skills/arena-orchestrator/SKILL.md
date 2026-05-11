---
name: arena-orchestrator
description: Multi-Model Arena의 병렬 실행 조정자. 단일 입력(블로그 본문 또는 ticker)을 받아 OpenAI worker, Gemini worker, Claude(현재 세션)에 동시 분배하여 독립 결과 3개를 생성한다. 결과는 표준 스키마로 정규화되어 consensus-builder가 비교할 수 있는 형태로 /tmp/arena_*.json에 저장된다. 사용자가 "arena 실행", "3개 모델 병렬 분석", "multi-model 비교", "Claude vs GPT vs Gemini" 등을 언급하면 트리거된다.
---

# Arena Orchestrator

## 역할

세 명의 worker (Claude · OpenAI · Gemini)를 동시에 호출해 독립 분석을 수행하고, 결과를 정규화하여 consensus-builder가 비교할 수 있도록 한다.

## 핵심 흐름

```
입력 (post.json 또는 ticker)
        │
        ▼
┌──────────────────────────────────┐
│  arena-orchestrator              │
│  - parallel dispatch             │
│  - retry & fallback              │
│  - cost tracking                 │
└──────────┬───────────────────────┘
           │
   ┌───────┼────────┐
   ▼       ▼        ▼
[Claude] [OpenAI] [Gemini]
   │       │        │
   └───────┼────────┘
           ▼
   /tmp/arena_extract_<ts>/
     ├── claude.json
     ├── openai.json
     ├── gemini.json
     └── orchestration.json   ← 비용·소요시간·실패 모델
```

## 사용

### 종목 추출 arena

```bash
python skills/arena-orchestrator/scripts/orchestrate_extract.py \
    /tmp/post.json \
    --output-dir /tmp/arena_extract_2026-04-28 \
    --include claude,openai,gemini      # 일부만 선택 가능
```

### 7-role 분석 arena

```bash
python skills/arena-orchestrator/scripts/orchestrate_analyze.py \
    439260.KS \
    --market /tmp/market_439260_KS.json \
    --post /tmp/post.json \
    --output-dir /tmp/arena_analyze_439260
```

## Claude worker 처리

Claude는 별도 worker 스크립트가 아니라 **Cowork 세션의 Claude(현재 모델)** 가 직접 분석한다:
- arena-orchestrator는 placeholder JSON을 미리 작성 (`/tmp/arena_*/claude.json`)
- Claude는 stock-extractor·trading-analysis SKILL.md를 따라 직접 본문 읽고 결과를 해당 파일에 덮어쓰기
- 외부 API 비용 없음

이 방식의 장점: 다른 worker는 환경변수·네트워크 의존, Claude는 항상 가용.

## 실패 처리

- 한 worker가 실패해도 나머지는 계속 진행
- `orchestration.json`에 worker별 status: success | failed | skipped 기록
- 모두 실패 시 명확한 에러 + 원인별 hint

## 비용·시간 한도

```bash
# 환경변수
ARENA_MAX_COST_USD=2.00       # 1회 arena 한도 (모든 worker 합산)
ARENA_TIMEOUT_SECONDS=120     # 1개 worker 최대 시간
```

초과 시 해당 worker 강제 종료 + 결과 부분 보존.
