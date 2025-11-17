'''
Script Name: frame io shot uploader
Script Version: 0.9.2
Flame Version: 2024.2
Written by: John Geehreng
Creation Date: 01.03.23
Update Date: 01.25.24

Script Type: MediaPanel

Description:

    This script will export h264 .mp4's to a FROM_FLAME folder in your job folder, save it to a FROM_FLAME shared library, and upload them to FrameIO.
    It will also automatically create or add to version stacks if it can find a matching base name.
    Script assumes a verion of _v## or _V### in order to match file names.

Updates:
01.25.24 - v0.9.2 - Prep for distribution
12.04.23 - v0.9.1 - Updates for PySide6 (Flame 2025)
09.21.23 - v0.6 - Updated Preset to export mp4's directly from Flame instead of exporting h264 mov's and changing the extension.
04.27.23 - v0.5 - Added Mitch Gardiner and removed Marcus Wei
01.13.23 - v0.31 - changed os.mkdir to subprocess mkdir -p because John was having issues on nyc-lfx-001. Added messages if it can't make a directory.
01.10.23 - v0.3 - fixed issue where search was finding deleted files.
01.05.23 - v0.2 - Added ability to make directories and added scope for clips. Changed pattern to include a user nickname when searching for a match - helps if shot changes artists.

To install:

    Copy scripts into /opt/Autodesk/shared/python/frame_io


'''

import xml.etree.ElementTree as ET
import flame
import datetime
import os
import subprocess
import re
import glob
import requests
from frameioclient import FrameioClient

