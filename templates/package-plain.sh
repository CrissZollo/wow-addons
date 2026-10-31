#!/usr/bin/env bash
# Build script for a plain addon (no helper program). Copy it to <Addon>/build/package.sh.
# It makes dist/<Addon>-Windows.zip and dist/<Addon>-Linux.zip: the <Addon>/ folder plus the
# Addon Updater, whose installer puts the addon into the game and keeps it up to date.
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd)
ADDON=$(basename "$ROOT")
DIST=$ROOT/dist
VERSION=$(sed -n 's/^## Version: *//p' "$ROOT/$ADDON.toc" | tr -d '\r')
. "$ROOT/../updater/bundle.sh"
rm -rf "$DIST" && mkdir -p "$DIST"

common() {  # $1 = package folder; the addon files are the ones updater/make-manifest.py lists
    mkdir -p "$1/$ADDON"
    find "$ROOT" -maxdepth 1 -type f \( -name '*.toc' -o -name '*.lua' -o -name '*.xml' \) -exec cp {} "$1/$ADDON/" \;
    if [ -d "$ROOT/media" ]; then cp -r "$ROOT/media" "$1/$ADDON/"; fi
    add_updater "$1"
}

# ---------------------------------------------------------------- Windows
WIN=$DIST/$ADDON-Windows
common "$WIN"
add_python "$WIN"
printf '@echo off\r\nchcp 65001 >nul\r\ntitle %s\r\n"%%~dp0python\\python.exe" "%%~dp0updater\\updater.py" install --addon %s --addon-dir "%%~dp0%s"\r\necho.\r\npause\r\n' \
    "$ADDON" "$ADDON" "$ADDON" > "$WIN/Install $ADDON.bat"
sed 's/$/\r/' > "$WIN/README.txt" <<TXT
$ADDON $VERSION for Windows (WoW Forever).

INSTALL
 1. Extract this zip (right-click -> Extract All).
 2. Double-click "Install $ADDON.bat".
    If Windows says "Windows protected your PC": More info -> Run anyway.
    It finds WoW Forever, puts $ADDON in the game and turns on automatic updates.
 3. Restart WoW.
 You can delete the extracted folder afterwards.

UPDATES
 Automatic: the Addon Updater checks for new versions every 30 minutes and
 installs them. In game, /updates shows the versions.

UNINSTALL
 Delete the $ADDON folder in _forever_\\Interface\\AddOns. The updater notices
 and stops updating it.

Full guide: https://github.com/CrissZollo/wow-addons/wiki/$ADDON
TXT

# ---------------------------------------------------------------- Linux
LIN=$DIST/$ADDON-Linux
common "$LIN"
cp "$ROOT/../updater/install-plain.sh" "$LIN/install.sh"
chmod +x "$LIN/install.sh"
cat > "$LIN/README.txt" <<TXT
$ADDON $VERSION for Linux (WoW Forever through Wine / Proton: Heroic,
Lutris, Steam, Bottles...).

INSTALL
  Open a terminal in this folder and run:   bash install.sh
  It finds WoW Forever, puts $ADDON in the game and turns on automatic updates
  (the Addon Updater, a systemd user service). Then restart WoW.

UPDATES
  Automatic, every 30 minutes. In game, /updates shows the versions.

UNINSTALL
  Delete the $ADDON folder in _forever_/Interface/AddOns. The updater notices
  and stops updating it.

Full guide: https://github.com/CrissZollo/wow-addons/wiki/$ADDON
TXT

zip_dirs "$DIST" "$ADDON-Windows" "$ADDON-Linux"
