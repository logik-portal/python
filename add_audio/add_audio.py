# Add Audio
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
Script Name: Add Audio
Script Version: 1.4.0
Flame Version: 2023
Written by: Michael Vaglienty
Creation Date: 02.04.22
Update Date: 01.20.24

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Add stereo or 5.1 audio to selected sequences.

    To add stereo audio to a sequence, select the sequence then select the audio clip to be added.
    To add stereo audio to multiple sequences, select in sequence/audio/sequence/audio... order.

    To add 5.1 surround audio to a sequence, select the sequence followed by all the audio channels(LF, RF, C, LFE, LS, RS, Stereo)
    To add 5.1 surround audio to multiple sequences, select in sequence/all audio channels/sequences/all audio channels... order.

    Order of 5.1 surround files does not matter when being selected.
    When added to the sequence they will be put in this order: LF, RF, C, LFE, LS, RS, Stereo

    5.1 surround file names must end with _LF, _RF, _C, _LFE, _LS, _RS, or _Stereo. Case is not important.

URL:
    https://github.com/logik-portal/python/add_audio

Menus:

    Right-click selection of sequences and audio -> Audio -> Insert Stereo Audio - 01:00:00:00
    Right-click selection of sequences and audio -> Audio -> Insert Stereo Audio - 00:59:58:00
    Right-click selection of sequences and audio -> Audio -> Insert 5.1 Audio - 01:00:00:00
    Right-click selection of sequences and audio -> Audio -> Insert 5.1 Audio - 00:59:58:00

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.4.0 01.20.24
        - Updates to PySide.
        - Fixed scoping issue with Flame 2023.2+ menus.

    v1.3.0 90.18.23
        - Updated to pyflame lib v2.0

    v1.2 05.31.22
        - Messages print to Flame message window - Flame 2023.1 and later

    v1.1 03.15.22
        - Added new message window
