#!/usr/bin/env bash
# Builds dist/FirstKills-Windows.zip: the addon, the watcher and a portable Python,
# so Windows users don't have to install anything. Run from anywhere.
set -euo pipefail
PY_VERSION=3.14.10
ROOT=$(cd "$(dirname "$0")/.." && pwd)
CACHE=${XDG_CACHE_HOME:-$HOME/.cache}/firstkills-build
OUT=$ROOT/dist/FirstKills-Windows
EMBED=$CACHE/python-$PY_VERSION-embed-amd64.zip

mkdir -p "$CACHE"
if [ ! -f "$EMBED" ]; then
    echo "downloading portable Python $PY_VERSION"
    curl -fL --proto '=https' -o "$EMBED.part" \
        "https://www.python.org/ftp/python/$PY_VERSION/python-$PY_VERSION-embed-amd64.zip"
    mv "$EMBED.part" "$EMBED"
fi

rm -rf "$OUT" "$OUT.zip"
mkdir -p "$OUT/FirstKills" "$OUT/watcher" "$OUT/python"
cp "$ROOT/FirstKills.toc" "$ROOT/FirstKills.lua" "$OUT/FirstKills/"
cp "$ROOT/watcher/wow-firstkills.py" "$ROOT/watcher/progress.py" "$OUT/watcher/"
(cd "$OUT/python" && unzip -q "$EMBED")

bat() {  # name, command; Windows wants CRLF line endings
    printf '@echo off\r\nchcp 65001 >nul\r\ntitle FirstKills\r\n"%%~dp0python\\python.exe" "%%~dp0watcher\\wow-firstkills.py" %s\r\necho.\r\npause\r\n' "$2" > "$OUT/$1"
}
bat "Start FirstKills.bat" start
bat "Stop FirstKills.bat" stop
bat "FirstKills Setup.bat" setup

sed 's/$/\r/' > "$OUT/README.txt" <<'TXT'
FirstKills - posts your WoW Forever first kills, level milestones and progress
reports to a Discord channel. Nothing to install.

FIRST TIME
 1. Extract this zip somewhere permanent, e.g. Documents\FirstKills
    (not inside Downloads\...zip - extract it first).
 2. Double-click "Start FirstKills.bat".
    It finds WoW Forever, installs the addon, asks for the Discord webhook URL
    (you get it from whoever runs the Discord channel) and sends a test message.
 3. Answer Y to "start automatically with Windows" and you never have to think
    about it again.
 4. Restart WoW. In game, type /fk - it should say combat logging is ON.

FILES
 Start FirstKills.bat   start it (runs setup the first time)
 Stop FirstKills.bat    stop it
 FirstKills Setup.bat   change the webhook, reinstall the addon, autostart on/off

WHAT IT POSTS
 - first kill of every kind of mob (with a picture and Wowhead link), bosses,
   enemy players: right away while you play
 - level 10/20/30... and a progress report (gear, stats, gold): when you log out
   or type /reload, if you played 5+ minutes

If Windows warns "Windows protected your PC" when you run a .bat, click
"More info" -> "Run anyway". Settings and history are in %APPDATA%\FirstKills.
TXT

(cd "$ROOT/dist" && rm -f FirstKills-Windows.zip && zip -qr FirstKills-Windows.zip FirstKills-Windows)
echo "built $ROOT/dist/FirstKills-Windows.zip ($(du -h "$ROOT/dist/FirstKills-Windows.zip" | cut -f1))"
