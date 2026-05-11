---
description: 분석 디렉토리를 GitHub + Notion에 수동으로 sync (post-build hook이 실패했거나 백필 시)
---

# /sync-github-notion

## 용도

`build_combined.py`의 post-build hook이 실패했거나, 기존 분석을 GitHub + Notion에 백필(backfill)할 때 사용.

## 사용법

```
/sync-github-notion <pipeline-dir> <ticker>
```

예시:
```
/sync-github-notion .analysis-log/standalone/2026-04-30_BTU_Peabody_Energy BTU
/sync-github-notion .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy LNG
```

## 동작

1. 분석 디렉토리에서 meta·thesis·persona aggregate·decisions를 읽어 metadata payload 생성
2. **GitHub** (private repo로 push):
   - 핵심 JSON 파일들 + README.md + PDF 보고서
   - 같은 파일이 있으면 SHA 기반 update (idempotent)
   - `GITHUB_TOKEN` 미설정 시 skip
3. **Notion** ("주식 분석 Hub" DB에 row 생성/업데이트):
   - 같은 Ticker가 있으면 update, 없으면 create
   - Cowork/Claude Code 환경에서 MCP 자동 사용
   - `NOTION_TOKEN` 직접 호출도 지원

## 셋업 확인

```bash
python3 plugins/github-notion-sync/scripts/github_client.py status
python3 plugins/github-notion-sync/scripts/notion_client.py status
```

## 백필 — 모든 기존 분석을 일괄 sync

```bash
for d in .analysis-log/standalone/*/ .analysis-log/bloggers/*/*/; do
  if [ -f "$d/meta.json" ]; then
    ticker=$(python3 -c "import json; m=json.load(open('$d/meta.json')); s=json.load(open('$d/stocks.json')) if __import__('os').path.exists('$d/stocks.json') else []; print(m.get('ticker') or (s[0].get('ticker') if s else ''))")
    if [ -n "$ticker" ]; then
      python3 plugins/github-notion-sync/scripts/sync_analysis.py --pipeline-dir "$d" --ticker "$ticker"
    fi
  fi
done
```

## 트러블슈팅

- `GitHub 401`: `.env`의 `GITHUB_TOKEN` 만료. 새로 발급: https://github.com/settings/tokens
- `NOTION_DATA_SOURCE_ID not set`: `.env`에 추가 (값: `7aa5488f-99e9-4ca0-afef-4ac110435597`)
- 자세한 셋업: `plugins/github-notion-sync/README.md`
