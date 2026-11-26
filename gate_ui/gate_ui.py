# GateUI
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: GateUI
Script Version: 1.0.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 11.24.26
Update Date: 11.24.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Pop-up radial gate menu for Batch, based on the gate UI in Autodesk Toxik.

    The gate works with installed Python scripts and Flame hotkeys (keyboard shortcuts),
    but only ones that work from Batch.

    The gate opens at the cursor with a hotkey in Batch (Alt-` unless another is set
    in the Gate UI Setup window).

    Note: the gate opens anywhere in the Batch tab, not only over the Batch schematic.
    The gate can't tell when the cursor is outside the Batch schematic, so it also opens
    over areas where a script or hotkey on a tab might fail. Some scripts and hotkeys
    may not work unless the gate is opened over the Batch schematic. Some things won't
    work if it is opened over the Media Panel, the Batch node area, or a node's own
    schematic view such as GMask, GMask Tracer or Action. This is a limitation within
    the Flame API to be able to tell what part of the Flame UI the cursor is currently
    over.

    The gate has four or eight tabs. Each tab runs a Batch right-click menu action of
    another installed script by reference: the script's own action is called, none of
    its code is copied here. A blank tab only closes the gate. When nothing is selected
    and the action adds one node, the node is placed where the gate was opened.

    Until the tabs are set up, the top tab opens the Gate UI Setup window and the other
    three are blank. The Gate UI Setup tab can be replaced with any other action, or put
    on another tab: it is in the action list of the Gate UI Setup window under GateUI.
 
Usage:

    Press the hotkey (Alt-` by default) in Batch.

    The gate opens with the cursor at its center. Move the cursor from the center
    out through a tab to run it.

    Press Escape, or click anywhere (on the gate or off it), to close
    without running a tab.

    Setup:

        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Gate UI Setup

        Drag a Batch action from the list onto a tab of the gate picture. Dropping on
        a tab that already has an action asks before replacing it. Dragging between
        two of the four tabs adds four more tabs, one in each space, for eight in all.

        To run a Flame keyboard shortcut from a tab, drag Flame Hotkey (under Flame, the
        first group at the top of the Available Actions list) onto it and type the
        shortcut's name exactly as its Description is shown in Flame's Keyboard Shortcut
        editor. Only Flame's own built-in keyboard shortcuts can be used, not the Python
        script actions the Keyboard Shortcut editor also lists. The name is checked
        against Flame's shortcut list, and a name that isn't found adds nothing. If
        Flame's shortcut list can't be read, the name is used without checking and a
        warning is printed. Cancel adds nothing. Some shortcuts only work in certain
        places, so a valid one can still be refused when swiped.

        Drag a tab onto another tab to move what is on it. A blank tab takes it, a
        tab that has something on it swaps with it.

        Click a tab to select it, then edit its name, or clear it with Clear Tab.
        Add Extra Tabs adds the four extra tabs without dragging. Remove Extra Tabs
        takes them away again.

        To change the hotkey, click Edit Hotkey and press the new key combination
        anywhere in that window. It must include Shift, Control, Alt or Command. Clear
        Hotkey, or Backspace or Delete, empties it, and Save can't be used until a new
        one is pressed. Save in that window saves the hotkey at once and it works
        straight away, Cancel in Gate UI Setup does not undo it. In Batch that
        combination then opens the gate instead of doing what Flame used it for.

        UI Scale sets the size of the gate, from 0.1 to 2.0 (1.0 unless another is
        set). Drag the slider left or right, or click it to type a value. The text
        and the ring lines stay the same size. It is saved with Save.

URL:

    https://logik-portal.com/scripts/gate_ui

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Gate UI Setup

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 11.24.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import copy
import json
import math
import os
import sys

import flame
from PySide6 import QtCore, QtGui, QtWidgets
from lib.pyflame_lib_gate_ui import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'GateUI'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
SCRIPT_URL = 'https://logik-portal.com/scripts/gate_ui'
FONT_PATH = os.path.join(SCRIPT_PATH, 'assets', 'fonts')
CONFIG_PATH = os.path.join(SCRIPT_PATH, 'config', 'config.json')

CLICK_FILTER_NAME = 'GateUI Click Filter'

# The hotkey that opens the gate is a Qt key and its modifier keys. Alt-` unless Gate UI Setup saved another
DEFAULT_HOTKEY_KEY = QtCore.Qt.Key_QuoteLeft.value
DEFAULT_HOTKEY_MODIFIERS = QtCore.Qt.AltModifier.value

# With Shift held the ` key arrives as ~ on most keyboards, and with Alt held it can arrive as the
# grave accent dead key, so the three count as the same key
GATE_KEYS = (QtCore.Qt.Key_AsciiTilde.value, QtCore.Qt.Key_QuoteLeft.value, QtCore.Qt.Key_Dead_Grave.value)

# Modifier keys that are part of a hotkey. Anything else that comes with a key press, such as the keypad flag, is ignored
HOTKEY_MODIFIER_MASK = (QtCore.Qt.ShiftModifier | QtCore.Qt.ControlModifier | QtCore.Qt.AltModifier | QtCore.Qt.MetaModifier).value

# Highest value of a plain Qt key. Above it are the modifier bits
HOTKEY_KEY_MAX = 0x01ffffff

# Keys that can't be the hotkey: Escape closes windows and the gate, Return and Enter confirm, Tab and Backtab move between fields
HOTKEY_RESERVED_KEYS = (
    QtCore.Qt.Key_Escape.value,
    QtCore.Qt.Key_Return.value,
    QtCore.Qt.Key_Enter.value,
    QtCore.Qt.Key_Tab.value,
    QtCore.Qt.Key_Backtab.value,
    )

# Keys that are only ever held with another key, or that Qt could not name
HOTKEY_MODIFIER_KEYS = (
    QtCore.Qt.Key_Shift.value,
    QtCore.Qt.Key_Control.value,
    QtCore.Qt.Key_Alt.value,
    QtCore.Qt.Key_Meta.value,
    QtCore.Qt.Key_AltGr.value,
    QtCore.Qt.Key_CapsLock.value,
    QtCore.Qt.Key_NumLock.value,
    QtCore.Qt.Key_ScrollLock.value,
    QtCore.Qt.Key_unknown.value,
    )

# Keys that empty the hotkey in the Edit Hotkey window when pressed without a modifier key
HOTKEY_CLEAR_KEYS = (
    QtCore.Qt.Key_Backspace.value,
    QtCore.Qt.Key_Delete.value,
    )

# First and last of Qt's dead keys (accents that wait for the next key, such as the grave accent)
DEAD_KEY_FIRST = QtCore.Qt.Key_Dead_Grave.value
DEAD_KEY_LAST = QtCore.Qt.Key_Dead_Longsolidusoverlay.value

# Dead keys and the key they are on, used outside macOS
DEAD_KEY_BASE_KEYS = {
    QtCore.Qt.Key_Dead_Grave.value: QtCore.Qt.Key_QuoteLeft.value,
    QtCore.Qt.Key_Dead_Acute.value: QtCore.Qt.Key_Apostrophe.value,
    QtCore.Qt.Key_Dead_Circumflex.value: QtCore.Qt.Key_AsciiCircum.value,
    QtCore.Qt.Key_Dead_Diaeresis.value: QtCore.Qt.Key_QuoteDbl.value,
    }

# macOS virtual key codes of a US keyboard and their Qt keys. On macOS Alt (Option) turns many keys into
# dead keys or other characters, so a key Qt can't name is found by its place on the keyboard instead
MAC_VIRTUAL_KEYS = {
    0: QtCore.Qt.Key_A.value,
    1: QtCore.Qt.Key_S.value,
    2: QtCore.Qt.Key_D.value,
    3: QtCore.Qt.Key_F.value,
    4: QtCore.Qt.Key_H.value,
    5: QtCore.Qt.Key_G.value,
    6: QtCore.Qt.Key_Z.value,
    7: QtCore.Qt.Key_X.value,
    8: QtCore.Qt.Key_C.value,
    9: QtCore.Qt.Key_V.value,
    11: QtCore.Qt.Key_B.value,
    12: QtCore.Qt.Key_Q.value,
    13: QtCore.Qt.Key_W.value,
    14: QtCore.Qt.Key_E.value,
    15: QtCore.Qt.Key_R.value,
    16: QtCore.Qt.Key_Y.value,
    17: QtCore.Qt.Key_T.value,
    18: QtCore.Qt.Key_1.value,
    19: QtCore.Qt.Key_2.value,
    20: QtCore.Qt.Key_3.value,
    21: QtCore.Qt.Key_4.value,
    22: QtCore.Qt.Key_6.value,
    23: QtCore.Qt.Key_5.value,
    24: QtCore.Qt.Key_Equal.value,
    25: QtCore.Qt.Key_9.value,
    26: QtCore.Qt.Key_7.value,
    27: QtCore.Qt.Key_Minus.value,
    28: QtCore.Qt.Key_8.value,
    29: QtCore.Qt.Key_0.value,
    30: QtCore.Qt.Key_BracketRight.value,
    31: QtCore.Qt.Key_O.value,
    32: QtCore.Qt.Key_U.value,
    33: QtCore.Qt.Key_BracketLeft.value,
    34: QtCore.Qt.Key_I.value,
    35: QtCore.Qt.Key_P.value,
    37: QtCore.Qt.Key_L.value,
    38: QtCore.Qt.Key_J.value,
    39: QtCore.Qt.Key_Apostrophe.value,
    40: QtCore.Qt.Key_K.value,
    41: QtCore.Qt.Key_Semicolon.value,
    42: QtCore.Qt.Key_Backslash.value,
    43: QtCore.Qt.Key_Comma.value,
    44: QtCore.Qt.Key_Slash.value,
    45: QtCore.Qt.Key_N.value,
    46: QtCore.Qt.Key_M.value,
    47: QtCore.Qt.Key_Period.value,
    50: QtCore.Qt.Key_QuoteLeft.value,
    }

# Names of the modifier keys in the order they are shown. On macOS Qt calls the Command key Control and the Control key Meta
if sys.platform == 'darwin':
    HOTKEY_MODIFIER_NAMES = (
        (QtCore.Qt.MetaModifier.value, 'Ctrl'),
        (QtCore.Qt.AltModifier.value, 'Alt'),
        (QtCore.Qt.ShiftModifier.value, 'Shift'),
        (QtCore.Qt.ControlModifier.value, 'Cmd'),
        )
else:
    HOTKEY_MODIFIER_NAMES = (
        (QtCore.Qt.ControlModifier.value, 'Ctrl'),
        (QtCore.Qt.AltModifier.value, 'Alt'),
        (QtCore.Qt.ShiftModifier.value, 'Shift'),
        (QtCore.Qt.MetaModifier.value, 'Meta'),
        )

# Object name of the Gate UI Setup window, so an open one can be found even after Flame reloads the script
SETUP_WINDOW_NAME = 'Gate UI Setup Window'

# Script name PyFlameConfig writes into the config file: the script folder name in title case, as PyFlameLib makes it
CONFIG_SCRIPT_NAME = os.path.basename(SCRIPT_PATH).title().replace('_', ' ')

# The gate has this many sections (tabs), or twice as many once the extra tabs are added
SECTION_COUNT = 4

# Sections the gate has until Gate UI Setup saves others, clockwise from the top. A section has a
# 'label' (text shown on its tab) and the Batch right-click action it runs: 'script' (module name of
# the installed script), 'group' (names of the menu groups the action is in, None for a group with
# no name) and 'action' (action name). A blank section has no label and no script. The top tab
# opens Gate UI Setup and the other three are blank until the user fills them in Gate UI Setup
DEFAULT_SECTIONS = [
    {
        'label': 'Gate UI Setup',
        'script': 'gate_ui',
        'group': ['GateUI'],
        'action': 'Gate UI Setup',
        },
    {
        'label': '',
        'script': '',
        'group': [],
        'action': '',
        },
    {
        'label': '',
        'script': '',
        'group': [],
        'action': '',
        },
    {
        'label': '',
        'script': '',
        'group': [],
        'action': '',
        },
    ]

# GateUI's own action that opens Gate UI Setup. It is not a Batch menu action, the gate runs it itself
SETUP_ACTION = {
    'script': 'gate_ui',
    'group': ['GateUI'],
    'action': 'Gate UI Setup',
    }

# A tab can run a Flame keyboard shortcut. Its action is the shortcut's Description in Flame's Keyboard
# Shortcut editor, run with flame.execute_shortcut. Tabs are told apart by this script value only, so tabs
# saved with the older 'Flame Shortcuts' group still run
FLAME_SHORTCUT_SCRIPT = 'flame_shortcut'
FLAME_SHORTCUT_GROUP = ['Flame Hotkey']

