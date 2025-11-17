# Adjust Text Fx
# Copyright (c) 2025 Michael Vaglienty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: Adjust Text FX
Script Version: 2.10.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 05.08.20
Update Date: 04.12.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Timeline

Description:

    Interactively adjust timeline text fx settings that can then be applied to all selected timeline text fx

URL:
    https://github.com/logik-portal/python/adjust_text_fx

Menu:

    Right-click on selected clips on timeline with text fx -> Adjust Text FX

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.10.0 04.12.25
        - Updated to PyFlameLib v4.3.0.

    v2.9.0 12.30.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v2.8.0 08.12.24
        - Updated to PyFlameLib v3.0.0.

    v2.7.0 01.30.24
        - Updates to UI/PySide.
        - Updated to PyFlameLib v2.0.0
        - Updated script versioning to semantic versioning.

    v2.6 03.23.23
        - Added ability to select different font types to the file browser for 2022 - 2022.3.

    v2.5 03.13.23
        - Added check to make sure script is installed in the correct location.
        - Misc bug fixes.

    v2.4 10.31.22
        - Updated menu for Flame 2023.2+

    v2.3 07.23.22
        - Messages print to Flame message window - Flame 2023.1 and later
        - Added Flame file browser - Flame 2023.1 and later

    v2.2 03.18.22
        - Moved UI widgets to external file

    v2.1 02.25.22
        - Updated UI for Flame 2023

    v2.0 05.22.21
        - Updated to be compatible with Flame 2022/Python 3.7

    v1.4 02.17.21
        - Multiple text layers can now be repositioned properly
        - Fixes to slider calculator

    v1.3 02.06.21
        - Misc slider calculator fixes
        - Converted UI elements to classes
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import ast
import os
import shutil
import xml.etree.cElementTree as ET
from functools import partial

import flame
from lib.pyflame_lib_adjust_text_fx import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Adjust Text FX'
SCRIPT_VERSION = 'v2.10.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class AdjustFX():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} - {SCRIPT_VERSION}')

        # Check script path, if not correct, display error message and end script
        if not pyflame.verify_script_install():
            return

        # Filter select for segments
        self.selection = [s for s in selection if isinstance(s, flame.PySegment)]
        print('Selection:', self.selection, '\n')

        self.selection_count = len(self.selection)
        print('Selection Count:', self.selection_count, '\n')

        self.selected_segment = self.selection[0]
        print('Selected segment:', self.selected_segment, '\n')

        self.temp_save_path = os.path.join(SCRIPT_PATH, 'temp')
        if not os.path.isdir(self.temp_save_path):
            os.makedirs(self.temp_save_path)

        self.temp_text_file = os.path.join(self.temp_save_path, 'temp_text.ttg_node')
        print('Temp text file:', self.temp_text_file)

        self.backup_temp_text_file = os.path.join(self.temp_save_path, 'backup_temp_text.ttg_node')
        print('Backup temp text file:', self.backup_temp_text_file)

        self.temp_xml_path = os.path.join(self.temp_save_path, 'temp_text.xml')
        print('Temp xml path:', self.temp_xml_path, '\n')

        self.default_font_path = '/opt/Autodesk/font'

        self.font_size_anim = False
        self.italic_angle_anim = False
        self.kern_anim = False
        self.fill_transp_anim = False
        self.char_soft_anim = False
        self.translation_x_anim = False
        self.translation_y_anim = False
        self.separation_anim = False
        self.shadow_transp_anim = False
        self.shad_soft_anim = False
        self.all_shadows_translation_x_anim = False
        self.all_shadows_translation_y_anim = False

        # Init variables
        self.channel_anim = ''
        self.text_fx_setup = ''

        self.align_changed = False

        self.get_initial_text_fx()

        # Import text node setup xml
        tree = ET.ElementTree(file=self.temp_text_file)
        self.root = tree.getroot()

        # Check text fx for text layers
        if not self.get_value('FontName'):
            PyFlameMessageWindow(
                message='Segment text fx contains no text layers',
                type=MessageType.ERROR
                )
            return

        # Check number of fx on segment. If only one add additional fx
        # Needed for gap fx. Script deletes gap fx later. If no additional gap fx
        # is added, gap will be deleted.
        if len(self.selected_segment.effects) < 2:
            self.create_temp_timeline_fx = True
            print('Temp fx needed.')
        else:
            self.create_temp_timeline_fx = False
            print('Temp fx not needed.')

        # Get text fx values

        self.get_text_fx_values()

        self.main_window()

    def get_initial_text_fx(self):

        def load_text_setup():
            """
            Get text lines from saved timeline text fx
            """

            get_text_values = open(self.temp_text_file, 'r')
            self.text_fx_setup = get_text_values.read()
            get_text_values.close()

        def insert_lines():
            """
            Insert missing <Extrap> and <Value> lines if x/y translation is set to 0
            """

            load_text_setup()

            line = '<Extrap>constant</Extrap><Value>0</Value>'

            if '<Channel Name="translation/x"/><Channel' in self.text_fx_setup:
                translate_x_split = self.text_fx_setup.split('<Channel Name="translation/x"/>', 1)
                self.text_fx_setup = translate_x_split[0] + '<Channel Name="translation/x">' + line + '</Channel>' + translate_x_split[1]

            if '<Channel Name="translation/y"/><Channel' in self.text_fx_setup:
                translate_y_split = self.text_fx_setup.split('<Channel Name="translation/y"/>', 1)
                self.text_fx_setup = translate_y_split[0] + '<Channel Name="translation/y">' + line + '</Channel>' + translate_y_split[1]

        # Get playhead position on timeline
        track = self.selected_segment.parent
        version = track.parent
        self.seq = version.parent
        print('Sequence name:', self.seq.name)

        self.playhead_position = self.seq.current_time.get_value()
        print('Playhead position:', self.playhead_position, '\n')

        # Save text fx setup as xml
        for fx in self.selected_segment.effects:
            if fx.type == 'Text':
                #  Save text node to be modified
                fx.save_setup(self.temp_text_file)

                # Save backup text node to be restored if script cancelled
                fx.save_setup(self.backup_temp_text_file)

                # Insert missing lines if x/y translation is set to 0
                insert_lines()

                # Save out new text node and xml files
                text_node_file = open(self.temp_text_file, "w")
                text_node_file.write(self.text_fx_setup)
                text_node_file.close()

                xml_file = open(self.temp_xml_path, "w")
                xml_file.write(self.text_fx_setup)
                xml_file.close()

    def get_value(self, value):
        """
        Get Value
        =========

        Get value from saved xml file
        """

        try:
            for elem in self.root.iter(value):
                item_value = elem.text
            return item_value
        except:
            return False

    def get_text_fx_values(self):

        def get_line_value(line_name, value):
            # Get values from lines that contain multiple values
            # Such as Font Style of Colour Fill

            for elem in self.root.iter(line_name):
                elem_dict = elem.attrib
            result = elem_dict.get(value)

            return result

        def parse_xml(channel):

            # Reset channel anim to False as default
            self.channel_anim = False

            child_names = [child.tag for child in channel]
            # print 'child_names:', child_names

            child_objects = [child for child in channel]
            # print 'child_objects:', child_objects

            if 'KFrames' not in child_names:
                # print 'No Key Frames Found'
                self.channel_anim = False

                for child in channel:
                    # print 'CHILD:', child
                    if 'Value' in str(child):
                        # print child.tag
                        # print child.text
                        value = child.text
                # print 'value:', value
                # print 'channel_name:', channel_name

            else:
                # print('Key Frames Found')
                self.channel_anim = True
                kframe_index = child_names.index('KFrames')
                kframe_object = child_objects[kframe_index]
                # print kframe_object.tag

                # Only get first key frame value
                for key in kframe_object:
                    # print key.tag
                    key_names = [k.tag for k in key]
                    # print key_names
                    key_objects = [k for k in key]
                    key_value_index = key_names.index('Value')
                    value = key_objects[key_value_index].text
                    # print 'Value:', value
                    break

            # print 'value:', value

            result = float(value)

            # Convert float to int if float has .0 at end
            if str(result).endswith('.0'):
                result = int(result)

            return result

        # Get text file values
        self.font_path = self.get_value('FontName')

        if self.font_path == 'Discreet':
            self.font_path = '/opt/Autodesk/font/Discreet.font'

        # Extract font name from font path
        #self.get_font_name(self.font_path)

        self.font_size = int(self.get_value('FontSize'))
        self.italic_angle = float(self.get_value('ItalicAngle'))
        self.kern = float(self.get_value('Kern'))
        self.alignment = (self.get_value('Justification')).rsplit('_', 1)[1]
        self.char_soft = float(self.get_value('CharSoftness'))
        self.shadow_softness = float(self.get_value('ShadowSoftness'))
        self.all_shadows_translation_x = float(self.get_value('RulerStaticTranslationX'))
        self.all_shadows_translation_y = float(self.get_value('RulerStaticTranslationY'))
        self.separation = 0

        self.drop_shadow = get_line_value('FontStyle', 'DropShadow')
        if self.drop_shadow == '1':
            self.drop_shadow = True
        else:
            self.drop_shadow = False
        # print 'drop_shadow:', self.drop_shadow, '\n'

        self.fill_transp = int(round(float(get_line_value('ColourFill', 'a'))))
        # print 'fill_transp:', self.fill_transp

        self.shadow_transp = int(round(float(get_line_value('ColourDrop', 'a'))))
        # print 'shadow_transp:', self.shadow_transp

        self.shadow_blur = ast.literal_eval(self.get_value('BlurOn'))
        # print 'shadow_blur:', self.shadow_blur

        self.shadow_blur_level = int(self.get_value('BlurLevel'))
        # print 'shadow_blur_level', self.shadow_blur_level, '\n'

        # Create lists for layer x/y offsets

        self.translation_x_list = []
        self.translation_y_list = []

        # Check for Channel/Key Frame values
        # Overwrite values from above if Channel/Key Frame values exist
        for channel in self.root.iter('Channel'):
            channel_name = str(channel.attrib).rsplit("'", 2)[1]
            # print 'channel_name:', channel_name

            # Get values from xml
            # If channel has animation set channel value to 0 - slider will act as offset

            if 'size' in channel_name:
                self.font_size = parse_xml(channel)
                if self.channel_anim:
                    self.font_size_anim = True
                    self.font_size = 0
                # print 'font_size:', self.font_size, '\n'

            elif 'italic' in channel_name:
                self.italic_angle = parse_xml(channel)
                if self.channel_anim:
                    self.italic_angle_anim = True
                    self.italic_angle = 0
                # print 'italic_angle:', self.italic_angle, '\n'

            elif 'kern' in channel_name:
                self.kern = parse_xml(channel)
                if self.channel_anim:
                    self.kern_anim = True
                    self.kern = 0
                # print 'kern:', self.kern, '\n'

            elif 'fill_colour/transp' in channel_name:
                self.fill_transp = parse_xml(channel)
                if self.channel_anim:
                    self.fill_transp_anim = True
                    self.fill_transp = 0
                # print 'fill_transp:', self.fill_transp, '\n'

            elif 'char_soft' in channel_name:
                self.char_soft = parse_xml(channel)
                if self.channel_anim:
                    self.char_soft_anim = True
                    self.char_soft = 0
                # print 'char_soft:', self.char_soft, '\n'

            elif channel_name == 'translation/x':
                self.translation_x = parse_xml(channel)
                self.translation_x_list.append(self.translation_x)
                # print 'translation_x:', self.translation_x, '\n'

            elif channel_name == 'translation/y':
                self.translation_y = parse_xml(channel)
                self.translation_y_list.append(self.translation_y)
                # print 'translation_y:', self.translation_y, '\n'

            elif 'separation' in channel_name:
                self.separation = parse_xml(channel)
                # print 'separation:', self.separation, '\n'

            elif 'drop_colour/transp' in channel_name:
                self.shadow_transp = parse_xml(channel)
                # print 'shadow_transp:', self.shadow_transp, '\n'

            elif 'shad_soft' in channel_name:
                self.shad_soft = parse_xml(channel)
                # print 'shad_soft:', self.shad_soft, '\n'

            elif 'all_shadows/translation/x' in channel_name:
                self.all_shadows_translation_x = parse_xml(channel)
                # print 'all_shadows_translation_x:', self.all_shadows_translation_x, '\n'

            elif 'all_shadows/translation/y' in channel_name:
                self.all_shadows_translation_y = parse_xml(channel)

    def regen_align(self):

        self.regen_text_fx(True)

    def main_window(self):

        #-------------------------------------
        # [Window Elements]
        #-------------------------------------

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.apply_text_fx,
            grid_layout_columns=10,
            grid_layout_rows=10,
            grid_layout_column_width=100,
            grid_layout_adjust_column_widths={6: 50},
            )

        # Labels
        self.font_label = PyFlameLabel(
            text='Font',
            style=Style.UNDERLINE,
            )
        self.position_offset_label = PyFlameLabel(
            text='Position Offset',
            style=Style.UNDERLINE,
            )
        self.shadow_label = PyFlameLabel(
            text='Shadow',
            style=Style.UNDERLINE,
            )

        self.font_path_label = PyFlameLabel(
            text='Font',
            )
        self.font_size_label = PyFlameLabel(
            text='Font Size',
            )
        self.italic_angle_label = PyFlameLabel(
            text='Italic Angle',
            )
        self.kern_label = PyFlameLabel(
            text='Kern',
            )
        self.align_label = PyFlameLabel(
            text='Align',
            )
        self.fill_trans_label = PyFlameLabel(
            text='Transparency',
            )
        self.softness_label = PyFlameLabel(
            text='Softness',
            )
        self.separation_label = PyFlameLabel(
            text='Separation',
            )
        self.offset_x_pos_label = PyFlameLabel(
            text='Offset X Pos',
            )
        self.offset_y_pos_label = PyFlameLabel(
            text='Offset Y Pos',
            )
        self.shadow_transp_label = PyFlameLabel(
            text='Transparency',
            )
        self.shadow_softness_label = PyFlameLabel(
            text='Softness',
            )
        self.shadow_x_pos_label = PyFlameLabel(
            text='X Pos',
            )
        self.shadow_y_pos_label = PyFlameLabel(
            text='Y Pos',
            )
        self.shadow_blur_label = PyFlameLabel(
            text='Blur',
            )

        self.font_path_entry = PyFlameLineEditFileBrowser(
            text=self.font_path,
            browser_type=BrowserType.FILE,
            browser_ext=[
                'afm',
                'font',
                'pfa',
                'ttf',
                'ttc',
                'otf',
                'dfont',
                'TMM',
                ],
            browser_title='Select Font',
            browser_window_to_hide=[self.window],
            connect=partial(self.regen_text_fx, self.align_changed),
            )

        # Sliders
        if self.font_size_anim:
            minimum_value = 0
        else:
            minimum_value = 1

        self.font_size_slider = PyFlameSlider(
            start_value=int(self.font_size),
            min_value=minimum_value,
            max_value=2000,
            connect=self.regen_text_fx,
            )
        self.italic_angle_slider = PyFlameSlider(
            start_value=int(self.italic_angle),
            min_value=-60,
            max_value=60,
            connect=self.regen_text_fx,
            )
        self.kern_slider = PyFlameSlider(
            start_value=int(self.kern),
            min_value=-100,
            max_value=100,
            connect=self.regen_text_fx,
            )
        self.fill_transp_slider = PyFlameSlider(
            start_value=int(self.fill_transp),
            min_value=0,
            max_value=100,
            connect=self.regen_text_fx,
            )
        self.softness_slider = PyFlameSlider(
            start_value=float(self.char_soft),
            min_value=-100,
            max_value=100,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.offset_x_pos_slider = PyFlameSlider(
            start_value=0,
            min_value=-99999,
            max_value=99999,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.offset_y_pos_slider = PyFlameSlider(
            start_value=0,
            min_value=-99999,
            max_value=99999,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.separation_slider = PyFlameSlider(
            start_value=self.separation,
            min_value=0,
            max_value=999,
            connect=self.regen_text_fx,
            )
        self.shadow_transp_slider = PyFlameSlider(
            start_value=self.shadow_transp,
            min_value=0,
            max_value=100,
            connect=self.regen_text_fx,
            )
        self.shadow_softness_slider = PyFlameSlider(
            start_value=self.shadow_softness,
            min_value=-100,
            max_value=100,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.shadow_x_pos_slider = PyFlameSlider(
            start_value=self.all_shadows_translation_x,
            min_value=-9999,
            max_value=9999,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.shadow_y_pos_slider = PyFlameSlider(
            start_value=self.all_shadows_translation_y,
            min_value=-9999,
            max_value=9999,
            value_is_float=True,
            connect=self.regen_text_fx,
            )
        self.shadow_blur_slider = PyFlameSlider(
            start_value=self.shadow_blur_level,
            min_value=0,
            max_value=200,
            connect=self.regen_text_fx,
            )

        # Shadow Pushbuttons
        def shadow_options():

            shadow_checked = self.shadow_pushbutton.isChecked()
            shadow_options_toggle(shadow_checked)
            self.regen_text_fx(self.align_changed)

        def shadow_blur_options():

            shadow_blur_checked = self.shadow_blur_pushbutton.isChecked()
            shadow_blur_options_toggle(shadow_blur_checked)
            self.regen_text_fx(self.align_changed)

        def shadow_options_toggle(shadow_checked):

            if shadow_checked:
                self.shadow_transp_label.setEnabled(True)
                self.shadow_transp_slider.setEnabled(True)
                self.shadow_softness_label.setEnabled(True)
                self.shadow_softness_slider.setEnabled(True)
                self.shadow_x_pos_label.setEnabled(True)
                self.shadow_x_pos_slider.setEnabled(True)
                self.shadow_y_pos_label.setEnabled(True)
                self.shadow_y_pos_slider.setEnabled(True)

                self.shadow_blur_pushbutton.setEnabled(True)
                if self.shadow_blur_pushbutton.isChecked():
                    self.shadow_blur_label.setEnabled(True)
                    self.shadow_blur_slider.setEnabled(True)
            else:
                self.shadow_transp_label.setEnabled(False)
                self.shadow_transp_slider.setEnabled(False)
                self.shadow_softness_label.setEnabled(False)
                self.shadow_softness_slider.setEnabled(False)
                self.shadow_x_pos_label.setEnabled(False)
                self.shadow_x_pos_slider.setEnabled(False)
                self.shadow_y_pos_label.setEnabled(False)
                self.shadow_y_pos_slider.setEnabled(False)

                self.shadow_blur_pushbutton.setEnabled(False)
                self.shadow_blur_label.setEnabled(False)
                self.shadow_blur_slider.setEnabled(False)

        def shadow_blur_options_toggle(shadow_blur_checked):

            if shadow_blur_checked:
                self.shadow_blur_label.setEnabled(True)
                self.shadow_blur_slider.setEnabled(True)
            else:
                self.shadow_blur_label.setEnabled(False)
                self.shadow_blur_slider.setEnabled(False)

        self.shadow_pushbutton = PyFlamePushButton(
            text='Shadow',
            button_checked=self.drop_shadow,
            connect=shadow_options,
            )
        self.shadow_blur_pushbutton = PyFlamePushButton(
            text='Shadow Blur',
            button_checked=self.shadow_blur,
            connect=shadow_blur_options,
            )

        if self.shadow_pushbutton.isChecked():
            shadow_options_toggle(True)
        else:
            shadow_options_toggle(False)
            shadow_blur_options_toggle(False)

        if not self.shadow_blur_pushbutton.isChecked():
            self.shadow_blur_label.setEnabled(False)
            self.shadow_blur_slider.setEnabled(False)

        # Pushbutton Menus
        self.align_push_button = PyFlamePushButtonMenu(
            text=self.alignment,
            menu_options=[
                'Left',
                'Centre',
                'Right',
                ],
            connect=self.regen_align,
            )

        # Buttons
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.cancel,
            )
        self.apply_button = PyFlameButton(
            text='Apply',
            connect=self.apply_text_fx,
            color=Color.BLUE,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.font_label, 0, 0, 1, 6)

        self.window.grid_layout.addWidget(self.font_path_label, 1, 0)
        self.window.grid_layout.addWidget(self.font_path_entry, 1, 1, 1, 5)

        self.window.grid_layout.addWidget(self.font_size_label, 2, 0)
        self.window.grid_layout.addWidget(self.font_size_slider, 2, 1)
        self.window.grid_layout.addWidget(self.fill_trans_label, 2, 2)
        self.window.grid_layout.addWidget(self.fill_transp_slider, 2, 3)
        self.window.grid_layout.addWidget(self.italic_angle_label, 2, 4)
        self.window.grid_layout.addWidget(self.italic_angle_slider, 2, 5)

        self.window.grid_layout.addWidget(self.softness_label, 3, 0)
        self.window.grid_layout.addWidget(self.softness_slider, 3, 1)
        self.window.grid_layout.addWidget(self.kern_label, 3, 2)
        self.window.grid_layout.addWidget(self.kern_slider, 3, 3)
        self.window.grid_layout.addWidget(self.separation_label, 3, 4)
        self.window.grid_layout.addWidget(self.separation_slider, 3, 5)

        self.window.grid_layout.addWidget(self.align_label, 4, 0)
        self.window.grid_layout.addWidget(self.align_push_button, 4, 1)

        self.window.grid_layout.addWidget(self.shadow_label, 0, 7, 1, 3)

        self.window.grid_layout.addWidget(self.shadow_pushbutton, 1, 7)
        self.window.grid_layout.addWidget(self.shadow_transp_label, 1, 8)
        self.window.grid_layout.addWidget(self.shadow_transp_slider, 1, 9)

        self.window.grid_layout.addWidget(self.shadow_softness_label, 2, 8)
        self.window.grid_layout.addWidget(self.shadow_softness_slider, 2, 9)

        self.window.grid_layout.addWidget(self.shadow_x_pos_label, 3, 8)
        self.window.grid_layout.addWidget(self.shadow_x_pos_slider, 3, 9)

        self.window.grid_layout.addWidget(self.shadow_y_pos_label, 4, 8)
        self.window.grid_layout.addWidget(self.shadow_y_pos_slider, 4, 9)

        self.window.grid_layout.addWidget(self.shadow_blur_pushbutton, 6, 7)
        self.window.grid_layout.addWidget(self.shadow_blur_label, 6, 8)
        self.window.grid_layout.addWidget(self.shadow_blur_slider, 6, 9)

        self.window.grid_layout.addWidget(self.position_offset_label, 6, 0, 1, 4)

        self.window.grid_layout.addWidget(self.offset_x_pos_label, 7, 0)
        self.window.grid_layout.addWidget(self.offset_x_pos_slider, 7, 1)
        self.window.grid_layout.addWidget(self.offset_y_pos_label, 7, 2)
        self.window.grid_layout.addWidget(self.offset_y_pos_slider, 7, 3)

        self.window.grid_layout.addWidget(self.cancel_button, 9, 8)
        self.window.grid_layout.addWidget(self.apply_button, 9, 9)

        #-------------------------------------

        self.seq.current_time = self.playhead_position

    def apply_text_fx(self):

        print('\n')
        print('[=========', 'Applying changes', '=========]', '\n')

        # Apply changes to all selected timeline segments with text fx
        self.selection_processed = 1

        for seg in self.selection:
            print(f'\nProcessing Text FX {self.selection_processed} of {self.selection_count} ...\n')
            if isinstance(seg, flame.PySegment):
                for fx in seg.effects:
                    if fx.type == 'Text':
                        self.selection_processed += 1
                        fx.save_setup(self.temp_text_file)
                        self.save_text_fx(fx, seg, self.align_changed)

        # Remove temp files
        shutil.rmtree(self.temp_save_path)

        pyflame.print('Temp files removed.')

        # Restore playhead position
        self.seq.current_time = self.playhead_position

        self.window.close()

        pyflame.print('Changes applied to all selected timeline segments.', text_color=TextColor.GREEN)

    def regen_text_fx(self, align_changed):

        self.playhead_position = self.seq.current_time.get_value()
        #print('playhead_position:', self.playhead_position, '\n')

        if align_changed:
            self.align_changed = True

        for fx in self.selected_segment.effects:
            if fx.type == 'Text':
                self.save_text_fx(fx, self.selected_segment, align_changed)

        # Restore playhead position
        self.seq.current_time = self.playhead_position

        print('-' * 30, '\n\n\n')

    def save_text_fx(self, fx, seg, align_changed):

        def get_ui_values():

            print('\nNew Text Values', '\n------------------------------------------\n')

            # If channel has animation use spinbox value to offset current channel value
            # If channel has no animation use spinbox value as new channel value
            # Offset X and Y Position spinbox value is always used to offset current value

            self.new_font_path = self.font_path_entry.path
            print('New Font Path:', self.new_font_path)

            if self.font_size_anim:
                self.new_font_size = str(int(self.font_size_slider.text()) + self.font_size)
            else:
                self.new_font_size = self.font_size_slider.text()
            print('New Font Size:', self.new_font_size)

            if self.italic_angle_anim:
                self.new_italic_angle = str(int(self.italic_angle_slider.text()) + self.italic_angle)
            else:
                self.new_italic_angle = self.italic_angle_slider.text()
            print('New Italic Angle:', self.new_italic_angle)

            if self.kern_anim:
                self.new_kern = str(int(self.kern_slider.text()) + self.kern)
            else:
                self.new_kern = self.kern_slider.text()
            print('New Kern:', self.new_kern)

            self.new_align = 'Justify_' + self.align_push_button.text()
            print('New Align:', self.new_align)

            if self.fill_transp_anim:
                self.new_fill_transp = str(int(self.fill_transp_slider.text()) + self.fill_transp)
            else:
                self.new_fill_transp = str(self.fill_transp_slider.text())
            print('New Fill Transp:', self.new_fill_transp)

            if self.char_soft_anim:
                self.new_char_soft = str(float(self.softness_slider.text()) + self.char_soft)
            else:
                self.new_char_soft = str(self.softness_slider.text())
            print('New Char Soft:', self.new_char_soft)

            # self.new_offset_x = str(float(self.offset_x_pos_lineedit.text()) + self.translation_x)
            # print 'new_offset_x:', self.new_offset_x

            self.new_translation_x_list = [str(x + float(self.offset_x_pos_slider.text())) for x in self.translation_x_list]
            print('New Translation X List:', self.new_translation_x_list)

            # self.new_offset_y = str(float(self.offset_y_pos_lineedit.text()) + self.translation_y)
            # print 'new_offset_y:', self.new_offset_y

            self.new_translation_y_list = [str(y + float(self.offset_y_pos_slider.text())) for y in self.translation_y_list]
            print('New Translation Y List:', self.new_translation_y_list)

            if self.separation_anim:
                self.new_separation = str(self.separation_slider.text() + self.separation)
            else:
                self.new_separation = str(self.separation_slider.text())
            print('New Separation:', self.new_separation)

            # Shadow

            if self.shadow_pushbutton.isChecked():
                self.new_shadow = '1'
            else:
                self.new_shadow = '0'
            print('New Shadow:', self.new_shadow)

            if self.shadow_transp_anim:
                self.new_shadow_transp = str(self.shadow_transp_slider.text() + self.shadow_transp)
            else:
                self.new_shadow_transp = str(self.shadow_transp_slider.text())
            print('New Shadow Transp:', self.new_shadow_transp)

            if self.shad_soft_anim:
                self.new_shad_softness = str(float(self.shadow_softness_slider.text()) + self.shad_soft)
            else:
                self.new_shad_softness = str(self.shadow_softness_slider.text())
            print('New Shad Softness:', self.new_shad_softness)

            if self.all_shadows_translation_x_anim:
                self.new_all_shadows_translation_x = str(float(self.shadow_x_pos_slider.text()) + self.all_shadows_translation_x)
            else:
                self.new_all_shadows_translation_x = str(self.shadow_x_pos_slider.text())
            print('New All Shadows Translation_x:', self.new_all_shadows_translation_x)

            if self.all_shadows_translation_y_anim:
                self.new_all_shadows_translation_y = str(float(self.shadow_y_pos_slider.text()) + self.all_shadows_translation_y)
            else:
                self.new_all_shadows_translation_y = str(self.shadow_y_pos_slider.text())
            print('New All Shadows Translation_y:', self.new_all_shadows_translation_y)

            # Shadow Blur
            self.new_shadow_blur = str(self.shadow_blur_pushbutton.isChecked())
            print('New Shadow Blur:', self.new_shadow_blur)

            self.new_shadow_blur_level = str(self.shadow_blur_slider.text())
            print('New Shadow Blur Level:', self.new_shadow_blur_level)

        def replace_value(elem_name, new_value):

            for elem in root.iter(elem_name):
                elem.text = new_value

        def replace_channel_value(channel_name, translation_list):

            index = 0

            for elem in root.iter('Channel'):

                child_objects = [child for child in elem if elem.get('Name') == channel_name] # Get list of channel values for desired channel
                # print 'child_objects:', child_objects
                if child_objects:
                    # Get channel object for 'Value'
                    for child in child_objects:
                        # print child.tag
                        if child.tag == 'Value':
                            # print 'translation_list_value:', translation_list[index]
                            child.text = translation_list[index]
                    index += 1

        def replace_equals_value(name, value_name, new_value, *args):

            #  Use for fill transparency and turning dropshadows off and on
            for elem in root.iter(name):
                elem.set(value_name, new_value)

        self.get_text_fx_values()

        # Import text node setup
        tree = ET.ElementTree(file=self.temp_text_file)
        root = tree.getroot()

        # Get values from GUI
        get_ui_values()

        # Replace values in xml with values from UI
        if self.new_font_path != self.font_path:
            replace_value('FontName', self.font_path_entry.path)

        if int(self.new_font_size) != int(self.font_size):
            replace_value('FontSize', self.new_font_size)

        if int(self.new_italic_angle) != int(self.italic_angle):
            replace_value('ItalicAngle', self.new_italic_angle)

        if int(self.new_kern) != int(self.kern):
            replace_value('Kern', self.new_kern)

        if align_changed:
            replace_value('Justification', self.new_align)

        if int(self.new_fill_transp) != int(self.fill_transp):
            replace_equals_value('ColourFill', 'a', self.new_fill_transp)

        if float(self.new_char_soft) != float(self.char_soft):
            replace_value('CharSoftness', self.new_char_soft)

        if float(self.new_translation_x_list[0]) != float(self.translation_x_list[0]):
            replace_channel_value('translation/x', self.new_translation_x_list)

        if float(self.new_translation_y_list[0]) != float(self.translation_y_list[0]):
            replace_channel_value('translation/y', self.new_translation_y_list)

        if int(self.new_separation) != int(self.separation):
            replace_value('Separation', self.new_separation)

        # Shadow values
        replace_equals_value('FontStyle', 'DropShadow', self.new_shadow)

        if int(self.new_shadow_transp) != int(self.shadow_transp):
            replace_equals_value('ColourDrop', 'a', self.new_shadow_transp)

        if float(self.new_shad_softness) != float(self.shadow_softness):
            replace_value('ShadowSoftness', self.new_shad_softness)

        if float(self.new_all_shadows_translation_x) != float(self.all_shadows_translation_x):
            replace_value('RulerStaticTranslationX', self.new_all_shadows_translation_x)

        if float(self.new_all_shadows_translation_y) != float(self.all_shadows_translation_y):
            replace_value('RulerStaticTranslationY', self.new_all_shadows_translation_y)

        # Shadow Blur
        replace_value('BlurOn', self.new_shadow_blur)

        if int(self.new_shadow_blur_level) != int(self.shadow_blur_level):
            replace_value('BlurLevel', self.new_shadow_blur_level)

        # Save new text node setup
        tree.write(self.temp_text_file)

        # Add aditional timeline fx to prevent timeline gap from being deleted
        if self.create_temp_timeline_fx:
            tempfx = seg.create_effect('blur')

        # Clear old text fx
        flame.delete(fx)
        fx = seg.create_effect('Text')

        # Delete temp timeline fx if one was added
        if self.create_temp_timeline_fx:
            flame.delete(tempfx)

        # Load temp text setup back to timeline
        fx.load_setup(self.temp_text_file)

        # Copy temp text file to xml
        # Only for testing
        shutil.copy(self.temp_text_file, self.temp_xml_path)

    def cancel(self):

        pyflame.print('Apply Text FX Cancelled - Restoring Original Text FX', text_color=TextColor.RED)

        # Add aditional timeline fx to prevent timeline gap from being deleted
        if self.create_temp_timeline_fx:
            tempfx = self.selected_segment.create_effect('blur')

        # Restore original text fx
        for fx in self.selected_segment.effects:
            if fx.type == 'Text':
                flame.delete(fx)
                fx = self.selected_segment.create_effect('Text')
                fx.load_setup(self.backup_temp_text_file)

        # Delete temp timeline fx if one was added
        if self.create_temp_timeline_fx:
            flame.delete(tempfx)

        # Remove temp files
        shutil.rmtree(self.temp_save_path)

        # Close window
        self.window.close()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_segment(selection):

    for item in selection:
        if isinstance(item, flame.PySegment):
            for fx in item.effects:
                if fx.type == 'Text':
                    return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_timeline_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Adjust Text FX',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_segment,
                    'execute': AdjustFX,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
