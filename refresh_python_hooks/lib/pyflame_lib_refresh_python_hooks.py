# PyFlame Library
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
Script Name: PyFlame Library
Version: 4.3.1
Written by: Michael Vaglienty
Creation Date: 10.31.20
Update Date: 04.14.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

This file contains a library of various custom UI widgets that can be used to build QT windows similar to the look of Flame along with some other useful functions.

This file should be placed in same folder as main script.

To avoid conflicts with having multiple copies within the Flame python packages folder, file should be renamed to: pyflame_lib_<script name>.py

This is the required folder structure when using this library:

    script_folder/
    ├── main_script.py
    ├── lib/
    │   └── pyflame_lib_<main_script_name>.py
    ├── assets/
    │   └── fonts/
    │       └── Montserrat-Regular.ttf
    │       └── Montserrat-Light.ttf
    │       └── Montserrat-Thin.ttf

Required Files:
    - Montserrat-Regular.ttf
    - Montserrat-Light.ttf
    - Montserrat-Thin.ttf
    - pyflame_lib_<main_script_name>.py (This file with the name of the main script added to the end of the file name)

All paths are relative to the script's root directory.
Make sure this structure is preserved when deploying or moving the script.

To import the library in a script, use:

    from lib.pyflame_lib_<main_script_name> import *

Check README.md for more information.
"""

#---------------------------------------------
# [Imports]
#---------------------------------------------

import csv
import datetime
import json
import os
import platform
import re
import shutil
import subprocess
import traceback
import xml.etree.ElementTree as ET
from enum import Enum
from functools import partial
from subprocess import PIPE, Popen
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import flame

#--------------------------------------------
# [PySide Imports]
#--------------------------------------------

# Try to import PySide6, otherwise import PySide2

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtGui import QAction
    from PySide6.QtCore import QRegularExpression
    from PySide6.QtGui import QRegularExpressionValidator as QValidator

except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import QRegExp as QRegularExpression
    from PySide2.QtGui import QRegExpValidator as QValidator
    QAction = QtWidgets.QAction

#---------------------------------------------
# [Constants]
#---------------------------------------------

# Get script name from file name. Removes 'pyflame_lib_' and '.py' from file name.
LIB_PATH = os.path.abspath(__file__).rsplit("/", 1)[0]
SCRIPT_NAME = LIB_PATH.rsplit("/", 2)[1].title().replace('_', ' ')
SCRIPT_PATH = LIB_PATH.rsplit("/", 1)[0]

SHARED_FILE_SEQUENCE_PATH = '/opt/Autodesk/shared/export/presets/file_sequence'
SHARED_MOVIE_EXPORT_PATH = '/opt/Autodesk/shared/export/presets/movie_file'
PROJECT_FILE_SEQUENCE_PATH = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/file_sequence')
PROJECT_MOVIE_EXPORT_PATH = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/movie_file')

#---------------------------------------------
# [PyFlame Enums]
#---------------------------------------------
# For internal script use only.
# Not meant to be used outside of this file.
#---------------------------------------------

class Color(Enum):
    """
    Color
    ======

    Enum for storing color values used in the PyFlame UI elements. This class helps in maintaining a consistent
    color scheme throughout the application, making it easy to change colors in a centralized manner.

    Each color is represented as an RGB value string, which can be used to style different elements
    in the application, such as text, buttons, borders, and backgrounds.

    Examples
    --------
        To set a button background color:
        ```
        button.setStyleSheet(f'background-color: {Color.GRAY.value};')
        ```

        To set a text color for a label:
        ```
        label.setStyleSheet(f'color: {Color.TEXT.value};')
        ```
    """

    BLUE = 'rgb(0, 110, 175)'
    RED = 'rgb(200, 29, 29)'
    YELLOW = 'rgb(160, 143, 48)'
    GREEN = 'rgb(0, 255, 0)'
    TEAL = 'rgb(0, 255, 255)'

    BLUE_TRANS = 'rgba(0, 43, 66, 0.2)'
    RED_TRANS = 'rgba(200, 29, 29, 0.15)'
    YELLOW_TRANS = 'rgba(255, 255, 0, 0.15)'
    GREEN_TRANS = 'rgba(0, 255, 0, 0.15)'
    TEAL_TRANS = 'rgba(0, 255, 255, 0.15)'

    GRAY = 'rgb(58, 58, 58)'
    DARK_GRAY = 'rgb(30, 30, 30)'
    BRIGHT_GRAY = 'rgb(71, 71, 71)'
    BLACK = 'rgb(0, 0, 0)'
    WHITE = 'rgb(255, 255, 255)'

    TEXT = 'rgb(154, 154, 154)'
    TEXT_BRIGHT = 'rgb(185, 185, 185)'
    TEXT_SELECTED = 'rgb(210, 210, 210)'
    TEXT_DISABLED = 'rgb(116, 116, 116)'
    TEXT_UNDERLINE = 'rgb(40, 40, 40)'
    TEXT_BORDER = 'rgb(64, 64, 64)'
    TEXT_READ_ONLY_BACKGROUND = 'rgb(30, 30, 30)'

    BUTTON_TEXT = 'rgb(165, 165, 165)'
    SELECTED_GRAY = 'rgb(71, 71, 71)'

    BORDER = 'rgb(90, 90, 90)'
    BORDER_BRIGHTER = 'rgb(120, 120, 120)'

    UNDERLINE = 'rgb(40, 40, 40, 1)'

    ENTRY_GRAY = 'rgb(54, 54, 54)'

    DISABLED_GRAY = 'rgb(54, 54, 54)'

    # List and Tree Widget Colors
    ITEM_BACKGROUND_COLOR = 'rgb(30, 30, 30)'
    ITEM_ALT_BACKGROUND_COLOR = 'rgb(36, 36, 36)'

    # Push Button Colors
    PUSHBUTTON_BLUE = 'rgb(44, 54, 68)'
    PUSHBUTTON_BLUE_CHECKED = 'rgb(50, 101, 173)'
    PUSHBUTTON_BLUE_DISABLED = 'rgb(50, 50, 50)'

    TAB_PANE = 'rgb(49, 49, 49)'

    SCROLLBAR_HANDLE = 'rgb(49, 49, 49)'

class TextColor(Enum):
    """
    TextColor
    =========

    Color options for text being printed to the terminal.

    Attributes:
    -----------
        GREEN (str):
            Green text.

        YELLOW (str):
            Yellow text.

        RED (str):
            Red text.

        WHITE (str):
            White text.

        BLUE (str):
            Blue text.

        RESET (str):
            Reset text color to default.
    """

    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BLUE = '\033[38;2;0;120;215m'
    RESET = '\033[0m'

    def format(self, text: str) -> str:
        """
        Formats the given text with the Enum's color.

        Args:
            text (str): The text to format.

        Returns:
            str: The formatted text with ANSI color codes.
        """
        return f"{self.value}{text}{TextColor.RESET.value}"

class Style(Enum):
    """
    Style
    =====

    Enum for PyFlameLabel style options.

    Attributes:
    -----------
        NORMAL (str):
            Standard label without any additional styling. Text is left aligned by default.

        UNDERLINE (str):
            Text is underlined. Text is centered by default.

        BORDER (str):
            Adds a white border around the label with a dark background. Text is centered by default.

        BACKGROUND (str):
            Adds a darker background to the label. Text is left aligned by default.

        BACKGROUND_THIN (str):
            Adds a darker background to the label. Text is left aligned by default.
    """

    NORMAL = 'normal'
    UNDERLINE = 'underline'
    BORDER = 'border'
    BACKGROUND = 'background'
    BACKGROUND_THIN = 'background_thin'

class Align(Enum):
    """
    Align
    =====

    Enum for text alignment.

    Attributes:
    -----------
        LEFT (str):
            Align text to the left.

        RIGHT (str):
            Align text to the right.

        CENTER (str):
            Align text to the center.
    """

    LEFT = 'left'
    RIGHT = 'right'
    CENTER = 'center'

class MessageType(Enum):
    """
    MessageType
    ===========

    Enum for PyFlameMessageWindows types.

    Attributes:
    -----------
        INFO (str):
            Information message type.

        OPERATION_COMPLETE (str):
            Operation complete message type.

        CONFIRM (str):
            Confirmation message type.

        ERROR (str):
            Error message type.

        WARNING (str):
            Warning message type.
    """

    INFO = 'Info'
    OPERATION_COMPLETE = 'Operation Complete'
    CONFIRM = 'Confirm'
    ERROR = 'Error'
    WARNING = 'Warning'

class PrintType(Enum):
    """
    MessageType
    ===========

    Enum for pyflame.print types.

    Attributes:
    -----------
        INFO (str):
            Information type.

        ERROR (str):
            Error type.

        WARNING (str):
            Warning type.
    """

    INFO = 'info'
    ERROR = 'error'
    WARNING = 'warning'

class BrowserType(Enum):
    """
    BrowserType
    ===========

    Enum for PyFlameLineEditFileBrowser browser type options.

    Attributes:
    -----------
        FILE (str):
            File browser.

        DIRECTORY (str):
            Directory browser.
    """

    FILE = 'file'
    DIRECTORY = 'directory'

class TextType(Enum):
    """
    Enumeration of supported text types for PyFlameTextEdit.
    """

    PLAIN = 'plain'
    MARKDOWN = 'markdown'
    HTML = 'html'

#-------------------------------------
# [PyFlame Functions]
#-------------------------------------

class _PyFlameFunctions():
    """
    PyFlameFunctions
    ================

    A class containing various useful functions.

    Methods that can be accessed using:
        ```
        pyflame.method_name
        ```

    Example
    -------
        To print a message using the `print` method:
        ```
        pyflame.print(
            text='Config not found.',
            type=PrintType.ERROR
            )
        ```
    """

    @staticmethod
    def print_title(text: str) -> None:
        """
        Print a stylized title banner with the script name and version centered to the terminal.

        Args:
        -----
            text (str):
                The full banner line, e.g., 'Cool Script v1.0.0'

        Example:
        --------
            ---=====[ Cool Script ]=====---
              ~~~~~~===[ v1.0.0 ]===~~~~~~
        """

        # Split input into script name and version
        parts = text.strip().rsplit(" ", 1)

        if len(parts) != 2 or not parts[1].lower().startswith("v"):
            raise ValueError("ValueError: pyflame.print_title: Text must end with a version (e.g., 'Script Name v1.2.3')")

        name, version = parts
        # First line with frame
        top_line = f'{TextColor.BLUE.value}---====={TextColor.WHITE.value}[ {name} ]{TextColor.BLUE.value}=====---'

        # Second line to be centered under top_line
        version_line = f'{TextColor.BLUE.value}~~~~~~==={TextColor.WHITE.value}[ {version} ]{TextColor.BLUE.value}===~~~~~~'

        # Calculate exact left padding to center second line under top line
        total_width = len(top_line)
        padding = max(0, (total_width - len(version_line)) // 2)
        centered_version_line = " " * padding + version_line

        # Output
        print(top_line)
        print(centered_version_line)
        print(f'{TextColor.RESET.value}\n', end='')

    @staticmethod
    def create_temp_folder(folder_name: str='temp') -> str:
        """
        Create Temp Folder
        ==================

        Create a temporary folder in the script folder.

        If folder already exists, it will be deleted and recreated.

        Temp folder is added to <SCRIPT_PATH>/<folder_name>.

        Args:
        -----
            `folder_name` (str):
                Name of the temporary folder to create.
                (Default: `temp`)

        Returns:
        --------
            str:
                Path to the temporary folder.

        Raises:
        -------
            TypeError:
                If `folder_name` is not a string.

        Example:
        --------
            To create a temporary folder:
            ```
            temp_folder_path = pyflame.create_temp_folder()
            ```
        """

        # Validate argument type
        if not isinstance(folder_name, str):
            pyflame.raise_type_error('pyflame.create_temp_folder', 'folder_name', 'string', folder_name)

        # Temp folder path
        temp_folder_path = os.path.join(SCRIPT_PATH, folder_name)

        # Create temp folder. If folder already exists, delete it and recreate.
        try:
            os.makedirs(temp_folder_path)
        except:
            shutil.rmtree(temp_folder_path)
            pyflame.print(f'Existing Temp Folder Deleted: {temp_folder_path}', text_color=TextColor.RED)
            os.makedirs(temp_folder_path)

        pyflame.print(f'Temp Folder Created: {temp_folder_path}', text_color=TextColor.GREEN)

        return temp_folder_path

    @staticmethod
    def cleanup_temp_folder(folder_name: str='temp') -> None:
        """
        Cleanup Temp Folder
        ===================

        Clear the contents of the temporary folder.

        Path to temp folder is: <SCRIPT_PATH>/<folder_name>.

        Args:
        -----
            `folder_name` (str):
                Name of the temporary folder to clear. Temp folder is added to <SCRIPT_PATH>/<folder_name>.
                (Default: `temp`)
        """

        # Validate argument type
        if not isinstance(folder_name, str):
            pyflame.raise_type_error('pyflame.cleanup_temp_folder', 'folder_name', 'string', folder_name)

        # Temp folder path
        temp_folder_path = os.path.join(SCRIPT_PATH, folder_name)

        # Remove and recreate temp folder if it exists, if not, print message
        try:
            shutil.rmtree(temp_folder_path)
            os.makedirs(temp_folder_path)
            pyflame.print(f'Temp Folder Cleaned Up: {temp_folder_path}', text_color=TextColor.GREEN)
        except:
            pyflame.print(f'Temp Folder Not Found, not cleared: {temp_folder_path}', text_color=TextColor.RED)

    @staticmethod
    def verify_script_install(additional_files: list=None) -> bool:
        """
        Verify Script Install
        =====================

        Verify that script is installed in the correct location.

        Scripts should always be installed in a folder with the same name as the script file.

        Checks to make sure the script folder is named the same as the main script file, that the
        script folder is writable, and that the script folder contains the required additional
        files if any are specified.

        Args:
        -----
            `additional_files` (list):
                List of additional files to check for in the script folder. These are other files
                that are required for the script to work. This should only be a list of file names,
                not full paths. If file is in a subfolder of the script folder, it should include
                the subfolder name. For example, if the script folder is named 'srt_to_xml' and the
                file 'xml_template.xml' is in the 'templates' subfolder, the file name should be
                'templates/xml_template.xml'.

        Returns:
        --------
            bool: True if script is installed in correct location and not missing any additional files, False if not.

        Raises:
        -------
            TypeError:
                If `additional_files` is not a list.

        Example:
        --------
            To check if script is installed in proper location along with additional files:
            ```
            verify_install = pyflame.verify_script_install(
                additional_files=[
                    'xml_template.xml',
                    'xml_title_template.xml',
                    'text_node_template.ttg',
                    ]
                )

            print(verify_install)
            ```
        """

        # Validate arguments
        if additional_files and not isinstance(additional_files, list):
            raise TypeError(f"pyflame.verify_script_install: Expected 'additional_files' to be a list, got {type(additional_files).__name__} instead.")

        pyflame.print('Verifying Script Install', new_line=False)
        print('------------------------\n')

        # Get script path info
        script_path = os.path.abspath(os.path.dirname(__file__))
        script_path = script_path.rsplit('/', 1)[0]
        root_path = os.path.dirname(script_path)
        script_folder_name = script_path.rsplit('/', 1)[1]
        script_file_name = os.path.basename(__file__)[12:-3]

        print('Script Path:', script_path)
        print('Root Path:', root_path)
        print('Script Folder Name:', script_folder_name)
        print('Script File Name:', script_file_name + '.py\n')

        # Check if script folder name matches script file name
        if not script_folder_name == script_file_name:
            PyFlameMessageWindow(
                message=(
                    f'Script install path is incorrect: \n\n'
                    f'    {script_path} \n\n'
                    f'The name of the script folder should match the name of the main script file. \n\n'
                    f'Script install path should be:\n\n'
                    f'    {os.path.join(root_path, script_file_name)}'
                    ),
                type=MessageType.ERROR
                )
            return False

        # Check script folder for write permissions
        if not os.access(script_path, os.W_OK):
            PyFlameMessageWindow(
                message=(
                    'Script folder is not writable. \n\n'
                    'Please check permissions and try again.'
                    ),
                type=MessageType.ERROR
                )
            return False

        # Check for additional files needed for script to work
        if additional_files:
            pyflame.print('Checking For Additional Files:')
            for file in additional_files:
                if not os.path.isfile(os.path.join(script_path, file)):
                    PyFlameMessageWindow(
                        message=(
                            f'File not found: \n\n'
                            f'    {file}\n\n'
                            f'Please check that the file is in the correct location and try again.'
                            ),
                        type=MessageType.ERROR
                        )
                    return False
                else:
                    pyflame.print(f'{file} -> Found', text_color=TextColor.GREEN, new_line=False)
            print('\n', end='')

        print('------------------------\n')

        pyflame.print('Script Install Verified', text_color=TextColor.GREEN)
        return True

    @staticmethod
    def create_media_panel_libraries(library_structure: dict[str, Any]) -> None:
        """
        Create Media Panel Library
        ==========================

        Create libraries/folders in the media panel based on the provided library/folder structure.

        Tokens can be used in library/folder names.

        Args:
        -----
            `library_structure` (dict):
                A dictionary representing the library/folder structure to be created.
                'Workspace' should always be the top level key.

        Raises:
        -------
            TypeError:
                If `library_structure` is not a dictionary.
            ValueError:
                If 'Workspace' is not the only top-level key in `library_structure`.

        Example:
        --------
            To create a library with folders in the media panel:
            ```
            library_structure = {
                'Workspace': {
                    'Library1': {
                        'Folder1': {
                            'SubFolder1': {},
                            'SubFolder2': {}
                            },
                        'Folder2': {}
                        },
                    'Library2': {
                        'Folder1': {
                            'SubFolder1': {},
                            'SubFolder2': {}
                            },
                        'Folder2': {}
                        }
                    }
                }

            pyflame.create_media_panel_libraries(library_structure)
            ```
        """

        # Validate argument type
        if not isinstance(library_structure, dict):
            raise TypeError(f"pyflame.create_media_panel_libraries: Expected 'library_structure' to be a dict, got {type(library_structure).__name__} instead.")
        # Validate that 'Workspace' is the only top-level key
        if set(library_structure.keys()) != {'Workspace'}:
            raise ValueError("pyflame.create_media_panel_libraries: 'library_structure' must have 'Workspace' as its only top-level key.")

        pyflame.print('Creating Media Panel Libraries and Folders...')
        pyflame.print('Library Structure:', underline=True, print_to_flame=False)
        pyflame.print_dict(library_structure)

        # Create new libraries and folders
        def create_folders(folder_structure, folder_dest):

            for key, value in folder_structure.items():
                key = pyflame.resolve_tokens(key) # Resolve tokens in folder name
                folder = folder_dest.create_folder(key)
                create_folders(value, folder)

        for key, value in library_structure.items():
            for library, folder_structure in value.items():
                new_library_name = pyflame.resolve_tokens(library) # Resolve tokens in library name
                new_library = flame.projects.current_project.current_workspace.create_library(new_library_name)
                create_folders(folder_structure, new_library)

        pyflame.print('Media Panel Libraries and Folders Created', arrow=True)

    @staticmethod
    def create_media_panel_folder(folder_name: str, folder_structure: dict[str, Any], dest: Union[flame.PyFolder, flame.PyLibrary], shot_name_tag: str=None) -> None:
        """
        Create Media Panel Folder
        =========================

        Create a folder in the media panel based on the provided folder structure. Tokens can be used in folder names.

        By default folders are tagged with the shot name token.

        Args:
        -----
            `folder_name` (str):
                Name of the main folder to create in the media panel.

            `folder_structure` (dict):
                A dictionary representing the folder structure to be created.

            `dest` (Folder):
                The destination folder/library in the Media Panel where the main folder will be created.

            `shot_name_tag` (str):
                Use to add ShotName tag to folder with matching name. If shot_name_tag is PYT_0010 any folder named PYT_0010 will be tagged with 'ShotName: PYT_0010'.
                (Default: `None`)

        Raises:
        -------
            TypeError:
                If `folder_name` is not a string.
                If `folder_structure` is not a dictionary.
                If `dest` is not a flame.PyFolder or flame.PyLibrary.
                If `shot_name_tag` is not a string.

        Example:
        --------
            To create media panel folders:
            ```
            folder_structure = {
                'Folder1': {
                    'SubFolder1': {},
                    'SubFolder2': {
                        'SubSubFolder1': {}
                    }
                },
                'Folder2': {}
            }

            pyflame.create_media_panel_folder(
                folder_name='Shot001',
                folder_structure=folder_structure,
                dest=flame.projects.current_project.current_workspace,
                shot_name_tag='Shot0010',
                )
            ```
        """

        # Validate arguments
        if not isinstance(folder_name, str):
            raise TypeError(f"pyflame.create_media_panel_folder: Expected 'folder_name' to be a str, got {type(folder_name).__name__} instead.")
        if not isinstance(folder_structure, dict):
            raise TypeError(f"pyflame.create_media_panel_folder: Expected 'folder_structure' to be a dict, got {type(folder_structure).__name__} instead.")
        if not isinstance(dest, (flame.PyFolder, flame.PyLibrary)):
            raise TypeError(f"pyflame.create_media_panel_folder: Expected 'dest' to be a flame.PyFolder or flame.PyLibrary, got {type(dest).__name__} instead.")
        if shot_name_tag != None and not isinstance(shot_name_tag, str):
            raise TypeError(f"pyflame.create_media_panel_folder: Expected 'shot_name_tag' to be None or a str, got {type(shot_name_tag).__name__} instead.")

        def create_sub_folders(folders, parent_folder):
            """
            Create Sub-Folders
            ==================

            Recursively create sub-folders based on the provided folder structure.

            Args:
            -----
                `folder_structure` (dict):
                    A dictionary representing the folder structure to be created.

                `parent_folder` (Folder):
                    The parent folder where the sub-folders will be created.
            """

            for key, value in folders.items():
                key = pyflame.resolve_tokens(key) # Resolve tokens in folder name
                new_folder = parent_folder.create_folder(key)
                if shot_name_tag and new_folder.name == shot_name_tag:
                    new_folder.tags=[f'ShotName: {shot_name_tag}']
                create_sub_folders(value, new_folder)

        pyflame.print('Creating Media Panel Folder...')
        pyflame.print('Folder Structure:', underline=True, print_to_flame=False)
        pyflame.print_dict(folder_structure)

        # Create the main shot folder
        folder_name = pyflame.resolve_tokens(folder_name) # Resolve tokens in folder name
        root_folder = dest.create_folder(folder_name)

        # Tag root folder with shot name if shot_name_tag is provided and folder_name matches shot_name_tag
        if shot_name_tag and folder_name == shot_name_tag:
            root_folder.tags=[f'ShotName: {shot_name_tag}']

        # Create sub-folders under the shot folder based on the settings
        for folders in folder_structure.values():
            create_sub_folders(folders, root_folder)

        pyflame.print(f'Media Panel Folder Created: {folder_name}', arrow=True)

    @staticmethod
    def create_media_panel_folders(folder_list: list[str], folder_structure: dict[str, Any], dest: Union[flame.PyFolder, flame.PyLibrary]) -> None:
        """
        Create Media Panel Folders
        ==========================

        Create folders in the Media Panel from a list of folder names. Tokens can be used in folder names.

        Args:
        -----
            `folder_list` (list[str]):
                List of folder names to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest` (Folder):
                The destination folder/library in the Media Panel where the folders will be created.

        Raises:
        -------
            TypeError:
                If `folder_list` is not a list.
                If `folder_structure` is not a dictionary.
                If `dest` is not a flame.PyFolder or flame.PyLibrary.

        Notes:
        ------
            Tokens can be used in folder names.

            Uses _PyFlameFunctions.create_media_panel_folder() to create each folder in list.

        Example:
        --------
            To create media panel folders:
            ```
            folder_list = [
                'PYT_0010',
                'PYT_0020',
                'PYT_0030',
                'PYT_0040',
                ]

            folder_structure = {
                'Folder1': {
                    'SubFolder1': {},
                    'SubFolder2': {}
                },
                'Folder2': {}
            }

            pyflame.create_media_panel_folders(
                folder_list=folder_list,
                folder_structure=folder_structure,
                dest=flame.projects.current_project.current_workspace,
                )
            ```
        """

        # Validate arguments
        if not isinstance(folder_list, list):
            raise TypeError(f"pyflame.create_media_panel_folders: Expected 'folder_list' to be a list, got {type(folder_list).__name__} instead.")
        if not isinstance(folder_structure, dict):
            raise TypeError(f"pyflame.create_media_panel_folders: Expected 'folder_structure' to be a dict, got {type(folder_structure).__name__} instead.")
        if not isinstance(dest, (flame.PyFolder, flame.PyLibrary)):
            raise TypeError(f"pyflame.create_media_panel_folders: Expected 'dest' to be a flame.PyFolder or flame.PyLibrary, got {type(dest).__name__} instead.")

        pyflame.print('Creating Media Panel Folders...')
        pyflame.print('Folder Structure:', underline=True, print_to_flame=False, text_color=TextColor.BLUE)
        pyflame.print_dict(folder_structure)

        for folder_name in folder_list:
            _PyFlameFunctions.create_media_panel_folder(folder_name, folder_structure, dest, folder_name)

    @staticmethod
    def create_file_system_folder(folder_name: str, folder_structure: dict[str, Any], dest_path: str, skip_existing: bool=False) -> None:
        """
        Create File System Folder
        =========================

        Create a folder in the file system based on the provided folder structure. Tokens can be used in folder names.

        Args:
        -----
            `folder_name` (str):
                Name of the main folder to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest_path` (str):
                Path where folders will be created.

            `skip_existing` (bool):
                Skip creating folders if they already exist.

        Raises:
        -------
            TypeError:
                If `folder_name` is not a string.
                If `folder_structure` is not a dictionary.
                If `dest_path` is not a string.
                If `skip_existing` is not a boolean.

        Example:
        --------
            To create a file system folder:
            ```
            folder_structure = {
                'Folder1': {
                    'SubFolder1': {},
                    'SubFolder2': {
                        'SubSubFolder1': {}
                    }
                },
                'Folder2': {}
            }

            pyflame.create_file_system_folder(
                folder_name='Shot001',
                folder_structure=folder_structure,
                dest_path='/path/to/dest/folder',
                skip_existing=False
                )
            ```

            The above example will create the following folder structure:
            ```
            /path/to/dest/folder/Shot001/Folder1/SubFolder1
            /path/to/dest/folder/Shot001/Folder1/SubFolder2/SubSubFolder1
            /path/to/dest/folder/Shot001/Folder2
            ```
        """

        def create_sub_folders(value: dict, parent_folder: str) -> None:
            """
            Create Sub-Folders
            ==================

            Recursively create sub-folders based on the provided folder structure.

            Args:
            -----
                `value` (dict):
                    Nested dictionary representing folder structure.

                `parent_folder` (str):
                    The parent folder where the sub-folders will be created.
            """

            for key, value in value.items():
                key = pyflame.resolve_tokens(key) # Resolve tokens in folder name
                folder = os.path.join(parent_folder, key)
                try:
                    os.makedirs(folder, exist_ok=True)
                except OSError as e:
                    print(f"Error creating directory {folder}: {e}")
                create_sub_folders(value, folder)

        #Validate arguments
        if not isinstance(folder_name, str):
            raise TypeError(f"pyflame.create_file_system_folder: Expected 'folder_name' to be a str, got {type(folder_name).__name__} instead.")
        if not isinstance(folder_structure, dict):
            raise TypeError(f"pyflame.create_file_system_folder: Expected 'folder_structure' to be a dict, got {type(folder_structure).__name__} instead.")
        if not isinstance(dest_path, str):
            raise TypeError(f"pyflame.create_file_system_folder: Expected 'dest_path' to be a str, got {type(dest_path).__name__} instead.")
        if not isinstance(skip_existing, bool):
            raise TypeError(f"pyflame.create_file_system_folder: Expected 'skip_existing' to be a bool, got {type(skip_existing).__name__} instead.")

        # Create folders
        for key, value in folder_structure.items():
            folder_name = pyflame.resolve_tokens(folder_name) # Resolve tokens in folder name
            parent_folder = os.path.join(dest_path, folder_name)
            if not os.path.isdir(parent_folder) or not skip_existing:
                try:
                    os.makedirs(parent_folder, exist_ok=True)
                    pyflame.print(
                        text=f'Creating File System Folders For: {folder_name}',
                        new_line=False,
                        text_color=TextColor.GREEN,
                        )
                except OSError as e:
                    print(f"Error creating directory {parent_folder}: {e}")
                create_sub_folders(value, parent_folder)
            else:
                pyflame.print(
                    text=f'File system folder: {folder_name} already exists, skipping.',
                    new_line=False,
                    )

        # Refresh Media Panel
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

    @staticmethod
    def create_file_system_folders(folder_list: list[str], folder_structure: dict[str, Any], dest_path: str) -> None:
        """
        Create File System Folders
        ==========================

        Create file system folders for a list of folders. Tokens can be used in folder names.

        Args:
        -----
            `folder_list` (list[str]):
                List of folder names to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest_path` (str):
                Path where folders will be created.

        Raises:
        -------
            TypeError:
                If `folder_list` is not a list.
                If `folder_structure` is not a dictionary.
                If `dest_path` is not a string.

        Notes:
        ------
            Tokens can be used in folder names.

            Uses _PyFlameFunctions.create_file_system_folder() to create each folder in list.

        Example:
        --------
            To create file system folders:
            ```
            folder_structure = {
                'Folder1': {
                    'SubFolder1': {},
                    'SubFolder2': {
                        'SubSubFolder1': {}
                    }
                },
                'Folder2': {}
            }

            folder_list = [
                'PYT_0010',
                'PYT_0020',
                'PYT_0030',
                'PYT_0040',
                ]

            pyflame.create_file_system_folders(
                folder_list=folder_list,
                folder_structure=folder_structure,
                dest_path='/path/to/dest/folder',
                )
            ```

            The above example will create the following folder structure:
            ```
            /dest/folder/path/PYT_0010/Folder1/SubFolder1
            /dest/folder/path/PYT_0010/Folder1/SubFolder2/SubSubFolder1
            /dest/folder/path/PYT_0010/Folder2
            /dest/folder/path/PYT_0020/Folder1/SubFolder1
            /dest/folder/path/PYT_0020/Folder1/SubFolder2/SubSubFolder1
            /dest/folder/path/PYT_0020/Folder2
            /dest/folder/path/PYT_0030/Folder1/SubFolder1
            /dest/folder/path/PYT_0030/Folder1/SubFolder2/SubSubFolder1
            /dest/folder/path/PYT_0030/Folder2
            /dest/folder/path/PYT_0040/Folder1/SubFolder1
            /dest/folder/path/PYT_0040/Folder1/SubFolder2/SubSubFolder1
            /dest/folder/path/PYT_0040/Folder2
            ```
        """

        # Validate arguments
        if not isinstance(folder_list, list):
            raise TypeError(f"pyflame.create_file_system_folders: Expected 'folder_list' to be a list, got {type(folder_list).__name__} instead.")
        if not isinstance(folder_structure, dict):
            raise TypeError(f"pyflame.create_file_system_folders: Expected 'folder_structure' to be a dict, got {type(folder_structure).__name__} instead.")
        if not isinstance(dest_path, str):
            raise TypeError(f"pyflame.create_file_system_folders: Expected 'dest_path' to be a str, got {type(dest_path).__name__} instead.")

        pyflame.print('Creating File System Folders', text_color=TextColor.GREEN)
        pyflame.print('Folder Structure:', underline=True, print_to_flame=False, text_color=TextColor.BLUE)
        pyflame.print_dict(folder_structure)

        for folder_name in folder_list:
            _PyFlameFunctions.create_file_system_folder(folder_name, folder_structure, dest_path)

    @staticmethod
    def copy_to_clipboard(value: Union[str, int]) -> None:
        """
        Copy to Clipboard
        =================

        Copy string(text) to clipboard using QT.

        Args:
        -----
            `value` (str | int):
                Text or integer to copy to clipboard.

        Raises:
        -------
            TypeError:
                If `value` is not a string or integer.

        Example:
        --------
            To copy text to clipboard:
            ```
            pyflame.copy_to_clipboard('Text to copy to clipboard.')
            ```
            To copy an integer to clipboard:
            ```
            pyflame.copy_to_clipboard(12345)
            ```
        """

        # Validate argument type
        if not isinstance(value, str | int):
            raise TypeError(f"pyflame.copy_to_clipboard: Expected 'value' to be a string or int, got {type(value).__name__} instead.")

        # Convert value to string if it is an integer
        if isinstance(value, int):
            value = str(value)

        # Copy path to clipboard
        qt_app_instance = QtWidgets.QApplication.instance()
        qt_app_instance.clipboard().setText(value)

        pyflame.print(f'Copied to Clipboard', text_color=TextColor.GREEN)

    @staticmethod
    def print(text: str, indent: int=0, print_type=PrintType.INFO, new_line: bool=True, arrow: bool=False, underline: bool=False, double_underline: bool=False, text_color: TextColor=None, time: int=3, print_to_flame: bool=True, script_name: str=SCRIPT_NAME) -> None:
        """
        Print
        =====

        Print text to the terminal and Flame message area.

        Args:
        -----
            `text` (str):
                Text to print.

            `indent` (int):
                Indent text in terminal by the specified amount of spaces.
                (Default: `0`)

            `print_type` (PrintType):
                See print types below.
                (Default: `PrintType.INFO`)

            `new_line` (bool):
                Print a new line after text.
                (Default: `True`)

            `arrow` (bool):
                Add an arrow `--> ` to the start of the text. Also sets text color to green.
                (Default: `False`)

            `underline` (bool):
                Add an underline to the text. A line of dashes will be printed below the text.
                (Default: `False`)

            `double_underline` (bool):
                Add a double underline to the text. Equals sign will be printed below the text.
                (Default: `False`)

            `text_color` (TextColor):
                Text color to print text in terminal. Overrides print_type color. See text colors below.
                (Default: `None`)

            `time` (int):
                Amount of time to display text in Flame for in seconds.
                (Default: `3`)

            `print_to_flame` (bool):
                Print message to Flame message area.
                (Default: `True`)

            `script_name` (str):
                Name of script. This is displayed in the Flame message area.
                (Default: `SCRIPT_NAME`)

        Print Types:
        --------------
        - `PrintType.INFO`: Prints text in default color.
        - `PrintType.ERROR`: Printed text will be yellow.
        - `PrintType.WARNING`: Printed text will be red.

        Text Color:
        ------------
        - `TextColor.GREEN`: Green text.
        - `TextColor.YELLOW`: Yellow text.
        - `TextColor.RED`: Red text.
        - `TextColor.WHITE`: White text.
        - `TextColor.BLUE`: Blue text.
        - `TextColor.RESET`: Reset text color to default.

        Raises:
        -------
        TypeError:
            If `text` is not a string.
            If `indent` is not an integer.
            If `new_line`, `arrow`, `underline`, or `double_underline` is not a boolean.
            If `time` is not an integer.
            If `script_name` is not a string.
            If `text_color` is not a TextColor.
        ValueError:
            If `type` is not a valid PrintType.

        Example:
        --------
            To print some text:
            ```
            pyflame.print('This is some text.')
            ```

            To print indented text:
            ```
            pyflame.print('This is some indented text.', indent=True)
            ```
        """

        # Validate argument types
        if not isinstance(text, str):
            raise TypeError(f"pyflame.print: Expected 'text' to be a string, got {type(text).__name__} instead.")
        if not isinstance(indent, int):
            raise TypeError(f"pyflame.print: Expected 'indent' to be a int, got {type(indent).__name__} instead.")
        if not isinstance(new_line, bool):
            raise TypeError(f"pyflame.print: Expected 'new_line' to be a boolean, got {type(new_line).__name__} instead.")
        if not isinstance(arrow, bool):
            raise TypeError(f"pyflame.print: Expected 'arrow' to be a boolean, got {type(arrow).__name__} instead.")
        if not isinstance(underline, bool):
            raise TypeError(f"pyflame.print: Expected 'underline' to be a boolean, got {type(underline).__name__} instead.")
        if not isinstance(double_underline, bool):
            raise TypeError(f"pyflame.print: Expected 'double_underline' to be a boolean, got {type(double_underline).__name__} instead.")
        if not isinstance(time, int):
            raise TypeError(f"pyflame.print: Expected 'time' to be an integer, got {type(time).__name__} instead.")
        if not isinstance(script_name, str):
            raise TypeError(f"pyflame.print: Expected 'script_name' to be a string, got {type(script_name).__name__} instead.")
        valid_message_types = (PrintType.INFO, PrintType.ERROR, PrintType.WARNING)
        if print_type not in valid_message_types:
            raise ValueError(f"pyflame.print:  Expected 'print_type' to be one of: PrintType.INFO, PrintType.ERROR, PrintType.WARNING. Got: {type(print_type).__name__} instead.")
        if text_color and not isinstance(text_color, TextColor):
            raise TypeError(f"pyflame.print: Expected 'text_color' to be a TextColor(TextColor.GREEN, TextColor.YELLOW, TextColor.RED, TextColor.WHITE, TextColor.BLUE, TextColor.RESET.), got {type(text_color).__name__} instead.")

        original_text = text
        text_length = len(text)

        # Add arrow to text if specified
        if arrow:
            text = f'--> {text}'
            text_color = TextColor.GREEN

        # Add indentation to text if specified
        if indent:
            text = f'{" " * indent}{text}'

        # Add text color to text if specified
        if text_color:
            text = text_color.format(text) # Print message with specified text_color and indentation
            color = text_color.value
        elif print_type == PrintType.INFO:
            text = text # Print message text normally
            color = ''
        elif print_type == PrintType.ERROR:
            text = f'{TextColor.YELLOW.value}{text}{TextColor.RESET.value}' # Print message text in yellow
            color = TextColor.YELLOW.value
        elif print_type == PrintType.WARNING:
            text = f'{TextColor.RED.value}{text}{TextColor.RESET.value}' # Print message text in red
            color = TextColor.RED.value

        print(text) # Print message text to terminal with specified color

        if underline:
            print(f'{color}{"-" * text_length}{TextColor.RESET.value}') # Print underline
        if double_underline:
            print(f'{color}{"=" * text_length}{TextColor.RESET.value}') # Print double underline
        if new_line:
            print('\n', end='')

        # Print to Flame Message Window - Flame 2023.1 and later
        # Warning and error intentionally swapped to match color of message window
        if print_to_flame:
            try:
                if print_type == PrintType.INFO:
                    flame.messages.show_in_console(f'{script_name}: {original_text}', 'info', time)
                elif print_type == PrintType.ERROR:
                    flame.messages.show_in_console(f'{script_name}: {original_text}', 'warning', time)
                elif print_type == PrintType.WARNING:
                    flame.messages.show_in_console(f'{script_name}: {original_text}', 'error', time)
            except:
                pass

    @staticmethod
    def print_dict(dict_data: dict[str, Any], indent: int=0) -> None:
        """
        Print Dict
        ==========

        Cleanly prints nested dictionaries with indentation to the terminal.

        Args:
        -----
            `dict_data` (dict):
                Dictionary to print.

            `indent` (int):
                Indentation level.
                (Default: `0`)

        Raises:
        -------
            TypeError:
                If `dict_data` is not a dictionary.
                If `indent` is not an integer.

        Example:
        --------
            To print a nested dictionary:
            ```
            dictionary = {
                'Key1': {
                    'SubKey1': 'Value1',
                    'SubKey2': 'Value2'
                    },
                'Key2': {
                    'SubKey1': 'Value1',
                    'SubKey2': 'Value2'
                    }
                }

            pyflame.print_dict(
                data_dict=dictionary,
                indent=0,
                )
            ```

            Output:
            ```
            Key1
                SubKey1: Value1
                SubKey2: Value2
            Key2
                SubKey1: Value1
                SubKey2: Value2
            ```
        """

        # Validate argument type
        if not isinstance(dict_data, dict):
            raise TypeError(f"pyflame.print_dict: Expected 'dict_data' to be a dict, got {type(dict_data).__name__} instead.")
        if not isinstance(indent, int):
            raise TypeError(f"pyflame.print_dict: Expected 'indent' to be an int, got {type(indent).__name__} instead.")

        def print_to_terminal(dict_data: dict[str, Any], indent: int) -> None:

            # Print dictionary data
            for key, value in dict_data.items():
                print('  ' * indent + str(key))
                if isinstance(value, dict) and value:
                    print_to_terminal(
                        dict_data=value,
                        indent=indent+1,
                        )

        print_to_terminal(dict_data, indent)

        print('\n', end='')

    @staticmethod
    def print_json(json_data, indent=0) -> None:
        """
        Print JSON
        ==========

        Cleanly print JSON data to terminal with proper indentation.

        Args:
        -----
            `json_data` (dict | list | str | int | bool):
                JSON data to print.

            `indent` (int):
                Indentation level.
                (Default: `0`)

        Raises:
        -------
            TypeError:
                If `indent` is not an integer.

        Example:
        --------
            ```
            pyflame.print_json(
                json_data=config.json,
                )
            ```
        """

        def print_to_terminal(json_data, indent):

            spacing = ' ' * indent

            # Check if the current data is a dictionary
            if isinstance(json_data, dict):
                # If "script_name" is present, print it first
                if "script_name" in json_data and indent == 0:
                    print(f"{spacing}script_name: {json_data['script_name']}")

                # Now print the rest of the dictionary except "script_name"
                for key, value in json_data.items():
                    if key == "script_name":
                        continue  # Skip "script_name" as it has already been printed

                    if isinstance(value, dict) and not value:
                        print(f"{spacing}{key}")  # Print the key without a colon if the value is an empty dict
                    else:
                        print(f"{spacing}{key}: ", end="")
                        if isinstance(value, (dict, list)):
                            print()  # Add a new line for nested structures
                            print_to_terminal(value, indent + original_indent)  # Recursive call
                        else:
                            print(value)  # Print the value immediately without an extra new line


            # If it's a list, iterate through the list items
            elif isinstance(json_data, list):
                for item in json_data:
                    print_to_terminal(item, indent + original_indent)  # Recursive call

            # Handle boolean values
            elif isinstance(json_data, bool):
                print(f"{'true' if json_data else 'false'}")

            # Handle any other data type (e.g., strings, numbers)
            else:
                print(f"{spacing}{json_data}")

        # Validate argument type
        if not isinstance(indent, int):
            raise TypeError(f"pyflame.print_json: Expected 'indent' to be an int, got {type(indent).__name__} instead.")

        original_indent = indent  # Store the original indent level

        print_to_terminal(json_data, indent)

        print()  # Ensure a single new line after all the data is printed

    @staticmethod
    def print_list(list_name: str, list_items: list, indent=0, time: int=3, script_name: str=SCRIPT_NAME) -> None:
        """
        Print List
        ===========

        Print a list of items to the terminal and Flame message area.

        Args:
        -----
            `list_name` (str):
                Name of the list.

            `list_items` (list):
                List of items to print.

            `indent` (int, optional):
                Indent message in terminal by specified amount of spaces.
                (Default: `0`)

            `time` (int, optional):
                Amount of time to display message in Flame for in seconds.
                (Default: `3`)

            `script_name` (str, optional):
                Name of script. This is displayed in the Flame message area.
                (Default: `SCRIPT_NAME`)

        Raises:
        -------
            TypeError:
                If `list_name` is not a string.
                If `list_items` is not a list.
                If any item in `list_items` is not a string.
                If `indent` is not an integer.
                If `time` is not an integer.
                If `script_name` is not a string.

            ValueError:
                If `list_items` is not a list of strings.

        Example:
        --------
            To print a list of items:
            ```
            pyflame.print_list(
                list_name='List of Items',
                list_items=[
                    'Item1',
                    'Item2',
                    'Item3'
                    ]
                )
            ```
        """

        # Validate argument types
        if not isinstance(list_name, str):
            raise TypeError(f"pyflame.print_list: Expected 'text' to be a string, got {type(list_name).__name__} instead.")
        if not isinstance(list_items, list):
            raise TypeError(f"pyflame.print_list: Expected 'list_items' to be a list, got {type(list_items).__name__} instead.")
        if not all(isinstance(item, str) for item in list_items):
            raise ValueError(f"pyflame.print_list: Expected all items in 'list_items' to be strings.")
        if not isinstance(indent, int):
            raise TypeError(f"pyflame.print_list: Expected 'indent' to be a integer, got {type(indent).__name__} instead.")
        if not isinstance(time, int):
            raise TypeError(f"pyflame.print_list: Expected 'time' to be an integer, got {type(time).__name__} instead.")
        if not isinstance(script_name, str):
            raise TypeError(f"pyflame.print_list: Expected 'script_name' to be a string, got {type(script_name).__name__} instead.")

        # Print list name to terminal
        print(f'{list_name}:')
        print('-' * (len(list_name)+1))
        print('\n', end='')

        # Print list name to Flame message area
        flame.messages.show_in_console(f'{script_name}: {list_name}:', 'info', 3)

        # Print list to terminal, indenting each item by 4 spaces if indent is True
        for item in list_items:
            print(f'{" " * indent}{item}')
        print('\n', end='')
        print('-' * (len(list_name)+1)) # Print a line of dashes after the list
        print('\n', end='')

        # Print list items to Flame message area. List items are not indented in the Flame message area.
        for item in list_items:
            flame.messages.show_in_console(f'{script_name}: {item}', 'info', 3)

    @staticmethod
    def message_print(message: str, type=MessageType.INFO, script_name: str=SCRIPT_NAME, time: int=3, ) -> None:
        """
        Message Print
        =============

        **Deprecated** Use `pyflame.print` instead.

        Prints messages to terminal and Flame message area(2023.1+).

        Args:
        -----
            message (str):
                Message to print.

            type (MessageType):
                Type of message. See message types below.
                (Default: `MessageType.INFO`)

            script_name (str):
                Name of script. This is displayed in the Flame message area.
                (Default: `SCRIPT_NAME`)

            time (int):
                Amount of time to display message for in seconds.
                (Default: `3`)

        Message Types:
        --------------
        - `MessageType.INFO`: Standard message.
        - `MessageType.ERROR`: Error message. Text in terminal will be yellow.
        - `MessageType.WARNING`: Warning message. Text in terminal will be red.

        Example:
        --------
            To print an error message:
            ```
            pyflame.message_print(
                message='Config not found.',
                type=MessageType.ERROR,
                )
            ```
        """

        script_name = script_name.upper()

        # Validate arguments
        if not isinstance(message, str):
            raise TypeError(f'PyFlame message_print: Invalid message type: {message}. message must be of type str.')
        if not isinstance(script_name, str):
            raise TypeError(f'Pyflame message_print: Invalid script_name type: {script_name}. script_name must be of type str.')
        valid_message_types = {MessageType.INFO, MessageType.ERROR, MessageType.WARNING}
        if type not in valid_message_types:
            raise ValueError(f'PyFlame message_print: Invalid message type: {type}. Accepted types: MessageType.INFO, MessageType.ERROR, MessageType.WARNING.')
        if not isinstance(time, int):
            raise TypeError(f'Pyflame message_print: Invalid time type. time must be of type int.')

        print(f'\033[91m--> DeprecationWarning: pyflame.message_print: Use pyflame.print instead.\033[0m\n') # Print message text in red

        # Print to terminal/shell
        if type == MessageType.INFO:
            print(f'--> {message}\n') # Print message text normally
        elif type == MessageType.ERROR:
            print(f'\033[93m--> {message}\033[0m\n') # Print message text in yellow
        elif type == MessageType.WARNING:
            print(f'\033[91m--> {message}\033[0m\n') # Print message text in red

        script_name = script_name.upper()

        # Print to Flame Message Window - Flame 2023.1 and later
        # Warning and error intentionally swapped to match color of message window
        try:
            if type == MessageType.INFO:
                flame.messages.show_in_console(f'{script_name}: {message}', 'info', time)
            elif type == MessageType.ERROR:
                flame.messages.show_in_console(f'{script_name}: {message}', 'warning', time)
            elif type == MessageType.WARNING:
                flame.messages.show_in_console(f'{script_name}: {message}', 'error', time)
        except:
            pass

    @staticmethod
    def generate_unique_node_names(node_names: list[str], existing_node_names: list[str]) -> list[str]:
        """
        Generate Unique Node Names
        ==========================

        Generate unique node names based on the provided list of node names, ensuring that each new node
        name does not conflict with names in a given list of existing node names. If a conflict is found,
        the function appends an incrementing number to the original name until a unique name is created.

        Args:
        -----
            `node_names` (list[str]):
                List of node names that need to be checked and possibly modified to ensure uniqueness.

            `existing_node_names` (list[str]):
                List of already existing node names against which the new node names will be checked for uniqueness.

        Returns:
        --------
            list[str]:
                A list of new unique node names. Each name in this list is guaranteed to be unique against the provided list of existing node names.

        Raises:
        -------
            TypeError:
                If `node_names` is not a list.
                If `existing_node_names` is not a list.
            ValueError:
                If any element in `node_names` is not a string.
                If any element in `existing_node_names` is not a string.

        Example:
        --------
            To generate unique node names for a list of nodes:
            ```
            generate_unique_node_names(
                node_names=[
                    'Node1',
                    'Node2',
                    'Node3'
                    ],
                existing_node_names=[
                    'Node7',
                    'Node2',
                    'Node4',
                    ]
                )
            ```
        """

        # Validate arguments types
        if not isinstance(node_names, list):
            raise TypeError(f"pyflame.generate_unique_node_names: Expected 'node_names' to be a list, got {type(node_names).__name__} instead.")
        if not all(isinstance(name, str) for name in node_names):
            raise ValueError(f'pyflame.generate_unique_node_names: All elements in node_names list must be strings.')
        if not isinstance(existing_node_names, list):
            raise TypeError(f"pyflame.generate_unique_node_names: Expected 'existing_node_names' to be a list, got {type(existing_node_names).__name__} instead.")
        if not all(isinstance(name, str) for name in existing_node_names):
            raise ValueError(f'pyflame.generate_unique_node_names: All elements in existing_node_names list must be strings.')

        # Check node names for uniqueness
        new_node_names = []
        for name in node_names:
            # If name starts with a number, add a '_' to the name
            if name[0].isdigit():
                name = f'_{name}'
            original_name = name
            i = 1
            # Keep appending a number to the name until it's unique
            while name in existing_node_names:
                name = f"{original_name}{i}"
                i += 1

            # Add the unique name to the list
            new_node_names.append(name)
            existing_node_names.append(name)

        return new_node_names

    @staticmethod
    def get_flame_version() -> float:
        """
        Get Flame Version
        =================

        Gets version of flame and returns float value.

        Returns:
        --------
            `flame_version` (float): 2022.0
                2022 -> 2022.0
                2022.1.1 -> 2022.1
                2022.1.pr145 -> 2022.1

        Example:
        --------
            To get the version of Flame:
            ```
            flame_version = pyflame.get_flame_version()
            ```
        """

        flame_version = flame.get_version()

        if 'pr' in flame_version:
            flame_version = flame_version.rsplit('.pr', 1)[0]
        if len(flame_version) > 6:
            flame_version = flame_version[:6]
        flame_version = float(flame_version)

        print('Flame Version:', flame_version, '\n')

        return flame_version

    @staticmethod
    def get_flame_python_packages_path(print_path: bool=True) -> str:
        """
        Get Flame Python Packages Path
        ===============================

        Get path to Flame's python packages folder.

        Args:
        -----
            `print_path` (bool):
                Print path to terminal.
                (Default: `True`)

        Returns:
        --------
            `python_packages_path` (str):
                Path to Flame's python packages folder.

        Raises:
        -------
            FileNotFoundError:
                If no python3.* folder is found in the python lib path.

        Example:
        --------
            To get the path to Flame's python packages folder:
            ```
            python_packages_path = pyflame.pyflame_get_flame_python_packages_path()
            ```
        """

        # Validate argument types
        if not isinstance(print_path, bool):
            raise TypeError(f"pyflame.get_flame_python_packages_path: Expected 'print_path' to be a bool, got {type(print_path).__name__} instead.")

        flame_version = flame.get_version() # Get flame version

        python_lib_path = f'/opt/Autodesk/python/{flame_version}/lib' # Path to Flame's python lib folder

        # Find the folder in the python lib path that starts with 'python3.'
        for folder in os.listdir(python_lib_path):
            if folder.startswith('python3.'):
                python_package_folder = os.path.join(python_lib_path, folder, 'site-packages')
                if print_path:
                    print('Flame Python Packages Folder:', python_package_folder, '\n')
                return python_package_folder

        raise FileNotFoundError('No python3.* folder found in the python lib path.')

    @staticmethod
    def file_browser(path: str='/opt/Autodesk', title: Optional[str]=None, extension: Optional[List[str]]=None, select_directory: bool=False, multi_selection: bool=False, include_resolution: bool=False, use_flame_browser: bool=True, window_to_hide: Optional[List[QtWidgets.QWidget]]=None) -> Optional[Union[str, list]]:
        """
        File Browser
        ============

        Opens Flame's file browser(Flame 2023.1+) or QT file browser window(Flame 2022 - Flame 2023).

        Args:
        -----
            `path` (str):
                Open file browser to this path.
                (Default: `'/opt/Autodesk'`)

            `title` (str):
                File browser window title.
                (Default: `None`)

            `extension` (list):
                File extension filter. None to list directories.
                (Default: `None`)

            `select_directory` (bool):
                Ability to select directories.
                (Default: `False`)

            `multi_selection` (bool):
                Ability to select multiple files/folders.
                (Default: `False`)

            `include_resolution` (bool):
                Enable resolution controls in flame browser.
                (Default: `False`)

            `use_flame_browser` (bool):
                Use Flame's file browser if using Flame 2023.1 or later.
                (Default: `True`)

            `window_to_hide` (list[QtWidgets.QWidget]):
                Hide Qt window while Flame file browser window is open. Window is restored when browser is closed.
                (Default: `None`)

        Returns:
        --------
            `path` (str, list):
                Path to selected file or directory. When `multi_selection` is enabled, the file browser will return a list. Otherwise it will return a string.

        Example:
        --------
            To open a file browser:
            ```
            path = pyflame_file_browser(
                path=self.undistort_map_path,
                title='Load Undistort ST Map(EXR)',
                extension=['exr'],
                )
            ```
        """

        # Check argument values
        if not isinstance(path, str):
            raise TypeError(f'Pyflame file_browser: Invalid path type: {path}. path must be of type str.')
        if title is not None and not isinstance(title, str):
            raise TypeError(f'Pyflame file_browser: Invalid title type: {title}. title must be of type str or None.')
        if extension is not None and not isinstance(extension, list):
            raise TypeError(f'Pyflame file_browser: Invalid extension type: {extension}. extension must be of type list or None.')
        if not isinstance(select_directory, bool):
            raise TypeError(f'Pyflame file_browser: Invalid select_directory type: {select_directory}. select_directory must be of type bool.')
        if not isinstance(multi_selection, bool):
            raise TypeError(f'Pyflame file_browser: Invalid multi_selection type: {multi_selection}. multi_selection must be of type bool.')
        if not isinstance(include_resolution, bool):
            raise TypeError(f'Pyflame file_browser: Invalid include_resolution type: {include_resolution}. include_resolution must be of type bool.')
        if not isinstance(use_flame_browser, bool):
            raise TypeError(f'Pyflame file_browser: Invalid use_flame_browser type: {use_flame_browser}. use_flame_browser must be of type bool.')
        if window_to_hide is not None and not isinstance(window_to_hide, list):
            raise TypeError(f'Pyflame file_browser: Invalid window_to_hide type: {window_to_hide}. window_to_hide must be of type list or None.')

        if not title and not extension:
            title = 'Select Directory'
        elif not title and extension:
            title = 'Select File'

        # Clean up path
        while os.path.isdir(path) is not True:
            path = path.rsplit('/', 1)[0]
            if '/' not in path and not os.path.isdir(path):
                path = '/opt/Autodesk'
            print('Browser path:', path, '\n')

        # Open file browser
        if pyflame.get_flame_version() >= 2023.1 and use_flame_browser:

            # Hide Qt window while browser is open
            if window_to_hide:
                for window in window_to_hide:
                    window.hide()

            # Open Flame file browser
            flame.browser.show(
                title=title,
                extension=extension,
                default_path=path,
                select_directory=select_directory,
                multi_selection=multi_selection,
                include_resolution=include_resolution
                )

            # Restore Qt windows
            if window_to_hide:
                for window in window_to_hide:
                    window.show()

            # Return file path(s) from Flame file browser
            if flame.browser.selection:
                if multi_selection:
                    return flame.browser.selection
                return flame.browser.selection[0]
        else:
            browser = QtWidgets.QFileDialog()
            browser.setDirectory(path)

            if select_directory or not extension:
                browser.setFileMode(QtWidgets.QFileDialog.Directory)
            else:
                browser.setFileMode(QtWidgets.QFileDialog.ExistingFile)
                filter_str = ';;'.join(f'*.{ext}' for ext in extension)
                browser.setNameFilter(filter_str)

                browser.selectNameFilter(filter_str)

            if browser.exec_():
                return str(browser.selectedFiles()[0])

            print('\n--> Import cancelled \n')
            return

    @staticmethod
    def open_in_finder(path: str) -> None:
        """
        Open in Finder
        ==============

        Open path in System Finder.

        Args:
        -----
            `path` (str):
                Path to open in Finder.
        """

        # Validate argument types
        if not isinstance(path, str):
            raise TypeError(f"pyflame.open_in_finder: Expected 'open_in_finder' to be a string, got {type(open_in_finder).__name__} instead.")

        if not os.path.exists(path):
            pyflame.print(
                text=f'Path does not exist: {path}',
                type=MessageType.ERROR,
            )
            return

        # Open path in Finder or File Explorer
        if platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

        pyflame.print(f'Opening path in Finder: {path}')

    @staticmethod
    def raise_type_error(source_name: str=None, arg_name: str=None, expected_type: str=None, actual_value: Any=None, error_message: str=None, time: int=10) -> None:
        """
        Raise Type Error
        =================

        Print error message to Flame and Terminal/Shell then raise TypeError.

        Args:
        -----
            `source_name` (str):
                Name of the class or function that raised the error.

            `arg_name` (str):
                Name of the argument that caused the error.

            `expected_type` (str):
                Expected type of the argument.

            `actual_value` (Any):
                Actual value of the argument.

            `error_message` (str):
                Error message to print.

            `time` (int):
                Time to display the error message.
        """

        if not error_message:
            error_message = f"{source_name}: Expected '{arg_name}' to be {expected_type}, got {type(actual_value).__name__} instead."

        # Capture the current traceback
        tb_info = traceback.format_exc()

        # If no traceback is captured (no prior exception), capture the current stack
        if tb_info.strip() == "NoneType: None":
            tb_info = ''.join(traceback.format_stack())

        # Combine the error message with the traceback information
        print(f'\n\nTraceback: (Most Recent Call Last):\n\n{tb_info}')

        pyflame.print(error_message, print_type=PrintType.WARNING, time=time)
        raise TypeError(error_message)

    @staticmethod
    def raise_value_error(source_name: str=None, arg_name: str=None, expected_value: Any=None, actual_value: Any=None, error_message: str=None, time: int=10) -> None:
        """
        Raise Value Error
        =================

        Print error message to Flame and Terminal/Shell then raise ValueError.

        Args:
        -----
            `source_name` (str):
                Name of the class or function that raised the error.

            `arg_name` (str):
                Name of the argument that caused the error.

            `expected_value` (Any):
                Expected value of the argument.

            `actual_value` (Any):
                Actual value of the argument.

            `error_message` (str):
                Error message to print.

            `time` (int):
                Time to display the error message.
                (Default: `10`)
        """

        if not error_message:
            error_message = f"{source_name}: Expected '{arg_name}' to be {expected_value}, got {actual_value} instead."

        # Capture the current traceback
        tb_info = traceback.format_exc()

        # If no traceback is captured (no prior exception), capture the current stack
        if tb_info.strip() == "NoneType: None":
            tb_info = ''.join(traceback.format_stack())

        # Combine the error message with the traceback information
        print(f'\n\nTraceback: (Most Recent Call Last):\n\n{tb_info}')

        pyflame.print(error_message, print_type=PrintType.WARNING, time=time)
        raise ValueError(error_message)

    @staticmethod
    def refresh_hooks(script_name: str=SCRIPT_NAME) -> None:
        """
        Refresh Hooks
        =============

        Refresh python hooks and print message to terminal and Flame message window.

        Args:
        -----
            `script_name` (str):
                Name of script. This is displayed in the Flame message area.
                (Default: `SCRIPT_NAME`)

        Raises:
        -------
            TypeError:
                If `script_name` is not a string.

        Example:
        --------
            To refresh python hooks:
            ```
            pyflame.refresh_hooks()
            ```
        """

        # Validate argument type
        if not isinstance(script_name, str):
            raise TypeError(f"pyflame.refresh_hooks: Expected 'script_name' to be a string, got {type(script_name).__name__} instead.")

        flame.execute_shortcut('Rescan Python Hooks') # Refresh python hooks

        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80
            )
        pyflame.print('Python Hooks Refreshed', new_line=False, text_color=TextColor.WHITE)
        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

    @staticmethod
    def resolve_path_tokens(tokenized_path: str, flame_pyobject=None, date=None) -> str:
        """
        Resolve Path Tokens
        ===================

        Resolves paths with tokens.

        **Deprecated** Use `pyflame.resolve_tokens` instead.
        """

        print('\033[91m--> DeprecationWarning - pyflame.resolve_path_tokens - use pyflame.resolve_tokens instead.\033[0m\n')

        return pyflame.resolve_tokens(tokenized_path, flame_pyobject, date) # Resolve path tokens

    @staticmethod
    def resolve_tokens(tokenized_string: str, flame_pyobject=None, date=None) -> str:
        """
        Resolve Path Tokens
        ===================

        Resolves strings containing tokens.

        Args:
        -----
            `tokenized_string` (str):
                String with tokens to be translated.

            `flame_pyobject` (flame.PyClip, optional):
                Flame PyClip/PySegment/PyBatch Object.
                (Default: `None`)

            `date` (datetime, optional):
                Date/time to use for token translation. If None is passed datetime value will be gotten each time function is run.
                (Default: `None`)

        Supported tokens:
        -----------------
            <ProjectName>, <ProjectNickName>, <UserName>, <UserNickName>, <YYYY>, <YY>, <MM>, <DD>, <Hour>, <Minute>, <AMPM>, <ampm>

            Additional tokens available when Flame PyObjects as passed in the flame_pyobject argument:
                PyClip and PySegment:
                    <ShotName>, <SeqName>, <SEQNAME>, <ClipName>, <Resolution>, <ClipHeight>, <ClipWidth>, <TapeName>
                PyBatch:
                    <BatchGroupName>, <ShotName>, <SeqName>, <SEQNAME>

        Returns:
        --------
            `resolved_string` (str):
                String with resolved tokens.

        Raises:
        -------
            TypeError:
                If `tokenized_string` is not a string.

        Example:
        --------
            To resolve path tokens:
            ```
            export_path = pyflame.translate_path_tokens(
                tokenized_string=custom_export_path,
                flame_pyobject=clip,
                date=date
                )
            ```
        """

        # Validate argument types
        if not isinstance(tokenized_string, str):
            raise TypeError(f"pyflame.resolve_tokens: Expected 'tokenized_string' to be a string, got {type(tokenized_string).__name__} instead.")

        def get_seq_name(name):
            """
            Get sequence name abreviation from shot name
            """

            seq_name = re.split('[^a-zA-Z]', name)[0]
            return seq_name

        pyflame.print('Resolving Tokens', new_line=False)
        print('----------------')


        print('Checking for tokens in string666:', tokenized_string)

        # Check if string has tokens
        if not re.search(r'<.*?>', tokenized_string):
            pyflame.print(f'No tokens found in string: {tokenized_string}')
            return tokenized_string
        else:
            pyflame.print(f'Tokens found in string, resolving...')
        # Get time values for token conversion
        if not date:
            date = datetime.datetime.now()

        yyyy = date.strftime('%Y')
        yy = date.strftime('%y')
        mm = date.strftime('%m')
        dd = date.strftime('%d')
        hour = date.strftime('%I')
        if hour.startswith('0'):
            hour = hour[1:]
        minute = date.strftime('%M')
        ampm_caps = date.strftime('%p')
        ampm = str(date.strftime('%p')).lower()

        # Replace tokens in path
        resolved_path = re.sub('<ProjectName>', flame.projects.current_project.name, tokenized_string)
        resolved_path = re.sub('<ProjectNickName>', flame.projects.current_project.nickname, resolved_path)
        resolved_path = re.sub('<UserName>', flame.users.current_user.name, resolved_path)
        resolved_path = re.sub('<UserNickName>', flame.users.current_user.nickname, resolved_path)
        resolved_path = re.sub('<YYYY>', yyyy, resolved_path)
        resolved_path = re.sub('<YY>', yy, resolved_path)
        resolved_path = re.sub('<MM>', mm, resolved_path)
        resolved_path = re.sub('<DD>', dd, resolved_path)
        resolved_path = re.sub('<Hour>', hour, resolved_path)
        resolved_path = re.sub('<Minute>', minute, resolved_path)
        resolved_path = re.sub('<AMPM>', ampm_caps, resolved_path)
        resolved_path = re.sub('<ampm>', ampm, resolved_path)

        # Get Batch Group Name - Only works when a PyBatch object is passed as the flame_pyobject argument.
        if '<BatchGroupName>' in tokenized_string and isinstance(flame_pyobject, flame.PyBatch):
            resolved_path = re.sub('<BatchGroupName>', str(flame_pyobject.name)[1:-1], resolved_path)

        # Resolve tokens for flame pyobjects
        if flame_pyobject:
            if isinstance(flame_pyobject, flame.PyClip):

                def resolve_clip_tokens(clip, resolved_path: str) -> str:
                    """
                    Resolve Clip Tokens
                    ===================
                    """

                    clip_name = str(clip.name)[1:-1] # Get clip name

                    # Get shot name from clip
                    try:
                        if clip.versions[0].tracks[0].segments[0].shot_name != '':
                            shot_name = str(clip.versions[0].tracks[0].segments[0].shot_name)[1:-1]
                        else:
                            shot_name = pyflame.resolve_shot_name(clip_name)
                    except:
                        shot_name = ''

                    # Get tape name from clip
                    try:
                        tape_name = str(clip.versions[0].tracks[0].segments[0].tape_name) # Get tape name
                    except:
                        tape_name = ''

                    seq_name = get_seq_name(shot_name) # Get Seq Name from shot name

                    # Replace clip tokens in path
                    resolved_path = re.sub('<ShotName>', shot_name, resolved_path)
                    resolved_path = re.sub('<SeqName>', seq_name, resolved_path)
                    resolved_path = re.sub('<SEQNAME>', seq_name.upper(), resolved_path)
                    resolved_path = re.sub('<ClipName>', str(clip.name)[1:-1], resolved_path)
                    resolved_path = re.sub('<Resolution>', str(clip.width) + 'x' + str(clip.height), resolved_path)
                    resolved_path = re.sub('<ClipHeight>', str(clip.height), resolved_path)
                    resolved_path = re.sub('<ClipWidth>', str(clip.width), resolved_path)
                    resolved_path = re.sub('<TapeName>', tape_name, resolved_path)

                    return resolved_path

                resolved_path = resolve_clip_tokens(flame_pyobject, resolved_path)

            elif isinstance(flame_pyobject, flame.PySegment):

                def resolve_segment_tokens(segment, resolved_path: str) -> str:
                    """
                    Resolve Segment Tokens
                    ======================

                    Args:
                    -----
                        `segment` (flame.PySegment):
                            Flame PySegment object.

                        `resolved_path` (str):
                            Resolved path with tokens.

                    Returns:
                    --------
                        `resolved_path` (str):
                            Resolved path with tokens.
                    """

                    segment_name = str(segment.name)[1:-1]

                    # Get shot name from clip
                    try:
                        if segment.shot_name != '':
                            shot_name = str(segment.shot_name)[1:-1]
                        else:
                            shot_name = pyflame.resolve_shot_name(segment_name)
                    except:
                        shot_name = ''

                    # Get tape name from segment
                    try:
                        tape_name = str(segment.tape_name)
                    except:
                        tape_name = ''

                    seq_name = get_seq_name(shot_name) # Get Seq Name from shot name

                    # Replace segment tokens in path
                    resolved_path = re.sub('<ShotName>', shot_name, resolved_path)
                    resolved_path = re.sub('<SeqName>', seq_name, resolved_path)
                    resolved_path = re.sub('<SEQNAME>', seq_name.upper(), resolved_path)
                    resolved_path = re.sub('<ClipName>', segment_name, resolved_path)
                    resolved_path = re.sub('<Resolution>', 'Unable to Resolve', resolved_path)
                    resolved_path = re.sub('<ClipHeight>', 'Unable to Resolve', resolved_path)
                    resolved_path = re.sub('<ClipWidth>', 'Unable to Resolve', resolved_path)
                    resolved_path = re.sub('<TapeName>', tape_name, resolved_path)

                    return resolved_path

                resolved_path = resolve_segment_tokens(flame_pyobject, resolved_path)

            elif isinstance(flame_pyobject, flame.PyBatch):

                def resolve_batch_tokens(batch, resolved_path: str) -> str:
                    """
                    Resolve Batch Tokens
                    ====================

                    Batch is checked for a ShotName tag(ShotName:<shot_name>). If found, it is used to resolve the shot name token.
                    Otherwise, any Render nodes in the batch are checked for a shot name. If a shot name is found, it is used to resolve the shot name token.
                    If no shot name is found, the batch name is used to resolve the shot name token.

                    Args:
                    -----
                        `batch` (flame.PyBatch):
                            Flame PyBatch object.

                        `resolved_path` (str):
                            Resolved path with tokens.

                    Returns:
                    --------
                        `resolved_path` (str):
                            Resolved path with tokens.
                    """

                    def get_shot_name_tag(batch) -> str:
                        """
                        Get Shot Name Tag
                        """

                        # Check for ShotName tag
                        if batch.tags.get_value() != []:
                            print('Batch Tags:', batch.tags.get_value())
                            for tag in batch.tags.get_value():
                                if tag.startswith('ShotName:'):
                                    shot_name = tag.split(': ')[1]
                                    print(f'Batch Shot Name Tag Found: {shot_name}')
                                    return shot_name
                        else:
                            print('No Batch Shot Name Tags Found')
                            return None

                    def get_shot_name_from_render_nodes(batch) -> str:
                        """
                        Get Shot Name from Render Nodes
                        """

                        render_node_types = ['Render', 'Write File']
                        render_nodes = [node for node in batch.nodes if node.type in render_node_types]

                        if render_nodes:
                            shot_name = str(render_nodes[0].shot_name)[1:-1]
                            if shot_name:
                                print(f'Render Node Shot Name Found: {shot_name}')
                                return shot_name
                            else:
                                print('Render Node Shot Name Not Found')
                                return None
                        else:
                            print('No Render Nodes Found')
                            return None

                    shot_name = None
                    print('Checking for Shot Name Tag...')
                    if batch.tags:
                        shot_name = get_shot_name_tag(batch)
                        print(f'Shot Name from Batch Tag: {shot_name}')
                    else:
                        print('No Batch Shot Name Tags Found')

                    if not shot_name:
                        shot_name = get_shot_name_from_render_nodes(batch)
                        print(f'Shot Name from Render Nodes: {shot_name}')

                    if not shot_name:
                        shot_name = pyflame.resolve_shot_name(str(batch.name)[1:-1])
                        print(f'Shot Name from Batch Name: {shot_name}')

                    print('\n', end='')

                    seq_name = get_seq_name(shot_name) # Get Seq Name from shot name

                    # Replace tokens in path
                    resolved_path = re.sub('<ShotName>', shot_name, resolved_path)
                    resolved_path = re.sub('<SeqName>', seq_name, resolved_path)
                    resolved_path = re.sub('<SEQNAME>', seq_name.upper(), resolved_path)

                    print(f'Resolved Path: {resolved_path}')

                    return resolved_path
                print(6)
                resolved_path = resolve_batch_tokens(flame_pyobject, resolved_path)

        pyflame.print(f'Resolved Tokenized String: {resolved_path}', text_color=TextColor.GREEN, new_line=False)
        print('----------------\n')

        return resolved_path

    @staticmethod
    def resolve_shot_name(name: str) -> str:
        """
        Resolve Shot Name
        =================

        Resolves a shot name from a provided string. This function is intended to handle
        two formats: a camera source name like 'A010C0012' or a standard name where the
        shot name precedes other identifiers (e.g. 'pyt_0010_comp').

        Args:
        -----
            `name` (str):
                The name to be resolved into a shot name.

        Returns:
        --------
            str: The resolved shot name.

        Raises:
        -------
            TypeError:
                If `name` is not a string.

        Examples:
        ---------
            Using a camera source name:
            ```
            shot_name = pyflame.resolve_shot_name('A010C0012')
            print(shot_name)  # Outputs: A010C001
            ```

            Using a standard name:
            ```
            shot_name = pyflame.resolve_shot_name('pyt_0010_comp')
            print(shot_name)  # Outputs: pyt_0010
            ```
        """

        # Validate argument types
        if not isinstance(name, str):
            raise TypeError(f"pyflame.resolve_shot_name: Expected 'name' to be a string, got {type(name).__name__} instead.")

        # Check if the name follows the format of a camera source (e.g. A010C0012).
        # If so, take the first 8 characters as the shot name.
        # The regex ^A\d{3}C\d{3} matches strings that start with 'A', followed by
        # three digits, followed by 'C', followed by three more digits.
        if re.match(r'^A\d{3}C\d{3}', name):
            shot_name = name[:8]
        else:
            # If the name is not a camera source, we assume it's in a different format
            # that requires splitting to find the shot name.
            # We split the name using digit sequences as delimiters.
            shot_name_split = re.split(r'(\d+)', name)

            # After splitting, we need to reassemble the shot name.
            # If there is at least one split, we check if the second element in the
            # split is alphanumeric. If it is, we concatenate the first two elements.
            # If it's not alphanumeric, we concatenate the first three elements.
            if len(shot_name_split) > 1:
                if shot_name_split[1].isalnum():
                    shot_name = shot_name_split[0] + shot_name_split[1]
                else:
                    shot_name = shot_name_split[0] + shot_name_split[1] + shot_name_split[2]
            else:
                # If the name wasn't split (no digits found), we keep the original name.
                shot_name = name

        return shot_name

    @staticmethod
    def untar(tar_file_path: str, untar_path: str, sudo_password: Optional[str]=None) -> bool:
        """
        Untar
        =====

        Untar a tar file.

        Args:
        -----
            `tar_file_path` (str):
                Path to tar file to untar including filename.tgz/tar.

            `untar_path` (str):
                Untar destination path.

            `sudo_password` (bool, optional):
                Password for sudo.
                (Default: `None`)

        Returns:
        --------
            bool: True if untar successful, False if not.

        Example:
        --------
            To untar a file:
            ```
            pyflame.unzip('/home/user/file.tar', '/home/user/untarred')
            ```
        """

        # Validate arguments
        if not isinstance(tar_file_path, str):
            raise TypeError(f"pyflame.untar: Expected 'tar_file_path' to be a string, got {type(tar_file_path).__name__} instead.")
        if not isinstance(untar_path, str):
            raise TypeError(f"pyflame.untar: Expected 'untar_path' to be a string, got {type(untar_path).__name__} instead.")
        if sudo_password is not None and not isinstance(sudo_password, str):
            raise TypeError(f"pyflame.untar: Expected 'sudo_password' to be a string, got {type(sudo_password).__name__} instead.")

        # Untar
        untar_command = f'tar -xvf {tar_file_path} -C {untar_path}'
        untar_command = untar_command.split()

        if sudo_password:
            process = Popen(['sudo', '-S'] + untar_command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = process.communicate(sudo_password + '\n')
            if stderr:
                print(stderr)
        else:
            process = Popen(untar_command, stdin=PIPE, stderr=PIPE, universal_newlines=True)

        # Check if files exist in untar_path
        files_exist = False
        if os.path.isdir(untar_path):
            files = os.listdir(untar_path)
            if files:
                files_exist = True

        if files_exist:
            print('--> Untar successful.\n')
            return True
        else:
            print('--> Untar failed.\n')
            return False

    @staticmethod
    def gui_resize(value: int) -> int:
        """
        GUI Resize
        ==========

        Provides scaling for Qt UI elements based on the current screen's height
        relative to a standard height of 3190 pixels(HighDPI(Retina) resolution of
        Mac Studio Display).

        Args:
        -----
            `value` (int):
                Value to be scaled.

        Returns:
        --------
            int:
                The value scaled for the current screen resolution.

        Example:
        --------
            To resize a window:
            ```
            self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
            ```
        """

        # Validate argument type
        if not isinstance(value, int):
            raise TypeError(f"pyflame.gui_resize: Expected 'value' to be an int, got {type(value).__name__} instead.")

        # Baseline resolution from mac studio display
        base_screen_height = 3190

        # Get current screen resolution
        main_window_res = pyflamewin.main_window()
        screen_resolution = main_window_res.screenGeometry()

        # Check if high DPI scaling is enabled. If so, double the screen height.
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
            screen_height = screen_resolution.height() * 2
        else:
            screen_height = screen_resolution.height()

        # Calculate screen ratio
        screen_ratio = round(screen_height / base_screen_height, 1)

        if screen_ratio >= 1.0:
            screen_ratio = screen_ratio * .9

        # Scale value based on screen ratio
        scaled_value = int(float(value) * screen_ratio * 1.1)

        return scaled_value

    @staticmethod
    def font_resize(value: int) -> int:
        """
        Font Resize
        ===========

        Provides scaling for fonts to be used in Qt UI elements.
        Fonts are first scaled with the gui_resize method. Then if the
        current display is a High DPI display(Retina Displays) the
        result is returned. If the current display is not a High DPI
        display the the value is scaled further by 0.8 so fonts don't
        appear to big.

        Args:
        -----
            `value` (int):
                Value to be scaled.

        Returns:
        --------
            int:
                The font size value scaled for the current screen resolution.

        Example:
        --------
            To resize a font:
            ```
            font.setPointSize(pyflame.font_resize(13)
            ```
        """

        # Validate argument types
        if not isinstance(value, int):
            raise TypeError(f"pyflame.font_resize: Expected 'value' to be an int, got {type(value).__name__} instead.")

        # Scale font size through gui_resize method
        scaled_size = pyflame.gui_resize(value)

        # If screen is High DPI return scaled value, if not return scaled value * .8 to scale smaller.
        if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling')  and platform.system() == 'Darwin':
            return scaled_size
        else:
            #return int(scaled_size * 0.8)
            return value

    @staticmethod
    def get_export_preset_version(preset_path: str) -> Tuple[str, str]:
        """
        Get Export Preset Version
        ==========================

        Get current export preset version and current Flame preset export version.
        This should be updated with each new version of Flame.

        Args:
        -----
            `preset_path` (str):
                Path of preset to check/update.

        Returns:
        --------
            `current_export_version` (str):
                Version of current preset export.

            `export_version` (str):
                Export preset version for currernt version of Flame.

        Example:
        --------
            To get the export preset version:
            ```
            current_export_version, export_version = pyflame.get_export_preset_version(preset_path)
            ```

        Note:
        -----
            Scripts that use this:
                Create Export Menus
                SynthEyes Export
                Create Shot
        """

        # Validate argument types
        if not isinstance(preset_path, str):
            raise TypeError(f"pyflame.get_export_preset_version: Expected 'preset_path' to be a str, got {type(preset_path).__name__} instead.")

        print('Checking export preset version...')

        print('    Export preset path:', preset_path)

        def get_current_export_version(preset_path) -> str:
            """
            Get export version for current export preset XML.
            """

            # Open export preset XML
            export_preset_xml_tree = ET.parse(preset_path)
            root = export_preset_xml_tree.getroot()

            # Get version export preset is currently set to
            for setting in root.iter('preset'):
                current_export_version = setting.get('version')
                print(f'    Current export preset version: {current_export_version}')

            return current_export_version

        def get_export_version() -> str:
            """
            Get export version for current version of Flame from the default
            Jpeg export preset XML.
            """

            # Open Flame default Jpeg export preset XML
            preset_dir = flame.PyExporter.get_presets_dir(
                flame.PyExporter.PresetVisibility.Autodesk, flame.PyExporter.PresetType.Image_Sequence
            )
            preset_path = os.path.join(
                preset_dir, "Jpeg", "Jpeg (8-bit).xml"
            )
            preset_xml_tree = ET.parse(preset_path)
            root = preset_xml_tree.getroot()

            # Get version default export preset is currently set to
            for setting in root.iter('preset'):
                default_export_version = setting.get('version')
                print(f'    Flame default export preset version: {default_export_version}')
                print('\n', end='')

            return default_export_version

        current_export_version = get_current_export_version(preset_path)
        export_version = get_export_version()

        return current_export_version, export_version

    @staticmethod
    def update_export_preset(preset_path: str) -> None:
        """
        Update Export Preset
        ====================

        Update export preset file version to match current version of flame being used.

        Args:
        -----
            `preset_path` (str):
                Path of preset to check/update.

        Example:
        --------
            To update the export preset:
            ```
            pyflame.update_export_preset(preset_path)
            ```
        """

        # Validate argument types
        if not isinstance(preset_path, str):
            raise TypeError(f"pyflame.update_export_preset: Expected 'preset_path' to be a str, got {type(preset_path).__name__} instead.")

        current_export_version, export_version = pyflame.get_export_preset_version(
            preset_path=preset_path,
            )

        # If preset version if different than current export version then update preset xml
        if current_export_version != export_version:
            export_preset_xml_tree = ET.parse(preset_path) # Open preset XML file
            root = export_preset_xml_tree.getroot()

            # Update preset version in preset XML
            for element in root.iter('preset'):
                element.set('version', export_version)

            # Write out updated preset XML file
            export_preset_xml_tree.write(preset_path)

            print(f'Export preset updated to: {export_version}\n')
        print('Export preset current, nothing to update.\n')

    @staticmethod
    def iterate_name(existing_names: List[str], new_name: str) -> str:
        """
        Iterate Name
        ============

        Generates a unique name by appending a counter to the new_name until it no longer appears in the existing_names list.

        Args:
        -----
            `existing_names` (list of str):
                A list of existing names.

            `new_name` (str):
                The base name to be made unique.

        Returns:
        --------
            str:
                A unique name not present in the existing_names list.

        Example:
        --------
            To generate a unique name:
            ```
            unique_name = pyflame.iterate_name(existing_names, new_name)
            ```
        """

        # Validate argument types
        if not isinstance(existing_names, list):
            raise TypeError(f"pyflame.iterate_name: Expected 'existing_names' to be a list, got {type(iterate_name).__name__} instead.")
        if not all(isinstance(name, str) for name in existing_names):
            raise TypeError("pyflame.iterate_name: All elements in existing_names must be a string.")
        if not isinstance(new_name, str):
            raise TypeError(f"pyflame.iterate_name: Expected 'new_name' to be a string, got {type(new_name).__name__} instead.")

        # Initialize a counter
        counter = 1

        # Initialize the potential new name
        potential_name = new_name

        # Loop until we find a unique name
        while potential_name in existing_names:
            # Increment the name with the counter
            potential_name = f"{new_name} {counter}"
            # Increment the counter
            counter += 1

        return potential_name

    @staticmethod
    def get_export_preset_names() -> List[str]:
        """
        Get Export Preset Names
        =======================

        Get Export Preset Names from Shared and Project paths. User paths are not checked.

        The following are added to the beginning of each preset name:
            Shared: File Sequence:
            Shared: Movie:
            Project: File Sequence:
            Project: Movie:

        Returns:
        --------
            list[str]:
                A list of export preset names.
        """

        print('Getting Export Presets:\n')

        # Get Shared File Sequence Export Presets
        if os.path.isdir(SHARED_FILE_SEQUENCE_PATH):
            shared_file_sequence_export_presets = [f'Shared: File Sequence: {p[:-4]}' for p in os.listdir(SHARED_FILE_SEQUENCE_PATH) if p.endswith('.xml')]
        else:
            shared_file_sequence_export_presets = []
            print('Shared File Sequence Export Presets path does not exist:', SHARED_FILE_SEQUENCE_PATH, '\n')

        # Get Shared Movie Export Presets
        if os.path.isdir(SHARED_MOVIE_EXPORT_PATH):
            shared_movie_export_presets = [f'Shared: Movie: {p[:-4]}' for p in os.listdir(SHARED_MOVIE_EXPORT_PATH) if p.endswith('.xml')]
        else:
            shared_movie_export_presets = []
            print('Shared Movie Export Presets path does not exist:', SHARED_MOVIE_EXPORT_PATH, '\n')

        # Get Project File Sequence Export Presets
        if os.path.isdir(PROJECT_FILE_SEQUENCE_PATH):
            project_file_sequence_export_presets = [f'Project: File Sequence: {p[:-4]}' for p in os.listdir(PROJECT_FILE_SEQUENCE_PATH) if p.endswith('.xml')]
        else:
            project_file_sequence_export_presets = []
            print('Project File Sequence Export Presets path does not exist:', PROJECT_FILE_SEQUENCE_PATH, '\n')

        # Get Project Movie Export Presets
        if os.path.isdir(PROJECT_MOVIE_EXPORT_PATH):
            project_movie_export_presets = [f'Project: Movie: {p[:-4]}' for p in os.listdir(PROJECT_MOVIE_EXPORT_PATH) if p.endswith('.xml')]
        else:
            project_movie_export_presets = []
            print('Project Movie Export Presets path does not exist:', PROJECT_MOVIE_EXPORT_PATH, '\n')

        # Combine all export presets
        export_presets = shared_file_sequence_export_presets + shared_movie_export_presets + project_file_sequence_export_presets + project_movie_export_presets
        pyflame.print_list(
            list_name='Export Presets',
            list_items=export_presets,
            )

        print('Export Preset Check Complete.\n')

        return export_presets

    @staticmethod
    def convert_export_preset_name_to_path(export_preset_name: str) -> str:
        """
        Convert Export Preset Name to Path
        ==================================

        Convert Export Preset Name from Preset Menus(PyFlamePushButtonMenu) to Path.

        Preset Menu names should be in the following format:
            Shared: File Sequence: Jpeg (8-bit)
            Project: File Sequence: Jpeg (8-bit)
            Shared: Movie: Quicktime 4444
            Project: Movie: Quicktime 4444

        Shared:, Project:, File Sequence:, and Movie: are fixed strings and will be used to determine the path.

        Args:
        -----
            export_preset_name (str):
                Export preset name to convert to path.
                Example: 'Shared: File Sequence: Jpeg (8-bit)'

        Returns:
        --------
            str:
                Path to export preset.

        Raises:
        -------
            TypeError:
                If 'export_preset_name' is not a string.

        Example:
        --------
            To convert an export preset name to a path:
            ```
            export_preset_name = 'Shared: File Sequence: Jpeg (8-bit)'
            export_preset_path = pyflame.convert_export_preset_name_to_path(export_preset_name)
            ```

            export_preset_path will be:
            ```
            /opt/Autodesk/shared/presets/file_sequence/Jpeg (8-bit).xml
            ```
        """

        # Validate argument types
        if not isinstance(export_preset_name, str):
            raise TypeError(f"pyflame.convert_export_preset_name_to_path: Expected 'export_preset_name' to be a string, got {type(export_preset_name).__name__} instead.")

        # Convert export preset name to path
        if export_preset_name == '':
            return ''
        elif 'Shared: File Sequence:' in export_preset_name:
            print('Shared: File Sequence:',os.path.join(SHARED_FILE_SEQUENCE_PATH, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(SHARED_FILE_SEQUENCE_PATH, f'{export_preset_name.split(": ")[2]}.xml')
        elif 'Shared: Movie:' in export_preset_name:
            print('Shared: Movie:', os.path.join(SHARED_MOVIE_EXPORT_PATH, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(SHARED_MOVIE_EXPORT_PATH, f'{export_preset_name.split(": ")[2]}.xml')
        elif 'Project: File Sequence:' in export_preset_name:
            print('Project: File Sequence:', os.path.join(PROJECT_FILE_SEQUENCE_PATH, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(PROJECT_FILE_SEQUENCE_PATH, f'{export_preset_name.split(": ")[2]}.xml')
        elif 'Project: Movie:' in export_preset_name:
            print('Project: Movie:', os.path.join(PROJECT_MOVIE_EXPORT_PATH, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(PROJECT_MOVIE_EXPORT_PATH, f'{export_preset_name.split(":")[2]}.xml')
        else:
            return ''

    @staticmethod
    def set_shot_tagging(pyobject: Union[flame.PyLibrary, flame.PyFolder, flame.PyDesktop, flame.PyBatch, flame.PyClip], shot_name: str, append: bool=False) -> None:
        """
        Set Shot Tagging
        ================

        Set shot tagging for Flame object.

        Tags can be appended to existing tags or set directly. Default is to set tag directly.

        Args:
        -----
            pyobject (flame.PyObject):
                Flame object to set tagging for. Can be PyLibrary, PyFolder, PyDesktop, PyBatch, or PyClip.

            shot_name (str):
                Shot name to set as tag.

            append (bool, optional):
                Append shot name tag to existing tags.
                (Default: False)

        Raises:
        -------
            TypeError:
                If 'pyobject' is not a PyLibrary, PyFolder, PyDesktop, PyBatch, or PyClip.
                If 'shot_name' is not a string.
                If 'append' is not a boolean.

        Notes:
        ------
            - If appending tags, existing tags starting with ShotName: are removed before new tag is added.
        """

        # Validate arguments
        if not isinstance(pyobject, (flame.PyLibrary, flame.PyFolder, flame.PyDesktop, flame.PyBatch, flame.PyClip)):
            raise TypeError(f"pyflame.set_shot_tagging: Expected 'pyobject' to be a PyLibrary, PyFolder, PyDesktop, PyBatch, or PyClip, got {type(pyobject).__name__} instead.")
        if not isinstance(shot_name, str):
            raise TypeError(f"pyflame.set_shot_tagging: Expected 'shot_name' to be a string, got {type(shot_name).__name__} instead.")
        if not isinstance(append, bool):
            raise TypeError(f"pyflame.set_shot_tagging: Expected 'append' to be a boolean, got {type(append).__name__} instead.")

        # If appending tag, get all existing object tags and add new tag otherwise set tag directly
        if append:
            # Get all existing object tags
            all_tags = pyobject.tags.get_value()

            # If tag starting with ShotName: already exists, remove it
            if any(tag.startswith('ShotName:') for tag in all_tags):
                all_tags = [tag for tag in all_tags if not tag.startswith('ShotName:')]

            # Add new ShotName tag
            all_tags.append(f'ShotName: {shot_name}')

            pyobject.tags = all_tags
        else:
            pyobject.tags = [f'ShotName: {shot_name}'] # Set tag directly

    @staticmethod
    def find_by_tag(pyobject: Union[flame.PyLibrary, flame.PyDesktop, flame.PyFolder], target_tag: str, sorted: bool=True):
        """
        Find By Tag
        ===========

        Perform binary or linear search on PyObject's contained objects by tags.

        For example, search through a Library for a folder with a specific tag. It will not recursively search through subfolders.

        If `sorted` is True, uses binary search to efficiently find a Flame object that contains the target tag in its tag list.
        The search assumes PyObjects contained within the given PyObject are sorted by the tag being searched for.
        For instance, if searching a folder, the folder's immediate contained objects (subfolders and clips) must
        be sorted by the tag being searched for.

        If `sorted` is False, performs a linear search through the PyObjects contained within the given PyObject. This can be slower
        for large lists of PyObjects.

        Args:
        -----
            pyobject (flame.PyLibrary, flame.PyDesktop, or flame.PyFolder):
                Flame PyObject (Library, Desktop, or Folder) that will be searched for item with target tag.

            target_tag (str):
                Tag to search for. If contains ':', will match against tag_type:value format.

            sorted (bool):
                If True, assumes PyObjects contained within `pyobject` are sorted by tag.
                When True, performs a binary search. If False, performs a linear search.
                (Default: True)

        Returns:
        --------
            The matching Flame PyObject if found, None otherwise.

        Examples:
        --------
            Find a shot folder by tag where PyObjects are sorted by tag:
            ```
            find_by_tag(
                pyobject=<PyLibraryObject>,
                target_tag='ShotName: PYT_0010',
                )
            ```

            Find a clip by tag where PyObjects are not sorted by tag:
            ```
            find_by_tag(
                pyobject=<PyLibraryObject>,
                target_tag='ShotName: PYT_0010',
                sorted=False
                )
            ```
        """

        # If sorted is True, perform binary search other wise perform a linear search
        if sorted:
            print('Performing Binary Tag Search')
            # Split target tag at ': ' to get tag_type if ':' is present
            if ':' in target_tag:
                tag_type = target_tag.split(': ', 1)[0]
            else:
                tag_type = target_tag

            # Perform binary search
            start, end = 0, len(pyobject) - 1

            while start <= end:
                mid = (start + end) // 2
                pyobject_tags = pyobject[mid].tags.get_value()
                # Loop through folder_tags to fing tag starting with tag_type
                for tag in pyobject_tags:
                    if tag.startswith(tag_type):
                        pyobject_tag = tag
                        break

                # Perform a direct comparison
                if pyobject_tag == target_tag:
                    print(f'Found Tagged PyObject: {pyobject[mid].name}\n')
                    return pyobject[mid]  # Return the PyObject object if found
                elif pyobject_tag < target_tag:
                    start = mid + 1
                else:
                    end = mid - 1
        else:
            # Perform linear search
            print('Performing Linear Tag Search')
            for pyobject_item in pyobject:
                if target_tag in pyobject_item.tags.get_value():
                    print(f'Found Tagged PyObject: {pyobject_item.name}\n')
                    return pyobject_item

        print(f'Tagged PyObject: {target_tag} Not Found\n')

        return None

    @staticmethod
    def shot_name_from_clip(clip: flame.PyClip) -> str:
        """
        Shot Name From Clip
        ===================

        Get shot name from clip.

        Args:
        -----
            clip (flame.PyClip):
                Clip to get shot name from

        Returns:
        --------
            shot_name (str):
                Shot name

        Notes:
        -----
            - Check if clip has assigned Shot Name.
            - Check if clip is tagged with ShotName (ShotName: PYT_0010)
            - If no Shot Name is assigned or tagged, extract shot name from clip name.
        """

        pyflame.print('Getting Shot Name From Clip', new_line=False)

        # Check if shot name is assigned to clip
        assigned_shot_name = str(clip.versions[0].tracks[0].segments[0].shot_name)[1:-1]
        if assigned_shot_name != '':
            shot_name = assigned_shot_name
            pyflame.print(f'Shot Name Found: {shot_name}', text_color=TextColor.GREEN)
            return shot_name

        # Check if clip is tagged with ShotName
        if clip.tags:
            clip_tags = clip.tags.get_value()
            shot_name_tag = [tag for tag in clip_tags if tag.startswith('ShotName:')]
            if shot_name_tag:
                shot_name = shot_name_tag[0].split(': ')[1]
                pyflame.print(f'Shot Name Tag Found: {shot_name}', text_color=TextColor.GREEN)
                return shot_name

        # Get shot name from clip name
        clip_name = str(clip.name)[1:-1]
        print('Clip Name:', clip_name)

        # Split clip name into list by numbers in clip name
        shot_name_split = re.split(r'(\d+)', clip_name)
        shot_name_split = [s for s in shot_name_split if s != '']
        #print('shot_name_split:', shot_name_split)

        # If second part of split name contains only alphanumeric chars,
        # combine first two parts (e.g. "Shot" + "01" -> "Shot01")
        # Otherwise combine first three parts to handle separators
        # (e.g. "Shot" + "_" + "01" -> "Shot_01")
        if shot_name_split[1].isalnum():
            shot_name = shot_name_split[0] + shot_name_split[1]
        else:
            shot_name = shot_name_split[0] + shot_name_split[1] + shot_name_split[2]

        # Tag clip with shot name, pass if Flame 2025 or older
        try:
            pyflame.set_shot_tagging(clip, shot_name)
        except:
            pass

        pyflame.print(f'Shot Name from Clip Name: {shot_name}', text_color=TextColor.GREEN)

        return shot_name

    @staticmethod
    def move_to_shot_folder(shot_name: str, pyobject: Union[flame.PyClip, flame.PyBatch, flame.PyDesktop], search_location: Union[flame.PyLibrary, flame.PyFolder], dest_folder_path: str) -> None:
        """
        Move to Shot Folder
        ===================

        Move PyClip, PyBatch, or PyDesktop to a Media Panel shot folder in search_location(flame.PyLibrary or flame.PyFolder)

        Folders in search location must be tagged with 'ShotName: <shot_name>', i.e. 'ShotName: PYT_0010'

        Args:
        -----
            shot_name (str):
                Name of shot

            pyobject (Union[flame.PyClip, flame.PyBatch, flame.PyDesktop]):
                PyClip, PyBatch, or PyDesktop to move to shot folder.

            search_location (Union[flame.PyLibrary, flame.PyFolder]):
                Media Panel Library or Folder to search through for shot folder.

            dest_folder_path (str):
                Destination folder path in Shot Folder.
                Example: 'Shot_Folder/Plates'
        """

        def get_folder_from_path(folder: flame.PyFolder, media_panel_folder_path: str) -> flame.PyFolder:
            """
            Get Folder from Path
            ====================

            Recursively find Media Panel folder from path

            Args:
            -----
                folder (flame.PyFolder):
                    Media Panel Folder to search through for destination folder.

                media_panel_folder_path (str):
                    Media Panel destination folder path.
                    Example: 'Shot_Folder/Plates'

            Returns:
            --------
                dest_folder (flame.PyFolder):
                    Destination folder.
            """


            def find_next_folder(folder: flame.PyFolder, folder_list: list) -> flame.PyFolder:
                """
                Find Next Folder
                ===============

                Recursively find next folder in folder list.
                """

                for sub_folder in folder.folders:
                    if sub_folder.name == folder_list[0]:
                        return find_next_folder(sub_folder, folder_list[1:])
                return folder

            # Convert media_panel_folder_path to list and remove first element (root folder)
            folder_list = media_panel_folder_path.split('/', 1)[1].split('/')

            # Find destination folder
            dest_folder = find_next_folder(shot_folder, folder_list)

            return dest_folder

        # Create target tag for shot folder search
        target_tag = f'ShotName: {shot_name}'

        # Search through search_location(flame.PyLibrary or flame.PyFolder) for shot folder with matching target tag
        shot_folder = pyflame.find_by_tag(search_location.folders, target_tag)

        dest_folder = get_folder_from_path(shot_folder, dest_folder_path)
        flame.media_panel.move(pyobject, dest_folder)

pyflame = _PyFlameFunctions()

#-------------------------------------
# [Internal Utility Functions/Classes]
#-------------------------------------

class _WindowResolution():
    """
    Window Resolution
    =================

    Utility class to determine the main window resolution based on the Qt version.
    It checks the major version of the QtCore module and uses the appropriate method
    to obtain the main window resolution. Fixes issues when using QT with Shotgrid
    in Flame 2025. Thanks to Ari Brown for this fix.
    """

    @staticmethod
    def main_window():
        """
        Get the main window resolution based on the Qt version.

        Returns:

            main_window_res : QDesktopWidget or QScreen
                The main window resolution object. The type depends on the Qt version:
                    - QtWidgets.QDesktopWidget for Qt versions less than 6
                    - QtGui.QGuiApplication.primaryScreen for Qt versions 6 and above
        """

        if QtCore.__version_info__[0] < 6:
            main_window_res = QtWidgets.QDesktopWidget()
        else:
            main_window_res = QtGui.QGuiApplication.primaryScreen()
        return main_window_res

pyflamewin = _WindowResolution()

def _load_font():
    """
    Load Font
    =========

    Load font from path for use in all PyFlame QT Widgets.

    If font is not found, Discreet font is used as a fallback.

    Args:
    -----
        font_path (dict):
            Name and path to font in dictionary form.

    Returns:
    --------
        font (QtGui.QFont):
            Loaded font.
        font_size (int):
            Font size.
    """

    # Set font path(s)
    font_path = {
        "MontserratRegular": f'{SCRIPT_PATH}/assets/fonts/Montserrat-Regular.ttf',
        "MontserratLight": f'{SCRIPT_PATH}/assets/fonts/Montserrat-Light.ttf',
        }

    font_size = pyflame.font_resize(14)

    # Dictionary to store loaded QFont objects
    loaded_fonts = {}

    for font_name, path in font_path.items():
        # Convert to absolute path
        abs_path = os.path.abspath(path)

        # Load the font
        font_id = QtGui.QFontDatabase.addApplicationFont(abs_path)
        if font_id == -1:
            print(f'PyFlameLib: Failed to load the font: {abs_path}')
            # Provide a fallback font
            loaded_fonts[font_name] = QtGui.QFont("Discreet", font_size)
        else:
            # Get the font family name
            families = QtGui.QFontDatabase.applicationFontFamilies(font_id)
            if families:
                font_family = families[0]
                loaded_fonts[font_name] = QtGui.QFont(font_family, font_size)
                print(f'PyFlameLib: Font Successfully Loaded: {font_family}: {font_name}')
            else:
                # Fallback if no family returned
                loaded_fonts[font_name] = QtGui.QFont("Discreet", font_size)
                print(f'PyFlameLib: Font Load Failed: {font_name} - Using Discreet Font')

    font = loaded_fonts['MontserratRegular']
    font.setStretch(88)

    font_light = loaded_fonts['MontserratLight']
    font_light.setStretch(88)

    return font, font_size

FONT, FONT_SIZE = _load_font()

class _WindowSideLineOverlay(QtWidgets.QWidget):
    """
    Overlay Widget
    ==============

    This is a private class, should not be used outside this module.

    This class is used to help add the vertical and horizontal colored lines to the
    PyFlameDialogWindow and PyFlameMessageWindow windows. It draws a vertical line
    along the left edge of the parent widget.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setPalette(QtGui.QPalette(QtCore.Qt.transparent))
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        # Get the RGB string from parent's line_color
        rgb_str = self.parent().line_color.value
        # Extract RGB values using string manipulation
        rgb_values = rgb_str.strip('rgb()').split(',')
        r, g, b = map(int, rgb_values)
        # Create QColor with the RGB values
        color = QtGui.QColor(r, g, b)
        painter.setPen(QtGui.QPen(color, pyflame.gui_resize(2)))
        painter.drawLine(0, 0, 0, 1000)

#-------------------------------------
# [PyFlame Config]
#-------------------------------------

class PyFlameConfig:
    """
    PyFlameConfig
    =============

    A class to manage configuration settings for the PyFlame script.

    This class handles loading and saving configuration settings from and to a JSON file.
    It updates instance attributes based on the configuration values.

    Values can be provided as their original data types. Values no longer need to be converted to strings.

    Args:
    -----
        `config_values` (Dict[str, Any]):
            A dictionary to store configuration key-value pairs.

        `config_path` (str):
            The file path to the configuration JSON file.

        `script_name` (str):
            The name of the script. This is used to identify the script in the configuration file. This does not need to be set in most cases.
            (Default: `SCRIPT_NAME`)

    Methods:
    --------
        `load_config(config_values: Dict[str, Any])`:
            Loads configuration values from a JSON file and updates instance attributes.

        `save_config(config_values: Dict[str, Any])`:
            Saves the current configuration values to a JSON file.

        `get_config_values()` -> Dict[str, Any]:
            Returns the current configuration values.

    Raises:
    -------
        TypeError:
            If `config_values` is not a dictionary.
            If `config_path` is not a string.
        ValueError:
            If `config_values` is empty.

    Examples:
    ---------
        To Load/Create settings:
        ```
        settings = PyFlameConfig(
                config_values={
                'camera_path': '/opt/Autodesk',
                'scene_scale': 100,
                'import_type': 'Action Objects',
                'st_map_setup': False,
                }
            )
        ```

        To save settings:
        ```
        settings.save_config(
            config_values={
                'camera_path': self.path_entry.text(),
                'scene_scale': self.scene_scale_slider.get_value(),
                'import_type': self.import_type.text(),
                'st_map_setup': self.st_map_setup.isChecked(),
                }
            )
        ```

        To get setting values:
        ```
        print(settings.camera_path)
        >'/opt/Autodesk'
        ```
    """

    def __init__(self,
                 config_values: Dict[str, Any],
                 config_path: str=os.path.join(SCRIPT_PATH, 'config/config.json'),
                 script_name: str=SCRIPT_NAME
                 ):

        # Argument type validation
        if not isinstance(config_values, dict):
            raise TypeError(f"PyFlameConfig: Expected 'config_values' to be a dictionary, got {type(config_values).__name__} instead.")
        if not config_values:
            raise ValueError("PyFlameConfig: config_values dictionary cannot be empty.")
        if not isinstance(config_path, str):
            raise TypeError(f"PyFlameConfig: Expected 'config_path' to be a string, got {type(config_path).__name__} instead.")

        # Initialize instance attributes
        self.config_values: Dict[str, Any] = config_values
        self.config_path = config_path
        self.script_name = script_name

        # Load the configuration
        self.load_config()

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads the configuration from the JSON file and updates instance attributes.

        This method reads the configuration file specified by `config_path`. If the file exists,
        it updates the instance's configuration values and attributes with those read from the file.
        If the file does not exist, it saves the default configuration values to the file.
        """

        #print('Loading script configuration...\n')

        pyflame.print('Loading Script Configuration', underline=True, )

        # Load the configuration from the JSON file
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                loaded_config: Dict[str, Any] = json.load(f)
                # Update the default values with the loaded ones
                self.config_values.update(loaded_config)
        else:
            # Ensure the config directory exists
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            # Save the default configuration values if the file does not exist
            self.save_config(self.config_values)

        # Set the attributes from config values
        for key, value in self.config_values.items():
            setattr(self, key, value)

        # Print values to terminal
        pyflame.print_json(
            json_data=self.config_values,
            indent=2,
            )

        print('-' * 28, '\n')

        pyflame.print('Script Configuration Loaded', arrow=True)

    def save_config(self, config_values: Optional[Dict[str, Any]]=None, config_path: Optional[str]=None) -> None:
        """
        Save Config
        ===========

        Saves the current configuration values to the JSON file.

        This method updates the configuration values with any provided values and writes them to
        the configuration file specified by `config_path`. It ensures that existing values are
        preserved unless explicitly overwritten.

        Args:
        -----
            `config_values` (Dict[str, Any]):
                A dictionary of configuration values to update.
                (Default: None)

            `config_path` (str):
                The file path to save the configuration JSON file. This does not need to be set in most cases.
                (Default: None)

        Raises:
        -------
            TypeError:
                If `config_values` is not a dictionary.

        Example:
        --------
            To save the current configuration values:
            ```
            settings.save_config(
                config_values={
                    'camera_path': self.path_entry.text(),
                    'scene_scale': self.scene_scale_slider.get_value(),
                    'import_type': self.import_type.text(),
                    'st_map_setup': self.st_map_setup.isChecked(),
                    }
                )
            ```
        """

        # Validate argument types
        if config_values is not None and not isinstance(config_values, dict):
            raise TypeError(f"PyFlameConfig.save_config: Expected 'config_values' to be a dictionary or None, got {type(config_values).__name__} instead.")
        if config_path is not None and not isinstance(config_path, str):
            raise TypeError(f"PyFlameConfig.save_config: Expected 'config_path' to be a string or None, got {type(config_path).__name__} instead.")

        pyflame.print('Saving Script Configuration', underline=True, )

        if config_path is None:
            config_path = self.config_path

        if config_values:
            self.config_values.update(config_values)

        # Ensure the script name is in the config
        self.config_values['script_name'] = self.script_name

        # script_name should be the first key in the config
        self.config_values = {key: self.config_values[key] for key in ['script_name'] + list(self.config_values.keys())}

        # Read existing config to keep unaltered values
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                existing_config: Dict[str, Any] = json.load(f)
        else:
            existing_config = {}

        # Update only provided values
        existing_config.update(self.config_values)

        with open(config_path, 'w') as f:
            json.dump(existing_config, f, indent=4)

        # Update the instance attributes with new config values
        for key, value in self.config_values.items():
            setattr(self, key, value)

        # Print values to terminal
        pyflame.print_json(
            json_data=self.config_values,
            indent=2,
            )

        print('-' * 27, '\n')

        pyflame.print('Script Configuration Saved', arrow=True)

    def get_config_values(config_path: str) -> Dict[str, Any]:
        """
        Get Config Values
        =================

        Returns the current configuration values.

        This method provides access to the current state of configuration values stored in the instance.

        Args:
        -----
            `config_path` (str):
                The file path to the configuration JSON file.

        Returns:
        --------
            Dict[str, Any]: The current configuration values.
        """

        # Validate argument type
        if not isinstance(config_path, str):
            raise TypeError(f"PyFlameConfig.get_config_values: Expected 'config_path' to be a string, got {type(config_path).__name__} instead.")

        # Load the configuration from the JSON file
        with open(config_path, 'r') as f:
            return json.load(f)

#-------------------------------------
# [PyFlame QT Widget Classes]
#-------------------------------------

class PyFlameButton(QtWidgets.QPushButton):
    """
    PyFlameButton
    =============

    Custom QT Flame Button Widget Subclass

    Args:
    -----
        `text` (str):
            PyFlameButton text.

        `connect` (callable):
            Function to call when PyFlameButton is clicked.

        `width` (int, optional):
            PyFlameButton width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameButton height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameButton to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `max_height` (bool, optional):
            Set PyFlameButton to maximum height. Use if height is being set by layout. Overrides `height` if set to True.
            (Default: `False`)

        `color` (Color, optional):
            PyFlameButton color. See Color Options below.
            (Default: `Color.GRAY`)

        `tooltip` (str, optional):
            PyFlameButton tooltip text.
            (Default: `None`)

    Color Options:
    --------------
        - `Color.GRAY`: Standard gray button.
        - `Color.BLUE`: Blue button.
        - `Color.RED`: Red button.

    Methods:
    --------
        `set_button_color(color)`:
            Set the color of the button after its creation using Color Options.

    Examples:
    ---------
        Create a blue PyFlameButton:
        ```
        button = PyFlameButton(
            text='Button Name',
            connect=some_function,
            color=Color.BLUE
            )
        ```

        To change the button color after creation:
        ```
        button.set_button_color(Color.BLUE)
        ```

        Enable or disable the button:
        ```
        button.setEnabled(True)
        button.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlameButton',
                 text: str,
                 connect: Callable[..., None],
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 max_height: bool=False,
                 color: Color=Color.GRAY,
                 tooltip: Optional[str]=None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameButton', 'text', 'string', text)
            if not callable(connect):
                pyflame.raise_type_error(f'PyFlameButton', 'connect', 'callable', connect)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameButton', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameButton', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameButton', 'max_width', 'bool', max_width)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameButton', 'max_height', 'bool', max_height)
            if not isinstance(color, Color):
                pyflame.raise_type_error(f'PyFlameButton', 'color', 'Color Enum', color)
            if tooltip is not None and not isinstance(tooltip, str):
                pyflame.raise_type_error(f'PyFlameButton', 'tooltip', 'string or None', tooltip)

        validate_arguments()

        # Set Button Settings
        self.setFont(FONT)
        self.setText(text)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(connect)
        self.setToolTip(tooltip)

        # Set Button Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))
        if max_height:
            self.setMaximumHeight(pyflame.gui_resize(3000))

        # Set Button Stylesheet
        self._set_stylesheet(color)

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def set_button_color(self, color: Color) -> None:
        """
        Set Button Color
        ================

        Set the color of the button after its creation.

        This public method updates the button's appearance by changing its color.

        Args:
        -----
            `color` (Color):
                The color to set for the button: `Color.GRAY`, `Color.Blue`, `Color.RED`

        Raises:
        -------
            ValueError:
                If the provided `color` is not a supported color option.

        Example:
        --------
            Change the button color to red:

            ```
            button.set_button_color(Color.RED)
            ```
        """

        if color not in {Color.GRAY, Color.BLUE, Color.RED}:
            raise ValueError(f'PyFlameButton.set_button_color: Unsupported color: {color}. Supported colors are: GRAY, BLUE, RED.')

        self._set_stylesheet(color)
        self.update()  # Refresh the button's appearance

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self, color: Color) -> None:
        """
        Set Style Sheet
        ===============

        Private method to set the widget stylesheet.

        The stylesheet has three color options for the button: GRAY, BLUE, and RED.

        Args:
        -----
            `color` (Color):
                The color to set for the button: `Color.GRAY`, `Color.Blue`, `Color.RED`

        Raises:
        -------
            ValueError:
                If the provided `color` is not a supported color option.
        """

        # Validate argument
        if color not in {Color.GRAY, Color.BLUE, Color.RED}:
            raise ValueError(f'PyFlameButton._set_stylesheet: Unsupported color: {color}. Supported colors are: GRAY, BLUE, RED.')

        # Set button color based on color enum
        if color == Color.GRAY:
            self.setStyleSheet(f"""
                QPushButton {{
                    color: {Color.BUTTON_TEXT.value}; /* Button text color */
                    background-color: {Color.GRAY.value}; /* Button color */
                    border: none; /* Button border */
                    }}
                QPushButton:hover{{
                    border: 1px solid {Color.BORDER.value}; /* Hover button border */
                    }}
                QPushButton:pressed{{
                    color: {Color.TEXT_SELECTED.value}; /* Pressed text color */
                    background-color: {Color.SELECTED_GRAY.value}; /* Pressed button color */
                    border: 1px solid {Color.BORDER.value}; /* Pressed button border */
                    }}
                QPushButton:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    background-color: {Color.GRAY.value}; /* Disabled button color */
                    border: none; /* Disabled button border */
                    }}
                QToolTip{{
                    color: {Color.WHITE.value}; /* Tooltip text color */
                    background-color: {Color.SELECTED_GRAY.value}; /* Tooltip background color */
                    border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                    }}
                """)

        elif color == Color.BLUE:
            self.setStyleSheet(f"""
                QPushButton{{
                    color: {Color.TEXT_BRIGHT.value}; /* Button text color */
                    background-color: {Color.BLUE.value}; /* Button color */
                    border: none; /* Button border */
                    }}
                QPushButton:hover{{
                    border: 1px solid {Color.BORDER_BRIGHTER.value}; /* Hover button border */
                    }}
                QPushButton:pressed{{
                    color: {Color.TEXT_SELECTED.value}; /* Pressed text color */
                    border: 1px solid {Color.BORDER_BRIGHTER.value}; /* Pressed button border */
                    }}
                QPushButton:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    background-color: {Color.GRAY.value}; /* Disabled button color */
                    border: none; /* Disabled button border */
                    }}
                QToolTip{{
                    color: {Color.WHITE.value}; /* Tooltip text color */
                    background-color: {Color.SELECTED_GRAY.value}; /* Tooltip background color */
                    border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                    }}
                """)

        elif color == Color.RED:
            self.setStyleSheet(f"""
                QPushButton{{
                    color: {Color.TEXT_BRIGHT.value}; /* Button text color */
                    background-color: {Color.RED.value}; /* Button color */
                    border: none; /* Button border */
                    }}
                QPushButton:hover{{
                    border: 1px solid {Color.BORDER.value}; /* Hover button border */
                    }}
                QPushButton:pressed{{
                    color: {Color.TEXT_SELECTED.value}; /* Pressed text color */
                    border: 1px solid {Color.BORDER.value}; /* Pressed button border */
                    }}
                QPushButton:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    background-color: {Color.GRAY.value}; /* Disabled button color */
                    border: none; /* Disabled button border */
                    }}
                QToolTip{{
                    color: {Color.WHITE.value}; /* Tooltip text color */
                    background-color: {Color.SELECTED_GRAY.value}; /* Tooltip background color */
                    border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                    }}
                """)

class PyFlameButtonGroup(QtWidgets.QButtonGroup):
    """
    PyFlameButtonGroup
    ==================

    Custom QT Flame Button Group Widget Subclass

    This class allows for grouping multiple buttons to control their checked state collectively.
    It supports setting the buttons to exclusive or non-exclusive behavior, meaning that either
    only one button can be checked at a time or multiple buttons can be checked simultaneously.

    Args:
    -----
        `buttons` (list):
            List of buttons to be part of group.

        `set_exclusive` (bool, optional):
            If True, only one button can be checked at a time.
            (Default: `True`)

    Example:
    --------
        To create a button group:
        ```
        button_group = PyFlameButtonGroup(
            buttons=[
                self.action_node_only_push_button,
                self.st_map_setup_button,
                self.patch_setup_button,
                ],
            )
        ```
    """

    def __init__(self: 'PyFlameButtonGroup',
                    buttons: list,
                    set_exclusive: bool=True,
                    ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(buttons, list):
                pyflame.raise_type_error(f'PyFlameButtonGroup', 'buttons', 'list', buttons)
            if not all(isinstance(button, QtWidgets.QPushButton) for button in buttons):
                pyflame.raise_type_error(f'PyFlameButtonGroup', 'buttons', 'QPushButton', buttons)
            if not isinstance(set_exclusive, bool):
                pyflame.raise_type_error(f'PyFlameButtonGroup', 'set_exclusive', 'bool', set_exclusive)

        validate_arguments()

        # Set exclusive
        self.setExclusive(set_exclusive)

        # Add buttons to group
        for button in buttons:
            self.addButton(button)

class PyFlameEntry(QtWidgets.QLineEdit):
    """
    PyFlameEntry
    ============

    Custom QT Flame LineEdit Widget Subclass

    Replaces PyFlameLineEdit.

    Args:
    -----
        `text` (str):
            Initial text to be displayed in the entry field.

        `align` (Align, optional):
            Align text to left, right, or center.
            See Align Options below.
            (Default: `Align.LEFT`)

        `width` (int, optional):
            Width of the entry field in pixels.
            (Default: `50`)

        `height` (int, optional):
            Height of the entry field in pixels.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameEntry to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `text_changed` (callable, optional):
            Function to be called whenever the text in the entry field changes. This is typically used to perform live updates based on user input.
            (Default: `None`)

        `placeholder_text` (str):
            Temporary text to display when PyFlameEntry is empty.
            (Default: `""`)

        `read_only` (bool, optional):
            Sets the entry to be read-only if True, disabling user input and applying a distinct visual style to indicate this state. Text is not selectable.
            (Default: `False`)

        `tooltip` (str, optional):
            Tooltip text to display when hovering over the entry field.
            (Default: `None`)

    Align Options:
    --------------
        - `Align.LEFT`: Aligns text to the left side of the label.
        - `Align.RIGHT`: Aligns text to the right side of the label.
        - `Align.CENTER`: Centers text within the label.

    Methods:
    --------
        `text_changed(connected_function: Callable)`:
            Calls a function when the text in the entry field changes.

    Examples:
    ---------
        To create a PyFlameEntry:
        ```
        entry = PyFlameEntry(
            value='Something here'
            )
        ```

        To get text from PyFlameEntry:
        ```
        entry.text()
        ```

        To set PyFlameEntry text:
        ```
        entry.setText('Some text here')
        ```

        To enable/disable PyFlameEntry:
        ```
        entry.setEnabled(True)
        entry.setEnabled(False)
        ```

        To set PyFlameEntry as focus (cursor will be in PyFlameEntry):
        ```
        entry.setFocus()
        ```
    """

    def __init__(self: 'PyFlameEntry',
                 text: str,
                 align: Align=Align.LEFT,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 text_changed: Optional[Callable]=None,
                 placeholder_text: str="",
                 read_only: bool=False,
                 tooltip: Optional[str]=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameEntry', 'text', 'string', text)
            if not isinstance(align, Align):
                pyflame.raise_type_error(f'PyFlameEntry', 'align', 'Align Enum', align)
            if width is not None and not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameEntry', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameEntry', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameEntry', 'max_width', 'bool', max_width)
            if text_changed is not None and not callable(text_changed):
                pyflame.raise_type_error(f'PyFlameEntry', 'text_changed', 'callable', text_changed)
            if not isinstance(placeholder_text, str):
                pyflame.raise_type_error(f'PyFlameEntry', 'placeholder_text', 'string', placeholder_text)
            if not isinstance(read_only, bool):
                pyflame.raise_type_error(f'PyFlameEntry', 'read_only', 'bool', read_only)
            if tooltip is not None and not isinstance(tooltip, str):
                pyflame.raise_type_error(f'PyFlameEntry', 'tooltip', 'string or None', tooltip)

        validate_arguments()

        # Set Entry Settings
        self.setFont(FONT)
        self.setText(str(text))
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.read_only = read_only
        self.setReadOnly(read_only)
        self.setPlaceholderText(placeholder_text)
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay * 1000
        self.tooltip_duration = tooltip_duration * 1000

        # Create Tooltip using PyFlameLabel
        if self.tooltip:
            self._create_tooltip_label(tooltip)

        # Settings for Alt+Click to show full entry text
        self.setMouseTracking(True)  # Enable mouse tracking
        self.alt_pressed = False
        self.mouse_inside = False
        self.full_entry_text_label = None  # Custom tooltip label
        self.installEventFilter(self)

        # Connect textChanged signal to text_changed function if provided
        if text_changed is not None:
            self.textChanged.connect(text_changed)

        # Set Entry Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Set Text Alignment
        if align == Align.LEFT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        elif align == Align.RIGHT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        elif align == Align.CENTER:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

        # Set Entry Stylesheet
        self._set_stylesheet(self.read_only)

    #-------------------------------------
    # [Public Methods]
    #-------------------------------------

    def text_changed(self, connected_function: Callable) -> None:
        """
        Text Changed
        ============

        Calls a function when the text in the entry field changes.

        Args:
        -----
            `connected_function` (callable):
                Function to call when the text in the entry field changes.
        """

        # Validate argument type
        if not callable(connected_function):
            pyflame.raise_type_error(f'PyFlameEntry', 'connected_function', 'callable', connected_function)

        # Connect textChanged signal to connected_function
        self.textChanged.connect(connected_function)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self, read_only) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the widget stylesheet.

        The stylesheet has two states: read-only and editable.

        If read-only, the background color is darker and the text color is gray.
        Otherwise, the default Flame line edit stylesheet is applied.

        Args:
        -----
            `read_only` (bool):
                Indicates whether the PyFlameLineEdit is read-only.

        Raises:
        -------
            TypeError:
                If `read_only` is not a boolean.

        Example:
        --------
            Set PyFlameEntry stylesheet to `read_only`:
            ```
            self._set_stylesheet(read_only)
            ```
        """

        # Validate argument type
        if not isinstance(read_only, bool):
            raise TypeError(f'_set_stylesheet: Invalid read_only argument: {read_only}. Must be a boolean.')

        # Set line edit stylesheet based on read-only state
        if read_only:
            self.setStyleSheet(f"""
                QLineEdit{{
                    color: {Color.TEXT.value};
                    background-color: {Color.TEXT_READ_ONLY_BACKGROUND.value};
                    border: 1px solid {Color.TEXT_READ_ONLY_BACKGROUND.value};
                    padding-left: 1px;
                    }}
                QLineEdit:hover{{
                    border: 1px solid {Color.BORDER.value};
                    padding-left: 1px;
                    }}
                QLineEdit:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    background-color: {Color.DISABLED_GRAY.value};
                    border: 1px solid {Color.DISABLED_GRAY.value};
                    padding-left: 1px;
                    }}
                QToolTip{{
                    color: {Color.WHITE.value}; /* Tooltip text color */
                    background-color: {Color.SELECTED_GRAY.value};
                    border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                    }}
                """)
        # Set line edit stylesheet based on editable state
        else:
            self.setStyleSheet(f"""
                QLineEdit{{
                    color: {Color.TEXT.value};
                    background-color: rgb(55, 65, 75);
                    border: 1px solid rgb(55, 65, 75);
                    selection-color: rgb(38, 38, 38);
                    selection-background-color: rgb(184, 177, 167);
                    padding-left: 1px;
                    }}
                QLineEdit:focus{{
                    background-color: rgb(73, 86, 99);
                    padding-left: 1px;
                    }}
                QLineEdit:hover{{
                    border: 1px solid {Color.BORDER.value};
                    padding-left: 1px;
                    }}
                QLineEdit:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    background-color: {Color.DISABLED_GRAY.value};
                    border: 1px solid {Color.DISABLED_GRAY.value};
                    padding-left: 1px;
                    }}
                QToolTip{{
                    color: {Color.WHITE.value}; /* Tooltip text color */
                    background-color: {Color.SELECTED_GRAY.value};
                    border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                    }}
                """)

    #-------------------------------------
    # [QT Event Handlers]
    #-------------------------------------

    def mousePressEvent(self, event):
        if self.read_only:
            self.clearFocus()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.read_only:
            event.ignore()
        else:
            super().mouseMoveEvent(event)

    def keyPressEvent(self, event):
        if not self.read_only:  # This allows typing when not read-only.
            super().keyPressEvent(event)
        else:
            pass

    def mouseDoubleClickEvent(self, event):
        if self.read_only:
            event.accept()
        else:
            super().mouseDoubleClickEvent(event)

    #-------------------------------------------
    # [For Alt+Click to show full text as Tooltip]
    #-------------------------------------------

    def eventFilter(self, obj, event):
        """
        Event Filter
        ============

        Filter events for PyFlameEntry. Used to show tooltip when Alt+Click.
        """

        if obj == self:
            if event.type() == QtCore.QEvent.Enter:
                self.mouse_inside = True
                if self.alt_pressed:
                    self._show_full_entry_text()
            elif event.type() == QtCore.QEvent.Leave:
                self.mouse_inside = False
                self._hide_full_entry_text()
            elif event.type() == QtCore.QEvent.KeyPress and event.key() == QtCore.Qt.Key_Alt:
                self.alt_pressed = True
                if self.mouse_inside:
                    self._show_full_entry_text()
                return True
            elif event.type() == QtCore.QEvent.KeyRelease and event.key() == QtCore.Qt.Key_Alt:
                self.alt_pressed = False
                self._hide_full_entry_text()
                return True
        return super().eventFilter(obj, event)

    def _show_full_entry_text(self):
        """
        Show Full Entry Text
        ====================

        Show full entry text as tooltip and copy full entry text to clipboard.
        """

        full_text = self.text()

        if full_text:
            if self.full_entry_text_label is None:
                self.full_entry_text_label = PyFlameLabel(
                    text=full_text,
                    parent=self.parent(),
                    )
                self.full_entry_text_label.setWindowFlags(QtCore.Qt.ToolTip)
                self.full_entry_text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

            self.full_entry_text_label.setText(full_text)
            self.full_entry_text_label.adjustSize()
            pos = self.mapToGlobal(self.rect().bottomLeft())
            self.full_entry_text_label.move(pos)
            self.full_entry_text_label.show()

            # Copy full entry text to clipboard
            pyflame.copy_to_clipboard(full_text)

    def _hide_full_entry_text(self):
        """
        Hide Full Entry Text
        ====================

        Hide and delete full entry text tooltip
        """

        if self.full_entry_text_label:
            self.full_entry_text_label.hide()
            self.full_entry_text_label.deleteLater()
            self.full_entry_text_label = None

    #-------------------------------------------
    # [For Tooltip - Private Methods]
    #-------------------------------------------

    def _create_tooltip_label(self, tooltip: str):
        """
        Create Tooltip Label
        ===================

        Create a PyFlameLabel for the tooltip.
        """

        self.tooltip_label = PyFlameLabel(
            text=tooltip,
            parent=self,
            )
        self.tooltip_label.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint)
        self.tooltip_label.hide()

        # Timers for delayed showing and auto-hiding
        self.show_timer = QtCore.QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._show_tooltip)

        self.hide_timer = QtCore.QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._hide_tooltip)

    def enterEvent(self, event):
        """
        Enter Event
        ===========

        Start the delay timer when cursor enters the button.
        """

        if self.tooltip:
            self.show_timer.start(self.tooltip_delay)  # Start delay

    def leaveEvent(self, event):
        """
        Leave Event
        ===========

        Stop the timer if the cursor leaves before tooltip is shown.
        """

        if self.tooltip:
            self.show_timer.stop()  # Prevent tooltip from showing
            self._hide_tooltip()  # Hide immediately if already visible

    def _show_tooltip(self):
        """
        Show Tooltip
        ============

        Show tooltip and set a timer to hide it after 5 seconds.
        """

        self.tooltip_label.setWindowFlags(QtCore.Qt.ToolTip)
        self.tooltip_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.tooltip_label.adjustSize()
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.tooltip_label.move(pos)
        self.tooltip_label.show()
        self.hide_timer.start(self.tooltip_duration)  # Hide after duration

    def _hide_tooltip(self):
        """
        Hide Tooltip
        ============

        Hide the tooltip and stop the hide timer.
        """

        self.tooltip_label.hide()
        self.hide_timer.stop()  # Ensure hiding process is controlled

class PyFlameEntryBrowser(QtWidgets.QLineEdit):
    """
    PyFlameEntryBrowser
    ===================

    Custom QT Flame LineEdit File Browser Widget Subclass

    Opens a Flame file browser when clicked on.

    Args:
    -----
        `text` (str):
            PyFlameEntryBrowser text.

        `width` (int, optional):
            PyFlameEntryBrowser width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameEntryBrowser height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameEntryBrowser to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `placeholder_text` (str, optional):
            Temporary text to display when PyFlameEntryBrowser is empty.
            (Default: `None`)

        `browser_type` (BrowserType):
            Type of browser to open. Select from BrowserType.FILE or BrowserType.DIRECTORY.
            (Default: `BrowserType.FILE`)

        `browser_ext` (list, optional):
            List of file extensions to filter by when browser_type is BrowserType.FILE. Ignore if browser_type is BrowserType.DIRECTORY.
            (Default: `[]`)

        `browser_title` (str):
            Title of browser window.
            (Default: `Select File`)

        `browser_window_to_hide` (QtWidgets.QWidget, optional):
            Window to hide when browser is open.
            (Default: `None`)

        `connect` (callable, optional):
            Function to call when text is changed.
            (Default: `None`)

    Attributes:
    -----------
        `path` (str):
            The selected file or directory path.

    Examples:
    ---------
        To create a PyFlameEntryBrowser:
        ```
        path_entry = PyFlameEntryBrowser(
            text=some_path,
            browser_type=BrowserType.FILE,
            browser_ext=[
                'exr',
                ],
            browser_title='Select Image',
            browser_window_to_hide=[self.window],
            )
        ```

        To get path from PyFlameEntryBrowser:
        ```
        path_entry.path
        ```

        To get path from PyFlameEntryBrowser:
        ```
        path_entry.text()
        ```

        To set path in PyFlameEntryBrowser:
        ```
        path_entry.setText('Some text here')
        ```

        To enable/disable PyFlameEntryBrowser:
        ```
        path_entry.setEnabled(True)
        path_entry.setEnabled(False)
        ```

        To set PyFlameEntryBrowser as focus (cursor will be in PyFlameEntryBrowser):
        ```
        path_entry.setFocus()
        ```
    """

    clicked = QtCore.Signal()

    def __init__(self: 'PyFlameEntryBrowser',
                 text: str,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 placeholder_text: Optional[str]=None,
                 browser_type: BrowserType=BrowserType.FILE,
                 browser_ext: List[str]=[],
                 browser_title: str='Select File',
                 browser_window_to_hide: Optional[QtWidgets.QWidget]=None,
                 connect: Optional[Callable[..., None]] = None,
                 ):
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'text', 'str', text)
            elif not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'width', 'int', width)
            elif not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'height', 'int', height)
            elif not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'max_width', 'int', max_width)
            elif placeholder_text is not None and not isinstance(placeholder_text, str):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'placeholder_text', 'str or None', placeholder_text)
            elif not isinstance(browser_type, BrowserType):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'browser_type', 'BrowserType Enum(BrowserType.FILE or BrowserType.DIRECTORY)', browser_type)
            elif not isinstance(browser_ext, list):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'browser_ext', 'list', browser_ext)
            elif not isinstance(browser_title, str):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'browser_title', 'str', browser_title)
            elif browser_window_to_hide is not None and not isinstance(browser_window_to_hide, list):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'browser_window_to_hide', 'list or None', browser_window_to_hide)
            elif connect is not None and not callable(connect):
                pyflame.raise_type_error(f'PyFlameEntryBrowser', 'connect', 'callable function or method, or None', connect)

        validate_arguments()

        # Set Browser Settings
        self.setFont(FONT)
        self.setText(text)
        self.path = self.text()
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set Browser Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Set placeholder text if specified
        if placeholder_text is not None:
            self.setPlaceholderText(placeholder_text)

        # If browser title is not specified, set it based on browser type
        if browser_title == '':
            if browser_type == BrowserType.FILE:
                browser_title = 'Select File'
            elif browser_type == BrowserType.DIRECTORY:
                browser_title = 'Select Directory'

        # Set browser select directory based on browser type
        if browser_type == BrowserType.FILE:
            browser_select_directory = False
        elif browser_type == BrowserType.DIRECTORY:
            browser_select_directory = True

        def open_file_browser():
            """
            Open File Browser
            =================

            Open flame file browser to select file or directory.
            """

            new_path = pyflame.file_browser(
                path=self.text(),
                title=browser_title,
                extension=browser_ext,
                select_directory=browser_select_directory,
                window_to_hide=browser_window_to_hide,
                )

            if new_path:
                self.setText(new_path)
                self.path = new_path

        self.clicked.connect(open_file_browser)

        # Connect to function if one is specified
        if connect:
            self.clicked.connect(connect)

        self._set_stylesheet()

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlameEntryBrowser stylesheet.
        """

        self.setStyleSheet(f"""
            QLineEdit{{
                color: {Color.TEXT.value};
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: 1px solid rgb(55, 65, 75);
                padding-left: 5px;
            }}
            QLineEdit:focus{{
                background-color: rgb(73, 86, 99);
            }}
            QLineEdit:hover{{
                border: 1px solid {Color.BORDER.value};
            }}
            QLineEdit:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: {Color.DISABLED_GRAY.value};
                border: 1px solid {Color.DISABLED_GRAY.value};
            }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
        """)

    #-------------------------------------
    # [QT Event Handlers]
    #-------------------------------------

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.clicked.emit()
            return
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        pass

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key_Left, QtCore.Qt.Key_Right):
            super().keyPressEvent(event)
        else:
            pass

class PyFlameLabel(QtWidgets.QLabel):
    """
    PyFlameLabel
    ============

    Custom QT Flame Label Widget Subclass

    Args:
    -----
        `text` (str):
            PyFlameLabel text.

        `style` (Style, optional):
            Select from different styles. See Style Options below.
            (Default: `Style.NORMAL`)

        `align` (Align, optional):
            Align text to left, right, or center. Overrides LabelStyle alignment. If set to None, Style alignment will be used.
            See Align Options below.
            (Default: `None`)

        `width` (int, optional):
            PyFlameLabel width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameLabel height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameLabel to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `max_height` (bool, optional):
            Set PyFlameLabel to maximum height. Use if height is being set by layout. Overrides `height` if set to True.
            (Default: `False`)

        `underline_color` (Color, optional):
            Color of text underline when using `Style.UNDERLINE`.
            Tuple must contain 4 values rgba(Red, Green, Blue, Alpha).
            The fourth value (alpha) is a float number between 0 and 1.
            (Default: `Color.TEXT_UNDERLINE.value`)

        `font_size` (int, optional):
            Set size of the font to be used for the text. If None, the default constant `FONT_SIZE` is used.
            (Default: `None`)

        `parent` (QtWidgets.QWidget, optional):
            Parent widget for the label. Use if label is being used as a tooltip.
            (Default: `None`)

    Style Options:
    --------------
        - `Style.NORMAL`: Standard Label without any additional styling. Text is left aligned.
        - `Style.UNDERLINE`: Underlines Label text. Text is centered.
        - `Style.BORDER`: Adds a white border around the Label with a dark background. Text is centered.
        - `Style.BACKGROUND`: Adds a darker background to the Label. Text is left aligned.
        - `Style.BACKGROUND_THIN`: Adds a darker background to the Label with a thinner font weight. Text is left aligned.

    Align Options:
    --------------
        - `None`: Uses the alignment defined by the style.
        - `Align.LEFT`: Aligns text to the left side of the Label.
        - `Align.RIGHT`: Aligns text to the right side of the Label.
        - `Align.CENTER`: Centers text within the Label.

    Examples:
    ---------
        To create a PyFlameLabel:
        ```
        label = PyFlameLabel(
            text='This is a label',
            style=Style.UNDERLINE,
            align=Align.LEFT,
            )
        ```

        To set PyFlameLabel text:
        ```
        label.setText('New Text')
        ```

        To enable/disable PyFlameLabel:
        ```
        label.setEnabled(True)
        label.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlameLabel',
                 text: str,
                 style: Style=Style.NORMAL,
                 align: Optional[Align]=None,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 max_height: bool=False,
                 underline_color: Color=Color.TEXT_UNDERLINE,
                 font_size: Optional[int]=None,
                 parent: Optional[QtWidgets.QWidget]=None,
                 ) -> None:
        super().__init__(parent)

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameLabel', 'text', 'string', text)
            if not isinstance(style, Style):
                pyflame.raise_type_error(f'PyFlameLabel', 'style', 'Style Enum', style)
            if align is not None and not isinstance(align, Align):
                pyflame.raise_type_error(f'PyFlameLabel', 'align', 'Align Enum or None', align)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameLabel', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameLabel', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameLabel', 'max_width', 'bool', max_width)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameLabel', 'max_height', 'bool', max_height)
            if not isinstance(underline_color, Color):
                pyflame.raise_type_error(f'PyFlameLabel', 'underline_color', 'Color Enum', underline_color)
            if font_size is not None and not isinstance(font_size, int):
                pyflame.raise_type_error(f'PyFlameLabel', 'font_size', 'int or None', font_size)
            if parent is not None and not isinstance(parent, QtWidgets.QWidget):
                pyflame.raise_type_error(f'PyFlameLabel', 'parent', 'QWidget or None', parent)

        validate_arguments()

        # Set Label Parent
        if parent is not None:
            self.setParent(parent)

        # Set Label Settings
        self.setFont(FONT)
        # Change font size if font_size is provided
        if font_size:
            font = self.font()
            font.setPointSize(pyflame.font_resize(font_size))
            self.setFont(font)
        self.setText(text)
        self.underline_color = underline_color
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set Label Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Set Label Stylesheet Based on Style and Align Arguments
        if align == Align.LEFT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        elif align == Align.RIGHT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        elif align == Align.CENTER:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        else:  # If align is None
            if style == Style.NORMAL or style == Style.BACKGROUND or style == Style.BACKGROUND_THIN:
                self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            else:  # UNDERLINE or BORDER
                self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

        self._set_stylesheet(style)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self, style: Style) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the widget stylesheet.

        The stylesheet has four predefined style options: NORMAL, UNDERLINE, and BORDER.

        Args:
        -----
            `style` (Style):
                The style to set for the label. This should be an instance of the `Style` enum,
                which defines the available styles.

        Raises:
        -------
            ValueError:
                If the provided `style` is not a supported style option.

        Example:
        --------
            Set the label stylesheet:
            ```
            self._set_stylesheet(style)
            ```
        """

        # Set label style based on style enum
        if style == Style.NORMAL:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value}; /* Label text color */
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    }}
                """)
        elif style == Style.UNDERLINE:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value}; /* Label text color */
                    border-bottom: 1px inset {self.underline_color.value}; /* Underline color */
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    }}
                """)
        elif style == Style.BORDER:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value}; /* Label text color */
                    border: 1px solid rgb{Color.TEXT_BORDER.value}; /* Label border */
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    }}
                """)
        elif style == Style.BACKGROUND:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    }}
                """)
        elif style == Style.BACKGROUND_THIN:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    font-weight: 100;
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value}; /* Disabled text color */
                    }}
                """)

class PyFlameLineEdit(PyFlameEntry):
    """
    PyFlameLineEdit
    ===============

    **DEPRECATED**

    Custom QT Flame LineEdit Widget Subclass. This class is deprecated and will be removed in future versions.
    Please use `PyFlameEntry` instead.
    """

    def __init__(self: 'PyFlameLineEdit',
                 text: str,
                 width: int = 150,
                 height: int = 28,
                 max_width: bool = False,
                 text_changed: Optional[Callable] = None,
                 placeholder_text: Optional[str] = None,
                 tooltip: Optional[str] = None,
                 read_only: bool = False,
                 ) -> None:

        # Issue a deprecation warning
        pyflame.print('*** PyFlameLineEdit: Deprecated. Use PyFlameEntry instead. ***', text_color=TextColor.RED)

        # Call the parent class (PyFlameEntry) __init__ method
        super().__init__(
            text=text,
            width=width,
            height=height,
            max_width=max_width,
            text_changed=text_changed,
            placeholder_text=placeholder_text,
            tooltip=tooltip,
            read_only=read_only,
            )

class PyFlameLineEditFileBrowser(PyFlameEntryBrowser):
    """
    PyFlameLineEditFileBrowser
    ==========================

    **DEPRECATED**

    Use `PyFlameEntryBrowser` instead.
    """

    clicked = QtCore.Signal()

    def __init__(self: 'PyFlameLineEditFileBrowser',
                 text: str,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 placeholder_text: Optional[str]=None,
                 browser_type: BrowserType=BrowserType.FILE,
                 browser_ext: List[str]=[],
                 browser_title: str='Select File',
                 browser_window_to_hide: Optional[QtWidgets.QWidget]=None,
                 connect: Optional[Callable[..., None]] = None,
                 ):

        # Issue a deprecation warning
        pyflame.print('*** PyFlameLineEditFileBrowser: Deprecated. Use PyFlameEntryBrowser instead. ***', text_color=TextColor.RED)

        super().__init__(
            text=text,
            width=width,
            height=height,
            max_width=max_width,
            placeholder_text=placeholder_text,
            browser_type=browser_type,
            browser_ext=browser_ext,
            browser_title=browser_title,
            browser_window_to_hide=browser_window_to_hide,
            connect=connect,
            )

class PyFlameListWidget(QtWidgets.QListWidget):
    """
    PyFlameListWidget
    =================

    Custom QT Flame List Widget Subclass

    Args:
    -----
        `items` (List[str], optional):
            List of items to be added to the list widget.
            (Default: `[]`)

        `width` (int, optional):
            PyFlameListWidget width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameListWidget height.
            (Default: `50`)

        `max_width` (bool, optional):
            Set PyFlameListWidget to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `max_height` (bool, optional):
            Set PyFlameListWidget to maximum height. Use if height is being set by layout. Overrides `height` if set to True.
            (Default: `True`)

    Methods:
    --------
        `add_items(items: List[str])`:
            Add a list of strings to the list widget.

    Examples:
    ---------
        To create PyFlameListWidget:
        ```
        list_widget = PyFlameListWidget(
            items=[
                'item1',
                'item2',
                'item3',
                ],
            )
        ```

        To add items to PyFlameListWidget:
        ```
        list_widget.add_items([
            'item1',
            'item2',
            'item3',
            ])
        ```

        To enable/disable PyFlameListWidget:
        ```
        list_widget.setEnabled(True)
        list_widget.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlameListWidget',
                 items: List[str]=[],
                 width: int=50,
                 height: int=50,
                 max_width: bool=True,
                 max_height: bool=True,
                 tooltip: Optional[str]=None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(items, list):
                pyflame.raise_type_error(f'PyFlameListWidget', 'items', 'list', items)
            if not all(isinstance(item, str) for item in items):
                pyflame.raise_type_error(f'PyFlameListWidget', 'items', 'list of strings', items)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameListWidget', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameListWidget', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameListWidget', 'max_width', 'bool', max_width)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameListWidget', 'max_height', 'bool', max_height)
            if tooltip is not None and not isinstance(tooltip, str):
                pyflame.raise_type_error(f'PyFlameListWidget', 'tooltip', 'str or None', tooltip)

        validate_arguments()

        # Set List Widget Settings
        self.setFont(FONT)
        self.setUniformItemSizes(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setToolTip(tooltip)
        self.add_items(items)

        # Set List Widget Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))
        if max_height:
            self.setMaximumHeight(pyflame.gui_resize(3000))

        # Set List Widget Stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_items(self, items: List[str]) -> None:
        """
        Add Items
        =========

            Add a list of strings to PyFlameListWidget.

            Args:
            -----
                `items` (List[str]):
                    The list of strings to be added.

            Raises:
            -------
                TypeError:
                    If `items` is not a list.
                    If `items` is not a list of strings.

            Example:
            --------
                ```
                list_widget.add_items([
                    'item1',
                    'item2',
                    'item3',
                ])
                ```
            """

        # Validate argument type
        if not isinstance(items, list):
            raise TypeError('PyFlameListWidget: items must be a list.')
        if not all(isinstance(item, str) for item in items):
            raise TypeError('PyFlameListWidget: All items must be strings.')

        # Add items to list widget
        self.addItems(items)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlameListWidget stylesheet.

        Example:
        --------
            ```
            self._set_stylesheet()
            ```
        """

        self.setStyleSheet(f"""
            QListWidget{{
                color: {Color.TEXT.value};
                background-color: {Color.ITEM_BACKGROUND_COLOR.value};
                alternate-background-color: {Color.ITEM_ALT_BACKGROUND_COLOR.value};
                outline: 3px {Color.BLACK.value};
                border: 1px solid rgba(0, 0, 0, .2);
                }}
            QListWidget::item{{
                padding-top: {pyflame.gui_resize(5)}px;  /* Increase top padding */
                padding-bottom: {pyflame.gui_resize(5)}px;  /* Increase bottom padding */
                }}
            QListWidget::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.SELECTED_GRAY.value};
                }}
            QScrollBar::handle{{
                background: {Color.GRAY.value};  /* Scrollbar handle color */
                }}
            QScrollBar:vertical{{
                width: {pyflame.gui_resize(8)}px;  /* Adjust the width of the vertical scrollbar */
                }}
            QScrollBar:horizontal{{
                height: {pyflame.gui_resize(8)}px;  /* Adjust the height of the horizontal scrollbar */
                }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
            """)

class PyFlamePushButton(QtWidgets.QPushButton):
    """
    PyFlamePushButton
    =================

    Custom QT Flame Push Button Widget Subclass

    Args:
    -----
        `text` (str):
            PyFlamePushButton text.

        `button_checked` (bool, optional):
            Set PyFlamePushButton to be checked or unchecked. True for checked, False for unchecked.
            (Default: `False`)

        `connect` (callable, optional):
            Function to be called when PyFlamePushButton is pressed.
            (Default: `None`)

        `width` (int, optional):
            PyFlamePushButton width.
            (Default: `50`)

        `height` (int, optional):
            PyFlamePushButton height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlamePushButton to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `enabled` (bool, optional):
            Set PyFlamePushButton to be enabled or disbaled. True for enabled, False for disabled.
            (Default: `True`)

        `tooltip` (str, optional):
            PyFlamePushButton tooltip text.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Tooltip delay in seconds. Delay before tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Tooltip duration in seconds. Duration tooltip is shown.
            (Default: `5`)

    Examples:
    ---------
        To create a PyFlamePushButton:
        ```
        pushbutton = PyFlamePushButton(
            text='Button Name',
            button_checked=False,
            )
        ```

        To get the checked state of the button:
        ```
        pushbutton.isChecked()
        ```

        To set the checked state of the button:
        ```
        pushbutton.setChecked(True)
        ```

        To enable/disable the button:
        ```
        pushbutton.setEnabled(True)
        pushbutton.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlamePushButton',
                 text: str,
                 button_checked: bool=False,
                 connect: Optional[Callable[..., None]]=None,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 enabled: bool=True,
                 tooltip: Optional[str]=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlamePushButton', 'text', 'str', text)
            if not isinstance(button_checked, bool):
                pyflame.raise_type_error(f'PyFlamePushButton', 'button_checked', 'bool', button_checked)
            if connect is not None and not callable(connect):
                pyflame.raise_type_error(f'PyFlamePushButton', 'connect', 'callable', connect)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlamePushButton', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlamePushButton', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlamePushButton', 'max_width', 'bool', max_width)
            if not isinstance(enabled, bool):
                pyflame.raise_type_error(f'PyFlamePushButton', 'enabled', 'bool', enabled)
            if tooltip is not None and not isinstance(tooltip, str):
                pyflame.raise_type_error(f'PyFlamePushButton', 'tooltip', 'str or None', tooltip)

        validate_arguments()

        # Push Button Settings
        self.setFont(FONT)
        self.setText(text)
        self.setCheckable(True)
        self.setChecked(button_checked)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(connect)
        self.setEnabled(enabled)
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay * 1000
        self.tooltip_duration = tooltip_duration * 1000

        # Set Push Button Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Create Tooltip using PyFlameLabel
        if self.tooltip:
            self._create_tooltip_label(tooltip)

        # Set Push Button Stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the widget stylesheet.

        Example:
        --------
            ```
            self._set_stylesheet()
            ```
        """

        self.setStyleSheet(f"""
            QPushButton{{
                color: {Color.TEXT.value};
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE.value});
                text-align: left;
                border-top: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE.value});
                border-bottom: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE.value});
                border-left: 1px solid {Color.GRAY.value};
                border-right: 1px solid {Color.PUSHBUTTON_BLUE.value};
                padding-left: {pyflame.gui_resize(5)}px;
                }}
            QPushButton:checked{{
                color: {Color.TEXT_SELECTED.value};
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.SELECTED_GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE_CHECKED.value});
                text-align: {Align.LEFT.value};
                border-top: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.SELECTED_GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE_CHECKED.value});
                border-bottom: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.SELECTED_GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE_CHECKED.value});
                border-left: 1px solid {Color.SELECTED_GRAY.value};
                border-right: 1px solid {Color.PUSHBUTTON_BLUE_CHECKED.value};
                padding-left: {pyflame.gui_resize(5)}px;
                font: italic;
                }}
            QPushButton:hover{{
                border: 1px solid {Color.BORDER.value};
                }}
            QPushButton:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: .93 {Color.GRAY.value}, stop: .94 {Color.PUSHBUTTON_BLUE_DISABLED.value});
                font: light;
                border: none;
                }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
            """)

    #-------------------------------------------
    # [For Tooltip - Private Methods]
    #-------------------------------------------

    def _create_tooltip_label(self, tooltip: str):
        """
        Create Tooltip Label
        ===================

        Create a PyFlameLabel for the tooltip.
        """

        self.tooltip_label = PyFlameLabel(
            text=tooltip,
            parent=self,
            )
        self.tooltip_label.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint)
        self.tooltip_label.hide()

        # Timers for delayed showing and auto-hiding
        self.show_timer = QtCore.QTimer()
        self.show_timer.setSingleShot(True)
        self.show_timer.timeout.connect(self._show_tooltip)

        self.hide_timer = QtCore.QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._hide_tooltip)

    def enterEvent(self, event):
        """
        Enter Event
        ===========

        Start the delay timer when cursor enters the button.
        """

        if self.tooltip:
            self.show_timer.start(self.tooltip_delay)  # Start delay

    def leaveEvent(self, event):
        """
        Leave Event
        ===========

        Stop the timer if the cursor leaves before tooltip is shown.
        """

        if self.tooltip:
            self.show_timer.stop()  # Prevent tooltip from showing
            self._hide_tooltip()  # Hide immediately if already visible

    def _show_tooltip(self):
        """
        Show Tooltip
        ============

        Show tooltip and set a timer to hide it after 5 seconds.
        """

        self.tooltip_label.setWindowFlags(QtCore.Qt.ToolTip)
        self.tooltip_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

        self.tooltip_label.adjustSize()
        pos = self.mapToGlobal(self.rect().bottomLeft())
        self.tooltip_label.move(pos)
        self.tooltip_label.show()
        self.hide_timer.start(self.tooltip_duration)  # Hide after duration

    def _hide_tooltip(self):
        """
        Hide Tooltip
        ============

        Hide the tooltip and stop the hide timer.
        """

        self.tooltip_label.hide()
        self.hide_timer.stop()  # Ensure hiding process is controlled

class PyFlamePushButtonMenu(QtWidgets.QPushButton):
    """
    PyFlamePushButtonMenu
    =====================

    Custom QT Flame Menu Push Button Widget Subclass

    Args:
    -----
        `text` (str):
            PyFlamePushButtonMenu text.

        `align` (str, optional):
            Set PyFlamePushButtonMenu text alignment. See `Align` options below.
            (Default: `Align.LEFT`)

        `menu_options` (list):
            Options shown in menu when the PyFlamePushButtonMenu is pressed.
            (Default: `[]`)

        `width` (int, optional):
            PyFlamePushButtonMenu width.
            (Default: `50`)

        `height` (int, optional):
            PyFlamePushButtonMenu height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlamePushButtonMenu to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `connect` (callable, optional):
            Function to be called when PyFlamePushButtonMenu is changed.
            (Default: `None`)

        `menu_indicator` (bool, optional):
            Show menu indicator arrow.
            (Default: `False`)

    Align Options:
    --------------
        - `Align.LEFT`: Aligns text to the left side of the Push Button Menu.
        - `Align.RIGHT`: Aligns text to the right side of the Push Button Menu.
        - `Align.CENTER`: Centers text within the Push Button Menu.

    Methods:
    --------
        `update_menu(text, menu_options, connect)`:
            Use to update an existing button menu.

    Examples:
    ---------
        To create a PyFlamePushButtonMenu:
        ```
        menu_push_button = PyFlamePushButtonMenu(
            text='push_button_name',
            menu_options=[
                'Item 1',
                'Item 2',
                'Item 3',
                'Item 4'
                ],
            align=Align.LEFT,
            )
        ```

        To get current PyFlamePushButtonMenu selection:
        ```
        menu_push_button.text()
        ```

        To update an existing PyFlamePushButtonMenu:
        ```
        menu_push_button.update_menu(
            text='Current Menu Selection',
            menu_options=[
                'Item 5',
                'Item 6',
                'Item 7',
                'Item 8'
                ],
            )
        ```
    """

    def __init__(self: 'PyFlamePushButtonMenu',
                 text: str,
                 align: Align=Align.LEFT,
                 menu_options: List[str]=[],
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 connect: Optional[Callable[..., None]]=None,
                 enabled: bool=True,
                 menu_indicator: bool=False,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'text', 'str', text)
            if not isinstance(align, Align):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'align', 'Align', align)
            if not isinstance(menu_options, list):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'menu_options', 'list', menu_options)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'max_width', 'bool', max_width)
            if connect is not None and not callable(connect):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'connect', 'callable', connect)
            if not isinstance(enabled, bool):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'enabled', 'bool', enabled)
            if not isinstance(menu_indicator, bool):
                pyflame.raise_type_error(f'PyFlamePushButtonMenu', 'menu_indicator', 'bool', menu_indicator)

        validate_arguments()

        # Set Button Settings
        self.setFont(FONT)
        self.setText(text)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.align = align

        # Set Button Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Create Menu
        self.pushbutton_menu = QtWidgets.QMenu(self)
        self.pushbutton_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushbutton_menu.aboutToShow.connect(self._match_push_button_width) # Match menu width to button width
        self.pushbutton_menu.setMinimumWidth(pyflame.gui_resize(width))

        # Add Menu Options
        for menu in menu_options:
            new_menu = self.pushbutton_menu.addAction(menu, partial(self._create_menu, menu, connect))
            new_menu.setFont(FONT)

        self.setMenu(self.pushbutton_menu)

        # Set Button Enabled/Disabled
        self.setEnabled(enabled)

        # Set Button Stylesheets
        self._set_button_stylesheet(menu_indicator)
        self._set_menu_stylesheet()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def update_menu(self, text: str, menu_options: List[str], connect: Optional[Callable[..., None]]=None) -> None:
        """
        Update Menu
        ===========

        This method is used to update an existing PyFlamePushButtonMenu menu.

        Args:
        -----
            `text` (str):
                Set PyFlamePushButtonMenu text.

            `menu_options` (List[str]):
                The list of menu options to be added to the PyFlamePushButtonMenu menu.

            `connect` (callable, optional):
                Function to be called when PyFlamePushButtonMenu is changed.
                (Default: `None`)

        Raises:
        -------
            TypeError:
                If `text` is not a string.
                If `menu_options` is not a list.
                If `menu_options` is not a list of strings
                If `connect` is not None or a callable function or method.

        Example:
        --------
            ```
            menu_push_button.update_menu(
                text='Current Menu Selection',
                menu_options=[
                    new_option1,
                    new_option2,
                    new_option3
                    ],
                )
            ```
        """

        # Validate argument types
        if not isinstance(text, str):
            raise TypeError(f'PyFlamePushButtonMenu: Invalid text argument: {text}. Must be of type str.')
        elif not isinstance(menu_options, list):
            raise TypeError(f'PyFlamePushButtonMenu: Invalid menu_options argument: {menu_options}. Must be of type list.')
        elif not all(isinstance(menu, str) for menu in menu_options):
            raise TypeError(f'PyFlamePushButtonMenu: All menu_options must be strings.')
        elif connect is not None and not callable(connect):
            raise TypeError(f'PyFlamePushButtonMenu: Invalid connect argument: {connect}. Must be a callable function or method, or None.')

        # Set button text
        self.set_text(' ' + text) # Add space to text to create padding. Space is removed when text is returned.

        # Clear existing menu options
        self.pushbutton_menu.clear()

        # Add new menu options
        for menu in menu_options:
            new_menu = self.pushbutton_menu.addAction(menu, partial(self._create_menu, menu, connect))
            new_menu.setFont(FONT)  # Apply font to action

    def set_text(self, text: str) -> None:
        """
        Set Text
        ========

        Public method that sets the button's text with a space added to the beginning to create padding.

        This method is an alias for setText. Alias is used to maintain consistency with other PyFlame widgets.

        Args:
        -----
            `text` (str):
                Set PyFlamePushButtonMenu text.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Example:
        --------
        ```
        push_button.set_text('Button Name')
        ```
        """

        # Validate argument types
        if not isinstance(text, str):
            raise TypeError(f'PyFlamePushButtonMenu: Invalid text argument: {text}. Must be of type str.')

        # Set text using setText
        self.setText(text)

    def text(self) -> str:
        """
        Text
        ====

        Returns the PyFlamePushButtonMenu's text with the first character (space that is added to button text) removed.

        Returns:
        --------
            str:
                The PyFlamePushButtonMenu text without the first character.

        Example:
        --------
            ```
            menu_push_button.text()
            ```
        """

        # Get current text
        current_text = super().text()

        # Return text without first character
        return current_text[1:] if current_text else ''

    def setText(self, text: str) -> None:
        """
        Set Text
        ========

        Public method that sets the button's text with a space added to the beginning to create padding.

        Note:
        -----
        This method is retained for backwards compatibility. The new method to use is `set_text`.

        Args:
        -----
            `text` (str):
                Set PyFlamePushButtonMenu text.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Example:
        --------
        ```
        push_button.setText('Button Name')
        ```
        """

        # Validate argument types
        if not isinstance(text, str):
            raise TypeError(f'PyFlamePushButtonMenu: Invalid text argument: {text}. Must be of type str.')

        # Strip leading and trailing whitespace
        text = text.strip()

        # Set button text
        super().setText(' ' + text)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_button_stylesheet(self, menu_indicator) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the widget stylesheet, optionally including a menu indicator.

        This private method updates the button's appearance by applying a stylesheet
        that includes styles for various states such as normal, disabled, and hover.
        It also optionally includes a menu indicator based on the `menu_indicator` parameter.

        Args:
        -----
            `menu_indicator (bool)`:
                If True, includes a menu indicator in the PyFlamePushButtonMenu stylesheet. False, hides the menu indicator.

        Raises:
        -------
            TypeError:
                If `menu_indicator` is not a bool.

        Example:
        --------
            ```
            button._set_button_stylesheet(menu_indicator)
            ```
        """

        # Validate argument types
        if not isinstance(menu_indicator, bool):
            pyflame.raise_type_error(f'PyFlamePushButtonMenu._set_button_stylesheet', 'menu_indicator', 'bool', menu_indicator)

        # Set menu indicator to show or hide
        if menu_indicator:
            menu_indicator_style = f"""
            QPushButton::menu-indicator{{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: {pyflame.gui_resize(15)}px;
                height: {pyflame.gui_resize(15)}px;
                right: {pyflame.gui_resize(10)}px;
            }}
            """
        else:
            menu_indicator_style = f"""
            QPushButton::menu-indicator{{
                image: none;
            }}"""

        self.setStyleSheet(f"""
            QPushButton{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                border: none;
                text-align: {self.align.value};
                padding-left: {pyflame.gui_resize(2)}px;
                }}
            QPushButton:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: rgb(45, 55, 68);
                border: none;
                }}
            QPushButton:hover{{
                border: 1px solid {Color.BORDER.value};
                padding-left: {pyflame.gui_resize(1)}px;
                }}
            QToolTip{{
                color: {Color.WHITE.value};
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value};
                }}
                {menu_indicator_style} # Insert menu indicator style
            """)

    def _set_menu_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlamePushButtonMenu stylesheet.

        Example:
        --------
            ```
            self._set_menu_stylesheet()
            ```
        """

        self.pushbutton_menu.setStyleSheet(f"""
            QMenu{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                border: none;
                font: {FONT_SIZE}px "{FONT}";
                }}
            QMenu::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: rgb(58, 69, 81);
                }}
            """)

    def _match_push_button_width(self):

        self.pushbutton_menu.setMinimumWidth(self.size().width())

    def _create_menu(self, menu, connect):

        self.setText(' ' + menu) # Add space to text to create padding. Space is removed when text is returned.

        # Add connect to menu
        if connect:
            connect()

class PyFlameColorPushButtonMenu(QtWidgets.QPushButton):
    """
    PyFlameColorPushButtonMenu
    ==========================

    Custom QT Flame Color Push Button Menu Widget Subclass

    Args:
    -----
        `color` (str):
            Name of the color to set.

        `menu_options` (list):
            Options shown in menu when PyFlameColorPushButtonMenu is pressed.

        `width` (int, optional):
            PyFlameColorPushButtonMenu width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameColorPushButtonMenu height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameColorPushButtonMenu to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `color_options` (dict, optional):
            Color options and their normalized RGBA values. Values must be in the range of 0.0 to 1.0.
            When None is passed, the default color options are used.
            (Default: `None`)

        `menu_indicator` (bool, optional):
            Show menu indicator arrow.
            (Default: `False`)

    Default Color Options:
    ----------------------
        'No Color': (0.0, 0.0, 0.0, 0.0)
        'Red': (0.310, 0.078, 0.078, 1.0)
        'Green': (0.125, 0.224, 0.165, 1.0)
        'Bright Green': (0.118, 0.396, 0.196, 1.0)
        'Blue': (0.176, 0.227, 0.322, 1.0)
        'Light Blue': (0.227, 0.325, 0.396, 1.0)
        'Purple': (0.318, 0.263, 0.424, 1.0)
        'Orange': (0.467, 0.290, 0.161, 1.0)
        'Gold': (0.380, 0.380, 0.235, 1.0)
        'Yellow': (0.592, 0.592, 0.180, 1.0)
        'Grey': (0.537, 0.537, 0.537, 1.0)
        'Black': (0.0, 0.0, 0.0, 1.0)

    Methods:
    --------

        `get_color()`:
            Return selected color name.

        `get_color_value()`:
            Return normalized RGB color value of selected color.

        `set_color(color: str)`:
            Set the color of the PyFlameColorPushButtonMenu.

    Examples:
    ---------
        To create a PyFlameColorPushButtonMenu:
        ```
        color_pushbutton = PyFlameColorPushButtonMenu(
            color='Red',
            )
        ```

        To get selected color value:
        ```
        color_value = color_pushbutton.get_color_value()
        ```

        To get selected color name:
        ```
        color_name = color_pushbutton.get_color()
        ```

        To set the color of the PyFlameColorPushButtonMenu:
        ```
        color_pushbutton.set_color('Red')
        ```
    """

    def __init__(self,
                 color: str,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 color_options: Optional[Dict[str, Tuple[float, float, float]]]=None,
                 menu_indicator: bool=False,
                 ) -> None:
        super().__init__()

        # Initialize with default color options if None
        if color_options is None:
            color_options = {
                'No Color': (0.0, 0.0, 0.0, 0.0),
                'Red': (0.310, 0.078, 0.078, 1.0),
                'Green': (0.125, 0.224, 0.165, 1.0),
                'Bright Green': (0.118, 0.396, 0.196, 1.0),
                'Blue': (0.176, 0.227, 0.322, 1.0),
                'Light Blue': (0.227, 0.325, 0.396, 1.0),
                'Purple': (0.318, 0.263, 0.424, 1.0),
                'Orange': (0.467, 0.290, 0.161, 1.0),
                'Gold': (0.380, 0.380, 0.235, 1.0),
                'Yellow': (0.592, 0.592, 0.180, 1.0),
                'Grey': (0.537, 0.537, 0.537, 1.0),
                'Black': (0.0, 0.0, 0.0, 1.0),
                }

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(color, str):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'color', 'str', color)
            if color not in color_options:
                pyflame.raise_type_error(error_message=f'PyFlameColorPushButtonMenu: "{color}" is not a valid color option. {color} must be one of the following: {color_options.keys()}')
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'max_width', 'bool', max_width)
            if color_options is None and not isinstance(color_options, dict):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'color_options', 'dict', color_options)
            if not isinstance(menu_indicator, bool):
                pyflame.raise_type_error(f'PyFlameColorPushButtonMenu', 'menu_indicator', 'bool', menu_indicator)

        validate_arguments()

        # Set PyFlameColorPushButtonMenu Settings
        self.setFont(FONT)
        self.setText(color)
        self.color_options = color_options # Color options and their RGB values
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set PyFlameColorPushButtonMenu Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Create Menu
        self.pushbutton_menu = QtWidgets.QMenu(self)
        self.pushbutton_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushbutton_menu.setMinimumWidth(width)
        self.pushbutton_menu.setFont(FONT)

        # Set initial color
        self.set_color(color)

        # Add color menu options
        for color_name, color_value in self.color_options.items():
            icon = self._generate_color_icon(color_value)
            action = QAction(icon, color_name, self)
            action.triggered.connect(partial(self._create_menu, color_name))
            action.setFont(FONT)
            self.pushbutton_menu.addAction(action)
        self.setMenu(self.pushbutton_menu)

        # Set Stylesheets
        self._set_button_stylesheet(menu_indicator)
        self._set_menu_stylesheet()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def get_color(self) -> str:
        """
        Get Color
        =========

        Get name of selected color.

        Returns:
        --------
            str:
                The name of the currently selected color.

        Example:
        --------
            Get the name of the currently selected color:
            ```
            color_name = button.get_color()
            ```
        """

        return self.text()

    def get_color_value(self) -> Tuple[float, float, float, float]:
        """
        Get Color Value
        ===============

        Retrieves the RGBA color value corresponding to the currently selected color.
        The color value is returned as a tuple of four floats.

        Returns:
        --------
            Tuple[float, float, float, float]:
                The current selected color RGBA value.

        Example:
        --------
            Get the RGBA color value of the PyFlameColorPushButtonMenu's currently selected color:
            ```
            color_value = button.get_color_value()
            ```
        """

        return self.color_options[self.text()]

    def set_color(self, color: str) -> None:
        """
        Set Color
        =========

        Updates the button text and icon to reflect the selected color.

        Args:
        -----
            `color (str)`:
                The name of the color to set.

        Raises:
        -------
            ValueError: If `color` is not in `color_options`.

        Example:
        --------
            Set the color of the PyFlameColorPushButtonMenu to 'Red':
            ```
            button.set_color('Red')
            ```
        """

        if color not in self.color_options:
            pyflame.raise_value_error(error_message=f'PyFlameColorPushButtonMenu: "{color}" is not a valid color option. {color} must be one of the following: {self.color_options.keys()}')

        # Update button text
        self.setText(color)

        # Update button icon
        icon = self._generate_color_icon(self.color_options[color])
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(FONT_SIZE, FONT_SIZE))

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _generate_color_icon(self, color_value: Tuple[float, float, float, float]) -> QtGui.QIcon:
        """
        Generate Color Icon
        ===================

        This private method generates a color icon based on the given color value.
        The size of the icon is based on the widget font size.

        Args:
        -----
            `color_value` (Tuple[float, float, float]):
                The RGB color value, where each float is between 0 and 1.

        Returns:
        --------
            QtGui.QIcon:
                The generated color icon.

        Raises:
        -------
            TypeError:
                If `color_value` is not a tuple.
            ValueError:
                If `color_value` does not contain exactly three float values between 0 and 1.

        Example:
        --------
            Generate an icon for the color red:
            ```
            red_icon = widget._generate_color_icon((1.0, 0.0, 0.0))
            ```
        """

        # Validate argument types
        if not isinstance(color_value, tuple):
            raise TypeError(f'_generate_color_icon: Invalid type for color_value: {type(color_value)}. Must be a tuple.')
        if len(color_value) != 4 or not all(isinstance(c, float) and 0 <= c <= 1 for c in color_value):
           raise ValueError(f'_generate_color_icon: Invalid value for color_value: {color_value}. Must be a tuple of three floats between 0 and 1.')

        # Create the pixmap and fill with the given color
        pixmap = QtGui.QPixmap(FONT_SIZE, FONT_SIZE)  # Size of the color square
        pixmap.fill(QtGui.QColor(*[int(c * 255) for c in color_value]))  # Convert color values to 0-255 range
        return QtGui.QIcon(pixmap)

    def _create_menu(self, color_name) -> None:
        """
        Create Menu
        ===========

        This private method updates the button's text and icon to reflect the selected color.

        Args:
        -----
            `color_name (str)`:
                The name of the color to set for the button.

        Raises:
        -------
            TypeError:
                If `color_name` is not a string.
            ValueError:
                If `color_name` does not correspond to any available color option.

        Example:
        --------
            Update the button to reflect the color 'red':
            ```
            button._create_menu('red')
            ```
        """

        # Validate argument types
        if not isinstance(color_name, str):
            raise TypeError(f'_create_menu: Invalid type for color_name: {type(color_name)}. Must be a string.')
        if color_name not in self.color_options:
            raise ValueError(f'_create_menu: Invalid color_name: "{color_name}". Must be one of the available color options.')

        # Update the button's text and icon
        self.setText(color_name)
        icon = self._generate_color_icon(self.color_options[color_name])
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(FONT_SIZE, FONT_SIZE))

    def _set_button_stylesheet(self, menu_indicator) -> None:
        """
        Set Button Stylesheet
        =====================

        This private method sets the PyFlameColorPushButtonMenu stylesheet.
        """

        # Set menu indicator style
        if menu_indicator:
            menu_indicator_style =f"""
            QPushButton::menu-indicator{{
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: {pyflame.gui_resize(15)}px;
                height: {pyflame.gui_resize(15)}px;
                right: {pyflame.gui_resize(10)}px;
            }}
            """
        else:
            # Hide the menu indicator by setting its image to none
            menu_indicator_style = """
            QPushButton::menu-indicator{
                image: none;
                }"""

        self.setStyleSheet(f"""
            QPushButton{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                border: none;
                text-align: left;
                left: {pyflame.gui_resize(10)}px;
                }}
            QPushButton:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: rgb(45, 55, 68);
                border: none;
                }}
            QPushButton:hover{{
                border: 1px solid {Color.BORDER.value};
                }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
            {menu_indicator_style} # Insert menu indicator style
            """)

    def _set_menu_stylesheet(self) -> None:
        """
        Set Menu Stylesheet
        ===================

        This private method sets the PyFlameColorPushButtonMenu menu stylesheet.
        """

        self.pushbutton_menu.setStyleSheet(f"""
            QMenu{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                text-align: center;
                border: none;
                font: {FONT_SIZE}px "{FONT}";
                }}
            QMenu::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: rgb(58, 69, 81);
                }}
            """)

class PyFlameSlider(QtWidgets.QLineEdit):
    """
    PyFlameSlider
    =============

    Custom QT Line Edit Widget Subclass

    Args:
    -----
        `start_value` (int or float):
            Initial value.

        `min_value` (int or float):
            Minimum value.

        `max_value` (int or float):
            Maximum value.

        `value_is_float` (bool, optional):
            If True, the value is float.
            (Default: `False`)

        `rate` (int or float, optional):
            Slider sensitivity. The value should be between 1 and 10. Lower values are more sensitive.
            (Default: `10`)

        `width` (int, optional):
            PyFlameSlider width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameSlider height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set PyFlameSlider to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `connect` (callable, optional):
            Function to call when value is changed.
            (Default: `None`)

        `tooltip` (str, optional):
            PyFlameSlider tooltip text.
            (Default: `None`)

    Methods:
    --------
        `get_value()`:
            Return the PyFlameSlider value as an integer or float.

    Examples:
    ---------
        To create a PyFlameSlider:
        ```
        slider = PyFlameSlider(
            start_value=0,
            min_value=-20,
            max_value=20,
            )
        ```

        To return the PyFlameSlider value as an integer or float:
        ```
        slider.get_value()
        ```

        To return the PyFlameSlider value as a string:
        ```
        slider.text()
        ```

        To enable/disable PyFlameSlider:
        ```
        slider.setEnabled(True)
        slider.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlameSlider',
                 start_value: int,
                 min_value: int,
                 max_value: int,
                 value_is_float: bool=False,
                 rate: Union[int, float]=10,
                 width: int=50,
                 height: int=28,
                 max_width: bool=True,
                 connect=None,
                 tooltip: Optional[str]=None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(start_value, (int, float)):
                pyflame.raise_type_error(f'PyFlameSlider', 'start_value', 'int or float', start_value)
            if not isinstance(min_value, (int, float)):
                pyflame.raise_type_error(f'PyFlameSlider', 'min_value', 'int or float', min_value)
            if not isinstance(max_value, (int, float)):
                pyflame.raise_type_error(f'PyFlameSlider', 'max_value', 'int or float', max_value)
            if not isinstance(value_is_float, bool):
                pyflame.raise_type_error(f'PyFlameSlider', 'value_is_float', 'bool', value_is_float)
            if not isinstance(rate, (int, float)) or rate < 1 or rate > 10:
                pyflame.raise_type_error(f'PyFlameSlider', 'rate', 'int or float between 1 and 10', rate)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameSlider', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameSlider', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameSlider', 'max_width', 'bool', max_width)
            if connect is not None and not callable(connect):
                pyflame.raise_type_error(f'PyFlameSlider', 'connect', 'callable', connect)
            if tooltip is not None and not isinstance(tooltip, str):
                pyflame.raise_type_error(f'PyFlameSlider', 'tooltip', 'str', tooltip)

        validate_arguments()

        # Set Slider Font
        self.font = FONT
        #self.font.setPointSize(pyflame.font_resize(FONT_SIZE + 2))
        self.setFont(self.font)

        # Set Slider Size
        self.width = pyflame.gui_resize(width)
        self.height = pyflame.gui_resize(height)
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))
        else:
            self.setMinimumWidth(self.width)
            self.setMaximumWidth(self.width)

        # Build Slider
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumHeight(self.height)

        if value_is_float:
            self.spinbox_type = 'Float'
        else:
            self.spinbox_type = 'Integer'

        self.rate = rate *.1
        self.min = min_value
        self.max = max_value
        self.steps = 1
        self.value_at_press = None
        self.pos_at_press = None
        self.setValue(start_value)
        self.setReadOnly(True)
        self.textChanged.connect(self.value_changed)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setToolTip(tooltip)

        self._set_stylesheet()

        self.clearFocus()

        class Slider(QtWidgets.QSlider):

            def __init__(self, start_value, min_value, max_value, width):
                super(Slider, self).__init__()

                self.setMaximumHeight(pyflame.gui_resize(4))
                self.setMinimum(min_value)
                self.setMaximum(max_value)
                self.setValue(start_value)
                self.setOrientation(QtCore.Qt.Horizontal)

                # Slider stylesheet

                self.setStyleSheet(f"""
                    QSlider{{
                        color: rgb(55, 65, 75);
                        background-color: rgb(39, 45, 53);
                        }}
                    QSlider::groove{{
                        color: rgb(39, 45, 53);
                        background-color: rgb(39, 45, 53);
                        }}
                    QSlider::handle:horizontal{{
                        background-color: rgb(102, 102, 102);
                        width: {pyflame.gui_resize(3)}px;
                        }}
                    QSlider::disabled{{
                        color: {Color.TEXT_DISABLED.value};
                        background-color: rgb(55, 65, 75);
                        }}
                    """)

                self.setDisabled(True)
                self.raise_()

        def set_slider():
            slider666.setValue(float(self.text()))
            slider666.setFont(self.font)

        slider666 = Slider(start_value, min_value, max_value, pyflame.gui_resize(width))
        self.textChanged.connect(set_slider)

        self.textChanged.connect(connect) # Connect to function when slider value is changed

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(slider666)
        self.vbox.setContentsMargins(0, pyflame.gui_resize(24), 0, 0)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:

        # Slider stylesheet
        self.setStyleSheet(f"""
            QLineEdit{{
                color: {Color.TEXT.value};
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: none;
                padding-left: 5px;
                }}
            QLineEdit:hover{{
                border: 1px solid {Color.BORDER.value};
                }}
            QLineEdit:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: rgb(55, 65, 75);
                }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
            """)

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def get_value(self):
        """
        Returns the slider's current value as an int or float.

        If the slider's value is of type 'Integer', this method will return the value as an int.
        Otherwise, the value will be returned as a float.

        Returns:
            Union[int, float]:
                The current slider value.
        """
        if self.spinbox_type == 'Integer':
            return int(self.text())
        else:
            return float(self.text())

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _calculator(self):

        def clear():
            calc_entry.setText('')

        def button_press(key):

            if self.clean_line == True:
                calc_entry.setText('')

            calc_entry.insert(key)

            self.clean_line = False

        def plus_minus():

            if calc_entry.text():
                calc_entry.setText(str(float(calc_entry.text()) * -1))

        def add_sub(key):

            if calc_entry.text() == '':
                calc_entry.setText('0')

            if '**' not in calc_entry.text():
                try:
                    calc_num = eval(calc_entry.text().lstrip('0'))

                    calc_entry.setText(str(calc_num))

                    calc_num = float(calc_entry.text())

                    if calc_num == 0:
                        calc_num = 1
                    if key == 'add':
                        self.setValue(float(self.text()) + float(calc_num))
                    else:
                        self.setValue(float(self.text()) - float(calc_num))

                    self.clean_line = True
                except:
                    pass

        def enter():

            if self.clean_line == True:
                return calc_window.close()

            if calc_entry.text():
                try:

                    # If only single number set slider value to that number

                    self.setValue(float(calc_entry.text()))
                except:

                    # Do math

                    new_value = calculate_entry()
                    self.setValue(float(new_value))

            close_calc()

        def equals():

            if calc_entry.text() == '':
                calc_entry.setText('0')

            if calc_entry.text() != '0':

                calc_line = calc_entry.text().lstrip('0')
            else:
                calc_line = calc_entry.text()

            if '**' not in calc_entry.text():
                try:
                    calc = eval(calc_line)
                except:
                    calc = 0

                calc_entry.setText(str(calc))
            else:
                calc_entry.setText('1')

        def calculate_entry():

            calc_line = calc_entry.text().lstrip('0')

            if '**' not in calc_entry.text():
                try:
                    if calc_line.startswith('+'):
                        calc = float(self.text()) + eval(calc_line[-1:])
                    elif calc_line.startswith('-'):
                        calc = float(self.text()) - eval(calc_line[-1:])
                    elif calc_line.startswith('*'):
                        calc = float(self.text()) * eval(calc_line[-1:])
                    elif calc_line.startswith('/'):
                        calc = float(self.text()) / eval(calc_line[-1:])
                    else:
                        calc = eval(calc_line)
                except:
                    calc = 0
            else:
                calc = 1

            calc_entry.setText(str(float(calc)))

            return calc

        def close_calc():

            calc_window.close()

            self.setStyleSheet(f"""
                QLineEdit{{
                    color: {Color.TEXT.value};
                    background-color: rgb(55, 65, 75);
                    selection-color: {Color.TEXT.value};
                    selection-background-color: rgb(55, 65, 75);
                    border: none;
                    padding-left: 5px;
                    }}
                QLineEdit:hover{{
                    border: 1px solid {Color.BORDER.value};
                    }}
                """)

        def calc_null():

            # Does nothing

            pass

        self.clean_line = False

        calc_window = PyFlameDialogWindow(
            title='Calculator',
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=30,
            return_pressed=enter,
            )
        calc_window.move(QtGui.QCursor.pos().x() - 110, QtGui.QCursor.pos().y() - 290)
        calc_window.setWindowFlags(calc_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        calc_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Label
        calc_label = PyFlameLabel('Calculator')

        # Entry
        calc_entry = PyFlameEntry(
            text='',
            )
        calc_entry.returnPressed.connect(enter)

        regex = QRegularExpression('[0-9_,=,/,*,+,\-,.]+')
        validator = QValidator(regex)
        calc_entry.setValidator(validator)

        #-------------------------------------

        # Buttons
        blank_button = PyFlameButton(
            text='',
            connect=calc_null,
            width=40,
            )
        blank_button.setDisabled(True)

        plus_minus_button = PyFlameButton(
            text='+/-',
            connect=plus_minus,
            width=40,
            )
        plus_minus_button.setStyleSheet(f"""
            color: {Color.TEXT.value};
            background-color: rgb(45, 55, 68);
        """)

        add_button = PyFlameButton(
            text='Add',
            connect=(partial(add_sub, 'add')),
            width=40,
            )
        sub_button = PyFlameButton(
            text='Sub',
            connect=(partial(add_sub, 'sub')),
            width=40,
            )

        #-------------------------------------

        clear_button = PyFlameButton(
            text='C',
            connect=clear,
            width=40,
            )
        equal_button = PyFlameButton(
            text='=',
            connect=equals,
            width=40,
            )
        div_button = PyFlameButton(
            text='/',
            connect=(partial(button_press, '/')),
            width=40,
            )
        mult_button = PyFlameButton(
            text='*',
            connect=(partial(button_press, '*')),
            width=40,
            )

        #-------------------------------------

        _7_button = PyFlameButton(
            text='7',
            connect=(partial(button_press, '7')),
            width=40,
            )
        _8_button = PyFlameButton(
            text='8',
            connect=(partial(button_press, '8')),
            width=40,
            )
        _9_button = PyFlameButton(
            text='9',
            connect=(partial(button_press, '9')),
            width=40,
            )
        minus_button = PyFlameButton(
            text='-',
            connect=(partial(button_press, '-')),
            width=40,
            )

        #-------------------------------------

        _4_button = PyFlameButton(
            text='4',
            connect=(partial(button_press, '4')),
            width=40,
            )
        _5_button = PyFlameButton(
            text='5',
            connect=(partial(button_press, '5')),
            width=40,
            )
        _6_button = PyFlameButton(
            text='6',
            connect=(partial(button_press, '6')),
            width=40,
            )
        plus_button = PyFlameButton(
            text='+',
            connect=(partial(button_press, '+')),
            width=40,
            )

        #-------------------------------------

        _1_button = PyFlameButton(
            text='1',
            connect=(partial(button_press, '1')),
            width=40,
            )
        _2_button = PyFlameButton(
            text='2',
            connect=(partial(button_press, '2')),
            width=40,
            )
        _3_button = PyFlameButton(
            text='3',
            connect=(partial(button_press, '3')),
            width=40,
            )
        enter_button = PyFlameButton(
            text='Enter',
            connect=enter,
            max_height=True,
            width=40,
            )

        #-------------------------------------

        _0_button = PyFlameButton(
            text='0',
            connect=(partial(button_press, '0')),
            width=40,
            )
        point_button = PyFlameButton(
            text='.',
            connect=(partial(button_press, '.')),
            width=40,
            )

        #-------------------------------------

        calc_window.grid_layout.addWidget(calc_entry, 0, 0, 1, 4)

        calc_window.grid_layout.addWidget(blank_button, 1, 0)
        calc_window.grid_layout.addWidget(plus_minus_button, 1, 1)
        calc_window.grid_layout.addWidget(add_button, 1, 2)
        calc_window.grid_layout.addWidget(sub_button, 1, 3)

        calc_window.grid_layout.addWidget(clear_button, 2, 0)
        calc_window.grid_layout.addWidget(equal_button, 2, 1)
        calc_window.grid_layout.addWidget(div_button, 2, 2)
        calc_window.grid_layout.addWidget(mult_button, 2, 3)

        calc_window.grid_layout.addWidget(_7_button, 3, 0)
        calc_window.grid_layout.addWidget(_8_button, 3, 1)
        calc_window.grid_layout.addWidget(_9_button, 3, 2)
        calc_window.grid_layout.addWidget(minus_button, 3, 3)

        calc_window.grid_layout.addWidget(_4_button, 4, 0)
        calc_window.grid_layout.addWidget(_5_button, 4, 1)
        calc_window.grid_layout.addWidget(_6_button, 4, 2)
        calc_window.grid_layout.addWidget(plus_button, 4, 3)

        calc_window.grid_layout.addWidget(_1_button, 5, 0)
        calc_window.grid_layout.addWidget(_2_button, 5, 1)
        calc_window.grid_layout.addWidget(_3_button, 5, 2)
        calc_window.grid_layout.addWidget(enter_button, 5, 3, 2, 1)

        calc_window.grid_layout.addWidget(_0_button, 6, 0, 1, 2)
        calc_window.grid_layout.addWidget(point_button, 6, 2)

    def value_changed(self):

        # If value is greater or less than min/max values set values to min/max

        if int(self.value()) < self.min:
            self.setText(str(self.min))
        if int(self.value()) > self.max:
            self.setText(str(self.max))

    def mousePressEvent(self, event):

        if event.buttons() == QtCore.Qt.LeftButton:
            self.value_at_press = self.value()
            self.pos_at_press = event.pos()
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.setFont(self.font)
            self.setStyleSheet(f"""
                QLineEdit{{
                    color: {Color.TEXT_SELECTED.value};
                    background-color: rgb(73, 86, 99);
                    selection-color: {Color.TEXT.value};
                    selection-background-color: rgb(73, 86, 99);
                    border: none; padding-left: 5px;
                    }}
                QLineEdit:hover{{
                    border: 1px solid {Color.BORDER.value};
                    }}
                """)

    def mouseReleaseEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:

            # Open calculator if button is released within 10 pixels of button click

            if event.pos().x() in range((self.pos_at_press.x() - 10), (self.pos_at_press.x() + 10)) and event.pos().y() in range((self.pos_at_press.y() - 10), (self.pos_at_press.y() + 10)):
                self._calculator()
            else:
                self.setStyleSheet(f"""
                    QLineEdit{{
                        color: {Color.TEXT.value};
                        background-color: rgb(55, 65, 75);
                        selection-color: {Color.TEXT.value};
                        selection-background-color: rgb(55, 65, 75);
                        border: none;
                        padding-left: 5px;
                        }}
                    QLineEdit:hover{{
                        border: 1px solid {Color.BORDER.value};
                        }}
                    """)

            self.value_at_press = None
            self.pos_at_press = None
            self.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
            return

        super(PyFlameSlider, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):

        if event.buttons() != QtCore.Qt.LeftButton:
            return

        if self.pos_at_press is None:
            return

        steps_mult = self.getStepsMultiplier(event)
        delta = event.pos().x() - self.pos_at_press.x()

        if self.spinbox_type == 'Integer':
            delta /= 10 * self.rate # Make movement less sensiteve.
        else:
            delta /= 100 * self.rate
        delta *= self.steps * steps_mult

        value = self.value_at_press + delta
        self.setValue(value)

        super(PyFlameSlider, self).mouseMoveEvent(event)

    def getStepsMultiplier(self, event):

        steps_mult = 1

        if event.modifiers() == QtCore.Qt.CTRL:
            steps_mult = 10
        elif event.modifiers() == QtCore.Qt.SHIFT:
            steps_mult = 0.10

        return steps_mult

    def setMinimum(self, value):

        self.min = value

    def setMaximum(self, value):

        self.max = value

    def setSteps(self, steps):

        if self.spinbox_type == 'Integer':
            self.steps = max(steps, 1)
        else:
            self.steps = steps

    def value(self):

        if self.spinbox_type == 'Integer':
            return int(self.text())
        else:
            return float(self.text())

    def setValue(self, value):

        if self.min is not None:
            value = max(value, self.min)

        if self.max is not None:
            value = min(value, self.max)

        if self.spinbox_type == 'Integer':
            self.setText(str(int(value)))
        else:
            # Keep float values to two decimal places

            self.setText('%.2f' % float(value))

class PyFlameTable(QtWidgets.QTableView):
    """
    PyFlameTable
    ============

    Custom QT Table Widget Subclass

    Not compatible with PySide2.

    Args:
    -----
        `csv_file_path` (str, optional):
            The path to the CSV file to load.
            (Default: `None`)

    Methods:
    --------
        `load_csv(csv_file_path: str) -> None`:
            Load CSV file into the table.

        `save_csv_file(csv_file_path: str) -> None`:
            Save the CSV file to the given path.

    Examples:
    ---------
        ```
        table = PyFlameTable()
        table.load_csv('path/to/csv/file.csv')
        table.save_csv_file('path/to/csv/file.csv')
        ```
    """

    def __init__(self: 'PyFlameTable', csv_file_path: str=None) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate arguments, raise TypeError if any arguments are invalid.
            """

            if csv_file_path is not None and not isinstance(csv_file_path, str):
                pyflame.raise_type_error(f'PyFlameTable', 'csv_file_path', 'string or None', csv_file_path)

        validate_arguments()

        self.setFont(FONT)
        self.horizontalHeader().setFont(FONT)
        self.verticalHeader().setFont(FONT)

        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectItems)  # Allow individual cell selection
        self.setSelectionMode(QtWidgets.QTableView.ExtendedSelection)  # Allow multi-cell selection
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Configure headers
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.horizontalHeader().sectionDoubleClicked.connect(self._rename_column_header)

        self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)

        self.verticalHeader().customContextMenuRequested.connect(self._show_row_menu)
        self.horizontalHeader().customContextMenuRequested.connect(self._show_column_menu)

        # Prevent selecting all column items when clicking on header
        self.horizontalHeader().mousePressEvent = self._block_column_selection

        # If a CSV file path is provided, load the CSV file
        if csv_file_path:
            self.load_csv(csv_file_path)

        # Set widgetstylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def load_csv(self, csv_file_path: str) -> None:
        """
        Load CSV
        ========

        Load CSV file into the table.

        Args:
        -----
            csv_file_path: str
                The path to the CSV file to load.

        Raises:
        -------
            TypeError:
                If `csv_file_path` is not a string.

        Example:
        --------
            ```
            table = PyFlameTable()
            table.load_csv('path/to/csv/file.csv')
            ```
        """

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate arguments, raise TypeError if any arguments are invalid.
            """

            if not isinstance(csv_file_path, str):
                pyflame.raise_type_error(f'PyFlameTable.load_csv', 'csv_file_path', 'string', csv_file_path)

        validate_arguments()

        self.model.clear()
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)

            if data:
                self.model.setColumnCount(len(data[0]))
                self.model.setHorizontalHeaderLabels(data[0])

                for row in data[1:]:
                    items = [QtGui.QStandardItem(cell) for cell in row]
                    self.model.appendRow(items)

    def save_csv_file(self, csv_file_path: str) -> None:
        """
        Save CSV File
        =============

        Save the CSV file to the given path.

        Args:
        -----
            csv_file_path: str
                The path to save the CSV file to.

        Raises:
        -------
            TypeError:
                If `csv_file_path` is not a string.

        Example:
        --------
            ```
            table = PyFlameTable()
            table.save_csv_file('path/to/csv/file.csv')
            ```
        """

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate arguments, raise TypeError if any arguments are invalid.
            """

            if not isinstance(csv_file_path, str):
                pyflame.raise_type_error(f'PyFlameTable.save_csv_file', 'csv_file_path', 'string', csv_file_path)

        validate_arguments()

        # Open file for writing
        with open(csv_file_path, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)

            # Write headers
            headers = [self.model.headerData(col, QtCore.Qt.Horizontal) for col in range(self.model.columnCount())]
            writer.writerow(headers)

            # Write rows
            for row in range(self.model.rowCount()):
                row_data = [self.model.item(row, col).text() if self.model.item(row, col) else "" for col in range(self.model.columnCount())]
                writer.writerow(row_data)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _rename_column_header(self, index: int) -> None:
        """
        Rename Column Header
        ====================

        Rename a column header when double-clicked.

        Args:
        -----
            index: int
                The index of the column header to rename.
        """

        if not isinstance(index, int):
            pyflame.raise_type_error(f'PyFlameTable._rename_column_header', 'index', 'int', index)

        # Get current header text
        current_header_text = self.model.headerData(index, QtCore.Qt.Horizontal)

        # Open input dialog to get new value
        rename_column_header_dialog = PyFlameInputDialog(
            text=f'New Column Header Name\n\nCurrent Header Name: {current_header_text}',
            input_text=current_header_text,
            title='Rename Column Header',
            )

        new_text, ok = rename_column_header_dialog.get_text()

        # If the user confirmed, rename the column header
        if new_text and ok:
            self.model.setHeaderData(index, QtCore.Qt.Horizontal, new_text, QtCore.Qt.DisplayRole)

    def _rename_selected_cells(self) -> None:
        """
        Rename Selected Cells
        =====================

        Rename all selected cells to a new value.
        """

        for index in self.selectionModel().selectedIndexes():
            item = self.model.itemFromIndex(index)

        # Open input dialog to get new value
        rename_selected_cells_dialog = PyFlameInputDialog(
            text='Enter New Value',
            input_text=item.text(),
            title='Rename Selected Cells',
            )

        new_text, ok = rename_selected_cells_dialog.get_text()

        # If the user confirmed, rename the selected cells
        if new_text and ok:
            for index in self.selectionModel().selectedIndexes():
                item = self.model.itemFromIndex(index)
                if item:
                    item.setText(new_text)

    def _show_row_menu(self, position: tuple) -> None:
        """
        Show Right-Click Menu for Rows
        ==============================

        Show right-click menu for rows.

        Args:
        -----
            position: tuple
                The position of the mouse in the table view.
        """

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(self._set_menu_stylesheet())

        add_row_action = QtGui.QAction("Add Row", self)
        add_row_action.triggered.connect(self._add_row)
        add_row_action.setFont(FONT)

        delete_row_action = QtGui.QAction("Delete Row", self)
        delete_row_action.triggered.connect(self._delete_selected_rows)
        delete_row_action.setFont(FONT)

        menu.addAction(add_row_action)
        menu.addAction(delete_row_action)

        menu.exec(self.verticalHeader().mapToGlobal(position))

    def _show_column_menu(self, position: tuple) -> None:
        """
        Show Right-Click Menu for Columns
        =================================

        Show right-click menu for columns.

        Args:
        -----
            position: tuple
                The position of the mouse in the table view.
        """

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(self._set_menu_stylesheet())

        add_column_action = QtGui.QAction("Add Column", self)
        add_column_action.triggered.connect(self._add_column)
        add_column_action.setFont(FONT)

        delete_column_action = QtGui.QAction("Delete Column", self)
        delete_column_action.triggered.connect(self._delete_selected_columns)
        delete_column_action.setFont(FONT)

        rename_header_action = QtGui.QAction("Rename Column Header", self)
        logical_index = self.horizontalHeader().logicalIndexAt(position)
        rename_header_action.triggered.connect(lambda: self._rename_column_header(logical_index))
        rename_header_action.setFont(FONT)

        menu.addAction(add_column_action)
        menu.addAction(delete_column_action)
        menu.addAction(rename_header_action)

        menu.exec(self.horizontalHeader().mapToGlobal(position))

    def _add_row(self) -> None:
        """
        Add Row
        =======

        Add a new row after the selected row, or at the end if no row is selected.
        """

        selected_rows = sorted(set(index.row() for index in self.selectionModel().selectedRows()))
        insert_row = selected_rows[-1] + 1 if selected_rows else self.model.rowCount()
        self.model.insertRow(insert_row)

    def _delete_selected_rows(self) -> None:
        """
        Delete Selected Rows
        ===================

        Delete selected rows.
        """

        selected_indexes = self.selectionModel().selectedRows()
        for index in sorted(selected_indexes, key=lambda x: x.row(), reverse=True):
            self.model.removeRow(index.row())

    def _add_column(self) -> None:
        """
        Add Column
        ==========

        Add a new column after the selected column, or at the end if no column is selected.
        """

        selected_columns = sorted(set(index.column() for index in self.selectionModel().selectedColumns()))
        insert_column = selected_columns[-1] + 1 if selected_columns else self.model.columnCount()
        self.model.insertColumn(insert_column)

        # Set default header label
        self.model.setHeaderData(insert_column, QtCore.Qt.Horizontal, 'NEW COLUMN')

    def _delete_selected_columns(self) -> None:
        """
        Delete Selected Columns
        =======================

        Delete selected columns.
        """

        selected_indexes = self.selectionModel().selectedColumns()
        for index in sorted(selected_indexes, key=lambda x: x.column(), reverse=True):
            self.model.removeColumn(index.column())

    def _block_column_selection(self, event) -> None:
        """
        Block Column Selection
        ======================

        Prevents column selection when clicking on a header.
        """

        if event.button() == QtCore.Qt.LeftButton:
            index = self.horizontalHeader().logicalIndexAt(event.pos())
            if index != -1:
                return
        super(QtWidgets.QHeaderView, self.horizontalHeader()).mousePressEvent(event)

    #-------------------------------------
    # [Stylesheets - Private Methods]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        PyFlameTable stylesheet
        """

        self.setStyleSheet(f"""
            QTableView {{
                color: {Color.TEXT.value};
                background-color: {Color.ITEM_BACKGROUND_COLOR.value};
                alternate-background-color: {Color.ITEM_ALT_BACKGROUND_COLOR.value};
                gridline-color: rgba(25, 25, 25, .5);
                border: 1px solid rgba(25, 25, 25, .5);
                outline: none; /* Removes default focus outline */
                }}
            QTableView:focus {{
                outline: none;
                }}
            /* Removes cell borders to prevent extra lines */
            QTableView::item {{
                border: none;
                padding: 0px; /* Ensure no extra padding */
                margin: 0px;
                }}
            /* Cell when it is selected */
            QTableView::item:selected {{
                color: {Color.TEXT_SELECTED.value};
                background-color: {Color.SELECTED_GRAY.value};
                border: none; /* Ensures no borders on selected cells */
                }}
            /* Cell when it is being edited */
            QTableView QLineEdit {{
                color: {Color.TEXT.value}; /* Text color inside the editor */
                background-color: rgb(55, 65, 75); /* Background color when editing */
                selection-color: rgb(38, 38, 38); /* Text color when selected */
                selection-background-color: rgb(184, 177, 167); /* Selection background inside editor */
                border: none; /* Completely removes borders */
                margin: 0px;
                padding: 0px;
                }}

            QHeaderView::section {{
                background-color: {Color.ITEM_ALT_BACKGROUND_COLOR.value};
                color: {Color.TEXT.value};
                padding: {pyflame.gui_resize(4)}px;
                border: 1px solid rgb(25, 25, 25);
                }}
            QHeaderView::section:checked,
            QHeaderView::section:pressed {{
                background-color: rgb(50, 50, 50);
                color: {Color.TEXT_SELECTED.value};
                }}

            /* Context Menu (Right-Click Menu) */
            QMenu {{
                background-color: rgb(90, 90, 90);
                color: {Color.TEXT.value};
                border: 1px solid {Color.BLACK.value};
                padding: {pyflame.gui_resize(4)}px;
                }}
            /* Context Menu Items */
            QMenu::item {{
                padding: {pyflame.gui_resize(6)}px {pyflame.gui_resize(12)}px;
                background-color: transparent;
                }}
            /* Context Menu Item Hover */
            QMenu::item:selected {{
                background-color: {Color.SELECTED_GRAY.value};
                color: {Color.TEXT_SELECTED.value};
                }}

            QScrollBar::handle {{
                background: {Color.GRAY.value};  /* Scrollbar handle color */
                }}
            QScrollBar:vertical {{
                width: {pyflame.gui_resize(8)}px;  /* Adjust the width of the vertical scrollbar */
                }}
            QScrollBar:horizontal {{
                height: {pyflame.gui_resize(8)}px;  /* Adjust the height of the horizontal scrollbar */
                }}
            """)

    def _set_menu_stylesheet(self) -> None:
        """
        Set Menu Stylesheet
        ==================

        PyFlameTable menu stylesheet
        """

        return f"""
            QMenu {{
                background-color: rgb(44, 54, 68);  /* Menu background */
                color: rgb(170, 170, 170);  /* Text color */
                border: 1px solid rgb(35, 43, 54); /* Menu border */
                 }}
            QMenu::item {{
                background-color: transparent;  /* Default item background */
                color: rgb(170, 170, 170);  /* Item text color */
                padding: {pyflame.gui_resize(4)}px {pyflame.gui_resize(8)}px; /* Padding around menu items */
                }}
            QMenu::item:selected {{
                background-color: rgb(73, 86, 99);  /* Hovered item background */
                color: rgb(220, 220, 220);  /* Hovered item text color */
                }}
            QMenu::separator {{
                height: 1px;
                background: rgb(55, 68, 85);  /* Separator line */
                margin: {pyflame.gui_resize(3)}px {pyflame.gui_resize(2)}px;
                }}
            """

    #-------------------------------------
    # [QT Event Handlers]
    #-------------------------------------

    def contextMenuEvent(self, event) -> None:
        """
        Custom Context Menu on Right-Click for Table Body
        =================================================

        Custom context menu on right-click for table body.

        Args:
        -----
            event: PySide6.QtWidgets.QContextMenuEvent
                The context menu event.
        """

        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet(self._set_menu_stylesheet())

        rename_action = QtGui.QAction('Rename Selected Cells', self)
        rename_action.triggered.connect(self._rename_selected_cells)
        rename_action.setFont(FONT)
        menu.addAction(rename_action)

        menu.exec(event.globalPos())

class PyFlameTabWidget(QtWidgets.QTabWidget):
    """
    PyFlameTabWidget
    ================

    Custom QT Flame Tab Widget Subclass

    This tab widget uses PyFlameGridLayout for each tab's internal layout.

    Can be added to a PyFlameWindow or PyFlameDialogWindow.

    Args:
    -----
        tab_names (list[str]):
            Names of tabs to add.
            (Default: `[]`)

        columns (int):
            Number of columns for the tab layout.
            (Default: `4`, optional)

        rows (int):
            Number of rows for the tab layout.
            (Default: `3`, optional)

        column_width (int):
            Default width of each column.
            (Default: `150`, optional)

        row_height (int):
            Default height of each row.
            (Default: `28`, optional)

        adjust_column_widths (dict[int, int]):
            Optional column width overrides.
            (Default: `{}`, optional)

        adjust_row_heights (dict[int, int]):
            Optional row height overrides.
            (Default: `{}`, optional)

        tab_width (int):
            Width of each tab.
            (Default: `150`, optional)

        tab_height (int):
            Height of each tab.
            (Default: `28`, optional)

        parent (QtWidgets.QWidget, optional):
            Parent widget.
            (Default: `None`, optional)

    Methods:
    --------
        `add_tab(name: str) -> PyFlameTabWidget.TabContainer`:
            Add a tab to the tab widget.

    Examples:
    ---------
        To create a PyFlameTabWidget:
        ```
        tab_widget = PyFlameTabWidget(
            tab_names=[
                'Tab 1',
                'Tab 2',
                'Tab 3',
                ],
            grid_layout_columns=4,
            grid_layout_rows=10,
            )
        ```

        To add a widget to a tab:
        ```
        tab_widget.tab_pages['Tab 1'].grid_layout.addWidget(menu_label, 0, 0)
        ```

        To add the tab widget to a window:
        ```
        window.grid_layout.addWidget(tab_widget, 0, 0, 10, 10)
        ```

        To add a tab to an existing tab widget:
        ```
        tab_widget.add_tab('Tab 4')
        ```
    """

    class TabContainer:
        def __init__(self, name: str, parent_tab_widget: 'PyFlameTabWidget'):
            self.widget = QtWidgets.QWidget()

            # Inherit layout settings from parent tab widget
            self.grid_layout = PyFlameGridLayout(
                columns=parent_tab_widget.grid_layout_columns,
                rows=parent_tab_widget.grid_layout_rows,
                column_width=parent_tab_widget.grid_layout_column_width,
                row_height=parent_tab_widget.grid_layout_row_height,
                adjust_column_widths=parent_tab_widget.grid_layout_adjust_column_widths,
                adjust_row_heights=parent_tab_widget.grid_layout_adjust_row_heights,
                )

            self.widget.setLayout(self.grid_layout)
            parent_tab_widget.addTab(self.widget, name)

    def __init__(self,
                 tab_names: list[str],
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: Optional[dict[int, int]]=None,
                 grid_layout_adjust_row_heights: Optional[dict[int, int]]=None,
                 tab_width: int=150,
                 tab_height: int=28,
                 parent: Optional[QtWidgets.QWidget]=None):
        super().__init__(parent)

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            # Validate arguments
            if not isinstance(tab_names, list):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'tab_names', 'list', tab_names)
            for name in tab_names:
                if not isinstance(name, str):
                    pyflame.raise_type_error(f'PyFlameTabWidget', 'tab_names', 'list of strings', tab_names)
            if not isinstance(grid_layout_columns, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_columns', 'int', grid_layout_columns)
            if not isinstance(grid_layout_rows, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_rows', 'int', grid_layout_rows)
            if not isinstance(grid_layout_column_width, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_column_width', 'int', grid_layout_column_width)
            if not isinstance(grid_layout_row_height, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_row_height', 'int', grid_layout_row_height)
            if grid_layout_adjust_column_widths is not None and not isinstance(grid_layout_adjust_column_widths, dict):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_adjust_column_widths', 'dict or None', grid_layout_adjust_column_widths)
            if grid_layout_adjust_row_heights is not None and not isinstance(grid_layout_adjust_row_heights, dict):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'grid_layout_adjust_row_heights', 'dict or None', grid_layout_adjust_row_heights)
            if not isinstance(tab_width, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'tab_width', 'int', tab_width)
            if not isinstance(tab_height, int):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'tab_height', 'int', tab_height)
            if parent is not None and not isinstance(parent, QtWidgets.QWidget):
                pyflame.raise_type_error(f'PyFlameTabWidget', 'parent', 'QtWidgets.QWidget or None', parent)

        # Validate arguments
        validate_arguments()

        # Set tab settings
        self.setFont(FONT)
        self.tab_width = tab_width
        self.tab_height = tab_height

        # Disable tab focus
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Store layout config for use in each tab
        self.grid_layout_columns = grid_layout_columns
        self.grid_layout_rows = grid_layout_rows
        self.grid_layout_column_width = grid_layout_column_width
        self.grid_layout_row_height = grid_layout_row_height
        self.grid_layout_adjust_column_widths = grid_layout_adjust_column_widths or {}
        self.grid_layout_adjust_row_heights = grid_layout_adjust_row_heights or {}

        # Track tab containers
        self.tab_pages: dict[str, PyFlameTabWidget.TabContainer] = {}

        # Set stylesheet
        self._set_stylesheet()

        # Create tabs from tab_names
        for name in tab_names:
            self.add_tab(name)

    #-------------------------------------
    # [Public Methods]
    #-------------------------------------

    def add_tab(self, name: str) -> 'PyFlameTabWidget.TabContainer':
        """
        Add Tab
        =======

        Add a tab to the tab widget.

        Will not add a tab if a tab with the same name already exists.

        Args:
        -----
            name (str):
                The name of the tab to add.

        Returns:
        --------
            PyFlameTabWidget.TabContainer:
                The tab container object.
        """

        # Validate argument
        if not isinstance(name, str):
            pyflame.raise_type_error(f'PyFlameTabWidget', 'name', 'string', name)

        # Don't add it again if it already exists
        if name in self.tab_pages:
            return self.tab_pages[name]

        # Add tab
        container = self.TabContainer(name, self)
        self.tab_pages[name] = container
        return container

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============

        Sets tab stylesheet.
        """

        self.setStyleSheet(f"""
            QWidget{{
                background-color: rgb(36, 36, 36);
                }}
            QTabWidget{{
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::tab-bar{{
                alignment: center;
                }}
            QTabBar::tab{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                width: {self.tab_width}px;
                height: {self.tab_height}px;
                padding: {pyflame.gui_resize(5)}px;
                }}
            QTabBar::tab:selected{{
                color: rgb(200, 200, 200);
                background-color: rgb(31, 31, 31);
                border: 1px solid rgb(31, 31, 31);
                border-bottom: 1px solid {Color.BLUE.value};
                }}
            QTabBar::tab:!selected{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::pane{{
                border-top: 1px solid {Color.TAB_PANE.value};
                }}
            """)

class PyFlameTextEdit(QtWidgets.QTextEdit):
    """
    PyFlameTextEdit
    ===============

    Custom QT Flame Text Edit Widget Subclass

    Args:
    -----
        `text` (str):
            PyFlameTextEdit text.

        `text_type` (TextType, optional):
            Type of text being input.
            Options:
                `TextType.PLAIN`: Plain text.
                `TextType.MARKDOWN`: Markdown text.
                `TextType.HTML`: HTML text.
            (Default: `TextType.PLAIN`)

        `width` (int, optional):
            PyFlameTextEdit width.
            (Default: `50`)

        `height` (int, optional):
            PyFlameTextEdit height.
            (Default: `50`)

        `max_width` (bool, optional):
            Set PyFlameTextEdit to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `max_height` (bool, optional):
            Set PyFlameTextEdit to maximum height. Use if height is being set by layout. Overrides `height` if set to True.
            (Default: `True`)

        `read_only` (bool, optional):
            Text in PyFlameTextEdit is read only.
            (Default: `False`)

        `message_window` (bool, optional):
            If True, PyFlameTextEdit will be used in a PyFlameMessageWindow and will use a different stylesheet.
            (Default: `False`)

    Methods:
    --------
        `text()`:
            Returns PyFlameTextEdit text.

    Useful Inheritance:
    -------------------
        `setText(text)`:
            Set plain or html text.

        `setPlainText(text)`:
            Set plain text.

        `setMarkdown(text)`:
            Set Markdown text.

        `setHtml(text)`:
            Set HTML text.

        `toPlainText()`:
            Returns the text as plain text.

        `toMarkdown()`:
            Returns the text as Markdown.

        `toHtml()`:
            Returns the text as HTML.

        `setEnabled(bool)`:
            Enable(True) or disable(False) widget.

    Examples:
    ---------
        To create a PyFlameTextEdit:
        ```
        text_edit = PyFlameTextEdit(
            text='Some text here',
            read_only=True,
            )
        ```

        To set text in PyFlameTextEdit:
        ```
        text_edit.setText('Some text here')
        ```

        To enable/disable PyFlameTextEdit:
        ```
        text_edit.setEnabled(True)
        text_edit.setEnabled(False)
        ```
    """

    def __init__(self: 'PyFlameTextEdit',
                 text: str,
                 text_type: TextType=TextType.PLAIN,
                 width: int=50,
                 height: int=50,
                 max_width: Optional[bool]=True,
                 max_height: Optional[bool]=True,
                 read_only: bool=False,
                 message_window: bool=False,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'text', 'string', text)
            if not isinstance(text_type, TextType):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'text_type', 'TextType', text_type)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'max_width', 'bool', max_width)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'max_height', 'bool', max_height)
            if not isinstance(read_only, bool):
                pyflame.raise_type_error(f'PyFlameTextEdit', 'read_only', 'bool', read_only)

        validate_arguments()

        # Set TextEdit Settings
        self.setFont(FONT)
        self.setReadOnly(read_only)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        # Set TextEdit Text
        if text_type == TextType.PLAIN:
            self.setPlainText(text)
        elif text_type == TextType.MARKDOWN:
            self.setMarkdown(text)
        elif text_type == TextType.HTML:
            self.setHtml(text)

        # Set TextEdit Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(10000))
        if max_height:
            self.setMaximumHeight(pyflame.gui_resize(10000))

        # Set TextEdit Stylesheet
        if read_only:
            style_sheet_type = 'read_only'
        elif message_window:
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)
            style_sheet_type = 'message_window'
        else:
            style_sheet_type = 'default'

        self._set_stylesheet(style_sheet_type)

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def text(self) -> str:
        """
        Text
        ====

        Get text from PyFlameTextEdit.

        Returns:
        --------
            str: PyFlameTextEdit text.

        Example:
        --------
            To get text from PyFlameTextEdit:
            ```
            text = text_edit.text()
            ```
        """

        pyflame.print('Deprecated: PyFlameTextEdit.text() is deprecated. Use PyFlameTextEdit.toPlainText() instead.',
                      print_type=PrintType.WARNING)

        return self.toPlainText()

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self, style_sheet_type: str):
        """
        Set Text Edit Stylesheet
        ========================

        This private method sets the PyFlameTextEdit stylesheet.
        """

        if style_sheet_type == 'read_only':
            self.setStyleSheet(f"""
                QTextEdit{{
                    color: {Color.TEXT.value};
                    background-color: {Color.TEXT_READ_ONLY_BACKGROUND.value};
                    selection-color: rgb(38, 38, 38);
                    selection-background-color: rgb(184, 177, 167);
                    border: none;
                    padding-left: 1px;
                    }}
                QScrollBar::handle{{
                    background: {Color.SCROLLBAR_HANDLE.value};
                    }}
                QScrollBar:vertical{{
                    width: {pyflame.gui_resize(8)}px;  /* Adjust the width of the vertical scrollbar */
                    }}
                QScrollBar:horizontal{{
                    height: {pyflame.gui_resize(8)}px;  /* Adjust the height of the horizontal scrollbar */
                    }}
                """)

        elif style_sheet_type == 'message_window':
            self.setStyleSheet(f"""
                QTextEdit{{
                    color: {Color.TEXT.value};
                    border: none;
                    padding-left: 1px;
                    }}
                """)
        elif style_sheet_type == 'default':
            self.setStyleSheet(f"""
                QTextEdit{{
                    color: {Color.TEXT.value};
                    background-color: rgb(55, 65, 75);
                    selection-color: rgb(38, 38, 38);
                    selection-background-color: rgb(184, 177, 167);
                    border: none;
                    padding-left: 1px;
                    }}
                QTextEdit:hover{{
                    border: 1px solid {Color.BORDER.value};
                    padding-left: 1px;
                    }}
                QTextEdit:focus{{
                    background-color: rgb(73, 86, 99);
                    }}
                QScrollBar::handle{{
                    background: {Color.SCROLLBAR_HANDLE.value};
                    }}
                QScrollBar:vertical{{
                    width: {pyflame.gui_resize(8)}px;  /* Adjust the width of the vertical scrollbar */
                    }}
                QScrollBar:horizontal{{
                    height: {pyflame.gui_resize(8)}px;  /* Adjust the height of the horizontal scrollbar */
                    }}
                """)

class PyFlameTokenPushButton(QtWidgets.QPushButton):
    """
    PyFlameTokenPushButton
    ======================

    Custom QT Flame Token Push Button Widget Subclass

    When a token is chosen from the menu, it is inserted into the PyFlameEntry widget specified by token_dest.

    Args:
    -----
        `text` (str, optional):
            PyFlameTokenPushButton text.
            (Default: `Add Token`)

        `token_dict` (dict, optional):
            Dictionary defining tokens. {'Token Name': '<Token>'}.
            (Default: `{}`)

        `token_dest` (PyFlameEntry, optional):
            PyFlameEntry that token value will be applied to.
            (Default: `None`)

        `clear_dest` (bool, optional):
            Clear destination QLineEdit before inserting token.
            (Default: `False`)

        `width` (int, optional):
            Button width.
            (Default: `50`)

        `height` (int, optional):
            Button height.
            (Default: `28`)

        `max_width` (bool, optional):
            Set to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

    Methods:
    --------
        `add_menu_options(new_options)`:
            Clears existing menu and adds new menu options PyFlameTokenPushButton menu.

    Examples:
    ---------
        To create a PyFlameTokenPushButton:
        ```
        token_push_button = PyFlameTokenPushButton(
            token_dict={
                'Token 1': '<Token1>',
                'Token 2': '<Token2>',
                },
            token_dest=PyFlameEntry,
            clear_dest=True,
            )
        ```

        To enable/disable PyFlameTokenPushButton:
        ```
        token_push_button.setEnabled(True)
        token_push_button.setEnabled(False)
        ```

        To add new menu options to the existing token menu:
        ```
        token_push_button.add_menu_options(
            new_options={
                'New Token Name': '<New Token>',
                }
            )
        ```
    """

    def __init__(self: 'PyFlameTokenPushButton',
                 text: str='Add Token',
                 token_dict: Dict[str, str]={},
                 token_dest: Optional[PyFlameEntry]=None,
                 clear_dest: bool=False,
                 width: int=50,
                 height: int=28,
                 max_width: Optional[bool]=True,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'text', 'string', text)
            if not isinstance(token_dict, dict):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'token_dict', 'dict', token_dict)
            if not isinstance(token_dest, QtWidgets.QLineEdit):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'token_dest', 'QtWidgets.QLineEdit', token_dest)
            if not isinstance(clear_dest, bool):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'clear_dest', 'bool', clear_dest)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameTokenPushButton', 'max_width', 'bool', max_width)

        validate_arguments()

        # Set Token Push Button Settings
        self.setFont(FONT)
        self.setText(text)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set Token Push Button Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))

        # Create the token menu
        self.token_menu = QtWidgets.QMenu(self)
        self.token_menu.setFocusPolicy(QtCore.Qt.NoFocus)

        def token_action_menu():

            def insert_token(token):
                if clear_dest:
                    token_dest.setText('')
                for key, value in token_dict.items():
                    if key == token:
                        token_name = value
                        token_dest.insert(token_name)

            for key, value in token_dict.items():
                self.token_menu.addAction(key, partial(insert_token, key))

        # Set Token Push Button Menu
        token_action_menu()
        self.setMenu(self.token_menu)

        # Set Token Push Button Stylesheet
        self._set_stylesheet()
        self._set_menu_stylesheet()

        # Set Token Push Button Attributes
        self.token_dict = token_dict
        self.token_dest = token_dest
        self.clear_dest = clear_dest

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_menu_options(self, new_options: Dict[str, str]):
            """
            Add Menu Options
            ================

            Clears existing PyFlameTokenPushButton menu and creats new menu from `add_menu_options`.

            Args:
            -----
                `new_options` (dict):
                    Dictionary of new token options to add. The key is the name of the token to display in the menu, and the
                    value is the token to insert into the destination PyFlameLineEdit.

            Raises:
            -------
                TypeError:
                    If `new_options` is not a dictionary
                    If the dictionary does not contain strings as keys and values.

            Example:
            --------
                Add new options to PyFlameTokenPushButton menu:
                ```
                token_push_button.add_menu_options(
                    new_options={
                        'New Token Name': '<New Token>'
                        },
                    )
                ```
            """

            # Validate the argument type
            if not isinstance(new_options, dict):
                raise TypeError('add_menu_options: new_options must be a dictionary.')

            # Validate the contents of the dictionary
            for key, value in new_options.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise TypeError('add_menu_options: All keys and values in new_options must be strings.')

            def insert_new_token(token):
                """
                Insert New Token
                ================

                Insert the new token into the destination PyFlameEntry.

                Args:
                -----
                   `token` (str):
                        The token to insert into the destination PyFlameEntry.
                """

                if self.clear_dest:
                    self.token_dest.setText('')
                for key, value in self.token_dict.items():
                    if key == token:
                        token_name = value
                        self.token_dest.insert(token_name)

            # Clear existing token menu and dictionary
            self.token_menu.clear()
            self.token_dict.clear()

            # Add new menu options
            for key, value in new_options.items():
                self.token_dict[key] = value
                action = self.token_menu.addAction(key, partial(insert_new_token, key))
                action.setFont(FONT)  # Apply font to action

    #-------------------------------------
    # [Stylesheets - Private Methods]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlameTokenPushButton stylesheet.
        """

        self.setStyleSheet(f"""
            QPushButton{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                border: none;
                }}
            QPushButton:hover{{
                border: 1px solid {Color.BORDER.value};
                }}
            QPushButton:disabled{{
                color: {Color.TEXT_DISABLED.value};
                background-color: rgb(45, 55, 68);
                border: none;
                }}
            QPushButton::menu-indicator{{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: {pyflame.gui_resize(15)}px;
                height: {pyflame.gui_resize(15)}px;
                right: {pyflame.gui_resize(10)}px;
                }}
            QToolTip{{
                color: {Color.WHITE.value}; /* Tooltip text color */
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.BLACK.value}; /* Tooltip border color */
                }}
            """)

    def _set_menu_stylesheet(self):
        """
        Set Menu Stylesheet
        ===================

        This private method sets the PyFlameTokenPushButton menu stylesheet.
        """

        # Explicitly set the font for the menu

        self.token_menu.setStyleSheet(f"""
            QMenu{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 55, 68);
                border: none;
                font: {FONT_SIZE}px "{FONT}";
            }}
            QMenu::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: rgb(58, 69, 81);
            }}
        """)

class PyFlameTreeWidget(QtWidgets.QTreeWidget):
    """
    PyFlameTreeWidget
    =================

    Custom QT Flame Tree Widget Subclass

    Args:
    -----
        `column_names` (list[str]):
            List of names to be used for column names in tree.

        `connect` (callable, optional):
            Function to call when item in tree is clicked on.
            (Default: `None`)

        `width` (int, optional):
            Width of tree widget.
            (Default: `50`)

        `height` (int, optional):
            Height of tree widget.
            (Default: `50`)

        `max_width` (bool, optional):
            Set to maximum width. Use if width is being set by layout. Overrides `width` if set to True.
            (Default: `True`)

        `max_height` (bool, optional):
            Set to maximum height. Use if height is being set by layout. No need to set height if this is used.
            (Default: `True`)

        `tree_dict` (Dict[str, Dict[str, str]], optional):
            Dictionary of items to populate the tree widget. Useful when dealing with folder trees.
            (Default: `{}`)

        `tree_list` (List[str], optional):
            List of items to populate the tree widget. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            (Default: `[]`)

        `allow_children` (bool, optional):
            Whether to allow children in the tree.
            (Default: `True`)

        `sorting` (bool, optional):
            Whether to enable sorting in the tree widget.
            (Default: `False`)

        `min_items` (int, optional):
            Minimum number of items that must remain in the tree.
            (Default: `1`)

        `update_callback` (callable, optional):
            Function to call when an item is edited, inserted, or deleted.
            (Default: `None`)

    Methods:
    --------
        `fill_tree_dict(tree_dict: Dict[str, Dict[str, str]], editable: bool=False)`:
            Fill the PyFlameTreeWidget with the provided dictionary.

        `fill_tree_list(tree_list: List[str])`:
            Fill the PyFlameTreeWidget with the provided list.

        `add_item(item_name: str)`:
            Add a new item as a child of the currently selected item in the tree, or as a child of the top-level item if no item is selected.

        `delete_item()`:
            Delete the selected item in the PyFlameTreeWidget.
            Does not delete if the item is the top-level item or if the total number of items under the top-level item would drop below
            the minimum required that is set by the min_items argument.

        `sort_items()`:
            Sort all items in the tree while maintaining the structure and keeping the tree expanded.

    Attributes:
    -----------
        `all_item_paths`:
            Returns:
                List[str]:
                    The recursive paths of all items in the PyFlameTreeWidget.

        `all_item_paths_no_root`:
            Returns:
                List[str]:
                    The recursive paths of all items in the PyFlameTreeWidget excluding the root item.

        `item_path`:
            Returns:
                str:
                    The recursive path of the currently selected item.

        `item_paths`:
            Returns:
                List[str]:
                    The recursive paths of all selected items.

        `selected_item`:
            Returns:
                str:
                    The text of the currently selected item.
        `tree_dict`: A nested dictionary representing the tree structure. Useful when dealing with folder trees.
            Returns:
                Dict[str, Dict]:
                    A nested dictionary representing the tree structure.

        `tree_list`: A list of all item names in the tree. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            Returns:
                List[str]:
                    A list of all item names.

        `tree_list_no_root`: A list of all item names in the tree excluding the root item. Useful when dealing with batch group schematic reels shelf reels and desktop reels.
            Returns:
                List[str]:
                    A list of all item names excluding the root item.

    Inherited Methods:
    ------------------
        `setEnabled(bool)`:
            Enable or disable the PyFlameTreeWidget. True to enable, False to disable.

        `setSortingEnabled(bool)`:
            Enable or disable sorting in the PyFlameTreeWidget. True to enable sorting, False to disable.

        `clear()`:
            Clear all items from the PyFlameTreeWidget.

    Examples:
    ---------
        To create a PyFlameTreeWidget with a dictionary:
        ```
        tree_widget = PyFlameTreeWidget(
            column_names=[
                'Column 1',
                'Column 2',
                'Column 3',
                'Column 4',
                ],
            tree_dict={
                'Shot Folder': {
                    'Elements': {},
                    'Plates': {},
                    'Ref': {},
                    'Renders': {},
                    }
                },
            sorting=True,
            allow_children=False
            )
        ```

        To create a PyFlameTreeWidget with a list:
        ```
        tree_widget = PyFlameTreeWidget(
            column_names=[
                'Schematic Reel Template',
                ],
            tree_list=[
                'Schematic Reel 1',
                'Schematic Reel 2',
                'Schematic Reel 3',
                'Schematic Reel 4',
                ],
            top_level_item='Schematic Reels',
            sorting=True,
            allow_children=False
            )
        ```

        Add a new item to the tree:
        ```
        tree_widget.add_item(item_name='New Item')
        ```

        Delete the selected item in the tree:
        ```
        tree_widget.delete_item()
        ```

        Sort all items in the tree:
        ```
        tree_widget.sort_items()
        ```

        Get the text of the currently selected item:
        ```
        tree_widget.selected_item
        ```

        Get the recursive path of the currently selected item:
        ```
        tree_widget.item_path
        ```

        Get the recursive paths of all selected items:
        ```
        tree_widget.item_paths
        ```

        Get the recursive paths of all items in the PyFlameTreeWidget:
        ```
        tree_widget.all_item_paths
        ```
    """

    def __init__(self: 'PyFlameTreeWidget',
                 column_names: List[str],
                 connect: Optional[Callable[..., None]] = None,
                 width: int = 50,
                 height: int = 50,
                 max_width: Optional[bool] = True,
                 max_height: Optional[bool] = True,
                 tree_dict: Dict[str, Dict[str, str]] = {},
                 tree_list: List[str] = [],
                 top_level_item: Optional[str] = None,
                 top_level_editable: bool = False,
                 allow_children: bool = True,
                 sorting: bool = False,
                 min_items: int = 1,
                 update_callback: Optional[Callable[..., None]] = None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(column_names, list):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'column_names', 'list', column_names)
            if connect is not None and not callable(connect):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'connect', 'callable or None', connect)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'max_width', 'bool', max_width)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'max_height', 'bool', max_height)
            if not isinstance(tree_dict, dict):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'tree_dict', 'dict', tree_dict)
            if not isinstance(tree_list, list):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'tree_list', 'list', tree_list)
            if top_level_item is not None and not isinstance(top_level_item, str):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'top_level_item', 'str or None', top_level_item)
            if tree_list and not top_level_item:
                pyflame.raise_type_error(error_message="PyFlameTreeWidget: 'top_level_item' must be provided when 'tree_list' is used.")
            if not isinstance(top_level_editable, bool):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'top_level_editable', 'bool', top_level_editable)
            if not isinstance(allow_children, bool):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'allow_children', 'bool', allow_children)
            if not isinstance(sorting, bool):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'sorting', 'bool', sorting)
            if not isinstance(min_items, int) or min_items < 1:
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'min_items', 'int', min_items)
            if update_callback is not None and not callable(update_callback):
                pyflame.raise_type_error(f'PyFlameTreeWidget', 'update_callback', 'callable or None', update_callback)

        validate_arguments()

        # Set attributes
        self.allow_children = allow_children
        self.min_items = min_items
        self.top_level_editable = top_level_editable
        self.update_callback = update_callback

        # Set TreeWidget Settings
        self.setFont(FONT)
        self.header().setFont(FONT)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(connect)
        self.setHeaderLabels(column_names)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.itemCollapsed.connect(self._on_item_collapsed)  # Prevent top-level item from collapsing

        # Set PyFlameTreeWidget Size
        self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
        if max_width:
            self.setMaximumWidth(pyflame.gui_resize(3000))
        if max_height:
            self.setMaximumHeight(pyflame.gui_resize(3000))

        self._set_stylesheet()

        # Set sorting based on the argument
        self.setSortingEnabled(sorting)
        if sorting:
            self.sortItems(0, QtCore.Qt.AscendingOrder)

        # Fill tree with dictionary if provided, otherwise use list
        if tree_dict:
            self.fill_tree_dict(tree_dict)
        elif tree_list:
            # Convert list to dict using top_level_item as the key. Each item in the list should be a string value of the key not a list.
            tree_dict = {top_level_item: {str(item): {} for item in tree_list}}

            self.fill_tree_dict(tree_dict)

        # Set the first top-level item as the current item
        self.setCurrentItem(self.topLevelItem(0))

        # Set the top-level item as uneditable if top_level_editable is False
        if not top_level_editable:
            self._set_top_level_uneditable()

        # Trigger the callback function if it is set when an item is changed
        self.itemChanged.connect(self._trigger_callback)

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def fill_tree_dict(self, tree_dict: Dict[str, str], editable: bool=False) -> None:
        """
        Fill Tree Dict
        ==============

        Fill the PyFlameTreeWidget with items from the provided dictionary.

        Args:
        -----
            `tree_dict` (Dict[str, str]):
                Dictionary to populate the PyFlameTreeWidget.
                The keys and values should be strings representing item names and
                nested dictionaries in string format respectively.

            `editable` (bool, optional):
                Whether the items in the tree should be editable.
                (Default: False)

        Raises:
        -------
            TypeError:
                If `tree_dict` is not a dictionary.
                If `editable` is not a boolean.

            ValueError:
                If any key or value in `tree_dict` is not a string.
                If any value cannot be evaluated as a dictionary.

        Example:
        --------
            Populate the PyFlameTreeWidget with items from a dictionary:
            ```
            tree_data =
            tree_widget.fill_tree(
                tree_dict={
                    'Shot_Folder': {
                        'Elements': {},
                        'Plates': {},
                        'Ref': {},
                        'Renders': {}
                        }
                    },
                editable=True,
                )
            ```
        """

        # Validate arguments
        if not isinstance(tree_dict, dict):
            raise TypeError('fill_tree: tree_dict must be a dictionary.')
        if not isinstance(editable, bool):
            raise TypeError('fill_tree: editable must be a boolean.')
        for key, value in tree_dict.items():
            if not isinstance(key, (str, dict)):
                raise ValueError(f'fill_tree: All keys in tree_dict must be strings. Invalid key: {key}')
            if not isinstance(value, (str, dict)):
                raise ValueError(f'fill_tree: All values in tree_dict must be strings. Invalid value for key "{key}": {value}')

        # ============ Fill Tree ============ #

        # Disable sorting before filling the tree
        self.setSortingEnabled(False)

        # Set the default and editable flags for the items
        default_flags = (
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsEditable
            )
        editable_flags = default_flags | QtCore.Qt.ItemIsEditable

        def fill_item(parent: QtWidgets.QTreeWidgetItem, value: Dict) -> None:
            """
            Fill Item
            =========

            Recursively fill the PyFlameTreeWidget with items from the dictionary.
            """

            for key, val in value.items():
                child = QtWidgets.QTreeWidgetItem([key])
                parent.addChild(child)
                if isinstance(val, dict):
                    fill_item(child, val)

                # Set item flags
                if editable:
                    child.setFlags(editable_flags)
                else:
                    child.setFlags(default_flags)

                # Set the item as expanded initially if it has children
                if isinstance(val, dict) and val:
                    child.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)
                    child.setExpanded(True)

        self.clear()
        fill_item(self.invisibleRootItem(), tree_dict)

        # Restore sorting state based on the initial setting
        self.setSortingEnabled(self.isSortingEnabled())

    def fill_tree_list(self, tree_list: List[str]) -> None:
        """
        Fill Tree List
        ==============
        """

        self.clear()
        for item in tree_list:
            self.addTopLevelItem(QtWidgets.QTreeWidgetItem([item]))

    def add_item(self, item_name: str) -> None:
        """
        Add Item
        ========

        Add a new item as a child of the currently selected item in the PyFlameTreeWidget,
        or as a child of the top-level item if no item is selected.

        The new item will have the following flags:
        - Selectable
        - User checkable
        - Enabled
        - Editable

        Args:
            `item_name` (str):
                The name of new item to add.

        Raises:
            TypeError:
                If `item_name` is not a string.

        Example:
        --------
            Add a new item to the PyFlameTreeWidget:
            ```
            tree_widget.add_item(item_name='New Item')
            ```
        """

        # Validate the argument type
        if not isinstance(item_name, str):
            raise TypeError(f'add_item: item_name must be a string. Invalid item_name: {item_name}')

        # Disable sorting before adding the item
        self.setSortingEnabled(False)

        # Iterate the item name if it already exists in the tree
        existing_item_names = self.tree_list
        item_name = pyflame.iterate_name(existing_item_names, item_name)

        # Get the currently selected items
        selected_items = self.selectedItems()

        if not selected_items:
            # No item is selected, add the new item under the top-level item
            parent = self.topLevelItem(0)  # Always add under the first top-level item
            index = parent.childCount()
        else:
            selected_item = selected_items[0]
            if self.allow_children:
                parent = selected_item
                index = parent.childCount()
            else:
                parent = selected_item.parent()
                if not parent:
                    # Selected item is a top-level item, add under it
                    parent = selected_item
                    index = parent.childCount()
                else:
                    # Selected item is not a top-level item
                    index = parent.indexOfChild(selected_item) + 1

        # Create a new tree widget item with the specified name
        new_item = QtWidgets.QTreeWidgetItem([item_name])

        # Set the desired flags for the new item
        new_item.setFlags(
            QtCore.Qt.ItemIsSelectable |
            QtCore.Qt.ItemIsUserCheckable |
            QtCore.Qt.ItemIsEnabled |
            QtCore.Qt.ItemIsEditable
        )

        # Insert the new item at the determined position under the parent
        parent.insertChild(index, new_item)

        # Ensure the parent item is expanded to show the new child
        if parent != self.invisibleRootItem():
            parent.setExpanded(True)

        # Set the newly added item as the currently selected item
        self.setCurrentItem(new_item)

        # Restore sorting state based on the initial setting
        self.setSortingEnabled(self.isSortingEnabled())

        # Trigger the callback function if it is set
        self._trigger_callback()

        pyflame.print(f'Added item: {item_name}', text_color=TextColor.GREEN)

    def delete_item(self) -> None:
        """
        Delete Item
        ===========

        Deletes the selected item in the PyFlameTreeWidget.
        Will not delete if the item is the top-level item or if the total number of items under the top-level item would drop below the minimum required.

        Example:
        --------
            Delete the selected item in the PyFlameTreeWidget:
            ```
            tree_widget.delete_item()
            ```
        """

        # Get the currently selected items
        selected_items = self.selectedItems()

        if not selected_items:
            return  # No item is selected, do nothing

        selected_item = selected_items[0]

        # Get the parent of the selected item
        parent = selected_item.parent()

        # Check if the selected item is a top-level item
        if parent is None:
            pyflame.print('Cannot delete root folder from tree.', text_color=TextColor.RED)
            return  # Do not delete the top-level item

        # Count the total number of items under the top-level item
        def count_items(item: QtWidgets.QTreeWidgetItem) -> int:
            count = item.childCount()
            for i in range(item.childCount()):
                count += count_items(item.child(i))
            return count

        top_level_item = self.topLevelItem(0)
        total_items_under_top = count_items(top_level_item)

        # Check if the total number of items under the top-level item is less than or equal to the minimum items
        if total_items_under_top <= self.min_items:
            return  # Do not delete items if it would drop below the minimum number of items

        # If the item can be deleted, proceed with the deletion
        index = parent.indexOfChild(selected_item)
        parent.takeChild(index)

        # Restore sorting state based on the initial setting
        self.setSortingEnabled(self.isSortingEnabled())

        # Trigger the callback function if it is set
        self._trigger_callback()

        pyflame.print(f'Deleted item: {selected_item.text(0)}', text_color=TextColor.RED)

    def sort_items(self) -> None:
        """
        Sort Items
        ==========

        Sorts all items in the PyFlameTreeWidget while maintaining the structure and keeping the tree expanded.
        """

        def save_expansion_state(item: QtWidgets.QTreeWidgetItem, state: Dict[str, bool]) -> None:
            """
            Recursively save the expansion state of the items.
            """

            state[item.text(0)] = item.isExpanded()
            for i in range(item.childCount()):
                save_expansion_state(item.child(i), state)

        def restore_expansion_state(item: QtWidgets.QTreeWidgetItem, state: Dict[str, bool]) -> None:
            """
            Recursively restore the expansion state of the items.
            """

            item.setExpanded(state.get(item.text(0), False))
            for i in range(item.childCount()):
                restore_expansion_state(item.child(i), state)

        def sort_items_recursively(item: QtWidgets.QTreeWidgetItem) -> None:
            """
            Recursively sort the children of the item.
            """

            children = [item.child(i) for i in range(item.childCount())]
            children.sort(key=lambda x: x.text(0))

            for i, child in enumerate(children):
                item.takeChild(item.indexOfChild(child))
                item.insertChild(i, child)
                sort_items_recursively(child)

        # Save the expansion state
        expansion_state = {}
        top_level_items = [self.topLevelItem(i) for i in range(self.topLevelItemCount())]
        for top_level_item in top_level_items:
            save_expansion_state(top_level_item, expansion_state)

        # Disable sorting before manually sorting the items
        self.setSortingEnabled(False)

        # Sort the top-level items
        top_level_items.sort(key=lambda x: x.text(0))
        for i, top_level_item in enumerate(top_level_items):
            self.takeTopLevelItem(self.indexOfTopLevelItem(top_level_item))
            self.insertTopLevelItem(i, top_level_item)
            sort_items_recursively(top_level_item)

        # Restore the expansion state
        for top_level_item in top_level_items:
            restore_expansion_state(top_level_item, expansion_state)

        # Restore sorting state based on the initial setting
        self.setSortingEnabled(self.isSortingEnabled())

        # Trigger the callback function if it is set
        self._trigger_callback()

        pyflame.print('Tree items sorted.', text_color=TextColor.GREEN)

    #-------------------------------------
    # [Attributes]
    #-------------------------------------

    @property
    def all_item_paths(self) -> list:
        """
        All Item Paths
        ==============

        Generate a list of paths to all items in the tree.

        Returns:
        --------
            list:
                A list of strings, where each string is the recursive path to an item in the tree.
        """

        def get_paths(item, current_path):
            # Recursive helper function to build paths for each item and its children
            path = current_path + [item.text(0)]
            paths.append("/".join(path))
            for i in range(item.childCount()):
                get_paths(item.child(i), path)

        paths = []
        root_count = self.topLevelItemCount()
        for i in range(root_count):
            root_item = self.topLevelItem(i)
            get_paths(root_item, [])

        return paths

    @property
    def all_item_paths_no_root(self) -> list:
        """
        All Item Paths No Root
        ======================

        Generate a list of paths to all items in the tree excluding the root.

        Returns:
        --------
            list:
                A list of strings, where each string is the recursive path to an item in the tree excluding the root.
        """

        # Remove root item from paths
        clean_paths = []
        for path in self.all_item_paths:
            # Split the path by '/', exclude the root element, and rejoin the rest
            path_parts = path.split('/')
            if len(path_parts) > 1:  # Make sure there's more than just the root
                clean_paths.append("/".join(path_parts[1:]))

        return clean_paths

    @property
    def item_path(self) -> str:
        """
        Item Path
        =========

        Return the recursive path of the currently selected item.

        Returns:
        --------
            str:
                The recursive path of the currently selected item.

        Example:
        --------
            Get the recursive path of the currently selected item:
            ```
            tree_widget.item_path
            ```

        """

        item = self.currentItem()

        path = []
        while item is not None:
            path.insert(0, item.text(0))  # Insert at the beginning to build from root to leaf
            item = item.parent()  # Move up to the parent item

        return "/".join(path)  # Combine path elements with "/"

    @property
    def item_paths(self) -> List[str]:
        """
        Item Paths
        ==========

        Return the recursive paths of the currently selected items.

        Returns:
        --------
            List[str]:
                The recursive paths of the currently selected items.

        Example:
        --------
            Get the recursive paths of the currently selected items:
            ```
            tree_widget.item_paths
            ```
        """

        def get_item_path():

            item = self.currentItem()

            path = []
            while item is not None:
                path.insert(0, item.text(0))  # Insert at the beginning to build from root to leaf
                item = item.parent()  # Move up to the parent item

            return "/".join(path)  # Combine path elements with "/"

        return [get_item_path(item) for item in self.selectedItems()]

    @property
    def selected_item(self) -> str:
        """
        Selected Item
        =============

        Return the text of the currently selected item.

        Returns:
        --------
            str:
                The text of the currently selected item.

        Example:
        --------
            Get the text of the currently selected item:
            ```
            tree_widget.selected_item
            ```
        """

        return self.currentItem().text(0)

    @property
    def tree_dict(self) -> Dict[str, Dict]:
        """
        Tree Dict
        =========

        Get the items in the tPyFlameTreeWidget as a nested dictionary.

        This traverses the PyFlameTreeWidget, captures the hierarchical paths of each item,
        and converts these paths into a nested dictionary structure. Each item's path is
        represented as keys in the dictionary.

        Returns:
        --------
            Dict[str, Dict]:
                A nested dictionary representing the hierarchical structure of the PyFlameTreeWidget.

        Example:
        --------
            Get a nested dictionary representing the hierarchical structure of the PyFlameTreeWidget:
            ```
            tree_widget.tree_dict
            ```
        """

        def get_tree_path(item):
            """
            Get Tree Path
            =============

            Get the path of a tree item as a string.

            Args:
            -----
                `item` (QTreeWidgetItem):
                    The tree item to get the path for.

            Returns:
            --------
                str: The path of the item.
            """

            path = []
            while item:
                path.append(str(item.text(0)))
                item = item.parent()
            return '/'.join(reversed(path))

        def get_items_recursively():
            """
            Get Items Recursively
            ======================

            Recursively traverse the PyFlameTreeWidget and collect paths of all items.

            Args:
            -----
                `item` (QTreeWidgetItem, optional):
                    The tree item to start traversal from. Defaults to None.

            Returns:
            --------
                list: A list of paths of all tree items.
            """

            path_list = []

            def search_child_item(item):
                for m in range(item.childCount()):
                    child_item = item.child(m)
                    path_list.append(get_tree_path(child_item))
                    search_child_item(child_item)

            for i in range(self.topLevelItemCount()):
                top_item = self.topLevelItem(i)
                path_list.append(get_tree_path(top_item))
                search_child_item(top_item)

            return path_list

        # Get all paths from tree
        path_list = get_items_recursively()

        # Convert path list to dictionary
        tree_dict = {}
        for path in path_list:
            p = tree_dict
            for x in path.split('/'):
                p = p.setdefault(x, {})

        return tree_dict

    @property
    def tree_list(self) -> List[str]:
        """
        Tree List
        =========

        Property to get a list of all item names in the PyFlameTreeWidget.

        This property traverses the tree widget and collects the names of all items in a list.

        Returns:
        --------
            List[str]:
                A list of all item names.

        Example:
        --------
            Get a list of all item names:
            ```
            tree_widget.tree_list
            ```
        """

        item_names = []

        def traverse_item(item: QtWidgets.QTreeWidgetItem) -> None:
            item_names.append(item.text(0))
            for i in range(item.childCount()):
                traverse_item(item.child(i))

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            traverse_item(root.child(i))

        return item_names

    @property
    def tree_list_no_root(self) -> List[str]:
        """
        Tree List No Root
        =================

        Return the tree list excluding the root item.
        """

        return self.tree_list[1:]

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _trigger_callback(self) -> None:
        """
        Trigger Callback
        ================

        Trigger the callback function if it is set.
        """

        if self.update_callback:
            self.update_callback()

    def _set_top_level_uneditable(self) -> None:
        """
        Set Top Level Uneditable
        ========================

        Set the top-level item in the PyFlameTreeWidget as uneditable and all child items as editable.
        """

        # Access the top item using the tree object
        top_item = self.topLevelItem(0)  # Index 0 gets the first top-level item

        # Check if the top item exists. If it does, set the flags to make it uneditable and all child items editable
        if top_item:
            # Make the top_item non-editable
            top_item.setFlags(top_item.flags() & ~QtCore.Qt.ItemIsEditable)
            # Ensure all child items remain editable
            for i in range(top_item.childCount()):
                child_item = top_item.child(i)
                child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)

    def _on_item_collapsed(self, item):
        """
        On Item Collapsed
        =================

        Prevent the top-level item from collapsing.

        Args:
        -----
            `item` (PyFlameTreeWidget.QTreeWidgetItem):
                The item that was collapsed.
        """

        # Check if the item is a top-level item
        if self.indexOfTopLevelItem(item) != -1:
            self.expandItem(item)  # Re-expand the top-level item

    #-------------------------------------
    # [Stylesheet - Private Methods]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlameTreeWidget stylesheet.
        """

        self.setStyleSheet(f"""
            QTreeWidget{{
                color: {Color.TEXT.value};
                background-color: rgb(30, 30, 30);
                alternate-background-color: rgb(36, 36, 36);
                border: 1px solid rgba(0, 0, 0, .1);
                }}
            QTreeWidget::item{{
                padding-top: {pyflame.gui_resize(5)}px;  /* Increase top padding */
                padding-bottom: {pyflame.gui_resize(5)}px;  /* Increase bottom padding */
            }}
            QHeaderView::section{{
                color: {Color.TEXT.value};
                background-color: rgb(57, 57, 57);
                border: none;
                padding-left: {pyflame.gui_resize(10)}px;
                height: {pyflame.gui_resize(18)}px;
                }}
            QTreeWidget:item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: {Color.SELECTED_GRAY.value};
                selection-background-color: rgb(153, 153, 153);
                }}
            QTreeWidget:item:selected:active{{
                color: rgb(153, 153, 153);
                border: none;
                }}
            QTreeWidget:disabled{{
                color: rgb(101, 101, 101);
                background-color: rgb(34, 34, 34);
                }}
            QMenu{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 48, 61);
                }}
            QMenu::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: rgb(58, 69, 81);
                }}
            QScrollBar::handle{{
                background: {Color.SCROLLBAR_HANDLE.value};
                }}
            QScrollBar:vertical{{
                width: {pyflame.gui_resize(8)}px;  /* Adjust the width of the vertical scrollbar */
                }}
            QScrollBar:horizontal{{
                height: {pyflame.gui_resize(8)}px;  /* Adjust the height of the horizontal scrollbar */
                }}
            QTreeWidget::branch:has-siblings:!adjoins-item{{
                border-image: none;
                background: transparent;
                }}
            QTreeWidget::branch:has-siblings:adjoins-item{{
                border-image: none;
                background: transparent;
                }}
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item{{
                border-image: none;
                background: transparent;
                }}
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings{{
                border-image: none;
                background: transparent;
                }}
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings{{
                border-image: none;
                background: transparent;
                }}
            QTreeWidget:item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: {Color.SELECTED_GRAY.value};
                }}
            QHeaderView::section:disabled{{
                color: {Color.TEXT_DISABLED.value};
                }}
            QTreeWidget::item:disabled:selected {{
                color: {Color.TEXT_DISABLED.value};
                background-color: {Color.SELECTED_GRAY.value};
                }}
            """)

#-------------------------------------
# [PyFlame Line Widget Classes]
#-------------------------------------

class PyFlameHorizontalLine(QtWidgets.QFrame):
    def __init__(self: 'PyFlameHorizontalLine',
                width: int=50,
                height: int=1,
                max_width: bool=True,
                color: Color=Color.GRAY,
                ) -> None:
        super().__init__()

        """
        PyFlameHorizontalLine
        =====================

        Horizontal line widget. Controls for width, height, and color of line.

        Args:
        -----
            `width` (int):
                The width of the line in pixels.

            `height` (int):
                The height of the line in pixels.

            `max_width` (bool):
                If True, the line will have a maximum width. Lenght of line will be controlled by the layout when this is True.
                When False, the line will have a fixed width set by the `width` argument.

            `color` (Color):
                The color of the line. Uses Color Enum.

        Color Options:
        --------------
            - `Color.BLACK`
            - `Color.WHITE`
            - `Color.GRAY`
            - `Color.BRIGHT_GRAY`
            - `Color.BLUE`
            - `Color.RED`

        Example:
        --------
            Create a blue horizontal line:
            ```
            line = PyFlameHorizontalLine(color=Color.Blue)
            ```
        """

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameHorizontalLine', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameHorizontalLine', 'height', 'int', height)
            if not isinstance(max_width, bool):
                pyflame.raise_type_error(f'PyFlameHorizontalLine', 'max_width', 'bool', max_width)
            if not isinstance(color, Color):
                pyflame.raise_type_error(f'PyFlameHorizontalLine', 'color', 'Color Enum', color)

        validate_arguments()

        # Set frame shape and shadow
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Set line width
        if not max_width:
            self.setFixedWidth(width)

        # Set style sheet
        self.set_style_sheet(height, color)

    def set_style_sheet(self, height, color) -> None:

        self.setStyleSheet(f"""
            QFrame{{
                background-color: {color.value}; /* Line color */
                border: none;
                max-height: {height}px;
                min-height: {height}px;
                }}
            """)

class PyFlameVerticalLine(QtWidgets.QFrame):
    def __init__(self: 'PyFlameVerticalLine',
                width: int=1,
                height: int=50,
                max_height: bool=True,
                color: Color=Color.GRAY,
                ) -> None:
        super().__init__()
        """
        PyFlameVerticalLine
        ===================

        Vertical line widget. Controls for width, height, and color of line.

        Args:
        -----
            `width` (int):
                The width of the line in pixels.

            `height` (int):
                The height of the line in pixels.

            `max_height` (bool):
                If True, the line will have a maximum height. Lenght of line will be controlled by the layout when this is True.
                When False, the line will have a fixed height set by the `height` argument.

            `color` (Color):
                The color of the line. Uses Color Enum.

        Color Options:
        --------------
            - `Color.BLACK`
            - `Color.WHITE`
            - `Color.GRAY`
            - `Color.BRIGHT_GRAY`
            - `Color.BLUE`
            - `Color.RED`

        Example:
        --------
            Create a blue vertical line:
            ```
            line = PyFlameVerticalLine(color=Color.Blue)
            ```
        """

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameVerticalLine', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameVerticalLine', 'height', 'int', height)
            if not isinstance(max_height, bool):
                pyflame.raise_type_error(f'PyFlameVerticalLine', 'max_height', 'bool', max_height)
            if not isinstance(color, Color):
                pyflame.raise_type_error(f'PyFlameVerticalLine', 'color', 'Color Enum', color)

        validate_arguments()

        # Set frame shape and shadow
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Set line width
        if not max_height:
            self.setFixedHeight(height)

        # Set style sheet
        self.set_style_sheet(width, color)

    def set_style_sheet(self, width, color) -> None:

        self.setStyleSheet(f"""
            QFrame{{
                background-color: {color.value}; /* Line color */
                border: none;
                max-width: {width}px;
                min-width: {width}px;
                }}
            """)

#-------------------------------------
# [PyFlame Layout Classes]
#-------------------------------------

class PyFlameGridLayout(QtWidgets.QGridLayout):
    """
    PyFlameGridLayout
    =================

    Custom QT QGridLayout Subclass.

    Configure the grid size of the layout by setting the number of columns, rows,
    and their respective sizes. Optionally adjust the width of specific columns
    and the height of specific rows.

    Args:
    -----
        `columns` (int):
            Number of columns in the grid.
            Columns start counting at 0.
            (Default: `0`)

        `rows` (int):
            Number of rows in the grid.
            Rows start counting at 0.
            (Default: `0`)

        `column_width` (int):
            Default width of each column in pixels.
            (Default: `150`)

        `row_height` (int):
            Default height of each row in pixels.
            (Default: `28`)

        `adjust_column_widths` (dict[int, int], optional):
            A dictionary to adjust the width of specific columns.
            Keys are column indices (0-based), and values are widths in pixels.
            (Default: `{}`)

        `adjust_row_heights` (dict[int, int], optional):
            A dictionary to adjust the height of specific rows.
            Keys are row indices (0-based), and values are heights in pixels.
            (Default: `{}`)

    Raises:
    -------
        TypeError:
            If any argument is not of the expected type.

    Example:
    --------
        Create a PyFlameGridLayout with 4 columns and 5 rows:
        ```
        grid_layout = PyFlameGridLayout(
            columns=4,
            rows=5,
            )
        ```

        Create a PyFlameGridLayout with 4 columns and 5 rows, with specific column widths:
        ```
        grid_layout = PyFlameGridLayout(
            columns=4,
            rows=5,
            adjust_column_widths={0: 200, 1: 150, 2: 100, 3: 50},
            )
        ```
    """

    def __init__(
        self: 'PyFlameGridLayout',
        columns: int = 0,
        rows: int = 0,
        column_width: int = 150,
        row_height: int = 28,
        adjust_column_widths: dict[int, int] = {},
        adjust_row_heights: dict[int, int] = {}
        ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(columns, int):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'columns', 'int', columns)
            if not isinstance(rows, int):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'rows', 'int', rows)
            if not isinstance(column_width, int):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'column_width', 'int', column_width)
            if not isinstance(row_height, int):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'row_height', 'int', row_height)
            if not isinstance(adjust_column_widths, dict):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'adjust_column_widths', 'dict', adjust_column_widths)
            if not isinstance(adjust_row_heights, dict):
                pyflame.raise_type_error(f'PyFlameGridLayout', 'adjust_row_heights', 'dict', adjust_row_heights)

        validate_arguments()

        self.setContentsMargins(pyflame.gui_resize(5), pyflame.gui_resize(5), pyflame.gui_resize(5), pyflame.gui_resize(5))

        # Create and add widgets to the grid
        for row in range(rows):
            for col in range(columns):
                # If adjust_column_widths is None or empty, default to column_width
                if adjust_column_widths and col in adjust_column_widths:
                    width = adjust_column_widths[col]
                else:
                    width = column_width

                # If adjust_row_heights is None or empty, default to row_height
                if adjust_row_heights and row in adjust_row_heights:
                    height = adjust_row_heights[row]
                else:
                    height = row_height

                # Create the label with the specified dimensions
                empty_label = PyFlameLabel(
                    text='',
                    width=width,
                    height=height
                )
                self.addWidget(empty_label, row, col)

class PyFlameHBoxLayout(QtWidgets.QHBoxLayout):
    """
    PyFlameHBoxLayout
    =================

    Custom QT QHBoxLayout Subclass.

    Values are adjusted for display scale using `pyflame.gui_resize()`.

    Methods:
    --------
        `setSpacing(spacing)`:
            Apply spacing between widgets in PyFlameHBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

        `setContentsMargins(left, top, right, bottom)`:
            Apply margins to PyFlameHBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

    Example:
    --------
        To create a PyFlameHBoxLayout with a couple of widgets added to it:
        ```
        hbox_layout = PyFlameHBoxLayout()
        hbox_layout.setSpacing(10)
        hbox_layout.setContentsMargins(10, 10, 10, 10)
        hbox_layout.addWidget(self.label_01)
        hbox_layout.addWidget(self.pushbutton_01)
        ```
    """

    def __init__(self: 'PyFlameHBoxLayout') -> None:
        super().__init__()

    def setSpacing(self, spacing: int) -> None:
        """
        Set Spacing
        ===========

        Add fixed amount of space between widgets in the PyFlameHBoxLayout.

        Spacing is adjusted for display scale using `pyflame.gui_resize()`.

        The spacing affects all widgets added to the PyFlameHBoxLayout after the `setSpacing` call. It does not
        alter the PyFlameHBoxLayout's margins—use `setContentsMargins` for margin adjustments. The spacing is
        applied between the widgets themselves, not between widgets and the PyFlameHBoxLayout's border or between
        widgets and any layout containers (e.g., windows) they may be in.

        Args:
        -----
            `spacing` (int):
                Spacing in pixels.

        Raises:
        -------
            TypeError:
                If `spacing` is not an integer.

        Example:
        --------
            To set the spacing between widgets in the PyFlameHBoxLayout to 10 pixels:
            ```
            hbox_layout.setSpacing(10)
            ```
        """

        if not isinstance(spacing, int):
            pyflame.raise_type_error(f'PyFlameHBoxLayout.setSpacing', 'spacing', 'int', spacing)

        # Set Spacing
        super().setSpacing(pyflame.gui_resize(spacing))

    def addSpacing(self, spacing: int) -> None:
        """
        Add Spacing
        ===========

        Insert fixed amount of non-stretchable space between widgets in the PyFlameHBoxLayout.

        Spacing is adjusted for display scale using `pyflame.gui_resize()`.

        This method adds a spacer item of a specified size to the PyFlameHBoxLayout, effectively increasing
        the distance between the widget that precedes the spacer and the widget that follows it.
        The space is a one-time, non-adjustable gap that does not grow or shrink with the PyFlameHBoxLayout's
        resizing, providing precise control over the spacing in the PyFlameHBoxLayout.

        Args:
        -----
            `spacing` (int):
                Spacing in pixels.

        Raises:
        -------
            TypeError:
                If `spacing` is not an integer.

        Example:
        --------
            To add a 10-pixel space between two widgets in the PyFlameHBoxLayout:
            ```
            hbox_layout.addSpacing(10)
            ```
        """

        # Validate argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error(f'PyFlameHBoxLayout.setSpacing', 'spacing', 'int', spacing)

        # Add Spacing
        super().addSpacing(pyflame.gui_resize(spacing))

    def setContentsMargins(self, left: int, top: int, right: int, bottom: int) -> None:
        """
        Set Contents Margins
        ====================

        Set margins around the contents of the PyFlameHBoxLayout.

        Values are adjusted for display scale using `pyflame.gui_resize()`.

        This method specifies the size of the margins on each side of the PyFlameHBoxLayout container.
        Margins are defined as the space between the outermost widgets in the PyFlameHBoxLayout and the
        edges of the PyFlameHBoxLayout's container (e.g., a window).

        Args:
        -----
            `left` (int):
                Left margin in pixels.

            `top` (int):
                Top margin in pixels.

            `right` (int):
                Right margin in pixels.

            `bottom` (int):
                Bottom margin in pixels.

        Raises:
        -------
            TypeError:
                If `left` is not an integer.
                If `top` is not an integer.
                If `right` is not an integer.
                If `bottom` is not an integer.

        Example:
        --------
            To set margins around the contents of the PyFlameHBoxLayout to 10 pixels:
            ```
            hbox_layout.setContentsMargins(10, 10, 10, 10)
            ```
        """

        def validate_arguments():

            if not isinstance(left, int):
                pyflame.raise_type_error(f'PyFlameHBoxLayout.setContentsMargins', 'left', 'int', left)
            if not isinstance(top, int):
                pyflame.raise_type_error(f'PyFlameHBoxLayout.setContentsMargins', 'top', 'int', top)
            if not isinstance(right, int):
                pyflame.raise_type_error(f'PyFlameHBoxLayout.setContentsMargins', 'right', 'int', right)
            if not isinstance(bottom, int):
                pyflame.raise_type_error(f'PyFlameHBoxLayout.setContentsMargins', 'bottom', 'int', bottom)

        validate_arguments()

        # Set Margins
        super().setContentsMargins(
            pyflame.gui_resize(left),
            pyflame.gui_resize(top),
            pyflame.gui_resize(right),
            pyflame.gui_resize(bottom)
            )

class PyFlameVBoxLayout(QtWidgets.QVBoxLayout):
    """
    PyFlameVBoxLayout
    =================

    Custom QT QVBoxLayout Subclass.

    Values are adjusted for display scale using `pyflame.gui_resize()`.

    Methods:
    --------
        `setSpacing(spacing)`:
            Apply spacing between widgets in the PyFlameVBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

        `setContentsMargins(left, top, right, bottom)`:
            Apply margins to the PyFlameVBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

    Example:
    --------
        To create a PyFlameVBoxLayout with a couple of widgets added to it:
        ```
        vbox_layout = PyFlameVBoxLayout()
        vbox_layout.setSpacing(10)
        vbox_layout.setContentsMargins(10, 10, 10, 10)
        vbox_layout.addWidget(self.label_01)
        vbox_layout.addWidget(self.pushbutton_01)
        ```
    """

    def __init__(self: 'PyFlameVBoxLayout') -> None:
        super().__init__()

    def setSpacing(self, spacing: int) -> None:
        """
        Set Spacing
        ===========

        Add fixed amount of space between widgets in the PyFlameVBoxLayout.

        Spacing is adjusted for display scale using `pyflame.gui_resize()`.

        The spacing affects all widgets added to the PyFlameVBoxLayout after the `setSpacing` call. It does not
        alter the PyFlameVBoxLayout's margins—use `setContentsMargins` for margin adjustments. The spacing is
        applied between the widgets themselves, not between widgets and the PyFlameVBoxLayout's border or between
        widgets and any PyFlameVBoxLayout containers (e.g., windows) they may be in.

        Args:
        -----
            `spacing` (int):
                Spacing in pixels.

        Raises:
        -------
            TypeError:
                If `spacing` is not an integer.

        Example:
        --------
            To set the spacing between widgets in the PyFlameVBoxLayout to 10 pixels:
            ```
            vbox_layout.setSpacing(10)
            ```
        """

        # Validate argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error(f'PyFlameVBoxLayout.setSpacing', 'spacing', 'int', spacing)

        # Set Spacing
        super().setSpacing(pyflame.gui_resize(spacing))

    def addSpacing(self, spacing: int) -> None:
        """
        Add Spacing
        ===========

        Insert fixed amount of non-stretchable space between widgets in the PyFlameVBoxLayout.

        Spacing is adjusted for display scale using `pyflame.gui_resize()`.

        This method adds a spacer item of a specified size to the PyFlameVBoxLayout, effectively increasing
        the distance between the widget that precedes the spacer and the widget that follows it.
        The space is a one-time, non-adjustable gap that does not grow or shrink with the PyFlameVBoxLayout's
        resizing, providing precise control over the spacing in the PyFlameVBoxLayout.

        Args:
        -----
            `spacing` (int):
                Spacing in pixels.

        Raises:
        -------
            TypeError:
                If `spacing` is not an integer.

        Example:
        --------
            To add a 10-pixel space between two widgets in the PyFlameVBoxLayout:
            ```
            vbox_layout.addSpacing(10)
            ```
        """

        # Validate argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error(f'PyFlameVBoxLayout.addSpacing', 'spacing', 'int', spacing)

        # Add Spacing
        super().addSpacing(pyflame.gui_resize(spacing))

    def setContentsMargins(self, left: int, top: int, right: int, bottom: int) -> None:
        """
        Set Contents Margins
        ====================

        Sets the margins around the contents of the PyFlameVBoxLayout.

        Values are adjusted for display scale using `pyflame.gui_resize()`.

        This method specifies the size of the margins on each side of the PyFlameVBoxLayout container.
        Margins are defined as the space between the outermost widgets in the PyFlameVBoxLayout and the
        edges of the PyFlameVBoxLayout's container (e.g., a window).

        Args:
        -----
            `left` (int):
                Left margin in pixels.
            `top` (int):
                Top margin in pixels.
            `right` (int):
                Right margin in pixels.
            `bottom` (int):
                Bottom margin in pixels.

        Raises:
        -------
            TypeError:
                If `left` is not an integer.
                If `top` is not an integer.
                If `right` is not an integer.
                If `bottom` is not an integer.

        Example:
        --------
            To set margins around the contents of the PyFlameVBoxLayout to 10 pixels:
            ```
            vbox_layout.setContentsMargins(10, 10, 10, 10)
            ```
        """

        def validate_arguments():

            if not isinstance(left, int):
                pyflame.raise_type_error(f'PyFlameVBoxLayout.setContentsMargins', 'left', 'int', left)
            if not isinstance(top, int):
                pyflame.raise_type_error(f'PyFlameVBoxLayout.setContentsMargins', 'top', 'int', top)
            if not isinstance(right, int):
                pyflame.raise_type_error(f'PyFlameVBoxLayout.setContentsMargins', 'right', 'int', right)
            if not isinstance(bottom, int):
                pyflame.raise_type_error(f'PyFlameVBoxLayout.setContentsMargins', 'bottom', 'int', bottom)

        validate_arguments()

        # Set Margins
        super().setContentsMargins(
            pyflame.gui_resize(left),
            pyflame.gui_resize(top),
            pyflame.gui_resize(right),
            pyflame.gui_resize(bottom)
            )

#-------------------------------------
# [PyFlame Preset Manager]
#-------------------------------------

class PyFlamePresetManager():
    """
    PyFlamePresetManager
    ====================

    Handles management of presets for Flame python scripts.

    Actions
    -------

        New
        ---
            Creates a new preset using default values that can be edited.

        Edit
        ----
            Edit an existing preset from the preset list.

        Duplicate
        ---------
            Create a duplicate of the selected preset.

        Delete
        ------
            Delete the selected preset.
            If the selected preset is the default preset, the default preset will be set to the first preset in the preset list.
            If the selected preset is a project preset, all project presets using the preset will be set to the default preset.
            If the selected preset is both the default and project preset, the default preset will be set to the first preset in
            the preset list and all project presets using the preset will be set to the default preset.

        Set Default Preset
        ------------------
            Set the selected preset as the default preset.
            The default preset will be used for all Flame projects unless a project preset is set.

        Set Project Preset
        ------------------
            Set the selected preset as the project preset for the current project.
            This will bypass the default preset.

        Remove Project Preset
        ---------------------
            Remove the preset assigned to the current project.
            This will cause the current project to use the default preset.

    Args
    ----
        `script_version` (str):
            Version of the script.

        `setup_script` (callable):
            Setup window class/function.

        `script_name` (str):
            Name of the script.
            (Default: `SCRIPT_NAME`)

        `script_path` (str): Path to the script.
            (Default: `SCRIPT_PATH`)

    Raises
    ------
        TypeError:
            If `script_name` is not a string.
            if `script_version` is not a string.
            If `script_path` is not a string.
            If `setup_script` is not callable function.

    Example
    -------
        Initialize PyFlamePresetManager:
        ```
        PyFlamePresetManager(
            script_version=SCRIPT_VERSION,
            setup_script=ScriptSetup,
            )
        ```

    Public Methods
    --------------
        load_preset() -> PyFlameConfig:
            Loads preset assigned to current project(Project or Default Preset) and returns preset settings as attributes.
            ```
            self.settings = PyFlamePresetManager(
                script_version=SCRIPT_VERSION,
                setup_script=None,
                ).load_preset()
            ```
    """

    def __init__(
            self,
            script_version: str,
            setup_script: Callable[..., Any] = None,
            script_name: str=SCRIPT_NAME,
            script_path: str=SCRIPT_PATH,
        ):

        # Validate argument types
        if not isinstance(script_version, str):
            raise TypeError(f'PyFlamePresetManager: script_version must be a string.')
        elif setup_script is not None and not callable(setup_script):
            raise TypeError('PyFlamePresetManager: setup_script must be a callable function or None.')
        elif not isinstance(script_name, str):
            raise TypeError('PyFlamePresetManager: script_name must be a string.')
        elif not isinstance(script_path, str):
            raise TypeError(f'PyFlamePresetManager: script_path must a string.')

        pyflame.print_title(f'{script_name} Preset Manager {script_version}')

        # Initialize variables
        self.default_preset_extension = ' (Default)'
        self.project_preset_extension = ' (Project)'
        self.script_name = script_name
        self.script_version = script_version
        self.script_path = script_path
        self.setup_script = setup_script
        self.flame_prj_name = flame.projects.current_project.project_name
        self.preset_settings_name = self.script_name.lower().replace(' ', '_') + '_preset_settings'

        # Initialize paths
        self.preset_config_json = os.path.join(self.script_path, 'config', 'preset_manager_config.json') # Preset Manager config file
        self.preset_path = os.path.join(self.script_path, 'config', 'presets')
        self.project_config_path = os.path.join(self.script_path, 'config', 'project_presets')

        # Create preset folders if they do not exist
        self.create_preset_folders()

        # Load/Create Preset Manager config file
        self.settings = self.load_config()

        if setup_script:
            # Open preset window
            self.preset_window()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load Preset Manager config values from config file.

        Returns:
        --------
            settings (PyFlameConfig): PyFlameConfig instance with loaded config values.
        """

        settings = PyFlameConfig(
            config_values={
                'default_preset': '',
                },
            config_path=self.preset_config_json,
            script_name=self.script_name,
            )

        return settings

    def save_config(self) -> None:
        """
        Save Config
        ===========

        Save Preset Manager config values to config file.
        """

        self.settings.save_config(
            config_values={
                'default_preset': self.settings.default_preset,
                },
            config_path=self.preset_config_json,
            )

    def message_print(self, message: str) -> None:
        """
        Message Print
        =============

        Print message to Flame message window and terminal/shell.

        Args:
        -----
            `message (str)`:
                Message to print.
        """

        pyflame.print(
            text=message,
            script_name=self.script_name,
            )

    def info_message(self, message: str) -> None:
        """
        Info Message
        ============

        Open info message window using PyFlameMessageWindow.

        Args:
        -----
            `message (str)`:
                The message to display.
        """

        PyFlameMessageWindow(
            message=message,
            script_name=self.script_name,
            )

    def error_message(self, message: str) -> None:
        """
        Error Message
        =============

        Open error message window using PyFlameMessageWindow.

        Args:
        -----
            `message (str)`:
                The message to display.
        """

        PyFlameMessageWindow(
            message=message,
            script_name=self.script_name,
            type=MessageType.ERROR,
            )

    def warning_message(self, message:str) -> bool:
        """
        Warning Message
        ===============

        Open warning message window using PyFlameMessageWindow.

        Args:
        -----
            `message (str)`:
                The message to display.

        Returns:
        --------
            confirm (bool): User confirmation to proceed.
        """

        confirm = PyFlameMessageWindow(
            message=message,
            script_name=self.script_name,
            type=MessageType.WARNING,
            )

        return confirm

    def confirm_message(self, message: str) -> bool:
        """
        Confirm Message
        ===============

        Open confirm message window using PyFlameMessageWindow.

        Args:
        -----
            `message (str)`:
                The message to display.

        Returns:
        --------
            confirm (bool): User confirmation to proceed.
        """

        confirm = PyFlameMessageWindow(
            message=message,
            script_name=self.script_name,
            type=MessageType.CONFIRM,
            )

        return confirm

    def create_preset_folders(self) -> None:
        """
        Create Preset Folders
        ======================

        Check for preset folders and create if they do not exist.
        """

        if not os.path.isdir(self.preset_path):
            os.makedirs(self.preset_path)

        if not os.path.isdir(self.project_config_path):
            os.makedirs(self.project_config_path)

    # ----------------------------------------------------------------------------------------------------------------------

    def preset_window(self) -> None:
        """
        Preset Window
        =============

        Build Preset Manager window.
        """

        def close_window() -> None:
            """
            Close Window
            ============

            Close preset window
            """

            self.preset_window.close()

            self.message_print('Done.')

        # Build window
        self.preset_window = PyFlameWindow(
            title=f'{self.script_name} Preset Manager <small>{self.script_version}',
            return_pressed=close_window,
            grid_layout_columns=7,
            grid_layout_rows=7,
            grid_layout_adjust_column_widths={4: 50},
            )

        # Labels
        self.current_project_preset_label = PyFlameLabel(
            text='Current Project Preset',
            )
        self.presets_label = PyFlameLabel(
            text='Presets',
            )

        # Entry Fields
        self.current_project_preset_field = PyFlameEntry(
            text='',
            placeholder_text='No presets available. Create a new preset.',
            read_only=True,
            )

        # Push Button Menu
        self.current_preset_menu_pushbutton = PyFlamePushButtonMenu(
            text='',
            menu_options=[],
            )

        #  Buttons
        self.new_button = PyFlameButton(
            text='New',
            connect=self.new_preset,
            tooltip='Create new preset.',
            )
        self.set_as_default_button = PyFlameButton(
            text='Set Default Preset',
            connect=self.set_as_default_preset,
            tooltip='Set selected preset as default preset. The default preset will be used for all Flame projects unless a different preset is set for the current project.',
            )
        self.edit_button = PyFlameButton(
            text='Edit',
            connect=self.edit_preset,
            tooltip='Edit selected preset.',
            )
        self.set_project_preset_button = PyFlameButton(
            text='Set Project Preset',
            connect=self.set_preset_to_current_project,
            tooltip='Set current preset as current project preset. This will bypass the default preset.',
            )
        self.remove_from_project_button = PyFlameButton(
            text='Remove Project Preset',
            connect=self.remove_preset_from_project,
            tooltip='Remove preset assigned to current project.',
            )
        self.delete_button = PyFlameButton(
            text='Delete',
            connect=self.delete_preset,
            tooltip='Delete selected preset.',
            )
        self.duplicate_button = PyFlameButton(
            text='Duplicate',
            connect=self.duplicate_preset,
            tooltip='Duplicate selected preset.',
            )

        self.done_btn = PyFlameButton(
            text='Done',
            connect=close_window,
            color=Color.BLUE,
            )

        # Get current project preset to display in current project preset field
        self.update_ui()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.preset_window.grid_layout.addWidget(self.current_project_preset_label, 0, 0)
        self.preset_window.grid_layout.addWidget(self.current_project_preset_field, 0, 1, 1, 3)
        self.preset_window.grid_layout.addWidget(self.presets_label, 1, 0)
        self.preset_window.grid_layout.addWidget(self.current_preset_menu_pushbutton, 1, 1, 1, 3)

        self.preset_window.grid_layout.addWidget(self.new_button, 1, 5)
        self.preset_window.grid_layout.addWidget(self.edit_button, 1, 6)

        self.preset_window.grid_layout.addWidget(self.duplicate_button, 2, 5)
        self.preset_window.grid_layout.addWidget(self.delete_button, 2, 6)

        self.preset_window.grid_layout.addWidget(self.set_as_default_button, 3, 5)

        self.preset_window.grid_layout.addWidget(self.set_project_preset_button, 4, 5)
        self.preset_window.grid_layout.addWidget(self.remove_from_project_button, 4, 6)

        self.preset_window.grid_layout.addWidget(self.done_btn, 6, 6)

        # self.preset_window.add_layout(grid_layout)
        # self.preset_window.show()

    # ---------------------------------------- #
    # Button Functions
    # ---------------------------------------- #

    def new_preset(self) -> None:
        """
        New Preset
        ==========

        Create a new preset by opening the setup window with default settings.
        """

        self.message_print('Creating new preset...')

        new_preset_name = self.create_or_edit_preset()

        if new_preset_name:
            self.message_print(f'New preset created: {new_preset_name}')
        else:
            self.message_print('New preset creation cancelled.')

    def edit_preset(self) -> None:
        """
        Edit Preset
        ===========

        Edit the currently selected preset by loading the setup window with the preset settings.
        """

        self.message_print('Editing selected preset...')

        # Get config settings from selected preset
        preset = self.get_current_preset_button_name()
        preset_path = os.path.join(self.preset_path, preset + '.json')
        #print('Preset Path:', preset_path, '\n')

        settings = PyFlameConfig.get_config_values(config_path=preset_path)
        #print('Settings Dict:', settings, '\n')

        preset_config = PyFlameConfig(
            config_values=settings,
            config_path=preset_path,
            script_name=self.script_name,
            )

        # Load Setup window passing preset_config to load preset values.
        preset_name = self.create_or_edit_preset(preset_path=preset_path, preset_config=preset_config)

        if preset_name:
            self.message_print(f'Edited preset: {preset_name}')
        else:
            self.message_print('Edit cancelled.')

    def set_as_default_preset(self) -> None:
        """
        Set as Default Preset
        ======================

        Set currently selected preset as the default preset.
        Default preset will have ' (Default)' added to the end of the name.

        Updates current Current Project Preset field, Preset button, Preset list, and config file.
        """

        self.message_print('Updating default preset...')

        if self.current_preset_menu_pushbutton.text():
            self.update_default_preset(self.current_preset_menu_pushbutton.text())# Set default preset in preset config JSON
            self.update_ui() # Update UI with new default preset
            self.message_print(f'Default preset set to: {self.current_preset_menu_pushbutton.text()}')
        else:
            self.message_print('No preset selected to set as Default Preset.')

    def set_preset_to_current_project(self) -> None:
        """
        Set Preset to Current Project
        ==============================

        Assigns the current preset to the current project.

        Set the currently selected preset as the project preset for the current project.
        If a project preset already exists for the current project, it will be deleted and replaced with the new preset.

        If there is no preset currently selected, the function prints a message indicating that no preset was selected to set as the project preset.
        """

        self.message_print('Assigning preset to current project...')

        if self.current_preset_menu_pushbutton.text():
            preset_name_text = self.get_current_preset_button_name() # Get current preset button name
            #print('Preset Name Text:', preset_name_text, '\n')

            # Path for new preset file
            preset_path = os.path.join(self.project_config_path, self.flame_prj_name + '.json')

            # If project preset already exists, delete it before creating new one.
            if os.path.isfile(preset_path):
                os.remove(preset_path)

            # Create project preset
            self.create_project_preset_json(preset_name_text, preset_path)

            # Update ui with new project preset name
            self.update_ui() # Update UI with new preset

            self.message_print(f'Preset set for this project: {preset_name_text}')
        else:
            self.message_print('No preset selected to set as Project Preset.')

    def remove_preset_from_project(self) -> None:
        """
        Remove Preset from Project
        ==========================

        Remove the preset from the current project.

        Unassign the preset from the current project. If the preset is not set as the default preset,
        it will no longer be associated with this project. The preset file itself will not be deleted, only its
        association with the current project is removed.

        Note:
        - If the preset is also set as the default preset, it will remain associated with the project.
        - This function updates the UI after removing the preset.
        """

        preset_name = self.get_current_preset_button_name() # Get current preset from push button

        self.message_print(f'Removing preset from project: {preset_name}')

        # Delete project preset JSON file
        project_preset_path = os.path.join(self.project_config_path, self.flame_prj_name + '.json')
        if os.path.isfile(project_preset_path):
            os.remove(project_preset_path)
            self.message_print(f'Preset removed from project: {preset_name}')
        else:
            self.message_print(f'No project preset found for current project.')

        # Update UI
        self.update_ui()

    def duplicate_preset(self) -> None:
        """
        Duplicate Preset
        ================

        Create a duplicate of the currently selected preset.

        Duplicate the currently selected preset by creating a copy of its JSON file with 'copy' appended to the end of its name.
        If there are existing presets with the same name in the preset directory, 'copy' is incrementally appended until a unique name is found.

        If there is no preset currently selected, the function prints a message indicating that no preset was selected for duplication.

        Note:
        - The duplicated preset maintains the same settings as the original.
        - The duplicated preset is immediately added to the preset menu and displayed in the UI.
        """

        print('Duplicating preset...\n')

        if self.current_preset_menu_pushbutton.text():
            # Get list of existing saved presets
            existing_presets = [f[:-5] for f in os.listdir(self.preset_path)]

            # Get current preset name from push button
            current_preset_name = self.get_current_preset_button_name()

            # Set new preset name to current preset name
            new_preset_name = current_preset_name

            # If preset name already exists, add ' copy' to the end of the name until a unique name is found
            while new_preset_name in existing_presets:
                new_preset_name = new_preset_name  + ' copy'

            # Duplicate preset JSON file with new preset name
            source_file = os.path.join(self.preset_path, current_preset_name + '.json')
            dest_file = os.path.join(self.preset_path, new_preset_name + '.json')
            shutil.copyfile(source_file, dest_file)

            # Update preset name in new preset JSON file
            self.preset_json_save_preset_name(
                preset_path=dest_file,
                preset_name=new_preset_name,
                )

            # Update UI
            self.update_ui()
            self.current_preset_menu_pushbutton.setText(new_preset_name)

            self.message_print(f'Duplicate preset created: {new_preset_name}')
        else:
            print('No preset selected to duplicate.\n')

    def delete_preset(self) -> None:
        """
        Delete Preset
        =============

        Deletes the currently selected preset.

        This function ensures that the preset being deleted is not in use by any project preset or set as the default preset.
        If the preset is the default preset, the preset at the top of the list will be set as the default preset until one is set.
        If the preset is being used by other projects, the user will be prompted to confirm deletion. All project presets using the preset
        being deleted will be set to the default preset.
        """

        def check_project_files():
            """
            Check all project config files for the current preset before deletion.
            """

            preset_names = []
            preset_paths = []

            if os.listdir(self.project_config_path):
                for config_file in os.listdir(self.project_config_path):
                    preset_path = os.path.join(self.project_config_path, config_file)
                    saved_preset_name = self.get_project_preset_name_json(preset_path)
                    preset_names.append(saved_preset_name)
                    preset_paths.append(preset_path)

            if preset_names:
                if preset_name.split(' (Project)')[0] in preset_names:
                    return preset_paths # User confirmed deletion.
                else:
                    return True # Preset not used by other projects, can be deleted.
            else:
                return True # No project presets, can be deleted.

        print('Deleting preset...\n')

        if self.current_preset_menu_pushbutton.text():
            preset_name = self.current_preset_menu_pushbutton.text() # Get current preset from push button
            preset_path = os.path.join(self.preset_path, preset_name + '.json') # Get path to preset JSON file

            project_files = check_project_files()

            # If selected preset is not the default preset, confirm deletion, check to see if other projects are using preset, then delete preset, otherwise return.
            if not preset_name.endswith(self.default_preset_extension) and not preset_name.endswith(self.project_preset_extension):
                if self.warning_message(message=f'Delete preset: {preset_name}'):
                    # Check all project config files for current preset before deleting.
                    if project_files:
                        os.remove(preset_path)
                        self.update_ui() # Update UI with new default preset
                        self.message_print(f'Preset deleted: {preset_name}')
                        self.save_config()
                    else:
                        return
                else:
                    return

            # If selected preset is the default preset, confirm that the user wants to delete it.
            elif preset_name.endswith(self.default_preset_extension):
                confirm_delete = self.warning_message(message=f'Selected preset is currently the default preset.\n\nDeleting this preset will set the default preset to the first saved preset in the preset list.\n\nAre you sure you want to delete this preset?')
                if not confirm_delete:
                    return

            # If selected preset it the project preset, confirm that the user wants to delete it.
            elif preset_name.endswith(self.project_preset_extension):
                confirm_delete = self.warning_message(message=f'Selected preset is currently the project preset for one or more projects.\n\nDeleting this preset will set all those projects to the default preset.\n\nAre you sure you want to delete this preset?')
                if not confirm_delete:
                    return

            # If user confirmed deletion, check all project config files for current preset before deleting.
            if confirm_delete:
                if project_files:
                    # If confirmed, delete preset
                    preset_path = os.path.join(self.preset_path, preset_name + '.json')
                    os.remove(os.path.join(self.preset_path, self.get_current_preset_button_name() + '.json'))

                    # Set new default preset to first preset in preset list if it exists, otherwise set to empty string
                    if os.listdir(self.preset_path):
                        new_preset = self.get_preset_list()[0]
                    else:
                        new_preset = ''

                    # Delete all project presets using preset being deleted
                    if isinstance(project_files, list):
                        for path in project_files:
                            os.remove(path)

                    # Update UI and config file with new default preset
                    self.update_default_preset(new_preset) # Update preset name
                    self.update_ui() # Update UI with new default preset
                    self.message_print(f'Preset deleted: {preset_name}')
                    return
        else:
            print('No preset selected to delete.\n')

    # ---------------------------------------- #
    # Button Helper Functions
    # ---------------------------------------- #

    def create_or_edit_preset(self, preset_path: str=None, preset_config: PyFlameConfig=None) -> None:
        """
        Create or Edit Preset
        =====================

        Creates a new preset or edits an existing one.

        Create a new preset or the modification of an existing one.
        Hides the preset window during the modification process, then loads the setup window
        to allow users to modify preset settings. After the modification is complete, it updates
        the UI and returns the name of the modified or newly created preset.

        Args:
        -----
            `preset_path` (str, optional):
                The path to the existing preset JSON file. If provided, the function will edit the preset located at this path. Defaults to None.

            `preset_config` (PyFlameConfig, optional): An instance of PyFlameConfig representing the existing preset
                configuration.
                (Default: `None`)

        Returns:
        --------
            str or None: The name of the modified or newly created preset, if successful. Returns None if the
            preset modification or creation process is canceled.

        Raises:
        -------
            TypeError:
                If `new_preset.settings` is not a dictionary.

        Example:
        --------
            Creating a new preset:
            ```
            new_preset_name = self.create_or_edit_preset()
            ```

            Editing an existing preset:
            ```
            edited_preset_name = self.create_or_edit_preset(preset_path='/path/to/preset.json', preset_config=preset_config)
            ```
        """

        # Hide preset window while creating new preset
        self.preset_window.hide()

        # Load Setup window passing preset_config to load preset values.
        new_preset = self.setup_script(settings=preset_config)

        # Restore preset window after creating new preset
        self.preset_window.show()

        # If preset name is changed during edit, update all project presets using preset with new preset name
        if new_preset.settings:
            # Check to make sure new_preset.settings is returning a dictionary
            if not isinstance(new_preset.settings, dict):
                raise TypeError(f"PyFlamePresetManager: Expected 'new_preset.settings' to be a dictionary, got {type(new_preset.settings).__name__} instead.")

            # Remove old preset file if replacing preset
            if preset_path:
                os.remove(preset_path)

            # Get preset_name value from new_preset.settings dictionary
            new_preset_name = new_preset.settings['preset_name']

            new_default_preset_name = ''

            # If preset list is empty, set new preset as default preset
            if not self.get_preset_list() or new_preset_name == self.settings.default_preset:
                self.update_default_preset(new_preset_name)
                new_default_preset_name += self.default_preset_extension

            # Save new preset to file
            PyFlameConfig(
                config_values=new_preset.settings,
                config_path=os.path.join(os.path.join(self.script_path, 'config', 'presets'), new_preset_name + '.json'),
                script_name=self.script_name,
                )

            # Update UI with new preset name
            self.update_ui()

            if new_default_preset_name:
                self.current_preset_menu_pushbutton.setText(new_preset_name + new_default_preset_name)
            else:
                self.current_preset_menu_pushbutton.setText(new_preset_name)

            return new_preset_name

        else:
            return None

    def create_project_preset_json(self, preset_name: str, preset_path: str) -> None:
        """
        Create Project Preset JSON
        ==========================

        Creates a new project preset JSON file with the specified preset name.

        Args:
        -----
            `preset_name (str)`:
                The name of the preset.

            `preset_path (str)`:
                The path to the project preset JSON file.
        """

        # Create project preset as a dictionary
        preset_json = {
                "preset_name": preset_name
            }

        # Create or overwrite the preset file with JSON content
        with open(preset_path, 'w') as json_file:
            json.dump(preset_json, json_file, indent=4)
            print(f"Preset file created at {preset_path}")

        # Update and save new preset file with current preset name
        self.preset_json_save_preset_name(preset_path, preset_name)

    def update_project_presets(self, old_preset_name: str, new_preset_name: str):
        """
        Update Project Presets
        ======================

        This function iterates through all project presets in the project config path. If it finds a project preset with the old preset name,
        it updates the project preset to use the new preset name.

        Args:
        -----
            `old_preset_name (str)`:
                The name of the preset to be replaced.

            `new_preset_name (str)`:
                The new name of the preset.
        """

        self.message_print(f'Updating project presets to new preset name: {new_preset_name}')

        for project_preset_json in os.listdir(self.project_config_path):
            project_preset_json_path = os.path.join(self.project_config_path, project_preset_json)
            project_preset_name = self.get_project_preset_name_json(project_preset_json_path)
            if project_preset_name == old_preset_name:
                self.preset_json_save_preset_name(project_preset_json_path, new_preset_name)

        self.message_print(f'Updated project presets to new preset name: {new_preset_name}')

    def get_project_preset_name_json(self, project_preset_path: str) -> str:
        """
        Get Project Preset Name JSON
        ============================

        Get name of preset from project preset JSON file.

        Args:
        -----
            `project_preset_path (str)`:
                Path to project preset JSON file.
        """

        # Load the JSON file
        with open(project_preset_path, 'r') as json_file:
            data = json.load(json_file)

        # Extract the preset name
        preset_name = data.get("preset_name", None)

        return preset_name

    def get_preset_list(self) -> List[str]:
        """
        Get Preset List
        ===============

        Builds list of presets from preset folder.
        Adds (Default) to the end of the default preset name.
        Sorts list alphabetically.

        Returns:
        --------
            `preset_list (List[str])`:
                List of preset names.
        """

        try:
            presets = [file[:-5] for file in os.listdir(self.preset_path)]
            if self.settings.default_preset in presets:
                default_index = presets.index(self.settings.default_preset)
                presets[default_index] += self.default_preset_extension
        except Exception as e:
            print(f"Error listing presets: {e}")
            return []
        else:
            presets.sort()
            return presets

    def update_ui(self) -> None:
        """
        Update UI
        =========

        Updates Preset Manager UI based on the current preset settings.

        This function updates UI elements such as the Current Project Preset field, Current Preset button, and Preset list
        based on the current preset settings. It checks if a project preset exists for the current project. If a project preset
        exists, it uses that preset. If no project preset exists, it uses the default preset. If no default preset exists, it
        uses the first preset in the list of available presets. If no presets exist, the Current Project Preset field will
        display 'No saved presets found.'
        """

        def get_project_preset_name() -> str:
            """
            Checks for an existing project preset and returns its name.

            Returns:
                str: The name of the project preset if found, else None.
            """

            print('PROJECT NAME:', self.flame_prj_name)

            print('list dir:', os.listdir(self.project_config_path))

            # Check for existing project preset in project preset folder
            try:
                project_preset = [f[:-5] for f in os.listdir(self.project_config_path) if f[:-5] == self.flame_prj_name][0]
            except:
                project_preset = False

            # If project preset is found, get preset name from project preset file. Else return None.
            if project_preset:
                project_preset_path = os.path.join(self.project_config_path, project_preset + '.json')
                preset_name = self.get_project_preset_name_json(project_preset_path) # Get preset name from project preset JSON file
                preset_path = os.path.join(self.preset_path, preset_name + '.json')

                # If preset exists, return preset name adding (Default) if preset is default preset.
                # Else preset does not exist, delete project preset JSON and return None.
                if os.path.isfile(preset_path):
                    # If preset name is the default preset, add (Default) to the end of the name
                    if preset_name == self.settings.default_preset:
                        preset_name = preset_name + self.default_preset_extension
                    return preset_name
                else:
                    os.remove(project_preset_path) # Delete project preset JSON file
                    return None
            else:
                return None

        def update_buttons() -> None:
            """
            Update which buttons are enabled or disabled based on current preset field.
            """

            # Get text from current project preset field
            current_preset = self.current_project_preset_field.text()

            # If 'No saved presets found.' is in current preset field, disable buttons
            if current_preset == 'No saved presets found.':
                self.set_as_default_button.setEnabled(False)
                self.edit_button.setEnabled(False)
                self.set_project_preset_button.setEnabled(False)
                self.remove_from_project_button.setEnabled(False)
                self.delete_button.setEnabled(False)
                self.duplicate_button.setEnabled(False)
            else:
                self.set_as_default_button.setEnabled(True)
                self.edit_button.setEnabled(True)
                self.set_project_preset_button.setEnabled(True)
                self.delete_button.setEnabled(True)
                self.duplicate_button.setEnabled(True)

            # If ' (Project)' is not in current preset field, disable remove project preset button
            if not current_preset.endswith(self.project_preset_extension):
                self.remove_from_project_button.setEnabled(False)
            else:
                self.remove_from_project_button.setEnabled(True)

        self.message_print('Updating Preset Manager UI...')

        # Get list of existing presets
        existing_presets = self.get_preset_list()
        #print('EXISTING PRESETS:', existing_presets, '\n')

        # Check for to see if a project preset is set for current project
        preset = get_project_preset_name()
        if preset:
            new_preset_name = preset + self.project_preset_extension
            #print('NEW PRESET NAME:', new_preset_name, '\n')
            if new_preset_name.endswith(' (Default) (Project)'):
                new_preset_name = new_preset_name.replace(' (Default) (Project)', ' (Project)')
            # Add project preset extension to preset name in existing presets list
            if preset in existing_presets:
                existing_presets[existing_presets.index(preset)] = new_preset_name
            # Add project preset extension to preset name
            preset = new_preset_name
            #print('Project Preset:', preset, '\n')

        # If no project preset exists, try using the default preset, else set to first preset in list, if it exists, else set to 'No saved presets found.'
        else:
            preset = self.settings.default_preset
            if os.path.isfile(os.path.join(self.preset_path, preset + '.json')):
                preset = preset + self.default_preset_extension
            else:
                presets = existing_presets
                if presets:
                    preset = presets[0]
                    self.update_default_preset(preset)
                else:
                    preset = 'No saved presets found.'
        #print('Current Project Preset:', preset, '\n')

        # Update current preset push button and current project preset field
        self.current_preset_menu_pushbutton.setText(preset)
        self.current_project_preset_field.setText(preset)
        self.current_preset_menu_pushbutton.update_menu(preset, existing_presets)

        # Update which buttons are enabled or disabled based on current preset field
        update_buttons()

        self.message_print('Preset Manager UI Updated.')

    def get_current_preset_button_name(self) -> str:
        """
        Get Current Preset Button Name
        ===============================

        Get current preset button text. Remove ' (Default)' or '( Project)' if it exists in name.

        Returns:
        --------
            current_preset (str): Current preset name.
        """

        # Get current preset name from push button
        current_preset = self.current_preset_menu_pushbutton.text()

        # Remove ' (Default)' or '( Project)' from preset name if it exists
        if current_preset.endswith(self.default_preset_extension):
            current_preset = current_preset[:-10]
        elif current_preset.endswith(self.project_preset_extension):
            current_preset = current_preset[:-9]
        current_preset = current_preset.strip()

        return current_preset

    def update_default_preset(self, new_default_preset: str) -> None:
        """
        Update Default Preset
        =====================

        Update default preset setting and write to config file.

        Args:
        -----
            `new_default_preset (str)`:
                New default preset name.
        """

        # Remove ' (Default)' from preset name if it exists
        if new_default_preset.endswith(self.default_preset_extension):
            new_default_preset = new_default_preset[:-10]
        #print('new_default_preset:', new_default_preset, '\n')

        # Update default preset setting
        self.settings.default_preset = new_default_preset

        # Update config file with new default preset
        self.save_config()

        print(f'--> Updated default preset to: {new_default_preset}')

    def preset_json_save_preset_name(self, preset_path: str, preset_name: str) -> None:
        """
        Preset JSON Save Preset Name
        ============================

        Add preset name to project preset JSON file.

        Args:
        -----
            `preset_path (str)`:
                Path to project preset JSON file.

            `preset_name (str)`:
                Name of preset.
        """

        # Read the JSON file
        with open(preset_path, 'r') as file:
            data = json.load(file)

        # Update the preset_name field
        data['preset_name'] = preset_name

        # Write the updated data back to the JSON file
        with open(preset_path, 'w') as file:
            json.dump(data, file, indent=4)

    # ---------------------------------------- #
    # Public Methods
    # ---------------------------------------- #

    def load_preset(self) -> PyFlameConfig:
        """
        Load Preset
        ===========

        Load preset from preset JSON file and return settings.

        Returns:
        --------
            settings: With preset values as attributes.
        """

        def get_project_preset() -> str:
            """
            Check for project preset. If found, return project preset path.

            Returns:
            --------
                project_preset (str):
                    Path to project preset JSON file.
            """

            print('Checking for project preset...')

            try:
                project_preset_list = [f[:-5] for f in os.listdir(self.project_config_path)]
            except:
                project_preset_list = []
            print('Project Preset List:', project_preset_list, '\n')

            if self.flame_prj_name in project_preset_list:
                # Get project preset name from project preset JSON file
                project_preset = os.path.join(self.project_config_path, self.flame_prj_name + '.json')
                project_preset_name = self.get_project_preset_name_json(project_preset)
                # Get path to preset set as project preset
                project_preset = os.path.join(self.preset_path, project_preset_name + '.json')
                print('Project Preset found:', project_preset)
            else:
                project_preset = None
                print('No Project Preset found.')

            return project_preset

        def get_default_preset() -> str:
            """
            Check for default preset. If found, return preset path.

            Returns:
            --------
                default_preset (str):
                    Path to default preset JSON file.
            """

            print('Checking for default preset...')

            # Get list of existing presets
            existing_presets = self.get_preset_list()

            if self.settings.default_preset:
                default_preset = os.path.join(self.preset_path, self.settings.default_preset + '.json')
                print('Default Preset found:', default_preset, '\n')
            elif existing_presets:
                default_preset = os.path.join(self.preset_path, existing_presets[0] + '.json')
                print('Default Preset not set, using first preset found:', default_preset, '\n')
            else:
                print('No Default Preset found.\n')
                default_preset = None

            return default_preset

        print('Loading preset...')

        # Check for project preset JSON file
        preset_path = get_project_preset()

        # if no project preset is found, use default preset
        if not preset_path:
            preset_path = get_default_preset()

        # if no default preset is found, give message to create new preset in script setup.
        if not preset_path:
            #print('No presets found. Open setup window to create new preset.\n')
            self.info_message('No presets found.\n\nGo to script setup to create new preset.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Uber Save Setup')
            return

        settings = PyFlameConfig(
            config_values=PyFlameConfig.get_config_values(config_path=preset_path),
            config_path=preset_path,
            script_name=self.script_name,
            )

        return settings

#-------------------------------------
# [PyFlame Window Classes]
#-------------------------------------

class PyFlameInputDialog():
    """
    PyFlameInputDialog
    ==================

    Custom QT Flame Input Dialog

    Simple dialog window thatprompts the user for text input and provides options to confirm or cancel.

    Args:
    -----
        `text` (str):
            Text displayed above input field.
            (Default: `Enter New Value`)

        `input_text` (str, optional):
            Text displayed in input field.
            (Default: `None`)

        `title` (str, optional):
            Provide a custom title for the dialog window.
            (Default: `User Input`)

        `title_style` (Style, optional):
            The style of the title text using the Style Enum.
            (Default: `Style.BACKGROUND`)

        `line_color` (Color, optional):
            The color of the line using the Color Enum.
            (Default: `Color.BLUE`)

    Example:
    --------
        ```
        input_dialog = PyFlameInputDialog(text="Enter your name:", input_text="John Doe")
        user_input, confirmed = input_dialog.get_text()

        if confirmed:
            print(f"User entered: {user_input}")
        else:
            print("User cancelled input.")
        ```
    """

    def __init__(self: 'PyFlameInputDialog',
                 text: str='Enter New Value',
                 input_text: Optional[str] = None,
                 title: str='User Input',
                 title_style: Style=Style.BACKGROUND_THIN,
                 line_color: Color=Color.BLUE,
                 ):
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate arguments, raise TypeError if any arguments are invalid.
            """

            if text is not None and not isinstance(text, str):
                pyflame.raise_type_error(f'PyFlameInputDialog', 'text', 'string or None', text)
            if input_text is not None and not isinstance(input_text, str):
                pyflame.raise_type_error(f'PyFlameInputDialog', 'input_text', 'string or None', input_text)
            if title is not None and not isinstance(title, str):
                pyflame.raise_type_error(f'PyFlameInputDialog', 'title', 'string or None', title)
            if title_style is not None and not isinstance(title_style, Style):
                pyflame.raise_type_error(f'PyFlameInputDialog', 'title_style', 'Style Enum or None', title_style)
            if line_color is not None and not isinstance(line_color, Color):
                pyflame.raise_type_error(f'PyFlameInputDialog', 'line_color', 'Color Enum or None', line_color)

        validate_arguments()

        self.ok = False
        if input_text is None:
            input_text = ''
        self.input_text = input_text

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.input_window = PyFlameDialogWindow(
            title=title,
            title_style=title_style,
            line_color=line_color,
            return_pressed=self._confirm,
            grid_layout_columns=4,
            grid_layout_rows=3,
            grid_layout_column_width=110,
            )

        # Label
        self.input_label = PyFlameLabel(
            text=text,
            style=Style.UNDERLINE,
            )

        # Entry
        self.input_entry = PyFlameEntry(
            text=input_text,
            )

        # Buttons
        self.ok_button = PyFlameButton(
            text='Ok',
            connect=self._confirm,
            width=110,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self._cancel,
            width=110,
            )

        self.input_window.grid_layout.addWidget(self.input_label, 0, 0, 1, 4)
        self.input_window.grid_layout.addWidget(self.input_entry, 1, 0, 1, 4)
        self.input_window.grid_layout.addWidget(self.cancel_button, 3, 2)
        self.input_window.grid_layout.addWidget(self.ok_button, 3, 3)

        #-------------------------------------

        # Set input entry focus
        self.input_entry.setFocus()

        # Print to terminal/shell
        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'User Input: {TextColor.WHITE.value}{SCRIPT_NAME.upper()}{TextColor.BLUE.value}' + '\n' +
            '=' * 80 + '\n\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

        self.input_window.exec_()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def get_text(self):
        """
        Get Text
        ========

        Returns the text entered by the user and whether they confirmed or cancelled the dialog.

        Returns:
        --------
            tuple[str, bool]: A tuple containing:
                The text entered by the user (str), or None if cancelled.
                Whether the user confirmed (True) or cancelled (False).
        """

        pyflame.print(f'User Input: {self.input_text}', text_color=TextColor.GREEN)

        return self.input_text, self.ok

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _confirm(self):
        """
        Confirm
        =======

        Called when the user presses OK. Stores the input and sets `self.ok = True`.
        """

        self.ok = True
        self.input_text = self.input_entry.text()
        self.input_window.close()

    def _cancel(self):
        """
        Cancel
        ======

        Called when the user presses Cancel. Sets `self.ok = False`.
        """

        self.ok = False
        self.input_text = None
        self.input_window.close()
        pyflame.print('Input Cancelled', text_color=TextColor.RED)

class PyFlameMessageWindow():
    """
    PyFlameMessageWindow
    ====================

    Custom QT Flame Message Window.

    Messsage window to display various types of messages.

    Args:
    -----
        `message` (str):
            Text displayed in the body of the window.

        `type` (MessageType):
            Type of message window to be shown. See Message Types below.
            (Default: `MessageType.INFO`)

        `title` (str, optional):
            Use to override default title for message type.
            (Default: `None`)

        `title_style` (Style, optional):
            The style of the title text.
            (Default: `Style.BACKGROUND`)

        `script_name` (str, optional):
            Name of script. Used to set window title.
            (Default: `SCRIPT_NAME`)

        `time` (int):
            Time in seconds to display message in flame message area.
            (Default: `3`)

        `parent` (QtWidget, optional):
            Parent window.
            (Default: `None`)

    Message Types:
    --------------
        - `MessageType.INFO`:
            - Title: SCRIPT_NAME
            - Title with no script_name: Python Hook
            - Window lines: Blue
            - Buttons: Ok
        - `MessageType.OPERATION_COMPLETE`:
            - Title: SCRIPT_NAME: Operation Complete
            - Title with no script_name: Python Hook: Operation Complete
            - Window lines: Blue
            - Buttons: Ok
        - `MessageType.CONFIRM`:
            - Title: SCRIPT_NAME: Confirm Operation
            - Title with no script_name: Python Hook: Confirm Operation
            - Window lines: Grey
            - Buttons: Confirm, Cancel
            - Returns bool value.
        - `MessageType.ERROR`:
            - Title: SCRIPT_NAME: Error
            - Title with no script_name: Python Hook: Error
            - Window lines: Yellow
            - Buttons: Ok
        - `MessageType.WARNING`:
            - Title: SCRIPT_NAME: Warning
            - Title with no script_name: Python Hook: Warning
            - Window lines: Red
            - Buttons: Confirm, Cancel
            - Returns bool value.

    Returns:
    --------
        bool: True if confirm button is pressed, False if cancel button is pressed.
              A bool value is only returned for `MessageType.CONFIRM` and `MessageType.WARNING`.

    Examples:
    ---------
        Example for an error message:
        ```
        PyFlameMessageWindow(
            message=(
                'File not found.'
                ),
            type=MessageType.ERROR,
            )
        ```

        Example for a confirmation message, returns a bool:
        ```
        proceed = PyFlameMessageWindow(
            message='Do you want to do this?',
            type=MessageType.CONFIRM,
            )
        ```
    """

    def __init__(self: 'PyFlameMessageWindow',
                 message: str,
                 type: MessageType=MessageType.INFO,
                 title: Optional[str]=None,
                 title_style: Style=Style.BACKGROUND_THIN,
                 script_name: str=SCRIPT_NAME,
                 time: int=5,
                 parent=None
                 ):
        super().__init__()

        # Validate argument types
        if not isinstance(message, str):
            raise TypeError('PyFlameMessageWindow: message must be a string.')
        if script_name is not None and not isinstance(script_name, str):
            raise TypeError('PyFlameMessageWindow: script_name must be a string or None.')
        if not isinstance(type, MessageType):
            raise ValueError('PyFlameMessageWindow: type must be an instance of Type Enum: '
                            'MessageType.INFO, MessageType.OPERATION_COMPLETE, MessageType.CONFIRM, MessageType.ERROR, '
                            'MessageType.WARNING.')
        if title is not None and not isinstance(title, str):
            raise TypeError('PyFlameMessageWindow: title must be a string or None.')
        if not isinstance(time, int):
            raise TypeError('PyFlameMessageWindow: time must be an integer.')

        self.type = type
        self.confirmed = False

        # Set message window type options
        if type == MessageType.INFO:
            line_color = Color.BLUE
            if not title:
                title = script_name
        elif type == MessageType.OPERATION_COMPLETE:
            line_color = Color.BLUE
            if not title:
                title = f'{script_name}: Operation Complete'
        elif type == MessageType.ERROR:
            line_color = Color.YELLOW
            if not title:
                title = f'{script_name}: Error'
        elif type == MessageType.CONFIRM:
            line_color = Color.BLUE
            if not title:
                title = f'{script_name}: Confirm Operation'
        elif type == MessageType.WARNING:
            line_color = Color.RED
            if not title:
                title = f'{script_name}: Warning'

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.message_window = PyFlameDialogWindow(
            title=title,
            title_style=title_style,
            line_color=line_color,
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=110,
            )

        self.text = PyFlameTextEdit(
            text=message,
            message_window=True,
            )

        if type == MessageType.CONFIRM or type == MessageType.WARNING:
            self.cancel_button = PyFlameButton(
                text='Cancel',
                connect=self.cancel,
                width=110,
                )
            self.confirm_button = PyFlameButton(
                text='Confirm',
                connect=self.confirm,
                width=110,
                color=Color.BLUE,
                )

            if type == MessageType.CONFIRM:
                self.confirm_button.setText = 'Confirm'
            elif type == MessageType.WARNING:
                self.confirm_button.set_button_color(Color.RED)

            self.message_window.grid_layout.addWidget(self.text, 0, 0, 6, 4)
            self.message_window.grid_layout.addWidget(self.cancel_button, 7, 2)
            self.message_window.grid_layout.addWidget(self.confirm_button, 7, 3)
        else:
            self.ok_button = PyFlameButton(
                text='Ok',
                connect=self.confirm,
                width=110,
                color=Color.BLUE,
                )
            self.message_window.grid_layout.addWidget(self.text, 0, 0, 6, 4)
            self.message_window.grid_layout.addWidget(self.ok_button, 7, 3)

        self._print(message, title, time) # Print message to terminal and Flame's console area

        self.message_window.exec_()

    def __bool__(self):
        return self.confirmed

    def _print(self, message: str, title: str, time: int):
        """
        Print
        =====

        Private method to print to the terminal/shell and Flame's console area.

        Notes:
        ------
            This method is intended for internal use only and should not be called directly.
        """

        def print_message(color_code: str, message_type: str, message: str):
            print(
                f'{color_code}' + # Set text color
                '=' * 80 + '\n' +
                f'{message_type}: {TextColor.WHITE.value}{SCRIPT_NAME.upper()}{color_code}' + '\n' +
                '=' * 80 + '\n\n' +
                f'{TextColor.WHITE.value}' + # Set text color
                f'{message}\n\n' +
                f'{color_code}' + # Set text color
                '-' * 80 + '\n'
                f'{TextColor.RESET.value}'  # Reset text color
                )

        # Print to terminal/shell
        if self.type == MessageType.INFO or self.type == MessageType.OPERATION_COMPLETE or self.type == MessageType.CONFIRM:
            print_message(TextColor.BLUE.value, 'Info', message)
        elif self.type == MessageType.WARNING:
            print_message(TextColor.RED.value, 'Warning', message)
        elif self.type == MessageType.ERROR:
            print_message(TextColor.YELLOW.value, 'Error', message)

        # Print message to the Flame message area - only works in Flame 2023.1 and later
        # Warning and error intentionally swapped to match color of message window
        title = title.upper()

        if self.type == MessageType.INFO or self.type == MessageType.OPERATION_COMPLETE or self.type == MessageType.CONFIRM:
            flame.messages.show_in_console(f'{title}: {message}', 'info', time)
        elif self.type == MessageType.ERROR:
            flame.messages.show_in_console(f'{title}: {message}', 'warning', time)
        elif self.type == MessageType.WARNING:
            flame.messages.show_in_console(f'{title}: {message}', 'error', time)

    def cancel(self):

        self.message_window.close()
        self.confirmed = False

        pyflame.print('Operation Cancelled', text_color=TextColor.RED)

    def confirm(self):
        self.message_window.close()
        self.confirmed = True
        if self.type == MessageType.CONFIRM or self.type == MessageType.WARNING:
            pyflame.print('Operation Confirmed', text_color=TextColor.GREEN)

class PyFlamePasswordWindow():
    """
    PyFlamePasswordWindow
    =====================

    Custom Qt Flame Password Window.

    This class provides a custom dialog window for entering a password or a username and password.

    Args:
    -----
        `message` (str):
            The message to be displayed in the window.

        `title` (str, optional):
            The title text shown in the top left of the window. If set to None, the default title of either
            'Enter Password' or 'Enter Username and Password' will be used based on `user_name_prompt` argument.
            (Default: `None`)

        `title_style` (Style, optional):
            The style of the title text.
            (Default: `Style.BACKGROUND`)

        `user_name_prompt` (bool):
            If set to True, the window will prompt for both username and password.
            (Default: `False`)

    Methods:
    --------
        `password` -> Optional[Union[str, bool]]:
            Returns the entered password as a string or None if no password was entered.

        `username_password` -> Tuple[Optional[str], Optional[str]]:
            Returns the entered username and password as a tuple or (None, None) if no username or password was entered.

    Notes:
    ------
        For messages with multiple lines, use triple quotes for message text.

    Examples:
    ---------
        For a password prompt:
        ```
        password_window = PyFlamePasswordWindow(
            message=f'System password needed to install {SCRIPT_NAME}.',
            )

        # Get password
        password = password_window.password()
        ```

        For a username and password prompt:
        ```
        password_window = PyFlamePasswordWindow(
            message='Enter username and password.',
            user_name_prompt=True,
            )

        # Get username and password
        username, password = password_window.username_password()
        ```
    """

    def __init__(self: 'PyFlamePasswordWindow',
                 message: str,
                 title: Optional[str]=None,
                 title_style: Style=Style.BACKGROUND_THIN,
                 user_name_prompt: bool=False,
                 ):
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(message, str):
                pyflame.raise_type_error('PyFlamePasswordWindow', 'message', 'string', message)
            if title is not None and not isinstance(title, str):
                pyflame.raise_type_error('PyFlamePasswordWindow', 'title', 'string', title)
            if not isinstance(title_style, Style):
                pyflame.raise_type_error('PyFlamePasswordWindow', 'title_style', 'Style Enum', title_style)
            if not isinstance(user_name_prompt, bool):
                pyflame.raise_type_error('PyFlamePasswordWindow', 'user_name_prompt', 'boolean', user_name_prompt)

        validate_arguments()

        # Set window title if set to None
        if not title and user_name_prompt:
            title = 'Enter Username and Password'
        elif not title and not user_name_prompt:
            title = 'Enter Password'

        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{title}' + '\n' +
            '=' * 80 + '\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

        self.user_name_prompt = user_name_prompt
        self.username_value = ''
        self.password_value = ''

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.password_window = PyFlameDialogWindow(
            title=title,
            title_style=title_style,
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=110,
            )

        self.text = PyFlameTextEdit(
            text=message,
            message_window=True,
            )

        self.password_label = PyFlameLabel(
            text='Password',
            )
        self.password_entry = PyFlameEntry(
            text='',
            )
        self.password_entry.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_entry.returnPressed.connect(self._set_password)

        if user_name_prompt:
            self.username_label = PyFlameLabel(
                text='Username',
                )
            self.username_entry = PyFlameEntry(
                text='',
                )
            self.username_entry.returnPressed.connect(self._set_username_password)
            self.confirm_button = PyFlameButton(
                text='Confirm',
                connect=self._set_username_password,
                color=Color.BLUE,
                )
        else:
            self.confirm_button = PyFlameButton(
                text='Confirm',
                connect=self._set_password,
                color=Color.BLUE,
                )

        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self._cancel,
            )

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.password_window.grid_layout.addWidget(self.text, 0, 0, 3, 4)

        if user_name_prompt:
            self.password_window.grid_layout.addWidget(self.username_label, 3, 0)
            self.password_window.grid_layout.addWidget(self.username_entry, 3, 1, 1, 3)
            self.password_window.grid_layout.addWidget(self.password_label, 4, 0)
            self.password_window.grid_layout.addWidget(self.password_entry, 4, 1, 1, 3)
        else:
            self.password_window.grid_layout.addWidget(self.password_label, 3, 0)
            self.password_window.grid_layout.addWidget(self.password_entry, 3, 1, 1, 3)


        self.password_window.grid_layout.addWidget(self.cancel_button, 6, 2)
        self.password_window.grid_layout.addWidget(self.confirm_button, 6, 3)

        # Set entry focus
        if user_name_prompt:
            self.username_entry.setFocus()
        else:
            self.password_entry.setFocus()

        self.password_window.exec_()

    def _cancel(self):
        """
        Cancel
        ======

        Close window and return False when cancel button is pressed.
        """

        self.password_window.close()

        if self.user_name_prompt:
            pyflame.print('Username and Password Cancelled', text_color=TextColor.RED)
        else:
            pyflame.print('Password Cancelled', text_color=TextColor.RED)

        return False

    def _set_username_password(self):
        """
        Set Username and Password
        =========================

        Set the username and password values and close the window.
        """

        if self.password_entry.text() and self.username_entry.text():
            self.username_value = self.username_entry.text()
            self.password_value = self.password_entry.text()
            self.password_window.close()
            return

    def _set_password(self):
        """
        Set Password
        ============

        Set the password value, test it, and close the window.
        If the password is incorrect, the user will be prompted to try again.
        """

        password = self.password_entry.text()

        if password:
            command = ['sudo', '-S', 'echo', 'Testing sudo password']
            try:
                # Run the command with sudo and pass the password through stdin
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, error = process.communicate(input=password+'\n')

                if process.returncode == 0:
                    print('Sudo password is correct.\n')
                    self.password_value = self.password_entry.text()
                    self.password_window.close()
                    return
                else:
                    print('Sudo password is incorrect.')
                    self.text.setText('Password incorrect, try again.')
            except Exception as e:
                print('Error occurred while testing sudo password:', str(e))

    def password(self) -> Optional[str]:
        """
        Password
        ========

        Returns the entered password as a string or None if no password was entered.

        Returns:
        --------
            password (str):
                The entered password as a string.

        Examples:
        ---------
            To get the entered password:
            ```
            password = password_window.password()
            ```
        """

        if self.password_value:
            return self.password_value
        return None

    def username_password(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Username Password
        =================

        Returns the entered username and password as a tuple or (None, None) if no username or password was entered.

        Returns:
        --------
            Tuple[Optional[str], Optional[str]]:
                Username and password as a tuple.

        Examples:
        ---------
            To get the entered username and password:
            ```
            username, password = password_window.username_password()
            ```
        """

        if self.username_value and self.password_value:
            return self.username_value, self.password_value
        return None, None

class PyFlameProgressWindow():
    """
    PyFlameProgressWindow
    =====================

    Custom QT Flame Progress Window

    Args:
    -----
        `num_to_do` (int):
            Total number of operations to do.

        `title` (str, optional):
            text shown in top left of window ie. Rendering...
            (Default: `Processing...`)

        `title_underline` (bool, optional):
            If True, underline title text.
            (Default: `False`)

        `text` (str, optional): message to show in window.
            (Default: `None`)

        `line_color` (WindowBarColor):
            Color of bar on left side of window.
            (Default: `Color.BLUE`)

            Color Options:
            --------------
            `Color.GRAY`: For gray line.
            `Color.BLUE`: For blue line.
            `Color.RED`: For red line.
            `Color.GREEN`: For green line.
            `Color.YELLOW`: For yellow line.
            `Color.TEAL`: For teal line.

        `enable_done_button` (bool):
            Enable/Disable done button,
            (Default: `False`)

    Methods:
    --------
        `set_progress_value(int)`:
            Set progress bar value.

        `enable_done_button(bool)`:
            Enable or disable done button.

        `set_text(str)`:
            Set text in window.

    Notes:
    ------
        For text with multiple lines, use triple quotes.

    Examples:
    ---------
        To create progress bar window:
        ```
        progress_window = PyFlameProgressWindow(
            num_to_do=10,
            title='Rendering...',
            text='Rendering: Batch 1 of 5',
            enable_done_button=True,
            )
        ```

        To update progress bar progress value:
        ```
        progress_window.set_progress_value(5)
        ```

        To update text in window:
        ```
        progress_window.set_text('Rendering: Batch 2 of 5')
        ```

        To enable or disable done button - True or False:
        ```
        progress_window.enable_done_button(True)
        ```

        To set the title text:
        ```
        progress_window.set_title_text('Render Completed')
        ```
    """

    def __init__(self: 'PyFlameProgressWindow',
                 num_to_do: int,
                 title: str='Processing...',
                 title_style: Style=Style.BACKGROUND_THIN,
                 text: str='',
                 line_color: Color=Color.BLUE,
                 enable_done_button: bool=False,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(num_to_do, int):
                pyflame.raise_type_error('PyFlameProgressWindow', 'num_to_do', 'integer', num_to_do)
            if title is not None and not isinstance(title, str):
                pyflame.raise_type_error('PyFlameProgressWindow', 'title', 'string', title)
            if not isinstance(title_style, Style):
                pyflame.raise_type_error('PyFlameProgressWindow', 'title_style', 'Style Enum', title_style)
            if not isinstance(text, str):
                pyflame.raise_type_error('PyFlameProgressWindow', 'text', 'string', text)
            if not isinstance(line_color, Color):
                pyflame.raise_type_error('PyFlameProgressWindow', 'line_color', 'Color Enum', line_color)
            if not isinstance(enable_done_button, bool):
                pyflame.raise_type_error('PyFlameProgressWindow', 'enable_done_button', 'boolean', enable_done_button)

        validate_arguments()

        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{TextColor.WHITE.value}' + # Set text color
            f'{title}' + '\n' +
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

        self.num_to_do = num_to_do

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.progress_window = PyFlameDialogWindow(
            title=title,
            title_style=title_style,
            grid_layout_columns=4,
            grid_layout_rows=8,
            grid_layout_column_width=110,
            )

        self.text = PyFlameTextEdit(
            text=text,
            message_window=True,
            )

        # Progress bar
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximum(num_to_do)
        self.progress_bar.setMaximumHeight(pyflame.gui_resize(5))
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar{{
                color: {Color.TEXT.value};
                background-color: rgb(45, 45, 45);
                border: none;
                }}
            QProgressBar:chunk{{
                background-color: {Color.BLUE.value};
                }}
            """)

        self.done_button = PyFlameButton(
            text='Done',
            connect=self.progress_window.close,
            color=Color.BLUE,
            )
        self.done_button.setEnabled(enable_done_button)

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.progress_window.grid_layout.addWidget(self.text, 0, 0, 6, 4)
        self.progress_window.grid_layout.addWidget(self.progress_bar, 6, 0, 1, 4)
        self.progress_window.grid_layout.addWidget(self.done_button, 8, 3)

        #self.progress_window.exec_()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def set_text(self, text: str) -> None:
        """
        Set Text
        ========

        Use to set the text of the message text edit widget to the specified text.

        Args:
        -----
            `text` (str):
                The text to set in the message text edit widget.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Example:
        ---------
            To set the text in the progress window:
            ```
            self.progress_window.set_text('Rendering: Batch 2 of 5')
            ```
        """

        # Validate argument type
        if not isinstance(text, str):
            pyflame.raise_type_error('PyFlameProgressWindow', 'text', 'string', text)

        # Set progress window text
        self.text.setText(text)

    def set_title_text(self, text: str) -> None:
        """
        Set Title Text
        ==============

        Set the title text of the progress window.

        Used to change the title of the progress window after it has been created or when task is completed.

        Args:
        -----
            text (str):
                Text to display in the title of the progress window.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Examples:
        ---------
            To set the title text:
            ```
            progress_window.set_title_text('Render Completed')
            ```
        """

        # Validate argument type
        if not isinstance(text, str):
            pyflame.raise_type_error('PyFlameProgressWindow', 'text', 'string', text)

        # Set progress window title text
        self.progress_window.set_title_text(text)

    def set_num_to_do(self, num_to_do: int) -> None:
        """
        Set Number to Do
        =================

        Use to set the number of operations to do.
        """

        # Validate argument type
        if not isinstance(num_to_do, int):
            pyflame.raise_type_error('PyFlameProgressWindow', 'num_to_do', 'integer', num_to_do)

        # Set number of operations to do
        self.num_to_do = num_to_do

    def set_progress_value(self, value: int) -> None:
        """
        Set Progress Value
        ==================

        Use to set the progress value of the progress bar.

        Args:
        -----
            `value` (int):
                The value to set the progress bar to.

        Raises:
        -------
            TypeError:
                If `value` is not an integer.

        Examples:
        ---------
            To set the progress bar to 5:
            ```
            self.progress_window.set_progress_value(5)
            ```
        """

        # Validate argument type
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressWindow', 'value', 'integer', value)

        # Set progress bar value
        self.progress_bar.setValue(value)
        QtWidgets.QApplication.processEvents()

        # Enable Done button if progress bar value equals num_to_do(completed)
        if value == self.num_to_do:
            self.done_button.setEnabled(True)

    def enable_done_button(self, value: bool) -> None:
        """
        Enable Done Button
        ==================

        Use to enable or disable the done button.

        Args:
        -----
            `value` (bool):
                True to enable done button, False to disable done button.

        Raises:
        -------
            TypeError:
                If `value` is not a boolean.

        Examples:
        ---------
            To enable done button:
            ```
            self.progress_window.enable_done_button(True)
            ```
        """

        # Validate argument type
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameProgressWindow', 'value', 'boolean', value)

        # Enable or disable done button
        if value:
            self.done_button.setEnabled(True)
        else:
            self.done_button.setEnabled(False)

class PyFlameDialogWindow(QtWidgets.QDialog):
    """
    PyFlameDialogWindow
    ===================

    Custom QT Flame Dialog Window Widget

    Args:
    -----
        `title` (str):
            Text displayed in top left corner of window.
            (Default: `Python Script`)

        `title_style` (Style):
            Style of title text. Use Style Enum to set style.
            (Default: `Style.BACKGROUND`)

            Style Options:
            --------------
            `Style.BACKGROUND`: For background style.
            `Style.NORMAL`: For normal style.
            `Style.UNDERLINE`: For underline style.

        `width` (int, optional):
            Set minimum width of window.
            (Default: `150`)

        `height` (int, optional):
            Set minimum height of window.
            (Default: `30`)

        `line_color` (Color):
            Color of bar on left side of window.
            (Default: `Color.BLUE`)

            Color Options:
            --------------
            `Color.GRAY`: For gray line.
            `Color.BLUE`: For blue line.
            `Color.RED`: For red line.
            `Color.GREEN`: For green line.
            `Color.YELLOW`: For yellow line.
            `Color.TEAL`: For teal line.

        `return_pressed` (callable, optional):
            Function to be called when return key is pressed.
            (Default: `None`)

        `tab_width` (int):
            Set width of window tab labels.

        `tab_height` (int):
            Set height of of window tab labels.

        `grid_layout` (bool):
            Add grid layout to window.
            (Default: `True`)

        `grid_columns` (int):
            Number of columns in grid layout. Only used if `grid_layout` is `True`.
            (Default: `4`)

        `grid_rows` (int):
            Number of rows in grid layout. Only used if `grid_layout` is `True`.
            (Default: `3`)

        `parent` (QWidget, optional):
            Parent widget for the window.
            (Default: `None`)

    Methods:
    --------
        `add_layout(layout)`:
            Add layout to window.

    Example:
    --------
        To create a window:
        ```
        window = PyFlameDialogWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION},
            return_pressed=confirm,
            )
        ```

        To add a layout to the window:
        ```
        window.add_layout(layout)
        ```
    """

    def __init__(self: 'PyFlameDialogWindow',
                 title: str='Python Script',
                 title_style: Style=Style.BACKGROUND_THIN,
                 width: int=150,
                 height: int=30,
                 line_color: Color=Color.BLUE,
                 return_pressed: Optional[Callable]=None,
                 tab_width: int=150,
                 tab_height: int=24,
                 grid_layout: bool=True,
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: Optional[dict[int, int]]={},
                 grid_layout_adjust_row_heights: Optional[dict[int, int]]={},
                 parent: Optional[QtWidgets.QWidget]=None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(title, str):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'title', 'string', title)
            if not isinstance(title_style, Style):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'title_style', 'Style Enum', title_style)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'height', 'int', height)
            if width and not height:
                pyflame.raise_value_error(error_message='PyFlameDialogWindow: height must be set if width is set.')
            if height and not width:
                pyflame.raise_value_error(error_message='PyFlameDialogWindow: width must be set if height is set.')
            if not isinstance(line_color, Color):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'line_color', 'Color Enum', line_color)
            if return_pressed is not None and not callable(return_pressed):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'return_pressed', 'callable or None', return_pressed)
            if not isinstance(tab_width, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'tab_width', 'int', tab_width)
            if not isinstance(tab_height, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'tab_height', 'int', tab_height)
            if not isinstance(grid_layout, bool):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout', 'bool', grid_layout)
            if not isinstance(grid_layout_columns, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_columns', 'int', grid_layout_columns)
            if not isinstance(grid_layout_rows, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_rows', 'int', grid_layout_rows)
            if not isinstance(grid_layout_column_width, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_column_width', 'int', grid_layout_column_width)
            if not isinstance(grid_layout_row_height, int):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_row_height', 'int', grid_layout_row_height)
            if not isinstance(grid_layout_adjust_column_widths, dict):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_adjust_column_widths', 'dict', grid_layout_adjust_column_widths)
            if not isinstance(grid_layout_adjust_row_heights, dict):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'grid_layout_adjust_row_heights', 'dict', grid_layout_adjust_row_heights)
            if parent is not None and not isinstance(parent, QtWidgets.QWidget):
                pyflame.raise_type_error(f'PyFlameDialogWindow', 'parent', 'QWidget or None', parent)

        def center_window():
            """
            Center Window
            =============

            Center the window on the screen.
            """

            # Get Current Screen Resolution
            main_window_res = pyflamewin.main_window()
            resolution = main_window_res.screenGeometry()

            # Center Window on Screen
            self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

        validate_arguments()

        self.setFont(FONT)
        self.line_color = line_color # Being passed to _WindowSideLineOverlay
        self.return_pressed = return_pressed
        self.tab_width = pyflame.gui_resize(tab_width)
        self.tab_height = pyflame.gui_resize(tab_height)
        self.parent = parent

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Match title underline color to side line color with transparency
        if self.line_color == Color.BLUE:
            underline_color = Color.BLUE_TRANS
        elif self.line_color == Color.GRAY:
            underline_color = Color.GRAY_TRANS
        elif self.line_color == Color.RED:
            underline_color = Color.RED_TRANS
        elif self.line_color == Color.GREEN:
            underline_color = Color.GREEN_TRANS
        elif self.line_color == Color.YELLOW:
            underline_color = Color.YELLOW_TRANS
        elif self.line_color == Color.TEAL:
            underline_color = Color.TEAL_TRANS

        # Window title label
        self.title_label = PyFlameLabel(
            text='<span style="white-space: pre;">  ' + title, # Add space to title using CSS code. This pushes the title to the right one space.
            style=title_style,
            align=Align.LEFT,
            max_width=True,
            underline_color=underline_color,
            height=40,
            font_size=24,
            )

        # Window layout
        # -------------
        title_text_hbox = PyFlameHBoxLayout()
        title_text_hbox.addWidget(self.title_label)
        title_text_hbox.setContentsMargins(0, 0, 0, 0)  # Remove margins around the title label

        # Center layout - where main UI is added
        self.center_layout = PyFlameGridLayout()
        # Create widget to hold the center layout
        center_widget = QtWidgets.QWidget()
        center_widget.setLayout(self.center_layout)

        # Add the center layout to the main layout
        main_vbox2 = PyFlameVBoxLayout()
        main_vbox2.addWidget(center_widget, alignment=QtCore.Qt.AlignCenter)
        main_vbox2.addStretch()
        main_vbox2.setContentsMargins(15, 15, 15, 15) # Add margin around main UI

        main_vbox3 = PyFlameVBoxLayout()
        main_vbox3.addLayout(title_text_hbox)
        main_vbox3.addLayout(main_vbox2)
        main_vbox3.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.setLayout(main_vbox3)

        self._set_stylesheet()

        # Initialize and set up the overlay for blue line on left edge of window
        self.overlay = _WindowSideLineOverlay(self)

        # Create default grid layout if grid_layout is True
        if grid_layout:
            self.grid_layout = PyFlameGridLayout(
                columns=grid_layout_columns,
                rows=grid_layout_rows,
                column_width=grid_layout_column_width,
                row_height=grid_layout_row_height,
                adjust_column_widths=grid_layout_adjust_column_widths,
                adjust_row_heights=grid_layout_adjust_row_heights,
                )

            self.add_layout(self.grid_layout)
            self.show()

        self.setFixedSize(self.size())  # Lock current size

        # Center Window on Screen
        center_window()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_layout(self, layout):
        """
        Add Layout
        ==========

        Add widget layout to the main window.

        Args:
        -----
            layout (PyFlameLayout):
                Main widget layout to add to Main Window.

        Raises:
        -------
            TypeError:
                If `layout` is not a QLayout(PyFlameGridLayout, PyFlameVBoxLayout, PyFlameHBoxLayout).

        Example:
        --------
            ```
            layout = PyFlameGridLayout(
                columns=6,
                rows=5,
                column_width=150,
                row_height=28,
                )
            window.add_layout(layout)
            ```
        """

        # Validate argument type
        if not isinstance(layout, QtWidgets.QLayout):
            pyflame.raise_type_error(f'PyFlameWindow', 'layout', 'QLayout', layout)

        # Add layout to center layout
        self.center_layout.addLayout(layout, 0, 0)

    def set_title_text(self, text: str):
        """
        Set Title Text
        ==============

        Set the title of the window.

        Used to change the title of the window after it has been created.

        Args:
        -----
            text (str):
                Text to display in the title of the window.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Example:
        --------
            ```
            window.set_title_text('New Title')
            ```
        """

        # Validate argument type
        if not isinstance(text, str):
            raise TypeError('PyFlameDialogWindow: set_title_text must be called with a string.')

        # Set window title
        self.title_label.setText(text)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============

        Set window stylesheet.
        """

        self.setStyleSheet(f"""
            QWidget{{
                background-color: rgb(36, 36, 36);
                }}
            QTabWidget{{
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::tab-bar{{
                alignment: center;
                }}
            QTabBar::tab{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                width: {self.tab_width}px;
                height: {self.tab_height}px;
                padding: {pyflame.gui_resize(5)}px;
                }}
            QTabBar::tab:selected{{
                color: rgb(200, 200, 200);
                background-color: rgb(31, 31, 31);
                border: 1px solid rgb(31, 31, 31);
                border-bottom: 1px solid {Color.BLUE.value};
                }}
            QTabBar::tab:!selected{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::pane{{
                border-top: 1px solid {Color.TAB_PANE.value};
                }}
            """)

    #-------------------------------------
    # [QT Event Handlers]
    #-------------------------------------

    def mousePressEvent(self, event):
        """
        Mouse Press Event
        =================

        Handle mouse press event.
        """

        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        """
        Mouse Move Event
        ================

        Handle mouse move event.
        """

        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            pass

    def keyPressEvent(self, event):
        """
        Key Press Event
        ===============

        Handle key press event.
        """

        if event.key() == QtCore.Qt.Key_Return and self.return_pressed is not None:
            self.return_pressed()

    def resizeEvent(self, event):
        """
        Resize Event
        ============

        Handle resize event.
        """

        # Ensure the left blue line overlay covers the whole window when resizing
        self.overlay.setGeometry(0, 0, 100, 3000)
        super().resizeEvent(event)

class PyFlameWindow(QtWidgets.QWidget):
    """
    PyFlameWindow
    =============

    Custom QT Flame Window Widget

    Creates a custom QT window with a colored bar on the left side of the window.

    By default, the window will have a grid layout with 4 columns and 2 rows.
    This can be overridden by setting the `grid_columns` and `grid_rows` arguments.
    If `grid_layout` is set to `False`, the window will not have a grid layout and a layout
    will need to be added in the main script.

    Args:
    -----
        `title` (str):
            Text displayed in top left corner of window.
            (Default: `Python Script`)

        `title_style` (Style):
            Style of title text. Use Style Enum to set style.
            (Default: `Style.BACKGROUND`)

            Style Options:
            --------------
            `Style.BACKGROUND`: For background style.
            `Style.NORMAL`: For normal style.
            `Style.UNDERLINE`: For underline style.

        `width` (int):
            Set minimum width of window.
            (Default: `150`)

        `height` (int):
            Set minimum height of window.
            (Default: `30`)

        `line_color` (Color):
            Color of bar on left side of window.
            (Default: `Color.BLUE`)

            Color Options:
            --------------
            `Color.GRAY`: For gray line.
            `Color.BLUE`: For blue line.
            `Color.RED`: For red line.
            `Color.GREEN`: For green line.
            `Color.YELLOW`: For yellow line.
            `Color.TEAL`: For teal line.

        `return_pressed` (callable, optional):
            Function to be called when return key is pressed.
            (Default: `None`)

        `tab_width` (int):
            Set width of window tab labels.
            (Default: `150`)

        `tab_height` (int):
            Set height of of window tab labels.
            (Default: `24`)

        `grid_layout` (bool):
            Add grid layout to window.
            (Default: `True`)

        `grid_columns` (int):
            Number of columns in grid layout. Only used if `grid_layout` is `True`.
            (Default: `4`)

        `grid_rows` (int):
            Number of rows in grid layout. Only used if `grid_layout` is `True`.
            (Default: `3`)

        `parent` (QWidget, optional):
            Parent widget for the window.
            (Default: `None`)

    Methods:
    --------
        `add_layout(layout: PyFlameLayout)`:
            Add layout to window.

        `set_title_text(text: str)`:
            Set title text of window.

    Notes:
    ------
        - For proper sizing of widgets and placement of widgets in the window,
        be sure to set the correct number of columns and rows in the grid layout
        when using the default grid layout.

    Example:
    --------
        To create a window using the default grid layout:
        ```
        window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION},
            return_pressed=confirm,
            grid_columns=6,
            grid_rows=5,
            )

        window.addWidget(some_widget1, row=0, column=0, row_span=1, column_span=1)
        window.addWidget(some_widget2, row=0, column=0, row_span=1, column_span=1)
        window.addWidget(some_widget3, row=0, column=0, row_span=1, column_span=1)
        ```

        To create a window not using the default grid layout:
        ```
        window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION},
            return_pressed=confirm,
            grid_layout=False,
            )

        create some widgets here...

        layout = PyFlameVBoxLayout()

        layout.addWidget(some_widget1, row=0, column=0, row_span=1, column_span=1)
        layout.addWidget(some_widget2, row=0, column=0, row_span=1, column_span=1)
        layout.addWidget(some_widget3, row=0, column=0, row_span=1, column_span=1)

        window.add_layout(layout)

        window.show()
        ```
    """

    def __init__(self: 'PyFlameWindow',
                 title: str='Python Script',
                 title_style: Style=Style.BACKGROUND_THIN,
                 width: int=150,
                 height: int=30,
                 line_color: Color=Color.BLUE,
                 return_pressed: Optional[Callable]=None,
                 tab_width: int=150,
                 tab_height: int=24,
                 grid_layout: bool=True,
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: Optional[dict[int, int]]={},
                 grid_layout_adjust_row_heights: Optional[dict[int, int]]={},
                 parent: Optional[QtWidgets.QWidget]=None,
                 ) -> None:
        super().__init__()

        def validate_arguments():
            """
            Validate Arguments
            ==================

            Validate argument types and raise TypeError if any arguments are invalid.
            """

            if not isinstance(title, str):
                pyflame.raise_type_error(f'PyFlameWindow', 'title', 'string', title)
            if not isinstance(title_style, Style):
                pyflame.raise_type_error(f'PyFlameWindow', 'title_style', 'Style Enum', title_style)
            if not isinstance(width, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'width', 'int', width)
            if not isinstance(height, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'height', 'int', height)
            if width and not height:
                pyflame.raise_value_error(error_message='PyFlameWindow: height must be set if width is set.')
            if height and not width:
                pyflame.raise_value_error(error_message='PyFlameWindow: width must be set if height is set.')
            if not isinstance(line_color, Color):
                pyflame.raise_type_error(f'PyFlameWindow', 'line_color', 'Color Enum', line_color)
            if return_pressed is not None and not callable(return_pressed):
                pyflame.raise_type_error(f'PyFlameWindow', 'return_pressed', 'callable or None', return_pressed)
            if not isinstance(tab_width, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'tab_width', 'int', tab_width)
            if not isinstance(tab_height, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'tab_height', 'int', tab_height)
            if not isinstance(grid_layout, bool):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout', 'bool', grid_layout)
            if not isinstance(grid_layout_columns, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_columns', 'int', grid_layout_columns)
            if not isinstance(grid_layout_rows, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_rows', 'int', grid_layout_rows)
            if not isinstance(grid_layout_column_width, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_column_width', 'int', grid_layout_column_width)
            if not isinstance(grid_layout_row_height, int):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_row_height', 'int', grid_layout_row_height)
            if not isinstance(grid_layout_adjust_column_widths, dict):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_adjust_column_widths', 'dict', grid_layout_adjust_column_widths)
            if not isinstance(grid_layout_adjust_row_heights, dict):
                pyflame.raise_type_error(f'PyFlameWindow', 'grid_layout_adjust_row_heights', 'dict', grid_layout_adjust_row_heights)
            if parent is not None and not isinstance(parent, QtWidgets.QWidget):
                pyflame.raise_type_error(f'PyFlameWindow', 'parent', 'QWidget or None', parent)

        def center_window():
            """
            Center Window
            =============

            Center the window on the screen.
            """

            # Get Current Screen Resolution
            main_window_res = pyflamewin.main_window()
            resolution = main_window_res.screenGeometry()

            # Center Window on Screen
            self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

        validate_arguments()

        # Set Window Settings
        self.setFont(FONT)
        self.line_color = line_color # Being passed to _WindowSideLineOverlay
        self.return_pressed = return_pressed
        self.tab_width = pyflame.gui_resize(tab_width)
        self.tab_height = pyflame.gui_resize(tab_height)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.parent = parent

        # Match title underline color to side line color with transparency
        if self.line_color == Color.BLUE:
            underline_color = Color.BLUE_TRANS
        elif self.line_color == Color.GRAY:
            underline_color = Color.GRAY_TRANS
        elif self.line_color == Color.RED:
            underline_color = Color.RED_TRANS
        elif self.line_color == Color.GREEN:
            underline_color = Color.GREEN_TRANS
        elif self.line_color == Color.YELLOW:
            underline_color = Color.YELLOW_TRANS
        elif self.line_color == Color.TEAL:
            underline_color = Color.TEAL_TRANS

        # Window Title Label
        title_label = PyFlameLabel(
            text='<span style="white-space: pre;">  ' + title, # Add space to title using CSS code. This pushes the title to the right one space.
            style=title_style,
            align=Align.LEFT,
            max_width=True,
            underline_color=underline_color,
            height=40,
            font_size=24,
            )

        # Window Layout
        # -------------
        title_text_hbox = PyFlameHBoxLayout()
        title_text_hbox.addWidget(title_label)
        title_text_hbox.setContentsMargins(0, 0, 0, 0)  # Remove margins around the title label

        # Center layout - where main UI is added
        self.center_layout = PyFlameGridLayout()
        # Create widget to hold the center layout
        center_widget = QtWidgets.QWidget()
        center_widget.setLayout(self.center_layout)

        # Add the center layout to the main layout
        main_vbox2 = PyFlameVBoxLayout()
        main_vbox2.addWidget(center_widget, alignment=QtCore.Qt.AlignCenter)
        main_vbox2.addStretch()
        main_vbox2.setContentsMargins(pyflame.gui_resize(15), pyflame.gui_resize(15), pyflame.gui_resize(15), pyflame.gui_resize(15)) # Add margin around main UI

        main_vbox3 = PyFlameVBoxLayout()
        main_vbox3.addLayout(title_text_hbox)
        main_vbox3.addLayout(main_vbox2)
        main_vbox3.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.setLayout(main_vbox3)

        self._set_stylesheet()

        # Initialize and set up the overlay for colored line on left edge of window
        self.overlay = _WindowSideLineOverlay(self)

        # Create default grid layout if grid_layout is True
        if grid_layout:
            self.grid_layout = PyFlameGridLayout(
                columns=grid_layout_columns,
                rows=grid_layout_rows,
                column_width=grid_layout_column_width,
                row_height=grid_layout_row_height,
                adjust_column_widths=grid_layout_adjust_column_widths,
                adjust_row_heights=grid_layout_adjust_row_heights,
                )

            self.add_layout(self.grid_layout)
            self.show()

        self.setFixedSize(self.size())  # Lock current size

        # Center Window on Screen
        center_window()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_layout(self, layout):
        """
        Add Layout
        ==========

        Add widget layout to the main window.

        Args:
        -----
            layout (PyFlameLayout):
                Main widget layout to add to Main Window.

        Raises:
        -------
            TypeError:
                If `layout` is not a QLayout(PyFlameGridLayout, PyFlameVBoxLayout, PyFlameHBoxLayout).

        Example:
        --------
            ```
            layout = PyFlameGridLayout(
                columns=6,
                rows=5,
                column_width=150,
                row_height=28,
                )
            window.add_layout(layout)
            ```
        """

        # Validate argument type
        if not isinstance(layout, QtWidgets.QLayout):
            pyflame.raise_type_error(f'PyFlameWindow', 'layout', 'QLayout', layout)

        # Add layout to center layout
        self.center_layout.addLayout(layout, 0, 0)

    def set_title_text(self, text: str):
        """
        Set Title Text
        ==============

        Set the title of the window.

        Used to change the title of the window after it has been created.

        Args:
        -----
            text (str):
                Text to display in the title of the window.

        Raises:
        -------
            TypeError:
                If `text` is not a string.

        Example:
        --------
            ```
            window.set_title_text('New Title')
            ```
        """

        # Validate argument type
        if not isinstance(text, str):
            raise TypeError('PyFlameWindow: set_title_text must be called with a string.')

        # Set window title
        self.title_label.setText(text)

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============

        Set window stylesheet.
        """

        self.setStyleSheet(f"""
            QWidget{{
                background-color: rgb(36, 36, 36);
                }}
            QTabWidget{{
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::tab-bar{{
                alignment: center;
                }}
            QTabBar::tab{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                width: {self.tab_width}px;
                height: {self.tab_height}px;
                padding: {pyflame.gui_resize(5)}px;
                }}
            QTabBar::tab:selected{{
                color: rgb(200, 200, 200);
                background-color: rgb(31, 31, 31);
                border: 1px solid rgb(31, 31, 31);
                border-bottom: 1px solid {Color.BLUE.value};
                }}
            QTabBar::tab:!selected{{
                color: {Color.TEXT.value};
                background-color: rgb(36, 36, 36);
                border: none;
                }}
            QTabWidget::pane{{
                border-top: 1px solid {Color.TAB_PANE.value};
                }}
            """)

    #-------------------------------------
    # [QT Event Handlers]
    #-------------------------------------

    def mousePressEvent(self, event):
        """
        Mouse Press Event
        =================

        Handle mouse press event.
        """

        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        """
        Mouse Move Event
        ================

        Handle mouse move event.
        """

        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            pass

    def keyPressEvent(self, event):
        """
        Key Press Event
        ===============

        Handle key press event.
        """

        if event.key() == QtCore.Qt.Key_Return and self.return_pressed is not None:
            self.return_pressed()

    def resizeEvent(self, event):
        """
        Resize Event
        ============

        Handle resize event.
        """

        # Ensure the left blue line overlay covers the whole window when resizing
        self.overlay.setGeometry(0, 0, 100, 3000)
        super().resizeEvent(event)

#-------------------------------------
# [PyFlame Tabbed Window Classes]
#-------------------------------------
# DO NOT USE THESE CLASSES
# They will be removed in the next release
# Use PyFlameTabWidget instead for tabbed windows
#------------------------------------------------

class _PyFlameTabbedWindow:
    """
    _PyFlameTabbedWindow
    ====================

    **** DO NOT USE THIS CLASS ****
    **** TO BE REMOVED IN FUTURE VERSIONS ****

    A subclass of PyFlameWindow/PyFlameDialogWindow that adds a tabbed interface.

    Inherits all functionality of PyFlameWindow/PyFlameDialogWindow.

    Methods:
    --------
        `add_tab`(name: str) -> TabContainer
            Creates a new tab with a grid layout and returns a container object
            with `widget` (the tab itself) and `grid_layout` (its layout).

        `get_current_tab`() -> int
            Get index of current tab.

        `go_to_tab`(index: int) -> None
            Switches to the specified tab by index.

    Attributes:
    -----------
        tab_pages: dict[str, TabContainer]:
            A dictionary of tab names and their corresponding tab containers.

    Examples:
    ---------
        Create a tabbed window with 3 tabs:
        ```
        def main_window(self):

            self.window = PyFlameTabWindow(
                title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
                return_pressed=self.done_button,
                grid_layout_columns=5,
                grid_layout_rows=12,
                grid_layout_adjust_column_widths={4: 110},
                )

            # Add tabs to main window
            self.tab1 = self.window.add_tab('Some Tab 1')
            self.tab2 = self.window.add_tab('Some Tab 2')
            self.tab3 = self.window.add_tab('Some Tab 3')

            # Load Tab UI's
            self.some_tab_1()
            self.some_tab_2()
            self.some_tab_3()
        ```

        Add widgets to tab1:
        ```
        self.tab1.grid_layout.addWidget(self.label, 0, 0,)
        self.tab1.grid_layout.addWidget(self.tree, 1, 0)
        self.tab1.grid_layout.addWidget(self.entry, 2, 0)
        ```

        Get current tab:
        ```
        self.window.get_current_tab()
        ```

        Switch to tab1:
        ```
        self.window.go_to_tab(0)
        ```
    """

    class TabContainer:
        """
        Tab Container
        =============

        Container for individual tabs in PyFlameTabWindow.
        """

        def __init__(self, tab_widget, parent_window):

            self.widget = tab_widget

            self.grid_layout = PyFlameGridLayout(
                columns=parent_window.grid_layout_columns,
                rows=parent_window.grid_layout_rows,
                column_width=parent_window.grid_layout_column_width,
                row_height=parent_window.grid_layout_row_height,
                adjust_column_widths=parent_window.grid_layout_adjust_column_widths,
                adjust_row_heights=parent_window.grid_layout_adjust_row_heights
                )

            # Sets the contents margins of the grid layout to 0 on the top, 15 on the right, 0 on the bottom, and 0 on the left.
            #self.grid_layout.setContentsMargins(0, pyflame.gui_resize(15), 0, 0)

            self.widget.setLayout(self.grid_layout)

    def __init__(self,
                 title: str='Python Script',
                 title_style: Style=Style.BACKGROUND_THIN,
                 width: int=150,
                 height: int=30,
                 line_color: Color=Color.BLUE,
                 return_pressed: Optional[Callable]=None,
                 tab_width: int=150,
                 tab_height: int=24,
                 grid_layout: bool=True,
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: Optional[dict[int, int]]={},
                 grid_layout_adjust_row_heights: Optional[dict[int, int]]={},
                 parent: Optional[QtWidgets.QWidget]=None):

        super().__init__(title=title,
                         title_style=title_style,
                         width=width,
                         height=height,
                         line_color=line_color,
                         return_pressed=return_pressed,
                         tab_width=tab_width,
                         tab_height=tab_height,
                         grid_layout=grid_layout,
                         grid_layout_columns=grid_layout_columns,
                         grid_layout_rows=grid_layout_rows,
                         grid_layout_column_width=grid_layout_column_width,
                         grid_layout_row_height=grid_layout_row_height,
                         grid_layout_adjust_column_widths=grid_layout_adjust_column_widths,
                         grid_layout_adjust_row_heights=grid_layout_adjust_row_heights,
                         parent=parent)

        # Store layout parameters
        self.grid_layout_columns = grid_layout_columns
        self.grid_layout_rows = grid_layout_rows
        self.grid_layout_column_width = grid_layout_column_width
        self.grid_layout_row_height = grid_layout_row_height
        self.grid_layout_adjust_column_widths = grid_layout_adjust_column_widths
        self.grid_layout_adjust_row_heights = grid_layout_adjust_row_heights

        # Initializes a dictionary to store tab pages, mapping tab names (as strings) to their corresponding TabContainer objects.
        self.tab_pages: dict[str, PyFlameTabWindow.TabContainer] = {}

        # Initializes a QTabWidget instance to manage the tabs.
        self.tabs = QtWidgets.QTabWidget()
        self.tabs.setFont(FONT)

        # Initializes a main layout (PyFlameGridLayout) and adds the tabs widget to it.
        main_layout = PyFlameGridLayout()
        main_layout.addWidget(self.tabs, 0, 0)
        self.add_layout(main_layout)

    def add_tab(self, name: str) -> TabContainer:
        """
        Add Tab
        =======

        Creates and adds a new tab to the window with its own grid layout.

        Args:
        -----
            name (str):
                Name of the tab to add.

        Returns:
        --------
            TabContainer:
                TabContainer object with the new tab.
        """

        # Creates a new tab widget (QtWidgets.QWidget) to serve as the container for the tab's contents.
        tab_widget = QtWidgets.QWidget()

        # Initializes a TabContainer object with the newly created tab widget and the parent window (self).
        tab_container = self.TabContainer(tab_widget, self)

        # Adds the tab to the QTabWidget using the tab's name as the label.
        self.tabs.addTab(tab_container.widget, name)

        # Adds the tab container to the tab_pages dictionary, mapping the tab's name to the TabContainer object.
        self.tab_pages[name] = tab_container

        return tab_container

    def get_current_tab(self) -> TabContainer:
        """
        Get Current Tab
        ===============

        Get index of current tab.

        Returns:
        --------
            int:
                Index of the current tab.
        """

        return self.tabs.currentIndex()

    def go_to_tab(self, index: int):
        """
        Go To Tab
        ==========

        Switches to the specified tab by index.

        Args:
        -----
            index (int):
                Index of the tab to switch to.
        """

        self.tabs.setCurrentIndex(index)

class PyFlameTabWindow(_PyFlameTabbedWindow, PyFlameWindow):
    """
    PyFlameTabWindow
    =================

    **** DO NOT USE THIS CLASS ****
    **** TO BE REMOVED IN FUTURE VERSIONS ****

    A convenience subclass that combines `PyFlameWindow` with the tabbed interface
    provided by `PyFlameTabbedMixin`.

    This class is functionally equivalent to `_PyFlameTabbedWindow` using
    `PyFlameWindow` as its base class. It is best suited for creating
    standard, non-modal tabbed windows.

    Inherits:
    ---------
        PyFlameWindow:
            Provides the base window functionality, including styling, layout,
            window title bar, and event handling.

        _PyFlameTabbedWindow:
            Adds support for a tabbed interface via a `QTabWidget`, and manages
            individual tab pages with `PyFlameGridLayout`.

    Methods:
    --------
        `add_tab(name: str) -> TabContainer`:
            Adds a new tab with a grid layout and returns a container object
            with `widget` and `grid_layout`.

        `get_current_tab() -> int`:
            Returns the index of the currently selected tab.

        `go_to_tab(index: int) -> None`:
            Switches to the tab at the specified index.

    Attributes:
    -----------
        tab_pages: dict[str, TabContainer]:
            Dictionary mapping tab names to their corresponding tab container objects.

        tabs: QtWidgets.QTabWidget:
            The main tab widget managing the tabbed interface.

    Usage:
    ------
        ```
        self.window = PyFlameTabWindow(
            title='My Script',
            grid_layout_columns=5,
            grid_layout_rows=10
        )

        tab1 = self.window.add_tab('Tab One')
        tab1.grid_layout.addWidget(self.label, 0, 0)
        ```
    """

    pass

class PyFlameTabDialogWindow(_PyFlameTabbedWindow, PyFlameDialogWindow):
    """
    PyFlameTabDialogWindow
    =======================

    **** DO NOT USE THIS CLASS ****
    **** TO BE REMOVED IN FUTURE VERSIONS ****

    A convenience subclass that combines `PyFlameDialogWindow` with the tabbed
    interface provided by `_PyFlameTabbedWindow`.

    This class is functionally equivalent to `_PyFlameTabbedWindow` using
    `PyFlameDialogWindow` as its base class. It is ideal for creating modal or
    dialog-style tabbed windows that require user interaction before continuing.

    Inherits:
    ---------
        PyFlameDialogWindow:
            Provides dialog-specific window features including modal behavior,
            accept/reject buttons, and additional window chrome.

        _PyFlameTabbedWindow:
            Adds support for a tabbed interface via a `QTabWidget`, and manages
            individual tab pages with `PyFlameGridLayout`.

    Methods:
    --------
        `add_tab(name: str) -> TabContainer`:
            Adds a new tab with a grid layout and returns a container object
            with `widget` and `grid_layout`.

        `get_current_tab() -> int`:
            Returns the index of the currently selected tab.

        `go_to_tab(index: int) -> None`:
            Switches to the tab at the specified index.

    Attributes:
    -----------
        tab_pages: dict[str, TabContainer]:
            Dictionary mapping tab names to their corresponding tab container objects.

        tabs: QtWidgets.QTabWidget:
            The main tab widget managing the tabbed interface.

    Usage:
    ------
        ```
        self.dialog = PyFlameTabDialogWindow(
            title='Settings Dialog',
            grid_layout_columns=4,
            grid_layout_rows=8
        )

        settings_tab = self.dialog.add_tab('Settings')
        settings_tab.grid_layout.addWidget(self.checkbox, 0, 0)
        ```
    """

    pass
