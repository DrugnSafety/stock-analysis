# 000660.KS (SK하이닉스) — 분석 리포트

> 농구천재 — 1Q26 메모리/스토리지 5사 비교 (하이닉스·마이크론·샌디스크·시게이트·키옥시아)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-02  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 000660.KS (SK하이닉스) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/tosoha1/224273450422 |
| **분석 대상 종목 수** | 6개 |
| **추출 thesis 수** | 7개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 10 / Neutral 2 / Bear 1 |
| **Signal Score** | +0.692 |
| **평균 Confidence** | 0.78 |
| **최종 Decision** | BUY (542 주 (~$154,700,000)) |

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
| T01 | SK하이닉스는 1Q26 영업이익 마이크론 대비 약 +10bil USD (100억 달러) 우위, DRAM/NAND 매출 +50% — 그러나 시총은 비슷하게 상승. 코리아 디스카운트 명백 | factual | user_provided |
| T02 | 샌디스크 vs Seagate — 과거 동조하던 NAND vs HDD가 이번 분기 극단적으로 갈라짐. 샌디스크 Gross Profit Seagate 대비 3배. 그럼에도 시총 같이 상승 | factual | user_provided |
| T03 | 샌디스크 vs 키옥시아 (NAND JV 파트너) — 키옥시아 매출 +20-30% 우위 + 일본 생산 NAND 웨이퍼 6:4 키옥시아 우세. 그러나 시총은 샌디스크 우위 — 베인캐피탈 오버행 + 일본 디스카운트 + 미 | factual | user_provided |
| T04 | 메모리·NAND 사이클 진입 — AI 데이터센터 수요 + DDR5/HBM 가격 +85% YoY + NAND 가격 가속화. 사이클 mid-cycle 진입 | predictive | user_provided |
| T05 | 코리아 디스카운트 normalization 가능성 — 정부 밸류업 프로그램 + KOSPI Newrating + 외국인 매수 가속화 시 -30% gap 일부 회복 가능 | predictive | user_provided |
| T06 | Anchor pick: SK하이닉스 (이익 우위 + 코리아 디스카운트 회복 옵션) + 키옥시아 (매출 우위 + 일본 디스카운트). 단, 키옥시아는 베인 오버행 risk 존재 | predictive | user_provided |
| T07 | 마이크론·샌디스크는 미국 프리미엄 + HBM 지배력 수렴 narrative 가격화 — fair value or slightly overpriced | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 000660.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/persona_panel/000660.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/persona_panel/000660.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/deep_research/000660.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/tosoha1/2026-05-02_memory_storage_1Q26/reports/combined/01_000660.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 000660.KS \
  --output /tmp/000660.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-02_memory_storage_1Q26/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 000660.KS.json
│   ├── 005930.KS.json
│   ├── 285A.T.json
│   ├── MU.json
│   ├── SNDK.json
│   └── ... (+1 more)
├── meta.json
├── persona_panel/
│   ├── 000660.KS/
│   ├── 005930.KS/
│   ├── 285A.T/
│   ├── MU/
│   ├── SNDK/
│   └── ... (+2 more)
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

- `reports/combined/5_STX_Seagate_combined.pdf (519 KB)`
- `reports/combined/3_SNDK_Sandisk_combined.pdf (499 KB)`
- `reports/combined/1_000660.KS_SK하이닉스_combined.pdf (424 KB)`
- `reports/combined/4_MU_Micron_combined.pdf (511 KB)`
- `reports/combined/2_285A.T_키옥시아_combined.pdf (425 KB)`
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
