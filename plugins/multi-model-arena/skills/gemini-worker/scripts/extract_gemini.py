#!/usr/bin/env python3
"""Google Gemini 3.1 종목 추출 worker."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "api-key-manager" / "scripts"))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "openai-worker" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config, mask
from _prompts import EXTRACT_SYSTEM, EXTRACT_USER_TEMPLATE

KST = timezone(timedelta(hours=9))


# Approximate Gemini pricing (USD per million tokens)
COST_PER_M_TOKENS = {
    "gemini-3.1": {"input": 5.00, "output": 20.00, "thinking": 20.00},
    "gemini-3.1-flash": {"input": 0.30, "output": 1.20, "thinking": 1.20},
    "gemini-2.5-pro": {"input": 1.25, "output": 10.00, "thinking": 10.00},
    "gemini-2.5-flash": {"input": 0.10, "output": 0.40, "thinking": 0.40},
}


def estimate_cost(model: str, input_tok: int, output_tok: int, thinking_tok: int = 0) -> float:
    rate = COST_PER_M_TOKENS.get(model, COST_PER_M_TOKENS["gemini-2.5-pro"])
    return (
        input_tok * rate["input"]
        + output_tok * rate["output"]
        + thinking_tok * rate["thinking"]
    ) / 1_000_000


def call_gemini(api_key: str, model: str, system: str, user: str, deep_think: bool) -> tuple[str, dict]:
    """Gemini API 호출 + thinking 모드 자동 fallback."""
    import google.generativeai as genai

    genai.configure(api_key=api_key)

    config = {
        "temperature": 0.2,
        "response_mime_type": "application/json",
    }

    # Deep think (thinking budget) 시도
    if deep_think:
        config["thinking_config"] = {"thinking_budget": -1}  # auto

    # 모델 매칭 (Gemini 모델명은 'models/' 접두사 가능)
    model_name = model if model.startswith("models/") else f"models/{model}"

    try:
        m = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system,
            generation_config=config,
        )
        response = m.generate_content(user)
    except Exception as e:
        msg = str(e).lower()
        if "thinking_config" in msg or "unknown" in msg:
            config.pop("thinking_config", None)
            m = genai.GenerativeModel(
                model_name=model_name,
                system_instruction=system,
                generation_config=config,
            )
            response = m.generate_content(user)
        else:
            raise

    text = response.text
    usage = {
        "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
        "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
        "thinking_tokens": getattr(response.usage_metadata, "thoughts_token_count", 0) if response.usage_metadata else 0,
    }
    return text, usage


def main():
    parser = argparse.ArgumentParser(description="Gemini 종목 추출 worker")
    parser.add_argument("post_json")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--blog-url")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()
    api_key = get_key("GOOGLE_API_KEY", required=True)

    with open(args.post_json, encoding="utf-8") as f:
        post = json.load(f)

    body = post.get("content_text", "")[:100_000]  # Gemini는 큰 context 가능
    user_prompt = EXTRACT_USER_TEMPLATE.format(
        title=post.get("title", ""),
        author=post.get("author", ""),
        hashtags=post.get("tags", []) or [],
        body=body,
    )

    model = cfg["google"]["model"]
    fallback = cfg["google"]["fallback"]
    deep_think = cfg["google"]["deep_think"]

    start = time.time()
    try:
        content, usage = call_gemini(api_key, model, EXTRACT_SYSTEM, user_prompt, deep_think)
        model_used = model
    except Exception as e:
        print(f"[gemini-worker] {model} 실패, fallback {fallback}: {e}", file=sys.stderr)
        content, usage = call_gemini(api_key, fallback, EXTRACT_SYSTEM, user_prompt, False)
        model_used = fallback
    elapsed = time.time() - start

    # JSON 파싱
    try:
        result = json.loads(content)
    except json.JSONDecodeError:
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
    result["post_meta"]["url"] = args.blog_url or post.get("url", "")
    result["post_meta"].setdefault("title", post.get("title", ""))
    result["post_meta"].setdefault("author", post.get("author", ""))
    result["post_meta"].setdefault("hashtags", post.get("tags", []) or [])

    cost = estimate_cost(
        model_used, usage["prompt_tokens"], usage["completion_tokens"], usage.get("thinking_tokens", 0)
    )
    result["extraction_meta"] = {
        "extracted_at": datetime.now(KST).isoformat(),
        "mode": "gemini_worker",
        "model": model_used,
        "provider": "google",
        "key_masked": mask(api_key),
        "deep_think": deep_think,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "thinking_tokens": usage.get("thinking_tokens", 0),
        "estimated_cost_usd": round(cost, 4),
        "elapsed_seconds": round(elapsed, 2),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[gemini-worker] 추출 완료")
    print(f"  모델: {model_used}")
    print(f"  회사: {len(result.get('companies', []))}")
    print(f"  ETF: {len(result.get('etfs', []))}")
    print(f"  토큰: in={usage['prompt_tokens']}, out={usage['completion_tokens']}, think={usage.get('thinking_tokens', 0)}")
    print(f"  비용: ${cost:.4f}")
    print(f"  소요: {elapsed:.1f}s")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
