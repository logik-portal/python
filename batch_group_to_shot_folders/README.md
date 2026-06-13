# Batch Group To Shot Folders

**Script Version:** 1.0.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.02.26  
**Update Date:** 06.11.26  

## Description

Copy or Move selected batch groups to folders in the Media Panel using a tokenized path.

## Usage

Tokenized path is used to determine the destination folder for the batch groups.
<br><br>
The tokenized path structure is: <LibraryName>/<FolderPath>
<br><br>
If the Library and/or Folder structure does not exist for a batch group, it will be created.
<br><br>
Example Tokenized Path:
Shot Folders/<SEQNAME>/<ShotName>/Batch_Groups
<br><br>
Example batch group name:
PYT_0010_comp
<br><br>
This would create the following folder structure with the batch group going into the Batch Groups folder:
Library: Shot Folders
Folder Path: PYT/PYT_0010/Batch_Groups
<br><br>
Batch groups must be named with a standard shot name or be tagged with a shot name tag.
<br><br>
Example Batch Group Names:
PYT_0010_comp
PYT0010_comp
PYT010_comp
PYT_010_comp
PYT_0010
PYT0010
PYT010
<br><br>
Example Shot Name Tags:
ShotName: PYT_0010
ShotName: PYT0010
ShotName: PYT010
<br><br>
Script menu will not show up if the current tab is MediaHub.

## Menus

### Setup
- Flame Main Menu →  Logik → Logik Portal Script Setup → Batch Groups to Folders Setup
### To Move Batch Groups
- Right-click on selected batch groups in Media Panel/Desktop → Move Batch Groups to Folders
### To Copy Batch Groups
- Right-click on selected batch groups in Media Panel/Desktop → Copy Batch Groups to Folders

## Installation

Copy script into /opt/Autodesk/shared/python/batch_group_to_shot_folders

## Updates

### v1.0.0 [06.11.26]
- Initial release.
