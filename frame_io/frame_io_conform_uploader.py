'''
Script Name: frame_io_conform_uploader
Script Version: 1.1.3
Flame Version: 2024.2
Written by: John Geehreng
Creation Date: 01.03.23
Update Date: 09.28.24

Script Type: MediaPanel

Description:

    This script will export h264 .mp4's to a FROM_FLAME folder in your job folder, save it to a FROM_FLAME shared library, and upload them to FrameIO.
    It will also automatically create or add to version stacks if it can find a matching base name.
    Script assumes a verion of _v## or _V### in order to match file names.

Updates:
09.28.24 - v1.1.3 Prep for Logik Portal
09.28.24 - v1.1.2 Simplified the way of searching for the FROM_FLAME shared library and it's subfolders.
09.24.24 - v1.0.2 Adjusted base name search to work with v## or V##. Splits at the last match.
09.19.24 - v1.0.1 Fixed a bug where script would fail if there wasn't an existing project
09.13.24 - v1.0 - Added automatic version upper
06.13.24 - v0.9.3 - Added Progress window for uploads
03.20.24 - v0.9.2 - API Updates and Updates for failing searches
12.04.23 - v0.8 - Updates for PySide6 (Flame 2025)
10.31.23 - v0.7 - Minor print Adjustments
09.21.23 - v0.6 - Updated Preset to export mp4's directly from Flame instead of exporting h264 mov's and changing the extension.
04.27.23 - v0.5 - changes to uppercut staff
01.11.23 - v04.1- changed pattern from: r'_[vV]\d*' to r'_[vV]\d+'
01.10.23 - v0.4 - fixed issue where search was finding deleted files.
01.05.23 - v0.3 - added scope

To install:

    Copy script into /opt/Autodesk/shared/python/frame_io
'''

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets
import xml.etree.ElementTree as ET
import flame
import datetime
import os
import re
import glob
import requests
from frameioclient import FrameioClient
from pyflame_lib_frame_io import PyFlameProgressWindow

SCRIPT_NAME = 'FrameIO Conform Uploader'
SCRIPT_PATH = '/opt/Autodesk/shared/python/frame_io'
VERSION = 'v1.0.2'

#-------------------------------------#
# Main Script

