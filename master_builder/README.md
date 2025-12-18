# Master Builder

**Script Version:** 1.6.0  
**Flame Version:** 2025  
**Written by:** Michael Vaglienty  
**Creation Date:** 02.09.22  
**Update Date:** 05.28.25  

**Script Type:** Reel Group

## Description

Create masters from clips/sequences in a Reel Group.
<br><br>
Each reel should contain one part of the final master. For example:
<br><br>
Reel 1 - color bars
Reel 2 - slates
Reel 3 - edits
<br><br>
Reels that contain one clip will have that clip added to every master created.
<br><br>
Reels that contain multiple clips will cause the script to make a new master from each clip.
<br><br>
For instance if there are: 1 2-second clip of color bars, 4 slates, 4 edits, and 1 1-second clip of black
the script will create 4 edits with each one containing: color bars, a slate, edit, and 1 second clip of black.
<br><br>
Black is automatically inserted into timeline gaps between clips on the primary track.
<br><br>
Reels containing more than one clip must have an equal number of clips. If there are 4 slates, there
should be 4 edits.
<br><br>
Other things to keep in mind:
<br><br>
All clips must have proper record timecode set for placement in timeline.
<br><br>
Each reel should contain either all clips or all sequences. Clips and sequences
should not be mixed within the same reel.
<br><br>
Sequences can contain multiple tracks but not multiple versions.

## Menus

- Right-click on Reel Group → Master Builder

## Installation

Copy script into /opt/Autodesk/shared/python/master_builder

## Updates

### v1.6.0 [05.28.25]
- Updated to PyFlameLib v5.0.0.
<br>

### v1.5.0 [04.13.25]
- Updated to PyFlameLib v4.3.0.
- Added support for PyFlameTabWidget.
<br>

### v1.4.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
<br>

### v1.3.0 [08.24.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v1.2.0 [02.06.24]
- Black is now automatically inserted into timeline gaps between clips.
- Updates to UI/PySide.
- Updated to PyFlameLib v2.0.0.
- Updated script versioning to semantic versioning.
- Updated menu for Flame 2023.2.
<br>

### v1.1 [06.08.22]
- Messages print to Flame message window - Flame 2023.1 and later
