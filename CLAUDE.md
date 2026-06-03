# 주식 분석 시스템 — Claude Code 컨텍스트

> **Auto-loaded by Claude Code** when started in this directory. Provides project context, plugin registry, and frequently-used commands.



## ⚡ 에이전트 행동 원칙 (요약 — 새 세션 필독)

> 상세는 아래 본문 + `REPORT_FORMAT_STANDARD.md`. 이 블록은 "무엇을 절대 지킬지"의 요약이다.

**1. 작업 방식**

- 모든 분석은 `plugins/`(현재 16개) 안의 plugin·skill·command 호출로만 수행한다. one-off 스크립트 작성 금지.
- 새 분석은 `.analysis-log/{bloggers|standalone}/{date}_{slug}/`에 격리 저장하며 기존 결과를 덮어쓰지 않는다.

**2. 워크플로 라우팅 (요청 유형 → 진입점)**


| 요청 유형 / 트리거                        | 진입점                                           |
| ---------------------------------- | --------------------------------------------- |
| 네이버 블로그 URL · "블로그 분석" · "메르 글 분석" | `naver-blog-investment:analyze-blog` (8단계 자동) |
| 종목명만 (URL 없음) · "{종목} 분석 보고서"      | `/analyze-stock` 또는 report-suite 직접 빌드        |
| 한국 종목(.KS/.KQ) — 공시·재무             | `dart-integration` (DART 공시 + 5Y 재무)          |
| 미국 종목 — 공시·재무                      | `sec-edgar-integration` (10-K/10-Q/8-K)       |
| 미국 종목 — 뉴스                         | `news-integration` (NewsAPI + Finnhub)        |
| "적중률" · "백테스트" · alpha             | `backtester`                                  |
| "Bull/Bear 토론" · "debate"          | `subagent-orchestrator`                       |
| "포지션 한도" · "매수/매도 신호"              | `trade-engine` (risk / portfolio)             |
| Claude vs OpenAI/Gemini 교차검증       | `multi-model-arena` · `codex-integration`     |


**빌드 순서 (고정)**: ① `specialist-agents` 4종 선실행(research/sentiment/earnings/model) → ①b `evidence_retriever`로 `evidence/{ticker}.json` 수집(Phase 7, 권장) → ② `build_multi_stocks.py` (Layer1 종목별 combined PDF, **필수** — evidence 있으면 자동 주입+팩트체크 Citation Audit 렌더) → ③ `build_overview.py` (Layer2 MD/PDF/PPTX, 권장) → ④ `validate_format.py` (종료 시 **의무**, 28+ checks) → ⑤ 빌드 시 GitHub+Notion 자동 sync (`DISABLE_SYNC=1`로 끔). **Phase 7 env**: `DISABLE_FACTCHECK=1`(팩트체크 끔) · `FACTCHECK_LLM=1`(codex LLM 검증기 on).

**3. 보고서 형식 lock-in (사용자 confirm — 변경 금지)**

- ✅ 종목별 44~45p combined PDF = 표준. 단일 `report.pdf` 금지.
- ✅ 13명 풀 페르소나 + 4-Analyst. 5명 축약·7-Role 대체 금지.
- ✅ `stocks.json`의 `market_data`는 `market_fetcher.py` yfinance **live fetch** 의무 — LLM placeholder 절대 금지 (`fetched_via`에 `yfinance ... (live)` 확인).
- ✅ 섹션 흐름(v0.5.0): Cover → Company Intro → Deep Research → Financial Statements(US-GAAP 5Y+5Q) → News Timeline → Executive Brief → R1 → R2 → R3 → (선택) → Appendix.
- ❌ `analyses/` 디렉토리, Roman numeral 섹션 금지. canonical 참조: `.canonical-samples/`.

**4. 응답·콘텐츠 원칙**

- 한국어, 두괄식, 출처(yfinance/DART/SEC/뉴스 URL) 필수 병기. 사실 미확인 시 "확인 불가" 명시, 추측 금지.
- 새 종목 clean 분석: "fresh context, 이전 thesis·persona 참조 금지" 선언 후 시작.



## 🎯 프로젝트 개요

네이버 블로그 (메르·의교창·DaeGurr 등 8명) 또는 사용자 지정 종목에 대해 **multi-agent 투자 분석 시스템**을 운영한다. 13명 페르소나 패널 (Buffett·Munger·Lynch·Wood·Burry 등) + 4-Analyst (Macro/Industry/Empirical/Counter) + Risk Manager + Portfolio Manager + Backtester를 통합하여 **R1 (정량) + R2 (페르소나) + R3 (의사결정) + Deep Research**가 합쳐진 단일 PDF 보고서를 자동 생성한다.