SCRIPT_NAME = 'FrameIO Shot Uploader'
SCRIPT_PATH = '/opt/Autodesk/shared/python/frame_io'
VERSION = 'v0.9.2'

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

        # Execution start here:
        self.export_mp4(selection)
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
  

    def export_mp4(self, selection):
        self.project_name = flame.project.current_project.name
        self.project_name = flame.project.current_project.name

        dateandtime = datetime.datetime.now()
        today = (dateandtime.strftime("%Y-%m-%d"))
        time = (dateandtime.strftime("%H%M"))

        # Define Export Path & Check for Preset
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

        self.export_dir = str(self.jobs_folder)+ "/" + str(self.project_name) + "/FROM_FLAME" + "/" + str(today) + "/" + str(time)
        print (self.export_dir)
        if not os.path.isdir(self.export_dir):
            print ("Export Directory doesn't exist. Making it now.")
            try:
                command = 'mkdir -p ' + self.export_dir
                command = command.split()
                subprocess.call(command)
            except:
                message = ("Can't make this directory: " + self.export_dir)
                print (message)
                flame.messages.show_in_console(message, 'info',6)
                return

        #Define Exporter
        exporter = flame.PyExporter()
        exporter.foreground = True
        exporter.export_between_marks = False
        exporter.use_top_video_track = True

        for item in selection:
            exporter.export(item, self.preset_path_h264, self.export_dir)

    def upload_to_frameio(self):
        print("Starting FrameIO stuff...")     

        # FACILITY SPECIFIC OPTION START - THIS IS GOOD IF YOU HAVE MULTIPLE USERS
        # user_nickname = flame.users.current_user.nickname

        # if user_nickname == "xx":
        #     self.token = 'fio-x-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx-xxxxxxxxxxx-xxxxxxxxxxx'

        # FACILITY SPECIFIC OPTION  END


        # Initialize the client library
        client = FrameioClient(self.token)
        self.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(self.token)
        }
        # print("headers: ", self.headers)
        print("Project Name: ", self.project_name)
        try:
            root_asset_id, project_id = self.get_fio_projects()
        except:
            root_asset_id, project_id = self.create_fio_project(self.project_name)
        print('root_asset_id: ', root_asset_id)
        print('project_id: ', project_id)
        self.root_asset_id = root_asset_id

        self.export_path = self.export_dir + '/**/*'
        files = glob.glob(self.export_path, recursive=True)

        for filename in files:
            print('\n')
            path, file_name = os.path.split(filename)
            print("file path: ", filename)
            print ("file name: ", file_name)
            # Split file name at _<user nickname>_v## to get the base name then search for it
            pattern = r'_[a-zA-Z]*_[vV]\d*'
            base_name = re.split(pattern, file_name)[0]
            print("base name for search: ", base_name)

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
                    asset = client.assets.upload(parent_id, filename)
                    # print(asset)
                    next_asset_id = str(asset.get('id'))
                    # print('next_asset_id: ', next_asset_id)
                    self.version_asset(id, next_asset_id)

                if 'version_stack' in search:
                    print('Version Stack ID: ', id)
                    asset = client.assets.upload(id, filename)

            else:
                print("Can't find a match...uploading to the SHOTS folder.")
                # Try to upload to the newly created SHOTS Folder. If that doesn't work, look for one or create it.
                try:
                    asset = client.assets.upload(self.new_folder_id, filename)
                except:
                    # print ("looking for SHOTS folder...")
                    shots_folder_id = self.find_shots_folder(project_id)
                    # print ("shots_folder_id: ", shots_folder_id)
                    
                    if shots_folder_id == []:
                        # print ("SHOT FOLDER NOT FOUND. Creating one.")
                        self.create_fio_folder(self.root_asset_id, "SHOTS")
                        asset = client.assets.upload(self.new_folder_id, filename)
                    else:
                        # print ("SHOT FOLDER FOUND.")
                        asset = client.assets.upload(shots_folder_id, filename)

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
        root_asset_id = data.get('root_asset_id')
        # print('root_asset_id: ', root_asset_id)
        project_id = data.get('id')
        # print('project_id: ', project_id)
        self.create_fio_folder(root_asset_id, "CONFORMS")
        self.create_fio_folder(root_asset_id, "SHOTS")
        print  ("New SHOTS Folder ID: ", self.new_folder_id)
        return (root_asset_id,project_id)

    def create_fio_folder(self, root_asset_id,name:str):
        url = "https://api.frame.io/v2/assets/" + root_asset_id + "/children"

        payload = {
            "filesize": 0,
            "name": name,
            "type": "folder"
        }

        response = requests.post(url, json=payload, headers=self.headers)

        data = response.json()
        self.new_folder_id = data.get('id')

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
        "filter[archived]": "all"
        }
        response = requests.get(url, headers=self.headers, params=query)
        data = response.json()

        print("\n")
        print("Frame IO Projects:")
        for projects in data:
            if (projects.get('_type') == "project"):
                print(projects.get('name'))
            if (projects.get('_type') == "project") and (projects.get('name') == self.project_name):
                # print(projects.get('name'), "id: ", projects.get('id'))
                root_asset_id = projects.get('root_asset_id')
                # print("root_asset_id: ", root_asset_id)
                project_id = projects.get('id')
                # print("project_id: ", project_id)
                return (root_asset_id, project_id)
        print("\n")
    
    def find_a_fio_asset(self, project_id,base_name):
        url = "https://api.frame.io/v2/search/assets"

        query = {
            "account_id": self.account_id,
            "include": "user_role",
            # "include_deleted": "true",
            "page": "0",
            "page_size": "0",
            "project_id": project_id,
            "q": base_name,
            # "query": "string",
            "shared_projects": "true",
            # "sort": "string",
            "team_id": self.team_id#,
            # "type": "file"
        }
        # print(query)
        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # print(data)
        type = []
        id = []
        parent_id = []
        for item in data:
            # print(item.get('name'))
            type = item.get('type')
            # print(item.get('type'))
            id = item.get('id')
            # print(item.get('id'))
            parent_id = item.get('parent_id')
            # print(item.get('parent_id'))
            break
        return(type,id,parent_id)
    
    def find_shots_folder(self, project_id):
        url = "https://api.frame.io/v2/search/assets"

        query = {
            "account_id": self.account_id,
            "include": "user_role",
            # "include_deleted": "true",
            "page": "0",
            "page_size": "0",
            "project_id": project_id,
            "q": "SHOTS",
            # "query": "string",
            "shared_projects": "true",
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
            folder_id = item.get('id')
            # print(folder_id)
            return(folder_id)

# Scope
def scope_clip(selection):
    import flame

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

#-------------------------------------#
# Flame Menus

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'FrameIO',
            'actions': [
                {
                    'name': 'Shot Uploader',
                    'order': 1,
                    'isVisible': scope_clip,
                    'execute': frame_io_uploader,
                    'minimumVersion': '2024.2'
                }
            ]
        }
    ]
