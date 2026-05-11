#!/usr/bin/env python3
"""Persona Evaluator — 단일 (ticker, persona) 평가."""
import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

# 경로 설정
SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent  # plugins/investor-personas/
ARENA_PLUGIN = PLUGIN_ROOT.parent / "multi-model-arena"

sys.path.insert(0, str(ARENA_PLUGIN / "skills" / "api-key-manager" / "scripts"))
sys.path.insert(0, str(ARENA_PLUGIN / "skills" / "thesis-extractor" / "scripts"))

from api_key_manager import load_env, get_key, get_model_config, mask
from extract_theses import call_openai, call_gemini, parse_json

KST = timezone(timedelta(hours=9))


PERSONA_DIR = PLUGIN_ROOT / "personas"


def load_persona(persona_id: str) -> tuple[str, dict]:
    """페르소나 SKILL.md 로드. (raw_text, frontmatter)."""
    p = PERSONA_DIR / persona_id / "SKILL.md"
    if not p.exists():
        # 일부 폴더명이 다를 수 있음 (예: warren-buffett → warren_buffett)
        alt = PERSONA_DIR / persona_id.replace("_", "-") / "SKILL.md"
        if alt.exists():
            p = alt
        else:
            available = [d.name for d in PERSONA_DIR.iterdir() if d.is_dir()]
            raise SystemExit(f"페르소나 미발견: {persona_id}. 사용 가능: {available}")

    raw = p.read_text(encoding="utf-8")
    # Frontmatter 파싱 (간단한 YAML)
    fm = {}
    if raw.startswith("---"):
        end = raw.find("---", 3)
        front = raw[3:end].strip()
        for line in front.split("\n"):
            if ":" in line and not line.lstrip().startswith("#"):
                k, v = line.split(":", 1)
                fm[k.strip()] = v.strip().strip("\"'")
    return raw, fm


SYSTEM_TEMPLATE = """You are evaluating a stock through a specific investor persona's lens.

The persona's full SKILL.md is below. Follow its Required Analysis Sequence step-by-step.
Apply Decision Rules to reach a verdict. Honor Anti-Hallucination Rules — every number must be tagged
[actual] / [estimated] / [assumption] / [derived] / [unavailable].

=== PERSONA SKILL.md ===
{persona_skill}
=== END PERSONA ===

=== 의무 평가 절차 (THESIS-AWARE QUANT ANCHORING) ===

평가 시 다음 3단계를 의무적으로 수행하고 출력에 명시:

STEP 1 — Thesis별 lens 적용:
블로거가 제시한 thesis (T01, T02, ...) 각각에 대해 당신의 페르소나 lens에서
어떻게 해석되는지 명시. 본문에 thesis가 명시되어 있지 않으면 본문 핵심 주장을
스스로 식별하고 그것을 'implicit_thesis'로 기록.

STEP 2 — 정량 anchor와 thesis 정합:
시장 정량 데이터(PE, ROE, FCF margin, 변동성 등) 중 어느 metric이 어느 thesis를
강화/약화하는지 명시. 정량 = narrative의 검증 도구로 활용.

STEP 3 — 정량 vs narrative 충돌 처리:
정량 신호와 narrative가 충돌할 때 당신의 페르소나는 어느 것을 더 무겁게 가중하는가?
이는 페르소나 정체성을 반영해야 함:
- Buffett: margin of safety (정량) > narrative
- Cathie Wood: TAM·growth narrative > 단기 정량
- Druckenmiller: macro tailwind narrative > micro 정량
- Damodaran: story와 numbers의 일관성 강제

Output ONLY valid JSON in the exact schema requested."""


USER_TEMPLATE = """Ticker: {ticker}

Market data:
{market_data}

{blog_context_block}

Required JSON schema (must be followed exactly):
{{
  "ticker": "{ticker}",
  "persona_kr": "{persona_kr}",
  "persona_en": "{persona_en}",
  "verdict": "lean_bullish | lean_bearish | neutral",
  "confidence": 0.0,
  "horizon": "long_term | medium_term | short_term",
  "stage_results": [
    {{
      "stage_num": 1,
      "stage_name": "name from SKILL.md sequence",
      "passed": true,
      "rationale": "2-4 sentences in Korean",
      "data_tags": ["[actual] ...", "[inference] ..."]
    }}
  ],
  "thesis_lens_applications": [
    {{
      "claim_id": "T01 또는 implicit",
      "claim_text": "thesis 짧은 인용",
      "persona_take": "본 페르소나 lens에서 해석",
      "stance": "support | challenge | neutral"
    }}
  ],
  "quant_anchor_validation": [
    {{"metric": "예: forward_pe 3.76", "supports_or_challenges": "T03을 support", "tag": "[actual]"}}
  ],
  "narrative_vs_quant_resolution": "충돌 시 페르소나 정체성에 따른 우선순위",
  "key_concerns": ["우려 1", "우려 2"],
  "key_opportunities": ["기회 1", "기회 2"],
  "uncertainty_acknowledged": "어떤 가정이 깨지면 verdict가 뒤집히는가"
}}

Apply this persona's lens authentically — not generic value investing. Output JSON only.
"""


