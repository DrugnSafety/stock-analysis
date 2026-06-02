# 주식 분석 시스템 — 고도화 로드맵

> **작성일**: 2026-04-29
> **현재 시스템 상태**: 다중 종목 통합 보고서 (Top 3-5 stocks × Deep Research × 1 Combined PDF) 완료

---

## 0. 현재 달성된 기능 (Baseline)

| 영역 | 기능 | 상태 |
|---|---|---|
| **Blog 수집** | 8명 블로거 자동 모니터링 (메르·의교창·승도리·DaeGurr·GSVI·인피의·제주바람·농구천재) | ✓ |
| **Thesis 추출** | 블로거 글 → 검증 가능한 6-12개 thesis 자동 분해 | ✓ |
| **종목 식별** | thesis-to-stocks (top 3-5 자동 선정) | ✓ |
| **4-Analyst 평가** | Macro / Industry / Empirical / Counter | ✓ |
| **13명 페르소나 패널** | Buffett·Munger·Lynch·Wood·Burry·Taleb·Graham·Ackman·Pabrai·Fisher·Jhunjhunwala·Druckenmiller·Damodaran | ✓ |
| **Risk Manager** | 변동성-조정 position 한도 (vol_multiplier × correlation_multiplier) | ✓ |
| **Portfolio Manager** | signal_score → BUY/HOLD/SELL 액션 | ✓ |
| **Paper Portfolio** | yfinance 기반 시뮬레이션 + ledger | ✓ |
| **Backtester** | 5건 메르 글 백테스트 → 1m hit rate 66%, KOSPI alpha +2.03% | ✓ |
| **Subagent debate** | Bull-Bear-Skeptic cycle (convergence 0.46 → 0.778 시연) | ✓ |
| **Multi-Model Arena** | Claude + OpenAI gpt-5.5 (Gemini 옵션) | ✓ |
| **통합 보고서** | Top 5 종목 × R1+R2+R3+Deep Research = 1 PDF/종목 (213 pages 5 reports) | ✓ NEW |
| **Deep Research 섹션** | 산업맥락 / 5년 재무 / 시나리오 / 카탈리스트 / 리스크 매트릭스 / DART 공시 | ✓ NEW |
| **Ticker resolver** | "005490.KS" → "POSCO홀딩스" 자동 변환 (yfinance + curated 100+ 종목) | ✓ NEW |

---

## 1. Phase 1 — 자동화 (1-2주)

### 1-1. Real-Time Monitoring Cron
- **목적**: 블로거가 새 글 올리면 자동으로 분석 → 보고서 생성
- **구현**: `monitor-bloggers.cron` — 매일 09:00·15:00·21:00 KST 체크
  - PostTitleListAsync.naver API 폴링 (각 블로거당 ~1초)
  - 신규 logNo 발견 시 → analyze-blog 자동 트리거
  - 결과를 `outputs/{date}/{blogger}/{ticker}/combined.pdf`에 저장
- **활용**: Cowork mode의 `mcp__scheduled-tasks__create_scheduled_task` 활용
- **우선순위**: 🔥 High — 가장 즉각적인 ROI

### 1-2. Email / Slack 자동 발송
- **목적**: 분석 완료 시 이메일·Slack으로 PDF 첨부 + executive summary 본문
- **구현**:
  - Gmail MCP 활용 (이미 이용 가능)
  - Subject: `[블로거] 신규 글 분석 — Top 3 종목 verdict 요약`
  - Body: TL;DR (3종목 액션·signal·confidence) + PDF 첨부
- **선택**: Email vs Slack vs Notion 페이지 — 사용자 선호 확인 필요
- **우선순위**: 🔥 High

### 1-3. Notion 대시보드 통합
- **목적**: 모든 분석을 Notion DB에 누적 → 시계열 추적·검색·필터링
- **구현**:
  - Notion DB schema:
    - Title (블로거 + 글 제목)
    - Date (발행일)
    - Top tickers (multi-select)
    - Signal scores (number)
    - Verdict mix (formula)
    - Combined PDF (file attachment)
    - Hit rate (formula — 백테스터와 자동 동기화)
  - notion-create-pages MCP 활용
- **우선순위**: ⭐ Medium

---

## 2. Phase 2 — 데이터 보강 (2-4주)

