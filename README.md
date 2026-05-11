# 주식 분석 시스템 (Naver Blogger Multi-Agent Investment Analysis)

> 네이버 블로그 (메르·의교창·DaeGurr 등 8명) 또는 사용자 지정 종목에 대해 **13명 페르소나 패널 + 4-Analyst + Risk·Portfolio Manager + Backtester** 통합 분석을 수행하고 **Deep Research 형식의 단일 통합 PDF 보고서**를 자동 생성합니다.

**현재 버전**: v0.5.0 (2026-05-11)

---

## ✨ 주요 기능

### 코어 분석
- **다중 종목 분석**: Top 3-5 종목 동시 보고서 생성 (각 60-69 페이지)
- **13명 legendary 투자자 패널**: Buffett·Munger·Lynch·Wood·Burry·Taleb·Graham·Ackman·Pabrai·Fisher·Jhunjhunwala·Druckenmiller·Damodaran
- **4-Analyst 평가**: Macro / Industry / Empirical / Counter-thesis
- **Multi-model arena**: Claude + OpenAI gpt-5.5 + Gemini 3.1
- **Backtester**: 과거 verdict 적중률 + KOSPI/SPY 대비 alpha

### v0.5.0 신규 기능
- **5년 + 5분기 US-GAAP 재무제표 자동 분석** (`financial_statements_us_gaap.py`):
  - SEC EDGAR (미국) + DART (한국 K-IFRS → US GAAP equivalent) 통합 fetch
  - ASC 220 / 210 / 230 (US GAAP) 형식 Income Statement / Balance Sheet / Cash Flow
  - Material Variance Summary 자동 생성 (임계값 기반 플래깅)
- **Implicit Thesis 자동 추출** (`implicit_thesis_extractor.py`):
  - 블로그 글 없이 ticker만으로 분석할 때 자동으로 thesis 보강
  - catalysts → predictive thesis, risks → conditional thesis, financial trends → factual thesis
  - standalone 분석에서도 Thesis × Persona Matrix가 의미있게 작동
- **News Timeline 개선** (`news_disclosures.py`):
  - 중립(○) 항목 자동 제외 (KPI에는 카운트 유지)
  - 상세 요약 expansion (`expand_summary=True`)
  - 종목별 월별 +/- bar chart (matplotlib base64 PNG 임베드)
- **NewsAPI.ai (Event Registry) 통합**: UUID 키 형식, 1-year lookback (NewsAPI.org 30일 cap 보완)
- **Thesis × Persona Matrix 정상화**: silent skip 제거 + 진단 fallback 메시지
- **새 보고서 섹션 흐름**: Deep Research를 페이지 도입부(Section 3)로 승격

### 데이터 표준
- **DART 통합**: 한국 종목 공시·재무제표 자동 fetch
- **SEC EDGAR 통합**: 미국 종목 10-K/10-Q XBRL 데이터 자동 fetch
- **한글 PDF 호환**: `pdftocairo` 후처리로 모든 PDF 뷰어에서 정상 표시
- **한글 docx 폰트 표준**: Apple SD Gothic Neo (macOS) — Malgun Gothic (Windows-only) 금지

---

## 🚀 5분 셋업

### 1. 시스템 의존성

```bash
# Python packages
pip install --break-system-packages weasyprint matplotlib yfinance pypdf requests \
    openai google-generativeai python-docx

# 한글 폰트 (Linux/Cowork sandbox는 chart_utils.py가 자동 bootstrap)
mkdir -p ~/.fonts
# Google Fonts에서 Noto Sans KR Regular + Bold 다운로드 후 ~/.fonts/ 에 배치
fc-cache -fv

# PDF 후처리 도구 (CJK 호환성 핵심)
brew install poppler        # macOS
# 또는 sudo apt-get install poppler-utils  # Ubuntu/Debian
```

### 2. API 키 설정

`.env` 파일 (`.gitignore` 처리됨):

