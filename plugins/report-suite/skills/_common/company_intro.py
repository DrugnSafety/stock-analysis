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


def render_company_intro(ticker: str) -> str:
    """Return HTML for company intro section. Returns '' if no data."""
    intro = COMPANY_INTROS.get(ticker)
    if not intro:
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

    return f"""
    <h2>📋 회사 소개 (Company Profile)</h2>

    <h3>사업 개요</h3>
    <div class="info">{intro.get('overview', '-')}</div>

    <h3>매출 구조 (Segment 비중)</h3>
    <table class="dt">
      <thead><tr><th style="width:30%">Segment</th><th style="width:12%">비중</th><th>설명</th></tr></thead>
      <tbody>{seg_rows}</tbody>
    </table>

    <h3>글로벌 위치</h3>
    <p style="font-size:10pt;line-height:1.6;">{intro.get('global_position', '-')}</p>

    <h3>주요 고객 / 경쟁사</h3>
    <table class="dt">
      <tr><th style="width:14%">주요 고객</th><td>{customers}</td></tr>
      <tr><th>주요 경쟁사</th><td>{competitors}</td></tr>
    </table>
    """
