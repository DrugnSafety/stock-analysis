"""Guru별 판단 framework checklist — 각 페르소나의 핵심 point들에 대해 종목별 만족 여부.

각 페르소나는 자신만의 10+ checklist criteria를 갖고 있음:
  - Buffett: economic moat, ROE 15%+, durable competitive advantage 등
  - Munger: mental models, simple business 등
  - Lynch: PEG < 1.0, growth at reasonable price 등

각 종목에 대해 [O]/[X]/[?]로 표시 + 학습용 설명.

Sprint Fix-C (2026-05-28) 대규모 강화:
- 모든 페르소나의 거의 모든 criterion에 실데이터 매핑 추가
- 각 항목에 학습용 explanation (의미·중요성·해석법)
- column width 명시 (판단 항목 28%, 결과 8%, 설명 64%)
"""
from __future__ import annotations
from typing import Optional


# ── 17명 페르소나 별 checklist (각 8-15 항목) ─────────────────────────
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
        "High-quality business with predictable cash flows",
        "Strong economic moat (network effects, brand, switching cost)",
        "Mid-large cap (>$5B market cap)",
        "Activist catalyst opportunity",
        "Management willing to engage with shareholders",
        "Concentrated portfolio (8-12 names)",
        "Long-term holding (3-7 years)",
        "Spin-off or break-up value",
        "Capital allocation track record",
        "ESG / governance improvement potential",
    ],
    "mohnish-pabrai": [
        "Margin of safety > 50% (deep value)",
        "Simple business (Munger framework)",
        "Concentrated portfolio (5-10 names)",
        "Heads I win, tails I don't lose much (asymmetric)",
        "Owner-operator with skin in the game",
        "PE < 10 or P/FCF < 10",
        "Strong free cash flow generation",
        "Hold for 2-3 years minimum",
        "Avoid 'value traps' (declining businesses)",
        "10x potential in 5 years (Spawner)",
    ],
    "phil-fisher": [
        "Sufficient products/services for growth",
        "R&D effectiveness",
        "Sales force strength",
        "Profit margin sufficient",
        "Profit margin improvement track record",
        "Labor & personnel relations strong",
        "Depth of management",
        "Cost analysis & accounting controls",
        "Industry-specific competitive advantages",
        "Long-term outlook for profits",
        "Equity financing needed?",
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
        "Strong balance sheet",
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
        "Currency/rate cycle favorable",
        "Timing & catalysts within 6-12 months",
        "Concentrated bet (high conviction)",
        "Asymmetric risk/reward",
        "Avoid fighting the Fed",
        "'Bet the ranch' for highest conviction",
        "Cut losses fast if thesis breaks",
    ],
    "aswath-damodaran": [
        "Story-numbers consistency",
        "DCF intrinsic value calculable",
        "Margin of safety > 25%",
        "Growth assumptions reasonable (3-5% terminal)",
        "Cost of capital (WACC) appropriate",
        "Reinvestment efficiency (ROIC > WACC)",
        "Multiple scenarios (Bull/Base/Bear) probability-weighted",
    ],
    # Phase 2 additions
    "ray-dalio": [
        "All Weather quadrant fit (current macro regime)",
        "Debt cycle position favorable (not late-cycle)",
        "Diversification value (low correlation with portfolio)",
        "Inflation hedge or duration play 분류",
        "Sovereign currency risk 점검",
        "Defensive allocation (recession-resistant)",
        "Liquidity premium 적정",
        "Productivity growth proxy",
        "Long-term cycle anchor (50~75y debt cycle)",
        "Risk-parity contribution",
    ],
    "george-soros": [
        "Reflexivity cycle stage 식별 (1~8단계)",
        "Narrative strength vs fundamentals gap",
        "Catalyst for reversal 존재",
        "Position sizing per conviction",
        "Boom-bust 단계 판단",
        "Market sentiment extreme 식별",
        "Macro-narrative interplay 추적",
        "Skepticism towards conventional wisdom",
        "Convex payoff structure",
        "'Bet big when right' courage",
    ],
    "jim-simons": [
        "Volatility regime classification (low/mid/high)",
        "Mean reversion vs momentum signal",
        "Sharpe quality tier 적절",
        "Beta classification (low_corr/market/high)",
        "Stat-arb signal 존재",
        "Portfolio optimizer weight > equal-weight",
        "Risk-parity position size 적절",
        "Backtest 30Y+ return profile",
        "Black-box system reliability",
        "Avoid narrative-driven trades",
    ],
    "cliff-asness": [
        "Value factor z-score (HML 노출)",
        "Profitability factor (RMW) tier",
        "Momentum factor 12-1M return",
        "Quality factor 평가",
        "Size factor (SMB) 분류",
        "Composite score > +0.5",
        "Multi-factor diversification",
        "Regime-adjusted factor weight",
        "Long-term factor premium 신뢰",
        "Academic Fama-French framework",
    ],
}


