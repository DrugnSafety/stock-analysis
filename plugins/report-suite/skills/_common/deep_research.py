"""Deep Research-style report sections.

Adds substantive analytical depth beyond the base Quant/Persona/Executive
reports — modeled on the structure of professional sell-side reports and
"Deep Research"-style assistant output.

All renderers return HTML strings ready to drop into a WeasyPrint pipeline.
"""
from __future__ import annotations

from typing import Optional
from currency_format import format_price


# ── Industry Context Section ─────────────────────────────────────────────
def render_industry_context(
    industry: str,
    overview: str,
    competitive_landscape: list[dict],
    recent_news: list[dict],
    market_size: Optional[dict] = None,
) -> str:
    """Industry context section.

    competitive_landscape: [{"name": "...", "ticker": "...", "share_pct": 0, "moat": "..."}]
    recent_news: [{"date": "...", "title": "...", "source": "...", "summary": "..."}]
    market_size: {"current_usd_bn": 100, "cagr_pct": 15, "horizon": "2024-2030"}
    """
    market_size_html = ""
    if market_size:
        _cur = market_size.get('current_usd_bn')
        _cagr = market_size.get('cagr_pct')
        _hz = market_size.get('horizon', '')
        if isinstance(_cur, (int, float)) and isinstance(_cagr, (int, float)):
            market_size_html = f"""
        <div class="info" style="margin-top:8pt;">
          <strong>시장 규모</strong>: 현재 ${_cur:.1f}B
          → {_hz} CAGR <strong>{_cagr:.1f}%</strong>
        </div>
        """
        elif _hz:
            market_size_html = f"""
        <div class="info" style="margin-top:8pt;">
          <strong>시장 규모</strong>: {_hz}
        </div>
        """

    competitors_rows = "".join(
        f"""
        <tr>
          <td><strong>{c['name']}</strong> <code>{c.get('ticker', '-')}</code></td>
          <td style="text-align:center;">{(f"{c['share_pct']:.1f}%" if isinstance(c.get('share_pct'), (int, float)) else "—")}</td>
          <td>{c.get('moat', '-')}</td>
        </tr>
        """
        for c in competitive_landscape
    )

    def _src_cell(n: dict) -> str:
        src = n.get('source', '-')
        url = n.get('url')
        if url:
            # 출처 URL 있으면 하이퍼링크 + 검증가능 배지 (Phase 7 절차 A)
            return (f'<a href="{url}" style="color:#2563eb;text-decoration:none;">'
                    f'{src} ↗</a> <span style="font-size:7.5pt;color:#16a34a;">✓출처</span>')
        return f'<em>{src}</em>'

    news_rows = "".join(
        f"""
        <tr>
          <td style="white-space:nowrap;font-size:8.5pt;">{n.get('date', '')}</td>
          <td><strong>{n['title']}</strong><br/>
              <span style="font-size:8.5pt;color:#6b7280;">{n.get('summary', '')} ({_src_cell(n)})</span></td>
        </tr>
        """
        for n in recent_news
    )

    # ── Sprint E-5: paragraph → bullet point ──
    def _industry_to_bullets(text: str, min_len: int = 18) -> str:
        import re as _re
        if not text or not text.strip():
            return text
        if "<ul" in text or "<li" in text:
            return text
        parts = _re.split(
            r"(?<=다[.])\s+|(?<=음[.])\s+|(?<=함[.])\s+|(?<=[.])\s+(?=[A-Z가-힣])|\n+",
            text,
        )
        items = [p.strip() for p in parts if p and len(p.strip()) >= min_len]
        if len(items) <= 1:
            return f"<p>{text}</p>"
        lis = "".join(f"<li style='margin-bottom:5pt;'>{it}</li>" for it in items)
        return f"<ul style='margin:6pt 0 0 0;padding-left:18pt;line-height:1.6;'>{lis}</ul>"

    return f"""
    <h2>🌐 산업 맥락 (Industry Context)</h2>
    <h3>{industry} 개요</h3>
    {_industry_to_bullets(overview)}
    {market_size_html}

    <h3>경쟁 구도</h3>
    <table class="dt">
      <thead><tr><th>회사</th><th>점유율</th><th>경쟁우위 (Moat)</th></tr></thead>
      <tbody>{competitors_rows}</tbody>
    </table>

    <h3>최근 산업 뉴스 (90일 이내)</h3>
    <table class="dt">
      <thead><tr><th style="width:14%">날짜</th><th>내용</th></tr></thead>
      <tbody>{news_rows}</tbody>
    </table>
    """


