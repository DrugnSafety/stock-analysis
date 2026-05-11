#!/usr/bin/env python3
"""OpenAI GPT-5.5 종목 추출 worker."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Allow importing from sibling skill
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "api-key-manager" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config, mask
from _prompts import EXTRACT_SYSTEM, EXTRACT_USER_TEMPLATE

KST = timezone(timedelta(hours=9))


# Approximate cost per million tokens (USD) — adjust per OpenAI pricing
COST_PER_M_TOKENS = {
    "gpt-5.5": {"input": 10.00, "output": 40.00},
    "gpt-5.5-mini": {"input": 1.50, "output": 6.00},
    "o3": {"input": 60.00, "output": 240.00},
    "gpt-4.1": {"input": 2.50, "output": 10.00},
    "gpt-4.1-mini": {"input": 0.15, "output": 0.60},
}


def estimate_cost(model: str, prompt_tokens: int, completion_tokens: int) -> float:
    rate = COST_PER_M_TOKENS.get(model, COST_PER_M_TOKENS["gpt-4.1"])
    return (prompt_tokens * rate["input"] + completion_tokens * rate["output"]) / 1_000_000


def call_openai(client, model: str, messages: list, reasoning_effort: str | None) -> tuple[str, dict]:
    """OpenAI API 호출 + reasoning 모드 자동 fallback."""
    kwargs = {"model": model, "messages": messages}

    # GPT-5.5+: reasoning_effort 시도
    if reasoning_effort and "5" in model.split("-")[0][-1]:
        kwargs["reasoning_effort"] = reasoning_effort

    # Force JSON
    kwargs["response_format"] = {"type": "json_object"}

    try:
        response = client.chat.completions.create(**kwargs)
    except Exception as e:
        # 일부 옵션 미지원 시 단계적 제거
        msg = str(e).lower()
        if "reasoning_effort" in msg or "unknown parameter" in msg:
            kwargs.pop("reasoning_effort", None)
            response = client.chat.completions.create(**kwargs)
        else:
            raise

    content = response.choices[0].message.content
    usage = response.usage
    return content, {
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
    }


def main():
    parser = argparse.ArgumentParser(description="OpenAI 종목 추출 worker")
    parser.add_argument("post_json", help="naver-blog-scraper의 출력 JSON 경로")
    parser.add_argument("--output", "-o", required=True, help="결과 저장 경로")
    parser.add_argument("--blog-url", help="원본 블로그 URL (메타에 포함)")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()
    api_key = get_key("OPENAI_API_KEY", required=True)

    # 입력 로드
    with open(args.post_json, encoding="utf-8") as f:
        post = json.load(f)

    body = post.get("content_text", "")[:20_000]  # 입력 토큰 제한
    title = post.get("title", "")
    author = post.get("author", "")
    hashtags = post.get("tags", [])
    blog_url = args.blog_url or post.get("url", "")

    user_prompt = EXTRACT_USER_TEMPLATE.format(
        title=title, author=author, hashtags=hashtags or [], body=body
    )

    # OpenAI 호출
    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    model = cfg["openai"]["model"]
    fallback = cfg["openai"]["fallback"]
    reasoning = cfg["openai"]["reasoning_effort"]

    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    start = time.time()
    try:
        content, usage = call_openai(client, model, messages, reasoning)
        model_used = model
    except Exception as e:
        print(f"[openai-worker] {model} 실패, fallback {fallback} 시도: {e}", file=sys.stderr)
        content, usage = call_openai(client, fallback, messages, None)
        model_used = fallback
    elapsed = time.time() - start

    # JSON 파싱
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        # 마크다운 ```json``` 블록 제거 시도
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0]
        result = json.loads(cleaned)

    # post_meta 보강
    if "post_meta" not in result:
        result["post_meta"] = {}
    result["post_meta"]["url"] = blog_url
    result["post_meta"].setdefault("title", title)
    result["post_meta"].setdefault("author", author)
    result["post_meta"].setdefault("hashtags", hashtags or [])

    # 메타 추가
    cost = estimate_cost(model_used, usage["prompt_tokens"], usage["completion_tokens"])
    result["extraction_meta"] = {
        "extracted_at": datetime.now(KST).isoformat(),
        "mode": "openai_worker",
        "model": model_used,
        "provider": "openai",
        "key_masked": mask(api_key),
        "reasoning_effort": reasoning,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "estimated_cost_usd": round(cost, 4),
        "elapsed_seconds": round(elapsed, 2),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[openai-worker] 추출 완료")
    print(f"  모델: {model_used}")
    print(f"  회사: {len(result.get('companies', []))}")
    print(f"  ETF: {len(result.get('etfs', []))}")
    print(f"  토큰: in={usage['prompt_tokens']}, out={usage['completion_tokens']}")
    print(f"  비용: ${cost:.4f}")
    print(f"  소요: {elapsed:.1f}s")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
