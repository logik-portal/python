# User Batch Setups
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: User Batch Setups
Script Version: 1.10.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 03.29.22
Update Date: 11.02.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Create menus for batch setups saved to a specified folder.

    Menu's for setups will only be visible in versions of Flame that setups are compatible with.

    After saving or deleting batch setups to the chosen folder, use the Refresh Menus menu option to regenerate setup menus.

    Setup menus are automatically regenerated each time Flame starts up.

URL:

    https://logik-portal.com/scripts/user_batch_setups

Menus:

    Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> User Batch Setups: Setup

    To refresh/update menus:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> User Batch Setups: Refresh Menus

     To access batch setup menus:
        Right-click in batch -> User Batch Setups -> Setup Name

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.10.0 11.02.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Fixed the menu paths in the setup path error message and in the Menus section of this
          docstring. They now match the real menu: Logik -> Logik Portal Script Setup.
        - Fixed one unreadable batch setup stopping the menu refresh and removing the other menus.
          Unreadable setups are now skipped and listed in one message. If no setup can be read,
          the menus are left as they were.
        - Fixed two setups with the same name (for example comp.batch and comp.flare.batch) writing
          to the same menu. The first is kept and the other is skipped.
        - Fixed messages popping up at every Flame startup when the setups folder is missing or has
          no setups. These are now only printed to the console at startup.

    v1.9.0 05.25.26
        - Updated to PyFlameLib v5.3.2.

    v1.8.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v1.7.0 04.11.25
        - Updated to PyFlameLib v4.3.0.

    v1.6.0 01.03.25
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.5.0 10.01.24
        - Updated to PyFlameLib v3.2.0.

    v1.4.0 01.24.24
        - Updates to UI/PySide.

    v1.3.0 08.13.23
        - Update to PyFlameLib v2.0.0.

    v1.2.1 06.27.23
        - Updated script versioning to semantic versioning.
        - Save button in setup window now blue.
        - Pressing return closes setup window.

    v1.2 02.04.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.

    v1.1 05.31.22
        - Messages print to Flame message window - Flame 2023.1 and later.
        - Flame file browser used to select folders - Flame 2023.1 and later.`
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os
import re
import shutil
import xml.etree.ElementTree as ET

from lib.pyflame_lib_user_batch_setups import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'User Batch Setups'
SCRIPT_VERSION = 'v1.10.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

def print_action_header(action: str) -> None:

    label = f'-=[ {action} ]='
    line = label + '-' * max(2, 80 - len(label))
    colored_line = ''.join(
        f'{TextColor.BLUE.value}{ch}' if ch in '-='
        else f'{TextColor.WHITE.value}{ch}'
        for ch in line
    ) + TextColor.RESET.value
    print(colored_line)
    flame.messages.show_in_console(f'{action}', 'info')

def print_action_footer() -> None:
    print(f'{TextColor.BLUE.value}-' * 80, f'{TextColor.RESET.value}\n')

class UserSetups:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if not correct, display error message and end script
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Create/Load config
        self.settings = self.load_config()

        # Create menus folder if it doesn't already exist
        self.menu_path = os.path.join(SCRIPT_PATH, 'menus')
        if not os.path.isdir(self.menu_path):
            os.makedirs(self.menu_path)

        self.template_path = os.path.join(SCRIPT_PATH, 'assets/templates/batch_menu_template')
        if not os.path.exists(self.template_path):
            PyFlameMessageWindow(
                message=('Script templates path does not exist. Check and try again.'),
                message_type=MessageType.ERROR,
                parent=None,
                )
            pyflame.raise_value_error(
                error_message=f'Script templates path does not exist. Check and try again. Should be: {SCRIPT_PATH}/assets/templates/batch_menu_template',
                )

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
        --------
            PyFlameConfig: PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            config_values={
                'setup_path': '/',
                }
            )

        return settings

    def setup(self) -> None:
        """
        Setup
        =====

        Setup window to set path to batch setups.
        """

        def browse_dir() -> None:
            """
            Browse Directory
            ================

            Browse to directory where batch setups are saved.
            """

            batch_dir = pyflame.file_browser(
                path=self.setup_path_entry.text,
                title='Select Directory',
                select_directory=True,
                window_to_hide=[self.setup_window]
                )

            if batch_dir:
                self.setup_path_entry.text = str(batch_dir)

        def save_config():
            """
            Save Config
            ===========

            Save settings to config file.
            """

            self.settings.save_config(
                config_values={
                    'setup_path': self.setup_path_entry.text
                    }
                )

            self.setup_window.close()

            self.refresh_menus_folder()

        def close_window():

            self.setup_window.close()

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.setup_path_label = PyFlameLabel(
            text='Path to Batch Setups',
            )

        # Entry
        self.setup_path_entry = PyFlameEntry(
            text=self.settings.setup_path,
            )

        # Buttons
        self.browse_button = PyFlameButton(
            text='Browse',
            connect=browse_dir,
            )
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.setup_window.close,
            )

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.setup_window.grid_layout.addWidget(self.setup_path_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.setup_path_entry, 0, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.browse_button, 0, 4)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 2, 3)
        self.setup_window.grid_layout.addWidget(self.save_button, 2, 4)

        #-------------------------------------

        self.setup_path_entry.setFocus()

    def refresh_menus_folder(self, startup_refresh=False) -> None:
        """
        Refresh Menus Folder
        ====================

        Refresh menus folder by deleting existing menus and creating new menus for all batch setups found in batch setup path.

        Setups are read before the menus folder is cleared. Unreadable setups, and setups with the same menu name as an
        earlier setup, are skipped and listed in one message at the end.
        """

        def show_message(message: str, message_type=MessageType.INFO) -> None:
            """
            Show Message
            ============

            Show message window, or print message to the console as a warning at Flame startup.

            Args
            ----
                message (str):
                    Message to show.

                message_type (MessageType):
                    Message window type.
            """

            if startup_refresh:
                pyflame.print(message.replace('\n\n', ' '), print_type=PrintType.WARNING)
            else:
                PyFlameMessageWindow(
                    message=message,
                    message_type=message_type,
                    parent=None,
                    )

        def skipped_list() -> str:
            """
            Skipped List
            ============

            Build list of skipped setups for the end message.

            Returns
            -------
                skipped_text (str): One line per skipped setup with its reason.
            """

            return '\n'.join(f'{file_name}: {reason}' for file_name, reason in skipped_setups)

        # Check batch setup path, if path not found give error
        if not os.path.isdir(self.settings.setup_path):
            show_message('Batch setup path not found.\n\nCheck path in script setup.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> User Batch Setups: Setup')

            return

        # Check for batch setups in batch setup path, if none found give error. Ignore macOS AppleDouble (._) files
        batch_setups = sorted((f for f in os.listdir(self.settings.setup_path) if f.endswith('.batch') and not f.startswith('._')), key=str.lower)
        if not batch_setups:
            show_message('No batch setups found.\n\nNo menus to create/update.')

            return

        pyflame.print('Refreshing User Batch Menus')

        # Read every setup before clearing menus so one bad setup can't remove the other menus
        good_setups = []
        skipped_setups = []
        menu_names = {}

        for file_name in batch_setups:
            batch_name = file_name.split('.', 1)[0]
            batch_path = os.path.join(self.settings.setup_path, file_name)

            # Skip setups that would write over an earlier setup's menu. Names are compared case-insensitively for case-insensitive volumes
            if batch_name.lower() in menu_names:
                reason = f'Same menu name as {menu_names[batch_name.lower()]}'
                pyflame.print(f'Skipping {file_name}: {reason}', print_type=PrintType.WARNING)
                skipped_setups.append((file_name, reason))
                continue

            try:
                batch_version = self.get_batch_version(batch_path)
            except Exception as e:
                reason = f'Could not read setup ({e})'
                pyflame.print(f'Skipping {file_name}: {reason}', print_type=PrintType.WARNING)
                skipped_setups.append((file_name, reason))
                continue

            menu_names[batch_name.lower()] = file_name
            good_setups.append((file_name, batch_path, batch_name, batch_version))

        # Leave existing menus alone if no setups could be read
        if not good_setups:
            show_message(f'No readable batch setups found. Menus were not changed.\n\nSkipped setups:\n\n{skipped_list()}', MessageType.ERROR)

            return

        # Delete existing menus and recreate menus folder
        shutil.rmtree(self.menu_path)
        os.makedirs(self.menu_path)

        pyflame.print('Existing User Batch Menus Cleared')

        # Create new menus for all batch setups found in batch setup path
        #pyflame.print ('Generating New User Batch Menus:\n')

        print_action_header('Generating User Batch Menus')

        menus_created = 0

        for file_name, batch_path, batch_name, batch_version in good_setups:
            try:
                self.create_menu(batch_path, batch_name, batch_version)
                menus_created += 1
            except Exception as e:
                reason = f'Could not write menu ({e})'
                pyflame.print(f'Skipping {file_name}: {reason}', print_type=PrintType.WARNING)
                skipped_setups.append((file_name, reason))
        print('-' * 80, '\n')

        # Refresh python hooks
        pyflame.refresh_hooks()

        # Give user message that setup menus have been updated, listing any skipped setups
        if not menus_created:
            show_message(f'No menus could be created.\n\nSkipped setups:\n\n{skipped_list()}', MessageType.ERROR)
        elif skipped_setups:
            show_message(f'User Batch Menus Updated\n\nSkipped setups:\n\n{skipped_list()}', MessageType.ERROR)
        elif not startup_refresh:
            PyFlameMessageWindow(
                message='User Batch Menus Updated',
                parent=None,
                )
        else:
            pyflame.print('User Batch Menus Updated')

    def get_batch_version(self, batch_path: str) -> str:
        """
        Get Batch Version
        =================

        Read the Flame version a batch setup was saved with. Any .pr suffix is removed.

        Args
        ----
            batch_path (str): Path to the batch setup file.

        Returns
        -------
            batch_version (str): Flame version of the batch setup.

        Raises
        ------
            OSError:
                If the batch setup file can't be read.

            ET.ParseError:
                If the batch setup isn't valid XML.

            ValueError:
                If the batch setup has no Flame version.
        """

        # Read flame version from batch setup file
        xml_tree = ET.parse(batch_path)
        root = xml_tree.getroot()

        xml_version = root.find('.//Version')
        if xml_version is None or not xml_version.text:
            raise ValueError('Flame version not found')

        batch_version = str(xml_version.text)

        if 'pr' in batch_version:
            batch_version = batch_version.rsplit('.pr', 1)[0]

        return batch_version

    def create_menu(self, batch_path, batch_name, batch_version) -> None:
        """
        Create Menu
        ===========

        Create menu for batch with menu minimum version set to flame version.
        """

        #print (f'    {batch_name}')
        name = batch_name.replace('_', ' ').title()
        pyflame.print(f'{name}', new_line=False)

        # Create menu for batch with menu minimum version set to flame version
        # Read menu template file
        template = open(self.template_path, 'r')
        template_lines = template.read().splitlines()

        # Replace tokens in template
        token_dict = {}

        token_dict['<BatchName>'] = batch_name
        token_dict['<ScriptVersion>'] = SCRIPT_VERSION[1:]
        token_dict['<SetupPath>'] = batch_path
        token_dict['<MinFlameVersion>'] = batch_version

        # Replace tokens in menu template
        for key, value in token_dict.items():
            for line in template_lines:
                if key in line:
                    line_index = template_lines.index(line)
                    new_line = re.sub(key, value, line)
                    template_lines[line_index] = new_line

        # Write out menu for batch setup
        new_batch_script_path = os.path.join(self.menu_path, batch_name + '.py')

        out_file = open(new_batch_script_path, 'w')
        for line in template_lines:
            print(line, file=out_file)
        out_file.close()

def setup(selection):

    script = UserSetups(selection)
    script.setup()

def refresh(selection):

    script = UserSetups(selection)
    script.refresh_menus_folder()

def startup_refresh(selection):

    script = UserSetups(selection)
    script.refresh_menus_folder(startup_refresh=True)

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
                    'name': 'User Batch Setups: Setup',
                    'execute': setup,
                    'minimumVersion': '2025.1'
               },
               {
                    'name': 'User Batch Setups: Refresh Menus',
                    'execute': refresh,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def app_initialized(project_name):
    startup_refresh(project_name)
