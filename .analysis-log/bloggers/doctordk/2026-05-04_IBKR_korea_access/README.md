# 000660.KS (SK하이닉스) — 분석 리포트

> IBKR = I Buy Korea RightNow (3-part series)

**분석 종류**: 블로그 글 기반  ·  
**분석 일자**: 2026-05-04  ·  
**보고서 빌드**: v0.5.0

## 1. 분석 개요

| 항목 | 내용 |
|---|---|
| **종목** | 000660.KS (SK하이닉스) |
| **분석 종류** | blogger |
| **분석 대상 종목 수** | 8개 |
| **추출 thesis 수** | 12개  |
| **페르소나 패널** | 13명 |
| **Verdict 분포** | Bull 9 / Neutral 4 / Bear 0 |
| **Signal Score** | +0.692 |
| **평균 Confidence** | 0.68 |
| **최종 Decision** | BUY (53 주 (~$77,000,000)) |

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
| T01 | IBKR이 미국 개인투자자의 한국 주식 직접 매수 마찰비용(계좌·인증·환전·체결)을 자동화로 거의 0으로 제거 — 매수까지 5분 | factual | user_provided |
| T02 | 삼성증권이 IBKR 홍콩 법인의 한국 시장 모든 거래 체결 통로를 선점 — 글로벌 자금 입구 독점 구조 | factual | user_provided |
| T03 | 1차 수혜는 글로벌 메가트렌드(AI 인프라) 위 대형주 — SK하이닉스가 'AI 인프라 핵심 공급자'로 재포지셔닝되며 자금이 가장 먼저 집중 | predictive | user_provided |
| T04 | 2차 수혜는 NAV 디스카운트 지주사 — SK스퀘어 = 'SK하이닉스를 40% 할인된 가격에 사는 구조'로 직관적 번역 가능 | predictive | user_provided |
| T05 | 최대 변동성 구간은 반도체 소부장 — 오로스테크놀로지처럼 'HBM 공정 계측 장비 업체'로 명확한 역할 부여 시 SNS 확산 → 가격 급변 | predictive | user_provided |
| T06 | 오로스테크놀로지의 해외 커뮤니티 언급 → 상한가 사례가 '정보→SNS확산→해외 개인 유입→주가 반응' 루프의 작동을 입증 | factual | user_provided |
| T07 | IBKR 직접거래 + SK하이닉스 ADR 추진 + X(트위터) 실시간 정보 확산이 동시 결합 → 한국 시장의 폐쇄성 구조적 해체 | predictive | user_provided |
| T08 | 글로벌 자금이 사는 기업의 6대 조건 — (1)메가트렌드 (2)명확한 역할 (3)단순화된 숫자 (4)영어 한 문장 설명 (5)SNS 전파력 (6)아직 알려지지 않음 | normative | user_provided |
| T09 | 삼성SDI는 'EV battery and ESS leader with U.S. exposure' 한 문장 서사로 번역 비용이 낮아 자금 유입 우선순위 | predictive | user_provided |
| T10 | 두산테스나(131970)가 'NVIDIA 파트너 + SoC/CIS/MCU 테스트 #1 outsourcer' 라는 명확한 역할 + 시총 ~$1.7B 정보 비대칭으로 SNS 확산 후보 | predictive | user_provided |
| T11 | 코리아 디스카운트의 핵심 원인이 '저평가 구조'가 아닌 '접근성 마찰' — 마찰 제거로 점진적 해소되는 초입 단계 ('일부만 아는 구간') | predictive | user_provided |
| T12 | 투자가 정보 싸움이 아니라 '번역 싸움'으로 이동 — 영어로 설명되지 않은 좋은 한국 기업이 다음 알파의 원천 | normative | user_provided |

## 4. 빌드/재빌드 명령어

이 분석을 다시 빌드하려면 (예: 코드 업데이트 후 재생성):

```bash
# v0.5.0 섹션 흐름 적용된 per-stock combined PDF 생성
python3 plugins/report-suite/skills/unified-builder/scripts/build_combined.py \
  --ticker 000660.KS \
  --meta /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/meta.json \
  --stocks /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/stocks.json \
  --thesis /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/thesis_list.json \
  --eval-dir /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/thesis_eval \
  --persona-aggregate /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/persona_panel/000660.KS/aggregate.json \
  --persona-full /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/persona_panel/000660.KS \
  --persona-aggregates-all /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/persona_panel/_all_aggregates.json \
  --risk-limits /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/risk_limits.json \
  --decisions /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/decisions.json \
  --portfolio /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/portfolio.json \
  --deep-research /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/deep_research/000660.KS.json \
  --output /sessions/fervent-vigilant-knuth/mnt/주식 분석/.analysis-log/bloggers/doctordk/2026-05-04_IBKR_korea_access/reports/combined/01_000660.KS_combined.pdf
```

부분 재실행 (재무 분석만):
```bash
# 5년 + 5분기 US GAAP 재무 분석 단독 (디버깅용)
python3 plugins/report-suite/skills/_common/financial_statements_us_gaap.py 000660.KS \
  --output /tmp/000660.KS_fs.json
```

## 5. 디렉토리 구조

```
2026-05-04_IBKR_korea_access/
├── README.md
├── combined_post.txt
├── decisions.json
├── deep_research/
│   ├── 000660.KS.json
│   ├── 005930.KS.json
│   ├── 006400.KS.json
│   ├── 016360.KS.json
│   ├── 131970.KQ.json
│   └── ... (+3 more)
├── ledger.jsonl
├── meta.json
├── part1.json
├── part2.json
├── part3.json
├── persona_panel/
│   ├── 000660.KS/
│   ├── 005930.KS/
│   ├── 006400.KS/
│   ├── 016360.KS/
│   ├── 131970.KQ/
│   └── ... (+4 more)
├── portfolio.json
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

- `reports/combined/1_000660_KS_SK하이닉스_combined.pdf (423 KB)`
- `reports/combined/2_402340_KS_SK스퀘어_combined.pdf (424 KB)`
- `reports/combined/8_IBKR_Interactive_Brokers_combined.pdf (482 KB)`
- `reports/combined/5_322310_KQ_오로스테크놀로지_combined.pdf (419 KB)`
- `reports/combined/7_005930_KS_삼성전자_combined.pdf (419 KB)`
- `reports/combined/3_016360_KS_삼성증권_combined.pdf (419 KB)`
- `reports/combined/4_131970_KQ_두산테스나_combined.pdf (419 KB)`
- `reports/combined/6_006400_KS_삼성SDI_combined.pdf (430 KB)`
- `reports/overview/overview.pdf (82 KB)`

## 7. 주의사항 — 데이터 출처 및 한계

- **Financial Statements (Section 4)**: SEC EDGAR XBRL companyfacts API에서 5년 annual + 5분기 quarterly 자동 fetch. 한국 종목은 DART OpenAPI 사용. K-IFRS 항목은 US GAAP-equivalent로 매핑되며, SG&A/D&A 등 일부 line item은 미지원.
- **Material Variance Summary**: 임계값 기반 자동 플래깅 (>$1B 라인 = $50M/5%, $100M-$1B = $25M/10%, <$100M = $5M/15%). 원인 분석은 LLM이 추정한 narrative이므로 10-K Item 7 MD&A 직접 확인 권장.
- **News Timeline (Section 5)**: 중립(○) 항목은 KPI에는 카운트되지만 상세 표에서 제외됨. 긍정/부정만 상세 요약 + 월별 +/- bar chart 자동 생성 (종목별 개별).
- **Persona Panel (Section 8)**: 13명 페르소나의 verdict는 sector-aware heuristic 또는 LLM 평가 결과. `_meta.is_mock: true`이면 demo 데이터, 아니면 실제 OpenAI/Gemini 평가.
- **투자 자문 아님**: 본 분석은 paper portfolio simulation 전용. 실제 거래는 절대 자동 실행하지 않음. 모든 verdict는 `[actual]` / `[inference]` / `[assumption]` 태그로 출처 명시.

---

_이 README는 `plugins/report-suite/skills/readme-generator/scripts/build_instruction_readme.py`로 자동 생성되었습니다._  
_생성 일시: 2026-05-11 20:07 UTC  ·  보고서 빌더 v0.5.0_
