# Import Write Node
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
Script Name: Import Write Node
Script Version: 2.11.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 05.26.19
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Import open clip created by selected write node into batch schematic reel or
    shelf reel or auto-import write node image sequence when render is complete.

URL:
    https://github.com/logik-portal/python/import_write_node

Menus:

    Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Import Write Node Setup

    To import open clips:
        Right-click on write file node in batch -> Import... -> Import Open Clip to Batch
        Right-click on write file node in batch -> Import... -> Import Open Clip to Renders Reel

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.11.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v2.10.0 04.10.25
        - Updated to PyFlameLib v4.3.0.

    v2.9.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v2.8.0 09.02.24
        - Updated to PyFlameLib v3.0.0.

    v2.7.0 01.15.24
        - Updates to PySide.
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.

    v2.6 03.02.23
        - Updated config file loading/saving.
        - Updated menus for Flame 2023.2+
        - Added check to make sure script is installed in the correct location.

    v2.5 11.10.22
        - Fixed bug loading open clip when (ext) token is used in the Create Open Clip path.

    v2.4 05.30.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v2.3 04.13.22
        - Script renamed to: Import Write Node.
        - Updated UI for Flame 2023.
        - Moved UI widgets to external file.

    v2.1 09.24.21
        - Added token translation for project nickname.

    v2.0 05.25.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v1.5 09.19.20
        - Pops up message box when open clip doesn't exist.

    v1.4 07.01.20
        - Open clips can be imported to Batch Renders shelf reel - Batch group must have shelf reel called Batch Renders.
        - Added token for version name.

    v1.3 11.01.19
        - Right-click menu now appears under Import...

    v1.1 09.29.19
        - Code cleanup.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_import_write_node import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Import Write Node'
