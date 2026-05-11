---
name: analyze-blog
description: 네이버 블로그 URL을 받아 풀 분석 파이프라인 실행 → Top N 종목 통합 PDF 보고서 생성. URL 한 줄로 8단계 자동 실행 (수집 → thesis 추출 → 4-Analyst → 13명 페르소나 → Risk → Portfolio → Deep Research → PDF).
argument-hint: <블로그 URL> [--top-n N]
---

블로그 URL: $ARGUMENTS

## 🔒🔒🔒 표준 형식 — 사용자 confirm 완료 (절대 변경 금지)

새 분석은 **사용자가 2026-05-01에 canonical로 confirm한 형식**을 정확히 재현해야 합니다.

### Canonical Reference (md5 검증된 샘플)
- **`.canonical-samples/ranto28_2026-04-21_ECM_skinbooster/`** — 5개 PDF + overview.{md,pdf,pptx}
- 본 디렉토리의 구조·파일·내용을 **그대로 모방**하세요. 임의 변형 금지.

### Few-shot 참조 (analysis 디렉토리)
- **메르 ECM**: `.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/` (canonical)
- **의교창 lithium**: `.analysis-log/bloggers/doctordk/2026-04-29_lithium/`

### ❌ 금지 사항

- ❌ `analyses/` 디렉토리 사용
- ❌ 단일 `report.pdf` 출력
- ❌ 7-Role 분석 (13명 페르소나 + 4-Analyst가 표준)
- ❌ One-off scripts (plugin 호출만)
- ❌ 페르소나 5명만 (13명 풀 패널 필수)

## 8단계 분석 파이프라인

1. **수집**: 본문 + 댓글 스크래핑 (Naver mobile + cbox API)
2. **Thesis 추출**: 6-12개 검증 가능 thesis 분해 → `thesis_list.json`
3. **종목 식별**: 직간접 수혜 종목 추출 (top 5) → `stocks.json`
4. **4-Analyst 평가**: Macro/Industry/Empirical/Counter (확장 rationale 600+자) → `thesis_eval/all_aggregate.json`
5. **Market Data**: yfinance + DART/SEC EDGAR → `stocks.json`의 market_data 필드
6. **13명 페르소나 패널**: 풀 평가 + thesis_lens_applications → `persona_panel/{ticker}/aggregate.json + 13개 persona JSON`
7. **Risk + Portfolio**: vol_multiplier + signal score → `risk_limits.json`, `decisions.json`, `portfolio.json`
8. **Deep Research**: 산업·재무·시나리오·카탈리스트·리스크 → `deep_research/{ticker}.json`

## 빌드 명령 (필수 — 두 layer 모두 실행)

### Layer 1 — Per-stock Combined PDF (44p × 5)
```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_multi_stocks.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{date}_{slug} \
  --output-dir .analysis-log/.../reports/combined \
  --top-n 5
```
출력: `1_{ticker}_{name}_combined.pdf` (×5)

### Layer 2 — Multi-format Overview (MD + PDF + PPT)
```bash
python3 plugins/report-suite/skills/unified-builder/scripts/build_overview.py \
  --pipeline-dir .analysis-log/bloggers/{blogger}/{date}_{slug} \
  --output-dir .analysis-log/.../reports/overview \
  --formats md pdf pptx
```
출력: `overview.md` + `overview.pdf` + `overview.pptx`

### Validator — 분석 종료 시 의무 실행
```bash
python3 plugins/report-suite/skills/unified-builder/scripts/validate_format.py \
  .analysis-log/bloggers/{blogger}/{date}_{slug}
```
**28+ checks 모두 통과해야 분석 완료**. 누락 항목 발견 시 즉시 보완.

## ⚠ 주의 사항

- 블로그 글이 한글이면 분석도 한글로 진행
- 한국 종목 (.KS / .KQ) → DART API 자동 활성 (DART_API_KEY 설정 시)
- 미국 종목 → SEC EDGAR 자동 활성 (API 키 불필요)
- 미국 종목 뉴스 → NewsAPI/Finnhub 자동 (NEWSAPI_KEY/FINNHUB_KEY 설정 시)
- ETF 종목 (LIT 등)은 holdings + 섹터 breakdown 자동 추가
- PDF는 pdftocairo 후처리로 모든 PDF 뷰어 호환
- Layer 1 + Layer 2 모두 생성 — Layer 1만으로 종료 X
