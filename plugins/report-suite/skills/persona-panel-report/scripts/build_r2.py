#!/usr/bin/env python3
"""R2: Persona Panel Report — 13명 페르소나 평가 종합."""
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from weasyprint import HTML, CSS

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR.parent.parent / "_common"))
from css import CSS_BASE, fmt_money_krw, fmt_pct, VERDICT_COLOR, VERDICT_KOR
import chart_utils as cu
from persona_intro import render_persona_intro, PERSONA_INTRO
from ticker_resolver import resolve_ticker
from guru_checklist import render_guru_checklist


PERSONA_NAMES = {
    "warren-buffett": ("워런 버핏", "Warren Buffett", "value"),
    "charlie-munger": ("찰리 멍거", "Charlie Munger", "value"),
    "peter-lynch": ("피터 린치", "Peter Lynch", "growth"),
    "cathie-wood": ("캐시 우드", "Cathie Wood", "growth"),
    "michael-burry": ("마이클 버리", "Michael Burry", "value-contrarian"),
    "nassim-taleb": ("나심 탈레브", "Nassim Taleb", "risk"),
    "ben-graham": ("벤저민 그레이엄", "Ben Graham", "value"),
    "bill-ackman": ("빌 애크먼", "Bill Ackman", "activist"),
    "mohnish-pabrai": ("모니시 파브라이", "Mohnish Pabrai", "value"),
    "phil-fisher": ("필 피셔", "Phil Fisher", "growth"),
    "rakesh-jhunjhunwala": ("라케시 준준왈라", "Rakesh Jhunjhunwala", "growth-em"),
    "stanley-druckenmiller": ("스탠리 드러켄밀러", "Stanley Druckenmiller", "macro"),
    "aswath-damodaran": ("애스워드 다모다란", "Aswath Damodaran", "valuation"),
}


def build_cover(meta: dict, agg: dict) -> str:
    dist = agg.get("verdict_distribution", {})
    bull = dist.get("lean_bullish", {"count": 0, "pct": 0})
    neu = dist.get("neutral", {"count": 0, "pct": 0})
    bear = dist.get("lean_bearish", {"count": 0, "pct": 0})

    # Verdict 분포 pie chart (cover에 embed)
    pie = ""
    if (bull["count"] + neu["count"] + bear["count"]) > 0:
        pie_labels = []
        pie_values = []
        pie_colors = []
        if bull["count"] > 0:
            pie_labels.append(f"매수 {bull['count']}")
            pie_values.append(bull["count"])
            pie_colors.append(cu.COLORS["bull"])
        if neu["count"] > 0:
            pie_labels.append(f"중립 {neu['count']}")
            pie_values.append(neu["count"])
            pie_colors.append(cu.COLORS["neutral"])
        if bear["count"] > 0:
            pie_labels.append(f"매도 {bear['count']}")
            pie_values.append(bear["count"])
            pie_colors.append(cu.COLORS["bear"])
        pie = cu.pie_chart(pie_labels, pie_values, title="Verdict 분포", colors=pie_colors)

    ticker_meta = meta.get('ticker', '')
    info = resolve_ticker(ticker_meta) if ticker_meta else {"kr": ""}
    company_kr = info.get("kr", ticker_meta)
    return f"""
    <div class="cover">
      <p class="cover-meta">R2. Persona Panel Report · {meta.get('date', '')}</p>
      <h1>{company_kr} 13 Personas Panel</h1>
      <p class="cover-meta"><code>{ticker_meta}</code> · {info.get('sector', meta.get('subjects', ''))}</p>
      <div class="kpi-grid">
        <div class="kpi"><div class="num green">{bull['count']}</div><div class="label">매수 성향</div></div>
        <div class="kpi"><div class="num amber">{neu['count']}</div><div class="label">중립</div></div>
        <div class="kpi"><div class="num red">{bear['count']}</div><div class="label">매도 성향</div></div>
        <div class="kpi"><div class="num">{int((agg.get('average_confidence') or 0)*100)}%</div><div class="label">평균 신뢰도</div></div>
      </div>
      {pie}
      <div class="info" style="text-align:left;margin-top:1cm;">
        <strong>이 보고서의 역할</strong><br/>
        같은 fact-base 위에서 13명 대가의 lens가 어떻게 다른 결론을 내는가? 합의는 어디에서, 이견은 어디에서 발생하는가?
      </div>
    </div>
    """


