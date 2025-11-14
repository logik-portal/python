# PyFlame Library

**Version:** 4.3.1<br>
**Written by:** Michael Vaglienty<br>
**Creation Date:** 10.31.20<br>
**Update Date:** 04.13.25

This file contains a library of various custom UI widgets that can be used to build QT windows similar to the look of Flame along with some other useful functions.

To avoid conflicts with having multiple copies within the Flame python folder, this file should be renamed to: pyflame_lib_<script_name>.py

Required folder structure when using this library:
```
script_folder/
├── main_script.py
├── lib/
│   └── pyflame_lib_<main_script_name>.py
├── assets/
│   └── fonts/
│       └── Montserrat-Regular.ttf
│       └── Montserrat-Light.ttf
│       └── Montserrat-Thin.ttf
```

Required Files:
    - Montserrat-Regular.ttf
    - Montserrat-Light.ttf
    - Montserrat-Thin.ttf
    - pyflame_lib_<main_script_name>.py

All paths are relative to the script's root directory.

Make sure this structure is preserved when deploying or moving the script.

To import the library into the main script, use:
    `from lib.pyflame_lib_<main_script_name> import *`

## PyFlame QT Widget Classes

- `PyFlameButton` - Custom QT Flame Button
- `PyFlameButtonGroup` - Allows for groupings of PyFlameButton types(PyFlameButton, PyFlamePushButton...).
- `PyFlameEntry` - Custom QT Flame Entry Field Widget. Replaces PyFlameLineEdit.
- `PyFlameEntryFileBrowser` - Custom QT Entry Field Widget that opens Flame File Browser when clicked.
- `PyFlameLabel` - Custom QT Flame Label Widget.
- `PyFlameLineEditFileBrowser` - Deprecated. Use PyFlameEntryFileBrowser instead.
- `PyFlameListWidget` - Custom QT Flame List Widget.
- `PyFlamePushButton` - Custom QT Flame Push Button.
- `PyFlamePushButtonMenu` - Custom QT Flame Push Button Widget with Menu.
- `PyFlameColorPushButtonMenu` - Custom QT Flame Push Button with Color Menu.
- `PyFlameSlider` - Custom QT Flame Numerical Slider.
- `PyFlameTable` - Custom QT Flame Table Widget.
- `PyFlameTabWidget` - Custom QT Flame Tab Widget.
- `PyFlameTextEdit` - Custom QT Flame Text Edit Widget.
- `PyFlameTokenPushButtonMenu` - Custom QT Flame Push Button with Token Menu.
- `PyFlameTreeWidget` - Custom QT Flame Tree Widget.

- `PyFlameHorizontalLine` - Custom QT Horizontal Line Widget.
- `PyFlameVerticalLine` - Custom QT Vertical Line Widget.

## PyFlame QT Layout Classes

- `PyFlameGridLayout` - Custom QT Grid Layout.
- `PyFlameHBoxLayout` - Custom QT Horizontal Box Layout.
- `PyFlameVBoxLayout` - Custom QT Vertical Box Layout.

## PyFlame QT Window Classes

- `PyFlamePresetManager` - Preset Manager for scripts.
- `PyFlameMessageWindow` - Flame Message Window
- `PyFlamePasswordWindow` - Flame Password Window
- `PyFlameProgressWindow` - Flame Progress Window
- `PyFlameDialogWindow` - Flame QT Dialog Window
- `PyFlameWindow` - Flame QT Window
- `PyFlameInputDialog` - Flame QT Input Dialog Window

## Utility Classes

- `PyFlameConfig` - Class for creating, loading, and saving config files.

## PyFlame Functions