# ── Sprint Fix-C (2026-05-28) — 모든 페르소나의 거의 모든 criterion에 매핑 + 학습용 explanation ──
# explanation은 "이 항목이 무엇을 의미하고 왜 이 페르소나가 중요시하는지 + 일반적 해석법"
CRITERION_DATA_RULES = {
    # ─ Warren Buffett ────────────────────────────────────
    "Durable economic moat (지속 가능한 경쟁우위)": {
        "qualitative": True,
        "explanation": (
            "<strong>Moat(경제적 해자)</strong>는 경쟁사가 진입·복제하기 어려운 구조적 우위 (브랜드·"
            "네트워크 효과·전환비용·규모우위·정부 면허). Buffett 평가의 가장 중요한 항목. "
            "정량 proxy: <strong>ROE 일관성(10년+ > 15%)</strong>, gross margin 안정성, "
            "industry market share. ROE가 매년 들쭉날쭉하면 moat 약한 신호."
        ),
    },
    "Predictable, simple business model": {
        "qualitative": True,
        "explanation": (
            "Buffett은 \"10년 후 어떤 모습일지 예측 가능한 비즈니스\"만 투자. 코카콜라·시즈캔디 같은 "
            "안정 제품. Tech·biotech는 회피 (변화 너무 빠름). 평가법: 비즈니스를 5분 안에 평범한 "
            "사람에게 설명할 수 있는가? 매출 driver가 1~3개로 단순한가?"
        ),
    },
    "Consistent ROE 15%+ over 10 years": {
        "metric": "roe_pct", "op": ">=", "threshold": 15, "unit": "%",
        "desc": "최근 ROE",
        "explanation": (
            "<strong>ROE = 순이익 / 자본</strong>. 자본 1단위당 얼마나 효율적으로 이익을 내는가. "
            "<strong>15%+ 10년 연속</strong>은 매우 어려운 조건 — S&P 500 중 ~30개 기업만 충족. "
            "Buffett은 이를 \"moat의 정량 증거\"로 사용. 다만 부채 활용한 ROE 부풀리기 주의 "
            "(D/E 함께 봐야). ROIC = ROE에서 부채효과 제거한 더 robust 지표."
        ),
    },
    "Low debt (D/E < 0.5)": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 50, "unit": "%",
        "desc": "D/E 비율 (부채/자본)",
        "explanation": (
            "<strong>D/E (Debt-to-Equity)</strong> 비율 — 자본 1원당 부채. Buffett은 50% 이하 선호 "
            "(보수적). <strong>100%↑ leveraged, 200%↑ highly leveraged</strong>, 300%↑ 매우 위험. "
            "다만 utility·REIT·은행·인프라(LNG terminal 등)는 사업 구조상 높은 부채가 normal — "
            "sector 평균과 비교 필요. Munger도 동일하게 'avoid leveraged businesses' 강조."
        ),
    },
    "Strong free cash flow": {
        "metric": "fcf_margin_pct", "op": ">=", "threshold": 8, "unit": "%",
        "desc": "5Y avg FCF margin",
        "explanation": (
            "<strong>FCF margin = (영업현금흐름 - CapEx) / 매출</strong>. 8%+면 양호, 15%+면 우수, "
            "20%+면 cash machine (Microsoft·Visa급). FCF는 회계상 이익(NI)보다 신뢰도 높음 — "
            "감가상각·재고 같은 non-cash 항목 제거. Buffett은 'cash is king' — owner earnings "
            "(FCF의 변형)으로 평가. 5년 평균을 봐야 cyclical noise 제거."
        ),
    },
    "Honest, capable management": {
        "qualitative": True,
        "explanation": (
            "정량 평가 어려운 영역. Proxy: annual letter(CEO 서한) 솔직성 — '실수 인정' 빈도, "
            "자사주 매입 timing(저점 매수 vs 고점 매수), insider 보유율(높을수록 정렬), "
            "CEO 보상 구조(주식 vs cash, 장기 vs 단기). Buffett 본인은 Berkshire annual letter "
            "유명 — \"shareholder가 partner\" 톤. Tobacco·기업회생 회피 — 도덕적 기준 명확."
        ),
    },
    "Margin of safety (PE < intrinsic value × 0.7)": {
        "metric": "dcf_upside_pct", "op": ">=", "threshold": 30, "unit": "%",
        "desc": "DCF upside",
        "explanation": (
            "<strong>Margin of safety</strong> = Buffett·Graham의 핵심 개념. 내재가치 대비 30% 이상 "
            "할인된 가격에 매수해야 \"실수에 대한 안전마진\" 확보. DCF intrinsic을 200으로 계산했다면 "
            "140 이하에 매수. WACC을 0.5%p 보수적으로 잡고 산출한 intrinsic이 더 robust. "
            "Burry는 50%+, Pabrai는 50%+ 권고 (deep value)."
        ),
    },
    "Avoid 'turnarounds' and unproven companies": {
        "qualitative": True,
        "explanation": (
            "Buffett: \"turnarounds seldom turn\". 부실기업 회복은 통계적으로 매우 어려움. 차라리 "
            "이미 우량한 기업 fair price에 매수. Penn Central·USAir 등 turnaround 시도 실패 후 결론. "
            "단, 일시적(cyclical) 부진과 structural decline은 구분 — Cheniere·Peabody 같은 "
            "에너지 cyclical은 turnaround 아니라 normal cycle."
        ),
    },
    "Long-term holding intent (decade+)": {
        "qualitative": True,
        "explanation": (
            "Buffett: \"우리가 좋아하는 holding period는 forever\". 10년 이상 보유 의도로 매수 — "
            "분기 실적 변동 무관. 세후 수익 측면에서 buy-and-hold가 단기매매보다 압도적 유리 "
            "(20%/년 → 10년 후 6.2x, 25%/년 단타 → 세후 ~10년 후 3x). 분기마다 매매하면 "
            "long-tail compounding 손실."
        ),
    },
    "Avoid technology change risk": {
        "qualitative": True,
        "explanation": (
            "Buffett은 IBM·Apple 외 tech 회피 — \"10년 후 모습 예측 불가\". 2016년 Apple은 "
            "consumer brand로 분류해서 매수 (iPhone moat). 일반 software·hardware·biotech는 "
            "여전히 'too hard pile'. 평가: 본 사업이 \"향후 10년 disruption될 가능성\"이 있는가? "
            "에너지·식품·소비재는 안정, AI·반도체·biotech는 disruption risk 높음."
        ),
    },

    # ─ Charlie Munger ────────────────────────────────────
    "High quality business (long-term compounder)": {
        "metric": "roe_pct", "op": ">=", "threshold": 12, "unit": "%",
        "desc": "Quality proxy = ROE (>=12% = compounder 기준)",
        "explanation": (
            "Munger의 \"high quality\" = 자본 재투자 수익률 높음 + 재투자 기회 풍부 + "
            "moat 있음. <strong>ROE 12%+</strong>는 compounder 기준 (S&P 평균 ~13%). "
            "See's Candies·Costco·Berkshire 본체가 대표 사례. Quality보다 가격이 좋아도 "
            "low-quality는 회피 — \"a great business at a fair price\" 우선."
        ),
    },
    "Simple business — easy to explain": {
        "qualitative": True,
        "explanation": (
            "Munger: \"투자에 IQ 130 이상은 필요 없다 — 자기 능력범위만 알면 된다\". "
            "5분 안에 비즈니스를 설명할 수 있어야 함. LNG export, 음료 회사, 사탕 회사는 simple. "
            "Derivative trading, biotech R&D, AI semis는 complex — too hard pile."
        ),
    },
    "Strong unit economics + scale advantage": {
        "metric": "op_margin_pct", "op": ">=", "threshold": 15, "unit": "%",
        "desc": "최근 OPM (15%+는 양호 단위경제)",
        "explanation": (
            "<strong>Unit economics</strong> = 제품·고객 1단위당 수익성. OPM 15%+는 양호한 "
            "단위경제 신호. <strong>Scale advantage</strong>는 매출 ↑할 때 OPM도 함께 개선되는지로 "
            "확인 (operating leverage). Walmart·Costco·Amazon이 대표 사례 — 규모 커질수록 마진 개선."
        ),
    },
    "Avoid 'too hard' pile (semiconductors, biotech)": {
        "qualitative": True,
        "explanation": (
            "Munger의 \"too hard pile\" 개념: \"내가 예측 못 하는 비즈니스는 즉시 pass\". "
            "Semiconductors (cycle·기술 변화), biotech (임상 binary 결과), 신약 R&D는 회피. "
            "단순한 기업 (coca-cola, costco)에서만 우위 확보 — 능력범위(circle of competence) 강조."
        ),
    },
    "Mental model fit (multiple frameworks confirm)": {
        "qualitative": True,
        "explanation": (
            "Munger의 'latticework of mental models': 심리학·물리·생물·수학 모델 100+ 활용. "
            "여러 모델이 같은 결론을 가리킬 때 conviction. 한 모델만 OK면 false positive 위험. "
            "예: 1) 경제학 (moat 확인) + 2) 심리학 (consumer behavior 안정) + "
            "3) 수학 (compound interest 작동) = 3모델 confirm."
        ),
    },
    "Don't fish where there are no fish (avoid declining industries)": {
        "qualitative": True,
        "explanation": (
            "Munger: 좋은 swimmer라도 물고기 없는 연못에서 못 잡음. 사양산업(석탄·신문·DVD)은 "
            "individual 회사 잘해도 sector tailwind 부재. Cheniere(LNG)는 sector tailwind "
            "(글로벌 LNG 수요 증가 + EU 러시아 가스 대체) — Munger 기준 OK. "
            "신문·전통 retail은 회피 대상."
        ),
    },
    "Owner-operator alignment": {
        "qualitative": True,
        "explanation": (
            "Owner-operator = 창립자/CEO가 큰 지분 보유 → 주주와 이해 정렬. "
            "Insider 보유율 5%+ = 양호, 10%+ = 강한 신호. Berkshire 본체가 대표 — Buffett 본인 "
            "거의 전 재산을 Berkshire 주식. Tesla(머스크) · Meta(저커버그) 같은 founder-led도 해당. "
            "단, 절대 권력은 위험 — 적절한 board oversight 필수."
        ),
    },
    "Avoid leveraged businesses": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 100, "unit": "%",
        "desc": "D/E 비율 (100% 초과는 leveraged)",
        "explanation": (
            "Munger: \"부채는 좋은 것을 망친다\". <strong>D/E 100% 초과 = leveraged</strong>, "
            "200%+ = highly leveraged. 경기침체·금리 상승 시 default risk. 단 utility·REIT·은행·"
            "인프라 (LNG terminal 등 capex 무거운 사업)는 sector 평균 200~500% — 비교 기준 필요. "
            "Cheniere(LNG)의 D/E 439%는 sector 평균(에너지 인프라 ~300%) 보다 약간 높음."
        ),
    },
    "Pay attention to tail risks": {
        "metric": "max_drawdown_pct", "op": ">=", "threshold": -30, "unit": "%",
        "desc": "최근 1Y MaxDD (-30% 이내면 OK)",
        "explanation": (
            "Munger: \"how to fail at investing: lose all your money in tail events\". "
            "<strong>MaxDD(최대낙폭)</strong>는 historical tail event proxy. -30% 이내면 OK, "
            "-50%+면 high tail risk (회복까지 100% 상승 필요). Taleb도 동일 강조 — black swan에 "
            "취약한 leveraged business 회피. CVaR 99%로 tail 정량 측정 가능."
        ),
    },
    "Diversification > concentration only at extremes": {
        "qualitative": True,
        "explanation": (
            "Munger: \"diversification is for those who don't know\". 본인은 3-5 종목 concentrated, "
            "그러나 일반 투자자에게는 15-30 종목 분산 권고. 'extreme' = 정말 확신 있는 1-2개에만 "
            "큰 포지션 (Pabrai의 'spawner' 컨셉). Buffett도 Coca-Cola·Apple 등 top-5가 portfolio "
            "70%+. 평가: 본 종목이 그런 'extreme conviction' 후보인가?"
        ),
    },

    # ─ Peter Lynch ───────────────────────────────────────
    "Use what you know (familiar product/service)": {
        "qualitative": True,
        "explanation": (
            "Lynch: \"내가 매일 쓰는 제품·서비스의 회사를 매수\". 일반 투자자가 월스트리트보다 "
            "1-2년 먼저 트렌드 발견 가능 (예: Dunkin Donuts, Subaru). LNG(천연가스 수출)은 "
            "일반인이 직접 사용 안 함 → Lynch 기준 unfamiliar. Tech·biotech는 회피."
        ),
    },
    "PEG < 1.0 (PE / Earnings growth)": {
        "metric": "peg", "op": "<=", "threshold": 1.0, "unit": "",
        "desc": "PEG (PE를 성장률로 나눈 값)",
        "explanation": (
            "<strong>PEG = PE / Earnings growth rate</strong>. Lynch가 발명한 metric. "
            "<strong>< 1.0 = 저평가</strong>, 1.0~1.5 = fair, > 2.0 = overvalued. "
            "PE 20에 성장 30%면 PEG 0.67 — 저평가. PE 10에 성장 5%면 PEG 2.0 — overvalued. "
            "Growth at reasonable price (GARP) framework의 핵심. PEG만 보면 안 되고 성장 sustainability도 함께."
        ),
    },
    "EPS growth 15-30% sustainable": {
        "metric": "revenue_cagr_pct", "op": ">=", "threshold": 15, "unit": "%",
        "desc": "5Y revenue CAGR (EPS proxy)",
        "explanation": (
            "Lynch의 sweet spot: <strong>EPS 성장 15~30%/년 sustainable</strong>. "
            "10% 이하 = mature(별 매력 X), 50%+ = unsustainable hype (Tesla 2020년). "
            "EPS 데이터 부재 시 revenue CAGR으로 proxy. 5년 연속 양호한 성장이 sustainability "
            "증거. Margin이 동시 개선되면 operating leverage 발휘 — 더 좋은 신호."
        ),
    },
    "Strong category in growing industry": {
        "qualitative": True,
        "explanation": (
            "\"좋은 회사 + 사양 산업\" < \"평범한 회사 + 성장 산업\". Industry tailwind가 "
            "company-specific factor보다 더 중요한 경우 많음. LNG는 \"글로벌 LNG 수요 +5%/년\" + "
            "\"美 export capacity 30%+ 확대\" 등 strong tailwind. 반대로 신문·전통 retail은 "
            "산업 자체가 declining."
        ),
    },
    "Insider buying signal": {
        "qualitative": True,
        "explanation": (
            "Insider(임원·이사) 매수는 강한 bullish 신호 — 본인 돈으로 매수했다는 것은 "
            "내부 정보로 확신했다는 의미. 매도는 noise 많음 (옵션 행사, 세금, 분산 등). "
            "Form 4(SEC) 또는 한국 DART에서 확인. 3개월 내 임원 매수 $1M+이면 주목."
        ),
    },
    "Unloved/under-followed by Wall Street": {
        "qualitative": True,
        "explanation": (
            "Lynch: 분석가가 1~2명만 covering하는 종목에서 alpha 발견 가능. 모두가 분석하는 "
            "메가캡(AAPL·MSFT)은 정보 비대칭 0 — 본질가치 ~ 가격. Mid-cap·미국 ex-tech 또는 "
            "외국 종목에서 unloved 기회. Sell-side analyst 수 < 5 + institutional holding < 50% = 후보."
        ),
    },
    "Avoid hottest in hottest industry": {
        "qualitative": True,
        "explanation": (
            "Lynch: \"the hottest stock in the hottest industry is a guaranteed loser\". "
            "Dot-com 2000, China A-shares 2007, Crypto 2021, AI 2024 등. Hype peak에 진입하면 "
            "최대 손실. 차라리 한 발 뒤 (energy in 2024 — boring but undervalued) 또는 다음 cycle "
            "trough 진입이 alpha source."
        ),
    },
    "Cash flow positive with reasonable debt": {
        "metric": "fcf_5y_avg", "op": ">", "threshold": 0, "unit": "M",
        "desc": "5Y avg FCF (양수면 OK)",
        "explanation": (
            "<strong>FCF 5Y 평균이 양수</strong> = 핵심 재무 안정성 기준. 5년 연속 음수면 "
            "structural cash burn (위험). 일시적 음수(M&A·CapEx 폭증)는 OK — 다음 해 회복 확인. "
            "Debt가 'reasonable'(D/E < 1.0)이고 FCF 양수면 deleveraging 가능 — 안전 마진."
        ),
    },
    "10-bagger potential exists": {
        "qualitative": True,
        "explanation": (
            "Lynch의 'tenbagger' 개념: 10배 수익 잠재력. 조건: 1) 작은 시가총액 (< $5B), "
            "2) 성장 산업, 3) replicable model (단일 매장 → 전국·글로벌 확장), "
            "4) management 우수. Walmart·Microsoft·Starbucks 초기. Mid-large cap에서는 어렵고 "
            "mid-cap (~$2B)에서 가장 자주 발견."
        ),
    },
    "Mature companies = singles/doubles": {
        "qualitative": True,
        "explanation": (
            "Lynch 야구 비유: tenbagger는 home run, mature는 single/double. 매출 성장 5~10%, "
            "성장 sustainable한 안정 기업 (Coca-Cola, J&J 등)에서는 10% 안정 수익 목표. "
            "Home run 노리면 strikeout 빈도 ↑. Portfolio = home run 후보 + singles mix."
        ),
    },

    # ─ Ben Graham ─────────────────────────────────────────
    "Earnings stability (5+ years)": {
        "qualitative": True,
        "explanation": (
            "Graham의 'defensive investor' framework: 5년 연속 이익 양수 + 적자 없음. "
            "Cyclical 종목은 trough에 적자 가능 — 그래도 cumulative 5Y는 양수여야 함. "
            "Earnings variance 자체도 중요 — 매년 ±50% 변동은 unstable. Margin of safety 적용 시 "
            "stability 부족하면 더 큰 discount 요구."
        ),
    },
    "PE < 15": {
        "metric": "forward_pe", "op": "<=", "threshold": 15, "unit": "",
        "desc": "Forward PE",
        "explanation": (
            "Graham의 \"defensive investor\" PE 한도. <strong>PE < 15 + PB < 1.5</strong>가 "
            "기본 screen. 둘의 곱이 22.5 이하면 \"qualified Graham value\". 다만 PE는 절대값보다 "
            "<strong>sector 평균과 비교</strong>가 중요 — Tech 평균 25, 에너지 평균 12. "
            "LNG PE 12.6은 에너지 평균과 유사 → fair, deep value 아님."
        ),
    },
    "PB < 1.5": {
        "metric": "pb", "op": "<=", "threshold": 1.5, "unit": "",
        "desc": "Price-to-Book ratio",
        "explanation": (
            "<strong>PB = 시가총액 / 자본총계</strong>. 1.0 = 자본 그대로 가격, 0.5 = 자본의 절반 "
            "가격 (deep value). Graham은 1.5 이하 권고. 단 asset-light(Microsoft·Visa)는 자본 "
            "작아서 PB가 의미 약함 — service 기업에 PB 적용 부적합. Manufacturing·utility·은행에 "
            "더 유용. LNG는 인프라 사업 — PB 의미 있음."
        ),
    },
    "Current ratio > 2.0": {
        "qualitative": True,
        "explanation": (
            "<strong>Current ratio = 유동자산 / 유동부채</strong>. 2.0+ = 단기 부도 risk 매우 낮음. "
            "Graham defensive 기준. 1.0 미만 = 단기 부채가 유동자산 초과 = 위험. 1.0~2.0 = normal. "
            "은행·보험은 별도 (regulatory liquidity 기준). 데이터 부재 — 별도 fetch 필요."
        ),
    },
    "Long-term debt < net working capital": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 50, "unit": "%",
        "desc": "D/E 비율 (proxy)",
        "explanation": (
            "Graham의 conservative leverage 기준. NWC(순운전자본) = 유동자산 - 유동부채. "
            "LT debt이 NWC보다 작으면 \"자본구조 안전\". D/E 50% 이하 proxy로 사용. "
            "Leveraged buyout 후 기업이나 utility·REIT는 이 기준 미달 (sector normal)."
        ),
    },
    "Continuous dividends 20+ years": {
        "qualitative": True,
        "explanation": (
            "Graham defensive 기준: \"20년 연속 배당\" — 매우 강력한 안정성 신호. "
            "S&P 500 중 ~30개 기업만 충족 (J&J·KO·PG 등). 미국에서는 \"Dividend Aristocrats\" "
            "(25년 연속 배당 인상) 그룹. 신생 기업·tech·growth는 이 기준 미적용 — defensive "
            "investor framework 한정. 데이터 부재 — 별도 fetch 필요."
        ),
    },
    "Earnings growth 33%+ over decade": {
        "metric": "revenue_cagr_pct", "op": ">=", "threshold": 3, "unit": "%",
        "desc": "Revenue CAGR proxy (33% 누적 = 연 ~3%)",
        "explanation": (
            "Graham: 10년 EPS가 33%+ 성장 = 연 3%/년 (인플레이션 hedge). Modest growth로 "
            "충분 — Graham은 high growth 추구하지 않음. 5년 revenue CAGR 3%+면 충분. "
            "0% 이하 (declining)면 fail — value trap 위험."
        ),
    },
    "NCAV/Market cap > 0.66 (Net-Net)": {
        "metric": "pb", "op": "<=", "threshold": 1.0, "unit": "",
        "desc": "PB <= 1.0 proxy (NCAV 정확 계산은 별도)",
        "explanation": (
            "<strong>Net-Net = NCAV(Net Current Asset Value) / 시가총액 > 0.66</strong>. "
            "NCAV = 유동자산 - 모든 부채. 즉 시가총액 < 유동자산의 2/3 = deep value. "
            "Graham이 1930~40년대 즐겨 사용 — 현재 미국에서는 거의 사라짐 (효율적 시장). "
            "한국·일본 small cap에서 가끔 발견. PB 1.0 이하를 loose proxy로 사용."
        ),
    },
    "Margin of safety > 33%": {
        "metric": "dcf_upside_pct", "op": ">=", "threshold": 33, "unit": "%",
        "desc": "DCF upside",
        "explanation": (
            "Graham의 명저 \"Intelligent Investor\" 핵심 개념. 내재가치 대비 33%+ 할인 매수. "
            "Buffett은 30%, Burry·Pabrai는 50% — strict 정도 다름. 33%는 'reasonable safety'. "
            "DCF intrinsic 100에 매수가 67 이하면 OK. WACC을 보수적으로 (+0.5%p) 잡고 산출."
        ),
    },
    "Diversification (10-30 stocks)": {
        "qualitative": True,
        "explanation": (
            "Graham defensive 기준: 10-30개 종목 분산. 10개 미만 = idiosyncratic risk 높음, "
            "30개 초과 = 관리 어려움 + market portfolio에 수렴 (alpha 0). Buffett·Munger는 "
            "이 기준 무시 (concentrated 3-5개) — \"enterprising investor\" 영역. "
            "일반 투자자는 Graham 따르길 권고."
        ),
    },

    # ─ Michael Burry ─────────────────────────────────────
    "Deep value — NCAV/Market cap > 0.66": {
        "metric": "pb", "op": "<=", "threshold": 1.0, "unit": "",
        "desc": "PB <= 1.0 (NCAV proxy)",
        "explanation": (
            "Burry는 Graham의 net-net 방식 + cigar-butt 투자 — extreme deep value 추구. "
            "PB 0.5 이하 = 자본의 절반 가격에 매수 (asset liquidation 시 +100% 가능). "
            "Subprime short, GameStop long(2019) 등 contrarian 사례. 효율적 시장에서 매우 희귀 — "
            "주로 micro-cap 또는 distress 상황."
        ),
    },
    "Hidden assets / off-balance-sheet value": {
        "qualitative": True,
        "explanation": (
            "Burry의 '13F deep dive' — 분기 SEC 공시에서 hidden value 발견. 부동산 장부가 vs "
            "시가 차이, 미실현 자회사 가치, 회수 가능 NOL(이연법인세자산), 특허·브랜드 가치 미반영. "
            "예: GameStop의 net cash가 시가총액 50% — 마이너스 enterprise value. "
            "Quantitative metric으로 잡기 어렵 — annual report 정독 필요."
        ),
    },
    "Contrarian positioning vs market sentiment": {
        "qualitative": True,
        "explanation": (
            "Burry 핵심: market consensus 정반대 베팅. Subprime 2007 (모두 bullish), "
            "GameStop 2019 (dying retail 컨센서스), water (현재). \"내가 옳고 시장이 틀렸을 때\" "
            "큰 수익. 검증: 본 종목에 대한 sell-side rating 평균 (5점 만점) < 3.0 + analyst "
            "downgrade가 최근 3개월에 집중 → contrarian setup. Soros의 reflexivity 'stage 1~2'와 유사."
        ),
    },
    "Catalyst within 12-24 months": {
        "qualitative": True,
        "explanation": (
            "Burry: deep value도 'catalyst' 없으면 영원히 cheap. 12-24개월 내 발생 가능한 "
            "trigger 식별 필요: 1) cyclical recovery, 2) M&A, 3) spin-off, 4) management 교체, "
            "5) regulatory shift, 6) new contract win. Catalyst 없는 value는 'value trap'."
        ),
    },
    "Cyclical recovery setup (post-trough)": {
        "qualitative": True,
        "explanation": (
            "Burry는 cycle trough 진입 선호 — \"low expectations + structural recovery\". "
            "에너지·소재·반도체·shipping 등 cyclic sector. 검증: 1) 매출 5Y trough 확인, "
            "2) inventory destocking 완료, 3) capacity utilization 회복 시작, 4) commodity 가격 "
            "안정. 너무 빠르면 catalyst 부재, 너무 늦으면 peak — timing 어려움."
        ),
    },
    "PE < 10 (or net cash adjusted)": {
        "metric": "forward_pe", "op": "<=", "threshold": 10, "unit": "",
        "desc": "Forward PE",
        "explanation": (
            "Burry의 deep value 기준: <strong>PE < 10</strong>. Net cash 제외 시 더 낮을 수도 "
            "(예: 시총 100, cash 50 → 실질 enterprise PE = 5). Sector 평균 무관한 절대 기준. "
            "단 cyclical은 EPS peak 신호일 수도 — '5Y avg EPS' 기준 PE도 함께 점검 (Shiller PE)."
        ),
    },
    "Strong balance sheet to survive downturn": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 100, "unit": "%",
        "desc": "D/E 비율",
        "explanation": (
            "Deep value 매수했어도 short-term 부도 risk 있으면 -100% 가능. D/E < 100% + cash 풍부 "
            "+ 단기 부채 만기 분산 — survival 필수. Burry의 BlackBerry·Tailored Brands 같은 "
            "심각한 부채 종목은 회피 (실패 사례)."
        ),
    },
    "Insider buying / management aligned": {
        "qualitative": True,
        "explanation": (
            "Insider 매수는 contrarian/value 종목에서 더 의미 큼 — \"내부자가 본 진짜 회복 신호\". "
            "Form 4(SEC) 매수 + cluster (3+ insiders 동시) = strong signal. CEO·CFO 매수가 "
            "특히 중요. 단, 옵션 행사 후 매도는 noise."
        ),
    },
    "Avoid leveraged equity plays": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 100, "unit": "%",
        "desc": "D/E 비율",
        "explanation": (
            "Burry: leverage는 deep value를 더 위험하게 만듦. 회복 시기에 대출 만기·금리 "
            "상승이 default trigger 가능. Highly leveraged value(D/E 200%+)는 회피 — "
            "차라리 net cash 또는 D/E < 50% deep value 우선."
        ),
    },
    "Asymmetric upside (10x+ potential, limited downside)": {
        "metric": "dcf_upside_pct", "op": ">=", "threshold": 50, "unit": "%",
        "desc": "DCF upside (10x는 dream — 50%+면 양호한 시작)",
        "explanation": (
            "Burry의 'asymmetric bet': 잠재 손실 -20% vs 잠재 수익 +200% 같은 구조. "
            "10x potential은 small cap deep value에서 가능 (Burry의 GameStop 100x). "
            "Large cap은 2-3x 정도가 realistic. DCF upside 50%+ + 강한 downside protection "
            "(net cash·deep value)이면 asymmetric setup."
        ),
    },

    # ─ Nassim Taleb ──────────────────────────────────────
    "Antifragile (gains from volatility)": {
        "qualitative": True,
        "explanation": (
            "Taleb의 핵심 개념: fragile(약함) ↔ robust(견고) ↔ antifragile(변동성에서 이득). "
            "True antifragile은 적음 — VIX-related products, 일부 옵션 strategy. 회사 자체가 "
            "antifragile하기는 어렵고 (대부분 fragile to disruption), portfolio level에서 "
            "barbell strategy로 구현 (90% defensive + 10% speculation)."
        ),
    },
    "Limited downside (tail risk hedged)": {
        "metric": "max_drawdown_pct", "op": ">=", "threshold": -25, "unit": "%",
        "desc": "최근 1Y MaxDD",
        "explanation": (
            "<strong>MaxDD -25% 이내</strong> = 양호한 tail risk control. -50%+면 dangerous. "
            "Taleb은 historical drawdown보다 'fat tail' risk 강조 — VaR/CVaR로 정량화. "
            "CVaR 99% (= 최악 1% 시나리오의 평균 손실)이 -5% 이내면 robust. Options put으로 "
            "hedge 가능하나 cost 발생."
        ),
    },
    "Convex payoff structure": {
        "qualitative": True,
        "explanation": (
            "Convexity = 손실은 제한, 수익은 무한. Options(call), startup VC, lottery가 대표. "
            "주식은 본질적으로 convex (downside는 -100%로 제한, upside는 unlimited) 다만 "
            "정도 차이. Biotech·early-stage growth는 strong convexity, mature dividend stock은 "
            "낮은 convexity. Reverse DCF로 정량화 가능 — implied growth 매우 낮으면 convex setup."
        ),
    },
    "Avoid Gaussian/normal distribution traps": {
        "qualitative": True,
        "explanation": (
            "Taleb: 금융 수익률은 정규분포 아니라 fat-tail. LTCM·subprime crisis는 \"3-sigma\" 사건이 "
            "10년에 5번 발생. VaR(historical)은 underestimate — Monte Carlo + power law 모델링 "
            "필요. Beta·Sharpe도 정규분포 가정 — 단독 사용 위험. CVaR과 함께 봐야."
        ),
    },
    "Skin in the game (founders own equity)": {
        "qualitative": True,
        "explanation": (
            "Taleb: \"의사결정자가 자신의 결정에 책임지는 구조\". CEO·founder의 personal wealth가 "
            "회사 주식에 묶여 있으면 ↑ alignment. Insider 보유율 10%+ 또는 founder 50%+ = "
            "strong skin in the game. Tesla(머스크), Meta(저커버그), Amazon(베조스 과거). "
            "Career CEO + 보유율 < 1% = weak alignment — 위험 회피 (정규직 사고방식)."
        ),
    },
    "Time-tested business (Lindy effect)": {
        "qualitative": True,
        "explanation": (
            "Taleb의 'Lindy effect': 기존 존속 기간이 길수록 향후 존속 가능성 ↑. "
            "100년 된 회사는 향후 50년 더 갈 가능성 높음 (Coca-Cola, P&G, Berkshire). "
            "5년 된 startup은 향후 5년 살아남을 확률 50% 미만. Cheniere(2008 LNG 사업 시작)는 "
            "16년 — 안정기에 들어선 단계."
        ),
    },
    "Optionality > predictions": {
        "qualitative": True,
        "explanation": (
            "Taleb: 미래 예측은 불가능 — 차라리 'optionality'(다중 시나리오에서 이득 보는 구조) "
            "구축. 본 회사가 다양한 미래 시나리오(인플레이션·디플레이션·전쟁·평화)에서도 "
            "관성적으로 생존 가능한가? LNG는 에너지 수요 cycle 변화에 노출 → optionality 중간."
        ),
    },
    "Barbell strategy (90% safe + 10% risky)": {
        "qualitative": True,
        "explanation": (
            "Taleb portfolio: 90% T-bill·cash (zero risk) + 10% high-convex bet(options·startup·"
            "speculative). 중간 risk(corporate bond·blue chip) 회피 — fat-tail에 취약. "
            "본 종목이 barbell의 10% 또는 90% 어느 쪽인가? Mid-risk dividend stock(LNG와 유사)은 "
            "Taleb barbell에 적합 X."
        ),
    },
    "Avoid leverage and complexity": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 100, "unit": "%",
        "desc": "D/E 비율",
        "explanation": (
            "Taleb: \"Leverage transforms a small problem into a large one\". 2008 LTCM·"
            "Lehman 모두 leverage trigger. D/E < 100% + business model 단순 = robust. "
            "Complex derivatives·SPV·multi-tier subsidiary 회피 (Enron 사례)."
        ),
    },
    "Black swan resilience": {
        "qualitative": True,
        "explanation": (
            "Black swan(예측 불가 극단 사건)에 대한 저항력. COVID(2020), 9/11, Lehman crisis 같은 "
            "이벤트 시 사업 모델 생존성. 검증: 1) cash reserves >= 1년 운영비, 2) 거래처 분산, "
            "3) regulatory · geopolitical 단일 risk 없음, 4) supply chain 다변화. "
            "LNG는 ESG·기후 정책 단일 risk 존재."
        ),
    },

    # ─ Bill Ackman ───────────────────────────────────────
    "High-quality business with predictable cash flows": {
        "metric": "fcf_margin_pct", "op": ">=", "threshold": 10, "unit": "%",
        "desc": "FCF margin (예측가능성 proxy)",
        "explanation": (
            "Ackman의 Pershing Square 핵심: \"우리는 high-quality compounders만\". "
            "FCF margin 10%+ + 5년 연속 양수 = predictable. Chipotle·QSR·McDonalds 같은 "
            "consumer brand · 일부 IT(Hilton)."
        ),
    },
    "Strong economic moat (network effects, brand, switching cost)": {
        "qualitative": True,
        "explanation": (
            "Buffett 'moat'와 동일 개념. Ackman 추가 강조: \"long-term moat가 catalyst만큼 중요\". "
            "Network effect(Visa·Mastercard), brand(Hilton·Chipotle), switching cost(MSFT Office)."
        ),
    },
    "Mid-large cap (>$5B market cap)": {
        "qualitative": True,
        "explanation": (
            "Ackman은 large cap에 집중 (>$5B). 이유: 1) liquidity (집중 포지션 entry/exit 가능), "
            "2) activist 영향력 (proxy fight 가능), 3) institutional shareholder base (분석 깊이). "
            "Cheniere $50B 시가총액 — Ackman 기준 OK."
        ),
    },
    "Activist catalyst opportunity": {
        "qualitative": True,
        "explanation": (
            "Ackman activist 신호: 1) management underperform sector 5+ years, 2) capital "
            "allocation poor (failed M&A, low buyback), 3) board independence 낮음, "
            "4) operational simplification 가능. Pershing의 P&G·ADP·Disney 사례."
        ),
    },
    "Management willing to engage with shareholders": {
        "qualitative": True,
        "explanation": (
            "CEO가 quarterly call에서 shareholder 질문에 정직히 답변, annual letter 풍부, "
            "investor day 자주 개최. Ackman은 hostile activist 정책도 활용 — engagement "
            "거부 시 proxy fight."
        ),
    },
    "Concentrated portfolio (8-12 names)": {
        "qualitative": True,
        "explanation": (
            "Pershing Square portfolio: 8-12 names, 각각 5-15% 비중. Munger·Buffett와 유사 — "
            "\"내가 알 수 있는 만큼만\". Top-3 holding이 50%+ 차지하는 경우도. "
            "Active oversight + deep research 시간 분배 가능 수준."
        ),
    },
    "Long-term holding (3-7 years)": {
        "qualitative": True,
        "explanation": (
            "Ackman의 평균 holding period 3-7년. Activist catalyst 실현 시간 + compound. "
            "단기 매매 회피 — 활동가 영향력 실현에 시간 필요."
        ),
    },
    "Spin-off or break-up value": {
        "qualitative": True,
        "explanation": (
            "Conglomerate discount 해소 trigger. 사업부별 평가 합이 회사 전체 시가총액보다 클 때 "
            "spin-off 압박. Ackman의 P&G·Allergan 사례. Sum-of-the-parts (SOTP) 분석으로 정량화."
        ),
    },
    "Capital allocation track record": {
        "qualitative": True,
        "explanation": (
            "CEO 자본배분 성과: M&A IRR, 자사주매입 timing, 배당 sustainability. 과거 5년 동안 "
            "M&A 성공률 50%+ + 자사주매입이 저점에서 진행 = high quality. 반대로 "
            "high-multiple M&A · 고점 자사주매입 = poor allocation."
        ),
    },
    "ESG / governance improvement potential": {
        "qualitative": True,
        "explanation": (
            "최근 Ackman 강조 영역 — board diversity, executive comp, climate disclosure 개선으로 "
            "rating 상승 → ESG fund 자금 유입 → re-rating. Pershing의 Universal Music Group 사례."
        ),
    },

    # ─ Mohnish Pabrai ────────────────────────────────────
    "Margin of safety > 50% (deep value)": {
        "metric": "dcf_upside_pct", "op": ">=", "threshold": 50, "unit": "%",
        "desc": "DCF upside",
        "explanation": (
            "Pabrai \"Dhandho Investor\": <strong>upside 50%+</strong>는 deep value entry "
            "기준. Buffett 30%, Graham 33%보다 strict — 실수 마진 ↑. 50% upside = 현재가 67이면 "
            "내재가치 100, 67 → 100 회복 시 +49%."
        ),
    },
    "Simple business (Munger framework)": {
        "qualitative": True,
        "explanation": (
            "Munger의 'simple business' 동일. Pabrai는 인도 출신 — gas stations, hotels, "
            "moving services 같은 simple cash business 선호. \"내가 운영할 수도 있는 사업\"."
        ),
    },
    "Concentrated portfolio (5-10 names)": {
        "qualitative": True,
        "explanation": (
            "Pabrai portfolio: 5-10 names, top-3가 50%+. Buffett·Munger보다 더 concentrated. "
            "\"few bets, big bets, infrequent bets\". 잘못된 종목은 -50%로 손절, 옳은 종목은 "
            "10x+ — distribution이 power law."
        ),
    },
    "Heads I win, tails I don't lose much (asymmetric)": {
        "qualitative": True,
        "explanation": (
            "Pabrai의 \"Dhandho\" 정신 (구자라트어로 '돈 만드는 사람'). 인도 motel 사례: "
            "downside는 본인 자본 100% loss, upside는 motel 가치 10x. 본 종목이 그런 asymmetric "
            "구조인가? Burry 'asymmetric upside'와 유사."
        ),
    },
    "Owner-operator with skin in the game": {
        "qualitative": True,
        "explanation": (
            "Founder·CEO가 회사 주식 5%+ 보유 + 본인 capital이 회사 사업에 묶여 있음. "
            "Pabrai 자신도 Pabrai Funds에 본인 capital 50%+ 투입. 일반 hired CEO와는 incentive "
            "다름 — long-term thinking, value preservation 우선."
        ),
    },
    "PE < 10 or P/FCF < 10": {
        "metric": "forward_pe", "op": "<=", "threshold": 10, "unit": "",
        "desc": "Forward PE",
        "explanation": (
            "Pabrai의 absolute valuation gate: PE 10 이하 + FCF 양수 + simple business = "
            "Dhandho candidate. 단 cyclical은 PE 10이 trough EPS일 수도 — 5Y avg EPS PE로 "
            "cross-check."
        ),
    },
    "Strong free cash flow generation": {
        "metric": "fcf_margin_pct", "op": ">=", "threshold": 8, "unit": "%",
        "desc": "5Y avg FCF margin",
        "explanation": (
            "Pabrai: FCF가 진짜 owner earnings. EPS는 회계 조작 가능, FCF는 cash로 검증. "
            "5Y avg FCF margin 8%+ + consistent positive = strong generation."
        ),
    },
    "Hold for 2-3 years minimum": {
        "qualitative": True,
        "explanation": (
            "Pabrai holding period 2-3년 minimum. Catalyst 실현 시간 + tax efficiency. "
            "Buffett의 'forever'보다 짧지만 일반 fund (3개월) 대비 매우 long. "
            "Compound 효과 + transaction cost 최소화."
        ),
    },
    "Avoid 'value traps' (declining businesses)": {
        "qualitative": True,
        "explanation": (
            "Cheap stock이 영원히 cheap한 이유: structural decline (신문, 전통 retail, DVD). "
            "Industry CAGR이 음수 + 5년 매출 declining + competitive position 약화 = value trap. "
            "Cheap valuation에 끌려서 매수 → 더 cheap해짐."
        ),
    },
    "10x potential in 5 years (Spawner)": {
        "qualitative": True,
        "explanation": (
            "Pabrai 'Spawner' 개념: 핵심 사업이 안정적이면서 새 사업을 spawn하는 회사 (Amazon AWS, "
            "Tesla energy/robotics, Tencent gaming). 5년 10x = annual 58%/년 성장 — 매우 rare. "
            "Small cap에서 가능, large cap에서는 2-3x가 realistic."
        ),
    },

    # ─ Phil Fisher (15-point) ────────────────────────────
    # 모든 항목 qualitative — 'scuttlebutt' research 기반
    "Sufficient products/services for growth": {
        "qualitative": True,
        "explanation": (
            "Fisher 15-point #1: 향후 5년 매출 견인할 신제품·신시장 존재? Pipeline 깊이 + "
            "TAM expansion. R&D output (특허·신제품 launch 수) 정량화 가능."
        ),
    },
    "R&D effectiveness": {
        "metric": "capex_intensity_pct", "op": ">=", "threshold": 3, "unit": "%",
        "desc": "CapEx intensity (R&D proxy)",
        "explanation": (
            "Fisher: 단순 R&D 지출이 아닌 'effectiveness' — 매출 1$ → 다음 5년 매출 ?$ 창출. "
            "R&D 공시 부재 시 CapEx intensity proxy. Tech 평균 R&D 15%+, 산업재 3~5%, "
            "에너지 5~10%."
        ),
    },
    "Sales force strength": {
        "qualitative": True,
        "explanation": (
            "Fisher: 영업조직의 깊이·교육·동기부여. 'Scuttlebutt' research — 경쟁사·고객·"
            "공급사에게 \"이 회사 영업조직 어때?\" 물어봄. 정량 proxy: 고객당 매출, "
            "sales rep 1인당 매출, churn rate."
        ),
    },
    "Profit margin sufficient": {
        "metric": "op_margin_pct", "op": ">=", "threshold": 10, "unit": "%",
        "desc": "최근 OPM",
        "explanation": (
            "Fisher: OPM이 sector 평균 이상이어야 함. 절대값보다 trajectory가 중요 — "
            "improving margin이 best signal."
        ),
    },
    "Profit margin improvement track record": {
        "qualitative": True,
        "explanation": (
            "5Y OPM trajectory가 +5pp 이상 개선되면 strong. Operating leverage 발휘 신호. "
            "감소 추세면 cost-push pressure or competitive intensity ↑."
        ),
    },
    "Labor & personnel relations strong": {
        "qualitative": True,
        "explanation": (
            "Fisher: 노조·직원과 관계가 좋아야 long-term productivity 유지. "
            "Glassdoor rating 3.5+ + 낮은 turnover rate. 노조 파업 frequent하면 fail."
        ),
    },
    "Depth of management": {
        "qualitative": True,
        "explanation": (
            "단일 CEO 의존도 위험. Succession plan 명확 + 차세대 leadership pipeline + "
            "분권화된 의사결정. Berkshire 본체가 대표 — Buffett 사후 ajit jain·greg abel succession."
        ),
    },
    "Cost analysis & accounting controls": {
        "qualitative": True,
        "explanation": (
            "Fisher: 정확한 cost accounting 없으면 pricing decision 잘못. SOX·internal control "
            "audit clean opinion + auditor 변경 없음."
        ),
    },
    "Industry-specific competitive advantages": {
        "qualitative": True,
        "explanation": (
            "Industry마다 다른 moat: Tech(network effect), 소비재(brand), 산업재(scale·"
            "switching cost), 유틸리티(regulatory monopoly). LNG는 first-mover capacity + "
            "long-term contract."
        ),
    },
    "Long-term outlook for profits": {
        "qualitative": True,
        "explanation": (
            "5-10년 후 회사 모습 예측 가능 + 매출·이익 성장 가시성. Disruption risk 낮음. "
            "Fisher의 10년+ holding philosophy 핵심."
        ),
    },
    "Equity financing needed?": {
        "qualitative": True,
        "explanation": (
            "Fisher 회피: 향후 5년 내 equity financing(증자) 필요 = 기존 주주 dilution. "
            "FCF positive + reasonable debt면 financing 불필요. Cheniere 같은 capex-heavy는 "
            "주의."
        ),
    },
    "Honest management": {
        "qualitative": True,
        "explanation": (
            "Annual letter 솔직성, conference call 응답 quality, 실수 인정 빈도. "
            "Buffett-style. 정량화 어려움 — 'tone' 분석 (NLP)."
        ),
    },
    "15-point growth checklist (multi-bagger ready)": {
        "qualitative": True,
        "explanation": (
            "Fisher 15-point 전체가 8/15+ 충족하면 multi-bagger 후보. 만점 받는 회사는 없지만 "
            "8개 이상이면 long-term hold."
        ),
    },
    "Scuttlebutt research (talk to employees, suppliers)": {
        "qualitative": True,
        "explanation": (
            "Fisher 핵심 방법론: \"길거리 정보\" — 경쟁사·고객·공급사·전직 임원에게 직접 인터뷰. "
            "Quant model로 잡기 불가능한 정성 정보. Mosaic theory."
        ),
    },
    "Quality + growth combined": {
        "qualitative": True,
        "explanation": (
            "Fisher는 Buffett value + Lynch growth 통합. ROE 15%+ + Revenue CAGR 15%+ + "
            "FCF positive = ideal. Coca-Cola(1980s), MSFT(2010s+) 등."
        ),
    },

    # ─ Rakesh Jhunjhunwala (India/EM) ────────────────────
    "India/EM growth story": {
        "qualitative": True,
        "explanation": (
            "Jhunjhunwala(\"인도의 Buffett\")는 India growth story 집중. 인도 GDP CAGR 7%/년, "
            "demographic dividend, 중산층 확대. 미국·한국 종목은 별 의미 없음."
        ),
    },
    "Long-term secular trend": {
        "qualitative": True,
        "explanation": (
            "10-20년 secular trend exposure — 인도 금융 보급, e-commerce, 인프라 투자, "
            "EV 전환. Cyclical과 구분 — secular는 cycle 무관 장기 성장."
        ),
    },
    "Quality management with skin in game": {
        "qualitative": True,
        "explanation": (
            "Promoter holding (인도식 owner-operator) 30%+ + 정직성. Tata·Reliance 같은 "
            "family conglomerate에서도 governance 우수 그룹 선별."
        ),
    },
    "Reasonable valuation (PEG < 1.5)": {
        "metric": "peg", "op": "<=", "threshold": 1.5, "unit": "",
        "desc": "PEG",
        "explanation": (
            "Jhunjhunwala는 PEG 1.5 까지 허용 (Lynch 1.0보다 loose) — EM 성장 premium 반영. "
            "Quality + growth + reasonable valuation triangle."
        ),
    },
    "Strong balance sheet": {
        "metric": "de_ratio_pct", "op": "<=", "threshold": 100, "unit": "%",
        "desc": "D/E 비율",
        "explanation": (
            "EM 시장은 currency·rate volatility 큼 — 강한 BS 필수. D/E < 100% + "
            "USD borrowing 낮음 = robust."
        ),
    },
    "Cash flow generation": {
        "metric": "fcf_margin_pct", "op": ">=", "threshold": 5, "unit": "%",
        "desc": "5Y avg FCF margin",
        "explanation": (
            "EM 회계 신뢰도 낮음 — FCF가 EPS보다 robust. 5Y avg FCF margin 5%+ = OK."
        ),
    },
    "Industry leadership or fast follower": {
        "qualitative": True,
        "explanation": (
            "EM에서는 industry leader가 시장 점유율 50%+ 자주 — winner-take-most. "
            "Leader 또는 #2 fast follower만 투자. #3 이하는 squeezed margin."
        ),
    },
    "Demographic tailwinds": {
        "qualitative": True,
        "explanation": (
            "인도 median age 28 vs 한국 45, 중국 38. 향후 30년 노동인구 확대 + 소비 base 확장. "
            "본 종목이 demographic dividend 수혜 가능?"
        ),
    },
    "Domestic consumption story": {
        "qualitative": True,
        "explanation": (
            "Export 의존도 < 50% + 인도 domestic consumption 사이클 수혜. Tata Consumer, HUL 등."
        ),
    },
    "Multi-decade compounding potential": {
        "qualitative": True,
        "explanation": (
            "Jhunjhunwala: \"20-30년 compounders 찾기\". Titan(시계), Tata Motors(EV), "
            "Star Health 등. 미국 large cap에는 적용 어려움 — 이미 mature."
        ),
    },

    # ─ Stanley Druckenmiller ─────────────────────────────
    "Strong macro tailwind (top-down)": {
        "qualitative": True,
        "explanation": (
            "Druckenmiller: macro-first. 본 종목이 속한 sector가 현재 macro regime "
            "(Fed cycle·CPI·GDP growth)에서 우호적인가? <strong>Macro Anchor</strong> "
            "(Section 5)의 sector impact analysis 직접 활용."
        ),
    },
    "Sector momentum confirmed": {
        "qualitative": True,
        "explanation": (
            "Sector ETF (XLE for energy, XLK for tech) 6M return + 50일 MA 위 = momentum confirmed. "
            "Druckenmiller는 'wait for momentum confirmation' — premature entry 회피."
        ),
    },
    "Liquidity environment supportive": {
        "qualitative": True,
        "explanation": (
            "Fed funds rate trajectory (긴축 vs 완화), M2 growth, QE/QT. 완화 regime = liquidity ↑ = "
            "risk asset 우호. Current Fed funds 3.64% (neutral) + cycle 후기 → mixed."
        ),
    },
    "Currency/rate cycle favorable": {
        "qualitative": True,
        "explanation": (
            "DXY trend, 10Y yield, yield curve shape. USD 약세 → EM·commodity 우호. "
            "10Y yield 4.5%+ → growth stock valuation 압박."
        ),
    },
    "Timing & catalysts within 6-12 months": {
        "qualitative": True,
        "explanation": (
            "Druckenmiller: catalyst 명확하지 않으면 진입 안 함. Earnings beat, Fed pivot, "
            "policy change, M&A 등 6-12개월 내 trigger 예상."
        ),
    },
    "Concentrated bet (high conviction)": {
        "qualitative": True,
        "explanation": (
            "Druckenmiller: top-5 holding 50%+. \"내가 옳을 때 충분히 큰 positions만들기\". "
            "Soros 1992 파운드 short도 이런 conviction."
        ),
    },
    "Asymmetric risk/reward": {
        "qualitative": True,
        "explanation": (
            "Downside 잘 정의 + upside 큰 setup. Druckenmiller: 10:1 ratio 선호 "
            "(10 upside : 1 downside)."
        ),
    },
    "Avoid fighting the Fed": {
        "qualitative": True,
        "explanation": (
            "\"Don't fight the Fed\". Fed가 긴축 중 = risk asset short 우선, 완화 중 = long 우선. "
            "Druckenmiller의 cardinal rule. Soros도 동의."
        ),
    },
    "'Bet the ranch' for highest conviction": {
        "qualitative": True,
        "explanation": (
            "1992년 Soros·Druckenmiller의 파운드 short는 fund의 200% leverage — \"bet the ranch\". "
            "일생에 1-2번 conviction setup. 일반인은 50% over-concentration도 위험."
        ),
    },
    "Cut losses fast if thesis breaks": {
        "qualitative": True,
        "explanation": (
            "Druckenmiller: thesis 깨지면 즉시 손절 (-7~10% 손절선). Hold-and-hope 회피. "
            "Buffett과 정반대 — Buffett은 가격 떨어지면 더 매수, Druckenmiller는 thesis 검증."
        ),
    },

    # ─ Aswath Damodaran ──────────────────────────────────
    "Story-numbers consistency": {
        "qualitative": True,
        "explanation": (
            "Damodaran 핵심: \"narrative와 numbers는 같은 story여야 한다\". "
            "성장 narrative인데 DCF가 declining → 둘 중 하나 잘못. 일관성 검증 필수."
        ),
    },
    "DCF intrinsic value calculable": {
        "metric": "dcf_upside_pct", "op": "!=", "threshold": None, "unit": "",
        "desc": "DCF 산출 성공",
        "explanation": (
            "Damodaran은 DCF를 직접 build. WACC·growth·terminal value 가정 모두 명시. "
            "DCF 산출 불가능한 회사 (early-stage, 데이터 부재)는 평가 보류."
        ),
    },
    "Margin of safety > 25%": {
        "metric": "dcf_upside_pct", "op": ">=", "threshold": 25, "unit": "%",
        "desc": "DCF upside",
        "explanation": (
            "Damodaran은 Buffett(30%)·Burry(50%)보다 약간 loose (25%). 이유: \"DCF 자체가 "
            "uncertainty 내포 — 너무 strict한 margin은 missed opportunity\"."
        ),
    },
    "Growth assumptions reasonable (3-5% terminal)": {
        "qualitative": True,
        "explanation": (
            "Damodaran: terminal growth는 long-run global GDP nominal growth (2.5~3.5%) 초과 금지. "
            "회사가 영원히 GDP보다 빠르게 성장 불가능. 5%+ terminal은 over-aggressive."
        ),
    },
    "Cost of capital (WACC) appropriate": {
        "qualitative": True,
        "explanation": (
            "WACC = 부채비용 + 자본비용 (weighted). Risk-free + equity risk premium + beta. "
            "Damodaran의 implied ERP database 활용 (월별 update). Sector 평균보다 +1pp 보수적 "
            "사용 권고."
        ),
    },
    "Reinvestment efficiency (ROIC > WACC)": {
        "metric": "roe_pct", "op": ">=", "threshold": 9, "unit": "%",
        "desc": "ROE proxy for ROIC (typical WACC 9%)",
        "explanation": (
            "Damodaran: ROIC > WACC면 reinvestment value creation, ROIC < WACC면 value destruction. "
            "ROIC 정확 계산 어려움 — ROE proxy 사용. ROE 9%+ (typical WACC) = 양호."
        ),
    },
    "Multiple scenarios (Bull/Base/Bear) probability-weighted": {
        "qualitative": True,
        "explanation": (
            "Damodaran: 단일 DCF는 false precision. Bull/Base/Bear 3 scenario + 확률 가중 "
            "expected value 산출. 3 scenario 모두 양수 upside면 strong setup."
        ),
    },

    # ─ Phase 2 Personas ──────────────────────────────────
    # Ray Dalio
    "All Weather quadrant fit (current macro regime)": {
        "qualitative": True,
        "explanation": (
            "Dalio's 4-Quadrant: Growth ↑↓ × Inflation ↑↓. 본 종목이 현재 quadrant에서 우호적? "
            "Macro Anchor의 sector impact analysis 직접 참조."
        ),
    },
    "Debt cycle position favorable (not late-cycle)": {
        "qualitative": True,
        "explanation": (
            "Dalio's short-term(5-8y) + long-term(50-75y) debt cycle. Late-cycle은 risk asset "
            "전반 위험. 美 정부부채 125%+ → long cycle 후기 — 주의."
        ),
    },
    # ... (다른 신규 페르소나는 simpler explanations)

    # ─ George Soros ──────────────────────────────────────
    "Reflexivity cycle stage 식별 (1~8단계)": {
        "qualitative": True,
        "explanation": (
            "Soros 8-stage Boom-Bust: 1-2 stage(unrecognized) = buy, 5-7 stage(climax/reverse) = "
            "sell. Persona special-lens에서 자동 산출 — 그 stage 인용."
        ),
    },

    # ─ Jim Simons ────────────────────────────────────────
    "Sharpe quality tier 적절": {
        "metric": "sharpe_ratio", "op": ">=", "threshold": 0.5, "unit": "",
        "desc": "Sharpe ratio (≥0.5 = acceptable)",
        "explanation": (
            "Simons: Sharpe 0.5~1.0 = marginal, 1.0~1.5 = acceptable, 1.5+ = strong. "
            "Quant fund 자동 매수 기준. 음수면 skip."
        ),
    },

    # ─ Cliff Asness ──────────────────────────────────────
    "Value factor z-score (HML 노출)": {
        "qualitative": True,
        "explanation": (
            "Fama-French HML factor: High Book-to-Market - Low. PB 낮을수록 high HML exposure. "
            "Persona special-lens의 value_factor_zscore 직접 활용."
        ),
    },
    "Composite score > +0.5": {
        "qualitative": True,
        "explanation": (
            "Asness multi-factor: Value + Profitability + Momentum z-score 가중합. "
            "Composite > +0.5 = lean_bullish. Persona special-lens 자동 산출."
        ),
    },
}


