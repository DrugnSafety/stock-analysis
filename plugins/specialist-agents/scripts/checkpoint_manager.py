#!/usr/bin/env python3
"""Checkpoint Manager — TradingAgents 0.2.4 LangGraph checkpoint resume pattern.

Persists per-stage state to {pipeline_dir}/.checkpoint.json so that
build_combined.py and pipeline runners can resume from the last completed
stage if interrupted (Cowork 45s bash timeout, network failure, etc.).

Stage definitions:
    1. collect_blog       (blog post fetch)
    2. extract_thesis     (thesis_list.json)
    3. identify_stocks    (stocks.json with market_data)
    4. evaluate_thesis    (thesis_eval/all_aggregate.json)
    5. persona_panel      (persona_panel/{ticker}/*.json)
    6. risk_portfolio     (risk_limits.json + decisions.json + portfolio.json)
    7. deep_research      (deep_research/{ticker}.json)
    8. specialist_agents  (research_intel/, sentiment/, earnings_review/, models/)
    9. build_pdf          (reports/combined/*.pdf)
    10. sync              (GitHub + Notion)
"""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Optional


CANONICAL_STAGES = [
    "collect_blog",
    "extract_thesis",
    "identify_stocks",
    "evaluate_thesis",
    "persona_panel",
    "risk_portfolio",
    "deep_research",
    "specialist_agents",
    "build_pdf",
    "sync",
]


def _checkpoint_path(pipeline_dir: Path) -> Path:
    return pipeline_dir / ".checkpoint.json"


def load(pipeline_dir: Path) -> dict:
    """Load existing checkpoint or return fresh state."""
    p = _checkpoint_path(pipeline_dir)
    if p.exists():
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "version": "0.1.0",
        "pipeline_dir": str(pipeline_dir),
        "created_at": datetime.now().isoformat() + "+09:00",
        "updated_at": None,
        "completed_stages": [],
        "stage_artifacts": {},   # stage_name -> list of output files
        "current_stage": None,
        "failed_attempts": {},   # stage -> [{"at": ..., "error": ...}]
    }


def save(pipeline_dir: Path, state: dict) -> None:
    state["updated_at"] = datetime.now().isoformat() + "+09:00"
    _checkpoint_path(pipeline_dir).write_text(
        json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def mark_complete(pipeline_dir: Path, stage: str, artifacts: Optional[list] = None) -> None:
    state = load(pipeline_dir)
    if stage not in state["completed_stages"]:
        state["completed_stages"].append(stage)
    if artifacts:
        state["stage_artifacts"][stage] = artifacts
    state["current_stage"] = None
    save(pipeline_dir, state)


def mark_started(pipeline_dir: Path, stage: str) -> None:
    state = load(pipeline_dir)
    state["current_stage"] = stage
    save(pipeline_dir, state)


def mark_failed(pipeline_dir: Path, stage: str, error: str) -> None:
    state = load(pipeline_dir)
    state.setdefault("failed_attempts", {}).setdefault(stage, []).append(
        {"at": datetime.now().isoformat() + "+09:00", "error": str(error)[:500]}
    )
    state["current_stage"] = None
    save(pipeline_dir, state)


def is_complete(pipeline_dir: Path, stage: str) -> bool:
    state = load(pipeline_dir)
    return stage in state.get("completed_stages", [])


def next_stage(pipeline_dir: Path) -> Optional[str]:
    """Return the next stage to run, or None if all complete."""
    state = load(pipeline_dir)
    completed = set(state.get("completed_stages", []))
    for s in CANONICAL_STAGES:
        if s not in completed:
            return s
    return None


def progress_pct(pipeline_dir: Path) -> float:
    state = load(pipeline_dir)
    return round(len(state.get("completed_stages", [])) / len(CANONICAL_STAGES) * 100, 1)


def reset(pipeline_dir: Path, from_stage: Optional[str] = None) -> None:
    """Reset checkpoint. If from_stage given, only drop stages from that point onward."""
    state = load(pipeline_dir)
    if from_stage is None:
        state["completed_stages"] = []
        state["stage_artifacts"] = {}
    else:
        try:
            cut_idx = CANONICAL_STAGES.index(from_stage)
            drop_set = set(CANONICAL_STAGES[cut_idx:])
            state["completed_stages"] = [s for s in state["completed_stages"] if s not in drop_set]
            for s in drop_set:
                state["stage_artifacts"].pop(s, None)
        except ValueError:
            pass
    save(pipeline_dir, state)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("pipeline_dir")
    p.add_argument("--status", action="store_true", help="show checkpoint status")
    p.add_argument("--reset", action="store_true", help="reset all stages")
    p.add_argument("--reset-from", help="reset from specific stage onward")
    args = p.parse_args()

    pdir = Path(args.pipeline_dir)
    if args.reset:
        reset(pdir)
        print(f"OK reset all stages")
    elif args.reset_from:
        reset(pdir, args.reset_from)
        print(f"OK reset from stage '{args.reset_from}'")
    else:
        state = load(pdir)
        completed = state.get("completed_stages", [])
        next_s = next_stage(pdir)
        pct = progress_pct(pdir)
        print(f"=== Checkpoint Status ({pdir.name}) ===")
        print(f"Progress: {pct}% ({len(completed)}/{len(CANONICAL_STAGES)} stages)")
        for s in CANONICAL_STAGES:
            mark = "✓" if s in completed else ("▶" if s == next_s else " ")
            print(f"  {mark} {s}")
        print(f"\nNext: {next_s or 'all complete'}")
        if state.get("failed_attempts"):
            print(f"Failed attempts: {sum(len(v) for v in state['failed_attempts'].values())} total")
