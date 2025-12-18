# Invert Axis

**Script Version:** 2.10.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 07.26.19  
**Update Date:** 12.18.25  

**Script Type:** Action / GMask Tracer

## Description

Create inverted axis at current frame or copy parent axis and invert at current frame.

## Menus

### Action Axis Nodes
- Right-click on axis node → Axis... → Create Inverted Axis At Current Frame
- Right-click on axis node → Axis... → Invert Parent Axis At Current Frame
### GMask Tracer Axis Nodes
- Right-click on axis node → Axis... → GMask - Create Inverted Axis At Current Frame
- Right-click on axis node → Axis... → GMask - Invert Parent Axis At Current Frame

## Installation

Copy script into /opt/Autodesk/shared/python/invert_axis

## Updates

### v2.10.0 [12.18.25]
- Updated to PyFlameLib v5.1.1.
<br>

### v2.9.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v2.8.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Script now only works with Flame 2023.2+.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v2.7.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.6.0 [01.19.24]
- Updates to PySide.
<br>

### v2.5.0 [07.27.23]
- Updated to PyFlameLib v2.0.0.
- Updated versioning to semeantic versioning.
<br>

### v2.4 [07.17.22]
- Messages print to Flame message window - Flame 2023.1 and later.
- Fixed: Right-clicking in Action or GMask Tracer with no axis selected causes error to show in shell.
<br>

### v2.3 [03.25.22]
- Now works with axis nodes in GMask Tracer in Flame 2023.
<br>

### v2.2 [11.12.21]
- Changed menu name to Axis...
<br>

### v2.1 [10.26.21]
- Script now works when media layer is selected instead of action node.
<br>

### v2.0 [05.23.21]
- Updated to be compatible with Flame 2022/Python 3.7.
- Fixed inverting axis not working when multiple axis parented to same axis.
<br>

### v1.5 [05.10.20]
- Inverted axis is now added as child of selected axis.
<br>

### v1.3 [10.24.19]
- Menu's now show up under Invert Axis... when right-clicking on axis node in action schematic.
- Removed menu's from showing up in GMask Tracer. Action python commands do not work in GMask Tracer.
