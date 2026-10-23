# Csv Renamer

**Script Version:** 1.0.1  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 05.04.26  
**Update Date:** 10.13.26  

**Script Type:** MediaPanel/Desktop

## Description

Rename selected clips and sequences using names chosen from a CSV file.

## Usage

1. Right-click selected clips/sequences and choose CSV Renamer.
2. Select a CSV file when prompted.
3. Choose the clip/sequence to rename from the Selected Clips menu.
4. Click a cell in the CSV table to use as the new name.
5. Click Rename Clip or press Enter to apply the rename.
<br><br>
Note: If multiple selected clips share the same name, a numeric suffix is appended to each duplicate entry in the menu (e.g. Shot_010 (1), Shot_010 (2)).

## URL

https://logik-portal.com/scripts/csv_renamer

## Menus

### Media Panel/Desktop
- Right-click on selected clips/sequences → CSV Renamer

## Installation

Copy script into /opt/Autodesk/shared/python/csv_renamer

## Updates

### v1.0.1 [10.13.26]
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.0.0 [05.04.26]
- Initial release.
