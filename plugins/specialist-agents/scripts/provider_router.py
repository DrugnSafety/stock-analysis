#!/usr/bin/env python3
"""Provider Router — Multi-LLM cost-optimized routing (TradingAgents 0.2.4 pattern).

Routes LLM calls to the cheapest sufficient model based on task complexity.

Cost tier (per 1M tokens, May 2026 approximate):
  - tier_cheap   (~$0.10-0.30/M):  DeepSeek-V3, Qwen-Plus, GLM-4.5
  - tier_mid     (~$1-3/M):         Claude Haiku 4.5, gpt-4o-mini, Gemini 2.5 Flash
  - tier_premium (~$10-15/M):       Claude Opus 4, gpt-5, Gemini 2.5 Pro

Task → tier routing (default policy):
  - debate_cycle (Bull/Bear/Skeptic rounds) → tier_cheap (high volume, low stakes per call)
  - sentiment_aggregation                  → tier_cheap (deterministic mostly)
  - thesis_extraction                      → tier_mid (structured but needs reasoning)
  - persona_evaluation (13 personas)       → tier_mid (parallel, moderate stakes)
  - final_synthesis (verdict_consolidation) → tier_premium (high stakes, single call)
  - report_writing (executive summary)      → tier_premium (quality matters)

Override with env vars:
  ROUTER_FORCE_PROVIDER=anthropic|openai|google|deepseek|qwen|glm
  ROUTER_OVERRIDE_TIER=cheap|mid|premium
"""
from __future__ import annotations
import os
from typing import Optional


PROVIDER_MODELS = {
    "tier_cheap": {
        "deepseek": "deepseek-chat",
        "qwen": "qwen-plus",
        "glm": "glm-4.5",
        "openai": "gpt-4o-mini",
    },
    "tier_mid": {
        "anthropic": "claude-haiku-4-5-20251001",
        "openai": "gpt-4o",
        "google": "gemini-2.5-flash",
    },
    "tier_premium": {
        "anthropic": "claude-opus-4-7",
        "openai": "gpt-5",
        "google": "gemini-2.5-pro",
    },
}

# Task → tier default mapping
TASK_TIER_MAP = {
    "debate_cycle": "tier_cheap",
    "sentiment_aggregation": "tier_cheap",
    "news_summary": "tier_cheap",
    "thesis_extraction": "tier_mid",
    "thesis_evaluation": "tier_mid",
    "persona_evaluation": "tier_mid",
    "deep_research_synthesis": "tier_mid",
    "final_synthesis": "tier_premium",
    "verdict_consolidation": "tier_premium",
    "executive_summary": "tier_premium",
    "report_writing": "tier_premium",
}


def route(task: str, preferred_provider: Optional[str] = None) -> dict:
    """Return {provider, model, tier} for the given task.

    Args:
        task: One of TASK_TIER_MAP keys.
        preferred_provider: Optional override. If set + available API key, use it.

    Returns:
        dict with provider, model_name, tier, api_key_present
    """
    # Override via env
    force_provider = os.environ.get("ROUTER_FORCE_PROVIDER")
    override_tier = os.environ.get("ROUTER_OVERRIDE_TIER")

    tier = override_tier or TASK_TIER_MAP.get(task, "tier_mid")
    if not tier.startswith("tier_"):
        tier = f"tier_{tier}"

    candidates = PROVIDER_MODELS.get(tier, {})

    # Priority: forced > preferred > first with API key > first available
    provider_priority = []
    if force_provider and force_provider in candidates:
        provider_priority.append(force_provider)
    if preferred_provider and preferred_provider in candidates:
        provider_priority.append(preferred_provider)
    provider_priority.extend(candidates.keys())

    # Find first with API key
    for p in provider_priority:
        key_name = _api_key_env_name(p)
        if os.environ.get(key_name):
            return {
                "provider": p,
                "model": candidates[p],
                "tier": tier,
                "api_key_env": key_name,
                "api_key_present": True,
            }

    # Fall back to first candidate even without key (caller decides)
    first = list(candidates.keys())[0] if candidates else "anthropic"
    return {
        "provider": first,
        "model": candidates.get(first, "claude-opus-4-7"),
        "tier": tier,
        "api_key_env": _api_key_env_name(first),
        "api_key_present": False,
    }


def _api_key_env_name(provider: str) -> str:
    return {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
        "qwen": "QWEN_API_KEY",
        "glm": "GLM_API_KEY",
    }.get(provider, f"{provider.upper()}_API_KEY")


def estimate_cost_savings(task_breakdown: dict, default_tier: str = "tier_premium") -> dict:
    """Estimate cost vs. always using premium tier.

    Args:
        task_breakdown: {task_name: n_calls}

    Returns:
        Estimated savings dict.
    """
    # Approximate $/M tokens (May 2026)
    tier_cost = {
        "tier_cheap": 0.20,
        "tier_mid": 2.50,
        "tier_premium": 12.50,
    }
    avg_tokens_per_call = 5000  # generous estimate

    naive_cost = 0
    routed_cost = 0
    for task, n in task_breakdown.items():
        tokens = n * avg_tokens_per_call
        routed_tier = TASK_TIER_MAP.get(task, "tier_mid")
        naive_cost += tokens / 1e6 * tier_cost[default_tier]
        routed_cost += tokens / 1e6 * tier_cost[routed_tier]

    return {
        "naive_cost_usd": round(naive_cost, 2),
        "routed_cost_usd": round(routed_cost, 2),
        "savings_usd": round(naive_cost - routed_cost, 2),
        "savings_pct": round((1 - routed_cost / naive_cost) * 100, 1) if naive_cost else 0,
    }


if __name__ == "__main__":
    import json
    print("=== Provider Router Demo (assuming all keys present) ===\n")
    sample_tasks = ["debate_cycle", "thesis_evaluation", "persona_evaluation",
                    "final_synthesis", "executive_summary"]
    for t in sample_tasks:
        r = route(t)
        print(f"  {t:30s} → {r['tier']:15s} {r['provider']:10s} {r['model']}")

    print("\n=== Cost Savings Estimate (typical analysis run) ===")
    breakdown = {
        "debate_cycle": 60,
        "sentiment_aggregation": 5,
        "thesis_extraction": 1,
        "thesis_evaluation": 60,    # 15 thesis × 4 analyst
        "persona_evaluation": 65,    # 5 stocks × 13 personas
        "deep_research_synthesis": 5,
        "final_synthesis": 5,
        "executive_summary": 1,
    }
    savings = estimate_cost_savings(breakdown)
    print(json.dumps(savings, indent=2))
