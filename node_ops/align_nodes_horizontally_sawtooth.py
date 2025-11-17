'''
Script Name: Node Ops | Align Nodes Horizontally Sawtooth
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Michael Vaglienty & Andrew Miller
Creation Date: 07.26.24
Update Date: 07.26.24

Usage: Batch Desktop

Description:

    Automatically aligns the selected nodes horizontally with sawtooth pattern.
    Intention is to make it easier to read node titles that are very long.

Note:

    This script uses Michael Vaglienty's PyFlame Library script.

    Script Name: pyflame_lib_script_template.py
    Version: 3.2.0

    For usage with my script, I renamed his script to:

    pyflame_lib_align_nodes_horizontally_sawtooth.py

    His latest version can be downloaded here:

    https://www.dropbox.com/sh/xirh0yo3d27upy8/AADtzjcPMh4xIMbBlNahNmbxa?dl=0

    From the following folder: _SCRIPT_TEMPLATE

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select two or more nodes and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Align Nodes Horizontally Sawtooth

    -- The leftmost node sets the starting X and Y coordinates for horizontal alignment.

    -- The rightmost node determines the maximum distance from the leftmost node.

    -- This script will align the selected nodes horizontally with a sawtooth pattern.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame
from pyflame_lib_align_nodes_horizontally_sawtooth import PyFlameWindow, PyFlameButton, PyFlameSlider, PyFlameLabel, Color
from PySide6 import QtWidgets

# ------------------------------------------------------------------------------

def get_batch_custom_ui_actions():

    def align_horizontal_sawtooth(selection) :

        nodes = [node for node in selection]

        # If script finds a compass in selection, terminate script.
        for node in nodes:
            if node.type == "Compass":
                return

        # Filters for selected nodes
        if len(selection) > 1 :
            for item in selection:
                if isinstance(item, flame.PyNode):
                    return True
            return False

    # GUI related code
    def gui_window(selection):

        def close_gui_window():
            userOffset=Slider.get_value()
            Window.close()
            batch_prep(selection,userOffset)

        def cancel_gui_window():
            Window.close()

        grid_layout = QtWidgets.QGridLayout()

        Window = PyFlameWindow(width = 400, height = 150, title = "Horizontal Sawtooth Align")

        # Declare 175 as default value for vertical offset
        Window.add_layout(grid_layout)
        Slider=PyFlameSlider(start_value=175, min_value=0,max_value=500)
        Button=PyFlameButton(text="Offset Height", connect=close_gui_window)
        ButtonCancel=PyFlameButton(text="Cancel", color=Color.GRAY, connect=cancel_gui_window)

        Lable=PyFlameLabel(text="Vertical Height")

     # Slidergrid
        grid_layout.addWidget(Lable, 0, 0)
        grid_layout.addWidget(Slider, 0, 1)

        grid_layout.addWidget(ButtonCancel, 6, 0)
        grid_layout.addWidget(Button, 6, 1)

        Window.setLayout(grid_layout)

        Window.show()

        return Window

    def batch_prep(selection,userOffset):

        nodes = selection

        # Dictionary Comprehension
        node_lookup = {node.pos_x.get_value(): node for node in nodes}

        # Creates a list of the dictionary keys and then reverse sorts them
        x_positions = list(node_lookup.keys())
        x_positions.sort()

        # Store the topmost and bottommost nodes
        left_node = node_lookup[x_positions[0]]
        right_node = node_lookup[x_positions[-1]]

        # Do some math to figure out node spacing
        spaces = len(x_positions) - 1

        x_delta = left_node.pos_x.get_value() - right_node.pos_x.get_value()
        spacer = int(x_delta / spaces)

        # Make a new list of just the inner nodes we want to move
        sliced_positions = x_positions[1:-1]

        # Create a base value that will offset as we move more and more nodes
        offset = spacer

        for position in sliced_positions:
            node_lookup[position].pos_x = left_node.pos_x.get_value() - offset

            offset += spacer

        # Align lower nodes pos_y value to the leftmost node

        for index, position in enumerate(x_positions[1:]):
            switch = index%2
            if switch == 1:
                node_lookup[position].pos_y = left_node.pos_y
            else:
                node_lookup[position].pos_y = left_node.pos_y + userOffset

# =============================================================================

    return [
            {
            "name": "Node Ops",
            "actions": [
                {
                    "name": "Align Nodes Horizontally Sawtooth",
                    "isVisible": align_horizontal_sawtooth,
                    "execute": gui_window
                }
            ]
        }
        ]


