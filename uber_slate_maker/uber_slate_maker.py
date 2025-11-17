# -*- coding: utf-8 -*-
# Uber Slate Maker
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
Script Name: Uber Slate Maker
Script Version: 1.3.1
Flame Version: 2026
Written by: Michael Vaglienty
Creation Date: 12.29.18
Update Date: 04.14.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create and update slates from CSV file data using Type Node templates.

    - Slates of multiple ratios can be created from the same CSV file.
    - Update existing slates in sequences.
    - Preview slate text before creation.
    - Automatic slate naming with tokens.
    - Add color to slate clips - color can be changed when updating slates as well.
    - Does not work with Flare

    - Detailed instructions: https://pyflame.com/uber-slate-maker
    - Example files: <FlamePythonPath>/uber_slate_maker/example_files/
        - CSV Template Files
        - Type Node Template Files

Notes:

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

URL:
    https://github.com/logik-portal/python/uber_slate_maker

Menus:

    Right-click on clip to be used as slate background -> UberSlate Maker
    Right-click on selection of slates or sequences containing slates -> Uber Slate Maker - Update Slates

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.3.1 04.14.25
        - Added CURRENT_DATE token to token menu.
        - Fixed bug: Selecting a sequence with no slates created by this script would cause the script to crash.
        - Fixed bug: Changing text in CSV field was causing errors in the terminal.
        - Fixed bug: Rename Column Header was not working properly in CSV Editor.
        - Fixed bug: Text in cells/headers beinging renamed now shows in renaming window is CSV Editor.
        - Slates made with older versions of the script cannot be updated with this version.

    v1.3.0 04.01.25
        - Combined Multi-ratio and Single-ratio modes.
        - Slate background clips name must contain have a underscore and ratio. Example: slate_background_16x9
        - Type Node templates no longer needs to be saved when creating slates. Slate background clips should have a Type Node Timeline Effect with a Slate Template applied.
        - Saved Type Node Templates are still required to UPDATE slates. They must have the ratio in the filename. Example: slate_16x9.type_node
        - The ability to make slates of different ratios from the same csv file is done automatically if a ratio column is present in the csv file.
        - If a ratio column is present in the csv file, only the ratios of the selected slate backgrounds will be created.
          Example: If the CSV has a ratio column with entries of 16x9, 1x1, and 4x3, and slate_bg_16x9 is selected as the slate background, only 16x9 slates will be created.

    v1.2.0 03.23.25
        - Added ability to set slate clip color and change color when updating slates.
        - Fixed misc bugs.

    v1.1.0 03.16.25
        - Added Preview Slates feature with clipboard support.
        - Added simple CSV Editor to quickly change/update CSV files.
        - Added Update Slates option.
        - Added ability to set slate clip color and change color when updating slates.
        - Holding down alt while hovering over a selected field will show the full field value and copy it to the clipboard.
        - Fixed misc bugs.

    v1.0.0 03.07.25
        - Updated to use Type Node instead of Text Node for Flame 2026 and later.
"""

#-------------------------------------
# [Import Modules]
#-------------------------------------

import csv
import datetime
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
SCRIPT_VERSION = 'v1.3.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class UberSlateMaker():

    def __init__(self, selection: Any) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Get selection
        self.selection = selection

        # Create/Load config
        self.settings = self.load_config()

        # Create temp folder
        self.temp_path = pyflame.create_temp_folder()
        self.templates_path = os.path.join(self.temp_path, 'slate_templates')

        self.current_date = ''

        # Switch tab to Timeline if current tab is MediaHub
        # Slates cannot be created in the MediaHub tab
        if flame.get_current_tab() == 'MediaHub':
            flame.go_to('Timeline')

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
                'csv_file_path': '',
                'date_format': 'mm/dd/yy',
                'slate_clip_name': '',
                'spaces_to_underscores': True,
                'create_ratio_folders': True,
                'clip_color': 'No Color',
                'templates_path': '/opt/Autodesk'
                }
            )

        return settings

    #-------------------------------------

    def slate_maker(self, update_mode: bool=False) -> None:

        def validate_selection() -> bool:
            """
            Validate Selection
            ==================

            Validate selection.
            """

            def type_node_check() -> bool:
                """
                Type Node Check
                ===============

                Check selected clips for existing Type Node.

                All clips must have a Type Node with a Slate Template applied. If not, user error message is shown.

                Args:
                -----
                    `selection` (list):
                        Selection of clips to check.

                Returns:
                --------
                    True if all selected clips contain a Type Node, False if not.
                """

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

                    # If this clip does not have a Type node, immediately return False
                    if not clip_has_type_node:
                        PyFlameMessageWindow(
                            message='All selected slate backgrounds must have a Type Node with a Slate Template applied.',
                            type=MessageType.ERROR
                            )
                        return False

                # If we've made it through all clips, all must have a Type node
                return True

            def protect_from_editing_check() -> bool:
                """
                Protect From Editing Check
                ==========================

                Check to make sure Protect From Editing option is turned off in preferences by copying a clip.
                Copied clip gets deleted after check is done.

                Returns:
                --------
                    False if Protect From Editing is turned off, True if Protect From Editing is turned on and needs to
                    be turned off.
                """

                pyflame.print('Checking Protect From Editing setting...', new_line=False)

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
                    flame.delete(new_clip)
                    PyFlameMessageWindow(
                        message='Turn off Protect from Editing: Flame Preferences -> General.',
                        type=MessageType.ERROR
                        )
                    return True

            # Type node check
            type_node = type_node_check()
            if not type_node:
                return False

            # Protect from editing check
            protect_from_editing = protect_from_editing_check()
            if protect_from_editing:
                return False

            # If we've made it through all checks, return True
            return True

        def get_slate_templates() -> list:
            """
            Get Slate Templates
            ===================

            Save Slate Type Node Template Setups to the temp folder.

            Type Node setups have the same name as the clip they were created with the ratio added to the end.

            Returns:
            --------
                List of template paths.
            """

            def create_temp_slate_templates_folder() -> None:
                """
                Create Temp Slate Templates Folder
                =================================

                Create a temporary folder for slate templates.

                If the folder already exists, delete it. Then create a new folder.
                """

                if os.path.exists(self.templates_path):
                    shutil.rmtree(self.templates_path)

                # Create slate templates folder
                os.makedirs(self.templates_path)

                pyflame.print(f'Created temporary folder for slate templates: {self.templates_path}', new_line=False, text_color=TextColor.GREEN)

            def get_slate_templates_from_clips() -> list:
                """
                Get Slate Templates from Clips
                =============================

                Get slate templates from clips.
                """

                # Save slate Type Node setups
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

            def browse_for_templates() -> list:
                """
                Browse for Templates
                ===================

                Browse for templates.

                Templates should all be in the same folder and have a filename that contains the slate ratio.

                Returns:
                --------
                    List of template paths.
                """

                PyFlameMessageWindow(
                    message='Select folder containing Type Node Template Setups to be used for updating slates.\n\nType Node Template setups should have the slate ratio in the filename.\n\nExample: slate_16x9.type_node',
                    )
                folder_path = pyflame.file_browser(
                    path=self.settings.templates_path,
                    title='Select Type Node Templates Folder',
                    select_directory=True,
                    )
                if not folder_path:
                    pyflame.print('No folder selected, exiting...', text_color=TextColor.RED)
                    return []
                else:
                    self.templates_path = folder_path
                    template_list = [slate for slate in os.listdir(folder_path) if slate.endswith('.type_node')]
                    self.settings.save_config(
                        config_values=
                            {
                                'templates_path': folder_path
                            }
                        )
                    return template_list

            pyflame.print('Saving Slate Type Node Template Setups...', text_color=TextColor.GREEN, new_line=False)

            template_list = []

            # If updating slates, browse for templates.
            # Otherwise create slate templates folder and save templates to folder.
            if update_mode:
                template_list = browse_for_templates()
                if not template_list:
                    return
            else:
                create_temp_slate_templates_folder() # Create slate templates folder
                template_list = get_slate_templates_from_clips() # Get slate templates from selected slate background clips

            # Print template list
            print('Slate Templates:')
            for template in template_list:
                print(template)

            print('\n', end='')

            return template_list

        def csv_browse() -> None:
            """
            CSV Browse
            ==========

            Open file browser to select CSV file with slate info.

            When a path is selected, save path to config file and update UI.
            """

            csv_file_path = pyflame.file_browser(
                path=self.csv_path_entry.text(),
                title='Select CSV File',
                extension=['csv'],
                window_to_hide=[self.window],
                )

            if csv_file_path:
                self.settings.save_config(
                    config_values=
                        {
                            f'csv_file_path': csv_file_path
                        }
                    )

                self.csv_path_entry.setText(csv_file_path)

                self.get_clip_name_tokens(
                    csv_file_path=csv_file_path,
                    clip_name_push_button=self.slate_clip_name_token_push_button,
                    )

        def get_slate_ratios() -> str:
            """
            Get Slate Ratios
            ================

            Get the ratios of the selected slate backgrounds or slates in selected sequences.
            """

            def get_clip_ratios():
                """
                Get Clip Ratios
                ===============

                Get the ratios of the selected clips.
                """

                print('Getting Selected Clip Ratios...')

                slate_ratios = []

                for clip in self.selection:
                    ratio = self.get_slate_ratios_from_clip_name(clip)
                    if not ratio:
                        return False

                    # Tag slate clip with ratio
                    clip.tags = [f'SlateRatio: {ratio}']

                    if ratio not in slate_ratios:
                        slate_ratios.append(ratio)

                return slate_ratios

            def get_sequence_ratios():
                """
                Get Sequence Ratios
                ==================

                Get the ratios of the selected sequences from slate segment tags.
                """

                print('Getting Selected Sequence Ratios...')

                slate_ratios = []

                for seq in self.selection:
                    for version in seq.versions:
                        for track in version.tracks:
                            for segment in track.segments:
                                for tag in segment.tags.get_value():
                                    if 'SlateRatio: ' in tag:
                                        ratio = tag.split(':', 1)[1].strip()
                                        if ratio not in slate_ratios:
                                            slate_ratios.append(ratio)

                return slate_ratios

            if isinstance(self.selection[0], flame.PySequence):
                slate_ratios = get_sequence_ratios()
            elif isinstance(self.selection[0], flame.PyClip):
                slate_ratios = get_clip_ratios()

            self.slate_ratios = slate_ratios
            slate_ratios = ' | '.join([str(elem).lower() for elem in slate_ratios])

            pyflame.print(f'Slate Ratios: {slate_ratios}', text_color=TextColor.GREEN)

            return slate_ratios

        def get_tokenized_slate_name() -> str:
            """
            Get Tokenized Slate Name
            ======================

            Get the tokenized slate name.
            """

            print('Getting Tokenized Slate Name...')

            tokenized_slate_name = None

            for seq in self.selection:
                for version in seq.versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            for tag in segment.tags.get_value():
                                if 'TokenizedSlateName: ' in tag:
                                    tokenized_slate_name = tag.split(':', 1)[1].strip()
                                    print('Tokenized Slate Name:', tokenized_slate_name, '\n')
                                    #return tokenized_slate_name
                                    if tokenized_slate_name == '':
                                        PyFlameMessageWindow(
                                            message='Unable to update slates in one or more of the selected sequences.\n\nMake sure all selected sequences have a slate created by this script.',
                                            type=MessageType.ERROR
                                            )
                                        return None

            PyFlameMessageWindow(
                message='Unable to update slates in one or more of the selected sequences.\n\nMake sure all selected sequences have a slate created by this script.',
                type=MessageType.ERROR
                )

            return None

        def validate_fields() -> bool:
            """
            Validate Fields
            ==============

            Validate UI fields.
            """

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

            # CSV file should contain RATIO in first line - check for this
            if len(self.selection) > 1:
                with open(self.csv_path_entry.text(), 'r') as csv_file:
                    csv_token_line = csv_file.readline().strip()
                csv_token_line = csv_token_line.split(',')
                if 'RATIO' not in csv_token_line:
                    PyFlameMessageWindow(
                        message='CSV file missing column called RATIO.\n\n\n\nThe RATIO field should contain the ratio of the slate to be created',
                        type=MessageType.ERROR
                        )
                    return False

            # Return True if all checks pass
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
            """
            Create Slates
            =============

            Create slates from CSV file.
            """

            # Validate all fields are filled
            if not validate_fields():
               return

            # Save settings to config file
            save_config()

            # Close main window
            self.window.hide()

            # Create slates
            self.create_slates(
                csv_file_path=self.csv_path_entry.text(),
                date_format=self.date_push_button.text(),
                )

        def update_slates() -> None:
            """
            Create Slates
            =============

            Create slates from CSV file.
            """

            # Validate all fields are filled
            if not validate_fields():
                return

            # Save settings to config file
            save_config()

            # Close main window
            self.window.hide()

            # Create slates
            self.update_slates(
                csv_file_path=self.csv_path_entry.text(),
                date_format=self.date_push_button.text(),
                )

        def preview_slates() -> None:
            """
            Preview Slates
            =============

            Preview slates.
            """

            # Validate all fields are filled
            if not validate_fields():
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

            self.csv_editor(
                csv_file_path=self.csv_path_entry.text(),
                )

        validated = validate_selection()
        if not validated:
            return

        slate_ratios = get_slate_ratios()

        if update_mode:
            self.settings.slate_clip_name = get_tokenized_slate_name()
            if not self.settings.slate_clip_name:
                return

        self.slate_templates = get_slate_templates()
        if not self.slate_templates:
            return

        # Set window title based on update mode
        if update_mode:
            window_title = f'{SCRIPT_NAME} - Update Slates <small>{SCRIPT_VERSION}</small>'
        else:
            window_title = f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>'

        #-------------------------------------

        # Create Main Window
        self.window = PyFlameWindow(
            title=window_title,
            return_pressed=save_config,
            grid_layout_columns=6,
            grid_layout_rows=7,
            )

        # Labels
        self.slate_ratios_label = PyFlameLabel(
            text='Selected Slate Ratios',
            )
        self.csv_label = PyFlameLabel(
            text='CSV File',
            )
        self.date_format_label = PyFlameLabel(
            text='Date Format',
            )
        self.slate_clip_name_label = PyFlameLabel(
            text='Slate Name',
            )
        self.clip_color_label = PyFlameLabel(
            text='Slate Clip Color',
            )

        # Entry Fields
        self.slate_ratios_field = PyFlameEntry(
            text=slate_ratios,
            read_only=True,
            )
        self.csv_path_entry = PyFlameEntry(
            text=self.settings.csv_file_path,
            text_changed=self.get_clip_name_tokens,
            )
        self.csv_path_entry = PyFlameEntry(
            text=self.settings.csv_file_path,
            )
        if not update_mode:
            self.csv_path_entry.text_changed(self.get_clip_name_tokens)
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

        # Token Push Button Menus
        self.slate_clip_name_token_push_button = PyFlameTokenPushButton(
            token_dest=self.slate_clip_name_entry,
            )

        # Clip Color Pushbutton Menu
        self.clip_color_push_button = PyFlameColorPushButtonMenu(
            color=self.settings.clip_color,
            )

        # Push Buttons
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

        # Buttons
        self.csv_browse_button = PyFlameButton(
            text='Browse',
            connect=csv_browse,
            )
        self.edit_csv_button = PyFlameButton(
            text='Edit CSV',
            connect=edit_csv,
            )
        self.preview_slates_button = PyFlameButton(
            text='Preview Slates',
            connect=preview_slates,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        # Create/Update Slates Button depending on update mode
        if update_mode:
            self.create_slates_button = PyFlameButton(
                text='Update Slates',
                connect=update_slates,
                color=Color.BLUE,
                )
        else:
            self.create_slates_button = PyFlameButton(
                text='Create Slates',
                connect=create_slates,
                color=Color.BLUE,
                )

        # Get clip name tokens from csv
        self.get_clip_name_tokens(
            csv_file_path=self.csv_path_entry.text(),
            clip_name_push_button=self.slate_clip_name_token_push_button,
            )

        # Disable create ratio folders button in update mode
        if update_mode:
            self.create_resolutions_folders_button.setDisabled(True)
            self.create_resolutions_folders_button.setToolTip('')
            self.slate_clip_name_entry.setDisabled(True)
            self.slate_clip_name_token_push_button.setDisabled(True)
            self.convert_spaces_button.setDisabled(True)

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
        """
        Slate Preview
        =============

        Create a text preview of the slates.
        """

        def create_preview_text():
            """
            Create Preview Text
            ==================

            Create a text preview of the slates.

            Creates Slate Type Node setups and reads setups from temp folder.
            """

            def read_type_node_setups() -> None:
                """
                Read Type Node Setups
                =====================

                Read type node setups from temp folder.
                """

                def read_type_node_setup(type_node_setup_path: str) -> list:
                    """
                    Read Type Node Setup
                    ====================

                    Read Type Node Setup from file and return a list of the text.

                    Args:
                    ------
                        `type_node_setup_path` (str):
                            Path to the Type Node Setup.

                    Returns:
                    --------
                        `slate_text_list` (list):
                            List of slate text.
                    """

                    print('Type Node Setup Path: ', type_node_setup_path)

                    slate_text_list = []

                    # Load Type Node Template XML
                    tree = ET.parse(type_node_setup_path)
                    root = tree.getroot()

                    # Loop over every <CharacterSet> element in the XML
                    for char_set in root.findall('.//CharacterSet'):
                        # Find the <Type> element within the <CharacterSet> and get the text
                        try:
                            type_elem = char_set.find('Text')
                            if type_elem is not None:
                                slate_text = type_elem.text.strip()
                                slate_text = slate_text.strip()
                                slate_text = self.convert_ascii_to_text(slate_text)
                                slate_text_list.append(slate_text)
                        except:
                            pass

                    return slate_text_list

                def create_slate_template_preview() -> list:
                    """
                    Create Slate Template Preview
                    =============================

                    Create a preview of the slate template.

                    Returns:
                    --------
                        `slate_preview` (list):
                            List of slate preview.
                    """

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

                    # Add slates preview to slate preview
                    slate_preview.extend([' ', '--== Slates ==--'])

                    # Get all the slates in the temp folder and sort them
                    slates = [slate for slate in os.listdir(self.temp_path) if slate.endswith('.type_node')]
                    slates.sort()

                    # Add the slates to the preview
                    for slate in slates:
                        slate_name = 'Slate Name: ' + slate.rsplit('.', 1)[0]
                        try:
                            slate_ratio = slate_name.rsplit('_', 1)[1]
                            slate_name = slate_name.rsplit('_', 1)[0]
                        except:
                            pass

                        # Add the slate name and ratio to the preview
                        slate_preview.append(' ')
                        slate_preview.append(f'{slate_name}')
                        try:
                            slate_preview.append(f'Slate Ratio: {slate_ratio}')
                        except:
                            pass
                        slate_preview.append(' ')

                        # Read the slate text and add it to the preview
                        slate_path = os.path.join(self.temp_path, slate)
                        slate_text = read_type_node_setup(slate_path)
                        for line in slate_text:
                            slate_preview.append(line)

                    return slate_preview

                # Create slate template preview
                slate_preview = create_slate_template_preview()

                # Add slates to the slate preview
                slate_preview = create_slates_preview(slate_preview)

                # Print the slate preview in blue text
                print('\nSlate Preview:\n')
                for line in slate_preview:
                    pyflame.print(line, text_color=TextColor.BLUE, print_to_flame=False, new_line=False)
                print('\n', end='')

                # Update the preview text edit
                self.preview_text_edit.setText('\n'.join(slate_preview))

            pyflame.print('Creating Slate Preview...', text_color=TextColor.GREEN)

            # Create slate dicts
            slate_dict = self.create_slate_dicts(csv_file_path, date_format)
            print(slate_dict)

            # Create type nodes
            self.create_type_nodes(slate_dict)

            # Read each text node file and add to preview text
            read_type_node_setups()

        def copy_text():
            """
            Copy Text
            ========

            Copy the preview slate text to the clipboard.
            """

            pyflame.copy_to_clipboard(self.preview_text_edit.text())

        def close_preview_window():
            """
            Close Preview Window
            ===================

            Delete contents of temp folder and close preview window.
            """

            self.clean_temp_folder()

            self.preview_window.close()

        # Cleanup temp folder
        self.clean_temp_folder()

        # Create Preview Window
        self.preview_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Slate Preview <small>{SCRIPT_VERSION}',
            return_pressed=close_preview_window,
            grid_layout_columns=6,
            grid_layout_rows=16,
            )

        # Labels
        self.preview_slates_label = PyFlameLabel(
            text='Slates',
            style=Style.UNDERLINE,
            )

        # Text Edit
        self.preview_text_edit = PyFlameTextEdit(
            text='',
            read_only=True,
            )

        # Buttons
        self.preview_copy_button = PyFlameButton(
            text='Copy to Clipboard',
            connect=copy_text,
            )

        self.preview_close_button = PyFlameButton(
            text='Close',
            connect=close_preview_window,
            color=Color.BLUE,
            )

        # Create Preview Text
        create_preview_text()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.preview_window.grid_layout.addWidget(self.preview_slates_label, 0, 0, 1, 6)
        self.preview_window.grid_layout.addWidget(self.preview_text_edit, 1, 0, 14, 6)
        self.preview_window.grid_layout.addWidget(self.preview_copy_button, 16, 4)
        self.preview_window.grid_layout.addWidget(self.preview_close_button, 16, 5)

    def csv_editor(self, csv_file_path) -> None:
        """
        CSV Editor
        ==========

        Open selected CSV file and edit.
        """

        def save_csv(csv_file_path):
            """
            Save CSV
            =======

            Save the CSV file.
            """

            def save_file(csv_file_path):
                """
                Save File
                ========

                Save the CSV file.
                """

                self.csv_editor_csv_table.save_csv_file(csv_file_path) # Save file
                self.csv_editor_window.close() # Close window

                # Update path in main window
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
            """
            Close CSV Editor Window
            =====================

            Close the CSV editor window.
            """

            self.csv_editor_window.close()

        # Create CSV Editor Window
        self.csv_editor_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: CSV Editor <small>{SCRIPT_VERSION}',
            return_pressed=save_csv,
            grid_layout_columns=6,
            grid_layout_rows=17,
            )

        # Labels
        self.csv_editor_csv_label = PyFlameLabel(
            text='Selected CSV',
            )

        # Entry
        self.csv_editor_selected_csv_entry = PyFlameEntry(
            text=csv_file_path.split('/')[-1],
            )

        # Table
        self.csv_editor_csv_table = PyFlameTable(
            csv_file_path=csv_file_path,
            )

        # Buttons
        self.csv_editor_cancel_button = PyFlameButton(
            text='Close',
            connect=close_csv_editor_window,
            )
        self.csv_editor_save_button = PyFlameButton(
            text='Save',
            connect=partial(save_csv, csv_file_path),
            color=Color.BLUE,
            )

        # Horizontal Line
        self.csv_editor_horizontal_line_01 = PyFlameHorizontalLine()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_csv_label, 0, 0)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_selected_csv_entry, 0, 1, 1, 5)

        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_horizontal_line_01, 1, 0, 1, 6)

        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_csv_table, 2, 0, 14, 6)

        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_cancel_button, 17, 4)
        self.csv_editor_window.grid_layout.addWidget(self.csv_editor_save_button, 17, 5)

    #-------------------------------------
    # [Misc Functions]
    #-------------------------------------

    def get_slate_ratios_from_clip_name(self, clip) -> list:
        """
        Get Slate Ratios
        =================

        Get ratio from clip name.

        Args:
        -----
            `clip` (flame.PyClip):
                Clip to get ratio of.

        Returns:
        --------
            str: Ratio of clip. False if ratio is not found.
        """

        match = re.search(r'(\d+)x(\d+)', str(clip.name)[1:-1])
        if match:
            return f"{match.group(1)}x{match.group(2)}"
        PyFlameMessageWindow(
            message='Slate background clip name must contain have a underscore and ratio.\n\nExample: slate_background_16x9',
            type=MessageType.ERROR
            )
        return None

    def clean_temp_folder(self) -> None:
        """
        Clean Temp Folder
        =================

        Clean the temp folder.
        """

        # Delete files in temp folder ignore folders
        for file in os.listdir(self.temp_path):
            if os.path.isfile(os.path.join(self.temp_path, file)):
                os.remove(os.path.join(self.temp_path, file))

    def convert_ascii_to_text(self, ascii_code) -> str:
        """
        Convert ASCII to Text
        =====================

        Convert ASCII code to text.

        Args:
        -----
            `ascii_code` (str):
                ASCII code to convert to text.

        Returns:
        --------
            `text` (str):
                Text.
        """

        return ''.join(chr(int(code)) for code in ascii_code.split())

    def convert_text_to_ascii(self, text_to_convert) -> str:
        """
        Convert Text to ASCII
        =====================

        Convert text to ASCII code.

        Args:
        -----
            `text_to_convert` (str):
                Text to convert to ASCII code.

        Returns:
        --------
            `ascii_code` (str):
                ASCII code.
        """

        # Convert fancy quotes to regular quotes
        text_to_convert = text_to_convert.replace('"', '"').replace('"', '"')

        # Create list for ASCII codes
        ascii_list = []

        # Convert characters to ASCII code then add to list

        for char in text_to_convert:
            ascii_num = ord(char)
            if ascii_num != 194:
                ascii_list.append(ascii_num)

        ascii_code = ' '.join(str(a) for a in ascii_list)

        return ascii_code

    def get_clip_name_tokens(self, csv_file_path, clip_name_push_button) -> None:
        """
        Get Clip Name Tokens
        ====================

        Get tokens from first line of csv file and add to clip name token menu.

        Tokens are taken from the first line of the CSV.

        Args:
        -----
            `csv_file_path` (str):
                Path to the CSV file.

            `clip_name_push_button` (PyFlamePushButton):
                Push button to add tokens to.
        """

        # Get tokens from csv file
        if os.path.exists(csv_file_path):

            # Get list of items in first line of CSV file.
            with open(csv_file_path, 'r') as csv_file:
                csv_token_line = csv_file.readline().strip()
            csv_token_line = csv_token_line.split(',')

            # Create token dict from first line of CSV. Create menu from this dict.
            token_menu_dict = {}

            for name in csv_token_line:
                menu_key = name
                menu_value = '<' + name + '>'
                token_menu_dict[menu_key] = menu_value

            # Add 'CURRENT_DATE' to token menu dict
            token_menu_dict['CURRENT_DATE'] = '<CURRENT_DATE>'

            clip_name_push_button.add_menu_options(token_menu_dict)

    def color_segment(self, segment) -> None:
        """
        Color Segment
        =============

        Color slate segment.

        Args:
        -----
            `segment` (flame.PySegment):
                Segment to color.
        """

        # Add color to segment if color is not 'No Color'
        try:
            color_name = self.clip_color_push_button.get_color()
            rgba_value = self.clip_color_push_button.get_color_value()
        except:
            color_name = self.clip_color_push_button.get_color()
            rgba_value = self.clip_color_push_button.get_color_value()

        if color_name != 'No Color':
            segment.colour = rgba_value

    def update_progress_window(self,slates_created, slates_total) -> int:
        """
        Update Progress Window
        ======================

        Update progress window with current slate number.

        Args:
        ------
            `slates_created` (int):
                Current slate number.

            `slates_total` (int):
                Total number of slates to create.

        Returns:
        --------
            `slates_created` (int):
                Current slate number.
        """

        self.progress_window.set_progress_value(slates_created)
        self.progress_window.set_text(f'Processing Slate: [{str(slates_created)} of {str(slates_total)}]')

        slates_created += 1

        return slates_created

    #-------------------------------------

    def update_slates(self, csv_file_path, date_format) -> None:
        """
        Update Slates
        =============

        Update existing slates in sequences.

        Args:
        -----
            `csv_file_path` (str):
                Path to the CSV file containing the slate information.

            `date_format` (str):
                Date format string.
        """

        def update_seq_slates() -> None:
            """
            Update Seq Slates
            =================

            Update existing slates in sequences.
            """

            def build_edit_list():

                # Create list of seqeunces from selection
                edit_list = []
                for clip in self.selection:
                    if isinstance(clip, flame.PySequence):
                        edit_list.append(clip)

                if not edit_list:
                    PyFlameMessageWindow(
                        message='No Sequences Selected. Select sequences with slates already created.',
                        type=MessageType.ERROR
                        )
                    return

                print('Edit List:', edit_list)

                return edit_list

            def get_type_node_setup_path(sequence):
                """
                Get Type Node Setup Path
                ========================

                Get the type node setup path from the sequence.
                """

                def find_type_node_setup(slate_tag, ratio_tag) -> str:
                    """
                    Find Type Node Setup
                    ===================

                    Find type node setup in temp folder that matches the slate name tag and ratio tag if it exists.
                    """

                    # Find type node setup in temp folder that matches the slate name tag
                    type_node_setup_path = None

                    for type_node_setup in os.listdir(self.temp_path):
                        #if type_node_setup.endswith(slate_tag.rsplit(':', 1)[1].strip() + '.type_node'):

                        if type_node_setup.endswith(slate_tag.rsplit(':', 1)[1].strip() + '_' + ratio_tag.rsplit(':', 1)[1].strip() + '.type_node'):
                            type_node_setup_path = os.path.join(self.temp_path, type_node_setup)
                        elif type_node_setup.endswith(slate_tag.rsplit(':', 1)[1].strip() + '.type_node'):
                            type_node_setup_path = os.path.join(self.temp_path, type_node_setup)

                    print('Type Node Setup Path:', type_node_setup_path)

                    return type_node_setup_path

                slate_tag = None

                for version in sequence.versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            if segment.tags:
                                segment_tags = segment.tags.get_value()
                                print('Segment Tags:', segment_tags)
                                for tag in segment_tags:
                                    if tag.startswith('SlateName: '):
                                        slate_tag = tag
                                        slate_segment = segment
                                        print('Slate Tag:', slate_tag)
                                        #print('Seg Effects:', slate_segment.effects, '\n')
                                    elif tag.startswith('SlateRatio: '):
                                        ratio_tag = tag
                                        print('Ratio Tag:', ratio_tag)
                            # Break if slate tag is found
                            if slate_tag:
                                break

                type_node_setup_path = find_type_node_setup(slate_tag, ratio_tag)

                return type_node_setup_path, slate_segment

            slates_created = 1

            edit_list = build_edit_list()

            for sequence in edit_list:
                type_node_setup_path, slate_segment = get_type_node_setup_path(sequence)

                # Load Type Node setup if it exists, otherwise add to unslated list
                if type_node_setup_path:
                    print('Loading Type Node setup...')
                    for fx in slate_segment.effects:
                        if fx.type == 'Type':
                            fx.load_setup(type_node_setup_path)
                            break

                    # Color slate segment
                    self.color_segment(slate_segment)
                else:
                    print('No Type Node setup found for slate:', str(sequence.name)[1:-1])
                    unslated.append(str(sequence.name)[1:-1])

                slates_created = self.update_progress_window(slates_created, slates_total)

            print('\n')

        # Create empty list for Sequences that aren't updated
        unslated = []

        pyflame.print('Updating Existing Slates...', text_color=TextColor.GREEN)

        # Create slate dictionaries
        slate_dict = self.create_slate_dicts(csv_file_path, date_format)
        slates_total = len(self.selection)

        # Create Progress Window
        self.progress_window = PyFlameProgressWindow(
            num_to_do=slates_total,
            title='Updating Slates',
            )

        # Create type node setups for each slate
        self.create_type_nodes(slate_dict)

        # Update existing slates in sequences
        update_seq_slates()

        # Cleanup temp folder
        pyflame.cleanup_temp_folder()

        # Enable done button in progress window
        self.progress_window.enable_done_button(True)

        # Close hidden main window
        self.window.close()

        self.progress_window.set_title_text('Slate Updates Complete')

        pyflame.print('Slate Updates Complete', text_color=TextColor.GREEN)

        if unslated:
            PyFlameMessageWindow(
                message="Slates not updated:\n\n{}".format("\n".join(unslated)),
                type=MessageType.ERROR,
                )

    def create_slates(self, csv_file_path, date_format) -> None:
        """
        Create Slates
        =============

        Create new slates from selected clip(s) as background.

        Args:
        -----
            `csv_file_path` (str):
                Path to the CSV file containing the slate information.

            `date_format` (str):
                Date format string.
        """

        def create_slate_library() -> None:
            """
            Create Slate Library
            ====================

            Create a slate library and set as slate dest.
            """

            self.slate_library = flame.projects.current_project.current_workspace.create_library('-= Slates =-')
            self.slate_library.expanded = True

            pyflame.print('Slate Library Created', text_color=TextColor.GREEN)

        def create_slated_clips() -> None:
            """
            Create Slated Clips
            ===================

            Create slated clips from type node setups with selected clip(s) as background.
            """

            def get_tag_value(flame_pyobject, tag_name) -> str:
                """
                Get Tag Value
                =============

                Get the value of a tag from a clip.

                Assumes tag formatting is: <tag_name>: <tag_value>

                Args:
                -----
                    `flame_pyobject`:
                        Flame pyobject to get tag value from.

                    `tag_name` (str):
                        Tag name to get value from.

                Returns:
                --------
                    `tag_value` (str):
                        Value of the tag.

                Example:
                --------
                    clip.tags = ['SlateRatio: 16x9']
                    get_tag_value(clip, 'SlateRatio') -> '16x9'
                """

                for tag in flame_pyobject.tags.get_value():
                    if tag.startswith(tag_name + ': '):
                        tag_value = tag.split(':')[1].strip()
                        print('Tag Value:', tag_value)
                        return tag_value

                return None

            def create_type_node_slate_clip(slate_background, type_node_setup, slate_dest, slate_bg_ratio) -> None:
                """
                Create Type Node Slate Clip
                ===========================

                Copy slate background and add Type Node setup to it. If multi ratio, remove ratio from clip name.

                New slated clips are added to the slate dest - either a slate library or ratio folders within the slate library.

                Args:
                -----
                    `slate_background` (flame.PyClip):
                        Slate background clip.

                    `type_node_setup` (str):
                        Path to the Type Node setup.

                    `slate_dest` (flame.PyFolder):
                        Slate destination - either a slate library or ratio folders within the slate library.
                """

                # Copy slate background to slate dest - either a slate library or ratio folders within the slate library
                clip = flame.media_panel.copy(slate_background, slate_dest)[0]

                # Rename clip to match name of text node, if multi ratio remove ratio from clip name
                clip_name = str(type_node_setup.rsplit('/', 1)[1])[:-10]
                clip_name = clip_name.rsplit('_', 1)[0]
                clip.name = clip_name
                print('Clip Name:', clip.name)

                # Add tags to slate clip
                clip.tags = [f'SlateName: {clip_name}', f'SlateRatio: {slate_bg_ratio}', f'TokenizedSlateName: {self.settings.slate_clip_name}']

                pyflame.print(f'Creating Slate: {str(clip.name)[1:-1]}', new_line=False, text_color=TextColor.GREEN)

                # Add Type effect and load Type Node setup
                seg = clip.versions[0].tracks[0].segments[0]
                for fx in seg.effects:
                    if fx.type == 'Type':
                        fx.load_setup(type_node_setup)

                # Color slate segment
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

                # If no type node setup list, get all type node setups.
                # This is for when there is only one slate bg selected and no ratio column in csv file.
                #if len(type_node_setup_list) == 0:
                if len(self.selection) == 1 and 'RATIO' not in self.row_dict:
                    type_node_setup_list = [f for f in os.listdir(self.temp_path) if f.endswith('.type_node')]

                # Create type node setup clips
                for type_node_setup in type_node_setup_list:
                    print('Type Node Setup:', type_node_setup)
                    type_node_setup_path = os.path.join(self.temp_path, type_node_setup)
                    print('Type Node Setup Path:', type_node_setup_path)
                    # Create ratio folder in slate dest library if create ratio folders is checked
                    if self.settings.create_ratio_folders:
                        existing_ratio_folders = [str(folder.name)[1:-1] for folder in self.slate_library.folders]
                        if slate_bg_ratio not in existing_ratio_folders:
                            # Create ratio folder in slate dest library
                            slate_ratio_folder = self.slate_library.create_folder(slate_bg_ratio)
                            slate_ratio_folder.expanded = True
                            slate_dest = slate_ratio_folder
                    else:
                        slate_dest = self.slate_library

                    # Create type node slate clip
                    create_type_node_slate_clip(slate_background=slate_bg_clip, type_node_setup=type_node_setup_path, slate_dest=slate_dest, slate_bg_ratio=slate_bg_ratio)

                    slates_created = self.update_progress_window(slates_created, slates_total)

            print('\n', end='')

        #-------------------------------------

        # Create new slate library if not updating slates
        create_slate_library()

        # Create slate dictionaries
        slate_dict = self.create_slate_dicts(csv_file_path, date_format)

        # If no slates to create, show error message and return
        if slate_dict == {}:
            PyFlameMessageWindow(
                message='Ratio not found in CSV file.\n\nNo slates to create.',
                type=MessageType.ERROR
                )
            return

        # Create Progress Window
        self.progress_window = PyFlameProgressWindow(
            num_to_do=len(slate_dict),
            title='Creating Slates',
            )

        # Create type node setups for each slate
        self.create_type_nodes(slate_dict)

        # Create new slated clips
        create_slated_clips()

        # Cleanup temp folder
        pyflame.cleanup_temp_folder()

        # Enable done button in progress window
        self.progress_window.enable_done_button(True)

        # Close hidden main window
        self.window.close()

        self.progress_window.set_title_text('Slate Creation Complete')

        pyflame.print('Slate Creation Complete', text_color=TextColor.GREEN)

    def create_slate_dicts(self, csv_file_path, date_format) -> dict:
        """
        Create Slate Dicts
        ==================

        Create a dictionary of slates to be created from the csv file.

        Args:
        -----
            `csv_file_path` (str):
                Path to the csv file containing the slate information.

        Returns:
        --------
            `slate_dict` (dict):
                Dictionary of slates from the csv file.
        """

        def add_to_slate_dict(slate_name: str) -> None:
            """
            Add to Slate Dict
            =================

            Add the slate name and token-value pairs for the current row to the slate dictionary.

            Args:
            -----
                `slate_name` (str):
                    Slate name.
            """

            # Create the slate dictionary entry
            slate_dict[slate_key] = {'_Slate Name': slate_name}
            # Add remaining token-value pairs to slate dictionary
            slate_dict[slate_key].update(self.row_dict)

        def get_date(date_format: str) -> str:
            """
            Get Date
            ========

            Get current date in the format specified by the date format string.

            Args:
            -----
                `date_format` (str):
                    Date format string.

            Returns:
            --------
                `current_date` (str):
                    Current date in the format specified by the date format string.
            """

            now = datetime.datetime.now()
            date_format = date_format.replace('yyyy', '20%y')
            date_format = date_format.replace('yy', '%y')
            date_format = date_format.replace('mm', '%m')
            date_format = date_format.replace('dd', '%d')
            current_date = now.strftime(date_format)

            return current_date

        def resolve_slate_name_tokens(row_dict: dict) -> str:
            """
            Resolve Slate Name Tokens
            =========================

            Resolve the tokens in the slate name.

            Args:
            -----
                `row_dict` (dict):
                    Dictionary of row values.

            Returns:
            --------
                `slate_name` (str):
                    Slate name with tokens resolved.
            """


            slate_name = str(self.slate_clip_name_entry.text())

            for token, value in row_dict.items():
                token_placeholder = f'<{token}>'
                if token_placeholder in slate_name:
                    value = re.sub(r'[\\/*?:"<>|]', '_', value.strip()) # Replace special characters with underscore
                    slate_name = slate_name.replace(token_placeholder, value)

            return slate_name

        def check_duplicate_name(slate_names: list, base_name: str) -> str:
            """
            Check Duplicate Name
            ===================

            Check if base name already exists in slate names, if so, append a number to the end of the name.

            Args:
            -----
                `slate_names` (list):
                    List of slate names.

                `base_name` (str):
                    Base name.

            Returns:
            --------
                `base_name` (str):
                    Base name with a number appended if it already exists.
            """

            if base_name in slate_names:
                i = 1
                while f'{base_name}_{i}' in slate_names:
                    i += 1
                return f'{base_name}_{i}'
            return base_name

        pyflame.print('Creating Slate Dicts...', text_color=TextColor.GREEN)

        # Get current date
        self.current_date = get_date(date_format)
        print('Current Date:', self.current_date)
        print('CSV File Path:', csv_file_path, '\n')

        slate_dict = {} # For storing slates
        slate_names = [] # For checking duplicate slatenames

        with open(csv_file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            tokens = next(reader) # Read and store the header (tokens)
            # Process each subsequent row
            for index, row in enumerate(reader, start=1):
                slate_key = f"Slate {index}"
                self.row_dict = dict(zip(tokens, row)) # Create the initial dictionary with token-value pairs
                # If CURRENT_DATE is in self.row_dict, replace the value with the current date
                if 'CURRENT_DATE' in self.row_dict:
                    self.row_dict['CURRENT_DATE'] = self.current_date
                slate_name = resolve_slate_name_tokens(self.row_dict) # Resolve slate name tokens

                # Check for duplicate slate names and append a number to the end of the name if it exists
                if slate_name in slate_names:
                    slate_name = check_duplicate_name(slate_names, slate_name)
                    slate_names.append(slate_name)
                else:
                    slate_names.append(slate_name)

                # Handle current date if present
                if '<CURRENT_DATE>' in slate_name:
                    slate_name = slate_name.replace('<CURRENT_DATE>', self.current_date)

                # If more than one slate bg is selected, or RATIO column exists in csv file, add ratio to slate name
                if len(self.selection) > 1 or 'RATIO' in self.row_dict:
                    ratio = self.row_dict['RATIO']
                    slate_name = f'{slate_name}_{ratio}'
                    # If slate ratio is in csv ratio list, add to slate dict, if not, skip
                    if ratio in self.slate_ratios:
                        add_to_slate_dict(slate_name)
                    else:
                        print('Skipping:', slate_name)
                        pass
                else:
                    add_to_slate_dict(slate_name)

        pyflame.print('Slate Dicts Created', text_color=TextColor.GREEN)

        return slate_dict

    def create_type_nodes(self, slate_dict: dict) -> None:
        """
        Create Type Node
        ================

        Create a Type Node setup for each slate from the selectedType Node Template.

        Saves out a Type Node setup for each slate to: SCRIPT_PATH/temp.

        Args:
        -----
            `slate_dict` (dict):
                Dictionary of slates from the csv file.
        """

        def generate_type_node_setups(slate_name: str, slate_dict: dict, slate_template: str) -> None:
            """
            Generate Type Node Setups
            ======================

            Generate a Type Node setup for each slate from the selected Type Node Template.
            """

            def get_slate_name(slate_name: str, slate_dict: dict) -> str:
                """
                Get Slate Name
                ==============

                Get the _Slate Name from the slate dict and replace the token with the value.

                Args:
                -----
                    `slate_name` (str):
                        Slate name.

                    `slate_dict` (dict):
                        Slate dictionary.

                Returns:
                --------
                    `slate_name` (str):
                        Slate name with _Slate Name replaced with the value from the slate dict.
                """

                # Get the _Slate Name from the slate dict and replace the token with the value
                for key, value in slate_dict.items():
                    if key == slate_name:
                        for token, value in value.items():
                            if token == '_Slate Name':
                                slate_name = value

                # Remove bad characters from slate name
                slate_name = re.sub(r'[\\/*?:"<>|]', ' ', slate_name)

                # If Use Underscores in checked, replace spaces with underscores in slate name
                if self.convert_spaces_button.isChecked():
                    slate_name = re.sub(r' ', '_', slate_name)

                return slate_name

            def generate_type_node_name(slate_name: str) -> str:
                """
                Generate Type Node Name
                =====================

                Generate a type node name and make sure it doesn't exist in temp folder. If it does, add a number to the end of the name.

                Args:
                ------
                    `slate_name` (str):
                        Slate name.

                Returns:
                --------
                    `type_node_name` (str):
                        Type node name.
                """

                type_node_name = f'{slate_name}.type_node'

                i = 1
                while os.path.exists(os.path.join(self.temp_path, type_node_name)):
                    type_node_name = f'{slate_name}_{i}.type_node'
                    i += 1

                return type_node_name

            def edit_type_node(slate_name: str, slate_dict: dict, slate_template: str) -> None:
                """
                Edit Type Node
                ==============

                Edit and save the Type Node.

                Args:
                -----
                    `slate_name` (str):
                        Slate name.

                    `slate_dict` (dict):
                        Slate dictionary.

                    `slate_template` (str):
                        Path to the Type Node Template.
                """

                # Load Type Node Template XML
                tree = ET.parse(slate_template)
                root = tree.getroot()

                # Loop over every <CharacterSet> element in the XML
                for char_set in root.findall('.//CharacterSet'):
                    # Find the <Type> element within the <CharacterSet>
                    type_elem = char_set.find('Text')
                    if type_elem is not None:
                        # Read the original value and store it in a variable
                        original_value = type_elem.text or ''
                        #print(f'Original Value: {original_value}')
                        translated_value = self.convert_ascii_to_text(original_value)
                        #print('Translated Value:', translated_value)

                        # Find tokens wrapped in <> and replace with values from slate_dict
                        tokens = re.findall(r'<([^<>]+)>', translated_value)
                        for token in tokens:
                            token_placeholder = f'<{token}>'
                            #print('Token:', token)
                            if token in slate_dict[slate]:  # Use the slate-specific dictionary
                                value = slate_dict[slate][token]
                                #print('Value:', value)
                                translated_value = translated_value.replace(token_placeholder, value)
                            if token == 'CURRENT_DATE':
                                translated_value = translated_value.replace(token_placeholder, self.current_date)

                        # Convert translated value to ASCII
                        ascii_value = self.convert_text_to_ascii(translated_value)

                        # Replace type element in Type Node XML
                        type_elem.text = ascii_value

                # Write the updated XML to a new file (or overwrite the original)
                tree.write(os.path.join(self.temp_path, generate_type_node_name(slate_name)), encoding='utf-8', xml_declaration=True)

            pyflame.print(f'Creating Type Node Setup: {slate_name}', new_line=False, text_color=TextColor.GREEN)

            # Get the slate name
            slate_name = get_slate_name(slate_name, slate_dict)
            print('Slate Name:', slate_name)

            # Edit the Type Node
            edit_type_node(slate_name, slate_dict, slate_template)

        pyflame.print('Creating Type Node Setups...')

        # If more than one slate bg is selected, create a type node setup for each ratio
        # If only one slate bg is selected and ratio column exists in csv file, create a type node setup for the slate bg ratio entries in csv file
        # If only one slate bg is selected and ratio column does not exist in csv file, create a type node setup for all entries in csv file
        if len(self.selection) > 1:
            for slate in slate_dict:
                print('Slate:', slate)
                ratio = slate_dict[slate]['RATIO']
                if ratio in self.slate_ratios:
                    # Get slate template from file path that ends with ratio
                    for template_file in os.listdir(self.templates_path):
                        if template_file.endswith(ratio + '.type_node'):
                            template_file_path = os.path.join(self.templates_path, template_file)
                    # Create Type Node Setup
                    generate_type_node_setups(slate, slate_dict, template_file_path)
        else:
            # Only one slate bg is selected.
            # Check for the existence of the 'RATIO' key
            if 'RATIO' in self.row_dict:
                for slate in slate_dict:
                    print('Slate:', slate)
                    ratio = slate_dict[slate]['RATIO']
                    print('Ratio:', ratio)
                    if ratio in self.slate_ratios:
                        # Get slate template from file path that ends with ratio
                        for template_file in os.listdir(self.templates_path):
                            if template_file.endswith(ratio + '.type_node'):
                                template_file_path = os.path.join(self.templates_path, template_file)
                                print('Template File Path:', template_file_path)
                        # Create Type Node Setup
                        generate_type_node_setups(slate, slate_dict, template_file_path)
            else:
                # No ratio column in csv file. Create type node setup for all entries in csv file.
                for slate in slate_dict:
                    generate_type_node_setups(slate, slate_dict, self.slate_templates[0])

        pyflame.print('Completed: Creating Type Node Setups', text_color=TextColor.GREEN)

        print('\n', end='')

#-------------------------------------

def slate_maker(selection: Any) -> None:
    """
    Slate Maker
    ===========
    """

    script = UberSlateMaker(selection)
    script.slate_maker()

def update_slates(selection: Any) -> None:
    """
    Update Slates Multi Ratio
    =========================

    Update slates in selected sequences with selected slates.
    """

    script = UberSlateMaker(selection)
    script.slate_maker(update_mode=True)

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

def get_media_panel_custom_ui_actions():

    return [
        {
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Uber Slate Maker',
                    'isVisible': scope_clip,
                    'execute': slate_maker,
                    'minimumVersion': '2026',
                },
                {
                    'name': 'Uber Slate Maker - Update Slates',
                    'isVisible': scope_sequence,
                    'execute': update_slates,
                    'minimumVersion': '2026',
                }
            ]
        }
    ]
