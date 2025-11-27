# Auto Scale XMLs

**Script Version:** 1.0.0  
**Flame Version:** 2025  
**Written by:** John Geehreng  
**Creation Date:** 12.06.24  
**Update Date:** 10.22.25  

**Script Type:** MediaPanel

## Description

The goal is to be able to select multiple xmls that have been run through the fix premiere xmls script at various resolutions using a json file.

## Menus

- Media Panel → UC Timelines → Auto Scale XML's

## Installation

Copy script into your python folder, typically /opt/Autodesk/shared/python/auto_scale_xmls or wherever you keep your scripts

## Updates

### v1.0.0 [10.22.25]
<br>
- use flame.projects.current_project.project_folder to determine where to save json's and action's
<br>

### v0.7 [12.27.24]
<br>
- customized for Uppercut
<br>

### v0.6 [12.27.24]
<br>
- Added Build Resolution list options
<br>

### v0.5 [12.18.24]
<br>
- added Track and Segment checks. made folder names more flexible
<br>

### v0.4 [12.14.24]
<br>
- Assumes there aren't multiple versions in the xmls
<br>

### v0.3 [12.09.24]
<br>
- Added script_path = os.path.abspath(os.path.dirname(__file__)) for centralized workflows
<br>

### v0.2 [12.09.24]
<br>
- Deleting the actions, creating new ones, and loading the target action seems to fix the resize/xml bug. (Lines 273 - 275)
<br>

### v0.1 [12.06.24]
<br>
- Inception
