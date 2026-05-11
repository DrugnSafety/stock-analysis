#!/usr/bin/env python3
"""Persona Panel aggregate.json → PDF report."""
import argparse
import json
from pathlib import Path
from weasyprint import HTML, CSS


VERDICT_COLOR = {"lean_bullish": "#16a34a", "neutral": "#ca8a04", "lean_bearish": "#dc2626"}
VERDICT_KOR = {"lean_bullish": "🟢 매수 성향", "neutral": "🟡 중립", "lean_bearish": "🔴 매도 성향"}

CSS_TEXT = """
@page { size: A4; margin: 18mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; } }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.5; font-size: 10pt; }
h1 { color: #111; font-size: 22pt; border-bottom: 2pt solid #2563eb; padding-bottom: 8pt; }
h2 { color: #111827; margin-top: 24pt; border-left: 4pt solid #2563eb; padding-left: 8pt; font-size: 16pt; }
h3 { color: #1f2937; margin-top: 16pt; font-size: 12pt; }
h4 { font-size: 11pt; margin-top: 14pt; }
.cover { page-break-after: always; padding-top: 3cm; text-align: center; }
.cover h1 { border: none; font-size: 30pt; }
.dist-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12pt; margin: 16pt 0; }
.dist-card { padding: 16pt; border-radius: 6pt; text-align: center; color: white; }
.dist-bull { background: #16a34a; } .dist-neu { background: #ca8a04; } .dist-bear { background: #dc2626; }
.dist-card .num { font-size: 32pt; font-weight: 700; }
.persona-table { width: 100%; border-collapse: collapse; font-size: 9pt; }
.persona-table th, .persona-table td { border: 1pt solid #e5e7eb; padding: 5pt 7pt; vertical-align: top; }
.persona-table th { background: #f3f4f6; }
.persona-card { border-left: 4pt solid #2563eb; background: #f9fafb; padding: 10pt 14pt; margin: 8pt 0; page-break-inside: avoid; }
.persona-card.bull { border-left-color: #16a34a; }
.persona-card.neu { border-left-color: #ca8a04; }
.persona-card.bear { border-left-color: #dc2626; }
.style-box { background: #eff6ff; padding: 10pt 14pt; border-left: 3pt solid #2563eb; margin: 8pt 0; }
.concern-item { background: #fef3c7; padding: 6pt 10pt; border-left: 3pt solid #f59e0b; margin: 4pt 0; font-size: 9.5pt; }
code { background: #f3f4f6; padding: 1pt 4pt; border-radius: 3pt; font-family: monospace; font-size: 0.92em; }
"""


