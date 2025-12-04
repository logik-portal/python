# Slate Maker

**Script Version:** 4.11.0  
**Flame Version:** 2023.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 12.29.18  
**Update Date:** 12.28.24  

**Script Type:** MediaPanel

## Description

Create slates from CSV file
<br><br>
*** DOES NOT WORK WITH FLARE ***
<br><br>
Detailed instructions to use this script can be found on pyflame.com
<br><br>
Example CSV and Text Node Template files can be found in /opt/autodesk/shared/python/slate_maker/example_files

## URL

https://github.com/logik-portal/python/slate_maker

## Menus

- Right-click on clip to be used as slate background → Slates... → Slate Maker
- Right-click on selection of clips to be used as slate backgrounds → Slates... → Slate Maker - Multi Ratio

## Installation

Copy script into /opt/Autodesk/shared/python/slate_maker

## Updates

### v4.11.0 [12.28.24]
<br>
- Updated to PyFlameLib v4.0.0.
<br>
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>
- Script now only works with Flame 2023.2+.
<br>

### v4.10.0 [08.12.24]
<br>
- Updated to PyFlameLib v3.0.0.
<br>

### v4.9.0 [01.25.24]
<br>
- Updates to UI/PySide.
<br>
- Updated to PyFlameLib v2.
<br>
- Updated script versioning to semantic versioning.
<br>

### v4.8 [02.09.23]
<br>
- Updated config file loading/saving.
<br>
- Fixed: Token button wasn't updating when csv is loaded. Script had to be restarted to update token button.
<br>
- Added check to make sure script is installed in the correct location.
<br>

### v4.7 [06.06.22]
<br>
- Messages print to Flame message window - Flame 2023.1 and later.
<br>
- Added Flame file browser - Flame 2023.1 and later.
<br>

### v4.6 [03.18.22]
<br>
- Moved UI widgets to external file.
<br>

### v4.5 [03.06.22]
<br>
- Updated UI for Flame 2023.
<br>

### v4.4 [11.16.21]
<br>
- Improved parsing of csv file.
<br>
- If current tab is MediaHub, switch to Timeline tab. Slates cannot be created in MediaHub tab.
<br>

### v4.3 [10.18.21]
<br>
- If path is typed into csv or template fields the browser will now open to those paths.
<br>
- Script now saves last path selected in browser.
<br>
- Script now creates test clip to check for Protect from Editing. Gives warning if Protect from Editing is on.
<br>

### v4.2 [10.12.21]
<br>
- Added ability to create slates of different ratios from one CSV file.
<br>
- A new menu has been created for this: Slates... -> Slate Maker - Multi Ratio
<br>
- Added progress bar.
<br>
- Updated config to xml.
<br>

### v4.0 [05.23.21]
<br>
- Updated to be compatible with Flame 2022/Python 3.7.
<br>

### v3.7 [02.12.21]
<br>
- Fixed bug causing script not to load when CSV or ttg files have been moved or deleted - Thanks John!
<br>

### v3.6 [01.10.21]
<br>
- Added ability to use tokens to name slate clip.
<br>
- Added button to convert spaces to underscores in slate clip name.
<br>

### v3.5 [10.13.20]
<br>
- More UI Updates.
<br>

### v3.4 [08.26.20]
<br>
- Updated UI.
<br>
- Added drop down menu to select CSV column for slate clip naming.
<br>

### v3.3 [04.03.20]
<br>
- Fixed UI issues in Linux.
<br>
- Main Window opens centered in linux.
<br>

### v2.6 [09.02.19]
<br>
- Fixed bug - Script failed to convert multiple occurrences of token in slate template.
<br>
- Fixed bug - Script failed when token not present in slate template for column in csv file.
