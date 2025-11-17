# Replace Render Nodes
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
Script Name: Replace Render Nodes
Script Version: 2.2.0
Flame Version: 2023.2+
Written by: Michael Vaglienty
Creation Date: 02.22.20
Update Date: 04.14.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    Use to replace all render nodes in comp when they fail to properly show up in render list.

URL:
    https://github.com/logik-portal/python/replace_render_nodes

Menus:

    Right-click in batch -> Replace Render Nodes

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.2.0 04.14.25
        - Updated to PyFlameLib 4.3.0.

    v2.1.0 09.18.23
        - Updated menus for Flame 2023.2+
        - Updated to pyflame lib 2.0.0.

    v2.0 06.03.21
        - Updated to be compatible with Flame 2022/Python 3.7
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame
from lib.pyflame_lib_replace_render_nodes import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Replace Render Nodes'
SCRIPT_VERSION = 'v2.2.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

def replace_render_nodes(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Duplicate render node and delete original
    for node in flame.batch.nodes:
        if node.type in ('Render', 'Write File'):
            new_node = node.duplicate(keep_node_connections=True)
            new_node.pos_x = node.pos_x
            new_node.pos_y = node.pos_y
            pyflame.print(f'Render Node Replaced: {str(node.name)[1:-1]}')
            node.delete()

    pyflame.print('All Render Nodes Replaced')

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_render_nodes(selection):

    render_nodes = [node for node in flame.batch.nodes if node.type in ('Render', 'Write File')]
    if render_nodes:
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
                    'name': 'Replace Render Nodes',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_render_nodes,
                    'execute': replace_render_nodes,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
