# Create Media Panel Templates
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Create Media Panel Templates
Script Version: 3.10.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 05.01.19
Update Date: 10.28.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create templates from libraries and folders in the Media Panel.
    Right-click menus will be created for each template

URL:
    https://logik-portal.com/scripts/create_media_panel_templates

Menus:

    To create new template menus:
        Right-click on library or folder -> Create Template... -> Create Library Template / Create Folder Template

    Newly created templates:
        Right-click on library or folder -> Library/Folder Templates -> Select from saved templates

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.10.0 10.28.26
        - A / in the template name is now replaced with an underscore in the menu file name.
        - Generated folder templates now skip selected clips when run.
        - The overwrite warning now names the existing template when a different name uses the same menu file name.
        - Overwriting a template now names the template that will be replaced, and the old template is only removed after the new one is written.
        - Fixed template names with an apostrophe or quote creating a menu with a syntax error.
        - Fixed empty folders being left out when several items are selected.
        - Fixed wrong template tree when the selected item's name is part of a parent, library or workspace name.
        - Clips in the selection are now ignored instead of stopping the script.
        - Fixed template names with a backslash causing an error or a wrong menu name.
        - An empty template name now shows an error instead of creating a hidden menu file.
        - Fixed library templates creating their libraries once for each selected item.

    v3.9.1 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

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

from __future__ import annotations

import ast
import os