def render_persona_table(personas: dict) -> str:
    rows = ""
    for pid, p in sorted(personas.items(), key=lambda x: -(x[1].get('confidence') or 0)):
        v = p.get("verdict", "neutral")
        color = VERDICT_COLOR.get(v, "#666")
        kr, en, cat = PERSONA_NAMES.get(pid, (pid, pid, "other"))
        rows += f"""
        <tr>
          <td><strong>{kr}</strong><br/><span style="font-size:8pt;color:#6b7280;">{en} · {cat}</span></td>
          <td><span style="color:{color};font-weight:600;">{VERDICT_KOR.get(v, v)}</span></td>
          <td>{int((p.get('confidence') or 0)*100)}%</td>
          <td>{p.get('horizon', '-')}</td>
          <td style="font-size:9pt;">{((p.get('key_concerns_top3') or [None])[0] or '-')}</td>
        </tr>
        """
    return f"""
    <h2>1. 13 페르소나 종합 표</h2>
    <table class="dt">
      <thead><tr><th>페르소나</th><th>Verdict</th><th>신뢰도</th><th>Horizon</th><th>주요 우려</th></tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


def render_style_split(agg: dict, personas: dict) -> str:
    style = agg.get("style_split", {})
    body = '<h2>2. Style Split — 투자 스타일별 합의</h2>'

    # Stacked bar chart by style
    if style:
        cats = []
        bull_counts = []
        neu_counts = []
        bear_counts = []
        for cat, info in style.items():
            cats.append(cat)
            members = info.get("members", [])
            b = sum(1 for m in members if m.get("verdict") == "lean_bullish")
            n = sum(1 for m in members if m.get("verdict") == "neutral")
            r = sum(1 for m in members if m.get("verdict") == "lean_bearish")
            bull_counts.append(b)
            neu_counts.append(n)
            bear_counts.append(r)
        body += cu.stacked_bar(cats, {"매수": bull_counts, "중립": neu_counts, "매도": bear_counts},
                                title="투자 스타일별 verdict 분포",
                                colors={"매수": cu.COLORS["bull"], "중립": cu.COLORS["neutral"], "매도": cu.COLORS["bear"]})

    for cat, info in style.items():
        members = info.get("members", [])
        members_str = ", ".join([
            f'<span style="color:{VERDICT_COLOR.get(m.get("verdict"), "#666")};">{PERSONA_NAMES.get(m["persona_id"], (m["persona_id"], "", ""))[0]}</span>'
            for m in members
        ])
        body += f"""
        <div class="info">
          <strong>{cat.upper()}</strong> ({info.get('n_members', 0)}명) — 우세: <span class="bull">{info.get('dominant', '?')}</span><br/>
          <span style="font-size:9pt;">{members_str}</span>
        </div>
        """

    # Confidence 분포
    confs = [p.get("confidence", 0) for p in personas.values() if p.get("confidence") is not None]
    if confs:
        body += '<h3>2-1. Confidence 분포</h3>'
        body += cu.confidence_histogram(confs, title="13명 페르소나 confidence 분포")
    return body


def render_thesis_persona_matrix(personas_full: dict, theses: list[dict]) -> str:
    """Thesis × Persona stance matrix — heatmap + table.

    데이터 binding 진단 (Phase 4 — 사용자 요청 #2):
    - personas_full[pid]['thesis_lens_applications']에 [{'claim_id': 'T1', 'stance': '...'}] 필요
    - 누락 시 fallback 메시지 + 진단 정보 표시
    """
    body = '<h2>3. Thesis × Persona Matrix</h2>'
    body += '<p style="font-size:9.5pt;">각 thesis에 대한 13명 페르소나의 stance (support/challenge/neutral). 합의 영역과 split 영역을 한눈에.</p>'

    # 데이터 부재 시 명시적 fallback (silent skip 금지)
    if not theses:
        body += '<div class="warn"><strong>⚠️ Thesis 데이터 부재</strong> — Standalone 분석(블로그 글 없이 ticker만 분석)인 경우 이 섹션이 비어있습니다. Thesis × Persona matrix는 블로그 글에서 추출된 thesis가 있어야 작동합니다.</div>'
        return body
    if not personas_full:
        body += '<div class="warn"><strong>⚠️ Persona full 데이터 부재</strong> — persona_panel/{ticker}/{persona_id}.json 파일이 누락되었거나 로딩되지 않았습니다.</div>'
        return body

    # Diagnose binding: do any personas have thesis_lens_applications?
    has_lens_count = sum(1 for p in personas_full.values() if p.get("thesis_lens_applications"))
    if has_lens_count == 0:
        body += f'''<div class="warn">
        <strong>⚠️ Thesis-Persona Binding 데이터 부재</strong> — {len(personas_full)}명의 페르소나 평가 결과에서
        <code>thesis_lens_applications</code> 필드가 모두 비어있습니다.<br/>
        <strong>원인</strong>: persona-evaluator의 LLM 프롬프트가 이 필드를 출력하지 않았습니다.<br/>
        <strong>해결</strong>: <code>plugins/investor-personas/skills/persona-evaluator/SKILL.md</code>의
        프롬프트 템플릿에 thesis별 stance 평가 강제 출력을 추가해야 합니다.
        </div>'''
        # Render fallback table showing thesis list only (no stances)
        body += '<h3>Thesis List (stance 미평가)</h3>'
        body += '<table class="dt"><thead><tr><th>ID</th><th>Claim</th></tr></thead><tbody>'
        for t in theses[:12]:
            body += f'<tr><td><strong>{t.get("claim_id", "?")}</strong></td><td>{t.get("claim", "")}</td></tr>'
        body += '</tbody></table>'
        return body

    # Heatmap matrix — accept both 'challenge' and 'rebut' as the negative stance
    stance_to_num = {"support": 1.0, "neutral": 0.0, "challenge": -1.0, "rebut": -1.0}
    persona_ids = sorted(personas_full.keys())
    persona_labels = [PERSONA_NAMES.get(pid, (pid, "", ""))[0] for pid in persona_ids]
    matrix = []
    row_labels = []
    for t in theses[:8]:
        cid = t.get("claim_id") or t.get("id")  # robust: fall back to 'id'
        row = []
        for pid in persona_ids:
            p = personas_full[pid]
            stance = "neutral"
            for app in (p.get("thesis_lens_applications") or []):
                # Accept both 'claim_id' and 'thesis_id'
                app_cid = app.get("claim_id") or app.get("thesis_id")
                if app_cid == cid:
                    raw = app.get("stance", "neutral")
                    stance = "challenge" if raw == "rebut" else raw
                    break
            row.append(stance_to_num.get(stance, 0))
        matrix.append(row)
        row_labels.append(cid)

    if matrix and any(any(v != 0 for v in r) for r in matrix):
        body += cu.heatmap(matrix, row_labels, persona_labels,
                            title="Thesis × Persona Stance Matrix (녹: support · 빨: challenge)",
                            cmap="RdYlGn", vmin=-1, vmax=1, annotate=False)
    else:
        body += '<div class="info">⚠️ 모든 stance가 neutral로 평가됨 — 13명 페르소나의 thesis별 의견 분화가 발견되지 않음.</div>'

    body += '<table class="dt"><thead><tr><th>Thesis</th>'
    for pid in persona_ids:
        kr = PERSONA_NAMES.get(pid, (pid, "", ""))[0]
        body += f'<th style="font-size:8pt;writing-mode:vertical-rl;height:80pt;">{kr}</th>'
    body += '</tr></thead><tbody>'

    for t in theses[:8]:
        cid = t.get("claim_id") or t.get("id")
        body += f'<tr><td><strong>{cid}</strong><br/><span style="font-size:8pt;">{t.get("claim", "")}</span></td>'
        for pid in persona_ids:
            p = personas_full[pid]
            stance = "?"
            for app in (p.get("thesis_lens_applications") or []):
                app_cid = app.get("claim_id") or app.get("thesis_id")
                if app_cid == cid:
                    raw = app.get("stance", "?")
                    stance = "challenge" if raw == "rebut" else raw
                    break
            color = {"support": "#16a34a", "challenge": "#dc2626", "neutral": "#ca8a04"}.get(stance, "#e5e7eb")
            symbol = {"support": "✓", "challenge": "✗", "neutral": "○"}.get(stance, "·")
            body += f'<td style="text-align:center;background:{color};color:white;font-weight:700;">{symbol}</td>'
        body += '</tr>'
    body += '</tbody></table>'
    body += '<p style="font-size:8pt;color:#6b7280;">✓ = support, ✗ = challenge, ○ = neutral, · = 미평가</p>'
    return body


def render_universal_concerns(agg: dict) -> str:
    concerns = agg.get("universal_concerns", [])
    if not concerns:
        return '<h2>4. Universal Concerns</h2><p>다수 페르소나 공통 우려 키워드 미발견.</p>'
    body = '<h2>4. Universal Concerns (다수가 공통으로 짚는 우려)</h2>'
    for c in concerns[:8]:
        body += f"""
        <div class="warn">
          <strong>[{c['theme']}]</strong> {c['frequency']}건 ({len(c.get('personas', []))} 명 unique)<br/>
          <em style="font-size:9pt;">{(c.get('examples') or ['-'])[0][:200]}</em>
        </div>
        """
    return body


def render_persona_details(personas_full: dict) -> str:
    body = """<h2>5. 페르소나별 상세 (각 대가의 철학 + 이 종목 분석)</h2>
    <div class="info" style="margin:8pt 0;">
      <strong>📖 이 섹션 읽는 법</strong>: 각 페르소나마다 (1) 투자 철학·배경 소개 → (2) 이 종목에 대한 verdict + 신뢰도 →
      (3) 우려 / 기회 → (4) <strong>narrative vs quant 우선순위</strong>(각 페르소나의 정체성이 어떻게
      판단에 작용했는지) 순으로 구성됩니다. 페르소나 13명을 비교하며 읽으면 같은 사실에 대한
      서로 다른 해석을 학습할 수 있습니다.
    </div>
    """
    for pid, p in sorted(personas_full.items(), key=lambda x: -(x[1].get('confidence') or 0)):
        kr, en, cat = PERSONA_NAMES.get(pid, (pid, "", ""))
        v = p.get("verdict", "neutral")
        color = VERDICT_COLOR.get(v, "#666")

        # 페르소나 철학·배경 소개 박스 (NEW — 학습용 풍부)
        intro_html = render_persona_intro(pid)

        body += f"""
        <h3>{kr} ({en}) — <span style="color:{color};">{VERDICT_KOR.get(v, v)}</span> · 신뢰도 {int((p.get('confidence') or 0)*100)}%</h3>
        <p><strong>Horizon:</strong> {p.get('horizon', '-')} · <strong>Style:</strong> {cat}</p>
        {intro_html}
        """

        # 이 종목에 대한 Verdict 핵심 카드
        body += f"""
        <div style="background:#eef2ff;border-left:4pt solid {color};padding:12pt 16pt;margin:10pt 0;">
          <div style="font-size:11pt;font-weight:700;color:{color};">📊 이 종목에 대한 {kr}의 평가</div>
          <p style="margin:6pt 0;"><strong>Verdict:</strong> <span style="color:{color};font-weight:600;">{VERDICT_KOR.get(v, v)}</span> · <strong>신뢰도</strong> {int((p.get('confidence') or 0)*100)}% · <strong>Horizon</strong> {p.get('horizon', '-')}</p>
        </div>
        """

        # Stage results — 5단계 분석 (accept both canonical and legacy schema)
        stage_rows = ""
        for i, s in enumerate((p.get("stage_results") or [])[:5], 1):
            # Canonical schema fields
            stage_num = s.get('stage_num', i)
            stage_name = s.get('stage_name')
            rationale = s.get('rationale')
            passed_field = s.get('passed')
            # Legacy schema fallback: {'stage': '이해 (Understand)', 'content': '...'}
            if not stage_name:
                stage_name = s.get('stage', f'Stage {i}')
            if not rationale:
                rationale = s.get('content', '')
            # If 'passed' field missing, assume the persona completed its stage (= Pass)
            if passed_field is None:
                passed_field = bool(rationale)  # has content → pass
            status_html = '✓ Pass' if passed_field else '✗ Fail'
            stage_rows += f"""
            <tr>
              <td><strong>Stage {stage_num}. {stage_name}</strong></td>
              <td>{status_html}</td>
              <td style="font-size:9.5pt;">{rationale}</td>
            </tr>
            """
        if stage_rows:
            body += f'<p style="margin-top:10pt;"><strong>5단계 분석 결과 (이 페르소나의 의무 framework)</strong></p>'
            body += f'<table class="dt"><thead><tr><th>Stage</th><th>결과</th><th>Rationale</th></tr></thead><tbody>{stage_rows}</tbody></table>'

        # Concerns / opportunities — 풍부하게 (각각 별도 섹션, 자세히)
        concerns = p.get("key_concerns_top3") or []
        if concerns:
            body += '<p style="margin-top:10pt;"><strong>🔴 우려 사항 (이 페르소나가 짚는 위험)</strong></p>'
            body += '<ul style="font-size:10pt;line-height:1.7;">'
            for c in concerns:
                body += f'<li>{c}</li>'
            body += '</ul>'

        opps = p.get("key_opportunities_top3") or []
        if opps:
            body += '<p style="margin-top:8pt;"><strong>🟢 기회 요인 (이 페르소나가 보는 매력)</strong></p>'
            body += '<ul style="font-size:10pt;line-height:1.7;">'
            for o in opps:
                body += f'<li>{o}</li>'
            body += '</ul>'

        # Narrative vs Quant 우선순위
        if p.get("narrative_vs_quant_resolution"):
            body += f"""<div class="win" style="margin-top:8pt;">
              <strong>⚖️ Narrative vs Quant 우선순위</strong> (이 페르소나의 정체성이 판단에 어떻게 작용했는가)<br/>
              <span style="font-size:10pt;">{p["narrative_vs_quant_resolution"]}</span>
            </div>"""

        # Uncertainty
        if p.get("uncertainty"):
            body += f"""<div class="note" style="margin-top:6pt;">
              <strong>⚠️ Verdict이 뒤집힐 가정</strong>: <span style="font-size:10pt;">{p["uncertainty"]}</span>
            </div>"""

        # NEW (요청 #5): Guru별 판단 framework checklist (10+ 항목 만족 여부)
        ticker_meta = p.get("ticker", "이 종목")
        body += render_guru_checklist(pid, kr, ticker_meta, p)

        body += '<hr style="margin:18pt 0;border:none;border-top:1pt solid #e5e7eb;"/>'
    return body


def main():
    parser = argparse.ArgumentParser(description="R2 Persona Panel Report")
    parser.add_argument("--aggregate", required=True, help="aggregate.json (panel)")
    parser.add_argument("--full-results", help="dir의 모든 페르소나 JSON (thesis_lens_applications 포함)")
    parser.add_argument("--thesis", help="thesis_list.json — Thesis × Persona matrix용")
    parser.add_argument("--meta", help="JSON: ticker/date/subjects")
    parser.add_argument("--output", "-o", required=True)
    args = parser.parse_args()

    agg = json.load(open(args.aggregate))
    personas_summary = agg.get("persona_results", {})

    personas_full = {}
    if args.full_results:
        for p in Path(args.full_results).glob("*.json"):
            if p.stem in ("aggregate", "panel_summary"):
                continue
            try:
                personas_full[p.stem] = json.load(open(p, encoding="utf-8"))
            except Exception:
                pass

    theses = []
    if args.thesis:
        theses = json.load(open(args.thesis)).get("theses", [])

    meta = json.load(open(args.meta)) if args.meta else {"ticker": agg.get("ticker", "?"), "date": ""}

    body = build_cover(meta, agg)
    body += render_persona_table(personas_summary)
    body += render_style_split(agg, personas_summary)
    if theses and personas_full:
        body += render_thesis_persona_matrix(personas_full, theses)
    body += render_universal_concerns(agg)
    body += render_persona_details(personas_full or personas_summary)

    html = f"<!doctype html><html><head><meta charset='utf-8'><title>R2 Persona Panel</title></head><body>{body}</body></html>"
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(args.output, stylesheets=[CSS(string=CSS_BASE)])

    import os
    print(f"[R2] saved: {args.output} ({os.path.getsize(args.output):,} bytes)")


if __name__ == "__main__":
    main()
