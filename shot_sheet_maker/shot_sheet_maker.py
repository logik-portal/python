# Shot Sheet Maker
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
Script Name: Shot Sheet Maker
Script Version: 3.13.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 02.18.19
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create shot sheets from selected sequence clips that can be loaded into Excel, Google Sheets, or Numbers.

    Shot sheets can be created individually for each sequence or all selected sequences can be added to a
    single spreadsheet as separate worksheets.

    Sequence should have all clips on one version/track.

    *** First time script is run it will need to install xlsxWriter - System password required for this ***
    This will need to happen for each new version of Flame.

URL:
    https://github.com/logik-portal/python/shot_sheet_maker

Menus:

    Right-click on selected sequences in media panel -> Export Shot Sheet

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.13.0 07.10.25
        - Images are linked to cells when opening shot sheet in Excel.
        - Option to save images to shot sheet export path.
        - Updated to PyFlameLib v5.0.0.
        - The tab key can now be used to cycle through all the entries in the Edit Column Names window.

    v3.12.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v3.11.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v3.10.0 08.06.24
        - Updated to PyFlameLib v3.0.0.

    v3.9.1 06.06.24
        - Small UI fixes/adjustments.

    v3.9.0 01.21.24
        - Updates to UI/PySide.

    v3.8.0 11.16.23
        - Added ability to add Shot Frame In and Shot Frame Out to clip info column and column names.
        - Added drop down menus to add clip info to column names in Edit Column Names window.

    v3.7.1 11.07.23
        - Fixed incorrect path in script path check error message.

    v3.7.0 08.20.23
        - Updated to PyFlameLib v2.0.0.

    v3.6.0 06.26.23
        - Pressing return in the main window will now create shot sheets.
        - Updated script versioning to semantic versioning.
        - Updated xlsxwriter install for Flame 2024+.
        - Updated config loading/saving.
        - Fixed linux install problems.

    v3.5 01.05.23
        - Misc bug fixes.
        - Error window will now pop up if the selected export path is not writable.
        - Column names can be edited by clicking on the Edit Column Names button.
        - By using any of the following names for a column name, the corresponding clip info will be added to the cells
          in that column.
          For example, if you want to add the Shot Name to a cell, name the column 'Shot Name' and the shot name will
          be added to the cells in that column.

          Shot Name
          Source Name
          Source Path
          Source TC
          Source TC In
          Source TC Out
          Record TC
          Record TC In
          Record TC Out
          Shot Length
          Source Length
          Comment

    v3.4 10.04.22
        - Updated menus for Flame 2023.2+

    v3.3 08.04.22
        - Fixed bug where script would not work properly if 'Inclusive Out Marks' was selected in Flame Timeline
          Preferences.
        - Added ability to add segment comments to first column with Add Comment button.

    v3.2 07.21.22
        - Spreadsheets can now be created from multiple sequences.
        - When creating spreadsheets from multiple sequences, there is now the option(Create One Workbook) to create a
        single spreadsheet with all sequences
          added as separate worksheets.
        - Fixed export issues with 2023.1.
        - Messages print to Flame message window - Flame 2023.1 and later.

    v3.1 03.25.22
        - Updated UI for Flame 2023.
        - Moved UI widgets to external file.
        - Updated xlsxwriter module to 3.0.3.
        - Gaps in timeline no longer cause script to crash.
        - Misc improvements and bug fixes.
        - Config updated to XML.

    v3.0 05.28.21
        - Updated to be compatible with Flame 2022/Python 3.7.
        - Updated UI.
        - Added check to make sure sequence has only one version/track.
        - Added button to reveal spreadsheet in finder when done.

    v2.2 07.15.20
        - Script setup now in Flame Main Menu: Flame Main Menu -> pyFlame -> Shot Sheet Maker Setup.
        - Window now closes before overwrite warning appears so overwrite warning is not behind window.
        - Better sizing of image column to match size/ratio of sequence images.
        - The following information can be added to the spreadsheet for each shot:
            Source Clip Name
            Source Clip Path
            Source Timecode
            Record Timecode
            Shot Length - Length of shot minus handles
            Source Length - Length of shot plus handles

    v2.1 04.05.20
        - Fixed UI issues in Linux.

    v2.0 12.26.19
        - Up to 20 columns can now be added through the Edit Column Names button.
        - Thumbnail images used in the shot sheet can be saved if desired.
        - Misc. bug fixes.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil
import zipfile
import xml.etree.ElementTree as ET
from collections import OrderedDict

