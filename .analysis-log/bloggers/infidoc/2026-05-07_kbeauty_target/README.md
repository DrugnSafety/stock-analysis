# 460870.KQ (SMCG Co., Ltd.) — 분석 리포트

> 인피의 — K뷰티는 맞았다, 투자자의 표적이 틀렸다 (조건부 병목 thesis)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-07  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 460870.KQ (SMCG Co., Ltd.) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/infidoc/224277478142 |
| **분석 대상 종목 수** | 3개 |
| **추출 thesis 수** | 11개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 0 / Neutral 0 / Bear 0 |
| **Signal Score** | +0.000 |
| **평균 Confidence** | 0.61 |
| **최종 Decision** | BUY (? 주 (~$0)) |

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
| T01 | K뷰티 산업 자체는 2025년 수출 114억달러(+12.3% YoY)로 사상 최대를 경신했고, 2026년 분기·월별 데이터도 우상향 중. 산업 fundamental은 살아있고 미국 포함 수출처 다변화 진행 중 | factual | user_provided |
| T02 | 화장품 브랜드 비즈니스는 구조적 한계가 있음. 브랜드 충성도 낮고 유행 빠르며, 한국콜마·코스맥스 같은 ODM이 유사 포뮬러를 여러 브랜드에 동시 제공 가능. 산업이 자라도 특정 브랜드 초과수익은 오래 유지 안 됨 | factual | user_provided |
| T03 | ODM(한국콜마·코스맥스)은 K뷰티 수출 성장의 수혜를 받았고 2025 사상 최대 실적 — 한국콜마 매출 2.7조·영업이익 2,396억, 코스맥스 매출 2.4조·영업이익 1,958억. 다만 ODM은 결국 제조업으로, | factual | user_provided |
| T04 | 플라스틱 용기는 (1) 금형·사출 진입장벽 낮아 범용화, (2) 산업 총량이 아닌 포맷 믹스(튜브/펌프/에어리스) 기준 수혜 분화, (3) 인디 브랜드 확대로 단가 민감도 증가, (4) 글로벌 가격 경쟁 직접 노출  | factual | user_provided |
| T05 | K뷰티 sector에는 절대적 병목(반도체 노광장비·데이터센터 전력 같은)이 약하지만, 4가지 조건(기술·인증 장벽 / 고객 락인 / 대체 공급자 부재 / 규제 진입 장벽)이 결합되는 순간 병목성이 강해지는 '조건부 | predictive | user_provided |
| T06 | 유리용기는 조건부 병목의 가장 강력한 후보. (1) EU PPWR(2025-02 발효, 2026-08 일반 적용)이 플라스틱에 더 엄격한 규제 환경 조성 — 유리에 상대적 우위, (2) 프리미엄 유리 패키징은 외관· | predictive | user_provided |
| T07 | 에스엠씨지(460870.KQ)는 화장품 유리용기 토탈 패키지 솔루션 전문 상장사 — 전기용해로 기반 생산, 파유리 70%+ 배합, GRS 인증, 안성공장 일평균 50톤·24시간 자동제병, 프리몰드 750종+부자재 1 | factual | user_provided |
| T08 | 에스엠씨지 1Q26 EBITDA를 단순 연환산하면 ~100억원 전후. 자산차입금비율 27% 양호. 현재 EV/EBITDA 8배대 초중반 — 펀더멘탈 개선 + 하반기 자동화·인건비 절감 leverage + 낮은 밸류에 | predictive | user_provided |
| T09 | 마이크로캡 약점도 명확 — 한국 마이크로캡은 싸고 좋은데 안 오르는 상태가 길게 지속될 수 있음. (1) 스팩 합병 직후 주가 약세 패턴, (2) 2026 시장이 반도체·AI에 자금 극단 집중 — 관심 바깥 마이크로 | predictive | user_provided |
| T10 | 글로벌 자본은 이미 한국 화장품 패키징 공급망을 구조적 자산군으로 검증한 바 있음 — TPG가 2023년 삼화를 인수 후 2025년 KKR에 7,330억원(약 5.3억달러)에 매각, 2년 만에 2.2배 수익. 삼화가 | factual | user_provided |
| T11 | 투자 표적의 우선순위: ① 유리용기·인증 ODM 등 '조건부 병목' segment (HIGH conviction, 에스엠씨지 등) > ② ODM 대장(코스맥스·한국콜마) — 검증된 segment지만 제조업 multi | normative | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 460870.KQ \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/persona_panel/460870.KQ/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/persona_panel/460870.KQ \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/deep_research/460870.KQ.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/infidoc/2026-05-07_kbeauty_target/reports/combined/01_460870.KQ_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 460870.KQ \
  --output /tmp/460870.KQ_fs.json
```

## 5. 디렉토리 구조

```
2026-05-07_kbeauty_target/
├── README.md
├── body.txt
├── decisions.json
├── deep_research/
│   ├── 161890.KS.json
│   ├── 192820.KS.json
│   ├── 460870.KQ.json
├── meta.json
├── persona_panel/
│   ├── 161890.KS/
│   ├── 192820.KS/
│   ├── 460870.KQ/
│   ├── _all_aggregates.json
├── portfolio.json
├── raw.html
├── reports/
│   ├── combined/
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/3_161890.KS_KolmarKorea_combined.pdf (367 KB)`
- `reports/combined/1_460870.KQ_SMCG_combined.pdf (364 KB)`
- `reports/combined/2_192820.KS_Cosmax_combined.pdf (362 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
