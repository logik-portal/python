# Delete Empty Folders
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
Script Name: Delete Empty Folders
Script Version: 1.5.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 11.15.23
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Delete any empty folders in selected Library or Folder.

URL:
    https://github.com/logik-portal/python/delete_empty_folders

Menu:

    Right-click on Folder or Library in Media Panel -> Delete Empty Folders

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.5.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v1.4.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.3.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.2.0 08.09.24
        - Updated to PyFlameLib v3.0.0.

    v1.1.0 01.21.24
        - Updates to PySide.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_delete_empty_folders import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Delete Empty Folders'
SCRIPT_VERSION = 'v1.5.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class DeleteEmptyFolders:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        self.delete_empty_folders()

    def delete_empty_folders(self):
        """
        Delete Empty Folders
        ====================

        Loop through selection(Library or Folder) and delete empty folders.
        """

        def check_folders(root_folder):

            while True:
                # Find empty folders
                empty_folders = find_empty_folders(root_folder)

                # If no empty folders, break the loop
                if not empty_folders:
                    break

                # Delete found empty folders
                for folder in empty_folders:
                    pyflame.print(f'Deleting empty folder: {str(folder.name)[1:-1]}')
                    flame.delete(folder)

            pyflame.print('All empty folders have been deleted.', text_color=TextColor.GREEN)

        def find_empty_folders(folder, parent=None):

            empty_folders = []

            # Iterate through each subfolder
            for subfolder in list(folder.folders):
                # Recursively check each subfolder
                empty_folders.extend(find_empty_folders(subfolder, folder))

            # Check if the current folder is empty
            if not folder.children and not folder.folders and parent is not None:
                empty_folders.append(folder)

            return empty_folders

        pyflame.print('Checking for and deleting empty folders...')

        # Loop through selection and check for empty folders
        for folder in self.selection:
            check_folders(folder)

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
                    'name': 'Delete Empty Folders',
                    'order': 1,
                    'separator': 'below',
                    'execute': DeleteEmptyFolders,
                    'isVisible': scope_library_folder,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
