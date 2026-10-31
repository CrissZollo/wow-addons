"""Progress reports and level milestones, built from the Herald addon's saved data.

The addon writes HeraldDB to WTF/Account/<account>/SavedVariables/Herald.lua
when you log out or /reload. Each time that file changes we:
  - post a card for every new milestone level (with the level-up screenshot attached),
  - post a progress report comparing the last report with now, if you've played at
    least `min_report_minutes` since the last report.
"""
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

ICON = "https://wow.zamimg.com/images/wow/icons/large/{}.jpg"
GOLD = 0xFFD100
CLASS_COLORS = {
    "WARRIOR": 0xC69B6D, "PALADIN": 0xF48CBA, "HUNTER": 0xAAD372, "ROGUE": 0xFFF468,
    "PRIEST": 0xFFFFFF, "SHAMAN": 0x0070DD, "MAGE": 0x3FC7EB, "WARLOCK": 0x8788EE,
    "DRUID": 0xFF7C0A, "DEATHKNIGHT": 0xC41E3A, "MONK": 0x00FF98, "DEMONHUNTER": 0xA330C9,
    "EVOKER": 0x33937F,
}
CLASS_NAMES = {"DEATHKNIGHT": "Death Knight", "DEMONHUNTER": "Demon Hunter"}
RACE_NAMES = {"Scourge": "Undead", "NightElf": "Night Elf", "BloodElf": "Blood Elf",
              "HighmountainTauren": "Highmountain Tauren", "LightforgedDraenei": "Lightforged Draenei",
              "VoidElf": "Void Elf", "DarkIronDwarf": "Dark Iron Dwarf", "MagharOrc": "Mag'har Orc",
              "KulTiran": "Kul Tiran", "ZandalariTroll": "Zandalari Troll"}
QUALITY = {0: "⬛", 1: "⬜", 2: "🟩", 3: "🟦", 4: "🟪", 5: "🟧", 6: "🟨", 7: "🟨"}
SLOTS = [
    ("HeadSlot", "Head"), ("NeckSlot", "Neck"), ("ShoulderSlot", "Shoulders"),
    ("BackSlot", "Back"), ("ChestSlot", "Chest"), ("WristSlot", "Wrists"),
    ("HandsSlot", "Hands"), ("WaistSlot", "Waist"), ("LegsSlot", "Legs"),
    ("FeetSlot", "Feet"), ("Finger0Slot", "Ring"), ("Finger1Slot", "Ring"),
    ("Trinket0Slot", "Trinket"), ("Trinket1Slot", "Trinket"),
    ("MainHandSlot", "Main hand"), ("SecondaryHandSlot", "Off hand"), ("RangedSlot", "Ranged"),
]
# key, label, is_percentage
STATS = [
    ("str", "Strength", False), ("agi", "Agility", False), ("sta", "Stamina", False),
    ("int", "Intellect", False), ("spi", "Spirit", False), ("armor", "Armor", False),
    ("ap", "Attack Power", False), ("crit", "Melee crit", True),
    ("spellcrit", "Spell crit", True), ("dodge", "Dodge", True),
]


# ---------------------------------------------------------------- SavedVariables parser

_TOKEN = re.compile(r"""\s*(?:
      (?P<comment>--\[\[.*?\]\]|--[^\n]*)
    | (?P<str>"(?:\\.|[^"\\])*")
    | (?P<num>-?(?:0[xX][0-9a-fA-F]+|(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?))
    | (?P<name>[A-Za-z_]\w*)
    | (?P<op>\S))""", re.S | re.X)
_ESC = {"n": 10, "t": 9, "r": 13, "a": 7, "b": 8, "f": 12, "v": 11, "\n": 10}


