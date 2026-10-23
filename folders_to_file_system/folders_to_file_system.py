# Folders To File System
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Folders to File System
Script Version: 1.7.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 03.26.23
Update Date: 10.23.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create folders in selected file system path from folders in selected Library or Folder.

URL:
    https://logik-portal.com/scripts/folders_to_file_system

Menus:

    Select Library or Folder in Media Panel -> Folders to File System

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.7.0 10.23.26
        - Fixed wrong folder paths when the selected folder's name is part of a parent, library, workspace or project name.
        - Fixed error when clips are selected along with libraries or folders.
        - Fixed permission error message not showing the selected path.
        - Errors creating folders are now shown instead of being hidden.
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

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

from __future__ import annotations

import os

import flame
from lib.pyflame_lib_folders_to_file_system import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Folders to File System'
SCRIPT_VERSION = 'v1.7.0'
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
        path: Any = pyflame.file_browser(
            path=self.settings.path,
            title='Select Folder',
            select_directory=True,
            )

        if path:
            print('Selected path:', path, '\n')
            if not os.access(path, os.W_OK):
                PyFlameMessageWindow(
                    message=f'You do not have permission to create folders in the selected path:\n\n{path}',
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

        def get_folders(folder, folder_path: str) -> None:
            """
            Get Folders
            ===========

            Add the path of every subfolder of folder to folder_list, relative to the selected item.

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
                folder_list.append(new_folder_path)

        folder_list = []

        # Convert folder tree into list of folders to create, skipping anything that isn't a library or folder
        for folder in self.selection:
            if isinstance(folder, (flame.PyLibrary, flame.PyFolder)):
                get_folders(folder, str(folder.name)[1:-1])

        # Create folders
        pyflame.print('Creating folders...')

        failed_folders = []

        for folder in folder_list:
            folder_path = os.path.join(path, folder)
            print(f'   {folder_path}')
            try:
                os.makedirs(folder_path, exist_ok=True)
            except Exception as e:
                pyflame.print(f'Failed to create folder: {folder_path} - {e}', print_type=PrintType.ERROR)
                failed_folders.append(f'{folder_path} - {e}')

        print('\n', end='')

        # Show one error window listing every folder that couldn't be created
        if failed_folders:
            failed_list = '\n'.join(failed_folders)
            PyFlameMessageWindow(
                message=f'Unable to create folders:\n\n{failed_list}',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

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
