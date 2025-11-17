# Clip To Batch Group
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
Script Name: Clip to Batch Group
Script Version: 2.7.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 06.16.19
Update Date: 04.09.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel / Media Hub

Description:

    Import selected clips from the mediahub into newly created batch groups set to clip length with a render node

    Option to switch to batch tab when batch groups are done being created can be
    turned off and on. Edit the following line in the __init__ section to either be True or False:

    self.go_to_batch = False

    Additional naming can be added to the end of batch group names. Edit the following line
    in the __init__ section. Naming must be in quotes.

    self.additional_naming = '_comp'

    Names of the batch group reels that are created by default can be
    changed by editing these two lists in the __init__ section:

    schematic_reel_list = [
        'Elements',
        'Plates',
        'PreRenders',
        'Ref',
        ]

    shelf_reel_list = [
        'Renders',
        ]

URL:
    https://github.com/logik-portal/python/clip_to_batch_group

Menus:

    To import clips into batch group with shot name extracted from clip name:
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Shot Name
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Shot Name - All Clips One Batch

    To import clips into batch group with clip name:
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Clip Name
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Clip Name - All Clips One Batch

    To create batch group from clips in media panel with shot name extracted from clip name:
        Right-click on clip in Media Panel -> Create New Batch Group... -> Shot Name

    To create batch group from clips in media panel with clip name:
        Right-click on clip in Media Panel -> Create New Batch Group... -> Clip Name

To install:

    Copy script into /opt/Autodesk/shared/python/clip_to_batch_group

Updates:

    v2.7.0 04.09.25
        - Updated to PyFlameLib v4.3.0.

    v2.6.0 01.15.25
        - Updated to PyFlameLib v4.1.0.
        - Script now only works with Flame 2025+.

    v2.5.0 08.22.24
        - Updated to PyFlameLib v3.0.0.

    v2.4.0 04.27.24
        - Render node now sets in and out marks based on clip in and out marks.

    v2.3.0 01.21.24
        - Sequences can now be imported into batch groups. This caused an error before.
        - Updates to PySide.

    v2.2.0 09.12.23
        - When creating a batch group from a clip in the media panel, the script will check for a shot name assigned to the clip.
        - If a shot name is assigned, that will be used for the batch group name. If no shot name is assigned, the script will
          attempt to extract the shot name from the clip name.
        - Updated with PyFlameLib v2.

    v2.1 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v1.8 05.15.21
        - Properly names batch group with shot name when clip name starts with number - 123_030_bty_plate -> 123_030_comp

    v1.7 02.19.21
        - Option added to switch to batch tab or not when batch groups are create can be toggled
          by editing self.go_to_batch value in __init__. Must be True or False.
        - Mediahub menu options added to import all selected clips into one batch group. Clip selected first is
          plate used for shot length and timecode.

    v1.6 11.18.20
        - Added Mux nodes with context 1 and 2 preset.

    v1.5 09.10.20
        - Batch groups can now be imported and named after either the clip name or shot name.
        - Script will now switch to the Batch tab when creating a batch group from the media panel - caused an error before.

    v1.4 04.20.20
        - Added ability to create batchgroup from clip in Media Panel.
        - Right-click on clip in Media Panel -> Clips... -> Create New Batchgroup

    v1.3 11.01.19
        - Changed menu name to Import...
        - Render node takes frame rate from imported clip

    v1.1 08.13.19
        - Code cleanup.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re

import flame
from lib.pyflame_lib_clip_to_batch_group import *

#-------------------------------------
# [Main Script]
#-------------------------------------

