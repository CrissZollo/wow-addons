#!/usr/bin/env python3
"""Watch the WoW combat log and post each character's first kills to Discord.

Posts a Discord embed for:
  - the first kill of each mob type, linked to Wowhead and coloured by rank
    (normal / elite / rare / boss)
  - dungeon and raid boss encounters (ENCOUNTER_END)
  - the first time you kill each enemy player

Needs combat logging on in-game (/combatlog, or the FirstKills addon does it for you).
Config and state: ~/.config/wow-firstkills + ~/.local/share/wow-firstkills (Linux),
%APPDATA%\\FirstKills (Windows).

  wow-firstkills.py              watch the log and post (default)
  wow-firstkills.py setup        find the game, install the addon, set the webhook
  wow-firstkills.py start        setup if needed, then watch (what Start FirstKills.bat runs)
  wow-firstkills.py stop         stop a watcher running in the background
  wow-firstkills.py autostart on|off   start with Windows (Windows only)
  wow-firstkills.py test         post sample messages to the webhook
  wow-firstkills.py list         show recorded first kills
  add --dry-run to print the messages instead of posting them
"""
import csv
import html
import json
import os
import re
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path

SCRIPT = Path(__file__).resolve()
sys.path.insert(0, str(SCRIPT.parent))  # the embeddable Windows Python doesn't add it
import progress  # noqa: E402

IS_WIN = os.name == "nt"
if IS_WIN:
    APP_DIR = Path(os.environ.get("APPDATA", Path.home())) / "FirstKills"
    CONFIG_PATH = APP_DIR / "config.json"
    STATE_PATH = APP_DIR / "kills.json"
else:
    CONFIG_PATH = (Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
                   / "wow-firstkills" / "config.json")
    STATE_PATH = (Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
                  / "wow-firstkills" / "kills.json")
LOCK_PATH = STATE_PATH.with_name("watcher.lock")
STOP_PATH = STATE_PATH.with_name("watcher.stop")
LOG_PATH = STATE_PATH.with_name("watcher.log")

DEFAULTS = {
    "webhook_url": "",
    # Empty = find the game automatically.
    "logs_dir": "",
    "ignore": [],
    "poll_seconds": 1.0,
    # Wowhead data set used for mob info and links ("forever", "classic", ...).
    "wowhead_env": "forever",
    "npc_url": "https://www.wowhead.com/forever/npc={id}",
    "search_url": "https://www.wowhead.com/forever/search?q={query}",
    "item_url": "https://www.wowhead.com/forever/item={id}",
    # Link for enemy players, e.g. an armory page. Placeholders: {name} {realm}. Empty = no link.
    "player_url": "",
    # Progress report: only when at least this much was played since the last one.
    "min_report_minutes": 5,
    # Default to the WTF and Screenshots folders next to logs_dir.
    "wtf_dir": "",
    "screenshots_dir": "",
}
REPORTS_PATH = STATE_PATH.with_name("reports.json")
UA = "wow-firstkills/1.1"
PSEP = "pvp:"  # state key prefix for enemy players

AFFIL_MINE, AFFIL_PARTY, AFFIL_RAID = 0x1, 0x2, 0x4
REACTION_HOSTILE = 0x40
TYPE_PLAYER = 0x400
NPC_PREFIXES = ("Creature-", "Vehicle-")

ICON = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"
RENDER = "https://wow.zamimg.com/modelviewer/{env}/webthumbs/npc/{bucket}/{display}.png"
# rank -> (embed colour, thumbnail icon, title emoji, label)
STYLES = {
    "normal":     (0x2ECC71, "ability_warrior_rampage",      "⚔️", "Normal"),
    "elite":      (0xF1C40F, "inv_sword_04",                 "⭐", "Elite"),
    "rare":       (0x5DADE2, "inv_misc_gem_diamond_02",      "💎", "Rare"),
    "rare elite": (0xA335EE, "inv_misc_gem_diamond_02",      "💎", "Rare Elite"),
    "boss":       (0xFF8000, "inv_misc_head_dragon_01",      "💀", "Boss"),
    "encounter":  (0xFF8000, "achievement_boss_onyxia",      "🏆", "Boss encounter"),
    "pvp":        (0xC0392B, "achievement_pvp_a_01",         "🩸", "Enemy player"),
}
MILESTONES = {10, 25, 50, 100, 250, 500, 750, 1000}


