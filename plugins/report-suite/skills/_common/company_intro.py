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
}


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


def render_company_intro(ticker: str) -> str:
    """Return HTML for company intro section with yfinance enrichment."""
    intro = COMPANY_INTROS.get(ticker, {})
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

    # Korean translation block (curated)
    ko_summary = BUSINESS_SUMMARY_KO.get(ticker, "")
    ko_block = ""
    if ko_summary:
        ko_block = f"""
        <h3>사업 내용 상세 (한글)</h3>
        <div class="info" style="font-size:10pt;line-height:1.7;">{ko_summary}</div>
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

    return f"""
    <h2>📋 회사 소개 (Company Profile)</h2>

    <h3>사업 개요 (요약)</h3>
    <div class="info">{intro.get('overview', '-')}</div>

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
