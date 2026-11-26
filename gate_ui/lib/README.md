# PyFlame Library

https://logik-portal.com/pyflame

Python library for Autodesk Flame providing PyQt widgets styled to
match Flame’s UI and utility functions that streamline script development.

**Version:** 5.6.0<br>
**Creation Date:** 10.31.20<br>
**Update Date:** 11.23.26<br>
**Written By:** Michael Vaglienty<br>
**License:** MIT License (MIT) - see LICENSE file for details<br>

## Compatibility

**Python:** 3.11 - 3.13<br>
**Qt binding:** PySide6 (Pyside2 no longer supported)<br>
**Autodesk Flame:** 2025.2+<br>

## Usage

**Required script folder structure when using this library:**

```
script_folder/
├── main_script.py
├── lib/
│   └── pyflame_lib_<main_script_name>.py
│   └── README.md (This file) - Optional file, not required.
│   └── CHANGELOG.md - Optional file, not required.
├── assets/
│   └── fonts/
│       └── Montserrat-Regular.ttf
│       └── Montserrat-Light.ttf
│       └── Montserrat-Thin.ttf
```

- Required Files:
    - Montserrat-Regular.ttf
    - Montserrat-Light.ttf
    - Montserrat-Thin.ttf
    - pyflame_lib_<main_script_name>.py

To avoid conflicts with having multiple copies within the Flame python folder, this file should be renamed to: pyflame_lib_<script_name>.py

**Import the library in your script:**

```python
from lib.pyflame_lib_<main_script_name> import *
```

This makes all classes, functions and constants from the library directly available in the script's namespace.

**Examples:**

To utilize PyFlameFunctions, access methods through pyflame:

- `pyflame.print("Flame")`
- `flame_version = pyflame.get_flame_version()`

To utilize widgets, instantiate them directly by their class names:

- `window = PyFlameWindow()`
- `button = PyFlamePushButton()`
- `menu = PyFlameMenu()`

## PyFlame Custom QT Widget Classes

- `PyFlameButton` - Custom QT Flame Button
- `PyFlameCheckBox` - Custom QT Flame Check Box Widget.
- `PyFlameEntry` - Custom QT Flame Entry Field Widget. Replaces PyFlameLineEdit.
- `PyFlameEntryBrowser` - Custom QT Entry Field Widget that opens Flame File Browser when clicked.
- `PyFlameImageWidget` - Custom QT Flame Image Widget. Shows a scaled image in a bordered frame, with an optional info bar.
- `PyFlameImageGallery` - Custom QT Flame Image Gallery Widget. Scrollable grid of the images in a folder.
- `PyFlameLabel` - Custom QT Flame Label Widget.
- `PyFlameListWidget` - Custom QT Flame List Widget.
- `PyFlamePushButton` - Custom QT Flame Push Button.
- `PyFlameMenu` - Custom QT Flame Menu - Replaces `PyFlamePushButtonMenu`
- `PyFlameColorMenu` - Custom QT Flame Push Button with Color Menu. - Replaces `PyFlamePushButtonColorMenu`
- `PyFlameTokenMenu` - Custom QT Flame Token Menu. - Replaces `PyFlameTokenPushButton`
- `PyFlameSlider` - Custom QT Flame Numerical Slider.
- `PyFlameTable` - Custom QT Flame Table Widget.
- `PyFlameTabWidget` - Custom QT Flame Tab Widget.
- `PyFlameTextEdit` - Custom QT Flame Text Edit Widget.
- `PyFlameTextBrowser` - Custom QT Flame Text Browser Widget.
- `PyFlameTreeWidget` - Custom QT Flame Tree Widget.

- `PyFlameButtonGroup` - Custom QT Flame Button Group. Allows for groupings of PyFlameButton types(PyFlameButton, PyFlamePushButton...).
- `PyFlameCheckBoxGroup` - Custom QT Flame Check Box Group. Groups PyFlameCheckBox widgets and sets the fewest and most that can be checked.
- `PyFlameProgressBarWidget` - Custom QT Flame Progress Bar Widget.
- `PyFlameHorizontalLine` - Custom QT Horizontal Line Widget.
- `PyFlameVerticalLine` - Custom QT Vertical Line Widget.
- `PyFlameToolTip` - Custom QT Tooltip for PyFlame widgets.

## PyFlame QT Layout Classes

- `PyFlameGridLayout` - Custom QT Grid Layout.
- `PyFlameHBoxLayout` - Custom QT Horizontal Box Layout.
- `PyFlameVBoxLayout` - Custom QT Vertical Box Layout.

## PyFlame QT Window Classes

- `PyFlameWindow` - Flame QT Window
- `PyFlameMessageWindow` - Flame Message Window
- `PyFlameOptionWindow` - Flame Option Window. Shows a message with up to four user-defined buttons.
- `PyFlamePasswordWindow` - Flame Password Window
- `PyFlameProgressWindow` - Flame Progress Window
- `PyFlameInputDialog` - Flame QT Input Dialog Window
- `PyFlameHelpWindow` - Flame Help Window. Shows a Markdown file, such as a script's README.md, fully rendered. Added in v5.6.0.

