# add dated and timed folders

**Script Version:** 2.4.0  
**Flame Version:** 2025  
**Written by:** John Geehreng and Michael Vaglienty  
**Creation Date:** 07.04.20  
**Update Date:** 08.27.25  

**Script Type:** MediaPanel/MediaHub Files

## Description

Create folders with the current date and time, date only, or time only.
<br><br>
Examples of date formats include: YY-MM-DD, YYYY-MM-DD, YYMMDD, etc.

## Menus

### Script Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Add Dated and Timed Folders Setup
### Create Media Panel Folders
- Right-click on library or folder → Folders → Add Dated and Timestamped Folders
- Right-click on library or folder → Folders → Add Dated Folder
- Right-click on library or folder → Folders → Add Timestamped Folder
### Create MediaHub Files Folders
- Right-click on folder → Folders → Add Dated and Timestamped Folders
- Right-click on folder → Folders → Add Dated Folder
- Right-click on folder → Folders → Add Timestamped Folder

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.4.0 [08.27.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes setup window.
- Window layer order in linux is now fixed.
- Time is now always given as four digits.
<br>

### v2.3.0 [04.07.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v2.2.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v2.1.1 [12.20.24]
- MediaHub is now refreshed after creating folders.
<br>

### v2.1.0 [05.21.24]
- Added ability to create folders in the MediaHub Files tab.
<br>

### v2.0.0 [04.23.24]
- Date and time formats are now customizable from the script setup:
- Flame Main Menu -> Logik -> Logik Portal Script Setup -> Add Dated and Timed Folders Setup
<br>

### v1.1.0 [03.02.21]
- Updated to work with strftime
