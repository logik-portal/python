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
Script Version: 3.0.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 06.16.19
Update Date: 05.05.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel / Media Hub

Description:

    Create batch group(s) from selected clips in the media panel or media hub.

Usage:

    Script Setup:
        - Set batch group to use either Render or Write File node.
          (Default:  Render)
        - Set batch group suffix.
          (Default: _comp)
        - Set tokenized save path. Batch setup will be saved when the batch group is created.
          Leaving Tokenized Save Path button off will not save the batch group and the default Flame path will be used.
          (Default: off)

    When creating a batch group from all clips, clips are loaded in the order
    they are selected. Select clips individually to control the order, or use
    shift-select to load them top-down. The first clip in the selection
    determines the batch group settings.

URL:

    https://logik-portal.com/scripts/#clip_to_batch_group

Menus:

    Setup:
        Flame Main Menu -> Logik Portal -> Logik Portal Script Setup -> Clip to Batch Group Setup

    To import clips into batch group with shot name extracted from clip name:
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Shot Name
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Shot Name - All Clips One Batch

    To import clips into batch group with clip name:
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Clip Name
        Right-click on clip in MediaHub -> Import... -> Create New Batch Group - Clip Name - All Clips One Batch

    To create batch group from clips in media panel with shot name extracted from clip name:
        Right-click on clip in Media Panel -> Create New Batch Group... -> Shot Name
        Right-click on clip in Media Panel -> Create New Batch Group... -> Shot Name - All Clips One Batch

    To create batch group from clips in media panel with clip name:
        Right-click on clip in Media Panel -> Create New Batch Group... -> Clip Name
        Right-click on clip in Media Panel -> Create New Batch Group... -> Clip Name - All Clips One Batch

To install:

    Copy script into /opt/Autodesk/shared/python/clip_to_batch_group

Updates:

    v3.0.0 05.05.26
        - Updated to work in Flame 2027.
        - Added setup window to configure script options:
            - Set batch group to use either Render or Write File node.
            - Set batch group suffix.
            - Set tokenized save path. Batch setup will be saved when the batch group is created.
              Leaving Tokenized Save Path button off will not save the batch group and the default Flame path will be used.
        - Updated to PyFlameLib v5.3.1.

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

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re

import flame
from lib.pyflame_lib_clip_to_batch_group import *

# ==============================================================================
# [Main Script]
# ==============================================================================

SCRIPT_NAME = 'Clip to Batch Group'
SCRIPT_VERSION = 'v3.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

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
            'render_node_type': 'Render',
            'batch_group_suffix': '_comp',
            'use_tokenized_save_path': False,
            'tokenized_save_path': '/opt/Autodesk',
            },
        )

