# Import St Maps

**Script Version:** 3.1.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 04.30.21  
**Update Date:** 07.10.25  

**Script Type:** Batch

## Description

Imports ST Maps and builds ST Map setup
<br><br>
Comp work is recomped over original plate at end of setup

## Menus

- Right-click in batch or on selected node → Import... → Import ST Map - ST Map Node Setup

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v3.1.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v3.0.0 [03.11.25]
- Updated to PyFlameLib v4.3.0.
- Batch setups are now created with either matchbox or Flame ST Map nodes. Flame ST Map nodes are only available in Flame 2025+.
<br>

### v2.9.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v2.8.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.7.0 [01.21.24]
- Updates to PySide.
<br>

### v2.6.0 [08.20.23]
- Updated to PyFlameLib v2.0.0.
- Updated script versioning to semantic versioning.
<br>

### v2.5 [03.28.23]
- Updated config file loading/saving.
- Added check to make sure script is installed in the correct location.
- Fixed resize node saving issue that causes script to fail in 2024.
<br>

### v2.4 [05.27.22]
- Messages print to Flame message window - Flame 2023.1 and later.
<br>

### v2.3 [03.15.22]
- Updated UI for Flame 2023.
- Moved UI widgets to external file.
<br>

### v2.2 [02.17.22]
- Updated config to XML.
<br>

### v2.1 [01.04.21]
- Files starting with '.' are ignored when searching for undistort map after distort map is selected.
<br>

### v2.0 [05.19.21]
- Updated to be compatible with Flame 2022/Python 3.7.
