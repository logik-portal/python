# Neat Freak
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
Script Name: Neat Freak
Script Version: 2.2.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 10.22.21
Update Date: 04.19.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch/Media Panel/Timeline

Description:

    Add Neat/Render/Write nodes to selected clips in Batch, Media Panel, or Timeline Segments.

Usage:

    Neat OFX 5.x or 6.x is required!

    Select multiple clips in Batch, Media Panel, or Timeline Segments. When selecting clips in the Media Panel, a new Batch Group will be created.

    Render/Write node outputs are set to match each clip's: name, duration, timecode, fps, etc.

    Using Neat Node Profiles:

        - Using Neat Node Profiles allows for easily applying the same Neat node
          settings to multiple clips bypassing having to set each Neat node manually.

        - Enabled by default. To turn off, disable in Neat Freak setup. When
          disabled, the Neat node loads with default settings. When enabled, a
          prompt appears to select a Neat node profile.

        - To create a Neat node profile: add a Neat node, go into the node and apply
          desired settings, then right-click on the Neat node and select
          Neat Freak... -> Save Neat Node Profile. The profile then appears in
          the selection prompt. Multiple profiles can be created. Profiles
          are saved per project.

URL:

    https://logik-portal.com/scripts/#neat_freak

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Neat Freak Setup

    Batch:
        Right-click on any clips(s) in batch -> Neat Freak... -> Neat Denoise Selected Clips

    Media Panel:
        Right-click on any clips(s) in media panel -> Neat Freak... -> Neat Denoise Selected Clips

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.2.0 04.19.26
        - Updated to work in Flame 2027+.
        - Added option to save/use Neat node profiles.
        - Added ability to add Neat OFX to selected timeline segments.
        - Fixed: Bug causing multiple Neat reels to be created in a batch group.

    v2.1.0 03.28.26
        - Updated to PyFlameLib v5.3.0.

    v2.0.0 12.18.25
        - Removed Write node options from setup. Write nodes now use default settings set in Flame Preferences(2026.2+).
        - Added render destination reel options to setup.
        - Added option to enable/disable render node in setup.
        - Only new nodes are framed after creation.

    v1.10.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Tab-key cycles through entries in setup window.

    v1.9.0 04.12.25
        - Updated to PyFlameLib v4.3.0.
        - Works with Neat v6.x.
        - Added check for Neat OFX plugin. If not found, show error message and return.

    v1.8.0 01.02.25
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.7.0 09.09.24
        - Updated to PyFlameLib v3.0.0.
        - Misc bug fixes.

    v1.6.0 02.05.24
        - Added entry field for render node suffix name in setup.
        - Added option to turn Add to Workspace on/off for Write nodes.
        - Updates to UI/PySide.
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.

    v1.5 02.04.23
        - Script now checks if script is installed in correct path.

    v1.4 01.25.23
        - Render/Write nodes now take start frame into account when setting render range.
        - Colour Management in render node now gets set to 16-bit float, Colour Management node is no longer needed/added.
        - Updated config file loading/saving.
        - Moved menus for Flame 2023.2+:
            Setup:
                Flame Main Menu -> Logik -> Logik Portal Script Setup -> Neat Freak Setup
            Batch:
                Right-click on any clip in batch -> Neat Denoise Selected Clips
            Media Panel:
                Right-click on any clip in media panel -> Neat Denoise Selected Clips

    v1.3 08.03.22
        - Color management node added after Neat node to take render down to 16bit/float.
        - Render node will try to renders to go to the Batch Renders shelf reel if other shelf reels exist.

    v1.2 07.14.22
        - Neat/render nodes can now be added to selected clips in batch.
        - Write nodes can now be used instead of render nodes.
        - Added Setup options for setting up Write nodes. Flame Main Menu -> PyFlame -> Neat Freak Setup

    v1.1 10.26.21
        - Script now attempts to add shot name to render node.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os

