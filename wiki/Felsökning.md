# Felsökning

🇬🇧 [[Read in English|Troubleshooting]]

## Alla addons

| Problem | Lösning |
|---|---|
| Addonen syns inte i AddOns-listan | Mappen måste ligga direkt i `_forever_/Interface/AddOns/` med sin `.toc`-fil i: `AddOns/Herald/Herald.toc`, inte `AddOns/Herald/Herald/Herald.toc`. Starta om spelet helt (`/reload` hittar inte nya addons) |
| Addonen visas som *out of date* (inaktuell) | Bocka i **Load out of date AddOns** högst upp i AddOns-listan |

## Automatiska uppdateringar

| Problem | Lösning |
|---|---|
| En ny version kommer inte | Uppdateraren letar var 30:e minut. Titta i dess logg och status ([[Automatiska uppdateringar]]): där står vad den gjort, eller varför den inte nådde GitHub |
| Statusen säger *waits until WoW closes* ("väntar tills WoW stängs") | Normalt: uppdateringen lägger till eller tar bort filer, och sådant märker WoW bara när det startar. Stäng WoW så installeras den några sekunder senare |
| `/updates` säger att inget hålls uppdaterat, eller *Addon Updater* saknas i AddOns-listan | Kör addonens installation igen (*Start Herald.bat*, *Install &lt;Addon&gt;.bat* eller `bash install.sh`) |
| Inget meddelande medan du spelar | Meddelandena under spelets gång är på försök och fungerar kanske inte i WoW Forever. Uppdateringarna installeras ändå, och meddelandet vid inloggning berättar om dem |
| Du installerade Herald 1.0.0 | Version 1.0.0 kom före de automatiska uppdateringarna. Installera en nyare version en gång, på vanligt sätt |

## Herald

| Problem | Lösning |
|---|---|
| Inget postas | 1) I spelet ska `/herald` säga att combat logging är ON. 2) Hjälpprogrammet måste vara igång: starta det igen, så säger det till om det redan körs. 3) Titta i bakgrundsloggen ([[Skillnader mellan Windows och Linux]]) |
| Testmeddelandet misslyckades under installationen | Webhook-länken är fel eller har raderats. Be om en ny ([[Webhook-länken]]) och kör installationen igen |
| Korten kommer sent | Spelet skriver sin stridslogg i omgångar, så några sekunders fördröjning är normalt (mer när det händer lite) |
| Inga nivåkort eller framstegsrapporter | De postas bara när du **loggar ut eller skriver `/reload`**, och framstegsrapporten kräver 5+ minuters spel sedan förra |
| Nivåkortet saknar skärmdump | Spelet kan hindra addons från att ta skärmdumpar. Kortet postas ändå, utan bild |
| Länkarna till varelserna öppnar fel sida | Ändra `npc_url` i inställningarna till `https://www.wowhead.com/classic/npc={id}` |
| Installationen hittar inte spelet | Klistra in sökvägen till din mapp `World of Warcraft` när den frågar (se [[Installera på Windows]] / [[Installera på Linux]] för vanliga platser) |
| Windows: *"Windows skyddade datorn"* | **Mer information → Kör ändå** |
| Linux: `herald: command not found` | Använd `~/.local/bin/herald`, eller lägg till `~/.local/bin` i din PATH |

Kommer du inte vidare? Fråga i gängets Discord och ta med vad bakgrundsloggen säger.
