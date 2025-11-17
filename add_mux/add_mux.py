# Add Mux
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
Script Name: Add Mux
Script Version: 2.6.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 07.31.19
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Add regular mux node or frame locked mux to batch.

    Right-click on an existing node to add connected mux node after it.

URL:
    https://github.com/logik-portal/python/add_mux

Menus:

    Right-click in batch -> Add Mux... -> Add MUX
    Right-click in batch -> Add Mux... -> Add Freeze Frame MUX

    Right-click on node in batch -> Add Mux... -> Add MUX
    Right-click on node in batch -> Add Mux... -> Add Freeze Frame MUX

    Right-click on Mux node in batch -> Add Mux... -> Freeze Selected MUX

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.6.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v2.5.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v2.4.0 01.07.25
        - Updated to PyFlameLib v4.0.0.

    v2.3.1 01.15.24
        - Updated PySide.

    v2.3.0 07.24.23
        - Updated to pyflame lib v2.0.0.
        - Updated versioning to semantic versioning.

    v2.2 05.24.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v2.1 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v1.6 05.12.21
        - Mux node can now be added at cursor position.
        - Regular MUX can now be added.

    v1.5 02.10.20
        - Freeze existing mux at current frame.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame
from lib.pyflame_lib_add_mux import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Add Mux'
SCRIPT_VERSION = 'v2.6.0'

#-------------------------------------
# [Main Script]
#-------------------------------------

def add_mux(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    mux_node = flame.batch.create_node('MUX')
    mux_node.name = name_node('mux')

    position_mux(mux_node, selection)

    pyflame.print('MUX Node Added to Batch', text_color=TextColor.GREEN)

def add_mux_freeze(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Add MUX Freeze Frame {SCRIPT_VERSION}')

    current_frame = flame.batch.current_frame

    mux_node = flame.batch.create_node('MUX')
    mux_node.name = name_node('freeze_frame')
    mux_node.range_active = True
    mux_node.range_start = current_frame
    mux_node.range_end = current_frame
    mux_node.before_range = 'Repeat First'
    mux_node.after_range = 'Repeat Last'

    position_mux(mux_node, selection)

    pyflame.print('MUX Node Added to Batch Frozen at Current Frame', text_color=TextColor.GREEN)

def name_node(node_type, node_num=0):

    existing_node_list = []

    for item in flame.batch.nodes:
        existing_node = item.name
        existing_node_list.append(existing_node)

    node_name = 'freeze_frame' + str(node_num)
    node_name = node_type + str(node_num)

    if node_name.endswith('e0'):
        node_name = node_name[:-1]

    if node_name not in existing_node_list:
        node_name = node_name
        return node_name
    else:
        node_num = node_num + 1
        return name_node(node_type, node_num)

def position_mux(mux_node, selection):

    # If node is selected, connect mux node
    if selection:
        for item in selection:
            mux_node.pos_x = item.pos_x + 300
            mux_node.pos_y = item.pos_y
            flame.batch.connect_nodes(item, 'Default', mux_node, 'Default')

    # If no node is selected, add mux at cursor position
    else:
        cursor_pos = flame.batch.cursor_position

        mux_node.pos_x = cursor_pos[0]
        mux_node.pos_y = cursor_pos[1]

def freeze_mux_node(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Freeze MUX Node {SCRIPT_VERSION}')

    current_frame = flame.batch.current_frame

    for mux_node in selection:
        mux_node.range_active = True
        mux_node.range_start = current_frame
        mux_node.range_end = current_frame
        mux_node.before_range = 'Repeat First'
        mux_node.after_range = 'Repeat Last'

    pyflame.print('MUX Node Frozen at Current Frame', text_color=TextColor.GREEN)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_mux_node(selection):

    for item in selection:
        if item.type == 'MUX':
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Add Mux...',
            'actions': [
                {
                    'name': 'Add MUX',
                    'execute': add_mux,
                    'order': 1,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Add Freeze Frame MUX',
                    'execute': add_mux_freeze,
                    'order': 2,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Freeze Selected MUX',
                    'isVisible': scope_mux_node,
                    'execute': freeze_mux_node,
                    'order': 3,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
