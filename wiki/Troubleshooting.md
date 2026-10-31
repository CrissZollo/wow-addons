# Troubleshooting

## Any addon

| Problem | Fix |
|---|---|
| The addon isn't in the AddOns list | The folder must sit directly in `_forever_/Interface/AddOns/` with its `.toc` file inside: `AddOns/Herald/Herald.toc`, not `AddOns/Herald/Herald/Herald.toc`. Restart the game completely (`/reload` doesn't find new addons) |
| The addon shows as *out of date* | Tick **Load out of date AddOns** at the top of the AddOns list |

## Herald

| Problem | Fix |
|---|---|
| Nothing gets posted | 1) In game, `/herald` must say combat logging is ON. 2) The helper program must be running: start it again, and it tells you if it already is. 3) Check the background log ([[Platform Differences]]) |
| The test message failed during setup | The webhook link is wrong or was deleted. Ask for a new one ([[Discord Webhook]]) and run the setup again |
| Posts come late | The game writes its combat log in batches, so a few seconds of delay is normal (more when little is happening) |
| No level or progress cards | They only post when you **log out or `/reload`**, and the progress report needs 5+ minutes of play since the last one |
| The level card has no screenshot | The game may block addons from taking screenshots. The card still posts without it |
| The creature links open the wrong page | Set `npc_url` in the settings to `https://www.wowhead.com/classic/npc={id}` |
| Setup can't find the game | Paste the path to your `World of Warcraft` folder when asked (see [[Install on Windows]] / [[Install on Linux]] for typical locations) |
| Windows: *"Windows protected your PC"* | **More info → Run anyway** |
| Linux: `herald: command not found` | Use `~/.local/bin/herald`, or add `~/.local/bin` to your PATH |

Still stuck? Ask in the group's Discord and include what the background log says.
