"""공통 state 관리 유틸 — JSON dict 기반 state machine."""
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

KST = timezone(timedelta(hours=9))


def init_debate_state(ticker: str, max_rounds: int = 3,
                       convergence_threshold: float = 0.85) -> dict:
    return {
        "type": "debate",
        "ticker": ticker,
        "round": 0,
        "max_rounds": max_rounds,
        "convergence_threshold": convergence_threshold,
        "bull_history": [],      # 각 round의 Bull verdict + reasoning
        "bear_history": [],
        "skeptic_history": [],
        "convergence_score": 0.0,
        "final_verdict": None,
        "final_confidence": None,
        "consolidation_reasoning": None,
        "started_at": datetime.now(KST).isoformat(),
        "ended_at": None,
        "total_subagent_spawns": 0,
    }


def init_refinement_state(thesis_list_path: str,
                           min_confidence: float = 0.5,
                           max_iterations: int = 2) -> dict:
    return {
        "type": "refinement",
        "thesis_list_path": thesis_list_path,
        "min_confidence": min_confidence,
        "max_iterations": max_iterations,
        "iteration": 0,
        "weak_theses": [],            # 보강 대상
        "refinement_history": [],     # iteration별 결과
        "started_at": datetime.now(KST).isoformat(),
    }


def init_pipeline_state(blog_url: str) -> dict:
    return {
        "type": "pipeline",
        "blog_url": blog_url,
        "stage": "init",
        "stages_completed": [],
        "post_data": None,
        "thesis_list": None,
        "thesis_evaluations": None,
        "stocks_extracted": None,
        "persona_panel_results": {},
        "risk_limits": None,
        "trade_decisions": None,
        "errors": [],
        "started_at": datetime.now(KST).isoformat(),
    }


def save_state(state: dict, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def load_state(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def append_round(state: dict, role: str, result: dict):
    """role: 'bull', 'bear', 'skeptic'"""
    key = f"{role}_history"
    if key in state:
        state[key].append({**result, "round": state["round"]})
    state["total_subagent_spawns"] = state.get("total_subagent_spawns", 0) + 1


def stage_complete(state: dict, stage: str, result: dict = None):
    state.setdefault("stages_completed", []).append({
        "stage": stage,
        "completed_at": datetime.now(KST).isoformat(),
        "summary": result or {},
    })
    state["stage"] = stage


def finalize(state: dict):
    state["ended_at"] = datetime.now(KST).isoformat()
    return state
