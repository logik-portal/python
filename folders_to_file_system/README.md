# Folders To File System

**Script Version:** 1.7.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.26.23  
**Update Date:** 10.23.26  

**Script Type:** MediaPanel

## Description

Create folders in selected file system path from folders in selected Library or Folder.

## URL

https://logik-portal.com/scripts/folders_to_file_system

## Menus

- Select Library or Folder in Media Panel → Folders to File System

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.7.0 [10.23.26]
- Fixed wrong folder paths when the selected folder's name is part of a parent, library, workspace or project name.
- Fixed error when clips are selected along with libraries or folders.
- Fixed permission error message not showing the selected path.
- Errors creating folders are now shown instead of being hidden.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.6.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v1.5.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v1.4.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v1.3.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v1.2.0 [01.21.24]
- Updates to PySide.
<br>

### v1.1.0 [08.20.23]
- Updated to PyFlameLib v2.0.0.
- Updated script versioning to semantic versioning.
