'''
Script Name: add_automatte
Script Version: 1.0.0
Flame Version: 2026.2
Written by: John Geehreng
Creation Date: 04.17.26
Update Date:  

Description: Quickly add an automatte setup to a Gmask Tracer node in Batch.

Updates:
04.17.26 - v1.0.0 - Start
'''

# imports
import flame
import os

FOLDER_NAME = "Gmask Tools"
ACTION_NAME = "Add Automatte"
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

def add_automatte(selection):
    current_batch = flame.batch
    current = flame.batch.current_node.get_value()

    # Extract the actual values from the PyAttribute objects of the current node
    current_pos_x = current.pos_x.get_value()
    current_pos_y = current.pos_y.get_value()

    # Create and connect new Gmask Tracer node
    new_gmask_tracer_node = flame.batch.create_node("Gmask Tracer")
    new_gmask_tracer_node.load_node_setup(f"{SCRIPT_PATH}/presets/automatte.mask")
    
    # Position the new Gmask Tracer node to the right of the current node
    new_gmask_tracer_node.pos_x = current_pos_x + 200
    new_gmask_tracer_node.pos_y = current_pos_y - 75

    # Connect Selection to the Paint Node
    flame.batch.connect_nodes(current, "Default", new_gmask_tracer_node, "Front")
   

#----------scope------------------
def scope_node(selection):
    for item in selection:
        if isinstance(item, flame.PyNode):
            return True
    return False

#----------Batch Menu------------------

def get_batch_custom_ui_actions():   
    return [
         {
            "name": FOLDER_NAME,
            "actions": [
                {
                    "name": ACTION_NAME,
                    "isVisible": scope_node,
                    "minimumVersion": "2026.2.2",
                    # "order": 6,
                    # "separator": "below",
                    "execute": add_automatte
                }
            ]
        }
    ]
