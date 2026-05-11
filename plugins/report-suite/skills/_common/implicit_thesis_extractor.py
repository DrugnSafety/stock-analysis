"""Phase 5 — Implicit Thesis 자동 추출 (standalone 분석용).

블로그 글 없이 ticker만으로 분석할 때, 종목 본질에 기반한 implicit thesis를 자동 생성.
이를 통해 Thesis × Persona Matrix가 standalone 분석에서도 의미있는 매트릭스 렌더링 가능.

데이터 소스 우선순위:
1. deep_research.json의 catalysts → predictive thesis 변환
2. deep_research.json의 risks → conditional/challenge thesis 변환
3. deep_research.json의 industry overview → sector-level structural thesis
4. SEC EDGAR / DART 재무 데이터 → quantitative thesis (e.g., "FCF margin declining")
5. Sector template (fallback) → 모든 종목에 적용 가능한 generic thesis

사용 예:
    from implicit_thesis_extractor import extract_implicit_theses
    theses = extract_implicit_theses(
        ticker="LNG",
        company_name="Cheniere Energy",
        sector="LNG Export Operator",
        deep_research={...},  # optional
        financials={...},     # optional (financial_statements_us_gaap output)
    )
    # → [{"claim_id": "T1", "claim": "...", "type": "predictive", ...}, ...]
"""
from __future__ import annotations

from typing import Optional


def _make_thesis(claim_id: str, claim: str, type_: str,
                 timeframe: str = "medium_term",
                 supporting_evidence: Optional[list] = None,
                 source: str = "implicit") -> dict:
    """Standard thesis dict."""
    return {
        "claim_id": claim_id,
        "claim": claim,
        "type": type_,  # factual | predictive | normative | conditional
        "timeframe": timeframe,  # short_term (<6m) | medium_term (6m-2y) | long_term (>2y)
        "supporting_evidence": supporting_evidence or [],
        "_source": source,  # implicit | catalyst | risk | macro | financial | sector_template
    }


def _from_catalysts(catalysts: list[dict], start_idx: int) -> list[dict]:
    """Convert deep_research catalysts into predictive thesis."""
    out = []
    for i, c in enumerate(catalysts[:5]):
        title = c.get("title") or c.get("name") or c.get("event") or ""
        date = c.get("date") or c.get("timing") or ""
        impact = c.get("impact") or c.get("description") or ""
        if not title:
            continue
        claim = f"{title}이(가) 실현되면, 시장은 본 종목의 valuation을 reprice할 가능성이 높음"
        if impact:
            claim += f" ({impact[:80]})"
        out.append(_make_thesis(
            f"T{start_idx + i + 1}",
            claim,
            "predictive",
            timeframe="medium_term" if date else "short_term",
            supporting_evidence=[{"type": "catalyst", "detail": title, "date": date}],
            source="catalyst"
        ))
    return out


def _from_risks(risks: list[dict], start_idx: int) -> list[dict]:
    """Convert deep_research risks into conditional/challenge thesis."""
    out = []
    for i, r in enumerate(risks[:4]):
        title = r.get("title") or r.get("name") or r.get("risk") or ""
        prob = r.get("probability") or r.get("likelihood") or ""
        impact = r.get("impact") or r.get("description") or ""
        if not title:
            continue
        claim = f"본 종목의 thesis는 다음 리스크가 현실화되지 않는다는 가정에 의존: {title}"
        if impact:
            claim += f" — 발생 시 {impact[:60]}"
        out.append(_make_thesis(
            f"T{start_idx + i + 1}",
            claim,
            "conditional",
            timeframe="medium_term",
            supporting_evidence=[{"type": "risk", "detail": title, "probability": prob}],
            source="risk"
        ))
    return out


