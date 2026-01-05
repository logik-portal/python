# PyFlame Library Changelog

All notable changes to this project will be documented in this file.

https://github.com/logik-portal/pyflame

## v5.2.0 [01.04.26]

### Updates/Fixes

- **Widgets**
    - `PyFlameLabel`
        - **Fixed**
            - `Enabled` argument wasn't working.
    - `PyFlameTabWidget`
        - **Fixed**
            - Widget wasn't properly spanning in gridlayout. This caused windows to not be sized properly.
            - Changed `enable` argument to `enabled` to be consistent with other widgets

- **Windows**
    - `PyFlameWindow`
        - **Fixed**
            - Window centering
        - **New Argument**
            - `message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: True)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameInputWindow`
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameMessageWindow`
        - Added properties to docstring.
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlamePasswordWindow`
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.

    - `PyFlameProgressWindow`
        - Simplified arguments/properties.
        - **Fixed**
            - Added missing docstrings to properties.
        - **New Argument**
            -`message_bar`
                - Add message bar area to bottom of windows. Used to display short messages.
                  (Default: False)
        - **New Property**
            - `message_bar_text`
                - Use to set or get message bar text.
        - **New Methods**
            -`text_append`
                - Appends text to the currently displayed message
            -`pause`
                - Adds a delay in seconds to allow the UI time to refresh before moving on the the next operation.
            -`tasks_completed`
                - Sets completed state of progress window after tasks are done.
            -`enable_done_button`
                - Enabled the Done button.

## v5.1.1 [12.16.25]

### Updates/Fixes

- **Widgets**
    - `PyFlameProgressWindow`
        - **Misc Fixes**

## v5.1.0 [12.05.25]

### Added

- **PyFlameFunctions**
    - `pyflame.python_package_local_install`
        - New function to install python packages locally bundled with a script.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Methods**
            - `add_item_with_columns`
                - Add a new item to a tree with tree column entries.
            - `color_item`
                - Color item in tree.
            - `set_fixed_column_headers`
                - Set all tree column headers to a fixed length

## v5.0.0 [09.03.25]

**Major Rewrite of PyFlame Library**

This update will break most scripts using this library.

### New Features

- All widgets now have properties to simplify things and provide more consistency and commonality between all widgets.
  Previous widget arguments and methods may not longer work as expected.
  All new properties/methods are documented in the docstring of each widget.

### Added

- **Widgets**
    - `PyFlameProgressBarWidget` -
        - Progress bar widget to show progress of tasks

    - `PyFlameTextBrowser`
        - Text widget for displaying text with hyperlinks.
        - Has ability to display html, markdown, and plain text.

- **PyFlameFunctions**
    - pyflame.get_media_panel_shot_folder

    - pyflame.move_to_shot_folder

    - pyflame.copy_to_shot_folder

### Updates/Fixes

- **Widgets**
    - `PyFlamePushButton`
        - **New Methods**
            - `connect`
                - Connect a function to button press.
        - Argument changed: `button_checked` -> `checked`
        - instead of button.isChecked() to get checked state, use button.checked
        - instead of button.isEnabled() use button.enabled to get enabled state

    - `PyFlameTextEdit`
        - Added ability to display text as html, markdown, and plain text.

    - `PyFlameListWidget`
        - **New methods**
            - `replace_items` - Replaces all items in list with new list of items.

    - `PyFlameSlider`
        -Removed `use_float` argument. Whether the Slider is float or int is taken from min/max values.
        -Calculator window now closes when user clicks outside calculator window.

    - Renamed Widgets
        - `PyFlamePushButtonMenu` -> `PyFlameMenu`
        - `PyFlamePushButtonColorMenu` -> `PyFlameColorMenu`
        - `PyFlameTokenPushButton` -> `PyFlameTokenMenu`

