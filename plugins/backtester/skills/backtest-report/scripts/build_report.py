#!/usr/bin/env python3
"""Backtest 종합 PDF — 적중률·alpha·calibration 시각화."""
import argparse
import json
from pathlib import Path
from weasyprint import HTML, CSS


CSS_TEXT = """
@page { size: A4; margin: 18mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; } }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.5; font-size: 10pt; }
h1 { color: #111; font-size: 22pt; border-bottom: 2pt solid #2563eb; padding-bottom: 8pt; }
h2 { color: #111827; margin-top: 22pt; border-left: 4pt solid #2563eb; padding-left: 8pt; }
h3 { margin-top: 16pt; font-size: 12pt; }
.cover { page-break-after: always; padding-top: 3cm; text-align: center; }
.cover h1 { border: none; font-size: 28pt; }
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10pt; margin: 12pt 0; }
.kpi { background: #f9fafb; padding: 12pt; border-left: 3pt solid #2563eb; text-align: center; }
.kpi .num { font-size: 22pt; font-weight: 700; color: #111; }
.kpi .label { font-size: 9pt; color: #6b7280; margin-top: 4pt; }
table.dt { width: 100%; border-collapse: collapse; font-size: 9.5pt; margin: 8pt 0; }
table.dt th, table.dt td { border: 1pt solid #e5e7eb; padding: 5pt 7pt; text-align: left; }
table.dt th { background: #f3f4f6; }
.bar-row { display: flex; align-items: center; margin: 4pt 0; font-size: 9pt; }
.bar-label { width: 30%; }
.bar-track { flex: 1; height: 14pt; background: #e5e7eb; border-radius: 3pt; overflow: hidden; position: relative; }
.bar-fill { height: 100%; background: #16a34a; }
.bar-fill.med { background: #ca8a04; } .bar-fill.low { background: #dc2626; }
.bar-value { width: 80px; text-align: right; font-weight: 600; }
.calib-bar { width: 50%; height: 18pt; background: #e5e7eb; position: relative; display: inline-block; }
.calib-bar > div { position: absolute; height: 100%; }
.calib-pred { background: #93c5fd; opacity: 0.6; }
.calib-actual { background: #16a34a; opacity: 0.8; }
.note { background: #fef3c7; padding: 8pt 10pt; border-left: 3pt solid #f59e0b; margin: 8pt 0; font-size: 9pt; }
"""


def render_overall(hd: dict) -> str:
    ov = hd.get("overall", {})
    rows = ""
    for vt in ["BUY", "HOLD", "SELL"]:
        if f"{vt}_total" not in ov:
            continue
        total = ov[f"{vt}_total"]
        if total == 0:
            continue
        hits = ov[f"{vt}_hit"]
        rate = ov[f"{vt}_rate"]
        avg_ret = ov.get(f"{vt}_avg_return_pct", 0)
        bar_class = "" if rate >= 0.6 else "med" if rate >= 0.4 else "low"
        rows += f"""
        <div class="bar-row">
          <div class="bar-label"><strong>{vt}</strong></div>
          <div class="bar-track"><div class="bar-fill {bar_class}" style="width:{rate*100:.0f}%"></div></div>
          <div class="bar-value">{hits}/{total} ({int(rate*100)}%) · 평균 {avg_ret:+.1f}%</div>
        </div>
        """
    return rows


def render_by_persona(hd: dict) -> str:
    bp = hd.get("by_persona", {})
    if not bp:
        return "<p>페르소나 데이터 없음 (persona-panel source 미사용 또는 데이터 부족).</p>"
    sorted_p = sorted(bp.items(), key=lambda x: -x[1]["rate"])
    rows = "".join(f"""
    <tr>
      <td><strong>{p}</strong></td>
      <td>{d['hit']}/{d['total']}</td>
      <td>{int(d['rate']*100)}%</td>
      <td>{int(d['avg_confidence']*100)}%</td>
      <td>{d['avg_return_pct']:+.2f}%</td>
    </tr>
    """ for p, d in sorted_p)
    return f"""
    <table class="dt">
      <thead><tr><th>Persona</th><th>Hit/Total</th><th>적중률</th><th>평균 conf</th><th>평균 수익</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_by_source(hd: dict) -> str:
    bs = hd.get("by_source", {})
    if not bs:
        return ""
    sorted_s = sorted(bs.items(), key=lambda x: -x[1]["rate"])
    rows = "".join(f"""
    <tr><td><strong>{s}</strong></td><td>{d['hit']}/{d['total']}</td><td>{int(d['rate']*100)}%</td></tr>
    """ for s, d in sorted_s)
    return f"""
    <table class="dt">
      <thead><tr><th>Source</th><th>Hit/Total</th><th>적중률</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_calibration(hd: dict) -> str:
    cal = hd.get("calibration", {})
    if not cal or not cal.get("buckets"):
        return "<p>Calibration 데이터 없음.</p>"
    rows = ""
    for b in cal["buckets"]:
        if b["n"] == 0:
            continue
        rows += f"""
        <tr>
          <td><strong>{b['range']}%</strong></td>
          <td>{b['n']}</td>
          <td>{int(b['predicted']*100)}%</td>
          <td>{int(b['actual']*100)}%</td>
          <td style="color:{'#16a34a' if abs(b['predicted']-b['actual'])<0.05 else '#dc2626'}">{(b['actual']-b['predicted'])*100:+.0f}pp</td>
        </tr>
        """
    return f"""
    <table class="dt">
      <thead><tr><th>Confidence</th><th>n</th><th>예상</th><th>실제</th><th>차이</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;">ECE (Expected Calibration Error): {cal.get('ece')} · Brier Score: {cal.get('brier_score')}</p>
    """


