# create export menus

**Script Version:** 5.4.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.29.20  
**Update Date:** 07.14.25  

**Script Type:** MediaPanel

## Description

Create custom right-click export menu's from saved export presets

## URL

https://github.com/logik-portal/python/create_export_menus

## Menus

### To create or edit export menus
- Flame Main Menu → Logik Portal → Logik Portal Script Setup → Create Export Menus
### To access newly created menus
- Right-click on clip → Project Export Presets... → Select export
- Right-click on clip → Shared Export Presets... → Select export

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v5.4.0 [07.14.25]
- Updated to PyFlameLib v5.0.0.
- Window layer order in linux is now fixed.
<br>

### v5.3.1 [04.24.25]
- Hour token now gives 24 hour format.
- Added new hour (12 Hour) token to give 12 hour format.
<br>

### v5.3.0 [04.07.25]
- Updated to PyFlameLib v4.3.0.
- Added confirmation window when overwriting an existing export menu.
<br>

### v5.2.0 [01.15.25]
- Updated to PyFlameLib v4.1.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v5.1.0 [08.24.24]
- Updated to PyFlameLib v3.
<br>

### v5.0.0 [03.25.24]
- Major code cleanup.
- Added subtitle export options to export presets.
- Script now scans shared/project export preset subdirectories for saved export presets.
<br>

### v4.6.1 [02.25.24]
- Misc UI Fixes.
<br>

### v4.6.0 [01.21.24]
- Updated UI/PySide.
- Fixed misc UI issues.
- Fixed issue with Reveal in MediaHub/Finder buttons not updating in Edit tab.
- Updated config file loading/saving.
<br>

### v4.5.0 [09.03.23]
- Update to pyflame lib v2.0.0.
- *** The update to pyflame lib v2.0.0. will cause old script menus to not work. ***
<br>

### v4.4 [04.20.23]
- Updated menus for Flame 2023.2+
- Added 2024 preset version number.
- Removed maximum version from preset menu template. This allows presets to be used with newer versions of Flame.
<br>

### v4.3 [08.22.22]
- Added duplicate button to Edit tab - Duplicates selected preset
<br>

### v4.2 [06.22.22]
- Messages print to Flame message window - Flame 2023.1 and later
- Updated browser window for Flame 2023.1 and later
- Setup window no longer closes after creating a new export preset
- Menu template updated - With template importing new pyflame_lib module, error appears during flame startup when loading
- menu presets. There errors can be ignored. Errors might be due to order flame is loading modules. Menus work fine.
<br>

### v4.1 [03.19.22]
- Moved UI widgets to external file
- Added confirmation window when deleting an existing preset
<br>

### v4.0 [03.02.22]
- Updated UI for Flame 2023
- Code optimization
- Misc bug fixes
<br>

### v3.7 [01.03.22]
- Shared export menus now only work with the major version of Flame they're created with. This avoids errors when using
- a menu with a new version of Flame. For example a menu created with Flame 2022.2 will work with all versions
- of Flame 2022 but not 2021 or 2023. Shared export menus will now also only show up in versions of Flame that they will
- work with.
- Added token for Tape Name to be used if clip has a clip name assigned
<br>

### v3.6 [11.02.21]
- Fixed shot name token translation to work with python 3.7 in menu_template
<br>

### v3.5 [10.13.21]
- Added button to reveal export path in MediaHub after export
- Added button to reveal export path in finder after export
- Export shared movie/file export presets not compatible with working version of Flame are not listed in list drop downs
- Fixed: Exporting using time tokens would create additional folders if time changed during export
- Removed leading zero from hour token if hour less than 10.
- Added lower case ampm token
- Shot name token improvements
- Shot name token will now attempt to get assigned shot name from clip before guessing from clip name
- Added SEQNAME token
<br>

### v3.4 [05.21.21]
- Updated to be compatible with Flame 2022/Python 3.7
<br>

### v3.3 [05.19.21]
- Edited menus now save properly
- Shot name token fixed to handle clip names that start with numbers
<br>

### v3.2 [02.15.21]
- Python hooks refresh after deleting a preset
<br>

### v3.1 [01.19.21]
- Added ability to assign multiple exports to single right-click export menu
- Added ability to edit/rename/delete existing export presets
- When export is done Flame with switch to export destination in the Media Hub (Flame 2021.2 of higher only)
<br>

### v2.1 [09.19.20]
- Updated UI
- Added Shot Name token to export path token list - Shot Name derived from clip name
- Added Sequence Name token to export path token list - Seq Name derived from Shot Name
- Added Batch Group Name token to export path token list - Can only be used when exporting clips from batch groups
- Added Batch Group Shot Name token to export path token list - Can only be used when exporting clips from batch groups
- Saved project export presets can now be found if project is not saved in the default location
- Duplicate preset names no longer allowed - duplicate preset names cause preset not to work
<br>

### v2.0 [04.27.20]
- New UI
- Tokens can be used to dynamically set the export path
- Options to choose to export in foreground, export between marks, and export top layer
- Menus can be saved so that they're visible in current project only and
- shared between all projects
<br>

### v1.1 [04.05.20]
- Fixed: Config path
- Fixed: Problem when checking for project presets to delete
