# Tag Tools

**Script Version:** 1.5.1  
**Flame Version:** 2025.1  
**Written by:** Kyle Obley  
**Creation Date:** 03.12.26  
**Update Date:** 09.12.26  

**Script Type:** Media Panel, Media Hub

## Description

Manages tags on sequences to be used later in QTs with the objective
of being able to track original sequence name from Flame vs client name
as well as audio.
<br><br>
See:
https://forum.logik.tv/t/python-tag-tools-internal-name-client-name-management/
https://github.com/kmatchbox/PythonHooks/tree/main/tag_tools
<br><br>
Very much a work in progress.

## Menus

- Flame Media Panel → Right-click → Tag Tools
- Flame Media Hub → Right-click → Tag Tools

## Installation

Copy script into /opt/Autodesk/shared/python/tag_tools

## Updates

### v1.5.1 [09.12.26]
- Adjusted formating to adhear to Logik-Portal requirements.
<br>

### v1.5 [07.01.26]
- Added ability to use the selected sequences and try to match those to QTs at a choosen location.
- If a match is found, the tags are copied from the sequence to the QT. This allows you to bypass
- the exporter all together so long as the sequence name matches the file name exactly.
<br>

### v1.4.2 [07.01.26]
- Added export between marks option.
<br>

### v1.4.1 [03.20.26]
- Fixed object has no attribute 'set_focus' error.
<br>

### v1.4 [03.19.26]
- Updated qt_metadata library to be more strict. Files were failing to open on MacOS 26
- within QuickTime player & Preview.
<br>

### v1.3 [03.16.26]
- CSV import/export support.
- PyFlame config now working.
<br>

### v1.2 [03.14.26]
- Added ability to rename files on the filesystem to internal/external name.
<br>

### v1.1 [03.13.26]
- Added ability to read/set tags from imported QT.
- Added ability to dump the contents of selected QT fiels within the media panel
- to the terminal.
- Added UI via PyFlameUI Builder
- Added ability to export from Flame and set the metadata afterwards. Current
- this is only working in the foreground. Need to figure out Backburner.
<br>

### v1.0 [03.12.26]
- Initial release.
