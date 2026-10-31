#!/usr/bin/env bash
# Build script for a plain addon (no helper program). Copy it to <Addon>/build/package.sh.
# It makes dist/<Addon>.zip containing the <Addon>/ folder, ready to drop into Interface/AddOns.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ADDON=$(basename "$ROOT")
DIST=$ROOT/dist
rm -rf "$DIST" && mkdir -p "$DIST/$ADDON"
find "$ROOT" -maxdepth 1 -type f \( -name '*.toc' -o -name '*.lua' -o -name '*.xml' \) -exec cp {} "$DIST/$ADDON/" \;
[ -d "$ROOT/media" ] && cp -r "$ROOT/media" "$DIST/$ADDON/"
(cd "$DIST" && zip -qr "$ADDON.zip" "$ADDON")
echo "built $DIST/$ADDON.zip"
