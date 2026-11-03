# Create New Folder
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Create New Folder
Script Version: 1.0.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 11.03.26
Update Date: 11.03.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: MediaHub Files

Description:

    Adds a pop-up entry field for naming new folders created in the MediaHub Files tab.
    Useful for creating folders when the on-screen keyboard preference is off in Flame preferences.

    Nested paths such as new_folder/new_folder can be entered. Every missing folder in the path is created.

    The name is checked before anything is created. It must be relative (no / at the start), with no empty,
    . or .. parts, no \\ : * ? " < > | or control characters, no spaces at the start or end of a part, and no
    part longer than 255 bytes. The folder to create in must still exist and be writable, and the new folder
    must not already exist.

Usage:

    With one or more folders selected, the new folder is created inside each selected folder.
    With nothing selected, the new folder is created in the folder MediaHub is showing.

    Enter the folder name, or a path such as new_folder/new_folder, then press Create or Return.

URL:

    https://logik-portal.com/scripts/create_new_folder

Menus:

    Right-click in MediaHub Files with a folder selected or nothing selected -> Create New Folder

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 11.03.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os

import flame
from lib.pyflame_lib_create_new_folder import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Create New Folder'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# Characters that break folder names on macOS, Linux or network shares
INVALID_CHARACTERS = '\\:*?"<>|'

# ==============================================================================
# [Main Script]
# ==============================================================================

