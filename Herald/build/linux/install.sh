#!/usr/bin/env bash
# Herald installer for Linux (WoW Forever running through Wine / Proton).
# Copies Herald to ~/.local/share/herald/program, adds the `herald` command,
# then runs setup: finds the game, installs the addon, asks for the Discord
# webhook and sets up autostart. Run it again to update.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)
DEST=${XDG_DATA_HOME:-$HOME/.local/share}/herald/program
BIN=$HOME/.local/bin

if ! command -v python3 >/dev/null 2>&1; then
    echo "Herald needs Python 3. Install it, then run this again:"
    echo "  Ubuntu / Mint / Pop!_OS:  sudo apt install python3"
    echo "  Fedora:                   sudo dnf install python3"
    echo "  Arch / Manjaro:           sudo pacman -S python"
    exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))'; then
    echo "Herald needs Python 3.8 or newer (you have $(python3 --version))."
    exit 1
fi

# Stop a running copy so the new version is used.
[ -x "$BIN/herald" ] && "$BIN/herald" stop >/dev/null 2>&1 || true

mkdir -p "$DEST" "$BIN"
rm -rf "$DEST/Herald" "$DEST/watcher"
cp -r "$HERE/Herald" "$HERE/watcher" "$DEST/"
chmod +x "$DEST/watcher/herald.py"
ln -sf "$DEST/watcher/herald.py" "$BIN/herald"
echo "Installed to $DEST"
case ":$PATH:" in
    *":$BIN:"*) ;;
    *) echo "Note: $BIN isn't in your PATH, so use $BIN/herald instead of herald." ;;
esac

python3 "$DEST/watcher/herald.py" start
