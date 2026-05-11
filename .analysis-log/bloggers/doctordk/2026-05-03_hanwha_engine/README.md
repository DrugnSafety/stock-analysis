# 082740.KS (한화엔진 (Hanwha Engine)) — 분석 리포트

> 의교창 — 한화엔진: AI 데이터센터 BTM 가스엔진 신사업 + 조선 슈퍼사이클 결합 분석

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-03  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 082740.KS (한화엔진 (Hanwha Engine)) |
| **섹터** | Marine Engine / Power Generation |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/doctordk/224273991216 |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 7 / Neutral 4 / Bear 2 |
| **Signal Score** | +0.385 |
| **평균 Confidence** | 0.68 |
| **최종 Decision** | LEAN_BULLISH (485 주 (~$0)) |

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
| T01 | 한화엔진이 데이터센터 BTM 가스엔진 신사업 진출 — 그룹사 한화에너지와의 수직 협업 구조 확립 | factual | user_provided |
| T02 | 미국 송배전망 포화로 BTM(Behind-the-Meter) 자체 발전 방식이 확산되며 가스엔진 수요가 구조적으로 증가 | factual | user_provided |
| T03 | 2016년 철수했던 4행정 엔진 사업이 데이터센터 수요로 재가동 — 과거 비경제 영역이 이제는 고수익 시장 | factual | user_provided |
| T04 | 매출 전망: 2026년 1.6조 → 2027년 2.8조 → 2028년 ~3조 — 데이터센터향 매출이 2027년부터 본격 반영 | predictive | user_provided |
| T05 | Wärtsilä가 미국 데이터센터 대규모 가스엔진 공급계약 선점 — HD현대중공업도 진입 = 경쟁 격화 | factual | user_provided |
| T06 | 기존 선박엔진 cash cow가 동시에 호황 — 조선 슈퍼사이클 + 친환경 이중연료 엔진 가격 상승세 | factual | user_provided |
| T07 | AI 시대 인프라는 반도체에 국한되지 않음 — '연산'(GPU)에서 '전력'(엔진·발전기)로 가치체인 확장 | predictive | user_provided |
| T08 | [보조] '군포엔진유니버스 Go Go' = AI 인프라스트럭처 — 의교창 본인 단정적 직관 (한화엔진 강한 확신 시그널) | normative | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 082740.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/persona_panel/082740.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/persona_panel/082740.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/deep_research/082740.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-03_hanwha_engine/reports/combined/01_082740.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 082740.KS \
  --output /tmp/082740.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-03_hanwha_engine/
├── README.md
├── _build_combined_lite.py
├── _canonical_082740.log
├── _generate_personas.py
├── _generate_risk_decisions.py
├── _layer1_build.log
├── _md_to_pdf.py
├── _overview_build.log
├── _p082740.log
├── _pdf_log.txt
├── _pptx2.log
├── _regenerate_deep_research.py
├── decisions.json
├── deep_research/
│   ├── 012450.KS.json
│   ├── 034020.KS.json
│   ├── 082740.KS.json
│   ├── 329180.KS.json
│   ├── WRTBY.json
├── meta.json
├── persona_panel/
│   ├── 012450.KS/
│   ├── 012450_KS/
│   ├── 034020.KS/
│   ├── 034020_KS/
│   ├── 082740.KS/
│   └── ... (+5 more)
├── portfolio.json
├── reports/
│   ├── combined/
│   ├── overview/
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/v3_034020.KS_두산에너빌리티.pdf (391 KB)`
- `reports/combined/canonical_test_WRTBY.pdf (463 KB)`
- `reports/combined/v3_082740.KS_한화엔진.pdf (394 KB)`
- `reports/combined/1_WRTBY_Wärtsilä_Oyj_Abp_combined.pdf (522 KB)`
- `reports/combined/5_034020.KS_두산에너빌리티_combined.pdf (459 KB)`
- `reports/combined/v3_WRTBY_Wartsila.pdf (433 KB)`
- `reports/combined/v3_012450.KS_한화에어로스페이스.pdf (390 KB)`
- `reports/combined/2_082740.KS_한화엔진_combined.pdf (495 KB)`
- `reports/combined/3_012450.KS_한화에어로스페이스_combined.pdf (457 KB)`
- `reports/combined/1_WRTBY_Wärtsilä_ADR__combined.pdf (457 KB)`
- `reports/combined/1_WRTBY_Wärtsilä_combined.pdf (480 KB)`
- `reports/combined/4_329180.KS_HD현대중공업_combined.pdf (457 KB)`
- `reports/combined/v3_329180.KS_HD현대중공업.pdf (388 KB)`
- `reports/overview/overview.pdf (70 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
