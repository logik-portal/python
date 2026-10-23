# Delete Empty Folders

**Script Version:** 1.7.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 11.15.23  
**Update Date:** 10.23.26  

**Script Type:** MediaPanel

## Description

Delete any empty folders in selected Library or Folder.

## URL

https://logik-portal.com/scripts/delete_empty_folders

## Menus

- Right-click on Folder or Library in Media Panel → Delete Empty Folders

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.7.0 [10.23.26]
- Fixed Flame hanging when an empty folder can't be deleted. Folders that can't be deleted are listed in one message.
- Fixed error when clips are selected along with libraries or folders.
- Folders are now deleted without a confirmation prompt for each folder.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.6.0 [03.31.26]
- Updated to PyFlameLib v5.3.0.
<br>

### v1.5.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v1.4.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v1.3.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v1.2.0 [08.09.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v1.1.0 [01.21.24]
- Updates to PySide.
