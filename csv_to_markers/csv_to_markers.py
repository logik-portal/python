"""
Script Name: CSV to Markers
Script Version: 1.3
Flame Version: 2022
Written by: Andy Milkis, Jacob Silberman-Baron, John Geehreng
Creation Date: 07.11.22
Update Date: 11.07.22

Description:

    Imports a CSV file exported from frame.io and adds markers to a clip in flame. There is no need to modify the CSV downloaded from FrameIO.

Menus:

    Right-click on a clip in the Media Panel --> Add Timeline Markers --> Select CSV File
    Right-click on a segment in the timeline --> Add Segment Markers --> Select CSV File


Updates:

v1.3 (11.07.22 JG)
    - Added Flame 2023.1 Browser option, 2023.2 Print to Console message if it can't find the "Timecode In" header, Timeline Segment scopes,
      minimumVersion of 2022 scopes, CSV File Filters, and default path of ~/Downloads
v1.2 (7.11.22 JS-B)
    - Removed the CSVFileSelector Object and replaced it with a generic QFileDialog
"""

from PySide2.QtWidgets import QFileDialog

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
    import flame
    import os, sys
    import PySide2
    from PySide2.QtWidgets import QFileDialog
    from os.path import expanduser

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


        #Create markers from the dictionary
        for flame_obj in selection:
            if isinstance(flame_obj, (flame.PyClip, flame.PySequence, flame.PySegment)):

                if "Timecode In" in marker_dict:
                    timecode = marker_dict["Timecode In"]
                else:
                    print("No timecode found. The CSV needs a header that reads 'Timecode In'.")
                    try:
                        flame.messages.show_in_console("The CSV needs a header that reads 'Timecode In'.", "warning", 5)
                    except:
                        continue
                    return

                from flame import PyTime

                #get the frame rate
                if isinstance(flame_obj, flame.PyClip):
                    frame_rate = flame_obj.frame_rate
                elif isinstance(flame_obj, flame.PySegment):
                    par = flame_obj.parent
                    while not(isinstance(par, (flame.PyClip, flame.PySequence))):
                        par = par.parent
                    frame_rate = par.frame_rate
                else:
                    print("Cannot find frame rate.")
                    return

                marker_time = PyTime(timecode, frame_rate)


                try:
                    m = flame_obj.create_marker(marker_time.frame)
                    m.duration = marker_dict["Duration"]
                    comment = remove_quotes(marker_dict["Comment"])
                    m.comment = comment
                    print("Sucessfully created marker at", m.location)

                except Exception as e:
                    print("Couldn't create marker because of error:", e)

def get_timeline_custom_ui_actions():

    return [
        {
            "name": "Add Segment Markers",
            "actions": [
                {
                    "name": "Select CSV",
                    "isVisible": scope_segment,
                    "minimumVersion": '2022',
                    "execute": add_markers
                }
            ]
        }

     ]

def get_media_panel_custom_ui_actions():

    return [
        {
            "name": "Add Timeline Markers",
            "actions": [
                {
                    "name": "Select CSV",
                    "isVisible": scope_clip,
                    "minimumVersion": '2022',
                    "execute": add_markers
                }
            ]
        }

     ]
