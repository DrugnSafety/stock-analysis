# Investor Personas Plugin

13명의 전설적 투자자 lens로 단일 종목 또는 thesis-mapped 종목들을 평가하는 plugin.

## 개요

각 페르소나는 통일된 5섹션 SKILL.md 구조를 따른다:
1. **Overview / Role Definition** — 어떤 시각의 분석가인가
2. **Core Principles** — 핵심 원칙 5-7개
3. **Required Analysis Sequence** — 의무 5단계
4. **Decision Rules** — Lean bullish / bearish / neutral 기준
5. **Anti-Hallucination Rules** — 환각 방지·데이터 태깅

## 13명 페르소나 (영한 병기)

| 한국어 | English | 핵심 lens |
|---|---|---|
| 워런 버핏 | Warren Buffett | Circle of Competence + Moat + Margin of Safety |
| 찰리 멍거 | Charlie Munger | Quality + Multidisciplinary + Incentives |
| 피터 린치 | Peter Lynch | GARP + Ten-bagger + 일상 제품 |
| 캐시 우드 | Cathie Wood | Disruptive Innovation + Large TAM + Exponential |
| 마이클 버리 | Michael Burry | Hard-number Contrarian + Downside Protection |
| 나심 탈레브 | Nassim Taleb | Antifragility + Convexity + Tail Risk |
| 벤저민 그레이엄 | Ben Graham | Margin of Safety + NCAV + Graham Number |
| 빌 애크먼 | Bill Ackman | Concentrated Activist + FCF + Catalyst |
| 모니시 파브라이 | Mohnish Pabrai | "Heads I win, tails I don't lose much" + Dhandho |
| 필 피셔 | Phil Fisher | Scuttlebutt + Mgmt Quality + Long Duration |
| 라케시 준준왈라 | Rakesh Jhunjhunwala | ROE + Long-term Wealth |
| 스탠리 드러켄밀러 | Stanley Druckenmiller | Asymmetric Setup + Momentum + Sentiment Inflection |
| 애스워드 다모다란 | Aswath Damodaran | Story → Numbers → Intrinsic Value |

## 명령

| 명령 | 설명 |
|---|---|
| `/persona-eval <TICKER> <PERSONA>` | 단일 종목 × 단일 페르소나 |
| `/persona-panel <TICKER> [PERSONAS]` | 단일 종목 × 다중 페르소나 (기본: 13명 전부) |
| `/persona-roundtable <TICKERS>` | 다중 종목 × 13명 페르소나 매트릭스 |

## 평가 출력 (per persona per ticker)

```json
{
  "ticker": "267250.KS",
  "persona_kr": "워런 버핏",
  "persona_en": "Warren Buffett",
  "verdict": "lean_bullish | lean_bearish | neutral",
  "confidence": 0.0,
  "horizon": "long_term",
  "stage_results": {
    "stage_1": {"name": "Circle of competence", "passed": true, "rationale": "..."},
    "stage_2": {"name": "Moat and durability", "passed": true, "rationale": "..."},
    ...
  },
  "key_concerns": [...],
  "key_opportunities": [...],
  "data_tags": ["[actual] FY24 ROE 8.2%", "[inference] 조선 슈퍼사이클 sustain", "[assumption] 정유 마진 정상화"],
  "uncertainty_acknowledged": "..."
}
```

## 패널 종합 (per ticker)

13명 페르소나의 verdict 분포:
- **Strong consensus**: 9명 이상이 같은 방향 (보수적·공격적 페르소나 모두 일치)
- **Style-split**: 가치파(Buffett/Graham) vs 성장파(Wood/Lynch)가 갈리는 경우
- **Universal concern**: 13명 모두가 짚는 공통 위험 (가장 신뢰도 높은 risk signal)
- **Unique alpha**: 1-2명만 보는 기회/위험 (놓치기 쉬운 인사이트)

## 출처 (Attribution)

이 plugin의 페르소나 SKILL.md는 [vibe-investing](https://github.com/monarchjuno/vibe-investing) 의 영문 SKILL.md를 한국어로 번역·각색한 것이다.

- 원저작권: © 2026 monarchjuno (MIT License)
- 페르소나 SKILL.md 원천: vibe-investing이 [virattt/ai-hedge-fund](https://github.com/virattt/ai-hedge-fund)에서 추가 적응
- 한국어 번역·한국 시장 보강: 본 plugin

LICENSE 사본: `LICENSE-MIT-vibe-investing` 파일 참조  
변경 이력 및 추가 출처: `NOTICE.md` 참조

## 의존성

```
openai>=1.50.0
google-generativeai>=0.8.0
python-dotenv>=1.0.0
weasyprint>=60.0
```

multi-model-arena plugin의 api-key-manager 재사용.

## 사용 시 주의

- **투자 자문 아님**: 교육·연구 목적. 페르소나는 실존 인물의 투자 철학을 lens로 사용할 뿐 그 인물을 대변하지 않음.
- **인물명·초상권**: 각 페르소나 SKILL.md는 "X의 lens로 분석한다"는 중립적 표현만 사용. 마케팅 카피에서 "X가 추천" 같은 잘못된 표현 금지.
- **Anti-hallucination**: 모든 숫자에 `[actual]/[estimated]/[assumption]/[derived]/[unavailable]` 태그 의무.
