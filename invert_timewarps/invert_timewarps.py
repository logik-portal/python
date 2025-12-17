"""
Script Name: Invert Timewarps
Script Version: 1.1.1
Flame Version: 2026.1
Written by: John Geehreng
Creation Date: 08.03.25
Update Date: 08.07.25

Script Type: Batch

Usage: Right click and look for Timewarp Tools -> Invert Timewarps

Description: Invert Timewarps assuming they're in Timing Mode.

To install: Copy script to whereever you keep your scripts.

Updates:
08.07.25 - v1.1.1 - Added the unique names bit
08.03.25 - v1.1.0 - Work for Speed based timewarps now too
08.03.25 - v1.0.0 - Initial Release
"""

#-------------------------------------#
# Imports

import flame

#-------------------------------------#
# Main Script

FOLDER_NAME = "Timewarp Tools"
SCRIPT_NAME = 'Invert Timewarps'
SCRIPT_VERSION = 'v1.1.1'

def get_unique_name(base_name):
                """Return a unique node name by appending a number if necessary."""
                existing_names = [node.name for node in flame.batch.nodes]
                if base_name not in existing_names:
                    return base_name

                i = 1
                while f"{base_name}_{i}" in existing_names:
                    i += 1
                return f"{base_name}_{i}"

def invert_time_warp(selection):

    for item in selection:

        if item.type == 'Timewarp':
            if item.mode == 'Timing':
                # Get batch and nodes
                current_batch = flame.batch
                current_node = item
                # Make New TW Node, set and connect it
                new_tw_node = current_batch.create_node("timewarp")
                new_tw_node.name = get_unique_name("inverted_tw")
                new_tw_node.frame_interpolation_mode = 'ML(2026)'
                new_tw_node.pos_x = current_node.pos_x + 200
                new_tw_node.pos_y = current_node.pos_y
                flame.batch.connect_nodes(current_node, "Result", new_tw_node, "Front")

                # Get frame range
                start_frame = int(str(current_batch.start_frame))
                duration = int(str(current_batch.duration))
                last_frame = start_frame + duration - 1

                # Build frame range
                frame_range = range(start_frame, last_frame + 1)

                # Step 1: Collect timing from current_node
                frame_to_timing = {}
                for frame in frame_range:
                    timing = current_node.get_timing(float(frame))
                    frame_to_timing[frame] = timing

                # Step 2: Write swapped values to new_tw_node
                for frame, timing in frame_to_timing.items():
                    new_tw_node.set_timing(timing, frame)  # At frame=timing, set value=frame

            elif item.mode == 'Speed':

                # Get batch and nodes
                current_batch = flame.batch
                current_node = item

                # Make New TW Node, set and connect it
                new_tw_node = current_batch.create_node("timewarp")
                new_tw_node.name = get_unique_name("inverted_tw")
                new_tw_node.frame_interpolation_mode = 'ML(2026)'
                new_tw_node.pos_x = current_node.pos_x + 200
                new_tw_node.pos_y = current_node.pos_y
                flame.batch.connect_nodes(current_node, "Result", new_tw_node, "Front")

                # Get frame range
                start_frame = int(str(current_batch.start_frame))
                duration = int(str(current_batch.duration))
                last_frame = start_frame + duration - 1

                # Build frame range
                frame_range = range(start_frame, last_frame + 1)

                # Step 1: Collect timing from current_node
                frame_to_timing = {}
                for frame in frame_range:
                    timing = current_node.get_speed_timing(float(frame))
                    frame_to_timing[frame] = timing

                # Step 2: Write swapped values to new_tw_node
                for frame, timing in frame_to_timing.items():
                    new_tw_node.set_timing(timing, frame)  # At frame=timing, set value=frame
        else:
            pass

#--------------------------------
# Scopes

def scope_batch_tw_node(selection):

    for item in selection:
        if item.type == 'Timewarp':
            return True
    return False

#--------------------------------
# Menu
def get_batch_custom_ui_actions():
    return [
        {
            'name': FOLDER_NAME,
            # "separator": "above",
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'isVisible': scope_batch_tw_node,
                    'execute': invert_time_warp,
                    # "separator": "below",
                    'minimumVersion': '2026.1'
                }
            ]
        }
    ]