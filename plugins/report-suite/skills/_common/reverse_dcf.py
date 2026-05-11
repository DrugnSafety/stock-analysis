"""Reverse DCF — Damodaran 스타일 implied growth 자동 산출.

Approach:
  Current Market Cap = PV of future Free Cash Flows
  → Solve for implied perpetual growth (g) given assumptions on:
    - WACC (discount rate)
    - Operating margin
    - Reinvestment rate
    - Tax rate

  Then compare implied g vs consensus g → "시장은 더 낙관적/비관적이다"
"""
from __future__ import annotations


def reverse_dcf(market_cap_bn: float, revenue_bn: float, wacc: float = 0.10,
                operating_margin: float = 0.10, tax_rate: float = 0.22,
                reinvestment_rate: float = 0.30, terminal_g: float = 0.025) -> dict:
    """Solve for implied 5-year growth that justifies current market cap.

    Simplified 5-year DCF + terminal value model:
      FCF_t = Revenue_t × OpMargin × (1 - Tax) × (1 - Reinvest)
      Terminal = FCF_5 × (1 + g_term) / (WACC - g_term)
      Market Cap = sum(FCF_t / (1+WACC)^t) + Terminal / (1+WACC)^5

    Returns: dict with implied_growth_5y, implied_growth_year, scenarios.
    """
    # Binary search for implied 5y CAGR
    lo, hi = -0.20, 0.50
    for _ in range(60):
        mid = (lo + hi) / 2
        # Project revenue
        rev = revenue_bn
        pv = 0.0
        for t in range(1, 6):
            rev *= (1 + mid)
            fcf = rev * operating_margin * (1 - tax_rate) * (1 - reinvestment_rate)
            pv += fcf / (1 + wacc) ** t
        # Terminal value at year 5
        rev_5 = revenue_bn * (1 + mid) ** 5
        fcf_5 = rev_5 * operating_margin * (1 - tax_rate) * (1 - reinvestment_rate)
        terminal = fcf_5 * (1 + terminal_g) / (wacc - terminal_g)
        pv += terminal / (1 + wacc) ** 5

        if pv < market_cap_bn:
            lo = mid
        else:
            hi = mid

    implied_5y = (lo + hi) / 2

    # Scenario sensitivity (vary OPM ±2pp, WACC ±1pp)
    scenarios = []
    for opm_delta, wacc_delta, label in [
        (-0.02, +0.01, "Bear (낮은 OPM + 높은 WACC)"),
        (0.0, 0.0, "Base (현재 가정)"),
        (+0.02, -0.01, "Bull (높은 OPM + 낮은 WACC)"),
    ]:
        s_opm = operating_margin + opm_delta
        s_wacc = wacc + wacc_delta
        s_lo, s_hi = -0.30, 0.60
        for _ in range(40):
            s_mid = (s_lo + s_hi) / 2
            rev_s = revenue_bn
            pv_s = 0.0
            for t in range(1, 6):
                rev_s *= (1 + s_mid)
                fcf_s = rev_s * s_opm * (1 - tax_rate) * (1 - reinvestment_rate)
                pv_s += fcf_s / (1 + s_wacc) ** t
            rev_s5 = revenue_bn * (1 + s_mid) ** 5
            fcf_s5 = rev_s5 * s_opm * (1 - tax_rate) * (1 - reinvestment_rate)
            term = fcf_s5 * (1 + terminal_g) / max(s_wacc - terminal_g, 0.001)
            pv_s += term / (1 + s_wacc) ** 5
            if pv_s < market_cap_bn:
                s_lo = s_mid
            else:
                s_hi = s_mid
        scenarios.append({"label": label, "implied_g": (s_lo + s_hi) / 2,
                          "opm": s_opm, "wacc": s_wacc})

    return {
        "market_cap_bn": market_cap_bn,
        "revenue_bn": revenue_bn,
        "wacc": wacc,
        "operating_margin": operating_margin,
        "implied_growth_5y_cagr": implied_5y,
        "scenarios": scenarios,
    }


