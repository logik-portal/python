"""
Script Name: copy actions from
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 01.16.24
Update Date: 01.28.26

Custom Action Type: Timeline

Description:

    Mass Copy Actions From other Tracks

Menus:

    Flame 2025+:

        Timeline -> Copy Actions -> Copy From

To install:

    Copy script into /opt/Autodesk/shared/python/copy_actions or appropriate shared python folder

Updates:

    v1.0.0 01.28.26

        Fixed issue with incorrect project tmp path in Flame 2026+ again. Pyflame lib update. Turned off print statements.

    v0.6.2 10.31.25

        Fixed issue with incorrect project tmp path in Flame 2026+ Turned off script path check

    v0.6.1 10.28.25

        Removed .action extension from action_path

    v0.6.0 07.10.25

        Fixed an issue where it was behaving more like Copy To

    v0.5 12.11.24

        Delete TL Action, create a new one, and then load the saved action - seems to fix the action xml bug.

    v0.4 10.15.24

        Adjusted action_path for 2025.1.2

    v0.3 01.19.24

        Added limits to the sliders based on the number of tracks

    v0.2 01.18.24

        Added a check for valid 'action_path'

    v0.1 01.16.24

        Inception
"""

# ---------------------------------------- #
# Imports

import os
import flame
from lib.pyflame_lib_copy_actions import *

#-------------------------------------#
# Main Script

SCRIPT_NAME = 'Copy Actions From'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

class CopyActions():

    def __init__(self, selection):

        # print('\n')
        # print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        self.selection = selection
        
        self.project_name = flame.projects.current_project.name
        self.simple_flame_version = flame.get_version().split('.')[0]
        
        if self.simple_flame_version <= '2026':
            full_project_path = flame.projects.current_project.project_folder
            self.project_tmp_path = re.sub(r"^/hosts/[^/]+", "", full_project_path)
            self.action_path = f"{self.project_tmp_path}/setups/action/flame"
        else:
            self.action_path = f"/opt/Autodesk/project/{self.project_name}/tmp"

        self.selection = selection
        
        # Half the Number of Tracks for the Slider UI
        for item in self.selection:
            version = item.parent.parent
            break
        self.half_nb_of_tracks = int(len(version.tracks) / 2) #* -1
        self.nb_of_tracks = int(len(version.tracks) -1 )
        # print ("Half the Number of Tracks: ", self.half_nb_of_tracks)

        # Open main window
        self.main_window()

    def copy_actions(self):

        if not os.path.exists(self.action_path):
            try:
                os.makedirs(self.action_path)
                action_path = self.action_path + '/copy_from.action_node'
            except:
                action_path = '/var/tmp/copy_from.action_node'

        # print(f"Action Path: {action_path}")

        for item in self.selection:
            clip = item.parent.parent.parent
            break

        version_count = -1
        track_target = self.count_slider.value
        
        for version in clip.versions:
            version_count = version_count + 1
            # print ("Version: ", version)
            track_count = -1
            for track in version.tracks:
                # print ("Track: ", track)
                segment_count = -1
                track_count = track_count + 1
                for segment in track.segments:
                    # print ("Segment: ", segment)
                    segment_count = segment_count + 1
                    # print ("Segment Count: ", segment_count)
                    if segment in self.selection:
                        
                        source_segments = clip.versions[int(version_count)].tracks[int(track_count)]
                        target_segments = clip.versions[int(version_count)].tracks[int(track_count+track_target)]
                        

                        if len(source_segments.segments) == len(target_segments.segments):
                            target_segment = clip.versions[int(version_count)].tracks[int(track_count+track_target)].segments[segment_count]
                            
                            for tlfx in target_segment.effects:
                                if tlfx.type == 'Action':
                                    tlfx.save_setup(action_path)

                                    for tlfx in segment.effects:
                                        if tlfx.type == 'Action':
                                            flame.delete(tlfx)
                                            # action_fx = target_segment.create_effect('Action')
                                            action_fx = segment.create_effect('Action')
                                            action_fx.load_setup(action_path)
                                    # segment.colour = (50,50,50)

                        else:
                            self.window.close()
                            PyFlameMessageWindow(title='Segment Mismatch', message='Relative tracks need to have the same amount of Segments.', type=MessageType.ERROR )
                            return
        
        # print('\n')
        # print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        self.window.close()

    def main_window(self):

        #------------------------------------#
        # Window Elements

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            grid_layout_columns=2,
            grid_layout_rows=3,
            return_pressed=self.copy_actions,
            grid_layout_adjust_column_widths={1: 180, 0: 180},
            parent=None
            )

        # Labels
        self.label = PyFlameLabel(
            text='Copy From Relative Tracks',
            style=Style.UNDERLINE
            )
        
        # Slider
        self.count_slider = PyFlameSlider(
            start_value=self.half_nb_of_tracks,
            min_value=-self.nb_of_tracks,
            max_value=self.nb_of_tracks
            )

        # Buttons
        self.copy_btn = PyFlameButton(
            text='Copy ',
            connect=self.copy_actions,
            color=Color.BLUE,
            )
        self.cancel_btn = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #------------------------------------#
        # Window Layout

        self.window.grid_layout.addWidget(self.label, 1, 0)
        self.window.grid_layout.addWidget(self.count_slider, 1, 1)

        self.window.grid_layout.addWidget(self.cancel_btn, 6, 0)
        self.window.grid_layout.addWidget(self.copy_btn, 6, 1)
        
        self.window.show()

# ---------------------------------------- #
# Scopes

def scope_library(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary)):
            return True
    return False

#-------------------------------------#
# Flame Menus

def get_timeline_custom_ui_actions():

    return [
        {
            'hierarchy': ['Copy Actions'],
            'actions': [
               {
                    'name': 'Copy From',
                    'execute': CopyActions,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
