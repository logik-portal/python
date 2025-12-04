# Multi Batch Render

**Script Version:** 4.13.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 12.12.18  
**Update Date:** 07.10.25  

**Script Type:** Batch / Media Panel Desktop

## Description

Batch render multiple batch groups

## URL

https://github.com/logik-portal/python/multi_batch_render

## Menus

- Right-click in batch → Multi-Batch Render
- Right-click selected batch groups in desktop → Render Selected Batch Groups

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v4.13.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Added Background Reactor render option.
- Escape key closes window.
<br>

### v4.12.0 [03.11.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v4.11.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Script now only works with Flame 2023.2+.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v4.10.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v4.9.0 [01.21.24]
- Updates to UI/PySide.
<br>

### v4.8.0 [07.08.23]
- Updated to PyFlameLib v2.0.0.
<br>

### v4.7.1 [06.26.23]
- Updated script versioning to semantic versioning.
- Render button is now blue.
- Pressing return in main window will now start render.
<br>

### v4.7 [05.23.23]
- Fixed bug with Smart Replace getting turned off when rendering.
<br>

### v4.6 [02.04.23]
- Updated config file loading/saving.
- Added check to make sure script is installed in the correct location.
<br>

### v4.5 [09.06.22]
- Updated menus for Flame 2023.2+:
- Right-click in batch -> Multi-Batch Render
- Right-click selected batch groups in desktop -> Render Selected Batch Groups
<br>

### v4.4 [05.27.22]
- Messages print to Flame message window - Flame 2023.1+.
- Fixed Exit Flame button.
- Added confirmation dialog for Exit Flame button.
<br>

### v4.3 [03.14.22]
- Moved UI widgets to external file - Added new render progress window.
<br>

### v4.2 [02.25.22]
- Updated UI for Flame 2023.
- Updated config to XML.
- Burn button removed - no ability to test.
<br>

### v4.1 [05.19.21]
- Updated to be compatible with Flame 2022/Python 3.7.
<br>

### v3.5 [11.29.20]
- More UI enhancements / Fixed Font for Linux.
- Misc bug fixes.
- Batch groups that fail to render won't stop script. Failed batch group renders listed when all renders are complete.
<br>

### v3.2 [08.10.20]
- Updated UI.
<br>

### v3.1 [07.26.20]
- Save/Exit button added to main render window. This will save the project and exit Flame when the render is done.
- Fixed errors when attempting to render from desktop with multiple batch groups with same name.
<br>

### v3.0 [07.09.20:]
- Fixed errors when attempting to render batch groups with no Render or Write nodes. These batch groups will now be skipped.
- Code cleanup.
<br>

### v2.91 [05.18.20:]
- Render menu no longer incorrectly appears when selecting a batchgroup in a Library or Folder.
<br>

### v2.9 [02.23.20:]
- Render window now centers in linux.
- Script auto replaces all render and write nodes. Works as a fix for when render/write nodes stop working in batch.
- Added menu to render current batch to batch menu. Render... -> Render Current - Use when getting errors with existing render and write nodes.
<br>

### v2.8 [02.09.20:]
- Window can now be resized.
- Fixed bug with Close Batch After Rendering checkbox - showed as checked even after being unchecked.
- Burn button updated when checked or unchecked in setup.
<br>

### v2.7 [11.06.19]
- Menu now appears as Render... when right-clicking on batch groups and in the batch window.
- Removed menu that showed up in media panel when right clicking on items that could not be rendered.
<br>

### v2.6 [10.13.19]
- Add option in main setup that will close batch groups when renders are done.
- Removed menu that showed up when clicking on items in media panel that could not be rendered.
