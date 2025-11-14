# Create Projection

**Script Version:** 2.10.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 07.09.19  
**Update Date:** 07.10.25  

**Script Type:** Flame Main Menu

## Description

Create projector or diffuse projections in Action from selected action layer.
<br><br>
Action must have another camera added other than just the default camera.

## Menus

- Right-click on Action surface or geo  → Create Projection... → Projector Projection
- Right-click on Action surface or geo  → Create Projection... → Projector Light-Linked Projection
- Right-click on Action surface or geo  → Create Projection... → Diffuse Projection

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.10.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v2.9.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v2.8.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v2.7.0 [07.22.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.6.0 [01.19.24]
- Updates to PySide.
<br>

### v2.5.0 [07.29.23]
- Updated to PyFlameLib v2.
- Updated to semantic versioning.
<br>

### v2.4 [05.26.22]
- Messages print to Flame message window - Flame 2023.1 and later
<br>

### v2.3 [03.15.22]
- Updated UI for Flame 2023
- Moved UI widgets to external file
<br>

### v2.2 [01.14.22]
- Added message when default camera is selected and should be changed to 3d camera
<br>

### v2.1 [11.15.21]
- Fixed problem creating projections when Media Layer is selected instead of Action Node
<br>

### v2.0 [05.22.21]
- Updated to be compatible with Flame 2022/Python 3.7
<br>

### v1.6 [05.16.21]
- Error when creating projection while not having action node selected fixed
<br>

### v1.5 [05.10.20]
- Fixed problem with diffuse not switching to new frame camera in Flame 2020.2 and up.
<br>

### v1.4 [10.21.19]
- Changed menu to Create Projection...
<br>

### v1.3 [09.15.19]
- Code Cleanup
