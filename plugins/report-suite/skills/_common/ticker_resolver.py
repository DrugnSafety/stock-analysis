"""Ticker → company name resolver.

Provides format_ticker_with_name(ticker) that returns "005490.KS POSCO홀딩스"
instead of just "005490.KS".

Resolution order:
  1. Curated KR/Global map (fast, hardcoded for major tickers)
  2. yfinance info.longName / shortName (network call, cached)
  3. Fallback: ticker only

Cache: in-memory dict (process lifetime). Persistent JSON cache at
~/.cache/ticker_resolver.json prevents redundant yfinance calls.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Optional

# ── 1. Curated map for major Korean / Global tickers ──────────────────────
# Hardcoded for speed and to avoid yfinance "Not Found" issues
CURATED: dict[str, dict[str, str]] = {
    # OSV 공급절벽 테마 (sungdory 2026-07-27 · FPSO 생산지원 + 고사양 PSV/AHTS 공급부족)
    "TDW": {"kr": "타이드워터", "en": "Tidewater Inc.", "sector": "Offshore Support Vessel (글로벌 OSV 대장주 · PSV/AHTS 최대 선대 · 공급절벽 최순수 노출)"},
    "SEA1.OL": {"kr": "SEA1 오프쇼어", "en": "SEA1 Offshore ASA", "sector": "Offshore Support Vessel (구 Solstad Offshore · 브라질·북해 PSV/AHTS 장기계약 레버리지)"},
    "SOFF.OL": {"kr": "솔스타드 마리타임", "en": "Solstad Maritime ASA", "sector": "Offshore Support Vessel / Subsea (CSV 중심 · Petrobras subsea 수요 수혜 · OSV 혼합)"},
    "RIG": {"kr": "트랜스오션", "en": "Transocean Ltd.", "sector": "Offshore Drilling (울트라딥워터 드릴십 최대 선대 · OSV 수요의 상류 드라이버 · 고베타)"},
    "XES": {"kr": "SPDR 오일·가스 장비/서비스 ETF", "en": "SPDR S&P Oil & Gas Equipment & Services ETF", "sector": "Energy Services ETF (동일가중 · TDW 상위 편입 · OSV/서비스 테마 분산 노출)"},
    "RGTI": {"kr": "리게티 컴퓨팅", "en": "Rigetti Computing, Inc.", "sector": "Quantum Computing (초전도 큐비트 풀스택 · 美 상무부 ~$1억 배정 수혜 · 양자컴 순수 플레이)"},
    "QBTS": {"kr": "디웨이브 퀀텀", "en": "D-Wave Quantum Inc.", "sector": "Quantum Computing (양자 어닐링 + 게이트형 · 상업 QC 매출 선두 · 美 상무부 ~$1억 배정 수혜)"},
    "IONQ": {"kr": "아이온큐", "en": "IonQ, Inc.", "sector": "Quantum Computing (트랩 이온 방식 · 양자컴 최대 순수 플레이 시총 · 미 국책 간접 수혜)"},
    "IBM": {"kr": "IBM", "en": "International Business Machines Corporation", "sector": "IT Services / Quantum (IBM Quantum 로드맵 · 분사기업 $10억 배정 · 행정명령 서명식 배석)"},
    "GFS": {"kr": "글로벌파운드리스", "en": "GlobalFoundries Inc.", "sector": "Semiconductor Foundry (미국 특수공정 파운드리 · 양자칩 위탁생산 · 美 상무부 $3.75억 배정)"},
    "285490.KS": {"kr": "노바텍", "en": "Novatek Co., Ltd.", "sector": "Permanent Magnet (Nd-Fe-B 응용자석 · 비희토류 자석 양산 · 베트남 깐안 자석공장 + 라오스 광산 MOU 수직계열화)"},
    "008730.KQ": {"kr": "유니온머티리얼", "en": "Union Materials Corp.", "sector": "Permanent Ferrite/Magnetic Materials (페라이트 마그넷 · 희토류 테마 대장주 · MLCC용 자성소재)"},
    "NDA.DE": {"kr": "아우루비스", "en": "Aurubis AG", "sector": "Copper Smelter / Sulphuric Acid (유럽 1위 동제련, 분기 reset H2SO4)"},
    "MOS": {"kr": "모자이크", "en": "The Mosaic Company", "sector": "Fertilizer (Phosphate / Potash · H2SO4 buyer · 미 200만t 감산)"},
    "BRK-B": {"kr": "버크셔 해서웨이", "en": "Berkshire Hathaway Inc. Class B", "sector": "Diversified Holdings (Insurance/Energy/Rail)"},
    # Korea — 건강기능식품 ODM (jhlimidea K-건기식 수출 모멘텀 thesis, 2026-06-05)
    "194700.KQ": {"kr": "노바렉스", "en": "NOVAREX Co., Ltd.", "sector": "건강기능식품 ODM / 개별인정형 원료 (수출 38%·내수성장)"},
    "222040.KQ": {"kr": "코스맥스엔비티", "en": "Cosmax NBT, Inc.", "sector": "건강기능식품 ODM / 글로벌(美 댈러스·濠 멜버른 공장)·OBM"},
    "008490.KS": {"kr": "서흥", "en": "Suheung Co., Ltd.", "sector": "하드캡슐 / 건강기능식품 ODM (수출비중 1위 43%·PBR 딥밸류)"},
    "200130.KQ": {"kr": "콜마비앤에이치", "en": "Kolmar BNH Co., Ltd.", "sector": "건강기능식품 ODM·OBM (헤모힘 개별인정형 수출)"},
    "044820.KQ": {"kr": "코스맥스비티아이", "en": "Cosmax BTI Inc.", "sector": "화장품·건기식 지주 (코스맥스엔비티 모회사)"},
    "BRBR": {"kr": "벨링브랜즈", "en": "BellRing Brands, Inc.", "sector": "단백질 보충제 브랜드 (Premier Protein / 美 GLP-1 수혜)"},
    # Korea — 화장품 ODM·브랜드 (khiro38 워렌넝구 K-뷰티 수출 구조적 성장 thesis, 2026-06-10)
    "192820.KS": {"kr": "코스맥스", "en": "Cosmax, Inc.", "sector": "화장품 ODM 글로벌 1위 (中·美·동남아 생산기지 / Anua·COSRX 등 인디브랜드 위탁생산)"},
    "161890.KS": {"kr": "한국콜마", "en": "Kolmar Korea Co., Ltd.", "sector": "화장품 ODM (선케어 강점 / 美 PA 공장 / HK이노엔 제약 자회사)"},
    "241710.KS": {"kr": "코스메카코리아", "en": "Cosmecca Korea Co., Ltd.", "sector": "화장품 ODM (美 Englewood 잉글우드랩 자회사 / 北美 직접생산)"},
    "278470.KS": {"kr": "에이피알", "en": "APR Corporation", "sector": "뷰티테크 브랜드 (메디큐브 AGE-R 디바이스 / 美 직진출 고성장·고베타)"},
    "090430.KS": {"kr": "아모레퍼시픽", "en": "Amorepacific Corporation", "sector": "화장품 대형 브랜드 (라네즈·설화수·COSRX 인수 / 美·日 리오프닝)"},
    "GL9.IR": {"kr": "글랜비아", "en": "Glanbia plc", "sector": "유청단백 원료·뉴트리션 (Optimum Nutrition / GLP-1 upstream)"},
    # Korea — Casino / Hotel / Integrated Resort (jp187 파라다이스 카지노 순환매 thesis)
    "034230.KQ": {"kr": "파라다이스", "en": "Paradise Co., Ltd.", "sector": "Foreigner-only Casino / Integrated Resort (파라다이스시티)"},
    "034230.KS": {"kr": "파라다이스", "en": "Paradise Co., Ltd.", "sector": "Foreigner-only Casino / Integrated Resort (파라다이스시티) · KOSDAQ"},
    "114090.KS": {"kr": "GKL(그랜드코리아레저)", "en": "Grand Korea Leisure", "sector": "Foreigner-only Casino (세븐럭) / State-owned"},
    "032350.KS": {"kr": "롯데관광개발", "en": "Lotte Tour Development", "sector": "Casino / Integrated Resort (제주 드림타워) / Travel"},
    "035250.KS": {"kr": "강원랜드", "en": "Kangwon Land", "sector": "Domestic Casino (내국인) / Resort"},
    "008770.KS": {"kr": "호텔신라", "en": "Hotel Shilla", "sector": "Hotel / Duty-Free (TR) / Inbound Tourism"},
    # Korea — AI Data Center Value Chain (jp187 골드핑거 AIDC 밸류체인 + 하나증권 '데크크' 인뎁스, 2026-07-22)
    "119850.KQ": {"kr": "지엔씨에너지", "en": "GNC Energy Co., Ltd.", "sector": "DC 비상발전기 (국내 M/S 70~80% 준독점 / IDC 전원 인프라)"},
    "475150.KS": {"kr": "SK이터닉스", "en": "SK eternix Co., Ltd.", "sector": "재생에너지 발전·RE100 PPA (KKR SK 에너지전환 3조 투자 핵심 / DC 전력공급)"},
    "018260.KS": {"kr": "삼성에스디에스", "en": "Samsung SDS Co., Ltd.", "sector": "IT서비스·클라우드/DC 운영사업자 (KKR 1.2조 투자 / 삼성그룹 IT 계열)"},
    "005090.KS": {"kr": "SGC에너지", "en": "SGC Energy Co., Ltd.", "sector": "집단에너지·발전 (DC 부지+전력 동시공급 모델 구축 중)"},
    "006360.KS": {"kr": "GS건설", "en": "GS E&C Corporation", "sector": "건설 (DC 시공·MEP / 하나증권 DC 수혜 최선호)"},
    "012210.KQ": {"kr": "삼미금속", "en": "Sammi Metal Products Co., Ltd.", "sector": "형단조 (커넥팅로드 / DC 전력인프라용 엔진부품 개발 중)"},
    "006110.KS": {"kr": "삼아알미늄", "en": "Sama Aluminium Co., Ltd.", "sector": "알루미늄박 (DC용 ESS·커패시터 소재)"},
    "388050.KQ": {"kr": "지투파워", "en": "G2Power Co., Ltd.", "sector": "수배전반·소배전반 (AI DC 전력설비)"},
    "003720.KS": {"kr": "삼영", "en": "Samyoung Chemical Co., Ltd.", "sector": "커패시터 필름 (DC 전력변환 소재)"},
    "355690.KQ": {"kr": "에이텀", "en": "ATUM Co., Ltd.", "sector": "변압기 (DC 사업 인증 단계)"},
    "093320.KQ": {"kr": "케이아이엔엑스", "en": "KINX Inc.", "sector": "IX·IDC 트래픽 처리 / DC 운영사업자"},
    # Korea — Battery / Materials
    "005490.KS": {"kr": "POSCO홀딩스", "en": "POSCO Holdings", "sector": "Steel/Battery Materials"},
    # Korea — Energy Steel Pipe (OCTG) / LNG·Offshore Wind (mnmniana 휴스틸 고유가 thesis)
    "005010.KS": {"kr": "휴스틸", "en": "Husteel Co., Ltd.", "sector": "Energy Steel Pipe / OCTG / Line Pipe"},
    "306200.KS": {"kr": "세아제강", "en": "SeAH Steel Corporation", "sector": "Steel Pipe / Energy Line Pipe / Offshore"},
    "092790.KS": {"kr": "넥스틸", "en": "NEXTEEL Co., Ltd.", "sector": "OCTG / Energy Steel Pipe"},
    "100090.KS": {"kr": "SK오션플랜트", "en": "SK oceanplant Co., Ltd.", "sector": "Offshore Wind Substructure / Large Steel Pipe / Special Steel"},
    "017960.KS": {"kr": "한국카본", "en": "Hankuk Carbon Co., Ltd.", "sector": "LNG Carrier Insulation (보냉재) / Composite Materials"},
    "003670.KS": {"kr": "포스코퓨처엠", "en": "POSCO Future M", "sector": "Battery Materials"},
    "006400.KS": {"kr": "삼성SDI", "en": "Samsung SDI", "sector": "Battery"},
    "373220.KS": {"kr": "LG에너지솔루션", "en": "LG Energy Solution", "sector": "Battery"},
    "247540.KQ": {"kr": "에코프로비엠", "en": "EcoPro BM", "sector": "Battery Materials"},
    "086520.KQ": {"kr": "에코프로", "en": "EcoPro", "sector": "Battery Materials"},
    "066970.KQ": {"kr": "엘앤에프", "en": "L&F", "sector": "Battery Materials"},
    "051910.KS": {"kr": "LG화학", "en": "LG Chem", "sector": "Chemical/Battery"},
    "096770.KS": {"kr": "SK이노베이션", "en": "SK Innovation", "sector": "Refining/Battery"},

    # Korea — Semiconductor
    "005930.KS": {"kr": "삼성전자", "en": "Samsung Electronics", "sector": "Semiconductor"},
    "000660.KS": {"kr": "SK하이닉스", "en": "SK Hynix", "sector": "Memory Semiconductor"},
    "042700.KQ": {"kr": "한미반도체", "en": "Hanmi Semiconductor", "sector": "HBM TC Bonder / Semi Equipment"},
    "039030.KQ": {"kr": "이오테크닉스", "en": "EO Technics", "sector": "Semi Laser / Test Equipment"},
    "009150.KS": {"kr": "삼성전기", "en": "Samsung Electro-Mechanics", "sector": "MLCC / Camera Module / Substrate"},
    "4062.T": {"kr": "이비덴", "en": "Ibiden Co., Ltd.", "sector": "FC-BGA / IC Substrate / Ceramics"},
    "3037.TW": {"kr": "유니마이크론", "en": "Unimicron Technology", "sector": "FC-BGA / IC Substrate / PCB"},
    "011070.KS": {"kr": "LG이노텍", "en": "LG Innotek", "sector": "ABF 기판 / 카메라모듈 / 반도체 패키징 PCB"},
    "058470.KQ": {"kr": "리노공업", "en": "LEENO Industrial", "sector": "테스트 소켓 / 프로브카드 / 반도체 후공정 검사"},
    "131290.KQ": {"kr": "티에스이", "en": "TSE Co., Ltd.", "sector": "반도체 검사 / 프로브카드 / 인터페이스 보드"},
    "MRAAY": {"kr": "무라타제작소", "en": "Murata Manufacturing Co., Ltd. (ADR)", "sector": "MLCC / Passive Components"},
    "TTDKY": {"kr": "TDK", "en": "TDK Corporation (ADR)", "sector": "MLCC / Magnetic Components / Battery"},

    # Taiwan / US — Memory Semiconductor Niche (농구천재 Taiwan memory 1Q26 분석용)
    "2344.TW": {"kr": "윈본드일렉트로닉스", "en": "Winbond Electronics Corporation", "sector": "Niche Memory Semiconductor (Specialty DRAM/NAND)"},
    "8299.TWO": {"kr": "파이슨일렉트로닉스", "en": "Phison Electronics Corp.", "sector": "NAND Module/Controller"},
    "SIMO": {"kr": "실리콘모션", "en": "Silicon Motion Technology Corporation", "sector": "NAND Controller (Fabless)"},
    "MU": {"kr": "마이크론테크놀로지", "en": "Micron Technology Inc.", "sector": "Memory Semiconductor (DRAM/NAND IDM)"},

    # Korea — Shipbuilding / Heavy Industry
    "329180.KS": {"kr": "HD현대중공업", "en": "HD Hyundai Heavy Industries", "sector": "Shipbuilding"},
    "010140.KS": {"kr": "삼성중공업", "en": "Samsung Heavy Industries", "sector": "Shipbuilding"},
    "042660.KS": {"kr": "한화오션", "en": "Hanwha Ocean", "sector": "Shipbuilding"},
    "009540.KS": {"kr": "HD한국조선해양", "en": "HD Korea Shipbuilding & Offshore Engineering", "sector": "Shipbuilding"},
    "272210.KS": {"kr": "한화시스템", "en": "Hanwha Systems Co., Ltd.", "sector": "Defense Electronics (필리조선소 공동 인수·레이더/지휘통제)"},
    "HII": {"kr": "헌팅턴잉걸스", "en": "Huntington Ingalls Industries, Inc.", "sector": "US Naval Shipbuilding (미 해군 함정건조 1위)"},
    "267250.KS": {"kr": "HD현대", "en": "HD Hyundai", "sector": "Holding"},
    "439260.KS": {"kr": "대한조선", "en": "Daehan Shipbuilding", "sector": "Shipbuilding"},
    "010620.KS": {"kr": "HD현대미포", "en": "HD Hyundai Mipo", "sector": "Shipbuilding (delisted Dec 2025 due to merger)"},

    # Korea — Consumer Electronics / HVAC / Data Center Cooling (메르 FDC 분석용)
    "066570.KS": {"kr": "LG전자", "en": "LG Electronics Inc.", "sector": "Consumer Electronics / HVAC·Chiller (Data Center Cooling)"},

    # Japan — Shipping / FDC consortium (메르 FDC 분석용)
    "9104.T": {"kr": "미쓰이OSK라인즈", "en": "Mitsui O.S.K. Lines Ltd.", "sector": "Shipping / FDC (Floating Data Center) Consortium Lead"},
    "6501.T": {"kr": "히타치", "en": "Hitachi Ltd.", "sector": "Electronics / IT / Power Infrastructure (FDC Consortium)"},

    # Korea — Auto
    "005380.KS": {"kr": "현대차", "en": "Hyundai Motor", "sector": "Automobile"},
    "000270.KS": {"kr": "기아", "en": "Kia", "sector": "Automobile"},
    "012330.KS": {"kr": "현대모비스", "en": "Hyundai Mobis", "sector": "Auto Parts / 휴머노이드 액추에이터"},
    "086280.KS": {"kr": "현대글로비스", "en": "Hyundai Glovis", "sector": "Logistics / 완성차 물류·해운"},
    "277810.KQ": {"kr": "레인보우로보틱스", "en": "Rainbow Robotics", "sector": "Robotics / 휴머노이드 (삼성전자 captive)"},
    "454910.KS": {"kr": "두산로보틱스", "en": "Doosan Robotics", "sector": "Robotics / 협동로봇·휴머노이드 (코스피 신규)"},
    "064350.KS": {"kr": "현대로템", "en": "Hyundai Rotem", "sector": "방산·철도·로봇 (현대차그룹 — Boston Dynamics 협업)"},

    # Korea — Pharma / Bio
    "207940.KS": {"kr": "삼성바이오로직스", "en": "Samsung Biologics", "sector": "Bio CDMO"},
    "068270.KS": {"kr": "셀트리온", "en": "Celltrion", "sector": "Bio"},

    # Korea — Medical Aesthetics / Beauty (메르 ECM 분석용)
    "290650.KQ": {"kr": "엘앤씨바이오", "en": "L&C Bio", "sector": "Bio (인체조직·ECM·재생의료)"},
    "214450.KQ": {"kr": "파마리서치", "en": "Pharma Research Products", "sector": "Bio (PN·리쥬란·콜라겐)"},
    "145020.KQ": {"kr": "휴젤", "en": "Hugel", "sector": "Bio (보툴리눔 톡신·필러)"},
    "086900.KQ": {"kr": "메디톡스", "en": "Medytox", "sector": "Bio (보툴리눔 톡신·필러)"},
    "214150.KQ": {"kr": "클래시스", "en": "Classys", "sector": "미용 의료기기 (HIFU·RF)"},
    "200670.KQ": {"kr": "휴메딕스", "en": "Humedix", "sector": "Bio (콜라겐·HA 필러)"},
    "216080.KQ": {"kr": "제테마", "en": "Jetema", "sector": "Bio (보툴리눔 톡신·필러)"},
    "228760.KQ": {"kr": "지노믹트리", "en": "Genomictree", "sector": "Bio (분자진단)"},

    # Korea — Genomics / Longevity (메르 역노화 ER-100 분석용)
    "038290.KQ": {"kr": "마크로젠", "en": "Macrogen", "sector": "Bio (유전체 분석·메틸화·NGS)"},

    # US — Longevity / Anti-aging / AI-Bio (메르 역노화 ER-100 분석용)
    "RXRX": {"kr": "Recursion Pharmaceuticals", "en": "Recursion Pharmaceuticals", "sector": "AI-driven Drug Discovery / Longevity"},
    "BIOA": {"kr": "BioAge Labs", "en": "BioAge Labs Inc.", "sector": "Longevity Biotech"},
    "UBX": {"kr": "Unity Biotechnology", "en": "Unity Biotechnology", "sector": "Senolytics / Aging Biology"},
    "NTLA": {"kr": "Intellia Therapeutics", "en": "Intellia Therapeutics", "sector": "CRISPR Gene Editing / In-vivo Reprogramming"},

    # Korea — Entertainment / K-POP (ricemankr JYP 분석용)
    "035900.KQ": {"kr": "JYP Ent.", "en": "JYP Entertainment", "sector": "Entertainment (K-POP·아티스트 매니지먼트)"},
    "352820.KS": {"kr": "HYBE", "en": "HYBE Co., Ltd.", "sector": "Entertainment (K-POP·BTS·플랫폼)"},
    "041510.KQ": {"kr": "에스엠", "en": "S.M. Entertainment", "sector": "Entertainment (K-POP·에스파·NCT)"},
    "122870.KQ": {"kr": "와이지엔터테인먼트", "en": "YG Entertainment", "sector": "Entertainment (K-POP·블랙핑크·베이비몬스터)"},
    "376300.KQ": {"kr": "디어유", "en": "Dear U", "sector": "엔터 플랫폼 (Bubble 팬덤 메시징)"},

    # Korea — Tech / Internet
    "035420.KS": {"kr": "네이버", "en": "NAVER", "sector": "Internet"},
    "035720.KS": {"kr": "카카오", "en": "Kakao", "sector": "Internet"},

    # Korea — Metals/Smelting/Materials
    "010130.KS": {"kr": "고려아연", "en": "Korea Zinc", "sector": "Zinc/Lead Smelting + 황산 부산물"},
    "000670.KS": {"kr": "영풍", "en": "Young Poong", "sector": "Zinc Smelting"},
    "006260.KS": {"kr": "LS", "en": "LS Corporation", "sector": "복합 사업회사 (LS전선·LS MnM·LS아이앤디·LS ELECTRIC)"},
    "060370.KS": {"kr": "LS마린솔루션", "en": "LS Marine Solution", "sector": "해저케이블 포설·해상 시공 (LS전선 HVDC 패키지)"},
    "060370.KQ": {"kr": "LS마린솔루션", "en": "LS Marine Solution", "sector": "해저케이블 포설·해상 시공 (LS전선 HVDC 패키지)"},
    "000500.KS": {"kr": "가온전선", "en": "Gaon Cable", "sector": "산업용 전선·재도체화 가공선 (미국 SPARK 수혜)"},
    "062040.KS": {"kr": "산일전기", "en": "Sanil Electric", "sector": "변압기 (북미 데이터센터·블룸에너지향 고마진 OPM 39%)"},
    "103140.KS": {"kr": "풍산", "en": "Poongsan", "sector": "Copper/Brass + 방산"},
    "082740.KS": {"kr": "한화엔진", "en": "Hanwha Engine", "sector": "선박·발전 엔진 (4행정 중속·저속)"},

    # Tungsten / Critical Minerals + Carbide Tooling
    "ALM": {"kr": "알몬티 인더스트리스", "en": "Almonty Industries", "sector": "Tungsten Mining (상동광산·비중국 텅스텐)"},
    "AII.TO": {"kr": "알몬티 인더스트리스", "en": "Almonty Industries", "sector": "Tungsten Mining (상동광산·비중국 텅스텐)"},
    "KMT": {"kr": "케나메탈", "en": "Kennametal Inc.", "sector": "초경합금·텅스텐 절삭공구 (Tungsten Carbide Tooling)"},

    # Japan — Materials/Smelting
    "5713.T": {"kr": "스미토모금속광업", "en": "Sumitomo Metal Mining", "sector": "Nickel/Copper Smelting (Japan)"},
    "5711.T": {"kr": "미쓰비시 머티리얼", "en": "Mitsubishi Materials", "sector": "Copper Smelting"},

    # Global — Mining/Materials
    "FCX": {"kr": "프리포트맥모란", "en": "Freeport-McMoRan", "sector": "Copper Mining (US/Indonesia)"},
    "BHP": {"kr": "BHP", "en": "BHP Group", "sector": "Diversified Mining"},
    "VALE": {"kr": "발레", "en": "Vale S.A.", "sector": "Iron Ore/Nickel Mining (Brazil)"},

    # US — Solar / Renewable / ESS
    "FSLR": {"kr": "퍼스트솔라", "en": "First Solar, Inc.", "sector": "Solar PV Modules — CdTe thin-film + Perovskite(Evolar) (US-domiciled)"},
    "DQ": {"kr": "다초뉴에너지", "en": "Daqo New Energy Corp.", "sector": "Polysilicon — solar-grade 실리콘 원소재 pure-play (China)"},
    "WCH.DE": {"kr": "바커케미", "en": "Wacker Chemie AG", "sector": "Polysilicon·Silicones — Western 폴리실리콘 챔피언 (Germany)"},
    "JKS": {"kr": "징코솔라", "en": "JinkoSolar Holding Co., Ltd.", "sector": "Solar PV Modules — TOPCon 실리콘 volume leader (China)"},
    "CSIQ": {"kr": "캐나디안솔라", "en": "Canadian Solar Inc.", "sector": "Solar PV Modules 실리콘 + Energy Storage (Canada/China)"},
    "ENPH": {"kr": "엔페이즈", "en": "Enphase Energy", "sector": "Solar Microinverters + Residential ESS"},
    "RUN": {"kr": "선런", "en": "Sunrun Inc.", "sector": "Residential Solar — US lease/PPA model (largest US residential installer)"},

    # Europe — Power Equipment
    "WRT1V.HE": {"kr": "바르질라", "en": "Wärtsilä Corporation", "sector": "Power Plant Engines (Finland)"},

    # US — Hyperscaler (already partial)
    "MSFT": {"kr": "마이크로소프트", "en": "Microsoft Corporation", "sector": "Software/Cloud (Azure)"},
    "META": {"kr": "메타", "en": "Meta Platforms", "sector": "Internet/AI Infrastructure"},
    "GOOGL": {"kr": "알파벳 (구글)", "en": "Alphabet Inc.", "sector": "Internet/Cloud (GCP)"},

    # Korea — Other notable
    "017670.KS": {"kr": "SK텔레콤", "en": "SK Telecom", "sector": "Telecom"},
    "030200.KS": {"kr": "KT", "en": "KT", "sector": "Telecom"},
    "032830.KS": {"kr": "삼성생명", "en": "Samsung Life Insurance", "sector": "Insurance"},

    # Korea — Power Infrastructure (의교창 2026-05-10 AI 에너지 thesis)
    "267260.KS": {"kr": "HD현대일렉트릭", "en": "HD Hyundai Electric", "sector": "변압기·전력기기 (글로벌 Top3·미국 데이터센터 수혜)"},
    "010120.KS": {"kr": "LS ELECTRIC", "en": "LS ELECTRIC", "sector": "변압기·차단기·ESS (한국 1위 + 미국 진출)"},
    "298040.KS": {"kr": "효성중공업", "en": "Hyosung Heavy Industries", "sector": "변압기·STATCOM·중전기 (미국 멤피스 공장)"},
    "034020.KS": {"kr": "두산에너빌리티", "en": "Doosan Enerbility", "sector": "원전·SMR·가스터빈 (X-energy NuScale 협력)"},
    "229640.KS": {"kr": "LS에코에너지", "en": "LS EcoEnergy", "sector": "해저케이블·송배전 (영국 East Anglia 수주)"},
    "001440.KS": {"kr": "대한전선", "en": "Taihan Cable & Solution", "sector": "송배전 케이블·해저케이블"},
    "112610.KS": {"kr": "씨에스윈드", "en": "CS Wind Corporation", "sector": "풍력 타워·해상풍력"},
    "009830.KS": {"kr": "한화솔루션", "en": "Hanwha Solutions", "sector": "태양광·화학 (미국 Qcells 모듈)"},
    "456040.KS": {"kr": "OCI(사업회사)", "en": "OCI Company Ltd", "sector": "폴리실리콘 제조 OpCo (2023.05 분할 신설)"},
    "010060.KS": {"kr": "OCI홀딩스", "en": "OCI Holdings", "sector": "폴리실리콘·태양광 소재 지주사 (Malaysia plant·NeoSilicon wafer·OCI TRS)"},
    "012450.KS": {"kr": "한화에어로스페이스", "en": "Hanwha Aerospace Co., Ltd.", "sector": "방산·우주발사체 (누리호 체계종합·항공엔진·위성, 한화시스템 모회사)"},

    # Korea — IBKR series 분석용 (의교창 2026-05-04)
    "016360.KS": {"kr": "삼성증권", "en": "Samsung Securities", "sector": "Brokerage/IB (IBKR 한국 체결 관문)"},
    "402340.KS": {"kr": "SK스퀘어", "en": "SK Square", "sector": "Holding (SK하이닉스 NAV 디스카운트)"},
    "322310.KQ": {"kr": "오로스테크놀로지", "en": "Auros Technology", "sector": "반도체 계측 장비 (HBM 공정)"},
    "131970.KQ": {"kr": "두산테스나", "en": "Doosan Tesna", "sector": "반도체 후공정 테스트 (SoC/CIS/MCU, NVIDIA 파트너)"},
    "IBKR": {"kr": "인터랙티브 브로커스", "en": "Interactive Brokers Group", "sector": "Online Brokerage Platform"},

    # US — Lithium
    "ALB": {"kr": "Albemarle", "en": "Albemarle Corporation", "sector": "Lithium Mining"},
    "SQM": {"kr": "SQM", "en": "Sociedad Química y Minera de Chile", "sector": "Lithium/Fertilizer"},
    "LAC": {"kr": "Lithium Americas", "en": "Lithium Americas", "sector": "Lithium Mining"},
    "LIT": {"kr": "Global X 리튬 ETF", "en": "Global X Lithium & Battery Tech ETF", "sector": "Lithium ETF"},

    # US — EV / Battery
    "TSLA": {"kr": "테슬라", "en": "Tesla Inc.", "sector": "EV/Energy"},
    "RIVN": {"kr": "리비안", "en": "Rivian Automotive", "sector": "EV"},
    "F": {"kr": "포드", "en": "Ford Motor", "sector": "Automobile"},
    "GM": {"kr": "GM", "en": "General Motors", "sector": "Automobile"},

    # US — Semiconductor / Memory / Storage
    "MU": {"kr": "마이크론", "en": "Micron Technology", "sector": "Memory Semiconductor (DRAM/NAND)"},
    "SNDK": {"kr": "샌디스크", "en": "Sandisk Corporation", "sector": "NAND Flash Storage"},
    "STX": {"kr": "Seagate", "en": "Seagate Technology", "sector": "HDD Storage"},
    "WDC": {"kr": "Western Digital", "en": "Western Digital Corp.", "sector": "HDD/NAND Storage"},
    "285A.T": {"kr": "키옥시아", "en": "Kioxia Holdings", "sector": "NAND Flash (Japan)"},
    "NVDA": {"kr": "엔비디아", "en": "NVIDIA Corporation", "sector": "GPU/AI Semiconductor"},
    "AMD": {"kr": "AMD", "en": "Advanced Micro Devices", "sector": "Semiconductor"},
    "NVTS": {"kr": "나비타스 세미컨덕터", "en": "Navitas Semiconductor Corporation", "sector": "Power Semiconductor (GaN + SiC pure-play, AI 800VDC)"},
    "VRT": {"kr": "버티브 홀딩스", "en": "Vertiv Holdings Co.", "sector": "AI Data Center Critical Infrastructure (Power·Cooling·800VDC)"},
    "WOLF": {"kr": "울프스피드", "en": "Wolfspeed Inc.", "sector": "Power Semiconductor (SiC pure-play)"},
    "ON": {"kr": "온세미", "en": "ON Semiconductor Corp.", "sector": "Power Semiconductor (SiC + Image Sensors)"},
    "IFNNY": {"kr": "인피니언 테크놀로지스", "en": "Infineon Technologies AG (ADR)", "sector": "Power Semiconductor (SiC+GaN+Si)"},
    "IFX.DE": {"kr": "인피니언 테크놀로지스", "en": "Infineon Technologies AG", "sector": "Power Semiconductor (SiC+GaN+Si, NVIDIA 800VDC SST 파트너)"},
    "ABBNY": {"kr": "ABB", "en": "ABB Ltd (ADR)", "sector": "Power & Automation Equipment (Switchgear·Transformers·SST)"},
    "SBGSY": {"kr": "슈나이더 일렉트릭", "en": "Schneider Electric SE (ADR)", "sector": "Power Equipment (Data Center UPS·Switchgear)"},
    "INTC": {"kr": "인텔", "en": "Intel Corporation", "sector": "Semiconductor"},
    "TSM": {"kr": "TSMC", "en": "Taiwan Semiconductor Manufacturing", "sector": "Foundry"},
    "AVGO": {"kr": "브로드컴", "en": "Broadcom Inc.", "sector": "Semiconductor"},
    "ARM": {"kr": "ARM 홀딩스", "en": "Arm Holdings plc", "sector": "Semiconductor IP (CPU Architecture)"},
    "YPF": {"kr": "YPF (아르헨티나 에너지)", "en": "YPF Sociedad Anónima", "sector": "Oil & Gas (Argentina, Vaca Muerta Shale)"},
    "ARGT": {"kr": "Global X 아르헨티나 ETF", "en": "Global X MSCI Argentina ETF", "sector": "Country ETF (Argentina equities)"},
    "MRVL": {"kr": "마벨", "en": "Marvell Technology", "sector": "Semiconductor (Networking)"},

    # US — Optical Networking / AI Infrastructure
    "GLW": {"kr": "코닝", "en": "Corning Incorporated", "sector": "Optical Communications / Specialty Glass"},
    "COHR": {"kr": "코히런트", "en": "Coherent Corp.", "sector": "Optical/Photonics Components"},
    "LITE": {"kr": "루멘텀", "en": "Lumentum Holdings", "sector": "Optical Components / Lasers"},
    "ANET": {"kr": "아리스타 네트웍스", "en": "Arista Networks", "sector": "Network Switches"},

    # US — Tech mega-cap
    "AAPL": {"kr": "애플", "en": "Apple Inc.", "sector": "Consumer Electronics"},
    "MSFT": {"kr": "마이크로소프트", "en": "Microsoft Corporation", "sector": "Software/Cloud"},
    "GOOG": {"kr": "알파벳 (구글)", "en": "Alphabet Inc.", "sector": "Internet/Cloud"},
    "GOOGL": {"kr": "알파벳 (구글)", "en": "Alphabet Inc.", "sector": "Internet/Cloud"},
    "META": {"kr": "메타", "en": "Meta Platforms", "sector": "Internet/AR/VR"},
    "AMZN": {"kr": "아마존", "en": "Amazon.com", "sector": "E-commerce/Cloud"},

    # US — Healthcare / Bio (frequently mentioned)
    "PRTA": {"kr": "프로테나", "en": "Prothena Corporation", "sector": "Bio (Neurology)"},
    "LLY": {"kr": "일라이 릴리", "en": "Eli Lilly", "sector": "Pharma"},
    "NVO": {"kr": "노보 노디스크", "en": "Novo Nordisk", "sector": "Pharma (GLP-1)"},

    # US — Coal / Mining
    "BTU": {"kr": "Peabody Energy", "en": "Peabody Energy Corporation", "sector": "Coal Mining (Thermal + Metallurgical)"},
    "ARCH": {"kr": "Arch Resources", "en": "Arch Resources Inc.", "sector": "Coal Mining (Metallurgical)"},
    "AMR": {"kr": "Alpha Metallurgical", "en": "Alpha Metallurgical Resources", "sector": "Coal Mining (Metallurgical)"},
    "CEIX": {"kr": "Consol Energy", "en": "CONSOL Energy Inc.", "sector": "Coal Mining (Thermal)"},
    "HCC": {"kr": "Warrior Met Coal", "en": "Warrior Met Coal Inc.", "sector": "Coal Mining (Metallurgical)"},
    "TECK": {"kr": "Teck Resources", "en": "Teck Resources Limited", "sector": "Diversified Mining (Coal·Copper·Zinc)"},

    # US/Australia/China — Rare Earth (dhgusdnd44 2026-05-07)
    "MP": {"kr": "MP 머티리얼스", "en": "MP Materials Corp.", "sector": "Rare Earth Mining/Refining (US Mountain Pass, 1~6단계 vertical, NdPr $110/kg DoD floor)"},
    "USAR": {"kr": "USA 레어어스", "en": "USA Rare Earth Inc.", "sector": "Rare Earth Magnet Manufacturing (US Round Top deposit + Stillwater 자석 시설)"},
    "ENR": {"kr": "에네르고텍", "en": "Energizer Holdings", "sector": "Battery (NOT rare earth — placeholder)"},
    "UUUU": {"kr": "Energy Fuels", "en": "Energy Fuels Inc.", "sector": "Uranium + Rare Earth (US White Mesa Mill — monazite 정제)"},
    "LYC.AX": {"kr": "라이너스 레어어스 (Lynas)", "en": "Lynas Rare Earths Limited", "sector": "Rare Earth Mining/Refining (Australia Mt Weld + Malaysia/Kalgoorlie 정제 — 비중국 분리/금속화 사실상 유일)"},
    "LYSDY": {"kr": "라이너스 ADR", "en": "Lynas Rare Earths ADR", "sector": "Rare Earth (Lynas ADR)"},

    # US — Space Industry Value Chain (doctordk 2026-04-20)
    # Layer 1: Infrastructure (발사체)
    "RKLB": {"kr": "로켓랩", "en": "Rocket Lab USA Inc.", "sector": "Space Launch + Satellites (Electron rocket + Photon bus)"},
    "LUNR": {"kr": "인튜이티브 머신스", "en": "Intuitive Machines Inc.", "sector": "Lunar Lander / NASA Artemis"},
    "RDW": {"kr": "레드와이어", "en": "Redwire Corporation", "sector": "Space Infrastructure / Manufacturing"},
    # Layer 2: Platform (위성 네트워크 / 데이터)
    "ASTS": {"kr": "AST 스페이스모바일", "en": "AST SpaceMobile Inc.", "sector": "Direct-to-Device Satellite Communications (BlueBird LEO constellation)"},
    "BKSY": {"kr": "블랙스카이", "en": "BlackSky Technology", "sector": "Real-time Geospatial Intelligence"},
    "IRDM": {"kr": "이리듐", "en": "Iridium Communications", "sector": "Global LEO Satellite Network"},
    "SPIR": {"kr": "스파이어 글로벌", "en": "Spire Global Inc.", "sector": "Satellite Data (Maritime/Weather/RF)"},
    "PL": {"kr": "플래닛 랩스", "en": "Planet Labs PBC", "sector": "Earth Observation Satellites"},
    # Layer 3: Supply Chain (원자재)
    "AA": {"kr": "알코아", "en": "Alcoa Corporation", "sector": "Aluminum (Aerospace-grade)"},
    "FCX": {"kr": "프리포트맥모란", "en": "Freeport-McMoRan Inc.", "sector": "Copper / Gold Mining"},
    # El Niño theme (2026-06-16 ranto28 super El Niño)
    "ADM": {"kr": "아처대니얼스미들랜드", "en": "Archer-Daniels-Midland Company", "sector": "Agribusiness / Grain Processing / Biofuel"},
    "011200.KS": {"kr": "HMM", "en": "HMM Co., Ltd.", "sector": "Container Shipping"},
    "025860.KS": {"kr": "남해화학", "en": "Namhae Chemical Corporation", "sector": "Fertilizer (Urea·Compound)"},
    "005180.KS": {"kr": "빙그레", "en": "Binggrae Co., Ltd.", "sector": "Food / Ice Cream·Beverage"},
    # Layer 4: Materials (특수 소재)
    "ATI": {"kr": "ATI 인코퍼레이티드", "en": "ATI Inc.", "sector": "Specialty Alloys (Titanium·Nickel for Aerospace)"},
    "HXL": {"kr": "헥셀", "en": "Hexcel Corporation", "sector": "Carbon Fiber Composites (Aerospace)"},
    "PKE": {"kr": "파크 에어로스페이스", "en": "Park Aerospace Corp.", "sector": "Advanced Composite Materials"},
    "CRS": {"kr": "카펜터 테크놀로지", "en": "Carpenter Technology Corp.", "sector": "High-performance Specialty Alloys"},
    "MTRN": {"kr": "마테리온", "en": "Materion Corporation", "sector": "Precision Specialty Materials (Beryllium·Photonics)"},
    # Layer 5: Compute (반도체·통신·AI)
    "QRVO": {"kr": "코르보", "en": "Qorvo Inc.", "sector": "RF Communications Chips"},
    "ADI": {"kr": "아날로그 디바이시스", "en": "Analog Devices Inc.", "sector": "Precision Sensors / Mixed-signal Semiconductor"},
    "STM": {"kr": "ST마이크로일렉트로닉스", "en": "STMicroelectronics N.V.", "sector": "Space-qualified Semiconductors"},
    "ILU.AX": {"kr": "일루카 리소시스", "en": "Iluka Resources Limited", "sector": "Mineral Sands + Rare Earth Refining (Australia Eneabba 정제 시설 2027 가동, 호주 정부 $1.65B 융자)"},
    "ARU.AX": {"kr": "아라푸라 리소시스", "en": "Arafura Rare Earths", "sector": "Rare Earth (Australia Nolans Project, NdPr 중심)"},
    "600111.SS": {"kr": "북방희토 (China Northern)", "en": "China Northern Rare Earth Group", "sector": "Rare Earth Mining/Separation (中 내몽고 Bayan Obo, 글로벌 경희토류 1위)"},
    "600392.SS": {"kr": "성허 자원 (Shenghe)", "en": "Shenghe Resources Holding", "sector": "Rare Earth Trading/Refining (中 사천성, MP Materials 옛 정광 처리 파트너, 그린란드 Tanbreez 지분)"},
    "REMX": {"kr": "VanEck 희토류·전략광물 ETF", "en": "VanEck Rare Earth/Strategic Metals ETF", "sector": "Rare Earth ETF"},

    # 13F 분석 — Q1 2026 (산업분석러)
    "NTRA": {"kr": "나테라", "en": "Natera, Inc.", "sector": "Genetic Testing / Liquid Biopsy (Signatera MRD ctDNA, MCED competition with Illumina)"},
    "NEM": {"kr": "뉴몬트", "en": "Newmont Corporation", "sector": "Gold Mining (largest global producer, AISC $1,400-1,600/oz)"},
    "316140.KS": {"kr": "우리금융지주", "en": "Woori Financial Group Inc.", "sector": "Korean Banking / Financial Holdings"},
    "GOLD": {"kr": "배릭 골드", "en": "Barrick Mining Corporation", "sector": "Gold Mining"},
    "MCO": {"kr": "무디스", "en": "Moody's Corporation", "sector": "Credit Rating / Financial Infrastructure"},
    "SPGI": {"kr": "S&P 글로벌", "en": "S&P Global Inc.", "sector": "Credit Rating / Financial Infrastructure"},
    "MSCI": {"kr": "MSCI", "en": "MSCI Inc.", "sector": "Index Provider / Financial Infrastructure"},
    "YPF": {"kr": "YPF", "en": "YPF Sociedad Anónima", "sector": "Argentina Energy (Vaca Muerta Shale)"},
    "AAGIY": {"kr": "AngloGold Ashanti", "en": "AngloGold Ashanti", "sector": "Gold Mining"},
    "KGC": {"kr": "킨로스 골드", "en": "Kinross Gold Corp.", "sector": "Gold Mining"},
    "AEM": {"kr": "Agnico Eagle Mines", "en": "Agnico Eagle Mines Limited", "sector": "Gold Mining (Canada-focused)"},
    "FNV": {"kr": "프랑코 네바다", "en": "Franco-Nevada Corporation", "sector": "Gold Royalty / Streaming"},
    "LEN": {"kr": "레나", "en": "Lennar Corporation", "sector": "US Homebuilder"},
    "DAL": {"kr": "델타 항공", "en": "Delta Air Lines, Inc.", "sector": "US Airline (Premium / strong balance sheet)"},
    "CRWV": {"kr": "코어위브", "en": "CoreWeave, Inc.", "sector": "AI Cloud Infrastructure (NVIDIA partner, GPU rental)"},
    "AKAM": {"kr": "아카마이", "en": "Akamai Technologies, Inc.", "sector": "Edge Cloud / CDN / AI Inference Infrastructure"},
    "NET": {"kr": "클라우드플레어", "en": "Cloudflare, Inc.", "sector": "Edge Network / CDN / Workers AI Inference"},
    "EQIX": {"kr": "에퀴닉스", "en": "Equinix, Inc.", "sector": "Data Center REIT / Global Interconnection / Edge Colocation"},
    "WCC": {"kr": "웨스코 인터내셔널", "en": "WESCO International, Inc.", "sector": "Electrical Distribution / Power Equipment"},
    "MSFT": {"kr": "마이크로소프트", "en": "Microsoft Corporation", "sector": "Software / Cloud (Azure, OpenAI)"},
    "SCCO": {"kr": "서던 코퍼", "en": "Southern Copper Corporation", "sector": "Copper Mining (Peru / Mexico)"},
    "GSG": {"kr": "iShares S&P GSCI 상품인덱스 ETF", "en": "iShares S&P GSCI Commodity-Indexed Trust", "sector": "Broad Commodities ETF"},

    # 산업분석러 2026-05-18 금리 상승·광산주의 시대 — 5 종목
    "GDX": {"kr": "VanEck 금광주 ETF", "en": "VanEck Gold Miners ETF", "sector": "Gold Miners ETF (top holdings NEM·AEM·GOLD·WPM·FNV, 50개 광산기업 시총 가중)"},
    "COPX": {"kr": "Global X 구리광주 ETF", "en": "Global X Copper Miners ETF", "sector": "Copper Miners ETF (FCX·SCCO·Antofagasta·Glencore·SOLI·BHP 등 40개)"},
    "138040.KS": {"kr": "메리츠금융지주", "en": "Meritz Financial Group Inc.", "sector": "Korean Financial Holding (자사주매입 50%+ 배당 = 총주주환원율 80% 한국 financial 대표)"},
    "BHP": {"kr": "BHP", "en": "BHP Group Limited", "sector": "Iron Ore / Copper / Coal Mining (Australia)"},
    "RIO": {"kr": "리오 틴토", "en": "Rio Tinto Group", "sector": "Iron Ore / Copper / Lithium Mining"},
    "XOM": {"kr": "엑손모빌", "en": "Exxon Mobil Corporation", "sector": "Integrated Oil & Gas"},
    "CVX": {"kr": "셰브론", "en": "Chevron Corporation", "sector": "Integrated Oil & Gas"},

    # US — Energy / Tanker (DaeGurr / 메르 호르무즈+VLCC)
    "FRO": {"kr": "프론트라인", "en": "Frontline Ltd.", "sector": "VLCC Tanker Shipping (#1 pure-play VLCC operator)"},
    "DHT": {"kr": "DHT 홀딩스", "en": "DHT Holdings Inc.", "sector": "Pure-play VLCC Tanker"},
    "INSW": {"kr": "International Seaways", "en": "International Seaways Inc.", "sector": "Crude + Product Tanker (Suezmax/VLCC/LR1·MR)"},
    "TNK": {"kr": "Teekay Tankers", "en": "Teekay Tankers Ltd.", "sector": "Mid-size Crude Tanker (Suezmax·Aframax)"},
    "STNG": {"kr": "Scorpio Tankers", "en": "Scorpio Tankers Inc.", "sector": "Product Tanker (LR2·MR·Handymax — US light crude·refined product 수송)"},

    # Korea — Refining / Oil (메르 호르무즈·미국 경질유 분석용)
    "010950.KS": {"kr": "S-Oil", "en": "S-Oil Corporation", "sector": "Refining (Aramco 63% backed, RHDS·RFCC 고도화 비중 최고)"},

    # US — Refining (산업분석러 3-2-1 크랙 스프레드 분석용)
    "VLO": {"kr": "발레로에너지", "en": "Valero Energy Corporation", "sector": "Refining (미국 최대 독립 정유 — Gulf Coast 3-2-1 크랙 직수혜)"},

    # Korea — Tanker / Shipping (메르 VLCC 분석용)
    "044450.KS": {"kr": "KSS해운", "en": "KSS Line Ltd.", "sector": "LPG·암모니아·케미컬 탱커 (Korean tanker operator)"},
    "028670.KS": {"kr": "팬오션", "en": "Pan Ocean Co. Ltd.", "sector": "Bulk·탱커·LNG 종합 해운"},
    "011200.KS": {"kr": "HMM", "en": "HMM Co. Ltd.", "sector": "컨테이너 중심 종합 해운"},

    # US — Natural Gas / LNG (메르 Henry Hub thesis)
    "LNG": {"kr": "셰니어 에너지", "en": "Cheniere Energy Inc.", "sector": "LNG Export Operator"},
    "VG": {"kr": "Venture Global", "en": "Venture Global Inc.", "sector": "LNG Export Operator"},
    "SRE": {"kr": "셈프라", "en": "Sempra", "sector": "LNG/Utility (Cameron LNG)"},
    "XOM": {"kr": "엑슨모빌", "en": "Exxon Mobil Corporation", "sector": "Integrated Oil & Gas (Golden Pass LNG)"},
    "EQT": {"kr": "EQT 코퍼레이션", "en": "EQT Corporation", "sector": "Natural Gas E&P (Marcellus)"},
    "WMB": {"kr": "윌리엄스 컴퍼니즈", "en": "Williams Companies Inc.", "sector": "Pipeline / Natural Gas Midstream"},
    "KMI": {"kr": "킨더 모건", "en": "Kinder Morgan Inc.", "sector": "Pipeline / Natural Gas Midstream"},
    "UNG": {"kr": "United States Natural Gas Fund", "en": "United States Natural Gas Fund", "sector": "Natural Gas Commodity ETF"},
    "FCG": {"kr": "First Trust Natural Gas ETF", "en": "First Trust Natural Gas ETF", "sector": "Natural Gas Equity ETF"},

    # ETFs (commonly referenced)
    "SPY": {"kr": "S&P 500 ETF", "en": "SPDR S&P 500 ETF", "sector": "Index ETF"},
    "QQQ": {"kr": "나스닥 100 ETF", "en": "Invesco QQQ Trust", "sector": "Index ETF"},
    "VOO": {"kr": "Vanguard S&P 500 ETF", "en": "Vanguard S&P 500 ETF", "sector": "Index ETF"},
    "VT": {"kr": "Vanguard Total World ETF", "en": "Vanguard Total World Stock ETF", "sector": "Global ETF"},
    "VTI": {"kr": "Vanguard Total Market ETF", "en": "Vanguard Total Stock Market ETF", "sector": "Index ETF"},
    "EWJ": {"kr": "iShares MSCI Japan ETF", "en": "iShares MSCI Japan ETF", "sector": "Country ETF"},
    "EWY": {"kr": "iShares MSCI 한국 ETF", "en": "iShares MSCI South Korea ETF", "sector": "Country ETF"},
    "ITA": {"kr": "iShares 항공우주방산 ETF", "en": "iShares U.S. Aerospace & Defense ETF", "sector": "Sector ETF"},

    # ── ESS / Grid / Renewable bottleneck (2026-05-10 추가) ──
    "GEV": {"kr": "GE Vernova", "en": "GE Vernova Inc.", "sector": "Power Grid Equipment (HVDC·변압기·GIS) + 가스/풍력 터빈"},
    "267260.KS": {"kr": "HD현대일렉트릭", "en": "HD Hyundai Electric", "sector": "전력기기 (변압기·차단기·배전반·HVDC)"},
    "010120.KS": {"kr": "LS ELECTRIC", "en": "LS ELECTRIC", "sector": "전력기기 (배전·자동화·태양광 인버터·ESS PCS)"},
    "NEE": {"kr": "넥스트에라 에너지", "en": "NextEra Energy", "sector": "Utility/IPP (재생에너지 + ESS 운영사)"},
    "ENPH": {"kr": "엔페이즈 에너지", "en": "Enphase Energy", "sector": "마이크로인버터·가정용 ESS (IQ Battery)"},
    "FLNC": {"kr": "플루언스 에너지", "en": "Fluence Energy", "sector": "ESS 시스템 통합 (Siemens·AES JV)"},
    "AES": {"kr": "AES Corporation", "en": "The AES Corporation", "sector": "Utility/IPP (재생+ESS)"},
    "PWR": {"kr": "콴타 서비스", "en": "Quanta Services", "sector": "Grid EPC (송전·배전·재생)"},
    "ETN": {"kr": "이튼", "en": "Eaton Corporation plc", "sector": "Power Management (변압기·배전·데이터센터)"},
    "HUBB": {"kr": "허벨", "en": "Hubbell Incorporated", "sector": "Utility T&D (변압기·미터기·배전)"},
    "SHLS": {"kr": "숄스 테크놀로지", "en": "Shoals Technologies Group", "sector": "ESS/PV BoS (전력 인터커넥션 시스템)"},
    "STEM": {"kr": "스템", "en": "Stem Inc.", "sector": "AI 기반 ESS 운영 (Athena 플랫폼)"},
    "VST": {"kr": "비스트라", "en": "Vistra Corp.", "sector": "Utility/IPP (재생+ESS+원자력)"},
    "TAN": {"kr": "Invesco Solar ETF", "en": "Invesco Solar ETF", "sector": "Solar ETF"},
    "GRID": {"kr": "First Trust 그리드 ETF", "en": "First Trust NASDAQ Clean Edge Smart Grid ETF", "sector": "Grid Infrastructure ETF"},

    # ── SOCAMM / AI Memory Substrate (2026-05-22 doctordk LPDDR4 분석용) ──
    "222800.KQ": {"kr": "심텍", "en": "Simmtech Co., Ltd.", "sector": "PCB / Memory Substrate (DDR/LPDDR DIMM·SOCAMM·HBM 기판)"},
    "008060.KS": {"kr": "대덕전자", "en": "Daeduck Electronics Co., Ltd.", "sector": "PCB / Memory Substrate (FC-BGA·SOCAMM·HBM·AI 가속기 기판)"},
    "2408.TW": {"kr": "난야 테크놀로지", "en": "Nanya Technology Corporation", "sector": "Taiwan DRAM (DDR4 trapped maker, Niche PC/Consumer DRAM)"},
}


# ── 2. Persistent cache file ─────────────────────────────────────────────
_CACHE_PATH = Path.home() / ".cache" / "ticker_resolver.json"
_MEMORY_CACHE: dict[str, dict[str, str]] = {}


def _load_persistent_cache() -> dict[str, dict[str, str]]:
    """Load persistent cache from disk."""
    global _MEMORY_CACHE
    if _MEMORY_CACHE:
        return _MEMORY_CACHE
    if _CACHE_PATH.exists():
        try:
            _MEMORY_CACHE = json.loads(_CACHE_PATH.read_text())
        except Exception:
            _MEMORY_CACHE = {}
    return _MEMORY_CACHE


def _save_persistent_cache() -> None:
    """Save cache to disk."""
    try:
        _CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
        _CACHE_PATH.write_text(json.dumps(_MEMORY_CACHE, ensure_ascii=False, indent=2))
    except Exception:
        pass


def resolve_ticker(ticker: str) -> dict[str, str]:
    """Return {'kr': ..., 'en': ..., 'sector': ...} for ticker.

    Resolution: curated → cache → yfinance → fallback.
    """
    ticker = ticker.strip().upper()

    if ticker in CURATED:
        return CURATED[ticker]

    cache = _load_persistent_cache()
    if ticker in cache:
        return cache[ticker]

    # yfinance lookup
    try:
        import yfinance as yf  # type: ignore
        t = yf.Ticker(ticker)
        info = t.info or {}
        en = info.get("longName") or info.get("shortName") or ticker
        sector = info.get("sector") or info.get("industry") or "Unknown"
        result = {"kr": en, "en": en, "sector": sector}
        cache[ticker] = result
        _save_persistent_cache()
        return result
    except Exception:
        return {"kr": ticker, "en": ticker, "sector": "Unknown"}


def format_ticker_with_name(ticker: str, lang: str = "kr", show_sector: bool = False) -> str:
    """Return human-readable ticker label.

    Examples:
      format_ticker_with_name("005490.KS")       → "005490.KS POSCO홀딩스"
      format_ticker_with_name("ALB", lang="en")  → "ALB Albemarle Corporation"
      format_ticker_with_name("005490.KS", show_sector=True)
        → "005490.KS POSCO홀딩스 (Steel/Battery Materials)"
    """
    info = resolve_ticker(ticker)
    name = info.get(lang) or info.get("kr") or ticker
    base = f"{ticker} {name}" if name and name != ticker else ticker
    if show_sector and info.get("sector") and info["sector"] != "Unknown":
        base = f"{base} ({info['sector']})"
    return base


def format_ticker_html(ticker: str) -> str:
    """HTML-formatted ticker with name (for report rendering).

    Returns: <code>005490.KS</code> <strong>POSCO홀딩스</strong>
    """
    info = resolve_ticker(ticker)
    kr = info.get("kr", ticker)
    if kr == ticker:
        return f"<code>{ticker}</code>"
    return f'<code>{ticker}</code> <strong>{kr}</strong>'


if __name__ == "__main__":
    # Self-test
    test_tickers = ["005490.KS", "ALB", "SQM", "006400.KS", "PRTA", "FRO"]
    for t in test_tickers:
        print(f"  {format_ticker_with_name(t):60s} | {format_ticker_with_name(t, show_sector=True)}")
