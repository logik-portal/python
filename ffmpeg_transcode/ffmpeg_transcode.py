# ffmpeg Transcode
# Copyright (c) 2026 Kyle Obley
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
Script Name:    ffmpeg Transcode
Script Version: 1.0.0
Flame Version:  2025.1
Written by:     Kyle Obley
Creation Date:  06.30.26
Update Date:    06.30.26

License:        GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type:    Media Hub

Description:

    Transcodes the selected .mov files to .mp4 using specified bit-rates from both audio and video
    when the supplied profiles don't match a delivery specification and you want to avoid the likes
    of Media Encoder, etc.

Menus:

    Flame Media Hub -> Right-click -> ffmpeg Transcode

To install:

    Copy script into /opt/Autodesk/shared/python/ffmpeg_transcode

Updates:

    v1.0.0 06.30.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import flame
import subprocess
from lib.pyflame_lib_ffmpeg_transcode import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME    = 'ffmpeg Transcode'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH    = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class ffmpeg_transcode:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Make selection available to the other functions
        self.selection = selection

        # Open main window
        self.main_window()

    # Set-up the sub-process to do all the heavy lifting.
    def do_transcode(self, file, video_frmt, vbr, buffer, audio_frmt, abr, append_name, subfolder):

        source_folder = os.path.dirname(file)
        source_filename = os.path.splitext(os.path.basename(file))[0]

        # Create sub-folder if that's been selected.
        if subfolder:
            destination_folder = os.path.join(source_folder, "transcoded")
            if not os.path.isdir(destination_folder):
                os.makedirs(destination_folder)

        # Destination folder is same as source folder
        else:
            destination_folder = source_folder

        # If the append name isn't blank, add it to the existing name with an underscore.
        if append_name != "":
            destination_filename = source_filename + "_" + append_name

        # Add video format to end
        destination_filename = destination_filename + "." + video_frmt

        # Set full file path
        destination_file = os.path.join(destination_folder, destination_filename)

        
        print ("-------- ffmpeg Transcode --------\n")
        print (f"Source:          {file}")
        print (f"Destination:     {destination_file}")
        print (f"Video Format:    {video_frmt}")
        print (f"Video Bitrate:   {vbr}")
        print (f"Buffer Size:     {buffer}")
        print (f"Audio Format:    {audio_frmt}")
        print (f"Audio Bitrate:   {abr}")
        print ("----------------------------------\n")

        # Create the subprocess
        transcode = subprocess.Popen(
            ["ffmpeg", "-nostdin", "-y", "-i", file, "-c:v", "libx264", "-b:v", vbr,
             "-maxrate", vbr, "-bufsize", buffer, "-pix_fmt", "yuv420p",
             "-c:a", audio_frmt, "-b:a", abr, "-preset", "slow",
             "-movflags", "+faststart", destination_file],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,   # merge stderr into stdout, one stream to read
            text=True,
            bufsize=1,
        )

        for line in transcode.stdout:
            print(line, end="")

        # Might remove this. It locks Flame out.
        transcode.wait()

        print(f"Return code: {transcode.returncode}")

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for script.
        """

        def setup_transcode() -> None:
            """
            Gathers all the values and formats them to be passed to the function that
            calls the actual ffmpeg process.
            """

            self.window.close()

            # Get video values
            video_frmt = self.video_frmt_menu.text
            raw_vbr = int(self.vbr_text.text)
            vbr_type = self.vbr_measure.text

            # Set buffer & convert to a string
            buffer = raw_vbr * 2
            buffer = str(buffer)

            # Format the VBR with the correct rate & set the buffer.
            # Buffer being rate * 2
            if vbr_type.startswith('k'):
                vbr = str(raw_vbr) + "k"
                buffer = buffer + "k"
            else:
                vbr = str(raw_vbr) + "M"
                buffer = buffer + "M"

            # Get audio values
            audio_frmt = self.audio_frmt_menu.text
            abr = self.abr_text.text + "k"

            # Append Name
            append_name = self.append_text.text
            
            # Replace and spaces with underscores
            append_name = append_name.replace(" ", "_")


            if self.subfolder_button.isChecked():
                subfolder = True
            else:
                subfolder = False

            # Send each selected file to do_transcode with the entered values.
            for item in self.selection:
                self.do_transcode(item.path, video_frmt, vbr, buffer, audio_frmt, abr, append_name, subfolder)

        def close_window() -> None:
            """
            Close window when escape is pressed.
            """

            self.window.close()

        # ------------------------------------------------------------------------------
        # [Start Window Build]
        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            parent=None,
            escape_pressed=close_window,
            grid_layout_columns=3,
            grid_layout_rows=7,
            )

        # Labels
        self.vbr_label = PyFlameLabel(
            text='Video Bitrate',
            style=Style.NORMAL,
            align=Align.LEFT,
            )
        self.abr_label = PyFlameLabel(
            text='Audio Bitrate (kbps)',
            style=Style.NORMAL,
            align=Align.LEFT,
            )
        self.append_label = PyFlameLabel(
            text='Append Name',
            style=Style.NORMAL,
            align=Align.LEFT,
            )
        self.video_fmt_label = PyFlameLabel(
            text='Video Format',
            style=Style.NORMAL,
            align=Align.LEFT,
            )
        self.audio_fmt_label = PyFlameLabel(
            text='Audio Format',
            style=Style.NORMAL,
            align=Align.LEFT,
            )

        # Buttons
        self.cancel_button = PyFlameButton(
            text='Cancel',
            color=Color.GRAY,
            connect=close_window,
            tooltip='',
            )
        self.transcode_button = PyFlameButton(
            text='Transcode',
            color=Color.BLUE,
            tooltip='',
            connect=setup_transcode,
            )

        self.subfolder_button = PyFlamePushButton(
            text='Transcode Sub-folder',
            checked=False,
            tooltip='',
            )

        # Menus
        self.video_frmt_menu = PyFlameMenu(
            text='mp4',
            menu_options=['mp4'],
            align=Align.LEFT,
            menu_indicator=False,
            tooltip='',
            )
        self.audio_frmt_menu = PyFlameMenu(
            text='aac',
            menu_options=['aac'],
            align=Align.LEFT,
            menu_indicator=False,
            tooltip='',
            )
        self.vbr_measure = PyFlameMenu(
            text='Mbps',
            menu_options=['kbps', 'Mbps'],
            align=Align.LEFT,
            menu_indicator=False,
            tooltip='',
            )

        # Text Edits
        self.vbr_text = PyFlameTextEdit(
            text='20',
            text_type=TextType.PLAIN,
            text_style=TextStyle.EDITABLE,
            )
        self.abr_text = PyFlameTextEdit(
            text='128',
            text_type=TextType.PLAIN,
            text_style=TextStyle.EDITABLE,
            )
        self.append_text = PyFlameTextEdit(
            text='youtube',
            text_type=TextType.PLAIN,
            text_style=TextStyle.EDITABLE,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.window.grid_layout.addWidget(self.video_fmt_label, 0, 0)
        self.window.grid_layout.addWidget(self.video_frmt_menu, 0, 1)
        self.window.grid_layout.addWidget(self.vbr_label, 1, 0)
        self.window.grid_layout.addWidget(self.vbr_text, 1, 1)
        self.window.grid_layout.addWidget(self.vbr_measure, 1, 2)
        self.window.grid_layout.addWidget(self.audio_fmt_label, 2, 0)
        self.window.grid_layout.addWidget(self.audio_frmt_menu, 2, 1)
        self.window.grid_layout.addWidget(self.abr_label, 3, 0)
        self.window.grid_layout.addWidget(self.abr_text, 3, 1)
        self.window.grid_layout.addWidget(self.append_label, 4, 0)
        self.window.grid_layout.addWidget(self.append_text, 4, 1)
        self.window.grid_layout.addWidget(self.subfolder_button, 5, 1)
        self.window.grid_layout.addWidget(self.cancel_button, 6, 1)
        self.window.grid_layout.addWidget(self.transcode_button, 6, 2)


        # ------------------------------------------------------------------------------
        # [End Window Build]
        # ------------------------------------------------------------------------------

# ==============================================================================
# [OP-ATOM fucntion]
# NOT WORKING CURRENTLY
# ==============================================================================
def add_opatom(selection):
    for item in selection:
        file = item.path
        
        source_folder = os.path.dirname(file)
        source_filename = os.path.splitext(os.path.basename(file))[0]
        destination_filename = source_filename + "_temp.mxf"
        destination_file = os.path.join(source_folder, destination_filename)

        print ("-------- ffmpeg Transcode --------\n")
        print (f"Adding OP-ATOM to {file}")
        print ("----------------------------------\n")

        # Create the subprocess
        transcode = subprocess.Popen(
            ["ffmpeg", "-nostdin", "-y", "-i", file, "-map", "0:v:0", "-c:v", "copy", "-an",
             "-f", "mxf_opatom", destination_file],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,   # merge stderr into stdout, one stream to read
            text=True,
            bufsize=1,
        )

        for line in transcode.stdout:
            print(line, end="")

        transcode.wait()

        print(f"Return code: {transcode.returncode}")

        # Overwrite our source with the transcoded file.
        #try:
        #    os.replace(destination_file, file)
        #except OSError as error:
        #    print(f"Some other error occurred: {error}")



# ==============================================================================
# [Scoping]
# ==============================================================================
def is_mov(selection):
    import os
    for item in selection:
        if os.path.splitext(item.path)[1] == '.mov':
            return True
    return False

def is_mxf(selection):
    import os
    for item in selection:
        if os.path.splitext(item.path)[1] == '.mxf':
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_mediahub_files_custom_ui_actions():
    return [
        {
            "name": "ffmepg Transcode",
            "actions": [
                {
                    "name": "Transcode",
                    "isVisable": is_mov,
                    "isEnabled": is_mov,
                    "execute": ffmpeg_transcode,
                    "minimumVersion": "2025.1"
                }
            ]
        }
    ]