# ── Financial Deep Dive Section ─────────────────────────────────────────
def render_financial_deep_dive(
    ticker: str,
    pl_5y: list[dict],  # [{"year": 2021, "revenue": 100, "op_income": 20, "net_income": 15}]
    bs_snapshot: dict,  # {"total_assets": 500, "total_liab": 200, "equity": 300, "cash": 50, "debt": 100}
    cf_summary: dict,  # {"ocf_5y_avg": 80, "fcf_5y_avg": 40, "capex_intensity": 0.10}
    peer_compare: list[dict],  # [{"ticker": "...", "name": "...", "pe": 15, "pb": 1.2, "roe": 18, "div_yield": 2.5}]
    financial_unit: dict | None = None,  # {"currency": "USD", "scale": "B"} — display hint
) -> str:
    """Financial deep dive — 5y P&L, balance sheet, cash flow, peer comparison."""

    def _calc_margin(income, revenue):
        try:
            if revenue and float(revenue) != 0:
                return float(income) / float(revenue) * 100.0
        except (ValueError, TypeError):
            pass
        return 0.0

    # Determine number-format precision: if revenue<1000 use 2-dp (likely $B billions);
    # otherwise 0-dp (likely 백만 KRW or full-units). Prevents truncation like 4.5B→"4".
    _max_rev = max((float(r.get('revenue', 0) or 0) for r in pl_5y), default=0)
    _fmt_n = "{:,.2f}" if 0 < _max_rev < 1000 else "{:,.0f}"
    # Unit label for table header — uses financial_unit hint if provided, else infer
    _fu = financial_unit or {}
    _cur = _fu.get('currency') or ('USD' if 0 < _max_rev < 1000 else 'KRW')
    _scale = _fu.get('scale') or ('B' if 0 < _max_rev < 1000 else '백만')
    _unit_label = f"{_cur} {_scale}" if _scale != '백만' else f"백만 {_cur}"
    _unit_note = "B = billions; ticker별 currency/scale 자동 결정. 5Y annual P&L."
    pl_rows = "".join(
        f"""
        <tr>
          <td>{r['year']}</td>
          <td style="text-align:right;">{_fmt_n.format(float(r.get('revenue', 0) or 0))}</td>
          <td style="text-align:right;">{_fmt_n.format(float(r.get('op_income', 0) or 0))}</td>
          <td style="text-align:right;">{(r.get('op_margin') or r.get('op_margin_pct') or _calc_margin(r.get('op_income', 0), r.get('revenue', 0))):.1f}%</td>
          <td style="text-align:right;">{_fmt_n.format(float(r.get('net_income', 0) or 0))}</td>
          <td style="text-align:right;">{(r.get('net_margin') or r.get('net_margin_pct') or _calc_margin(r.get('net_income', 0), r.get('revenue', 0))):.1f}%</td>
        </tr>
        """
        for r in pl_5y
    )

    de_ratio = (bs_snapshot.get("total_liab", 0) / max(bs_snapshot.get("equity", 1), 1)) * 100
    cash_ratio = (bs_snapshot.get("cash", 0) / max(bs_snapshot.get("total_assets", 1), 1)) * 100

    def _fmt(val, dp=1, suffix=""):
        """Defensive formatter — handle None/string values gracefully."""
        if val is None or val == "" or val == "-":
            return "N/A"
        try:
            return f"{float(val):.{dp}f}{suffix}"
        except (ValueError, TypeError):
            return str(val)

    peer_rows = "".join(
        f"""
        <tr>
          <td><code>{p.get('ticker', '-')}</code> <strong>{p.get('name', '-')}</strong></td>
          <td style="text-align:right;">{_fmt(p.get('pe'), 1)}</td>
          <td style="text-align:right;">{_fmt(p.get('pb'), 2)}</td>
          <td style="text-align:right;">{_fmt(p.get('roe'), 1, '%')}</td>
          <td style="text-align:right;">{_fmt(p.get('div_yield'), 2, '%')}</td>
        </tr>
        """
        for p in peer_compare
    )

    # ── PL 5Y Trend Narrative (analytic agent) ─────────────────────
    trend_html = ""
    if len(pl_5y) >= 3:
        try:
            r_first = float(pl_5y[0]["revenue"])
            r_last = float(pl_5y[-1]["revenue"])
            n_years = len(pl_5y) - 1
            cagr_pct = (pow(r_last / r_first, 1 / n_years) - 1) * 100 if r_first > 0 else 0

            op_first = float(pl_5y[0].get("op_margin") or pl_5y[0].get("op_margin_pct") or 0)
            op_last = float(pl_5y[-1].get("op_margin") or pl_5y[-1].get("op_margin_pct") or 0)
            opm_delta = op_last - op_first

            ni_first = float(pl_5y[0].get("net_margin") or _calc_margin(pl_5y[0].get("net_income", 0), pl_5y[0].get("revenue", 0)))
            ni_last = float(pl_5y[-1].get("net_margin") or _calc_margin(pl_5y[-1].get("net_income", 0), pl_5y[-1].get("revenue", 0)))
            npm_delta = ni_last - ni_first

            # Detect turnaround (negative → positive transitions)
            negative_years = [r["year"] for r in pl_5y if (r.get("op_income") or 0) < 0]
            positive_years = [r["year"] for r in pl_5y if (r.get("op_income") or 0) > 0]
            has_turnaround = bool(negative_years) and bool(positive_years) and max(negative_years) < min(positive_years)

            # Direction labels
            rev_label = "고성장 (CAGR 15%+)" if cagr_pct > 15 else "두 자릿수 성장" if cagr_pct > 10 else "안정 성장" if cagr_pct > 3 else "정체" if cagr_pct > -3 else "축소"
            opm_label = ("개선 가속" if opm_delta > 5 else "꾸준한 개선" if opm_delta > 1 else "안정 유지" if abs(opm_delta) <= 1 else "둔화" if opm_delta > -5 else "구조적 압박")

            # Turnaround / cycle insight
            cycle_insight = ""
            if has_turnaround:
                cycle_insight = f"<strong>턴어라운드 확인</strong>: {max(negative_years)}년 적자 → {min(positive_years)}년 흑자전환. 영업이익률 {op_first:+.1f}% → {op_last:+.1f}% (+{opm_delta:.1f}pp). 사이클 회복 단계로 판단."
            elif op_last > op_first + 2:
                cycle_insight = f"<strong>이익률 확장 단계</strong>: 영업이익률 {op_first:.1f}% → {op_last:.1f}%로 {opm_delta:+.1f}pp 확장. 단순 매출 성장 이상의 operating leverage 작동."
            elif op_last < op_first - 2:
                cycle_insight = f"<strong>마진 압박 단계</strong>: 영업이익률 {op_first:.1f}% → {op_last:.1f}%로 {opm_delta:+.1f}pp 축소. cost 인플레·경쟁 격화·믹스 악화 등 점검 필요."
            else:
                cycle_insight = f"<strong>마진 안정 유지</strong>: 영업이익률 {op_first:.1f}% → {op_last:.1f}% (변동 {opm_delta:+.1f}pp). cyclical pressure 없이 base 수익성 유지."

            # Net margin vs operating margin gap (debt cost·tax efficiency proxy)
            avg_op_margin = sum(float(r.get("op_margin") or r.get("op_margin_pct") or 0) for r in pl_5y) / len(pl_5y)
            avg_np_margin = sum(float(r.get("net_margin") or _calc_margin(r.get("net_income", 0), r.get("revenue", 0))) for r in pl_5y) / len(pl_5y)
            margin_gap = avg_op_margin - avg_np_margin

            # Sprint C-2 (2026-05-28): 학습용 부연설명 + watch points 추가
            watch_points = []
            if cagr_pct >= 15:
                watch_points.append(f"🟢 매출 고성장 (+{cagr_pct:.0f}%/년) — sustainability 확인 필요 (수주잔고·CapEx 가이던스)")
            elif cagr_pct >= 5:
                watch_points.append(f"🟡 매출 안정 성장 (+{cagr_pct:.0f}%/년) — sector demand 환경 영향 큼")
            elif cagr_pct < 0:
                watch_points.append(f"🔴 매출 역성장 ({cagr_pct:+.0f}%/년) — cyclic? structural decline? 구분 필요")
            if opm_delta >= 5:
                watch_points.append(f"🟢 OPM 개선 가속 ({opm_delta:+.1f}pp) — operating leverage 발휘, 추가 margin 확장 여력 점검")
            elif opm_delta <= -5:
                watch_points.append(f"🔴 OPM 악화 ({opm_delta:+.1f}pp) — 원자재 cost-push? 가격경쟁? 환율 손실? 원인 분해 필요")
            if margin_gap > 8:
                watch_points.append(f"🟡 OP→NP gap {margin_gap:.0f}pp 큼 — 이자비용·세금·환차익 등 비영업 손익 영향. 부채 비중 점검 권장")
            if op_last > 30:
                watch_points.append(f"🟢 OPM {op_last:.0f}% — 매우 높은 수익성 (typical mid-cycle 12~18%). cycle peak 가능성 점검")

            watch_html = ""
            if watch_points:
                watch_html = (
                    '<div style="margin-top:8pt;padding:10pt 14pt;background:#fefce8;'
                    'border-left:3pt solid #ca8a04;border-radius:0 4pt 4pt 0;">'
                    '<strong style="color:#92400e;font-size:10.5pt;">👀 Watch Points (향후 1~2년):</strong>'
                    '<ul style="margin:4pt 0 0 18pt;font-size:10pt;line-height:1.6;">'
                    + "".join(f"<li>{wp}</li>" for wp in watch_points) +
                    '</ul></div>'
                )

            education_html = (
                '<div style="margin-top:8pt;padding:10pt 14pt;background:#f0f9ff;'
                'border-left:3pt solid #0284c7;border-radius:0 4pt 4pt 0;font-size:10pt;line-height:1.6;">'
                '<strong style="color:#0c4a6e;font-size:10.5pt;">📚 추세 지표 해석 가이드 (학습용):</strong>'
                '<ul style="margin:4pt 0 0 18pt;">'
                '<li><strong>매출 CAGR (연평균 성장률)</strong>: 5년치 매출의 기하평균 성장률. '
                '<em>15%+는 성장주, 5~10%는 안정주, 0% 부근은 성숙·전환기, 음수는 cyclic trough 또는 structural decline 의심.</em></li>'
                '<li><strong>OPM (Operating Profit Margin)</strong>: 매출 대비 영업이익. '
                '<em>업종 평균을 알아야 함 — Tech 25%+, 산업재 10~15%, 유틸리티 12~18%, 에너지 cyclic 5~25%. '
                '추세(trajectory)가 절대값보다 중요 — 5pp 개선은 operating leverage 또는 가격 인상 효과.</em></li>'
                '<li><strong>NPM (Net Profit Margin)</strong>: 매출 대비 당기순이익. '
                '<em>OPM과의 gap이 8pp 이상이면 이자비용·세금·환차익 등 비영업 손익이 큰 영향 — leveraged 기업 신호.</em></li>'
                '<li><strong>OP→NP gap</strong>: OPM과 NPM의 차이. <em>저금리에서 좁아지고 긴축에서 확대 — '
                'Fed funds 변화에 민감한 기업 식별 가능.</em></li>'
                '</ul></div>'
            )

            trend_html = f"""
            <h4 style="margin-top:8pt;">📈 추세 분석 (Analytic Agent)</h4>
            <table class="dt">
              <tr><th style="width:18%">매출 CAGR ({n_years}년)</th><td><strong>{cagr_pct:+.1f}%</strong> — {rev_label}</td></tr>
              <tr><th>OPM 변화</th><td>{op_first:+.1f}% → {op_last:+.1f}% (<strong>{opm_delta:+.1f}pp</strong>) — {opm_label}</td></tr>
              <tr><th>NPM 변화</th><td>{ni_first:+.1f}% → {ni_last:+.1f}% (<strong>{npm_delta:+.1f}pp</strong>)</td></tr>
              <tr><th>OP→NP gap</th><td>평균 {margin_gap:.1f}pp (이자비용·세금·기타 손익 합산) — {'재무비용 부담 큼' if margin_gap > 5 else '효율적 비용 구조' if margin_gap < 2 else '정상 범위'}</td></tr>
            </table>
            <p style="font-size:10pt;line-height:1.6;background:#f0f9ff;padding:10pt 14pt;border-left:3pt solid #0ea5e9;margin-top:6pt;">
              <strong>종합 해석</strong>: {cycle_insight}
            </p>
            {watch_html}
            {education_html}
            <p style="font-size:9pt;color:#6b7280;">위 narrative는 analytic agent가 PL 5Y 수치로부터 CAGR·margin trajectory·turnaround signal·op/np gap을 자동 계산하여 생성. 외부 LLM 호출 없음 (deterministic).</p>
            """
        except Exception as e:
            trend_html = f"<p style='font-size:9pt;color:#dc2626;'>Trend 분석 실패: {e}</p>"

    return f"""
    <h2>💰 재무 심층 분석 (Financial Deep Dive)</h2>

    <h3>5년 손익 추이 ({_unit_label})</h3>
    <table class="dt">
      <thead><tr><th>연도</th><th>매출 ({_unit_label})</th><th>영업이익 ({_unit_label})</th><th>OPM</th><th>순이익 ({_unit_label})</th><th>NPM</th></tr></thead>
      <tbody>{pl_rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;">단위: {_unit_label}. {_unit_note}</p>

    {trend_html}

    <h3>대차대조표 스냅샷 ({_unit_label})</h3>
    <table class="dt">
      <tr><th>총자산</th><td>{_fmt_n.format(float(bs_snapshot.get('total_assets', 0) or 0))}</td>
          <th>총부채</th><td>{_fmt_n.format(float(bs_snapshot.get('total_liab', 0) or 0))}</td></tr>
      <tr><th>자본</th><td>{_fmt_n.format(float(bs_snapshot.get('equity', 0) or 0))}</td>
          <th>현금</th><td>{_fmt_n.format(float(bs_snapshot.get('cash', 0) or 0))}</td></tr>
      <tr><th>총차입금</th><td>{_fmt_n.format(float(bs_snapshot.get('debt', 0) or 0))}</td>
          <th>D/E 비율</th><td><strong>{de_ratio:.1f}%</strong></td></tr>
      <tr><th>현금/자산</th><td>{cash_ratio:.1f}%</td>
          <th>순현금</th><td>{_fmt_n.format(float((bs_snapshot.get('cash', 0) or 0) - (bs_snapshot.get('debt', 0) or 0)))}</td></tr>
    </table>
    {('<p style="font-size:9pt;color:#6b7280;">' + bs_snapshot.get('_note','') + '</p>') if bs_snapshot.get('_note') else ''}

    <h3>현금흐름 요약 (5년 평균)</h3>
    <table class="dt">
      <tr><th>OCF (영업현금흐름)</th><td>{cf_summary.get('ocf_5y_avg', 0):,.0f}</td>
          <th>FCF (잉여현금흐름)</th><td>{cf_summary.get('fcf_5y_avg', 0):,.0f}</td></tr>
      <tr><th>CapEx 강도</th><td>{cf_summary.get('capex_intensity', 0)*100:.1f}% (매출 대비)</th>
          <th>FCF 전환율</th><td>{(cf_summary.get('fcf_5y_avg', 0) / max(cf_summary.get('ocf_5y_avg', 1), 1)) * 100:.1f}%</td></tr>
    </table>

    <h3>피어 비교 (Peer Comparison)</h3>
    <table class="dt">
      <thead><tr><th>종목</th><th>PE</th><th>PB</th><th>ROE</th><th>배당수익률</th></tr></thead>
      <tbody>{peer_rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;">
      <strong>해석</strong>: 동종업계 대비 PE 낮을수록 저평가 가능성. 단 cyclical 업종은 EPS peak
      신호로도 해석 가능 — Burry는 'PE는 함정', Buffett은 'ROE × 자본효율'을 더 중시.
    </p>
    """


