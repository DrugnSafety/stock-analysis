---
name: notion-page-builder
description: Notion 페이지 본문(markdown), DB row 페이지 콘텐츠, PDF 첨부, 메인 페이지 + 하위 페이지 구성을 자동화하는 skill. 'Notion 페이지 보강', 'PDF 첨부', '메인 페이지 구성', 'DB 페이지 본문 작성' 등의 키워드에 트리거.
---

# Notion Page Builder

분석 시스템의 Notion 페이지 빌딩을 표준화하는 skill. 단순 row 생성 (notion_client.py)을 넘어 **페이지 본문 markdown 작성, PDF 첨부, 메인 페이지 hub 구성, 하위 페이지 (README·Methodology) 자동 생성**을 통합 제공.

## 책임 분리

| 역할 | 모듈 |
|---|---|
| DB row 메타데이터 upsert | `scripts/notion_client.py` (기존) |
| Row 페이지 본문 (markdown 변환) | **`scripts/page_builder.py` (이 skill)** |
| PDF GitHub raw URL 첨부 | **`scripts/page_builder.py`** |
| 메인 페이지 + 하위 페이지 구성 | **`scripts/page_builder.py`** |
| 분석별 README → Notion blocks 변환 | **`scripts/markdown_to_notion.py`** |

## 사용

### 1. DB row 페이지 본문에 분석 README 작성

```bash
python3 scripts/page_builder.py write-row \
    --ticker LNG \
    --readme-path .analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/README.md \
    --pdf-github-url https://github.com/DrugnSafety/stock-analysis/blob/main/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/reports/combined/01_LNG_Cheniere_Energy_combined.pdf
```

### 2. 메인 페이지 hub 구성

```bash
python3 scripts/page_builder.py build-hub \
    --main-page-id 2d402c77-e2c9-800b-ba24-c9d354d4c0aa
```

생성되는 콘텐츠:
- README 요약 (시스템 소개 + 핵심 기능)
- Version history (v0.5.0 → v0.1.0)
- DB linked view (📊 주식 분석 Hub)
- 하위 페이지 링크 (README · 분석 Methodology)

### 3. 하위 페이지 2개 자동 생성

```bash
python3 scripts/page_builder.py build-subpages \
    --main-page-id 2d402c77-e2c9-800b-ba24-c9d354d4c0aa \
    --readme-path README.md
```

생성:
- `README` 페이지 — root README.md 전체 변환
- `분석 Methodology` 페이지 — 8단계 파이프라인 · 13명 페르소나 · 5Y/5Q US-GAAP 재무 분석 상세

### 4. 한 번에 전체 보강 (BTU + LNG 등 모든 row + 메인 페이지)

```bash
python3 scripts/page_builder.py full-rebuild \
    --main-page-id 2d402c77-e2c9-800b-ba24-c9d354d4c0aa
```

## MCP 모드 vs Direct API 모드

이 skill은 두 환경 모두 지원:

1. **Cowork / Claude Code MCP** — Notion MCP 도구를 활용 (NOTION_TOKEN 불필요)
   - `mcp__<notion>__notion-update-page` 호출
   - 페이지 content 필드에 markdown 직접 전달
2. **Direct API** — `NOTION_TOKEN` + REST API 호출 (.env 설정 필요)
   - `PATCH /v1/blocks/{block_id}/children` 호출
   - markdown → Notion blocks 변환

## Notion-flavored Markdown 가이드

Notion MCP가 받는 markdown은 일반 markdown + Notion 확장:
- `## Heading` → Heading 2
- `### Heading` → Heading 3
- 표는 `| col | col |` 일반 markdown 형식
- 임베드: `[external-pdf](url)` 또는 `![file-preview](url)`
- DB linked view: `<linked-db-view ds-id="..."/>` (메인 페이지에서 사용)

## Anti-hallucination

- 페이지 ID는 항상 fetch 결과 또는 사용자 직접 제공만 사용 — 추측 금지
- DB row 페이지 본문은 source README.md 또는 분석 데이터 기반으로만 생성 (LLM 자유 작문 금지)
- PDF URL은 GitHub repo에 실제 push된 파일만 링크 (broken link 방지)