def _lua_string(tok):
    s, out, i = tok[1:-1], bytearray(), 0
    while i < len(s):
        if s[i] == "\\" and i + 1 < len(s):
            digits = re.match(r"\d{1,3}", s[i + 1:])
            if digits:
                out.append(int(digits.group()) & 0xFF)
                i += 1 + len(digits.group())
            else:
                out.append(_ESC.get(s[i + 1], ord(s[i + 1]) & 0xFF))
                i += 2
        else:
            out.append(ord(s[i]) & 0xFF)
            i += 1
    return out.decode("utf-8", "replace")


def parse_saved_variables(data: bytes) -> dict:
    """Parse a WoW SavedVariables file ("Name = <lua value>" lines) into Python values."""
    text = data.decode("latin-1")  # keep bytes 1:1; strings are re-decoded as UTF-8
    toks = [(m.lastgroup, m.group(m.lastgroup)) for m in _TOKEN.finditer(text)
            if m.lastgroup and m.lastgroup != "comment"]
    pos = 0

    def take(expect=None):
        nonlocal pos
        kind, val = toks[pos]
        if expect and val != expect:
            raise ValueError(f"expected {expect!r}, got {val!r}")
        pos += 1
        return kind, val

    def value():
        kind, val = take()
        if kind == "str":
            return _lua_string(val)
        if kind == "num":
            return int(val, 16) if val.lower().startswith(("0x", "-0x")) else (
                float(val) if any(c in val for c in ".eE") else int(val))
        if kind == "name":
            return {"true": True, "false": False, "nil": None}.get(val, val)
        if val == "{":
            return table()
        raise ValueError(f"unexpected {val!r}")

    def table():
        arr, d = [], {}
        while toks[pos][1] != "}":
            if toks[pos][1] == "[":
                take("[")
                key = value()
                take("]")
                take("=")
                d[key] = value()
            elif toks[pos][0] == "name" and toks[pos + 1][1] == "=":
                key = take()[1]
                take("=")
                d[key] = value()
            else:
                arr.append(value())
            if toks[pos][1] in (",", ";"):
                take()
        take("}")
        for i, v in enumerate(arr, 1):
            d[i] = v
        if d and all(isinstance(k, int) for k in d) and sorted(d) == list(range(1, len(d) + 1)):
            return [d[k] for k in sorted(d)]
        return d

    result = {}
    while pos < len(toks):
        name = take()[1]
        take("=")
        result[name] = value()
    return result


# ---------------------------------------------------------------- formatting

def money(copper):
    copper = int(copper or 0)
    sign, copper = ("-" if copper < 0 else ""), abs(copper)
    g, s, c = copper // 10000, copper // 100 % 100, copper % 100
    parts = [f"{g}g"] * bool(g) + [f"{s}s"] * bool(s) + [f"{c}c"] * bool(c or not (g or s))
    return sign + " ".join(parts)


def duration(sec):
    sec = int(sec)
    h, m = sec // 3600, sec // 60 % 60
    return f"{h}h {m}m" if h else f"{m}m"


def xp_bar(xp, xp_max, width=12):
    if not xp_max:
        return ""
    frac = max(0.0, min(1.0, xp / xp_max))
    filled = round(frac * width)
    return "▰" * filled + "▱" * (width - filled) + f" {frac:.0%}"


def nice_class(cls):
    return CLASS_NAMES.get(cls, (cls or "").capitalize())


def nice_race(race):
    return RACE_NAMES.get(race, race or "")


def race_icon(race, sex):
    return ICON.format(f"race_{(race or 'human').lower()}_{'female' if sex == 3 else 'male'}")


def class_icon(cls):
    return ICON.format(f"classicon_{(cls or 'warrior').lower()}")


def avg_ilvl(snap):
    levels = [g.get("ilvl") for g in (snap.get("gear") or {}).values() if g.get("ilvl")]
    return sum(levels) / len(levels) if levels else None


def change(before, after, pct=False):
    """'45 → **52** ▲7' style text; just the value when nothing changed."""
    fmt = (lambda v: f"{v:.2f}%") if pct else (lambda v: f"{round(v):,}")
    if after is None:
        return None
    if before is None or abs(after - before) < (0.005 if pct else 0.5):
        return fmt(after)
    delta = after - before
    arrow = "▲" if delta > 0 else "▼"
    d = f"{abs(delta):.2f}" if pct else f"{abs(round(delta)):,}"
    return f"{fmt(before)} → **{fmt(after)}** {arrow}{d}"


