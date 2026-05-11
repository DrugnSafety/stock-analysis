#!/usr/bin/env python3
"""Layer 2 — Overview Markdown builder.

모든 종목 정보를 단일 Markdown 문서로 통합. Layer 1의 per-stock PDF에 대한
overview/summary 역할. Email·Slack·Notion 공유 적합.

Usage:
  python build_overview_md.py \\
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \\
    --output overview.md
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))

from currency_format import format_price, format_amount_local
from ticker_resolver import resolve_ticker  # type: ignore


def _read_json(path: Path) -> dict | list:
    if not path.exists():
        return {}
    return json.loads(path.read_text())


def render(pipeline_dir: Path) -> str:
    meta = _read_json(pipeline_dir / "meta.json")
    thesis_data = _read_json(pipeline_dir / "thesis_list.json")
    theses = thesis_data.get("theses", [])
    summary_oneliner = thesis_data.get("summary_one_liner", "")

    stocks = _read_json(pipeline_dir / "stocks.json") or []
    decisions = (_read_json(pipeline_dir / "decisions.json") or {}).get("decisions", [])
    risk_limits = (_read_json(pipeline_dir / "risk_limits.json") or {}).get("limits", [])
    persona_aggs_path = pipeline_dir / "persona_panel" / "_all_aggregates.json"
    persona_aggs = _read_json(persona_aggs_path) if persona_aggs_path.exists() else {}

    # ── Header ─────────────────────────────────────────────────────────
    title = meta.get("title", "분석 보고서")
    blog_url = meta.get("blog_url", "")
    blogger = meta.get("blogger", "")
    date = meta.get("date", "")
    n_stocks = len(stocks)

    md = f"""# {title}

**원문**: [{blog_url}]({blog_url})  \n
**블로거**: {blogger}  \n
**작성일**: {date} | **분석 대상**: {n_stocks} 종목  \n
**분석 시스템**: 13명 페르소나 패널 + 4-Analyst + Deep Research + Multi-format Output

---

## I. Executive Summary

### 핵심 thesis (한 줄 요약)

> {summary_oneliner}

### 추출된 핵심 thesis ({len(theses)}개)

