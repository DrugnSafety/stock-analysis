#!/usr/bin/env python3
"""R1: Quant Anchor Report — 정량지표 전체 보고서."""
import argparse
import json
import sys
from pathlib import Path
from weasyprint import HTML, CSS

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "_common"))
from css import CSS_BASE, fmt_money_krw, fmt_pct, VERDICT_COLOR, VERDICT_KOR
import chart_utils as cu
from metric_glossary import render_metric_glossary, render_data_tag_education
from ticker_resolver import resolve_ticker, format_ticker_with_name


def build_cover(meta: dict) -> str:
    return f"""
    <div class="cover">
      <p class="cover-meta">R1. Quant Anchor Report · {meta.get('date', '')}</p>
      <h1>{meta.get('title', '정량지표 전체 보고서')}</h1>
      <p class="cover-meta">대상: {meta.get('subjects', '')}</p>
      <p class="cover-meta">출처 블로그: {meta.get('blog_url', '')}</p>
      <div class="info">
        <strong>이 보고서의 역할</strong><br/>
        "데이터가 뭐라고 하는가?" — 페르소나 lens 적용 전, 순수 정량 anchor를
        체계적으로 정리. 모든 숫자는 [actual]/[inference]/[assumption] 태깅으로
        confidence 명시.
      </div>
    </div>
    """


def render_fundamentals(stocks: list[dict]) -> str:
    rows = ""
    labels, vols, ret_1m, ret_3m, pes = [], [], [], [], []
    for s in stocks:
        m = s.get("market_data", {})
        ticker = s.get("ticker", "")
        info = resolve_ticker(ticker) if ticker else {"kr": s.get("name", "?")}
        company_kr = info.get("kr") or s.get("name") or ticker
        sector = info.get("sector", "")
        rows += f"""
        <tr>
          <td><strong>{company_kr}</strong> <span style="font-size:8.5pt;color:#6b7280;">({sector})</span><br/><code>{ticker}</code></td>
          <td>{fmt_money_krw(m.get('current_price'))}</td>
          <td>{m.get('forward_pe', '-')}</td>
          <td>{m.get('beta', '-')}</td>
          <td>{fmt_pct(m.get('return_1m_pct'))}</td>
          <td>{fmt_pct(m.get('return_3m_pct'))}</td>
          <td>{fmt_pct(m.get('volatility_annualized_pct'))}</td>
        </tr>
        """
        labels.append((company_kr or ticker)[:8])
        vols.append(m.get('volatility_annualized_pct') or 0)
        ret_1m.append(m.get('return_1m_pct') or 0)
        ret_3m.append(m.get('return_3m_pct') or 0)
        pes.append(m.get('forward_pe') or 0)

    # Determine fetch date from first stock's market_data
    fetch_dates = [s.get("market_data", {}).get("as_of_date") for s in stocks if s.get("market_data", {}).get("as_of_date")]
    fetch_via_set = {s.get("market_data", {}).get("fetched_via", "") for s in stocks}
    fetch_via = ", ".join(filter(None, fetch_via_set))
    date_label = f"조회일 {sorted(fetch_dates)[-1]}" if fetch_dates else "조회일 미상"

    body = f"""
    <h2>1. Fundamentals <span style="font-size:11pt;color:#6b7280;font-weight:normal;">({date_label})</span></h2>
    <p style="font-size:9pt;color:#6b7280;margin-bottom:6pt;">
      <strong>데이터 출처</strong>: {fetch_via or 'yfinance live'} ·
      <strong>분석 시점 가격</strong>: 본 표의 모든 가격·수익률·시가총액은 위 조회일의 시장 종가 기준
    </p>
    <table class="dt">
      <thead><tr><th>종목</th><th>현재가</th><th>Fwd PE</th><th>베타</th><th>1M</th><th>3M</th><th>변동성(연)</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """

    if labels:
        # 1M·3M 수익률 비교
        body += '<h3>1-1. 단기 수익률 (1M vs 3M)</h3>'
        body += cu.bar_chart(labels, ret_3m, title="3개월 수익률 (%)",
                              ylabel="%", colors=[cu.COLORS["bull"] if r > 0 else cu.COLORS["bear"] for r in ret_3m],
                              h_line=0)
        body += '<h3>1-2. 변동성 비교</h3>'
        body += cu.bar_chart(labels, vols, title="연환산 변동성 (%)", ylabel="%",
                              colors=[cu.COLORS["bear"] if v > 50 else cu.COLORS["warn"] if v > 30 else cu.COLORS["bull"] for v in vols])
        body += '<h3>1-3. Forward PE 비교</h3>'
        body += cu.bar_chart(labels, pes, title="Forward PE", ylabel="PER",
                              colors=[cu.COLORS["bull"] if p < 12 else cu.COLORS["warn"] if p < 20 else cu.COLORS["bear"] for p in pes])

    return body