- **Windows**
    - `PyFlameDialogWindow`
        - Class has been removed. Use `PyFlameWindow` instead.

    - `PyFlameWindow`
        - Now uses QDialog instead of QWidget.
        - **New Arguments**
            - `enter_pressed`
                -  Function to call when enter/return key is pressed on keyboard.
            - `escape_pressed`
                - Function to call when escape button is pressed on keyboard.

    - `PyFlameInputDialog`
        - **New Property**
            - `text`
                - Get or set input entry text.
        - **Returns**
            Ok - Input text string
            Cancel - None

### Misc

- Removed Support for PySide2.

- Removed: `max_width` and `max_height` arguments from all widgets.

- `PyFlameToolTip`
    - New class for adding tooltips to pyflame widgets. Not intended to be used directly.
    - Added delay and duration arguments. These can be used to set the delay and duration of the tooltip.

## v4.3.1 [04.16.25]

### Fixed

- **Widgets**
    - `PyFlameEntryBrowser` – Error when setting `connect=None`

## v4.3.0 [03.16.25]

### Added

- **Widgets**
    - `PyFlameTable`
        - A table widget that allows for displaying and interacting with tabular data such as CSV files.

    - `PyFlameTabWidget`
        - Creates a tab widget inside of a window that other widgets can be places inside of.

- **PyFlameFunctions**
  - `pyflame.print_title`
    - Prints title and version of script to terminal.

- **Windows**
    - `PyFlameInputDialog`
        - A simple dialog window that allows for input of a single line of text.

### Updates/Fixes

- **Widgets**
    - `PyFlameButton`
        - **New Arguments**
            - `max_height`
                - Set PyFlameButton to maximum height. Use if height is being set by layout. Overrides `height` if set to True.

    - `PyFlameEntry`
        - **New Methods**
            - `text_changed(connected_function: Callable)`:
                - Calls a function when the text in the entry field changes.

    - `PyFlameSlider`
        - Updated Calculator UI

    - `PyFlameTextEdit`
        - **New Arguments**
            - `text_type`
                - Set type of text being added using TextType enum. TextType.PLAIN, TextType.MARKDOWN, TextType.HTML.

    - `PyFlameColorPushButtonMenu`
        - **New Methods**
            - `get_color`
                - Return selected color name.
            - `get_color_value`
                - Return normalized RGB color value of selected color.
            - `set_color`
                - Set the color of the `PyFlameColorPushButtonMenu`.

        - `No Color` option added to default color menu. This either applies no color or clears the current color.

- **Windows**
    - `PyFlameWindow`/`PyFlameDialogWindow`
        - **New Methods**
            - `set_title_text`
                - Set the title of the window.

### Misc

- Added new file structure for libraries and assets.
    ```
    script_folder/
    ├── main_script.py
    ├── lib/
    │   └── pyflame_lib_<main_script_name>.py
    ├── assets/
    │   └── fonts/
    │       └── Montserrat-Regular.ttf
    │       └── Montserrat-Light.ttf
    ```

- To import the library in a script, use:
    `from lib.pyflame_lib_<main_script_name> import *`

## v4.2.0 [02.19.25]

### Added

- **Widgets**
    - `PyFlameEntryFileBrowser`
        - Replaces PyFlameLineEditFileBrowser which is now deprecated.

- **PyFlame Functions**
    - `pyflame.raise_type_error`
        - Raise a type error. Print error message with traceback to Flame message area and terminal.

    - `pyflame.raise_value_error`
        - Raise a value error. Print error message with traceback to Flame message area and terminal.

    - `create_temp_folder`
        - Create a temporary folder in the script folder.

    - `cleanup_temp_folder`
        - Clear the contents of the temporary folder.

### Updates/Fixes

- **Widgets**
    - `PyFlameEntry`
        - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.
        - Added Alt+Click to show full entry text as tooltip. Also copies full entry text to clipboard.

    - PyFlameLabel
        - **New Style Option**
            - `Style.BACKGROUND_THIN`
                - Adds a darker background to the Label with a thinner font weight. Text is left aligned by default. Used for window titles.

    - `PyFlameListWidget`
        - **New Arguments**
            - `items`
                - A list of items to add to the list widget can now be provided on creation of the widget.

    - `PyFlamePushButton`
        - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.

    - `PyFlameTextEdit`
        - **New Arguments**
            - `text_type`
                - Type of text being input. `TextType.PLAIN`, `TextType.MARKDOWN`, `TextType.HTML`

