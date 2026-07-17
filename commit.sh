#!/bin/bash
# commit.sh — enforced commit workflow
# Usage: ./commit.sh "your commit message"
# Stages all tracked/new files (git add -A, .gitignore decides). Prints what
# was staged — never stages silently (old pathspec version staged NOTHING in
# repos without src/). Blocks commit if CHANGELOG not updated with src/ changes.

set -e

if [ -z "$1" ]; then
  echo 'Usage: ./commit.sh "commit message"' && exit 1
fi

git add -A

STAGED=$(git diff --cached --name-only)
if [ -z "$STAGED" ]; then
  echo "commit.sh: nothing to commit — no changes staged."
  exit 0
fi
echo "commit.sh: staged:"
echo "$STAGED" | sed 's/^/  - /'

SRC_CHANGED=$(echo "$STAGED" | grep "^src/" || true)
CHANGELOG_CHANGED=$(echo "$STAGED" | grep "CHANGELOG.md" || true)

if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
  echo "ERROR: src/ changed but CHANGELOG.md was not updated. Update it first."
  exit 1
fi

git commit -m "$1" && git push
