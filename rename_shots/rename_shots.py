# Rename Shots
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
Script Name: Rename Shots
Script Version: 1.12.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 04.05.22
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel/Timeline

Description:

    Save clip and/or shot name naming patterns with tokens, then apply both to segments in a timeline.

    <index> token does not work as expected in python. Use other tokens to rename shots.

URL:
    https://github.com/logik-portal/python/rename_shots

Menus:

    Timeline:
        Right-click on selected segments -> Rename Shots

    Media Panel:
        Right-click on selected sequence -> Rename Shots

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.12.0 01.03.26
        - Progress messages print to script window

    v1.11.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes window.
        - Tab-key now moves focus between clip and shot name entry fields.

    v1.10.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.9.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.8.0 08.05.24
        - Updated to PyFlameLib v3.0.0.

    v1.7.0 01.02.24
        - Updates to UI/PySide.
        - Fixed scoping issue with Flame 2023.2+ menus.

    v1.6.0 07.25.23
        - Updated to PyFlameLib v2.0.0.

    v1.5.1 06.26.23
        - Updated script versioning to semantic versioning.
        - Clip Name entry field now has focus when window opens.
        - Pressing enter in Clip Name or Shot Name entry field now applies names.

    v1.5 02.04.23
        - Added check to make sure script is installed in the correct location.

    v1.4 01.19.23
        - Updated config file loading/saving.

    v1.3 10.24.22
        - Updated menus for Flame 2023.2+:
            - Timeline:
                Right-click on selected segments -> Rename Shots
            - Media Panel:
                Right-click on selected sequence -> Rename Shots

    v1.2 05.24.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v1.1 05.11.22
        - Removed setup window and eliminated sequence entry to simplify UI.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_rename_shots import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Rename Shots'