def render_4analyst(theses: list[dict], evals: dict) -> str:
    """thesis별 4-Analyst 평가 (Macro/Industry/Empirical/Counter)"""
    body = '<h2>2. 4-Analyst 평가 (thesis별)</h2>'

    # thesis × analyst stance heatmap
    matrix = []
    row_labels = []
    col_labels = ["Macro", "Industry", "Empirical", "Counter"]
    stance_to_num = {"support": 1.0, "neutral": 0.0, "rebut": -1.0}
    for t in theses[:8]:
        cid = t.get("claim_id")
        agg = evals.get(cid, {})
        eval_data = agg.get("evaluations", {})
        row = []
        for analyst in ["macro", "industry", "empirical", "counter"]:
            stance = (eval_data.get(analyst) or {}).get("stance", "neutral")
            conf = (eval_data.get(analyst) or {}).get("confidence", 0)
            row.append(stance_to_num.get(stance, 0) * conf)  # signed score
        matrix.append(row)
        row_labels.append(cid)

    if matrix:
        body += '<h3>2-1. Thesis × Analyst Stance Heatmap</h3>'
        body += cu.heatmap(matrix, row_labels, col_labels,
                            title="Stance × Confidence (녹: support · 빨: rebut)",
                            cmap="RdYlGn", vmin=-1, vmax=1, annotate=True)

    body += '<h3>2-2. Thesis별 4-Analyst 평가 상세</h3>'
    for t in theses[:8]:  # core 8개만
        cid = t.get("claim_id")
        agg = evals.get(cid, {})
        agg_data = agg.get("aggregate", {})
        body += f"""
        <h3>{cid} — {t.get('claim', '')}</h3>
        <p><span class="tag-{ 'actual' if t.get('type')=='factual' else 'inference'}">{t.get('type')}</span> · {t.get('importance')} · {t.get('timeframe')}</p>
        """
        eval_data = agg.get("evaluations", {})
        rows = ""
        for analyst in ["macro", "industry", "empirical", "counter"]:
            e = eval_data.get(analyst, {})
            stance = e.get("stance", "-")
            color = "#16a34a" if stance == "support" else "#dc2626" if stance == "rebut" else "#ca8a04"
            rows += f"""
            <tr>
              <td><strong>{analyst.title()}</strong></td>
              <td><span style="color:{color};font-weight:600;">{stance}</span></td>
              <td>{int((e.get('confidence') or 0)*100)}%</td>
              <td style="font-size:9.5pt;line-height:1.6;">{e.get('rationale') or '-'}</td>
            </tr>
            """
        if rows:
            body += f'<table class="dt"><thead><tr><th style="width:11%">Analyst</th><th style="width:8%">Stance</th><th style="width:6%">Conf</th><th>Rationale (자세히)</th></tr></thead><tbody>{rows}</tbody></table>'
        if agg_data.get("weighted_stance"):
            ws = agg_data["weighted_stance"]
            wc = agg_data.get("weighted_confidence", 0)
            body += f'<p><strong>Aggregate:</strong> <span class="bull" style="color:{VERDICT_COLOR.get(ws, "#666")};">{ws} ({int(wc*100)}%)</span> · {agg_data.get("agreement_level", "")}</p>'
    return body


def render_risk(risk_limits: dict) -> str:
    rows = ""
    for r in risk_limits.get("limits", []):
        if "error" in r:
            continue
        v = r["volatility_metrics"].get("annualized_volatility")
        info = resolve_ticker(r['ticker'])
        company_kr = info.get("kr", r['ticker'])
        rows += f"""
        <tr>
          <td><strong>{company_kr}</strong><br/><code style="font-size:8.5pt;">{r['ticker']}</code></td>
          <td>{r['as_of_date']}</td>
          <td>{fmt_pct((v or 0)*100, sign=False) if v else '-'}</td>
          <td>{r['vol_multiplier']:.2f}</td>
          <td>{r['combined_limit_pct']*100:.1f}%</td>
          <td>{fmt_money_krw(r['position_limit_value'])}</td>
          <td>{r['max_quantity']:,}주</td>
        </tr>
        """
    return f"""
    <h2>3. Risk Metrics — 변동성-조정 포지션 한도</h2>
    <table class="dt">
      <thead><tr><th>Ticker</th><th>As of</th><th>변동성(연)</th><th>vol_mult</th><th>한도 %</th><th>한도 ₩</th><th>최대수량</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;">변동성 multiplier: 저변동성 1.25× / 30% 0.75× / 50%+ 0.50×.
    상관관계 multiplier 별도 적용 가능.</p>
    """


