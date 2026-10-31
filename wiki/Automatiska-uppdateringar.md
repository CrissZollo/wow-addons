# Automatiska uppdateringar

🇬🇧 [[Read in English|Automatic Updates]]

Alla addons här håller sig själva uppdaterade. Du laddar ner och installerar en addon en gång. Efter det
installerar ett litet program på din dator, **Addon Updater** ("addon-uppdateraren"), nya versioner åt dig.

## Så fungerar det

- **Addonens installation sätter upp den.** *Start Herald.bat*, `bash install.sh` eller *Install &lt;Addon&gt;.bat*
  slår på automatiska uppdateringar som en del av installationen. Det finns inget extra att ladda ner eller klicka på.
- **Den körs i bakgrunden** och startar när du loggar in på datorn. Den letar efter nya versioner
  **var 30:e minut**.
- **Den uppdaterar allt som hör till addonen:** addonen i spelet, dess hjälpprogram (som Heralds) och sig
  själv. Dina inställningar och din historik rörs aldrig.
- **En och samma uppdaterare sköter alla addons** från den här wikin, hur många du än installerar.
- Den lägger också in en liten addon i spelet som heter **Addon Updater**. Det är den som berättar om
  uppdateringar. Låt den vara ibockad i AddOns-listan.

## Det här ser du i spelet

Meddelandena är på engelska:

| När | Meddelande i chattfönstret |
|---|---|
| Du loggar in efter en uppdatering | *Addon Updater: Herald updated: 1.0.0 -> 1.1.0 - (vad som är nytt)*, alltså "Herald uppdaterad" |
| En uppdatering kommer medan du spelar, och det räcker med `/reload` | *An addon update was installed. Type /reload to start using it.* ("En uppdatering är installerad. Skriv /reload för att börja använda den.") |
| En uppdatering kommer medan du spelar, och WoW måste startas om | *An addon update is ready. It installs when you close WoW; it's there next time you play.* ("En uppdatering är klar. Den installeras när du stänger WoW och finns där nästa gång du spelar.") |

Skriv `/updates` i spelet för att se versionen av varje addon som hålls uppdaterad.

## Medan du spelar

Medan spelet körs kan WoW-addons inte höra något från program på datorn. De läser bara sina filer när du
loggar in eller skriver `/reload`. Därför:

- **Uppdateringar som bara ändrar befintliga filer** installeras direkt. Skriv `/reload` när du blir ombedd,
  eller fortsätt bara spela: du får den nya versionen nästa gång du loggar in.
- **Uppdateringar som lägger till eller tar bort filer** väntar tills du stänger WoW, och installeras några
  sekunder efter. WoW märker bara nya filer när det startar.

De två meddelandena under spelets gång är **på försök**: de bygger på ett trick (uppdateraren byter ut en
pytteliten typsnittsfil som addonen i spelet försöker läsa in) som inte har provats i WoW Forever än. Om de
aldrig dyker upp går inget sönder. Uppdateringarna installeras ändå, och du ser *updated*-meddelandet nästa
gång du loggar in.

**Testa meddelandet i spelet** (med WoW igång och en karaktär inloggad):

- **Windows:** tryck **Win+R**, klistra in det här och tryck Enter:
  `cmd /k ""%LOCALAPPDATA%\AddonUpdater\python\python.exe" "%LOCALAPPDATA%\AddonUpdater\updater.py" notice-test"`
- **Linux:** `python3 ~/.local/share/addon-updater/updater.py notice-test`

Inom ungefär 30 sekunder ska spelet säga *Type /reload to start using it*. Testet stänger av sig självt
efter 10 minuter.

## Kolla läget

| | Windows | Linux |
|---|---|---|
| Var den ligger | `%LOCALAPPDATA%\AddonUpdater` (klistra in i adressfältet i Utforskaren) | `~/.local/share/addon-updater` |
| Logg (vad den gjort och när) | `updater.log` i den mappen | `updater.log` i den mappen |
| Status och kolla nu | **Win+R**: `cmd /k ""%LOCALAPPDATA%\AddonUpdater\python\python.exe" "%LOCALAPPDATA%\AddonUpdater\updater.py" status"` (eller `check`) | `python3 ~/.local/share/addon-updater/updater.py status` (eller `check`) |
| Startar via | Genvägen *Addon Updater* i mappen Autostart | systemd-användartjänsten `addon-updater` |

Den pratar bara med GitHub: den hämtar listan över de senaste versionerna och filerna som ändrats, och
kontrollerar varje fil mot en kontrollsumma innan den installeras. Den skickar inget om dig eller din dator.

## Stänga av den

- **Avinstallera en addon:** radera dess mapp i `_forever_/Interface/AddOns` (varje addons sida säger vad mer
  som ska bort). Uppdateraren märker det och slutar uppdatera den.
- När ingen av de här addonsen finns kvar stänger uppdateraren av sig själv och tar bort sin addon i spelet.
  På Windows kan du sedan radera `%LOCALAPPDATA%\AddonUpdater`. På Linux tar den bort sig själv helt.
- **Stoppa den tills vidare:** på Linux, `python3 ~/.local/share/addon-updater/updater.py stop`. På Windows,
  avsluta `pythonw.exe` i Aktivitetshanteraren. Den startar igen nästa gång du loggar in.
