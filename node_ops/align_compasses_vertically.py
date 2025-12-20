
'''
Script Name: Node Ops | Align Compasses Vertically
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller, Fred Warren & Philippe Jean
Creation Date: 03.01.25
Update Date: 03.01.25

Usage: Batch Desktop

Description:

    Automatically aligns the selected compasses vertically with equal spacing.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more compasses and right-click on a compass to see Node Ops menu.

    -- From the Node Ops menu, select Align Compasses Vertically

    -- The topmost compass sets the starting X and Y coordinates for vertical alignment.

    -- The bottommost compass determines the maximum distance from the topmost compass.

    -- This script will align the selected compasses vertically with equal spacing.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

def align_compasses_vertically(selection):

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
        # the list_compasses against children_compasses. Ignores compasses within compasses.

        parent_compasses = [foo for foo in nodes if foo not in children_compasses]

        # ---------------------------------------------------------------------------
        # Calculate sum of all the height for the compasses

        sum_compass_heights = 0

        for compass in parent_compasses:
            sum_compass_heights += compass.height.get_value()

        # ---------------------------------------------------------------------------

        # Lambda sorting accounts for compasses that have same pos_y value
        ordered_compasses = sorted(parent_compasses, key=lambda node:node.pos_y.get_value())


        # Makes top compass the anchor
        ordered_compasses.reverse()

        # Store the top and bottom compasses
        top_compass = ordered_compasses[0]
        bottom_compass = ordered_compasses[-1]

        # Get number of compass nodes minus one to get gap count between nodes
        spaces = len(ordered_compasses) - 1

        # ---------------------------------------------------------------------------

        # Get sum for top compass pos_y plus it's height for maximum pos_y value
        # Note: Bottom left corner is 0, 0 for a compass node.
        bottom_node_posy_max = bottom_compass.pos_y.get_value() + bottom_compass.height.get_value()

        # Do math to get gap size between compass nodes
        spacer = int((bottom_node_posy_max - top_compass.pos_y.get_value() - sum_compass_heights) / spaces)

        # ---------------------------------------------------------------------------

        # Make a list of just the inner compass nodes that we want to move.
        # This ignores the top and bottom compasses.
        inner_compasses = ordered_compasses[1:-1]

        # ---------------------------------------------------------------------------

        # Move each inner compass based on offset
        # First we move the nodes, then the compasses
        for i,compass in enumerate(inner_compasses,1):

            old_position_x = compass.pos_x.get_value()
            old_position_y = compass.pos_y.get_value()

            last_node = ordered_compasses [i-1]

            new_position_x = top_compass.pos_x.get_value()
            new_position_y = last_node.pos_y.get_value() + last_node.height.get_value() + spacer

            offset_x = new_position_x - old_position_x
            offset_y = new_position_y - old_position_y

            # Child variable consists of the node contents within a compass node
            for child in commpass_dict[compass.name.get_value()]:
                 child.pos_x = child.pos_x.get_value() + offset_x
                 child.pos_y = child.pos_y.get_value() + offset_y

            compass.pos_x = new_position_x
            compass.pos_y = new_position_y

        offset = bottom_compass.pos_x.get_value() - top_compass.pos_x.get_value()

        for child in bottom_compass.nodes:
                child.pos_x = child.pos_x.get_value() - offset

        # Align bottommost compass to topmost in pos_x
        bottom_compass.pos_x = top_compass.pos_x.get_value()

# Makes this script visible and executable only if more than one compass is selected.
# This script will not be visible in menu if no compasses or only one compass is selected.

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
                    "name": "Align Compasses Vertically",
                    "isVisible": scope_nodes,
                    "execute": align_compasses_vertically
                }
            ]
        }
        ]
