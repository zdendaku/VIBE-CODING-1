#!/usr/bin/env bash
# Sync homework content from the course repo into this publish repo.
#
# Source : <course-repo>/homework/zdendaku@gmail.com/
# Target : this directory (the publish repo)
#
# Usage:
#   ./sync.sh                  # rsync, then print git status
#   ./sync.sh --dry-run        # show what would change, no writes
#   ./sync.sh --commit "msg"   # rsync + git commit -m "msg"
#   ./sync.sh --push "msg"     # rsync + git commit -m "msg" + git push
#   ./sync.sh --help           # this help

set -euo pipefail

SRC="/media/zdenek/DevDisk/DEV/laba/VIBE-CODING-1/homework/zdendaku@gmail.com/"
DEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Files that live in the publish repo only — never overwrite or delete them.
EXCLUDES=(
  "--exclude=/.git"
  "--exclude=/.gitignore"
  "--exclude=/README.md"
  "--exclude=/sync.sh"
  "--exclude=__pycache__"
  "--exclude=*.pyc"
  "--exclude=.venv"
  "--exclude=.pytest_cache"
  "--exclude=.ruff_cache"
  "--exclude=.mypy_cache"
  "--exclude=.claude/settings.local.json"
)

usage() {
  sed -n '2,12p' "$0" | sed 's/^# \{0,1\}//'
}

main() {
  local mode="sync"
  local message=""
  local rsync_flags=("-av" "--delete")

  case "${1:-}" in
    --help|-h)
      usage
      exit 0
      ;;
    --dry-run|-n)
      rsync_flags+=("--dry-run")
      mode="dry"
      ;;
    --commit)
      mode="commit"
      message="${2:-}"
      if [[ -z "$message" ]]; then
        echo "error: --commit needs a message" >&2
        exit 2
      fi
      ;;
    --push)
      mode="push"
      message="${2:-}"
      if [[ -z "$message" ]]; then
        echo "error: --push needs a message" >&2
        exit 2
      fi
      ;;
    "" )
      ;;
    *)
      echo "error: unknown flag '$1'" >&2
      usage >&2
      exit 2
      ;;
  esac

  if [[ ! -d "$SRC" ]]; then
    echo "error: source not found: $SRC" >&2
    exit 1
  fi

  echo ">>> rsync $SRC  ->  $DEST_DIR"
  rsync "${rsync_flags[@]}" "${EXCLUDES[@]}" "$SRC" "$DEST_DIR/"

  if [[ "$mode" == "dry" ]]; then
    echo
    echo "Dry run only — no changes written."
    exit 0
  fi

  cd "$DEST_DIR"

  echo
  echo ">>> git status"
  git status --short

  if [[ "$mode" == "sync" ]]; then
    echo
    echo "Sync done. Next: review the diff, then commit & push manually,"
    echo "or rerun with:  $0 --push \"<commit message>\""
    exit 0
  fi

  if git diff --cached --quiet && git diff --quiet; then
    echo
    echo "Nothing to commit — working tree is clean."
    exit 0
  fi

  git add -A
  git commit -m "$message"

  if [[ "$mode" == "push" ]]; then
    git push
  fi
}

main "$@"