# ── Risk Factor Matrix ─────────────────────────────────────────────────
def render_risk_matrix(risks: list[dict]) -> str:
    """Risk factor matrix (probability × impact).

    risks: [{"name": "...", "probability": "high|med|low",
             "impact": "high|med|low", "description": "...",
             "mitigation": "..."}]
    """
    color_map = {
        ("high", "high"): "#dc2626",   # red
        ("high", "med"): "#f59e0b",    # orange
        ("high", "low"): "#fbbf24",    # yellow
        ("med", "high"): "#f59e0b",
        ("med", "med"): "#fbbf24",
        ("med", "low"): "#a3e635",     # lime
        ("low", "high"): "#fbbf24",
        ("low", "med"): "#a3e635",
        ("low", "low"): "#10b981",     # green
    }
    label_map = {"high": "高", "med": "中", "low": "低"}

    # ── Defensive normalize — accept both schemas ─────────────────────────
    # Schema A (canonical): {name, probability(high/med/low), impact, description, mitigation}
    # Schema B (Korean DART): {risk, p(高/中/低), i(高/中/低), mitigation}
    kor_pi = {"高": "high", "中": "med", "低": "low",
              "high": "high", "med": "med", "low": "low",
              "med.": "med", "medium": "med"}

    rows = ""
    for r in risks:
        name = r.get("name") or r.get("risk") or r.get("title") or "(unnamed)"
        p_raw = r.get("probability") or r.get("p") or "med"
        i_raw = r.get("impact") or r.get("i") or "med"
        p = kor_pi.get(str(p_raw).strip(), "med")
        i = kor_pi.get(str(i_raw).strip(), "med")
        color = color_map.get((p, i), "#9ca3af")
        rows += f"""
        <tr>
          <td><strong>{name}</strong></td>
          <td style="text-align:center;background:{color};color:white;">
            <strong>{label_map[p]} × {label_map[i]}</strong>
          </td>
          <td style="font-size:9pt;">{r.get('description', '')}</td>
          <td style="font-size:9pt;">{r.get('mitigation', '-')}</td>
        </tr>
        """

    return f"""
    <h2>⚠️ 리스크 매트릭스 (Risk Factor Matrix)</h2>
    <div class="info">발생 확률(probability) × 영향도(impact) 격자로 정리. 색상이 진할수록 우선 모니터링 대상.</div>
    <table class="dt">
      <thead><tr>
        <th style="width:22%">리스크</th>
        <th style="width:14%">P × I</th>
        <th>설명</th>
        <th style="width:25%">완화 방안</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


# ── Catalyst Timeline ────────────────────────────────────────────────────
def render_catalyst_timeline(catalysts: list[dict]) -> str:
    """Upcoming catalysts in timeline form.

    catalysts: [{"date": "2026-Q2", "event": "...", "type": "earnings|policy|product|m&a",
                 "expected_impact": "+", "description": "..."}]
    """
    type_emoji = {
        "earnings": "💼",
        "policy": "🏛️",
        "product": "🚀",
        "m&a": "🤝",
        "regulatory": "⚖️",
        "macro": "🌍",
    }

    rows = ""
    for c in catalysts:
        emoji = type_emoji.get(c.get("type", ""), "📌")
        impact = c.get("expected_impact") or c.get("impact") or "?"
        impact_color = "#10b981" if impact == "+" else "#dc2626" if impact == "-" else "#6b7280"
        date = c.get("date") or c.get("when") or "TBD"
        event = c.get("event") or c.get("name") or c.get("title") or "(unnamed)"
        rows += f"""
        <tr>
          <td style="white-space:nowrap;"><strong>{date}</strong></td>
          <td>{emoji} {event}</td>
          <td style="text-align:center;color:{impact_color};font-weight:bold;">{impact}</td>
          <td style="font-size:9pt;">{c.get('description', '')}</td>
        </tr>
        """

    return f"""
    <h2>📅 카탈리스트 타임라인 (Catalyst Timeline)</h2>
    <div class="info">향후 6-12개월간 주가에 영향을 줄 가능성이 큰 예정 이벤트. + 는 상승 촉매, - 는 하락 위험.</div>
    <table class="dt">
      <thead><tr>
        <th style="width:14%">시점</th>
        <th style="width:30%">이벤트</th>
        <th style="width:8%">방향</th>
        <th>설명</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


