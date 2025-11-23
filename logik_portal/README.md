# logik portal

**Script Version:** 6.5.1  
**Flame Version:** 2023.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 10.31.20  
**Update Date:** 10.20.25  

**Script Type:** Flame Main Menu

## Description

Share/install python scripts, batch setups, inference nodes, and download matchboxes

## URL

https://github.com/logik-portal/python/logik_portal

## Menus

- Flame Main Menu → Logik → Logik Portal

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v6.5.1 [10.20.25]
- Fixed issues with inference copyright window.
<br>

### v6.5.0 [03.16.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v6.4.0 [01.09.25]
- Added ability to select where python scripts are installed. Default path is /opt/Autodesk/shared/python.
- *** When selecting a path, make sure its a path Flame will look for python scripts in and is writeable ***
- Fixed: Adding a matchbox to batch would sometimes load the wrong matchbox if it had a similar name to another matchbox.
<br>

### v6.3.0 [01.07.25]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v6.2.0 [08.31.24]
- Added disclaimer message when downloading inference nodes.
- Added notice to users uploading inference nodes that they should include links to the original source of the model and that the model should be open source.
- Fixed misc bugs.
<br>

### v6.1.0 [08.16.24]
- Added search fields to python scripts, batch setups, and inference nodes tabs.
- User is given message to save work before installing the Logik Portal from within the Logik Portal. Flame will crash but will be fine after restarting Flame.
<br>

### v6.0.0 [08.03.24]
- Added Inference Nodes tab. Allows for downloading and submitting Inference nodes.
- Updated to PyFlameLib v3.0.0.
- Removed Archive tab.
- Fixed: Matchbox not installing correctly.
- Fixed: Autodesk scripts not installing correctly.
<br>

### v5.9.1 [04.18.24]
- Fixed: Install button not properly working for python scripts. Thanks for catching Mottizle!
<br>

### v5.9.0 [03.05.24]
- Added column to python script tab to show minimum and maximum flame versions required to run script.
- Scripts that require a newer or older version of flame will be greyed out in the list and not installable.
<br>

### v5.8.2 [02.08.24]
- Python scripts can now sorted by year when clicking on year header.
- Dates are flipped from dd.mm.yy to yy.mm.dd for sorting.
- Replaced browse buttons in submit windows with clickable line edit file browsers.
<br>

### v5.8.1 [01.21.24]
- Fixed: Submit buttons not working after submitting script unless portal is restarted.
<br>

### v5.8.0 [01.18.24]
- Updates to UI/PySide.
<br>

### v5.7.1 [10.09.23]
- Fixed progress window overflow error when uploading/downloading large files.
<br>

### v5.7.0 [10.03.23]
- Progress windows added when downloading or uploading files.
- When uploading python scripts __pycache__ folder is now excluded from tar file.
- Updated to pyflame lib v2.
<br>

### v5.6.1 [06.26.23]
- Updated script versioning to semantic versioning.
- Removed old version check of python script uploads to allow for semantic versioning.
- Updated password window for uploading python scripts.
- Main tabs now longer have outline when selected in linux.
<br>

### v5.6 [03.02.23]
- Updated FTP server info.
<br>

### v5.5 [02.04.23]
- Added search to matchbox tab.
<br>

### v5.4 [02.02.23]
- Improvements to Matchbox tab:
- All current matchboxes are now listed with descriptions.
- Matchboxes can be sorted by Name, Shader Type, and Author.
- Matchboxes can be added to current batch setup.
<br>
- Added check to make sure script is installed to correct path.
- Portal now opens to last used tab.
- Portal updates will be shown on whatever tab script first opens to.
<br>

### v5.3 [01.25.23]
- Matchboxes will now install into a directory called LOGIK in the selected directory.
- Reverted menu for Flame 2023.2+ to Flame Main Menu -> Logik -> Logik Portal. Scripts downloaded from the Portal that have a setup menu
- in the future will have their menu added under Flame Main Menu -> Logik -> Logik Portal Setup -> Script Name for clarity.
- Updated config file loading/saving.
<br>

### v5.2 [01.08.23]
- Updates to the Logik Portal are now shown in the main window when the script first loads up.
<br>

### v5.1 [12.22.22]
- Fixed possible ssl error when downloading matchboxes.
<br>

### v5.0 [11.28.22]
- Updated with new FTP server.
- Autodesk python scripts provided with Flame 2023.2+ are now listed/installable through the Portal.
- Maximum archive size increased to 1GB.
<br>

### v4.2 [09.06.22]
- Updated menu for Flame 2023.2+:
- Flame Main Menu -> Logik Portal
<br>

### v4.1 [07.22.22]
- Messages print to Flame message window - Flame 2023.1+.
- Added Flame file browser - Flame 2023.1+.
- pyflame_lib files aren't shown in the installed scripts list anymore.
- Matchbox install path now defaults to  /opt/Autodesk/presets/FLAME_VERSION/matchbox/shaders
<br>

### v4.0 [03.23.22]
- Updated UI for Flame 2023.
- Moved UI widgets to external file.
<br>

### v3.0 [12.09.21]
- Getting Flame version is updated to work with new PR versioning.
- Moved a few buttons around.
<br>

### v2.9 [12.02.21]
- Python script upload login bug fix.
<br>

### v2.8 [11.17.21]
- Login info for uploading scripts only needs to be entered first time something is uploaded.
<br>

### v2.7 [10.16.21]
- Install Local button added to python tab to install python scripts from local drive.
- Improved Flame version detection.
- Script will now attempt to download matchbox collection from website. If website is down, it will download from portal ftp.
<br>

### v2.6 [09.06.21]
- Misc bug fixes / fixed problem with not being able to enter system password to load matchboxes to write protected folder.
<br>

### v2.5 [07.30.21]
- Added ability to upload/download archives - Archive size limit is 200MB.
- Config is now XML.
<br>

### v2.4 [07.23.21]
- Added python submit button back. User name and password now required to submit scripts.
- Fixed bug - files starting with . sometimes caused script to not work.
<br>

### v2.3 [07.06.21]
- Added Logik Matchbox archive to Portal FTP. Matchbox archive now stored on FTP instead of pulling directly from logik-matchbook.org.
<br>

### v2.2 [06.03.21]
- Updated to be compatible with Flame 2022/Python 3.7.
- Removed python script submission ability. Scripts can now be added through github submissions only.
<br>

### v1.6 [03.14.21]
- UI improvements/updates - UI elements to classes.
- Added contextual menus to python tab to install and delete scripts and to batch tab to download batch setups.
- User will be prompted for system password when trying to download matchboxes to protected folders such as /opt/Autodesk/presets/2021.1/matchbox/shaders.
- If newer version of installed script is available on portal it will be highlighted in portal list.
- If newer version of flame is required for a script, script entry will be greyed out.
- If newer version of flame is required for a batch setup, batch setup entry will be greyed out.
- Batch setups now properly download into paths with spaces in folder names.
- User will get message if script folder needs permissions changed to create temp folders/files.
- File browse buttons removed - browser now opens when clicking lineedit field.
- If new version of a python script is submitted old script will be removed.
<br>

### v1.5 [02.27.21]
- UI code updates.
- Fixed bug causing script to hang when reading descriptions on certain scripts.
- Fixed batch submit button.
<br>

### v1.4 [01.25.21]
- Fixed temp path for logik matchbox install.
<br>

### v1.3 [01.14.21]
- Script description info can now be entered in Portal UI instead of being in script header.
- Fixed font size for linux.
<br>

### v1.2 [12.29.20]
- Fixed problems with script running on Flame with extra .x in Flame version.
