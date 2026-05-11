# LNG (Cheniere Energy) — 분석 리포트

> Cheniere Energy (LNG) — 미국 LNG Export 1위, Henry Hub Macro 노출 standalone 분석

**분석 종류**: Standalone (사용자 지정 종목)  ·  
**분석 일자**: 2026-05-11  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | LNG (Cheniere Energy) |
| **섹터** | LNG Export Operator |
| **분석 종류** | standalone |
| **분석 대상 종목 수** | 1개 |
| **추출 thesis 수** | 12개 (implicit thesis 자동 추출 활용) |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 6 / Neutral 6 / Bear 1 |
| **Signal Score** | +0.385 |
| **평균 Confidence** | 0.58 |
| **최종 Decision** | BUY (290 주 (~$70,000,000)) |

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

이 분석은 **Implicit Thesis 자동 추출** (v0.5.0)을 활용했습니다 (sources: catalyst, risk, user_provided).

| ID | Claim | Type | Source |
|---|---|---|---|
| T1 | 미국 헨리허브 천연가스 가격은 LNG 수출능력(터미널·운반선) 한계로 국제시세와 디커플링되어 있음 | factual | user_provided |
| T2 | 2026 하반기부터 Plaquemines/Golden Pass/Corpus Christi Stage 3 등 신규 수출터미널 가동으로 미국 LNG 수출능력 30%+ 확대 → 헨리허브 가격 국제시세 수렴 + LNG운반선 | predictive | user_provided |
| T3 | Cheniere Energy는 신규 capacity 가동의 1차 수혜자 (Sabine Pass + Corpus Christi 합산 capacity 45+ MTPA, 미국 LNG export 1위) | factual | user_provided |
| T4 | EU TTF vs Henry Hub 가격차 21달러는 비정상적으로 크며, 미국 LNG 수출 확대로 수렴 압력 증가 | predictive | user_provided |
| T5 | Corpus Christi Stage 3 Train 1 상업 가동이(가) 실현되면, 시장은 본 종목의 valuation을 reprice할 가능성이 높음 (추가 5+ MTPA capacity → 영업현금흐름 +$1.5 | predictive | catalyst |
| T6 | Q2/Q3 2026 어닝 발표이(가) 실현되면, 시장은 본 종목의 valuation을 reprice할 가능성이 높음 (신규 train 가동 시 가이던스 raise 기대) | predictive | catalyst |
| T7 | 유럽 LNG 수요 회복이(가) 실현되면, 시장은 본 종목의 valuation을 reprice할 가능성이 높음 (TTF-HH 가격차 확대 시 SPA margin 확대) | predictive | catalyst |
| T8 | Cheniere Stage 4 FID (Final Investment Decision)이(가) 실현되면, 시장은 본 종목의 valuation을 reprice할 가능성이 높음 (장기 capacity 추가 — long- | predictive | catalyst |
| T9 | 본 종목의 thesis는 다음 리스크가 현실화되지 않는다는 가정에 의존: Henry Hub 가격 상승 (수출 마진 압박) — 발생 시 Tolling fee 모델이라 직접 노출은 낮지만 spot 매출 비중 감소 | conditional | risk |
| T10 | 본 종목의 thesis는 다음 리스크가 현실화되지 않는다는 가정에 의존: 글로벌 LNG 공급 과잉 (Qatar, Australia, US 동시 capacity 확대) — 발생 시 2027 이후 LNG 가격 하방 압력 | conditional | risk |
| T11 | 본 종목의 thesis는 다음 리스크가 현실화되지 않는다는 가정에 의존: 유럽 LNG 수요 둔화 (러시아 PNG 복귀 또는 재생에너지 가속) — 발생 시 spot 매출 감소 | conditional | risk |
| T12 | 본 종목의 thesis는 다음 리스크가 현실화되지 않는다는 가정에 의존: 탄소세/Methane Tax 등 ESG 규제 강화 — 발생 시 장기적으로 LNG 수요 plateau 가능성 | conditional | risk |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker LNG \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/persona_panel/LNG/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/persona_panel/LNG \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/deep_research/LNG.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/standalone/2026-05-11_LNG_Cheniere_Energy/reports/combined/01_LNG_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py LNG \
  --output /tmp/LNG_fs.json
```

## 5. 디렉토리 구조

```
2026-05-11_LNG_Cheniere_Energy/
├── README.md
├── decisions.json
├── deep_research/
│   ├── LNG.json
├── meta.json
├── persona_panel/
│   ├── LNG/
│   ├── _all_aggregates.json
├── portfolio.json
├── reports/
│   ├── combined/
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/01_LNG_Cheniere_Energy_combined.pdf (453 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **Implicit Thesis 자동 추출 (v0.5.0)**: 이 분석은 standalone (블로그 글 없음)이므로 implicit thesis가 자동 추출되었습니다. deep_research의 catalysts → predictive thesis, risks → conditional thesis로 변환됨. 실제 블로거의 1차 분석이 없으므로 narrative 깊이는 제한적.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
