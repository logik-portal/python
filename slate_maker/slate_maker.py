# -*- coding: utf-8 -*-
# Slate Maker
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
Script Name: Slate Maker
Script Version: 4.11.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 12.29.18
Update Date: 12.28.24

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create slates from CSV file

    *** DOES NOT WORK WITH FLARE ***

    Detailed instructions to use this script can be found on pyflame.com

    Example CSV and Text Node Template files can be found in /opt/autodesk/shared/python/slate_maker/example_files

URL:
    https://github.com/logik-portal/python/slate_maker

Menus:

    Right-click on clip to be used as slate background -> Slates... -> Slate Maker

    Right-click on selection of clips to be used as slate backgrounds -> Slates... -> Slate Maker - Multi Ratio

To install:

    Copy script into /opt/Autodesk/shared/python/slate_maker

Updates:

    v4.11.0 12.28.24

        Updated to PyFlameLib v4.0.0.

        Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

        Script now only works with Flame 2023.2+.

    v4.10.0 08.12.24

        Updated to PyFlameLib v3.0.0.

    v4.9.0 01.25.24

        Updates to UI/PySide.

        Updated to PyFlameLib v2.

        Updated script versioning to semantic versioning.

    v4.8 02.09.23

        Updated config file loading/saving.

        Fixed: Token button wasn't updating when csv is loaded. Script had to be restarted to update token button.

        Added check to make sure script is installed in the correct location.

    v4.7 06.06.22

        Messages print to Flame message window - Flame 2023.1 and later.

        Added Flame file browser - Flame 2023.1 and later.

    v4.6 03.18.22

        Moved UI widgets to external file.

    v4.5 03.06.22

        Updated UI for Flame 2023.

    v4.4 11.16.21

        Improved parsing of csv file.

        If current tab is MediaHub, switch to Timeline tab. Slates cannot be created in MediaHub tab.

    v4.3 10.18.21

        If path is typed into csv or template fields the browser will now open to those paths.

        Script now saves last path selected in browser.

        Script now creates test clip to check for Protect from Editing. Gives warning if Protect from Editing is on.

    v4.2 10.12.21

        Added ability to create slates of different ratios from one CSV file.

        A new menu has been created for this: Slates... -> Slate Maker - Multi Ratio

        Added progress bar.

        Updated config to xml.

    v4.0 05.23.21

        Updated to be compatible with Flame 2022/Python 3.7.

    v3.7 02.12.21

        Fixed bug causing script not to load when CSV or ttg files have been moved or deleted - Thanks John!

    v3.6 01.10.21

        Added ability to use tokens to name slate clip.

        Added button to convert spaces to underscores in slate clip name.

    v3.5 10.13.20

        More UI Updates.

    v3.4 08.26.20

        Updated UI.

        Added drop down menu to select CSV column for slate clip naming.

    v3.3 04.03.20

        Fixed UI issues in Linux.

        Main Window opens centered in linux.

    v2.6 09.02.19

        Fixed bug - Script failed to convert multiple occurrences of token in slate template.

        Fixed bug - Script failed when token not present in slate template for column in csv file.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import csv
import datetime
import os
import re
import shutil
from functools import partial
from random import randint

