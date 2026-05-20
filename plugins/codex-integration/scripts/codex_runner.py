#!/usr/bin/env python3
"""OpenAI Codex Runner — dual-mode (CLI subprocess + Direct API fallback).

Detection logic:
  1. If `codex` CLI binary is in PATH → use CLI subprocess (Claude Code environment)
  2. Else if OPENAI_API_KEY env var set → use OpenAI API directly (Cowork environment)
  3. Else → return error with install hint

Usage:
    from codex_runner import codex_query

    result = codex_query(
        prompt="Evaluate this investment thesis...",
        mode="o3"  # 'o3' | 'o4-mini' | 'gpt-5' | 'gpt-4o'
    )
"""
from __future__ import annotations
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional


SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent
# Add specialist-agents/scripts to path for langsmith_wrapper
sys.path.insert(0, str(PLUGIN_ROOT.parent / "specialist-agents" / "scripts"))

try:
    from langsmith_wrapper import traced_call, log_run_metadata
except ImportError:
    def traced_call(name=None, run_type="llm", metadata=None):
        def deco(fn): return fn
        return deco

    def log_run_metadata(**kwargs):
        pass


MODEL_MAP = {
    "o3": "o3",
    "o4-mini": "o4-mini",
    "gpt-5": "gpt-5",
    "gpt-4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
}


def detect_environment() -> str:
    """Return 'cli' (codex CLI available) | 'api' (only OPENAI_API_KEY) | 'none'."""
    if shutil.which("codex"):
        return "cli"
    if os.environ.get("OPENAI_API_KEY"):
        return "api"
    return "none"


@traced_call(name="codex_query", run_type="llm",
             metadata={"provider": "openai"})
def codex_query(prompt: str,
                mode: str = "o4-mini",
                system: Optional[str] = None,
                temperature: float = 0.3,
                max_tokens: int = 4000) -> dict:
    """Run an OpenAI query via Codex CLI or direct API.

    Returns:
        {
            "status": "ok" | "error",
            "model": resolved model name,
            "via": "codex_cli" | "openai_api" | "none",
            "response": text,
            "tokens": {input, output} | None,
        }
    """
    env = detect_environment()
    log_run_metadata(mode=mode, via=env)

    model = MODEL_MAP.get(mode, mode)

    if env == "cli":
        return _run_via_codex_cli(prompt, model, system, temperature, max_tokens)
    elif env == "api":
        return _run_via_openai_api(prompt, model, system, temperature, max_tokens)
    else:
        return {
            "status": "error",
            "via": "none",
            "error": (
                "Neither codex CLI nor OPENAI_API_KEY available. Install codex via "
                "`npm i -g @openai/codex` (claude-code env) or set OPENAI_API_KEY in .env"
            ),
        }


def _run_via_codex_cli(prompt, model, system, temperature, max_tokens) -> dict:
    """Subprocess to codex CLI. Codex authenticates via ChatGPT account."""
    cmd = ["codex", "--model", model, "--non-interactive"]
    if system:
        cmd += ["--system", system]
    cmd += ["--prompt", prompt]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=120,
        )
        if result.returncode != 0:
            return {
                "status": "error",
                "via": "codex_cli",
                "model": model,
                "error": result.stderr[:500],
            }
        return {
            "status": "ok",
            "via": "codex_cli",
            "model": model,
            "response": result.stdout.strip(),
            "tokens": None,  # codex CLI doesn't expose usage
        }
    except subprocess.TimeoutExpired:
        return {"status": "error", "via": "codex_cli", "error": "timeout after 120s"}
    except Exception as e:
        return {"status": "error", "via": "codex_cli", "error": str(e)}


def _run_via_openai_api(prompt, model, system, temperature, max_tokens) -> dict:
    """Direct OpenAI Chat Completions API."""
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "status": "error",
            "via": "openai_api",
            "error": "openai package not installed (pip install openai)",
        }

    try:
        client = OpenAI()
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        # o-series models use different params
        is_reasoning = model.startswith("o")
        kwargs = {"model": model, "messages": messages}
        if is_reasoning:
            kwargs["max_completion_tokens"] = max_tokens
        else:
            kwargs["max_tokens"] = max_tokens
            kwargs["temperature"] = temperature

        resp = client.chat.completions.create(**kwargs)
        usage = resp.usage if hasattr(resp, "usage") else None
        return {
            "status": "ok",
            "via": "openai_api",
            "model": model,
            "response": resp.choices[0].message.content,
            "tokens": (
                {"input": usage.prompt_tokens, "output": usage.completion_tokens}
                if usage else None
            ),
        }
    except Exception as e:
        return {"status": "error", "via": "openai_api", "error": str(e)}


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--mode", default="o4-mini")
    p.add_argument("--prompt", required=True)
    p.add_argument("--system", default=None)
    args = p.parse_args()

    env = detect_environment()
    print(f"[codex_runner] detected env: {env}")
    result = codex_query(args.prompt, mode=args.mode, system=args.system)
    print(f"\nstatus: {result.get('status')}")
    print(f"via: {result.get('via')}")
    print(f"model: {result.get('model')}")
    if result.get("response"):
        print(f"\n--- response ---\n{result['response']}")
    if result.get("error"):
        print(f"\nerror: {result['error']}")
