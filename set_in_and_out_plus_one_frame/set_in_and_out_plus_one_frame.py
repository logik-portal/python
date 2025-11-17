# Set In And Out Plus One Frame
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
Script Name: Set In and Out Plus One Frame
Script Version: 1.3.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 05.01.24
Update Date: 04.03.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Sets in and out marks for selected sequences/clips to their full duration, plus one additional frame.
    This extra frame ensures a clean black frame at the end of exports when using Export Between Marks.

URL:
    https://github.com/logik-portal/python/set_in_and_out_plus_one_frame

Menus:

    Right-click on selected sequences/clips in the Media Panel -> Set In and Out -> Set In and Out +1 Frame of Black

To install:

    Copy script into /opt/Autodesk/shared/python/set_in_and_out_plus_one_frame

Updates:

    v1.3.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.2.0 12.31.24
        - Updated to PyFlameLib v4.0.0.

    v1.1.0 08.12.24
        - Updated to PyFlameLib v3.0.0.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame

from lib.pyflame_lib_set_in_and_out_plus_one_frame import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Set In and Out Plus One Frame'
SCRIPT_VERSION = 'v1.3.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class SetInAndOutPlusOne():

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Set in and out marks for selected sequences
        self.set_in_out(selection)

    def set_in_out(self, selection) -> None:
        """
        Set In Out
        ==========

        Set in and out marks for selected sequences.

        Switch to Timeline tab if not already in Timeline tab.
        If not already in Timeline tab, switch back to original tab after setting in and out marks.

        Args:
            selection (list):
                List of selected items.
        """

        pyflame.print('Setting new in and out marks for sequence.')

        # Get current tab
        current_tab = flame.get_current_tab()

        # If current tab is not Timeline, switch to Timeline
        if not current_tab == 'Timeline':
            flame.set_current_tab('Timeline')
            pyflame.print('Switching to Timeline tab...')

        # Loop through all sequences in the selection
        for sequence in selection:
            if isinstance(sequence, (flame.PySequence, flame.PyClip)):
                pyflame.print(f'Sequence Name: {str(sequence.name)[1:-1]}', new_line=False)
                print('Sequence Start Time:', sequence.start_time)
                print('Sequence Frame Rate:', sequence.frame_rate)
                print('Sequence Duration:', sequence.duration, '\n')

                if str(sequence.start_time).startswith('-'):
                    PyFlameMessageWindow(
                        message='Sequence Start Time cannot be negative.\n\n'
                                'Selected Sequence Start Time: ' + str(sequence.start_time) + '\n\n'
                                'Please check the sequence start time and try again.',
                        type=MessageType.ERROR,
                        )
                    return

                # Clear in and out marks
                sequence.in_mark = None
                sequence.out_mark = None

                # Set in and out marks
                sequence.in_mark = flame.PyTime(f'{str(sequence.start_time)}', f'{str(sequence.frame_rate)}')
                sequence.out_mark = flame.PyTime(int(sequence.duration.frame) + 2)
                pyflame.print(f'Sequence In Set: {sequence.in_mark}')
                pyflame.print(f'Sequence Out Set: {sequence.out_mark}')

        if not current_tab == 'Timeline':
            flame.set_current_tab(current_tab)
            pyflame.print(f'Switching back to {current_tab} tab...')

        pyflame.print('In and Out marks set for selected sequences/clips.', text_color=TextColor.GREEN)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_seq(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence, flame.PyClip)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Set In and Out',
            'actions': [
                {
                    'name': 'Set In and Out +1 Frame of Black',
                    'isVisible': scope_seq,
                    'execute': SetInAndOutPlusOne,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
