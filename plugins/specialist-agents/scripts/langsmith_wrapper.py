#!/usr/bin/env python3
"""LangSmith Tracing Wrapper — graceful no-op if langsmith not installed.

Wraps Anthropic/OpenAI/Gemini API calls with `@traceable` so every LLM call
in our analysis pipeline appears in LangSmith UI.

Usage:
    from langsmith_wrapper import traced_call, init_langsmith

    init_langsmith()  # idempotent; reads env vars

    @traced_call(name="thesis_evaluation", run_type="llm")
    def evaluate_thesis(thesis, analyst):
        ...

Env vars (set in .env):
    LANGSMITH_TRACING=true
    LANGSMITH_API_KEY=lsv2_pt_...
    LANGSMITH_PROJECT=stock-analysis
    LANGSMITH_ENDPOINT=https://api.smith.langchain.com  (default)

If LANGSMITH_TRACING != "true" or langsmith package not installed,
all decorators become no-ops (no overhead).
"""
from __future__ import annotations
import os
import functools
from typing import Any, Callable, Optional


_LANGSMITH_INITIALIZED = False
_LANGSMITH_AVAILABLE = False


def init_langsmith() -> bool:
    """Idempotent init. Returns True if tracing is active."""
    global _LANGSMITH_INITIALIZED, _LANGSMITH_AVAILABLE
    if _LANGSMITH_INITIALIZED:
        return _LANGSMITH_AVAILABLE

    _LANGSMITH_INITIALIZED = True

    if os.environ.get("LANGSMITH_TRACING", "").lower() not in ("true", "1", "yes"):
        return False

    if not os.environ.get("LANGSMITH_API_KEY"):
        print("[langsmith] LANGSMITH_API_KEY not set — tracing disabled")
        return False

    try:
        # Ensure project is set
        os.environ.setdefault("LANGSMITH_PROJECT", "default")
        # Also set LANGCHAIN_* aliases for legacy code paths
        os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
        os.environ.setdefault("LANGCHAIN_API_KEY", os.environ["LANGSMITH_API_KEY"])
        os.environ.setdefault("LANGCHAIN_PROJECT", os.environ["LANGSMITH_PROJECT"])

        # Try import (lazy)
        from langsmith import traceable as _traceable  # noqa: F401
        _LANGSMITH_AVAILABLE = True
        print(f"[langsmith] tracing → project '{os.environ.get('LANGSMITH_PROJECT')}'")
        return True
    except ImportError:
        print("[langsmith] langsmith package not installed (pip install langsmith) — tracing disabled")
        return False
    except Exception as e:
        print(f"[langsmith] init failed: {e}")
        return False


def traced_call(name: Optional[str] = None,
                run_type: str = "llm",
                metadata: Optional[dict] = None) -> Callable:
    """Decorator that wraps a function with langsmith.traceable when available.

    Args:
        name: display name in LangSmith UI (default: function name)
        run_type: 'llm' | 'chain' | 'tool' | 'retriever' | 'embedding' | 'parser'
        metadata: dict of static metadata attached to every trace
    """
    def decorator(func: Callable) -> Callable:
        if not init_langsmith():
            return func

        try:
            from langsmith import traceable
            return traceable(
                name=name or func.__name__,
                run_type=run_type,
                metadata=metadata or {},
            )(func)
        except Exception:
            return func

    return decorator


def log_run_metadata(**kwargs) -> None:
    """Manually attach metadata to current trace (no-op if no active run).

    Useful for attaching ticker, persona_id, thesis_id mid-execution.
    """
    if not init_langsmith():
        return
    try:
        from langsmith import get_current_run_tree
        run = get_current_run_tree()
        if run is not None:
            run.extra = run.extra or {}
            run.extra.setdefault("metadata", {}).update(kwargs)
    except Exception:
        pass


def estimate_session_cost() -> dict:
    """Pull current LangSmith project's cost via REST API (last 30d)."""
    if not init_langsmith():
        return {"status": "tracing_disabled"}
    try:
        import requests
        endpoint = os.environ.get("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        api_key = os.environ["LANGSMITH_API_KEY"]
        project = os.environ.get("LANGSMITH_PROJECT", "default")
        # Use Runs Stats endpoint
        url = f"{endpoint}/api/v1/runs/stats"
        params = {"session": project, "is_root": "true"}
        r = requests.get(url, headers={"x-api-key": api_key}, params=params, timeout=10)
        if r.status_code == 200:
            return r.json()
        return {"status": "error", "code": r.status_code, "body": r.text[:200]}
    except Exception as e:
        return {"status": "exception", "error": str(e)}


if __name__ == "__main__":
    # Demo / smoke test
    print("=== LangSmith Wrapper Smoke Test ===")
    active = init_langsmith()
    print(f"Active: {active}")
    if active:
        print(f"Project: {os.environ.get('LANGSMITH_PROJECT')}")
        print(f"Endpoint: {os.environ.get('LANGSMITH_ENDPOINT')}")

    @traced_call(name="smoke_test_func", run_type="chain")
    def add(a, b):
        return a + b

    result = add(2, 3)
    print(f"add(2,3) = {result}")
    print(f"\nCheck https://smith.langchain.com/o/.../projects/p/{os.environ.get('LANGSMITH_PROJECT')} for the trace.")
