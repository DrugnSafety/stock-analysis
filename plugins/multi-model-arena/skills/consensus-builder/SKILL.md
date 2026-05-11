---
name: consensus-builder
description: Multi-Model Arena 결과를 비교·통합하는 skill. arena-orchestrator가 생성한 claude.json/openai.json/gemini.json을 읽어 union of tickers, verdict 분포, ticker별 합의 점수, 이견 영역을 분석하고 시각화한다. 사용자가 "consensus 만들어", "3개 모델 비교", "합의 분석", "이견 시각화", "arena 통합" 등을 언급하면 트리거된다. LLM을 사용하지 않으므로 추가 비용 없음.
---

# Consensus Builder

## 역할

Arena 결과를 다음과 같이 통합:

### 추출 단계 통합

```
┌─────────────────────────────────────────────────────┐
│  consensus_companies (3/3 모델 모두 추출)             │
│  → 가장 신뢰할 수 있는 핵심 종목                       │
├─────────────────────────────────────────────────────┤
│  majority_companies (2/3 모델 추출)                   │
│  → 일반적 합의                                       │
├─────────────────────────────────────────────────────┤
│  single_model_only (1/3 모델만)                      │
│  → 누락 가능성 검토 대상 (예: 대한조선 케이스)         │
└─────────────────────────────────────────────────────┘
```

### 분석 단계 통합

각 ticker별 verdict 분포:
- 3-way 합의 (BUY/BUY/BUY 등) → high agreement
- 2-1 분포 → medium agreement, 1 모델의 이견 명시
- 3-way 이견 → low agreement, 추가 조사 권고

confidence 가중평균 (모델별 가중치 조정 가능):
- Claude: 1.0 (Cowork 기본)
- OpenAI: 1.0
- Gemini: 1.0
- 사용자가 Bayesian update로 모델별 신뢰도 학습 후 가중치 조정 가능

## 사용

```bash
# 추출 consensus
python skills/consensus-builder/scripts/build_consensus.py \
    /tmp/arena_extract_2026-04-28 \
    --type extract \
    --output /tmp/consensus_extract.json

# 분석 consensus
python skills/consensus-builder/scripts/build_consensus.py \
    /tmp/arena_analyze_439260 \
    --type analyze \
    --output /tmp/consensus_analyze_439260.json

# 시각화 (HTML)
python skills/consensus-builder/scripts/visualize.py \
    /tmp/consensus_extract.json \
    --output /tmp/consensus.html
```

## 출력 스키마

### Extract consensus

```json
{
  "blog_url": "...",
  "models_run": ["claude", "openai", "gemini"],
  "extraction_consensus": {
    "all_companies_union": [
      {"ticker": "...", "name_kr": "...", "found_by": ["claude","openai","gemini"], "consensus_score": 1.00}
    ],
    "consensus_3of3": [...],     // 모든 모델 합의
    "majority_2of3": [...],       // 다수
    "single_model": [...],        // 단일 모델만 — 검토 대상
    "summary": {
      "total_unique": 17,
      "consensus_count": 8,
      "majority_count": 5,
      "single_count": 4
    }
  },
  "industries_consensus": [...],
  "etfs_consensus": [...],
  "cost_summary": {"openai_usd": 0.42, "google_usd": 0.18, "total_usd": 0.60}
}
```

### Analyze consensus

```json
{
  "ticker": "439260.KS",
  "verdicts": {
    "claude": {"verdict": "BUY", "confidence": 0.74},
    "openai": {"verdict": "BUY", "confidence": 0.81},
    "gemini": {"verdict": "HOLD", "confidence": 0.62}
  },
  "weighted_verdict": "BUY",
  "weighted_confidence": 0.72,
  "agreement_level": "medium",
  "agreement_breakdown": {"BUY": 2, "HOLD": 1, "SELL": 0},
  "disagreement_summary": "Gemini takes a more cautious HOLD stance citing valuation concerns; OpenAI is most bullish on the mid-tier rotation thesis.",
  "perspectives_diff": {
    "fundamentals": {"claude": 4, "openai": 5, "gemini": 3, "spread": 2},
    "technical": {...},
    "news": {...},
    "sentiment": {...}
  },
  "bull_thesis_overlap": [...],
  "bear_thesis_overlap": [...],
  "unique_insights": {
    "claude": ["Claude만 발견한 인사이트"],
    "openai": [...],
    "gemini": [...]
  }
}
```

## 시각화

`visualize.py`는 HTML/PDF로 다음 요소를 포함한 보고서 생성:
- 3-way verdict bar chart
- ticker별 합의 점수 히트맵
- agreement level 분포
- 단일 모델 발견 종목 강조 (놓치기 쉬운 인사이트)