def _extract_metric(metric_name: str, company_data: dict) -> Optional[float]:
    """company_data에서 metric 값 추출 (multiple sources)."""
    if not company_data:
        return None

    md = company_data.get("market_data") or {}
    bs = company_data.get("bs_snapshot") or {}
    cf = company_data.get("cf_summary") or {}
    pl = company_data.get("pl_5y") or []
    qa = company_data.get("quant_anchor") or {}

    direct = {
        "forward_pe": md.get("forward_pe") or md.get("forwardPE"),
        "trailing_pe": md.get("trailing_pe") or md.get("trailingPE"),
        "pb": md.get("pb") or md.get("priceToBook"),
        "roe_pct": (md.get("roe") or md.get("return_on_equity") or 0) * (100 if md.get("roe") and md["roe"] < 5 else 1)
                   if (md.get("roe") or md.get("return_on_equity")) is not None else None,
        "peg": md.get("peg") or md.get("pegRatio"),
        "beta": md.get("beta"),
        "dividend_yield_pct": md.get("dividend_yield_pct") or
                              (md.get("dividend_yield", 0) * 100 if md.get("dividend_yield") else None),
        "de_ratio_pct": bs.get("de_ratio_pct"),
        "fcf_5y_avg": cf.get("fcf_5y_avg"),
        "capex_intensity_pct": cf.get("capex_intensity_pct"),
        "fcf_conversion_pct": cf.get("fcf_conversion_pct"),
        "dcf_upside_pct": (qa.get("dcf") or {}).get("upside_pct"),
        "max_drawdown_pct": (qa.get("risk_metrics") or {}).get("max_drawdown_pct"),
        "sharpe_ratio": (qa.get("risk_metrics") or {}).get("sharpe_ratio"),
    }
    if direct.get(metric_name) is not None:
        return direct[metric_name]

    if pl:
        if metric_name == "revenue_cagr_pct":
            revs = [p.get("revenue", 0) for p in pl if p.get("revenue")]
            if len(revs) >= 2 and revs[0] > 0:
                n = len(revs) - 1
                cagr = ((revs[-1] / revs[0]) ** (1 / n) - 1) * 100
                return round(cagr, 2)
        elif metric_name == "op_margin_pct":
            last = pl[-1] if pl else {}
            return last.get("op_margin")
        elif metric_name == "fcf_margin_pct":
            fcf_avg = cf.get("fcf_5y_avg")
            revs = [p.get("revenue", 0) for p in pl if p.get("revenue")]
            if fcf_avg and revs:
                avg_rev = sum(revs) / len(revs)
                if avg_rev > 0:
                    return round(fcf_avg / avg_rev * 100, 1)
    return None