# Approximate cost per million tokens (USD) — sync with openai-worker
COST = {
    "openai": {
        "gpt-5.5": {"input": 10.00, "output": 40.00},
        "gpt-4.1": {"input": 2.50, "output": 10.00},
    },
    "google": {
        "gemini-3.1": {"input": 5.00, "output": 20.00},
        "gemini-2.5-pro": {"input": 1.25, "output": 10.00},
    },
}


def estimate_cost(provider: str, model: str, in_tok: int, out_tok: int) -> float:
    rate = COST.get(provider, {}).get(model, {"input": 2.0, "output": 8.0})
    return (in_tok * rate["input"] + out_tok * rate["output"]) / 1_000_000


def main():
    parser = argparse.ArgumentParser(description="단일 종목 × 단일 페르소나 평가")
    parser.add_argument("ticker")
    parser.add_argument("persona", help="persona ID (예: warren-buffett)")
    parser.add_argument("--market", required=True)
    parser.add_argument("--post", help="블로그 컨텍스트 JSON (옵션)")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--provider", choices=["openai", "gemini"], default="openai")
    args = parser.parse_args()

    load_env()
    cfg = get_model_config()

    # Persona 로드
    skill_text, fm = load_persona(args.persona)
    persona_kr = fm.get("name_kr", args.persona)
    persona_en = fm.get("name", args.persona).replace("-", " ").title()

    # Market data
    with open(args.market, encoding="utf-8") as f:
        market = json.load(f)
    market_str = json.dumps(market, ensure_ascii=False, indent=2)

    # Blog context (옵션)
    blog_block = ""
    if args.post:
        with open(args.post, encoding="utf-8") as f:
            post = json.load(f)
        body = post.get("content_text", "")[:8000]
        blog_block = f"""Blog context (Korean — investment thesis source):
URL: {post.get('url', '')}
Title: {post.get('title', '')}
Author: {post.get('author', '')}

Body excerpt:
\"\"\"
{body}
\"\"\"
"""

    system = SYSTEM_TEMPLATE.format(persona_skill=skill_text)
    user = USER_TEMPLATE.format(
        ticker=args.ticker, market_data=market_str,
        blog_context_block=blog_block,
        persona_kr=persona_kr, persona_en=persona_en,
    )

    start = time.time()
    if args.provider == "openai":
        api_key = get_key("OPENAI_API_KEY", required=True)
        content, usage, used = call_openai(
            api_key, cfg["openai"]["model"], cfg["openai"]["fallback"],
            cfg["openai"]["reasoning_effort"], system, user
        )
    else:
        api_key = get_key("GOOGLE_API_KEY", required=True)
        content, usage, used = call_gemini(
            api_key, cfg["google"]["model"], cfg["google"]["fallback"],
            cfg["google"]["deep_think"], system, user
        )
    elapsed = time.time() - start

    result = parse_json(content)
    cost = estimate_cost(args.provider, used,
                         usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0))

    result["evaluated_at"] = datetime.now(KST).isoformat()
    result["_meta"] = {
        "model_provider": args.provider,
        "model_used": used,
        "key_masked": mask(api_key),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "thinking_tokens": usage.get("thinking_tokens", 0),
        "estimated_cost_usd": round(cost, 4),
        "elapsed_seconds": round(elapsed, 2),
        "persona_id": args.persona,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"[persona-eval] {args.ticker} × {persona_kr}")
    print(f"  verdict: {result.get('verdict')} (conf {result.get('confidence', 0)})")
    print(f"  model: {used}, ${cost:.4f}, {elapsed:.1f}s")
    print(f"  saved: {args.output}")


if __name__ == "__main__":
    main()
