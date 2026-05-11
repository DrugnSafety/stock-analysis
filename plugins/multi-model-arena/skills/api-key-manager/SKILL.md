---
name: api-key-manager
description: Multi-Model Arena를 위한 API 키 관리 skill. .env 파일에서 OPENAI_API_KEY와 GOOGLE_API_KEY를 안전하게 로드하고, 키의 유효성을 빠르게 검증하며, 로그 출력 시 키를 마스킹한다. 사용자가 "API 키 설정", "OpenAI 키 등록", "Gemini 키 확인", "키 마스킹" 등을 언급하면 트리거된다. LLM을 사용하지 않으므로 추가 비용 없음.
---

# API Key Manager

## 역할

- **load_keys.py**: 워크스페이스의 `.env` 파일을 찾아 환경변수로 로드
- **mask_key.py**: 로그·결과 파일에 키를 출력할 때 첫 4자리 + `...` + 끝 4자리만 표시
- **check_keys.py**: OpenAI·Google API에 가벼운 ping을 보내 키 유효성 확인 (모델 list 호출)

## 키 검색 순서

스크립트는 다음 순서로 `.env` 파일을 탐색한다:

1. `$ARENA_ENV_FILE` 환경변수가 가리키는 경로
2. 현재 워크 디렉토리(`.`)의 `.env`
3. **워크스페이스 루트의 `.env`** (Cowork에서 보통 여기)
4. 부모 디렉토리(`..`)의 `.env`
5. `~/.config/multi-model-arena/.env` (사용자 글로벌)

가장 먼저 찾은 파일을 사용. 발견 시 경로를 stderr에 출력 (마스킹 후).

## 사용 예 (Bash)

```bash
# .env 로드 + 검증
python skills/api-key-manager/scripts/check_keys.py

# 출력 예:
#   .env loaded from: /Users/.../주식 분석/.env
#   OPENAI_API_KEY: sk-pr...abc1 ✅ (gpt-5.5 available)
#   GOOGLE_API_KEY: AIza...xyz9 ✅ (gemini-3.1 available)
#   Estimated cost per arena: ~$0.65
```

## 사용 예 (Python)

```python
from api_key_manager import load_env, get_key, mask

load_env()  # .env를 환경변수로 로드
openai_key = get_key("OPENAI_API_KEY")  # None 안전, 에러 시 명시적 메시지
print(f"Loaded: {mask(openai_key)}")  # sk-pr...abc1
```

## 안전성 규칙

- 절대 키를 그대로 stdout/stderr에 출력하지 않음 (mask 거쳐야 함)
- 결과 JSON에는 키를 저장하지 않음 (사용된 모델명만 기록)
- 환경변수에서 키를 읽고 메모리에서만 보관, 불필요 시 즉시 del

## 입력 형식 — `.env` 파일

```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-5.5
OPENAI_REASONING_EFFORT=high

GOOGLE_API_KEY=AIza...
GOOGLE_MODEL=gemini-3.1
GOOGLE_DEEP_THINK=true

ARENA_MAX_COST_USD=2.00
```
