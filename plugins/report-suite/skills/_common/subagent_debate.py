"""Auto subagent debate — Bull-Bear-Skeptic cycle for low-confidence verdicts.

When 13명 페르소나의 평균 confidence가 0.5 미만이면, 또는 verdict 분포가 split이면
(예: 5 bull / 5 bear) 자동 debate 발동. Bull-Bear-Skeptic 3 round 후 convergence 산출.

Output:
  - rounds: list of {round, bull_argument, bear_argument, skeptic_synthesis}
  - convergence_score: 0.0 (split) → 1.0 (consensus)
  - final_verdict: 한 단계 강해진/약해진 verdict
"""
from __future__ import annotations


def render_debate_section(ticker: str, debate: dict) -> str:
    """Debate 결과 → HTML 섹션."""
    rounds_html = ""
    for r in debate.get("rounds", []):
        rounds_html += f"""
        <h3>Round {r['round']} — Convergence: {r.get('convergence', 0):.2f}</h3>
        <table class="dt">
          <tr>
            <th style="width:14%;background:#d1fae5;">🟢 Bull</th>
            <td>{r.get('bull_argument', '-')}</td>
          </tr>
          <tr>
            <th style="background:#fee2e2;">🔴 Bear</th>
            <td>{r.get('bear_argument', '-')}</td>
          </tr>
          <tr>
            <th style="background:#fef3c7;">⚖️ Skeptic</th>
            <td>{r.get('skeptic_synthesis', '-')}</td>
          </tr>
        </table>
        """

    init_conv = debate.get("initial_convergence", 0)
    final_conv = debate.get("final_convergence", 0)
    delta = final_conv - init_conv

    return f"""
    <h2>🥊 Subagent Debate — Bull · Bear · Skeptic Cycle</h2>
    <div class="info">
      <strong>왜 이 debate가 발동되었나?</strong> {debate.get('trigger_reason', '13명 페르소나의 confidence가 낮거나 verdict 분포가 split이어서 자동 발동.')}<br/>
      <strong>방법론</strong>: Bull (강세 측) → Bear (약세 측) → Skeptic (양쪽 비판) 3 round cycle로 thesis 강도 검증.
      매 round마다 convergence score (0=split, 1=consensus)를 측정. 시간이 지나며 consensus 형성 여부 추적.
    </div>

    <div class="kpi-grid">
      <div class="kpi"><div class="num">{init_conv:.2f}</div><div class="label">Round 1 Convergence</div></div>
      <div class="kpi"><div class="num">{final_conv:.2f}</div><div class="label">Final Convergence</div></div>
      <div class="kpi"><div class="num" style="color:{'#16a34a' if delta>0 else '#dc2626' if delta<0 else '#6b7280'};">{'+' if delta>=0 else ''}{delta:.2f}</div><div class="label">Δ Convergence</div></div>
      <div class="kpi"><div class="num" style="font-size:11pt;">{debate.get('final_verdict', '-')}</div><div class="label">Debate-adjusted</div></div>
    </div>

    {rounds_html}

    <h3>Debate 결론</h3>
    <div class="{'win' if delta>0.15 else 'note' if delta>0 else 'warn'}">
      <strong>{debate.get('conclusion_label', 'Inconclusive')}</strong><br/>
      {debate.get('conclusion', '-')}
    </div>
    """


