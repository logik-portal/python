# Uber Save

**Script Version:** 5.1.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 07.28.19  
**Update Date:** 08.18.26  

## Description

Save/Save Iterate one or more batch groups to the set path by right-clicking on a selection of batch groups in the desktop or an
open batch group in the batch view.

## Usage

To save batch groups to a custom path, create a new path in the script setup window(Flame Main Menu -> Logik -> Logik Portal Script Setup ->
Uber Save Setup) then select it in the dropdown menu and save.
<br><br>
If multiple paths have been created, the one selected in the dropdown menu will be used to save batch groups.
<br><br>
The path can be tokenized using the following tokens:
<ProjectName> - Adds name of current Flame project to path
<ProjectNickName> - Adds Flame project nicknick to path
<DesktopName> - Adds name of current desktop to path
<SeqName> - Will try to guess shot seqeunce name from the batch group name - for example: PYT_0100_comp will give a sequence name of: pyt
<SEQNAME> - Will do the same as above but give the sequence name in all caps - for example: PYT_0100_comp will give a sequence name of: PYT
<ShotName> - Adds shot name to path. Will first try getting shot name from batch group tag, then render/write node, then it will try to
guess shot name from batch group name - for example: PYT_0100_comp will give a shot name of: PYT_0100.
<BatchGroupName> - Adds name of batch group to path
<YYYY> - Adds current year to path
<YY> - Adds current year to path (last two digits)
<MM> - Adds current month to path
<DD> - Adds current day to path

## URL

https://github.com/logik-portal/python/uber_save

## Menus

- Flame Main Menu → Logik → Logik Portal Script Setup → Uber Save Setup
- Right-click selected batchgroups in desktop → Uber Save... → Save Selected Batchgroups
- Right-click selected batchgroups in desktop → Uber Save... → Iterate and Save Selected Batchgroups
- Right-click on desktop in media panel → Uber Save... → Save All Batchgroups
- Right-click in batch → Uber Save... → Save Current Batchgroup
- Right-click in batch → Uber Save... → Iterate and Save Current Batchgroup

## Installation

Copy script into /opt/Autodesk/shared/python/uber_save

## Updates

### v5.1.0 [08.18.26]
- Simplified/improved the process of creating and saving paths further.
- Updated to PyFlameLib v5.6.0.
<br>

### v5.0.0 [06.07.25]
- Updated to PyFlameLib v5.0.0.
- Removed Preset Manager for simplicity. Presets are now saved in script setup window.
<br>

### v4.9.0 [04.10.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v4.8.0 [12.03.25]
- Fixed misc bugs.
- Batch Group tagging can now be used to save batch groups to the correct shot folder even if the batch group doesn't have the shot name in the name.
- Updated to PyFlameLib v4.0.0.
- Script now only works with Flame 2023.2+.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v4.7.0 [10.02.24]
- Updated to PyFlameLib v3.2.0.
<br>

### v4.6.0 [06.13.24]
- Added path tokens for Year (YYYY), Year (YY), Month (MM), and Day (DD).
<br>

### v4.5.0 [05.05.24]
- Simplified tokenzied path setup.
- Added BatchGroupName token to available path tokens. This will add the name of the selected batch group to the path.
- Updated Preset Manager to use new PyFlamePresetManager class.
- Updates to UI/PySide.
- Updated to pyflame lib v2.2.0.
- Updated script versioning to semantic versioning.
<br>

### v4.4 [03.03.23]
- Updated config file loading/saving.
- Added check to make sure script is installed in the correct location.
- Updated menus for Flame 2023.2+.
- Improvements to Preset Window.
<br>

### v4.3 [06.20.22]
- Messages print to Flame message window - Flame 2023.1 and later.
- Added Flame file browser - Flame 2023.1 and later.
- Preset window code cleaned up and moved to imported pyflame_lib.
- Default preset can now be set in the preset window.
- Uber Save menu was incorrectly showing up when right-clicking on batch groups saved in a desktop that is saved to the library. Batch
- groups can not be saved from the library. This menu no longer shows up.
<br>

### v4.2 [03.18.22]
- Moved UI widgets to external file (pyflame_lib.py).
<br>

### v4.1 [03.06.22]
- Updated UI for Flame 2023.
<br>

### v4.0 [12.28.21]
- Added ability to save presets so different settings can be used with different Flame projects.
<br>

### v3.2 [10.11.21]
- Removed JobName token - not needed with new project nick name token.
- Removed Desktop Name token.
- Shot name token improvements.
<br>

### v3.1 [07.10.21]
- Fixed problem when trying to save on a flare. Added check for flame and flare batch folders.
- ProjectName token now uses exact flame project name. No longer tries to guess name of project on server. If flame
- project name is different than server project name, set flame project nickname and use ProjectNickName token.
- Fixed sequence token when using batch group name as save type.
<br>

### v3.0 [06.08.21]
- Updated to be compatible with Flame 2022/Python 3.7.
- Improvements to shot name detection.
- Speed improvements when saving.
<br>

### v2.0 [10.08.20:]
- Updated UI.
- Improved iteration handling.
- Added SEQNAME token to add sequence name in caps to path.
<br>

### v1.91 [05.13.20:]
- Fixed iterating: When previous iterations were not in batchgroup, new itereations would reset to 1.
- Iterations now continue from current iteration number.
<br>

### v1.9 [03.10.20:]
- Fixed Setup UI for Linux.
<br>

### v1.7 [12.29.19:]
- Menu now appears as Uber Save in right-click menu.
