# Neat Freak
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
Script Name: Neat Freak
Script Version: 1.10.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 10.22.21
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Add Neat/Render/Write nodes to selected clips in batch or select multiple clips in the media panel to build a new
    batch group with Neat/Render/Write nodes for all selected clips.

    Works with Neat OFX v5.x and Neat OFX v6.x.

    Render/Write node outputs are set to match each clip(name, duration, timecode, fps).

    Write node options can be set in Script Setup.

URL:
    https://github.com/logik-portal/python/neat_freak

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Neat Freak Setup

    Batch:
        Right-click on any clip in batch -> Neat Denoise Selected Clips

    Media Panel:
        Right-click on any clip in media panel -> Neat Denoise Selected Clips

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

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
        - Added entry field for render node extension name in setup.
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

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame
from lib.pyflame_lib_neat_freak import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Neat Freak'
SCRIPT_VERSION = 'v1.10.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

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
                'render_node_type': 'Render Node',
                'write_file_media_path': '/opt/Autodesk',
                'write_file_pattern': '<name>',
                'write_file_create_open_clip': True,
                'write_file_include_setup': False,
                'write_file_create_open_clip_value': '<name>',
                'write_file_include_setup_value': '<name>',
                'write_file_image_format': 'Dpx 10-bit',
                'write_file_compression': 'Uncompressed',
                'write_file_padding': 4,
                'write_file_frame_index': 'Use Start Frame',
                'write_file_version_name': 'v<version>',
                'write_file_add_to_batch_renders': True,
                'render_node_extension': '_Neat',
                }
            )

        return settings

    #-------------------------------------

    def batch_neat_clips(self):

        # Get current batch
        self.batch_group = flame.batch

        for clip in self.selection:
            self.x_position = clip.pos_x
            self.y_position = clip.pos_y

            self.get_clip_info(clip)

            self.create_batch_nodes(clip)

        self.batch_group.frame_all()

        print('Done\n')

    def media_panel_neat_clips(self):

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
        self.batch_neat_clips()

        batch_group.frame_all()

    def get_clip_info(self, clip):
        """
        Get Clip Info
        =============

        Get clip values for use in Neat/Render/Write nodes.

        Args:
        -----
            clip (PyFlameClip):
                Flame clip object.
        """

        self.clip_name = str(clip.name)[1:-1]
        self.clip_duration = clip.duration
        self.clip_frame_rate = clip.clip.frame_rate
        self.clip_timecode = clip.clip.start_time
        self.clip_shot_name = pyflame.resolve_shot_name(self.clip_name)

    def create_batch_nodes(self, clip):

        def add_render_node():
            """
            Add Render Node
            ===============

            Add render node to batch group and set render node values.

            Returns:
            --------
                render_node (PyFlameNode):
                    Render node object.
            """

            # Create render node
            render_node = self.batch_group.create_node('Render')

            # Set render node values
            render_node.range_start = self.batch_group.start_frame
            render_node.range_end = int(str(self.batch_group.start_frame)) + int(str(self.clip_duration)) - 1
            render_node.frame_rate = self.clip_frame_rate
            render_node.source_timecode = self.clip_timecode
            render_node.record_timecode = self.clip_timecode
            render_node.name = self.clip_name + self.settings.render_node_extension
            render_node.destination = ('Batch Reels', 'Batch Renders')
            render_node.bit_depth = '10-bit'
            render_node.bit_depth = '16-bit fp'

            if self.clip_shot_name:
                render_node.shot_name = self.clip_shot_name

            return render_node

        def add_write_node():
            """
            Add Write Node
            ==============

            Add write node to batch group and set write node values.

            Returns:
            --------
                render_node (PyFlameNode):
                    Write node object.
            """

            # Create write node
            render_node = flame.batch.create_node('Write File')

            # Set write node values
            render_node.name = self.clip_name + self.settings.render_node_extension

            render_node.media_path = self.settings.write_file_media_path
            render_node.media_path_pattern = self.settings.write_file_pattern
            render_node.create_clip = self.settings.write_file_create_open_clip
            render_node.include_setup = self.settings.write_file_include_setup
            render_node.create_clip_path = self.settings.write_file_create_open_clip_value
            render_node.include_setup_path = self.settings.write_file_include_setup_value

            image_format = self.settings.write_file_image_format.split(' ', 1)[0]
            bit_depth = self.settings.write_file_image_format.split(' ', 1)[1]

            render_node.file_type = image_format
            render_node.bit_depth = bit_depth

            if self.settings.write_file_compression:
                render_node.compress = True
                render_node.compress_mode = self.settings.write_file_compression
            if image_format == 'Jpeg':
                render_node.quality = 100

            render_node.frame_index_mode = self.settings.write_file_frame_index
            render_node.frame_padding = int(self.settings.write_file_padding)
            render_node.frame_rate = self.clip_frame_rate
            render_node.source_timecode = self.clip_timecode
            render_node.record_timecode = self.clip_timecode
            render_node.shot_name = self.clip_shot_name
            render_node.range_start = int(str(flame.batch.start_frame))
            render_node.range_end = int(str(self.batch_group.start_frame)) + int(str(self.clip_duration)) - 1

            if self.settings.write_file_create_open_clip:
                render_node.version_mode = 'Follow Iteration'
                render_node.version_name = self.settings.write_file_version_name

            render_node.add_to_workspace = self.settings.write_file_add_to_batch_renders

            return render_node

        def add_neat_node():
            """
            Add Neat Node
            =============

            Add Neat node to batch group and set Neat node values.

            Returns:
            --------
                neat_node (PyFlameNode):
                    Neat node object. None if Neat OFX is not found.
            """

            # Try to add an OpenFX node. If not found, return None.
            try:
                neat_node = self.batch_group.create_node('OpenFX')
                neat_node.pos_x = self.x_position + 300
                neat_node.pos_y = self.y_position - 25
            except:
                return None

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

        # Add Render Node or Write File Node
        if self.settings.render_node_type == 'Render Node':
            render_node = add_render_node()
        else:
            render_node = add_write_node()

        # Set render node position
        render_node.pos_x = neat_node.pos_x + 300
        render_node.pos_y = neat_node.pos_y - 0

        # Connect nodes: Clip -> Neat -> Render
        flame.batch.connect_nodes(clip, 'Default', neat_node, 'Default')
        flame.batch.connect_nodes(neat_node, 'Default', render_node, 'Default')

        self.y_position = self.y_position - 200

        pyflame.print(
            message=f'Added Neat nodes added for: {self.clip_name}',
            )

    #-------------------------------------

    def write_node_setup(self):
        """
        Write Node Setup
        ================

        Setup window for setting up Write Nodes.
        """

        def save_config():
            """
            Save Config
            ===========

            Check if all required fields are filled in and save config values.
            """

            if not self.write_file_media_path_entry.text:
                PyFlameMessageWindow(
                    message='Write Node Setup: Enter Media Path.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
            elif not self.write_file_pattern_entry.text:
                PyFlameMessageWindow(
                    message='Write Node Setup: Enter Pattern for image files.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
            elif not self.write_file_create_open_clip_entry.text:
                PyFlameMessageWindow(
                    message='Write Node Setup: Enter Create Open Clip Naming.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
            elif not self.write_file_include_setup_entry.text:
                PyFlameMessageWindow(
                    message='Write Node Setup: Enter Include Setup Naming.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
            elif not self.write_file_version_name_entry.text:
                PyFlameMessageWindow(
                    message='Write Node Setup: Enter Version Naming.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
            else:
                self.settings.save_config(
                    config_values={
                        'render_node_type': self.write_file_render_node_type_menu.text,
                        'write_file_media_path': self.write_file_media_path_entry.text,
                        'write_file_pattern': self.write_file_pattern_entry.text,
                        'write_file_create_open_clip': self.write_file_create_open_clip_button.checked,
                        'write_file_include_setup': self.write_file_include_setup_button.checked,
                        'write_file_create_open_clip_value': self.write_file_create_open_clip_entry.text,
                        'write_file_include_setup_value': self.write_file_include_setup_entry.text,
                        'write_file_image_format': self.write_file_image_format_menu.text,
                        'write_file_compression': self.write_file_compression_menu.text,
                        'write_file_padding': self.write_file_padding_slider.value,
                        'write_file_frame_index': self.write_file_frame_index_menu.text,
                        'write_file_version_name': self.write_file_version_name_entry.text,
                        'write_file_add_to_batch_renders': self.write_file_add_to_batch_renders_button.checked,
                        'render_node_extension': self.render_node_extension_entry.text,
                        }
                    )

                self.setup_window.close()

        def write_file_create_open_clip_button_check():

            if self.write_file_create_open_clip_button.isEnabled() and self.write_file_create_open_clip_button.checked:
                self.write_file_create_open_clip_entry.enabled = True
                self.write_file_open_clip_token_menu.enabled = True
            else:
                self.write_file_create_open_clip_entry.enabled = False
                self.write_file_open_clip_token_menu.enabled = False

        def write_file_include_setup_button_check():
            if self.write_file_include_setup_button.isEnabled() and self.write_file_include_setup_button.checked:
                self.write_file_include_setup_entry.enabled = True
                self.write_file_include_setup_token_menu.enabled = True
            else:
                self.write_file_include_setup_entry.enabled = False
                self.write_file_include_setup_token_menu.enabled = False

        def render_node_type_toggle():
            """
            Render Node Type Toggle
            =======================

            Toggle between Render Node and Write File Node.
            """

            widgets = [
                self.write_file_setup_label,
                self.write_file_media_path_label,
                self.write_file_pattern_label,
                self.write_file_type_label,
                self.write_file_frame_index_label,
                self.write_file_padding_label,
                self.write_file_compression_label,
                self.write_file_settings_label,
                self.write_file_version_name_label,
                self.write_file_media_path_entry,
                self.write_file_pattern_entry,
                self.write_file_create_open_clip_entry,
                self.write_file_include_setup_entry,
                self.write_file_version_name_entry,
                self.write_file_padding_slider,
                self.write_file_image_format_menu,
                self.write_file_compression_menu,
                self.write_file_frame_index_menu,
                self.write_file_pattern_token_menu,
                self.write_file_browse_button,
                self.write_file_include_setup_button,
                self.write_file_create_open_clip_button,
                self.write_file_open_clip_token_menu,
                self.write_file_include_setup_token_menu,
                self.write_file_add_to_batch_renders_button,
                ]

            enable = self.write_file_render_node_type_menu.text == 'Write File Node'

            for widget in widgets:
                widget.enabled = enable

            write_file_create_open_clip_button_check()

            write_file_include_setup_button_check()

        def media_path_browse():

            file_path = pyflame.file_browser(
                path=self.write_file_media_path_entry.text,
                title='Select Directory',
                select_directory=True,
                window_to_hide=[self.setup_window],
                )

            if file_path:
                self.write_file_media_path_entry.text = file_path

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
            grid_layout_columns=6,
            grid_layout_rows=14,
            parent=None,
            )

        # Labels
        self.write_file_render_node_type_label = PyFlameLabel(
            text='Render Node Type'
            )
        self.write_file_setup_label = PyFlameLabel(
            text='Write File Node Setup',
            style=Style.UNDERLINE,
            )
        self.write_file_media_path_label = PyFlameLabel(
            text='Media Path',
            )
        self.write_file_pattern_label = PyFlameLabel(
            text='Pattern',
            )
        self.write_file_type_label = PyFlameLabel(
            text='File Type',
            )
        self.write_file_frame_index_label = PyFlameLabel(
            text='Frame Index',
            )
        self.write_file_padding_label = PyFlameLabel(
            text='Padding',
            )
        self.write_file_compression_label = PyFlameLabel(
            text='Compression',
            )
        self.write_file_settings_label = PyFlameLabel(
            text='Settings',
            style=Style.UNDERLINE,
            )
        self.write_file_version_name_label = PyFlameLabel(
            text='Version Name',
            )
        self.write_file_rendered_clip_label = PyFlameLabel(
            text='Rendered Clip',
            )
        self.render_node_extension_label = PyFlameLabel(
            text='Render Node Extension',
            )

        # Entries
        self.render_node_extension_entry = PyFlameEntry(
            text=self.settings.render_node_extension,
            )
        self.write_file_media_path_entry = PyFlameEntry(
            text=self.settings.write_file_media_path,
            )
        self.write_file_pattern_entry = PyFlameEntry(
            text=self.settings.write_file_pattern,
            )
        self.write_file_create_open_clip_entry = PyFlameEntry(
            text=self.settings.write_file_create_open_clip_value,
            )
        self.write_file_include_setup_entry = PyFlameEntry(
            text=self.settings.write_file_include_setup_value,
            )
        self.write_file_version_name_entry = PyFlameEntry(
            text=self.settings.write_file_version_name,
            )

        # Sliders
        self.write_file_padding_slider = PyFlameSlider(
            min_value=1,
            max_value=20,
            start_value=self.settings.write_file_padding,
            )

        def update_compression_menu():
            """
            Update Compression Menu
            ========================

            Update list of available compression options based on selected image format.
            """

            file_format = self.write_file_image_format_menu.text

            if 'Dpx' in file_format:
                self.write_file_compression_menu.text = 'Uncompressed'
                compression_list = [
                    'Uncompressed',
                    'Pixspan',
                    'Packed',
                    ]
                self.write_file_compression_menu.enabled = True

            elif 'Jpeg' in file_format:
                self.write_file_compression_menu.text = ''
                compression_list = ['']
                self.write_file_compression_menu.enabled = False

            elif 'OpenEXR' in file_format:
                self.write_file_compression_menu.text = 'Uncompressed'
                compression_list = [
                    'Uncompressed',
                    'Scanline',
                    'Multi_Scanline',
                    'RLE',
                    'PXR24',
                    'PIZ',
                    'DWAB',
                    'DWAA',
                    'B44A',
                    'B44',
                    ]
                self.write_file_compression_menu.enabled = True

            elif 'Png' in file_format:
                self.write_file_compression_menu.text = ''
                compression_list = ['']
                self.write_file_compression_menu.enabled = False

            elif 'Sgi' in file_format:
                self.write_file_compression_menu.text = 'Uncompressed'
                compression_list = [
                    'Uncompressed',
                    'RLE',
                    ]
                self.write_file_compression_menu.enabled = True

            elif 'Targa' in file_format:
                self.write_file_compression_menu.text = ''
                compression_list = ['']
                self.write_file_compression_menu.enabled = False

            elif 'Tiff' in file_format:
                self.write_file_compression_menu.text = 'Uncompressed'
                compression_list = [
                    'Uncompressed',
                    'RLE',
                    'LZW',
                    ]
                self.write_file_compression_menu.enabled = True

            self.write_file_compression_menu.update_menu(
                text=compression_list[0],
                menu_options=compression_list
                )

        self.write_file_image_format_menu = PyFlameMenu(
                text=self.settings.write_file_image_format,
                menu_options=[
                    'Dpx 8-bit',
                    'Dpx 10-bit',
                    'Dpx 12-bit',
                    'Dpx 16-bit',
                    'Jpeg 8-bit',
                    'OpenEXR 16-bit fp',
                    'OpenEXR 32-bit fp',
                    'Png 8-bit',
                    'Png 16-bit',
                    'Sgi 8-bit',
                    'Sgi 16-bit',
                    'Targa 8-bit',
                    'Tiff 8-bit',
                    'Tiff 16-bit',
                    ],
                connect=update_compression_menu,
                )

        self.write_file_compression_menu = PyFlameMenu(
                text=self.settings.write_file_compression,
                menu_options=[],
                )

        # Render Type Menu
        self.write_file_render_node_type_menu = PyFlameMenu(
            text=self.settings.render_node_type,
            menu_options=[
                'Render Node',
                'Write File Node',
                ],
            connect=render_node_type_toggle,
            )

        # Frame Index Menu
        self.write_file_frame_index_menu = PyFlameMenu(
            text=self.settings.write_file_frame_index,
            menu_options=[
                'Use Start Frame',
                'Use Timecode',
                ],
            )

        # Token Menus
        write_file_tokens = {
            'Batch Name': '<batch name>',
            'Batch Iteration': '<batch iteration>',
            'Iteration': '<iteration>',
            'Project': '<project>',
            'Project Nickname': '<project nickname>',
            'Shot Name': '<shot name>',
            'Clip Height': '<height>',
            'Clip Width': '<width>',
            'Clip Name': '<name>',
            }

        self.write_file_pattern_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict=write_file_tokens,
            token_dest=self.write_file_pattern_entry,
            )
        self.write_file_open_clip_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict=write_file_tokens,
            token_dest=self.write_file_create_open_clip_entry,
            )
        self.write_file_include_setup_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict=write_file_tokens,
            token_dest=self.write_file_include_setup_entry,
            )

        # Push Buttons
        self.write_file_add_to_batch_renders_button = PyFlamePushButton(
            text='Add to Batch Renders',
            checked=self.settings.write_file_add_to_batch_renders,
            )
        self.write_file_create_open_clip_button = PyFlamePushButton(
            text='Create Open Clip',
            checked=self.settings.write_file_create_open_clip,
            connect=write_file_create_open_clip_button_check,
            )
        write_file_create_open_clip_button_check()

        self.write_file_include_setup_button = PyFlamePushButton(
            text='Include Setup',
            checked=self.settings.write_file_include_setup,
            connect=write_file_include_setup_button_check,
            )
        write_file_include_setup_button_check()

        # Buttons
        self.write_file_browse_button = PyFlameButton(
            text='Browse',
            connect=media_path_browse,
            )
        self.write_file_save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.write_file_cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.setup_window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.setup_window.grid_layout.addWidget(self.write_file_render_node_type_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_render_node_type_menu, 0, 1)

        self.setup_window.grid_layout.addWidget(self.render_node_extension_label, 0, 2)
        self.setup_window.grid_layout.addWidget(self.render_node_extension_entry, 0, 3)

        self.setup_window.grid_layout.addWidget(self.write_file_setup_label, 1, 0, 1, 6)

        self.setup_window.grid_layout.addWidget(self.write_file_media_path_label, 2, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_media_path_entry, 2, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_browse_button, 2, 5)

        self.setup_window.grid_layout.addWidget(self.write_file_pattern_label, 3, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_pattern_entry, 3, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_pattern_token_menu, 3, 5)

        self.setup_window.grid_layout.addWidget(self.write_file_create_open_clip_button, 5, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_create_open_clip_entry, 5, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_open_clip_token_menu, 5, 5)

        self.setup_window.grid_layout.addWidget(self.write_file_include_setup_button, 6, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_include_setup_entry, 6, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_include_setup_token_menu, 6, 5)

        self.setup_window.grid_layout.addWidget(self.write_file_settings_label, 8, 0, 1, 6)
        self.setup_window.grid_layout.addWidget(self.write_file_frame_index_label, 9, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_frame_index_menu, 9, 1)
        self.setup_window.grid_layout.addWidget(self.write_file_type_label, 10, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_image_format_menu, 10, 1)
        self.setup_window.grid_layout.addWidget(self.write_file_compression_label, 11, 0)
        self.setup_window.grid_layout.addWidget(self.write_file_compression_menu, 11, 1)

        self.setup_window.grid_layout.addWidget(self.write_file_padding_label, 9, 2)
        self.setup_window.grid_layout.addWidget(self.write_file_padding_slider, 9, 3)
        self.setup_window.grid_layout.addWidget(self.write_file_rendered_clip_label, 9, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_add_to_batch_renders_button, 9, 5)
        self.setup_window.grid_layout.addWidget(self.write_file_version_name_label, 10, 2)
        self.setup_window.grid_layout.addWidget(self.write_file_version_name_entry, 10, 3)

        self.setup_window.grid_layout.addWidget(self.write_file_cancel_button, 13, 4)
        self.setup_window.grid_layout.addWidget(self.write_file_save_button, 13, 5)

        #-------------------------------------

        update_compression_menu() # Update compression menu based on saved image format
        render_node_type_toggle() # Set initial state of render node type
        self.render_node_extension_entry.set_focus() # Set focus to first entry

        # Tab-key focus order
        self.setup_window.tab_order = [
            self.render_node_extension_entry,
            self.write_file_media_path_entry,
            self.write_file_pattern_entry,
            self.write_file_create_open_clip_entry,
            self.write_file_include_setup_entry,
            self.write_file_version_name_entry,
            ]

#-------------------------------------

def neat_media_panel_clips(selection):

    script = NeatFreak(selection)
    script.media_panel_neat_clips()

def neat_batch_clips(selection):

    script = NeatFreak(selection)
    script.batch_neat_clips()

def setup(selection):

    script = NeatFreak(selection)
    script.write_node_setup()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_clip(selection):

    for item in selection:
        if isinstance(item, (flame.PyClip, flame.PyClipNode)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

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
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Neat Denoise Selected Clips',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': neat_batch_clips,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Neat Denoise Selected Clips',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': neat_media_panel_clips,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
