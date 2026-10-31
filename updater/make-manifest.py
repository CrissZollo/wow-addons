#!/usr/bin/env python3
"""Write updates.json: what the Addon Updater on players' PCs installs.

    updater/make-manifest.py <Addon> <version> <tag> [notes]

release.sh runs this right before it commits and tags a release. The updater reads
updates.json from the main branch and downloads each file from the release tag, so every
path here is relative to the repository root and must be committed in that tag.

For the addon it records:
  - the in-game files, the same ones the plain build ships: *.toc, *.lua and *.xml at the top
    of <Addon>/, plus media/; they go to Interface/AddOns/<Addon>/;
  - its helper program's files, listed in <Addon>/build/program-files as
    "<file in <Addon>/>  <where it goes in the program folder>" (optional).
It also points the updater's own files (updater.py and the AddonUpdater in-game addon) at this
tag, so every release ships the current updater.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "updates.json"


def entry(src, to):
    path = ROOT / src
    return {"src": src, "to": to, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}


def addon_files(addon):
    base = ROOT / addon
    files = [p for p in sorted(base.iterdir())
             if p.is_file() and p.suffix.lower() in (".toc", ".lua", ".xml")]
    if (base / "media").is_dir():
        files += sorted(p for p in (base / "media").rglob("*") if p.is_file())
    return [entry(p.relative_to(ROOT).as_posix(), f"addons/{addon}/{p.relative_to(base).as_posix()}")
            for p in files]


def program_files(addon):
    listing = ROOT / addon / "build" / "program-files"
    if not listing.exists():
        return []
    out = []
    for line in listing.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            src, dest = line.split()
            out.append(entry(f"{addon}/{src}", f"program/{dest}"))
    return out


def updater_files():
    files = [entry("updater/updater.py", "updater/updater.py")]
    for p in sorted((ROOT / "updater" / "AddonUpdater").iterdir()):
        if p.is_file():
            files.append(entry(p.relative_to(ROOT).as_posix(), f"addons/AddonUpdater/{p.name}"))
    return files


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 1
    addon, version, tag = sys.argv[1:4]
    notes = sys.argv[4] if len(sys.argv) > 4 else ""
    if not (ROOT / addon / f"{addon}.toc").exists():
        print(f"no {addon}/{addon}.toc")
        return 1
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")) if MANIFEST.exists() else {}
    updater_version = re.search(r'^VERSION = "([^"]+)"',
                                (ROOT / "updater" / "updater.py").read_text(encoding="utf-8"), re.M)
    manifest["format"] = 1
    manifest["updater"] = {"version": updater_version.group(1), "tag": tag, "files": updater_files()}
    manifest.setdefault("addons", {})[addon] = {
        "version": version, "tag": tag, "notes": notes,
        "files": addon_files(addon) + program_files(addon),
    }
    manifest["addons"] = dict(sorted(manifest["addons"].items()))
    MANIFEST.write_text(json.dumps(manifest, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"updates.json: {addon} {version} ({tag}), updater {updater_version.group(1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