def log(msg):
    print(f"[firstkills] {msg}", flush=True)


def read_raw_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    return {}


def save_raw_config(raw):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps({**DEFAULTS, **raw}, indent=2) + "\n", encoding="utf-8")
    if not IS_WIN:
        CONFIG_PATH.chmod(0o600)


def game_dir_candidates():
    """Places where WoW Forever's _forever_ folder usually is."""
    if IS_WIN:
        import winreg
        for key in (r"SOFTWARE\WOW6432Node\Blizzard Entertainment\World of Warcraft",
                    r"SOFTWARE\Blizzard Entertainment\World of Warcraft"):
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
                    p = Path(winreg.QueryValueEx(k, "InstallPath")[0])
                    yield p / "_forever_"
                    yield p.parent / "_forever_"  # InstallPath may point at _retail_
            except OSError:
                pass
        for drive in string.ascii_uppercase:
            if os.path.exists(f"{drive}:\\"):
                for sub in ("Program Files (x86)", "Program Files", "Games", "Blizzard", ""):
                    yield Path(f"{drive}:\\") / sub / "World of Warcraft" / "_forever_"
    else:
        home = Path.home()
        yield from home.glob("Games/Heroic/Prefixes/*/*/drive_c/Program Files (x86)/"
                             "World of Warcraft/_forever_")
        yield from home.glob("Games/*/drive_c/Program Files (x86)/World of Warcraft/_forever_")
        yield home / ".wine/drive_c/Program Files (x86)/World of Warcraft/_forever_"


def is_game_dir(p):
    return p.is_dir() and any((p / x).exists() for x in ("Wow.exe", "Interface", "Logs", "WTF"))


def find_game_dir():
    return next((p for p in game_dir_candidates() if is_game_dir(p)), None)


def load_config():
    cfg = dict(DEFAULTS)
    cfg.update(read_raw_config())
    if not CONFIG_PATH.exists():
        save_raw_config({})
        log(f"wrote a default config to {CONFIG_PATH}")
    if cfg["logs_dir"]:
        cfg["logs_dir"] = Path(os.path.expanduser(cfg["logs_dir"]))
    else:
        game = find_game_dir()
        cfg["logs_dir"] = (game or Path("_forever_")) / "Logs"
        if not game:
            log("couldn't find the WoW Forever folder; run setup or set logs_dir in the config")
    game_dir = cfg["logs_dir"].parent
    cfg["wtf_dir"] = Path(os.path.expanduser(cfg["wtf_dir"])) if cfg["wtf_dir"] else game_dir / "WTF"
    cfg["screenshots_dir"] = (Path(os.path.expanduser(cfg["screenshots_dir"]))
                              if cfg["screenshots_dir"] else game_dir / "Screenshots")
    cfg["ignore"] = {n.lower() for n in cfg["ignore"]}
    return cfg


def load_state():
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_PATH)


# ---------------------------------------------------------------- Discord

def multipart(payload, attachment):
    """Webhook body with an uploaded file; the embed refers to it as attachment://<name>."""
    boundary = uuid.uuid4().hex
    ctype = "image/png" if attachment.suffix.lower() == ".png" else "image/jpeg"
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"payload_json\"\r\n"
            f"Content-Type: application/json\r\n\r\n").encode() + json.dumps(payload).encode()
    body += (f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"files[0]\"; "
             f"filename=\"{attachment.name}\"\r\nContent-Type: {ctype}\r\n\r\n").encode()
    body += attachment.read_bytes() + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def post(cfg, payload, dry_run=False, attachment=None):
    payload = {"username": "First Kills", "allowed_mentions": {"parse": []}, **payload}
    if dry_run:
        log("would post:\n" + json.dumps(payload, indent=2, ensure_ascii=False)
            + (f"\n  + attachment {attachment}" if attachment else ""))
        return True
    if not cfg["webhook_url"]:
        log(f"no webhook_url in {CONFIG_PATH}; not posting")
        return False
    if attachment:
        body, ctype = multipart(payload, attachment)
    else:
        body, ctype = json.dumps(payload).encode(), "application/json"
    for _ in range(3):
        req = urllib.request.Request(cfg["webhook_url"], data=body, method="POST", headers={
            "Content-Type": ctype, "User-Agent": UA})
        try:
            urllib.request.urlopen(req, timeout=10).close()
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limited: Discord says how long to wait
                time.sleep(float(json.loads(e.read() or b"{}").get("retry_after", 2)))
                continue
            log(f"Discord said HTTP {e.code}: {e.read()[:300]!r}")
            return False
        except OSError as e:
            log(f"couldn't reach Discord: {e}")
            time.sleep(3)
    return False