class ClipToBatchGroupSetup:

    def __init__(self, selection):

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        # Open setup window
        self.setup()

    def setup(self):

        def tokenized_save_path_toggle() -> None:
            """
            Tokenized Save Path Toggle
            ==========================

            Toggle tokenized save path entry and tokenized save path menu based on use tokenized save path push button state.
            """

            if self.use_tokenized_save_path_push_button.checked:
                self.tokenized_save_path_label.enabled = True
                self.tokenized_save_path_entry.enabled = True
                self.save_path_token_menu.enabled = True
                self.browse_button.enabled = True
            else:
                self.tokenized_save_path_label.enabled = False
                self.tokenized_save_path_entry.enabled = False
                self.save_path_token_menu.enabled = False
                self.browse_button.enabled = False

        def browse_save_path() -> None:
            """
            Browse Save Path
            ================

            Browse to save path and set save path entry to selected path.
            """

            save_path = pyflame.file_browser(
                path=self.tokenized_save_path_entry.text,
                title='Select Save Path',
                select_directory=True,
                window_to_hide=self.setup_window,
                )

            if save_path:
                self.tokenized_save_path_entry.text = str(save_path)

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings to config file.
            """

            # Validate settings
            if not self.suffix_name_entry.text:
                PyFlameMessageWindow(
                    message='Enter Task Name',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return
            if not self.tokenized_save_path_entry.text:
                PyFlameMessageWindow(
                    message='Enter Tokenized Save Path',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            self.settings.save_config(
                config_values={
                    'render_node_type': self.render_node_type_menu.text,
                    'batch_group_suffix': self.suffix_name_entry.text,
                    'use_tokenized_save_path': self.use_tokenized_save_path_push_button.checked,
                    'tokenized_save_path': self.tokenized_save_path_entry.text,
                    }
                )

            self.setup_window.close()

            PyFlameMessageWindow(
                message='Config Saved',
                parent=None,
                )

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
            grid_layout_rows=6,
            grid_layout_adjust_column_widths={2: 50},
            message_bar=False,
            parent=None,
            )

        # Labels
        self.render_node_type_label = PyFlameLabel(
            text='Render Node Type',
            )
        self.suffix_name_label = PyFlameLabel(
            text='Batch Group Suffix',
            )
        self.tokenized_save_path_label = PyFlameLabel(
            text='Tokenized Save Path',
            )

        # Entries
        self.suffix_name_entry = PyFlameEntry(
            text=self.settings.batch_group_suffix,
            )
        self.tokenized_save_path_entry = PyFlameEntry(
            text=self.settings.tokenized_save_path,
            )

        # Set Entry Tab-key Order
        self.setup_window.tab_order = [
            self.suffix_name_entry,
            self.tokenized_save_path_entry,
            ]

        # Menu
        self.render_node_type_menu = PyFlameMenu(
            text=self.settings.render_node_type,
            menu_options=[
                'Render',
                'Write File',
                ],
            )

        # Token Menu
        self.save_path_token_menu = PyFlameTokenMenu(
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                'Sequence Name': '<SeqName>',
                'Sequence Name (All Caps)': '<SEQNAME>',
                'Shot Name': '<ShotName>',
                'Batch Group Name': '<BatchGroupName>',
                'Year (YYYY)': '<YYYY>',
                'Year (YY)': '<YY>',
                'Month (MM)': '<MM>',
                'Day (DD)': '<DD>',
                },
            token_dest=self.tokenized_save_path_entry,
            )

        # Push Button
        self.use_tokenized_save_path_push_button = PyFlamePushButton(
            text='Tokenized Save Path',
            checked=self.settings.use_tokenized_save_path,
            connect=tokenized_save_path_toggle,
            )

        # Buttons
        self.browse_button = PyFlameButton(
            text='Browse',
            connect=browse_save_path,
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

        # Toggle UI
        tokenized_save_path_toggle()

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.render_node_type_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.render_node_type_menu, 0, 1)

        self.setup_window.grid_layout.addWidget(self.suffix_name_label, 0, 3)
        self.setup_window.grid_layout.addWidget(self.suffix_name_entry, 0, 4)

        self.setup_window.grid_layout.addWidget(self.use_tokenized_save_path_push_button, 2, 0)
        self.setup_window.grid_layout.addWidget(self.tokenized_save_path_label, 3, 0)
        self.setup_window.grid_layout.addWidget(self.tokenized_save_path_entry, 3, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.save_path_token_menu, 3, 4)
        self.setup_window.grid_layout.addWidget(self.browse_button, 3, 5)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 5, 4)
        self.setup_window.grid_layout.addWidget(self.save_button, 5, 5)

        # ------------------------------------------------------------------------------

        self.suffix_name_entry.setFocus()

class ClipToBatchGroup:

    def __init__(self, selection):

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        # Set selection
        self.selection = selection

        # Init variables
        self.clip_path = ''
        self.clip_name = ''
        self.shot_name = None

    # ==============================================================================

    def create_batch_group(self) -> None:
        """
        Create Batch Group
        ==================

        Create batch group and add 'Plates' reel if it doesn't exist. Get index of 'Plates' reel.
        """

        # Create batch group
        self.batch_group = flame.batch.create_batch_group(
            'New Batch',
            duration=100,
            )

        # Check for existing 'Plates' reel and create a new one if it doesn't exist.
        reel_names = [str(reel.name)[1:-1] for reel in self.batch_group.reels]
        existing = next((n for n in reel_names if n.lower() == 'plates'), None)
        if existing:
            self.clip_reel = existing
        else:
            # Use capitalised name if any existing reel starts with an uppercase letter.
            use_caps = any(n[0].isupper() for n in reel_names if n)
            self.clip_reel = 'Plates' if use_caps else 'plates'
            self.batch_group.create_reel(self.clip_reel)
            reel_names.append(self.clip_reel)
        self.clip_reel_index = reel_names.index(self.clip_reel)

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

        # Create render/write file node
        if self.settings.render_node_type == 'Render':
            render_node = self.batch_group.create_node('Render')
        else:
            render_node = self.batch_group.create_node('Write File')

        # Set basic metadata for render/write file node for Flame 2027+
        try:
            render_node.basic_metadata = 'Custom Values'
            render_node.collapsed = True
        except:
            pass

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
        except:
            pass

        # Save batch group if tokenized save path is enabled
        if self.settings.use_tokenized_save_path:
            self.save_batch_group()

        pyflame.print(f'Batch Group Created: {str(self.batch_group.name)[1:-1]}', text_color=TextColor.GREEN)

    def save_batch_group(self) -> None:
        """
        Save Batch Group
        ===============

        Save batch group to batch setups folder.
        """

        pyflame.print(f'Saving Batch Group: {str(self.batch_group.name)[1:-1]}')

        iteration_name = str(self.batch_group.current_iteration.name)[1:-1]
        resolved_path = pyflame.resolve_tokens(self.settings.tokenized_save_path, self.batch_group) + '/' +  iteration_name

        # Create batch setups folder if it doesn't exist
        if not os.path.isdir(resolved_path):
            try:
                os.makedirs(resolved_path)
            except:
                PyFlameMessageWindow(
                    message='Unable to save batch group. Check tokenized save path in setup.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return

        # Save batch group
        self.batch_group.save_setup(resolved_path)

    # ==============================================================================

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
        self.batch_group.name = self.shot_name + self.settings.batch_group_suffix

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
        self.batch_group.name = self.clip_name + self.settings.batch_group_suffix

        # Add ShotName tag to batch group if Flame 2025.1 or newer
        try:
            self.batch_group.tags = [f'ShotName: {self.clip_name}']
        except:
            pass

        # Set shot name
        self.shot_name = self.clip_name

    # -------------------[ Batch Groups from Media Panel Clips ]--------------------

    def batch_group_from_clip_name(self):
        """
        Batch Group From Clip Name
        ==========================
        One batch group will be created for each clip in the selection.

        Batch Group Name and Shot Name will be the name of the clip.
        """

        print('Creating batch groups from clip name...\n')

        for clip in self.selection:
            print('Clip Name:', str(clip.name)[1:-1])

            self.clip = clip

            flame.go_to('Batch')

            # Create batch group
            self.create_batch_group()

            # Copy clip to batchgroup
            flame.media_panel.copy(self.clip, self.batch_group.reels[self.clip_reel_index])

            # Get batch group name
            self.name_batch_group_clip_name()

            # Create render node and set render node properties
            self.create_nodes()

    def batch_group_from_clip_name_all_clips(self):
        """
        Batch Group From Clip Name All Clips
        ====================================

        One batch group will be created for all clips in the selection.

        Batch Group Name and Shot Name will be the name of the first clip in the selection.

        To have clips load in a specific order, select each clip one at a time.
        Using shift to create a selection will load the clips in a top down order.
        """

        print('Creating batch group from all clips with clip name as batch group name...\n')

        self.clip = self.selection[0]
        print('Clip Name:', str(self.clip.name)[1:-1])

        flame.go_to('Batch')

        # Create batch group
        self.create_batch_group()

        # Copy clip to batchgroup
        for clip in self.selection:
            flame.media_panel.copy(clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

    def batch_group_from_shot_name(self):
        """
        Batch Group From Shot Name
        ==========================

        Create batch group for each Shot Name in the selection.

        One batch group will be created for each Shot Name in the selection. Multiple clips with the same Shot Name will be added to the same batch group.
        """

        # Switch to batch tab
        flame.go_to('Batch')

        # Get list of unique shot names from selected clips
        shot_names = []
        for clip in self.selection:
            clip_shot_name = pyflame.shot_name_from_clip(clip)
            if clip_shot_name not in shot_names:
                shot_names.append(clip_shot_name)

        # Iterate through each Shot Name and create batch group for each Shot Name adding all clips with the same Shot Name to the batch group.
        for shot_name in shot_names:
            shot_clips = []
            for clip in self.selection:
                clip_shot_name = pyflame.shot_name_from_clip(clip)
                if clip_shot_name == shot_name:
                    shot_clips.append(clip)

            # Get first clip from shot clips
            self.clip = shot_clips[0]

            # Create batch group
            self.create_batch_group()

            # Copy clip to batch group
            for clip in shot_clips:
                flame.media_panel.copy(clip, self.batch_group.reels[self.clip_reel_index])

            # Get batch group name
            self.name_batch_group_shot_name()

            # Create render node and setup render node properties
            self.create_nodes()

    def batch_group_from_shot_name_all_clips(self):
        """
        Batch Group From Shot Name All Clips
        ==========================

        Create batch group for all clips in the selection with shot name extracted from clip name.

        One batch group will be created for each shot name in the selection. Multiple clips with the same shot name will be added to the same batch group.
        """

        # Switch to batch tab
        flame.go_to('Batch')

        # Get first clip from shot clips
        self.clip = self.selection[0]

        # Create batch group
        self.create_batch_group()

        # Copy clip to batch group
        for clip in self.selection:
            flame.media_panel.copy(clip, self.batch_group.reels[self.clip_reel_index])

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and setup render node properties
        self.create_nodes()

    # --------------------[ Batch Groups from Media Hub Clips ]---------------------

    def batch_group_from_media_hub_clip_name(self):
        """
        Batch Group From Media Hub Clips Clip Name
        ==========================================

        Creates batch group for each clip in the selection with clip name as batch group name.
        """

        pyflame.print('Creating batch group from selected clips...')

        # Switch to batch tab - batch group cannot be created in MediaHub tab.
        flame.go_to('Batch')

        pyflame.print('Importing clips to batch group...')

        # Iterate through each clip in the selection and create batch group for each clip.
        for clip in self.selection:

            # Set clip from selection to current clip
            self.clip = clip

            # Get clip path
            self.clip_path = str(self.clip.path)

            # Create batch group
            self.create_batch_group()

            # Import clip to batchgroup
            flame.batch.import_clip(self.clip_path, self.clip_reel)

            # Get batch group name
            self.name_batch_group_clip_name()

            # Create render node and set render node properties
            self.create_nodes()

            self.batch_group.expanded = False

    def batch_group_from_media_hub_clip_name_all_clips(self):
        """
        Batch Group From Media Hub Clips Clip Name All Clips
        ====================================================

        Creates a single batch group for all clips in the selection with clip name as batch group name.
        """

        # Switch to batch tab - batch group cannot be created in MediaHub tab.
        flame.go_to('Batch')

        pyflame.print('Creating batch group from selected clips...')

        # Set clip from selection to current clip
        self.clip = self.selection[0]

        # Create batch group
        self.create_batch_group()

        pyflame.print('Importing clips to batch group...')

        for clip in self.selection:

            # Get clip path
            clip_path = str(clip.path)

            # Import clip to batchgroup
            flame.batch.import_clip(clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_clip_name()

        # Create render node and set render node properties
        self.create_nodes()

        self.batch_group.expanded = False

    def batch_group_from_media_hub_shot_name(self):
        """
        Import Batch Group Shot Name
        ============================

        Import clips into batch groups with shot name extracted from clip path.

        Each Shot Name will have its own batch group. Multiple clips with the same Shot Name will be added to the same batch group.
        """

        def get_clip_shot_name(clip):
            """
            Get Clip Shot Name
            ==================

            Get shot name from clip path
            """

            clip_path = str(clip.path)
            clip_name = clip_path.split('/')[-1]
            clip_name = clip_name.split('.')[0]
            clip_shot_name = pyflame.resolve_shot_name(clip_name)
            return clip_shot_name

        pyflame.print('Creating batch groups from selected clips...')

        # Switch to batch tab - batch group cannot be created in MediaHub tab.
        flame.go_to('Batch')

        # Get list of unique shot names from selected clips
        shot_names = []
        for clip in self.selection:
            clip_shot_name = get_clip_shot_name(clip)
            if clip_shot_name not in shot_names:
                shot_names.append(clip_shot_name)
        print('Shot Names Found:', shot_names)

        # Iterate through each Shot Name and create batch group for each Shot Name adding all clips with the same Shot Name to the batch group.
        for shot_name in shot_names:
            shot_clips = []
            for clip in self.selection:
                clip_shot_name = get_clip_shot_name(clip)
                if clip_shot_name == shot_name:
                    shot_clips.append(clip.path)

            # Create batch group
            self.create_batch_group()

            pyflame.print('Importing clips to batch group...')

            # Import clips to batch group
            for clip in shot_clips:
                flame.batch.import_clip(clip, self.clip_reel)

            # Get batch group name
            self.name_batch_group_shot_name()

            # Create render node and setup render node properties
            self.create_nodes()

            self.batch_group.expanded = False

    def batch_group_from_media_hub_shot_name_all_clips(self):
        """
        Batch Group From Media Hub Shot Name All Clips
        ==============================================

        Import all selected clips into one batch group with Shot Name extracted from the first selected clip path.
        """

        pyflame.print('Creating batch group from selected clips...')

        # Switch to batch tab - batch group cannot be created in MediaHub tab.
        flame.go_to('Batch')

        # Create batch group
        self.create_batch_group()

        pyflame.print('Importing clips to batch group...')

        # Import clips to batch group
        for clip in self.selection:
            clip_path = str(clip.path)
            flame.batch.import_clip(clip_path, self.clip_reel)

        # Get batch group name
        self.name_batch_group_shot_name()

        # Create render node and setup render node properties
        self.create_nodes()

        self.batch_group.expanded = False

# ==============================================================================

def clip_to_batch_group_clip_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_clip_name()

    print('Done.\n')

def clip_to_batch_group_clip_name_all_clips(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_clip_name_all_clips()

    print('Done.\n')

def clip_to_batch_group_shot_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_shot_name()

    print('Done.\n')

def clip_to_batch_group_shot_name_all_clips(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_shot_name_all_clips()

    print('Done.\n')

# ------------------------------------------------------------------------------

def media_hub_import_to_batch_group_from_clip_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import Clips {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_media_hub_clip_name()

    print('Done.\n')

def media_hub_import_to_batch_group_from_clip_name_all_clips(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import All Clips to Single Batch Group {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_media_hub_clip_name_all_clips()

    print('Done.\n')

def media_hub_import_to_batch_group_from_shot_name(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import Clips {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_media_hub_shot_name()

    print('Done.\n')

def media_hub_import_to_batch_group_from_shot_name_all_clips(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Import All Clips to Single Batch Group {SCRIPT_VERSION}')

    create = ClipToBatchGroup(selection)
    create.batch_group_from_media_hub_shot_name_all_clips()

    print('Done.\n')

# ==============================================================================
# [Scopes]
# ==============================================================================

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
                    'name': 'Clip to Batch Group Setup',
                    'execute': ClipToBatchGroupSetup,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': 'Import...',
            'actions': [
                {
                    'name': 'Create New Batch Group - Shot Name',
                    'isVisible': scope_file,
                    'execute': media_hub_import_to_batch_group_from_shot_name,
                    'minimumVersion': '2025.1',
                    'order': 1,
                },
                {
                    'name': 'Create New Batch Group - Shot Name - All Clips One Batch',
                    'isVisible': scope_file,
                    'execute': media_hub_import_to_batch_group_from_shot_name_all_clips,
                    'minimumVersion': '2025.1',
                    'order': 2,
                },
                {
                    'name': 'Create New Batch Group - Clip Name',
                    'isVisible': scope_file,
                    'execute': media_hub_import_to_batch_group_from_clip_name,
                    'minimumVersion': '2025.1',
                    'order': 3,
                },
                {
                    'name': 'Create New Batch Group - Clip Name - All Clips One Batch',
                    'isVisible': scope_file,
                    'execute': media_hub_import_to_batch_group_from_clip_name_all_clips,
                    'minimumVersion': '2025.1',
                    'order': 4,
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
                    'minimumVersion': '2025.1',
                    'order': 1,
                },
                {
                    'name': 'Shot Name - All Clips One Batch',
                    'isVisible': scope_clip,
                    'execute': clip_to_batch_group_shot_name_all_clips,
                    'minimumVersion': '2025.1',
                    'order': 2,
                },
                {
                    'name': 'Clip Name',
                    'isVisible': scope_clip,
                    'execute': clip_to_batch_group_clip_name,
                    'minimumVersion': '2025.1',
                    'order': 3,
                },
                {
                    'name': 'Clip Name - All Clips One Batch',
                    'isVisible': scope_clip,
                    'execute': clip_to_batch_group_clip_name_all_clips,
                    'minimumVersion': '2025.1',
                    'order': 4,
                }
            ]
        }
    ]
