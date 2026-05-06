# Neat Freak

**Script Version:** 2.2.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 10.22.21  
**Update Date:** 04.19.26  

**Script Type:** Batch/Media Panel/Timeline

## Description

Add Neat/Render/Write nodes to selected clips in Batch, Media Panel, or Timeline Segments.

## Usage

Neat OFX 5.x or 6.x is required!
<br><br>
Select multiple clips in Batch, Media Panel, or Timeline Segments. When selecting clips in the Media Panel, a new Batch Group will be created.
<br><br>
Render/Write node outputs are set to match each clip's: name, duration, timecode, fps, etc.
<br><br>
Using Neat Node Profiles:
<br><br>
- Using Neat Node Profiles allows for easily applying the same Neat node
settings to multiple clips bypassing having to set each Neat node manually.
<br><br>
- Enabled by default. To turn off, disable in Neat Freak setup. When
disabled, the Neat node loads with default settings. When enabled, a
prompt appears to select a Neat node profile.
<br><br>
- To create a Neat node profile: add a Neat node, go into the node and apply
desired settings, then right-click on the Neat node and select
Neat Freak... -> Save Neat Node Profile. The profile then appears in
the selection prompt. Multiple profiles can be created. Profiles
are saved per project.

## URL

https://logik-portal.com/scripts/#neat_freak

## Menus

### Script Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Neat Freak Setup
### Batch
- Right-click on any clips(s) in batch → Neat Freak... → Neat Denoise Selected Clips
### Media Panel
- Right-click on any clips(s) in media panel → Neat Freak... → Neat Denoise Selected Clips

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.2.0 [04.19.26]
- Updated to work in Flame 2027+.
- Added option to save/use Neat node profiles.
- Added ability to add Neat OFX to selected timeline segments.
- Fixed: Bug causing multiple Neat reels to be created in a batch group.
<br>

### v2.1.0 [03.28.26]
- Updated to PyFlameLib v5.3.0.
<br>

### v2.0.0 [12.18.25]
- Removed Write node options from setup. Write nodes now use default settings set in Flame Preferences(2026.2+).
- Added render destination reel options to setup.
- Added option to enable/disable render node in setup.
- Only new nodes are framed after creation.
<br>

### v1.10.0 [07.10.25]
- Updated to PyFlameLib v5.0.0.
- Tab-key cycles through entries in setup window.
<br>

### v1.9.0 [04.12.25]
- Updated to PyFlameLib v4.3.0.
- Works with Neat v6.x.
- Added check for Neat OFX plugin. If not found, show error message and return.
<br>

### v1.8.0 [01.02.25]
- Updated to PyFlameLib v4.0.0.
- Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
- Script now only works with Flame 2023.2+.
<br>

### v1.7.0 [09.09.24]
- Updated to PyFlameLib v3.0.0.
- Misc bug fixes.
<br>

### v1.6.0 [02.05.24]
- Added entry field for render node suffix name in setup.
- Added option to turn Add to Workspace on/off for Write nodes.
- Updates to UI/PySide.
- Updated to PyFlameLib v2.0.0.
- Updated script versioning to semantic versioning.
<br>

### v1.5 [02.04.23]
- Script now checks if script is installed in correct path.
<br>

### v1.4 [01.25.23]
- Render/Write nodes now take start frame into account when setting render range.
- Colour Management in render node now gets set to 16-bit float, Colour Management node is no longer needed/added.
- Updated config file loading/saving.
- Moved menus for Flame 2023.2+:
- Setup:
- Flame Main Menu -> Logik -> Logik Portal Script Setup -> Neat Freak Setup
- Batch:
- Right-click on any clip in batch -> Neat Denoise Selected Clips
- Media Panel:
- Right-click on any clip in media panel -> Neat Denoise Selected Clips
<br>

### v1.3 [08.03.22]
- Color management node added after Neat node to take render down to 16bit/float.
- Render node will try to renders to go to the Batch Renders shelf reel if other shelf reels exist.
<br>

### v1.2 [07.14.22]
- Neat/render nodes can now be added to selected clips in batch.
- Write nodes can now be used instead of render nodes.
- Added Setup options for setting up Write nodes. Flame Main Menu -> PyFlame -> Neat Freak Setup
<br>

### v1.1 [10.26.21]
- Script now attempts to add shot name to render node.