- **Windows**
    - `PyFlameWindow`/`PyFlameDialogWindow`
        - Fixed: Line colors not properly being applied to side of window.
        - **New Arguments**
            - `title_style`
                - Set style of title line in window. Use Style Enum to set style.
            - `parent`
                - Set parent of window.

### Deprecated

    - PyFlameLineEditFileBrowser
        - Use PyFlameFileBrowser instead.

    - LineColor Enum. All colors are now set using the Color Enum.

### Misc

- Updated font used for widgets. Montserrat Regular is now the default font for all QT widgets. The Discreet font is used
as a fallback if Montserrat is not found. Font location: `<SCRIPT_FOLDER>/assets/fonts`

- PyFlame Widget Argument Validation
    - Argument errors now print to Flame message area as well as terminal.

## v4.1.0 [01.15.25]

### Added

- **Widgets**
    - `PyFlameHorizontalLine`
        - A horizontal line widget.
    - `PyFlameVerticalLine`
        - A vertical line widget.

## v4.0.0 [01.05.25]

### Added

- **Widgets**
    - `PyFlameEntry`
        - Replaces `PyFlameLineEdit` which has been deprecated.
        - **New Arguments**
            - `align`
                - Align entry text to left, right, or center. Default is left.


- **PyFlameFunctions**
    - `create_media_panel_library`
        - Create a library with folders in the media panel based on the provided folder structure.

    - `create_media_panel_folder`
        - Create a single folder in the media panel based on the provided folder structure.

    - `create_media_panel_folders`
        - Create folders in the media panel from a list of folder names and a folder structure.

    - `create_file_system_folder`
        - Create a single folder in the file system based on the provided folder structure.

    - `create_file_system_folders`
        - Create folders from a list of folder names and a folder structure.

    - `print`
        - Print a message to the terminal and Flame message area. Replaces message_print function which has been deprecated.

    - `print_dict`
        - Cleanly print nested dictionaries with indentation to the terminal.

    - `print_json`
        - Cleanly print JSON data to terminal with proper indentation for easy readability.

    - `set_shot_tagging`
        - Tag Flame objects with shot name tag (ShotName: <shot_name>).

    - `verify_script_install`
        - Verify that script is installed in the correct location with any additional files that are required.

    - `find_by_tag`
        - Search through a Flame object's contained objects by tags.

    - `shot_name_from_clip`
        - Get shot name from clip.

    - `move_to_shot_folder`
        - Move a clip to a shot folder in the Media Panel.

    - `get_export_preset_names`
        - Get export preset names from Shared and Project paths. User paths are not checked.

    - `convert_export_preset_name_to_path`
        - Convert export preset name to path.

### Updates/Fixes

