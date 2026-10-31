# Installera på Windows

🇬🇧 [[Read in English|Install on Windows]]

## Det här behöver du

- **World of Warcraft: Forever**, installerat med [Battle.net-appen](https://download.battle.net/sv-se/desktop).
  Spelet ligger i `C:\Program Files (x86)\World of Warcraft\_forever_` om du inte valt en annan mapp.
- Addonens **Windows-nedladdning** från tabellen på [[Startsida]].
- Inget annat. Varje nedladdning har med sig allt den behöver, även Python.

Du installerar varje addon en gång. Sedan håller den sig själv uppdaterad: se [[Automatiska uppdateringar]].

## Vanliga addons (utan hjälpprogram)

1. Ladda ner addonens **Windows**-zip och packa upp den (högerklicka → **Extrahera alla** / *Extract All*).
2. Öppna mappen och dubbelklicka på **Install &lt;Addon&gt;.bat**.
   - Om Windows säger *"Windows skyddade datorn"*: klicka **Mer information → Kör ändå**.
   - Den hittar WoW Forever, lägger in addonen i spelet och slår på [[Automatiska uppdateringar]]. Ligger spelet
     på ett ovanligt ställe frågar den efter mappen `World of Warcraft`: kopiera sökvägen från adressfältet i Utforskaren och klistra in den.
3. Starta om WoW. Klicka på **AddOns** på karaktärsskärmen och se till att addonen är ibockad.

Du kan radera den uppackade mappen efteråt.

## Herald

1. Ladda ner [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Windows.zip).
2. Högerklicka på den → **Extrahera alla**, och lägg mappen på ett ställe där den får ligga kvar, t.ex. `Dokument\Herald-Windows`.
   Kör den inte inifrån zip-filen och lämna den inte i en tillfällig mapp: autostarten pekar på den här mappen.
3. Öppna mappen och dubbelklicka på **Start Herald.bat**.
   - Om Windows säger *"Windows skyddade datorn"* (*Windows protected your PC*): klicka **Mer information → Kör ändå**
     (*More info → Run anyway*). Det händer med alla nedladdade skript som inte är signerade.
4. Ett svart fönster öppnas och installationen körs. Texten i fönstret är på engelska:
   1. Den hittar WoW Forever, installerar addonen och slår på [[Automatiska uppdateringar]] (*automatic updates on*).
      Ligger spelet på ett ovanligt ställe frågar den efter mappen `World of Warcraft`: kopiera sökvägen från
      adressfältet i Utforskaren och klistra in den.
   2. Den frågar efter **webhook-länken** (*Webhook URL*): klistra in med högerklick eller Ctrl+V och tryck Enter.
      Länken får du av den som sköter Discord-kanalen, se [[Webhook-länken]]. Ett testmeddelande dyker upp i Discord.
   3. *"Start Herald automatically when Windows starts?"* betyder "Starta Herald automatiskt när Windows startar?".
      Tryck **Y** och Enter. Herald körs då dolt i bakgrunden, nu och efter varje omstart.
5. Stäng fönstret, starta om WoW och kolla att **Herald** är ibockad under **AddOns**. Skriv `/herald` i spelet:
   det ska stå *combat logging is ON*.

I mappen finns också **Stop Herald.bat** och **Herald Setup.bat** (byt webhook, installera om addonen,
autostart på/av). Inställningar, historik och bakgrundsloggen ligger i `%APPDATA%\Herald`: klistra in det i
adressfältet i Utforskaren för att öppna mappen.

**Uppdatera:** sker automatiskt, se [[Automatiska uppdateringar]]. Låt mappen ligga kvar där den är: Herald körs
därifrån, och uppdateraren håller den uppdaterad.
