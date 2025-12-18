# Add Dated and Timed Folders
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
Script Name: Add Dated and Timed Folders
Script Version: 2.4.0
Flame Version: 2025
Written by: John Geehreng and Michael Vaglienty
Creation Date: 07.04.20
Update Date: 08.27.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel/MediaHub Files

Description:

    Create folders with the current date and time, date only, or time only.

    Examples of date formats include: YY-MM-DD, YYYY-MM-DD, YYMMDD, etc.

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Add Dated and Timed Folders Setup

    Create Media Panel Folders:
        Right-click on library or folder -> Folders -> Add Dated and Timestamped Folders
        Right-click on library or folder -> Folders -> Add Dated Folder
        Right-click on library or folder -> Folders -> Add Timestamped Folder

    Create MediaHub Files Folders:
        Right-click on folder -> Folders -> Add Dated and Timestamped Folders
        Right-click on folder -> Folders -> Add Dated Folder
        Right-click on folder -> Folders -> Add Timestamped Folder

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.4.0 08.27.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes setup window.
        - Window layer order in linux is now fixed.
        - Time is now always given as four digits.

    v2.3.0 04.07.25
        - Updated to PyFlameLib v4.3.0.

    v2.2.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v2.1.1 12.20.24
        - MediaHub is now refreshed after creating folders.

    v2.1.0 05.21.24
        - Added ability to create folders in the MediaHub Files tab.

    v2.0.0 04.23.24
        - Date and time formats are now customizable from the script setup:
            Flame Main Menu -> Logik -> Logik Portal Script Setup -> Add Dated and Timed Folders Setup

    v1.1.0 03.02.21
        - Updated to work with strftime
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re
import flame
import datetime

