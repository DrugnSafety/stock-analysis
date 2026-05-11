#!/bin/bash
# 메르 블로그 한 글에 대한 thesis-first arena 풀 파이프라인.
# 사용자 macOS Terminal에서 직접 실행 (Cowork bash sandbox 제약 없음).
#
# 사용:
#   ./run_arena.sh <BLOG_URL> [--skip gemini|claude|...] [--dry-run]

set -e

# 0. 환경 결정
WORKSPACE="${WORKSPACE:-/Users/mingyukang/Documents/Claude/Projects/주식 분석}"
PLUGIN_ROOT="$WORKSPACE/plugins/multi-model-arena"
NAVER_PLUGIN="$WORKSPACE/plugins/naver-blog-investment"
ENV_FILE="$WORKSPACE/.env"

# .env 로드
if [ -f "$ENV_FILE" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    set +a
else
    echo "❌ .env 파일을 찾을 수 없습니다: $ENV_FILE"
    exit 1
fi

# 1. 인자 파싱
URL=""
SKIP=""
DRY_RUN=0
SKIP_THESIS=0
ONLY=""

while [ $# -gt 0 ]; do
    case "$1" in
        --skip)
            SKIP="$2"; shift 2 ;;
        --only)
            ONLY="$2"; shift 2 ;;
        --skip-thesis)
            SKIP_THESIS=1; shift ;;
        --dry-run)
            DRY_RUN=1; shift ;;
        http*)
            URL="$1"; shift ;;
        *)
            echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [ -z "$URL" ]; then
    echo "Usage: $0 <BLOG_URL> [--skip gemini] [--only openai] [--skip-thesis] [--dry-run]"
    exit 1
fi

# 2. 출력 디렉토리
TS=$(date +%Y-%m-%d_%H%M)
SLUG=$(echo "$URL" | sed 's|.*/||' | head -c 30)
OUT_DIR="$WORKSPACE/.analysis-log/arena/${TS}_${SLUG}"
mkdir -p "$OUT_DIR"

echo "════════════════════════════════════════════════════════"
echo "  Multi-Model Arena — Thesis-First Pipeline"
echo "════════════════════════════════════════════════════════"
echo "  URL:        $URL"
echo "  Out:        $OUT_DIR"
echo "  Skip:       ${SKIP:-(none)}"
echo "  Only:       ${ONLY:-(all)}"
echo "  Skip thesis: $SKIP_THESIS"
echo "  Dry-run:    $DRY_RUN"
echo "  OpenAI model: ${OPENAI_MODEL:-(env)}"
echo "  Gemini model: ${GOOGLE_MODEL:-(env)}"
echo "════════════════════════════════════════════════════════"
echo

if [ "$DRY_RUN" = "1" ]; then
    echo "🔎 dry-run: 비용 추정만 — pipeline 5단계 × 모델 2개 × $0.30 ≈ $3.00"
    exit 0
fi

# 3. 본문 스크래핑
echo "[1/6] 본문 스크래핑..."
python3 "$NAVER_PLUGIN/skills/naver-blog-scraper/scripts/scrape_naver_blog.py" \
    "$URL" --output "$OUT_DIR/post.json" || {
    echo "❌ 스크래핑 실패"; exit 1; }

# 4. Thesis 추출
if [ "$SKIP_THESIS" = "0" ]; then
    echo
    echo "[2/6] ★ Thesis 추출 (gpt-5.5 + reasoning=high)..."
    python3 "$PLUGIN_ROOT/skills/thesis-extractor/scripts/extract_theses.py" \
        "$OUT_DIR/post.json" \
        --output "$OUT_DIR/thesis_list.json" \
        --blog-url "$URL" || echo "  ⚠️  thesis 추출 실패, skip"

    if [ -f "$OUT_DIR/thesis_list.json" ]; then
        N=$(python3 -c "import json; print(len(json.load(open('$OUT_DIR/thesis_list.json')).get('theses',[])))")
        echo "  → $N 개 thesis 추출됨"
    fi

    echo
    echo "[3/6] ★ Thesis 평가 (4-Analyst per thesis)..."
    python3 "$PLUGIN_ROOT/skills/thesis-evaluator/scripts/evaluate_theses.py" \
        "$OUT_DIR/thesis_list.json" \
        --output-dir "$OUT_DIR/thesis_eval" \
        --analysts macro,industry,empirical,counter || echo "  ⚠️  thesis 평가 실패, skip"

    echo
    echo "[4/6] ★ Thesis → 종목 매핑..."
    python3 "$PLUGIN_ROOT/skills/thesis-to-stocks/scripts/map_to_stocks.py" \
        "$OUT_DIR/thesis_list.json" \
        --eval-dir "$OUT_DIR/thesis_eval" \
        --output "$OUT_DIR/thesis_to_stocks.json" || echo "  ⚠️  매핑 실패, skip"
else
    echo "[2-4/6] thesis 단계 건너뜀"
fi

# 5. 종목 추출 arena (claude/openai/gemini)
echo
echo "[5/6] 종목 추출 arena..."
INCLUDE="claude,openai,gemini"
[ -n "$ONLY" ] && INCLUDE="$ONLY"
for x in $(echo "$SKIP" | tr ',' ' '); do
    INCLUDE=$(echo "$INCLUDE" | sed "s/$x,//; s/,$x//; s/^$x$//")
done

mkdir -p "$OUT_DIR/arena_extract"
python3 "$PLUGIN_ROOT/skills/arena-orchestrator/scripts/orchestrate_extract.py" \
    "$OUT_DIR/post.json" \
    --output-dir "$OUT_DIR/arena_extract" \
    --include "$INCLUDE" \
    --blog-url "$URL"

# 6. consensus + PDF
echo
echo "[6/6] consensus build + PDF..."
python3 "$PLUGIN_ROOT/skills/consensus-builder/scripts/build_consensus.py" \
    "$OUT_DIR/arena_extract" \
    --type extract \
    --output "$OUT_DIR/consensus_extract.json"

python3 "$PLUGIN_ROOT/skills/consensus-builder/scripts/visualize.py" \
    "$OUT_DIR/consensus_extract.json" \
    --output "$OUT_DIR/consensus_extract.pdf" \
    --format pdf

# 7. Final report (thesis-first 통합)
if [ -f "$OUT_DIR/thesis_to_stocks.json" ] && [ -f "$OUT_DIR/consensus_extract.json" ]; then
    echo
    echo "[+] Final thesis-first report 생성..."
    python3 "$PLUGIN_ROOT/skills/consensus-builder/scripts/build_thesis_report.py" \
        --thesis "$OUT_DIR/thesis_list.json" \
        --eval-dir "$OUT_DIR/thesis_eval" \
        --mapping "$OUT_DIR/thesis_to_stocks.json" \
        --consensus "$OUT_DIR/consensus_extract.json" \
        --output "$OUT_DIR/report.pdf" || echo "  ⚠️  최종 리포트 생성 실패"
fi

echo
echo "════════════════════════════════════════════════════════"
echo "  ✅ 완료"
echo "  📁 결과: $OUT_DIR"
echo "════════════════════════════════════════════════════════"
ls -la "$OUT_DIR/"
