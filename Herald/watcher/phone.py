"""Phone page: a small web server on your home network that shows your characters.

Off by default. Turn it on with `herald.py phone on` (or "phone_port" in config.json),
then open http://<this PC's address>:<port> on a phone on the same Wi-Fi.

  /                      the page (phone.html): characters, stats, gear, guild, kills
  /widget                the same page as a compact card, for an Android web-widget app
  /api/characters.json   everything the page shows
  /api/widget.json       flat fields for widget apps like KWGT (?char=Name picks one)

The watcher's main loop builds the data (Phone.update) and the server threads only hand out
the latest copy, so they never touch the watcher's own state.
"""
import json
import socket
import struct
import threading
import time
import zlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import progress

HERE = Path(__file__).resolve().parent
LIVE_SECONDS = 300  # combat log written this recently = you're in game
DEFAULT_PORT = 8765


def lan_ip():
    """This PC's address on the home network (no packets are sent)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


def url(port):
    return f"http://{lan_ip()}:{port}"


# ---------------------------------------------------------------- data

def character(key, char, kills_state, cfg):
    info = char.get("info") or {}
    last = char.get("last") or {}
    gear = []
    for slot, label in progress.SLOTS:
        g = (last.get("gear") or {}).get(slot)
        if g:
            gear.append({"slot": slot, "label": label, "id": g.get("id"), "name": g.get("name"),
                         "q": g.get("q"), "ilvl": g.get("ilvl")})
    kills = progress.kills_of(info, kills_state)
    pve = sorted(((k, v) for k, v in kills if not k.startswith("pvp:")),
                 key=lambda kv: -kv[1].get("t", 0))
    pvp = [(k, v) for k, v in kills if k.startswith("pvp:")]
    recent = sorted(pve[:12] + sorted(pvp, key=lambda kv: -kv[1].get("t", 0))[:5],
                    key=lambda kv: -kv[1].get("t", 0))[:15]
    guild = char.get("guild")
    if isinstance(guild, dict):
        members = [m for m in guild.get("members") or [] if isinstance(m, dict)]
        guild = {k: guild.get(k) for k in ("t", "name", "rank", "motd", "total")}
        guild["members"] = members
        guild["onlineCount"] = sum(1 for m in members if m.get("online"))
    ilvl = progress.avg_ilvl(last)
    return {
        "key": key,
        "name": info.get("name") or key.split("-")[0],
        "realm": info.get("realm") or "",
        "class": info.get("class"),
        "className": progress.nice_class(info.get("class")),
        "race": progress.nice_race(info.get("race")),
        "color": "#%06X" % progress.CLASS_COLORS.get(info.get("class"), progress.GOLD),
        "classIcon": progress.class_icon(info.get("class")),
        "t": last.get("t"),
        "sessionStart": last.get("sessionStart") or char.get("sessionStart"),
        "level": last.get("level"),
        "xp": last.get("xp"),
        "xpMax": last.get("xpMax"),
        "rested": last.get("rested"),
        "money": last.get("money"),
        "zone": last.get("zone"),
        "health": last.get("health"),
        "power": last.get("power"),
        "powerType": (last.get("powerType") or "").replace("_", " ").title() or None,
        "stats": [{"key": k, "label": label, "value": (last.get("stats") or {}).get(k), "pct": pct}
                  for k, label, pct in progress.STATS
                  if (last.get("stats") or {}).get(k) not in (None, 0)],
        "ilvl": round(ilvl, 1) if ilvl else None,
        "gear": gear,
        "guild": guild or None,
        "milestones": sorted(char.get("milestones") or [], key=lambda m: -m.get("t", 0))[:10],
        "kills": [{"name": k[4:].split("-")[0] if k.startswith("pvp:") else k, "pvp": k.startswith("pvp:"),
                   "boss": bool(v.get("encounter")), "t": v.get("t"), "zone": v.get("zone"),
                   "n": v.get("n"), "npc": v.get("npc_id")} for k, v in recent],
        "killCount": len(pve),
        "pvpCount": len(pvp),
    }


def build(cfg, chars, kills_state, live):
    out = [character(key, c, kills_state, cfg) for key, c in chars.items() if c.get("last")]
    me, seen, zone = live
    playing = None
    if me and seen and time.time() - seen < LIVE_SECONDS:
        playing = {"name": me.split("-")[0], "zone": zone, "seen": seen}
    for c in out:
        c["playing"] = bool(playing and playing["name"] == c["name"])
    out.sort(key=lambda c: (not c["playing"], -(c["t"] or 0)))
    return {"updated": int(time.time()), "playing": playing,
            "itemUrl": cfg.get("item_url") or "", "npcUrl": cfg.get("npc_url") or "",
            "characters": out}


def money_text(copper):
    return progress.money(copper) if copper is not None else ""


def widget(data, name=None):
    chars = data["characters"]
    c = next((c for c in chars if name and c["name"].lower() == name.lower()), None)
    c = c or (chars[0] if chars else None)
    if not c:
        return {"name": "", "status": "No characters yet: log in with Herald on, then /reload"}
    xp_pct = round(100 * c["xp"] / c["xpMax"]) if c.get("xpMax") else None
    g = c.get("guild") or {}
    last_kill = c["kills"][0] if c["kills"] else {}
    if c["playing"]:
        status = f"In game · {data['playing'].get('zone') or c.get('zone') or ''}".rstrip(" ·")
    else:
        status = f"Offline · {c.get('zone') or ''}".rstrip(" ·")
    return {
        "name": c["name"], "class": c["className"], "race": c["race"], "color": c["color"],
        "level": c["level"], "xp_pct": xp_pct,
        "xp_text": f"{xp_pct}% to {(c['level'] or 0) + 1}" if xp_pct is not None else "",
        "gold": money_text(c.get("money")), "zone": c.get("zone") or "",
        "status": status, "playing": c["playing"], "ilvl": c.get("ilvl"),
        "guild": g.get("name") or "", "guild_rank": g.get("rank") or "",
        "guild_online": g.get("onlineCount"), "guild_motd": g.get("motd") or "",
        "first_kills": c["killCount"], "last_kill": last_kill.get("name") or "",
        "saved": c.get("t"),
        "saved_text": time.strftime("%H:%M", time.localtime(c["t"])) if c.get("t") else "",
    }


# ---------------------------------------------------------------- icon

def _png(size, pixel):
    rows = b"".join(b"\0" + b"".join(pixel(x, y) for x in range(size)) for y in range(size))

    def chunk(kind, data):
        return (struct.pack(">I", len(data)) + kind + data
                + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(rows, 9)) + chunk(b"IEND", b""))


def icon_png(size=192):
    """A gold shield on a dark background, drawn without any image library."""
    bg, gold, dark = b"\x14\x16\x1c", b"\xff\xd1\x00", b"\x2a\x22\x08"

    def inside(x, y, margin):
        # shield: flat top, straight sides, curving to a point at the bottom
        top, mid, bottom = 0.18 + margin, 0.5, 0.86 - margin
        half = 0.32 - margin
        if not (top <= y <= bottom):
            return False
        w = half if y <= mid else half * (1 - ((y - mid) / (bottom - mid)) ** 1.6)
        return abs(x - 0.5) <= w

    def pixel(px, py):
        x, y = (px + 0.5) / size, (py + 0.5) / size
        if inside(x, y, 0.06):
            return gold if abs(x - 0.5) < 0.035 or abs(y - 0.42) < 0.035 else dark
        return gold if inside(x, y, 0) else bg
    return _png(size, pixel)


MANIFEST = {
    "name": "Herald", "short_name": "Herald", "start_url": "/", "display": "standalone",
    "background_color": "#14161c", "theme_color": "#14161c",
    "icons": [{"src": "/icon.png", "sizes": "192x192", "type": "image/png"},
              {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png"}],
}


# ---------------------------------------------------------------- server

class Phone:
    def __init__(self, cfg, port, log):
        self.cfg, self.port, self.log = cfg, port, log
        self.data = build(cfg, {}, {}, (None, None, None))
        self.json = json.dumps(self.data).encode()
        self.next_update = 0.0
        self.icons = {}
        threading.Thread(target=self.serve, daemon=True).start()

    def update(self, chars, kills_state, live):
        """Call from the watcher's loop; rebuilds the data every few seconds."""
        if time.time() < self.next_update:
            return
        self.next_update = time.time() + 3
        try:
            data = build(self.cfg, chars, kills_state, live)
        except Exception as e:  # never let the phone page stop the watcher
            self.log(f"phone page: couldn't build the data: {e!r}")
            return
        self.data, self.json = data, json.dumps(data, ensure_ascii=False).encode()

    def icon(self, size):
        if size not in self.icons:
            self.icons[size] = icon_png(size)
        return self.icons[size]

    def serve(self):
        phone = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def send(self, body, ctype, cache=False):
                self.send_response(200)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "max-age=86400" if cache else "no-store")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self):
                u = urlparse(self.path)
                if u.path in ("/", "/index.html", "/widget"):
                    self.send((HERE / "phone.html").read_bytes(), "text/html; charset=utf-8")
                elif u.path == "/api/characters.json":
                    self.send(phone.json, "application/json; charset=utf-8")
                elif u.path == "/api/widget.json":
                    name = (parse_qs(u.query).get("char") or [None])[0]
                    body = json.dumps(widget(phone.data, name), ensure_ascii=False).encode()
                    self.send(body, "application/json; charset=utf-8")
                elif u.path == "/manifest.webmanifest":
                    self.send(json.dumps(MANIFEST).encode(), "application/manifest+json", True)
                elif u.path in ("/icon.png", "/favicon.ico"):
                    self.send(phone.icon(192), "image/png", True)
                elif u.path == "/icon-512.png":
                    self.send(phone.icon(512), "image/png", True)
                else:
                    self.send_error(404)

        # After an update the old watcher may still hold the port for a moment.
        for attempt in range(30):
            try:
                server = ThreadingHTTPServer(("", self.port), Handler)
                break
            except OSError as e:
                if attempt == 0:
                    self.log(f"phone page: port {self.port} is busy ({e.strerror}), retrying")
                time.sleep(2)
        else:
            self.log(f"phone page: gave up on port {self.port}; pick another with: phone on <port>")
            return
        server.daemon_threads = True
        self.log(f"phone page: {url(self.port)}  (open it on your phone, same Wi-Fi)")
        server.serve_forever()
