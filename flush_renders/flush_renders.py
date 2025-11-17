# Flush Renders
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
Script Name: Flush Renders
Script Version: 1.3.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 08.05.24
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Flush renders for all clips/sequences in selected folder or library.

URL:
    https://github.com/logik-portal/python/flush_renders

Menus:

    Right-click on Folder or Library in Media Panel -> Flush Renders

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.3.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v1.2.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.1.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame
from lib.pyflame_lib_flush_renders import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Flush Renders'
SCRIPT_VERSION = 'v1.3.0'

#-------------------------------------
# [Main Script]
#-------------------------------------

class Flusher:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Set selection
        self.selection = selection

        # Flush
        self.flush()

    def flush(self) -> None:
        """
        Flush
        =====

        Loop through selection(Library or Folder) and flush renders for all clips/sequences.
        """

        def flush_item(item) -> None:

            # If item is a clip or sequence, flush
            if isinstance(item, (flame.PyClip, flame.PySequence)):
                print('    Flushing render for:', item.name)
                item.flush_renders()

        def flush_folder(folder) -> None:
            """
            Flush Folder
            ============

            Flush renders for any clips or sequences in the selected folder and all its subfolders.

            Args:
            -----
                folder (flame.PyFolder):
                    Folder to flush renders for.
            """

            # Loop through each item in the folder
            for item in folder.children:
                flush_item(item)

            # Loop through each subfolder
            for subfolder in folder.folders:
                flush_folder(subfolder)

        def flush_library(library) -> None:
            """
            Flush Library
            =============

            Flush renders for any clips or sequences in the selected library and all its subfolders.

            Args:
            -----
                library (flame.PyLibrary):
                    Library to flush renders for.
            """

            # Loop through each item in the library
            for item in library.children:
                flush_item(item)

                # If item is a folder, flush caches of items in folder
                if isinstance(item, flame.PyFolder):
                    flush_folder(item)

        if not PyFlameMessageWindow(
            message='Are you sure you want to flush the renders for the selected items?\n\nThis will clear the renderss for all clips and sequences in the selected folder or library and all subfolders.\n\nContinue?',
            message_type=MessageType.CONFIRM,
            parent=None,
            ):
            return

        pyflame.print('Flushing renders...')

        # Loop through selection and flush caches
        for item in self.selection:
            if isinstance(item, flame.PyLibrary):
                flush_library(item)
            if isinstance(item, flame.PyFolder):
                flush_folder(item)

        print('\n', end='')

        pyflame.print('Renders have been flushed.', text_color=TextColor.GREEN)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope(selection):

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
                    'name': 'Flush Renders',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope,
                    'execute': Flusher,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
