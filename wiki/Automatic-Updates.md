# Automatic Updates

🇸🇪 [[Läs på svenska|Automatiska uppdateringar]]

Every addon here keeps itself up to date. You download and install an addon once. After that, a small
program on your PC, the **Addon Updater**, installs new versions for you.

## How it works

- **The addon's installer sets it up.** *Start Herald.bat*, `bash install.sh` or *Install &lt;Addon&gt;.bat* turn on
  automatic updates as part of the install. There's nothing extra to download or click.
- **It runs in the background** and starts when you log in to your PC. It checks for new versions
  **every 30 minutes**.
- **It updates everything that belongs to the addon:** the addon in the game, its helper program (like
  Herald's), and the updater itself. Your settings and history are never touched.
- **One updater serves all the addons** from this wiki, however many you install.
- It also puts a small addon called **Addon Updater** in the game. It's the part that tells you about updates.
  Keep it ticked in the AddOns list.

## What you see in game

| When | Message in the chat window |
|---|---|
| You log in after an update | *Addon Updater: Herald updated: 1.0.0 -> 1.1.0 - (what's new)* |
| An update arrives while you play, and a `/reload` is enough | *An addon update was installed. Type /reload to start using it.* |
| An update arrives while you play, and WoW has to restart | *An addon update is ready. It installs when you close WoW; it's there next time you play.* |

Type `/updates` in game to see the version of each addon that's kept up to date.

## While you're playing

While the game runs, WoW addons can't hear anything from programs on your PC. They only read their files
when you log in or `/reload`. So:

- **Updates that only change existing files** install right away. Type `/reload` when you're told to, or
  just keep playing: you get the new version the next time you log in.
- **Updates that add or remove files** wait until you close WoW, and install a few seconds after. WoW only
  notices new files when it starts.

The two messages during play are **experimental**: they use a trick (the updater swaps a tiny font file that
the in-game addon tries to load) that hasn't been tried in WoW Forever yet. If they never show up, nothing
breaks. Updates still install, and you see the *updated* message at your next login.

**Testing the in-game message** (with WoW running and a character logged in):

- **Windows:** press **Win+R**, paste this and press Enter:
  `cmd /k ""%LOCALAPPDATA%\AddonUpdater\python\python.exe" "%LOCALAPPDATA%\AddonUpdater\updater.py" notice-test"`
- **Linux:** `python3 ~/.local/share/addon-updater/updater.py notice-test`

Within about 30 seconds the game should say *Type /reload to start using it*. The test switches itself off
after 10 minutes.

## Checking on it

| | Windows | Linux |
|---|---|---|
| Where it lives | `%LOCALAPPDATA%\AddonUpdater` (paste into File Explorer's address bar) | `~/.local/share/addon-updater` |
| Log (what it did and when) | `updater.log` in that folder | `updater.log` in that folder |
| Status and check now | **Win+R**: `cmd /k ""%LOCALAPPDATA%\AddonUpdater\python\python.exe" "%LOCALAPPDATA%\AddonUpdater\updater.py" status"` (or `check`) | `python3 ~/.local/share/addon-updater/updater.py status` (or `check`) |
| Starts with | The *Addon Updater* shortcut in the Startup folder | The `addon-updater` systemd user service |

It only talks to GitHub: it downloads the list of the latest versions and the files that changed, and checks
each file against a checksum before installing it. It doesn't send anything about you or your PC.

## Turning it off

- **Uninstalling an addon:** delete its folder in `_forever_/Interface/AddOns` (each addon's page says what
  else to remove). The updater notices and stops updating it.
- When none of these addons are left, the updater switches itself off and removes its in-game addon.
  On Windows you can then delete `%LOCALAPPDATA%\AddonUpdater`. On Linux it removes itself completely.
- **Stopping it for now:** on Linux, `python3 ~/.local/share/addon-updater/updater.py stop`. On Windows, end
  `pythonw.exe` in Task Manager. It starts again the next time you log in.
