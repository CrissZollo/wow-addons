# WoW addons

Addons for World of Warcraft (mainly WoW Forever), one folder per addon.

| Addon | What it does |
|---|---|
| [FirstKills](FirstKills/) | Posts first kills, boss kills, enemy players, level milestones and progress reports to a Discord channel, with a watcher program for Linux and a no-install Windows package |

## Adding a new addon

Create a folder named exactly like the addon (the folder name must match its `.toc`
file), put the `.toc` and `.lua` files in it, add a `README.md`, and add a row to the
table above.

## Installing an addon

Copy (or on Linux, symlink) the addon's folder into
`World of Warcraft/_forever_/Interface/AddOns/`. Some addons need extra setup;
see their own README.