- `pyflame.copy_to_clipboard` - Copy text to clipboard using QT.
- `pyflame.create_file_system_folders` - Create a folder in the file system based on the provided folder structure.
- `pyflame.create_media_panel_folders` - Create a folder in the media panel based on the provided folder structure.
- `pyflame.create_media_panel_libraries` - Create libraries with folders in the media panel based on the provided folder structure.
- `pyflame.create_temp_folder` - Create a temporary folder in the script folder.
- `pyflame.cleanup_temp_folder` - Clear the contents of the temporary folder.
- `pyflame.convert_export_preset_name_to_path` - Convert export preset name to path.
- `pyflame.file_browser` - Flame file browser or QT file browser window.
- `pyflame.find_by_tag` - Search through a Flame object's contained objects by tags.
- `pyflame.font_resize` - Resize font size for all PyFlame widgets for different screen resolutions. - Not intended to be used outside of this file.
- `pyflame.generate_unique_node_names` - Generate unique node names based on a list of existing node names.
- `pyflame.get_export_preset_names` - Get export preset names from Shared and Project paths. User paths are not checked.
- `pyflame.get_export_preset_version` - Get export preset version.
- `pyflame.get_flame_python_packages_path` - Get path to Flame python packages folder.
- `pyflame.get_flame_version` - Get version of Flame.
- `pyflame.gui_resize` - Resize PyFlame widgets for different screen resolutions. - Not intended to be used outside of this file.
- `pyflame.iterate_name` - Iterate through a list of names and return a unique name based on the list.
- `pyflame.move_to_shot_folder` - Move a clip to a shot folder in the Media Panel.
- `pyflame.open_in_finder` - Open path in System Finder.
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
- `pyflame.shot_name_from_clip` - Get shot name from clip.
- `pyflame.untar` - Untar a tar file.
- `pyflame.update_export_preset` - Update export preset version.
- `pyflame.verify_script_install` - Verify that script is installed in the correct location with any additional files that are required.

## Usage

To use this library in a script, add the following import statement:

`from lib.pyflame_lib_<script name> import *`

This makes all classes, functions and constants from the library directly available in the script's namespace.

Example:

`pyflame.print("Hello")  # Use PyFlame functions`
`window = PyFlameWindow()  # Create PyFlame widgets`

To utilize PyFlameFunctions, access methods through pyflame:

`pyflame.print("Hello")`
`pyflame.get_flame_version()`

To utilize widgets, instantiate them directly by their class names:

`window = PyFlameWindow()`
`button = PyFlamePushButton()`
`menu = PyFlamePushButtonMenu()`

## Updates

**v4.3.1 04.16.25**

- Fixed Bug: PyFlameEntryBrowser - Errors when setting `connect` to `None`

**v4.3.0 03.16.25**

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

- New PyFlame Function
  - `pyflame.print_title`
    - Prints title and version of script to terminal.

- New Widgets
    - `PyFlameTable`
        - A table widget that allows for displaying and interacting with tabular data such as CSV files.

    - `PyFlameTabWidget`
        - Creates a tab widget inside of a window that other widgets can be places inside of.

- New Window Classes:
    - `PyFlameInputDialog`
        - A simple dialog window that allows for input of a single line of text.

- PyFlameButton:
    - New Argument
        - `max_height`
            - Set PyFlameButton to maximum height. Use if height is being set by layout. Overrides `height` if set to True.

- PyFlameEntry:
    - New Method
        - `text_changed(connected_function: Callable)`:
            - Calls a function when the text in the entry field changes.

- PyFlameSlider:
    - Updated Calculator UI

- PyFlameTextEdit:
    - New Argument
        - `text_type`
            - Set type of text being added using TextType enum. TextType.PLAIN, TextType.MARKDOWN, TextType.HTML.

- PyFlameWindow/PyFlameDialogWindow:
    - New Method
        - `set_title_text`
            - Set the title of the window.

- PyFlameColorPushButtonMenu:
    - `No Color` option added to default color menu. This either applies no color or clears the current color.

    - New Methods
        - `get_color`
            - Return selected color name.
        - `get_color_value`
            - Return normalized RGB color value of selected color.
        - `set_color`
            - Set the color of the PyFlameColorPushButtonMenu.

**v4.2.0 02.19.25**

- Updated font used for widgets. Montserrat Regular is now the default font for all QT widgets. The Discreet font is used
as a fallback if Montserrat is not found. Font location: `<SCRIPT_FOLDER>/assets/fonts`

- PyFlame Widget Argument Validation
    - Argument errors now print to Flame message area as well as terminal.

- PyFlameEntry
    - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.
    - Added Alt+Click to show full entry text as tooltip. Also copies full entry text to clipboard.

- PyFlameListWidget
    - New Argument
        - `items`
            - A list of items to add to the list widget can now be provided on creation of the widget.