def _from_industry(industry: dict, start_idx: int) -> list[dict]:
    """Convert industry/sector overview into structural thesis."""
    out = []
    if not industry:
        return out

    market_size = industry.get("market_size") or {}
    cagr = market_size.get("cagr_pct")
    if cagr:
        out.append(_make_thesis(
            f"T{start_idx + 1}",
            f"본 종목이 속한 산업의 구조적 성장률({cagr}% CAGR)이 macro tailwind를 제공",
            "factual" if cagr > 0 else "factual",
            timeframe="long_term",
            supporting_evidence=[{"type": "industry_cagr", "value": cagr,
                                   "horizon": market_size.get("horizon", "")}],
            source="macro"
        ))

    competitors = industry.get("competitors") or []
    if competitors:
        moats = [c.get("moat") for c in competitors if c.get("moat")]
        if moats:
            out.append(_make_thesis(
                f"T{start_idx + len(out) + 1}",
                f"본 종목은 산업 내 경쟁우위(moat) — 주요 경쟁사 대비 차별적 포지셔닝 보유",
                "factual",
                timeframe="long_term",
                supporting_evidence=[{"type": "competitors", "count": len(competitors)}],
                source="industry"
            ))

    return out


def _from_financials(financials: dict, ticker: str, start_idx: int) -> list[dict]:
    """Convert financial trends into quantitative thesis."""
    out = []
    if not financials:
        return out

    annual = financials.get("annual", {})
    INC = annual.get("income_statement", {})
    CF = annual.get("cash_flow", {})

    revenue = INC.get("revenue", {})
    op_income = INC.get("op_income", {})
    fcf = CF.get("fcf", {})

    if revenue and len(revenue) >= 3:
        years = sorted(revenue.keys())
        recent_rev = revenue.get(years[-1], 0)
        earlier_rev = revenue.get(years[0], 0)
        if earlier_rev > 0:
            cagr = ((recent_rev / earlier_rev) ** (1.0 / (len(years) - 1)) - 1) * 100
            stance_word = "성장 모멘텀" if cagr > 5 else "정체 시그널" if cagr > -5 else "구조적 매출 감소"
            out.append(_make_thesis(
                f"T{start_idx + 1}",
                f"본 종목은 최근 {len(years)}년간 매출 CAGR {cagr:+.1f}% — {stance_word}",
                "factual",
                timeframe="medium_term",
                supporting_evidence=[{"type": "revenue_cagr", "value": cagr,
                                       "years": len(years)}],
                source="financial"
            ))

    # FCF transition thesis
    if fcf and len(fcf) >= 2:
        years = sorted(fcf.keys())
        recent_fcf = fcf.get(years[-1], 0)
        prior_fcf = fcf.get(years[-2], 0)
        if recent_fcf < 0 < prior_fcf:
            out.append(_make_thesis(
                f"T{start_idx + len(out) + 1}",
                f"본 종목의 FCF가 ${prior_fcf:.0f}M → ${recent_fcf:.0f}M로 음전환 — 자본 사이클 trough 시그널 또는 capex 과중",
                "factual",
                timeframe="medium_term",
                supporting_evidence=[{"type": "fcf_trend", "transition": "positive_to_negative"}],
                source="financial"
            ))
        elif recent_fcf > 0 and prior_fcf > 0 and recent_fcf > prior_fcf * 1.2:
            out.append(_make_thesis(
                f"T{start_idx + len(out) + 1}",
                f"본 종목의 FCF가 ${prior_fcf:.0f}M → ${recent_fcf:.0f}M로 확대 — 현금 창출력 가속화",
                "factual",
                timeframe="medium_term",
                supporting_evidence=[{"type": "fcf_trend", "transition": "accelerating"}],
                source="financial"
            ))

    return out


def _sector_template_theses(ticker: str, sector: str, start_idx: int) -> list[dict]:
    """Sector-agnostic generic theses (always added as fallback)."""
    out = [
        _make_thesis(
            f"T{start_idx + 1}",
            f"본 종목의 valuation은 현재 시장 가격에 충분히 반영되었는가? — 가격 vs 내재가치 갭",
            "normative",
            timeframe="medium_term",
            source="sector_template"
        ),
        _make_thesis(
            f"T{start_idx + 2}",
            f"경영진의 자본 배분 정책(배당·자사주매입·M&A·재투자)이 주주가치 극대화에 부합하는가",
            "normative",
            timeframe="long_term",
            source="sector_template"
        ),
    ]
    return out


