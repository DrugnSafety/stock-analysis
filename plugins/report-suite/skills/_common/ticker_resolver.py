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
    "BRK-B": {"kr": "버크셔 해서웨이", "en": "Berkshire Hathaway Inc. Class B", "sector": "Diversified Holdings (Insurance/Energy/Rail)"},
    # Korea — Battery / Materials
    "005490.KS": {"kr": "POSCO홀딩스", "en": "POSCO Holdings", "sector": "Steel/Battery Materials"},
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

    # Korea — Shipbuilding / Heavy Industry
    "329180.KS": {"kr": "HD현대중공업", "en": "HD Hyundai Heavy Industries", "sector": "Shipbuilding"},
    "010140.KS": {"kr": "삼성중공업", "en": "Samsung Heavy Industries", "sector": "Shipbuilding"},
    "042660.KS": {"kr": "한화오션", "en": "Hanwha Ocean", "sector": "Shipbuilding"},
    "267250.KS": {"kr": "HD현대", "en": "HD Hyundai", "sector": "Holding"},
    "439260.KS": {"kr": "대한조선", "en": "Daehan Shipbuilding", "sector": "Shipbuilding"},
    "010620.KS": {"kr": "HD현대미포", "en": "HD Hyundai Mipo", "sector": "Shipbuilding (delisted Dec 2025 due to merger)"},

    # Korea — Auto
    "005380.KS": {"kr": "현대차", "en": "Hyundai Motor", "sector": "Automobile"},
    "000270.KS": {"kr": "기아", "en": "Kia", "sector": "Automobile"},
    "012330.KS": {"kr": "현대모비스", "en": "Hyundai Mobis", "sector": "Auto Parts"},

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
    "006260.KS": {"kr": "LS", "en": "LS Corporation", "sector": "Cable/Copper Smelting (LS MnM)"},
    "103140.KS": {"kr": "풍산", "en": "Poongsan", "sector": "Copper/Brass + 방산"},
    "082740.KS": {"kr": "한화엔진", "en": "Hanwha Engine", "sector": "선박·발전 엔진 (4행정 중속·저속)"},

    # Japan — Materials/Smelting
    "5713.T": {"kr": "스미토모금속광업", "en": "Sumitomo Metal Mining", "sector": "Nickel/Copper Smelting (Japan)"},
    "5711.T": {"kr": "미쓰비시 머티리얼", "en": "Mitsubishi Materials", "sector": "Copper Smelting"},

    # Global — Mining/Materials
    "FCX": {"kr": "프리포트맥모란", "en": "Freeport-McMoRan", "sector": "Copper Mining (US/Indonesia)"},
    "BHP": {"kr": "BHP", "en": "BHP Group", "sector": "Diversified Mining"},
    "VALE": {"kr": "발레", "en": "Vale S.A.", "sector": "Iron Ore/Nickel Mining (Brazil)"},

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
    "456040.KS": {"kr": "OCI홀딩스", "en": "OCI Holdings", "sector": "폴리실리콘·태양광 소재"},

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
    "INTC": {"kr": "인텔", "en": "Intel Corporation", "sector": "Semiconductor"},
    "TSM": {"kr": "TSMC", "en": "Taiwan Semiconductor Manufacturing", "sector": "Foundry"},
    "AVGO": {"kr": "브로드컴", "en": "Broadcom Inc.", "sector": "Semiconductor"},
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

    # US — Energy / Tanker (DaeGurr)
    "FRO": {"kr": "프론트라인", "en": "Frontline Ltd.", "sector": "Tanker Shipping"},
    "DHT": {"kr": "DHT 홀딩스", "en": "DHT Holdings", "sector": "Tanker Shipping"},
    "INSW": {"kr": "International Seaways", "en": "International Seaways", "sector": "Tanker Shipping"},
    "TNK": {"kr": "Teekay Tankers", "en": "Teekay Tankers", "sector": "Tanker Shipping"},
    "STNG": {"kr": "Scorpio Tankers", "en": "Scorpio Tankers", "sector": "Tanker Shipping"},

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