def render_alpha(hd: dict) -> str:
    a = hd.get("alpha", {})
    if not a:
        return "<p>Alpha 데이터 없음.</p>"
    rows = ""
    for k, v in a.items():
        if "_avg_pct" not in k:
            continue
        bench = k.replace("vs_", "").replace("_avg_pct", "")
        n_key = k.replace("_avg_pct", "_n")
        n = a.get(n_key, 0)
        color = "#16a34a" if v > 0 else "#dc2626"
        rows += f'<tr><td>{bench}</td><td style="color:{color};font-weight:700;">{v:+.2f}%</td><td>{n}</td></tr>'
    return f"""
    <table class="dt">
      <thead><tr><th>Benchmark</th><th>BUY 평균 alpha</th><th>n</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_horizon(name: str, hd: dict) -> str:
    if hd.get("n_valid", 0) == 0:
        return f"""<h2>{name}</h2><p>데이터 부족: {hd.get('note', '')}</p>"""

    return f"""
    <h2>📊 {name} Horizon — n={hd['n_valid']}</h2>

    <h3>Overall Hit Rate</h3>
    {render_overall(hd)}

    <h3>Source별 적중률</h3>
    {render_by_source(hd)}

    <h3>Persona별 적중률 (상위)</h3>
    {render_by_persona(hd)}

    <h3>Alpha vs Benchmarks (BUY 평균)</h3>
    {render_alpha(hd)}

    <h3>Confidence Calibration</h3>
    {render_calibration(hd)}
    """


def main():
    parser = argparse.ArgumentParser(description="Backtest 보고서 PDF 생성")
    parser.add_argument("hit_rate_json")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.hit_rate_json, encoding="utf-8") as f:
        s = json.load(f)

    cover = f"""
    <div class="cover">
      <p style="color:#6b7280;font-size:11pt;">Backtest Report · {s.get('ran_at', '')[:10]}</p>
      <h1>13 Personas + Thesis-First<br/>Hit Rate Analysis</h1>
      <p style="color:#6b7280;">verdict ledger의 사후 수익률 검증</p>
      <div class="kpi-grid">
        <div class="kpi">
          <div class="num">{s.get('n_verdicts_total', 0)}</div>
          <div class="label">총 verdict</div>
        </div>
        <div class="kpi">
          <div class="num">{s.get('n_verdicts_with_data', 0)}</div>
          <div class="label">데이터 충분</div>
        </div>
        <div class="kpi">
          <div class="num">{len(s.get('horizons', {}))}</div>
          <div class="label">Horizons</div>
        </div>
        <div class="kpi">
          <div class="num">{len(s.get('benchmarks', []))}</div>
          <div class="label">Benchmarks</div>
        </div>
      </div>
      <div class="note" style="text-align:left;margin-top:1.5cm;">
        <strong>임계값:</strong> BUY ≥ +{s.get('thresholds', {}).get('buy', 5)}%,
        HOLD ±{s.get('thresholds', {}).get('hold_band', 3)}%,
        SELL ≤ {s.get('thresholds', {}).get('sell', -5)}%
      </div>
    </div>
    """

    body = cover
    for h_name, hd in s.get("horizons", {}).items():
        body += render_horizon(h_name, hd)

    html = f"""<!doctype html><html><head><meta charset="utf-8"><title>Backtest Report</title></head>
<body>{body}</body></html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_TEXT)])

    import os
    print(f"[backtest-report] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
