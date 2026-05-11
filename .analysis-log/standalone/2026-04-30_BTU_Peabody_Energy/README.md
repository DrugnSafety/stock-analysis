# BTU (Peabody Energy) — 분석 리포트

> Peabody Energy (BTU) — 미국 최대 석탄 생산자 standalone 분석

**분석 종류**: Standalone (사용자 지정 종목)  ·  
**분석 일자**: 2026-04-30  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | BTU (Peabody Energy) |
| **분석 종류** | standalone |
| **블로그 URL** | (standalone analysis — not blog-driven) |
| **분석 대상 종목 수** | 4개 |
| **추출 thesis 수** | 6개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 6 / Neutral 4 / Bear 3 |
| **Signal Score** | +0.231 |
| **평균 Confidence** | 0.63 |
| **최종 Decision** | HOLD (2900 주 (~$70,000,000)) |

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
| T01 | AI 데이터센터·산업 전력 수요로 미국 thermal coal 수요가 2025-2027 baseline 시나리오 +5-8% 증가 — gas peaker 부족 + 풍력·태양광 capacity factor 한계 | predictive | user_provided |
| T02 | Metallurgical coal (제철 원료탄)은 인도·동남아 철강 capa 증설로 2025-2030 수요 +12-15%. 호주·미국이 main producer — BTU의 NAPP·CAPP 자산 직접 수혜. | predictive | user_provided |
| T03 | BTU는 NCAV (cash + working capital) 대비 시가총액이 매우 가까운 deep value — Buffett·Burry style 'cigar butt'. 부채 축소 + 자기주식 매입 지속. | factual | user_provided |
| T04 | ESG/climate divestment 압력은 2024-2025 정점 통과. Trump 2기 정책 + EU 천연가스 의존도 reset (러우전쟁 후) + 인도·중국 지속 수요로 'coal terminal decli | predictive | user_provided |
| T05 | BTU는 LNG 수출 partnership을 통해 'coal-to-LNG transition arbitrage' 가능 — 자체 mining 자산을 미래 LNG export terminal 인프라와 연계. | predictive | user_provided |
| T06 | Tail risk — 이상 기후 (mild winter), 가스 가격 $2/MMBtu 이하 지속, 태양광·ESS 가격 추가 -30% 시 thermal coal 수요 -15-20% 가능. | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker BTU \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/persona_panel/BTU/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/persona_panel/BTU \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/deep_research/BTU.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-04-30_BTU_Peabody_Energy/reports/combined/01_BTU_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py BTU \
  --output /tmp/BTU_fs.json
```

## 5. 디렉토리 구조

```
2026-04-30_BTU_Peabody_Energy/
├── README.md
├── decisions.json
├── deep_research/
│   ├── BTU.json
├── meta.json
├── persona_panel/
│   ├── BTU/
│   ├── _all_aggregates.json
├── portfolio.json
├── reports/
│   ├── BTU_Peabody_Energy_combined.pdf
│   ├── BTU_Peabody_v2_SEC.pdf
│   ├── combined_v2/
├── risk_limits.json
├── stocks.json
├── stocks.json.placeholder_backup
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/BTU_Peabody_v2_SEC.pdf (463 KB)`
- `reports/BTU_Peabody_Energy_combined.pdf (441 KB)`
- `reports/combined_v2/01_BTU_Peabody_Energy_combined.pdf (495 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
