# Report Suite Plugin

블로거 글 1편 + 분석 시스템 결과를 입력받아 **3종 PDF 보고서**를 자동 생성:

| 보고서 | 페이지 | 대상 독자 | 핵심 내용 |
|---|---|---|---|
| **R1. Quant Anchor Report** | 10-15p | 정량 분석가 | Fundamentals + Technical + 거시 + 4-Analyst + Risk metrics |
| **R2. Persona Panel Report** | 15-20p | 투자 철학 비교 독자 | 13명 페르소나 5단계 + thesis × persona matrix + style-split |
| **R3. Executive Summary** | 5-8p | 의사결정자 | 메르 thesis + 정량 검증 + persona 합의 + trade decision + 한 페이지 결정 시트 |

3개 보고서가 **같은 데이터·결과**에서 다른 lens로 빌드됨. 사용자는 시간이 있으면 R1·R2·R3 모두 읽고, 시간이 없으면 R3만 봐도 결정 가능.

## Plugin 구조

```
plugins/report-suite/
├── plugin.json
├── README.md
├── skills/
│   ├── quant-anchor-report/      ← R1 builder
│   ├── persona-panel-report/     ← R2 builder
│   ├── executive-summary/         ← R3 builder
│   └── unified-builder/          ← 한 명령으로 3종 동시 생성
└── commands/
    └── report-suite.md
```

## 사용

```bash
# 한 번에 3개 보고서 모두 생성
python plugins/report-suite/skills/unified-builder/scripts/build_all.py \
    --thesis /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --persona-panel-dir /tmp/persona_panel \
    --risk-limits /tmp/risk_limits.json \
    --decisions /tmp/decisions.json \
    --portfolio /tmp/portfolio_history.json \
    --output-dir /tmp/reports

# → /tmp/reports/R1_quant.pdf, R2_personas.pdf, R3_executive.pdf
```

## 보고서 디자인 원칙

### R1. Quant Anchor Report
- **목적**: "데이터가 뭐라고 하는가?"
- **구조**:
  1. Cover (종목·날짜·핵심 메트릭 KPI)
  2. Fundamentals 섹션 (PE·PBR·ROE·FCF·부채)
  3. Technical 섹션 (이평·RSI·변동성·모멘텀)
  4. 거시 섹션 (KOSPI/SPY 동조성·환율·금리)
  5. 4-Analyst 평가 (Macro/Industry/Empirical/Counter — thesis별)
  6. Risk metrics (변동성-조정 한도·상관관계)
  7. 데이터 태깅 요약 (`[actual]` vs `[inference]` vs `[assumption]` 비율)

### R2. Persona Panel Report
- **목적**: "13명의 대가는 뭐라고 하는가?"
- **구조**:
  1. Cover (verdict 분포 차트)
  2. 13명 종합 표
  3. Style-split (가치파/성장파/매크로파/리스크파)
  4. **Thesis × Persona Matrix** (각 thesis에 대한 13명 stance — 핵심 추가)
  5. Universal concerns (다수 페르소나가 공통 우려)
  6. Unique alpha (1-2명만 본 인사이트)
  7. 페르소나별 상세 (5단계 분석 + narrative_vs_quant_resolution)

### R3. Executive Summary
- **목적**: "의사결정"
- **구조**:
  1. **한 페이지 결정 시트** (cover에 BUY/HOLD/SELL + qty + entry/exit)
  2. 메르 thesis 요약 (3-5 bullet)
  3. 정량 검증 결과 (사실 vs 가정 분리 표)
  4. Persona panel 합의도 (verdict 분포 + 이견 요약)
  5. Trade decision (risk-adjusted size)
  6. 핵심 위험 5개 (가장 먼저 무너질 가정)
  7. 다음 모니터링 포인트

---

## Phase 7 — Evidence Layer (외부 근거 강화 + 팩트체크)

> AMEET-style "외부 1차 자료 조회 → 교차검증 → 인용" 레이어. `_common/`에 2개 신규 모듈.
> 의존성 **stdlib-only**(`urllib`·`json`·`re`·`dataclasses`) → Cowork·Claude Code 양쪽 portable.

### `evidence_retriever.py` — 절차 A (Evidence Retrieval)

출처 URL이 박힌 외부 1차 자료를 수집·정규화하여 `evidence/{ticker}.json`으로 격리 저장.

```python
from evidence_retriever import EvidenceRetriever, WebSearchHit
er = EvidenceRetriever("BTU", exchange="NYSE", company="Peabody Energy")
er.add_websearch_hits([WebSearchHit(category="catalyst", claim="...", value="...",
                       source_url="https://...", publisher="EIA", date="2026-05-05", impact="-")])
er.fetch_sec_efts(forms=["8-K","10-Q"], lookback_days=400)   # 무료, 날짜필터·최신순
er.fetch_dart(lookback_days=365)                              # .KS/.KQ 종목만 (DART 재사용)
er.write(pipeline_dir / "evidence")                          # evidence/{ticker}.json
```

- **소스 우선순위(전부 무료)**: ① WebSearch hits(backbone) → ② SEC EDGAR EFTS → ③ DART → ④ news-integration
- **pluggable**: `register_source(fn)`로 향후 bigdata.com 등 소스 ⓪ prepend
- **build 연계**: `merge_into_deep()`(industry.news를 URL 인용 버전으로 prepend) · `annotate_scenarios()`(bull/base/bear 가정에 ✓출처/⚠반박 배지) · `audit_deep_research()`(무출처 비율 진단)

### `fact_checker.py` — 절차 B (Fact-Check / Citation Lock)

발행 전 thesis·정량주장을 evidence와 대조해 자동 플래그. 결과는 보고서 말미 **Citation Audit** 섹션.

```python
from fact_checker import FactChecker, render_citation_audit_html, make_codex_verifier
fc = FactChecker("BTU")
fc.register_verifier(make_codex_verifier())   # FACTCHECK_LLM=1 일 때만 codex 호출, 그 외 no-op
res = fc.run(deep, evidence)                   # 3종 체크 실행
html = render_citation_audit_html(res)
```

- **3종 체크**: ① thesis↔evidence 모순(stance-aware — 헤지 가정 제외) ② 무출처 정량주장 ③ 밸류에이션 정합성(시나리오 목표가 vs 애널 컨센서스)
- **등급**: 🔴 conflict(evidence가 반박) · 🟡 unsourced(대조 출처 부재) · 🟢 confirmed(뒷받침)
- **LLM plug**: `register_verifier()`로 codex-integration 연결(opt-in `FACTCHECK_LLM=1`)

### build_combined.py 배선 (자동)

`--deep-research` 지정 시 빌드가 자동으로: evidence 주입 → scenarios 근거태깅 → 팩트체크 → Citation Audit 섹션 렌더.
- `DISABLE_FACTCHECK=1` → 팩트체크/Audit 끔
- `FACTCHECK_LLM=1` → codex LLM 검증기 추가 동작 (codex CLI 또는 OPENAI_API_KEY 필요)

### BTU 검증 결과 (2026-06-02)

| 항목 | 결과 |
|---|---|
| evidence 수집 | 13건 (URL 100%), SEC 최신공시 2026-06-02 |
| deep_research 뉴스 | 5건(URL 0%) → 12건(URL 7) |
| scenarios 근거태깅 | 9건 (✓출처/⚠반박) |
| Citation Audit | 🔴4 🟡3 🟢1 — **EIA -9% 전망이 bull "AI=석탄수요" 논리 반박** 자동 탐지 |
