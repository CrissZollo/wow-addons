#!/usr/bin/env python3
"""Addon Updater: keeps the WoW Forever addons from CrissZollo/wow-addons up to date.

Every addon download includes this program. The addon's installer runs `updater.py install`,
which copies the updater to a fixed place on the PC, registers the addon, installs the in-game
AddonUpdater addon and makes the updater start in the background when you log in. From then on
it reads updates.json from the repository every 30 minutes and installs whatever changed: the
addon, its helper program (e.g. Herald's watcher) and the updater itself.

While WoW is running it only installs updates that a /reload picks up (new contents for the
same files). Updates that add or remove files wait until WoW closes. The in-game addon says
"<Addon> updated: 1.0.0 -> 1.1.0" at the next login. Mid-session it (experimentally) asks for a
/reload or a restart: addons can't hear from programs on the PC, so this program switches two
files in AddonUpdater/probe/ between junk and a real font, and the addon checks whether they load.

  updater.py                  check now and every 30 minutes (what autostart runs)
  updater.py install --addon NAME [--addon-dir DIR] [--program-dir DIR] [--game DIR]
                              register an addon (and copy DIR into AddOns), set up the updater
  updater.py check            check for updates now
  updater.py status           show the addons it keeps up to date
  updater.py stop             stop the background updater
  updater.py remove NAME      stop updating NAME (removes the updater when nothing is left)
  updater.py notice-test [off]  light the in-game "/reload" notice for 10 minutes, to test it
  add --dry-run to check without installing anything

Python 3.8+, standard library only (the Windows downloads carry a portable Python).
"""
import base64
import hashlib
import json
import os
import re
import shutil
import string
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

VERSION = "1.0.0"
REPO = "CrissZollo/wow-addons"
# updates.json is read from <SOURCE>/main/updates.json and files from <SOURCE>/<tag>/<path>.
SOURCE = os.environ.get("ADDON_UPDATER_SOURCE") or f"https://raw.githubusercontent.com/{REPO}"
CHECK_EVERY = 30 * 60
RETRY_EVERY = 5 * 60
TICK = 15                      # seconds between looks at the game (running? reloaded?)
UA = f"addon-updater/{VERSION}"
COMPANION = "AddonUpdater"     # the in-game addon's folder
GENERATED = ("Managed.lua", "probe")  # written by this program into the companion's folder
NOTICE_TEST_SECONDS = 10 * 60

SCRIPT = Path(__file__).resolve()
IS_WIN = os.name == "nt"
NO_WINDOW = 0x08000000 if IS_WIN else 0  # CREATE_NO_WINDOW: no console flash under pythonw
if os.environ.get("ADDON_UPDATER_HOME"):
    HOME = Path(os.environ["ADDON_UPDATER_HOME"])
elif IS_WIN:
    HOME = Path(os.environ.get("LOCALAPPDATA") or Path.home() / "AppData" / "Local") / "AddonUpdater"
else:
    HOME = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "addon-updater"
INSTALLED = HOME / "updater.py"
STATE_PATH = HOME / "state.json"
LOCK_PATH = HOME / "updater.lock"
STOP_PATH = HOME / "updater.stop"
CHECK_PATH = HOME / "updater.check"
NOTICE_TEST_PATH = HOME / "notice-test"
LOG_PATH = HOME / "updater.log"
UNIT = "addon-updater"

