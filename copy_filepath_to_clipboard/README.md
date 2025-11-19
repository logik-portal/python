# Copy Filepath to Clipboard

Plugin for [Autodesk Flame software](http://www.autodesk.com/products/flame).

Copy the source filepaths of the segments contained within the selected clips or sequences.

## Example
The format will match what is listed in the **Clip Location** column in the Conform tab.  For example:

`/path/path/path/file.[0001-0100].ext`

## Compatibility
|Release Version|Flame Version|
|---|---|
|v1.X.X|Flame 2025 and up|

## Installation

### Flame 2025 and newer
To make available to all users on the workstation, copy `copy_filepath_to_clipboard.py` to `/opt/Autodesk/shared/python/`

For specific users, copy `copy_filepath_to_clipboard.py` to the appropriate path below...
|Platform|Path|
|---|---|
|Linux|`/home/<user_name>/flame/python/`|
|Mac|`/Users/<user_name>/Library/Preferences/Autodesk/flame/python/`|

### Last Step
Finally, inside of Flame, go to Flame (fish) menu `->` Python `->` Rescan Python Hooks

## Menus
- Right-click selected items on the Desktop `->` Copy... `->` Filepath to Clipboard
- Right-click selected items in the Media Panel `->` Copy... `->` Filepath to Clipboard

## Acknowledgements
Many thanks to [pyflame.com](http://www.pyflame.com)
