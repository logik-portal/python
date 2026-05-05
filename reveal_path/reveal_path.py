# Reveal Path
# Copyright (c) 2026 Michael Vaglienty
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
Script Name: Reveal Path
Script Version: 2.10.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 06.16.19
Update Date: 05.05.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Timeline / Media Panel / MediaHub / Batch

Description:

    Reveal the path of a clip, open clip, write node, or batch group shot folder in the finder or Media Hub.

Usage:

    Script Setup menu allows for setting the tokenized shot folder path for batch group shot folders.

    For batch group shot folder reveal, batch groups must have have a standard shot name or be tagged with a shot name tag.
        Shot name tag should be formatted as: ShotName: <shot_name>
        Example:
            ShotName: PYT_0010

        If no shot name tag is found/assigned, the batch group name is used to resolve the shot name token.
        Examples:
            PYT_0010_comp -> PYT_0010
            PYT0010_comp -> PYT0010
            PYT010_comp -> PYT010

    Path is copied to clipboard.

URL:

    https://logik-portal.com/scripts/#reveal_path

Menus:

    Script Setup:
        Flame Main Menu -> Logik Portal Script Setup -> Reveal Path Setup

    Right-click on clip in timeline -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in media panel -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in batch -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in media hub -> Reveal... -> Reveal Clip in Finder
    Right-click on Write File node in batch -> Reveal... -> Reveal in Finder
    Right-click on Write File node in batch -> Reveal... -> Reveal in MediaHub
    Right-click on batch group in media panel -> Reveal... -> Reveal Shot Folder in Finder / Reveal Shot Folder in MediaHub

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.10.0 05.05.26
        - Added ability to reveal shot folder for batch group in Finder and MediaHub.
        - Updated to PyFlameLib v5.3.1.

    v2.9.0 03.26.26
        - Updated to PyFlameLib v5.3.0.

    v2.8.0 04.03.25
        - Updated to PyFlameLib v4.3.0.
        - Fixed Bug: Revealing clip in MediaHub was not working.

    v2.7.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Script now only works with Flame 2023.2+.

    v2.6.0 08.15.24
        - Updated to PyFlameLib v3.0.0.

    v2.5.0 01.21.24
        - Updates to PySide.

    v2.4.0 07.27.23
        - Updated to PyFlameLib v2.0.0.
        - Updated to semantic versioning.

    v2.3 10.24.22
        - Write File node path translation improved.

    v2.2 05.26.22
        - Messages print to Flame message window - Flame 2023.1 and later
        - Path is copied to clipboard

    v2.1 10.21.21
        - Path that the MediaHub is currently open to can be revealed in Finder
        - Write File node render path can be revealed in the MediaHub or in Finder
        - Only the following tokens are currently supported with the write file node:
            project
            project nickname
            batch iteration
            batch name
            ext
            name
            shot name
            version padding
            version
            user
            user nickname

    v2.0 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7

    v1.5 05.12.21
        - Copy path to clipboard functionality moved to it's own script
        - Merged with Reveal in Mediahub script - Reveal in MediaHub options only work in Flame 2021.2
        - Clips in Timeline can now be revealed in Finder and Mediahub

    v1.4 05.08.21
        - Clips in MediaHub can now be revealed in Finder and have paths copied to clipboard

    v1.2 01.25.20
        - Menu option will now only show up when right-clicking on clips with file paths

    v1.1 08.11.19
        - Code cleanup
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re

import flame
from lib.pyflame_lib_reveal_path import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Reveal Path'
SCRIPT_VERSION = 'v2.10.0'

# ==============================================================================

def load_config() -> PyFlameConfig:
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

    return PyFlameConfig(
        config_values={
            'tokenized_shot_folder_path': '',
            },
        )

# ==============================================================================
# [Reveal in Finder]
# ==============================================================================

def reveal_timeline_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Timeline Clip {SCRIPT_VERSION}')

    open_finder(selection[0].file_path.rsplit('/', 1)[0])

def reveal_mediapanel_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Media Panel Clip {SCRIPT_VERSION}')

    open_finder(selection[0].versions[0].tracks[0].segments[0].file_path.rsplit('/', 1)[0])

def reveal_batch_clip_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Batch Clip {SCRIPT_VERSION}')

    open_finder(str(selection[0].media_path)[1:-1].rsplit('/', 1)[0])

def reveal_mediahub_clip_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Media Hub Clip {SCRIPT_VERSION}')

    open_finder(selection[0].path.rsplit('/', 1)[0])

def reveal_write_file_node_path_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Write File Node {SCRIPT_VERSION}')

    resolved_path = selection[0].get_resolved_media_path().rsplit('/', 1)[0]

    if os.path.isdir(resolved_path):
        open_finder(resolved_path)
    else:
        pyflame.print('Write File node path not found. May not exist until rendered.', print_type=PrintType.ERROR)

def open_finder(path: str):
    """
    Open Finder
    ===========

    Open the path in Finder and copy the path to the clipboard.

    Args:
    -----
        path (str):
            Path to open in Finder.
    """

    # Open path in Finder
    pyflame.open_in_finder(path)

    # Copy path to clipboard
    pyflame.copy_to_clipboard(path)

