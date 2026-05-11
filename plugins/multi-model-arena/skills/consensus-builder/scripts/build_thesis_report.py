#!/usr/bin/env python3
"""Thesis-First 통합 보고서 생성: thesis 추출 + 4-Analyst 평가 + 종목 매핑을 한 PDF로."""
import argparse
import json
from pathlib import Path
from weasyprint import HTML, CSS


STANCE_COLOR = {"support": "#16a34a", "neutral": "#ca8a04", "rebut": "#dc2626"}
STANCE_KOR = {"support": "지지", "neutral": "중립", "rebut": "반박"}
TYPE_KOR = {"factual": "사실", "predictive": "예측", "normative": "규범", "conditional": "조건부"}
TIMEFRAME_KOR = {
    "historical": "과거",
    "present": "현재",
    "short_term": "단기(~6M)",
    "medium_term": "중기(6-24M)",
    "long_term": "장기(2y+)",
}
SIGN_BG = {"++": "#15803d", "+": "#86efac", "0": "#e5e7eb", "-": "#fca5a5", "--": "#b91c1c"}
SIGN_FG = {"++": "white", "+": "#14532d", "0": "#374151", "-": "#7f1d1d", "--": "white"}


def render_thesis_section(thesis_list: dict, eval_data: dict) -> str:
    """1) 메르의 주장 N개 + 2) 4-Analyst 평가."""
    summary = thesis_list.get("summary_one_liner", "")
    theses = thesis_list.get("theses", [])
    aggregates = {a["claim_id"]: a for a in eval_data.get("aggregates", [])}

    body = f"""
    <h2>1. 메르의 핵심 주장 (Thesis Map)</h2>
    <div class="summary-box">
      <strong>한 줄 요약 (메르의 시각):</strong><br/>
      {summary}
    </div>

    <p>총 {len(theses)}개 주장 추출. 핵심 {sum(1 for t in theses if t.get('importance')=='core')}개 + 부수 {sum(1 for t in theses if t.get('importance')=='supporting')}개</p>
    """

    for t in theses:
        cid = t.get("claim_id")
        agg = aggregates.get(cid, {}).get("aggregate", {})
        stance = agg.get("weighted_stance", "?")
        conf = agg.get("weighted_confidence", 0)
        agree = agg.get("agreement_level", "")
        scolor = STANCE_COLOR.get(stance, "#666")

        body += f"""
        <div class="thesis-card">
          <div class="thesis-head">
            <span class="thesis-id">{cid}</span>
            <span class="thesis-type">{TYPE_KOR.get(t.get('type'), t.get('type'))}</span>
            <span class="thesis-timeframe">{TIMEFRAME_KOR.get(t.get('timeframe'), '')}</span>
            <span class="thesis-importance importance-{t.get('importance')}">{t.get('importance', '')}</span>
            <span class="thesis-stance" style="background:{scolor};">
              {STANCE_KOR.get(stance, stance)} {int(conf*100)}% · {agree}
            </span>
          </div>
          <div class="thesis-body">
            <p class="thesis-claim">{t.get('claim', '')}</p>
            <p class="thesis-evidence">📜 <em>{(t.get('supporting_evidence', ''))[:200]}{'...' if len(t.get('supporting_evidence', ''))>200 else ''}</em>
            {f' ({t.get("evidence_section", "")})' if t.get("evidence_section") else ''}</p>
        """

        if cid in aggregates:
            evals = aggregates[cid].get("evaluations", {})
            body += '<table class="analyst-table"><thead><tr>'
            body += '<th>Analyst</th><th>Stance</th><th>Conf</th><th>Rationale</th>'
            body += '</tr></thead><tbody>'
            for analyst in ["macro", "industry", "empirical", "counter"]:
                e = evals.get(analyst, {})
                est = e.get("stance", "-")
                ec = STANCE_COLOR.get(est, "#666")
                body += f"""
                <tr>
                  <td><strong>{analyst.title()}</strong></td>
                  <td><span style="color:{ec};font-weight:600;">{STANCE_KOR.get(est, est)}</span></td>
                  <td>{int(e.get('confidence', 0)*100)}%</td>
                  <td style="font-size:9pt;">{e.get('rationale', '')[:280]}</td>
                </tr>
                """
            body += '</tbody></table>'

            if agg.get("key_disagreement"):
                body += f'<p class="disagreement">⚠️ <strong>핵심 이견:</strong> {agg["key_disagreement"]}</p>'

        body += '</div></div>'

    return body


