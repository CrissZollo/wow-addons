# Webhook-länken

🇬🇧 [[Read in English|Discord Webhook]]

Addons som postar i Discord (som [[Herald på svenska]]) behöver en **webhook-länk**: en privat adress som låter ett
program posta meddelanden i en viss kanal. En person, den som sköter Discord-servern, skapar den en gång och
delar den med gänget.

## Skapa webhooken (kanalens ägare)

1. I Discord: håll muspekaren över kanalen → ⚙️ **Redigera kanal** → **Integrationer** → **Webhooks** → **Ny webhook**.
   Du behöver behörigheten *Hantera webhooks* på servern.
2. Ge den gärna ett namn och en bild. Herald sätter ändå sitt eget namn ("Herald") när den postar.
3. Klicka **Kopiera webhook-URL**. Den ser ut ungefär så här: `https://discord.com/api/webhooks/123456789/AbCdEf...`.
4. Skicka den till kompisarna **privat**, t.ex. i ett DM. Alla använder **samma** länk, och varje kort visar vems
   karaktär det handlar om.

## Håll den hemlig

Den som har länken kan posta i kanalen. Klistra därför inte in den i öppna kanaler, på skärmdumpar eller på GitHub.

**Om den läcker ut:** radera webhooken i samma Integrationer-meny, skapa en ny och skicka runt den nya länken.
Alla kör sedan `Herald Setup.bat` (Windows) eller `herald setup` (Linux) och klistrar in den nya länken.
