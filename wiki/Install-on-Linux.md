# Install on Linux

On Linux, WoW Forever runs through **Wine** or **Proton**, using one of these launchers:

| Launcher | Get it | Where the game ends up (`_forever_` folder) |
|---|---|---|
| **Heroic** (Battle.net added as a game) | [heroicgameslauncher.com](https://heroicgameslauncher.com) | `~/Games/Heroic/Prefixes/default/<name>/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Lutris** (Battle.net installer) | [lutris.net](https://lutris.net) | `~/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Steam** (Battle.net as a non-Steam game, Proton) | [store.steampowered.com](https://store.steampowered.com/about/) | `~/.local/share/Steam/steamapps/compatdata/<number>/pfx/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Bottles** | [usebottles.com](https://usebottles.com) | `~/.local/share/bottles/bottles/<bottle>/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| Plain **Wine** | your distro's packages | `~/.wine/drive_c/Program Files (x86)/World of Warcraft/_forever_` |

Flatpak versions keep their prefixes under `~/.var/app/...`. Herald looks there too.
Everything inside the game works exactly like on Windows: addons are just files in the game folder.

## Plain addons (no helper program)

1. Download the zip and extract it.
2. Copy the addon's folder into the `_forever_/Interface/AddOns/` folder from the table above
   (create `Interface/AddOns` if it doesn't exist yet).
3. Restart WoW and check that the addon is ticked under **AddOns** on the character screen.

## Herald

**You need `python3`** (3.8 or newer). It's preinstalled on almost every distro, including SteamOS. Check with
`python3 --version`. If it's missing:

| Distro | Command |
|---|---|
| Ubuntu, Mint, Pop!_OS, Debian | `sudo apt install python3` |
| Fedora | `sudo dnf install python3` |
| Arch, Manjaro, EndeavourOS | `sudo pacman -S python` |
| openSUSE | `sudo zypper install python3` |

Then:

1. Download [Herald-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Linux.zip) and extract it.
2. Open a terminal in the extracted `Herald-Linux` folder (most file managers: right-click → *Open Terminal Here*) and run:
   ```sh
   bash install.sh
   ```
3. The installer:
   1. copies Herald to `~/.local/share/herald/program` and adds the `herald` command,
   2. finds WoW Forever in your launcher's prefix and installs the addon. If it can't, it asks for the path
      to the `World of Warcraft` folder: use the table above, with `World of Warcraft` instead of `_forever_` at the end,
   3. asks for the **webhook link** (from whoever runs the Discord channel, see [[Discord Webhook]]) and sends a test message,
   4. asks *"Start Herald automatically when you log in?"*: answer **Y** to set it up as a systemd user service.
4. Restart WoW, check that **Herald** is ticked under **AddOns**, and type `/herald` in game.

**Commands:** `herald start`, `herald stop`, `herald setup`, `herald test` (sample cards), `herald list`.
If `herald` isn't found, use `~/.local/bin/herald`. Background log: `journalctl --user -u herald -f`.

**Updating:** extract the new zip and run `bash install.sh` again. **Uninstalling:** `bash uninstall.sh`.

**Steam Deck:** install from **Desktop Mode** (Konsole is the terminal). Whether the background service keeps
running in Game Mode hasn't been tested yet. If posts don't appear there, report it.