- **Widgets**
    - `PyFlameTextEdit`
        -`read-only` background color now matches read-only background color of PyFlameEntry for consistency.

    - `PyFlameTreeWidget`
        - **New Arguments**
            - `top_level_editable`
                - Allow editing of name of top level items in the tree. Default is False.
            - `tree_list`
                - List of items to populate the tree. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            - `tree_list_no_root`
                - List of items to populate the tree excluding the root item. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            - `update_callback`
                - Function to call when an item is edited, inserted, or deleted.

        - **New Attributes**
            - `selected_item`
                - Return the text of the currently selected item.
            - `item_path`
                - Return the recursive path of the currently selected item.
            - `item_paths`
                - Return the recursive paths of the currently selected items.
            - `all_item_paths`
                - Return the recursive paths of all items in the PyFlameTreeWidget.

    - `PyFlameGridLayout`
        - Added the ability to set the number of columns and rows in the grid to make it easier to place widgets especially where space is desired between widgets.
        By default the unit size of the grid is 150px wide and 28px high. The size of a normal button. The width and height of each grid unit along with the
        number of columns and rows can be adjusted using setGridSize method.
        - **New Arguments**
            - `columns`
                - Set number of columns in the grid. Default is 0.
            - `rows`
                - Set number of rows in the grid. Default is 0.
            - `column_width`
                - Set width of each column in the grid. Default is 150.
            - `row_height`
                - Set height of each row in the grid. Default is 28.
            - `adjust_column_widths`
                - Set width of specific columns in the grid. Default is {}.
            - `adjust_row_heights`
                - Set height of specific rows in the grid. Default is {}.

        - **New Methods**
            - `setGridSize`
                - Configure the grid layout dimensions and cell sizes. This method allows you to:
                - Set the number of columns and rows in the grid
                - Define the width of each column (in pixels)
                - Define the height of each row (in pixels)
                - Automatically adjust spacing between grid cells

        - **Arguments Removed**
            - `setMinimumColumnWidth`
                - No longer needed.
            - `setMinimumRowHeight`
                - No longer needed.


- **PyFlameFunctions**
    - `pyflame.copy_to_clipboard`
        - Type hinting made compatible with Flame 2024.

    - pyflame.generate_unique_node_names
        - Fixed: Would not properly generate a new name if the first character of the new name was a number.

    - pyflame.resolve_tokens
        - Batch groups are now checked for a ShotName tag(ShotName:<shot_name>). If found, it is used to resolve the shot name token.

- **Windows**

- `PyFlameWindow`/`PyFlameDialogWindow`
    - Simplified window creation by adding PyFlameGridLayout to the window by default with optional
        arguments to set the number of columns and rows along with column and row widths. This can
        be overridden by passing grid_layout=False.

    - **New Arguments**
        - `tab_width`
            - Set the width of tab name label
        - `tab_height`
            - Set the height of the tab name label
        - `grid_layout`
            - Set to True to use the default grid layout. Default is True.
        - `grid_layout_columns`
            - Set the number of columns in the grid layout. Default is 4.
        - `grid_layout_rows`
            - Set the number of rows in the grid layout. Default is 3.
        - `grid_layout_column_width`
            - Set the width of each column in the grid layout. Default is 150.
        - `grid_layout_row_height`
            - Set the height of each row in the grid layout. Default is 28.
        - `grid_layout_adjust_column_widths`
            - Set the width of specific columns in the grid layout. Default is {}.
        - `grid_layout_adjust_row_heights`
            - Set the height of specific rows in the grid layout. Default is {}.

- `PyFlameMessageWindow`
    - Updated message printing to terminal to be more clear.
    - Message text no longer uses html tags. Text is now printed as plain text.

- `PyFlameProgressWindow`
    - Updated message printing to terminal to be more clear.

### Deprecated

- **Widgets**
    - `PyFlameLineEdit`
        - Use PyFlameEntry instead.

    - `PyFlameLabel.Style.BACKGROUND`
        - Use PyFlameEntry with read_only=True instead.

- **PyFlameFunctions**
    - `pyflame.message_print`
        - Use pyflame.print instead.

    - `pyflame.resolve_path_tokens`
        - Use pyflame.resolve_tokens instead.

### Misc
    - `max_width` argument is now set to True by default for all widgets. width and height are now bypassed. This means the widgets will now expand to fill the available space. The size of the widgets is now determined by the layout(PyFlameGridLayout, PyFlameHBoxLayout, PyFlameVBoxLayout). To override this behavior, set max_width to False and set width and height arguments to set the size of the widget.

    - `max_height` argument is now set to True by default on the following widgets. The above behavior for `max_width` applies to max_height in these widgets:
        - PyFlameListWidget
        - PyFlameTreeWidget
        - PyFlameTextEdit

## v3.2.0 [09.09.24]

### Added

- **PyFlame Functions**
    - `pyflame.json_print`
        - Cleanly print JSON data to terminal with proper indentation for easy readability.

## v3.1.0 [09.01.24]

