# Claude Code 환경 Quick-Start (v0.9.x)

> Cowork(데스크탑 GUI)와 별도로 **Claude Code (macOS CLI)** 에서 동일 분석을 실행하기 위한 5분 가이드.
> 본 가이드는 v0.9.x baseline (Sprint E+F+F-3 모든 패치 적용 후) 기준입니다. v0.8.0 이전 명령은 backwards compatible 하나, F-3 LLM Checklist 등 신규 기능 활용 권장.

## 0. 환경 비교

| 항목 | Claude Cowork (현재) | Claude Code (CLI) |
|---|---|---|
| 인터페이스 | 데스크탑 GUI 앱 | macOS Terminal |
| Sandbox | 격리 VM (45초 bash timeout) | 로컬 머신 직접 실행 (timeout 없음) |
| 디렉토리 | `~/Documents/Claude/Projects/주식 분석` (Drive mount) | 자유롭게 `cd` (예: `~/dev/stock-analysis`) |
| 외부 CLI 호출 (Codex, git 등) | 제한적 | ✅ 자유 |
| Long-running 작업 (5분+) | ❌ timeout | ✅ 가능 |
| 적합 시나리오 | 빠른 1-2종목 분석 | 5+ 종목 풀 파이프라인, 백테스트 |

## 1. Claude Code 설치 (1회)

```bash
# macOS Homebrew
brew install claude-code

# 또는 npm
npm install -g @anthropic-ai/claude-code

# 확인
claude --version
```

## 2. 본 repo 로컬 clone (1회)

```bash
# 원하는 디렉토리에서 (예: 홈 directory)
cd ~
git clone https://github.com/DrugnSafety/stock-analysis.git stock-analysis
cd stock-analysis
```