import flame
from pyflame_lib_slate_maker import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Slate Maker'
SCRIPT_VERSION = 'v4.11.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class CreateSlates():

    def __init__(self, selection):

        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Set selection
        self.selection = selection

        # Set paths
        self.temp_save_path = os.path.join(SCRIPT_PATH, 'temp_slate_folder')

        # Create/Load config
        self.settings = self.load_config()

        # Create temp folder for text node files
        try:
            os.makedirs(self.temp_save_path)
        except:
            shutil.rmtree(self.temp_save_path)
            os.makedirs(self.temp_save_path)

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
                'template_file_path': '',
                'date_format': 'mm/dd/yy',
                'slate_clip_name': '<ISCI>',
                'spaces_to_underscores': True,

                'multi_ratio_csv_file_path': '',
                'multi_ratio_template_folder_path': '',
                'multi_ratio_date_format': 'mm/dd/yy',
                'multi_ratio_slate_clip_name': '<ISCI>',
                'multi_ratio_spaces_to_underscores': True,
                'multi_ratio_create_ratio_folders': True,
                }
            )

        return settings

    #-------------------------------------

    def slate_maker(self):

        def save_config():

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

            elif not self.template_path_entry.text():
                PyFlameMessageWindow(
                    message='Enter path to text node template file.',
                    type=MessageType.ERROR
                    )
                return False

            elif not os.path.isfile(self.template_path_entry.text()):
                PyFlameMessageWindow(
                    message='Text node template file does not exist.',
                    type=MessageType.ERROR
                    )
                return False

            elif not self.slate_clip_name_entry.text():
                PyFlameMessageWindow(
                    message='Enter tokens for slate clip naming.',
                    type=MessageType.ERROR
                    )
                return False

            # Save settings to config file

            self.settings.save_config(
                config_values=
                    {
                        'csv_file_path': self.csv_path_entry.text(),
                        'template_file_path': self.template_path_entry.text(),
                        'date_format': self.date_push_button.text(),
                        'slate_clip_name': self.slate_clip_name_entry.text(),
                        'spaces_to_underscores': self.convert_spaces_button.isChecked(),
                    }
                )

            self.multi_ratio = False

            self.template_path = self.template_path_entry.text()

            self.create_slates()

        # Create main window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            grid_layout_columns=6,
            grid_layout_rows=6,
            )

        # Labels
        self.csv_label = PyFlameLabel(
            text='CSV File',
            )
        self.template_label = PyFlameLabel(
            text='Template',
            )
        self.date_format_label = PyFlameLabel(
            text='Date Format',
            )
        self.slate_clip_name_label = PyFlameLabel(
            text='Slate Clip Name',
            )

        # Entries
        self.csv_path_entry = PyFlameEntry(
            text=self.settings.csv_file_path,
            text_changed=self.get_csv_tokens,
            )
        self.template_path_entry = PyFlameEntry(
            text=self.settings.template_file_path,
            )
        self.slate_clip_name_entry = PyFlameEntry(
            text=self.settings.slate_clip_name,
            )

        # Pushbutton Menus
        self.date_push_button = PyFlamePushButtonMenu(
            text=self.settings.date_format,
            menu_options=[
                'yy/mm/dd',
                'yyyy/mm/dd',
                'mm/dd/yy',
                'mm/dd/yyyy',
                'dd/mm/yy',
                'dd/mm/yyyy',
                ],
            )

        # Token Pushbutton Menu
        self.clip_name_push_button = PyFlameTokenPushButton(
            token_dest=self.slate_clip_name_entry,
            )

        # Pushbuttons
        self.convert_spaces_button = PyFlamePushButton(
            text='Spaces to Underscores',
            button_checked=self.settings.spaces_to_underscores,
            tooltip='Enable to convert spaces in clip name to underscores',
            )

        # Buttons
        self.csv_browse_button = PyFlameButton(
            text='Browse',
            connect=partial(self.csv_browse, 'csv_file_path'),
            )
        self.template_browse_button = PyFlameButton(
            text='Browse',
            connect=self.template_browse,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )
        self.create_slates_button = PyFlameButton(
            text='Create Slates',
            connect=save_config,
            color=Color.BLUE,
            )

        # Get clip name tokens from csv
        try:
            self.get_csv_tokens()
        except:
            pass

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.csv_label, 0, 0)
        self.window.grid_layout.addWidget(self.csv_path_entry, 0, 1, 1, 4)
        self.window.grid_layout.addWidget(self.csv_browse_button, 0, 5)

        self.window.grid_layout.addWidget(self.template_label, 1, 0)
        self.window.grid_layout.addWidget(self.template_path_entry, 1, 1, 1, 4)
        self.window.grid_layout.addWidget(self.template_browse_button, 1, 5)

        self.window.grid_layout.addWidget(self.slate_clip_name_label, 2, 0)
        self.window.grid_layout.addWidget(self.slate_clip_name_entry, 2, 1, 1, 3)
        self.window.grid_layout.addWidget(self.clip_name_push_button, 2, 4)
        self.window.grid_layout.addWidget(self.convert_spaces_button, 2, 5)

        self.window.grid_layout.addWidget(self.date_format_label, 3, 0)
        self.window.grid_layout.addWidget(self.date_push_button, 3, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 5, 4)
        self.window.grid_layout.addWidget(self.create_slates_button, 5, 5)

    def slate_maker_multi_ratio(self):

        def save_config():

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

            elif not self.template_path_entry.text():
                PyFlameMessageWindow(
                    message='Enter path to text node template folder.',
                    type=MessageType.ERROR
                    )
                return False

            elif not os.path.isdir(self.template_path_entry.text()):
                PyFlameMessageWindow(
                    message='Text node template folder does not exist.',
                    type=MessageType.ERROR
                    )
                return False

            elif not self.slate_clip_name_entry.text():
                PyFlameMessageWindow(
                    message='Enter tokens for slate clip naming.',
                    type=MessageType.ERROR
                    )
                return False

            # Check for missing templates for selected slate backgrounds

            self.slate_bgs = [str(clip.name)[1:-1].rsplit('_', 1)[1] for clip in self.selection]
            print('Slate Backgrounds:', self.slate_bgs)

            self.missing_templates = []

            for bg in self.slate_bgs:
                found = False
                for f in os.listdir(self.template_path_entry.text()):
                    if bg.lower() in f.lower():
                        found = True
                if not found:
                    self.missing_templates.append(bg)

            if self.missing_templates:
                missing = ', '.join([str(elem) for elem in self.missing_templates])
                PyFlameMessageWindow(
                    message=f'Text node templates not found for: {missing}',
                    type=MessageType.ERROR
                    )
                return
            else:
                print('--> Templates found for all slate backgrounds.\n')

            # CSV file should contain RATIO in first line - check for this

            with open(self.csv_path_entry.text(), 'r') as csv_file:
                csv_token_line = csv_file.readline().strip()
            csv_token_line = csv_token_line.split(',')
            if 'RATIO' not in csv_token_line:
                PyFlameMessageWindow(
                    message='CSV file missing column called RATIO.\n\n\n\nThe RATIO field should contain the ratio of the slate to be created',
                    type=MessageType.ERROR
                    )
                return
            # Save settings to config file

            self.settings.save_config(
                config_values=
                    {
                        'multi_ratio_csv_file_path': self.csv_path_entry.text(),
                        'multi_ratio_template_folder_path': self.template_path_entry.text(),
                        'multi_ratio_date_format': self.date_push_button.text(),
                        'multi_ratio_slate_clip_name': self.slate_clip_name_entry.text(),
                        'multi_ratio_spaces_to_underscores': self.convert_spaces_button.isChecked(),
                        'multi_ratio_create_ratio_folders' : self.ratio_folders_button.isChecked(),
                    }
                )

            self.multi_ratio = True

            self.create_slates()

        def get_slate_ratios():

            # Check selected slate backgrounds for proper name. Must end with ratio. Such as: slate_bg_16x9

            self.slate_bgs = [str(clip.name)[1:-1].rsplit('_', 1)[1] for clip in self.selection if 'x' in str(clip.name)[1:-1].rsplit('_', 1)[1].lower()]
            self.ratios = ', '.join([str(elem).lower() for elem in self.slate_bgs])

        get_slate_ratios()

        # Create main window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} - MultiRatio <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            grid_layout_columns=6,
            grid_layout_rows=7,
            )

        # Labels
        self.selected_slate_ratio_label = PyFlameLabel(
            text='Selected Slate Ratios',
            )
        self.csv_label = PyFlameLabel(
            text='CSV File',
            )
        self.template_label = PyFlameLabel(
            text='Template Folder',
            )
        self.date_format_label = PyFlameLabel(
            text='Date Format',
            )
        self.slate_clip_name_label = PyFlameLabel(
            text='Slate Clip Name',
            )

        # Entries
        self.selected_slate_ratio_field = PyFlameEntry(
            text=self.ratios,
            read_only=True,
            )
        self.csv_path_entry = PyFlameEntry(
            text=self.settings.multi_ratio_csv_file_path,
            text_changed=self.get_csv_tokens,
            )
        self.template_path_entry = PyFlameEntry(
            text=self.settings.multi_ratio_template_folder_path,
            )
        self.slate_clip_name_entry = PyFlameEntry(
            text=self.settings.multi_ratio_slate_clip_name,
            )

        # Date Pushbutton Menu
        self.date_push_button = PyFlamePushButtonMenu(
            text=self.settings.multi_ratio_date_format,
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

        # Token Pushbutton Menus
        self.clip_name_push_button = PyFlameTokenPushButton(
            token_dest=self.slate_clip_name_entry,
            )

        # Pushbuttons
        self.convert_spaces_button = PyFlamePushButton(
            text='Spaces to Underscores',
            button_checked=self.settings.multi_ratio_spaces_to_underscores,
            tooltip='Enable to convert spaces in clip name to underscores',
            )

        self.ratio_folders_button = PyFlamePushButton(
            text=' Create Ratio Folders',
            button_checked=self.settings.multi_ratio_create_ratio_folders,
            tooltip='Create separate folders for each ratio',
            )

        # Buttons
        self.csv_browse_button = PyFlameButton(
            text='Browse',
            connect=partial(self.csv_browse, 'multi_ratio_csv_file_path'),
            )
        self.template_browse_button = PyFlameButton(
            text='Browse',
            connect=self.template_folder_browse,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )
        self.create_slates_button = PyFlameButton(
            text='Create Slates',
            connect=save_config,
            color=Color.BLUE,
            )

        # Get clip name tokens from csv
        try:
            self.get_csv_tokens()
        except:
            pass

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.selected_slate_ratio_label, 0, 0)
        self.window.grid_layout.addWidget(self.selected_slate_ratio_field, 0, 1, 1, 4)
        self.window.grid_layout.addWidget(self.ratio_folders_button, 0, 5)

        self.window.grid_layout.addWidget(self.csv_label, 1, 0)
        self.window.grid_layout.addWidget(self.csv_path_entry, 1, 1, 1, 4)
        self.window.grid_layout.addWidget(self.csv_browse_button, 1, 5)

        self.window.grid_layout.addWidget(self.template_label, 2, 0)
        self.window.grid_layout.addWidget(self.template_path_entry, 2, 1, 1, 4)
        self.window.grid_layout.addWidget(self.template_browse_button, 2, 5)

        self.window.grid_layout.addWidget(self.slate_clip_name_label, 3, 0)
        self.window.grid_layout.addWidget(self.slate_clip_name_entry, 3, 1, 1, 3)
        self.window.grid_layout.addWidget(self.clip_name_push_button, 3, 4)
        self.window.grid_layout.addWidget(self.convert_spaces_button, 3, 5)


        self.window.grid_layout.addWidget(self.date_format_label, 5, 0)
        self.window.grid_layout.addWidget(self.date_push_button, 5, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 6, 4)
        self.window.grid_layout.addWidget(self.create_slates_button, 6, 5)

    #-------------------------------------

    def save_path(self, path_type, path):
        """
        Save Path
        =========

        Save path to config file
        """

        self.settings.save_config(
            config_values=
                {
                    f'{path_type}': path
                }
            )

    def csv_browse(self, path_type):
        """
        CSV Browse
        ==========

        Open file browser to select CSV file with slate info.
        """

        csv_file_path = pyflame.file_browser(
            path=self.csv_path_entry.text(),
            title='Select CSV File',
            extension=['csv'],
            window_to_hide=[self.window],
            )

        if csv_file_path:
            self.save_path(path_type, csv_file_path)
            self.csv_path_entry.setText(csv_file_path)
            self.get_csv_tokens()

    def template_browse(self):
        """
        Template Browse
        ===============

        Open file browser to select text node template.
        """

        template_file_path = pyflame.file_browser(
            path=self.template_path_entry.text(),
            title='Select Text Node Template Setup (ttg)',
            extension=['ttg'],
            window_to_hide=[self.window],
            )

        if template_file_path:
            self.save_path('csv_file_path', template_file_path)
            self.template_path_entry.setText(template_file_path)

    def template_folder_browse(self):
        """
        Template Folder Browse
        ======================

        Open file browser to select folder containing text node templates for multi ratio slates.
        """

        folder_path = pyflame.file_browser(
            path=self.template_path_entry.text(),
            title='Select Text Node Template Setup Directory',
            extension=[''],
            select_directory=True,
            window_to_hide=[self.window],
            )

        if folder_path:
            self.save_path('multi_ratio_template_folder_path', folder_path)
            self.template_path_entry.setText(folder_path)

    #-------------------------------------

    def get_csv_tokens(self):
        """
        Get CSV Tokens
        ==============

        Get tokens from first line of csv file.

        If csv file path is found, add tokens to clip name token menu,
        otherwise clear clip name token menu.
        """

        # Get tokens from csv file
        if os.path.exists(self.csv_path_entry.text()):

            # Get list of items in first line of csv file.
            with open(self.csv_path_entry.text(), 'r') as csv_file:
                self.csv_token_line = csv_file.readline().strip()
            self.csv_token_line = self.csv_token_line.split(',')

            # Use tokens as column names.
            self.column_names = self.csv_token_line

            # Add tokens to clip name token menu.
            self.create_clip_name_menu()
        else:
            # Clear clip name token menu if csv file not found.
            self.clip_name_push_button.add_menu_options({})

    def create_clip_name_menu(self):
        """
        Create Clip Name Menu
        =====================

        Add tokens to clip name token menu from csv column names.
        """

        token_menu_dict = {}

        for name in self.column_names:
            menu_key = name
            menu_value = '<' + name + '>'
            token_menu_dict[menu_key] = menu_value

        self.clip_name_push_button.add_menu_options(token_menu_dict)

    def create_slates(self):
        """
        Create Slates
        =============

        Create new '- Slate -' library and build slates from CSV file.
        """

        def get_date(date_format):

            now = datetime.datetime.now()
            date_format = date_format.replace('yyyy', '20%y')
            date_format = date_format.replace('yy', '%y')
            date_format = date_format.replace('mm', '%m')
            date_format = date_format.replace('dd', '%d')
            current_date = now.strftime(date_format)
            return current_date

        def create_temp_text_file():

            # Get random number

            text_node_num = randint(1, 10000)

            temp_text_file = self.temp_save_path + '/Slate_Template_' + str(text_node_num) + '.ttg'

            shutil.copy(self.template_path, temp_text_file)

            return temp_text_file

        def ascii_convert(text_to_convert):

            # Convert fancy quotes to regular quotes

            text_to_convert = text_to_convert.replace('“', '"').replace('”', '"')

            # Create list for ascii codes

            ascii_list = []

            # Convert characters to ascii code then add to list

            for char in text_to_convert:
                ascii_num = ord(char)
                if ascii_num != 194:
                    ascii_list.append(ascii_num)

            ascii_code = ' '.join(str(a) for a in ascii_list)

            return ascii_code

        def modify_setup_line(token, token_value, temp_text_file):

            # Open text node file and get token and character length line number

            with open(temp_text_file, 'r') as text_node:
                for num, line in enumerate(text_node, 1):
                    if token in line:
                        token_line_num = num - 1
                        token_char_len_line_num = num - 2

                        # Replace token with token value in line

                        token_line_split = line.rsplit(token, 1)[0]
                        new_token_line = token_line_split + token_value + '\n'
                        new_token_chars = new_token_line.rsplit('Text ', 1)[1]
                        new_token_char_len_line = 'TextLength ' + str(len(new_token_chars.split(' '))) + '\n'

                        # Edit text node with new token and character lenth lines

                        edit_text_node = open(temp_text_file, 'r')
                        contents = edit_text_node.readlines()
                        edit_text_node.close()

                        contents[token_line_num] = f'{new_token_line}'
                        contents[token_char_len_line_num] = f'{new_token_char_len_line}'

                        edit_text_node = open(temp_text_file, 'w')
                        contents = ''.join(contents)
                        edit_text_node.write(contents)
                        edit_text_node.close()

        def create_text_node(line):

            def rename_text_file(clip_name, temp_text_file, temp_save_path):

                def name_clip(clip_num, num):

                    new_text_file = os.path.join(temp_save_path, clip_name) + clip_num + '.ttg'

                    if os.path.isfile(new_text_file):
                        if len(str(num)) == 1:
                            clip_num = '_0' + str(num)
                        else:
                            clip_num = '_' + str(num)
                        num += 1
                        return name_clip(clip_num, num)

                    return new_text_file

                clip_num = ''
                num = 1
                if clip_name != '':
                    clip_name = clip_name.replace('/', '')

                    self.text_node_path = name_clip(clip_num, num)

                    shutil.move(temp_text_file, self.text_node_path)

                    return

            clip_name = self.slate_clip_name_entry.text()

            temp_text_file = create_temp_text_file()

            for item in iter(line.items()):

                # Try to convert token in CSV
                # If token not in template, pass

                try:
                    token = '<' + item[0] + '>'
                    token_value = item[1]

                    if token == '<CURRENT_DATE>':
                        token_value = get_date(self.date_push_button.text())

                    # Convert token to ascii code

                    token = ascii_convert(token)

                    # Convert token value to ascii code

                    token_value = ascii_convert(token_value)

                    # Update text node setup file

                    modify_setup_line(token, token_value, temp_text_file)

                except:
                    pass

            # Get clip name pushbutton text to name clips

            for item in iter(line.items()):

                token = '<' + item[0] + '>'
                token_value = item[1]
                # print('token:', token)

                if token in clip_name:
                    clip_name = clip_name.replace(token, token_value)

                if '<CURRENT_DATE>' in clip_name:
                    date = get_date(self.date_push_button.text())
                    clip_name = clip_name.replace('<CURRENT_DATE>', date)

            # Remove bad characters from clip name

            clip_name = re.sub(r'[\\/*?:"<>|]', ' ', clip_name)
            # print('clip_name:', clip_name)

            # If Use Underscores in checked, replace spaces with underscores

            if self.convert_spaces_button.isChecked():
                clip_name = re.sub(r' ', '_', clip_name)

            # Rename temp text file selected clip name option

            rename_text_file(clip_name, temp_text_file, self.temp_save_path)

        def create_slate_clip(slate_background):

            # Copy slate background to slate dest - either a slate library or ratio folders within the slate library
            new_bg_clip = flame.media_panel.copy(slate_background, self.slate_dest)

            # Rename clip to match name of text node
            for clip in new_bg_clip:
                clip.name = str(self.text_node_path.rsplit('/', 1)[1])[:-4]
                print('   ', str(clip.name)[1:-1])

            # Add text effect and load text setup
            seg = clip.versions[0].tracks[0].segments[0]
            seg_name = str(seg.name)[1:-1]
            text_fx = seg.create_effect('Text')
            text_file_path = os.path.join(self.temp_save_path, seg_name) + '.ttg'
            text_fx.load_setup(text_file_path)

        self.window.hide()

        # Create slate library and set as slate dest

        self.slate_library = flame.project.current_project.current_workspace.create_library('- Slates -')
        self.slate_library.expanded = True
        self.slate_dest = self.slate_library

        # Read token like from csv

        self.get_csv_tokens()

        # Add < and > to column names
        token_list = ['<' + item.upper() + '>' for item in self.csv_token_line]
        print('CSV Tokens:', token_list, '\n')

        #-------------------------------------

        # Create slates

        missing_slate_bgs = []

        if self.multi_ratio:

            # Get list of all ratios from csv file

            csv_ratios = []

            with open(self.csv_path_entry.text(), 'r') as csv_file:
                csv_text = csv.DictReader(csv_file)
                for line in csv_text:
                    for key, value in line.items():
                        if key == 'RATIO':
                            if value not in csv_ratios:
                                csv_ratios.append(value)

            print('CSV Ratios:', csv_ratios)

            # Remove slate background from list if not found is csv file
            for bg in self.slate_bgs:
                slate_bg_missing = True

                for ratio in csv_ratios:
                    if re.search(bg, ratio, re.I):
                        slate_bg_missing = False

                if slate_bg_missing:
                    missing_slate_bgs.append(bg)
                    self.slate_bgs.remove(bg)

            print('Missing slate entries for:', missing_slate_bgs)

            # Get number of slates to be created then load progress bar window
            if self.slate_bgs:
                num_of_slates = 0
                with open(self.csv_path_entry.text(), 'r') as csv_file:
                    csv_text = csv.DictReader(csv_file)
                    for line in csv_text:
                        for bg in self.slate_bgs:
                            if bg.lower() in str(line).lower():
                                num_of_slates += 1

                print('Number of slates to create:', num_of_slates)

                slates_created = 1

                self.progress_window = PyFlameProgressWindow(
                    num_to_do=num_of_slates,
                    title='Creating Slates:',
                    enable_done_button=False,
                    )

                # Iterate through selected slate backgrounds
                for bg in self.slate_bgs:

                    # If Create Ratio Folders button is enabled create folder for ratio in slate library then set folder as slate dest
                    if self.ratio_folders_button.isChecked():
                        ratio_folder = self.slate_library.create_folder(bg.lower())
                        self.slate_dest = ratio_folder

                    # Find csv lines that matches background ratio
                    with open(self.csv_path_entry.text(), 'r') as csv_file:
                        csv_text = csv.DictReader(csv_file)
                        for line in csv_text:
                            if bg.lower() in str(line).lower():

                                # Get slate background clip object to use as background
                                for clip in self.selection:
                                    if bg in str(clip.name):
                                        slate_background = clip
                                        #print('slate_background:', str(slate_background.name)[1:-1])

                                # Find text node template that matches background ratio
                                for (root, dirs, files) in os.walk(self.template_path_entry.text()):
                                    for f in files:
                                        if bg.lower() in f.lower() and f.endswith('.ttg'):
                                            self.template_path = os.path.join(root, f)

                                create_text_node(line)
                                create_slate_clip(slate_background)

                                # Update progress window

                                self.progress_window.set_progress_value(slates_created)
                                self.progress_window.set_text(f'Processing Slate: {str(slates_created)} of {str(num_of_slates)}')
                                slates_created += 1

        else:
            # Create text nodes for single slate bg/template

            # Get number of slates to be created then load progress bar window
            with open(self.csv_path_entry.text(), 'r') as csv_file:
                csv_text = csv.DictReader(csv_file)
                num_of_slates = len([c for c in enumerate(csv_text)])

            slates_created = 1

            self.progress_window = PyFlameProgressWindow(
                num_to_do=num_of_slates,
                title='Creating Slates:',
                enable_done_button=False,
                )

            # Get slate background clip from selection

            slate_background = self.selection[0]
            self.template_path = self.template_path_entry.text()

            # Create slates

            with open(self.csv_path_entry.text(), 'r') as csv_file:
                csv_text = csv.DictReader(csv_file)
                for line in csv_text:
                    create_text_node(line)
                    create_slate_clip(slate_background)

                    # Update progress window

                    self.progress_window.set_progress_value(slates_created)
                    self.progress_window.set_text(f'Processing Slate: {str(slates_created)} of {str(num_of_slates)}')
                    slates_created += 1

        if missing_slate_bgs:
            missing = ', '.join(missing_slate_bgs)
            PyFlameMessageWindow(
                message=f'No entries in csv for selected slate backgrounds: {missing}',
                type=MessageType.ERROR
                )
        # Delete temp folder

        shutil.rmtree(self.temp_save_path)

        self.progress_window.enable_done_button(True)

        self.window.close()

        print('\n')

        pyflame.print('Finished processing slates.', text_color=TextColor.GREEN)

