# uber save

**Script Version:** 4.9.0  
**Flame Version:** 2023.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 07.28.19  
**Update Date:** 04.10.25  

**Script Type:** Batch / Media Panel

## Description

Save/Save Iterate batch group iteration and batch setup file to custom path in one click.

## Usage

Uber Save Preset Manager Window:
<br><br>
- Manage multiple presets for Uber Save. Presets can be set as default for all Flame projects or for the current Flame project.
<br><br>
New:
Opens Uber Save Main Window to create new preset.
<br><br>
Edit:
Opens Uber Save Main Window to edit selected preset.
<br><br>
Duplicate:
Duplicates the selected preset. The new preset will have the same name as the original preset with COPY added at the end.
<br><br>
Delete:
Deletes the selected preset.
<br><br>
Set Default Preset:
Makes selected preset the default for all Flame projects.
<br><br>
Set Project Preset:
Makes selected preset the preset for the current Flame project. Overrides default preset for current project.
<br><br>
Remove Project Preset:
Removes preset from current project. Default preset will be used for current project. Does not delete the preset.
<br><br>
Uber Save Main Window
<br><br>
Preset Name:
Set name for preset.
<br><br>
Batch Save Path:
Use this to define a tokenized folder structure to save batch setups to.
<br><br>
Tokens:
- <ProjectName> - Adds name of current Flame project to path
- <ProjectNickName> - Adds Flame project nicknick to path
- <DesktopName> - Adds name of current desktop to path
- <SeqName> - Will try to guess shot seqeunce name from the batch group name - for example: PYT_0100_comp will give a sequence name of: pyt
- <SEQNAME> - Will do the same as above but give the sequence name in all caps - for example: PYT_0100_comp will give a sequence name of: PYT
- <ShotName> - Adds shot name to path. Will first try getting shot name from render/write node. If not found, will try to guess shot name
from batch group name - for example: PYT_0100_comp will give a shot name of: PYT_0100.
- <BatchGroupName> - Adds name of batch group to path
- <YYYY> - Adds current year to path
- <YY> - Adds current year to path (last two digits)
- <MM> - Adds current month to path
- <DD> - Adds current day to path
<br><br>
Example:
- /opt/Autodesk/project/<ProjectName>/batch/flame/<ShotName>
<br><br>
Batch Group Shot Name Tagging
<br><br>
You can now tag batch groups with a specific shot name using the format:
ShotName: <shot_name>
<br><br>
Example:
<br><br>
- Batch Group Name: tracking_fix
- Batch Group Tag: ShotName: PYT_0100_comp
- Save Path Template: /JOBS/<ProjectName>/Shots/<ShotName>/Batch
<br><br>
- Result: /JOBS/<ProjectName>/Shots/PYT_0100/Batch
<br><br>
This allows you to save batch groups to the correct shot folder even when
the batch group name doesn't contain the shot name.

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
