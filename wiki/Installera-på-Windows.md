# Installera på Windows

🇬🇧 [[Read in English|Install on Windows]]

## Det här behöver du

- **World of Warcraft: Forever**, installerat med [Battle.net-appen](https://download.battle.net/sv-se/desktop).
  Spelet ligger i `C:\Program Files (x86)\World of Warcraft\_forever_` om du inte valt en annan mapp.
- Addonens **Windows-nedladdning** från tabellen på [[Startsida]].
- Inget annat. Addons med ett hjälpprogram (som Herald) har med sig allt de behöver.

## Vanliga addons (utan hjälpprogram)

1. Ladda ner zip-filen och packa upp den (högerklicka → **Extrahera alla** / *Extract All*).
2. Kopiera addonens mapp (t.ex. `Herald`) till `C:\Program Files (x86)\World of Warcraft\_forever_\Interface\AddOns\`.
   Skapa `Interface\AddOns` om mappen inte finns än.
3. Starta om WoW. Klicka på **AddOns** på karaktärsskärmen och se till att addonen är ibockad.

## Herald

1. Ladda ner [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Windows.zip).
2. Högerklicka på den → **Extrahera alla**, och lägg mappen på ett ställe där den får ligga kvar, t.ex. `Dokument\Herald-Windows`.
   Kör den inte inifrån zip-filen och lämna den inte i en tillfällig mapp: autostarten pekar på den här mappen.
3. Öppna mappen och dubbelklicka på **Start Herald.bat**.
   - Om Windows säger *"Windows skyddade datorn"* (*Windows protected your PC*): klicka **Mer information → Kör ändå**
     (*More info → Run anyway*). Det händer med alla nedladdade skript som inte är signerade.
4. Ett svart fönster öppnas och installationen körs. Texten i fönstret är på engelska:
   1. Den hittar WoW Forever och installerar addonen. Ligger spelet på ett ovanligt ställe frågar den efter mappen
      `World of Warcraft`: kopiera sökvägen från adressfältet i Utforskaren och klistra in den.
   2. Den frågar efter **webhook-länken** (*Webhook URL*): klistra in med högerklick eller Ctrl+V och tryck Enter.
      Länken får du av den som sköter Discord-kanalen, se [[Webhook-länken]]. Ett testmeddelande dyker upp i Discord.
   3. *"Start Herald automatically when Windows starts?"* betyder "Starta Herald automatiskt när Windows startar?".
      Tryck **Y** och Enter. Herald körs då dolt i bakgrunden, nu och efter varje omstart.
5. Stäng fönstret, starta om WoW och kolla att **Herald** är ibockad under **AddOns**. Skriv `/herald` i spelet:
   det ska stå *combat logging is ON*.

I mappen finns också **Stop Herald.bat** och **Herald Setup.bat** (byt webhook, installera om addonen,
autostart på/av). Inställningar, historik och bakgrundsloggen ligger i `%APPDATA%\Herald`: klistra in det i
adressfältet i Utforskaren för att öppna mappen.

**Uppdatera:** kör *Stop Herald.bat*, ersätt mappen med den nya nedladdningen (på samma ställe) och kör sedan
*Start Herald.bat*. Inställningarna finns kvar, och addonen i spelet uppdateras automatiskt.
