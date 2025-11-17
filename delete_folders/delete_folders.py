# Delete Folders
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
Script Name: Delete Folders
Script Version: 2.10.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 10.04.20
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaHub - Files Tab

Description:

    Delete one or more folders along with contents in the MediaHub File Tab view

    *** WARNING - THIS WILL DELETE ALL SELECTED FOLDERS/SUBFOLDERS - THIS IS CAN NOT BE UNDONE***

URL:
    https://github.com/logik-portal/python/delete_folders

Menu:

    Right-click with folders selected -> Delete Selected Folders

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.10.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v2.9.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v2.8.0 12.16.24
        - Updated to PyFlameLib v3.3.0.
        - Added script install check.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script installed in different locations.

    v2.7.0 08.05.24
        - Updated to PyFlameLib v3.0.0.

    v2.6.0 01.24.24
        - Updates to PySide.

    v2.5.0 07.27.23
        - Updated to PyFlameLib v2.0.0.
        - Updated versioning to semantic versioning.

    v2.4 09.28.22
        - Updated menus for Flame 2023.2+.

    v2.3 05.24.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v2.2 03.14.22
        - Added delete confirmation

    v2.1 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import shutil
import flame

from lib.pyflame_lib_delete_folders import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Delete Folders'
SCRIPT_VERSION = 'v2.10.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

def delete_folders(selection):
    """
    Delete Folders
    ==============

    This cannot be undone!
    ----------------------

    Delete all files and sub-folders in selected folder(s).
    """

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    delete_files = PyFlameMessageWindow(
        message=(
            'Delete selected folder(s)?\n\n'
            'All files and sub-folders in selected folder(s) will be deleted.\n\n'
            'This cannot be undone!\n\n'
            'Are you sure you want to continue?'
            ),
        message_type=MessageType.WARNING,
        parent=None,
        )

    if delete_files:
        pyflame.print(
            text='Deleting Selected Folders:',
            underline=True,
            text_color=TextColor.GREEN,
            )
        for folder in selection:
            pyflame.print(
                text=f'{folder.path[:-1]}',
                print_type=PrintType.WARNING,
                new_line=False,
                )
            shutil.rmtree(folder.path)

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

        pyflame.print('\nSelected Folders Deleted', text_color=TextColor.GREEN)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_folder(selection):

    for item in selection:
        if 'FilesFolder' in str(item):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_mediahub_files_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Delete Selected Folders',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_folder,
                    'execute': delete_folders,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