```bash
# Multi-model arena (선택 — 페르소나 평가 LLM 호출 시 필요)
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5.5
GOOGLE_API_KEY=AIzaSy...
GOOGLE_MODEL=gemini-3.1

# 한국 종목 분석 (무료, 일일 10,000 calls)
# https://opendart.fss.or.kr 가입 후 인증키 발급
DART_API_KEY=fcda...

# 미국 종목 뉴스 (3-source — 모두 freemium)
NEWSAPI_KEY=...           # NewsAPI.org (32-char hex, 30일 lookback)
NEWSAPI_AI_KEY=...        # NewsAPI.ai/Event Registry (UUID, 1년 lookback)
FINNHUB_KEY=...           # Finnhub (60 calls/min)

# SEC EDGAR — 키 불필요 (User-Agent header만)
```

### 3. 셋업 점검

```
/setup
```

---

## 📖 사용법

### 슬래시 명령어 (Cowork & Claude Code 동일 작동)

| 명령어 | 용도 |
|---|---|
| `/setup` | 시스템 셋업 점검 |
| `/dart-status` | DART API 활성 상태 + 캐시 점검 |
| `/sec-status` | SEC EDGAR + NewsAPI/Finnhub/NewsAPI.ai 통합 상태 |
| `/analyze-blog <URL>` | 네이버 블로그 → Top 5 종목 통합 보고서 |
| `/analyze-stock <ticker>` | 종목 standalone 분석 (implicit thesis 자동 적용) |
| `/list-analyses` | 모든 기존 분석 리스트 |
| `/validate-analysis <dir>` | 분석 디렉토리가 표준 schema 준수하는지 검증 |

### 직접 호출 (CLI — Claude Code 환경)

```bash
# 단일 종목 통합 PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker LNG \
  --meta meta.json --stocks stocks.json \
  --thesis thesis_list.json --eval-dir thesis_eval/ \
  --persona-aggregate persona_panel/LNG/aggregate.json \
  --persona-full persona_panel/LNG/ \
  --risk-limits risk_limits.json --decisions decisions.json \
  --portfolio portfolio.json --deep-research deep_research/LNG.json \
  --output combined.pdf

# Top N 종목 일괄
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/doctordk/2026-04-29_lithium \
  --output-dir reports/combined --top-n 5

# 5년 + 5분기 US GAAP 재무 분석 단독 호출 (v0.5)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py BTU \
  --output /tmp/btu_fs.json

# Implicit thesis 추출 단독 호출 (v0.5)
python3 plugins/report-suite/skills/_common/implicit_thesis_extractor.py LNG \
  --company "Cheniere Energy" --sector "LNG Export Operator" \
  --deep-research deep_research/LNG.json \
  --output thesis_list.json

# 분석별 README.md 자동 생성
python3 plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py \
  --pipeline-dir .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy \
  --output README.md

# DART 공시 직접 fetch (한국)
python3 plugins/dart-integration/scripts/dart_client.py 005490.KS

# SEC EDGAR 재무 직접 fetch (미국)
python3 plugins/sec-edgar-integration/scripts/sec_client.py BTU
```

---

## 📊 보고서 섹션 흐름

per-stock combined PDF의 섹션 순서 (v0.5.0 기준):

```
1.  Cover
2.  Company Intro
3.  Deep Research (산업 + 재무 + 카탈리스트/리스크)
4.  Financial Statements US-GAAP (5Y annual + 5Q quarterly + variance)
5.  News Timeline (중립 제외 + 월별 +/- bar chart)
6.  Executive Brief + Thesis List (implicit thesis 자동 보강)
7.  R1 Quant Anchor
8.  R2 Persona Panel (Thesis × Persona Matrix)
9.  R3 Decision Section
10. (선택) ETF Holdings · Reverse DCF · Subagent Debate
11. Appendix
```

---

## 📁 프로젝트 구조

