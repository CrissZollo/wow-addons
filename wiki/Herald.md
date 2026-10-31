# Herald

Herald posts your WoW Forever adventures to the group's Discord channel: first kills, boss kills, level milestones and progress reports.

## What it does

| Card | What it shows | When it posts |
|---|---|---|
| ⚔️ ⭐ 💎 💀 **First kill** | The first time your character kills a kind of mob: a picture of the creature, a Wowhead link, and its type and rank (green normal, gold elite, blue/purple rare, orange boss) | A few seconds after the kill |
| 🏆 **BOSS DOWN** | A dungeon or raid boss encounter you won | A few seconds after the kill |
| 🩸 **Enemy player** | The first time you kill each enemy player | A few seconds after the kill |
| 🎖️ **LEVEL 10 / 20 / 30 …** | The level reached, with a screenshot of the moment you levelled up | When you log out or `/reload` |
| 📈 **Progress report** | Level and XP, gold, every stat and your gear compared with your last report, plus everything you have equipped | When you log out or `/reload`, if you played at least 5 minutes since the last report |

Level cards and progress reports wait until you log out or `/reload` because that's the only time
WoW lets addons save their data.

Herald has two parts, and both are set up by the installer:

1. **The addon** inside WoW keeps combat logging on, saves your character's stats and gear, and screenshots milestone level-ups.
2. **A small helper program** on your PC reads what the game writes to disk and posts it to Discord. Addons
   can't reach the internet on their own. **The helper must be running while you play**, which the
   installer sets up to happen automatically.

## Download

| Windows | Linux (Wine / Proton) |
|---|---|
| [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Windows.zip) | [Herald-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Linux.zip) |

Older versions are on the [releases page](https://github.com/CrissZollo/wow-addons/releases).

## What you need

| | Windows | Linux |
|---|---|---|
| WoW Forever | Installed through Battle.net | Installed through Battle.net inside Heroic, Lutris, Steam (Proton), Bottles or Wine |
| Python | Nothing to install, it's included | `python3` 3.8 or newer, already installed on almost every distro (see [[Install on Linux]]) |
| Discord webhook link | Ask whoever runs the channel ([[Discord Webhook]]) | Same |

## Install

- **Windows:** extract the zip somewhere permanent, double-click **Start Herald.bat**, paste the webhook link,
  answer **Y** to autostart, and restart WoW. Step by step: [Install on Windows → Herald](Install-on-Windows#herald)
- **Linux:** extract the zip, run `bash install.sh` in a terminal, paste the webhook link, answer **Y** to
  autostart, and restart WoW. Step by step: [Install on Linux → Herald](Install-on-Linux#herald)

## Check that it works

1. On the character screen, **Herald** is ticked under *AddOns*.
2. In game, `/herald` says *combat logging is ON*.
3. Kill something you've never killed on that character. A card appears in Discord a few seconds later.

## Using it

| In game | |
|---|---|
| `/herald` | Shows whether combat logging is on and how long the session has run |
| `/reload` | Posts a progress report right away, if you've played 5+ minutes since the last one |

| On your PC | Windows | Linux |
|---|---|---|
| Start | `Start Herald.bat` | `herald start` |
| Stop | `Stop Herald.bat` | `herald stop` |
| Change webhook, reinstall the addon, autostart on/off | `Herald Setup.bat` | `herald setup` |
| Post sample cards to Discord | — | `herald test` |
| List your recorded first kills | — | `herald list` |

Several friends can use **the same webhook**. Everyone's cards go into one channel, and each card says whose kill it was.

## Settings

Setup writes `config.json` for you: in `%APPDATA%\Herald` on Windows, or `~/.config/herald` on Linux.
You only need to edit it for these extras. Restart Herald afterwards.

| Setting | What it does |
|---|---|
| `ignore` | Mob names that are never posted, e.g. `["Rabbit", "Squirrel"]` |
| `min_report_minutes` | Play time needed between progress reports (default 5) |
| `logs_dir` | The game's `_forever_/Logs` folder, if it isn't found automatically |
| `npc_url`, `item_url` | Where the creature and item links go (default: Wowhead's Forever pages) |
| `player_url` | A link for enemy players, using `{name}` and `{realm}` (default: no link) |

## Updating

- **Windows:** run *Stop Herald.bat*, replace the folder with the new download, then run *Start Herald.bat*.
- **Linux:** extract the new zip and run `bash install.sh` again.

Your settings and history are kept, and the new addon version is copied into the game automatically.

## Uninstalling

- **Windows:** run `Herald Setup.bat` and answer **N** to autostart, run `Stop Herald.bat`, delete the folder,
  and delete `Herald` in `_forever_\Interface\AddOns`. Settings are in `%APPDATA%\Herald`.
- **Linux:** run `bash uninstall.sh` from the download, and delete `Herald` in `_forever_/Interface/AddOns`.

## Known limitations

- **Not tested in the live game yet** (WoW Forever launches November 4, 2026). Everything was tested with simulated game data.
- Only kills by you or your group count. The game's combat log only covers what happens near you.
- Enemy player cards have no picture, because the game's log doesn't say their class or race.
- Creature pictures come from Wowhead and are probably the Classic models.
- More: [[Platform Differences]] and [[Troubleshooting]].