# Flame Hotkey item in Gate UI Setup's action list, under the Flame group, which is always the first group. It is
# only a template: dropping it on a tab asks for the shortcut's name, and the tab gets a Flame shortcut action. It
# is never put on a tab as is
FLAME_HOTKEY_ACTION = {
    'script': 'gate_ui_flame_hotkey',
    'group': ['Flame'],
    'action': 'Flame Hotkey',
    }

# Folder of Flame's keyboard shortcut presets: one folder per Flame version, holding a folder per shortcut profile
FLAME_SHORTCUTS_PATH = '/opt/Autodesk/presets'

# Heading in Gate UI Setup for actions whose menu group has no name
NO_GROUP_NAME = 'Other'

# Sizes in pixels, angles in degrees
WIDGET_SIZE = 360
RING_RADIUS = 62
RING_WIDTH = 2
RING_GAP_ANGLE = 4
TICK_LENGTH = 8
HOVER_START_RADIUS = 8
TRIGGER_RADIUS = 85
GLOW_RADIUS = 172
GLOW_GAP_ANGLE = 14
LABEL_RADIUS = 114
LABEL_RING_SPACE = 13
LABEL_MAX_LINES = 3

# The pop-up gate is drawn this many times the sizes above when UI Scale in Gate UI Setup is 1.0. Label font
# sizes, label line widths and the width of the ring lines are not scaled. The picture in Gate UI Setup is not
# scaled either
GATE_SCALE = 1.5

# UI Scale of the pop-up gate, set in Gate UI Setup: the gate is GATE_SCALE times this
DEFAULT_UI_SCALE = 1.0
UI_SCALE_MIN = 0.1
UI_SCALE_MAX = 2.0

# Label font size and the widest a label line can be, for a gate with the extra tabs and without
LABEL_FONT_SIZE = 14
LABEL_WIDTH = 100
LABEL_FONT_SIZE_EXTRA = 12
LABEL_WIDTH_EXTRA = 84

# Degrees of each space between two tabs in Gate UI Setup where a dragged action adds the extra tabs
NEW_TAB_ZONE_ANGLE = 30

# Kind of data in a drag of a tab in Gate UI Setup. The data is the index of the dragged tab
TAB_MIME_TYPE = 'application/x-gate-ui-tab'

# Milliseconds between cursor checks while the gate is open
CURSOR_POLL_INTERVAL = 15

# Milliseconds after a tablet pen comes into range in which a cursor move counts as a jump to the pen
PEN_ARRIVAL_TIME = 500

# Colors
RING_COLOR = QtGui.QColor(0, 110, 175)
CENTER_COLOR = QtGui.QColor(30, 30, 30, 150)
TEXT_COLOR = QtGui.QColor(215, 215, 215)
HIT_COLOR = QtGui.QColor(0, 0, 0, 1)
SELECTED_COLOR = QtGui.QColor(224, 173, 28)
GLOW_ALPHA = 48
GLOW_HOVER_ALPHA = 83

# Dark backing under each tab's glow so the labels stay readable over busy schematics
TAB_BACKING_ALPHA = 153

# ==============================================================================
# [Main Script]
# ==============================================================================

def load_config() -> PyFlameConfig:
    """
    Load Config
    ===========

    Load the script's config values from the config file.

    Returns
    -------
        settings (PyFlameConfig): PyFlameConfig object with the loaded config values.
    """

    settings = PyFlameConfig(
        config_values={
            'sections': copy.deepcopy(DEFAULT_SECTIONS),
            'hotkey_key': DEFAULT_HOTKEY_KEY,
            'hotkey_modifiers': DEFAULT_HOTKEY_MODIFIERS,
            'ui_scale': DEFAULT_UI_SCALE,
            },
        config_path=CONFIG_PATH,
        )

    return settings

def clean_ui_scale(ui_scale) -> float:
    """
    Clean UI Scale
    ==============

    Check a UI Scale value, such as one read from the config file. A value that isn't a number gives
    the default, and a number outside UI_SCALE_MIN to UI_SCALE_MAX is brought into that range.

    Args
    ----
        ui_scale (any): UI Scale value to check.

    Returns
    -------
        ui_scale (float): UI Scale from UI_SCALE_MIN to UI_SCALE_MAX, to two decimal places.
    """

    if isinstance(ui_scale, bool) or not isinstance(ui_scale, (int, float)) or not math.isfinite(ui_scale):
        return DEFAULT_UI_SCALE

    return round(min(max(float(ui_scale), UI_SCALE_MIN), UI_SCALE_MAX), 2)

def load_ui_scale() -> float:
    """
    Load UI Scale
    =============

    Read the gate's UI Scale from the config file. Nothing is created or changed, and a config that is
    missing or can't be read gives the default.

    Returns
    -------
        ui_scale (float): UI Scale from UI_SCALE_MIN to UI_SCALE_MAX.
    """

    ui_scale = None

    try:
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as config_file:
                ui_scale = json.load(config_file).get('ui_scale')
    except Exception:
        ui_scale = None

    return clean_ui_scale(ui_scale)

def clean_hotkey(key, modifiers) -> tuple:
    """
    Clean Hotkey
    ============

    Get a usable hotkey from saved values. A missing or wrong key or modifiers gives the
    default hotkey, so a damaged config can never leave the gate without one. So does a
    key with no modifier key: it would be taken from Flame on every press in Batch, even
    while typing in one of Flame's own fields.

    Args
    ----
        key (int):
            Qt key as loaded from the config.

        modifiers (int):
            Qt keyboard modifiers as loaded from the config.

    Returns
    -------
        hotkey (tuple): The key (int) and its modifiers (int, Shift, Control, Alt and Meta only).
    """

    for value in (key, modifiers):
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            return DEFAULT_HOTKEY_KEY, DEFAULT_HOTKEY_MODIFIERS

    if key in HOTKEY_RESERVED_KEYS or key in HOTKEY_MODIFIER_KEYS:
        return DEFAULT_HOTKEY_KEY, DEFAULT_HOTKEY_MODIFIERS

    # Only a plain key Qt has a name for: not 0, and nothing with modifier bits or beyond Qt's key values
    if not hotkey_key_name(key):
        return DEFAULT_HOTKEY_KEY, DEFAULT_HOTKEY_MODIFIERS

    # At least one of Shift, Control, Alt or Meta must be held with the key
    if not modifiers & HOTKEY_MODIFIER_MASK:
        return DEFAULT_HOTKEY_KEY, DEFAULT_HOTKEY_MODIFIERS

    return key, modifiers & HOTKEY_MODIFIER_MASK

def hotkey_key_name(key: int) -> str:
    """
    Hotkey Key Name
    ===============

    Get the name of a Qt key to show the user. Never raises.

    Args
    ----
        key (int): Qt key.

    Returns
    -------
        name (str): Name of the key, such as G, Space or F5. Empty if the value is not a plain Qt key.
    """

    if not isinstance(key, int) or isinstance(key, bool) or not 0 < key <= HOTKEY_KEY_MAX:
        return ''

    # Show the key that is pressed, not the character Shift turns it into
    if key in GATE_KEYS:
        return '`'

    try:
        name = QtGui.QKeySequence(key).toString(QtGui.QKeySequence.PortableText).strip()
    except Exception:
        return ''

    # A value Qt has no key for comes back as a character that can't be shown
    if not name.isprintable():
        return ''

    return name

def hotkey_text(key: int, modifiers: int) -> str:
    """
    Hotkey Text
    ===========

    Get a hotkey as text to show the user, such as Shift+` or Ctrl+Space.

    Args
    ----
        key (int):
            Qt key.

        modifiers (int):
            Qt keyboard modifiers.

    Returns
    -------
        text (str): Names of the modifier keys and the key, joined with +. Never raises: values that are not a hotkey give Unknown Key.
    """

    try:
        names = [name for modifier, name in HOTKEY_MODIFIER_NAMES if modifiers & modifier]
        names.append(hotkey_key_name(key) or 'Unknown Key')

        return '+'.join(names)

    except Exception:
        return 'Unknown Key'

def hotkey_event_key(event) -> int:
    """
    Hotkey Event Key
    ================

    Get the Qt key a key press stands for, as a hotkey is saved. ` and ~ are the same
    key. On macOS a key that Alt turned into a dead key or another character is found by
    its place on the keyboard.

    Args
    ----
        event (QKeyEvent): Qt key event.

    Returns
    -------
        key (int): Qt key. 0 if it can't be told, or if the key is a modifier key.
    """

    key = event.key()

    # Keep ` as the key when Shift turned it into ~ or Alt into the grave accent
    if key in GATE_KEYS:
        return DEFAULT_HOTKEY_KEY

    # A modifier key is only ever held with the key of a hotkey
    if key in HOTKEY_MODIFIER_KEYS and key != QtCore.Qt.Key_unknown.value:
        return 0

    # Printable ASCII, or a special key such as Space, F5 or Backspace
    if 0x20 <= key <= 0x7e:
        return key
    if 0x01000000 <= key < QtCore.Qt.Key_unknown.value and not DEAD_KEY_FIRST <= key <= DEAD_KEY_LAST:
        return key

    # No usable key: a dead key, an unknown key or another character, find the key by its place on the keyboard
    if sys.platform == 'darwin':
        return MAC_VIRTUAL_KEYS.get(event.nativeVirtualKey(), 0)

    key = DEAD_KEY_BASE_KEYS.get(key, key)
    if key == QtCore.Qt.Key_unknown.value or not hotkey_key_name(key):
        return 0

    return key

def blank_section() -> dict:
    """
    Blank Section
    =============

    Get a section with no label and no action. Its tab is drawn, and swiping into it only
    closes the gate.

    Returns
    -------
        section (dict): Blank section.
    """

    return {
        'label': '',
        'script': '',
        'group': [],
        'action': '',
        }

def clean_sections(sections) -> list:
    """
    Clean Sections
    ==============

    Get a usable list of sections from a saved value. Anything that is not a list of four
    or eight sections gives the default sections, and missing or wrong values in a section
    are replaced with blank ones, so a damaged config can never break the gate.

    Args
    ----
        sections (list): Sections as loaded from the config.

    Returns
    -------
        sections (list): New list of four or eight section dicts.
    """

    if not isinstance(sections, list) or len(sections) not in (SECTION_COUNT, SECTION_COUNT * 2):
        return copy.deepcopy(DEFAULT_SECTIONS)

    cleaned_sections = []

    for section in sections:
        cleaned_section = blank_section()

        if isinstance(section, dict):
            for key in ('label', 'script', 'action'):
                if isinstance(section.get(key), str):
                    cleaned_section[key] = section[key]
            if isinstance(section.get('group'), list):
                cleaned_section['group'] = list(section['group'])

        cleaned_sections.append(cleaned_section)

    return cleaned_sections

def load_sections() -> list:
    """
    Load Sections
    =============

    Load the gate's sections from the config file. If the config can't be read the default
    sections are used.

    Returns
    -------
        sections (list): List of four or eight section dicts.
    """

    try:
        sections = load_config().sections
    except Exception as e:
        pyflame.print(f'Config could not be loaded, using the default tabs: {e}', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)
        sections = None

    return clean_sections(sections)

def add_extra_sections(sections: list) -> list:
    """
    Add Extra Sections
    ==================

    Get eight sections from four by adding a blank section after each one, so the four
    keep their places and a new tab sits in each space between them.

    Args
    ----
        sections (list): The four sections.

    Returns
    -------
        sections (list): New list of eight sections. The extra ones have the odd indexes.
    """

    extra_sections = []

    for section in sections:
        extra_sections.append(section)
        extra_sections.append(blank_section())

    return extra_sections

def remove_extra_sections(sections: list) -> list:
    """
    Remove Extra Sections
    =====================

    Get the four original sections from eight by dropping the four extra ones.

    Args
    ----
        sections (list): The eight sections.

    Returns
    -------
        sections (list): New list of the four sections with even indexes.
    """

    return sections[::2]

def group_name(group: list) -> str:
    """
    Group Name
    ==========

    Get the name of an action's menu group as shown to the user.

    Args
    ----
        group (list): Names of the menu groups the action is in. None for a group with no name.

    Returns
    -------
        name (str): Group names joined with ' / '. A group with no name is shown as Other.
    """

    return ' / '.join(name if isinstance(name, str) else NO_GROUP_NAME for name in group) or NO_GROUP_NAME

