# Version Upper

**Script Version:** 3.0.0
**Flame Version:** 2020
**Written by:** John Geehreng
**Creation Date:** 06.06.20
**Update Date:** 07.24.26

## Description

Versions up all selected items. The version prefix is a preference instead of a hard coded
letter, so the script works in any pipeline without editing it.

- Preferences holds a **list of prefixes**, shipping with just `v`. All are live at once, so a
  selection mixing `_v03` and `_OL01` versions up in one pass. No mode to switch.
- **Padding comes from the name**: `v01` → `v02`, `c001` → `c002`, `v99` → `v100`.
- If nothing matches, the script reads the names, works out the prefix in use, and offers to
  add it in one click.

## Menus

- Right-click on clips, sequences, reels, or folders → **Renamers → Version Upper**
- Right-click → **Renamers → Version Upper Preferences**
- Flame Main Menu → **Version Upper → Preferences**

To rename the `Renamers` folder, edit `folder_name` near the top of the script. It needs a
Python hooks reload either way, so it is a one line edit rather than a preference.

## Install

Copy into its own folder in your Flame python path:

```
/opt/Autodesk/shared/python/version_upper/version_upper.py
```

Reload Python hooks, or restart Flame. Needs PySide6 or PySide2, whichever your Flame ships.

## Preferences

| Setting | What it does |
| --- | --- |
| **Version Prefixes** | Prefixes to match. Double-click to edit, **Add** / **Remove** to manage. No numbers allowed — the digits after the prefix are the version. |
| **Case sensitive** | On, `v01` matches and `V01` does not. Off, both match, and each name keeps its own casing (`V01` → `V02`). |
| **Require a separator before the version** | On, the version must follow `_ - .` or a space, or start the name. Off, it counts anywhere, including inside a word — how the original script matched. See below. |

Two behaviours are fixed rather than configurable:

- Padding always comes from the name.
- When a name holds two versions, the last one changes. Versions trail, so this is right
  essentially always.

## Word boundaries

By default **a version only counts when the prefix starts at a word boundary** — the character
before it must be a separator (`_`, `-`, `.`, space) or the start of the name.

| Name | Prefix `v` | Why |
| --- | --- | --- |
| `SHOW_comp_v01` | → `v02` | Preceded by `_` |
| `v01_SHOW_plate` | → `v02` | Start of name |
| `SHOW_comp_v01a` | → `v02a` | Revision letters unaffected |
| `Commercial_Nov25` | skipped | The `v` is inside `Nov` |
| `render_1080_final` | skipped | No prefix in front of the digits |
| `SHOWv01` | skipped | No separator |

**If your names run the version onto the previous word** — `SHOWv01`, `SPOTv3` — untick
**Require a separator before the version** in Preferences. That restores how the original
script matched.

Why it is on by default: with it off, `Commercial_Nov25` reads as version 25 and becomes
`Commercial_Nov26`. A wrong rename is silent; a skipped item shows up in the dialog where you
can see it.

Names that contain a real version stay safe either way, because the last match in the name
wins — `Commercial_Nov25_Sequence_v10` still versions `v10` with the setting off. The exposure
is only names carrying a date and no version at all.

## When items do not match

Skipped items are collected into **one dialog at the end**, not one popup per item. Everything
that did match versions up regardless.

| What it found | What it offers |
| --- | --- |
| A prefix you have not added | **Add "ABC" And Version Up** — adds, saves, versions the skipped items, remembers it |
| The right prefix, wrong case | Explains the casing mismatch and points at Case sensitive |
| No version at all | Points at Preferences |

All three also offer **Preferences**; **Skip These Items** leaves them alone.

Detection ignores four-digit-and-longer numbers, so a year or shot number is never offered as a
prefix.

## Config

Written to a config folder beside the script:

```
version_upper/config/config.json
```

- If the script folder is read only (a system wide install usually is), preferences go to
  `~/.version_upper/config.json` instead.
- An existing config beside the script always wins, so a facility can ship a read-only one.
- The Preferences window shows whichever path is in use.
- `VERSION_UPPER_CONFIG` overrides the location — point it at a shared path to sync a facility.
- A missing or damaged config falls back to defaults rather than breaking the Flame menu.

## Updates

### v3.0.0 [07.24.26]
- Added a Preferences window. The version prefix is now a setting, not a hard coded letter.
- Multiple prefixes live at once — a mixed selection versions up in one pass.
- Padding is read from each name and kept.
- Skipped items collected into one dialog, which names the prefix it found and offers to add it.
- Versions match at the start of a word by default, so `Nov25` is no longer read as version 25.
  Untick **Require a separator before the version** to get the original matching back.
- The prefix a skipped name suggests is never a month, so a date is never one click from being
  renamed.
- Fixed: more than one version token in a name raised a `ValueError` and stopped the run.
- Fixed: more than one version token had every token renumbered. Only the last one changes now.

### v2.1 [06.05.26]
- Updated to work with either PySide6 or PySide2.

### v2.0 [07.12.21]
- Items do not need to end in `v##` anymore. `v##` can be anywhere in the item name. If it cannot
  find `v##` that item will be skipped, but you will see an error message in the Flame UI and the
  script continues.
