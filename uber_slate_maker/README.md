# Uber Slate Maker

**Script Version:** 2.7.0  
**Flame Version:** 2027.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 12.29.18  
**Update Date:** 11.02.26  

**Script Type:** MediaPanel

## Description

Create slates from CSV file data using Type Node templates, and update slates after they have been created.
<br><br>
This script only works with Flame 2027.1 and later.
Use v1.3.1 of this script for earlier versions of Flame with the Type Node.
<br><br>
- Slates of multiple ratios can be created from the same CSV file.
- Preview slate text before creation.
- Automatic slate naming with tokens.
- Add color to slate clips.
- Update token values (date, copyright, etc.) on slates after creation.
- Rename sequences/clips from slate info using a tokenized pattern (e.g. <AD-ID>_<TITLE>).
- Does not work with Flare

## Usage

- Legacy Text Node templates are not supported
- Tokens in Type Node Template and CSV First Row (Column Headers) must be in all CAPS.
- Slates of multiple ratios can be created. CSV needs to have a RATIO column for this to work.
- If the CSV contains multiple slate ratios, only the ratios of the selected slate backgrounds will be created.
- If only one slate background is selected and no RATIO column is present in the CSV, slates for all entries in the CSV will be created.
- Slate Preview only provides a good preview of slates if each line of the slate is its own layer.
<br><br>
Metadata Storage (v2.5.0+, requires Flame 2027):
<br><br>
- Created slates are stamped with custom metadata keys on a Metadata TimelineFX on the slate segment (PyMetadataNode API): one 'SlateToken.<TOKEN>' key per resolved token, plus SlateName, SlateRatio, TokenizedSlateName, SlateDateFormat, SlateSpaces,
SlateVersion and SlateTokenOrder. Values are stored raw (no escaping needed).
- Segment effects travel with the clip when it is edited into a sequence, so the keys are found on the slate segment inside sequences.
- Slates created with v2.0.0-v2.4.x stored the same schema in clip tags; those are still read as a fallback and updates are written back to the tags.
<br><br>
Update Mode Notes:
<br><br>
- Update mode reads the stamped metadata (custom keys, or legacy tags) and does exact-value replacement in the slate's Type Node text, then re-stamps the changed values.
- Slates created with v1.0.0 (no stamped metadata) cannot be bulk-updated (but see
Update Field's any-slate support below).
- CURRENT_DATE gets a 'Set to Today' button that uses the date format stamped at creation.
- If an updated token appears in the tokenized slate name, the clip is renamed to match.
- Slates manually tweaked after creation still update as long as the stamped value text is intact.
- Update Slates also works on sequences with a v2 slate cut in - the slate segment is found by its tags and its Type Node is updated in place. The slate segment is renamed to match updated values; the sequence's own name is left alone (re-run Rename from
Slate to refresh it). If a sequence contains multiple slate segments, only the first is updated.
- The Slate Maker: Update Field submenu offers one menu item per field (Update
Date, Update Agency, etc.) that opens the same update flow restricted to that single token - a quick way to change one value across all selected slates. The field list is learned automatically: whenever slates are created, the CSV's tokens are added to the menu (RATIO excluded, CURRENT_DATE listed as DATE).
The list can also be curated by hand via the Edit Update Fields menu item - one field per line, in menu order. It is stored under 'update_field_tokens' in config/config.json; python hooks are rescanned on change, so new menu items appear without a Flame restart.
- Update Field works on ANY slate, not just ones made by this script. For items without Slate Maker tags, the slate is taken to be the FIRST SEGMENT of the sequence (or the clip itself), and the field's current value is read from its label line in the Type Node text - a line starting with the field name, e.g.
'Agency: Mother' or 'AGENCY  Mother' (case-insensitive). Updating replaces
everything after the label on that line. Bare label lines with no value on the same line (two-column slate layouts) are not matched, so label-only text layers are never damaged; such slates are reported and skipped. Untagged slates get a pure text edit - no rename, no tags added.
<br><br>
Rename Mode Notes:
<br><br>
- Slate clip tags propagate onto the timeline segment when a slate is edited into a sequence, so a sequence containing a v2 slate carries that slate's SlateToken tags.
- Rename from Slate reads those tags and renames the selected sequences (or bare slate clips) using a tokenized pattern, e.g. <AD-ID>_<TITLE>.
- Sequences without a v2 slate segment are reported and skipped.

## URL

https://logik-portal.com/scripts/uber_slate_maker

## Menus

