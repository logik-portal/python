'''
Script Name: Node Ops | Align Compasses Horizontally
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller, Fred Warren & Philippe Jean
Creation Date: 03.01.25
Update Date: 03.01.25

Usage: Batch Desktop

Description:

    Automatically aligns the selected compasses horizontally with equal spacing.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more compasses and right-click on a compass to see the Node Ops menu.

    -- From the Node Ops menu, select Align Compasses Horizontally

    -- The leftmost compass sets the starting X and Y coordinates for horizontal alignment.

    -- The rightmost compass determines the maximum distance from the leftmost compass.

    -- This script will align the selected compasses horizontally with equal spacing.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

def align_compasses_horizontally(selection):

        nodes = [node for node in selection if node.type == "Compass"]

        # ---------------------------------------------------------------------------

        # Create a list that contains the children ".nodes" and compasses that live
        # within the parent compass node.

        children_compasses = []

        # This loop will cycle through each parent compass and one by one look at all
        # the children via ".nodes" to check to see if they are compasses or not. If they
        # are children, it will add them to the list: children_compasses.

        commpass_dict = {}
        for compass in nodes:
             commpass_dict[compass.name.get_value()] = compass.nodes
             for node in compass.nodes:
                  if node.type == "Compass":
                       children_compasses.append(node)

        # This dictionary comprehension will create a new list of parent compasses by comparing
        # the list_compasses against children_compasses.

        parent_compasses = [foo for foo in nodes if foo not in children_compasses]

        # ---------------------------------------------------------------------------
        # calculate the sum of all the widths for the compasses

        sum_compass_widths = 0

        for compass in parent_compasses:
            sum_compass_widths += compass.width.get_value()

        # ---------------------------------------------------------------------------

        # Lambda sorting accounts for compasses that have same pos_x value
        ordered_nodes = sorted(parent_compasses, key=lambda node:node.pos_x.get_value())

        # Store the left and right nodes
        left_node = ordered_nodes[0]
        right_node = ordered_nodes[-1]

        # Get number of compass nodes minus one to get gap number between nodes
        spaces = len(ordered_nodes) - 1

        # ---------------------------------------------------------------------------

        # Get sum for farthest right node pos_x plus it's width for maximum pos_x value
        right_node_posx_max = right_node.pos_x.get_value() + right_node.width.get_value()

        # Do math to get gap size between compass nodes
        spacer = int((right_node_posx_max - left_node.pos_x.get_value() - sum_compass_widths) / spaces)

        # ---------------------------------------------------------------------------

        # Make a list of just the inner compass nodes that we want to move
        inner_compasses = ordered_nodes[1:-1]

        # Move each inner node based on offset
        # First we move the nodes, then the compasses
        for i,compass in enumerate(inner_compasses,1):

            old_position_x = compass.pos_x.get_value()
            old_position_y = compass.pos_y.get_value()

            last_node = ordered_nodes [i-1]

            new_position_x = last_node.pos_x.get_value() + last_node.width.get_value() + spacer
            new_position_y = left_node.pos_y.get_value()

            offset_x = new_position_x - old_position_x
            offset_y = new_position_y - old_position_y

            # Child variable consists of the node contents within a compass node
            for child in commpass_dict[compass.name.get_value()]:
                 child.pos_x = child.pos_x.get_value() + offset_x
                 child.pos_y = child.pos_y.get_value() + offset_y

            compass.pos_x = new_position_x
            compass.pos_y = new_position_y

        offset = right_node.pos_y.get_value() - left_node.pos_y.get_value()

        for child in right_node.nodes:
                child.pos_y = child.pos_y.get_value() - offset

        # Align rightmost compass to leftmost in pos_y
        right_node.pos_y = left_node.pos_y.get_value()

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
                    "name": "Align Compasses Horizontally",
                    "isVisible": scope_nodes,
                    "execute": align_compasses_horizontally
                }
            ]
        }
        ]