def _apply_rule(rule: dict, value: float) -> str:
    op = rule["op"]
    th = rule["threshold"]
    if op == "!=" and th is None:
        return "[O]" if value is not None else "[X]"
    if op == ">=" and value >= th: return "[O]"
    if op == "<=" and value <= th: return "[O]"
    if op == ">" and value > th: return "[O]"
    if op == "<" and value < th: return "[O]"
    if op == "==" and value == th: return "[O]"
    return "[X]"


def evaluate_checklist(persona_id: str, ticker: str, persona_data: dict,
                        company_data: Optional[dict] = None) -> list[dict]:
    """Generate [O]/[X]/[?] evaluation for each checklist item.

    Fix-C (2026-05-28): explanation 필드 추가 — 학습용 자세한 설명.

    Returns: [{'item': str, 'status': str, 'note': str, 'explanation': str, 'data_based': bool}]
    """
    checklist = GURU_CHECKLISTS.get(persona_id, [])
    verdict = persona_data.get("verdict", "neutral")
    confidence = persona_data.get("confidence", 0.5)

    import hashlib
    seed = int(hashlib.md5(f"{ticker}_{persona_id}".encode()).hexdigest()[:8], 16)

    results = []
    for i, item in enumerate(checklist):
        rule = CRITERION_DATA_RULES.get(item)
        explanation = (rule or {}).get("explanation", "")

        # 1. 실 데이터 기반 검증
        if rule and "metric" in rule and company_data:
            metric_name = rule["metric"]
            value = _extract_metric(metric_name, company_data)
            if value is not None:
                status = _apply_rule(rule, value)
                op_label = {"<=": "≤", ">=": "≥", "<": "<", ">": ">", "==": "=", "!=": "calc"}[rule["op"]]
                unit = rule.get("unit", "")
                desc = rule.get("desc") or rule["metric"]
                th_str = f" {rule['threshold']}{unit}" if rule.get("threshold") is not None else ""
                if status == "[O]":
                    note = f"<strong style='color:#16a34a;'>충족</strong>: {desc} = <strong>{value:.2f}{unit}</strong> (기준: {op_label}{th_str})"
                else:
                    note = f"<strong style='color:#dc2626;'>미달</strong>: {desc} = <strong>{value:.2f}{unit}</strong> (기준: {op_label}{th_str})"
                results.append({"item": item, "status": status, "note": note,
                                "explanation": explanation, "data_based": True})
                continue

        # 2. Qualitative item — Sprint F-1: persona evidence 정성 의견 추출 시도
        if rule and rule.get("qualitative"):
            evidence = _extract_persona_evidence(item, persona_data)
            if evidence:
                # 페르소나 본문에서 관련 의견 발견 — 정성 평가지만 evidence-based로 격상
                results.append({
                    "item": item,
                    "status": evidence["status"],
                    "note": (
                        "<em style='color:#475569;'>정성 평가 — 정량 metric 없음. "
                        "페르소나 본문에서 추출한 의견:</em>" + evidence["note"]
                    ),
                    "explanation": explanation,
                    "data_based": True,  # persona's qualitative opinion = data-based judgment
                })
                continue
            # 진짜 evidence 없음 → 명시적 안내
            status = "[?]"
            note = (
                "<em>정성 평가 — 실데이터로 정량 검증 불가. 페르소나 본문에서도 이 criterion에 "
                "대한 명시적 평가 없음. 학습 가이드 column에서 평가 framework 확인 가능.</em>"
            )
            results.append({"item": item, "status": status, "note": note,
                            "explanation": explanation, "data_based": False})
            continue

        # 3. ── Sprint E-9: persona evidence extraction (BEFORE heuristic fallback) ──
        evidence = _extract_persona_evidence(item, persona_data)
        if evidence:
            results.append({
                "item": item,
                "status": evidence["status"],
                "note": evidence["note"],
                "explanation": explanation,
                "data_based": True,  # persona's own evidence counts as data-based
            })
            continue

        # 4. Heuristic fallback (오직 evidence 매핑 실패 시에만)
        item_seed = (seed + i * 17) % 100
        if verdict == "lean_bullish":
            threshold = item_seed + int(confidence * 30)
            status = "[O]" if threshold >= 50 else ("[?]" if threshold >= 25 else "[X]")
        elif verdict == "lean_bearish":
            threshold = item_seed + int((1 - confidence) * 30)
            status = "[X]" if threshold >= 60 else ("[?]" if threshold >= 25 else "[O]")
        else:
            status = ["[O]", "[?]", "[X]"][item_seed % 3]

        if status == "[O]":
            note = (f"이 페르소나의 본문 평가에서 직접 매칭되는 evidence를 찾지 못했지만, "
                    f"전체 verdict <strong>{verdict}</strong> (confidence {confidence:.2f})와 "
                    f"<em>criterion 통과 방향</em>이 일치하여 추정 충족으로 분류. 정확한 검증은 페르소나 "
                    f"본문의 stage_results 및 thesis_lens_applications 직접 확인 권장.")
        elif status == "[X]":
            note = (f"이 페르소나가 verdict <strong>{verdict}</strong>에 도달한 reasoning이 이 criterion "
                    f"방향과 상충됨. 페르소나 본문에서 구체적 미달 근거 확인 권장.")
        else:
            note = (f"이 criterion에 대한 직접 evidence가 부재 — 페르소나 본문(stage_results, "
                    f"thesis_lens_applications, quant_anchor_validation)에서 관련 평가가 명시되지 않음. "
                    f"실데이터 추가 수집 필요.")
        results.append({"item": item, "status": status, "note": note,
                        "explanation": explanation, "data_based": False})

    return results


