# Install on Windows

🇸🇪 [[Läs på svenska|Installera på Windows]]

## What you need

- **World of Warcraft: Forever**, installed with the [Battle.net app](https://download.battle.net/en-us/desktop).
  The game lives in `C:\Program Files (x86)\World of Warcraft\_forever_` unless you picked another folder.
- The addon's **Windows download** from the table on [[Home]].
- Nothing else. Addons with a helper program (like Herald) include everything they need.

## Plain addons (no helper program)

1. Download the zip and extract it (right-click → **Extract All**).
2. Copy the addon's folder (e.g. `Herald`) into `C:\Program Files (x86)\World of Warcraft\_forever_\Interface\AddOns\`.
   Create `Interface\AddOns` if it doesn't exist yet.
3. Restart WoW. On the character screen, click **AddOns** and make sure the addon is ticked.

## Herald

1. Download [Herald-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/Herald-v1.0.0/Herald-Windows.zip).
2. Right-click it → **Extract All**, and put the folder somewhere permanent, e.g. `Documents\Herald-Windows`.
   Don't run it from inside the zip, and don't leave it in a temporary folder: the autostart points to this folder.
3. Open the folder and double-click **Start Herald.bat**.
   - If Windows says *"Windows protected your PC"*: click **More info → Run anyway**. This happens with any
     downloaded script that isn't signed.
4. A black window opens and the setup runs:
   1. It finds WoW Forever and installs the addon. If your game is somewhere unusual, it asks for the
      `World of Warcraft` folder: copy the path from File Explorer's address bar and paste it.
   2. It asks for the **webhook link**: paste it with right-click or Ctrl+V and press Enter
      (you get the link from whoever runs the Discord channel, see [[Discord Webhook]]). A test message appears in Discord.
   3. *"Start Herald automatically when Windows starts?"*: press **Y** and Enter. Herald then runs
      hidden in the background, now and after every restart.
5. Close the window, restart WoW, and check that **Herald** is ticked under **AddOns**. In game, type `/herald`:
   it should say *combat logging is ON*.

The folder also has **Stop Herald.bat** and **Herald Setup.bat** (change the webhook, reinstall the addon,
autostart on/off). Settings, history and the background log are in `%APPDATA%\Herald`: paste that into
File Explorer's address bar to open it.

**Updating:** run *Stop Herald.bat*, replace the folder with the new download (same place), then run
*Start Herald.bat*. Settings are kept, and the addon in the game is updated automatically.
