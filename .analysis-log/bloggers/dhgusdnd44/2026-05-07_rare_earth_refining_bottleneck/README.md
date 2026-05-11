# MP (MP 머티리얼스) — 분석 리포트

> MP 분석

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: ['2026-05-05', '2026-05-06', '2026-05-07']  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | MP (MP 머티리얼스) |
| **분석 종류** | blogger |
| **블로거** | happy |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 10개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 6 / Neutral 2 / Bear 2 |
| **Signal Score** | +0.308 |
| **평균 Confidence** | 0.69 |
| **최종 Decision** | STARTER_BUY (? 주 (~$0)) |

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
| ? | 중국 점유율은 채굴에서 60%지만 정제 91%, 중희토류 분리 99%, 자석 제조 94%로 단계가 올라갈수록 독점이 강화된다. 시장 컨센서스는 '광산만 더 캐면 된다'에 머물러 있어 정제 capacity의 진짜 희소 | factual | user_provided |
| ? | 2025-04 7개 중희토류 통제 → 2025-10 12개 원소 + 45일 허가제 + 0.1% 역외 관할권 + 정제 설비까지 확대. 트럼프-시진핑 부산 회담 후 26년 11월 10일까지 유예됐으나, 중국은 역사적으로 | predictive | user_provided |
| ? | (1) 30년 단절된 암묵지 (도제식 화학 레시피), (2) 정제 장비 100% 중국 독점 + 2025-10 수출 통제 포함, (3) 의도적 비용 구조 (서방 정제 비용 중국 대비 2.5~10배), (4) 자금조달  | factual | user_provided |
| ? | 글로벌 NdPr/Dy/Tb 수요는 2024년 55,000~60,000톤 → 2030년 90,000~100,000톤 (50~70% ↑). IEA: 2035년까지 비중국 정제 capacity는 수요의 25% (자석 20 | predictive | user_provided |
| ? | NdFeB 에너지 밀도 50MGOe vs 페라이트 4MGOe — 동일 성능 위해 10배 부피 필요. 방산·로봇·고성능 EV·해상풍력·MRI 등 6개 핵심 산업에서 물리적으로 대체 불가. 가격이 얼마나 오르든 사용해야 | factual | user_provided |
| ? | Dy·Tb는 매장량 90% 이상이 중국 남부·미얀마에 집중 + 정제 99% 중국 독점. 2025년 통제 후 Tb 중국 외 가격 $3,625/kg (中 내 4배). NdPr 격차 50~80%, Dy 200%, Tb 4 | factual | user_provided |
| ? | 방산은 가격 탄력성 ZERO. 미사일 1m 유도 오차 = 수십억 폐기. 미 국방부 2026-03 13개 핵심 광물에 1~5억$ 긴급 자금 + MP에 NdPr $110/kg 가격 하한 보장. 2011년에 없었던 '국방 | factual | user_provided |
| ? | 시장은 '대체 가능한 부분(채굴)'에 프리미엄을 부여 중. 진짜 대체 불가능한 정제 기업은 미스프라이싱. Lynas가 비중국 정제의 사실상 전부에 가깝다는 사실을 시장이 충분히 인식하지 못함. 채굴+정제 vertic | normative | user_provided |
| ? | 2025년 이후 호주·미국·브라질에서 신규 광산 프로젝트 다수 발표. 그러나 비중국 정제 capacity 부족 시 원광은 결국 중국 정제소로 보내져 중국 지배력만 강화. 구리에서 1980-2025 유럽·북미 점유율  | factual | user_provided |
| ? | Toyota·VW·Siemens·GM 등 20대 OEM 6~12개월치 비축 → 7,000~15,000톤 미래수요 당겨옴. 가격 $55→$100/kg 급등. 2028~2029년 비축 소멸 + 신규 정제 capacity | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker MP \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/persona_panel/MP/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/persona_panel/MP \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/deep_research/MP.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-07_rare_earth_refining_bottleneck/reports/combined/01_MP_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py MP \
  --output /tmp/MP_fs.json
```

## 5. 디렉토리 구조

```
2026-05-07_rare_earth_refining_bottleneck/
├── 224274891820.json
├── 224275680861.json
├── 224277824384.json
├── README.md
├── decisions.json
├── deep_research/
│   ├── 600111.SS.json
│   ├── ILU.AX.json
│   ├── LYC.AX.json
│   ├── MP.json
│   ├── USAR.json
├── meta.json
├── persona_panel/
│   ├── 600111.SS/
│   ├── ILU.AX/
│   ├── LYC.AX/
│   ├── MP/
│   ├── USAR/
│   └── ... (+1 more)
├── portfolio.json
├── reports/
│   ├── combined/
│   ├── overview/
│   ├── overview_v2/
├── risk_limits.json
├── stocks.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/4_600111.SS_북방희토_combined.pdf (380 KB)`
- `reports/combined/2_ILU.AX_일루카_combined.pdf (376 KB)`
- `reports/combined/1_LYC.AX_라이너스_combined.pdf (391 KB)`
- `reports/combined/3_MP_MP머티리얼스_combined.pdf (460 KB)`
- `reports/combined/5_USAR_USA레어어스_combined.pdf (466 KB)`
- `reports/overview/overview.pdf (85 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
