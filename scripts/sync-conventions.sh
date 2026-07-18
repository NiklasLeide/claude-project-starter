#!/bin/bash
# sync-conventions.sh — keep the public conventions file (this repo's
# shared-conventions.md, canonical for chat surfaces) and the plugin's copy
# (distributed to Claude Code) in step. Run at EVERY plugin bump, from a
# machine that has both repos. Enforcement in code, not memory (DEC-009).
#
#   bash scripts/sync-conventions.sh [path-to-marketplace-repo]        # check
#   bash scripts/sync-conventions.sh [path] --push-to-plugin           # root -> plugin
#
# Exit 0 = in sync (or copy done) · 1 = drift detected · 2 = setup error
set -euo pipefail
KIT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MARKET="${1:-$HOME/tools/niklas-marketplace}"
SRC="$KIT_ROOT/shared-conventions.md"
DEST="$(find "$MARKET" -name 'shared-conventions.md' -path '*project*' 2>/dev/null | head -1 || true)"
[[ -f "$SRC" ]] || { echo "setup error: $SRC missing"; exit 2; }
[[ -n "$DEST" && -f "$DEST" ]] || { echo "setup error: no shared-conventions.md found under $MARKET"; exit 2; }
if [[ "${2:-}" == "--push-to-plugin" ]]; then
  cp "$SRC" "$DEST"
  echo "copied: $SRC -> $DEST"
  echo "next: commit in $MARKET and bump the plugin version"
  exit 0
fi
if diff -u "$DEST" "$SRC" >/dev/null; then
  echo "in sync: plugin copy == root copy"
else
  echo "DRIFT between plugin copy and root copy (root is canonical):"
  diff -u "$DEST" "$SRC" | head -40 || true
  echo "run with --push-to-plugin at next bump"
  exit 1
fi
