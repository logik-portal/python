# Script Template
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Script Template
Script Version: 5.1.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 02.09.22
Update Date: 11.03.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Flame Main Menu

Description:

    Starting point for new Flame Python scripts. Opens a sample PyFlameWindow with entries,
    menus and buttons, and saves its settings to a config file.

    The config sections can be deleted if the new script doesn't need a config file.

URL:

    https://logik-portal.com/scripts/script_template

Usage:

    Flame Main Menu -> Logik -> Logik Portal Script Setup -> Script Template

To install:

    Copy script folder into /opt/Autodesk/shared/python

    To start a new script from this template:
        1. Copy the folder and rename the folder, script_template.py and
           lib/pyflame_lib_script_template.py to the new script name.
        2. Update the import line to match: from lib.pyflame_lib_<script_name> import *
        3. Change the header comment, every docstring field, SCRIPT_NAME, SCRIPT_VERSION,
           the ScriptTemplate class, the script_template entry point and the menu name.
        4. Replace or delete the sample config settings, and reset config/config.json.
        5. Update README.md to match the new docstring.

Updates:

    v5.1.0 11.03.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Second entry now shows its saved setting instead of starting empty.
        - Closed the <small> tag in the window title.
        - Added a module-level entry point and an [Entry Points] section. The menu now calls the entry point.
        - Docstrings, imports and sections now follow the style guide.

    v5.0.1 12.18.25
        - Added license to script.

    v5.0.0 08.27.25
        - Updated to PyFlameLib v5.0.0.

    v4.1.0 04.13.25
        - Updated to PyFlameLib v4.3.0.

    v4.0.0 12.29.24
        - Updated to PyFlameLib v4.0.0.
        - Removed script path checking method. This is now handled by PyFlameLib: pyflame.verify_script_install().
        - PyFlameWindow now creates a PyFlameGridLayout by default that widgets can be added to. This should simplify the process of adding widgets to the window.
          Number of rows and columns in the grid layout can be set using the grid_layout_columns and grid_layout_rows arguments in the PyFlameWindow constructor.
          Overall and individual row height and column width can also be set from the PyFlameWindow constructor.
          Check PyFlameWindow docstring for more information.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v3.1.1 04.18.24
        - Replaced QGridLayout with PyFlameGridLayout.
        - Moved checking of script path and creating/loading of config to their own functions.

    v3.1.0 02.07.24
        - Updates to UI/PySide.
        - Updated script versioning to semantic versioning.

    v3.0 08.10.23
        - Updated for pyflame lib v2.0.0.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os

import flame
from lib.pyflame_lib_script_template import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Script Template'
SCRIPT_VERSION = 'v5.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class ScriptTemplate:

    def __init__(self, selection) -> None:
        """
        Init
        ====

        Load config settings and open the main window.

        Args
        ----
            selection (list): Items selected in Flame when the menu was run.
        """

        # Create/Load config file settings
        self.load_config()

        # Open main window
        self.main_window()

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Load config values from the config file into `self.settings`.

        If the config file doesn't exist, it's created with the default values
        from the `config_values` dictionary.
        """

        self.settings = PyFlameConfig(
            config_values={
                'setting_01': 'Some value',
                'setting_02': 'Another value',
                },
            )

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Build and show the main window for the script.
        """

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings to the config file, close the window and show a message.
            """

            # Optional example: ask before continuing. A WARNING message returns True only when Confirm is pressed.
            # if not PyFlameMessageWindow(
            #     message='Overwrite saved settings?',
            #     message_type=MessageType.WARNING,
            #     parent=self.window,
            #     ):
            #     return

            self.settings.save_config(
                config_values={
                    'setting_01': self.entry1.text,
                    'setting_02': self.entry2.text,
                    }
                )

            self.window.close()

            PyFlameMessageWindow(
                message='A really cool message goes here.',
                parent=None,
                )

        def close_window() -> None:
            """
            Close Window
            ============

            Close window without saving.
            """

            self.window.close()

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=save_config, # Save config then close window when return/enter is pressed
            escape_pressed=close_window, # Close window when escape is pressed
            grid_layout_columns=5,
            grid_layout_rows=4,
            grid_layout_adjust_column_widths={2: 50},
            parent=None,
            )

        # Labels
        self.label1 = PyFlameLabel(
            text='Enter Something',
            )
        self.label2 = PyFlameLabel(
            text='Enter Something Else',
            )
        self.menu_label = PyFlameLabel(
            text='Menu',
            )

        # Entries
        self.entry1 = PyFlameEntry(
            text=self.settings.setting_01,
            )
        self.entry2 = PyFlameEntry(
            text=self.settings.setting_02,
            )
        self.token_entry = PyFlameEntry(
            text='',
            )

        # Set Entry Tab-key Order
        self.window.tab_order = [
            self.entry1,
            self.entry2,
            self.token_entry,
            ]

        # Menu
        self.menu = PyFlameMenu(
            text='Option 1',
            menu_options=[
                'Option 1',
                'Option 2',
                'Option 3',
                ]
            )

        # Token Menu
        self.token_menu = PyFlameTokenMenu(
            token_dict={
                'token_01': 'Token 1',
                'token_02': 'Token 2',
                },
            token_dest=self.token_entry,
            )

        # Buttons
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.window.grid_layout.addWidget(self.label1, 0, 0)
        self.window.grid_layout.addWidget(self.entry1, 0, 1)

        self.window.grid_layout.addWidget(self.label2, 0, 3)
        self.window.grid_layout.addWidget(self.entry2, 0, 4)

        self.window.grid_layout.addWidget(self.menu_label, 1, 0)
        self.window.grid_layout.addWidget(self.menu, 1, 1)

        self.window.grid_layout.addWidget(self.token_entry, 1, 3)
        self.window.grid_layout.addWidget(self.token_menu, 1, 4)

        self.window.grid_layout.addWidget(self.cancel_button, 3, 3)
        self.window.grid_layout.addWidget(self.save_button, 3, 4)

        # ------------------------------------------------------------------------------

        self.entry1.set_focus()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_library(selection) -> bool:
    """
    Scope Library
    =============

    Check if the selection contains a library.

    Args
    ----
        selection (list): Items selected in Flame.

    Returns
    -------
        has_library (bool): True if any selected item is a library, otherwise False.
    """

    for item in selection:
        if isinstance(item, flame.PyLibrary):
            return True

    return False

# ==============================================================================
# [Entry Points]
# ==============================================================================

def script_template(selection) -> None:
    """
    Script Template
    ===============

    Check the script install, then open the Script Template window.

    Args
    ----
        selection (list): Items selected in Flame when the menu was run.
    """

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    ScriptTemplate(selection)

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
                    'name': 'Script Template',
                    'execute': script_template,
                    #'isVisible': scope_library, # Uncomment to show the menu only when scope_library returns True
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
