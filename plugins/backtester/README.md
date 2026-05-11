# Backtester Plugin

메르 블로그 과거 글들 + 우리 분석 시스템(thesis-first / 13 personas / multi-model arena)의 verdict들을 사후 수익률로 검증하는 plugin.

## 핵심 질문

> "13명 페르소나·thesis-first·multi-model arena 시스템이 정말로 alpha를 만드는가?"

이 질문에 데이터로 답한다.

## 측정하는 것

| 메트릭 | 설명 |
|---|---|
| **Hit Rate** | BUY 후 실제 +5% 이상 상승한 비율 / HOLD 후 ±3% 이내 / SELL 후 -5% 이하 |
| **Alpha** | KOSPI·SPY 동일 기간 수익률 대비 outperformance |
| **Confidence Calibration** | conf 80% verdict의 실제 적중률이 80%인가? (overconfidence 측정) |
| **Persona Hit Rate** | 13명 각자의 적중률 — 어느 페르소나가 한국 시장에서 alpha 있는가 |
| **Source Hit Rate** | thesis-first vs multi-model arena vs 페르소나 패널 — 어느 방식이 우수한가 |
| **Time-to-Hit** | BUY verdict가 +5% 도달까지 평균 며칠 걸리는가 |

## Plugin 구조

```
plugins/backtester/
├── plugin.json
├── README.md
├── LICENSE-MIT-ai-hedge-fund         ← ai-hedge-fund의 backtester 패턴 차용
├── NOTICE.md
├── skills/
│   ├── historical-blog-collector/    ← 메르 블로그 과거 글 자동 수집
│   ├── backtest-engine/              ← entry → exit 사후 수익률 추적
│   ├── hit-rate-analyzer/            ← 적중률·alpha·calibration 계산
│   └── backtest-report/              ← PDF 시각화 (한글 폰트)
└── commands/
    ├── backtest-recent.md            ← 최근 N개월 글 일괄 backtest
    └── backtest-persona.md           ← 단일 페르소나 적중률 추적
```

## 사용 흐름

### Step 1: 과거 글 수집
```bash
python skills/historical-blog-collector/scripts/collect_meru.py \
    --start-date 2024-01-01 \
    --end-date 2026-04-01 \
    --sample monthly_first \
    --output /tmp/meru_historical.json
```

### Step 2: 각 글에 verdict 생성 (외부 plugin 활용)
- naver-blog-investment의 thesis-first 흐름
- investor-personas의 13명 패널
- multi-model-arena의 consensus

→ 각 verdict는 ledger.jsonl에 누적 저장

### Step 3: Backtest 실행
```bash
python skills/backtest-engine/scripts/run_backtest.py \
    --verdicts /path/to/ledger.jsonl \
    --horizon 1m,3m,6m,12m \
    --output /tmp/backtest_results.json
```

각 verdict에 대해:
- entry_price = 발행일 +1 거래일 종가
- exit_price = 1개월·3개월·6개월·12개월 후 종가
- benchmark_price = 같은 시점 KOSPI/SPY

### Step 4: 적중률 분석
```bash
python skills/hit-rate-analyzer/scripts/analyze.py \
    /tmp/backtest_results.json \
    --output /tmp/hit_rate_summary.json
```

### Step 5: PDF 보고서
```bash
python skills/backtest-report/scripts/build_report.py \
    /tmp/hit_rate_summary.json \
    --output /tmp/backtest_report.pdf
```

## ai-hedge-fund의 BacktestEngine과 차이점

| 항목 | ai-hedge-fund | 우리 backtester |
|---|---|---|
| 입력 | 단일 모델의 verdict | 여러 source(personas/thesis/arena)의 verdict ledger |
| 시뮬레이션 | 모의 거래 (cash·position 시뮬) | 사후 수익률 추적만 (실제 trade는 portfolio-manager 별도) |
| 페르소나별 hit rate | 없음 | **있음 — 13명 비교** |
| Source별 hit rate | 없음 | **있음 — 분석 방식 비교** |
| Confidence calibration | 없음 | **있음 — overconfidence 측정** |
| 메르 블로그 통합 | 없음 | **있음 — historical collector 포함** |

## 출력 메트릭 예시

```
Phase 1 결과 (2024-01 ~ 2026-04 메르 글 30개 backtest)

Persona Hit Rate (1개월 horizon):
  Druckenmiller    72% (적중 18 / 총 25)
  Cathie Wood      68% (적중 17 / 총 25)
  Buffett          65% (적중 15 / 총 23)
  Lynch            61% (적중 14 / 총 23)
  ...

Source Hit Rate:
  thesis-first 7-Analyst:  64%
  multi-model arena:        62%
  persona panel (13명):     67% ← 가장 우수
  
Alpha vs KOSPI (1개월):
  +4.2% (단순 페르소나 패널 매수 종목 평균)
  
Confidence Calibration:
  conf 80%+: 실제 적중 75% (slight overconfident)
  conf 60-80%: 실제 적중 62% (well calibrated)
  conf <60%: 실제 적중 51%
```

## 의존성

```
yfinance>=0.2.40       # 사후 수익률 fetch
pandas>=2.0.0
matplotlib>=3.7.0      # 차트 (PDF embed)
weasyprint>=60.0       # 한글 PDF
```

## 라이선스

본 plugin은 [ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)의 Backtester 패턴을 차용. MIT 라이선스 의무 충족 (LICENSE 사본 + NOTICE 출처 표시).
