"""
Script Name: Render Selected Nodes
Written by: Kieran Hanrahan

Script Version: 1.0.1
Flame Version: 2025

URL: http://github.com/khanrahan/render-selected-nodes

Creation Date: 04.06.25
Update Date: 04.06.25

Description:

    Render selected Render or Write File nodes.

Menus:

    Right-click selected nodes in the Batch schematic --> Render... -> Selected Nodes

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import flame

TITLE = 'Render Selected Nodes'
VERSION_INFO = (1, 0, 1)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

OUTPUT_NODES = (
        flame.PyRenderNode,
        flame.PyWriteFileNode,
)


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def get_nodes_bypass_status(node_types):
    """Store node object and bypass statuses.

    Args:
        node_types: A tuple of Flame node classes to filter for.

    Returns:
        A list contains tuples of the node object and its bypass status as a bool.
    """
    nodes_bypass_status = []

    for node in flame.batch.nodes:
        if isinstance(node, node_types):
            node_state = (node, node.bypass.get_value())
            nodes_bypass_status.append(node_state)

    return nodes_bypass_status


def render_selected_nodes(selection, node_types):
    """Set only selected nodes of a certain type to be active, then Render."""
    for node in flame.batch.nodes:
        if isinstance(node, node_types):
            if node in selection:
                node.bypass.set_value(False)
            else:
                node.bypass.set_value(True)

    flame.execute_shortcut('Render (Current Mode)')


def set_nodes_bypass_status(nodes_bypass_status):
    """Loop through the provided nodes and set their bypass status.

    Args:
        nodes_bypass_status: A list of tuples containing node objects and their bypass
           status stored as a bool.
    """
    for node, bypass_state in nodes_bypass_status:
        node.bypass.set_value(bypass_state)


def process_selection(selection):
    """The main function of this script."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    nodes_bypass_status = get_nodes_bypass_status(OUTPUT_NODES)
    render_selected_nodes(selection, OUTPUT_NODES)
    set_nodes_bypass_status(nodes_bypass_status)

    message('Done!')


def scope_selection(selection, objects):
    """Test if the selection only contains the specified objects."""
    return all(isinstance(item, objects) for item in selection)


def scope_output_nodes(selection):
    """Filter for only Render or Write File nodes."""
    return scope_selection(selection, OUTPUT_NODES)


def get_batch_custom_ui_actions():
    """Python hook to add custom right click menu item."""
    return [{'name': 'Render...',
             'actions': [{'name': 'Selected Nodes',
                          'isVisible': scope_output_nodes,
                          'execute': process_selection,
                          'minimumVersion': '2025.0.0.0'}]
            }]
