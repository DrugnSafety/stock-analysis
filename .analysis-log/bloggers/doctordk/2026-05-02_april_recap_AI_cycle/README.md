# 000660.KS (SK하이닉스) — 분석 리포트

> 의교창 — 4월 시장 복기 (feat. 5월의 도전)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-02  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 000660.KS (SK하이닉스) |
| **분석 종류** | blogger |
| **블로그 URL** | https://blog.naver.com/doctordk/224273176389 |
| **분석 대상 종목 수** | 6개 |
| **추출 thesis 수** | 8개  |
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
| T01 | 4월 시장은 펀더멘털 (실적 surge)이 매크로 (유가·종전 부재) headwind를 능가 — 기업 이익 증가 속도가 비용 상승보다 빨라 시장 상승 지속 | factual | user_provided |
| T02 | AI 인프라 가치사슬은 단순 테마가 아닌 '실제 돈이 순환하는 산업 생태계' — 6단계 (인프라 투자 → 반도체 → 데이터센터 → 전력 → 장비 → 소프트웨어)에서 낙수효과 강화 | predictive | user_provided |
| T03 | 사이클 단계 진단: '중기 후반 ~ 후기 초입' — 펀더멘털 서프라이즈 강도 둔화 + 자금 쏠림 심화 동시 발생 | predictive | user_provided |
| T04 | 조선업 (한화오션·HD현대중공업·삼성중공업)은 'AI 인프라용 데이터센터선·LNG선' 수요로 새로운 cycle 진입 — referenced post 1번 | predictive | user_provided |
| T05 | CPU + DDR5는 새로운 병목 — referenced post 2번. SK하이닉스·삼성전자가 DDR5/HBM에서 글로벌 dominant | predictive | user_provided |
| T06 | 투자 질문 변화: '좋은 산업?' → '이 기업의 이익이 매크로 환경에서도 계속 증가하는가?' — 동일 AI 테마 내에서도 승자/패자 갈리기 시작 | predictive | user_provided |
| T07 | 포지셔닝 철학: 'matrix vs fundamental 속도 차이'에서 움직이는 시장에서는 섹터 분산 + 이익 검증이 risk management의 핵심 | factual | user_provided |
| T08 | Anchor 종목: SK하이닉스 + 삼성전자 (DDR5/HBM 글로벌 dominant), 한화오션 + HD현대중공업 (조선 + AI 인프라), NVDA (AI 글로벌 anchor) | predictive | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 000660.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/persona_panel/000660.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/persona_panel/000660.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/deep_research/000660.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-02_april_recap_AI_cycle/reports/combined/01_000660.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 000660.KS \
  --output /tmp/000660.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-02_april_recap_AI_cycle/
├── README.md
├── decisions.json
├── deep_research/
│   ├── 000660.KS.json
│   ├── 005930.KS.json
│   ├── 010140.KS.json
│   ├── 042660.KS.json
│   ├── 329180.KS.json
│   └── ... (+1 more)
├── meta.json
├── persona_panel/
│   ├── 000660.KS/
│   ├── 005930.KS/
│   ├── 010140.KS/
│   ├── 042660.KS/
│   ├── 329180.KS/
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

- `reports/combined/2_005930.KS_삼성전자_combined.pdf (438 KB)`
- `reports/combined/1_000660.KS_SK하이닉스_combined.pdf (440 KB)`
- `reports/combined/5_NVDA_NVIDIA_combined.pdf (556 KB)`
- `reports/combined/4_329180.KS_HD현대중공업_combined.pdf (437 KB)`
- `reports/combined/3_042660.KS_한화오션_combined.pdf (438 KB)`
- `reports/overview/overview.pdf (61 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
