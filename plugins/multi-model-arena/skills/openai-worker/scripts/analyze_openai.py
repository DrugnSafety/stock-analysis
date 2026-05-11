#!/usr/bin/env python3
"""OpenAI GPT-5.5 7-role 분석 worker."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "api-key-manager" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config, mask
from _prompts import ANALYZE_SYSTEM, ANALYZE_USER_TEMPLATE
from extract_openai import call_openai, estimate_cost

KST = timezone(timedelta(hours=9))


def main():
    parser = argparse.ArgumentParser(description="OpenAI 7-role 분석 worker")
    parser.add_argument("ticker", help="분석할 ticker (예: 439260.KS)")
    parser.add_argument("--market", required=True, help="market_data.py 출력 JSON")
    parser.add_argument("--post", help="naver-blog-scraper 출력 (블로그 컨텍스트용)")
    parser.add_argument("--output", "-o", required=True, help="결과 저장 경로")
    parser.add_argument("--blog-url", help="원본 블로그 URL")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()
    api_key = get_key("OPENAI_API_KEY", required=True)

    # 시장 데이터 로드
    with open(args.market, encoding="utf-8") as f:
        market = json.load(f)
    market_str = json.dumps(market, ensure_ascii=False, indent=2)

    # 블로그 컨텍스트
    blog_block = ""
    if args.post:
        with open(args.post, encoding="utf-8") as f:
            post = json.load(f)
        blog_url = args.blog_url or post.get("url", "")
        body = post.get("content_text", "")[:6000]
        blog_block = f"""Blog context (Korean — the post that motivated this analysis):
URL: {blog_url}
Title: {post.get('title', '')}
Author: {post.get('author', '')}

Body excerpt:
\"\"\"
{body}
\"\"\"

Use this as supplementary context. Cite the post when bull/bear thesis depends on it.
"""

    user_prompt = ANALYZE_USER_TEMPLATE.format(
        ticker=args.ticker,
        market_data=market_str,
        blog_context_block=blog_block,
    )

    from openai import OpenAI
    client = OpenAI(api_key=api_key)

    model = cfg["openai"]["model"]
    fallback = cfg["openai"]["fallback"]
    reasoning = cfg["openai"]["reasoning_effort"]

    messages = [
        {"role": "system", "content": ANALYZE_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    start = time.time()
    try:
        content, usage = call_openai(client, model, messages, reasoning)
        model_used = model
    except Exception as e:
        print(f"[openai-worker] {model} 실패, fallback {fallback}: {e}", file=sys.stderr)
        content, usage = call_openai(client, fallback, messages, None)
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

    cost = estimate_cost(model_used, usage["prompt_tokens"], usage["completion_tokens"])
    result["_meta"] = {
        "model_provider": "openai",
        "model_used": model_used,
        "key_masked": mask(api_key),
        "reasoning_effort": reasoning,
        "prompt_tokens": usage["prompt_tokens"],
        "completion_tokens": usage["completion_tokens"],
        "estimated_cost_usd": round(cost, 4),
        "elapsed_seconds": round(elapsed, 2),
        "called_at": datetime.now(KST).isoformat(),
        "market_data": market,  # 추적용
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[openai-worker] 분석 완료")
    print(f"  ticker: {args.ticker}")
    print(f"  verdict: {result.get('verdict')} (conf {result.get('confidence', 0)})")
    print(f"  모델: {model_used}")
    print(f"  토큰: in={usage['prompt_tokens']}, out={usage['completion_tokens']}")
    print(f"  비용: ${cost:.4f}")
    print(f"  소요: {elapsed:.1f}s")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