def fit(lines, limit=1024):
    out = ""
    for line in lines:
        if len(out) + len(line) + 1 > limit - 4:
            return out + "\n…"
        out += ("\n" if out else "") + line
    return out or "—"


# ---------------------------------------------------------------- messages

def milestone_message(info, m, prev_m, screenshot_name=None):
    who = info.get("name", "?")
    lvl = m["level"]
    desc = f"**{who}** reached **level {lvl}**!"
    if m.get("zone"):
        desc += f"\n📍 {m['zone']}"
    if prev_m:
        desc += f"\n⏳ {duration(m['t'] - prev_m['t'])} since level {prev_m['level']}"
    e = {
        "author": {"name": f"{who} · {nice_race(info.get('race'))} {nice_class(info.get('class'))}",
                   "icon_url": race_icon(info.get("race"), info.get("sex"))},
        "title": f"🎖️ LEVEL {lvl}!",
        "description": desc,
        "color": GOLD,
        "thumbnail": {"url": ICON.format(f"achievement_level_{lvl}")},
        "footer": {"text": "WoW Forever · Milestone"},
        "timestamp": datetime.fromtimestamp(m["t"], timezone.utc).isoformat(),
    }
    if screenshot_name:
        e["image"] = {"url": f"attachment://{screenshot_name}"}
    return {"embeds": [e]}


def report_message(cfg, info, before, after, played, new_kills):
    who, cls = info.get("name", "?"), info.get("class")
    color = CLASS_COLORS.get(cls, GOLD)
    b_lvl, a_lvl = before.get("level"), after.get("level")

    # --- header
    lines = []
    if b_lvl is not None and a_lvl and a_lvl > b_lvl:
        lines.append(f"## Level {b_lvl} → {a_lvl}  (+{a_lvl - b_lvl}) 🎉")
    else:
        lines.append(f"## Level {a_lvl}")
    bar = xp_bar(after.get("xp") or 0, after.get("xpMax"))
    if bar:
        lines.append(f"`{bar}` to level {(a_lvl or 0) + 1}")
    if after.get("money") is not None:
        delta = (after["money"] or 0) - (before.get("money") or 0)
        sign = "+" if delta >= 0 else ""
        lines.append(f"💰 **{money(after['money'])}**" + (f"  ({sign}{money(delta)})" if delta else ""))
    lines.append(f"⏱️ {duration(played)} played since the last report")
    if after.get("zone"):
        lines.append(f"📍 {after['zone']}")
    if new_kills:
        names = ", ".join(new_kills[:6]) + (f" +{len(new_kills) - 6} more" if len(new_kills) > 6 else "")
        lines.append(f"⚔️ **{len(new_kills)}** new first kills: {names}")
    header = {
        "author": {"name": f"{who} · Level {a_lvl} {nice_race(info.get('race'))} {nice_class(cls)}",
                   "icon_url": race_icon(info.get("race"), info.get("sex"))},
        "title": "📈 Progress report",
        "description": "\n".join(lines),
        "color": color,
        "thumbnail": {"url": class_icon(cls)},
    }

    # --- stats
    bs, as_ = before.get("stats") or {}, after.get("stats") or {}
    fields = []
    hp = change(before.get("health"), after.get("health"))
    if hp:
        fields.append({"name": "❤️ Health", "value": hp, "inline": True})
    pw = change(before.get("power"), after.get("power"))
    if pw:
        ptype = (after.get("powerType") or "Power").replace("_", " ").title()
        fields.append({"name": f"🔷 {ptype}", "value": pw, "inline": True})
    for key, label, pct in STATS:
        v = change(bs.get(key), as_.get(key), pct)
        if v and not (pct and as_.get(key) == 0):
            fields.append({"name": label, "value": v, "inline": True})
    stats = {"title": "📊 Stats", "color": color, "fields": fields[:24]}

    # --- gear
    bg, ag = before.get("gear") or {}, after.get("gear") or {}
    url = cfg.get("item_url") or ""

    def item(g):
        name = g.get("name") or f"item {g.get('id')}"
        link = f"[{name}]({url.format(id=g['id'])})" if url and g.get("id") else name
        return f"{QUALITY.get(g.get('q'), '⬜')} {link}"

    upgrades, gear_lines = [], []
    for slot, label in SLOTS:
        a, b = ag.get(slot), bg.get(slot)
        if not a:
            continue
        new = not b or b.get("id") != a.get("id")
        ilvl = f" ({a['ilvl']})" if a.get("ilvl") else ""
        gear_lines.append(f"**{label}:** {item(a)}{ilvl}" + (" 🆕" if new and bg else ""))
        if new and bg:
            old = f"~~{b.get('name')}~~ → " if b else ""
            upgrades.append(f"**{label}:** {old}{item(a)}{ilvl}")
    b_il, a_il = avg_ilvl(before), avg_ilvl(after)
    title = "🛡️ Equipment"
    if a_il:
        title += f" · item level {a_il:.1f}"
        if b_il and abs(a_il - b_il) >= 0.05:
            title += f" ({'▲' if a_il > b_il else '▼'}{abs(a_il - b_il):.1f})"
    gfields = []
    if upgrades:
        gfields.append({"name": "🆕 New gear", "value": fit(upgrades), "inline": False})
    half = (len(gear_lines) + 1) // 2
    gfields.append({"name": "Equipped", "value": fit(gear_lines[:half]), "inline": True})
    if gear_lines[half:]:
        gfields.append({"name": "​", "value": fit(gear_lines[half:]), "inline": True})
    gear = {"title": title, "color": color, "fields": gfields,
            "footer": {"text": "WoW Forever · Progress report"},
            "timestamp": datetime.fromtimestamp(after.get("t") or time.time(), timezone.utc).isoformat()}
    return {"embeds": [header, stats, gear]}


