---
name: specialist-agents:earnings-reviewer
description: >
  최근 4 분기 컨퍼런스콜 transcript와 10-Q/K filing을 읽고 thesis-relevant 변경사항을 자동 flag.
  Anthropic Earnings Reviewer Agent 템플릿(2026-05) 패턴.

  트리거: "최근 어닝 리뷰", "guidance 변경 추적", "Earnings Reviewer 호출", "thesis impact 분석".
version: 0.1.0
based_on: Anthropic Financial Services Agents 2026-05
---

# Earnings Reviewer — Thesis-Relevant Change Extraction

## 목적
페르소나 평가 시점의 **stale 정보 risk**를 차단. 분기 결산 후 ~1주 내 신규 정보가 thesis verdict에 미치는 영향 자동 측정.

## 입력
- ticker
- thesis_list.json (T1-T15 등)
- (자동) yfinance `Ticker.earnings_history`·`Ticker.quarterly_earnings`
- (KR) DART 분기 사업보고서
- (US) SEC 10-Q/10-K filings + earnings call transcripts (Seeking Alpha/MotleyFool)

## 출력 `earnings_review/{ticker}_Q{N}.json`
```json
{
  "ticker": "010140.KS",
  "quarter": "2025-Q4",
  "filing_date": "2026-02-22",
  "key_metrics": {
    "revenue": {"actual": 2950, "consensus": 2780, "beat_pct": 6.1, "yoy": 18.5},
    "op_income": {"actual": 158, "consensus": 142, "beat_pct": 11.3, "yoy": 25.4},
    "op_margin": {"actual": 5.4, "consensus": 5.1, "delta_bps": 30},
    "backlog": {"actual": 30000, "qoq": 1.5}
  },
  "guidance_changes": [
    {"metric": "2026 revenue", "old": "11.0조", "new": "12.5조", "direction": "+", "magnitude": "moderate"}
  ],
  "thesis_impact": [
    {
      "thesis_id": "T4",
      "claim": "삼성중공업 FDC 표준 빌더",
      "impact_direction": "+",
      "confidence_delta": "+0.10",
      "evidence_quote": "FDC 본계약 2건 2026-Q3 마감 예정 - 컨퍼런스콜 회장 발언",
      "previous_status": "pending",
      "new_status": "pending (strengthened)"
    }
  ],
  "management_tone": {
    "overall": "+0.6 (cautiously optimistic)",
    "verbatim_quotes": ["FDC는 확실히 새로운 모멘텀임...(중략)"]
  },
  "red_flags": [],
  "next_catalyst": "2026-Q1 어닝 (예상 2026-05)"
}
```

## thesis verdict 갱신 자동화
Earnings Reviewer가 thesis_impact 추출 후 `thesis_eval/all_aggregate.json`의 confidence를 ±0.10 범위에서 자동 조정 (overshoot 방지를 위해 절대값 0.95 cap).

## TradingAgents 패턴
- LangGraph checkpoint resume 활용 — 분기 결산 후 자동 재실행
- structured output (Pydantic schema) 강제 — render_combined에서 안전 parsing
