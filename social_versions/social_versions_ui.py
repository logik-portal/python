"""
Script Name: social versions ui
Script Version: 1.0.2
Flame Version: 2023.2
Written by: Kyle Obley (info@kyleobley.com), UI by John Geehreng
Creation Date: 02.08.25
Update Date: 02.13.25

Script Type: MediaPanel

Description:

    Create new timelines with various resolutions

Menus:

    Media Panel -> Social  -> Logik Portal Script Setup -> Setup

To install:

    Copy script into /opt/Autodesk/shared/python/social_versions or wherever you keep your scripts

Updates:
02.13.25 - v1.0.2 - Reversed width and height
02.10.25 - v1.0.1 - Tweaked Labels
02.08.25 - v1.0.0 - Initial release

"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame

from pyflame_lib_social_versions_ui import *
from social_versions import create_timeline

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Social Versions UI'
SCRIPT_VERSION = 'v1.0.2'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
FOLDER_NAME = 'Social Versions'

#-------------------------------------
# [Main Script]
#-------------------------------------

class SocialVersionsUI():

    def __init__(self, selection) -> None:

        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')

        # # Check script path, if path is incorrect, stop script.
        # if not pyflame.verify_script_install():
        #     return

        # Create/Load config file settings.
        self.load_config()
        
        # Define selection
        self.selection = selection
        
        # Open main window
        self.main_window()
 
        # Check active buttons
        self.check_active_buttons()

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
                'setting_01': '1x1',
                'setting_02': '4x5',
                'setting_03': '2x3',
                'setting_04': '9x16',
                'setting_05': 'UHD',
                'button_01': True,
                'button_02': True,
                'button_03': False,
                'button_04': True,
                'button_05': False,
                'x_res_01': 1080,
                'x_res_02': 1080,
                'x_res_03': 1080,
                'x_res_04': 1080,
                'x_res_05': 3840,
                'y_res_01': 1080,
                'y_res_02': 1350,
                'y_res_03': 1620,
                'y_res_04': 1920,
                'y_res_05': 2160,
                },
            )

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for script.
        """

        #-------------------------------------
        # [Window Elements]
        #-------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.create_timelines,
            grid_layout_columns=4,
            grid_layout_rows=7,
            # grid_layout_adjust_column_widths={0: 20}
            )

        # Top Labels
        self.label1 = PyFlameLabel(text='Active', align=Align.CENTER)
        self.label2 = PyFlameLabel(text='X Res', align=Align.CENTER)
        self.label3 = PyFlameLabel(text='Y Res', align=Align.CENTER)
        self.label4 = PyFlameLabel(text='Name', align=Align.CENTER)

        # Row 1
        self.check1 = PyFlamePushButton(text='         Version 1', button_checked=self.settings.button_01, connect=self.check_active_buttons)
        self.xslider1 = PyFlameSlider(start_value=self.settings.x_res_01, min_value=256, max_value=9000, rate=1)
        self.yslider1 = PyFlameSlider(start_value=self.settings.y_res_01, min_value=256, max_value=9000, rate=1)
        self.entry1 = PyFlameEntry(text=self.settings.setting_01)

        # Row 2
        self.check2 = PyFlamePushButton(text='         Version 2', button_checked=self.settings.button_02, connect=self.check_active_buttons)
        self.xslider2 = PyFlameSlider(start_value=self.settings.x_res_02, min_value=256, max_value=9000, rate=1)
        self.yslider2 = PyFlameSlider(start_value=self.settings.y_res_02, min_value=256, max_value=9000, rate=1)
        self.entry2 = PyFlameEntry(text=self.settings.setting_02)

        # Row 3
        self.check3 = PyFlamePushButton(text='         Version 3', button_checked=self.settings.button_03, connect=self.check_active_buttons)
        self.xslider3 = PyFlameSlider(start_value=self.settings.x_res_03, min_value=256, max_value=9000, rate=1)
        self.yslider3 = PyFlameSlider(start_value=self.settings.y_res_03, min_value=256, max_value=9000, rate=1)
        self.entry3 = PyFlameEntry(text=self.settings.setting_03)

        # Row 4
        self.check4 = PyFlamePushButton(text='         Version 4', button_checked=self.settings.button_04, connect=self.check_active_buttons)
        self.xslider4 = PyFlameSlider(start_value=self.settings.x_res_04, min_value=256, max_value=9000, rate=1)
        self.yslider4 = PyFlameSlider(start_value=self.settings.y_res_04, min_value=256, max_value=9000, rate=1)
        self.entry4 = PyFlameEntry(text=self.settings.setting_04)

        # Row 5
        self.check5 = PyFlamePushButton(text='         Version 5', button_checked=self.settings.button_05, connect=self.check_active_buttons)
        self.xslider5 = PyFlameSlider(start_value=self.settings.x_res_05, min_value=256, max_value=9000, rate=1)
        self.yslider5 = PyFlameSlider(start_value=self.settings.y_res_05, min_value=256, max_value=9000, rate=1)
        self.entry5 = PyFlameEntry(text=self.settings.setting_05)

        # Buttons
        self.run_button = PyFlameButton(
            text='Run',
            connect=self.create_timelines,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        # Top Labels
        self.window.grid_layout.addWidget(self.label1, 0, 0)
        self.window.grid_layout.addWidget(self.label2, 0, 1)
        self.window.grid_layout.addWidget(self.label3, 0, 2)
        self.window.grid_layout.addWidget(self.label4, 0, 3)

        # Row 1
        self.window.grid_layout.addWidget(self.check1, 1, 0)
        self.window.grid_layout.addWidget(self.xslider1, 1, 1)
        self.window.grid_layout.addWidget(self.yslider1, 1, 2)
        self.window.grid_layout.addWidget(self.entry1, 1, 3)

        # Row 2
        self.window.grid_layout.addWidget(self.check2, 2, 0)
        self.window.grid_layout.addWidget(self.xslider2, 2, 1)
        self.window.grid_layout.addWidget(self.yslider2, 2, 2)
        self.window.grid_layout.addWidget(self.entry2, 2, 3)

        # Row 3
        self.window.grid_layout.addWidget(self.check3, 3, 0)
        self.window.grid_layout.addWidget(self.xslider3, 3, 1)
        self.window.grid_layout.addWidget(self.yslider3, 3, 2)
        self.window.grid_layout.addWidget(self.entry3, 3, 3)

        # Row 4
        self.window.grid_layout.addWidget(self.check4, 4, 0)
        self.window.grid_layout.addWidget(self.xslider4, 4, 1)
        self.window.grid_layout.addWidget(self.yslider4, 4, 2)
        self.window.grid_layout.addWidget(self.entry4, 4, 3)

        # Row 5
        self.window.grid_layout.addWidget(self.check5, 5, 0)
        self.window.grid_layout.addWidget(self.xslider5, 5, 1)
        self.window.grid_layout.addWidget(self.yslider5, 5, 2)
        self.window.grid_layout.addWidget(self.entry5, 5, 3)

        # Buttons
        self.window.grid_layout.addWidget(self.cancel_button, 7, 2)
        self.window.grid_layout.addWidget(self.run_button, 7, 3)

    def check_active_buttons(self):
        elements = [
            (self.check1, [self.xslider1, self.yslider1, self.entry1]),
            (self.check2, [self.xslider2, self.yslider2, self.entry2]),
            (self.check3, [self.xslider3, self.yslider3, self.entry3]),
            (self.check4, [self.xslider4, self.yslider4, self.entry4]),
            (self.check5, [self.xslider5, self.yslider5, self.entry5]),
        ]

        for checkbox, widgets in elements:
            enabled = checkbox.isChecked()
            for widget in widgets:
                widget.setEnabled(enabled)

    def create_timelines(self):
            elements = [
            (self.check1, self.xslider1, self.yslider1, self.entry1),
            (self.check2, self.xslider2, self.yslider2, self.entry2),
            (self.check3, self.xslider3, self.yslider3, self.entry3),
            (self.check4, self.xslider4, self.yslider4, self.entry4),
            (self.check5, self.xslider5, self.yslider5, self.entry5),
            ]

            for check, xslider, yslider, entry in elements:
                if check.isChecked():
                    create_timeline(self.selection, xslider.value(), yslider.value(), entry.text())

            self.save_config()
        
    def save_config(self) -> None:
        """
        Save settings to config file and close window.
        """

        self.settings.save_config(
            config_values={
                'setting_01': self.entry1.text(),
                'setting_02': self.entry2.text(),
                'setting_03': self.entry3.text(),
                'setting_04': self.entry4.text(),
                'setting_05': self.entry5.text(),
                'button_01': self.check1.isChecked(),
                'button_02': self.check2.isChecked(),
                'button_03': self.check3.isChecked(),
                'button_04': self.check4.isChecked(),
                'button_05': self.check5.isChecked(),
                'x_res_01': self.xslider1.value(),
                'x_res_02': self.xslider2.value(),
                'x_res_03': self.xslider3.value(),
                'x_res_04': self.xslider4.value(),
                'x_res_05': self.xslider5.value(),
                'y_res_01': self.yslider1.value(),
                'y_res_02': self.yslider2.value(),
                'y_res_03': self.yslider3.value(),
                'y_res_04': self.yslider4.value(),
                'y_res_05': self.yslider5.value(),
                }
            )

        self.window.close()

        # PyFlameMessageWindow(
        #     message='Social Versions made.',
        #     )
        

#-------------------------------------
# [Scopes]
#-------------------------------------

def sequence_selected(selection):
    for item in selection:
        if isinstance(item, (flame.PySequence)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [

        {
            'name': FOLDER_NAME,
            # 'hierarchy': ['Logik'],
            # 'order': 2,
            'actions': [
               {
                    'name': SCRIPT_NAME,
                    'execute': SocialVersionsUI,
                    'order': 1,
                    'separator': 'below',
                    'isVisible': sequence_selected,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
