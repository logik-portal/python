# Import ST Map
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
Script Name: Import ST Map
Script Version: 3.1.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 04.30.21
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Imports ST Maps and builds ST Map setup

    Comp work is recomped over original plate at end of setup

URL:
    https://github.com/logik-portal/python/import_st_map

Menus:

    Right-click in batch or on selected node -> Import... -> Import ST Map - ST Map Node Setup

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.1.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v3.0.0 03.11.25
        - Updated to PyFlameLib v4.3.0.
        - Batch setups are now created with either matchbox or Flame ST Map nodes. Flame ST Map nodes are only available in Flame 2025+.

    v2.9.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v2.8.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v2.7.0 01.21.24
        - Updates to PySide.

    v2.6.0 08.20.23
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.

    v2.5 03.28.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.
        - Fixed resize node saving issue that causes script to fail in 2024.

    v2.4 05.27.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v2.3 03.15.22
        - Updated UI for Flame 2023.
        - Moved UI widgets to external file.

    v2.2 02.17.22
        - Updated config to XML.

    v2.1 01.04.21
        - Files starting with '.' are ignored when searching for undistort map after distort map is selected.

    v2.0 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re

import flame
from lib.pyflame_lib_import_st_map import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Import ST Maps'
SCRIPT_VERSION = 'v3.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ImportSTMap:

    def __init__(self, selection, import_type):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check Script Path, If Path Is Incorrect, Stop Script.
        if not pyflame.verify_script_install():
            return

        # Create/Load Config File Settings.
        self.settings = self.load_config()

        # Get Current Cursor Position
        if selection:
            self.selection = selection[0]
            self.master_pos_x = self.selection.pos_x + 300
            self.master_pos_y = self.selection.pos_y
        else:
            self.selection = ''
            self.master_pos_x = flame.batch.cursor_position[0]
            self.master_pos_y = flame.batch.cursor_position[1]

        # Init Variables
        self.undistort_map_path = ''
        self.redistort_map_path = ''
        self.redistort_map = ''
        self.undistort_map = ''

        # Create ST Map Batch Setup
        if import_type == 'matchbox':
            self.create_st_map_matchbox_setup()
        elif import_type == 'st_map_node':
            self.create_st_map_node_setup()

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
                'st_map_path': '/opt/Autodesk'
                }
            )

        return settings

    def save_config(self, undistort_map_path) -> None:
        """
        Save Config
        ===========

        Save config values to config file.
        """

        self.settings.save_config(
            config_values={
                'st_map_path': undistort_map_path.rsplit('/', 1)[0]
                }
            )

    #-------------------------------------

    def get_st_maps(self) -> tuple:
        """
        Get ST Maps
        ===========

        Prompt user to select undistort and redistort ST Maps.

        The ST Maps are added to the 'st_maps' schematic reel in the current batch group.
        If a 'st_maps' reel does not exist, it is created.

        Returns:
        --------
            tuple: A tuple containing the undistort and redistort st map objects.
        """

        undistort_map_path = None
        redistort_map_path = None

        # Browse for undistort map
        PyFlameMessageWindow(
            message='Select Undistort ST Map',
            message_type=MessageType.INFO,
            parent=None,
            )

        undistort_map_path = pyflame.file_browser(
            path=self.settings.st_map_path,
            title='Load Undistort ST Map (EXR)',
            extension=['exr'],
            )

        # If undistort map not selected, return
        if not undistort_map_path:
            return None, None

        # Make sure map selected is undistort, if not, start over
        if not re.search('undistort', undistort_map_path, re.I):
            PyFlameMessageWindow(
                message=('Undistort Map Not Selected.\n\n"undistort" Should be in Selected File Name.'),
                message_type=MessageType.ERROR,
                parent=None,
                )
            return None, None

        # Search for undistort folder for redistort map
        pyflame.print('Searching for ST Redistort Map...')

        for root, dirs, files in os.walk(undistort_map_path.rsplit('/', 1)[0]):
            for f in files:
                if not f.startswith('.'):
                    if re.search('redistort', f, re.I):
                        redistort_map_path = os.path.join(root, f)
                        pyflame.print('ST Redistort Map Found', text_color=TextColor.GREEN)
                        break

        # If redistort map not found in search, browse for it
        if not redistort_map_path:
            PyFlameMessageWindow(
                message='Select Redistort ST Map',
                message_type=MessageType.INFO,
                parent=None,
                )

            redistort_map_path = pyflame.file_browser(
                path=undistort_map_path,
                title='Load Undistort ST Map (EXR)',
                extension=['exr'],
                )

            if not redistort_map_path:
                return None, None

            # Make sure map selected is undistort, if not, start over
            if not re.search('redistort', redistort_map_path, re.I):
                PyFlameMessageWindow(
                    message=(
                        'Redistort Map Not Selected.\n\n'
                        '"redistort" Should be in Selected File Name.'
                        ),
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return None, None

        # If redistort map not selected, return
        if not redistort_map_path:
            return None, None

        # Create st maps schematic reel if it doesn't exist
        if 'st_maps' not in [reel.name for reel in flame.batch.reels]:
            flame.batch.create_reel('st_maps')

        # Import maps
        undistort_map = flame.batch.import_clip(undistort_map_path, 'st_maps')
        redistort_map = flame.batch.import_clip(redistort_map_path, 'st_maps')

        pyflame.print('ST Maps Imported', text_color=TextColor.GREEN)

        # Save config
        self.save_config(undistort_map_path)

        return undistort_map, redistort_map

    def create_st_map_matchbox_setup(self) -> None:
        """
        Create ST Map Matchbox Setup
        ============================

        Create setup with ST Map workflow with 3d camera. Recomp over original plate at end.
        Prompt user to select undistort and redistort ST Maps.

        Uses Matchbox node for ST Map undistort and redistort.
        """

        def build_st_map_matchbox_setup(undistort_map, redistort_map) -> None:

            pyflame.print('Building ST Map Matchbox Setup...')

            # Get unique node names
            new_node_names = pyflame.generate_unique_node_names(
                node_names=[
                    'mux_in',
                    'uvmap_3vis_undistort',
                    'st_map_undistort_map',
                    'mux',
                    'divide',
                    'uvmap_3vis_redistort',
                    'uvmap_3vis_redistort_matte',
                    'st_map_redistort_map',
                    'result_comp',
                    'regrain',
                    'comp',
                    ],
                existing_node_names=[str(node.name)[1:-1] for node in flame.batch.nodes]
                )

            # Path to UVMap_3vis matchbox
            matchbox_path = os.path.join(SCRIPT_PATH, 'assets/matchbox/uvmap_3vis')

            #-------------
            # Create nodes
            #-------------

            plate_in_mux = flame.batch.create_node('MUX')
            plate_in_mux.name = new_node_names[0]
            plate_in_mux.pos_x = self.master_pos_x + 300
            plate_in_mux.pos_y = self.master_pos_y

            st_map_undistort = flame.batch.create_node('Matchbox')
            st_map_undistort.load_node_setup(matchbox_path)
            st_map_undistort.name = new_node_names[1]
            st_map_undistort.pos_x = plate_in_mux.pos_x + 600
            st_map_undistort.pos_y = plate_in_mux.pos_y - 300

            st_map_undistort_mux = flame.batch.create_node('MUX')
            st_map_undistort_mux.name = new_node_names[2]
            st_map_undistort_mux.pos_x = st_map_undistort.pos_x - 300
            st_map_undistort_mux.pos_y = st_map_undistort.pos_y - 300

            comp_action = flame.batch.create_node('Action')
            comp_action.name = new_node_names[10]
            comp_action.pos_x = st_map_undistort.pos_x + 600
            comp_action.pos_y = st_map_undistort.pos_y - 60
            comp_action.load_node_setup(f'{SCRIPT_PATH}/assets/action_nodes/camera_action/camera_action.flare.action')
            comp_action.collapsed = False

            mux = flame.batch.create_node('MUX')
            mux.name = new_node_names[3]
            mux.pos_x = comp_action.pos_x + 600
            mux.pos_y = comp_action.pos_y - 65

            divide_comp = flame.batch.create_node('Comp')
            divide_comp.name = new_node_names[4]
            divide_comp.flame_blend_mode = 'Divide'
            divide_comp.swap_inputs = True
            divide_comp.pos_x = mux.pos_x + 600
            divide_comp.pos_y = mux.pos_y + 70

            st_map_redistort = flame.batch.create_node('Matchbox')
            st_map_redistort.load_node_setup(matchbox_path)
            st_map_redistort.name = new_node_names[5]
            st_map_redistort.pos_x = mux.pos_x + 250
            st_map_redistort.pos_y = mux.pos_y + 100

            st_map_redistort_matte = flame.batch.create_node('Matchbox')
            st_map_redistort_matte.load_node_setup(matchbox_path)
            st_map_redistort_matte.name = new_node_names[6]
            st_map_redistort_matte.pos_x = st_map_redistort.pos_x
            st_map_redistort_matte.pos_y = st_map_redistort.pos_y - 190

            st_map_redistort_mux = flame.batch.create_node('MUX')
            st_map_redistort_mux.name = new_node_names[7]
            st_map_redistort_mux.pos_x = mux.pos_x
            st_map_redistort_mux.pos_y = st_map_redistort.pos_y - 400

            result_comp_action = flame.batch.create_node('Action')
            result_comp_action.name = new_node_names[8]
            result_comp_action.collapsed = True
            result_comp_action.pos_x = plate_in_mux.pos_x + 2750
            result_comp_action.pos_y = self.master_pos_y + 10

            # Create redistort action media layer 1
            result_comp_action_in_media = result_comp_action.add_media()
            result_comp_action_in_media.pos_x = result_comp_action.pos_x - 40
            result_comp_action_in_media.pos_y = result_comp_action.pos_y - 490

            # Create regrain node
            regrain_node = flame.batch.create_node('Regrain')
            regrain_node.name = new_node_names[9]
            regrain_node.pos_x = result_comp_action.pos_x + 450
            regrain_node.pos_y = result_comp_action.pos_y

             # Position nodes in batch
            undistort_map.pos_x = st_map_undistort_mux.pos_x - 300
            undistort_map.pos_y = st_map_undistort_mux.pos_y + 30

            redistort_map.pos_x = st_map_redistort_mux.pos_x - 300
            redistort_map.pos_y = st_map_redistort_mux.pos_y + 30

            # Edit recomp action node
            result_comp_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/st_map_node_action/comp.action'))

            # Connect nodes
            if self.selection != '':
                flame.batch.connect_nodes(self.selection, 'Default', plate_in_mux, 'Input_0')

            flame.batch.connect_nodes(plate_in_mux, 'Result', st_map_undistort, 'Input 1')
            flame.batch.connect_nodes(plate_in_mux, 'Result', result_comp_action, 'Back')
            flame.batch.connect_nodes(st_map_undistort_mux, 'Result', st_map_undistort, 'Input 2')
            flame.batch.connect_nodes(st_map_undistort, 'Result', comp_action, 'Back')
            flame.batch.connect_nodes(undistort_map, 'Default', st_map_undistort_mux, 'Input_0')

            flame.batch.connect_nodes(comp_action, 'Output [ Comp ]', mux, 'Input_0')
            flame.batch.connect_nodes(comp_action, 'Output [ Matte ]', mux, 'Matte_0')
            flame.batch.connect_nodes(st_map_redistort, 'Result', divide_comp, 'Front')
            flame.batch.connect_nodes(st_map_redistort_matte, 'Result', divide_comp, 'Back')

            flame.batch.connect_nodes(mux, 'Result', st_map_redistort, 'Input 1')
            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort, 'Input 2')
            flame.batch.connect_nodes(redistort_map, 'Default', st_map_redistort_mux, 'Input_0')
            flame.batch.connect_nodes(mux, 'OutMatte', st_map_redistort_matte, 'Input 1')
            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort_matte, 'Input 2')

            flame.batch.connect_nodes(divide_comp, 'Result', result_comp_action_in_media, 'Front')
            flame.batch.connect_nodes(st_map_redistort_matte, 'Result',  result_comp_action_in_media, 'Matte')

            flame.batch.connect_nodes(result_comp_action, 'Comp [ Comp ]', regrain_node, 'Front')
            flame.batch.connect_nodes(result_comp_action, 'Comp [ Comp ]', regrain_node, 'Back')
            flame.batch.connect_nodes(result_comp_action, 'Matte [ Matte ]', regrain_node, 'Matte')

            pyflame.print('ST Map Matchbox Batch Setup Created', text_color=TextColor.GREEN)

        # Load st maps
        undistort_map, redistort_map = self.get_st_maps()

        # Build st map setup if ST Maps have be selected, otherwise end script.
        if undistort_map and redistort_map:
            build_st_map_matchbox_setup(undistort_map, redistort_map)
        else:
            pyflame.print('ST Map Import Cancelled', text_color=TextColor.RED)

    def create_st_map_node_setup(self) -> None:
        """
        Create ST Map Node Setup
        ========================

        Create setup with ST Map workflow with 3d camera. Recomp over original plate at end.
        Prompts user to select undistort and redistort ST Maps.

        Uses ST Map node for ST Map undistort and redistort. Flame 2025+ only.
        """

        def build_st_map_node_setup(undistort_map, redistort_map) -> None:

            pyflame.print('Building ST Map Node Setup...')

            # Make sure node names are unique in batch.
            new_node_names = pyflame.generate_unique_node_names(
                node_names=[
                    'mux_in',
                    'st_map_undistort',
                    'st_map_undistort_map',
                    'mux',
                    'divide',
                    'st_map_redistort',
                    'st_map_redistort_map',
                    'result_comp',
                    'regrain',
                    'comp',
                    ],
                existing_node_names=[str(node.name)[1:-1] for node in flame.batch.nodes]
                )

            #-------------
            # Create nodes
            #-------------

            plate_in_mux = flame.batch.create_node('MUX')
            plate_in_mux.name = new_node_names[0]
            plate_in_mux.pos_x = self.master_pos_x + 300
            plate_in_mux.pos_y = self.master_pos_y

            st_map_undistort = flame.batch.create_node('STMap')
            st_map_undistort.name = new_node_names[1]
            st_map_undistort.pos_x = plate_in_mux.pos_x + 600
            st_map_undistort.pos_y = plate_in_mux.pos_y - 300

            st_map_undistort_mux = flame.batch.create_node('MUX')
            st_map_undistort_mux.name = new_node_names[2]
            st_map_undistort_mux.pos_x = st_map_undistort.pos_x - 300
            st_map_undistort_mux.pos_y = st_map_undistort.pos_y - 300

            comp_action = flame.batch.create_node('Action')
            comp_action.name = new_node_names[9]
            comp_action.pos_x = st_map_undistort.pos_x + 600
            comp_action.pos_y = st_map_undistort.pos_y - 60
            comp_action.load_node_setup(f'{SCRIPT_PATH}/assets/action_nodes/camera_action/camera_action.flare.action')
            comp_action.collapsed = False

            mux = flame.batch.create_node('MUX')
            mux.name = new_node_names[3]
            mux.pos_x = comp_action.pos_x + 600
            mux.pos_y = comp_action.pos_y - 65

            divide_comp = flame.batch.create_node('Comp')
            divide_comp.name = new_node_names[4]
            divide_comp.flame_blend_mode = 'Divide'
            divide_comp.swap_inputs = True
            divide_comp.pos_x = mux.pos_x + 580
            divide_comp.pos_y = mux.pos_y + 150

            st_map_redistort = flame.batch.create_node('STMap')
            st_map_redistort.name = new_node_names[5]
            st_map_redistort.pos_x = mux.pos_x + 250
            st_map_redistort.pos_y = mux.pos_y

            st_map_redistort_mux = flame.batch.create_node('MUX')
            st_map_redistort_mux.name = new_node_names[6]
            st_map_redistort_mux.pos_x = mux.pos_x
            st_map_redistort_mux.pos_y = divide_comp.pos_y - 400

            result_comp_action = flame.batch.create_node('Action')
            result_comp_action.name = new_node_names[7]
            result_comp_action.collapsed = True
            result_comp_action.pos_x = plate_in_mux.pos_x + 2750
            result_comp_action.pos_y = self.master_pos_y + 10

            # Create redistort action media layer 1
            result_comp_action_in_media = result_comp_action.add_media()
            result_comp_action_in_media.pos_x = result_comp_action.pos_x - 40
            result_comp_action_in_media.pos_y = result_comp_action.pos_y - 430

            # Create regrain node
            regrain_node = flame.batch.create_node('Regrain')
            regrain_node.name = new_node_names[8]
            regrain_node.pos_x = result_comp_action.pos_x + 450
            regrain_node.pos_y = result_comp_action.pos_y

             # Position nodes in batch
            undistort_map.pos_x = st_map_undistort_mux.pos_x - 300
            undistort_map.pos_y = st_map_undistort_mux.pos_y + 30

            redistort_map.pos_x = st_map_redistort_mux.pos_x - 300
            redistort_map.pos_y = st_map_redistort_mux.pos_y + 30

            # Load Recomp Action Node
            result_comp_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/st_map_node_action/comp.action'))

            # Connect nodes
            if self.selection != '':
                flame.batch.connect_nodes(self.selection, 'Default', plate_in_mux, 'Input_0')

            flame.batch.connect_nodes(plate_in_mux, 'Result', st_map_undistort, 'Front')
            flame.batch.connect_nodes(plate_in_mux, 'Result', result_comp_action, 'Back')
            flame.batch.connect_nodes(st_map_undistort_mux, 'Result', st_map_undistort, 'STMap')
            flame.batch.connect_nodes(st_map_undistort, 'Result', comp_action, 'Back')
            flame.batch.connect_nodes(undistort_map, 'Default', st_map_undistort_mux, 'Input_0')

            flame.batch.connect_nodes(comp_action, 'Output [ Comp ]', mux, 'Input_0')
            flame.batch.connect_nodes(comp_action, 'Output [ Matte ]', mux, 'Matte_0')
            flame.batch.connect_nodes(st_map_redistort, 'Result', divide_comp, 'Front')
            flame.batch.connect_nodes(st_map_redistort, 'OutMatte', divide_comp, 'Back')
            flame.batch.connect_nodes(mux, 'Result', st_map_redistort, 'Front')

            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort, 'STMap')
            flame.batch.connect_nodes(redistort_map, 'Default', st_map_redistort_mux, 'Input_0')
            flame.batch.connect_nodes(mux, 'OutMatte', st_map_redistort, 'Matte')

            flame.batch.connect_nodes(divide_comp, 'Result', result_comp_action_in_media, 'Front')
            flame.batch.connect_nodes(st_map_redistort, 'OutMatte',  result_comp_action_in_media, 'Matte')

            flame.batch.connect_nodes(result_comp_action, 'Comp [ Comp ]', regrain_node, 'Front')
            flame.batch.connect_nodes(result_comp_action, 'Comp [ Comp ]', regrain_node, 'Back')
            flame.batch.connect_nodes(result_comp_action, 'Matte [ Matte ]', regrain_node, 'Matte')

            pyflame.print('Camera Imported with ST Map Node Setup', text_color=TextColor.GREEN)

        # Load st maps
        undistort_map, redistort_map = self.get_st_maps()

        # Build st map setup if ST Maps have be selected, otherwise end script.
        if undistort_map and redistort_map:
            build_st_map_node_setup(undistort_map, redistort_map)
        else:
            pyflame.print('ST Map Import Cancelled', text_color=TextColor.RED)

#-------------------------------------

def import_matchbox_setup(selection):

    ImportSTMap(selection, 'matchbox')

def import_st_map_node_setup(selection):

    ImportSTMap(selection, 'st_map_node')

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Import...',
            'actions': [
                {
                    'name': 'Import ST Map - Matchbox Setup',
                    'execute': import_matchbox_setup,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Import ST Map - ST Map Node Setup',
                    'execute': import_st_map_node_setup,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
