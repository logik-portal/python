# Reveal Path
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
Script Name: Reveal Path
Script Version: 2.8.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 06.16.19
Update Date: 04.03.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Timeline / Media Panel / MediaHub / Batch

Description:

    Reveal the path of a clip, open clip, or write node in the finder or Media Hub.

    Path is also copied to clipboard.

URL:
    https://github.com/logik-portal/python/reveal_path

Menus:

    Right-click on clip in timeline -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in media panel -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in batch -> Reveal... -> Reveal Clip in Finder / Reveal Clip in MediaHub
    Right-click on clip in media hub -> Reveal... -> Reveal Clip in Finder
    Right-click on Write File node in batch -> Reveal... -> Reveal in Finder
    Right-click on Write File node in batch -> Reveal... -> Reveal in MediaHub

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

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

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re

import flame
from lib.pyflame_lib_reveal_path import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Reveal Path'
SCRIPT_VERSION = 'v2.8.0'

print('\n')

#-------------------------------------
# [Reveal in Finder]
#-------------------------------------

def reveal_timeline_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Timeline Clip {SCRIPT_VERSION}')

    open_finder(selection[0].file_path.rsplit('/', 1)[0])

def reveal_mediapanel_finder(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Media Panel Clip {SCRIPT_VERSION}')

    open_finder(selection[0].versions[0].tracks[0].segments[0].file_path.rsplit('/', 1)[0])

def reveal_batch_finder(selection):

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

#-------------------------------------
# [Reveal in MediaHub]
#-------------------------------------

def reveal_timeline_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Timeline Clip {SCRIPT_VERSION}')

    if selection[0].type == 'Video Segment':
        open_media_hub(str(selection[0].file_path).rsplit('/', 1)[0])

def reveal_mediapanel_mediahub(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Media Panel Clip {SCRIPT_VERSION}')

    open_media_hub(str(selection[0].versions[0].tracks[0].segments[0].file_path).rsplit('/', 1)[0])

def reveal_batch_mediahub(selection):

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

    print(f'Opening MediaHub: {path}')

    # Open path in MediaHub
    flame.go_to('MediaHub')
    flame.mediahub.files.set_path(path)

    # Copy path to clipboard
    pyflame.copy_to_clipboard(path)

    pyflame.print(f'Path opened in MediaHub: {path}', text_color=TextColor.GREEN)

#-------------------------------------
# [Scopes]
#-------------------------------------

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

#-------------------------------------
# [Flame Menus]
#-------------------------------------

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
                    'name': 'Reveal Clip in Media Hub',
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
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Reveal Clip in Media Hub',
                    'isVisible': scope_clip,
                    'execute': reveal_mediapanel_mediahub,
                    'minimumVersion': '2023.2'
                }
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
                    'execute': reveal_batch_finder,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Reveal Clip in Media Hub',
                    'isVisible': scope_batch_clip,
                    'execute': reveal_batch_mediahub,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Reveal Write File Path in Finder',
                    'isVisible': scope_write_file_node,
                    'execute': reveal_write_file_node_path_finder,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Reveal Write File Path in Media Hub',
                    'isVisible': scope_write_file_node,
                    'execute': reveal_write_file_node_path_mediahub,
                    'minimumVersion': '2023.2'
                }
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
                    'minimumVersion': '2023.2'
                },
            ]
        }
    ]
