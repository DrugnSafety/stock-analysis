# 077970.KS (STX엔진 (STX Engine)) — 분석 리포트

> 의교창 — STX엔진: 4행정 중속엔진 데이터센터 On-site 발전 재정의 (한화엔진 후속 series)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-04  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 077970.KS (STX엔진 (STX Engine)) |
| **섹터** | Marine Engine / Power Generation (4-stroke medium-speed) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/doctordk/224274833178 |
| **분석 대상 종목 수** | 1개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 3 / Neutral 6 / Bear 4 |
| **Signal Score** | -0.077 |
| **평균 Confidence** | 0.60 |
| **최종 Decision** | HOLD / WATCH (? 주 (~$0)) |

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
| T01 | 전력망 부족·송배전 병목으로 데이터센터의 'On-site(BTM) 자체 발전' 방식이 구조적 수요로 부상 | factual | user_provided |
| T02 | 4행정 중속엔진 산업이 조선 기자재 → 데이터센터 인프라 공급으로 영역 확장 — Wärtsilä·HD현대중공업이 선례 입증 | factual | user_provided |
| T03 | STX엔진은 국내 2위 + 선박용·육상 발전용 엔진 경험 보유 = 데이터센터용 전력 공급 시장 진입의 구조적 위치 확보 | factual | user_provided |
| T04 | 6MW vs 20MW 스펙 갭은 본질이 아님 — 4행정 중속엔진의 경쟁력은 '모듈화 병렬 구성' (Wärtsilä도 동일 경로) | interpretive | user_provided |
| T05 | 민수산업부 가동률 23.6% 유휴 capacity → 데이터센터 수요 add-on 시 가동률 상승 = 고정비 레버리지 → ROE/멀티플 동시 상승 | factual | user_provided |
| T06 | 2028년 EPS 50% 이상 상향, ROE 약 29.7% 추정 — 구조적 수요·가동률 레버리지·re-rating 3요소 동시 작용 구간 | predictive | user_provided |
| T07 | 현재 주가 급등은 '가능성에 대한 인식' 단계 — 완전한 멀티플 확장은 ① 실제 수주 → ② 실적 확인 → ③ 산업 분류 재평가 3단계 sequence 필요 | predictive | user_provided |
| T08 | 조선 기자재 → 전력 인프라 공급자로 산업 재분류 시 적용 멀티플 프레임 자체 변경 — LS electric·산일전기 BE 밸류체인 진입 사례가 선례 | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 077970.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/persona_panel/077970.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/persona_panel/077970.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/deep_research/077970.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_STX_engine/reports/combined/01_077970.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 077970.KS \
  --output /tmp/077970.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-04_STX_engine/
├── README.md
├── _generate_personas.py
├── decisions.json
├── deep_research/
│   ├── 077970.KS.json
├── meta.json
├── persona_panel/
│   ├── 077970.KS/
│   ├── _all_aggregates.json
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

- `reports/combined/1_077970.KS_STX엔진_combined.pdf (379 KB)`
- `reports/overview/overview.pdf (65 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
