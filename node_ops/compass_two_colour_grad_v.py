'''
Script Name: Node Ops | Compass 2 Colour Grad Vertical
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller
Creation Date: 02.10.25
Update Date: 02.10.25

Usage: Batch Desktop

Description:

    -- Vertically colourizes the selected compasses with a gradient using two user-defined colors.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more compasses and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Compass 2 Colour Gradient Vertical

    -- The selected compasses are colourized using two user-defined colors.

    -- Scroll down to adjust the colors to your preference.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

# Note: This is block of code is currently not implemented. Feel free to experiment with it.
def rgb_gradient(float_colour_start, float_colour_end, compasses):
        """Math to calculate RGB values for graident steps. Assigns colours to compasses."""

        steps = len(compasses)
        # Calculate the difference between the RGB Float values for each channel

        r_step = (float_colour_end[0] - float_colour_start[0]) / (steps - 1)
        g_step = (float_colour_end[1] - float_colour_start[1]) / (steps - 1)
        b_step = (float_colour_end[2] - float_colour_start[2]) / (steps - 1)

        # Generate the gradient colors in a tuple

        current_colour = float_colour_start

        # We are using ,1 so that the colour is multipled by 1 instead of 0,
        # which would yield black.

        for step,compass in enumerate(compasses,1):

            compass.colour = current_colour

            r = float_colour_start[0] + r_step * step
            g = float_colour_start[1] + g_step * step
            b = float_colour_start[2] + b_step * step

            current_colour = (r, g, b)

def two_colour_gradient_vertically(selection):
    """Sorts selected compasses from top to bottom."""

    #Dictionary comprehension - creates a dictionary from a list
    node_lookup = {node.pos_y.get_value(): node for node in selection if node.type == "Compass"}

    #Creates a list of the dictionary keys and then reverse sorts them
    y_positions = list(node_lookup.keys())
    y_positions.sort(reverse = True)

    node_order = [node_lookup[position] for position in y_positions]

    return node_order

# The following is the code that gets executed in Node Ops
# Note: Colour values must be between 0.00 and 1.00
# Tip: Use a Colour Souce node in Batch (16 Bit Colour) to choose colour values

# Custom Colour Combinations

def assign_gradient_to_nodes(selection):

    # step one: order the compasses from left to right
    order_compasses = two_colour_gradient_vertically(selection)
    # step two: assign custom colours to compasses -

    # turquoise to orange
    # rgb_gradient((0.00, 0.54, 0.86),(1.00, 0.50,0.00), order_compasses)

    # dark blue to gold
    rgb_gradient((0.00, 0.094, 0.194),(0.543, 0.443, 0.189), order_compasses)


# ======= ACTIVATE RIGHT-CLICK FOR SCRIPT WHEN COMPASSES ARE SELECTED =========

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
                    "name": "Compass 2 Colour Gradient Vertical",
                    "isVisible": scope_nodes,
                    "execute": assign_gradient_to_nodes
                }
            ]
        }
        ]
