# User Batch Setups
# Copyright (c) 2025 Michael Vaglienty
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
Script Name: User Batch Setups
Script Version: 1.8.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 03.29.22
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Create menus for batch setups saved to a specified folder.

    Menu's for setups will only be visible in versions of Flame that setups are compatible with.

    After saving or deleting batch setups to the chosen folder, use the Refresh Menus menu option to regenerate setup menus.

    Setup menus are automatically regenerated each time Flame starts up.

URL:
    https://github.com/logik-portal/python/user_batch_setups

Menus:

    Setup:
        Flame Main Menu -> pyFlame -> User Batch Setups - Setup

    To refresh/update menus:
        Flame Main Menu -> pyFlame -> User Batch Setups - Refresh Menus

     To access batch setup menus:
        Right-click in batch -> User Batch Setups -> Setup Name

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

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

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil
import xml.etree.ElementTree as ET

from lib.pyflame_lib_user_batch_setups import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'User Batch Setups'
SCRIPT_VERSION = 'v1.8.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

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
                self.setup_path_entry.text = batch_dir

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
        # [Widget Layout]
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
        """

        # Check batch setup path, if path not found give error
        if not os.path.isdir(self.settings.setup_path):
            PyFlameMessageWindow(
                message='Batch setup path not found.\n\nCheck path in script setup.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> User Setups Setup',
                parent=None,
                )
            return

        # Check for batch setups in batch setup path, if none found give error
        batch_setups = [f for f in os.listdir(self.settings.setup_path) if f.endswith('.batch')]
        if not batch_setups:
            PyFlameMessageWindow(
                message='No batch setups found.\n\nNo menus to create/update.',
                parent=None,
                )
            return

        pyflame.print('Refreshing user batch menus...')

        # Delete existing menus and recreate menus folder
        shutil.rmtree(self.menu_path)
        os.makedirs(self.menu_path)

        pyflame.print('Existing User Batch Menus Cleared')

        # Create new menus for all batch setups found in batch setup path
        pyflame.print ('Generating New User Batch Menus:\n')

        for f in os.listdir(self.settings.setup_path):
            if f.endswith('.batch'):
                self.create_menu(os.path.join(self.settings.setup_path, f), f.split('.', 1)[0])

        print ('\n')

        # Refresh python hooks
        pyflame.refresh_hooks()

        # Give user message that setup menus have been updated
        if not startup_refresh:
            PyFlameMessageWindow(
                message='User Batch Menus Updated',
                parent=None,
                )
        else:
            pyflame.print('User Batch Menus Updated')

    def create_menu(self, batch_path, batch_name) -> None:
        """
        Create Menu
        ===========

        Create menu for batch with menu minimum version set to flame version.
        """

        print (f'    {batch_name}')

        # Read flame version from batch setup file
        xml_tree = ET.parse(batch_path)
        root = xml_tree.getroot()

        xml_version = root.find('.//Version')
        batch_version = xml_version.text

        if 'pr' in batch_version:
            batch_version = batch_version.rsplit('.pr', 1)[0]

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

#-------------------------------------
# [Flame Menus]
#-------------------------------------

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
                    'minimumVersion': '2025'
               },
               {
                    'name': 'User Batch Setups: Refresh Menus',
                    'execute': refresh,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def app_initialized(project_name):
    startup_refresh(project_name)
