'''
Script Name: batch renamer
Script Version: 2.0.1
Flame Version: 2024.2 and above
Written by: John Geehreng
Creation Date: 10.01.21
Update Date: 01.28.26

Custom Action Type: Media Panel

Usage: Right click a selection of clips or sequences and look for UC Renamers -> Batch Renamer

Description: Renames a bunch of clips or sequences based on text input and tokens.

To install: Copy script into /opt/Autodesk/shared/python/batch_renamer

Updates:
    01.28.26 - v2.0.1 - Changed SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    01.28.26 - v2.0.0 - Updated for Flame 2024.2 and above. Updated UI for pyflame lib v5.1.1
    02.28.25 - v1.9   - Added YYMMDD token
    09.18.24 - v1.8   - Added Reel Group Name and Desktop Name options.
    05.15.24 - V1.7   - Added Date Option
    12.13.23 - v1.6   - Updated for pyflame lib v2. Start updates for Flame 2025.
    06.05.23 - v1.5   - added "Count"
    05.09.23 - v1.4   - added ability to keep current name
    09.08.22 - v1.3   - 2023.2 ordering (commented out for Logik Portal)
    04.15.22 - v1.2   - UI adjustments for 2023

'''
import flame
import xml.etree.ElementTree as ET
import os
import re
import datetime
from lib.pyflame_lib_batch_renamer import *

SCRIPT_VERSION = 'v2.0.1'
SCRIPT_NAME = 'Batch Renamer'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------#
# Main Script