"""
    for t in theses:  # show ALL theses, not just 6
        importance = t.get("importance", "")
        timeframe = t.get("timeframe", "")
        md += f"- **{t.get('claim_id', '')}** ({importance}·{timeframe}): {t.get('claim', '')}\n"

    # ── Top 3 picks ────────────────────────────────────────────────────
    sorted_decisions = sorted(decisions, key=lambda d: -abs(d.get("signal_score", 0)))
    top3 = sorted_decisions[:3]

    md += "\n### Top 3 Picks\n\n"
    md += "| 순위 | 티커 | 종목명 | Verdict | Signal | 한 줄 근거 |\n"
    md += "|---|---|---|---|---|---|\n"
    medals = ["🥇", "🥈", "🥉"]
    for i, d in enumerate(top3):
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        action = d.get("action", "-").upper()
        action_color = "🟢" if action == "BUY" else "🔴" if action.startswith("SELL") else "🟡"
        signal = d.get("signal_score", 0)
        risk = d.get("primary_risks", [""])[0][:80]
        md += f"| {medals[i] if i < len(medals) else ''} | **{ticker}** | {name} | {action_color} **{action}** | {signal:+.2f} | {risk}... |\n"

    md += "\n---\n\n## II. 종목별 Verdict 종합\n\n"
    md += "| # | 티커 | 종목명 | Sector | 매수/중립/매도 | 평균 신뢰도 | Action | Signal |\n"
    md += "|---|---|---|---|---|---|---|---|\n"
    for i, d in enumerate(decisions, 1):
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        sector = info.get("sector", "")
        agg = persona_aggs.get(ticker, {})
        dist = agg.get("verdict_distribution", {})
        bull = dist.get("lean_bullish", {}).get("count", 0)
        neu = dist.get("neutral", {}).get("count", 0)
        bear = dist.get("lean_bearish", {}).get("count", 0)
        avg_conf = agg.get("average_confidence", 0)
        action = d.get("action", "-").upper()
        action_color = "🟢" if action == "BUY" else "🔴" if action.startswith("SELL") else "🟡"
        signal = d.get("signal_score", 0)
        md += f"| {i} | **{ticker}** | {name} | {sector[:28]} | {bull}/{neu}/{bear} | {avg_conf*100:.0f}% | {action_color} {action} | {signal:+.2f} |\n"

    # ── Per-stock summary ──────────────────────────────────────────────
    md += "\n---\n\n## III. 종목별 핵심 분석\n\n"
    for d in decisions:
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        agg = persona_aggs.get(ticker, {})
        action = d.get("action", "-").upper()
        action_color = "🟢" if action == "BUY" else "🔴" if action.startswith("SELL") else "🟡"
        signal = d.get("signal_score", 0)

        # Find market data
        m = next((s.get("market_data", {}) for s in stocks if s.get("ticker") == ticker), {})
        price = m.get("current_price", 0)
        currency = m.get("currency", "KRW")
        pe = m.get("forward_pe", "-")
        ret_1y = m.get("return_1y_pct", 0)
        vol = m.get("volatility_annualized_pct", 0)

        md += f"### {action_color} {ticker} {name} — {action} (signal {signal:+.2f})\n\n"
        md += f"**현재가**: {format_price(price, currency)} | **Forward PE**: {pe} | **1Y**: {ret_1y:+.1f}% | **변동성**: {vol:.1f}%\n\n"

        # Top concerns + opportunities
        persona_results = agg.get("persona_results", {})
        if persona_results:
            top_personas = sorted(persona_results.items(),
                                    key=lambda x: -(x[1].get("confidence", 0)))[:3]
            md += "**페르소나 highlight (top-3 confidence)**:\n"
            for pid, p in top_personas:
                v = p.get("verdict", "")
                conf = p.get("confidence", 0)
                v_kr = {"lean_bullish": "🟢 매수", "neutral": "🟡 중립", "lean_bearish": "🔴 매도"}.get(v, v)
                concern = (p.get("key_concerns_top3") or [""])[0][:120]
                md += f"- **{p.get('persona_kr', pid)}**: {v_kr} ({conf*100:.0f}%) — {concern}\n"

        # Risks
        risks = d.get("primary_risks", [])
        if risks:
            md += "\n**핵심 위험**:\n"
            for r in risks[:3]:
                md += f"- {r}\n"

        # Universal concerns
        universal = agg.get("universal_concerns", [])
        if universal:
            md += "\n**다수 페르소나 공통 우려**:\n"
            for u in universal[:2]:
                md += f"- **{u['theme']}** ({u.get('frequency', 0)}건): {(u.get('examples') or [''])[0][:140]}\n"
        md += "\n"

    # ── Portfolio Allocation ───────────────────────────────────────────
    md += "---\n\n## IV. Portfolio Allocation 권고\n\n"
    md += "| 종목 | Action | Target Quantity | Target Value | Position Limit |\n"
    md += "|---|---|---|---|---|\n"
    total_target = 0
    for d in decisions:
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker)
        name = info.get("kr", ticker)
        action = d.get("action", "-").upper()
        qty = d.get("target_quantity", 0)
        val = d.get("target_value", 0)
        limit = d.get("position_limit_value", 0)
        total_target += val if action == "BUY" else 0
        md += f"| {ticker} {name} | {action} | {qty:,}주 | ₩{val:,} | ₩{limit:,} |\n"
    md += f"\n**총 BUY 목표 금액**: ₩{total_target:,}\n"

    # ── Risk factors ───────────────────────────────────────────────────
    md += "\n---\n\n## V. 핵심 Risk 요인 (Top 5)\n\n"
    all_risks = []
    for d in decisions:
        for r in d.get("primary_risks", []):
            all_risks.append(r)
    seen = set()
    deduped = []
    for r in all_risks:
        key = r[:50]
        if key not in seen:
            seen.add(key)
            deduped.append(r)
    for i, r in enumerate(deduped[:5], 1):
        md += f"{i}. {r}\n"

    # ── Footer ─────────────────────────────────────────────────────────
    md += f"""

---

## VI. 분석 메타데이터

- **분석 방법**: 13명 페르소나 패널 + 4-Analyst (Macro/Industry/Empirical/Counter) + Deep Research
- **시장 데이터**: yfinance + DART (한국) + SEC EDGAR (미국) + NewsAPI/Finnhub (뉴스)
- **저장 경로**: `{pipeline_dir.as_posix()}`
- **Layer 1 (deep)**: `reports/combined/*.pdf` — 종목별 44-52p 상세 보고서
- **Layer 2 (overview)**: `reports/overview/overview.{{md,pdf,pptx}}` — 통합 요약 (이 문서)

---

*본 보고서는 paper portfolio simulation 자료이며, 실제 투자 권유가 아닙니다. 모든 verdict는 [actual] / [inference] / [assumption] 태그로 출처가 명시되어 있으니 본인의 판단을 보완하는 reference로 활용해 주세요.*
"""
    return md


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline-dir", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    md = render(Path(args.pipeline_dir))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(md)
    print(f"[md] saved {args.output} ({len(md):,} chars)")


if __name__ == "__main__":
    main()
