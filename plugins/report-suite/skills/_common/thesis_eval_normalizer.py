"""thesis_eval/all_aggregate.json schema normalizer.

Background — 2026-05-12 doctordk_nvidia_800vdc_power 분석에서 4-Analyst 평가 자료가
PDF에 빠진 사고가 발생했다. 원인은 all_aggregate.json schema 불일치였다:

  • Legacy/canonical schema (build_r1.py·build_r3.py가 읽는 형식):
      {
        "aggregates": [
          {
            "claim_id": "T01",
            "evaluations": {
              "macro": {"stance": "support|neutral|rebut", "confidence": 0.0-1.0, "rationale": "..."},
              "industry": {...},
              "empirical": {...},
              "counter": {...}
            },
            "aggregate": {
              "weighted_stance": "support|neutral|rebut",
              "weighted_confidence": 0.0-1.0,
              "agreement_level": "..."
            }
          },
          ...
        ]
      }

  • V2-style schema (LLM이 자연스럽게 작성하는 형식, 위 사고에서 사용된 형식):
      {
        "evaluations": [
          {
            "claim_id": "T01",
            "analysts": {
              "macro": {"stance": "strong_support|qualified_support|skeptical|...", "confidence": 0.0-1.0, "rationale": "..."},
              ...
            },
            "weighted_stance": "support|qualified_support|...",
            "aggregate_confidence": 0.0-1.0,
            "consensus_note": "..."
          },
          ...
        ]
      }

이 모듈은 두 schema 모두 입력으로 받아 canonical 형식으로 정규화한다.
또한 7-class stance vocabulary를 3-class(support/rebut/neutral)로 매핑한다.

사용:
    from thesis_eval_normalizer import load_and_normalize, normalize_stance
    eval_data = load_and_normalize(Path("thesis_eval/all_aggregate.json"))
    # eval_data[claim_id] → canonical dict with 'evaluations' and 'aggregate'
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


# ── Stance vocabulary normalization (7-class → 3-class) ─────────────────
# Renderers (build_r1.py heatmap, build_r3.py validation table) understand only
# support / rebut / neutral. Anything else must map.
STANCE_MAP = {
    # canonical
    "support": "support",
    "rebut": "rebut",
    "neutral": "neutral",

    # v2 LLM-natural variants
    "strong_support": "support",
    "qualified_support": "support",
    "partial_support": "support",
    "lean_support": "support",
    "minor_caveat": "support",  # caveat 정도면 여전히 동의

    "disagree": "rebut",
    "skeptical": "rebut",
    "partial_disagreement": "rebut",
    "lean_disagree": "rebut",
    "strong_disagree": "rebut",
    "rebuttal": "rebut",

    # neutral spellings
    "mixed": "neutral",
    "uncertain": "neutral",
}


def normalize_stance(stance: Optional[str]) -> str:
    """Map any stance string to canonical {support, rebut, neutral}."""
    if not stance:
        return "neutral"
    s = stance.strip().lower()
    return STANCE_MAP.get(s, "neutral")  # unknown → neutral (defensive)


def _normalize_v2_to_canonical(v2_eval: dict) -> dict:
    """Convert one v2-style thesis evaluation dict to canonical.

    Patched 2026-05-28: case-insensitive analyst key matching (LNG bug fix).
    LLM이 "Macro"/"Industry"/"Empirical"/"Counter" (대문자)로 출력 시 정규화 못 했음.
    """
    cid = v2_eval.get("claim_id", "")
    analysts_raw = v2_eval.get("analysts") or v2_eval.get("evaluations") or {}

    # Case-insensitive lookup table — analyst 키가 대소문자 어떻든 처리
    analysts_lookup = {k.lower(): v for k, v in analysts_raw.items()}

    # Normalize each analyst's stance
    # Sprint E-3 patch: preserve rich metadata (supporting_data, counter_evidence, key_assumption)
    # — previously only stance/confidence/rationale were carried over, causing data tagging count = 0
    #   and downstream renderers (R1 thesis×analyst matrix) to lose evidence detail.
    evaluations = {}
    for analyst in ("macro", "industry", "empirical", "counter"):
        a = analysts_lookup.get(analyst)
        if not a:
            continue
        evaluations[analyst] = {
            "stance": normalize_stance(a.get("stance")),
            "confidence": float(a.get("confidence") or 0.0),
            "rationale": a.get("rationale") or "",
            # ── Rich metadata pass-through (Sprint E-3) ─────────────────
            "supporting_data": a.get("supporting_data") or [],
            "counter_evidence": a.get("counter_evidence") or [],
            "key_assumption": a.get("key_assumption") or "",
            "fragility_score": a.get("fragility_score"),
            "rationale_meta": a.get("rationale_meta"),
            # original (non-normalized) stance for traceability
            "stance_raw": a.get("stance"),
        }

    # Aggregate sub-object — multiple possible field names (LLM-natural variants)
    # Defensive: consensus가 string("neutral")으로 올 수도 있음 → dict일 때만 .get 사용
    agg_sub = v2_eval.get("aggregate")
    if not isinstance(agg_sub, dict):
        agg_sub_candidate = v2_eval.get("consensus")
        agg_sub = agg_sub_candidate if isinstance(agg_sub_candidate, dict) else {}

    # consensus가 string인 경우 → top-level fields로 fallback
    consensus_str = v2_eval.get("consensus") if isinstance(v2_eval.get("consensus"), str) else None

    ws = agg_sub.get("weighted_stance") or agg_sub.get("stance") or \
         v2_eval.get("weighted_stance") or v2_eval.get("consensus_stance") or consensus_str
    wc = agg_sub.get("weighted_confidence") or agg_sub.get("confidence") or \
         v2_eval.get("aggregate_confidence") or v2_eval.get("weighted_confidence")
    al = agg_sub.get("agreement_level") or agg_sub.get("note") or \
         v2_eval.get("consensus_note") or v2_eval.get("agreement_level") or ""

    aggregate = {
        "weighted_stance": normalize_stance(ws),
        "weighted_confidence": float(wc or 0.0),
        "agreement_level": al,
    }

    # claim_text → claim (이전 출력 누락)
    claim_text = v2_eval.get("claim") or v2_eval.get("claim_text") or ""

    return {
        "claim_id": cid,
        "claim": claim_text,
        "evaluations": evaluations,
        "aggregate": aggregate,
    }


def load_and_normalize(path: Path) -> dict:
    """Load all_aggregate.json (either schema) → dict keyed by claim_id.

    Fix-A (2026-05-28): mock data 자동 감지 — rationale에 "(mock)" 또는 "user_provided"가
    있으면 __mock__: True 플래그 표시.

    Returns:
        dict mapping claim_id → canonical thesis eval dict + 선택적 '__mock_count__' key.
    """
    if not path.exists():
        return {}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}

    items = data.get("aggregates")
    if items is None:
        items = data.get("evaluations")
    if not isinstance(items, list):
        return {}

    out: dict = {}
    mock_count = 0
    total_analyst_evals = 0
    for raw in items:
        norm = _normalize_v2_to_canonical(raw)
        if norm["claim_id"]:
            out[norm["claim_id"]] = norm
        # Mock detection: 각 analyst의 rationale에 mock 마커 있는지
        analysts_raw = raw.get("analysts") or raw.get("evaluations") or {}
        for k, v in analysts_raw.items():
            if isinstance(v, dict):
                total_analyst_evals += 1
                rat = v.get("rationale", "") or ""
                if "(mock)" in rat or "user_provided" in rat.lower():
                    mock_count += 1

    # mock ratio 계산 — 50%+면 thesis_eval 전체가 placeholder로 간주
    # NOTE: metadata는 nested dict로 묶어서 caller가 iterate 시 .get() 충돌 회피
    if total_analyst_evals > 0:
        mock_ratio = mock_count / total_analyst_evals
        out["__metadata__"] = {
            "mock_count": mock_count,
            "total_evals": total_analyst_evals,
            "mock_ratio": mock_ratio,
            "is_mock_data": mock_ratio >= 0.5,
        }

    return out


def detect_schema_version(path: Path) -> str:
    """Return 'canonical', 'v2', 'unknown', or 'missing'.

    Used by validators to warn when schema is non-canonical.
    """
    if not path.exists():
        return "missing"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return "unknown"

    if isinstance(data.get("aggregates"), list) and data["aggregates"]:
        sample = data["aggregates"][0]
        if isinstance(sample.get("evaluations"), dict) and isinstance(sample.get("aggregate"), dict):
            return "canonical"
        if isinstance(sample.get("analysts"), dict):
            return "v2"
        return "unknown"

    if isinstance(data.get("evaluations"), list) and data["evaluations"]:
        sample = data["evaluations"][0]
        if isinstance(sample.get("analysts"), dict):
            return "v2"
        return "unknown"

    return "unknown"