def render(agg: dict) -> str:
    ticker = agg.get("ticker", "?")
    n = agg.get("n_personas", 0)
    dist = agg.get("verdict_distribution", {})
    avg_conf = agg.get("average_confidence", 0)
    style = agg.get("style_split", {})
    concerns = agg.get("universal_concerns", [])
    personas = agg.get("persona_results", {})

    bull = dist.get("lean_bullish", {"count": 0, "pct": 0})
    neu = dist.get("neutral", {"count": 0, "pct": 0})
    bear = dist.get("lean_bearish", {"count": 0, "pct": 0})

    cover = f"""
    <div class="cover">
      <p style="color:#6b7280;font-size:11pt;">Investor Personas Panel · {agg.get('aggregated_at', '')[:10]}</p>
      <h1>{ticker}</h1>
      <p style="font-size:13pt;color:#6b7280;">13명 전설적 투자자의 lens로 평가한 종목 분석</p>

      <div class="dist-grid">
        <div class="dist-card dist-bull"><div class="num">{bull['count']}</div><div>매수 성향</div><div>{bull['pct']}%</div></div>
        <div class="dist-card dist-neu"><div class="num">{neu['count']}</div><div>중립</div><div>{neu['pct']}%</div></div>
        <div class="dist-card dist-bear"><div class="num">{bear['count']}</div><div>매도 성향</div><div>{bear['pct']}%</div></div>
      </div>

      <p style="font-size:11pt;color:#374151;">평균 신뢰도: {int(avg_conf*100)}% · 참여 페르소나 {n}명</p>
    </div>
    """

    # Persona 표
    table_rows = ""
    for pid, p in sorted(personas.items(), key=lambda x: -x[1].get("confidence", 0)):
        v = p.get("verdict", "neutral")
        vc = VERDICT_COLOR.get(v, "#666")
        table_rows += f"""
        <tr>
          <td><strong>{p.get('persona_kr')}</strong><br/><span style="color:#6b7280;font-size:8.5pt;">{p.get('persona_en')}</span></td>
          <td><span style="color:{vc};font-weight:600;">{VERDICT_KOR.get(v, v)}</span></td>
          <td>{int(p.get('confidence', 0)*100)}%</td>
          <td>{p.get('horizon', '-')}</td>
          <td style="font-size:9pt;">{(p.get('key_concerns_top3', [{}])[:1] or ['-'])[0][:120] if p.get('key_concerns_top3') else '-'}</td>
        </tr>
        """

    table_section = f"""
    <h2>1. 13명 페르소나 종합 표</h2>
    <table class="persona-table">
      <thead><tr><th>페르소나</th><th>Verdict</th><th>신뢰도</th><th>Horizon</th><th>주요 우려</th></tr></thead>
      <tbody>{table_rows}</tbody>
    </table>
    """

    # Style split
    style_html = '<h2>2. Style Split — 투자 스타일별 합의 분석</h2>'
    for cat, info in style.items():
        members_html = ""
        for m in info.get("members", []):
            mv = m.get("verdict", "neutral")
            mc = VERDICT_COLOR.get(mv, "#666")
            mname = personas.get(m["persona_id"], {}).get("persona_kr", m["persona_id"])
            members_html += f'<span style="color:{mc};">{mname} ({mv})</span>, '
        style_html += f"""
        <div class="style-box">
          <strong>{cat.upper()}</strong> ({info.get('n_members', 0)}명) — 우세: {info.get('dominant', '?')}<br/>
          <span style="font-size:9pt;">{members_html.rstrip(', ')}</span>
        </div>
        """

    # Universal concerns
    concerns_html = '<h2>3. Universal Concerns (다수 페르소나가 짚는 우려)</h2>'
    if not concerns:
        concerns_html += '<p>여러 페르소나에서 공통 우려 키워드 발견되지 않음.</p>'
    else:
        for c in concerns[:6]:
            personas_list = ", ".join(personas.get(p, {}).get("persona_kr", p) for p in c.get("personas", []))
            concerns_html += f"""
            <div class="concern-item">
              <strong>[{c['theme']}]</strong> {c['frequency']}명 ({len(c['personas'])} unique persona) — {personas_list}<br/>
              <em style="font-size:9pt;">예: {c['examples'][0][:200]}</em>
            </div>
            """

    # Persona detail cards
    detail_html = '<h2>4. 페르소나별 상세</h2>'
    for pid, p in sorted(personas.items(), key=lambda x: -x[1].get("confidence", 0)):
        v = p.get("verdict", "neutral")
        klass = "bull" if v == "lean_bullish" else "bear" if v == "lean_bearish" else "neu"
        opp = "; ".join((p.get("key_opportunities_top3", []) or [])[:2])
        con = "; ".join((p.get("key_concerns_top3", []) or [])[:2])
        detail_html += f"""
        <div class="persona-card {klass}">
          <h4>{p.get('persona_kr')} ({p.get('persona_en')}) — {VERDICT_KOR.get(v, v)} {int(p.get('confidence', 0)*100)}% · {p.get('horizon', '-')}</h4>
          {f'<p>🟢 <strong>기회:</strong> {opp}</p>' if opp else ''}
          {f'<p>🔴 <strong>우려:</strong> {con}</p>' if con else ''}
          {f'<p style="font-size:9pt;color:#6b7280;"><em>불확실성: {p.get("uncertainty", "")[:200]}</em></p>' if p.get('uncertainty') else ''}
        </div>
        """

    return cover + table_section + style_html + concerns_html + detail_html


def main():
    parser = argparse.ArgumentParser(description="Persona Panel PDF 생성")
    parser.add_argument("aggregate_json")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.aggregate_json, encoding="utf-8") as f:
        agg = json.load(f)

    body = render(agg)
    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{agg.get('ticker', '')} Personas Panel</title></head>
<body>{body}</body></html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_TEXT)])

    import os
    print(f"[panel-pdf] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