SCRIPT_NAME = 'Clip to Batch Group'
SCRIPT_VERSION = 'v2.7.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class CreateBatchGroup():

    def __init__(self, clip):

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.clip = clip
        self.clips_list = clip

        # Init variables
        self.clip_path = ''
        self.clip_name = ''
        self.shot_name = None

        # Additional naming to add to end of batch group name
        self.additional_naming = '_comp'

        # Go to batch tab when done creating batch groups
        self.go_to_batch = True

        # Names for shelf and schematic reels can be added or deleted here
        # Each reel name must be in quotes and seperated by commas
        # self.clip_reel points to the reel where clips will be imported to
        # The order of self.clip_reel in the list can changed but do not
        # remove it from the schematic reel list.
        self.clip_reel = 'Plates'

        self.schematic_reel_list = [
            self.clip_reel,
            'Elements',
            'PreRenders',
            'Ref',
            'Roto',
            ]

        self.shelf_reel_list = [
            'Renders',
            ]

        self.clip_reel_index = self.schematic_reel_list.index(self.clip_reel)

        # Create batch group
        self.batch_group = flame.batch.create_batch_group(
            'New Batch',
            duration=100,
            reels=self.schematic_reel_list,
            shelf_reels=self.shelf_reel_list,
            )

    def import_batch_group(self):
        """
        Import Batch Group
        ==================

        Import clip and create batch group with clip name as batch group name.
        """

        # Get clip path
        self.clip_path = str(self.clip.path)
        pyflame.print(f'Clip Path: {self.clip_path}')

        # Import clip to batchgroup
        flame.batch.import_clip(self.clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

    def import_all_batch_group(self):
        """
        Import All Batch Group
        ======================

        Import all selected clips into one batch group with clip name as batch group name.
        """

        # Import clip to batch group
        for clip in self.clips_list:
            self.clip_path = str(clip.path)
            print('Clip path:', self.clip_path, '\n')
            flame.batch.import_clip(self.clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

    def import_batch_group_shot_name(self):
        """
        Import Batch Group Shot Name
        ============================

        Import clip into batch group with shot name extracted from clip name.
        """

        # Get clip path
        self.clip_path = str(self.clip.path)
        pyflame.print(f'Clip Path: {self.clip_path}')

        # Import clip to batchgroup
        flame.batch.import_clip(self.clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and set render node properties
        self.create_nodes()

    def import_all_batchgroup_shot_name(self):
        """
        Import All Batch Group Shot Name
        ================================

        Import all selected clips into one batch group with shot name extracted from the first selected clip name.
        """

        # Import clip to batch group
        for clip in self.clips_list:
            self.clip_path = str(clip.path)
            pyflame.print(f'Clip Path: {self.clip_path}')

            flame.batch.import_clip(self.clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and set render node properties
        self.create_nodes()

    def clip_batch_group(self):
        """
        Clip Batch Group
        ================

        Create batch group for clip with clip name.
        """

        flame.go_to('Batch')

        # Copy clip to batchgroup
        flame.media_panel.copy(self.clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

    def all_clips_batch_group(self):
        """
        All Clips Batch Group
        =====================

        Create one batch group with all selected clips. Batch group name is taken from first selected clip.
        """

        # Switch to batch tab
        flame.go_to('Batch')

        # Copy all selected clips to batch group
        for clip in self.clips_list:
            flame.media_panel.copy(clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

    def clip_batch_group_shot_name(self):
        """
        Clip Batch Group Shot Name
        ==========================

        Create batch group for clip with shot name extracted from clip name.
        """

        # Switch to batch tab
        flame.go_to('Batch')

        # Copy clip to batch group
        flame.media_panel.copy(self.clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and setup render node properties
        self.create_nodes()

    def all_clips_batch_group_shot_name(self):
        """
        All Clips Batch Group Shot Name
        ===============================

        Create batch group from selected all clips with shot name extracted from clip name.
        """

        # Switch to batch tab
        flame.go_to('Batch')

        # Copy clip to batch group
        for clip in self.clips_list:
            flame.media_panel.copy(clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and setup render node properties
        self.create_nodes()

    def name_batch_group_shot_name(self):
        """
        Name Batch Group Shot Name
        ==========================

        Name batch group with shot name extracted from clip name.
        """

        # Get clip from batch group
        self.clip = flame.batch.nodes[0]

        # Get shot name from clip
        self.shot_name = pyflame.shot_name_from_clip(self.clip.clip)

        # Name batch group with shot name
        self.batch_group.name = self.shot_name

        # Add ShotName tag to batch group if Flame 2025.1 or newer
        try:
            self.batch_group.tags = [f'ShotName: {self.shot_name}']
        except:
            pass

    def name_batch_group_clip_name(self):
        """

        Name Batch Group Clip Name
        ==========================

        Name batch group with clip name.
        """

        self.clip = flame.batch.nodes[0]
        self.clip_name = str(self.clip.name)[1:-1]
        self.batch_group.name = self.clip_name + self.additional_naming

        # Add ShotName tag to batch group if Flame 2025.1 or newer
        try:
            self.batch_group.tags = [f'ShotName: {self.clip_name}']
        except:
            pass

        # Set shot name
        self.shot_name = self.clip_name

    def create_nodes(self):
        """
        Create Nodes
        ============

        Create Mux and Render nodes in batch group and connect nodes.
        """

        # Set batch group duration
        self.batch_group.duration = self.clip.duration

        # Get clip timecode
        try:
            imported_clip = self.batch_group.reels[self.clip_reel_index].clips[0]
        except:
            imported_clip = self.batch_group.reels[self.clip_reel_index].sequences[0]

        clip_timecode = imported_clip.start_time
        clip_frame_rate = imported_clip.frame_rate
        clip_in = imported_clip.in_mark
        clip_out = imported_clip.out_mark

        # Create mux nodes
        plate_in_mux = self.batch_group.create_node('Mux')
        plate_in_mux.name = 'plate_in'
        plate_in_mux.set_context(1, 'Default')
        plate_in_mux.pos_x = 400
        plate_in_mux.pos_y = -30

        render_out_mux = self.batch_group.create_node('Mux')
        render_out_mux.name = 'render_out'
        render_out_mux.set_context(2, 'Default')
        render_out_mux.pos_x = plate_in_mux.pos_x + 1600
        render_out_mux.pos_y = plate_in_mux.pos_y - 30

        # Create render node
        render_node = self.batch_group.create_node('Render')
        render_node.frame_rate = clip_frame_rate
        render_node.range_end = self.clip.duration
        render_node.source_timecode = clip_timecode
        render_node.record_timecode = clip_timecode
        render_node.name = '<batch iteration>'
        render_node.pos_x = render_out_mux.pos_x + 400
        render_node.pos_y = render_out_mux.pos_y -30
        render_node.shot_name = self.shot_name

        # Set in and out marks for render node if clip has in and out marks
        if str(clip_in) != '<NULL>':

            render_node.in_mark = clip_in
        if str(clip_out) != '<NULL>':
            render_node.out_mark = clip_out

        # Connect nodes
        flame.batch.connect_nodes(self.clip, 'Default', plate_in_mux, 'Default')
        flame.batch.connect_nodes(plate_in_mux, 'Result', render_out_mux, 'Default')
        flame.batch.connect_nodes(render_out_mux, 'Result', render_node, 'Default')

        try:
            flame.go_to('Batch')
            flame.batch.frame_all()

            if not self.go_to_batch:
                flame.go_to('Mediahub')
        except:
            pass

        pyflame.print(f'Batch group created: {str(self.batch_group.name)[1:-1]}')

#-------------------------------------

def clip_to_batch_group(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    for clip in selection:
        create = CreateBatchGroup(clip)
        create.clip_batch_group()

    print('Done.\n')

def clip_to_batch_group_shot_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    for clip in selection:
        create = CreateBatchGroup(clip)
        create.clip_batch_group_shot_name()

    print('Done.\n')

def import_to_batch_group(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import Clips {SCRIPT_VERSION}')

    for clip in selection:
        create = CreateBatchGroup(clip)
        create.import_batch_group()

    print('Done.\n')

def import_all_to_batch_group(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import All Clips to Single Batch Group {SCRIPT_VERSION}')

    create = CreateBatchGroup(selection)
    create.import_all_batch_group()

    print('Done.\n')

def import_to_batch_group_shot_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import Clips {SCRIPT_VERSION}')

    for clip in selection:
        create = CreateBatchGroup(clip)
        create.import_batch_group_shot_name()

    print('Done.\n')

def import_all_to_batch_group_shot_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import All Clips to Single Batch Group {SCRIPT_VERSION}')

    create = CreateBatchGroup(selection)
    create.import_all_batchgroup_shot_name()

    print('Done.\n')

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def scope_file(selection):

    for item in selection:
        item_path = str(item.path)
        item_ext = re.search(r'\.\w{3}$', item_path, re.I)
        if item_ext != (None):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': 'Import...',
            'actions': [
                {
                    'name': 'Create New Batch Group - Shot Name',
                    'isVisible': scope_file,
                    'execute': import_to_batch_group_shot_name,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Create New Batch Group - Shot Name - All Clips One Batch',
                    'isVisible': scope_file,
                    'execute': import_all_to_batch_group_shot_name,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Create New Batch Group - Clip Name',
                    'isVisible': scope_file,
                    'execute': import_to_batch_group,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Create New Batch Group - Clip Name - All Clips One Batch',
                    'isVisible': scope_file,
                    'execute': import_all_to_batch_group,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Create New Batch Group...',
            'actions': [
                {
                    'name': 'Shot Name',
                    'isVisible': scope_clip,
                    'execute': clip_to_batch_group_shot_name,
                    'minimumVersion': '2025',
                },
                {
                    'name': 'Clip Name',
                    'isVisible': scope_clip,
                    'execute': clip_to_batch_group,
                    'minimumVersion': '2025',
                }
            ]
        }
    ]
