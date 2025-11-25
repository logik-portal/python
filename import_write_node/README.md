# Import Write Node

**Script Version:** 2.11.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 05.26.19  
**Update Date:** 07.10.25  

**Script Type:** Batch

## Description

Import open clip created by selected write node into batch schematic reel or
shelf reel or auto-import write node image sequence when render is complete.

## URL

https://github.com/logik-portal/python/import_write_node

## Menus

### Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Import Write Node Setup
### To import open clips
- Right-click on write file node in batch → Import... → Import Open Clip to Batch
- Right-click on write file node in batch → Import... → Import Open Clip to Renders Reel

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.11.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v2.10.0 [04.10.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v2.9.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v2.8.0 [09.02.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.7.0 [01.15.24]
- Updates to PySide.
- Updated to PyFlameLib v2.0.0.
- Updated script versioning to semantic versioning.
<br>

### v2.6 [03.02.23]
- Updated config file loading/saving.
- Updated menus for Flame 2023.2+
- Added check to make sure script is installed in the correct location.
<br>

### v2.5 [11.10.22]
- Fixed bug loading open clip when (ext) token is used in the Create Open Clip path.
<br>

### v2.4 [05.30.22]
- Messages print to Flame message window - Flame 2023.1 and later.
<br>

### v2.3 [04.13.22]
- Script renamed to: Import Write Node.
- Updated UI for Flame 2023.
- Moved UI widgets to external file.
<br>

### v2.1 [09.24.21]
- Added token translation for project nickname.
<br>

### v2.0 [05.25.21]
- Updated to be compatible with Flame 2022/Python 3.7.
<br>

### v1.5 [09.19.20]
- Pops up message box when open clip doesn't exist.
<br>

### v1.4 [07.01.20]
- Open clips can be imported to Batch Renders shelf reel - Batch group must have shelf reel called Batch Renders.
- Added token for version name.
<br>

### v1.3 [11.01.19]
- Right-click menu now appears under Import...
<br>

### v1.1 [09.29.19]
- Code cleanup.
