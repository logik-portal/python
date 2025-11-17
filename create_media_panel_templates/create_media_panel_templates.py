# Create Media Panel Templates
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
Script Name: Create Media Panel Templates
Script Version: 3.9.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 05.01.19
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create templates from libraries and folders in the Media Panel.
    Right-click menus will be created for each template

URL:
    https://github.com/logik-portal/python/create_media_panel_templates

Menus:

    To create new template menus:
        Right-click on library or folder -> Create Template... -> Create Library Template / Create Folder Template

    Newly created templates:
        Right-click on library or folder -> Library/Folder Templates -> Select from saved templates

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.9.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Window layer order in linux is now fixed.

    v3.8.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v3.7.0 01.02.25
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v3.6.0 08.24.24
        - Updated to PyFlameLib v3.0.0.

    v3.5.0 01.02.24
        - Updates to UI/PySide.

    v3.4.0 08.19.23
        - Fixed creating menus for libraries/folders with periods in name.
          Periods are now replaced with underscores in menu file name.
        - Updated to PyFlameLib v2.0.0.
        - Updated to semantic versioning.

    v3.3 07.12.22
        - Messages print to Flame message window - Flame 2023.1 and later

    v3.2 03.15.22
        - Moved UI widgets to external file

    v3.1 03.07.22
        - Updated UI for Flame 2023
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re

