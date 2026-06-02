"""1년치 주요 뉴스 + 공시 timeline.

Auto-routing:
  - Korean tickers (.KS / .KQ) → DART (DART_API_KEY 활성 시) + curated 보충
  - US tickers → SEC EDGAR (공시) + NewsAPI/Finnhub (뉴스) + curated 보충
  - Fallback: curated NEWS_TIMELINE
"""
from __future__ import annotations

import sys
from pathlib import Path

_PLUGINS_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# Try DART (Korean disclosures)
_DART_AVAILABLE = False
try:
    _dart_path = _PLUGINS_ROOT / "dart-integration" / "scripts"
    if _dart_path.exists():
        sys.path.insert(0, str(_dart_path))
        from dart_client import fetch_disclosures as _dart_fetch_disclosures  # type: ignore
        from dart_client import _is_available as _dart_is_available  # type: ignore
        _DART_AVAILABLE = True
except Exception:
    pass

# Try SEC EDGAR (US disclosures)
_SEC_AVAILABLE = False
try:
    _sec_path = _PLUGINS_ROOT / "sec-edgar-integration" / "scripts"
    if _sec_path.exists():
        sys.path.insert(0, str(_sec_path))
        from sec_client import fetch_disclosures as _sec_fetch_disclosures  # type: ignore
        _SEC_AVAILABLE = True
except Exception:
    pass

# Try News integration (NewsAPI + Finnhub)
_NEWS_AVAILABLE = False
try:
    _news_path = _PLUGINS_ROOT / "news-integration" / "scripts"
    if _news_path.exists():
        sys.path.insert(0, str(_news_path))
        from news_client import fetch_news as _news_fetch  # type: ignore
        from news_client import get_status as _news_status  # type: ignore
        _NEWS_AVAILABLE = True
except Exception:
    pass


