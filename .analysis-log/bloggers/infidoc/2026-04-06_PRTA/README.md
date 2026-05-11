# PRTA (Prothena Corporation plc) — 분석 리포트

> 인피의 — PRTA(Prothena) 분석

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-04-06  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | PRTA (Prothena Corporation plc) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/infidoc/224242468542 |
| **분석 대상 종목 수** | 1개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 0명 |
| **최종 Decision** | BUY (7281 주 (~$73,106)) |

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
| T01 | PRTA는 Elan(티사브리 개발사)에서 2012년 분사된 신경과학 바이오텍으로 핵심 R&D 인력이 그대로 남아있다 | factual | user_provided |
| T02 | 22-23년 $70+ 더블탑 후 약 3년에 걸쳐 90% 가량 하락, 최근 바닥에서 2배 회복 중 | factual | user_provided |
| T03 | 자체 신약 birtamimab의 AFFIRM-AL 3상이 2025년 5월 1차 평가지표 충족 실패 — 자체 임상 자산은 사실상 끝남 | factual | user_provided |
| T04 | Prasinezumab(Roche, 파킨슨병 α-synuclein 항체)이 PADOVA 2b 1차 미스했으나 레보도파 하위그룹 HR=0.79·p=0.0438 강한 신호로 Phase 3 진입 결정, AD/PD 2026 | factual | user_provided |
| T05 | Roche의 prasinezumab peak sales target은 $3.5B CHF (연간 매출 6조원). 미국에서만 파킨슨 환자 100-110만, 글로벌 1천만+ | predictive | user_provided |
| T06 | PRTA는 prasinezumab으로 이미 $135M 수령, 향후 규제·판매 마일스톤 $620M + high-teens 로열티 + 미국 공동판촉 옵션 보유 | factual | user_provided |
| T07 | PRTA pipeline 전체 (Roche prasinezumab + BMS PRX005·PRX012 + Novo coramitug)로 멀티카탈리스트 모멘텀 — 빅파마 3사가 수천억 비용을 태워 임상 우선순위로 진행 | factual | user_provided |
| T08 | 한국 바이오텍의 'L/O 마일스톤 선반영 + 플랫폼 프리미엄' 식 기형적 valuation 대비, PRTA 같은 미국 임상 후기 자산이 압도적 가치 | normative | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker PRTA \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/persona_panel/PRTA/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/persona_panel/PRTA \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/deep_research/PRTA.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-04-06_PRTA/reports/combined/01_PRTA_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py PRTA \
  --output /tmp/PRTA_fs.json
```

## 5. 디렉토리 구조

```
2026-04-06_PRTA/
├── README.md
├── decisions.json
├── ledger.jsonl
├── meta.json
├── persona_aggregates.json
├── persona_panel/
│   ├── panel_PRTA/
├── portfolio.json
├── r2_meta.json
├── reports/
│   ├── R1_quant.pdf
│   ├── R2_persona_PRTA_13.pdf
│   ├── R3_executive.pdf
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/R3_executive.pdf (184 KB)`
- `reports/R1_quant.pdf (268 KB)`
- `reports/R2_persona_PRTA_13.pdf (304 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
