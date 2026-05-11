# NVDA (엔비디아) — 분석 리포트

> 욕망과 두려움이 만드는 시장, 그리고 멀티플의 본질

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-10  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | NVDA (엔비디아) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/doctordk/224280707641 |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 4 / Neutral 3 / Bear 3 |
| **Signal Score** | +0.077 |
| **평균 Confidence** | 0.00 |
| **최종 Decision** | HOLD (? 주 (~$0)) |

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
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |
| ? |  | factual | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker NVDA \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/persona_panel/NVDA/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/persona_panel/NVDA \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/deep_research/NVDA.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-10_market_multiples_essay/reports/combined/01_NVDA_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py NVDA \
  --output /tmp/NVDA_fs.json
```

## 5. 디렉토리 구조

```
2026-05-10_market_multiples_essay/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 000660.KS.json
│   ├── 005930.KS.json
│   ├── AAPL.json
│   ├── BRK-B.json
│   ├── NVDA.json
├── meta.json
├── persona_panel/
│   ├── 000660.KS/
│   ├── 005930.KS/
│   ├── AAPL/
│   ├── BRK-B/
│   ├── NVDA/
│   └── ... (+1 more)
├── portfolio.json
├── raw_post.json
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

- `reports/combined/4_NVDA_엔비디아_combined.pdf (450 KB)`
- `reports/combined/3_005930.KS_삼성전자_combined.pdf (333 KB)`
- `reports/combined/1_BRK-B_버크셔_해서웨이_combined.pdf (365 KB)`
- `reports/combined/5_000660.KS_SK하이닉스_combined.pdf (330 KB)`
- `reports/combined/2_AAPL_애플_combined.pdf (395 KB)`
- `reports/overview/overview.pdf (39 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