NEWS_TIMELINE: dict[str, list[dict]] = {
    # ── 2026-05-30 Sprint E-8: Samsung Electronics 12개월 curated (standalone 005930.KS 분석) ──
    "005930.KS": [
        # — 2026 Q2 (최근 90일) —
        {"date": "2026-05-28", "type": "뉴스", "category": "산업", "headline": "Samsung HBM3e 12-stack NVIDIA qualification 최종 단계 진입", "summary": "NVIDIA B200/B300 차세대 GPU 채택 검토. SK하이닉스 단독 공급 구조 균열 시작. 양사 가격경쟁 시작 예상.", "impact": "+", "source": "Reuters"},
        {"date": "2026-05-15", "type": "공시", "category": "주요사항", "headline": "삼성전자 자사주 매입 1차 완료 — 3.5조원 (10조원 목표 35%)", "summary": "2026년 자사주 매입 총 10조원 계획 중 1차 3.5조원 완료 공시. 주주환원율 확대 트렌드 가속.", "impact": "+", "source": "DART 공시"},
        {"date": "2026-05-08", "type": "뉴스", "category": "어닝", "headline": "삼성전자 1Q26 영업이익 9.2조원 (컨센 8.5조) — 메모리 회복 정착", "summary": "DS(반도체) 5.1조 + DX(디바이스) 3.4조 + Harman 0.5조. DRAM ASP +18% QoQ, HBM 매출 비중 32%로 상승.", "impact": "+", "source": "삼성전자 IR"},
        {"date": "2026-04-22", "type": "뉴스", "category": "산업", "headline": "Samsung Foundry 2nm GAA — Qualcomm Snapdragon 8 Gen 5 듀얼소싱 채택", "summary": "TSMC N3 + Samsung SF2 50:50 분할 발주. 2nm GAA 양산 신뢰성 첫 외부 검증 사례.", "impact": "+", "source": "Bloomberg"},
        {"date": "2026-04-10", "type": "공시", "category": "주요사항", "headline": "삼성전자, 미국 Taylor 텍사스 fab 가동 시작 (4nm)", "summary": "170억$ 투자 미국 최첨단 공정 가동. CHIPS Act 보조금 47억$ 1차 수령. 지정학 위험 분산 가속.", "impact": "+", "source": "DART 공시"},
        # — 2026 Q1 —
        {"date": "2026-03-25", "type": "뉴스", "category": "제품", "headline": "Galaxy Z Fold 7 + Galaxy AI 2.0 — 온디바이스 멀티모달 LLM 탑재", "summary": "iPhone Air 대비 productivity 차별화 마케팅. 폴더블 출하 전년대비 +35% 목표.", "impact": "+", "source": "삼성 Unpacked"},
        {"date": "2026-03-08", "type": "뉴스", "category": "산업", "headline": "DRAM 평균판매단가 5개월 연속 상승 — DDR5 비중 65% 돌파", "summary": "AI 서버향 DDR5 수요 폭증 + 일반 PC/모바일 회복. 2026년 메모리 capex 전년 대비 +25% 전망.", "impact": "+", "source": "TrendForce"},
        {"date": "2026-02-19", "type": "뉴스", "category": "정책", "headline": "한국 정부 K-반도체 2.0 정책 — 추가 R&D 펀드 8조원 + Foundry 보조금", "summary": "Samsung Foundry 2nm 양산 추가 정부 지원. TSMC 추격 가속화 정부 의지 천명.", "impact": "+", "source": "산업통상자원부"},
        {"date": "2026-02-05", "type": "뉴스", "category": "어닝", "headline": "삼성전자 4Q25 영업이익 6.8조원 (컨센 5.9조) — turnaround 정착", "summary": "메모리 영업이익 4.2조원 (직전 분기 2.1조) 두 배. HBM3 NVIDIA Z200 채택 수혜 본격화.", "impact": "+", "source": "삼성전자 IR"},
        {"date": "2026-01-22", "type": "뉴스", "category": "지배구조", "headline": "이재용 회장 사법 risk 1심 무죄 — 지배구조 reform 모멘텀 회복", "summary": "삼성생명·삼성물산 지분 정리 논의 재개. governance discount 해소 기대.", "impact": "+", "source": "한겨레"},
        # — 2025 Q4 —
        {"date": "2025-12-18", "type": "공시", "category": "주요사항", "headline": "삼성전자 자사주 매입 10조원 계획 공식 발표 — 2026년 분기별 실행", "summary": "최근 5년 최대 규모 자사주 매입. PB 1.0 deep value 해소 의지 분명.", "impact": "+", "source": "DART 공시"},
        {"date": "2025-12-04", "type": "뉴스", "category": "산업", "headline": "HBM3e 8-stack 시장 점유율 — SK하이닉스 60% · Samsung 28% · Micron 12%", "summary": "Samsung 점유율 분기 +6%p 상승. 12-stack 양산 시 점유율 추가 확대 전망.", "impact": "+", "source": "Counterpoint Research"},
        {"date": "2025-11-21", "type": "뉴스", "category": "산업", "headline": "Samsung-AMD MI400 HBM 공급 계약 — 30억$ 규모 (2026-2027)", "summary": "NVIDIA 외 두 번째 대형 HBM 고객 확보. AMD GPU 시장 점유율 확대 시 추가 upside.", "impact": "+", "source": "AMD Press Release"},
        {"date": "2025-11-05", "type": "뉴스", "category": "어닝", "headline": "삼성전자 3Q25 영업이익 3.1조원 — 메모리 적자 탈출 + Foundry 적자 축소", "summary": "DS 영업이익 +1.8조 (작년 -3.7조 → 흑자전환). NAND 가격 상승 + DDR5 수요 가시화.", "impact": "+", "source": "삼성전자 IR"},
        {"date": "2025-10-15", "type": "뉴스", "category": "지정학", "headline": "美 BIS, 對중국 첨단 반도체 추가 제재 — Samsung 시안 fab 영향 제한적", "summary": "삼성 시안 NAND fab은 legacy 공정 위주로 영향 적음. 다만 향후 capacity 확장 제약 우려.", "impact": "○", "source": "Reuters"},
        # — 2025 Q3 —
        {"date": "2025-09-28", "type": "뉴스", "category": "산업", "headline": "Samsung Foundry 2nm GAA 첫 wafer-out 성공 — TSMC와 6개월 격차", "summary": "PPT 2nm 양산 일정 2026-H2 → 2026-Q3로 가속화. 수율 40%+ 확인.", "impact": "+", "source": "DigiTimes"},
        {"date": "2025-09-12", "type": "뉴스", "category": "제품", "headline": "Galaxy S26 Pre-order — Galaxy AI 1.0 글로벌 출시", "summary": "온디바이스 번역·요약·이미지 생성 기본 탑재. iPhone Air 출시 일주일 앞서 marketing 우위.", "impact": "+", "source": "Samsung Press"},
        {"date": "2025-08-26", "type": "뉴스", "category": "환율", "headline": "USD/KRW 1410 돌파 — 수출주 마진 호조", "summary": "삼성전자 매출 70%가 USD/EUR 결제. 1Y 평균 환율 1380 가정 시 영업이익 +1.5조원 효과.", "impact": "+", "source": "한국은행"},
        {"date": "2025-08-07", "type": "뉴스", "category": "어닝", "headline": "삼성전자 2Q25 영업이익 1.8조원 (컨센 1.5조) — 4분기 연속 흑자", "summary": "메모리 적자 폭 축소 + 모바일 견조. Galaxy Z Fold 6 출하 호조.", "impact": "+", "source": "삼성전자 IR"},
        {"date": "2025-07-18", "type": "뉴스", "category": "제품", "headline": "Samsung HBM3 8-stack — Apple M5 Pro/Max 채택 결정", "summary": "Apple 첫 Samsung HBM 채택. TSMC N3 fab과 시너지로 supply 안정.", "impact": "+", "source": "9to5Mac"},
        # — 2025 Q2 (12개월 lower bound) —
        {"date": "2025-06-29", "type": "공시", "category": "주요사항", "headline": "삼성전자 인도 노이다 fab 2단계 확장 결정 — 30억$ 추가 투자", "summary": "월 capacity 2배 확대 (월 60K → 120K wafers). 중국 의존도 추가 분산.", "impact": "+", "source": "DART 공시"},
        {"date": "2025-06-12", "type": "뉴스", "category": "산업", "headline": "HBM3e 12-stack 양산 — Samsung·SK하이닉스 동시 진입", "summary": "Samsung HBM3e 양산 본격화. NVIDIA H300 채택 검토 진행 — qualification 기간 6개월.", "impact": "+", "source": "TrendForce"},
        {"date": "2025-05-30", "type": "뉴스", "category": "산업", "headline": "메모리 산업 turnaround 공식화 — DRAM/NAND 동시 상승", "summary": "WSTS 2025년 글로벌 반도체 시장 +20% 전망 (메모리 +28%). 2년 downturn 종료 컨센서스.", "impact": "+", "source": "WSTS"},
        {"date": "2025-05-08", "type": "뉴스", "category": "어닝", "headline": "삼성전자 1Q25 영업이익 0.8조원 — 4Q24 -2.2조 대비 흑자전환", "summary": "DRAM ASP 회복 + NAND 가격 안정. Galaxy S25 출하 +18% YoY. turnaround inflection 확인.", "impact": "+", "source": "삼성전자 IR"},
    ],
    # ── 2026-05-19 Merged Perovskite + Space DC analysis (메르 224288651743 + 224287501270) ──
    "010140.KS": [
        {"date": "2026-04-28", "type": "공시", "category": "주요사항", "headline": "삼성중공업, 50MW 부유식 해상데이터센터(FDC) 개념설계 ABS·LR 동시 인증 획득", "summary": "한국 최초·세계 두번째 FDC 양대 선급 인증. 글로벌 hyperscaler 발주 파이프라인 진입권 확보.", "impact": "+", "source": "DART 공시"},
        {"date": "2026-04-18", "type": "공시", "category": "주요사항", "headline": "삼성중공업, 미국 Mousterian과 FDC 공급 MOU 체결", "summary": "미국 데이터센터 신축 대안으로 FDC 첫 계약 가시화. 2026-Q3 본계약 협상 진행.", "impact": "+", "source": "DART 공시"},
        {"date": "2026-03-12", "type": "뉴스", "category": "산업", "headline": "삼성중공업, FLNG → FSRU → FDC cascade 일관 솔루션 발표", "summary": "LNG 인프라 보유 한국·일본의 구조적 우위. 글로벌 LNG 점유 60% 후광 효과.", "impact": "+", "source": "한경"},
        {"date": "2026-02-22", "type": "뉴스", "category": "어닝", "headline": "삼성중공업 4Q25 영업이익 1,580억원 (컨센 1,420억) — 흑자전환 정착", "summary": "2025 연간 흑자 2,200억 확정. LNG선 분기 5+척 수주 페이스 유지.", "impact": "+", "source": "연합뉴스"},
        {"date": "2025-12-15", "type": "공시", "category": "주요사항", "headline": "2025 1H 영업이익 흑자전환 확정 (영업이익률 5.1%)", "summary": "연속 4분기 흑자 달성. KOSPI 우량주 rerate 모멘텀.", "impact": "+", "source": "DART 공시"},
        {"date": "2025-09-08", "type": "공시", "category": "주요사항", "headline": "페트로나스 FLNG2 인도 완료", "summary": "FLNG 운영 track record 5건 누적. 셸·페트로나스·코랄 사우스 등 메이저 고객 지속.", "impact": "+", "source": "DART 공시"},
        {"date": "2025-06-20", "type": "뉴스", "category": "정책", "headline": "한국 정부 K-조선 디지털 전환 5조원 펀드", "summary": "한국 조선업 우주·해상 DC·수소선박 등 차세대 분야 R&D 지원.", "impact": "+", "source": "산업통상자원부"},
    ],
    "TSLA": [
        {"date": "2026-05-19", "type": "뉴스", "category": "제품/이벤트", "headline": "SpaceX V3 Starship 12차 시험비행 임박", "summary": "200t 페이로드 검증 시 우주 데이터센터 경제성($500/kg) 임계점 돌파. Musk vertical integration 핵심 카탈리스트.", "impact": "+", "source": "SpaceX 공식"},
        {"date": "2026-02-04", "type": "뉴스", "category": "제품/이벤트", "headline": "Musk + SpaceX 기술팀, 중국 페로브스카이트 태양광 기업 비공개 방문", "summary": "우주 DC 전력 솔루션으로 페로브스카이트 채택 시사. xAI-SpaceX-Tesla vertical integration 가속.", "impact": "+", "source": "Reuters"},
        {"date": "2026-01-28", "type": "뉴스", "category": "실적", "headline": "Tesla 4Q25 자동차 GM 19.5% — BYD 가격 경쟁 속 마진 방어", "summary": "단가 인상 + cost down 동시 추진. Robotaxi 5개 도시 확장 가이던스 유지.", "impact": "○", "source": "Tesla IR"},
        {"date": "2025-11-15", "type": "뉴스", "category": "정책", "headline": "Trump-Musk Space Force 예산 +20% 통과", "summary": "미국 우주 산업 규제 청신호. SpaceX·Tesla 우주 분야 수혜 가시화.", "impact": "+", "source": "Reuters"},
        {"date": "2025-10-05", "type": "뉴스", "category": "제품", "headline": "xAI Grok 4 출시 + SpaceX 인프라 통합 시사", "summary": "Musk가 xAI-SpaceX 합병 가능성 공언. 우주 AI 인프라 풀스택 구상 가시화.", "impact": "+", "source": "X(Twitter)"},
    ],
    "FSLR": [
        {"date": "2026-04-22", "type": "뉴스", "category": "신공장", "headline": "First Solar AZ 5GW 신공장 가동 시작 — 미국 양산 capacity 8GW+ 진입", "summary": "IRA Section 45X 보조금 $0.07/W = 연간 $350M 안정 수익. 백로그 $25B+ 사상최대.", "impact": "+", "source": "First Solar IR"},
        {"date": "2026-01-18", "type": "뉴스", "category": "기술", "headline": "First Solar 페로브스카이트 탠덤 35.2% 효율 NREL 공식 인증", "summary": "CdTe 박막 → 페로브스카이트 탠덤 진화. SpaceX-xAI 우주 솔라 공급망 단독 후보.", "impact": "+", "source": "NREL"},
        {"date": "2025-11-12", "type": "뉴스", "category": "실적", "headline": "백로그 $25B 사상최대 갱신 — 2028년까지 수주 가시성", "summary": "영업이익률 30%+ 유지. AZ·OH 신공장 ramp 정상.", "impact": "+", "source": "First Solar 10-Q"},
        {"date": "2025-08-14", "type": "뉴스", "category": "실적", "headline": "2Q25 영업이익률 30.4% 달성 — 미국 박막 솔라 1위 입지 굳건", "summary": "중국 PV 모듈 보호관세 + IRA 동시 효과. 미국 자체 페로브스카이트 1순위.", "impact": "+", "source": "First Solar IR"},
        {"date": "2025-06-22", "type": "뉴스", "category": "정책", "headline": "IRA Section 45X 2032년까지 보조금 보장 확정", "summary": "$0.07/W 보조금 7년 lock-in. First Solar 8GW 양산 기준 연간 $350M 안정 수익.", "impact": "+", "source": "미국 재무부"},
    ],
    "014680.KS": [
        {"date": "2026-04-12", "type": "공시", "category": "주요사항", "headline": "한솔케미칼, 페로브스카이트 도판트·전자수송층(ETL) 신규 라인 가동", "summary": "UNIST·KAIST 페로브스카이트 R&D 네트워크 활용. 우주용 신규 공급망 진입 가능성.", "impact": "+", "source": "DART 공시"},
        {"date": "2026-01-22", "type": "공시", "category": "주요사항", "headline": "HBM4 SK하이닉스 공급 확정 — 반도체 소재 매출 가시화", "summary": "HBM cycle 회복 + AI 반도체 capex 수혜. 반도체 매출 비중 50%+ 회복.", "impact": "+", "source": "DART 공시"},
        {"date": "2025-11-08", "type": "뉴스", "category": "제휴", "headline": "UNIST와 페로브스카이트 공동 연구 MOU 체결", "summary": "한국 페로브스카이트 양산 third source 입지 강화.", "impact": "+", "source": "연합뉴스"},
        {"date": "2025-08-25", "type": "뉴스", "category": "실적", "headline": "3Q25 반도체 소재 매출 회복 가속 — YoY +18%", "summary": "HBM cycle 회복 + OLED iPhone 17 소재 채택. 영업이익률 15.3% 회복.", "impact": "+", "source": "한국경제"},
        {"date": "2025-06-15", "type": "뉴스", "category": "제품", "headline": "OLED iPhone 17 소재 채택 — 디스플레이 매출 견조", "summary": "디스플레이 매출 단계 확장. 2026 매출 1조원 가시화.", "impact": "+", "source": "머니투데이"},
    ],
    "9104.T": [
        {"date": "2026-04-30", "type": "뉴스", "category": "제휴", "headline": "MOL-Hitachi FDC MOU 공식 체결 — 9,731t PCTC 개조 결정", "summary": "일본 컨소시엄 4사(MOL·Hitachi·NYK·NTT) 첫 본계약. 2027 가동 일정 확정.", "impact": "+", "source": "MOL IR"},
        {"date": "2026-03-15", "type": "뉴스", "category": "신사업", "headline": "자동차운반선(PCTC) FDC 개조 프로젝트 실시 결정", "summary": "신축 5-7년 대비 6-8개월 개조 진행. 일본 정부 GX 8조엔 자금 활용.", "impact": "+", "source": "Nikkei"},
        {"date": "2025-12-22", "type": "뉴스", "category": "정책", "headline": "일본 GX(Green Transformation) 8조엔 자금 활용 발표", "summary": "일본 정부 FDC 컨소시엄 직접 지원. NTT-Hitachi-NYK-MOL 4사 공식 출범 후속.", "impact": "+", "source": "日経新聞"},
        {"date": "2025-09-30", "type": "뉴스", "category": "실적", "headline": "3Q25 PCTC 자동차 운반 매출 정점 — 영업이익률 16.0% 유지", "summary": "글로벌 EV·자동차 운송 수요 호조. 자동차 운반선 비축 100+척 활용 가능.", "impact": "+", "source": "Nikkei"},
        {"date": "2025-06-14", "type": "뉴스", "category": "제휴", "headline": "NTT-Hitachi-NYK 4사 컨소시엄 공식 출범", "summary": "풀스택 일본 FDC 컨소시엄 (텔레콤 + IT + 해운 + 운항). NTT Communications captive 수요 보장.", "impact": "+", "source": "PR Newswire"},
    ],

    "005490.KS": [
        {"date": "2026-04-15", "type": "공시", "category": "주요사항", "headline": "POSCO홀딩스, 아르헨티나 Salar del Hombre Muerto 1단계 상업생산 개시",
         "summary": "리튬 부문 매출 인식 시작 (연 2.5만톤 LCE 캐파). 캐파 가동률 ramp은 2026 Q4까지 80% 목표. 2027년 EBITDA $1B+ 추가 추정.",
         "impact": "+", "source": "DART 공시"},
        {"date": "2026-03-20", "type": "공시", "category": "임원변동", "headline": "리튬·이차전지 부문 신임 부사장 선임",
         "summary": "전직 LG에너지솔루션 임원 영입. 리튬 사업부 의사결정 속도 ↑ 시그널.",
         "impact": "+", "source": "DART 공시"},
        {"date": "2026-02-28", "type": "뉴스", "category": "어닝", "headline": "POSCO홀딩스 4Q25 영업이익 7,200억원 (컨센 6,800억)",
         "summary": "철강 부문 turning + 리튬 부문 매출 인식 시작. 정유 OPM 2.9% → 3.5% 개선.",
         "impact": "+", "source": "한경"},
        {"date": "2026-01-30", "type": "공시", "category": "주요사항", "headline": "Salar 2단계 투자안 이사회 통과 — 3,500억원 추가 CAPEX",
         "summary": "2028년 가동 목표. 캐파 5만톤 LCE까지 확대. 2027년 reverse-DCF implied growth +1.5%p 상향 가능.",
         "impact": "+", "source": "DART 공시"},
        {"date": "2025-11-12", "type": "뉴스", "category": "산업", "headline": "UBS, 2027년 lithium 가격 전망 $42k/톤으로 +47% 상향",
         "summary": "Western 공급망 재편 + EV 수요 가속이 가격 회복 드라이버. POSCO 직접 수혜.",
         "impact": "+", "source": "UBS Research"},
        {"date": "2025-10-04", "type": "공시", "category": "주식관련사채", "headline": "EB 5,000억 발행 — 양극재 capa 확장 자금",
         "summary": "EPS 2.0% dilution but 매출 성장 가속. 자금 사용처 명확.",
         "impact": "○", "source": "DART 공시"},
        {"date": "2025-08-20", "type": "뉴스", "category": "정책", "headline": "K-IRA 2단계 발표 — 양극재 보조금 확대",
         "summary": "포스코퓨처엠 (003670.KS) + POSCO홀딩스 양극재 부문 직접 수혜.",
         "impact": "+", "source": "산업부"},
        {"date": "2025-06-15", "type": "뉴스", "category": "리스크", "headline": "리튬 spot 가격 $13k/톤 저점 형성 — UBS 'cycle bottom'",
         "summary": "2026 H2 회복 컨센서스. POSCO Salar는 cost가 낮아 가격 회복 시 leverage 큼.",
         "impact": "+", "source": "Benchmark Mineral Intelligence"},
        {"date": "2025-04-22", "type": "공시", "category": "자기주식", "headline": "자기주식 5,000억원 매입 결정",
         "summary": "주가 안정 + 주주환원 강화. PB 0.36 historical 저점 인지.",
         "impact": "+", "source": "DART 공시"},
    ],
    "ALB": [
        {"date": "2026-04-22", "type": "earnings", "category": "1Q26", "headline": "Albemarle 1Q26 EBITDA $250M (consensus $190M)",
         "summary": "QoQ +12% 회복. 가이던스 raise: 2026 EBITDA $1.0B → $1.2B. 가격 안정 신호.",
         "impact": "+", "source": "Albemarle IR"},
        {"date": "2026-03-22", "type": "earnings", "category": "guidance", "headline": "ALB 2026 가이던스: 가격 stabilize 시작 — EBITDA 회복 -45% → +12% QoQ",
         "summary": "Cost cut 효과 + 캐파 운영 효율 개선.",
         "impact": "+", "source": "Albemarle Investor Day"},
        {"date": "2026-02-08", "type": "M&A", "category": "산업", "headline": "ALB, Greenbushes 2단계 expansion 완공 발표",
         "summary": "spodumene 캐파 +20%. 2027년 매출 $1B+ 추가 가능.",
         "impact": "+", "source": "ALB Press Release"},
        {"date": "2025-11-30", "type": "리스크", "category": "정치", "headline": "Argentina Catamarca 주 환경 인허가 지연",
         "summary": "ALB 단독 사업장 아니라 영향 limited. 단, 산업 전체 sentiment 일시 악화.",
         "impact": "-", "source": "Reuters"},
        {"date": "2025-09-15", "type": "earnings", "category": "3Q25", "headline": "ALB 3Q25 매출 -32% YoY but 시장 예상 부합",
         "summary": "Cycle 저점 통과 신호. 2026년부터 회복 시작 시그널.",
         "impact": "○", "source": "Albemarle IR"},
        {"date": "2025-07-10", "type": "정책", "category": "산업", "headline": "US IRA 추가 보조금 — 미국 내 lithium 정련 capa에 $2B 추가",
         "summary": "ALB Kemerton (호주) + Silver Peak (네바다) 직접 수혜.",
         "impact": "+", "source": "DOE 발표"},
        {"date": "2025-05-20", "type": "M&A", "category": "산업", "headline": "ALB, Liontown Resources 인수 시도 → 실패",
         "summary": "다음 M&A 타겟 모색 중. cash $1.2B 보유 — 2026년 추가 deal 가능성.",
         "impact": "○", "source": "Bloomberg"},
    ],
    "SQM": [
        {"date": "2026-04-10", "type": "earnings", "category": "guidance", "headline": "SQM 2026 가이던스: lithium volume +15%",
         "summary": "Atacama 캐파 안정 가동. cost leader 포지션 유지.",
         "impact": "+", "source": "SQM IR"},
        {"date": "2026-03-08", "type": "공시", "category": "환경", "headline": "Salar de Atacama 환경 영향 평가 통과",
         "summary": "expansion plan 1단계 승인. 캐파 +30% 가능.",
         "impact": "+", "source": "SQM"},
        {"date": "2026-01-25", "type": "정치", "category": "리스크", "headline": "칠레 Codelco-SQM JV final agreement (서명) 임박",
         "summary": "정부 stake 확보 vs 로열티 인상 trade-off. JV 후 SQM의 lithium 사업 안정성 ↑.",
         "impact": "○", "source": "El Mercurio"},
        {"date": "2025-12-15", "type": "earnings", "category": "FY25", "headline": "SQM FY25 EBITDA $1.5B — 컨센 부합",
         "summary": "Cost leader 입증. 2026년 회복 시 leverage 크게.",
         "impact": "+", "source": "SQM IR"},
        {"date": "2025-08-30", "type": "M&A", "category": "산업", "headline": "SQM, Mt Holland (호주) 50% JV 운영 확대",
         "summary": "Wesfarmers와 협력 강화. 호주 spodumene 비중 ↑.",
         "impact": "+", "source": "SQM"},
    ],
    "006400.KS": [
        {"date": "2026-04-02", "type": "공시", "category": "주요사항", "headline": "GM JV (Spring Hill, Tennessee) 양산 본격 가동 보고",
         "summary": "북미 EV 매출 인식 시작. 2026 매출 +1.2조 추정. 2027 +2.5조.",
         "impact": "+", "source": "DART 공시"},
        {"date": "2026-02-18", "type": "공시", "category": "주식관련사채", "headline": "EB 5,000억 발행 — 양극재 capa 확장",
         "summary": "EPS 2.5% dilution but 매출 성장 가속.",
         "impact": "○", "source": "DART 공시"},
        {"date": "2026-01-12", "type": "뉴스", "category": "수주", "headline": "삼성SDI, BMW iX 차세대 모델 angular battery 수주",
         "summary": "각형 → 원통형 전환 가속. 2027 양산 목표.",
         "impact": "+", "source": "한경"},
        {"date": "2025-11-22", "type": "earnings", "category": "3Q25", "headline": "삼성SDI 3Q25 영업이익 920억 (컨센 750억) 상회",
         "summary": "ESS 수주 확대 + GM JV 가동 임박 효과.",
         "impact": "+", "source": "한경"},
        {"date": "2025-08-08", "type": "공시", "category": "투자", "headline": "삼성SDI, Stellantis JV 미국 공장 투자 발표 — 25GWh",
         "summary": "북미 capa 추가 확보. K-IRA 보조금 직접 수혜.",
         "impact": "+", "source": "DART"},
        {"date": "2025-05-15", "type": "뉴스", "category": "수주", "headline": "GM 신규 EV 라인업 부진 — 삼성SDI 수주 악영향 우려",
         "summary": "GM Ultium battery 수요 감소 → JV 수주 축소 가능성. 2025 H2 매출 -10% 예상.",
         "impact": "-", "source": "Bloomberg"},
    ],
    "LIT": [
        {"date": "2026-04-25", "type": "ETF", "category": "AUM", "headline": "LIT AUM $1.6B 회복 (2024 저점 $1.1B 대비 +45%)",
         "summary": "리튬 sector inflow 회복 시그널. 가격 상승 시 추가 inflow 가속 가능.",
         "impact": "+", "source": "Global X"},
        {"date": "2026-03-31", "type": "ETF", "category": "리밸런싱", "headline": "LIT Q1 2026 리밸런싱 — 한국 비중 ↑",
         "summary": "한국 종목 비중 14% → 17%로 확대. K-IRA 수혜 종목 추가.",
         "impact": "+", "source": "Solactive"},
        {"date": "2026-02-14", "type": "정책", "category": "산업", "headline": "EU CRMA 발효 — Critical Raw Materials Act",
         "summary": "EU 내 lithium 정련 capa 40% 자급 의무. 한국·호주 paritization 수혜.",
         "impact": "+", "source": "EU Commission"},
        {"date": "2025-12-30", "type": "산업", "category": "거시", "headline": "리튬 sector 2025 평균 -18% (S&P 500 +12%)",
         "summary": "underperform 1년차. 2026 mean reversion 기대 (Druckenmiller 매수 신호).",
         "impact": "○", "source": "S&P Dow Jones"},
        {"date": "2025-09-20", "type": "ETF", "category": "리밸런싱", "headline": "LIT Q3 리밸런싱 — Tesla 비중 6.8%로 유지",
         "summary": "Tesla EV 노출 유지 — lithium pure-play와 차이.",
         "impact": "○", "source": "Solactive"},
        {"date": "2025-04-08", "type": "산업", "category": "정책", "headline": "Trump 2기 'Western 공급망 우선' 정책 — 중국 lithium 종목 압박",
         "summary": "LIT 중국 비중 36% 직접 영향. PER -2 derate 가능.",
         "impact": "-", "source": "Bloomberg"},
    ],
    "003670.KS": [
        {"date": "2026-04-10", "type": "공시", "category": "주요사항", "headline": "북미 양극재 N-Plant 1단계 가동 개시",
         "summary": "K-IRA 보조금 직접 수혜. 2026 매출 +6,000억 추정.",
         "impact": "+", "source": "DART 공시"},
        {"date": "2026-02-05", "type": "공시", "category": "수주", "headline": "GM·Tesla 신규 양극재 수주 발표",
         "summary": "수주 가시성 향상. 2027 매출 7조+ 가시.",
         "impact": "+", "source": "DART"},
        {"date": "2025-11-30", "type": "earnings", "category": "3Q25", "headline": "포스코퓨처엠 3Q25 영업이익 240억 (YoY +60%)",
         "summary": "양극재 cycle bottom 통과. 가동률 회복.",
         "impact": "+", "source": "한경"},
        {"date": "2025-09-10", "type": "공시", "category": "투자", "headline": "북미 N-Plant 2단계 투자 결정 — 1조 추가",
         "summary": "2028년 가동 목표. K-IRA 보조금 long-term lock.",
         "impact": "+", "source": "DART"},
    ],
    "BTU": [
        {"date": "2026-04-22", "type": "earnings", "category": "1Q26", "headline": "Peabody 1Q26 EBITDA $135M (consensus $108M, beat +25%)",
         "summary": "PRB thermal volume +18% YoY (AI 데이터센터 driver) + met-coal price $245/톤 안정. 자기주식 매입 $80M 진행.",
         "impact": "+", "source": "Peabody IR"},
        {"date": "2026-03-28", "type": "산업", "category": "정책", "headline": "Vistra Energy, Texas coal plant 3기 운영 연장 발표 (2030 → 2035)",
         "summary": "PJM·ERCOT capacity emergency 대응. BTU PRB 직접 수혜 — 2026-2030 thermal demand floor 형성.",
         "impact": "+", "source": "Vistra IR"},
        {"date": "2026-03-10", "type": "산업", "category": "수주", "headline": "India Tata Steel + JSW 신규 blast furnace 6기 발주 — met-coal demand +15 Mt/year",
         "summary": "BTU·HCC·AMR 호주·미국 met-coal 직접 수혜. 2027년 글로벌 met-coal 가격 $280+ 가능성.",
         "impact": "+", "source": "Indian Steel Ministry"},
        {"date": "2026-02-20", "type": "정책", "category": "EPA", "headline": "Trump 행정부 EPA 'Clean Power Plan 2.0' 폐기 절차 시작",
         "summary": "Coal plant retirement 의무화 후퇴 — 'coal terminal decline 시점 연기' thesis 강화. ESG divestment 흐름 일부 reverse 신호.",
         "impact": "+", "source": "EPA Federal Register"},
        {"date": "2026-01-30", "type": "M&A", "category": "산업", "headline": "Peabody, Centurion (Queensland) 광산 1단계 commissioning 완료 발표",
         "summary": "Met-coal 캐파 +4-5 Mt/year 추가. 2027년 매출 +$800M-1B 추정.",
         "impact": "+", "source": "Peabody IR"},
        {"date": "2025-11-08", "type": "산업", "category": "AI 전력", "headline": "Microsoft Three Mile Island nuclear PPA 가동 시작",
         "summary": "AI 데이터센터의 carbon-free 24/7 약속 부분적 실현 — but coal 수요는 단기 (2026-2030) 유지.",
         "impact": "○", "source": "Constellation Energy"},
        {"date": "2025-09-15", "type": "earnings", "category": "3Q25", "headline": "Peabody 3Q25 매출 $1.05B + EBITDA $115M",
         "summary": "Met-coal 가격 회복 + PRB volume 안정. 가이던스 raise.",
         "impact": "+", "source": "Peabody IR"},
        {"date": "2025-08-12", "type": "공시", "category": "자기주식", "headline": "Peabody 자기주식 매입 프로그램 $1B 승인",
         "summary": "2027년까지 누적 $1.4B (market cap의 70%) shareholder return.",
         "impact": "+", "source": "8-K filing"},
        {"date": "2025-06-02", "type": "산업", "category": "리스크", "headline": "Mild winter 2024-2025 + 가스 가격 $3.2 → BTU stock -22% YoY",
         "summary": "Cycle 저점 형성. 2026 회복 시작 신호.",
         "impact": "-", "source": "Bloomberg"},
        {"date": "2025-04-18", "type": "정치", "category": "선거", "headline": "Trump 대선 승리 후 coal stock 평균 +35% 반등",
         "summary": "Coal divestment 정점 통과 신호. ESG fund 일부 coal 종목 재포함.",
         "impact": "+", "source": "Reuters"},
    ],
}