```
.
├── CLAUDE.md                           # Claude Code/Cowork 자동 로드 컨텍스트
├── README.md                           # 이 파일
├── REPORT_FORMAT_STANDARD.md           # 보고서 형식 표준 (lock-in)
├── ENHANCEMENT_ROADMAP.md              # 향후 계획
├── .env                                # API 키 (gitignored)
├── .claude/
│   ├── commands/                       # Claude Code slash commands (자동 동기화)
│   └── settings.local.json
│
├── commands/                           # Cowork plugin commands
│   ├── analyze-blog.md
│   ├── analyze-stock.md
│   ├── dart-status.md
│   ├── list-analyses.md
│   ├── sec-status.md
│   ├── setup.md
│   └── validate-analysis.md
│
├── scripts/
│   └── sync_commands.sh                # Cowork ↔ Claude Code commands 동기화
│
├── plugins/                            # 10 plugins
│   ├── backtester/                     # 적중률·alpha 백테스트
│   ├── blogger-registry/               # 8명 블로거 메타·라우팅
│   ├── dart-integration/               # 한국 전자공시 자동 fetch
│   ├── investor-personas/              # 13명 페르소나 정의
│   ├── multi-model-arena/              # Claude + OpenAI + Gemini
│   ├── news-integration/               # NewsAPI.org + .ai + Finnhub
│   ├── report-suite/                   # ⭐ R1+R2+R3+Deep Research+FS PDF
│   │   └── skills/_common/
│   │       ├── financial_statements_us_gaap.py
│   │       ├── implicit_thesis_extractor.py
│   │       ├── news_disclosures.py
│   │       └── ...
│   ├── sec-edgar-integration/          # 미국 SEC EDGAR XBRL fetch
│   ├── subagent-orchestrator/          # Bull-Bear-Skeptic debate
│   └── trade-engine/                   # Risk · Portfolio · Paper sim
│
└── .analysis-log/                      # 분석 결과 영구 저장 (각 README.md 포함)
    ├── bloggers/{blogger}/{date}_{slug}/
    └── standalone/{date}_{ticker}_{name}/
```

---

## 🎯 분석 사례

### Peabody Energy (BTU) — 미국 석탄 standalone (2026-04-30, 재빌드 2026-05-11)
- **종목**: BTU (NYSE)
- **데이터**: SEC EDGAR FY2025 10-K (2026-02-19 공시) + 5분기 quarterly
- **Verdict**: lean_bullish (signal +0.15)
- **핵심 발견**: FY2025 영업 적자 전환 (-$80M), Net Cash position 유지 ($-254M Net Debt)
- **결과**: 69p 통합 PDF
- **위치**: `.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/reports/combined_v2/`

### Cheniere Energy (LNG) — 미국 천연가스 LNG export 1위 (2026-05-11)
- **종목**: LNG (NYSE)
- **컨텍스트**: 메르(ranto28) Henry Hub LNG 분석에서 식별
- **Verdict**: lean_bullish (signal +0.385) — Buy 6 / Neutral 6 / Sell 1
- **Implicit Thesis**: 메르 thesis 4개 + implicit catalyst 4개 + risk 4개 = 총 12개 thesis
- **결과**: 62p 통합 PDF
- **위치**: `.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/reports/combined/`

### 의교창 — 리튬 구조적 강세 (2026-04-29)
- **블로그**: https://blog.naver.com/doctordk/224269642921
- **종목**: POSCO홀딩스 · 삼성SDI · ALB · SQM · LIT (Top 5)
- **결과**: 5개 통합 PDF (각 45-52p)
- **위치**: `.analysis-log/bloggers/doctordk/2026-04-29_lithium/reports/combined_v6_final/`

---

## 📜 Version History

### v0.5.0 (2026-05-11) — 재무 분석 + Standalone 강화
구체적인 5단계 phase 작업으로 진행:

- **Phase 1 — Deep Research 위치 승격**
  - 보고서 섹션 8 → 섹션 3으로 이동 (Cover → Intro → Deep Research)
  - 산업·재무·카탈리스트·리스크를 페이지 도입부에서 먼저 보여줌
- **Phase 2 — `financial_statements_us_gaap.py` 신규 모듈**
  - 모든 plugin agent의 재무 분석 anchor 의무 사용
  - 5년 annual + 5분기 quarterly (Q4는 10-K - 9M YTD로 derive)
  - SEC EDGAR XBRL (미국) + DART (한국) 통합
  - ASC 220 / 210 / 230 표준 형식
  - Material Variance Summary 자동 플래깅 (임계값: > $1B = $50M/5%, $100M-$1B = $25M/10%, < $100M = $5M/15%)
- **Phase 3 — News Timeline 개선**
  - 중립(○) 항목 상세 표에서 제외 (KPI엔 카운트 유지)
  - 긍정/부정 상세 요약 (`expand_summary` + `impact_reason` 필드)
  - 종목별 월별 +/- bar chart (matplotlib base64 PNG 임베드)
- **Phase 4 — Thesis × Persona Matrix 정상화**
  - silent skip 제거 → 데이터 부재 시 명시적 진단 메시지
  - `thesis_lens_applications` 필드 강제 출력 (persona-evaluator 프롬프트)
- **Phase 5 — Implicit Thesis 자동 추출** (`implicit_thesis_extractor.py`)
  - blog 글 없이 ticker만 분석 시 deep_research·financial 데이터로 thesis 자동 보강
  - catalysts → predictive · risks → conditional · industry → factual · sector → normative

추가 개선:
- **NewsAPI.ai (Event Registry) 통합**: UUID 키 형식, 1-year lookback (NewsAPI.org 30일 cap 보완)
- **한글 docx 폰트 표준**: `Apple SD Gothic Neo` (macOS) + OXML rFonts 직접 설정 — Malgun Gothic 사용 금지
- **분석별 instruction README 자동 생성기**: `build_instruction_readme.py` 신규
- **Claude Code CLI 호환성**: `.claude/commands/` 자동 동기화 (`scripts/sync_commands.sh`)

### v0.4.0 (2026-04-30) — 통합 보고서 풍성화
- **ETF Holdings 섹션**: ETF 종목인 경우 holdings 자동 표시
- **Reverse DCF (Damodaran 자동)**: 현재 가격에 내재된 성장률·할인율 역산
- **Subagent Debate**: Bull(Druckenmiller) vs Bear(Buffett) vs Skeptic round-robin
- **종목명 자동 매핑**: 005490.KS → POSCO홀딩스 등 (ticker_resolver)
- **PDF 한글 호환성 개선**: pdftocairo 후처리 도입 (모든 뷰어 호환)

### v0.3.0 (2026-04 초) — 13명 페르소나 + 4-Analyst
- **13명 legendary 투자자 페르소나**: Buffett·Munger·Lynch·Wood·Burry·Taleb·Graham·Ackman·Pabrai·Fisher·Jhunjhunwala·Druckenmiller·Damodaran
- **4-Analyst 평가**: Macro · Industry · Empirical · Counter-thesis
- **Deep Research 섹션 도입**: 산업 · 5년 P&L · Bull/Base/Bear · Catalyst Timeline · Risk Matrix
- **한국 종목 calibration**: 페르소나별 가중치 (Druckenmiller 1.5x, Lynch 1.3x, Buffett 0.7x 등)

### v0.2.0 (2026-03 ~ 2026-04 초) — Multi-model + Backtester
- **Multi-model arena**: OpenAI gpt-5.5 + Gemini 3.1 + Claude 합의
- **Backtester**: verdict 적중률 + KOSPI/SPY 대비 alpha + drawdown 분석
- **Trade engine**: Risk Manager (변동성 기반 한도) + Portfolio Manager + Paper portfolio simulator
- **Subagent orchestrator**: pipeline · debate · refinement cycle