SCRIPT_VERSION = 'v2.11.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ImportWriteNode:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Create/Load config file settings.
        self.settings = self.load_config()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
        --------
            PyFlameConfig:
                PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
             config_values={
                'schematic_reel': 'Renders',
                'shelf_reel': 'Batch Renders',
                'import_after_render': False,
                'schematic_reel_import': True,
                'shelf_reel_import': True,
                'import_again': False,
                }
            )

        return settings

    def translate_write_node_path(self):

        print ('Translating write node path...')

        # Translate write node tokens
        for self.write_node in self.selection:
            media_path = str(self.write_node.media_path)[1:-1]
            print ('    media path:', media_path)
            pattern = str(self.write_node.create_clip_path)[1:-1]
            print ('    pattern:', pattern)
            project = str(flame.project.current_project.name)
            project_nickname = str(flame.project.current_project.nickname)
            batch_iteration = str(flame.batch.current_iteration.name)
            batch_name = str(flame.batch.name)[1:-1]
            #ext = str(self.write_node.format_extension)[1:-1]
            ext = ''
            name = str(self.write_node.name)[1:-1]
            shot_name = str(self.write_node.shot_name)[1:-1]

            token_dict = {
                '<project>': project,
                '<project nickname>': project_nickname,
                '<batch iteration>': batch_iteration,
                '<batch name>': batch_name,
                '<ext>': ext,
                '<name>': name,
                '<shot name>':shot_name,
                '<version name>': batch_iteration
                }

            for token, value in token_dict.items():
                pattern = pattern.replace(token, value)

            translated_path = os.path.join(media_path, pattern) + '.clip'
            print ('    Open clip translated path:', translated_path, '\n')

            return translated_path

    #-------------------------------------

    def setup(self):

        def save_config():
            """
            Save Config
            ===========

            Save settings to config file.
            """

            self.settings.save_config(
                config_values={
                    'schematic_reel': self.schematic_reel_entry.text,
                    'shelf_reel': self.shelf_reel_entry.text,
                    'import_after_render': self.enable_import_push_button.checked,
                    'schematic_reel_import': self.schematic_reel_import_push_button.checked,
                    'shelf_reel_import': self.shelf_reel_import_push_button.checked,
                    'import_again': self.import_again_push_button.checked,
                    }
                )

            self.setup_window.close()

        def import_toggle() -> None:
            """
            Import Toggle
            =============

            Enable/Disable import widgets based on Import After Render push button state.
            """

            widgets = [
                self.schematic_reel_import_push_button,
                self.shelf_reel_import_push_button,
                self.import_dest_label,
                self.clip_exists_label,
                self.import_again_push_button,
                ]

            enabled = self.enable_import_push_button.checked

            for widget in widgets:
                widget.setEnabled(enabled)

        def close_window():

            self.setup_window.close()

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns = 7,
            grid_layout_rows = 7,
            grid_layout_adjust_column_widths={3: 50},
            parent=None,
            )

        # Labels
        self.import_settings_label = PyFlameLabel(
            text='Import Destination Reels',
            style=Style.UNDERLINE,
            )
        self.auto_import_options_label = PyFlameLabel(
            text='Write File Image Sequence Automatic Import Options',
            style=Style.UNDERLINE,
            )
        self.schematic_reel_label = PyFlameLabel(
            text='Schematic Reel Name',
            )
        self.batch_shelf_label = PyFlameLabel(
            text='Batch Shelf Name',
            )
        self.import_dest_label = PyFlameLabel(
            text='Import Destination',
            )
        self.clip_exists_label = PyFlameLabel(
            text='If clip exists in dest',
            )

        # Entries
        self.schematic_reel_entry = PyFlameEntry(
            text=self.settings.schematic_reel,
            )
        self.shelf_reel_entry = PyFlameEntry(
            text=self.settings.shelf_reel,
            )

        # Push Buttons
        self.enable_import_push_button = PyFlamePushButton(
            text='Enable Import',
            checked=self.settings.import_after_render,
            connect=import_toggle,
            )
        self.schematic_reel_import_push_button = PyFlamePushButton(
            text='Schematic Reel',
            checked=self.settings.schematic_reel_import,
            )
        self.shelf_reel_import_push_button = PyFlamePushButton(
            text='Shelf Reel',
            checked=self.settings.shelf_reel_import,
            )
        self.import_again_push_button = PyFlamePushButton(
            text='Import Again',
            checked=self.settings.import_again,
            )

        #  Buttons
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

        self.setup_window.grid_layout.addWidget(self.import_settings_label, 0 ,0, 1, 3)

        self.setup_window.grid_layout.addWidget(self.schematic_reel_label, 1 ,0)
        self.setup_window.grid_layout.addWidget(self.schematic_reel_entry, 1, 1, 1, 2)

        self.setup_window.grid_layout.addWidget(self.batch_shelf_label, 2 ,0)
        self.setup_window.grid_layout.addWidget(self.shelf_reel_entry, 2 ,1, 1, 2)

        self.setup_window.grid_layout.addWidget(self.auto_import_options_label, 0 ,4, 1, 4)

        self.setup_window.grid_layout.addWidget(self.enable_import_push_button, 1 ,4)

        self.setup_window.grid_layout.addWidget(self.import_dest_label, 1 ,5)

        self.setup_window.grid_layout.addWidget(self.schematic_reel_import_push_button, 1 ,6)
        self.setup_window.grid_layout.addWidget(self.shelf_reel_import_push_button, 2 ,6)

        self.setup_window.grid_layout.addWidget(self.clip_exists_label, 4 ,5)
        self.setup_window.grid_layout.addWidget(self.import_again_push_button, 4 ,6)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 6, 5)
        self.setup_window.grid_layout.addWidget(self.save_button, 6, 6)

        #-------------------------------------

        # Toggle import widgets
        import_toggle()

        # Set focus to schematic reel entry
        self.schematic_reel_entry.set_focus()

        # Set tab-key order
        self.setup_window.tab_order = [
            self.schematic_reel_entry,
            self.shelf_reel_entry,
            ]

    def import_to_schematic_reel(self):
        """
        Import To Schematic Reel
        ========================

        Import open clip to batch schematic reel.
        """

        open_clip_path = self.translate_write_node_path()

        if not os.path.isfile(open_clip_path):
            PyFlameMessageWindow(
                message='Open clip not found\n\nWrite node export path:\n\n' + open_clip_path,
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        self.create_schematic_reel()

        self.import_schematic_reel(open_clip_path)

    def import_to_shelf_reel(self):
        """
        Import To Shelf Reel
        ====================

        Import open clip to batch shelf reel.
        """

        open_clip_path = self.translate_write_node_path()

        if not os.path.isfile(open_clip_path):
            PyFlameMessageWindow(
                message='Open clip not found',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        self.create_shelf_reel()

        self.import_shelf_reel(open_clip_path)

    def post_render_import(self):
        """
        Post Render Import
        ==================

        Import write node image sequence to schematic/shelf reel after render is complete.
        """

        if self.settings.import_after_render:

            image_seq_path = os.path.join(self.selection["exportPath"], self.selection["resolvedPath"])

            clip_name = image_seq_path.rsplit('/', 1)[1]
            clip_name = clip_name.rsplit('.', 2)[0]

            # Import image seq to schematic/shelf reel if Import After Render is selected in Setup
            # If Import Again is selected, import clip again
            # If not then check if clip is already imported to reel, if not, import

            # Import to schematic reel
            if self.settings.schematic_reel_import:
                self.create_schematic_reel()

                if self.settings.import_again:
                    self.import_schematic_reel(image_seq_path)
                else:
                    if not [clip for clip in self.schematic_reel_for_import.clips if clip.name == clip_name]:
                        self.import_schematic_reel(image_seq_path)

            # Import to shelf reel
            if self.settings.shelf_reel_import:
                self.create_shelf_reel()

                # Import to shelf reel
                if self.settings.import_again:
                    self.import_shelf_reel(image_seq_path)
                else:
                    if not [clip for clip in self.shelf_reel_for_import.clips if clip.name == clip_name]:
                        self.import_shelf_reel(image_seq_path)

            pyflame.print('Imported write node image sequence.', text_color=TextColor.GREEN)

        else:
            pyflame.print('Import write node not enabled. Nothing Imported.', print_type=PrintType.ERROR)

    #-------------------------------------

    def create_schematic_reel(self):
        """
        Create Schematic Reel
        =====================

        Create open clip schematic reel if it doesn't exist.
        """

        if self.settings.schematic_reel not in [reel.name for reel in flame.batch.reels]:
            self.schematic_reel_for_import = flame.batch.create_reel(self.settings.schematic_reel)
        else:
            self.schematic_reel_for_import = [reel for reel in flame.batch.reels if reel.name == self.settings.schematic_reel][0]

    def create_shelf_reel(self):
        """
        Create Shelf Reel
        =================

        Create batch renders shelf reel if it doesn't exist.
        """

        if self.settings.shelf_reel not in [reel.name for reel in flame.batch.shelf_reels]:
            self.shelf_reel_for_import = flame.batch.create_shelf_reel(self.settings.shelf_reel)
        else:
            self.shelf_reel_for_import = [reel for reel in flame.batch.shelf_reels if reel.name == self.settings.shelf_reel][0]

    def import_schematic_reel(self, path):
        """
        Import Schematic Reel
        =====================

        Import to schematic reel.
        """

        flame.batch.import_clip(path, self.settings.schematic_reel)

    def import_shelf_reel(self, path):
        """
        Import Shelf Reel
        =================

        Import to shelf reel.
        """

        flame.import_clips(path, self.shelf_reel_for_import)

#-------------------------------------

def schematic_import(selection):

    script = ImportWriteNode(selection)
    script.import_to_schematic_reel()

    pyflame.print('Open clip imported.', text_color=TextColor.GREEN)

def shelf_import(selection):

    script = ImportWriteNode(selection)
    script.import_to_shelf_reel()

    pyflame.print('Open clip imported.', text_color=TextColor.GREEN)

def setup(selection):

    script = ImportWriteNode(selection)
    script.setup()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_write_node(selection):

    for item in selection:
        if item.type == 'Write File':
            return True
    return False

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
                    'name': 'Import Write Node Setup',
                    'execute': setup,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Import...',
            'actions': [
                {
                    'name': 'Import Open Clip to Batch',
                    'isVisible': scope_write_node,
                    'execute': schematic_import,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Import Open Clip to Renders Reel',
                    'isVisible': scope_write_node,
                    'execute': shelf_import,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

def batch_export_end(info, userData, *args, **kwargs):

    script = ImportWriteNode(info)
    script.post_render_import()