def render_data_tags_summary(theses: list[dict], evals: dict) -> str:
    """[actual] / [inference] / [assumption] 비율 — 분석의 사실 anchor 강도"""
    counts = {"actual": 0, "inference": 0, "assumption": 0, "derived": 0, "unavailable": 0}
    for t in theses:
        evid = t.get("supporting_evidence", "")
        # 본문 인용은 actual로 가정
        if evid:
            counts["actual"] += 1

    for cid, agg in evals.items():
        for a, e in (agg.get("evaluations") or {}).items():
            for d in (e.get("supporting_data") or []):
                tag = (d.get("source", "") or "").lower()
                if "report" in tag or "통계" in tag or "공식" in tag or "발표" in tag:
                    counts["actual"] += 1
                elif "추론" in tag or "inference" in tag:
                    counts["inference"] += 1
                else:
                    counts["assumption"] += 1

    total = sum(counts.values()) or 1
    body = '<h2>4. 데이터 태깅 요약 (분석의 사실 anchor 강도)</h2>'
    body += '<table class="dt"><thead><tr><th>Tag</th><th>건수</th><th>비율</th></tr></thead><tbody>'
    for tag, n in counts.items():
        pct = n / total * 100
        body += f'<tr><td><span class="tag-{tag}">[{tag}]</span></td><td>{n}</td><td>{pct:.1f}%</td></tr>'
    body += '</tbody></table>'

    # Pie chart
    nonzero_labels = [k for k, v in counts.items() if v > 0]
    nonzero_values = [counts[k] for k in nonzero_labels]
    if nonzero_values:
        tag_colors = {"actual": "#16a34a", "inference": "#f59e0b",
                      "assumption": "#dc2626", "derived": "#8b5cf6", "unavailable": "#6b7280"}
        colors = [tag_colors.get(t, "#6b7280") for t in nonzero_labels]
        body += cu.pie_chart([f"[{t}] {counts[t]}" for t in nonzero_labels],
                              nonzero_values,
                              title="데이터 태깅 분포",
                              colors=colors)
    body += f'<p style="font-size:9pt;color:#6b7280;">전체 {total}개 평가 항목 중 [actual] 비율이 높을수록 분석이 사실 기반.</p>'
    return body


def main():
    parser = argparse.ArgumentParser(description="R1 Quant Anchor Report")
    parser.add_argument("--meta", help="JSON: title/date/blog_url/subjects")
    parser.add_argument("--stocks", required=True, help="ticker별 market_data 리스트 JSON")
    parser.add_argument("--thesis", help="thesis_list.json")
    parser.add_argument("--eval-dir", help="thesis_eval 디렉토리")
    parser.add_argument("--risk-limits", help="risk_limits.json")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    meta = json.load(open(args.meta)) if args.meta else {"title": "Quant Anchor Report"}
    stocks = json.load(open(args.stocks))

    theses = []
    evals = {}
    if args.thesis:
        with open(args.thesis, encoding="utf-8") as f:
            theses = json.load(f).get("theses", [])
    if args.eval_dir:
        eval_path = Path(args.eval_dir) / "all_aggregate.json"
        if eval_path.exists():
            agg_data = json.load(open(eval_path, encoding="utf-8"))
            for a in agg_data.get("aggregates", []):
                evals[a["claim_id"]] = a

    risk_limits = json.load(open(args.risk_limits)) if args.risk_limits else {"limits": []}

    body = build_cover(meta)
    # 학습용 metric 용어 풀이 추가
    body += render_metric_glossary()
    body += render_fundamentals(stocks)
    if theses and evals:
        body += render_4analyst(theses, evals)
        body += render_data_tags_summary(theses, evals)
        # 데이터 태깅 시스템 교육
        body += render_data_tag_education()
    if risk_limits.get("limits"):
        body += render_risk(risk_limits)

    html = f"<!doctype html><html><head><meta charset='utf-8'><title>R1 Quant Anchor</title></head><body>{body}</body></html>"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_BASE)])

    import os
    print(f"[R1] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
