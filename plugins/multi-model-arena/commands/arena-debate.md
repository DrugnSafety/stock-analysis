---
name: arena-debate
description: Multi-Model Arena의 의도적 대결 모드. Claude는 Bull, GPT-5.5는 Bear, Gemini는 Skeptic으로 역할을 강제 배정하여 단일 종목에 대한 강한 대립적 견해를 도출. 일반 arena-analyze가 "균형 잡힌 합의"를 추구한다면, debate는 의도적으로 극단을 부각시켜 사용자가 양극단의 강한 논거를 모두 들을 수 있도록 한다. .env에 두 API 키가 필요.
---

# /arena-debate

세 모델에 의도적으로 다른 입장을 부여하여 강한 Bull vs Bear vs Skeptic 토론을 유도.

## 사용법

```
/arena-debate <TICKER>
```

## 역할 배정

| 모델 | 역할 | 시스템 프롬프트 |
|---|---|---|
| Claude | **Bull Researcher** | "당신은 가장 낙관적인 long thesis 전문가. 약점은 인정하되 핵심은 catalysts에 집중." |
| OpenAI GPT-5.5 | **Bear Researcher** | "당신은 가장 비관적인 short thesis 전문가. 모든 risk를 정량화하고 valuation 거품을 강조." |
| Gemini 3.1 | **Skeptic / Devil's Advocate** | "당신은 양쪽 모두에 반박하는 회의주의자. Bull과 Bear 양쪽의 가정을 모두 의심하고 데이터로 도전." |

## 출력

3개의 강한 논거 + arbitrator(Claude)가 최종 정리:

```
🥊 ARENA DEBATE — 439260.KS

🐂 Bull (Claude): "1년 +30% 상승 가능"
  3-5개 catalysts...

🐻 Bear (GPT-5.5): "단기 -25% 조정 가능"
  3-5개 risks...

🤔 Skeptic (Gemini): "양쪽 모두 데이터 부족"
  Bull/Bear의 약점 지적...

⚖️ Arbitrator (Claude 재판단)
  - Bull의 가장 강한 논거: ...
  - Bear의 가장 강한 논거: ...
  - Skeptic이 제기한 핵심 의심: ...
  - 최종 균형: ...
  - 추가 조사 필요한 데이터 포인트: ...
```

## 활용 시나리오

- 단일 모델 분석에서 verdict가 강한 BUY/SELL일 때 **반대편 논거 강제 노출**
- 본인 의견과 정반대 thesis를 듣고 싶을 때
- 투자 결정 전 마지막 stress test

## 비용

`/arena-analyze`와 비슷 (~$0.50-$0.80) — debate 형식이지만 호출 횟수는 동일.
