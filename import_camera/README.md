# Import Camera

**Script Version:** 4.16.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.02.18  
**Update Date:** 08.27.25  

## Description

Creates a new Action node with selected FBX or Alembic file loaded.
<br><br>
The Action camera will be automatically switched to the new FBX/Alembic camera.
<br><br>
Options to load with simple re-comp or ST map setups.

## URL

https://github.com/logik-portal/python/import_camera

## Menus

### Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Import Camera Setup
### To Import
- Right-click in batch or on selected node → Import... → Import FBX Camera
- Right-click in batch or on selected node → Import... → Import Alembic Camera

## Installation

Copy script into /opt/Autodesk/shared/python/import_camera

## Updates

### v4.16.0 [08.27.25]
- Updated to PyFlameLib v5.0.0.
- Escape key closes main window.
- Added warning message when importing ST Map Matchbox Setup without background clip or node with background resolution selected.
- ST Map and camera track aren't applied properly without the background clip or node with background resolution selected.
<br>

### v4.15.0 [03.12.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v4.14.0 [12.27.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v4.13.0 [08.04.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v4.12.0 [05.09.24]
- Added two new options for working with ST Maps:
- ST Map Matchbox Setup - Uses UVMap_3vis matchbox for undistort and redistort.
- ST Map Node Setup - Flame 2025+ only. Uses Flame ST Map node for undistort and redistort.
- Removed Action node ST Map setup option.
- Added new buttons (These are not enabled when Import Type is Read File):
- Linearize Keyframes - Set camera keyframes to linear. Helps with motion blur on first and last frames.
- Consolidate Geometry - Alembic setting only. Consolidates geometry into a single object.
- Create Object Group - Alembic setting only. Creates a group for each object in the Alembic file.
- Load objects - Choose which objects to load from FBX/Alembic file:
- Cameras
- Models
- Lights
- Mesh Animations
- Normals
- Fixed Tokenzied path not working properly.
- Fixed Linearize keyframes. Was crashing script when applied to loading FBX/ABC files as Read Files.
- Cleaned up duplicate node naming code.
<br>

### v4.11.2 [02.25.24]
- Misc UI fixes.
<br>

### v4.11.1 [01.29.24]
- Fixed PySide6 errors/font in slider calculator.
<br>

### v4.11.0 [01.02.24]
- Updates to UI/PySide.
<br>

### v4.10.0 [07.26.23]
- Updated to pyflame lib v2.0.0.
<br>

### v4.9.1 [06.26.23]
- Updated script versioning to semantic versioning.
- Load button is now blue.
- Pressing return in the main window will now load the selected camera.
<br>

### v4.9 [03.14.23]
- Fixed: ST Map Setup - Resize node setup is not being saved with correct name in 2024.
<br>

### v4.8 [02.04.23]
- Added check to make sure script is installed in the correct location.
<br>

### v4.7 [01.17.23]
- Moved setup menu for Flame 2023.2+ to: Flame Main Menu -> Logik -> Logik Portal Script Setup -> Import Camera Setup
- Fixed not being able to load setup window.
- Updated config file loading/saving.
- Fixed: ST Map Setup - Selecting an image other than the undistort map would cause the script to fail.
<br>

### v4.6 [01.02.23]
- Fixed not being able to select Alembic files in the import browser.
- Minimum Flame version is now 2022.3.
- Ability to set tokenized path to always open browser to when importing: Flame Main Menu -> pyFlame -> Import Camera Setup
- By default this is turned off.
- Patch Setup button renamed to ReComp Setup for clarity.
<br>

### v4.5 [07.28.22]
- Camera keyframe extrapolation is now set to linear to help with motion blur.
<br>

### v4.4 [05.26.22]
- Added new flame browser window - Flame 2023.1 and later.
- Messages print to Flame message window - Flame 2023.1 and later.
<br>

### v4.3 [03.15.22]
- Moved UI widgets to external file.
<br>

### v4.2 [02.25.22]
- Updated UI for Flame 2023.
- Updated config to XML.
<br>

### v4.1 [01.04.22]
- Files starting with '.' are ignored when searching for undistort map after distort map is selected.
<br>

### v4.0 [05.22.21]
- Updated to be compatible with Flame 2022/Python 3.7.
- Redistort map will automatically be found if in the same folder as undistort map.
- Speed improvements.
<br>

### v3.6 [02.21.21]
- Updated UI.
- Improved calculator.
- Plate resize node in ST Map Setup now takes ratio from st map.
<br>

### v3.5 [01.25.21]
- Added ability to import Alembic(ABC) files.
- Fixed UI font size for Linux.
<br>

### v3.4 [11.05.20]
- Updates to paths and description for Logik Portal.
<br>

### v3.3 [10.18.20]
- ST Map search no longer case sensitive.
- If ST Map not found, file browser will open to manually select.
<br>

### v3.2 [10.12.20]
- Improved spinbox with calculator.
<br>

### v3.1 [09.26.20]
- Updated UI
- Import FBX with Patch Setup - Will import FBX into an Action node and also create
- other nodes to re-comp work done in FBX Action over original background.
- Import FBX with ST map Setup - Will import FBX into an Action node and also build
- a undistort/redistort setup using the ST maps. ST maps must be in the same folder or sub-folder of
- FBX camera for this to work. ST Maps should also contain 'undistort' or 'redistort' in their file
- names.
<br>

### v3.0 [06.06.20]
- Code re-write
- Add FBX Action under cursor position
- Fixed UI in Linux
