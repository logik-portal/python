# Rename Shots

**Script Version:** 1.12.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 04.05.22  
**Update Date:** 07.10.25  

**Script Type:** MediaPanel/Timeline

## Description

Save clip and/or shot name naming patterns with tokens, then apply both to segments in a timeline.
<br><br>
> **Note:** <index> token does not work as expected in python. Use other tokens to rename shots.

## URL

https://github.com/logik-portal/python/rename_shots

## Menus

### Timeline
- Right-click on selected segments → Rename Shots
### Media Panel
- Right-click on selected sequence → Rename Shots

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.12.0 [01.03.26]
- Progress messages print to script window
<br>

### v1.11.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes window.
- Tab-key now moves focus between clip and shot name entry fields.
<br>

### v1.10.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v1.9.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v1.8.0 [08.05.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v1.7.0 [01.02.24]
- Updates to UI/PySide.
- Fixed scoping issue with Flame 2023.2+ menus.
<br>

### v1.6.0 [07.25.23]
- Updated to PyFlameLib v2.0.0.
<br>

### v1.5.1 [06.26.23]
- Updated script versioning to semantic versioning.
- Clip Name entry field now has focus when window opens.
- Pressing enter in Clip Name or Shot Name entry field now applies names.
<br>

### v1.5 [02.04.23]
- Added check to make sure script is installed in the correct location.
<br>

### v1.4 [01.19.23]
- Updated config file loading/saving.
<br>

### v1.3 [10.24.22]
- Updated menus for Flame 2023.2+:
- Timeline:
- Right-click on selected segments -> Rename Shots
- Media Panel:
- Right-click on selected sequence -> Rename Shots
<br>

### v1.2 [05.24.22]
- Messages print to Flame message window - Flame 2023.1 and later.
<br>

### v1.1 [05.11.22]
- Removed setup window and eliminated sequence entry to simplify UI.
