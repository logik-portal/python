# Delete Empty Folders
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Delete Empty Folders
Script Version: 1.7.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 11.15.23
Update Date: 10.23.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Delete any empty folders in selected Library or Folder.

URL:
    https://logik-portal.com/scripts/delete_empty_folders

Menu:

    Right-click on Folder or Library in Media Panel -> Delete Empty Folders

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.7.0 10.23.26
        - Fixed Flame hanging when an empty folder can't be deleted. Folders that can't be deleted are listed in one message.
        - Fixed error when clips are selected along with libraries or folders.
        - Folders are now deleted without a confirmation prompt for each folder.
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.6.0 03.31.26
        - Updated to PyFlameLib v5.3.0.

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

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os
import flame
from lib.pyflame_lib_delete_empty_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Delete Empty Folders'
SCRIPT_VERSION = 'v1.7.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

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

        def check_folders(root_folder, failed_folders: list) -> None:
            """
            Check Folders
            =============

            Delete empty folders in root folder until none are left. Folders that can't be deleted are added to
            failed_folders and not retried.

            Args
            ----
                root_folder (PyLibrary or PyFolder):
                    Library or folder to delete empty folders from.

                failed_folders (list):
                    List of folders that couldn't be deleted. Each item is (folder, error message).
            """

            failed_count = len(failed_folders)
            attempted_folders = []

            while True:
                # Find empty folders, skipping folders that were already attempted
                failed = [failed_folder for failed_folder, error in failed_folders]
                empty_folders = []
                for folder in find_empty_folders(root_folder):
                    if folder not in attempted_folders:
                        empty_folders.append(folder)
                    elif folder not in failed:
                        # Delete returned True but folder still exists, record as failed so it isn't retried
                        folder_name = str(folder.name)[1:-1]
                        pyflame.print(f'Could not delete folder: {folder_name} - still there after delete', print_type=PrintType.ERROR)
                        failed_folders.append((folder, f'{folder_name} - still there after delete'))
                        failed.append(folder)

                # If no new empty folders, break the loop
                if not empty_folders:
                    break

                # Delete found empty folders
                deleted = False
                for folder in empty_folders:
                    folder_name = str(folder.name)[1:-1]
                    pyflame.print(f'Deleting empty folder: {folder_name}')
                    attempted_folders.append(folder)
                    try:
                        if flame.delete(folder, confirm=False):
                            deleted = True
                        else:
                            pyflame.print(f'Could not delete folder: {folder_name}', print_type=PrintType.ERROR)
                            failed_folders.append((folder, folder_name))
                    except Exception as e:
                        pyflame.print(f'Could not delete folder: {folder_name} - {e}', print_type=PrintType.ERROR)
                        failed_folders.append((folder, f'{folder_name} - {e}'))

                # Stop if nothing could be deleted so the loop can't run forever
                if not deleted:
                    break

            if len(failed_folders) == failed_count:
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

        failed_folders = []

        # Loop through selected libraries and folders and check for empty folders. Skip anything else.
        for folder in self.selection:
            if isinstance(folder, (flame.PyLibrary, flame.PyFolder)):
                check_folders(folder, failed_folders)

        # Show one message listing folders that couldn't be deleted
        if failed_folders:
            failed_list = '\n'.join(error for failed_folder, error in failed_folders)
            PyFlameMessageWindow(
                message=f'Could not delete these empty folders:\n\n{failed_list}',
                message_type=MessageType.ERROR,
                parent=None,
                )

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_library_folder(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary, flame.PyFolder)):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

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
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