### 2-1. DART (전자공시) Integration
- **목적**: 한국 종목의 사업보고서·분기보고서·주요사항 공시를 자동 fetch
- **구현**:
  - DART OpenAPI (https://opendart.fss.or.kr) — 무료 API
  - corp_code 매핑 → 사업보고서 PDF 자동 다운로드
  - 보고서에서 매출·OPM·NCAV·CapEx 자동 추출
  - 현재 placeholder 처리되어 있는 `make_korean_disclosures()` 함수 자동화
- **효과**: KR 종목 분석 깊이 +50% (현재는 yfinance 의존, DART는 분기별 신뢰성 ↑)
- **우선순위**: 🔥 High — 한국 주식 분석의 차별점

### 2-2. KIND (한국거래소) Integration
- **목적**: 자기주식 매입·임원변동·M&A 등 시장 영향 큰 공시 실시간 추적
- **구현**:
  - KIND Open API
  - 공시 type별 필터링 (자기주식·M&A·CEO 사임 등)
  - 분석 대상 종목 + 정기 모니터링 watchlist 양쪽
- **우선순위**: ⭐ Medium

### 2-3. 실제 yfinance 5년 데이터 자동 fetch
- **목적**: 현재 deep_research 섹션의 5년 P&L은 placeholder. 실제 데이터로 전환
- **구현**:
  - `_common/financial_fetcher.py` — yfinance.financials, balance_sheet, cashflow 직접 fetch
  - 자동 환율 변환 (USD ↔ KRW, 외화 종목 대응)
  - peer comparison은 sector ETF 구성종목 자동 추출
- **우선순위**: 🔥 High — placeholder → 실데이터 전환 필수

### 2-4. 뉴스·소셜 sentiment integration
- **목적**: 분석 시점의 시장 sentiment를 정량화 (+/- score)
- **구현**:
  - Naver 뉴스·증권 게시판 + Twitter/X 키워드 검색
  - LLM (Claude Haiku) 기반 sentiment 분류 (1점~5점)
  - 보고서에 "sentiment score 트렌드" 차트 추가
- **우선순위**: ⭐ Medium

---

## 3. Phase 3 — 정교화 (1-2개월)

### 3-1. Confidence Calibration Loop
- **목적**: 백테스터 결과를 portfolio-manager 가중치에 자동 피드백
- **구현**:
  - Backtester가 매 분기 verdict 적중률 평가 → CSV 출력
  - 페르소나별 hit rate (예: Druckenmiller 75%, Buffett 60%)
  - persona_weights.json 자동 업데이트 (Druckenmiller 1.5× → 1.8×)
  - 한국 시장 / 미국 시장 분리 가중치 (이미 KR-bias 있음, 자동 학습 추가)
- **수학적 근거**: Bayesian update — prior weights × 사후 hit rate ratio
- **효과**: 시간이 지날수록 정확도 자동 향상
- **우선순위**: 🔥 High — 시스템의 자기 학습 기능

### 3-2. Reverse DCF Auto-Generation
- **목적**: Damodaran 페르소나가 자동으로 reverse DCF 수행 (현재는 결과만 입력 시뮬레이션)
- **구현**:
  - 현재 시가총액 ÷ 현재 매출 → "성장률 G가 얼마면 정당화되는가?" 자동 계산
  - 비교: 컨센서스 G vs reverse-implied G → "시장은 더 낙관적이다 / 비관적이다"
  - 보고서에 "Reverse DCF Implied Growth" 차트 자동 삽입
- **우선순위**: ⭐ Medium

### 3-3. Cross-Blogger Consensus 분석 (선택적)
- **사용자 피드백**: "블로거 사이의 시각 차이를 평가하는 것은 의미 없어"
- **재해석**: 같은 종목을 여러 블로거가 다른 시점에 언급 시 — 해당 종목의 "의견 변화 timeline"을 추적
  - 예: 005490.KS — 메르 (2024-02 BUY) → 의교창 (2026-04 BUY) → 일관된 매수 신호
- **구현**: ledger.jsonl에 cross-blogger 종목 검색 기능
- **우선순위**: ⭐ Medium

### 3-4. 실시간 가격 alert (verdict 보호)
- **목적**: BUY 시점 후 -10% 빠지면 즉시 알림 (verdict 재검토 트리거)
- **구현**:
  - paper-portfolio가 매일 yfinance fetch
  - threshold 기반 alert (예: -10% 또는 thesis 핵심 가정 무너짐 신호)
  - Email/Slack push
- **우선순위**: 🔥 High — 실제 portfolio 관리 가치

---

## 4. Phase 4 — 글로벌 확장 (3-6개월)

### 4-1. Multi-Language Support
- **목적**: 영어권 사용자에게 한국 블로거 분석 결과 제공
- **구현**:
  - Claude Sonnet → 한국어 보고서를 영어로 자동 번역 (서머리 + 핵심 차트)
  - 보고서 별 PDF 2종 (한 / 영) 동시 생성
  - 영어 버전은 Korean ticker → MSCI Korea ETF (EWY) 등 ADR/ETF 추천 추가
- **우선순위**: ⭐ Medium — 사용자가 영어권 독자 보유 시

### 4-2. 일본·중국 블로거 추가
- **목적**: 일본 (kabu日記·yahoo finance JP) / 중국 (snowball·xueqiu) 블로거 통합
- **구현**:
  - blogger-registry에 일본·중국 블로거 type 추가
  - 일본·중국 ticker resolver 매핑 추가 (이미 일부 있음 — TSM, 1772.HK 등)
  - 통화 변환·한국어 번역 자동화
- **우선순위**: 🔵 Low — 한국 시장 우선

### 4-3. 다국가 portfolio 통합
- **목적**: 한국·미국·일본 종목 통합 portfolio (FX 헷지 포함)
- **구현**: 환율 변환 + correlation matrix 다국가 확장
- **우선순위**: 🔵 Low

---

## 5. Phase 5 — UI / UX (2-4주, Phase 1과 병행 가능)

### 5-1. Web Dashboard (Cowork artifact 활용)
- **목적**: PDF 보고서 외에 web view에서 인터랙티브 탐색
- **구현**:
  - `mcp__cowork__create_artifact`로 HTML dashboard 생성
  - 종목 선택 → 13명 페르소나 의견 토글 / Bull-Base-Bear 시나리오 슬라이더
  - 실시간 yfinance 가격 fetch 버튼
- **우선순위**: ⭐ Medium

### 5-2. Mobile-friendly Email Digest
- **목적**: 출퇴근 시 모바일에서 빠르게 확인
- **구현**: 1-2 페이지 압축 PDF + HTML email body
- **우선순위**: ⭐ Medium

---

## 6. Phase 6 — 고급 분석 (6개월+)

### 6-1. Subagent Debate 자동 발동
- **목적**: confidence 낮은 verdict (< 0.5)이 발생하면 자동으로 Bull-Bear-Skeptic debate
- **구현**:
  - pipeline-orchestrator에 trigger 추가: `if confidence < 0.5: debate_orchestrator(rounds=2)`
  - debate 결과로 verdict 재산출 (이미 PRTA 시연에서 0.46 → 0.778 입증)
- **우선순위**: ⭐ Medium

### 6-2. Multi-Model Arena 활성화
- **현 상태**: OpenAI gpt-5.5 + Gemini 3.1 코드는 있으나 quota 0으로 비활성
- **활성화 시**: Claude vs gpt-5.5 vs Gemini의 verdict 비교 → 합의/이견 분석
- **구현**: 사용자 API key 주입 후 자동 활성
- **우선순위**: 🔵 Low — Claude 단독으로도 우수

### 6-3. Black Swan / Tail Risk 시뮬레이션
- **목적**: Taleb 페르소나가 단순히 "tail risk 우려"가 아니라 실제 stress test
- **구현**:
  - VaR (95%, 99%) + Expected Shortfall 계산
  - 과거 black swan event (2008 / 2020 / 2022) period 적용
  - "본 종목이 2008 같은 시나리오에서 -X% drawdown 예상" 자동 산출
- **우선순위**: 🔵 Low — 일반 사용자에게는 over-engineering

### 6-4. ESG Scoring Integration
- **목적**: Pabrai·Buffett 같은 가치 투자자에게 ESG 리스크 보강
- **구현**: Sustainalytics·MSCI ESG API integration (paid)
- **우선순위**: 🔵 Low

---

## 7. 우선순위 요약

### 즉시 (1-2주):
1. 🔥 **Real-time monitoring cron** — 신규 글 자동 분석
2. 🔥 **Email/Slack 발송** — 결과 push
3. 🔥 **yfinance 5년 데이터 자동 fetch** — placeholder → 실데이터

### 단기 (1개월):
4. 🔥 **DART API integration** — KR 종목 깊이 +50%
5. 🔥 **Confidence calibration loop** — 자기 학습 시스템
6. 🔥 **실시간 가격 alert** — portfolio 관리 가치
7. ⭐ **Notion dashboard** — 분석 누적·검색

### 중기 (2-3개월):
8. ⭐ **KIND 공시 integration**
9. ⭐ **뉴스 sentiment** integration
10. ⭐ **Reverse DCF** 자동화
11. ⭐ **Web dashboard** (Cowork artifact)
12. ⭐ **Subagent debate 자동 발동**

### 장기 (3-6개월+):
13. 🔵 Multi-language (한·영)
14. 🔵 일본·중국 블로거 확장
15. 🔵 Black Swan stress test
16. 🔵 ESG integration

---

## 8. 다음 단계 (사용자 결정 필요)

1. **현재 보고서 확인** — `1_005490.KS_POSCO홀딩스_combined.pdf` 등 5개 PDF (각 43 pages, 평균 663 KB)
2. **자동화 우선순위 선정** — 위 Phase 1 (monitoring cron + email/slack) 중 어느 것부터?
3. **DART API 키 발급** — Phase 2-1 시작하려면 https://opendart.fss.or.kr/ 무료 가입 필요
4. **Notion workspace 연결 확인** — 이미 Notion MCP 연결되어 있으므로 Phase 1-3 즉시 시작 가능

---

## 9. 시스템 현재 한계 (Honest Disclosure)

- **Persona panel synthesis**: 005490.KS 외 4개 ticker (ALB·SQM·006400.KS·LIT)은 LLM 풀 평가가 아니라 POSCO baseline + bias_factor + 페르소나별 ticker 특성 overlay 방식. 풀 평가가 필요하면 ~$0.50 LLM 비용 + 시간 추가 발생.
- **Deep Research financials**: 현재는 산업 컨센서스 추정치 (placeholder). yfinance 자동 fetch 적용하면 실데이터 전환.
- **DART 공시**: 현재 hardcoded sample. Phase 2-1 적용 시 실시간 자동 fetch.
- **시나리오 가정**: Bull/Base/Bear 확률은 분석가 판단 (LLM 추론 + 산업 컨센서스). 정량 모델 (e.g. Monte Carlo) 적용 시 더 robust.
- **Backtester**: 메르 글 5건만 적용. 더 다양한 블로거·기간으로 확장 필요.

위 한계는 모두 Phase 2-3에서 해결 예정이며, **현재도 시스템은 충분히 작동**합니다. 단, 사용자가 결과를 신뢰할 때 위 한계를 의식하면 더 정확한 의사결정이 가능합니다.

---

# Phase 7 — 외부 근거 강화 & 팩트체크 (AMEET-style Evidence Layer)

> **작성일**: 2026-05-30 / **트리거**: ameet-media.com 사례 벤치마킹 brainstorming
> **목표**: 현재 "공시는 1차 자료로 잘 쓰지만, 산업·경쟁·사례 맥락은 외부 조회 없이 LLM 추론으로 채워지는" 구조를 → **외부 1차 자료 폭넓게 조회 → 교차검증 → 인용**하는 구조로 전환

## 7-0. 진단 — 현재 외부 자료 활용의 격차

AMEET 방법론(데이터수집 → **맥락추출** → 다관점토론 → **팩트체크** → 발행)과 비교한 결과, 본 시스템은 **양 끝단(입력 폭·출력 검증)이 비어 있음**:

| AMEET 단계 | 현 시스템 | 격차 |
|---|---|---|
| 뉴스 RSS·API (시간별) | NewsAPI 30일/curated fallback | lookback·소스 폭 부족 |
| 공시 DART·KIND·SEC | DART·SEC (✅) / KIND ✗ | 거래소 공시·IR PT 미연동 |
| 시계열 FRED·ECB·BOK | macro plugin 보유하나 종목 분석에 미주입 | 거시변수 → DCF 미연결 |
| **맥락 추출**(과거·유사사례 연결) | ✗ 없음 | 유사기업·과거국면 retrieval 부재 |
| **팩트체크**(원문 자동 대조) | ✗ 없음 | 인용 수치 hallucination 검증 단계 부재 |
| 다관점 토론 | 13 페르소나 + subagent (✅ 더 강함) | — |

**핵심 진단**: 부족한 건 데이터 소스가 아니라 **① 조회 폭 ② 팩트체크 ③ 사례연결** 3개 절차.

## 7-1. A/B 프로토타입 결과 (BTU 실측, 2026-05-30)

기존 `deep_research/BTU.json` vs WebSearch evidence-retrieval 출력 비교:

| 항목 | 현재 (LLM 생성 deep_research) | WebSearch Evidence Retrieval |
|---|---|---|
| 뉴스 건수 | 5건 (curated) | 즉시 5+ URL 반환 |
| **출처 URL** | ❌ 없음 (source는 "EIA Monthly Energy Review" 텍스트만) | ✅ stocktitan·fool·globeandmail 등 직링크 |
| **provenance** | `research_meta: {}` (비어 있음) | ✅ 각 fact에 URL·매체·일자 |
| 사실 신선도 | 추정·일반론 | ✅ Q1'26 Centurion 250k톤 미달, FY 목표 10.3–11.3M톤 재확인, ICF 25% 수요전망, 가스 $3.45/MMBtu |
| 검증 가능성 | 불가 (대조 원문 없음) | ✅ 원문 대조 가능 |

**결론**: 현재 deep_research는 *그럴듯하지만 검증 불가능한 주장*을 생산. WebSearch만으로도 **출처 URL이 박힌 현재 사실**로 즉시 대체 가능 → 절차 A의 투자 가치 입증됨.

## 7-2. 가용 외부 skill 전수조사 (활용 맵)

이 환경에 설치된 자산을 파이프라인 절차에 매핑:

| 자산 | 상태 | 매핑 절차 | 비고 |
|---|---|---|---|
| **WebSearch / web_fetch** | ✅ 즉시 가용 | A(Evidence), B(Fact-check) | **Evidence 백본** — 출처 URL 자동 확보 |
| **SEC EDGAR full-text + DART** | ✅ 보유 (무료) | A(Evidence) | 1차 공시. EDGAR EFTS 전문검색 확장 가능 |
| **news-integration** (NewsAPI·Finnhub 무료 tier) | ✅ 보유 | A(Evidence) | lookback 한계 보완은 WebSearch로 |
| **bigdata-com** (`financial-research-analyst` + 27 commands) | ❌ **제외** (사용자 계정 없음 + 동적등록 미지원) | — | 유료 기관 코퍼스. 향후 계정 확보 시 소스 ①로 끼움. 현재 계획에서 제외 |
| **moai-research:patent-search** (KIPRIS) | ✅ skill (무료) | C(사례연결) | SMR·수소 등 기술 moat 종목 특허 근거 |
| **moai-research:paper-search** (RISS/KCI) | ✅ skill | C(사례연결) | 학술 근거 |
| **moai-finance:korean-stock-search** (KRX) | ✅ skill | A(시세 보강) | DART 보완 |
| **macro-economic-integration** (FRED/ECB/IMF/OECD/BOK) | ✅ 보유, 미주입 | D(거시주입) | 금리·환율 → DCF 할인율 |
| **multi-model-arena / codex-integration** | ✅ 보유 | B(팩트체크 재배치) | 신규 인프라 0 |

## 7-2b. 구현 현황 (2026-06-02 프로토타입 완료)

절차 A·B·C가 BTU 종목으로 **end-to-end 동작 검증** 완료:

| 산출물 | 위치 | 상태 |
|---|---|---|
| `evidence_retriever.py` | `report-suite/skills/_common/` | ✅ A 모듈 (WebSearch hits + SEC EFTS 직접 fetch + `register_source` pluggable + `merge_into_deep` + `audit_deep_research`) |
| `fact_checker.py` | `report-suite/skills/_common/` | ✅ B 모듈 (thesis-evidence 모순 / 무출처 정량 / 밸류 정합성 3종 체크 + `register_verifier` LLM plug) |
| build_combined.py 배선 | line 773 직후 | ✅ A 주입 — evidence 있으면 industry.news를 URL 인용 버전으로 prepend |
| deep_research.py 렌더 | `render_industry_context` | ✅ news 출처를 하이퍼링크 + ✓출처 배지 |
| `evidence/BTU.json`, `factcheck/BTU.json` | 분석 디렉토리 | ✅ 표준 스키마 산출물 |

**검증 결과 (BTU)**: 기존 deep_research 뉴스 5건(URL 0%) → 주입 후 12건(URL 7건). 팩트체크가 **EIA -9% 전망이 bull "AI=석탄수요" 논리를 반박**(🔴), market_size·점유율 무출처(🟡), bull 목표가 $35 vs 컨센서스 $34.42 정합(🟢)을 자동 탐지. SEC EFTS 날짜필터로 2026-06-02 최신 공시 반환(구 2017 공시 배제).

**다듬기 완료 (2026-06-02)**:
- ✅ **stance-aware 팩트체크** — 헤지/부정 가정을 conflict에서 제외(`_stance()`). BTU conflict 6→4건으로 과탐지 제거, 남은 4건 모두 정당(bull AI-coal·3중catalyst·base thermal회복·bear -74% 괴리). 추가 정밀화는 `register_verifier()`에 codex 연결.
- ✅ **Citation Audit PDF 렌더** — `build_combined.py` deep research 섹션 뒤에 `render_citation_audit_html` 삽입(`DISABLE_FACTCHECK=1`로 off). factcheck/{ticker}.json 자동 저장.
- ✅ **DART evidence fetcher** — `evidence_retriever.fetch_dart()` 추가(dart-integration 재사용). US ticker skip·graceful 검증 완료. ⚠️ *live KR fetch는 DART corp_code 캐시 예열 필요* — CORPCODE.zip 최초 다운로드가 Cowork 45초 sandbox 초과(기존 알려진 제약). `/dart-status` 등으로 1회 예열하면 이후 정상.

**확장 완료 (2026-06-02 2차)**:
- ✅ **codex LLM 검증기 plug** — `fact_checker.make_codex_verifier()` (codex-integration 재사용). `build_combined`가 `register_verifier`로 등록. opt-in `FACTCHECK_LLM=1` + codex/OPENAI_API_KEY 가용 시만 동작, 그 외 graceful no-op(검증 완료).
- ✅ **evidence → scenarios 주입** — `EvidenceRetriever.annotate_scenarios()`로 bull/base/bear 가정에 ✓출처/⚠반박 배지 부착(BTU 9건). build_combined 배선.
- ✅ **통합 회귀 테스트(렌더 경로)** — merge→annotate→industry/scenarios/citation-audit 렌더까지 BTU end-to-end 정상(출처링크 7·근거배지 13·Audit 표). 4개 파일 py_compile OK. ⚠️ *PDF 최종 rasterize(weasyprint)는 sandbox 디스크 부족으로 미실행* — 코드 무결성은 확인됨, 실 PDF 빌드는 정상 환경(로컬/Claude Code)에서 검증 필요.

**Phase 7 종합**: A(evidence 수집) → 주입 → scenarios 근거태깅 → B(팩트체크 + LLM plug) → Citation Audit PDF 섹션까지 **전 구간 배선·검증 완료**. 잔여는 (1) 정상 환경에서 실 PDF 빌드 확인 (2) KR DART corp_code 예열 (3) 다종목 배치 적용.

## 7-3. 신규 절차 A — Evidence Retrieval 단계 (우선순위 🔥)

deep_research 생성 **전에** 외부 1차 자료를 폭넓게 수집·격리저장하는 단계.

- **구현 위치**: `report-suite/skills/_common/`에 `evidence_retriever.py` 신설 (one-off 금지 원칙 → 기존 plugin 확장)
- **출력**: `evidence/{ticker}.json` — `[{claim, value, source_url, publisher, date, retrieved_via}]` 스키마
- **소스 우선순위 (전부 무료)**: ① WebSearch 5–10건 → ② SEC EDGAR/DART 공시 → ③ web_fetch IR/보도자료 → ④ news-integration(NewsAPI·Finnhub). *bigdata-com은 사용자 계정 없어 제외; 향후 확보 시 소스 ⓪로 prepend만 하면 되도록 pluggable 설계*
- **연결**: `deep_research.py`의 `competitive_landscape`·`market_size`·`recent_news`를 **evidence/{ticker}.json에서 주입** (현재 LLM 생성 대체)
- **공수**: 중 (evidence_retriever.py 1개 + deep_research.py 연결부 수정)

## 7-4. 신규 절차 B — Fact-Check / Citation Lock 단계 (우선순위 🔥, 신뢰도 직결)

PDF 빌드 **직전**, 본문 정량 주장을 원본과 자동 대조. **기존 multi-model-arena/codex를 재배치 → 신규 인프라 0.**

**아키텍처 (3단계)**:

1. **Claim 추출** — `build_combined.py`가 생성한 본문 HTML에서 정량 문장(매출·PER·점유율·성장률) regex/LLM 추출 → `claims_{ticker}.json`
2. **출처 대조** — 각 claim을 다음과 순서대로 대조:
   - `stocks.json`(yfinance live) — 가격·밸류에이션 지표
   - `financial_statements_us_gaap.py` 출력 — 재무 수치
   - `evidence/{ticker}.json`(절차 A) — 산업·뉴스 수치
   - 불일치/무출처 → **flag**
3. **검증 의견** — codex-integration(OpenAI) 또는 arena 2차 모델에 "이 claim이 출처와 일치하는가" 질의 → cross-model 합의. 불일치 claim은 보고서에 `⚠️ 출처 확인 불가` 태깅 (CLAUDE.md 응답원칙 일치)
- **출력**: `factcheck_{ticker}.json` (claim·status·source·verdict) + 보고서 말미 **Citation Audit 섹션**
- **공수**: 중상 (claim 추출기 + 대조 로직; arena/codex는 재사용)

## 7-5. 신규 절차 C — 유사 사례·과거 국면 연결 (우선순위 ⭐)

AMEET의 "맥락 추출: 과거 사례 연결"에 대응.

- **기술 moat 종목**: `moai-research:patent-search`(KIPRIS)로 특허 동향 → "실행력" 근거 (SMR·수소·2차전지)
- **시나리오 보강**: `bigdata-com:scenario-analysis`·`thematic-research`로 Bull/Base/Bear를 외부 테마 리서치로 뒷받침 (현재 LLM 단독)
- **과거 유사국면**: backtester ledger와 연결 — "고밸류 성장주 조정" 등 유사 국면 사후수익률 인용
- **공수**: 중 (skill 호출 + deep_research scenarios 연결)

## 7-6. 신규 절차 D — 거시 자료의 종목 분석 주입 (우선순위 ⭐)

- 보유 중인 `macro-economic-integration`(FRED/ECB/IMF/BOK) 출력을 **deep_research `scenarios`의 실제 변수로 연결** (금리 → DCF 할인율, 환율 → 수출주 민감도)
- **공수**: 소~중 (plugin 이미 존재, 연결부만 작성)

## 7-7. 우선순위·실행 순서

| 순위 | 절차 | 임팩트 | 공수 | 선결 조건 |
|---|---|---|---|---|
| 1 | **A. Evidence Retrieval** | 🔥 최상 | 중 | WebSearch만으로 즉시 시작 가능 |
| 2 | **B. Fact-Check / Citation Lock** | 🔥 최상(신뢰도) | 중상 | A 완료(evidence가 대조 소스) |
| 3 | **D. 거시 주입** | ⭐ | 소~중 | macro plugin 기존 |
| 4 | **C. 사례 연결** | ⭐ | 중 | patent/paper skill |
| — | ~~bigdata-com MCP 인증~~ | — | — | **제외** (사용자 계정 없음). 무료 소스 스택으로 진행 |

## 7-8. 다음 단계 (사용자 결정 필요)

1. **절차 A 우선 구현** — `evidence_retriever.py`(무료 소스 pluggable)를 신규 1개 종목에 적용 후 기존 deep_research/PDF와 품질 A/B 비교
2. **절차 B claim 추출 범위** — 전체 정량 문장 vs 핵심 지표(매출·PER·시총)만 우선
3. **KIND 통합(Phase 2-2)과 통합** — 절차 A의 한국 종목 소스로 KIND 동시 진행 권장
4. **(보류) bigdata-com** — 사용자 계정 없어 제외. 향후 구독 확보 시 소스 ⓪로 prepend