import flame
from lib.pyflame_lib_shot_sheet_maker import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Shot Sheet Maker'
SCRIPT_VERSION = 'v3.13.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ShotSheetMaker:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        self.selection = selection

        # Make sure sequences only have one version/track
        for item in self.selection:
            if len(item.versions) > 1:
                PyFlameMessageWindow(
                    message='Sequences can only have one version/track',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return
            elif len(item.versions[0].tracks) > 1:
                PyFlameMessageWindow(
                    message='Sequences can only have one version/track',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return

        # Make sure no two sequences are named the same
        sequence_names = [str(seq.name)[1:-1] for seq in self.selection]
        duplicate_names = [name for name in sequence_names if sequence_names.count(name) > 1]
        if duplicate_names:
            PyFlameMessageWindow(
                message='No two sequences can have the same name.\n\nRename sequences and try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Define paths
        self.temp_path = os.path.join(SCRIPT_PATH, 'temp')

        # Create temp directory. If it already exists, delete it and create a new one.
        if os.path.isdir(self.temp_path):
            shutil.rmtree(self.temp_path)
        os.mkdir(self.temp_path)

        # Get Flame variables
        self.flame_project_name = flame.projects.current_project.name
        self.current_flame_version = flame.get_version()

        # Initialize misc. variables
        self.thumb_nail_height = ''
        self.thumb_nail_width = ''
        self.x_offset = ''
        self.y_offset = ''
        self.column_width = ''
        self.row_height = ''
        self.temp_image_path = ''

        # Initialize exporter
        self.exporter = flame.PyExporter()
        self.exporter.foreground = True
        self.exporter.export_between_marks = True

        # Get jpeg export preset
        preset_dir = flame.PyExporter.get_presets_dir(
            flame.PyExporter.PresetVisibility.Autodesk,
            flame.PyExporter.PresetType.Image_Sequence)
        jpg_preset_path = os.path.join(preset_dir, "Jpeg", "Jpeg (8-bit).xml")

        # Copy jpeg export preset to temp directory
        self.temp_export_preset = os.path.join(self.temp_path, 'Temp_Export_Preset.xml')
        shutil.copy(jpg_preset_path, self.temp_export_preset)

        # Make sure xlsxwriter is installed, if not, install it. Otherwise, open window.
        xlsxwriter_installed = self.xlsxwriter_check()

        if xlsxwriter_installed:
            return self.main_window()
        return self.install_xlsxwriter()

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
                'export_path': '/opt/Autodesk',
                'thumbnail_size': 'Medium',
                'one_workbook': False,
                'reveal_in_finder': False,
                'add_source_name': False,
                'add_source_path': False,
                'add_source_tc': False,
                'add_record_tc': False,
                'add_shot_length': False,
                'add_source_length': False,
                'add_shot_frame_in': False,
                'add_shot_frame_out': False,
                'add_comment': False,
                'save_images': False,

                'column_01_name': 'Internal Notes',
                'column_02_name': 'Client Notes',
                'column_03_name': 'Shot Description',
                'column_04_name': 'Task',
                'column_05_name': '',
                'column_06_name': '',
                'column_07_name': '',
                'column_08_name': '',
                'column_09_name': '',
                'column_10_name': '',
                'column_11_name': '',
                'column_12_name': '',
                'column_13_name': '',
                'column_14_name': '',
                'column_15_name': '',
                'column_16_name': '',
                'column_17_name': '',
                'column_18_name': '',
                'column_19_name': '',
                'column_20_name': '',
                }
            )

        return settings

    def xlsxwriter_check(self) -> bool:
        """
        XlsxWriter Check

        Check if xlsxWriter is installed by attempting to import it.

        Returns:
        --------
            bool:
                True if xlsxWriter is installed, False if not.
        """

        try:
            import xlsxwriter
            pyflame.print('XlsxWriter Successfully Imported')
            return True
        except:
            pyflame.print('XlsxWriter Not Found, Installing...')

            return False

    def install_xlsxwriter(self) -> None:
        """
        Install XlsxWriter
        ==================

        Install xlsxWriter python package.
        """

        password_window = PyFlamePasswordWindow(
            text='System password is required to install xlsxwriter python package.',
            parent=None,
            )
        #password_window.show()
        system_password = password_window.password

        if system_password:
            python_install_dir = pyflame.get_flame_python_packages_path()
            print('python Install Directory:', python_install_dir)

            # Untar xlsxwriter
            xlsxwriter_tar = os.path.join(SCRIPT_PATH, 'assets/xlsxwriter/xlsxwriter-3.0.3.tgz')

            pyflame.untar(
                tar_file_path=xlsxwriter_tar,
                untar_path=python_install_dir,
                sudo_password=system_password,
                )

            install_dir = os.path.join(python_install_dir, 'xlsxwriter')

            if os.path.isdir(install_dir):
                files = os.listdir(install_dir)
                if files:
                    PyFlameMessageWindow(
                        message='Python xlsxWriter module installed.',
                        title=f'{SCRIPT_NAME}: Operation Complete',
                        parent=None,
                        )
                    flame.execute_shortcut('Rescan Python Hooks')
                    self.main_window()
            else:
                PyFlameMessageWindow(
                    message='Python xlsxWriter module install failed.',
                    parent=None,
                    )

    #-------------------------------------
    # [Windows]
    #-------------------------------------

    def main_window(self):

        def export_path_browse():
            """
            Export Path Browse
            ==================

            Browse for export path. If path is valid, set export path entry to selected path.
            """

            export_path = pyflame.file_browser(
                path=self.export_path_entry.text,
                title='Select Export Path',
                select_directory=True,
                window_to_hide=[self.window],
                )

            if export_path:
                self.export_path_entry.text = export_path

        def save_config():
            """
            Save Config
            ===========

            Save config values to config file. Then create shot sheets.
            """

            # Check export path
            self.settings.export_path = self.export_path_entry.text

            if not os.path.isdir(self.settings.export_path):
                PyFlameMessageWindow(
                    message='Export path not found - Select new path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Check if export path is writeable
            if not os.access(self.settings.export_path, os.W_OK):
                PyFlameMessageWindow(
                    message='Unable to export to selected path - Select new path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            self.settings.save_config(
                config_values={
                    'export_path': self.export_path_entry.text,
                    'thumbnail_size': self.thumbnail_menu.text,
                    'one_workbook': self.one_workbook_push_button.checked,
                    'reveal_in_finder': self.reveal_in_finder_push_button.checked,
                    'add_source_name': self.source_name_push_button.checked,
                    'add_source_path': self.source_path_push_button.checked,
                    'add_source_tc': self.source_tc_push_button.checked,
                    'add_record_tc': self.record_tc_push_button.checked,
                    'add_shot_length': self.shot_length_push_button.checked,
                    'add_source_length': self.source_length_push_button.checked,
                    'add_shot_frame_in':self.shot_frame_in_push_button.checked,
                    'add_shot_frame_out': self.shot_frame_out_push_button.checked,
                    'add_comment': self.comment_push_button.checked,
                    'save_images': self.save_images_push_button.checked,
                    }
                )

            # Hide window
            self.window.hide()

            # Create shot sheets
            self.create_shot_sheets()

            # Close window
            self.window.close()

        def close_window():

            self.window.close()

        #-------------------------------------
        # [Main Window]
        #-------------------------------------

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=12,
            parent=None,
            )

        # Labels
        self.spread_sheet_settings_label = PyFlameLabel(
            text='Spreadsheet Settings',
            style=Style.UNDERLINE,
            )
        self.export_path_label = PyFlameLabel(
            text='Export Path',
            )
        self.thumbnail_size_label = PyFlameLabel(
            text='Thumbnail Size',
            )
        self.clip_info_label = PyFlameLabel(
            text='Clip Info Column',
            style=Style.UNDERLINE,
            )

        # Entries
        self.export_path_entry = PyFlameEntry(
            text=self.settings.export_path,
            )

        # Menu
        self.thumbnail_menu = PyFlameMenu(
            text=self.settings.thumbnail_size,
            menu_options=[
                'Large',
                'Medium',
                'Small',
                ],
            )

        # Push Buttons
        self.one_workbook_push_button = PyFlamePushButton(
            text='Create One Workbook',
            checked=self.settings.one_workbook,
            tooltip='Create one workbook containing separate sheets for each sequence',
            )
        self.reveal_in_finder_push_button = PyFlamePushButton(
            text='Reveal in Finder',
            checked=self.settings.reveal_in_finder,
            )

        self.source_name_push_button = PyFlamePushButton(
            text='Source Name',
            checked=self.settings.add_source_name,
            )
        self.source_path_push_button = PyFlamePushButton(
            text='Source Path',
            checked=self.settings.add_source_path,
            )
        self.source_tc_push_button = PyFlamePushButton(
            text='Source Timecode',
            checked=self.settings.add_source_tc,
            )
        self.record_tc_push_button = PyFlamePushButton(
            text='Record Timecode',
            checked=self.settings.add_record_tc,
            )
        self.shot_length_push_button = PyFlamePushButton(
            text='Shot Length',
            checked=self.settings.add_shot_length,
            )
        self.source_length_push_button = PyFlamePushButton(
            text='Source Length',
            checked=self.settings.add_source_length,
            )
        self.shot_frame_in_push_button = PyFlamePushButton(
            text='Shot Frame In',
            checked=self.settings.add_shot_frame_in,
            )
        self.shot_frame_out_push_button = PyFlamePushButton(
            text='Shot Frame Out',
            checked=self.settings.add_shot_frame_out,
            )
        self.comment_push_button = PyFlamePushButton(
            text='Comment',
            checked=self.settings.add_comment,
            )
        self.save_images_push_button = PyFlamePushButton(
            text='Save Images',
            checked=self.settings.save_images,
            )

        # Buttons
        self.export_path_browse_button = PyFlameButton(
            text='Browse',
            connect=export_path_browse,
            )
        self.edit_column_names_button = PyFlameButton(
            text='Edit Column Names',
            connect=self.edit_column_names_window,
            )
        self.create_button = PyFlameButton(
            text='Create',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.export_path_label, 0, 0)
        self.window.grid_layout.addWidget(self.export_path_entry, 0, 1, 1, 3)
        self.window.grid_layout.addWidget(self.export_path_browse_button, 0, 4)

        self.window.grid_layout.addWidget(self.spread_sheet_settings_label, 3, 0, 1, 5)
        self.window.grid_layout.addWidget(self.thumbnail_size_label, 4, 0)
        self.window.grid_layout.addWidget(self.thumbnail_menu, 4, 1)
        self.window.grid_layout.addWidget(self.edit_column_names_button, 4, 3)
        self.window.grid_layout.addWidget(self.one_workbook_push_button, 4, 4)
        self.window.grid_layout.addWidget(self.save_images_push_button, 5, 4)
        self.window.grid_layout.addWidget(self.reveal_in_finder_push_button, 6, 4)

        self.window.grid_layout.addWidget(self.clip_info_label, 6, 0, 1, 3)

        self.window.grid_layout.addWidget(self.source_name_push_button, 7, 0)
        self.window.grid_layout.addWidget(self.source_path_push_button, 7, 1)
        self.window.grid_layout.addWidget(self.source_tc_push_button, 7, 2)

        self.window.grid_layout.addWidget(self.record_tc_push_button, 8, 0)
        self.window.grid_layout.addWidget(self.shot_length_push_button, 8, 1)
        self.window.grid_layout.addWidget(self.source_length_push_button, 8, 2)

        self.window.grid_layout.addWidget(self.shot_frame_in_push_button, 9, 0)
        self.window.grid_layout.addWidget(self.shot_frame_out_push_button, 9, 1)
        self.window.grid_layout.addWidget(self.comment_push_button, 9, 2)

        self.window.grid_layout.addWidget(self.cancel_button, 11, 3)
        self.window.grid_layout.addWidget(self.create_button, 11, 4)

        #-------------------------------------

        self.export_path_entry.set_focus()

    def edit_column_names_window(self):

        def save_config():
            """
            Save Config
            ===========

            Save column names to config file. Then close window.
            """

            self.settings.save_config(
                config_values={
                    'column_01_name': self.column_01_entry.text,
                    'column_02_name': self.column_02_entry.text,
                    'column_03_name': self.column_03_entry.text,
                    'column_04_name': self.column_04_entry.text,
                    'column_05_name': self.column_05_entry.text,
                    'column_06_name': self.column_06_entry.text,
                    'column_07_name': self.column_07_entry.text,
                    'column_08_name': self.column_08_entry.text,
                    'column_09_name': self.column_09_entry.text,
                    'column_10_name': self.column_10_entry.text,
                    'column_11_name': self.column_11_entry.text,
                    'column_12_name': self.column_12_entry.text,
                    'column_13_name': self.column_13_entry.text,
                    'column_14_name': self.column_14_entry.text,
                    'column_15_name': self.column_15_entry.text,
                    'column_16_name': self.column_16_entry.text,
                    'column_17_name': self.column_17_entry.text,
                    'column_18_name': self.column_18_entry.text,
                    'column_19_name': self.column_19_entry.text,
                    'column_20_name': self.column_20_entry.text,
                    }
                )

            self.edit_window.close()

        def close_window():

            self.edit_window.close()

        #-------------------------------------
        # [Edit Window]
        #-------------------------------------

        self.edit_window = PyFlameWindow(
            title='Edit Column Names',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=9,
            grid_layout_rows=12,
            grid_layout_adjust_column_widths={
                0: 100,
                4: 50,
                5: 100,
                },
            parent=self.window,
            )

        # Labels
        self.column_names_label = PyFlameLabel(
            text='Shot Sheet Column Names',
            style=Style.UNDERLINE,
            )
        self.column_01_label = PyFlameLabel(
            text='Column 01',
            )
        self.column_02_label = PyFlameLabel(
            text='Column 02',
            )
        self.column_03_label = PyFlameLabel(
            text='Column 03',
            )
        self.column_04_label = PyFlameLabel(
            text='Column 04',
            )
        self.column_05_label = PyFlameLabel(
            text='Column 05',
            )
        self.column_06_label = PyFlameLabel(
            text='Column 06',
            )
        self.column_07_label = PyFlameLabel(
            text='Column 07',
            )
        self.column_08_label = PyFlameLabel(
            text='Column 08',
            )
        self.column_09_label = PyFlameLabel(
            text='Column 09',
            )
        self.column_10_label = PyFlameLabel(
            text='Column 10',
            )
        self.column_11_label = PyFlameLabel(
            text='Column 11',
            )
        self.column_12_label = PyFlameLabel(
            text='Column 12',
            )
        self.column_13_label = PyFlameLabel(
            text='Column 13',
            )
        self.column_14_label = PyFlameLabel(
            text='Column 14',
            )
        self.column_15_label = PyFlameLabel(
            text='Column 15',
            )
        self.column_16_label = PyFlameLabel(
            text='Column 16',
            )
        self.column_17_label = PyFlameLabel(
            text='Column 17',
            )
        self.column_18_label = PyFlameLabel(
            text='Column 18',
            )
        self.column_19_label = PyFlameLabel(
            text='Column 19',
            )
        self.column_20_label = PyFlameLabel(
            text='Column 20',
            )

        # Entries
        self.column_01_entry = PyFlameEntry(
            text=self.settings.column_01_name,
            )
        self.column_02_entry = PyFlameEntry(
            text=self.settings.column_02_name,
            )
        self.column_03_entry = PyFlameEntry(
            text=self.settings.column_03_name,
            )
        self.column_04_entry = PyFlameEntry(
            text=self.settings.column_04_name,
            )
        self.column_05_entry = PyFlameEntry(
            text=self.settings.column_05_name,
            )
        self.column_06_entry = PyFlameEntry(
            text=self.settings.column_06_name,
            )
        self.column_07_entry = PyFlameEntry(
            text=self.settings.column_07_name,
            )
        self.column_08_entry = PyFlameEntry(
            text=self.settings.column_08_name,
            )
        self.column_09_entry = PyFlameEntry(
            text=self.settings.column_09_name,
            )
        self.column_10_entry = PyFlameEntry(
            text=self.settings.column_10_name,
            )
        self.column_11_entry = PyFlameEntry(
            text=self.settings.column_11_name,
            )
        self.column_12_entry = PyFlameEntry(
            text=self.settings.column_12_name,
            )
        self.column_13_entry = PyFlameEntry(
            text=self.settings.column_13_name,
            )
        self.column_14_entry = PyFlameEntry(
            text=self.settings.column_14_name,
            )
        self.column_15_entry = PyFlameEntry(
            text=self.settings.column_15_name,
            )
        self.column_16_entry = PyFlameEntry(
            text=self.settings.column_16_name,
            )
        self.column_17_entry = PyFlameEntry(
            text=self.settings.column_17_name,
            )
        self.column_18_entry = PyFlameEntry(
            text=self.settings.column_18_name,
            )
        self.column_19_entry = PyFlameEntry(
            text=self.settings.column_19_name,
            )
        self.column_20_entry = PyFlameEntry(
            text=self.settings.column_20_name,
            )

        # Token Push Button Menus
        clip_info_tokens = {
            'Shot Name': 'Shot Name',
            'Source Name': 'Source Name',
            'Source Path': 'Source Path',
            'Source TC': 'Source TC',
            'Source TC In': 'Source TC In',
            'Source TC Out': 'Source TC Out',
            'Record TC': 'Record TC',
            'Record TC In': 'Record TC In',
            'Record TC Out': 'Record TC Out',
            'Shot Frame In': 'Shot Frame In',
            'Shot Frame Out': 'Shot Frame Out',
            'Shot Length': 'Shot Length',
            'Source Length': 'Source Length',
            'Comment': 'Comment',
            }

        self.column_01_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_01_entry,
            clear_dest=True,
            )
        self.column_02_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_02_entry,
            clear_dest=True,
            )
        self.column_03_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_03_entry,
            clear_dest=True,
            )
        self.column_04_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_04_entry,
            clear_dest=True,
            )
        self.column_05_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_05_entry,
            clear_dest=True,
            )
        self.column_06_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_06_entry,
            clear_dest=True,
            )
        self.column_07_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_07_entry,
            clear_dest=True,
            )
        self.column_08_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_08_entry,
            clear_dest=True,
            )
        self.column_09_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_09_entry,
            clear_dest=True,
            )
        self.column_10_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_10_entry,
            clear_dest=True,
            )
        self.column_11_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_11_entry,
            clear_dest=True,
            )
        self.column_12_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_12_entry,
            clear_dest=True,
            )
        self.column_13_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_13_entry,
            clear_dest=True,
            )
        self.column_14_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_14_entry,
            clear_dest=True,
            )
        self.column_15_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_15_entry,
            clear_dest=True,
            )
        self.column_16_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_16_entry,
            clear_dest=True,
            )
        self.column_17_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_17_entry,
            clear_dest=True,
            )
        self.column_18_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_18_entry,
            clear_dest=True,
            )
        self.column_19_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_19_entry,
            clear_dest=True,
            )
        self.column_20_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_20_entry,
            clear_dest=True,
            )

        # Buttons
        self.save_columns_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.edit_cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.edit_window.grid_layout.addWidget(self.column_names_label, 0, 0, 1, 9)

        self.edit_window.grid_layout.addWidget(self.column_01_label, 1, 0)
        self.edit_window.grid_layout.addWidget(self.column_02_label, 2, 0)
        self.edit_window.grid_layout.addWidget(self.column_03_label, 3, 0)
        self.edit_window.grid_layout.addWidget(self.column_04_label, 4, 0)
        self.edit_window.grid_layout.addWidget(self.column_05_label, 5, 0)
        self.edit_window.grid_layout.addWidget(self.column_06_label, 6, 0)
        self.edit_window.grid_layout.addWidget(self.column_07_label, 7, 0)
        self.edit_window.grid_layout.addWidget(self.column_08_label, 8, 0)
        self.edit_window.grid_layout.addWidget(self.column_09_label, 9, 0)
        self.edit_window.grid_layout.addWidget(self.column_10_label, 10, 0)

        self.edit_window.grid_layout.addWidget(self.column_11_label, 1, 5)
        self.edit_window.grid_layout.addWidget(self.column_12_label, 2, 5)
        self.edit_window.grid_layout.addWidget(self.column_13_label, 3, 5)
        self.edit_window.grid_layout.addWidget(self.column_14_label, 4, 5)
        self.edit_window.grid_layout.addWidget(self.column_15_label, 5, 5)
        self.edit_window.grid_layout.addWidget(self.column_16_label, 6, 5)
        self.edit_window.grid_layout.addWidget(self.column_17_label, 7, 5)
        self.edit_window.grid_layout.addWidget(self.column_18_label, 8, 5)
        self.edit_window.grid_layout.addWidget(self.column_19_label, 9, 5)
        self.edit_window.grid_layout.addWidget(self.column_20_label, 10, 5)

        self.edit_window.grid_layout.addWidget(self.column_01_entry, 1, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_02_entry, 2, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_03_entry, 3, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_04_entry, 4, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_05_entry, 5, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_06_entry, 6, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_07_entry, 7, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_08_entry, 8, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_09_entry, 9, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_10_entry, 10, 1, 1, 2)

        self.edit_window.grid_layout.addWidget(self.column_11_entry, 1, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_12_entry, 2, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_13_entry, 3, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_14_entry, 4, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_15_entry, 5, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_16_entry, 6, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_17_entry, 7, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_18_entry, 8, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_19_entry, 9, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_20_entry, 10, 6, 1, 2)

        self.edit_window.grid_layout.addWidget(self.column_01_token_menu, 1, 3)
        self.edit_window.grid_layout.addWidget(self.column_02_token_menu, 2, 3)
        self.edit_window.grid_layout.addWidget(self.column_03_token_menu, 3, 3)
        self.edit_window.grid_layout.addWidget(self.column_04_token_menu, 4, 3)
        self.edit_window.grid_layout.addWidget(self.column_05_token_menu, 5, 3)
        self.edit_window.grid_layout.addWidget(self.column_06_token_menu, 6, 3)
        self.edit_window.grid_layout.addWidget(self.column_07_token_menu, 7, 3)
        self.edit_window.grid_layout.addWidget(self.column_08_token_menu, 8, 3)
        self.edit_window.grid_layout.addWidget(self.column_09_token_menu, 9, 3)
        self.edit_window.grid_layout.addWidget(self.column_10_token_menu, 10, 3)

        self.edit_window.grid_layout.addWidget(self.column_11_token_menu, 1, 8)
        self.edit_window.grid_layout.addWidget(self.column_12_token_menu, 2, 8)
        self.edit_window.grid_layout.addWidget(self.column_13_token_menu, 3, 8)
        self.edit_window.grid_layout.addWidget(self.column_14_token_menu, 4, 8)
        self.edit_window.grid_layout.addWidget(self.column_15_token_menu, 5, 8)
        self.edit_window.grid_layout.addWidget(self.column_16_token_menu, 6, 8)
        self.edit_window.grid_layout.addWidget(self.column_17_token_menu, 7, 8)
        self.edit_window.grid_layout.addWidget(self.column_18_token_menu, 8, 8)
        self.edit_window.grid_layout.addWidget(self.column_19_token_menu, 9, 8)
        self.edit_window.grid_layout.addWidget(self.column_20_token_menu, 10, 8)

        self.edit_window.grid_layout.addWidget(self.edit_cancel_button, 12, 7)
        self.edit_window.grid_layout.addWidget(self.save_columns_button, 12, 8)

        #-------------------------------------

        self.edit_window.tab_order = [
            self.column_01_entry,
            self.column_02_entry,
            self.column_03_entry,
            self.column_04_entry,
            self.column_05_entry,
            self.column_06_entry,
            self.column_07_entry,
            self.column_08_entry,
            self.column_09_entry,
            self.column_10_entry,
            self.column_11_entry,
            self.column_12_entry,
            self.column_13_entry,
            self.column_14_entry,
            self.column_15_entry,
            self.column_16_entry,
            self.column_17_entry,
            self.column_18_entry,
            self.column_19_entry,
            self.column_20_entry,
            ]

        self.column_01_entry.set_focus()

    #-------------------------------------

    def create_shot_sheets(self):
        """
        Create Shot Sheets
        ==================

        Create shot sheets from selected sequences. Export to xlsx format. Open in Finder if selected.
        """
        import xlsxwriter

        def edit_xlsx_file(xlsx_path):
            """
            Edit XLSX File
            ==============

            Edit the xlsx file to add image links. Links the images to cell in the xlsx file.

            This only works in Excel. It does not work in Google Sheets or Numbers.

            Args
            ----
                xlsx_path (str): Path to the xlsx file to edit.
            """



            def unzip_xlsx(xlsx_path, extract_dir):
                with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)

            def zip_dir(source_dir, zip_path):
                with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for root, dirs, files in os.walk(source_dir):
                        for file in files:
                            full_path = os.path.join(root, file)
                            arcname = os.path.relpath(full_path, source_dir)
                            zipf.write(full_path, arcname)

            def modify_drawing_xml(drawing_xml_path):
                ns = {
                    'xdr': 'http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing',
                }
                ET.register_namespace('', ns['xdr'])

                tree = ET.parse(drawing_xml_path)
                root = tree.getroot()

                for anchor_tag in ['{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}twoCellAnchor',
                                '{http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing}oneCellAnchor']:
                    for anchor in root.findall(anchor_tag):
                        anchor.set('editAs', 'twoCell')  # Options: 'absolute', 'oneCell', 'twoCell'

                tree.write(drawing_xml_path, encoding='utf-8', xml_declaration=True)

            def patch_xlsx_images(xlsx_path, output_path):
                temp_dir = os.path.join(os.path.dirname(xlsx_path), 'temp_xlsx')

                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                os.makedirs(temp_dir)

                # Step 1: Unzip the .xlsx file
                unzip_xlsx(xlsx_path, temp_dir)

                # Step 2: Modify drawing XML files
                drawings_dir = os.path.join(temp_dir, 'xl', 'drawings')
                if os.path.isdir(drawings_dir):
                    for file in os.listdir(drawings_dir):
                        if file.startswith('drawing') and file.endswith('.xml'):
                            full_path = os.path.join(drawings_dir, file)
                            modify_drawing_xml(full_path)

                # Step 3: Zip folder back to .xlsx
                temp_zip = output_path + '.zip'
                zip_dir(temp_dir, temp_zip)

                # Step 4: Rename .zip back to .xlsx
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_zip, output_path)

                # Cleanup
                shutil.rmtree(temp_dir)

            patch_xlsx_images(xlsx_path, xlsx_path)

        def save_images():
            """
            Save Images
            ===========

            Save images to export path if selected.
            """

            # Copy images to export path
            if self.settings.save_images:
                image_path = os.path.join(self.export_path_entry.text, f'{seq_name}_images')
                if not os.path.exists(image_path):
                    os.makedirs(image_path)
                for image in os.listdir(self.temp_image_path):
                    if image.endswith('.jpg'):
                        shutil.copy(os.path.join(self.temp_image_path, image), os.path.join(image_path, image))


        # Sort selected sequences by name
        sequence_names = [str(seq.name)[1:-1] for seq in self.selection]
        sequence_names.sort()

        sorted_sequences = []
        for name in sequence_names:
            for seq in self.selection:
                if str(seq.name)[1:-1] == name:
                    sorted_sequences.append(seq)

        # Create workbooks
        if self.settings.one_workbook:

            xlsx_path = os.path.join(self.export_path_entry.text, 'Shot_Sheets.xlsx')

            # Create single workbook with worksheets for each sequence
            workbook = xlsxwriter.Workbook(xlsx_path)

            for sequence in sorted_sequences:
                seq_name = str(sequence.name)[1:-1]

                # Get shot info and export thumbnails
                self.get_shots(sequence)

                # Create worksheet
                self.create_sequence_worksheet(workbook, seq_name)

                # Save images
                save_images()

            # Close workbook
            workbook.close()

            # Edit xlsx file to add image links for Excel
            edit_xlsx_file(xlsx_path)

        else:
            # Create workbook/worksheet for each sequence
            for sequence in sorted_sequences:
                seq_name = str(sequence.name)[1:-1]

                xlsx_path = os.path.join(self.export_path_entry.text, seq_name + '.xlsx')

                workbook = xlsxwriter.Workbook(xlsx_path)

                # Get shot info and export thumbnails
                self.get_shots(sequence)

                # Create worksheet
                self.create_sequence_worksheet(workbook, seq_name)

                # Save images
                save_images()

                # Close workbook
                workbook.close()

                # Edit xlsx file to add image links for Excel
                edit_xlsx_file(xlsx_path)

        # Delete temp directory
        shutil.rmtree(self.temp_path)

        # Close window
        self.window.close()

        # Show message window
        PyFlameMessageWindow(
            message=f'Shot Sheet(s) Exported:\n\n{self.export_path_entry.text}',
            title=f'{SCRIPT_NAME}: Export Complete',
            parent=self.window,
            )

        if self.settings.reveal_in_finder:
            pyflame.open_in_finder(
                path=self.export_path_entry.text,
                )
            pyflame.print('Finder opened')

        print('Done.\n')

    def get_shots(self, sequence):
        """
        Get Shots
        =========

        Export thumbnails and get shot info for all shots in selected sequence
        """

        def thumbnail_res():

            thumbnail_size = self.thumbnail_menu.text

            seq_height = sequence.height
            seq_width = sequence.width
            seq_ratio = float(seq_width) / float(seq_height)

            if thumbnail_size == 'Small':
                self.thumb_nail_height = 50
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 20

            elif thumbnail_size == 'Medium':
                self.thumb_nail_height = 100
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 30

            elif thumbnail_size == 'Large':
                self.thumb_nail_height = 150
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 31

            self.row_height = self.thumb_nail_height + (self.thumb_nail_height * .2)
            self.column_width = (self.thumb_nail_width + (self.x_offset * 2)) / 7.83
            self.y_offset = ((self.row_height * 1.333) - self.thumb_nail_height) / 2

        def export_thumbnail(self, sequence, segment, shot_name):

            # Create list of existing exported thumbnails to check for extra frames
            temp_image_path_files = os.listdir(self.temp_image_path)

            # Modify export preset with selected resolution
            edit_preset = open(self.temp_export_preset, 'r')
            contents = edit_preset.readlines()
            edit_preset.close()

            contents[8] = f'  <namePattern>{shot_name}</namePattern>\n'
            contents[15] = f'   <width>{self.thumb_nail_width}</width>\n'
            contents[16] = f'   <height>{self.thumb_nail_height}</height>\n'
            contents[26] = '  <framePadding>0</framePadding>\n'

            edit_preset = open(self.temp_export_preset, 'w')
            contents = ''.join(contents)
            edit_preset.write(contents)
            edit_preset.close()

            # Mark in and out in sequence for segment frame to export
            sequence.in_mark = segment.record_in
            sequence.out_mark = segment.record_in + 1

            # Export thumbnail
            self.exporter.export(sequence, self.temp_export_preset, self.temp_image_path)

            # Clear sequence in and out marks
            sequence.in_mark = None
            sequence.out_mark = None

            # Fix for extra frames being exported when Inclusive Out Marks is selected in Flame Timeline Prefs.
            # Check if more than one thumbnail was exported. If so, delete the second frame and rename the first frame to remove the frame number.
            updated_temp_image_path_files = os.listdir(self.temp_image_path)

            if len(updated_temp_image_path_files) - len(temp_image_path_files) == 2:
                new_images = [image for image in updated_temp_image_path_files if image not in temp_image_path_files]

                # Delete first image in new_images list
                os.remove(os.path.join(self.temp_image_path, new_images[0]))

                # Rename second image in new_images list to remove frame number and add to temp_image_path_files list.
                new_image = new_images[1]

                if new_image.count('.') > 1:
                    os.rename(os.path.join(self.temp_image_path, new_image), os.path.join(self.temp_image_path, new_image.split('.')[0] + '.jpg'))
                temp_image_path_files.append(new_image)

        # Create temp directory to store thumbnails
        self.temp_image_path = os.path.join(self.temp_path, str(sequence.name)[1:-1])
        if os.path.exists(self.temp_image_path):
            shutil.rmtree(self.temp_image_path)
        os.makedirs(self.temp_image_path)

        # Set thumbnail size
        thumbnail_res()

        self.shot_dict = OrderedDict()

        # Create dictionary for all shots containing clip info
        for segment in sequence.versions[0].tracks[0].segments:
            if segment.type == 'Video Segment':
                shot_name = str(segment.shot_name)[1:-1]
                if not shot_name:
                    shot_name = str(segment.name)[1:-1]

                # Export thumbnail for segment
                export_thumbnail(self, sequence, segment, shot_name)

                self.clip_info_list = []

                self.clip_info_list.append(f'Shot Name: {shot_name}')
                self.clip_info_list.append(f'Source Name: {str(segment.source_name)}')
                self.clip_info_list.append(f'Source Path: {segment.file_path}')
                self.clip_info_list.append(f'Source TC: {str(segment.source_in)[1:-1]} - {str(segment.source_out)[1:-1]}')
                self.clip_info_list.append(f'Source TC In: {str(segment.source_in)[1:-1]}')
                self.clip_info_list.append(f'Source TC Out: {str(segment.source_out)[1:-1]}')
                self.clip_info_list.append(f'Record TC: {str(segment.record_in)[1:-1]} - {str(segment.record_out)[1:-1]}')
                self.clip_info_list.append(f'Record TC In: {str(segment.record_in)[1:-1]}')
                self.clip_info_list.append(f'Record TC Out: {str(segment.record_out)[1:-1]}')
                self.clip_info_list.append(f'Shot Frame In: {str(flame.PyTime(segment.record_in.relative_frame))}')
                self.clip_info_list.append(f'Shot Frame Out: {str(flame.PyTime(segment.record_out.relative_frame))}')
                self.clip_info_list.append(f'Shot Length: {str(segment.record_duration)[1:-1]} - {str(flame.PyTime(segment.record_duration.frame))} Frames')

                # Source length can be inifinite for things like solid colors, check for this.
                if segment.source_duration != 'infinite':
                    self.clip_info_list.append(f'Source Length: {str(segment.source_duration)[1:-1]} - {str(flame.PyTime(segment.source_duration.frame))} Frames')
                else:
                    self.clip_info_list.append('Source Length: Infinite')

                self.clip_info_list.append(f'Comment: {str(segment.comment)[1:-1]}')

                print(f'{shot_name} Clip Info:\n')
                for info in self.clip_info_list:
                    print(f'    {info}')
                print('\n')

                self.shot_dict.update({shot_name : self.clip_info_list})

    def create_sequence_worksheet(self, workbook, seq_name):

        def create_column_names_list() -> list:
            """
            Create list of column names with no empty entries at end of list
            """

            column_names = [
                self.settings.column_01_name,
                self.settings.column_02_name,
                self.settings.column_03_name,
                self.settings.column_04_name,
                self.settings.column_05_name,
                self.settings.column_06_name,
                self.settings.column_07_name,
                self.settings.column_08_name,
                self.settings.column_09_name,
                self.settings.column_10_name,
                self.settings.column_11_name,
                self.settings.column_12_name,
                self.settings.column_13_name,
                self.settings.column_14_name,
                self.settings.column_15_name,
                self.settings.column_16_name,
                self.settings.column_17_name,
                self.settings.column_18_name,
                self.settings.column_19_name,
                self.settings.column_20_name,
                ]

            # Create list of column names with no empty entries at end of list
            i = len(column_names) - 1
            while i >= 0:
                # If the current element is empty, remove it from the list
                if not column_names[i]:
                    column_names.pop(i)
                # If the current element is not empty, stop the loop
                else:
                    break
                # Move to the next element
                i -= 1

            #print('column_names:', column_names)

            return column_names

        def add_clip_info_column(clip_info) -> None:
            """
            This will add a column for clip info and populate it with the selected options.
            """

            # If clip info True fill in clip info
            if clip_info:
                worksheet.set_column('B:B', 50)

                clip_info_row = 3

                for shot in self.shot_dict:

                    # Add shot name to clip info - This is always added
                    clip_info = str(self.shot_dict[shot][0])

                    # Add source name to clip info
                    if self.settings.add_source_name:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][1])

                    # Add source path to clip info
                    if self.settings.add_source_path:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][2])

                    # Add source tc to clip info
                    if self.settings.add_source_tc:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][3])

                    # Add record tc to clip info
                    if self.settings.add_record_tc:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][6])

                    # Add shot length to clip info
                    if self.settings.add_shot_length:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][9])

                    # Add source length to clip info
                    if self.settings.add_source_length:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][10])

                    # Add comment to clip info
                    if self.settings.add_comment:
                        clip_info = clip_info + '\n' + str(self.shot_dict[shot][11])

                    worksheet.write(clip_info_row, 1, clip_info)
                    clip_info_row += 2

        def add_token_clip_info() -> None:
            """
            Add the clip info to the cell in the column of each row of the same name. To add clip info
            to a cell in the column of each row of the same name, the column name must be one of the info_tokens.
            """

            # List of clip info tokens to check against column names
            info_tokens = [
                'Shot Name',
                'Source Name',
                'Source Path',
                'Source TC',
                'Source TC In',
                'Source TC Out',
                'Record TC',
                'Record TC In',
                'Record TC Out',
                'Shot Frame In',
                'Shot Frame Out',
                'Shot Length',
                'Source Length',
                'Comment',
                ]

            # Add clip info to the cell in the column of each row of the same name
            start_column = 1
            info_row = 3

            for key in self.shot_dict:
                for name in column_names:
                    if name in info_tokens:
                        column_number = column_names.index(name) + start_column
                        info = self.shot_dict[key][info_tokens.index(name)].split(': ', 1)[1]
                        worksheet.write(info_row, column_number, info)
                info_row += 2

        # Are any clip info buttons selected
        if self.source_name_push_button.checked:
            clip_info = True
        elif self.source_path_push_button.checked:
            clip_info = True
        elif self.source_tc_push_button.checked:
            clip_info = True
        elif self.record_tc_push_button.checked:
            clip_info = True
        elif self.shot_length_push_button.checked:
            clip_info = True
        elif self.source_length_push_button.checked:
            clip_info = True
        else:
            clip_info = False

        # Create worksheet
        worksheet = workbook.add_worksheet(seq_name)
        worksheet.set_column('A:A', self.column_width)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        cell_format = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'bg_color': '#d6d6d6',
                'bold': True,
                'font_color': 'black'
                }
            )
        cell_format02 = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'bg_color': '#adadad',
                'align': 'top',
                'text_wrap': True
                }
            )
        cell_format03 = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'align': 'top',
                'text_wrap': True
                }
            )

        worksheet.set_row(0, cell_format=cell_format02)
        worksheet.set_row(1, cell_format=cell_format02)

        shot_name_insert_row = 3
        image_insert_row = 4

        if clip_info:
            line_height = (len(self.clip_info_list) * 13) + 26
            if line_height > self.row_height:
                self.row_height = line_height
                self.y_offset = ((line_height * 1.333) - self.thumb_nail_height) / 2

        shot_name_row_list = []

        for image in self.shot_dict:
            image_path = os.path.join(self.temp_image_path, image) + '.jpg'
            worksheet.set_row(shot_name_insert_row, self.row_height, cell_format=cell_format03)
            shot_name_row = 'A' + str(shot_name_insert_row)
            image_row = 'A' + str(image_insert_row)
            shot_name_row_list.append(shot_name_row)
            worksheet.write(shot_name_row, image, cell_format)
            worksheet.insert_image(image_row, image_path, {'x_offset': self.x_offset, 'y_offset': self.y_offset})
            shot_name_insert_row = shot_name_insert_row + 2
            image_insert_row = image_insert_row + 2

        # Create list of column names
        column_names = create_column_names_list()

        # If clip info True add clip info column
        if clip_info:
            column_names.insert(0, 'Clip Info')

        # Add sequence name to cell above first shot
        worksheet.write(1, 0, seq_name)

        # List to hold column codes
        column_code_list = []

        # Set column letter iteration
        column_letter = 'A'

        # Iterate through alphabet to create column codes
        for _ in column_names:
            column_letter = chr(ord(column_letter) + 1)
            column_code = column_letter + '2'
            column_code_list.append(column_code)

        # Add column names and set column width
        for (code, val) in zip(column_code_list, column_names):
            column_letter = re.split(r'(\d+)', code)[0]
            column_width_code = column_letter + ':' + column_letter
            worksheet.write(code, val, cell_format02)
            worksheet.set_column(column_width_code, 25)

        # If any clip info button is checked add clip info column
        add_clip_info_column(clip_info)

        # Check column names for info tokens and add clip info to those cells
        add_token_clip_info()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence, flame.PyClip)):
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
                    'name': 'Shot Sheet Maker',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_sequence,
                    'execute': ShotSheetMaker,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
