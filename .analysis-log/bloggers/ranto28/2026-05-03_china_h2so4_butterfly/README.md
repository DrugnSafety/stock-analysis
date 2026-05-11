# 010130.KS (고려아연) — 분석 리포트

> 메르 — 중국의 황산수출 금지가 일으키는 나비효과 A/S

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-03  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 010130.KS (고려아연) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/ranto28/224273477400 |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 7개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 10 / Neutral 2 / Bear 1 |
| **Signal Score** | +0.692 |
| **평균 Confidence** | 0.78 |
| **최종 Decision** | BUY (182 주 (~$154,700,000)) |

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
| T01 | 중국 2026-05-01 황산 수출 공식 금지 — 글로벌 황산 시장 23% 점유 + 칠레 의존 50% 즉각 영향 | factual | user_provided |
| T02 | 한국·일본은 아연·구리 제련 부산물로 황산 생산 — 한국 2025 순수출 238만톤. 황산 가격 +200% 시 추가 마진 발생 | factual | user_provided |
| T03 | 칠레 산화광 구리 제련 직격탄 — Cu 1톤당 황산 4톤 필요. 글로벌 구리 -17% 가능 (Goldman Sachs) | predictive | user_provided |
| T04 | 인도네시아 HPAL 니켈 제련 압박 — 원가 40%+ 황산. 인도네시아 니켈 가격 +30% 가능 | predictive | user_provided |
| T05 | 황산 전용 탱크선 300척 한정 + 장기계약 — 대체 공급망 구축 1년 소요. 황산 수출 한국·일본 우위 sustained | predictive | user_provided |
| T06 | Anchor pick: 고려아연 (한국 아연 #1, 황산 부산물 dominant) + LS (LS MnM 구리 제련) + Sumitomo Metal Mining (일본 니켈/구리) | predictive | user_provided |
| T07 | Freeport-McMoRan (FCX) 등 황화광 구리 제련사 — 산화광 share gain. 글로벌 구리 가격 상승 직접 수혜 | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 010130.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/persona_panel/010130.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/persona_panel/010130.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/deep_research/010130.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-03_china_h2so4_butterfly/reports/combined/01_010130.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 010130.KS \
  --output /tmp/010130.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-03_china_h2so4_butterfly/
├── README.md
├── _build_all.sh
├── decisions.json
├── deep_research/
│   ├── 006260.KS.json
│   ├── 010130.KS.json
│   ├── 103140.KS.json
│   ├── 5713.T.json
│   ├── FCX.json
├── meta.json
├── persona_panel/
│   ├── 006260.KS/
│   ├── 010130.KS/
│   ├── 103140.KS/
│   ├── 5713.T/
│   ├── FCX/
│   └── ... (+1 more)
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

- `reports/combined/3_5713.T_Sumitomo_combined.pdf (361 KB)`
- `reports/combined/5_103140.KS_풍산_combined.pdf (361 KB)`
- `reports/combined/2_006260.KS_LS_combined.pdf (360 KB)`
- `reports/combined/1_010130.KS_고려아연_combined.pdf (360 KB)`
- `reports/combined/4_FCX_Freeport_combined.pdf (422 KB)`
- `reports/overview/overview.pdf (56 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