### Added

- **PyFlame Functions**
    - `pyflame.print_list`
        -  Print a list of items to the terminal and Flame message area.
    - `pyflame.print`
        - Print a message to the terminal and Flame message area.

### Updates/Fixes

- **Windows**
    - `PyFlameMessageWindow`
        - Added scrollbars to message window for long messages.

## v3.0.0 [08.16.24]

### Added

- **PyFlame Functions**
    - `pyflame.copy_to_clipboard`
        - Copy text to clipboard using QT.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - Fixed font size issue in linux.
        - When sorting is enabled, sorting is done in ascending order of items in column 0.

- **Config**
    - `PyFlameConfig`
        - Config file is now saved as a JSON file. Values no longer need to be converted to strings before saving as before. Values are saved as their original data types.

- **Windows**
    - Message/Password/Progress Windows
        - Message text is now set to plain text format. HTML tags are no longer supported. Text appears as typed.
        - Added line wrap to message window text. Text will wrap to next line if it exceeds the window width.

    - `PyFlameProgressWindow`
        - Done button is now enabled once progress is complete. No need to manually set it to enabled.

### Misc
    - `_WindowResolution`
        - Utility class to determine the main window resolution based on the Qt version. Fixes conflicts with Shotgrid Toolkit and Flame 2025. Thanks to Ari Brown for this fix.

## v2.5.0 [06.22.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Attributes**
            - `tree_list`
                - Get a list of all item names in the tree. (Converted this to an attribute from a method)
            - `tree_dict`
                - Get a dictionary of all items in the tree.

### Misc

- Docstring improvements for richer IDE tooltips.

## v2.4.0 [06.12.24]

### Added

- **Pyflame Functions**
    - `pyflame.iterate_name`
        - Iterate through a list of names and return a unique name based on the list.

### Updates/Fixes

- **Widgets**
    - `PyFlameTreeWidget`
        - **New Methods**
            - `fill_tree`
                - Fill the tree widget with the provided dictionary.
            - `add_item`
                - Add a new item as a child of the currently selected item in the tree,
            - `delete_item`
                - Delete the selected item in the tree.
            - `sort_items`
                - Sort all items in the tree while maintaining the structure and keeping the tree expanded.
            - `tree_list`
                - Get a list of all item names in the tree.

## v2.3.0 [05.07.24]

### Added

- **Widgets**
    - `PyFlameButtonGroup`
        - Allows for grouping of PyFlameButtons, PyFlamePushButtons, PyFlamePushButtonMenus, and PyFlameColorPushButtonMenus.
          By default set_exclusive is set to True. This means only one button in the group can be selected at a time.

- **Pyflame Functions**
    - `pyflame.generate_unique_node_names`
        - Generate unique node names based on a list of existing node names.

## v2.2.0 [05.05.24]

### Misc

- Added constants for script name(SCRIPT_NAME), script path(SCRIPT_PATH). These are used as default values for script_name and script_path arguments in all classes and functions.
  Both constants are derived from the pyflame_lib file path and file name.
- Updated all classes and functions that have parameters for script_name and script_path.
  They now use SCRIPT_NAME constant for script name and SCRIPT_PATH constant for script path as default values if not passed as arguments.

## v2.1.16 [04.29.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameDialogWindow`
        - Updated window layout to fix alignment issues with lines.

- **PyFlame Functions**
    - `pyflame.resolve_path_tokens`
        - Added BatchGroupName token. A PyBatch object must be passed as the flame_pyobject argument.

## v2.1.15 [04.23.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameLineEdit`
        - **New Argument**
            - `tooltip`
                - Set tooltip text.

## v2.1.14 [04.16.24]

### Updates/Fixes

- **Config**
    - `PyFlameConfig`
        - **New Method**
            - `get_config_values`
                - Returns the values of a config file at the supplied path as a dictionary.

## v2.1.13 [04.01.24]

### Updates/Fixes

- **Config**
    - `PyFlameConfig`
        - Config file is saved if it doesn't exist when loading the default config values.

