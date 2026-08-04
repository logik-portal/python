'''
Script Name: csv to markers
Script Version: 1.7
Flame Version: 2023.2
Originally Created by: Andy Milkis
Updated by: Jacob Silberman-Baron, John Geehreng
Updated On: 03.01.24

Description:
    Imports a CSV file exported from frame.io and adds markers to a clip in flame. There is no need to modify the CSV downloaded from FrameIO.

Menus:
    Right click on a clip in the Media Panel
        UC FrameIO -> CSV -> Timeline Markers
        Navigate to the CSV file and the script will automatically add markers

    Or, right click on a segment in the timeline to add segment markers
        UC FrameIO -> CSV -> Segment Markers
        Navigate to the CSV file and the script will automatically add markers

    Works for Flame 2023.2 and onward

Updates:
Script Version 1.7 (03.01.24 JG)
    - Use 'Timecode Source In' instead of 'Timecode In'
Script Version 1.6 (02.12.24 JG)
    - Rewrite to be able to use commas and ignore empty rows
Script Version 1.5 (12.03.23 JG)
    - Updates for PySide6 (Flame 2025)
Script Version 1.4 (01.11.23 JG)
    - Added Marker Durations. Added names to be "Commenter: Name of person who made the comment"
    - Uses "Timecode Source" instead of "Timecode In" for search and uses "Frame" for placing markers.
Script Version: 1.3 (11.07.22 JG)
    - Added Flame 2023.1 Browser option, 2023.2 Print to Console message if it can't find the "Timecode In" header, Timeline Segment scopes,
        minimumVersion of 2022 scopes, CSV File Filters, and default path of ~/Downloads
Script Version: 1.2 (7.11.22 JS-B)
    - Removed the CSVFileSelector Object and replaced it with a generic QFileDialog

'''

# ------------- IMPORTS------------------#
import ast
import os
import flame
import csv
from flame import PyTime
from os.path import expanduser

# ------------- MAIN SCRIPT------------------#
    
def remove_quotes(string):
    """Remove matching quotes from the ends of a string."""
    if not string:
        return ""

    string = string.strip()
    if len(string) >= 2 and string[0] == "'" and string[-1] == "'":
        return remove_quotes(string[1:-1])
    if len(string) >= 2 and string[0] == '"' and string[-1] == '"':
        return remove_quotes(string[1:-1])
    return string


def _resolve_csv_path():
    """Return the CSV path selected in the Flame browser."""
    selection = getattr(flame.browser, "selection", None)

    if isinstance(selection, str):
        try:
            parsed = ast.literal_eval(selection)
            if isinstance(parsed, (list, tuple)) and parsed:
                selection = parsed[0]
        except Exception:
            selection = selection.strip("[]'\" ")

    if isinstance(selection, (list, tuple)):
        selection = selection[0] if selection else ""

    return expanduser(selection) if selection else ""

def add_markers(selection):
   
    # Modify Default Path for File Browsers:
    default_path = expanduser("~/Downloads")
    
    #Asks the user to select a file
    flame.browser.show(
        title = "Select CSV",
        select_directory = False,
        multi_selection = False,
        extension = "csv",
        default_path = default_path)
    csv_path = _resolve_csv_path()

    if not csv_path:
        return

    if not os.path.isfile(csv_path):
        flame.messages.show_in_console(f"CSV file not found: {csv_path}", "warning", 5)
        return

    # Requrited Header names of the column containing Timecodes and Comments
    tc_header = 'Timecode Source In'
    comment_header = 'Comment'

    try:
        with open(csv_path, mode='r', newline='') as file:
            csv_reader = csv.DictReader(file)
            fieldnames = csv_reader.fieldnames or []
            if tc_header not in fieldnames or comment_header not in fieldnames:
                message = "'Timecode Source In' and/or 'Comment' header not found in CSV file."
                print(message)
                flame.messages.show_in_console(message, "warning", 5)
                return

            rows = [
                row for row in csv_reader
                if (row.get(tc_header) and row.get(comment_header))
            ]
    except Exception as exc:
        flame.messages.show_in_console(f"Failed to read CSV: {exc}", "warning", 5)
        return

    if not rows:
        flame.messages.show_in_console("No usable marker rows found in CSV.", "info", 5)
        return
    
    for flame_obj in selection:
        if isinstance(flame_obj, (flame.PyClip, flame.PySequence, flame.PySegment)):
            if isinstance(flame_obj, flame.PySegment):
                parent_sequence = flame_obj.parent.parent.parent
                frame_rate = parent_sequence.frame_rate
            elif isinstance(flame_obj, flame.PyClip):
                frame_rate = flame_obj.frame_rate
            else:
                continue

        if isinstance(flame_obj, (flame.PyClip, flame.PySequence, flame.PySegment)):
            for row in rows:
                timecode = row.get(tc_header, "").strip()
                comment = remove_quotes(row.get(comment_header, ""))
                duration_raw = row.get('Duration') or '0'
                commenter = remove_quotes(row.get('Commenter') or 'Unknown')

                try:
                    marker_time = PyTime(timecode, frame_rate)
                except Exception:
                    continue

                try:
                    m = flame_obj.create_marker(marker_time)
                    m.colour = (0.2, 0.0, 0.0)
                    try:
                        duration_frames = int(float(duration_raw))
                    except (ValueError, TypeError):
                        duration_frames = 0
                    if duration_frames > 0:
                        m.duration = duration_frames
                    m.comment = comment
                    m.name = f"Commenter: {commenter}" 
                except Exception:
                    continue

# ----------- SCOPES ------------------#
                
def scope_clip(selection):
    for item in selection:
        if isinstance(item, (flame.PyClip, flame.PySegment)):
            return True
    return False

def scope_segment(selection):
    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False

# ----------- MAIN MENU------------------#

def get_timeline_custom_ui_actions():

    return [
        {
            "name": "UC FrameIO",
            "separator": "above",
            "actions": [
                {
                    "name": "CSV -> Segment Markers",
                    "isVisible": scope_segment,
                    "minimumVersion": '2023.2',
                    'order ': 1,
                    "separator": 'above',
                    "execute": add_markers
                }
            ]
        }

     ]


def get_media_panel_custom_ui_actions():

    return [
        {
            "name": "UC FrameIO",
            "actions": [
                {
                    "name": "CSV -> Timeline Markers",
                    "isVisible": scope_clip,
                    "minimumVersion": '2023.2',
                    "separator": 'above',
                    "execute": add_markers
                }
            ]
        }

     ]
