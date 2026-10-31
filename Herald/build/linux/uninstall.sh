#!/usr/bin/env bash
# Removes Herald (the program and autostart) and stops updating it; the Addon
# Updater removes itself too when no other addon uses it. Your settings and kill
# history stay in ~/.config/herald and ~/.local/share/herald.
set -uo pipefail
DEST=${XDG_DATA_HOME:-$HOME/.local/share}/herald/program
FK="$DEST/watcher/herald.py"
if [ -f "$FK" ]; then
    python3 "$FK" autostart off
    python3 "$FK" stop
fi
UPDATER=${XDG_DATA_HOME:-$HOME/.local/share}/addon-updater/updater.py
[ -f "$UPDATER" ] && python3 "$UPDATER" remove Herald
rm -rf "$DEST" "$HOME/.local/bin/herald"
echo "Herald removed."
echo "Also delete the Herald folder in WoW's _forever_/Interface/AddOns,"
echo "and ~/.config/herald + ~/.local/share/herald to remove settings and history."