# ==============================================================================
# [Reveal in MediaHub]
# ==============================================================================

def reveal_timeline_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Timeline Clip {SCRIPT_VERSION}')

    if selection[0].type == 'Video Segment':
        open_media_hub(str(selection[0].file_path).rsplit('/', 1)[0])

def reveal_mediapanel_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Media Panel Clip {SCRIPT_VERSION}')

    open_media_hub(str(selection[0].versions[0].tracks[0].segments[0].file_path).rsplit('/', 1)[0])

def reveal_batch_clip_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Batch Clip {SCRIPT_VERSION}')

    open_media_hub(str(selection[0].media_path)[1:-1].rsplit('/', 1)[0])

def reveal_write_file_node_path_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Write File Node {SCRIPT_VERSION}')

    resolved_path = selection[0].get_resolved_media_path().rsplit('/', 1)[0]

    if os.path.isdir(resolved_path):
        open_media_hub(resolved_path)
    else:
        pyflame.print('Write File node path not found. May not exist until rendered.', print_type=PrintType.ERROR)

def open_media_hub(path):
    """
    Open MediaHub
    =============

    Open the path in MediaHub and copy the path to the clipboard.

    Args:
    -----
        path (str):
            Path to open in MediaHub.
    """

    print(f'Opening MediaHub: {path}', '\n')

    # Open path in MediaHub
    flame.go_to('MediaHub')
    flame.mediahub.files.set_path(path)

    # Copy path to clipboard
    pyflame.copy_to_clipboard(path)

    pyflame.print(f'Path opened in MediaHub: {path}', text_color=TextColor.GREEN)

# ==============================================================================
# [Reveal Batch Group Shot Folder]
# ==============================================================================

def reveal_batch_group_shot_folder_finder(selection):
    reveal_batch_group_shot_folder(selection, type='finder')

def reveal_batch_group_shot_folder_mediahub(selection):
    reveal_batch_group_shot_folder(selection, type='mediahub')

def reveal_batch_group_shot_folder(selection, type: str) -> None:
    """
    Reveal Batch Group Shot Folder
    ==============================

    Reveal the shot folder for a batch group in Finder or MediaHub.

    Batch group must have have a standard shot name or be tagged with a shot name tag.

    Shot name tag should be formatted as: ShotName: <shot_name>
    Example: ShotName: PYT_0010

    If no shot name tag is found, the batch group name is used to resolve the shot name token.
    Examples:
        PYT_0010_comp -> PYT_0010
        PYT0010_comp -> PYT0010
        PYT010_comp -> PYT010

    Args:
    -----
        selection (list):
            Selected batch group
        type (str):
            Type of reveal: 'finder' or 'mediahub'
    """

    pyflame.print_title(f'{SCRIPT_NAME} - Shot Folder {SCRIPT_VERSION}')

    settings = load_config()

    if not settings.tokenized_shot_folder_path:
        PyFlameMessageWindow(
            message='Tokenized shot folder path not set. Please set in setup.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Reveal Path Setup',
            message_type=MessageType.ERROR,
            parent=None,
            )
        return

    selection = selection[0]

    # Add shot name token to shot folder path
    tokenized_shot_folder_path = os.path.join(settings.tokenized_shot_folder_path, '<ShotName>')

    # Resolve shot folder path tokens
    resolved_tokenized_shot_folder_path = pyflame.resolve_tokens(tokenized_shot_folder_path, flame_pyobject=selection)

    if not os.path.isdir(resolved_tokenized_shot_folder_path):
        PyFlameMessageWindow(
            message=f'Shot folder path not found:\n\n{resolved_tokenized_shot_folder_path}',
            message_type=MessageType.ERROR,
            parent=None,
            )
        return

    # Reveal in Finder or MediaHub
    if type == 'finder': # Reveal in Finder
        # Open resolved shot folder path in Finder
        open_finder(resolved_tokenized_shot_folder_path)
    elif type == 'mediahub':
        # Open resolved shot folder path in MediaHub
        open_media_hub(resolved_tokenized_shot_folder_path)

# ==============================================================================
# [Script Setup]
# ==============================================================================

