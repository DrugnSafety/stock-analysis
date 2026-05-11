---
name: overview-builder
description: Layer 2 — 모든 종목 정보를 단일 문서로 통합하는 multi-format overview 생성 (Markdown + PDF + PowerPoint). Layer 1 (per-stock 44p PDFs)에 대한 portfolio-level summary. Email·Slack·Notion 공유, presentation 적합. 사용자가 "통합 요약", "PPT 자료", "Markdown export", "한 페이지 overview" 등을 언급하면 트리거.
---

# Layer 2 Overview Builder — Multi-format Output

Layer 1의 per-stock deep PDFs를 보완하는 portfolio-level overview를 3가지 format으로 동시 생성:

- **`overview.md`** — Markdown (Email/Slack/Notion/GitHub 공유 적합)
- **`overview.pdf`** — Markdown 기반 PDF (모든 종목 통합 5-15p)
- **`overview.pptx`** — 6-8 slides PowerPoint (presentation 적합)

## 호출

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
  --output-dir .../reports/overview \
  --formats md pdf pptx
```

`--formats`은 선택적 — 일부만 생성 가능 (예: `--formats md pptx`).

## 출력 구조

### Markdown
1. Cover (제목·블로거·분석일·종목 수)
2. Executive Summary (한 줄 요약 + 추출된 thesis 6개)
3. Top 3 Picks 표 (signal 절대값 기준)
4. 종목별 Verdict 종합 표 (모든 종목)
5. 종목별 핵심 분석 (페르소나 highlight + risks)
6. Portfolio Allocation 권고 표
7. Top 5 Risk 요인
8. 분석 메타데이터

### PowerPoint (6-8 slides, 13.33×7.5 widescreen)
1. **Cover** — 블로거·thesis 1-line + Top 3 banner
2. **Thesis** — 핵심 thesis 3-box
3. **Top 3 Picks** — 3-column detail
4. **Verdict 종합 표** — 11 row × 8 column
5. **Portfolio Allocation** — bar chart by ticker
6. **Risk + 결론** — 2-column

### PDF (5-15 pages)
- Markdown을 WeasyPrint로 PDF 변환
- pdftocairo 후처리로 한글 폰트 호환성 보장

## Layer 1 vs Layer 2

| 항목 | Layer 1 (per-stock) | Layer 2 (overview) |
|---|---|---|
| 출력 | 5 PDFs × 44-52p | 3 files (md + pdf + pptx) |
| 분석 깊이 | 13 페르소나 + 4-Analyst 풀 | Top 3 highlight + 표 |
| 활용 | 종목별 진입 결정 | Portfolio decision + 공유 |
| 권장 사용 | 깊이 우선 | 한눈 우선 |

## 자동 통합

`commands/analyze-blog.md` slash command가 **Layer 1 + Layer 2 모두 자동 실행**.

## 의존성
- `python-pptx` (PPT 생성)
- `markdown` (MD → HTML 변환)
- `weasyprint` (HTML → PDF)
- `pdftocairo` (CJK 폰트 호환 후처리)
