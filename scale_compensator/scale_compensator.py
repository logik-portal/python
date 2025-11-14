"""
Script Name: scale compensator
Script Version: 1.1.1
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 11.18.23
Update Date: 10.22.25

Script Type: Action and Timeline

Description:

    Compensate for different resolutions. In Action, you can generate Axes. In Timeline, you can color code a selection.

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.1.1 10.22.25
        - Started using flame.projects.current_project.project_folder to determine where to save/load json's

    v1.1 01.10.25
        - Fixed odd issue when adusting the offline vs online sliders.

    v1.0 12.27.24
        - Changed script path, started using json file with aspect ratios and resolutions

    v0.6 01.02.24
        - Fixed some miscalcuations and errors

    v0.5 12.13.23
        - Add Anamorphic Options. Fixed duplicated variables. Updates for Flame 2025.

    v0.4 12.05.23
        - Updated for pyflame lib v2.

    v0.3 11.28.23
        - UI Adjustments and Minor Code Cleanup

    v0.2 11.22.23
        - Added Offline Res and Online Res Compensation + Combo Button

    v0.6 01.02.24
        - Fixed some miscalcuations and errors

    v0.5 12.13.23
        - Add Anamorphic Options. Fixed duplicated variables. Updates for Flame 2025.

    v0.4 12.05.23
        - Updated for pyflame lib v2.

    v0.3 11.28.23
        - UI Adjustments and Minor Code Cleanup

    v0.2 11.22.23
        - Added Offline Res and Online Res Compensation + Combo Button
"""

import flame
import re
import os
import json
import traceback
from pathlib import Path
import xml.etree.ElementTree as ET
from pyflame_lib_scale_compensator import *

SCRIPT_NAME = 'Scale Compensator'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
SCRIPT_VERSION = 'v1.1.1'

#-------------------------------------#
# Main Script

class ScaleCompensator(object):

    def __init__(self, selection):

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        # Load config file
        self.settings = PyFlameConfig(
            script_name=SCRIPT_NAME,
            script_path=SCRIPT_PATH,
            config_values={
                'proxy_x_res': '1920',
                'proxy_y_res': '1080',
                'full_x_res': '1920',
                'full_y_res': '1080',
                'offline_x_res': '1920',
                'offline_y_res': '1080',
                'online_x_res': '1920',
                'online_y_res': '1080',
                'anamorphic_footage': 'False',
                'pixel_ratio_value': '2',
                'combo_scale': '100'
                }
            )
        # # Paths

        # Get host node
        self.host_node = flame.batch.current_node.get_value()
        self.host_node_type = str(self.host_node.type)[1:-1]

        # Open main window
        self.main_window()

    def catch_exception(method):
        def wrapper(self,*args,**kwargs):
            try:
                return method(self,*args,**kwargs)
            except:
                traceback.print_exc()
        return wrapper

    @catch_exception
    def create_axis(self):
            scaled_axis = self.host_node.create_node('Axis')
            axis_name = f"scl_for_{self.full_x_res_slider.text()}x{self.full_y_res_slider.text()}".replace(".", "_")
            if self.anamorphic_btn.isChecked():
                 axis_name = f'{axis_name}_ana'
            else:
                pass
            try:
                scaled_axis.name = axis_name
            except:
                flame.delete(scaled_axis)
                error_mesage = f'An axis with a scale of {self.scale_calculation_bg_label.text()} already exists. Please enter new values.'
                pyflame.message_print(SCRIPT_NAME, error_mesage)
                PyFlameMessageWindow(
                    message=error_mesage,
                    script_name=SCRIPT_NAME,
                    type=MessageType.ERROR
                    )
                return
            scaled_axis.pos_y = 190

            # print("Axis Attributes: ", scaled_axis.attributes)

            if self.anamorphic_btn.isChecked():
                scaled_axis.scale = ((self.proxy_res_x / self.full_x_res)*100,((self.proxy_res_x / self.full_x_res)*100)/self.pixel_ratio_slider.get_value(), 0)

            else:
                scaled_axis.scale = (self.scale_factor_calculation, self.scale_factor_calculation, 0)

    @catch_exception
    def use_resolution_list(self):

            # check for resolution list
            project_name = flame.projects.current_project.name

            # Specify file path
            project_name = flame.projects.current_project.name
            # res_file_location = (f"/opt/Autodesk/project/{project_name}/tmp")

            simple_flame_version = flame.get_version().split('.')[0]

            if simple_flame_version <= '2026':
                full_project_path = flame.projects.current_project.project_folder
                project_tmp_path = re.sub(r"^/hosts/[^/]+", "", full_project_path) + '/tmp'
                json_path = Path(f"{project_tmp_path}/scale_compensator_res_list.json")
            else:
                json_path = Path(f"/opt/Autodesk/project/{project_name}/tmp/scale_compensator_res_list.json")

            if not os.path.isfile(json_path):
                self.window.close()
                flame.messages.show_in_dialog(
                            title = "Error",
                            message = 'You need to generate the Scale Compensator Resolution List using UC Timeline -> Build Resolution List.',
                            type = "error",
                            buttons = ["Ok"],
                            cancel_button = "Cancel")
                return

            # Read the JSON file
            with json_path.open("r") as json_file:
                loaded_data = json.load(json_file)

            proxy_aspect_ratio = self.proxy_res_x / self.proxy_res_y
            vertical_position = 190
            horizontal_position = 190

            # Access items
            for item in loaded_data["items"]:
                # print(f"ID: {item['id']}")
                resolution = str({item['resolution']})[2:-2]
                # print(f"Resolution: {resolution}")
                json_aspect_ratio = float(str({item['aspect_ratio']})[1:-1])
                # print(f"Aspect Ratio: {json_aspect_ratio}")
                # print('\n')

                full_x_res = int(resolution.split('x')[0])
                full_y_res = int(resolution.split('x')[1])
                full_res_aspect_ratio = round(full_x_res / full_y_res, 3)
                horizontal_position = horizontal_position + 190
                scaled_axis = self.host_node.create_node('Axis')
                axis_name = f"scl_for_{resolution}"

                if json_aspect_ratio > float(full_res_aspect_ratio):
                    axis_name = f'{axis_name}_ana'
                    anamorphic_check = True
                else:
                    anamorphic_check = False
                    pass
                try:
                    scaled_axis.name = axis_name
                except:
                    flame.delete(scaled_axis)
                    error_mesage = f'An axis name "scl_for_{resolution}" already exists.'
                    pyflame.message_print(SCRIPT_NAME, error_mesage)
                    PyFlameMessageWindow(
                        message=error_mesage,
                        script_name=SCRIPT_NAME,
                        type=MessageType.ERROR
                        )
                    continue

                scaled_axis.pos_y = vertical_position
                scaled_axis.pos_x = horizontal_position

                if anamorphic_check == True:
                    scale_factor_calculation = (self.proxy_res_x / full_x_res)*100
                    scale_y_factor_calculation = scale_factor_calculation*(1/json_aspect_ratio)
                    scaled_axis.scale = (scale_factor_calculation,scale_y_factor_calculation, 0)

                elif json_aspect_ratio >= proxy_aspect_ratio:
                    scale_factor_calculation = (self.proxy_res_x / full_x_res)*100
                else:
                    scale_factor_calculation = (self.proxy_res_y / full_y_res)*100

                if anamorphic_check == False:
                    scaled_axis.scale = (scale_factor_calculation, scale_factor_calculation, 0)

    @catch_exception
    def create_off_vs_on_axis(self):
            # print("Creating Offline vs Online Compensation Axis")
            off_to_on_axis = self.host_node.create_node('Axis')
            axis_name = f"scl_for_{self.offline_x_res_slider.text()}x{self.offline_y_res_slider.text()}_to_{self.online_x_res_slider.text()}x{self.online_y_res_slider.text()}".replace(".", "_")
            if self.anamorphic_btn.isChecked():
                 axis_name = f'{axis_name}_ana'
            else:
                pass
            try:
                off_to_on_axis.name = axis_name
            except:
                flame.delete(off_to_on_axis)
                error_mesage = f'An axis with a scale of {self.off_vs_online_calculation_bg_label.text()} already exists. Please enter new values.'
                pyflame.message_print(SCRIPT_NAME, error_mesage)
                PyFlameMessageWindow(
                    message=error_mesage,
                    script_name=SCRIPT_NAME,
                    type=MessageType.ERROR
                    )
                return
            off_to_on_axis.pos_y = 190
            off_to_on_axis.scale = (float(self.off_vs_online_calculation_bg_label.text()),float(self.off_vs_online_calculation_bg_label.text()),0)

    @catch_exception
    def create_combo_axis(self):
                # print("Creating Combo Axis")
                combo_axis = self.host_node.create_node('Axis')
                axis_name = f"scl_{self.full_x_res_slider.text()}x{self.full_y_res_slider.text()}_in_{self.online_x_res_slider.text()}x{self.online_y_res_slider.text()}".replace(".", "_").replace("1080x1350", "4x5").replace("1080x1920", "9x16").replace("1280x1920", "2x3").replace("1920x1080", "16x9").replace("1080x1080", "1x1")
                if self.anamorphic_btn.isChecked():
                 axis_name = f'{axis_name}_ana'
                else:
                    pass
                try:
                    combo_axis.name = axis_name
                except:
                    flame.delete(combo_axis)
                    error_mesage = 'That axis already exits.  Please enter new values.'
                    pyflame.message_print(SCRIPT_NAME, error_mesage)
                    PyFlameMessageWindow(
                        message=error_mesage,
                        script_name=SCRIPT_NAME,
                        type=MessageType.ERROR
                        )
                    return
                combo_axis.pos_y = 190
                if self.anamorphic_btn.isChecked() == True:
                    combo_axis.scale = (self.combo_x_scale, self.combo_y_scale,0)
                else:
                    combo_scale = (float(self.off_vs_online_calculation_bg_label.text()) * float(self.scale_factor_calculation)) / 100
                    combo_axis.scale = (combo_scale,combo_scale,0)



    def update_auto_scale_multiplier(self):

        # Disable UI Elements
        if self.anamorphic_btn.isChecked():
            self.pixel_ratio_slider.show()
            self.pixel_ratio_label.setText('Pixel Ratio')
        else:
            self.pixel_ratio_label.setText('')
            self.pixel_ratio_slider.hide()

		# Calculate Scale Multiplier
        self.proxy_res_x = int(self.proxy_x_res_slider.text())
        self.proxy_res_y = int(self.proxy_y_res_slider.text())
        self.full_x_res = int(self.full_x_res_slider.text())
        self.full_y_res = int(self.full_y_res_slider.text())
        proxy_aspect_ratio = self.proxy_res_x / self.proxy_res_y
        full_res_aspect_ratio = self.full_x_res / self.full_y_res

        if self.anamorphic_btn.isChecked() == True:
            self.scale_factor_calculation = (self.proxy_res_x / self.full_x_res)*100
            self.scale_y_factor_calculation = self.scale_factor_calculation*(1/self.pixel_ratio_slider.get_value())
            self.anamorphic_scale_factor_calculation = f'({str(round(self.scale_factor_calculation,2))}, {str(round(self.scale_y_factor_calculation,2))})'
            self.scale_calculation_bg_label.setText(self.anamorphic_scale_factor_calculation)
        elif full_res_aspect_ratio >= proxy_aspect_ratio:
            self.scale_factor_calculation = (self.proxy_res_x / self.full_x_res)*100
            self.scale_calculation_bg_label.setText(str(round(self.scale_factor_calculation,2)))
        else:
            self.scale_factor_calculation = (self.proxy_res_y / self.full_y_res)*100
            self.scale_calculation_bg_label.setText(str(round(self.scale_factor_calculation,2)))

        self.update_combo_label()

    @catch_exception
    def update_on_vs_offline_scale(self, *args):
        print(f"Args: {args}")
        # Calculate Offline vs Online Scale Multiplier
        offline_x_res = int(self.offline_x_res_slider.text())
        # print("Offline X Res: ", offline_x_res)
        offline_y_res = int(self.offline_y_res_slider.text())
        # print("Offline Y Res: ", offline_y_res)
        online_x_res = int(self.online_x_res_slider.text())
        # print("Online X Res: ", online_x_res)
        online_y_res = int(self.online_y_res_slider.text())
        # print("Online Y Res: ", online_y_res)
        offline_aspect_ratio = offline_x_res / offline_y_res
        # print("Offline Aspect Ratio: ", offline_aspect_ratio)
        online_aspect_ratio = online_x_res / online_y_res
        # print("Online Aspect Ratio: ", online_aspect_ratio)

        if online_aspect_ratio >= offline_aspect_ratio:
            # print("Online Aspect Ratio is Greater")
            off_to_on_scale_factor_calculation = str(round((online_x_res / offline_x_res)*100,2))
        else:
            # print("Offline Aspect Ratio is Greater")
            off_to_on_scale_factor_calculation = str(round((online_y_res / offline_y_res)*100,2))

        # print("Offline vs Online Scale: ", off_to_on_scale_factor_calculation)
        self.off_vs_online_calculation_bg_label.setText(off_to_on_scale_factor_calculation)
        self.update_combo_label()


    @catch_exception
    def update_combo_label(self):
        if self.anamorphic_btn.isChecked() == True:
            self.combo_x_scale = (float(self.off_vs_online_calculation_bg_label.text()) * float(self.scale_factor_calculation)) / 100
            self.combo_y_scale = (float(self.off_vs_online_calculation_bg_label.text()) * float(self.scale_y_factor_calculation)) / 100
            self.combo_calculation_bg_label.setText(f'({str(round(self.combo_x_scale,2))}, {str(round(self.combo_y_scale,2))})')
        else:
            combo_scale = (float(self.off_vs_online_calculation_bg_label.text()) * float(self.scale_factor_calculation)) / 100
            combo_scale_rounded = str(round(combo_scale, 2))
            self.combo_calculation_bg_label.setText(combo_scale_rounded)

    @catch_exception
    def main_window(self):

        def save_config():

            # Save settings to config file
            self.settings.save_config(
                script_name=SCRIPT_NAME,
                script_path=SCRIPT_PATH,
                config_values={
                    'proxy_x_res': self.proxy_x_res_slider.text(),
                    'proxy_y_res': self.proxy_y_res_slider.text(),
                    'full_x_res': self.full_x_res_slider.text(),
                    'full_y_res': self.full_y_res_slider.text(),
                    'offline_x_res': self.offline_x_res_slider.text(),
                    'offline_y_res': self.offline_y_res_slider.text(),
                    'online_x_res': self.online_x_res_slider.text(),
                    'online_y_res': self.online_y_res_slider.text(),
                    'anamorphic_footage': str(self.anamorphic_btn.isChecked()),
                    'pixel_ratio_value': self.pixel_ratio_slider.text(),
                    'combo_scale': self.combo_calculation_bg_label.text(),
                    }
                )

            self.window.close()

        # Window
        self.window = PyFlameWindow(
            width=650,
            height=450,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            )

        # Labels

        self.proxy_x_res_label = PyFlameLabel(text='Proxy X Res', style=Style.UNDERLINE)
        self.proxy_y_res_label = PyFlameLabel(text='Proxy Y Res', style=Style.UNDERLINE)
        self.full_x_res_label = PyFlameLabel(text='Footage X Res', style=Style.UNDERLINE)
        self.full_y_res_label = PyFlameLabel(text='Footage Y Res', style=Style.UNDERLINE)
        self.scale_calculation_label = PyFlameLabel(text='Full Res to Proxy', style=Style.UNDERLINE)
        self.scale_calculation_bg_label = PyFlameLabel(text='100.00', style=Style.BACKGROUND, width=110)
        self.scale_calculation_bg_label.setAlignment(QtCore.Qt.AlignCenter)
        self.offline_x_res_label = PyFlameLabel(text='Offline X Res', style=Style.UNDERLINE)
        self.offline_y_res_label = PyFlameLabel(text='Offline Y Res', style=Style.UNDERLINE)
        self.online_x_res_label = PyFlameLabel(text='Online X Res', style=Style.UNDERLINE)
        self.online_y_res_label = PyFlameLabel(text='Online Y Res', style=Style.UNDERLINE)
        self.off_vs_online_calculation_label = PyFlameLabel(text='Offline to Online', style=Style.UNDERLINE)
        self.off_vs_online_calculation_bg_label = PyFlameLabel(text='100.00', style=Style.BACKGROUND, width=110,align=Align.CENTER)
        self.blank_label = PyFlameLabel(text='', style=Style.NORMAL,width=560)
        self.blank_label2 = PyFlameLabel(text='', style=Style.NORMAL)
        self.blank_label3 = PyFlameLabel(text='', style=Style.NORMAL)
        self.combo_label = PyFlameLabel(text='Compensate for Both', style=Style.UNDERLINE)
        self.combo_calculation_bg_label = PyFlameLabel(text=str(self.settings.combo_scale), style=Style.BACKGROUND, width=110,align=Align.CENTER)
        self.pixel_ratio_label = PyFlameLabel(text='Pixel Ratio', style=Style.UNDERLINE)

        # Sliders

        self.proxy_x_res_slider = PyFlameSlider(float(self.settings.proxy_x_res), 0, 15000, False)
        self.proxy_y_res_slider = PyFlameSlider(float(self.settings.proxy_y_res), 0, 15000, False)
        self.full_x_res_slider = PyFlameSlider(float(self.settings.full_x_res), 0, 15000, False)
        self.full_y_res_slider = PyFlameSlider(float(self.settings.full_y_res), 0, 15000, False)

        self.pixel_ratio_slider = PyFlameSlider(float(self.settings.pixel_ratio_value), .9, 3, True)

        self.offline_x_res_slider = PyFlameSlider(float(self.settings.offline_x_res), 0, 15000, False)
        self.offline_y_res_slider = PyFlameSlider(float(self.settings.offline_y_res), 0, 15000, False)
        self.online_x_res_slider = PyFlameSlider(float(self.settings.online_x_res), 0, 15000, False)
        self.online_y_res_slider = PyFlameSlider(float(self.settings.online_y_res), 0, 15000, False)

        # Slider updates
        self.full_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.full_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)

        self.pixel_ratio_slider.textChanged.connect(self.update_auto_scale_multiplier)

        self.offline_x_res_slider.textChanged.connect(self.update_on_vs_offline_scale)
        self.offline_y_res_slider.textChanged.connect(self.update_on_vs_offline_scale)
        self.online_x_res_slider.textChanged.connect(self.update_on_vs_offline_scale)
        self.online_y_res_slider.textChanged.connect(self.update_on_vs_offline_scale)

        # Buttons
        self.create_axis_btn = PyFlameButton(text='Create Axis', connect=self.create_axis)
        self.save_btn = PyFlameButton(text='Save and Close',  connect=save_config,color=Color.BLUE, width=110)
        self.cancel_btn = PyFlameButton(text='Close',  connect=self.window.close, width=110)
        self.create_off_vs_on_btn = PyFlameButton(text='Off to Online Axis',  connect=self.create_off_vs_on_axis, width=110)
        self.create_combo_axis_btn = PyFlameButton(text='Combo Axis',  connect=self.create_combo_axis, width=110)
        self.use_res_list_btn = PyFlameButton(text='Use Res List', connect=self.use_resolution_list, color=Color.BLUE, width=110)

        # PushButtons
        self.anamorphic_btn = PyFlamePushButton('  Anamorphic Footage',
            button_checked=self.settings.anamorphic_footage,
            connect=self.update_auto_scale_multiplier
            )
        self.anamorphic_btn.setToolTip('Enable for Anamorphic Footage.')

       # Update Calculations
        self.update_auto_scale_multiplier()
        self.update_on_vs_offline_scale()
        self.update_combo_label()

        #------------------------------------#

        # Window Layout

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
        grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
        try:
            grid_layout.setMargin(pyflame.gui_resize(10))
        except:
            grid_layout_margin = pyflame.gui_resize(10)
            grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

        grid_layout.addWidget(self.proxy_x_res_label, 1, 0)
        grid_layout.addWidget(self.proxy_x_res_slider, 1, 1)
        grid_layout.addWidget(self.proxy_y_res_label, 1, 2)
        grid_layout.addWidget(self.proxy_y_res_slider, 1, 3)

        grid_layout.addWidget(self.full_x_res_label, 2, 0)
        grid_layout.addWidget(self.full_x_res_slider, 2, 1)
        grid_layout.addWidget(self.full_y_res_label, 2, 2)
        grid_layout.addWidget(self.full_y_res_slider, 2, 3)

        grid_layout.addWidget(self.anamorphic_btn, 3, 0)
        grid_layout.addWidget(self.pixel_ratio_label, 3, 1)
        grid_layout.addWidget(self.pixel_ratio_slider, 3, 2)

        grid_layout.addWidget(self.scale_calculation_label, 4, 0)
        grid_layout.addWidget(self.scale_calculation_bg_label, 4, 1)
        grid_layout.addWidget(self.create_axis_btn, 4, 2)

        grid_layout.addWidget(self.blank_label, 5, 0)

        grid_layout.addWidget(self.offline_x_res_label, 6, 0)
        grid_layout.addWidget(self.offline_x_res_slider, 6, 1)
        grid_layout.addWidget(self.offline_y_res_label, 6, 2)
        grid_layout.addWidget(self.offline_y_res_slider, 6, 3)

        grid_layout.addWidget(self.online_x_res_label, 7, 0)
        grid_layout.addWidget(self.online_x_res_slider, 7, 1)
        grid_layout.addWidget(self.online_y_res_label, 7, 2)
        grid_layout.addWidget(self.online_y_res_slider, 7, 3)

        grid_layout.addWidget(self.off_vs_online_calculation_label, 8, 0)
        grid_layout.addWidget(self.off_vs_online_calculation_bg_label, 8, 1)
        grid_layout.addWidget(self.create_off_vs_on_btn, 8, 2)

        grid_layout.addWidget(self.blank_label2, 9, 0)

        grid_layout.addWidget(self.combo_label, 10, 0)
        grid_layout.addWidget(self.combo_calculation_bg_label, 10, 1)
        grid_layout.addWidget(self.create_combo_axis_btn, 10, 2)

        grid_layout.addWidget(self.blank_label3, 11, 0)

        grid_layout.addWidget(self.cancel_btn, 12, 0)
        grid_layout.addWidget(self.use_res_list_btn, 12, 2)
        grid_layout.addWidget(self.save_btn, 12, 3)

        # Add layout to window
        self.window.add_layout(grid_layout)

        self.window.show()

        return self.window

def color_code_action_nodes(selection):
    for segment in selection:
            if isinstance(segment, flame.PySegment):
                for tlfx in segment.effects:
                    if tlfx.type == 'Action':
                        # Set color of clips on timeline
                        segment.colour = (50,0,0)
            else:
                continue

#-------------------------------------#
# Scopes

def scope_timeline_segment(selection):
    '''Return True if selection is a timeline segment.'''

    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False
#-------------------------------------#
# Flame Menus

def get_action_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Scale Compensator',
                    # 'order': 1,
                    # 'separator': 'below',
                    'execute': ScaleCompensator,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]

def get_timeline_custom_ui_actions():
    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Color Code Action Segments',
                    # 'order': 1,
                    # 'separator': 'below',
                    'isVisible': scope_timeline_segment,
                    'execute': color_code_action_nodes,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]