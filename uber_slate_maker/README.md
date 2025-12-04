# Uber Slate Maker

**Script Version:** 1.3.1  
**Flame Version:** 2026  
**Written by:** Michael Vaglienty  
**Creation Date:** 12.29.18  
**Update Date:** 04.14.25  

**Script Type:** MediaPanel

## Description

Create and update slates from CSV file data using Type Node templates.
<br><br>
- Slates of multiple ratios can be created from the same CSV file.
- Update existing slates in sequences.
- Preview slate text before creation.
- Automatic slate naming with tokens.
- Add color to slate clips - color can be changed when updating slates as well.
- Does not work with Flare
<br><br>
- Detailed instructions: https://pyflame.com/uber-slate-maker
- Example files: <FlamePythonPath>/uber_slate_maker/example_files/
- CSV Template Files
- Type Node Template Files

## Notes

- Legacy Text Node templates are not supported
- Tokens in Type Node Template and CSV First Row (Column Headers) must be in all CAPS.
- Slates of multiple ratios can be created. CSV needs to have a RATIO column for this to work.
- If the CSV contains multiple slate ratios, only the ratios of the selected slate backgrounds will be created.
- If only one slate background is selected and no RATIO column is present in the CSV,
slates for all entries in the CSV will be created.
- Slate Preview only provides a good preview of slates if each line of the slate is its own layer.
See example Type Node Template files for reference.
- Updating slates:
- Only slates created with this script can be updated using the Update option
- Slate names cannot be changed when updating slates.
- The slate update option only becomes available if the slate is in a sequence.
- Type Node Slate templates must be saved into a folder with the slate ratio in the filename. Example: slate_16x9.type_node
- If anything in the CSV used for tokenized slate naming is changed, the script will not find the correct templates and will not update the slates.
Example:
Slate Name: <ISCI>
If the ISCI values have changed in the CSVfor the updated slates, the script will not be able to match the correct templates to the slates.

## URL

https://github.com/logik-portal/python/uber_slate_maker

## Menus

- Right-click on clip to be used as slate background → UberSlate Maker
- Right-click on selection of slates or sequences containing slates → Uber Slate Maker - Update Slates

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.3.1 [04.14.25]
- Added CURRENT_DATE token to token menu.
- Fixed bug: Selecting a sequence with no slates created by this script would cause the script to crash.
- Fixed bug: Changing text in CSV field was causing errors in the terminal.
- Fixed bug: Rename Column Header was not working properly in CSV Editor.
- Fixed bug: Text in cells/headers beinging renamed now shows in renaming window is CSV Editor.
- Slates made with older versions of the script cannot be updated with this version.
<br>

### v1.3.0 [04.01.25]
- Combined Multi-ratio and Single-ratio modes.
- Slate background clips name must contain have a underscore and ratio. Example: slate_background_16x9
- Type Node templates no longer needs to be saved when creating slates. Slate background clips should have a Type Node Timeline Effect with a Slate Template applied.
- Saved Type Node Templates are still required to UPDATE slates. They must have the ratio in the filename. Example: slate_16x9.type_node
- The ability to make slates of different ratios from the same csv file is done automatically if a ratio column is present in the csv file.
- If a ratio column is present in the csv file, only the ratios of the selected slate backgrounds will be created.
- Example: If the CSV has a ratio column with entries of 16x9, 1x1, and 4x3, and slate_bg_16x9 is selected as the slate background, only 16x9 slates will be created.
<br>

### v1.2.0 [03.23.25]
- Added ability to set slate clip color and change color when updating slates.
- Fixed misc bugs.
<br>

### v1.1.0 [03.16.25]
- Added Preview Slates feature with clipboard support.
- Added simple CSV Editor to quickly change/update CSV files.
- Added Update Slates option.
- Added ability to set slate clip color and change color when updating slates.
- Holding down alt while hovering over a selected field will show the full field value and copy it to the clipboard.
- Fixed misc bugs.
<br>

### v1.0.0 [03.07.25]
- Updated to use Type Node instead of Text Node for Flame 2026 and later.
