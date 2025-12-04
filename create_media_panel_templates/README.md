# Create Media Panel Templates

**Script Version:** 3.9.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 05.01.19  
**Update Date:** 07.10.25  

**Script Type:** MediaPanel

## Description

Create templates from libraries and folders in the Media Panel.
Right-click menus will be created for each template

## URL

https://github.com/logik-portal/python/create_media_panel_templates

## Menus

### To create new template menus
- Right-click on library or folder → Create Template... → Create Library Template / Create Folder Template
### Newly created templates
- Right-click on library or folder → Library/Folder Templates → Select from saved templates

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v3.9.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Window layer order in linux is now fixed.
<br>

### v3.8.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v3.7.0 [01.02.25]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v3.6.0 [08.24.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v3.5.0 [01.02.24]
- Updates to UI/PySide.
<br>

### v3.4.0 [08.19.23]
- Fixed creating menus for libraries/folders with periods in name.
- Periods are now replaced with underscores in menu file name.
- Updated to PyFlameLib v2.0.0.
- Updated to semantic versioning.
<br>

### v3.3 [07.12.22]
- Messages print to Flame message window - Flame 2023.1 and later
<br>

### v3.2 [03.15.22]
- Moved UI widgets to external file
<br>

### v3.1 [03.07.22]
- Updated UI for Flame 2023