def section_name(section: dict) -> str:
    """
    Section Name
    ============

    Get the name of a section for messages: its label, followed by its menu group and
    action when it has an action and the label is not the action's own name.

    Args
    ----
        section (dict): Section.

    Returns
    -------
        name (str): Name of the section on one line.
    """

    label = ' '.join(section['label'].split())
    action_name = section['action']

    if not label:
        return action_name

    if not section['script'] or label == action_name:
        return label

    return f'{label} ({group_name(section["group"])} / {action_name})'

def get_script_actions(script) -> list:
    """
    Get Script Actions
    ==================

    Get the Batch right-click menu actions of an installed script, by calling the same
    hook Flame calls to build the menu.

    Args
    ----
        script (module): Script module with a get_batch_custom_ui_actions function.

    Returns
    -------
        actions (list): A (group, action) tuple for each action. group is the list of menu group names the action is in (None for a group with no name), action is the script's own action dict.
    """

    def add_actions(items, group: list) -> None:
        """
        Add Actions
        ===========

        Add the actions in a list of menu items, going into every group in it.

        Args
        ----
            items (list):
                Menu items: groups and actions.

            group (list):
                Names of the menu groups the items are in.
        """

        for item in items or []:
            if not isinstance(item, dict):
                continue

            if 'actions' in item:
                add_actions(item['actions'], group + list(item.get('hierarchy') or []) + [item.get('name')])
            elif 'execute' in item:
                actions.append((group, item))

    actions = []

    add_actions(script.get_batch_custom_ui_actions(), [])

    return actions

def find_batch_actions() -> list:
    """
    Find Batch Actions
    ==================

    Find every Batch right-click menu action of the installed scripts. Flame loads each
    hook script as a top-level module, so the loaded modules in the Flame Python hook
    folder are asked for their actions. A script whose hook fails is left out.

    Returns
    -------
        actions (list): A dict for each action with 'script' (module name), 'group' (menu group names) and 'action' (action name). GateUI's own action that opens Gate UI Setup and the Flame Hotkey item are included.
    """

    hook_path = os.path.realpath(os.path.dirname(SCRIPT_PATH)) + os.sep

    # GateUI's own action, so a tab can open Gate UI Setup, and the Flame Hotkey item, so a tab can run a Flame shortcut
    actions = [copy.deepcopy(SETUP_ACTION), copy.deepcopy(FLAME_HOTKEY_ACTION)]

    for script_name, script in sorted(sys.modules.items()):
        try:
            if script_name == __name__:
                continue

            # Only scripts in the hook folder this script is in. Checked first, so no other module is asked for anything
            script_file = script.__dict__.get('__file__')
            if not isinstance(script_file, str) or not os.path.realpath(script_file).startswith(hook_path):
                continue

            if not callable(getattr(script, 'get_batch_custom_ui_actions', None)):
                continue

            for group, action in get_script_actions(script):
                if isinstance(action.get('name'), str):
                    actions.append(
                        {
                            'script': script_name,
                            'group': group,
                            'action': action['name'],
                            }
                        )
        except Exception:
            continue

    return actions

def flame_shortcut_names() -> set:
    """
    Flame Shortcut Names
    ====================

    Get the names of Flame's keyboard shortcuts: the Description of every shortcut in the
    shortcut preset files of every shortcut profile of this Flame version. Files that
    can't be read are skipped.

    Returns
    -------
        shortcut_names (set): Shortcut names. Empty if no shortcut file could be read.
    """

    shortcut_names = set()

    try:
        shortcuts_path = os.path.join(FLAME_SHORTCUTS_PATH, str(flame.get_version()), 'shortcuts')
        profiles = sorted(os.listdir(shortcuts_path))
    except Exception:
        return shortcut_names

    for profile in profiles:
        profile_path = os.path.join(shortcuts_path, profile)

        try:
            file_names = sorted(os.listdir(profile_path))
        except Exception:
            continue

        for file_name in file_names:
            if not (file_name.startswith('shortcuts.') and file_name.endswith('.json')):
                continue

            try:
                with open(os.path.join(profile_path, file_name)) as shortcut_file:
                    shortcuts = json.load(shortcut_file)

                # Each file holds one list of shortcuts under a single key
                for shortcut_list in shortcuts.values():
                    for shortcut in shortcut_list:
                        if isinstance(shortcut, dict) and isinstance(shortcut.get('Description'), str):
                            shortcut_names.add(shortcut['Description'])
            except Exception:
                continue

    return shortcut_names

def load_gate_font() -> str:
    """
    Load Gate Font
    ==============

    Load the Montserrat fonts from the script's assets folder.

    Returns
    -------
        font_family (str): Family name of Montserrat Regular. Empty if the font could not be loaded.
    """

    font_family = ''

    for font_file in ('Montserrat-Regular.ttf', 'Montserrat-Light.ttf', 'Montserrat-Thin.ttf'):
        font_id = QtGui.QFontDatabase.addApplicationFont(os.path.join(FONT_PATH, font_file))
        font_families = QtGui.QFontDatabase.applicationFontFamilies(font_id)

        # Use the family name of the first font that loads (Regular)
        if font_families and not font_family:
            font_family = font_families[0]

    return font_family

def wrap_label(label: str, font_metrics, max_width: int) -> list:
    """
    Wrap Label
    ==========

    Split a label into lines that fit its tab. A newline in the label always starts a new
    line. A word too wide for a line, and text left over after the last line, is cut short
    with an ellipsis. A line that fits is never changed.

    Args
    ----
        label (str):
            Label text.

        font_metrics (QFontMetrics):
            Metrics of the label font.

        max_width (int):
            Widest a line can be, in pixels.

    Returns
    -------
        lines (list): Lines of the label. Empty for a blank label.
    """

    lines = []

    for label_line in label.split('\n'):
        line = ''

        for word in label_line.split():
            longer_line = f'{line} {word}' if line else word

            if not line or font_metrics.horizontalAdvance(longer_line) <= max_width:
                line = longer_line
            else:
                lines.append(line)
                line = word

        if line:
            lines.append(line)

    # Mark text that doesn't fit in the last line as cut off
    if len(lines) > LABEL_MAX_LINES:
        lines = lines[:LABEL_MAX_LINES]
        lines[-1] = f'{lines[-1]}...'

    # Cut short only the lines that are too wide, measured the same way the lines were filled
    for index, line in enumerate(lines):
        if font_metrics.horizontalAdvance(line) > max_width:
            lines[index] = font_metrics.elidedText(line, QtCore.Qt.ElideRight, max_width)

    return lines

def gate_labels(sections: list, font_family: str, scale: float=1.0) -> tuple:
    """
    Gate Labels
    ===========

    Work out the label of each section: its font, its wrapped lines and where its text goes.
    Used by paint_gate to draw the labels and by GateUI to size its window, so both always agree.

    Args
    ----
        sections (list):
            Section dicts. The first is centered at the top and the rest go clockwise.

        font_family (str):
            Family name of the label font.

        scale (float):
            Size of the gate: 1.0 is WIDGET_SIZE square. The label font and the label line
            width stay the same at any scale.

    Returns
    -------
        label_font (QFont): Font of the labels.

        label_width (int): Widest a label line can be, in pixels.

        labels (list): One (lines, text_rect) per section. text_rect is the space the text takes,
            relative to the gate's center. A blank section has no lines and an empty rect.
    """

    ring_radius = RING_RADIUS * scale
    label_radius = LABEL_RADIUS * scale
    label_ring_space = LABEL_RING_SPACE * scale

    # Smaller labels on narrower lines when the gate has the extra tabs
    extra_sections = len(sections) > SECTION_COUNT
    label_font = QtGui.QFont(font_family)
    label_font.setPixelSize(LABEL_FONT_SIZE_EXTRA if extra_sections else LABEL_FONT_SIZE)
    label_width = LABEL_WIDTH_EXTRA if extra_sections else LABEL_WIDTH
    font_metrics = QtGui.QFontMetrics(label_font)

    section_angle = 360 / len(sections)
    labels = []

    for index, section in enumerate(sections):

        # Label wrapped to fit the tab. A blank section has no label
        lines = wrap_label(section['label'], font_metrics, label_width)
        if not lines:
            labels.append((lines, QtCore.QRectF()))
            continue

        # Qt angles start at 3 o'clock and go counter-clockwise, sections start at the top and go clockwise
        middle_radians = math.radians(90 - index * section_angle)
        direction = QtCore.QPointF(math.cos(middle_radians), -math.sin(middle_radians))

        text_width = max(font_metrics.horizontalAdvance(line) for line in lines)
        text_height = font_metrics.lineSpacing() * len(lines)

        # Label centered on the section's middle angle, moved out when it would otherwise reach the ring's tick
        text_reach = abs(direction.x()) * text_width / 2 + abs(direction.y()) * text_height / 2
        label_center = direction * max(label_radius, ring_radius + label_ring_space + text_reach)
        text_rect = QtCore.QRectF(label_center.x() - text_width / 2, label_center.y() - text_height / 2, text_width, text_height)

        labels.append((lines, text_rect))

    return label_font, label_width, labels

def paint_gate(painter, sections: list, font_family: str, hover_section=None, selected_section=None, scale: float=1.0) -> None:
    """
    Paint Gate
    ==========

    Draw the gate: center disc, then a dark backing, glow, ring arc, tick and label for each section.
    Nothing is drawn behind them. The gate is drawn WIDGET_SIZE * scale square from the
    painter's origin; scale the painter to draw everything, text and lines included, another size.
    Labels can reach past that square at small scales (see gate_labels).

    Used by both the pop-up gate and the Gate UI Setup window, so the picture in Setup is
    always what the gate looks like.

    Args
    ----
        painter (QPainter):
            Painter to draw with.

        sections (list):
            Section dicts. The first is centered at the top and the rest go clockwise.

        font_family (str):
            Family name of the label font.

        hover_section (int | None):
            Index of the section to draw with a brighter glow.

        selected_section (int | None):
            Index of the section to draw as selected.

        scale (float):
            Size of the gate: 1.0 is WIDGET_SIZE square. The label font, the label line
            width and the width of the ring lines stay the same at any scale.
    """

    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setRenderHint(QtGui.QPainter.TextAntialiasing)

    # Sizes of the gate at this scale
    ring_radius = RING_RADIUS * scale
    glow_radius = GLOW_RADIUS * scale
    tick_length = TICK_LENGTH * scale

    center = QtCore.QPointF(WIDGET_SIZE * scale / 2, WIDGET_SIZE * scale / 2)
    ring_rect = QtCore.QRectF(center.x() - ring_radius, center.y() - ring_radius, ring_radius * 2, ring_radius * 2)
    glow_rect = QtCore.QRectF(center.x() - glow_radius, center.y() - glow_radius, glow_radius * 2, glow_radius * 2)

    ring_pen = QtGui.QPen(RING_COLOR, RING_WIDTH)
    ring_pen.setCapStyle(QtCore.Qt.FlatCap)
    selected_pen = QtGui.QPen(SELECTED_COLOR, RING_WIDTH)
    selected_pen.setCapStyle(QtCore.Qt.FlatCap)

    label_font, label_width, labels = gate_labels(sections, font_family, scale)

    # Dark disc inside the ring
    painter.setPen(QtCore.Qt.NoPen)
    painter.setBrush(CENTER_COLOR)
    painter.drawEllipse(ring_rect)

    section_angle = 360 / len(sections)

    # Glow wedge of each section from the ring out to the glow radius
    glow_paths = []
    for index in range(len(sections)):
        glow_start = 90 - index * section_angle - section_angle / 2 + GLOW_GAP_ANGLE / 2
        glow_sweep = section_angle - GLOW_GAP_ANGLE

        glow_path = QtGui.QPainterPath()
        glow_path.arcMoveTo(glow_rect, glow_start)
        glow_path.arcTo(glow_rect, glow_start, glow_sweep)
        glow_path.arcTo(ring_rect, glow_start + glow_sweep, -glow_sweep)
        glow_path.closeSubpath()
        glow_paths.append(glow_path)

    # Dark backing under every wedge, fading like the glow, so whatever is behind the gate shows through less.
    # Drawn for all sections first so it never covers a label that reaches into the next tab
    backing_color = QtGui.QColor(CENTER_COLOR.red(), CENTER_COLOR.green(), CENTER_COLOR.blue(), TAB_BACKING_ALPHA)
    backing_gradient = QtGui.QRadialGradient(center, glow_radius)
    backing_gradient.setColorAt(0, backing_color)
    backing_gradient.setColorAt(ring_radius / glow_radius, backing_color)
    backing_gradient.setColorAt(1, QtGui.QColor(CENTER_COLOR.red(), CENTER_COLOR.green(), CENTER_COLOR.blue(), 0))

    painter.setPen(QtCore.Qt.NoPen)
    painter.setBrush(backing_gradient)
    for glow_path in glow_paths:
        painter.drawPath(glow_path)

    for index, section in enumerate(sections):

        # Qt angles start at 3 o'clock and go counter-clockwise, sections start at the top and go clockwise
        middle_angle = 90 - index * section_angle
        middle_radians = math.radians(middle_angle)
        direction = QtCore.QPointF(math.cos(middle_radians), -math.sin(middle_radians))

        # White glow on top of the backing, fading to nothing at the outer edge
        glow_path = glow_paths[index]
        glow_alpha = GLOW_HOVER_ALPHA if index == hover_section else GLOW_ALPHA
        glow_gradient = QtGui.QRadialGradient(center, glow_radius)
        glow_gradient.setColorAt(0, QtGui.QColor(255, 255, 255, glow_alpha))
        glow_gradient.setColorAt(ring_radius / glow_radius, QtGui.QColor(255, 255, 255, glow_alpha))
        glow_gradient.setColorAt(1, QtGui.QColor(255, 255, 255, 0))

        painter.setPen(QtCore.Qt.NoPen)
        painter.setBrush(glow_gradient)
        painter.drawPath(glow_path)

        # Ring arc with a small gap between it and the next section's arc
        arc_start = middle_angle - section_angle / 2 + RING_GAP_ANGLE / 2
        arc_sweep = section_angle - RING_GAP_ANGLE

        arc_path = QtGui.QPainterPath()
        arc_path.arcMoveTo(ring_rect, arc_start)
        arc_path.arcTo(ring_rect, arc_start, arc_sweep)

        painter.setPen(selected_pen if index == selected_section else ring_pen)
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawPath(arc_path)

        # Tick pointing outward from the middle of the arc
        painter.drawLine(center + direction * ring_radius, center + direction * (ring_radius + RING_WIDTH / 2 + tick_length))

        # Label placed by gate_labels. A blank section has no label
        lines, text_rect = labels[index]
        if not lines:
            continue

        label_center = center + text_rect.center()
        text_height = text_rect.height()
        label_rect = QtCore.QRectF(label_center.x() - label_width, label_center.y() - text_height, label_width * 2, text_height * 2)

        painter.setPen(TEXT_COLOR)
        painter.setFont(label_font)
        painter.drawText(label_rect, QtCore.Qt.AlignCenter, '\n'.join(lines))