# A 640-byte TrueType font with one glyph. The in-game addon tries to load probe/<name>.ttf
# as a font; this program writes either this font ("lit") or PROBE_OFF (fails to load) there.
PROBE_FONT = base64.b64decode(
    "AAEAAAAKAIAAAwAgT1MvMkUAQzMAAAEoAAAAYGNtYXAADABzAAABkAAAADRnbHlm99EkBgAAAcwAAAAaaGVhZC8i"
    "XfYAAACsAAAANmhoZWEFFgFhAAAA5AAAACRobXR4Au4AMgAAAYgAAAAIbG9jYQANAA0AAAHEAAAABm1heHAABAAG"
    "AAABCAAAACBuYW1lqBkNYQAAAegAAABvcG9zdAAHAAAAAAJYAAAAJgABAAAAAQAAbS7zZl8PPPUAAwPoAAAAAOcM"
    "DS0AAAAA5wwNLQAyAAABwgK8AAAAAwACAAAAAAAAAAEAAAMg/zgAAAH0ADIAMgHCAAEAAAAAAAAAAAAAAAAAAAAC"
    "AAEAAAACAAQAAQAAAAAAAgAAAAAAAAAAAAAAAAAAAAAAAwF3AZAABQAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    "AAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAPz8/PwAAACAAIAMg/zgAAAMgAMgAAAAAAAAAAAAAAAAAAAAgAAAB9AAy"
    "APoAAAAAAAIAAAADAAAAFAADAAEAAAAUAAQAIAAAAAQABAABAAAAIP//AAAAIP///+EAAQAAAAAAAAANAA0AAAAB"
    "ADIAAAHCArwAAwAAMxEhETIBkAK8/UQAAAAAAAAEADYAAQAAAAAAAQAMAAAAAQAAAAAAAgAHAAwAAwABBAkAAQAY"
    "ABMAAwABBAkAAgAOACtVcGRhdGVyUHJvYmVSZWd1bGFyAFUAcABkAGEAdABlAHIAUAByAG8AYgBlAFIAZQBnAHUA"
    "bABhAHIAAAIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAAAMAAA==")
PROBE_OFF = b"no update\n"