# ── Bull / Base / Bear Scenario Table ──────────────────────────────────
def render_scenarios(
    bull: dict, base: dict, bear: dict, current_price: float, currency: str = "KRW"
) -> str:
    """Bull/Base/Bear scenarios with probability-weighted price targets.

    each: {"prob_pct": 30, "target_price": 100, "thesis": "...",
           "key_assumptions": ["...", "..."]}
    """
    _has_targets = all(
        isinstance(s.get("target_price"), (int, float)) for s in (bull, base, bear)
    )

    # ── Defensive: accept both prob_pct (0~100) and probability (0~1) keys ──
    def _prob_pct(sc: dict) -> float:
        if isinstance(sc.get("prob_pct"), (int, float)):
            return float(sc["prob_pct"])
        if isinstance(sc.get("probability"), (int, float)):
            p = float(sc["probability"])
            return p * 100 if p <= 1.0 else p
        return 0.0
    for _s in (bull, base, bear):
        _s["prob_pct"] = _prob_pct(_s)

    if _has_targets:
        expected = (
            bull["prob_pct"] * bull["target_price"]
            + base["prob_pct"] * base["target_price"]
            + bear["prob_pct"] * bear["target_price"]
        ) / 100.0
        upside_expected = (expected / current_price - 1) * 100 if current_price else 0
        _ev_html = f"""3가지 시나리오의 확률 가중 기대 주가: <strong>{format_price(expected, currency)}</strong>
    (현재가 {current_price:,.0f} 대비 <strong style="color:{'#10b981' if upside_expected>=0 else '#dc2626'};">
    {'+' if upside_expected>=0 else ''}{upside_expected:.1f}%</strong>)."""
    else:
        _ev_html = ("정성 시나리오 — 목표주가는 검증 가능한 밸류에이션 모델 부재로 미산정 "
                    "(추측성 목표가 생성 금지 원칙). 확률·논거·핵심 가정 중심으로 해석.")

    def _row(name: str, color: str, sc: dict) -> str:
        tp = sc.get("target_price")
        if isinstance(tp, (int, float)):
            upside = (tp / current_price - 1) * 100 if current_price else 0
            tp_html = (f"<strong>{format_price(tp, currency)}</strong><br/>"
                       f"<span style=\"color:{'#10b981' if upside>=0 else '#dc2626'};font-size:9pt;\">"
                       f"{'+' if upside>=0 else ''}{upside:.1f}%</span>")
        else:
            tp_html = "<span style=\"font-size:9pt;color:#6b7280;\">미산정</span>"
        assumptions = "".join(f"<li>{a}</li>" for a in sc.get("key_assumptions", []))
        return f"""
        <tr>
          <td style="background:{color};color:white;text-align:center;font-weight:bold;width:10%;">{name}</td>
          <td style="text-align:center;width:10%;"><strong>{sc['prob_pct']}%</strong></td>
          <td style="text-align:right;width:14%;">{tp_html}</td>
          <td style="font-size:9pt;">{sc.get('thesis', '')}<br/>
              <strong style="font-size:8.5pt;">핵심 가정</strong>:
              <ul style="margin:2pt 0 0 12pt;padding:0;font-size:8.5pt;">{assumptions}</ul></td>
        </tr>
        """

    return f"""
    <h2>🎯 시나리오 분석 (Bull / Base / Bear)</h2>
    <div class="info">{_ev_html}</div>
    <table class="dt">
      <thead><tr>
        <th>시나리오</th><th>확률</th><th>목표주가</th><th>논거 및 핵심 가정</th>
      </tr></thead>
      <tbody>
        {_row("🟢 Bull", "#10b981", bull)}
        {_row("🟡 Base", "#f59e0b", base)}
        {_row("🔴 Bear", "#dc2626", bear)}
      </tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;margin-top:6pt;">
      <strong>방법론</strong>: Bull/Base/Bear는 각각 매출·이익·multiple 가정을 다르게 두고 계산.
      확률 가중 기대치는 portfolio decision의 expected return 계산에 직접 사용됨.
    </p>
    """