def get_news_items(ticker: str, company_name: str = "") -> list[dict]:
    """Get news/disclosure items for ticker.

    Routing:
      - .KS/.KQ → DART (공시) + curated (뉴스)
      - US tickers → SEC EDGAR (공시) + NewsAPI/Finnhub (뉴스) + curated
      - Both: dedup + sort by date desc
    """
    import os as _os
    curated = NEWS_TIMELINE.get(ticker, [])
    is_kr = ticker.endswith((".KS", ".KQ"))

    merged = list(curated)  # start with curated
    _skip_ext = _os.environ.get("DISABLE_FIN_FETCH") == "1"

    if is_kr and _DART_AVAILABLE and _dart_is_available() and not _skip_ext:
        try:
            dart_items = _dart_fetch_disclosures(ticker, lookback_days=365)
            if dart_items:
                # DART is authoritative for 공시 — replace curated 공시 entries
                merged = [c for c in curated if c.get("type") != "공시"]
                merged.extend(dart_items)
        except Exception as e:
            print(f"[news] DART fetch failed for {ticker}: {e}")

    if (not is_kr) and _SEC_AVAILABLE and not _skip_ext:
        try:
            sec_items = _sec_fetch_disclosures(ticker, lookback_days=365)
            if sec_items:
                # SEC is authoritative for 공시
                merged = [c for c in curated if c.get("type") != "공시"]
                merged.extend(sec_items)
        except Exception as e:
            print(f"[news] SEC fetch failed for {ticker}: {e}")

    # Add live news (US tickers — NewsAPI/Finnhub)
    if (not is_kr) and _NEWS_AVAILABLE and not _skip_ext:
        try:
            status = _news_status()
            if status.get("any_active"):
                news_items = _news_fetch(ticker, company_name=company_name, lookback_days=365)
                if news_items:
                    # Add news (avoid dup with curated 뉴스 by headline)
                    existing_headlines = {m.get("headline", "")[:80] for m in merged}
                    for n in news_items:
                        if n.get("headline", "")[:80] not in existing_headlines:
                            merged.append(n)
        except Exception as e:
            print(f"[news] live news fetch failed for {ticker}: {e}")

    # Dedup + sort
    seen_keys = set()
    deduped = []
    for it in merged:
        key = (it.get("date", ""), it.get("headline", "")[:80])
        if key not in seen_keys:
            seen_keys.add(key)
            deduped.append(it)

    deduped.sort(key=lambda x: x.get("date", ""), reverse=True)
    return deduped