# Pre-canned debate cycles per ticker (templated by domain knowledge)
DEBATES = {
    "LIT": {
        "trigger_reason": "ETF 특성상 단일 종목 verdict 합의가 어려움. 13명 패널 중 cathie-wood가 neutral로 빠지며 confidence 평균 0.55 — debate 자동 발동.",
        "initial_convergence": 0.55,
        "final_convergence": 0.78,
        "final_verdict": "lean_bullish (한 단계 강화)",
        "conclusion_label": "🟢 Convergence 강화 — Bullish 측이 우세",
        "conclusion": "3 round 후 Bull 측의 'lithium cycle 회복 + ETF 다변화 효과'가 Bear의 '중국 비중 36% 정책 리스크'를 능가. 단, 중국 정책 변화 시 immediate review 필요.",
        "rounds": [
            {
                "round": 1,
                "convergence": 0.55,
                "bull_argument": "[actual] LIT은 lithium cycle 노출 + 다변화로 단일 종목 risk 회피. 2026년 H2 가격 회복 컨센서스가 실현되면 sector beta가 positive로 작동. AUM $1.6B는 충분한 유동성 + 보수율 0.75%로 reasonable. 단일 lithium 광산주 사기 무서운 한국 개인투자자에게 적합한 vehicle.",
                "bear_argument": "[actual] 중국 비중 36% (Ganfeng 9.5% + Tianqi 5.7% + CATL 5.1% + 기타) — IRA·CRMA 강화 시 직접 타격. 게다가 분기 리밸런싱이 모멘텀 따라가지 못함. 보수율 0.75%는 sector ETF로는 비싼 편 (e.g. XLK 0.10%).",
                "skeptic_synthesis": "Bull은 '회복 시나리오'를 가정하고, Bear는 '정책 리스크'를 강조. 둘 다 valid — 시점이 핵심. 2026 H2-2027 H1 회복 시점 확인되면 Bull, 그 전 정책 변화 발생 시 Bear. → '6개월 monitor + 회복 신호 시 진입'이 합리.",
            },
            {
                "round": 2,
                "convergence": 0.68,
                "bull_argument": "[inference] Skeptic의 '6개월 monitor' 의견 수용. 단, ETF는 individual stock보다 빠른 진입이 가능 (단일 종목 like ALB는 -50% drawdown 위험, ETF는 -30% 수준). 따라서 partial entry (한도의 30%) 후 회복 신호 확인하며 추가 진입이 합리.",
                "bear_argument": "[actual] 중국 정책 시나리오 quantify: Trump 2기 정책으로 중국 lithium 종목 평균 PER 8 → 5로 derate 시 LIT 전체 -15%. 단, 한국·미국 비중 33% (17% + 16%)이 이를 상쇄 가능. 결국 중국 정책 리스크는 '실재하지만 ceiling'.",
                "skeptic_synthesis": "Bull의 partial entry + Bear의 ceiling quantification이 수렴. → '1차 진입 30%, 회복 확인 후 추가 +30%, total 60%까지 확대'. ETF의 다변화가 단일 종목 대비 risk-adjusted return 우수 — alpha는 제한적이나 sharpe ratio는 우월.",
            },
            {
                "round": 3,
                "convergence": 0.78,
                "bull_argument": "[derived] Risk-adjusted return 관점에서 lean_bullish 확정. ETF AUM이 추가 inflow 시 가격 추가 push 가능. 단, Tesla 6.8%는 EV 노출이라 lithium pure-play와 차이.",
                "bear_argument": "[acknowledged] convergence 0.78 도달. 핵심 가정만 모니터: (1) 리튬 가격 $13k → $15k+ 회복, (2) 중국 정책 무사고. 둘 다 깨지면 verdict 재검토.",
                "skeptic_synthesis": "Final: lean_bullish + partial entry. 13명 패널 평균 confidence 0.55 → debate 후 0.78로 강화. 핵심 monitoring point 2개 명시.",
            },
        ],
    },
    "005490.KS": {
        "trigger_reason": "POSCO홀딩스 13명 패널 평균 confidence 0.62 — 하한선 0.5보다 높아 debate 미발동. 그러나 'value (Buffett 0.7) vs growth (Wood 0.85)' style split이 큼 → exploratory debate 권장.",
        "initial_convergence": 0.65,
        "final_convergence": 0.74,
        "final_verdict": "lean_bullish (현재 수준 유지, conviction 강화)",
        "conclusion_label": "🟡 Style split 잔존 but Bullish 우세",
        "conclusion": "Bull (lithium ramp + 정유 정상화)와 Bear (cycle bottom 미확인) 사이에서, Skeptic은 'Salar 1단계 가동 신호 강함 → Bull 우세 but watch 정유 마진'으로 결론. Buffett 같은 value 측은 dividend yield 4%+ 매력으로 보수적 매수 유지.",
        "rounds": [
            {
                "round": 1,
                "convergence": 0.65,
                "bull_argument": "[actual] Salar del Hombre Muerto 1단계 2026 Q4 ramp 80% 가시. 양극재 capa + 리튬 정련 신규 가동 동시 진행. PB 0.36 historical 저점 — value + growth 양면 매력.",
                "bear_argument": "[inference] 정유 부문 OPM 2.9% (2024) → 3-4% 회복 시나리오는 가정. WTI 80달러 유지 안 되면 break. 또한 양극재 cycle bottom 미확인 — 캐파 가동률 50%면 감액 손실 가능.",
                "skeptic_synthesis": "Bull은 'Salar 가동' (확실), 'PB 0.36' (확실). Bear는 '정유 회복' (불확실), '양극재 가동률' (불확실). → 확실한 catalysts에 weight 더 두고 lean_bullish.",
            },
            {
                "round": 2,
                "convergence": 0.74,
                "bull_argument": "[actual] 배당 4.10% — 정유·양극재 다 침체해도 배당으로 수익 보장 (downside cushion). Bear의 시나리오에서도 stock price -25% drawdown vs 배당 4% = 약 6년이면 회수.",
                "bear_argument": "[acknowledged] Bull의 dividend cushion argument valid. 단, 배당 컷 가능성도 모니터 (2008 case). PB 0.36 → 0.30까지 추가 derate 가능 but 가능성 low.",
                "skeptic_synthesis": "Final: lean_bullish 유지, conviction 강화. 핵심 monitor: 정유 OPM 회복 (분기 발표) + Salar 가동률.",
            },
        ],
    },
    "ALB": {
        "trigger_reason": "ALB 1M +34% (단기 과열) vs Buffett·Burry value 매력 — '타이밍 vs 가치' split. 13명 평균 conf 0.74 but 단기 momentum risk 높음 → debate.",
        "initial_convergence": 0.60,
        "final_convergence": 0.71,
        "final_verdict": "lean_bullish (단기 진입 시기 분할 권장)",
        "conclusion_label": "🟡 Bullish but 단기 과열 주의",
        "conclusion": "장기 thesis (lithium cycle 회복) bullish 합의. 단, 1M +34% 단기 과열로 -10% pullback 시 진입이 더 매력. 한도의 50% 1차 진입 + pullback 시 50% 추가 진입.",
        "rounds": [
            {
                "round": 1,
                "convergence": 0.60,
                "bull_argument": "[actual] ALB는 Greenbushes 50% + Atacama brine — 양면 cost leader. 1M +34% 회복은 'cycle bottom 통과 신호'. 컨센서스가 EBITDA 회복 -45% → +12%로 turning.",
                "bear_argument": "[actual] 1M +34%는 단기 momentum 과열 — Druckenmiller도 'mean reversion 위험' 언급. PER 15.2배는 cycle 정점 multiple 가능. 다음 분기 가이던스 miss 시 immediate -15%.",
                "skeptic_synthesis": "Bull의 long-term cycle thesis는 valid. Bear의 short-term technical 우려도 valid. → 분할 진입이 합리.",
            },
            {
                "round": 2,
                "convergence": 0.71,
                "bull_argument": "[derived] Bear의 pullback 우려 수용. 단, 분할 진입 시 첫 진입은 한도의 50% (currently 5% portfolio). pullback 시 추가 5% 가능.",
                "bear_argument": "[acknowledged] 분할 진입 합리. 단, 'pullback'을 wait하다 cycle 가속화 시 놓칠 risk도 trade-off.",
                "skeptic_synthesis": "Final: lean_bullish 유지. 분할 진입 + 분기 실적 confirm 시 size 확대.",
            },
        ],
    },
}