def log(msg):
    print(f"[updater {time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)


def run_quiet(cmd, timeout=60):
    """Run a command without a console window; returns (ok, stdout)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           creationflags=NO_WINDOW)
        return r.returncode == 0, r.stdout
    except (OSError, subprocess.SubprocessError):
        return False, ""


# ---------------------------------------------------------------- state

def load_state(strict=False):
    """strict: raise ValueError for a damaged state.json instead of starting over."""
    try:
        state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except OSError:
        state = {}
    except ValueError:
        if strict:
            raise
        state = {}
    state.setdefault("addons", {})
    return state


def save_state(state):
    HOME.mkdir(parents=True, exist_ok=True)
    tmp = STATE_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
    tmp.replace(STATE_PATH)


def sha256(path):
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def toc_version(toc):
    try:
        m = re.search(r"^## Version: *(\S+)", toc.read_text(encoding="utf-8", errors="replace"), re.M)
    except OSError:
        return None
    return m.group(1) if m else None


def version_tuple(v):
    return tuple(int(x) for x in re.findall(r"\d+", v or ""))


def file_version(script):
    """VERSION of another copy of this program, or None."""
    try:
        m = re.search(r'^VERSION = "([^"]+)"', script.read_text(encoding="utf-8"), re.M)
    except OSError:
        return None
    return m.group(1) if m else None


# ---------------------------------------------------------------- the game
# Same places as find_game_dir() in Herald/watcher/herald.py; keep the two lists in step.

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
                    yield p.parent / "_forever_"
            except OSError:
                pass
        for drive in string.ascii_uppercase:
            if os.path.exists(f"{drive}:\\"):
                for sub in ("Program Files (x86)", "Program Files", "Games", "Blizzard", ""):
                    yield Path(f"{drive}:\\") / sub / "World of Warcraft" / "_forever_"
    else:
        home = Path.home()
        prefixes = [
            "Games/Heroic/Prefixes/*/*", "Games/Heroic/Prefixes/*",
            "Games/*", "Games/*/*",
            ".local/share/Steam/steamapps/compatdata/*/pfx",
            ".steam/steam/steamapps/compatdata/*/pfx",
            ".var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/compatdata/*/pfx",
            ".local/share/bottles/bottles/*",
            ".var/app/com.usebottles.bottles/data/bottles/bottles/*",
            ".var/app/net.lutris.Lutris/data/lutris/prefixes/*",
            ".wine",
        ]
        for prefix in prefixes:
            for pf in ("Program Files (x86)", "Program Files"):
                yield from home.glob(f"{prefix}/drive_c/{pf}/World of Warcraft/_forever_")


def is_game_dir(p):
    return p.is_dir() and any((p / x).exists() for x in ("Wow.exe", "Interface", "Logs", "WTF"))


def find_game_dir():
    return next((p for p in game_dir_candidates() if is_game_dir(p)), None)


def wow_running(game):
    """Is the game running? Looks for the Wow*.exe of this install among the processes."""
    names = {p.name.lower() for p in game.glob("*.exe") if p.name.lower().startswith("wow")}
    names = names or {"wow.exe", "wowclassic.exe"}
    if IS_WIN:
        ok, out = run_quiet(["tasklist", "/FO", "CSV", "/NH"], timeout=30)
        return ok and any(line.split(",")[0].strip('"').lower() in names for line in out.splitlines())
    # Wine and Proton keep the Windows path of the .exe in the process's command line.
    for cmdline in Path("/proc").glob("[0-9]*/cmdline"):
        try:
            args = cmdline.read_bytes().split(b"\0")
        except OSError:
            continue
        for a in args:
            if a and a.decode("utf-8", "replace").replace("\\", "/").rsplit("/", 1)[-1].lower() in names:
                return True
    return False


class Game:
    def __init__(self, state):
        self.dir = Path(state.get("game_dir") or "")
        self.ok = bool(state.get("game_dir")) and is_game_dir(self.dir)
        self.addons = self.dir / "Interface" / "AddOns"
        self.running = self.ok and wow_running(self.dir)

    def companion_saved(self):
        """When WoW last wrote the companion's SavedVariables (at /reload and logout)."""
        times = [p.stat().st_mtime for p in
                 self.dir.glob(f"WTF/Account/*/SavedVariables/{COMPANION}.lua")]
        return max(times, default=0.0)


# ---------------------------------------------------------------- updates.json

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_manifest():
    data = json.loads(fetch(f"{SOURCE}/main/updates.json"))
    if not isinstance(data, dict) or data.get("format") != 1:
        raise ValueError("updates.json has an unknown format; is this updater too old?")
    return data


def components(manifest, state):
    """(name, entry) for the updater itself and every registered addon in updates.json."""
    if manifest.get("updater"):
        yield "updater", manifest["updater"]
    for name in sorted(state["addons"]):
        entry = (manifest.get("addons") or {}).get(name)
        if entry:
            yield name, entry


TO_RE = re.compile(r"^(addons|program|updater)/([\w .()+-]+(?:/[\w .()+-]+)*)$")


def target(to, name, state, game):
    """Where a release file goes on this PC, or None when it doesn't apply here.

    addons/<Folder>/...  the game's Interface/AddOns (only the component's own folder)
    program/...          the addon's helper program folder, if it registered one
    updater/...          this program's own folder (only for the updater itself)
    """
    m = TO_RE.match(to)
    if not m or any(part in (".", "..") or part != part.strip() for part in m.group(2).split("/")):
        raise ValueError(f"bad file target {to!r} in updates.json")
    root, rel = m.groups()
    if root == "addons":
        if rel.split("/")[0] != (COMPANION if name == "updater" else name):
            raise ValueError(f"{name} may not write {to!r}")
        return game.addons / rel
    if root == "program":
        pdir = state["addons"].get(name, {}).get("program_dir") if name != "updater" else None
        return Path(pdir) / rel if pdir and Path(pdir).is_dir() else None
    return HOME / rel if name == "updater" else None


def toc_body(data):
    """The .toc without its Version line: when this changes, a /reload isn't enough."""
    return [line.strip() for line in data.decode("utf-8", "replace").splitlines()
            if line.strip() and not re.match(r"##\s*Version\s*:", line.strip(), re.I)]


def update_component(name, entry, state, game, dry_run=False):
    """Bring one addon (or the updater) up to date.

    Returns "current", "dry", "deferred" (waits until WoW closes), "installed", or "reload"
    (installed addon files while WoW runs: a /reload picks them up).
    """
    files = [(f, target(f["to"], name, state, game)) for f in entry["files"]]
    files = [(f, dest) for f, dest in files if dest]
    folder = game.addons / (COMPANION if name == "updater" else name)
    wanted = {dest for _, dest in files}
    stale = []  # files in the addon's folder that the new version no longer has
    if folder.is_dir():
        for p in folder.rglob("*"):
            rel = p.relative_to(folder).parts
            if p.is_file() and p not in wanted and not (name == "updater" and rel[0] in GENERATED):
                stale.append(p)
    changed = [(f, dest) for f, dest in files if sha256(dest) != f["sha256"]]
    if not changed and not stale:
        return "current"
    if dry_run:
        return "dry"

    staged = []
    for f, dest in changed:
        data = fetch(f"{SOURCE}/{urllib.parse.quote(entry['tag'])}/{urllib.parse.quote(f['src'])}")
        if hashlib.sha256(data).hexdigest() != f["sha256"]:
            raise ValueError(f"{f['src']} from {entry['tag']} doesn't match updates.json")
        staged.append((dest, data))

    in_game = [(dest, data) for dest, data in staged if folder in dest.parents]
    if game.running and (in_game or stale):
        # WoW only sees new or removed files after a restart, and reads the .toc at startup.
        same_files = not stale and all(dest.exists() for dest, _ in in_game)
        same_toc = all(toc_body(data) == toc_body(dest.read_bytes())
                       for dest, data in in_game if dest.suffix.lower() == ".toc")
        if not (same_files and same_toc):
            return "deferred"

    for dest, data in staged:
        dest.parent.mkdir(parents=True, exist_ok=True)
        mode = dest.stat().st_mode if dest.exists() else None
        tmp = dest.with_name(dest.name + ".new")
        tmp.write_bytes(data)
        if mode is not None and not IS_WIN:
            tmp.chmod(mode & 0o7777)  # keep e.g. the executable bit of herald.py
        os.replace(tmp, dest)
    for p in stale:
        p.unlink()
    return "reload" if game.running and in_game else "installed"


def check(state, manifest, game, dry_run=False):
    """Install every update that can go in now. Changes state; logs what happened."""
    if not game.ok:
        log(f"can't find WoW Forever at {state.get('game_dir')!r}; run the addon's installer again")
        return
    forget_uninstalled(state, game)
    deferred = []
    for name, entry in components(manifest, state):
        label = f"{'Addon Updater' if name == 'updater' else name} {entry.get('version', '')}".strip()
        try:
            result = update_component(name, entry, state, game, dry_run)
        except (OSError, ValueError, KeyError, TypeError) as e:
            log(f"couldn't update {label}: {e}")
            continue
        if result == "deferred":
            deferred.append(name)
            if name not in state.get("deferred", []):
                log(f"{label} adds or removes files, so it installs when WoW closes")
        elif result == "dry":
            log(f"{label} would be installed (--dry-run)")
        elif result != "current":
            log(f"installed {label}" + (" (a /reload in game picks it up)" if result == "reload" else ""))
            if name != "updater":
                state["addons"][name]["version"] = entry.get("version")
            if result == "reload" and state.get("reload_since") is None:
                state["reload_since"] = game.companion_saved()
    state["deferred"] = deferred
    write_managed(state, manifest, game)


def forget_uninstalled(state, game):
    """An addon whose folder was deleted from AddOns was uninstalled: stop updating it."""
    if not game.addons.is_dir():
        return
    for name in list(state["addons"]):
        if not (game.addons / name).is_dir():
            log(f"{name} isn't in the AddOns folder any more, so it won't be updated")
            del state["addons"][name]


# ---------------------------------------------------------------- the in-game addon

def lua_str(s):
    s = str(s or "").replace("\\", "\\\\").replace('"', '\\"').replace("\r", "").replace("\n", "\\n")
    return f'"{s}"'


def write_if_changed(path, data):
    try:
        if path.read_bytes() == data:
            return
    except OSError:
        pass
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    except OSError as e:  # e.g. WoW holds the probe font open on Windows
        log(f"couldn't write {path}: {e}")


def write_managed(state, manifest, game):
    """Managed.lua tells the in-game addon which addons this program keeps up to date."""
    folder = game.addons / COMPANION
    if not folder.is_dir():
        return
    latest = (manifest or {}).get("addons") or {}
    lines = ["-- Written by the Addon Updater program on your PC; don't edit.",
             "AddonUpdater_Managed = {"]
    for name in sorted(state["addons"]):
        e = latest.get(name) or {}
        lines.append(f"    {{ name = {lua_str(name)}, version = {lua_str(e.get('version'))}, "
                     f"notes = {lua_str(e.get('notes'))} }},")
    lines.append("}")
    write_if_changed(folder / "Managed.lua", ("\n".join(lines) + "\n").encode("utf-8"))


def sync_probes(state, game):
    """Light probe/reload.ttf while a /reload is due and probe/restart.ttf while an update
    waits for WoW to close. Everything goes dark when WoW isn't running."""
    folder = game.addons / COMPANION
    if not game.ok or not folder.is_dir():
        return
    if not game.running or (state.get("reload_since") is not None
                            and game.companion_saved() > state["reload_since"]):
        state["reload_since"] = None  # WoW closed, or the player reloaded / logged out since
    try:
        testing = time.time() - NOTICE_TEST_PATH.stat().st_mtime < NOTICE_TEST_SECONDS
    except OSError:
        testing = False
    lit = {"reload": game.running and (state.get("reload_since") is not None or testing),
           "restart": game.running and bool(state.get("deferred"))}
    for name, on in lit.items():
        write_if_changed(folder / "probe" / f"{name}.ttf", PROBE_FONT if on else PROBE_OFF)


def install_companion(game, state):
    """Put the in-game addon in AddOns (from this download) unless it's already there."""
    dest = game.addons / COMPANION
    src = SCRIPT.parent / COMPANION
    if not dest.is_dir() and src.is_dir():
        shutil.copytree(src, dest)
    if dest.is_dir():
        for name in ("reload", "restart"):
            if not (dest / "probe" / f"{name}.ttf").exists():
                write_if_changed(dest / "probe" / f"{name}.ttf", PROBE_OFF)
        write_managed(state, None, game)


# ---------------------------------------------------------------- running in the background

_lock = None


def acquire_lock(wait=0):
    """Only one updater may run at a time."""
    global _lock
    if _lock:
        return True
    HOME.mkdir(parents=True, exist_ok=True)
    deadline = time.time() + wait
    while True:
        fh = open(LOCK_PATH, "a+")
        try:
            if IS_WIN:
                import msvcrt
                fh.seek(0)
                msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
            _lock = fh
            return True
        except OSError:
            fh.close()
            if time.time() >= deadline:
                return False
            time.sleep(0.5)


def release_lock():
    global _lock
    if _lock:
        _lock.close()
        _lock = None


def restart_self():
    """Run the new version after updating this file."""
    log("the updater was updated; restarting")
    release_lock()
    os.environ["ADDON_UPDATER_RESTARTED"] = "1"
    args = [sys.executable, str(SCRIPT)] + [a for a in sys.argv[1:] if a.startswith("--")]
    if not IS_WIN:
        os.execv(sys.executable, args)
    subprocess.Popen(args, creationflags=0x00000008 | 0x00000200, close_fds=True,  # detached
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    sys.exit(0)


def run(dry_run):
    if not acquire_lock(wait=20 if os.environ.pop("ADDON_UPDATER_RESTARTED", None) else 0):
        log("the updater is already running")
        return 0
    STOP_PATH.unlink(missing_ok=True)
    my_sha = sha256(SCRIPT)
    log(f"Addon Updater {VERSION} started")
    next_check, was_running, saved = time.time() + 5, False, None
    while True:
        try:
            state = load_state(strict=True)
        except ValueError:
            log(f"{STATE_PATH} is damaged; run an addon's installer again")
            return 1
        if not state["addons"]:
            log("no addons left to update; turning the updater off")
            retire(state)
            return 0
        game = Game(state)
        if CHECK_PATH.exists():
            CHECK_PATH.unlink(missing_ok=True)
            next_check = 0
        if was_running and not game.running and state.get("deferred"):
            next_check = 0  # WoW closed: install what was waiting
        was_running = game.running
        if time.time() >= next_check:
            try:
                manifest = fetch_manifest()
                next_check = time.time() + CHECK_EVERY
            except (OSError, ValueError) as e:
                log(f"couldn't read updates.json: {e}")
                manifest, next_check = None, time.time() + RETRY_EVERY
            if manifest:
                check(state, manifest, game, dry_run)
        sync_probes(state, game)
        if json.dumps(state, sort_keys=True) != saved:
            save_state(state)
            saved = json.dumps(state, sort_keys=True)
        if SCRIPT == INSTALLED and sha256(SCRIPT) != my_sha:
            restart_self()
        for _ in range(TICK):
            if STOP_PATH.exists():
                STOP_PATH.unlink(missing_ok=True)
                log("stopped")
                return 0
            if CHECK_PATH.exists():
                break
            time.sleep(1)


# ---------------------------------------------------------------- autostart

def runner_python():
    """The Python to run the installed updater with, without a console window on Windows."""
    if IS_WIN:
        for exe in (HOME / "python" / "pythonw.exe", Path(sys.executable).with_name("pythonw.exe")):
            if exe.exists():
                return exe
    return Path(sys.executable)


def startup_dir():
    return (Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu"
            / "Programs" / "Startup")


def unit_path():
    return (Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
            / "systemd" / "user" / f"{UNIT}.service")


def systemctl(*args):
    return run_quiet(["systemctl", "--user", *args], timeout=30)[0]


def autostart_enabled():
    if IS_WIN:
        return any((startup_dir() / n).exists() for n in ("Addon Updater.lnk", "Addon Updater.bat"))
    return unit_path().exists()


def set_autostart(on):
    """Start the updater when you log in to the PC. Returns a line saying what happened."""
    if not IS_WIN:
        if not shutil.which("systemctl"):
            return "! no systemd here: run 'python3 %s' yourself before playing" % INSTALLED
        if not on:
            systemctl("disable", UNIT)
            unit_path().unlink(missing_ok=True)
            systemctl("daemon-reload")
            return "✓ updater autostart off"
        unit_path().parent.mkdir(parents=True, exist_ok=True)
        unit_path().write_text(
            "[Unit]\nDescription=Keep WoW Forever addons up to date (Addon Updater)\n"
            "After=network-online.target\n\n"
            f'[Service]\nExecStart="{runner_python()}" "{INSTALLED}" --background\n'
            "Restart=on-failure\nRestartSec=60\n\n[Install]\nWantedBy=default.target\n",
            encoding="utf-8")
        if systemctl("daemon-reload") and systemctl("enable", UNIT):
            return "✓ the updater starts when you log in (systemd user service addon-updater)"
        return "! couldn't enable the addon-updater systemd user service"
    lnk, bat = startup_dir() / "Addon Updater.lnk", startup_dir() / "Addon Updater.bat"
    if not on:
        lnk.unlink(missing_ok=True)
        bat.unlink(missing_ok=True)
        return "✓ updater autostart off"
    startup_dir().mkdir(parents=True, exist_ok=True)
    q = lambda p: str(p).replace("'", "''")  # PowerShell single-quoted string
    ps = (f"$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{q(lnk)}');"
          f"$s.TargetPath='{q(runner_python())}';$s.Arguments='\"{q(INSTALLED)}\" --background';"
          f"$s.WorkingDirectory='{q(HOME)}';$s.Description='Keeps WoW Forever addons up to date';$s.Save()")
    run_quiet(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps])
    if lnk.exists():
        bat.unlink(missing_ok=True)
    else:  # no PowerShell: a batch file (flashes a window briefly at login)
        try:
            bat.write_text(f'@start "" "{runner_python()}" "{INSTALLED}" --background\r\n',
                           encoding="utf-8")
        except OSError as e:
            return f"! couldn't make the updater start with Windows: {e}"
    return "✓ the updater starts with Windows (in the background, no window)"


def start_background():
    if not IS_WIN and unit_path().exists() and systemctl("start", UNIT):
        return
    flags = 0x00000008 | 0x00000200 if IS_WIN else 0  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    subprocess.Popen([str(runner_python()), str(INSTALLED), "--background"], cwd=str(HOME),
                     creationflags=flags, start_new_session=not IS_WIN, close_fds=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def stop_background():
    """Stop the background updater; True if it was running."""
    if not IS_WIN and systemctl("is-active", "--quiet", UNIT):
        systemctl("stop", UNIT)
        return True
    if acquire_lock():
        release_lock()
        return False
    STOP_PATH.touch()
    ok = acquire_lock(wait=30)
    release_lock()
    STOP_PATH.unlink(missing_ok=True)
    return ok


def retire(state):
    """Nothing left to update: switch autostart off and remove the in-game addon."""
    log(set_autostart(False))
    game = Game(state)
    if game.ok and (game.addons / COMPANION).is_dir():
        shutil.rmtree(game.addons / COMPANION, ignore_errors=True)


# ---------------------------------------------------------------- commands

def ask(prompt):
    try:
        return input(prompt).strip().strip('"')
    except EOFError:
        return ""


def option(args, name):
    if name in args and args.index(name) + 1 < len(args):
        return args[args.index(name) + 1]
    return None


def install_self():
    """Copy this program (and on Windows the portable Python) to HOME, unless a copy at least
    as new is already there. After that it updates itself."""
    HOME.mkdir(parents=True, exist_ok=True)
    if SCRIPT != INSTALLED and (not INSTALLED.exists()
                                or version_tuple(file_version(INSTALLED)) < version_tuple(VERSION)):
        shutil.copy2(SCRIPT, INSTALLED)
    here = Path(sys.executable).parent
    if IS_WIN and any(here.glob("python*._pth")) and not (HOME / "python" / "pythonw.exe").exists():
        shutil.copytree(here, HOME / "python", dirs_exist_ok=True)


def cmd_install(args):
    name, src, pdir, game_arg = (option(args, o) for o in
                                 ("--addon", "--addon-dir", "--program-dir", "--game"))
    if not name or not re.match(r"^[A-Za-z0-9_]+$", name):
        print("usage: updater.py install --addon NAME [--addon-dir DIR] [--program-dir DIR] [--game DIR]")
        return 1
    if IS_WIN and "\\AppData\\Local\\Temp\\" in str(SCRIPT):
        print("It looks like this is running from inside the zip file.\n"
              "Right-click the zip -> Extract All, then run the installer from the extracted folder.")
        return 1
    was_running = stop_background()
    state = load_state()
    game = Path(game_arg) if game_arg else Path(state.get("game_dir") or "")
    if not is_game_dir(game):
        game = find_game_dir()
    while not game or not is_game_dir(game):
        p = ask("Couldn't find WoW Forever. Paste the path to your 'World of Warcraft' folder: ")
        if not p:
            return 1
        game = Path(p) if Path(p).name == "_forever_" else Path(p) / "_forever_"
        if not is_game_dir(game):
            print(f"  ! no WoW Forever install in {game}")
    state["game_dir"] = str(game)
    g = Game(state)

    if src:  # a plain addon: this program installs the addon itself
        dest = g.addons / name
        try:
            shutil.copytree(src, dest, dirs_exist_ok=True)
            print(f"  ✓ {name} installed in {dest}")
        except OSError as e:
            print(f"  ! couldn't install {name} ({e}).\n    Copy the {name} folder into {g.addons} yourself.")
    if not (g.addons / name).is_dir():
        print(f"  ! {name} isn't in {g.addons} yet, so it can't be kept up to date")
        return 1
    state["addons"][name] = {
        "program_dir": str(Path(pdir).resolve()) if pdir else None,
        "version": toc_version(g.addons / name / f"{name}.toc"),
    }
    try:
        install_self()
        install_companion(g, state)
    except OSError as e:
        print(f"  ! couldn't set up automatic updates: {e}")
        return 1
    save_state(state)
    if "--no-start" not in args:
        line = set_autostart(True)
        if line.startswith("!"):
            print(f"  {line}")
        start_background()
    print(f"  ✓ automatic updates on for {name}"
          + (" (the updater was restarted)" if was_running else ""))
    return 0


def cmd_check(dry_run):
    if not dry_run and not acquire_lock():
        CHECK_PATH.touch()
        print("The background updater is checking now. See 'updater.py status' in a minute.")
        return 0
    state = load_state()
    if not state["addons"]:
        print("No addons registered. Run an addon's installer first.")
        return 1
    try:
        manifest = fetch_manifest()
    except (OSError, ValueError) as e:
        print(f"Couldn't read updates.json: {e}")
        return 1
    game = Game(state)
    check(state, manifest, game, dry_run)
    sync_probes(state, game)
    if not dry_run:
        save_state(state)
    return 0


def cmd_status():
    state = load_state()
    running = not acquire_lock()
    release_lock()
    print(f"Addon Updater {VERSION} in {HOME}")
    print(f"  background: {'running' if running else 'not running'}, "
          f"autostart {'on' if autostart_enabled() else 'off'}")
    game = Game(state)
    print(f"  WoW Forever: {state.get('game_dir') or 'not set'}"
          + (" (running)" if game.running else "" if game.ok else " (not found!)"))
    try:
        latest = fetch_manifest().get("addons") or {}
    except (OSError, ValueError) as e:
        latest = {}
        print(f"  couldn't read updates.json: {e}")
    for name, a in sorted(state["addons"].items()):
        have = toc_version(game.addons / name / f"{name}.toc") or a.get("version") or "?"
        new = (latest.get(name) or {}).get("version")
        note = ""
        if name in state.get("deferred", []):
            note = f" -> {new} waits until WoW closes"
        elif new and new != have:
            note = f" -> {new} installs at the next check"
        print(f"  {name}: {have}{note}" + (f"  (program: {a['program_dir']})" if a.get("program_dir") else ""))
    if not state["addons"]:
        print("  no addons registered")
    print(f"  log: {LOG_PATH}")
    return 0


def cmd_remove(name):
    state = load_state()
    if name not in state["addons"]:
        print(f"{name} isn't kept up to date by the updater.")
        return 0
    stop_background()
    del state["addons"][name]
    save_state(state)
    if state["addons"]:
        start_background()
        print(f"  ✓ {name} won't be updated any more")
        return 0
    retire(state)
    if not IS_WIN or not str(Path(sys.executable)).startswith(str(HOME)):
        shutil.rmtree(HOME, ignore_errors=True)
    print(f"  ✓ {name} won't be updated any more; the updater is removed")
    return 0


def cmd_notice_test(off):
    if off:
        NOTICE_TEST_PATH.unlink(missing_ok=True)
        print("Notice test off.")
    else:
        HOME.mkdir(parents=True, exist_ok=True)
        NOTICE_TEST_PATH.touch()
        print("For the next 10 minutes, while WoW runs, the in-game addon should say:\n"
              "  'Addon Updater: An addon update was installed. Type /reload to start using it.'\n"
              "within about 30 seconds. If it doesn't, the in-game /reload notice doesn't work in\n"
              "this version of WoW; updates still install and are announced at the next login.")
    if acquire_lock():  # no background updater to light the probe, so do it here
        state = load_state()
        sync_probes(state, Game(state))
        save_state(state)
    return 0


def main():
    args = sys.argv[1:]
    if sys.stdout is None or "--background" in args:  # no console: log to a file
        HOME.mkdir(parents=True, exist_ok=True)
        if LOG_PATH.exists() and LOG_PATH.stat().st_size > 1_000_000:
            LOG_PATH.unlink()
        sys.stdout = sys.stderr = open(LOG_PATH, "a", encoding="utf-8", buffering=1)
    else:
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    dry_run = "--dry-run" in args
    cmd = args[0] if args and not args[0].startswith("--") else ""
    if cmd == "install":
        return cmd_install(args)
    if cmd == "check":
        return cmd_check(dry_run)
    if cmd == "status":
        return cmd_status()
    if cmd == "stop":
        print("Updater stopped." if stop_background() else "The updater isn't running.")
        return 0
    if cmd == "remove" and len(args) > 1:
        return cmd_remove(args[1])
    if cmd == "notice-test":
        return cmd_notice_test(args[1:2] == ["off"])
    if cmd:
        print(__doc__)
        return 1
    try:
        return run(dry_run)
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    sys.exit(main())
