# Wiki snippets for a new addon (Swedish pages)

The same entries as `templates/en/wiki-snippets.md`, for the Swedish pages in `wiki/`. Write them in Swedish.
`check-wiki.py` verifies that all of them are present.

## Startsida.md: a row in the "Addonsen" table

```markdown
| **{Addon}** | {Vad den gör, en rad} | [{Addon}-Windows.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}-Windows.zip) | [{Addon}-Linux.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}-Linux.zip) | [[{Addon} på svenska]] |
```

## _Sidebar.md: under **🇸🇪 Svenska** → *Addons*

```markdown
- [[{Addon} på svenska]]
```

## Installera-på-Windows.md and Installera-på-Linux.md: a section at the end of each

Plain addon:
```markdown
## {Addon}

{Addon} är en vanlig addon: följ *Vanliga addons* ovan med [{Addon}.zip](https://github.com/CrissZollo/wow-addons/releases/download/{Addon}-v{version}/{Addon}.zip).
```
Addon with a helper program: numbered steps like the Herald section. Quote the program's English texts and explain them in Swedish.

## Skillnader-mellan-Windows-och-Linux.md: a section

```markdown
## {Addon}

Inga skillnader: den fungerar likadant på Windows och Linux.
```

## Felsökning.md: a section

```markdown
## {Addon}

| Problem | Lösning |
|---|---|
| {problem} | {lösning} |
```
Or: "Inga kända problem än."
