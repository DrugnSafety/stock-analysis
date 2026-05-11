#!/usr/bin/env python3
"""Consensus JSON → HTML/PDF 시각화."""
import argparse
import json
from pathlib import Path


def render_extract(c: dict) -> str:
    summary = c["extraction_consensus"]["summary"]
    blog = c.get("blog_url", "")

    def render_company_table(items, title, color):
        if not items:
            return f"<h3>{title} <em>(없음)</em></h3>"
        rows = "".join(f"""
        <tr>
          <td><strong>{i.get('name_kr') or i.get('name_en') or '-'}</strong></td>
          <td><code>{i.get('ticker') or '-'}</code></td>
          <td>{i.get('exchange', '-')}</td>
          <td>{', '.join(i.get('found_by', []))}</td>
          <td>{int(i.get('consensus_score', 0) * 100)}%</td>
        </tr>""" for i in items)
        return f"""
        <h3 style="color:{color};">{title} ({len(items)}개)</h3>
        <table class="data-table">
          <thead><tr><th>회사</th><th>Ticker</th><th>거래소</th><th>발견 모델</th><th>합의 점수</th></tr></thead>
          <tbody>{rows}</tbody>
        </table>
        """

    body = f"""
    <h1>Multi-Model Arena — 종목 추출 Consensus</h1>
    <p>출처: <a href="{blog}">{blog}</a></p>
    <p>실행 모델: {', '.join(c.get('models_run', []))}</p>

    <div class="summary-grid">
      <div><strong>총 unique</strong><br/>{summary['total_unique']}</div>
      <div><strong>3/3 합의</strong><br/>{summary['consensus_count']}</div>
      <div><strong>2/3 다수</strong><br/>{summary['majority_count']}</div>
      <div><strong>1/3 단독</strong><br/>{summary['single_count']}</div>
    </div>

    {render_company_table(c['extraction_consensus']['consensus_3of3'], '3/3 합의 종목 (가장 신뢰)', '#16a34a')}
    {render_company_table(c['extraction_consensus']['majority_2of3'], '2/3 다수 종목', '#2563eb')}
    {render_company_table(c['extraction_consensus']['single_model'], '1/3 단독 발견 종목 (검토 필요)', '#dc2626')}

    <h3>비용</h3>
    <ul>{"".join(f'<li>{k}: ${v}</li>' for k, v in c['cost_summary'].items() if k != 'total_usd')}
    <li><strong>합계: ${c['cost_summary']['total_usd']:.4f}</strong></li></ul>
    """
    return body


def render_analyze(c: dict) -> str:
    if "error" in c:
        return f"<h1>Error</h1><p>{c['error']}</p>"

    verdict_color = {"BUY": "#16a34a", "HOLD": "#ca8a04", "SELL": "#dc2626"}

    verdicts_html = "".join(f"""
    <div class="model-card">
      <h4>{m}</h4>
      <p style="color:{verdict_color.get(v['verdict'], '#666')};font-weight:700;font-size:18pt;">
        {v['verdict']}
      </p>
      <p>신뢰도: {int(v.get('confidence', 0) * 100)}%</p>
      <p style="font-size:9pt;color:#666;">model: {v.get('model_used', m)}</p>
    </div>
    """ for m, v in c["verdicts"].items())

    perspectives_html = ""
    for role, scores in c["perspectives_diff"].items():
        spread = scores.get("spread", 0)
        spread_color = "#dc2626" if spread >= 2 else ("#ca8a04" if spread == 1 else "#16a34a")
        score_cells = "".join(f"<td>{scores.get(m, '-')}/5</td>" for m in c["models_run"])
        perspectives_html += f"""
        <tr>
          <td><strong>{role.title()}</strong></td>
          {score_cells}
          <td style="color:{spread_color};">{spread}</td>
        </tr>
        """

    bull_html = "<ul>" + "".join(
        f"<li><strong>{m}</strong>: {t[:300]}{'...' if len(t)>300 else ''}</li>"
        for m, t in c.get("bull_theses_by_model", [])
    ) + "</ul>"

    bear_html = "<ul>" + "".join(
        f"<li><strong>{m}</strong>: {t[:300]}{'...' if len(t)>300 else ''}</li>"
        for m, t in c.get("bear_theses_by_model", [])
    ) + "</ul>"

    body = f"""
    <h1>Arena Consensus — {c['ticker']}</h1>
    <p>실행 모델: {', '.join(c.get('models_run', []))}</p>

    <h2>Weighted Verdict: <span style="color:{verdict_color.get(c['weighted_verdict'])};">
        {c['weighted_verdict']}</span> (신뢰도 {int(c['weighted_confidence']*100)}%)
    </h2>
    <p><strong>Agreement:</strong> {c['agreement_level']}</p>

    <div class="model-grid">{verdicts_html}</div>

    <h3>4-Analyst Perspectives 비교 (1-5 점수)</h3>
    <table class="data-table">
      <thead><tr><th>역할</th>{"".join(f"<th>{m}</th>" for m in c['models_run'])}<th>스프레드</th></tr></thead>
      <tbody>{perspectives_html}</tbody>
    </table>

    <h3>🐂 Bull Thesis (모델별)</h3>
    {bull_html}

    <h3>🐻 Bear Thesis (모델별)</h3>
    {bear_html}

    <h3>비용</h3>
    <ul>{"".join(f'<li>{k}: ${v}</li>' for k, v in c['cost_summary'].items() if k != 'total_usd')}
    <li><strong>합계: ${c['cost_summary']['total_usd']:.4f}</strong></li></ul>
    """
    return body


CSS = """
@page { size: A4; margin: 18mm; }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.6; font-size: 10.5pt; }
h1 { color: #111; border-bottom: 2pt solid #2563eb; padding-bottom: 6pt; }
h2 { color: #111827; margin-top: 24pt; }
h3 { color: #1f2937; margin-top: 18pt; }
table.data-table { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9.5pt; }
table.data-table th, table.data-table td { border: 1pt solid #e5e7eb; padding: 6pt 8pt; text-align: left; }
table.data-table th { background: #f3f4f6; }
.summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8pt; margin: 12pt 0; }
.summary-grid > div { background: #f9fafb; padding: 10pt; text-align: center; border-left: 3pt solid #2563eb; }
.model-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12pt; margin: 12pt 0; }
.model-card { background: #f9fafb; padding: 12pt; border-radius: 4pt; text-align: center; }
.model-card h4 { margin: 0 0 6pt 0; }
code { background: #f3f4f6; padding: 1pt 4pt; border-radius: 3pt; font-family: monospace; }
"""


def main():
    parser = argparse.ArgumentParser(description="Visualize consensus JSON")
    parser.add_argument("consensus_json")
    parser.add_argument("--output", "-o", required=True)
    parser.add_argument("--format", choices=["html", "pdf"], default="html")
    args = parser.parse_args()

    with open(args.consensus_json, encoding="utf-8") as f:
        c = json.load(f)

    if c.get("type") == "extract":
        body = render_extract(c)
    elif c.get("type") == "analyze":
        body = render_analyze(c)
    else:
        body = "<h1>Unknown consensus type</h1>"

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Arena Consensus</title>
<style>{CSS}</style></head><body>{body}</body></html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    if args.format == "html":
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(html)
    else:
        from weasyprint import HTML
        HTML(string=html).write_pdf(args.output)

    print(f"[consensus-visualize] saved: {args.output}")


if __name__ == "__main__":
    main()