## 📁 프로젝트 구조

```
.
├── plugins/                          # 10개 plugin (모두 자체 README + plugin.json)
│   ├── backtester/                   # 과거 verdict 적중률 + alpha 계산
│   ├── blogger-registry/             # 8명 블로거 메타데이터 + 라우팅
│   ├── dart-integration/             # ✨ 한국 DART 전자공시 자동 fetch
│   ├── sec-edgar-integration/        # ✨ 미국 SEC EDGAR 자동 fetch (Phase 2-2)
│   ├── news-integration/             # ✨ NewsAPI + Finnhub 자동 fetch (Phase 2-3)
│   ├── investor-personas/            # 13명 대가 페르소나 정의
│   ├── multi-model-arena/            # OpenAI gpt-5.5 + Gemini 3.1 + Claude 합의
│   ├── report-suite/                 # ⭐ R1+R2+R3+Deep Research 통합 보고서
│   ├── subagent-orchestrator/        # Bull-Bear-Skeptic debate cycle
│   └── trade-engine/                 # Risk · Portfolio · Paper Portfolio
├── .analysis-log/
│   ├── bloggers/{blogger}/{date}_{topic}/   # 블로거별 분석 결과 (영구 저장)
│   └── standalone/{date}_{ticker}_{name}/    # 사용자 지정 종목 (영구 저장)
├── .env                              # API keys (gitignored)
├── ENHANCEMENT_ROADMAP.md            # 향후 개선 계획
├── CLAUDE.md                         # 이 파일 (Claude Code 컨텍스트)
└── README.md                         # 사용자 셋업 가이드
```

## 🔑 환경변수 (.env)

```bash
# 필수 (현재 설정됨)
OPENAI_API_KEY=sk-proj-...           # gpt-5.5 (선택적 multi-model)
GOOGLE_API_KEY=AIzaSy...              # gemini-3.1 (선택적)
DART_API_KEY=fcda4b9b...              # 한국 전자공시 (한국 종목용)

# SEC EDGAR — 키 불필요 (User-Agent header만 필요, 기본값 작동)
# SEC_USER_AGENT=YourName/1.0 (your-email@example.com)

# 권장 — 미국 종목 뉴스 (둘 다 무료 freemium)
NEWSAPI_KEY=                          # https://newsapi.org/register
FINNHUB_KEY=                          # https://finnhub.io/register
```

## 🚀 핵심 워크플로

### 1. 새 블로그 글 분석 → 통합 보고서

```bash
# Skill: naver-blog-investment:analyze-blog
# Trigger: "https://blog.naver.com/{user}/{logNo} 분석해줘"
```

### 2. 사용자 지정 종목 standalone 분석

```bash
# Skill: report-suite (직접 빌드)
# Trigger: "{종목명} 분석 보고서 만들어줘" (예: "Peabody Energy 분석")
```

### 3. PDF 통합 보고서 생성 (top N 종목)

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{date}_{slug} \
  --output-dir .analysis-log/.../reports/combined \
  --top-n 5
```

### 4. DART 공시 fetch (한국 종목)

```bash
python3 plugins/dart-integration/scripts/dart_client.py 005490.KS
```

## 🧩 자주 쓰는 Skills (전체 31개)


| Skill                                        | 트리거 키워드                               |
| -------------------------------------------- | ------------------------------------- |
| `naver-blog-investment:analyze-blog`         | "블로그 분석", "메르 글 분석"                   |
| `dart-integration:dart-disclosure-fetch`     | "DART 공시", "전자공시", "사업보고서"            |
| `dart-integration:dart-financial-fetch`      | "DART 재무", "5년 손익"                    |
| `sec-edgar-integration:sec-disclosure-fetch` | "SEC 공시", "10-K", "EDGAR filings"     |
| `sec-edgar-integration:sec-financial-fetch`  | "SEC 재무", "10-K 재무제표", "5년 손익 미국"     |
| `news-integration:news-fetcher`              | "뉴스 fetch", "company news"            |
| `report-suite:unified-builder`               | "통합 보고서", "PDF 생성"                    |
| `subagent-orchestrator:debate-orchestrator`  | "Bull/Bear debate", "subagent debate" |
| `backtester:hit-rate-analyzer`               | "적중률", "백테스트"                         |
| `trade-engine:risk-manager`                  | "포지션 한도", "변동성 조정"                    |
| `trade-engine:portfolio-manager`             | "신호 점수", "매수/매도 결정"                   |


## 📊 분석 결과 위치 (영구 저장)

각 분석은 **독립된 디렉토리에 격리** — 새 분석이 이전 결과를 덮어쓰지 않음:

```
.analysis-log/
├── bloggers/
│   ├── doctordk/2026-04-29_lithium/   # 의교창 리튬 (POSCO·삼성SDI·ALB·SQM·LIT)
│   ├── infidoc/2026-04-06_PRTA/       # 인피의 PRTA (13명 페르소나)
│   ├── daegurrr_/2026-03-01_tanker/   # DaeGurr 탱커 (5종목)
│   └── ranto28/...                     # 메르 (5건 backtest)
└── standalone/
    └── 2026-04-30_BTU_Peabody_Energy/ # Peabody Energy
