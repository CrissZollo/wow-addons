#!/usr/bin/env bash
# Removes FirstKills (the program and autostart). Your settings and kill history
# stay in ~/.config/wow-firstkills and ~/.local/share/wow-firstkills.
set -uo pipefail
DEST=${XDG_DATA_HOME:-$HOME/.local/share}/FirstKills
FK="$DEST/watcher/wow-firstkills.py"
if [ -f "$FK" ]; then
    python3 "$FK" autostart off
    python3 "$FK" stop
fi
rm -rf "$DEST" "$HOME/.local/bin/firstkills"
echo "FirstKills removed."
echo "Also delete the FirstKills folder in WoW's _forever_/Interface/AddOns,"
echo "and ~/.config/wow-firstkills + ~/.local/share/wow-firstkills to remove settings and history."
