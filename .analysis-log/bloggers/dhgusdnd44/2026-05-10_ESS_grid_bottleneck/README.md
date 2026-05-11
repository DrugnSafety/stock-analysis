# GEV (GE Vernova) — 분석 리포트

> ESS에서 병목찾기

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-10  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | GEV (GE Vernova) |
| **분석 종류** | blogger |
| **분석 대상 종목 수** | 5개 |
| **추출 thesis 수** | 9개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 7 / Neutral 5 / Bear 1 |
| **Signal Score** | +0.462 |
| **평균 Confidence** | 0.63 |
| **최종 Decision** | N/A (? 주 (~$0)) |

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
| ? | 2024년 칠레 태양광 발전량의 17.2%가 버려졌고, 중국도 태양광 3.2%·풍력 4.1%로 전년 대비 1%p 이상 상승했다. EU 계통 혼잡관리 비용은 2023년 40억 유로를 돌파했다. '버려지는 전기'가 ES | factual | user_provided |
| ? | 2024년 전 세계 재생에너지 경매의 25%(45GW)가 ESS 의무 부착(firm capacity) 형태로 발주됐고, 이는 2021~2023년의 5~8% 대비 폭증한 수치다. 인도(40% 이상), 호주(2MWh/M | predictive | user_provided |
| ? | 글로벌 태양광 패널 제조능력은 1,100~1,350GW로 실제 설치량의 2배를 넘기며 가동률 55~65%, 모듈 가격 $0.09/W로 대부분 원가 이하다. 배터리 셀도 동일 경로 — 중국 LFP $30~40/kWh, | factual | user_provided |
| ? | 중국 턴키 ESS $62/kWh 대비 미국 $219/kWh, 유럽 $177/kWh로 3.5배 차이가 난다. 이 격차는 셀 가격이 아니라 변압기·BMS·EPC·PCS 등 Balance-of-System(BoS)에서 발 | factual | user_provided |
| ? | Enel·Iberdrola·EDF·E.ON 등 거대 유틸리티의 연간 CAPEX 수백억 유로 중 20~60%가 전력망에 투자되고 있으며 이 비중은 5~15%p씩 더 늘고 있다. 변압기·송전선·변전소 부족이 ESS 설치 | predictive | user_provided |
| ? | 출력제한율이 올라가면 낮 시간대(태양광 과잉) 전력가격은 0원/마이너스로, 저녁 가격은 가스 발전 한계비용으로 수렴해 스프레드가 극단적으로 벌어진다. ESS 운영사는 이 스프레드를 먹는 트레이딩 사업이며, 커튼율 심 | predictive | user_provided |
| ? | 중앙 전력망 요금에는 망 건설비·혼잡관리비가 포함되어 계속 상승하는 반면 태양광+ESS 가격은 하락 → 자체 발전·자체 저장 경제성 개선. IEA에 따르면 파키스탄에서 2024년에만 6GW의 오프그리드 PV+ESS가 | predictive | user_provided |
| ? | 유럽 CfD 2.0이 2027년까지 의무화되면 보조금 수령을 위해 ESS가 필수가 되며, 인도 FDRE 모델 확산, 호주 2MWh/MW 의무, 포르투갈·불가리아 20~30% 의무, 폴란드 보조금 박탈 등 정책이 계속 | conditional | user_provided |
| ? | IEA가 올해 재생에너지 발전량 전망을 850TWh로 하향했고 그 이유 중 하나로 '버려지는 전기'를 명시적으로 지목. 이는 컨센서스 모델조차 curtailment 문제의 심각성을 인정한 의미 있는 신호이며, ESS | factual | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker GEV \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/persona_panel/GEV/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/persona_panel/GEV \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/deep_research/GEV.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/dhgusdnd44/2026-05-10_ESS_grid_bottleneck/reports/combined/01_GEV_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py GEV \
  --output /tmp/GEV_fs.json
```

## 5. 디렉토리 구조

```
2026-05-10_ESS_grid_bottleneck/
├── README.md
├── _generate_personas.py
├── _persona_input.json
├── decisions.json
├── deep_research/
│   ├── 267260.KS.json
│   ├── ENPH.json
│   ├── FLNC.json
│   ├── GEV.json
│   ├── NEE.json
├── meta.json
├── persona_panel/
│   ├── 267260.KS/
│   ├── ENPH/
│   ├── FLNC/
│   ├── GEV/
│   ├── NEE/
│   └── ... (+1 more)
├── portfolio.json
├── post.json
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

- `reports/combined/3_NEE_NextEra_Energy_combined.pdf (432 KB)`
- `reports/combined/2_267260.KS_HD현대일렉트릭_combined.pdf (345 KB)`
- `reports/combined/1_GEV_GE_Vernova_combined.pdf (398 KB)`
- `reports/combined/4_ENPH_Enphase_Energy_combined.pdf (399 KB)`
- `reports/combined/5_FLNC_Fluence_Energy_combined.pdf (391 KB)`
- `reports/overview/overview.pdf (59 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
