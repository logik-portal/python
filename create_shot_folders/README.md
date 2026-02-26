# Create Shot Folders

**Script Version:** 5.5.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.09.18  
**Update Date:** 02.18.26  

**Script Type:** MediaPanel

## Description

Create shot folders in the Media Panel and/or file system based on folder structure templates.
<br><br>
Custom folder structure templates can be set up in the script setup window.

## URL

https://github.com/logik-portal/python/create_shot_folders

## Menus

### Script Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Create Shot Folders Setup
### Media Panel
- Right-click in Media Panel → Create Shot Folders
- Right-click on selected clips in Media Panel → Create Shot Folders (From Clips)
### MediaHub
- Right-click on selected folder in MediaHub → Create Shot Folders
### Timeline
- Right-click on selected timeline segments in Media Panel → Create Shot Folders (From Segments)

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v5.5.0 [02.18.26]
- Create shot folders for selected clips in Media Panel.
- Create shot folders for selected timeline segments.
- Set folder location for selected clips or segments for shot folders. (Setup Window)
- Create shot folders in MediaHub at selected folder location.
- Export clips to file system folders.
- Set location of plate export folders in file system folders. (Setup Window)
- Set render type. Foreground or Background.
<br>

### v5.4.0 [08.27.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes out of windows.
- Fixed: Reveal in Finder button was not disabled when File System Folders button was unchecked.
<br>

### v5.3.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v5.2.0 [01.02.25]
- Updated to PyFlameLib v4.1.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2025.1+.
<br>

### v5.1.0 [10.01.24]
- Updated to PyFlameLib v3.2.0.
<br>

### v5.0.1 [09.15.24]
- Shot Folder top level item in folder tree can no longer be edited.
<br>

### v5.0.0 [09.09.24]
- Split off from Create Shot script.
- Updated to PyFlameLib v3.0.0.
