# shot sheet maker

**Script Version:** 3.13.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 02.18.19  
**Update Date:** 07.10.25  

**Script Type:** MediaPanel

## Description

Create shot sheets from selected sequence clips that can be loaded into Excel, Google Sheets, or Numbers.
<br><br>
Shot sheets can be created individually for each sequence or all selected sequences can be added to a
single spreadsheet as separate worksheets.
<br><br>
Sequence should have all clips on one version/track.
<br><br>
*** First time script is run it will need to install xlsxWriter - System password required for this ***
This will need to happen for each new version of Flame.

## URL

https://github.com/logik-portal/python/shot_sheet_maker

## Menus

- Right-click on selected sequences in media panel → Export Shot Sheet

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v3.13.0 [07.10.25]
- Images are linked to cells when opening shot sheet in Excel.
- Option to save images to shot sheet export path.
- Updated to PyFlameLib v5.0.0.
- The tab key can now be used to cycle through all the entries in the Edit Column Names window.
<br>

### v3.12.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v3.11.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v3.10.0 [08.06.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v3.9.1 [06.06.24]
- Small UI fixes/adjustments.
<br>

### v3.9.0 [01.21.24]
- Updates to UI/PySide.
<br>

### v3.8.0 [11.16.23]
- Added ability to add Shot Frame In and Shot Frame Out to clip info column and column names.
- Added drop down menus to add clip info to column names in Edit Column Names window.
<br>

### v3.7.1 [11.07.23]
- Fixed incorrect path in script path check error message.
<br>

### v3.7.0 [08.20.23]
- Updated to PyFlameLib v2.0.0.
<br>

### v3.6.0 [06.26.23]
- Pressing return in the main window will now create shot sheets.
- Updated script versioning to semantic versioning.
- Updated xlsxwriter install for Flame 2024+.
- Updated config loading/saving.
- Fixed linux install problems.
<br>

### v3.5 [01.05.23]
- Misc bug fixes.
- Error window will now pop up if the selected export path is not writable.
- Column names can be edited by clicking on the Edit Column Names button.
- By using any of the following names for a column name, the corresponding clip info will be added to the cells
- in that column.
- For example, if you want to add the Shot Name to a cell, name the column 'Shot Name' and the shot name will
- be added to the cells in that column.
<br>
- Shot Name
- Source Name
- Source Path
- Source TC
- Source TC In
- Source TC Out
- Record TC
- Record TC In
- Record TC Out
- Shot Length
- Source Length
- Comment
<br>

### v3.4 [10.04.22]
- Updated menus for Flame 2023.2+
<br>

### v3.3 [08.04.22]
- Fixed bug where script would not work properly if 'Inclusive Out Marks' was selected in Flame Timeline
- Preferences.
- Added ability to add segment comments to first column with Add Comment button.
<br>

### v3.2 [07.21.22]
- Spreadsheets can now be created from multiple sequences.
- When creating spreadsheets from multiple sequences, there is now the option(Create One Workbook) to create a
- single spreadsheet with all sequences
- added as separate worksheets.
- Fixed export issues with 2023.1.
- Messages print to Flame message window - Flame 2023.1 and later.
<br>

### v3.1 [03.25.22]
- Updated UI for Flame 2023.
- Moved UI widgets to external file.
- Updated xlsxwriter module to 3.0.3.
- Gaps in timeline no longer cause script to crash.
- Misc improvements and bug fixes.
- Config updated to XML.
<br>

### v3.0 [05.28.21]
- Updated to be compatible with Flame 2022/Python 3.7.
- Updated UI.
- Added check to make sure sequence has only one version/track.
- Added button to reveal spreadsheet in finder when done.
<br>

### v2.2 [07.15.20]
- Script setup now in Flame Main Menu: Flame Main Menu -> pyFlame -> Shot Sheet Maker Setup.
- Window now closes before overwrite warning appears so overwrite warning is not behind window.
- Better sizing of image column to match size/ratio of sequence images.
- The following information can be added to the spreadsheet for each shot:
- Source Clip Name
- Source Clip Path
- Source Timecode
- Record Timecode
- Shot Length - Length of shot minus handles
- Source Length - Length of shot plus handles
<br>

### v2.1 [04.05.20]
- Fixed UI issues in Linux.
<br>

### v2.0 [12.26.19]
- Up to 20 columns can now be added through the Edit Column Names button.
- Thumbnail images used in the shot sheet can be saved if desired.
- Misc. bug fixes.
