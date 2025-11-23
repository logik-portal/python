# delete iterations

**Script Version:** 1.6.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 01.23.23  
**Update Date:** 07.10.25  

**Script Type:** Batch Iterations

## Description

Delete iterations from batch groups. Keeps the specified number of iterations.
<br><br>
Modified from clean_batch_iteration.py by Autodesk.
<br><br>
Selecting a desktop will delete iterations from all batch groups in the desktop.
<br><br>
Selecting a libraries will delete iterations from all batch groups in the library including in any folders.
<br><br>
Selecting batch groups will delete iterations from the selected batch groups.
<br><br>
Selecting folders will delete iterations from all batch groups in the folders.

## URL

https://github.com/logik-portal/python/delete_iterations

## Menus

- Right-click on a desktop, library, batch group, or folder → Delete Batch Iterations

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.6.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes main window.
<br>

### v1.5.0 [03.12.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v1.4.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Script now only works with Flame 2023.2+.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v1.3.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v1.2.1 [01.29.24]
- Fixed PySide6 errors/font in slider calculator.
<br>

### v1.2.0 [01.21.24]
- Updated to PyFlameLib v2.
- Updates to UI/PySide.
<br>

### v1.1.0 [08.15.23]
- Updated to PyFlameLib v2.0.0.
<br>

### v1.0.1 [06.29.23]
- Updated script versioning to semantic versioning.
- Pressing return with the window open will now apply the settings.
