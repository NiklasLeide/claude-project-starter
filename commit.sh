#!/bin/bash
# commit.sh — enforced commit workflow
# Usage: ./commit.sh "your commit message"
# Auto-stages docs/, src/, config files. Blocks commit if CHANGELOG not updated with src/ changes.

set -e

if [ -z "$1" ]; then
  echo 'Usage: ./commit.sh "commit message"' && exit 1
fi

git add docs/ src/ .claude/ 2>/dev/null || true
git add *.json *.ts *.js *.sh *.md *.toml *.py *.bat 2>/dev/null || true

SRC_CHANGED=$(git diff --cached --name-only | grep "^src/" || true)
CHANGELOG_CHANGED=$(git diff --cached --name-only | grep "CHANGELOG.md" || true)

if [ -n "$SRC_CHANGED" ] && [ -z "$CHANGELOG_CHANGED" ]; then
  echo "ERROR: src/ changed but CHANGELOG.md was not updated. Update it first."
  exit 1
fi

git commit -m "$1" && git push