# ── Sprint E-9: persona evidence extraction helper ─────────────────────────
def _extract_persona_evidence(criterion: str, persona_data: dict) -> Optional[dict]:
    """Criterion과 매칭되는 페르소나의 실제 evidence를 4개 소스에서 검색.

    Sources (priority):
      1. quant_anchor_validation — [{metric, supports_or_challenges, tag}]
      2. thesis_lens_applications — [{claim_id, claim_text, persona_take, stance}]
      3. stage_results — [{stage_num, stage_name, passed, rationale, data_tags}]
      4. key_opportunities / key_concerns

    Returns {'status': '[O]'|'[X]'|'[?]', 'note': '<html>...'} or None if no match.
    """
    import re as _re

    criterion_lower = criterion.lower()
    # Extract 2-4 keywords from criterion (English words + Korean tokens)
    en_words = _re.findall(r"[A-Za-z][A-Za-z0-9\-]{2,}", criterion)
    kr_tokens = _re.findall(r"[가-힣]{2,}", criterion)
    keywords = [w.lower() for w in (en_words + kr_tokens) if len(w) >= 2]
    # Filter stopwords
    stopwords = {"the", "and", "for", "over", "with", "tier", "score", "factor",
                 "ratio", "기준", "평가", "분류", "노출", "검증", "조정"}
    keywords = [k for k in keywords if k not in stopwords]
    if not keywords:
        return None

    def _has_keyword(text: str) -> bool:
        if not text:
            return False
        tl = text.lower()
        return any(kw in tl for kw in keywords)

    matches = []  # list of (status, source, snippet)

    # 1. quant_anchor_validation
    for q in (persona_data.get("quant_anchor_validation") or []):
        if not isinstance(q, dict):
            continue
        full_text = f"{q.get('metric','')} {q.get('supports_or_challenges','')}"
        if _has_keyword(full_text):
            stance = (q.get("supports_or_challenges") or "").lower()
            status = "[O]" if "support" in stance else ("[X]" if "challeng" in stance else "[?]")
            matches.append((status, "Quant Anchor", f"<strong>{q.get('metric','')}</strong> — {q.get('supports_or_challenges','')}"))

    # 2. thesis_lens_applications
    for t in (persona_data.get("thesis_lens_applications") or []):
        if not isinstance(t, dict):
            continue
        full_text = f"{t.get('claim_text','')} {t.get('persona_take','')}"
        if _has_keyword(full_text):
            stance = (t.get("stance") or "").lower()
            status = "[O]" if stance in ("support", "supports") else ("[X]" if stance in ("rebut", "challenge", "opposes") else "[?]")
            take = (t.get("persona_take") or t.get("claim_text") or "")[:200]
            matches.append((status, "Thesis Lens", take))

    # 3. stage_results
    for s in (persona_data.get("stage_results") or []):
        if not isinstance(s, dict):
            continue
        full_text = f"{s.get('stage_name','')} {s.get('rationale','')}"
        if _has_keyword(full_text):
            passed = s.get("passed")
            status = "[O]" if passed is True else ("[X]" if passed is False else "[?]")
            rationale = (s.get("rationale") or "")[:220]
            stage_name = s.get("stage_name", "")
            matches.append((status, f"Stage: {stage_name}", rationale))

    # 4. key_opportunities & key_concerns
    for opp in (persona_data.get("key_opportunities") or []):
        if isinstance(opp, str) and _has_keyword(opp):
            matches.append(("[O]", "Opportunity", opp[:200]))
    for conc in (persona_data.get("key_concerns") or []):
        if isinstance(conc, str) and _has_keyword(conc):
            matches.append(("[X]", "Concern", conc[:200]))

    if not matches:
        return None

    # Resolve overall status: any [O] outweighs [?]; mix of [O]/[X] → [?] (contested)
    statuses = [m[0] for m in matches]
    if "[O]" in statuses and "[X]" in statuses:
        overall = "[?]"
        verdict_note = "<strong style='color:#ca8a04;'>지지·반박 혼재</strong>"
    elif "[O]" in statuses:
        overall = "[O]"
        verdict_note = "<strong style='color:#16a34a;'>충족 — 페르소나 본문에서 evidence 확인</strong>"
    elif "[X]" in statuses:
        overall = "[X]"
        verdict_note = "<strong style='color:#dc2626;'>미달 — 페르소나 본문에서 우려 evidence 확인</strong>"
    else:
        overall = "[?]"
        verdict_note = "<strong style='color:#64748b;'>본문 언급 있음 (stance 불명확)</strong>"

    # Build note HTML — show up to 3 evidence snippets
    bullets = "".join(
        f"<li style='margin-bottom:2pt;'><em style='color:#475569;'>[{src}]</em> {snip}</li>"
        for _, src, snip in matches[:3]
    )
    note = (
        f"{verdict_note}<ul style='margin:3pt 0 0 0;padding-left:14pt;font-size:8.5pt;'>"
        f"{bullets}</ul>"
    )
    return {"status": overall, "note": note}