import flame
from lib.pyflame_lib_create_media_panel_templates import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Create Media Panel Templates'
SCRIPT_VERSION = 'v3.10.0'
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
                self.targets = '[item for item in selection if isinstance(item, (flame.PyFolder, flame.PyLibrary))]'
                self.item_name = str(item.name)[1:-1]
                self.creation_type = 'Folder'
                self.menu_name = 'Folder Templates...'
                break

        for item in self.selection:
            if isinstance(item, (flame.PyLibrary)):
                self.top_item = 'flame.project.current_project.current_workspace.create_library'
                self.targets = 'selection[:1]'
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

        def existing_template_name(menu_path: str) -> str:
            """
            Existing Template Name
            ======================

            Get the template name of an existing menu file from its docstring, without running it.
            Falls back to the file name if the file can't be parsed.

            Args
            ----
                menu_path (str): Path of existing menu file.

            Returns
            -------
                template_name (str): Template name of existing menu.
            """

            try:
                with open(menu_path, 'r') as menu_file:
                    docstring = ast.get_docstring(ast.parse(menu_file.read()))
                for line in docstring.splitlines():
                    if line.startswith('Script Name:') and 'Menu: ' in line:
                        return line.split('Menu: ', 1)[1]
            except Exception:
                pass

            return os.path.basename(menu_path)[:-3]

        # Stop if template name is empty
        if not self.name_entry.text.strip():
            PyFlameMessageWindow(
                message='Enter a template name.',
                message_type=MessageType.ERROR,
                parent=self.window,
                )
            return

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
        menu_file_name = menu_file_name.replace('.', '_').replace('/', '_') + '.py'

        # Set possible menu save paths
        folder_menu_file_path = os.path.join(self.folder_menus, menu_file_name)
        library_menu_file_path = os.path.join(self.library_menus, menu_file_name)

        # Select menu file save path. Template names are unique across both types, so a same-named template of the other type gets replaced.
        if self.creation_type == 'Folder':
            self.menu_save_path = folder_menu_file_path
            other_menu_file_path = library_menu_file_path
            other_type = 'Library'
        elif self.creation_type == 'Library':
            self.menu_save_path = library_menu_file_path
            other_menu_file_path = folder_menu_file_path
            other_type = 'Folder'

        # Check if menu file name already exists, overwrite?
        template_name = self.name_entry.text
        same_type_exists = os.path.isfile(self.menu_save_path)
        other_type_exists = os.path.isfile(other_menu_file_path)

        # Get existing template names, they can differ from the typed name but share the file name (a.b, a_b, a/b)
        same_type_name = existing_template_name(self.menu_save_path) if same_type_exists else template_name
        other_type_name = existing_template_name(other_menu_file_path) if other_type_exists else template_name

        if same_type_exists and other_type_exists:
            file_name_note = ' and use the same file name' if template_name != same_type_name or template_name != other_type_name else ''
            overwrite_message = f"{self.creation_type} template '{same_type_name}' and {other_type} template '{other_type_name}' already exist{file_name_note}. Replace both with the new {self.creation_type} template?"
        elif same_type_exists:
            file_name_note = ' and uses the same file name' if same_type_name != template_name else ''
            overwrite_message = f"{self.creation_type} template '{same_type_name}' already exists{file_name_note}. Overwrite?"
        elif other_type_exists:
            file_name_note = ' and uses the same file name' if other_type_name != template_name else ''
            overwrite_message = f"{other_type} template '{other_type_name}' already exists{file_name_note}. Replace it with a {self.creation_type} template?"

        if same_type_exists or other_type_exists:
            if not PyFlameMessageWindow(
                message=overwrite_message,
                message_type=MessageType.WARNING,
                parent=self.window,
                ):
                return

        # Other type menu is removed only after the new menu is written
        self.other_menu_file_path = other_menu_file_path if other_type_exists else None

        return self.create_new_template()

    def create_new_template(self):

        def get_tree():

            def get_folders(folder, folder_path: str) -> None:
                """
                Get Folders
                ===========

                Add the path of every subfolder of folder to master_folder_list, relative to the selected item.

                Args
                ----
                    folder (PyLibrary | PyFolder):
                        Library or folder to get subfolders from.

                    folder_path (str):
                        Path of folder, starting with the selected item's name.
                """

                for folders in folder.folders:
                    new_folder_path = f'{folder_path}/{str(folders.name)[1:-1]}'

                    get_folders(folders, new_folder_path)

                    # Add folder path string to master folder list for dictionary conversion
                    master_folder_list.append(new_folder_path)

            master_folder_list = []

            # Convert folder tree into list, skipping anything that isn't a library or folder
            for folder in self.selection:
                if isinstance(folder, (flame.PyFolder, flame.PyLibrary)):
                    root_folder = str(folder.name)[1:-1]

                    # Add selected item itself so empty items are still top-level keys
                    master_folder_list.append(root_folder)

                    get_folders(folder, root_folder)

            # Convert folder list to dictionary
            self.folder_dict = {}

            for path in master_folder_list:
                p = self.folder_dict
                for x in path.split('/'):
                    p = p.setdefault(x, {})
            #print ('folder_dict:', self.folder_dict, '\n')

        def save_new_menu():

            # Set tokens for menu template file
            menu_template_token_dict = {}

            menu_template_token_dict['<FolderDict>'] = f'{self.folder_dict}'
            menu_template_token_dict['<TopItem>'] = self.top_item
            menu_template_token_dict['<TemplateMenuName>'] = self.menu_name
            menu_template_token_dict['<Targets>'] = self.targets

            # Escape backslashes and quotes so the name is valid inside the template's quoted strings and docstring
            menu_template_token_dict['<TemplateName>'] = self.name_entry.text.replace('\\', '\\\\').replace('\'', '\\\'').replace('"', '\\"')
            #print ('menu_template_token_dict:', menu_template_token_dict, '\n')

            # Open menu template
            menu_template = open(self.menu_template_path, 'r')
            menu_template_lines = menu_template.read().splitlines()

            # Replace tokens in menu template
            for key, value in menu_template_token_dict.items():
                for line in menu_template_lines:
                    if key in line:
                        line_index = menu_template_lines.index(line)
                        new_line = line.replace(key, value)
                        menu_template_lines[line_index] = new_line

            # Save new menu to a temp file first, then move it over the old menu so a failed write never leaves a broken menu
            temp_menu_path = self.menu_save_path + '.tmp'
            try:
                with open(temp_menu_path, 'w') as out_file:
                    for line in menu_template_lines:
                        print(line, file=out_file)
                os.replace(temp_menu_path, self.menu_save_path)
            except Exception:
                if os.path.isfile(temp_menu_path):
                    os.remove(temp_menu_path)
                raise

            # Close menu template
            menu_template.close()

        # Build folder or library tree
        get_tree()

        # Save new menu
        try:
            save_new_menu()
        except Exception as e:
            PyFlameMessageWindow(
                message=f'Could not save menu: {e}',
                message_type=MessageType.ERROR,
                parent=self.window,
                )
            return

        # Remove same-named menu of the other type now that the new menu is saved
        if self.other_menu_file_path:
            try:
                os.remove(self.other_menu_file_path)
                pyflame.print(f'Old menu deleted: {self.other_menu_file_path}')
            except Exception as e:
                pyflame.print(f'Could not delete old menu: {self.other_menu_file_path} - {e}', print_type=PrintType.ERROR)

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
