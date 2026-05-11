# Multi-Model Arena — 빠른 시작 가이드

## 1단계: API 키 입력

워크스페이스 루트에 `.env` 파일을 만드세요 (또는 `.env.template`을 복사):

```bash
cp /Users/mingyukang/Documents/Claude/Projects/주식\ 분석/plugins/multi-model-arena/.env.template \
   /Users/mingyukang/Documents/Claude/Projects/주식\ 분석/.env
```

그리고 실제 키 값을 채워주세요:

```env
OPENAI_API_KEY=sk-proj-...
OPENAI_MODEL=gpt-5.5
OPENAI_REASONING_EFFORT=high

GOOGLE_API_KEY=AIzaSy...
GOOGLE_MODEL=gemini-3.1
GOOGLE_DEEP_THINK=true

ARENA_MAX_COST_USD=2.00
```

## 2단계: 의존성 설치

```bash
pip install -r /Users/mingyukang/Documents/Claude/Projects/주식\ 분석/plugins/multi-model-arena/requirements.txt
```

또는 Cowork 세션에서 Claude에게 부탁:
> "multi-model-arena requirements 설치해줘"

## 3단계: 키 검증

```bash
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/api-key-manager/scripts/check_keys.py"
```

성공 시 출력:
```
=== API Key 검증 ===

OpenAI: sk-pr...abc1
  ✅ gpt-5.5 사용 가능

Google: AIza...xyz9
  ✅ gemini-3.1 사용 가능

💰 비용 한도: $2.00/arena
✅ 두 키 모두 설정됨 — arena 실행 가능
```

## 4단계: 첫 arena 실행

### 종목 추출 arena (메르 글에서 모든 모델이 종목 추출)

```bash
TS=$(date +%Y%m%d_%H%M%S)
OUT="/tmp/arena_extract_$TS"

# (이전 세션 post.json 재사용 또는 새로 스크래핑)
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/arena-orchestrator/scripts/orchestrate_extract.py" \
    /tmp/post.json \
    --output-dir "$OUT" \
    --include openai,gemini   # claude는 Cowork 세션이 별도 처리

# Claude 인라인 추출 (Cowork 환경에서 Claude에게 부탁):
# "이 post.json 기반으로 stock-extractor SKILL.md 따라 종목 추출하고 $OUT/claude.json에 저장해줘"

# Consensus 분석
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/consensus-builder/scripts/build_consensus.py" \
    "$OUT" --type extract \
    --output "$OUT/consensus.json"

# 시각화 (HTML)
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/consensus-builder/scripts/visualize.py" \
    "$OUT/consensus.json" \
    --output "$OUT/consensus.html"
```

### 7-role 분석 arena (단일 종목)

```bash
TICKER="439260.KS"
OUT="/tmp/arena_analyze_${TICKER//./_}"

# 1) 시장 데이터
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/naver-blog-investment/skills/trading-analysis/scripts/market_data.py" \
    "$TICKER" --output "/tmp/market_${TICKER//./_}.json"

# 2) Arena dispatch
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/arena-orchestrator/scripts/orchestrate_analyze.py" \
    "$TICKER" \
    --market "/tmp/market_${TICKER//./_}.json" \
    --post /tmp/post.json \
    --output-dir "$OUT" \
    --include openai,gemini

# 3) Claude 인라인 분석 (Cowork에서 Claude에게)

# 4) Consensus
python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/consensus-builder/scripts/build_consensus.py" \
    "$OUT" --type analyze \
    --output "$OUT/consensus.json"

python "/Users/mingyukang/Documents/Claude/Projects/주식 분석/plugins/multi-model-arena/skills/consensus-builder/scripts/visualize.py" \
    "$OUT/consensus.json" \
    --output "$OUT/consensus.pdf" --format pdf
```

## 비용 가이드

1회 arena 실행당 추정 비용 (입력 토큰 ~5K, 출력 ~2K 기준):

| 작업 | OpenAI (gpt-5.5) | Google (gemini-3.1) | 합계 |
|---|---|---|---|
| Extract (1글) | $0.20-0.50 | $0.10-0.30 | $0.30-0.80 |
| Analyze (1종목) | $0.30-0.80 | $0.15-0.40 | $0.45-1.20 |
| Debate (1종목) | $0.30-0.80 | $0.15-0.40 | $0.45-1.20 |

`ARENA_MAX_COST_USD`로 한도 설정 가능.

## 트러블슈팅

| 문제 | 해결 |
|---|---|
| `OPENAI_API_KEY 누락` | .env 파일 위치·이름 확인 (.env.template과 같은 디렉토리에 .env로) |
| `Model gpt-5.5 not found` | OpenAI 플랜 확인. fallback gpt-4.1로 자동 전환됨 |
| `Model gemini-3.1 not matched` | Google AI Studio에서 모델 가용성 확인. fallback gemini-2.5-pro로 자동 전환 |
| `unknown parameter reasoning_effort` | OpenAI 모델이 reasoning을 지원하지 않음. 자동 fallback 진행됨 |
| Gemini 응답 깨짐 | `GOOGLE_DEEP_THINK=false`로 thinking 비활성화 시도 |

## 보안

- `.env`는 `.gitignore`에 등록되어 절대 git에 커밋되지 않음
- 모든 로그·결과 파일에는 키 첫 4자리 + 끝 4자리만 마스킹되어 저장
- 키는 메모리에서만 보관, 디스크에 평문 저장 안 됨 (.env 제외)
