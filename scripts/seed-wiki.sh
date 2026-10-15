#!/usr/bin/env bash
# Seed GitHub Wiki from docs/ after the Wiki feature is enabled.
# Usage (from repo root, with git credentials):
#   bash scripts/seed-wiki.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OWNER="${OWNER:-Pooya-Ideas}"
REPO="${REPO:-markitdown-cli}"
WIKI_URL="https://github.com/${OWNER}/${REPO}.wiki.git"
TMP="$(mktemp -d)"
cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

echo "Cloning wiki (must already exist — create the first page on GitHub if clone fails)..."
if ! git clone "$WIKI_URL" "$TMP/wiki"; then
  echo ""
  echo "Wiki not initialized yet."
  echo "1) Open https://github.com/${OWNER}/${REPO}/wiki"
  echo "2) Click 'Create the first page' and save (any content)."
  echo "3) Re-run: bash scripts/seed-wiki.sh"
  exit 1
fi

cp "$ROOT/docs/Home.md" "$TMP/wiki/Home.md"
cp "$ROOT/docs/_Sidebar.md" "$TMP/wiki/_Sidebar.md"
for f in Installation Usage Persian-PDF Troubleshooting Architecture \
         Contributing Code-of-Conduct Security Accessibility; do
  src="$ROOT/docs/${f}.md"
  if [[ -f "$src" ]]; then
    cp "$src" "$TMP/wiki/${f}.md"
  fi
done

cd "$TMP/wiki"
git add -A
if git diff --cached --quiet; then
  echo "Wiki already up to date."
  exit 0
fi
git commit -m "Sync wiki pages from docs/"
git push origin HEAD
echo "Wiki updated: https://github.com/${OWNER}/${REPO}/wiki"
