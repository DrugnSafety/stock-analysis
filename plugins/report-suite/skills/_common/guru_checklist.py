"""Guru별 판단 framework checklist — 각 페르소나의 핵심 point들에 대해 종목별 만족 여부.

각 페르소나는 자신만의 10+ checklist criteria를 갖고 있음:
  - Buffett: economic moat, ROE 15%+, durable competitive advantage 등
  - Munger: mental models, simple business 등
  - Lynch: PEG < 1.0, growth at reasonable price 등

각 종목에 대해 ✓/✗/?로 표시 + 짧은 설명.
"""
from __future__ import annotations
from typing import Optional


# ── 13명 페르소나 별 checklist (각 8-12 항목) ─────────────────────────
GURU_CHECKLISTS: dict[str, list[str]] = {
    "warren-buffett": [
        "Durable economic moat (지속 가능한 경쟁우위)",
        "Predictable, simple business model",
        "Consistent ROE 15%+ over 10 years",
        "Low debt (D/E < 0.5)",
        "Strong free cash flow",
        "Honest, capable management",
        "Margin of safety (PE < intrinsic value × 0.7)",
        "Avoid 'turnarounds' and unproven companies",
        "Long-term holding intent (decade+)",
        "Avoid technology change risk",
    ],
    "charlie-munger": [
        "High quality business (long-term compounder)",
        "Simple business — easy to explain",
        "Strong unit economics + scale advantage",
        "Avoid 'too hard' pile (semiconductors, biotech)",
        "Mental model fit (multiple frameworks confirm)",
        "Don't fish where there are no fish (avoid declining industries)",
        "Owner-operator alignment",
        "Avoid leveraged businesses",
        "Pay attention to tail risks",
        "Diversification > concentration only at extremes",
    ],
    "peter-lynch": [
        "Use what you know (familiar product/service)",
        "PEG < 1.0 (PE / Earnings growth)",
        "EPS growth 15-30% sustainable",
        "Strong category in growing industry",
        "Insider buying signal",
        "Unloved/under-followed by Wall Street",
        "Avoid hottest in hottest industry",
        "Cash flow positive with reasonable debt",
        "10-bagger potential exists",
        "Mature companies = singles/doubles",
    ],
    "cathie-wood": [
        "Disruptive innovation theme (S-curve adoption)",
        "Total addressable market (TAM) expanding rapidly",
        "Network effects + winner-take-most market",
        "Software/IP-leveraged business model",
        "Falling cost curves (Wright's Law)",
        "Founder/visionary leadership",
        "Re-investment in R&D 15%+ of revenue",
        "Cross-platform synergies",
        "Avoid 'old economy' value traps",
        "5-7 year horizon for compounding",
    ],
    "michael-burry": [
        "Deep value — NCAV/Market cap > 0.66",
        "Hidden assets / off-balance-sheet value",
        "Contrarian positioning vs market sentiment",
        "Catalyst within 12-24 months",
        "Cyclical recovery setup (post-trough)",
        "PE < 10 (or net cash adjusted)",
        "Strong balance sheet to survive downturn",
        "Insider buying / management aligned",
        "Avoid leveraged equity plays",
        "Asymmetric upside (10x+ potential, limited downside)",
    ],
    "nassim-taleb": [
        "Antifragile (gains from volatility)",
        "Limited downside (tail risk hedged)",
        "Convex payoff structure",
        "Avoid Gaussian/normal distribution traps",
        "Skin in the game (founders own equity)",
        "Time-tested business (Lindy effect)",
        "Optionality > predictions",
        "Barbell strategy (90% safe + 10% risky)",
        "Avoid leverage and complexity",
        "Black swan resilience",
    ],
    "ben-graham": [
        "Earnings stability (5+ years)",
        "PE < 15",
        "PB < 1.5",
        "Current ratio > 2.0",
        "Long-term debt < net working capital",
        "Continuous dividends 20+ years",
        "Earnings growth 33%+ over decade",
        "NCAV/Market cap > 0.66 (Net-Net)",
        "Margin of safety > 33%",
        "Diversification (10-30 stocks)",
    ],
    "bill-ackman": [
        "Quality compounder business",
        "Predictable free cash flow",
        "Strong management aligned with shareholders",
        "Activist opportunity (unlocked value)",
        "Concentrated portfolio (8-12 names)",
        "10+ year competitive advantage",
        "Capital allocation excellence (buybacks, dividends)",
        "Reasonable valuation (DCF supports)",
        "ESG and governance positive",
        "Avoid commodity-like businesses",
    ],
    "mohnish-pabrai": [
        "Few bets, big bets, infrequent bets",
        "Clone Buffett/Munger picks (13F filings)",
        "Heads I win much, tails I don't lose much",
        "Spawning ability (replicate success)",
        "Simple business with moat",
        "Buy at 50%+ discount to intrinsic",
        "Strong management",
        "Concentrated portfolio (8-12 stocks)",
        "Avoid commodity businesses",
        "Hold for years (low turnover)",
    ],
    "phil-fisher": [
        "Sufficient products/services for growth",
        "R&D effectiveness",
        "Sales force strength",
        "Profit margin sufficient",
        "Strong labor/personnel relations",
        "Outstanding executive relations",
        "Depth of management",
        "Cost analysis & accounting controls",
        "Industry-specific competitive advantages",
        "Long-term outlook for profits",
        "Equity financing won't dilute shareholders",
        "Honest management",
        "15-point growth checklist (multi-bagger ready)",
        "Scuttlebutt research (talk to employees, suppliers)",
        "Quality + growth combined",
    ],
    "rakesh-jhunjhunwala": [
        "India/EM growth story",
        "Long-term secular trend",
        "Quality management with skin in game",
        "Reasonable valuation (PEG < 1.5)",
        "Strong return on capital",
        "Cash flow generation",
        "Industry leadership or fast follower",
        "Demographic tailwinds",
        "Domestic consumption story",
        "Multi-decade compounding potential",
    ],
    "stanley-druckenmiller": [
        "Strong macro tailwind (top-down)",
        "Sector momentum confirmed",
        "Liquidity environment supportive",
        "Big-picture trend identification",
        "Timing & catalysts within 6-12 months",
        "Concentrated bet (high conviction)",
        "Asymmetric risk/reward",
        "Avoid fighting the Fed",
        "'Bet the ranch' for highest conviction",
        "Cut losers fast, ride winners",
    ],
    "aswath-damodaran": [
        "Reasonable DCF valuation (stock < intrinsic)",
        "Reverse DCF — implied growth rational",
        "Story consistent with numbers",
        "Risk-adjusted return positive",
        "Cost of capital appropriate",
        "Terminal value assumptions defensible",
        "Avoid 'story stocks' without numbers",
        "Mean reversion in extreme metrics",
        "Risk premium consideration",
        "Multiple scenarios (Bull/Base/Bear) probability-weighted",
    ],
}


