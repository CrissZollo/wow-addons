#!/usr/bin/env bash
# Publishes the pages in wiki/ to the repository's GitHub wiki.
# Edit the pages here (they're versioned with the code), then run this.
set -euo pipefail
WIKI_REMOTE=git@github-crisszollo:CrissZollo/wow-addons.wiki.git
WIKI_URL=https://github.com/CrissZollo/wow-addons/wiki
ROOT=$(cd "$(dirname "$0")" && pwd)
"$ROOT/check-wiki.py" || { echo "fix the format problems above first (templates/README.md)"; exit 1; }
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

if ! git clone -q "$WIKI_REMOTE" "$TMP/wiki" 2>/dev/null; then
    echo "The GitHub wiki doesn't exist yet. Open $WIKI_URL, click"
    echo "'Create the first page', save it as is, then run this again."
    exit 1
fi
cd "$TMP/wiki"
find . -maxdepth 1 -name '*.md' -delete
cp "$ROOT"/wiki/*.md .
git add -A
if git diff --cached --quiet; then
    echo "wiki already up to date: $WIKI_URL"
    exit 0
fi
git commit -qm "Update wiki from wow-addons/wiki"
git push -q origin HEAD
echo "wiki updated: $WIKI_URL"
