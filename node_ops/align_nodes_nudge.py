'''
Script Name: Node Ops | Nudge
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special Thanks: Britt Ciampa for the challenge to write this. Enjoy!
Special Thanks: Andrew Miller
Creation Date: 03.01.25
Update Date: 04.10.25
Usage: Batch Desktop

Description:

    This script contains eight executable functions.

    Nudge selected nodes in Batch using the up, down, left and right arrow keys.

    Shortcut keys that I am using are:

    Min Translation (default is 10 units)
    Use this for moving selection in smaller increments.

    up:    meta + shift + up arrow key
    down:  meta + shift + down arrow key
    right: meta + shift + right arrow key
    left:  meta + shift + left arrow key

    Max Translation (default is Min Translation * 4)
    Use this for moving selection in larger increments.

    up:    control + meta + shift + up arrow key
    down:  control + meta + shift + down arrow key
    right: control + meta + shift + right arrow key
    left:  control + meta + shift + left arrow key

To use:

    -- Use the shortcut keys you've assigned, or...

    -- Select one or more node/compasses and right-click on a node to see the
       Node Ops Nudge menu.

    -- From the Node Ops Nudge menu, select a Align Nudge command.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================
# DEFINE MIN AND MAX TRANSLATION VALUES
# =============================================================================

# Minimum translation value
MIN_TRANSLATION = 10
#MIN_TRANSLATION = 20

# Maximum translation value
#MAX_TRANSLATION = MIN_TRANSLATION * 2
MAX_TRANSLATION = MIN_TRANSLATION * 4

# =============================================================================
# MIN TRANSLATION
# =============================================================================
def align_nodes_nudge_up_MIN(selection):

    # Move each node based on min_translation
    for node in selection:
        node.pos_y = node.pos_y + MIN_TRANSLATION

    return

def align_nodes_nudge_down_MIN(selection):

    # Move each node based on min_translation
    for node in selection:
        node.pos_y = node.pos_y - MIN_TRANSLATION

    return

def align_nodes_nudge_right_MIN(selection):

    # Move each node based on min_translation
    for node in selection:
        node.pos_x = node.pos_x + MIN_TRANSLATION

    return

def align_nodes_nudge_left_MIN(selection):

    # Move each node based on min_translation
    for node in selection:
        node.pos_x = node.pos_x - MIN_TRANSLATION

    return

# =============================================================================
# MAX TRANSLATION
# =============================================================================

def align_nodes_nudge_up_MAX(selection):

    # Move each node based on max_translation
    for node in selection:
        node.pos_y = node.pos_y + MAX_TRANSLATION

    return

def align_nodes_nudge_down_MAX(selection):

    # Move each node based on max_translation
    for node in selection:
        node.pos_y = node.pos_y - MAX_TRANSLATION

    return

def align_nodes_nudge_right_MAX(selection):

    # Move each node based on max_translation
    for node in selection:
        node.pos_x = node.pos_x + MAX_TRANSLATION

    return

def align_nodes_nudge_left_MAX(selection):

    # Move each node based on max_translation
    for node in selection:
        node.pos_x = node.pos_x - MAX_TRANSLATION

    return

# =============================================================================

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
            "name": "Node Ops Nudge",
            "actions": [

                # MIN TRANSLATION ---------------------------------------------

                {
                    "name": "Align Nodes Nudge Up MIN",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_up_MIN
                },
                    {
                    "name": "Align Nodes Nudge Down MIN",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_down_MIN
                },
                    {
                    "name": "Align Nodes Nudge Left MIN",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_left_MIN
                },
                    {
                    "name": "Align Nodes Nudge Right MIN",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_right_MIN
                },

                # MAX TRANSLATION ---------------------------------------------

                {
                    "name": "Align Nodes Nudge Up MAX",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_up_MAX
                },
                    {
                    "name": "Align Nodes Nudge Down MAX",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_down_MAX
                },
                    {
                    "name": "Align Nodes Nudge Left MAX",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_left_MAX
                },
                    {
                    "name": "Align Nodes Nudge Right MAX",
                    "isVisible": scope_nodes,
                    "execute": align_nodes_nudge_right_MAX
                },
            ]
        }
        ]