from lib.pyflame_lib_add_dated_and_timed_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Add Dated and Timed Folders'
SCRIPT_VERSION = 'v2.4.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class AddDatedAndTimedFolders:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        self.selection = selection

        self.current_date = self.get_current_date(self.settings.date_format)
        self.current_time = self.get_current_time(self.settings.time_format)
        print('Current Date Format:', self.settings.date_format)
        print('Current Date:', self.current_date)
        print('Current Time Format:', self.settings.time_format)
        print('Current Time:', self.current_time, '\n')

    def load_config(self) -> PyFlameConfig:
        """
        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
            PyFlameConfig: Config values as an object with attributes.
        """

        settings = PyFlameConfig(
            config_values={
                'date_format': 'YY-MM-DD',
                'time_format': '24 Hour',
                },
            )

        return settings

    # ------------------------------------------------------------------------------

    def setup(self) -> None:

        def save_config() -> None:
            """
            Save settings to config file and close window.
            """

            def validate_date_format() -> bool:
                """
                Validate that the user input contains a valid combination of date components.
                The input should match patterns containing either (YY, MM, DD) or (YYYY, MM, DD) combinations,
                potentially separated by '-', '/', or '.'. YY, YYYY, MM, DD must all be present in any order.

                Returns:
                    bool: True if the format is valid, False otherwise.
                """

                # Regex pattern to check for date components in any order, with non-alphanumeric separators
                pattern = re.compile(
                    r'^(YY|YYYY|MM|DD)(\W*)(YY|YYYY|MM|DD)(\W*)(YY|YYYY|MM|DD)$'
                    )

                # Search the user format string for the required patterns. If found, return True, otherwise False.
                if pattern.search(self.date_entry.text):
                    return True
                else:
                    return False

            # Validate the date format before saving
            if not validate_date_format():
                PyFlameMessageWindow(
                    message='Invalid date format.\n\nExpected combinations of YY or YYYY with MM and DD.\n\nSuch as: YYYY-MM-DD, MM-DD-YY, YYMMDD, etc.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            self.settings.save_config(
                config_values={
                    'date_format': self.date_entry.text,
                    'time_format': self.time_format_menu.text,
                    }
                )

            self.setup_window.close()

        def close_window():
            """
            Close Window
            ============

            Close setup window.
            """

            self.setup_window.close()

        # Window
        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_rows=3,
            grid_layout_columns=5,
            grid_layout_adjust_column_widths={2: 50},
            parent=None,
            )

        # Labels
        self.date_label = PyFlameLabel(
            text='Date Format',
            )
        self.time_label = PyFlameLabel(
            text='Time Format',
            )

        # Entry
        self.date_entry = PyFlameEntry(
            text=self.settings.date_format,
            tooltip='Enter date format. Example formats include: YY-MM-DD, YYYY-MM-DD, YYMMDD, etc.',
            )

        # Menu
        self.time_format_menu = PyFlameMenu(
            text=self.settings.time_format,
            menu_options=[
                '24 Hour',
                '12 Hour',
                '12 Hour AM/PM'
                ],
            )

        # Buttons
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ------------------------------------------------------------------------------
        # [UI Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.date_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.date_entry, 0, 1)

        self.setup_window.grid_layout.addWidget(self.time_label, 0, 3)
        self.setup_window.grid_layout.addWidget(self.time_format_menu, 0, 4)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 2, 3)
        self.setup_window.grid_layout.addWidget(self.save_button, 2, 4)

        # ------------------------------------------------------------------------------

        self.date_entry.set_focus()

    # ------------------------------------------------------------------------------

    def get_current_date(self, date_format) -> str:
        """
        Get Current Date
        ================

        Convert user-provided date format into a strftime-compatible format string and return the current date formatted accordingly.

        Args
        ----
            date_format (str): Date format string.
                Example formats include:
                    'MM-DD-YY', 'YYYY-MM-DD', 'YYMMDD'

        Returns
        -------
            str:
                The current date formatted according to the user's format.

        Raises
        ------
            ValueError: If the date_format includes unsupported date components or delimiters.

        Examples
        --------
            get_current_date(date_format='MM-DD-YY')
            04-23-24
            get_current_date(date_format='YYYY-MM-DD')
            2024-04-23
            get_current_date(date_format='YYMMDD')
            240423
        """

        # Define the mapping from user input to strftime format
        format_map = {
            'YY': '%y',
            'YYYY': '%Y',
            'MM': '%m',
            'DD': '%d'
        }

        # Start with an empty string to build the strftime format
        strftime_format = ''

        # Variable to track positions in the format string
        i = 0

        # Iterate over each character in the user format
        while i < len(date_format):
            # Try to match four-character elements first (YYYY)
            if i + 4 <= len(date_format) and date_format[i:i+4] in format_map:
                strftime_format += format_map[date_format[i:i+4]]
                i += 4
            # Then try to match two-character elements (YY, MM, DD)
            elif i + 2 <= len(date_format) and date_format[i:i+2] in format_map:
                strftime_format += format_map[date_format[i:i+2]]
                i += 2
            # Handle delimiters directly (dash, slash, etc.)
            elif date_format[i] in '-/.':
                strftime_format += date_format[i]
                i += 1
            else:
                raise ValueError(f'Unsupported date component or delimiter found: {date_format[i]}')

        # Get the current date
        current_date = datetime.datetime.now()

        # Format the current date using the constructed strftime format
        formatted_date = current_date.strftime(strftime_format)

        return formatted_date

    def get_current_time(self, time_format) -> str:
        """
        Get Current Time
        ================

        Return the current time in HHMM format according to the specified time format.

        Args
        ----
            time_format (str):
                The time format specified by the user, which can be one of
                '24 Hour', '12 Hour', or '12 Hour AM/PM'.

        Returns
        -------
            str:
                The current time formatted as HHMM or HHMM AM/PM, depending on the specified format.

        Raises
        ------
            ValueError:
                If the provided time_format is not one of the specified valid options.

        Examples
        --------
            24 Hour:
                1830
            12 Hour:
                0630
            12 Hour AM/PM
                0630 PM
        """

        # Get the current time
        now = datetime.datetime.now()

        # Format the current time based on the provided format
        if time_format == '24 Hour':
            return now.strftime('%H%M')
        elif time_format == '12 Hour':
            return now.strftime('%I%M')
        elif time_format == '12 Hour AM/PM':
            return now.strftime('%I%M %p') # Include AM/PM
        else:
            raise ValueError("Invalid time format. Choose '24hr', '12hr', or '12hr-am/pm'.")

    # ------------------------------------------------------------------------------
    # [Media Panel Operations]
    # ------------------------------------------------------------------------------

    def date_time_folders(self):
        """
        Date and Time Folders
        =====================

        Create a folder with the current date and a subfolder with the current time.
        """

        for item in self.selection:
            item.create_folder(self.current_date).create_folder(self.current_time)
            pyflame.print(f'Created date and timestamped folder: {self.current_date}/{self.current_time}', text_color=TextColor.GREEN)

    def dated_folders(self):
        """
        Dated Folders
        =============

        Create a folder with the current date.
        """

        for item in self.selection:
            item.create_folder(self.current_date)
            pyflame.print(f'Created dated folder: {self.current_date}', text_color=TextColor.GREEN)

    def timed_folders(self):
        """
        Timed Folders
        =============

        Create a folder with the current time.
        """

        for item in self.selection:
            item.create_folder(self.current_time)
            pyflame.print(f'Created timestamped folder: {self.current_time}', text_color=TextColor.GREEN)

    # ------------------------------------------------------------------------------
    # [Media Hub Operations]
    # ------------------------------------------------------------------------------

    def files_date_time_folders(self):
        """
        Files Date and Time Folders
        ===========================

        Create a folder with the current date and a subfolder with the current time.
        """

        for folder in self.selection:
            path = f'{folder.path}{self.current_date}/{self.current_time}'
            if self.create_file_path(path):
                pyflame.print(f'Created date and timestamped folder: {path}', text_color=TextColor.GREEN)

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

    def files_dated_folders(self):
        """
        Files Dated Folders
        ===================

        Create a folder with the current date.
        """

        for folder in self.selection:
            path = f'{folder.path}{self.current_date}'
            if self.create_file_path(path):
                pyflame.print(f'Created dated folder: {path}', text_color=TextColor.GREEN)

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

    def files_timed_folders(self) -> None:
        """
        Files Timed Folders
        ===================

        MediaHubFiles - Create a folder with the current time within the selected folder.
        """

        for folder in self.selection:
            path = f'{folder.path}{self.current_time}'
            if self.create_file_path(path):
                pyflame.print(f'Created timestamped folder: {path}', text_color=TextColor.GREEN)

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

    def create_file_path(self, path) -> bool:
        """
        Create File Path
        ================

        Create folders for the supplied path.

        Args
        ----
            path (str):
                Path to create folders for.

        Returns
        -------
            bool:
                Returns True if folders are created successfully, False if not.
        """

        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
                return True
            except Exception as e:
                print(f'Python Error:', e, '\n')
                pyflame.print(f'Error creating folder: {path}', print_type=PrintType.ERROR)
                return False
        else:
            pyflame.print(f'Folder already exists: {path}', print_type=PrintType.WARNING)
            return False

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