- Uber Slate Maker... → Create Slates             (select slate background clip(s))
- Uber Slate Maker... → Rename from Slate         (select sequences containing a slate, or slate clips)
- Uber Slate Maker: Update... → Update Slates     (bulk editor; v2 slate clips or sequences containing one)
- Uber Slate Maker: Update... → Update <Field>    (one item per learned/configured field; works on any slate)
- Uber Slate Maker: Update... → Edit Update Fields (curate the Update <Field> menu list)

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.7.0 [11.02.26]
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Fixed spaces around CSV column headers or RATIO values causing errors, skipped rows or tokens left in the slate text. Also fixed in the Slate Name token menu.
- Fixed blank or short CSV rows causing an error.
- Fixed CSV files saved as CSV UTF-8 (Excel) not reading the first column header.
- Fixed Create Slates making extra or wrong slates after a Slate Preview or a failed run.
- If Create Slates, Update Slates or Rename from Slate fails, an error message is now shown. Create Slates shows its window again so the CSV can be fixed. Before, the window was left hidden.
- An empty -= Slates =- library is no longer created when there are no slates to create.
- Fixed Enter key error in the CSV Editor.
- Escape now closes the script windows.
<br>

### v2.6.1 [08.31.26]
- Reverted to older version of pyflame library to resolve compability issues that could cause script not to work.
<br>

### v2.6.0 [08.06.26]
- Facility-agnostic update fields: the Update <Field> menu now learns its field list from the slates you create - each creation run merges the CSV's tokens into 'update_field_tokens' (RATIO excluded, CURRENT_DATE folded into DATE) and python hooks are rescanned so the menu updates without a Flame restart. New Edit Update Fields menu item to curate the list in a window (one field per line, in menu order). Shipped defaults are now neutral: the field list starts empty (populated by the first creation) and the rename pattern default is blank. 'Set to Today' now appears on any token containing the word DATE (e.g. AIR DATE), not just DATE/CURRENT_DATE.
<br>

### v2.5.4 [08.05.26]
- Confirmation dialogs are now conditional: Rename from Slate and the Update tools apply immediately when everything is clean, and only ask when something needs attention (update: value found 0 or multiple times in the slate text, empty original; rename: items skipped for missing tokens, resulting-name collisions). Selections without slate metadata still warn during gathering.
<br>

### v2.5.3 [08.05.26]
- Fix: Update Date now treats DATE and CURRENT_DATE as the same field. Slates created with the <CURRENT_DATE> token store CURRENT_DATE, so Update Date (single_token DATE) found no matching token and errored; it now edits whichever date alias the selection actually carries.
<br>

### v2.5.2 [08.05.26]
- Fix: values read back via get_metadata() render wrapped in single quotes (Flame-attribute style, like clip.name). They are now unquoted on read - Rename from Slate no longer puts quotes in names, and Update tools' occurrence matching against the Type Node text works again (the quoted old value never matched, so metadata updated but the slate text did not).
<br>

### v2.5.1 [08.05.26]
- Fix: the Metadata timeline effect's create_effect type string is 'Source Metadata' (a source-level effect like 'Source Colour Mgmt'), not 'Metadata'. Creation crashed with "Could not create an effect of given effect type".
<br>

### v2.5.0 [08.05.26]
- Slate metadata is now stored as custom keys on a Metadata TimelineFX on the slate segment (PyMetadataNode API, Flame 2027+) instead of clip tags. Legacy tag-stamped slates (v2.0.0-v2.4.x) are still read and updated via their tags.
<br>

### v2.4.2 [08.05.26]
- All update tools moved to their own 'Slate Maker: Update...' folder (Update Slates + the per-field items); 'Slate Maker...' keeps Create Slates and Rename from Slate. Flame's menu API has no nested subfolders, so a sibling folder is used.
<br>

### v2.4.1 [08.05.26]
- Context menu reorganized: all tools now live under one 'Slate Maker...' folder (Create Slates, Update Slates, Rename from Slate, and the per-field Update items), using the group-name pattern from alternating_colors.py.
<br>

### v2.4.0 [08.05.26]
- Update Field now works on any slate, not just v2-created ones. Untagged items use the first segment as the slate and match the field by its label line in the Type Node text ('Agency: value'), replacing the text after the label. Tagged v2 slates still use exact-value replacement from their stamped metadata.
<br>

### v2.3.0 [08.05.26]
- Added Update Field submenu: one menu item per configured field (Date, Agency, Client, ID, Title, Duration, Audio Channels, Audio Details, Copyright) that updates that single token across all selected slates/sequences. Field list is configurable via 'update_field_tokens' in config.json. DATE now also gets the 'Set to Today' button in update windows.
<br>

### v2.2.0 [08.02.26]
- Update Slates now also works on sequences containing a v2 slate: the slate segment is located by its tags and updated in place.
<br>

### v2.1.0 [08.02.26]
- Added Rename from Slate mode: rename sequences containing a v2 slate (or slate clips themselves) from their slate token values using a tokenized name pattern.
<br>

### v2.0.0 [08.02.26]
- Added Update Slates mode: token values are stamped to clip tags at creation and can be bulk-edited later via Slate Maker: Update Slates.
<br>

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
- If a ratio column is present in the csv file, only the ratios of the selected slate backgrounds will be created. Example: If the CSV has a ratio column with entries of 16x9, 1x1, and 4x3, and slate_bg_16x9 is selected as the slate background, only 16x9 slates will be created.
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
