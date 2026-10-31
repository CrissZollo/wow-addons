#!/usr/bin/env bash
# Builds the downloads for a release:
#   dist/FirstKills-Windows.zip  addon + watcher + portable Python + .bat files (nothing to install)
#   dist/FirstKills-Linux.zip    addon + watcher + install.sh (uses the system's python3)
# Run from anywhere.
set -euo pipefail
PY_VERSION=3.14.10
ROOT=$(cd "$(dirname "$0")/.." && pwd)
DIST=$ROOT/dist
CACHE=${XDG_CACHE_HOME:-$HOME/.cache}/firstkills-build
EMBED=$CACHE/python-$PY_VERSION-embed-amd64.zip
VERSION=$(sed -n 's/^## Version: *//p' "$ROOT/FirstKills.toc" | tr -d '\r')

mkdir -p "$CACHE" "$DIST"
if [ ! -f "$EMBED" ]; then
    echo "downloading portable Python $PY_VERSION"
    curl -fsSL --proto '=https' -o "$EMBED.part" \
        "https://www.python.org/ftp/python/$PY_VERSION/python-$PY_VERSION-embed-amd64.zip"
    mv "$EMBED.part" "$EMBED"
fi

common() {  # $1 = package folder: the addon and the watcher
    rm -rf "$1"
    mkdir -p "$1/FirstKills" "$1/watcher"
    cp "$ROOT/FirstKills.toc" "$ROOT/FirstKills.lua" "$1/FirstKills/"
    cp "$ROOT/watcher/wow-firstkills.py" "$ROOT/watcher/progress.py" "$1/watcher/"
    chmod +x "$1/watcher/wow-firstkills.py"
}

# ---------------------------------------------------------------- Windows
WIN=$DIST/FirstKills-Windows
common "$WIN"
mkdir -p "$WIN/python"
(cd "$WIN/python" && unzip -q "$EMBED")

bat() {  # name, command; Windows wants CRLF line endings
    printf '@echo off\r\nchcp 65001 >nul\r\ntitle FirstKills\r\n"%%~dp0python\\python.exe" "%%~dp0watcher\\wow-firstkills.py" %s\r\necho.\r\npause\r\n' "$2" > "$WIN/$1"
}
bat "Start FirstKills.bat" start
bat "Stop FirstKills.bat" stop
bat "FirstKills Setup.bat" setup

sed 's/$/\r/' > "$WIN/README.txt" <<TXT
FirstKills $VERSION for Windows - posts your WoW Forever first kills, level
milestones and progress reports to a Discord channel. Nothing to install.

You need the Discord webhook URL from whoever runs the Discord channel.

FIRST TIME
 1. Extract this zip somewhere permanent, e.g. Documents\FirstKills-Windows
    (don't run it from inside the zip).
 2. Double-click "Start FirstKills.bat".
    If Windows says "Windows protected your PC": More info -> Run anyway.
    It finds WoW Forever, installs the addon, asks for the webhook URL and
    sends a test message to Discord.
 3. Answer Y to "start automatically when Windows starts".
 4. Restart WoW. In game, type /fk - it should say combat logging is ON.

FILES
 Start FirstKills.bat   start it (runs setup the first time)
 Stop FirstKills.bat    stop it
 FirstKills Setup.bat   change the webhook, reinstall the addon, autostart on/off

UPDATING
 Download the new zip, run "Stop FirstKills.bat" in the old folder, replace the
 folder with the new one, then run "Start FirstKills.bat" (it also updates the
 addon in the game and keeps your settings).

Settings and history: %APPDATA%\FirstKills
Full guide: https://github.com/CrissZollo/wow-addons/tree/main/FirstKills
TXT

# ---------------------------------------------------------------- Linux
LIN=$DIST/FirstKills-Linux
common "$LIN"
cp "$ROOT/build/linux/install.sh" "$ROOT/build/linux/uninstall.sh" "$LIN/"
chmod +x "$LIN/install.sh" "$LIN/uninstall.sh"
cat > "$LIN/README.txt" <<TXT
FirstKills $VERSION for Linux (WoW Forever through Wine / Proton: Heroic,
Lutris, Steam, Bottles...). Posts your first kills, level milestones and
progress reports to a Discord channel.

You need the Discord webhook URL from whoever runs the Discord channel,
and python3 (already installed on almost every distro).

INSTALL / UPDATE
  Open a terminal in this folder and run:   bash install.sh
  It copies FirstKills to ~/.local/share/FirstKills, adds the 'firstkills'
  command, finds WoW Forever, installs the addon, asks for the webhook URL
  and sets up autostart (systemd user service). Then restart WoW and type /fk.

COMMANDS
  firstkills setup     change the webhook, reinstall the addon, autostart
  firstkills stop      stop it          firstkills start   start it
  firstkills test      post sample cards to Discord

UNINSTALL
  bash uninstall.sh

Full guide: https://github.com/CrissZollo/wow-addons/tree/main/FirstKills
TXT

# ---------------------------------------------------------------- zip
cd "$DIST"
for d in FirstKills-Windows FirstKills-Linux; do
    rm -f "$d.zip"
    zip -qr "$d.zip" "$d"
    echo "built $DIST/$d.zip ($(du -h "$d.zip" | cut -f1))"
done