```

각 분석 디렉토리 내부:

```
{date}_{slug}/
├── meta.json                # 제목·날짜·블로그 URL
├── thesis_list.json         # 추출된 6-12개 thesis
├── thesis_eval/             # 4-Analyst 평가 결과
├── stocks.json              # 식별된 종목 + market data
├── persona_panel/{ticker}/  # 종목별 13명 페르소나 verdict
├── risk_limits.json         # Risk Manager 포지션 한도
├── decisions.json           # Portfolio Manager 액션
├── portfolio.json           # Paper portfolio 상태
├── deep_research/{ticker}.json  # 산업·재무·시나리오 등
└── reports/                 # 최종 PDF 보고서
```

## ⚠️ 새 분석 시작 시 주의

같은 대화 세션에서 새 종목 분석 시 **LLM 추론 컨텍스트가 일부 영향**받을 수 있음. 다음 중 하나 선택:

1. **새 대화 세션 시작** (가장 깨끗) — 이전 분석 데이터는 모두 디스크에 보존됨
2. **명시적 reset 요청**: "fresh context로 새 분석 시작. 이전 thesis·persona 패턴 참조 금지."
3. **같은 산업 시리즈는 OK** — 의도적으로 컨텍스트 공유가 효율 (예: 리튬 sector 5종목)

## 🛠️ 자주 발생하는 작업

### PDF 한글 깨짐 발생 시

이미 해결됨 — `pdftocairo` 후처리로 모든 PDF 뷰어에서 정상 표시. 만약 깨짐 재발 시:

- Noto Sans KR 폰트 설치 확인: `fc-list | grep -i noto.*kr`
- pdftocairo 설치 확인: `which pdftocairo`

### 새 종목을 ticker_resolver에 추가

`plugins/report-suite/skills/_common/ticker_resolver.py`의 `CURATED` dict에 추가:

```python
"BTU": {"kr": "Peabody Energy", "en": "Peabody Energy Corporation", "sector": "Coal Mining"},
```

### DART API 활성화 확인

```bash
python3 -c "
import sys; sys.path.insert(0, 'plugins/dart-integration/scripts')
from dart_client import get_status; print(get_status())
"
```

## 🎓 페르소나 13명 가중치 (한국 시장 calibration)

```python
# plugins/investor-personas/personas/_weights.json
{
    "stanley-druckenmiller": 1.5,   # macro tailwind 강조
    "peter-lynch": 1.3,              # PEG 직관
    "michael-burry": 1.2,            # contrarian deep value
    "warren-buffett": 0.7,           # quality 우선 (한국 deep value 환경 부적합)
    "cathie-wood": 0.9,              # disruption thesis
}
```

## 📚 추가 문서

- `README.md` — 5분 셋업 가이드
- `ENHANCEMENT_ROADMAP.md` — Phase 1-6 향후 계획
- `**REPORT_FORMAT_STANDARD.md` — 보고서 형식 표준 (필수 참조)**
- 각 `plugins/*/README.md` — plugin별 상세 사용법
- 각 `plugins/*/skills/*/SKILL.md` — skill 트리거 키워드 + 사용법

## 🔄 GitHub + Notion 자동 sync (v0.5.0+)

분석 완료 시 `build_combined.py`가 자동으로 다음 위치에 동기화합니다:

- **Notion DB**: [📊 주식 분석 Hub](https://www.notion.so/b689c03e9bc6481b8c732ca17729f8db) — Cowork/Claude Code MCP 자동
- **GitHub repo**: private repo (사용자가 GITHUB_TOKEN 발급 후 자동 생성)

### 셋업 (1회)

```bash
# 1. GitHub PAT 발급 — https://github.com/settings/tokens?type=beta
# 2. .env에 추가:
GITHUB_TOKEN=github_pat_...   # 사용자가 발급
GITHUB_OWNER=DrugnSafety      # (이미 .env에 설정됨)
GITHUB_REPO=stock-analysis    # 첫 sync 시 자동 생성 (이미 .env에 설정됨)

# 3. NOTION_DATA_SOURCE_ID는 이미 .env에 설정됨
```

### 자동 sync (PDF 빌드 시)

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py ... --output combined.pdf
# [combined] saved: combined.pdf
# [sync] post-build hook → GitHub + Notion (자동 실행)
```

비활성화: `DISABLE_SYNC=1 python3 build_combined.py ...`

### 수동 sync (백필 등)

```
/sync-github-notion .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy LNG
```

자세한 가이드: `plugins/github-notion-sync/README.md`

---

## 🚀 v0.8.0 고도화 (2026-06-02 적용 완료) — Phase 7 Evidence Layer (외부 근거 + 팩트체크)

AMEET-style "외부 1차 자료 조회 → 교차검증 → 인용" 레이어. 기존 deep_research가 LLM 추론으로 채우던 산업·경쟁·카탈리스트를 **출처 URL 박힌 외부 근거**로 대체/보강.

### 신규 모듈 (`report-suite/skills/_common/`, stdlib-only → Cowork·Claude Code portable)

1. **`evidence_retriever.py`** — 절차 A
   - `EvidenceRetriever(ticker).add_websearch_hits([...])` + `.fetch_sec_efts()` + `.fetch_dart()` → `.write(pdir/"evidence")`
   - 소스 우선순위(무료): WebSearch → SEC EFTS(날짜필터) → DART(.KS/.KQ) → news-integration
   - `register_source()` pluggable(bigdata.com 향후) · `merge_into_deep()`(news에 URL prepend) · `annotate_scenarios()`(가정에 ✓출처/⚠반박 배지) · `audit_deep_research()`(무출처 진단)
2. **`fact_checker.py`** — 절차 B
   - `FactChecker(ticker).run(deep, evidence)` → 🔴conflict/🟡unsourced/🟢confirmed
   - 3종: thesis↔evidence 모순(stance-aware) · 무출처 정량 · 밸류 정합성(시나리오 vs 애널 컨센서스)
   - `make_codex_verifier()` → `register_verifier`로 codex LLM plug (opt-in `FACTCHECK_LLM=1`)
   - `render_citation_audit_html()` → 보고서 말미 Citation Audit 섹션

### 빌드 자동 배선 (`build_combined.py`)

`--deep-research` 지정 시 자동: evidence 주입 → scenarios 근거태깅 → 팩트체크 → Citation Audit 렌더. `DISABLE_FACTCHECK=1`로 끔.

### 수동 evidence 수집 예 (빌드 전)

```bash
PDIR=.analysis-log/standalone/{date}_{ticker}_{name}
python3 -c "
import sys; sys.path.insert(0,'plugins/report-suite/skills/_common')
from evidence_retriever import EvidenceRetriever, WebSearchHit
er = EvidenceRetriever('BTU', exchange='NYSE', company='Peabody Energy')
# WebSearch 결과를 agent가 WebSearchHit 으로 주입 (category/claim/value/source_url/publisher/date/impact)
er.fetch_sec_efts(forms=['8-K','10-Q'], lookback_days=400)
er.fetch_dart()  # .KS/.KQ 만
er.write('$PDIR/evidence')
"
```

### 검증 (BTU, 2026-06-02)

뉴스 5건(URL 0%)→12건(URL 7) · scenarios 9건 태깅 · Citation Audit가 **EIA -9% 전망이 bull "AI=석탄수요" 논리 반박** 자동 탐지(🔴4/🟡3/🟢1). ⚠️ weasyprint PDF 최종 rasterize·DART corp_code 예열은 Cowork sandbox 제약 → **Claude Code(로컬 macOS)에서 제약 없이 실행**. 상세: `ENHANCEMENT_ROADMAP.md` Phase 7.

---

## 🚀 v0.7.0 고도화 (2026-05-20 적용 완료) — LangSmith + Codex + Claude Code 호환

### 신규 통합

1. **LangSmith Tracing** (`plugins/specialist-agents/scripts/langsmith_wrapper.py`)
  - `@traced_call` decorator로 모든 LLM call 자동 추적
  - 미설치/미설정 시 graceful no-op (overhead 0)
  - env 설정: `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT=stock-analysis`
  - Dashboard: [https://smith.langchain.com](https://smith.langchain.com) → stock-analysis project
2. **codex-integration plugin** (`plugins/codex-integration/`)
  - OpenAI Codex CLI subprocess 호출 (Claude Code 환경) 또는 OpenAI API 직접 호출 (Cowork)
  - 2개 skill: codex-thesis-validator (Claude vs OpenAI cross-validation), codex-code-reviewer
  - 환경 자동 감지 (`shutil.which("codex")` → CLI / OPENAI_API_KEY → API / none → error)
3. **Claude Code 호환** (`CLAUDE_CODE_QUICKSTART.md`)
  - macOS Terminal에서 `claude` 실행으로 동일 분석 가능
  - Office-Home 동기화는 GitHub repo (.env는 별도 보관)
  - 5분 셋업 가이드 + Cowork와 환경 비교 표

### 통합 사용 예시 (Claude Code 환경)

```bash
cd ~/stock-analysis  # GitHub clone
claude                # Claude Code 시작
# Claude Code 내부에서:
> /analyze-blog https://blog.naver.com/ranto28/...
> # 자동으로 specialist-agents → codex cross-validation → LangSmith trace → PDF 빌드
```

---

## 🚀 v0.6.0 고도화 (2026-05-20 적용 완료) — Tier 2 Specialist Agents

### specialist-agents plugin 신설

`plugins/specialist-agents/` — Anthropic Financial Services Agents 2026-05 + TradingAgents 0.2.4 + LangAlpha 패턴 차용한 신규 plugin.

**4가지 specialist agent skill**:


| Agent                | 출력                                     | 핵심 기능                          |
| -------------------- | -------------------------------------- | ------------------------------ |
| 🧭 Research Manager  | `research_intel/{ticker}_sector.json`  | sector·issuer 동향 종합            |
| 💭 Sentiment Analyst | `sentiment/{ticker}_score.json`        | news impact -1.0~+1.0 정량화      |
| 📊 Earnings Reviewer | `earnings_review/{ticker}_latest.json` | YoY·margin·thesis impact 자동 추출 |
| 📐 Model Builder     | `models/{ticker}_dcf.json`             | DCF + Reverse-DCF + L/S signal |


### Infrastructure 모듈

- `plugins/specialist-agents/scripts/checkpoint_manager.py` — 10-stage 진행 상태 영구 저장 (Cowork 45s timeout 안전)
- `plugins/specialist-agents/scripts/provider_router.py` — Multi-LLM 3-tier 비용 라우팅 (83% 절감)

### Plugin 안정성 패치 (5건)

1. `build_r1.py` — `t.get("claim_id") or t.get("id")` fallback
2. `build_r2.py` — `claim_id`/`thesis_id` + `rebut`/`challenge` stance 자동 정규화 + stage_results legacy schema fallback
3. `deep_research.py` — peer_compare `_fmt()` defensive (None/string) + pl_5y OPM/NPM fallback chain + **5Y trend narrative (CAGR · OPM trajectory · turnaround signal)**
4. `company_intro.py` — yfinance longBusinessSummary 자동 fetch + 7일 캐시 + **BUSINESS_SUMMARY_KO** 한글 번역본 + 네이버/DART/FnGuide 직링크
5. `news_disclosures.py` — 5종목 curated NEWS_TIMELINE entry 25건 추가

### 빌드 명령 (v0.6.0 신규)

```bash
# Specialist agents 사전 실행 (build_combined.py 호출 전)
PDIR=.analysis-log/bloggers/{blogger}/{date}_{slug}
python3 plugins/specialist-agents/skills/research-manager/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2 ...
python3 plugins/specialist-agents/skills/sentiment-analyst/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2 ...
python3 plugins/specialist-agents/skills/earnings-reviewer/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2 ...
python3 plugins/specialist-agents/skills/model-builder/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2 ...

# 그 다음 build_multi_stocks.py 평소대로 실행 → specialist section 자동 통합
```

### Checkpoint 사용법

```bash
python3 plugins/specialist-agents/scripts/checkpoint_manager.py $PDIR --status
python3 plugins/specialist-agents/scripts/checkpoint_manager.py $PDIR --reset-from build_pdf  # PDF 단계부터 재실행
```

---

## 🚀 v0.5.0 고도화 (2026-05-11 적용 완료)

다음 4가지 고도화가 보고서 표준에 통합되었습니다:

1. `**/finance:financial-statements` 의무 활용** (모든 plugin agent)
  - 모듈: `plugins/report-suite/skills/_common/financial_statements_us_gaap.py`
  - 5년 annual + 5분기 quarterly 재무 분석 (US GAAP / ASC 220, 210, 230)
  - SEC EDGAR (미국) + DART (한국 K-IFRS → US GAAP equivalent mapping)
  - Material Variance Summary 자동 생성 (임계값: > $1B = $50M/5%, $100M-$1B = $25M/10%, < $100M = $5M/15%)
  - **모든 페르소나 평가 시 이 출력을 anchor로 사용 의무**
2. **Thesis × Persona Matrix 정상화** (build_r2.py, persona-evaluator/SKILL.md)
  - `thesis_lens_applications` 필드 강제 출력 (persona-evaluator)
  - 데이터 부재 시 silent skip 금지 → 명시적 진단 메시지 표시 (build_r2.py)
3. **News Timeline 개선** (news_disclosures.py)
  - 중립(○) 제외 옵션 (`filter_neutral=True`)
  - 긍정/부정 상세 요약 (`expand_summary=True`, `impact_reason` 필드 활용)
  - 종목별 월별 +/- bar chart (`with_monthly_chart=True`, base64 PNG 임베드)
4. **Deep Research 위치 승격** (build_combined.py)
  - Section 8 → Section 3 (Cover → Company Intro → **Deep Research** → Financial Statements → ...)
  - 산업·재무·카탈리스트·리스크를 페이지 도입부에 통합

### 새 섹션 흐름 (v0.5.0 적용 후)

```
1. Cover
2. Company Intro
3. Deep Research (산업 + 재무 + 카탈리스트/리스크)        ← 승격
4. Financial Statements US-GAAP (5Y annual + 5Q quarterly)  ← NEW (필수)
5. News Timeline (중립 제외 + 월별 +/- bar chart)
6. Executive Brief + Thesis List
7. R1 Quant Anchor
8. R2 Persona Panel (Thesis × Persona Matrix 정상화)
9. R3 Decision Section
10. (선택) ETF Holdings, Reverse DCF, Subagent Debate
11. Appendix
```

### docx 생성 시 한글 폰트 표준

- python-docx에서 `Malgun Gothic` (Windows 전용) 사용 금지
- macOS Word 호환 cascade: `w:eastAsia` = `Apple SD Gothic Neo`, `w:ascii`/`w:hAnsi` = `Helvetica Neue`
- OXML rFonts 직접 설정 필수 (font.name만으로는 한글 미적용)

```python
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_font(run, size=11, bold=False, color=None):
    run.font.name = 'Helvetica Neue'
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts')
        rPr.append(rFonts)
    rFonts.set(qn('w:ascii'), 'Helvetica Neue')
    rFonts.set(qn('w:hAnsi'), 'Helvetica Neue')
    rFonts.set(qn('w:eastAsia'), 'Apple SD Gothic Neo')
    rFonts.set(qn('w:cs'), 'Apple SD Gothic Neo')
