# WoW addons

Addons for **World of Warcraft: Forever**. Pick one, download the file for your system,
and follow its guide.

| Addon | What it does | Windows | Linux (Wine / Proton) | Guide |
|---|---|---|---|---|
| **Herald** | Posts your first kills, boss kills, enemy players, level milestones and progress reports (gear, stats, gold) to a Discord channel | [Download](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Windows.zip) | [Download](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Linux.zip) | [Read me](Herald/README.md) |

All versions are on the [releases page](https://github.com/CrissZollo/wow-addons/releases).

**You only install once.** Every download includes the *Addon Updater*, which installs new versions in the
background and tells you in game when one arrived. See [Automatic Updates](https://github.com/CrissZollo/wow-addons/wiki/Automatic-Updates).

📖 **Step-by-step guides are in the [wiki](https://github.com/CrissZollo/wow-addons/wiki)**: installing on Windows and Linux, what each addon needs, the Discord webhook, and troubleshooting.
🇸🇪 **[Wikin på svenska](https://github.com/CrissZollo/wow-addons/wiki/Startsida)**: samma guider på svenska.

## Windows or Linux?

- **Windows:** download the *Windows* file. Everything it needs is included.
- **Linux:** WoW runs through Wine or Proton (Heroic, Lutris, Steam, Bottles). The addon part
  works exactly as on Windows. The *Linux* download uses your system's Python (3.8+) for the
  installer, the updater and any helper program.

Each addon's guide lists any differences between the platforms.

## Addons without a helper program

Plain addons come with a small installer, so they can keep themselves up to date too. Extract the
download, then double-click **Install &lt;Addon&gt;.bat** (Windows) or run `bash install.sh` (Linux), and
restart the game.

---

## For developers

- **Layout:** one folder per addon, named exactly like its `.toc` file. Each has its own `README.md`.
  Addons with downloads have a `build/package.sh` that writes zips to `<Addon>/dist/`, which isn't committed.
- **Releasing:** commit your changes, then run `./release.sh <Addon> <version> ["what's new"]`, e.g.
  `./release.sh Herald 1.0.1 "Fixes the gold total"`. It bumps the version, builds the zips, updates the download
  links above, writes `updates.json`, tags `<Addon>-v<version>`, pushes, and creates the GitHub release.
  Players' updaters install it within 30 minutes and show the "what's new" line in game.
- **Automatic updates:** `updater/` holds the Addon Updater that every download carries (`updater.py`,
  the in-game `AddonUpdater` addon, `bundle.sh` for build scripts, `make-manifest.py` for `updates.json`).
  It reads `updates.json` from `main` and downloads files from the release tag, so **don't edit
  `updates.json` by hand**, and remember that everything you push to a release tag reaches players' PCs.
- **Wiki:** the pages live in `wiki/` and are versioned with the code. Edit them there, then run
  `./publish-wiki.sh`. `release.sh` also does this.
- **Adding an addon:** every addon follows the same format: folder layout, build script, wiki page
  with fixed sections, and entries on the shared wiki pages. The checklist and templates are in
  [`templates/`](templates/README.md). `./check-wiki.py` verifies it, and `release.sh` / `publish-wiki.sh`
  won't run until it passes.