# ------------------------------------------------------------------------------

def setup(selection):

    script = AddDatedAndTimedFolders(selection)
    script.setup()

def date_time_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.date_time_folders()

def dated_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.dated_folders()

def timed_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.timed_folders()

def files_date_time_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.files_date_time_folders()

def files_dated_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.files_dated_folders()

def files_timed_folders(selection):

    script = AddDatedAndTimedFolders(selection)
    script.files_timed_folders()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_library_or_folder(selection):

    for item in selection:
        if isinstance(item, (flame.PyLibrary, flame.PyFolder)):
            return True
    return False

def scope_folder(selection):

    for item in selection:
        if isinstance(item, flame.PyMediaHubFilesFolder):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Folders',
            'actions': [
                {
                    'name': "Add Dated and Timestamped Folders",
                    'order': 1,
                    'isVisible': scope_library_or_folder,
                    'execute': date_time_folders,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Add Dated Folder',
                    'order': 2,
                    'isVisible': scope_library_or_folder,
                    'execute': dated_folders,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Add Timestamped Folder',
                    'order': 3,
                    'isVisible': scope_library_or_folder,
                    'execute': timed_folders,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': 'Folders',
            'actions': [
                {
                    'name': "Add Dated and Timestamped Folders",
                    'order': 1,
                    'isVisible': scope_folder,
                    'execute': files_date_time_folders,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Add Dated Folder',
                    'order': 2,
                    'isVisible': scope_folder,
                    'execute': files_dated_folders,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Add Timestamped Folder',
                    'order': 3,
                    'isVisible': scope_folder,
                    'execute': files_timed_folders,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'Logik',
            'hierarchy': [],
            'actions': []
        },
        {
            'name': 'Logik Portal Script Setup',
            'hierarchy': ['Logik'],
            'order': 2,
            'actions': [
               {
                    'name': 'Add Dated and Timed Folders Setup',
                    'execute': setup,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
