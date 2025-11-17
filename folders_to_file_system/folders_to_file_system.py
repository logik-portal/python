# Folders To File System
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
Script Name: Folders to File System
Script Version: 1.6.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 03.26.23
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create folders in selected file system path from folders in selected Library or Folder.

URL:
    https://github.com/logik-portal/python/folders_to_file_system

Menus:

    Select Library or Folder in Media Panel -> Folders to File System

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.6.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v1.5.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.4.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.3.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v1.2.0 01.21.24
        - Updates to PySide.

    v1.1.0 08.20.23
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_folders_to_file_system import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Folders to File System'
SCRIPT_VERSION = 'v1.6.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class FoldersToFileSystem:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Set selection
        self.selection = selection

        # Open file browser to select folder to create folders in
        self.select_path()

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
                'path': '/'
                }
            )

        return settings

    def select_path(self):
        """
        Select Path
        ===========

        Open file browser to select folder to create folders in.
        """

        # Open file browser to select folder to create folders in
        path = pyflame.file_browser(
            path=self.settings.path,
            title='Select Folder',
            select_directory=True,
            )

        if path:
            print('Selected path:', path, '\n')
            if not os.access(path, os.W_OK):
                PyFlameMessageWindow(
                    message='You do not have permission to create folders in the selected path:\n\n{path}',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return
            else:
                # Save selected path to config file
                self.settings.save_config(
                    config_values={
                        'path': path
                        }
                    )

                # Create folders
                self.create_folders(path)

    def create_folders(self, path):
        """
        Create Folders
        ==============

        Create folders in selected file system path from folders in selected Library or Folder.

        Args
        ----
            path (str):
                Path to create folders in.
        """

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

                # Convert folder list to string
                new_folder_path = '/'.join(folder_path_list)
                new_folder_path = root_folder + new_folder_path.split(root_folder, 1)[1]

                # Add folder path string to master folder list for dictionary conversion
                folder_list.append(new_folder_path)

        folder_list = []

        # Convert folder tree into list of folders to create
        for folder in self.selection:
            root_folder = str(folder.name)[1:-1]
            get_folders(folder)

        # Create folders
        pyflame.print('Creating folders...')

        for folder in folder_list:
            folder_path = os.path.join(path, folder)
            print(f'   {folder_path}')
            try:
                os.makedirs(folder_path)
            except:
                pass

        print('\n', end='')

        PyFlameMessageWindow(
            message=f'Folders Created Successfully\n\n{path}',
            parent=None,
            )

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_library_folder(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary, flame.PyFolder)):
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
                    'name': 'Folders to File System',
                    'order': 1,
                    'separator': 'below',
                    'execute': FoldersToFileSystem,
                    'isVisible': scope_library_folder,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
