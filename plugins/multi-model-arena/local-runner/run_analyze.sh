#!/bin/bash
# 단일 ticker에 대한 풀 7-role arena 분석 (블로그 컨텍스트 옵션).
# 사용자 macOS Terminal에서 직접 실행.
#
# 사용:
#   ./run_analyze.sh <TICKER> [BLOG_URL] [--skip gemini]
set -e

WORKSPACE="${WORKSPACE:-/Users/mingyukang/Documents/Claude/Projects/주식 분석}"
PLUGIN_ROOT="$WORKSPACE/plugins/multi-model-arena"
NAVER_PLUGIN="$WORKSPACE/plugins/naver-blog-investment"
ENV_FILE="$WORKSPACE/.env"

[ -f "$ENV_FILE" ] && { set -a; source "$ENV_FILE"; set +a; }

TICKER=""
BLOG_URL=""
SKIP=""

while [ $# -gt 0 ]; do
    case "$1" in
        --skip) SKIP="$2"; shift 2 ;;
        http*) BLOG_URL="$1"; shift ;;
        *) TICKER="$1"; shift ;;
    esac
done

if [ -z "$TICKER" ]; then
    echo "Usage: $0 <TICKER> [BLOG_URL] [--skip gemini]"
    exit 1
fi

TS=$(date +%Y-%m-%d)
TICKER_SAFE="${TICKER//./_}"
OUT_DIR="$WORKSPACE/.analysis-log/arena/${TS}_${TICKER_SAFE}"
mkdir -p "$OUT_DIR"

echo "════════════════════════════════════════════════════════"
echo "  Arena Analyze — $TICKER"
echo "════════════════════════════════════════════════════════"

# 시장 데이터
echo "[1/3] 시장 데이터..."
python3 "$NAVER_PLUGIN/skills/trading-analysis/scripts/market_data.py" \
    "$TICKER" --output "$OUT_DIR/market.json"

# 블로그 (옵션)
POST_ARG=""
if [ -n "$BLOG_URL" ]; then
    echo "[1.5/3] 블로그 본문 (컨텍스트)..."
    python3 "$NAVER_PLUGIN/skills/naver-blog-scraper/scripts/scrape_naver_blog.py" \
        "$BLOG_URL" --output "$OUT_DIR/post.json"
    POST_ARG="--post $OUT_DIR/post.json --blog-url $BLOG_URL"
fi

# Arena
echo "[2/3] Arena dispatch..."
INCLUDE="claude,openai,gemini"
for x in $(echo "$SKIP" | tr ',' ' '); do
    INCLUDE=$(echo "$INCLUDE" | sed "s/$x,//; s/,$x//; s/^$x$//")
done

python3 "$PLUGIN_ROOT/skills/arena-orchestrator/scripts/orchestrate_analyze.py" \
    "$TICKER" --market "$OUT_DIR/market.json" $POST_ARG \
    --output-dir "$OUT_DIR/arena" --include "$INCLUDE"

# Consensus
echo "[3/3] consensus..."
python3 "$PLUGIN_ROOT/skills/consensus-builder/scripts/build_consensus.py" \
    "$OUT_DIR/arena" --type analyze \
    --output "$OUT_DIR/consensus.json"

python3 "$PLUGIN_ROOT/skills/consensus-builder/scripts/visualize.py" \
    "$OUT_DIR/consensus.json" \
    --output "$OUT_DIR/consensus.pdf" --format pdf

echo
echo "✅ 완료: $OUT_DIR"
ls -la "$OUT_DIR/"
