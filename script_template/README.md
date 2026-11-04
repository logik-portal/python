# Script Template

**Script Version:** 5.1.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 02.09.22  
**Update Date:** 11.03.26  

**Script Type:** Flame Main Menu

## Description

Starting point for new Flame Python scripts. Opens a sample PyFlameWindow with entries, menus and buttons, and saves its settings to a config file.
<br><br>
The config sections can be deleted if the new script doesn't need a config file.

## URL

https://logik-portal.com/scripts/script_template

## Menus

- Flame Main Menu → Logik → Logik Portal Script Setup → Script Template

## Installation

Copy script folder into /opt/Autodesk/shared/python
<br><br>
To start a new script from this template:
1. Copy the folder and rename the folder, `script_template.py` and `lib/pyflame_lib_script_template.py` to the new script name.
2. Update the import line to match: `from lib.pyflame_lib_<script_name> import *`
3. Change the header comment, every docstring field, `SCRIPT_NAME`, `SCRIPT_VERSION`, the `ScriptTemplate` class, the `script_template` entry point and the menu name.
4. Replace or delete the sample config settings, and reset `config/config.json`.
5. Update `README.md` to match the new docstring.

---

# User Guide

<!-- user-guide: v5.1.0 11.03.26 -->

This guide is for people writing their own Flame scripts. Script Template doesn't do anything useful on its own: it's a working, minimal script to copy and build on.

## Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [What's in the Folder](#whats-in-the-folder)
- [Starting a New Script](#starting-a-new-script)
- [How the Script Is Laid Out](#how-the-script-is-laid-out)
- [Choosing Where the Menu Appears](#choosing-where-the-menu-appears)
- [Saving Settings With a Config File](#saving-settings-with-a-config-file)
- [Asking the User to Confirm](#asking-the-user-to-confirm)
- [Testing Your Script in Flame](#testing-your-script-in-flame)
- [Before You Share It](#before-you-share-it)
- [Tips, Troubleshooting and FAQ](#tips-troubleshooting-and-faq)

## Overview

Copying Script Template gives a new script:

- the license header and a docstring with every field the Logik Portal reads,
- the standard section layout (`[Imports]`, `[Constants]`, `[Main Script]`, `[Scopes]`, `[Entry Points]`),
- `SCRIPT_NAME`, `SCRIPT_VERSION` and `SCRIPT_PATH` constants,
- an entry point that prints a title in the console and checks the script is installed correctly before doing anything,
- a settings file that is loaded when the script starts and saved when the user clicks **Save**,
- a sample window built with PyFlameLib (entries, a menu, a token menu, Cancel and Save buttons),
- a sample scope function, to show the menu only for certain selections,
- the Flame hook that adds the menu.

Replace the sample window and settings with your own and keep the rest.

## Requirements

- Flame 2025 or newer.
- PyFlameLib, which comes with the template in `lib/`, and the Montserrat fonts in `assets/fonts/` that it needs. Keep both folders in every script made from the template.
- To try the template itself, copy the `script_template` folder into `/opt/Autodesk/shared/python` and rescan Python hooks (or restart Flame). It adds **Flame Main Menu → Logik → Logik Portal Script Setup → Script Template**.

## What's in the Folder

| File or folder | What it is |
| --- | --- |
| `script_template.py` | The script. This is the file you edit. |
| `lib/pyflame_lib_script_template.py` | PyFlameLib, the helper library with the `PyFlame*` widgets and `pyflame.*` functions. Its file name must end with the script's name (see below). |
| `lib/README.md`, `lib/LICENSE` | PyFlameLib's notes and license. |
| `assets/fonts/` | Montserrat fonts used by PyFlameLib windows. |
| `config/config.json` | The saved settings. Created automatically the first time the script runs. |
| `README.md` | This file. |
| `LICENSE` | MIT license. |

## Starting a New Script

The example below makes a script called `my_tool`. Use `snake_case` for the name.

1. **Copy and rename.** Copy the `script_template` folder, then rename the folder, the main script and the library file so all three use the new name:

   ```
   my_tool/
   ├── my_tool.py
   ├── lib/
   │   └── pyflame_lib_my_tool.py
   └── assets/
       └── fonts/
   ```

   Leave out the `__pycache__` folders if the copy has any.

2. **Fix the import line** in `my_tool.py` to match the library's new name:

   ```python
   from lib.pyflame_lib_my_tool import *
   ```

3. **Rename everything else:**
   - the tool name in the header comment at the top of the file,
   - every docstring field (Script Name, Script Version, Flame Version, Written by, the dates, Script Type, Description, URL, Usage, To install, Updates),
   - `SCRIPT_NAME` and `SCRIPT_VERSION` (keep the `v` in `SCRIPT_VERSION`: `'v1.0.0'`),
   - the `ScriptTemplate` class (for example `MyTool`),
   - the `script_template` entry point (for example `my_tool`) and the `'execute'` line in the hook that calls it,
   - the menu `'name'` in the hook.

4. **Replace the sample settings and window.** Change the `setting_01` / `setting_02` config keys to your own, or remove the config code if the script doesn't need saved settings. Delete `config/config.json` from the copy so the new script doesn't start with the template's values; a fresh one is made the first time it runs.

5. **Update `README.md`** to match the new docstring, and start the Updates list again at `v1.0.0`.

A new script usually starts at version `1.0.0`, with one Updates entry: `- Initial release.`

## How the Script Is Laid Out

The file reads top to bottom in this order:

| Part | What it holds |
| --- | --- |
| Header comment | Tool name, copyright and license. |
| Docstring | The script's details. The Logik Portal reads Script Name, Script Version, Flame Version, Written by, Creation Date and Update Date from here, so keep each one as `Label: value` on one line. Dates are `MM.DD.YY`. |
| `[Imports]` | Python modules, `flame`, and PyFlameLib. |
| `[Constants]` | `SCRIPT_NAME`, `SCRIPT_VERSION`, `SCRIPT_PATH` (the script's folder, so files can be found wherever it's installed). |
| `[Main Script]` | The `ScriptTemplate` class: `load_config()` loads the settings, `main_window()` builds the window. Button actions (`save_config`, `close_window`) are small functions inside `main_window()`. |
| `[Scopes]` | `scope_library()`, an example of a function that decides when the menu is shown. |
| `[Entry Points]` | `script_template()`, the function the menu runs, and the Flame hook that adds the menu. |

The entry point always starts the same way:

```python
def my_tool(selection) -> None:

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    MyTool(selection)
```

`selection` is the list of items selected in Flame when the menu was clicked. It's passed on to the class, so the script can work on those items.

## Choosing Where the Menu Appears

The template adds a Flame main menu item with `get_main_menu_custom_ui_actions()`. To put the menu somewhere else, rename the hook function. The `'name'`, `'actions'`, `'execute'` and `'minimumVersion'` keys work the same way in each.

| Menu appears in | Hook function |
| --- | --- |
| Flame main menu | `get_main_menu_custom_ui_actions` |
| Right-click in the Media Panel | `get_media_panel_custom_ui_actions` |
| Right-click in Batch | `get_batch_custom_ui_actions` |
| Right-click in the MediaHub file browser | `get_mediahub_files_custom_ui_actions` |
| Right-click in the Timeline | `get_timeline_custom_ui_actions` |
| Right-click in Action | `get_action_custom_ui_actions` |

A script can have more than one hook, for example a setup window in the main menu and the real action in the Media Panel.

In each action:

- `'execute'` is the entry point to run.
- `'minimumVersion'` is the oldest Flame version that shows the menu. Match it to the docstring's Flame Version.
- `'isVisible'` (optional) is a scope function. It gets the selection and returns `True` to show the menu or `False` to hide it. The template has `scope_library` (shows the menu only when a library is selected) with its `isVisible` line commented out. Uncomment it, or write your own scope, to try it.

## Saving Settings With a Config File

`load_config()` creates a `PyFlameConfig` with default values:

```python
self.settings = PyFlameConfig(
    config_values={
        'setting_01': 'Some value',
        'setting_02': 'Another value',
        },
    )
```

- The settings are stored in `config/config.json` inside the script's folder. The file is created with these defaults the first time the script runs.
- Read a setting as an attribute: `self.settings.setting_01`. The template's entries show their saved settings this way, so the window opens with whatever was saved last.
- Save new values with `self.settings.save_config(config_values={...})`, as `save_config()` in `main_window()` does when **Save** is clicked.
- A setting added later uses its default until it's saved; existing saved values are kept.
- No settings to save? Delete `load_config()`, the call to it in `__init__`, the `save_config(...)` call, and the `text=self.settings...` values in the window. The docstring says this is fine.

## Asking the User to Confirm

`save_config()` in `main_window()` has a commented-out example that asks before going on. A `WARNING` message window returns `True` only when the user clicks **Confirm**:

```python
if not PyFlameMessageWindow(
    message='Overwrite saved settings?',
    message_type=MessageType.WARNING,
    parent=self.window,
    ):
    return
```

Use this before anything that overwrites or deletes something.

## Testing Your Script in Flame

1. Put the script's folder in `/opt/Autodesk/shared/python`.
2. In Flame, rescan Python hooks (or restart Flame). Saved edits are picked up the same way, so you don't need to restart after every change.
3. Run the menu. The console (the shell Flame was started from) shows the title banner and the install check. Errors in your script are printed there too.
4. If the menu doesn't appear, check the console for a Python error when the hooks load, the hook function's name, and `minimumVersion`.

## Before You Share It

- Every docstring field is filled in, and the version and Update Date are current.
- `SCRIPT_VERSION` matches the docstring's Script Version, with a `v` in front.
- The newest change is at the top of the Updates list, in both the docstring and `README.md`.
- The folder name, main script name and `lib/pyflame_lib_<name>.py` all match.
- `config/config.json` doesn't hold your own paths or settings, and no `__pycache__` folders are left in it.
- `LICENSE` and the header comment have the right name and year.

## Tips, Troubleshooting and FAQ

**"Script install path is incorrect" when I run the menu.**
The script folder's name doesn't match the end of the library file's name (`lib/pyflame_lib_<name>.py`). The script stops before doing anything. Rename the folder or the library file so they match. The message shows the path the folder should have.

**"Script folder is not writable".**
The install check also needs write access to the script's folder (the config file is saved there). Fix the folder's permissions.

**`ModuleNotFoundError: No module named 'lib.pyflame_lib_...'`.**
The import line doesn't match the library file's name. See step 2 of [Starting a New Script](#starting-a-new-script).

**Two scripts' menus get mixed up, or one script's change breaks another.**
Each script needs its own folder name, main script name and library file name. Every script imports its library as `lib.pyflame_lib_<name>`, so two scripts with the same library file name share one loaded copy, and two main scripts with the same file name clash when Flame loads them.

**Where do I find the widgets I can use?**
PyFlameLib's widgets (`PyFlameWindow`, `PyFlameLabel`, `PyFlameEntry`, `PyFlameMenu`, `PyFlameTokenMenu`, `PyFlameButton`, `PyFlameMessageWindow` and many more) are documented in the docstrings in `lib/pyflame_lib_<name>.py`.

**Should I update the library in an older script?**
Only on purpose. Each script keeps its own copy so one script's library update can't break another. Test the script after replacing its copy.

---

## Updates

### v5.1.0 [11.03.26]
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
- Second entry now shows its saved setting instead of starting empty.
- Closed the `<small>` tag in the window title.
- Added a module-level entry point and an [Entry Points] section. The menu now calls the entry point.
- Docstrings, imports and sections now follow the style guide.
<br>

### v5.0.1 [12.18.25]
- Added license to script.
<br>

### v5.0.0 [08.27.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v4.1.0 [04.13.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v4.0.0 [12.29.24]
- Updated to PyFlameLib v4.0.0.
- Removed script path checking method. This is now handled by PyFlameLib: pyflame.verify_script_install().
- PyFlameWindow now creates a PyFlameGridLayout by default that widgets can be added to. This should simplify the process of adding widgets to the window. Number of rows and columns in the grid layout can be set using the grid_layout_columns and grid_layout_rows arguments in the PyFlameWindow constructor. Overall and individual row height and column width can also be set from the PyFlameWindow constructor. Check PyFlameWindow docstring for more information.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v3.1.1 [04.18.24]
- Replaced QGridLayout with PyFlameGridLayout.
- Moved checking of script path and creating/loading of config to their own functions.
<br>

### v3.1.0 [02.07.24]
- Updates to UI/PySide.
- Updated script versioning to semantic versioning.
<br>

### v3.0 [08.10.23]
- Updated for pyflame lib v2.0.0.
