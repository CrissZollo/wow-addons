# Wiki snippets for a new addon

Add each of these to the existing wiki pages in `wiki/`. Replace `{Addon}`, `{version}` and the text in braces.
`check-wiki.py` verifies that all of them are present.

## Home.md: a row in "The addons" table

```markdown
| **{Addon}** | {What it does, one line} | [{Addon}-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}-Windows.zip) | [{Addon}-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}-Linux.zip) | [[{Addon}]] |
```
For a plain addon, use the same `{Addon}.zip` link in both download columns.

## _Sidebar.md: under **Addons**, in alphabetical order

```markdown
- [[{Addon}]]
```

## Install-on-Windows.md and Install-on-Linux.md: a section at the end of each

Plain addon:
```markdown
## {Addon}

{Addon} is a plain addon: follow *Plain addons* above with [{Addon}.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}.zip).
```
Addon with a helper program: numbered steps like the Herald section (download → extract → run → what the setup asks → restart WoW and check).

## Platform-Differences.md: a section

```markdown
## {Addon}

No differences: it works the same on Windows and Linux.
```
Or a "| | Windows | Linux (Wine / Proton) |" table like Herald's, ending with a *Tested* row.

## Troubleshooting.md: a section

```markdown
## {Addon}

| Problem | Fix |
|---|---|
| {problem} | {fix} |
```
Or: "No known problems yet."

## README.md (repository root): a row in the addons table

Same columns as the Home.md row, with `[Read me]({Addon}/README.md)` in the last column.