# ---------------------------------------------------------------- watcher

class Progress:
    def __init__(self, cfg, post, kills_state, state_path, dry_run=False):
        self.cfg, self.post, self.kills_state, self.dry_run = cfg, post, kills_state, dry_run
        self.state_path = state_path
        self.state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
        self.seen_mtime = {}
        self.next_check = 0.0

    def save(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, indent=1, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.state_path)

    def check(self):
        """Call often; looks at the SavedVariables files every few seconds."""
        if time.time() < self.next_check:
            return
        self.next_check = time.time() + 3
        for path in Path(self.cfg["wtf_dir"]).glob("Account/*/SavedVariables/Herald.lua"):
            try:
                mtime = path.stat().st_mtime
            except OSError:
                continue
            if self.seen_mtime.get(path) == mtime or time.time() - mtime < 2:
                continue  # unchanged, or WoW may still be writing it
            try:
                db = parse_saved_variables(path.read_bytes()).get("HeraldDB") or {}
            except (ValueError, IndexError) as e:
                print(f"[herald] couldn't read {path.name}: {e}", flush=True)
                continue
            self.seen_mtime[path] = mtime
            for key, char in (db.get("chars") or {}).items():
                if isinstance(char, dict):
                    self.handle(key, char)

    def handle(self, key, char):
        info = char.get("info") or {}
        rep = self.state.setdefault(key, {"milestones": []})

        milestones = sorted(char.get("milestones") or [], key=lambda m: m["t"])
        for i, m in enumerate(milestones):
            if m["t"] in rep["milestones"]:
                continue
            shot = self.find_screenshot(m["t"])
            payload = milestone_message(info, m, milestones[i - 1] if i else None,
                                        shot.name if shot else None)
            self.post(self.cfg, payload, self.dry_run, attachment=shot)
            rep["milestones"].append(m["t"])
            self.save()

        last = char.get("last")
        if not last or rep.get("seen") == last.get("t"):
            return
        baseline = rep.get("baseline") or char.get("start")
        since = max(last.get("sessionStart") or last["t"], (baseline or {}).get("t") or 0)
        played = last["t"] - since
        if baseline and played >= self.cfg["min_report_minutes"] * 60:
            payload = report_message(self.cfg, info, baseline, last, played,
                                     self.new_kills(info, since, last["t"]))
            self.post(self.cfg, payload, self.dry_run)
            rep["baseline"] = last
        elif not baseline:
            rep["baseline"] = last
        rep["seen"] = last["t"]
        self.save()

    def new_kills(self, info, start, end):
        name = info.get("name")
        realm = (info.get("realm") or "").replace(" ", "")
        out = []
        for char, kills in self.kills_state().items():
            parts = char.split("-")
            if parts[0] != name or (realm and len(parts) > 1 and parts[1] != realm):
                continue
            out += [(k["t"], mob) for mob, k in kills.items()
                    if not mob.startswith("pvp:") and start <= k.get("t", 0) <= end]
        return [mob for _, mob in sorted(out)]

    def find_screenshot(self, t):
        best = None
        for p in Path(self.cfg["screenshots_dir"]).glob("WoWScrnShot_*"):
            if p.suffix.lower() not in (".jpg", ".jpeg", ".png"):
                continue
            st = p.stat()
            dt = st.st_mtime - t
            if -2 <= dt <= 30 and st.st_size < 10_000_000 and (best is None or dt < best[0]):
                best = (dt, p)
        return best[1] if best else None


