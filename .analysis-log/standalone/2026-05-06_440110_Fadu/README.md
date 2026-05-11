# 440110.KQ (FADU Inc.) — 분석 리포트

> 파두 (440110.KQ) — 의교창 SSD 컨트롤러 500억 공급계약 분석

**분석 종류**: Standalone (사용자 지정 종목)  ·  
**분석 일자**: 2026-05-06  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 440110.KQ (FADU Inc.) |
| **분석 종류** | standalone |
| **블로거** | 의교창 (doctordk) |
| **블로그 URL** | https://blog.naver.com/doctordk/224276811815 |
| **분석 대상 종목 수** | 1개 |
| **추출 thesis 수** | 12개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 4 / Neutral 4 / Bear 4 |
| **Signal Score** | +0.000 |
| **평균 Confidence** | 0.62 |

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
| T01 | 단일 공급계약 500억 = 2025년 매출 924억의 54.11% 비중 — 외형보다 실적의 구조적 불확실성 제거가 핵심 | factual | user_provided |
| T02 | SSD에서 진짜 마진은 NAND가 아닌 컨트롤러 — 공급 사이클·가격 변동성에서 자유로운 IP·소프트웨어성 부품 | factual | user_provided |
| T03 | SSD 컨트롤러는 lock-in 구조 — 한 번 채택되면 제품 사이클(2-4년) 동안 반복 공급 | predictive | user_provided |
| T04 | 공시 문구 '3년 내 동종계약 이행 이력 존재' = 신규 고객이 아닌 검증된 기존 고객의 재계약 | factual | user_provided |
| T05 | 선급금 10% 수령은 단순 공급자가 아닌 '선택된 파트너' 인증 — 고객이 리스크를 일부 부담 | factual | user_provided |
| T06 | 납품 후 다음 주 결제 = 운전자본·재고 리스크 제로 구조, 현금흐름 가시성 극대화 | factual | user_provided |
| T07 | AI 인프라 진짜 병목은 GPU·DRAM뿐 아니라 스토리지(SSD), 그중 컨트롤러가 가장 IP·기술집약적 레이어 | predictive | user_provided |
| T08 | 파두의 산업 내 포지션이 '부품 회사' → '데이터 흐름 제어 레이어'로 격상 = 멀티플 re-rating 근거 | predictive | user_provided |
| T09 | 단일 공시가 (1) 고객 유지능력 + (2) 반복 가능한 매출 구조 + (3) 시스템 내 필수 포지션 3축을 동시 입증 | normative | user_provided |
| T10 | 시장은 늦게 반응한다 — 숫자를 보고 나서야 구조를 이해 → 현재 주가 하락은 미스프라이싱 기회 | predictive | user_provided |
| T11 | 좋은 회사의 정의 = 실적이 좋아질 수밖에 없는 구조를 만드는 회사, 파두는 그 구조 완성 신호 | normative | user_provided |
| T12 | 이런 시그널은 한 번이 아니라 반복된다 — 향후 추가 공급계약·동일 고객 추가 발주 가능성 | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 440110.KQ \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/persona_panel/440110.KQ/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/persona_panel/440110.KQ \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/deep_research/440110.KQ.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-06_440110_Fadu/reports/combined/01_440110.KQ_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 440110.KQ \
  --output /tmp/440110.KQ_fs.json
```

## 5. 디렉토리 구조

```
2026-05-06_440110_Fadu/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 440110.KQ.json
├── meta.json
├── persona_panel/
│   ├── 440110.KQ/
│   ├── _all_aggregates.json
├── portfolio.json
├── reports/
│   ├── combined/
│   ├── overview.md
├── risk_limits.json
├── sources/
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/01_440110_Fadu_combined.pdf (320 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
