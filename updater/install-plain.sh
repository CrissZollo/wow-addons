#!/usr/bin/env bash
# Linux installer for a plain addon (shipped as install.sh in <Addon>-Linux.zip).
# Finds WoW Forever, copies the addon into Interface/AddOns and turns on automatic updates:
# the Addon Updater goes to ~/.local/share/addon-updater and starts when you log in.
set -euo pipefail
HERE=$(cd "$(dirname "$0")" && pwd)

if ! command -v python3 >/dev/null 2>&1; then
    echo "The installer needs Python 3. Install it, then run this again:"
    echo "  Ubuntu / Mint / Pop!_OS:  sudo apt install python3"
    echo "  Fedora:                   sudo dnf install python3"
    echo "  Arch / Manjaro:           sudo pacman -S python"
    exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 8))'; then
    echo "The installer needs Python 3.8 or newer (you have $(python3 --version))."
    exit 1
fi

ADDON=
for toc in "$HERE"/*/*.toc; do
    dir=$(dirname "$toc")
    [ "$toc" = "$dir/$(basename "$dir").toc" ] && ADDON=$(basename "$dir")
done
[ -n "$ADDON" ] || { echo "no addon folder next to install.sh"; exit 1; }

python3 "$HERE/updater/updater.py" install --addon "$ADDON" --addon-dir "$HERE/$ADDON"
echo "Done. Restart WoW to load $ADDON."
