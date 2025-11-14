"""
Script Name: Replace Render Nodes
Script Version: 2.2.0
Flame Version: 2023.2+
Written by: Michael Vaglienty
Creation Date: 02.22.20
Update Date: 04.14.25

Script Type: Batch

Description:

    Use to replace all render nodes in comp when they fail to properly show up in render list.

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
