#!/usr/bin/env python3
"""Build ONE combined PDF (R1 + R2 + R3 + Deep Research) for a single ticker.

Usage:
  python build_combined.py \\
      --ticker 005490.KS \\
      --meta meta.json \\
      --stocks stocks.json \\
      --thesis thesis.json \\
      --eval-dir evals/ \\
      --persona-aggregate aggregate.json \\
      --persona-full results/ \\
      --risk-limits risks.json \\
      --decisions decisions.json \\
      --portfolio portfolio.json \\
      --deep-research deep_research.json   # optional Bull/Base/Bear etc.
      --output 005490.KS_POSCO홀딩스_combined.pdf
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from weasyprint import HTML, CSS

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "_common"))
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "quant-anchor-report" / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "persona-panel-report" / "scripts"))
sys.path.insert(0, str(PLUGIN_ROOT / "skills" / "executive-summary" / "scripts"))

from css import CSS_BASE, fmt_money_krw, fmt_pct, VERDICT_COLOR, VERDICT_KOR  # type: ignore
from ticker_resolver import format_ticker_with_name, format_ticker_html, resolve_ticker
from metric_glossary import (
    render_metric_glossary,
    render_data_tag_education,
    VERDICT_INTERPRETATION,
    CONFIDENCE_INTERPRETATION,
)
import deep_research as dr
import chart_utils as cu
from etf_holdings import render_etf_holdings, ETF_HOLDINGS
from reverse_dcf import auto_reverse_dcf
from subagent_debate import get_debate_for_ticker, render_debate_section
from news_disclosures import render_news_timeline, NEWS_TIMELINE
from emoji_replace import remove_emoji
from financial_fetcher import fetch_financials_for_deep_research, get_status as fin_status
from currency_format import format_price, format_amount_local
from company_intro import render_company_intro
from guru_checklist import render_guru_checklist

# Import section renderers from existing builders
import build_r1 as r1_mod  # type: ignore
import build_r2 as r2_mod  # type: ignore
import build_r3 as r3_mod  # type: ignore


def _read_json(path: str | None) -> dict | list:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def render_combined_cover(ticker: str, meta: dict, persona_agg: dict | None) -> str:
    """Combined cover — single ticker focus with company name."""
    info = resolve_ticker(ticker)
    company_kr = info.get("kr", ticker)
    company_en = info.get("en", "")
    sector = info.get("sector", "")

    dist = (persona_agg or {}).get("verdict_distribution", {}) if persona_agg else {}
    bull = dist.get("lean_bullish", {"count": 0})
    neu = dist.get("neutral", {"count": 0})
    bear = dist.get("lean_bearish", {"count": 0})
    avg_conf = (persona_agg or {}).get("average_confidence", 0)

    return f"""
    <div class="cover">
      <p class="cover-meta">Combined Investment Report · Deep Research · {meta.get('date', '')}</p>
      <h1 style="font-size:28pt;line-height:1.2;">{company_kr}</h1>
      <p style="font-size:13pt;color:#475569;margin-top:6pt;">
        <code style="font-size:13pt;">{ticker}</code>
        <span style="color:#94a3b8;"> · </span>
        {company_en}
      </p>
      <p style="font-size:11pt;color:#64748b;margin-top:2pt;">{sector}</p>

      <div class="info" style="margin-top:1.5cm;">
        <strong>이 보고서</strong>는 R1 (정량 anchor) + R2 (13명 페르소나 패널) + R3 (의사결정 시트) +
        Deep Research (산업·재무·시나리오)를 <strong>하나의 PDF</strong>로 통합한 종합 분석 문서입니다.
        <br/><br/>
        <strong>출처 블로그</strong>: {meta.get('blog_url', '-')}<br/>
        <strong>제목</strong>: {meta.get('title', '-')}
      </div>

      <div class="kpi-grid" style="margin-top:1cm;">
        <div class="kpi"><div class="num green">{bull.get('count', 0)}</div><div class="label">매수 성향</div></div>
        <div class="kpi"><div class="num amber">{neu.get('count', 0)}</div><div class="label">중립</div></div>
        <div class="kpi"><div class="num red">{bear.get('count', 0)}</div><div class="label">매도 성향</div></div>
        <div class="kpi"><div class="num">{int((avg_conf or 0)*100)}%</div><div class="label">평균 신뢰도</div></div>
      </div>

      <div class="warn" style="margin-top:1cm;">
        ⚠️ <strong>면책 사항</strong>: 본 보고서는 paper portfolio simulation이며, 실제 투자 권유가 아닙니다.
        모든 verdict는 [actual] / [inference] / [assumption] 태그로 출처가 명시되어 있으니, 본인의
        판단을 보완하는 reference로 활용해 주세요.
      </div>
    </div>
    """


def render_company_intro_with_metrics(ticker: str, stocks: list[dict]) -> str:
    """회사 소개 + PER/PBR/EV/EBITDA 등 핵심 지표 + 5년 재무 변동 통합."""
    base_intro = render_company_intro(ticker)
    if not base_intro:
        # No intro data — minimal fallback
        info = resolve_ticker(ticker)
        base_intro = f"""
        <h2>📋 회사 소개 (Company Profile)</h2>
        <div class="info">
          <strong>{info.get('kr', ticker)}</strong> ({ticker}) · {info.get('sector', '-')}<br/>
          (회사 상세 프로파일 데이터 미등록 — company_intro.py에 추가 필요)
        </div>
        """

    # Find market data for this ticker
    s = next((s for s in stocks if s.get("ticker") == ticker), {})
    m = s.get("market_data", {})
    if not m:
        return base_intro

    currency = m.get("currency", "USD")
    price = m.get("current_price", 0)
    as_of = m.get("as_of_date", "-")
    pe_fwd = m.get("forward_pe")
    pe_trail = m.get("trailing_pe")
    pb = m.get("pb")
    ev_ebitda = m.get("ev_ebitda")
    div_y = m.get("div_yield_pct", 0)
    beta = m.get("beta")
    mc_local = m.get("market_cap_local_bn", 0)
    mc_usd = m.get("market_cap_usd_bn", 0)

    metrics_html = f"""
    <h3>주요 지표 (Valuation Snapshot · 조회일 {as_of})</h3>
    <table class="dt">
      <tr>
        <th style="width:20%">현재가</th>
        <td><strong>{format_price(price, currency)}</strong></td>
        <th style="width:20%">시가총액</th>
        <td><strong>{format_amount_local(mc_local * 1e9, currency)}</strong> ({format_amount_local(mc_usd * 1e9, "USD")})</td>
      </tr>
      <tr>
        <th>Forward PE</th>
        <td>{pe_fwd if pe_fwd is not None else '-'}</td>
        <th>Trailing PE</th>
        <td>{pe_trail if pe_trail is not None else '-'}</td>
      </tr>
      <tr>
        <th>PB (Price/Book)</th>
        <td>{pb if pb is not None else '-'}</td>
        <th>EV/EBITDA</th>
        <td>{ev_ebitda if ev_ebitda is not None else '-'}</td>
      </tr>
      <tr>
        <th>배당수익률</th>
        <td>{div_y:.2f}%</td>
        <th>베타 (5Y)</th>
        <td>{beta if beta is not None else '-'}</td>
      </tr>
      <tr>
        <th>1M 수익률</th>
        <td>{m.get('return_1m_pct', 0):+.1f}%</td>
        <th>3M 수익률</th>
        <td>{m.get('return_3m_pct', 0):+.1f}%</td>
      </tr>
      <tr>
        <th>6M 수익률</th>
        <td>{m.get('return_6m_pct', 0):+.1f}%</td>
        <th>1Y 수익률</th>
        <td>{m.get('return_1y_pct', 0):+.1f}% {'⚠ data anomaly' if m.get('return_1y_pct', 0) and abs(m.get('return_1y_pct', 0)) > 1500 else ''}</td>
      </tr>
      <tr>
        <th>연환산 변동성</th>
        <td>{m.get('volatility_annualized_pct', 0):.1f}%</td>
        <th>데이터 출처</th>
        <td><span style="font-size:9pt;color:#16a34a;">{m.get('fetched_via', '-')}</span></td>
      </tr>
    </table>
    <p style="font-size:9pt;color:#6b7280;">
      * 시장 데이터는 {as_of} 기준 yfinance live fetch.
      * Forward PE는 향후 12개월 예상 EPS 기준, Trailing PE는 직전 12개월 실적 기준.
      * PE &lt; 12 deep value, 12-20 fair, 20-30 premium, 30+ expensive growth.
      * EV/EBITDA &lt; 8 cheap, 8-12 fair, 12+ premium.
    </p>
    """

    return base_intro + metrics_html


def render_brief_and_thesis_combined(ticker: str, decisions: list[dict],
                                       persona_agg: dict | None, theses: list[dict],
                                       stocks: list[dict] = None) -> str:
    """Executive Brief + 전체 Thesis List 통합 (요청 #1)."""
    company = resolve_ticker(ticker).get("kr", ticker)
    my_decision = next((d for d in decisions if d.get("ticker") == ticker), {})
    action = my_decision.get("action", "-")
    action_color = {"buy": "#16a34a", "sell_all": "#dc2626", "sell_partial": "#dc2626"}.get(action, "#ca8a04")
    signal = my_decision.get("signal_score", 0)
    target_value = my_decision.get("target_value", 0)
    target_qty = my_decision.get("target_quantity", 0)

    currency = "KRW"
    if stocks:
        s = next((s for s in stocks if s.get("ticker") == ticker), {})
        currency = s.get("market_data", {}).get("currency", "KRW")

    dist = (persona_agg or {}).get("verdict_distribution", {})
    bull = dist.get("lean_bullish", {}).get("count", 0)
    neu = dist.get("neutral", {}).get("count", 0)
    bear = dist.get("lean_bearish", {}).get("count", 0)

    # ── Executive Brief ─────────────────────────────────────────────
    body = f"""
    <h1 style="page-break-before:always;">📋 Executive Brief & 전체 Thesis List — {company}</h1>

    <h2>① Executive Brief (TL;DR)</h2>
    <div class="info" style="font-size:11pt;line-height:1.7;">
      <strong>한 줄 요약</strong>: {company} ({ticker}) — 13명 페르소나 패널 결과
      매수 {bull} / 중립 {neu} / 매도 {bear}, signal score
      <strong style="color:{action_color};">{signal:+.2f}</strong> →
      portfolio manager 권고
      <strong style="color:{action_color};">{action.upper()}</strong>
      ({target_qty:,}주, {format_amount_local(target_value, currency)}).
    </div>

    <h3>왜 이 액션인가?</h3>
    <ul style="font-size:10pt;line-height:1.7;">
      <li><strong>합의도</strong>: 13명 중 {bull}명이 lean_bullish ({(bull/13*100):.0f}%) →
          {'강한 매수 합의' if bull >= 9 else '중간 합의' if bull >= 6 else '합의 부족, 본인 판단 필요'}</li>
      <li><strong>Signal Score</strong>: {signal:+.2f} →
          {'+0.7 이상이면 한도까지 매수' if signal >= 0.7 else '+0.3-0.7면 한도의 50%' if signal >= 0.3 else '±0.3 이내는 hold' if abs(signal) < 0.3 else 'sell'}
          가이드 적용</li>
      <li><strong>주의 사항</strong>: 13명 중 challenge한 페르소나의 우려 사항을 본 보고서 §5에서 확인 필요</li>
    </ul>
    """

    # ── 전체 Thesis List ─────────────────────────────────────────────
    if theses:
        rows = ""
        for t in theses:
            cid = t.get("claim_id", "")
            claim = t.get("claim", "")
            type_ = t.get("type", "")
            importance = t.get("importance", "")
            timeframe = t.get("timeframe", "")
            evidence = t.get("supporting_evidence", "")
            type_color = "#16a34a" if type_ == "factual" else "#f59e0b"

            rows += f"""
            <tr>
              <td style="vertical-align:top;font-weight:bold;color:#0d47a1;">{cid}</td>
              <td>
                <strong style="font-size:10.5pt;">{claim}</strong><br/>
                <span style="font-size:9pt;color:#475569;">📎 근거: {evidence}</span>
              </td>
              <td style="text-align:center;vertical-align:top;">
                <span style="background:{type_color};color:white;padding:2pt 6pt;border-radius:3pt;font-size:8.5pt;">{type_}</span><br/>
                <span style="font-size:8pt;color:#6b7280;margin-top:3pt;display:inline-block;">{importance}<br/>{timeframe}</span>
              </td>
            </tr>"""

        body += f"""
        <h2 style="margin-top:18pt;">② 전체 Thesis List ({len(theses)}개)</h2>
        <div class="info">
          블로거가 제시한 모든 thesis를 분석 진입 전에 정리합니다.
          각 thesis는 <strong>type</strong> (factual / predictive),
          <strong>importance</strong> (core / supporting),
          <strong>timeframe</strong> (present / short_term / medium_term / long_term)으로 분류됩니다.
        </div>
        <table class="dt">
          <thead>
            <tr>
              <th style="width:7%">ID</th>
              <th>Thesis 전문 + 근거</th>
              <th style="width:14%;text-align:center;">분류</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
        <p style="font-size:9pt;color:#6b7280;margin-top:6pt;">
          ✓ 본 list 전체가 다음 섹션의 4-Analyst 평가 + 13명 페르소나 lens application의 input입니다.
        </p>
        """

    return body


def render_full_thesis_list(theses: list[dict]) -> str:
    """전체 thesis list (8-12개) — 분석 시작 전 완전한 list 제시. truncation 없음."""
    if not theses:
        return ""

    rows = ""
    for t in theses:
        cid = t.get("claim_id", "")
        claim = t.get("claim", "")
        type_ = t.get("type", "")
        importance = t.get("importance", "")
        timeframe = t.get("timeframe", "")
        evidence = t.get("supporting_evidence", "")
        type_color = "#16a34a" if type_ == "factual" else "#f59e0b"

        rows += f"""
        <tr>
          <td style="vertical-align:top;font-weight:bold;color:#0d47a1;">{cid}</td>
          <td>
            <strong style="font-size:10.5pt;">{claim}</strong><br/>
            <span style="font-size:9pt;color:#475569;">📎 근거: {evidence}</span>
          </td>
          <td style="text-align:center;vertical-align:top;">
            <span style="background:{type_color};color:white;padding:2pt 6pt;border-radius:3pt;font-size:8.5pt;">{type_}</span><br/>
            <span style="font-size:8pt;color:#6b7280;margin-top:3pt;display:inline-block;">{importance}<br/>{timeframe}</span>
          </td>
        </tr>"""

    return f"""
    <h1 style="page-break-before:always;">📑 전체 Thesis List (분석 진입 전 정리)</h1>
    <div class="info">
      블로거가 제시한 모든 thesis ({len(theses)}개)를 분석 진입 전에 정리합니다.
      각 thesis는 <strong>type</strong> (factual = 사실 검증 가능 / predictive = 미래 가정),
      <strong>importance</strong> (core = 결정적 / supporting = 보조),
      <strong>timeframe</strong> (present / short_term / medium_term / long_term)으로 분류됩니다.
    </div>
    <table class="dt">
      <thead>
        <tr>
          <th style="width:7%">ID</th>
          <th>Thesis 전문 + 근거</th>
          <th style="width:14%;text-align:center;">분류</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;margin-top:6pt;">
      ✓ 본 list 전체가 다음 섹션의 4-Analyst 평가 + 13명 페르소나 lens application의 input입니다.
    </p>
    """


def render_executive_brief(ticker: str, decisions: list[dict], persona_agg: dict | None,
                            theses: list[dict], stocks: list[dict] = None) -> str:
    """Executive brief — TL;DR for this single ticker (positioned right after cover)."""
    company = resolve_ticker(ticker).get("kr", ticker)
    my_decision = next((d for d in decisions if d.get("ticker") == ticker), {})
    action = my_decision.get("action", "-")
    action_color = {"buy": "#16a34a", "sell_all": "#dc2626", "sell_partial": "#dc2626"}.get(action, "#ca8a04")
    signal = my_decision.get("signal_score", 0)
    target_value = my_decision.get("target_value", 0)
    target_qty = my_decision.get("target_quantity", 0)

    # Get currency from stocks data
    currency = "KRW"
    if stocks:
        s = next((s for s in stocks if s.get("ticker") == ticker), {})
        currency = s.get("market_data", {}).get("currency", "KRW")

    # Verdict mix
    dist = (persona_agg or {}).get("verdict_distribution", {})
    bull = dist.get("lean_bullish", {}).get("count", 0)
    neu = dist.get("neutral", {}).get("count", 0)
    bear = dist.get("lean_bearish", {}).get("count", 0)

    core_theses = [t for t in theses if t.get("importance") == "core"][:3]
    thesis_html = "".join(
        f"<li><strong>{t.get('claim_id', '?')}</strong>: {t.get('claim', '')}</li>"
        for t in core_theses
    ) or "<li>thesis 데이터 없음</li>"

    return f"""
    <h1 style="page-break-before:always;">📋 Executive Brief — {company}</h1>
    <div class="info" style="font-size:11pt;line-height:1.7;">
      <strong>한 줄 요약</strong>: {company} ({ticker}) — 13명 페르소나 패널 결과
      매수 {bull} / 중립 {neu} / 매도 {bear}, signal score
      <strong style="color:{action_color};">{signal:+.2f}</strong> →
      portfolio manager 권고
      <strong style="color:{action_color};">{action.upper()}</strong>
      ({target_qty:,}주, {format_amount_local(target_value, currency)}).
    </div>

    <h3>핵심 주장 (블로거 thesis 상위 3개)</h3>
    <ol style="font-size:10pt;line-height:1.7;">{thesis_html}</ol>

    <h3>왜 이 액션인가?</h3>
    <ul style="font-size:10pt;line-height:1.7;">
      <li><strong>합의도</strong>: 13명 중 {bull}명이 lean_bullish ({(bull/13*100):.0f}%) →
          {'강한 매수 합의' if bull >= 9 else '중간 합의' if bull >= 6 else '합의 부족, 본인 판단 필요'}</li>
      <li><strong>Signal Score</strong>: {signal:+.2f} →
          {'+0.7 이상이면 한도까지 매수' if signal >= 0.7 else '+0.3-0.7면 한도의 50%' if signal >= 0.3 else '±0.3 이내는 hold' if abs(signal) < 0.3 else 'sell'}
          가이드 적용</li>
      <li><strong>주의 사항</strong>: 13명 중 challenge한 페르소나의 우려 사항을 본 보고서 §5에서 확인 필요</li>
    </ul>
    """


def render_persona_section_for_ticker(persona_agg: dict, persona_full: dict, theses: list[dict],
                                       ticker: str) -> str:
    """R2 sections adapted for single-ticker focus."""
    if not persona_agg:
        return f"<h1 style='page-break-before:always;'>R2 페르소나 패널 데이터 없음</h1>"

    company = resolve_ticker(ticker).get("kr", ticker)
    meta_for_r2 = {"ticker": ticker, "date": "", "subjects": company}

    body = '<h1 style="page-break-before:always;">R2. Persona Panel (13명 대가 패널)</h1>'
    body += f'<p class="cover-meta">대상: <code>{ticker}</code> {company}</p>'

    body += r2_mod.render_persona_table(persona_agg.get("persona_results", {}))
    body += r2_mod.render_style_split(persona_agg, persona_agg.get("persona_results", {}))

    if theses and persona_full:
        body += r2_mod.render_thesis_persona_matrix(persona_full, theses)
    body += r2_mod.render_universal_concerns(persona_agg)
    body += r2_mod.render_persona_details(persona_full or persona_agg.get("persona_results", {}))
    return body


def render_quant_section(stocks: list[dict], theses: list[dict], evals: dict,
                          risk_limits: dict, ticker: str) -> str:
    """R1 sections — keep all stocks for context but highlight the focus ticker."""
    company = resolve_ticker(ticker).get("kr", ticker)
    body = '<h1 style="page-break-before:always;">R1. Quant Anchor — 정량 데이터</h1>'
    body += f'<p class="cover-meta">중점 분석 대상: <code>{ticker}</code> {company} (참고: 같이 언급된 종목 비교 포함)</p>'

    body += render_metric_glossary()
    body += r1_mod.render_fundamentals(stocks)

    if theses and evals:
        body += r1_mod.render_4analyst(theses, evals)
        body += r1_mod.render_data_tags_summary(theses, evals)
        body += render_data_tag_education()

    if risk_limits.get("limits"):
        body += r1_mod.render_risk(risk_limits)

    return body


def render_decision_section(decisions: list[dict], portfolio: dict, theses: list[dict],
                              eval_data: dict, persona_aggregates: dict, ticker: str) -> str:
    """R3 sections — focused on this ticker."""
    body = '<h1 style="page-break-before:always;">R3. Executive Summary — 의사결정 시트</h1>'

    # Filter to this ticker first, then include others as context
    my_decisions = [d for d in decisions if d.get("ticker") == ticker]
    other_decisions = [d for d in decisions if d.get("ticker") != ticker]
    body += r3_mod.build_decision_sheet(my_decisions + other_decisions, portfolio)

    # Verdict / Confidence interpretation guide
    body += "<h2>📚 Verdict · Confidence 해석 가이드</h2>"
    body += '<table class="dt"><thead><tr><th>Verdict</th><th>의미</th></tr></thead><tbody>'
    for v, desc in VERDICT_INTERPRETATION.items():
        body += f"<tr><td><strong>{v}</strong></td><td>{desc}</td></tr>"
    body += "</tbody></table>"
    body += "<h3>Confidence 의미</h3>"
    body += '<table class="dt"><thead><tr><th>Confidence</th><th>의미</th></tr></thead><tbody>'
    for c, desc in CONFIDENCE_INTERPRETATION.items():
        body += f"<tr><td><strong>{c.replace('_', ' ').title()}</strong></td><td>{desc}</td></tr>"
    body += "</tbody></table>"

    body += r3_mod.render_thesis_summary({"summary_one_liner": "", "theses": theses})
    body += r3_mod.render_quant_validation(eval_data)
    if persona_aggregates:
        body += r3_mod.render_persona_consensus(persona_aggregates)
    body += r3_mod.render_key_risks(theses, my_decisions)
    body += r3_mod.render_monitor_points(theses)
    return body


def render_deep_research_section(deep: dict, ticker: str, current_price: float = 0,
                                   currency: str = "KRW", thesis_eval: dict | None = None) -> str:
    """Deep Research-style sections — industry, financials, scenarios, catalysts, risks.

    thesis_eval: thesis_eval/all_aggregate.json content — overlays 4-analyst evaluation
                 onto thesis_decomposition section (Sprint E-2 patch).
    """
    if not deep:
        return ""

    company = resolve_ticker(ticker).get("kr", ticker)
    # NOTE: page-break는 caller의 <div>가 담당 (중복 시 blank page 발생)
    body = f'<h1>🔬 Deep Research — {company} 심층 분석</h1>'
    body += '<div class="info">전문 sell-side 보고서 형식의 심층 분석 — 산업 맥락, 5년 재무, 시나리오, 카탈리스트, 리스크 매트릭스를 포함합니다.</div>'

    if "thesis_decomposition" in deep:
        body += dr.render_thesis_decomposition(deep["thesis_decomposition"], thesis_eval=thesis_eval)

    if "industry" in deep:
        ind = deep["industry"]
        body += dr.render_industry_context(
            industry=ind.get("name", "-"),
            overview=ind.get("overview", "-"),
            competitive_landscape=ind.get("competitors", []),
            recent_news=ind.get("news", []),
            market_size=ind.get("market_size"),
        )

    if "financials" in deep:
        fin = deep["financials"]
        body += dr.render_financial_deep_dive(
            ticker=ticker,
            pl_5y=fin.get("pl_5y", []),
            bs_snapshot=deep.get("bs_snapshot") or fin.get("bs_snapshot", {}),
            cf_summary=deep.get("cf_summary") or fin.get("cf_summary", {}),
            peer_compare=fin.get("peer_compare", []),
            financial_unit=deep.get("financial_unit") or fin.get("financial_unit"),
        )

    if "scenarios" in deep:
        sc = deep["scenarios"]
        if all(k in sc for k in ("bull", "base", "bear")) and current_price:
            body += dr.render_scenarios(
                bull=sc["bull"], base=sc["base"], bear=sc["bear"],
                current_price=current_price, currency=currency,
            )

    if "catalysts" in deep:
        body += dr.render_catalyst_timeline(deep["catalysts"])

    if "risks" in deep:
        body += dr.render_risk_matrix(deep["risks"])

    if "korean_disclosures" in deep and deep["korean_disclosures"]:
        body += dr.render_korean_disclosure_check(ticker, deep["korean_disclosures"])

    return body


def render_specialist_agents_section(ticker: str, pdir) -> str:
    """Render specialist-agents plugin output (Tier 2 — Anthropic Financial Services Agents pattern)."""
    from pathlib import Path as _Path
    import json as _json

    pdir = _Path(pdir)
    sections = []

    # Research Manager
    ri_path = pdir / "research_intel" / f"{ticker}_sector.json"
    if ri_path.exists():
        try:
            ri = _json.loads(ri_path.read_text(encoding="utf-8"))
            dev_rows = "".join(
                f"<tr><td>{d.get('date','-')}</td><td>{d.get('headline', d.get('event','-'))}</td><td>{d.get('impact', d.get('expected_impact','○'))}</td></tr>"
                for d in (ri.get("sector_developments_30d", []) + ri.get("issuer_developments_30d", []))[:5]
            )
            sections.append(f"""
            <h2>🧭 Research Manager — Sector & Issuer Intelligence</h2>
            <div class="info">Anthropic Financial Services Market Researcher 패턴 (2026-05) — sector·issuer 동향 종합. 페르소나 lens 적용 전 정량 anchor.</div>
            <table class="dt"><tr><th>섹터</th><td>{ri.get('sector','-')}</td></tr>
              <tr><th>경쟁사 수</th><td>{ri.get('competitive_intel',{}).get('peer_count','-')}</td></tr>
              <tr><th>Tailwinds</th><td>{', '.join(ri.get('tailwinds', [])) or '-'}</td></tr>
              <tr><th>Headwinds</th><td>{', '.join(ri.get('headwinds', [])) or '-'}</td></tr>
              <tr><th>Credit risk flags</th><td>{', '.join(ri.get('credit_risk_flags', [])) or '없음'}</td></tr>
            </table>
            <h3>최근 30일 sector·issuer development</h3>
            <table class="dt"><thead><tr><th style="width:14%">날짜</th><th>내용</th><th style="width:8%">영향</th></tr></thead><tbody>{dev_rows or '<tr><td colspan="3" style="text-align:center;color:#9ca3af;">최근 30일 신규 development 부재</td></tr>'}</tbody></table>
            """)
        except Exception as e:
            sections.append(f"<p style='color:#dc2626;'>Research Manager 파싱 실패: {e}</p>")

    # Sentiment Analyst
    sa_path = pdir / "sentiment" / f"{ticker}_score.json"
    if sa_path.exists():
        try:
            sa = _json.loads(sa_path.read_text(encoding="utf-8"))
            s30 = sa.get("news_sentiment_30d", 0)
            s_color = "#16a34a" if s30 > 0.3 else "#dc2626" if s30 < -0.3 else "#ca8a04"
            pos_rows = "".join(f"<li>{p['date']} — {p['headline']}</li>" for p in sa.get("key_drivers_positive", []))
            neg_rows = "".join(f"<li>{n['date']} — {n['headline']}</li>" for n in sa.get("key_drivers_negative", []))
            sections.append(f"""
            <h2>💭 Sentiment Analyst — News & Social Mood</h2>
            <div class="info">PrimoAgent NLP + TradingAgents Researcher 패턴. news impact flag aggregation.</div>
            <table class="dt">
              <tr><th>30일 sentiment</th><td><strong style="color:{s_color};font-size:14pt;">{s30:+.2f}</strong> (n={sa.get('n_items_30d', 0)})</td></tr>
              <tr><th>90일 sentiment</th><td>{sa.get('news_sentiment_90d', 0):+.2f}</td></tr>
              <tr><th>365일 sentiment</th><td>{sa.get('news_sentiment_365d', 0):+.2f}</td></tr>
              <tr><th>30d vs 90d trend</th><td>{sa.get('trend_30d_vs_90d', 0):+.2f}</td></tr>
              <tr><th>Confidence</th><td>{sa.get('confidence', '-')}</td></tr>
              <tr><th>Calibration</th><td>{sa.get('calibration_check', '-')}</td></tr>
            </table>
            <h3>긍정 driver (최근 30일)</h3><ul style="font-size:9.5pt;">{pos_rows or '<li style="color:#9ca3af;">강한 긍정 driver 부재</li>'}</ul>
            <h3>부정 driver (최근 30일)</h3><ul style="font-size:9.5pt;">{neg_rows or '<li style="color:#9ca3af;">부정 driver 부재</li>'}</ul>
            """)
        except Exception as e:
            sections.append(f"<p style='color:#dc2626;'>Sentiment Analyst 파싱 실패: {e}</p>")

    # Earnings Reviewer
    er_path = pdir / "earnings_review" / f"{ticker}_latest.json"
    if er_path.exists():
        try:
            er = _json.loads(er_path.read_text(encoding="utf-8"))
            km = er.get("key_metrics", {})
            tone = er.get("management_tone", {})
            thesis_rows = "".join(
                f"<tr><td><strong>{t.get('thesis_id','-')}</strong></td><td>{(t.get('claim','-') or '-')[:100]}</td><td>{t.get('impact_direction','-')}</td><td>{t.get('confidence_delta','-')}</td></tr>"
                for t in er.get("thesis_impact", [])[:5]
            )
            sections.append(f"""
            <h2>📊 Earnings Reviewer — Thesis-Relevant Change Extraction</h2>
            <div class="info">Anthropic Earnings Reviewer Agent 패턴 (2026-05). 최근 실적 → thesis verdict impact 자동 추출.</div>
            <table class="dt">
              <tr><th>최근 결산</th><td>{er.get('latest_period','-')} vs {er.get('comparison_period','-')}</td></tr>
              <tr><th>매출 YoY</th><td>{km.get('revenue',{}).get('actual','-'):,} ({km.get('revenue',{}).get('yoy_pct','-')}%)</td></tr>
              <tr><th>영업이익 YoY</th><td>{km.get('op_income',{}).get('actual','-'):,} ({km.get('op_income',{}).get('yoy_pct','-')}%)</td></tr>
              <tr><th>영업이익률 변화</th><td>{km.get('op_margin',{}).get('actual','-')}% ({km.get('op_margin',{}).get('delta_bps','-'):+.0f}bps)</td></tr>
              <tr><th>경영진 톤</th><td><strong>{tone.get('label','-')}</strong> (점수 {tone.get('score','-')})</td></tr>
              <tr><th>Red flags</th><td>{', '.join(er.get('red_flags', [])) or '없음'}</td></tr>
            </table>
            <h3>Thesis impact 추출</h3>
            <table class="dt"><thead><tr><th>ID</th><th>Claim</th><th>방향</th><th>Δconf</th></tr></thead><tbody>{thesis_rows or '<tr><td colspan="4" style="text-align:center;color:#9ca3af;">최근 실적과 직접 정렬된 thesis 없음</td></tr>'}</tbody></table>
            """)
        except Exception as e:
            sections.append(f"<p style='color:#dc2626;'>Earnings Reviewer 파싱 실패: {e}</p>")

    # Model Builder
    mb_path = pdir / "models" / f"{ticker}_dcf.json"
    if mb_path.exists():
        try:
            mb = _json.loads(mb_path.read_text(encoding="utf-8"))
            dcf = mb.get("dcf_summary", {})
            ls = mb.get("long_short_signal", "-")
            ls_color = "#16a34a" if "Long" in ls else "#dc2626" if "Short" in ls else "#ca8a04"
            peer = mb.get("peer_multiple_check", {})
            sections.append(f"""
            <h2>📐 Model Builder — DCF + Reverse-DCF + L/S Signal</h2>
            <div class="info">Anthropic Model Builder + LangAlpha L/S Hedge Fund 패턴. probability-weighted scenario synthesis.</div>
            <table class="dt">
              <tr><th>현재가</th><td>{mb.get('current_price','-'):,} {mb.get('currency','')}</td></tr>
              <tr><th>기대 가격 (확률 가중)</th><td>{dcf.get('scenarios_weighted_target','-'):,} ({dcf.get('expected_upside_pct','-'):+.1f}%)</td></tr>
              <tr><th>Bull (확률 {dcf.get('bull',{}).get('prob','-')}%)</th><td>{dcf.get('bull',{}).get('target','-'):,} — {dcf.get('bull',{}).get('thesis','-')[:80]}</td></tr>
              <tr><th>Base (확률 {dcf.get('base',{}).get('prob','-')}%)</th><td>{dcf.get('base',{}).get('target','-'):,} — {dcf.get('base',{}).get('thesis','-')[:80]}</td></tr>
              <tr><th>Bear (확률 {dcf.get('bear',{}).get('prob','-')}%)</th><td>{dcf.get('bear',{}).get('target','-'):,} — {dcf.get('bear',{}).get('thesis','-')[:80]}</td></tr>
              <tr><th>Reverse-DCF</th><td>{mb.get('reverse_dcf_check',{}).get('embedded_in_current_price','-')}</td></tr>
              <tr><th>Peer multiple</th><td>Forward PE {peer.get('current_fwd_pe','-')} vs peer avg {peer.get('peer_avg_pe','-')} → <strong>{peer.get('relative_position','-')}</strong></td></tr>
              <tr><th>L/S Signal</th><td><strong style="color:{ls_color};font-size:13pt;">{ls}</strong></td></tr>
            </table>
            """)
        except Exception as e:
            sections.append(f"<p style='color:#dc2626;'>Model Builder 파싱 실패: {e}</p>")

    if not sections:
        return ""
    return '<h1 style="page-break-before:always;">🤖 Specialist Agents — Tier 2 Augmentation</h1>' + \
           '<div class="info">Anthropic Financial Services Agents (2026-05) + TradingAgents/LangAlpha 패턴 기반 추가 분석 layer. 13 persona panel + 4-Analyst lens를 보완하는 정량·정성 anchor.</div>' + \
           "".join(sections)


def render_appendix_glossary() -> str:
    """Final appendix — full glossary for self-study."""
    body = '<h1 style="page-break-before:always;">📚 부록 — 학습용 용어 사전</h1>'
    body += '<div class="info">이 보고서를 처음 보시는 분을 위한 모든 용어 풀이 모음입니다.</div>'
    body += render_metric_glossary()
    body += render_data_tag_education()

    body += """
    <h2>이 보고서의 분석 방법론</h2>
    <ol style="font-size:10pt;line-height:1.8;">
      <li><strong>Stage 1 — Blog scraping</strong>: 블로거 글을 자동 수집하고 댓글까지 함께 분석</li>
      <li><strong>Stage 2 — Thesis extraction</strong>: 블로거의 주장을 검증 가능한 6-12개 thesis로 분해</li>
      <li><strong>Stage 3 — Stock identification</strong>: thesis에서 직간접 수혜 종목 자동 추출 (top 3-5개 선정)</li>
      <li><strong>Stage 4 — 4-Analyst evaluation</strong>: Macro/Industry/Empirical/Counter 4명이 각 thesis를 평가</li>
      <li><strong>Stage 5 — Quant fundamentals</strong>: yfinance로 PE·베타·변동성·1M/3M/1Y 수익률 자동 수집</li>
      <li><strong>Stage 6 — 13 Persona panel</strong>: Buffett·Munger·Lynch 등 13명 대가의 lens로 verdict + confidence + horizon 평가</li>
      <li><strong>Stage 7 — Risk-adjusted sizing</strong>: 변동성 기반 vol_multiplier로 단일 종목 최대 한도 결정</li>
      <li><strong>Stage 8 — Portfolio decision</strong>: signal_score (가중 평균 verdict) → BUY/HOLD/SELL 액션</li>
    </ol>
    """
    return body


def main():
    parser = argparse.ArgumentParser(description="Combined R1+R2+R3+Deep Research single-PDF builder for one ticker")
    parser.add_argument("--ticker", required=True, help="Focus ticker (e.g. 005490.KS)")
    parser.add_argument("--meta", help="meta.json: date/title/blog_url")
    parser.add_argument("--stocks", required=True, help="market_data list JSON")
    parser.add_argument("--thesis", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--persona-aggregate", help="aggregate.json for THIS ticker's panel")
    parser.add_argument("--persona-full", help="dir of {persona_id}.json files for this ticker")
    parser.add_argument("--persona-aggregates-all", help="dict of ticker → aggregate (for R3 cross-ticker view)")
    parser.add_argument("--risk-limits", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--deep-research", help="deep_research.json with industry/financials/scenarios/etc.")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    meta = _read_json(args.meta)
    stocks = _read_json(args.stocks) or []
    thesis_data = _read_json(args.thesis)
    theses = thesis_data.get("theses", []) if isinstance(thesis_data, dict) else (thesis_data if isinstance(thesis_data, list) else [])

    # Phase 5 (사용자 요청): Standalone 분석 자동 감지 + implicit thesis 보강
    # blog 글이 없거나 thesis가 비어있으면 deep_research + financial 데이터로 implicit thesis 생성
    if len(theses) < 3:
        try:
            from implicit_thesis_extractor import extract_implicit_theses
            # Get sector from stocks data
            sector_for_ticker = ""
            for s in stocks:
                if s.get("ticker") == args.ticker:
                    sector_for_ticker = s.get("sector") or s.get("kr_name") or ""
                    break
            # Get financials via the new module
            financials_data = {}
            try:
                from financial_statements_us_gaap import fetch_us_gaap_5y_5q
                financials_data = fetch_us_gaap_5y_5q(args.ticker)
            except Exception as e:
                print(f"[combined] financial_statements fetch for implicit thesis failed: {e}")

            deep_for_thesis = _read_json(args.deep_research) if args.deep_research else {}
            implicit_theses = extract_implicit_theses(
                ticker=args.ticker,
                sector=sector_for_ticker,
                deep_research=deep_for_thesis,
                financials=financials_data,
                user_provided_theses=theses if theses else None,
            )
            if implicit_theses and len(implicit_theses) > len(theses):
                print(f"[combined] Phase 5: implicit thesis 활성화 — {len(theses)}개 (입력) → {len(implicit_theses)}개 (보강)")
                theses = implicit_theses
        except ImportError as e:
            print(f"[combined] implicit_thesis_extractor not available: {e}")
        except Exception as e:
            print(f"[combined] implicit thesis extraction failed: {e}")

    # Thesis evaluation — use normalizer (handles both legacy 'aggregates' and v2 'evaluations' schemas)
    # 2026-05-12 fix: previously hardcoded for 'aggregates' key, silently dropped v2-schema files.
    try:
        from thesis_eval_normalizer import load_and_normalize as _normalize_eval
    except ImportError:
        # _common is on sys.path via _common_path injection; fall back if not yet on path
        import sys as _sys
        _sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_common"))
        from thesis_eval_normalizer import load_and_normalize as _normalize_eval

    eval_path = Path(args.eval_dir) / "all_aggregate.json"
    eval_data: dict = _normalize_eval(eval_path)
    if not eval_data and eval_path.exists():
        print(f"[combined] WARN: thesis_eval/{eval_path.name} present but no evaluations parsed — check schema (expect 'aggregates' or 'evaluations' list)")

    risk_limits = _read_json(args.risk_limits) or {"limits": []}
    decisions = (_read_json(args.decisions) or {}).get("decisions", [])
    portfolio = _read_json(args.portfolio) or {}

    persona_agg = _read_json(args.persona_aggregate) if args.persona_aggregate else {}
    persona_full = {}
    if args.persona_full:
        for p in Path(args.persona_full).glob("*.json"):
            if p.stem in ("aggregate", "panel_summary"):
                continue
            try:
                persona_full[p.stem] = _read_json(str(p))
            except Exception:
                pass

    persona_aggregates_all = _read_json(args.persona_aggregates_all) if args.persona_aggregates_all else {}

    deep = _read_json(args.deep_research) if args.deep_research else {}

    # ── Phase 7 절차 A: evidence/{ticker}.json 주입 (출처 URL 박힌 외부 근거) ──
    # evidence 파일이 있으면 industry.news 를 URL 인용 버전으로 prepend (graceful).
    if deep and args.deep_research:
        try:
            from evidence_retriever import EvidenceRetriever as _ER
            _pdir = Path(args.deep_research).resolve().parent.parent  # deep_research/{t}.json → pipeline_dir
            _ev_path = _pdir / "evidence" / f"{args.ticker}.json"
            deep = _ER.merge_into_deep(deep, _ev_path)
            deep = _ER.annotate_scenarios(deep, _ev_path)   # 시나리오 가정에 근거 배지
            if deep.get("_evidence", {}).get("injected"):
                _ev_meta = deep["_evidence"]
                print(f"[combined] evidence injected: {_ev_meta['news_with_url']} URL-backed items "
                      f"({_ev_meta['evidence_total']} total), "
                      f"scenarios annotated: {_ev_meta.get('scenarios_annotated', 0)}")
        except ImportError:
            pass
        except Exception as e:
            print(f"[combined] evidence injection skipped: {e}")

    # ── Auto-convert dict-by-year financials → pl_5y/bs_snapshot/cf_summary ──
    # (Sprint A-2 fix, 2026-05-28 — 미국 ticker LNG.json 형식 호환)
    if deep:
        try:
            from financial_format_helper import auto_convert_deep_research_financials
            deep = auto_convert_deep_research_financials(deep, ticker=args.ticker)
            fin = deep.get("financials") or {}
            if fin.get("pl_5y"):
                print(f"[combined] auto-converted financials: pl_5y={len(fin['pl_5y'])} years, "
                      f"bs_snapshot={'yes' if fin.get('bs_snapshot') else 'no'}, "
                      f"cf_summary={'yes' if fin.get('cf_summary') else 'no'}")
        except ImportError as e:
            print(f"[combined] financial_format_helper not available: {e}")
        except Exception as e:
            print(f"[combined] financials auto-conversion failed: {e}")

    # ── Auto-fetch DART financials for KR tickers if API key is set ──
    if args.ticker.endswith((".KS", ".KQ")) and os.environ.get("DISABLE_FIN_FETCH") != "1":
        live_fin = fetch_financials_for_deep_research(args.ticker)
        if live_fin and live_fin.get("pl_5y"):
            if not deep:
                deep = {}
            # Merge: DART data overrides placeholder, keep other deep_research sections
            existing_fin = deep.get("financials", {})
            existing_fin.update({
                "pl_5y": live_fin["pl_5y"],
                "bs_snapshot": live_fin.get("bs_snapshot", existing_fin.get("bs_snapshot", {})),
                "data_source": live_fin.get("source", "DART"),
            })
            deep["financials"] = existing_fin
            print(f"[combined] DART financials applied for {args.ticker}: "
                  f"{len(live_fin['pl_5y'])}y P&L")

    # Find current price for scenarios
    current_price = 0.0
    currency = "KRW" if args.ticker.endswith((".KS", ".KQ")) else "USD"
    for s in stocks:
        if s.get("ticker") == args.ticker:
            current_price = (s.get("market_data") or {}).get("current_price") or 0.0
            break

    # ── Compose body ─────────────────────────────────────────────────
    # SECTION ORDER (v0.6.0, 2026-05-27 — Sprint 1.5: Macro Anchor 추가):
    #   1. Cover
    #   2. Company Intro
    #   3. ★ Macro Anchor (FRED + IMF WEO) — Deep Research 도입부 ★ NEW (Sprint 1.5)
    #   4. Deep Research (산업 + 재무 + 카탈리스트/리스크)
    #   5. Financial Statements US-GAAP (5Y annual + 5Q quarterly + variance)
    #   6. News Timeline (중립 제외 + 월별 +/- bar chart)
    #   7. Executive Brief + Thesis List
    #   8. R1 Quant Anchor
    #   9. R2 Persona Panel (Thesis × Persona Matrix 정상화)
    #  10. R3 Decision Section
    #  11. (선택) ETF Holdings, Reverse DCF, Subagent Debate
    #  12. Appendix
    body = render_combined_cover(args.ticker, meta, persona_agg)

    # [2] Company Intro
    company_intro_html = render_company_intro_with_metrics(args.ticker, stocks)
    if company_intro_html:
        body += '<div style="page-break-before:always;"></div>' + company_intro_html

    # [3] Macro Anchor — Sprint 1.5 신설 (FRED + IMF WEO)
    # plugins/macro-economic-integration이 생성하는 macro_snapshot.json을
    # Deep Research 도입부 anchor로 자동 삽입. 환경변수 DISABLE_MACRO=1로 비활성화 가능.
    if os.environ.get("DISABLE_MACRO") != "1":
        try:
            from macro_renderer import ensure_macro_snapshot, render_macro_anchor_section
            from macro_sector_impact import get_sector_from_stocks
            from pathlib import Path as _Path
            pdir_for_macro = _Path(args.thesis).parent if args.thesis else None
            if pdir_for_macro:
                macro_snap = ensure_macro_snapshot(pdir_for_macro, stocks)
                if macro_snap:
                    # Sprint B-2: sector 기반 macro impact narrative 자동 추가
                    sector = get_sector_from_stocks(stocks, args.ticker)
                    company_kr = resolve_ticker(args.ticker).get("kr", "")
                    macro_html = render_macro_anchor_section(
                        macro_snap, sector=sector,
                        ticker=args.ticker, company_name=company_kr,
                    )
                    if macro_html:
                        body += '<div style="page-break-before:always;"></div>' + macro_html
                        print(f"[combined] macro anchor section added (sector={sector or 'N/A'})")
        except ImportError as e:
            print(f"[combined] macro_renderer not available: {e}")
        except Exception as e:
            print(f"[combined] macro section failed: {e}")

    # [4] Deep Research — 페이지 도입부로 승격 (사용자 요청 #4)
    # Sprint E-2: thesis_eval/all_aggregate.json raw inject → thesis_decomposition overlay
    if deep:
        thesis_eval_raw = None
        try:
            if eval_path.exists():
                with open(eval_path, encoding="utf-8") as _f:
                    thesis_eval_raw = json.load(_f)
        except Exception as _e:
            print(f"[combined] thesis_eval raw load failed: {_e}")
        body += '<div style="page-break-before:always;"></div>' + render_deep_research_section(
            deep, args.ticker, current_price, currency, thesis_eval=thesis_eval_raw
        )

    # [4b] Citation Audit — Phase 7 절차 B (evidence 기반 자동 팩트체크)
    # evidence/{ticker}.json 이 있으면 deep_research 주장을 대조해 ⚠️ 플래그.
    # 환경변수 DISABLE_FACTCHECK=1 로 비활성화 가능.
    if deep and args.deep_research and os.environ.get("DISABLE_FACTCHECK") != "1":
        try:
            from evidence_retriever import EvidenceRetriever as _ER  # noqa: F401
            from fact_checker import FactChecker, render_citation_audit_html, make_codex_verifier
            _pdir = Path(args.deep_research).resolve().parent.parent
            _ev_path = _pdir / "evidence" / f"{args.ticker}.json"
            if _ev_path.exists():
                _evidence = json.loads(_ev_path.read_text(encoding="utf-8"))
                _fc = FactChecker(args.ticker)
                _fc.register_verifier(make_codex_verifier())  # FACTCHECK_LLM=1 일 때만 동작
                _fc_res = _fc.run(deep, _evidence)
                _fc.write(_pdir / "factcheck")
                body += ('<div style="page-break-before:always;"></div>'
                         + render_citation_audit_html(_fc_res))
                print(f"[combined] citation audit: {_fc_res['verdict']} "
                      f"(🔴{_fc_res['summary']['conflict']} "
                      f"🟡{_fc_res['summary']['unsourced']} "
                      f"🟢{_fc_res['summary']['confirmed']})")
        except ImportError:
            pass
        except Exception as e:
            print(f"[combined] citation audit skipped: {e}")

    # [5] Quantitative Anchor — Sprint 2 신설 (DCF + Reverse DCF + Risk + Portfolio)
    # plugins/quant-anchor가 생성하는 quant_anchor_{TICKER}.json을 자동 삽입.
    # 환경변수 DISABLE_QUANT_ANCHOR=1로 비활성화 가능.
    if os.environ.get("DISABLE_QUANT_ANCHOR") != "1":
        try:
            from quant_anchor_renderer import (
                ensure_quant_anchor as ensure_qa,
                render_quant_anchor_section,
            )
            from pathlib import Path as _Path
            pdir_for_qa = _Path(args.thesis).parent if args.thesis else None
            if pdir_for_qa:
                qa = ensure_qa(pdir_for_qa, args.ticker, stocks)
                if qa:
                    qa_html = render_quant_anchor_section(qa)
                    if qa_html:
                        body += '<div style="page-break-before:always;"></div>' + qa_html
                        print(f"[combined] quant anchor section added")
        except ImportError as e:
            print(f"[combined] quant_anchor_renderer not available: {e}")
        except Exception as e:
            print(f"[combined] quant anchor section failed: {e}")

    # [4] Financial Statements US-GAAP — 5Y annual + 5Q quarterly + variance (사용자 요청 #1)
    try:
        from financial_statements_us_gaap import render_financial_statements_section
        fs_html = render_financial_statements_section(args.ticker)
        if fs_html:
            body += '<div style="page-break-before:always;"></div>' + fs_html
    except ImportError as e:
        print(f"[combined] financial_statements_us_gaap module not available: {e}")
    except Exception as e:
        print(f"[combined] financial_statements rendering failed: {e}")

    # [5] News Timeline — 개선된 버전 (중립 제외 + 월별 bar chart) (사용자 요청 #3)
    company_kr = resolve_ticker(args.ticker).get("kr", "")
    news_html = render_news_timeline(args.ticker, company_name=company_kr,
                                      filter_neutral=True, with_monthly_chart=True,
                                      expand_summary=True)
    if news_html:
        body += '<div style="page-break-before:always;"></div>' + news_html

    # [6] Executive Brief + Thesis List
    body += render_brief_and_thesis_combined(args.ticker, decisions, persona_agg, theses, stocks)

    # [7] R1 Quant
    # Fix-A (2026-05-28): thesis_eval mock data 감지 시 경고 배너 추가
    eval_meta = eval_data.get("__metadata__") or {}
    if eval_meta.get("is_mock_data"):
        mock_ratio_val = eval_meta.get("mock_ratio", 0) * 100
        mock_warning = '<div style="page-break-before:always;"></div>'
        mock_warning += (
            '<div style="background:#fef3c7;border-left:5pt solid #ea580c;padding:14pt 18pt;'
            'margin:14pt 0;border-radius:0 6pt 6pt 0;">'
            '<h3 style="margin-top:0;color:#9a3412;">[주의] Thesis × 4-Analyst 평가 데이터 부재</h3>'
            '<p style="font-size:11pt;margin:6pt 0;">현재 <strong>all_aggregate.json의 '
            + f"{mock_ratio_val:.0f}%" +
            '</strong>가 mock(placeholder) 데이터입니다. 4-Analyst (Macro·Industry·Empirical·'
            'Counter-thesis)가 실제 LLM 호출로 thesis를 평가하지 않은 상태입니다.</p>'
            '<p style="font-size:10.5pt;margin:6pt 0;color:#475569;">→ 실제 평가를 실행하려면 '
            '<code>plugins/multi-model-arena/skills/thesis-evaluator/scripts/evaluate_theses.py</code>를 '
            '실행하세요 (cost 추정: thesis 12개 × 4 analyst × tier_mid = ~$0.03 with gpt-4o-mini).</p>'
            '</div>'
        )
        body += mock_warning

    body += render_quant_section(stocks, theses, eval_data, risk_limits, args.ticker)

    # [8] R2 Persona Panel (Matrix 정상화 — 사용자 요청 #2)
    # Sprint C-3 (2026-05-28): personas_full에 company_data 주입 — guru_checklist 실데이터 검증용
    # market_data + bs_snapshot + cf_summary + pl_5y + quant_anchor를 한 곳에
    company_data_pkg = {}
    for s in stocks:
        if s.get("ticker") == args.ticker:
            company_data_pkg["market_data"] = s.get("market_data") or {}
            break
    if deep and deep.get("financials"):
        fin = deep["financials"]
        company_data_pkg["bs_snapshot"] = fin.get("bs_snapshot") or {}
        company_data_pkg["cf_summary"] = fin.get("cf_summary") or {}
        company_data_pkg["pl_5y"] = fin.get("pl_5y") or []
    # Quant Anchor JSON 로드 (있으면)
    try:
        from pathlib import Path as _Path
        pdir_for_qa = _Path(args.thesis).parent if args.thesis else None
        if pdir_for_qa:
            qa_file = pdir_for_qa / f"quant_anchor_{args.ticker.replace('.', '_')}.json"
            if qa_file.exists():
                company_data_pkg["quant_anchor"] = _read_json(str(qa_file))
    except Exception:
        pass
    persona_full["_company_data"] = company_data_pkg

    body += render_persona_section_for_ticker(persona_agg, persona_full, theses, args.ticker)

    # [8.5] Specialist Agents (Tier 2 — specialist-agents plugin)
    try:
        from pathlib import Path as _Path
        import json as _json
        pdir_for_specialist = _Path(args.thesis).parent if args.thesis else None
        if pdir_for_specialist:
            specialist_html = render_specialist_agents_section(args.ticker, pdir_for_specialist)
            if specialist_html:
                body += '<div style="page-break-before:always;"></div>' + specialist_html
    except Exception as e:
        print(f"[combined] specialist-agents section skipped: {e}")

    # [10] Optional: ETF holdings
    if args.ticker in ETF_HOLDINGS:
        body += '<div style="page-break-before:always;"></div>' + render_etf_holdings(args.ticker)

    # [10] Optional: Reverse DCF
    rdcf = auto_reverse_dcf(args.ticker)
    if rdcf:
        body += '<div style="page-break-before:always;"></div>' + rdcf

    # [10] Optional: Subagent debate
    debate = get_debate_for_ticker(args.ticker)
    if debate:
        body += '<div style="page-break-before:always;"></div>' + render_debate_section(args.ticker, debate)

    # [9] R3 Decision Section
    body += render_decision_section(decisions, portfolio, theses, eval_data,
                                     persona_aggregates_all, args.ticker)
    # [11] Appendix
    body += render_appendix_glossary()

    body = remove_emoji(body)  # Strip emoji glyphs that Noto Sans KR doesn't carry
    html = f"<!doctype html><html><head><meta charset='utf-8'><title>Combined Report</title></head><body>{body}</body></html>"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)

    # Use /tmp for intermediate files (avoid permission issues on user folders)
    import tempfile, subprocess as _sp, shutil as _sh
    with tempfile.NamedTemporaryFile(suffix=".weasy.pdf", delete=False) as tf:
        tmp_pdf = tf.name
    try:
        HTML(string=html).write_pdf(tmp_pdf, stylesheets=[CSS(string=CSS_BASE)])

        # ── PDF post-processing for cross-viewer compatibility ──
        # Strategy: pdftocairo handles CJK (Korean/Chinese/Japanese) reliably.
        # Cairo has proper CID font support and writes correct ToUnicode CMap,
        # so Korean text renders identically in Adobe Acrobat / Chrome / Preview.
        # ghostscript -dNoOutputFonts was tried but it has CID outline bugs
        # that cause partial Korean glyph loss.
        with tempfile.NamedTemporaryFile(suffix=".cairo.pdf", delete=False) as tf2:
            cairo_out = tf2.name
        cairo_cmd = ["pdftocairo", "-pdf", tmp_pdf, cairo_out]
        try:
            _sp.run(cairo_cmd, check=True, capture_output=True, timeout=60)
            if Path(cairo_out).exists() and Path(cairo_out).stat().st_size > 1000:
                _sh.copy(cairo_out, args.output)
            else:
                # pdftocairo failed silently — use raw WeasyPrint
                _sh.copy(tmp_pdf, args.output)
            Path(cairo_out).unlink(missing_ok=True)
        except Exception as e:
            print(f"[warn] pdftocairo post-process failed ({e}); using raw WeasyPrint output")
            _sh.copy(tmp_pdf, args.output)
    finally:
        Path(tmp_pdf).unlink(missing_ok=True)

    print(f"[combined] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")

    # ── Post-build hook: GitHub + Notion sync (v0.5.0+) ──────────────
    # Graceful skip if sync plugin not present or keys not set
    try:
        sync_script = (PLUGIN_ROOT.parent / "github-notion-sync" / "scripts" / "sync_analysis.py")
        if sync_script.exists() and os.environ.get("DISABLE_SYNC") != "1":
            # Pipeline dir is parent of stocks.json (or deduce from args.stocks)
            pipeline_dir = Path(args.stocks).resolve().parent
            print(f"[sync] post-build hook → GitHub + Notion (pipeline_dir={pipeline_dir.name})")
            import subprocess as _spp
            _spp.run(
                ["python3", str(sync_script),
                 "--pipeline-dir", str(pipeline_dir),
                 "--ticker", args.ticker],
                timeout=120,
                check=False,  # graceful — don't fail PDF build if sync fails
            )
    except Exception as e:
        print(f"[sync] post-build hook skipped (non-fatal): {e}")


if __name__ == "__main__":
    main()
