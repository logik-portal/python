"""
Script Name: auto_scale_xmls
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 12.06.24
Update Date: 10.22.25

Script Type: MediaPanel

Description:

    The goal is to be able to select multiple xmls that have been run through the fix premiere xmls script at various resolutions using a json file.

Menus:

    Media Panel -> UC Timelines -> Auto Scale XML's

To install:

    Copy script into your python folder, typically /opt/Autodesk/shared/python/auto_scale_xmls or wherever you keep your scripts

Updates:

    v1.0.0 10.22.25

        use flame.projects.current_project.project_folder to determine where to save json's and action's

    v0.7 12.27.24

        customized for Uppercut

    v0.6 12.27.24

        Added Build Resolution list options

    v0.5 12.18.24

        added Track and Segment checks. made folder names more flexible

    v0.4 12.14.24

        Assumes there aren't multiple versions in the xmls
    
    v0.3 12.09.24

        Added script_path = os.path.abspath(os.path.dirname(__file__)) for centralized workflows

    v0.2 12.09.24

        Deleting the actions, creating new ones, and loading the target action seems to fix the resize/xml bug. (Lines 273 - 275)

    v0.1 12.06.24

        Inception
"""

#-------------------------------------#
# Imports

import os
import re
import flame
import traceback
import json
from pathlib import Path
from pyflame_lib_auto_scale_xmls import *

#-------------------------------------#
# Main Script