```

---

## 🔒🔒🔒 보고서 형식 표준 (사용자 confirm 완료 — 절대 변경 금지)

> **사용자가 2026-05-01에 canonical format을 명시적으로 confirm했습니다. 새 세션에서 임의로 다른 형식을 만들면 안 됩니다.**
> **2026-05-11 v0.5.0 고도화 적용** — 위의 새 섹션 흐름이 우선합니다.

### Canonical Reference (md5 검증된 샘플)

- 위치: `.canonical-samples/ranto28_2026-04-21_ECM_skinbooster/`
- 5개 PDF (44-45p 각, 441-453KB), `overview.{md,pdf,pptx}` 포함
- 사용자 업로드 PDF와 시스템 생성 PDF가 byte-for-byte 동일 (md5 일치)

### 새 분석 시작 시 의무 절차

1. `CLAUDE.md` 읽기 (이 문서) — 자동 로드됨
2. `REPORT_FORMAT_STANDARD.md` 참조 — 디렉토리·파일 schema
3. `.canonical-samples/` 샘플 디렉토리 구조 확인
4. **8단계 파이프라인 실행** (수집 → thesis → 종목 → 4-Analyst → market data → 13 페르소나 → risk + portfolio → deep research)
5. **Layer 1 빌드 (필수)**: `build_multi_stocks.py`로 per-stock combined PDF 5개
6. **Layer 2 빌드 (권장)**: `build_overview.py`로 MD + PDF + PPTX 3종
7. **검증 (의무)**: `validate_format.py` 실행 → 28+ checks 모두 통과 확인

### ❌ DO NOT (절대 금지)

- ❌ `analyses/` 디렉토리 사용 (잘못된 패턴)
- ❌ 단일 `report.pdf` 출력 (per-stock PDF가 표준)
- ❌ 7-Role 분석으로 대체 (13명 페르소나 + 4-Analyst가 표준)
- ❌ Roman numeral 섹션 (Korean 헤더 통일)
- ❌ One-off scripts 작성 (plugin 호출만 사용)
- ❌ Layer 1 누락 또는 단축 형태 PDF
- ❌ 페르소나 panel 5명만 (13명 풀 패널 필수)
- ❌ **stocks.json의 market_data를 LLM이 placeholder로 채움 — 반드시 yfinance live fetch 사용**

### 🚨 CRITICAL — 시장 데이터 fetch 의무

`**stocks.json`의 `market_data` 필드는 절대 LLM이 채우면 안 됨.** 반드시 `market_fetcher.py`로 실제 yfinance 호출:

```bash
# 분석 시작 시 stocks.json 자동 생성
python3 -c "
import sys
sys.path.insert(0, 'plugins/report-suite/skills/_common')
from market_fetcher import build_stocks_json
from pathlib import Path

