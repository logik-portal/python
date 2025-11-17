'''
Script Name: frame_io_get_status
Script Version: 0.2
Flame Version: 2025.1
Written by: John Geehreng
Creation Date: 09.06.24
Update Date: 09.11.24

Script Type: MediaPanel

Description:

    This script will fetch the status of any items in FrameIO and color code the Flame selection according to the status on FrameIO.

To install:

    Copy script into /opt/Autodesk/shared/python/frame_io

Updates:
09.11.24 - v0.2 - Added Try/Except for Colour Labels.
09.06.24 - v0.1 - Inception

'''

import xml.etree.ElementTree as ET
import flame
import os
import requests
from frameioclient import FrameioClient

SCRIPT_NAME = 'FrameIO Get Status'
SCRIPT_PATH = '/opt/Autodesk/shared/python/frame_io'
VERSION = 'v0.2'

#-------------------------------------#
# Main Script

class frame_io_get_status(object):

    def __init__(self, selection):

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' Start ', '<' * 10, '\n')

        # Paths

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        # Load config file

        self.config()

        # Start Script Here
        self.get_comments(selection)

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

    def get_comments(self, selection):
        print("Starting FrameIO stuff...")
       
        self.project_nickname = flame.project.current_project.nickname
        # Initialize the client library
        # client = FrameioClient(self.token)
        self.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(self.token)
        }
        # print("headers: ", self.headers)
        print("Project Nickname: ", self.project_nickname)
        try:
            root_asset_id, project_id = self.get_fio_projects()
        except:
            message = ("Can't find " + self.project_nickname + " FrameIO Project.")
            flame.messages.show_in_dialog(
            title = "Error",
            message = message,
            type = "error",
            buttons = ["Ok"])
            print (message)
            return

        # print('root_asset_id: ', root_asset_id)
        # print('project_id: ', project_id)
        self.root_asset_id = root_asset_id

        for item in selection:
            selection_name = item.name
            print ("Selection Name: ", selection_name)

            # find an asset using project and selection name
            search = self.find_a_fio_asset(project_id,selection_name)
            if search != ([], [], []):
                # print('search: ', search)
                type, id, status = search
                # print ("type: ", type)
                # print("id: ", id)
                print("status: ", status)
                print ('\n')
                if status == 'approved':
                    try:
                        item.colour_label = "Approved"
                    except:
                        item.colour = (0.11372549086809158, 0.26274511218070984, 0.1764705926179886)
                elif status == 'needs_review':
                    try:
                        item.colour_label = "Needs Review"
                    except:
                        item.colour = (0.6000000238418579, 0.3450980484485626, 0.16470588743686676)
                elif status == 'in_progress':
                    try:
                        item.colour_label = "In Progress"
                    except:
                        item.colour = (0.26274511218070984, 0.40784314274787903, 0.5019607543945312)
                else:
                    message = f"{selection_name} has no status in FrameIO." 
                    flame.messages.show_in_console(message, 'info',3)

            else:
                message = "Can't find " + selection_name + " in FrameIO."
                flame.messages.show_in_console(message, 'info',6)
                continue

        print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' End ', '<' * 10, '\n')


    def get_fio_projects(self):
        # Get FrameIO Project ID using the Flame Project Name
        url = "https://api.frame.io/v2/teams/" + self.team_id + "/projects"
        query = {
        "filter[archived]": "none",
        "include_deleted": "false"
        }
        response = requests.get(url, headers=self.headers, params=query)
        data = response.json()

        for projects in data:
            if projects['_type'] == "project" and projects['name'] == self.project_nickname:
                # print(projects['name'], "id: ", projects['id'])
                root_asset_id = projects['root_asset_id']
                # print("root_asset_id: ", root_asset_id)
                project_id = projects['id']
                # print("project_id: ", project_id)
                return (root_asset_id, project_id)
       
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
            "team_id": self.team_id
        }
        # print(query)
        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # print(data)
        type = []
        id = []
        status = []
        for item in data:
            # print(item[('name'))
            type = item['type']
            # print(item['type'])
            id = item['id']
            # print(item['id'])
            status = item['label']
            # print(item['label'])
            break
        return(type,id,status)

    def get_selection_comments(self, id):

        url = "https://api.frame.io/v2/assets/" + id + "/comments"

        query = {
        "include": "replies"
        }

        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # print(data)
        return(data)

# Scope
def scope_clip(selection):
    import flame

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def scope_segment(selection):
    import flame
    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False
#-------------------------------------#
# Flame Menus

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'UC FrameIO',
            'actions': [
                {
                    'name': 'Get Status',
                    'order': 5,
                    'isVisible': scope_clip,
                    'separator': 'above',
                    'execute': frame_io_get_status,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
