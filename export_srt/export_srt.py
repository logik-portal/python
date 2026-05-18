"""
Script Name: Export SRT
Script Version: 2.0.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 07.22.20
Update Date: 04.30.26

Custom Action Type: Timeline

Description:

    Export SRT file from timeline Text FX.

Menu:

    Right-click on selected clips with timeline text fx -> SRT... -> Export SRT

To install:

    Copy script into /opt/Autodesk/shared/python/export_srt

Updates:

    v2.0.0 04.30.26

        - Updated to work with PySide6/Flame 2025+

    v1.3 07.18.22

        Messages print to Flame message window - Flame 2023.1 and later

        Flame file browser used to select export path - Flame 2023.1 and later

    v1.2 03.30.22

        Updated config to xml

        Updated UI for Flame 2023

        UI Widgets moved to external file

    v1.1 10.23.21

        Updated to be compatible with Flame 2022/Python 3.7
"""

import xml.etree.ElementTree as ET
import os, shutil
from pyflame_lib_export_srt import FlameMessageWindow, pyflame_print, pyflame_file_browser, pyflame_open_in_finder

SCRIPT_NAME = 'Export SRT'
SCRIPT_PATH = '/opt/Autodesk/shared/python/export_srt'
VERSION = 'v2.0.0'

class ExportSRT():

    def __init__(self, selection):

        print ('>' * 10, f'{SCRIPT_NAME} {VERSION}', '<' * 10, '\n')

        self.selection = selection

        self.temp_save_path = '/opt/Autodesk/shared/python/export_srt/temp'
        if not os.path.isdir(self.temp_save_path):
            os.makedirs(self.temp_save_path)

        self.temp_text_file = os.path.join(self.temp_save_path, 'temp_text.ttg_node')

        # Load config

        self.config()

        # Init variables

        self.seq_name = ''
        self.text_lines = []
        self.srt_block_list = []
        self.record_in = ''
        self.record_out = ''
        self.frame_rate = ''
        self.srt_timecode = ''

    def config(self):

        def get_config_values():

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            # Get Settings

            for setting in root.iter('export_srt_settings'):
                self.export_path = setting.find('export_path').text

            pyflame_print(SCRIPT_NAME, 'Config loaded.')

        def create_config_file():

            if not os.path.isdir(self.config_path):
                try:
                    os.makedirs(self.config_path)
                except:
                    FlameMessageWindow('error', f'{SCRIPT_NAME}: Error', f'Unable to create folder: {self.config_path}<br>Check folder permissions')

            if not os.path.isfile(self.config_xml):
                print ('--> config file does not exist, creating new config file ')

                config = """
<settings>
    <export_srt_settings>
        <export_path>/</export_path>
    </export_srt_settings>
</settings>"""

                with open(self.config_xml, 'a') as config_file:
                    config_file.write(config)
                    config_file.close()

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        if os.path.isfile(self.config_xml):
            get_config_values()
        else:
            create_config_file()
            if os.path.isfile(self.config_xml):
                get_config_values()

    def export_srt(self):
        import flame

        def save_config():

            # Save settings to config file

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            export_path = root.find('.//export_path')
            export_path.text = self.export_path

            xml_tree.write(self.config_xml)

            pyflame_print(SCRIPT_NAME, 'Config saved.')

        self.export_path = self.path_browse()

        if self.export_path:

            save_config()

            event_number = 1

            # Get sequence name and frame rate

            self.get_seqeunce_info()

            for seg in self.selection:
                if isinstance(seg, flame.PySegment):
                    for fx in seg.effects:
                        if fx.type == 'Text':

                            # Get segment in and out timecode

                            record_in = str(seg.record_in)[1:-1]
                            record_out = str(seg.record_out)[1:-1]

                            converted_record_in = self.convert_timecode(record_in, 'in')
                            converted_record_out = self.convert_timecode(record_out, 'out')

                            seg_timecode = converted_record_in + ' --> ' + converted_record_out

                            # Save text fx file

                            fx.save_setup(self.temp_text_file)

                            # Get segment text lines

                            self.read_text_file()

                            # Convert ascii to text

                            self.text_convert()

                            # Segment to list

                            self.srt_block_list.append(event_number)
                            self.srt_block_list.append(seg_timecode)
                            for line in self.line_list:
                                self.srt_block_list.append(line)
                            self.srt_block_list.append('')

                            event_number += 1

            self.export_file()
        else:
            pyflame_print(SCRIPT_NAME, 'Nothing exported.')

        # Remove temp folder

        shutil.rmtree(self.temp_save_path)
        print ('--> cleaning up temp files\n')

        pyflame_print(SCRIPT_NAME, 'Export complete.')

    def path_browse(self):

        path = pyflame_file_browser('Select Export Path', [''], self.export_path, select_directory=True)
        if path:
            return path

    def get_seqeunce_info(self):

        # Get name and frame rate of segment sequence

        for seg in self.selection:
            track = seg.parent
            version = track.parent
            sequence = version.parent
            self.seq_name = str(sequence.name)[1:-1]
            self.frame_rate = float(str(sequence.frame_rate)[:-4])
            break

        print ('sequence_name:', self.seq_name)
        print ('frame_rate:', self.frame_rate, '\n')

    def convert_timecode(self, timecode, in_out):

        if self.frame_rate == '50':
            self.frame_rate = '25'
        elif self.frame_rate == '59.94':
            self.frame_rate = '29.97'
        elif self.frame_rate == '60':
            self.frame_rate = '30'

        milliseconds_per_frame = 1000/float(self.frame_rate)

        hours_mins_secs = timecode[:-3]

        frames = timecode[-2:]

        # Add one extra frame to out timecode

        if in_out == 'out':
            frames = str(int(frames) + 1)

        milliseconds = str(int(round(float(frames)*milliseconds_per_frame)))

        if len(milliseconds) == 1:
            milliseconds = '00' + milliseconds
        elif len(milliseconds) == 2:
            milliseconds = '0' + milliseconds
        elif len(milliseconds) == 4:
            # Remove first number from milliseconds and add one to seconds
            milliseconds = milliseconds[1:]
            hours = hours_mins_secs[:2]
            print ('hours:', hours)
            mins = hours_mins_secs[3:-3]
            print ('mins:', mins)
            seconds = str(int(hours_mins_secs[-2:]) + 1)
            print ('seconds:', seconds)

            if len(seconds) == 1:
                seconds = '0' + seconds

            if seconds == '60':
                seconds = '00'
                mins = str(int(mins)) + 1
                if len(mins) == 1:
                    mins = '0' + mins

            if mins == '60':
                mins = '00'
                hours = str(int(hours)) + 1
                if len(hours) == 1:
                    hours = '0' + hours

            hours_mins_secs = hours + ':' + mins + ':' + seconds

        converted_timecode = hours_mins_secs + ',' + milliseconds

        return converted_timecode

    def read_text_file(self):

        # Get text lines from saved timeline text fx

        get_text_values = open(self.temp_text_file, 'r')
        lines = get_text_values.read()

        split_lines = lines.split('>')

        self.text_lines = [l.split('<', 1)[0] for l in split_lines if '</Text' in l]

        while '' in self.text_lines:
            self.text_lines.remove('')

        get_text_values.close()

    def text_convert(self):

        # Convert ascii to plain text

        self.line_list = []

        for line in self.text_lines:
            ascii_list = line.split()
            for i in range(0, len(ascii_list)):
                ascii_list[i] = int(ascii_list[i])
            result = ''.join(map(chr, ascii_list))
            self.line_list.append(result)

    def export_file(self):

        try:
            self.srt_export_file = os.path.join(self.export_path, self.seq_name) + '.srt'

            out_file = open(self.srt_export_file, 'w')
            for line in self.srt_block_list:
                print(line, file=out_file)
            out_file.close()

            if FlameMessageWindow('confirm', f'{SCRIPT_NAME}: Operation Complete', f'SRT File Exported:<br><br>{self.srt_export_file}<br><br>Open path file browser?'):
                #self.open_finder(self.export_path)
                pyflame_open_in_finder(self.export_path)

        except OSError as error:
            FlameMessageWindow('error', f'{SCRIPT_NAME}: Error', f'SRT file not exported<br><br>Check file path permissions:<br><br>{error}')

# -------------------------------------- #

def export(selection):

    script = ExportSRT(selection)
    script.export_srt()

def scope_segment(selection):
    import flame

    if isinstance(selection[0], flame.PySegment):
        tlfx = selection[0].effects
        for fx in tlfx:
            if fx.type == 'Text':
                return True
    return False

def get_timeline_custom_ui_actions():

    return [
        {
            'name': 'SRT...',
            'actions': [
                {
                    'name': 'Export SRT',
                    'isVisible': scope_segment,
                    'execute': export,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
