# Import Camera
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
Script Name: Import Camera
Script Version: 4.16.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 06.02.18
Update Date: 08.27.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Custom Action Type: Batch

Description:

    Creates a new Action node with selected FBX or Alembic file loaded.

    The Action camera will be automatically switched to the new FBX/Alembic camera.

    Options to load with simple re-comp or ST map setups.

URL:
    https://github.com/logik-portal/python/import_camera

Menus:

    Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Import Camera Setup

    To Import:
        Right-click in batch or on selected node -> Import... -> Import FBX Camera
        Right-click in batch or on selected node -> Import... -> Import Alembic Camera

To install:

    Copy script into /opt/Autodesk/shared/python/import_camera

Updates:

    v4.16.0 08.27.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes main window.
        - Added warning message when importing ST Map Matchbox Setup without background clip or node with background resolution selected.
          ST Map and camera track aren't applied properly without the background clip or node with background resolution selected.

    v4.15.0 03.12.25
        - Updated to PyFlameLib v4.3.0.

    v4.14.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v4.13.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v4.12.0 05.09.24
        - Added two new options for working with ST Maps:
            - ST Map Matchbox Setup - Uses UVMap_3vis matchbox for undistort and redistort.
            - ST Map Node Setup - Flame 2025+ only. Uses Flame ST Map node for undistort and redistort.
        - Removed Action node ST Map setup option.
        - Added new buttons (These are not enabled when Import Type is Read File):
            - Linearize Keyframes - Set camera keyframes to linear. Helps with motion blur on first and last frames.
            - Consolidate Geometry - Alembic setting only. Consolidates geometry into a single object.
            - Create Object Group - Alembic setting only. Creates a group for each object in the Alembic file.
            - Load objects - Choose which objects to load from FBX/Alembic file:
                - Cameras
                - Models
                - Lights
                - Mesh Animations
                - Normals
        - Fixed Tokenzied path not working properly.
        - Fixed Linearize keyframes. Was crashing script when applied to loading FBX/ABC files as Read Files.
        - Cleaned up duplicate node naming code.

    v4.11.2 02.25.24
        - Misc UI fixes.

    v4.11.1 01.29.24
        - Fixed PySide6 errors/font in slider calculator.

    v4.11.0 01.02.24
        - Updates to UI/PySide.

    v4.10.0 07.26.23
        - Updated to pyflame lib v2.0.0.

    v4.9.1 06.26.23
        - Updated script versioning to semantic versioning.
        - Load button is now blue.
        - Pressing return in the main window will now load the selected camera.

    v4.9 03.14.23
        - Fixed: ST Map Setup - Resize node setup is not being saved with correct name in 2024.

    v4.8 02.04.23
        - Added check to make sure script is installed in the correct location.

    v4.7 01.17.23
        - Moved setup menu for Flame 2023.2+ to: Flame Main Menu -> Logik -> Logik Portal Script Setup -> Import Camera Setup
        - Fixed not being able to load setup window.
        - Updated config file loading/saving.
        - Fixed: ST Map Setup - Selecting an image other than the undistort map would cause the script to fail.

    v4.6 01.02.23
        - Fixed not being able to select Alembic files in the import browser.
        - Minimum Flame version is now 2022.3.
        - Ability to set tokenized path to always open browser to when importing: Flame Main Menu -> pyFlame -> Import Camera Setup
          By default this is turned off.
        - Patch Setup button renamed to ReComp Setup for clarity.

    v4.5 07.28.22
        - Camera keyframe extrapolation is now set to linear to help with motion blur.

    v4.4 05.26.22
        - Added new flame browser window - Flame 2023.1 and later.
        - Messages print to Flame message window - Flame 2023.1 and later.

    v4.3 03.15.22
        - Moved UI widgets to external file.

    v4.2 02.25.22
        - Updated UI for Flame 2023.
        - Updated config to XML.

    v4.1 01.04.22
        - Files starting with '.' are ignored when searching for undistort map after distort map is selected.

    v4.0 05.22.21
        - Updated to be compatible with Flame 2022/Python 3.7.
        - Redistort map will automatically be found if in the same folder as undistort map.
        - Speed improvements.

    v3.6 02.21.21
        - Updated UI.
        - Improved calculator.
        - Plate resize node in ST Map Setup now takes ratio from st map.

    v3.5 01.25.21
        - Added ability to import Alembic(ABC) files.
        - Fixed UI font size for Linux.

    v3.4 11.05.20
        - Updates to paths and description for Logik Portal.

    v3.3 10.18.20
        - ST Map search no longer case sensitive.
        - If ST Map not found, file browser will open to manually select.

    v3.2 10.12.20
        - Improved spinbox with calculator.

    v3.1 09.26.20
        - Updated UI
        - Import FBX with Patch Setup - Will import FBX into an Action node and also create
          other nodes to re-comp work done in FBX Action over original background.
        - Import FBX with ST map Setup - Will import FBX into an Action node and also build
          a undistort/redistort setup using the ST maps. ST maps must be in the same folder or sub-folder of
          FBX camera for this to work. ST Maps should also contain 'undistort' or 'redistort' in their file
          names.

    v3.0 06.06.20
        - Code re-write
        - Add FBX Action under cursor position
        - Fixed UI in Linux
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil

import flame
from lib.pyflame_lib_import_camera import *

#-------------------------------------
# [Main Script]
#-------------------------------------

