# ALB (Albemarle) — 분석 리포트

> 의교창 — 리튬 구조적 강세 분석 (2차전지)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-04-29  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | ALB (Albemarle) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/doctordk/224269642921 |
| **분석 대상 종목 수** | 10개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 10 / Neutral 2 / Bear 1 |
| **Signal Score** | +0.692 |
| **평균 Confidence** | 0.74 |
| **최종 Decision** | BUY (806789 주 (~$154,000,000)) |

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
| T01 | UBS가 2027 배터리급 탄산리튬 가격 전망을 톤당 $42,000으로 +47% 상향, 2026 +17% 상향 | factual | user_provided |
| T02 | ESS가 '선택'에서 '필수 인프라'로 변화 — 전력망 안정성·재생에너지 확대·데이터센터 전력 수요 동시 작용 | predictive | user_provided |
| T03 | 전기차 보급률이 임계 도달, 수요가 선형 → 비선형 가속화. 중국 가격 경쟁력으로 '대체재' → '기본재' 전환 | predictive | user_provided |
| T04 | 트럭 전동화로 단위당 리튬 소비량 급증 — 승용차 대비 훨씬 큰 배터리 + 시장 과소평가 단계 | predictive | user_provided |
| T05 | 리튬 생산업체들이 공격적 증설을 하지 않고 있음 — 나트륨 배터리 불확실성 때문 | factual | user_provided |
| T06 | 나트륨 배터리는 리튬을 완전 대체할 수 없음 — 에너지 밀도·효율·적용범위 모두 제한 | factual | user_provided |
| T07 | 리튬 시장이 '공급이 가격을 결정' → '수요가 가격을 밀어 올리는' 구조로 구조적 이동, 가격이 먼저 폭등하며 공급을 강제로 끌어냄 | predictive | user_provided |
| T08 | 전통적 사이클 투자 접근('올랐으니 꺾인다')이 통하지 않는 구간 — '왜 올랐는가'가 핵심 | normative | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker ALB \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/persona_panel/ALB/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/persona_panel/ALB \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/deep_research/ALB.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-04-29_lithium/reports/combined/01_ALB_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py ALB \
  --output /tmp/ALB_fs.json
```

## 5. 디렉토리 구조

```
2026-04-29_lithium/
├── README.md
├── README_v2.md
├── decisions.json
├── deep_research/
│   ├── 003670.KS.json
│   ├── 005490.KS.json
│   ├── 006400.KS.json
│   ├── ALB.json
│   ├── LIT.json
│   └── ... (+1 more)
├── ledger.jsonl
├── meta.json
├── persona_aggregates.json
├── persona_panel/
│   ├── 003670.KS/
│   ├── 005490.KS/
│   ├── 006400.KS/
│   ├── ALB/
│   ├── LIT/
│   └── ... (+3 more)
├── portfolio.json
├── portfolio_stub.json
├── r2_meta.json
├── reports/
│   ├── 005490.KS_POSCO홀딩스_combined.pdf
│   ├── R1_quant.pdf
│   ├── R2_persona_POSCO_13.pdf
│   ├── R3_executive.pdf
│   └── ... (+11 more)
├── risk_limits.json
├── stocks.json
├── stocks.json.placeholder_backup
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/R3_executive.pdf (216 KB)`
- `reports/005490.KS_POSCO홀딩스_combined.pdf (609 KB)`
- `reports/R1_quant.pdf (356 KB)`
- `reports/R2_persona_POSCO_13.pdf (376 KB)`
- `reports/combined_v5_dart/posco_dart_test.pdf (3688 KB)`
- `reports/combined_v4_clean/1_005490.KS_POSCO홀딩스_combined.pdf (525 KB)`
- `reports/combined_v6/posco_v6_test.pdf (469 KB)`
- `reports/combined_v3_clean/4_SQM_SQM_combined.pdf (700 KB)`
- `reports/combined_v3_clean/5_LIT_Global_X_리튬_ETF_combined.pdf (711 KB)`
- `reports/combined_v3_clean/3_ALB_Albemarle_combined.pdf (704 KB)`
- `reports/combined_v3_clean/1_005490.KS_POSCO홀딩스_combined.pdf (710 KB)`
- `reports/combined_v3_clean/2_006400.KS_삼성SDI_combined.pdf (702 KB)`
- `reports/combined_v4_final/4_SQM_SQM_combined.pdf (3546 KB)`
- `reports/combined_v4_final/5_LIT_Global_X_리튬_ETF_combined.pdf (3751 KB)`
- `reports/combined_v4_final/3_ALB_Albemarle_combined.pdf (3675 KB)`
- `reports/combined_v4_final/1_005490.KS_POSCO홀딩스_combined.pdf (3684 KB)`
- `reports/combined_v4_final/2_006400.KS_삼성SDI_combined.pdf (3532 KB)`
- `reports/combined_v6_final/4_SQM_SQM_combined.pdf (461 KB)`
- `reports/combined_v6_final/5_LIT_Global_X_리튬_ETF_combined.pdf (475 KB)`
- `reports/combined_v6_final/3_ALB_Albemarle_combined.pdf (465 KB)`
- `reports/combined_v6_final/1_005490.KS_POSCO홀딩스_combined.pdf (469 KB)`
- `reports/combined_v6_final/2_006400.KS_삼성SDI_combined.pdf (462 KB)`
- `reports/combined_v4_outline/posco_outlined.pdf (3674 KB)`
- `reports/combined_v2/4_SQM_SQM_combined.pdf (662 KB)`
- `reports/combined_v2/5_LIT_Global_X_리튬_ETF_combined.pdf (660 KB)`
- `reports/combined_v2/3_ALB_Albemarle_combined.pdf (661 KB)`
- `reports/combined_v2/1_005490.KS_POSCO홀딩스_combined.pdf (665 KB)`
- `reports/combined_v2/2_006400.KS_삼성SDI_combined.pdf (664 KB)`
- `reports/combined/4_SQM_SQM_combined.pdf (662 KB)`
- `reports/combined/5_LIT_Global_X_리튬_ETF_combined.pdf (660 KB)`
- `reports/combined/3_ALB_Albemarle_combined.pdf (661 KB)`
- `reports/combined/1_005490.KS_POSCO홀딩스_combined.pdf (533 KB)`
- `reports/combined/2_006400.KS_삼성SDI_combined.pdf (664 KB)`
- `reports/overview/overview.pdf (58 KB)`
- `reports/combined_v3/4_SQM_SQM_combined.pdf (707 KB)`
- `reports/combined_v3/5_LIT_Global_X_리튬_ETF_combined.pdf (717 KB)`
- `reports/combined_v3/3_ALB_Albemarle_combined.pdf (711 KB)`
- `reports/combined_v3/1_005490.KS_POSCO홀딩스_combined.pdf (717 KB)`
- `reports/combined_v3/2_006400.KS_삼성SDI_combined.pdf (709 KB)`
- `reports/combined_v4/2_006400.KS_삼성SDI_combined.tmp.pdf (702 KB)`
- `reports/combined_v4/3_ALB_Albemarle_combined.pdf (682 KB)`
- `reports/combined_v4/1_005490.KS_POSCO홀딩스_combined.pdf (710 KB)`
- `reports/combined_v4/2_006400.KS_삼성SDI_combined.pdf (77 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
