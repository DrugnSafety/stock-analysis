# 보고서 형식 표준 (Report Format Standard)

> **목적**: 새 세션에서도 동일한 형식의 보고서가 생성되도록 표준을 명시. 모든 분석은 본 문서의 형식을 따라야 함.

---

## 1. 차이점 분석 (왜 형식이 달라졌는가?)

### 현재 표준 (이 시스템의 정식 형식)
- **출력 단위**: Top 5 종목 각각 독립 PDF (per-stock combined)
- **각 PDF 구조**: 44-52 페이지, 470KB 내외
- **분석 깊이**: 13명 풀 페르소나 + 4-Analyst (확장 rationale 600+자) + Deep Research
- **디렉토리 구조**:
  ```
  .analysis-log/bloggers/{blogger}/{date}_{slug}/
  ├── meta.json
  ├── thesis_list.json
  ├── thesis_eval/all_aggregate.json
  ├── stocks.json
  ├── persona_panel/{ticker}/aggregate.json
  ├── persona_panel/{ticker}/{persona_id}.json (13개)
  ├── persona_panel/_all_aggregates.json
  ├── deep_research/{ticker}.json
  ├── risk_limits.json
  ├── decisions.json
  ├── portfolio.json
  └── reports/combined/{idx}_{ticker}_{name}_combined.pdf
  ```

### 새 세션 (2026-04-23 헨리허브 LNG, 2026-05-01 ECM)
- **출력 단위**: 단일 PDF + MD + PPT (모든 종목 통합)
- **각 출력**: 12-15 페이지 PDF, 13KB MD, 8 slide PPT
- **분석 깊이**: 7-Role (Fundamentals/Technical/News/Sentiment + Bull/Bear + Trader/Risk)
- **디렉토리 구조**:
  ```
  .analysis-log/bloggers/{blogger}/{date}_{slug}/
  ├── analyses/
  ├── reports/
  │   ├── report.md
  │   ├── report.html
  │   ├── report.pdf
  │   ├── report_raw.pdf
  │   ├── report.pptx
  │   └── build_pptx.py
  └── meta.json
  ```

### 핵심 차이
| 항목 | 현재 표준 | 새 세션 |
|---|---|---|
| 분석 깊이 | 13 페르소나 + 4-Analyst | 7-Role |
| 출력 파일 수 | 5 PDFs (per-stock) | 6 files (1 doc, multi-format) |
| 종목별 깊이 | 44-52p 각 | ~2p 각 |
| 페르소나 panel | ✓ (13명) | ✗ (없음) |
| Deep Research 섹션 | ✓ | 부분 |
| 통합 viewing 편의 | △ (5개 분리) | ✓ (1개) |
| 다중 format (PPT/MD) | ✗ | ✓ |
| 회사명 한글 표기 | ✓ | ✓ |
| Plugin reusable | ✓ | ✗ (one-off scripts) |

---

## 2. 표준 형식 lock-in 방안

### A. **Few-shot 샘플 디렉토리** (이 방식 적용)
- 기준 샘플: `.analysis-log/bloggers/doctordk/2026-04-29_lithium/`
- 새 세션이 시작될 때 `CLAUDE.md`가 자동 로드되며 이 디렉토리를 참조
- 시스템 prompt에 "기존 의교창 lithium 분석 결과 = canonical format"으로 명시

### B. **SKILL.md 강화**
- `analyze-blog.md` slash command + `unified-builder` SKILL.md에 명시:
  - "**MUST** 사용: persona_panel + thesis_eval + deep_research 디렉토리 구조"
  - "**MUST** 호출: `build_combined.py` per-stock + `build_multi_stocks.py` for top 5"
- 새 세션 LLM이 임의로 다른 구조를 만들지 않도록 explicit guard

### C. **Multi-format 추가** (새 세션의 장점 흡수)
- 기존 per-stock PDF는 그대로 유지 (deep dive)
- **신규**: portfolio overview PPT + Markdown (tactical summary)
- 두 layer 동시 생성:
  - **Layer 1 (Deep)**: 5 PDFs × 44p (각 종목별 상세)
  - **Layer 2 (Summary)**: 1 PPT (8-10 slides) + 1 Markdown (모든 종목 overview)

### D. **자동 검증 hook**
- 분석 종료 시 file structure validator 실행
- 필수 파일 누락 시 warning + auto-create

---

## 3. 표준 디렉토리 구조 (이대로 따를 것)

```
.analysis-log/bloggers/{blogger}/{date}_{slug}/
├── meta.json                      # 필수: blog_url, title, date, blogger
├── thesis_list.json               # 필수: 6-12 theses with importance/timeframe
├── stocks.json                    # 필수: top 5 stocks with market_data
│
├── thesis_eval/
│   └── all_aggregate.json         # 필수: 4-Analyst (Macro/Industry/Empirical/Counter)
│
├── persona_panel/
│   ├── _all_aggregates.json       # 필수: 모든 ticker의 aggregate
│   └── {ticker}/
│       ├── aggregate.json         # 필수: 13명 verdict + style_split + universal_concerns
│       └── {persona_id}.json      # 필수: 13개 persona 개별 평가 + thesis_lens_applications
│
├── deep_research/
│   └── {ticker}.json              # 필수: industry, financials, scenarios, catalysts, risks
│
├── risk_limits.json               # 필수: vol_multiplier 기반 position 한도
├── decisions.json                 # 필수: signal_score → BUY/HOLD/SELL
├── portfolio.json                 # 필수: paper portfolio state
│
└── reports/
    ├── combined/                  # Layer 1 — per-stock deep PDFs
    │   ├── 1_{ticker}_{name}_combined.pdf
    │   └── ... (5개)
    └── overview/                  # Layer 2 — multi-format summary
        ├── overview.md
        ├── overview.pdf
        └── overview.pptx
```

---

## 4. Layer별 사용 가이드

### Layer 1 — Deep PDFs (per-stock)
- **언제**: 종목별 진입 결정 직전, 페르소나별 reasoning 필요시
- **호출**:
  ```bash
  python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
    --output-dir .../reports/combined --top-n 5
  ```
- **출력**: 5 × 44p combined PDFs (R1+R2+R3+Deep Research)

### Layer 2 — Overview Summary (multi-format)
- **언제**: 전체 portfolio 결정 + email/slack 공유 + presentation
- **호출**:
  ```bash
  python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
    --pipeline-dir .analysis-log/bloggers/{blogger}/{slug} \
    --output-dir .../reports/overview \
    --formats md pdf pptx
  ```
- **출력**: overview.md (10-15p) + overview.pdf + overview.pptx (8-10 slides)

---

## 5. Layer 2 (Overview) 표준 구조

### Markdown
1. **Cover** — 블로거·글 제목·분석일·종목 수
2. **Executive Summary** — 메르 thesis 3-line + Top 3 picks 표
3. **메르 본문 핵심 사실** — verbatim 인용 + 핵심 수치
4. **Catalyst Timeline** — 향후 6-12개월 예정 이벤트
5. **종목별 verdict 요약 표** — 11개 row × 8 columns
6. **Portfolio Allocation** — 추천 비중 (그룹별)
7. **핵심 위험 요인** — Top 5 risks
8. **결론 + 다음 단계**
9. **메타** — 분석 방법·데이터 소스·면책

### PPT (8-10 slides, 13.33×7.5 widescreen)
1. Cover (블로거·thesis 1-line + Top 3)
2. 메르 thesis 3-box (디커플링·Catalyst·결론)
3. 현재 진행 중 supply 이벤트 (heatmap)
4. Catalyst timeline 표
5. Top 3 picks (3-column)
6. 전체 verdict 요약 표 (11 rows)
7. Portfolio allocation (비중 그래프)
8. Risk 요인 + 결론

### PDF (10-15p)
- Markdown을 WeasyPrint + pdftocairo로 PDF 생성

---

## 6. 형식 일관성 자동 검증

```bash
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py \
  .analysis-log/bloggers/{blogger}/{slug}
```

- 필수 파일 존재 확인
- thesis 개수, persona 13명 풀 평가, deep_research 모든 ticker 등 schema 검증
- 누락 시 명확한 에러 메시지

---

## 7. 향후 새 세션 시작 시 — Best Practice

```
사용자 → "/analyze-blog <URL>"
   ↓
Claude → CLAUDE.md 로드 → 본 표준 인지
   ↓
Claude → 기존 의교창 lithium 샘플 디렉토리 참조 (few-shot)
   ↓
Claude → 동일 디렉토리 구조 + 동일 PDF 양식으로 분석
   ↓
Output: Layer 1 (per-stock 5 PDFs) + Layer 2 (PPT/MD overview)
```

---

## 8. 결론

- **현재 시스템 = 표준** (deep + reusable plugin)
- **새 세션 형식의 장점 = Multi-format (PPT/MD)** 흡수해서 Layer 2로 추가
- **Few-shot 샘플 + SKILL.md 강화 + 자동 검증**으로 일관성 보장

본 문서는 모든 새 분석의 baseline이며, `CLAUDE.md`에서 자동 참조됩니다.
