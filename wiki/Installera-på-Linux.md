# Installera på Linux

🇬🇧 [[Read in English|Install on Linux]]

På Linux körs WoW Forever via **Wine** eller **Proton**, med någon av de här startarna:

| Startare | Hämta den | Var spelet hamnar (mappen `_forever_`) |
|---|---|---|
| **Heroic** (Battle.net tillagt som spel) | [heroicgameslauncher.com](https://heroicgameslauncher.com) | `~/Games/Heroic/Prefixes/default/<namn>/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Lutris** (Battle.net-installationen) | [lutris.net](https://lutris.net) | `~/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Steam** (Battle.net som spel utanför Steam, Proton) | [store.steampowered.com](https://store.steampowered.com/about/) | `~/.local/share/Steam/steamapps/compatdata/<nummer>/pfx/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| **Bottles** | [usebottles.com](https://usebottles.com) | `~/.local/share/bottles/bottles/<flaska>/drive_c/Program Files (x86)/World of Warcraft/_forever_` |
| Vanlig **Wine** | din distributions paket | `~/.wine/drive_c/Program Files (x86)/World of Warcraft/_forever_` |

Flatpak-versioner har sina prefix under `~/.var/app/...`, och Herald letar där också.
Allt inne i spelet fungerar precis som på Windows: addons är bara filer i spelmappen.

Du installerar varje addon en gång. Sedan håller den sig själv uppdaterad: se [[Automatiska uppdateringar]].
Installationerna behöver `python3` version 3.8 eller nyare, som nästan alla distributioner redan har (se tabellen under *Herald* nedan).

## Vanliga addons (utan hjälpprogram)

1. Ladda ner addonens **Linux**-zip och packa upp den.
2. Öppna en terminal i den uppackade mappen och kör `bash install.sh`. Den hittar WoW Forever, lägger in addonen
   i spelet och slår på [[Automatiska uppdateringar]]. Hittar den inte spelet frågar den efter sökvägen till mappen
   `World of Warcraft`: använd tabellen ovan, med `World of Warcraft` i stället för `_forever_` på slutet.
3. Starta om WoW och kolla att addonen är ibockad under **AddOns** på karaktärsskärmen.

Du kan radera den uppackade mappen efteråt.

## Herald

**Du behöver `python3`** (3.8 eller nyare). Det finns redan på nästan alla distributioner, även SteamOS. Kolla med
`python3 --version`. Om det saknas:

| Distribution | Kommando |
|---|---|
| Ubuntu, Mint, Pop!_OS, Debian | `sudo apt install python3` |
| Fedora | `sudo dnf install python3` |
| Arch, Manjaro, EndeavourOS | `sudo pacman -S python` |
| openSUSE | `sudo zypper install python3` |

Sedan:

1. Ladda ner [Herald-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Linux.zip) och packa upp den.
2. Öppna en terminal i den uppackade mappen `Herald-Linux` (i de flesta filhanterare: högerklicka → *Öppna terminal här*) och kör:
   ```sh
   bash install.sh
   ```
3. Installationen (texten är på engelska):
   1. kopierar Herald till `~/.local/share/herald/program` och lägger till kommandot `herald`,
   2. hittar WoW Forever i din startares prefix, installerar addonen och slår på [[Automatiska uppdateringar]]. Hittar den inte spelet frågar den efter
      sökvägen till mappen `World of Warcraft`: använd tabellen ovan, med `World of Warcraft` i stället för `_forever_` på slutet,
   3. frågar efter **webhook-länken** (*Webhook URL*, från den som sköter Discord-kanalen, se [[Webhook-länken]]) och skickar ett testmeddelande,
   4. frågar *"Start Herald automatically when you log in?"* ("Starta Herald automatiskt när du loggar in?"): svara **Y** så sätts den upp som en systemd-användartjänst.
4. Starta om WoW, kolla att **Herald** är ibockad under **AddOns** och skriv `/herald` i spelet.

**Kommandon:** `herald start`, `herald stop`, `herald setup`, `herald test` (exempelkort), `herald list`.
Om `herald` inte hittas, använd `~/.local/bin/herald`. Bakgrundslogg: `journalctl --user -u herald -f`.

**Uppdatera:** sker automatiskt, se [[Automatiska uppdateringar]]. **Avinstallera:** `bash uninstall.sh`.

**Steam Deck:** installera från **skrivbordsläget** (Desktop Mode; terminalen heter Konsole). Om bakgrundstjänsten
fortsätter köra i spelläget (Game Mode) är inte testat än. Säg till om inga kort dyker upp där.
