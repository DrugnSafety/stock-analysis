---
name: thesis-extractor
description: 메르(또는 다른 경제·투자 블로거)의 글에서 핵심 주장(thesis/claim)들을 추출하는 skill. 종목보다 먼저 "글쓴이가 무엇을 주장하는가"를 N개의 독립 명제로 분리하고 각각에 type(factual/predictive/normative/conditional), timeframe, supporting_evidence를 부여한다. 이후 thesis-evaluator가 각 주장을 4-Analyst lens로 평가하고, thesis-to-stocks가 영향받는 종목으로 매핑한다. 사용자가 "메르가 무엇을 주장했는지", "글의 핵심 포인트", "thesis 추출", "주장 분해", "claim 정리" 등을 언급하면 트리거된다.
---

# Thesis Extractor

## 핵심 원칙

분석의 starting point를 **종목 → 주장**으로 전환.

- ❌ 기존: "이 글에서 어떤 종목이 언급되는가?"
- ✅ 새로운: "이 글의 글쓴이는 무엇을 주장하는가? 그 주장들이 맞다면 어떤 종목이 영향받는가?"

## 추출 규칙

### 1. 명제 분리 (atomicity)

한 문단에 여러 주장이 있으면 각각을 독립 thesis로 분리:

> 본문: "캐나다는 환경규제가 까다로워 신규 정유시설 건설이 어렵고, Trans Mountain Pipeline 확장으로 밴쿠버 89만 b/d 캐파가 추가됐다."

→ 두 개의 thesis로 분리:
- T01: "캐나다는 환경규제가 까다로워 신규 정유시설 건설이 어렵다" (factual)
- T02: "Trans Mountain Pipeline 확장으로 밴쿠버 89만 b/d 캐파 추가됨 (2024.5)" (factual)

### 2. Thesis Type 분류

| Type | 정의 | 예시 |
|---|---|---|
| `factual` | 검증 가능한 사실 | "한국이 2026.4.20 캐나다산 원유 3% 관세를 면제했다" |
| `predictive` | 미래 예측·추론 | "Panamax 만재가 합리적 대안이 될 것" |
| `normative` | 가치 판단·권고 | "캐나다는 미국 외 다변화가 필요하다" |
| `conditional` | 조건부 명제 | "만약 X면, Y가 발생할 것" |

### 3. Timeframe

| Timeframe | 의미 |
|---|---|
| `historical` | 과거 사실 |
| `present` | 현재 상태 |
| `short_term` | ~6개월 |
| `medium_term` | 6-24개월 |
| `long_term` | 2년 이상 |

### 4. 지지 증거

각 thesis마다 본문에서 인용한 raw text 보존:

```json
{
  "claim_id": "T05",
  "claim": "Aframax 유조선은 밴쿠버항에서 70%만 적재 가능",
  "type": "factual",
  "timeframe": "present",
  "supporting_evidence": "아프로막스 유조선이 벤쿠버항을 출입하려면, 기름을 풀로 채우지 못하고 70%정도를 채워야 함",
  "evidence_section": "원문 46-47번"
}
```

### 5. 핵심 주장과 부수 주장 구분

`importance` 필드:
- `core` (핵심): 글 전체의 thesis (보통 3-7개)
- `supporting` (부수): core를 뒷받침하는 사실
- `aside` (여담): 글 흐름상 추가된 정보

평가는 `core`와 `supporting`만 진행 (`aside`는 메타데이터로만)

## 출력 스키마

```json
{
  "post_meta": {
    "url": "...",
    "title": "...",
    "author": "..."
  },
  "summary_one_liner": "글의 한 줄 요약 (메르의 한줄 코멘트가 있으면 그것 우선)",
  "theses": [
    {
      "claim_id": "T01",
      "claim": "본문에서 추출한 한 문장 명제",
      "type": "factual | predictive | normative | conditional",
      "importance": "core | supporting | aside",
      "timeframe": "historical | present | short_term | medium_term | long_term",
      "supporting_evidence": "본문 raw text 인용",
      "evidence_section": "원문 X-Y번 (메르 글의 번호 형식이 있을 때)",
      "tags": ["원유", "정유", "캐나다", "관세"]
    }
  ],
  "extraction_meta": {
    "extracted_at": "ISO 8601",
    "model": "gpt-5.5 | claude | gemini",
    "n_core": 7,
    "n_supporting": 12,
    "n_aside": 3
  }
}
```

## 사용 예 (CLI)

```bash
# OpenAI gpt-5.5로 추출 (로컬 머신, reasoning_effort=high)
python skills/thesis-extractor/scripts/extract_theses.py \
    /tmp/post.json \
    --output /tmp/thesis_list.json \
    --provider openai \
    --blog-url "https://blog.naver.com/ranto28/224264942275"

# Claude (Cowork 인라인)
# → Claude가 직접 본문 읽고 SKILL.md 따라 JSON 생성
```

## Cowork 인라인 사용

Claude(Cowork 세션)가 이 skill을 사용할 때:
1. `/tmp/post.json` 읽기
2. 본문을 한 문장씩 분해하며 thesis 후보 식별
3. 각 후보에 type / importance / timeframe 부여
4. `core` thesis 3-7개 + `supporting` 5-15개 + `aside` 0-5개로 분류
5. JSON 출력

## 다음 단계

추출된 thesis_list.json은 다음 skill의 입력:
- `thesis-evaluator`: 각 thesis에 대해 4-Analyst가 평가
- `thesis-to-stocks`: 평가된 thesis를 영향받는 종목으로 매핑