# ── Thesis Decomposition ───────────────────────────────────────────────
def _derive_status_from_evaluations(evaluations: dict) -> tuple[str, str]:
    """4-analyst stance 집계 → (status, summary).

    Rules:
      - 3+ support → confirmed
      - 3+ challenge/rebut → invalidated
      - 2 support + 2 oppose → contested (rendered as pending with note)
      - else → pending
    """
    if not evaluations or not isinstance(evaluations, dict):
        return ("pending", "")
    stances = []
    for analyst_id in ("macro", "industry", "empirical", "counter"):
        e = evaluations.get(analyst_id) or evaluations.get(analyst_id.title())
        if e and isinstance(e, dict):
            stances.append(str(e.get("stance", "")).lower().strip())
    if not stances:
        return ("pending", "")
    support = sum(1 for s in stances if s in ("support", "agree", "supports"))
    challenge = sum(1 for s in stances if s in ("challenge", "rebut", "rebuts", "oppose", "opposes"))
    neutral = len(stances) - support - challenge
    summary = f"{support}지지·{neutral}중립·{challenge}반박 (of {len(stances)})"
    if support >= 3:
        return ("confirmed", summary)
    if challenge >= 3:
        return ("invalidated", summary)
    return ("pending", summary)


def _short_rationale(evaluations: dict, max_len: int = 240) -> str:
    """4-analyst rationale을 짧은 multi-line summary로 변환."""
    if not evaluations or not isinstance(evaluations, dict):
        return "-"
    lines = []
    analyst_label = {
        "macro": "🌍 거시", "industry": "🏭 산업",
        "empirical": "📊 정량", "counter": "⚖️ 반박"
    }
    for aid in ("macro", "industry", "empirical", "counter"):
        e = evaluations.get(aid) or evaluations.get(aid.title())
        if not e or not isinstance(e, dict):
            continue
        stance = str(e.get("stance", "?")).lower()
        conf = e.get("confidence")
        stance_emoji = {"support": "✅", "challenge": "❌", "rebut": "❌",
                         "neutral": "◯", "supports": "✅", "opposes": "❌"}.get(stance, "◯")
        rationale = (e.get("rationale") or "")[:max_len].strip()
        conf_str = f" ({conf:.2f})" if isinstance(conf, (int, float)) else ""
        label = analyst_label.get(aid, aid)
        lines.append(f"<li><strong>{label}{conf_str}</strong> {stance_emoji} {rationale}</li>")
    if not lines:
        return "-"
    return f'<ul style="margin:2pt 0 0 0;padding-left:14pt;font-size:8.5pt;">{"".join(lines)}</ul>'