> **참고**: GitHub repo는 private이므로 GitHub PAT (Personal Access Token) 필요. [github.com/settings/tokens](https://github.com/settings/tokens?type=beta)에서 발급 후
> `git clone https://<USERNAME>:<TOKEN>@github.com/DrugnSafety/stock-analysis.git`

## 3. .env 설정 (1회)

`.env`는 git에 push 안 됨 — Office/Home 각자 따로 작성. **현재 Cowork의 .env를 복사하는 것이 가장 빠름**:

```bash
# .env 새로 작성 (또는 1Password 등에서 복사)
cat > .env << 'EOF'
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIzaSy...
DART_API_KEY=fcda4b9b...
NEWSAPI_KEY=
FINNHUB_KEY=

# LangSmith
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=lsv2_pt_...
LANGSMITH_PROJECT=stock-analysis
LANGSMITH_ENDPOINT=https://api.smith.langchain.com

# GitHub sync
GITHUB_TOKEN=github_pat_...
GITHUB_OWNER=DrugnSafety
GITHUB_REPO=stock-analysis

# Notion
NOTION_DATA_SOURCE_ID=...

# Anthropic (Claude Code가 사용)
ANTHROPIC_API_KEY=sk-ant-...
EOF
```

## 4. Python 의존성 설치 (1회)

```bash
# Python 3.10+ 권장
python3 -m venv .venv
source .venv/bin/activate
pip install yfinance pdfkit reportlab python-docx python-pptx requests beautifulsoup4 \
            matplotlib pandas numpy lxml weasyprint langsmith openai anthropic
```

## 5. OpenAI Codex CLI 설치 (선택)

```bash
npm install -g @openai/codex
codex  # 처음 실행 시 ChatGPT 계정으로 인증
```

## 6. 분석 실행 (매번)

```bash
cd ~/stock-analysis
git pull  # 최신 코드 동기화

# Claude Code 세션 시작
claude

# 또는 직접 실행:
PDIR=.analysis-log/bloggers/ranto28/2026-05-19_perovskite_space_DC_merged

# Specialist Agents (Tier 2)
python3 plugins/specialist-agents/skills/research-manager/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2
python3 plugins/specialist-agents/skills/sentiment-analyst/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2
python3 plugins/specialist-agents/skills/earnings-reviewer/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2
python3 plugins/specialist-agents/skills/model-builder/scripts/run.py --pipeline-dir $PDIR --tickers TICK1 TICK2

# OpenAI Codex cross-validation (선택)
python3 plugins/codex-integration/scripts/codex_runner.py --mode o3 \
  --system "당신은 senior equity analyst. thesis review only." \
  --prompt "$(cat $PDIR/thesis_list.json)"

# PDF 빌드 (Cowork와 동일)
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir $PDIR \
  --output-dir $PDIR/reports/combined \
  --top-n 5

# GitHub sync (자동)
# build_combined.py post-build hook으로 자동 실행
```

## 6b. Phase 7 Evidence Layer (외부 근거 + 팩트체크) — Claude Code 재검증 완료

> **재검증 결과 (2026-06-02)**: Phase 7 신규 모듈은 **stdlib-only**(`urllib`·`json`·`re`)라 외부 패키지 의존이 없습니다. Cowork sandbox에서 막히던 **weasyprint PDF 최종 빌드·DART corp_code 예열이 Claude Code(로컬 macOS)에서는 제약 없이 실행**됩니다. 즉 Phase 7은 Claude Code에서 **더 완전하게** 동작합니다.

```bash
PDIR=.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy

# (1) evidence 수집 — WebSearch hits는 Claude Code 세션에서 agent가 주입,
#     SEC EFTS·DART는 Python이 직접 fetch (timeout 제약 없음)
python3 -c "
import sys; sys.path.insert(0,'plugins/report-suite/skills/_common')
from evidence_retriever import EvidenceRetriever
er = EvidenceRetriever('BTU', exchange='NYSE', company='Peabody Energy')
er.fetch_sec_efts(forms=['8-K','10-Q'], lookback_days=400)
er.fetch_dart()          # .KS/.KQ 종목만 (corp_code 예열 제약 없음)
er.write('$PDIR/evidence')
"

# (2) 빌드 — evidence/{ticker}.json 있으면 자동으로 주입+팩트체크 Citation Audit 렌더
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker BTU --deep-research $PDIR/deep_research/BTU.json \
  --stocks $PDIR/stocks.json --thesis $PDIR/thesis_list.json \
  --eval-dir $PDIR/thesis_eval --risk-limits $PDIR/risk_limits.json \
  --decisions $PDIR/decisions.json --portfolio $PDIR/portfolio.json \
  --output $PDIR/reports/BTU_combined.pdf

# (3) codex LLM 검증기 추가 (선택) — codex CLI 네이티브라 Claude Code에서 유리
FACTCHECK_LLM=1 python3 ... (동일 빌드)   # codex가 stance-aware 모순 판단 보강
```

**Phase 7 env 플래그**: `DISABLE_FACTCHECK=1`(팩트체크/Audit 끔) · `FACTCHECK_LLM=1`(codex 검증기 on).

## 7. Office-Home 동기화 워크플로우

```bash
# Office에서 분석 실행 후
git add -A
git commit -m "분석 결과 X 추가 + 인사이트 메모"
git push

# Home에서
git pull
# Claude Code 시작하여 결과 review·확장
```

## 8. LangSmith Dashboard 활용

매 분석 실행 시 자동으로 [smith.langchain.com](https://smith.langchain.com) → `stock-analysis` project에 trace 적재.

확인 가능:
- 각 LLM call의 input/output/latency
- 비용 추적 (모델별·agent별)
- A/B 비교 (Claude vs OpenAI cross-validation 결과)

## 9. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| `weasyprint` 설치 실패 (macOS) | system lib 부족 | `brew install pango cairo gdk-pixbuf libffi` |
| `claude` 명령 not found | Claude Code 미설치 | `brew install claude-code` |
| `codex` 명령 not found | OpenAI Codex CLI 미설치 | `npm i -g @openai/codex` |
| LangSmith trace 안 보임 | LANGSMITH_TRACING=false | `.env` 확인 |
| 한글 PDF 깨짐 | Noto Sans CJK 미설치 | `brew install --cask font-noto-sans-cjk-kr` |
| Citation Audit 섹션 안 나옴 | `evidence/{ticker}.json` 없음 | evidence_retriever로 먼저 수집 (6b 참조) |
| DART evidence 0건 | corp_code 캐시 없음 | Claude Code는 예열 제약 없음 — 첫 fetch 시 자동 다운로드 |
| codex 검증기 no-op | `FACTCHECK_LLM` 미설정 or codex 없음 | `FACTCHECK_LLM=1` + `npm i -g @openai/codex` |

## 10. 추가 학습 자료

- 본 repo `README.md` — 전체 시스템 개요
- `CLAUDE.md` — 상세 워크플로우 + plugin 인덱스
- `REPORT_FORMAT_STANDARD.md` — canonical 형식
- [Anthropic Claude Code docs](https://docs.claude.com/en/docs/agents/code-overview)
- [LangSmith docs](https://docs.smith.langchain.com)
- [OpenAI Codex CLI](https://github.com/openai/codex)

---

## 11. v0.9.x baseline 명령 (Sprint E+F+F-3 모두 적용 후)

### A. 기존 분석을 Claude Code로 이어가기

Cowork에서 진행 중이던 삼성전자(005930.KS) 분석을 그대로 Claude Code에서 재빌드하려면:

```bash
cd ~/stock-analysis  # 또는 ~/Documents/Claude/Projects/주식 분석
git pull             # cowork에서 push한 v0.9.x 패치 모두 받기

SAMSUNG=".analysis-log/standalone/2026-05-30_005930_삼성전자"

# (1) Persona 17명 aggregate — Sprint E-1 신규 의무 절차
python3 plugins/investor-personas/skills/persona-panel/scripts/aggregate_panel.py \
  $SAMSUNG/persona_panel/005930.KS \
  --output $SAMSUNG/persona_panel/005930.KS/aggregate.json

# (2) (선택) 영어 rationale 한글 번역 — Sprint E-6, 처음 1회만
# .bak 자동 백업, 캐시 없으므로 다시 실행 시 비용 발생
python3 scripts/translate_thesis_eval.py $SAMSUNG/thesis_eval/all_aggregate.json

# (3) PDF 빌드 — F-3 LLM Checklist 자동 작동 (~50건 call, ~$0.005)
DISABLE_SYNC=1 python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 005930.KS \
  --stocks "$SAMSUNG/stocks.json" \
  --meta "$SAMSUNG/meta.json" \
  --thesis "$SAMSUNG/thesis_list.json" \
  --eval-dir "$SAMSUNG/thesis_eval" \
  --persona-aggregate "$SAMSUNG/persona_panel/005930.KS/aggregate.json" \
  --persona-aggregates-all "$SAMSUNG/persona_panel/_all_aggregates.json" \
  --persona-full "$SAMSUNG/persona_panel/005930.KS" \
  --decisions "$SAMSUNG/decisions.json" \
  --portfolio "$SAMSUNG/portfolio.json" \
  --risk-limits "$SAMSUNG/risk_limits.json" \
  --deep-research "$SAMSUNG/deep_research/005930.KS.json" \
  --output "$SAMSUNG/reports/combined/1_005930.KS_삼성전자_combined_v6.pdf"

open "$SAMSUNG/reports/combined/1_005930.KS_삼성전자_combined_v6.pdf"
```

→ Cowork v5 PDF와 동일 결과, F-3 LLM Checklist 캐시는 `.cache/checklist_llm/005930.KS.json`이 git tracked가 아니라면 다시 LLM 호출 발생.

### B. 새 종목 standalone 분석 (Claude Code 권장)

```bash
# Claude Code 세션 시작
claude

# 세션 안에서:
> /analyze-stock 000660.KS SK하이닉스
```

→ Claude가 8단계 파이프라인 자동 실행:
1. meta.json 작성
2. yfinance live fetch → stocks.json
3. thesis_list.json (DART 사업보고서·뉴스 기반)
4. deep_research/{ticker}.json (DART 5Y 재무 + 산업 + 시나리오 + 카탈리스트 + 리스크)
5. macro_snapshot.json (6 institutions)
6. quant_anchor_{ticker}.json (DCF + Reverse DCF + Risk Metrics)
7. thesis_eval/ (real 4-Analyst — gpt-4o-mini)
8. persona_panel/{ticker}/ (17명) → `aggregate_panel.py` 실행
9. risk_limits + decisions + portfolio
10. PDF 빌드 (F-3 LLM Checklist 자동 적용)

### C. v0.9.x 신규 환경변수

```bash
# .env 또는 명령 prefix로 설정 가능
OECD_FULL_TABLE=1            # OECD 57개국 raw table 강제 (default: 1줄 summary)
DISABLE_LLM_CHECKLIST=1      # F-3 LLM Checklist 비활성화 (default: 켜짐)
DISABLE_FACTCHECK=1          # v0.8.0 Citation Audit 끔
FACTCHECK_LLM=1              # codex LLM fact-checker 켬 (codex CLI 필요)
DISABLE_SYNC=1               # GitHub+Notion auto-sync 끔
```

### D. F-3 LLM Checklist 캐시 관리

```bash
# 캐시 위치
ls -la .cache/checklist_llm/

# 특정 종목 캐시 삭제 (LLM 재호출 강제)
rm .cache/checklist_llm/005930.KS.json

# 전체 캐시 정리
rm -rf .cache/checklist_llm/

# 캐시 영구 보관 (git에 push 원할 시 .gitignore에서 제거)
# 기본 .gitignore는 .cache/ 무시 — 캐시는 local 전용
```

## 12. v0.9.x 핵심 차이 (Cowork → Claude Code)

| 항목 | Cowork (45초 timeout) | Claude Code (timeout 없음) |
|---|---|---|
| Persona 17명 panel | ✅ 가능하지만 분할 실행 권장 | ✅ 한 번에 17 thread 병렬 |
| F-3 LLM Checklist (~50 calls) | ⚠️ 끝나기 직전 timeout 가능 | ✅ 여유 있음 |
| E-6 영어→한글 번역 | ❌ 30~60초 소요로 timeout | ✅ 1~2분 완료 |
| weasyprint PDF 빌드 | ⚠️ system lib 의존 (brew 권장) | ✅ macOS 직접 brew 설치 가능 |
| Phase 7 evidence_retriever | ⚠️ WebSearch 의존 시 timeout | ✅ DART corp_code 예열 가능 |
| Multi-stock (5종목) 일괄 | ⚠️ chunk 분할 필요 | ✅ 한 번에 가능 |

## 13. macOS 첫 설치 체크리스트 (한 번에 묶음)

```bash
# 1. 필수 brew packages
brew install python@3.11 git node
brew install pango cairo gdk-pixbuf libffi      # weasyprint
brew install --cask font-noto-sans-cjk-kr       # 한글 PDF 폰트

# 2. Claude Code + Codex CLI (선택)
brew install claude-code                         # 또는 npm i -g @anthropic-ai/claude-code
npm install -g @openai/codex                     # OpenAI Codex (FACTCHECK_LLM용)

# 3. 본 repo clone
cd ~
git clone https://<USERNAME>:<GITHUB_PAT>@github.com/DrugnSafety/stock-analysis.git
cd stock-analysis

# 4. Python venv + 패키지
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install yfinance pdfkit reportlab python-docx python-pptx requests beautifulsoup4 \
            matplotlib pandas numpy lxml weasyprint langsmith openai anthropic pypdf

# 5. .env 작성 (Cowork .env 복사 또는 1Password 동기화)
# 필수: OPENAI_API_KEY, ANTHROPIC_API_KEY, DART_API_KEY, GITHUB_TOKEN
# 권장: NEWSAPI_KEY, FINNHUB_KEY, LANGSMITH_API_KEY

# 6. 첫 분석 실행
claude
> 삼성전자 005930.KS 분석해줘
```

## 14. Cowork와 결과 공유 (Office-Home 워크플로우)

```bash
# Claude Code 측 (분석 실행 후)
git add -A
git commit -m "삼성전자 v6 분석 + F-3 캐시 갱신"
git push

# Cowork 측 (사용자 데스크탑)
# CLAUDE.md 자동 reload — 별도 작업 불필요
# 단, .cache/checklist_llm/은 cowork/Claude Code 서로 다른 위치라 캐시 공유 안 됨
```

## 15. F-3 LLM Checklist 사용 사례

Claude Code에서 가장 큰 이점:

| 사례 | Cowork | Claude Code |
|---|---|---|
| 5종목 분석 × 17 persona × 50 LLM calls = 4,250 calls | ❌ 8시간+ chunk 분할 | ✅ 약 15~25분 |
| 회사 데이터 사전 캐시 후 17×10 LLM 평가 보고서 자동화 | 어려움 | 1줄 명령 |
| LangSmith trace 분석 (어느 페르소나가 가장 비용 큰지) | timeout으로 일부만 | 전체 trace 확보 |

Cowork는 "빠른 1-2종목 검증·prototyping"에, Claude Code는 "프로덕션 배치·다종목 비교"에 최적.