import flame
from lib.pyflame_lib_create_media_panel_templates import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Create Media Panel Templates'
SCRIPT_VERSION = 'v3.9.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class CreateTemplate:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection
        self.creation_type = ''
        self.user_name = flame.users.current_user.name

        # Define Paths
        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.menu_template_path = os.path.join(SCRIPT_PATH, 'assets/menu_template/menu_template')
        self.menus_folder = os.path.join(SCRIPT_PATH, 'menus')
        self.folder_menus = os.path.join(self.menus_folder, 'folders')
        self.library_menus = os.path.join(self.menus_folder, 'libraries')

        # Set Variables

        for item in self.selection:
            if isinstance(item, (flame.PyFolder)):
                self.top_item = 'item.create_folder'
                self.item_name = str(item.name)[1:-1]
                self.creation_type = 'Folder'
                self.menu_name = 'Folder Templates...'
                break

        for item in self.selection:
            if isinstance(item, (flame.PyLibrary)):
                self.top_item = 'flame.project.current_project.current_workspace.create_library'
                self.item_name = str(item.name)[1:-1]
                self.creation_type = 'Library'
                self.menu_name = 'Library Templates...'
                break

        self.name_window()

    def name_window(self):

        def close_window():

            self.window.close()

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.check_file_paths,
            escape_pressed=close_window,
            grid_layout_columns=3,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.name_label = PyFlameLabel(
            text='Template Name',
            )

        # Entry
        self.name_entry = PyFlameEntry(
            text=self.item_name,
            )

        # Buttons
        self.create_btn = PyFlameButton(
            text='Create Template',
            connect=self.check_file_paths,
            color=Color.BLUE,
            )
        self.cancel_btn = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.name_label, 0, 0)
        self.window.grid_layout.addWidget(self.name_entry, 0, 1, 1, 2)

        self.window.grid_layout.addWidget(self.cancel_btn, 2, 1)
        self.window.grid_layout.addWidget(self.create_btn, 2, 2)

        #-------------------------------------

        # Set focus to name entry
        self.name_entry.set_focus()

    def check_file_paths(self):

        # Check for menu folders, create if they don't exist
        if not os.path.isdir(self.folder_menus):
            try:
                os.makedirs(self.folder_menus)
            except:
                PyFlameMessageWindow(
                    message='Could not create menu folder. Check folder permissions',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

        if not os.path.isdir(self.library_menus):
            try:
                os.makedirs(self.library_menus)
            except:
                PyFlameMessageWindow(
                    message='Could not create menu folder. Check folder permissions',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

        # Set menu file name
        menu_file_name = self.name_entry.text
        menu_file_name = menu_file_name.replace('.', '_') + '.py'

        # Set possible menu save paths
        folder_menu_file_path = os.path.join(self.folder_menus, menu_file_name)
        library_menu_file_path = os.path.join(self.library_menus, menu_file_name)

        # Select menu file save path
        if self.creation_type == 'Folder':
            self.menu_save_path = folder_menu_file_path
        elif self.creation_type == 'Library':
            self.menu_save_path = library_menu_file_path

        # Check if menu file name already exists, overwrite?
        shared_folders_list = os.listdir(self.folder_menus)
        shared_libraries_list = os.listdir(self.library_menus)

        if menu_file_name in shared_libraries_list or menu_file_name in shared_folders_list:
            if not PyFlameMessageWindow(
                message='Menu already exists, overwrite?',
                message_type=MessageType.WARNING,
                parent=self.window,
                ):
                return
            try:
                os.remove(folder_menu_file_path)
                os.remove(folder_menu_file_path + 'c')
            except:
                pass
            try:
                os.remove(library_menu_file_path)
                os.remove(library_menu_file_path + 'c')
            except:
                pass

            pyflame.print('Old menu deleted.')

            return self.create_new_template()
        return self.create_new_template()

    def create_new_template(self):

        def get_tree():

            def get_folders(folder):

                def get_parent(folders):

                    # Get folder parent name and add to list
                    folder_parent = folders.parent
                    folder_parent_name = folder_parent.name

                    folder_path_list.append(str(folder_parent_name)[1:-1])

                    # Try to loop through to parent of parent if it exists
                    try:
                        get_parent(folder_parent)
                    except:
                        pass

                for folders in folder.folders:
                    folder_path_list = []
                    folder_name = folders.name
                    folder_path_list.append(str(folder_name)[1:-1])

                    get_parent(folders)
                    get_folders(folders)

                    # Reverse folder list order
                    folder_path_list.reverse()
                    #print ('folder_path_list:', folder_path_list)

                    # Convert folder list to string
                    new_folder_path = '/'.join(folder_path_list)
                    new_folder_path = root_folder + new_folder_path.split(root_folder, 1)[1]
                    #print ('new_folder_path:', new_folder_path)

                    # Add folder path string to master folder list for dictionary conversion
                    master_folder_list.append(new_folder_path)

            master_folder_list = []

            # Convert folder tree into list
            for folder in self.selection:
                root_folder = str(folder.name)[1:-1]

                get_folders(folder)

            # Convert folder list to dictionary
            self.folder_dict = {}

            for path in master_folder_list:
                p = self.folder_dict
                for x in path.split('/'):
                    p = p.setdefault(x, {})

            # If only a single empty library or folder, make dict root_folder
            if self.folder_dict == {}:
                self.folder_dict = {root_folder: {}}
            #print ('folder_dict:', self.folder_dict, '\n')

        def save_new_menu():

            # Set tokens for menu template file
            menu_template_token_dict = {}

            menu_template_token_dict['<FolderDict>'] = f'{self.folder_dict}'
            menu_template_token_dict['<TopItem>'] = self.top_item
            menu_template_token_dict['<TemplateMenuName>'] = self.menu_name
            menu_template_token_dict['<TemplateName>'] = self.name_entry.text
            #print ('menu_template_token_dict:', menu_template_token_dict, '\n')

            # Open menu template
            menu_template = open(self.menu_template_path, 'r')
            menu_template_lines = menu_template.read().splitlines()

            # Replace tokens in menu template
            for key, value in menu_template_token_dict.items():
                for line in menu_template_lines:
                    if key in line:
                        line_index = menu_template_lines.index(line)
                        new_line = re.sub(key, value, line)
                        menu_template_lines[line_index] = new_line

            # Save new menu
            out_file = open(self.menu_save_path, 'w')
            for line in menu_template_lines:
                print(line, file=out_file)
            out_file.close()

            # Close menu template
            menu_template.close()

        # Build folder or library tree
        get_tree()

        # Save new menu
        save_new_menu()

        self.window.close()

        PyFlameMessageWindow(
            message=f'Menu created: {self.name_entry.text}',
            parent=None,
            )

        flame.execute_shortcut('Rescan Python Hooks')

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_folder(selection):

    for item in selection:
        if isinstance(item, (flame.PyFolder)):
            return True
    return False

def scope_library(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Create Template...',
            'actions': [
                {
                    'name': 'Create Folder Template',
                    'isVisible': scope_folder,
                    'execute': CreateTemplate,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Create Library Template',
                    'isVisible': scope_library,
                    'execute': CreateTemplate,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
