# 주식 분석 시스템 — Claude Code 컨텍스트

> **Auto-loaded by Claude Code** when started in this directory. Provides project context, plugin registry, and frequently-used commands.

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

| Skill | 트리거 키워드 |
|---|---|
| `naver-blog-investment:analyze-blog` | "블로그 분석", "메르 글 분석" |
| `dart-integration:dart-disclosure-fetch` | "DART 공시", "전자공시", "사업보고서" |
| `dart-integration:dart-financial-fetch` | "DART 재무", "5년 손익" |
| `sec-edgar-integration:sec-disclosure-fetch` | "SEC 공시", "10-K", "EDGAR filings" |
| `sec-edgar-integration:sec-financial-fetch` | "SEC 재무", "10-K 재무제표", "5년 손익 미국" |
| `news-integration:news-fetcher` | "뉴스 fetch", "company news" |
| `report-suite:unified-builder` | "통합 보고서", "PDF 생성" |
| `subagent-orchestrator:debate-orchestrator` | "Bull/Bear debate", "subagent debate" |
| `backtester:hit-rate-analyzer` | "적중률", "백테스트" |
| `trade-engine:risk-manager` | "포지션 한도", "변동성 조정" |
| `trade-engine:portfolio-manager` | "신호 점수", "매수/매도 결정" |

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
- **`REPORT_FORMAT_STANDARD.md` — 보고서 형식 표준 (필수 참조)**
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

## 🚀 v0.5.0 고도화 (2026-05-11 적용 완료)

다음 4가지 고도화가 보고서 표준에 통합되었습니다:

1. **`/finance:financial-statements` 의무 활용** (모든 plugin agent)
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

**`stocks.json`의 `market_data` 필드는 절대 LLM이 채우면 안 됨.** 반드시 `market_fetcher.py`로 실제 yfinance 호출:

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

- DART OpenAPI: https://opendart.fss.or.kr (한국 종목 공시)
- SEC EDGAR: https://www.sec.gov/edgar/sec-api-documentation (미국 종목 — 향후 통합)
- yfinance docs: https://pypi.org/project/yfinance/ (가격·재무)
- Naver 블로그 API: PostTitleListAsync.naver (블로그 글 list)
