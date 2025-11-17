'''
Script Name: frame_io_get_comments
Script Version: 0.9
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 01.06.23
Update Date: 10.03.24

Script Type: MediaPanel

Description:

    This script will fetch comments from FrameIO and make markers according to the selection.

To install:

    Copy script into /opt/Autodesk/shared/python/frame_io

Updates:
10.03.24 - v0.9 - Start using Color Code Labels
03.21.24 - v0.8 - Misc Optimizations
12.04.23 - v0.7 - Updates for PySide6 (Flame 2025)
11.01.23 - v0.6 - Flag Sequences by assigning color
02.27.23 - v0.5 - Fixed issue for users not signed in, but left comments.
01.18.23 - v0.4 - Added ability to compensate for In Points set before frame 1.
01.11.23 - v0.3 - Fixed Error message when there's not FrameIO Project. Added ability to make segment markers. Added warnings and messages if comments can't be found.
'''

import xml.etree.ElementTree as ET
import flame
import math
import re
import os
import requests
from frameioclient import FrameioClient

SCRIPT_NAME = 'FrameIO Get Comments'
SCRIPT_PATH = '/opt/Autodesk/shared/python/frame_io'
VERSION = 'v0.9'

#-------------------------------------#
# Main Script

class frame_io_get_comments(object):

    def __init__(self, selection):

        #print('\n')
        #print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' Start ', '<' * 10, '\n')

        # Paths

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        # Load config file

        self.config()

        # Start Script Here
        self.get_frame_rate(selection)
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


            # pyflame_#print(SCRIPT_NAME, 'Config loaded.')

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
                # pyflame_#print(SCRIPT_NAME, 'Config file does not exist. Creating new config file.')

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

    def get_frame_rate(self, selection):
        for item in selection:
            if isinstance(item, flame.PySegment):
                # #print ("I am a segment. Selection name: ", item.name)
                parent_sequence = item.parent.parent.parent
                frame_rate = parent_sequence.frame_rate
                # #print ("frame_rate: ", frame_rate)
                regex = r'\s[a-zA-Z]*'
                test_str = str(frame_rate)
                subst = ""
                fixed_framerate = float(re.sub(regex, subst, test_str, 0))
                fixed_framerate =  math.ceil(fixed_framerate)
                # #print('fixed_framerate: ', str(fixed_framerate))
                self.frame_rate = fixed_framerate
            elif isinstance(item, flame.PyClip):
                # selection_name = item.name
                # #print ("Selection Name: ", selection_name)
                frame_rate = item.frame_rate
                # #print ("frame_rate: ", frame_rate)
                regex = r'\s[a-zA-Z]*'
                test_str = str(frame_rate)
                subst = ""
                fixed_framerate = float(re.sub(regex, subst, test_str, 0))
                fixed_framerate =  math.ceil(fixed_framerate)
                # #print('fixed_framerate: ', str(fixed_framerate))
                self.frame_rate = fixed_framerate
            else:
                # #print('\n')
                self.frame_rate = 24
                #print ("I am not a segment. Selection name: ", item.name)
                # #print('\n')
                pass
    
    def _seconds(self, value):
        if isinstance(value, str):  # value seems to be a timestamp
            _zip_ft = zip((3600, 60, 1, 1/self.frame_rate), value.split(':'))
            return sum(f * float(t) for f,t in _zip_ft)
        elif isinstance(value, (int, float)):  # frames
            return value / self.frame_rate
        else:
            return 0

    def _timecode(self, seconds):
        return '{h:02d}:{m:02d}:{s:02d}:{f:02d}' \
                .format(h=int(seconds/3600),
                        m=int(seconds/60%60),
                        s=int(seconds%60),
                        f=round((seconds-int(seconds))*self.frame_rate))

    def _frames(self, seconds):
        return seconds * self.frame_rate

    def timecode_to_frames(self, timecode, start=None):
        return self._frames(self._seconds(timecode) - self._seconds(start))

    def frames_to_timecode(self, frames, start=None):
        return self._timecode(self._seconds(frames) + self._seconds(start))

    def get_comments(self, selection):
        #print("Starting FrameIO stuff...")
       
        self.project_nickname = flame.project.current_project.nickname
        # Initialize the client library
        # client = FrameioClient(self.token)
        self.headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + str(self.token)
        }
        # #print("headers: ", self.headers)
        #print("Project Nickname: ", self.project_nickname)
        try:
            root_asset_id, project_id = self.get_fio_projects()
        except:
            message = ("Can't find " + self.project_nickname + " FrameIO Project.")
            flame.messages.show_in_dialog(
            title = "Error",
            message = message,
            type = "error",
            buttons = ["Ok"])
            #print (message)
            return

        #print('root_asset_id: ', root_asset_id)
        #print('project_id: ', project_id)
        self.root_asset_id = root_asset_id

        for item in selection:
            offset_value = 0
            if isinstance(item, flame.PySegment):
                #print ("I am a segment. Selection name: ", item.name)
                parent_sequence = item.parent.parent.parent
                selection_name = parent_sequence.name
                in_point = parent_sequence.in_mark
                start_time = parent_sequence.start_time
                # #print ("Parent Name: ", selection_name)
                selection_framerate = parent_sequence.frame_rate
            elif isinstance(item, flame.PyClip):
                selection_name = item.name
                in_point = item.in_mark
                start_time = item.start_time
                #print ("Selection Name: ", selection_name)
                selection_framerate = item.frame_rate
            else:
                # #print('\n')
                # #print ("I am not a segment. Selection name: ", item.name)
                # #print('\n')
                pass
                # continue
            # #print('\n')

            # See where the in point is:
            if 'NULL' in str(in_point):
                offset_value = 1
                #print("No In Point Set. ")
                
            else:
                in_point = str(in_point).replace("+", ":")
                # #print ("in_point: ", in_point)
                
                start_time = str(start_time).replace("+", ":")
                # #print ("start_time: ", start_time)

                in_point_frames = self.timecode_to_frames(in_point)
                # #print ("in_point_frames: ", in_point_frames)

                start_time_frames = self.timecode_to_frames(start_time)
                # #print ("start_time_frames: ", start_time_frames)

                if int(in_point_frames) < int(start_time_frames):
                    # #print ("In point is before Start Time.")
                    # offset_value = int(in_point_frames) - int(start_time_frames)
                    # #print ("In point is at frame: ", offset_value + 1)
                    offset_value = 0

                if int(in_point_frames) > int(start_time_frames):
                    # #print ("In point is after Start Time.")
                    # offset_value = int(in_point_frames) - int(start_time_frames)
                    # #print ("In point is at frame: ", offset_value + 1)
                    offset_value = 0
            #print (f"Offset Value: {offset_value}")

            # find an asset using project and selection name
            search = self.find_a_fio_asset(project_id,selection_name)
            if search != ([], [], []):
                # #print('search: ', search)
                type, id, parent_id = search
                # #print ("type: ", type)
                # #print("id: ", id)
                # #print("parent_id: ", parent_id)
                # #print ('\n')
                comment_data = self.get_selection_comments(id)
                # #print ("comment_data: ", comment_data)
                if 'errors:' in comment_data:
                    message = ("Comment Data: " + comment_data)
                    #print (message)
                    flame.messages.show_in_console(message, 'info',6)
                    flame.messages.show_in_dialog(
                        title = "Warning",
                        message = message,
                        type = "warning",
                        buttons = ["Ok"])
                    pass

                #print ('\n')
                if comment_data:
                    # if you find comment data, make the sequence red...
                    if isinstance(item, flame.PyClip):
                        try:
                            item.colour_label = "Address Comments"
                        except:
                            item.colour = (0.11372549086809158, 0.26274511218070984, 0.1764705926179886)
                        
                    # get comments and add them as markers
                    for info in comment_data:
                        comment = str(info['text'])
                        #print ('Comment: ', comment)
                        try:
                            name = info.get('owner').get('name')
                            #print ('Name: ', name)
                        except:
                            pass
                        frame = str(info['frame'])[0:-2]
                        #print ('Frame: ', frame)
                        duration = info['duration']
                        # #print ('Duration: ', duration)
                        # #print ('Offset Value: ', offset_value)

                        #print ('\n')
                
                        try:
                            marker = item.create_marker(int(frame) + offset_value)
                            marker.comment = comment
                            marker.name = "Commenter: " + name
                            try:
                                marker.colour_label = "Address Comments"
                            except:
                                marker.colour = (0.11372549086809158, 0.26274511218070984, 0.1764705926179886)
                                # marker.colour = (0.2, 0.0, 0.0)
                            if duration:
                                # #print (selection_framerate,duration)
                                regex = r'\s[a-zA-Z]*'
                                test_str = str(selection_framerate)
                                subst = ""
                                # You can manually specify the number of replacements by changing the 4th argument
                                fixed_framerate = float(re.sub(regex, subst, test_str, 0))
                                fixed_framerate =  math.ceil(fixed_framerate)
                                # #print('fixed_framerate: ', str(fixed_framerate))
                                duration_calc = fixed_framerate * duration
                                # #print (str(int(duration_calc)))
                                marker.duration = int(duration_calc)

                        except:
                            pass
                else:
                    message = "Can't find comments for " + '"' + selection_name + '." \nSequence name must match FrameIO name exactly.'
                    flame.messages.show_in_console(message, 'info',6)
                    # flame.messages.show_in_dialog(
                    #     title = "Warning",
                    #     message = message,
                    #     type = "warning",
                    #     buttons = ["Ok"])
                    #print (message)
                    if isinstance(item, flame.PyClip):
                        continue
                    else:
                        return
            else:
                message = "Can't find " + selection_name + " in FrameIO."
                flame.messages.show_in_console(message, 'info',6)
                continue

        #print('>' * 10, f'{SCRIPT_NAME} {VERSION}', ' End ', '<' * 10, '\n')


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
                # #print(projects['name'], "id: ", projects['id'])
                root_asset_id = projects['root_asset_id']
                # #print("root_asset_id: ", root_asset_id)
                project_id = projects['id']
                # #print("project_id: ", project_id)
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
        # #print(query)
        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # #print(data)
        type = []
        id = []
        parent_id = []
        for item in data:
            # #print(item[('name'))
            type = item['type']
            # #print(item['type'])
            id = item['id']
            # #print(item['id'])
            parent_id = item['parent_id']
            # #print(item['parent_id'])
            break
        return(type,id,parent_id)

    def get_selection_comments(self, id):

        url = "https://api.frame.io/v2/assets/" + id + "/comments"

        query = {
        "include": "replies"
        }

        response = requests.get(url, headers=self.headers, params=query)

        data = response.json()
        # #print(data)
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

def get_timeline_custom_ui_actions():

    return [
        {
            'name': 'UC FrameIO',
            'actions': [
                {
                    'name': 'Get Comments',
                    'order': 0,
                    'isVisible': scope_segment,
                    'separator': 'below',
                    'execute': frame_io_get_comments,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'UC FrameIO',
            'actions': [
                {
                    'name': 'Get Comments',
                    'order': 2,
                    'isVisible': scope_clip,
                    'separator': 'above',
                    'execute': frame_io_get_comments,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
