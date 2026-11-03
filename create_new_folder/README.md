# Create New Folder

**Script Version:** 1.0.0  
**Flame Version:** 2025.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 11.03.26  
**Update Date:** 11.03.26  

**Script Type:** MediaHub Files

## Description

Adds a pop-up entry field for naming new folders created in the MediaHub Files tab.
Useful for creating folders when the on-screen keyboard preference is off in Flame preferences.
<br><br>
Nested paths such as new_folder/new_folder can be entered. Every missing folder in the path is created.
<br><br>
The name is checked before anything is created. It must be relative (no / at the start), with no empty,
. or .. parts, no \ : * ? " < > | or control characters, no spaces at the start or end of a part, and no part longer than 255 bytes. The folder to create in must still exist and be writable, and the new folder must not already exist.

## Usage

With one or more folders selected, the new folder is created inside each selected folder.
With nothing selected, the new folder is created in the folder MediaHub is showing.
<br><br>
Enter the folder name, or a path such as new_folder/new_folder, then press Create or Return.

## URL

https://logik-portal.com/scripts/create_new_folder

## Menus

- Right-click in MediaHub Files with a folder selected or nothing selected → Create New Folder

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.0.0 [11.03.26]
- Initial release.