def render_thesis_decomposition(theses: list[dict], thesis_eval: dict | None = None) -> str:
    """Blogger's thesis broken down into testable claims, with 4-analyst evaluation overlay.

    theses: [{"claim": "...", "type": "macro|industry|company|policy",
              "evidence": "...", "testability": "high|med|low",
              "current_status": "confirmed|pending|invalidated"}]
    thesis_eval: dict from thesis_eval/all_aggregate.json
                 — {aggregates: [{claim_id, claim, evaluations: {macro, industry, empirical, counter}}]}
                 — used to overlay status/rationale per thesis (matched by claim_id or claim substring).
    """
    type_emoji = {
        "macro": "🌍",
        "industry": "🏭",
        "company": "🏢",
        "policy": "🏛️",
    }
    status_color = {
        "confirmed": "#10b981",
        "pending": "#f59e0b",
        "invalidated": "#dc2626",
    }
    status_label = {
        "confirmed": "검증됨",
        "pending": "검증 중",
        "invalidated": "반증됨",
    }

    # ── Build claim_id → evaluations map from thesis_eval ──
    eval_map_by_id = {}
    eval_map_by_text = {}  # fallback: substring match
    if thesis_eval and isinstance(thesis_eval, dict):
        agg = thesis_eval.get("aggregates") or thesis_eval.get("evaluations") or []
        if isinstance(agg, list):
            for entry in agg:
                if not isinstance(entry, dict):
                    continue
                cid = entry.get("claim_id")
                evals = entry.get("evaluations") or entry.get("analyst_evaluations") or {}
                if cid:
                    eval_map_by_id[cid] = evals
                claim_txt = entry.get("claim") or entry.get("text") or ""
                if claim_txt:
                    eval_map_by_text[claim_txt[:50]] = evals

    rows = ""
    for idx, t in enumerate(theses):
        emoji = type_emoji.get(t.get("type", ""), "📋")
        # Defensive: 'claim', 'thesis_short', 'text', 'description' 순으로 fallback
        claim_text = (
            t.get("claim") or t.get("thesis_short") or
            t.get("text") or t.get("description") or "(no claim text)"
        )

        # ── Match this thesis to evaluations ─────────────────
        # Try claim_id (T1, T2, ...) → ordinal index → substring match
        cid = t.get("claim_id") or t.get("id") or f"T{idx+1}"
        evaluations = eval_map_by_id.get(cid) or {}
        if not evaluations:
            # Substring match (first 50 chars)
            for key, ev in eval_map_by_text.items():
                if key in claim_text or claim_text[:50] in key:
                    evaluations = ev
                    break

        status, status_note = _derive_status_from_evaluations(evaluations)
        # Allow explicit current_status override
        status = t.get("current_status", status)
        rationale_html = _short_rationale(evaluations) if evaluations else (
            t.get('evidence', '-') or '-'
        )

        # Status cell — include 지지·중립·반박 breakdown if available
        status_cell = status_label.get(status, status)
        if status_note:
            status_cell += f'<br/><span style="font-size:7.5pt;font-weight:normal;">{status_note}</span>'

        weight = t.get("weight")
        weight_html = f'<br/><span style="font-size:7.5pt;color:#6b7280;">w={weight}</span>' if weight else ''

        rows += f"""
        <tr>
          <td>{emoji}<br/><span style="font-size:8pt;color:#6b7280;">{t.get('type', '-')}</span>{weight_html}</td>
          <td><strong>{claim_text}</strong></td>
          <td style="font-size:9pt;">{rationale_html}</td>
          <td style="text-align:center;">{(t.get('testability') or '-').upper()}</td>
          <td style="text-align:center;background:{status_color.get(status, '#9ca3af')};color:white;font-weight:bold;font-size:9pt;">
            {status_cell}
          </td>
        </tr>
        """

    return f"""
    <h2>🧩 테제 분해 (Thesis Decomposition × 4-Analyst Lens)</h2>
    <div class="info">블로거의 핵심 주장을 검증 가능한 단위로 분해 + 4명의 analyst(거시·산업·정량·반박)가 독립적으로 평가한 결과 overlay.
    각 thesis가 깨지면 verdict가 변화함을 추적 가능 — 이는 우리 시스템의 'thesis-aware' 설계의 핵심.</div>
    <table class="dt">
      <thead><tr>
        <th style="width:10%">유형</th>
        <th style="width:24%">주장 (Claim)</th>
        <th>4-Analyst 평가 근거 (Evidence)</th>
        <th style="width:8%">검증성</th>
        <th style="width:14%">현재 상태</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """


# ── ESG / Korean-specific (DART/KIND) ──────────────────────────────────
def render_korean_disclosure_check(ticker: str, items: list[dict]) -> str:
    """For Korean tickers: recent DART/KIND disclosures.

    items: [{"date": "...", "type": "주요사항|주식관련사채|임원변동", "title": "...", "impact": "..."}]
    """
    if not items:
        return ""

    rows = "".join(
        f"""
        <tr>
          <td style="white-space:nowrap;font-size:8.5pt;">{i['date']}</td>
          <td><span class="tag-actual">{i['type']}</span></td>
          <td>{i['title']}</td>
          <td style="font-size:9pt;">{i.get('impact', '-')}</td>
        </tr>
        """
        for i in items
    )

    return f"""
    <h2>📑 한국 공시 점검 ({ticker})</h2>
    <div class="info">DART (전자공시) 및 KIND (한국거래소 공시) 최근 6개월 내 주요사항.</div>
    <table class="dt">
      <thead><tr>
        <th style="width:12%">날짜</th>
        <th style="width:14%">유형</th>
        <th>제목</th>
        <th style="width:24%">영향 (잠정)</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """
