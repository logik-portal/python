# Create Shot Folders
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
Script Name: Create Shot Folders
Script Version: 5.5.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 06.09.18
Update Date: 02.18.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create shot folders in the Media Panel and/or file system based on folder structure templates.

    Custom folder structure templates can be set up in the script setup window.

URL:
    https://github.com/logik-portal/python/create_shot_folders

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Create Shot Folders Setup

    Media Panel:
        Right-click in Media Panel -> Create Shot Folders
        Right-click on selected clips in Media Panel -> Create Shot Folders (From Clips)

    MediaHub:
        Right-click on selected folder in MediaHub -> Create Shot Folders

    Timeline:
        Right-click on selected timeline segments in Media Panel -> Create Shot Folders (From Segments)

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v5.5.0 02.18.26
        - Create shot folders for selected clips in Media Panel.
        - Create shot folders for selected timeline segments.
        - Set folder location for selected clips or segments for shot folders. (Setup Window)
        - Create shot folders in MediaHub at selected folder location.
        - Export clips to file system folders.
        - Set location of plate export folders in file system folders. (Setup Window)
        - Set render type. Foreground or Background.

    v5.4.0 08.27.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes out of windows.
        - Fixed: Reveal in Finder button was not disabled when File System Folders button was unchecked.

    v5.3.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v5.2.0 01.02.25
        - Updated to PyFlameLib v4.1.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2025.1+.

    v5.1.0 10.01.24
        - Updated to PyFlameLib v3.2.0.

    v5.0.1 09.15.24
        - Shot Folder top level item in folder tree can no longer be edited.

    v5.0.0 09.09.24
        - Split off from Create Shot script.
        - Updated to PyFlameLib v3.0.0.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re
from functools import partial

import flame
from lib.pyflame_lib_create_shot_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Create Shot Folders'
SCRIPT_VERSION = 'v5.5.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

def load_config() -> PyFlameConfig:
    """
    Load Config
    ===========

    Create/Load config values from config file.
    If config file does not exist, create it using config_values as default values otherwise load config values from file.
    Default values should be set in the config_values dictionary.

    Returns
    -------
        PyFlameConfig:
            PyFlameConfig object with config values.
    """

    settings = PyFlameConfig(
        config_values={
            'shot_name': 'PYT_<ShotNum####>',
            'number_of_shots': 10,
            'starting_shot': 10,
            'shot_increments': 10,
            'create_folders': True,
            'create_system_folders': False,
            'reveal_in_finder': False,
            'folders': {
                'Shot_Folder': {
                    'Elements': {},
                    'Plates': {},
                    'Ref': {},
                    'Renders': {}
                    }
                },
            'file_system_folders': {
                'Shot_Folder': {
                    'Elements': {},
                    'Plates': {},
                    'Ref': {},
                    'Renders': {}
                    }
                },
            'file_system_folders_path': '/Volumes/Projects/<ProjectName>/Shots/<SeqName>',
            'plate_folder': 'Shot_Folder/Plates',
            'plate_export_folder': 'Shot_Folder/Plates',
            'export_preset_type': 'User',
            'export_preset': '',
            'clips_to_folders': False,
            'export_clips': False,
            'foreground_export': False,
            }
        )

    return settings

class CreateShotFolders():

    def __init__(self, selection, mode) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        # Initialize variables
        self.shot_list = []
        self.mode = mode
        #print('Mode:', self.mode)

        # Get selected item(s) and validate selection. If selection is not valid, exit script.
        selection_valid = self.get_selection(selection)
        if not selection_valid:
            return

        # Open main window
        self.main_window()

    def get_selection(self, selection) -> bool:
        """
        Get Selection
        =============

        Get selection from Media Panel or MediaHub.

        Returns
        -------
            bool:
                True if selection is valid, False if not.
        """

        print('Selection: ', selection)
        print('Flame Tab:', flame.get_current_tab())

        if selection == None:
            return True

        # If mode is segments, build selection of video segments only, check for shot names, then build shot list.
        if self.mode == 'segments':
            for item in selection:
                print(item.type)
            self.selection = [item for item in selection if isinstance(item, flame.PySegment) and item.type == 'Video Segment']
            print('--------------------------------')
            for item in self.selection:
                print(item.type)
            print('--------------------------------')

            if self.selection == []:
                PyFlameMessageWindow(
                    message='Must have a Segment selected to create shot folders',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return False

            for item in self.selection:
                print('Name:', item.name)
                print('Shot Name:', item.shot_name)
                if item.shot_name == '':
                    PyFlameMessageWindow(
                        message='All selected segments must have a Shot Name assigned.',
                        message_type=MessageType.ERROR,
                        parent=None,
                        )
                    return False

            for item in self.selection:
                if str(item.shot_name)[1:-1] not in self.shot_list:
                    self.shot_list.append(str(item.shot_name)[1:-1])

            self.shot_list.sort()

            print('Shot List:', self.shot_list)

            return True

        # If no folder in MediaHub is selected, give error
        if flame.get_current_tab() == 'MediaHub' and selection == ():
            PyFlameMessageWindow(
                message='Must have a folder selected in MediaHub to create shot folders',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

        # If a folder or library is in selection, set selection to it and create shot folders in the folder or library.
        for item in selection:
            if isinstance(item, (flame.PyFolder, flame.PyLibrary)):
                self.selection = item
                return True

        # If all items in a selection are clips
        if all(isinstance(item, flame.PyClip) for item in selection):
            self.selection = selection
            # Make sure all clips have a shot name assigned. If not, give error.
            for item in self.selection:
                if item.shot_name == '':
                    PyFlameMessageWindow(
                        message='All selected clips must have a Shot Name assigned.',
                        message_type=MessageType.ERROR,
                        parent=None,
                        )
                    return False

            for item in self.selection:
                if str(item.shot_name)[1:-1] not in self.shot_list:
                    self.shot_list.append(str(item.shot_name)[1:-1])

            self.shot_list.sort()

            return True

        # If Media Hub Folder is selected, set file system path to Media Hub Folder path.
        if isinstance(selection[0], (flame.PyMediaHubFilesFolder)):
            self.selection = selection[0]
            self.settings.file_system_folders_path = self.selection.path
            self.settings.create_system_folders = True
            print('Media Hub Folder found!')
            return True

        return False

    def main_window(self) -> None:

        def create_folders_toggle():
            """
            Create Folders Toggle
            =====================

            If Create Folders button is checked, enable Clips to Folders button.
            """

            if self.create_folders_push_button.checked and self.mode == 'empty':
                self.clips_to_folders_push_button.enabled = False
            elif self.create_folders_push_button.checked and self.mode == 'clips' or self.mode == 'segments':
                self.clips_to_folders_push_button.enabled = True
            elif not self.create_folders_push_button.checked:
                self.clips_to_folders_push_button.enabled = False

        def clips_to_folders_toggle():
            """
            Clips to Folders Toggle
            =======================

            If clips in the media panel are selected and Folders button is checked, enable Clips to Folders button.
            """

            if (self.mode == 'clips' or self.mode == 'segments') and self.create_folders_push_button.checked:
                self.clips_to_folders_push_button.enabled = True
            else:
                self.clips_to_folders_push_button.enabled = False

        #-------------------------------------

        def file_system_toggle() -> None:
            """
            File System Toggle
            =================

            If File System Folders button is checked, enable Export Clips and Reveal in Finder buttons.
            """

            if self.create_file_system_folders_push_button.checked:
                self.export_clips_push_button.enabled = True
                self.reveal_in_finder_push_button.enabled = True
                self.file_system_folder_path_label.enabled = True
                self.file_system_path_entry.enabled = True
            else:
                self.export_clips_push_button.enabled = False
                self.reveal_in_finder_push_button.enabled = False
                self.file_system_folder_path_label.enabled = False
                self.file_system_path_entry.enabled = False

            if self.mode == 'empty':
                self.export_clips_push_button.enabled = False
                self.foreground_export_push_button.enabled = False

        def export_clips_toggle():
            """
            Export Clips Toggle
            ===================

            If Export Clips button is checked, enable Export Preset Type and Export Preset menus.
            """

            if self.mode == 'empty':
                self.export_preset_type_label.enabled = False
                self.export_preset_type_menu.enabled = False
                self.export_preset_menu.enabled = False
                self.foreground_export_push_button.enabled = False
                self.file_system_plate_export_folder_label.enabled = False
                self.file_system_plate_export_folder_entry.enabled = False
            else:
                if self.export_clips_push_button.checked:
                    self.export_preset_type_label.enabled = True
                    self.export_preset_type_menu.enabled = True
                    self.export_preset_menu.enabled = True
                    self.foreground_export_push_button.enabled = True
                    self.file_system_plate_export_folder_label.enabled = True
                    self.file_system_plate_export_folder_entry.enabled = True
                else:
                    self.export_preset_type_label.enabled = False
                    self.export_preset_type_menu.enabled = False
                    self.export_preset_menu.enabled = False
                    self.foreground_export_push_button.enabled = False
                    self.file_system_plate_export_folder_label.enabled = False
                    self.file_system_plate_export_folder_entry.enabled = False

        def clip_selection_toggle():
            """
            Clip Selection Toggle
            ====================

            If clips in the media panel are selected, update shot name entry to show shot list and disable shot name entry and token menu.
            """

            if self.mode == 'clips' or self.mode == 'segments':
                self.shot_name_entry.text = ', '.join(self.shot_list)
                self.shot_name_entry.enabled = False
                self.shot_name_token_menu.enabled = False

        #-------------------------------------

        def get_export_preset_list():
            """
            Get Export Preset List
            ======================

            Get list of export presets from Flame and update export preset menu.
            """

            # Get preset directories
            if self.export_preset_type_menu.text == 'User':
                movie_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.User, flame.PyExporter.PresetType.Movie)
                file_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.User, flame.PyExporter.PresetType.Image_Sequence)
            elif self.export_preset_type_menu.text == 'Shared':
                movie_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.Shared, flame.PyExporter.PresetType.Movie)
                file_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.Shared, flame.PyExporter.PresetType.Image_Sequence)
            elif self.export_preset_type_menu.text == 'Project':
                movie_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.Project, flame.PyExporter.PresetType.Movie)
                file_preset_dir = flame.PyExporter.get_presets_dir(flame.PyExporter.PresetVisibility.Project, flame.PyExporter.PresetType.Image_Sequence)

            # Get movie preset list adding 'Movie: ' to beginning of preset name
            if os.path.isdir(movie_preset_dir):
                movie_preset_list = ['Movie: ' + preset[:-4] for preset in os.listdir(movie_preset_dir) if preset.endswith('.xml')]
            else:
                movie_preset_list = []

            # Get file preset list adding 'Image Sequence: ' to beginning of preset name
            if os.path.isdir(file_preset_dir):
                file_preset_list = ['Image Sequence: ' + preset[:-4] for preset in os.listdir(file_preset_dir) if preset.endswith('.xml')]
            else:
                file_preset_list = []

            # Combine movie and file preset lists
            preset_list = movie_preset_list + file_preset_list
            print('Preset List:', preset_list)

            if not preset_list:
                self.export_preset_menu.menu_options = []
            else:
                self.export_preset_menu.menu_options = preset_list

            self.export_preset_menu.refresh_menu()

            self.preset_list = preset_list

        def update_export_preset_menu():
            """
            Update Export Preset Menu
            =========================

            Get list of export presets and update export preset menu.
            """

            get_export_preset_list()

            if self.preset_list:
                self.export_preset_menu.update_menu(
                    text=self.preset_list[0],
                    menu_options=self.preset_list,
                    )
            else:
                self.export_preset_menu.update_menu(
                    text='',
                    menu_options=[],
                    )

        def validate_export_preset():
            """
            Validate Export Preset
            ======================

            Ensure the saved export preset exists on the file system. If not,
            default to the first preset in the export_preset_type location, or
            leave blank if none exist.
            """

            if self.settings.export_preset and self.settings.export_preset not in self.preset_list:
                if self.preset_list:
                    self.export_preset_menu.update_menu(
                        text=self.preset_list[0],
                        menu_options=self.preset_list,
                    )
                    preset_msg = f'Saved export preset not found:\n\n{self.settings.export_preset}\n\n' if self.settings.export_preset else 'No export preset was set. '
                    PyFlameMessageWindow(
                        message=f'{preset_msg}Using first available preset.',
                        message_type=MessageType.WARNING,
                        parent=self.window,
                    )
                else:
                    self.export_preset_menu.update_menu(
                        text='',
                        menu_options=[],
                    )
                    preset_msg = f'Saved export preset not found:\n\n{self.settings.export_preset}\n\n' if self.settings.export_preset else ''
                    PyFlameMessageWindow(
                        message=f'{preset_msg}No presets available in {self.export_preset_type_menu.text} location.\n\nSelect a different Preset Type or save a preset in Flame.',
                        message_type=MessageType.WARNING,
                        parent=self.window,
                    )

        def update_shot_name_entry():
            """
            Update Shot Name Entry
            =====================

            Check shot name entry field and enable/disable sliders based on entry. Also update file system path field.
            """

            if re.search('<ShotNum#*>', self.shot_name_entry.text):
                self.num_of_shots_slider.enabled = True
                self.num_shots_label.enabled = True
                self.start_shot_num_slider.enabled = True
                self.start_shot_num_label.enabled = True
                self.shot_increment_label.enabled = True
                self.shot_increment_slider.enabled = True
            elif '[' in self.shot_name_entry.text and ']' in self.shot_name_entry.text and re.search(r'\d-\d', self.shot_name_entry.text):
                self.num_of_shots_slider.enabled = False
                self.num_shots_label.enabled = False
                self.start_shot_num_slider.enabled = False
                self.start_shot_num_label.enabled = False
                self.shot_increment_label.enabled = True
                self.shot_increment_slider.enabled = True
            else:
                self.num_of_shots_slider.enabled = False
                self.num_shots_label.enabled = False
                self.start_shot_num_slider.enabled = False
                self.start_shot_num_label.enabled = False
                self.shot_increment_label.enabled = False
                self.shot_increment_slider.enabled = False

            self.file_system_path_entry.setText(self.translate_file_system_path(self.settings.file_system_folders_path))

        def close_window():
            """
            Close Window
            ============

            Close main window.
            """

            self.window.close()

        def create():
            """
            Create Shot Folders
            ==================

            Create shot folders.
            """

            self.window.close()

            self.create_shot_folders()

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=create,
            escape_pressed=close_window,
            grid_layout_columns=7,
            grid_layout_rows=11,
            parent=None,
            )

        # Labels
        self.shot_settings_label = PyFlameLabel(
            text='Shot Folder Settings',
            style=Style.UNDERLINE,
            )
        self.create_label = PyFlameLabel(
            text='Create',
            style=Style.UNDERLINE,
            )
        self.shot_name_label = PyFlameLabel(
            text='Shot Name Pattern',
            )
        self.num_shots_label = PyFlameLabel(
            text='Number of Shots',
            )
        self.start_shot_num_label = PyFlameLabel(
            text='Starting Shot',
            )
        self.shot_increment_label = PyFlameLabel(
            text='Shot Increments',
            )
        self.file_system_folder_path_label = PyFlameLabel(
            text='File System Path',
            )
        self.file_system_plate_export_folder_label = PyFlameLabel(
            text='Export Folder',
            )
        self.export_preset_type_label = PyFlameLabel(
            text='Export Preset',
            )

        # Entries
        self.shot_name_entry = PyFlameEntry(
            text=self.settings.shot_name,
            text_changed=update_shot_name_entry,
            )
        self.file_system_plate_export_folder_entry = PyFlameEntry(
            text=self.settings.plate_export_folder,
            read_only=True,
            )
        self.file_system_path_entry = PyFlameEntry(
            text=self.settings.file_system_folders_path,
            read_only=True,
            )

        # Sliders
        self.num_of_shots_slider = PyFlameSlider(
            min_value=1,
            max_value=1000,
            start_value=self.settings.number_of_shots,
            )
        self.start_shot_num_slider = PyFlameSlider(
            min_value=1,
            max_value=10000,
            start_value=self.settings.starting_shot,
            )
        self.shot_increment_slider = PyFlameSlider(
            min_value=1,
            max_value=100,
            start_value=self.settings.shot_increments,
            )

        # Token Menu
        self.shot_name_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict={
                'Shot Number': '<ShotNum####>',
                'Shot List': '<ShotNum[0010, 0020, 0050]>',
                'Shot Range': '<ShotNum[0010, 0020, 0050-0090]>',
                },
            token_dest=self.shot_name_entry,
            )

        # Menus
        self.export_preset_type_menu = PyFlameMenu(
            text=self.settings.export_preset_type,
            menu_options=[
                'User',
                'Project',
                'Shared',
                ],
            connect=update_export_preset_menu,
            )
        self.export_preset_menu = PyFlameMenu(
            text=self.settings.export_preset,
            menu_options=[],
            )

        # Push Buttons
        self.create_folders_push_button = PyFlamePushButton(
            text='Folders',
            checked=self.settings.create_folders,
            connect=create_folders_toggle,
            )
        self.clips_to_folders_push_button = PyFlamePushButton(
            text='Clips to Folders',
            checked=self.settings.clips_to_folders,
            )
        self.create_file_system_folders_push_button = PyFlamePushButton(
            text='File System Folders',
            checked=self.settings.create_system_folders,
            connect=file_system_toggle,
            )
        self.reveal_in_finder_push_button = PyFlamePushButton(
            text='Reveal in Finder',
            checked=self.settings.reveal_in_finder,
            )
        self.export_clips_push_button = PyFlamePushButton(
            text='Export Clips',
            checked=self.settings.export_clips,
            connect=export_clips_toggle,
            )
        self.foreground_export_push_button = PyFlamePushButton(
            text='Foreground Export',
            checked=self.settings.foreground_export,
            )

        # Buttons
        create_button = PyFlameButton(
            text='Create',
            connect=create,
            color=Color.BLUE,
            )
        cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.shot_settings_label, 0, 0, 1, 5)

        self.window.grid_layout.addWidget(self.shot_name_label, 1, 0)
        self.window.grid_layout.addWidget(self.shot_name_entry, 1, 1, 1, 3)
        self.window.grid_layout.addWidget(self.shot_name_token_menu, 1, 4)

        self.window.grid_layout.addWidget(self.shot_increment_label, 2, 0)
        self.window.grid_layout.addWidget(self.shot_increment_slider, 2, 1)

        self.window.grid_layout.addWidget(self.num_shots_label, 3, 0)
        self.window.grid_layout.addWidget(self.num_of_shots_slider, 3, 1)

        self.window.grid_layout.addWidget(self.start_shot_num_label, 4, 0)
        self.window.grid_layout.addWidget(self.start_shot_num_slider, 4, 1)

        self.window.grid_layout.addWidget(self.create_label, 0, 6)
        self.window.grid_layout.addWidget(self.create_folders_push_button, 1, 6)
        self.window.grid_layout.addWidget(self.clips_to_folders_push_button, 2, 6)

        self.window.grid_layout.addWidget(self.create_file_system_folders_push_button, 4, 6)
        self.window.grid_layout.addWidget(self.reveal_in_finder_push_button, 5, 6)
        self.window.grid_layout.addWidget(self.export_clips_push_button, 6, 6)
        self.window.grid_layout.addWidget(self.foreground_export_push_button, 7, 6)

        self.window.grid_layout.addWidget(self.file_system_folder_path_label, 6, 0)
        self.window.grid_layout.addWidget(self.file_system_path_entry, 6, 1, 1, 4)

        self.window.grid_layout.addWidget(self.file_system_plate_export_folder_label, 7, 0)
        self.window.grid_layout.addWidget(self.file_system_plate_export_folder_entry, 7, 1)

        self.window.grid_layout.addWidget(self.export_preset_type_label, 8, 0)
        self.window.grid_layout.addWidget(self.export_preset_type_menu, 8, 1)
        self.window.grid_layout.addWidget(self.export_preset_menu, 8, 2, 1, 3)

        self.window.grid_layout.addWidget(cancel_button, 10, 5)
        self.window.grid_layout.addWidget(create_button, 10, 6)

        #-------------------------------------
        # [Update UI]
        #-------------------------------------

        update_shot_name_entry() # Update shot name entry and enable/disable sliders based on entry. Also update file system path field.
        export_clips_toggle() # Export Clips push button enabled/disabled based on Export Clips push button
        clips_to_folders_toggle() # Clips to Folders push button enabled/disabled based on Folders push button
        file_system_toggle() # Reveal in Finder push button enabled/disabled based on File System Folders push button
        clip_selection_toggle() # If clips in the media panel are selected, update shot name entry to show shot list and disable shot name entry and token menu
        get_export_preset_list() # Update export preset menu with list of export presets.
        validate_export_preset() # Ensure saved preset exists on file system; default to first or blank.

        self.shot_name_entry.setFocus()
        self.translate_file_system_path(path=self.settings.file_system_folders_path)

    def save_settings(self) -> bool:
        """
        Save Settings
        =============

        Check UI settings and save to config file.

        Returns
        -------
            bool:
                True if settings are valid and saved, False if not.
        """

        # Check that at least on shot creation type is selection
        if not any ([self.create_folders_push_button.checked, self.create_file_system_folders_push_button.checked]):
            PyFlameMessageWindow(
                message='Select at least one shot type to create.\n\nFolders or File System Folders.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

        # Check shot name field
        if self.shot_name_entry.text == '':
            PyFlameMessageWindow(
                message=(
                    'Enter shot name pattern.\n\n'
                    'Examples\n\n'
                    '    PYT_<ShotNum####>\n'
                    '    PYT_<ShotNum####>\n'
                    '    PYT_<ShotNum[0010, 0020, 0050-0090]>\n'
                    ),
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

        # Save settings
        if self.mode == 'clips' or self.mode == 'segments':
            self.settings.save_config(
                {
                    'create_folders': self.create_folders_push_button.checked,
                    'create_system_folders': self.create_file_system_folders_push_button.checked,
                    'reveal_in_finder': self.reveal_in_finder_push_button.checked,
                    'export_preset_type': self.export_preset_type_menu.text,
                    'export_preset': self.export_preset_menu.text,
                    'clips_to_folders': self.clips_to_folders_push_button.checked,
                    'export_clips': self.export_clips_push_button.checked,
                    'export_preset_type': self.export_preset_type_menu.text,
                    'export_preset': self.export_preset_menu.text,
                    'foreground_export': self.foreground_export_push_button.checked,
                }
            )
        else:
            self.settings.save_config(
                    {
                        'shot_name': self.shot_name_entry.text,
                        'number_of_shots': self.num_of_shots_slider.value,
                        'starting_shot': self.start_shot_num_slider.value,
                        'shot_increments': self.shot_increment_slider.value,
                        'create_folders': self.create_folders_push_button.checked,
                        'create_system_folders': self.create_file_system_folders_push_button.checked,
                        'reveal_in_finder': self.reveal_in_finder_push_button.checked,
                        'export_preset_type': self.export_preset_type_menu.text,
                        'export_preset': self.export_preset_menu.text,
                    }
                )

        return True

    def translate_file_system_path(self, path) -> str:
        """
        Translate File System Path
        ==========================

        Translate file system path using tokens. Updates the file_system_path_field with the translated path
        and returns the translated path.

        Args
        ----
            path (str):
                The file system path to translate.

        Returns
        -------
            path (str):
                The translated file system path.
        """

        def extract_sequence_name(text):

            match = re.match(r'([a-zA-Z0-9_]+)(?=_*<ShotNum#*>)', text)
            if not match:
                match = re.match(r'([a-zA-Z0-9_]+?)(?=(_*\d+))', text)
            if match:
                return match.group(1).rstrip('_')
            else:
                return ''  # Handle the case where no match is found

        path = pyflame.resolve_tokens(path)

        if '<SeqName>' in path or '<SEQNAME>' in path:
            seq_name = extract_sequence_name(self.shot_name_entry.text)
            if '<SeqName>' in path:
                path = re.sub('<SeqName>', seq_name, path)
            if '<SEQNAME>' in path:
                seq_name_caps = seq_name.upper()
                path = re.sub('<SEQNAME>', seq_name_caps, path)

        self.file_system_path_entry.setText(path)

        return path

    def create_shot_list(self):
        """
        Create Shot List
        =================

        Generate a list of shot names based on UI settings.

        This function processes a template shot name, which can include a sequence token
        (<ShotNum###>, <ShotNum[0010, 0020, 0050-0090]>, or <ShotNum> by itself) and/or a range specified in brackets
        (e.g., prefix[0010, 0020, 0050-0090]). It returns a list of shot names by expanding the sequence and/or range.

        Returns
        -------
            shot_list (list):
                A list of generated shot names based on the provided settings.

        Notes
        -----
            - If the shot_name contains a <ShotNum###> token, it will be replaced with sequentially
            incremented numbers, padded according to the number of # characters.
            - If the shot_name contains a <ShotNum[0010, 0020, 0030-0090]> token, the function will generate
            shot names for each specified number and range within the token. The numbers can be individual values
            (e.g., 0010, 0020) or ranges (e.g., 0030-0090). The function handles both types and generates
            the corresponding shot names.
            - If the shot_name contains a <ShotNum> token by itself, it will generate shot names with 4-digit padding.
            - If the shot_name contains a range in brackets outside of the <ShotNum> token (e.g., prefix[0010, 0020, 0050-0090]),
            the function will generate shot names for each specified number and range within the brackets.
            - The function supports padding of shot numbers with leading zeros. The padding length is determined
            by the length of the numbers within the range or sequence.
            - If neither the <ShotNum> token nor a range in brackets is present, the function will return a single
            shot name as specified in the shot_name.

        Examples
        --------
            For shot_name = "PYT_<ShotNum###>", starting_shot = 10, number_of_shots = 5, shot_increments = 10,
            the function will return:
            ["PYT_0010", "PYT_0020", "PYT_0030", "PYT_0040", "PYT_0050"]

            For shot_name = "PYT_<ShotNum[0010, 0020, 0030-0050]>", and shot_increments = 10,
            the function will return:
            ["PYT_0010", "PYT_0020", "PYT_0030", "PYT_0040", "PYT_0050"]

            For shot_name = "Shot_[0010, 0020, 0030-0050]", and shot_increments = 10,
            the function will return:
            ["Shot_0010", "Shot_0020", "Shot_0030", "Shot_0040", "Shot_0050"]

            For shot_name = "PYT_<ShotNum>", starting_shot = 10, number_of_shots = 5, shot_increments = 10,
            the function will return:
            ["PYT_0010", "PYT_0020", "PYT_0030", "PYT_0040", "PYT_0050"]

            For shot_name = "PYT_0010", the function will return:
            ["PYT_0010"]
        """

        pyflame.print('Creating shot list...')

        if self.mode == 'clips' or self.mode == 'segments':
            return self.shot_list

        # Initialize shot name list
        shot_list = []

        # Extract <ShotNum> token with brackets
        shot_num_match = re.search(r'<ShotNum\[([0-9, \-]+)\]>', self.settings.shot_name)
        if shot_num_match:
            shot_sequence = shot_num_match.group(1).replace(' ', '')
            shots = shot_sequence.split(',')
            shot_name_prefix = self.settings.shot_name.split('<ShotNum', 1)[0]
            shot_name_suffix = self.settings.shot_name.split('>', 1)[1]

            # Generate shot names from sequence
            for shot in shots:
                if '-' in shot:
                    start, end = shot.split('-')
                    start, end = int(start.lstrip('0')), int(end.lstrip('0'))
                    padding = len(shot.split('-')[0])

                    for n in range(start, end + 1, self.settings.shot_increments):
                        shot_name = shot_name_prefix + str(n).zfill(padding) + shot_name_suffix
                        shot_list.append(shot_name)
                else:
                    shot_list.append(shot_name_prefix + shot + shot_name_suffix)
        else:
            # Check for <ShotNum> token with or without padding
            shot_padding_match = re.search(r'<ShotNum#+>|<ShotNum>', self.settings.shot_name)
            if shot_padding_match:
                # Set default padding to 4 if only <ShotNum> is used
                if shot_padding_match.group(0) == '<ShotNum>':
                    shot_padding = 4
                else:
                    shot_padding = shot_padding_match.group(0).count('#')

                # Calculate the total number of folders
                num_folders = self.settings.number_of_shots * self.settings.shot_increments + self.settings.starting_shot

                # Generate shot names with padding
                for x in range(self.settings.starting_shot, num_folders, self.settings.shot_increments):
                    shot_name = re.sub(r'<ShotNum#+>|<ShotNum>', str(x).zfill(shot_padding), self.settings.shot_name)
                    shot_list.append(shot_name)
            else:
                # Check if shot_name contains a sequence in brackets outside of <ShotNum>
                if '[' in self.settings.shot_name and ']' in self.settings.shot_name:
                    # Extract prefix and sequence
                    shot_name_prefix = self.settings.shot_name.split('[', 1)[0]
                    shot_sequence = self.settings.shot_name.split('[', 1)[1].rsplit(']', 1)[0].replace(' ', '')
                    shots = shot_sequence.split(',')

                    # Generate shot names from sequence
                    for shot in shots:
                        if '-' in shot:
                            start, end = shot.split('-')
                            start, end = int(start.lstrip('0')), int(end.lstrip('0'))
                            padding = len(shot.split('-')[0])

                            for n in range(start, end + 1, self.settings.shot_increments):
                                shot_name = shot_name_prefix + str(n).zfill(padding)
                                shot_list.append(shot_name)
                        else:
                            shot_list.append(shot_name_prefix + shot)
                else:
                    # Single shot name without sequence
                    shot_list.append(self.settings.shot_name)

        pyflame.print_list(
            list_name='Shots To Create',
            list_items=shot_list,
            )

        return shot_list

    def create_shot_folders(self):
        """
        Create Shot Folders
        ===================

        Create shot folders in the Media Panel and/or file system based on folder structure templates.
        """

        def match_segments_to_temp_library() -> None:
            """
            Match Segments to Temp Library
            ==============================

            Create a temp library and match out timeline segments to it.
            """

            # Create Clips Library
            pyflame.print('Creating Temp Clips Library', underline=True)
            self.temp_library = flame.projects.current_project.current_workspace.create_library('Temp Clips Library')

            # Match out segments to temp library
            pyflame.print('Matching out segments to temp library...')
            for item in self.selection:
                item.match(self.temp_library)

            # Replace selection of segements with clips from temp library
            self.selection = self.temp_library.clips

        def create_shot_folders_in_media_panel() -> None:
            """
            Create Shot Folders in Media Panel
            ==================================

            Create shot folders in the Media Panel.
            """

            pyflame.print('Creating Media Panel Shot Folders', underline=True)

            # Create new shot library
            self.media_panel_dest = flame.projects.current_project.current_workspace.create_library('Shot Folders')

            # Create Media Panel shot folders
            pyflame.create_media_panel_folders(
                folder_list=shot_list,
                folder_structure=self.settings.folders,
                dest=self.media_panel_dest,
                )

            pyflame.print('Media Panel Shot Folders Created', arrow=True)

            # If clips in the media panel are selected, copy them to the shot folders
            if self.mode == 'clips' or self.mode == 'segments':
                self.copy_clips()

        def create_file_system_shot_folders() -> None:
            """
            Create File System Shot Folders
            ===============================

            Create file system shot folders.
            """

            pyflame.print('Creating File System Shot Folders', underline=True)

            folder_dest = self.translate_file_system_path(self.file_system_path_entry.text)
            # print(f'folder_dest: {folder_dest}\n')

            # If folder_dest doesn't exist, create it
            if not os.path.isdir(folder_dest):
                try:
                    os.makedirs(folder_dest)
                except:
                    PyFlameMessageWindow(
                        message=f'Unable to create folder:\n\n{folder_dest}\n\nCheck folder path and permissions then try again.',
                        message_type=MessageType.ERROR,
                        parent=None,
                        )
                    return

            # Check for folder and that it is writable
            if not os.access(folder_dest, os.W_OK):
                PyFlameMessageWindow(
                    message=f'File system folder destination not writable.\n\n{folder_dest}',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return

            # Create file system shot folders
            pyflame.create_file_system_folders(
                folder_list=shot_list,
                folder_structure=self.settings.file_system_folders,
                dest_path=folder_dest,
                )

            # Reveal in Finder if enabled
            if self.settings.reveal_in_finder:
                pyflame.open_in_finder(folder_dest)

            print('\n', end='')

            # If clips in the media panel are selected, export them to the shot folders
            if self.mode in ('clips', 'segments') and self.settings.export_clips:
                self.export_clips()

            pyflame.print('File System Shot Folders Created', arrow=True)

        pyflame.print('Creating Shot Folders...')

        # Save settings
        settings_saved = self.save_settings()
        if not settings_saved:
            return

        # Create list of shots to create.
        shot_list = self.create_shot_list()

        # Match out timeline segments to temp library if mode is segments
        if self.mode == 'segments':
            match_segments_to_temp_library()

        # Create Media Panel folders.
        if self.settings.create_folders:
            create_shot_folders_in_media_panel()

        # Create file system folders
        if self.settings.create_system_folders:
            create_file_system_shot_folders()

        # Delete temp library if mode is segments
        if self.mode == 'segments':
            flame.delete(self.temp_library)
            pyflame.print('Temp Library Deleted', arrow=True)

        print('\n', end='')

    def copy_clips(self) -> None:
        """
        Copy Clips
        ==========

        Copy clips to shot folders.
        """

        print('Mode:', self.mode)
        print('Shot List:', self.shot_list)
        print('Selection:', self.selection)
        print('Plate Copy Path:', self.settings.plate_folder)
        print('Media Panel Dest:', self.media_panel_dest)

        print('Current Tab:', flame.get_current_tab())

        # Check current Flame tab. Clips cannot be copied while in the MediaHub tab.
        if flame.get_current_tab() == 'MediaHub':
            switch_tab = True
            flame.set_current_tab('Tools')
            pyflame.print('Switching to Tools tab to copy clips in MediaPanel.')
        else:
            switch_tab = False


        for clip in self.selection:
            # shot_name = pyflame.shot_name_from_clip(clip)
            print('Shot Name:', str(clip.shot_name)[1:-1])
            print('Clip:', clip)
            pyflame.copy_to_shot_folder(
                shot_name=str(clip.shot_name)[1:-1],
                pyobject=clip,
                search_location=self.media_panel_dest,
                dest_folder_path=self.settings.plate_folder,
                )

        # If original tab was MediaHub, switch back to it.
        if switch_tab:
            flame.set_current_tab('MediaHub')
            pyflame.print('Switching back to MediaHub tab.')

    def export_clips(self) -> None:
        """
        Export Clips
        ============

        Export clips to shot folders.
        """

        pyflame.print('Exporting Clips', underline=True)

        def get_export_paths() -> str:
            """
            Get Export Paths
            ===============

            Get export paths for preset.

            Returns
            -------
                str:
                    Path of selected export preset.
            """

            preset_type = self.settings.export_preset_type
            preset_format = self.settings.export_preset.split(':')[0]
            preset_name = self.settings.export_preset.split(': ')[1]

            print('Preset Type:', preset_type)
            print('Preset Format:', preset_format)
            print('Preset Name:', preset_name)

            # Get preset directories
            visibility_map = {
                'User': flame.PyExporter.PresetVisibility.User,
                'Shared': flame.PyExporter.PresetVisibility.Shared,
                'Project': flame.PyExporter.PresetVisibility.Project,
                }
            preset_type_map = {
                'Movie': flame.PyExporter.PresetType.Movie,
                'Image Sequence': flame.PyExporter.PresetType.Image_Sequence,
                }
            preset_dir = flame.PyExporter.get_presets_dir(
                visibility_map[self.export_preset_type_menu.text],
                preset_type_map[preset_format],
                )

            print('Preset Directory:', preset_dir)

            preset_path = os.path.join(preset_dir, f'{preset_name}.xml')
            print('Preset Path:', preset_path, '\n')

            return preset_path

        # Get export preset path
        preset_path = get_export_paths()

        # Initialize Flame Exporter
        exporter = flame.PyExporter()
        exporter.foreground = self.settings.foreground_export

        file_system_folder_path = self.translate_file_system_path(self.file_system_path_entry.text)

        # Export clips in selection to shot folders.
        for clip in self.selection:
            shot_name = str(clip.shot_name)[1:-1]
            shot_export_path = os.path.join(file_system_folder_path, shot_name, self.settings.plate_export_folder.split('/', 1)[1])
            print('Shot Name:', shot_name)
            print('Shot Export Path:', shot_export_path, '\n')

            # Run Flame Export
            exporter.export(clip, preset_path, shot_export_path)

        pyflame.print('Clips Export Complete')

class CreateShotFoldersSetup():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} - Setup {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        self.setup()

    def setup(self):

        def file_system_path_browse():
            """
            File System Path Browse
            =======================

            Browse for file system folder path.
            """

            path = pyflame.file_browser(
                path=self.file_system_folder_path_entry.text,
                title='Select Path',
                select_directory=True,
                window_to_hide=[self.setup_window],
                )

            if path:
                self.file_system_folder_path_entry.setText(path)

        def save_setup_settings():
            """
            Save Setup Settings
            ===================

            Save setup settings to config file and close setup window.
            """

            # Convert tree dict to paths
            media_panel_paths = [path for path in self.media_panel_folder_tree.all_item_paths]
            file_system_paths = [path for path in self.file_system_folder_tree.all_item_paths]

            if self.media_panel_plate_folder_entry.text not in media_panel_paths:
                PyFlameMessageWindow(
                    message='Plate Folder must be a valid folder in the Media Panel folder structure.\n\nExample: Shot_Folder/Plates',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            if self.file_system_plate_export_folder_entry.text not in file_system_paths:
                PyFlameMessageWindow(
                    message='Plate Export Folder must be a valid folder in the File System folder structure.\n\nExample: Shot_Folder/Plates',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            # Save settings to config file
            self.settings.save_config(
                config_values={
                    'folders': self.media_panel_folder_tree.tree_dict,
                    'file_system_folders': self.file_system_folder_tree.tree_dict,
                    'file_system_folders_path': self.file_system_folder_path_entry.text,
                    'plate_folder': self.media_panel_plate_folder_entry.text,
                    'plate_export_folder': self.file_system_plate_export_folder_entry.text,
                    'plate_export_preset': None,
                    }
                )

            self.setup_window.close()

        def close_window():
            """
            Close Window
            ============

            Close setup window.
            """

            self.setup_window.close()

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} Setup <small>{SCRIPT_VERSION}',
            return_pressed=save_setup_settings,
            escape_pressed=close_window,
            grid_layout_columns=6,
            grid_layout_rows=13,
            parent=None,
            )

        # Labels
        self.media_panel_folders_setup_label = PyFlameLabel(
            text='Media Panel Folder Setup',
            style=Style.UNDERLINE,
            )
        self.media_panel_plate_folder_label = PyFlameLabel(
            text='Plate Folder',
            )
        self.file_system_folder_setup_label = PyFlameLabel(
            text='File System Folder Setup',
            style=Style.UNDERLINE,
            )
        self.file_system_folder_path_label = PyFlameLabel(
            text='File System Folder Path',
            )
        self.file_system_plate_export_folder_label = PyFlameLabel(
            text='Plate Export Folder',
            align=Align.RIGHT,
            )

        # Entries
        self.media_panel_plate_folder_entry = PyFlameEntry(
            text=self.settings.plate_folder,
            )
        self.file_system_folder_path_entry = PyFlameEntry(
            text=self.settings.file_system_folders_path,
            )
        self.file_system_plate_export_folder_entry = PyFlameEntry(
            text=self.settings.plate_export_folder,
            )

        # Tree Widgets
        self.media_panel_folder_tree = PyFlameTreeWidget(
            column_names=['Media Panel Shot Folder Template'],
            tree_dict=self.settings.folders,
            allow_children=True,
            )
        self.file_system_folder_tree = PyFlameTreeWidget(
            column_names=['File System Shot Folder Template'],
            tree_dict=self.settings.file_system_folders,
            allow_children=True,
            )

        # Token PushButton
        self.file_system_path_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                'Sequence Name': '<SeqName>',
                'Sequence Name (All Caps)': '<SEQNAME>',
                'Year (YYYY)': '<YYYY>',
                'Year (YY)': '<YY>',
                'Month (MM)': '<MM>',
                'Day (DD)': '<DD>',
                },
            token_dest=self.file_system_folder_path_entry,
            )

        # Buttons
        self.media_panel_add_folder_button = PyFlameButton(
            text='Add Folder',
            connect=partial(self.media_panel_folder_tree.add_item, 'New Folder'),
            )
        self.media_panel_delete_folder_button = PyFlameButton(
            text='Delete Folder',
            connect=self.media_panel_folder_tree.delete_item,
            )
        self.media_panel_sort_folders_button = PyFlameButton(
            text='Sort Folders',
            connect=self.media_panel_folder_tree.sort_items,
            )

        self.file_system_add_folder_button = PyFlameButton(
            text='Add Folder',
            connect=partial(self.file_system_folder_tree.add_item, 'New Folder'),
            )
        self.file_system_delete_folder_button = PyFlameButton(
            text='Delete Folder',
            connect=self.file_system_folder_tree.delete_item,
            )
        self.file_system_sort_button = PyFlameButton(
            text='Sort Folders',
            connect=self.file_system_folder_tree.sort_items,
            )

        self.file_system_path_browser_button = PyFlameButton(
            text='Browse',
            connect=file_system_path_browse,
            )

        self.setup_save_button = PyFlameButton(
            text='Save',
            connect=save_setup_settings,
            color=Color.BLUE,
            )
        self.setup_cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.setup_window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.setup_window.grid_layout.addWidget(self.media_panel_folders_setup_label, 0, 0, 1, 3)

        self.setup_window.grid_layout.addWidget(self.media_panel_add_folder_button, 1, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_delete_folder_button, 2, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_sort_folders_button, 3, 0)

        self.setup_window.grid_layout.addWidget(self.media_panel_folder_tree, 1, 1, 7, 2)

        self.setup_window.grid_layout.addWidget(self.file_system_folder_setup_label, 0, 3, 1, 3)

        self.setup_window.grid_layout.addWidget(self.file_system_folder_tree, 1, 3, 7, 2)

        self.setup_window.grid_layout.addWidget(self.file_system_add_folder_button, 1, 5)
        self.setup_window.grid_layout.addWidget(self.file_system_delete_folder_button, 2, 5)
        self.setup_window.grid_layout.addWidget(self.file_system_sort_button, 3, 5)

        self.setup_window.grid_layout.addWidget(self.media_panel_plate_folder_label, 8, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_plate_folder_entry, 8, 1, 1, 2)
        self.setup_window.grid_layout.addWidget(self.file_system_plate_export_folder_entry, 8, 3, 1, 2)
        self.setup_window.grid_layout.addWidget(self.file_system_plate_export_folder_label, 8, 5)

        self.setup_window.grid_layout.addWidget(self.file_system_folder_path_label, 10, 0)
        self.setup_window.grid_layout.addWidget(self.file_system_folder_path_entry, 10, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.file_system_path_browser_button, 10, 4)
        self.setup_window.grid_layout.addWidget(self.file_system_path_token_menu, 10, 5)

        self.setup_window.grid_layout.addWidget(self.setup_cancel_button, 12, 4)
        self.setup_window.grid_layout.addWidget(self.setup_save_button, 12, 5)

def create_shot_folders(selection):

    CreateShotFolders(selection=None, mode='empty')

def create_shot_folders_from_clips(selection):

    CreateShotFolders(selection, mode='clips')

def create_shot_folders_from_segments(selection):

    CreateShotFolders(selection, mode='segments')

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_library(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary)):
            return True
    return False

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def scope_segment(selection):

    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False

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
                    'name': 'Create Shot Folders Setup',
                    'execute': CreateShotFoldersSetup,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Create...',
            'actions': [
                {
                    'name': 'Shot Folders',
                    'execute': create_shot_folders,
                    'minimumVersion': '2025.1',
                },
                {
                    'name': 'Shot Folders (From Clips)',
                    'isVisible': scope_clip,
                    'execute': create_shot_folders_from_clips,
                    'minimumVersion': '2025.1',
                }
            ]
        }
    ]

def get_mediahub_files_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Create Shot Folders',
                    'order': 1,
                    'separator': 'below',
                    'execute': CreateShotFolders,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_timeline_custom_ui_actions():

    return [
        {
            'name': 'Create...',
            'actions': [
                {
                    'name': 'Shot Folders (From Segments)',
                    'isVisible': scope_segment,
                    'execute': create_shot_folders_from_segments,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
