# SRT to XML
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
Script Name: SRT to XML
Script Version: 3.7.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 05.01.20
Update Date: 04.13.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Convert SRT files to XML files that can be imported into Flame through MediaHub

URL:
    https://github.com/logik-portal/python/srt_to_xml

Menu:

    Right-click on clip in Media Panel that subtitles will be added to -> Convert SRT to XML

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.7.0 04.13.25
        - Updated to PyFlameLib v4.3.0.

    v3.6.0 12.27.24
        - Updated for Python 3/Flame 2025+
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v3.5 03.04.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.

    v3.4 09.22.22
        - Updated menu for Flame 2023.2+:
            Right-click on clip in Media Panel that subtitles will be added to -> Convert SRT to XML

    v3.3 06.06.22
        - Messages print to Flame message window - Flame 2023.1 and later.
        - Added Flame file browser - Flame 2023.1 and later.

    v3.2 03.15.22
        - Moved UI widgets to external file.

    v3.1 03.05.22
        - Updated UI for Flame 2023.
        - Config updated to XML.
        - Added option to open MediaHub to location of created XML.

    v3.0 05.22.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v2.1 04.27.21
        - Bug fixes

    v1.4 03.18.21:
        - Added bottom align button - will align rows of text to bottom row.
        - Changed event detection from empty line to timecode line.

    v1.3 02.17.21:
        - Fixed problem that caused script not to work when right clicking on clip with ratio of 1.0.
        - UI Improvements.

    v1.2 10.12.20:
        - Updated UI.

    v1.1 05.16.20:
        - Fixed scoping so menu only shows when right-clicking on clips.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import itertools