def render_stocks_section(mapping: dict, thesis_list: dict) -> str:
    """3) thesis → stocks 매핑 + 4) 랭킹."""
    stocks = mapping.get("stocks", [])
    ranking = mapping.get("ranking", [])
    theses = thesis_list.get("theses", [])
    core_ids = [t["claim_id"] for t in theses if t.get("importance") == "core"]

    body = f"""
    <h2>2. Thesis → 종목 매핑 (Exposure Matrix)</h2>
    <p>각 종목이 메르의 주장 8개에 어떻게 노출되는지 (++/+/0/-/-- 5단계). 평가된 thesis의 stance·confidence·importance를 가중하여 thesis-weighted score 산출.</p>

    <h3>2-1. 종목 랭킹 (thesis-weighted score)</h3>
    <table class="ranking-table">
      <thead><tr><th>순위</th><th>종목</th><th>Ticker</th><th>Score</th><th>주요 동인</th><th>리스크</th></tr></thead>
      <tbody>
    """
    for r in ranking:
        s = next((x for x in stocks if x["ticker"] == r["ticker"]), {})
        drivers = ", ".join(s.get("primary_drivers", [])[:3]) or "-"
        risks = ", ".join(s.get("primary_risks", [])[:2]) or "-"
        body += f"""
        <tr>
          <td><strong>{r['rank']}</strong></td>
          <td><strong>{r.get('name_kr') or r['ticker']}</strong></td>
          <td><code>{r['ticker']}</code></td>
          <td><strong>{r['score']:+.2f}</strong></td>
          <td style="font-size:9pt;">{drivers}</td>
          <td style="font-size:9pt;">{risks}</td>
        </tr>
        """
    body += '</tbody></table>'

    body += '<h3>2-2. Exposure 매트릭스 (종목 × Thesis)</h3>'
    body += '<table class="exposure-matrix"><thead><tr><th>종목</th>'
    for cid in core_ids:
        body += f'<th>{cid}</th>'
    body += '<th style="background:#f3f4f6;">Score</th></tr></thead><tbody>'

    sorted_stocks = sorted(stocks, key=lambda x: -x.get("thesis_weighted_score", 0))
    for s in sorted_stocks:
        body += f'<tr><td><strong>{s.get("name_kr") or s["ticker"]}</strong><br/><code style="font-size:8pt;">{s["ticker"]}</code></td>'
        for cid in core_ids:
            exp = s.get("exposures", {}).get(cid, {})
            sign = exp.get("sign", "0")
            bg = SIGN_BG.get(sign, "#e5e7eb")
            fg = SIGN_FG.get(sign, "#374151")
            title = (exp.get("rationale", "") or "").replace('"', "'")[:80]
            body += f'<td style="background:{bg};color:{fg};font-weight:600;text-align:center;" title="{title}">{sign}</td>'
        body += f'<td style="background:#f9fafb;text-align:center;"><strong>{s.get("thesis_weighted_score", 0):+.2f}</strong></td>'
        body += '</tr>'
    body += '</tbody></table>'

    body += '<h3>2-3. 종목별 상세 분석</h3>'
    for s in sorted_stocks:
        body += f"""
        <div class="stock-detail">
          <h4>{s.get('name_kr') or s['ticker']} <code>({s['ticker']})</code> — Score {s.get('thesis_weighted_score', 0):+.2f}</h4>
          <p class="stock-summary">{s.get('summary', '')}</p>
          <p><strong>Drivers:</strong> {', '.join(s.get('primary_drivers', []))}</p>
          {f'<p style="color:#b91c1c;"><strong>Risks:</strong> {", ".join(s.get("primary_risks", []))}</p>' if s.get('primary_risks') else ''}
        </div>
        """

    return body