def extract_implicit_theses(
    ticker: str,
    company_name: str = "",
    sector: str = "",
    deep_research: Optional[dict] = None,
    financials: Optional[dict] = None,
    user_provided_theses: Optional[list[dict]] = None,
) -> list[dict]:
    """Top-level entry — combine all sources into ordered thesis list.

    우선순위 (가장 신뢰도 높은 것부터):
    1. 사용자 제공 thesis (예: 블로그 글에서 추출된 것)
    2. Catalysts → predictive
    3. Risks → conditional
    4. Industry/macro → factual
    5. Financial trends → factual
    6. Sector template → normative (always added)

    Returns: thesis list with claim_id T1, T2, ... in priority order.
    """
    deep_research = deep_research or {}
    theses = []

    # 1. User-provided (from blog extraction)
    if user_provided_theses:
        for i, t in enumerate(user_provided_theses):
            t_copy = dict(t)
            t_copy["claim_id"] = f"T{i + 1}"
            t_copy.setdefault("_source", "user_provided")
            theses.append(t_copy)

    next_idx = len(theses)

    # 2. From catalysts
    catalysts = deep_research.get("catalysts", [])
    catalyst_theses = _from_catalysts(catalysts, next_idx)
    theses.extend(catalyst_theses)
    next_idx = len(theses)

    # 3. From risks
    risks = deep_research.get("risks", [])
    risk_theses = _from_risks(risks, next_idx)
    theses.extend(risk_theses)
    next_idx = len(theses)

    # 4. From industry
    industry = deep_research.get("industry", {})
    industry_theses = _from_industry(industry, next_idx)
    theses.extend(industry_theses)
    next_idx = len(theses)

    # 5. From financials
    financial_theses = _from_financials(financials or {}, ticker, next_idx)
    theses.extend(financial_theses)
    next_idx = len(theses)

    # 6. Sector template (always)
    template_theses = _sector_template_theses(ticker, sector, next_idx)
    theses.extend(template_theses)

    # Cap at 12 thesis
    return theses[:12]


def is_standalone_analysis(thesis_list_path) -> bool:
    """Detect if this is a standalone analysis (no blog input)."""
    import json
    from pathlib import Path
    p = Path(thesis_list_path)
    if not p.exists():
        return True
    try:
        d = json.loads(p.read_text())
        if isinstance(d, dict):
            d = d.get("theses", d.get("thesis_list", []))
        if not d or len(d) == 0:
            return True
    except Exception:
        return True
    return False


# ============== CLI ==============
if __name__ == "__main__":
    import argparse, json, sys
    from pathlib import Path

    p = argparse.ArgumentParser(description="Implicit Thesis Extractor (Phase 5)")
    p.add_argument("ticker", help="Ticker (e.g. LNG, BTU)")
    p.add_argument("--company", default="", help="Company name")
    p.add_argument("--sector", default="", help="Sector")
    p.add_argument("--deep-research", help="Path to deep_research/{ticker}.json")
    p.add_argument("--financials", help="Path to financial_statements_us_gaap.py output JSON")
    p.add_argument("--user-theses", help="Path to existing thesis_list.json (to merge)")
    p.add_argument("--output", help="Save thesis list to this JSON path")
    args = p.parse_args()

    dr = {}
    if args.deep_research and Path(args.deep_research).exists():
        dr = json.loads(Path(args.deep_research).read_text())

    fin = {}
    if args.financials and Path(args.financials).exists():
        fin = json.loads(Path(args.financials).read_text())

    user_th = None
    if args.user_theses and Path(args.user_theses).exists():
        raw = json.loads(Path(args.user_theses).read_text())
        if isinstance(raw, dict):
            user_th = raw.get("theses") or raw.get("thesis_list") or []
        else:
            user_th = raw

    theses = extract_implicit_theses(
        ticker=args.ticker,
        company_name=args.company,
        sector=args.sector,
        deep_research=dr,
        financials=fin,
        user_provided_theses=user_th,
    )

    out = {"theses": theses, "_implicit_extraction": True,
           "ticker": args.ticker, "source_count": len(theses)}

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(json.dumps(out, indent=2, ensure_ascii=False))
        print(f"Saved {len(theses)} theses to {args.output}")
    else:
        print(json.dumps(out, indent=2, ensure_ascii=False))