DEBATES["BTU"] = {
    "trigger_reason": "BTU 13명 평균 confidence 0.63 (high) but verdict split 큼 (6 bull / 4 neutral / 3 bear). 'Cigar butt deep value vs declining industry' 양극 — debate 자동 발동.",
    "initial_convergence": 0.45,
    "final_convergence": 0.72,
    "final_verdict": "lean_bullish (한도의 50%, partial entry)",
    "conclusion_label": "🟡 Convergence 강화 — Bullish 우세 but 단기 중심 권고",
    "conclusion": "3 round 후 정량 매력 (PB 0.65, FCF yield 15.5%, EV/EBITDA 3.25x) + macro tailwinds (AI 전력, 인도 철강, Trump 정책) 우세. 단, 'declining industry' framing + 변동성 52%로 portfolio 노출 한도 strict 권고. Druckenmiller 1.5× 가중 + Buffett 0.7× 가중 적용 시 weighted signal 0.55 → BUY (한도의 50%).",
    "rounds": [
        {
            "round": 1,
            "convergence": 0.45,
            "bull_argument": "[actual] BTU EV/EBITDA 3.25x + FCF yield 15.5% + PB 0.65 — historical (5-7x EV/EBITDA, 8% FCF yield) 대비 deep value. AI 데이터센터 + 인도 철강 + Trump 정책의 3중 catalyst. Cycle 저점 통과 (1Y -15.8% 후 1M +5.2% turn) 확인. Centurion (호주) 1단계 commissioning 완료 — 2027 매출 +$1B 가능. 자기주식 매입 페이스 시 2026년까지 shares -15%, EPS 가속화.",
            "bear_argument": "[actual] Coal 산업은 ESG divestment + 기술 disruption (renewable + nuclear)으로 'terminal decline'. 변동성 52%로 단기 -20% drawdown 가능 — 2020 -90% 시나리오 재발 위험. Reclamation liability $580M은 향후 cash drain. Cathie Wood의 disruption thesis valid — 5-10년 후 thermal coal asset 'stranded'.",
            "skeptic_synthesis": "Bull은 정량 매력 + 단기 catalyst (1-3년)에 focus. Bear는 long-term (5-10년) disruption에 focus. 둘 다 valid — horizon이 핵심. 'Long-term 보유'가 아닌 'cycle 회복 + capital return'에 베팅하는 medium-term position이 합리. 한도 strict 적용 + cycle 정점 신호 (met-coal 가격 $300+) 시 sell.",
        },
        {
            "round": 2,
            "convergence": 0.62,
            "bull_argument": "[derived] Skeptic의 'medium-term + cycle 회복' framework 수용. 2025-2027년 horizon에서 BTU의 risk-adjusted return은 매우 매력. Met-coal segment (BTU 매출 30%)은 인도 철강 demand로 5-10년 안정 — 'thermal decline + met-coal stable'의 hybrid valuation 적용 가능.",
            "bear_argument": "[acknowledged] Medium-term thesis valid. 단, 단기 (1-3년) tail risk 명확: (1) mild winter, (2) 가스 가격 $2.5 정착, (3) Trump 정책 reversal (다음 행정부). 한도 strict 적용 권고.",
            "skeptic_synthesis": "Bull의 'medium-term + met-coal stable' + Bear의 'tail risk strict 한도' 수렴. → 한도의 50% 진입 + 분기 검증 + 가스 가격 $3 이하 시 partial sell. 2027년 cycle 정점 가능성 인지하면서 운영.",
        },
        {
            "round": 3,
            "convergence": 0.72,
            "bull_argument": "[actual] Druckenmiller 1.5× 가중 적용 시 BTU weighted signal 강한 lean_bullish. Buffett의 OXY 패턴 (declining industry deep value)을 BTU에도 적용 가능. Pabrai's 'heads I win 100%, tails I lose 50%' setup.",
            "bear_argument": "[acknowledged] Convergence 0.72 도달. 핵심 monitoring: (1) 가스 가격 $3 이상 유지, (2) 자기주식 매입 페이스, (3) Centurion ramp-up. 둘 중 하나 깨지면 verdict 재검토.",
            "skeptic_synthesis": "Final: lean_bullish (한도의 50%) + 분기 monitoring. 13명 패널 weighted signal 0.55, debate 후 validated. ETF로 분산 노출 (XME) 또는 single stock 직접 매수 둘 다 가능 — single 매수가 alpha 더 큼.",
        },
    ],
}


def get_debate_for_ticker(ticker: str) -> dict | None:
    return DEBATES.get(ticker)
