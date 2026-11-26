# PyFlame Widget Tester

A standalone PySide6 app, run outside Flame, that shows every `PyFlame*` class in a PyFlameLib file so you can try its widgets before testing in Flame. The settings, properties and methods panels are built from the library itself, so new widgets and new arguments appear without changing the app.

File: `pyflame_widget_tester.py` (v1.0.0). Importing it does nothing: all work runs under `if __name__ == '__main__':`, and it defines no Flame hooks.

## Running it

You need a `python3` that has PySide6. Flame's own is the easiest:

```
/opt/Autodesk/python/2027.2/bin/python3 -B pyflame_widget_tester.py
```

Tested offscreen on macOS with:

- `/opt/Autodesk/python/2027.2/bin/python3`: Python 3.13.3, PySide6 6.8.3 (Flame 2027.x).
- `/opt/Autodesk/python/2026.2.4/bin/python3`: Python 3.11.5, PySide6 6.5.2 (Flame 2025.x/2026.x).

Not tested on screen by a person yet. Homebrew's `python3` has no PySide6, so it can't run the app. Run it with `python3 -B` so no `__pycache__` is written next to it (this folder is in Flame's hook path).

Options:

| Option | What it does |
| --- | --- |
| `--lib PATH` | Library file to load. Default: `../pyflame_lib.py` (the shared library, found from the app's own folder). Use it to try a scratch copy before it's applied. |
| `--self-test` | Agent mode: test every class without a human, print a report, exit 0 (all passed) or 1. |
| `--grab DIR` | With `--self-test`: save a PNG of each preview (or window) to `DIR`. |
| `--only NAMES` | With `--self-test`: test only these classes (comma-separated). |
| `--screenshot DIR` | Save a PNG of the whole app window to `DIR`, once per class in `--select`, then exit. |
| `--select NAMES` | With `--screenshot`: classes to select (comma-separated). |

`--self-test` and `--screenshot` use the offscreen platform automatically when `QT_QPA_PLATFORM` isn't set, so nothing appears on screen.

## The window

- **Left: widget list.** Every `PyFlame*` class in the loaded library, in file order. Window classes are marked `(window)`. Classes the app didn't know about when it was written are marked `(new)` and get the same generic handling.
- **Centre: preview.** The selected widget, built from the current settings, on a Flame-like dark background. Arguments that need another widget (a token menu's destination entry, a tooltip's target, a button group's buttons) get one built for them and shown in the preview too. Layout classes are shown in a host widget with four sample buttons. Objects that aren't widgets (`PyFlameConfig`, `PyFlameButtonGroup`, `PyFlameToolTip`) are listed with a note; use the Properties and Methods tabs on them.
- **Window classes** (`PyFlameWindow`, `PyFlameMessageWindow`, `PyFlameOptionWindow`, `PyFlameInputDialog`, `PyFlamePasswordWindow`, `PyFlameProgressWindow`) aren't built on selection, because most of them block until closed. Press **Open**. When the window closes, its result (`confirmed`, `selected`, `text`, `username`, and the password's length only) goes to the log. **Close Open Windows** closes non-modal ones (`PyFlameWindow`, `PyFlameProgressWindow`). A plain `PyFlameWindow` gets a label and a Close button so it can be closed.
- **Drop target** (below the preview). Accepts any drag and logs the source widget's class, its `currentItem()` text, the mime formats and text, and the drop action. It takes a copy when the drag allows one, so a dragged item isn't removed from its widget. Use it with `draggable` / `drag_end_connect` on the tree and list widgets.
- **Bottom: log.** Every callback call with its arguments, property get/set, method call, drop, library print, and error (with traceback). Exceptions raised in Qt slots (library callbacks, paint events) are logged too. **Clear** empties it.
- **Status bar.** Library path, its `Version:` line, and the font family in use (Montserrat when the fonts were found). The window title has the file name and version too.

### Right: Constructor tab

One editor per constructor argument, from the class's `__init__` signature and type hints:

| Type | Editor |
| --- | --- |
| `bool` | Checkbox |
| `int` | Spin box |
| `float`, `int \| float` | Decimal spin box |
| `str` | Text field |
| Enum (`Color`, `Style`, `Align`, ...) | Menu of the enum's members |
| Callable | **connect to log**: passes a function that logs each call and its arguments |
| A widget (`parent`, `QWidget`, `PyFlameEntry`, ...) | Menu: None, tester window, preview area, new PyFlameButton / PyFlameEntry (in the Properties tab also **current widget**, preselected when the property holds one) |
| Anything else (lists, dicts, unions) | A small text box that takes a Python literal |

- Optional values (`X | None`, or a `None` default) get a **None** checkbox, or a `None` menu item for enums.
- Literal boxes accept plain literals plus the library's enum members (`{1: {'text': 'Ok', 'color': Color.BLUE}}`). Nothing else is evaluated: no calls, no other names.
- For Callable types inside a literal, the text `'log'` becomes a logging function. For example `context_menu` takes `{'Rename': 'log', 'Delete': 'log'}`, and choosing **Rename** logs `PyFlameTreeWidget.context_menu['Rename']()`.
- Required arguments are marked `*`. Hover a label for its type hint, library default and editor kind.
- **Reset (Library Defaults)** puts the library's defaults back. Required arguments, which have no default, keep their sample value.
- **Sample Data** fills in useful values where the default would be empty: tree data, list items, menu options, tokens, a CSV table, slider range, text, and small generated images. It also connects every Callable to the log. A class gets sample data when it's selected.
- **Rebuild** builds the widget again (it says **Open** for window classes). **Auto-rebuild on change** rebuilds shortly after any edit; it never opens window classes.
- An argument the library rejects, or a constructor that raises, is logged with its traceback. The app doesn't crash. A literal box that can't be read turns red, and its tooltip says why.

### Right: Properties tab

Every Python property on the class and its library base classes, with its current value, an editor (same kinds as above, from the setter's type hint), **Set** and **Get**. Read-only properties are marked and can only be read. **Get All** reads every property again. Setting a value goes to the live widget without rebuilding it, then reads the value back.

Modal window classes are deleted when they close, so most of their properties can't be read after Open returns. The self-test checks them while the window is open.

### Right: Methods tab

The public methods defined in the library class and its library bases. Qt event-handler and paint overrides (`*Event`, `eventFilter`, `drawRow`, `drawBranches`, ...) are left out, because they can't be called with literal arguments. Select one to see its signature, type the arguments as in a call (`'New Item', column=1`), then press **Call** or Enter. The result or exception goes to the log, and the properties are read again afterwards. `'log'` works for Callable parameters here too.

## Self-test (agent mode)

```
QT_QPA_PLATFORM=offscreen /opt/Autodesk/python/2027.2/bin/python3 -B pyflame_widget_tester.py --self-test [--lib PATH] [--grab DIR] [--only NAMES]
```

Each class is tested in its own child process (with `-B`), and all of them share the run's one temp folder. A class that takes more than 120 seconds fails with `timed out`, with no retry. Per class:

1. Build with the library defaults.
2. Build with each bool argument flipped (on top of sample data).
3. Build with each member of each enum argument. Many arguments only accept some colours or styles, so a value refused by one of the library's own argument checks counts as "rejected" (a note), not as a failure. Any other constructor error (for example a crash in a paint event during `exec_()`) is a failure.
4. Build with sample data. This instance is grabbed (`--grab`) and used for step 5.
5. Read every property and set each settable one back to its own value (bools are flipped, then set back). Modal windows are tested while they're open. If the sample build failed, the properties are tested on a library-defaults build instead.

A setter that refuses `None` on purpose counts as a note, not a failure, for example `PyFlameImageGallery.rows` in columns mode.

"On purpose" means the same thing for constructors and setters: a `TypeError`, `ValueError` or `RuntimeError` raised by `pyflame.raise_type_error` / `raise_value_error`, or by an explicit `raise` statement in the library (for a setter: in that setter itself). Errors that only happen to be a `TypeError` or `ValueError` (a Qt binding error, a failed `int()` in a paint event) are failures. Every note is printed on its own line, so a wrongly filed error can be seen.

Modal windows are closed automatically. Exceptions raised in Qt slots or paint events count as failures, listed once with a count. If a variant crashes the process (a segfault in the library), it's reported as `process crashed (exit -11)` and the class runs again without that variant. Library output is captured and shown (last 6 lines) only for failing classes.

Example report lines:

```
PASS PyFlameButton: 34 builds, 8 properties, 28 notes
    note: rejected [color=Color.YELLOW] ValueError: PyFlameButton: Expected 'color' to be Color Enum: Color.GRAY, Color.BLUE, Color.RED, got Color.YELLOW instead.
    ...
```

## Safety

- **No sudo.** Any `subprocess` command that runs `sudo` is blocked in the app's process. `PyFlamePasswordWindow`'s password test is replaced in memory, so **Confirm** accepts the typed password without testing it. The password is never logged (only its length). The library file isn't changed.
- **Temp files only.** The library's `SCRIPT_PATH` points at a new temp folder (one per run; self-test children share it) (`<system temp>/pyflame_widget_tester_*/pyflame_widget_tester`), so anything the library writes under its script path (config, temp folders) lands there. `PyFlameConfig`'s sample `config_path` is in that temp folder too. Sample images and the CSV are generated there. The app never deletes the temp folder; the system's temp cleanup does.
- **Fonts aren't copied.** The temp folder gets a symlink, `assets/fonts`, to the real fonts: next to the library file, in its script folder (`<script>/assets/fonts` for `<script>/lib/<file>`), or else `_pyflame_lib/assets/fonts`.
- **No Flame.** A fake `flame` module is installed first: the shared stubs (`_claude_python/stubs/stub_loader.py`) when they're there, else a tiny local fake with only `get_version()` and a do-nothing `messages.show_in_console()`. The real Flame session is never touched.
- **No bytecode.** `sys.dont_write_bytecode` is set, so no `__pycache__` lands next to the library or the stubs.
- **File browsers only open when you click.** The self-test never opens one.
