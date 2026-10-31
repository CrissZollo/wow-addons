# Adding an addon: the standard format

Every addon in this repository has the same pieces and the same wiki layout, so friends always know
where to look. `./check-wiki.py` checks all of this, and `release.sh` and `publish-wiki.sh` refuse to
run until it passes.

## Checklist

1. **Addon folder** `<Addon>/`, named exactly like its `.toc` file (`<Addon>/<Addon>.toc`) with `## Version: x.y.z`.
2. **`<Addon>/README.md`** for the GitHub repository page (same sections as the wiki page is fine).
3. **`<Addon>/build/package.sh`**, which writes the downloads to `<Addon>/dist/`:
   - plain addon: copy `templates/package-plain.sh`, which makes `<Addon>.zip`,
   - addon with a helper program: `<Addon>-Windows.zip` + `<Addon>-Linux.zip` (see `Herald/build/package.sh`).
4. **Wiki page `wiki/<Addon>.md`:** copy `templates/wiki-addon-page.md` and fill it in.
   Keep **all** the `##` sections in the same order, even when one only says "None.":
   `What it does` → `Download` → `What you need` → `Install` → `Check that it works` → `Using it` →
   `Settings` → `Updating` → `Uninstalling` → `Known limitations`.
5. **Snippets in the shared wiki pages** (`templates/wiki-snippets.md` has them ready to paste):
   - `wiki/Home.md`: a row in *The addons* table,
   - `wiki/_Sidebar.md`: `- [[<Addon>]]` under **Addons**,
   - `wiki/Install-on-Windows.md` and `wiki/Install-on-Linux.md`: a `## <Addon>` section,
   - `wiki/Platform-Differences.md`: a `## <Addon>` section (or "No differences"),
   - `wiki/Troubleshooting.md`: a `## <Addon>` section (or "No known problems yet."),
   - the root `README.md`: a row in the addons table.
6. **Check, commit and release:**
   ```sh
   ./check-wiki.py
   git add -A && git commit -m "Add <Addon>"
   ./release.sh <Addon> 1.0.0     # builds, tags, releases, updates download links, publishes the wiki
   ```

## Writing style

- Write for players, not developers: say what to click and what they'll see.
- Always cover **both Windows and Linux** (WoW through Wine/Proton). If something differs or is
  untested on one of them, say so on the addon page and in *Platform Differences*.
- Download links always use the versioned form
  `https://github.com/CrissZollo/wow-addons/releases/download/<Addon>-v<version>/<file>`.
  `release.sh` updates them for new versions.
- Link other wiki pages with `[[Page Name]]`, and sections with `[Text](Page-Name#section)`.