- PyFlamePushButton
    - Improved tooltip functionality. Added arguments to set the tooltip delay and duration.

- PyFlameTextEdit
    - New Argument
        - `text_type`
            - Type of text being input. TextType.PLAIN, TextType.MARKDOWN, TextType.HTML.

- PyFlameWindow/PyFlameDialogWindow
    - New Arguments
        - `title_style`
            - Set style of title line in window. Use Style Enum to set style.
        - `parent`
            - Set parent of window.

- New Widget
    - PyFlameEntryFileBrowser
        - Replaces PyFlameLineEditFileBrowser which is now deprecated.

- New pyflame functions
    - `pyflame.raise_type_error`
        - Raise a type error. Print error message with traceback to Flame message area and terminal.

    - `pyflame.raise_value_error`
        - Raise a value error. Print error message with traceback to Flame message area and terminal.

    - `create_temp_folder`
        - Create a temporary folder in the script folder.

    - `cleanup_temp_folder`
        - Clear the contents of the temporary folder.

- Deprecated Widget
    - PyFlameLineEditFileBrowser

- New Label Style
    - `Style.BACKGROUND_THIN`
        - Adds a darker background to the Label with a thinner font weight. Text is left aligned by default. Used for window titles.

- Fixed
    - Line colors not properly being applied to PyFlameWindow and PyFlameDialogWindow.

- Removed
    - LineColor Enum. All colors are now set using the Color Enum.

**v4.1.0 01.15.25**

- New Widgets
    - `PyFlameHorizontalLine`
        - A horizontal line widget.
    - `PyFlameVerticalLine`
        - A vertical line widget.

**v4.0.0 01.05.25**

- Fixed type hinting for `pyflame.copy_to_clipboard` function. This was causing scripts not to work with Flame 2024.

- New pyflame Functions:
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

- pyflame.generate_unique_node_names
    - Fixed: Would not properly generate a new name if the first character of the new name was a number.

- pyflame.resolve_tokens
    - Batch groups are now checked for a ShotName tag(ShotName:<shot_name>). If found, it is used to resolve the shot name token.

- New Widget
    - `PyFlameEntry`
        - Replaces PyFlameLineEdit which has been deprecated.
        - New Argument:
            - `align`
                - Align entry text to left, right, or center. Default is left.

- PyFlameTextEdit
      -`read-only` background color now matches read-only background color of PyFlameEntry for consistency.

- PyFlameTreeWidget
    - New Arguments
        - `top_level_editable`
            - Allow editing of name of top level items in the tree. Default is False.
        - `tree_list`
            - List of items to populate the tree. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
        - `tree_list_no_root`
            - List of items to populate the tree excluding the root item. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
        - `update_callback`
            - Function to call when an item is edited, inserted, or deleted.

    - New Attributes:
        - `selected_item`
            - Return the text of the currently selected item.
        - `item_path`
            - Return the recursive path of the currently selected item.
        - `item_paths`
            - Return the recursive paths of the currently selected items.
        - `all_item_paths`
            - Return the recursive paths of all items in the PyFlameTreeWidget.

- PyFlameGridLayout
    - Added the ability to set the number of columns and rows in the grid to make it easier to place widgets especially where space is desired between widgets. By default the unit size of the grid is 150px wide and 28px high. The size of a normal button. The width and height of each grid unit along with the number of columns and rows can be adjusted using setGridSize method.

    - New Arguments:
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

    - Arguments Removed
        - `setMinimumColumnWidth`
            - No longer needed.
        - `setMinimumRowHeight`
            - No longer needed.

    - New Method:
        - `setGridSize`
            - Configure the grid layout dimensions and cell sizes. This method allows you to:
            - Set the number of columns and rows in the grid
            - Define the width of each column (in pixels)
            - Define the height of each row (in pixels)
            - Automatically adjust spacing between grid cells

- PyFlameWindow/PyFlameDialogWindow
    - Simplified window creation by adding PyFlameGridLayout to the window by default with optional
        arguments to set the number of columns and rows along with column and row widths. This can
        be overridden by passing grid_layout=False.

    - New Arguments
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

