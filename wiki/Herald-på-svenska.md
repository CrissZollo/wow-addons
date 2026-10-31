# Herald på svenska

🇬🇧 [[Read in English|Herald]]

Herald postar dina äventyr i WoW Forever i gängets Discord-kanal: första kills, bosskills, nivåmilstolpar och framstegsrapporter.

## Vad den gör

| Kort | Vad det visar | När det postas |
|---|---|---|
| ⚔️ ⭐ 💎 💀 **First kill** | Första gången din karaktär dödar en viss sorts monster: en bild på varelsen, en Wowhead-länk och dess typ och rang (grönt vanlig, guld elit, blått/lila rare, orange boss) | Några sekunder efter killen |
| 🏆 **BOSS DOWN** | En dungeon- eller raidboss som ni har besegrat | Några sekunder efter killen |
| 🩸 **Fiendespelare** | Första gången du dödar varje fiendespelare | Några sekunder efter killen |
| 🎖️ **LEVEL 10 / 20 / 30 …** | Nivån du nått, med en skärmdump från ögonblicket du gick upp i nivå | När du loggar ut eller skriver `/reload` |
| 📈 **Framstegsrapport** | Nivå och XP, guld, alla stats och din utrustning jämfört med förra rapporten, plus allt du har på dig | När du loggar ut eller skriver `/reload`, om du spelat minst 5 minuter sedan förra rapporten |

Nivåkort och framstegsrapporter väntar tills du loggar ut eller skriver `/reload`, eftersom det är enda gången
WoW låter addons spara sin data.

Herald består av två delar, och installationen sätter upp båda:

1. **Addonen** i WoW håller stridsloggningen (combat log) igång, sparar din karaktärs stats och utrustning och tar en skärmdump vid milstolpsnivåer.
2. **Ett litet hjälpprogram** på din dator läser det spelet skriver till disken och postar det i Discord. Addons
   kan inte nå internet på egen hand. **Hjälpprogrammet måste vara igång medan du spelar.** Installationen
   ordnar så att det startar av sig självt.

## Ladda ner

| Windows | Linux (Wine / Proton) |
|---|---|
| [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Windows.zip) | [Herald-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Linux.zip) |

Äldre versioner finns på [releasesidan](https://github.com/CrissZollo/wow-addons/releases).

## Det här behöver du

| | Windows | Linux |
|---|---|---|
| WoW Forever | Installerat via Battle.net | Installerat via Battle.net i Heroic, Lutris, Steam (Proton), Bottles eller Wine |
| Python | Inget att installera, det följer med | `python3` version 3.8 eller nyare, som redan finns på nästan alla distributioner (se [[Installera på Linux]]) |
| Discord-webhook-länk | Fråga den som sköter kanalen ([[Webhook-länken]]) | Samma |

## Installera

- **Windows:** packa upp zip-filen på ett ställe där den får ligga kvar, dubbelklicka på **Start Herald.bat**, klistra in
  webhook-länken, svara **Y** på frågan om autostart och starta om WoW. Steg för steg: [Installera på Windows → Herald](Installera-på-Windows#herald)
- **Linux:** packa upp zip-filen, kör `bash install.sh` i en terminal, klistra in webhook-länken, svara **Y** på
  frågan om autostart och starta om WoW. Steg för steg: [Installera på Linux → Herald](Installera-på-Linux#herald)

## Kolla att det fungerar

1. På karaktärsskärmen är **Herald** ibockad under *AddOns*.
2. I spelet säger `/herald` *combat logging is ON*.
3. Döda något du aldrig dödat med den karaktären. Ett kort dyker upp i Discord några sekunder senare.

## Så använder du den

| I spelet | |
|---|---|
| `/herald` | Visar om stridsloggningen är på och hur länge sessionen har pågått |
| `/reload` | Postar en framstegsrapport direkt, om du spelat 5+ minuter sedan förra |
| `/updates` | Visar Heralds version (från Addon Updater, se [[Automatiska uppdateringar]]) |

| På datorn | Windows | Linux |
|---|---|---|
| Starta | `Start Herald.bat` | `herald start` |
| Stoppa | `Stop Herald.bat` | `herald stop` |
| Byt webhook, installera om addonen, autostart på/av | `Herald Setup.bat` | `herald setup` |
| Posta exempelkort i Discord | — | `herald test` |
| Lista dina registrerade första kills | — | `herald list` |

Flera kompisar kan använda **samma webhook**. Allas kort hamnar i samma kanal, och varje kort visar vems kill det är.

## Inställningar

Installationen skriver `config.json` åt dig: i `%APPDATA%\Herald` på Windows, eller `~/.config/herald` på Linux.
Du behöver bara ändra i den för de här extrasakerna. Starta om Herald efteråt.

| Inställning | Vad den gör |
|---|---|
| `ignore` | Namn på monster som aldrig postas, t.ex. `["Rabbit", "Squirrel"]` |
| `min_report_minutes` | Speltid som krävs mellan framstegsrapporter (standard 5) |
| `logs_dir` | Spelets mapp `_forever_/Logs`, om den inte hittas automatiskt |
| `npc_url`, `item_url` | Vart länkarna för varelser och föremål går (standard: Wowheads Forever-sidor) |
| `player_url` | En länk för fiendespelare, med `{name}` och `{realm}` (standard: ingen länk) |

## Uppdatera

Sker automatiskt. Installationen slår på Addon Updater, som installerar nya versioner av addonen och av
hjälpprogrammet inom 30 minuter efter en release, och startar om hjälpprogrammet av sig själv. I spelet ser du
*Herald updated: … -> …* ("Herald uppdaterad") nästa gång du loggar in. Detaljer: [[Automatiska uppdateringar]].

Låt Windows-mappen ligga kvar där du packade upp den: Herald körs därifrån, och uppdateraren håller den aktuell.
Dina inställningar och din historik rörs aldrig.

**Installerade du version 1.0.0?** Den kom före de automatiska uppdateringarna. Installera en nyare version en
gång, på samma sätt som första gången (på Windows: *Stop Herald.bat*, ersätt mappen, *Start Herald.bat*). Sedan
uppdaterar den sig själv.

## Avinstallera

- **Windows:** kör `Herald Setup.bat` och svara **N** på frågan om autostart, kör `Stop Herald.bat`, radera mappen
  och radera `Herald` i `_forever_\Interface\AddOns`. Inställningarna ligger i `%APPDATA%\Herald`. Addon Updater
  slutar då uppdatera Herald. Var Herald din enda addon härifrån stänger den av sig själv, och du kan radera
  `%LOCALAPPDATA%\AddonUpdater`.
- **Linux:** kör `bash uninstall.sh` från nedladdningen (den stoppar också uppdateringarna) och radera `Herald` i
  `_forever_/Interface/AddOns`.

## Kända begränsningar

- **Inte testad i det riktiga spelet än** (WoW Forever släpps 4 november 2026). Allt är testat med simulerad speldata.
- Bara kills av dig eller din grupp räknas. Spelets stridslogg täcker bara det som händer nära dig.
- Kort för fiendespelare saknar bild, eftersom spelets logg inte anger deras klass eller ras.
- Bilderna på varelserna kommer från Wowhead och är troligen Classic-modellerna.
- Meddelandet *type /reload* i spelet, för uppdateringar som kommer medan du spelar, är på försök ([[Automatiska uppdateringar]]).
- Mer: [[Skillnader mellan Windows och Linux]] och [[Felsökning]].
