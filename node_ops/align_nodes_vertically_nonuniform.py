'''
Script Name: Node Ops | Align Nodes Vertically Non-Uniform
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller
Creation Date: 07.26.24
Update Date: 07.26.24

Usage: Batch Desktop

Description:

    Automatically aligns the selected nodes vertically, preserving existing spacing.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more nodes and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Align Nodes Vertically Non-Uniform

    -- The topmost node sets the starting X and Y coordinates for vertical alignment.

    -- The bottommost node determines the maximum distance from the topmost node.

    -- This script will align the selected nodes vertically, preserving existing spacing.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

def align_vertical_nonuniform(selection):

        nodes = [node for node in selection]

        # If script finds a compass in selection, terminate script.
        for node in nodes:
            if node.type == "Compass":
                return

        # Dictionary comprehension - creates a dictionary from a list
        node_lookup = {node.pos_y.get_value(): node for node in nodes}

        # Creates a list of the dictionary keys and then reverse sorts them
        y_positions = list(node_lookup.keys())
        y_positions.sort(reverse = True)

        # Store the top and bottom nodes
        top_node = node_lookup[y_positions[0]]
        bottom_node = node_lookup[y_positions[-1]]

        # Do some math to figure out node spacing
        spaces = len(y_positions) - 1

        y_delta = top_node.pos_y.get_value() - bottom_node.pos_y.get_value()
        spacer = int(y_delta / spaces)

        # Make a new list of just the inner nodes we want to move
        sliced_positions = y_positions[1:-1]

        # Create an offset value that will grow as we move more and more nodes
        offset = spacer

        # Align bottommost node pos_x value to the topmost node
        for position in y_positions[1:]:
            node_lookup[position].pos_x = top_node.pos_x

# Makes this script visible and executable only if more than one node is selected
# This script will not be visible in menu if no nodes or only one node is selected

def get_batch_custom_ui_actions():
    def scope_nodes(selection):
        if len(selection) <= 1:
            return False
        # Filters for selected nodes
        for item in selection:
            if isinstance(item, flame.PyNode):
                return True
        return False

# =============================================================================

    return [
            {
            "name": "Node Ops",
            "actions": [
                {
                    "name": "Align Nodes Vertically Non-Uniform",
                    "isVisible": scope_nodes,
                    "execute": align_vertical_nonuniform
                }
            ]
        }
        ]