# ---------------------------------------------------------------- sample data for `test`

def sample_messages(cfg):
    info = {"name": "Testchar", "realm": "Realm", "class": "WARRIOR", "race": "Human", "sex": 2}
    now = int(time.time())
    gear_before = {
        "HeadSlot": {"id": 7413, "name": "Dutch's Hat", "q": 1, "ilvl": 8},
        "ChestSlot": {"id": 6125, "name": "Brawler's Harness", "q": 1, "ilvl": 1},
        "LegsSlot": {"id": 2385, "name": "Tarnished Chain Leggings", "q": 1, "ilvl": 10},
        "MainHandSlot": {"id": 2488, "name": "Gladius", "q": 1, "ilvl": 11},
    }
    gear_after = dict(gear_before, **{
        "ChestSlot": {"id": 6087, "name": "Chausses of Westfall", "q": 2, "ilvl": 20},
        "MainHandSlot": {"id": 1937, "name": "Buzz Saw", "q": 2, "ilvl": 20},
        "FeetSlot": {"id": 4831, "name": "Stalking Pants", "q": 2, "ilvl": 18},
    })
    before = {"t": now - 5400, "level": 12, "xp": 0, "xpMax": 5000, "money": 12050,
              "health": 410, "power": 100, "powerType": "RAGE", "gear": gear_before,
              "stats": {"str": 45, "agi": 30, "sta": 40, "int": 20, "spi": 25, "armor": 420,
                        "ap": 110, "crit": 5.2, "dodge": 4.1}}
    after = {"t": now, "level": 15, "xp": 2100, "xpMax": 5800, "money": 30520, "zone": "Westfall",
             "health": 560, "power": 100, "powerType": "RAGE", "gear": gear_after,
             "stats": {"str": 52, "agi": 34, "sta": 51, "int": 20, "spi": 27, "armor": 610,
                       "ap": 124, "crit": 5.9, "dodge": 4.4}}
    m10 = {"level": 10, "t": now - 9000, "zone": "Elwynn Forest"}
    m20 = {"level": 20, "t": now, "zone": "Westfall"}
    return [
        milestone_message(info, m20, m10),
        report_message(cfg, info, before, after, 5400,
                       ["Young Wolf", "Hogger", "Defias Pathstalker", "Harvest Golem"]),
    ]
