# 290650.KQ (엘앤씨바이오) — 분석 리포트

> 메르 — 스킨부스터 미용 시장의 돌연변이, ECM의 정체는?

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-04-21  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 290650.KQ (엘앤씨바이오) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/ranto28/224259581475 |
| **분석 대상 종목 수** | 6개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 3 / Neutral 5 / Bear 5 |
| **Signal Score** | -0.154 |
| **평균 Confidence** | 0.62 |
| **최종 Decision** | SELL_ALL (-7567 주 (~$140,000,000)) |

## 2. 보고서 섹션 흐름 (v0.5.0)

이 분석으로 생성된 PDF는 다음 섹션 순서를 따릅니다 (per-stock combined PDF):

| # | 섹션 | 데이터 소스 |
|---|---|---|
| 1 | Cover | meta.json + persona aggregate |
| 2 | Company Intro | stocks.json (yfinance live) |
| 3 | **Deep Research** (산업 + 재무 + 카탈리스트/리스크) | deep_research/{ticker}.json |
| 4 | **Financial Statements US-GAAP** (5Y annual + 5Q quarterly) | SEC EDGAR / DART (auto live fetch) |
| 5 | News Timeline (중립 제외 + 월별 +/- bar chart) | DART/SEC + NewsAPI.org/.ai/Finnhub |
| 6 | Executive Brief + Thesis List | thesis_list.json (+ implicit thesis if standalone) |
| 7 | R1 Quant Anchor | stocks.json + risk_limits.json |
| 8 | R2 Persona Panel + Thesis × Persona Matrix | persona_panel/{ticker}/*.json |
| 9 | R3 Decision Section | decisions.json + portfolio.json |
| 10 | (선택) ETF Holdings · Reverse DCF · Subagent Debate | 자동 |
| 11 | Appendix (용어 사전) | static |

## 3. 추출된 Thesis

| ID | Claim | Type | Source |
|---|---|---|---|
| T01 | ECM 스킨부스터는 의료기기가 아닌 '인체조직'으로 분류되어 임상시험을 건너뛰고 유통되고 있음. 미국 FDA에서는 면역반응 최소화 의무 — 한국은 규제 공백 | factual | user_provided |
| T02 | ECM 원재료는 인체 기증자(사체)의 진피를 냉동건조 분쇄해 분말화한 것 — 본래 화상 환자 재건 등 치료 목적이었던 것이 고가 미용 시술에 사용되어 윤리 risk 큼 | factual | user_provided |
| T03 | 한국 미용 의료기기·필러·바이오 sector는 1~4세대 스킨부스터·보톡스·HIFU 등 다양한 카테고리 보유 — ECM은 그 중 가장 회색지대 카테고리. 다른 카테고리는 imminent regulatory risk  | predictive | user_provided |
| T04 | 한국 미용 시장은 internal demand 정점 통과 + 중국·동남아 export 가속화 단계. 1조원+ 규모, 5년 CAGR 12-15%. 다만 ECM 카테고리 negative news 시 sector mult | predictive | user_provided |
| T05 | 엘앤씨바이오 (290650.KQ) 같은 ECM 사업 직접 영업 회사는 해당 카테고리 비중에 따라 imminent regulatory risk 노출 — 핵심 monitoring 대상 | predictive | user_provided |
| T06 | 리쥬란(PN) 제조사 파마리서치(214450.KQ)는 4세대 스킨부스터 main player — ECM 카테고리와 차별화 (PN은 의료기기 분류, 임상시험 통과). 메르의 부정적 framing이 단기 sentimen | predictive | user_provided |
| T07 | 휴젤(145020.KQ)·메디톡스(086900.KQ) 등 보툴리눔 톡신 회사는 ECM과 무관 — 메르의 글이 sector multiple에 sentiment risk 줄 수 있으나 fundamental impact  | predictive | user_provided |
| T08 | 클래시스(214150.KQ) 등 미용 의료기기 (HIFU·RF) 제조사는 ECM과 무관 + 미국·중국 등 글로벌 export 가속화 단계 — 메르의 글로 인한 직접 영향 없음 | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 290650.KQ \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/persona_panel/290650.KQ/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/persona_panel/290650.KQ \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/deep_research/290650.KQ.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-04-21_ECM_skinbooster/reports/combined/01_290650.KQ_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 290650.KQ \
  --output /tmp/290650.KQ_fs.json
```

## 5. 디렉토리 구조

```
2026-04-21_ECM_skinbooster/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 086900.KQ.json
│   ├── 145020.KQ.json
│   ├── 214150.KQ.json
│   ├── 214450.KQ.json
│   ├── 290650.KQ.json
├── meta.json
├── persona_panel/
│   ├── 086900.KQ/
│   ├── 145020.KQ/
│   ├── 214150.KQ/
│   ├── 214450.KQ/
│   ├── 290650.KQ/
│   └── ... (+1 more)
├── portfolio.json
├── reports/
│   ├── combined/
│   ├── overview/
├── risk_limits.json
├── stocks.json
├── stocks.json.placeholder_backup
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/2_214450.KQ_파마리서치_combined.pdf (442 KB)`
- `reports/combined/3_145020.KQ_휴젤_combined.pdf (441 KB)`
- `reports/combined/1_290650.KQ_엘앤씨바이오_combined.pdf (442 KB)`
- `reports/combined/4_086900.KQ_메디톡스_combined.pdf (441 KB)`
- `reports/combined/5_214150.KQ_클래시스_combined.pdf (441 KB)`
- `reports/overview/overview.pdf (61 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