build_stocks_json(
    tickers=['000660.KS', '005930.KS', ...],  # ← top 5 tickers
    output_path=Path('.analysis-log/.../stocks.json'),
    thesis_alignments={'000660.KS': 'very_high', ...}  # ← 선택
)
"

# 또는 기존 분석 마이그레이션 (LLM placeholder → live)
python3 plugins/report-suite/skills/unified-builder/scripts/migrate_stocks_to_live.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug}
```

검증: `market_data.fetched_via` 필드에 `yfinance X.X.X (live)` 문자열 필수.

### ✅ MUST 빌드 명령

```bash
# Layer 1 — per-stock combined PDFs (필수)
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
  --output-dir .analysis-log/.../reports/combined --top-n 5

# Layer 2 — multi-format overview (권장)
python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
  --output-dir .analysis-log/.../reports/overview --formats md pdf pptx

# 검증 — 모든 분석 종료 시 실행 의무
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py \
  .analysis-log/bloggers/{blogger}/{slug}
```

---

## 보고서 형식 표준 (Lock-in)

**모든 새 분석은 다음 형식을 반드시 따라야 함**:

### 디렉토리 구조 (필수)

```
.analysis-log/bloggers/{blogger}/{date}_{slug}/
├── meta.json
├── thesis_list.json
├── thesis_eval/all_aggregate.json
├── stocks.json
├── persona_panel/{ticker}/aggregate.json + 13개 persona JSON
├── persona_panel/_all_aggregates.json
├── deep_research/{ticker}.json
├── risk_limits.json
├── decisions.json
├── portfolio.json
└── reports/
    ├── combined/         # Layer 1 — per-stock 44p PDFs (필수)
    │   └── {idx}_{ticker}_{name}_combined.pdf
    └── overview/         # Layer 2 — multi-format summary (권장)
        ├── overview.md
        ├── overview.pdf
        └── overview.pptx
