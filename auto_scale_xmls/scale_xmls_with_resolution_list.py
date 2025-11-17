"""
Script Name: scale xmls with resolution list
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 12.06.24
Update Date: 12.25.24

Script Type: MediaHub

Description:

    Fix Adobe Premiere XML's.

Menus:

        MediaHub -> XML Prep -> Scale XML's with Resolution List

To install:

    Copy script into your python folder, typically /opt/Autodesk/shared/python/auto_scale_xmls or put it wherever you keep your scripts

Updates:

    v1.0.0   10.22.25

        use flame.projects.current_project.project_folder to determine where to save json's

    v0.4   12.26.24

        moved script path
        
    v0.3   12.18.24

        made foler names more flexible

    v0.2   12.14.24

        added try/except for changing names

    v0.1   12.06.24

        Inception

"""

# ---------------------------------------- #
# Imports

import flame
import re
import os
import json
import traceback
from pathlib import Path
from pyflame_lib_auto_scale_xmls import *

#-------------------------------------#
# Main Script

FOLDER_NAME = "XML Prep"
SCRIPT_NAME = "Scale XML's with Resolution List"
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class fix_premiere_xmls():

    def __init__(self, selection) -> None:

        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        
        # Specify file path
        project_name = flame.projects.current_project.name
        # res_file_location = (f"/opt/Autodesk/project/{project_name}/tmp")

        simple_flame_version = flame.get_version().split('.')[0]
        
        if simple_flame_version <= '2026':
            full_project_path = flame.projects.current_project.project_folder
            project_tmp_path = re.sub(r"^/hosts/[^/]+", "", full_project_path) + '/tmp'
            res_file_location = f"{project_tmp_path}/auto_scale_resolution_list.json"
        else:
            res_file_location = f"/opt/Autodesk/project/{project_name}/tmp/auto_scale_resolution_list.json"
        print (f"Resolution List Path: {res_file_location}")
        
        json_path = Path(pyflame.file_browser(
            path=res_file_location,
            title='Load Resolution List',
            extension=['json'],
            ))

        # Read the JSON file
        with json_path.open("r") as json_file:
            loaded_data = json.load(json_file)

        print("Loaded data:", loaded_data)
        # for item in loaded_data:
        #     print(f"Resolution: {item}")
        for item in selection:
            print (f"XML: {item.path}")
            self.xml_path = item.path
            for item in loaded_data:
                self.resolution = item
                self.scale_xml()
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} Complete', '=========]\n')
    
    def catch_exception(method):                                                                                                                                              
        def wrapper(self,*args,**kwargs):                                                                                                                                     
            try:                                                                                                                                                              
                return method(self,*args,**kwargs)                                                                                                                            
            except:                                                                                                                                                           
                traceback.print_exc()                                                                                                                                         
        return wrapper    
    
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
            # print("Clip " + str(status) + ": " + name)
            status += 1

            file = clip.find('file')
            if file is None:
                # print("ERROR: No file, maybe a nest?")
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
        outname = f"{directory}/{filename}/{filename}_{self.resolution}.xml"
        
        # Try to control the name that gets imported to Flame
        sequence_names = self.root.findall(".//sequence")
        for offline_name in sequence_names:
            try:
                xml_name = offline_name.find('name')
                xml_name.text = f"{filename}_{self.resolution}"
            except:
                pass

        # Kick out the XMLs
        if os.path.isfile(outname):
            self.window.hide()
            xml = outname.split("/")[-1]
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
        print("Exporting: ", outname.split("/")[-1])
        tree.write(outname)
        # print('*' * 60)
        
        # Refresh MediaHub
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        print('\n')


# ---------------------------------------- #
# Scope

def scope_all_xmls(selection):
    return all(file.path.endswith('.xml') for file in selection)

#-------------------------------------#
# Flame Menus

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': FOLDER_NAME,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'execute': fix_premiere_xmls,
                    'isVisible': scope_all_xmls,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]