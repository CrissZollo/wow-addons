#!/usr/bin/env bash
# Publish a new version of an addon as a GitHub release.
#
#   ./release.sh Herald 1.0.1
#
# Sets "## Version:" in the addon's .toc, builds its downloads (<Addon>/build/package.sh),
# points the download links in the READMEs at the new release, commits, tags
# "<Addon>-v<version>", pushes and creates the release with the zips attached.
set -euo pipefail
REPO=CrissZollo/wow-addons
GH_USER=CrissZollo

ADDON=${1:?usage: ./release.sh <Addon> <version>}
VERSION=${2:?usage: ./release.sh <Addon> <version>}
TAG="$ADDON-v$VERSION"
ROOT=$(cd "$(dirname "$0")" && pwd)
cd "$ROOT"

[ -f "$ADDON/$ADDON.toc" ] || { echo "no $ADDON/$ADDON.toc"; exit 1; }
[ -x "$ADDON/build/package.sh" ] || { echo "no $ADDON/build/package.sh"; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "commit or stash your changes first"; exit 1; }
git rev-parse -q --verify "refs/tags/$TAG" >/dev/null && { echo "$TAG already exists"; exit 1; }

sed -i "s/^## Version: .*/## Version: $VERSION/" "$ADDON/$ADDON.toc"
sed -i -E "s#releases/download/$ADDON-v[0-9][0-9.]*/#releases/download/$TAG/#g" \
    README.md "$ADDON/README.md"
"$ADDON/build/package.sh"

if [ -n "$(git status --porcelain)" ]; then
    git commit -qam "$ADDON $VERSION"
fi
git tag "$TAG"
git push -q origin HEAD "$TAG"

GH_TOKEN=$(gh auth token --user "$GH_USER") gh release create "$TAG" --repo "$REPO" \
    --title "$ADDON $VERSION" "$ADDON"/dist/*.zip --notes "$(cat <<NOTES
**Download** the file for your system below (under *Assets*):

- **Windows:** \`$ADDON-Windows.zip\`. Nothing to install, Python is included.
- **Linux** (Wine / Proton / Heroic / Lutris / Steam): \`$ADDON-Linux.zip\`

Install guide: https://github.com/$REPO/tree/main/$ADDON#readme
NOTES
)"
echo "released https://github.com/$REPO/releases/tag/$TAG"