### v0.1.0 (2026-02 ~ 2026-03 초) — 초기 셋업
- **8명 네이버 블로거 registry**: 메르·의교창·승도리·DaeGurr·GSVI·인피의·제주바람·농구천재
- **DART OpenAPI 통합**: 한국 종목 공시·재무 자동 fetch
- **R1/R2/R3 보고서 builder**: 정량 anchor + 페르소나 panel + 의사결정 시트
- **Naver 블로그 본문 추출 + thesis-first 분석 파이프라인**

---

## 🛠️ Plugin 버전 매트릭스

| Plugin | 현재 | 주요 변경 |
|---|---|---|
| `report-suite` | v0.5.0 | financial_statements_us_gaap.py + implicit_thesis_extractor.py + 새 섹션 흐름 |
| `news-integration` | v0.2.0 | NewsAPI.ai (Event Registry) 통합 추가 |
| `investor-personas` | v0.4.0 | thesis_lens_applications 강제 출력 + financial_statements anchor 의무 |
| `dart-integration` | v0.1.0 | 한국 종목 공시·재무 (안정 운영) |
| `sec-edgar-integration` | v0.1.0 | 미국 종목 10-K/10-Q XBRL (안정 운영) |
| `multi-model-arena` | v0.2.0 | Claude + OpenAI + Gemini 합의 |
| `subagent-orchestrator` | v0.2.0 | Bull-Bear-Skeptic debate cycle |
| `trade-engine` | v0.2.0 | Risk · Portfolio · Paper portfolio simulator |
| `backtester` | v0.2.0 | 적중률·alpha·drawdown 분석 |
| `blogger-registry` | v0.1.0 | 8명 블로거 메타·라우팅 |

---

## 💻 Cowork 모드 vs Claude Code CLI

본 시스템은 **두 환경 모두 동일하게 작동**합니다:

### Cowork 모드 (claude.ai 데스크탑 앱)
- `commands/*.md` 슬래시 명령어 자동 인식
- `CLAUDE.md` 자동 컨텍스트 로드
- workspace 폴더 직접 접근

### Claude Code CLI
- `.claude/commands/*.md` 슬래시 명령어 (Cowork commands를 mirror함)
- `CLAUDE.md` 자동 컨텍스트 로드 (working directory 기반)
- 직접 Python 호출 + bash 환경

### 환경 동기화
새 명령어 추가 시 다음 스크립트로 동기화:
```bash
bash scripts/sync_commands.sh
```

---

## ⚠️ 면책 사항

본 시스템은 **paper portfolio simulation** 전용입니다. 실제 거래는 절대 자동 실행하지 않습니다. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처가 명시되어 있으니, 본인의 판단을 보완하는 reference로 활용해 주세요.

---

## 📚 추가 문서

- [`CLAUDE.md`](CLAUDE.md) — Claude Code/Cowork 자동 로드 컨텍스트
- [`REPORT_FORMAT_STANDARD.md`](REPORT_FORMAT_STANDARD.md) — 보고서 형식 표준 (필수 참조)
- [`ENHANCEMENT_ROADMAP.md`](ENHANCEMENT_ROADMAP.md) — 향후 계획
- [`plugins/dart-integration/README.md`](plugins/dart-integration/README.md) — DART 활성화 가이드
- 각 분석 디렉토리의 `README.md` — 분석별 instruction (자동 생성)

---

## 🔗 참고

- DART OpenAPI: https://opendart.fss.or.kr
- SEC EDGAR API: https://www.sec.gov/edgar/sec-api-documentation
- NewsAPI.ai (Event Registry): https://eventregistry.org/documentation
- vibe-investing (영감): https://github.com/virattt/ai-hedge-fund (MIT)
- WeasyPrint: https://weasyprint.org/

---

## 📝 라이선스

MIT (각 plugin 동일)
