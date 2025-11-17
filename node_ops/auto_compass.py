'''
Script Name: Node Ops | Auto Compass
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller
Creation Date: 02.03.25
Update Date: 02.03.25

Usage: Batch Desktop

Description:

    Automatically encompasses selected node(s) and/ or compasses with a new compass.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:

    -- Select one or more node(s) and/ or compasses and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Auto Compass

    -- The selected node(s) and/or compasses will be enclosed within a newly created compass.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

# Encompass selected nodes, then assign a custom colour to the compass.

def auto_compass(selection):

        nodes = [node for node in selection]
        ccomp = flame.batch.encompass_nodes(nodes)
        # Assign custom colour to compass - Dark Gray
        ccomp.colour = (0.083, 0.083, 0.083)


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
                    "name": "Auto Compass",
                    "isVisible": scope_nodes,
                    "execute": auto_compass
                }
            ]
        }
        ]
