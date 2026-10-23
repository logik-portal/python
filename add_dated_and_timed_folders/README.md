# Add Dated And Timed Folders

**Script Version:** 2.8.0  
**Flame Version:** 2025.2  
**Written by:** John Geehreng and Michael Vaglienty  
**Creation Date:** 07.04.20  
**Update Date:** 10.21.26  

**Script Type:** MediaPanel/MediaHub Files

## Description

Create folders with the current date and time, date only, or time only.

## Usage

Date and time format can be customized in the script setup window.
<br><br>
Examples of date formats include: YY-MM-DD, YYYY-MM-DD, YYMMDD, etc.

## URL

https://logik-portal.com/scripts/add_dated_and_timed_folders

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
- Right-click with nothing selected → Folders → (same actions) - creates folders in the current MediaHub folder

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.8.0 [10.21.26]
- In the MediaHub if no folder is selected, new dated/timed folders can be created at whatever path the MediaHub is currently open to.
- Setup now only accepts date formats the script can use: YY or YYYY, MM and DD once each, separated by - / . or nothing. Other characters show a message listing them. A bad saved format no longer stops Setup from opening.
- Selecting a library or folder together with other items no longer fails. Only the libraries and folders are used.
- MediaHub folders are now always created inside the selected folder.
- With several libraries or folders selected, folders are created in each one that needs them. The ones that already have them are listed in one message.
- MediaHub folders that can't be created are now shown in a message with the reason.
- The script now stops cleanly if the install check fails.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v2.7.0 [06.25.26]
- Path is now copied to clipboard when creating folders in the MediaHub Files tab.
<br>

### v2.6.0 [06.18.26]
- No longer creates extra dated or timed folders if they already exist in the media panel.
<br>

### v2.5.0 [03.24.26]
- Update to PyFlameLib v5.3.0.
<br>

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
- Date and time formats are now customizable from the script setup: Flame Main Menu -> Logik -> Logik Portal Script Setup -> Add Dated and Timed Folders Setup
<br>

### v1.1.0 [03.02.21]
- Updated to work with strftime
