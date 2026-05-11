---
name: arena-analyze
description: Multi-Model Arena로 단일 종목 7-role 분석. Claude(현재 세션) + GPT-5.5 + Gemini 3.1을 병렬 실행하여 verdict 분포, agreement level, perspectives spread, Bull/Bear thesis의 모델별 차이를 분석. .env에 OPENAI_API_KEY, GOOGLE_API_KEY가 설정되어 있어야 한다.
---

# /arena-analyze

3개 모델을 동시 가동해 단일 ticker의 verdict 신뢰도를 calibration한다.

## 사용법

```
/arena-analyze <TICKER> [--post BLOG_URL_OR_JSON]
```

예시:
- `/arena-analyze 439260.KS --post https://blog.naver.com/ranto28/224264942275`
- `/arena-analyze NVDA` (블로그 컨텍스트 없이)

## 절차

### Step 1: 환경 + 시장 데이터 준비

```bash
# 키 검증
python plugins/multi-model-arena/skills/api-key-manager/scripts/check_keys.py

# 시장 데이터
python plugins/naver-blog-investment/skills/trading-analysis/scripts/market_data.py \
    439260.KS --output /tmp/market_439260_KS.json
```

### Step 2: (선택) 블로그 컨텍스트

블로그 URL이 주어지면 본문 수집:
```bash
python plugins/naver-blog-investment/skills/naver-blog-scraper/scripts/scrape_naver_blog.py \
    "$URL" --output /tmp/post.json
```

### Step 3: Arena 디스패치

```bash
OUT_DIR="/tmp/arena_analyze_${TICKER//./_}"
python plugins/multi-model-arena/skills/arena-orchestrator/scripts/orchestrate_analyze.py \
    "$TICKER" --market /tmp/market_${TICKER//./_}.json \
    --post /tmp/post.json --output-dir "$OUT_DIR" \
    --include claude,openai,gemini
```

### Step 4: Claude 인라인 분석

Claude는 trading-analysis SKILL.md의 7-role 지침을 따라 분석하고 `$OUT_DIR/claude.json`에 덮어쓰기.

### Step 5: Consensus

```bash
python plugins/multi-model-arena/skills/consensus-builder/scripts/build_consensus.py \
    "$OUT_DIR" --type analyze --output /tmp/consensus_analyze.json
```

### Step 6: 시각화

```bash
python plugins/multi-model-arena/skills/consensus-builder/scripts/visualize.py \
    /tmp/consensus_analyze.json --output /tmp/consensus_analyze.pdf --format pdf
```

### Step 7: 사용자에게 결과 제시

```
✅ Arena Analysis — 439260.KS (대한조선)

🏆 Weighted Verdict: BUY (신뢰도 72%)
Agreement: medium (2/3 합의)

| 모델 | Verdict | 신뢰도 | Horizon |
| Claude | BUY | 78% | 6-12 months |
| OpenAI | BUY | 81% | 6-12 months |
| Gemini | HOLD | 62% | 3-6 months ← 이견 |

📈 4-Analyst Perspectives (1-5 점수, spread)
| 역할 | Claude | OpenAI | Gemini | Spread |
| Fundamentals | 4 | 5 | 3 | 2 ⚠️ |
| Technical | 4 | 4 | 4 | 0 ✅ |
| News | 4 | 5 | 4 | 1 |
| Sentiment | 3 | 4 | 3 | 1 |

🎯 Spread 분석
- Fundamentals 의견 갈림 (3-5) → Gemini가 valuation 우려 강조 vs OpenAI는 사이클 정점 대비 저렴
- Technical 만장일치 → 단기 모멘텀 부족(+5.83%)에 대한 합의

🐂 Bull Thesis 차이
- Claude: 본문 Panamax 테마 직접 수혜 강조
- OpenAI: 신규 상장 후 외국인 자금 유입 가능성
- Gemini: 단기 underperform이 mean reversion catalyst

🐻 Bear Thesis 차이
- Claude: 시장 반영 지연 = 정보 부재 가능성
- OpenAI: 케이조선 대표 종목 vs 단일 야드 capacity
- Gemini: VLCC 비중 약함 → super-cycle 후행

💰 비용: $0.34 (OpenAI) + $0.21 (Google) = $0.55
📁 결과: /tmp/consensus_analyze.pdf
```
