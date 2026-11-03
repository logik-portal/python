# Batch Group To Shot Folders

**Script Version:** 1.1.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.02.26  
**Update Date:** 11.02.26  

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
If a batch group with the same name is already in the destination folder, choose Replace, Replace All, Add or Cancel.
Batch groups already in their destination folder are skipped, and batch groups in the selection are never replaced.
<br><br>
Script menu will not show up if the current tab is MediaHub.

## URL

https://logik-portal.com/scripts/batch_group_to_shot_folders

## Menus

### Setup
- Flame Main Menu →  Logik → Logik Portal Script Setup → Batch Group to Shot Folders Setup
### To Move Batch Groups
- Right-click on selected batch groups in Media Panel/Desktop → Batch Group to Shot Folders → Move to Shot Folders
### To Copy Batch Groups
- Right-click on selected batch groups in Media Panel/Desktop → Batch Group to Shot Folders → Copy to Shot Folders

## Installation

Copy script into /opt/Autodesk/shared/python/batch_group_to_shot_folders

## Updates

### v1.1.0 [11.02.26]
- Fixed Replace deleting a selected batch group when a same-named batch group in the selection is processed first. Batch groups in the selection are never deleted.
- Fixed Replace deleting a batch group that is already in its destination folder. Batch groups already in their destination folder are now skipped.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.0.0 [06.11.26]
- Initial release.
