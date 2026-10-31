# Platform differences

**Inside the game, every addon works the same on Windows and Linux.** Differences only show up in the helper
programs some addons come with (currently: Herald).

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

## Not supported

- **macOS:** the addon itself works, but the helper program has never been tried there.
- **Linux without systemd:** Herald works, but it can't start automatically. Run `herald start` before playing.
- **Steam Deck Game Mode:** installing works (from Desktop Mode). Running in Game Mode is untested.
