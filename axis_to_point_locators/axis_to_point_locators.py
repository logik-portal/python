# Axis to Point Locators
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
Script Name: Axis to Point Locators
Script Version: 1.5.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 11.12.21
Update Date: 04.03.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Action

Description:

    Convert selected axis nodes to point locators

URL:
    https://github.com/logik-portal/python/axis_to_point_locators

Menu:

    Right-click on axis node -> Axis to Point Locator

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.5.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.4.0 12.28.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v1.3.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v1.2.2 05.17.24
        - Fixed: Point locators not in proper position.

    v1.2.1 01.15.24
        - Updated PySide.

    v1.2.0 07.29.23
        - Updated to PyFlameLib v2.0.0.

    v1.1 01.04.23:
        - Updated menu for Flame 2023.2+
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import shutil
from random import randint

import flame
from lib.pyflame_lib_axis_to_point_locators import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Axis to Point Locators'
SCRIPT_VERSION = 'v1.5.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class AxisToPointLocators(object):

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Create temp folder for saving action setup
        self.temp_folder = os.path.join(SCRIPT_PATH, 'temp_action')
        self.create_temp_folder()

        # Action variables
        self.action_node = self.get_action_node()
        self.action_node_name = str(self.action_node.name)[1:-1]
        self.save_action_path = os.path.join(self.temp_folder, self.action_node_name)
        self.action_filename = self.save_action_path + '.action'

        # Get list of axis nodes from selected nodes
        self.axis_list = [node for node in self.selection if node.type == 'Axis']

        # Get position of first selected axis
        self.first_axis = self.axis_list[0]
        self.first_axis_name = str(self.first_axis.name)[1:-1]

        # Set position of point locator in action schematic below first selected axis
        self.point_locator_pos_x = self.first_axis.pos_x
        self.point_locator_pos_y = self.first_axis.pos_y - 200

        # Create point locator from selected axis nodes
        self.convert_axis_to_point_locator()

    def create_temp_folder(self) -> None:
        """
        Create Temp Folder
        ==================

        Create temp folder for saving action setup. If temp folder already exists, delete it, then create new temp folder.
        """

        if os.path.exists(self.temp_folder):
            shutil.rmtree(self.temp_folder)

        os.makedirs(self.temp_folder)

    def convert_axis_to_point_locator(self) -> None:
        """
        Convert Axis to Point Locator
        =============================

        Convert selected axis nodes to point locators.
        """

        pyflame.print('Creating point locators from selected axis nodes...')

        # Save current action node
        action_node = self.get_action_node()
        action_node.save_node_setup(self.save_action_path)

        # Get ConcreteEnd line
        # Point locator node data to be inserted above this line
        item_line = self.find_line('ConcreteEnd')
        concrete_end_line = item_line - 1
        # print ('concrete_end_line:', concrete_end_line, '\n')

        # Get node number for point locator node
        node_number_line = self.find_line_before('Number', concrete_end_line)
        point_locator_node_number = str(int(self.get_line_value(node_number_line)) + 1)

        # Build point locator node
        point_locator_node = self.build_point_locator_insert(point_locator_node_number)

        # Read in saved action node
        edit_action = open(self.action_filename, 'r')
        contents = edit_action.read()
        edit_action.close()

        # Combine action lines with point locator insert lines
        contents_start = contents.rsplit('ConcreteEnd', 1)[0]
        contents_end = contents.rsplit('ConcreteEnd', 1)[1]

        new_action_script = contents_start + point_locator_node + '''ConcreteEnd''' + contents_end

        # Save modified action file
        new_action = open(self.action_filename, 'w')
        new_action.write(new_action_script)
        new_action.close()

        # Reload saved action node
        self.action_node.load_node_setup(self.save_action_path)

        #
        # Connect point locator to parent axis if one exists
        #

        # Get updated action node
        self.action_node = self.get_action_node()

        # Find selected axis node number
        item_line = self.find_line(self.first_axis_name)
        line_number = self.find_line_after('Number', item_line)
        item_value = self.get_line_value(line_number)
        selected_axis_number = item_value

        # Find parent of selected axis
        item_line = self.find_line(f'Child {selected_axis_number}')
        line_number = self.find_line_before('Name', item_line)
        item_value = self.get_line_value(line_number)
        parent_axis_name = item_value[:-1]

        # Connect point locator node to parent if one exists
        parent_axis = [node for node in self.action_node.nodes if node.type == 'Axis' and node.name == parent_axis_name]
        # print ('parent_axis:', parent_axis)

        if parent_axis:
            self.action_node = self.get_action_node()
            point_locator = [node for node in self.action_node.nodes if node.name == self.point_locator_name]

            self.action_node.connect_nodes(parent_axis[0], point_locator[0])

        # Remove temp action folder
        shutil.rmtree(self.temp_folder)

        pyflame.print('Point locators created from selected axis nodes.', text_color=TextColor.GREEN)

        print ('Done.\n')

    def build_point_locator_insert(self, point_locator_node_number) -> str:
        """
        Build Point Locator Insert
        ==========================

        Build point locator node insert from selected axis nodes.

        Args:
        -----
            point_locator_node_number (str):
                Point locator node number.

        Returns:
        --------
            point_locator_node (str):
                Point locator node string
        """

        random_number = randint(10, 99)
        self.point_locator_name = f'PointLocators{random_number}'

        point_locator_start = f"""Node PointCloud
    Name {self.point_locator_name}
    Number {point_locator_node_number}
    MotionPath yes
    ShadowCaster no
    ShadowReceiver no
    ShadowOnly no
    PosX {self.point_locator_pos_x}
    PosY {self.point_locator_pos_y}
    IsLocked no
    IsSoftImported no
    OutputsSize 0
    Specifics
    {{
            Colour 0.800000012 0.5 1
            DisplayMethod 1
            Radius 10
            Transparency 0
            TransformMode 0
            EnableSnap 1
            SnapTolerance 15
            Point"""

        point_locator_end = """
        CoNodeFlags
        Collapsed no
        CoNodeFlagsEnd
    }
End
"""

        # Build axis insert for each selected axis node.
        point_locator_insert = ''
        for axis in self.axis_list:
            print('    Converting:', axis.name)
            axis_insert = self.build_axis_insert(axis)
            point_locator_insert = point_locator_insert + axis_insert
        print() # Print blank line
        point_locator_insert = point_locator_insert[:-14] # Remove last occurrence of 'Point' from point_locator_insert
        point_locator_node = point_locator_start + point_locator_insert + point_locator_end # Combine point locator node data

        return point_locator_node

    def build_axis_insert(self, axis) -> str:
        """
        Build Axis Insert
        =================

        Build axis insert from selected axis node.

        Args:
        -----
            axis (object):
                Selected axis node object.

        Returns:
        --------
            axis_insert (str):
                Axis insert string.
        """

        position = eval(str(axis.position))

        axis_insert = f"""
        Channel x
            Extrapolation constant
            Value {position[0]}
            End
        Channel y
            Extrapolation constant
            Value {position[1]}
            End
        Channel z
            Extrapolation constant
            Value {position[2]}
            End
        ChannelEnd
        Point"""

        return axis_insert

    def get_action_node(self) -> object:
        """
        Get Action Node
        ===============

        Get action node from selected action node or selected media node.

        Returns:
        --------
            action_node (object):
                Action node object.
        """

        node_type = str(flame.batch.current_node.get_value().type)[1:-1]

        if node_type == 'Action Media':
            node_value = flame.batch.current_node.get_value()
            node_sockets = node_value.sockets
            output_dict = node_sockets.get('output')
            action_node_name = output_dict.get('Result')[0]
            action_node = flame.batch.get_node(action_node_name)
        else:
            action_node_name = str(flame.batch.current_node.get_value().name)[1:-1]
            action_node = flame.batch.get_node(action_node_name)

        return action_node

    def find_line(self, item) -> int:
        """
        Find Line
        =========

        Find a specific line in Action node setup file.

        Args:
        -----
            item (str):
                Item to search for in Action node setup file.

        Returns:
        --------
            item_line (int):
                Line number where item is found in Action node setup file.
        """

        with open(self.action_filename, 'r') as action_file:
            for num, line in enumerate(action_file, 1):
                if item in line:
                    item_line = num
                    return item_line

    def find_line_before(self, item, item_line_num) -> int:
        """
        Find Line Before
        ================

        Find the line before a specific line in Action node setup file

        Args:
        -----
            item (str):
                Item to search for in Action node setup file.

            item_line_num (int):
                Line number to search before.

        Returns:
        --------
            line_number (int):
                Line number where item is found in Action node setup file.
        """

        with open(self.action_filename, 'r') as action_file:
            for num, line in enumerate(action_file, 1):
                if num == item_line_num:
                    if item in line:
                        line_number = num
                        return line_number

            item_line_num = item_line_num - 1
            return self.find_line_before(item, item_line_num)

    def find_line_after(self, item, item_line_num) -> int:
        """
        Find Line After
        ===============

        Find the line after a specific line in Action node setup file

        Args:
        -----
            item (str):
                Item to search for in Action node setup file.

            item_line_num (int):
                Line number to search after.

        Returns:
        --------
            line_number (int):
                Line number where item is found in Action node setup file.
        """

        with open(self.action_filename, 'r') as action_file:
            for num, line in enumerate(action_file, 1):
                if num > item_line_num:
                    if item in line:
                        line_number = num
                        return line_number

    def get_line_value(self, line_number) -> str:
        """
        Get Line Value
        ==============

        Get the value of a specific line in Action node setup file

        Args:
        -----
            line_number (int):
                Line number to get value from.

        Returns:
        --------
            item_value (str):
                Value of line in Action node setup file.
        """

        with open(self.action_filename, 'r') as action_file:
            for num, line in enumerate(action_file, 1):
                if num == line_number:
                    item_value = line.rsplit(' ', 1)[1]
                    return item_value

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_axis(selection):

    for item in selection:
        if item.type == 'Axis':
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_action_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Axis to Point Locator',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_axis,
                    'execute': AxisToPointLocators,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