class CreateNewFolder:

    def __init__(self, selection) -> None:

        # Folders to create the new folder in
        self.target_folders = self.get_target_folders(selection)
        if not self.target_folders:
            return

        self.main_window()

    def get_target_folders(self, selection) -> list:
        """
        Get Target Folders
        ==================

        Get the paths of the selected MediaHub folders. Items that aren't folders are ignored.
        With no folder selected, use the folder MediaHub is showing.

        Args
        ----
            selection (tuple): Selected MediaHub items.

        Returns
        -------
            target_folders (list):
                Folder paths to create the new folder in, without a trailing /. Empty if no folder is found.
        """

        selected_paths = [str(item.path) for item in selection if isinstance(item, flame.PyMediaHubFilesFolder)]

        # Nothing selected, use the folder MediaHub is showing. Flame versions without get_path show the error below instead of crashing
        if not selected_paths:
            try:
                current_path = str(flame.mediahub.files.get_path())
            except Exception:
                current_path = ''
            if current_path:
                selected_paths = [current_path]

        # Remove the trailing / MediaHub adds and skip folders selected more than once
        target_folders = []
        for path in selected_paths:
            path = path.rstrip('/') or '/'
            if path not in target_folders:
                target_folders.append(path)

        if not target_folders:
            PyFlameMessageWindow(
                message='No folder selected and the folder MediaHub is showing could not be found.',
                message_type=MessageType.ERROR,
                parent=None,
                )

        return target_folders

    def check_folder_name(self, folder_name: str) -> list:
        """
        Check Folder Name
        =================

        Check the folder name or path entered can be used to create folders.

        Args
        ----
            folder_name (str): Folder name or relative path, such as new_folder/new_folder.

        Returns
        -------
            problems (list):
                One message for each kind of problem found. Empty if the name can be used.
        """

        if not folder_name:
            return ['Enter a folder name.']

        problems = []

        parts = folder_name.split('/')

        # A leading / makes an absolute path, which os.path.join would use in place of the target folder
        if folder_name.startswith('/'):
            problems.append('The folder name can not start with /. Enter a name or a path inside the folder, such as: new_folder/new_folder')
            parts = parts[1:]

        if '' in parts:
            problems.append('The folder name has an empty part. Remove any // and any / at the end.')

        if '.' in parts or '..' in parts:
            problems.append('. and .. can not be used as folder names.')

        # List each character that can't be used once, in the order typed
        bad_characters = []
        has_control_characters = False
        for character in folder_name:
            if ord(character) < 32 or ord(character) == 127:
                has_control_characters = True
            elif character in INVALID_CHARACTERS and character not in bad_characters:
                bad_characters.append(character)
        if bad_characters:
            problems.append(f'These characters can not be used in a folder name: {"  ".join(bad_characters)}')
        if has_control_characters:
            problems.append('Control characters (such as tab) can not be used in a folder name.')

        spaced_parts = [part for part in parts if part and part != part.strip(' ')]
        if spaced_parts:
            problems.append('Folder names can not start or end with a space: ' + ', '.join(f"'{part}'" for part in spaced_parts))

        long_parts = [part for part in parts if len(part.encode('utf-8')) > 255]
        if long_parts:
            problems.append('Folder names can not be longer than 255 bytes: ' + ', '.join(f"'{part[:40]}...'" for part in long_parts))

        return problems

    def get_deepest_existing(self, path: str) -> str:
        """
        Get Deepest Existing
        ====================

        Get the deepest part of the path that exists on disk.

        Args
        ----
            path (str): Absolute path to check.

        Returns
        -------
            existing_path (str): The path itself if it exists, otherwise its deepest existing parent.
        """

        existing_path = path
        while not os.path.lexists(existing_path):
            existing_path = os.path.dirname(existing_path)

        return existing_path

    def check_location(self, target_folder: str, full_path: str) -> str:
        """
        Check Location
        ==============

        Check the new folder can be created in the target folder.

        Args
        ----
            target_folder (str):
                Folder to create the new folder in.

            full_path (str):
                Full path of the new folder.

        Returns
        -------
            reason (str): Why the folder can't be created. Empty if it can.
        """

        # MediaHub can still show folders that were deleted or moved
        if not os.path.isdir(target_folder):
            return f'This folder no longer exists, but MediaHub is still showing it: {target_folder}\nRefresh MediaHub and try again.'

        if os.path.lexists(full_path):
            return 'Already exists.'

        # New folders are created inside the deepest part of the path that already exists
        existing_path = self.get_deepest_existing(full_path)

        if not os.path.isdir(existing_path):
            return f'Not a folder: {existing_path}'

        if not os.access(existing_path, os.W_OK | os.X_OK):
            return f'No permission to create folders in: {existing_path}'

        return ''

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Build the window for entering the new folder name.
        """

        def create_folders() -> None:
            """
            Create Folders
            ==============

            Check the folder name, then create it in every target folder.
            Closes the window if at least one folder was created. Problems are shown in one message.
            """

            folder_name = self.folder_name_entry.text

            # Check the name first so the window stays open to fix it
            problems = self.check_folder_name(folder_name)
            if problems:
                PyFlameMessageWindow(
                    message='This folder name can not be used:\n\n' + '\n\n'.join(problems),
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )

                return

            created_paths = []
            failures = []

            # Set if os.makedirs fails part way, so MediaHub still shows the levels it made
            partly_created = False

            for target_folder in self.target_folders:
                full_path = os.path.join(target_folder, folder_name)

                reason = self.check_location(target_folder, full_path)
                if reason:
                    failures.append(f'{full_path}\n{reason}')
                    continue

                # Remember the deepest folder that exists before creating, to find any levels made before a failure
                existing_path = self.get_deepest_existing(full_path)

                try:
                    os.makedirs(full_path)
                except Exception as e:
                    failure = f'{full_path}\n{e}'
                    deepest_path = self.get_deepest_existing(full_path)
                    if deepest_path != existing_path:
                        partly_created = True
                        failure += f'\nPart of the path was created: {deepest_path}'
                    failures.append(failure)
                    continue

                created_paths.append(full_path)
                pyflame.print(f'Created folder: {full_path}', text_color=TextColor.GREEN)

            if created_paths or partly_created:
                flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

            # Keep the window open if nothing was created so the name can be changed
            if created_paths:
                self.window.close()

            if failures:
                PyFlameMessageWindow(
                    message='Could not create these folders:\n\n' + '\n\n'.join(failures),
                    message_type=MessageType.ERROR,
                    parent=None if created_paths else self.window,
                    )

        def close_window() -> None:
            """
            Close Window
            ============

            Close window.
            """

            self.window.close()

        # Show the folder when there's only one, otherwise how many. The tooltip lists the full paths
        if len(self.target_folders) == 1:
            location_text = self.target_folders[0]
        else:
            location_text = f'{len(self.target_folders)} selected folders'
        location_tooltip = '\n'.join(self.target_folders)

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=create_folders,
            escape_pressed=close_window,
            grid_layout_columns=4,
            grid_layout_rows=4,
            parent=None,
            )

        # Labels
        self.create_in_label = PyFlameLabel(
            text='Create In',
            )
        self.location_label = PyFlameLabel(
            text=location_text,
            )
        self.folder_name_label = PyFlameLabel(
            text='Folder Name',
            )

        # Show paths as they are on disk, even if they contain < or >
        self.location_label.setTextFormat(QtCore.Qt.TextFormat.PlainText)

        # Cut long paths at the start so the folder at the end stays visible. The label spans 3 grid columns
        self.location_label.text = QtGui.QFontMetrics(self.location_label.font()).elidedText(
            location_text,
            QtCore.Qt.TextElideMode.ElideLeft,
            pyflame.gui_resize(150) * 3,
            )
        self.location_label.setToolTip(location_tooltip)

        # Entries
        self.folder_name_entry = PyFlameEntry(
            placeholder_text='new_folder or new_folder/new_folder',
            )

        # Buttons
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )
        self.create_button = PyFlameButton(
            text='Create',
            connect=create_folders,
            color=Color.BLUE,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.window.grid_layout.addWidget(self.create_in_label, 0, 0)
        self.window.grid_layout.addWidget(self.location_label, 0, 1, 1, 3)

        self.window.grid_layout.addWidget(self.folder_name_label, 1, 0)
        self.window.grid_layout.addWidget(self.folder_name_entry, 1, 1, 1, 3)

        self.window.grid_layout.addWidget(self.cancel_button, 3, 2)
        self.window.grid_layout.addWidget(self.create_button, 3, 3)

        # ------------------------------------------------------------------------------

        self.folder_name_entry.set_focus()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_folder(selection) -> bool:
    """
    Scope Folder
    ============

    Show the menu when nothing is selected or at least one MediaHub folder is selected.

    Args
    ----
        selection (tuple): Selected MediaHub items.

    Returns
    -------
        visible (bool): True if the menu should be shown.
    """

    # Nothing selected uses the folder MediaHub is showing
    if not selection:
        return True

    for item in selection:
        if isinstance(item, flame.PyMediaHubFilesFolder):
            return True

    return False

# ==============================================================================
# [Entry Points]
# ==============================================================================

def create_new_folder(selection) -> None:

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    CreateNewFolder(selection)

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Create New Folder',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_folder,
                    'execute': create_new_folder,
                    'minimumVersion': '2025.2',
                },
            ],
        },
    ]
