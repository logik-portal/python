"""
Script Name: Build Resolution List
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 12.20.24
Update Date: 10.22.25

Script Type: MediaPanel

Description:

    The goal is to be able to select multiple xmls that have been run through the fix premiere xmls script at various resolutions using a json file.

Menu:

    Media Panel -> UC Timelines -> Build Resolution List

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0   10.22.25
        - Use flame.projects.current_project.project_folder to determine where to save json's

    v0.2   12.27.24
        - Added aspect ratio to json file

    v0.1   12.20.24
        - Initial release.
"""

#-------------------------------------#
# Imports

import flame
import re
import os
import traceback
import json
from pathlib import Path

#-------------------------------------#
# Main Script

FOLDER_NAME = 'UC Timelines'
SCRIPT_NAME = 'Build Resolution List'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class BuildResolutionList():

    def __init__(self, selection) -> None:

        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')

        self.project_name = flame.projects.current_project.name
        self.simple_flame_version = flame.get_version().split('.')[0]

        if self.simple_flame_version <= '2026':
            full_project_path = flame.projects.current_project.project_folder
            self.project_tmp_path = re.sub(r"^/hosts/[^/]+", "", full_project_path) + '/tmp'
            self.action_path = f"{self.project_tmp_path}/auto_xml_temp.action"
            self.res_file_location = Path(f"{self.project_tmp_path}/auto_scale_resolution_list.json")
            self.scale_compensator_res_file_location = Path(f"{self.project_tmp_path}/scale_compensator_res_list.json")
        else:
            self.action_path = f"/opt/Autodesk/project/{self.project_name}/tmp/auto_xml_temp.action"
            self.res_file_location = Path(f"/opt/Autodesk/project/{self.project_name}/tmp/auto_scale_resolution_list.json")
            self.scale_compensator_res_file_location = Path(f"/opt/Autodesk/project/{self.project_name}/tmp/scale_compensator_res_list.json")
        # print (f"Action Path: {self.action_path}")
        # print (f"Resolution List Path: {self.res_file_location}")

        # Define selection
        self.selection = selection
        self.resolution_list()

    def catch_exception(method):
        def wrapper(self,*args,**kwargs):
            try:
                return method(self,*args,**kwargs)
            except:
                traceback.print_exc()
        return wrapper

    @catch_exception
    def resolution_list(self):

        project_name = flame.projects.current_project.name

        self.resolution_list = []

        # Build the dictionary
        data = {"items": []}
        count = 0
        # Build list based on all the linked segments
        for item in self.selection:
            if isinstance(item, flame.PySequence):
                for version in item.versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            resolution = f"{segment.source_width}x{segment.source_height}"
                            if resolution not in self.resolution_list:
                                count += 1
                                id = f"resolution_{count:03}"
                                self.resolution_list.append(resolution)
                                data["items"].append({
                                    "id": id,
                                    "resolution": resolution,
                                    "aspect_ratio": round(float(segment.source_ratio), 3)
                                })

            elif isinstance(item, flame.PyClip):
                resolution = f"{item.width}x{item.height}"
                if resolution not in self.resolution_list:
                    count += 1
                    id = f"resolution_{count:03}"
                    self.resolution_list.append(resolution)
                    data["items"].append({
                                    "id": id,
                                    "resolution": resolution,
                                    "aspect_ratio": round(float(item.ratio), 3)
                                })

        # # Specify json file path
        # res_file_location = Path(f"/opt/Autodesk/project/{project_name}/tmp/auto_scale_resolution_list.json")
        # scale_compensator_res_file_location = Path(f"/opt/Autodesk/project/{project_name}/tmp/scale_compensator_res_list.json")


        # Ensure the directory exists
        self.res_file_location.parent.mkdir(parents=True, exist_ok=True)

        # Write the list to the JSON file
        with self.res_file_location.open("w") as json_file:
            json.dump(self.resolution_list, json_file, indent=4)
        with self.scale_compensator_res_file_location.open("w") as json_file:
            json.dump(data, json_file, indent=4)

        # Show Success Dialog with path
        flame.messages.show_in_dialog(
            title="Success",
            message=f"Resolution lists exported to: {self.res_file_location.parent}",
            type="info",
            buttons=["Ok"],
            cancel_button="Cancel"
        )
        print(f"List export to: {self.res_file_location}", '\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Build Resolution List Complete', '=========]\n')


#-------------------------------------#
# Scopes

def scope_sequence_or_clip(selection):
    for item in selection:
        if isinstance(item, (flame.PySequence, flame.PyClip)):
            return True
    return False


#-------------------------------------#
# Flame Menus

def get_media_panel_custom_ui_actions():

    return [

        {
            'name': FOLDER_NAME,
            # 'hierarchy': [],
            # 'order': 2,
            'actions': [
               {
                    'name': SCRIPT_NAME,
                    'execute': BuildResolutionList,
                    'isVisible': scope_sequence_or_clip,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]