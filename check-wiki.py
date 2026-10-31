#!/usr/bin/env python3
"""Check that every addon follows the standard wiki/repository format (see templates/README.md).

Exit code 0 when everything is in place, 1 with a list of problems otherwise.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WIKI = ROOT / "wiki"
SECTIONS = ["What it does", "Download", "What you need", "Install", "Check that it works",
            "Using it", "Settings", "Updating", "Uninstalling", "Known limitations"]
SHARED_SECTIONS = ["Install-on-Windows.md", "Install-on-Linux.md",
                   "Platform-Differences.md", "Troubleshooting.md"]


def addons():
    return sorted(d.name for d in ROOT.iterdir()
                  if d.is_dir() and (d / f"{d.name}.toc").exists())


def read(path):
    return path.read_text(encoding="utf-8") if path.exists() else None


def headings(text, level):
    marker = "#" * level + " "
    return [line[len(marker):].strip() for line in text.splitlines() if line.startswith(marker)]


def check(addon):
    problems = []
    if not re.search(r"^## Version: *\d", read(ROOT / addon / f"{addon}.toc") or "", re.M):
        problems.append(f"{addon}/{addon}.toc has no '## Version: x.y.z'")
    if not (ROOT / addon / "README.md").exists():
        problems.append(f"{addon}/README.md is missing")
    if not (ROOT / addon / "build" / "package.sh").exists():
        problems.append(f"{addon}/build/package.sh is missing (see templates/package-plain.sh)")

    page = read(WIKI / f"{addon}.md")
    if page is None:
        problems.append(f"wiki/{addon}.md is missing (copy templates/wiki-addon-page.md)")
    else:
        if not page.startswith(f"# {addon}\n"):
            problems.append(f"wiki/{addon}.md must start with '# {addon}'")
        if headings(page, 2) != SECTIONS:
            problems.append(f"wiki/{addon}.md sections must be exactly, in order: {', '.join(SECTIONS)}"
                            f"\n      found: {', '.join(headings(page, 2)) or 'none'}")
        if f"releases/download/{addon}-v" not in page:
            problems.append(f"wiki/{addon}.md has no versioned download link")
        if "{" in page and re.search(r"\{(Addon|version|addon-lowercase)\}", page):
            problems.append(f"wiki/{addon}.md still has template placeholders")

    row = re.compile(rf"^\| \*\*{re.escape(addon)}\*\* \|", re.M)
    if not row.search(read(WIKI / "Home.md") or ""):
        problems.append(f"wiki/Home.md has no '| **{addon}** |' row")
    if not row.search(read(ROOT / "README.md") or ""):
        problems.append(f"README.md has no '| **{addon}** |' row")
    if f"[[{addon}]]" not in (read(WIKI / "_Sidebar.md") or ""):
        problems.append(f"wiki/_Sidebar.md has no '- [[{addon}]]'")
    for name in SHARED_SECTIONS:
        if addon not in headings(read(WIKI / name) or "", 2):
            problems.append(f"wiki/{name} has no '## {addon}' section")
    return problems


def main():
    found = addons()
    problems = [p for a in found for p in check(a)]
    if problems:
        print("Wiki/repository format problems (see templates/README.md):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print(f"format OK for: {', '.join(found)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
