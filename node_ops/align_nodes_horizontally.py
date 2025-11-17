'''
Script Name: Node Ops | Align Nodes Horizontally
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller
Creation Date: 07.26.24
Update Date: 07.26.24

Usage: Batch Desktop

Description:

    Automatically aligns the selected nodes horizontally with equal spacing.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more nodes and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Align Nodes Horizontally

    -- The leftmost node sets the starting X and Y coordinates for horizontal alignment.

    -- The rightmost node determines the maximum distance from the leftmost node.

    -- This script will align the selected nodes horizontally with equal spacing.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

def align_horizontally(selection):

        nodes = [node for node in selection]

        # If script finds a compass in selection, terminate script.
        for node in nodes:
             if node.type == "Compass":
                  return

        # Dictionary comprehension - creates a dictionary from a list
        node_lookup = {node.pos_x.get_value(): node for node in nodes}

        # Creates a list of the dictionary keys and then reverse sorts them
        x_positions = list(node_lookup.keys())
        x_positions.sort(reverse = False)

        # Store the leftmost and rightmost nodes
        left_node = node_lookup[x_positions[0]]
        right_node = node_lookup[x_positions[-1]]

        # Do some math to figure out node spacing
        spaces = len(x_positions) - 1

        x_delta = left_node.pos_x.get_value() - right_node.pos_x.get_value()
        spacer = int(x_delta / spaces)

        # Make a new list of just the inner nodes we want to move
        sliced_positions = x_positions[1:-1]

        # Create an offset value that will grow as we move more and more nodes
        offset = spacer

        # Move each inner node based on that offset
        for position in sliced_positions:
            node_lookup[position].pos_x = left_node.pos_x.get_value() - offset

            offset += spacer

        # Align lower nodes pos_y value to the leftmost node
        for position in x_positions[1:]:
            node_lookup[position].pos_y = left_node.pos_y

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
                    "name": "Align Nodes Horizontally",
                    "isVisible": scope_nodes,
                    "execute": align_horizontally
                }
            ]
        }
        ]
