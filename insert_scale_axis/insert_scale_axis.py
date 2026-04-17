#!/usr/bin/env python3
"""
Script Name: insert_scale_axis
Script Version: 0.1
Flame Version: 2025
Written by: Ted Stanley, with help from Claude
Creation Date: 04.17.26

Custom Action Type: MediaPanel, Timeline

Description:
    For all selected segments with Actions, creates a new top level Axis node with a user-supplied scale value

Menus:
    Right-click on a segment or timeline --> Action Tools -> Scale Action with Axis

Updates:
    v.1 - 04.17.26
    - Initial Release
"""

import flame
import re
import sys
import traceback
import os
from pyflame_lib_action_tools import *

FOLDER_NAME = 'Action Tools'
SCRIPT_NAME = 'Scale Action with Axis'
SCRIPT_VERSION = 'v.1'

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
            'execute': ScaleActionAxis,
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
                    'execute': ScaleActionAxis,
                    'isVisible': scope_segment,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

class ScaleActionAxis():
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
            tooltip='1.0 = 100%',
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
            tooltip='1.0 = 100%',
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

    def parse_scale_multiplier(self, text: str) -> float | None:
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
        for segment in self.get_segments(selection):
            for tlfx in segment.effects:
                if tlfx.type == 'Action':
                    print(f"Processing Action effect in {segment.name}")
                    # Save the action setup
                    tlfx.save_setup(action_path)
                    print(action_path)
                    self.insert_scale_axis(action_path, action_path, scale_multiplier)
                    # Delete and recreate action
                    flame.delete(tlfx)
                    action_fx = segment.create_effect('Action')
                    action_fx.load_setup(action_path)


        self.main_window.close()
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')


    def parse_nodes(self, lines):
        """
        Parse the file into a list of segments. Each segment is a dict:
            {
                "type":    "node" | "text",
                "lines":   [str, ...],        # raw lines of this segment
                # for "node" segments only:
                "node_type": str,             # e.g. "Axis", "Camera", "Group"
                "name":      str | None,
                "number":    int | None,
                "pos_x":     int | None,
                "pos_y":     int | None,
                "children":  [int, ...],      # Child numbers listed in this node
            }
        """
        segments = []
        i = 0

        # Header lines before the first node
        header_lines = []
        while i < len(lines):
            if re.match(r'^Node\s+\S+', lines[i].strip()):
                break
            header_lines.append(lines[i])
            i += 1

        if header_lines:
            segments.append({"type": "text", "lines": header_lines})

        # Parse node blocks
        while i < len(lines):
            line = lines[i]
            node_match = re.match(r'^Node\s+(\S+)', line.strip())
            if not node_match:
                # Non-node line between nodes (blank lines, comments, etc.)
                # Attach to previous text segment or create new one
                if segments and segments[-1]["type"] == "text":
                    segments[-1]["lines"].append(line)
                else:
                    segments.append({"type": "text", "lines": [line]})
                i += 1
                continue

            node_type = node_match.group(1)
            node_lines = [line]
            i += 1

            name = None
            number = None
            pos_x = None
            pos_y = None
            children = []
            brace_depth = 0
            in_specifics = False

            while i < len(lines):
                l = lines[i]
                stripped = l.strip()

                # Track Specifics brace depth
                if stripped == "Specifics":
                    in_specifics = True
                if in_specifics:
                    brace_depth += l.count("{") - l.count("}")
                    if brace_depth <= 0:
                        in_specifics = False
                        brace_depth = 0

                if not in_specifics:
                    m_name = re.match(r'^\s*Name\s+(\S+)', l)
                    if m_name:
                        name = m_name.group(1)

                    m_num = re.match(r'^\s*Number\s+(\d+)', l)
                    if m_num:
                        number = int(m_num.group(1))

                    m_px = re.match(r'^\s*PosX\s+(-?\d+)', l)
                    if m_px:
                        pos_x = int(m_px.group(1))

                    m_py = re.match(r'^\s*PosY\s+(-?\d+)', l)
                    if m_py:
                        pos_y = int(m_py.group(1))

                    m_child = re.match(r'^\s*Child\s+(\d+)', l)
                    if m_child:
                        children.append(int(m_child.group(1)))

                node_lines.append(l)

                # Node ends at a top-level bare "End"
                if stripped == "End" and not in_specifics:
                    i += 1
                    break

                i += 1

            segments.append({
                "type":      "node",
                "node_type": node_type,
                "name":      name,
                "number":    number,
                "pos_x":     pos_x,
                "pos_y":     pos_y,
                "children":  children,
                "lines":     node_lines,
            })

        return segments


    def find_top_axis(self, segments):
        """
        Return the segment index of the first Node Axis in the file.
        Per the Action file spec, the highest node in the hierarchy is written first.
        """
        for idx, seg in enumerate(segments):
            if seg["type"] == "node" and seg["node_type"] == "Axis":
                return idx
        return None


    def all_node_numbers(self, segments):
        """Collect all Number values already used in the file."""
        numbers = set()
        for seg in segments:
            if seg["type"] == "node" and seg["number"] is not None:
                numbers.add(seg["number"])
        return numbers


    def next_free_number(self, used_numbers):
        """Find the lowest positive integer not already used as a node Number."""
        n = 1
        while n in used_numbers:
            n += 1
        return n


    def build_new_axis_node(self, new_number, child_number, pos_x, pos_y, scale_value):
        """
        Build the text for a new Axis node that:
        - Has its own unique Number
        - Lists the original top axis as its Child
        - Is positioned just above its child (pos_y + 125)
        - Has scaling/x, scaling/y, scaling/z all set to scale_value
        - Has position/x, position/y, position/z all at 0
        - Leaves rotation, shearing, etc. at defaults
        """
        sv = f"{scale_value:.10g}"
        #name = f"scale_{int(round(scale_value * 100))}"
        name = f"scale_{int(round(scale_value ))}"
        new_pos_y = pos_y + 125

        node_text = f"""\
Node Axis
\tName {name}
\tNumber {new_number}
\tChild {child_number}
\tMotionPath no
\tShadowCaster yes
\tShadowReceiver yes
\tShadowOnly no
\tPosX {pos_x}
\tPosY {new_pos_y}
\tIsLocked no
\tIsSoftImported no
\tOutputsSize 0
\tSpecifics
\t{{
\t\tChannel lookAt
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel position/x
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel position/y
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel position/z
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel speed
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel rotation/x
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel rotation/y
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel rotation/z
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel scaling/x
\t\t\tExtrapolation constant
\t\t\tValue {sv}
\t\t\tEnd
\t\tChannel scaling/y
\t\t\tExtrapolation constant
\t\t\tValue {sv}
\t\t\tEnd
\t\tChannel scaling/z
\t\t\tExtrapolation constant
\t\t\tValue {sv}
\t\t\tEnd
\t\tChannel shearing/x
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel shearing/y
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannel shearing/z
\t\t\tExtrapolation constant
\t\t\tValue 0
\t\t\tEnd
\t\tChannelEnd
\t}}
End
"""
        return node_text


    def update_group_child(self, seg, old_child_number, new_child_number):
        """
        In a Node Group segment, replace any Child line referencing old_child_number
        with one referencing new_child_number, and insert an additional Child line
        for old_child_number if it was the only reference (the new axis parent takes
        over that slot; the old axis becomes a child of the new axis, not the group).

        Actually, per the design: the new axis IS inserted between the group and the
        old top axis. So the group should reference new_child_number instead of
        old_child_number.
        """
        new_lines = []
        for l in seg["lines"]:
            m = re.match(r'^(\s*Child\s+)(\d+)(\s*)$', l)
            if m and int(m.group(2)) == old_child_number:
                new_lines.append(f"{m.group(1)}{new_child_number}{m.group(3)}\n")
            else:
                new_lines.append(l)
        seg["lines"] = new_lines


    def insert_scale_axis(self, input_path, output_path, scale_value):

        input_path += "/_action.action"
        output_path += "/_action.action"

        with open(input_path, "r") as f:
            lines = f.readlines()

        segments = self.parse_nodes(lines)

        # Find the top-level axis
        top_idx = self.find_top_axis(segments)
        if top_idx is None:
            print("Error: No Node Axis found in the file.")
            sys.exit(1)

        top_axis = segments[top_idx]
        child_number = top_axis["number"]
        pos_x = top_axis["pos_x"] if top_axis["pos_x"] is not None else 0
        pos_y = top_axis["pos_y"] if top_axis["pos_y"] is not None else 0

        # Pick a new unique node number
        used = self.all_node_numbers(segments)
        new_number = self.next_free_number(used)

        print(f"Top-level Axis: '{top_axis['name']}' (Number {child_number})")
        new_name = f"scale_{int(round(scale_value * 100))}"
        print(f"New parent Axis: '{new_name}' (Number {new_number})")
        print(f"  PosX={pos_x}, PosY={pos_y + 125}  (child is at PosY={pos_y})")
        scale_value = scale_value * 100
        print(f"  scaling/x/y/z = {scale_value}")

        # Update any Node Group that references the old top axis as a Child
        for seg in segments:
            if seg["type"] == "node" and seg["node_type"] == "Group":
                if child_number in seg["children"]:
                    self.update_group_child(seg, child_number, new_number)
                    print(f"Updated Node Group '{seg['name']}': Child {child_number} --> Child {new_number}")

        # Build the new axis node text
        new_axis_text = self.build_new_axis_node(new_number, child_number, pos_x, pos_y, scale_value)

        # Insert the new axis node immediately before the current top axis
        new_axis_seg = {"type": "text", "lines": new_axis_text.splitlines(keepends=True)}
        segments.insert(top_idx, new_axis_seg)

        # Write output
        with open(output_path, "w") as f:
            for seg in segments:
                f.writelines(seg["lines"])

        print(f"\nDone. Written to: {output_path}")
