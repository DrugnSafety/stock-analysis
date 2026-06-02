"""종목별 회사 소개 — 보고서 초반 (Cover 직후)에 위치.

각 ticker에 대한:
  - 사업 개요 (한 단락 200-400자)
  - 매출 구조 (segment 비중)
  - 글로벌 위치
  - 주요 고객·경쟁사
"""
from __future__ import annotations
from typing import Optional


COMPANY_INTROS: dict[str, dict] = {
    "009150.KS": {
        "overview": "삼성전기는 한국 부품 1위 업체로 MLCC (적층세라믹콘덴서)·FCBGA 기판·실리콘 커패시터·카메라모듈을 자체 생산하는 글로벌 유일 vertical integration 부품사. AI 반도체 패키징 super-cycle의 직접 수혜로 2026년 YTD +492% (27만→160만원). FCBGA 기판 수요가 capacity 50% 초과로 가격결정력 확보, 1.5조원 실리콘 커패시터 supply 계약(2025-12) 체결.",
        "revenue_segments": [
            ("Component (MLCC)", 38, "AI MLCC 비중 25%→35% 가이드, 가격 인상 사이클 진입"),
            ("Substrate (FCBGA/ABF)", 32, "AI 기판 BB ratio 1.4x, NVIDIA·AMD·Google 공급"),
            ("Optics & Communication", 22, "스마트폰 카메라 모듈 (Apple·Samsung)"),
            ("실리콘 커패시터·기타", 8, "1.5조원 공급계약 — GPU/HBM 패키지 내부 침투"),
        ],
        "global_position": "MLCC 글로벌 #2 (Murata 35% / Samsung 15% / TDK 12%). FCBGA 글로벌 #2-3 (Ibiden 22% / Shinko 12% / Samsung 15%). 글로벌 부품사 중 MLCC + FCBGA + 실리콘 커패시터 통합 유일 — vertical integration moat.",
        "key_customers": ["NVIDIA", "AMD", "Apple", "Samsung Electronics", "Broadcom"],
        "key_competitors": ["Murata Manufacturing (MRAAY)", "TDK (TTDKY)", "Ibiden (4062.T)", "Shinko Denki (6967.T)", "LG이노텍 (011070.KS)"],
    },
    "011070.KS": {
        "overview": "LG이노텍은 LG그룹 산하 종합 부품사로 카메라모듈(Apple iPhone 주요 supplier) + ABF 기판(반도체 패키징) duo 구조. 2025-2026년 사업 mix shift 가속 — ABF 매출 1.2조→1.8조원 (+50%) 가이드. 2026 YTD +295%로 시장이 AI 패키징 직접 노출 인식. Apple·AMD·Broadcom과 ABF 신규 supply 계약 발표(2026 Q1).",
        "revenue_segments": [
            ("Optics Solution (카메라모듈)", 62, "Apple iPhone17·M5 메인 supplier — 매출 8조원"),
            ("Substrate (ABF/RF-PCB)", 18, "글로벌 ABF #2-3, AI GPU 패키지 직접 수혜"),
            ("Vehicle Components", 12, "EV·자율주행 부품"),
            ("기타 (LED·tape substrate)", 8, ""),
        ],
        "global_position": "ABF 기판 글로벌 #2-3 (점유율 약 15%, Ibiden 22% 격차). 카메라모듈 Apple iPhone 메인 supplier — global smartphone 카메라 #1-2.",
        "key_customers": ["Apple", "AMD", "Broadcom", "Microsoft", "Tesla"],
        "key_competitors": ["Ibiden (4062.T)", "Shinko Denki (6967.T)", "Unimicron (3037.TW)", "삼성전기 (009150.KS)", "Sunny Optical (HK 2382)"],
    },
    "058470.KQ": {
        "overview": "리노공업은 한국 부산 본사의 반도체 후공정 검사 전문기업. IC 생산·테스트·분석용 핵심 검사 부품(테스트 소켓·프로브 헤드·스프링 콘택트) 글로벌 leader. HBM 전용 테스트 소켓 글로벌 점유율 약 25% 1위 — HBM4 12-Hi 검사 횟수 2배 증가로 ASP·교체 주기 비대칭 수혜. OPM 32.5% 한국 코스닥 최고 수준, 1978년 설립.",
        "revenue_segments": [
            ("Test Socket (메모리·HBM)", 55, "HBM·DDR·SoC 전용 — design-in lock-in"),
            ("Probe Head·Spring Contact", 30, "fine-pitch RF + Kelvin probe + 코악시얼"),
            ("PCB·기타 (의료·배터리)", 15, "카테터 PCB + 배터리 충방전 prober"),
        ],
        "global_position": "HBM 테스트 소켓 글로벌 #1 (점유율 25%). 글로벌 프로브카드 시장에서 FormFactor #1 (30%) / MPI #2 (18%) / 리노공업 #3-4. fine-pitch 영역 차별화.",
        "key_customers": ["SK하이닉스", "삼성전자", "Micron", "NVIDIA (test 간접)", "TSMC"],
        "key_competitors": ["FormFactor (FORM)", "MPI (6223.TWO)", "ISC (095340.KQ)", "Yokowo (6800.T)", "티에스이 (131290.KQ)"],
    },
    "010120.KS": {
        "overview": "LS ELECTRIC은 LS그룹 산하 전력기기·자동화 종합 부품사. AI 데이터센터 전력 인프라(HVDC·변압기·스위치기어) cycle의 직접 수혜 — 2026 Q1 수주잔고 2.8조원 사상 최대. 미국 grid 수출 가속(Trump 2.0 + IRA 유지 정책). 한국 #1 + 미국 진출 가속 단계.",
        "revenue_segments": [
            ("전력 (HVDC·변압기·스위치기어)", 45, "수주잔고 2.8조 사상 최대, 미국 grid 직접 수혜"),
            ("자동화 (PLC·HMI·드라이브)", 28, "스마트팩토리 + 산업용 자동화"),
            ("ESS·태양광 인버터", 17, "한국 #1, 신재생 전환 cycle"),
            ("기타 (해외·서비스)", 10, ""),
        ],
        "global_position": "한국 전력기기 #1. 글로벌 변압기·HVDC 시장에서 Hitachi Energy 20% / Siemens 18% / GE Vernova 12% / LS ELECTRIC 약 6%. AI 데이터센터 전력 outer-layer 차별화.",
        "key_customers": ["미국 utility (Duke Energy, NextEra)", "사우디 SEC", "한국전력공사", "Hyperscaler 직접 발주"],
        "key_competitors": ["Hitachi Energy (HTHIY)", "Siemens Energy (ENR.DE)", "GE Vernova (GEV)", "HD현대일렉트릭 (267260.KS)", "효성중공업 (298040.KS)"],
    },
    "000660.KS": {
        "overview": "SK하이닉스는 한국 2위 종합반도체 기업으로 메모리 (DRAM·NAND·HBM) 글로벌 share 2위 (32%). HBM3E NVDA 단독 공급으로 AI 인프라 cycle의 직접 수혜 종목. 2024-2025년 메모리 super-cycle 진입 후 영업이익 +180% YoY, 시가총액 1,000조원 돌파.",
        "revenue_segments": [
            ("DRAM (HBM 포함)", 65, "DDR5 + HBM3E NVDA 단독, 글로벌 share 32%"),
            ("NAND Flash", 28, "Solidigm 인수 후 enterprise SSD 강화"),
            ("기타 (CIS·System IC)", 7, "스마트폰 카메라 센서 + system semiconductor"),
        ],
        "global_position": "DRAM #2 (Samsung 40%, SK하이닉스 32%, Micron 22%). HBM3E NVDA 단독 80%+. NAND #4-5.",
        "key_customers": ["NVIDIA", "Apple", "Microsoft", "Google", "Meta"],
        "key_competitors": ["삼성전자 (005930.KS)", "Micron (MU)", "Sandisk", "Kioxia"],
    },
    "005930.KS": {
        "overview": "삼성전자는 글로벌 #1 종합 IT 기업. 메모리 (DRAM·NAND) 글로벌 1위, 파운드리 #2 (TSMC 다음), 스마트폰 #2, 가전 #1 multi-segment. 코리아 디스카운트 + HBM3E qualification 진입 단계로 SK하이닉스 대비 derate.",
        "revenue_segments": [
            ("DS (반도체)", 45, "DRAM #1, NAND #1, 파운드리 #2"),
            ("MX (모바일)", 35, "Galaxy 스마트폰·태블릿"),
            ("VD/DA (가전)", 12, "TV·냉장고·세탁기 글로벌 #1"),
            ("기타 (디스플레이·하만)", 8, ""),
        ],
        "global_position": "DRAM 글로벌 1위 40%, 파운드리 글로벌 2위 (TSMC 60% / Samsung 11%), 스마트폰 #2 (Apple 다음).",
        "key_customers": ["Apple (파운드리)", "Qualcomm", "Tesla", "글로벌 OEM 다수"],
        "key_competitors": ["TSMC", "Apple", "SK하이닉스", "Micron"],
    },
    "042660.KS": {
        "overview": "한화오션은 한국 조선 빅3 (HD현대중공업·삼성중공업·한화오션) 중 한화그룹 인수 후 재무 정상화 진행 단계. LNG 운반선 + 방산 (군함·잠수함) duo로 다각화. 2024년 미국 Philly Shipyard 인수로 Jones Act 시장 진입.",
        "revenue_segments": [
            ("상선 (LNG·컨테이너·탱커)", 65, "LNG선 글로벌 점유율 30%+"),
            ("해양 (FPSO·LNG bunker)", 15, "FPSO + offshore"),
            ("방산", 20, "군함·잠수함 (한국·폴란드 수주)"),
        ],
        "global_position": "LNG선 글로벌 빅3 (HD현대 + 삼성 + 한화 합계 70%+). 미국 Philly 인수로 Jones Act 진출.",
        "key_customers": ["Shell", "ExxonMobil", "Cheniere", "한국·폴란드 해군"],
        "key_competitors": ["HD현대중공업 (329180.KS)", "삼성중공업 (010140.KS)", "Imabari (Japan)"],
    },
    "329180.KS": {
        "overview": "HD현대중공업은 한국 조선 #1 leader. LNG선·컨테이너·탱커·해양 multi-segment. 단가 사상 최고 ($300M+/LNG선) + 수주잔고 multi-year peak. 2026년 RSI 80+ overbought 단기 과열.",
        "revenue_segments": [
            ("상선", 70, "LNG선 + 컨테이너선 + 탱커"),
            ("해양 (FPSO·offshore)", 18, ""),
            ("엔진·기계", 12, "선박용 저속·중속 엔진"),
        ],
        "global_position": "글로벌 조선 빅3 (China 다음). LNG선 share 30%+. 2026 수주잔고 multi-year peak.",
        "key_customers": ["Shell", "Cheniere", "QatarEnergy", "Maersk"],
        "key_competitors": ["삼성중공업", "한화오션", "Imabari", "China State Shipbuilding"],
    },
    "010140.KS": {
        "overview": "삼성중공업은 한국 조선 빅3 중 FLNG (Floating LNG) 차별화. 1Y +120% 가장 큰 momentum. Mozambique pipeline + 흑자 전환 multi-year EPS 가시성.",
        "revenue_segments": [
            ("상선·LNG", 55, "LNG선 + 컨테이너선"),
            ("해양 (FLNG·FPSO)", 35, "FLNG 차별화 — Coral Sul, Mozambique"),
            ("엔진·기타", 10, ""),
        ],
        "global_position": "LNG선 빅3, FLNG 글로벌 leader.",
        "key_customers": ["TotalEnergies", "Eni", "Shell", "ExxonMobil"],
        "key_competitors": ["HD현대중공업", "한화오션"],
    },
    "NVDA": {
        "overview": "NVIDIA는 글로벌 GPU dominant 90% share. AI 인프라 super-cycle anchor. Blackwell GB200 ramp으로 2026 매출 가이던스 $200B+. Hyperscaler capex $300B의 직접 수혜 (MSFT·GOOG·META·AMZN 90% 의존).",
        "revenue_segments": [
            ("Data Center (AI GPU)", 85, "H100/H200/Blackwell GB200 — Hyperscaler 직접 공급"),
            ("Gaming (GeForce)", 8, "RTX 50 시리즈"),
            ("Auto·Pro Viz", 5, "DRIVE Orin/Thor"),
            ("OEM·기타", 2, ""),
        ],
        "global_position": "GPU 글로벌 90%, AI inference 75%+. CUDA ecosystem dominant.",
        "key_customers": ["Microsoft", "Google", "Meta", "Amazon", "Tesla", "Oracle"],
        "key_competitors": ["AMD (MI400)", "Intel (Gaudi)", "Custom ASIC (TPU·Trainium)"],
    },
    "BTU": {
        "overview": "Peabody Energy는 미국 최대 석탄 생산자 — Thermal (PRB Powder River Basin) + Metallurgical (NAPP·CAPP·Centurion 호주). 2024-2025 cycle bottom 통과 후 회복 단계. EV/EBITDA 3.25x deep value + FCF yield 15.5%.",
        "revenue_segments": [
            ("Thermal coal (PRB)", 55, "미국 발전소용, low-cost ~$11/톤 break-even"),
            ("Metallurgical coal", 35, "제철 원료탄, 호주 Centurion 가동"),
            ("기타 (Trading·Brokerage)", 10, ""),
        ],
        "global_position": "미국 thermal coal #1 (share 18%). 글로벌 met-coal 8%.",
        "key_customers": ["Vistra", "Duke Energy", "NextEra", "Tata Steel", "JSW"],
        "key_competitors": ["Arch Resources", "Alpha Met", "Glencore", "Teck"],
    },
    "010130.KS": {
        "overview": "고려아연은 한국 #1 + 글로벌 top-3 비철금속 제련사. 아연·납·은·금 다각화. 황산은 부산물 — 2025년 한국 황산 순수출 238만톤 중 메인 player. 2026년 영풍 분쟁 governance issue 잔존.",
        "revenue_segments": [
            ("아연 (Zinc)", 45, "글로벌 #1, capa 600k 톤/년"),
            ("납·은 (Lead·Silver)", 25, "은 글로벌 top-3"),
            ("황산 + 기타 부산물", 15, "한국 황산 export leader"),
            ("동·금·기타", 15, ""),
        ],
        "global_position": "아연 글로벌 #1 (Glencore·Nyrstar 대비 우위). 은 #3.",
        "key_customers": ["Posco", "현대제철", "TSMC (silver)", "Apple supply chain"],
        "key_competitors": ["Glencore", "Nyrstar", "Teck", "Boliden"],
    },
    "MU": {
        "overview": "Micron은 미국 #1 메모리 반도체. DRAM 글로벌 share 22% (3위), NAND #4. HBM3E NVDA qualification 진행 중 (현재 share 5-10%). 미국 정책 우대 (CHIPS Act $6B+) + 'CFIUS-safe' 프리미엄.",
        "revenue_segments": [
            ("DRAM", 70, "DDR5 + HBM3E (진입 단계)"),
            ("NAND Flash", 25, "Enterprise SSD + Mobile"),
            ("기타", 5, ""),
        ],
        "global_position": "DRAM 글로벌 3위 (Samsung 40%, SK 32%, Micron 22%). NAND #4.",
        "key_customers": ["Apple", "Dell", "HPE", "AWS"],
        "key_competitors": ["Samsung", "SK하이닉스", "Sandisk", "Kioxia"],
    },
    "NEM": {
        "overview": "Newmont Corporation은 글로벌 1위 금광 기업이다. 2026년 기준 연 6.0Moz 금 생산으로 피어 평균(1.5-2.5Moz) 대비 압도적 규모. 2024년 Newcrest Mining 인수($19B)로 호주·캐나다·미국·페루·가나·서아프리카·인도네시아 7개 jurisdiction 16개 광산으로 portfolio 확장. AISC $1,400-1,500/oz 환경에서 gold $4,400+ 시 30%+ operating margin 보장. Druckenmiller·Burry·Donald Smith·Renaissance·Howard Marks 등 13F clustering 종목.",
        "revenue_segments": [
            ("North America (Nevada·Mexico·Canada)", 35, "Cripple Creek·Penasquito·Cadia 핵심 자산"),
            ("South America (Peru·Suriname)", 20, "Yanacocha·Merian"),
            ("Australia (Boddington·Cadia)", 22, "Newcrest 인수 자산 통합"),
            ("Africa (Ghana·Mali)", 13, "Akyem·Ahafo"),
            ("Other (PNG·Indonesia)", 10, "Lihir + Batu Hijau 25% stake"),
        ],
        "global_position": "글로벌 금광 #1 (Barrick·Agnico·AngloGold 대비 1.5-2x 규모). 동·은 by-product 추가. 2024 Newcrest 인수로 reserves 96Moz 도달.",
        "key_customers": ["bullion banks (JPM·HSBC·Goldman)", "central banks (China·India·Russia)", "jewelry trade (India·Middle East)"],
        "key_competitors": ["Barrick Gold (GOLD)", "Agnico Eagle (AEM)", "AngloGold Ashanti (AU)", "Kinross (KGC)"],
    },
    "AEM": {
        "overview": "Agnico Eagle Mines는 캐나다 본사의 금광 quality leader. 2026년 기준 연 3.5Moz 금 생산. 2022년 Kirkland Lake와 합병($11B)으로 portfolio 2.6x 확장. 안전한 jurisdiction (캐나다·핀란드·멕시코·호주) 집중으로 sovereign risk 최소화. AISC $1,290/oz로 industry 최저. Net debt/EBITDA 0.3x — 광산 sector 최우량 재무. 'tier-1 ounces only' 전략으로 자산 quality 최상.",
        "revenue_segments": [
            ("Canada (Detour·LaRonde·Malartic·Meliadine)", 55, "Detour Lake 18-year mine life"),
            ("Finland (Kittilä)", 12, "유럽 유일 대형 금광"),
            ("Mexico (Pinos Altos·La India)", 13, ""),
            ("Australia (Fosterville)", 12, "high-grade epithermal"),
            ("USA (Nunavut·기타)", 8, ""),
        ],
        "global_position": "글로벌 금광 #3 (시총 $90B+). Tier-1 jurisdiction 비중 95%로 sector 최고. ESG 등급 sector 최상.",
        "key_customers": ["bullion refineries (Asahi·PAMP·Valcambi)", "central banks", "jewelry trade"],
        "key_competitors": ["Newmont (NEM)", "Barrick Gold (GOLD)", "Kinross (KGC)", "B2Gold (BTG)"],
    },
    "GDX": {
        "overview": "VanEck Gold Miners ETF (GDX)는 글로벌 51개 금광 기업 시총 가중 ETF다. AUM $24B (2026.5). Newmont 12.5%·AEM 10.8%·Franco-Nevada 8.5%·Barrick 7.5%·Wheaton 5.5%·Northern Star 4.5%·Kinross 3.8% 등 top 10이 80%+ 차지. 평균 PE 13.2x, dividend yield 1.8%. 광산 sector 인식 시차 노출을 single ticker로 분산 가능. Expense ratio 0.51%.",
        "revenue_segments": [
            ("Senior Producers (Tier-1)", 65, "NEM·AEM·GOLD·Northern Star — annual 1Moz+ 생산"),
            ("Mid-tier Producers", 20, "KGC·B2Gold·AU·등"),
            ("Royalty/Streaming", 12, "FNV·WPM — 자본 효율 ↑"),
            ("Junior/Small-cap", 3, "exploration upside"),
        ],
        "global_position": "글로벌 #1 금광 sector ETF (Vanguard·iShares 동급 ETF 대비 AUM 2x+). 2024 inflow $2.8B YTD — 18-month high.",
        "key_customers": ["retail investors (gold sector exposure)", "pension funds (inflation hedge allocation)", "macro hedge funds (tactical sector trade)"],
        "key_competitors": ["GDXJ (junior miners)", "RING (BlackRock)", "SGDM (sprout direxion)", "GOEX"],
    },
    "FCX": {
        "overview": "Freeport-McMoRan은 글로벌 구리 #1 (Codelco·Glencore 다음). 2026년 기준 연 구리 4.2Blbs + 금 1.4Moz + 몰리브덴 80Mlbs 생산. 핵심 자산: Indonesia Grasberg (세계 최대 단일 구리·금 광산), Cerro Verde (페루), Morenci/Bagdad (애리조나). 구리는 EV (대당 80kg)·데이터센터 (서버랙 50kg+)·신재생 grid·인프라 megatrend의 직접 수혜. 2025 ROIC 18% 신기록.",
        "revenue_segments": [
            ("North America (Morenci·Bagdad·Sierrita)", 35, "Arizona open-pit 대형 광산"),
            ("South America (Cerro Verde·El Abra)", 25, "Peru·Chile copper"),
            ("Indonesia (Grasberg)", 35, "세계 최대 단일 광산, 51% 정부 지분"),
            ("Smelting & Refining", 5, "Atlantic Copper (Spain) + Indonesia Smelter"),
        ],
        "global_position": "글로벌 구리 #3 (Codelco·Glencore 다음, BHP·Anglo American과 경쟁). 미국 internal 구리 생산 1위. 몰리브덴 글로벌 1위.",
        "key_customers": ["LME copper exchange", "Glencore (trading)", "Atlantic Copper smelter", "Chinese smelters"],
        "key_competitors": ["BHP Group (BHP)", "Rio Tinto (RIO)", "Anglo American", "Codelco (state)", "Glencore"],
    },
    "TECK": {
        "overview": "Teck Resources Limited은 캐나다 본사의 metals & mining major. 2024년 coal 자산(Glencore $7.0B에 매각) 후 pure copper play로 재포지셔닝. 핵심 자산: Quebrada Blanca Phase 2 (칠레 — 구리 290kt/년 ramp 진행), Highland Valley (캐나다 BC — 구리 145kt/년), Antamina (페루 22.5% 지분 — 구리·아연), Carmen de Andacollo (칠레). 2026 생산 구리 400kt + 아연 600kt + 몰리브덴 12kt. Coal 매각 자금으로 자사주 매입 $1.5B + dividend hike.",
        "revenue_segments": [
            ("Copper (Chile·Canada·Peru)", 65, "QB2 ramp 도달 시 1순위 segment"),
            ("Zinc & Lead (Red Dog Alaska·Trail BC)", 25, "Red Dog 세계 1위 zinc 광산"),
            ("Molybdenum & 기타", 10, "by-product"),
        ],
        "global_position": "Copper Tier-1 producer 7-8위 (BHP·Rio·Anglo·FCX·Codelco·Glencore 다음). Zinc 글로벌 #1 (Red Dog).",
        "key_customers": ["smelters (China·Korea·Japan)", "Glencore (trading)", "LME exchange"],
        "key_competitors": ["Freeport-McMoRan (FCX)", "BHP", "Rio Tinto", "Anglo American", "First Quantum"],
    },
    "2351.TW": {
        "overview": "SDI Corporation(大山電子, 대산전자)은 1989년 설립된 대만 1위 리드프레임(lead frame) 제조사. 자동차 전장·산업용 반도체 패키징 핵심 부품 공급. 2026년 AI 데이터센터 800V HVDC 전환과 함께 매출 mix가 자동차(65%+)에서 AI 서버 segment로 빠르게 이동 중 — AI 매출 비중이 2025년 1% → 2026년 1분기 6%로 한 분기에 6배 점프. HVDC용 고출력 리드프레임 customization 40개+ projects 양산 진입. 시총 약 USD 35B, Taiwan TWSE 상장.",
        "revenue_segments": [
            ("자동차 (Auto)", 65, "EV·ADAS·산업 모터 드라이버 — Infineon·STMicro·NXP 등 IDM 공급"),
            ("산업·소비전자 (Industrial)", 25, "산업 모터·white goods·소비전자 power IC"),
            ("AI 서버 (HVDC)", 6, "800VDC 전력반도체 lead frame — 2025 1% → 2026 Q1 6% ramp"),
            ("기타", 4, "test sockets·기타 패키지 component"),
        ],
        "global_position": "Taiwan lead frame #1 (글로벌 share ~12%, Mitsui High-tec·ASM Pacific 다음 글로벌 #3). HVDC 영역에서는 IDM customer 40+ projects 양산으로 시장 선점.",
        "key_customers": ["Infineon Technologies (IFX.DE)", "STMicroelectronics (STM)", "NXP Semiconductors", "Onsemi", "Tesla (간접)"],
        "key_competitors": ["Mitsui High-tec (6966.T)", "ASM Pacific (0522.HK)", "HAESUNG DS (195870.KS)", "Jih Lin Technology (6204.TPEx)", "Shinko Electric (6967.T)"],
    },
    "195870.KS": {
        "overview": "해성디에스(HAESUNG DS)는 한국 lead frame·패키지 substrate 시장 1위 (한국 share 70%+). 자동차 전장(현대모비스·LG에너지솔루션) + 메모리·AI 패키지 substrate dual 사업으로 자동차 cyclical + AI structural dual driver 보유. 2016년 KOSPI 상장, 시총 ₩1.4T 중소형주로 한국 투자자에게는 대만 SDI Corp/Jih Lin Technology의 가장 직접적 proxy.",
        "revenue_segments": [
            ("자동차 lead frame", 60, "현대모비스·LG에너지솔루션·자동차 IDM 공급 — EV/HEV power"),
            ("Package Substrate", 28, "메모리 패키지 substrate (DDR5·HBM) + AI/server"),
            ("산업·소비전자", 8, "산업 모터·white goods·소비전자 IC"),
            ("기타", 4, "test·신규 사업"),
        ],
        "global_position": "한국 lead frame #1, 글로벌 share ~5%. 자동차 segment에서 현대차그룹 lock-in customer. AI 메모리 substrate에서는 Samsung Electro-Mechanics와 경쟁.",
        "key_customers": ["현대모비스 (012330.KS)", "LG에너지솔루션 (373220.KS)", "SK하이닉스 (000660.KS)", "Samsung Electronics", "Infineon (간접)"],
        "key_competitors": ["Samsung Electro-Mechanics (009150.KS)", "Mitsui High-tec (6966.T)", "Shinko Electric (6967.T)", "SDI Corporation (2351.TW)"],
    },
    "IFX.DE": {
        "overview": "Infineon Technologies AG는 독일 본사 글로벌 #1 power semiconductor IDM (SiC·IGBT·MOSFET 합산 점유율 18-22%). 1999년 Siemens semiconductor 분사, 2000년 Frankfurt 상장. 2020년 Cypress Semiconductor 인수로 자동차 MCU + 무선 connectivity 확장. 자동차(52%)·산업(22%)·소비전자/AI DC(14%)·보안(12%) multi-segment. 2026년 AI 데이터센터 800VDC PSU·SST 시장 공략 본격화 — 본문(의교창 글)에서 대만 lead frame 업체 핵심 customer로 명시.",
        "revenue_segments": [
            ("Automotive (ATV)", 52, "EV·ADAS·MCU — SiC AURIX·CoolSiC portfolio"),
            ("Industrial (IPC)", 22, "산업 모터·태양광·BESS·전력 인프라"),
            ("Power & Sensor Systems (PSS)", 14, "AI DC PSU + 소비전자 전력"),
            ("Connected Secure Systems (CSS)", 12, "보안 IC·결제·IoT connectivity"),
        ],
        "global_position": "글로벌 power semi #1 (Infineon 20% / STMicro 15% / Onsemi 12% / NXP 8%). SiC 시장에서는 STMicro 다음 #2. Cypress 통합 후 MCU 시장 #4.",
        "key_customers": ["Tesla", "BYD", "Volkswagen", "Bosch", "글로벌 자동차 OEM 다수", "Schneider Electric (AI DC)", "Vertiv"],
        "key_competitors": ["STMicroelectronics (STM)", "Onsemi (ON)", "NXP Semiconductors (NXPI)", "Renesas (6723.T)", "Wolfspeed (WOLF)"],
    },
    "STM": {
        "overview": "STMicroelectronics N.V.는 1987년 SGS Microelettronica(이탈리아)와 Thomson Semiconducteurs(프랑스)의 합병으로 설립된 유럽 #1 IDM. 본사 스위스(Geneva), Euronext Paris·Milan·NYSE 동시 상장. 글로벌 SiC capacity #1 — Tesla 차량용 SiC 공급으로 SiC market leader 확립. 자동차·산업(45%)·MEMS/센서(28%)·MCU/디지털(22%) multi-segment. 본문에서 대만 lead frame 업체 핵심 customer로 명시.",
        "revenue_segments": [
            ("Automotive & Discrete (ADG)", 45, "SiC #1 (Tesla 공급) + 자동차 MCU·전력"),
            ("Analog/MEMS/Sensors (AMS)", 28, "스마트폰 MEMS·이미지 센서·imaging"),
            ("Microcontrollers & Digital ICs (MDG)", 22, "STM32 MCU portfolio + AI edge"),
            ("기타", 5, ""),
        ],
        "global_position": "글로벌 power semi #2 (Infineon 다음). SiC 시장 #1 — Tesla 차세대 차량 단독 공급 contract. 자동차 MCU에서는 NXP·Renesas와 경쟁.",
        "key_customers": ["Tesla", "Apple (MEMS)", "Bosch", "Continental", "글로벌 자동차 OEM 다수"],
        "key_competitors": ["Infineon (IFX.DE)", "Onsemi (ON)", "NXP (NXPI)", "Wolfspeed (WOLF)", "Renesas (6723.T)"],
    },
    "AMKR": {
        "overview": "Amkor Technology, Inc.는 글로벌 #2 OSAT(반도체 후공정 외주) — Taiwan ASE 다음 시장 share ~13%. 1968년 한국 안양에서 설립(원래 명칭 '아남산업'), 현재 미국 본사·NASDAQ 상장이지만 한국·필리핀·중국·베트남에 생산기지. 자동차·HPC·통신·소비전자 multi-segment 패키징. 2026년 AI advanced packaging(CoWoS·FOPLP·HBM substrate) ramp 진입.",
        "revenue_segments": [
            ("자동차·산업 (Auto/Industrial)", 38, "EV·ADAS·산업용 IC 패키징 — 안정 base"),
            ("Communications", 28, "Apple modem·5G RF·스마트폰 SoC"),
            ("Computing (PC·HPC)", 22, "AI accelerator·서버 CPU/GPU·메모리"),
            ("Consumer", 12, "TV·가전·웨어러블"),
        ],
        "global_position": "글로벌 OSAT #2 (ASE 30% / Amkor 13% / JCET 12%). Apple modem 패키징 단독 공급 (~20% revenue concentration). Vietnam Bac Ninh 신규 fab 2025-2027 ramp.",
        "key_customers": ["Apple (modem·SoC)", "Qualcomm", "Tesla", "글로벌 IDM 다수 (Infineon·STMicro 간접)", "NVIDIA (간접)"],
        "key_competitors": ["ASE Group (3711.TW)", "JCET Group (600584.SS)", "Powertech (6239.TW)", "SPIL (ASE 자회사)"],
    },
}


