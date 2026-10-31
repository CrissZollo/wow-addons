# Platform differences

🇸🇪 [[Läs på svenska|Skillnader mellan Windows och Linux]]

**Inside the game, every addon works the same on Windows and Linux.** Differences only show up in the programs
on your PC: the helper programs some addons come with (currently: Herald), and the Addon Updater.

## Herald

| | Windows | Linux (Wine / Proton) |
|---|---|---|
| Features | All | All, identical |
| Python | Included in the download | Uses your system's `python3` (3.8+) |
| Install | Double-click `Start Herald.bat` | `bash install.sh` |
| Finds the game in | Battle.net's install location, and the usual folders on every drive | Heroic, Lutris, Steam (Proton), Bottles and Wine prefixes, including Flatpak |
| Runs in the background | Hidden, starts with Windows (Startup folder) | systemd user service, starts when you log in |
| Commands | `.bat` files | `herald start / stop / setup / test / list` |
| Settings and history | `%APPDATA%\Herald` | `~/.config/herald` and `~/.local/share/herald` |
| Background log | `%APPDATA%\Herald\watcher.log` | `journalctl --user -u herald` |
| Tested | Under Wine only, not on a real Windows PC yet | Arch Linux + Heroic, with test data |

## Automatic updates

| | Windows | Linux (Wine / Proton) |
|---|---|---|
| Python | Its own copy, in `%LOCALAPPDATA%\AddonUpdater\python` | Your system's `python3` (3.8+) |
| Runs in the background | Hidden, starts with Windows (*Addon Updater* in the Startup folder) | systemd user service `addon-updater`, starts when you log in |
| Program and log | `%LOCALAPPDATA%\AddonUpdater` | `~/.local/share/addon-updater` |
| Notices that WoW is running | From the list of running programs | From the running Wine/Proton processes |
| Tested | Not yet | Arch Linux, with a simulated game |

More: [[Automatic Updates]].

## Not supported

- **macOS:** the addon itself works, but the helper program has never been tried there.
- **Linux without systemd:** Herald and the Addon Updater work, but can't start automatically. Run `herald start`
  before playing. The updater runs from the install until you log out; start it again with
  `python3 ~/.local/share/addon-updater/updater.py --background &`.
- **Steam Deck Game Mode:** installing works (from Desktop Mode). Running in Game Mode is untested.
