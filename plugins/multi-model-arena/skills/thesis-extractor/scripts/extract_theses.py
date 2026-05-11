#!/usr/bin/env python3
"""Thesis Extractor — 메르 블로그에서 핵심 주장 N개 추출 (OpenAI 또는 Gemini)."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "api-key-manager" / "scripts"))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "openai-worker" / "scripts"))
sys.path.insert(0, str(SCRIPTS_DIR.parent.parent / "gemini-worker" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config, mask

KST = timezone(timedelta(hours=9))


THESIS_SYSTEM = """You are an expert reader of Korean financial blogs (especially 메르/ranto28's posts).

Your task: extract the AUTHOR'S CLAIMS (theses), not stocks.

Rules:
1. Atomicity — one claim per thesis. Split compound sentences.
2. Type — classify each as: factual / predictive / normative / conditional
3. Importance — core / supporting / aside
   - core: the post's main argumentative pillars (typically 3-7)
   - supporting: facts that back up the core
   - aside: tangential remarks
4. Timeframe — historical / present / short_term / medium_term / long_term
5. Quote raw evidence verbatim from the body
6. Preserve the author's numbering (e.g., "원문 14번") if present
7. Add 1-3 tags per thesis (Korean preferred for Korean posts)

CRITICAL — what makes thesis extraction good:
- Don't paraphrase too aggressively; the claim must be falsifiable as stated
- Predictions like "X가 합리적 대안이 될 것" are predictive, not factual
- Normative claims (should/ought) are different from predictions
- If the post has a "한줄 코멘트" or summary, capture it as `summary_one_liner`

Return ONLY valid JSON. No prose."""


THESIS_USER_TEMPLATE = """Korean blog post:

Title: {title}
Author: {author}
Hashtags: {hashtags}

Body:
\"\"\"
{body}
\"\"\"

Required JSON schema:
{{
  "post_meta": {{"url":"{url}","title":"{title}","author":"{author}"}},
  "summary_one_liner": "글의 한 줄 요약. 메르의 '한줄 코멘트'가 있으면 그것을 우선.",
  "theses": [
    {{
      "claim_id": "T01",
      "claim": "한 문장으로 진술된 명제",
      "type": "factual|predictive|normative|conditional",
      "importance": "core|supporting|aside",
      "timeframe": "historical|present|short_term|medium_term|long_term",
      "supporting_evidence": "본문에서 인용한 raw text",
      "evidence_section": "원문 X번 형식 또는 비워둠",
      "tags": ["태그1", "태그2"]
    }}
  ]
}}

Output JSON only."""


def call_openai(api_key: str, model: str, fallback: str, reasoning: str | None,
                system: str, user: str) -> tuple[str, dict, str]:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    kwargs = {
        "model": model,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "response_format": {"type": "json_object"},
        "timeout": 300,
    }
    if reasoning and "5" in model.split("-")[0][-1:]:
        kwargs["reasoning_effort"] = reasoning

    try:
        r = client.chat.completions.create(**kwargs)
        used = model
    except Exception as e:
        msg = str(e).lower()
        if "reasoning_effort" in msg or "unknown parameter" in msg:
            kwargs.pop("reasoning_effort", None)
            r = client.chat.completions.create(**kwargs)
            used = model
        elif "model" in msg or "404" in msg:
            kwargs["model"] = fallback
            kwargs.pop("reasoning_effort", None)
            r = client.chat.completions.create(**kwargs)
            used = fallback
        else:
            raise

    return r.choices[0].message.content, {
        "prompt_tokens": r.usage.prompt_tokens,
        "completion_tokens": r.usage.completion_tokens,
    }, used


def call_gemini(api_key: str, model: str, fallback: str, deep_think: bool,
                system: str, user: str) -> tuple[str, dict, str]:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    config = {"temperature": 0.2, "response_mime_type": "application/json"}
    if deep_think:
        config["thinking_config"] = {"thinking_budget": -1}

    def _try(m):
        name = m if m.startswith("models/") else f"models/{m}"
        gm = genai.GenerativeModel(name, system_instruction=system, generation_config=config)
        return gm.generate_content(user)

    try:
        r = _try(model)
        used = model
    except Exception as e:
        msg = str(e).lower()
        if "thinking" in msg:
            config.pop("thinking_config", None)
            r = _try(model)
            used = model
        else:
            r = _try(fallback)
            used = fallback

    text = r.text
    usage = {
        "prompt_tokens": r.usage_metadata.prompt_token_count if r.usage_metadata else 0,
        "completion_tokens": r.usage_metadata.candidates_token_count if r.usage_metadata else 0,
        "thinking_tokens": getattr(r.usage_metadata, "thoughts_token_count", 0) if r.usage_metadata else 0,
    }
    return text, usage, used


def parse_json(content: str) -> dict:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```", 2)[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.rsplit("```", 1)[0]
        return json.loads(cleaned)


def main():
    parser = argparse.ArgumentParser(description="Thesis extractor")
    parser.add_argument("post_json")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--blog-url", default="")
    parser.add_argument("--provider", choices=["openai", "gemini", "auto"], default="auto",
                        help="auto = openai 우선, 실패 시 gemini")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()

    with open(args.post_json, encoding="utf-8") as f:
        post = json.load(f)
    body = post.get("content_text", "")[:50_000]
    blog_url = args.blog_url or post.get("url", "")

    user = THESIS_USER_TEMPLATE.format(
        title=post.get("title", ""),
        author=post.get("author", ""),
        hashtags=post.get("tags", []) or [],
        body=body,
        url=blog_url,
    )

    providers = ["openai", "gemini"] if args.provider == "auto" else [args.provider]

    last_err = None
    result = None
    used_model = ""
    usage = {}
    elapsed = 0.0

    for prov in providers:
        try:
            start = time.time()
            if prov == "openai":
                key = get_key("OPENAI_API_KEY", required=True)
                content, usage, used_model = call_openai(
                    key, cfg["openai"]["model"], cfg["openai"]["fallback"],
                    cfg["openai"]["reasoning_effort"], THESIS_SYSTEM, user
                )
            else:
                key = get_key("GOOGLE_API_KEY", required=True)
                content, usage, used_model = call_gemini(
                    key, cfg["google"]["model"], cfg["google"]["fallback"],
                    cfg["google"]["deep_think"], THESIS_SYSTEM, user
                )
            elapsed = time.time() - start
            result = parse_json(content)
            print(f"[thesis-extract] {prov} 성공: model={used_model}, {elapsed:.1f}s", file=sys.stderr)
            break
        except Exception as e:
            last_err = e
            print(f"[thesis-extract] {prov} 실패: {e}", file=sys.stderr)

    if result is None:
        raise SystemExit(f"모든 provider 실패: {last_err}")

    # Meta 보강
    if "post_meta" not in result:
        result["post_meta"] = {}
    result["post_meta"].setdefault("url", blog_url)
    result["post_meta"].setdefault("title", post.get("title", ""))
    result["post_meta"].setdefault("author", post.get("author", ""))

    theses = result.get("theses", [])
    n_core = sum(1 for t in theses if t.get("importance") == "core")
    n_supp = sum(1 for t in theses if t.get("importance") == "supporting")
    n_aside = sum(1 for t in theses if t.get("importance") == "aside")

    result["extraction_meta"] = {
        "extracted_at": datetime.now(KST).isoformat(),
        "model": used_model,
        "provider": providers[0] if result is not None else "unknown",
        "n_total": len(theses),
        "n_core": n_core,
        "n_supporting": n_supp,
        "n_aside": n_aside,
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "thinking_tokens": usage.get("thinking_tokens", 0),
        "elapsed_seconds": round(elapsed, 2),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[thesis-extract] 완료")
    print(f"  모델: {used_model}")
    print(f"  thesis: {len(theses)}개 (core={n_core}, supp={n_supp}, aside={n_aside})")
    print(f"  소요: {elapsed:.1f}s")
    print(f"  저장: {args.output}")


if __name__ == "__main__":
    main()