FOLDER_NAME = 'UC Timelines'
SCRIPT_NAME = 'Auto Scale XML\'s'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class AutoScaleXMLs():

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
        else:
            self.action_path = f"/opt/Autodesk/project/{self.project_name}/tmp/auto_xml_temp.action"
            self.res_file_location = Path(f"/opt/Autodesk/project/{self.project_name}/tmp/auto_scale_resolution_list.json")

        # Create/Load config file settings.
        self.load_config()

        # Define selection
        self.selection = selection
        
        # Ask what to do...
        warning_dialogue = flame.messages.show_in_dialog(
                            title = "Warning",
                            message = 'The first item in your selection must be linked.\n\nAll selected sequences have to have the same amount of Tracks and Segments. \n\nYou also need to select a sequence for each resolution in your timeline.\n\nWhat would you like to do?',
                            type = "warning",
                            buttons = ["Build Res List","Build XML's","Auto Scale"],
                            cancel_button = "Cancel")
        if warning_dialogue == "Auto Scale":
            if len(self.selection) > 1:
                self.copy_actions()
            else:
                error_warnining = flame.messages.show_in_dialog(
                            title = "Error",
                            message = 'You will need more than one sequence selected.',
                            type = "error",
                            buttons = ["Build XML's"],
                            cancel_button = "Cancel")
                if error_warnining == "Build XML's":
                    self.build_xmls()

        elif warning_dialogue == "Build XML's":
            self.build_xmls()
        
        elif warning_dialogue == "Build Res List":
            self.resolution_list()
        
        else:
            return
    
    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads configuration values from the config file and applies them to `self.settings`.

        If the config file does not exist, it creates the file using the default values
        from the `config_values` dictionary. Otherwise, it loads the existing config values
        and applies them to `self.settings`.
        """

        self.settings = PyFlameConfig(
            config_values={
                'xml_path': '/'
                },
            )
    
    def save_config(self) -> None:
            """
            Save settings to config file and close window.
            """

            self.settings.save_config(
                config_values={
                    'xml_path': str(self.xml_path)
                    }
                )

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

        # Build list based on all the linked segments
        for item in self.selection:
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        resolution = f"{segment.source_width}x{segment.source_height}"              
                        if resolution not in self.resolution_list:
                            self.resolution_list.append(resolution)
        
        # # Specify json file path
        # self.res_file_location = Path(f"/opt/Autodesk/project/{project_name}/tmp/auto_scale_resolution_list.json")

        # Ensure the directory exists
        self.res_file_location.parent.mkdir(parents=True, exist_ok=True)

        # Write the list to the JSON file
        with self.res_file_location.open("w") as json_file:
            json.dump(self.resolution_list, json_file, indent=4)
        
        # Show Sucess Dialog with path        
        flame.messages.show_in_dialog(
                            title = "Success",
                            message = f"Resolution list exported to: {self.res_file_location}",
                            type = "info",
                            buttons = ["Ok"],
                            cancel_button = "Cancel")
        
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Build Resolution List Complete', '=========]\n')

    @catch_exception
    def build_xmls(self):

        project_name = flame.projects.current_project.name
        uc_xml_file_location = (f"/Volumes/vfx/UC_Jobs/{project_name}/CONFORM_PREP/XML")
        self.resolution_list = []
        # Build a list of all the different resolutions of segments that have an action timeline effect
        for item in self.selection:
            # destination_reel = item.parent.parent.create_reel('temp_xmls')
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        for tlfx in segment.effects:
                            if tlfx.type == 'Action':
                                resolution = f"{segment.source_width}x{segment.source_height}"
                                                                
                                if resolution not in self.resolution_list:
                                    self.resolution_list.append(resolution)

            # Select XML result from Fix Premiere XML script
            xml_paths = pyflame.file_browser(
            use_flame_browser=True,
            path = str(uc_xml_file_location),
            multi_selection = False,
            title='Select Fixed XML',
            extension=['xml'],
            )
            
            self.xml_path = Path(xml_paths)
            for item in self.resolution_list:
                self.resolution = item
                self.scale_xml()

            # Break after 1st item in selection
            break
        
        # Set MediaHub Path
        xml_exports = str(Path(self.outname).parent)
        flame.set_current_tab('MediaHub')       
        flame.mediahub.files.set_path(xml_exports)

        # Refresh MediaHub and save Config
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        self.save_config()
        
        # Ensure the directory exists
        self.res_file_location.parent.mkdir(parents=True, exist_ok=True)

        # Write the list to the JSON file
        with self.res_file_location.open("w") as json_file:
            json.dump(self.resolution_list, json_file, indent=4)

        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Build XML\'s Complete', '=========]\n')

    @catch_exception
    def copy_actions(self):

        self.resolution_list = []
        skip_list = []
        target_sequence = None

        self.sequence_list = []
        for item in self.selection:
            self.sequence_list.append(item.name)
        # print (f"Sequence List: {self.sequence_list}")

        for item in self.selection:
            # Look for the primary version (the version that has the primary track.)
            for version in item.versions:
                
                # Use the version that has the primary track
                track_list = []
                primary_version = []
                
                for track in version.tracks:
                    track_list.append(str(track))
                    if str(item.primary_track) in track_list:
                        primary_version = version
            break

        # Get the total number of tracks and segments for the first item
        first_item_tracks_count = len(primary_version.tracks)
        first_item_segments_count = sum(
            len(track.segments) for track in primary_version.tracks
        )
        print (f"First item Tracks: {first_item_tracks_count}")
        print (f"First item Tracks: {first_item_segments_count}","\n")

        # Compare the counts for the rest of the items
        count = 0
        for item in self.selection[1:]:
            # Calculate total tracks and segments for this item
            count = count +1
            item_tracks_count = sum(len(version.tracks) for version in item.versions)
            item_segments_count = sum(
                len(track.segments) for version in item.versions for track in version.tracks
            )

            print (f"XML #{count} Tracks: {item_tracks_count}")
            print (f"XML #{count} Segments: {item_segments_count}")
            # Compare with the first item's counts
            if item_tracks_count != first_item_tracks_count or item_segments_count != first_item_segments_count:
                print (f"Mismatched XML: {item.name}")
                flame.messages.show_in_dialog(
                            title = "Error",
                            message = 'Not all selected sequences have amount of Tracks and Segments.',
                            type = "error",
                            buttons = ["Ok"],
                            cancel_button = "Cancel")
                return
        print ("\n","Passed Track and Segment Check.","\n")

        if not os.path.split(self.action_path):
            self.action_path = '/var/tmp/auto_xml_temp.action'      

        # Only copy actions for the primary version
        if primary_version:

            track_count = -1                
            
            for track in primary_version.tracks:
                track_list.append(str(track))
                track_count = track_count + 1
                segment_count = -1                       

                for segment in track.segments:
                    segment_count = segment_count + 1

                    for tlfx in segment.effects:
                        if tlfx.type == 'Action':
                            resolution = f"{segment.source_width}x{segment.source_height}"
            
                            for seq in self.selection:
                                if resolution in str(seq.name):
                                    target_sequence = seq

                            if target_sequence:
                                target_segment = target_sequence.versions[0].tracks[int(track_count)].segments[int(segment_count)]
                                for tlfx in target_segment.effects:
                                    if tlfx.type == 'Action':
                                        tlfx.save_setup(self.action_path)
                                        for tlfx in segment.effects:
                                            if tlfx.type == 'Action':
                                                flame.delete(tlfx)
                                                action_fx = segment.create_effect('Action')
                                                action_fx.load_setup(self.action_path)
                                                # tlfx.load_setup(self.action_path)
                                                segment.colour = (50,50,50)
                                target_sequence = None

                            else:
                                print("Didn't find a matching sequence.")
                                if resolution not in skip_list:
                                    skip_list.append(resolution)
                                    PyFlameMessageWindow(title='Missing Conform', message=f'Cannot find a sequence with "{resolution}" in the name.', type=MessageType.ERROR )
                    
            # Delete everything except for the first item in the selection
            for item in self.selection[1:]:
                flame.delete(item)
    
        else:
            print("Can't find a Version with the Primary Track.")
            return


        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Auto Scale Complete', '=========]\n')

    @catch_exception
    def scale_xml(self):
        tree = ET.parse(self.xml_path)
        self.root = tree.getroot()
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        
        # Get Conform Resolution and Aspect Ratio
        full_x_res = int(self.resolution.split('x')[0])
        full_y_res = int(self.resolution.split('x')[1])
        full_res_aspect_ratio = full_x_res / full_y_res

        status = 1
        # print("Fixing Scale...")
        for clip in clips:
            name = clip.find('name').text
            print("Clip " + str(status) + ": " + name)
            status += 1

            file = clip.find('file')
            if file is None:
                print("ERROR: No file, maybe a nest?")
                continue
            search = ".//*[@id='{}']".format(list((file.attrib).items())[0][1])
            master = self.root.find(search)

            cliphoriz = master.find(".//media/video/samplecharacteristics/width").text
            proxy_x_res = int(cliphoriz)
            clipvert= master.find(".//media/video/samplecharacteristics/height").text
            proxy_y_res = int(clipvert)
            proxy_aspect_ratio = proxy_x_res / proxy_y_res

            if full_res_aspect_ratio >= proxy_aspect_ratio:
                self.scalemult = round((proxy_x_res / full_x_res),4)
            else:
                self.scalemult = round((proxy_y_res / full_y_res),4)

            scaleparam = clip.find(".//filter/effect/[name='Basic Motion']/parameter/[name='Scale']")
            if scaleparam is not None and self.scalemult != 1:
                xmlscale = scaleparam.find("value")
                if xmlscale is None: continue
                newscale = self.scalemult * float(xmlscale.text)
                # print("New Scale = " + str(newscale))
                xmlscale.text = str(newscale)
                keyframes = scaleparam.findall('keyframe')
                if len(keyframes) != 0:
                    # print("New Scale Keyframes:")
                    for keyframe in keyframes:
                        keyframe[1].text = str(float(keyframe[1].text) * self.scalemult)
                        # print(keyframe[1].text)

        # Build Output Name
        xml_file_path = Path(self.xml_path)
        directory = xml_file_path.parent
        
        # Remove extension
        filename = xml_file_path.name.replace(".xml","")
        # remove any _scl garbage
        filename = xml_file_path.name.split("_scl")[0]

        try:
            os.mkdir(f"{directory}/{filename}")
        except:
            pass
        self.outname = f"{directory}/{filename}/{filename}_{self.resolution}.xml"
        
        # Try to control the name that gets imported to Flame
        sequence_names = self.root.findall(".//sequence")
        for offline_name in sequence_names:
            try:
                xml_name = offline_name.find('name')
                xml_name.text = f"{filename}_{self.resolution}"
            except:
                pass

        # Kick out the XMLs
        if os.path.isfile(self.outname):
            xml = self.outname.split("/")[-1]
            warning_dialogue = flame.messages.show_in_dialog(
            title = "Warning",
            message = f'"{xml}" alredy exists. Do you want to overwrite it?',
            type = "warning",
            buttons = ["Overwrite"],
            cancel_button = "Cancel")

            if warning_dialogue == "Overwrite":
                pass
            else:
                print("Export of XML Canceled")
                return
        else:
            pass
        # print("Exporting: ", self.outname.split("/")[-1])
        tree.write(self.outname)
        # print('*' * 60)


#-------------------------------------#
# Scopes

def scope_sequence_or_segment(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence)) or isinstance(item, (flame.PySegment)):
            return True
    return False

def scope_sequence_or_clip(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence)) or isinstance(item, (flame.PyClip)):
            return True
    return False

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence)):
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
                    'execute': AutoScaleXMLs,
                    'isVisible': scope_sequence,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]