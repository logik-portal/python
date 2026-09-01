# -*- coding: utf-8 -*-
# Slate Maker
# Copyright (c) 2026 Michael Vaglienty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: Uber Slate Maker
Script Version: v2.6.1
Flame Version: 2027
Written by: Michael Vaglienty
Extended by: Bryan Bayley (v2.0.0 and later)
Creation Date: 12.29.18
Update Date: 08.31.26

Derived from: Slate Maker v1.0.0 / Uber Slate Maker v1.3.1

Modifications: v1.0.0 is Michael Vaglienty's original. Everything from v2.0.0
onward (update, rename and per-field tools, metadata stamping, learned update
fields) was added in-house by Bryan Bayley with the original author's
permission - see Version History below for the per-version detail.

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create slates from CSV file data using Type Node templates, and update
    slates after they have been created.

    - Slates of multiple ratios can be created from the same CSV file.
    - Preview slate text before creation.
    - Automatic slate naming with tokens.
    - Add color to slate clips.
    - Update token values (date, copyright, etc.) on slates after creation.
    - Rename sequences/clips from slate info using a tokenized pattern (e.g. <AD-ID>_<TITLE>).
    - Does not work with Flare

URL:
    https://logik-portal.com/scripts/#uber_slate_maker

Usage:

    - Legacy Text Node templates are not supported
    - Tokens in Type Node Template and CSV First Row (Column Headers) must be in all CAPS.
    - Slates of multiple ratios can be created. CSV needs to have a RATIO column for this to work.
    - If the CSV contains multiple slate ratios, only the ratios of the selected slate backgrounds will be created.
    - If only one slate background is selected and no RATIO column is present in the CSV,
      slates for all entries in the CSV will be created.
    - Slate Preview only provides a good preview of slates if each line of the slate is its own layer.

    Metadata Storage (v2.5.0+, requires Flame 2027):

        - Created slates are stamped with custom metadata keys on a Metadata TimelineFX on the
        slate segment (PyMetadataNode API): one 'SlateToken.<TOKEN>' key per resolved token,
        plus SlateName, SlateRatio, TokenizedSlateName, SlateDateFormat, SlateSpaces,
        SlateVersion and SlateTokenOrder. Values are stored raw (no escaping needed).
        - Segment effects travel with the clip when it is edited into a sequence, so the keys
        are found on the slate segment inside sequences.
        - Slates created with v2.0.0-v2.4.x stored the same schema in clip tags; those are
        still read as a fallback and updates are written back to the tags.

    Update Mode Notes:

        - Update mode reads the stamped metadata (custom keys, or legacy tags) and does
        exact-value replacement in the slate's Type Node text, then re-stamps the changed
        values.
        - Slates created with v1.0.0 (no stamped metadata) cannot be bulk-updated (but see
        Update Field's any-slate support below).
        - CURRENT_DATE gets a 'Set to Today' button that uses the date format stamped at creation.
        - If an updated token appears in the tokenized slate name, the clip is renamed to match.
        - Slates manually tweaked after creation still update as long as the stamped value text
        is intact.
        - Update Slates also works on sequences with a v2 slate cut in - the slate segment is
        found by its tags and its Type Node is updated in place. The slate segment is renamed
        to match updated values; the sequence's own name is left alone (re-run Rename from
        Slate to refresh it). If a sequence contains multiple slate segments, only the first
        is updated.
        - The Slate Maker: Update Field submenu offers one menu item per field (Update
        Date, Update Agency, etc.) that opens the same update flow restricted to that
        single token - a quick way to change one value across all selected slates. The
        field list is learned automatically: whenever slates are created, the CSV's
        tokens are added to the menu (RATIO excluded, CURRENT_DATE listed as DATE).
        The list can also be curated by hand via the Edit Update Fields menu item -
        one field per line, in menu order. It is stored under 'update_field_tokens'
        in config/config.json; python hooks are rescanned on change, so new menu
        items appear without a Flame restart.
        - Update Field works on ANY slate, not just ones made by this script. For items
        without Slate Maker tags, the slate is taken to be the FIRST SEGMENT of the
        sequence (or the clip itself), and the field's current value is read from its
        label line in the Type Node text - a line starting with the field name, e.g.
        'Agency: Mother' or 'AGENCY  Mother' (case-insensitive). Updating replaces
        everything after the label on that line. Bare label lines with no value on the
        same line (two-column slate layouts) are not matched, so label-only text layers
        are never damaged; such slates are reported and skipped. Untagged slates get a
        pure text edit - no rename, no tags added.

    Rename Mode Notes:

        - Slate clip tags propagate onto the timeline segment when a slate is edited into a
        sequence, so a sequence containing a v2 slate carries that slate's SlateToken tags.
        - Rename from Slate reads those tags and renames the selected sequences (or bare slate
        clips) using a tokenized pattern, e.g. <AD-ID>_<TITLE>.
        - Sequences without a v2 slate segment are reported and skipped.

Updates:

    v2.6.1 08.31.26
        - Reverted to older version of pyflame library for resolve
          compability issues that could cause script not to work.

    v2.6.0 08.06.26
        - Facility-agnostic update fields: the Update <Field> menu
          now learns its field list from the slates you create -
          each creation run merges the CSV's tokens into
          'update_field_tokens' (RATIO excluded, CURRENT_DATE
          folded into DATE) and python hooks are rescanned so the
          menu updates without a Flame restart. New Edit Update
          Fields menu item to curate the list in a window (one
          field per line, in menu order). Shipped defaults are now
          neutral: the field list starts empty (populated by the
          first creation) and the rename pattern default is blank.
          'Set to Today' now appears on any token containing the
          word DATE (e.g. AIR DATE), not just DATE/CURRENT_DATE.

    v2.5.4 08.05.26
        - Confirmation dialogs are now conditional: Rename from
          Slate and the Update tools apply immediately when
          everything is clean, and only ask when something needs
          attention (update: value found 0 or multiple times in the
          slate text, empty original; rename: items skipped for
          missing tokens, resulting-name collisions). Selections
          without slate metadata still warn during gathering.

    v2.5.3 08.05.26
        - Fix: Update Date now treats DATE and CURRENT_DATE as the
          same field. Slates created with the <CURRENT_DATE> token
          store CURRENT_DATE, so Update Date (single_token DATE)
          found no matching token and errored; it now edits
          whichever date alias the selection actually carries.

    v2.5.2 08.05.26
        - Fix: values read back via get_metadata() render wrapped
          in single quotes (Flame-attribute style, like clip.name).
          They are now unquoted on read - Rename from Slate no
          longer puts quotes in names, and Update tools' occurrence
          matching against the Type Node text works again (the
          quoted old value never matched, so metadata updated but
          the slate text did not).

    v2.5.1 08.05.26
        - Fix: the Metadata timeline effect's create_effect type
          string is 'Source Metadata' (a source-level effect like
          'Source Colour Mgmt'), not 'Metadata'. Creation crashed
          with "Could not create an effect of given effect type".

    v2.5.0 08.05.26
        - Slate metadata is now stored as custom keys on a Metadata
          TimelineFX on the slate segment (PyMetadataNode API, Flame
          2027+) instead of clip tags. Legacy tag-stamped slates
          (v2.0.0-v2.4.x) are still read and updated via their tags.

    v2.4.2 08.05.26
        - All update tools moved to their own 'Slate Maker: Update...'
          folder (Update Slates + the per-field items); 'Slate Maker...'
          keeps Create Slates and Rename from Slate. Flame's menu API
          has no nested subfolders, so a sibling folder is used.

    v2.4.1 08.05.26
        - Context menu reorganized: all tools now live under one
          'Slate Maker...' folder (Create Slates, Update Slates,
          Rename from Slate, and the per-field Update items), using
          the group-name pattern from alternating_colors.py.

    v2.4.0 08.05.26
        - Update Field now works on any slate, not just v2-created ones.
          Untagged items use the first segment as the slate and match the
          field by its label line in the Type Node text ('Agency: value'),
          replacing the text after the label. Tagged v2 slates still use
          exact-value replacement from their stamped metadata.

    v2.3.0 08.05.26
        - Added Update Field submenu: one menu item per configured field
          (Date, Agency, Client, ID, Title, Duration, Audio Channels,
          Audio Details, Copyright) that updates that single token across
          all selected slates/sequences. Field list is configurable via
          'update_field_tokens' in config.json. DATE now also gets the
          'Set to Today' button in update windows.

    v2.2.0 08.02.26
        - Update Slates now also works on sequences containing a v2 slate:
          the slate segment is located by its tags and updated in place.

    v2.1.0 08.02.26
        - Added Rename from Slate mode: rename sequences containing a v2 slate
          (or slate clips themselves) from their slate token values using a
          tokenized name pattern.

    v2.0.0 08.02.26
        - Added Update Slates mode: token values are stamped to clip tags at
          creation and can be bulk-edited later via Slate Maker: Update Slates.

    v1.0.0 04.29.25
        - Initial version, derived from Uber Slate Maker with update
          functionality removed.

Menus:

    Tools live in two right-click folders in the Media Panel (Flame's menu API
    does not support nested subfolders, so the update tools get a sibling folder):

    Uber Slate Maker... -> Create Slates             (select slate background clip(s))
    Uber Slate Maker... -> Rename from Slate         (select sequences containing a slate, or slate clips)
    Uber Slate Maker: Update... -> Update Slates     (bulk editor; v2 slate clips or sequences containing one)
    Uber Slate Maker: Update... -> Update <Field>    (one item per learned/configured field; works on any slate)
    Uber Slate Maker: Update... -> Edit Update Fields (curate the Update <Field> menu list)

To install:

    Copy script folder into /opt/Autodesk/shared/python
