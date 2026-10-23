# Replace Render Nodes
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Replace Render Nodes
Script Version: 2.3.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 02.22.20
Update Date: 10.13.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Replace all render nodes in batch when they fail to properly show up in render list.

URL:

    https://logik-portal.com/scripts/replace_render_nodes

Menus:

    Right-click in batch -> Replace Render Nodes

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.3.1 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v2.3.0 04.02.26
        - Updated to PyFlameLib v5.3.0.

    v2.2.0 04.14.25
        - Updated to PyFlameLib 4.3.0.

    v2.1.0 09.18.23
        - Updated menus for Flame 2023.2+
        - Updated to pyflame lib 2.0.0.

    v2.0 06.03.21
        - Updated to be compatible with Flame 2022/Python 3.7
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import flame
from lib.pyflame_lib_replace_render_nodes import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Replace Render Nodes'
SCRIPT_VERSION = 'v2.3.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

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

    pyflame.print('All Render Nodes Replaced', text_color=TextColor.GREEN)

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_render_nodes(selection):

    render_nodes = [node for node in flame.batch.nodes if node.type in ('Render', 'Write File')]
    if render_nodes:
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

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
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
