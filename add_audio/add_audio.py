# Add Audio
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Add Audio
Script Version: 1.5.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 02.04.22
Update Date: 10.16.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Add stereo or 5.1 audio to selected sequences.

    Only works with sequences. Clips are not supported, and the menu only appears when a sequence is selected.

    To add stereo audio to a sequence, select the sequence then select the audio clip to be added.
    To add stereo audio to multiple sequences, select in sequence/audio/sequence/audio... order.

    To add 5.1 surround audio to a sequence, select the sequence followed by all the audio channels(LF, RF, C, LFE, LS, RS, Stereo)
    To add 5.1 surround audio to multiple sequences, select in sequence/all audio channels/sequences/all audio channels... order.

    Order of 5.1 surround files does not matter when being selected.
    When added to the sequence they will be put in this order: LF, RF, C, LFE, LS, RS, Stereo

    5.1 surround file names must end with _LF, _RF, _C, _LFE, _LS, _RS, or _Stereo. Case is not important.

URL:
    https://logik-portal.com/scripts/add_audio
 
Menus:

    Right-click selection of sequences and audio -> Audio -> Insert Stereo Audio - 01:00:00:00
    Right-click selection of sequences and audio -> Audio -> Insert Stereo Audio - 00:59:58:00
    Right-click selection of sequences and audio -> Audio -> Insert 5.1 Audio - 01:00:00:00
    Right-click selection of sequences and audio -> Audio -> Insert 5.1 Audio - 00:59:58:00

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.5.1 10.16.26
        - Audio tracks are now labelled after the audio added to them: Stereo L/R, or 5.1 LF, RF, 
          C, LFE, LS, RS and 5.1 Stereo L/R. The audio clips keep their original names.
        - 5.1 audio now stops with an error naming any missing, duplicate or misnamed channel 
          files. Previously a misnamed file was silently skipped and the other channels shifted tracks.
        - Selection order is now checked before anything is created. Selecting audio before its sequence 
          shows an error instead of failing and leaving a partly made library.
        - Added note that the script only works with sequences.
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.5.0 03.26.26
        - Updated to PyFlameLib v5.3.0.

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

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import re

import flame
from lib.pyflame_lib_add_audio import *

# ==============================================================================
# [Main Script]
# ==============================================================================

SCRIPT_NAME = 'Add Audio'
SCRIPT_VERSION = 'v1.5.1'
SCRIPT_PATH    = os.path.abspath(os.path.dirname(__file__))