class batch_rename(object):

    def __init__(self, selection):
        

        print ('>' * 20, 'batch renamer %s' % SCRIPT_VERSION, '<' * 20, '\n')

        # Paths

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        # Load config file

        self.config()

        # Open main window

        self.main_window(selection)

    def config(self):

        def get_config_values():

            # Get settings from saved config.xml file

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            # Assign values from config file to variables

            for setting in root.iter('batch_renamer_settings'):
                self.naming_convention = setting.find('naming_convention').text
                # self.setting_02 = setting.find('setting_02').text

            print ('>>> config loaded <<<\n')

        def create_config_file():

            # Create config.xml file with default settings

            if not os.path.isdir(self.config_path):
                try:
                    os.makedirs(self.config_path)
                except:
                    flame.messages.show_in_dialog(
                        title = "f'{SCRIPT_NAME}: Permissions Error",
                        message = f'Unable to create folder: {self.config_path}<br>Check folder permissions',
                        type = "error",
                        buttons = ["Ok"])
            if not os.path.isfile(self.config_xml):
                print ('>>> config file does not exist, creating new config file <<<\n')

                # Add default settings here

                config = """
                        <settings>
                            <batch_renamer_settings>
                                <naming_convention>Some Value Here</naming_convention>
                            </batch_renamer_settings>
                        </settings>
                        """

                # Save settings to config.xml file

                with open(self.config_xml, 'a') as config_file:
                    config_file.write(config)
                    config_file.close()

        if os.path.isfile(self.config_xml):
            get_config_values()
        else:
            create_config_file()
            if os.path.isfile(self.config_xml):
                get_config_values()

    def main_window(self,selection):
        dateandtime = datetime.datetime.now()
        self.today = (dateandtime.strftime("%Y-%m-%d"))
        self.us_date = (dateandtime.strftime("%m%d%y"))
        self.ymd_date = (dateandtime.strftime("%y%m%d"))

        def save_config():

            # Save settings to config file

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            # Replace values in config file with values from UI

            naming_convention = root.find('.//naming_convention')
            naming_convention.text = self.naming_convention_lineedit.text

            xml_tree.write(self.config_xml)

            print ('>>> config saved <<<\n')

            self.window.close()
            rename()
            print ('>' * 20, 'batch renamer %s' % SCRIPT_VERSION, '<' * 20, '\n')
            

        def rename():

            # print ("*" * 40)
            self.naming_convention_entry = self.naming_convention_lineedit.text
            print ("naming_convention_entry: " + self.naming_convention_entry)
            # print ("*" * 40)
            print ("\n"*1)
            count = 0
            for item in selection:
                print ("*" * 50)
                # print ("I think this is working...")
                count += int(1)
                count_padded = '%02d' % count
                seq_name = str(item.name)[(1):-(1)]
                print ("Selection Name: ", seq_name)
                try:
                    frames = int(item.duration.frame)
                except:
                    frames = 0
                # print ("Clip Length: " + str(frames) + " frames")
                resolution = str(item.width) + "x" + str(item.height)
                # print ("Resolution: " + str(resolution) )
                # print ("Framerate: " + str(item.frame_rate))

                #Get Aspect Ratio
                aspect_ratio = resolution
                seq_format = "format"
                if resolution == '1920x1080':
                    aspect_ratio = "16x9"
                    seq_format = "HD"
                if resolution == '3840x2160':
                    aspect_ratio = "16x9"
                    seq_format = "UHD"
                if resolution == '1080x1080':
                    aspect_ratio = "1x1"
                    seq_format = "square"
                if resolution == '1280x1920':
                    aspect_ratio = "2x3"
                if resolution == '1080x1620':
                    aspect_ratio = "2x3"
                if resolution == '1080x1350':
                    aspect_ratio = "4x5"
                if resolution == '1080x1920':
                    aspect_ratio = "9x16"
                    seq_format = "vertical"
                if resolution == '2560 x 1440':
                    aspect_ratio = "16x9"
                    seq_format = "1440P"
                
                # print ("Aspect Ratio is: " + str(aspect_ratio) )

                #Get duration in seconds
                try:
                    framerate = str((item.frame_rate).split(" fps")[0])
                    duration = '%02d' % (int(frames / float(framerate)))
                except:
                    framerate = 24
                    duration = 0
                # print ("Duration: " + str(duration) + " seconds")

                #get parent name
                reel_name = str(item.parent.name)[(1):-(1)]
                reel_group_name = str(item.parent.parent.name)[(1):-(1)]
                desktop_name = str(item.parent.parent.parent.name)[(1):-(1)]
                # print ("Parent Name: " + reel_name)

                naming_convention = re.sub('<reel_name>', reel_name, str(self.naming_convention_entry))
                naming_convention = re.sub('<reel_group_name>', reel_group_name, naming_convention)
                naming_convention = re.sub('<desktop_name>', desktop_name, naming_convention)
                naming_convention = re.sub('<date>', str(self.today), naming_convention)
                naming_convention = re.sub('<us_date>', str(self.us_date), naming_convention)
                naming_convention = re.sub('<ymd_date>', str(self.ymd_date), naming_convention)
                naming_convention = re.sub('<current_name>', str(seq_name), naming_convention)
                naming_convention = re.sub('<duration>', str(duration), naming_convention)
                naming_convention = re.sub('<aspect_ratio>', str(aspect_ratio), naming_convention)
                naming_convention = re.sub('<resolution>', str(resolution), naming_convention)
                naming_convention = re.sub('<framerate>', str(framerate), naming_convention)
                naming_convention = re.sub('<format>', str(seq_format), naming_convention)
                naming_convention = re.sub('<count>', str(count_padded), naming_convention)

                print ("Naming Convention Name: " + str(naming_convention))
                item.name = naming_convention
                print ("*" * 50,"\n"*1)
        
        def update_preview():
            self.naming_convention_entry = self.naming_convention_lineedit.text
            count = 0
            for item in selection:
                count += int(1)
                count_padded = '%02d' % count
                seq_name = str(item.name)[(1):-(1)]
                try:
                    frames = int(item.duration.frame)
                except:
                    frames = 0
                resolution = str(item.width) + "x" + str(item.height)

                #Get Aspect Ratio
                aspect_ratio = resolution
                seq_format = "format"
                if resolution == '1920x1080':
                    aspect_ratio = "16x9"
                    seq_format = "HD"
                if resolution == '3840x2160':
                    aspect_ratio = "16x9"
                    seq_format = "UHD"
                if resolution == '1080x1080':
                    aspect_ratio = "1x1"
                    seq_format = "square"
                if resolution == '1280x1920':
                    aspect_ratio = "2x3"
                if resolution == '1080x1620':
                    aspect_ratio = "2x3"
                if resolution == '1080x1350':
                    aspect_ratio = "4x5"
                if resolution == '1080x1920':
                    aspect_ratio = "9x16"
                    seq_format = "vertical"
                if resolution == '2560 x 1440':
                    aspect_ratio = "16x9"
                    seq_format = "1440P"

                #Get duration in seconds
                try:
                    framerate = str((item.frame_rate).split(" fps")[0])
                    duration = '%02d' % (int(frames / float(framerate)))
                except:
                    framerate = 24
                    duration = 0

                #get parents name
                reel_name = str(item.parent.name)[(1):-(1)]
                reel_group_name = str(item.parent.parent.name)[(1):-(1)]
                desktop_name = str(item.parent.parent.parent.name)[(1):-(1)]

                naming_convention = re.sub('<reel_name>', reel_name, str(self.naming_convention_entry))
                naming_convention = re.sub('<reel_group_name>', reel_group_name, naming_convention)
                naming_convention = re.sub('<desktop_name>', desktop_name, naming_convention)
                naming_convention = re.sub('<date>', str(self.today), naming_convention)
                naming_convention = re.sub('<us_date>', str(self.us_date), naming_convention)
                naming_convention = re.sub('<ymd_date>', str(self.ymd_date), naming_convention)
                naming_convention = re.sub('<current_name>', str(seq_name), naming_convention)
                naming_convention = re.sub('<duration>', str(duration), naming_convention)
                naming_convention = re.sub('<aspect_ratio>', str(aspect_ratio), naming_convention)
                naming_convention = re.sub('<resolution>', str(resolution), naming_convention)
                naming_convention = re.sub('<framerate>', str(framerate), naming_convention)
                naming_convention = re.sub('<format>', str(seq_format), naming_convention)
                naming_convention = re.sub('<count>', str(count_padded), naming_convention)

                self.preview_bg_label.setText(naming_convention)
                break

        # Window=
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            grid_layout_columns=3,
            grid_layout_rows=4,
            grid_layout_adjust_column_widths={1: 660},
            parent=None
            )

        # Labels
        self.label = PyFlameLabel(text='Naming Convention', style=Style.UNDERLINE)
        self.preview_label = PyFlameLabel(text='Preview', style=Style.UNDERLINE)
        self.preview_bg_label = PyFlameLabel(text='', style=Style.BACKGROUND)
        self.blank_label = PyFlameLabel(text='', style=Style.NORMAL)

        # LineEdits
        self.naming_convention_lineedit = PyFlameEntry(text=self.naming_convention, text_changed=update_preview)
                
        # Token Button
        self.token_dict = {'Current Name': '<current_name>',
                             'Reel Name': '<reel_name>',
                             'Reel Group Name': '<reel_group_name>',
                             'Desktop Name': '<desktop_name>',
                             'Duration': '<duration>',
                             'Aspect Rato': '<aspect_ratio>',
                             'Resolution': '<resolution>',
                             'Date YYYY-MM-DD': '<date>',
                             'Date MMDDYY': '<us_date>',
                             'Date YYMMDD': '<ymd_date>',
                             'Framerate': '<framerate>',
                             'Master': '_Master',
                             'Generic': '_Generic',
                             'Count': '<count>'}
        self.setup_token_push_button = PyFlameTokenMenu(text='Add Token', token_dict=self.token_dict, token_dest=self.naming_convention_lineedit)
        
        # Buttons
        self.rename_btn = PyFlameButton(text='Rename',  connect=save_config,color=Color.BLUE)
        self.cancel_btn = PyFlameButton(text='Cancel',  connect=self.window.close)

        update_preview()

        #------------------------------------#

        # Window Layout

        self.window.grid_layout.addWidget(self.label, 0, 0)
        self.window.grid_layout.addWidget(self.naming_convention_lineedit, 0, 1)
        self.window.grid_layout.addWidget(self.setup_token_push_button, 0, 2)

        self.window.grid_layout.addWidget(self.preview_label, 1, 0)
        self.window.grid_layout.addWidget(self.preview_bg_label, 1, 1, 1 , 2) # row 0, column 0, row span 1, column span 2

        # self.window.grid_layout.addWidget(self.blank_label, 2, 0)

        self.window.grid_layout.addWidget(self.cancel_btn, 3, 0)
        self.window.grid_layout.addWidget(self.rename_btn, 3, 2)

        self.window.show()
       

##########################################
#Scopes
def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


############################

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'UC Renamers',
            'order': 6,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    # 'order': 0,
                    'execute': batch_rename,
                    'minimumVersion': '2024.2'
                }
            ]
        }
    ]