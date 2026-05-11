# 028670.KS (팬오션) — 분석 리포트

> DaeGurr — 탱커 운임 구조적 국면 분석

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-03-01  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 028670.KS (팬오션) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/daegurrr_/224199825373 |
| **분석 대상 종목 수** | 7개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 0명 |
| **최종 Decision** | BUY (19966 주 (~$105,420,700)) |

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
| T01 | VLCC 스팟 평균 운임(TCE)이 13만달러/일을 돌파, 2020년 4월 이후 최고. 곧 20만달러 가능 | factual | user_provided |
| T02 | 이란 전운으로 호르무즈 공급 불확실성, 세계 유조선 20%가 호르무즈 통과 — 운임 상방 압력 | factual | user_provided |
| T03 | Dark Fleet(이란 그림자 선단) 제재 본격화로 약 19%의 원유운반선 부족 → 공급자 우위 강화 | factual | user_provided |
| T04 | 장금상선이 VLCC 시장 장악 가속화 (올해에만 35-40척 추가 매입) | factual | user_provided |
| T05 | 탱커 운임 강세는 일회성 spike가 아닌 '구조적 흐름' | predictive | user_provided |
| T06 | 한국 상장사들의 탱커 이익비중이 작아 해외 탱커 스토리를 그대로 적용하기 어렵다 | factual | user_provided |
| T07 | 본업 실적까지 함께 고려한 선별적 투자가 권고됨 — 단, 재평가 여지는 늘어남 | normative | user_provided |
| T08 | 팬오션·장금상선이 탱커 비중을 확대하며 사업 다각화 진행 — 기존 벌크 집중 탈피 | factual | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 028670.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/persona_panel/028670.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/persona_panel/028670.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/deep_research/028670.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/daegurrr_/2026-03-01_tanker/reports/combined/01_028670.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 028670.KS \
  --output /tmp/028670.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-03-01_tanker/
├── README.md
├── decisions.json
├── ledger.jsonl
├── meta.json
├── persona_aggregates.json
├── persona_panel/
│   ├── panel_028670_KS/
│   ├── panel_FRO/
│   ├── panel_INSW/
├── portfolio.json
├── reports/
│   ├── R1_quant.pdf
│   ├── R2_persona_028670_KS.pdf
│   ├── R2_persona_FRO.pdf
│   ├── R2_persona_INSW.pdf
│   ├── R3_executive.pdf
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/R2_persona_INSW.pdf (273 KB)`
- `reports/R2_persona_FRO.pdf (272 KB)`
- `reports/R3_executive.pdf (192 KB)`
- `reports/R1_quant.pdf (304 KB)`
- `reports/R2_persona_028670_KS.pdf (273 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
