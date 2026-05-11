#!/usr/bin/env python3
"""R3: Executive Summary — 의사결정 시트 (5-8p)."""
import argparse
import json
import sys
from pathlib import Path
from weasyprint import HTML, CSS

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "_common"))
from css import CSS_BASE, fmt_money_krw, fmt_pct, VERDICT_COLOR, VERDICT_KOR
import chart_utils as cu
from metric_glossary import VERDICT_INTERPRETATION, CONFIDENCE_INTERPRETATION
from ticker_resolver import resolve_ticker


def build_decision_sheet(decisions: list[dict], portfolio: dict) -> str:
    """1페이지 결정 시트 (Cover)"""
    rows = ""
    for d in decisions[:5]:
        action = d.get("action", "hold")
        action_color = {"buy": "#16a34a", "sell_all": "#dc2626", "sell_partial": "#dc2626"}.get(action, "#ca8a04")
        ticker = d.get("ticker", "")
        info = resolve_ticker(ticker) if ticker else {"kr": "-"}
        company_kr = info.get("kr", ticker)
        rows += f"""
        <tr>
          <td><strong>{company_kr}</strong><br/><code style="font-size:8.5pt;">{ticker}</code></td>
          <td><span style="color:{action_color};font-weight:700;">{action.upper()}</span></td>
          <td>{d.get('target_quantity', 0):,}주</td>
          <td>{fmt_money_krw(d.get('target_value'))}</td>
          <td>{d.get('signal_score', 0):+.2f}</td>
        </tr>
        """

    final_nav = portfolio.get("final_nav", 0)
    total_return = portfolio.get("total_return_pct", 0)
    color = "#16a34a" if total_return > 0 else "#dc2626"

    # Position size horizontal bars
    items = []
    for d in decisions[:5]:
        if "error" in d:
            continue
        action = d.get("action", "hold")
        c = {"buy": cu.COLORS["bull"], "sell_all": cu.COLORS["bear"],
             "sell_partial": cu.COLORS["bear"]}.get(action, cu.COLORS["neutral"])
        ticker = d.get("ticker", "")
        company_kr = resolve_ticker(ticker).get("kr", ticker) if ticker else ticker
        items.append({
            "label": f"{company_kr} ({action})",
            "value": d.get("target_value", 0),
            "max": d.get("position_limit_value", d.get("target_value", 1)) or 1,
            "color": c,
            "format": "₩{:,.0f}".replace("{:", "{:") if d.get("target_value", 0) < 100_000_000 else "₩{:.1f}"
        })
    pos_chart = cu.kpi_horizontal_bars(items, title="Trade Decision — 종목별 포지션 사이즈") if items else ""

    return f"""
    <div class="cover">
      <p class="cover-meta">R3. Executive Summary — Decision Sheet</p>
      <h1>한 페이지 결정 시트</h1>
      <table class="dt" style="margin-top:1.5cm;">
        <thead><tr><th>종목</th><th>액션</th><th>수량</th><th>금액</th><th>신호</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>

      {pos_chart}

      <div class="kpi-grid" style="margin-top:1cm;">
        <div class="kpi"><div class="num">{len(decisions)}</div><div class="label">Decisions</div></div>
        <div class="kpi"><div class="num">{fmt_money_krw(portfolio.get('start_cash', 0))}</div><div class="label">Start Capital</div></div>
        <div class="kpi"><div class="num" style="color:{color};">{fmt_pct(total_return)}</div><div class="label">Total Return</div></div>
        <div class="kpi"><div class="num">{portfolio.get('total_trades', 0)}</div><div class="label">Trades</div></div>
      </div>

      <div class="warn" style="margin-top:1cm;">
        ⚠️ 본 보고서는 paper portfolio simulation입니다. 실제 거래는 사용자가 별도 증권사 시스템에서 수행하며,
        본 시스템은 어떤 자동 거래도 수행하지 않습니다.
      </div>
    </div>
    """