- PyFlameMessageWindow
  - Updated message printing to terminal to be more clear.
  - Message text no longer uses html tags. Text is now printed as plain text.

- PyFlameProgressWindow
    - Updated message printing to terminal to be more clear.

- Deprecated PyFlame Functions:
    - `pyflame.message_print`
        - Use pyflame.print instead.
    - `pyflame.resolve_path_tokens`
        - Use pyflame.resolve_tokens instead.

- Deprecated Widgets
    - `PyFlameLineEdit`
        - Use PyFlameEntry instead.
    - `PyFlameLabel.Style.BACKGROUND`
        - Use PyFlameEntry with read_only=True instead.

- Miscellaneous
    - `max_width` argument is now set to True by default for all widgets. width and height are now bypassed. This means the widgets will now expand to fill the available space. The size of the widgets is now determined by the layout(PyFlameGridLayout, PyFlameHBoxLayout, PyFlameVBoxLayout). To override this behavior, set max_width to False and set width and height arguments to set the size of the widget.

    - `max_height` argument is now set to True by default on the following widgets. The above behavior for `max_width` applies to max_height in these widgets:
        - PyFlameListWidget
        - PyFlameTreeWidget
        - PyFlameTextEdit

**v3.2.0 09.09.24**

- New pyflame Functions
    - `pyflame.json_print`
        - Cleanly print JSON data to terminal with proper indentation for easy readability.

**v3.1.0 09.01.24**

- PyFlameMessageWindow
    - Added scrollbars to message window for long messages.

- New pyflame Functions:
    - `pyflame.print_list`
        -  Print a list of items to the terminal and Flame message area.
    - `pyflame.print`
        - Print a message to the terminal and Flame message area.

**v3.0.0 08.16.24**

- New pyflame Function
    - `pyflame.copy_to_clipboard`
        - Copy text to clipboard using QT.

New Utility Class:
    - `_WindowResolution`
        - Utility class to determine the main window resolution based on the Qt version. Fixes conflicts with Shotgrid Toolkit and Flame 2025. Thanks to Ari Brown for this fix.

- PyFlameConfig
    - Config file is now saved as a JSON file. Values no longer need to be converted to strings before saving as before. Values are saved as their original data types.

- Message/Password/Progress Windows
    - Message text is now set to plain text format. HTML tags are no longer supported. Text appears as typed.
    - Added line wrap to message window text. Text will wrap to next line if it exceeds the window width.

- PyFlameTreeWidget
    - Fixed font size issue in linux.
    - When sorting is enabled, sorting is done in ascending order of items in column 0.

- PyFlameProgressBar Window
    - Done button is now enabled once progress is complete. No need to manually set it to enabled.

**v2.5.0 06.22.24**

- Improvements to docstrings to enhance hover over tooltips in IDEs.

- PyFlameTreeWidget
    - New Attributes:
        - `tree_list`
            - Get a list of all item names in the tree. (Converted this to an attribute from a method)
        - `tree_dict`
            - Get a dictionary of all items in the tree.

**v2.4.0 06.12.24**

- PyFlameTreeWidget
    - New Methods
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

New pyflame Function
    - `pyflame.iterate_name`
        - Iterate through a list of names and return a unique name based on the list.

**v2.3.0 05.07.24**

- New Widget
    - `PyFlameButtonGroup`
        - Allows for grouping of PyFlameButtons, PyFlamePushButtons, PyFlamePushButtonMenus, and PyFlameColorPushButtonMenus. By default set_exclusive is set to True. This means only one button in the group can be selected at a time.

- New pyflame Function
    - `pyflame.generate_unique_node_names`
        - Generate unique node names based on a list of existing node names.

**v2.2.0 05.05.24**

- New Class
    - `PyFlamePresetManager`
        - This class allows for saving/editing/deleting of presets for scritps. Presets can be assigned to specific projects or be global.

- Added constants for script name(SCRIPT_NAME), script path(SCRIPT_PATH). These are used as default values for script_name and script_path arguments in all classes and functions. Both constants are derived from the pyflame_lib file path and file name.

- Updated all classes and functions that have parameters for script_name and script_path. They now use SCRIPT_NAME constant for script name and SCRIPT_PATH constant for script path as default values if not passed as arguments.