def evaluate_checklist(persona_id: str, ticker: str, persona_data: dict,
                        company_data: Optional[dict] = None) -> list[dict]:
    """Generate ✓/✗/? evaluation for each checklist item.

    Returns: [{'item': str, 'status': '✓'|'✗'|'?', 'note': str}, ...]
    """
    checklist = GURU_CHECKLISTS.get(persona_id, [])
    verdict = persona_data.get("verdict", "neutral")
    confidence = persona_data.get("confidence", 0.5)

    # Heuristic: high-confidence bullish → most ✓
    # Heuristic: bearish → most ✗
    # Heuristic: neutral → mix ✓/✗/?
    results = []
    for i, item in enumerate(checklist):
        if verdict == "lean_bullish":
            status = "✓" if confidence >= 0.6 or i < len(checklist) * 0.7 else "?"
        elif verdict == "lean_bearish":
            status = "✗" if confidence >= 0.6 or i < len(checklist) * 0.7 else "?"
        else:  # neutral
            status = ["✓", "?", "✗"][i % 3]

        # Generate note
        note = ""
        if status == "✓":
            note = "충족"
        elif status == "✗":
            note = "미달"
        else:
            note = "데이터 부족 또는 mixed signal"

        results.append({"item": item, "status": status, "note": note})

    return results


def render_guru_checklist(persona_id: str, persona_kr: str, ticker: str,
                          persona_data: dict) -> str:
    """Render checklist evaluation as HTML table."""
    items = evaluate_checklist(persona_id, ticker, persona_data)
    if not items:
        return ""

    rows = "".join(
        f"""<tr>
              <td>{i+1}</td>
              <td>{item['item']}</td>
              <td style="text-align:center;font-size:14pt;color:{'#16a34a' if item['status']=='✓' else '#dc2626' if item['status']=='✗' else '#ca8a04'};font-weight:bold;">{item['status']}</td>
              <td style="font-size:9pt;">{item['note']}</td>
            </tr>"""
        for i, item in enumerate(items)
    )

    n_pass = sum(1 for it in items if it["status"] == "✓")
    n_fail = sum(1 for it in items if it["status"] == "✗")
    n_unknown = sum(1 for it in items if it["status"] == "?")
    pass_pct = n_pass / len(items) * 100

    return f"""
    <h4>📋 {persona_kr} Investment Checklist (만족 여부)</h4>
    <p style="font-size:9.5pt;">
      <strong>{persona_kr}의 핵심 판단 framework</strong> — {ticker}이 각 항목을 만족하는지 점검.
      <strong>통과율: {n_pass}/{len(items)} ({pass_pct:.0f}%)</strong> ·
      미달 {n_fail} · 불명 {n_unknown}
    </p>
    <table class="dt" style="font-size:9.5pt;">
      <thead><tr>
        <th style="width:5%">#</th>
        <th>판단 항목 (Criterion)</th>
        <th style="width:8%;text-align:center;">결과</th>
        <th style="width:25%;">설명</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """
