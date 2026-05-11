# Trade Engine Plugin

verdict ledger를 입력받아 **변동성·상관관계로 포지션 사이즈를 정하고**, **buy/sell/hold + quantity**의 명확한 trade decision까지 도달하는 plugin. 모의 포트폴리오 추적 포함.

ai-hedge-fund의 `risk_manager.py` + `portfolio_manager.py` 패턴 차용.

## 핵심 차이 — 분석 vs Trade

| 단계 | 입력 | 출력 |
|---|---|---|
| **분석 (기존)** | 메르 글 → thesis-first / 13 personas | verdict (BUY/HOLD/SELL + confidence) |
| **Risk Manager (신규)** | verdict + 시장 데이터 | position 한도 (% of NAV) |
| **Portfolio Manager (신규)** | verdict + 한도 + 현재 cash | trade decision (action + quantity) |
| **Paper Portfolio (신규)** | trade 누적 + 시간 | 일일 NAV + 누적 수익률 |

## Plugin 구조

```
plugins/trade-engine/
├── plugin.json
├── README.md
├── LICENSE-MIT-ai-hedge-fund
├── NOTICE.md
├── skills/
│   ├── risk-manager/        ← 변동성·상관관계 → position 한도
│   ├── portfolio-manager/   ← verdict aggregate → trade decision
│   └── paper-portfolio/     ← 모의 포트폴리오 + NAV 추적
└── commands/
    ├── trade-decision.md     ← /trade-decision <ledger>
    └── paper-portfolio.md   ← /paper-portfolio
```

## Risk Manager — 변동성-조정 포지션 한도

ai-hedge-fund 원본 공식 (재현):

```python
base_limit = 0.20  # 20% baseline (단일 종목 최대)

if annualized_volatility < 0.15:    vol_multiplier = 1.25  # 25%
elif annualized_volatility < 0.30:  vol_multiplier = 1.0 - (vol - 0.15) * 0.5
elif annualized_volatility < 0.50:  vol_multiplier = 0.75 - (vol - 0.30) * 0.5
else:                                vol_multiplier = 0.50  # 10%

position_limit = base_limit × vol_multiplier
```

**상관관계 multiplier** (활성 포지션과의 평균 상관):
```
avg_correlation >= 0.80: × 0.70
avg_correlation >= 0.60: × 0.85
avg_correlation >= 0.40: × 1.00
avg_correlation >= 0.20: × 1.05
< 0.20:                  × 1.10
```

## Portfolio Manager — verdict → trade decision

verdict aggregate 방식:

1. **신호 강도** = 평균 confidence × verdict 일관성
2. **Action 결정**:
   - 신호 ≥ +0.7: `buy` (한도까지 진입)
   - +0.3 ≤ 신호 < +0.7: `buy` (한도의 50%)
   - -0.3 ≤ 신호 ≤ +0.3: `hold`
   - 신호 ≤ -0.3: `sell` (보유분 청산)
3. **Quantity** = floor(position_limit_value / current_price)

페르소나별 가중치 적용 가능 (Druckenmiller × 1.5 등 — Phase C 결과 반영).

## Paper Portfolio — 모의 포트폴리오 추적

- $1M 시작 cash
- 각 trade decision은 시점 종가에 체결 가정
- 일일 mark-to-market으로 NAV 계산
- 메트릭: cumulative return, max drawdown, Sharpe ratio
- KOSPI / SPY 벤치마크와 일별 비교

## 의존성

```
yfinance>=0.2.40
pandas>=2.0.0
numpy>=1.24
weasyprint>=60.0
```

## 사용 흐름 (Phase C → A 통합)

```bash
# 1. 분석 → verdict 생성 (이미 완료)
# ledger.jsonl 누적

# 2. Risk Manager: 각 ticker의 position 한도 계산
python plugins/trade-engine/skills/risk-manager/scripts/calc_limits.py \
    --ledger .../ledger.jsonl \
    --as-of 2025-09-01 \
    --portfolio-value 1000000 \
    --output /tmp/risk_limits.json

# 3. Portfolio Manager: trade decision 생성
python plugins/trade-engine/skills/portfolio-manager/scripts/make_decisions.py \
    --ledger .../ledger.jsonl \
    --risk-limits /tmp/risk_limits.json \
    --output /tmp/decisions.json

# 4. Paper Portfolio: 시점별 시뮬레이션
python plugins/trade-engine/skills/paper-portfolio/scripts/simulate.py \
    --decisions /tmp/decisions.json \
    --start-cash 1000000 \
    --start-date 2025-09-01 \
    --end-date 2026-04-28 \
    --output /tmp/portfolio_history.json

# 5. PDF
python plugins/trade-engine/skills/paper-portfolio/scripts/build_report.py \
    /tmp/portfolio_history.json --output /tmp/portfolio_report.pdf
```

## 라이선스 / 안전장치

- ai-hedge-fund MIT 라이선스 사본 동봉 (`LICENSE-MIT-ai-hedge-fund`)
- **실제 거래 절대 금지** — paper-portfolio는 simulation only
- 실제 매수·매도는 사용자가 별도 증권사 시스템에서 수동 실행 필요