CSS_TEXT = """
@page { size: A4; margin: 18mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font-size: 9pt; color: #6b7280; } }
body { font-family: 'Noto Sans KR', 'Malgun Gothic', sans-serif; color: #1f2937; line-height: 1.6; font-size: 10pt; }
h1 { color: #111; font-size: 22pt; border-bottom: 2pt solid #2563eb; padding-bottom: 8pt; }
h2 { color: #111827; margin-top: 22pt; border-left: 4pt solid #2563eb; padding-left: 8pt; }
h3 { color: #1f2937; margin-top: 16pt; font-size: 12pt; }
h4 { color: #1f2937; margin-top: 12pt; font-size: 11pt; }
.summary-box { background: #eff6ff; padding: 14pt; border-left: 4pt solid #2563eb; font-size: 10.5pt; margin: 10pt 0; }
.thesis-card { border: 1pt solid #e5e7eb; border-radius: 4pt; padding: 12pt; margin: 12pt 0; page-break-inside: avoid; }
.thesis-head { display: flex; gap: 6pt; align-items: center; flex-wrap: wrap; margin-bottom: 8pt; font-size: 9pt; }
.thesis-id { background: #1f2937; color: white; padding: 2pt 8pt; border-radius: 3pt; font-family: monospace; font-weight: 700; }
.thesis-type { background: #eef2ff; color: #4338ca; padding: 2pt 6pt; border-radius: 3pt; }
.thesis-timeframe { background: #f0fdf4; color: #166534; padding: 2pt 6pt; border-radius: 3pt; }
.thesis-importance { padding: 2pt 6pt; border-radius: 3pt; }
.importance-core { background: #fee2e2; color: #b91c1c; }
.importance-supporting { background: #f3f4f6; color: #4b5563; }
.thesis-stance { color: white; padding: 2pt 8pt; border-radius: 3pt; font-weight: 600; margin-left: auto; }
.thesis-claim { font-size: 11pt; font-weight: 600; margin: 6pt 0; }
.thesis-evidence { color: #6b7280; font-size: 9pt; margin: 4pt 0 8pt 0; }
.analyst-table { width: 100%; border-collapse: collapse; margin: 6pt 0; font-size: 9pt; }
.analyst-table th, .analyst-table td { border: 1pt solid #e5e7eb; padding: 5pt 6pt; text-align: left; vertical-align: top; }
.analyst-table th { background: #f9fafb; font-size: 8pt; }
.disagreement { background: #fef3c7; padding: 6pt 10pt; border-left: 3pt solid #f59e0b; font-size: 9pt; margin: 6pt 0 0 0; }
.ranking-table { width: 100%; border-collapse: collapse; font-size: 9.5pt; }
.ranking-table th, .ranking-table td { border: 1pt solid #e5e7eb; padding: 5pt 6pt; vertical-align: top; }
.ranking-table th { background: #f3f4f6; }
.exposure-matrix { width: 100%; border-collapse: collapse; margin: 8pt 0; font-size: 9pt; }
.exposure-matrix th, .exposure-matrix td { border: 1pt solid #d1d5db; padding: 4pt; text-align: center; }
.exposure-matrix th { background: #f3f4f6; font-size: 8.5pt; }
.exposure-matrix td:first-child { text-align: left; }
.stock-detail { background: #f9fafb; padding: 10pt; border-radius: 4pt; margin: 6pt 0; page-break-inside: avoid; }
.stock-summary { font-style: italic; color: #4b5563; }
code { background: #f3f4f6; padding: 1pt 4pt; border-radius: 3pt; font-family: monospace; font-size: 0.92em; }
.cover { page-break-after: always; padding-top: 4cm; text-align: center; }
.cover h1 { border: none; font-size: 28pt; }
.cover-meta { color: #6b7280; font-size: 11pt; }
"""


def main():
    parser = argparse.ArgumentParser(description="Thesis-first 통합 보고서")
    parser.add_argument("--thesis", required=True, help="thesis_list.json")
    parser.add_argument("--eval-dir", required=True, help="thesis_eval 디렉토리")
    parser.add_argument("--mapping", required=True, help="thesis_to_stocks.json")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    with open(args.thesis, encoding="utf-8") as f:
        thesis_list = json.load(f)

    eval_path = Path(args.eval_dir) / "all_aggregate.json"
    with open(eval_path, encoding="utf-8") as f:
        eval_data = json.load(f)

    with open(args.mapping, encoding="utf-8") as f:
        mapping = json.load(f)

    post_meta = thesis_list.get("post_meta", {})

    cover = f"""
    <div class="cover">
      <div class="cover-meta">메르 블로그 분석 — Thesis-First Pipeline · 2026-04-28</div>
      <h1>{post_meta.get('title', '')}</h1>
      <div class="cover-meta">메르(ranto28) — <a href="{post_meta.get('url', '')}">{post_meta.get('url', '')}</a></div>
      <p style="margin-top: 1.5cm; color: #6b7280;">
        분석 흐름: 본문 → ★ 메르의 주장 N개 → ★ 4-Analyst 평가 → ★ 종목 매핑<br/>
        모델: Claude Opus (Cowork 인라인) + GPT-5.5 + Gemini 3.1 (planned)
      </p>
      <p style="margin-top: 2cm; color: #92400e; background: #fef3c7; padding: 12pt;">
        ⚠️ 본 보고서는 교육·연구 목적이며 투자 자문이 아닙니다.
      </p>
    </div>
    """

    body = render_thesis_section(thesis_list, eval_data)
    body += render_stocks_section(mapping, thesis_list)

    html = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>{post_meta.get('title', '')}</title></head>
<body>{cover}{body}</body></html>"""

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_TEXT)])

    import os
    print(f"[thesis-report] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
