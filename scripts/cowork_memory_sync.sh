#!/bin/bash
# Cowork Memory Sync — 두 컴퓨터 간 Cowork memory 폴더 git 동기화
#
# 사용법:
#   ./cowork_memory_sync.sh push    # 현재 컴퓨터 memory → GitHub
#   ./cowork_memory_sync.sh pull    # GitHub → 현재 컴퓨터 memory
#   ./cowork_memory_sync.sh status  # 양쪽 비교
#
# 안전성:
#   - memory/ 폴더만 동기화 (대화 본문·token·sandbox 캐시는 sync 안 함)
#   - 자동 backup (sync 전 timestamp 폴더로 백업)
#   - .gitignore로 secret 가능성 자동 제외
#
# 셋업 (1회):
#   1. ANTHROPIC_ACCOUNT_ID·ANTHROPIC_WORKSPACE_ID·COWORK_SPACE_ID 환경변수 확인
#   2. ./cowork_memory_sync.sh init 실행

set -euo pipefail

REPO_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
COWORK_BASE="$HOME/Library/Application Support/Claude/local-agent-mode-sessions"
MIRROR_DIR="$REPO_ROOT/.cowork-memory-mirror"
BACKUP_DIR="$REPO_ROOT/.cowork-memory-backup"

# Auto-detect account/workspace/space IDs (deepest single child at each level)
detect_paths() {
  if [ ! -d "$COWORK_BASE" ]; then
    echo "[error] Cowork base path 없음: $COWORK_BASE"
    echo "  Cowork 데스크탑 앱이 설치되어 있고 한 번 이상 실행되었는지 확인"
    exit 1
  fi

  ACCOUNT_DIR=$(ls -d "$COWORK_BASE"/*/ 2>/dev/null | head -1)
  if [ -z "$ACCOUNT_DIR" ]; then
    echo "[error] account 폴더 없음 — Cowork에 한 번 로그인 후 다시 시도"
    exit 1
  fi

  WORKSPACE_DIR=$(ls -d "$ACCOUNT_DIR"*/ 2>/dev/null | head -1)
  if [ -z "$WORKSPACE_DIR" ]; then
    echo "[error] workspace 폴더 없음"
    exit 1
  fi

  SPACES_DIR="$WORKSPACE_DIR/spaces"
  if [ ! -d "$SPACES_DIR" ]; then
    echo "[error] spaces/ 폴더 없음 — 메모리 시스템 미사용 상태"
    exit 1
  fi

  # All spaces (사용자가 여러 Project를 사용할 수 있음)
  ALL_SPACES=$(ls -d "$SPACES_DIR"/*/ 2>/dev/null)
  if [ -z "$ALL_SPACES" ]; then
    echo "[error] spaces/<id>/ 하위 폴더 없음"
    exit 1
  fi

  echo "[detect] account: $(basename "$ACCOUNT_DIR")"
  echo "[detect] workspace: $(basename "$WORKSPACE_DIR")"
  echo "[detect] spaces:"
  for s in $ALL_SPACES; do echo "  - $(basename "$s")"; done
}

# Push: local memory/ → MIRROR_DIR → git commit
cmd_push() {
  detect_paths
  mkdir -p "$BACKUP_DIR"
  TS=$(date +%Y%m%d_%H%M%S)
  BACKUP_PATH="$BACKUP_DIR/push_$TS"

  # Backup current MIRROR_DIR before overwriting
  if [ -d "$MIRROR_DIR" ]; then
    cp -R "$MIRROR_DIR" "$BACKUP_PATH"
    echo "[push] previous mirror backed up: $BACKUP_PATH"
  fi

  rm -rf "$MIRROR_DIR"
  mkdir -p "$MIRROR_DIR"

  # Copy memory/ from all spaces (one folder per space)
  for s in $ALL_SPACES; do
    space_id=$(basename "$s")
    memory_src="$s/memory"
    if [ -d "$memory_src" ]; then
      dest="$MIRROR_DIR/$space_id"
      mkdir -p "$dest"
      rsync -av --delete \
            --exclude '*.token' --exclude '*.jwt' --exclude '*secret*' \
            --exclude '.DS_Store' \
            "$memory_src/" "$dest/"
      echo "[push] copied $(basename "$s")/memory ($(find "$dest" -type f | wc -l | tr -d ' ') files)"
    fi
  done

  # Git commit
  cd "$REPO_ROOT"
  git add .cowork-memory-mirror/ .gitignore 2>/dev/null || true
  git diff --cached --quiet && { echo "[push] no changes — skip commit"; return 0; }
  git commit -m "cowork-memory: sync from $(hostname) @ $(date +%Y-%m-%d_%H:%M)" || true
  git push origin main && echo "[push] ✓ pushed to GitHub"
}

# Pull: git pull → MIRROR_DIR → local memory/
cmd_pull() {
  detect_paths
  cd "$REPO_ROOT"
  git pull origin main || { echo "[pull] git pull failed"; exit 1; }

  if [ ! -d "$MIRROR_DIR" ]; then
    echo "[pull] mirror 폴더 없음 — 다른 컴퓨터에서 먼저 push 필요"
    exit 0
  fi

  mkdir -p "$BACKUP_DIR"
  TS=$(date +%Y%m%d_%H%M%S)

  # Restore each space
  for space_dir in "$MIRROR_DIR"/*/; do
    space_id=$(basename "$space_dir")
    local_memory="$SPACES_DIR/$space_id/memory"

    if [ -d "$local_memory" ]; then
      # Backup local memory before overwriting
      BACKUP_PATH="$BACKUP_DIR/pull_${TS}_${space_id}"
      cp -R "$local_memory" "$BACKUP_PATH"
      echo "[pull] local memory backed up: $BACKUP_PATH"
    fi

    mkdir -p "$local_memory"
    rsync -av --delete \
          "$space_dir/" "$local_memory/"
    echo "[pull] restored to $local_memory ($(find "$local_memory" -type f | wc -l | tr -d ' ') files)"
  done
  echo "[pull] ✓ Cowork memory updated. 다음 Cowork 세션부터 반영됨"
}

# Status: compare local vs mirror
cmd_status() {
  detect_paths

  echo ""
  echo "=== Local Cowork memory ==="
  for s in $ALL_SPACES; do
    space_id=$(basename "$s")
    memory="$s/memory"
    if [ -d "$memory" ]; then
      cnt=$(find "$memory" -type f -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
      latest=$(find "$memory" -type f -name "*.md" -exec stat -f "%m" {} \; 2>/dev/null | sort -rn | head -1)
      latest_human=$([ -n "$latest" ] && date -r "$latest" "+%Y-%m-%d %H:%M" || echo "-")
      echo "  $space_id: $cnt files, latest=$latest_human"
    fi
  done

  echo ""
  echo "=== GitHub mirror ==="
  if [ -d "$MIRROR_DIR" ]; then
    for d in "$MIRROR_DIR"/*/; do
      [ -d "$d" ] || continue
      cnt=$(find "$d" -type f -name "*.md" | wc -l | tr -d ' ')
      echo "  $(basename "$d"): $cnt files"
    done
  else
    echo "  (mirror 없음)"
  fi

  echo ""
  echo "=== Git status ==="
  cd "$REPO_ROOT"
  git log -5 --oneline -- .cowork-memory-mirror/ 2>/dev/null | sed 's/^/  /' || echo "  (커밋 이력 없음)"
}

# Init: .gitignore 설정
cmd_init() {
  cd "$REPO_ROOT"

  # Ensure .gitignore protects sensitive files even inside mirror
  if ! grep -q "cowork-memory-mirror" .gitignore 2>/dev/null; then
    cat >> .gitignore << 'EOF'

# Cowork memory mirror — protect any accidentally-copied secrets
.cowork-memory-mirror/**/*.token
.cowork-memory-mirror/**/*.jwt
.cowork-memory-mirror/**/*secret*
.cowork-memory-backup/
EOF
    echo "[init] .gitignore 업데이트 완료"
  fi

  echo "[init] ready. 사용법:"
  echo "  ./scripts/cowork_memory_sync.sh push    # 회사 → GitHub"
  echo "  ./scripts/cowork_memory_sync.sh pull    # GitHub → 집"
  echo "  ./scripts/cowork_memory_sync.sh status  # 비교"
}

# ── main ──
case "${1:-status}" in
  push)   cmd_push ;;
  pull)   cmd_pull ;;
  status) cmd_status ;;
  init)   cmd_init ;;
  *)
    echo "Usage: $0 {push|pull|status|init}"
    exit 1
    ;;
esac
