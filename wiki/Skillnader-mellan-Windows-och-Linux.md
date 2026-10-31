# Skillnader mellan Windows och Linux

🇬🇧 [[Read in English|Platform Differences]]

**Inne i spelet fungerar alla addons likadant på Windows och Linux.** Skillnaderna gäller bara programmen på
datorn: hjälpprogrammen som vissa addons har med sig (just nu: Herald) och Addon Updater.

## Herald

| | Windows | Linux (Wine / Proton) |
|---|---|---|
| Funktioner | Alla | Alla, likadana |
| Python | Följer med i nedladdningen | Använder systemets `python3` (3.8+) |
| Installation | Dubbelklicka på `Start Herald.bat` | `bash install.sh` |
| Hittar spelet i | Battle.nets installationsplats, och de vanliga mapparna på alla enheter | Prefix från Heroic, Lutris, Steam (Proton), Bottles och Wine, även Flatpak |
| Körs i bakgrunden | Dolt, startar med Windows (mappen Autostart) | systemd-användartjänst, startar när du loggar in |
| Kommandon | `.bat`-filer | `herald start / stop / setup / test / list` |
| Inställningar och historik | `%APPDATA%\Herald` | `~/.config/herald` och `~/.local/share/herald` |
| Bakgrundslogg | `%APPDATA%\Herald\watcher.log` | `journalctl --user -u herald` |
| Testad | Bara under Wine, inte på en riktig Windows-dator än | Arch Linux + Heroic, med testdata |

## Automatiska uppdateringar

| | Windows | Linux (Wine / Proton) |
|---|---|---|
| Python | En egen kopia, i `%LOCALAPPDATA%\AddonUpdater\python` | Systemets `python3` (3.8+) |
| Körs i bakgrunden | Dolt, startar med Windows (*Addon Updater* i mappen Autostart) | systemd-användartjänsten `addon-updater`, startar när du loggar in |
| Program och logg | `%LOCALAPPDATA%\AddonUpdater` | `~/.local/share/addon-updater` |
| Märker att WoW körs | Via listan över program som körs | Via Wine/Proton-processerna som körs |
| Testad | Inte än | Arch Linux, med ett simulerat spel |

Mer: [[Automatiska uppdateringar]].

## Stöds inte

- **macOS:** själva addonen fungerar, men hjälpprogrammet har aldrig provats där.
- **Linux utan systemd:** Herald och Addon Updater fungerar, men kan inte starta automatiskt. Kör `herald start`
  innan du spelar. Uppdateraren körs från installationen tills du loggar ut; starta den igen med
  `python3 ~/.local/share/addon-updater/updater.py --background &`.
- **Steam Decks spelläge:** installationen fungerar (från skrivbordsläget). Körning i spelläget är otestad.