class RevealPathSetup:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        # Open main window
        self.main_setup_window()

    def main_setup_window(self) -> None:

        def browse_shot_folder_path() -> None:
            """
            Browse Shot Folder Path
            ================

            Browse to shot folder path and set shot folder path entry to selected path.
            """

            shot_folder_path = pyflame.file_browser(
                path=self.shot_folder_path_entry.text,
                title='Select Shot Folder Path',
                select_directory=True,
                window_to_hide=self.setup_window,
                )

            if shot_folder_path:
                self.shot_folder_path_entry.text = str(shot_folder_path)

        def save_config() -> None:
            """
            Save Config
            ===========

            Validate settings and save to config file then close window.
            """

            # Validate settings
            if not self.shot_folder_path_entry.text:
                PyFlameMessageWindow(
                    message='Shot folder path not set.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            # Save config
            self.settings.save_config(
                config_values={
                    'tokenized_shot_folder_path': self.shot_folder_path_entry.text,
                    }
                )

            # Close window
            self.setup_window.close()

        def close_window() -> None:

            self.setup_window.close()

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            return_pressed=save_config, # Save config then close window when return/enter is pressed
            escape_pressed=close_window, # Close window when escape is pressed
            grid_layout_columns=6,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.shot_folder_path_label = PyFlameLabel(
            text='Tokenized Shot Folder Path',
            )

        # Entries
        self.shot_folder_path_entry = PyFlameEntry(
            text=self.settings.tokenized_shot_folder_path,
            )

        # Token Menus
        self.shot_folder_path_token_menu = PyFlameTokenMenu(
            token_dest=self.shot_folder_path_entry,
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                'Sequence Name': '<SeqName>',
                'Sequence Name (All Caps)': '<SEQNAME>',
                },
            )

        # Buttons
        self.shot_folder_path_browse_button = PyFlameButton(
            text='Browse',
            connect=browse_shot_folder_path,
            )
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.shot_folder_path_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.shot_folder_path_entry, 0, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.shot_folder_path_token_menu, 0, 4)
        self.setup_window.grid_layout.addWidget(self.shot_folder_path_browse_button, 0, 5)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 2, 4)
        self.setup_window.grid_layout.addWidget(self.save_button, 2, 5)

        # ------------------------------------------------------------------------------

        self.shot_folder_path_entry.setFocus()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_timeline_clip(selection):

    for item in selection:
        if isinstance(item, flame.PySegment):
            if item.file_path != '':
                return True
    return False

def scope_batch_clip(selection):

    for item in selection:
        if item.type == 'Clip':
            clip_path = str(item.media_path)[1:-1].rsplit('/', 1)[0]
            if clip_path != '':
                return True
    return False

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            if item.versions[0].tracks[0].segments[0].file_path != '':
                return True
    return False

def scope_file(selection):

    for item in selection:
        item_path = str(item.path)
        item_ext = re.search(r'\.\w{3}$', item_path, re.I)
        if item_ext != (None):
            return True
    return False

def scope_write_file_node(selection):

    for item in selection:
        if item.type == 'Write File':
            return True
    return False

def scope_batch_group(selection):

    for item in selection:
        if isinstance(item, flame.PyBatch):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'Logik',
            'hierarchy': [],
            'actions': []
        },
        {
            'name': 'Logik Portal Script Setup',
            'hierarchy': ['Logik'],
            'order': 2,
            'actions': [
               {
                    'name': 'Reveal Path Setup',
                    'execute': RevealPathSetup,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_timeline_custom_ui_actions():

    return [
        {
            'name': 'Reveal...',
            'actions': [
                {
                    'name': 'Reveal Clip in Finder',
                    'isVisible': scope_timeline_clip,
                    'execute': reveal_timeline_finder,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Reveal Clip in MediaHub',
                    'isVisible': scope_timeline_clip,
                    'execute': reveal_timeline_mediahub,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Reveal...',
            'actions': [
                {
                    'name': 'Reveal Clip in Finder',
                    'isVisible': scope_clip,
                    'execute': reveal_mediapanel_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Clip in MediaHub',
                    'isVisible': scope_clip,
                    'execute': reveal_mediapanel_mediahub,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Shot Folder in Finder',
                    'isVisible': scope_batch_group,
                    'execute': reveal_batch_group_shot_folder_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Shot Folder in MediaHub',
                    'isVisible': scope_batch_group,
                    'execute': reveal_batch_group_shot_folder_mediahub,
                    'minimumVersion': '2025.1'
                },
            ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Reveal...',
            'actions': [
                {
                    'name': 'Reveal Clip in Finder',
                    'isVisible': scope_batch_clip,
                    'execute': reveal_batch_clip_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Clip in MediaHub',
                    'isVisible': scope_batch_clip,
                    'execute': reveal_batch_clip_mediahub,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Write File Path in Finder',
                    'isVisible': scope_write_file_node,
                    'execute': reveal_write_file_node_path_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Write File Path in MediaHub',
                    'isVisible': scope_write_file_node,
                    'execute': reveal_write_file_node_path_mediahub,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Shot Folder in Finder',
                    'isVisible': scope_batch_group,
                    'execute': reveal_batch_group_shot_folder_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Shot Folder in Finder',
                    'isVisible': scope_batch_group,
                    'execute': reveal_batch_group_shot_folder_finder,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Reveal Shot Folder in MediaHub',
                    'isVisible': scope_batch_group,
                    'execute': reveal_batch_group_shot_folder_mediahub,
                    'minimumVersion': '2025.1'
                },
            ]
        }
    ]

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': 'Reveal...',
            'actions': [
                {
                    'name': 'Reveal Clip in Finder',
                    'isVisible': scope_file,
                    'execute': reveal_mediahub_clip_finder,
                    'minimumVersion': '2025.1'
                },
            ]
        }
    ]
