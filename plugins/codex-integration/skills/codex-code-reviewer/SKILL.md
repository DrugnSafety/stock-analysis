---
name: codex-integration:codex-code-reviewer
description: >
  Plugin 코드 변경 시 OpenAI Codex로 second-opinion 코드 리뷰. Claude가 작성한 패치를
  OpenAI o3가 검토하여 logic bug, edge case, performance issue 자동 flag.

  트리거: "Codex 리뷰", "plugin 코드 OpenAI 검증", "second-opinion code review".
version: 0.1.0
environment: Claude Code (preferred) or Cowork (with OPENAI_API_KEY)
---

# Codex Code Reviewer

## 목적
Claude가 작성한 plugin 코드를 OpenAI o3로 cross-review하여 단일 모델 blind spot 차단. Anthropic + OpenAI 양사 reasoning 모델이 동시에 OK한 코드만 merge.

## 사용법 (Claude Code)
```bash
# 1. Claude Code 세션에서 코드 변경 작업
cd ~/Documents/Claude/Projects/주식\ 분석
claude  # Claude Code 시작 → 코드 작업

# 2. Codex로 cross-review 호출 (Claude Code 명령창에서)
/codex-review plugins/specialist-agents/scripts/checkpoint_manager.py

# 3. Codex가 review comment 출력 → 사용자가 accept/reject 결정
```

## 사용법 (Cowork)
```bash
python3 plugins/codex-integration/scripts/codex_runner.py \
  --mode o3 \
  --system "당신은 시니어 Python 코드 리뷰어. logic bug·edge case·performance·readability 4가지로 review." \
  --prompt "$(cat plugins/specialist-agents/scripts/checkpoint_manager.py)"
```

## 출력 schema
```json
{
  "file": "plugins/specialist-agents/scripts/checkpoint_manager.py",
  "reviewer": "openai-o3 via codex_cli",
  "issues": [
    {"severity": "high|medium|low", "line": 42, "category": "logic|edge_case|perf|readability", "comment": "..."}
  ],
  "overall_assessment": "approve | request_changes | comment",
  "summary": "전반적으로 견고한 구현. 다만 ..."
}
```

## 활용 시나리오
1. **PR 자동 review**: GitHub Actions에 codex_runner를 hook → Claude가 작성한 PR을 OpenAI가 review
2. **Plugin 패치 검증**: Tier 2 plugin 변경 시 자동 호출
3. **Refactor 대안 제안**: "이 함수를 더 simple하게 다시 써줘" — Claude vs Codex 다른 접근법 비교

## 비용 control
- o4-mini: ~$0.50/file (저렴, 빠름)
- o3: ~$2/file (deep reasoning)
- gpt-5: ~$1.50/file (balanced)
- gpt-4o: ~$0.30/file (cheapest)
