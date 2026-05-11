---
name: paper-portfolio
description: yfinance 기반 모의 portfolio 시뮬레이션. Portfolio Manager 결정 (BUY/HOLD/SELL)을 반영하여 가상 NAV·수익률·trade ledger를 추적한다. 실제 거래는 절대 실행하지 않음. 사용자가 "paper portfolio", "모의 포트폴리오", "verdict 시뮬레이션" 등을 언급하면 트리거.
---

# Paper Portfolio Simulator

## 사용법

```bash
python3 plugins/trade-engine/skills/paper-portfolio/scripts/simulate.py \
  --decisions decisions.json \
  --start-cash 1400000000 \
  --output portfolio.json
```

## Portfolio 구조
```json
{
  "start_cash": 1400000000,
  "current_nav": 1450000000,
  "total_return_pct": 3.57,
  "current_holdings": {"005490.KS": {"quantity": 164, "avg_price": 470000}},
  "trade_history": [...]
}
```

## ⚠️ 주의
**실제 거래는 절대 실행하지 않음**. 본 시스템은 paper portfolio simulation 전용. 실제 매매는 사용자가 별도 증권사 시스템에서 수행.

## yfinance fetch
- 매일 자동 가격 fetch
- 환율 변환 (USD ↔ KRW) 자동
- 1m/3m/6m/1y 수익률 자동 계산