"""

# ---------------------------------------- #
# Imports

import re

import flame
from lib.pyflame_lib_add_audio import *

# ---------------------------------------- #
# Main Script

SCRIPT_NAME = 'Add Audio'
SCRIPT_VERSION = 'v1.4.0'
SCRIPT_PATH = '/opt/Autodesk/shared/python/add_audio'

class AddAudio():

    def __init__(self, selection):

        print ('\n')
        print ('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        self.selection = selection

        self.ws = flame.projects.current_project.current_workspace

        if flame.get_current_tab() == 'MediaHub':
            flame.set_current_tab('Timeline')

    def create_new_library(self, audio_type):

        self.audio_library = self.ws.create_library(f'{audio_type}')

        self.audio_library.expanded = True

        pyflame.message_print(
            message='New audio library created.',
            script_name=SCRIPT_NAME,
            )

    def add_stereo_audio(self, timecode):

        if len(self.selection) < 2:
            PyFlameMessageWindow(
                message='At least one clip/sequence and audio clip must be selected.',
                script_name=SCRIPT_NAME,
                type=MessageType.ERROR,
                )
            return

        sequence_selection = self.selection[::2]
        audio_selection = self.selection[1::2]

        if len(sequence_selection) != len(audio_selection):
            PyFlameMessageWindow(
                message='For every sequence/clip selected an audio clip must be selected.',
                script_name=SCRIPT_NAME,
                type=MessageType.ERROR,
                )
            return

        self.create_new_library('Stereo Audio')

        for sequence in sequence_selection:

            # Create duplicate of sequence in dest library
            duplicate_sequence = flame.media_panel.copy(sequence, self.audio_library)[0]

            # Open sequence
            open_sequence = duplicate_sequence.open_as_sequence()

            # Get sequence frame rate
            open_sequence_frame_rate = open_sequence.frame_rate

            # Set pyTime
            insert_timecode = flame.PyTime(timecode, open_sequence_frame_rate)

            # Add audio track to open sequence
            open_sequence.create_audio()

            # Get corresponding audio clip from audio selection list
            audio_clip = audio_selection[sequence_selection.index(sequence)]

            # Insert audio
            open_sequence.insert(audio_clip, insert_time = insert_timecode)

        PyFlameMessageWindow(
            message=f"""Stereo audio added to selected clips at {timecode}.<br><br>
            New clips can be found here: {str(self.audio_library.name)[1:-1]} Library""",
            script_name=SCRIPT_NAME,
            type=MessageType.OPERATION_COMPLETE,
            )

    def add_surround_audio(self, timecode):

        def sort_surround_list(audio_selection_list):

            # Sort selected audio files into proper order
            audio_selection_sorted = []

            surround_order = ['LF', 'RF', 'C', 'LFE', 'LS', 'RS', 'Stereo']

            for track in surround_order:
                for audio_clip in audio_selection_list:
                    audio_clip_name = str(audio_clip.name)[1:-1]
                    if re.search(f'{track}$', audio_clip_name, re.I):
                        audio_selection_sorted.append(audio_clip)

            return audio_selection_sorted

        # Check selection
        n = 8
        selected_groups = [self.selection[i * n:(i + 1) * n] for i in range((len(self.selection) + n - 1) // n )]

        for group in selected_groups:
            if len(group) != 8:
                PyFlameMessageWindow(
                    message="""Selection should be sequence followed by surround audio tracks:<br><br>
                    LF, RF, C, LFE, LS, RS, Stereo.<br><br>
                    Audio does not need to be in proper order.""",
                    script_name=SCRIPT_NAME,
                    type=MessageType.ERROR,
                    )
                return

        # Create new library for clips with audio added
        self.create_new_library('5.1 Audio')

        for group in selected_groups:

            duplicate_sequence = flame.media_panel.copy(group[0], self.audio_library)[0]

            audio_selection = group[1:8]

            # Make sure 7 tracks are selected per clip
            if len(audio_selection) != 7:
                PyFlameMessageWindow(
                    message="""Audio selection for 5.1 should contain these tracks:<br><br>
                    LF, RF, C, LFE, LS, RS, Stereo<br><br>
                    Audio does not need to be selected in proper order.""",
                    script_name=SCRIPT_NAME,
                    type=MessageType.ERROR,
                    )
                return

            # Open sequence
            open_sequence = duplicate_sequence.open_as_sequence()

            # Get sequence frame rate
            open_sequence_frame_rate = open_sequence.frame_rate

            # Set pyTime
            insert_timecode = flame.PyTime(timecode, open_sequence_frame_rate)

            # Sort audio clips to proper order
            audio_selection_sorted = sort_surround_list(audio_selection)

            for audio_clip in audio_selection_sorted:

                # Add audio track to open sequence
                open_sequence.create_audio()

                audio_track = open_sequence.audio_tracks[audio_selection_sorted.index(audio_clip)].channels[0]

                # Insert audio
                open_sequence.overwrite(audio_clip, insert_timecode, audio_track)

        PyFlameMessageWindow(
            message=f"""5.1 audio added to selected clips at {timecode}.<br><br>
            New clips can be found here: {str(self.audio_library.name)[1:-1]} Library""",
            script_name=SCRIPT_NAME,
            type=MessageType.OPERATION_COMPLETE,
            )

def add_stereo_audio_one_hour(selection):

    script = AddAudio(selection)
    script.add_stereo_audio('01:00:00:00')

def add_stereo_audio_two_pop(selection):

    script = AddAudio(selection)
    script.add_stereo_audio('00:59:58:00')

def add_surround_audio_one_hour(selection):

    script = AddAudio(selection)
    script.add_surround_audio('01:00:00:00')

def add_surround_audio_two_pop(selection):

    script = AddAudio(selection)
    script.add_surround_audio('00:59:58:00')

# ---------------------------------------- #
# Scopes

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False

# ---------------------------------------- #
# Flame Menus

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Audio...',
            'actions': [
                {
                    'name': 'Insert Stereo Audio - 01:00:00:00',
                    'isVisible': scope_sequence,
                    'execute': add_stereo_audio_one_hour,
                    'minimumVersion': '2023'
                },
                {
                    'name': 'Insert Stereo Audio - 00:59:58:00',
                    'isVisible': scope_sequence,
                    'execute': add_stereo_audio_two_pop,
                    'minimumVersion': '2023'
                },
                {
                    'name': 'Insert 5.1 Audio - 01:00:00:00',
                    'isVisible': scope_sequence,
                    'execute': add_surround_audio_one_hour,
                    'minimumVersion': '2023'
                },
                {
                    'name': 'Insert 5.1 Audio - 00:59:58:00',
                    'isVisible': scope_sequence,
                    'execute': add_surround_audio_two_pop,
                    'minimumVersion': '2023'
                }
            ]
        }
    ]