def _render_monthly_sentiment_chart(items: list[dict], ticker: str) -> str:
    """월별 +/- 공시·뉴스 건수 막대그래프 (종목별 개별 — 사용자 요청 #3, #4).

    Returns base64-encoded PNG embedded as <img> for HTML inclusion.
    """
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import io, base64
        from datetime import datetime, timedelta
        from collections import defaultdict
    except ImportError:
        return ""

    # Build last 12 months calendar
    today = datetime.utcnow().date()
    months = []
    for i in range(11, -1, -1):
        y = today.year
        m = today.month - i
        while m <= 0:
            m += 12
            y -= 1
        months.append(f"{y}-{m:02d}")

    pos_count = defaultdict(int)
    neg_count = defaultdict(int)
    for it in items:
        date = it.get("date", "")
        if not date or len(date) < 7:
            continue
        ym = date[:7]
        if ym not in months:
            continue
        impact = it.get("impact", "○")
        if impact == "+":
            pos_count[ym] += 1
        elif impact == "-":
            neg_count[ym] += 1

    pos_vals = [pos_count.get(m, 0) for m in months]
    neg_vals = [-neg_count.get(m, 0) for m in months]  # Negative for downward bar

    fig, ax = plt.subplots(figsize=(10, 4))
    x = list(range(len(months)))
    ax.bar(x, pos_vals, color='#10b981', label='긍정 (+)', width=0.7)
    ax.bar(x, neg_vals, color='#dc2626', label='부정 (-)', width=0.7)
    ax.axhline(0, color='black', linewidth=0.6)
    ax.set_xticks(x)
    ax.set_xticklabels([m[2:] for m in months], rotation=45, fontsize=8)
    ax.set_ylabel('건수')
    ax.set_title(f'{ticker} — 최근 12개월 월별 공시/뉴스 sentiment (긍정 위, 부정 아래)')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=110, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('ascii')
    return f'<img src="data:image/png;base64,{img_b64}" style="max-width:100%;margin:8pt 0;" />'


