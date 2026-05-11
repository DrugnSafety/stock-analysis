# 035900.KQ (JYP Ent.) — 분석 리포트

> ricemankr — JYP Ent., K-POP 글로벌화 전략 및 밸류에이션 분석

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-09  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 035900.KQ (JYP Ent.) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/ricemankr/224279694166 |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 10 / Neutral 3 / Bear 0 |
| **Signal Score** | +0.769 |
| **평균 Confidence** | 0.72 |
| **최종 Decision** | BUY (3505 주 (~$210,000,000)) |

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
| T01 | JYP Ent.의 핵심 캐시카우는 '글로벌 현지화(Globalization by Localization)' 라인업 — NEXZ(일본)·VCHA(북미)·KickFlip(다국적)·뻔푸소년CIIU(중국)·dodree(여성 | factual | user_provided |
| T02 | 트와이스 북미 투어, 스트레이키즈 SKZOO 팝업스토어 등 고마진 MD·IP 라이선싱 사업이 신보 발매 공백기에도 이익 방어력 입증 — 단순 용역 매출 의존도 축소 | factual | user_provided |
| T03 | Target P/E 24x 적용 시 적정주가 88,000~92,000원 — 현재가 60,100~63,000원 대비 +40~50% 상승여력. 2026E 지배주주순이익 1,290~1,310억원 가정 | predictive | user_provided |
| T04 | JYP Ent.는 무차입 경영(순차입금/자기자본 -60%대) + 자사주 6.8% 보유로 재무 건전성·거버넌스 우수 — 한국 mid-cap 엔터 sector 내 최상위 | factual | user_provided |
| T05 | 2026 2분기부터 NMIXX·ITZY·KickFlip 등 신인·저연차 아티스트 연속 컴백 → 본격 실적 turnaround 구간 진입. 2026 하반기 스트레이키즈 신보·북미투어 재개 시 추정치 상향 여지 | predictive | user_provided |
| T06 | 스트레이키즈 핵심 멤버 군 입대 시점(2027말~2028초)이 다가옴 — 저연차 그룹(NMIXX·NEXZ·KickFlip)이 공백을 메울 성장 속도를 증명 못 할 시 sector multiple 하락 + 장기 val | predictive | user_provided |
| T07 | K-POP sector 전반 — JYP·HYBE·SM·YG 4사가 2024~2025 신인 IP 풀 확장 cycle 진입 → 2026~2027 동시 모멘텀. 글로벌 fan engagement 플랫폼(디어유 Bubble | predictive | user_provided |
| T08 | 한국 엔터 sector multiple은 미국 음반·미디어 peer 대비 30~40% premium — disruptive K-POP global penetration thesis 반영. 단, 글로벌 macro sl | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 035900.KQ \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/persona_panel/035900.KQ/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/persona_panel/035900.KQ \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/deep_research/035900.KQ.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ricemankr/2026-05-09_JYP_Ent_valuation/reports/combined/01_035900.KQ_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 035900.KQ \
  --output /tmp/035900.KQ_fs.json
```

## 5. 디렉토리 구조

```
2026-05-09_JYP_Ent_valuation/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 035900.KQ.json
│   ├── 041510.KQ.json
│   ├── 122870.KQ.json
│   ├── 352820.KS.json
│   ├── 376300.KQ.json
├── meta.json
├── persona_panel/
│   ├── 035900.KQ/
│   ├── 041510.KQ/
│   ├── 122870.KQ/
│   ├── 352820.KS/
│   ├── 376300.KQ/
│   └── ... (+1 more)
├── portfolio.json
├── posts/
│   ├── 224279694166.json
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

- `reports/combined/2_352820.KS_HYBE_combined.pdf (477 KB)`
- `reports/combined/4_122870.KQ_YG_combined.pdf (476 KB)`
- `reports/combined/1_035900.KQ_JYP_Ent_combined.pdf (484 KB)`
- `reports/combined/3_041510.KQ_SM_combined.pdf (475 KB)`
- `reports/combined/5_376300.KQ_DearU_combined.pdf (476 KB)`
- `reports/overview/overview.pdf (84 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
