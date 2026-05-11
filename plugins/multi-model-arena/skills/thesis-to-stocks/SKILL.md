---
name: thesis-to-stocks
description: 평가된 thesis들을 영향받는 종목으로 매핑하는 skill. 각 ticker에 대해 thesis별 노출도(++/+/0/-/--)를 산출하고, evaluator의 weighted_stance · confidence를 가중치로 적용하여 thesis-weighted 종합 점수를 계산. 결과는 "왜 이 종목이 매력적인가"를 thesis 단위로 추적 가능한 표로 제공. 사용자가 "thesis 종목 매핑", "주장별 영향 종목", "thesis exposure", "수혜주 도출" 등을 언급하면 트리거된다.
---

# Thesis to Stocks Mapping

## 핵심 아이디어

각 thesis가 "지지(support)"되었다면, 그 thesis가 함의하는 영향이 시장에 반영될 것:
- **양의 영향**(+) 받는 종목: 수혜주
- **음의 영향**(-) 받는 종목: 부담주
- **무관**(0) 종목: 노이즈

각 종목의 종합 점수 = Σ (thesis_i의 noise_signed × thesis_i의 weighted_stance × thesis_i의 confidence × thesis_i의 importance_weight)

## 입력

- `thesis_list.json` (thesis-extractor 결과)
- `thesis_eval/` (thesis-evaluator 결과들)
- (선택) 후보 종목 리스트 (없으면 자동으로 stock-extractor 호출)

## 출력 스키마

```json
{
  "post_meta": {...},
  "scoring_method": "thesis_weighted_v1",
  "stocks": [
    {
      "ticker": "439260.KS",
      "name_kr": "대한조선",
      "exposures": {
        "T01": {"sign": "+", "magnitude": 0.5, "rationale": "관세 면제 → 직접 수혜자 아니지만 정유 다변화 catalyst"},
        "T05": {"sign": "++", "magnitude": 1.0, "rationale": "Aframax 70% 적재 — 중형 유조선 신조 직접 수혜"},
        "T06": {"sign": "++", "magnitude": 1.0, "rationale": "Panamax 만재 합리적 → 중형선 전문 야드 핵심 수혜"},
        ...
      },
      "thesis_weighted_score": 4.2,
      "primary_drivers": ["T05", "T06"],
      "primary_risks": [],
      "summary": "Panamax/Aframax 중형선 전문 야드로 본문 핵심 thesis(T05, T06)의 가장 직접적 수혜. T01의 관세 면제도 간접 catalyst."
    }
  ],
  "ranking": [
    {"ticker": "439260.KS", "score": 4.2, "rank": 1},
    ...
  ]
}
```

## 노출도(magnitude) 표기

| 표기 | 수치 | 의미 |
|---|---|---|
| `++` | +1.0 | 강한 양의 노출 (직접 수혜) |
| `+` | +0.5 | 약한 양의 노출 (간접 수혜) |
| `0` | 0 | 무관 |
| `-` | -0.5 | 약한 음의 노출 |
| `--` | -1.0 | 강한 음의 노출 |

## Score 계산 공식

```
importance_weight: core=1.0, supporting=0.5, aside=0.0
stance_weight:     support=+1.0, neutral=0, rebut=-1.0

stock_score = Σ_t [
    exposure_magnitude(stock, t) × 
    stance_weight(t.weighted_stance) × 
    t.weighted_confidence × 
    importance_weight(t.importance)
]
```

직관:
- thesis가 강하게 지지되고(stance=support, conf=0.85) 종목 노출이 강하면(++) → +0.85 기여
- thesis가 반박되면(stance=rebut, conf=0.7) 그 thesis에 양으로 노출된 종목은 -0.7 기여 (위험)

## 사용

```bash
python skills/thesis-to-stocks/scripts/map_to_stocks.py \
    /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --candidate-stocks /tmp/stocks.json \
    --output /tmp/thesis_to_stocks.json

# 자동 후보 종목 결정 (stock-extractor 호출)
python skills/thesis-to-stocks/scripts/map_to_stocks.py \
    /tmp/thesis_list.json \
    --eval-dir /tmp/thesis_eval \
    --auto-extract \
    --output /tmp/thesis_to_stocks.json
```

## Multi-model

`--multi-model` 옵션 시 노출도 결정도 GPT-5.5 + Gemini로 이중 체크 → 합의 시만 적용.

## Cowork 인라인 (Claude 직접 매핑)

Claude가 이 skill을 직접 사용할 때:
1. 각 종목의 사업 모델·자산 구성 학습 지식 활용
2. 각 thesis와의 관계를 1줄 rationale로 정리
3. 노출도(++/+/0/-/--) 부여
4. JSON 출력

비용 효율적 (외부 API 없이 가능, 단 Claude 학습 cutoff 종목 한정)

## 출력 활용

- 종목별 score 랭킹 → top-N pick
- thesis별 driver 종목 → 단일 thesis 검증 시 어느 종목 추적할지
- primary_risks → bear thesis 시나리오에서 위험 노출 종목