import flame
from lib.pyflame_lib_srt_to_xml import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'SRT to XML'
SCRIPT_VERSION = 'v3.7.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ConvertSRT(object):

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path
        if not pyflame.verify_script_install(
            additional_files=[
                'assets/templates/xml_template.xml',
                'assets/templates/xml_title_template.xml',
                'assets/templates/text_node_template.ttg',
                ]
            ):
            return

        # Define paths
        self.xml_template_path = os.path.join(SCRIPT_PATH, 'assets/templates/xml_template.xml')
        self.xml_title_template_path = os.path.join(SCRIPT_PATH, 'assets/templates/xml_title_template.xml')
        self.default_template_path = os.path.join(SCRIPT_PATH, 'assets/templates/text_node_template.ttg')
        if not os.path.isfile(self.default_template_path):
            self.default_template_path = SCRIPT_PATH

        # Create/Load config file settings.
        self.settings = self.load_config()

        #-----------------------------------------

        # Check SRT path. If file no longer exists set to /
        if not (os.path.isfile(self.settings.srt_path) or os.path.isdir(self.settings.srt_path)):
            self.settings.srt_path = '/'

        # Check default template path
        # If path is empty, set to default
        # If file doesn't exist, set to default

        if self.settings.template_path == '/' or '':
            self.settings.template_path = self.default_template_path
        elif not os.path.isfile(self.settings.template_path):
            self.settings.template_path = self.default_template_path

        #-----------------------------------------

        # Get sequence variables
        self.seq = selection[0]

        print('Sequence Info:')
        print('------------------------')

        self.seq_name = str(self.seq.name)[1:-1]
        print('Sequence name:', self.seq_name)

        self.seq_frame_rate = self.seq.frame_rate.split(' ', 1)[0]
        print('Sequence frame rate:', self.seq_frame_rate)

        self.seq_width = self.seq.width
        print('Sequence width:', self.seq_width)

        self.seq_height = self.seq.height
        print('Sequence height:', self.seq_height)

        self.seq_ratio = self.seq.ratio
        if len(str(self.seq_ratio)) > 5:
            self.seq_ratio = str(self.seq_ratio)[:5]
        print('Sequence ratio:', self.seq_ratio)

        self.seq_bit_depth = self.seq.bit_depth
        print('Sequence bit depth:', self.seq_bit_depth)

        print('------------------------\n', end='')

        # Set XML label default values
        self.xml_name = 'None Selected'
        self.xml_start_timecode = '00:00:00:00'
        self.xml_end_timecode = '00:00:00:00'

        self.main_window()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
        --------
            PyFlameConfig:
                PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            config_values={
                'srt_path': '/',
                'template_path': '/',
                'bottom_align': False,
                'reveal_in_mediahub': False,
                }
            )

        return settings

    def main_window(self):

        def update_srt_info() -> None:
            """
            Update SRT Info
            =================

            Update SRT setting and info in UI.
            """

            self.settings.srt_path = self.srt_path_entry.text()
            self.get_srt_info()

        def update_template_info() -> None:
            """
            Update Template Info
            ====================

            Update template settings.
            """

            self.settings.template_path = self.template_path_entry.text()

        def apply_settings() -> None:
            """
            Apply Settings
            ==============

            Check entry field values and save config settings then convert SRT to XML.
            """

            def confirm_entry_fields() -> bool:
                """
                Confirm Entry Fields
                ====================

                Confirm entry field values.

                Returns:
                --------
                    bool:
                        True if entry fields are valid, False otherwise.
                """


                # Confirm entry field values
                if not os.path.isfile(self.srt_path_entry.text()):
                    PyFlameMessageWindow(
                        message='Select SRT file to convert.',
                        title='SRT to XML: Error',
                        type=MessageType.ERROR
                        )
                    return False

                elif not os.path.isfile(self.template_path_entry.text()):
                    PyFlameMessageWindow(
                        message='Select Text node template file.',
                        title='SRT to XML: Error',
                        type=MessageType.ERROR
                        )
                    return False

                self.xml_save_file_path = self.srt_path_entry.text()[:-3] + 'XML'
                print('XML Save Path:', self.xml_save_file_path, '\n')

                self.srt_lines = self.open_srt_file(self.srt_path_entry.text())
                if not self.srt_lines:
                    return False

                if os.path.isfile(self.xml_save_file_path):
                    if not PyFlameMessageWindow(
                        message=(
                            f'File Already Exists: \n\n'
                            f'{self.xml_save_file_path} \n\n'
                            f'Overwrite?'
                            ),
                        title='SRT to XML: Warning',
                        type=MessageType.WARNING
                        ):
                        return False
                    return True
                return True

            def save_config() -> None:
                """
                Save Config
                ===========

                Save config values to config file.
                """

                # Save config file
                self.settings.save_config(
                    config_values={
                        'srt_path': self.srt_path_entry.text(),
                        'template_path': self.template_path_entry.text(),
                        'bottom_align': self.bottom_align_button.isChecked(),
                        'reveal_in_mediahub': self.reveal_in_mediahub_button.isChecked(),
                        }
                    )

            # Confirm entry field values
            confirm_settings = confirm_entry_fields()
            if not confirm_settings:
                return

            # Save config settings
            save_config()

            # Convert SRT to XML
            self.convert_srt()

        # Create Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=apply_settings,
            grid_layout=True,
            grid_layout_columns=4,
            grid_layout_rows=9,
            )

        # Labels
        self.srt_path_label = PyFlameLabel(
            text='SRT File',
            )
        self.template_path_label = PyFlameLabel(
            text='Text Node Template',
            )
        self.xml_resolution_label = PyFlameLabel(
            text='XML Resolution',
            style=Style.UNDERLINE,
            )
        self.xml_ratio_label = PyFlameLabel(
            text='XML Ratio',
            style=Style.UNDERLINE,
            )
        self.xml_start_timecode_label = PyFlameLabel(
            text='XML Start Timecode',
            style=Style.UNDERLINE,
            )
        self.xml_end_timecode_label = PyFlameLabel(
            text='XML End Timecode',
            style=Style.UNDERLINE,
            )

        # Entries
        self.xml_resolution_entry = PyFlameEntry(
            text=f'{self.seq_width}x{self.seq_height}',
            align=Align.CENTER,
            read_only=True,
            )
        self.xml_ratio_entry = PyFlameEntry(
            text=str(self.seq_ratio),
            align=Align.CENTER,
            read_only=True,
            )
        self.xml_start_timecode_entry = PyFlameEntry(
            text=self.xml_start_timecode,
            align=Align.CENTER,
            read_only=True,
            )
        self.xml_end_timecode_entry = PyFlameEntry(
            text=self.xml_end_timecode,
            align=Align.CENTER,
            read_only=True,
            )

        #  File Browser Entries
        self.srt_path_entry = PyFlameLineEditFileBrowser(
            text=self.settings.srt_path,
            browser_ext=['SRT'],
            browser_title='Select SRT File',
            browser_window_to_hide=[self.window],
            connect=update_srt_info,
            )

        self.template_path_entry = PyFlameLineEditFileBrowser(
            text=self.settings.template_path,
            browser_ext=['ttg'],
            browser_title='Select Text Node Setup File (ttg)',
            browser_window_to_hide=[self.window],
            connect=update_template_info,
            )

        # Push Buttons
        self.bottom_align_button = PyFlamePushButton(
            text='Bottom Align Text',
            button_checked=self.settings.bottom_align,
            )
        self.reveal_in_mediahub_button = PyFlamePushButton(
            text='Reveal in MediaHub',
            button_checked=self.settings.reveal_in_mediahub,
            )

        # Buttons
        self.convert_button = PyFlameButton(
            text='Convert',
            connect=apply_settings,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        # Update UI with SRT info
        self.get_srt_info()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.srt_path_label, 0, 0)
        self.window.grid_layout.addWidget(self.srt_path_entry, 0, 1, 1, 3)

        self.window.grid_layout.addWidget(self.template_path_label, 1, 0)
        self.window.grid_layout.addWidget(self.template_path_entry, 1, 1, 1, 3)

        self.window.grid_layout.addWidget(self.xml_resolution_label, 3, 0)
        self.window.grid_layout.addWidget(self.xml_resolution_entry, 4, 0)

        self.window.grid_layout.addWidget(self.xml_ratio_label, 3, 1)
        self.window.grid_layout.addWidget(self.xml_ratio_entry, 4, 1)

        self.window.grid_layout.addWidget(self.xml_start_timecode_label, 3, 2)
        self.window.grid_layout.addWidget(self.xml_start_timecode_entry, 4, 2)

        self.window.grid_layout.addWidget(self.xml_end_timecode_label, 3, 3)
        self.window.grid_layout.addWidget(self.xml_end_timecode_entry, 4, 3)

        self.window.grid_layout.addWidget(self.bottom_align_button, 6, 2)
        self.window.grid_layout.addWidget(self.reveal_in_mediahub_button, 6, 3)

        self.window.grid_layout.addWidget(self.cancel_button, 8, 2)
        self.window.grid_layout.addWidget(self.convert_button, 8, 3)

    def open_srt_file(self, srt_path) -> list:
        """
        Open SRT File
        =============

        Open SRT file and return list of lines.

        Args:
        -----
            srt_path (str):
                Path to SRT file.

        Returns:
        --------
            list:
                List of lines from SRT file.

        Raises:
        -------
            UnicodeDecodeError:
                If SRT file is not a standard format.
        """

        try:
            with open(srt_path, 'r') as srt_file:
                return srt_file.read().splitlines()
        except UnicodeDecodeError as error:
            PyFlameMessageWindow(
                message=(
                    f'Unable to load SRT: {error}. \n'
                    f'Non standard characters or fancy quotes could be causing a problem.'
                    ),
                title='SRT to XML: Error',
                type=MessageType.ERROR
                )
            return False

    def get_srt_info(self) -> None:
        """
        Get SRT Info
        ============

        Get SRT file information.
        """

        if os.path.isfile(self.settings.srt_path):

            print('\n')
            print('SRT Info')
            print('========\n')

            # Get XML name from name of SRT file
            self.xml_name = str(self.settings.srt_path.rsplit('/', 1)[1])[:-4]
            print('XML Name:', self.xml_name)

            # Open SRT file
            self.srt_lines = self.open_srt_file(self.settings.srt_path)

            if self.srt_lines:
                # Get SRT start timecode
                for line in self.srt_lines:
                    start_timecode = re.match(r'\d\d:\d\d:\d\d,\d\d\d', line)
                    if start_timecode:
                        self.start_timecode = start_timecode.group(0)
                        print('Start Timecode:', self.start_timecode)
                        break

                # Convert start milliseconds to frames based on frame rate
                self.xml_start_timecode = self.calculate_frames(self.start_timecode)

                # Get SRT end timecode
                for line in self.srt_lines:
                    end_timecode = re.findall(r'\d\d:\d\d:\d\d,\d\d\d', line)
                    if end_timecode:
                        self.end_timecode = end_timecode[1]

                print('End Timecode:', self.end_timecode, '\n')

                # Convert end milliseconds to frames based on frame rate
                self.xml_end_timecode = self.calculate_frames(self.end_timecode)

                self.xml_start_timecode_entry.setText(self.xml_start_timecode)
                self.xml_end_timecode_entry.setText(self.xml_end_timecode)

    def calculate_frames(self, timecode) -> str:
        """
        Calculate Frames
        ================

        Calculate frames from timecode.

        Returns:
        --------
            str:
                Timecode in frames.
        """

        frame_rate = self.seq_frame_rate

        if self.seq_frame_rate == '50':
            frame_rate = '25'
        elif self.seq_frame_rate == '59.94':
            frame_rate = '29.97'
        elif self.seq_frame_rate == '60':
            frame_rate = '30'

        milliseconds_per_frame = 1000/float(frame_rate)

        timecode_split = timecode.rsplit(',', 1)

        milliseconds = timecode_split[1]

        hours_mins_secs = timecode_split[0]

        frames = str(int(round(float(milliseconds)/milliseconds_per_frame)))
        if len(frames) == 1:
            frames = '0' + frames

        if self.seq_frame_rate in ('23.976', '24'):
            resolved_timecode = hours_mins_secs + '+' + frames
        elif self.seq_frame_rate in ('25', '29.97', '30'):
            resolved_timecode = hours_mins_secs + ':' + frames
        elif self.seq_frame_rate in ('50', '59.94', '60'):
            resolved_timecode = hours_mins_secs + '#' + frames

        return resolved_timecode

    def convert_srt(self) -> None:
        """
        Convert SRT
        ===========

        Convert SRT file to XML file.

        Creates XML file with timecode and text lines from SRT file.
        """

        def replace_xml_template_tokens() -> list:
            """
            Replace XML Template Tokens
            ===========================

            Replace tokens in XML template file with values from UI.

            Returns:
            --------
                list:
                    List of lines from XML template file with tokens replaced.
            """

            bit_depth = str(self.seq_bit_depth) + ' bit'
            if self.seq_bit_depth == 16:
                bit_depth = bit_depth + ' fp'

            frame_rate = self.seq_frame_rate
            if frame_rate == '29.97':
                frame_rate = '29.97 NDF'
            elif frame_rate == '59.94':
                frame_rate = '59.94 NDF'

            # Replace tokens in XML template file
            template_token_dict = {}

            template_token_dict['<XmlName>'] = self.srt_path_entry.text().rsplit('/', 1)[1][:-4]
            template_token_dict['<FrameRate>'] = frame_rate
            template_token_dict['<SeqWidth>'] = str(self.seq_width)
            template_token_dict['<SeqHeight>'] = str(self.seq_height)
            template_token_dict['<SeqBitDepth>'] = bit_depth
            template_token_dict['<SeqRatio>'] = str(self.seq_ratio)
            template_token_dict['<SeqTimecodeStart>'] = self.xml_start_timecode
            template_token_dict['<SeqTimecodeEnd>'] = self.xml_end_timecode

            # Open menu template
            xml_template = open(self.xml_template_path, 'r')
            xml_template_lines = xml_template.read().splitlines()

            # Replace tokens in menu template
            for key, value in template_token_dict.items():
                for line in xml_template_lines:
                    if key in line:
                        line_index = xml_template_lines.index(line)
                        new_line = re.sub(key, value, line)
                        xml_template_lines[line_index] = new_line

            xml_template.close()

            return xml_template_lines

        def create_srt_lists() -> list:
            """
            Create SRT Lists
            =================

            Create timecode and text line lists from SRT file.

            Returns:
            --------
                list:
                    List of timecode line numbers.
            """

            line_num = -1

            timecode_line_list = []

            for line in self.srt_lines:
                line_num += 1
                timecode_line = re.match('\d\d:\d\d:\d\d,\d\d\d --> \d\d:\d\d:\d\d,\d\d\d', line)
                if timecode_line:
                    #print(str(line_num) + '   ' + timecode_line.group(0))
                    timecode_line_list.append(line_num)

            return timecode_line_list

        # Replace tokens in XML template with values from UI
        xml_template_lines = replace_xml_template_tokens()

        # Create timecode and text line lists from SRT
        timecode_line_list = create_srt_lists()

        # loop through entries in SRT to create XML titles
        # ------------------------------------------------

        # Line to start inserting titles into XML template
        xml_title_insert_line = 17

        # Get last line of text in SRT file for end of last event
        with open(self.srt_path_entry.text(), 'r') as f:
            lines = f.read().splitlines()
            #print(lines, '\n')

        def get_last_line():
            last_line = lines[-1]
            if not last_line:
                lines.pop()
                get_last_line()
            return len(lines) + 2

        srt_end_line = get_last_line()
        #print('srt_end_line:', srt_end_line)

        # Get max number of text lines in all events for bottom row align button
        text_line_num_list = []

        for item in timecode_line_list:
            next_item_index = timecode_line_list.index(item) + 1
            try:
                next_item = timecode_line_list[next_item_index]
            except:
                next_item = srt_end_line
            line_num_value = next_item - item - 1
            text_line_num_list.append(line_num_value)
        max_line_value = max(text_line_num_list) - 2
        #print('max_line_value:', max_line_value)

        # Loop through events in timecode list to replace title tokens
        for item in timecode_line_list:
            item_index = timecode_line_list.index(item)

            # Convert start and end timecode from milliseconds to frames
            with open(self.srt_path_entry.text(), 'r') as srt_file:
                for srt_timecode_line in itertools.islice(srt_file, item, (item + 1)):
                    srt_start_timecode = self.calculate_frames(srt_timecode_line.split(' ', 1)[0])
                    srt_end_timecode = self.calculate_frames(srt_timecode_line.split('-> ', 1)[1])
                    # print('srt_timecode_line:', srt_timecode_line)
                    # print('srt_start_timecode:', srt_start_timecode)
                    # print('srt_end_timecode:', srt_end_timecode, '\n')

            # Add text lines to list to be converted to string later
            srt_text_line_list = []

            # print('item_index:', item_index)
            timecode_line_num = timecode_line_list[item_index]
            # print('timecode_line_num:', timecode_line_num)
            first_line_num = timecode_line_num + 1
            # print('first_line_num:', first_line_num)
            try:
                next_timecode_line_num = timecode_line_list[item_index + 1]
            except:
                next_timecode_line_num = srt_end_line
            # print('next_timecode_line_num:', next_timecode_line_num)
            last_line_num = next_timecode_line_num - 2
            # print('last_line_num:', last_line_num)

            # Get text lines from SRT file
            with open(self.srt_path_entry.text(), 'r') as srt_file:
                for text_line in itertools.islice(srt_file, first_line_num, last_line_num):
                    text_line = text_line.strip()
                    srt_text_line_list.append(text_line)
            #print('srt_text_line_list:', srt_text_line_list)

            # If bottom align button is selected insert empty lines to align rows of text
            if self.bottom_align_button.isChecked():
                while len(srt_text_line_list) < max_line_value:
                    srt_text_line_list.insert(0, ' ')

            # Convert srt_text_line_list to string
            # Add return code if list has more than one item
            srt_line_text = ''

            if len(srt_text_line_list) == 1:
                srt_line_text = srt_text_line_list[0]
            else:
                for line in srt_text_line_list:
                    srt_line_text = srt_line_text + '&#13;' + line
                srt_line_text = srt_line_text[5:]

            # Create dict with value to replace tokens in XML title template
            title_template_token_dict = {}
            title_template_token_dict['<TitleStartTimecode>'] = srt_start_timecode
            title_template_token_dict['<TitleEndTimecode>'] = srt_end_timecode
            title_template_token_dict['<TitleText>'] = srt_line_text
            title_template_token_dict['<TextNodeTemplatePath>'] = self.template_path_entry.text()

            # Open XML title template
            xml_title_template = open(self.xml_title_template_path, 'r')
            title_template_lines = xml_title_template.read().splitlines()

            # Replace tokens in XML title template
            for key, value in title_template_token_dict.items():
                for line in title_template_lines:
                    if key in line:
                        line_index = title_template_lines.index(line)
                        new_line = re.sub(key, value, line)
                        title_template_lines[line_index] = new_line

            xml_title_template.close()

            # Insert new title template lines into XML template
            for line in title_template_lines:
                xml_template_lines.insert(xml_title_insert_line, line)
                xml_title_insert_line += 1

        # Save XML file
        out_file = open(self.xml_save_file_path, 'w')
        for line in xml_template_lines:
            print(line, file=out_file)
        out_file.close()

        # Close main window
        self.window.close()

        PyFlameMessageWindow(
            message='XML Exported.',
            title='SRT to XML: Operation Complete',
            )

        # Reveal in MediaHub if button is selected
        if self.reveal_in_mediahub_button.isChecked():
            flame.go_to('MediaHub')
            flame.mediahub.files.set_path(self.xml_save_file_path.rsplit('/', 1)[0])

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Convert SRT to XML',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': ConvertSRT,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