def render_reverse_dcf(ticker: str, dcf: dict, consensus_growth: float = 0.10,
                        currency: str = "USD") -> str:
    """Reverse DCF 결과 → HTML 섹션."""
    implied = dcf["implied_growth_5y_cagr"]
    consensus = consensus_growth
    gap = implied - consensus

    if gap > 0.03:
        verdict = ("🔴 시장은 매우 낙관적", "현재 주가는 컨센서스보다 +{:.1f}%p 더 높은 성장을 가격화. 컨센서스를 신뢰하면 비싸 보임.".format(gap*100))
    elif gap > 0.0:
        verdict = ("🟡 시장은 약간 낙관적", "현재 주가는 컨센서스 +{:.1f}%p 더 높은 성장을 요구. 약간 fair-to-overvalued.".format(gap*100))
    elif gap > -0.03:
        verdict = ("🟢 적정 수준 (Fair)", "implied growth가 consensus와 근접. 컨센 신뢰 시 fair priced.")
    else:
        verdict = ("🟢 매우 매력적 (저평가 가능)", "현재 주가는 컨센서스보다 {:.1f}%p 낮은 성장만 가격화. 컨센 신뢰 시 저평가 가능.".format(abs(gap*100)))

    scenario_rows = "".join(
        f"""<tr>
              <td><strong>{s['label']}</strong></td>
              <td style="text-align:center;">OPM {s['opm']*100:.1f}% / WACC {s['wacc']*100:.1f}%</td>
              <td style="text-align:right;font-weight:bold;color:{'#dc2626' if s['implied_g']>0.15 else '#16a34a' if s['implied_g']<0.05 else '#ca8a04'};">
                {s['implied_g']*100:.1f}%
              </td>
            </tr>"""
        for s in dcf["scenarios"]
    )

    return f"""
    <h2>📐 Reverse DCF — Damodaran 스타일 implied growth 산출</h2>
    <div class="info">
      <strong>"현재 주가는 미래 성장률이 얼마라고 시장이 가정하는가?"</strong><br/>
      현재 시가총액에서 거꾸로 풀어 implied growth를 산출. 컨센서스 성장률과 비교하면
      주가가 낙관적/비관적인지 판단 가능. (Damodaran 페르소나의 핵심 framework)
    </div>

    <h3>1. 입력 가정 (Assumptions)</h3>
    <table class="dt">
      <tr><th>현재 시가총액</th><td>{dcf['market_cap_bn']:.1f}B {currency}</td>
          <th>현재 매출</th><td>{dcf['revenue_bn']:.1f}B {currency}</td></tr>
      <tr><th>WACC (discount rate)</th><td>{dcf['wacc']*100:.1f}%</td>
          <th>영업이익률</th><td>{dcf['operating_margin']*100:.1f}%</td></tr>
      <tr><th>Terminal growth</th><td>2.5% (perpetual)</td>
          <th>재투자율</th><td>30% of after-tax operating income</td></tr>
    </table>

    <h3>2. 산출 결과</h3>
    <div class="kpi-grid">
      <div class="kpi"><div class="num">{implied*100:.1f}%</div><div class="label">Implied 5Y CAGR</div></div>
      <div class="kpi"><div class="num">{consensus*100:.1f}%</div><div class="label">Consensus 5Y</div></div>
      <div class="kpi"><div class="num" style="color:{'#dc2626' if gap>0 else '#16a34a'};">{'+' if gap>=0 else ''}{gap*100:.1f}%p</div><div class="label">Gap (시장 - 컨센)</div></div>
      <div class="kpi"><div class="num" style="font-size:12pt;">{verdict[0].split(' ',1)[1]}</div><div class="label">Verdict</div></div>
    </div>

    <h3>3. 시나리오 분석 (OPM·WACC 변동성)</h3>
    <table class="dt">
      <thead><tr><th>시나리오</th><th>가정</th><th>Implied Growth</th></tr></thead>
      <tbody>{scenario_rows}</tbody>
    </table>

    <h3>4. 해석</h3>
    <div class="{'warn' if gap>0.03 else 'note' if gap>0 else 'win'}">
      <strong>{verdict[0]}</strong><br/>
      {verdict[1]}
    </div>
    <p style="font-size:9.5pt;line-height:1.6;margin-top:8pt;">
      <strong>Damodaran 원칙</strong>: "DCF로 valuation을 하기 전에 reverse DCF를 먼저 보라.
      현재 가격이 어떤 가정을 하고 있는지를 알아야, 본인의 가정과 비교할 수 있다."<br/><br/>
      <strong>주의</strong>: implied growth는 현재 가격을 정당화하는 단일 변수.
      OPM·재투자율·WACC도 함께 변하므로 sensitivity 표를 함께 봐야 합니다.
    </p>
    """


# Per-ticker default assumptions (can be overridden)
TICKER_DCF_INPUTS = {
    "005490.KS": {"market_cap_bn": 250.0/1300, "revenue_bn": 75.0/1300,  # KRW → USD billion
                   "wacc": 0.105, "operating_margin": 0.04, "consensus_growth": 0.04, "currency": "USD (env)"},
    "ALB": {"market_cap_bn": 11.5, "revenue_bn": 5.8, "wacc": 0.115, "operating_margin": 0.07,
             "consensus_growth": 0.12, "currency": "USD"},
    "SQM": {"market_cap_bn": 14.5, "revenue_bn": 5.1, "wacc": 0.135, "operating_margin": 0.21,
             "consensus_growth": 0.10, "currency": "USD"},
    "006400.KS": {"market_cap_bn": 16.5/1300, "revenue_bn": 18.5/1300,
                   "wacc": 0.105, "operating_margin": 0.05, "consensus_growth": 0.08, "currency": "USD (env)"},
    "003670.KS": {"market_cap_bn": 12.0/1300, "revenue_bn": 4.5/1300,
                   "wacc": 0.115, "operating_margin": 0.05, "consensus_growth": 0.15, "currency": "USD (env)"},

    "BTU": {"market_cap_bn": 2.0, "revenue_bn": 4.5,
             "wacc": 0.12, "operating_margin": 0.12, "consensus_growth": 0.0, "currency": "USD"},
}


def auto_reverse_dcf(ticker: str) -> str | None:
    """ticker 받아서 자동 reverse DCF render."""
    inputs = TICKER_DCF_INPUTS.get(ticker)
    if not inputs:
        return None
    dcf = reverse_dcf(
        market_cap_bn=inputs["market_cap_bn"],
        revenue_bn=inputs["revenue_bn"],
        wacc=inputs.get("wacc", 0.10),
        operating_margin=inputs.get("operating_margin", 0.10),
    )
    return render_reverse_dcf(ticker, dcf, inputs.get("consensus_growth", 0.10),
                                inputs.get("currency", "USD"))
