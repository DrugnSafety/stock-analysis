"""각 페르소나의 투자 철학 + 핵심 원칙 + 의사결정 방식 — 학습용 풍부한 설명."""

PERSONA_INTRO = {
    "warren-buffett": {
        "kr": "워런 버핏",
        "en": "Warren Buffett",
        "category": "value (가치)",
        "lifetime": "1930년생, 95세",
        "background": "버크셔 해서웨이 회장. '오마하의 현인'으로 불리며 역사상 가장 위대한 투자자로 평가받습니다. 12살에 첫 주식 매수, 19세에 콜롬비아대에서 벤저민 그레이엄에게 가치투자를 배웠습니다.",
        "philosophy": "<strong>'좋은 가격에 wonderful business를 사라'</strong>가 핵심. 단순히 싼 주식이 아닌, 영구적 경쟁우위(moat)를 가진 우수한 비즈니스를 합리적 가격에 매수해 평생 보유합니다. 코카콜라·아메리칸 익스프레스·애플 같이 brand·network 같은 무형 moat를 가진 기업을 선호합니다.",
        "core_principles": [
            "<strong>능력범위(Circle of Competence)</strong> 안에서만 투자. 모르는 사업은 평가하지 않습니다.",
            "<strong>해자(Moat)</strong>: 브랜드·전환비용·네트워크 효과·비용우위·정부면허 5가지 중 하나 이상이 견고해야 합니다.",
            "<strong>경영진 품질</strong>: 자본배분 능력 + 솔직한 주주 커뮤니케이션 + 장기 정렬된 인센티브 구조.",
            "<strong>안전마진(Margin of Safety)</strong>: 내재가치 대비 30% 이상 디스카운트로 매수합니다.",
            "<strong>장기 보유</strong>: 'Forever' — 사이클 변동에 흔들리지 않습니다."
        ],
        "five_step": [
            "1. <strong>능력범위 점검</strong> — 5분 안에 plain Korean으로 설명 가능한가? 10년 후 모습 예측 가능한가? 통과 못하면 즉시 종료.",
            "2. <strong>해자 평가</strong> — 어떤 종류 moat인가? 좁아지는가, 넓어지는가? 향후 10년 유지 가능?",
            "3. <strong>경영진·자본배분</strong> — 자사주매입 vs 배당 vs M&A 비율 트랙레코드. Annual letter 솔직성.",
            "4. <strong>재무 강건성·밸류에이션</strong> — ROE, ROIC, FCF margin, 부채비율, 이자보상배율. Owner earnings 추정.",
            "5. <strong>결론</strong> — 안전마진 충분(30%+)? Lean bullish / lean bearish / neutral 판정. Horizon은 항상 long_term."
        ],
        "famous_quote": "\"Rule No. 1: Never lose money. Rule No. 2: Never forget Rule No. 1.\"",
        "weakness": "기술 변화 빠른 산업·바이오·commodity·신규 IPO에 약함. 능력범위 외로 분류해 verdict가 너무 보수적이 될 수 있습니다."
    },
    "charlie-munger": {
        "kr": "찰리 멍거",
        "en": "Charlie Munger",
        "category": "value (가치)",
        "lifetime": "1924-2023 (99세 작고)",
        "background": "버크셔 해서웨이 부회장이자 버핏의 '50년 동업자'. 변호사 출신으로 다학제적 사고(multidisciplinary thinking)의 대가. Wesco Financial 회장 역임.",
        "philosophy": "<strong>'단순히 싼 것보다 wonderful business가 우월하다'</strong>. Quality에 합당한 가격을 지불하는 것이 deep value 함정에 빠지는 것보다 낫다고 강조. <strong>역사고(Inversion)</strong>의 대가 — '어떻게 부자가 되는가'가 아닌 '어떻게 망하는가'를 먼저 생각합니다.",
        "core_principles": [
            "<strong>Quality > Cheap</strong>: 단순히 싼 비즈니스보다 합당한 가격의 우수한 비즈니스 선호.",
            "<strong>다학제적 사고</strong>: 심리학·물리학·생물학·경제학을 cross-check하는 mental models 100개.",
            "<strong>인센티브를 따르라</strong>: '내게 인센티브를 보여주면, 결과를 보여주겠다.'",
            "<strong>너무 어렵거나 fragile한 비즈니스 회피</strong>: 'Too hard pile'에 분류해 평가 자체를 거부.",
            "<strong>Lollapalooza 효과</strong>: 여러 favorable factor가 동시에 작동하는 setup 선호."
        ],
        "five_step": [
            "1. <strong>Inversion Test (역사고)</strong> — 이 회사가 망한다면 어떤 시나리오? 그 시나리오 가능성?",
            "2. <strong>Business Quality</strong> — ROIC, ROE가 자본비용을 지속 초과하는가? 가격 결정력? 고객/공급자 분산?",
            "3. <strong>Incentive·Culture</strong> — 경영진 보상이 단기 EPS인가, 장기 ROIC인가? CEO 인터뷰 톤·문화.",
            "4. <strong>Mental Model Cross-Check</strong> — Lollapalooza factor? Confirmation bias 의심?",
            "5. <strong>결론</strong> — Wonderful at fair price인가, fair at wonderful price인가?"
        ],
        "famous_quote": "\"Invert, always invert.\" / \"Show me the incentive and I'll show you the outcome.\"",
        "weakness": "버핏보다 더 까다로워 'Too hard pile' 분류가 잦음. Bio·신규IPO·복잡 conglomerate는 거의 평가 거부."
    },
    "peter-lynch": {
        "kr": "피터 린치",
        "en": "Peter Lynch",
        "category": "growth (성장)",
        "lifetime": "1944년생, 81세",
        "background": "Fidelity Magellan 펀드를 1977-1990 운용하며 연평균 29% 수익률 달성 (S&P 500 대비 +14% alpha). One Up On Wall Street 저자.",
        "philosophy": "<strong>'아는 것에 투자하라(Invest in what you know)'</strong>. 일상에서 관찰 가능한 비즈니스(쇼핑몰, 음식점, 자녀가 쓰는 제품)에서 ten-bagger(10배 종목)를 찾습니다. 가격이 합리적인 성장(GARP, Growth At Reasonable Price)이 핵심.",
        "core_principles": [
            "<strong>Plain language 이해</strong>: 12살 아이에게 한 문장으로 설명 가능해야 함.",
            "<strong>GARP — PEG ratio</strong>: PER ÷ EPS 성장률. PEG < 1.0 = undervalued, > 2.0 = overvalued.",
            "<strong>Ten-bagger</strong>: 10배 수익 종목 추구. Fast grower 카테고리 + plain understanding 결합.",
            "<strong>실용적 수요 신호</strong>: '몰에서 사람들이 줄 서 있다', '자녀가 매일 사용한다' 같은 기초 관찰.",
            "<strong>부채 면밀 점검</strong>: 좋은 성장 스토리도 leverage가 망친다."
        ],
        "five_step": [
            "1. <strong>이해 가능성</strong> — 12세 아이 설명 + 일상에서 본 적 있는 제품/서비스?",
            "2. <strong>성장 품질</strong> — 매출·EPS 일관 성장? 카테고리 분류 (slow grower / stalwart / fast grower / cyclical / turnaround / asset play).",
            "3. <strong>GARP — PEG</strong> — PEG < 1.0: undervalued, 1-2: fair, > 2: overvalued.",
            "4. <strong>부채·스토리 위험</strong> — 부채/자기자본, 스토리가 깨지는 가장 큰 risk?",
            "5. <strong>실용적 결론</strong> — 카테고리 명시 + PEG 인용. Diworsification(의미 없는 다각화) 의심."
        ],
        "famous_quote": "\"The person that turns over the most rocks wins the game.\" / \"Know what you own, and know why you own it.\"",
        "weakness": "Bio·금융·complex commodity 카테고리에 약함. PEG 적용 어려운 종목은 'too hard'."
    },
    "cathie-wood": {
        "kr": "캐시 우드",
        "en": "Cathie Wood",
        "category": "growth (성장)",
        "lifetime": "1955년생, 70세",
        "background": "ARK Invest 창립자·CEO. Tudor·Jennison Associates·AllianceBernstein에서 일한 후 2014년 ARK 설립. ARKK ETF가 2020년에 +152% 수익으로 폭발적 주목 받음.",
        "philosophy": "<strong>'Disruptive Innovation'</strong>이 핵심. 5년+ horizon으로 기술 곡선이 비용 곡선을 무너뜨리는 회사를 매수. <strong>Wright's law (학습곡선)</strong>: 누적 생산량 2배 → 비용 일정 비율 감소. 변동성을 exponential upside의 가격으로 수용.",
        "core_principles": [
            "<strong>Disruptive Innovation > Mature Steady-state</strong>",
            "<strong>큰 TAM 확장 + Winner-take-most</strong>",
            "<strong>5년+ horizon</strong>: 단기 변동성 무시",
            "<strong>R&D intensity 매우 높은 회사 선호</strong>",
            "<strong>5대 platform</strong>: AI, Robotics, Genomics, Blockchain, Energy Storage. 이들의 융합이 가장 큰 disruption."
        ],
        "five_step": [
            "1. <strong>혁신 식별</strong> — 어떤 disruptive technology? Wright's law / Moore's law 적용?",
            "2. <strong>TAM 사이즈</strong> — 5년 후 시장 규모? CAGR 30%+? Winner-take-most 가능?",
            "3. <strong>성장 증거</strong> — 매출 acceleration, R&D 강도, top engineering talent 영입.",
            "4. <strong>실행·비전</strong> — CEO vision, capital allocation, pivot 능력.",
            "5. <strong>밸류에이션</strong> — 5년 후 추정 매출 × IPO comp multiple. -50% drawdown 견딜 conviction?"
        ],
        "famous_quote": "\"Innovation creates new opportunities, but it also creates risks.\" / \"We don't worry about volatility; we worry about value.\"",
        "weakness": "단기 timing에 약함. 2021-22 ARKK -75% 폭락. Cyclical·commodity·전통 산업은 거의 lean_bearish (disruption 대상)."
    },
    "michael-burry": {
        "kr": "마이클 버리",
        "en": "Michael Burry",
        "category": "value-contrarian (가치-반대투자)",
        "lifetime": "1971년생, 54세",
        "background": "Scion Asset Management 창립. 의사 출신. 2005-2007 서브프라임 모기지 short으로 유명 (영화 'The Big Short'). Glance Investment Group → Scion Capital.",
        "philosophy": "<strong>'Hard numbers > Narrative'</strong>. 시가총액이 아닌 EV(Enterprise Value) 기반 valuation. 시장이 무시하는 catalyst (인사이더 매수, 자사주매입, restructuring, 자산매각) 추적. 'How much can I lose?'를 먼저 묻습니다.",
        "core_principles": [
            "<strong>EV 기반 valuation</strong> (시총 X)",
            "<strong>Downside protection 우선</strong>",
            "<strong>Contrarian mispricing 추구</strong>: 시장 합의가 틀린 곳",
            "<strong>Hard catalyst</strong>: 인사이더 매수·자사주매입·spin-off",
            "<strong>NCAV·자산담보가치 floor</strong>"
        ],
        "five_step": [
            "1. <strong>Hard valuation</strong> — EV/EBIT, EV/Sales, NCAV, 자산담보가치, earnings power",
            "2. <strong>Balance Sheet Stress</strong> — 부채 만기, dilution risk, 1년 cash burn vs cash",
            "3. <strong>Contrarian Mispricing</strong> — Sell-side가 어디서 틀렸는가? Short interest 높은데 펀더 양호?",
            "4. <strong>Catalyst</strong> — Form 4 인사이더, 13D, 자사주매입, 자산매각",
            "5. <strong>결론</strong> — Entry/exit price + 비대칭 payoff ratio"
        ],
        "famous_quote": "\"What is one's life worth? You can't measure that until you put it on the line.\" / \"My nature is not contrarian.\"",
        "weakness": "Timing이 너무 이르면 -50% drawdown 견뎌야 함. 2008 서브프라임도 2년 일찍 entry."
    },
    "nassim-taleb": {
        "kr": "나심 탈레브",
        "en": "Nassim Taleb",
        "category": "risk (리스크)",
        "lifetime": "1960년생, 65세",
        "background": "통계학자·옵션 트레이더 출신. 'The Black Swan', 'Antifragile' 저자. 1987 블랙 먼데이 + 2008 글로벌 금융위기에서 양쪽 모두 alpha 창출. Universa Investments 자문.",
        "philosophy": "<strong>'Antifragility > Robustness > Fragility'</strong>. 충격에서 더 강해지는 시스템에 노출, fragile 회피. <strong>Convex payoff</strong>: 작은 손실 + 큰 이익. 낮은 가시 변동성을 hidden danger로 의심.",
        "core_principles": [
            "<strong>Fragile 회피가 upside보다 우선</strong>",
            "<strong>Convex payoff 선호</strong>",
            "<strong>Tail risk·Fat tails 존중</strong>",
            "<strong>Skin in the game</strong>: 결과를 함께 부담",
            "<strong>'Lindy effect'</strong>: 오래된 비즈니스가 더 antifragile"
        ],
        "five_step": [
            "1. <strong>Fragility Diagnosis</strong> — 단일 장애점? 부채만기 집중? 단일 고객 의존?",
            "2. <strong>Convexity·Optionality</strong> — Upside / Downside ratio? Free option?",
            "3. <strong>Skin in the Game</strong> — 경영진 자기 회사 보유 비율, 보너스 단기 vs 장기?",
            "4. <strong>Volatility Regime</strong> — 낮은 가시 변동성 = hidden risk 누적?",
            "5. <strong>Antifragile / Robust / Fragile call</strong>"
        ],
        "famous_quote": "\"Black swans are events that are rare, extreme-impact, and only retrospectively predictable.\" / \"Fragility implies more to lose than to gain.\"",
        "weakness": "Bull market에서 underperform. 'Structural' framing 자체를 의심해서 mainstream thesis에 lean_bearish."
    },
    "ben-graham": {
        "kr": "벤저민 그레이엄",
        "en": "Ben Graham",
        "category": "value (가치, deep value)",
        "lifetime": "1894-1976",
        "background": "가치투자의 아버지. 컬럼비아대 교수. 'The Intelligent Investor', 'Security Analysis' 공저. 버핏의 멘토.",
        "philosophy": "<strong>'Margin of Safety'</strong>. 내재가치 대비 33%+ 디스카운트. <strong>'Mr. Market'</strong>은 변덕스러운 사업 동업자 — 그의 호가에 흔들리지 말 것. NCAV(Net Current Asset Value), Graham Number 같은 정량 floor 강조.",
        "core_principles": [
            "<strong>Margin of Safety 33%+</strong>",
            "<strong>Defensive vs Enterprising 투자자 구분</strong>",
            "<strong>Mr. Market의 변덕 무시</strong>",
            "<strong>재무 강건성</strong>: 부채<자본, 유동비율≥2, 이자보상≥5",
            "<strong>Graham Number = √(22.5 × EPS × BVPS)</strong>"
        ],
        "five_step": [
            "1. <strong>Defensive Tests</strong> — 시총, 유동비율 ≥2, 부채<자본, 7년 흑자, 20년 배당, EPS 33%+ 성장, PER<15, PBR<1.5, PER×PBR<22.5",
            "2. <strong>NCAV Test</strong> — 시총/NCAV < 0.67 = Net-Net deep value",
            "3. <strong>Graham Number 계산</strong>",
            "4. <strong>Earnings 안정성</strong> — 7년·10년 EPS",
            "5. <strong>결론 — Defensive or Enterprising?</strong>"
        ],
        "famous_quote": "\"Investment is most intelligent when it is most businesslike.\"",
        "weakness": "Earnings 부재(bio·early-stage)는 defensive 기준 통과 불가. Cyclical 정점은 PE만 보면 매력적이나 trap."
    },
    "bill-ackman": {
        "kr": "빌 애크먼",
        "en": "Bill Ackman",
        "category": "activist (액티비스트)",
        "lifetime": "1966년생, 59세",
        "background": "Pershing Square Capital 창립. Concentrated portfolio (8-12개) + activist intervention. Chipotle·Hilton·Wendy's에서 strong returns, Valeant·Herbalife에서 큰 손실.",
        "philosophy": "<strong>'Concentrated activist'</strong>. 한 종목에 5-10% 들어갈 conviction이 없으면 사지 말라. 강한 FCF + 우수 자본배분 + 명확한 catalyst를 가진 high-quality business를 찾아서 필요시 board seat·CEO 교체로 가치 창출.",
        "core_principles": [
            "<strong>Concentrated 8-12 holdings</strong>",
            "<strong>강한 FCF + 자본배분 우수성</strong>",
            "<strong>명확한 catalyst</strong> (12-24M)",
            "<strong>Activist intervention 가능성</strong>",
            "<strong>Quality + Price 둘 다 만족</strong>"
        ],
        "five_step": [
            "1. <strong>Business Quality</strong> — ROIC > WACC, recurring revenue, 가격 결정력",
            "2. <strong>FCF·자본배분</strong> — FCF margin trend, 자사주매입·배당·M&A 비율",
            "3. <strong>Catalyst</strong> — 6-24M, M&A·spin-off·CEO 교체 가능성",
            "4. <strong>Activist Path</strong> — 13D 가능성? 주주 지지 가능성?",
            "5. <strong>결론 — 5-10% 포지션 conviction?</strong>"
        ],
        "famous_quote": "\"Investing is a business where you can look very silly for a long period of time before you're proven right.\"",
        "weakness": "Small cap·neutral catalyst에 약함. Activist 어려운 시장(한국·일본 chaebol)에서 verdict 보수적."
    },
    "mohnish-pabrai": {
        "kr": "모니시 파브라이",
        "en": "Mohnish Pabrai",
        "category": "value (가치)",
        "lifetime": "1964년생, 61세",
        "background": "Pabrai Investment Funds. 인도 출신. 버핏·그레이엄의 직접적 후계자. 'The Dhandho Investor' 저자. Compounding rate 25%+ 장기 트랙레코드.",
        "philosophy": "<strong>'Heads I win, Tails I do not lose much'</strong>. 비대칭 payoff 우선. <strong>Risk vs Uncertainty 구분</strong>: Risk = 영구 자본 손실, Uncertainty = outcome 불확실하지만 손실 제한적. 50%+ 디스카운트가 진정한 안전마진.",
        "core_principles": [
            "<strong>'Heads I win'</strong> 비대칭 payoff",
            "<strong>Low risk + High uncertainty 추구</strong>",
            "<strong>50%+ 디스카운트 안전마진</strong>",
            "<strong>단순한 비즈니스, 단순한 분석</strong>",
            "<strong>Cloning 가능</strong>: 다른 위대한 투자자 13F filings 활용"
        ],
        "five_step": [
            "1. <strong>Risk vs Uncertainty</strong> — 영구손실 가능? Uncertainty는 OK",
            "2. <strong>Margin of Safety</strong> — 보수적 시나리오 IV/시가 < 0.5 (50% 디스카운트)",
            "3. <strong>단순성 Test</strong> — 한 문단 설명? 5년 후 모습 예측?",
            "4. <strong>비대칭 Payoff</strong> — Best/Worst case, X/Y > 3",
            "5. <strong>Cloning Check</strong> — 다른 위대한 투자자 보유? 13F 확인"
        ],
        "famous_quote": "\"Investing is all about decision-making. The best companies make excellent decisions consistently.\"",
        "weakness": "Bio·tech 등 복잡 비즈니스는 거의 평가 안 함. Cyclical 정점은 'low risk'로 분류하기 어려움."
    },
    "phil-fisher": {
        "kr": "필 피셔",
        "en": "Phil Fisher",
        "category": "growth (성장)",
        "lifetime": "1907-2004",
        "background": "성장주 투자의 선구자. 'Common Stocks and Uncommon Profits' 저자. Fisher & Co. 창립. 버핏이 자신을 '85% 그레이엄, 15% 피셔'로 표현.",
        "philosophy": "<strong>'Scuttlebutt(우물가 정보)'</strong>. 회사 외부 정보원 (고객·전직원·공급자·경쟁사)에게 직접 묻기. <strong>Decade+ holding</strong>으로 R&D·관리·영업력이 시간이 지나며 가치를 창출.",
        "core_principles": [
            "<strong>Scuttlebutt 정보 수집</strong>",
            "<strong>경영진 품질 출발점</strong>",
            "<strong>R&D 효율성</strong>",
            "<strong>영업력·시장 침투</strong>",
            "<strong>Decade+ holding</strong>"
        ],
        "five_step": [
            "1. <strong>15-Point Checklist</strong> — 시장잠재력, 추가성장 의지, R&D 효율, 영업, 마진, 노사관계, 임원관계, 경영진 깊이, 원가관리, 산업특수강점, 장기이익, 자본조달, 솔직함, <strong>정직성</strong>",
            "2. <strong>Scuttlebutt Synthesis</strong> — 고객·전직원·경쟁사·공급자",
            "3. <strong>R&D Productivity</strong> — R&D/매출, 신제품 매출 / R&D, patent",
            "4. <strong>Long-Duration Compounding</strong> — 10년 후 모습? Reinvestment runway?",
            "5. <strong>결론 — 15-point 통과 + scuttlebutt 양호?</strong>"
        ],
        "famous_quote": "\"The stock market is filled with individuals who know the price of everything, but the value of nothing.\"",
        "weakness": "Scuttlebutt 정보 수집이 한국·외국 기업에 어려움. Family 경영진 정직성 평가 모호."
    },
    "rakesh-jhunjhunwala": {
        "kr": "라케시 준준왈라",
        "en": "Rakesh Jhunjhunwala",
        "category": "growth-em (이머징 성장)",
        "lifetime": "1960-2022 (62세 작고)",
        "background": "'인도의 워런 버핏'. Rare Enterprises 운용. 5,000루피로 시작하여 5조원+ 자산 형성. Akasa Air 창립자.",
        "philosophy": "<strong>'Long-term wealth via emerging market growth'</strong>. 능력범위(인도 등 emerging) 안에서 ROE 지속성 + 거시 tailwind + 미시 quality 정렬된 종목에 장기 베팅. Decade-scale compounding 추구.",
        "core_principles": [
            "<strong>능력범위 (Circle of Competence)</strong>",
            "<strong>ROE 지속성</strong> 일차 quality 지표",
            "<strong>장기 부 창출</strong>",
            "<strong>Emerging market 성장 catalyst</strong>",
            "<strong>거시 + 미시 정렬</strong>"
        ],
        "five_step": [
            "1. <strong>Macro Tailwind</strong> — Emerging growth driver와 정렬?",
            "2. <strong>ROE 분석</strong> — 5년·10년 trend, DuPont 분해",
            "3. <strong>Circle of Competence</strong> — 본인 학습 범위 내?",
            "4. <strong>Reinvestment Opportunity</strong> — TAM 큼? Compounding runway 5-10년+",
            "5. <strong>결론 + Position sizing</strong>"
        ],
        "famous_quote": "\"Markets are like women - always commanding, mysterious, unpredictable and volatile.\" / \"Believing & holding is more important than buying.\"",
        "weakness": "한국은 이미 developed라 emerging tailwind 약함. ROE 변동성 큰 cyclical은 미적합."
    },
    "stanley-druckenmiller": {
        "kr": "스탠리 드러켄밀러",
        "en": "Stanley Druckenmiller",
        "category": "macro (매크로)",
        "lifetime": "1953년생, 72세",
        "background": "Duquesne Capital 창립. Soros 가족 사무실 조지 소로스의 right-hand로 1992년 영국 파운드화 베팅 (Bank of England 깨뜨림). 30년+ 연평균 30% 수익률 (-down year 0회).",
        "philosophy": "<strong>'Macro tailwind + Micro catalyst + Strong conviction = Aggressive sizing'</strong>. Asymmetric setup 발굴 후 <strong>'Bet the ranch when the odds are with you'</strong> — high conviction 시 30-50% 포지션도. <strong>Soros reflexivity</strong> (가격이 펀더멘털에 영향) 활용.",
        "core_principles": [
            "<strong>Asymmetric Setup</strong> (reward/risk > 3:1)",
            "<strong>Momentum</strong> — 가격 추세는 information",
            "<strong>Sentiment Inflection</strong>",
            "<strong>Macro + Micro 결합</strong>",
            "<strong>Position sizing</strong>: high-conviction 시 적극적"
        ],
        "five_step": [
            "1. <strong>Macro Regime</strong> — Fed·중앙은행 정책, 금리 곡선, 통화 흐름",
            "2. <strong>Sentiment Position</strong> — 시장 합의 위치, VIX, AAII, fund flows",
            "3. <strong>Asymmetric Setup</strong> — Reward/Risk > 3:1?",
            "4. <strong>Momentum & Catalyst</strong> — 가격 추세, reflexivity loop",
            "5. <strong>Position Sizing</strong> — Conviction 1-10, stop loss"
        ],
        "famous_quote": "\"Bet the ranch when the odds are with you.\" / \"Volatility is the price you pay for performance.\"",
        "weakness": "Single stock에 약함 (macro에 편중). Sentiment overcrowded 시 진입 회피해서 큰 wave 놓칠 수 있음."
    },
    "aswath-damodaran": {
        "kr": "애스워드 다모다란",
        "en": "Aswath Damodaran",
        "category": "valuation (밸류에이션)",
        "lifetime": "1957년생, 68세",
        "background": "NYU Stern School 교수 (Dean of Valuation). 'Damodaran on Valuation', 'Narrative and Numbers' 저자. 매년 모든 종목에 대한 valuation 공개. World's most respected valuation expert.",
        "philosophy": "<strong>'Story → Numbers → Value'</strong>. 모든 valuation은 story로 시작 → 숫자로 변환 → 내재가치 도출. <strong>Reverse DCF before Forward DCF</strong>: 현재 가격이 함의하는 expectations를 먼저 도출하고 그 가정이 합리적인가 평가.",
        "core_principles": [
            "<strong>Story → Numbers → Value</strong>",
            "<strong>Reverse DCF before Forward DCF</strong>",
            "<strong>Story 일관성 검증</strong>: 매출 성장률·마진·재투자율 모순 X",
            "<strong>장기 가정 명확성</strong>",
            "<strong>Country Risk Premium</strong> 별도 적용"
        ],
        "five_step": [
            "1. <strong>Story 정의</strong> — 회사가 무엇을 파는가, 누구에게, 어떻게 차별화, 어떻게 성장",
            "2. <strong>Story Test</strong> — Possible / Plausible / Probable",
            "3. <strong>Numbers Translation</strong> — 매출 성장, 영업마진, 재투자율, WACC",
            "4. <strong>Reverse DCF</strong> — 시장가 함의 expectations 도출, 합리성 평가",
            "5. <strong>결론</strong> — 내재가치 vs 시장가 ±30%"
        ],
        "famous_quote": "\"Numbers without a story are like a body without a soul; stories without numbers are like a soul without a body.\"",
        "weakness": "복잡한 narrative 종목 (PRTA 같은 binary bio) 평가에 framework 한계. Forward 추정의 sensitivity 큼."
    },
}