## Utility Classes

- `PyFlameConfig` - Class for creating, loading, and saving config files.

## Option Classes (Enums)

- `Color` - Color values used in the PyFlame UI elements.
- `TextColor` - Color options for text printed to the terminal.
- `Style` - PyFlameLabel style options.
- `Align` - Text alignment options.
- `MessageType` - PyFlameMessageWindow types.
- `PrintType` - pyflame.print types.
- `BrowserType` - PyFlameEntryBrowser browser type options.
- `TextStyle` - PyFlameTextEdit and PyFlameTextBrowser text style options.
- `TextType` - PyFlameTextEdit and PyFlameTextBrowser text type options.

## PyFlame Functions

- `pyflame.copy_to_clipboard` - Copy text to clipboard using QT.
- `pyflame.copy_to_shot_folder` - Copy a clip, batch group or desktop to a shot folder in the Media Panel.
- `pyflame.create_file_system_folders` - Create a folder in the file system based on the provided folder structure.
- `pyflame.create_file_system_folder` - Create a single folder in the file system. Tokens can be used in folder names.
- `pyflame.create_media_panel_folders` - Create a folder in the media panel based on the provided folder structure.
- `pyflame.create_media_panel_folder` - Create a single folder in the media panel. Tokens can be used in folder names.
- `pyflame.create_media_panel_libraries` - Create libraries with folders in the media panel based on the provided folder structure.
- `pyflame.create_temp_folder` - Create a temporary folder in the script folder.
- `pyflame.cleanup_temp_folder` - Clear the contents of the temporary folder.
- `pyflame.cursor_busy` - Set the cursor to the busy cursor.
- `pyflame.cursor_restore` - Restore the cursor after `pyflame.cursor_busy`.
- `pyflame.convert_export_preset_name_to_path` - Convert export preset name to path.
- `pyflame.file_browser` - Flame file browser or QT file browser window.
- `pyflame.find_by_tag` - Search through a Flame object's contained objects by tags.
- `pyflame.font_resize` - Resize font size for all PyFlame widgets for different screen resolutions. - Not intended to be used outside of this file.
- `pyflame.generate_unique_node_names` - Generate unique node names based on a list of existing node names.
- `pyflame.generate_unique_name` - Generate a unique name that does not conflict with a list of existing names.
- `pyflame.get_export_preset_names` - Get export preset names from Shared and Project paths. User paths are not checked.
- `pyflame.get_export_preset_version` - Get export preset version.
- `pyflame.get_flame_python_packages_path` - Get path to Flame python packages folder.
- `pyflame.get_flame_version` - Get version of Flame.
- `pyflame.get_media_panel_shot_folder` - Find a Media Panel shot folder from a path.
- `pyflame.gui_resize` - Resize PyFlame widgets for different screen resolutions. - Not intended to be used outside of this file.
- `pyflame.iterate_name` - Iterate through a list of names and return a unique name based on the list.
- `pyflame.move_to_shot_folder` - Move a clip to a shot folder in the Media Panel.
- `pyflame.open_in_finder` - Open path in System Finder.
- `pyflame.pause` - Pause QT for a brief time so the window UI can update.
- `pyflame.python_package_local_install` - Install python packages bundled with script.
- `pyflame.print` - Print a message to the terminal and Flame message area.
- `pyflame.print_dict` - Cleanly print nested dictionaries with indentation to the terminal.
- `pyflame.print_json` - Cleanly print JSON data to terminal with proper indentation for easy readability.
- `pyflame.print_list` - Print a list of items to the terminal and Flame message area.
- `pyflame.print_title` - Prints title of script to terminal.
- `pyflame.raise_type_error` - Raise a type error. Print error message with traceback to Flame message area and terminal.
- `pyflame.raise_value_error` - Raise a value error. Print error message with traceback to Flame message area and terminal.
- `pyflame.refresh_hooks` - Refresh Flame python hooks.
- `pyflame.resolve_shot_name` - Resolve shot name from string.
- `pyflame.resolve_tokens` - Resolve strings containing tokens.
- `pyflame.set_shot_tagging` - Tag Flame objects with shot name tag (ShotName: <shot_name>).
- `pyflame.shot_name_from_batch_group` - Get shot name from batch group.
- `pyflame.shot_name_from_clip` - Get shot name from clip.
- `pyflame.untar` - Untar a tar file.
- `pyflame.update_export_preset` - Update export preset version.
- `pyflame.verify_script_install` - Verify that script is installed in the correct location with any additional files that are required.
- `pyflame.window_resolution` - Get the main window resolution.

## Updates

See CHANGELOG for full listing of updates [CHANGELOG.md](CHANGELOG.md).

---

## License

This project is licensed under the **MIT License (MIT)**. See the [LICENSE](LICENSE) file for details.

## Support

For issues please include your Flame version, OS, Python version, and a minimal reproducible example when reporting bugs.