```

### Few-shot 참조 샘플 (canonical format)

- **의교창 lithium**: `.analysis-log/bloggers/doctordk/2026-04-29_lithium/`
- **메르 ECM**: `.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/`

### 빌드 명령

```bash
# Layer 1 (per-stock) — 필수
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
  --output-dir .../reports/combined --top-n 5

# Layer 2 (overview MD/PDF/PPT) — 권장
python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
  --output-dir .../reports/overview --formats md pdf pptx
```

**자세한 표준은 `REPORT_FORMAT_STANDARD.md` 참조.**

## 🔗 외부 자료

- DART OpenAPI: [https://opendart.fss.or.kr](https://opendart.fss.or.kr) (한국 종목 공시)
- SEC EDGAR: [https://www.sec.gov/edgar/sec-api-documentation](https://www.sec.gov/edgar/sec-api-documentation) (미국 종목 — 향후 통합)
- yfinance docs: [https://pypi.org/project/yfinance/](https://pypi.org/project/yfinance/) (가격·재무)
- Naver 블로그 API: PostTitleListAsync.naver (블로그 글 list)


---

## 🚀 v0.9.x 고도화 (2026-06-02 적용 완료) — Sprint E+F: PDF 결함 14건 일괄 패치

삼성전자 005930.KS 90페이지 검증 과정에서 발견된 데이터 누락·렌더링 오류·UX 결함 14건을 일괄 패치. 자세한 내용은 `CHANGELOG.md` 참조.

### 핵심 변경 (v0.9.0 — 12건)

| Sprint | 패치 위치 | 효과 |
|---|---|---|
| E-1 | `aggregate_panel.py` | persona 17명 aggregate 누락 — `aggregate.json` + `_all_aggregates.json` 자동 생성. Dalio·Soros·Simons·Asness 4명 추가 |
| E-2 | `deep_research.py` + `build_combined.py` | thesis_decomposition × 4-Analyst overlay (claim_id + claim_text fuzzy 매칭) |
| E-3 | `thesis_eval_normalizer.py` | `supporting_data`·`counter_evidence`·`key_assumption` 보존. data tagging keyword 33종 확장 |
| E-4·5 | `company_intro.py` · `deep_research.py` | paragraph → bullet 자동 변환 (한글 문장 끝 split) |
| E-6 | `translate_thesis_eval.py` (utility) | 영어 rationale → 한글 (gpt-4o-mini batch, ~$0.01/run) |
| E-7 | `macro_renderer.py` | OECD 57개국 raw → 1줄 summary 기본. `OECD_FULL_TABLE=1`로 강제 |
| E-8 | `news_disclosures.py` | Samsung NEWS_TIMELINE 24건 (13개월 분포) |
| E-9 | `guru_checklist.py` | `_extract_persona_evidence()` — 페르소나 본문 4 sources fuzzy match |
| E-10 | `build_r2.py` | thesis × persona matrix 거짓 "neutral" 진단 수정. 미평가 cell 명시 |
| F-1 | `guru_checklist.py` | qualitative 항목도 페르소나 evidence 추출 |
| F-2 | `deep_research.py` | 4-Analyst rationale → bullet + 음슴체 (격식체 0건) |

### v0.9.1 신규 — Sprint F-3: Checklist LLM 정성 평가

`guru_checklist.py`에 `_llm_qualitative_assessment()` 신설 — evidence·heuristic 모두 실패 시 gpt-4o-mini가 종목 데이터 + 페르소나 철학 종합하여 정성 평가.

```python
# 호출 순서 (qualitative + heuristic 양쪽 fallback)
1. 정량 metric 매핑 → 직접 계산
2. 페르소나 본문 evidence 추출 (E-9·F-1)
3. ★ NEW F-3: LLM 정성 평가
4. 최종 heuristic fallback (verdict-based)
```

**비용**: 1 ticker × 17 personas × ~3 qualitative items/persona ≈ 50건/run → **~$0.005/build**.
**캐시**: `.cache/checklist_llm/{ticker}.json` — `{persona_id}::{criterion}` 키. 영구 캐시.
**비활성화**: `DISABLE_LLM_CHECKLIST=1`

### 신규 환경변수 (v0.9.x)

```bash
# Sprint E+F 옵션 (모두 default OFF/ON 자동)
OECD_FULL_TABLE=1            # OECD 57개국 raw table 강제 (default: 1줄 summary)
DISABLE_LLM_CHECKLIST=1      # Checklist LLM 평가 비활성화 (default: enabled)
# 기존 v0.8.0 env (재명시)
DISABLE_FACTCHECK=1          # Citation Audit 비활성화
FACTCHECK_LLM=1              # codex LLM fact-checker 활성화
DISABLE_SYNC=1               # GitHub+Notion auto-sync 비활성화
```

### 표준 어조 (Sprint F-2 lock-in)

- 4-Analyst rationale + Checklist LLM 평가는 **bullet point + 한국어 음슴체** 사용 의무.
- 격식체 ("~합니다/입니다/됩니다/습니다") → 음슴체 ("~함/임/됨/음") 자동 변환 (`_to_eumsumche()` 3-pass).
- 영어 rationale 잔존 시 `translate_thesis_eval.py` 1회 실행 (~$0.01).

### Checklist 5-column layout (Sprint Fix-C → v0.9.x 확장)

```
| # | 판단 항목 (Criterion) | 결과 | 설명 (검증 결과) | 학습 가이드 (의미·해석법) |
| 5%| 25%                   | 7%   | 33%              | 30%                        |
```

- 결과: `[O]` 충족 · `[X]` 미달 · `[?]` 판단보류
- 설명 (검증 결과) 우선순위:
  1. **실데이터 검증**: 충족 evidence + metric 값 + 기준
  2. **페르소나 evidence**: `[Stage: ...]` `[Quant Anchor]` 등 source 태그 + 본문 직접 인용
  3. **AI 정성 평가**: gpt-4o-mini bullet 3개 + "※ gpt-4o-mini 추정 — 페르소나 본문 직접 근거 아님. 참고용." disclaimer
  4. **Heuristic fallback**: verdict-based 추정 (최종 fallback)

### Persona Panel aggregate 신규 절차 (E-1)

```bash
# persona individual JSON 17개 → aggregate.json + _all_aggregates.json
python3 plugins/investor-personas/skills/persona-panel/scripts/aggregate_panel.py \
  .analysis-log/standalone/{date}_{ticker}_{name}/persona_panel/{ticker} \
  --output .analysis-log/.../persona_panel/{ticker}/aggregate.json
```

→ build_combined.py가 `--persona-aggregate aggregate.json` + `--persona-aggregates-all _all_aggregates.json` 양쪽 요구. run_panel.py 실행 후 반드시 aggregate_panel.py 실행 의무.

