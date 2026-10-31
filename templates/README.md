# Adding an addon: the standard format

Every addon in this repository has the same pieces and the same wiki layout, so friends always know
where to look. `./check-wiki.py` checks all of this, and `release.sh` and `publish-wiki.sh` refuse to
run until it passes.

## Checklist

1. **Addon folder** `<Addon>/`, named exactly like its `.toc` file (`<Addon>/<Addon>.toc`) with `## Version: x.y.z`.
2. **`<Addon>/README.md`** for the GitHub repository page (same sections as the wiki page is fine).
3. **`<Addon>/build/package.sh`**, which writes `<Addon>-Windows.zip` + `<Addon>-Linux.zip` to `<Addon>/dist/`.
   Every download carries the Addon Updater (`updater/`, added by `add_updater` from `updater/bundle.sh`):
   - plain addon: copy `templates/package-plain.sh`. Its installers copy the addon into the game and turn on updates,
   - addon with a helper program: see `Herald/build/package.sh`. Its setup must run
     `updater/updater.py install --addon <Addon> --program-dir <download folder>`, and list the program's
     files in **`<Addon>/build/program-files`** so the updater keeps them current. The program should
     restart itself when its files change (see `restart()` in `Herald/watcher/herald.py`).
4. **Two wiki pages, one per language:**
   - `wiki/<Addon>.md` (English): copy `templates/en/wiki-addon-page.md`,
   - `wiki/<Addon>-på-svenska.md` (Swedish, titled `# <Addon> på svenska`): copy `templates/sv/wiki-addon-page.md`.

   Keep **all** the `##` sections in the same order, even when one only says "None." / "Inga.":
   English `What it does` → `Download` → `What you need` → `Install` → `Check that it works` → `Using it` →
   `Settings` → `Updating` → `Uninstalling` → `Known limitations`. Swedish `Vad den gör` → `Ladda ner` →
   `Det här behöver du` → `Installera` → `Kolla att det fungerar` → `Så använder du den` → `Inställningar` →
   `Uppdatera` → `Avinstallera` → `Kända begränsningar`.
   Each page links to the other language right under its title (the templates already do).
5. **Entries in the shared wiki pages, in both languages** (ready to paste: `templates/en/wiki-snippets.md`
   and `templates/sv/wiki-snippets.md`):

   | English page | Swedish page | Entry |
   |---|---|---|
   | `Home.md` | `Startsida.md` | a row in the addons table |
   | `_Sidebar.md` | `_Sidebar.md` | `- [[<Addon>]]` under English, `- [[<Addon> på svenska]]` under Svenska |
   | `Install-on-Windows.md` | `Installera-på-Windows.md` | a `## <Addon>` section |
   | `Install-on-Linux.md` | `Installera-på-Linux.md` | a `## <Addon>` section |
   | `Platform-Differences.md` | `Skillnader-mellan-Windows-och-Linux.md` | a `## <Addon>` section (or "No differences" / "Inga skillnader") |
   | `Troubleshooting.md` | `Felsökning.md` | a `## <Addon>` section (or "No known problems yet." / "Inga kända problem än.") |

   Plus a row in the addons table of the repository's root `README.md`.
6. **Check, commit and release:**
   ```sh
   ./check-wiki.py
   git add -A && git commit -m "Add <Addon>"
   ./release.sh <Addon> 1.0.0     # builds, tags, releases, updates download links, publishes the wiki
   ```

## Automatic updates

`release.sh` runs `updater/make-manifest.py`, which records the release in `updates.json`. For each addon it lists
the in-game files (`*.toc`, `*.lua`, `*.xml` at the top of the addon folder, plus `media/`), the files in
`build/program-files`, and the updater's own files, each with a SHA-256. Players' updaters read `updates.json`
from `main` every 30 minutes and download changed files from the release tag. While WoW runs they only install
updates that keep the same file list and `.toc` (apart from `## Version`); anything else waits until WoW closes.
So adding a file to an addon is fine, it just reaches players after their next restart of the game.

## Languages

The wiki is in **English and Swedish**. Every page exists in both languages with the same structure, and
starts with a link to its counterpart: `🇸🇪 [[Läs på svenska|<Swedish page>]]` on English pages,
`🇬🇧 [[Read in English|<English page>]]` on Swedish pages. When you change one language, change the other
one too. When you add a new shared page, add it in both languages, put both in `_Sidebar.md`, and add the
pair to `PAIRS` in `check-wiki.py`.

The programs themselves (setup texts, Discord cards) are in English. Swedish guides quote those
English texts and explain them in Swedish.

## Writing style

- Write for players, not developers: say what to click and what they'll see.
- Always cover **both Windows and Linux** (WoW through Wine/Proton). If something differs or is
  untested on one of them, say so on the addon page and in *Platform Differences*.
- Download links always use the versioned form
  `https://github.com/CrissZollo/wow-addons/releases/download/<Addon>-v<version>/<file>`.
  `release.sh` updates them for new versions.
- Link other wiki pages with `[[Page Name]]`, and sections with `[Text](Page-Name#section)`.
