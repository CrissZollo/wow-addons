# WoW addons

Addons for **World of Warcraft: Forever**. Pick one, download the file for your system,
and follow its guide.

| Addon | What it does | Windows | Linux (Wine / Proton) | Guide |
|---|---|---|---|---|
| **Herald** | Posts your first kills, boss kills, enemy players, level milestones and progress reports (gear, stats, gold) to a Discord channel | [Download](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Windows.zip) | [Download](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Linux.zip) | [Read me](Herald/README.md) |

All versions are on the [releases page](https://github.com/CrissZollo/wow-addons/releases).

📖 **Step-by-step guides are in the [wiki](https://github.com/CrissZollo/wow-addons/wiki)**: installing on Windows and Linux, what each addon needs, the Discord webhook, and troubleshooting.

## Windows or Linux?

- **Windows:** download the *Windows* file. Everything it needs is included.
- **Linux:** WoW runs through Wine or Proton (Heroic, Lutris, Steam, Bottles). The addon part
  works exactly as on Windows. Addons with a helper program (like Herald) have a *Linux*
  download that uses your system's Python instead.

Each addon's guide lists any differences between the platforms.

## Addons without a helper program

Plain addons are installed the normal way. Extract the download and put the addon's folder in
`World of Warcraft\_forever_\Interface\AddOns\` (on Linux, the same path inside your Wine
prefix's `drive_c`). Then restart the game.

---

## For developers

- **Layout:** one folder per addon, named exactly like its `.toc` file. Each has its own `README.md`.
  Addons with downloads have a `build/package.sh` that writes zips to `<Addon>/dist/`, which isn't committed.
- **Releasing:** commit your changes, then run `./release.sh <Addon> <version>`, e.g.
  `./release.sh Herald 1.0.1`. It bumps the version, builds the zips, updates the download
  links above, tags `<Addon>-v<version>`, pushes, and creates the GitHub release.
- **Wiki:** the pages live in `wiki/` and are versioned with the code. Edit them there, then run
  `./publish-wiki.sh`. `release.sh` also does this.
- **Adding an addon:** every addon follows the same format: folder layout, build script, wiki page
  with fixed sections, and entries on the shared wiki pages. The checklist and templates are in
  [`templates/`](templates/README.md). `./check-wiki.py` verifies it, and `release.sh` / `publish-wiki.sh`
  won't run until it passes.