class frame_io_uploader(object):

    def __init__(self, selection):

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' Start ', '<' * 10, '\n')

        # Paths

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        # Load config file

        self.config()

        # Search for existing version - if a matching version (with the same exact name) is found the selection will be automatically versioned up before being exported.
        self.version_upper(selection)
        # Copy to the FROM_FLAME shared library and export
        self.export_and_copy_path(selection)
        # Upload to FrameIO. Find appropriate folder and version stack if a match is found.
        self.upload_to_frameio()

    def config(self):

        def get_config_values():

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            # Get Settings from config XML

            for setting in root.iter('frame_io_settings'):
                self.token = setting.find('token').text
                self.account_id = setting.find('account_id').text
                self.team_id = setting.find('team_id').text
                self.jobs_folder = setting.find('jobs_folder').text
                self.preset_path_h264 = setting.find('preset_path_h264').text


            # pyflame_print(SCRIPT_NAME, 'Config loaded.')

        def create_config_file():

            if not os.path.isdir(self.config_path):
                try:
                    os.makedirs(self.config_path)
                except:
                    flame.messages.show_in_dialog(
                        title = "f'{SCRIPT_NAME}: Error",
                        message = f'Unable to create folder: {self.config_path}<br>Check folder permissions',
                        type = "error",
                        buttons = ["Ok"],
                        cancel_button = "Cancel")
                    # FlameMessageWindow('error', f'{SCRIPT_NAME}: Error', f'Unable to create folder: {self.config_path}<br>Check folder permissions')

            if not os.path.isfile(self.config_xml):
                # pyflame_print(SCRIPT_NAME, 'Config file does not exist. Creating new config file.')

                config = '''
<settings>
    <frame_io_settings>
        <token>fio-x-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxx-xxxxxxxxxxx</token>
        <account_id>xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</account_id>
        <team_id>xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx</team_id>
        <jobs_folder>/Volumes/vfx/UC_Jobs</jobs_folder>
        <preset_path_h264>/opt/Autodesk/shared/python/frame_io/presets/UC H264 10Mbits.xml</preset_path_h264>
    </frame_io_settings>
</settings>'''

                with open(self.config_xml, 'a') as config_file:
                    config_file.write(config)
                    config_file.close()

        if os.path.isfile(self.config_xml):
            get_config_values()
        else:
            create_config_file()
            if os.path.isfile(self.config_xml):
                get_config_values()
    
    
    def export_and_copy_path(self, selection):

        # self.project_nickname = flame.project.current_project.nickname
        dateandtime = datetime.datetime.now()
        today = (dateandtime.strftime("%Y-%m-%d"))
        time = (dateandtime.strftime("%H%M"))
        shared_libs = flame.projects.current_project.shared_libraries
        
        #Check for FROM_FLAME Shared Library if missing create one
        sharedlib = None
        # Look for a shared library called "FROM_FLAME"
        for libary in shared_libs:      
            if libary.name == "FROM_FLAME":
                sharedlib = libary
        # If it's found, keep going. Otherwise create a shared library called "FROM FLAME"
        if sharedlib:
            pass
        else:
            sharedlib = flame.project.current_project.create_shared_library('FROM_FLAME')

        #Define Export Path & Check for Preset

        preset_check = (str(os.path.isfile(self.preset_path_h264)))

        if preset_check == 'True':
            pass
            # print ("Export Preset Found")
        else:
            # print ('Export Preset Not Found.')
            flame.messages.show_in_dialog(
            title = "Error",
            message = "Cannot find Export Preset.",
            type = "error",
            buttons = ["Ok"])
            return

        export_dir =f"{self.jobs_folder}/{str(self.project_nickname)}/FROM_FLAME/{str(today)}"

        #Define Exporter
        exporter = flame.PyExporter()
        exporter.foreground = True
        exporter.export_between_marks = True
        exporter.use_top_video_track = True

        # Look for a Folder with Today's Date
        todays_match=False
        for folder in sharedlib.folders:
            if folder.name == today:
                todays_match = True
            # print ("Today's Folder # is: ", today_folder_number)
        
        # If it finds a match, create a timestamped folder
        if todays_match == True:
            sharedlib.acquire_exclusive_access()
            postingfolder = folder.create_folder(time)
            tab = flame.get_current_tab()
            if tab == 'MediaHub':
                flame.set_current_tab("Timeline")
            for item in selection:
                flame.media_panel.copy(item, postingfolder)
            exporter.export(postingfolder, self.preset_path_h264, export_dir)
            
            # Collapse everything
            sharedlib.expanded = False
            postingfolder.expanded = False
            folder.expanded = False
            sharedlib.release_exclusive_access()
            posted_folder = postingfolder.name
            self.export_path =f"{export_dir}/{str(posted_folder)[1:-1]}"
            qt_app_instance = QtWidgets.QApplication.instance()
            qt_app_instance.clipboard().setText(self.export_path)

        else:
            # print ("Today's Folder Not Found")
            sharedlib.acquire_exclusive_access()
            postingfolder = sharedlib.create_folder(today).create_folder(time)
            tab = flame.get_current_tab()
            if tab == 'MediaHub':
                flame.set_current_tab("Timeline")
            for item in selection:
                flame.media_panel.copy(item, postingfolder)
            exporter.export(postingfolder, self.preset_path_h264, export_dir)

            # Collapse everything
            sharedlib.expanded = False
            postingfolder.expanded = False
            postingfolder.parent.expanded = False
            folder.expanded = False
            sharedlib.release_exclusive_access()
            posted_folder = postingfolder.name
            self.export_path = f"{str(export_dir)}/{str(posted_folder)[1:-1]}"
            qt_app_instance = QtWidgets.QApplication.instance()
            qt_app_instance.clipboard().setText(self.export_path)


    def upload_to_frameio(self):
        print("Starting FrameIO stuff...")

        # Initialize the client library
        client = FrameioClient(self.token)
        # self.headers = {
        # "Content-Type": "application/json",
        # "Authorization": "Bearer " + str(self.token)
        # }
        # print("headers: ", self.headers)
        print("Project Nickname: ", self.project_nickname)
        try:
            root_asset_id, project_id = self.get_fio_projects()
        except:
            root_asset_id, project_id = self.create_fio_project(self.project_nickname)
        # print('root_asset_id: ', root_asset_id)
        # print('project_id: ', project_id)
        self.root_asset_id = root_asset_id
        # print(self.export_path)
                
        self.export_path = self.export_path + '/**/*'
        files = glob.glob(self.export_path, recursive=True)
        
        # Progress Bar Setup
        number_of_new_spots = len(files)
        spot_count = 0
        self.progress_window = PyFlameProgressWindow( num_to_do=number_of_new_spots,
                        title='Uploading...',
                        text=f'Uploading: Spot 1 of {number_of_new_spots}',
                        enable_done_button=False,
                        )
        
        print ("files", files)
        for filename in files:

            print('\n')
            path, file_name = os.path.split(filename)
            print("file_path: ", path)
            # print("file path: ", filename)
            print ("file name: ", file_name)

            # Check for v## or V##
            pattern=r'_[vV]\d+'
            # Find all matches of the pattern in the text
            matches = list(re.finditer(pattern, file_name))

            # If there are matches, split at the last match
            if matches:
                split_index = matches[-1].start()
                base_name = file_name[:split_index]
            # If there are no matches, use the file name
            else:    
                base_name = file_name
            print(f"base_name: {base_name}")

            #Update the spot
            spot_count = spot_count + 1
            # To update progress bar progress value:
            self.progress_window.set_progress_value(spot_count)
            # To update text in window:
            # self.progress_window.set_text(f'Uploading: Spot {spot_count} of {number_of_new_spots}')
            # This is a test to see if I want to display the filename.
            self.progress_window.set_text(f'Uploading: Spot {spot_count} of {number_of_new_spots}<br>\nFilename: {file_name}')

            # find an asset using project and base name
            search = self.find_a_fio_asset(project_id,base_name)
            if search != ([], [], []):
                # print('search: ', search)
                type, id, parent_id = search
                # print ("type: ", type)
                # print("id: ", id)
                # print("parent_id: ", parent_id)
                if 'file' in search:
                    print('Search results for matching base name asset ID: ', id)
                    try:
                        asset = client.assets.upload(parent_id, filename)
                        # print(asset)
                        next_asset_id = str(asset['id'])
                        # print('next_asset_id: ', next_asset_id)
                        self.version_asset(id, next_asset_id)
                    except:
                        print("File may have been deleted from FrameIO. Uploding elsewhere...")
                        
                if 'version_stack' in search:
                    print('Version Stack ID: ', id)
                    asset = client.assets.upload(id, filename)

            else:
                print("Can't find a match...uploading to the CONFORMS folder.")
                # Try to upload to the newly created CONFORMS Folder. If that doesn't work, look for one or create it.
                try:
                    asset = client.assets.upload(self.new_folder_id, filename)
                except:
                    # print ("looking for CONFORMS folder...")
                    conforms_folder_id = self.find_conforms_folder(project_id)
                    # print ("conforms_folder_id: ", conforms_folder_id)
                    
                    if conforms_folder_id == []:
                        # print ("CONFORMS FOLDER NOT FOUND. Creating one.")
                        self.create_fio_folder(self.root_asset_id, "SHOTS")
                        asset = client.assets.upload(self.new_folder_id, filename)
                    else:
                        # print ("CONFORMS FOLDER FOUND.")
                        asset = client.assets.upload(conforms_folder_id, filename)

        # Enable 'Done' button once uploads have finished then close it
        self.progress_window.enable_done_button(True)
        self.progress_window.close()

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' End ', '<' * 10, '\n')

    def create_fio_project(self, flame_project_name:str):
        print("create frameIO project...")

        url = "https://api.frame.io/v2/teams/" + self.team_id + "/projects"
        # print("url: ", url)
        payload = {
            "name": flame_project_name,
            "private": False
        }
        # print("payload: ", payload)
        response = requests.post(url, json=payload, headers=self.headers)

        data = response.json()
        # print(data)
        root_asset_id = data['root_asset_id']
        # print('root_asset_id: ', root_asset_id)
        project_id = data['id']
        # print('project_id: ', project_id)
        self.create_fio_folder(root_asset_id, "SHOTS")
        self.create_fio_folder(root_asset_id, "CONFORMS")
        print  ("New CONFORMS Folder ID: ", self.new_folder_id)
        return (root_asset_id,project_id)

    def create_fio_folder(self, root_asset_id,name:str):
        url = "https://api.frame.io/v2/assets/" + root_asset_id + "/children"

        payload = {
            "name": name,
            "type": "folder"
        }

        response = requests.post(url, json=payload, headers=self.headers)

        data = response.json()
        self.new_folder_id = data['id']

    def version_asset(self, asset_id, next_id):
        url = "https://api.frame.io/v2/assets/" + asset_id + "/version"

        payload = {
            "next_asset_id": next_id

        }
        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()

    def get_fio_projects(self):
        # Get FrameIO Project ID using the Flame Project Name
        url = "https://api.frame.io/v2/teams/" + self.team_id + "/projects"
        query = {
        "filter[archived]": "none",
        "include_deleted": "false"
        }
        response = requests.get(url, headers=self.headers, params=query)
        data = response.json()

        # print("\n")
        # print("Frame IO Projects:")
        for projects in data:
            # if (projects['_type'] == "project"):
            #     print(projects['name'])
            if (projects['_type'] == "project") and (projects['name'] == self.project_nickname):
                # print(projects['name'], "id: ", projects['id'])
                root_asset_id = projects['root_asset_id']
                # print("root_asset_id: ", root_asset_id)
                project_id = projects['id']
                # print("project_id: ", project_id)
                return (root_asset_id, project_id)

        print("\n")
       
    def find_a_fio_asset(self, project_id,base_name):
        url = "https://api.frame.io/v2/search/assets"

        query = {
            "account_id": self.account_id,
            # "include": "user_role",
            # "include_deleted": "true",
            # "page": "0",
            # "page_size": "0",
            "project_id": project_id,
            "q": base_name,
            # "query": "string",
            # "shared_projects": "true",
            # "sort": "string",
            "team_id": self.team_id,
            "type": "file"
        }
        # print(query)
        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # print(data)
        type = []
        id = []
        parent_id = []
        for item in data:
            # print(item['name'])
            type = item['type']
            # print(item['type'])
            id = item['id']
            # print(item['id'])
            parent_id = item['parent_id']
            # print(item['parent_id'))
            break
        return(type,id,parent_id)

    def find_conforms_folder(self, project_id):
        url = "https://api.frame.io/v2/search/assets"

        query = {
            "account_id": self.account_id,
            # "include": "user_role",
            # "include_deleted": "true",
            # "page": "0",
            # "page_size": "0",
            "project_id": project_id,
            "q": "CONFORMS",
            # "query": "string",
            # "shared_projects": "true",
            # "sort": "string",
            "team_id": self.team_id,
            "type": "folder"
        }
        # print(query)
        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # print('Conform search: ', data)
        # folder_id = []
        for item in data:
            folder_id = item['id']
            # print(folder_id)
            return(folder_id)
        
    def version_upper(self,selection): 

        # Get Project Nickname
        self.project_nickname = flame.project.current_project.nickname

        self.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(self.token)
        }

        try:
            root_asset_id, project_id = self.get_fio_projects()
        except:
            project_id = False
            pass
        # If the script can find a FrameIO project, it then checks to see if the current version is already on FrameIO. If it is, automatically version up.
        if project_id:
            for item in selection:
                clip_name = str(item.name)[(1):-(1)]
                search = self.find_a_fio_asset(project_id,clip_name)
                if search != ([], [], []):
                    if re.search(r'v\d+', clip_name):
                        version = str(re.findall(r'v\d+', clip_name))[(2):-(2)]
                        version_number = re.split('v', version)[1]
                        version_number = '%02d' % (int(version_number)+1)
                        new_version_name = re.sub('v\d+',"v" + str(version_number),clip_name)
                        item.name = new_version_name
                    # This is here for because Steve uses V## insead of v##
                    elif re.search(r'V\d+', clip_name):
                        version = str(re.findall(r'V\d+', clip_name))[(2):-(2)]
                        version_number = re.split('V', version)[1]
                        version_number = '%02d' % (int(version_number)+1)
                        new_version_name = re.sub('V\d+',"V" + str(version_number),clip_name)
                        item.name = new_version_name
                    
                    else:
                        message = clip_name + str(" needs a version number like 'v01' or 'V01.'")
                        flame.messages.show_in_dialog(
                            title = "Error",
                            message = message,
                            type = "error",
                            buttons = ["Ok"])
                        continue
        # If it can't find a project, it moves on
        else:
            pass

#-------------------------------------#
# Scope
def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

#-------------------------------------#
# Flame Menus

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'UC FrameIO',
            "order": 3,
            'actions': [
                {
                    'name': 'Conform Uploader',
                    'order': 0,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': frame_io_uploader,
                    'minimumVersion': '2024.2'
                }
            ]
        }
    ]