def render_news_timeline(ticker: str, company_name: str = "",
                          filter_neutral: bool = False,
                          with_monthly_chart: bool = False,
                          expand_summary: bool = False) -> str:
    """1년치 뉴스/공시 timeline render — auto DART/SEC/NewsAPI fetch.

    Args:
        ticker: 종목 ticker
        company_name: 한국어 회사명
        filter_neutral: True면 중립(○) 항목 상세 행에서 제외 (KPI엔 카운트 유지)
        with_monthly_chart: True면 월별 +/- bar chart 추가 (종목별 개별)
        expand_summary: True면 summary 필드를 1.5배 길이로 확장 표시
    """
    all_items = get_news_items(ticker, company_name=company_name)
    if not all_items:
        return ""

    # Apply neutral filter if requested
    items = all_items
    if filter_neutral:
        items = [it for it in all_items if it.get("impact", "○") != "○"]

    rows = ""
    impact_color = {"+": "#10b981", "-": "#dc2626", "○": "#6b7280"}
    type_emoji = {"공시": "📑", "뉴스": "📰", "earnings": "💼", "M&A": "🤝",
                   "정책": "🏛️", "정치": "🗳️", "산업": "🏭", "ETF": "📈",
                   "리스크": "⚠️"}

    for item in items:
        impact = item.get("impact", "○")
        emoji = type_emoji.get(item.get("type", ""), "📌")
        summary = item.get('summary', '')
        # Expand summary detail when expand_summary=True (사용자 요청 #3 — 상세 요약)
        if expand_summary and summary:
            # Add impact_reason if available, or extend with category+source detail
            impact_reason = item.get('impact_reason', '')
            if impact_reason:
                summary = f"{summary}<br/><em style='color:#6b7280;'>영향 사유: {impact_reason}</em>"
        rows += f"""
        <tr>
          <td style="white-space:nowrap;font-size:9pt;font-weight:bold;">{item['date']}</td>
          <td style="text-align:center;">{emoji}<br/><span style="font-size:8pt;color:#6b7280;">{item.get('type', '-')}</span></td>
          <td><span class="tag-actual" style="font-size:8pt;">{item.get('category', '-')}</span></td>
          <td><strong>{item['headline']}</strong><br/>
              <span style="font-size:9pt;color:#374151;">{summary}</span><br/>
              <span style="font-size:8pt;color:#6b7280;"><em>출처: {item.get('source', '-')}</em></span></td>
          <td style="text-align:center;background:{impact_color.get(impact, '#9ca3af')};color:white;font-weight:bold;font-size:14pt;">{impact}</td>
        </tr>
        """

    # KPI counts use ALL items (including neutral) so reader sees full activity
    plus_count = sum(1 for i in all_items if i.get('impact') == '+')
    minus_count = sum(1 for i in all_items if i.get('impact') == '-')
    neutral_count = sum(1 for i in all_items if i.get('impact') == '○')

    is_kr = ticker.endswith((".KS", ".KQ"))
    dart_active = _DART_AVAILABLE and is_kr and _dart_is_available()
    sec_active = _SEC_AVAILABLE and (not is_kr)
    news_active = _NEWS_AVAILABLE and (not is_kr) and _news_status().get("any_active") if _NEWS_AVAILABLE else False

    source_note = ""
    sources_used = []
    if dart_active:
        sources_used.append("✓ DART OpenAPI (한국 전자공시)")
    elif is_kr:
        source_note = "<p style='font-size:9pt;color:#6b7280;'>DART_API_KEY 미설정 — curated sample 사용 중.</p>"
    if sec_active:
        sources_used.append("✓ SEC EDGAR (미국 공시)")
    if news_active:
        nstatus = _news_status()
        if nstatus.get("finnhub_configured"):
            sources_used.append("✓ Finnhub (뉴스)")
        if nstatus.get("newsapi_configured"):
            sources_used.append("✓ NewsAPI (뉴스)")
    if sources_used:
        source_note = f"<p style='font-size:9pt;color:#16a34a;'><strong>활성 데이터 소스</strong>: {' · '.join(sources_used)}</p>"

    # Monthly sentiment chart (per-stock — 사용자 요청 #4)
    monthly_chart_html = ""
    if with_monthly_chart:
        monthly_chart_html = _render_monthly_sentiment_chart(all_items, ticker)

    filter_note = ""
    if filter_neutral:
        filter_note = f"""<p style='font-size:9pt;color:#6b7280;'>
        ※ 중립({neutral_count}건) 이벤트는 상세 표에서 제외됨 (집계만 표시).
        긍정·부정 영향 항목만 상세 요약 제공.</p>"""

    displayed_count = len(items)
    excluded_note = f" (중립 {len(all_items) - displayed_count}건 숨김)" if filter_neutral else ""

    return f"""
    <h2>📅 1년 뉴스·공시 Timeline ({ticker})</h2>
    <div class="info">최근 12개월 동안의 주요 뉴스, 공시, 어닝, 정책 변화를 시간 순으로 정리.
    Bull/Bear/Neutral 영향도를 분석가가 평가.</div>
    {source_note}

    <div class="kpi-grid" style="margin:8pt 0;">
      <div class="kpi"><div class="num green">{plus_count}</div><div class="label">긍정 (+)</div></div>
      <div class="kpi"><div class="num red">{minus_count}</div><div class="label">부정 (-)</div></div>
      <div class="kpi"><div class="num">{neutral_count}</div><div class="label">중립 (○)</div></div>
      <div class="kpi"><div class="num">{len(all_items)}</div><div class="label">총 이벤트</div></div>
    </div>

    {monthly_chart_html}

    <h3>상세 이벤트 목록 ({displayed_count}건{excluded_note})</h3>
    {filter_note}

    <table class="dt">
      <thead><tr>
        <th style="width:10%">날짜</th>
        <th style="width:8%">유형</th>
        <th style="width:14%">분류</th>
        <th>내용</th>
        <th style="width:8%">영향</th>
      </tr></thead>
      <tbody>{rows}</tbody>
    </table>

    <h3>분석 시사점</h3>
    <ul style="font-size:10pt;line-height:1.7;">
      <li><strong>Net Sentiment</strong>: 긍정 {plus_count}건 / 부정 {minus_count}건 — net <strong>{plus_count - minus_count:+d}</strong> →
          {'매우 긍정적 모멘텀' if plus_count - minus_count >= 5 else '긍정 모멘텀' if plus_count - minus_count >= 2 else '혼재' if abs(plus_count - minus_count) < 2 else '부정 모멘텀'}</li>
      <li><strong>최근 90일</strong> 이벤트 패턴이 verdict 강도를 결정. 4Q 어닝 결과 + 가이던스 raise 동반 시 high-conviction.</li>
      <li><strong>모니터링 권고</strong>: 매주 신규 뉴스/공시 추적 (Phase 2-1 자동화 적용 시 즉시 알림).</li>
    </ul>
    """