def embed(style, title, url, description, fields, author, thumb=None, image=None):
    """thumb: picture top-right (creature render), image: big picture at the bottom."""
    color, icon, emoji, _ = STYLES[style]
    e = {
        "author": {"name": author, "icon_url": ICON.format(icon)},
        "title": f"{emoji} {title}"[:256],
        "description": description,
        "color": color,
        "thumbnail": {"url": thumb or ICON.format(icon)},
        "fields": [{"name": k, "value": v, "inline": True} for k, v in fields if v],
        "footer": {"text": "WoW Forever · First Kills"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if url:
        e["url"] = url
    if image:
        e["image"] = {"url": image}
    return {"embeds": [e]}


def milestone(n):
    return f"\n\n🎉 **Milestone: {n} first kills!**" if n in MILESTONES or n % 500 == 0 else ""


def short(name):
    return name.split("-", 1)[0]  # "Name-Realm" -> "Name"


def realm(name):
    return name.split("-", 1)[1] if "-" in name else ""


# ---------------------------------------------------------------- Wowhead

def npc_info(cfg, npc_id):
    """Level/type line and rank for an NPC from Wowhead's tooltip API, or {}."""
    if not npc_id or not cfg["wowhead_env"]:
        return {}
    url = (f"https://nether.wowhead.com/tooltip/npc/{npc_id}"
           f"?dataEnv={urllib.parse.quote(str(cfg['wowhead_env']))}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.load(r)
    except (OSError, ValueError):
        return {}
    tooltip, name = data.get("tooltip", ""), data.get("name", "")
    info = {}
    img = re.search(r'<img src="([^"]+)"', tooltip)  # boss portrait from the dungeon journal
    if img:
        info["image"] = img.group(1)
    # Rows look like: name, [<Subtitle>], "[Level 5 - 30] Beast (Normal)", [family]
    for cell in re.findall(r"<td>(.*?)</td>", tooltip, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", cell)).strip()
        if not text or text == name:
            continue
        m = re.match(r"(.*?)\s*\(([^)]+)\)\s*$", text)
        if m:
            info["type"] = m.group(1).replace(" - ", "–")
            info["rank"] = m.group(2).lower()
            break
        info["subtitle"] = text
    if img and info.get("rank") in ("elite", "rare elite"):
        info["rank"] = "boss"  # only encounter bosses have a journal portrait
    return info


def http(url, method="GET", timeout=8):
    # Wowhead's CDN rejects most browser-like user agents from scripts but accepts this one.
    req = urllib.request.Request(url, method=method, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.headers.get("Content-Type", ""), r.read() if method == "GET" else b""


def npc_render(npc_id):
    """URL of a 3D-model render of the NPC, or None.

    Wowhead's renders are keyed by display ID, which only the NPC's page tells us.
    Try the Forever page, then classic, then retail, and make sure the render exists.
    """
    if not npc_id:
        return None
    for page, thumb_envs in (("forever/", ("classic", "live")),
                             ("classic/", ("classic", "live")),
                             ("", ("live",))):
        try:
            _, body = http(f"https://www.wowhead.com/{page}npc={npc_id}")
        except (OSError, ValueError):
            continue
        m = re.search(rb"displayId(?:&quot;:|\s*=\s*)(\d+)", body)
        if not m:
            continue
        display = int(m.group(1))
        for env in thumb_envs:
            url = RENDER.format(env=env, bucket=display & 0xFF, display=display)
            try:
                if http(url, method="HEAD")[0].startswith("image/"):
                    return url
            except (OSError, ValueError):
                pass
    return None


def npc_link(cfg, npc_id, name):
    if npc_id and cfg["npc_url"]:
        return cfg["npc_url"].format(id=npc_id)
    if cfg["search_url"]:
        return cfg["search_url"].format(query=urllib.parse.quote(name))
    return None


# ---------------------------------------------------------------- messages

def mob_message(cfg, me, mob, npc_id, killer, zone, n, in_encounter):
    info = npc_info(cfg, npc_id)
    rank = "boss" if in_encounter else info.get("rank", "normal")
    if rank not in STYLES:
        rank = "boss" if "boss" in rank else "normal"
    title = f"{mob} <{info['subtitle']}>" if info.get("subtitle") else mob
    desc = f"**{short(me)}** slew **{mob}** for the first time!"
    if killer != me:
        desc += f"\n-# Killing blow by {short(killer)}"
    return embed(rank, title, npc_link(cfg, npc_id, mob), desc + milestone(n),
                 [("Zone", zone), ("Type", info.get("type")), ("Rank", STYLES[rank][3])],
                 f"{short(me)} · First kill #{n}",
                 thumb=npc_render(npc_id), image=info.get("image"))


def encounter_message(cfg, me, encounter, npc_id, zone, n):
    """npc_id: the last creature killed during the encounter, used for its pictures."""
    info = npc_info(cfg, npc_id)
    desc = f"**{short(me)}** and the group defeated **{encounter}** for the first time!"
    return embed("encounter", f"BOSS DOWN: {encounter}", npc_link(cfg, None, encounter),
                 desc + milestone(n), [("Zone", zone)], f"{short(me)} · First kill #{n}",
                 thumb=npc_render(npc_id), image=info.get("image"))


def pvp_message(cfg, me, victim, killer, zone, n):
    url = cfg["player_url"].format(name=urllib.parse.quote(short(victim)),
                                   realm=urllib.parse.quote(realm(victim))) if cfg["player_url"] else None
    desc = f"**{short(me)}** took down **{short(victim)}** for the first time!"
    if killer != me:
        desc += f"\n-# Killing blow by {short(killer)}"
    return embed("pvp", short(victim), url, desc,
                 [("Realm", realm(victim)), ("Zone", zone)],
                 f"{short(me)} · Enemy player #{n}")


# ---------------------------------------------------------------- combat log

def npc_id_of(guid):
    parts = guid.split("-")  # Creature-0-server-instance-zone-npcID-spawn
    return parts[5] if len(parts) > 5 else None


def flags(s):
    try:
        return int(s, 16)
    except ValueError:
        return 0


class Tracker:
    def __init__(self, cfg, state, dry_run):
        self.cfg, self.state, self.dry_run = cfg, state, dry_run
        self.me = None          # "Name-Realm" of the character writing this log
        self.zone = ""
        self.encounter = None   # name of the boss encounter in progress
        self.encounter_npc = None  # last creature killed during it

    def handle(self, line):
        _, sep, payload = line.partition("  ")
        if not sep:
            return
        try:
            f = next(csv.reader([payload]))
        except (csv.Error, StopIteration):
            return
        event = f[0]
        if event == "ZONE_CHANGE" and len(f) >= 3:
            self.zone = f[2]
            return
        if event == "ENCOUNTER_START" and len(f) >= 3:
            self.encounter, self.encounter_npc = f[2], None
            return
        if event == "ENCOUNTER_END" and len(f) >= 6:
            self.encounter = None
            if f[5] == "1" and self.me:
                self.encounter_won(f[2])
            return
        if len(f) < 9:
            return
        src_guid, src_name, src_flags = f[1], f[2], flags(f[3])
        if (src_guid.startswith("Player-") and src_flags & AFFIL_MINE
                and src_flags & TYPE_PLAYER and src_name != "nil"):
            self.me = src_name
        if event != "PARTY_KILL":
            return
        if not src_flags & (AFFIL_MINE | AFFIL_PARTY | AFFIL_RAID) or not self.me:
            return
        dst_guid, dst_name, dst_flags = f[5], f[6], flags(f[7])
        if dst_name in ("", "nil") or dst_name.lower() in self.cfg["ignore"]:
            return
        if dst_guid.startswith(NPC_PREFIXES):
            if self.encounter:
                self.encounter_npc = npc_id_of(dst_guid)
            self.mob_killed(dst_name, dst_guid, src_name)
        elif dst_guid.startswith("Player-") and dst_flags & REACTION_HOSTILE:
            self.player_killed(dst_name, src_name)

    def kills(self):
        return self.state.setdefault(self.me, {})

    def count(self, pvp=False):
        return sum(1 for k in self.kills() if k.startswith(PSEP) == pvp)

    def record(self, key, **extra):
        self.kills()[key] = {"t": int(time.time()), "zone": self.zone, **extra}
        save_state(self.state)

    def mob_killed(self, mob, guid, killer):
        if mob in self.kills():
            return
        npc_id = npc_id_of(guid)
        n = self.count() + 1
        self.record(mob, n=n, npc_id=npc_id)
        post(self.cfg, mob_message(self.cfg, self.me, mob, npc_id, killer, self.zone, n,
                                   self.encounter is not None), self.dry_run)

    def encounter_won(self, encounter):
        if encounter in self.kills():  # boss itself was already posted via PARTY_KILL
            return
        n = self.count() + 1
        self.record(encounter, n=n, encounter=True)
        post(self.cfg, encounter_message(self.cfg, self.me, encounter, self.encounter_npc,
                                         self.zone, n), self.dry_run)

    def player_killed(self, victim, killer):
        key = PSEP + victim
        if key in self.kills():
            return
        n = self.count(pvp=True) + 1
        self.record(key, n=n)
        post(self.cfg, pvp_message(self.cfg, self.me, victim, killer, self.zone, n), self.dry_run)


def newest_log(logs_dir):
    files = list(logs_dir.glob("WoWCombatLog*.txt"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


_lock_handle = None


def acquire_lock():
    """Only one watcher may run, or everything would be posted twice."""
    global _lock_handle
    if _lock_handle:
        return True
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    fh = open(LOCK_PATH, "a+")
    try:
        if IS_WIN:
            import msvcrt
            fh.seek(0)
            msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        fh.close()
        return False
    _lock_handle = fh
    return True


def release_lock():
    global _lock_handle
    if _lock_handle:
        _lock_handle.close()
        _lock_handle = None


def watch(cfg, dry_run):
    if not dry_run and not acquire_lock():
        log("FirstKills is already running (in the background or another window)")
        return False
    STOP_PATH.unlink(missing_ok=True)
    tracker = Tracker(cfg, load_state(), dry_run)
    reports = progress.Progress(cfg, post, lambda: tracker.state, REPORTS_PATH, dry_run)
    current, fh, buf = None, None, b""
    log(f"watching {cfg['logs_dir']} and {cfg['wtf_dir']}")
    # A log that already exists at startup is old news: skip its contents.
    # Any log that appears later is a new session: read it from the start.
    old_log = newest_log(cfg["logs_dir"])
    while True:
        if STOP_PATH.exists():
            STOP_PATH.unlink(missing_ok=True)
            log("stopped")
            return True
        reports.check()
        latest = newest_log(cfg["logs_dir"])
        if latest and latest != current:
            if fh:
                fh.close()
            fh = open(latest, "rb")
            if latest == old_log and current is None:
                fh.seek(0, os.SEEK_END)
            current, buf = latest, b""
            tracker.me, tracker.encounter = None, None
            log(f"following {latest.name}")
        if fh:
            if os.path.getsize(current) < fh.tell():  # file was truncated
                fh.seek(0)
                buf = b""
            chunk = fh.read()
            if chunk:
                buf += chunk
                *lines, buf = buf.split(b"\n")
                for raw in lines:
                    tracker.handle(raw.decode("utf-8", "replace").rstrip("\r"))
                continue
        time.sleep(cfg["poll_seconds"])


# ---------------------------------------------------------------- setup (mainly Windows)

WEBHOOK_RE = re.compile(r"^https://(?:(?:ptb|canary)\.)?discord(?:app)?\.com/api/webhooks/\d+/[\w-]+$")


def ask(prompt, default=""):
    try:
        answer = input(prompt).strip().strip('"')
    except EOFError:
        return default
    return answer or default


def addon_source():
    """The addon folder shipped next to the watcher (bundle) or the project folder itself."""
    for d in (SCRIPT.parent.parent / "FirstKills", SCRIPT.parent.parent):
        if (d / "FirstKills.toc").exists():
            return d
    return None


def install_addon(game):
    src = addon_source()
    dest = game / "Interface" / "AddOns" / "FirstKills"
    if not src:
        print("  ! addon files not found next to the watcher; copy the FirstKills folder by hand")
        return
    if dest.resolve() == src.resolve():
        print(f"  ✓ addon already linked: {dest}")
        return
    try:
        dest.mkdir(parents=True, exist_ok=True)
        for name in ("FirstKills.toc", "FirstKills.lua"):
            (dest / name).write_bytes((src / name).read_bytes())
        print(f"  ✓ addon installed in {dest}")
    except OSError as e:
        print(f"  ! couldn't install the addon ({e}).\n"
              f"    Copy the FirstKills folder into {dest.parent} yourself.")


def setup(cfg_dry_run=False):
    print("\n=== FirstKills setup ===\n")
    if IS_WIN and "\\AppData\\Local\\Temp\\" in str(SCRIPT):
        print("It looks like this is running from inside the zip file.\n"
              "Right-click the zip -> Extract All, put the folder somewhere permanent\n"
              "(e.g. Documents), and start it from there.")
        return False
    raw = read_raw_config()

    # 1. the game
    game = Path(raw["logs_dir"]).expanduser().parent if raw.get("logs_dir") else find_game_dir()
    while not game or not is_game_dir(game):
        p = ask("Couldn't find WoW Forever. Paste the path to your 'World of Warcraft' folder: ")
        if not p:
            return False
        p = Path(p)
        game = p if p.name == "_forever_" else p / "_forever_"
        if not is_game_dir(game):
            print(f"  ! no WoW Forever install in {game}")
            game = None
    print(f"  ✓ game found: {game}")
    raw["logs_dir"] = str(game / "Logs")
    install_addon(game)

    # 2. the webhook
    current = raw.get("webhook_url", "")
    print("\nDiscord webhook: in Discord open the channel's settings -> Integrations ->\n"
          "Webhooks -> New Webhook -> Copy Webhook URL. Paste it here (right-click or Ctrl+V).")
    while True:
        hint = " (Enter keeps the current one)" if current else ""
        url = ask(f"Webhook URL{hint}: ", current)
        if WEBHOOK_RE.match(url):
            break
        print("  ! that doesn't look like a Discord webhook URL (https://discord.com/api/webhooks/...)")
    raw["webhook_url"] = url
    save_raw_config(raw)
    print(f"  ✓ saved to {CONFIG_PATH}")

    cfg = load_config()
    ok = post(cfg, {"embeds": [{
        "title": "✅ FirstKills is connected",
        "description": "First kills, level milestones and progress reports will show up here.",
        "color": 0x2ECC71}]}, cfg_dry_run)
    print("  ✓ test message sent, check Discord" if ok else "  ! sending the test message failed")

    # 3. autostart
    if IS_WIN:
        yes = ask("\nStart FirstKills automatically when Windows starts? [Y/n]: ", "y").lower()
        set_autostart(not yes.startswith("n"))
    print("\nSetup done. In game, type /fk to check that combat logging is ON.\n")
    return True


def startup_dir():
    return (Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu"
            / "Programs" / "Startup")


def autostart_enabled():
    return any((startup_dir() / n).exists() for n in ("FirstKills.lnk", "FirstKills.bat"))


def pythonw():
    exe = Path(sys.executable)
    w = exe.with_name("pythonw.exe")
    return w if w.exists() else exe


def set_autostart(on):
    if not IS_WIN:
        print("On Linux use: systemctl --user enable --now wow-firstkills")
        return
    lnk, bat = startup_dir() / "FirstKills.lnk", startup_dir() / "FirstKills.bat"
    if not on:
        lnk.unlink(missing_ok=True)
        bat.unlink(missing_ok=True)
        print("  ✓ autostart off")
        return
    startup_dir().mkdir(parents=True, exist_ok=True)
    q = lambda p: str(p).replace("'", "''")  # PowerShell single-quoted string
    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{q(lnk)}');"
          f"$s.TargetPath='{q(pythonw())}';$s.Arguments='\"{q(SCRIPT)}\" --background';"
          f"$s.WorkingDirectory='{q(SCRIPT.parent)}';$s.Description='FirstKills Discord poster';$s.Save()")
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                           capture_output=True, text=True, timeout=60)
        err = r.stderr.strip()[:200]
    except (OSError, subprocess.SubprocessError) as e:
        err = str(e)
    if lnk.exists():
        bat.unlink(missing_ok=True)
        print("  ✓ FirstKills will start with Windows (no window, runs in the background)")
        return
    # Fallback without PowerShell: a tiny batch file (flashes a window briefly at login).
    try:
        bat.write_text(f'@start "" "{pythonw()}" "{SCRIPT}" --background\r\n', encoding="utf-8")
        print("  ✓ FirstKills will start with Windows (runs in the background)")
    except OSError as e:
        print(f"  ! couldn't set up autostart: {err or e}\n"
              "    You can start it yourself with 'Start FirstKills.bat' before playing.")


def start_background():
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([str(pythonw()), str(SCRIPT), "--background"], cwd=str(SCRIPT.parent),
                     creationflags=flags if IS_WIN else 0, close_fds=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop():
    if acquire_lock():
        print("FirstKills isn't running.")
        return
    STOP_PATH.parent.mkdir(parents=True, exist_ok=True)
    STOP_PATH.touch()
    for _ in range(20):
        time.sleep(0.5)
        if not STOP_PATH.exists():
            print("FirstKills stopped.")
            return
    print("FirstKills didn't respond; end 'pythonw.exe' in Task Manager.")


def main():
    if sys.stdout is None or "--background" in sys.argv:  # no console: log to a file
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 1_000_000:
            LOG_PATH.unlink()
        sys.stdout = sys.stderr = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    cmd = args[0] if args and not args[0].startswith("--") else ""

    if cmd == "setup":
        return 0 if setup(dry_run) else 1
    if cmd == "stop":
        stop()
        return 0
    if cmd == "autostart":
        set_autostart(args[1:2] != ["off"])
        return 0
    if cmd == "start":
        if not read_raw_config().get("webhook_url") and not setup(dry_run):
            return 1
        if not dry_run and not acquire_lock():
            print("FirstKills is already running in the background. You can close this window.\n"
                  "To stop it, run 'Stop FirstKills.bat'.")
            return 0
        if IS_WIN and autostart_enabled():
            # Autostart is on but nothing runs yet (e.g. right after setup): start it hidden.
            release_lock()
            start_background()
            time.sleep(2)
            print("FirstKills is running in the background. You can close this window.\n"
                  "To stop it, run 'Stop FirstKills.bat'.")
            return 0
        print("Watching... leave this window open while you play (close it to stop).\n")

    cfg = load_config()
    if cmd == "test":
        me = "Testchar-Realm"
        samples = [
            mob_message(cfg, me, "Young Wolf", "299", me, "Elwynn Forest", 1, False),
            mob_message(cfg, me, "Hogger", "448", "Buddy-Realm", "Elwynn Forest", 25, False),
            mob_message(cfg, me, "Thuros Lightfingers", "61", me, "Elwynn Forest", 26, False),
            mob_message(cfg, me, "Edwin VanCleef", "639", me, "The Deadmines", 27, True),
            mob_message(cfg, me, "Onyxia", "10184", me, "Onyxia's Lair", 28, True),
            encounter_message(cfg, me, "The Seven", "9037", "Blackrock Depths", 29),
            pvp_message(cfg, me, "Enemyguy-Realm", me, "Hillsbrad Foothills", 1),
            *progress.sample_messages(cfg),
        ]
        ok = all([post(cfg, s, dry_run) for s in samples])
        log("posted test messages" if ok else "failed")
        return 0 if ok else 1
    if cmd == "list":
        for char, kills in load_state().items():
            mobs = {k: v for k, v in kills.items() if not k.startswith(PSEP)}
            pvp = {k[len(PSEP):]: v for k, v in kills.items() if k.startswith(PSEP)}
            print(f"{char}: {len(mobs)} first kills, {len(pvp)} enemy players")
            for name, k in sorted(mobs.items(), key=lambda kv: -kv[1]["n"])[:20]:
                print(f"  #{k['n']:<4} {name}  ({k.get('zone') or '?'})")
            for name, k in sorted(pvp.items(), key=lambda kv: -kv[1]["n"])[:10]:
                print(f"  PvP #{k['n']:<3} {name}  ({k.get('zone') or '?'})")
        return 0
    try:
        watch(cfg, dry_run)
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
