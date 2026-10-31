# Shared build helpers for the addon downloads; source it from <Addon>/build/package.sh.
# Every download carries the Addon Updater (in updater/), which keeps the addon up to date.
UPDATER_SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PY_VERSION=3.14.10
PY_CACHE=${XDG_CACHE_HOME:-$HOME/.cache}/wow-addons-build
PY_EMBED=$PY_CACHE/python-$PY_VERSION-embed-amd64.zip

add_updater() {  # $1 = package folder: the updater program and its in-game addon
    mkdir -p "$1/updater"
    cp "$UPDATER_SRC/updater.py" "$1/updater/"
    cp -r "$UPDATER_SRC/AddonUpdater" "$1/updater/"
}

add_python() {  # $1 = package folder: a portable Windows Python in $1/python
    if [ ! -f "$PY_EMBED" ]; then
        mkdir -p "$PY_CACHE"
        echo "downloading portable Python $PY_VERSION"
        curl -fsSL --proto '=https' -o "$PY_EMBED.part" \
            "https://www.python.org/ftp/python/$PY_VERSION/python-$PY_VERSION-embed-amd64.zip"
        mv "$PY_EMBED.part" "$PY_EMBED"
    fi
    mkdir -p "$1/python"
    (cd "$1/python" && unzip -q "$PY_EMBED")
}

zip_dirs() {  # $1 = dist folder, then the package folder names to zip
    local dist=$1; shift
    for d in "$@"; do
        rm -f "$dist/$d.zip"
        (cd "$dist" && zip -qr "$d.zip" "$d")
        echo "built $dist/$d.zip ($(du -h "$dist/$d.zip" | cut -f1))"
    done
}