class GateUI(QtWidgets.QWidget):

    def __init__(self, sections: list, ui_scale: float=DEFAULT_UI_SCALE) -> None:
        """
        Init
        ====

        Build the gate window. The window is created hidden; call show_at_cursor to show it.

        Args
        ----
            sections (list):
                Section dicts as returned by load_sections. The first is centered at the
                top and the rest go clockwise.

            ui_scale (float):
                UI Scale set in Gate UI Setup. The gate is GATE_SCALE times this.
        """

        super().__init__()

        self.sections = sections
        self.scale = GATE_SCALE * ui_scale
        self.hover_section = None
        self.triggered = False
        self.open_position = QtCore.QPoint()
        self.last_position = QtCore.QPoint()
        self.pen_arrived = False
        self.pen_timer = QtCore.QElapsedTimer()

        # Batch schematic position of the cursor when the gate opened. Empty when there is none
        self.schematic_position = ()

        # Frameless see-through window that floats above Flame
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
            | QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.NoDropShadowWindowHint
            | QtCore.Qt.WindowDoesNotAcceptFocus
            )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # Never take keyboard focus, so Flame still has it when the gate closes
        self.setAttribute(QtCore.Qt.WA_ShowWithoutActivating)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Label font
        self.font_family = load_gate_font()

        # Window is the gate's size, or bigger when the labels reach past it (their font doesn't scale).
        # A few pixels spare for letters that reach past their advance width
        label_reach = 0
        for lines, text_rect in gate_labels(self.sections, self.font_family, self.scale)[2]:
            if lines:
                label_reach = max(label_reach, abs(text_rect.left()), abs(text_rect.right()), abs(text_rect.top()), abs(text_rect.bottom()))
        self.gate_size = max(1, round(WIDGET_SIZE * self.scale), math.ceil(label_reach * 2) + 4)
        self.setFixedSize(self.gate_size, self.gate_size)

        # Create the native window now, otherwise the first showing opens 20 pixels too high on macOS
        self.winId()

        # Follow the cursor with a timer while the gate is open. Mouse move events can't be relied on,
        # the gate doesn't always get them when it is opened from a click in Flame
        self.cursor_timer = QtCore.QTimer(self)
        self.cursor_timer.setInterval(CURSOR_POLL_INTERVAL)
        self.cursor_timer.timeout.connect(self.track_cursor)

    # ==============================================================================

    def section_at_angle(self, x_offset: float, y_offset: float) -> int:
        """
        Section At Angle
        ================

        Get the section a point lies in by its angle around the center. Every angle belongs
        to the nearest section, so the gaps between sections are not dead zones.

        Args
        ----
            x_offset (float):
                Horizontal distance of the point from the center of the window.

            y_offset (float):
                Vertical distance of the point from the center of the window.

        Returns
        -------
            section_index (int): Index of the section.
        """

        # Angle clockwise from the top, shifted half a section so section 0 is centered on the top
        section_angle = 360 / len(self.sections)
        angle = math.degrees(math.atan2(x_offset, -y_offset)) % 360

        return int(((angle + section_angle / 2) % 360) // section_angle)

    def show_at_cursor(self) -> None:
        """
        Show At Cursor
        ==============

        Show the gate centered on the cursor, without taking keyboard focus from Flame.
        Remember where the cursor is in the Batch schematic, so a node a tab adds can be
        placed there instead of where the swipe ended.
        """

        self.hover_section = None
        self.triggered = False

        # Batch gives the cursor's schematic position as (x, y), and () outside the Batch tab
        try:
            schematic_position = tuple(flame.batch.cursor_position)
        except Exception:
            schematic_position = ()
        self.schematic_position = schematic_position if len(schematic_position) == 2 else ()

        # Center window on cursor, and remember where the cursor was for track_cursor
        cursor_position = QtGui.QCursor.pos()
        self.open_position = cursor_position
        self.last_position = cursor_position
        self.pen_arrived = False
        self.move(cursor_position.x() - self.gate_size // 2, cursor_position.y() - self.gate_size // 2)

        self.show()
        self.raise_()

        self.cursor_timer.start()

    def track_cursor(self) -> None:
        """
        Track Cursor
        ============

        Check where the cursor is. Called by the cursor timer while the gate is open.

        Run a section when the cursor is swiped from inside the gate out into its glow.
        Until then, highlight the section the cursor is heading toward. The gate never moves
        while it is open.

        The first cursor move after a tablet pen comes into range is a jump to the pen, not
        a swipe, so it never runs a section.
        """

        # A section runs only once each time the gate is shown
        if self.triggered or not self.isVisible():
            return

        # Measure from where the cursor was when the gate opened, not from the window: on a second
        # showing the window can still report its old place for a moment, which ran a section at once
        cursor_position = QtGui.QCursor.pos()
        last_offset = self.last_position - self.open_position
        position = cursor_position - self.open_position
        x_offset = position.x()
        y_offset = position.y()
        distance = math.hypot(x_offset, y_offset)

        # Pen just came into range, take its place as the new starting point without running anything
        if self.pen_arrived:
            if self.pen_timer.elapsed() > PEN_ARRIVAL_TIME:
                self.pen_arrived = False
            elif cursor_position != self.last_position:
                self.pen_arrived = False
                last_offset = position

        self.last_position = cursor_position

        trigger_radius = TRIGGER_RADIUS * self.scale

        # Cursor was swiped from inside the gate into a section's glow, run the section at that angle
        if distance > trigger_radius:
            if math.hypot(last_offset.x(), last_offset.y()) <= trigger_radius:
                self.triggered = True
                self.run_section(self.section_at_angle(x_offset, y_offset))

                return

        # Outside the gate, or too close to the center to tell which way the cursor is heading
        section_index = None
        if HOVER_START_RADIUS * self.scale < distance <= trigger_radius:
            section_index = self.section_at_angle(x_offset, y_offset)

        # Repaint only when the highlighted section changes
        if section_index != self.hover_section:
            self.hover_section = section_index
            self.update()

    def pen_in_range(self) -> None:
        """
        Pen In Range
        ============

        Note that a tablet pen just came into range, so track_cursor can tell the cursor's
        jump to the pen from a swipe. Called by the click filter.
        """

        self.pen_arrived = True
        self.pen_timer.start()

    def run_section(self, section_index: int) -> None:
        """
        Run Section
        ===========

        Close the gate, then run a section's action. A blank section only closes the gate.

        Args
        ----
            section_index (int): Index of the section to run.
        """

        # Close the gate first so a failing section can never leave it open
        self.hide()

        section = self.sections[section_index]

        if section['script']:
            self.run_script(section)

    def run_script(self, section: dict) -> None:
        """
        Run Script
        ==========

        Run a section's action: a Batch right-click menu action of another installed script,
        GateUI's own action that opens Gate UI Setup, or a Flame keyboard shortcut.
        Flame loads every hook script as a top-level module, so the script is looked up by
        name, asked for its menu actions as Flame does, and the action is called. None of
        the script's code is copied here.

        Prints which action was run, or why it could not be.

        When nothing is selected and the action adds exactly one node, the node is moved to
        where the gate was opened.

        Args
        ----
            section (dict): Section with 'script', 'group' and 'action'.
        """

        name = section_name(section)

        # GateUI's own action: open Gate UI Setup
        if all(section[key] == SETUP_ACTION[key] for key in SETUP_ACTION):
            pyflame.print(f'Executed: {name}', script_name=SCRIPT_NAME)

            try:
                getattr(sys.modules.get(__name__), 'GateUISetup', GateUISetup)(())
            except Exception as e:
                pyflame.print(f'{name} failed: {e}', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

            return

        # The Flame Hotkey item is never put on a tab as is, it has no shortcut to run
        if section['script'] == FLAME_HOTKEY_ACTION['script']:
            pyflame.print(f'{name} could not be run, no Flame shortcut name was set for it in Gate UI Setup.', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

            return

        # A Flame keyboard shortcut, run by its Description in the Keyboard Shortcut editor
        if section['script'] == FLAME_SHORTCUT_SCRIPT:
            try:
                flame.execute_shortcut(section['action'])
                pyflame.print(f'Executed: {name}', script_name=SCRIPT_NAME)
            except Exception as e:
                pyflame.print(f'{name} could not be run: {e}', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

            return

        try:

            # Get the script Flame has already loaded
            script = sys.modules.get(section['script'])
            if script is None or not callable(getattr(script, 'get_batch_custom_ui_actions', None)):
                pyflame.print(f'{name} could not be run, the {section["script"]} script is not installed.', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

                return

            # Get the action from the script's own Batch menu
            action = None
            for script_group, script_action in get_script_actions(script):
                if script_group == section['group'] and script_action.get('name') == section['action']:
                    action = script_action
                    break

            if action is None:
                pyflame.print(f'{name} could not be run, the {section["script"]} script has no such action.', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

                return

            # Same selection Flame passes to a Batch right-click menu
            selection = tuple(flame.batch.selected_nodes.get_value())

            # Check that the action's menu would show for the selection
            if 'isVisible' in action and not action['isVisible'](selection):
                pyflame.print(f'{name} is not available for the current selection.', print_type=PrintType.WARNING, script_name=SCRIPT_NAME)

                return

            pyflame.print(f'Executed: {name}', script_name=SCRIPT_NAME)

            # With nothing selected, note the nodes there are now so a node the action adds can be found
            node_names = None
            if not selection and self.schematic_position:
                node_names = self.batch_node_names()

            action['execute'](selection)

        except Exception as e:
            pyflame.print(f'{name} failed: {e}', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)

            return

        if node_names is not None:
            self.move_new_node(node_names)

    def batch_node_names(self) -> set | None:
        """
        Batch Node Names
        ================

        Get the names of the nodes in Batch. Flame keeps node names unique within a batch
        group, so a name tells a node apart from the others.

        Returns
        -------
            node_names (set | None): Name of each node in Batch. None if the nodes can't be read, so the action still runs, just without the move.
        """

        try:
            return {str(node.name)[1:-1] for node in flame.batch.nodes}
        except Exception:
            return None

    def move_new_node(self, node_names: set) -> None:
        """
        Move New Node
        =============

        Move the node an action added to where the gate was opened. Only when the action
        added exactly one node; otherwise nothing is moved. A failure is printed as a
        warning and goes no further.

        Args
        ----
            node_names (set): Names of the nodes in Batch before the action ran.
        """

        try:
            new_nodes = [node for node in flame.batch.nodes if str(node.name)[1:-1] not in node_names]
            if len(new_nodes) != 1:
                return

            new_nodes[0].pos_x = int(self.schematic_position[0])
            new_nodes[0].pos_y = int(self.schematic_position[1])
        except Exception as e:
            pyflame.print(f'The new node could not be moved to where the gate was opened: {e}', print_type=PrintType.WARNING, script_name=SCRIPT_NAME)

    # ==============================================================================

    def paintEvent(self, event) -> None:
        """
        Paint Event
        ===========

        Draw the gate. Nothing is drawn behind it, so whatever is under the window shows through.

        Args
        ----
            event (QPaintEvent): Qt paint event.
        """

        painter = QtGui.QPainter(self)

        # Almost invisible fill so the see-through parts of the window still get mouse events
        painter.fillRect(self.rect(), HIT_COLOR)

        # Gate centered in the window, which is bigger than the gate when its labels need the room
        gate_offset = (self.gate_size - WIDGET_SIZE * self.scale) / 2
        painter.translate(gate_offset, gate_offset)

        # The section the cursor is heading toward also gets the yellow ring that marks a selected tab in Setup
        paint_gate(painter, self.sections, self.font_family, self.hover_section, self.hover_section, self.scale)

        painter.end()

    def mousePressEvent(self, event) -> None:
        """
        Mouse Press Event
        =================

        Close the gate without running a section.

        Args
        ----
            event (QMouseEvent): Qt mouse event.
        """

        self.hide()

    def hideEvent(self, event) -> None:
        """
        Hide Event
        ==========

        Stop following the cursor whenever the gate closes, however it was closed.

        Args
        ----
            event (QHideEvent): Qt hide event.
        """

        super().hideEvent(event)

        self.cursor_timer.stop()

# ==============================================================================
# [Setup Window]
# ==============================================================================

class GateUISetupHotkeyFilter(QtCore.QObject):

    def __init__(self, window, hotkey_changed) -> None:
        """
        Init
        ====

        Create a filter that takes the key presses of the Edit Hotkey window, whichever of its
        widgets has focus. Install it on the application while the window is open.

        Args
        ----
            window (PyFlameWindow):
                Edit Hotkey window.

            hotkey_changed (callable):
                Called with the key (int) and modifiers (int) of a new hotkey, or with 0 and 0 when the hotkey is cleared.
        """

        super().__init__()

        self.window = window
        self.hotkey_changed = hotkey_changed

    def eventFilter(self, watched, event) -> bool:
        """
        Event Filter
        ============

        Take a key press in the Edit Hotkey window before any widget in it gets it. Key presses
        are handled when they reach the window, so focus and input methods don't matter.
        Shortcut checks for the window's widgets are answered too, so a shortcut set
        elsewhere in Flame can't take a key combination first. Everything else is passed on.

        Args
        ----
            watched (QObject):
                Object the event was sent to.

            event (QEvent):
                Qt event.

        Returns
        -------
            handled (bool): True for a key press taken as the hotkey or as clearing it, otherwise False.
        """

        event_type = event.type()

        if event_type != QtCore.QEvent.KeyPress and event_type != QtCore.QEvent.ShortcutOverride:
            return False

        # Never let an error here break the window's own key handling, so pass the event on
        try:
            if event_type == QtCore.QEvent.KeyPress:
                if watched != self.window.windowHandle():
                    return False
            elif not isinstance(watched, QtWidgets.QWidget) or watched.window() is not self.window:
                return False

            return self.key_press(event, event_type == QtCore.QEvent.ShortcutOverride)
        except Exception:
            return False

    def key_press(self, event, shortcut_check: bool) -> bool:
        """
        Key Press
        =========

        Take a key pressed with Shift, Control, Alt or Meta as the hotkey. Backspace or Delete
        pressed alone clears it. A modifier key by itself is waited out, and a key pressed
        alone is ignored. Escape, Return, Enter, Tab and Backtab are never taken; they are
        passed on so they keep doing what they do in the window.

        Args
        ----
            event (QKeyEvent):
                Qt key event.

            shortcut_check (bool):
                True when Qt is only asking if the key may be used as a shortcut. The key press itself follows.

        Returns
        -------
            handled (bool): True if the key was taken, so it goes no further.
        """

        if event.key() in HOTKEY_RESERVED_KEYS:
            return False

        modifiers = event.modifiers().value & HOTKEY_MODIFIER_MASK

        if not modifiers and event.key() in HOTKEY_CLEAR_KEYS:
            if not shortcut_check:
                self.hotkey_changed(0, 0)
            event.accept()

            return True

        key = hotkey_event_key(event)

        # A key alone would be taken from Flame on every press in Batch, even while typing in Flame's own fields
        if not key or not modifiers:
            return False

        # Only a combination the gate can use
        if clean_hotkey(key, modifiers) != (key, modifiers):
            return False

        if not shortcut_check:
            self.hotkey_changed(key, modifiers)
        event.accept()

        return True

class GateUISetupGraphic(QtWidgets.QWidget):

    def __init__(self, sections: list, dragged_action, confirm_replace, sections_changed, name_flame_hotkey) -> None:
        """
        Init
        ====

        Build the picture of the gate for the Gate UI Setup window. Batch actions are dropped
        on its tabs, a tab can be dragged onto another tab, and a click selects a tab.

        Args
        ----
            sections (list):
                The gate's four or eight section dicts. Read the edited ones back from the
                sections attribute.

            dragged_action (callable):
                Called with the widget a drag started in. Returns the Batch action being
                dragged ('script', 'group' and 'action'), or None if the drag is something else.

            confirm_replace (callable):
                Called with a section and the action dropped on it. Returns True if the
                section's action should be replaced.

            sections_changed (callable):
                Called with no arguments after a drop or a click changed the sections or
                the selected tab.

            name_flame_hotkey (callable):
                Called with no arguments when the Flame Hotkey item is dropped. Returns the
                Flame shortcut action to put on the tab, or None to add nothing.
        """

        super().__init__()

        self.sections = sections
        self.dragged_action = dragged_action
        self.confirm_replace = confirm_replace
        self.sections_changed = sections_changed
        self.name_flame_hotkey = name_flame_hotkey

        # Tab under a dragged action, the selected tab, and if the extra tabs are being shown for a drag
        self.hover_section = None
        self.selected_section = None
        self.extra_preview = False

        # Tab the mouse was pressed on and where, to tell a drag of the tab from a click
        self.press_section = None
        self.press_position = QtCore.QPoint()

        # True from a drop being taken until it has been handled, which is just after the drag ends
        self.drop_pending = False

        # Draw the gate at the size of the other window widgets
        self.gate_size = pyflame.gui_resize(WIDGET_SIZE)
        self.setMinimumSize(self.gate_size, self.gate_size)

        self.font_family = load_gate_font()

        self.setAcceptDrops(True)

    # ==============================================================================

    def shown_sections(self) -> list:
        """
        Shown Sections
        ==============

        Get the sections as drawn: with four blank extra ones while a drag is showing the extra tabs.

        Returns
        -------
            sections (list): Four or eight section dicts.
        """

        if self.extra_preview:
            return add_extra_sections(self.sections)

        return self.sections

    def angle_at(self, position) -> float | None:
        """
        Angle At
        ========

        Get the angle of a point around the center of the gate.

        Args
        ----
            position (QPoint): Point in the widget.

        Returns
        -------
            angle (float | None): Degrees clockwise from the top. None if the point is too close to the center to tell.
        """

        x_offset = position.x() - self.width() / 2
        y_offset = position.y() - self.height() / 2

        if math.hypot(x_offset, y_offset) <= HOVER_START_RADIUS * self.gate_size / WIDGET_SIZE:
            return None

        return math.degrees(math.atan2(x_offset, -y_offset)) % 360

    def section_at_angle(self, angle: float, section_count: int) -> int:
        """
        Section At Angle
        ================

        Get the section an angle lies in. Every angle belongs to the nearest section.

        Args
        ----
            angle (float):
                Degrees clockwise from the top.

            section_count (int):
                Number of sections the gate is showing.

        Returns
        -------
            section_index (int): Index of the section.
        """

        section_angle = 360 / section_count

        return int(((angle + section_angle / 2) % 360) // section_angle)

    def in_new_tab_zone(self, angle: float) -> bool:
        """
        In New Tab Zone
        ===============

        Check if an angle is in one of the spaces between the four tabs, where a dragged
        action adds the extra tabs.

        Args
        ----
            angle (float): Degrees clockwise from the top.

        Returns
        -------
            in_zone (bool): True if the angle is within half a zone of the middle of a space.
        """

        section_angle = 360 / SECTION_COUNT
        from_space = (angle - section_angle / 2) % section_angle

        return min(from_space, section_angle - from_space) <= NEW_TAB_ZONE_ANGLE / 2

    def in_gate(self, position) -> bool:
        """
        In Gate
        =======

        Check if a point is on the drawn gate: no further from the center than the glow reaches.

        Args
        ----
            position (QPoint): Point in the widget.

        Returns
        -------
            in_gate (bool): True if the point is on the gate.
        """

        return math.hypot(position.x() - self.width() / 2, position.y() - self.height() / 2) <= GLOW_RADIUS * self.gate_size / WIDGET_SIZE

    def drag_over(self, position, gate_only: bool=False) -> None:
        """
        Drag Over
        =========

        Highlight the tab under a drag. Over a space between the four tabs the four extra
        tabs are shown, and they stay shown until the drag leaves or drops.

        Args
        ----
            position (QPoint):
                Where the drag is, in the widget.

            gate_only (bool):
                True for a dragged tab: off the drawn gate no tab is highlighted, so a drop
                there changes nothing.
        """

        angle = self.angle_at(position)

        if angle is None or (gate_only and not self.in_gate(position)):
            hover_section = None
        else:
            if not self.extra_preview and len(self.sections) == SECTION_COUNT and self.in_new_tab_zone(angle):
                self.extra_preview = True

            hover_section = self.section_at_angle(angle, len(self.shown_sections()))

        self.hover_section = hover_section
        self.update()

    def drag_leave(self) -> None:
        """
        Drag Leave
        ==========

        Stop highlighting, and stop showing the extra tabs, when a drag leaves without dropping.
        """

        self.hover_section = None
        self.extra_preview = False
        self.update()

    def drop(self, position, action: dict) -> None:
        """
        Drop
        ====

        Put a dropped action on the tab under it. A tab that already has an action is only
        replaced after confirmation. A drop on one of the extra tabs shown for the drag
        adds the four extra tabs; a drop on one of the four tabs leaves the gate at four.
        The Flame Hotkey item first asks for the shortcut's name; without one nothing changes.

        Args
        ----
            position (QPoint):
                Where the action was dropped, in the widget.

            action (dict):
                Batch action with 'script', 'group' and 'action'.
        """

        self.drop_pending = False

        # Find the tab at the drop, then end the drag's highlight and extra tabs
        self.drag_over(position)
        section_index = self.hover_section
        extra_preview = self.extra_preview
        self.drag_leave()

        if section_index is None:
            return

        # The Flame Hotkey item becomes the named Flame shortcut. Cancelled or not found, nothing is added
        if action['script'] == FLAME_HOTKEY_ACTION['script']:
            action = self.name_flame_hotkey()
            if action is None:
                return

        sections = self.sections

        if extra_preview:
            if section_index % 2:
                sections = add_extra_sections(sections)
            else:
                section_index //= 2

        if sections[section_index]['script'] and not self.confirm_replace(sections[section_index], action):
            return

        # A new action's tab starts with the action's name
        sections[section_index] = {
            'label': action['action'],
            'script': action['script'],
            'group': list(action['group']),
            'action': action['action'],
            }

        self.sections = sections
        self.selected_section = section_index
        self.update()

        self.sections_changed()

    def drop_tab(self, position, source_index: int) -> None:
        """
        Drop Tab
        ========

        Move a dragged tab's name and action to the tab it was dropped on. A blank tab takes
        them and the dragged tab is left blank; a tab that has something on it swaps with
        the dragged tab, so nothing is lost. A drop on one of the extra tabs shown for the
        drag adds the four extra tabs. A drop on the dragged tab itself, at the center or
        off the gate changes nothing.

        Args
        ----
            position (QPoint):
                Where the tab was dropped, in the widget.

            source_index (int):
                Index of the dragged tab.
        """

        self.drop_pending = False

        # Find the tab at the drop, then end the drag's highlight and extra tabs
        self.drag_over(position, gate_only=True)
        section_index = self.hover_section
        extra_preview = self.extra_preview
        self.drag_leave()

        sections = self.sections

        if section_index is None or not 0 <= source_index < len(sections):
            return

        # With the extra tabs added every tab that was there moves to twice its index
        if extra_preview:
            if section_index % 2:
                sections = add_extra_sections(sections)
                source_index *= 2
            else:
                section_index //= 2

        if section_index == source_index:
            return

        sections[section_index], sections[source_index] = sections[source_index], sections[section_index]

        self.sections = sections
        self.selected_section = section_index
        self.update()

        self.sections_changed()

    def dragged_tab(self, event) -> int | None:
        """
        Dragged Tab
        ===========

        Get the tab being dragged, if a drag is a drag of one of the gate's tabs.

        Args
        ----
            event (QDropEvent): Qt drag or drop event.

        Returns
        -------
            source_index (int | None): Index of the dragged tab. None if the drag is something else.
        """

        mime_data = event.mimeData()
        if mime_data is None or not mime_data.hasFormat(TAB_MIME_TYPE):
            return None

        try:
            return int(bytes(mime_data.data(TAB_MIME_TYPE)).decode())
        except ValueError:
            return None

    def start_tab_drag(self, source_index: int) -> None:
        """
        Start Tab Drag
        ==============

        Start dragging a tab. Returns when the drag has ended.

        Args
        ----
            source_index (int): Index of the tab to drag.
        """

        mime_data = QtCore.QMimeData()
        mime_data.setData(TAB_MIME_TYPE, str(source_index).encode())

        drag = QtGui.QDrag(self)
        drag.setMimeData(mime_data)
        drag.exec(QtCore.Qt.CopyAction)

        self.drag_ended()

    def drag_ended(self) -> None:
        """
        Drag Ended
        ==========

        Stop highlighting and stop showing the extra tabs when a drag ended without a drop
        here, in case the drag never told the widget it left (a drag cancelled with Escape).
        After a drop here they are left alone: the drop is handled just after the drag ends
        and still needs them.
        """

        if not self.drop_pending:
            self.drag_leave()

    # ==============================================================================

    def dragEnterEvent(self, event) -> None:
        """
        Drag Enter Event
        ================

        Take drags of a Batch action or of one of the gate's own tabs only.

        Args
        ----
            event (QDragEnterEvent): Qt drag enter event.
        """

        tab_drag = self.dragged_tab(event) is not None

        if not tab_drag and self.dragged_action(event.source()) is None:
            event.ignore()

            return

        # Always a copy, whatever keys are held, so the action can never be taken out of the list
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()

        self.drag_over(event.position().toPoint(), gate_only=tab_drag)

    def dragMoveEvent(self, event) -> None:
        """
        Drag Move Event
        ===============

        Follow a dragged action or tab.

        Args
        ----
            event (QDragMoveEvent): Qt drag move event.
        """

        # Always a copy, whatever keys are held, so the action can never be taken out of the list
        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()

        self.drag_over(event.position().toPoint(), gate_only=self.dragged_tab(event) is not None)

    def dragLeaveEvent(self, event) -> None:
        """
        Drag Leave Event
        ================

        The drag left without dropping.

        Args
        ----
            event (QDragLeaveEvent): Qt drag leave event.
        """

        self.drag_leave()

    def dropEvent(self, event) -> None:
        """
        Drop Event
        ==========

        Take a dropped Batch action or tab.

        Args
        ----
            event (QDropEvent): Qt drop event.
        """

        position = event.position().toPoint()

        # One of the gate's own tabs
        source_index = self.dragged_tab(event)
        if source_index is not None:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()

            self.drop_pending = True
            QtCore.QTimer.singleShot(0, lambda: self.drop_tab(position, source_index))

            return

        action = self.dragged_action(event.source())
        if action is None:
            event.ignore()
            self.drag_leave()

            return

        event.setDropAction(QtCore.Qt.CopyAction)
        event.accept()

        # Handle the drop once the drag is over, so a confirmation window never opens in the middle of it
        self.drop_pending = True
        QtCore.QTimer.singleShot(0, lambda: self.drop(position, action))

    def mousePressEvent(self, event) -> None:
        """
        Mouse Press Event
        =================

        Select the pressed tab, and remember it in case the press turns into a drag of the
        tab. A press outside the drawn gate selects nothing. The press is kept from the
        window, which would start moving.

        Args
        ----
            event (QMouseEvent): Qt mouse event.
        """

        self.press_section = None

        position = event.position().toPoint()

        # Outside the glow there is no tab to click
        if not self.in_gate(position):
            return

        angle = self.angle_at(position)
        if angle is None:
            return

        self.selected_section = self.section_at_angle(angle, len(self.sections))
        self.update()

        if event.button() == QtCore.Qt.LeftButton:
            self.press_section = self.selected_section
            self.press_position = position

        self.sections_changed()

    def mouseMoveEvent(self, event) -> None:
        """
        Mouse Move Event
        ================

        Start dragging the pressed tab once the mouse has moved far enough from where it
        was pressed. A blank tab can't be dragged. Mouse moves are kept from the window,
        which would move with them.

        Args
        ----
            event (QMouseEvent): Qt mouse event.
        """

        event.accept()

        if self.press_section is None or not event.buttons() & QtCore.Qt.LeftButton:
            return

        if (event.position().toPoint() - self.press_position).manhattanLength() < QtWidgets.QApplication.startDragDistance():
            return

        # Take the pressed tab so one press starts one drag only
        source_index = self.press_section
        self.press_section = None

        section = self.sections[source_index]
        if not section['script'] and not section['label']:
            return

        self.start_tab_drag(source_index)

    def mouseReleaseEvent(self, event) -> None:
        """
        Mouse Release Event
        ===================

        The press was a click, not the start of a drag.

        Args
        ----
            event (QMouseEvent): Qt mouse event.
        """

        self.press_section = None

    def paintEvent(self, event) -> None:
        """
        Paint Event
        ===========

        Draw the gate in the middle of the widget, on the window's own background.

        Args
        ----
            event (QPaintEvent): Qt paint event.
        """

        # While the extra tabs are shown for a drag, the selected tab is at twice its index
        selected_section = self.selected_section
        if self.extra_preview and selected_section is not None:
            selected_section *= 2

        painter = QtGui.QPainter(self)
        painter.translate((self.width() - self.gate_size) / 2, (self.height() - self.gate_size) / 2)
        painter.scale(self.gate_size / WIDGET_SIZE, self.gate_size / WIDGET_SIZE)

        paint_gate(painter, self.shown_sections(), self.font_family, self.hover_section, selected_section)

        painter.end()

class GateUISetup:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} Setup {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Only one Gate UI Setup window at a time, bring an open one to the front instead
        open_window = find_setup_window()
        if open_window is not None:
            open_window.show()
            open_window.raise_()

            return

        # A config that can't be read must not keep Setup from opening: show the default tabs, Save replaces the config
        try:
            self.settings = load_config()
            sections = self.settings.sections
            hotkey = clean_hotkey(self.settings.get('hotkey_key'), self.settings.get('hotkey_modifiers'))
            ui_scale = clean_ui_scale(self.settings.get('ui_scale'))
        except Exception as e:
            pyflame.print(f'Config could not be loaded, showing the default tabs: {e}', print_type=PrintType.ERROR, script_name=SCRIPT_NAME)
            self.settings = None
            sections = None
            hotkey = (DEFAULT_HOTKEY_KEY, DEFAULT_HOTKEY_MODIFIERS)
            ui_scale = DEFAULT_UI_SCALE

        self.sections = clean_sections(sections)
        self.hotkey = hotkey
        self.ui_scale = ui_scale

        # Help window opened from Setup, if any
        self.help_window = None

        self.setup()

    def setup(self) -> None:

        def dragged_action(source) -> dict | None:
            """
            Dragged Action
            ==============

            Get the Batch action being dragged.

            Args
            ----
                source (QWidget): Widget the drag started in.

            Returns
            -------
                action (dict | None): The selected action of the actions list, or None if the drag is not from that list.
            """

            if source is not self.actions_tree or self.actions_tree.currentItem() is None:
                return None

            return self.actions_tree.currentItem().data(0, QtCore.Qt.UserRole)

        def confirm_replace(section: dict, action: dict) -> bool:
            """
            Confirm Replace
            ===============

            Ask if the action on a tab should be replaced with the one dropped on it.

            Args
            ----
                section (dict):
                    Section the action was dropped on.

                action (dict):
                    Batch action that was dropped.

            Returns
            -------
                replace (bool): True if the user confirmed.
            """

            return bool(
                PyFlameMessageWindow(
                    message=f'Replace {section_name(section)} with {action["action"]}?',
                    message_type=MessageType.CONFIRM,
                    parent=self.setup_window,
                    )
                )

        def name_flame_hotkey() -> dict | None:
            """
            Name Flame Hotkey
            =================

            Ask for the name of the Flame keyboard shortcut a tab should run: its Description in
            Flame's Keyboard Shortcut editor. The name is checked against Flame's shortcut list.
            A name that differs only in case gets the list's spelling. If the list can't be read
            the name is taken unchecked, with a warning.

            Returns
            -------
                action (dict | None): Flame shortcut action with 'script', 'group' and 'action'. None if cancelled, empty or not found.
            """

            input_dialog = PyFlameInputDialog(
                text='',
                label_text='Shortcut Name From Keyboard Shortcut Editor',
                title='Flame Hotkey',
                parent=self.setup_window,
                )

            if input_dialog.text is None:
                return None

            shortcut = input_dialog.text.strip()
            if not shortcut:
                return None

            shortcut_names = flame_shortcut_names()

            if not shortcut_names:
                pyflame.print(f'The Flame keyboard shortcut list could not be read, {shortcut} was not checked.', print_type=PrintType.WARNING, script_name=SCRIPT_NAME)
            elif shortcut not in shortcut_names:
                # Same name in another case: use the spelling Flame has
                matches = sorted(name for name in shortcut_names if name.lower() == shortcut.lower())
                if not matches:
                    PyFlameMessageWindow(
                        message=f'{shortcut} was not found among the Flame keyboard shortcuts.\n\nThe name must match the Description shown in the Flame Keyboard Shortcut editor exactly.',
                        message_type=MessageType.ERROR,
                        parent=self.setup_window,
                        )

                    return None

                shortcut = matches[0]

            return {
                'script': FLAME_SHORTCUT_SCRIPT,
                'group': list(FLAME_SHORTCUT_GROUP),
                'action': shortcut,
                }

        def update_tab_widgets() -> None:
            """
            Update Tab Widgets
            ==================

            Show the selected tab's name and action, and enable the buttons that can be used.
            """

            sections = self.gate_graphic.sections
            section_index = self.gate_graphic.selected_section

            if section_index is None:
                self.tab_name_entry.text = ''
                self.tab_action_entry.text = 'No tab selected'
            else:
                section = sections[section_index]
                self.tab_name_entry.text = section['label']
                if section['script']:
                    self.tab_action_entry.text = f'{group_name(section["group"])} / {section["action"]}'
                else:
                    self.tab_action_entry.text = 'Blank tab'

            self.tab_name_entry.enabled = section_index is not None
            self.clear_tab_button.enabled = section_index is not None
            self.add_extra_tabs_button.enabled = len(sections) <= SECTION_COUNT
            self.remove_extra_tabs_button.enabled = len(sections) > SECTION_COUNT

        def tab_name_changed(text: str) -> None:
            """
            Tab Name Changed
            ================

            Show the edited name on the selected tab.

            Args
            ----
                text (str): Text of the Tab Name entry.
            """

            section_index = self.gate_graphic.selected_section
            if section_index is None:
                return

            self.gate_graphic.sections[section_index]['label'] = text
            self.gate_graphic.update()

        def clear_tab() -> None:
            """
            Clear Tab
            =========

            Take the name and action off the selected tab. The tab stays, blank.
            """

            section_index = self.gate_graphic.selected_section
            if section_index is None:
                return

            self.gate_graphic.sections[section_index] = blank_section()
            self.gate_graphic.update()

            update_tab_widgets()

        def add_extra_tabs() -> None:
            """
            Add Extra Tabs
            ==============

            Add the four extra tabs, one blank tab between each of the four. They always come together.
            """

            sections = self.gate_graphic.sections
            if len(sections) > SECTION_COUNT:
                return

            # The four tabs already there move to twice their index
            section_index = self.gate_graphic.selected_section
            if section_index is not None:
                self.gate_graphic.selected_section = section_index * 2

            self.gate_graphic.sections = add_extra_sections(sections)
            self.gate_graphic.update()

            update_tab_widgets()

        def remove_extra_tabs() -> None:
            """
            Remove Extra Tabs
            =================

            Remove the four extra tabs, after confirmation. They always go together.
            """

            sections = self.gate_graphic.sections
            if len(sections) <= SECTION_COUNT:
                return

            # Tell the user what is on the tabs that will be erased
            extra_names = [section_name(section) for section in sections[1::2] if section['script'] or section['label']]
            if extra_names:
                erased = 'These tabs will be erased:\n\n' + '\n'.join(extra_names)
            else:
                erased = 'All four are blank.'

            if not PyFlameMessageWindow(
                message=f'Remove the extra tabs?\n\nThe four extra tabs are removed together, along with anything on them.\n\n{erased}',
                message_type=MessageType.WARNING,
                parent=self.setup_window,
                ):
                return

            # The four tabs that stay move to half their index
            section_index = self.gate_graphic.selected_section
            if section_index is not None:
                self.gate_graphic.selected_section = None if section_index % 2 else section_index // 2

            self.gate_graphic.sections = remove_extra_sections(sections)
            self.gate_graphic.update()

            update_tab_widgets()

        def edit_hotkey() -> None:
            """
            Edit Hotkey
            ===========

            Open a window that takes a new hotkey: a key pressed with Shift, Control, Alt or Meta
            anywhere in the window. Clear Hotkey, or Backspace or Delete, empties it, and Save
            can't be used until a new one is pressed. Save writes the new hotkey to the config
            file at once, has the gate use it and shows it in the Gate UI Hotkey field. Only the
            hotkey is written, unsaved tab changes are not. Cancel or Escape closes the window
            without changing anything.

            Cancel in the Gate UI Setup window afterwards does not undo a hotkey saved here.
            """

            def set_new_hotkey(key: int, modifiers: int) -> None:
                """
                Set New Hotkey
                ==============

                Show the hotkey pressed in the window, or nothing when it was cleared. Save can
                only be used while there is one.

                Args
                ----
                    key (int):
                        Qt key. 0 when the hotkey was cleared.

                    modifiers (int):
                        Qt keyboard modifiers.
                """

                nonlocal new_hotkey

                new_hotkey = (key, modifiers) if key else None

                hotkey_display_entry.text = hotkey_text(key, modifiers) if key else ''
                hotkey_save_button.enabled = new_hotkey is not None

            def clear_hotkey() -> None:
                """
                Clear Hotkey
                ============

                Empty the hotkey in the window, so a new one can be pressed.
                """

                set_new_hotkey(0, 0)

            def save_hotkey() -> None:
                """
                Save Hotkey
                ===========

                Save the new hotkey to the config file, use it at once and close the window.
                If it can't be saved an error is shown and nothing changes. Nothing happens
                while the hotkey is empty.
                """

                # Return does nothing while there is no hotkey to save
                if new_hotkey is None:
                    return

                hotkey = new_hotkey

                # Same hotkey as before, nothing to save
                if hotkey == self.hotkey:
                    hotkey_window.close()

                    return

                error = ''

                if self.settings is None:
                    error = 'The config file could not be read when Gate UI Setup opened. Save Gate UI Setup to write a new config file, then edit the hotkey again.'
                else:
                    try:
                        # Written with the tabs as they were loaded, not the unsaved ones, so only the hotkey changes
                        self.settings.save_config(
                            config_values={
                                'hotkey_key': hotkey[0],
                                'hotkey_modifiers': hotkey[1],
                                }
                            )
                    except Exception as e:
                        error = str(e)

                if error:
                    PyFlameMessageWindow(
                        message=f'The hotkey could not be saved.\n\n{error}',
                        message_type=MessageType.ERROR,
                        parent=hotkey_window,
                        )

                    return

                # After Flame reloads the script the hotkey in use is the newly loaded script's, not this one's
                getattr(sys.modules.get(__name__), 'set_hotkey', set_hotkey)(*hotkey)

                self.hotkey = hotkey
                self.hotkey_entry.text = hotkey_text(*hotkey)

                hotkey_window.close()

            def close_hotkey_window() -> None:
                """
                Close Hotkey Window
                ===================

                Close the window without changing the hotkey.
                """

                hotkey_window.close()

            # Instruction names the modifier keys as the hotkey field shows them on this platform
            modifier_names = [name for modifier, name in HOTKEY_MODIFIER_NAMES]
            instruction = f'In This Window Press {", ".join(modifier_names[:-1])} or {modifier_names[-1]} + Another Key'

            # Hotkey shown in the window until another is pressed or it is cleared
            new_hotkey = self.hotkey

            # ------------------------------------------------------------------------------
            # [Window Elements]
            # ------------------------------------------------------------------------------

            # Window
            hotkey_window = PyFlameWindow(
                title='Edit Hotkey',
                return_pressed=save_hotkey,
                escape_pressed=close_hotkey_window,
                grid_layout_columns=4,
                grid_layout_rows=3,
                grid_layout_column_width=110,
                message_bar=False,
                parent=self.setup_window,
                )

            # Labels
            hotkey_instruction_label = PyFlameLabel(
                text=instruction,
                style=Style.UNDERLINE,
                )

            # Entries
            hotkey_display_entry = PyFlameEntry(
                text=hotkey_text(*self.hotkey),
                read_only=True,
                )

            # The entry watches itself for the Alt key, to copy its text to the clipboard and show it in a
            # tooltip while the mouse is over it. Here Alt is part of a hotkey being pressed, so stop that
            hotkey_display_entry.removeEventFilter(hotkey_display_entry)

            # A focused read-only entry would keep Return and Escape from the window
            hotkey_display_entry.setFocusPolicy(QtCore.Qt.NoFocus)

            # Buttons
            hotkey_clear_button = PyFlameButton(
                text='Clear Hotkey',
                connect=clear_hotkey,
                )
            hotkey_save_button = PyFlameButton(
                text='Save',
                connect=save_hotkey,
                color=Color.BLUE,
                )
            hotkey_cancel_button = PyFlameButton(
                text='Cancel',
                connect=close_hotkey_window,
                )

            # ------------------------------------------------------------------------------
            # [Widget Layout]
            # ------------------------------------------------------------------------------

            hotkey_window.grid_layout.addWidget(hotkey_instruction_label, 0, 0, 1, 4)
            hotkey_window.grid_layout.addWidget(hotkey_display_entry, 1, 0, 1, 4)
            hotkey_window.grid_layout.addWidget(hotkey_clear_button, 3, 0)
            hotkey_window.grid_layout.addWidget(hotkey_cancel_button, 3, 2)
            hotkey_window.grid_layout.addWidget(hotkey_save_button, 3, 3)

            # Focus the window itself once it is showing: it has no input method, so a dead key such as Alt-` on macOS
            # arrives as a key press instead of starting an accent. A window that isn't shown yet can't take focus
            QtCore.QTimer.singleShot(0, hotkey_window.setFocus)

            # Take key presses for this window while it is open, and always stop when it closes
            hotkey_filter = GateUISetupHotkeyFilter(
                window=hotkey_window,
                hotkey_changed=set_new_hotkey,
                )
            app = QtWidgets.QApplication.instance()
            app.installEventFilter(hotkey_filter)

            # Wait here until the window is closed, like PyFlameLib's input dialog
            try:
                hotkey_window.exec_()
            finally:
                app.removeEventFilter(hotkey_filter)

        def show_help() -> None:
            """
            Show Help
            =========

            Open the Gate UI guide (README.md) in a help window. If one is already open, bring it to the front instead.
            """

            if self.help_window is not None and self.help_window.is_open():
                self.help_window.show()

                return

            self.help_window = PyFlameHelpWindow(
                readme_path=os.path.join(SCRIPT_PATH, 'README.md'),
                script_url=SCRIPT_URL,
                title=f'Gate UI Help <small>{SCRIPT_VERSION}</small>',
                parent=self.setup_window,
                )

        def save() -> None:
            """
            Save
            ====

            Save the tabs, the hotkey and the UI Scale to the config file, have the gate use them from now on, and close the window.
            A config that can't be read is written new. If the config can't be written an error is shown and the
            window stays open.
            """

            for section in self.gate_graphic.sections:
                section['label'] = section['label'].strip()

            config_values = {
                'sections': self.gate_graphic.sections,
                'hotkey_key': self.hotkey[0],
                'hotkey_modifiers': self.hotkey[1],
                'ui_scale': clean_ui_scale(self.ui_scale_slider.value),
                }

            saved = False

            if self.settings is not None:
                try:
                    self.settings.save_config(config_values=config_values)
                    saved = True
                except Exception as e:
                    pyflame.print(f'Config could not be updated, writing a new one: {e}', print_type=PrintType.WARNING, script_name=SCRIPT_NAME)

            # The config can't be read (damaged before or after the window opened), write a new one in its place, the
            # same way PyFlameConfig writes it
            if not saved:
                try:
                    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
                    with open(CONFIG_PATH, 'w') as config_file:
                        json.dump(
                            {'script_name': CONFIG_SCRIPT_NAME, **config_values},
                            config_file,
                            indent=4,
                            )
                except Exception as e:
                    PyFlameMessageWindow(
                        message=f'The settings could not be saved.\n\n{e}',
                        message_type=MessageType.ERROR,
                        parent=self.setup_window,
                        )

                    return

            # After Flame reloads the script the gate and hotkey in use are the newly loaded script's, not this one's
            current_script = sys.modules.get(__name__)
            getattr(current_script, 'reset_gate_window', reset_gate_window)()
            getattr(current_script, 'set_hotkey', set_hotkey)(*self.hotkey)

            self.setup_window.close()

        def close_window() -> None:
            """
            Close Window
            ============

            Close window without saving.
            """

            self.setup_window.close()

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.setup_window = PyFlameWindow(
            title=f'Gate UI Setup <small>{SCRIPT_VERSION}</small>',
            escape_pressed=close_window,
            grid_layout_columns=7,
            grid_layout_rows=19,
            grid_layout_adjust_column_widths={3: 50}, # Empty column between the list and the gate
            parent=None,
            )

        # Name the window so it can be found while it is open, the gate doesn't open over it
        self.setup_window.setObjectName(SETUP_WINDOW_NAME)

        # Labels
        self.actions_label = PyFlameLabel(
            text='Available Actions',
            style=Style.UNDERLINE,
            )
        self.gate_label = PyFlameLabel(
            text='Gate UI - Drag Actions onto Tabs, or Tab to Tab',
            style=Style.UNDERLINE,
            )
        self.tab_name_label = PyFlameLabel(
            text='Tab Name',
            )
        self.tab_action_label = PyFlameLabel(
            text='Tab Action',
            )
        self.hotkey_label = PyFlameLabel(
            text='Gate UI Hotkey',
            )
        self.ui_scale_label = PyFlameLabel(
            text='UI Scale',
            )

        # Entries
        self.tab_name_entry = PyFlameEntry(
            text='',
            text_changed=tab_name_changed,
            )
        self.tab_action_entry = PyFlameEntry(
            text='',
            read_only=True,
            )
        self.hotkey_entry = PyFlameEntry(
            text=hotkey_text(*self.hotkey),
            read_only=True,
            )

        # Available actions list, grouped by menu group. Only the actions can be dragged, and a drag only ever copies
        self.actions_tree = PyFlameTreeWidget(
            column_names=['Action'],
            top_level_selectable=False,
            top_level_collapsible=True,
            draggable=True,
            )
        self.actions_tree.clear()

        actions_by_group = {}
        for action in find_batch_actions():
            actions_by_group.setdefault(group_name(action['group']), []).append(action)

        # The Flame group (Flame Hotkey) always comes first, Other last. Another script's actions in a menu group also
        # named Flame are listed under the same heading
        flame_group = group_name(FLAME_HOTKEY_ACTION['group'])

        for group in sorted(actions_by_group, key=lambda name: (name != flame_group, name == NO_GROUP_NAME, name.lower())):
            group_item = self.actions_tree.add_item_with_columns([group])

            for action in sorted(actions_by_group[group], key=lambda action: action['action'].lower()):
                action_item = self.actions_tree.add_item_with_columns([action['action']], parent=group_item)
                action_item.setData(0, QtCore.Qt.UserRole, action)

        # Set what can be done with each item once the list is filled, the tree widget changes item flags as items
        # are added. It lets an item be dragged when it can be selected, so the groups can't be and the actions can
        for group_index in range(self.actions_tree.topLevelItemCount()):
            group_item = self.actions_tree.topLevelItem(group_index)
            group_item.setFlags(QtCore.Qt.ItemIsEnabled)
            group_item.setExpanded(True)

            for action_index in range(group_item.childCount()):
                group_item.child(action_index).setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)

        # Gate picture
        self.gate_graphic = GateUISetupGraphic(
            sections=self.sections,
            dragged_action=dragged_action,
            confirm_replace=confirm_replace,
            sections_changed=update_tab_widgets,
            name_flame_hotkey=name_flame_hotkey,
            )
        self.actions_tree.drag_end_connect_callback = self.gate_graphic.drag_ended

        # Sliders
        self.ui_scale_slider = PyFlameSlider(
            min_value=UI_SCALE_MIN,
            max_value=UI_SCALE_MAX,
            start_value=self.ui_scale,
            )

        # Buttons
        self.edit_hotkey_button = PyFlameButton(
            text='Edit Hotkey',
            connect=edit_hotkey,
            )
        self.clear_tab_button = PyFlameButton(
            text='Clear Tab',
            connect=clear_tab,
            )
        self.add_extra_tabs_button = PyFlameButton(
            text='Add Extra Tabs',
            connect=add_extra_tabs,
            )
        self.remove_extra_tabs_button = PyFlameButton(
            text='Remove Extra Tabs',
            connect=remove_extra_tabs,
            )
        self.help_button = PyFlameButton(
            text='Help',
            connect=show_help,
            )
        self.save_button = PyFlameButton(
            text='Save',
            connect=save,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.actions_label, 0, 0, 1, 3)
        self.setup_window.grid_layout.addWidget(self.actions_tree, 1, 0, 13, 3)

        self.setup_window.grid_layout.addWidget(self.hotkey_label, 15, 0)
        self.setup_window.grid_layout.addWidget(self.hotkey_entry, 15, 1)
        self.setup_window.grid_layout.addWidget(self.edit_hotkey_button, 15, 2)
        self.setup_window.grid_layout.addWidget(self.ui_scale_label, 16, 0)
        self.setup_window.grid_layout.addWidget(self.ui_scale_slider, 16, 1)

        self.setup_window.grid_layout.addWidget(self.gate_label, 0, 4, 1, 3)
        self.setup_window.grid_layout.addWidget(self.gate_graphic, 1, 4, 13, 3)

        self.setup_window.grid_layout.addWidget(self.tab_name_label, 14, 4)
        self.setup_window.grid_layout.addWidget(self.tab_name_entry, 14, 5, 1, 2)
        self.setup_window.grid_layout.addWidget(self.tab_action_label, 15, 4)
        self.setup_window.grid_layout.addWidget(self.tab_action_entry, 15, 5, 1, 2)

        self.setup_window.grid_layout.addWidget(self.clear_tab_button, 16, 4)
        self.setup_window.grid_layout.addWidget(self.add_extra_tabs_button, 16, 5)
        self.setup_window.grid_layout.addWidget(self.remove_extra_tabs_button, 16, 6)

        self.setup_window.grid_layout.addWidget(self.help_button, 18, 0)
        self.setup_window.grid_layout.addWidget(self.cancel_button, 18, 5)
        self.setup_window.grid_layout.addWidget(self.save_button, 18, 6)

        # The window was sized for its empty grid, with a space between every row. Qt leaves no space between
        # rows whose every cell is covered by the same tall widgets (the list and the gate picture), so the
        # filled grid is shorter and the window had empty space under the last row. Fit the window to what is in
        # it. The window's own waiting events are handled first (nothing else in Flame is touched): they show
        # the new widgets and give them their final look, and their sizes are not final until then
        for widget in [self.setup_window] + self.setup_window.findChildren(QtWidgets.QWidget):
            QtWidgets.QApplication.sendPostedEvents(widget)
        self.setup_window.grid_layout.activate()
        self.setup_window.layout().activate()
        self.setup_window.setFixedSize(self.setup_window.sizeHint())
        self.setup_window.center_window()

        # Nothing is selected to start with
        update_tab_widgets()

# ==============================================================================
# [Entry Points]
# ==============================================================================

gate_window = None

# Hotkey that opens the gate, kept in memory so the config is never read on a key press
hotkey_key = DEFAULT_HOTKEY_KEY
hotkey_modifiers = DEFAULT_HOTKEY_MODIFIERS

def set_hotkey(key, modifiers) -> None:
    """
    Set Hotkey
    ==========

    Set the hotkey that opens the gate. It is used from the next key press on.

    Args
    ----
        key (int):
            Qt key.

        modifiers (int):
            Qt keyboard modifiers.
    """

    global hotkey_key, hotkey_modifiers

    hotkey_key, hotkey_modifiers = clean_hotkey(key, modifiers)

def load_hotkey() -> None:
    """
    Load Hotkey
    ===========

    Load the hotkey from the config file. Called once when Flame loads the script. The
    file is only read, never created or changed, and a config that is missing, can't be
    read or has no usable hotkey gives the default hotkey.
    """

    key = None
    modifiers = None

    try:
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, 'r') as config_file:
                config_values = json.load(config_file)

            key = config_values.get('hotkey_key')
            modifiers = config_values.get('hotkey_modifiers')
    except Exception:
        pass

    set_hotkey(key, modifiers)

def hotkey_pressed(event) -> bool:
    """
    Hotkey Pressed
    ==============

    Check if a key press is the hotkey: the same key with exactly the same modifier keys.

    Args
    ----
        event (QKeyEvent): Qt key event.

    Returns
    -------
        pressed (bool): True if the key press is the hotkey.
    """

    key = hotkey_event_key(event)

    if not key:
        return False

    if key != hotkey_key and not (key in GATE_KEYS and hotkey_key in GATE_KEYS):
        return False

    return event.modifiers().value & HOTKEY_MODIFIER_MASK == hotkey_modifiers

def find_setup_window() -> PyFlameWindow | None:
    """
    Find Setup Window
    =================

    Find an open Gate UI Setup window by its object name, so one opened before Flame reloaded
    the script is found too. Never raises: a window that was closed, and so no longer
    exists, counts as not open.

    Returns
    -------
        setup_window (PyFlameWindow | None): The open Gate UI Setup window. None if there is none.
    """

    try:
        top_level_widgets = QtWidgets.QApplication.topLevelWidgets()
    except Exception:
        return None

    for widget in top_level_widgets:
        try:
            if widget.objectName() == SETUP_WINDOW_NAME and widget.isVisible():
                return widget
        except Exception:
            continue

    return None

def setup_window_open() -> bool:
    """
    Setup Window Open
    =================

    Check if a Gate UI Setup window is open. Never raises.

    Returns
    -------
        window_open (bool): True if a Gate UI Setup window is showing.
    """

    return find_setup_window() is not None

def show_gate_ui(selection) -> None:
    """
    Show GateUI
    ===========

    Show the gate at the cursor. The gate is built once, with the tabs saved in the config,
    and reused so it pops up quickly.

    Args
    ----
        selection (list): Items selected in Flame when the menu was run.
    """

    global gate_window

    # Build gate the first time only
    if gate_window is None:
        gate_window = GateUI(load_sections(), load_ui_scale())

    gate_window.show_at_cursor()

def reset_gate_window() -> None:
    """
    Reset Gate Window
    =================

    Drop the built gate, so the next time it opens it is built again with the tabs saved
    in the config.
    """

    global gate_window

    if gate_window is not None:
        gate_window.hide()
        gate_window.deleteLater()
        gate_window = None

# ==============================================================================
# [Click Filter]
# ==============================================================================

class GateUIClickFilter(QtCore.QObject):

    def __init__(self, parent) -> None:
        """
        Init
        ====

        Create the click filter.

        Args
        ----
            parent (QObject): Object that owns the filter (the Flame application).
        """

        super().__init__(parent)

        # Count of tablet pen arrivals seen, to check that Flame passes them on
        self.pen_arrivals = 0

    def eventFilter(self, watched, event) -> bool:
        """
        Event Filter
        ============

        Close an open gate when the mouse is pressed anywhere off it or Escape is pressed,
        and open the gate on the hotkey in Batch. This sees every Qt event in Flame, so
        anything that is not a mouse press, a key press or a tablet pen coming into range is
        passed on at once.

        The gate never has keyboard focus, so Escape and the hotkey are caught here. Those two
        key presses are the only events this filter keeps from Flame.

        Args
        ----
            watched (QObject):
                Object the event was sent to.

            event (QEvent):
                Qt event.

        Returns
        -------
            handled (bool): True for an Escape press that closed the gate and for a press of the hotkey in Batch while Gate UI Setup is not open. False for everything else, so the event still reaches Flame.
        """

        event_type = event.type()

        # Tell an open gate when a tablet pen comes into range, the cursor is about to jump to it
        if event_type == QtCore.QEvent.TabletEnterProximity:
            self.pen_arrivals += 1
            if gate_window is not None and gate_window.isVisible():
                gate_window.pen_in_range()

            return False

        if event_type != QtCore.QEvent.MouseButtonPress and event_type != QtCore.QEvent.KeyPress:
            return False

        # Never let an error here break Flame's own event handling, so fail silently and pass the event on
        try:
            if event_type == QtCore.QEvent.KeyPress:

                # Escape closes an open gate and goes no further, so Flame doesn't act on it too
                if event.key() == QtCore.Qt.Key_Escape and gate_window is not None and gate_window.isVisible():
                    gate_window.hide()

                    return True

                return self.gate_key_press(watched, event)

            self.mouse_press(watched)
        except Exception:
            pass

        return False

    def gate_key_press(self, watched, event) -> bool:
        """
        Gate Key Press
        ==============

        Open the gate when the hotkey is pressed in Batch, or close it if it is already open.
        Nothing is done, and the key is passed on, while the Gate UI Setup window is open.

        Args
        ----
            watched (QObject):
                Object the event was sent to.

            event (QKeyEvent):
                Qt key event.

        Returns
        -------
            handled (bool): True if the key press was the hotkey in Batch and should go no further, otherwise False.
        """

        if not hotkey_pressed(event):
            return False

        # Key presses go to the window first, then to the widget. Handle the window one only so the gate opens once
        if not isinstance(watched, QtGui.QWindow):
            return False

        # Leave the key alone while Gate UI Setup is open, so the gate stays closed and ~ can be typed in it
        if setup_window_open():
            return False

        if flame.get_current_tab() != 'Batch':
            return False

        # Holding the key down does nothing more, and the repeats are kept from Flame too
        if event.isAutoRepeat():
            return True

        # Gate is already open, close it instead of opening it again
        if gate_window is not None and gate_window.isVisible():
            gate_window.hide()
        else:
            show_gate_ui([])

        return True

    def mouse_press(self, watched) -> None:
        """
        Mouse Press
        ===========

        Close an open gate on a press of any mouse button in any other window.

        Args
        ----
            watched (QObject): Object the event was sent to.
        """

        # Mouse events go to the window first, then to the widget. Handle the window one only
        if not isinstance(watched, QtGui.QWindow):
            return

        # A press on the gate itself is handled by the gate
        if gate_window is None or watched == gate_window.windowHandle():
            return

        if gate_window.isVisible():
            gate_window.hide()

def install_click_filter() -> None:
    """
    Install Click Filter
    ====================

    Install the gate click filter on the Flame application. Filters left by an earlier load
    of the script are removed first, so there is never more than one.
    """

    app = QtWidgets.QApplication.instance()
    if app is None:
        return

    # Remove filters from before a Rescan Python Hooks
    for old_filter in app.findChildren(QtCore.QObject, CLICK_FILTER_NAME):
        app.removeEventFilter(old_filter)
        old_filter.deleteLater()

    click_filter = GateUIClickFilter(app)
    click_filter.setObjectName(CLICK_FILTER_NAME)
    app.installEventFilter(click_filter)

# Runs when Flame loads or rescans the hooks
load_hotkey()
install_click_filter()

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'Logik',
            'hierarchy': [],
            'actions': []
        },
        {
            'name': 'Logik Portal Script Setup',
            'hierarchy': ['Logik'],
            'order': 2,
            'actions': [
                {
                    'name': 'Gate UI Setup',
                    'execute': GateUISetup,
                    'minimumVersion': '2025.2'
                }
            ]
        }
    ]
