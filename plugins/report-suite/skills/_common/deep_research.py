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
        market_size_html = f"""
        <div class="info" style="margin-top:8pt;">
          <strong>시장 규모</strong>: 현재 ${market_size['current_usd_bn']:.1f}B
          → {market_size['horizon']} CAGR <strong>{market_size['cagr_pct']:.1f}%</strong>
        </div>
        """

    competitors_rows = "".join(
        f"""
        <tr>
          <td><strong>{c['name']}</strong> <code>{c.get('ticker', '-')}</code></td>
          <td style="text-align:center;">{c.get('share_pct', 0):.1f}%</td>
          <td>{c.get('moat', '-')}</td>
        </tr>
        """
        for c in competitive_landscape
    )

    news_rows = "".join(
        f"""
        <tr>
          <td style="white-space:nowrap;font-size:8.5pt;">{n['date']}</td>
          <td><strong>{n['title']}</strong><br/>
              <span style="font-size:8.5pt;color:#6b7280;">{n.get('summary', '')} <em>({n.get('source', '-')})</em></span></td>
        </tr>
        """
        for n in recent_news
    )

    return f"""
    <h2>🌐 산업 맥락 (Industry Context)</h2>
    <h3>{industry} 개요</h3>
    <p>{overview}</p>
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
) -> str:
    """Financial deep dive — 5y P&L, balance sheet, cash flow, peer comparison."""

    def _calc_margin(income, revenue):
        try:
            if revenue and float(revenue) != 0:
                return float(income) / float(revenue) * 100.0
        except (ValueError, TypeError):
            pass
        return 0.0

    pl_rows = "".join(
        f"""
        <tr>
          <td>{r['year']}</td>
          <td style="text-align:right;">{r['revenue']:,.0f}</td>
          <td style="text-align:right;">{r.get('op_income', 0):,.0f}</td>
          <td style="text-align:right;">{(r.get('op_margin') or r.get('op_margin_pct') or _calc_margin(r.get('op_income', 0), r.get('revenue', 0))):.1f}%</td>
          <td style="text-align:right;">{r.get('net_income', 0):,.0f}</td>
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

            trend_html = f"""
            <h4 style="margin-top:8pt;">📈 추세 분석 (Analytic Agent)</h4>
            <table class="dt">
              <tr><th style="width:18%">매출 CAGR ({n_years}년)</th><td><strong>{cagr_pct:+.1f}%</strong> — {rev_label}</td></tr>
              <tr><th>OPM 변화</th><td>{op_first:+.1f}% → {op_last:+.1f}% (<strong>{opm_delta:+.1f}pp</strong>) — {opm_label}</td></tr>
              <tr><th>NPM 변화</th><td>{ni_first:+.1f}% → {ni_last:+.1f}% (<strong>{npm_delta:+.1f}pp</strong>)</td></tr>
              <tr><th>OP→NP gap</th><td>평균 {margin_gap:.1f}pp (이자비용·세금·기타 손익 합산) — {'재무비용 부담 큼' if margin_gap > 5 else '효율적 비용 구조' if margin_gap < 2 else '정상 범위'}</td></tr>
            </table>
            <p style="font-size:10pt;line-height:1.6;background:#f0f9ff;padding:10pt 14pt;border-left:3pt solid #0ea5e9;margin-top:6pt;">
              <strong>해석</strong>: {cycle_insight}
            </p>
            <p style="font-size:9pt;color:#6b7280;">위 narrative는 analytic agent가 PL 5Y 수치로부터 CAGR·margin trajectory·turnaround signal·op/np gap을 자동 계산하여 생성. 외부 LLM 호출 없음 (deterministic).</p>
            """
        except Exception as e:
            trend_html = f"<p style='font-size:9pt;color:#dc2626;'>Trend 분석 실패: {e}</p>"

    return f"""
    <h2>💰 재무 심층 분석 (Financial Deep Dive)</h2>

    <h3>5년 손익 추이</h3>
    <table class="dt">
      <thead><tr><th>연도</th><th>매출</th><th>영업이익</th><th>OPM</th><th>순이익</th><th>NPM</th></tr></thead>
      <tbody>{pl_rows}</tbody>
    </table>
    <p style="font-size:9pt;color:#6b7280;">단위: 십억 원 (KRW) 또는 백만 달러 (USD), 통화는 ticker별 자동 결정.</p>

    {trend_html}

    <h3>대차대조표 스냅샷</h3>
    <table class="dt">
      <tr><th>총자산</th><td>{bs_snapshot.get('total_assets', 0):,.0f}</td>
          <th>총부채</th><td>{bs_snapshot.get('total_liab', 0):,.0f}</td></tr>
      <tr><th>자본</th><td>{bs_snapshot.get('equity', 0):,.0f}</td>
          <th>현금</th><td>{bs_snapshot.get('cash', 0):,.0f}</td></tr>
      <tr><th>총차입금</th><td>{bs_snapshot.get('debt', 0):,.0f}</td>
          <th>D/E 비율</th><td><strong>{de_ratio:.1f}%</strong></td></tr>
      <tr><th>현금/자산</th><td>{cash_ratio:.1f}%</td>
          <th>순현금</th><td>{bs_snapshot.get('cash', 0) - bs_snapshot.get('debt', 0):,.0f}</td></tr>
    </table>

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

    rows = ""
    for r in risks:
        p = r.get("probability", "med")
        i = r.get("impact", "med")
        color = color_map.get((p, i), "#9ca3af")
        rows += f"""
        <tr>
          <td><strong>{r['name']}</strong></td>
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
        impact = c.get("expected_impact", "?")
        impact_color = "#10b981" if impact == "+" else "#dc2626" if impact == "-" else "#6b7280"
        rows += f"""
        <tr>
          <td style="white-space:nowrap;"><strong>{c['date']}</strong></td>
          <td>{emoji} {c['event']}</td>
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
    expected = (
        bull["prob_pct"] * bull["target_price"]
        + base["prob_pct"] * base["target_price"]
        + bear["prob_pct"] * bear["target_price"]
    ) / 100.0

    upside_expected = (expected / current_price - 1) * 100 if current_price else 0

    def _row(name: str, color: str, sc: dict) -> str:
        upside = (sc["target_price"] / current_price - 1) * 100 if current_price else 0
        assumptions = "".join(f"<li>{a}</li>" for a in sc.get("key_assumptions", []))
        return f"""
        <tr>
          <td style="background:{color};color:white;text-align:center;font-weight:bold;width:10%;">{name}</td>
          <td style="text-align:center;width:10%;"><strong>{sc['prob_pct']}%</strong></td>
          <td style="text-align:right;width:14%;"><strong>{format_price(sc['target_price'], currency)}</strong><br/>
              <span style="color:{'#10b981' if upside>=0 else '#dc2626'};font-size:9pt;">
              {'+' if upside>=0 else ''}{upside:.1f}%</span></td>
          <td style="font-size:9pt;">{sc.get('thesis', '')}<br/>
              <strong style="font-size:8.5pt;">핵심 가정</strong>:
              <ul style="margin:2pt 0 0 12pt;padding:0;font-size:8.5pt;">{assumptions}</ul></td>
        </tr>
        """

    return f"""
    <h2>🎯 시나리오 분석 (Bull / Base / Bear)</h2>
    <div class="info">3가지 시나리오의 확률 가중 기대 주가: <strong>{format_price(expected, currency)}</strong>
    (현재가 {current_price:,.0f} 대비 <strong style="color:{'#10b981' if upside_expected>=0 else '#dc2626'};">
    {'+' if upside_expected>=0 else ''}{upside_expected:.1f}%</strong>).</div>
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
def render_thesis_decomposition(theses: list[dict]) -> str:
    """Blogger's thesis broken down into testable claims.

    theses: [{"claim": "...", "type": "macro|industry|company|policy",
              "evidence": "...", "testability": "high|med|low",
              "current_status": "confirmed|pending|invalidated"}]
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

    rows = ""
    for t in theses:
        emoji = type_emoji.get(t.get("type", ""), "📋")
        status = t.get("current_status", "pending")
        rows += f"""
        <tr>
          <td>{emoji}<br/><span style="font-size:8pt;color:#6b7280;">{t.get('type', '-')}</span></td>
          <td><strong>{t['claim']}</strong></td>
          <td style="font-size:9pt;">{t.get('evidence', '-')}</td>
          <td style="text-align:center;">{t.get('testability', '-').upper()}</td>
          <td style="text-align:center;background:{status_color.get(status, '#9ca3af')};color:white;font-weight:bold;">
            {status_label.get(status, status)}
          </td>
        </tr>
        """

    return f"""
    <h2>🧩 테제 분해 (Thesis Decomposition)</h2>
    <div class="info">블로거의 핵심 주장을 검증 가능한 단위로 분해. 각 thesis가 깨지면 verdict가 변화함을
    추적 가능 — 이는 우리 시스템의 'thesis-aware' 설계의 핵심.</div>
    <table class="dt">
      <thead><tr>
        <th style="width:12%">유형</th>
        <th style="width:30%">주장 (Claim)</th>
        <th>근거 (Evidence)</th>
        <th style="width:10%">검증성</th>
        <th style="width:12%">현재 상태</th>
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
