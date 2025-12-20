# This file is only meant to be used as a docstring source for the Logik Portal.

"""
Script Name: Node Ops
Script Version: 0.1.0
Flame Version: 2025.2
Written by: Erik Borzi
Special Thanks: Andrew Miller
Creation Date: 03.01.25
Update Date: 04.10.25
   
Description:
    
    Contains the following scripts:
        
        Align Compasses Horizontally
        Align Compasses Vertically
        Align Nodes Horizontally Nonuniform
        Align Nodes Horizontally Sawtooth
        Align Nodes Horizontally
        Align Nodes Nudge
        Align Nodes Vertically Nonuniform
        Align Nodes Vertically
        Auto Compass
        Auto Connect Nodes
        Compass Two Colour Grad H Stereo
        Compass Two Colour Grad H
        Compass Two Colour Grad V

Online tutorial:

    -- https://www.youtube.com/live/0SpDr3tMdPI?feature=shared

To use:
  
    Align Compasses Horizontally

        -- Select two or more compasses and right-click on a compass to see the Node Ops menu.

        -- From the Node Ops menu, select Align Compasses Horizontally

        -- The leftmost compass sets the starting X and Y coordinates for horizontal alignment.

        -- The rightmost compass determines the maximum distance from the leftmost compass.

        -- This script will align the selected compasses horizontally with equal spacing.

    Align Compasses Vertically

        -- Select two or more compasses and right-click on a compass to see Node Ops menu.

        -- From the Node Ops menu, select Align Compasses Vertically

        -- The topmost compass sets the starting X and Y coordinates for vertical alignment.

        -- The bottommost compass determines the maximum distance from the topmost compass.

        -- This script will align the selected compasses vertically with equal spacing.

    Align Nodes Horizontally Nonuniform

        -- Select two or more nodes and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Align Nodes Horizontally Non-Uniform

        -- The leftmost node sets the starting X and Y coordinates for horizontal alignment.

        -- The rightmost node determines the maximum distance from the leftmost node.

        -- This script will align the selected nodes horizontally without equal spacing.

    Align Nodes Horizontally Sawtooth

        -- Select two or more nodes and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Align Nodes Horizontally Sawtooth

        -- The leftmost node sets the starting X and Y coordinates for horizontal alignment.

        -- The rightmost node determines the maximum distance from the leftmost node.

        -- This script will align the selected nodes horizontally with a sawtooth pattern.

    Align Nodes Horizontally
    
        -- Select two or more nodes and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Align Nodes Horizontally

        -- The leftmost node sets the starting X and Y coordinates for horizontal alignment.

        -- The rightmost node determines the maximum distance from the leftmost node.

        -- This script will align the selected nodes horizontally with equal spacing.

    Align Nodes Nudge

        -- Nudge selected nodes in Batch using the up, down, left and right arrow keys.

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

    Align Nodes Vertically Nonuniform
    
        -- Select two or more nodes and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Align Nodes Vertically Non-Uniform

        -- The topmost node sets the starting X and Y coordinates for vertical alignment.

        -- The bottommost node determines the maximum distance from the topmost node.

        -- This script will align the selected nodes vertically, preserving existing spacing.

    Align Nodes Vertically
    
        -- Select two or more nodes and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Align Nodes Vertically

        -- The topmost node sets the starting X and Y coordinates for vertical alignment.

        -- The bottommost node determines the maximum distance from the topmost node.

        -- This script will align the selected nodes vertically with equal spacing.

    Auto Compass
    
        -- Select one or more node(s) and/ or compasses and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Auto Compass

        -- The selected node(s) and/or compasses will be enclosed within a newly created compass.

    Auto Connect Nodes
    
        Auto Connect Nodes

            -- Select two or more nodes and right-click on a node to see the Node Ops menu.

            -- From the Node Ops menu, select Auto Connect

            -- The selected nodes will automatically be connected from left to right.

        Auto Connect Nodes Multiple Inputs

            -- Select two or more nodes and right-click on a node to see the Node Ops menu.

            -- From the Node Ops menu, select Auto Connect Multiple Inputs

            -- The output of the leftmost node will automatically be connected to the input
               nodes of all the selected nodes to its right. This works best when the destination
               nodes are vertically aligned.

    Compass Two Colour Grad H Stereo
    
        -- Select two or more compasses and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Compass 2 Colour Grad Horizontal Stereo

        -- The selected compasses are colourized using blue (left) and red (right).

    Compass Two Colour Grad H
    
        -- Select two or more compasses and right-click on a compass to see the Node Ops menu.

        -- From the Node Ops menu, select Compass 2 Colour Gradient Horizontal

        -- The selected compasses are colourized using two user-defined colors.

        -- Scroll down to adjust the colors to your preference.

    Compass Two Colour Grad V

        -- Select two or more compasses and right-click on a node to see the Node Ops menu.

        -- From the Node Ops menu, select Compass 2 Colour Gradient Vertical

        -- The selected compasses are colourized using two user-defined colors.

        -- Scroll down to adjust the colors to your preference.

To install:

    Copy script into /opt/Autodesk/shared/python/node_ops
"""