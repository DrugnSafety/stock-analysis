# LNG (Cheniere Energy, Inc.) — 분석 리포트

> 메르 — 미국 천연가스의 심장, 헨리허브(Henry Hub)를 주목하는 이유?

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-01  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | LNG (Cheniere Energy, Inc.) |
| **섹터** | LNG Export Operator |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/ranto28/224262008286 |
| **분석 대상 종목 수** | 10개 |
| **추출 thesis 수** | 8개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 13 / Neutral 0 / Bear 0 |
| **Signal Score** | +1.000 |
| **평균 Confidence** | 0.60 |
| **최종 Decision** | BUY (375 주 (~$140,000,000)) |

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
| T01 | 글로벌 LNG 공급 충격 — 호르무즈 봉쇄(전세계 -20%), 카타르 LNG 시설 피격(-17%, 5년 복구), 호주 사이클론(-30% Australia, -8% global)으로 EU TTF·아시아 가격 폭등 | factual | user_provided |
| T02 | 헨리허브 가격은 LNG 수출 capacity 한계로 국제시세 디커플링 — TTF 대비 $21 spread. 미국 LNG 수출 풀가동(2026-3월 1,170만톤 역대최고)에도 spread 지속 | factual | user_provided |
| T03 | 2026 H2 ~ 2027 LNG terminal 신증설 본격 시작 — Plaquemines LNG(VG) 4월 capacity 증액 승인, Golden Pass LNG(XOM+QatarEnergy) 단계적 가동,  | predictive | user_provided |
| T04 | 퍼미안 분지 stranded gas — 파이프라인 capacity 부족으로 2026 1-4월 86% 기간 마이너스 가격. 신축 LNG 터미널이 이 가스를 수출 — upstream takeaway 정상화 | factual | user_provided |
| T05 | LNG 운반선 수요 폭발 — 미국 capacity +30%에 더해 2028년 이후도 LNG 수출시설 확충 계획 지속. 한국 빅3 (HD현대중공업·삼성중공업·한화오션) LNG선 신조 수주 직접 수혜 | predictive | user_provided |
| T06 | 헨리허브 가격 정상화 시 미국 천연가스 producer (EQT 중심) operating leverage 발생 — Marcellus·Utica·Haynesville unconventional E&P 수혜 | predictive | user_provided |
| T07 | LNG 수출 확대는 미국 internal natgas 가격 상승 → 소비자 부담 증가 risk. 정치적 backlash (export 제한 검토) 가능성 — BUT 현재 Trump 행정부는 LNG export 적극  | predictive | user_provided |
| T08 | 지정학 회복 risk — 호르무즈 재개·카타르 시설 조기 복구 시 LNG spot 가격 -30~50% drawdown 가능. 단, 호주 30% 복구는 6-12개월 + 카타르 5년 — 구조적 supply tight 유 | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker LNG \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/persona_panel/LNG/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/persona_panel/LNG \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/deep_research/LNG.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/ranto28/2026-05-01_test/reports/combined/01_LNG_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py LNG \
  --output /tmp/LNG_fs.json
```

## 5. 디렉토리 구조

```
2026-05-01_test/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 010140.KS.json
│   ├── 042660.KS.json
│   ├── 329180.KS.json
│   ├── EQT.json
│   ├── KMI.json
│   └── ... (+5 more)
├── meta.json
├── persona_panel/
│   ├── 010140.KS/
│   ├── 042660.KS/
│   ├── 329180.KS/
│   ├── EQT/
│   ├── KMI/
│   └── ... (+6 more)
├── portfolio.json
├── reports/
│   ├── combined/
│   ├── overview/
├── risk_limits.json
├── stocks.json
├── stocks_nested_backup.json
├── thesis_eval/
│   ├── all_aggregate.json
├── thesis_list.json
```

## 6. 생성된 보고서

- `reports/combined/3_LNG_셰니어_에너지_combined.pdf (690 KB)`
- `reports/combined/2_EQT_EQT_코퍼레이션_combined.pdf (703 KB)`
- `reports/combined/5_329180.KS_HD현대중공업_combined.pdf (695 KB)`
- `reports/combined/9_SRE_셈프라_combined.pdf (701 KB)`
- `reports/combined/10_KMI_킨더_모건_combined.pdf (699 KB)`
- `reports/combined/1_042660.KS_한화오션_combined.pdf (696 KB)`
- `reports/combined/6_VG_Venture_Global_combined.pdf (698 KB)`
- `reports/combined/7_WMB_윌리엄스_컴퍼니즈_combined.pdf (704 KB)`
- `reports/combined/8_XOM_엑슨모빌_combined.pdf (696 KB)`
- `reports/combined/4_010140.KS_삼성중공업_combined.pdf (691 KB)`
- `reports/overview/overview.pdf (173 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:08 UTC  ·  보고서 빌더 v0.5.0_