#-------------------------------------

def text_fx_check(selection):
    """
    Text FX Check
    =============

    Make sure clip selected for slate background does not already contain a timeline text fx.
    If clip contains a timeline text fx give user error message to remove it.

    Returns:
        True if clip contains a timeline text fx, Flase if not.
    """

    for clip in selection:
        for version in clip.versions:
            for track in version.tracks:
                for seg in track.segments:
                    for fx in seg.effects:
                        if fx.type == 'Text':
                            PyFlameMessageWindow(
                                message='Slate background clip cannot have a timeline text fx applied. Remove and try again.',
                                type=MessageType.ERROR
                                )
                            return True
    return False

def protect_from_editing_check(selection):
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

    try:
        for clip in selection:
            new_clip = flame.duplicate(clip)
            new_clip.name = 'protect_from_editing_test_clip'
            seg = new_clip.versions[0].tracks[0].segments[0]
            seg.create_effect('Text')
            break
        flame.delete(new_clip)
        return False
    except:
        flame.delete(new_clip)
        PyFlameMessageWindow(
            message='Turn off Protect from Editing: Flame Preferences -> General.',
            type=MessageType.ERROR
            )
        return True

def slate_maker(selection):
    """
    Slate Maker
    ===========

    Create slates from csv
    """

    text_fx = text_fx_check(selection)
    protect_from_editing = protect_from_editing_check(selection)

    if not text_fx and not protect_from_editing:
        script = CreateSlates(selection)
        script.slate_maker()

