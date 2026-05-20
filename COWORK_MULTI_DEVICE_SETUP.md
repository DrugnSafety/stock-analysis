# Claude Cowork 다중 디바이스 환경 셋업

> 회사·집 두 컴퓨터에서 동일 Cowork 환경을 사용하기 위한 가이드.
> Anthropic 공식 sync 제약을 솔직히 설명하고 **실제 작동하는 우회 셋업**을 단계별로 제시.

## 0. 현재 Claude Cowork 동기화 제약 (Anthropic 공식)

2026년 5월 기준 Claude Cowork의 multi-device 한계:

| 항목 | 자동 동기화 여부 | 출처 |
|---|---|---|
| 대화 내용 (conversation history) | ❌ **single-device lock**, account-level sync 없음 | [GitHub issue #22648](https://github.com/anthropics/claude-code/issues/22648), [#43698](https://github.com/anthropics/claude-code/issues/43698) |
| Cowork session export/import | ❌ 불가 | [#43698](https://github.com/anthropics/claude-code/issues/43698) |
| Imported knowledge (memory) | ⚠️ 부분 — 같은 Anthropic 계정 + 같은 knowledge base ID로 양쪽 mount 가능 | (Claude.ai web에서 관리) |
| Plugin 설치 상태 | ❌ 자동 sync 없음. **마켓플레이스 등록은 양쪽에서 동일하게 작동** | [Claude Code Plugin Marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces) |
| Project folder (`~/Documents/Claude/Projects/...`) | ❌ 로컬 파일시스템 — OS 레벨 sync에 의존 | macOS iCloud / Drive 등 |
| Claude Dispatch (2026-03-19 발표) | ✅ **cross-device conversation thread** — 회사에서 시작한 작업을 집에서 이어 가능 (제한적) | [Claude Dispatch 발표](https://letsdatascience.com/news/anthropic-launches-claude-dispatch-for-multi-device-tasks-62d8c30d) |

**핵심 메시지**: Cowork 대화 자체는 자동 sync 안 되지만, **분석 결과·plugin·project folder는 우회 방법으로 sync 가능**합니다.

---

## 1. 권장 셋업 — 3단계 전략

### 전략 A: Plugin은 Private Marketplace (GitHub) 사용
### 전략 B: Project folder는 iCloud Drive 또는 GitHub repo 사용
### 전략 C: 분석 결과·메모리는 Notion DB로 sync (이미 구축됨)

전략 별 trade-off:

| 항목 | iCloud Drive | GitHub repo | Notion DB |
|---|---|---|---|
| 자동 sync 속도 | ✅ 즉시 (~30초) | ⚠️ git pull/push 필요 | ✅ 즉시 |
| 충돌 해결 | ⚠️ Conflict file 생성 | ✅ git merge | ✅ 자동 |
| 한글 폴더명 | ⚠️ NFD/NFC 차이 가능 | ✅ UTF-8 정상 | ✅ 정상 |
| Secret(.env) 동기화 | ⚠️ 위험 (평문) | ❌ gitignored — 양쪽 따로 | ❌ 양쪽 따로 |
| 대용량 PDF | ⚠️ 트래픽 큼 | ✅ delta sync | ❌ 부적합 |

**최적 조합**: GitHub repo (소스코드·분석결과) + Notion DB (메타데이터) + **양쪽 컴퓨터 각자 .env**.

---

## 2. 셋업 — Phase 1: Plugin Private Marketplace (필수, 30분)

우리 plugin들을 **재사용 가능한 marketplace**로 변환합니다. 양쪽 Cowork에서 `/plugin install` 한 줄로 동기화 가능.

### Step 1: Marketplace repo 생성 (회사 컴퓨터에서 1회)

```bash
# 별도 marketplace repo 생성
cd ~/Documents/Claude/Projects/
git init stock-analysis-marketplace
cd stock-analysis-marketplace

# manifest 파일 작성
cat > .claude-plugin/marketplace.json << 'EOF'
{
  "name": "stock-analysis-marketplace",
  "version": "1.0.0",
  "description": "Mingyu의 private 주식 분석 plugin marketplace",
  "plugins": {
    "report-suite": {
      "source": "./plugins/report-suite",
      "description": "13 persona panel + 4-Analyst + R1/R2/R3 PDF 보고서 생성"
    },
    "specialist-agents": {
      "source": "./plugins/specialist-agents",
      "description": "Research Manager + Sentiment + Earnings Reviewer + Model Builder (Anthropic Finance Agents 패턴)"
    },
    "investor-personas": {
      "source": "./plugins/investor-personas",
      "description": "13명 legendary investor persona 정의"
    },
    "multi-model-arena": {
      "source": "./plugins/multi-model-arena",
      "description": "Claude + OpenAI + Gemini cross-validation"
    },
    "trade-engine": {
      "source": "./plugins/trade-engine",
      "description": "Risk Manager + Portfolio Manager + Paper Portfolio"
    },
    "backtester": {
      "source": "./plugins/backtester",
      "description": "과거 verdict 적중률 + KOSPI/SPY alpha"
    },
    "blogger-registry": {
      "source": "./plugins/blogger-registry",
      "description": "8명 네이버 블로거 메타데이터 + 신규 글 자동 수집"
    },
    "dart-integration": {
      "source": "./plugins/dart-integration",
      "description": "한국 DART 전자공시 + 5Y 재무 자동 fetch"
    },
    "sec-edgar-integration": {
      "source": "./plugins/sec-edgar-integration",
      "description": "미국 SEC EDGAR 10-K/10-Q/8-K + 5Y 재무 자동 fetch"
    },
    "news-integration": {
      "source": "./plugins/news-integration",
      "description": "NewsAPI + Finnhub 뉴스 자동 fetch"
    },
    "subagent-orchestrator": {
      "source": "./plugins/subagent-orchestrator",
      "description": "Bull/Bear/Skeptic debate cycle"
    },
    "github-notion-sync": {
      "source": "./plugins/github-notion-sync",
      "description": "분석 결과 GitHub + Notion 자동 동기화"
    },
    "codex-integration": {
      "source": "./plugins/codex-integration",
      "description": "OpenAI Codex CLI + API cross-validation"
    }
  }
}
EOF

# 실제 plugin 코드 복사
mkdir -p plugins
rsync -av ~/Documents/Claude/Projects/주식\ 분석/plugins/ ./plugins/ \
  --exclude '__pycache__' --exclude '*.pyc'

# GitHub private repo로 push
gh repo create DrugnSafety/stock-analysis-marketplace --private --source=. --remote=origin --push
```

### Step 2: 회사·집 양쪽 Cowork에서 marketplace 등록

각 컴퓨터의 Cowork 명령창에서:
```
/plugin marketplace add https://github.com/DrugnSafety/stock-analysis-marketplace
/plugin install report-suite@stock-analysis-marketplace
/plugin install specialist-agents@stock-analysis-marketplace
# ... 13개 plugin 일괄 install
```

또는 한 번에:
```
/plugin marketplace install-all stock-analysis-marketplace
```

### Step 3: Plugin 업데이트 자동화

회사에서 plugin 수정 후:
```bash
cd ~/Documents/Claude/Projects/stock-analysis-marketplace
# 변경 반영
rsync -av ~/Documents/Claude/Projects/주식\ 분석/plugins/ ./plugins/
git add -A && git commit -m "plugin 업데이트" && git push
```

집에서:
```
/plugin marketplace update stock-analysis-marketplace
# 모든 plugin 최신 버전으로 자동 업데이트
```

---

## 3. Phase 2: Project Folder iCloud 동기화 (선택, 10분)

**언제 사용**: macOS 양쪽 + 작은 파일 (대화 메모·분석 결과 JSON 등) 빠른 sync 원할 때.
**사용 안 함**: PDF 500KB×N 같은 큰 파일은 GitHub repo가 더 적합.

### Step 1: 현재 project folder를 iCloud Drive로 이동

```bash
# 백업
cp -R ~/Documents/Claude/Projects/주식\ 분석/ ~/Desktop/주식_분석_backup_$(date +%Y%m%d)/

# iCloud Drive로 이동
mv ~/Documents/Claude/Projects/주식\ 분석/ \
   ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ Projects/주식\ 분석/

# Cowork가 인식할 수 있도록 심볼릭 링크 생성
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ Projects/주식\ 분석/ \
      ~/Documents/Claude/Projects/주식\ 분석
```

### Step 2: 집 컴퓨터에서도 동일 심볼릭 링크

```bash
# iCloud Drive 동기화 대기 (회사에서 업로드 후 ~5-10분)
ls ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ Projects/주식\ 분석/

# 심볼릭 링크 생성
ln -s ~/Library/Mobile\ Documents/com~apple~CloudDocs/Claude\ Projects/주식\ 분석/ \
      ~/Documents/Claude/Projects/주식\ 분석
```

### 주의사항

- **`.env` 절대 iCloud에 두면 안 됨** — 평문 secret 노출
- **`.git/objects` 충돌 가능** — git 사용 시 iCloud sync 비활성화 권장
- **한글 폴더명 NFD/NFC** — macOS는 NFD 사용, 일부 도구는 NFC 기대 → `convmv -f utf8 -t utf8 --nfc` 등으로 통일 필요

---

## 4. Phase 3: 대화 내용 보존 — Notion + Memory 활용

Cowork 대화 자체는 sync 안 되지만, 다음 두 가지로 우회:

### A. 분석 결과 → Notion DB (이미 구축됨)

매 분석 종료 시 `sync_analysis.py`가 Notion DB에 자동 push:
- 종목·verdict·signal score·decision 메타데이터
- GitHub PDF link
- Bull/Neutral/Bear count

양쪽 컴퓨터에서 [Notion 주식 분석 Hub](https://www.notion.so/b689c03e9bc6481b8c732ca17729f8db) 열면 동일 데이터 확인 가능.

### B. 핵심 인사이트 → memory.md (Cowork imported knowledge)

대화 중요한 결정·인사이트는 `~/Documents/Claude/Projects/주식 분석/memory.md`에 수동 저장. iCloud sync 또는 git push로 양쪽 컴퓨터에서 접근:

```bash
# 회사에서 작업 종료 시
cat >> memory.md << 'EOF'

## 2026-05-20 회사 작업
- 메르 페로브스카이트 분석 진행 — FSLR 12/13 BUY 강세
- Tier 2 specialist-agents plugin 신규 작성
- LangSmith tracing 활성화 — project "stock-analysis"
- TSLA verdict는 split (5 bull / 5 bear) — 신중 검토 필요
EOF
git add memory.md && git commit -m "회사 작업 메모 추가" && git push
```

집에서 Cowork 시작 시 `git pull` → memory.md를 Claude가 자동 인식 (`CLAUDE.md`가 import).

### C. Claude Dispatch (2026-03-19 발표, 제한적 cross-device)

회사 Cowork에서 특정 작업을 Dispatch 모드로 시작 → 집 Cowork에서 이어 받기 가능. 단:
- 대화 history 전체가 아닌 **특정 task thread만** sync
- Anthropic 계정 정상 로그인 필요
- 양쪽 모두 Pro/Max/Team/Enterprise 플랜 (Free는 미지원)

Cowork 명령창:
```
/dispatch start "Tesla FSD 분석 — 회사에서 시작"
# ... 분석 작업 ...
/dispatch save
```

집에서:
```
/dispatch resume "Tesla FSD 분석"
```

---

## 5. 종합 실행 워크플로우

**Day 1 (회사) — 1회 셋업**:
1. `stock-analysis-marketplace` 생성 + plugin 13개 publish → GitHub private repo
2. Cowork에서 `/plugin marketplace add` + `/plugin install` 일괄 실행
3. `.env` 1Password 등 secret manager에 백업

**Day 2 (집) — 1회 셋업**:
1. Cowork에서 `/plugin marketplace add https://github.com/DrugnSafety/stock-analysis-marketplace`
2. `/plugin install` 일괄 실행 (자동으로 13개 plugin 동일 설치)
3. `~/Documents/Claude/Projects/주식 분석/` 디렉토리에 `git clone https://github.com/DrugnSafety/stock-analysis`
4. `.env`는 1Password에서 별도 복사 (절대 push 안 함)

**일상 작업 (회사 → 집)**:
1. 회사 Cowork에서 분석 — 결과 자동 GitHub push + Notion sync
2. 집에서 Cowork 시작 시 `git pull` (terminal 또는 Claude에게 `git pull 해줘` 요청)
3. memory.md + 분석 디렉토리 자동 업데이트 → Claude가 인식
4. 집에서 이어 작업 → 결과 다시 push

**Plugin 업데이트 (어디서든)**:
1. plugin 코드 수정 후 `stock-analysis-marketplace` repo에 push
2. 다른 컴퓨터에서 `/plugin marketplace update` → 자동 최신 버전 install

---

## 6. 한계점 — 솔직 인정

| 한계 | 우회 |
|---|---|
| Cowork 대화 자체가 sync 안 됨 | memory.md + Notion DB로 인사이트만 보존 |
| 1개 Anthropic 계정으로 양쪽 동시 사용 불가 (single-device lock) | 한쪽 사용 종료 후 다른 쪽 시작 |
| 회사 보안 정책상 GitHub access 제한 가능 | 회사 GitHub Enterprise 또는 GitLab으로 marketplace 이전 |
| iCloud Drive 한글 폴더 NFD/NFC 문제 | git repo 사용 (UTF-8 정상) |

---

## 7. 추천 — 우선순위

**오늘 할 일**:
1. ✅ Phase 1 (Plugin marketplace) — **반드시** 셋업. 30분 투자로 양쪽 plugin 동기화 영구 해결
2. ⚠️ Phase 2 (iCloud) — 선택. GitHub repo로 이미 충분히 sync 됨
3. ✅ Phase 3 (memory.md + Notion) — **반드시** 활용. 대화 sync의 한계 보완

**다음 주**:
- LangSmith dashboard에서 양쪽 컴퓨터의 분석 trace를 같은 project로 통합 모니터링 (`LANGSMITH_PROJECT=stock-analysis` 양쪽 동일 설정으로 자동 통합)
- Claude Dispatch 시도 — 일부 task는 cross-device 작동 가능

## 8. 참고 자료

- [Claude Code Plugin Marketplaces 공식 docs](https://code.claude.com/docs/en/plugin-marketplaces)
- [Private Plugin Marketplace 구축 가이드 (Dominic Böttger)](https://dominic-boettger.com/blog/claude-code-private-plugin-marketplace-guide/)
- [Claude Cowork sync 한계 issue (#43698)](https://github.com/anthropics/claude-code/issues/43698)
- [Claude Dispatch 발표 (2026-03-19)](https://letsdatascience.com/news/anthropic-launches-claude-dispatch-for-multi-device-tasks-62d8c30d)
- [Claude Marketplace 디렉토리](https://claudemarketplaces.com/)
