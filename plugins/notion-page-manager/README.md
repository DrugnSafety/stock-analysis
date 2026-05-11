# notion-page-manager

Notion 페이지·database 관리 전용 plugin.

`github-notion-sync`이 **DB row 생성/업데이트** (메타데이터)만 담당한다면, 이 plugin은:

1. **DB row 페이지 본문**에 분석 README markdown을 풀로 write
2. **메인 페이지** ("주식분석 by Claude") 자동 구성 — README 요약 + version history + DB view
3. **하위 페이지** 생성 — README · Analysis Methodology
4. **PDF 첨부** (GitHub Release public asset 또는 Notion file block)

## 주요 use case

### Case 1 — 분석 sync 후 페이지 본문 보강

```bash
# 1단계: github-notion-sync로 DB row 생성/업데이트 (메타데이터)
python3 plugins/github-notion-sync/scripts/sync_analysis.py \
    --pipeline-dir .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy \
    --ticker LNG

# 2단계: notion-page-manager로 DB row 페이지에 README 본문 write
python3 plugins/notion-page-manager/scripts/write_page_content.py \
    --ticker LNG \
    --markdown-path .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/README.md
```

### Case 2 — 메인 페이지 + 하위 페이지 일괄 구성

```bash
python3 plugins/notion-page-manager/scripts/build_main_page.py
python3 plugins/notion-page-manager/scripts/create_subpages.py
```

### Case 3 — PDF 첨부

private GitHub repo의 PDF는 인증 없이 fetch 불가. 두 가지 방법:

**Option A (권장) — GitHub Release public asset**:
```bash
python3 plugins/notion-page-manager/scripts/attach_pdf.py \
    --ticker LNG \
    --pdf-path .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/reports/combined/01_LNG_Cheniere_Energy_combined.pdf \
    --method github_release
```

**Option B — repo를 public으로 변경 후 raw URL embed**:
사용자가 GitHub에서 직접 settings → repo visibility → public 변경. 이후:
```bash
python3 plugins/notion-page-manager/scripts/attach_pdf.py --ticker LNG --method raw_url
```

## 페이지 구조

```
주식분석 by Claude (main page)
├── 📖 README 페이지
├── 🔬 Analysis Methodology 페이지
└── 📊 주식 분석 Hub (DB)
    └── 각 row → individual page (Ticker + 메타 + README 본문 + PDF link)
```