SCRIPT_VERSION = 'v1.12.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class RenameShots:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Make sure no cuts or transitions are selected
        self.selection = [s for s in selection if s.type == 'Video Segment' or isinstance(s, flame.PySequence)]

        self.main_window()

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
                'clip_name': '',
                'shot_name': '',
                'clip_name_tag': True,
                'shot_name_tag': True,
                }
            )

        return settings

    def main_window(self):

        def save_config():
            """
            Save Config
            ===========

            Save config values to config file.
            """

            # Save config file
            self.settings.save_config(
                config_values={
                    'clip_name': self.clip_name_entry.text,
                    'shot_name': self.shot_name_entry.text,
                    }
                )

        def apply():
            """
            Apply
            =====

            Apply clip, shot names to segments and tagging if selected.
            """

            # Make sure at least one shot name field is filled in
            if not self.clip_name_entry.text and not self.shot_name_entry.text:
                PyFlameMessageWindow(
                    message='At least one shot name field must be filled in.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Save config
            save_config()

            # Apply names to segments
            self.process_segments()

            PyFlameMessageWindow(
                message='Names applied to segments.',
                parent=None,
                )

            # Close window
            self.window.close()

        def close_window():
            """
            Close Window
            ============

            Close window and cancel changes.
            """

            self.window.close()

        # Create window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=apply,
            escape_pressed=close_window,
            grid_layout_columns=4,
            grid_layout_rows=5,
            grid_layout_adjust_column_widths={0: 100},
            parent=None,
            )

        # Labels
        self.name_pattern_label = PyFlameLabel(
            text='Name Pattern',
            style=Style.UNDERLINE,
            )
        self.clip_name_label = PyFlameLabel(
            text='Clip Name',
            )
        self.shot_name_label = PyFlameLabel(
            text='Shot Name',
            )

        # Entries
        self.clip_name_entry = PyFlameEntry(
            text=self.settings.clip_name,
            )
        self.shot_name_entry = PyFlameEntry(
            text=self.settings.shot_name,
            )

        # Token Push Buttons
        name_tokens = {
            'Souce Name': '<source name>',
            'Segment Index': '<segment>',
            'Segment Name': '<segment name>',
            'Shot Name': '<shot name>',
            'Background Index': '<background segment>',
            'Background Name': '<background name>',
            'Background Shot Name': '<background shot name>',
            'Track': '<track>',
            'Track Name': '<track name>',
            'Record Frame': '<record frame>',
            'Event Number': '<event number>',
            'Tape/Reel/Source': '<tape>',
            'Resolution': '<resolution>',
            'Width': '<width>',
            'Height': '<height>',
            'Depth': '<depth>',
            'Colour Space': '<colour space>',
            'Source Version Name': '<source version name>',
            'Source Version ID': '<source version>',
            'Clip Name': '<name>',
            'Date': '<date>',
            'Time': '<time>',
            'Year YYYYY': '<YYYY>',
            'Year YY': '<YY>',
            'Month': '<MM>',
            'Day': '<DD>',
            'Hour': '<hh>',
            'Minute': '<mm>',
            'Second': '<ss>',
            'Workstation': '<workstation>',
            'User NickName': '<user nickname',
            'User': '<user>',
            'Project Nickname': '<project nickname>',
            'Project': '<project>'
            }

        self.clip_name_token_button = PyFlameTokenMenu(
            text='Tokens',
            token_dict=name_tokens,
            token_dest=self.clip_name_entry,
            )
        self.shot_name_token_button = PyFlameTokenMenu(
            text='Tokens',
            token_dict=name_tokens,
            token_dest=self.shot_name_entry,
            )

        # Buttons
        self.apply_button = PyFlameButton(
            text='Apply',
            connect=apply,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.name_pattern_label, 0, 1, 1, 3)

        self.window.grid_layout.addWidget(self.shot_name_label, 1, 0)
        self.window.grid_layout.addWidget(self.shot_name_entry, 1, 1, 1, 2)
        self.window.grid_layout.addWidget(self.shot_name_token_button, 1, 3)

        self.window.grid_layout.addWidget(self.clip_name_label, 2, 0)
        self.window.grid_layout.addWidget(self.clip_name_entry, 2, 1, 1, 2)
        self.window.grid_layout.addWidget(self.clip_name_token_button, 2, 3)

        self.window.grid_layout.addWidget(self.cancel_button, 4, 2)
        self.window.grid_layout.addWidget(self.apply_button, 4, 3)

        #-------------------------------------

        # Set Tab-key Order
        self.window.tab_order = [self.shot_name_entry, self.clip_name_entry]

        # Set window focus to shot name entry
        self.shot_name_entry.set_focus()

    def process_segments(self):
        """
        Process Segments
        ===============

        Apply clip names and shot names to selected segments.
        """

        def rename_segment(segment):
            """
            Rename Segment
            ==============

            Rename segment with clip and/or shot name.
            """

            if self.settings.shot_name:
                segment.tokenized_shot_name = self.settings.shot_name
                self.window.print(f'Shot Name: {str(segment.shot_name)[1:-1]}')
            if self.settings.clip_name:
                segment.tokenized_name = self.settings.clip_name
                self.window.print(f'Clip Name: {str(segment.name)[1:-1]}')

        pyflame.print('Renaming Shots:')

        try:
            # If selection is segments, rename segments
            if isinstance(self.selection[0], flame.PySegment):
                for segment in self.selection:
                    rename_segment(segment)
                    print('\n', end='')

            # If selection is sequence, rename segments in selected sequence
            elif isinstance(self.selection[0], flame.PySequence):
                for version in self.selection[0].versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            rename_segment(segment)
                            print('\n', end='')

            pyflame.print('Shot Renaming Complete.')

        except RuntimeError:
            PyFlameMessageWindow(
                message='Clip is locked. Open the sequence or disable protect from editing in Flame preferences.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False

def scope_segment(selection):

    for item in selection:
        if isinstance(item, flame.PySegment):
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
                    'name': 'Rename Shots',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_sequence,
                    'execute': RenameShots,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_timeline_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Rename Shots',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_segment,
                    'execute': RenameShots,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
