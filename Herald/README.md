# Herald

Posts your WoW Forever adventures to a Discord channel as cards:

| Card | When |
|---|---|
| ⚔️ ⭐ 💎 💀 **First kill** of a kind of mob | Shows a picture of the creature, a Wowhead link, and its type and rank. Colours: green normal, gold elite, blue/purple rare, orange boss |
| 🏆 **BOSS DOWN** | You won a dungeon or raid boss encounter |
| 🩸 **Enemy player** | The first time you kill each enemy player |
| 🎖️ **LEVEL 10 / 20 / 30 …** | Includes a screenshot taken the moment you levelled up |
| 📈 **Progress report** | Level and XP, gold, stats and gear compared with your last report, plus your full equipment. Posted at most once per 5 minutes of play |

First kills post **while you play**, a few seconds after the kill.
Level cards and progress reports post **when you log out or type `/reload`**. That's the
only time WoW lets addons save their data.

## Download

| Windows | Linux (Wine / Proton) |
|---|---|
| [**Herald-Windows.zip**](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Windows.zip) | [**Herald-Linux.zip**](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Linux.zip) |

Older versions are on the [releases page](https://github.com/CrissZollo/wow-addons/releases).

**You also need the Discord webhook URL.** Ask whoever runs the Discord channel. It's a
private link, so don't post it anywhere public.

## Windows guide

1. Download **Herald-Windows.zip** and extract it (right-click → *Extract All*) somewhere
   permanent, for example `Documents\Herald-Windows`. Don't run it from inside the zip.
2. Double-click **Start Herald.bat**.
   - If Windows says *"Windows protected your PC"*: click **More info → Run anyway**.
     This happens with any downloaded script that isn't signed.
3. The setup:
   - finds WoW Forever and installs the addon (if your game is somewhere unusual, it asks you to paste the folder path),
   - asks for the **webhook URL** (paste with right-click or Ctrl+V) and sends a test message to Discord,
   - asks *"Start Herald automatically when Windows starts?"*. Answer **Y**, and from
     then on it runs hidden in the background with no window.
4. Restart WoW. On the character screen, check that **Herald** is ticked under *AddOns*.
   In game, type **`/herald`**. It should say *combat logging is ON*.

The other files in the folder: **Stop Herald.bat** stops it, and **Herald Setup.bat** lets
you change the webhook, reinstall the addon, or turn autostart on or off.

**Updating:** automatic. The setup turns on the Addon Updater, which installs new versions
(into the game and into this folder) within 30 minutes of a release. Keep the folder where it is.
See [Automatic Updates](https://github.com/CrissZollo/wow-addons/wiki/Automatic-Updates).

## Linux guide

For WoW Forever running through Wine or Proton (Heroic, Lutris, Steam, Bottles, plain Wine).

1. Download **Herald-Linux.zip** and extract it.
2. Open a terminal in the extracted folder and run:
   ```sh
   bash install.sh
   ```
   - It needs `python3`, which is already installed on almost every distro. If it's missing,
     the installer tells you the command to install it.
3. The setup:
   - copies Herald to `~/.local/share/herald/program` and adds a `herald` command,
   - finds WoW Forever inside your Wine prefix and installs the addon (if it can't, paste the
     path to the `World of Warcraft` folder inside the prefix's `drive_c`),
   - asks for the **webhook URL** and sends a test message,
   - asks whether to start automatically when you log in. **Y** sets up a systemd user service.
4. Restart WoW. Check that **Herald** is ticked under *AddOns*, then type **`/herald`** in game.

**Commands:** `herald setup`, `herald start`, `herald stop`, `herald test`
(posts sample cards), `herald list` (your recorded first kills).
If `herald` isn't found, use `~/.local/bin/herald`.

**Updating:** automatic, through the Addon Updater that the installer sets up.
**Uninstalling:** `bash uninstall.sh` (it also stops the updates).

## Windows vs Linux

All features are the same on both. Only the setup differs:

| | Windows | Linux (Wine / Proton) |
|---|---|---|
| Python | Included in the zip | Uses your system's `python3` (3.8+) |
| Install / start | `Start Herald.bat` | `bash install.sh`, then the `herald` command |
| Finds the game in | Battle.net's install location, and the usual folders on every drive | Heroic, Lutris, Steam (Proton), Bottles and `~/.wine` prefixes, including Flatpak versions |
| Runs in the background | Hidden, starts with Windows (Startup folder) | systemd user service, starts when you log in |
| Settings and history | `%APPDATA%\Herald` | `~/.config/herald` and `~/.local/share/herald` |
| Background log | `%APPDATA%\Herald\watcher.log` | `journalctl --user -u herald` |
| Tested | Under Wine only, not on a real Windows PC yet | Yes (Arch + Heroic), with test data |

**Not supported:** macOS (the addon itself works, but the watcher is untested there), and
Linux without systemd (it works, but you have to run `herald start` yourself each time).
On a **Steam Deck**, install it from Desktop Mode. Whether the background service also runs
while you're in Game Mode hasn't been tested.

## Using it

- In game, **`/herald`** shows whether combat logging is on and how long the session has run.
- **`/reload`** posts a progress report right away, if you've played 5+ minutes since the last one.
- **`/updates`** shows Herald's version. New versions install themselves, and the game tells you at the next login.
- Several friends can use **the same webhook**. Everyone's cards go into one channel, and each card says whose kill it was.

## Settings

The settings file is `config.json` (see the table above for where it lives). Setup writes it for you.
You only need to edit it for these extras:

- `ignore`: mob names that are never posted, e.g. `["Rabbit", "Squirrel"]`.
- `min_report_minutes`: play time needed between progress reports (default 5).
- `logs_dir`: the game's `_forever_/Logs` folder, if it can't be found automatically.
- `wowhead_env`, `npc_url`, `item_url`, `search_url`: where mob info and links come from (default: Wowhead's Forever pages).
- `player_url`: a link for enemy players, using `{name}` and `{realm}`. Empty means no link.

Restart Herald after editing (stop, then start).

## Troubleshooting

- **Nothing posts.** In game, type `/herald` and check it says ON. Make sure Herald is running
  (start it again: it tells you if it's already running). Check the background log (see the table).
- **"Herald" is shown as *out of date* in the AddOns list.** Tick *Load out of date AddOns*.
- **No level-up screenshot on the milestone card.** The game may block addons from taking
  screenshots. The card still posts without it.
- **The Wowhead links don't open the right page.** Set `npc_url` to `https://www.wowhead.com/classic/npc={id}`.
- **Posts lag.** The game writes its combat log in batches, so a few seconds of delay (sometimes
  more when little is happening) is normal.

## Known limitations

- **Not tested in the live game yet** (WoW Forever launches November 4, 2026). Everything was tested
  with simulated game data. Expect small fixes after launch.
- Level cards and progress reports can only post at logout or `/reload`.
- Only kills by you or your group count. The game's combat log only covers what happens near you.
- Enemy player cards have no picture or link, because the combat log doesn't record their class or race.
- Creature pictures come from Wowhead, so they're probably Classic models. If Forever changed how a creature looks, the picture won't match.

---

## For developers

```
Herald/
├── Herald.toc, Herald.lua   the addon
├── watcher/
│   ├── herald.py            watches the combat log, setup wizard, posting
│   ├── progress.py                  milestone cards + progress reports from SavedVariables
│   └── herald.service       example systemd unit
└── build/
    ├── package.sh                   builds dist/Herald-Windows.zip and -Linux.zip
    ├── program-files                watcher files the Addon Updater keeps current
    └── linux/install.sh, uninstall.sh
```

How it works: the addon keeps combat logging on and saves character snapshots plus milestones in
`HeraldDB`. The watcher follows `_forever_/Logs/WoWCombatLog-*.txt` (PARTY_KILL, ENCOUNTER_END),
reads `WTF/Account/*/SavedVariables/Herald.lua` whenever it changes, and posts Discord embeds to
the webhook. Wowhead provides the mob info, creature renders and icons.

Automatic updates: `herald.py setup`/`start` run `updater/updater.py install --addon Herald
--program-dir <download folder>` from the download (not from a repository checkout). The updater then
replaces the addon, the files in `build/program-files` and itself on new releases, and the watcher
restarts itself when its own files change (see `restart()` in `herald.py`).

Development setup: symlink the addon folder into `_forever_/Interface/AddOns/Herald`, and run
`watcher/herald.py --dry-run` to print the cards instead of posting them, or
`herald.py test --dry-run` for sample cards.

To release a new version, run `./release.sh Herald <version>` from the repository root
(see the main README).