# Curated Korean translations of yfinance longBusinessSummary
# Add new tickers as needed.
BUSINESS_SUMMARY_KO: dict[str, str] = {
    "010140.KS": (
        "삼성중공업은 전 세계를 대상으로 조선·해양·에너지 인프라 사업을 영위한다. "
        "LNG 운반선·LNG-FSRU·소형 LNG bunkering vessel·VLEC(에탄)·VLAC(암모니아)·LCO2 운반선, "
        "컨테이너선·원유·셔틀 탱커·북극 셔틀 탱커·석유/케미컬 운반선·풍력 발전기 설치선 등 다양한 선종을 건조한다. "
        "해양 부문은 FLNG(부유식 LNG)·FPSO(부유식 생산·저장·하역 설비)·FPU(부유식 생산 유닛)·TLP·드릴십·반잠수식 드릴링 리그 등 "
        "심해 에너지 인프라 풀라인을 보유한다. 2026년부터는 부유식 해상 데이터센터(FDC) 50MW 개념설계 ABS·LR 동시 인증 "
        "(한국 최초·세계 두 번째)을 발판으로 신시장에 진입하고 있다."
    ),
    "TSLA": (
        "Tesla는 전기차·에너지 저장·태양광 사업을 영위하는 글로벌 클린에너지 기업이다. "
        "Model S/3/X/Y/Cybertruck 등 EV 라인업과 Solar Roof·Powerwall·Megapack 에너지 저장 솔루션을 판매한다. "
        "FSD(완전자율주행)·Optimus 휴머노이드 로봇·Dojo AI 슈퍼컴퓨터로 모빌리티·AI 인프라 사업을 확장 중. "
        "Musk가 이끄는 SpaceX(우주 발사·Starlink)와 xAI(Grok LLM)는 Tesla의 형제 회사로, "
        "SpaceX V3 Starship·페로브스카이트 태양광·우주 데이터센터 분야에서 vertical integration이 진행 중. "
        "Trump-Musk 친밀도로 우주산업 규제 청신호 + Space Force 예산 확대로 우주 분야 추가 catalyst 확보."
    ),
    "FSLR": (
        "First Solar는 미국 최대 박막(CdTe) 솔라 셀·모듈 제조업체. AZ·OH 신공장 8GW+ 양산 capacity 보유. "
        "IRA Section 45X 보조금($0.07/W = 연간 $350M 안정 수익) 2032년까지 lock-in. "
        "CdTe 박막에서 페로브스카이트-실리콘 탠덤 셀(35.2% 효율 NREL 인증, 2026-01)로 진화 중. "
        "미국 ITAR 우주용 라이선스 + SpaceX-xAI 우주 솔라 공급망 단독 후보. "
        "2025년 매출 $5B·영업이익률 30%+·백로그 $25B 사상최대로 2028년까지 수주 가시성 확보."
    ),
    "014680.KS": (
        "한솔케미칼은 한국의 중견 화학 소재 기업으로, 반도체·디스플레이·솔라 3대 영역에서 사업한다. "
        "Fine chemicals(과산화수소·하이드로설파이트·벤조일 퍼옥사이드·라텍스·응집제), "
        "반도체 소재(High-k·실리콘·전극 메탈 프리커서), 디스플레이 소재(quantum dot 등) 라인을 보유한다. "
        "HBM4 SK하이닉스 공급 확정(2026-01)으로 HBM cycle 회복 수혜 + "
        "페로브스카이트 도판트·전자수송층(ETL) 신규 라인 가동(2026-04)으로 우주용 셀 third-source 진입 가능성. "
        "UNIST·KAIST 페로브스카이트 R&D 네트워크 활용. 영업이익률 15%+ 안정 유지."
    ),
    "9104.T": (
        "MOL(미쓰이 OSK 라인즈)은 일본 3대 해운사 중 하나로 글로벌 해운·물류 사업을 영위한다. "
        "LNG 운반선·자동차 운반선(PCTC, 100+척)·드라이 벌크·컨테이너·탱커 풀라인 운영. "
        "MOL+Hitachi+NYK+NTT 4사 컨소시엄으로 부유식 해상 데이터센터(FDC) first-mover 지위 확보 — "
        "9,731톤 PCTC 개조 FDC 1호선 2027년 가동 목표. 일본 정부 GX(Green Transformation) "
        "8조엔 자금 backdrop. 엔/달러 150 유지 시 export 우호 매크로 환경."
    ),
    "NEM": (
        "Newmont Corporation은 글로벌 1위 금광 기업으로 2026년 기준 연 6.0Moz의 금을 생산한다. "
        "2024년 Newcrest Mining $19B 인수로 호주·캐나다·미국·페루·가나·서아프리카·인도네시아 7개 jurisdiction의 "
        "16개 광산 portfolio를 보유한다. AISC $1,400-1,500/oz 환경에서 gold $4,400+ 시 operating margin 30%+ 보장. "
        "Tier-1 자산 비중·net debt/EBITDA 0.5x로 sector 최우량 재무. 2025년 dividend $1.20/년 + buyback $1B 등 capital return 강화 단계."
    ),
    "AEM": (
        "Agnico Eagle Mines는 캐나다 본사의 금광 quality leader로 2026년 기준 연 3.5Moz 금을 생산한다. "
        "2022년 Kirkland Lake와 $11B 합병 후 portfolio 2.6x 확장. 캐나다·핀란드·멕시코·호주 등 안전한 jurisdiction에 집중하여 sovereign risk를 최소화한다. "
        "AISC $1,290/oz로 industry 최저 수준이며 Net debt/EBITDA 0.3x는 광산 sector 중 최우량 재무. 'Tier-1 ounces only' 전략을 명시한다."
    ),
    "GDX": (
        "VanEck Gold Miners ETF (GDX)는 글로벌 51개 금광 기업 시총 가중 ETF다. AUM $24B (2026.5). "
        "Newmont 12.5%·Agnico Eagle 10.8%·Franco-Nevada 8.5%·Barrick 7.5% 등 top 10이 80% 차지. 평균 PE 13.2x, dividend yield 1.8%. "
        "광산 sector 인식 시차 노출을 단일 ticker로 분산 가능하며 expense ratio 0.51%. 2026 YTD ETF inflow $2.8B로 18개월 high."
    ),
    "FCX": (
        "Freeport-McMoRan은 글로벌 구리 #3로 2026년 기준 연 구리 4.2Blbs + 금 1.4Moz + 몰리브덴 80Mlbs를 생산한다. "
        "핵심 자산은 Indonesia Grasberg (세계 최대 단일 구리·금 광산, PT-FI 51% 정부 지분), Peru Cerro Verde, Arizona Morenci·Bagdad. "
        "구리는 EV (대당 80kg, ICE 23kg)·데이터센터 (서버랙 50kg+)·신재생 grid·인프라 4대 megatrend의 직접 수혜. 2025 ROIC 18% 신기록·OPM 36.8%."
    ),
    "TECK": (
        "Teck Resources Limited은 캐나다 본사의 metals & mining major. 2024년 coal 자산을 Glencore에 $7.0B로 매각한 후 pure copper play로 재포지셔닝. "
        "핵심 자산은 Quebrada Blanca Phase 2 (칠레 — 구리 290kt/년 ramp 진행), Highland Valley (캐나다 BC — 구리 145kt/년), Antamina (페루 22.5% 지분), Carmen de Andacollo (칠레). "
        "2026 생산 구리 400kt + 아연 600kt + 몰리브덴 12kt. Coal 매각 자금 $7B로 자사주 매입 $1.5B + dividend hike."
    ),
}


