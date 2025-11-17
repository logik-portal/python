# Master Builder
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
Script Name: Master Builder
Script Version: 1.5.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 02.09.22
Update Date: 04.13.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Reel Group

Description:

    Create masters from clips/sequences in a Reel Group.

    Each reel should contain one part of the final master. For example:

        Reel 1 - color bars
        Reel 2 - slates
        Reel 3 - edits

    Reels that contain one clip will have that clip added to every master created.

    Reels that contain multiple clips will cause the script to make a new master from each clip.

    For instance if there are: 1 2-second clip of color bars, 4 slates, 4 edits, and 1 1-second clip of black
    the script will create 4 edits with each one containing: color bars, a slate, edit, and 1 second clip of black.

    Black is automatically inserted into timeline gaps between clips on the primary track.

    Reels containing more than one clip must have an equal number of clips. If there are 4 slates, there
    should be 4 edits.

    Other things to keep in mind:

        All clips must have proper record timecode set for placement in timeline.

        Each reel should contain either all clips or all sequences. Clips and sequences
        should not be mixed within the same reel.

        Sequences can contain multiple tracks but not multiple versions.

URL:
    https://github.com/logik-portal/python/master_builder

Menu:

    Right-click on Reel Group -> Master Builder

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.5.0 04.13.25
        - Updated to PyFlameLib v4.3.0.
        - Added support for PyFlameTabWidget.

    v1.4.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v1.3.0 08.24.24
        - Updated to PyFlameLib v3.0.0.

    v1.2.0 02.06.24
        - Black is now automatically inserted into timeline gaps between clips.
        - Updates to UI/PySide.
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.
        - Updated menu for Flame 2023.2.

    v1.1 06.08.22
        - Messages print to Flame message window - Flame 2023.1 and later
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_master_builder import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Master Builder'
SCRIPT_VERSION = 'v1.5.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class MasterBuilder():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.reel_group = selection[0]

        # Check reels for mixed clip type
        mixed_reels = self.check_reels()
        if mixed_reels:
            PyFlameMessageWindow(
                message='Reels must contain either all clips or all sequences.',
                type=MessageType.ERROR,
                )
            return

        # Check clip count on reels
        good_clip_count = self.check_clip_count()
        if not good_clip_count:
            PyFlameMessageWindow(
                message='If a reel contains more than one clip it must contain the same number of clips as other reels with more than one clip.',
                type=MessageType.ERROR,
                )
            return

        # Check sequences for multiple versions - only one version allowed
        multiple_versions = self.check_versions()
        if multiple_versions:
            PyFlameMessageWindow(
                message='Sequences may only have one version.<br>Remove extra versions and try again.',
                type=MessageType.ERROR,
                )
            return

        self.main_window()

    def check_reels(self):
        """
        Make sure reels only have all sequences or all clips.
        """

        for reel in self.reel_group.reels:
            if reel.clips and reel.sequences:
                return True
        return False

    def check_clip_count(self):
        """
        Check reels to make sure either reel has one clip or reels
        that have more than one clip all have the same number of clips.
        """

        self.clip_count_dict = {}

        # Count number of clips on each reel
        for reel in self.reel_group.reels:
            clip_count = 0
            seq_count = 0
            if reel.clips:
                clip_count = len(reel.clips)
            if reel.sequences:
                seq_count = len(reel.sequences)

            total_clips = clip_count + seq_count

            # Add total number of clips on reel to dict. Ignore empty reels.
            if total_clips != 0:
                self.clip_count_dict[reel] = total_clips

        # Get highest and lowest number of clips on a reel
        self.max_clips = max(self.clip_count_dict.items(), key=lambda x: x[1])
        self.min_clips = min(self.clip_count_dict.items(), key=lambda x: x[1])

        self.clip_values = [self.max_clips[1], self.min_clips[1]]

        # Check number of clips on each reel against the lowest and highest number of clips on a reel
        for k, v in self.clip_count_dict.items():
            if v not in self.clip_values:
                return False
        return True

    def check_versions(self):
        """
        Make sure sequences only have one version
        """

        for reel in self.reel_group.reels:
            for seq in reel.sequences:
                if len(seq.versions) > 1:
                    return True
        return False

    #-------------------------------------

    def main_window(self):

        def get_reel_list():

            if self.max_clips[1] > 1:
                self.desktop_reel_options = [str(reel.name)[1:-1] for reel in self.reel_group.reels if int(len(reel.clips)) > 1 or int(len(reel.sequences)) > 1] + ['None']
            else:
                self.desktop_reel_options = [str(reel.name)[1:-1] for reel in self.reel_group.reels] + ['None']

        # Main Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.create_masters_list,
            grid_layout_columns=2,
            grid_layout_rows=3,
            )

        # Labels
        self.names_from_label = PyFlameLabel(
            text='Master Names From',
            )

        # Push Button Menu
        get_reel_list()
        self.desktop_reels_push_button = PyFlamePushButtonMenu(
            text=self.desktop_reel_options[0],
            menu_options=self.desktop_reel_options,
            )

        # Buttons
        self.create_masters_button = PyFlameButton(
            text='Create Masters',
            connect=self.create_masters_list,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.names_from_label, 0, 0)
        self.window.grid_layout.addWidget(self.desktop_reels_push_button, 0, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 2, 0)
        self.window.grid_layout.addWidget(self.create_masters_button, 2, 1)

    def create_masters_list(self):

        self.window.close()

        # Build list of clips from reels that only have a single clip.
        # If Multiple masters are being created these clips will be added to each master.

        clip_in_all_list = []

        for k, v in self.clip_count_dict.items():
            if v == 1:
                if k.clips:
                    clip_in_all_list.append(k.clips[0])
                if k.sequences:
                    clip_in_all_list.append(k.sequences[0])

        # ----------------- #

        # Create new reels for masters
        self.create_reels()

        # ----------------- #

        # Build list of reels with more than one clip
        multi_clip_reel = []

        for k, v in self.clip_count_dict.items():
            if v > 1:
                multi_clip_reel.append(k)

        # If reels exist with more than one clip, build multiple masters
        if multi_clip_reel:
            masters_list = []
            for x in range(self.max_clips[1]):
                masters_dict = {}
                clip_list = []
                master_name = ''
                for reel in multi_clip_reel:
                    if reel.clips:
                        clip = reel.clips[x]
                    elif reel.sequences:
                        clip = reel.sequences[x]
                    if reel.name == self.desktop_reels_push_button.text():
                        master_name = str(clip.name)[1:-1]
                    clip_list.append(clip)

                masters_dict[master_name] = (clip_list + clip_in_all_list)
                masters_list.append(masters_dict)

            # Build masters from lists of clips
            print ('Building masters:\n')

            for master in masters_list:
                for k, v in master.items():
                    self.assemble_master(k, v)

        else:
            # Create master from single clips on reels
            master_name = clip_in_all_list[0].name

            print('Master Name:', master_name)

            self.assemble_master(master_name, clip_in_all_list)

        # Delete temp reel
        flame.delete(self.temp_reel)

        print('\n')
        pyflame.print('Masters build complete.', text_color=TextColor.GREEN)

    def create_reels(self):
        """
        Create new reels for masters
        """

        self.temp_reel = self.reel_group.create_reel('Temp Reel')
        self.master_reel = self.reel_group.create_reel('Master Reel')

    def assemble_master(self, master_name, clips_list):
        """
        Create list of all first clips and sequences.
        Find clip/sequence with most tracks. This will be master clip all other clips will be added to.
        """

        # Create dict to hold clips/sequences with number of tracks
        clip_dict = {}

        for clip in clips_list:
            clip_dict[clip] = len(clip.versions[0].tracks)

        sorted_dict = dict(sorted(clip_dict.items(), key=lambda item: item[1]))

        # Create list of clips/sequences to be added to master clip
        clip_list = list(sorted_dict)[:-1]

        # Get clip/sequence with most tracks to be used as master clip
        master_clip = list(sorted_dict)[-1]

        # ----------------- #

        # Duplicate main clip to be used to build masters
        duplicate_sequence = flame.duplicate(master_clip)

        # Move duplicate to temp reel for editing
        flame.media_panel.move(duplicate_sequence, self.temp_reel)

        # Get sequence/clip from temp reel
        try:
            clip_to_edit = self.temp_reel.sequences[0]
        except:
            clip_to_edit = self.temp_reel.clips[0]

        # Open master sequence/clip
        master_sequence = clip_to_edit.open_as_sequence()

        # Set primary track to first tracks
        master_sequence.primary_track = master_sequence.versions[0].tracks[0]

        # ----------------- #

        # Add clips into master. Clips must have timecode set
        for clip in clip_list:
            # Set clip pytime
            insert_timecode = flame.PyTime(str(clip.start_time), clip.frame_rate)
            master_sequence.overwrite(clip, insert_timecode)

        # If slate reel exists take name from slate
        if master_name:
            master_sequence.name = master_name

        # Insert black into timeline gaps on primary track
        for n in master_sequence.versions[0].tracks[0].segments:
            if n.type == 'Gap':
                n.set_gap_colour(r=0.0, g=0.0, b=0.0)

        # Move master sequence from temp reel to master reel then delete temp reel
        flame.media_panel.move(master_sequence, self.master_reel)

        print (f'    Master Built: {master_name}')

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def scope_reel_group(selection):

    for item in selection:
        if isinstance(item, flame.PyReelGroup):
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
                    'name': 'Master Builder',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_reel_group,
                    'execute': MasterBuilder,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
