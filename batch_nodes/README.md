# batch nodes

**Script Version:** 3.11.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 04.18.20  
**Update Date:** 07.10.25  

**Script Type:** Batch / Flame Main Menu

## Description

*** Does not work with Flame 2024.0 due to bug in Flame ***
<br><br>
Add menus to batch right-click for your favorite nodes.
<br><br>
Works with standard batch nodes/matchboxes/ofx.
<br><br>
OFX can only be added by right clicking on an existing node in batch.
<br><br>
Nodes added by right-clicking on them in batch will be saved with current settings.
<br><br>
All created node menu scripts are saved in /opt/Autodesk/user/YOURUSER/python/batch_node_menus

## URL

https://github.com/logik-portal/python/batch_nodes

## Menus

### To create/rename/delete menus from node lists
- Flame Main Menu → Logik → Logik Portal Script Setup → Batch Nodes Setup
### To create menus for nodes with settings applied in batch
- Right-click on node in batch → Batch Nodes... → Create Menu For Selected Node
### To create menus for ofx nodes
- Right-click on node in batch → Batch Nodes... → Create Menu For Selected Node
### To add node from menu to batch
- Right-click in batch → Batch Nodes... → Select Node to be added

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

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