def render_thesis_summary(thesis: dict) -> str:
    summary = thesis.get("summary_one_liner", "")
    theses = thesis.get("theses", [])[:6]
    rows = ""
    for t in theses:
        if t.get("importance") != "core":
            continue
        rows += f"""
        <tr>
          <td><strong>{t.get('claim_id')}</strong></td>
          <td>{t.get('claim', '')}</td>
          <td><span class="tag-{ 'actual' if t.get('type')=='factual' else 'inference'}">{t.get('type')}</span></td>
        </tr>
        """
    return f"""
    <h2>1. 메르의 핵심 주장 (요약)</h2>
    <div class="info">{summary}</div>
    <table class="dt">
      <thead><tr><th>ID</th><th>Claim</th><th>Type</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_quant_validation(eval_data: dict) -> str:
    """정량 검증 — 사실 vs 가정 분리"""
    body = '<h2>2. 정량 검증 결과 — 사실 vs 가정</h2>'
    rows = ""
    for cid, agg in eval_data.items():
        agg_data = agg.get("aggregate", {})
        stance = agg_data.get("weighted_stance", "?")
        conf = agg_data.get("weighted_confidence", 0)
        agreement = agg_data.get("agreement_level", "")
        color = VERDICT_COLOR.get(stance, "#666")
        rows += f"""
        <tr>
          <td><strong>{cid}</strong></td>
          <td><span style="color:{color};font-weight:600;">{stance}</span></td>
          <td>{int(conf*100)}%</td>
          <td style="font-size:9pt;">{agreement}</td>
        </tr>
        """
    return body + f'<table class="dt"><thead><tr><th>Thesis</th><th>4-Analyst 합의</th><th>Conf</th><th>Agreement</th></tr></thead><tbody>{rows}</tbody></table>'


def render_persona_consensus(panel_aggregates: dict) -> str:
    """종목별 13명 페르소나 합의도"""
    body = '<h2>3. Persona Panel 합의도 (종목별)</h2>'
    if not panel_aggregates:
        return body + '<p>panel data 없음.</p>'

    # Stacked bar chart 종목별 verdict
    # Replace tickers with company names in chart labels
    cats = [resolve_ticker(t).get("kr", t)[:10] for t in panel_aggregates.keys()]
    bull_c, neu_c, bear_c = [], [], []
    for t, agg in panel_aggregates.items():
        d = agg.get("verdict_distribution", {})
        bull_c.append(d.get("lean_bullish", {}).get("count", 0))
        neu_c.append(d.get("neutral", {}).get("count", 0))
        bear_c.append(d.get("lean_bearish", {}).get("count", 0))

    body += cu.stacked_bar(cats, {"매수 성향": bull_c, "중립": neu_c, "매도 성향": bear_c},
                            title="종목별 13명 페르소나 verdict 분포",
                            colors={"매수 성향": cu.COLORS["bull"], "중립": cu.COLORS["neutral"], "매도 성향": cu.COLORS["bear"]})

    for ticker, agg in panel_aggregates.items():
        dist = agg.get("verdict_distribution", {})
        bull = dist.get("lean_bullish", {}).get("count", 0)
        neu = dist.get("neutral", {}).get("count", 0)
        bear = dist.get("lean_bearish", {}).get("count", 0)
        avg_conf = agg.get("average_confidence", 0)
        company_kr = resolve_ticker(ticker).get("kr", ticker)
        body += f"""
        <h4>{company_kr} <code style="font-size:9pt;color:#6b7280;">{ticker}</code></h4>
        <p>매수 <span class="bull">{bull}</span> / 중립 <span class="neutral">{neu}</span> / 매도 <span class="bear">{bear}</span> · 평균 신뢰도 {int(avg_conf*100)}%</p>
        """
    return body


def render_key_risks(theses: list[dict], decisions: list[dict]) -> str:
    """핵심 위험 5개 — 가장 먼저 무너질 가정"""
    body = '<h2>4. 핵심 위험 5개 — 가장 먼저 무너질 가정</h2>'
    risks = []
    for t in theses:
        if t.get("importance") == "core" and t.get("type") in ("predictive", "conditional"):
            risks.append({
                "source": "thesis",
                "claim_id": t.get("claim_id"),
                "claim": t.get("claim"),
            })
    for d in decisions[:3]:
        if d.get("primary_risks"):
            for r in d.get("primary_risks", [])[:2]:
                risks.append({
                    "source": f"decision_{d.get('ticker')}",
                    "risk": r,
                })
    body += '<ol style="font-size:10pt;">'
    for r in risks[:5]:
        if "claim" in r:
            body += f'<li><span class="warn" style="display:inline-block;padding:1pt 6pt;">{r["claim_id"]}</span> {r["claim"]}</li>'
        else:
            body += f'<li>{r["risk"]}</li>'
    body += '</ol>'
    return body


def render_monitor_points(theses: list[dict]) -> str:
    body = '<h2>5. 모니터링 포인트 (verdict 뒤집을 신호)</h2><ul>'
    for t in theses[:5]:
        if t.get("importance") == "core":
            body += f'<li><strong>{t.get("claim_id")}</strong>: {t.get("claim", "")} <em style="color:#6b7280;">({t.get("timeframe", "")})</em></li>'
    body += '</ul>'
    return body


def main():
    parser = argparse.ArgumentParser(description="R3 Executive Summary")
    parser.add_argument("--thesis", required=True)
    parser.add_argument("--eval-dir", required=True)
    parser.add_argument("--persona-aggregates", help="dict: ticker → aggregate.json")
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--portfolio", required=True)
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    thesis_data = json.load(open(args.thesis))
    eval_data = {}
    eval_path = Path(args.eval_dir) / "all_aggregate.json"
    if eval_path.exists():
        for a in json.load(open(eval_path)).get("aggregates", []):
            eval_data[a["claim_id"]] = a

    decisions = json.load(open(args.decisions)).get("decisions", [])
    portfolio = json.load(open(args.portfolio))

    panel_aggregates = {}
    if args.persona_aggregates:
        panel_aggregates = json.load(open(args.persona_aggregates))

    body = build_decision_sheet(decisions, portfolio)
    # 학습용 verdict·confidence 해석 가이드 추가
    body += """
    <h2>📚 Verdict·Confidence 해석 가이드 (이 보고서를 처음 보시는 분께)</h2>
    <div class="info">이 보고서의 모든 'Verdict'·'Signal Score'는 다음 기준으로 해석됩니다.</div>
    <h3>Verdict 의미</h3>
    <table class="dt">
      <thead><tr><th>Verdict</th><th>의미</th></tr></thead>
      <tbody>"""
    for v, desc in VERDICT_INTERPRETATION.items():
        body += f"<tr><td><strong>{v}</strong></td><td>{desc}</td></tr>"
    body += """</tbody></table>
    <h3>Confidence 의미</h3>
    <table class="dt">
      <thead><tr><th>Confidence</th><th>의미</th></tr></thead>
      <tbody>"""
    for c, desc in CONFIDENCE_INTERPRETATION.items():
        body += f"<tr><td><strong>{c.replace('_', ' ').title()}</strong></td><td>{desc}</td></tr>"
    body += """</tbody></table>
    <h3>Signal Score (Portfolio Manager의 통합 지표)</h3>
    <p style="font-size:10pt;">각 종목별 13명 페르소나·thesis-first verdict를 페르소나 가중치(Druckenmiller 1.5×, Lynch 1.3×, Buffett 0.7× 등 한국 시장 calibration 적용)로 weighted average한 신호. <strong>+0.7 이상</strong>이면 한도까지 매수, <strong>+0.3-0.7</strong>이면 한도의 50%, <strong>±0.3 이내</strong>면 hold, <strong>-0.3 이하</strong>면 sell.</p>
    """

    body += render_thesis_summary(thesis_data)
    body += render_quant_validation(eval_data)
    body += render_persona_consensus(panel_aggregates)
    body += render_key_risks(thesis_data.get("theses", []), decisions)
    body += render_monitor_points(thesis_data.get("theses", []))

    # 의사결정 가이드 (마무리)
    body += """
    <h2>📚 이 보고서로 어떻게 의사결정을 해야 하는가?</h2>
    <div class="info">처음 보시는 분께 — 이 보고서를 어떻게 활용하면 좋은지 가이드입니다.</div>
    <ol style="font-size:10pt;line-height:1.8;">
      <li><strong>가장 먼저 — Cover의 Decision Sheet</strong>: 시간이 없으면 첫 페이지만 봐도 OK. 종목·액션·수량이 한눈에.</li>
      <li><strong>그 다음 — '메르의 핵심 주장'</strong>: 블로거가 무엇을 주장했는지 6개 thesis로 압축. 동의하지 않는 thesis가 있으면 verdict 신뢰 낮춤.</li>
      <li><strong>'정량 검증 결과'</strong>: 4-Analyst가 각 thesis를 사실/추론/가정으로 분류. <strong>'support 80%+'</strong> thesis는 신뢰 높음, <strong>'split (2/4)'</strong>는 약한 link.</li>
      <li><strong>'Persona Panel 합의도'</strong>: 13명이 같은 사실에 대해 다른 결론을 낼 수 있다는 점이 핵심. <strong>'9/13 lean_bullish'</strong>처럼 강한 합의는 신호, <strong>'split'</strong>은 본인 판단 필요.</li>
      <li><strong>'핵심 위험 5개'</strong>: 가장 먼저 무너질 가정. 만약 이 가정 중 하나라도 깨지는 신호 보이면 immediate review.</li>
      <li><strong>'모니터링 포인트'</strong>: 향후 verdict 뒤집을 신호. 정기적으로 확인.</li>
    </ol>
    <p style="font-size:9.5pt;margin-top:8pt;background:#fef3c7;padding:8pt 12pt;border-left:3pt solid #f59e0b;">
      <strong>💡 학습 권고</strong>: 같은 종목에 R1(정량) + R2(13명 페르소나 reasoning) 둘 다 읽고 비교하세요. R1의 정량 데이터가 R2의 13명 페르소나 verdict를 어떻게 다른 lens로 해석하는지 학습하면 본인의 투자 framework가 풍부해집니다.
    </p>
    """

    html = f"<!doctype html><html><head><meta charset='utf-8'><title>R3 Executive Summary</title></head><body>{body}</body></html>"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_BASE)])

    import os
    print(f"[R3] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
