'''
Script Name: frame io csv to markers
Script Version: 1.5
Flame Version: 2022
Originally Created by: Andy Milkis
Updated by: Jacob Silberman-Baron, John Geehreng
Updated On: 12.03.23

Description:
    Imports a CSV file exported from frame.io and adds markers to a clip in flame. There is no need to modify the CSV downloaded from FrameIO.

Menus:
    Right click on a clip in the Media Panel
        UC FrameIO -> CSV -> Timeline Markers
        Navigate to the CSV file and the script will automatically add markers

    Or, right click on a segment in the timeline to add segment markers
        UC FrameIO -> CSV -> Segment Markers
        Navigate to the CSV file and the script will automatically add markers

    Works for Flame 2022 and onward

Updates:
Script Version 1.5 (12.03.23 JG)
    - Updates for PySide6 (Flame 2025)
Script Version 1.4 (01.11.23 JG)
    - Added Marker Durations. Added names to be "Commentor: Name of person who made the comment"
    - Uses "Timecode Source" instead of "Timecode In" for search and uses "Frame" for placing markers.
Script Version: 1.3 (11.07.22 JG)
    - Added Flame 2023.1 Browser option, 2023.2 Print to Console message if it can't find the "Timecode In" header, Timeline Segment scopes,
        minimumVersion of 2022 scopes, CSV File Filters, and default path of ~/Downloads
Script Version: 1.2 (7.11.22 JS-B)
    - Removed the CSVFileSelector Object and replaced it with a generic QFileDialog

'''

# -------- IMPORTS------------------#
import flame
from os.path import expanduser
try:
    from PySide6.QtWidgets import QFileDialog
except ImportError:    
    from PySide2.QtWidgets import QFileDialog

# Temp
frame_rate = 24

def _seconds(value):
    if isinstance(value, str):  # value seems to be a timestamp
        _zip_ft = zip((3600, 60, 1, 1/frame_rate), value.split(':'))
        return sum(f * float(t) for f,t in _zip_ft)
    elif isinstance(value, (int, float)):  # frames
        return value / frame_rate
    else:
        return 0

def _timecode(seconds):
    return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
            .format(h=int(seconds/3600),
                    m=int(seconds/60%60),
                    s=int(seconds%60),
                    f=round((seconds-int(seconds))*frame_rate))

def _frames(seconds):
    return seconds * frame_rate

def timecode_to_frames(timecode, start=None):
    return _frames(_seconds(timecode) - _seconds(start))

def frames_to_timecode(frames, start=None):
    return _timecode(_seconds(frames) + _seconds(start))



def remove_quotes(string):
    #removes the quotes from the ends of a string
    # '""a""' turns into 'a'
    if string[0] == "\'" and string[-1] == "\'":
        return remove_quotes(string[1:-1])
    elif string[0] == "\"" and string[-1] == "\"":
        return remove_quotes(string[1:-1])
    else:
        return string

def scope_clip(selection):
    import flame
    for item in selection:
        if isinstance(item, (flame.PyClip, flame.PySegment)):
            return True
    return False

def scope_segment(selection):
    import flame
    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False

def add_markers(selection):
   
    # Modify Default Path for File Browsers:
    default_path = expanduser("~/Downloads")
    
    # print (default_path)

    #Asks the user to select a file
    try:
        flame.browser.show(
            title = "Select CSV",
            select_directory = False,
            multi_selection = False,
            extension = "csv",
            default_path = default_path)

        csv_path = (str(flame.browser.selection)[2:-2])
        print (csv_path)
    except:
        csv_selector = QFileDialog()
        csv_selector.setWindowTitle("Choose CSV File.")
        csv_selector.setNameFilter("CSV (*.csv)")
        csv_selector.setDirectory(default_path)
        if csv_selector.exec():
            csv_path = csv_selector.selectedFiles()[0]
            print (csv_path)
        else:
            print("No file selected")
            return

    #Add exception for not choosing a file

    with open(csv_path, 'r') as csv_file:
        csv_list = csv_file.readlines()
    headers = csv_list[0].split(",")

    print("Found and read CSV file:", csv_path)

    #Creating a dictionary from the CSV to reference
    for line in csv_list[1:]:
        line_list = line.split(",")
        #Constructs a dictionary matching the headers to info of each comment
        marker_dict = dict()
        for index, item in enumerate(line_list):
            marker_dict[headers[index]] = item

        for item in selection:
            offset_value = 0
            if isinstance(item, flame.PySegment):
                # print ("I am a segment. Selection name: ", item.name)
                parent_sequence = item.parent.parent.parent
                selection_name = parent_sequence.name
                in_point = parent_sequence.in_mark
                start_time = parent_sequence.start_time
                # print ("Parent Name: ", selection_name)
                selection_framerate = parent_sequence.frame_rate
            elif isinstance(item, flame.PyClip):
                selection_name = item.name
                in_point = item.in_mark
                start_time = item.start_time
                # print ("Selection Name: ", selection_name)
                selection_framerate = item.frame_rate
            else:
                # print('\n')
                print ("I am not a segment. Selection name: ", item.name)
                # print('\n')
                pass
            # print('\n')

            # See where the in point is:
            if 'NULL' in str(in_point):
                print("No In Point Set. ")
                
            else:
                in_point = str(in_point).replace("+", ":")
                # print ("in_point: ", in_point)
                
                start_time = str(start_time).replace("+", ":")
                # print ("start_time: ", start_time)

                in_point_frames = timecode_to_frames(in_point)
                # print ("in_point_frames: ", in_point_frames)

                start_time_frames = timecode_to_frames(start_time)
                # print ("start_time_frames: ", start_time_frames)

                if int(in_point_frames) < int(start_time_frames):
                    # print ("In point is before Start Time.")
                    # offset_value = int(in_point_frames) - int(start_time_frames)
                    # print ("In point is at frame: ", offset_value + 1)
                    offset_value = -1

                if int(in_point_frames) > int(start_time_frames):
                    # print ("In point is after Start Time.")
                    # offset_value = int(in_point_frames) - int(start_time_frames)
                    # print ("In point is at frame: ", offset_value + 1)
                    offset_value = 0

        # print ("Offset Value: ", offset_value)
        #Create markers from the dictionary
        for flame_obj in selection:
            if isinstance(flame_obj, (flame.PyClip, flame.PySequence, flame.PySegment)):

                if "Timecode Source" in marker_dict:
                    frame = int(marker_dict["Frame"])
                    duration = marker_dict["Duration"]
                    # print ("Duration: ", duration)
                    
                else:
                    print("No timecode found. The CSV needs a header that reads 'Timecode Source'.")
                    try:
                        flame.messages.show_in_console("The CSV needs a header that reads 'Timecode Source'.", "warning", 5)
                    except:
                        continue
                    return
                               
                try:
                    m = flame_obj.create_marker(frame + offset_value)
                    m.colour = (0.2, 0.0, 0.0)
                    if duration != '0':
                        m.duration = int(duration)
                    comment = remove_quotes(marker_dict["Comment"])
                    m.comment = comment
                    m.name = "Commenter: " + remove_quotes(marker_dict["Commenter"])
                    print("Sucessfully created marker at", m.location)
                    print("Comment: ", comment)
                    # print ('\n')

                except Exception as e:
                    print("Couldn't create marker because of error:", e)

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
            "name": "FrameIO",
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
