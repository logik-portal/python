# Batch Nodes

**Script Version:** 3.13.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 04.18.20  
**Update Date:** 10.28.26  

**Script Type:** Batch / Flame Main Menu

## Description

Add menus to batch right-click for your favorite nodes in batch.

## Usage

Works with standard batch nodes/matchboxes/ofx.
<br><br>
OFX can only be added by right clicking on an existing node in batch.
<br><br>
Nodes added by right-clicking on them in batch will be saved with current node settings.
<br><br>
All created node menu scripts are saved in /opt/Autodesk/shared/python/batch_nodes/menus
<br><br>
Menus can be renamed and removed from the node list in the Batch Nodes setup window.
<br><br>
Before a menu is overwritten, replaced or removed, a confirmation window is shown.
<br><br>
Renamed menus can not contain slashes, backslashes or quotes. Node names used with Create Menu for Selected Node can not contain slashes or quotes.

## URL

https://logik-portal.com/scripts/batch_nodes

## Menus

### To create/rename/delete menus from node lists
- Flame Main Menu → Logik → Logik Portal Script Setup → Batch Nodes Setup
### To create menus for nodes with settings applied in batch
- Right-click on node in batch → Batch Nodes... → Create Menu for Selected Node
### To create menus for ofx nodes
- Right-click on node in batch → Batch Nodes... → Create Menu for Selected Node
### To add node from menu to batch
- Right-click in batch → Batch Nodes... → Select Node to be added
### To add node from menu to batch connected to selected node
- Right-click on node in batch → Batch Nodes... → Select Node to be added

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v3.13.0 [10.28.26]
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
- Create Menu for Selected Node now stops with an error if the node name contains a quote or slash.
- Adding a menu from the Setup window now asks before overwriting an existing menu, and removes the old saved setup folder when a saved-setup menu is replaced.
- Remove now deletes only the selected menus' own files and setup folders, not other menus whose names contain them, and asks for confirmation first.
- Renaming a menu to the name of another existing menu now asks before replacing it. Names with slashes, backslashes or quotes are rejected before anything changes, and if the rename still fails partway the changes are undone.
- Renaming a menu now only changes the menu name in the menu script, not matching text in its code or path.
- Create Menu for Selected Node now asks before overwriting an existing menu that has no saved setup folder.
- Setup window now opens when the Matchbox shaders folder for the current Flame version is missing.
- Script now stops cleanly if the install check fails.
<br>

### v3.12.0 [05.15.26]
- Updated to PyFlameLib v5.3.1.
<br>

### v3.11.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Bug fixes to batch nodes menu.
- Window layer order in linux is now fixed.
<br>

### v3.10.0 [03.11.25]
- Updated to PyFlameLib v4.3.0.
- Fixed misc bugs.
<br>

### v3.9.0 [01.04.25]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v3.8.0 [08.14.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v3.7.0 [01.21.24]
- Updates to UI/PySide.
<br>

### v3.6.0 [08.13.23]
- Updated to PyFlameLib v2.0.0.
<br>

### v3.5.1 [06.28.23]
- Updated version naming to semantic versioning.
- Main window tabs no longer have outline around names when selected in linux.
<br>

### v3.5 [02.04.23]
- Updated menus for Flame 2023.2+
- Updated config file loading/saving.
- Added check to make sure script is installed in the correct location.
<br>

### v3.4 [05.31.22]
- Messages print to Flame message window - Flame 2023.1+
- Flame file browser used to select folders - Flame 2023.1+
- Misc bug fixes.
<br>

### v3.3 [03.31.22]
- UI widgets moved to external file
- Misc bug fixes
<br>

### v3.2 [03.07.22]
- Updated UI for Flame 2023
<br>

### v3.1 [10.26.21]
- Updated config to xml
<br>

### v3.0 [05.20.21]
- Updated to be compatible with Flame 2022/Python 3.7
<br>

### v2.5 [01.27.21]
- Updated UI
- Menus/Nodes can be renamed after they've been added
<br>

### v2.1 [05.17.20:]
- Misc code updates
