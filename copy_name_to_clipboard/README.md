# Copy Name to Clipboard

Plugin for [Autodesk Flame software](http://www.autodesk.com/products/flame).

Copy name of selected items to the clipboard.

Available for the following items:
 - Clips
 - Desktops
 - Folders
 - Libraries
 - Reels
 - Reel Groups
 - Sequences
 - Workspaces

## Compatibility
|Release Version|Flame Version|
|---|---|
|v3.X.X|Flame 2025 and up|
|v2.X.X|Flame 2022 up to 2024.2|
|v1.X.X|Flame 2021 up to 2021.2|

## Installation

### Flame 2025 and newer
To make available to all users on the workstation, copy `copy_name_to_clipboard.py` to `/opt/Autodesk/shared/python/`

For specific users, copy `copy_name_to_clipboard.py` to the appropriate path below...
|Platform|Path|
|---|---|
|Linux|`/home/<user_name>/flame/python/`|
|Mac|`/Users/<user_name>/Library/Preferences/Autodesk/flame/python/`|

### Flame 2021 up to 2024.2
To make available to all users on the workstation, copy `copy_name_to_clipboard.py` to `/opt/Autodesk/shared/python/`

For specific users, copy `copy_name_to_clipboard.py` to `/opt/Autodesk/user/<user name>/python/`

## Menus
- Right-click selected items on the Desktop `->` Copy... `->` Name to Clipboard
- Right-click selected items in the MediaHub `->` Copy... `->` Name to Clipboard
- Right-click selected items in the Media Panel `->` Copy... `->` Name to Clipboard
- Right-click selected items in the Timeline `->` Copy... `->` Name to Clipboard

## Acknowledgements
Many thanks to [pyflame.com](http://www.pyflame.com)