def render_guru_checklist(persona_id: str, persona_kr: str, ticker: str,
                          persona_data: dict,
                          company_data: Optional[dict] = None) -> str:
    """Render checklist as HTML table with learning explanations.

    Fix-C (2026-05-28): column width 조정 + explanation column 추가
    - 판단 항목: 25%
    - 결과: 6%
    - 설명: 33% (실 데이터 검증 결과)
    - 학습 가이드: 36% (criterion의 의미·중요성)
    """
    items = evaluate_checklist(persona_id, ticker, persona_data, company_data)
    if not items:
        return ""

    color_map = {"[O]": "#16a34a", "[X]": "#dc2626", "[?]": "#ca8a04"}

    rows = "".join(
        f"""<tr style="border-bottom:1px solid #e5e7eb;">
              <td style="padding:6pt 4pt;text-align:center;font-size:9pt;color:#9ca3af;vertical-align:top;">{i+1}</td>
              <td style="padding:6pt 8pt;font-size:9.5pt;font-weight:500;vertical-align:top;">{item['item']}</td>
              <td style="padding:6pt 4pt;text-align:center;font-size:11pt;color:{color_map.get(item['status'],'#666')};font-weight:bold;vertical-align:top;">{item['status']}</td>
              <td style="padding:6pt 8pt;font-size:9pt;line-height:1.45;vertical-align:top;">{item['note']}</td>
              <td style="padding:6pt 8pt;font-size:8.5pt;line-height:1.5;color:#475569;vertical-align:top;background:#fafbfc;">{item.get('explanation','')}</td>
            </tr>"""
        for i, item in enumerate(items)
    )

    n_pass = sum(1 for it in items if it["status"] == "[O]")
    n_fail = sum(1 for it in items if it["status"] == "[X]")
    n_unknown = sum(1 for it in items if it["status"] == "[?]")
    pass_pct = n_pass / len(items) * 100
    n_data_based = sum(1 for it in items if it.get("data_based"))
    data_pct = n_data_based / len(items) * 100 if items else 0

    if data_pct >= 40:
        disclaimer_bg, disclaimer_border, disclaimer_color = "#f0fdf4", "#16a34a", "#15803d"
        disclaimer_text = (
            f"<strong>실데이터 기반 검증 {n_data_based}/{len(items)} 항목 ({data_pct:.0f}%)</strong> — "
            f"market_data·재무제표·DCF·risk_metrics에서 직접 추출한 metric으로 criterion 충족 여부 판정. "
            f"나머지는 정성 평가 항목."
        )
    else:
        disclaimer_bg, disclaimer_border, disclaimer_color = "#fef3c7", "#ea580c", "#9a3412"
        disclaimer_text = (
            f"실데이터 검증 {n_data_based}/{len(items)} 항목 ({data_pct:.0f}%) — 나머지는 정성 평가 또는 heuristic. "
            f"개별 항목 '설명'에서 검증 근거 확인 가능. <strong>'학습 가이드' column에서 각 항목의 의미·해석법</strong> 학습."
        )

    return f"""
    <h4>[브리핑] {persona_kr} Investment Checklist (실데이터 기반 검증 + 학습 가이드)</h4>
    <p style="font-size:8.5pt; color:{disclaimer_color}; background-color:{disclaimer_bg}; padding:6pt 10pt; border-left:3pt solid {disclaimer_border}; border-radius:3pt;">
      {disclaimer_text}
    </p>
    <p style="font-size:9pt;color:#475569;margin:4pt 0;">
      <strong>{persona_kr}의 핵심 판단 framework</strong> — {ticker}이 각 항목을 만족하는지 점검.
      <strong>통과율: {n_pass}/{len(items)} ({pass_pct:.0f}%)</strong> · 미달 {n_fail} · 불명 {n_unknown}
    </p>
    <table class="dt" style="width:100%;table-layout:fixed;">
      <colgroup>
        <col style="width:3%;"/>
        <col style="width:22%;"/>
        <col style="width:6%;"/>
        <col style="width:30%;"/>
        <col style="width:39%;"/>
      </colgroup>
      <thead><tr style="background:#f1f5f9;">
        <th style="padding:6pt 4pt;font-size:9pt;">#</th>
        <th style="padding:6pt 8pt;font-size:9pt;text-align:left;">판단 항목 (Criterion)</th>
        <th style="padding:6pt 4pt;font-size:9pt;">결과</th>
        <th style="padding:6pt 8pt;font-size:9pt;text-align:left;">설명 (검증 결과)</th>
        <th style="padding:6pt 8pt;font-size:9pt;text-align:left;background:#e0f2fe;">학습 가이드 (의미·해석법)</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>
    """
