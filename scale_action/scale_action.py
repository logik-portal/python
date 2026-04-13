"""
Script Name: scale_action
Script Version: 0.1
Flame Version: 2025
Written by: Ted Stanley, with help from Claude
Creation Date: 04.07.26

Custom Action Type: MediaPanel, Timeline

Description:
    For all selected Actions, scales the top Axis (axis1 or axis_L1) by a user-supplied value

Menus:
    Action Tools -> Scale Action
"""

import flame
import re
import sys
import traceback
import os
from pyflame_lib_action_tools import *


FOLDER_NAME = 'Action Tools'
SCRIPT_NAME = 'Scale Action'
SCRIPT_VERSION = 'v.1'


TARGET_AXIS_NAMES = {"axis_L1", "axis1"}
SCALING_CHANNELS = {"scaling/x", "scaling/y", "scaling/z"}

def scope_sequence(selection):
    return any(isinstance(item, flame.PySequence) for item in selection)

def scope_segment(selection):
    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False

def get_media_panel_custom_ui_actions():
    return [{
        'name': FOLDER_NAME,
        'actions': [{
            'name': SCRIPT_NAME,
            'execute': ScaleAction,
            'isVisible': scope_sequence,
            'minimumVersion': '2025'
        }]
    }]

def get_timeline_custom_ui_actions():
    return [
        {
            'name': FOLDER_NAME,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'execute': ScaleAction,
                    'isVisible': scope_segment,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

class ScaleAction():
    def __init__(self, selection) -> None:
        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        self.selection = selection
        self.create_main_window()
        #self.BeginActionScale(selection)

    def catch_exception(method):                                                                                                                                              
        def wrapper(self, *args, **kwargs):                                                                                                                                     
            try:                                                                                                                                                              
                return method(self, *args, **kwargs)                                                                                                                            
            except:                                                                                                                                                           
                traceback.print_exc()                                                                                                                                         
        return wrapper                                                                                                                                                        
        
    @catch_exception

    def create_main_window(self) -> None:
        """
        create_main_window
        ==================

        Generated window for script.
        """

        def do_something() -> None:
            self.main_window.close()
            print('Do something...')

        def close_window() -> None:
            self.main_window.close()

        # ------------------------------------------------------------------------------
        # [Start Window Build]
        # ------------------------------------------------------------------------------

        self.main_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            parent=None,
            return_pressed=self.BeginActionScale,
            escape_pressed=close_window,
            grid_layout_columns=2,
            grid_layout_rows=2,
            window_margins=15,
            )

        # Labels
        self.label_1 = PyFlameLabel(
            text='Scale Value:',
            style=Style.NORMAL,
            align=Align.CENTER,
            )

        # Entries
        self.scale_multiplier = PyFlameEntry(
            text='',
            placeholder_text='1.0',
            read_only=False,
            tooltip='',
            )

        # Buttons
        self.cancel = PyFlameButton(
            text='Cancel',
            color=Color.GRAY,
            tooltip='',
            connect=self.main_window.close,
            # connect=on_cancel_click,  # TODO: Uncomment and implement callback
            )
        self.Scale_Actions = PyFlameButton(
            text='Scale Actions',
            color=Color.GRAY,
            tooltip='',
            connect=self.BeginActionScale
            # connect=on_Scale_Actions_click,  # TODO: Uncomment and implement callback
            )
        
        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.main_window.grid_layout.addWidget(self.label_1, 0, 0)
        self.main_window.grid_layout.addWidget(self.scale_multiplier, 0, 1)
        self.main_window.grid_layout.addWidget(self.Scale_Actions, 1, 0)
        self.main_window.grid_layout.addWidget(self.cancel, 1, 1)

        self.scale_multiplier.set_focus()

        # ------------------------------------------------------------------------------
        # [End Window Build]
        # ------------------------------------------------------------------------------

    def parse_scale_multiplier(sefl, text: str) -> float | None:
        try:
            value = float(text.strip())
        except ValueError:
            return None

        if value != value:          # NaN check (float('nan') != float('nan'))
            return None
        if value == float('inf') or value == float('-inf'):
            return None
        if value == 0:              # zero scale probably doesn't make sense
            return None
        
        value = abs(value)

        return value
    
    def get_segments(self, selection):
        segments = []
        for item in selection:
            if isinstance(item, flame.PySegment):
                segments.append(item)
            elif isinstance(item, flame.PySequence):
                for version in item.versions:
                    for track in version.tracks:
                        segments.extend(track.segments)
        return segments

    def BeginActionScale(self):
        project_name = flame.project.current_project.name
        selection = self.selection
        
        # Setup temporary action path
        action_path = f"/opt/Autodesk/project/{project_name}/tmp/auto_action_temp.action"
        #print(action_path)
        if not os.path.exists(os.path.dirname(action_path)):
            action_path = '/var/tmp/auto_action_temp.action'
        
        #scale_multiplier = float(self.scale_multiplier.text)

        scale_multiplier = self.parse_scale_multiplier(self.scale_multiplier.text)
        if scale_multiplier is None:
            print("Invalid scale value entered")
            return

        # Process all selected segments
        """"
        for item in selection:
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        for tlfx in segment.effects:
                            if tlfx.type == 'Action':
                                print(f"Processing Action effect in {segment.name}")
                                # Save the action setup
                                tlfx.save_setup(action_path)
                                print(action_path)
                                #scale_multiplier = .5
                                self.scale_action_file(action_path, action_path, scale_multiplier)
                                # Delete and recreate action
                                flame.delete(tlfx)
                                action_fx = segment.create_effect('Action')
                                action_fx.load_setup(action_path)
                                #segment.colour = (50, 50, 50)  # Mark as processed
        
        """
        for segment in self.get_segments(selection):
            for tlfx in segment.effects:
                if tlfx.type == 'Action':
                    print(f"Processing Action effect in {segment.name}")
                    # Save the action setup
                    tlfx.save_setup(action_path)
                    print(action_path)
                    self.scale_action_file(action_path, action_path, scale_multiplier)
                    # Delete and recreate action
                    flame.delete(tlfx)
                    action_fx = segment.create_effect('Action')
                    action_fx.load_setup(action_path)


        self.main_window.close()
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')

    def scale_action_file(self, input_path: str, output_path: str, scale_multiplier: float) -> None:
        input_path += "/_action.action"
        output_path += "/_action.action"
        with open(input_path, "r") as f:
            lines = f.readlines()

        output_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

        # Detect start of a Node Axis block
            if line.strip() == "Node Axis":
                node_lines = [line]
                i += 1

                # Read ahead to find the Name field
                axis_name = None
                while i < len(lines):
                    node_lines.append(lines[i])
                    name_match = re.match(r'^\s*Name\s+(\S+)', lines[i])
                    if name_match:
                        axis_name = name_match.group(1)
                        i += 1
                        break
                    i += 1

                should_scale = axis_name in TARGET_AXIS_NAMES

                # Continue reading the rest of the node block until top-level "End"
                in_specifics = False
                brace_depth = 0
                in_target_channel = False

                while i < len(lines):
                    current_line = lines[i]
                    stripped = current_line.strip()

                    # Track entry into Specifics { } block
                    if stripped == "Specifics":
                        in_specifics = True

                    if in_specifics:
                        if "{" in stripped:
                            brace_depth += stripped.count("{")
                        if "}" in stripped:
                            brace_depth -= stripped.count("}")
                            if brace_depth <= 0:
                                in_specifics = False
                                in_target_channel = False

                    # Detect which channel we're entering
                    channel_match = re.match(r'^\s*Channel\s+(\S+)', current_line)
                    if channel_match:
                        channel_name = channel_match.group(1)
                        in_target_channel = should_scale and (channel_name in SCALING_CHANNELS)

                    # Reset channel context at ChannelEnd
                    if re.match(r'^\s*ChannelEnd', current_line):
                        in_target_channel = False

                    # Scale any Value line within a target channel (covers both top-level and Key values)
                    if in_target_channel:
                        value_match = re.match(r'^(\s*Value\s+)([0-9eE+\-\.]+)(\s*)$', current_line)
                        if value_match:
                            original = float(value_match.group(2))
                            scaled = original * scale_multiplier
                            current_line = f"{value_match.group(1)}{scaled:.10g}{value_match.group(3)}\n"

                    node_lines.append(current_line)

                    # Node block ends at a top-level "End" (not inside Specifics braces)
                    if stripped == "End" and not in_specifics and brace_depth == 0:
                        i += 1
                        break

                    i += 1

                output_lines.extend(node_lines)
                continue

            output_lines.append(line)
            i += 1

        with open(output_path, "w") as f:
            f.writelines(output_lines)

        print(f"Done. Written to: {output_path}")
        