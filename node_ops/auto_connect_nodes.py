'''
Script Name: Node Ops | Auto Connect Nodes
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special thanks: Andrew Miller
Creation Date: 07.26.24
Update Date: 07.26.24

Usage: Batch Desktop

Note: This script is designed for dual usage. See bottom of script for multiple action types.

Description: Auto Connect Nodes

    Automatically connects two or more selected nodes from left to right.
    Regular nodes, Action Media Inputs, and Elbows are all supported.

Description: Auto Connect Multiple Inputs

    Automatically connects a source node to multiple inputs of selected nodes.
    Regular nodes, Action Media Inputs, and Elbows are all supported.

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use: Auto Connect Nodes

    -- Select two or more nodes and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Auto Connect

    -- The selected nodes will automatically be connected from left to right.

To use: Auto Connect Nodes Multiple Inputs

    -- Select two or more nodes and right-click on a node to see the Node Ops menu.

    -- From the Node Ops menu, select Auto Connect Multiple Inputs

    -- The output of the leftmost node will automatically be connected to the input
       nodes of all the selected nodes to its right. This works best when the destination
       nodes are vertically aligned.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
'''

import flame

# =============================================================================

def sort_nodes(selection):

        nodes = [node for node in selection]

        # lambda sorting accounts for nodes that have same pos_x value
        sorted_nodes = sorted(nodes, key=lambda node:node.pos_x.get_value())

        return sorted_nodes

# "Auto Connect Nodes"
# Automatically connect nodes from leftmost to rightmost node
def auto_connect_nodes(selection):

        sorted_nodes = sort_nodes(selection)

        for index in range(1,len(sorted_nodes)):
            nodeA = sorted_nodes[index-1]
            nodeB = sorted_nodes[index]
            if nodeA.type == "Elbow":
                 output_socket = "Result"
            else:
                 output_socket = "Default"
            if nodeB.type == "Elbow":
                input_socket = "Front"
            else:
                 input_socket = "Default"
            flame.batch.connect_nodes(nodeA, output_socket, nodeB, input_socket)
        return

# "Auto Connect Multiple Inputs"
# The output of the leftmost node will automatically be connected to the input
# nodes of all the selected nodes to its right. This works best when the destination
# nodes are vertically aligned.

# Note: Elbow nodes require Result, Front instead of Default, Default for connecting
def multiple_inputs(selection):

        sorted_nodes = sort_nodes(selection)

        if sorted_nodes[0].type == "Elbow":
            output_socket = "Result"
        else:
            output_socket = "Default"

        for index in range(1,len(sorted_nodes)):
            nodeB = sorted_nodes[index]
            if nodeB.type == "Elbow":
                input_socket = "Front"
            else:
                input_socket = "Default"
            flame.batch.connect_nodes(sorted_nodes[0], output_socket, nodeB, input_socket)
        return

# Makes this script visible and executable only if more than one node is selected
# This script will not be visible in menu if no nodes or only one node is selected

def get_batch_custom_ui_actions():
    def scope_nodes(selection):
        if len(selection) <= 1:
            return False
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
                    "name": "Auto Connect Nodes",
                    "isVisible": scope_nodes,
                    "execute": auto_connect_nodes
                },
                {
                    "name": "Auto Connect Multiple Inputs",
                    "isVisible": scope_nodes,
                    "execute": multiple_inputs
                }
            ]
        }
        ]
