# Csv To Markers

**Script Version:** 1.3  
**Flame Version:** 2022  
**Written by:** Andy Milkis, Jacob Silberman-Baron, John Geehreng  
**Creation Date:** 07.11.22  
**Update Date:** 11.07.22  

## Description

Imports a CSV file exported from frame.io and adds markers to a clip in flame. There is no need to modify the CSV downloaded from FrameIO.

## Menus

- Right-click on a clip in the Media Panel -→ Add Timeline Markers -→ Select CSV File
- Right-click on a segment in the timeline -→ Add Segment Markers -→ Select CSV File

## Updates

### v1.3 [(11.07.22 JG)]
- Added Flame 2023.1 Browser option, 2023.2 Print to Console message if it can't find the "Timecode In" header, Timeline Segment scopes,
- minimumVersion of 2022 scopes, CSV File Filters, and default path of ~/Downloads

### v1.2 [(7.11.22 JS-B)]
- Removed the CSVFileSelector Object and replaced it with a generic QFileDialog