SCRIPT_NAME = 'Import Camera'
SCRIPT_VERSION = 'v4.16.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class ImportCamera():

    def __init__(self, selection, scene_type=''):

        pyflame.print_title(f'{SCRIPT_NAME}: {scene_type.upper()} {SCRIPT_VERSION}')

        # Check script path, if not correct, display error message and end script
        if not pyflame.verify_script_install():
            return

        # Load config file
        self.settings = self.load_config()

        self.flame_version = pyflame.get_flame_version()

        self.existing_batch_nodes = [str(node.name)[1:-1] for node in flame.batch.nodes]

        # Open setup if no scene type is provided, otherwise import camera
        if not scene_type:
            self.setup()
        else:
            self.get_cursor_position(selection)
            self.get_camera(scene_type)

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
                'camera_path': '/opt/Autodesk',
                'scene_scale': 100,
                'import_type': 'Action Objects',
                'consolidate_geometry': False, # Alembic setting only
                'create_object_group': False, # Alembic setting only

                'linearize_keyframes': True,
                'objects_models': True,
                'objects_lights': True,
                'objects_cameras': True,
                'objects_mesh_animations': True,
                'objects_normals': True,

                'action_node_only': True,
                'no_st_map_setup': False,
                'st_map_matchbox_setup': False,
                'st_map_node_setup': False,

                'import_method': 'Browse To Path',
                'custom_import_path': '/opt/Autodesk',
                }
            )

        return settings

    def get_cursor_position(self, selection) -> None:
        """
        Get Cursor Position
        ===================

        Get cursor current position.

        If a node is selected, the position of that node will be used.
        Otherwise, the cursor position will be used.

        Args:
        -----
            selection (list):
                List of selected nodes if any.
        """

        if selection != ():
            self.selection = selection[0]
            self.master_pos_x = self.selection.pos_x + 300
            self.master_pos_y = self.selection.pos_y
        else:
            self.selection = ''
            self.master_pos_x = flame.batch.cursor_position[0]
            self.master_pos_y = flame.batch.cursor_position[1]

    def get_camera(self, scene_type) -> None:
        """
        Get Camera
        ==========

        Opens a Flame file browser to select either an FBX or Alembic file based on the provided scene_type.
        If the selection is successful, it opens the main window. Otherwise, it removes temporary files and ends the script.
        If the import method is set to 'Use Tokenized Path', it resolves the path tokens.

        Args:
        -----
            scene_type (str):
                The type of scene file to select. Must be either 'fbx' or 'abc'.
        """

        self.create_temp_folder()

        # Open file browser to select FBX or Alembic file
        if scene_type == 'fbx':
            self.camera_type = 'FBX'
        elif scene_type == 'abc':
            self.camera_type = 'Alembic'

        # If 'Use Tokenized Path' is selected, resolve path tokens, otherwise use path in settings
        if self.settings.import_method == 'Use Tokenized Path':
            import_path = pyflame.resolve_path_tokens(self.settings.custom_import_path, flame.batch)
        else:
            import_path = self.settings.camera_path

        # Open file browser to select FBX or Alembic file
        pyflame.print(f'Select {self.camera_type} file...')

        self.camera_file_path = pyflame.file_browser(
            path=import_path,
            title=f'Load {self.camera_type}',
            extension=[scene_type],
            )

        # If fbx/abc scene is selected open import options window, otherwise remove temp folder and script is done
        if self.camera_file_path:
            pyflame.print(f'{self.camera_type} file selected: {self.camera_file_path}')
            self.main_window()
        else:
            self.remove_temp_folder()
            pyflame.print('Import Cancelled.', text_color=TextColor.RED)

    def create_temp_folder(self) -> None:
        """
        Create Temp Folder
        ==================

        Create temporary folder to store action node setups.
        """

        self.temp_folder = os.path.join(SCRIPT_PATH, 'temp')
        if not os.path.exists(self.temp_folder):
            os.mkdir(self.temp_folder)
            pyflame.print('Temp folder created.', text_color=TextColor.GREEN)

    def remove_temp_folder(self) -> None:
        """
        Remove Temp Folder
        ==================

        Remove temporary folder.
        """

        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder, ignore_errors=True)
            pyflame.print('Temp folder removed.', text_color=TextColor.GREEN)

    def action_node_find_line(self, action_file, text) -> int:
        """
        Action Node Find Line
        =====================

        Find line in saved action node file containing text.

        Args:
        -----
            action_file (str):
                Action node lines.

            text (str):
                The text to search for in the file.

        Returns:
        --------
            num (int):
                The line number containing the text.
        """

        for num, line in enumerate(action_file, 1):
            if text in line:
                return num

    def action_node_find_next_line(self, action_file, text, text_line_num) -> int:
        """
        Action Node Find Next Line
        ==========================

        Find the line number of the next occurrence of the specified text in the action file after the given line number.

        Args:
        -----
            action_file (file):
                Action node lines.

            text (str):
                The text to search for.

            text_line_num (int):
                The line number to start the search at.

        Returns:
        --------
            num (int):
                The line number of the next occurrence of the specified text in the action lines.
        """

        for num, line in enumerate(action_file, 1):
            if num > text_line_num:
                if text in line:
                    return num

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
            path=self.camera_file_path.rsplit('/', 1)[0],
            title='Load Undistort ST Map (EXR)',
            extension=['exr'],
            )

        # If undistort map not selected, return
        if not undistort_map_path:
            return None, None

        # Make sure map selected is undistort, if not, start over
        if not re.search('undistort', undistort_map_path, re.I):
            PyFlameMessageWindow(
                message=('Undistort map not selected.\n\n"undistort" should be in selected file name.'),
                message_type=MessageType.ERROR,
                parent=None,
                )
            return None, None

        # Search for undistort folder for redistort map
        pyflame.print('Searching for ST Redistort map...')

        for root, dirs, files in os.walk(undistort_map_path.rsplit('/', 1)[0]):
            for f in files:
                if not f.startswith('.'):
                    if re.search('redistort', f, re.I):
                        redistort_map_path = os.path.join(root, f)
                        pyflame.print('ST Redistort map found.', text_color=TextColor.GREEN)
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
                        'Redistort map not selected.\n\n'
                        '"redistort" should be in selected file name.'
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

        pyflame.print('ST Maps imported.', text_color=TextColor.GREEN)

        return undistort_map, redistort_map

    #-------------------------------------

    def create_camera_action(self) -> bool:
        """
        Create Camera Action
        ====================

        Create action and load FBX or Alembic camera scene

        Returns:
        --------
            bool: True - Camera imported successfully.
        """

        def make_keyframes_linear() -> None:
            """
            Linearize action camera keyframes.
            """

            pyflame.print('Setting camera keyframes to linear.')

            # List of channels to change to linear extrapolation
            channel_list = [
                'Channel position/x',
                'Channel position/y',
                'Channel position/z',
                'Channel rotation/x',
                'Channel rotation/y',
                'Channel rotation/z',
                'Channel scale/x',
                'Channel scale/y',
                'Channel scale/z'
                ]

            # Save actiom node setup
            action_name = str(self.camera_action.name)[1:-1]
            action_save_path = os.path.join(self.temp_folder, action_name + '.action')
            self.camera_action.save_node_setup(action_save_path)

            # Read in action node
            action_file = open(action_save_path, 'r')
            action_contents = action_file.readlines()
            action_file.close()

            # Find new camera line
            new_camera_line = self.action_node_find_line(action_contents, 'Node CameraStereo') - 1

            # Set channel extrapolation from constant to linear
            for channel in channel_list:
                extrapolation_line = self.action_node_find_next_line(action_contents, channel, new_camera_line)
                action_contents[extrapolation_line] = action_contents[extrapolation_line].replace('constant', 'linear')

            # Find 'End' line for new camera node
            for i in range(new_camera_line, len(action_contents)):
                if action_contents[i].rstrip() == 'End':
                    end_line_index = i
                    break

            # Loop through the range from new_camera_line to end_line_index to find 'CurveOrder' and set to CurveOrder linear
            for i in range(new_camera_line, end_line_index + 1):
                # Check if 'CurveOrder' is in the line
                if 'CurveOrder' in action_contents[i]:
                    # Identify leading whitespace and preserve it
                    leading_whitespace = action_contents[i][:len(action_contents[i]) - len(action_contents[i].lstrip())]
                    # Set the entire line to "CurveOrder linear" with preserved leading whitespace
                    action_contents[i] = leading_whitespace + "CurveOrder linear"

            # Write action node back to file
            action_file = open(action_save_path, 'w')
            contents = ''.join(action_contents)
            action_file.write(contents)
            action_file.close()

            # Load new action setup into action node
            self.camera_action.load_node_setup(action_save_path)

            pyflame.print('Camera keyframes set to linear.')

        # Set Action node name, iterate name if already exists
        self.camera_action_node_name = pyflame.generate_unique_node_names(
            node_names=['imported_camera'],
            existing_node_names=self.existing_batch_nodes
            )[0]

        # Create Action node
        self.camera_action = flame.batch.create_node('Action')
        self.camera_action.name = self.camera_action_node_name
        self.camera_action.collapsed = False

        # Load saved action setup for extra outputs
        self.camera_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/camera_action/camera_action.flare.action'))

        # Position Action node
        # If exisiting node selected position Action node next to node and connect to node
        # If nothing selected, position Action node under cursor
        if self.selection != '':
            self.camera_action.pos_x = self.master_pos_x
            self.camera_action.pos_y = self.master_pos_y - 70
            flame.batch.connect_nodes(self.selection, 'Default', self.camera_action, 'Default')
        else:
            self.camera_action.pos_x = self.master_pos_x
            self.camera_action.pos_y = self.master_pos_y

        # Import FBX camera as either Import or Read
        if self.camera_file_path.endswith('.fbx'):
            if self.settings.import_type == 'Action Objects':
                self.camera_action.import_fbx(
                    file_path=self.camera_file_path,
                    models=self.settings.objects_models,
                    lights=self.settings.objects_lights,
                    cameras=self.settings.objects_cameras,
                    mesh_animations=self.settings.objects_mesh_animations,
                    normals=self.settings.objects_normals,
                    unit_to_pixels=int(self.settings.scene_scale), # Scene scale
                    )
            elif self.settings.import_type == 'Read File':
                self.camera_action.read_fbx(
                    file_path=self.camera_file_path,
                    models=self.settings.objects_models,
                    lights=self.settings.objects_lights,
                    cameras=self.settings.objects_cameras,
                    mesh_animations=self.settings.objects_mesh_animations,
                    normals=self.settings.objects_normals,
                    unit_to_pixels=int(self.settings.scene_scale), # Scene scale
                    )

        # Import Alembic camera as either Import or Read
        elif self.camera_file_path.endswith('.abc'):
            if self.settings.import_type == 'Action Objects':
                self.camera_action.import_abc(
                    file_path=self.camera_file_path,
                    consolidate_geometry=self.settings.consolidate_geometry,
                    create_object_group=self.settings.create_object_group,
                    models=self.settings.objects_models,
                    lights=self.settings.objects_lights,
                    cameras=self.settings.objects_cameras,
                    mesh_animations=self.settings.objects_mesh_animations,
                    normals=self.settings.objects_normals,
                    unit_to_pixels=int(self.settings.scene_scale), # Scene scale
                    )
            elif self.settings.import_type == 'Read File':
                self.camera_action.read_abc(
                    file_path=self.camera_file_path,
                    consolidate_geometry=self.settings.consolidate_geometry,
                    create_object_group=self.settings.create_object_group,
                    models=self.settings.objects_models,
                    lights=self.settings.objects_lights,
                    cameras=self.settings.objects_cameras,
                    mesh_animations=self.settings.objects_mesh_animations,
                    normals=self.settings.objects_normals,
                    unit_to_pixels=int(self.settings.scene_scale), # Scene scale
                    )

        # Set key frame interpolation and extrapolation to linear
        if self.settings.objects_cameras and self.settings.import_type == 'Action Objects' and self.settings.linearize_keyframes:
            make_keyframes_linear()

        pyflame.print('Camera imported.', text_color=TextColor.GREEN)

        return True

    def create_no_st_map_setup(self) -> bool:
        """
        Create No ST Map Setup
        ======================

        Create setup for doing simple patching with 3d camera.

        Returns:
        --------
            bool:
                True - Setup created successfully.
        """

        # Create Action node with imported camera.
        self.create_camera_action()

        # Make sure node names are unique in batch.
        new_node_names = pyflame.generate_unique_node_names(
            node_names=[
                'mux_in',
                'action_in',
                'action_out',
                'recomp',
                'regrain',
                'divide',
                ],
            existing_node_names=self.existing_batch_nodes
            )

        # Create nodes
        plate_in_mux = flame.batch.create_node('MUX')
        plate_in_mux.name = new_node_names[0]

        action_in_mux = flame.batch.create_node('MUX')
        action_in_mux.name = new_node_names[1]

        action_out_mux = flame.batch.create_node('MUX')
        action_out_mux.name = new_node_names[2]

        divide_comp = flame.batch.create_node('Comp')
        divide_comp.name = new_node_names[5]
        divide_comp.flame_blend_mode = 'Divide'
        divide_comp.swap_inputs = True

        recomp_action = flame.batch.create_node('Action')
        recomp_action.collapsed = True

        recomp_action.name = new_node_names[3]
        recomp_action_media = recomp_action.add_media()

        regrain = flame.batch.create_node('Regrain')
        regrain.name = new_node_names[4]

        # Position nodes in batch
        plate_in_mux.pos_x = self.master_pos_x
        plate_in_mux.pos_y = self.master_pos_y- 25

        action_in_mux.pos_x = plate_in_mux.pos_x + 450
        action_in_mux.pos_y = plate_in_mux.pos_y - 300

        self.camera_action.pos_x = action_in_mux.pos_x + 600
        self.camera_action.pos_y = action_in_mux.pos_y - 60

        action_out_mux.pos_x = self.camera_action.pos_x + 600
        action_out_mux.pos_y = self.camera_action.pos_y - 70

        divide_comp.pos_x = action_out_mux.pos_x + 220
        divide_comp.pos_y = action_out_mux.pos_y + 70

        recomp_action.pos_x = plate_in_mux.pos_x + 2150
        recomp_action.pos_y = plate_in_mux.pos_y + 20

        recomp_action_media.pos_x = recomp_action.pos_x - 30
        recomp_action_media.pos_y = recomp_action.pos_y - 440

        regrain.pos_x = recomp_action.pos_x + 300
        regrain.pos_y = recomp_action.pos_y

        # Load recomp action node setup
        recomp_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/patch_import/recomp.flare.action'))

        # Connect nodes
        if self.selection != '':
            flame.batch.connect_nodes(self.selection, 'Default', plate_in_mux, 'Input_0')

        flame.batch.connect_nodes(plate_in_mux, 'Result', action_in_mux, 'Input_0')
        flame.batch.connect_nodes(plate_in_mux, 'Result', recomp_action, 'Back')
        flame.batch.connect_nodes(action_in_mux, 'Result', self.camera_action, 'Back')
        flame.batch.connect_nodes(self.camera_action, 'Output [ Comp ]', action_out_mux, 'Input_0')
        flame.batch.connect_nodes(self.camera_action, 'Output [ Matte ]', action_out_mux, 'Matte_0')
        flame.batch.connect_nodes(recomp_action, 'Comp [ Comp ]', regrain, 'Front')
        flame.batch.connect_nodes(recomp_action, 'Comp [ Comp ]', regrain, 'Back')
        flame.batch.connect_nodes(recomp_action, 'Matte [ Matte ]', regrain, 'Matte')
        flame.batch.connect_nodes(action_out_mux, 'Result', divide_comp, 'Front')
        flame.batch.connect_nodes(action_out_mux, 'OutMatte', divide_comp, 'Back')
        flame.batch.connect_nodes(action_out_mux, 'OutMatte', recomp_action_media, 'Matte')
        flame.batch.connect_nodes(divide_comp, 'Result', recomp_action_media, 'Front')

        pyflame.print('Camera imported with No ST Map setup.', text_color=TextColor.GREEN)

        return True

    def create_st_map_matchbox_setup(self) -> bool:
        """
        Create ST Map Matchbox Setup
        ============================

        Create setup with ST Map workflow with 3d camera. Recomp over original plate at end.
        Prompt user to select undistort and redistort ST Maps.

        Uses Matchbox node for ST Map undistort and redistort.

        Returns:
        --------
            bool:
                True if setup created successfully, False otherwise.
        """

        def build_st_map_matchbox_setup(undistort_map, redistort_map) -> None:

            pyflame.print('Building ST Map Matchbox setup...')

            # Create Action node with imported camera.
            self.create_camera_action()

            # Make sure node names are unique in batch.
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
                    'comp',
                    'regrain',
                    ],
                existing_node_names=self.existing_batch_nodes
                )

            # Path to UVMap_3vis matchbox
            matchbox_path = os.path.join(SCRIPT_PATH, 'assets/matchbox/uvmap_3vis')

            # Create nodes
            # ----------- #

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

            self.camera_action.pos_x = st_map_undistort.pos_x + 600
            self.camera_action.pos_y = st_map_undistort.pos_y - 60

            mux = flame.batch.create_node('MUX')
            mux.name = new_node_names[3]
            mux.pos_x = self.camera_action.pos_x + 600
            mux.pos_y = self.camera_action.pos_y - 65

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

            comp_action = flame.batch.create_node('Action')
            comp_action.name = new_node_names[8]
            comp_action.collapsed = True
            comp_action.pos_x = plate_in_mux.pos_x + 2750
            comp_action.pos_y = self.master_pos_y + 10

            # Create redistort action media layer 1
            comp_action_in_media = comp_action.add_media()
            comp_action_in_media.pos_x = comp_action.pos_x - 40
            comp_action_in_media.pos_y = comp_action.pos_y - 490

            # Create regrain node
            regrain_node = flame.batch.create_node('Regrain')
            regrain_node.name = new_node_names[9]
            regrain_node.pos_x = comp_action.pos_x + 450
            regrain_node.pos_y = comp_action.pos_y

             # Position nodes in batch
            undistort_map.pos_x = st_map_undistort_mux.pos_x - 300
            undistort_map.pos_y = st_map_undistort_mux.pos_y + 30

            redistort_map.pos_x = st_map_redistort_mux.pos_x - 300
            redistort_map.pos_y = st_map_redistort_mux.pos_y + 30

            # Edit recomp action node
            comp_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/st_map_node_action/comp.action'))

            # Connect nodes
            if self.selection != '':
                flame.batch.connect_nodes(self.selection, 'Default', plate_in_mux, 'Input_0')

            flame.batch.connect_nodes(plate_in_mux, 'Result', st_map_undistort, 'Input 1')
            flame.batch.connect_nodes(plate_in_mux, 'Result', comp_action, 'Back')
            flame.batch.connect_nodes(st_map_undistort_mux, 'Result', st_map_undistort, 'Input 2')
            flame.batch.connect_nodes(st_map_undistort, 'Result', self.camera_action, 'Back')
            flame.batch.connect_nodes(undistort_map, 'Default', st_map_undistort_mux, 'Input_0')

            flame.batch.connect_nodes(self.camera_action, 'Output [ Comp ]', mux, 'Input_0')
            flame.batch.connect_nodes(self.camera_action, 'Output [ Matte ]', mux, 'Matte_0')
            flame.batch.connect_nodes(st_map_redistort, 'Result', divide_comp, 'Front')
            flame.batch.connect_nodes(st_map_redistort_matte, 'Result', divide_comp, 'Back')

            flame.batch.connect_nodes(mux, 'Result', st_map_redistort, 'Input 1')
            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort, 'Input 2')
            flame.batch.connect_nodes(redistort_map, 'Default', st_map_redistort_mux, 'Input_0')
            flame.batch.connect_nodes(mux, 'OutMatte', st_map_redistort_matte, 'Input 1')
            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort_matte, 'Input 2')

            flame.batch.connect_nodes(divide_comp, 'Result', comp_action_in_media, 'Front')
            flame.batch.connect_nodes(st_map_redistort_matte, 'Result',  comp_action_in_media, 'Matte')

            flame.batch.connect_nodes(comp_action, 'Comp [ Comp ]', regrain_node, 'Front')
            flame.batch.connect_nodes(comp_action, 'Comp [ Comp ]', regrain_node, 'Back')
            flame.batch.connect_nodes(comp_action, 'Matte [ Matte ]', regrain_node, 'Matte')

            pyflame.print('Camera imported with ST Map Matchbox setup.', text_color=TextColor.GREEN)

        # Load st maps
        undistort_map, redistort_map = self.get_st_maps()

        # Build st map setup if ST Maps have be selected, otherwise end script.
        if undistort_map and redistort_map:
            build_st_map_matchbox_setup(undistort_map, redistort_map)
            return True
        else:
            pyflame.print('ST Map import cancelled.', text_color=TextColor.RED)
            self.window.show()
            return False

    def create_st_map_node_setup(self) -> bool:
        """
        Create ST Map Node Setup
        ========================

        Create setup with ST Map workflow with 3d camera. Recomp over original plate at end.
        Prompts user to select undistort and redistort ST Maps.

        Uses ST Map node for ST Map undistort and redistort. Flame 2025+ only.

        Returns:
        --------
            bool:
                True if setup created successfully, False otherwise.
        """

        def build_st_map_node_setup(undistort_map, redistort_map) -> None:

            pyflame.print('Building ST Map Node setup...')

            # Create Action node with imported camera.
            self.create_camera_action()

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
                    'comp',
                    'regrain',
                    ],
                existing_node_names=self.existing_batch_nodes
                )

            # Create nodes
            # ----------- #

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

            self.camera_action.pos_x = st_map_undistort.pos_x + 600
            self.camera_action.pos_y = st_map_undistort.pos_y - 60

            mux = flame.batch.create_node('MUX')
            mux.name = new_node_names[3]
            mux.pos_x = self.camera_action.pos_x + 600
            mux.pos_y = self.camera_action.pos_y - 65

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

            comp_action = flame.batch.create_node('Action')
            comp_action.name = new_node_names[7]
            comp_action.collapsed = True
            comp_action.pos_x = plate_in_mux.pos_x + 2750
            comp_action.pos_y = self.master_pos_y + 10

            # Create redistort action media layer 1
            comp_action_in_media = comp_action.add_media()
            comp_action_in_media.pos_x = comp_action.pos_x - 40
            comp_action_in_media.pos_y = comp_action.pos_y - 430

            # Create regrain node
            regrain_node = flame.batch.create_node('Regrain')
            regrain_node.name = new_node_names[8]
            regrain_node.pos_x = comp_action.pos_x + 450
            regrain_node.pos_y = comp_action.pos_y

             # Position nodes in batch
            undistort_map.pos_x = st_map_undistort_mux.pos_x - 300
            undistort_map.pos_y = st_map_undistort_mux.pos_y + 30

            redistort_map.pos_x = st_map_redistort_mux.pos_x - 300
            redistort_map.pos_y = st_map_redistort_mux.pos_y + 30

            # Edit recomp action node
            comp_action.load_node_setup(os.path.join(SCRIPT_PATH, 'assets/action_nodes/st_map_node_action/comp.action'))

            # Connect nodes
            if self.selection != '':
                flame.batch.connect_nodes(self.selection, 'Default', plate_in_mux, 'Input_0')

            flame.batch.connect_nodes(plate_in_mux, 'Result', st_map_undistort, 'Front')
            flame.batch.connect_nodes(plate_in_mux, 'Result', comp_action, 'Back')
            flame.batch.connect_nodes(st_map_undistort_mux, 'Result', st_map_undistort, 'STMap')
            flame.batch.connect_nodes(st_map_undistort, 'Result', self.camera_action, 'Back')
            flame.batch.connect_nodes(undistort_map, 'Default', st_map_undistort_mux, 'Input_0')

            flame.batch.connect_nodes(self.camera_action, 'Output [ Comp ]', mux, 'Input_0')
            flame.batch.connect_nodes(self.camera_action, 'Output [ Matte ]', mux, 'Matte_0')
            flame.batch.connect_nodes(st_map_redistort, 'Result', divide_comp, 'Front')
            flame.batch.connect_nodes(st_map_redistort, 'OutMatte', divide_comp, 'Back')
            flame.batch.connect_nodes(mux, 'Result', st_map_redistort, 'Front')

            flame.batch.connect_nodes(st_map_redistort_mux, 'Result', st_map_redistort, 'STMap')
            flame.batch.connect_nodes(redistort_map, 'Default', st_map_redistort_mux, 'Input_0')
            flame.batch.connect_nodes(mux, 'OutMatte', st_map_redistort, 'Matte')

            flame.batch.connect_nodes(divide_comp, 'Result', comp_action_in_media, 'Front')
            flame.batch.connect_nodes(st_map_redistort, 'OutMatte',  comp_action_in_media, 'Matte')

            flame.batch.connect_nodes(comp_action, 'Comp [ Comp ]', regrain_node, 'Front')
            flame.batch.connect_nodes(comp_action, 'Comp [ Comp ]', regrain_node, 'Back')
            flame.batch.connect_nodes(comp_action, 'Matte [ Matte ]', regrain_node, 'Matte')

            pyflame.print('Camera imported with ST Map node setup.', text_color=TextColor.GREEN)

        # Load st maps
        undistort_map, redistort_map = self.get_st_maps()

        # Build st map setup if ST Maps have be selected, otherwise end script.
        if undistort_map and redistort_map:
            build_st_map_node_setup(undistort_map, redistort_map)
            return True
        else:
            pyflame.print('ST Map import cancelled.', text_color=TextColor.RED)
            self.window.show()
            return False

    #-------------------------------------

    def main_window(self):

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings to config file.
            """

            self.settings.save_config(
                config_values={
                    'camera_path': self.camera_file_path,
                    'scene_scale': self.scale_slider.value,
                    'import_type': self.import_type_menu.text,
                    'linearize_keyframes': self.linearize_keyframes_push_button.checked,
                    'consolidate_geometry': self.consolidate_geometry_push_button.checked, # Alembic setting only
                    'create_object_group': self.create_object_group_push_button.checked, # Alembic setting only

                    'objects_models': self.objects_models_push_button.checked,
                    'objects_lights': self.objects_lights_push_button.checked,
                    'objects_cameras': self.objects_cameras_push_button.checked,
                    'objects_mesh_animations': self.objects_mesh_animations_push_button.checked,
                    'objects_normals': self.objects_normals_push_button.checked,

                    'action_node_only': self.action_node_only_push_button.checked,
                    'no_st_map_setup': self.no_st_map_push_button.checked,
                    'st_map_matchbox_setup': self.st_map_matchbox_setup_button.checked,
                    'st_map_node_setup': self.st_map_node_setup_button.checked,
                    }
                )

        def load() -> None:
            """
            Load
            ====

            Saves settings and creates camera setup based on selected options then closes window and deletes temp folder.

            Nodes are created based on selected options in main window.
            """

            save_config() # Save settings

            self.window.hide() # Hide window while loading

            # Create nodes based on selected options in main window.
            if self.action_node_only_push_button.checked:
                camera_loaded = self.create_camera_action()
            elif self.no_st_map_push_button.checked:
                camera_loaded = self.create_no_st_map_setup()
            elif self.st_map_matchbox_setup_button.checked:
                if self.selection == '':
                    confirm_import = PyFlameMessageWindow(
                        message='For ST Map to be properly applied, be sure to have the background clip or node with background resolution selected when importing.\n\nContinue with import?',
                        message_type=MessageType.WARNING,
                        title='ST Map Camera Import',
                        parent=None,
                        )
                    if not confirm_import.confirmed:
                        return
                camera_loaded = self.create_st_map_matchbox_setup()
            elif self.st_map_node_setup_button.checked:
                if self.selection == '':
                    confirm_import = PyFlameMessageWindow(
                        message='For ST Map to be properly applied, be sure to have the background clip or node with background resolution selected when importing.\n\nContinue with import?',
                        message_type=MessageType.WARNING,
                        title='ST Map Camera Import',
                        parent=None,
                        )
                    if not confirm_import.confirmed:
                        return
                camera_loaded = self.create_st_map_node_setup()

            if camera_loaded:
                self.window.close() # Close window
                self.remove_temp_folder() # Delete temp folder
                pyflame.print(f'{self.camera_type} imported.', text_color=TextColor.GREEN)

        def cancel() -> None:
            """
            Cancel
            ======

            Cancels import.

            Remove temp folder and close window.
            """

            self.remove_temp_folder()
            self.window.close()

        def toggle_alembic_buttons() -> None:
            """
            Toggle Alembic Buttons
            ======================

            Toggle Alembic buttons based on Consolidate Geometry button.

            If camera type is FBX, disable both buttons.
            If camera type is Alembic, enable Create Object Group button if Consolidate Geometry button is checked.
            """

            if self.consolidate_geometry_push_button.checked:
                self.create_object_group_push_button.enabled = True
            else:
                self.create_object_group_push_button.enabled = False

        def toggle_import_type() -> None:
            """
            Toggle Import Type
            ==================

            Toggle Action Node buttons based on Import Type.
            """

            if self.import_type_menu.text == 'Action Objects' and self.camera_type == 'FBX':
                self.linearize_keyframes_push_button.enabled = True
                self.consolidate_geometry_push_button.enabled = False
                self.create_object_group_push_button.enabled = False

            elif self.import_type_menu.text == 'Action Objects' and self.camera_type == 'Alembic':
                self.linearize_keyframes_push_button.enabled = True
                self.consolidate_geometry_push_button.enabled = True
                if self.consolidate_geometry_push_button.checked:
                    self.create_object_group_push_button.enabled = True
                else:
                    self.create_object_group_push_button.enabled = False

            elif self.import_type_menu.text == 'Read File' and self.camera_type == 'FBX':
                self.linearize_keyframes_push_button.enabled = False
                self.consolidate_geometry_push_button.enabled = False
                self.create_object_group_push_button.enabled = False

            elif self.import_type_menu.text == 'Read File' and self.camera_type == 'Alembic':
                self.linearize_keyframes_push_button.enabled = False
                self.consolidate_geometry_push_button.enabled = False
                self.create_object_group_push_button.enabled = False

        def st_map_node_check() :
            """
            ST Map Node Check
            =================

            Check for ST Map node - available only in Flame 2025 and later.
            """

            if self.flame_version < 2025.0:
                self.st_map_node_setup_button.enabled = False
                self.st_map_node_setup_button.setChecked(False)
                self.st_map_node_setup_button.setToolTip('ST Map node is only available in Flame 2025 and later.')

        self.window = PyFlameWindow(
            title=f'Import {self.camera_type} Camera <small>{SCRIPT_VERSION}',
            return_pressed=load,
            escape_pressed=cancel,
            grid_layout_columns=5,
            grid_layout_rows=8,
            grid_layout_adjust_column_widths={2: 40},
            parent=None,
            )

        # Labels
        self.action_node_label = PyFlameLabel(
            text='Action Node',
            style=Style.UNDERLINE,
            )
        self.scene_scale_label = PyFlameLabel(
            text='Scene Scale',
            )
        self.import_type_label = PyFlameLabel(
            text='Import Type',
            )
        self.objects_label = PyFlameLabel(
            text='Load Objects',
            style=Style.UNDERLINE,
            )
        self.create_label = PyFlameLabel(
            text='Create Nodes',
            style=Style.UNDERLINE,
            )

        # Slider
        self.scale_slider = PyFlameSlider(
            min_value=1,
            max_value=1000,
            start_value=self.settings.scene_scale,
            )

        # Menu
        self.import_type_menu = PyFlameMenu(
            text=self.settings.import_type,
            menu_options=[
                'Action Objects',
                'Read File',
                ],
            connect=toggle_import_type,
            )

        # Push Buttons
        self.action_node_only_push_button = PyFlamePushButton(
            text='Action Node Only',
            checked=self.settings.action_node_only,
            tooltip='Create camera action node only.',
            )
        self.no_st_map_push_button = PyFlamePushButton(
            text='No ST Map Setup',
            checked=self.settings.no_st_map_setup,
            tooltip='Create batch setup with no ST Map.',
            )
        self.st_map_matchbox_setup_button = PyFlamePushButton(
            text='ST Map Matchbox Setup',
            checked=self.settings.st_map_matchbox_setup,
            tooltip='Create batch setup with ST Map Matchbox.',
            )
        self.st_map_node_setup_button = PyFlamePushButton(
            text='ST Map Node Setup',
            checked=self.settings.st_map_node_setup,
            tooltip='Create batch setup with ST Map Node.',
            )
        self.create_button_group = PyFlameButtonGroup(
            button_group=[
                self.action_node_only_push_button,
                self.no_st_map_push_button,
                self.st_map_matchbox_setup_button,
                self.st_map_node_setup_button,
                ],
            )

        self.linearize_keyframes_push_button = PyFlamePushButton(
            text='Linearize Keyframes',
            checked=self.settings.linearize_keyframes,
            tooltip='Sets keyframe interpolation to Linear. Helps with motion blur on first and last frames.',
            )

        self.consolidate_geometry_push_button = PyFlamePushButton(
            text='Consolidate Geometry',
            checked=self.settings.consolidate_geometry,
            connect=toggle_alembic_buttons,
            )
        self.create_object_group_push_button = PyFlamePushButton(
            text='Create Object Group',
            checked=self.settings.create_object_group,
            )
        self.alembic_button_group = PyFlameButtonGroup(
            button_group=[
                self.consolidate_geometry_push_button,
                self.create_object_group_push_button,
                ],
            set_exclusive=False,
            )

        self.objects_cameras_push_button = PyFlamePushButton(
            text='Cameras',
            checked=self.settings.objects_cameras,
            )
        self.objects_models_push_button = PyFlamePushButton(
            text='Models',
            checked=self.settings.objects_models,
            )
        self.objects_lights_push_button = PyFlamePushButton(
            text='Lights',
            checked=self.settings.objects_lights,
            )
        self.objects_mesh_animations_push_button = PyFlamePushButton(
            text='Mesh Animations',
            checked=self.settings.objects_mesh_animations,
            )
        self.objects_normals_push_button = PyFlamePushButton(
            text='Normals',
            checked=self.settings.objects_normals,
            )

        # Buttons
        self.load_button = PyFlameButton(
            text='Load',
            connect=load,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=cancel,
            )

        toggle_alembic_buttons() # Disable Alembic only buttons if camera type is FBX.
        toggle_import_type() # Toggle buttons based on Import Type.
        st_map_node_check() # Check for ST Map node - available only in Flame 2025 and later.

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.action_node_label, 0, 0, 1, 2)

        self.window.grid_layout.addWidget(self.scene_scale_label, 1, 0)
        self.window.grid_layout.addWidget(self.import_type_label, 2, 0)

        self.window.grid_layout.addWidget(self.scale_slider, 1, 1)
        self.window.grid_layout.addWidget(self.import_type_menu, 2, 1)
        self.window.grid_layout.addWidget(self.linearize_keyframes_push_button, 3, 1)
        self.window.grid_layout.addWidget(self.consolidate_geometry_push_button, 4, 1)
        self.window.grid_layout.addWidget(self.create_object_group_push_button, 5, 1)

        self.window.grid_layout.addWidget(self.objects_label, 0, 3)
        self.window.grid_layout.addWidget(self.objects_cameras_push_button, 1, 3)
        self.window.grid_layout.addWidget(self.objects_models_push_button, 2, 3)
        self.window.grid_layout.addWidget(self.objects_lights_push_button, 3, 3)
        self.window.grid_layout.addWidget(self.objects_mesh_animations_push_button, 4, 3)
        self.window.grid_layout.addWidget(self.objects_normals_push_button, 5, 3)

        self.window.grid_layout.addWidget(self.create_label, 0, 4)
        self.window.grid_layout.addWidget(self.action_node_only_push_button, 1, 4)
        self.window.grid_layout.addWidget(self.no_st_map_push_button, 2, 4)
        self.window.grid_layout.addWidget(self.st_map_matchbox_setup_button, 3, 4)
        self.window.grid_layout.addWidget(self.st_map_node_setup_button, 4, 4)

        self.window.grid_layout.addWidget(self.cancel_button, 7, 3)
        self.window.grid_layout.addWidget(self.load_button, 7, 4)

    #-------------------------------------

    def setup(self):
        """
        Setup
        =====

        Setup window to select import method.
        Import Destinations can either be selected by opening a browser window for each import or automated with a custom tokenized import path.
        """

        def toggle_custom_path() -> None:
            """
            Toggle Custom Path
            ==================

            Toggle custom path entry based on import method.
            """

            if self.import_method_menu.text == 'Browse To Path':
                self.custom_import_path_label.enabled = False
                self.custom_import_path_entry.enabled = False
                self.custom_import_path_token_menu.enabled = False
                self.browse_button.enabled = False
            else:
                self.custom_import_path_label.enabled = True
                self.custom_import_path_entry.enabled = True
                self.custom_import_path_token_menu.enabled = True
                self.browse_button.enabled = True
                self.custom_import_path_entry.set_focus()

        def browse():
            """
            Browse
            ======

            Browse to select custom import path. If path is selected, set path in custom import path entry.
            """

            browse_path = pyflame.file_browser(
                title='Select Directory',
                path=self.custom_import_path_entry.text,
                select_directory=True,
                window_to_hide=setup_window,
                )

            if browse_path:
                self.custom_import_path_entry.setText(browse_path)

        def save():
            """
            Save
            ====

            Save settings to config file and close setup window.
            """

            if self.import_method_menu.text == 'Use Custom Path' and not self.custom_import_path_entry.text:
                PyFlameMessageWindow(
                    message='Custom Import Path: Enter path before saving.',
                    message_type=MessageType.ERROR,
                    parent=setup_window,
                    )
                return

            self.settings.save_config(
                config_values={
                    'import_method': self.import_method_menu.text,
                    'custom_import_path': self.custom_import_path_entry.text,
                    }
                )

            setup_window.close()

        def cancel():
            """
            Cancel
            ======

            Close setup window.
            """

            setup_window.close()

        setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            return_pressed=save,
            grid_layout_columns=6,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.import_path_label = PyFlameLabel(
            text='Import Method',
            )
        self.custom_import_path_label = PyFlameLabel(
            text='Tokenized Import Path',
            )

        # Entry
        self.custom_import_path_entry = PyFlameEntry(
            text=self.settings.custom_import_path,
            )

        # Token Menu
        self.custom_import_path_token_menu = PyFlameTokenMenu(
            text='Add Token',
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                'Sequence Name': '<SeqName>',
                'SEQUENCE NAME': '<SEQNAME>',
                'Shot Name': '<ShotName>',
                },
            token_dest=self.custom_import_path_entry,
            )

        # Menu
        self.import_method_menu = PyFlameMenu(
            text=self.settings.import_method,
            menu_options=[
                'Browse To Path',
                'Use Tokenized Path',
                ],
            connect=toggle_custom_path,
            )

        # Buttons
        self.browse_button = PyFlameButton(
            text='Browse',
            connect=browse
            )
        self.save_button = PyFlameButton(
            text='Save',
            connect=save,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=cancel,
            )

        # Toggle UI
        toggle_custom_path()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        setup_window.grid_layout.addWidget(self.import_path_label, 0, 0)
        setup_window.grid_layout.addWidget(self.import_method_menu, 0, 1)
        setup_window.grid_layout.addWidget(self.custom_import_path_label, 1, 0)
        setup_window.grid_layout.addWidget(self.custom_import_path_entry, 1, 1, 1, 3)
        setup_window.grid_layout.addWidget(self.custom_import_path_token_menu, 1, 4)
        setup_window.grid_layout.addWidget(self.browse_button, 1, 5)

        setup_window.grid_layout.addWidget(self.cancel_button, 3, 4)
        setup_window.grid_layout.addWidget(self.save_button, 3, 5)

#-------------------------------------

def import_fbx(selection):

    ImportCamera(selection, 'fbx')

def import_abc(selection):

    ImportCamera(selection, 'abc')

def setup(selection):

    ImportCamera(selection)

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Import...',
            'actions': [
                {
                    'name': 'Import FBX Camera',
                    'order': 1,
                    'execute': import_fbx,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Import Alembic Camera',
                    'order': 2,
                    'execute': import_abc,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

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
                    'name': 'Import Camera Setup',
                    'execute': setup,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