def render_persona_intro(persona_id: str) -> str:
    """페르소나 학습용 소개 박스 HTML."""
    p = PERSONA_INTRO.get(persona_id)
    if not p:
        return ""
    principles_html = "".join(f"<li>{x}</li>" for x in p["core_principles"])
    steps_html = "".join(f"<li>{x}</li>" for x in p["five_step"])
    return f"""
    <div class="persona-intro" style="background:#f9fafb;border-left:4pt solid #2563eb;padding:14pt 18pt;margin:12pt 0;">
      <div style="font-size:13pt;font-weight:700;color:#111;">{p['kr']} ({p['en']})</div>
      <div style="font-size:9pt;color:#6b7280;margin:2pt 0 8pt 0;">{p['category']} · {p['lifetime']}</div>

      <p style="margin:6pt 0;"><strong>📚 배경</strong>: {p['background']}</p>
      <p style="margin:6pt 0;"><strong>💡 투자 철학</strong>: {p['philosophy']}</p>

      <p style="margin:8pt 0 4pt 0;"><strong>⭐ 핵심 원칙</strong></p>
      <ul style="margin:0 0 8pt 18pt;font-size:9.5pt;">{principles_html}</ul>

      <p style="margin:8pt 0 4pt 0;"><strong>🔍 의무 5단계 분석 시퀀스</strong></p>
      <ol style="margin:0 0 8pt 18pt;font-size:9.5pt;">{steps_html}</ol>

      <p style="margin:6pt 0;font-size:9pt;color:#374151;font-style:italic;">"{p['famous_quote']}"</p>

      <p style="margin:6pt 0;font-size:9pt;color:#92400e;background:#fef3c7;padding:6pt 10pt;border-radius:3pt;">
        <strong>⚠️ 약점·주의</strong>: {p['weakness']}
      </p>
    </div>
    """