## v2.1.12 [03.08.24]

- **PyFlamePushButtonMenu** / **PyFlamePushButton** – new arg `enabled` (default True).

### Updates/Fixes

- **Widgets**
    - `PyFlamePushButtonMenu`
        - **New Argument**
            - `enabled`
                - Enable or disable button state. Default is True.

    - `PyFlamePushButton`
        - **New Argument**
            - `enabled`
                - Enable or disable button state. Default is True.

## v2.1.11 [03.03.24]

### Updates/Fixes

- **Widgets**
    - `PyFlameTokenPushButton`
        – Menu sizing fix to be consistent with other menus
    - `PyFlamePushButtonMenu`
        – Menu text is now left aligned.

## v2.1.10 [02.29.24]

### Added

- **Widgets**
    - `PyFlameColorPushButtonMenu`
        - Push Button Menu with color options. Returns selected color as a tuple of normalized RGB values.

- **Layout Classes**
    - `PyFlameGridLayout`
    - `PyFlameHBoxLayout`
    - `PyFlameVBoxLayout`

    These classes adjust values for margins, spacing, and minimum size for the layout using pyflame.gui_resize method
    so the layout looks consistent across different screen resolutions. Removes need to use pyflame.gui_resize inside
    of main script.

### Misc

- Improved argument validations for all widgets.
- Added arguments to turn off/on menu indicators for PyFlamePushButtonMenu and PyFlameColorPushButtonMenu. Default is off.

## v2.1.9 [02.17.24]

### Misc

- Tooltip text color set to white; tooltip border set to `1px solid black`.

## v2.1.8 [02.11.24]

### Misc
- UI/code improvements for Message/Progress/Password windows.

## v2.1.7 [02.09.24]

### Updates/Fixes

- **Pyflame Functions**
    - `get_flame_python_packages_path`
        – new arg to toggle terminal printing (default True).

- **Config**
    Fixed: Config values not printing in terminal when loading config file.

## v2.1.6 [01.31.24]

### Added

- **Widgets**
    - `PyFlameLineEditFileBrowser`
        - Line Edit widget that opens a flame file browser when clicked.

### Updates/Fixes

- **Widgets**
    - `PyFlameLineEdit`
        - **New Argument**
            - `read_only`
                - Makes the line edit read only and unselectable with dark background. Default is False.

    - `PyFlameSlider`
        - **New Argument**
            - `rate`
                - Controls the sensitivity of the slider. The value should be between 1 and 10. 1 is the most sensitive and 10 is the least sensitive. Default is 10.

        - **Fixed**
            - PySide6 errors/font in slider calculator.

## v2.1.5 [01.25.24]

### Updates/Fixes

- **Widgets**

- `PyFlameTokenPushButton`
    - **Argument Defaults**
        - `text='Add Token'`
        - `token_dict={}`
        - `token_dest=None`

    - **Added Argument Default Values**
        - `text='Add Token'`
        - `token_dict={}`
        - `token_dest=None`

    - **Methods**
        - `add_menu_options(new_options)`
            - Add new menu options to the existing token menu and clear old options.

## v2.1.4 [01.21.24]

### Misc

- Updated PySide.
- Improved UI scaling for different screen resolutions.
- Fixed issue with PyFlameConfig not properly returning boolean values.

## v2.1.3 [11.21.23]

### Updates/Fixes

- **Pyflame Functions**
    - `pyflame.get_export_preset_version()`
        - Checks default JPEG preset automatically.

## v2.1.2 [11.17.23]

### Updates/Fixes

- **Widgets**
    - `TokenPushButtonMenu`
        - Option to clear destination before insert.

## v2.1.1 [11.06.23]

### Added

- **Pyflame Functions**
    - `pyflame.get_export_preset_version()`
    - `pyflame.update_export_preset()`

## v2.1.0 [08.14.23]

### Misc

- Renamed all widgets from Flame* to PyFlame*.
- Improved widget docs; note that some widgets rely on others—keep them in this file.
