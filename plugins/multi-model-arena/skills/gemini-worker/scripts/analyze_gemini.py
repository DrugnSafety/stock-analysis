#!/usr/bin/env python3
"""Google Gemini 3.1 7-role 분석 worker."""
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
from _prompts import ANALYZE_SYSTEM, ANALYZE_USER_TEMPLATE
from extract_gemini import call_gemini, estimate_cost

KST = timezone(timedelta(hours=9))


def main():
    parser = argparse.ArgumentParser(description="Gemini 7-role 분석 worker")
    parser.add_argument("ticker")
    parser.add_argument("--market", required=True)
    parser.add_argument("--post")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--blog-url")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()
    api_key = get_key("GOOGLE_API_KEY", required=True)

    with open(args.market, encoding="utf-8") as f:
        market = json.load(f)
    market_str = json.dumps(market, ensure_ascii=False, indent=2)

    blog_block = ""
    if args.post:
        with open(args.post, encoding="utf-8") as f:
            post = json.load(f)
        blog_url = args.blog_url or post.get("url", "")
        body = post.get("content_text", "")[:50_000]  # Gemini context 충분
        blog_block = f"""Blog context (Korean):
URL: {blog_url}
Title: {post.get('title', '')}
Author: {post.get('author', '')}

Body:
\"\"\"
{body}
\"\"\"
"""

    user_prompt = ANALYZE_USER_TEMPLATE.format(
        ticker=args.ticker, market_data=market_str, blog_context_block=blog_block
    )

    model = cfg["google"]["model"]
    fallback = cfg["google"]["fallback"]
    deep_think = cfg["google"]["deep_think"]

    start = time.time()
    try:
        content, usage = call_gemini(api_key, model, ANALYZE_SYSTEM, user_prompt, deep_think)
        model_used = model
    except Exception as e:
        print(f"[gemini-worker] {model} 실패, fallback {fallback}: {e}", file=sys.stderr)
        content, usage = call_gemini(api_key, fallback, ANALYZE_SYSTEM, user_prompt, False)
        model_used = fallback
    elapsed = time.time() - start

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

    cost = estimate_cost(
        model_used, usage["prompt_tokens"], usage["completion_tokens"], usage.get("thinking_tokens", 0)
    )
    result["_meta"] = {
        "model_provider": "google",
        "model_used": model_used,
        "key_masked": mask(api_key),
        "deep_think": deep_think,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "thinking_tokens": usage.get("thinking_tokens", 0),
        "estimated_cost_usd": round(cost, 4),
        "elapsed_seconds": round(elapsed, 2),
        "called_at": datetime.now(KST).isoformat(),
        "market_data": market,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[gemini-worker] 분석 완료")
    print(f"  ticker: {args.ticker}")
    print(f"  verdict: {result.get('verdict')} (conf {result.get('confidence', 0)})")
    print(f"  모델: {model_used}")
    print(f"  토큰: in={usage['prompt_tokens']}, out={usage['completion_tokens']}, think={usage.get('thinking_tokens', 0)}")
    print(f"  비용: ${cost:.4f}")
    print(f"  소요: {elapsed:.1f}s")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
