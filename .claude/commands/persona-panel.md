---
name: persona-panel
description: 단일 종목에 대해 13명 전설적 투자자(워런 버핏·캐시 우드·피터 린치 등)의 lens로 동시에 평가하고 합의·이견을 PDF로 정리. 사용자가 종목 ticker만 주면 ticker 시장 데이터 자동 수집 → 13명 페르소나 병렬 평가 → 종합 매트릭스 → 시각화. .env에 OPENAI_API_KEY 또는 GOOGLE_API_KEY 필요.
---

# /persona-panel

단일 종목 × 13명 페르소나 패널 분석.

## 사용법

```
/persona-panel <TICKER> [--include warren-buffett,peter-lynch,...] [--blog-url URL]
```

기본은 13명 전부 실행. `--include`로 부분 선택 가능.

## 사용 가능한 페르소나 ID

| ID | 한국어 | 카테고리 |
|---|---|---|
| `warren-buffett` | 워런 버핏 | value |
| `charlie-munger` | 찰리 멍거 | value |
| `peter-lynch` | 피터 린치 | growth |
| `cathie-wood` | 캐시 우드 | growth |
| `michael-burry` | 마이클 버리 | value-contrarian |
| `nassim-taleb` | 나심 탈레브 | risk |
| `ben-graham` | 벤저민 그레이엄 | value |
| `bill-ackman` | 빌 애크먼 | activist |
| `mohnish-pabrai` | 모니시 파브라이 | value |
| `phil-fisher` | 필 피셔 | growth |
| `rakesh-jhunjhunwala` | 라케시 준준왈라 | growth-em |
| `stanley-druckenmiller` | 스탠리 드러켄밀러 | macro |
| `aswath-damodaran` | 애스워드 다모다란 | valuation |

## 절차 (Claude/사용자 시스템이 따를 것)

### Step 1: 환경 검증

```bash
python plugins/multi-model-arena/skills/api-key-manager/scripts/check_keys.py
```

### Step 2: 시장 데이터 + 블로그 컨텍스트(옵션)

```bash
python plugins/naver-blog-investment/skills/trading-analysis/scripts/market_data.py \
    "$TICKER" --output /tmp/market_${TICKER//./_}.json

# 옵션
python plugins/naver-blog-investment/skills/naver-blog-scraper/scripts/scrape_naver_blog.py \
    "$BLOG_URL" --output /tmp/post.json
```

### Step 3: 13명 패널 병렬 실행

```bash
OUT_DIR="/tmp/panel_${TICKER//./_}"
python plugins/investor-personas/skills/persona-panel/scripts/run_panel.py \
    "$TICKER" \
    --market /tmp/market_${TICKER//./_}.json \
    --post /tmp/post.json \
    --output-dir "$OUT_DIR" \
    --max-workers 4
```

**주의**: Cowork bash sandbox는 45초 timeout이라 13명 호출은 로컬 wrapper(`run_arena.sh` 류) 또는 사용자 머신 Terminal에서 실행 권장.

### Step 4: 종합

```bash
python plugins/investor-personas/skills/persona-panel/scripts/aggregate_panel.py \
    "$OUT_DIR" \
    --output "$OUT_DIR/aggregate.json"
```

### Step 5: PDF 시각화

```bash
python plugins/investor-personas/skills/persona-panel/scripts/build_panel_pdf.py \
    "$OUT_DIR/aggregate.json" \
    --output "$OUT_DIR/report.pdf"
```

### Step 6: 결과 제시

```
🎯 HD현대 (267250.KS) — Persona Panel 결과

📊 Verdict 분포 (13명):
  🟢 매수 성향: 9 (69.2%)
  🟡 중립: 3 (23.1%)
  🔴 매도 성향: 1 (7.7%)

평균 신뢰도: 71%

🎨 Style Split:
  Value 5명: 매수 3, 중립 2 → 약한 매수
  Growth 4명: 매수 4 → 강한 매수
  Risk 1명: 중립 (Taleb fragility 우려)
  Activist 1명: 매수 (Ackman)
  Macro 1명: 매수 (Druckenmiller)
  Valuation 1명: 중립 (Damodaran 30% 이내)

⚠️ Universal Concerns (5명 이상 짚는 우려):
  [valuation] 6명 — 단기 +18% 급등으로 PER 부담
  [CAPEX] 4명 — HD현대오일뱅크 설비 보강 자본부담

💎 Unique Alpha:
  Druckenmiller만 본 catalyst: 외국인 자금 유입 모멘텀
  Cathie Wood만 본 우려: HD현대오일뱅크 친환경 전환 시 disruption 위험

💰 비용: $1.85 (13명 × ~$0.14)
📁 결과: /tmp/panel_267250_KS/report.pdf
```

## 비용 가이드

| 모드 | 모델 | 페르소나당 | 13명 전체 |
|---|---|---|---|
| `--quick` | gpt-4.1 | $0.04-0.08 | $0.50-1.00 |
| 기본 | gpt-5.5 + reasoning=high | $0.10-0.20 | $1.30-2.60 |
| `--multi-model` | gpt-5.5 + gemini-3.1 (반반) | $0.08-0.15 | $1.00-2.00 |

## Roundtable 변형

`--roundtable` 옵션 시 각 페르소나가 다른 페르소나의 의견을 본 후 자신의 verdict를 한 번 더 업데이트. 의견 갱신 비용 추가.
