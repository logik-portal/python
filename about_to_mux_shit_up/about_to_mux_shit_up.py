"""
Script Name: About to Mux Shit Up
Script Version: 1.0.1
Flame Version: 2022
Written By: Kieran Hanrahan
Creation Date: 02.22.24
Update Date: 02.28.24

Description:

    Attach Mux nodes to the output sockets of the selected Clip nodes in Batch.

    URL: http://github.com/khanrahan/about-to-mux-shit-up

Menus:

    Right-click selected Clip nodes in the Batch schematic -> Create... -> About to Mux Shit Up

To install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""

import flame

TITLE = 'About to Mux Shit Up'
VERSION_INFO = (1, 0, 1)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = '{} v{}'.format(TITLE, VERSION)
MESSAGE_PREFIX = '[PYTHON]'

NODE_SPACING = (400, 140)
OFFSET_THUMBNAIL = 48


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def create_socket_pairs(sockets):
    """Pair up corresponding RGB & Alpha sockets.

    Args:
        sockets: List of strings for the name of each output socket.

    Returns:
        A list containing tuples of each output socket and its corresponding alpha.
        None is used if alpha not present.
    """
    result = []

    for index, socket in enumerate(sockets):
        # socket is an alpha that was already paired in results?
        if len(result) >= 1 and socket == result[-1][1]:
            continue
        # following socket is the corresponding alpha?
        if index + 1 < len(sockets) and sockets[index + 1] == socket + '_alpha':
            pair = (socket, sockets[index + 1])
        # no corresponding alpha
        else:
            pair = (socket, None)
        result.append(pair)
    return result


def calculate_positions(anchor_node, quantity, spacing, offset, axis_x=True,
                        axis_y=True):
    """Generate new positions that are evely distributed based on the anchor node.

    Args:
        anchor_node (Flame PyNode object): Node to be used for starting position.
        quantity (int): The intended number of new positions to evenly distribute.
        spacing (tuple): Spacing between positions on X & Y axis as integers.
        offset (int): Offset node position by this amount if expanded.
        axis_x (bool, optional): Generate distributed positions for the x axis?
        axis_y (bool, optional): Generate disributed positions for the y axis?

    Returns:
        A list of tuples containing integers representing the X & Y positions for the
        Mux nodes.  Flame only takes integers for PyNode.set_pos_x or PyNode.set_pos_y
    """
    result = []

    anchor_position = (anchor_node.pos_x.get_value(), anchor_node.pos_y.get_value())
    distance_horizontal = (quantity - 1) * spacing[0]
    distance_vertical = (quantity - 1) * spacing[1]

    start_position = [anchor_position[0] + int(distance_horizontal / 2),
                      anchor_position[1] + int(distance_vertical / 2)]

    if not anchor_node.collapsed.get_value():
        start_position[1] = start_position[1] - offset

    for index in range(quantity):
        x = start_position[0] - index * spacing[0] if axis_x else anchor_position[0]
        y = start_position[1] - index * spacing[1] if axis_y else anchor_position[1]

        position = (x, y)
        result.append(position)

    return result


def connect_downstream_mux(node):
    """Connect a downstream Mux node to each output socket.

    Args:
        node (Flame PyNode onject): Node with output sockets to connect Mux to.
    """
    socket_pairs = create_socket_pairs(node.output_sockets)
    new_positions = calculate_positions(
            node, len(socket_pairs), NODE_SPACING, OFFSET_THUMBNAIL, axis_x=False)

    for index, (socket, alpha) in enumerate(socket_pairs):
        mux = flame.batch.create_node('Mux')
        mux.pos_x.set_value(new_positions[index][0] + NODE_SPACING[0])
        mux.pos_y.set_value(new_positions[index][1])
        flame.batch.connect_nodes(node, socket, mux, 'Input_0')

        if alpha:
            flame.batch.connect_nodes(node, alpha, mux, 'Matte_0')


def mux_shit_up(selection):
    """Process all selected nodes."""
    message(TITLE_VERSION)
    message('Script called from {}'.format(__file__))

    for node in selection:
        connect_downstream_mux(node)
    message('Done!')


def scope_clip_node(selection):
    """Filter for only PyClipNode objects."""
    return all(isinstance(item, flame.PyClipNode) for item in selection)


def get_batch_custom_ui_actions():
    """Python hook to add custom item to right click menu in Batch."""
    return [{'name': 'Create...',
             'actions': [{'name': 'About to Mux Shit Up',
                          'isVisible': scope_clip_node,
                          'execute': mux_shit_up,
                          'minimumVersion': '2022'}]}]
