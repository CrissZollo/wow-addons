# Install on Windows

🇸🇪 [[Läs på svenska|Installera på Windows]]

## What you need

- **World of Warcraft: Forever**, installed with the [Battle.net app](https://download.battle.net/en-us/desktop).
  The game lives in `C:\Program Files (x86)\World of Warcraft\_forever_` unless you picked another folder.
- The addon's **Windows download** from the table on [[Home]].
- Nothing else. Every download includes everything it needs, Python too.

You install each addon once. After that it keeps itself up to date: see [[Automatic Updates]].

## Plain addons (no helper program)

1. Download the addon's **Windows** zip and extract it (right-click → **Extract All**).
2. Open the folder and double-click **Install &lt;Addon&gt;.bat**.
   - If Windows says *"Windows protected your PC"*: click **More info → Run anyway**.
   - It finds WoW Forever, puts the addon in the game and turns on [[Automatic Updates]]. If your game is
     somewhere unusual, it asks for the `World of Warcraft` folder: copy the path from File Explorer's address bar and paste it.
3. Restart WoW. On the character screen, click **AddOns** and make sure the addon is ticked.

You can delete the extracted folder afterwards.

## Herald

1. Download [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.1.0/Herald-Windows.zip).
2. Right-click it → **Extract All**, and put the folder somewhere permanent, e.g. `Documents\Herald-Windows`.
   Don't run it from inside the zip, and don't leave it in a temporary folder: the autostart points to this folder.
3. Open the folder and double-click **Start Herald.bat**.
   - If Windows says *"Windows protected your PC"*: click **More info → Run anyway**. This happens with any
     downloaded script that isn't signed.
4. A black window opens and the setup runs:
   1. It finds WoW Forever, installs the addon and turns on [[Automatic Updates]]. If your game is somewhere
      unusual, it asks for the `World of Warcraft` folder: copy the path from File Explorer's address bar and paste it.
   2. It asks for the **webhook link**: paste it with right-click or Ctrl+V and press Enter
      (you get the link from whoever runs the Discord channel, see [[Discord Webhook]]). A test message appears in Discord.
   3. *"Start Herald automatically when Windows starts?"*: press **Y** and Enter. Herald then runs
      hidden in the background, now and after every restart.
5. Close the window, restart WoW, and check that **Herald** is ticked under **AddOns**. In game, type `/herald`:
   it should say *combat logging is ON*.

The folder also has **Stop Herald.bat** and **Herald Setup.bat** (change the webhook, reinstall the addon,
autostart on/off). Settings, history and the background log are in `%APPDATA%\Herald`: paste that into
File Explorer's address bar to open it.

**Updating:** automatic, see [[Automatic Updates]]. Keep the folder where it is: Herald runs from it, and the
updater keeps it up to date.
