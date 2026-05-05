# Clip To Batch Group

**Script Version:** 3.0.0  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.16.19  
**Update Date:** 05.05.26  

**Script Type:** MediaPanel / Media Hub

## Description

Create batch group(s) from selected clips in the media panel or media hub.

## Usage

Script Setup:
- Set batch group to use either Render or Write File node.
(Default:  Render)
- Set batch group suffix.
(Default: _comp)
- Set tokenized save path. Batch setup will be saved when the batch group is created.
Leaving Tokenized Save Path button off will not save the batch group and the default Flame path will be used.
(Default: off)
<br><br>
When creating a batch group from all clips, clips are loaded in the order
they are selected. Select clips individually to control the order, or use
shift-select to load them top-down. The first clip in the selection
determines the batch group settings.

## URL

https://logik-portal.com/scripts/#clip_to_batch_group

## Menus

### Setup
- Flame Main Menu → Logik Portal → Logik Portal Script Setup → Clip to Batch Group Setup
### To import clips into batch group with shot name extracted from clip name
- Right-click on clip in MediaHub → Import... → Create New Batch Group - Shot Name
- Right-click on clip in MediaHub → Import... → Create New Batch Group - Shot Name - All Clips One Batch
### To import clips into batch group with clip name
- Right-click on clip in MediaHub → Import... → Create New Batch Group - Clip Name
- Right-click on clip in MediaHub → Import... → Create New Batch Group - Clip Name - All Clips One Batch
### To create batch group from clips in media panel with shot name extracted from clip name
- Right-click on clip in Media Panel → Create New Batch Group... → Shot Name
- Right-click on clip in Media Panel → Create New Batch Group... → Shot Name - All Clips One Batch
### To create batch group from clips in media panel with clip name
- Right-click on clip in Media Panel → Create New Batch Group... → Clip Name
- Right-click on clip in Media Panel → Create New Batch Group... → Clip Name - All Clips One Batch

## Installation

Copy script into /opt/Autodesk/shared/python/clip_to_batch_group

## Updates

### v3.0.0 [05.05.26]
- Updated to work in Flame 2027.
- Added setup window to configure script options:
- Set batch group to use either Render or Write File node.
- Set batch group suffix.
- Set tokenized save path. Batch setup will be saved when the batch group is created.
- Leaving Tokenized Save Path button off will not save the batch group and the default Flame path will be used.
- Updated to PyFlameLib v5.3.1.
<br>

### v2.7.0 [04.09.25]
- Updated to PyFlameLib v4.3.0.
<br>

### v2.6.0 [01.15.25]
- Updated to PyFlameLib v4.1.0.
- Script now only works with Flame 2025+.
<br>

### v2.5.0 [08.22.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.4.0 [04.27.24]
- Render node now sets in and out marks based on clip in and out marks.
<br>

### v2.3.0 [01.21.24]
- Sequences can now be imported into batch groups. This caused an error before.
- Updates to PySide.
<br>

### v2.2.0 [09.12.23]
- When creating a batch group from a clip in the media panel, the script will check for a shot name assigned to the clip.
- If a shot name is assigned, that will be used for the batch group name. If no shot name is assigned, the script will
- attempt to extract the shot name from the clip name.
- Updated with PyFlameLib v2.
<br>

### v2.1 [05.19.21]
- Updated to be compatible with Flame 2022/Python 3.7.
<br>

### v1.8 [05.15.21]
- Properly names batch group with shot name when clip name starts with number - 123_030_bty_plate -> 123_030_comp
<br>

### v1.7 [02.19.21]
- Option added to switch to batch tab or not when batch groups are create can be toggled
- by editing self.go_to_batch value in __init__. Must be True or False.
- Mediahub menu options added to import all selected clips into one batch group. Clip selected first is
- plate used for shot length and timecode.
<br>

### v1.6 [11.18.20]
- Added Mux nodes with context 1 and 2 preset.
<br>

### v1.5 [09.10.20]
- Batch groups can now be imported and named after either the clip name or shot name.
- Script will now switch to the Batch tab when creating a batch group from the media panel - caused an error before.
<br>

### v1.4 [04.20.20]
- Added ability to create batchgroup from clip in Media Panel.
- Right-click on clip in Media Panel -> Clips... -> Create New Batchgroup
<br>

### v1.3 [11.01.19]
- Changed menu name to Import...
- Render node takes frame rate from imported clip
<br>

### v1.1 [08.13.19]
- Code cleanup.
