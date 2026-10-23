# Color Segment Fx

**Script Version:** 1.5.1  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.02.24  
**Update Date:** 10.21.26  

**Script Type:** Timeline

## Description

Colors segments on selected sequence with selected FX type.
<br><br>
Clear All Color removes color from every colored segment in the selected sequences.

## URL

https://logik-portal.com/scripts/color_segment_fx

## Menus

- Right-Click on Sequence in Media Panel → Color Segment FX

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.5.1 [10.21.26]
- Fixed Apply Color stopping partway when a segment can't be read.
- Fixed error when items other than sequences are selected along with a sequence.
- Added Clear All Color button. Clears color from all colored segments in the selected sequences.
- Fixed No Color and Clear All Color not clearing colors set in Flame.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.5.0 [03.24.26]
- Update to PyFlameLib v5.3.0.
<br>

### v1.4.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes main window.
- Window layer order in linux is now fixed.
<br>

### v1.3.0 [03.16.25]
- Updated to PyFlameLib v4.3.0.
- Added 'No Color' option to color menu and removed 'Remove Color' button.
<br>

### v1.2.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v1.1.0 [08.05.24]
- Updated to PyFlameLib v3.0.0.