def slate_maker_multi_ratio(selection):
    """
    Slate Maker Multi Ratio
    =======================

    Create slates of multiple ratios from one csv
    """

    text_fx = text_fx_check(selection)
    protect_from_editing = protect_from_editing_check(selection)

    if not text_fx and not protect_from_editing:
        script = CreateSlates(selection)

        # Make sure all selected clips have a ratio at the end of their name

        try:
            slate_bgs = [str(clip.name)[1:-1].rsplit('_', 1)[1] for clip in selection if 'x' in str(clip.name)[1:-1].rsplit('_', 1)[1].lower()]
        except:
            PyFlameMessageWindow(
                message='All selected slate backgrounds must have ratio at end of file name. Such as: slate_bg_16x9',
                type=MessageType.ERROR
                )
            return
        if not slate_bgs:
            PyFlameMessageWindow(
                message='All selected slate backgrounds must have ratio at end of file name. Such as: slate_bg_16x9',
                type=MessageType.ERROR
                )
            return
        script.slate_maker_multi_ratio()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Slates...',
            'actions': [
                {
                    'name': 'Slate Maker',
                    'isVisible': scope_clip,
                    'execute': slate_maker,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Slate Maker - Multi Ratio',
                    'isVisible': scope_clip,
                    'execute': slate_maker_multi_ratio,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
