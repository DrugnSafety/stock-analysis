#!/usr/bin/env bash
# sync_commands.sh — Cowork commands/ + plugins/*/commands/ → .claude/commands/ 동기화
#
# Claude Code는 `.claude/commands/*.md`를 슬래시 명령어로 자동 인식합니다.
# Cowork 모드는 `commands/*.md` 와 `plugins/*/commands/*.md`를 인식합니다.
#
# 이 스크립트는 두 환경에서 동일한 슬래시 명령어가 작동하도록 동기화합니다.
#
# 사용법:
#   bash scripts/sync_commands.sh
#
# 자동 실행 (post-commit hook으로 등록 가능):
#   ln -sf ../../scripts/sync_commands.sh .git/hooks/post-commit

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

mkdir -p .claude/commands

count=0

# Cowork commands/ → .claude/commands/
if [ -d commands ]; then
    for f in commands/*.md; do
        [ -f "$f" ] || continue
        cp "$f" ".claude/commands/$(basename "$f")"
        count=$((count + 1))
    done
fi

# Plugin commands → .claude/commands/
for f in plugins/*/commands/*.md; do
    [ -f "$f" ] || continue
    cp "$f" ".claude/commands/$(basename "$f")"
    count=$((count + 1))
done

echo "[sync] $count slash commands synced to .claude/commands/"
echo "[sync] Claude Code 환경에서 다음 명령어 사용 가능:"
ls .claude/commands/ | sed 's/\.md$//' | sed 's/^/  \//'