def _load_openai_key() -> str:
    """OPENAI_API_KEY를 env 또는 .env에서 로드 (LLM 번역용)."""
    import os
    from pathlib import Path as _Path
    k = os.environ.get("OPENAI_API_KEY")
    if k:
        return k
    candidates = [_Path.cwd() / ".env"]
    pd = os.environ.get("CLAUDE_PROJECT_DIR")
    if pd:
        candidates.append(_Path(pd) / ".env")
    candidates.append(_Path(__file__).resolve().parent.parent.parent.parent.parent / ".env")
    for ep in candidates:
        if ep.exists():
            for line in ep.read_text().splitlines():
                if line.strip().startswith("OPENAI_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


def _translate_business_summary_to_korean(en_text: str, ticker: str = "") -> str:
    """yfinance 영문 longBusinessSummary → 한글 번역 (7일 캐시, gpt-4o-mini tier_cheap).

    Cost: 약 $0.0001~0.0005/번역 (한 번 캐시 후 7일 재사용).
    Failures (no API key, network error) → 빈 문자열 silent fallback.
    """
    if not en_text or len(en_text.strip()) < 30:
        return ""

    import time
    from pathlib import Path as _Path
    cache_dir = _Path.home() / ".cache" / "yfinance_profiles"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{ticker.replace('.', '_').replace('/', '_')}_ko.txt"

    if cache_path.exists() and (time.time() - cache_path.stat().st_mtime) < 7 * 86400:
        cached = cache_path.read_text(encoding="utf-8").strip()
        if cached:
            return cached

    api_key = _load_openai_key()
    if not api_key:
        return ""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = (
            "다음 영문 기업 사업 설명을 한국어로 자연스럽게 번역해 주세요. "
            "전문 투자 보고서 톤으로, 250~400자 분량. "
            "고유명사(시설명·지명·인명)는 그대로 두고, 회사명만 한글 병기.\n\n"
            f"영문:\n\"\"\"\n{en_text[:2500]}\n\"\"\"\n\n"
            "한글 번역 (자연스러운 한국어, 투자보고서 톤):"
        )
        resp = client.chat.completions.create(
            model="gpt-4o-mini",  # tier_cheap — 번역은 단순 작업
            messages=[
                {"role": "system", "content": "당신은 금융 전문 번역가입니다. 영문 기업 사업 설명을 자연스러운 한국어 투자보고서 톤으로 번역하세요."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
            temperature=0.3,
        )
        ko = resp.choices[0].message.content.strip()
        if ko:
            cache_path.write_text(ko, encoding="utf-8")
        return ko
    except Exception as e:
        # Silent fallback — print warning but don't break PDF build
        print(f"[company_intro] LLM translation failed for {ticker}: {type(e).__name__}: {str(e)[:80]}")
        return ""


def _fetch_yfinance_profile(ticker: str) -> dict:
    """Lazy fetch yfinance profile for the given ticker, with disk cache."""
    import json as _json
    from pathlib import Path as _Path
    import os as _os

    cache_dir = _Path.home() / ".cache" / "yfinance_profiles"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"{ticker.replace('.', '_').replace('/', '_')}.json"
    # 7-day cache
    import time as _time
    if cache_path.exists() and (_time.time() - cache_path.stat().st_mtime) < 7 * 86400:
        try:
            return _json.loads(cache_path.read_text())
        except Exception:
            pass
    if _os.environ.get("DISABLE_YF_PROFILE") == "1":
        return {}
    try:
        import yfinance as yf
        info = (yf.Ticker(ticker).info or {})
        profile = {
            "longName": info.get("longName", ""),
            "sector": info.get("sector", ""),
            "industry": info.get("industry", ""),
            "employees": info.get("fullTimeEmployees"),
            "country": info.get("country", ""),
            "website": info.get("website", ""),
            "city": info.get("city", ""),
            "businessSummary": (info.get("longBusinessSummary") or "")[:2500],
        }
        cache_path.write_text(_json.dumps(profile, ensure_ascii=False, indent=2))
        return profile
    except Exception:
        return {}


def _load_profile_json(ticker: str) -> dict:
    """Load company_profile/{ticker}.json generated by specialist-agents:company-deep-profile.

    Returns dict with same schema as COMPANY_INTROS entries, or empty.
    Env: COMPANY_PROFILE_DIR (path to company_profile/ directory)
    """
    import os as _os
    import json as _json
    from pathlib import Path as _Path

    profile_dir = _os.environ.get("COMPANY_PROFILE_DIR")
    if not profile_dir:
        return {}
    p = _Path(profile_dir) / f"{ticker}.json"
    if not p.exists():
        return {}
    try:
        data = _json.loads(p.read_text())
        # Convert revenue_segments from list-of-dicts (new schema) to list-of-tuples (legacy)
        rs = data.get("revenue_segments", [])
        if rs and isinstance(rs[0], dict):
            data["revenue_segments"] = [(s.get("name", "-"), s.get("share_pct", 0), s.get("note", "")) for s in rs]
        return data
    except Exception:
        return {}


def render_company_intro(ticker: str) -> str:
    """Return HTML for company intro section with yfinance enrichment.

    Priority:
      1. COMPANY_INTROS hardcoded dict (manual curation)
      2. company_profile/{ticker}.json (specialist-agents auto-generated)
      3. yfinance metadata only
    """
    intro = COMPANY_INTROS.get(ticker, {})
    # Fallback to auto-generated profile if hardcoded miss
    if not intro:
        intro = _load_profile_json(ticker)
    profile = _fetch_yfinance_profile(ticker)

    # Skip if no data anywhere
    if not intro and not profile:
        return ""

    seg_rows = "".join(
        f"""<tr>
              <td><strong>{seg[0]}</strong></td>
              <td style="text-align:right;">{seg[1]}%</td>
              <td style="font-size:9pt;">{seg[2]}</td>
            </tr>"""
        for seg in intro.get("revenue_segments", [])
    )

    customers = " · ".join(intro.get("key_customers", []))
    competitors = " · ".join(intro.get("key_competitors", []))

    # ── Sprint E-4 helper: paragraph → bullet point ─────────────────
    def _to_bullets(text: str, min_len: int = 12) -> str:
        """문장을 분리 → ul/li. 마침표/줄바꿈 기준 split."""
        import re as _re
        if not text or not text.strip():
            return ""
        # Already contains <ul> or <li>? — leave as-is
        if "<ul" in text or "<li" in text:
            return text
        # Split on 마침표·줄바꿈
        # 한글 문장 끝 후보: ".", "다.", "음.", "함." 등
        parts = _re.split(r"(?<=다[.])\s+|(?<=음[.])\s+|(?<=함[.])\s+|(?<=[.])\s+(?=[A-Z가-힣])|\n+", text)
        items = [p.strip() for p in parts if p and len(p.strip()) >= min_len]
        if len(items) <= 1:
            return text  # 단일 문장이면 그대로
        lis = "".join(f"<li style='margin-bottom:4pt;'>{it}</li>" for it in items)
        return f"<ul style='margin:4pt 0 0 0;padding-left:18pt;'>{lis}</ul>"

    # Korean translation block (curated)
    ko_summary = BUSINESS_SUMMARY_KO.get(ticker, "")
    ko_block = ""
    if ko_summary:
        ko_block = f"""
        <h3>사업 내용 상세 (한글)</h3>
        <div class="info" style="font-size:10pt;line-height:1.7;">{_to_bullets(ko_summary)}</div>
        <p style="font-size:8pt;color:#6b7280;">출처: yfinance longBusinessSummary 한글 번역·확장 (curated)</p>
        """

    # yfinance enrichment block
    yf_block = ""
    if profile and profile.get("businessSummary"):
        meta_rows = []
        if profile.get("longName"):
            meta_rows.append(f"<tr><th style='width:14%'>법인명</th><td>{profile['longName']}</td></tr>")
        if profile.get("sector") or profile.get("industry"):
            meta_rows.append(f"<tr><th>섹터·산업</th><td>{profile.get('sector','')} · {profile.get('industry','')}</td></tr>")
        if profile.get("country") or profile.get("city"):
            meta_rows.append(f"<tr><th>본사</th><td>{profile.get('city','')}, {profile.get('country','')}</td></tr>")
        if profile.get("employees"):
            try:
                emp = f"{int(profile['employees']):,}명"
            except Exception:
                emp = str(profile['employees'])
            meta_rows.append(f"<tr><th>직원 수</th><td>{emp}</td></tr>")
        if profile.get("website"):
            meta_rows.append(f"<tr><th>웹사이트</th><td><a href='{profile['website']}'>{profile['website']}</a></td></tr>")

        yf_block = f"""
        <h3>회사 메타데이터 (yfinance 자동 수집)</h3>
        <table class="dt">{''.join(meta_rows)}</table>

        {ko_block}

        <h3>사업 내용 원문 (longBusinessSummary · 영문)</h3>
        <div class="info" style="font-size:9pt;line-height:1.6;color:#4b5563;">{profile['businessSummary']}</div>
        <p style="font-size:8pt;color:#6b7280;">출처: yfinance API (Yahoo Finance) · 7일 캐시 · 영문 원문 (한글 번역은 위 섹션)</p>
        """

    # Naver/Korean source link block for KR tickers
    naver_block = ""
    if ticker.endswith((".KS", ".KQ")):
        code = ticker.split(".")[0]
        naver_block = f"""
        <h3>한국 시장 추가 정보 소스</h3>
        <ul style="font-size:9.5pt;line-height:1.7;">
          <li>네이버 금융 — <a href="https://finance.naver.com/item/main.naver?code={code}">finance.naver.com/item/main.naver?code={code}</a> (시세·기업개요·재무·공시)</li>
          <li>DART 전자공시 — <a href="https://dart.fss.or.kr/dsab007/main.do?option=corp&textCrpNm={code}">dart.fss.or.kr 종목검색</a> (사업보고서·반기·분기·공시)</li>
          <li>FnGuide — <a href="https://comp.fnguide.com/SVO2/ASP/SVD_main.asp?gicode=A{code}">comp.fnguide.com/SVO2/ASP/SVD_main.asp?gicode=A{code}</a> (재무·valuation·peer 비교)</li>
        </ul>
        """

    # Sprint A-3 (2026-05-28): "사업 개요 (요약)" auto-fill via LLM 번역
    # Priority: curated COMPANY_INTROS.overview → LLM 번역(yfinance EN summary) → '-'
    overview_summary = intro.get('overview', '') or ''
    if not overview_summary and profile and profile.get('businessSummary'):
        # 자동 한글 번역 (gpt-4o-mini, 7일 캐시 — cost 거의 0)
        ko_translated = _translate_business_summary_to_korean(profile['businessSummary'], ticker)
        if ko_translated:
            overview_summary = ko_translated

    return f"""
    <h2>📋 회사 소개 (Company Profile)</h2>

    <h3>사업 개요 (요약)</h3>
    <div class="info" style="font-size:10.5pt;line-height:1.7;">{_to_bullets(overview_summary) or '-'}</div>

    {yf_block}

    <h3>매출 구조 (Segment 비중)</h3>
    <table class="dt">
      <thead><tr><th style="width:30%">Segment</th><th style="width:12%">비중</th><th>설명</th></tr></thead>
      <tbody>{seg_rows or '<tr><td colspan="3" style="text-align:center;color:#9ca3af;">segment 비중 데이터 부재 — 회사 IR 또는 사업보고서 참조</td></tr>'}</tbody>
    </table>

    <h3>글로벌 위치</h3>
    <p style="font-size:10pt;line-height:1.6;">{intro.get('global_position', '-')}</p>

    <h3>주요 고객 / 경쟁사</h3>
    <table class="dt">
      <tr><th style="width:14%">주요 고객</th><td>{customers or '데이터 부재'}</td></tr>
      <tr><th>주요 경쟁사</th><td>{competitors or '데이터 부재'}</td></tr>
    </table>

    {naver_block}
    """