**v2.1.16 04.29.24**

- Added BatchGroupName token to resolve_path_tokens function. A PyBatch object must be passed as the flame_pyobject argument.

- PyFlameDialogWindow - Updated window layout to fix alignment issues with lines.

**2.1.15 04.23.24**

- PyFlameLineEdit
    - New Argument
        - `tooltip`
            - Set tooltip text.

**v2.1.14 04.16.24**

- PyFlameConfig
    - New Method
        - `get_config_values`
            - Returns the values of a config file at the supplied path as a dictionary.

**v2.1.13 04.01.24**

- PyFlameConfig: Config file is now saved if it doesn't exist when loading the default config values.

**v2.1.12 03.08.24**

- PyFlamePushButtonMenu
    - New Argument
        - `enabled`
            - Enable or disable button state. Default is True.

- PyFlamePushButton
    - New Argument
        - `enabled`
            - Enable or disable button state. Default is True.

**v2.1.11 03.03.24**

- PyFlameTokenPushButtonMenu: Fixed menu sizing to be consistent with other menus.

- PyFlamePushButtonMenu: Menu text is now left aligned.

**v2.1.10 02.29.24**

- New Layout Classes
    - `PyFlameGridLayout`
    - `PyFlameHBoxLayout`
    - `PyFlameVBoxLayout`

    These classes adjust values for margins, spacing, and minimum size for the layout using pyflame.gui_resize method
    so the layout looks consistent across different screen resolutions. Removes need to use pyflame.gui_resize inside
    of main script.

- New class
    - `PyFlameColorPushButtonMenu`
        - Push Button Menu with color options. Returns selected color as a tuple of normalized RGB values.

- Added arguments to turn off/on menu indicators for PyFlamePushButtonMenu and PyFlameColorPushButtonMenu. Default is off.

- Improved argument validations for all widgets.

**v2.1.9 02.17.24**

- Fixed all widget tooltip text color. Color is now set to white instead of red.

- Fixed all widget tooltip border. Is now set to 1px solid black.

**v2.1.8 02.11.24**

- Improvements to UI/code for PyFlameMessage, PyFlameProgress, and PyFlamePassword windows.

**v2.1.7 02.09.24**

- Fixed: Config values not printing in terminal when loading config file.

- pyflame.get_flame_python_packages_path
- New Argument
- to enable/disable printing path to terminal.
    Default is True.

**v2.1.6 01.31.24**

- Fixed PySide6 errors/font in slider calculator.

- New Widget
    - `PyFlameLineEditFileBrowser`
        - Line Edit widget that opens a flame file browser when clicked.

- PyFlameLineEdit
    - New Argument
        - `read_only`
            - Makes the line edit read only and unselectable with dark background. Default is False.

- PyFlameSlider
    - New Argument
        - `rate`
            - Controls the sensitivity of the slider. The value should be between 1 and 10. 1 is the most sensitive and 10 is the least sensitive. Default is 10.

**v2.1.5 01.25.24**

- PyFlameTokenPushButton:
    - Added default argument values:
        - `text='Add Token'`
        - `token_dict={}`
        - `token_dest=None`
    - New Method:
        - `add_menu_options(new_options)`
            - Add new menu options to the existing token menu and clear old options.

**v2.1.4 01.21.24**

- Updated PySide.
- Improved UI scaling for different screen resolutions.
- Fixed issue with PyFlameConfig not properly returning boolean values.

**v2.1.3 11.21.23**

- Updated pyflame.get_export_preset_version() to check default jpeg export preset for preset version. This function no longer needs to be updated manually.

**v2.1.2 11.17.23**

- Updated Token Push Button Menu widget. Added ability to clean destination(line edit widget) before adding the token.

**v2.1.1 11.06.23**

- New pyflame functions
    - `pyflame.get_export_preset_version()`
    - `pyflame.update_export_preset()`

**v2.1.0 08.14.23**

- All widgets have been updated to be more consistent.

- All widgets have been changed from Flame to PyFlame.
    For example: FlamePushButtonMenu -> PyFlamePushButtonMenu
    Widgets should be left in this file and not moved individually
    to other files. This will cause problems since some widgets rely
    on other widgets/functions in this file.

- Widget documentation has been improved.
