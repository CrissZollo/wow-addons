# FirstKills

Posts a Discord card the first time your WoW Forever character:

- **kills a kind of mob.** The card's title links to the mob's Wowhead page and shows its type and rank.
  Colours: green ⚔️ normal, gold ⭐ elite, blue/purple 💎 rare, orange 💀 boss.
  The thumbnail is a 3D render of the actual creature (from Wowhead's model viewer); bosses also get
  their dungeon-journal portrait as a big picture when Wowhead has one.
- **beats a dungeon or raid boss encounter.** 🏆 BOSS DOWN. Wipes don't count.
- **kills an enemy player.** 🩸 Each enemy player is posted only once.

There's a 🎉 milestone line at 10, 25, 50, 100, … first kills.

It also posts two cards based on your character's progress:

- **🎖️ LEVEL 10 / 20 / 30 … (and max level).** The addon takes a screenshot the moment you
  level up, and the card shows it as the big image.
- **📈 Progress report.** A large card in your class colour that compares your last report with
  now: level and XP bar, gold, time played, new first kills, every stat (▲/▼), item level,
  new gear with old → new, and your full equipment with Wowhead links.
  It's only posted if you've played at least 5 minutes since the last report, so it doesn't spam.

**When these two post:** WoW only saves addon data when you **log out or `/reload`**, so
milestone cards and progress reports go out then, not live. First kills are still posted while you play.
Type `/reload` to post a progress report mid-session.

Addons can't reach the internet, so this comes in two parts:

- **The addon** (`FirstKills.toc` + `FirstKills.lua`) keeps combat logging switched on.
- **The addon** also saves a snapshot of your character at login and logout, and screenshots milestone level-ups.
- **The watcher** (`watcher/wow-firstkills.py` + `watcher/progress.py`) runs on your PC. It reads
  `_forever_/Logs/WoWCombatLog-*.txt` and the addon's `WTF/Account/*/SavedVariables/FirstKills.lua`,
  and posts to a Discord webhook. The watcher has to be running when you log out for the report to be posted.

It counts kills by you and by your group, and each character has its own list.
Posts can lag a few seconds behind the kill, because the game writes the log in batches.

## One-time: create the Discord webhook

Only one person does this.

1. In Discord, go to the channel → **Edit Channel → Integrations → Webhooks → New Webhook**.
2. Click **Copy Webhook URL** and share it privately with your friends. Anyone with the URL can post in that channel.

## Setup on Linux (this machine)

Already done here:

- `_forever_/Interface/AddOns/FirstKills` is a symlink to this folder.
- `~/.local/bin/wow-firstkills.py` is a symlink to `watcher/wow-firstkills.py`.
- The systemd user unit is installed at `~/.config/systemd/user/wow-firstkills.service`.

Still to do:

1. Put the webhook URL in `~/.config/wow-firstkills/config.json`, as `"webhook_url": "https://discord.com/api/webhooks/..."`.
2. Run `wow-firstkills.py test` and check that a test message shows up in Discord.
3. Run `systemctl --user enable --now wow-firstkills` to run it in the background from now on.
4. In game, check that **First Kills** is listed in the AddOns list on the character screen, then type `/fk`. It should say combat logging is ON.

## Setup on Windows (friends)

Send them `dist/FirstKills-Windows.zip`, which you build with `build/build-windows.sh`.
It includes a portable Python, so they don't install anything.

1. Extract the zip somewhere permanent, e.g. `Documents\FirstKills-Windows`.
2. Double-click **Start FirstKills.bat**. The first run:
   - finds WoW Forever (registry and the usual folders on every drive) and installs the addon,
   - asks for the webhook URL and sends a test message,
   - offers to start with Windows. It then runs hidden in the background.
3. Restart WoW and type `/fk` in game.

The other files are **Stop FirstKills.bat** and **FirstKills Setup.bat** (change webhook, reinstall the addon, autostart).
Settings, history and the background log (`watcher.log`) are in `%APPDATA%\FirstKills`.

### Building the Windows package

`build/build-windows.sh` downloads the portable Python once (cached in `~/.cache/firstkills-build`),
copies in the addon and watcher, and writes `dist/FirstKills-Windows.zip`. Re-run it after every change.

## Commands

| Where | Command | What it does |
|---|---|---|
| In game | `/fk` | Turns combat logging on if it's off, and shows its status and how long this session has run |
| In game | `/reload` | Saves the addon data now, which posts a progress report if 5+ minutes have passed |
| Terminal | `wow-firstkills.py` | Watches the log and posts first kills |
| Terminal | `wow-firstkills.py setup` / `start` / `stop` | Setup wizard / start (with setup if needed) / stop a background copy |
| Terminal | `wow-firstkills.py test` | Posts one sample card of each kind |
| Terminal | `wow-firstkills.py list` | Shows recorded first kills per character |
| Terminal | `wow-firstkills.py --dry-run` | Watches the log but prints instead of posting |
| Linux | `journalctl --user -u wow-firstkills -f` | Shows the background service's output |

## Config (`~/.config/wow-firstkills/config.json`)

- `webhook_url`: the Discord webhook to post to.
- `logs_dir`: the game's `_forever_/Logs` folder.
- `ignore`: mob names that never get posted, e.g. `["Rabbit", "Squirrel"]`.
- `poll_seconds`: how often to check the log for new lines.
- `wowhead_env`, `npc_url`, `search_url`: where mob info and links come from. The default is Wowhead's Forever pages.
- `item_url`: Wowhead link for gear in the progress report.
- `min_report_minutes`: minimum play time between progress reports (default 5).
- `wtf_dir`, `screenshots_dir`: found automatically next to `logs_dir`. Set them only if your folders are elsewhere.
- `player_url`: link for enemy players, using `{name}` and `{realm}`. Empty means no link, since I couldn't find an armory for Forever.

New settings use their defaults until you add them to your config file.

The kill history is saved in `~/.local/share/wow-firstkills/kills.json`, and what's been reported in `reports.json` next to it. Delete them to start over.

## Troubleshooting

- **Nothing posts.** Type `/fk` in game and check that it says ON. Then make sure a new
  `WoWCombatLog-*.txt` file is growing in `_forever_/Logs`.
- **The addon is "out of date".** Tick **Load out of date AddOns**, or change `## Interface:` in
  `FirstKills.toc` to the number from `/dump select(4, GetBuildInfo())`.
- **The addon isn't in the list (Linux).** Wine may not follow the symlink. Replace it with a real copy of the folder.
- **The Logs folder takes up a lot of space.** Delete old `WoWCombatLog-*.txt` files now and then.
