# Encompass Selected Nodes
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
Script Name: Encompass Selected Nodes
Script Version: 2.8.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 04.22.20
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch/Action

Description:

    Creates compass around selected nodes in batch or action.

URL:
    https://github.com/logik-portal/python/encompass_selected_nodes

Menus:

    Select nodes to encompass -> Encompass Selected Nodes

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.8.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes main window.

    v2.7.0 03.20.25
        - Updated to PyFlameLib v4.3.0.
        - Added menu to set compass color.

    v2.6.0 12.28.24
        - Fixed: Script had errors when creating compass with name that already exists.
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v2.5.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v2.4.0 01.21.24
        - Updates to PySide.

    v2.3.0 07.27.23
        - Updated to PyFlameLib v2.0.0.
        - Updated versioning to semantic versioning.

    v2.2 06.09.23
        - Compass is created when pressing enter in compass name field.

    v2.1 10.27.22
        - Window prompts for compass name when creating compass.
        - Updated right-click menu for 2023.2+.

    v2.0 05.23.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v1.1 05.10.20
        - Added ability to encompass selected action nodes.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame
from lib.pyflame_lib_encompass_selected_nodes import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Encompass Selected Nodes'
SCRIPT_VERSION = 'v2.8.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class EncompassSelectedNodes:

    def __init__(self, selection, compass_type):

        pyflame.print_title(f'{SCRIPT_NAME} - {compass_type.capitalize()} {SCRIPT_VERSION}')

        self.selection = selection

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.main_window(compass_type)

    def main_window(self, compass_type) -> None:

        def create_compass() -> None:

            existing_node_names = [str(node.name)[1:-1] for node in flame.batch.nodes]

            # Create batch/action node compass
            if compass_type == 'action':
                compass = flame.batch.current_node.get_value().encompass_nodes([node for node in self.selection])
            else:
                compass = flame.batch.encompass_nodes([node for node in self.selection])

            # Name compass
            if compass_name_entry.text != '':
                compass_name = pyflame.generate_unique_node_names([ compass_name_entry.text], existing_node_names)[0]
            else:
                compass_name = pyflame.generate_unique_node_names(['Compass'], existing_node_names)[0]

            pyflame.print(f'Compass Name: {compass_name}')

            compass.name = compass_name

            # Set compass color
            compass_color = compass_color_menu.color_value
            if compass_color != (0.0, 0.0, 0.0, 0.0):
                compass.colour=compass_color

            pyflame.print(f'Compass added around selected node(s)', text_color=TextColor.GREEN)

            window.close()

        def close_window():
            """
            Close Window
            ============

            Close main window.
            """

            window.close()

        # Create window
        window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=create_compass,
            escape_pressed=close_window,
            grid_layout_columns=3,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        compass_name_label = PyFlameLabel(
            text='Compass Name'
            )
        compass_color_label = PyFlameLabel(
            text='Compass Color'
            )

        # Entry
        compass_name_entry = PyFlameEntry(
            text='',
            )

        # Color Menu
        compass_color_menu = PyFlameColorMenu()

        # Buttons
        apply_button = PyFlameButton(
            text='Apply',
            connect=create_compass,
            color=Color.BLUE
            )
        cancel_button = PyFlameButton(
            text='Cancel',
            connect=window.close
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        window.grid_layout.addWidget(compass_name_label, 0, 0)
        window.grid_layout.addWidget(compass_name_entry, 0, 1, 1, 2)

        window.grid_layout.addWidget(compass_color_label, 1, 0)
        window.grid_layout.addWidget(compass_color_menu, 1, 1)

        window.grid_layout.addWidget(cancel_button, 3, 1)
        window.grid_layout.addWidget(apply_button, 3, 2)

        #-------------------------------------

        # Set widget focus
        compass_name_entry.setFocus()

def encompass_action_nodes(selection) -> None:

    EncompassSelectedNodes(selection, 'action')

def encompass_batch_nodes(selection) -> None:

    EncompassSelectedNodes(selection, 'batch')

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_action_node(selection):

    for n in selection:
        if isinstance(n, flame.PyCoNode):
            return True
        return False

def scope_node(selection):

    for n in selection:
        if isinstance(n, flame.PyNode):
            return True
        return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Encompass Selected Nodes',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_node,
                    'execute': encompass_batch_nodes,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_action_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Encompass Selected Nodes',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_action_node,
                    'execute': encompass_action_nodes,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
