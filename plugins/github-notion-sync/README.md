# github-notion-sync

분석 완료 시 **GitHub repo + Notion database**에 자동 동기화하는 plugin.

`build_combined.py` **및 `build_multi_stocks.py`** (v0.5.1+)가 PDF 생성을 완료하면 post-build hook으로 자동 호출되며, local 분석 결과(meta·thesis·decisions·persona aggregate·README·PDF)를 GitHub에 push하고 Notion DB에 row를 생성/업데이트합니다.

> **v0.5.1 (2026-05-18) 변경 사항**:
> - `build_multi_stocks.py`에 post-build sync hook 추가 (이전: `build_combined.py` 전용 → 멀티 종목 분석 sync 누락 원인 해결)
> - `universal_concerns`가 str 리스트인 경우 처리 (`'str' object has no attribute 'get'` KeyError 방지)
> - `meta.json`의 `blog_author`/`blogger`가 dict 객체일 때 nickname/blog_id 자동 추출
> - PDF Report URL을 ticker별 매칭으로 정확히 선택 (이전: 첫 PDF 고정 → 모든 종목 동일 URL)
>
> **NOTION_TOKEN 미설정 시 한계**: Notion 직접 API 미작동 → sync_analysis.py가 `mcp_payload_ready` 상태만 반환합니다. 이 경우 Cowork/Claude Code 세션에서 MCP `notion-create-pages` 호출이 필요합니다. 자동화하려면 `.env`에 `NOTION_TOKEN=secret_...` 추가 (https://www.notion.so/profile/integrations).

## 셋업

### 1. Notion (이미 완료됨)

- Database: [📊 주식 분석 Hub](https://www.notion.so/b689c03e9bc6481b8c732ca17729f8db)
- Data Source ID: `7aa5488f-99e9-4ca0-afef-4ac110435597` (`.env`에 저장됨)
- 동기화 방식: Notion MCP (Cowork/Claude Code 환경에서 자동) 또는 `NOTION_TOKEN` 직접 호출

### 2. GitHub (사용자 작업 필요)

#### Step 1 — Personal Access Token 발급

1. https://github.com/settings/tokens?type=beta (Fine-grained PAT 권장)
2. **Name**: `stock-analysis-sync`
3. **Repository access**: All repositories (또는 새로 만들 repo 선택)
4. **Permissions** → Repository permissions:
   - **Contents**: Read and write
   - **Metadata**: Read-only (자동 포함)
   - **Administration**: Read and write (private repo 생성 시 필요)
5. **Generate token** 클릭 → `github_pat_...` 복사

#### Step 2 — `.env`에 추가

```bash
GITHUB_TOKEN=github_pat_...
GITHUB_OWNER=DrugnSafety           # GitHub 사용자명 (대소문자 정확히)
GITHUB_REPO=stock-analysis         # 새 repo 이름 (자동 생성됨)
```

> **사전 설정 완료** — `GITHUB_OWNER=DrugnSafety`, `GITHUB_REPO=stock-analysis`는 이미 `.env`에 저장되어 있습니다. PAT 값(`GITHUB_TOKEN=`)만 채워넣으면 즉시 작동합니다.

#### Step 3 — 첫 sync (BTU + LNG 백필)

```bash
# 첫 호출 시 자동으로 private repo 생성 + 파일 push
python3 plugins/github-notion-sync/scripts/sync_analysis.py \
    --pipeline-dir .analysis-log/standalone/2026-04-30_BTU_Peabody_Energy \
    --ticker BTU

python3 plugins/github-notion-sync/scripts/sync_analysis.py \
    --pipeline-dir .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy \
    --ticker LNG
```

## 자동 동작 (Post-build hook)

`build_combined.py` 또는 `build_multi_stocks.py`로 PDF를 생성하면 자동으로 sync가 트리거됩니다:

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
    --ticker BTU ... --output combined.pdf

# 출력:
# [combined] saved: combined.pdf (507,366 bytes)
# [sync] post-build hook → GitHub + Notion (pipeline_dir=2026-04-30_BTU_Peabody_Energy)
# [github] creating new private repo: DrugnSafety/stock-analysis (첫 호출 시만)
# [github] pushed 11 files
# [notion] upserted page: https://www.notion.so/...
```

비활성화하려면: `DISABLE_SYNC=1 python3 build_combined.py ...`

## 동기화되는 데이터

### GitHub repo
파일 단위 push (idempotent — 기존 파일은 SHA 기반 update):
- `meta.json`, `stocks.json`, `thesis_list.json`
- `decisions.json`, `portfolio.json`, `risk_limits.json`
- `README.md` (분석별 instruction)
- `persona_panel/{ticker}/aggregate.json`
- `deep_research/{ticker}.json`
- `reports/combined/*.pdf` (binary)

### Notion DB row
한 분석 = 한 row. 같은 Ticker로 재실행 시 update (upsert):
| 필드 | 값 |
|---|---|
| Ticker | TITLE — 종목 코드 |
| Company | 회사명 |
| Date | 분석 일자 |
| Sector | LNG Export / Coal Mining / ... (자동 normalize) |
| Analysis Type | standalone / blogger |
| Blogger | 블로거명 (blogger 분석 시) |
| Verdict | lean_bullish / neutral / lean_bearish |
| Signal Score | (-1, +1) |
| Avg Confidence | (0, 1) |
| Decision | buy / hold / sell |
| Bull / Neutral / Bear | 13명 페르소나 카운트 |
| N Thesis | 추출 thesis 수 |
| Implicit Thesis | Phase 5 자동 추출 활용 여부 |
| Top Concerns | universal_concerns 상위 3개 |
| GitHub URL | repo 내 분석 디렉토리 |
| PDF Report | combined PDF 직접 링크 |
| Local Path | `.analysis-log` 상대 경로 |
| Last Synced | (자동) last_edited_time |

## 트러블슈팅

### GitHub 401 Unauthorized
- `GITHUB_TOKEN` 만료 또는 권한 부족
- Fine-grained PAT이면 repo에 access 부여되어 있는지 확인

### Notion 동기화 안 됨 (status: skipped)
- `NOTION_DATA_SOURCE_ID`가 `.env`에 있는지 확인
- Cowork/Claude Code 환경이면 MCP가 자동 작동 — `NOTION_TOKEN` 불필요

### PDF가 너무 큰 (>50MB)
- GitHub Contents API는 단일 파일 100MB 제한. 통상 PDF는 500KB 수준이라 안전.
- 50MB 이상이면 Git LFS 또는 release asset으로 별도 처리 권장.