class AddAudio():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        self.ws = flame.projects.current_project.current_workspace

        if flame.get_current_tab() == 'MediaHub':
            flame.set_current_tab('Timeline')

    def create_new_library(self, audio_type):

        self.audio_library = self.ws.create_library(f'{audio_type}')

        self.audio_library.expanded = True

        pyflame.print('New audio library created.')

    def label_audio_tracks(self, audio_tracks: list, labels: list) -> None:
        """
        Label Audio Tracks
        ==================

        Set the label of each audio track in the timeline. The audio clips on the tracks keep their own names.

        Args
        ----
            audio_tracks (list):
                Audio tracks to label.

            labels (list):
                Label for each track, in the same order.
        """

        for audio_track, label in zip(audio_tracks, labels):
            audio_track.channels[0].name = label

    def check_selection_order(self, sequence_selection: list, audio_selection: list) -> bool:
        """
        Check Selection Order
        =====================

        Make sure every sequence slot holds a sequence and every audio slot holds an audio clip.
        Catches selections made in the wrong order before any library is created.

        Args
        ----
            sequence_selection (list):
                Items expected to be sequences.

            audio_selection (list):
                Items expected to be audio clips.

        Returns
        -------
            bool: True if the selection order is correct.
        """

        bad_items = []

        for item in sequence_selection:
            if not isinstance(item, flame.PySequence):
                bad_items.append(f'{str(item.name)[1:-1]} - expected a sequence')

        for item in audio_selection:
            if isinstance(item, flame.PySequence) or not item.audio_tracks:
                bad_items.append(f'{str(item.name)[1:-1]} - expected an audio clip')

        if bad_items:
            PyFlameMessageWindow(
                message='Selection is not in the right order. Select each sequence, then its audio.\n\n' + '\n'.join(bad_items),
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

        return True

    def add_stereo_audio(self, timecode):

        if len(self.selection) < 2:
            PyFlameMessageWindow(
                message='At least one sequence and audio clip must be selected.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        sequence_selection = self.selection[::2]
        audio_selection = self.selection[1::2]

        if len(sequence_selection) != len(audio_selection):
            PyFlameMessageWindow(
                message='For every sequence selected an audio clip must be selected.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Check selection order before anything is created
        if not self.check_selection_order(sequence_selection, audio_selection):
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
            track_count = len(open_sequence.audio_tracks)
            open_sequence.create_audio()

            # Get corresponding audio clip from audio selection list
            audio_clip = audio_selection[sequence_selection.index(sequence)]

            # Insert audio
            open_sequence.insert(audio_clip, insert_time = insert_timecode)

            # Label new tracks. A stereo clip fills two tracks, left and right
            new_tracks = open_sequence.audio_tracks[track_count:]
            labels = ['Stereo L', 'Stereo R'] if len(new_tracks) == 2 else ['Stereo'] * len(new_tracks)
            self.label_audio_tracks(new_tracks, labels)

        PyFlameMessageWindow(
            message=f'Stereo audio added to selected clips at {timecode}.\n\nNew clips can be found here: {str(self.audio_library.name)[1:-1]} Library',
            message_type=MessageType.OPERATION_COMPLETE,
            parent=None,
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

        def check_surround_channels(audio_selection_list) -> list:
            """
            Check Surround Channels
            =======================

            Return problems with 5.1 channel names. Empty list if every channel is found exactly once.
            """

            surround_order = ['LF', 'RF', 'C', 'LFE', 'LS', 'RS', 'Stereo']
            problems = []
            matched_clips = []

            for track in surround_order:
                matches = [audio_clip for audio_clip in audio_selection_list if re.search(f'{track}$', str(audio_clip.name)[1:-1], re.I)]
                if not matches:
                    problems.append(f'Missing channel: {track}')
                elif len(matches) > 1:
                    problems.append(f'More than one {track} channel: ' + ', '.join(str(audio_clip.name)[1:-1] for audio_clip in matches))
                matched_clips.extend(matches)

            for audio_clip in audio_selection_list:
                if audio_clip not in matched_clips:
                    problems.append(f'Name does not end with a channel suffix: {str(audio_clip.name)[1:-1]}')

            return problems

        # Check selection
        n = 8
        selected_groups = [self.selection[i * n:(i + 1) * n] for i in range((len(self.selection) + n - 1) // n )]

        for group in selected_groups:
            if len(group) != 8:
                PyFlameMessageWindow(
                    message='Selection should be sequence followed by surround audio tracks:\n\nLF, RF, C, LFE, LS, RS, Stereo.\n\nAudio does not need to be in proper order.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return

        # Check selection order and 5.1 channel names before anything is created
        for group in selected_groups:
            if not self.check_selection_order(group[:1], group[1:]):
                return

            channel_problems = check_surround_channels(group[1:])
            if channel_problems:
                PyFlameMessageWindow(
                    message=f'5.1 audio for {str(group[0].name)[1:-1]} has channel problems:\n\n' + '\n'.join(channel_problems) + '\n\nFile names must end with _LF, _RF, _C, _LFE, _LS, _RS or _Stereo.',
                    message_type=MessageType.ERROR,
                    parent=None,
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
                    message='Audio selection for 5.1 should contain these tracks:\n\nLF, RF, C, LFE, LS, RS, Stereo\n\nAudio does not need to be selected in proper order.',
                    message_type=MessageType.ERROR,
                    parent=None,
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

            # Label tracks in 5.1 order. The Stereo clip fills the last two tracks, left and right
            stereo_tracks = open_sequence.audio_tracks[6:]
            stereo_labels = ['5.1 Stereo L', '5.1 Stereo R'] if len(stereo_tracks) == 2 else ['5.1 Stereo'] * len(stereo_tracks)
            self.label_audio_tracks(open_sequence.audio_tracks, ['5.1 LF', '5.1 RF', '5.1 C', '5.1 LFE', '5.1 LS', '5.1 RS'] + stereo_labels)

        PyFlameMessageWindow(
            message=f'5.1 audio added to selected clips at {timecode}.\n\nNew clips can be found here: {str(self.audio_library.name)[1:-1]} Library',
            message_type=MessageType.OPERATION_COMPLETE,
            parent=None,
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

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Audio...',
            'actions': [
                {
                    'name': 'Insert Stereo Audio - 01:00:00:00',
                    'isVisible': scope_sequence,
                    'execute': add_stereo_audio_one_hour,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Insert Stereo Audio - 00:59:58:00',
                    'isVisible': scope_sequence,
                    'execute': add_stereo_audio_two_pop,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Insert 5.1 Audio - 01:00:00:00',
                    'isVisible': scope_sequence,
                    'execute': add_surround_audio_one_hour,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Insert 5.1 Audio - 00:59:58:00',
                    'isVisible': scope_sequence,
                    'execute': add_surround_audio_two_pop,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