"""

#-------------------------------------
# [Import Modules]
#-------------------------------------

import csv
import datetime
import json
import os
import re
from functools import partial
import xml.etree.ElementTree as ET

import flame
from lib.pyflame_lib_uber_slate_maker import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Uber Slate Maker'
SCRIPT_VERSION = 'v2.6.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# Shared config schema - all modes load the same config/config.json.
# PyFlameConfig overlays saved values onto these defaults, so adding a key here
# is safe with existing config files.
DEFAULT_CONFIG = {
    'csv_file_path': '',
    'date_format': 'mm/dd/yy',
    'slate_clip_name': '',
    'spaces_to_underscores': True,
    'create_ratio_folders': True,
    'clip_color': 'No Color',
    'rename_pattern': '',
    # Update <Field> menu list. Starts empty and is learned from the tokens of
    # each creation run (see learn_update_fields); curate via Edit Update Fields.
    'update_field_tokens': [],
    }

# Metadata schema (v2.5.0+, Flame 2027+): slate metadata is stored as custom
# keys on a Metadata TimelineFX on the slate segment (PyMetadataNode API).
# Segment effects travel with the clip when it is edited into a sequence, so
# update/rename modes find the keys on the slate segment inside sequences.
METADATA_TOKEN_PREFIX = 'SlateToken.'
METADATA_TOKEN_ORDER_KEY = 'SlateTokenOrder'

# Legacy tag schema (v2.0.0-v2.4.x): stamped onto slate clips as clip tags.
# Still read (and written back) so slates created before v2.5.0 stay updatable.
TOKEN_TAG_PREFIX = 'SlateToken:'
DATE_FORMAT_TAG_PREFIX = 'SlateDateFormat:'
SPACES_TAG_PREFIX = 'SlateSpaces:'
VERSION_TAG = 'SlateVersion:2'

# Sentinel shown in update-mode entry fields when selected slates disagree on a value.
VARIES = '<varies across slates>'

# Aliases of the same date field: slates created with the <CURRENT_DATE> token
# store CURRENT_DATE, CSV-driven slates store DATE. Single-token update mode
# edits whichever one the selection carries. (The 'Set to Today' button is
# broader - any token passing is_date_token gets it.)
DATE_TOKENS = ('CURRENT_DATE', 'DATE')

#-------------------------------------
# [Shared Helpers]
#-------------------------------------

def escape_tag_value(value: str) -> str:
    """Escape a token value for storage in a clip tag. Reversible via unescape_tag_value."""

    return value.replace('%', '%25').replace('\n', '%0A').replace('\r', '%0D')

def unescape_tag_value(value: str) -> str:

    return value.replace('%0D', '\r').replace('%0A', '\n').replace('%25', '%')

def field_display_name(token: str) -> str:
    """
    Menu/window label for an ALL CAPS token: title-case long words, keep short
    words and short hyphen parts as-is so acronyms survive.
    'AUDIO CHANNELS' -> 'Audio Channels', 'ID' -> 'ID', 'AD-ID' -> 'AD-ID'.
    """

    return ' '.join(
        '-'.join(part if len(part) <= 3 else part.title() for part in word.split('-'))
        for word in token.split()
        )

def is_date_token(token: str) -> bool:
    """
    True if the token names a date field ('DATE', 'CURRENT_DATE', 'AIR DATE',
    'SHIP-DATE', ...). These get a 'Set to Today' button in update windows.
    """

    return 'DATE' in re.split(r'[\s\-_]+', token.upper())

def normalize_field_tokens(tokens) -> list:
    """
    Normalize a token list for the Update <Field> menu: uppercase and strip
    each entry, dedupe preserving order, fold CURRENT_DATE into its DATE alias,
    and drop RATIO (structural, never editable) and empty lines.
    """

    normalized = []
    for token in tokens:
        token = str(token).strip().upper()
        if token == 'CURRENT_DATE':
            token = 'DATE'
        if token and token != 'RATIO' and token not in normalized:
            normalized.append(token)
    return normalized

def refresh_python_hooks() -> None:
    """Rescan python hooks so Update <Field> menu changes appear without a Flame restart."""

    try:
        flame.execute_shortcut('Rescan Python Hooks')
    except Exception:
        pyflame.print(
            'Could not rescan python hooks - Update Field menu changes appear after a Flame restart.',
            text_color=TextColor.YELLOW,
            )

def learn_update_fields(settings, run_tokens: list) -> None:
    """
    Merge a creation run's tokens into update_field_tokens so the Update
    <Field> menu mirrors the fields actually used in this facility's slates.
    New tokens are appended in run order; nothing is removed (curate via the
    Edit Update Fields window).
    """

    current = normalize_field_tokens(settings.update_field_tokens)
    new_tokens = [t for t in normalize_field_tokens(run_tokens) if t not in current]
    if not new_tokens:
        return

    settings.save_config(config_values={'update_field_tokens': current + new_tokens})
    pyflame.print(
        f'Update Field menu: added {", ".join(new_tokens)}',
        text_color=TextColor.GREEN,
        )
    refresh_python_hooks()

def resolve_date(date_format: str) -> str:
    """Return today's date formatted per the script's date format strings (e.g. 'mm/dd/yy')."""

    now = datetime.datetime.now()
    date_format = date_format.replace('yyyy', '20%y')
    date_format = date_format.replace('yy', '%y')
    date_format = date_format.replace('mm', '%m')
    date_format = date_format.replace('dd', '%d')
    return now.strftime(date_format)

def convert_ascii_to_text(ascii_code: str) -> str:
    """Type Node XML stores text as space-separated ASCII code points - decode to a string."""

    return ''.join(chr(int(code)) for code in ascii_code.split())

def convert_text_to_ascii(text_to_convert: str) -> str:

    text_to_convert = text_to_convert.replace('“', '"').replace('”', '"')

    ascii_list = []

    for char in text_to_convert:
        ascii_num = ord(char)
        if ascii_num != 194:
            ascii_list.append(ascii_num)

    return ' '.join(str(a) for a in ascii_list)

def decode_type_node_layers(setup_path: str) -> list:
    """Decoded text of every CharacterSet layer in a .type_node file, in file order."""

    layers = []
    root = ET.parse(setup_path).getroot()
    for char_set in root.findall('.//CharacterSet'):
        type_elem = char_set.find('Text')
        if type_elem is not None and type_elem.text:
            layers.append(convert_ascii_to_text(type_elem.text))
    return layers

def label_line_pattern(token: str):
    """
    Pattern matching a slate text line that carries a labeled value, e.g.
    'Agency: Mother' or 'AGENCY  Mother' for token 'AGENCY'. Case-insensitive.
    Group 1 is the label part (kept verbatim on replacement), group 2 the value.
    A colon allows an empty value; without a colon the line must have a value,
    so bare label lines (two-column slate layouts) are never touched.
    """

    escaped = re.escape(token)
    return re.compile(rf'^(\s*{escaped}\s*:\s*|\s*{escaped}\s+(?=\S))(.*)$', re.IGNORECASE)

def find_label_value(decoded_layers: list, token: str):
    """
    Search decoded slate text for the token's label line. Returns
    (value, occurrences) - the value from the first matching line (stripped)
    and the number of matching lines. (None, 0) if the label is not found.
    """

    pattern = label_line_pattern(token)
    value = None
    occurrences = 0

    for layer in decoded_layers:
        for line in layer.split('\n'):
            match = pattern.match(line)
            if match:
                occurrences += 1
                if value is None:
                    value = match.group(2).strip()

    return value, occurrences

def replace_label_value(decoded: str, token: str, new_value: str) -> str:
    """Replace the value part of every label line for the token, keeping the label as-is."""

    pattern = label_line_pattern(token)
    lines = []
    for line in decoded.split('\n'):
        match = pattern.match(line)
        lines.append(f'{match.group(1)}{new_value}' if match else line)
    return '\n'.join(lines)

def find_type_fx(clip):
    """Return the first Type effect found on a clip, or None."""

    for version in clip.versions:
        for track in version.tracks:
            for seg in track.segments:
                for fx in seg.effects:
                    if fx.type == 'Type':
                        return fx
    return None

def read_slate_tags(tag_list) -> dict:
    """
    Parse Slate Maker metadata out of a list of tag strings.

    Returns a dict with 'tokens', 'token_order', 'date_format',
    'spaces_to_underscores', and 'tokenized_name' keys, or None if no
    SlateToken tags are present.
    """

    tokens = {}
    token_order = []
    date_format = None
    spaces_to_underscores = True
    tokenized_name = ''

    for tag in tag_list:
        if tag.startswith(TOKEN_TAG_PREFIX):
            token, _, value = tag[len(TOKEN_TAG_PREFIX):].partition('=')
            token = token.strip()
            tokens[token] = unescape_tag_value(value)
            token_order.append(token)
        elif tag.startswith(DATE_FORMAT_TAG_PREFIX):
            date_format = tag[len(DATE_FORMAT_TAG_PREFIX):].strip()
        elif tag.startswith(SPACES_TAG_PREFIX):
            spaces_to_underscores = tag[len(SPACES_TAG_PREFIX):].strip() == '1'
        elif tag.startswith('TokenizedSlateName:'):
            tokenized_name = tag.split(':', 1)[1].strip()

    if not tokens:
        return None

    return {
        'tokens': tokens,
        'token_order': token_order,
        'date_format': date_format,
        'spaces_to_underscores': spaces_to_underscores,
        'tokenized_name': tokenized_name,
        }

# The Metadata timeline effect's type string. It is a source-level effect like
# 'Source Colour Mgmt' - plain 'Metadata' is NOT a valid create_effect type
# (shows in the UI as "Metadata", but the effect name table calls it
# 'Source Metadata'; the python wrapper class is PyMetadataTimelineFX).
METADATA_FX_TYPE = 'Source Metadata'

def find_metadata_fx(segment):
    """Return the first Metadata effect on a segment, or None."""

    for fx in segment.effects:
        if fx.type in (METADATA_FX_TYPE, 'Metadata'):
            return fx
    return None

def stamp_slate_metadata(segment, keys: dict) -> None:
    """
    Write slate metadata as custom keys on the segment's Metadata effect
    (PyMetadataNode API, Flame 2027+). Creates the effect if the segment does
    not have one yet. All values are stored as strings.
    """

    meta_fx = find_metadata_fx(segment)
    if meta_fx is None:
        meta_fx = segment.create_effect(METADATA_FX_TYPE)

    for key, value in keys.items():
        meta_fx.set_metadata_value(key=key, value=str(value))

def unquote_metadata_value(value) -> str:
    """
    get_metadata() values render Flame-attribute style - wrapped in single
    quotes (like clip.name). Strip one matching pair; anything else passes
    through unchanged.
    """

    text = str(value)
    if len(text) >= 2 and text[0] == "'" and text[-1] == "'":
        return text[1:-1]
    return text

def read_slate_metadata(meta_fx) -> dict:
    """
    Parse Slate Maker custom keys out of a Metadata effect.

    Returns the same dict shape as read_slate_tags plus a 'meta_fx' key
    referencing the effect (used to write values back), or None if no
    SlateToken keys are present.
    """

    try:
        data = meta_fx.get_metadata()
    except Exception:
        return None

    if not isinstance(data, dict):
        return None

    tokens = {}
    for key, value in data.items():
        if key.startswith(METADATA_TOKEN_PREFIX):
            tokens[key[len(METADATA_TOKEN_PREFIX):]] = unquote_metadata_value(value)

    if not tokens:
        return None

    stamped_order = [t for t in unquote_metadata_value(data.get(METADATA_TOKEN_ORDER_KEY, '')).split('|') if t]
    token_order = [t for t in stamped_order if t in tokens]
    token_order += [t for t in tokens if t not in token_order]

    date_format = data.get('SlateDateFormat')

    return {
        'tokens': tokens,
        'token_order': token_order,
        'date_format': unquote_metadata_value(date_format).strip() if date_format is not None else None,
        'spaces_to_underscores': unquote_metadata_value(data.get('SlateSpaces', '1')).strip() == '1',
        'tokenized_name': unquote_metadata_value(data.get('TokenizedSlateName', '')).strip(),
        'meta_fx': meta_fx,
        }

def read_segment_slate_data(segment) -> dict:
    """
    Slate metadata from a segment - Metadata effect custom keys first
    (v2.5.0+ storage), then legacy tags (propagated onto the segment when a
    tag-stamped slate clip was cut into a sequence).
    """

    meta_fx = find_metadata_fx(segment)
    if meta_fx:
        info = read_slate_metadata(meta_fx)
        if info:
            return info

    return read_slate_tags(segment.tags.get_value())

def find_slate_tags(item) -> dict:
    """
    Find Slate Maker metadata on a clip or sequence.

    Checks the item's own tags first (a legacy tag-stamped slate clip), then
    walks its timeline segments reading Metadata effect custom keys or
    propagated tags (the slate segment inside a sequence, or the segment of a
    v2.5.0+ slate clip). Returns the same dict as read_slate_tags, or None.
    """

    info = read_slate_tags(item.tags.get_value())
    if info:
        return info

    for version in item.versions:
        for track in version.tracks:
            for segment in track.segments:
                info = read_segment_slate_data(segment)
                if info:
                    return info

    return None

#-------------------------------------
# [Main Script]
#-------------------------------------

class SlateMaker():

    def __init__(self, selection: Any) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        self.install_verified = pyflame.verify_script_install()
        if not self.install_verified:
            return

        self.selection = selection
        self.settings = self.load_config()
        self.temp_path = pyflame.create_temp_folder()
        self.templates_path = os.path.join(self.temp_path, 'slate_templates')
        self.current_date = ''
        self.setup_token_map = {}  # generated .type_node filename -> token value dict, used to stamp tags

        if flame.get_current_tab() == 'MediaHub':
            flame.go_to('Timeline')

    def load_config(self) -> PyFlameConfig:

        return PyFlameConfig(config_values=dict(DEFAULT_CONFIG))

    #-------------------------------------

    def slate_maker(self) -> None:

        if not self.install_verified:
            return

        def validate_selection() -> bool:

            def type_node_check() -> bool:

                for clip in self.selection:
                    clip_has_type_node = False

                    for version in clip.versions:
                        for track in version.tracks:
                            for seg in track.segments:
                                for fx in seg.effects:
                                    if fx.type == 'Type':
                                        clip_has_type_node = True
                                        break
                                if clip_has_type_node:
                                    break
                            if clip_has_type_node:
                                break
                        if clip_has_type_node:
                            break

                    if not clip_has_type_node:
                        PyFlameMessageWindow(
                            message='All selected slate backgrounds must have a Type Node with a Slate Template applied.',
                            type=MessageType.ERROR
                            )
                        return False

                return True

            def protect_from_editing_check() -> bool:

                pyflame.print('Checking Protect From Editing setting...', new_line=False)

                new_clip = None

                try:
                    for clip in self.selection:
                        new_clip = flame.duplicate(clip)
                        new_clip.name = 'protect_from_editing_test_clip'
                        seg = new_clip.versions[0].tracks[0].segments[0]
                        seg.create_effect('Text')
                        break
                    flame.delete(new_clip)
                    pyflame.print('Protect From Editing is turned off, continuing...', text_color=TextColor.GREEN)
                    return False
                except:
                    if new_clip:
                        flame.delete(new_clip)
                    PyFlameMessageWindow(
                        message='Turn off Protect from Editing: Flame Preferences -> General.',
                        type=MessageType.ERROR
                        )
                    return True

            if not type_node_check():
                return False

            if protect_from_editing_check():
                return False

            return True

        def get_slate_ratios() -> str:

            print('Getting Selected Clip Ratios...')

            slate_ratios = []

            for clip in self.selection:
                ratio = self.get_slate_ratios_from_clip_name(clip)
                if not ratio:
                    return None

                clip.tags = [f'SlateRatio: {ratio}']

                if ratio not in slate_ratios:
                    slate_ratios.append(ratio)

            self.slate_ratios = slate_ratios
            slate_ratios_str = ' | '.join([str(r).lower() for r in slate_ratios])

            pyflame.print(f'Slate Ratios: {slate_ratios_str}', text_color=TextColor.GREEN)

            return slate_ratios_str

        def get_slate_templates() -> list:

            def create_temp_slate_templates_folder() -> None:

                if os.path.exists(self.templates_path):
                    shutil.rmtree(self.templates_path)

                os.makedirs(self.templates_path)

                pyflame.print(f'Created temporary folder for slate templates: {self.templates_path}', new_line=False, text_color=TextColor.GREEN)

            def get_slate_templates_from_clips() -> list:

                template_list = []

                for clip in self.selection:
                    ratio = self.get_slate_ratios_from_clip_name(clip)
                    print('Ratio:', ratio)
                    for version in clip.versions:
                        for track in version.tracks:
                            for segment in track.segments:
                                for fx in segment.effects:
                                    if fx.type == 'Type':
                                        save_path = os.path.join(self.templates_path, f'{str(clip.name)[1:-1]}.type_node')
                                        print('Template Save Path: ', save_path)
                                        fx.save_setup(save_path)
                                        template_list.append(save_path)

                pyflame.print('Saved Type Node Template setups from selected clips', text_color=TextColor.GREEN)

                return template_list

            pyflame.print('Saving Slate Type Node Template Setups...', text_color=TextColor.GREEN, new_line=False)

            create_temp_slate_templates_folder()
            template_list = get_slate_templates_from_clips()

            print('Slate Templates:')
            for template in template_list:
                print(template)
            print('\n', end='')

            return template_list

        def csv_browse() -> None:

            csv_file_path = pyflame.file_browser(
                path=self.csv_path_entry.text(),
                title='Select CSV File',
                extension=['csv'],
                window_to_hide=[self.window],
                )

            if csv_file_path:
                self.settings.save_config(config_values={'csv_file_path': csv_file_path})
                self.csv_path_entry.setText(csv_file_path)
                self.get_clip_name_tokens(
                    csv_file_path=csv_file_path,
                    clip_name_push_button=self.slate_clip_name_token_push_button,
                    )

        def validate_fields() -> bool:

            if not self.csv_path_entry.text():
                PyFlameMessageWindow(
                    message='Enter path to CSV file.',
                    type=MessageType.ERROR
                    )
                return False

            elif not os.path.isfile(self.csv_path_entry.text()):
                PyFlameMessageWindow(
                    message='CSV file does not exist.',
                    type=MessageType.ERROR
                    )
                return False

            elif not self.slate_clip_name_entry.text():
                PyFlameMessageWindow(
                    message='Enter Slate Name tokens for Slate Clip Naming.',
                    type=MessageType.ERROR
                    )
                return False

            return True

        def save_config():

            self.settings.save_config(
                config_values=
                    {
                        'csv_file_path': self.csv_path_entry.text(),
                        'date_format': self.date_push_button.text(),
                        'slate_clip_name': self.slate_clip_name_entry.text(),
                        'spaces_to_underscores': self.convert_spaces_button.isChecked(),
                        'create_ratio_folders' : self.create_resolutions_folders_button.isChecked(),
                        'clip_color': self.clip_color_push_button.get_color(),
                    }
                )

        def create_slates() -> None:

            if not validate_fields():
               return

            if not self.preflight_csv(self.csv_path_entry.text()):
                return

            save_config()

            self.window.hide()

            self.create_slates(
                csv_file_path=self.csv_path_entry.text(),
                date_format=self.date_push_button.text(),
                )

        def preview_slates() -> None:

            if not validate_fields():
                return

            if not self.preflight_csv(self.csv_path_entry.text()):
                return

            self.slate_preview(
                csv_file_path=self.csv_path_entry.text(),
                date_format=self.date_push_button.text(),
                )

        def edit_csv() -> None:

            if not os.path.isfile(self.csv_path_entry.text()):
                PyFlameMessageWindow(
                    message='Enter path to valid CSV file.',
                    type=MessageType.ERROR
                    )
                return

            self.csv_editor(csv_file_path=self.csv_path_entry.text())

        #-------------------------------------

        if not validate_selection():
            return

        slate_ratios = get_slate_ratios()
        if slate_ratios is None:
            return

        self.slate_templates = get_slate_templates()
        if not self.slate_templates:
            return

        #-------------------------------------

        # Create Main Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=save_config,
            grid_layout_columns=6,
            grid_layout_rows=7,
            )

        # Labels
        self.slate_ratios_label = PyFlameLabel(text='Selected Slate Ratios')
        self.csv_label = PyFlameLabel(text='CSV File')
        self.date_format_label = PyFlameLabel(text='Date Format')
        self.slate_clip_name_label = PyFlameLabel(text='Slate Name')
        self.clip_color_label = PyFlameLabel(text='Slate Clip Color')

        # Entry Fields
        self.slate_ratios_field = PyFlameEntry(
            text=slate_ratios,
            read_only=True,
            )
        self.csv_path_entry = PyFlameEntry(
            text=self.settings.csv_file_path,
            )
        self.slate_clip_name_entry = PyFlameEntry(
            text=self.settings.slate_clip_name,
            )

        # Push Button Menu
        self.date_push_button = PyFlamePushButtonMenu(
            text=self.settings.date_format,
            menu_options=[
                'yy/mm/dd',
                'yyyy/mm/dd',
                'mm/dd/yy',
                'mm/dd/yyyy',
                'dd/mm/yy',
                'dd/mm/yyyy'
                ],
            max_width=True,
            )

        # Token Push Button Menu
        self.slate_clip_name_token_push_button = PyFlameTokenPushButton(
            token_dest=self.slate_clip_name_entry,
            )

        # Wire up text_changed after the token button exists
        self.csv_path_entry.text_changed(
            lambda text: self.get_clip_name_tokens(
                csv_file_path=text,
                clip_name_push_button=self.slate_clip_name_token_push_button,
                )
            )

        # Clip Color Push Button Menu
        self.clip_color_push_button = PyFlameColorPushButtonMenu(
            color=self.settings.clip_color,
            )

        # Toggle Push Buttons
        self.convert_spaces_button = PyFlamePushButton(
            text='Spaces to _',
            button_checked=self.settings.spaces_to_underscores,
            tooltip='Convert spaces in clip name to underscores',
            )
        self.create_resolutions_folders_button = PyFlamePushButton(
            text=' Create Folders',
            button_checked=self.settings.create_ratio_folders,
            tooltip='Create separate folders for each slate resolution in Slate Library',
            )

        # Action Buttons
        self.csv_browse_button = PyFlameButton(text='Browse', connect=csv_browse)
        self.edit_csv_button = PyFlameButton(text='Edit CSV', connect=edit_csv)
        self.preview_slates_button = PyFlameButton(text='Preview Slates', connect=preview_slates)
        self.cancel_button = PyFlameButton(text='Cancel', connect=self.window.close)
        self.create_slates_button = PyFlameButton(
            text='Create Slates',
            connect=create_slates,
            color=Color.BLUE,
            )

        # Populate token menu from CSV
        self.get_clip_name_tokens(
            csv_file_path=self.csv_path_entry.text(),
            clip_name_push_button=self.slate_clip_name_token_push_button,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.slate_ratios_label, 0, 0)
        self.window.grid_layout.addWidget(self.slate_ratios_field, 0, 1, 1, 4)
        self.window.grid_layout.addWidget(self.create_resolutions_folders_button, 0, 5)

        self.window.grid_layout.addWidget(self.csv_label, 1, 0)
        self.window.grid_layout.addWidget(self.csv_path_entry, 1, 1, 1, 4)
        self.window.grid_layout.addWidget(self.csv_browse_button, 1, 5)

        self.window.grid_layout.addWidget(self.slate_clip_name_label, 2, 0)
        self.window.grid_layout.addWidget(self.slate_clip_name_entry, 2, 1, 1, 3)
        self.window.grid_layout.addWidget(self.slate_clip_name_token_push_button, 2, 4)
        self.window.grid_layout.addWidget(self.convert_spaces_button, 2, 5)

        self.window.grid_layout.addWidget(self.date_format_label, 3, 0)
        self.window.grid_layout.addWidget(self.date_push_button, 3, 1)

        self.window.grid_layout.addWidget(self.clip_color_label, 4, 0)
        self.window.grid_layout.addWidget(self.clip_color_push_button, 4, 1)

        self.window.grid_layout.addWidget(self.edit_csv_button, 4, 4)
        self.window.grid_layout.addWidget(self.preview_slates_button, 4, 5)

        self.window.grid_layout.addWidget(self.cancel_button, 6, 4)
        self.window.grid_layout.addWidget(self.create_slates_button, 6, 5)

    def slate_preview(self, csv_file_path, date_format) -> None:

        def create_preview_text():

            def read_type_node_setups() -> None:

                def read_type_node_setup(type_node_setup_path: str) -> list:

                    print('Type Node Setup Path: ', type_node_setup_path)

                    slate_text_list = []

                    tree = ET.parse(type_node_setup_path)
                    root = tree.getroot()

                    for char_set in root.findall('.//CharacterSet'):
                        try:
                            type_elem = char_set.find('Text')
                            if type_elem is not None:
                                slate_text = type_elem.text.strip()
                                slate_text = convert_ascii_to_text(slate_text)
                                slate_text_list.append(slate_text)
                        except:
                            pass

                    return slate_text_list

                def create_slate_template_preview() -> list:

                    slate_preview = ['--== Slate Template ==--']

                    for template_file in os.listdir(self.templates_path):
                        if template_file.endswith('.type_node'):
                            slate_preview.extend([' ', f'Slate Template: {template_file}', ' '])
                            slate_template_path = os.path.join(self.templates_path, template_file)
                            print('slate_template_path: ', slate_template_path)
                            slate_template_text = read_type_node_setup(slate_template_path)
                            for line in slate_template_text:
                                slate_preview.append(line)

                    return slate_preview

                def create_slates_preview(slate_preview: list) -> list:

                    slate_preview.extend([' ', '--== Slates ==--'])

                    slates = [slate for slate in os.listdir(self.temp_path) if slate.endswith('.type_node')]
                    slates.sort()

                    for slate in slates:
                        slate_name = 'Slate Name: ' + slate.rsplit('.', 1)[0]
                        try:
                            slate_ratio = slate_name.rsplit('_', 1)[1]
                            slate_name = slate_name.rsplit('_', 1)[0]
                        except:
                            pass

                        slate_preview.append(' ')
                        slate_preview.append(f'{slate_name}')
                        try:
                            slate_preview.append(f'Slate Ratio: {slate_ratio}')
                        except:
                            pass
                        slate_preview.append(' ')

                        slate_path = os.path.join(self.temp_path, slate)
                        slate_text = read_type_node_setup(slate_path)
                        for line in slate_text:
                            slate_preview.append(line)

                    return slate_preview

                slate_preview = create_slate_template_preview()
                slate_preview = create_slates_preview(slate_preview)

                print('\nSlate Preview:\n')
                for line in slate_preview:
                    pyflame.print(line, text_color=TextColor.BLUE, print_to_flame=False, new_line=False)
                print('\n', end='')

                self.preview_text_edit.setText('\n'.join(slate_preview))

            pyflame.print('Creating Slate Preview...', text_color=TextColor.GREEN)

            slate_dict = self.create_slate_dicts(csv_file_path, date_format)
            print(slate_dict)

            self.create_type_nodes(slate_dict)

            read_type_node_setups()

        def copy_text():
            pyflame.copy_to_clipboard(self.preview_text_edit.text())

        def close_preview_window():
            self.clean_temp_folder()
            self.preview_window.close()

        self.clean_temp_folder()

        self.preview_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Slate Preview <small>{SCRIPT_VERSION}',
            return_pressed=close_preview_window,
            grid_layout_columns=6,
            grid_layout_rows=16,
            )

        self.preview_slates_label = PyFlameLabel(
            text='Slates',
            style=Style.UNDERLINE,
            )

        self.preview_text_edit = PyFlameTextEdit(
            text='',
            read_only=True,
            )

        self.preview_copy_button = PyFlameButton(
            text='Copy to Clipboard',
            connect=copy_text,
            )
        self.preview_close_button = PyFlameButton(
            text='Close',
            connect=close_preview_window,
            color=Color.BLUE,
            )

        create_preview_text()

        self.preview_window.grid_layout.addWidget(self.preview_slates_label, 0, 0, 1, 6)
        self.preview_window.grid_layout.addWidget(self.preview_text_edit, 1, 0, 14, 6)
        self.preview_window.grid_layout.addWidget(self.preview_copy_button, 16, 4)
        self.preview_window.grid_layout.addWidget(self.preview_close_button, 16, 5)

    def csv_editor(self, csv_file_path) -> None:

        def save_csv(csv_file_path):

            def save_file(csv_file_path):
                self.csv_editor_csv_table.save_csv_file(csv_file_path)
                self.csv_editor_window.close()
                self.csv_path_entry.setText(csv_file_path)
                pyflame.print('CSV Saved', text_color=TextColor.GREEN)

            csv_root_path = os.path.dirname(csv_file_path)
            csv_file_path = os.path.join(csv_root_path, self.csv_editor_selected_csv_entry.text())
            print('CSV File Path:', csv_file_path)

            if csv_file_path == '':
                PyFlameMessageWindow(
                    message='Enter a CSV file path.',
                    type=MessageType.ERROR,
                    )
                return

            if os.path.exists(csv_file_path):
                overwrite = PyFlameMessageWindow(
                    message='File already exists. Overwrite?',
                    type=MessageType.WARNING,
                    )
                if overwrite:
                    save_file(csv_file_path)
                else:
                    pyflame.print('CSV Save Cancelled', text_color=TextColor.RED)
            else:
                save_file(csv_file_path)

        def close_csv_editor_window():
            self.csv_editor_window.close()

        self.csv_editor_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: CSV Editor <small>{SCRIPT_VERSION}',
            return_pressed=save_csv,
            grid_layout_columns=6,
            grid_layout_rows=17,
            )

        self.csv_editor_csv_label = PyFlameLabel(text='Selected CSV')

        self.csv_editor_selected_csv_entry = PyFlameEntry(
            text=csv_file_path.split('/')[-1],
            )

        self.csv_editor_csv_table = PyFlameTable(csv_file_path=csv_file_path)

        self.csv_editor_cancel_button = PyFlameButton(
            text='Close',
            connect=close_csv_editor_window,
            )
        self.csv_editor_save_button = PyFlameButton(
            text='Save',
            connect=partial(save_csv, csv_file_path),
            color=Color.BLUE,
            )

        self.csv_editor_horizontal_line_01 = PyFlameHorizontalLine()

        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_csv_label, 0, 0)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_selected_csv_entry, 0, 1, 1, 5)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_horizontal_line_01, 1, 0, 1, 6)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_csv_table, 2, 0, 14, 6)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_cancel_button, 17, 4)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_save_button, 17, 5)

    #-------------------------------------
    # [Misc Functions]
    #-------------------------------------

    def get_slate_ratios_from_clip_name(self, clip) -> str:

        match = re.search(r'(\d+)x(\d+)', str(clip.name)[1:-1])
        if match:
            return f"{match.group(1)}x{match.group(2)}"
        PyFlameMessageWindow(
            message='Slate background clip name must contain have a underscore and ratio.\n\nExample: slate_background_16x9',
            type=MessageType.ERROR
            )
        return None

    def clean_temp_folder(self) -> None:

        for file in os.listdir(self.temp_path):
            if os.path.isfile(os.path.join(self.temp_path, file)):
                os.remove(os.path.join(self.temp_path, file))

    def get_clip_name_tokens(self, csv_file_path, clip_name_push_button) -> None:

        if os.path.exists(csv_file_path):

            with open(csv_file_path, 'r') as csv_file:
                csv_token_line = csv_file.readline().strip()
            csv_token_line = csv_token_line.split(',')

            token_menu_dict = {}

            for name in csv_token_line:
                menu_key = name
                menu_value = '<' + name + '>'
                token_menu_dict[menu_key] = menu_value

            token_menu_dict['CURRENT_DATE'] = '<CURRENT_DATE>'

            clip_name_push_button.add_menu_options(token_menu_dict)

    def color_segment(self, segment) -> None:

        color_name = self.clip_color_push_button.get_color()
        rgba_value = self.clip_color_push_button.get_color_value()

        if color_name != 'No Color':
            segment.colour = rgba_value

    def update_progress_window(self, slates_created, slates_total) -> int:

        self.progress_window.set_progress_value(slates_created)
        self.progress_window.set_text(f'Processing Slate: [{str(slates_created)} of {str(slates_total)}]')

        slates_created += 1

        return slates_created

    #-------------------------------------

    def preflight_csv(self, csv_file_path: str) -> bool:
        """
        Pre-flight CSV validation.

        Checks for structural errors (block creation) and warns about
        rows that will be silently skipped or produce incomplete names.
        Returns False if the user cancels or an error is found.
        """

        errors = []
        warnings = []

        with open(csv_file_path, mode='r', newline='') as f:
            reader = csv.reader(f)
            try:
                headers = [h.strip() for h in next(reader)]
            except StopIteration:
                PyFlameMessageWindow(
                    message='CSV pre-flight: file is empty.',
                    type=MessageType.ERROR,
                    )
                return False
            rows = list(reader)

        # No data rows
        if not rows:
            errors.append('File has no data rows (header only).')

        else:
            # Headers must be ALL CAPS
            non_caps = [h for h in headers if h and h != h.upper()]
            if non_caps:
                errors.append(f'Column headers must be ALL CAPS: {", ".join(non_caps)}')

            # RATIO required when multiple backgrounds selected
            if len(self.selection) > 1 and 'RATIO' not in headers:
                errors.append('RATIO column is required when multiple slate backgrounds are selected.')

            # Slate name tokens must exist in headers
            slate_name_pattern = self.slate_clip_name_entry.text()
            name_tokens = re.findall(r'<([^<>]+)>', slate_name_pattern)
            missing_tokens = [t for t in name_tokens if t not in headers and t != 'CURRENT_DATE']
            if missing_tokens:
                errors.append(f'Slate name uses tokens not found in CSV headers: {", ".join(missing_tokens)}')

            # RATIO values that don't match any selected background will be skipped
            if 'RATIO' in headers:
                ratio_idx = headers.index('RATIO')

                blank_ratio_rows = [
                    str(i)
                    for i, row in enumerate(rows, start=2)
                    if len(row) <= ratio_idx or not row[ratio_idx].strip()
                    ]
                if blank_ratio_rows:
                    sample = ', '.join(blank_ratio_rows[:5])
                    suffix = f' (+{len(blank_ratio_rows) - 5} more)' if len(blank_ratio_rows) > 5 else ''
                    warnings.append(
                        f'{len(blank_ratio_rows)} row(s) have a blank RATIO value and will be skipped '
                        f'(rows {sample}{suffix})'
                        )

                csv_ratios = {
                    row[ratio_idx].strip()
                    for row in rows
                    if len(row) > ratio_idx and row[ratio_idx].strip()
                    }
                unmatched = csv_ratios - set(self.slate_ratios)
                if unmatched:
                    warnings.append(
                        f'{sum(1 for r in rows if len(r) > ratio_idx and r[ratio_idx].strip() in unmatched)} '
                        f'row(s) have ratios with no matching background and will be skipped '
                        f'({", ".join(sorted(unmatched))})'
                        )
                if not (csv_ratios & set(self.slate_ratios)):
                    errors.append('No CSV rows match the selected slate backgrounds — no slates would be created.')

            # Rows where slate-name tokens are empty produce incomplete names
            name_tokens_in_csv = [t for t in name_tokens if t in headers and t != 'CURRENT_DATE']
            if name_tokens_in_csv:
                empty_rows = [
                    str(i)
                    for i, row in enumerate(rows, start=2)
                    for d in [dict(zip(headers, row))]
                    if any(not d.get(t, '').strip() for t in name_tokens_in_csv)
                    ]
                if empty_rows:
                    sample = ', '.join(empty_rows[:5])
                    suffix = f' (+{len(empty_rows) - 5} more)' if len(empty_rows) > 5 else ''
                    warnings.append(
                        f'{len(empty_rows)} row(s) have empty slate-name values '
                        f'(rows {sample}{suffix}) — those slates will have incomplete names.'
                        )

        if errors:
            message = 'CSV pre-flight failed:\n\n' + '\n'.join(f'• {e}' for e in errors)
            if warnings:
                message += '\n\nAlso:\n' + '\n'.join(f'• {w}' for w in warnings)
            PyFlameMessageWindow(message=message, type=MessageType.ERROR)
            return False

        if warnings:
            message = 'CSV pre-flight warnings:\n\n' + '\n'.join(f'• {w}' for w in warnings)
            message += '\n\nProceed with slate creation?'
            return bool(PyFlameMessageWindow(message=message, type=MessageType.WARNING))

        return True

    #-------------------------------------

    def create_slates(self, csv_file_path, date_format) -> None:

        def create_slate_library() -> None:

            self.slate_library = flame.projects.current_project.current_workspace.create_library('-= Slates =-')
            self.slate_library.expanded = True

            pyflame.print('Slate Library Created', text_color=TextColor.GREEN)

        def create_slated_clips() -> None:

            def get_tag_value(flame_pyobject, tag_name) -> str:

                for tag in flame_pyobject.tags.get_value():
                    if tag.startswith(tag_name + ': '):
                        tag_value = tag.split(':')[1].strip()
                        print('Tag Value:', tag_value)
                        return tag_value

                return None

            def create_type_node_slate_clip(slate_background, type_node_setup, slate_dest, slate_bg_ratio) -> None:

                clip = flame.media_panel.copy(slate_background, slate_dest)[0]

                clip_name = str(type_node_setup.rsplit('/', 1)[1])[:-10]
                # Strip the ratio suffix from the setup filename, but only if one is
                # actually there - in single-background/no-RATIO mode there is none.
                base_name, _, last_segment = clip_name.rpartition('_')
                if base_name and re.fullmatch(r'\d+x\d+', last_segment):
                    clip_name = base_name
                clip.name = clip_name
                print('Clip Name:', clip.name)

                token_values = self.setup_token_map.get(os.path.basename(type_node_setup), {})

                metadata_keys = {
                    'SlateName': clip_name,
                    'SlateRatio': slate_bg_ratio,
                    'TokenizedSlateName': self.settings.slate_clip_name,
                    'SlateDateFormat': date_format,
                    'SlateSpaces': int(self.convert_spaces_button.isChecked()),
                    'SlateVersion': '2',
                    METADATA_TOKEN_ORDER_KEY: '|'.join(token_values),
                    }
                for token, value in token_values.items():
                    metadata_keys[f'{METADATA_TOKEN_PREFIX}{token}'] = value

                stamp_slate_metadata(clip.versions[0].tracks[0].segments[0], metadata_keys)

                pyflame.print(f'Creating Slate: {str(clip.name)[1:-1]}', new_line=False, text_color=TextColor.GREEN)

                seg = clip.versions[0].tracks[0].segments[0]
                for fx in seg.effects:
                    if fx.type == 'Type':
                        fx.load_setup(type_node_setup)

                self.color_segment(seg)

            pyflame.print('Creating Slated Clips...', text_color=TextColor.GREEN)

            slates_created = 1
            slates_total = len(slate_dict)

            for slate_bg_clip in self.selection:
                print('Slate Background Clip:', slate_bg_clip)
                slate_bg_ratio = get_tag_value(slate_bg_clip, 'SlateRatio')
                print('Slate Background Ratio:', slate_bg_ratio)

                type_node_setup_list = [f for f in os.listdir(self.temp_path) if f.endswith(f'_{slate_bg_ratio}.type_node')]
                print('Type Node Setup List:', type_node_setup_list)

                if len(self.selection) == 1 and 'RATIO' not in self.row_dict:
                    type_node_setup_list = [f for f in os.listdir(self.temp_path) if f.endswith('.type_node')]

                for type_node_setup in type_node_setup_list:
                    print('Type Node Setup:', type_node_setup)
                    type_node_setup_path = os.path.join(self.temp_path, type_node_setup)
                    print('Type Node Setup Path:', type_node_setup_path)

                    if self.settings.create_ratio_folders:
                        existing_ratio_folders = [str(folder.name)[1:-1] for folder in self.slate_library.folders]
                        if slate_bg_ratio not in existing_ratio_folders:
                            slate_ratio_folder = self.slate_library.create_folder(slate_bg_ratio)
                            slate_ratio_folder.expanded = True
                            slate_dest = slate_ratio_folder
                        else:
                            slate_dest = next(f for f in self.slate_library.folders if str(f.name)[1:-1] == slate_bg_ratio)
                    else:
                        slate_dest = self.slate_library

                    create_type_node_slate_clip(
                        slate_background=slate_bg_clip,
                        type_node_setup=type_node_setup_path,
                        slate_dest=slate_dest,
                        slate_bg_ratio=slate_bg_ratio,
                        )

                    slates_created = self.update_progress_window(slates_created, slates_total)

            print('\n', end='')

        #-------------------------------------

        create_slate_library()

        slate_dict = self.create_slate_dicts(csv_file_path, date_format)

        if slate_dict == {}:
            PyFlameMessageWindow(
                message='Ratio not found in CSV file.\n\nNo slates to create.',
                type=MessageType.ERROR
                )
            return

        self.progress_window = PyFlameProgressWindow(
            num_to_do=len(slate_dict),
            title='Creating Slates',
            )

        self.create_type_nodes(slate_dict)

        create_slated_clips()

        pyflame.cleanup_temp_folder()

        self.progress_window.enable_done_button(True)

        self.window.close()

        self.progress_window.set_title_text('Slate Creation Complete')

        pyflame.print('Slate Creation Complete', text_color=TextColor.GREEN)

        # Teach the Update <Field> menu this run's tokens (in CSV order).
        run_tokens = []
        for token_values in self.setup_token_map.values():
            for token in token_values:
                if token not in run_tokens:
                    run_tokens.append(token)
        learn_update_fields(self.settings, run_tokens)

    def create_slate_dicts(self, csv_file_path, date_format) -> dict:

        def add_to_slate_dict(slate_name: str) -> None:

            slate_dict[slate_key] = {'_Slate Name': slate_name}
            slate_dict[slate_key].update(self.row_dict)

        def resolve_slate_name_tokens(row_dict: dict) -> str:

            slate_name = str(self.slate_clip_name_entry.text())

            for token, value in row_dict.items():
                token_placeholder = f'<{token}>'
                if token_placeholder in slate_name:
                    value = re.sub(r'[\\/*?:"<>|]', '_', value.strip())
                    slate_name = slate_name.replace(token_placeholder, value)

            return slate_name

        def check_duplicate_name(slate_names: list, base_name: str) -> str:

            if base_name in slate_names:
                i = 1
                while f'{base_name}_{i}' in slate_names:
                    i += 1
                return f'{base_name}_{i}'
            return base_name

        pyflame.print('Creating Slate Dicts...', text_color=TextColor.GREEN)

        self.current_date = resolve_date(date_format)
        print('Current Date:', self.current_date)
        print('CSV File Path:', csv_file_path, '\n')

        slate_dict = {}
        slate_names = []

        with open(csv_file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            tokens = next(reader)
            for index, row in enumerate(reader, start=1):
                slate_key = f"Slate {index}"
                self.row_dict = dict(zip(tokens, row))

                if 'CURRENT_DATE' in self.row_dict:
                    self.row_dict['CURRENT_DATE'] = self.current_date

                slate_name = resolve_slate_name_tokens(self.row_dict)

                if slate_name in slate_names:
                    slate_name = check_duplicate_name(slate_names, slate_name)
                    slate_names.append(slate_name)
                else:
                    slate_names.append(slate_name)

                if '<CURRENT_DATE>' in slate_name:
                    slate_name = slate_name.replace('<CURRENT_DATE>', self.current_date)

                if len(self.selection) > 1 or 'RATIO' in self.row_dict:
                    ratio = self.row_dict['RATIO']
                    slate_name = f'{slate_name}_{ratio}'
                    if ratio in self.slate_ratios:
                        add_to_slate_dict(slate_name)
                    else:
                        print('Skipping:', slate_name)
                else:
                    add_to_slate_dict(slate_name)

        pyflame.print('Slate Dicts Created', text_color=TextColor.GREEN)

        return slate_dict

    def create_type_nodes(self, slate_dict: dict) -> None:

        def generate_type_node_setups(slate_name: str, slate_dict: dict, slate_template: str) -> None:

            def get_slate_name(slate_name: str, slate_dict: dict) -> str:

                for key, value in slate_dict.items():
                    if key == slate_name:
                        for token, value in value.items():
                            if token == '_Slate Name':
                                slate_name = value

                slate_name = re.sub(r'[\\/*?:"<>|]', ' ', slate_name)

                if self.convert_spaces_button.isChecked():
                    slate_name = re.sub(r' ', '_', slate_name)

                return slate_name

            def generate_type_node_name(slate_name: str) -> str:

                type_node_name = f'{slate_name}.type_node'

                i = 1
                while os.path.exists(os.path.join(self.temp_path, type_node_name)):
                    type_node_name = f'{slate_name}_{i}.type_node'
                    i += 1

                return type_node_name

            def edit_type_node(slate_name: str, slate_dict: dict, slate_template: str) -> None:

                tree = ET.parse(slate_template)
                root = tree.getroot()

                for char_set in root.findall('.//CharacterSet'):
                    type_elem = char_set.find('Text')
                    if type_elem is not None:
                        original_value = type_elem.text or ''
                        translated_value = convert_ascii_to_text(original_value)

                        tokens = re.findall(r'<([^<>]+)>', translated_value)
                        for token in tokens:
                            token_placeholder = f'<{token}>'
                            if token in slate_dict[slate]:
                                value = slate_dict[slate][token]
                                translated_value = translated_value.replace(token_placeholder, value)
                            if token == 'CURRENT_DATE':
                                translated_value = translated_value.replace(token_placeholder, self.current_date)

                        ascii_value = convert_text_to_ascii(translated_value)
                        type_elem.text = ascii_value

                type_node_name = generate_type_node_name(slate_name)

                tree.write(
                    os.path.join(self.temp_path, type_node_name),
                    encoding='utf-8',
                    xml_declaration=True,
                    )

                # Record which token values produced this setup so the slate clip
                # can be stamped with SlateToken tags for later updating.
                token_values = {k: v for k, v in slate_dict[slate].items() if k != '_Slate Name'}
                token_values['CURRENT_DATE'] = self.current_date
                self.setup_token_map[type_node_name] = token_values

            pyflame.print(f'Creating Type Node Setup: {slate_name}', new_line=False, text_color=TextColor.GREEN)

            slate_name = get_slate_name(slate_name, slate_dict)
            print('Slate Name:', slate_name)

            edit_type_node(slate_name, slate_dict, slate_template)

        pyflame.print('Creating Type Node Setups...')

        if len(self.selection) > 1:
            for slate in slate_dict:
                print('Slate:', slate)
                ratio = slate_dict[slate]['RATIO']
                if ratio in self.slate_ratios:
                    template_file_path = next(
                        (os.path.join(self.templates_path, f) for f in os.listdir(self.templates_path)
                         if f.endswith(ratio + '.type_node')),
                        None
                        )
                    if template_file_path:
                        generate_type_node_setups(slate, slate_dict, template_file_path)
                    else:
                        pyflame.print(f'No template found for ratio {ratio}, skipping slate: {slate}', text_color=TextColor.RED)
        else:
            if 'RATIO' in self.row_dict:
                for slate in slate_dict:
                    print('Slate:', slate)
                    ratio = slate_dict[slate]['RATIO']
                    print('Ratio:', ratio)
                    if ratio in self.slate_ratios:
                        template_file_path = next(
                            (os.path.join(self.templates_path, f) for f in os.listdir(self.templates_path)
                             if f.endswith(ratio + '.type_node')),
                            None
                            )
                        print('Template File Path:', template_file_path)
                        if template_file_path:
                            generate_type_node_setups(slate, slate_dict, template_file_path)
                        else:
                            pyflame.print(f'No template found for ratio {ratio}, skipping slate: {slate}', text_color=TextColor.RED)
            else:
                for slate in slate_dict:
                    generate_type_node_setups(slate, slate_dict, self.slate_templates[0])

        pyflame.print('Completed: Creating Type Node Setups', text_color=TextColor.GREEN)

        print('\n', end='')

#-------------------------------------
# [Update Mode]
#-------------------------------------

class SlateUpdater():
    """
    Bulk token editor for slates created by Slate Maker v2.0.0+.

    Reads the SlateToken tags stamped onto slate clips at creation, presents all
    tokens found across the selection with their current values, and applies
    exact-value replacement inside each slate's Type Node text. Names and tags
    are updated to match the new values.

    Works on slate clips in the media panel and on sequences with a slate cut
    in - for sequences the slate segment is located by its tags (clip tags
    propagate onto the segment when edited into a sequence) and its Type Node
    is updated in place.

    When single_token is given (the Update Field submenu), the editor window is
    restricted to that one token - everything else (slate gathering, replacement,
    renaming, re-tagging) is the same flow. In this mode items WITHOUT Slate Maker
    tags are also updatable: the first segment is taken as the slate and the field
    is matched by its label line in the Type Node text ('Agency: value'), replacing
    the text after the label. Untagged slates get a pure text edit - no rename and
    no tags are added.
    """

    def __init__(self, selection: Any, single_token: str = None) -> None:

        self.single_token = single_token
        mode_title = f'Update {field_display_name(single_token)}' if single_token else 'Update Slates'
        pyflame.print_title(f'{SCRIPT_NAME}: {mode_title} {SCRIPT_VERSION}')

        self.install_verified = pyflame.verify_script_install()
        if not self.install_verified:
            return

        self.selection = selection
        self.settings = PyFlameConfig(config_values=dict(DEFAULT_CONFIG))
        self.temp_path = pyflame.create_temp_folder()

        if flame.get_current_tab() == 'MediaHub':
            flame.go_to('Timeline')

    def slate_updater(self) -> None:

        if not self.install_verified:
            return

        def read_slate_info(item) -> dict:
            """
            Read v2 slate metadata from a selected item.

            Handles both cases:
            - A slate clip: tags live on the clip itself.
            - A sequence with a slate cut in: tags live on the slate segment
              (clip tags propagate onto the segment when edited into a sequence).

            Returns None if no SlateToken tags or no Type Node is found. If a
            sequence contains more than one slate segment, the first is used.
            """

            # Legacy tag-stamped slate clip - tags live on the clip itself.
            info = read_slate_tags(item.tags.get_value())
            if info:
                if not find_type_fx(item):
                    return None
                info['clip'] = item
                info['segment'] = None
                info['name'] = str(item.name)[1:-1]
                return info

            is_sequence = isinstance(item, flame.PySequence)

            # Walk segments for slate metadata - Metadata effect custom keys
            # (v2.5.0+ slate clips and sequences) or tags propagated onto the
            # segment (legacy slates cut into a sequence).
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        info = read_segment_slate_data(segment)
                        if info is None:
                            continue
                        if not any(fx.type == 'Type' for fx in segment.effects):
                            continue
                        info['clip'] = item
                        # For a bare slate clip the clip itself is renamed on
                        # update, not its inner segment.
                        info['segment'] = segment if is_sequence else None
                        info['name'] = str(item.name)[1:-1]
                        return info

            # Any-slate fallback (Update Field only): no Slate Maker tags, so
            # take the first segment as the slate and read the field's current
            # value from its label line in the Type Node text.
            if not self.single_token:
                return None

            try:
                segment = item.versions[0].tracks[0].segments[0]
            except (AttributeError, IndexError):
                return None

            if not any(fx.type == 'Type' for fx in segment.effects):
                return None

            probe_path = os.path.join(self.temp_path, 'gather_probe.type_node')
            next(fx for fx in segment.effects if fx.type == 'Type').save_setup(probe_path)
            value, _ = find_label_value(decode_type_node_layers(probe_path), self.single_token)

            if value is None:
                return None

            return {
                'tokens': {self.single_token: value},
                'token_order': [self.single_token],
                'date_format': None,
                'spaces_to_underscores': True,
                'tokenized_name': '',
                'clip': item,
                'segment': segment,
                'name': str(item.name)[1:-1],
                'untagged': True,
                }

        def get_slate_fx(info: dict):
            """Return the Type effect to read/write for this slate - on the slate
            segment for sequences, on the clip for library slate clips."""

            if info['segment'] is not None:
                for fx in info['segment'].effects:
                    if fx.type == 'Type':
                        return fx
                return None

            return find_type_fx(info['clip'])

        def gather_slates() -> bool:

            pyflame.print('Reading slate metadata from selected clips...', new_line=False)

            self.slates = []
            skipped = []

            for clip in self.selection:
                info = read_slate_info(clip)
                if info is None:
                    skipped.append(str(clip.name)[1:-1])
                else:
                    self.slates.append(info)

            if not self.slates:
                if self.single_token:
                    reason = (
                        f'Update Field needs either Slate Maker v2 token metadata, or a '
                        f'Type Node on the first segment whose text contains a '
                        f'"{self.single_token}" label line (e.g. '
                        f'"{field_display_name(self.single_token)}: value").'
                        )
                else:
                    reason = (
                        'Update Slates works on slate clips created with Slate Maker '
                        'v2.0.0+, or on sequences with one of those slates cut in.'
                        )
                PyFlameMessageWindow(
                    message=f'None of the selected items are updatable slates.\n\n{reason}',
                    type=MessageType.ERROR,
                    )
                return False

            pyflame.print(f'{len(self.slates)} updatable slate(s) found.', text_color=TextColor.GREEN)

            if skipped:
                sample = '\n'.join(f'• {name}' for name in skipped[:10])
                suffix = f'\n(+{len(skipped) - 10} more)' if len(skipped) > 10 else ''
                if self.single_token:
                    skip_reason = (
                        f'have no Slate Maker token metadata and no "{self.single_token}" '
                        f'label line on their first segment'
                        )
                else:
                    skip_reason = 'have no Slate Maker token metadata'
                proceed = PyFlameMessageWindow(
                    message=(
                        f'{len(skipped)} selected item(s) {skip_reason} '
                        f'and will be skipped:\n\n{sample}{suffix}\n\n'
                        f'Continue with the {len(self.slates)} updatable slate(s)?'
                        ),
                    type=MessageType.WARNING,
                    )
                if not proceed:
                    return False

            return True

        def protect_from_editing_check() -> bool:

            pyflame.print('Checking Protect From Editing setting...', new_line=False)

            new_clip = None

            try:
                source = self.slates[0]
                new_clip = flame.duplicate(source['clip'])
                new_clip.name = 'protect_from_editing_test_clip'

                # Test on the duplicate's slate segment when the source is a
                # sequence - its first segment could be a gap where effect
                # creation fails for reasons other than protection.
                seg = None
                if source['segment'] is not None:
                    for version in new_clip.versions:
                        for track in version.tracks:
                            for segment in track.segments:
                                if read_segment_slate_data(segment):
                                    seg = segment
                                    break
                            if seg:
                                break
                        if seg:
                            break
                if seg is None:
                    seg = new_clip.versions[0].tracks[0].segments[0]

                seg.create_effect('Text')
                flame.delete(new_clip)
                pyflame.print('Protect From Editing is turned off, continuing...', text_color=TextColor.GREEN)
                return False
            except:
                if new_clip:
                    flame.delete(new_clip)
                PyFlameMessageWindow(
                    message='Turn off Protect from Editing: Flame Preferences -> General.',
                    type=MessageType.ERROR
                    )
                return True

        def build_token_summary() -> dict:
            """
            Union of tokens across all selected slates, in order of first appearance.
            Value is the shared current value, or the VARIES sentinel when slates disagree.
            RATIO is excluded - it is structural (tied to the background) and not editable.
            """

            token_order = []
            for info in self.slates:
                for token in info['token_order']:
                    if token != 'RATIO' and token not in token_order:
                        token_order.append(token)

            summary = {}
            for token in token_order:
                values = {info['tokens'][token] for info in self.slates if token in info['tokens']}
                summary[token] = values.pop() if len(values) == 1 else VARIES

            return summary

        def set_date_to_today(token: str) -> None:

            formats = [info['date_format'] for info in self.slates if info['date_format']]
            date_format = formats[0] if formats else self.settings.date_format

            if len(set(formats)) > 1:
                pyflame.print(f'Multiple date formats found across selected slates - using {date_format}.', text_color=TextColor.YELLOW)

            entry, _ = self.token_entries[token]
            entry.setText(resolve_date(date_format))

        def build_update_plan(changes: dict) -> list:
            """
            For each slate, work out which token substitutions apply, extract its
            current Type Node setup to temp, and count occurrences of each old value
            in the decoded slate text.
            """

            pyflame.print('Building update plan...', new_line=False)

            plan = []

            for index, info in enumerate(self.slates):
                subs = []
                for token, new_value in changes.items():
                    if token in info['tokens'] and info['tokens'][token] != new_value:
                        subs.append({
                            'token': token,
                            'old': info['tokens'][token],
                            'new': new_value,
                            'label_based': info.get('untagged', False),
                            })

                if not subs:
                    continue

                setup_path = os.path.join(self.temp_path, f'update_{index:03d}.type_node')
                get_slate_fx(info).save_setup(setup_path)

                decoded_layers = decode_type_node_layers(setup_path)
                decoded_text = '\n'.join(decoded_layers)

                for sub in subs:
                    if sub['label_based']:
                        _, sub['occurrences'] = find_label_value(decoded_layers, sub['token'])
                    else:
                        sub['occurrences'] = decoded_text.count(sub['old']) if sub['old'] else 0

                plan.append({'info': info, 'setup_path': setup_path, 'subs': subs})

            pyflame.print(f'{len(plan)} slate(s) affected by edited tokens.', text_color=TextColor.GREEN)

            return plan

        def confirm_update(plan: list) -> bool:

            lines = [f'About to update {len(plan)} slate(s):', '']

            token_counts = {}
            for item in plan:
                for sub in item['subs']:
                    token_counts.setdefault(sub['token'], {'count': 0, 'new': sub['new']})
                    token_counts[sub['token']]['count'] += 1

            for token, tc in token_counts.items():
                lines.append(f"• {token} → '{tc['new']}'  ({tc['count']} slate(s))")

            notes = []
            for item in plan:
                name = item['info']['name']
                for sub in item['subs']:
                    if sub['label_based']:
                        if sub['occurrences'] == 0:
                            notes.append(f"• {name}: no {sub['token']} label line found in slate text — nothing will change.")
                        elif sub['occurrences'] > 1:
                            notes.append(f"• {name}: {sub['token']} label appears on {sub['occurrences']} lines — all will be updated.")
                    elif not sub['old']:
                        notes.append(f"• {name}: {sub['token']} original value is empty — slate text unchanged, name/metadata only.")
                    elif sub['occurrences'] == 0:
                        notes.append(f"• {name}: {sub['token']} value '{sub['old']}' not found in slate text — name/metadata only.")
                    elif sub['occurrences'] > 1:
                        notes.append(f"• {name}: {sub['token']} value '{sub['old']}' appears {sub['occurrences']} times — all occurrences will be replaced.")

            # Clean updates apply without confirming - the dialog only appears
            # when a value looks off (0 or multiple occurrences in the slate
            # text, empty original). Missing-metadata selections are already
            # flagged in gather_slates().
            if not notes:
                return True

            lines.extend(['', 'Notes:'] + notes)
            lines.extend(['', 'Proceed with update?'])

            return bool(PyFlameMessageWindow(message='\n'.join(lines), type=MessageType.WARNING))

        def apply_updates(plan: list) -> None:

            def name_fragment(value: str, spaces_to_underscores: bool) -> str:
                """Apply the same transforms clip naming applies to a token value."""

                fragment = re.sub(r'[\\/*?:"<>|]', '_', value.strip())
                if spaces_to_underscores:
                    fragment = fragment.replace(' ', '_')
                return fragment

            def update_type_node(item: dict) -> None:

                text_subs = sorted(
                    [s for s in item['subs']
                     if s['occurrences'] and (s['old'] or s['label_based'])],
                    key=lambda s: len(s['old']),
                    reverse=True,
                    )

                if not text_subs:
                    return

                tree = ET.parse(item['setup_path'])
                root = tree.getroot()

                for char_set in root.findall('.//CharacterSet'):
                    type_elem = char_set.find('Text')
                    if type_elem is not None and type_elem.text:
                        decoded = convert_ascii_to_text(type_elem.text)
                        for sub in text_subs:
                            if sub['label_based']:
                                decoded = replace_label_value(decoded, sub['token'], sub['new'])
                            else:
                                decoded = decoded.replace(sub['old'], sub['new'])
                        type_elem.text = convert_text_to_ascii(decoded)

                updated_path = item['setup_path'].replace('.type_node', '_updated.type_node')
                tree.write(updated_path, encoding='utf-8', xml_declaration=True)

                get_slate_fx(item['info']).load_setup(updated_path)

            def rename_slate(item: dict) -> str:
                """
                Rename the slate to match updated token values - the clip itself
                for library slates, the slate segment for sequences (the sequence's
                own name is left alone; re-run Rename from Slate to refresh it).
                """

                info = item['info']
                target = info['segment'] if info['segment'] is not None else info['clip']
                name = str(target.name)[1:-1]
                new_name = name

                for sub in item['subs']:
                    if f"<{sub['token']}>" not in info['tokenized_name']:
                        continue
                    old_fragment = name_fragment(sub['old'], info['spaces_to_underscores'])
                    new_fragment = name_fragment(sub['new'], info['spaces_to_underscores'])
                    if old_fragment and old_fragment in new_name:
                        new_name = new_name.replace(old_fragment, new_fragment)

                if new_name != name:
                    try:
                        target.name = new_name
                    except:
                        pyflame.print(f'Could not rename slate: {name}', text_color=TextColor.YELLOW)
                        return name
                    if info['segment'] is None:
                        info['name'] = new_name

                return new_name

            def restamp_metadata(item: dict, new_name: str) -> None:

                info = item['info']

                # Untagged slates (any-slate Update Field) are a pure text edit -
                # no Slate Maker metadata to refresh, and none is added.
                if info.get('untagged'):
                    return

                changed = {sub['token']: sub['new'] for sub in item['subs']}

                # v2.5.0+ storage - write back to the Metadata effect's custom keys.
                meta_fx = info.get('meta_fx')
                if meta_fx is not None:
                    for token, value in changed.items():
                        meta_fx.set_metadata_value(key=f'{METADATA_TOKEN_PREFIX}{token}', value=str(value))
                    meta_fx.set_metadata_value(key='SlateName', value=new_name)
                    return

                # Legacy tag storage
                tag_object = info['segment'] if info['segment'] is not None else info['clip']

                new_tags = []
                for tag in tag_object.tags.get_value():
                    if tag.startswith(TOKEN_TAG_PREFIX):
                        token = tag[len(TOKEN_TAG_PREFIX):].partition('=')[0].strip()
                        if token in changed:
                            new_tags.append(f'{TOKEN_TAG_PREFIX}{token}={escape_tag_value(changed[token])}')
                        else:
                            new_tags.append(tag)
                    elif tag.startswith('SlateName:'):
                        new_tags.append(f'SlateName: {new_name}')
                    else:
                        new_tags.append(tag)

                tag_object.tags = new_tags

            pyflame.print('Updating Slates...', text_color=TextColor.GREEN)

            self.progress_window = PyFlameProgressWindow(
                num_to_do=len(plan),
                title='Updating Slates',
                )

            slates_done = 1
            for item in plan:
                pyflame.print(f"Updating Slate: {item['info']['name']}", new_line=False, text_color=TextColor.GREEN)

                update_type_node(item)
                new_name = rename_slate(item)
                restamp_metadata(item, new_name)

                self.progress_window.set_progress_value(slates_done)
                self.progress_window.set_text(f'Updating Slate: [{slates_done} of {len(plan)}]')
                slates_done += 1

            pyflame.cleanup_temp_folder()

            self.progress_window.enable_done_button(True)
            self.progress_window.set_title_text('Slate Update Complete')

            pyflame.print('Slate Update Complete', text_color=TextColor.GREEN)

        def update_slates() -> None:

            changes = {}
            for token, (entry, original) in self.token_entries.items():
                if entry.text() != original:
                    changes[token] = entry.text()

            if not changes:
                PyFlameMessageWindow(
                    message='No token values were changed.',
                    type=MessageType.INFO,
                    )
                return

            plan = build_update_plan(changes)

            if not plan:
                PyFlameMessageWindow(
                    message='No selected slates carry the edited token(s) — nothing to update.',
                    type=MessageType.INFO,
                    )
                return

            if not confirm_update(plan):
                pyflame.print('Slate Update Cancelled', text_color=TextColor.RED)
                return

            self.window.hide()

            apply_updates(plan)

            self.window.close()

        #-------------------------------------

        if not gather_slates():
            return

        if protect_from_editing_check():
            return

        token_summary = build_token_summary()

        if not token_summary:
            PyFlameMessageWindow(
                message='Selected slates have no editable tokens.',
                type=MessageType.ERROR,
                )
            return

        if self.single_token:
            # DATE and CURRENT_DATE are the same field: slates created with the
            # <CURRENT_DATE> token store CURRENT_DATE, CSV-driven slates store
            # DATE - Update Date must edit whichever the selection carries.
            if self.single_token in DATE_TOKENS:
                wanted = list(DATE_TOKENS)
            else:
                wanted = [self.single_token]
            edit_tokens = [t for t in wanted if t in token_summary]
            if not edit_tokens:
                available = ', '.join(token_summary) or 'none'
                PyFlameMessageWindow(
                    message=(
                        f'None of the selected slates carry a {" or ".join(wanted)} token.\n\n'
                        f'Tokens found on the selection: {available}\n\n'
                        f'The Update Field menu list can be changed via '
                        f'Slate Maker: Update... -> Edit Update Fields.'
                        ),
                    type=MessageType.ERROR,
                    )
                return
            token_summary = {t: token_summary[t] for t in edit_tokens}

        #-------------------------------------
        # [Update Window]
        #-------------------------------------

        if self.single_token:
            window_title = f'{SCRIPT_NAME}: Update {field_display_name(self.single_token)}'
            header_text = f'Updating {"/".join(edit_tokens)} on {len(self.slates)} Slate(s)'
        else:
            window_title = f'{SCRIPT_NAME}: Update Slates'
            header_text = f'Updating {len(self.slates)} Slate(s) — edit values to change them, leave the rest as-is'

        self.window = PyFlameWindow(
            title=f'{window_title} <small>{SCRIPT_VERSION}</small>',
            grid_layout_columns=6,
            grid_layout_rows=len(token_summary) + 4,
            )

        self.updating_label = PyFlameLabel(
            text=header_text,
            )
        self.header_line = PyFlameHorizontalLine()

        self.window.grid_layout.addWidget(self.updating_label, 0, 0, 1, 6)
        self.window.grid_layout.addWidget(self.header_line, 1, 0, 1, 6)

        self.token_entries = {}
        self.token_widgets = []

        row = 2
        for token, display_value in token_summary.items():
            token_label = PyFlameLabel(text=token)
            token_entry = PyFlameEntry(text=display_value)

            self.window.grid_layout.addWidget(token_label, row, 0)
            self.window.grid_layout.addWidget(token_entry, row, 1, 1, 4)

            if is_date_token(token):
                today_button = PyFlameButton(text='Set to Today', connect=partial(set_date_to_today, token))
                self.window.grid_layout.addWidget(today_button, row, 5)
                self.token_widgets.append(today_button)

            self.token_entries[token] = (token_entry, display_value)
            self.token_widgets.extend([token_label, token_entry])
            row += 1

        self.cancel_button = PyFlameButton(text='Cancel', connect=self.window.close)
        self.update_button = PyFlameButton(
            text='Update Slates',
            connect=update_slates,
            color=Color.BLUE,
            )

        self.window.grid_layout.addWidget(self.cancel_button, row + 1, 4)
        self.window.grid_layout.addWidget(self.update_button, row + 1, 5)

#-------------------------------------
# [Rename Mode]
#-------------------------------------

class SlateRenamer():
    """
    Rename sequences (or slate clips) from slate token values.

    A slate clip's tags propagate onto its timeline segment when the slate is
    edited into a sequence, so any sequence containing a v2 slate carries that
    slate's SlateToken tags. This mode reads those tags and renames each
    selected item using a tokenized name pattern, e.g. <AD-ID>_<TITLE>.
    """

    def __init__(self, selection: Any) -> None:

        pyflame.print_title(f'{SCRIPT_NAME}: Rename from Slate {SCRIPT_VERSION}')

        self.install_verified = pyflame.verify_script_install()
        if not self.install_verified:
            return

        self.selection = selection
        self.settings = PyFlameConfig(config_values=dict(DEFAULT_CONFIG))

        if flame.get_current_tab() == 'MediaHub':
            flame.go_to('Timeline')

    def slate_renamer(self) -> None:

        if not self.install_verified:
            return

        def gather_items() -> bool:

            pyflame.print('Reading slate info from selected items...', new_line=False)

            self.items = []
            skipped = []

            for item in self.selection:
                info = find_slate_tags(item)
                if info is None:
                    skipped.append(str(item.name)[1:-1])
                else:
                    info['item'] = item
                    info['name'] = str(item.name)[1:-1]
                    self.items.append(info)

            if not self.items:
                PyFlameMessageWindow(
                    message=(
                        'None of the selected items carry slate info.\n\n'
                        'Rename from Slate works on sequences containing a slate made by '
                        'Slate Maker v2.0.0+, or on those slate clips themselves.'
                        ),
                    type=MessageType.ERROR,
                    )
                return False

            pyflame.print(f'{len(self.items)} item(s) with slate info found.', text_color=TextColor.GREEN)

            if skipped:
                sample = '\n'.join(f'• {name}' for name in skipped[:10])
                suffix = f'\n(+{len(skipped) - 10} more)' if len(skipped) > 10 else ''
                proceed = PyFlameMessageWindow(
                    message=(
                        f'{len(skipped)} selected item(s) have no slate info and will be '
                        f'skipped:\n\n{sample}{suffix}\n\n'
                        f'Continue with the {len(self.items)} item(s) that do?'
                        ),
                    type=MessageType.WARNING,
                    )
                if not proceed:
                    return False

            return True

        def build_token_menu() -> dict:

            token_order = []
            for info in self.items:
                for token in info['token_order']:
                    if token not in token_order:
                        token_order.append(token)

            return {token: f'<{token}>' for token in token_order}

        def resolve_name(pattern: str, info: dict, spaces_to_underscores: bool):
            """Resolve the name pattern against one item's slate token values.

            Returns (new_name, missing_tokens)."""

            name = pattern
            missing = []

            for token in re.findall(r'<([^<>]+)>', pattern):
                if token in info['tokens']:
                    value = re.sub(r'[\\/*?:"<>|]', '_', info['tokens'][token].strip())
                    name = name.replace(f'<{token}>', value)
                else:
                    missing.append(token)

            if spaces_to_underscores:
                name = name.replace(' ', '_')

            return name, missing

        def rename_items() -> None:

            pattern = self.pattern_entry.text()

            if not pattern:
                PyFlameMessageWindow(
                    message=(
                        'Enter a name pattern.\n\n'
                        'Use the token menu to insert tokens from the selected '
                        'slates, e.g. <ID>_<TITLE>.'
                        ),
                    type=MessageType.ERROR,
                    )
                return

            spaces_to_underscores = self.spaces_button.isChecked()

            plan = []
            notes = []

            for info in self.items:
                new_name, missing = resolve_name(pattern, info, spaces_to_underscores)
                if missing:
                    notes.append(f"• {info['name']}: slate has no {', '.join(missing)} token(s) — skipped.")
                    continue
                if new_name == info['name']:
                    continue
                plan.append((info, new_name))

            if not plan:
                message = 'Nothing to rename — all names already match the pattern.'
                if notes:
                    message += '\n\n' + '\n'.join(notes)
                PyFlameMessageWindow(message=message, type=MessageType.INFO)
                return

            # Flag resulting name collisions - AD-IDs should be unique, so
            # duplicates usually mean the wrong slate is in a sequence.
            new_names = {}
            for info, new_name in plan:
                new_names.setdefault(new_name, []).append(info['name'])
            for new_name, sources in new_names.items():
                if len(sources) > 1:
                    notes.append(f"• {len(sources)} item(s) would share the name '{new_name}'.")

            # Clean renames apply without confirming - the dialog only appears
            # when something needs attention (items skipped for missing tokens,
            # or resulting-name collisions).
            if notes:
                lines = [f'Rename {len(plan)} item(s):', '']
                for info, new_name in plan[:15]:
                    lines.append(f"• {info['name']} → {new_name}")
                if len(plan) > 15:
                    lines.append(f'(+{len(plan) - 15} more)')
                lines.extend(['', 'Notes:'] + notes)
                lines.extend(['', 'Proceed with rename?'])

                if not bool(PyFlameMessageWindow(message='\n'.join(lines), type=MessageType.WARNING)):
                    pyflame.print('Rename Cancelled', text_color=TextColor.RED)
                    return

            self.settings.save_config(
                config_values={
                    'rename_pattern': pattern,
                    'rename_spaces_to_underscores': spaces_to_underscores,
                    }
                )

            self.window.hide()

            for info, new_name in plan:
                info['item'].name = new_name
                pyflame.print(f"Renamed: {info['name']} → {new_name}", new_line=False, text_color=TextColor.GREEN)

            print('\n', end='')

            pyflame.print('Rename Complete', text_color=TextColor.GREEN)

            self.window.close()

        #-------------------------------------

        if not gather_items():
            return

        #-------------------------------------
        # [Rename Window]
        #-------------------------------------

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Rename from Slate <small>{SCRIPT_VERSION}</small>',
            grid_layout_columns=6,
            grid_layout_rows=5,
            )

        self.info_label = PyFlameLabel(
            text=f'Renaming {len(self.items)} item(s) from slate info',
            )
        self.header_line = PyFlameHorizontalLine()

        self.pattern_label = PyFlameLabel(text='Name Pattern')
        self.pattern_entry = PyFlameEntry(text=self.settings.rename_pattern)
        self.token_push_button = PyFlameTokenPushButton(token_dest=self.pattern_entry)
        self.token_push_button.add_menu_options(build_token_menu())

        self.spaces_button = PyFlamePushButton(
            text='Spaces to _',
            button_checked=self.settings.rename_spaces_to_underscores,
            tooltip='Convert spaces in resulting names to underscores',
            )

        self.cancel_button = PyFlameButton(text='Cancel', connect=self.window.close)
        self.rename_button = PyFlameButton(
            text='Rename',
            connect=rename_items,
            color=Color.BLUE,
            )

        self.window.grid_layout.addWidget(self.info_label, 0, 0, 1, 6)
        self.window.grid_layout.addWidget(self.header_line, 1, 0, 1, 6)

        self.window.grid_layout.addWidget(self.pattern_label, 2, 0)
        self.window.grid_layout.addWidget(self.pattern_entry, 2, 1, 1, 3)
        self.window.grid_layout.addWidget(self.token_push_button, 2, 4)
        self.window.grid_layout.addWidget(self.spaces_button, 2, 5)

        self.window.grid_layout.addWidget(self.cancel_button, 4, 4)
        self.window.grid_layout.addWidget(self.rename_button, 4, 5)

#-------------------------------------
# [Update Field Menu Editor]
#-------------------------------------

class UpdateFieldEditor():
    """
    Window to curate the Update <Field> menu list (update_field_tokens in
    config): one field per line, in menu order. The list is also grown
    automatically by each creation run (learn_update_fields). Saving rescans
    python hooks so the menu reflects the change without a Flame restart.
    """

    def __init__(self, selection: Any) -> None:

        pyflame.print_title(f'{SCRIPT_NAME}: Edit Update Fields {SCRIPT_VERSION}')

        self.settings = PyFlameConfig(config_values=dict(DEFAULT_CONFIG))

    def edit_update_fields(self) -> None:

        def save_fields() -> None:

            tokens = normalize_field_tokens(self.fields_text_edit.toPlainText().splitlines())

            self.settings.save_config(config_values={'update_field_tokens': tokens})
            self.window.close()

            field_list = ', '.join(tokens) if tokens else 'none - no Update <Field> menu items'
            pyflame.print(f'Update Field menu set to: {field_list}', text_color=TextColor.GREEN)
            refresh_python_hooks()

        current_tokens = normalize_field_tokens(self.settings.update_field_tokens)

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Edit Update Fields <small>{SCRIPT_VERSION}</small>',
            grid_layout_columns=6,
            grid_layout_rows=12,
            )

        self.info_label = PyFlameLabel(
            text='One field per line, in menu order - each becomes an Update <Field> menu item',
            )
        self.header_line = PyFlameHorizontalLine()

        self.fields_text_edit = PyFlameTextEdit(text='\n'.join(current_tokens))

        self.note_label = PyFlameLabel(
            text='Fields are added here automatically when slates are created',
            )

        self.cancel_button = PyFlameButton(text='Cancel', connect=self.window.close)
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_fields,
            color=Color.BLUE,
            )

        self.window.grid_layout.addWidget(self.info_label, 0, 0, 1, 6)
        self.window.grid_layout.addWidget(self.header_line, 1, 0, 1, 6)
        self.window.grid_layout.addWidget(self.fields_text_edit, 2, 0, 8, 6)
        self.window.grid_layout.addWidget(self.note_label, 10, 0, 1, 4)
        self.window.grid_layout.addWidget(self.cancel_button, 11, 4)
        self.window.grid_layout.addWidget(self.save_button, 11, 5)

#-------------------------------------

def slate_maker(selection: Any) -> None:

    script = SlateMaker(selection)
    script.slate_maker()

def slate_maker_update(selection: Any) -> None:

    script = SlateUpdater(selection)
    script.slate_updater()

def slate_maker_update_field(token: str):
    """Return a menu execute callback that opens Update Slates restricted to one token."""

    def execute(selection: Any) -> None:
        script = SlateUpdater(selection, single_token=token)
        script.slate_updater()

    return execute

def slate_maker_edit_update_fields(selection: Any) -> None:

    script = UpdateFieldEditor(selection)
    script.edit_update_fields()

def slate_maker_rename(selection: Any) -> None:

    script = SlateRenamer(selection)
    script.slate_renamer()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_clip(selection) -> bool:

    for item in selection:
        if isinstance(item, flame.PyClip) and not isinstance(item, flame.PySequence):
            return True
    return False

def scope_sequence(selection) -> bool:

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_update_field_tokens() -> list:
    """
    Tokens for the Update Field submenu, from update_field_tokens in
    config/config.json - learned from creation runs and curated via Edit
    Update Fields. Read directly (not via PyFlameConfig) - this runs at
    menu-build time, before any mode is launched. An explicitly saved empty
    list is respected: no per-field items until slates are created (or fields
    are added by hand).
    """

    tokens = DEFAULT_CONFIG['update_field_tokens']

    try:
        with open(os.path.join(SCRIPT_PATH, 'config', 'config.json')) as config_file:
            saved = json.load(config_file).get('update_field_tokens')
        if isinstance(saved, list):
            tokens = saved
    except Exception:
        pass

    return normalize_field_tokens(tokens)

def get_media_panel_custom_ui_actions():

    # Flame's contextual menu API (see custom_actions_hook.py in the Flame
    # install) only supports one level of grouping - a group 'name' is the
    # folder and 'actions' is a flat list. Nested subfolders are not possible,
    # so the update tools get their own sibling folder instead.

    scope_clip_or_sequence = lambda selection: scope_clip(selection) or scope_sequence(selection)

    main_actions = [
        {
            'name': 'Create Slates',
            'isVisible': scope_clip_or_sequence,
            'execute': slate_maker,
            'minimumVersion': '2027',
        },
        {
            'name': 'Rename from Slate',
            'isVisible': scope_clip_or_sequence,
            'execute': slate_maker_rename,
            'minimumVersion': '2027',
        },
    ]

    update_actions = [
        {
            'name': 'Update Slates',
            'isVisible': scope_clip_or_sequence,
            'execute': slate_maker_update,
            'minimumVersion': '2027',
        },
    ]

    update_actions += [
        {
            'name': f'Update {field_display_name(token)}',
            'isVisible': scope_clip_or_sequence,
            'execute': slate_maker_update_field(token),
            'minimumVersion': '2027',
        }
        for token in get_update_field_tokens()
    ]

    update_actions.append(
        {
            'name': 'Edit Update Fields',
            'isVisible': scope_clip_or_sequence,
            'execute': slate_maker_edit_update_fields,
            'minimumVersion': '2027',
        }
    )

    return [
        {
            'name': 'Uber Slate Maker...',
            'actions': main_actions,
        },
        {
            'name': 'Uber Slate Maker: Update...',
            'actions': update_actions,
        },
    ]
