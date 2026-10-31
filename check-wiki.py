#!/usr/bin/env python3
"""Check that every addon follows the standard wiki/repository format (see templates/README.md).

The wiki exists in English and Swedish. Every page has a counterpart in the other language,
linked at the top, and every addon needs a page and the same entries in both languages.
Exit code 0 when everything is in place, 1 with a list of problems otherwise.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI = ROOT / "wiki"

LANGS = {
    "en": {
        "home": "Home",
        "addon_page": "{addon}",
        "switch": "Läs på svenska",       # link text pointing to the other language
        "sections": ["What it does", "Download", "What you need", "Install", "Check that it works",
                     "Using it", "Settings", "Updating", "Uninstalling", "Known limitations"],
        "shared": ["Install on Windows", "Install on Linux", "Platform Differences", "Troubleshooting"],
    },
    "sv": {
        "home": "Startsida",
        "addon_page": "{addon} på svenska",
        "switch": "Read in English",
        "sections": ["Vad den gör", "Ladda ner", "Det här behöver du", "Installera", "Kolla att det fungerar",
                     "Så använder du den", "Inställningar", "Uppdatera", "Avinstallera", "Kända begränsningar"],
        "shared": ["Installera på Windows", "Installera på Linux", "Skillnader mellan Windows och Linux",
                   "Felsökning"],
    },
}
# Shared pages that exist once per language, as (English, Swedish) pairs.
PAIRS = [("Home", "Startsida"), ("Install on Windows", "Installera på Windows"),
         ("Install on Linux", "Installera på Linux"),
         ("Platform Differences", "Skillnader mellan Windows och Linux"),
         ("Discord Webhook", "Webhook-länken"), ("Troubleshooting", "Felsökning"),
         ("Automatic Updates", "Automatiska uppdateringar")]


def file_of(title):
    return WIKI / (title.replace(" ", "-") + ".md")


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def headings(text, level):
    marker = "#" * level + " "
    return [line[len(marker):].strip() for line in text.splitlines() if line.startswith(marker)]


def addons():
    return sorted(d.name for d in ROOT.iterdir()
                  if d.is_dir() and (d / f"{d.name}.toc").exists())


def check_switch(title, other_title, lang):
    """The page links to the same page in the other language near the top."""
    text = read(file_of(title))
    if text is None:
        return [f"wiki/{file_of(title).name} is missing"]
    top = "\n".join(text.splitlines()[:5])
    if f"[[{LANGS[lang]['switch']}|{other_title}]]" not in top:
        return [f"wiki/{file_of(title).name} needs '[[{LANGS[lang]['switch']}|{other_title}]]' under its title"]
    return []


def check_addon(addon):
    problems = []
    if not re.search(r"^## Version: *\d", read(ROOT / addon / f"{addon}.toc") or "", re.M):
        problems.append(f"{addon}/{addon}.toc has no '## Version: x.y.z'")
    for f in ("README.md", "build/package.sh"):
        if not (ROOT / addon / f).exists():
            problems.append(f"{addon}/{f} is missing")
    if not re.search(rf"^\| \*\*{re.escape(addon)}\*\* \|", read(ROOT / "README.md") or "", re.M):
        problems.append(f"README.md has no '| **{addon}** |' row")

    sidebar = read(WIKI / "_Sidebar.md") or ""
    for lang, cfg in LANGS.items():
        title = cfg["addon_page"].format(addon=addon)
        page = read(file_of(title))
        name = file_of(title).name
        if page is None:
            problems.append(f"wiki/{name} is missing (template: templates/{lang}/wiki-addon-page.md)")
        else:
            if not page.startswith(f"# {title}\n"):
                problems.append(f"wiki/{name} must start with '# {title}'")
            if headings(page, 2) != cfg["sections"]:
                problems.append(f"wiki/{name} sections must be exactly, in order: {', '.join(cfg['sections'])}"
                                f"\n      found: {', '.join(headings(page, 2)) or 'none'}")
            if f"releases/download/{addon}-v" not in page:
                problems.append(f"wiki/{name} has no versioned download link")
            if re.search(r"\{(Addon|version|addon-lowercase)\}", page):
                problems.append(f"wiki/{name} still has template placeholders")
        other_lang = "sv" if lang == "en" else "en"
        problems += check_switch(title, LANGS[other_lang]["addon_page"].format(addon=addon), lang)

        if not re.search(rf"^\| \*\*{re.escape(addon)}\*\* \|", read(file_of(cfg["home"])) or "", re.M):
            problems.append(f"wiki/{file_of(cfg['home']).name} has no '| **{addon}** |' row")
        if f"[[{title}]]" not in sidebar:
            problems.append(f"wiki/_Sidebar.md has no '- [[{title}]]'")
        for shared in cfg["shared"]:
            if addon not in headings(read(file_of(shared)) or "", 2):
                problems.append(f"wiki/{file_of(shared).name} has no '## {addon}' section")
    return problems


def main():
    problems = []
    for en, sv in PAIRS:
        problems += check_switch(en, sv, "en") + check_switch(sv, en, "sv")
    found = addons()
    for addon in found:
        problems += check_addon(addon)
    if problems:
        print("Wiki/repository format problems (see templates/README.md):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"format OK (English + Swedish) for: {', '.join(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
