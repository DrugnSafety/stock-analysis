# Claude Code 환경 Quick-Start

> Cowork(데스크탑 GUI)와 별도로 **Claude Code (macOS CLI)** 에서 동일 분석을 실행하기 위한 5분 가이드.

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

## 10. 추가 학습 자료

- 본 repo `README.md` — 전체 시스템 개요
- `CLAUDE.md` — 상세 워크플로우 + plugin 인덱스
- `REPORT_FORMAT_STANDARD.md` — canonical 형식
- [Anthropic Claude Code docs](https://docs.claude.com/en/docs/agents/code-overview)
- [LangSmith docs](https://docs.smith.langchain.com)
- [OpenAI Codex CLI](https://github.com/openai/codex)