import flame
from lib.pyflame_lib_neat_freak import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Neat Freak'
SCRIPT_VERSION = 'v2.2.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class NeatFreak:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Init Variables
        self.selection = selection
        self.y_position = 0
        self.x_position = 0
        self.batch_duration = 1
        self.created_nodes = []
        self.selected_neat_node_profile = None

        # Load/Create config
        self.settings = self.load_config()

    def load_config(self):
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.
        """

        settings = PyFlameConfig(
            config_values={
                'render_node_type': 'Render',
                'render_reel_type': 'Schematic',
                'render_reel_name': 'Neat Renders',
                'render_node_suffix': '_NEAT',
                'render_node_enabled': True,
                'use_neat_node_profile': True,
                }
            )

        return settings

    # ==============================================================================

    def batch_neat_clips(self):
        """
        Batch Neat Clips
        ===============

        Create Neat/Render node setups for all clips in selection.
        """

        # Get current batch
        self.batch_group = flame.batch

        # Select Neat node profile if option is enabled
        if self.settings.use_neat_node_profile:
            self.select_neat_node_profile()
            if self.selected_neat_node_profile == 'abort':
                pyflame.print('Neat node profile not selected. Aborting.')
                return

        # Create Neat/Render node setups for all clips in selection
        for clip in self.selection:
            self.x_position = clip.pos_x
            self.y_position = clip.pos_y

            self.get_clip_info(clip)

            self.create_batch_nodes(clip)

        # Select new nodes in batch group and frame them
        new_selection = list(self.selection) + self.created_nodes
        self.batch_group.select_nodes(new_selection)
        self.batch_group.frame_selected()

        pyflame.print('Neat Nodes Created')
        return True

    def media_panel_neat_clips(self):
        """
        Media Panel Neat Clips
        ======================

        Create Batch Group with Neat/Render node setups for all clips in selection.
        """

        flame.go_to('Batch')

        # Create batch group
        batch_group = flame.batch.create_batch_group('Neat', reels=['plates'])

        plates_reel = batch_group.reels[0]

        batch_group.expanded = False

        # Copy all clips in selection to batch
        for clip in self.selection:
            flame.media_panel.copy(clip, plates_reel)

        # Create new selection of all clips in batch
        self.selection = flame.batch.nodes
        self.selection.reverse()

        # Repo clips in batch to spread them out
        clip_pos_y = 200

        for clip in self.selection:
                clip_pos_y += 200
                clip.pos_y = clip_pos_y

        # Set batch duration if duration of current clip is longer than last or Default
        for clip in flame.batch.nodes:
            if int(str(clip.duration)) > int(str(batch_group.duration)):
                batch_group.duration = int(str(clip.duration))

        # Run batch neat clips on all clips in batch
        neat_nodes_created = self.batch_neat_clips()
        print('Neat nodes created:', neat_nodes_created)
        if not neat_nodes_created:
            pyflame.print('Neat nodes not created. Deleting batch group.')
            flame.delete(batch_group)
            return

        batch_group.frame_all()

    def timeline_neat_clips(self):
        """
        Timeline Neat Clips
        ===================

        Add Neat OFX to selected timeline segments.
        """

        pyflame.print('Adding Neat OFX to selected timeline segments...')

        # Select Neat node profile if option is enabled
        if self.settings.use_neat_node_profile:
            self.select_neat_node_profile()
            if self.selected_neat_node_profile == 'abort':
                pyflame.print('Neat node profile not selected. Aborting.')
                return

        print('Selected Neat node profile:', self.selected_neat_node_profile, '\n')

        for item in self.selection:
            if item.type == 'Video Segment':
                try:
                    neat_ofx = item.create_effect('OpenFX')
                except:
                    pyflame.print('Error creating Neat OFX on segment')
                    continue
                if self.selected_neat_node_profile:
                    neat_ofx.load_setup(self.selected_neat_node_profile)
                    pyflame.print(f'{item.name}: Neat OFX setup loaded from profile.')
                else:
                    try:
                        neat_ofx.load_setup(f'{SCRIPT_PATH}/assets/timeline_fx_default_setups/Neat_v6.openfx_node')
                        pyflame.print(f'{item.name}: Loaded default Neat OFX v6 setup.')
                    except:
                        try:
                            neat_ofx.load_setup(f'{SCRIPT_PATH}/assets/timeline_fx_default_setups/Neat_v5.openfx_node')
                            pyflame.print(f'{item.name}: Loaded default Neat OFX v5 setup.')
                        except:
                            flame.delete(neat_ofx)
                            pyflame.print(f'{item.name}: Error loading Neat OFX setup.')
                            return

        PyFlameMessageWindow(
            message=f'Neat OFX added to selected timeline segments.',
            message_type=MessageType.INFO,
            parent=None,
            )

    # ==============================================================================

    def select_neat_node_profile(self):
        """
        Select Neat Node Profile
        ========================

        Select Neat node profile from saved profiles.
        """

        def apply_profile() -> None:
            """
            Apply Profile
            ============

            Apply selected Neat node profile.
            """

            self.selected_neat_node_profile = os.path.join(neat_node_profile_folder, self.select_profile_menu.text + '.openfx_node')

            self.select_profile_window.close()

        def close_window() -> None:
            """
            Close Window
            ============

            Close window and cancel changes.
            """

            self.select_profile_window.close()

            self.selected_neat_node_profile = 'abort'

        neat_node_profile_folder = os.path.join(SCRIPT_PATH, f'neat_node_profiles/{flame.project.current_project.name}')
        print('Neat node profile folder:', neat_node_profile_folder)

        # Check if neat node profile folder exists
        if not os.path.isdir(neat_node_profile_folder) or not os.listdir(neat_node_profile_folder):

            continue_without_profile = PyFlameMessageWindow(
                message=(
                    'No saved Neat node profiles found.\n\n'
                    'To create a Neat node profile:\n'
                    'Add a Neat node, create a grain profile, right-click on the Neat node '
                    'and select Neat Freak... -> Save Neat Node Profile.\n\n'
                    'Use of saved profiles can be disabled in Neat Freak setup.\n'
                    'Flame Main Menu -> Logik -> Logik Portal Script Setup -> Neat Freak Setup.\n\n'
                    'Cancel to abort or continue without profile?'
                    ),
                message_type=MessageType.CONFIRM,
                parent=None,
                )

            if not continue_without_profile:
                self.selected_neat_node_profile = 'abort'
                return
            else:
                self.selected_neat_node_profile = None
                return

        neat_node_profile_files = [f.split('.')[0] for f in os.listdir(neat_node_profile_folder) if f.endswith('.openfx_node')]
        print('Neat Node Profile Files:', neat_node_profile_files, '\n')

        self.select_profile_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}</small>',
            return_pressed=apply_profile,
            escape_pressed=close_window,
            grid_layout_columns=2,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.select_profile_label = PyFlameLabel(
            text='Select Neat Node Profile',
            )

        # Menus
        self.select_profile_menu = PyFlameMenu(
            text=neat_node_profile_files[0],
            menu_options=neat_node_profile_files,
            )

        # Buttons
        self.select_profile_apply_button = PyFlameButton(
            text='Apply',
            connect=apply_profile,
            color=Color.BLUE,
            )
        self.select_profile_cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ==============================================================================
        # [Widget Layout]
        # ==============================================================================

        self.select_profile_window.grid_layout.addWidget(self.select_profile_label, 0, 0)
        self.select_profile_window.grid_layout.addWidget(self.select_profile_menu, 0, 1)

        self.select_profile_window.grid_layout.addWidget(self.select_profile_cancel_button, 2, 0)
        self.select_profile_window.grid_layout.addWidget(self.select_profile_apply_button, 2, 1)

        # ==============================================================================

        self.select_profile_window.exec_()

    def get_clip_info(self, clip):
        """
        Get Clip Info
        =============

        Get clip values for use in Neat/Render nodes.

        Args
        ----
            clip (PyFlameClip):
                Flame clip object.
        """

        self.clip_name = str(clip.name)[1:-1]
        self.clip_duration = clip.duration
        self.clip_frame_rate = clip.clip.frame_rate
        self.clip_timecode = clip.clip.start_time
        self.clip_shot_name = pyflame.resolve_shot_name(self.clip_name)

    def create_batch_nodes(self, clip) -> None:
        """
        Create Batch Nodes
        ==================

        Create Neat/Render node setups for clip.

        Args
        ----
            clip (PyFlameClip):
               Flame clip object.

        Returns
        -------
            None
        """

        def set_render_destination():
            """
            Set Render Destination
            ======================

            Set render destination reel. If reel does not exist, create it.
            """

            render_destination = None

            if self.settings.render_reel_type == 'Schematic':
                for reel in self.batch_group.reels:
                    if reel.name == self.settings.render_reel_name:
                        return
                if not render_destination:
                    reel = self.batch_group.create_reel(self.settings.render_reel_name) # Create schematic reel
                    return
            elif self.settings.render_reel_type == 'Shelf':
                for reel in self.batch_group.shelf_reels:
                    if reel.name == self.settings.render_reel_name:
                        return
                if not render_destination:
                    self.batch_group.create_shelf_reel(self.settings.render_reel_name)
                    return

        def add_render_node(node_type: str):
            """
            Add Render Node
            ===============

            Add render node to batch group and set render node values.

            Args
            ----
                node_type (str):
                    Type of render node to add. 'Render' or 'Write File'.

            Returns
            -------
                render_node (PyFlameNode):
                    Render node object.
            """

            # Create render node
            render_node = self.batch_group.create_node(node_type)

            # Set basic metadata for render/write file node for Flame 2027+
            try:
                render_node.basic_metadata = 'Custom Values'
                render_node.collapsed = True
            except:
                pass

            # Set render node values
            render_node.name = self.clip_name + self.settings.render_node_suffix
            render_node.range_start = self.batch_group.start_frame
            render_node.range_end = int(str(self.batch_group.start_frame)) + int(str(self.clip_duration)) - 1
            render_node.frame_rate = self.clip_frame_rate
            render_node.source_timecode = self.clip_timecode
            render_node.record_timecode = self.clip_timecode
            render_node.destination = ('Batch Reels', f'{self.settings.render_reel_name}')

            if self.clip_shot_name:
                render_node.shot_name = self.clip_shot_name

            self.created_nodes.append(render_node)

            return render_node

        def add_neat_node():
            """
            Add Neat Node
            =============

            Add Neat node to batch group and set Neat node values.

            If a Neat node profile is selected, load the profile instead of creating a new Neat node.
            """

            # Try to add an OpenFX node. If not found, return None.
            try:
                neat_node = self.batch_group.create_node('OpenFX')
                neat_node.pos_x = self.x_position + 300
                neat_node.pos_y = self.y_position - 25
                self.created_nodes.append(neat_node)
            except:
                return None

            # Load Neat node profile if selected
            if self.selected_neat_node_profile:
                neat_node.load_node_setup(self.selected_neat_node_profile)
                return neat_node

            # Try to load Neat v6, if not found, try Neat v5.
            try:
                neat_node.change_plugin('Reduce Noise v6')
            except:
                try:
                    neat_node.change_plugin('Reduce Noise v5')
                except:
                    flame.delete(neat_node)
                    return None

            return neat_node

        # Add Neat Node, if Neat OFX is not found, show error message and return.
        neat_node = add_neat_node()
        if not neat_node:
            PyFlameMessageWindow(
                message='Neat OFX not found. Install Neat and try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Set render destination
        set_render_destination()

        # Add Render Node or Write File Node
        render_node = add_render_node(node_type=self.settings.render_node_type)

        # Set render node position
        render_node.pos_x = neat_node.pos_x + 300
        render_node.pos_y = neat_node.pos_y - 0

        # Connect nodes: Clip -> Neat -> Render
        flame.batch.connect_nodes(clip, 'Default', neat_node, 'Default')
        flame.batch.connect_nodes(neat_node, 'Default', render_node, 'Default')

        self.y_position = self.y_position - 200

        if not self.settings.render_node_enabled:
            render_node.bypass = True

        pyflame.print(f'Created Neat/Render node setup for: {self.clip_name}')

    # ==============================================================================

    def neat_freak_setup(self):
        """
        Neat Freak Setup
        ================

        Setup window for setting up Neat Freak.
        """

        def save_config():
            """
            Save Config
            ===========

            Check if all required fields are filled in and save config values.
            """

            if not self.render_node_suffix_entry.text:
                PyFlameMessageWindow(
                    message='Enter Render Node NameExtension.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return
            elif not self.render_reel_name_entry.text:
                PyFlameMessageWindow(
                    message='Enter Render Reel Name.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return
            else:
                self.settings.save_config(
                    config_values={
                        'render_node_type': self.render_node_type_menu.text,
                        'render_node_suffix': self.render_node_suffix_entry.text,
                        'render_reel_type': self.render_reel_type_menu.text,
                        'render_reel_name': self.render_reel_name_entry.text,
                        'render_node_enabled': self.render_node_enabled_push_button.checked,
                        'use_neat_node_profile': self.use_neat_node_profile_push_button.checked,
                        }
                    )

                self.setup_window.close()

        def close_window():
            """
            Close Window
            ============
            """

            self.setup_window.close()

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}</small>',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=6,
            grid_layout_adjust_column_widths={2: 50},
            parent=None,
            )

        # Labels
        self.render_node_type_label = PyFlameLabel(
            text='Render Node Type',
            )
        self.render_node_suffix_label = PyFlameLabel(
            text='Render Node Suffix',
            )
        self.render_reel_type_label = PyFlameLabel(
            text='Render Destination',
            )
        self.render_reel_name_label = PyFlameLabel(
            text='Render Reel Name',
            )

        # Entries
        self.render_node_suffix_entry = PyFlameEntry(
            text=self.settings.render_node_suffix,
            )
        self.render_reel_name_entry = PyFlameEntry(
            text=self.settings.render_reel_name,
            )

        # Menus
        self.render_node_type_menu = PyFlameMenu(
            text=self.settings.render_node_type,
            menu_options=[
                'Render',
                'Write File',
                ],
            )
        self.render_reel_type_menu = PyFlameMenu(
            text=self.settings.render_reel_type,
            menu_options=[
                'Schematic',
                'Shelf',
                ],
            )

        # Push Buttons
        self.render_node_enabled_push_button = PyFlamePushButton(
            text='Render Node Enabled',
            checked=self.settings.render_node_enabled,
            tooltip='Disable to have render node bypassed by default.',
            )
        self.use_neat_node_profile_push_button = PyFlamePushButton(
            text='Use Saved Profiles',
            checked=self.settings.use_neat_node_profile,
            tooltip='Enable to use saved Neat node profiles. A neat node with a grain profile set will need to be saved. A prompt will appear to select from saved profiles.',
            )

        # Buttons
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.setup_window.close,
            )

        # ==============================================================================
        # [Widget Layout]
        # ==============================================================================

        self.setup_window.grid_layout.addWidget(self.render_node_type_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.render_node_type_menu, 0, 1)

        self.setup_window.grid_layout.addWidget(self.render_node_suffix_label, 1, 0)
        self.setup_window.grid_layout.addWidget(self.render_node_suffix_entry, 1, 1)

        self.setup_window.grid_layout.addWidget(self.render_node_enabled_push_button, 3, 3)
        self.setup_window.grid_layout.addWidget(self.use_neat_node_profile_push_button, 3, 4)

        self.setup_window.grid_layout.addWidget(self.render_reel_type_label, 0, 3)
        self.setup_window.grid_layout.addWidget(self.render_reel_type_menu, 0, 4)

        self.setup_window.grid_layout.addWidget(self.render_reel_name_label, 1, 3)
        self.setup_window.grid_layout.addWidget(self.render_reel_name_entry, 1, 4)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 5, 3)
        self.setup_window.grid_layout.addWidget(self.save_button, 5, 4)

        # ==============================================================================

        # Set focus to first entry.
        self.render_node_suffix_entry.set_focus()

        # Tab-key focus order
        self.setup_window.tab_order = [
            self.render_node_suffix_entry,
            self.render_reel_name_entry,
            ]

# ==============================================================================

def neat_media_panel_clips(selection):

    script = NeatFreak(selection)
    script.media_panel_neat_clips()

def neat_batch_clips(selection):

    script = NeatFreak(selection)
    script.batch_neat_clips()

def neat_timeline_clips(selection):

    script = NeatFreak(selection)
    script.timeline_neat_clips()

def setup(selection):

    script = NeatFreak(selection)
    script.neat_freak_setup()

def save_neat_node_profile(selection):
    """
    Save Neat Node Profile
    ======================

    Save Neat node profile.
    """

    # Create Input Dialog
    input_dialog = PyFlameInputDialog(
        title='Save Neat Node Profile',
        text=f'{str(selection[0].name)[1:-1]}',
        label_text='Enter Neat Node Profile Name',
        parent=None,
        )

    if input_dialog.text:
        neat_node_profile_folder = os.path.join(SCRIPT_PATH, f'neat_node_profiles/{flame.project.current_project.name}')
        if not os.path.isdir(neat_node_profile_folder):
            os.makedirs(neat_node_profile_folder)
        neat_node_setup_path = os.path.join(SCRIPT_PATH, f'neat_node_profiles/{flame.project.current_project.name}', input_dialog.text)
        selection[0].save_node_setup(neat_node_setup_path)
        pyflame.print(f'Neat Node Setup Saved: {neat_node_setup_path}')

        PyFlameMessageWindow(
            message=f'Neat node profile saved: {input_dialog.text}',
            parent=None,
            )

    else:
        print('User canceled.')
        return

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_clip(selection):

    for item in selection:
        if isinstance(item, (flame.PyClip, flame.PyClipNode)):
            return True
    return False

def scope_neat_node(selection):
    for item in selection:
        if isinstance(item, flame.PyNode) and 'Reduce_Noise' in str(item.name):
            return True
    return False

def scope_segment(selection):

    for item in selection:
        if isinstance(item, flame.PySegment):
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
                    'name': 'Neat Freak Setup',
                    'execute': setup,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Neat Freak...',
            'actions': [
                {
                    'name': 'Neat Denoise Selected Clips',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': neat_batch_clips,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': 'Save Neat Node Profile',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_neat_node,
                    'execute': save_neat_node_profile,
                    'minimumVersion': '2025.1'
                },
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
           'name': 'Neat Freak...',
           'actions': [
               {
                    'name': 'Neat Denoise Selected Clips',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': neat_media_panel_clips,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_timeline_custom_ui_actions():

    return [
        {
           'name': 'Neat Freak...',
           'actions': [
               {
                    'name': 'Neat Denoise Selected Clips',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_segment,
                    'execute': neat_timeline_clips,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
