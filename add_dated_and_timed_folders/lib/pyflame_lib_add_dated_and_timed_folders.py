# PyFlame Library
# Copyright (c) 2026 Michael Vaglienty
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
PyFlame Library
Version: 5.3.0
Written By: Michael Vaglienty
Creation Date: 10.31.20
Update Date: 03.13.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Description:
    This library provides custom PyQt widgets styled to resemble Autodesk Flame,
    along with other useful utility functions.

    https://github.com/logik-portal/pyflame

Usage:
    - Place this file inside a folder named "lib" located in the same directory
      as the main script.
    - To avoid conflicts with multiple copies inside the Flame Python packages
      folder, rename this file to: pyflame_lib_<main_script_name>.py
    - The top-level "script_folder" should be named after the main script.

Folder Structure:
    script_folder/                # folder named after the main script
    ├── main_script.py
    ├── lib/
    │   └── pyflame_lib_<main_script_name>.py
    │   └── pyflame_lib_<main_script_name>.pyi   # Optional
    ├── assets/
    │   └── fonts/
    │       ├── Montserrat-Regular.ttf
    │       ├── Montserrat-Light.ttf
    │       └── Montserrat-Thin.ttf

Required Files:
    - Montserrat-Regular.ttf
    - Montserrat-Light.ttf
    - Montserrat-Thin.ttf
    - pyflame_lib_<main_script_name>.py (this file, renamed as above)

Notes:
    All paths are relative to the script's root directory and must be preserved
    when deploying or moving the script.

Import Example:
    from lib.pyflame_lib_<main_script_name> import *

See README.md and CHANGELOG.md for more details.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import csv
import datetime
import json
import os
import platform
import re
import shutil
import subprocess
import traceback
import importlib.util
from shiboken6 import isValid
import xml.etree.ElementTree as ET
from enum import Enum
from functools import partial
from subprocess import PIPE, Popen
from typing import Any, Callable, Dict, List, Tuple, Optional, Union

import flame # type: ignore[import]

# ==============================================================================
# [PySide6 Imports]
# ==============================================================================

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtGui import QAction
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator as QValidator

# ==============================================================================
# [Constants]
# ==============================================================================

LIB_PATH = os.path.abspath(__file__).rsplit("/", 1)[0]
SCRIPT_NAME = LIB_PATH.rsplit("/", 2)[1].title().replace('_', ' ')
SCRIPT_PATH = LIB_PATH.rsplit("/", 1)[0]

SHARED_FILE_SEQUENCE_PATH = '/opt/Autodesk/shared/export/presets/file_sequence'
SHARED_MOVIE_EXPORT_PATH = '/opt/Autodesk/shared/export/presets/movie_file'

# ==============================================================================
# [PyFlame Enums]
# ==============================================================================
# For internal script use only.
# Not meant to be used outside of this file.
# ==============================================================================

class Color(Enum):
    """
    Color
    =====

    Enum for storing color values used in the PyFlame UI elements. This class
    helps in maintaining a consistent color scheme throughout the application,
    making it easy to change colors in a centralized manner.

    Each color is represented as an RGB value string, which can be used to
    style different elements in the application, such as text, buttons,
    borders, and backgrounds.

    Examples
    --------
        ```
        # Set button background color
        button.setStyleSheet(f'background-color: {Color.GRAY.value};')

        # Set text color for a label
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

    Attributes
    ---------
        `GREEN` (str):
            Green text.

        `YELLOW` (str):
            Yellow text.

        `RED` (str):
            Red text.

        `WHITE` (str):
            White text.

        `BLUE` (str):
            Blue text.

        `RESET` (str):
            Reset text color to default.
    """

    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    BLUE = '\033[38;5;33m'
    RESET = '\033[0m'

    def format(self, text: str) -> str:
        """
        Format the given text with the Enum's color.

        Args
        ----
            text (str): The text to format.

        Returns
        -------
            str: The formatted text with ANSI color codes.
        """

        return f"{self.value}{text}{TextColor.RESET.value}"

class Style(Enum):
    """
    Style
    =====

    Enum for PyFlameLabel style options.

    Attributes
    ---------
        `NORMAL` (str):
            Standard label without any additional styling. Text is left aligned
            by default.

        `UNDERLINE` (str):
            Text is underlined. Text is centered by default.

        `BORDER` (str):
            Adds a white border around the label with a dark background. Text
            is centered by default.

        `BACKGROUND` (str):
            Adds a darker background to the label. Text is left aligned by
            default.

        `BACKGROUND_THIN` (str):
            Adds a darker background to the label with a thin font. Text is
            left aligned by default.
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

    Attributes
    ---------
        `LEFT` (str):
            Align text to the left.

        `RIGHT` (str):
            Align text to the right.

        `CENTER` (str):
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

    Attributes
    ---------
        `INFO` (str):
            Information message type.

        `OPERATION_COMPLETE` (str):
            Operation complete message type.

        `CONFIRM` (str):
            Confirmation message type.

        `ERROR` (str):
            Error message type.

        `WARNING` (str):
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

    Attributes
    ----------
        `INFO` (str):
            Information type.

        `ERROR` (str):
            Error type.

        `WARNING` (str):
            Warning type.
    """

    INFO = 'info'
    ERROR = 'error'
    WARNING = 'warning'

class BrowserType(Enum):
    """
    BrowserType
    ===========

    Enum for PyFlameEntryBrowser browser type options.

    Attributes
    ----------

        `FILE` (str):
            File browser.

        `DIRECTORY` (str):
            Directory browser.
    """

    FILE = 'file'
    DIRECTORY = 'directory'

class TextStyle(Enum):
    """
    Text Style
    ==========

    Enum for PyFlameTextEdit and PyFlameTextBrowser

    Attributes
    ---------
        `EDITABLE` (str):
            Text is Editable.

        `READ_ONLY` (str):
            Text is Read-Only.

        `UNSELECTABLE` (str):
            Text is Read-Only and cannot be highlighted.
    """

    EDITABLE = 'editable'
    READ_ONLY = 'read_only'
    READ_ONLY_SELECTABLE = 'read_only_selectable'
    UNSELECTABLE = 'unselectable'

class TextType(Enum):
    """
    Text Type
    =========

    Enum for PyFlameTextEdit and PyFlameTextBrowser

    Attributes
    ---------
        `PLAIN` (str):
            Text is read as Plain Text.

        `MARKDOWN` (str):
            Text is read as Markdown.

        `HTML` (str):
            Text is read as HTML.
    """

    PLAIN = 'plain'
    MARKDOWN = 'markdown'
    HTML = 'html'

# ==============================================================================
# [PyFlame Tools]
# ==============================================================================

class _PyFlame:
    """
    PyFlame
    =======

    Various useful functions for scripts.

    Example
    -------
        Print a message using `print`:
        ```
        pyflame.print(
            text='Config not found.',
            type=PrintType.ERROR
            )
        ```
    """

    @staticmethod
    def window_resolution():
        """
        Get the main window resolution.

        Returns
        -------
            main_window_res :
                The main window resolution object.
        """

        main_window_res = QtGui.QGuiApplication.primaryScreen()

        return main_window_res

    @staticmethod
    def pause(seconds: int|float=.01) -> None:
        """
        Pause
        =====

        Pause QT for a brief time. This is sometimes needed to allow the window UI to update
        before moving on to the next operation. Usually .01 seconds is long enough.

        Args
        ----
            seconds (int|float):
                Time in seconds to pause the UI.
        """

        # Validate Argument
        if not isinstance(seconds, (int, float)):
            pyflame.raise_type_error('pyflame.pause', 'seconds', 'int or float', seconds)

        def pause_loop(time):
            loop = QtCore.QEventLoop()
            QtCore.QTimer.singleShot(time, loop.quit)
            loop.exec_()

        milliseconds = seconds*1000 # 1000ms = 1 second

        pause_loop(milliseconds)

    @staticmethod
    def python_package_local_install(package: str | list[str]) -> bool:
        """
        Python Package Local Install
        ============================

        Check if required python packages are installed, and install missing packages
        from local compressed files to the Flame Python Packages directory.

        System Password is required to install any missing python packages.

        Args
        ----
            package (str|list[str]):
                The name(s) of the python package(s) to check/install. Should match
                the file name prefix of the compressed package.

        Returns
        -------
            bool:
                True if the python packages are installed, False otherwise.

        Notes
        -----
            - If a list of packages is provided, all packages will be checked/installed.
            - If a single package is provided, it will be checked/installed.
            - The function first checks if packages are already installed before attempting installation.
            - Python packages should be compressed with tgz and located in the script assets/python_packages directory.
                Example: /opt/Autodesk/shared/python/script_name/assets/python_packages/PIL_python3.11.tgz
            - The python package will be installed to the Flame Python Packages directory.
                Example: /opt/Autodesk/python/FLAME_VERSION/lib/PYTHON_VERSION/site-packages/<package_name>
            - Package requiring a specific python version should be named <package_name>_python<python_version>.tgz and located in the script assets/python_packages directory.
                Example: PIL_python3.11.tgz
        """

        def package_check(package: str) -> bool:
            """
            Package Check
            =============

            Check if required python package is installed.

            Args
            ----
                package (str):
                    The name of the required python package to check.
            """

            if '_python' in package:
                package = package.split('_python')[0]

            if importlib.util.find_spec(package) is None:
                return False
            else:
                return True

        def install_package(package: str, system_password: str | None=None) -> bool:
            """
            Install Package
            ===============

            Install python package to Flame Python Packages directory.

            System Password is required to install python packages.

            Args
            ----
                package (str):
                    The name of the python package to install.

            Returns
            -------
                bool:
                    True if package is installed, False otherwise.
            """

            # Get Flame Python Packages directory.
            python_install_dir = pyflame.get_flame_python_packages_path()
            print('Flame Python Packages Directory:', python_install_dir)

            # Get package tar file. If python_version if provided, check for it.
            package_tar = None
            for tgz in os.listdir(os.path.join(SCRIPT_PATH, 'assets/python_packages')):
                if tgz.endswith('.tgz') and tgz.startswith(package):
                    package_tar = os.path.join(os.path.join(SCRIPT_PATH, 'assets/python_packages', tgz))
                    break

            # If package tar file is not found, print error and return.
            if not package_tar:
                PyFlameMessageWindow(
                    message=f'Python package {package} not found.',
                    message_type=MessageType.ERROR,
                    title=SCRIPT_NAME,
                    parent=None,
                    )
                return False

            # Untar package.
            pyflame.untar(
                tar_file_path=package_tar,
                untar_path=python_install_dir,
                sudo_password=system_password,
                )

            # Refresh Python Hooks
            flame.execute_shortcut('Rescan Python Hooks')

            # Check if package is installed. If not, print error and return.
            installed = package_check(package)
            if not installed:
                PyFlameMessageWindow(
                    message=f'Python package {package} not installed.',
                    message_type=MessageType.ERROR,
                    title=SCRIPT_NAME,
                    parent=None,
                    )
                return False

            return True # Return True if all packages are installed.

        def get_system_password() -> str | None:
            """
            Get System Password
            ==================

            Get system password from password window.

            Returns
            -------
                str | None:
                    System password if entered, None otherwise.
            """

            # Open password window to get system password. If password is not entered, return None.
            password_window = PyFlamePasswordWindow(
                text=f'This script requires python packages to be installed. System password is required to install them.',
                title=f'{SCRIPT_NAME}: System Password',
                parent=None,
                )
            system_password = password_window.password # Get system password from password window.
            if not system_password:
                return None
            return system_password

        # Validate Arguments
        if not isinstance(package, (str, list)):
            pyflame.raise_type_error('python_package_local_install', 'package', 'str|list[str]', package)
        if isinstance(package, list) and not all(isinstance(item, str) for item in package):
            pyflame.raise_type_error('python_package_local_install', 'package', 'str|list[str]', package)

        system_password = None

        pyflame.print(f'This script requires python packages to be installed.', new_line=False)
        pyflame.print(f'Checking if required python package(s) are installed...', underline=True, new_line=False)

        # if package is a string, convert to list
        if isinstance(package, str):
            package = [package]

        print(f"Required python package(s): {', '.join(package)}")

        # Check if all packages are installed.
        packages_installed = True
        for pkg in package:
            if not package_check(pkg):
                packages_installed = False
                break

        # Install missing packages.
        if not packages_installed:
            for pkg in package:
                pyflame.print(f'{pkg}:', new_line=False)
                if not package_check(pkg):
                    if not system_password:
                        system_password = get_system_password()
                        if not system_password:
                            return False
                    pyflame.print(f'{pkg} not found. Installing...', print_type=PrintType.ERROR)
                    installed = install_package(pkg, system_password) # Install package.
                    if not installed: # If installation failed, print error and return.
                        pyflame.print(f'{pkg} installation failed.', print_type=PrintType.ERROR)
                        return False # Return False if any package installation failed.
                else: # If package is installed, print message.
                    pyflame.print(f'{pkg} found.')

            package_list = '\n'.join(package)
            PyFlameMessageWindow(
                message=f"Python packages successfully installed:\n\n{package_list}\n\nStarting script...",
                title=f'{SCRIPT_NAME}: Packages Installed',
                parent=None,
                )

            pyflame.print(f'All packages installed.')

            # Clear system password to prevent reuse
            system_password = ''

            return True # Return True if all packages are installed.

        else:
            pyflame.print(f'All packages already installed.')
            return True

    @staticmethod
    def cursor_busy() -> None:

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

    @staticmethod
    def cursor_restore() -> None:

        QtWidgets.QApplication.restoreOverrideCursor()

    @staticmethod
    def print_title(text: str) -> None:
        """
        Print Title
        ===========

        Print a stylized title banner with the script name and version centered to the terminal.

        Args
        ----
            text (str):
                The full banner line, e.g., 'Cool Script v1.0.0'

        Example
        -------

        --------------------------====[ Cool Script v1.0.0 ]====-----------------------
        """

        # Validate Argument
        if not isinstance(text, str):
            pyflame.raise_type_error('pyflame.print_title', 'text', 'str', value)

        text = f'====[ {text} ]===='
        line = text.center(80, "-")

        colored = ""
        in_text = False
        for char in line:
            if char == "[":
                in_text = True
                colored += TextColor.WHITE.value + char
            elif char == "]":
                in_text = False
                colored += TextColor.WHITE.value + char
            elif in_text:
                colored += TextColor.WHITE.value + char
            else:
                colored += TextColor.BLUE.value + char

        print('\n' + colored + TextColor.RESET.value + '\n')

    @staticmethod
    def create_temp_folder(folder_name: str='temp') -> str:
        """
        Create Temp Folder
        ==================

        Create a temporary folder in the script folder.

        If folder already exists, it will be deleted and recreated.

        Temp folder is added to <SCRIPT_PATH>/<folder_name>.

        Args
        ----
            `folder_name` (str):
                Name of the temporary folder to create.
                (Default: `temp`)

        Returns
        -------
            str:
                Path to the temporary folder.

        Raises
        ------
            TypeError:
                If `folder_name` is not a string.

        Example
        -------
            To create a temporary folder:
            ```
            temp_folder_path = pyflame.create_temp_folder()
            ```
        """

        # Validate Argument
        if not isinstance(folder_name, str):
            pyflame.raise_type_error('pyflame.create_temp_folder', 'folder_name', 'str', folder_name)

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

        Args
        ----
            `folder_name` (str):
                Name of the temporary folder to clear. Temp folder is added to <SCRIPT_PATH>/<folder_name>.
                (Default: `temp`)
        """

        # Validate Argument
        if not isinstance(folder_name, str):
            pyflame.raise_type_error('pyflame.cleanup_temp_folder', 'folder_name', 'str', folder_name)

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
    def verify_script_install(additional_files: list=[]) -> bool:
        """
        Verify Script Install
        =====================

        Verify that script is installed in the correct location.

        Scripts should always be installed in a folder with the same name as the script file.

        Checks to make sure the script folder is named the same as the main script file, that the
        script folder is writable, and that the script folder contains the required additional
        files if any are specified.

        Args
        ----
            `additional_files` (list):
                List of additional files to check for in the script folder. These are other files
                that are required for the script to work. This should only be a list of file names,
                not full paths. If file is in a subfolder of the script folder, it should include
                the subfolder name. For example, if the script folder is named 'srt_to_xml' and the
                file 'xml_template.xml' is in the 'templates' subfolder, the file name should be
                'templates/xml_template.xml'.

        Returns
        -------
            bool: True if script is installed in correct location and not missing any additional files, False if not.

        Raises
        ------
            TypeError:
                If `additional_files` is not a list.

        Example
        -------
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

        # Validate Argument
        if not isinstance(additional_files, list):
            pyflame.raise_type_error('verify_script_install.additional_files', 'list', f'{type(additional_files).__name__}', additional_files)

        label = '--[ VALIDATING: Script Install ]'
        print(f'{label}{"-" * (80 - len(label))}')

        # Get script path info
        script_path = os.path.abspath(os.path.dirname(__file__))
        script_path = script_path.rsplit('/', 1)[0]
        root_path = os.path.dirname(script_path)
        script_folder_name = script_path.rsplit('/', 1)[1]
        script_file_name = os.path.basename(__file__)[12:-3]

        print('Script Path        :', script_path)
        print('Root Path          :', root_path)
        print('Script Folder Name :', script_folder_name)
        print('Script File Name   :', script_file_name + '.py')
        print('--------------------------------------------------------------------------------')

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
                message_type=MessageType.ERROR,
                parent=None,
                )
            print(f'[{TextColor.RED.value}FAILED{TextColor.RESET.value}] Script Install Verified\n')
            return False

        # Check script folder for write permissions
        if not os.access(script_path, os.W_OK):
            PyFlameMessageWindow(
                message=(
                    'Script folder is not writable. \n\n'
                    'Please check permissions and try again.'
                    ),
                message_type=MessageType.ERROR,
                parent=None,
                )
            print(f'[{TextColor.RED.value}FAILED{TextColor.RESET.value}] Script Install Verified\n')
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
                        message_type=MessageType.ERROR,
                        parent=None,
                        )
                    print(f'[{TextColor.RED.value}FAILED{TextColor.RESET.value}] Script Install Verified\n')
                    return False
                else:
                    pyflame.print(f'{file} -> Found', text_color=TextColor.GREEN, new_line=False)

        print(f'[{TextColor.GREEN.value}VERIFIED{TextColor.RESET.value}] Script Install Verified\n')
        return True

    @staticmethod
    def create_media_panel_libraries(library_structure: dict[str, Any]) -> None:
        """
        Create Media Panel Library
        ==========================

        Create libraries/folders in the media panel based on the provided library/folder structure.

        Tokens can be used in library/folder names.

        Args
        ----
            `library_structure` (dict):
                A dictionary representing the library/folder structure to be created.
                'Workspace' should always be the top level key.

        Raises
        ------
            TypeError:
                If `library_structure` is not a dictionary.
            ValueError:
                If 'Workspace' is not the only top-level key in `library_structure`.

        Example
        -------
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

        # Validate Argument
        if not isinstance(library_structure, dict):
            pyflame.raise_type_error('pyflame.create_media_panel_libraries', 'library_structure', 'dict', value)

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
    def create_media_panel_folder(folder_name: str, folder_structure: dict[str, Any], dest: flame.PyFolder | flame.PyLibrary, shot_name_tag: str='') -> None:
        """
        Create Media Panel Folder
        =========================

        Create a folder in the media panel based on the provided folder structure. Tokens can be used in folder names.

        By default folders are tagged with the shot name token.

        Args
        ----
            `folder_name` (str):
                Name of the main folder to create in the media panel.

            `folder_structure` (dict):
                A dictionary representing the folder structure to be created.

            `dest` (Folder):
                The destination folder/library in the Media Panel where the main folder will be created.

            `shot_name_tag` (str):
                Use to add ShotName tag to folder with matching name. If shot_name_tag is PYT_0010 any folder named PYT_0010 will be tagged with 'ShotName: PYT_0010'.
                (Default: ``)

        Raises
        ------
            TypeError:
                If `folder_name` is not a string.
                If `folder_structure` is not a dictionary.
                If `dest` is not a flame.PyFolder or flame.PyLibrary.
                If `shot_name_tag` is not a string.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(folder_name, str):
            pyflame.raise_type_error('pyflame.create_media_panel_folder', 'folder_name', 'str', folder_name)
        if not isinstance(folder_structure, dict):
            pyflame.raise_type_error('pyflame.create_media_panel_folder', 'folder_structure', 'dict', folder_structure)
        if not isinstance(dest, (flame.PyFolder, flame.PyLibrary)):
            pyflame.raise_type_error('pyflame.create_media_panel_folder', 'dest', 'flame.PyFolder | flame.PyLibrary', dest)
        if not isinstance(shot_name_tag, str):
            pyflame.raise_type_error('pyflame.create_media_panel_folder', 'shot_name_tag', 'str', shot_name_tag)

        def create_sub_folders(folders, parent_folder):
            """
            Create Sub-Folders
            ==================

            Recursively create sub-folders based on the provided folder structure.

            Args
            ----
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
    def create_media_panel_folders(folder_list: list[str], folder_structure: dict[str, Any], dest: flame.PyFolder | flame.PyLibrary) -> None:
        """
        Create Media Panel Folders
        ==========================

        Create folders in the Media Panel from a list of folder names. Tokens can be used in folder names.

        Args
        ----
            `folder_list` (list[str]):
                List of folder names to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest` (Folder):
                The destination folder/library in the Media Panel where the folders will be created.

        Raises
        ------
            TypeError:
                If `folder_list` is not a list.
                If `folder_structure` is not a dictionary.
                If `dest` is not a flame.PyFolder or flame.PyLibrary.

        Notes
        -----
            Tokens can be used in folder names.

            Uses _PyFlame.create_media_panel_folder() to create each folder in list.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(folder_list, list):
            pyflame.raise_type_error('pyflame.create_media_panel_folders', 'folder_list', 'list', folder_list)
        if not isinstance(folder_structure, dict):
            pyflame.raise_type_error('pyflame.create_media_panel_folders', 'folder_structure', 'dict', folder_structure)
        if not isinstance(dest, (flame.PyFolder, flame.PyLibrary)):
            pyflame.raise_type_error('pyflame.create_media_panel_folders', 'dest', 'flame.PyFolder | flame.PyLibrary', dest)

        pyflame.print('Creating Media Panel Folders...')
        pyflame.print('Folder Structure:', underline=True, print_to_flame=False, text_color=TextColor.BLUE)
        pyflame.print_dict(folder_structure)

        for folder_name in folder_list:
            _PyFlame.create_media_panel_folder(folder_name, folder_structure, dest, folder_name)

    @staticmethod
    def create_file_system_folder(folder_name: str, folder_structure: dict[str, Any], dest_path: str, skip_existing: bool=False) -> None:
        """
        Create File System Folder
        =========================

        Create a folder in the file system based on the provided folder structure. Tokens can be used in folder names.

        Args
        ----
            `folder_name` (str):
                Name of the main folder to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest_path` (str):
                Path where folders will be created.

            `skip_existing` (bool):
                Skip creating folders if they already exist.

        Raises
        ------
            TypeError:
                If `folder_name` is not a string.
                If `folder_structure` is not a dictionary.
                If `dest_path` is not a string.
                If `skip_existing` is not a boolean.

        Example
        -------
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

            Args
            ----
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
            pyflame.raise_type_error('pyflame.create_file_system_folder', 'folder_name', 'str', folder_name)
        if not isinstance(folder_structure, dict):
            pyflame.raise_type_error('pyflame.create_file_system_folder', 'folder_structure', 'dict', folder_structure)
        if not isinstance(dest_path, str):
            pyflame.raise_type_error('pyflame.create_file_system_folder', 'dest_path', 'str', dest_path)
        if not isinstance(skip_existing, bool):
            pyflame.raise_type_error('pyflame.create_file_system_folder', 'skip_existing', 'bool', skip_existing)

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

        Args
        ----
            `folder_list` (list[str]):
                List of folder names to create.

            `folder_structure` (dict):
                Dictionary representing the folder structure to create.

            `dest_path` (str):
                Path where folders will be created.

        Raises
        ------
            TypeError:
                If `folder_list` is not a list.
                If `folder_structure` is not a dictionary.
                If `dest_path` is not a string.

        Notes
        -----
            Tokens can be used in folder names.

            Uses _PyFlame.create_file_system_folder() to create each folder in list.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(folder_list, list):
            pyflame.raise_type_error('pyflame.create_file_system_folders', 'folder_list', 'list', folder_list)
        if not isinstance(folder_structure, dict):
            pyflame.raise_type_error('pyflame.create_file_system_folders', 'folder_structure', 'dict', folder_structure)
        if not isinstance(dest_path, str):
            pyflame.raise_type_error('pyflame.create_file_system_folders', 'dest_path', 'str', dest_path)

        pyflame.print('Creating File System Folders', text_color=TextColor.GREEN)
        pyflame.print('Folder Structure:', underline=True, print_to_flame=False, text_color=TextColor.BLUE)
        pyflame.print_dict(folder_structure)

        for folder_name in folder_list:
            _PyFlame.create_file_system_folder(folder_name, folder_structure, dest_path)

    @staticmethod
    def copy_to_clipboard(value: str | int) -> None:
        """
        Copy to Clipboard
        =================

        Copy string(text) to clipboard using QT.

        Args
        ----
            `value` (str | int):
                Text or integer to copy to clipboard.

        Raises
        ------
            TypeError:
                If `value` is not a string or integer.

        Example
        -------
            To copy text to clipboard:
            ```
            pyflame.copy_to_clipboard('Text to copy to clipboard.')
            ```
            To copy an integer to clipboard:
            ```
            pyflame.copy_to_clipboard(12345)
            ```
        """

        # Validate Argument type
        if not isinstance(value, str | int):
            pyflame.raise_type_error('pyflame.copy_to_clipboard', 'value', 'str | int', value)

        # Convert value to string if it is an integer
        if isinstance(value, int):
            value = str(value)

        # Copy path to clipboard
        qt_app_instance = QtWidgets.QApplication.instance()
        qt_app_instance.clipboard().setText(value)

        pyflame.print(f'Copied to Clipboard', text_color=TextColor.GREEN)

    @staticmethod
    def print(text: str, indent: int=0, print_type=PrintType.INFO, new_line: bool=True, arrow: bool=False, underline: bool=False, double_underline: bool=False, text_color: TextColor | None=None, time: int=3, print_to_flame: bool=True, script_name: str=SCRIPT_NAME) -> None:
        """
        Print
        =====

        Print text to the terminal and Flame message area.

        Args
        ----
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
        -------------
        - `PrintType.INFO`: Prints text in default color.
        - `PrintType.ERROR`: Printed text will be yellow.
        - `PrintType.WARNING`: Printed text will be red.

        Text Color:
        -----------
        - `TextColor.GREEN`: Green text.
        - `TextColor.YELLOW`: Yellow text.
        - `TextColor.RED`: Red text.
        - `TextColor.WHITE`: White text.
        - `TextColor.BLUE`: Blue text.
        - `TextColor.RESET`: Reset text color to default.

        Raises
        ------
        TypeError:
            If `text` is not a string.
            If `indent` is not an integer.
            If `new_line`, `arrow`, `underline`, or `double_underline` is not a boolean.
            If `time` is not an integer.
            If `script_name` is not a string.
            If `text_color` is not a TextColor.
        ValueError:
            If `type` is not a valid PrintType.

        Example
        -------
            To print some text:
            ```
            pyflame.print('This is some text.')
            ```

            To print indented text:
            ```
            pyflame.print('This is some indented text.', indent=4)
            ```
        """

        # Validate Arguments
        if not isinstance(text, str):
            pyflame.raise_type_error('pyflame.print', 'text', 'str', text)
        if not isinstance(indent, int):
            pyflame.raise_type_error('pyflame.print', 'indent', 'int', indent)
        if not isinstance(new_line, bool):
            pyflame.raise_type_error('pyflame.print', 'new_line', 'bool', new_line)
        if not isinstance(arrow, bool):
            pyflame.raise_type_error('pyflame.print', 'arrow', 'bool', arrow)
        if not isinstance(underline, bool):
            pyflame.raise_type_error('pyflame.print', 'underline', 'bool', underline)
        if not isinstance(double_underline, bool):
            pyflame.raise_type_error('pyflame.print', 'double_underline', 'bool', double_underline)
        if not isinstance(time, int):
            pyflame.raise_type_error('pyflame.print', 'time', 'int', time)
        if not isinstance(script_name, str):
            pyflame.raise_type_error('pyflame.print', 'script_name', 'str', script_name)
        if not isinstance(print_type, PrintType):
            pyflame.raise_type_error('pyflame.print', 'print_type', 'Print Enum - PrintType.INFO, PrintType.ERROR, PrintType.WARNING', print_type)
        if text_color is not None and not isinstance(text_color, TextColor):
            pyflame.raise_type_error('pyflame.print', 'text_color', 'None | TextColor Enum - TextColor.GREEN, TextColor.YELLOW, TextColor.RED, TextColor.WHITE, TextColor.BLUE, TextColor.RESET', text_color)

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
        color = ''
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
            print(f'{color}{"-" * 80}{TextColor.RESET.value}') # Print underline
        if double_underline:
            print(f'{color}{"=" * 80}{TextColor.RESET.value}') # Print double underline
        if new_line:
            print('\n', end='')

        # Print to Flame Message Window
        # Warning and error intentionally swapped to match color of message window
        if print_to_flame:
            if print_type == PrintType.INFO:
                flame.messages.show_in_console(f'{script_name}: {original_text}', 'info', time)
            elif print_type == PrintType.ERROR:
                flame.messages.show_in_console(f'{script_name}: {original_text}', 'warning', time)
            elif print_type == PrintType.WARNING:
                flame.messages.show_in_console(f'{script_name}: {original_text}', 'error', time)

    @staticmethod
    def print_dict(dict_data: dict[str, Any], indent: int=0) -> None:
        """
        Print Dict
        ==========

        Cleanly prints nested dictionaries with indentation to the terminal.

        Args
        ----
            `dict_data` (dict):
                Dictionary to print.

            `indent` (int):
                Indentation level.
                (Default: `0`)

        Raises
        ------
            TypeError:
                If `dict_data` is not a dictionary.
                If `indent` is not an integer.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(dict_data, dict):
            pyflame.raise_type_error('pyflame.print_dict', 'dict_data', 'dict', dict_data)
        if not isinstance(indent, int):
            pyflame.raise_type_error('pyflame.print_dict', 'indent', 'int', indent)

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

        Args
        ----
            `json_data` (dict | list | str | int | bool):
                JSON data to print.

            `indent` (int):
                Indentation level.
                (Default: `0`)

        Raises
        ------
            TypeError:
                If `indent` is not an integer.

        Example
        -------
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

        # Validate Argument type
        if not isinstance(indent, int):
            pyflame.raise_type_error('pyflame.print_json', 'indent', 'int', indent)

        original_indent = indent  # Store the original indent level

        print_to_terminal(json_data, indent)

        print()  # Ensure a single new line after all the data is printed

    @staticmethod
    def print_list(list_name: str, list_items: list, indent=0, time: int=3, script_name: str=SCRIPT_NAME) -> None:
        """
        Print List
        ===========

        Print a list of items to the terminal and Flame message area.

        Args
        ----
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

        Raises
        ------
            TypeError:
                If `list_name` is not a string.
                If `list_items` is not a list.
                If any item in `list_items` is not a string.
                If `indent` is not an integer.
                If `time` is not an integer.
                If `script_name` is not a string.

            ValueError:
                If `list_items` is not a list of strings.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(list_name, str):
            pyflame.raise_type_error('pyflame.print_list', 'text', 'str', text)
        if not isinstance(list_items, list):
            pyflame.raise_type_error('pyflame.print_list', 'list_items', 'list', list_items)
        for item in list_items:
            if not isinstance(item, str):
                pyflame.raise_type_error('pyflame.print_list', 'list_items: item', 'str', item)
        if not isinstance(indent, int):
            pyflame.raise_type_error('pyflame.print_list', 'indent', 'int', indent)
        if not isinstance(time, int):
            pyflame.raise_type_error('pyflame.print_list', 'time', 'int', time)
        if not isinstance(script_name, str):
            pyflame.raise_type_error('pyflame.print_list', 'script_name', 'str', script_name)

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
    def generate_unique_node_names(node_names: list[str], existing_node_names: list[str]) -> list[str]:
        """
        Generate Unique Node Names
        ==========================

        Generate unique node names based on the provided list of node names, ensuring that each new node
        name does not conflict with names in a given list of existing node names. If a conflict is found,
        the function appends an incrementing number to the original name until a unique name is created.

        Args
        ----
            `node_names` (list[str]):
                List of node names that need to be checked and possibly modified to ensure uniqueness.

            `existing_node_names` (list[str]):
                List of already existing node names against which the new node names will be checked for uniqueness.

        Returns
        -------
            list[str]:
                A list of new unique node names. Each name in this list is guaranteed to be unique against the provided list of existing node names.

        Raises
        ------
            TypeError:
                If `node_names` is not a list.
                If `existing_node_names` is not a list.
            ValueError:
                If any element in `node_names` is not a string.
                If any element in `existing_node_names` is not a string.

        Example
        -------
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

        # Validate Arguments
        if not isinstance(node_names, list):
            pyflame.raise_type_error('pyflame.generate_unique_node_names', 'node_names', 'list', node_names)
        for name in node_names:
            if not isinstance(name, str):
                pyflame.raise_type_error('pyflame.generate_unique_node_names', 'node_names: name', 'str', name)
        if not isinstance(existing_node_names, list):
            pyflame.raise_type_error('pyflame.generate_unique_node_names', 'existing_node_names', 'list', existing_node_names)
        for name in existing_node_names:
            if not isinstance(name, str):
                pyflame.raise_type_error('pyflame.generate_unique_node_names', 'existing_node_names: name', 'str', name)

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
    def generate_unique_name(value: str, existing_names: list[str]) -> str:
        """
        Generate Unique Names
        =====================

        Generate unique names based on the provided list of names, ensuring that each new name does not conflict with names in a given list of existing names.
        If a conflict is found, the function appends an incrementing number to the original name until a unique name is created.

        Args
        ----
            `value` (str):
                Value to check for uniqueness.

            `existing_names` (list[str]):
                List of already existing names against which the new name will be checked for uniqueness.

        Returns
        -------
            string:
                A new unique name.

        Raises
        ------
            TypeError:
                If `value` is not a string.
                If `existing_names` is not a list.
                If any element in `existing_names` is not a string.

        Example
        -------
            To generate a unique name:
            ```
            generate_unique_name(
                value='Thing',
                existing_names=[
                    'Thing1',
                    'Thing2',
                    'Thing3'
                    ]
                )
            ```
        """

        # Validate Arguments
        if not isinstance(value, str):
            pyflame.raise_type_error('pyflame.generate_unique_name', 'value', 'str', value)
        if not isinstance(existing_names, list):
            pyflame.raise_type_error('pyflame.generate_unique_name', 'existing_names', 'list', existing_names)
        if not all(isinstance(name, str) for name in existing_names):
            pyflame.raise_type_error('pyflame.generate_unique_name', 'existing_names', 'list', existing_names)

        # Append ' Copy' to value if it already exists in existing_names until a unique name is created
        original_value = value
        while value in existing_names:
            value = f'{value} Copy' if value == original_value else f'{value} Copy'

        return value

    @staticmethod
    def get_flame_version() -> float:
        """
        Get Flame Version
        =================

        Gets version of flame and returns float value.

        Returns
        -------
            `flame_version` (float): 2022.0
                2022 -> 2022.0
                2022.1.1 -> 2022.1
                2022.1.pr145 -> 2022.1

        Example
        -------
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

        Args
        ----
            `print_path` (bool):
                Print path to terminal.
                (Default: `True`)

        Returns
        -------
            `python_packages_path` (str):
                Path to Flame's python packages folder.

        Raises
        ------
            FileNotFoundError:
                If no python3.* folder is found in the python lib path.

        Example
        -------
            To get the path to Flame's python packages folder:
            ```
            python_packages_path = pyflame.pyflame_get_flame_python_packages_path()
            ```
        """

        # Validate Argument
        if not isinstance(print_path, bool):
            pyflame.raise_type_error('pyflame.get_flame_python_packages_path', 'print_path', 'bool', print_path)

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
    def file_browser(
        path: str='/opt/Autodesk',
        title: str | None=None,
        extension: str | List[str] | None=None,
        select_directory: bool=False,
        multi_selection: bool=False,
        include_resolution: bool=False,
        use_flame_browser: bool=True,
        window_to_hide: QtWidgets.QWidget | list[QtWidgets.QWidget] | None=None,
        ) -> str | list | None:
        """
        File Browser
        ============

        Opens Flame's file browser or QT file browser window.

        Args
        ----
            `path` (str):
                Open file browser to this path.
                (Default: `'/opt/Autodesk'`)

            `title` (str):
                File browser window title.
                If `None`, the title will be set to 'Select Directory' or 'Select File' based on the `extension` and `select_directory` arguments.
                (Default: `None`)

            `extension` (str | list):
                File extension filter. None to list directories.
                Can be a single extension or a list of extensions.
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
                Use Flame's file browser. If `False`, QT file browser will be used.
                (Default: `True`)

            `window_to_hide` (QtWidgets.QWidget | list[QtWidgets.QWidget]):
                Hide Qt window while Flame file browser window is open. Window is restored when browser is closed.
                Can be a single window or a list of windows.
                (Default: `None`)

        Returns
        -------
            `path` (str, list):
                Path to selected file or directory as a string.
                When `multi_selection` is enabled, the file browser will return a list.

        Example
        -------
            To open a file browser:
            ```
            path = pyflame_file_browser(
                path=self.undistort_map_path,
                title='Load Undistort ST Map(EXR)',
                extension=['exr'],
                )
            ```
        """

        # Validate Arguments
        if not isinstance(path, str):
            pyflame.raise_type_error('pyflame.file_browser', 'path', 'str', path)
        if not isinstance(title, str):
            pyflame.raise_type_error('pyflame.file_browser', 'title', 'str', title)
        if extension is not None and not isinstance(extension, (str, list)):
            pyflame.raise_type_error('pyflame.file_browser', 'extension', 'str or list', extension)
        if not isinstance(select_directory, bool):
            pyflame.raise_type_error('pyflame.file_browser', 'select_directory', 'bool', select_directory)
        if not isinstance(multi_selection, bool):
            pyflame.raise_type_error('pyflame.file_browser', 'multi_selection', 'bool', multi_selection)
        if not isinstance(include_resolution, bool):
            pyflame.raise_type_error('pyflame.file_browser', 'include_resolution', 'bool', include_resolution)
        if not isinstance(use_flame_browser, bool):
            pyflame.raise_type_error('pyflame.file_browser', 'use_flame_browser', 'bool', use_flame_browser)
        if window_to_hide is not None and not isinstance(window_to_hide, (QtWidgets.QWidget, list)):
            pyflame.raise_type_error('pyflame.file_browser', 'window_to_hide', 'PyFlameWindow or Qt Window', window_to_hide)

        # Set title if None is passed
        if not title and not extension:
            title = 'Select Directory'
        elif not title and extension:
            title = 'Select File'

        # If path is not valid, recursively move up path until one is found. If no valid path is found go to /opt/Autodesk.
        while os.path.isdir(path) is not True:
            path = path.rsplit('/', 1)[0]
            if '/' not in path and not os.path.isdir(path):
                path = '/opt/Autodesk'
            print('Browser path:', path, '\n')

        # Open Flame File Browser otherwise open Qt File Browser
        if use_flame_browser:

            # Hide Window while file browser is open
            if window_to_hide:
                windows = window_to_hide if isinstance(window_to_hide, list) else [window_to_hide]
                for window in windows:
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

            # Restore Hidden Windows
            if window_to_hide:
                windows = window_to_hide if isinstance(window_to_hide, list) else [window_to_hide]
                for window in windows:
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
                # Normalize extension to a list
                extensions = [extension] if isinstance(extension, str) else extension
                filter_str = ';;'.join(f'*.{ext}' for ext in extensions)
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

        Args
        ----
            `path` (str):
                Path to open in Finder.
        """

        # Validate Argument
        if not isinstance(path, str):
            pyflame.raise_type_error('pyflame.open_in_finder', 'path', 'str', path)

        # Print message if path does not exist and return
        if not os.path.exists(path):
            pyflame.print(
                text=f'Path does not exist: {path}',
                print_type=PrintType.ERROR,
            )
            return

        # Open path in Finder or File Explorer
        if platform.system() == 'Darwin':
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])

        pyflame.print(f'Opening path in Finder: {path}')

    @staticmethod
    def raise_type_error(source_name: str | None=None, arg_name: str | None=None, expected_type: str | None=None, actual_value: Any=None, error_message: str | None=None, time: int=10) -> None:
        """
        Raise Type Error
        =================

        Print error message to Flame and Terminal/Shell then raise TypeError.

        Args
        ----
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
    def raise_value_error(source_name: str | None=None, arg_name: str | None=None, expected_value: Any=None, actual_value: Any=None, error_message: str | None=None, time: int=10) -> None:
        """
        Raise Value Error
        =================

        Print error message to Flame and Terminal/Shell then raise ValueError.

        Args
        ----
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

        Args
        ----
            `script_name` (str):
                Name of script. This is displayed in the Flame message area.
                (Default: `SCRIPT_NAME`)

        Raises
        ------
            TypeError:
                If `script_name` is not a string.

        Example
        -------
            To refresh python hooks:
            ```
            pyflame.refresh_hooks()
            ```
        """

        # Validate Argument
        if not isinstance(script_name, str):
            pyflame.raise_type_error('pyflame.refresh_hooks', 'script_name', 'str', script_name)

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

        Args
        ----
            `tokenized_string` (str):
                String with tokens to be translated.

            `flame_pyobject` (flame.PyClip, optional):
                Flame PyClip/PySegment/PyBatch Object.
                (Default: `None`)

            `date` (datetime, optional):
                Date/time to use for token translation. If None is passed datetime value will be gotten each time function is run.
                (Default: `None`)

        Supported tokens:
        ----------------
            <ProjectName>, <ProjectNickName>, <UserName>, <UserNickName>, <YYYY>, <YY>, <MM>, <DD>, <Hour>, <Minute>, <AMPM>, <ampm>

            Additional tokens available when Flame PyObjects as passed in the flame_pyobject argument:
                PyClip and PySegment:
                    <ShotName>, <SeqName>, <SEQNAME>, <ClipName>, <Resolution>, <ClipHeight>, <ClipWidth>, <TapeName>
                PyBatch:
                    <BatchGroupName>, <ShotName>, <SeqName>, <SEQNAME>

        Returns
        -------
            `resolved_string` (str):
                String with resolved tokens.

        Raises
        ------
            TypeError:
                If `tokenized_string` is not a string.

        Example
        -------
            To resolve path tokens:
            ```
            export_path = pyflame.translate_path_tokens(
                tokenized_string=custom_export_path,
                flame_pyobject=clip,
                date=date
                )
            ```
        """

        # Validate Argument types
        if not isinstance(tokenized_string, str):
            pyflame.raise_type_error('pyflame.resolve_tokens', 'tokenized_string', 'str', tokenized_string)

        def get_seq_name(name):
            """
            Get sequence name abreviation from shot name
            """

            seq_name = re.split('[^a-zA-Z]', name)[0]
            return seq_name

        pyflame.print('Resolving Tokens', new_line=False)
        print('----------------')

        print('Checking for tokens in string:', tokenized_string)

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
        if flame_pyobject:
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

                    Args
                    ----
                        `segment` (flame.PySegment):
                            Flame PySegment object.

                        `resolved_path` (str):
                            Resolved path with tokens.

                    Returns
                    -------
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

                    Args
                    ----
                        `batch` (flame.PyBatch):
                            Flame PyBatch object.

                        `resolved_path` (str):
                            Resolved path with tokens.

                    Returns
                    -------
                        `resolved_path` (str):
                            Resolved path with tokens.
                    """

                    def get_shot_name_tag(batch) -> str | None:
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

                    def get_shot_name_from_render_nodes(batch) -> str | None:
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

        Args
        ----
            `name` (str):
                The name to be resolved into a shot name.

        Returns
        -------
            str: The resolved shot name.

        Raises
        ------
            TypeError:
                If `name` is not a string.

        Examples
        --------
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

        # Validate Argument types
        if not isinstance(name, str):
            pyflame.raise_type_error('pyflame.resolve_shot_name', 'name', 'str', name)

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
    def untar(tar_file_path: str, untar_path: str, sudo_password: str | None=None) -> bool:
        """
        Untar
        =====

        Untar a tar file.

        Args
        ----
            `tar_file_path` (str):
                Path to tar file to untar including filename.tgz/tar.

            `untar_path` (str):
                Untar destination path.

            `sudo_password` (bool, optional):
                Password for sudo.
                (Default: `None`)

        Returns
        -------
            bool: True if untar successful, False if not.

        Example
        -------
            To untar a file:
            ```
            pyflame.unzip('/home/user/file.tar', '/home/user/untarred')
            ```
        """

        # Validate Arguments
        if not isinstance(tar_file_path, str):
            pyflame.raise_type_error('pyflame.untar', 'tar_file_path', 'str', tar_file_path)
        if not isinstance(untar_path, str):
            pyflame.raise_type_error('pyflame.untar', 'untar_path', 'str', untar_path)
        if sudo_password is not None and not isinstance(sudo_password, str):
            pyflame.raise_type_error('pyflame.untar', 'None | sudo_password', 'str', sudo_password)

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

        Args
        ----
            `value` (int):
                Value to be scaled.

        Returns
        -------
            int:
                The value scaled for the current screen resolution.

        Example
        -------
            To resize a window:
            ```
            self.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))
            ```
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('pyflame.gui_resize', 'value', 'int', value)

        # Baseline resolution from mac studio display
        base_screen_height = 3190

        # Get current screen resolution
        main_window_res = pyflame.window_resolution()
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

        Args
        ----
            `value` (int):
                Value to be scaled.

        Returns
        -------
            int:
                The font size value scaled for the current screen resolution.

        Example
        -------
            To resize a font:
            ```
            font.setPointSize(pyflame.font_resize(13)
            ```
        """

        # Validate Argument types
        if not isinstance(value, int):
            pyflame.raise_type_error('pyflame.font_resize', 'value', 'int', value)

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

        Args
        ----
            `preset_path` (str):
                Path of preset to check/update.

        Returns
        -------
            `current_export_version` (str):
                Version of current preset export.

            `export_version` (str):
                Export preset version for currernt version of Flame.

        Example
        -------
            To get the export preset version:
            ```
            current_export_version, export_version = pyflame.get_export_preset_version(preset_path)
            ```

        Note:
        ----
            Scripts that use this:
                Create Export Menus
                SynthEyes Export
                Create Shot
        """

        # Validate Argument types
        if not isinstance(preset_path, str):
            pyflame.raise_type_error('pyflame.get_export_preset_version', 'preset_path', 'str', preset_path)

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
            current_export_version = None
            for setting in root.iter('preset'):
                current_export_version = setting.get('version')
                print(f'    Current export preset version: {current_export_version}')

            return str(current_export_version) if current_export_version is not None else ''

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
            default_export_version = None
            for setting in root.iter('preset'):
                default_export_version = setting.get('version')
                print(f'    Flame default export preset version: {default_export_version}')
                print('\n', end='')

            return str(default_export_version) if default_export_version is not None else ''

        current_export_version = get_current_export_version(preset_path)
        export_version = get_export_version()

        return current_export_version, export_version

    @staticmethod
    def update_export_preset(preset_path: str) -> None:
        """
        Update Export Preset
        ====================

        Update export preset file version to match current version of flame being used.

        Args
        ----
            `preset_path` (str):
                Path of preset to check/update.

        Example
        -------
            To update the export preset:
            ```
            pyflame.update_export_preset(preset_path)
            ```
        """

        # Validate Argument types
        if not isinstance(preset_path, str):
            pyflame.raise_type_error('pyflame.update_export_preset', 'preset_path', 'str', preset_path)

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

        Args
        ----
            `existing_names` (list of str):
                A list of existing names.

            `new_name` (str):
                The base name to be made unique.

        Returns
        -------
            str:
                A unique name not present in the existing_names list.

        Example
        -------
            To generate a unique name:
            ```
            unique_name = pyflame.iterate_name(existing_names, new_name)
            ```
        """

        # Validate Arguments
        if not isinstance(existing_names, list):
            pyflame.raise_type_error('pyflame.iterate_name', 'existing_names', 'list', existing_names)
        for name in existing_names:
            if not isinstance(name, str):
                pyflame.raise_type_error('pyflame.iterate_name', 'existing_names: name', 'str', name)
        if not isinstance(new_name, str):
            pyflame.raise_type_error('pyflame.iterate_name', 'new_name', 'str', new_name)

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

        Returns
        -------
            list[str]:
                A list of export preset names.
        """

        print('Getting Export Presets:\n')

        project_file_sequence_path = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/file_sequence')
        project_movie_export_path = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/movie_file')

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
        if os.path.isdir(project_file_sequence_path):
            project_file_sequence_export_presets = [f'Project: File Sequence: {p[:-4]}' for p in os.listdir(project_file_sequence_path) if p.endswith('.xml')]
        else:
            project_file_sequence_export_presets = []
            print('Project File Sequence Export Presets path does not exist:', project_file_sequence_path, '\n')

        # Get Project Movie Export Presets
        if os.path.isdir(project_movie_export_path):
            project_movie_export_presets = [f'Project: Movie: {p[:-4]}' for p in os.listdir(project_movie_export_path) if p.endswith('.xml')]
        else:
            project_movie_export_presets = []
            print('Project Movie Export Presets path does not exist:', project_movie_export_path, '\n')

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

        Args
        ----
            export_preset_name (str):
                Export preset name to convert to path.
                Example 'Shared: File Sequence: Jpeg (8-bit)'

        Returns
        -------
            str:
                Path to export preset.

        Raises
        ------
            TypeError:
                If 'export_preset_name' is not a string.

        Example
        -------
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

        # Validate Argument
        if not isinstance(export_preset_name, str):
            pyflame.raise_type_error('pyflame.convert_export_preset_name_to_path', 'export_preset_name', 'str', export_preset_name)

        project_file_sequence_path = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/file_sequence')
        project_movie_export_path = os.path.join('/opt/Autodesk/', f'{flame.projects.current_project.name}', 'export/presets/flame/movie_file')

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
            print('Project: File Sequence:', os.path.join(project_file_sequence_path, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(project_file_sequence_path, f'{export_preset_name.split(": ")[2]}.xml')
        elif 'Project: Movie:' in export_preset_name:
            print('Project: Movie:', os.path.join(project_movie_export_path, f'{export_preset_name.split(": ")[2]}.xml'))
            return os.path.join(project_movie_export_path, f'{export_preset_name.split(":")[2]}.xml')
        else:
            return ''

    @staticmethod
    def set_shot_tagging(pyobject: flame.PyLibrary | flame.PyFolder | flame.PyDesktop | flame.PyBatch | flame.PyClip, shot_name: str, append: bool=False) -> None:
        """
        Set Shot Tagging
        ================

        Set shot tagging for Flame object.

        Tags can be appended to existing tags or set directly. Default is to set tag directly.

        Args
        ----
            pyobject (flame.PyObject):
                Flame object to set tagging for. Can be PyLibrary, PyFolder, PyDesktop, PyBatch, or PyClip.

            shot_name (str):
                Shot name to set as tag.

            append (bool, optional):
                Append shot name tag to existing tags.
                (Default: False)

        Raises
        ------
            TypeError:
                If 'pyobject' is not a PyLibrary, PyFolder, PyDesktop, PyBatch, or PyClip.
                If 'shot_name' is not a string.
                If 'append' is not a boolean.

        Notes
        -----
            - If appending tags, existing tags starting with ShotName: are removed before new tag is added.
        """

        # Validate Arguments
        if not isinstance(pyobject, (flame.PyLibrary, flame.PyFolder, flame.PyDesktop, flame.PyBatch, flame.PyClip)):
            pyflame.raise_type_error('pyflame.set_shot_tagging', 'pyobject', 'flame.PyLibrary | flame.PyFolder | flame.PyDesktop | flame.PyBatch | flame.PyClip', pyobject)
        if not isinstance(shot_name, str):
            pyflame.raise_type_error('pyflame.set_shot_tagging', 'shot_name', 'str', shot_name)
        if not isinstance(append, bool):
            pyflame.raise_type_error('pyflame.set_shot_tagging', 'append', 'bool', append)

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
    def find_by_tag(pyobject: flame.PyLibrary | flame.PyDesktop | flame.PyFolder, target_tag: str, sorted: bool=True):
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

        Args
        ----
            pyobject (flame.PyLibrary, flame.PyDesktop, or flame.PyFolder):
                Flame PyObject (Library, Desktop, or Folder) that will be searched for item with target tag.

            target_tag (str):
                Tag to search for. If contains ':', will match against tag_type:value format.

            sorted (bool):
                If True, assumes PyObjects contained within `pyobject` are sorted by tag.
                When True, performs a binary search. If False, performs a linear search.
                (Default: True)

        Returns
        -------
            The matching Flame PyObject if found, None otherwise.

        Examples
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

        # Validate Arguments
        if isinstance(pyobject, list):
            # Check if all items in the list are valid PyObject types
            if not all(isinstance(item, (flame.PyLibrary, flame.PyDesktop, flame.PyFolder)) for item in pyobject):
                pyflame.raise_type_error('pyflame.find_by_tag', 'pyobject', 'list[flame.PyLibrary | flame.PyDesktop | flame.PyFolder]', pyobject)
        elif not isinstance(pyobject, (flame.PyLibrary, flame.PyDesktop, flame.PyFolder)):
            pyflame.raise_type_error('pyflame.find_by_tag', 'pyobject', 'flame.PyLibrary | flame.PyDesktop | flame.PyFolder | list[flame.PyLibrary | flame.PyDesktop | flame.PyFolder]', pyobject)
        if not isinstance(target_tag, str):
            pyflame.raise_type_error('pyflame.find_by_tag', 'target_tag', 'str', target_tag)
        if not isinstance(sorted, bool):
            pyflame.raise_type_error('pyflame.find_by_tag', 'sorted', 'bool', sorted)

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
                pyobject_tag = None
                for tag in pyobject_tags:
                    if tag.startswith(tag_type):
                        pyobject_tag = tag
                        break

                # No matching tag type in this object, treat as "less than" target
                # and continue searching in the upper half.
                if pyobject_tag is None:
                    start = mid + 1
                    continue

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

        Args
        ----
            clip (flame.PyClip):
                Clip to get shot name from

        Returns
        -------
            shot_name (str):
                Shot name

        Notes
        -----
            - Check if clip has assigned Shot Name.
            - Check if clip is tagged with ShotName (ShotName: PYT_0010)
            - If no Shot Name is assigned or tagged, extract shot name from clip name.
        """

        # Validate Argument
        if not isinstance(clip, flame.PyClip):
            pyflame.raise_type_error('pyflame.shot_name_from_clip', 'clip', 'flame.PyClip', clip)

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

        # Check if numbders are in clip name and extract shot name from clip name
        if any(char.isdigit() for char in clip_name):

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
        else:
            shot_name = clip_name

        # Tag clip with shot name, pass if Flame 2025 or older
        try:
            pyflame.set_shot_tagging(clip, shot_name)
        except:
            pass

        pyflame.print(f'Shot Name from Clip Name: {shot_name}', text_color=TextColor.GREEN)

        return shot_name

    @staticmethod
    def get_media_panel_shot_folder(shot_name: str, pyobject: flame.PyClip | flame.PyBatch | flame.PyDesktop, search_location: flame.PyLibrary | flame.PyFolder, dest_folder_path: str) -> flame.PyFolder | None:
        """
        Get Media Panel Folder
        ======================

        Recursively find Media Panel shot folder from path. Path can be a single folder or a nested folder.

        Path should be in the following format:
            <shot_folder>/<folder_name>
            <shot_folder>/<folder_name>/<folder_name>
            ...

        If path is a single folder, return the folder.

        Args
        ----
            shot_name (str):
                Name of shot

            pyobject (flame.PyClip | flame.PyBatch | flame.PyDesktop):
                PyClip, PyBatch, or PyDesktop to move to shot folder.

            search_location (flame.PyLibrary | flame.PyFolder):
                Media Panel Library or Folder to search through for shot folder.

            dest_folder_path (str):
                Destination folder path in Shot Folder.
                Example 'Shot_Folder/Plates'

        Returns
        -------
            dest_folder (flame.PyFolder):
                Destination folder object.

        Examples
        --------
            Get shot folder from path:
            ```
            get_media_panel_shot_folder(
                shot_name='PYT_0010',
                pyobject=<PyClipObject>,
                search_location=<PyLibraryObject>,
                dest_folder_path='Shot_Folder/Plates'
            )
            ```
        """

        # Validate Arguments
        if not isinstance(shot_name, str):
            pyflame.raise_type_error('pyflame.get_media_panel_shot_folder', 'shot_name', 'str', shot_name)
        if not isinstance(pyobject, (flame.PyClip, flame.PyBatch, flame.PyDesktop)):
            pyflame.raise_type_error('pyflame.get_media_panel_shot_folder', 'pyobject', 'PyClip, PyBatch, or PyDesktop', pyobject)
        if not isinstance(search_location, (flame.PyLibrary, flame.PyFolder)):
            pyflame.raise_type_error('pyflame.get_media_panel_shot_folder', 'search_location', 'PyLibrary or PyFolder', search_location)
        if not isinstance(dest_folder_path, str):
            pyflame.raise_type_error('pyflame.get_media_panel_shot_folder', 'dest_folder_path', 'str', dest_folder_path)

        def get_folder_from_path(folder: flame.PyFolder, media_panel_folder_path: str) -> flame.PyFolder:
            """
            Get Folder from Path
            ====================

            Recursively find Media Panel folder from path

            Args
            ----
                folder (flame.PyFolder):
                    Media Panel Folder to search through for destination folder.

                media_panel_folder_path (str):
                    Media Panel destination folder path.
                    Example 'Shot_Folder/Plates'

            Returns
            -------
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

        # If dest_folder_path is a single folder, return shot_folder
        if '/' not in dest_folder_path:
            dest_folder = shot_folder
        else:
            # If dest_folder_path is a nested folder, recursively find the destination folder
            dest_folder = get_folder_from_path(shot_folder, dest_folder_path)

        return dest_folder

    @staticmethod
    def move_to_shot_folder(shot_name: str, pyobject: flame.PyClip | flame.PyBatch | flame.PyDesktop, search_location: flame.PyLibrary | flame.PyFolder, dest_folder_path: str, expand_dest_folder: bool=True) -> None:
        """
        Move to Shot Folder
        ===================

        Move PyClip, PyBatch, or PyDesktop to a Media Panel shot folder in search_location(flame.PyLibrary or flame.PyFolder)

        Folders in search location must be tagged with 'ShotName: <shot_name>', i.e. 'ShotName: PYT_0010'

        Args
        ----
            shot_name (str):
                Name of shot

            pyobject (flame.PyClip | flame.PyBatch | flame.PyDesktop):
                PyClip, PyBatch, or PyDesktop to move to shot folder.

            search_location (flame.PyLibrary | flame.PyFolder):
                Media Panel Library or Folder to search through for shot folder.

            dest_folder_path (str):
                Destination folder path in Shot Folder.
                Example 'Shot_Folder/Plates'

            expand_dest_folder (bool):
                Expands the destination folder after move is complete.
                (Default: True)

        Examples
        --------
            Move to shot folder:
            ```
            move_to_shot_folder(
                shot_name='PYT_0010',
                pyobject=<PyClipObject>,
                search_location=<PyLibraryObject>,
                dest_folder_path='Shot_Folder/Plates'
            )
            ```
        """

        # Validate Arguments
        if not isinstance(shot_name, str):
            pyflame.raise_type_error('pyflame.move_to_shot_folder', 'shot_name', 'str', shot_name)
        if not isinstance(pyobject, (flame.PyClip, flame.PyBatch, flame.PyDesktop)):
            pyflame.raise_type_error('pyflame.move_to_shot_folder', 'pyobject', 'PyClip, PyBatch, or PyDesktop', pyobject)
        if not isinstance(search_location, (flame.PyLibrary, flame.PyFolder)):
            pyflame.raise_type_error('pyflame.move_to_shot_folder', 'search_location', 'PyLibrary or PyFolder', search_location)
        if not isinstance(dest_folder_path, str):
            pyflame.raise_type_error('pyflame.move_to_shot_folder', 'dest_folder_path', 'str', dest_folder_path)
        if not isinstance(expand_dest_folder, bool):
            pyflame.raise_type_error('pyflame.move_to_shot_folder', 'expand_dest_folder', 'bool', expand_dest_folder)

        # Get Destination Folder
        dest_folder = pyflame.get_media_panel_shot_folder(shot_name, pyobject, search_location, dest_folder_path)

        # If Destination Folder is None, print error and return
        if dest_folder is None:
            pyflame.print(f'Shot Folder: {dest_folder_path} Not Found', text_color=TextColor.RED)
            return

        # Move PyObject to Destination Folder
        flame.media_panel.move(pyobject, dest_folder)

        # Expand Destination Folder
        if expand_dest_folder:
            dest_folder.expanded = True

    @staticmethod
    def copy_to_shot_folder(shot_name: str, pyobject: flame.PyClip | flame.PyBatch | flame.PyDesktop, search_location: flame.PyLibrary | flame.PyFolder, dest_folder_path: str, expand_dest_folder: bool=True) -> None:
        """
        Copy to Shot Folder
        ===================

        Copy PyClip, PyBatch, or PyDesktop to a Media Panel shot folder in search_location(flame.PyLibrary or flame.PyFolder)

        Folders in search location must be tagged with 'ShotName: <shot_name>', i.e. 'ShotName: PYT_0010'

        Args
        ----
            shot_name (str):
                Name of shot

            pyobject (flame.PyClip | flame.PyBatch | flame.PyDesktop):
                PyClip, PyBatch, or PyDesktop to copy to shot folder.

            search_location (flame.PyLibrary | flame.PyFolder):
                Media Panel Library or Folder to search through for shot folder.

            dest_folder_path (str):
                Destination folder path in Shot Folder.
                Example 'Shot_Folder/Plates'

            expand_dest_folder (bool):
                Expands the destination folder after copy is complete.
                (Default: True)

        Example
        -------
            Copy to shot folder:
            ```
            copy_to_shot_folder(
                shot_name='PYT_0010',
                pyobject=<PyClipObject>,
                search_location=<PyLibraryObject>,
                dest_folder_path='Shot_Folder/Plates'
            )
            ```
        """

        # Validate Arguments
        if not isinstance(shot_name, str):
            pyflame.raise_type_error('pyflame.copy_to_shot_folder', 'shot_name', 'str', shot_name)
        if not isinstance(pyobject, (flame.PyClip, flame.PyBatch, flame.PyDesktop)):
            pyflame.raise_type_error('pyflame.copy_to_shot_folder', 'pyobject', 'PyClip, PyBatch, or PyDesktop', pyobject)
        if not isinstance(search_location, (flame.PyLibrary, flame.PyFolder)):
            pyflame.raise_type_error('pyflame.copy_to_shot_folder', 'search_location', 'PyLibrary or PyFolder', search_location)
        if not isinstance(dest_folder_path, str):
            pyflame.raise_type_error('pyflame.copy_to_shot_folder', 'dest_folder_path', 'str', dest_folder_path)
        if not isinstance(expand_dest_folder, bool):
            pyflame.raise_type_error('pyflame.copy_to_shot_folder', 'expand_dest_folder', 'bool', expand_dest_folder)


        # Get Destination Folder
        dest_folder = pyflame.get_media_panel_shot_folder(shot_name, pyobject, search_location, dest_folder_path)

        # If Destination Folder is None, print error and return
        if dest_folder is None:
            pyflame.print(f'Shot Folder: {dest_folder_path} Not Found', text_color=TextColor.RED)
            return

        # Copy PyObject to Destination Folder
        flame.media_panel.copy(pyobject, dest_folder)

        # Expand Destination Folder
        if expand_dest_folder:
            dest_folder.expanded = True

pyflame = _PyFlame

def _load_font():
    """
    Load Font
    =========

    Load font from path for use in all PyFlame QT Widgets.

    If font is not found, Discreet font is used as a fallback.

    Args
    ----
        font_path (dict):
            Name and path to font in dictionary form.

    Returns
    -------
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
                #print(f'PyFlameLib: Font Successfully Loaded: {font_family}: {font_name}')
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

# ==============================================================================
# [Misc Classes]
# ==============================================================================

class PyFlameToolTip:
    """
    PyFlameToolTip
    ==============

    Custom QT Tooltip for PyFlameWidgets.

    Add this line to the widget __init__ method to create the widget tooltip:
        ```
        self.tooltip = PyFlameToolTip(self)
        ```

    Add Tooltip Properties(Reference existing widgets for these properties):
        tooltip - set tooltip text
        tooltip_delay - set time before tooltip shows
        tooltip_duration - set time tooltip shows for

    Add Tooltip Event Handler methods to widget(Reference existng widgets for these methods):
        enterEvent()
        leaveEvent()

    Args
    ----
        `parent_widget` (QtWidgets.QWidget):
            Parent widget to display tooltip.

        `text` (str):
            Text to display in tooltip.
            (Default: '')

        `delay` (int):
            Delay in seconds before tooltip is displayed.
            (Default: 3)

        `duration` (int):
            Duration in seconds tooltip is displayed.
            (Default: 5)

    Properties
    ----------
        `widget` (QtWidgets.QWidget):
            Get or set parent widget.

        `text` (str):
            Get or set tooltip text.
            (Default: '')

        `delay` (int):
            Get or set tooltip delay in seconds.
            (Default: 3)

        `duration` (int):
            Get or set tooltip duration in seconds.
            (Default: 5)

    Methods
    -------
        `enter_event()`:
            Show tooltip when mouse enters widget.

        `leave_event()`:
            Hide tooltip when mouse leaves widget.

    """

    def __init__(self: 'PyFlameToolTip',
                 parent_widget: QtWidgets.QWidget,
                 text: str='',
                 delay: int=3,
                 duration: int=5
                 ) -> None:

        # Create Tooltip Display Label
        self._label = PyFlameLabel()
        self._label.setWindowFlags(QtCore.Qt.ToolTip | QtCore.Qt.FramelessWindowHint)
        self._label.hide()

        self._label.setStyleSheet(f"""
                QLabel {{
                    color: {Color.WHITE.value};
                    background-color: {Color.SELECTED_GRAY.value};
                    border: 1px solid {Color.BLACK.value};
                    padding: 5px;
                }}
            """)

        # Set Properties
        self.widget = parent_widget
        self.text = text
        self.delay = delay
        self.duration = duration

        # Timers for delayed show/hide behavior
        self._show_timer = QtCore.QTimer(singleShot=True)
        self._show_timer.timeout.connect(self._show_tooltip)

        self._hide_timer = QtCore.QTimer(singleShot=True)
        self._hide_timer.timeout.connect(self._hide_tooltip)



    def __del__(self):
        """
        Stop timers when the helper is deleted to avoid lingering signals.
        """

        self._show_timer.stop()
        self._hide_timer.stop()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def widget(self) -> QtWidgets.QWidget:

        return self._widget

    @widget.setter
    def widget(self, value: QtWidgets.QWidget):

        # Validate Argument
        if not isinstance(value, QtWidgets.QWidget):
            pyflame.raise_type_error('PyFlameToolTip', 'widget', 'QWidget', value)

        # Set Widget
        self._widget = value

    @property
    def text(self) -> str:

        return self._text

    @text.setter
    def text(self, value: str):

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameToolTip', 'text', 'str', value)

        # Set Text
        self._text = value

        if isValid(self._label):
            self._label.setText(value or '')
            if value != '':
                self._label.adjustSize()
            else:
                self._label.hide()

    @property
    def delay(self) -> int:

        # Return delay in milliseconds
        return self._delay

    @delay.setter
    def delay(self, value: int):

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameToolTip', 'delay', 'int', value)

        # Set delay in milliseconds
        self._delay = value * 1000

    @property
    def duration(self) -> int:

        # Return duration in milliseconds
        return self._duration

    @duration.setter
    def duration(self, value: int):

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameToolTip', 'duration', 'int', value)

        # Set duration in milliseconds
        self._duration = value * 1000

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def enter_event(self):
        """
        Enter Event
        ===========

        Show tooltip when mouse enters widget.

        Called in widget.enterEvent()
        """

        if self.text:
            self._show_timer.start(self.delay)

    def leave_event(self):
        """
        Leave Event
        ===========

        Hide tooltip when mouse leaves widget.

        Called in widget.leaveEvent()
        """

        self._show_timer.stop()
        self._hide_tooltip()

    #-------------------------------------
    # [Internal Methods]
    #-------------------------------------

    def _show_tooltip(self):
        """
        Show Tooltip
        ============

        Show tooltip when mouse enters widget.
        """
        print('Duration:', self.duration)
        if self.text and isValid(self._label):
            self._label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)
            self._label.adjustSize()
            pos = self.widget.mapToGlobal(self.widget.rect().bottomLeft())
            self._label.move(pos)
            self._label.show()
            self._hide_timer.start(self.duration)

    def _hide_tooltip(self):
        if isValid(self._label):
            self._label.hide()
        self._hide_timer.stop()

class PyFlameConfig:
    """
    PyFlameConfig
    =============

    Flexible configuration manager for pyflame scripts.

    This class loads and saves JSON config values while keeping attribute
    access dynamic so different scripts can use different keys.

    Values are stored in `config_values` and mirrored as instance attributes.
    Unknown keys are allowed and preserved.

    Args
    ----
        `config_values` (Dict[str, Any]):
            Dictionary of default config key-value pairs.
            Must contain at least one key.
            (Default: Required)

        `config_path` (str):
            Path to the config json file.
            (Default: `os.path.join(SCRIPT_PATH, 'config/config.json')`)

        `script_name` (str):
            Script name to persist in config.
            (Default: `SCRIPT_NAME`)

    Methods
    -------
        `load_config()`:
            Load config from disk and hydrate attributes.

        `save_config(config_values: Dict[str, Any] | None=None, config_path: str | None=None)`:
            Save updated config values to disk.

        `get(key: str, default: Any=None) -> Any`:
            Return raw value from config dictionary.

        `get_str(key: str, default: str='') -> str`:
            Return value as string.

        `get_int(key: str, default: int=0) -> int`:
            Return value as integer.

        `get_float(key: str, default: float=0.0) -> float`:
            Return value as float.

        `get_bool(key: str, default: bool=False) -> bool`:
            Return value as boolean.

        `get_config_values(config_path: str) -> Dict[str, Any]`:
            Static helper to load and return config values from a path.
    """

    def __init__(self, config_values: Dict[str, Any], config_path: str = os.path.join(SCRIPT_PATH, 'config/config.json'), script_name: str = SCRIPT_NAME) -> None:

        # Validate Argument types
        if not isinstance(config_values, dict):
            pyflame.raise_type_error('PyFlameConfig', 'config_values', 'dict[str, Any]', config_values)
        if not config_values:
            pyflame.raise_value_error('PyFlameConfig', 'config_values', 'non-empty dictionary', config_values)
        if not isinstance(config_path, str):
            pyflame.raise_type_error('PyFlameConfig', 'config_path', 'str', config_path)
        if not isinstance(script_name, str):
            pyflame.raise_type_error('PyFlameConfig', 'script_name', 'str', script_name)

        # Core attributes are assigned with object.__setattr__ to avoid
        # __setattr__ mirroring before config_values exists.
        object.__setattr__(self, 'config_values', dict(config_values))
        object.__setattr__(self, 'config_path', config_path)
        object.__setattr__(self, 'script_name', script_name)

        # Load persisted configuration and hydrate dynamic attributes.
        self.load_config()

    # -------------------------------------------------------------------------
    # Dynamic attribute behavior
    # -------------------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        """
        Dynamic attribute fallback.

        If an attribute does not exist on the instance/class, look it up
        in config_values so `settings.some_key` works for arbitrary keys.
        """

        try:
            return self.config_values[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name: str, value: Any) -> None:
        """
        Dynamic attribute assignment.

        Non-core attributes are mirrored into config_values automatically.
        This keeps attribute-style updates and dictionary values in sync.
        """

        object.__setattr__(self, name, value)

        # Mirror non-core keys once config_values has been initialized.
        if (
            name not in {'config_values', 'config_path', 'script_name'}
            and 'config_values' in self.__dict__
            and isinstance(self.__dict__['config_values'], dict)
        ):
            self.__dict__['config_values'][name] = value

    # -------------------------------------------------------------------------
    # Load / Save
    # -------------------------------------------------------------------------

    def print_config(self, action: str) -> None:

        pad = max(len(k) for k in self.config_values) + 1

        label = f'--[ {SCRIPT_NAME}: {action} Config ]'
        top_rule = label + '-' * max(2, 80 - len(label))
        bottom_rule = '-' * 80

        print(f'{top_rule}')
        for key, val in self.config_values.items():
            print(f'{key:<{pad}}: {val}')
        print(bottom_rule)

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Load configuration from disk and update dynamic attributes.

        If the config file exists:
            - Read json object
            - Merge into current config_values (file values override defaults)

        If the config file does not exist:
            - Create parent folder
            - Save current defaults as new config file
        """

        # Load the configuration from the JSON file
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                loaded_config = json.load(f)

            # Validate loaded config type
            if not isinstance(loaded_config, dict):
                pyflame.raise_value_error('PyFlameConfig.load_config', 'loaded_config', 'dictionary JSON root object', loaded_config)

            # Update default values with loaded values
            self.config_values.update(loaded_config)
        else:
            # Ensure config directory exists then write defaults
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            self.save_config(self.config_values)

        # Ensure script_name exists in current config
        self.config_values['script_name'] = self.script_name

        # Hydrate instance attributes from config values
        for key, value in self.config_values.items():
            object.__setattr__(self, key, value)

        # Print config values to terminal
        self.print_config('Loading')
        print(f'[\033[92mLOADED\033[0m] Configuration ready\n')

    def save_config(self, config_values: Dict[str, Any] | None = None, config_path: str | None = None) -> None:
        """
        Save Config
        ===========

        Save configuration values to disk.

        Args
        ----
            `config_values` (Dict[str, Any] | None):
                Optional values to merge before saving.
                (Default: `None`)

            `config_path` (str | None):
                Optional target path. Uses instance config_path when None.
                (Default: `None`)
        """

        # Validate Argument types
        if config_values is not None and not isinstance(config_values, dict):
            pyflame.raise_type_error('PyFlameConfig.save_config', 'config_values', 'dict[str, Any] | None', config_values)
        if config_path is not None and not isinstance(config_path, str):
            pyflame.raise_type_error('PyFlameConfig.save_config', 'config_path', 'str | None', config_path)

        target_path = config_path if config_path is not None else self.config_path

        # Merge provided values into current config
        if config_values:
            self.config_values.update(config_values)

        # Keep script name in config
        self.config_values['script_name'] = self.script_name

        # Keep script_name first for readability
        ordered_config: Dict[str, Any] = {'script_name': self.script_name}
        for key, value in self.config_values.items():
            if key != 'script_name':
                ordered_config[key] = value
        self.config_values = ordered_config

        # Load existing file so unmodified keys are preserved
        action = 'Saving'
        if os.path.exists(target_path):
            with open(target_path, 'r') as f:
                existing_config = json.load(f)

            if not isinstance(existing_config, dict):
                pyflame.raise_value_error('PyFlameConfig.save_config', 'existing_config', 'dictionary JSON root object', existing_config)
        else:
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            existing_config = {}
            action = 'Creating'

        # Update only values currently present in instance config
        existing_config.update(self.config_values)

        with open(target_path, 'w') as f:
            json.dump(existing_config, f, indent=4)

        # Re-hydrate attributes after save
        for key, value in self.config_values.items():
            object.__setattr__(self, key, value)

        # Print config values to terminal
        self.print_config(action)
        print(f'[\033[92mSAVED\033[0m] Configuration saved\n')

    # -------------------------------------------------------------------------
    # Access helpers (script-agnostic)
    # -------------------------------------------------------------------------

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get raw config value by key.
        """
        return self.config_values.get(key, default)

    def get_str(self, key: str, default: str = '') -> str:
        """
        Get config value as string.
        """
        value = self.config_values.get(key, default)
        return value if isinstance(value, str) else str(value)

    def get_int(self, key: str, default: int = 0) -> int:
        """
        Get config value as int.
        """
        value = self.config_values.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """
        Get config value as float.
        """
        value = self.config_values.get(key, default)
        try:
            return float(value)
        except (TypeError, ValueError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """
        Get config value as bool.
        """
        value = self.config_values.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {'1', 'true', 'yes', 'on'}
        return bool(value)

    # -------------------------------------------------------------------------
    # Static Helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def get_config_values(config_path: str) -> Dict[str, Any]:
        """
        Get Config Values
        =================

        Load and return config values from a json file path.

        Args
        ----
            `config_path` (str):
                Path to config json file.

        Returns
        -------
            Dict[str, Any]:
                Loaded json dictionary.
        """

        if not isinstance(config_path, str):
            pyflame.raise_type_error(
                'PyFlameConfig.get_config_values',
                'config_path',
                'str',
                config_path,
            )

        with open(config_path, 'r') as f:
            data = json.load(f)

        if not isinstance(data, dict):
            pyflame.raise_value_error(
                'PyFlameConfig.get_config_values',
                'data',
                'dictionary JSON root object',
                data,
            )

        return data

# ==============================================================================
# [PyFlame QT Widgets]
# ==============================================================================

class PyFlameButton(QtWidgets.QPushButton):
    """
    PyFlameButton
    =============

    Custom QT Flame Button Widget Subclass

    Args
    ----
        `text` (str):
            Text displayed on the button.
            (Default: `""`)

        `connect` (callable, optional):
            Function to call when the button is clicked.
            (Default: `None`)

        `color` (Color, optional):
            Button color.
            (Default: `Color.GRAY`)

            Color Options
                `Color.GRAY`: Standard gray button
                `Color.BLUE`: Blue button
                `Color.RED`: Red button

        `enabled` (bool, optional):
            Whether the button is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the button in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the button in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set the button text.
            (Default: `""`)

        `color` (Color):
            Get or set the button color.
            (Default: `Color.GRAY`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `connect(callback: Callable)`:
            Connects a function to the button's click event.

    Examples
    --------
        Create a blue PyFlameButton with a tooltip:
        ```
        button = PyFlameButton(
            text='Export',
            connect=export_function,
            color=Color.BLUE,
            tooltip='Click to export the file'
        )
        ```

        To set or get any button property:
        ```
        # Set property
        button.text = 'New Button Name'

        # Get property
        print(button.text)
        ```
    """

    def __init__(self: 'PyFlameButton',
                 text: str='',
                 connect: Callable[..., None] | None=None,
                 color: Color=Color.GRAY,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Widget Settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.text = text
        self.width = width
        self.height = height
        self.color = color
        self.enabled = enabled
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Connect button click
        self.connect_callback(connect)

    #---------------------------
    # [Properties]
    #---------------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set button text.

        Returns
        -------
            str:
                Text shown on button.

        Set
        ---
            `value` (str):
                The text to set for the button.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get button text
            print(button.text)

            # Set button text
            button.text = 'Save'
            ```
        """

        return super().text()

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set button text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameButton', 'text', 'str', value)

        self.setText(value)

    @property
    def color(self) -> Color:
        """
        Color
        =====

        Get or set button color.

        Returns
        -------
            Color: The color of the button.

        Set
        ---
            `value` (Color):
                The color to set for the button.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color Enum.

        Examples
        --------
            ```
            # Get button color
            print(button.color)

            # Set button color
            button.color = Color.BLUE
            ```
        """

        return self._color

    @color.setter
    def color(self, value: Color) -> None:
        """
        Color
        =====

        Set button color.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameButton', 'color', f'Color Enum: Color.GRAY, Color.BLUE, Color.RED', value)
        if value not in {Color.GRAY, Color.BLUE, Color.RED}:
            pyflame.raise_value_error('PyFlameButton', 'color', f'Color Enum: Color.GRAY, Color.BLUE, Color.RED', value)

        # Set property
        self._color = value

        # Set button color
        self._set_stylesheet(value)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set button enabled state.

        Returns
        -------
            bool:
                `True` if the button is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get button enabled state
            print(button.enabled)

            # Set button enabled state
            button.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the button.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameButton', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the button width.

        Returns
        -------
            `int`:
                The current width of the button in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the button expands to fit the maximum width set by the layout. Minimum width is 25.
                If an integer, the button is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(button.width)

            # Set a fixed width
            button.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set button width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameButton', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the button height.

        Returns
        -------
            `int`:
                The current height of the button in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the button uses the default height of 28.
                If an integer, the button is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get button height
            print(button.height)

            # Set button height
            button.height = 40
            ```
        """
        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set button height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameButton', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set button tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the button.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the button.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get button tooltip
            print(button.tooltip)

            # Set button tooltip
            button.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the button.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameButton', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(button.tooltip_delay)

            # Set tooltip delay
            button.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameButton', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(button.tooltip_duration)

            # Set tooltip duration
            button.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameButton', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def connect_callback(self, callback: Callable | None) -> None:
        """
        Connect Callback
        ================

        Connect a callback function to the button click event.

        Args
        ---
            callback (Callable):
                The function to call when the button is clicked.

        Raises
        -----
            TypeError:
                If `callback` is not callable.
        """

        if callback is not None and not callable(callback):
            pyflame.raise_type_error('PyFlameButton', 'connect_callback', 'callable | None', callback)

        if callback:
            self.clicked.connect(callback)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self, color: Color) -> None:
        """
        Set Style Sheet
        ===============

        Args
        ---
            `color` (Color):
                The color to set for the button: `Color.GRAY`, `Color.Blue`, `Color.RED`

        Raises
        -----
            ValueError:
                If the provided `color` is not a supported color option.
        """

        # Validate Argument
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
                """)

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameEntry(QtWidgets.QLineEdit):
    """
    PyFlameEntry
    ============

    Custom QT Flame LineEdit Widget Subclass

    Replaces PyFlameLineEdit.

    Args
    ----
        `text` (str):
            Text shown in entry.
            (Default: `""`)

        `align` (Align, optional):
            Align text to left, right, or center.
            (Default: `Align.LEFT`)

            Align Options
                `Align.LEFT`: Aligns text to the left side of the entry.
                `Align.RIGHT`: Aligns text to the right side of the entry.
                `Align.CENTER`: Centers text within the entry.

        `text_changed` (callable, optional):
            Function to be called whenever the text in the entry changes. This is typically used to perform live updates based on user input.
            (Default: `None`)

        `placeholder_text` (str, optional):
            Temporary text to display when entry is empty.
            (Default: `""`)

        `read_only` (bool, optional):
            Sets the entry to be read-only if True, disabling user input and applying a distinct visual style to indicate this state. Text is not selectable.
            (Default: `False`)

        `password_echo` (bool, optional):
            If `True`, the entry will display asterisks instead of the actual characters.
            (Default: `False`)

        `enabled` (bool, optional):
            Whether the entry is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the entry in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the entry in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set entry text.
            (Default: `""`)

        `align` (Align, optional):
            Get or set text alignment.
            (Default: `Align.LEFT`)

        `placeholder_text` (str):
            Get or set placeholder text.
            (Default: `""`)

        `read_only` (bool):
            Get or set read-only state.
            (Default: `False`)

        `password_echo` (bool):
            Get or set password echo mode.
            (Default: `False`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `text_changed(connected_function: Callable)`:
            Connects a function to be called when the entry text changes.

        `set_focus()`:
            Sets focus to the entry.

    Examples
    --------
        To create a PyFlameEntry:
        ```
        entry = PyFlameEntry(
            text='Something here'
            )
        ```

        To set or get any entry property:
        ```
        # Set property
        entry.text = 'New Entry Text'

        # Get property
        print(entry.text)
        ```
    """

    def __init__(self: 'PyFlameEntry',
                 text: str='',
                 align: Align=Align.LEFT,
                 text_changed: Callable[..., None] | None=None,
                 placeholder_text: str='',
                 read_only: bool=False,
                 password_echo: bool=False,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Set Entry Settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Entry Properties
        self.text = text
        self.align = align
        self.placeholder_text = placeholder_text
        self.read_only = read_only
        self.password_echo = password_echo
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay * 1000
        self.tooltip_duration = tooltip_duration * 1000

        self.text_changed(text_changed)

        # Settings for Alt+Click to show full entry text
        self.setMouseTracking(True)  # Enable mouse tracking
        self.alt_pressed = False
        self.mouse_inside = False
        self.full_entry_text_label = None  # Custom tooltip label
        self.installEventFilter(self)

        # Set Entry Stylesheet
        self._set_stylesheet(self._read_only)

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set entry text.

        Returns
        -------
            str:
                The text of the entry.

        Set
        ---
            `value` (str):
                The text to set for the entry.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get entry text
            print(entry.text)

            # Set entry text
            entry.text = 'Save'
            ```
        """

        return super().text()

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set entry text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntry', 'text', 'str', value)

        # Set text
        self.setText(value)

    @property
    def align(self) -> Align:
        """
        Align
        =====

        Get or set the alignment of the entry.
        """

        return self._align

    @align.setter
    def align(self, value: Align) -> None:
        """
        Align
        =====

        Set the alignment of the entry.
        """

        # Validate Argument
        if not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameEntry', 'align', 'Align Enum', value)

        # Set alignment
        self._align = value

        if value == Align.LEFT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        elif value == Align.RIGHT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        elif value == Align.CENTER:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

    @property
    def placeholder_text(self) -> str | None:
        """
        Placeholder Text
        ================

        Get or set the placeholder text for the entry.

        Returns
        -------
            str:
                The placeholder text for the entry.

        Set
        ---
            `value` (str):
                The placeholder text for the entry.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get placeholder text
            print(entry.placeholder_text)

            # Set placeholder text
            entry.placeholder_text = 'Enter text here'
            ```
        """

        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value: str | None) -> None:
        """
        Placeholder Text
        ================

        Set the placeholder text for the entry.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntry', 'placeholder_text', 'str | None', value)

        # Set placeholder text
        self._placeholder_text = value
        if value:
            self.setPlaceholderText(value)

    @property
    def read_only(self) -> bool:
        """
        Read Only
        =========

        Get or set the read-only state of the entry.

        Returns
        -------
            bool:
                `True` if the entry is read-only, `False` otherwise.

        Set
        ---
            `value` (bool):
                `True` to set the entry to read-only, `False` to set it to read/write.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get read-only state
            print(entry.read_only)

            # Set read-only
            entry.read_only = True
            ```
        """

        return self._read_only

    @read_only.setter
    def read_only(self, value: bool) -> None:
        """
        Read Only
        =========

        Set the read-only state of the entry.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameEntry', 'read_only', 'bool', value)

        # Set read-only
        self._read_only = value
        self.setReadOnly(value)

    @property
    def password_echo(self) -> bool:
        """
        Password Echo
        =============

        Get or set the password echo mode.

        True to enable password echo, False to disable.

        Returns
        -------
            bool:
                True if password echo is enabled, False otherwise.

        Set
        ---
            `value` (bool):
                True to enable password echo, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get password echo
            print(entry.password_echo)

            # Set password echo
            entry.password_echo = True
            ```
        """

        return self._password_echo

    @password_echo.setter
    def password_echo(self, value: bool) -> None:
        """
        Password Echo
        =============

        Set the password echo mode.
        """

        self._password_echo = value

        if self._password_echo:
            self.setEchoMode(QtWidgets.QLineEdit.Password)
        else:
            self.setEchoMode(QtWidgets.QLineEdit.Normal)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set entry enabled state.

        Returns
        -------
            bool: `True` if the entry is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get entry enabled state
            print(entry.enabled)

            # Set entry enabled state
            entry.enabled = False
            ```
        """
        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the entry.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameEntry', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the entry width.

        Returns
        -------
            `int`:
                The current width of the entry in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the entry expands to fit the maximum width set by the layout. Minimum width is 25.
                If an integer, the entry is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(entry.width)

            # Set a fixed width
            entry.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set entry width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntry', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the entry height.

        Returns
        -------
            `int`:
                The current height of the entry in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the entry uses the default height of 28.
                If an integer, the entry is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get entry height
            print(entry.height)

            # Set entry height
            entry.height = 40
            ```
        """
        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set entry height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntry', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set entry tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the entry.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the entry.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get entry tooltip
            print(entry.tooltip)

            # Set entry tooltip
            entry.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the entry.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntry', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(button.tooltip_delay)

            # Set tooltip delay
            button.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntry', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(button.tooltip_duration)

            # Set tooltip duration
            button.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntry', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def set_focus(self) -> None:
        """
        Set Focus
        =========

        Set widget focus to the entry widget.
        """

        self.setFocus()

    def text_changed(self, connected_function: Callable | None) -> None:
        """
        Text Changed
        ============

        Calls a function when the text in the entry field changes.

        Args
        ----
            `connected_function` (callable):
                Function to call when the text in the entry field changes.
        """

        # Validate Argument type
        if connected_function is not None and not callable(connected_function):
            pyflame.raise_type_error('PyFlameEntry', 'text_changed', 'callable', connected_function)

        # Connect textChanged signal to connected_function
        if connected_function:
            self.textChanged.connect(connected_function)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self, read_only) -> None:
        """
        Set Stylesheet
        ==============

        The stylesheet has two states: read-only and editable.

        If read-only, the background color is darker and the text color is gray.
        Otherwise, the default Flame line edit stylesheet is applied.

        Args
        ----
            `read_only` (bool):
                Indicates whether the PyFlameLineEdit is read-only.

        Raises
        ------
            TypeError:
                If `read_only` is not a boolean.

        Example
        -------
            Set PyFlameEntry stylesheet to `read_only`:
            ```
            self._set_stylesheet(read_only)
            ```
        """

        # Validate Argument
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

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

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

        full_text = self.text

        if full_text:
            if self.full_entry_text_label is None:
                self.full_entry_text_label = PyFlameLabel(
                    text=full_text,
                    parent=self.parent(),
                    )
                self.full_entry_text_label.setWindowFlags(QtCore.Qt.ToolTip)
                self.full_entry_text_label.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents)

            self.full_entry_text_label.text = full_text
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

class PyFlameEntryBrowser(QtWidgets.QLineEdit):
    """
    PyFlameEntryBrowser
    ===================

    Custom QT Flame Entry File Browser Widget Subclass

    Displays a Flame file browser when clicked.

    Args
    ----
        `path` (str):
            Path to be displayed in entry.

        `placeholder_text` (str, optional):
            Text displayed when the entry is empty.
            (Default: `None`)

        `browser_type` (BrowserType):
            Type of browser to open. Must be either `BrowserType.FILE` or `BrowserType.DIRECTORY`.
            (Default: `BrowserType.FILE`)

        `browser_ext` (list[str], optional):
            List of file extensions to filter by when using `BrowserType.FILE`. Ignored if `browser_type` is `BrowserType.DIRECTORY`.
            (Default: `[]`)

        `browser_title` (str, optional):
            Title of the browser window.
            (Default: `"Select File"`)

        `window_to_hide` (list[QtWidgets.QWidget] | QtWidgets.QWidget, optional):
            Window to hide while the browser is open.
            (Default: `None`)

        `connect` (callable, optional):
            Function to call after the file browser closes.
            (Default: `None`)

        `enabled` (bool, optional):
            Whether the entry is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the entry in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the entry in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `path` (str):
            Get or set the current path in the entry field.
            (Default: `""`)

        `placeholder_text` (str):
            Get or set the placeholder text.
            (Default: `None`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `connect_callback(callback: Callable) -> None`:
            Connect a function to be called after the file browser closes.

        `open_file_browser(browser_type, browser_ext, browser_title, window_to_hide) -> None`:
            Opens the Flame file browser to select files or directories.

    Examples
    --------
        Create a PyFlameEntryBrowser:
        ```
        path_entry = PyFlameEntryBrowser(
            path=some_path,
            browser_type=BrowserType.FILE,
            browser_ext=['exr'],
            browser_title='Select Image',
            window_to_hide=self.window,
        )
        ```

        Set or get Properties
        ```
        # Set property
        entry.path = '/opt/Autodesk'

        # Get property
        print(entry.path)
        ```
    """

    clicked = QtCore.Signal()

    def __init__(self: 'PyFlameEntryBrowser',
                 path: str,
                 placeholder_text: str | None=None,
                 browser_type: BrowserType=BrowserType.FILE,
                 browser_ext: List[str]=[],
                 browser_title: str='Select File',
                 window_to_hide: list[QtWidgets.QWidget] | QtWidgets.QWidget | None=None,
                 connect: Callable[..., None] | None=None,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ):
        super().__init__()

        # Set Browser Settings
        self.setFont(FONT)
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.path = path
        self.placeholder_text = placeholder_text
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Open File Browser
        self.connect_callback(
            partial(
                self.open_file_browser,
                browser_type,
                browser_ext,
                browser_title,
                window_to_hide,
                )
            )

        # Connect to run after browser is closed
        self.connect_callback(connect)

        # Set stylesheet
        self._set_stylesheet()

    @property
    def path(self) -> str:
        """
        Path
        ====

        Get or set entry path.

        Returns
        -------
            str:
                The path of the entry.

        Set
        ---
            `value` (str):
                The path to set for the entry.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get entry path as string
            print(entry.path)

            # Set entry path
            entry.path = '/opt/Autodesk'
            ```
        """

        return super().text()

    @path.setter
    def path(self, value: str) -> None:
        """
        Path
        ====

        Set entry path.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'path', 'str', value)

        # Set text
        self._path = value
        self.setText(value)

    @property
    def placeholder_text(self) -> str | None:
        """
        Placeholder Text
        =================

        Get or set the placeholder text for the entry.

        Returns
        -------
            str:
                The placeholder text for the entry.

        Set
        ---
            `value` (str):
                The placeholder text for the entry.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get placeholder text
            print(entry.placeholder_text)

            # Set placeholder text
            entry.placeholder_text = 'Enter text here'
            ```
        """

        return self._placeholder_text

    @placeholder_text.setter
    def placeholder_text(self, value: str | None) -> None:
        """
        Placeholder Text
        =================

        Set the placeholder text for the entry.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'placeholder_text', 'str | None', value)

        # Set placeholder text
        self._placeholder_text = value
        if value:
            self.setPlaceholderText(value)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set entry enabled state.

        Returns
        -------
            bool: `True` if the entry is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get entry enabled state
            print(entry.enabled)

            # Set entry enabled state
            entry.enabled = False
            ```
        """
        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the entry.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the entry width.

        Returns
        -------
            `int`:
                The current width of the entry in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the entry expands to fit the maximum width set by the layout. Minimum width is 25.
                If an integer, the entry is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(entry.width)

            # Set a fixed width
            entry.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set entry width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the entry height.

        Returns
        -------
            `int`:
                The current height of the entry in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the entry uses the default height of 28.
                If an integer, the entry is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get entry height
            print(entry.height)

            # Set entry height
            entry.height = 40
            ```
        """
        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set entry height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set entry tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the entry.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the entry.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get entry tooltip
            print(entry.tooltip)

            # Set entry tooltip
            entry.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the entry.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(button.tooltip_delay)

            # Set tooltip delay
            button.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(button.tooltip_duration)

            # Set tooltip duration
            button.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameEntryBrowser', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def connect_callback(self, callback: Callable | None) -> None:
        """
        Connect Callback
        ================

        Connect a callback function to the button click event.

        Args
        ----
            callback (Callable):
                The function to call when the button is clicked.

        Raises
        ------
            TypeError:
                If `callback` is not callable.
        """

        if callback is not None and not callable(callback):
            pyflame.raise_type_error('PyFlameEntryBrowser.connect_callback', 'callback', 'callable', callback)

        if callback:
            self.clicked.connect(callback)

    def open_file_browser(
        self,
        browser_type: BrowserType,
        browser_ext: list,
        browser_title: str,
        window_to_hide: list[QtWidgets.QWidget] | QtWidgets.QWidget | None=None,
        ) -> None:
        """
        Open File Browser
        =================

        Open flame file browser to select file or directory.
        """

        # Validate Arguments
        if not isinstance(browser_type, BrowserType):
            pyflame.raise_type_error('PyFlameEntryBrowser.open_file_browser', 'browser_type', 'BrowserType Enum(BrowserType.FILE or BrowserType.DIRECTORY)', browser_type)
        if not isinstance(browser_ext, list):
            pyflame.raise_type_error('PyFlameEntryBrowser.open_file_browser', 'browser_ext', 'list', browser_ext)
        if not isinstance(browser_title, str):
            pyflame.raise_type_error('PyFlameEntryBrowser.open_file_browser', 'browser_title', 'str', browser_title)
        if window_to_hide is not None:
            if isinstance(window_to_hide, list):
                if not all(isinstance(w, QtWidgets.QWidget) for w in window_to_hide):
                    pyflame.raise_type_error('PyFlameEntryBrowser.open_file_browser', 'window_to_hide', 'list of QWidget or QWidget | None', window_to_hide)
            elif not isinstance(window_to_hide, QtWidgets.QWidget):
                pyflame.raise_type_error('PyFlameEntryBrowser.open_file_browser', 'window_to_hide', 'list of QWidget or QWidget | None', window_to_hide)

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

        new_path = pyflame.file_browser(
            path=self._path,
            title=browser_title,
            extension=browser_ext,
            select_directory=browser_select_directory,
            window_to_hide=window_to_hide,
            )

        if isinstance(new_path, str):
            self.path = new_path

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameImageWidget(QtWidgets.QWidget):
    """
    PyFlameImageWidget
    ==================

    Custom QT Flame Image Widget

    Displays a scaled image within a bordered frame, with an optional
    single-line info bar below the image area.

    When ``show_info=True`` a ``PyFlameEntry`` in read-only mode is shown below
    the image area and is automatically populated with the image filename and
    pixel dimensions whenever an image is loaded. The text can also be set
    directly via the ``info_text`` property.



    Args
    ----
        image (str | QPixmap | None):
            Path to an image file, a QPixmap, or None to show an empty frame.
            Supports any format that QPixmap can decode (PNG, JPG, EXR via
            plugins, DPX, TIFF, etc.).
            (Default: `None`)

        show_info (bool):
            Enable to show image filename and resolution at the botttom of the widget.
            (Default: `False`)

        show_border (bool):
            Draws a 1-pixel border around the image area.
            (Default: `False`)

        popup_viewer (bool):
            When True, double-clicking the image opens a standalone popup
            viewer window. When False, double-clicks are ignored.
            (Default: `False`)

        width (int | None):
            Optional fixed width in pixels. When None the widget expands to
            fill available horizontal space.
            (Default: `None`)

        height (int | None):
            Optional fixed height in pixels. When None the widget expands to
            fill available vertical space.
            (Default: `None`)

        parent (QWidget | None):
            Optional parent widget.
            (Default: `None`)

    Properties
    ----------
        image (str | QPixmap | None):
            Get or set the displayed image. Accepts a file path, a QPixmap, or
            None to clear the display.

        image_path (str | None):
            Read-only. The file-system path of the currently loaded image, or
            None if no image is loaded or the image was set via QPixmap.

        has_image (bool):
            Read-only. True if a valid image is currently loaded.

        image_size (tuple[int, int] | None):
            Read-only. Pixel dimensions of the loaded image as (width, height),
            or None if no image is loaded.

        show_info (bool):
            Read-only. True if the info bar entry is present.

        info_text (str):
            Get or set the text shown in the info bar. Only meaningful when
            ``show_info=True``. Setting this property overrides the
            automatically generated filename/resolution string until the next
            time ``image`` is assigned.

        background_color (Color):
            Color used to fill the areas not covered by the scaled image.
            Defaults to ``Color.DARK_GRAY``.

        border_color (Color):
            Color of the 1-pixel border surrounding the image area.
            Defaults to ``Color.BORDER``.

    Examples
    --------
        Load image from file with info bar::

            widget = PyFlameImageWidget(image='/path/to/image.png', show_info=True)

        Set image from QPixmap::

            pixmap = QtGui.QPixmap('/path/to/image.png')
            widget = PyFlameImageWidget(image=pixmap, show_info=True)

        Override info bar text::

            widget.info_text = 'Plate A  |  16-bit EXR'

        Change colors after creation::

            widget.background_color = Color.BLACK
            widget.border_color = Color.BORDER_BRIGHTER
    """

    # Height of the info bar entry and the gap between it and the image area
    _INFO_HEIGHT  = 28
    _INFO_SPACING = 4

    # Shared viewer geometry — persists across opens for all instances
    _viewer_geometry: Optional[QtCore.QRect] = None

    def __init__(
        self,
        image: Optional[Union[str, QtGui.QPixmap]] = None,
        show_info: bool = False,
        show_border: bool = False,
        popup_viewer: bool = False,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)

        # Internal state
        self._pixmap: Optional[QtGui.QPixmap] = None
        self._source_path: Optional[str] = None
        self._show_border: bool = show_border
        self._popup_viewer: bool = popup_viewer
        self._bg_color_enum: Color = Color.DARK_GRAY
        self._background_color: QtGui.QColor = self._color_to_qcolor(Color.DARK_GRAY)
        self._border_color_enum: Color = Color.BORDER
        self._border_color: QtGui.QColor = self._color_to_qcolor(Color.BORDER)

        # Viewer window reference — kept alive while the popup is open
        self._viewer_window: Optional['PyFlameImageWidget._ImageViewerWindow'] = None

        # Widget Settings
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        self.setMinimumSize(10, 10)

        if width is not None:
            self.setFixedWidth(width)
        if height is not None:
            self.setFixedHeight(height)

        # Optional info bar — parented to self, positioned manually in resizeEvent
        self._info_entry: Optional[PyFlameEntry] = None
        if show_info:
            self._info_entry = PyFlameEntry(read_only=True)
            self._info_entry.setParent(self)
            self._info_entry.show()

        # Set initial image
        if image is not None:
            self.image = image

    # -------------------------------------------------------------------------
    # Size hints
    # -------------------------------------------------------------------------

    def sizeHint(self) -> QtCore.QSize:
        """Default size hint when no explicit size is set."""

        h = 360
        if self._info_entry is not None:
            h += self._INFO_SPACING + self._INFO_HEIGHT
        return QtCore.QSize(640, h)

    def minimumSizeHint(self) -> QtCore.QSize:
        """Minimum sensible size for the widget."""

        return QtCore.QSize(10, 10)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def image(self) -> Optional[QtGui.QPixmap]:
        """
        Image
        =====

        Get or set the image displayed in the widget.

        Returns
        -------
            Optional[QtGui.QPixmap]:
                The current pixmap, or None if no image is loaded.

        Set
        ---
            `value` (str | QtGui.QPixmap | None):
                A file-system path to load, a QPixmap to display directly,
                or None to clear the display. Triggers an immediate repaint.
                When an info bar is present its text is updated automatically.

        Raises
        ------
            FileNotFoundError:
                If a str path points to a missing file.
            ValueError:
                If the file exists but cannot be loaded as an image.
            TypeError:
                If the value is not str, QPixmap, or None.

        Examples
        --------
            ```
            # Get current image
            pixmap = widget.image

            # Set image from file path
            widget.image = '/path/to/image.png'

            # Set image from QPixmap
            widget.image = QtGui.QPixmap('/path/to/image.png')

            # Clear image
            widget.image = None
            ```
        """

        return self._pixmap

    @image.setter
    def image(self, value: Optional[Union[str, QtGui.QPixmap]]) -> None:
        """
        Image
        =====

        Set the image displayed in the widget.
        """

        # Validate Argument
        if value is not None and not isinstance(value, (str, QtGui.QPixmap)):
            pyflame.raise_type_error(
                'PyFlameImageWidget',
                'image',
                'str | QPixmap | None',
                value,
            )

        self._source_path = None

        if value is None:
            self._pixmap = None
        elif isinstance(value, str):
            if not os.path.isfile(value):
                pyflame.raise_value_error(
                    'PyFlameImageWidget',
                    'image',
                    'existing file path',
                    value,
                )
            pixmap = QtGui.QPixmap(value)
            if pixmap.isNull():
                pyflame.raise_value_error(
                    'PyFlameImageWidget',
                    'image',
                    'valid image file',
                    value,
                )
            self._pixmap = pixmap
            self._source_path = value
        else:
            self._pixmap = value

        self.update()
        self._update_info_bar()

    @property
    def image_path(self) -> Optional[str]:
        """
        Image Path
        ==========

        Get the file-system path of the currently loaded image.

        Read-only — the path is set automatically when ``image`` is assigned
        a string. Returns ``None`` when no image is loaded or when the image
        was supplied as a QPixmap (no path available).

        Returns
        -------
            Optional[str]:
                Absolute path to the loaded image file, or ``None``.

        Examples
        --------
            ```
            widget.image = '/path/to/image.png'
            print(widget.image_path)  # '/path/to/image.png'

            widget.image = QtGui.QPixmap('/path/to/image.png')
            print(widget.image_path)  # None
            ```
        """

        return self._source_path

    @property
    def has_image(self) -> bool:
        """
        Has Image
        =========

        Return whether an image is currently loaded in the widget.

        Read-only — reflects whether the ``image`` property holds a valid
        pixmap.

        Returns
        -------
            bool:
                ``True`` if an image is loaded, ``False`` otherwise.

        Examples
        --------
            ```
            if widget.has_image:
                print('Image is loaded.')
            ```
        """

        return self._pixmap is not None and not self._pixmap.isNull()

    @property
    def image_size(self) -> Optional[tuple[int, int]]:
        """
        Image Size
        ==========

        Get the pixel dimensions of the currently loaded image.

        Read-only — reflects the size of the source pixmap, not the size at
        which it is displayed. Returns ``None`` when no image is loaded.

        Returns
        -------
            Optional[tuple[int, int]]:
                ``(width, height)`` of the loaded image in pixels, or
                ``None`` if no image is loaded.

        Examples
        --------
            ```
            size = widget.image_size
            if size is not None:
                width, height = size
                print(width, height)
            ```
        """

        if self._pixmap is None or self._pixmap.isNull():
            return None

        return (self._pixmap.width(), self._pixmap.height())

    @property
    def show_info(self) -> bool:
        """
        Show Info
        =========

        Return whether the info bar is present on the widget.

        Read-only — reflects the ``show_info`` argument passed at
        construction time.

        Returns
        -------
            bool:
                ``True`` if the info bar entry is present, ``False``
                otherwise.

        Examples
        --------
            ```
            if widget.show_info:
                widget.info_text = 'Custom label'
            ```
        """

        return self._info_entry is not None

    @property
    def info_text(self) -> str:
        """
        Info Text
        =========

        Get or set the text shown in the info bar.

        Returns
        -------
            str:
                The current info bar text, or an empty string when no info
                bar is present.

        Set
        ---
            `value` (str):
                The text to display in the info bar. Overrides the
                auto-generated filename/resolution string until the next time
                ``image`` is assigned. Has no effect when ``show_info=False``.

        Raises
        ------
            TypeError:
                If the provided value is not a string.

        Examples
        --------
            ```
            # Get info bar text
            print(widget.info_text)

            # Set info bar text
            widget.info_text = 'Plate A  |  16-bit EXR'
            ```
        """

        if self._info_entry is None:
            return ''

        return self._info_entry.text

    @info_text.setter
    def info_text(self, value: str) -> None:
        """
        Info Text
        =========

        Set the text shown in the info bar.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error(
                'PyFlameImageWidget',
                'info_text',
                'str',
                value,
                )

        if self._info_entry is not None:
            self._info_entry.setText(value)

    @property
    def background_color(self) -> Color:
        """
        Background Color
        ================

        Get or set the background fill color.

        Returns
        -------
            Color:
                The Color enum value used to fill letterbox/pillarbox areas
                not covered by the scaled image.

        Set
        ---
            `value` (Color):
                The Color enum value to use for the background fill.
                Triggers an immediate repaint.

        Raises
        ------
            TypeError:
                If the provided value is not a Color enum member.

        Examples
        --------
            ```
            # Get background color
            print(widget.background_color)

            # Set background color
            widget.background_color = Color.BLACK
            ```
        """

        return self._bg_color_enum

    @background_color.setter
    def background_color(self, value: Color) -> None:
        """
        Background Color
        ================

        Set the background fill color.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error(
                'PyFlameImageWidget',
                'background_color',
                'Color',
                value,
            )

        self._bg_color_enum = value
        self._background_color = self._color_to_qcolor(value)
        self.update()

    @property
    def border_color(self) -> Color:
        """
        Border Color
        ============

        Get or set the 1-pixel border color.

        Returns
        -------
            Color:
                The Color enum value used for the 1-pixel border surrounding
                the image area.

        Set
        ---
            `value` (Color):
                The Color enum value to use for the border.
                Triggers an immediate repaint.

        Raises
        ------
            TypeError:
                If the provided value is not a Color enum member.

        Examples
        --------
            ```
            # Get border color
            print(widget.border_color)

            # Set border color
            widget.border_color = Color.BORDER_BRIGHTER
            ```
        """

        return self._border_color_enum

    @border_color.setter
    def border_color(self, value: Color) -> None:
        """
        Border Color
        ============

        Set the 1-pixel border color.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error(
                'PyFlameImageWidget',
                'border_color',
                'Color',
                value,
            )

        self._border_color_enum = value
        self._border_color = self._color_to_qcolor(value)
        self.update()

    # -------------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------------

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """
        Resize Event
        ============

        Repositions the info bar entry at the bottom of the widget whenever
        the widget is resized.
        """

        super().resizeEvent(event)
        if self._info_entry is not None:
            y = self.height() - self._INFO_HEIGHT
            self._info_entry.setGeometry(0, y, self.width(), self._INFO_HEIGHT)

    def enterEvent(self, event: QtCore.QEvent) -> None:
        self._show_border = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self._show_border = False
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        """
        Paint Event
        ===========

        Draws:
          1. A 1-pixel border around the image area (Color.BORDER).
          2. A dark grey background fill inside the border (Color.DARK_GRAY).
          3. The image, scaled to fit inside the border while preserving the
             original aspect ratio, centered within the inner area.

        The info bar (when present) is a child widget that sits below the
        painted image area and is not affected by this paint event.
        """

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)

        canvas = self._canvas_rect()
        cw = canvas.width()
        ch = canvas.height()

        # Step 1 – border (optional) and background
        if self._show_border:
            painter.fillRect(canvas, self._border_color)
            inner_rect = QtCore.QRect(1, 1, cw - 2, ch - 2)
        else:
            inner_rect = canvas

        # Step 2 – background fill
        painter.fillRect(inner_rect, self._background_color)

        # Step 3 – scaled image centered inside the inner area
        if self._pixmap is not None and not self._pixmap.isNull():
            scaled = self._pixmap.scaled(
                inner_rect.width(),
                inner_rect.height(),
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            x = inner_rect.x() + (inner_rect.width() - scaled.width()) // 2
            y = inner_rect.y() + (inner_rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)

        painter.end()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    @staticmethod
    def _color_to_qcolor(color: Color) -> QtGui.QColor:
        """
        Convert a Color enum value (CSS rgb / rgba string) to a QColor.

        Supports both ``rgb(r, g, b)`` and ``rgba(r, g, b, a)`` formats where
        the alpha channel is expressed as a float in the range [0, 1].

        Args:
            color: A Color enum member whose ``.value`` is an rgb/rgba string.

        Returns:
            The equivalent QColor.

        Raises:
            ValueError: If the string cannot be parsed.
        """

        raw = color.value.strip()
        m = re.fullmatch(
            r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)',
            raw,
        )
        if not m:
            pyflame.raise_value_error(
                'PyFlameImageWidget',
                'color',
                'valid Color enum string',
                raw,
            )
        assert m is not None
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = int(float(m.group(4)) * 255) if m.group(4) is not None else 255
        return QtGui.QColor(r, g, b, a)

    def _canvas_rect(self) -> QtCore.QRect:
        """
        The rectangle available for image painting.

        When the info bar is present this is the full widget rect minus the
        height reserved for the info entry and its spacing gap.
        """

        h = self.height()
        if self._info_entry is not None:
            h -= self._INFO_SPACING + self._INFO_HEIGHT
        return QtCore.QRect(0, 0, self.width(), max(h, 0))

    def _update_info_bar(self) -> None:
        """Refresh the info bar text from the current image state."""

        if self._info_entry is None:
            return

        if self._pixmap is None or self._pixmap.isNull():
            self._info_entry.setText('')
            return

        w = self._pixmap.width()
        h = self._pixmap.height()

        if self._source_path:
            name = os.path.basename(self._source_path)
            self._info_entry.setText(f'{name}  |  {w} x {h}')
        else:
            self._info_entry.setText(f'{w} x {h}')

    # -------------------------------------------------------------------------
    # Double-click viewer
    # -------------------------------------------------------------------------

    def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent) -> None:
        """Open the popup image viewer on a left double-click when popup_viewer is enabled."""

        if self._popup_viewer and event.button() == QtCore.Qt.MouseButton.LeftButton and self.has_image:
            self._open_viewer()
        super().mouseDoubleClickEvent(event)

    def _open_viewer(self) -> None:
        """Open the popup viewer, or raise it if it is already visible."""

        if self._viewer_window is not None and self._viewer_window.isVisible():
            self._viewer_window.raise_()
            self._viewer_window.activateWindow()
            return

        self._viewer_window = PyFlameImageWidget._ImageViewerWindow(
            pixmap=self._pixmap,
            source_path=self._source_path,
            geometry=PyFlameImageWidget._viewer_geometry,
            parent=self.window(),
        )
        self._viewer_window.geometry_saved.connect(self._on_viewer_geometry_saved)
        self._viewer_window.show()

    def _on_viewer_geometry_saved(self, rect: QtCore.QRect) -> None:
        """Store the viewer window geometry so it is restored on the next open."""

        PyFlameImageWidget._viewer_geometry = rect

    # ==========================================================================
    # Popup Image Viewer
    # ==========================================================================

    class _ImageViewerWindow(QtWidgets.QWidget):
        """
        _ImageViewerWindow
        ==================

        Standalone popup window opened by double-clicking a PyFlameImageWidget.

        Displays the image with zoom controls, a copy-to-clipboard button, a
        save-as-PNG button, and an info bar that mirrors the parent widget's
        style (filename  |  width x height).

        Zoom controls
        -------------
        - **Fit** button   — scale image to fill the window (default on open).
        - **100%** button  — display at native 1:1 pixel resolution.
        - **Mouse wheel**  — zoom in / out continuously.

        Keyboard shortcuts
        ------------------
        - ``Escape``    — close the window.
        - ``Ctrl/Cmd+S``— open the Save PNG dialog.
        """

        geometry_saved = QtCore.Signal(QtCore.QRect)

        _ZOOM_MIN  = 0.05
        _ZOOM_MAX  = 8.0
        _ZOOM_STEP = 1.15

        def __init__(
            self,
            pixmap: QtGui.QPixmap,
            source_path: Optional[str],
            geometry: Optional[QtCore.QRect] = None,
            parent: Optional[QtWidgets.QWidget] = None,
        ) -> None:
            super().__init__(parent)

            self._original_pixmap = pixmap
            self._source_path = source_path
            self._zoom_factor: float = 1.0
            self._fit_mode: bool = True

            # Pan state
            self._pan_active: bool = False
            self._pan_origin: QtCore.QPoint = QtCore.QPoint()

            # --- Window setup ---
            title = os.path.basename(source_path) if source_path else 'Image Viewer'
            self.setWindowTitle(title)
            self.setMinimumSize(200, 200)
            self.setWindowFlags(
                QtCore.Qt.WindowType.Window
                | QtCore.Qt.WindowType.WindowCloseButtonHint
                | QtCore.Qt.WindowType.WindowMinMaxButtonsHint,
                )
            self.setStyleSheet(f'background-color: {Color.GRAY.value};')

            # --- Scroll area + image label ---
            self._image_label = QtWidgets.QLabel()
            self._image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._image_label.setStyleSheet('background-color: transparent;')

            self._scroll_area = QtWidgets.QScrollArea()
            self._scroll_area.setWidget(self._image_label)
            self._scroll_area.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._scroll_area.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {Color.DARK_GRAY.value};
                    border: 1px solid {Color.BORDER.value};
                }}
                QScrollBar:vertical {{
                    background: {Color.GRAY.value};
                    width: 10px;
                }}
                QScrollBar::handle:vertical {{
                    background: {Color.BRIGHT_GRAY.value};
                    border-radius: 5px;
                    min-height: 20px;
                }}
                QScrollBar:horizontal {{
                    background: {Color.GRAY.value};
                    height: 10px;
                }}
                QScrollBar::handle:horizontal {{
                    background: {Color.BRIGHT_GRAY.value};
                    border-radius: 5px;
                    min-width: 20px;
                }}
            """)
            self._scroll_area.viewport().installEventFilter(self)
            self._scroll_area.viewport().setCursor(QtCore.Qt.CursorShape.OpenHandCursor)

            # --- Info bar ---
            self._info_entry = PyFlameEntry(read_only=True)
            self._info_entry.setFixedHeight(28)
            self._refresh_info()

            # --- Buttons ---
            _btn_style = f"""
                QPushButton {{
                    color: {Color.BUTTON_TEXT.value};
                    background-color: {Color.GRAY.value};
                    border: 1px solid {Color.BORDER.value};
                    padding: 0px 12px;
                    height: 28px;
                }}
                QPushButton:hover {{
                    background-color: {Color.BRIGHT_GRAY.value};
                    border: 1px solid {Color.BORDER_BRIGHTER.value};
                }}
                QPushButton:pressed {{
                    background-color: {Color.SELECTED_GRAY.value};
                }}
            """

            self._btn_fit  = QtWidgets.QPushButton('Fit')
            self._btn_100  = QtWidgets.QPushButton('100%')
            self._btn_copy = QtWidgets.QPushButton('Copy')
            self._btn_save = QtWidgets.QPushButton('Save PNG')

            for btn in (self._btn_fit, self._btn_100, self._btn_copy, self._btn_save):
                btn.setStyleSheet(_btn_style)
                btn.setFixedHeight(28)
                btn.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)

            self._btn_fit.clicked.connect(self._zoom_fit)
            self._btn_100.clicked.connect(self._zoom_100)
            self._btn_copy.clicked.connect(self._copy_to_clipboard)
            self._btn_save.clicked.connect(self._save_png)

            # --- Keyboard shortcuts ---
            QtGui.QShortcut(QtGui.QKeySequence('Escape'), self, self.close)
            QtGui.QShortcut(QtGui.QKeySequence.StandardKey.Save, self, self._save_png)

            # --- Button bar ---
            btn_bar = QtWidgets.QHBoxLayout()
            btn_bar.setContentsMargins(0, 0, 0, 0)
            btn_bar.setSpacing(4)
            btn_bar.addWidget(self._btn_fit)
            btn_bar.addWidget(self._btn_100)
            btn_bar.addStretch()
            btn_bar.addWidget(self._btn_copy)
            btn_bar.addWidget(self._btn_save)

            # --- Main layout ---
            layout = QtWidgets.QVBoxLayout(self)
            layout.setContentsMargins(8, 8, 8, 8)
            layout.setSpacing(4)
            layout.addWidget(self._scroll_area)
            layout.addWidget(self._info_entry)
            layout.addLayout(btn_bar)

            # --- Geometry ---
            if geometry is not None:
                self.setGeometry(geometry)
            else:
                self.resize(960, 600)
                screen = QtGui.QGuiApplication.primaryScreen()
                if screen:
                    center = screen.availableGeometry().center()
                    self.move(center.x() - self.width() // 2, center.y() - self.height() // 2)

            # Defer initial fit so the viewport is fully laid out first
            QtCore.QTimer.singleShot(0, self._zoom_fit)

        # -------------------------------------------------------------------------
        # Events
        # -------------------------------------------------------------------------

        def closeEvent(self, event: QtGui.QCloseEvent) -> None:
            self.geometry_saved.emit(self.geometry())
            super().closeEvent(event)

        def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
            super().resizeEvent(event)
            if self._fit_mode:
                self._apply_zoom(self._calc_fit_factor())

        def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
            """Intercept viewport mouse and wheel events for zoom and pan."""

            if obj is self._scroll_area.viewport():
                t = event.type()

                if t == QtCore.QEvent.Type.Wheel:
                    delta = event.angleDelta().y()
                    step = self._ZOOM_STEP if delta > 0 else 1.0 / self._ZOOM_STEP
                    self._set_zoom(self._zoom_factor * step)
                    return True

                if t == QtCore.QEvent.Type.MouseButtonPress and event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self._pan_active = True
                    self._pan_origin = event.position().toPoint()
                    self._scroll_area.viewport().setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
                    return True

                if t == QtCore.QEvent.Type.MouseMove and self._pan_active:
                    delta = event.position().toPoint() - self._pan_origin
                    self._pan_origin = event.position().toPoint()
                    h_bar = self._scroll_area.horizontalScrollBar()
                    v_bar = self._scroll_area.verticalScrollBar()
                    h_bar.setValue(h_bar.value() - delta.x())
                    v_bar.setValue(v_bar.value() - delta.y())
                    return True

                if t == QtCore.QEvent.Type.MouseButtonRelease and event.button() == QtCore.Qt.MouseButton.LeftButton:
                    self._pan_active = False
                    self._scroll_area.viewport().setCursor(QtCore.Qt.CursorShape.OpenHandCursor)
                    return True

            return super().eventFilter(obj, event)

        # -------------------------------------------------------------------------
        # Zoom helpers
        # -------------------------------------------------------------------------

        def _calc_fit_factor(self) -> float:
            """Return the zoom factor required to fit the image in the viewport."""

            vp = self._scroll_area.viewport().size()
            pw = self._original_pixmap.width()
            ph = self._original_pixmap.height()
            if pw == 0 or ph == 0:
                return 1.0
            return min(vp.width() / pw, vp.height() / ph)

        def _apply_zoom(self, factor: float) -> None:
            """Scale the image label to the given factor."""

            self._zoom_factor = max(self._ZOOM_MIN, min(self._ZOOM_MAX, factor))
            w = int(self._original_pixmap.width()  * self._zoom_factor)
            h = int(self._original_pixmap.height() * self._zoom_factor)
            scaled = self._original_pixmap.scaled(
                w, h,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self._image_label.setPixmap(scaled)
            self._image_label.resize(scaled.size())

        def _set_zoom(self, factor: float) -> None:
            """Apply an explicit zoom factor and exit fit mode."""

            self._fit_mode = False
            self._apply_zoom(factor)

        def _zoom_fit(self) -> None:
            """Scale image to fill the current viewport (fit mode)."""

            self._fit_mode = True
            self._apply_zoom(self._calc_fit_factor())

        def _zoom_100(self) -> None:
            """Display image at its native 1:1 pixel resolution."""

            self._fit_mode = False
            self._apply_zoom(1.0)

        # -------------------------------------------------------------------------
        # Actions
        # -------------------------------------------------------------------------

        def _copy_to_clipboard(self) -> None:
            """Copy the original unscaled image to the system clipboard."""

            QtGui.QGuiApplication.clipboard().setPixmap(self._original_pixmap)

        def _save_png(self) -> None:
            """Open a native save dialog and write the image as a PNG file."""

            if self._source_path:
                base = os.path.splitext(self._source_path)[0]
                default_path = base + '.png'
            else:
                default_path = os.path.join(os.path.expanduser('~'), 'image.png')

            path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                'Save Image As PNG',
                default_path,
                'PNG Images (*.png)',
            )
            if not path:
                return
            if not path.lower().endswith('.png'):
                path += '.png'
            self._original_pixmap.save(path, 'PNG')

        def _refresh_info(self) -> None:
            """Populate the info bar with filename and pixel dimensions."""

            w = self._original_pixmap.width()
            h = self._original_pixmap.height()
            if self._source_path:
                name = os.path.basename(self._source_path)
                self._info_entry.setText(f'{name}  |  {w} x {h}')
            else:
                self._info_entry.setText(f'{w} x {h}')

class PyFlameImageGallery(QtWidgets.QWidget):
    """
    PyFlameImageGallery
    ===================

    Custom QT Flame Image Gallery Widget

    Scrollable image gallery widget that displays images from a folder in a
    grid, built on top of PyFlameImageWidget.

    Exactly one of ``columns`` or ``rows`` must be provided. Providing both
    raises a ``ValueError``.

    When ``columns`` is set the grid has a fixed number of columns and images
    wrap onto new rows as needed. A vertical scrollbar appears on the right
    when there are more rows than fit within the widget height.

    When ``rows`` is set the grid has a fixed number of rows and images wrap
    onto new columns as needed. A horizontal scrollbar appears at the bottom
    when there are more columns than fit within the widget width.

    Each image occupies a square cell whose side length is computed from the
    available viewport dimension divided by the fixed axis count.
    Cells are recomputed on every resize. Clicking a cell selects it
    (blue border); arrow keys move the selection. An optional read-only info
    bar below the grid shows the selected image filename and pixel dimensions.

    Args
    ----
        folder (str | None):
            Path to the folder to load images from. Can be changed later via
            the ``folder`` property.
            (Default: `None`)

        columns (int | None):
            Number of grid columns. Must be >= 1. Cannot be combined with
            ``rows``. When set, images flow left-to-right and wrap into new
            rows with a vertical scrollbar. Defaults to 4 when neither
            ``columns`` nor ``rows`` is provided.
            (Default: `None`)

        rows (int | None):
            Number of grid rows. Must be >= 1. Cannot be combined with
            ``columns``. When set, images flow top-to-bottom and wrap into
            new columns with a horizontal scrollbar.
            (Default: `None`)

        show_info (bool):
            When True, a read-only ``PyFlameEntry`` is displayed below the
            grid showing the selected image filename and resolution.
            (Default: `False`)

        popup_viewer (bool):
            When True, double-clicking a gallery image opens a standalone
            popup viewer window. When False, double-clicks are ignored.
            (Default: `False`)

        sort_ascending (bool):
            Filename sort order. True = A-Z, False = Z-A.
            (Default: `True`)

        extensions (list[str] | None):
            File extensions to include, e.g. ``['.png', '.exr']``. When
            None the default set of common image formats is used.
            (Default: `None`)

        image_selected (Callable[[str], None] | None):
            Callback invoked with the full path of the selected image
            whenever the selection changes.
            (Default: `None`)

        width (int | None):
            Optional fixed widget width in pixels.
            (Default: `None`)

        height (int | None):
            Optional fixed widget height in pixels.
            (Default: `None`)

        parent (QWidget | None):
            Optional parent widget.
            (Default: `None`)

    Properties
    ----------
        folder (str | None):
            Get or set the folder path. Setting reloads the gallery.

        columns (int | None):
            Get or set the number of grid columns. Only valid when the
            gallery was created in columns mode. Setting rebuilds the grid.

        rows (int | None):
            Get or set the number of grid rows. Only valid when the
            gallery was created in rows mode. Setting rebuilds the grid.

        sort_ascending (bool):
            Get or set the sort direction. Setting resorts and rebuilds.

        extensions (list[str]):
            Get or set the allowed extensions. Setting reloads.

        show_info (bool):
            Read-only. True if the info bar is present.

        image_count (int):
            Read-only. Total images currently loaded.

        selected_path (str | None):
            Read-only. Full path of the selected image.

        selected_name (str | None):
            Read-only. Filename of the selected image.

        selected_size (tuple[int, int] | None):
            Read-only. ``(width, height)`` of the selected image pixmap.

        selected_index (int | None):
            Read-only. Zero-based grid index of the selected image.

    Examples
    --------
        Column-based gallery with vertical scrolling::

            gallery = PyFlameImageGallery(
                folder='/path/to/images',
                columns=5,
                show_info=True,
            )

        Row-based gallery with horizontal scrolling::

            gallery = PyFlameImageGallery(
                folder='/path/to/images',
                rows=3,
                show_info=True,
            )

        Refresh after folder contents change::

            gallery.refresh()
    """

    _DEFAULT_EXTENSIONS: frozenset = frozenset({
        '.png', '.jpg', '.jpeg', '.tif', '.tiff',
        '.exr', '.dpx', '.bmp', '.gif', '.webp', '.hdr',
    })

    _INFO_HEIGHT  = 28
    _INFO_SPACING = 4

    def __init__(
        self,
        folder: Optional[str] = None,
        columns: Optional[int] = None,
        rows: Optional[int] = None,
        show_info: bool = False,
        popup_viewer: bool = False,
        sort_ascending: bool = True,
        extensions: Optional[list] = None,
        image_selected: Optional[Callable] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        parent: Optional[QtWidgets.QWidget] = None,
    ) -> None:
        super().__init__(parent)

        # Validate Arguments
        if columns is not None and rows is not None:
            pyflame.raise_value_error(
                'PyFlameImageGallery',
                'columns/rows',
                'one of columns or rows, not both',
                f'columns={columns!r}, rows={rows!r}',
            )
        if columns is None and rows is None:
            columns = 4
        if folder is not None and not isinstance(folder, str):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'folder',
                'str | None',
                folder,
            )
        if columns is not None and (not isinstance(columns, int) or columns < 1):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'columns',
                'int >= 1',
                columns,
            )
        if rows is not None and (not isinstance(rows, int) or rows < 1):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'rows',
                'int >= 1',
                rows,
            )
        if not isinstance(show_info, bool):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'show_info',
                'bool',
                show_info,
            )
        if not isinstance(popup_viewer, bool):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'popup_viewer',
                'bool',
                popup_viewer,
            )
        if not isinstance(sort_ascending, bool):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'sort_ascending',
                'bool',
                sort_ascending,
            )
        if extensions is not None and not isinstance(extensions, list):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'extensions',
                'list | None',
                extensions,
            )
        if image_selected is not None and not callable(image_selected):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'image_selected',
                'callable | None',
                image_selected,
            )
        if width is not None and (not isinstance(width, int) or width < 1):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'width',
                'int >= 1 | None',
                width,
            )
        if height is not None and (not isinstance(height, int) or height < 1):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'height',
                'int >= 1 | None',
                height,
            )

        # Internal state
        self._mode: str = 'columns' if columns is not None else 'rows'
        self._folder: Optional[str] = folder
        self._columns: Optional[int] = columns
        self._rows: Optional[int] = rows
        self._show_info: bool = show_info
        self._popup_viewer: bool = popup_viewer
        self._sort_ascending: bool = sort_ascending
        self._extensions: set = (
            set(extensions) if extensions is not None
            else set(self._DEFAULT_EXTENSIONS)
        )
        self._image_selected: Optional[Callable] = image_selected
        self._image_paths: list = []
        self._cells: list = []
        self._selected_index: Optional[int] = None

        # Widget settings
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Expanding,
        )
        if width is not None:
            self.setFixedWidth(width)
        if height is not None:
            self.setFixedHeight(height)

        # Border style strings for hover toggle
        self._border_off = f'border: 1px solid transparent;'
        self._border_on = f'border: 1px solid {Color.BORDER.value};'

        # Build UI
        self._build_ui()

        # Load initial folder
        if self._folder is not None:
            self._load_images()
            self._build_grid()

    # -------------------------------------------------------------------------
    # UI construction
    # -------------------------------------------------------------------------

    def _build_ui(self) -> None:
        """Build the scroll area, grid container, and optional info bar."""

        self.setStyleSheet(self._border_off)

        # Scroll area — parented directly, positioned in resizeEvent
        self._scroll_area = QtWidgets.QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self._scroll_area.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        if self._mode == 'columns':
            self._scroll_area.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )
            self._scroll_area.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
        else:
            self._scroll_area.setHorizontalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded
            )
            self._scroll_area.setVerticalScrollBarPolicy(
                QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
            )

        # Grid container
        bg = Color.DARK_GRAY.value
        self._scroll_area.setStyleSheet(f'QScrollArea {{ background-color: {bg}; }}')

        self._grid_widget = QtWidgets.QWidget()
        self._grid_widget.setStyleSheet(f'background-color: {bg};')
        self._grid_widget.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        self._grid_layout = QtWidgets.QGridLayout(self._grid_widget)
        self._grid_layout.setContentsMargins(0, 0, 0, 0)
        self._grid_layout.setSpacing(2)
        self._grid_layout.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )

        self._scroll_area.setWidget(self._grid_widget)

        # Optional info bar — parented directly, positioned in resizeEvent
        self._info_entry: Optional[PyFlameEntry] = None
        if self._show_info:
            self._info_entry = PyFlameEntry(read_only=True)
            self._info_entry.setParent(self)
            self._info_entry.show()

    # -------------------------------------------------------------------------
    # Size hints
    # -------------------------------------------------------------------------

    def sizeHint(self) -> QtCore.QSize:
        """Default size hint based on mode."""

        if self._mode == 'columns':
            columns = self._columns or 1
            vp_width = self._scroll_area.viewport().width()
            if vp_width <= 0:
                vp_width = 400
            cell_size = max(vp_width // columns, 10)
            h = cell_size * 3
            if self._show_info:
                h += self._INFO_SPACING + self._INFO_HEIGHT
            return QtCore.QSize(vp_width, h)
        else:
            rows = self._rows or 1
            vp_height = self._scroll_area.viewport().height()
            if vp_height <= 0:
                vp_height = 300
            cell_size = max(vp_height // rows, 10)
            w = cell_size * 4
            if self._show_info:
                vp_height += self._INFO_SPACING + self._INFO_HEIGHT
            return QtCore.QSize(w, vp_height)

    # -------------------------------------------------------------------------
    # Properties
    # -------------------------------------------------------------------------

    @property
    def folder(self) -> Optional[str]:
        """
        Folder
        ======

        Get or set the folder path. Setting this property re-scans the folder
        and rebuilds the grid.

        Returns
        -------
            Optional[str]:
                The current folder path, or None if not set.

        Set
        ---
            `value` (str | None):
                Path to an image folder, or None to clear the gallery.

        Raises
        ------
            TypeError:
                If the value is not str or None.

        Examples
        --------
            ```
            gallery.folder = '/path/to/images'
            gallery.folder = None  # clears the gallery
            ```
        """

        return self._folder

    @folder.setter
    def folder(self, value: Optional[str]) -> None:

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'folder',
                'str | None',
                value,
            )

        self._folder = value
        self._load_images()
        self._build_grid()

    @property
    def columns(self) -> Optional[int]:
        """
        Columns
        =======

        Get or set the number of grid columns. Only meaningful when the
        gallery was created in columns mode. Setting this property rebuilds
        the grid with the new column count.

        Returns
        -------
            Optional[int]:
                Current number of grid columns, or None if in rows mode.

        Set
        ---
            `value` (int):
                New column count. Must be >= 1.

        Raises
        ------
            TypeError:
                If the value is not an int >= 1.
            RuntimeError:
                If the gallery is in rows mode.

        Examples
        --------
            ```
            gallery.columns = 6
            ```
        """

        return self._columns

    @columns.setter
    def columns(self, value: int) -> None:

        if self._mode != 'columns':
            raise RuntimeError(
                "PyFlameImageGallery: Cannot set 'columns' when the "
                "gallery is in rows mode."
            )
        if not isinstance(value, int) or value < 1:
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'columns',
                'int >= 1',
                value,
            )

        self._columns = value
        self._build_grid()

    @property
    def rows(self) -> Optional[int]:
        """
        Rows
        ====

        Get or set the number of grid rows. Only meaningful when the gallery
        was created in rows mode. Setting this property rebuilds the grid
        with the new row count.

        Returns
        -------
            Optional[int]:
                Current number of grid rows, or None if in columns mode.

        Set
        ---
            `value` (int):
                New row count. Must be >= 1.

        Raises
        ------
            TypeError:
                If the value is not an int >= 1.
            RuntimeError:
                If the gallery is in columns mode.

        Examples
        --------
            ```
            gallery.rows = 5
            ```
        """

        return self._rows

    @rows.setter
    def rows(self, value: int) -> None:

        if self._mode != 'rows':
            raise RuntimeError(
                "PyFlameImageGallery: Cannot set 'rows' when the "
                "gallery is in columns mode."
            )
        if not isinstance(value, int) or value < 1:
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'rows',
                'int >= 1',
                value,
            )

        self._rows = value
        self._build_grid()

    @property
    def sort_ascending(self) -> bool:
        """
        Sort Ascending
        ==============

        Get or set the filename sort direction. Setting this property resorts
        the image list and rebuilds the grid.

        Returns
        -------
            bool:
                True for A→Z ordering, False for Z→A.

        Raises
        ------
            TypeError:
                If the value is not a bool.

        Examples
        --------
            ```
            gallery.sort_ascending = False  # reverse sort
            ```
        """

        return self._sort_ascending

    @sort_ascending.setter
    def sort_ascending(self, value: bool) -> None:

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'sort_ascending',
                'bool',
                value,
            )

        self._sort_ascending = value
        self._load_images()
        self._build_grid()

    @property
    def extensions(self) -> list:
        """
        Extensions
        ==========

        Get or set the allowed file extensions. Setting reloads images from
        the current folder with the new filter applied.

        Returns
        -------
            list[str]:
                Sorted list of current allowed extensions (e.g.
                ``['.exr', '.png']``).

        Set
        ---
            `value` (list[str]):
                New list of extensions to allow.

        Raises
        ------
            TypeError:
                If the value is not a list.

        Examples
        --------
            ```
            gallery.extensions = ['.png', '.jpg']
            ```
        """

        return sorted(self._extensions)

    @extensions.setter
    def extensions(self, value: list) -> None:

        # Validate Argument
        if not isinstance(value, list):
            pyflame.raise_type_error(
                'PyFlameImageGallery',
                'extensions',
                'list',
                value,
            )

        self._extensions = set(value)
        self._load_images()
        self._build_grid()

    @property
    def show_info(self) -> bool:
        """
        Show Info
        =========

        Read-only. True if the info bar entry is present.

        Returns
        -------
            bool:
                True if ``show_info=True`` was passed at construction time.

        Examples
        --------
            ```
            if gallery.show_info:
                print(gallery.selected_name)
            ```
        """

        return self._info_entry is not None

    @property
    def image_count(self) -> int:
        """
        Image Count
        ===========

        Read-only. Total number of images currently loaded in the gallery.

        Returns
        -------
            int:
                Number of image paths that matched the folder scan.

        Examples
        --------
            ```
            print(f'{gallery.image_count} images loaded')
            ```
        """

        return len(self._image_paths)

    @property
    def selected_path(self) -> Optional[str]:
        """
        Selected Path
        =============

        Read-only. Full filesystem path of the currently selected image, or
        None when nothing is selected.

        Returns
        -------
            Optional[str]:
                Absolute path to the selected image file, or None.

        Examples
        --------
            ```
            path = gallery.selected_path
            if path:
                print(path)
            ```
        """

        if self._selected_index is None:
            return None
        return self._image_paths[self._selected_index]

    @property
    def selected_name(self) -> Optional[str]:
        """
        Selected Name
        =============

        Read-only. Filename (basename) of the currently selected image, or
        None when nothing is selected.

        Returns
        -------
            Optional[str]:
                Filename of the selected image, or None.

        Examples
        --------
            ```
            name = gallery.selected_name
            ```
        """

        path = self.selected_path
        if path is None:
            return None
        return os.path.basename(path)

    @property
    def selected_size(self) -> Optional[tuple]:
        """
        Selected Size
        =============

        Read-only. Pixel dimensions of the currently selected image as
        ``(width, height)``, or None when nothing is selected or the image
        failed to load.

        Returns
        -------
            Optional[tuple[int, int]]:
                ``(width, height)`` of the selected image pixmap, or None.

        Examples
        --------
            ```
            size = gallery.selected_size
            if size:
                w, h = size
            ```
        """

        if self._selected_index is None:
            return None
        return self._cells[self._selected_index].image_size

    @property
    def selected_index(self) -> Optional[int]:
        """
        Selected Index
        ==============

        Read-only. Zero-based grid index of the currently selected image, or
        None when nothing is selected.

        Returns
        -------
            Optional[int]:
                Grid index of the selected image, or None.

        Examples
        --------
            ```
            idx = gallery.selected_index
            ```
        """

        return self._selected_index

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------

    def refresh(self) -> None:
        """
        Refresh
        =======

        Re-scan the current folder and rebuild the grid without recreating
        the gallery widget itself. Useful when the folder contents may have
        changed on disk.

        Examples
        --------
            ```
            gallery.refresh()
            ```
        """

        self._load_images()
        self._build_grid()

    # -------------------------------------------------------------------------
    # Events
    # -------------------------------------------------------------------------

    def showEvent(self, event: QtCore.QEvent) -> None:
        super().showEvent(event)
        self._position_children()
        self._resize_cells()

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        """Reposition children and recompute cell sizes."""

        super().resizeEvent(event)
        self._position_children()
        self._resize_cells()

    def enterEvent(self, event: QtCore.QEvent) -> None:
        self.setStyleSheet(self._border_on)
        super().enterEvent(event)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        self.setStyleSheet(self._border_off)
        super().leaveEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        """Arrow key navigation between cells."""

        if not self._cells:
            super().keyPressEvent(event)
            return

        key   = event.key()
        count = len(self._cells)
        idx   = self._selected_index
        columns = self._columns or 1
        rows = self._rows or 1

        if self._mode == 'columns':
            # Columns mode: left/right ±1, up/down ±columns
            if key == QtCore.Qt.Key.Key_Right:
                new_idx = 0 if idx is None else min(idx + 1, count - 1)
            elif key == QtCore.Qt.Key.Key_Left:
                new_idx = 0 if idx is None else max(idx - 1, 0)
            elif key == QtCore.Qt.Key.Key_Down:
                new_idx = 0 if idx is None else min(idx + columns, count - 1)
            elif key == QtCore.Qt.Key.Key_Up:
                new_idx = 0 if idx is None else max(idx - columns, 0)
            else:
                super().keyPressEvent(event)
                return
        else:
            # Rows mode: up/down ±1, left/right ±rows
            if key == QtCore.Qt.Key.Key_Down:
                new_idx = 0 if idx is None else min(idx + 1, count - 1)
            elif key == QtCore.Qt.Key.Key_Up:
                new_idx = 0 if idx is None else max(idx - 1, 0)
            elif key == QtCore.Qt.Key.Key_Right:
                new_idx = 0 if idx is None else min(idx + rows, count - 1)
            elif key == QtCore.Qt.Key.Key_Left:
                new_idx = 0 if idx is None else max(idx - rows, 0)
            else:
                super().keyPressEvent(event)
                return

        self._select_cell(new_idx)

    def eventFilter(self, obj: QtCore.QObject, event: QtCore.QEvent) -> bool:
        """Intercept mouse and hover events on cell widgets."""

        event_type = event.type()

        if event_type == QtCore.QEvent.Type.MouseButtonPress:
            for i, cell in enumerate(self._cells):
                if obj is cell:
                    self.setFocus()
                    self._select_cell(i)
                    return True

        elif event_type in (
            QtCore.QEvent.Type.MouseMove,
            QtCore.QEvent.Type.MouseButtonRelease,
        ):
            if obj in self._cells:
                return True

        elif event_type == QtCore.QEvent.Type.Enter:
            for i, cell in enumerate(self._cells):
                if obj is cell:
                    cell._show_border = True
                    cell.update()
                    return True

        elif event_type == QtCore.QEvent.Type.Leave:
            for i, cell in enumerate(self._cells):
                if obj is cell:
                    if i != self._selected_index:
                        cell._show_border = False
                        cell.update()
                    return True

        return super().eventFilter(obj, event)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------

    def _position_children(self) -> None:
        """Position the scroll area and info bar within the widget."""

        w = self.width()
        h = self.height()

        if self._info_entry is not None:
            scroll_h = h - self._INFO_SPACING - self._INFO_HEIGHT
            self._scroll_area.setGeometry(0, 0, w, max(scroll_h, 0))
            info_y = h - self._INFO_HEIGHT
            self._info_entry.setGeometry(0, info_y, w, self._INFO_HEIGHT)
        else:
            self._scroll_area.setGeometry(0, 0, w, h)

    def _load_images(self) -> None:
        """Scan the current folder and populate ``_image_paths``."""

        self._image_paths = []
        if self._folder is None or not os.path.isdir(self._folder):
            return

        paths = []
        for entry in os.scandir(self._folder):
            if not entry.is_file():
                continue
            ext = os.path.splitext(entry.name)[1].lower()
            if ext in self._extensions:
                paths.append(entry.path)

        paths.sort(
            key=lambda p: os.path.basename(p).lower(),
            reverse=not self._sort_ascending,
        )
        self._image_paths = paths

    def _build_grid(self) -> None:
        """Clear and rebuild the grid with the current image paths."""

        self._clear_grid()
        self._selected_index = None
        self._update_info_bar()

        cell_size = self._cell_size()
        columns = self._columns or 1
        rows = self._rows or 1

        for i, path in enumerate(self._image_paths):
            if self._mode == 'columns':
                row = i // columns
                col = i % columns
            else:
                row = i % rows
                col = i // rows

            cell = PyFlameImageWidget(popup_viewer=self._popup_viewer)
            cell.setFixedSize(cell_size, cell_size)
            cell.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

            try:
                cell.image = path
            except (FileNotFoundError, ValueError):
                pass

            cell.installEventFilter(self)
            self._cells.append(cell)
            self._grid_layout.addWidget(cell, row, col)

        if self._image_paths:
            if self._mode == 'columns':
                last_col = len(self._image_paths) % columns
                if last_col != 0:
                    last_row = (len(self._image_paths) - 1) // columns
                    for col in range(last_col, columns):
                        placeholder = QtWidgets.QWidget()
                        placeholder.setFixedSize(cell_size, cell_size)
                        placeholder.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._grid_layout.addWidget(placeholder, last_row, col)
            else:
                last_row = len(self._image_paths) % rows
                if last_row != 0:
                    last_col = (len(self._image_paths) - 1) // rows
                    for row in range(last_row, rows):
                        placeholder = QtWidgets.QWidget()
                        placeholder.setFixedSize(cell_size, cell_size)
                        placeholder.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
                        self._grid_layout.addWidget(placeholder, row, last_col)

    def _clear_grid(self) -> None:
        """Remove all widgets from the grid layout."""

        for cell in self._cells:
            cell.removeEventFilter(self)
        self._cells = []

        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)  # type: ignore[call-overload]

    def _cell_size(self) -> int:
        """Compute the square cell side length from the fixed axis viewport dimension."""

        spacing = self._grid_layout.spacing()

        if self._mode == 'columns':
            columns = self._columns or 1
            vp_width = self._scroll_area.viewport().width()
            if vp_width <= 0:
                vp_width = 400
            total_spacing = spacing * (columns - 1)
            size = (vp_width - total_spacing) // columns
        else:
            rows = self._rows or 1
            vp_height = self._scroll_area.viewport().height()
            if vp_height <= 0:
                vp_height = 300
            total_spacing = spacing * (rows - 1)
            size = (vp_height - total_spacing) // rows

        return max(size, 10)

    def _resize_cells(self) -> None:
        """Resize all grid widgets to the current computed cell size."""

        if not self._cells:
            return

        size = self._cell_size()
        for i in range(self._grid_layout.count()):
            item = self._grid_layout.itemAt(i)
            if item is not None:
                widget = item.widget()
                if widget is not None:
                    widget.setFixedSize(size, size)

        self._grid_layout.invalidate()
        self._grid_widget.updateGeometry()

    def _select_cell(self, index: int) -> None:
        """Update selection state, border colors, info bar, and fire callback."""

        if index < 0 or index >= len(self._cells):
            return

        # Deselect previous
        if self._selected_index is not None:
            prev = self._cells[self._selected_index]
            prev.border_color = Color.BORDER
            prev._show_border = False
            prev.update()

        self._selected_index = index
        self._cells[index].border_color = Color.BLUE
        self._cells[index]._show_border = True
        self._cells[index].update()

        self._update_info_bar()

        if self._image_selected is not None:
            self._image_selected(self._image_paths[index])

    def _update_info_bar(self) -> None:
        """Write ``filename | W x H`` to the info entry."""

        if self._info_entry is None:
            return

        if self._selected_index is None:
            self._info_entry.setText('')
            return

        name = self.selected_name or ''
        size = self.selected_size

        if size is not None:
            self._info_entry.setText(f'{name}  |  {size[0]} x {size[1]}')
        else:
            self._info_entry.setText(name)

class PyFlameLabel(QtWidgets.QLabel):
    """
    PyFlameLabel
    ============

    Custom QT Flame Label Widget Subclass

    Args
    ----
        `text` (str):
            Text to display in the label.
            (Default: `""`)

        `style` (Style, optional):
            Set the label text style.
            (Default: `Style.NORMAL`)

            Style Options
                `Style.NORMAL`: Standard label without styling (left-aligned).
                `Style.UNDERLINE`: Underlines the text (centered).
                `Style.BORDER`: White border with dark background (centered).
                `Style.BACKGROUND`: Darker background (left-aligned).
                `Style.BACKGROUND_THIN`: Dark background with thin font weight (left-aligned).

        `align` (Align, optional):
            Align text to the left, right, or center. Overrides alignment defined by `style`.
            (Default: `None`)

            Align Options
                `None`: Uses alignment from the style.
                `Align.LEFT`: Aligns text to the left.
                `Align.RIGHT`: Aligns text to the right.
                `Align.CENTER`: Centers text.

        `underline_color` (Color, optional):
            Color of underline when using `Style.UNDERLINE`.
            Can be a `Color` enum or an (R, G, B, A) tuple.
            (Default: `Color.TEXT_UNDERLINE.value`)

        `enabled` (bool, optional):
            Whether the label is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the label in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the label in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `font_size` (int, optional):
            Font size for the label text. If `None`, uses the default constant `FONT_SIZE`.
            (Default: `None`)

        `parent` (QtWidgets.QWidget, optional):
            Parent widget (e.g. for tooltips).
            (Default: `None`)

    Properties
    ----------
        `text` (str):
            Get or set the label text.
            (Default: `""`)

        `style` (Style):
            Get or set the label style.
            (Default: `Style.NORMAL`)

        `align` (Align, optional):
            Get or set text alignment. Overrides style alignment.
            (Default: `None`)

        `underline_color` (Color, optional):
            Get or set the underline color.
            Accepts a `Color` enum or RGBA tuple.
            (Default: `Color.TEXT_UNDERLINE.value`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `font_size` (int):
            Get or set font size.
            (Default: `None`)

    Examples
    --------
        To create a PyFlameLabel:
        ```
        label = PyFlameLabel(
            text='This is a label',
            style=Style.UNDERLINE,
            align=Align.LEFT,
            )
        ```

        To set or get any label property:
        ```
        # Set property
        label.text = 'New label Text'

        # Get property
        print(label.text)
        ```
    """

    def __init__(self: 'PyFlameLabel',
                 text: str='',
                 style: Style=Style.NORMAL,
                 align: Align | None=None,
                 underline_color: Color=Color.TEXT_UNDERLINE,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 font_size: int | None=None,
                 parent: QtWidgets.QWidget | None=None) -> None:
        super().__init__(parent)

        # Set Label Settings
        self.setFont(FONT)
        self.font_size = font_size
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set Label Properties
        self.text = text
        self.style = style
        self.align = align
        self.underline_color = underline_color
        self.enabled = enabled
        self.width = width
        self.height = height

        # Set Label Stylesheet
        self._set_stylesheet()

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set the text of the label.

        Returns
        -------
            `str`:
                The current text of the label.

        Set
        ---
            `value` (str):
                The new text of the label.

        Raises
        ------
            TypeError:
                If `value` is not a string.

        Examples
        --------
            ```
            # Get label text
            print(label.text)

            # Set label text
            label.text = 'New Label Text'
            ```
        """

        return super().text()

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set the text of the label.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameLabel', 'text', 'str', value)

        # Set text
        self.setText(value)

    @property
    def style(self) -> Style:
        """
        Style
        =====

        Get or set the style of the label.

        Returns
        -------
            `Style`:
                The current style of the label.

        Set
        ---
            `value` (Style):
                The new style of the label.

        Raises
        ------
            TypeError:
                If `value` is not an instance of Style Enum.

        Examples
        --------
            ```
            # Get label style
            print(label.style)

            # Set label style
            label.style = Style.UNDERLINE
            ```
        """

        return self._style

    @style.setter
    def style(self, value: Style) -> None:
        """
        Style
        =====

        Set style of label.
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlameLabel', 'style', 'Style Enum', value)

        # Set style
        self._style = value
        self._set_stylesheet()

    @property
    def align(self) -> Align | None:
        """
        Align
        =====

        Get or set the alignment of the label.

        Returns
        -------
            `Align | None`:
                The current alignment of the label.

        Set
        ---
            `value` (Align | None):
                The new alignment of the label.
                This must be an instance of the Align | None.

        Raises
        ------
            TypeError:
                If `value` is not an instance of Align | None.

        Examples
        --------
            ```
            # Get label alignment
            print(label.align)

            # Set label alignment
            label.align = Align.RIGHT
            ```
        """

        return self._align

    @align.setter
    def align(self, value: Align | None) -> None:
        """
        Align
        =====

        Set the alignment of the label.
        """

        if value is not None and not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameLabel', 'align', 'Align | None', value)

        self._align = value

        if value == Align.LEFT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
        elif value == Align.RIGHT:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignRight)
        elif value == Align.CENTER:
            self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)
        else:
            if self._style in [Style.NORMAL, Style.BACKGROUND, Style.BACKGROUND_THIN]:
                self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft)
            else:
                self.setAlignment(QtCore.Qt.AlignVCenter | QtCore.Qt.AlignCenter)

    @property
    def underline_color(self) -> Color:
        """
        Underline Color
        ===============

        Get or set label underline color.

        Returns
        -------
            `Color`:
                The current underline color of the label.

        Set
        ---
            `value` (Color):
                The new underline color of the label.
                This must be an instance of the Color Enum.

        Raises
        ------
            TypeError:
                If `value` is not an instance of Color Enum.

        Examples
        --------
            ```
            # Get label underline color
            print(label.underline_color)

            # Set label underline color
            label.underline_color = Color.TEXT_UNDERLINE
            ```
        """

        return self._underline_color

    @underline_color.setter
    def underline_color(self, value: Color) -> None:
        """
        Underline Color
        ===============

        Set label underline color.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameLabel', 'underline_color', 'Color Enum', value)

        # Set underline color
        self._underline_color = value

        # Update Stylesheet
        self._set_underline_stylesheet()

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set label enabled state.

        Returns
        -------
            bool: `True` if the label is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get label enabled state
            print(label.enabled)

            # Set label enabled state
            label.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Set whether the lable is enabled or disabled.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameLabel', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int | None:
        """
        Width
        =====

        Get or set label width.

        Returns
        -------
            `int`:
                The current width of the label in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the label expands to fit the maximum width set by the layout.
                Minimum width is 25 pixels.
                If an integer, the label is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get label width
            print(label.width)

            # Set fixed label width
            label.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set label width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameLabel', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int | None:
        """
        Height
        ======

        Get or set label height.

        Returns
        -------
            `int`:
                The current height of the label in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the label uses the default height of 28.
                If an integer, the label is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get label height
            print(label.height)

            # Set label height
            label.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set label height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameLabel', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def font_size(self) -> int | None:
        """
        Font Size
        =========

        Get or set label font size.

        Returns
        -------
            `int | None`:
                The current font size of the label.

        Set
        ---
            `value` (int | None):
                If `None`, the label uses the default font size set by the `FONT` constant.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get label font size
            print(label.font_size)

            # Set label font size
            label.font_size = 14
            ```
        """

        return self._font_size

    @font_size.setter
    def font_size(self, value: int | None) -> None:
        """
        Font Size
        ========

        Set label font size.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameLabel', 'font_size', 'None | int', value)

        self._font_size = value

        # Set font size if value given
        if value is not None:
            font = self.font()
            font.setPointSize(pyflame.font_resize(value))
            self.setFont(font)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
        """

        if self._style == Style.NORMAL:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    }}
                """)
        elif self._style == Style.BORDER:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    border: 1px solid rgb{Color.TEXT_BORDER.value};
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    }}
                """)
        elif self._style == Style.BACKGROUND:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    }}
                """)
        elif self._style == Style.BACKGROUND_THIN:
            self.setStyleSheet(f"""
                QLabel{{
                    color: {Color.TEXT.value};
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    font-weight: 100;
                    }}
                QLabel:disabled{{
                    color: {Color.TEXT_DISABLED.value};
                    }}
                """)

    def _set_underline_stylesheet(self) -> None:
        """
        Set Underline Stylesheet
        ========================
        """

        self.setStyleSheet(f"""
            QLabel{{
                color: {Color.TEXT.value};
                border-bottom: 1px inset {self._underline_color.value};
                }}
            QLabel:disabled{{
                color: {Color.TEXT_DISABLED.value};
                }}
            """)

class PyFlameListWidget(QtWidgets.QListWidget):
    """
    PyFlameListWidget
    =================

    Custom QT Flame List Widget Subclass

    Args
    ----
        `items` (List[str], optional):
            List of items to populate the list widget.
            (Default: `[]`)

        `alternating_row_colors` (bool, optional):
            Enable alternating row background colors.
            (Default: `True`)

        `enabled` (bool, optional):
            Whether the list wideggt is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the list widget in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the list widget in pixels. If `None`, it expands to fit the layour. Minimum height is 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `items` (List[str]):
            Get or set the list of items. Replaces all existing items.
            (Default: `[]`)

        `selected_items` (List[str]):
            Get the currently selected items.

        `alternating_row_colors` (bool):
            Enable or disable alternating row colors.
            (Default: `True`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `add_items(items: List[str])`:
            Append a list of strings to the existing items in the widget.

        `replace_items(items: List[str])`:
            Replace all items in list with new list.

    Examples
    --------
        Create a PyFlameListWidget:
        ```
        list_widget = PyFlameListWidget(
            items=[
                'item1',
                'item2',
                'item3'
            ]
        )
        ```

        Set or get Properties
        ```
        # Set property
        list_widget.alternating_row_colors = False

        # Get property
        print(list_widget.alternating_row_colors)
        ```

        Append items:
        ```
        list_widget.add_items(
            [
            'item4',
            'item5',
            'item6'
            ]
        )
        ```

        Replace all items:
        ```
        list_widget.replace_items(
            [
            'new_item1',
            'new_item2',
            'new_item3'
            ]
        )
        ```
    """
    def __init__(self,
                 items: List[str]=[],
                 alternating_row_colors: bool=True,
                 multi_selection: bool=True,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5) -> None:
        super().__init__()

        self.setFont(FONT)
        self.setUniformItemSizes(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.items = items
        self.alternating_row_colors = alternating_row_colors
        self.multi_selection = multi_selection
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Set stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def items(self) -> List[str]:
        """
        Items
        =====

        Get all items in the List Widget as a list of strings.

        Returns
        -------
            List[str]:
                A list of strings representing the items in the List Widget.

        Set
        ---
            `values` (List[str]):
                A list of strings to replace the current items in the List Widget.

        Raises
        ------
            TypeError:
                If the provided `values` is not a list.
                If the provided `values` is not a list of strings.

        Examples
        --------
            ```
            # Get List Widget items
            items = list_widget.items

            # Set List Widget items
            list_widget.items = ['Item 1', 'Item 2', 'Item 3']
            ```
        """

        return [self.item(i).text() for i in range(self.count())]

    @items.setter
    def items(self, values: List[str]) -> None:
        """
        Items
        =====

        Replace the List Widget contents with a new list of strings.
        """

        if not isinstance(values, list):
            pyflame.raise_type_error('PyFlameListWidget', 'items', 'list', values)
        if not all(isinstance(item, str) for item in values):
            pyflame.raise_type_error('PyFlameListWidget', 'items', 'list of strings', values)

        self.clear()
        self.addItems(values)

    @property
    def selected_items(self) -> List[QtWidgets.QListWidgetItem]:
        """
        Selected Items
        ==============

        Get the currently selected items in the list.

        Returns
        -------
            list of QListWidgetItem:
                The currently selected items.
        """
        return self.selectedItems()

    @property
    def alternating_row_colors(self) -> bool:
        """
        Alternating Row Colors
        ======================

        Get or set alternating row colors.

        Returns
        -------
            bool:
                `True` if alternating row colors are enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get alternating row colors
            print(list_widget.alternating_row_colors)

            # Set alternating row colors
            list_widget.alternating_row_colors = False
            ```
        """

        return self._alternating_row_colors

    @alternating_row_colors.setter
    def alternating_row_colors(self, value: bool) -> None:
        """
        Alternating Row Colors
        ======================

        Set alternating row colors.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameListWidget', 'alternating_row_colors', 'bool', value)

        # Set alternating row colors
        self._alternating_row_colors = value
        self.setAlternatingRowColors(value)

    @property
    def multi_selection(self) -> bool:
        """
        Multi Selection
        ===============

        Get or set item selection mode.

        Returns
        -------
            bool: `True` if multi selection is enabled, `False` if disabled.

        Set
        ---
            `value` (bool): `True` to enable multi selection, `False` to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get multi selection
            print(list_widget.multi_selection)

            # Set multi selection
            list_widget.multi_selection = False
            ```
        """

        return self._multi_selection

    @multi_selection.setter
    def multi_selection(self, value: bool) -> None:
        """
        Multi Selection
        ===============

        Set item selection mode.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameListWidget', 'multi_selection', 'bool', value)

        # Set multi selection
        self._multi_selection = value

        if value:
            self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        else:
            self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set List Widget enabled state.

        Returns
        -------
            bool: `True` if the List Widget is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get List Widget enabled state
            print(list_widget.enabled)

            # Set List Widget enabled state
            list_widget.enabled = False
            ```
        """
        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the List Widget.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameListWidget', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the List Widget width.

        Returns
        -------
            `int`:
                The current width of the List Widget in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the List Widget expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the List Widget is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(list_widget.width)

            # Set a fixed width
            list_widget.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set the List Widget width.
        """

        # Validate Argument type
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameListWidget', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the List Widget height.

        Returns
        -------
            `int`:
                The current height of the List Widget in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the List Widget expands to fit the maximum height set by the layout. Minimum height is 28 pixels.
                If an integer, the List Widget is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(list_widget.width)

            # Set a fixed width
            list_widget.width = 140
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set the List Widget height.
        """

        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameListWidget', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)
        else:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set List Widget tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the List Widget.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the List Widget.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get List Widget tooltip
            print(list_widget.tooltip)

            # Set List Widget tooltip
            list_widget.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the List Widget.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameListWidget', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(list_widget.tooltip_delay)

            # Set tooltip delay
            list_widget.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameListWidget', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(list_widget.tooltip_duration)

            # Set tooltip duration
            list_widget.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameListWidget', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_items(self, items: List[str]) -> None:
        """
        Add Items
        =========

        Append items to the list widget.

        Args
        ----
            `items` (List[str]):
                List of strings to append to the list widget.

        Raises
        ------
            TypeError:
                If the provided `items` is not a list.
                If the provided `items` is not a list of strings.

        Example
        -------
            ```
            # Append items to the list widget
            list_widget.add_items(
                    [
                    'Item 1',
                    'Item 2',
                    'Item 3',
                    ]
                )
            ```
        """

        # Validate Argument
        if not isinstance(items, list):
            pyflame.raise_type_error('PyFlameListWidget.add_items: items', 'items', 'list', items)
        if not all(isinstance(item, str) for item in items):
            pyflame.raise_type_error('PyFlameListWidget.add_items: items', 'items', 'list of strings', items)

        # Append items
        self.addItems(items)

    def replace_items(self, items: List[str]) -> None:
        """
        Replace Items
        =============

        Replace items in list with new list of items.

        Args
        ----
            `items` (List[str]):
                List of items to replace current list with.

        Raises
        ------
            TypeError:
                If the provided `items` is not a list.
                If the provided `items` is not a list of strings.

        Example
        -------
            ```
            # Replace items to the list widget
            list_widget.replace_items(
                    [
                    'Item 1',
                    'Item 2',
                    'Item 3',
                    ]
                )
            ```
        """

        # Validate Argument
        if not isinstance(items, list):
            pyflame.raise_type_error('PyFlameListWidget.replace_items', 'items', 'list', items)
        if not all(isinstance(item, str) for item in items):
            pyflame.raise_type_error('PyFlameListWidget.replace_items', 'items', 'list of strings', items)

        # Clear all existing items from list
        self.clear()

        # Add new items to list
        self.addItems(items)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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
                padding-top: {pyflame.gui_resize(5)}px;
                padding-bottom: {pyflame.gui_resize(5)}px;
            }}
            QListWidget::item:selected{{
                color: {Color.TEXT_SELECTED.value};
                background-color: {Color.SELECTED_GRAY.value};
                border: 1px solid {Color.SELECTED_GRAY.value};
            }}
            QScrollBar::handle{{
                background: {Color.GRAY.value};
            }}
            QScrollBar:vertical{{
                width: {pyflame.gui_resize(8)}px;
            }}
            QScrollBar:horizontal{{
                height: {pyflame.gui_resize(8)}px;
            }}
        """)

    #-------------------------------------
    # [Event Handlers]
    #-------------------------------------

    def mousePressEvent(self, event: QtGui.QMouseEvent) -> None:
        """
        Mouse Press Event
        =================

        Prevents items in list from being deselected when clicking off list.
        """

        item = self.itemAt(event.pos())
        if item:
            super().mousePressEvent(event)
        else:
            # Click outside items: ignore deselection
            event.ignore()

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlamePushButton(QtWidgets.QPushButton):
    """
    PyFlamePushButton
    =================

    Custom QT Flame Push Button Widget Subclass

    Args
    ----
        `text` (str):
            Text displated on button.
            (Default: `""`)

        `checked` (bool, optional):
            Whether the button is checked.
            (Default: `False`)

        `connect` (callable, optional):
            Function to be called when button is pressed.
            (Default: `None`)

        `enabled` (bool, optional):
            Whether the button is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the button in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the button in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Text displayed on button.
            (Default: `""`)

        `checked` (bool):
            Whether the button is currently checked.
            (Default: `False`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `connect_callback(callback) -> None`:
            Connect a function to the button click event.

    Examples
    --------
        To create a PyFlamePushButton:
        ```
        push_button = PyFlamePushButton(
            text='Button Name',
            button_checked=False,
            )
        ```

        To set or get any push button property:
        ```
        # Set property
        push_button.text = 'New Button Name'

        # Get property
        print(push_button.text)
        ```
    """

    def __init__(self,
                 text: str='',
                 checked: bool=False,
                 connect: Callable[..., None] | None=None,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Setup Button
        self.setFont(FONT)
        self.setCheckable(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.text = text
        self.checked = checked
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Connect Callback
        self.connect_callback(connect)

        # Set Stylesheet
        self._set_stylesheet()

    #-----------------------
    # Properties
    #-----------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set the push button text.

        Returns
        -------
            str:
                The text of the push button.

        Set
        ---
            `value` (str):
                The text to set for the push button.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get push button text
            print(push_button.text)

            # Set push button text
            push_button.text = 'Save'
            ```
        """

        return super().text()

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set button text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePushButton', 'text', 'str', value)

        # Set text
        self.setText(value)

    @property
    def checked(self) -> bool:
        """
        Checked
        =======

        Get or set whether the push button is checked.

        Returns
        -------
            bool:
                True if the push button is checked, False otherwise.

        Set
        ---
            `value` (bool):
                True to check the push button, False to uncheck it.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get push button checked state
            print(push_button.checked)

            # Set push button checked state
            push_button.checked = True
            ```
        """

        return self.isChecked()

    @checked.setter
    def checked(self, value: bool) -> None:
        """
        Checked
        =======

        Set the checked state of the push button.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlamePushButton', 'checked', 'bool', value)

        # Set checked state
        self.setChecked(value)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set push button enabled state.

        Returns
        -------
            bool: `True` if the push button is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get push button enabled state
            print(push_button.enabled)

            # Set push button enabled state
            push_button.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the push button.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlamePushButton', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the push button width.

        Returns
        -------
            `int`:
                The current width of the push button in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the push button expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the push button is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(push_button.width)

            # Set a fixed width
            push_button.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set push button width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlamePushButton', 'width', 'None | int', value)

        # Set width
        if value is not None:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)
        else:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the push button height.

        Returns
        -------
            `int`:
                The current height of the button in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the push button uses the default height of 28.
                If an integer, the push button is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get push button height
            print(push_button.height)

            # Set push button height
            push_button.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set push button height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlamePushButton', 'height', 'None | int', value)

        # Set height
        if value is not None:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)
        else:
            self._height = pyflame.gui_resize(28)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set push button tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the pushbutton.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the push button.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get push button tooltip
            print(push_button.tooltip)

            # Set push button tooltip
            push_button.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the button.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePushButton', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(push_button.tooltip_delay)

            # Set tooltip delay
            push_button.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlamePushButton', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(push_button.tooltip_duration)

            # Set tooltip duration
            push_button.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlamePushButton', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def connect_callback(self, callback: Callable | None) -> None:
        """
        Connect Callback
        ================

        Connect a callback function to the button click event.

        Args
        ----
            callback (Callable):
                The function to call when the button is clicked.

        Raises
        ------
            TypeError:
                If `callback` is not callable.
        """

        if callback is not None and not callable(callback):
            pyflame.raise_type_error('PyFlamePushButton.connect_callback', 'callback', 'callable', callback)

        if callback:
            self.clicked.connect(callback)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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
            """)

    #-------------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameMenu(QtWidgets.QPushButton):
    """
    PyFlameMenu
    ===========

    Custom QT Flame Menu Widget Subclass

    Args
    ----
        `text` (str):
            Current menu selection.

        `align` (Align, optional):
            Set text alignment.
            (Default: `Align.LEFT`)

            Align Options
                `Align.LEFT`: Aligns text to the left side of the menu.
                `Align.RIGHT`: Aligns text to the right side of the menu.
                `Align.CENTER`: Centers text within the menu.

        `menu_options` (list[str], optional):
            List of menu options.
            (Default: `[]`)

        `menu_indicator` (bool, optional):
            Whether the menu indicator arrow is shown.
            (Default: `False`)

        `connect` (callable, optional):
            Function called when menu selection is changed.
            (Default: `None`)

        `enabled` (bool, optional):
            Whether the menu is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the menu in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the menu in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set current menu selection.

        `align` (Align, optional):
            Get or set alignment of text on menu.
            (Default: `Align.LEFT`)

        `menu_options` (List[str]):
            Get or set list of menu options.
            (Default: `[]`)

        `menu_indicator` (bool, optional):
            Get or set whether the menu indicator arrow is shown.
            (Default: `False`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `update_menu(text, menu_options, connect)`:
            Use to update an existing button menu.

        `refresh_menu()`:
            Use to refresh the menu after a change has been made to the menu options.

    Examples
    --------
        To create a PyFlameMenu:
        ```
        menu = PyFlameMenu(
            text='menu_name',
            menu_options=[
                'Item 1',
                'Item 2',
                'Item 3',
                'Item 4'
                ],
            align=Align.LEFT,
            )
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

    def __init__(self: 'PyFlameMenu',
                 text: str='',
                 align: Align=Align.LEFT,
                 menu_options: List[str]=[],
                 menu_indicator: bool=False,
                 connect: Callable[..., None] | None=None,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Menu Settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.text = text
        self.align = align
        self.menu_indicator = menu_indicator
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Create Menu
        self.menu = QtWidgets.QMenu(self)
        self.menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.menu.setFont(FONT)
        self.menu.aboutToShow.connect(self._match_push_button_width) # Match menu width to button width

        self._menu_options = []
        self._connect_callback = connect
        self.menu_options = menu_options  # This calls the setter (which applies dropdown visibility)

        # Set Button Stylesheets
        self._set_button_stylesheet()
        self._set_menu_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set the selected menu text.

        Returns
        -------
            str:
                The text of the selected menu.

        Set
        ---
            `value` (str):
                The text to set for the selected menu.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get selected menu text
            print(menu.text)

            # Set selected menu text
            menu.text = 'Some Menu Item'
            ```
        """

        return super().text().lstrip() # Strips space that is added to the text to move it from the left edge of the menu

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set selected menu item text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameMenu', 'text', 'str', value)

        self.setText(' ' + value)

    @property
    def align(self) -> Align:
        """
        Align
        =====

        Get or set the menu alignment.

        Returns
        -------
            `Align`:
                The current alignment of the menu.

        Set
        ---
            `value` (Align):
                The alignment to set for the menu.

        Raises
        ------
            TypeError:
                If the provided `value` is not an instance of `Align`.

        Examples
        --------
            ```
            # Get current alignment
            print(menu.align)

            # Set alignment
            menu.align = Align.RIGHT
            ```
        """

        return self._align

    @align.setter
    def align(self, value: Align) -> None:
        """
        Align
        =====

        Set the menu alignment.
        """

        # Validate Argument
        if not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameMenu', 'align', 'Align', value)

        # Set alignment
        self._align = value

    @property
    def menu_options(self) -> List[str]:
        """
        Menu Options
        ============

        Get the current list of menu option labels.

        To update menu options with a connect signal use the update_menu() method.

        Returns
        -------
            List[str]:
                List of current menu option strings.

        Set
        ---
            `options` (List[str]):
                List of menu option strings to populate the button menu.

        Raises
        ------
            TypeError:
                If the provided `options` is not a list or contains non-string items.

        Examples
        --------
            ```
            # Get current menu options
            print(menu.menu_options)

            # Set menu options
            menu.menu_options = ['Option 1', 'Option 2', 'Option 3']
            ```
        """

        if self.menu is not None and self.menu.actions():
            return [action.text() for action in self.menu.actions()]
        return self._menu_options

    @menu_options.setter
    def menu_options(self, options: List[str]) -> None:
        """
        Set Menu Options
        ================

        Update the menu with a new list of options.
        """

        if not isinstance(options, list) or not all(isinstance(item, str) for item in options):
            pyflame.raise_type_error('PyFlameMenu', 'menu_options', 'List[str]', options)

        # Keep internal options in sync for refresh_menu()
        self._menu_options = options

        # Clear existing actions
        self.menu.clear()

        for menu_label in options:
            action = self.menu.addAction(
                menu_label,
                partial(self._create_menu, menu_label, self._connect_callback)
                )
            action.setFont(FONT)

        self._update_dropdown_visibility()

    @property
    def menu_indicator(self) -> bool:
        """
        Menu Indicator
        ==============

        Get or set the menu indicator.

        Returns
        -------
            bool:
                The current menu indicator state.

        Set
        ---
            `value` (bool):
                The menu indicator state to set.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get current menu indicator
            print(menu.menu_indicator)

            # Set menu indicator
            menu.menu_indicator = True
            ```
        """

        return self._menu_indicator

    @menu_indicator.setter
    def menu_indicator(self, value: bool) -> None:
        """
        Menu Indicator
        ==============

        Set the menu indicator.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameMenu', 'menu_indicator', 'bool', value)

        # Set menu indicator
        self._menu_indicator = value

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set menu enabled state.

        Returns
        -------
            bool: `True` if the menu is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get menu enabled state
            print(menu.enabled)

            # Set menu enabled state
            menu.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the menu.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameMenu', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the menu width.

        Returns
        -------
            `int`:
                The current width of the menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the menu expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the menu is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(menu.width)

            # Set a fixed width
            menu.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set menu width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameMenu', 'width', 'None | int', value)

        # Set width
        if value is not None:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)
        else:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the menu height.

        Returns
        -------
            `int`:
                The current height of the menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the menu uses the default height of 28.
                If an integer, the menu is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get menu height
            print(menu.height)

            # Set menu height
            menu.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set menu height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameMenu', 'height', 'None | int', value)

        # Set height
        if value is not None:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)
        else:
            self._height = pyflame.gui_resize(28)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set menu tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the menu.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the menu.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get menu tooltip
            print(menu.tooltip)

            # Set menu tooltip
            menu.tooltip = 'Click to save changes'
            ```
        """

        return self._tooltip

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the menu.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameMenu', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(menu.tooltip_delay)

            # Set tooltip delay
            menu.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameMenu', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(menu.tooltip_duration)

            # Set tooltip duration
            menu.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameMenu', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def update_menu(self, text: str, menu_options: list[str], connect: Callable[..., None] | None=None) -> None:
        """
        Update Menu
        ===========

        Add or update menu with items including a connect signal when an item is selected.

        Args
        ----
            `text` (str):
                Text shown as selected item.

            `menu_options` (List[str]):
                List of option strings to populate the menu.

            `connect` (callable, optional):
                Function called when the menu is changed.
                (Default: `None`)

        Raises
        ------
            TypeError:
                If `text` is not a string.
                If `menu_options` is not a list.
                If items in `menu_options` are not strings
                If `connect` is not None or a callable function or method.

        Example
        -------
            ```
            some_menu.update_menu(
                text='Current Menu Selection',
                menu_options=[
                    new_option1,
                    new_option2,
                    new_option3
                    ],
                connect=some_function,
                )
            ```
        """

        # Validate Arguments
        if not isinstance(text, str):
            pyflame.raise_type_error('PyFlameMenu.update_menu', 'text', 'str', text)
        if not isinstance(menu_options, list):
            pyflame.raise_type_error('PyFlameMenu.update_menu', 'menu_options', 'list', menu_options)
        if not all(isinstance(menu, str) for menu in menu_options):
            pyflame.raise_type_error('PyFlameMenu.update_menu', 'menu_options:items', 'str', menu_options)
        if connect is not None and not callable(connect):
            pyflame.raise_type_error('PyFlameMenu.update_menu', 'connect', 'Callable', connect)

        # Keep internal options in sync for refresh_menu()
        self._menu_options = menu_options

        # Set button text
        self.text = text

        # Clear existing menu options
        self.menu.clear()

        # Add new menu options
        for menu in menu_options:
            new_menu = self.menu.addAction(menu, partial(self._create_menu, menu, connect))
            new_menu.setFont(FONT)  # Apply font to menu item

        self._update_dropdown_visibility()

    def refresh_menu(self) -> None:
        """
        Refresh Menu
        ============

        Rebuilds the menu using the current `menu_options` list.
        """

        self.menu_options = self._menu_options

    #-------------------------------------
    # [Internal Methods]
    #-------------------------------------

    def _update_dropdown_visibility(self) -> None:
        """
        Show dropdown only when there are two or more options.
        With zero or one option, no menu is shown and the button displays the single option (or empty).
        """
        options = self._menu_options
        if len(options) <= 1:
            self.setMenu(None)
            self.setText(' ' + (options[0] if options else ''))
        else:
            self.setMenu(self.menu)
            current = self.text
            if current not in options:
                self.text = options[0]

    def _match_push_button_width(self):
        """
        Match Menu Width
        ================

        Match the width of the menu to the width of the button.
        """

        self.menu.setMinimumWidth(self.size().width())

    def _create_menu(self, menu, connect):

        self.setText(' ' + menu) # Add space to text to create padding. Space is removed when text is returned.

        # Add connect to menu
        if connect:
            connect()

    #-------------------------------------
    # [Stylesheets]
    #-------------------------------------

    def _set_button_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
        """

        # Set menu indicator to show or hide
        if self._menu_indicator:
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
                text-align: {self._align.value};
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
                {menu_indicator_style} # Insert menu indicator style
            """)

    def _set_menu_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============

        This private method sets the PyFlamePushButtonMenu stylesheet.

        Example
        -------
            ```
            self._set_menu_stylesheet()
            ```
        """

        self.menu.setStyleSheet(f"""
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

    #-------------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameColorMenu(QtWidgets.QPushButton):
    """
    PyFlameColorMenu
    ==========================

    Custom QT Flame Color Menu Widget Subclass

    Args
    ----
        `color_options` (dict, optional):
            Dictionary of color names and their RGBA values. Values must be normalized
            floats between 0.0 and 1.0.
            (Default:
                `{
                'No Color'    : (0.0,   0.0,   0.0,   0.0),
                'Red'         : (0.310, 0.078, 0.078, 1.0),
                'Green'       : (0.125, 0.224, 0.165, 1.0),
                'Bright Green': (0.118, 0.396, 0.196, 1.0),
                'Blue'        : (0.176, 0.227, 0.322, 1.0),
                'Light Blue'  : (0.227, 0.325, 0.396, 1.0),
                'Purple'      : (0.318, 0.263, 0.424, 1.0),
                'Orange'      : (0.467, 0.290, 0.161, 1.0),
                'Gold'        : (0.380, 0.380, 0.235, 1.0),
                'Yellow'      : (0.592, 0.592, 0.180, 1.0),
                'Grey'        : (0.537, 0.537, 0.537, 1.0),
                'Black'       : (0.0,   0.0,   0.0,   1.0)
                }`
            )

        `color` (str):
            Current color selection. Must exist in `color_options`.
            (Default: `'No Color'`)

        `menu_indicator` (bool, optional):
            Whether the menu indicator arrow is shown.
            (Default: `False`)

        `enabled` (bool, optional):
            Whether the menu is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the menu in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the menu in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `color_options` (Dict[float, float, float, float], optional):
            Get or set dictionary of available color names and RGBA values.
            (Default:
                `{
                'No Color'    : (0.0,   0.0,   0.0,   0.0),
                'Red'         : (0.310, 0.078, 0.078, 1.0),
                'Green'       : (0.125, 0.224, 0.165, 1.0),
                'Bright Green': (0.118, 0.396, 0.196, 1.0),
                'Blue'        : (0.176, 0.227, 0.322, 1.0),
                'Light Blue'  : (0.227, 0.325, 0.396, 1.0),
                'Purple'      : (0.318, 0.263, 0.424, 1.0),
                'Orange'      : (0.467, 0.290, 0.161, 1.0),
                'Gold'        : (0.380, 0.380, 0.235, 1.0),
                'Yellow'      : (0.592, 0.592, 0.180, 1.0),
                'Grey'        : (0.537, 0.537, 0.537, 1.0),
                'Black'       : (0.0,   0.0,   0.0,   1.0)
                }`
            )

        `color` (str, optional):
            Get or set the color name of the selected color.
            (Default: `No Color`)

        `color_value` (tuple[float, float, float, float]):
            Get the RGBA(Tuple) color value of the selected color.
            (Default: (0.0, 0.0, 0.0, 0.0))

        `menu_indicator` (bool, optional):
            Get or set whether the menu indicator arrow is shown.
            (Default: `False`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Private Methods
    ---------------
        `_set_color(color: str)`:
            Set the color of the PyFlameColorMenu.

        `_generate_color_icon(color: Tuple[float, float, float, float])`:
            Generate a color icon.

        `_create_menu(color: str)`:
            Create a menu.

        `_match_push_button_width()`:
            Match the width of the push button to the width of the menu.

    Examples
    --------
        To create a PyFlameColorMenu:
        ```
        color_menu = PyFlameColorMenu()
        ```

        To set or get any PyFlameColorMenu property:
        ```
        # Set property
        color_menu.color = 'Red'

        # Get property
        print(color_menu.color)
        ```
    """

    def __init__(self: 'PyFlameColorMenu',
                 color_options: Dict[str, Tuple[float, float, float, float]]={
                    'No Color'    : (0.0, 0.0, 0.0, 0.0),
                    'Red'         : (0.310, 0.078, 0.078, 1.0),
                    'Green'       : (0.125, 0.224, 0.165, 1.0),
                    'Bright Green': (0.118, 0.396, 0.196, 1.0),
                    'Blue'        : (0.176, 0.227, 0.322, 1.0),
                    'Light Blue'  : (0.227, 0.325, 0.396, 1.0),
                    'Purple'      : (0.318, 0.263, 0.424, 1.0),
                    'Orange'      : (0.467, 0.290, 0.161, 1.0),
                    'Gold'        : (0.380, 0.380, 0.235, 1.0),
                    'Yellow'      : (0.592, 0.592, 0.180, 1.0),
                    'Grey'        : (0.537, 0.537, 0.537, 1.0),
                    'Black'       : (0.0, 0.0, 0.0, 1.0),
                    },
                 color: str = 'No Color',
                 menu_indicator: bool=False,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Widget Settings
        self.setFont(FONT)
        self.setText(color)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.color_options = color_options
        self.color = color
        self.menu_indicator = menu_indicator
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Create Menu
        self.color_menu = QtWidgets.QMenu(self)
        self.color_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.color_menu.setFont(FONT)
        self.color_menu.aboutToShow.connect(self._match_push_button_width) # Match menu width to button width

        # Set initial color
        self._set_color(self.color)

        # Add color menu options
        for color_name, color_value in self.color_options.items():
            icon = self._generate_color_icon(color_value)
            action = QAction(icon, color_name, self)
            action.triggered.connect(partial(self._create_menu, color_name))
            action.setFont(FONT)
            self.color_menu.addAction(action)
        self.setMenu(self.color_menu)

        # Set Stylesheets
        self._set_button_stylesheet(menu_indicator)
        self._set_menu_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def color_options(self) -> Dict[str, Tuple[float, float, float, float]]:
        """
        Color Options
        =============

        Get or set the color options.

        Returns
        -------
            Dict[str, Tuple[float, float, float, float]]:
                Color options and their RGBA values.

        Set
        ---
            `color_options` (Dict[str, Tuple[float, float, float, float]]):
                Color options and their RGBA values.

        Raises
        ------
            TypeError:
                If the provided `color_options` is not a dictionary.
                If the key in `color_options` is not a string.
                If the value in `color_options` is not a tuple of 4 floats.

        Examples
        --------
            ```
            # Get color options
            print(color_menu.color_options)

            # Set color options
            color_menu.color_options = {
                'Red': (1.0, 0.0, 0.0, 1.0),
                'Green': (0.0, 1.0, 0.0, 1.0),
                'Blue': (0.0, 0.0, 1.0, 1.0),
                }
            ```
        """

        return self._color_options

    @color_options.setter
    def color_options(self, color_options: Dict[str, Tuple[float, float, float, float]]) -> None:
        """
        Color Options
        =============

        Set the color options.
        """

        # Validate Argument
        if not isinstance(color_options, dict):
            pyflame.raise_type_error('PyFlameColorMenu', 'color_options', 'dict', color_options)

        for value in color_options.values():
            if len(value) != 4:
                pyflame.raise_type_error(error_message='Value in color options must be a tuple of 4 floats representing RGBA values.')

        for key, value in color_options.items():
            if not isinstance(key, str):
                pyflame.raise_type_error('PyFlameColorMenu.color_options', 'key', 'str', key)
            if not isinstance(value, tuple):
                pyflame.raise_type_error('PyFlameColorMenu.color_options', 'value', 'tuple', value)

        # Set color options
        self._color_options = color_options

    @property
    def color(self) -> str:
        """
        Color
        =====

        Get or set the color.

        Returns
        -------
            str:
                The name of the selected color.

        Set
        ---
            `value` (str):
                Name of color to select.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get selected color
            print(menu.color)

            # Set selected menu text
            menu.color = 'Red'
            ```
        """

        return super().text().lstrip()

    @color.setter
    def color(self, value: str) -> None:
        """
        Set Color
        =========

        Set the color.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameColorMenu', 'color', 'str', value)

        self.setText(value)

    @property
    def color_value(self) -> Tuple[float, float, float, float]:
        """
        Color Value
        ===========

        Get the color value as a RGBA float tuple.

        Returns
        -------
            Tuple[float, float, float, float]:
                The color value.
        """

        return self.color_options[self.color]

    @property
    def menu_indicator(self) -> bool:
        """
        Menu Indicator
        ==============

        Get or set the menu indicator whether the menu indicator is present.

        Returns
        -------
            bool:
                The current menu indicator state.

        Set
        ---
            `value` (bool):
                The menu indicator state to set.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get current menu indicator
            print(menu.menu_indicator)

            # Set menu indicator
            menu.menu_indicator = True
            ```
        """

        return self._menu_indicator

    @menu_indicator.setter
    def menu_indicator(self, value: bool) -> None:
        """
        Menu Indicator
        ==============

        Set the menu indicator.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameColorMenu', 'menu_indicator', 'bool', value)

        # Set menu indicator
        self._menu_indicator = value

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set menu enabled state.

        Returns
        -------
            bool: `True` if the menu is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get menu enabled state
            print(menu.enabled)

            # Set menu enabled state
            menu.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the menu.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameMenu', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the menu width.

        Returns
        -------
            `int`:
                The current width of the menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the menu expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the menu is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(menu.width)

            # Set a fixed width
            menu.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set menu width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameColorMenu', 'width', 'None | int', value)

        # Set width
        if value is not None:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)
        else:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the menu height.

        Returns
        -------
            `int`:
                The current height of the menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the menu uses the default height of 28.
                If an integer, the menu is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get menu height
            print(menu.height)

            # Set menu height
            menu.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set menu height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameColorMenu', 'height', 'None | int', value)

        # Set height
        if value is not None:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)
        else:
            self._height = pyflame.gui_resize(28)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set menu tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the menu.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the menu.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get menu tooltip
            print(menu.tooltip)

            # Set menu tooltip
            menu.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the menu.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameColorMenu', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(menu.tooltip_delay)

            # Set tooltip delay
            menu.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameColorMenu', 'tooltip', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(menu.tooltip_duration)

            # Set tooltip duration
            menu.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameColorMenu', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Internal Methods]
    #-------------------------------------

    def _set_color(self, color: str) -> None:
        """
        Set Color
        =========

        Updates the button text and icon to reflect the selected color.

        Args
        ----
            `color (str)`:
                The name of the color to set.

        Raises
        ------
            ValueError: If `color` is not in `color_options`.

        Example
        -------
            Set the color of the PyFlameColorMenu to 'Red':
            ```
            button.set_color('Red')
            ```
        """

        if color not in self.color_options:
            pyflame.raise_value_error(error_message=f'PyFlameColorMenu."{color}" is not a valid color option. {color} must be one of the following: {self.color_options.keys()}')

        # Update button text
        self.setText(color)

        # Update button icon
        icon = self._generate_color_icon(self.color_options[color])
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(FONT_SIZE, FONT_SIZE))

    def _generate_color_icon(self, color_value: Tuple[float, float, float, float]) -> QtGui.QIcon:
        """
        Generate Color Icon
        ===================

        This private method generates a color icon based on the given color value.
        The size of the icon is based on the widget font size.

        Args
        ----
            `color_value` (Tuple[float, float, float]):
                The RGB color value, where each float is between 0 and 1.

        Returns
        -------
            QtGui.QIcon:
                The generated color icon.

        Raises
        ------
            TypeError:
                If `color_value` is not a tuple.
            ValueError:
                If `color_value` does not contain exactly three float values between 0 and 1.

        Example
        -------
            Generate an icon for the color red:
            ```
            red_icon = widget._generate_color_icon((1.0, 0.0, 0.0))
            ```
        """

        # Validate Argument types
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

        Args
        ----
            `color_name (str)`:
                The name of the color to set for the button.

        Raises
        ------
            TypeError:
                If `color_name` is not a string.
            ValueError:
                If `color_name` does not correspond to any available color option.

        Example
        -------
            Update the button to reflect the color 'red':
            ```
            button._create_menu('red')
            ```
        """

        # Validate Argument types
        if not isinstance(color_name, str):
            raise TypeError(f'_create_menu: Invalid type for color_name: {type(color_name)}. Must be a string.')
        if color_name not in self.color_options:
            raise ValueError(f'_create_menu: Invalid color_name: "{color_name}". Must be one of the available color options.')

        # Update the button's text and icon
        self.setText(color_name)
        icon = self._generate_color_icon(self.color_options[color_name])
        self.setIcon(icon)
        self.setIconSize(QtCore.QSize(FONT_SIZE, FONT_SIZE))

    def _match_push_button_width(self):
        """
        Match Menu Width
        ================

        Match the width of the menu to the width of the button.
        """

        self.color_menu.setMinimumWidth(self.size().width())

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_button_stylesheet(self, menu_indicator) -> None:
        """
        Set Button Stylesheet
        =====================

        This private method sets the PyFlameColorMenu stylesheet.
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
            {menu_indicator_style} # Insert menu indicator style
            """)

    def _set_menu_stylesheet(self) -> None:
        """
        Set Menu Stylesheet
        ===================

        This private method sets the PyFlameColorMenu menu stylesheet.
        """

        self.color_menu.setStyleSheet(f"""
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

    #-------------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameTokenMenu(QtWidgets.QPushButton):
    """
    PyFlameTokenMenu
    ================

    Custom QT Flame Token Menu Widget Subclass

    When a token is chosen from the menu, it is inserted into the PyFlameEntry widget specified by token_dest.

    Args
    ----
        `text` (str, optional):
            Text displayed on button.
            (Default: `Add Token`)

        `token_dict` (dict, optional):
            Dictionary defining tokens. {'Token Name': '<Token>'}.
            (Default: `None`)

        `token_dest` (PyFlameEntry, optional):
            PyFlameEntry that token value will be applied to.
            (Default: `None`)

        `clear_dest` (bool, optional):
            Clear destination PyFlameEntry before inserting token.
            (Default: `False`)

        `enabled` (bool, optional):
            Whether the menu is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the menu in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the menu in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set current token menu text.
            (Default: `Add Token`)

        `token_dict` (Dict[str, str]):
            Get or set token dictionary.
            (Default: `None`)

        `token_dest` (PyFlameEntry | None):
            Get or set token destination. Usually a PyFlameEntry widget.
            (Default: `None`)

        `clear_dest` (bool):
            Get or set whether or not to clear the token destination. True to clear, otherwise False.
            (Default: `False`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `add_menu_options(new_options)`:
            Clears existing menu and adds new menu options PyFlameTokenMenu menu.

    Examples
    --------
        To create a PyFlameTokenMenu:
        ```
        token_push_button = PyFlameTokenMenu(
            token_dict={
                'Token 1': '<Token1>',
                'Token 2': '<Token2>',
                },
            token_dest=SomePyFlameEntry,
            )
        ```

        To set or get any button property:
        ```
        # Set property
        token_push_button.text = 'Token'

        # Get property
        print(token_push_button.text)
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
    def __init__(self,
                 text: str='Add Token',
                 token_dict: Dict[str, str] | None=None,
                 token_dest: PyFlameEntry | None=None,
                 clear_dest: bool=False,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Create token menu
        self.token_menu = QtWidgets.QMenu(self)
        self.token_menu.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set properties
        self.text = text
        self.token_dict = token_dict or {}
        self.token_dest = token_dest
        self.clear_dest = clear_dest
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Set menu
        self.setMenu(self.token_menu)

        # Build token menu
        self._build_token_menu()

        # Set Stylesheets
        self._set_stylesheet()
        self._set_menu_stylesheet()

    #---------------------------
    # Properties
    #---------------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set Token Menu button text.

        Returns
        -------
            str:
                The text of the Token Menu.

        Set
        ---
            `value` (str):
                The text to set for the Token Menu.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get Token Menu text
            print(token_push_button.text)

            # Set button text
            token_push_button.text = 'Save'
            ```
        """

        return super().text()

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set Token Menu text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTokenMenu', 'text', 'str', value)

        # Set text
        self.setText(value)

    @property
    def token_dict(self) -> Dict[str, str]:
        """
        Token Dictionary
        ================

        Get or set the token dictionary.

        Returns
        -------
            Dict[str, str]:
                The token dictionary.

        Set
        ---
            `value` (Dict[str, str]):
                The token dictionary.

        Raises
        ------
            TypeError:
                If `value` is not a dictionary.

        Examples
        --------
            ```
            # Get token dictionary
            print(token_push_button.token_dict)

            # Set token dictionary
            token_push_button.token_dict = {
                'Token 1': '<Token1>',
                'Token 2': '<Token2>',
            }
            ```
        """

        return self._token_dict

    @token_dict.setter
    def token_dict(self, value: Dict[str, str]) -> None:
        """
        Token Dictionary
        ================

        Set the token dictionary.
        """

        # Validate Argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameTokenMenu', 'token_dict', 'dict', value)

        # Set token dictionary
        self._token_dict = value

        # Rebuild token menu
        self._build_token_menu()

    @property
    def token_dest(self):
        """
        Token Destination
        =================

        Get or set the token destination.

        Returns
        -------
            PyFlameEntry:
                The token destination.

        Set
        ---
            `value` (PyFlameEntry):
                The token destination.

        Raises
        ------
            TypeError:
                If `value` is not a PyFlameEntry.

        Examples
        --------
            ```
            # Get token destination
            print(token_push_button.token_dest)

            # Set token destination
            token_push_button.token_dest = SomePyFlameEntry
            ```
        """

        return self._token_dest

    @token_dest.setter
    def token_dest(self, value: PyFlameEntry) -> None:
        """
        Token Destination
        =================

        Set the token destination.
        """

        # Validate Argument
        if value is not None and not isinstance(value, PyFlameEntry):
            pyflame.raise_type_error('PyFlameTokenMenu', 'token_dest', 'PyFlameEntry', value)

        # Set token destination
        self._token_dest = value

    @property
    def clear_dest(self) -> bool:
        """
        Clear Destination
        =================

        Get whether the Token Menu should clear the destination.

        Returns
        -------
            bool:
                Whether the Token Menu should clear the destination.

        Set
        ---
            `value` (bool):
                Whether the Token Menu should clear the destination.

        Raises
        ------
            TypeError:
                If `value` is not a boolean.

        Examples
        --------
            ```
            # Get clear destination
            print(token_push_button.clear_dest)

            # Set clear destination
            token_push_button.clear_dest = True
            ```
        """

        return self._clear_dest

    @clear_dest.setter
    def clear_dest(self, value: bool) -> None:
        """
        Clear Destination
        =================

        Set whether the Token Menu should clear the destination.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTokenMenu', 'clear_dest', 'bool', value)

        # Set clear destination
        self._clear_dest = value

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set Token Menu enabled state.

        Returns
        -------
            bool: `True` if the Token Menu is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get Token Menu enabled state
            print(token_push_button.enabled)

            # Set Token Menu enabled state
            token_push_button.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the Token Menu button.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTokenMenu', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the Token Menu width.

        Returns
        -------
            `int`:
                The current width of the Token Menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Token Menu expands to fit the maximum width set by the layout.
                If an integer, the Token Menu is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(token_push_button.width)

            # Set a fixed width
            token_push_button.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set Token Menu width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTokenMenu', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the Token Menu height.

        Returns
        -------
            `int`:
                The current height of the Token Menu in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Token Menu uses the default height of 28.
                If an integer, the Token Menu is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get Token Menu height
            print(token_push_button.height)

            # Set Token Menu height
            token_push_button.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set Token Menu height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTokenMenu', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set Token Menu tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the Token Menu.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the Token Menu.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get Token Menu tooltip
            print(token_push_button.tooltip)

            # Set Token Menu tooltip
            token_push_button.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the Token Menu.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTokenMenu', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(button.tooltip_delay)

            # Set tooltip delay
            button.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTokenMenu', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(button.tooltip_duration)

            # Set tooltip duration
            button.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTokenMenu', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #---------------------------
    # Methods
    #---------------------------

    def add_menu_options(self, new_options: Dict[str, str]):
            """
            Add Menu Options
            ================

            Clears existing PyFlameTokenMenu menu and creats new menu from `new_options`.

            Args
            ----
                `new_options` (dict):
                    Dictionary of new token options to add. The key is the name of the token to display in the menu, and the
                    value is the token to insert into the destination PyFlameLineEdit.

            Raises
            ------
                TypeError:
                    If `new_options` is not a dictionary
                    If the dictionary does not contain strings as keys and values.

            Example
            -------
                Add new options to PyFlameTokenMenu menu:
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
                pyflame.raise_type_error('PyFlameTokenMenu.add_menu_options', 'new_options', 'dict', new_options)

            def insert_new_token(token):
                """
                Insert New Token
                ================

                Insert the new token into the destination PyFlameEntry.

                Args
                ----
                   `token` (str):
                        The token to insert into the destination PyFlameEntry.
                """

                if self._clear_dest:
                    self._token_dest.setText('')
                for key, value in self._token_dict.items():
                    if key == token:
                        token_name = value
                        self._token_dest.insert(token_name)

            # Clear existing token menu and dictionary
            self.token_menu.clear()
            self._token_dict.clear()

            # Add new menu options
            for key, value in new_options.items():
                self._token_dict[key] = value
                action = self.token_menu.addAction(key, partial(insert_new_token, key))
                action.setFont(FONT)  # Apply font to action

    #---------------------------
    # Private
    #---------------------------

    def _build_token_menu(self):
        """
        Build Token Menu
        ================

        Build the token menu.
        """

        self.token_menu.clear()

        def insert_token(token):
            if self.clear_dest:
                self.token_dest.setText('')
            if token in self._token_dict:
                self.token_dest.insert(self._token_dict[token])

        for key in self._token_dict:
            action = self.token_menu.addAction(key, partial(insert_token, key))
            action.setFont(FONT)

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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
        """)

    def _set_menu_stylesheet(self):
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

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameSlider(QtWidgets.QLineEdit):
    """
    PyFlameSlider
    =============

    Custom QT Flame Slider Widget Subclass

    Args
    ----
        `min_value` (int or float):
            Minimum value.
            (Default: `0`)

        `max_value` (int or float):
            Maximum value.
            (Default: `100`)

        `start_value` (int or float):
            Initial value.
            (Default: `0`)

        `rate` (int or float, optional):
            Slider sensitivity. The value should be between 1 and 10. Lower values are more sensitive.
            (Default: `10`)

        `connect` (callable, optional):
            Function called when slider value is changed.
            (Default: `None`)

        `enabled` (bool, optional):
            Whether the slider is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the slider in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the slider in pixels. If `None`, defaults to 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `min_value` (int or float):
            Get or set the minimum Slider value.
            (Default: `0`)

        `max_value` (int or float):
            Get or set the maximum Slider value.
            (Default: `100`)

        `value` (int or float):
            Get or set the current Slider value.
            (Default: `0`)

        `value_str` (str):
            Get the current Slider value as a string.
            (Default: `0`)

        `rate` (int):
            Get or set the Slider sensitivity rate.
            (Default: `10`)

        `connect` (callable):
            Get or set the function to be called when the Slider value is changed.
            (Default: `None`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `connect_callback(callback)`:
            Connect a callback function to the Slider value change event.

    Examples
    --------
        To create a PyFlameSlider:
        ```
        slider = PyFlameSlider(
            min_value=-20,
            max_value=20,
            start_value=0,
            )
        ```

        To set or get any Slider property:
        ```
        # Set property
        slider.value = 5

        # Get property
        print(slider.value)
        ```
    """

    def __init__(self: 'PyFlameSlider',
                 min_value: int=0,
                 max_value: int=100,
                 start_value: int=0,
                 rate: int | float=10,
                 connect: Callable[..., None] | None=None,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Slider Setup
        self.font = FONT
        self.setFont(self.font)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.min_value = min_value
        self.max_value = max_value
        self.value = start_value
        self.rate = rate
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration
        self.connect_callback(connect)
        self.textChanged.connect(self._value_changed)

        # Set misc variables
        self.steps = 1
        self.value_at_press = None
        self.pos_at_press = None

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

                # Slider Stylesheet
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
            slider.setValue(float(self.text()))
            slider.setFont(self.font)

        slider = Slider(start_value, min_value, max_value, pyflame.gui_resize(self.width))
        self.textChanged.connect(set_slider)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(slider)
        self.vbox.setContentsMargins(0, pyflame.gui_resize(24), 0, 0)

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def min_value(self) -> int | float:
        """
        Minimum Value
        =============
        """

        return self._min_value

    @min_value.setter
    def min_value(self, value: int | float) -> None:
        """
        Minimum Value
        =============
        """

        # Validate Argument
        if not isinstance(value, (int, float)):
            pyflame.raise_type_error('PyFlameSlider', 'min_value', 'int or float', value)

        # Set whether slider is float or int based on give value
        if isinstance(value, float):
            self.spinbox_type = 'Float'
        else:
            self.spinbox_type = 'Integer'

        self._min_value = value

    @property
    def max_value(self) -> int | float:
        """
        Maximum Value
        =============
        """

        return self._max_value

    @max_value.setter
    def max_value(self, value: int | float) -> None:
        """
        Maximum Value
        =============
        """

        # Validate Argument
        if not isinstance(value, (int, float)):
            pyflame.raise_type_error('PyFlameSlider', 'max_value', 'int or float', value)
        if type(value) != type(self._min_value):
            pyflame.raise_type_error('PyFlameSlider', 'max_value', 'value type matching min_value type', value)
        if value <= self._min_value:
            pyflame.raise_value_error('PyFlameSlider', 'max_value', 'value greater than min_value', value)

        self._max_value = value

    @property
    def value(self) -> int | float:
        """
        Value
        =====
        """

        value = float(self.text())

        if value.is_integer():
            return int(value)
        else:
            return value

    @value.setter
    def value(self, value: int | float) -> None:
        """
        Value
        =====
        """

        # Validate Argument
        if not isinstance(value, (int, float)):
            pyflame.raise_type_error('PyFlameSlider', 'value', 'int or float', value)
        if type(value) != type(self._min_value):
            pyflame.raise_type_error('PyFlameSlider', 'value', 'value type matching min_value and max_value types', value)
        if value < self._min_value:
            pyflame.raise_value_error('PyFlameSlider', 'value', 'value equal to or greater than min_value', value)
        if value > self._max_value:
            pyflame.raise_value_error('PyFlameSlider', 'value', 'value equal to or less than max_value', value)

        self._value = value
        self.setValue(value)

    @property
    def value_str(self) -> str:
        """
        Value (String)
        ==============

        Return the current Slider value as a string.
        """

        return self.text()

    @property
    def rate(self) -> int | float:
        """
        Rate
        ====

        Adjust the Slider sensitivity rate.

        Returns
        -------
            `float`:
                The current sensitivity rate of the Slider.

        Set
        ---
            `value` (float):
                The sensitivity rate of the Slider.

        Raises
        ------
            TypeError:
                If the provided `value` is not a float.
            ValueError:
                If the provided `value` is not between 1 and 10.

        Examples
        --------
            ```
            # Get Slider rate
            print(slider.rate)

            # Set Slider rate
            slider.rate = 5
            ```
        """

        return self._rate

    @rate.setter
    def rate(self, value: int | float) -> None:
        """
        Rate
        ====
        """

        # Validate Argument
        if not isinstance(value, (int, float)):
            pyflame.raise_type_error('PyFlameSlider', 'rate', 'int or float', value)
        if not (1 <= value <= 10):
            pyflame.raise_value_error('PyFlameSlider', 'rate', 'value between 1 and 10', value)


        self._rate = value * .1

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set Slider enabled state.

        Returns
        -------
            bool: `True` if the Slider is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get Slider enabled state
            print(slider.enabled)

            # Set Slider enabled state
            slider.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the Slider.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameSlider', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the Slider width.

        Returns
        -------
            `int`:
                The current width of the Slider in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Slider expands to fit the maximum width set by the layout.
                If an integer, the Slider is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(slider.width)

            # Set a fixed width
            slider.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set Slider width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameSlider', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the Slider height.

        Returns
        -------
            `int`:
                The current height of the Slider in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Slider uses the default height of 28.
                If an integer, the Slider is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get Slider height
            print(slider.height)

            # Set Slider height
            slider.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set Slider height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameSlider', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(28)
        else:
            self._height = pyflame.gui_resize(value)
        self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set Slider tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the Slider.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the Slider.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get Slider tooltip
            print(slider.tooltip)

            # Set Slider tooltip
            slider.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the Slider.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameSlider', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(slider.tooltip_delay)

            # Set tooltip delay
            slider.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameSlider', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(slider.tooltip_duration)

            # Set tooltip duration
            slider.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameSlider', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def connect_callback(self, callback: Callable | None) -> None:
        """
        Connect Callback
        ================

        Connect a callback function to the button click event.

        Args
        ----
            callback (Callable):
                The function to call when the button is clicked.

        Raises
        ------
            TypeError:
                If `callback` is not callable.
        """

        if callback is not None and not callable(callback):
            pyflame.raise_type_error('PyFlameSlider.connect_callback', 'callback', 'callable', callback)

        if callback:
            self.clicked.connect(callback)

    #-------------------------------------
    # [Internal Methods]
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

            if calc_entry.text:
                calc_entry.setText(str(float(calc_entry.text) * -1))

        def add_sub(key):

            if calc_entry.text == '':
                calc_entry.setText('0')

            if '**' not in calc_entry.text:
                try:
                    calc_num = eval(calc_entry.text.lstrip('0'))

                    calc_entry.setText(str(calc_num))

                    calc_num = float(calc_entry.text)

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

            if calc_entry.text:
                try:

                    # If only single number set slider value to that number

                    self.setValue(float(calc_entry.text))
                except:

                    # Do math

                    new_value = calculate_entry()
                    self.setValue(float(new_value))

            close_calc()

        def equals():

            if calc_entry.text == '':
                calc_entry.setText('0')

            if calc_entry.text != '0':

                calc_line = calc_entry.text.lstrip('0')
            else:
                calc_line = calc_entry.text

            if '**' not in calc_entry.text:
                try:
                    calc = eval(calc_line)
                except:
                    calc = 0

                calc_entry.setText(str(calc))
            else:
                calc_entry.setText('1')

        def calculate_entry():

            calc_line = calc_entry.text.lstrip('0')

            if '**' not in calc_entry.text:
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

        self.clean_line = False

        class CalcWindow(PyFlameWindow):
            """
            Calculator Window
            =================

            Adds a focus out event to close the window when the user clicks outside of the calculator window or switches focus to another window.
            """

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def _check_close_on_focus_lost(self):
                if not self.isActiveWindow():
                    self._close_check_timer.stop()
                    self.close()


            def closeEvent(self, event):
                self._close_check_timer.stop()
                super().closeEvent(event)


            def focusOutEvent(self, event):
                """
                Focus lost — clicked outside or switched focus
                """

                # Close calculator
                self.clicked_outside()

                # Call super
                super().focusOutEvent(event)

            def clicked_outside(self) -> None:
                """
                Close calculator
                """

                self.close()

            def keyPressEvent(self, event):
                """
                Handle keyboard input for calculator buttons
                """

                key = event.key()
                text = event.text()

                # Number keys 0-9
                if text in '0123456789':
                    button_press(text)
                # Operators and decimal point
                elif text == '+':
                    button_press('+')
                elif text == '-':
                    button_press('-')
                elif text == '*':
                    button_press('*')
                elif text == '/':
                    button_press('/')
                elif text == '.':
                    button_press('.')
                # Backspace to delete last character
                elif key == QtCore.Qt.Key_Backspace:
                    calc_entry.backspace()
                else:
                    # Pass unhandled keys to the parent class
                    super().keyPressEvent(event)

        calc_window = CalcWindow(
            title='Calculator',
            title_height=26,
            title_font_size=14,
            message_bar=False,
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=40,
            return_pressed=enter,
            escape_pressed=close_calc,
            parent=self.window(),
            )
        calc_window.move(QtGui.QCursor.pos().x() - 110, QtGui.QCursor.pos().y() - 320)
        calc_window.setWindowFlags(calc_window.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        calc_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Entry
        calc_entry = PyFlameEntry(
            text='',
            )
        calc_entry.returnPressed.connect(enter)

        regex = QRegularExpression('[0-9_,=,/,*,+,\\-,.]+')
        validator = QValidator(regex)
        calc_entry.setValidator(validator)

        #-------------------------------------

        # Buttons
        blank_button = PyFlameButton(
            text='',
            #connect=calc_null,
            )
        blank_button.setDisabled(True)

        plus_minus_button = PyFlameButton(
            text='+/-',
            connect=plus_minus,
            )
        plus_minus_button.setStyleSheet(f"""
            color: {Color.TEXT.value};
            background-color: rgb(45, 55, 68);
        """)

        add_button = PyFlameButton(
            text='Add',
            connect=(partial(add_sub, 'add')),
            )
        sub_button = PyFlameButton(
            text='Sub',
            connect=(partial(add_sub, 'sub')),
            )

        #-------------------------------------

        clear_button = PyFlameButton(
            text='C',
            connect=clear,
            )
        equal_button = PyFlameButton(
            text='=',
            connect=equals,
            )
        div_button = PyFlameButton(
            text='/',
            connect=(partial(button_press, '/')),
            )
        mult_button = PyFlameButton(
            text='*',
            connect=(partial(button_press, '*')),
            )

        #-------------------------------------

        _7_button = PyFlameButton(
            text='7',
            connect=(partial(button_press, '7')),
            )
        _8_button = PyFlameButton(
            text='8',
            connect=(partial(button_press, '8')),
            )
        _9_button = PyFlameButton(
            text='9',
            connect=(partial(button_press, '9')),
            )
        minus_button = PyFlameButton(
            text='-',
            connect=(partial(button_press, '-')),
            )

        #-------------------------------------

        _4_button = PyFlameButton(
            text='4',
            connect=(partial(button_press, '4')),
            )
        _5_button = PyFlameButton(
            text='5',
            connect=(partial(button_press, '5')),
            )
        _6_button = PyFlameButton(
            text='6',
            connect=(partial(button_press, '6')),
            )
        plus_button = PyFlameButton(
            text='+',
            connect=(partial(button_press, '+')),
            )

        #-------------------------------------

        _1_button = PyFlameButton(
            text='1',
            connect=(partial(button_press, '1')),
            )
        _2_button = PyFlameButton(
            text='2',
            connect=(partial(button_press, '2')),
            )
        _3_button = PyFlameButton(
            text='3',
            connect=(partial(button_press, '3')),
            )
        enter_button = PyFlameButton(
            text='Enter',
            connect=enter,
            height=61,
            )

        #-------------------------------------

        _0_button = PyFlameButton(
            text='0',
            connect=(partial(button_press, '0')),
            )
        dot_button = PyFlameButton(
            text='.',
            connect=(partial(button_press, '.')),
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
        calc_window.grid_layout.addWidget(dot_button, 6, 2)

    def _value_changed(self):

        # If value is greater or less than min/max values set values to min/max
        if self.value < self.min_value:
            self.setText(str(self.min_value))
        if self.value > self.max_value:
            self.setText(str(self.max_value))

    def mousePressEvent(self, event):

        if event.buttons() == QtCore.Qt.LeftButton:
            self.value_at_press = self.value
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

            if self.pos_at_press is None:
                return

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
            delta /= 10 * self.rate # Make movement less sensitive.
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

        self.min_value = value

    def setMaximum(self, value):

        self.max_value = value

    def setValue(self, value):

        if self.min_value is not None:
            value = max(value, self.min_value)

        if self.max_value is not None:
            value = min(value, self.max_value)

        if self.spinbox_type == 'Integer':
            self.setText(str(int(value)))
        else:
            # Keep float values to two decimal places
            self.setText('%.2f' % float(value))

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
        """

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
            """)

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameTable(QtWidgets.QTableView):
    """
    PyFlameTable
    ============

    Custom QT Table Widget Subclass

    Args
    ----
        `csv_file_path` (str, optional):
            The path to the CSV file to load.
            (Default: `None`)

        `alternating_row_colors` (bool, optional):
            Enable alternating row background colors.
            (Default: `True`)

        `enabled` (bool, optional):
            Whether the table is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the table in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the table in pixels. If `None`, it expands to fit the layout. Minimum height is 28.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Properties
    ----------
        `csv_file_path` (str):
            Get or set the file path to the loaded CSV file.
            (Default: `None`)

        `alternating_row_colors` (bool):
            Get or set alternating row colors.
            (Default: `True`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `load_csv(csv_file_path: str) -> None`:
            Load CSV file into the Table.

        `save_csv_file(csv_file_path: str) -> None`:
            Save the CSV file to the given path.

    Examples
    --------
        ```
        # Create a new Table
        table = PyFlameTable()

        # Load a CSV file into the Table
        table.load_csv('path/to/csv/file.csv')

        # Save the Table to a CSV file
        table.save_csv_file('path/to/csv/file.csv')
        ```

        To set or get any property:
        ```
        # Set property
        table.enabled = True

        # Get property
        print(table.enabled)
        ```
    """

    def __init__(self: 'PyFlameTable',
                 csv_file_path: str | None=None,
                 alternating_row_colors: bool=True,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Widget Settings
        self.setFont(FONT)
        self.horizontalHeader().setFont(FONT)
        self.verticalHeader().setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionBehavior(QtWidgets.QTableView.SelectItems)  # Allow individual cell selection
        self.setSelectionMode(QtWidgets.QTableView.ExtendedSelection)  # Allow multi-cell selection

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.alternating_row_colors = alternating_row_colors
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        # Set Model
        self.model = QtGui.QStandardItemModel()
        self.setModel(self.model)

        # Configure headers
        self.horizontalHeader().setSectionsClickable(True)
        self.horizontalHeader().setSectionsMovable(True)
        self.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.horizontalHeader().sectionDoubleClicked.connect(self._rename_column_header)

        # Set right-click context menus
        self.verticalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.verticalHeader().customContextMenuRequested.connect(self._show_row_menu)
        self.horizontalHeader().customContextMenuRequested.connect(self._show_column_menu)

        # Prevent selecting all column items when clicking on header
        self.horizontalHeader().mousePressEvent = self._block_column_selection

        # Load CSV file
        self.load_csv(csv_file_path)

        # Set widgetstylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def csv_file_path(self) -> str | None:
        """
        CSV File Path
        =============

        Get the currently loaded CSV file path.
        """

        return self._csv_file_path

    @property
    def alternating_row_colors(self) -> bool:
        """
        Alternating Row Colors
        ======================

        Get or set alternating row colors.

        Returns
        -------
            bool: `True` if alternating row colors are enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get alternating row colors
            print(table.alternating_row_colors)

            # Set alternating row colors
            table.alternating_row_colors = False
            ```
        """

        return self._alternating_row_colors

    @alternating_row_colors.setter
    def alternating_row_colors(self, value: bool) -> None:
        """
        Alternating Row Colors
        ======================

        Set alternating row colors.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTable', 'alternating_row_colors', 'bool', value)

        # Set alternating row colors
        self._alternating_row_colors = value
        self.setAlternatingRowColors(value)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set Table enabled state.

        Returns
        -------
            bool: `True` if the Table is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get Table enabled state
            print(table.enabled)

            # Set Table enabled state
            table.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the Table.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTable', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the Table width.

        Returns
        -------
            `int`:
                The current width of the Table in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Table expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the Table is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(table.width)

            # Set a fixed width
            table.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set the Table width.
        """

        # Validate Argument type
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTable', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the Table height.

        Returns
        -------
            `int`:
                The current height of the Table in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the Table expands to fit the maximum height set by the layout. Minimum height is 28 pixels.
                If an integer, the Table is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current height
            print(table.height)

            # Set a fixed height
            table.height = 140
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set the Table height.
        """

        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTable', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)
        else:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set Table tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the Table.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the Table.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get Table tooltip
            print(table.tooltip)

            # Set Table tooltip
            table.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the Table.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTable', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(table.tooltip_delay)

            # Set tooltip delay
            table.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTable', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(table.tooltip_duration)

            # Set tooltip duration
            table.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTable', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def load_csv(self, csv_file_path: str | None=None) -> None:
        """
        Load CSV
        ========

        Load CSV file into the table.

        Args
        ----
            csv_file_path: str
                The path to the CSV file to load.

        Raises
        ------
            TypeError:
                If `csv_file_path` is not a string.

        Example
        -------
            ```
            table = PyFlameTable()
            table.load_csv('path/to/csv/file.csv')
            ```
        """

        # Validate Argument
        if csv_file_path is not None and not isinstance(csv_file_path, str):
            pyflame.raise_type_error('PyFlameTable.load_csv', 'csv_file_path', 'str', csv_file_path)

        self._csv_file_path = csv_file_path  # Save the path after successful load

        if not csv_file_path:
            return

        # Clear table
        self.model.clear()

        # Read CSV file
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            data = list(reader)

            # If data is not empty, set column count and header labels
            if data:
                self.model.setColumnCount(len(data[0]))
                self.model.setHorizontalHeaderLabels(data[0])

                # Append rows
                for row in data[1:]:
                    items = [QtGui.QStandardItem(cell) for cell in row]
                    self.model.appendRow(items)

    def save_csv_file(self, csv_file_path: str) -> None:
        """
        Save CSV File
        =============

        Save the CSV file to the given path.

        Args
        ----
            csv_file_path: str
                The path to save the CSV file to.

        Raises
        ------
            TypeError:
                If `csv_file_path` is not a string.

        Example
        -------
            ```
            table = PyFlameTable()
            table.save_csv_file('path/to/csv/file.csv')
            ```
        """

        # Validate Argument
        if not isinstance(csv_file_path, str):
            pyflame.raise_type_error('PyFlameTable.save_csv_file', 'csv_file_path', 'str', csv_file_path)

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
    # [Internal Methods]
    #-------------------------------------

    def _rename_column_header(self, index: int) -> None:
        """
        Rename Column Header
        ====================

        Rename a column header when double-clicked.

        Args
        ----
            index: int
                The index of the column header to rename.
        """

        if not isinstance(index, int):
            pyflame.raise_type_error('PyFlameTable._rename_column_header', 'index', 'int', index)

        # Get current header text
        current_header_text = self.model.headerData(index, QtCore.Qt.Horizontal)

        # Open input dialog to get new value
        rename_column_header_input_dialog = PyFlameInputDialog(
            text=current_header_text,
            title='Rename Column Header',
            parent = self.parentWidget() if isinstance(self.parentWidget(), PyFlameWindow) else None
            )

        header_text = rename_column_header_input_dialog.text

        # If the user confirmed, rename the column header
        if header_text:
            self.model.setHeaderData(index, QtCore.Qt.Horizontal, header_text, QtCore.Qt.DisplayRole)

    def _rename_selected_cells(self) -> None:
        """
        Rename Selected Cells
        =====================

        Rename all selected cells to a new value.
        """

        selected_indexes = self.selectionModel().selectedIndexes()
        if not selected_indexes:
            return

        item = self.model.itemFromIndex(selected_indexes[0])
        if not item:
            return

        # Open input dialog to get new value
        rename_selected_cells = PyFlameInputDialog(
            label_text='Enter New Value',
            text=item.text(),
            title='Rename Selected Cells',
            parent = self.parentWidget() if isinstance(self.parentWidget(), PyFlameWindow) else None
            )

        # If the user confirmed, rename the selected cells
        cell_text = rename_selected_cells.text
        if cell_text:
            for index in selected_indexes:
                item = self.model.itemFromIndex(index)
                if item:
                    item.setText(cell_text)

    def _show_row_menu(self, position: tuple) -> None:
        """
        Show Right-Click Menu for Rows
        ==============================

        Show right-click menu for rows.

        Args
        ----
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

        Args
        ----
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
    # [Stylesheets]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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

    def _set_menu_stylesheet(self) -> str:
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

        Args
        ----
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

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameTabWidget(QtWidgets.QTabWidget):
    """
    PyFlameTabWidget
    ================

    Custom QT Flame Tab Widget Subclass

    This tab widget uses PyFlameGridLayout for each tab's internal layout.

    Args
    ----
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

        tab_label_width (int):
            Width of each tab.
            (Default: `150`, optional)

        tab_label_height (int):
            Height of each tab.
            (Default: `28`, optional)

        enabled (bool):
            Whether to enable the tab widget.
            (Default: `True`, optional)

        parent (QtWidgets.QWidget, optional):
            Parent widget.
            (Default: `None`, optional)

    Properties
    ----------
        `tab_names` (list[str]):
            The names of the tabs in the tab widget.
            (Default: `[]`, optional)

        `grid_layout_columns` (int):
            The number of columns in the grid layout.
            (Default: `4`, optional)

        `grid_layout_rows` (int):
            The number of rows in the grid layout.
            (Default: `3`, optional)

        `grid_layout_column_width` (int):
            The width of the columns in the grid layout.
            (Default: `150`, optional)

        `grid_layout_row_height` (int):
            The height of the rows in the grid layout.
            (Default: `28`, optional)

        `grid_layout_adjust_column_widths` (dict[int, int]):
            The adjusted widths of the columns in the grid layout.
            (Default: `{}`, optional)

        `grid_layout_adjust_row_heights` (dict[int, int]):
            The adjusted heights of the rows in the grid layout.
            (Default: `{}`, optional)

        `tab_label_width` (int):
            The width of the tab labels.
            (Default: `150`, optional)

        `tab_label_height` (int):
            The height of the tab labels.
            (Default: `28`, optional)

        `tab_pages` (dict[str, PyFlameTabWidget.TabContainer]):
            The tab containers in the tab widget.
            (Default: `{}`, optional)

        `enabled` (bool):
            Whether to enable the tab widget.
            This is passed to the tab containers.
            (Default: `True`, optional)

    Methods
    -------
        `add_tab(name: str) -> PyFlameTabWidget.TabContainer`:
            Add a tab to the tab widget.

        `get_current_tab_name() -> str | None`:
            Get the name of the current tab.

        `get_current_tab_index() -> int`:
            Get the index of the current tab.

        `set_current_tab(tab: str | int) -> None`:
            Set the current tab by name or index.

    Examples
    --------
        To add a PyFlameTabWidget to a window:
        ```
            # Create Main Window
            self.window = PyFlameWindow(
                title='Some Script',
                grid_layout_columns=7,
                grid_layout_rows=20,
                parent=None,
                )

            # Create Tab Widget
            self.tabs = PyFlameTabWidget(
                tab_names=[
                    'Tab 1',
                    'Tab 2',
                    'Tab 3',
                    'Tab 4',
                    ],
                grid_layout_columns=7,
                grid_layout_rows=20,
                grid_layout_adjust_column_widths={
                    3: 50,
                    }
                )

            # Add Tab Widget to Main Window
            self.window.grid_layout.addWidget(self.tabs, 0, 0, 20, 7)
        ```

        To add a widget to a tab:
        ```
        tab_widget.tab_pages['Tab 1'].grid_layout.addWidget(menu_label, 0, 0)
        ```

        To add a tab to an existing tab widget:
        ```
        tab_widget.add_tab('Tab 4')
        ```
    """

    class TabContainer:
        def __init__(self, name: str, parent_tab_widget: 'PyFlameTabWidget'):
            self.widget = QtWidgets.QWidget()

            # Tab Colntainer Settings
            self.widget.setFocusPolicy(QtCore.Qt.NoFocus)

            # Tab Container Properties
            self.widget.enabled = parent_tab_widget.enabled
            self.widget.tab_label_width = parent_tab_widget.tab_label_width
            self.widget.tab_label_height = parent_tab_widget.tab_label_height

            # Inherit layout settings from parent tab widget
            self.grid_layout = PyFlameGridLayout(
                columns=parent_tab_widget.grid_layout_columns,
                rows=parent_tab_widget.grid_layout_rows,
                column_width=parent_tab_widget.grid_layout_column_width,
                row_height=parent_tab_widget.grid_layout_row_height,
                adjust_column_widths=parent_tab_widget.grid_layout_adjust_column_widths,
                adjust_row_heights=parent_tab_widget.grid_layout_adjust_row_heights,
                )

            # Set Layout
            self.widget.setLayout(self.grid_layout)
            parent_tab_widget.addTab(self.widget, name)

        @property
        def enabled(self) -> bool:
            """
            Enable
            ======

            Get or set the enable state of the tab widget.

            Returns
            -------
                bool:
                    The enable state of the tab widget.

            Set
            ---
                value (bool):
                    The enable state of the tab widget.

            Raises
            ------
                TypeError:
                    If the value is not a boolean.

            Examples
            --------
                ```
                # Get the enable state of the tab widget
                tab_widget.enabled

                # Set the enable state of the tab widget
                tab_widget.enabled = True
                ```
            """

            return self.widget.isEnabled()

        @enabled.setter
        def enabled(self, value: bool) -> None:
            """
            Enable
            ======

            Set the enable state of the tab widget.
            """

            # Validate Argument
            if not isinstance(value, bool):
                pyflame.raise_type_error('PyFlameTabWidget', 'enabled', 'bool', value)

            # Set Enabled State
            self.widget.setEnabled(value)

    def __init__(self,
                 tab_names: list[str] = [],
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: dict[int, int]={},
                 grid_layout_adjust_row_heights: dict[int, int]={},
                 tab_label_width: int=150,
                 tab_label_height: int=28,
                 enabled: bool=True,
                 parent: QtWidgets.QWidget | None=None):
        super().__init__(parent)

        # Tab settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.tab_label_width = pyflame.gui_resize(tab_label_width)
        self.tab_label_height = pyflame.gui_resize(tab_label_height)

        # Set size policy to Expanding so the tab widget fills available space
        # This allows it to properly expand when added with rowSpan/columnSpan
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Tab Properties
        self.grid_layout_columns = grid_layout_columns
        self.grid_layout_rows = grid_layout_rows
        self.grid_layout_column_width = grid_layout_column_width
        self.grid_layout_row_height = grid_layout_row_height
        self.grid_layout_adjust_column_widths = grid_layout_adjust_column_widths
        self.grid_layout_adjust_row_heights = grid_layout_adjust_row_heights
        self.enabled = enabled

        # Create tab containers
        self.tab_pages: dict[str, PyFlameTabWidget.TabContainer] = {}
        self.tab_names = tab_names

        # Set stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def tab_names(self) -> list[str]:
        """
        Tab Names
        =========

        Get or set the names of the tabs in the tab widget.

        Returns
        -------
            `list[str]`:
                The names of the tabs.

        Set
        ---
            `value` (list[str]):
                The names of the tabs to set.


        Raises
        ------
            TypeError:
                If the `value` is not a list of strings.

        Examples
        --------
            ```
            # Get the names of the tabs
            tab_names = tab_widget.tab_names

            # Set the names of the tabs
            tab_widget.tab_names = ['Tab 1', 'Tab 2', 'Tab 3']
            ```
        """

        return list(self.tab_pages.keys())

    @tab_names.setter
    def tab_names(self, value: list[str]) -> None:
        """
        Tab Names
        =========

        Set the names of the tabs in the tab widget.
        """

        # Validate Argument
        if not isinstance(value, list):
            pyflame.raise_type_error('PyFlameTabWidget', 'tab_names', 'list', value)
        for name in value:
            if not isinstance(name, str):
                pyflame.raise_type_error('PyFlameTabWidget.tab_names', 'value', 'list of strings', value)

        # Set the names of the tabs
        for name in value:
            self.add_tab(name)

    @property
    def grid_layout_columns(self) -> int:
        """
        Grid Layout Columns
        ===================

        Get or set the number of columns in the grid layout.

        Returns
        -------
            `int`:
                The number of columns in the grid layout.

        Set
        ---
            `value` (int):
                The number of columns in the grid layout.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the number of columns in the grid layout
            grid_layout_columns = tab_widget.grid_layout_columns

            # Set the number of columns in the grid layout
            tab_widget.grid_layout_columns = 6
            ```
        """

        return self._grid_layout_columns

    @grid_layout_columns.setter
    def grid_layout_columns(self, value: int) -> None:
        """
        Grid Layout Columns
        ===================

        Set the number of columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_columns', 'int', value)

        self._grid_layout_columns = value

    @property
    def grid_layout_rows(self) -> int:
        """
        Grid Layout Rows
        ================

        Get or set the number of rows in the grid layout.

        Returns
        -------
            `int`:
                The number of rows in the grid layout.

        Set
        ---
            `value` (int):
                The number of rows in the grid layout.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the number of rows in the grid layout
            grid_layout_rows = tab_widget.grid_layout_rows

            # Set the number of rows in the grid layout
            tab_widget.grid_layout_rows = 6
            ```
        """

        return self._grid_layout_rows

    @grid_layout_rows.setter
    def grid_layout_rows(self, value: int) -> None:
        """
        Grid Layout Rows
        ================

        Set the number of rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_rows', 'int', value)

        # Set the number of rows in the grid layout
        self._grid_layout_rows = value

    @property
    def grid_layout_column_width(self) -> int:
        """
        Grid Layout Column Width
        =========================

        Get or set the width of the columns in the grid layout.

        Returns
        -------
            `int`:
                The width of the columns in the grid layout.

        Set
        ---
            `value` (int):
                The width of the columns in the grid layout.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the width of the columns in the grid layout
            grid_layout_column_width = tab_widget.grid_layout_column_width

            # Set the width of the columns in the grid layout
            tab_widget.grid_layout_column_width = 100
            ```
        """

        return self._grid_layout_column_width

    @grid_layout_column_width.setter
    def grid_layout_column_width(self, value: int) -> None:
        """
        Grid Layout Column Width
        =========================

        Set the width of the columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_column_width', 'int', value)

        self._grid_layout_column_width = value

    @property
    def grid_layout_row_height(self) -> int:
        """
        Grid Layout Row Height
        ======================

        Get or set the height of the rows in the grid layout.

        Returns
        -------
            `int`:
                The height of the rows in the grid layout.

        Set
        ---
            `value` (int):
                The height of the rows in the grid layout.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the height of the rows in the grid layout
            grid_layout_row_height = tab_widget.grid_layout_row_height

            # Set the height of the rows in the grid layout
            tab_widget.grid_layout_row_height = 100
            ```
        """

        return self._grid_layout_row_height

    @grid_layout_row_height.setter
    def grid_layout_row_height(self, value: int) -> None:
        """
        Grid Layout Row Height
        ======================

        Set the height of the rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_row_height', 'int', value)

        self._grid_layout_row_height = value

    @property
    def grid_layout_adjust_column_widths(self) -> dict[int, int]:
        """
        Grid Layout Adjust Column Widths
        ================================

        Get or set the widths of specific columns in the grid layout.

        Returns
        -------
            `dict[int, int]`:
                The widths of the columns in the grid layout.

        Set
        ---
            `value` (dict[int, int]):
                The widths of the columns in the grid layout.

        Raises
        ------
            TypeError:
                If the `value` is not a dictionary of integers and integers.

        Examples
        --------
            ```
            # Get the adjusted widths of the columns in the grid layout
            grid_layout_adjust_column_widths = tab_widget.grid_layout_adjust_column_widths

            # Set the adjusted widths of the columns in the grid layout
            tab_widget.grid_layout_adjust_column_widths = {1: 100, 2: 200}
            ```
        """

        return self._grid_layout_adjust_column_widths

    @grid_layout_adjust_column_widths.setter
    def grid_layout_adjust_column_widths(self, value: dict[int, int]) -> None:
        """
        Grid Layout Adjust Column Widths
        ================================

        Set the widths of the columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_adjust_column_widths', 'dict', value)

        self._grid_layout_adjust_column_widths = value

    @property
    def grid_layout_adjust_row_heights(self) -> dict[int, int]:
        """
        Grid Layout Adjust Row Heights
        ==============================

        Get or set the heights of specific rows in the grid layout.

        Returns
        -------
            `dict[int, int]`:
                The heights of the rows in the grid layout.

        Set
        ---
            `value` (dict[int, int]):
                The heights of the rows in the grid layout.

        Raises
        ------
            TypeError:
                If the value is not a dictionary of integers and integers.

        Examples
        --------
            ```
            # Get the adjusted heights of the rows in the grid layout
            grid_layout_adjust_row_heights = tab_widget.grid_layout_adjust_row_heights

            # Set the adjusted heights of the rows in the grid layout
            tab_widget.grid_layout_adjust_row_heights = {1: 100, 2: 200}
            ```
        """

        return self._grid_layout_adjust_row_heights

    @grid_layout_adjust_row_heights.setter
    def grid_layout_adjust_row_heights(self, value: dict[int, int]) -> None:
        """
        Grid Layout Adjust Row Heights
        ==============================

        Set the adjusted heights of the rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameTabWidget', 'grid_layout_adjust_row_heights', 'dict', value)

        self._grid_layout_adjust_row_heights = value

    @property
    def tab_label_width(self) -> int:
        """
        Tab Label Width
        ===============

        Get or set the width of the tab labels.

        Returns
        -------
            `int`:
                The width of the tab labels.

        Set
        ---
            `value` (int):
                The width of the tab labels.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the width of the tab labels
            tab_label_width = tab_widget.tab_label_width

            # Set the width of the tab labels
            tab_widget.tab_label_width = 100
            ```
        """

        return self._tab_label_width

    @tab_label_width.setter
    def tab_label_width(self, value: int) -> None:
        """
        Tab Label Width
        ===============

        Set the width of the tab labels.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'tab_label_width', 'int', value)

        self._tab_label_width = value

    @property
    def tab_label_height(self) -> int:
        """
        Tab Label Height
        ================

        Get or set the height of the tab labels.

        Returns
        -------
            `int`:
                The height of the tab labels.

        Set
        ---
            `value` (int):
                The height of the tab labels.

        Raises
        ------
            TypeError:
                If the `value` is not an integer.

        Examples
        --------
            ```
            # Get the height of the tab labels
            tab_label_height = tab_widget.tab_label_height

            # Set the height of the tab labels
            tab_widget.tab_label_height = 100
            ```
        """

        return self._tab_label_height

    @tab_label_height.setter
    def tab_label_height(self, value: int) -> None:
        """
        Tab Label Height
        ================

        Set the height of the tab labels.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTabWidget', 'tab_label_height', 'int', value)

        # Set the height of the tab labels
        self._tab_label_height = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def add_tab(self, name: str) -> 'PyFlameTabWidget.TabContainer':
        """
        Add Tab
        =======

        Add a tab to the tab widget.

        Will not add a tab if a tab with the same name already exists.

        Args
        ----
            `name` (str):
                The name of the tab to add.

        Returns
        -------
            `PyFlameTabWidget.TabContainer`:
                The tab container object.
        """

        # Validate Argument
        if not isinstance(name, str):
            pyflame.raise_type_error('PyFlameTabWidget.add_tab', 'name', 'str', name)

        # Don't add it again if it already exists
        if name in self.tab_pages:
            return self.tab_pages[name]

        # Add tab
        container = self.TabContainer(name, self)
        self.tab_pages[name] = container
        return container

    def get_current_tab_name(self) -> str | None:
        """
        Get Current Tab Name
        ====================

        Returns
        -------
            `str | None`:
                The name (label) of the currently selected tab, | None if no tab is selected.
        """

        index = self.currentIndex()
        if index != -1:
            return self.tabText(index)
        return None

    def get_current_tab_index(self) -> int:
        """
        Get Current Tab Index
        =====================

        Get the index of the current tab

        Returns
        -------
            `int`:
                The index of the current tab
        """

        return self.currentIndex()

    def set_current_tab(self, tab: str | int) -> None:
        """
        Set Current Tab
        ===============

        Set the current tab by name or index

        Args
        ----
            `tab` (str | int):
                The name or index of the tab to set as current
        """

        # Validate Argument
        if not isinstance(tab, (str | int)):
            pyflame.raise_type_error('PyFlameTabWidget.set_current_tab', 'tab', 'str | int', tab)

        if isinstance(tab, str):
            if tab not in self.tab_pages:
                raise ValueError(f"Tab name '{tab}' does not exist.")
            self.setCurrentIndex(self.indexOf(self.tab_pages[tab].widget))
        elif isinstance(tab, int):
            if tab < 0 or tab >= self.count():
                raise IndexError(f"Tab index {tab} is out of range.")
            self.setCurrentIndex(tab)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============
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
                width: {self.tab_label_width}px;
                height: {self.tab_label_height}px;
                padding: {pyflame.gui_resize(2)}px;
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
            QTabBar::tab:!enabled{{
                color: {Color.TEXT_DISABLED.value};
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

    Args
    ----
        `text` (str):
            Text displayed in widget.
            (Default: `""`)

        `text_type` (TextType, optional):
            Type of text being input.
            Options:
                `TextType.PLAIN`: Plain text.
                `TextType.MARKDOWN`: Markdown text.
                `TextType.HTML`: HTML text.
            (Default: `TextType.PLAIN`)

        `text_style` (TextStyle, optional):
            Text style.
            Options:
                `TextStyle.EDITABLE`: Editable text.
                `TextStyle.READ_ONLY`: Read only text.
                `TextStyle.READ_ONLY_SELECTABLE`: Read only text that is selectable.
                `TextStyle.UNSELECTABLE`: Unselectable text.
            (Default: `TextStyle.EDITABLE`)

        `enabled` (bool, optional):
            Whether the text edit widget is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the text edit widget in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the text edit widget in pixels. If `None`, it expands to fit the layout. Minimum height is 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set text displayed in widget. Text is returned as the same type as the text_type property. To get the text as a plain text string, use the text_str property.
            (Default: `""`)

        `text_str` (str):
            Returns text as a plain text string.

        `text_type` (TextType):
            Get or set text type.
            (Default: `TextType.PLAIN`)

        `text_style` (TextStyle):
            Get or set text style.
            (Default: `TextStyle.EDITABLE`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Methods
    -------
        `set_focus()`:
            Sets focus to the TextEdit.

    Examples
    --------
        To create a PyFlameTextEdit:
        ```
        text_edit = PyFlameTextEdit(
            text='Some text here',
            )
        ```

        To set or get any text edit property:
        ```
        # Set property
        text_edit.text = 'Some text here'

        # Get property
        print(text_edit.text)
        ```
    """

    def __init__(self: 'PyFlameTextEdit',
                 text: str='',
                 text_type: TextType=TextType.PLAIN,
                 text_style: TextStyle=TextStyle.EDITABLE,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Widget Settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.text_type = text_type
        self.text = text
        self.text_style = text_style
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text_type(self) -> TextType:
        """
        Text Type
        =========

        Get or set the text edit text type. Uses TextType enum.

        Text Type Options:
        -----------------
            `TextType.PLAIN`: Plain text.
            `TextType.MARKDOWN`: Markdown text.
            `TextType.HTML`: HTML text.

        Returns
        -------
            TextType:
                The text type of the text edit.

        Set
        ---
            `value` (TextType):
                The text type to set for the text edit.

        Raises
        ------
            TypeError:
                If the provided `value` is not a TextType enum.

        Examples
        --------
            ```
            # Get text edit text type
            print(text_edit.text_type)

            # Set text edit text type
            text_edit.text_type = TextType.MARKDOWN
            ```
        """

        return self._text_type

    @text_type.setter
    def text_type(self, value: TextType):
        """
        Text Type
        =========

        Set the text type. Uses TextType enum.

        Text Type Options:
        -----------------
            `TextType.PLAIN`: Plain text.
            `TextType.MARKDOWN`: Markdown text.
            `TextType.HTML`: HTML text.
        """

        if not isinstance(value, TextType):
            pyflame.raise_type_error('PyFlameTextEdit', 'text_type', 'TextType', value)

        self._text_type = value

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set text edit text.

        Text is returned as the same type as the text_type property.
        To get the text as a plain text string no matter what text type is set, use the text_str property.

        Returns
        -------
            str:
                The text of the text edit.

        Set
        ---
            `value` (str):
                The text to set for the text edit.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get text edit text
            print(text_edit.text)

            # Set text edit text
            text_edit.text = 'Some text here'
            ```
        """

        if self.text_type == TextType.PLAIN:
            return self.toPlainText()
        elif self.text_type == TextType.MARKDOWN:
            return self.toMarkdown()
        elif self.text_type == TextType.HTML:
            return self.toHtml()
        return self.toPlainText()

    @text.setter
    def text(self, value: str):
        """
        Text
        ====

        Set text edit text.

        Text is set as the same type as the text_type property.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextEdit', 'text', 'str', value)

        self.clear()

        if self.text_type == TextType.PLAIN:
            self.setPlainText(value)
        elif self.text_type == TextType.MARKDOWN:
            self.setMarkdown(value)
        elif self.text_type == TextType.HTML:
            self.setHtml(value)

    @property
    def text_str(self) -> str:
        """
        Text String
        ===========

        Set or get text as a plain text string no matter what text type is set.

        Returns
        -------
            str:
                The text of the text edit as a plain text string.

        Set
        ---
            `value` (str):
                The text to set for the text edit as a plain text string.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get text edit text as a plain text string
            print(text_browser.text_str)

            # Set text edit text as a plain text string
            text_browser.text_str = 'Some text here'
            ```
        """

        return self.toPlainText()

    @text_str.setter
    def text_str(self, value: str):
        """
        Text String
        ===========

        Set text edit text as a plain text string no matter what text type is set.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextEdit', 'text_str', 'str', value)

        self.text = str(value)

    @property
    def text_style(self) -> TextStyle:
        """
        Text Style
        ==========

        Get or set the text edit text style. Uses TextStyle enum.

        Text Style Options
            `TextStyle.EDITABLE`: Editable text.
            `TextStyle.READ_ONLY`: Read only text.
            `TextStyle.READ_ONLY_SELECTABLE`: Read only text that is selectable.
            `TextStyle.UNSELECTABLE`: Unselectable text.

        Returns
        -------
            TextStyle:
                The text style of the text edit.

        Set
        ---
            `value` (TextStyle):
                The text style to set for the text edit.

        Raises
        ------
            TypeError:
                If the provided `value` is not a TextStyle enum.

        Examples
        --------
            ```
            # Get text edit text style
            print(text_exit.text_style)

            # Set text edit text style
            text_edit.text_style = TextStyle.READ_ONLY
            ```
        """

        return self._text_style

    @text_style.setter
    def text_style(self, value: TextStyle):
        """
        Text Style
        ==========

        Set the text edit text style. Uses TextStyle enum.
        """

        if not isinstance(value, TextStyle):
            pyflame.raise_type_error('PyFlameTextEdit', 'text_style', 'TextStyle', value)

        self._text_style = value

        if self._text_style == TextStyle.EDITABLE:
            self.setReadOnly(False)
            self.setTextInteractionFlags(QtCore.Qt.TextEditorInteraction)
        elif self._text_style in (TextStyle.READ_ONLY, TextStyle.READ_ONLY_SELECTABLE):
            self.setReadOnly(True)
            self.setTextInteractionFlags(
                QtCore.Qt.TextSelectableByMouse | QtCore.Qt.TextSelectableByKeyboard
            )
        elif self._text_style == TextStyle.UNSELECTABLE:
            self.setReadOnly(True)
            self.setTextInteractionFlags(QtCore.Qt.NoTextInteraction)

        self._set_stylesheet()

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set text edit enabled state.

        Returns
        -------
            bool: `True` if the text edit is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get text edit enabled state
            print(text_edit.enabled)

            # Set text edit enabled state
            text_edit.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the text edit.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTextEdit', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the text edit width.

        Returns
        -------
            `int`:
                The current width of the text edit in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the text edit expands to fit the maximum width set by the layout.
                If an integer, the text edit is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(text_browser.width)

            # Set a fixed width
            text_browser.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set text edit width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextEdit', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the text edit height.

        Returns
        -------
            `int`:
                The set height of the text edit in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the text edit uses the default height of 28.
                If an integer, the text edit is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get text edit height
            print(text_edit.height)

            # Set text edit height
            text_edit.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set text edit height.
        """

        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextEdit', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)
        else:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set text edit tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the text edit.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the text edit.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get text edit tooltip
            print(text_edit.tooltip)

            # Set text edit tooltip
            text_edit.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the text edit.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextEdit', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(text_browser.tooltip_delay)

            # Set tooltip delay
            text_browser.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextEdit', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(text_browser.tooltip_duration)

            # Set tooltip duration
            text_browser.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextEdit', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def set_focus(self) -> None:
        """
        Set Focus
        =========

        Set widget focus to the entry widget.
        """

        self.setFocus()

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============
        """

        if self.text_style == TextStyle.READ_ONLY or self.text_style == TextStyle.READ_ONLY_SELECTABLE:
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

        elif self.text_style == TextStyle.UNSELECTABLE:
            self.setStyleSheet(f"""
                QTextEdit{{
                    color: {Color.TEXT.value};
                    border: none;
                    padding-left: 1px;
                    }}
                """)
        elif self.text_style == TextStyle.EDITABLE:
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

    #-------------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameTextBrowser(QtWidgets.QTextBrowser):
    """
    PyFlameTextBrowser
    ==================

    Custom QT Flame Text Browser Widget Subclass

    Args
    ----
        `text` (str):
            Text displayed in widget.
            (Default: `""`)

        `text_type` (TextType, optional):
            Type of text being input.
            Options:
                `TextType.PLAIN`: Plain text.
                `TextType.MARKDOWN`: Markdown text.
                `TextType.HTML`: HTML text.
            (Default: `TextType.PLAIN`)

        `text_style` (TextStyle, optional):
            Text style.
            Options:
                `TextStyle.EDITABLE`: Editable text.
                `TextStyle.READ_ONLY`: Read only text.
                `TextStyle.UNSELECTABLE`: Unselectable text.
            (Default: `TextStyle.EDITABLE`)

        `open_external_links` (bool, optional):
            Whether the text browser opens external links in an external browser.
            (Default: `True`)

        `enabled` (bool, optional):
            Whether the text browser widget is enabled.
            (Default: `True`)

        `width` (int, optional):
            Width of the text browser widget in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the text browser widget in pixels. If `None`, it expands to fit the layout. Minimum height is 28.
            (Default: `None`)

        `tooltip` (str, optional):
            Tooltip text shown on hover.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Delay in seconds before the tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Duration in seconds the tooltip remains visible.
            (Default: `5`)

    Properties
    ----------
        `text` (str):
            Get or set text displayed in widget. Text is returned as the same type as the text_type property. To get the text as a plain text string, use the text_str property.
            (Default: `""`)

        `text_str` (str):
            Get text as a plain text string.

        `text_type` (TextType):
            Get or set text type.
            (Default: `TextType.PLAIN`)

        `text_style` (TextStyle):
            Get or set text style.
            (Default: `TextStyle.EDITABLE`)

        `open_external_links` (bool):
            Get or set whether the text browser should open external links in an external browser.
            (Default: `True`)

        `enabled` (bool):
            Get or set whether the widget is enabled.
            (Default: `True`)

        `width` (int | None):
            Get or set the widget width.
            (Default: `None`)

        `height` (int | None):
            Get or set the widget height.
            (Default: `None`)

        `tooltip` (str | None):
            Get or set the tooltip text.
            (Default: `None`)

        `tooltip_delay` (int):
            Get or set the tooltip delay in seconds.
            (Default: `3`)

        `tooltip_duration` (int):
            Get or set the tooltip duration in seconds.
            (Default: `5`)

    Examples
    --------
        To create a PyFlameTextBrowser:
        ```
        text_browser = PyFlameTextBrowser(
            text='Some text here',
            )
        ```

        To set or get any text browser property:
        ```
        # Set property
        text_browser.text = 'Some text here'

        # Get property
        print(text_browser.text)
        ```
    """

    def __init__(self: 'PyFlameTextBrowser',
                 text: str='',
                 text_type: TextType=TextType.PLAIN,
                 text_style: TextStyle=TextStyle.EDITABLE,
                 open_external_links: bool=True,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # Widget Settings
        self.setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.text_type = text_type
        self.text = text
        self.text_style = text_style
        self.open_external_links = open_external_links
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text_type(self) -> TextType:
        """
        Text Type
        =========

        Get or set the text browser text type. Uses TextType enum.

        Text Type Options:
        -----------------
            `TextType.PLAIN`: Plain text.
            `TextType.MARKDOWN`: Markdown text.
            `TextType.HTML`: HTML text.

        Returns
        -------
            TextType:
                The text type of the text browser.

        Set
        ---
            `value` (TextType):
                The text type to set for the text browser.

        Raises
        ------
            TypeError:
                If the provided `value` is not a TextType enum.

        Examples
        --------
            ```
            # Get text browser text type
            print(text_browser.text_type)

            # Set text browser text type
            text_browser.text_type = TextType.MARKDOWN
            ```
        """

        return self._text_type

    @text_type.setter
    def text_type(self, value: TextType):
        """
        Text Type
        =========

        Set the text type. Uses TextType enum.

        Text Type Options:
        -----------------
            `TextType.PLAIN`: Plain text.
            `TextType.MARKDOWN`: Markdown text.
            `TextType.HTML`: HTML text.
        """

        if not isinstance(value, TextType):
            pyflame.raise_type_error('PyFlameTextBrowser', 'text_type', 'TextType', value)

        self._text_type = value

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set text browser text.

        Text is returned as the same type as the text_type property.
        To get the text as a plain text string no matter what text type is set, use the text_str property.

        Returns
        -------
            str:
                The text of the text browser.

        Set
        ---
            `value` (str):
                The text to set for the text browser.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get text browser text
            print(text_browser.text)

            # Set text browser text
            text_browser.text = 'Some text here'
            ```
        """

        if self.text_type == TextType.PLAIN:
            return self.toPlainText()
        elif self.text_type == TextType.MARKDOWN:
            return self.toMarkdown()
        elif self.text_type == TextType.HTML:
            return self.toHtml()
        return self.toPlainText()

    @text.setter
    def text(self, value: str):
        """
        Text
        ====

        Set text browser text.

        Text is set as the same type as the text_type property.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextBrowser', 'text', 'str', value)

        if self.text_type == TextType.PLAIN:
            self.setPlainText(value)
        elif self.text_type == TextType.MARKDOWN:
            self.setMarkdown(value)
        elif self.text_type == TextType.HTML:
            self.setHtml(value)

    @property
    def text_str(self) -> str:
        """
        Text String
        ===========

        Set or get text as a plain text string no matter what text type is set.

        Returns
        -------
            str:
                The text of the text browser as a plain text string.

        Set
        ---
            `value` (str):
                The text to set for the text browser as a plain text string.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get text browser text as a plain text string
            print(text_browser.text_str)

            # Set text browser text as a plain text string
            text_browser.text_str = 'Some text here'
            ```
        """

        return self.toPlainText()

    @text_str.setter
    def text_str(self, value: str):
        """
        Text String
        ===========

        Set text browser text as a plain text string no matter what text type is set.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextBrowser', 'text_str', 'str', value)

        self.text = str(value)

    @property
    def text_style(self) -> TextStyle:
        """
        Text Style
        ==========

        Get or set the text browser text style. Uses TextStyle enum.

        Text Style Options
            `TextStyle.EDITABLE`: Editable text.
            `TextStyle.READ_ONLY`: Read only text.
            `TextStyle.UNSELECTABLE`: Unselectable text.

        Returns
        -------
            TextStyle:
                The text style of the text browser.

        Set
        ---
            `value` (TextStyle):
                The text style to set for the text browser.

        Raises
        ------
            TypeError:
                If the provided `value` is not a TextStyle enum.

        Examples
        --------
            ```
            # Get text browser text style
            print(text_browser.text_style)

            # Set text browser text style
            text_browser.text_style = TextStyle.READ_ONLY
            ```
        """

        return self._text_style

    @text_style.setter
    def text_style(self, value: TextStyle):
        """
        Text Style
        ==========

        Set the text browser text style. Uses TextStyle enum.
        """

        if not isinstance(value, TextStyle):
            pyflame.raise_type_error('PyFlameTextBrowser', 'text_style', 'TextStyle', value)

        self._text_style = value
        self._set_stylesheet()

    @property
    def open_external_links(self) -> bool:
        """
        Open External Links
        ===================

        Get or set whether the text browser should open external links in an external browser.

        Returns
        -------
            bool: `True` if the text browser should open external links in an external browser, `False` if not.

        Set
        ---
            `value` (bool):
                True to open external links in an external browser, False to not open external links in an external browser.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get text browser open external links state
            print(text_browser.open_external_links)

            # Set text browser open external links state
            text_browser.open_external_links = False
            ```
        """

        return self._open_external_links

    @open_external_links.setter
    def open_external_links(self, value: bool):
        """
        Open External Links
        ===================

        Set whether the text browser should open external links in an external browser.
        """

        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTextBrowser', 'open_external_links', 'bool', value)

        self._open_external_links = value
        self.setOpenExternalLinks(value)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set text browser enabled state.

        Returns
        -------
            bool: `True` if the text browser is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get text browser enabled state
            print(text_browser.enabled)

            # Set text browser enabled state
            text_browser.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the text browser.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTextBrowser', 'enabled', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the text browser width.

        Returns
        -------
            `int`:
                The current width of the text browser in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the text browser expands to fit the maximum width set by the layout.
                If an integer, the text browser is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(text_browser.width)

            # Set a fixed width
            text_browser.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set text browser width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextBrowser', 'width', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the text browser height.

        Returns
        -------
            `int`:
                The set height of the text browser in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the text browser uses the default height of 28.
                If an integer, the text browser is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get text browser height
            print(text_browser.height)

            # Set text browser height
            text_browser.height = 40
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set text browser height.
        """

        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextBrowser', 'height', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)
        else:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set text browser tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the text browser.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the text browser.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get text browser tooltip
            print(text_browser.tooltip)

            # Set text browser tooltip
            text_browser.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the text browser.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTextBrowser', 'tooltip', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(text_browser.tooltip_delay)

            # Set tooltip delay
            text_browser.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextBrowser', 'tooltip_delay', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(text_browser.tooltip_duration)

            # Set tooltip duration
            text_browser.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTextBrowser', 'tooltip_duration', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self):
        """
        Set Stylesheet
        ==============
        """

        if self.text_style == TextStyle.READ_ONLY:
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

        elif self.text_style == TextStyle.UNSELECTABLE:
            self.setStyleSheet(f"""
                QTextEdit{{
                    color: {Color.TEXT.value};
                    border: none;
                    padding-left: 1px;
                    }}
                """)
        elif self.text_style == TextStyle.EDITABLE:
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

    #-------------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

class PyFlameTreeWidget(QtWidgets.QTreeWidget):
    """
    PyFlameTreeWidget
    =================

    Custom QT Flame Tree Widget Subclass

    Args
    ----
        `column_names` (list[str]):
            List of names to be used for column names in tree.

        `sort` (bool, optional):
            Whether to enable sorting in the tree widget.
            (Default: `False`)

        `tree_dict` (Dict[str, Dict[str, str]], optional):
            Dictionary of items to populate the tree widget. Useful when dealing with folder trees.
            (Default: `None`)

        `tree_list` (List[str], optional):
            List of items to populate the tree widget. Useful when dealing with batch group schematic reels shelf reels
            and desktop reels.
            (Default: `None`)

        `connect` (callable, optional):
            Function to call when item in tree is clicked on.
            (Default: `None`)

        `update_connect` (callable, optional):
            Function to call when an item is edited, inserted, or deleted.
            (Default: `None`)

        `allow_children` (bool, optional):
            Whether to allow children in the tree.
            (Default: `True`)

        `min_items` (int, optional):
            Minimum number of items that must remain in the tree.
            (Default: `1`)

        `alternating_row_colors` (bool, optional):
            Whether to enable alternating row colors.
            (Default: `True`)

        `enabled` (bool, optional):
            Set to True to enable the tree widget.
            (Default: `True`)

        `width` (int, optional):
            PyFlameTreeWidget width.
            If `None`, the tree widget expands to fit the maximum width set by the layout. Minimum width is 25.
            If an integer, the tree widget is given a fixed width.
            (Default: `None`)

        `height` (int, optional):
            PyFlameTreeWidget height.
            If `None`, the tree widget expands to fit the maximum height set by the layout. Minimum height is 28.
            If an integer, the tree widget is given a fixed height.
            (Default: `None`)

        `tooltip` (str, optional):
            PyFlameTreeWidget tooltip text.
            (Default: `None`)

        `tooltip_delay` (int, optional):
            Tooltip delay in seconds. Delay before tooltip is shown.
            (Default: `3`)

        `tooltip_duration` (int, optional):
            Tooltip duration in seconds. Duration tooltip is shown.
            (Default: `5`)

    Properties
    ----------
        `column_names` (List):
            A list of all column names in the tree.

        `sort` (bool):
            Whether to enable sorting in the tree widget.

        `tree_dict` (Dict[str, Dict]):
            A nested dictionary representing the tree structure. Useful when dealing with folder trees.

        `tree_list` (List[str]):
            A list of all item names in the tree. Useful when dealing with batch group schematic reels shelf reels and
            desktop reels.

        `tree_list_no_root` (List[str]):
            A list of all item names in the tree excluding the root item. Useful when dealing with batch group
            schematic reels shelf reels and desktop reels.

        `connect_callback` (Callable):
            A callback function that is called when an item is clicked.

        `update_connect_callback` (Callable):
            A callback function that is called when an item is updated.

        `top_level_item` (str):
            The top level item of the tree.

        `top_level_editable` (bool):
            Whether the top level item is editable.

        `allow_children` (bool):
            Whether children are allowed to be added to the tree.

        `min_items` (int):
            The minimum number of items that must be present in the tree.

        `enabled` (bool):
            Whether the tree widget is currently enabled.

        `width` (None | int):
            Width of tree widget in pixels.

        `height` (None | int):
            Height of tree widget in pixels.

        `tooltip` (None | str):
            Tooltip text shown on hover.

        `tooltip_delay` (int):
            Delay in seconds before the tooltip is shown.

        `tooltip_duration` (int):
            Duration in seconds the tooltip is shown.

        `all_item_paths` (List[str]):
            Get the recursive paths of all items in the tree.

        `all_item_paths_no_root` (List[str]):
            Get the recursive paths of all items in the tree excluding the root item.

        `item_path` (str):
            Get the recursive path of the currently selected item.

        `item_paths` (List[str]):
            Get the recursive paths of all selected items.

        `selected_item` (str):
            Get the name of the currently selected item.

    Methods
    -------
        `fill_tree_dict(tree_dict: Dict[str, Dict[str, str]], editable: bool=False)`:
            Fill the PyFlameTreeWidget with the provided dictionary.

        `fill_tree_list(tree_list: List[str])`:
            Fill the PyFlameTreeWidget with the provided list.

        `add_item(item_name: str)`:
            Add a new item as a child of the currently selected item in the tree, or as a child of the top-level item if no item is selected.

        `add_item_with_columns(item_name: str, column_entries: List[str])`:
            Add a new item to a tree with tree column entries.

        `delete_item()`:
            Delete the selected item in the PyFlameTreeWidget.
            Does not delete if the item is the top-level item or if the total number of items under the top-level item would drop below
            the minimum required that is set by the min_items argument.

        `sort_items()`:
            Sort all items in the tree while maintaining the structure and keeping the tree expanded.

        `color_item(item: QTreeWidgetItem, color: QColor)`:
            Color item in tree with supplied QColor value.

        `clear()`:
            Clear all items from the PyFlameTreeWidget.

        `update()`:
            Update the tree using the update_connect callback.

    Examples
    --------
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
            sort=True,
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
            sort=True,
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
                 sort: bool=False,
                 tree_dict: Dict[str, Dict[str, str]]={},
                 tree_list: List[str]=[],
                 top_level_item: str | None=None,
                 connect: Callable[..., None] | None=None,
                 update_connect: Callable[..., None] | None=None,
                 top_level_editable: bool=False,
                 allow_children: bool=True,
                 min_items: int=1,
                 alternating_row_colors: bool=True,
                 elide_text: bool=False,
                 enabled: bool=True,
                 width: int | None=None,
                 height: int | None=None,
                 tooltip: str | None=None,
                 tooltip_delay: int=3,
                 tooltip_duration: int=5,
                 ) -> None:
        super().__init__()

        # TreeWidget Settings
        self.setFont(FONT)
        self.header().setFont(FONT)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.itemCollapsed.connect(self._on_item_collapsed)  # Prevent top-level item from collapsing

        # Create Widget Tooltip
        self.tooltip_popup = PyFlameToolTip(parent_widget=self)

        # Set Properties
        self.column_names = column_names
        self.sort = sort
        self.tree_dict = tree_dict
        self.tree_list = tree_list
        self.top_level_editable = top_level_editable
        self.alternating_row_colors = alternating_row_colors
        self.min_items = min_items
        self.allow_children = allow_children
        self.elide_test = elide_text
        self.enabled = enabled
        self.width = width
        self.height = height
        self.tooltip = tooltip
        self.tooltip_delay = tooltip_delay
        self.tooltip_duration = tooltip_duration

        self.connect_callback = connect
        self.update_connect_callback = update_connect
        self.top_level_item = top_level_item


        # Set the first top-level item as the current item
        self.setCurrentItem(self.topLevelItem(0))

        # Set Stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def column_names(self) -> List[str]:
        """
        Column Names
        ============

        Set or get tree widget Column names.

        Returns
        -------
            list:
                List of tree widget column names.

        Set
        ---
            `value` (list):
                List of names to be used as column names

        Raises
        ------
            TypeError:
                If the provided `value` is not a list.

        Examples
        --------
            ```
            # Get list of tree widget column names
            print(tree_widget.column_names)

            # Set tree widget column names
            tree_widget.column_names[
                column_01,
                column_02,
                column_03,
                ]
            ```
        """

        return [self.headerItem().text(i) for i in range(self.columnCount())]

    @column_names.setter
    def column_names(self, value: List[str]) -> None:
        """
        Column Names
        ============

        Set tree widget Column names.
        """

        self.setHeaderLabels(value)
        self.header().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)

    @property
    def sort(self) -> bool:
        """
        Sort
        ====

        Set or get the sorting state of the tree widget.

        Returns
        -------
            bool: `True` if sorting is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get tree widget sorting state
            print(tree_widget.sort)

            # Set tree widget enabled state
            tree_widget.sort = True
            ```
        """

        return self.isSortingEnabled()

    @sort.setter
    def sort(self, value: bool) -> None:
        """
        Sort
        ====

        Set the sorting state of the tree widget.
        """

        # Validate argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget', 'sort', 'bool', value)

        # Set sorting state
        self.setSortingEnabled(value)

        # If sorting, set to ascending order
        if value:
            self.sortItems(0, QtCore.Qt.AscendingOrder)

    @property
    def tree_dict(self) -> Dict[str, Any] | None:
        """
        Tree Dict
        =========

        Get or set the tree dictionary.

        Returns
        -------
            dict:
                The tree dictionary.

        Set
        ---
            `value` (dict):
                The tree dictionary to be set.

        Raises
        ------
            TypeError:
                If the provided `value` is not a dictionary.

        Examples
        --------
            ```
            # Get tree dictionary
            print(tree_widget.tree_dict)

            # Set tree dictionary
            tree_widget.tree_dict = {'Root': {'Child 1': {}, 'Child 2': {}}}
            ```
        """

        def get_tree_path(item):
            """
            Get Tree Path
            =============

            Get the path of a tree item as a string.

            Args
            ----
                `item` (QTreeWidgetItem):
                    The tree item to get the path for.

            Returns
            -------
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

            Args
            -----
                `item` (QTreeWidgetItem, optional):
                    The tree item to start traversal from. Defaults to None.

            Returns
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

    @tree_dict.setter
    def tree_dict(self, value: Dict[str, Any]) -> None:
        """
        Tree Dict
        =========

        Set the tree dictionary.
        """

        # Validate argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameTreeWidget', 'tree_dict', 'dict', value)

        # Fill tree with dictionary
        if value != {}:
            self.fill_tree_dict(value)

    @property
    def top_level_item(self) -> str | None:
        """
        Top Level Item
        ==============

        Get or set the Top Level Item of the Tree when using a List to build the tree.

        Returns
        -------
            str:
                Item to be the top of the tree.

        Set
        ---
            `value` (str):
                Item to be the top of the tree.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get Top Level Item
            print(tree_widget.top_level_item)

            # Set Top Level Item
            tree_widget.top_level_item = 'Some Item'
            ```
        """

        return self._top_level_item

    @top_level_item.setter
    def top_level_item(self, value: str | None) -> None:
        """
        Top Level Item
        ==============

        Set the Top Level Item of the Tree when using a List to build the tree.
        """

        # Validate argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTreeWidget', 'top_level_item', 'str | None', value)

        self._top_level_item = value

    @property
    def tree_list(self) -> List[str] | None:
        """
        Tree List
        =========

        Get or set the List used to build the tree.

        When using a List to build the tree a Top Level Item must also be provided.

        Returns
        -------
            list:
                Items in the tree as a list.

        Set
        ---
            `value` (list):
                The tree list to be set.

        Raises
        ------
            TypeError:
                If the provided `value` is not a list.

        Examples
        --------
            ```
            # Get tree list
            print(tree_widget.tree_list)

            # Set tree list
            tree_widget.tree_list = ['Root', 'Child 1', 'Child 2']
            ```
        """

        # Get the tree list
        item_names = []

        def traverse_item(item: QtWidgets.QTreeWidgetItem) -> None:
            item_names.append(item.text(0))
            for i in range(item.childCount()):
                traverse_item(item.child(i))

        root = self.invisibleRootItem()
        for i in range(root.childCount()):
            traverse_item(root.child(i))

        return item_names

    @tree_list.setter
    def tree_list(self, value: List[str]) -> None:
        """
        Tree List
        =========

        Set the tree list.
        """

        # Validate argument
        if not isinstance(value, list):
            pyflame.raise_type_error('PyFlameTreeWidget', 'tree_list', 'list | None', value)

        # Convert list to dictionary and fill tree
        if value != [] and self.top_level_item is not None:
            self.tree_dict = {self.top_level_item: {str(item): {} for item in value}}

    @property
    def tree_list_no_root(self) -> List[str]:
        """
        Tree List No Root
        =================

        Return the tree list excluding the root item.
        """

        tree_list = self.tree_list
        if tree_list is None:
            return []

        return tree_list[1:]

    @property
    def connect_callback(self) -> Callable[..., None] | None:
        """
        Connect Callback
        ================

        Get or set the callback function to be called when an item is clicked.

        Returns
        -------
            callable:
                The callback function to be called when an item is clicked.

        Set
        ---
            `value` (callable):
                The callback function to be called when an item is clicked.

        Raises
        ------
            TypeError:
                If the provided `value` is not a callable.

        Examples
        --------
            ```
            # Get connect callback
            print(tree_widget.connect_callback)

            # Set connect callback
            tree_widget.connect_callback = lambda: print('Item clicked')
            ```
        """

        return self._connect_callback

    @connect_callback.setter
    def connect_callback(self, value: Callable[..., None] | None) -> None:
        """
        Connect Callback
        ================

        Set the callback function to be called when an item is clicked.
        """

        # Validate argument
        if value is not None and not callable(value):
            pyflame.raise_type_error('PyFlameTreeWidget', 'connect_callback', 'callable | None', value)

        # Set callback
        if value is not None:
            self.clicked.connect(value)

        self._connect_callback = value

    @property
    def update_connect_callback(self) -> Callable[..., None] | None:
        """
        Update Connect Callback
        =======================

        Get or set the callback function to be called when an item is updated.

        Returns
        -------
            callable:
                The callback function to be called when an item is updated.

        Set
        ---
            `value` (callable):
                The callback function to be called when an item is updated.

        Raises
        ------
            TypeError:
                If the provided `value` is not a callable.

        Examples
        --------
            ```
            # Get update connect callback
            print(tree_widget.update_connect_callback)

            # Set update connect callback
            tree_widget.update_connect_callback = lambda: print('Item updated')
            ```
        """

        return self._update_connect_callback

    @update_connect_callback.setter
    def update_connect_callback(self, value: Callable[..., None] | None) -> None:
        """
        Update Connect Callback
        =======================

        Set the callback function to be called when an item is updated.
        """

        # Validate argument
        if value is not None and not callable(value):
            pyflame.raise_type_error('PyFlameTreeWidget', 'update_connect_callback', 'callable | None', value)

        # Set callback
        if value is not None:
            self.itemChanged.connect(value)

        # Set the callback
        self._update_connect_callback = value

    @property
    def alternating_row_colors(self) -> bool:
        """
        Alternating Row Colors
        ======================

        Get or set alternating row colors.

        Returns
        -------
            bool:
                `True` if alternating row colors are enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get alternating row colors
            print(tree_widget.alternating_row_colors)

            # Set alternating row colors
            tree_widget.alternating_row_colors = False
            ```
        """

        return self._alternating_row_colors

    @alternating_row_colors.setter
    def alternating_row_colors(self, value: bool) -> None:
        """
        Alternating Row Colors
        ======================

        Set alternating row colors.
        """

        # Validate argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget', 'alternating_row_colors', 'bool', value)

        # Set alternating row colors
        self._alternating_row_colors = value
        self.setAlternatingRowColors(value)

    @property
    def allow_children(self) -> bool:
        """
        Allow Children
        ==============

        Get or set whether children are allowed to be added to the PyFlameTreeWidget.

        Returns
        -------
            bool:
                `True` if children are allowed, `False` if not.

        Set
        ---
            `value` (bool):
                `True` to allow, `False` to disallow.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get allow children
            print(tree_widget.allow_children)

            # Set allow children
            tree_widget.allow_children = False
            ```
        """

        return self._allow_children

    @allow_children.setter
    def allow_children(self, value: bool) -> None:
        """
        Allow Children
        ==============

        Set whether children are allowed to be added to the PyFlameTreeWidget.
        """

        # Validate argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget', 'allow_children', 'bool', value)

        # Set allow children
        self._allow_children = value

    @property
    def min_items(self) -> int:
        """
        Min Items
        =========

        Get or set the minimum number of items that must be present in the PyFlameTreeWidget.

        Must be an integer greater than 0.

        Returns
        -------
            int:
                The minimum number of items that must be present in the PyFlameTreeWidget.

        Set
        ---
            `value` (int):
                The minimum number of items that must be present in the PyFlameTreeWidget.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get minimum items
            print(tree_widget.min_items)

            # Set minimum items
            tree_widget.min_items = 10
            ```
        """

        return self._min_items

    @min_items.setter
    def min_items(self, value: int) -> None:
        """
        Min Items
        =========

        Set the minimum number of items that must be present in the PyFlameTreeWidget.
        """

        # Validate argument
        if not isinstance(value, int) or value < 1:
            pyflame.raise_type_error('PyFlameTreeWidget', 'min_items', 'int >= 1', value)

        # Set minimum items
        self._min_items = value

    @property
    def top_level_editable(self) -> bool:
        """
        Top Level Editable
        ==================

        Get or set whether the top-level item is editable.

        Returns
        -------
            bool: `True` if the top-level item is editable, `False` if not.

        Set
        ---
            `value` (bool): `True` to make the top-level item editable, `False` to make it uneditable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get top level editable
            print(tree_widget.top_level_editable)

            # Set top level editable
            tree_widget.top_level_editable = False
            ```
        """

        return self._top_level_editable

    @top_level_editable.setter
    def top_level_editable(self, value: bool) -> None:
        """
        Top Level Editable
        ==================

        Set whether the top-level item is editable.
        """

        # Validate argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget', 'top_level_editable', 'bool', value)

        # Set top level editable
        self._top_level_editable = value

        # Set the top-level item as uneditable if top_level_editable is False else make all items editable
        if not self._top_level_editable:
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
        else:
            # Access the top item
            top_item = self.topLevelItem(0)

            # Check if the top item exists. If it does, set the flags to make it editable
            if top_item:
                top_item.setFlags(top_item.flags() | QtCore.Qt.ItemIsEditable)
                # Optionally ensure child items are editable as well
                for i in range(top_item.childCount()):
                    child_item = top_item.child(i)
                    child_item.setFlags(child_item.flags() | QtCore.Qt.ItemIsEditable)

    @property
    def elide_text(self) -> bool:
        """
        Elide Text
        ==========

        Get or set whether to elide the text or not.

        If set to false '...' will be added when a string of text is longer than the display space.

        Returns
        -------
            bool: `True` if the tree widget is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get tree widget elide state
            print(tree_widget.enabled)

            # Set tree widget elide state
            tree_widget.enabled = False
            ```
        """

        return self._elide_text

    @elide_text.setter
    def elide_text(self, value: bool) -> None:
        """
        Elide Text
        ==========

        Set whether to elide the text or not.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget.elide_text', 'value', 'bool', value)

        self._elide_text = value

        # Set enabled state
        if self._elide_text:
            self.setTextElideMode(QtCore.Qt.ElideNone)

    @property
    def enabled(self) -> bool:
        """
        Enabled
        =======

        Get or set tree widget enabled state.

        Returns
        -------
            bool: `True` if the tree widget is enabled, `False` if disabled.

        Set
        ---
            `value` (bool):
                True to enable, False to disable.

        Raises
        ------
            TypeError:
                If the provided `value` is not a boolean.

        Examples
        --------
            ```
            # Get tree widget enabled state
            print(tree_widget.enabled)

            # Set tree widget enabled state
            tree_widget.enabled = False
            ```
        """

        return self.isEnabled()

    @enabled.setter
    def enabled(self, value: bool) -> None:
        """
        Enabled
        =======

        Enable or disable the tree widget.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameTreeWidget.enabled', 'value', 'bool', value)

        # Set enabled state
        self.setEnabled(value)

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set the tree widget width.

        Returns
        -------
            `int`:
                The current width of the tree widget in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the tree widget expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the tree widget is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(tree_widget.width)

            # Set a fixed width
            tree_widget.width = 150
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set the tree widget width.
        """

        # Validate Argument type
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTreeWidget.width', 'value', 'None | int', value)

        # Set width
        if value is None:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)
        else:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the List Widget height.

        Returns
        -------
            `int`:
                The current height of the tree widget in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the tree widget expands to fit the maximum height set by the layout. Minimum height is 28 pixels.
                If an integer, the tree widget is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(tree_widget.width)

            # Set a fixed width
            tree_widget.width = 140
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set the tree widget height.
        """

        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTreeWidget.height', 'value', 'None | int', value)

        # Set height
        if value is None:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)
        else:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)

    @property
    def tooltip(self) -> str | None:
        """
        Tooltip
        =======

        Get or set tree widget tooltip.

        Returns
        -------
            str | None:
                The tooltip text to display when hovering over the tree widget.

        Set
        ---
            `value` (str | None):
                The tooltip text to display when hovering over the tree widget.
                If `None`, no tooltip will be shown.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str | None.

        Examples
        --------
            ```
            # Get tree widget tooltip
            print(tree_widget.tooltip)

            # Set tree widget tooltip
            tree_widget.tooltip = 'Click to save changes'
            ```
        """

        return self.tooltip_popup.text

    @tooltip.setter
    def tooltip(self, value: str | None) -> None:
        """
        Tooltip
        =======

        Set the tooltip text for the tree widget.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlameTreeWidget.tooltip', 'value', 'None | str', value)

        # Set Tooltip Text
        if value is not None:
            self.tooltip_popup.text = value

    @property
    def tooltip_delay(self) -> int:
        """
        Tooltip Delay
        =============

        Get or set tooltip delay (in seconds).

        Returns
        -------
            int:
                The tooltip delay in seconds.

        Set
        ---
            `value` (int):
                The tooltip delay in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip delay
            print(tree_widget.tooltip_delay)

            # Set tooltip delay
            tree_widget.tooltip_delay = 0.5
            ```
        """

        return self.tooltip_popup.delay

    @tooltip_delay.setter
    def tooltip_delay(self, value: int) -> None:
        """
        Tooltip Delay
        =============

        Set tooltip delay.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTreeWidget.tooltip_delay', 'value', 'int', value)

        # Update Tooltip Delay
        self.tooltip_popup.delay = value

    @property
    def tooltip_duration(self) -> int:
        """
        Tooltip Duration
        ================

        Get or set tooltip duration (in seconds).

        Returns
        -------
            int:
                The tooltip duration in seconds.

        Set
        ---
            `value` (int):
                The tooltip duration in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an integer.

        Examples
        --------
            ```
            # Get tooltip duration
            print(tree_widget.tooltip_duration)

            # Set tooltip duration
            tree_widget.tooltip_duration = 5
            ```
        """

        return self.tooltip_popup.duration

    @tooltip_duration.setter
    def tooltip_duration(self, value: int) -> None:
        """
        Tooltip Duration
        ================

        Set tooltip duration (in seconds).
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameTreeWidget.tooltip_duration', 'value', 'int', value)

        # Update Tooltip Duration
        self.tooltip_popup.duration = value

    #-------------------------------------

    @property
    def all_item_paths(self) -> list:
        """
        All Item Paths
        ==============

        Get list of paths to all items in the tree.

        Returns
        -------
            list:
                A list of strings, where each string is the recursive path to an item in the tree.

        Example
        -------
            ```
            # Get list of paths to all items in the tree
            tree_widget.all_item_paths
            ```
        """

        def get_paths(item, current_path):

            # Recursively build paths for each item and its children
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

        Get list of paths to all items in the tree excluding the root.

        Returns
        -------
            list:
                A list of strings, where each string is the recursive path to an item in the tree excluding the root.

        Example
        -------
            ```
            # Get list of all items in tree except root
            tree_widget.all_item_paths_no_root
            ```
        """

        clean_paths = []

        # Remove root item from paths
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

        Get the recursive path of the currently selected item.

        Returns
        -------
            str:
                The recursive path of the currently selected item.

        Example
        -------
            ```
            # Get the recursive path of the currently selected item
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

        Get the recursive paths of the currently selected items.

        Returns
        -------
            List[str]:
                The recursive paths of the currently selected items.

        Example
        -------
            ```
            # Get the recursive paths of the currently selected items
            tree_widget.item_paths
            ```
        """

        def get_item_path(item):

            path = []
            while item is not None:
                path.insert(0, item.text(0))
                item = item.parent()

            return "/".join(path)

        return [get_item_path(item) for item in self.selectedItems()]

    @property
    def selected_item(self) -> str:
        """
        Selected Item
        =============

        Get the text of the currently selected item.

        Returns
        -------
            str:
                The text of the currently selected item.

        Example
        -------
            ```
            # Get the text of the currently selected item
            tree_widget.selected_item
            ```
        """

        return self.currentItem().text(0)

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def fill_tree_dict(self, tree_dict: Dict[str, Any], editable: bool=False) -> None:
        """
        Fill Tree Dict
        ==============

        Fill the PyFlameTreeWidget with items from the provided dictionary.

        Args
        ----
            `tree_dict` (Dict[str, str | Dict]):
                Dictionary to populate the PyFlameTreeWidget.
                The keys and values should be strings representing item names and
                nested dictionaries in string format respectively.

            `editable` (bool, optional):
                Whether the items in the tree should be editable.
                (Default: False)

        Raises
        ------
            TypeError:
                If `tree_dict` is not a dictionary.
                If `editable` is not a boolean.

            ValueError:
                If any key or value in `tree_dict` is not a string.
                If any value cannot be evaluated as a dictionary.

        Example
        -------
            Populate the PyFlameTreeWidget with items from a dictionary:
            ```
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

        # Validate Arguments
        if not isinstance(tree_dict, dict):
            pyflame.raise_type_error('PyFlameTreeWidget.fill_tree_dict', 'tree_dict', 'dict', tree_dict)
        if not isinstance(editable, bool):
            pyflame.raise_type_error('PyFlameTreeWidget.fill_tree_dict', 'editable', 'bool', editable)
        for key, value in tree_dict.items():
            if not isinstance(key, (str, dict)):
                pyflame.raise_type_error(error_message=f'PyFlameTreeWidget.fill_tree_dict: All keys in tree_dict must be strings. Invalid key: {key}')
            if not isinstance(value, (str, dict)):
                pyflame.raise_type_error(error_message=f'PyFlameTreeWidget.fill_tree_dict: All values in tree_dict must be strings. Invalid value for key "{key}": {value}')

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
            if not isinstance(value, dict):
                return  # Prevents recursion on non-dict

            for key, val in value.items():
                if not isinstance(key, str):
                    raise ValueError(f"Invalid key type: {key} (type: {type(key)})")

                child = QtWidgets.QTreeWidgetItem([key])
                parent.addChild(child)

                # Recursively add children only if val is a dict
                if isinstance(val, dict):
                    fill_item(child, val)

                # Set item flags
                child.setFlags(editable_flags if editable else default_flags)

                # Expand if it has children
                if isinstance(val, dict) and val:
                    child.setChildIndicatorPolicy(QtWidgets.QTreeWidgetItem.ShowIndicator)
                    child.setExpanded(True)

        if self.topLevelItemCount() > 0:
            self.clear()

        # Fill Tree with Items from Dict
        fill_item(self.invisibleRootItem(), tree_dict)

        # Restore sorting state based on the initial setting
        self.setSortingEnabled(self.isSortingEnabled())

    def fill_tree_list(self, tree_list: List[str]) -> None:
        """
        Fill Tree List
        ==============

        Fill the tree with items from the provided list.

        Args
        ----
            `tree_list` (List[str]):
                List of items to populate the tree.

        Raises
        ------
            TypeError:
                If `tree_list` is not a list.

        Example
        -------
            Populate the tree with items from a list:
            ```
            tree_widget.fill_tree_list(
                tree_list=['Item 1', 'Item 2', 'Item 3']
            )
            ```
        """

        # Validate the argument type
        if not isinstance(tree_list, list):
            pyflame.raise_type_error('PyFlameTreeWidget.fill_tree_list', 'tree_list', 'list', tree_list)

        # Clear the tree
        self.clear()

        # Fill the tree with items from the list
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

        Args
        ----
            `item_name` (str):
                The name of new item to add.

        Raises
        ------
            TypeError:
                If `item_name` is not a string.

        Example
        -------
            Add a new item to the PyFlameTreeWidget:
            ```
            tree_widget.add_item(item_name='New Item')
            ```
        """

        # Validate the argument type
        if not isinstance(item_name, str):
            pyflame.raise_type_error('PyFlameTreeWidget.add_item', 'item_name', 'str', item_name)

        # Disable sorting before adding the item
        self.setSortingEnabled(False)

        # Iterate the item name if it already exists in the tree
        existing_item_names = self.tree_list
        if existing_item_names:
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

    def add_item_with_columns(self, item: list[str]) -> QtWidgets.QTreeWidgetItem:
        """
        Add Item With Columns
        =====================

        Add a new item to the PyFlameTreeWidget with column data.

        Args
        ----
            `item` (list):
                New item to add to tree. The first item in the list is the name of the item.
                The following items in the list is the data to be added under the item columns.

        Returns
        -------
            Qt.Widgets.QTreeWidgetItem:
                Newly added item in tree

        Raises
        ------
            TypeError:
                If `item_name` is not a string.

        Example
        -------
            Add a new item to the PyFlameTreeWidget:
            ```
            tree_widget.add_item(item_name='New Item')
            ```
        """

        # Validate the argument type
        if not isinstance(item, list):
            pyflame.raise_type_error('PyFlameTreeWidget.add_item_with_columns', 'item', 'list', item)

        # Add item with columns to tree
        tree_item = QtWidgets.QTreeWidgetItem(self, item)

        # Trigger the callback function if it is set
        self._trigger_callback()

        return tree_item

    def delete_item(self) -> None:
        """
        Delete Item
        ===========

        Deletes the selected item in the PyFlameTreeWidget.
        Will not delete if the item is the top-level item or if the total number of items under the top-level item would drop below the minimum required.

        Example
        -------
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

    def color_item(self, item, color) -> None:
        """
        Color Item
        ==========

        Color item in tree with supplied QColor value.

        Args
        ----
            `item` (QTreeWidgetItem):
                QTreeWidgetItem to have color added.

            'color' (QColor):
                QColor value to be applied to item

        Raises
        ------
            TypeError:
                If `item` is not a QTreeWidgetItem(PyFlameTreeWidgetItem).

            ValueError:
                If 'color' is not a QColor value.

        Example
        -------
            Add color to item in tree
            ```
            tree_widget.color_item(item, color='#555555')
            ```
        """

        # Validate arguments
        if not isinstance(item, QtWidgets.QTreeWidgetItem):
            pyflame.raise_type_error('PyFlameTreeWidget.color_item', 'item', 'PyFlameTreeWidgetItem', item)

        if not QtGui.QColor.isValidColor(color):
            pyflame.raise_value_error('PyFlameTreeWidget.color_item', 'color', 'QColor', color)

        #Add color to item and all columns
        columns = self.columnCount()

        for column in range(columns):
            item.setForeground(column, QtGui.QColor(color))

    def set_fixed_column_headers(self) -> None:
        """
        Set Fixed Column Headers
        ========================

        Set all the column headers of a tree to a fixed length

        Example
        -------
            Set tree column headers to a fixed length
            ```
            tree_widget.color_item(item, color='#555555')
            ```
        """

        columns = self.columnCount()

        for column in range(columns):
            self.header().setSectionResizeMode(column, QtWidgets.QHeaderView.Fixed)

    def clear(self) -> None:
        """
        Clear
        =====

        Clears all items from the PyFlameTreeWidget.
        """

        super().clear()

    def update(self) -> None:
        """
        Update
        ======

        Update the tree using the update_connect callback.
        """

        self._trigger_callback()

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _trigger_callback(self) -> None:
        """
        Trigger Callback
        ================

        Trigger the callback function if it is set.
        """

        if self.update_connect_callback:
            self.update_connect_callback()

    def _on_item_collapsed(self, item) -> None:
        """
        On Item Collapsed
        =================

        Prevent the top-level item from collapsing.

        Args
        -----
            `item` (PyFlameTreeWidget.QTreeWidgetItem):
                The item that was collapsed.
        """

        # Check if the item is a top-level item
        if self.indexOfTopLevelItem(item) != -1:
            self.expandItem(item)  # Re-expand the top-level item

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
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

        # This custom line edit controls the color of the text when selected/highlighted
        class CustomItemDelegate(QtWidgets.QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                editor = QtWidgets.QLineEdit(parent)

                editor.setStyleSheet(f"""
                    QLineEdit {{
                        color: {Color.TEXT_SELECTED.value};
                        background-color: {Color.SELECTED_GRAY.value};
                        border: 1px solid {Color.SELECTED_GRAY.value};
                        selection-color: rgb(38, 38, 38);
                        selection-background-color: rgb(184, 177, 167);
                    }}
                """)

                return editor

        self.setItemDelegate(CustomItemDelegate(self))

    #-------------------------------------
    # [Tooltip Event Handlers]
    #-------------------------------------

    def enterEvent(self, event):
        self.tooltip_popup.enter_event()

    def leaveEvent(self, event):
        self.tooltip_popup.leave_event()

# ==============================================================================
# [PyFlame Misc Widgets]
# ==============================================================================

class PyFlameProgressBarWidget(QtWidgets.QProgressBar):
    """
    PyFlameProgressBarWidget
    ========================

    Custom QT Flame Progress Bar Widget Subclass

    Args
    ----
        `total_tasks` (int):
            Total number of tasks to be processed.
            (Default: 100)

        `processing_task` (int):
            Current task being processed.
            (Default: 0)

        `bar_color` (Color):
            Color of the progress bar.
            (Default: Color.BLUE)

        `bar_height` (int):
            Height of the progress bar.
            (Default: 5)

        `parent` (QtWidgets.QWidget, optional):
            Parent widget.
            (Default: None)

    Properties
    ----------
        `total_tasks` (int):
            Total number of tasks to be processed.
            (Default: 100)

        `processing_task` (int):
            Current task being processed.
            (Default: 0)

        `bar_color` (Color):
            Color of the progress bar.
            (Default: Color.BLUE)

        `bar_height` (int):
            Height of the progress bar.
            (Default: 5)
    """

    def __init__(self: 'PyFlameProgressBarWidget',
                 total_tasks: int=100,
                 processing_task: int=0,
                 bar_color: Color=Color.BLUE,
                 bar_height: int=5,
                 parent: QtWidgets.QWidget | None=None,
                 ) -> None:
        super().__init__(parent)

        # Set Properties
        self.total_tasks = total_tasks
        self.processing_task = processing_task
        self.bar_color = bar_color
        self.bar_height = bar_height

        # Widget Settings
        self.setTextVisible(False)

        # Set Style Sheet
        self.setStyleSheet(f"""
            QProgressBar {{
                color: {Color.TEXT.value};
                background-color: rgb(45, 45, 45);
                border: none;
            }}
            QProgressBar::chunk {{
                background-color: {self.bar_color.value};
            }}
        """)

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def total_tasks(self) -> int:
        """
        Total Tasks
        ===========

        Get or set the total number of tasks.

        Returns
        -------
            int:
                The total number of tasks.

        Set
        ---
            int:
                The total number of tasks.

        Raises
        ------
            TypeError:
                If `value` is not an integer.

        Examples
        --------
            ```
            # Get total number of tasks
            print(progress_bar.total_tasks)

            # Set total number of tasks
            progress_bar.total_tasks = 100
            ```
        """

        return self._total_tasks

    @total_tasks.setter
    def total_tasks(self, value: int) -> None:
        """
        Total Tasks
        ===========

        Set the total number of tasks.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressBarWidget', 'total_tasks', 'int', value)

        # Set Total Tasks
        self._total_tasks = value
        self.setMaximum(value)

    @property
    def processing_task(self) -> int:
        """
        Processing Task
        ===============

        Get or set the current task being processed.

        Returns
        -------
            int:
                The current task being processed.

        Set
        ---
            int:
                The current task being processed.

        Raises
        ------
            TypeError:
                If `value` is not an integer.

        Examples
        --------
            ```
            # Get current task
            print(progress_bar.processing_task)

            # Set current task
            progress_bar.processing_task = 10
            ```
        """

        return self._processing_task

    @processing_task.setter
    def processing_task(self, value: int) -> None:
        """
        Processing Task
        ===============

        Set the current task being processed.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressBarWidget', 'processing_task', 'integer', value)

        # Adjust value for progress bar
        if value > 0:
            value = value - 1

        # Set progress bar value
        self.setValue(value)
        QtWidgets.QApplication.processEvents()

        self._processing_take = value

    @property
    def bar_color(self) -> Color:
        """
        Bar Color
        =========

        Get or set the color of the progress bar using Color Enum.

        Returns
        -------
            Color:
                The color of progress bar.

        Set
        ---
            Color:
                The color of progress bar.

        Raises
        ------
            TypeError:
                If `value` is not a Color Enum.

        Examples
        --------
            ```
            # Get bar color
            print(progress_bar.bar_color)

            # Set bar color
            progress_bar.bar_color = Color.RED
            ```
        """

        return self._bar_color

    @bar_color.setter
    def bar_color(self, value: Color) -> None:
        """
        Bar Color
        =========

        Set color of progress bar using Color Enum.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameProgressBarWidget', 'bar_color', 'Color', value)

        self._bar_color = value

    @property
    def bar_height(self) -> int:
        """
        Bar Height
        ==========

        Get or set height of progress bar.

        Returns
        -------
            int:
                Height of progress bar.

        Set
        ---
            int:
                Height of progress bar.

        Raises
        ------
            TypeError:
                If `value` is not int.

        Examples
        --------
            ```
            # Get bar height
            print(progress_bar.bar_height)

            # Set bar height
            progress_bar.bar_height = 5
            ```
        """

        return self._bar_height

    @bar_height.setter
    def bar_height(self, value: int) -> None:
        """
        Bar Height
        ==========

        Set the height of the progress bar.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressBarWidget', 'bar_height', 'int', value)

        # Set Progress Bar Height
        self._bar_height = value
        self.setMaximumHeight(pyflame.gui_resize(value))

class PyFlameButtonGroup(QtWidgets.QButtonGroup):
    """
    PyFlameButtonGroup
    ==================

    Custom QT Flame Button Group Widget Subclass

    This class allows for grouping multiple buttons to control their checked state collectively.
    It supports setting the buttons to exclusive or non-exclusive behavior, meaning that either
    only one button can be checked at a time or multiple buttons can be checked simultaneously.

    Args
    ----
        `button_group` (list):
            List of buttons to be part of group.

        `set_exclusive` (bool, optional):
            If True, only one button can be checked at a time.
            (Default: `True`)

    Example
    -------
        To create a button group:
        ```
        button_group = PyFlameButtonGroup(
            button_group=[
                self.action_node_only_push_button,
                self.st_map_setup_button,
                self.patch_setup_button,
                ],
            )
        ```
    """

    def __init__(self: 'PyFlameButtonGroup',
                 button_group: list,
                 set_exclusive: bool=True,
                 ) -> None:
        super().__init__()

        self.button_group = button_group
        self.set_exclusive = set_exclusive

    @property
    def button_group(self) -> list:
        """
        Button Group
        ============

        Get or set the buttons in the button group.

        Returns
        -------
            list:
                The buttons in the button group.

        Set
        ---
            value (list):
                The buttons in the button group.

        Raises
        ------
            TypeError:
                If the value is not a list of QPushButton objects.

        Examples
        --------
            ```
            # Get the buttons in the button group
            button_group = button_group.button_group

            # Set the buttons in the button group
            button_group.button_group = [
                self.action_node_only_push_button,
                self.st_map_setup_button,
                self.patch_setup_button,
                ]
            ```
        """

        return self._button_group

    @button_group.setter
    def button_group(self, value: list) -> None:
        """
        Button Group
        ============

        Set the buttons in the button group.
        """

        # Validate Argument
        if not isinstance(value, list):
            pyflame.raise_type_error('PyFlameButtonGroup', 'button_group', 'list', value)
        if not all(isinstance(button, QtWidgets.QPushButton) for button in value):
            pyflame.raise_type_error('PyFlameButtonGroup', 'button_group', 'QPushButton', value)

        self._button_group = value

        # Add buttons to group
        for button in self._button_group:
            self.addButton(button)

    @property
    def set_exclusive(self) -> bool:
        """
        Set Exclusive
        =============

        Get or set the exclusive state of the button group.

        If set to True, only one button can be checked at a time.
        If set to False, multiple buttons can be checked simultaneously.

        Returns
        -------
            bool:
                The exclusive state of the button group.

        Set
        ---
            value (bool):
                The exclusive state of the button group.

        Raises
        ------
            TypeError:
                If the value is not a boolean.

        Examples
        --------
            ```
            # Get the exclusive state of the button group
            exclusive = button_group.set_exclusive

            # Set the exclusive state of the button group
            button_group.set_exclusive = True
            ```
        """

        return self.isExclusive()

    @set_exclusive.setter
    def set_exclusive(self, value: bool) -> None:
        """
        Set Exclusive
        =============

        Set the exclusive state of the button group.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameButtonGroup', 'set_exclusive', 'bool', value)

        # Set Exclusive
        self.setExclusive(value)

class PyFlameHorizontalLine(QtWidgets.QFrame):
    """
    PyFlameHorizontalLine
    =====================

    Horizontal line widget

    Args
    ----
        `color` (Color, optional):
            Color of the line. Uses Color Enum.
            (Default: `Color.GRAY`)

            Color Options:
                `Color.BLACK`: Black
                `Color.WHITE`: White
                `Color.GRAY`: Gray
                `Color.BRIGHT_GRAY`: Bright Gray
                `Color.BLUE`: Blue
                `Color.RED`: Red

        `width` (int, optional):
            Width of the line in pixels. If `None`, it expands to fit the layout. Minimum width is 25.
            (Default: `None`)

        `height` (int, optional):
            Height of the line in pixels. If `None`, defaults to 1.
            (Default: `None`)

    Properties
    ----------
        'color' (Color Enum):
            Line color.
            (Default: `Color.GRAY`)

        `width` (int):
            The width of line.
            (Default: `None`)

        `height` (int):
            The height of the line.
            (Default: `None`)

    Examples
    --------
        Create a blue horizontal line:
        ```
        line = PyFlameHorizontalLine(color=Color.Blue)
        ```

        To set or get any property:
        ```
        # Set property
        line.color = Color.RED

        # Get property
        print(line.color)
        ```
    """

    def __init__(self: 'PyFlameHorizontalLine',
                 color: Color=Color.GRAY,
                 width: int | None=None,
                 height: int | None=None,
                 ) -> None:
        super().__init__()

        # Set frame shape and shadow
        self.setFrameShape(QtWidgets.QFrame.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Set Properties
        self.color = color
        self.width = width
        self.height = height

        # Set Stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def color(self) -> Color:
        """
        Color
        =====

        Get or set the line color.

        Returns
        -------
            `Color`:
                Color of the line.

        Set
        ---
            `value` (Color):
                Color of the line.

        Raises
        ------
            TypeError:
                If `value` is not an instance of Color Enum.

        Examples
        --------
            ```
            # Get line color
            print(line.color)

            # Set line color
            line.color = COLOR.GRAY
            ```
        """

        return self._color

    @color.setter
    def color(self, value) -> None:
        """
        Color
        =====

        Set the color of the line.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameHorizontalLine', 'color', 'Color Enum', value)

        # Set style
        self._color = value

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set line width.

        Returns
        -------
            `int`:
                The current width of the line in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the line expands to fit the maximum width set by the layout. Minimum width is 25 pixels.
                If an integer, the line is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(line.width)

            # Set a fixed width
            line.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set line width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameHorizontalLine', 'width', 'None | int', value)

        # Set width
        if value is not None:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)
        else:
            self._width = pyflame.gui_resize(5000)
            self.setMinimumWidth(pyflame.gui_resize(25))
            self.setMaximumWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the line height.

        Returns
        -------
            `int`:
                The current height of the line in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the line uses the default height of 1.
                If an integer, the line is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get line height
            print(line.height)

            # Set line height
            line.height = 1
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set line height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameHorizontalLine', 'height', 'None | int', value)

        # Set height
        if value is not None:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)
        else:
            self._height = pyflame.gui_resize(1)
            self.setFixedHeight(self._height)

    #-------------------------------------
    # [Stylesheets]
    #-------------------------------------

    def _set_stylesheet(self) -> None:

        self.setStyleSheet(f"""
            QFrame{{
                background-color: {self.color.value}; /* Line color */
                border: none;
                max-height: {self.height}px;
                min-height: {self.height}px;
                }}
            """)

class PyFlameVerticalLine(QtWidgets.QFrame):
    """
    PyFlameVerticalLine
    ===================

    Vertical line widget

    Args
    ----
        `color` (Color, optional):
            Color of the line. Uses Color Enum.
            (Default: `Color.GRAY`)

            Color Options:
                `Color.BLACK`: Black
                `Color.WHITE`: White
                `Color.GRAY`: Gray
                `Color.BRIGHT_GRAY`: Bright Gray
                `Color.BLUE`: Blue
                `Color.RED`: Red

        `width` (int, optional):
            Width of the line in pixels. If `None`, defaults to 1.
            (Default: `None`)

        `height` (int, optional):
            Height of the line in pixels. If `None`, it expands to fit the layout. Minimum height is 28.
            (Default: `None`)

    Properties
    ----------
        'color' (Color Enum):
            Line color.
            (Default: `Color.GRAY`)

        `width` (int):
            The width of line.
            (Default: `None`)

        `height` (int):
            The height of the line.
            (Default: `None`)

    Examples
    --------
        Create a blue vertical line:
        ```
        line = PyFlameVerticalLine(color=Color.Blue)
        ```

        To set or get any property:
        ```
        # Set property
        line.color = Color.RED

        # Get property
        print(line.color)
        ```
    """

    def __init__(self: 'PyFlameVerticalLine',
                 color: Color=Color.GRAY,
                 width: int | None=None,
                 height: int | None=None,
                 ) -> None:
        super().__init__()

        # Set frame shape and shadow
        self.setFrameShape(QtWidgets.QFrame.VLine)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        # Set Properties
        self.color = color
        self.width = width
        self.height = height

        # Set Stylesheet
        self._set_style_sheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def color(self) -> Color:
        """
        Color
        =====

        Get or set the line color.

        Returns
        -------
            `Color`:
                Color of the line.

        Set
        ---
            `value` (Color):
                Color of the line.

        Raises
        ------
            TypeError:
                If `value` is not an instance of Color Enum.

        Examples
        --------
            ```
            # Get line color
            print(line.color)

            # Set line color
            line.color = COLOR.GRAY
            ```
        """

        return self._color

    @color.setter
    def color(self, value) -> None:
        """
        Color
        =====

        Set the color of the line.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameVerticalLine', 'color', 'Color Enum', value)

        # Set style
        self._color = value

    @property
    def width(self) -> int:
        """
        Width
        =====

        Get or set line width.

        Returns
        -------
            `int`:
                The current width of the line in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the line uses the default width of 1.
                If an integer, the line is given a fixed width.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get the current width
            print(line.width)

            # Set a fixed width
            line.width = 140
            ```
        """

        return self._width

    @width.setter
    def width(self, value: int | None) -> None:
        """
        Width
        =====

        Set line width.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameVerticalLine', 'width', 'None | int', value)

        # Set height
        if value is not None:
            self._width = pyflame.gui_resize(value)
            self.setFixedWidth(self._width)
        else:
            self._width = pyflame.gui_resize(1)
            self.setFixedWidth(self._width)

    @property
    def height(self) -> int:
        """
        Height
        ======

        Get or set the line height.

        Returns
        -------
            `int`:
                The current height of the line in pixels (after scaling).

        Set
        ---
            `value` (int | None):
                If `None`, the line expands to fit the maximum height set by the layout. Minimum height is 28 pixels.
                If an integer, the line is given a fixed height.

        Raises
        ------
            TypeError:
                If `value` is not `None` or an integer.

        Examples
        --------
            ```
            # Get line height
            print(line.height)

            # Set line height
            line.height = 100
            ```
        """

        return self._height

    @height.setter
    def height(self, value: int | None) -> None:
        """
        Height
        ======

        Set line height.
        """

        # Validate Argument
        if value is not None and not isinstance(value, int):
            pyflame.raise_type_error('PyFlameVerticalLine', 'height', 'None | int', value)

        # Set width
        if value is not None:
            self._height = pyflame.gui_resize(value)
            self.setFixedHeight(self._height)
        else:
            self._height = pyflame.gui_resize(5000)
            self.setMinimumHeight(pyflame.gui_resize(28))
            self.setMaximumHeight(self._height)

    #-------------------------------------
    # [Stylesheets]
    #-------------------------------------

    def _set_style_sheet(self) -> None:

        self.setStyleSheet(f"""
            QFrame{{
                background-color: {self.color.value}; /* Line color */
                border: none;
                max-width: {self.width}px;
                min-width: {self.width}px;
                }}
            """)

# ==============================================================================
# [PyFlame Layout Classes]
# ==============================================================================

class PyFlameGridLayout(QtWidgets.QGridLayout):
    """
    PyFlameGridLayout
    =================

    Custom QT QGridLayout Subclass.

    Configure the grid size of the layout by setting the number of columns, rows,
    and their respective sizes. Optionally adjust the width of specific columns
    and the height of specific rows.

    Args
    ----
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

    Properties
    ----------
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

        `adjust_column_widths` (dict[int, int]):
            A dictionary to adjust the width of specific columns.
            Keys are column indices (0-based), and values are widths in pixels.
            (Default: `{}`)

        `adjust_row_heights` (dict[int, int]):
            A dictionary to adjust the height of specific rows.
            Keys are row indices (0-based), and values are heights in pixels.
            (Default: `{}`)

    Raises
    ------
        TypeError:
            If any argument is not of the expected type.

    Example
    -------
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

    def __init__(self: 'PyFlameGridLayout',
                 columns: int=0,
                 rows: int=0,
                 column_width: int=150,
                 row_height: int=28,
                 adjust_column_widths: dict[int, int]={},
                 adjust_row_heights: dict[int, int]={},
                 ) -> None:
        super().__init__()

        self.setContentsMargins(pyflame.gui_resize(5), pyflame.gui_resize(5), pyflame.gui_resize(5), pyflame.gui_resize(5))

        # Set Properties
        self.columns = columns
        self.rows = rows
        self.column_width = column_width
        self.row_height = row_height
        self.adjust_column_widths = adjust_column_widths
        self.adjust_row_heights = adjust_row_heights

        # Create empty label widgets for each cell in the grid
        for row in range(self.rows):
            for col in range(self.columns):
                # If adjust_column_widths is None or empty, default to column_width
                if self.adjust_column_widths and col in self.adjust_column_widths:
                    width = self.adjust_column_widths[col]
                else:
                    width = self.column_width

                # If adjust_row_heights is None or empty, default to row_height
                if self.adjust_row_heights and row in self.adjust_row_heights:
                    height = self.adjust_row_heights[row]
                else:
                    height = self.row_height

                # Create the label with the specified dimensions
                empty_label = QtWidgets.QLabel('')
                empty_label.setFixedSize(pyflame.gui_resize(width), pyflame.gui_resize(height))

                self.addWidget(empty_label, row, col)

        #-------------------------------------
        # [Window Properties]
        #-------------------------------------

        @property
        def columns(self) -> int:
            """
            Columns
            =======

            Get or set the number of columns in the grid.

            Returns
            -------
                `int`:
                    The current number of columns in the grid.

            Set
            ---
                `value` (int):
                    The new number of columns in the grid.

            Raises
            ------
                TypeError:
                    If `value` is not an integer.

            Examples
            --------
                ```
                # Get the number of columns
                columns = grid_layout.columns

                # Set the number of columns
                grid_layout.columns = 4
                ```
            """

            return self._columns

        @columns.setter
        def columns(self, value: int) -> None:
            """
            Columns
            =======

            Set the number of columns in the grid.
            """

            # Validate Argument
            if not isinstance(value, int):
                pyflame.raise_type_error('PyFlameGridLayout', 'columns', 'int', value)

            # Set Columns
            self._columns = value

        @property
        def rows(self) -> int:
            """
            Rows
            ====

            Get or set the number of rows in the grid.

            Returns
            -------
                `int`:
                    The current number of rows in the grid.

            Set
            ---
                `value` (int):
                    The new number of rows in the grid.

            Raises
            ------
                TypeError:
                    If `value` is not an integer.

            Examples
            --------
                ```
                # Get the number of rows
                rows = grid_layout.rows

                # Set the number of rows
                grid_layout.rows = 5
                ```
            """

            return self._rows

        @rows.setter
        def rows(self, value: int) -> None:
            """
            Rows
            ====

            Set the number of rows in the grid.
            """

            # Validate Argument
            if not isinstance(value, int):
                pyflame.raise_type_error('PyFlameGridLayout', 'rows', 'int', value)

            # Set Rows
            self._rows = value

        @property
        def column_width(self) -> int:
            """
            Column Width
            ============

            Get or set the default width of each column in the grid.

            Returns
            -------
                `int`:
                    The current default width of each column in the grid.

            Set
            ---
                `value` (int):
                    The new default width of each column in the grid.

            Raises
            ------
                TypeError:
                    If `value` is not an integer.

            Examples
            --------
                ```
                # Get the default width of each column
                column_width = grid_layout.column_width

                # Set the default width of each column
                grid_layout.column_width = 150
                ```
            """

            return self._column_width

        @column_width.setter
        def column_width(self, value: int) -> None:
            """
            Column Width
            ============

            Set the default width of each column in the grid.
            """

            # Validate Argument
            if not isinstance(value, int):
                pyflame.raise_type_error('PyFlameGridLayout', 'column_width', 'int', value)

            # Set Column Width
            self._column_width = value

        @property
        def row_height(self) -> int:
            """
            Row Height
            ==========

            Get or set the default height of each row in the grid.

            Returns
            -------
                `int`:
                    The current default height of each row in the grid.

            Set
            ---
                `value` (int):
                    The new default height of each row in the grid.

            Raises
            ------
                TypeError:
                    If `value` is not an integer.

            Examples
            --------
                ```
                # Get the default height of each row
                row_height = grid_layout.row_height

                # Set the default height of each row
                grid_layout.row_height = 28
                ```
            """

            return self._row_height

        @row_height.setter
        def row_height(self, value: int) -> None:
            """
            Row Height
            ==========

            Set the default height of each row in the grid.
            """

            # Validate Argument
            if not isinstance(value, int):
                pyflame.raise_type_error('PyFlameGridLayout', 'row_height', 'int', value)

            # Set Row Height
            self._row_height = value

        @property
        def adjust_column_widths(self) -> dict[int, int]:
            """
            Adjust Column Widths
            ====================

            Get or set the widths of specific columns in the grid.

            Returns
            -------
                `dict[int, int]`:
                    A dictionary where keys are column indices (0-based) and values are widths in pixels.

            Set
            ---
                `value` (dict[int, int]):
                    A dictionary where keys are column indices (0-based) and values are widths in pixels.

            Raises
            ------
                TypeError:
                    If `value` is not a dictionary.

            Examples
            --------
                ```
                # Get the widths of specific columns
                adjust_column_widths = grid_layout.adjust_column_widths

                # Set the widths of specific columns
                grid_layout.adjust_column_widths = {0: 100, 1: 200}
                ```
            """

            return self._adjust_column_widths

        @adjust_column_widths.setter
        def adjust_column_widths(self, value: dict[int, int]) -> None:
            """
            Adjust Column Widths
            ====================

            Set the widths of specific columns in the grid.
            """

            # Validate Argument
            if not isinstance(value, dict):
                pyflame.raise_type_error('PyFlameGridLayout', 'adjust_column_widths', 'dict', value)

            # Set Adjust Column Widths
            self._adjust_column_widths = value

        @property
        def adjust_row_heights(self) -> dict[int, int]:
            """
            Adjust Row Heights
            ==================

            Get or set the heights of specific rows in the grid.

            Returns
            -------
                `dict[int, int]`:
                    A dictionary where keys are row indices (0-based) and values are heights in pixels.

            Set
            ---
                `value` (dict[int, int]):
                    A dictionary where keys are row indices (0-based) and values are heights in pixels.

            Raises
            ------
                TypeError:
                    If `value` is not a dictionary.

            Examples
            --------
                ```
                # Get the heights of specific rows
                adjust_row_heights = grid_layout.adjust_row_heights

                # Set the heights of specific rows
                grid_layout.adjust_row_heights = {0: 100, 1: 200}
                ```
            """

            return self._adjust_row_heights

        @adjust_row_heights.setter
        def adjust_row_heights(self, value: dict[int, int]) -> None:
            """
            Adjust Row Heights
            ==================

            Set the heights of specific rows in the grid.
            """

            # Validate Argument
            if not isinstance(value, dict):
                pyflame.raise_type_error('PyFlameGridLayout', 'adjust_row_heights', 'dict', value)

            # Set Adjust Row Heights
            self._adjust_row_heights = value

        #-------------------------------------
        # [Methods]
        #-------------------------------------

        def addWidget(self,
                      widget: QtWidgets.QWidget,
                      row: int,
                      column: int,
                      rowSpan: int=1,
                      columnSpan: int=1,
                      alignment: QtCore.Qt.Alignment | None=None,
                      ) -> None:
            """
            addWidget
            =========

            Passes arguments to QGridLayout.addWidget.

            Args
            ----
                widget (QWidget): The widget to add to the layout.
                row (int): Row position in the layout grid.
                column (int): Column position in the layout grid.
                rowSpan (int, optional): Number of rows the widget should span. Default is 1.
                columnSpan (int, optional): Number of columns the widget should span. Default is 1.
                alignment (Qt.Alignment, optional): Alignment flag from Qt. Default is None.
            """

            # Validate Arguments
            if not isinstance(widget, QtWidgets.QWidget):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'widget', 'QWidget', widget)
            if not isinstance(row, int):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'row', 'int', row)
            if not isinstance(column, int):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'column', 'int', column)
            if not isinstance(rowSpan, int):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'rowSpan', 'int', rowSpan)
            if not isinstance(columnSpan, int):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'columnSpan', 'int', columnSpan)
            if alignment is not None and not isinstance(alignment, QtCore.Qt.Alignment):
                pyflame.raise_type_error('PyFlameGridLayout.addWidget', 'alignment', 'Qt.Alignment | None', alignment)

            # Call base addWidget implementation
            if alignment is not None:
                return super().addWidget(widget, row, column, rowSpan, columnSpan, alignment)
            else:
                return super().addWidget(widget, row, column, rowSpan, columnSpan)

class PyFlameHBoxLayout(QtWidgets.QHBoxLayout):
    """
    PyFlameHBoxLayout
    =================

    Custom QT QHBoxLayout Subclass.

    Values are adjusted for display scale using `pyflame.gui_resize()`.

    Methods
    -------
        `setSpacing(spacing)`:
            Apply spacing between widgets in PyFlameHBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

        `setContentsMargins(left, top, right, bottom)`:
            Apply margins to PyFlameHBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

    Example
    -------
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

        Args
        ----
            `spacing` (int):
                Spacing in pixels.

        Raises
        ------
            TypeError:
                If `spacing` is not an integer.

        Example
        -------
            To set the spacing between widgets in the PyFlameHBoxLayout to 10 pixels:
            ```
            hbox_layout.setSpacing(10)
            ```
        """

        if not isinstance(spacing, int):
            pyflame.raise_type_error('PyFlameHBoxLayout.setSpacing', 'spacing', 'int', spacing)

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

        Args
        ----
            `spacing` (int):
                Spacing in pixels.

        Raises
        ------
            TypeError:
                If `spacing` is not an integer.

        Example
        -------
            To add a 10-pixel space between two widgets in the PyFlameHBoxLayout:
            ```
            hbox_layout.addSpacing(10)
            ```
        """

        # Validate Argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error('PyFlameHBoxLayout.setSpacing', 'spacing', 'int', spacing)

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

        Args
        ----
            `left` (int):
                Left margin in pixels.

            `top` (int):
                Top margin in pixels.

            `right` (int):
                Right margin in pixels.

            `bottom` (int):
                Bottom margin in pixels.

        Raises
        ------
            TypeError:
                If `left` is not an integer.
                If `top` is not an integer.
                If `right` is not an integer.
                If `bottom` is not an integer.

        Example
        -------
            To set margins around the contents of the PyFlameHBoxLayout to 10 pixels:
            ```
            hbox_layout.setContentsMargins(10, 10, 10, 10)
            ```
        """

        def validate_arguments():

            if not isinstance(left, int):
                pyflame.raise_type_error('PyFlameHBoxLayout.setContentsMargins', 'left', 'int', left)
            if not isinstance(top, int):
                pyflame.raise_type_error('PyFlameHBoxLayout.setContentsMargins', 'top', 'int', top)
            if not isinstance(right, int):
                pyflame.raise_type_error('PyFlameHBoxLayout.setContentsMargins', 'right', 'int', right)
            if not isinstance(bottom, int):
                pyflame.raise_type_error('PyFlameHBoxLayout.setContentsMargins', 'bottom', 'int', bottom)

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

    Methods
    -------
        `setSpacing(spacing)`:
            Apply spacing between widgets in the PyFlameVBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

        `setContentsMargins(left, top, right, bottom)`:
            Apply margins to the PyFlameVBoxLayout adjusted for display scale using `pyflame.gui_resize()`.

    Example
    -------
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

        Args
        ----
            `spacing` (int):
                Spacing in pixels.

        Raises
        ------
            TypeError:
                If `spacing` is not an integer.

        Example
        -------
            To set the spacing between widgets in the PyFlameVBoxLayout to 10 pixels:
            ```
            vbox_layout.setSpacing(10)
            ```
        """

        # Validate Argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error('PyFlameVBoxLayout', 'setSpacing', 'int', spacing)

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

        Args
        ----
            `spacing` (int):
                Spacing in pixels.

        Raises
        ------
            TypeError:
                If `spacing` is not an integer.

        Example
        -------
            To add a 10-pixel space between two widgets in the PyFlameVBoxLayout:
            ```
            vbox_layout.addSpacing(10)
            ```
        """

        # Validate Argument types
        if not isinstance(spacing, int):
            pyflame.raise_type_error('PyFlameVBoxLayout.addSpacing', 'spacing', 'int', spacing)

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

        Args
        ----
            `left` (int):
                Left margin in pixels.
            `top` (int):
                Top margin in pixels.
            `right` (int):
                Right margin in pixels.
            `bottom` (int):
                Bottom margin in pixels.

        Raises
        ------
            TypeError:
                If `left` is not an integer.
                If `top` is not an integer.
                If `right` is not an integer.
                If `bottom` is not an integer.

        Example
        -------
            To set margins around the contents of the PyFlameVBoxLayout to 10 pixels:
            ```
            vbox_layout.setContentsMargins(10, 10, 10, 10)
            ```
        """

        def validate_arguments():

            if not isinstance(left, int):
                pyflame.raise_type_error('PyFlameVBoxLayout.setContentsMargins', 'left', 'int', left)
            if not isinstance(top, int):
                pyflame.raise_type_error('PyFlameVBoxLayout.setContentsMargins', 'top', 'int', top)
            if not isinstance(right, int):
                pyflame.raise_type_error('PyFlameVBoxLayout.setContentsMargins', 'right', 'int', right)
            if not isinstance(bottom, int):
                pyflame.raise_type_error('PyFlameVBoxLayout.setContentsMargins', 'bottom', 'int', bottom)

        validate_arguments()

        # Set Margins
        super().setContentsMargins(
            pyflame.gui_resize(left),
            pyflame.gui_resize(top),
            pyflame.gui_resize(right),
            pyflame.gui_resize(bottom)
            )

# ==============================================================================
# [PyFlame Main Window]
# ==============================================================================

class PyFlameWindow(QtWidgets.QDialog):
    """
    PyFlameWindow
    =============

    Creates a custom QT window with a colored bar on the left side of the window.

    The windows uses a grid layout to place widgets. See example below.

    Setting a parent window is required to avoid window layering problems in linux.

    Args
    ----
        `parent` (PyFlameWindow | None):
            Parent window for the window if any. Set to `None` if no parent window.
            Not setting a parent window for any window that should appear over another window will cause window
            layering problems in linux.

        `title` (str):
            Text displayed in top left corner of window.
            (Default: `Python Script`)

        `title_style` (Style):
            Style of title text. Use `Style` Enum to set style.
            (Default: `Style.BACKGROUND`)

            Style Options
                `Style.BACKGROUND`: For background style.
                `Style.BACKGROUND_THIN`: For background style with thin border.
                `Style.NORMAL`: For normal style.
                `Style.UNDERLINE`: For underline style.

        `title_align` (Align):
            Alignment of title text. Use `Align` Enum to set alignment.
            (Default: `Align.LEFT`)

            Align Options
                `Align.LEFT`: For left alignment.
                `Align.CENTER`: For center alignment.
                `Align.RIGHT`: For right alignment.

        `title_underline_color` (Color):
            Color of underline below title text.
            Only used if `title_style` is `Style.UNDERLINE`.
            (Default: `Color.BLUE_TRANS`)

            Color Options
                `Color.BLUE_TRANS`: Blue underline.
                `Color.RED_TRANS`: Red underline.
                `Color.GREEN_TRANS`: Green underline.
                `Color.YELLOW_TRANS`: Yellow underline.
                `Color.TEAL_TRANS`: Teal underline.

        `title_height` (int):
            Height of title area.
            (Default: `48`)

        `title_font_size` (int):
            Font size of title text.
            (Default: `24`)

        `message_bar` (bool):
            Enable message bar at bottom of window.
            (Default: `True`)

        `line_color` (Color):
            Color of bar on left side of window.
            (Default: `Color.BLUE`)

            Color Options
                `Color.GRAY`: Gray line.
                `Color.BLUE`: Blue line.
                `Color.RED`: Red line.
                `Color.GREEN`: Green line.
                `Color.YELLOW`: Yellow line.
                `Color.TEAL`: Teal line.

        `tab_order` (list, optional):
            List of widgets in the tab order. Must have two or more widgets.
            (Default: `None`)

        `return_pressed` (callable, optional):
            Function to be called when return/enter key is pressed.
            (Default: `None`)

        `escape_pressed` (callable, optional):
            Function to be called when escape key is pressed.
            (Default: `None`)

        `grid_layout_columns` (int):
            Number of columns in grid layout. Only used if `grid_layout` is `True`.
            (Default: `4`)

        `grid_layout_rows` (int):
            Number of rows in grid layout. Only used if `grid_layout` is `True`.
            (Default: `3`)

        `grid_layout_column_width` (int):
            Width of columns in grid layout. Only used if `grid_layout` is `True`.
            (Default: `150`)

        `grid_layout_row_height` (int):
            Height of rows in grid layout. Only used if `grid_layout` is `True`.
            (Default: `28`)

        `grid_layout_adjust_column_widths` (dict, optional):
            Dictionary of column widths to adjust.
            (Default: `{}`)

        `grid_layout_adjust_row_heights` (dict, optional):
            Dictionary of row heights to adjust.
            (Default: `{}`)

        `window_margins` (int | tuple[int, int, int, int]):
            Margin in pixels around the main content area. Pass a single int to use the same value for left, top, right,
            and bottom; or pass a tuple of four ints for (left, top, right, bottom). Values are scaled by `pyflame.gui_resize()`.
            (Default: `15`)

    Properties
    ----------
        `title` (str):
            Get or set the title of the window.
            (Default: `Python Script`)

        `title_style` (Style):
            Get or set the style of the title.
            (Default: `Style.BACKGROUND`)

        `title_align` (Align):
            Get or set the alignment of the title.
            (Default: `Align.LEFT`)

        `title_underline_color` (Color):
            Get or set the color of the underline below the title.
            (Default: `Color.BLUE_TRANS`)

        `title_height` (int):
            Get or set the height of the title.
            (Default: `48`)

        `title_font_size` (int):
            Get or set the font size of the title.
            (Default: `24`)

        `message_bar_text` (str):
            Get or set text in message bar.
            (Default: `""`)

        `line_color` (Color):
            Get or set the color of the line on the left side of the window.
            (Default: `Color.BLUE`)

        `tab_order` (list):
            Get or set the list of widgets in the tab order.
            (Default: `None`)

        `return_pressed` (callable):
            Get or set the function to be called when the return/enter key is pressed.
            (Default: `None`)

        `escape_pressed` (callable):
            Get or set the function to be called when the escape key is pressed.
            (Default: `None`)

        `grid_layout_columns` (int):
            Get or set the number of columns in the grid layout.
            (Default: `4`)

        `grid_layout_rows` (int):
            Get or set the number of rows in the grid layout.
            (Default: `3`)

        `grid_layout_column_width` (int):
            Get or set the width of the columns in the grid layout.
            (Default: `150`)

        `grid_layout_row_height` (int):
            Get or set the height of the rows in the grid layout.
            (Default: `28`)

        `grid_layout_adjust_column_widths` (dict):
            Get or set the dictionary of column widths to adjust.
            (Default: `{}`)

        `grid_layout_adjust_row_heights` (dict):
            Get or set the dictionary of row heights to adjust.
            (Default: `{}`)

        `window_margins` (int | tuple[int, int, int, int]):
            Get or set the margin in pixels around the main content area. Accepts a single int or a tuple of four ints
            (left, top, right, bottom). Getter always returns a tuple of four ints.
            (Default: `15`)

    Notes
    -----
        For proper sizing of widgets and placement of widgets in the window,
        be sure to set the correct number of columns and rows in the grid layout
        when using the default grid layout.

    Example
    -------
        To create a new window with some widgets:
        ```
        window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION},
            return_pressed=confirm,
            escape_pressed=cancel,
            grid_layout_columns=6,
            grid_layout_rows=5,
            )

        # Add widgets with their default size
        window.grid_layout.addWidget(some_widget1, 0, 0) # row 0, column 0
        window.grid_layout.addWidget(some_widget2, 1, 0) # row 1, column 0
        window.grid_layout.addWidget(some_widget3, 2, 0) # row 2, column 0

        # Add widgets with a custom size spanning multiple rows and columns
        window.grid_layout.addWidget(some_widget1, 0, 0, 1, 2) # row 0, column 0, row span 1, column span 2
        window.grid_layout.addWidget(some_widget2, 1, 0, 2, 3) # row 1, column 0, row span 2, column span 3
        window.grid_layout.addWidget(some_widget3, 2, 0, 2, 4) # row 2, column 0, row span 2, column span 4
        ```

        To update text in message bar:
        ```
        window.message_bar_text = 'New Message'
        ```

        To update text in title:
        ```
        window.title = 'New Title'
        ```
    """

    def __init__(self: 'PyFlameWindow',
                 parent: QtWidgets.QWidget | None,
                 title: str='',
                 title_style: Style=Style.BACKGROUND_THIN,
                 title_align: Align=Align.LEFT,
                 title_underline_color: Color=Color.BLUE_TRANS,
                 title_height: int=48,
                 title_font_size: int=24,
                 message_bar: bool=True,
                 line_color: Color=Color.BLUE,
                 tab_order: list[QtWidgets.QWidget] | None=None,
                 return_pressed: Callable[..., None] | None=None,
                 escape_pressed: Callable[..., None] | None=None,
                 grid_layout_columns: int=4,
                 grid_layout_rows: int=3,
                 grid_layout_column_width: int=150,
                 grid_layout_row_height: int=28,
                 grid_layout_adjust_column_widths: dict[int, int]={},
                 grid_layout_adjust_row_heights: dict[int, int]={},
                 window_margins: int | tuple[int, int, int, int]=15,
                 ) -> None:

        # Validate Parent
        if not isinstance(parent, (type(None), PyFlameWindow)):
            pyflame.raise_type_error('PyFlameWindow', 'parent', 'PyFlameWindow | None', parent)

        super().__init__(parent)

        # Set Font
        self.setFont(FONT)

        # Window Title Label
        self.title_label = PyFlameLabel()

        # Window message bar
        self.message_bar_label = PyFlameLabel(
            text=' ',
            style=Style.BACKGROUND,
            align=Align.LEFT,
            )

        # Init window layout widgets
        self.title_text_hbox = PyFlameHBoxLayout()
        self.message_bar_hbox = PyFlameHBoxLayout()
        self.main_vbox2 = PyFlameVBoxLayout()
        self.center_layout = PyFlameGridLayout() # Main UI added to this widget

        #-------------------------------------
        # [Window Properties]
        #-------------------------------------

        self.title = title
        self.title_style = title_style
        self.title_align = title_align
        self.title_underline_color = title_underline_color
        self.title_height = title_height
        self.title_font_size = title_font_size
        self.message_bar = message_bar
        self.line_color = line_color
        self.tab_order = tab_order

        self.grid_layout_columns = grid_layout_columns
        self.grid_layout_rows = grid_layout_rows
        self.grid_layout_column_width = grid_layout_column_width
        self.grid_layout_row_height = grid_layout_row_height
        self.grid_layout_adjust_column_widths = grid_layout_adjust_column_widths
        self.grid_layout_adjust_row_heights = grid_layout_adjust_row_heights
        self.window_margins = window_margins

        # Set Window Flags
        self.setWindowFlags(QtCore.Qt.Tool | QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Return/Escape Key Events
        self.return_pressed = return_pressed
        self.escape_pressed = escape_pressed

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.title_text_hbox.addWidget(self.title_label)
        self.title_text_hbox.setContentsMargins(2, 0, 0, 0)  # Set margin to 2px to account for the line overlay.

        self.message_bar_hbox.addWidget(self.message_bar_label)
        self.message_bar_hbox.setContentsMargins(2, 0, 0, 0)  # Set margin to 2px to account for the line overlay.

        # Create widget to hold the center layout
        center_widget = QtWidgets.QWidget()
        center_widget.setLayout(self.center_layout)

        # Add the center layout to the main layout
        self.main_vbox2.addWidget(center_widget, alignment=QtCore.Qt.AlignCenter)
        self.main_vbox2.addStretch()

        main_vbox3 = PyFlameVBoxLayout()
        main_vbox3.addLayout(self.title_text_hbox)
        main_vbox3.addLayout(self.main_vbox2)
        if self.message_bar:
            main_vbox3.addLayout(self.message_bar_hbox)
        main_vbox3.setContentsMargins(0, 0, 0, 0)  # Remove margins

        self.setLayout(main_vbox3)

        # Create grid layout that widegts will be added to.
        self.grid_layout = PyFlameGridLayout(
            columns=self.grid_layout_columns,
            rows=self.grid_layout_rows,
            column_width=self.grid_layout_column_width,
            row_height=self.grid_layout_row_height,
            adjust_column_widths=self.grid_layout_adjust_column_widths,
            adjust_row_heights=self.grid_layout_adjust_row_heights,
            )

        self.center_layout.addLayout(self.grid_layout, 0, 0)

        # Show Window
        self.show()

        # Lock Window Size After Layout is Added
        self.setFixedSize(self.size())

        # Center Window on Screen
        self.center_window()

        # Set Window Stylesheet
        self._set_stylesheet()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def line_color(self) -> Color:
        """
        Line Color
        ==========

        Get or set the color of the line in the window.

        Returns
        -------
            Color:
                The color of the line in the window.

        Set
        ---
            line_color (Color):
                The color of the line in the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color.

        Examples
        --------
            ```
            # Get line color
            print(window.line_color)

            # Set line Color
            window.line_color = Color.RED
            ```
        """

        return self._line_color

    @line_color.setter
    def line_color(self, value: Color) -> None:
        """
        Line Color
        ===========

        Set the color of the line in the window.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameWindow', 'line_color', 'Color Enum', value)

        self._line_color = value
        self.update()  # Triggers paintEvent with new color

    @property
    def title(self) -> str:
        """
        Title
        =====

        Get or set the title of the window.

        Returns
        -------
            str:
                The title of the window.

        Set
        ---
            title (str):
                The title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get title
            print(window.title)

            # Set title
            window.title = 'New Title'
            ```
        """
        return self._title

    @title.setter
    def title(self, value: str) -> None:
        """
        Title
        ====

        Set the title of the window.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameWindow', 'title', 'str', value)

        # Set Window Title
        self._title = value
        self.title_label.text = '<span style="white-space: pre;">  ' + value

    @property
    def title_style(self) -> Style:
        """
        Title Style
        ===========

        Get or set the style of the title of the window.

        Returns
        -------
            Style:
                The style of the title of the window.

        Set
        ---
            title_style (Style):
                The style of the title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Style.

        Examples
        --------
            ```
            # Get title style
            print(window.title_style)

            # Set title style
            window.title_style = Style.UNDERLINE
            ```
        """

        return self.title_label.style

    @title_style.setter
    def title_style(self, value: Style) -> None:
        """
        Title Style
        ===========

        Set the style of the title of the window.
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlameWindow', 'title_style', 'Style Enum', value)

        # Set Window Title Style
        self.title_label.style = value

    @property
    def title_align(self) -> Align | None:
        """
        Title Align
        ===========

        Get or set the alignment of the title of the window.

        Returns
        -------
            Align:
                The alignment of the title of the window.

        Set
        ---
            title_align (Align):
                The alignment of the title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not an Align.

        Examples
        --------
            ```
            # Get title align
            print(window.title_align)

            # Set title align
            window.title_align = Align.CENTER
            ```
        """

        return self.title_label.align

    @title_align.setter
    def title_align(self, value: Align) -> None:
        """
        Title Align
        ===========

        Set the alignment of the title of the window.
        """

        # Validate Argument
        if not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameWindow', 'title_align', 'Align Enum', value)

        # Set Window Title Alignment
        self.title_label.align = value

    @property
    def title_underline_color(self) -> Color:
        """
        Title Underline Color
        =====================

        Get or set the color of the underline of the title of the window.

        Returns
        -------
            Color:
                The color of the underline of the title of the window.

        Set
        ---
            title_underline_color (Color):
                The color of the underline of the title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color.

        Examples
        --------
            ```
            # Get title underline color
            print(window.title_underline_color)

            # Set title underline color
            window.title_underline_color = Color.RED
            ```
        """

        return self.title_label.underline_color

    @title_underline_color.setter
    def title_underline_color(self, value: Color) -> None:
        """
        Title Underline Color
        =====================

        Set the color of the underline of the title of the window.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameWindow', 'title_underline_color', 'Color Enum', value)

        # Set Window Title Underline Color
        if self.title_style == Style.UNDERLINE:
            self.title_label.underline_color = value

    @property
    def title_height(self) -> int | None:
        """
        Title Height
        ============

        Get or set the height of the title of the window.

        Returns
        -------
            int:
                The height of the title of the window.

        Set
        ---
            title_height (int):
                The height of the title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get title height
            print(window.title_height)

            # Set title height
            window.title_height = 50
            ```
        """

        return self.title_label.height

    @title_height.setter
    def title_height(self, value: int) -> None:
        """
        Title Height
        ============

        Set the height of the title of the window.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'title_height', 'int', value)

        # Set Window Title Height
        self.title_label.height = value

    @property
    def title_font_size(self) -> int | None:
        """
        Title Font Size
        ===============

        Get or set the font size of the title of the window.

        Returns
        -------
            int:
                The font size of the title of the window.

        Set
        ---
            title_font_size (int):
                The font size of the title of the window.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get title font size
            print(window.title_font_size)

            # Set title font size
            window.title_font_size = 20
            ```
        """

        return self.title_label.font_size

    @title_font_size.setter
    def title_font_size(self, value: int) -> None:
        """
        Title Font Size
        ===============

        Set the font size of the title of the window.
        """

        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'title_font_size', 'int', value)

        # Set Window Title Font Size
        self.title_label.font_size = value

    @property
    def message_bar_text(self) -> str:
        """
        Message Bar Text
        ================

        Get or set the text of the message bar.

        Returns
        -------
            str:
                The text of the message bar.

        Set
        ---
        message_bar_text (str):
            The text of the message bar.

        Examples
        --------
            ```
            # Get message bar text
            print(window.message_bar_text)

            # Set message bar text
            window.message_bar_text = 'This is a message bar text'
            ```
        """

        return self.message_bar_label.text

    @message_bar_text.setter
    def message_bar_text(self, value: str) -> None:
        """
        Message Bar Text
        ================

        Set the text of the message bar.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameWindow', 'message_bar_text', 'str', value)

        # Set Message Bar Text
        self.message_bar_label.text = value

        #Pause QT briefly to allow the message bar to update
        pyflame.pause()

    @property
    def tab_order(self):
        """
        Tab Order
        =========

        Set or get the widget tab-key order of the window. Allows for tabbing between widgets.

        Must have two or more widgets in the tab order.

        Returns
        -------
            list:
                List of widgets in the tab order.

        Set
        ---
            tab_order (list):
                List of widgets to set the tab order of.

        Raises
        ------
            TypeError:
                If `tab_order` is not a list.
            ValueError:
                If `tab_order` is not a list of at least 2 widgets.

        Examples
        --------
            ```
            # Get Tab Order
            print(window.tab_order)

            # Set Tab Order
            window.tab_order = [widget1, widget2]
            ```
        """

        return self._tab_order

    @tab_order.setter
    def tab_order(self, tab_order):
        """
        Tab Order
        =========

        Set the tab order of the window.

        Must have two or more widgets in the tab order.
        """

        # Validate Argument
        if tab_order is not None and not isinstance(tab_order, list):
            pyflame.raise_type_error('PyFlameWindow', 'tab_order', 'list', tab_order)
        if tab_order is not None and len(tab_order) < 2:
            pyflame.raise_value_error(error_message='PyFlameWindow.tab_order must be a list of at least 2 widgets.')

        # Set Tab Order
        self._tab_order = tab_order

        if tab_order is not None:
            for widget in tab_order:
                widget.setFocusPolicy(QtCore.Qt.StrongFocus)
            for i in range(len(self._tab_order) - 1):
                QtWidgets.QWidget.setTabOrder(self._tab_order[i], self._tab_order[i + 1])

    @property
    def return_pressed(self) -> Callable[[], None] | None:
        """
        Return Pressed
        ==============

        Get or set the function to be called when the Return key is pressed.

        Returns
        -------
            callable:
                The function to be called when the Return key is pressed.

        Set
        ---
            return_pressed (callable):
                The function to be called when the Return key is pressed.

        Raises
        ------
            TypeError:
                If the provided `value` is not a callable.

        Examples
        --------
            ```
            # Get return pressed
            print(window.return_pressed)

            # Set return pressed
            window.return_pressed = lambda: print('Return key pressed')
            ```
        """

        return self._return_pressed

    @return_pressed.setter
    def return_pressed(self, value: Callable[[], None] | None) -> None:
        """
        Return Pressed
        ==============

        Set the function to be called when the Return key is pressed.
        """

        # Validate Argument
        if value is not None and not callable(value):
            pyflame.raise_type_error('PyFlameWindow', 'return_pressed', 'callable | None', value)

        # Set return pressed
        self._return_pressed = value

    @property
    def escape_pressed(self) -> Callable[[], None] | None:
        """
        Escape Pressed
        ==============

        Get or set the function to be called when the Escape key is pressed.

        Returns
        -------
            callable:
                The function to be called when the Escape key is pressed.

        Set
        ---
            escape_pressed (callable):
                The function to be called when the Escape key is pressed.

        Raises
        ------
            TypeError:
                If the provided `value` is not a callable.

        Examples
        --------
            ```
            # Get escape pressed
            print(window.escape_pressed)

            # Set escape pressed
            window.escape_pressed = lambda: print('Escape key pressed')
            ```
        """

        return self._escape_pressed

    @escape_pressed.setter
    def escape_pressed(self, value: Callable[[], None] | None) -> None:
        """
        Escape Pressed
        ==============

        Set the function to be called when the Escape key is pressed.
        """

        # Validate Argument
        if value is not None and not callable(value):
            pyflame.raise_type_error('PyFlameWindow', 'escape_pressed', 'callable | None', value)

        # Set escape pressed
        self._escape_pressed = value

    @property
    def grid_layout_columns(self) -> int:
        """
        Grid Layout Columns
        ===================

        Get or set the number of columns in the grid layout.

        Returns
        -------
            int:
                The number of columns in the grid layout.

        Set
        ---
            grid_layout_columns (int):
                The number of columns in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get grid layout columns
            print(window.grid_layout_columns)

            # Set grid layout columns
            window.grid_layout_columns = 2
            ```
        """

        return self._grid_layout_columns

    @grid_layout_columns.setter
    def grid_layout_columns(self, value: int) -> None:
        """
        Grid Layout Columns
        ===================

        Set the number of columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_columns', 'int', value)

        self._grid_layout_columns = value

    @property
    def grid_layout_rows(self) -> int:
        """
        Grid Layout Rows
        =================

        Get or set the number of rows in the grid layout.

        Returns
        -------
            int:
                The number of rows in the grid layout.

        Set
        ---
            grid_layout_rows (int):
                The number of rows in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get grid layout rows
            print(window.grid_layout_rows)

            # Set grid layout rows
            window.grid_layout_rows = 2
            ```
        """

        return self._grid_layout_rows

    @grid_layout_rows.setter
    def grid_layout_rows(self, value: int) -> None:
        """
        Grid Layout Rows
        =================

        Set the number of rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_rows', 'int', value)

        self._grid_layout_rows = value

    @property
    def grid_layout_column_width(self) -> int:
        """
        Grid Layout Column Width
        ========================

        Get or set the width of the columns in the grid layout.

        Returns
        -------
            int:
                The width of the columns in the grid layout.

        Set
        ---
            grid_layout_column_width (int):
                The width of the columns in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get grid layout column width
            print(window.grid_layout_column_width)

            # Set grid layout column width
            window.grid_layout_column_width = 200
            ```
        """

        return self._grid_layout_column_width

    @grid_layout_column_width.setter
    def grid_layout_column_width(self, value: int) -> None:
        """
        Grid Layout Column Width
        ========================

        Set the width of the columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_column_width', 'int', value)

        self._grid_layout_column_width = value

    @property
    def grid_layout_row_height(self) -> int:
        """
        Grid Layout Row Height
        ======================

        Get or set the height of the rows in the grid layout.

        Returns
        -------
            int:
                The height of the rows in the grid layout.

        Set
        ---
            grid_layout_row_height (int):
                The height of the rows in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not an int.

        Examples
        --------
            ```
            # Get grid layout row height
            print(window.grid_layout_row_height)

            # Set grid layout row height
            window.grid_layout_row_height = 200
            ```
        """

        return self._grid_layout_row_height

    @grid_layout_row_height.setter
    def grid_layout_row_height(self, value: int) -> None:
        """
        Grid Layout Row Height
        ======================

        Set the height of the rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_row_height', 'int', value)

        self._grid_layout_row_height = value

    @property
    def grid_layout_adjust_column_widths(self) -> dict[int, int]:
        """
        Grid Layout Adjust Column Widths
        ================================

        Get or set the widths of the columns in the grid layout.

        Returns
        -------
            dict[int, int]:
                The widths of the columns in the grid layout.

        Set
        ---
            grid_layout_adjust_column_widths (dict[int, int]):
                The widths of the columns in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not a dict.

        Examples
        --------
            ```
            # Get grid layout adjust column widths
            print(window.grid_layout_adjust_column_widths)

            # Set grid layout adjust column widths
            window.grid_layout_adjust_column_widths = {0: 200, 1: 200}
            ```
        """

        return self._grid_layout_adjust_column_widths

    @grid_layout_adjust_column_widths.setter
    def grid_layout_adjust_column_widths(self, value: dict[int, int]) -> None:
        """
        Grid Layout Adjust Column Widths
        ===============================

        Set the widths of the columns in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_adjust_column_widths', 'dict', value)

        self._grid_layout_adjust_column_widths = value

    @property
    def grid_layout_adjust_row_heights(self) -> dict[int, int]:
        """
        Grid Layout Adjust Row Heights
        ==============================

        Get or set the heights of the rows in the grid layout.

        Returns
        -------
            dict[int, int]:
                The heights of the rows in the grid layout.

        Set
        ---
            grid_layout_adjust_row_heights (dict[int, int]):
                The heights of the rows in the grid layout.

        Raises
        ------
            TypeError:
                If the provided `value` is not a dict.

        Examples
        --------
            ```
            # Get grid layout adjust row heights
            print(window.grid_layout_adjust_row_heights)

            # Set grid layout adjust row heights
            window.grid_layout_adjust_row_heights = {0: 200, 1: 200}
            ```
        """

        return self._grid_layout_adjust_row_heights

    @grid_layout_adjust_row_heights.setter
    def grid_layout_adjust_row_heights(self, value: dict[int, int]) -> None:
        """
        Grid Layout Adjust Row Heights
        ==============================

        Set the heights of the rows in the grid layout.
        """

        # Validate Argument
        if not isinstance(value, dict):
            pyflame.raise_type_error('PyFlameWindow', 'grid_layout_adjust_row_heights', 'dict', value)

        self._grid_layout_adjust_row_heights = value

    @property
    def window_margins(self) -> tuple[int, int, int, int]:
        """
        Window Margins
        =====================

        Get or set the margin in pixels around the main content area.

        Returns
        -------
            tuple[int, int, int, int]:
                Margins as (left, top, right, bottom).

        Set
        ---
            window_margins (int | tuple[int, int, int, int]):
                A single int (same value for all sides) or a tuple of four ints (left, top, right, bottom).

        Raises
        ------
            TypeError:
                If the provided `value` is not an int or a tuple of four ints.

        Examples
        --------
            ```
            # Get window margins (always returns tuple of four ints)
            left, top, right, bottom = window.window_margins

            # Set with single int (same for all sides)
            window.window_margins = 20

            # Set with tuple (left, top, right, bottom)
            window.window_margins = (10, 15, 10, 15)
            ```
        """

        return self.window_margins_value

    @window_margins.setter
    def window_margins(self, value: int | tuple[int, int, int, int]) -> None:
        """
        Window Margins
        ==============

        Set the margin in pixels around the main content area.
        """

        # Validate Argument and normalize to (left, top, right, bottom)
        margins: tuple[int, int, int, int]
        if isinstance(value, int):
            margins = (value, value, value, value)
        elif isinstance(value, tuple) and len(value) == 4:
            if not all(isinstance(v, int) for v in value):
                pyflame.raise_type_error('PyFlameWindow', 'window_margins', 'tuple of 4 ints (left, top, right, bottom)', value)
                return
            margins = value
        else:
            pyflame.raise_type_error('PyFlameWindow', 'window_margins', 'int or tuple of 4 ints (left, top, right, bottom)', value)
            return

        self.window_margins_value = margins
        self.main_vbox2.setContentsMargins(
            pyflame.gui_resize(margins[0]),
            pyflame.gui_resize(margins[1]),
            pyflame.gui_resize(margins[2]),
            pyflame.gui_resize(margins[3]),
            )

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def center_window(self) -> None:
        """
        Center Window
        =============

        Center the window on the screen.
        """

        # Get Current Screen Resolution
        main_window_res = pyflame.window_resolution()
        resolution = main_window_res.screenGeometry()

        # Get window size
        window_size = self.size()

        # Calculate center position
        x = (resolution.width() - window_size.width()) // 2
        y = (resolution.height() - window_size.height()) // 2

        # Move window to center
        self.move(x, y)

    def print(self, message: str) -> None:
        """
        Print
        =====

        Print message to message bar.

        Args
        ----
            `message` (str):
                Message to print.

        Examples
        --------
            ```
            # Print message to message bar
            window.print('This is a message')
            ```
        """

        # Print to window message bar
        self.message_bar_text = message

        # Print to terminal and flame message area
        pyflame.print(message, new_line=False)

    #-------------------------------------
    # [Stylesheet]
    #-------------------------------------

    def _set_stylesheet(self) -> None:
        """
        Set Stylesheet
        ==============
        """

        self.setStyleSheet(f"""
            QWidget{{
                background-color: rgb(36, 36, 36);
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

        Handle Return/Enter and Escape key events.
        """
        if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
            if self.return_pressed is not None:
                self.return_pressed()
                return  # Don't pass to parent if handled

        elif event.key() == QtCore.Qt.Key_Escape:
            if self.escape_pressed is not None:
                self.escape_pressed()
                return  # Don't pass to parent if handled

    def paintEvent(self, event):
        """
        Paint Event
        ===========

        Adds colored line to the left edge of the window.
        """

        painter = QtGui.QPainter(self)
        # Get the RGB string from parent's line_color
        rgb_str = self.line_color.value
        # Extract RGB values using string manipulation
        rgb_values = rgb_str.strip('rgb()').split(',')
        r, g, b = map(int, rgb_values)
        # Create QColor with the RGB values
        color = QtGui.QColor(r, g, b)
        painter.setPen(QtGui.QPen(color, pyflame.gui_resize(2)))
        painter.drawLine(0, 0, 0, 5000)

# ==============================================================================
# [PyFlame Window Classes]
# ==============================================================================

class PyFlameInputDialog:
    """
    PyFlameInputDialog
    ==================

    Custom QT Flame Input Dialog

    Simple dialog window that prompts the user for text input and provides options to confirm or cancel.

    The result is returned through the `text` property.

    When ok is pressed, the text is returned through the `text` property.
    When cancel is pressed, None is returned through the `text` property.

    Internal properties and methods are not intended to be used outside of the class.

    Args
    ----
        `parent` (PyFlameWindow | None):
            This windows parent window. Set to `None` if no parent window.

        `text` (str, optional):
            Input entry text.
            (Default: `""`)

        `label_text` (str, optional):
            Text displayed above input entry field.
            (Default: `Enter New Value`)

        `title` (str, optional):
            Custom title for the dialog window.
            (Default: `User Input`)

        `title_style` (Style, optional):
            The style of the title text using the Style Enum.
            (Default: `Style.BACKGROUND`)

        `title_align` (Align, optional):
            The alignment of the title text using the Align Enum.
            (Default: `None`)

        `line_color` (Color, optional):
            The color of the line using the Color Enum.
            (Default: `Color.BLUE`)

        `message_bar` (bool):
            Enable message bar at bottom of window.
            (Default: `False`)

    Properties
    ----------
        `text` (str):
            Get or set input entry text.
            (Default: `""`)

        `message_bar_text` (str):
            Get or set text in message bar.
            (Default: `""`)

        'label_text` (str):
            Get or set entry label text. Displayed above entry.
            (Default: `"Enter New Value"`)

        `title` (str):
            Get or set window title.
            (Default: `"User Input"`)

        `title_style` (Style):
            Get or set style applied to window title.
            (Default: `Style.BACKGROUND_THIN`)

        `line_color` (Color):
            Get or set window line color.
            (Default: `Color.BLUE`)

    Example
    -------
        ```
        # Create Input Dialog
        input_dialog = PyFlameInputDialog(
            text="Mike",
            label_text="Enter your name:",
            )

        # Get Input Dialog Text
        if input_dialog.text is not None:
            print("User input:", input_dialog.text)
        else:
            print("User canceled.")
        ```
    """

    def __init__(self: 'PyFlameInputDialog',
                 parent: PyFlameWindow | None,
                 text: str='',
                 label_text: str='Enter New Value',
                 title: str='User Input',
                 title_style: Style=Style.BACKGROUND_THIN,
                 title_align: Align | None=None,
                 line_color: Color=Color.BLUE,
                 message_bar: bool=False,
                 ):

        # Validate Parent
        if not isinstance(parent, (type(None), PyFlameWindow)):
            pyflame.raise_type_error('PyFlameInputWindow', 'parent', 'PyFlameWindow | None', parent)

        # Print to Terminal/Shell
        print(
            f'{TextColor.BLUE.value}' + # Set Text Color
            '=' * 80 + '\n' +
            f'User Input: {TextColor.WHITE.value}{SCRIPT_NAME.upper()}{TextColor.BLUE.value}' + '\n' +
            '=' * 80 + '\n\n' +
            f'{TextColor.RESET.value}'  # Reset Text Color
            )

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.input_window = PyFlameWindow(
            return_pressed=self._confirm,
            escape_pressed=self._cancel,
            grid_layout_columns=4,
            grid_layout_rows=3,
            grid_layout_column_width=110,
            message_bar=message_bar,
            parent=parent,
            )

        # Label
        self.input_label = PyFlameLabel(
            style=Style.UNDERLINE,
            )

        # Entry
        self.input_entry = PyFlameEntry()

        # Buttons
        self.ok_button = PyFlameButton(
            text='Ok',
            connect=self._confirm,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self._cancel,
            )

        self.input_window.grid_layout.addWidget(self.input_label, 0, 0, 1, 4)
        self.input_window.grid_layout.addWidget(self.input_entry, 1, 0, 1, 4)
        self.input_window.grid_layout.addWidget(self.cancel_button, 3, 2)
        self.input_window.grid_layout.addWidget(self.ok_button, 3, 3)

        #-------------------------------------

        # Set Properties
        self.text = text
        self.label_text = label_text
        self.title = title
        self.title_style = title_style
        self.title_align = title_align
        self.line_color = line_color

        # Set Input Entry Focus
        self.input_entry.set_focus()

        self.input_window.exec_()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text(self) -> str | None:
        """
        Text
        ====

        Get or set the text in the Input Dialog's entry field.

        Returns
        -------
            Text entered by the user if OK was pressed,
            otherwise returns `None`.

        Set
        ---
            `value` (str):
                Sets the initial text in the input entry field.

        Raises
        ------
            TypeError:
                If `value` is not a string when setting.

        Examples
        --------
            ```
            dialog = SimpleInputDialog()
            dialog.text = 'Default Value'  # Set initial text

            result = dialog.text           # Show dialog and get input
            if result is not None:
                print('User input:', result)
            else:
                print('User canceled.')
            ```
        """

        return self._input_text

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set the Input Dialog input entry Text
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameInputDialog', 'text', 'str', value)

        self.input_entry.text = value

    @property
    def message_bar_text(self) -> str:
        """
        Message Bar Text
        ================

        Get or set the text of the message bar.

        Returns
        -------
            str:
                The text of the message bar.

        Set
        ---
        message_bar_text (str):
            The text of the message bar.

        Examples
        --------
            ```
            # Get message bar text
            print(input_window.message_bar_text)

            # Set message bar text
            input_window.message_bar_text = 'This is a message bar text'
            ```
        """

        return self.input_window.message_bar_text

    @message_bar_text.setter
    def message_bar_text(self, value: str) -> None:
        """
        Message Bar Text
        ================

        Set the text of the message bar.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameInputWindow', 'message_bar_text', 'str', value)

        # Set Message Bar Text
        self.input_window.message_bar_text = value

        #Pause QT briefly to allow the message bar to update
        pyflame.pause()

    @property
    def label_text(self) -> str:
        """
        Label Text
        ==========

        Get or set Input Dialog input label Text.

        Returns
        -------
            `str`:
                Label text

        Set
        ---
            `value` (str):
                Text to be used as input label Text.

        Raises
        ------
            TypeError:
                If `value` is not a string.

        Examples
        --------
            ```
            # Get Input Dialog input label Text
            print(window._label_text)

            # Set window title
            window._label_text = 'Enter Input'
            ```
        """

        return self.input_label.text

    @label_text.setter
    def label_text(self, value: str) -> None:
        """
        Label Text
        ==========

        Set the Input Dialog input label Text
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameInputDialog', 'label_text', 'str', value)

        self.input_label.text = value

    @property
    def title(self) -> str:
        """
        Title
        =====

        Get or set Input Dialog window Title.

        Returns
        -------
            `str`:
                Window Title

        Set
        ---
            `value` (str):
                Text to be used as window Title.

        Raises
        ------
            TypeError:
                If `value` is not a string.

        Examples
        --------
            ```
            # Get window title
            print(window.title)

            # Set window title
            window.title = 'Some Input Window'
            ```
        """

        return self.input_window.title

    @title.setter
    def title(self, value: str) -> None:
        """
        Title
        =====

        Set the Input Dialog window title
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameInputDialog', 'title', 'str', value)

        self.input_window.title = value

    @property
    def title_style(self) -> Style:
        """
        Title Style
        ===========

        Get or set the style to be used for the Input Dialog window tite.

        Must be a Style Enum.

        Returns
        -------
            `Style`: A Style enum value representing the title style.

        Set
        ---
            `value` (Style):
                Style to be applied to the window title.
                Must be a Style Enum.

        Raises
        ------
            TypeError:
                If `value` is not a Style enum.

        Examples
        --------
            ```
            # Get title style
            print(window.title_style)

            # Set title style
            window.title_style = Style.BACKGROUND_THIN
        """

        return self.input_window.title_style

    @title_style.setter
    def title_style(self, value: Style) -> None:
        """
        Title Style
        ===========

        Set the Input Dialog window title style
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlameInputDialog', 'title_style', 'Style Enum', value)

        self.input_window.title_style = value

    @property
    def title_align(self) -> Align | None:
        """
        Title Align
        ===========

        Get or set the alignment of the title text.

        Returns
        -------
            `Align | None`:
                Alignment of the title text.

        Set
        ---
            `value` (Align | None):
                Alignment of the title text.

        Raises
        ------
            TypeError:
                If the provided `value` is not Align | None.

        Examples
        --------
            ```
            # Get title alignment
            print(window.title_align)

            # Set title alignment
            window.title_align = Align.CENTER
            ```
        """

        return self.input_window.title_align

    @title_align.setter
    def title_align(self, value: Align | None) -> None:
        """
        Title Align
        ===========

        Set the alignment of the title text.
        """

        if value is not None and not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameInputDialog', 'title_align', 'Align Enum | None', value)

        if value is not None:
            self.input_window.title_align = value

    @property
    def line_color(self) -> Color:
        """
        Line Color
        ==========

        Get or set the line color for the side of the Input Dialog window.

        Returns
        -------
            `Color`: A Color enum value representing the line color.

        Set
        ---
            `value` (Color):
                Color to be applied to the window line.
                Must be a Color Enum.

        Raises
        ------
            TypeError:
                If `value` is not a Color enum.

        Examples
        --------
            ```
            # Get line Color
            print(window.line_color)

            # Set line Color
            window.line_color = Color.RED
            ```
        """

        return self.input_window.line_color

    @line_color.setter
    def line_color(self, value: Color) -> None:
        """
        Line Color
        ==========

        Set the line Color for the side of the Input Dialog window.
        """

        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameInputDialog', 'line_color', 'Color Enum', value)

        self.input_window.line_color

    #-------------------------------------
    # [Internal Methods]
    #-------------------------------------

    def _confirm(self) -> None:
        """
        Confirm
        =======

        Called when the user presses OK. Stores the input and sets `self.confirm = True`.
        """

        self._input_text = self.input_entry.text
        self.input_window.close()

    def _cancel(self) -> None:
        """
        Cancel
        ======

        Called when the user presses Cancel. Sets `self.confirm = False`.
        """

        self._input_text = None
        self.input_window.close()

        pyflame.print('Input Cancelled', text_color=TextColor.RED)

class PyFlameMessageWindow:
    """
    PyFlameMessageWindow
    ====================

    Custom QT Flame Message Window.

    Message window to display various types of messages.

    Args
    ----
        `parent` (PyFlameWindow | None):
            This windows parent window. Set to `None` if no parent window.

        `message` (str):
            Text displayed in the body of the window.

        `message_type` (MessageType):
            Type of message window to be shown. Message types set defaults for title, title_style, title_align, and line_color.
            All of these can be overridden by providing values for the respective keyword arguments.
            (Default: `MessageType.INFO`)

            Message Types
                `MessageType.INFO`
                    Title: SCRIPT_NAME
                    Window lines: Blue
                    Buttons: Ok
                `MessageType.OPERATION_COMPLETE`
                    Title: SCRIPT_NAME: Operation Complete
                    Window lines: Blue
                    Buttons: Ok
                `MessageType.CONFIRM`
                    Title: SCRIPT_NAME: Confirm Operation
                    Window lines: Grey
                    Buttons: Confirm, Cancel
                    Returns bool value.
                `MessageType.ERROR`
                    Title: SCRIPT_NAME: Error
                    Window lines: Yellow
                    Buttons: Ok
                `MessageType.WARNING`
                    Title: SCRIPT_NAME: Warning
                    Window lines: Red
                    Buttons: Confirm, Cancel
                    Returns bool value.

        `title` (str, optional):
            Use to override default title for `message_type`. Providing a value will override the default title for the `message_type`.
            (Default: ``)

        `title_style` (Style, optional):
            Style of title text. Alignment of text from `title_style` can be overridden by providing `title_align` value.
            (Default: `Style.BACKGROUND_THIN`)

            Style Options
                `Style.NORMAL`: Plain text, left aligned.
                `Style.UNDERLINE`: Underlined text, centered.
                `Style.BORDER`: Border text, centered.
                `Style.BACKGROUND`: Text background is darker, left aligned.
                `Style.BACKGROUND_THIN`: Text background is darker, left aligned, thin font.

        `title_align` (Align, optional):
            Alignment of title text. Providing a value will override the default alignment for the `title_style`.
            (Default: `Align.LEFT`)

            Align Options
                `Align.LEFT`: Left aligned.
                `Align.CENTER`: Centered.
                `Align.RIGHT`: Right aligned.

        `line_color` (WindowBarColor):
            Color of bar on left side of window. Providing a value will override the default color for the `message_type`.
            (Default: `Color.BLUE`)

            Color Options
                `Color.GRAY`: Gray line.
                `Color.BLUE`: Blue line.
                `Color.RED`: Red line.
                `Color.GREEN`: Green line.
                `Color.YELLOW`: Yellow line.
                `Color.TEAL`: Teal line.

        `message_bar` (bool):
            Enable message bar at bottom of window.
            (Default: `False`)

        `duration` (int):
            Time in seconds to display message in flame message area.
            (Default: `5`)

    Properties
    ----------
        `message` (str):
            Get or set the message text in the window.
            (Default: `""`)

        `message_type` (MessageType):
            Get or set the type of message using the MessageType Enum.
            (Default: `MessageType.INFO`)

        `title` (str):
            Get or set the title of the progress window.
            (Default: `""`)

        `title_style` (Style):
            Get or set the title style of the progress window.
            (Default: `Style.BACKGROUND_THIN`)

        `title_align` (Align):
            Get or set the title alignment of the progress window.
            (Default: `Align.LEFT`)

        `line_color` (Color):
            Get or set the line color of the progress window.
            (Default: `Color.BLUE`)

        `message_bar_text` (str):
            Get or set text in message bar.
            (Default: `""`)

        `duration` (int):
            Get or set the amount of time to display the message in the Flame message area.
            (Default: `5`)

        `confirmed` (bool):
            Get or set the confirmed status of the message.

    Returns
    -------
        bool: True if confirm button is pressed, False if cancel button is pressed.
              A bool value is only returned for `MessageType.CONFIRM` and `MessageType.WARNING`.

    Examples
    --------
        Example for an error message:
        ```
        PyFlameMessageWindow(
            message=('File not found.'),
            message_type=MessageType.ERROR,
            parent=None
            )
        ```

        Example for a confirmation message, returns a bool:
        ```
        proceed = PyFlameMessageWindow(
            message='Do you want to do this?',
            message_type=MessageType.CONFIRM,
            parent=None,
            )
        ```
    """

    def __init__(self: 'PyFlameMessageWindow',
                 parent: PyFlameWindow | None,
                 message: str='',
                 message_type: MessageType=MessageType.INFO,
                 title: str='',
                 title_style: Style=Style.BACKGROUND_THIN,
                 title_align: Align | None=None,
                 line_color: Color | None=None,
                 message_bar=False,
                 duration: int=5,
                 ) -> None:

        # Validate Arguments
        if not isinstance(parent, (type(None), PyFlameWindow)):
            pyflame.raise_type_error('PyFlameMessageWindow', 'parent', 'PyFlameWindow | None', parent)
        if not isinstance(message, str):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message', 'str', message)
        if not isinstance(message_type, MessageType):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message_type', 'MessageType Enum', message_type)
        if not isinstance(title, str):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title', 'str', title)
        if not isinstance(title_style, Style):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title_style', 'Style Enum', title_style)
        if title_align is not None and not isinstance(title_align, Align):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title_align', 'Align Enum | None', title_align)
        if line_color is not None and not isinstance(line_color, Color):
            pyflame.raise_type_error('PyFlameMessageWindow', 'line_color', 'Color Enum | None', line_color)
        if not isinstance(message_bar, bool):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message_bar', 'bool', message_bar)
        if not isinstance(duration, int):
            pyflame.raise_type_error('PyFlameMessageWindow', 'duration', 'int', duration)

        self.confirmed = False

        #-------------------------------------
        # [Build Message Window]
        #-------------------------------------

        self.message_window = PyFlameWindow(
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=110,
            message_bar=message_bar,
            parent=parent,
            )

        self.message_window_text_edit = PyFlameTextEdit(
            text_style=TextStyle.UNSELECTABLE,
            )

        self.ok_button = PyFlameButton(
            text='Ok',
            connect=self.confirm,
            width=110,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.cancel,
            )
        self.confirm_button = PyFlameButton(
            text='Confirm',
            connect=self.confirm,
            color=Color.BLUE,
            )

        if message_type == MessageType.WARNING:
            self.confirm_button.color = Color.RED

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.message_window.grid_layout.addWidget(self.message_window_text_edit, 0, 0, 6, 4)

        # If message type is confirm or warning, add cancel and confirm buttons otherwise just add ok button
        if message_type == MessageType.CONFIRM or message_type == MessageType.WARNING:
            self.message_window.grid_layout.addWidget(self.cancel_button, 7, 2)
            self.message_window.grid_layout.addWidget(self.confirm_button, 7, 3)
        else:
            self.message_window.grid_layout.addWidget(self.ok_button, 7, 3)

        #-------------------------------------
        # [Set Window Properties]
        #-------------------------------------

        self.message = message
        self.message_type = message_type
        self.title = title
        self.title_style = title_style
        self.title_align = title_align
        self.line_color = line_color
        self.duration = duration

        # Print message to terminal and Flame's console area
        self._message_print(self.message, self.title, self.duration)

        # Show message window and wait for user to close it
        self.message_window.exec_()

    def __bool__(self):
        return self.confirmed

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def message(self):
        """
        Message
        =======

        Get or set message text.

        Returns
        -------
            `str`:
                Message text.

        Set
        ---
            `value` (str):
                Message text.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get message text
            print(message_window.title)

            # Set message text
            message_window.title = 'Message Window'
            ```
        """

        return self.message_window_text_edit.text

    @message.setter
    def message(self, value: str) -> None:
        """
        Message
        =======

        Set the message text.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message', 'str', value)

        # Set message window text
        self.message_window_text_edit.text = value

    @property
    def message_type(self):
        """
        Message Type
        ============

        Get or set type of message.

        MessageType Options
        -------------------
            - `MessageType.INFO`
            - `MessageType.OPERATION_COMPLETE`
            - `MessageType.CONFIRM`
            - `MessageType.ERROR`
            - `MessageType.WARNING`

        Returns
        -------
            `MessageType`:
                Message type as MessageType enum.

        Set
        ---
            `value` (MessageType):
                Message type as MessageType enum.

        Raises
        ------
            TypeError:
                If the provided `value` is not a MessageType enum.

        Examples
        --------
            ```
            # Get message type
            print(message_window.message_type)

            # Set message text
            message_window.message_type = MessageType.CONFIRM
            ```
        """

        return self._message_type

    @message_type.setter
    def message_type(self, value: MessageType) -> None:
        """
        Message Type
        ============

        Set the MessageType.
        """

        # Validate Argument
        if not isinstance(value, MessageType):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message_type', 'MessageType', value)

        # Set message window text
        self._message_type = value

    @property
    def title(self) -> str:
        """
        Title
        =====

        Get or set Message Window title.

        Returns
        -------
            `str`:
                Message Window title.

        Set
        ---
            `value` (str):
                Message Window title.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get title text
            print(message_window.title)

            # Set title style
            message_window.title = 'Message Window'
            ```
        """

        return self.message_window.title

    @title.setter
    def title(self, value: str) -> None:
        """
        Title
        =====

        Set the message window title.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title', 'str', value)

        # Set default title if empty
        if value == '':
            if self.message_type == MessageType.INFO:
                value = SCRIPT_NAME
            elif self.message_type == MessageType.OPERATION_COMPLETE:
                value = f'{SCRIPT_NAME}: Operation Complete'
            elif self.message_type == MessageType.ERROR:
                value = f'{SCRIPT_NAME}: Error'
            elif self.message_type == MessageType.CONFIRM:
                value = f'{SCRIPT_NAME}: Confirm Operation'
            elif self.message_type == MessageType.WARNING:
                value = f'{SCRIPT_NAME}: Warning'
            self.message_window.title = value
        else:
            self.message_window.title = value

    @property
    def title_style(self) -> Style:
        """
        Title Style
        ============

        Get or set the message window title style.

        Returns
        -------
            `Style`:
                Message window title style.

        Set
        ---
            `value` (Style):
                Message window title style.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Style.

        Examples
        --------
            ```
            # Get title style
            print(message_window.title_style)

            # Set title style
            message_window.title_style = Style.UNDERLINE
            ```
        """

        return self.message_window.title_style

    @title_style.setter
    def title_style(self, value: Style) -> None:
        """
        Title Style
        ============

        Set the message window title style.
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title_style', 'Style Enum', value)

        self.message_window.title_style = value

    @property
    def title_align(self) -> Align | None:
        """
        Title Align
        ============

        Get or set the message window title alignment.

        Returns
        -------
            `Align`:
                Message window title alignment.

        Set
        ---
            `value` (Align | None):
                Message window title alignment.

        Raises
        ------
            TypeError:
                If the provided `value` is not Align | None.

        Examples
        --------
            ```
            # Get title alignment
            print(message_window.title_align)

            # Set title alignment
            message_window.title_align = Align.CENTER
            ```
        """

        return self.message_window.title_align

    @title_align.setter
    def title_align(self, value: Align | None) -> None:
        """
        Title Align
        ============

        Set the message window title alignment.
        """

        # Validate Argument
        if value is not None and not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameMessageWindow', 'title_align', 'Align Enum | None', value)

        if value is not None:
            self.message_window.title_align = value

    @property
    def line_color(self) -> Color | None:
        """
        Line Color
        ==========

        Get or set the message window line color as Color Enum.

        If None is passed, default colors will be applied according to the MessageType set in message_type property.

        If a Color is passed, the message window line color will be set to the Color passed.

        Returns
        -------
            `Color | None`:
                Message window line color.

        Set
        ---
            `value` (Color | None):
                Message window line color.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color | None.

        Examples
        --------
            ```
            # Get window line color
            print(message_window.line_color)

            # Set window line color
            message_window.line_color = Color.BLUE
            ```
        """

        return self.message_window.line_color

    @line_color.setter
    def line_color(self, value: Color | None) -> None:
        """
        Line Color
        ==========

        Set the message window line color.
        """

        # Validate Argument
        if value is not None and not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameMessageWindow', 'line_color', 'Color Enum | None', value)

        # Resolve line color from message type when value is None
        resolved_color = value
        if resolved_color is None:
            if self.message_type == MessageType.INFO:
                resolved_color = Color.BLUE
            elif self.message_type == MessageType.OPERATION_COMPLETE:
                resolved_color = Color.BLUE
            elif self.message_type == MessageType.ERROR:
                resolved_color = Color.YELLOW
            elif self.message_type == MessageType.CONFIRM:
                resolved_color = Color.BLUE
            elif self.message_type == MessageType.WARNING:
                resolved_color = Color.RED
            else:
                # Fallback for unexpected enum values
                resolved_color = Color.BLUE

        self.message_window.line_color = resolved_color

    @property
    def message_bar_text(self) -> str:
        """
        Message Bar Text
        ================

        Get or set the text of the message bar.

        Returns
        -------
            str:
                The text of the message bar.

        Set
        ---
        message_bar_text (str):
            The text of the message bar.

        Examples
        --------
            ```
            # Get message bar text
            print(message_window.message_bar_text)

            # Set message bar text
            message_window.message_bar_text = 'This is a message bar text'
            ```
        """

        return self.message_window.message_bar_text

    @message_bar_text.setter
    def message_bar_text(self, value: str) -> None:
        """
        Message Bar Text
        ================

        Set the text of the message bar.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameMessageWindow', 'message_bar_text', 'str', value)

        # Set Message Bar Text
        self.message_window.message_bar_text = value

        #Pause QT briefly to allow the message bar to update
        pyflame.pause()

    @property
    def duration(self) -> int:
        """
        Duration
        ========

        Get or set the duration in seconds the message will show in the Flame Message Area.

        Returns
        -------
            `int`:
                Duration of message in seconds.

        Set
        ---
            `value` (int):
                Duration of message in seconds.

        Raises
        ------
            TypeError:
                If the provided `value` is not an `int`.

        Examples
        --------
            ```
            # Get message duration
            print(message_window.duration)

            # Set message duration
            message_window.duration = 5
            ```
        """

        return self._duration

    @duration.setter
    def duration(self, value: int) -> None:
        """
        Title Style
        ============

        Set the duration of the message in the Flame Message Area.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameMessageWindow', 'duration', 'int', value)

        self._duration = value

    @property
    def confirmed(self) -> bool:
        """
        Confirmed
        =========

        Get or set the confirmed status of the message.
        """

        return self._confirmed

    @confirmed.setter
    def confirmed(self, value: bool) -> None:
        """
        Set the confirmed status of the message.
        """

        # Validate Argument
        if not isinstance(value, bool):
            pyflame.raise_type_error('PyFlameMessageWindow', 'confirmed', 'bool', value)

        self._confirmed = value

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def _message_print(self, message: str, title: str, duration: int):
        """
        Print
        =====

        Print message to the terminal/shell and Flame's console area.
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
        if self.message_type == MessageType.INFO or self.message_type == MessageType.OPERATION_COMPLETE or self.message_type == MessageType.CONFIRM:
            print_message(TextColor.BLUE.value, 'Info', message)
        elif self.message_type == MessageType.WARNING:
            print_message(TextColor.RED.value, 'Warning', message)
        elif self.message_type == MessageType.ERROR:
            print_message(TextColor.YELLOW.value, 'Error', message)

        # Print message to the Flame message area
        # Warning and error intentionally swapped to match color of message window
        title = title.upper()

        if self.message_type == MessageType.INFO or self.message_type == MessageType.OPERATION_COMPLETE or self.message_type == MessageType.CONFIRM:
            flame.messages.show_in_console(f'{title}: {message}', 'info', duration)
        elif self.message_type == MessageType.ERROR:
            flame.messages.show_in_console(f'{title}: {message}', 'warning', duration)
        elif self.message_type == MessageType.WARNING:
            flame.messages.show_in_console(f'{title}: {message}', 'error', duration)

    def cancel(self) -> None:
        """
        Cancel
        ======

        Cancel the message.
        """

        self.message_window.close()
        self.confirmed = False

        pyflame.print('Operation Cancelled', text_color=TextColor.RED)

    def confirm(self) -> None:
        """
        Confirm
        =======

        Confirm the message.
        """

        self.message_window.close()
        self.confirmed = True
        if self.message_type == MessageType.CONFIRM or self.message_type == MessageType.WARNING:
            pyflame.print('Operation Confirmed', text_color=TextColor.GREEN)

    def close(self) -> None:
        """
        Close
        =====

        Close the message window.
        """

        self.message_window.close()

class PyFlamePasswordWindow:
    """
    PyFlamePasswordWindow
    =====================

    Custom Qt Flame Password Window.

    This class provides a custom dialog window for entering a password(system password) or a username and password.

    When prompting only for a password, the password is assumed to be for a system account and will test the password
    using sudo.

    Set `user_name_prompt` to True to prompt for a username and password. Username and password are not used
    for system password testing.

    Args
    ----
        `parent` (PyFlameWindow | None):
            This windows parent window. Set to `None` if no parent window.

        `text` (str):
            The text to be displayed in the window.
            The default text of either `'Enter system password'` or `'Enter username and password'` will be used based
            on `user_name_prompt` argument.
            (Default: `'Enter system password'`)

        `user_name_prompt` (bool):
            If set to True, the window will prompt for both username and password.
            (Default: `False`)

        `title` (str, optional):
            The title text shown in the top left of the window.
            The default title of either `'Enter Password'` or `'Enter Username and Password'` will be used based on
            `user_name_prompt` argument.
            (Default: `'Enter System Password'`)

        `title_style` (Style, optional):
            The style of the title text.
            (Default: `Style.BACKGROUND_THIN`)

        `title_align` (Align, optional):
            The alignment of the title text. Use to override the default alignment set by `title_style`.
            (Default: `None`)

        `line_color` (Color, optional):
            The color of the line on the side of the window. Use to override the default line color(Color.BLUE).
            (Default: `None`)

        `message_bar` (bool):
            Enable message bar at bottom of window.
            (Default: `False`)

    Properties
    ----------
        `text` (str):
            Get or set the text of the password window.
            (Default: `'Enter System Password'`)

        `title` (str):
            Get or set the title of the password window.
            (Default: `'Enter System Password'`)

        `user_name_prompt` (bool):
            Get or set the user name prompt of the password window.
            (Default: `False`)

        `title_style` (Style):
            Get or set the title style of the password window.
            (Default: `Style.BACKGROUND_THIN`)

        `title_align` (Align):
            Get or set the title alignment of the password window.
            (Default: `None`)

        `line_color` (Color):
            Get or set the line color of the password window.
            (Default: `None`)

        `message_bar_text` (str):
            Get or set text in message bar.
            (Default: `""`)

        `password` (str):
            Get or set the password of the password window.
            (Default: `None`)

        `username` (str):
            Get or set the username of the password window.
            (Default: `None`)

    Private Methods
    ---------------
        `_test_password` -> str | None:
            Test the password value as sudo and close the window. If the password is incorrect,
            the user will be prompted to try again.

        `_confirm` -> None:
            Confirm the password and close the window. If username and password are provided,
            the password will not be tested as sudo.

        `_cancel` -> None:
            Close the window.

    Examples
    --------
        For a password prompt only:
        ```
        password_window = PyFlamePasswordWindow()

        # Get password
        password = password_window.password
        ```

        For a username and password prompt:
        ```
        password_window = PyFlamePasswordWindow(
            user_name_prompt=True,
            )

        # Get username and password
        username = password_window.username
        password = password_window.password
        ```
    """

    def __init__(self,
                 parent: PyFlameWindow | None,
                 text: str='Enter System Password',
                 user_name_prompt: bool=False,
                 title: str='Enter System Password',
                 title_style: Style=Style.BACKGROUND_THIN,
                 title_align: Align | None=None,
                 line_color: Color | None=None,
                 message_bar: bool=False,
                 ):

        # Validate Parent
        if not isinstance(parent, (type(None), PyFlameWindow)):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'parent', 'PyFlameWindow | None', parent)

        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{title}' + '\n' +
            '=' * 80 + '\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

        # Set Default Window Title if not provided
        if not title and user_name_prompt:
            title = 'Enter Username and Password'
        elif not title and not user_name_prompt:
            title = 'Enter System Password'

        # Set Default Window Text if not provided
        if not text and user_name_prompt:
            text = 'Enter username and password.'
        elif not text and not user_name_prompt:
            text = 'Enter system password.'

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.password_window = PyFlameWindow(
            return_pressed=self._confirm,
            escape_pressed=self._cancel,
            grid_layout_columns=4,
            grid_layout_rows=6,
            grid_layout_column_width=110,
            message_bar=message_bar,
            parent=parent,
            )

        self.password_label = PyFlameLabel(
            text='Password',
            )
        self.user_name_label = PyFlameLabel(
            text='Username',
            )

        self.password_text_edit = PyFlameTextEdit(
            text_style=TextStyle.UNSELECTABLE,
            )

        self.password_entry = PyFlameEntry(
            password_echo=True,
            )
        self.user_name_entry = PyFlameEntry()

        self.confirm_button = PyFlameButton(
            text='Confirm',
            connect=self._confirm,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self._cancel,
            )

        #-------------------------------------
        # [Set Window Properties]
        #-------------------------------------

        self.password = None
        self._password = None
        self.username = None
        self._username = None
        self.text = text
        self.user_name_prompt = user_name_prompt
        self.title = title
        self.title_style = title_style
        self.title_align = title_align
        self.line_color = line_color

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.password_window.grid_layout.addWidget(self.password_text_edit, 0, 0, 3, 4)

        if user_name_prompt:
            self.password_window.grid_layout.addWidget(self.user_name_label, 3, 0)
            self.password_window.grid_layout.addWidget(self.user_name_entry, 3, 1, 1, 3)
            self.password_window.grid_layout.addWidget(self.password_label, 4, 0)
            self.password_window.grid_layout.addWidget(self.password_entry, 4, 1, 1, 3)
        else:
            self.password_window.grid_layout.addWidget(self.password_label, 3, 0)
            self.password_window.grid_layout.addWidget(self.password_entry, 3, 1, 1, 3)

        self.password_window.grid_layout.addWidget(self.cancel_button, 6, 2)
        self.password_window.grid_layout.addWidget(self.confirm_button, 6, 3)

        # Set entry focus and tab-key order
        if user_name_prompt:
            self.user_name_entry.set_focus()
            self.password_window.tab_order = [self.user_name_entry, self.password_entry]
        else:
            self.password_entry.set_focus()

        self.password_window.exec_()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text(self) -> str:
        """
        Text
        ====

        Get or set the text of the password window.

        Returns
        -------
            str:
                Text of the password window.

        Set
        ---
            `value` (str):
                Text of the password window.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get text
            print(password_window.text)

            # Set text
            password_window.text = 'Hello, world!'
            ```
        """

        return self.password_text_edit.text

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set the text of the password window.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'text', 'str', value)

        self.password_text_edit.text = value

    @property
    def title(self) -> str:
        """
        Title
        =====

        Get or set the Password window title.

        Returns
        -------
            str:
                Password window title.

        Set
        ---
            `value` (str):
                Password window title.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get title text
            print(password_window.title)

            # Set title style
            password_window.title = 'Password Window'
            ```
        """

        return self.password_window.title

    @title.setter
    def title(self, value: str) -> None:
        """
        Title
        =====

        Set the Password window title.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'title', 'str', value)

        self.password_window.title = value

    @property
    def title_style(self) -> Style:
        """
        Title Style
        ============

        Get or set the Password window title style.

        Returns
        -------
            `Style`:
                Password window title style.

        Set
        ---
            `value` (Style):
                Password window title style.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Style.

        Examples
        --------
            ```
            # Get title style
            print(password_window.title_style)

            # Set title style
            password_window.title_style = Style.UNDERLINE
            ```
        """

        return self.password_window.title_style

    @title_style.setter
    def title_style(self, value: Style) -> None:
        """
        Title Style
        ============

        Set the Password window title style.
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'title_style', 'Style Enum', value)

        self.password_window.title_style = value

    @property
    def title_align(self) -> Align | None:
        """
        Title Align
        ============

        Get or set the Password window title alignment.

        Returns
        -------
            `Align`:
                Password window title alignment.

        Set
        ---
            `value` (Align | None):
                Password window title alignment.

        Raises
        ------
            TypeError:
                If the provided `value` is not Align | None.

        Examples
        --------
            ```
            # Get title alignment
            print(password_window.title_align)

            # Set title alignment
            password_window.title_align = Align.CENTER
            ```
        """

        return self.password_window.title_align

    @title_align.setter
    def title_align(self, value: Align | None) -> None:
        """
        Title Align
        ============

        Set the Password window title alignment.
        """

        # Validate Argument
        if value is not None and not isinstance(value, Align):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'title_align', 'Align Enum | None', value)

        if value is not None:
            self.password_window.title_align = value

    @property
    def line_color(self) -> Color | None:
        """
        Line Color
        ==========

        Get or set the Password window line color as Color Enum.

        Returns
        -------
            `Color | None`:
                Password window line color.

        Set
        ---
            `value` (Color | None):
                Password window line color as Color Enum.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color | None.

        Examples
        --------
            ```
            # Get window line color
            print(password_window.line_color)

            # Set window line color
            password_window.line_color = Color.BLUE
            ```
        """

        return self.password_window.line_color

    @line_color.setter
    def line_color(self, value: Color | None) -> None:
        """
        Line Color
        ==========

        Set the Password window line color.
        """

        # Validate Argument
        if value is not None and not isinstance(value, Color):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'line_color', 'Color Enum | None', value)

        if value is not None:
            self.password_window.line_color = value

    @property
    def message_bar_text(self) -> str:
        """
        Message Bar Text
        ================

        Get or set the text of the message bar.

        Returns
        -------
            str:
                The text of the message bar.

        Set
        ---
        message_bar_text (str):
            The text of the message bar.

        Examples
        --------
            ```
            # Get message bar text
            print(password_window.message_bar_text)

            # Set message bar text
            password_window.message_bar_text = 'This is a message bar text'
            ```
        """

        return self.password_window.message_bar_text

    @message_bar_text.setter
    def message_bar_text(self, value: str) -> None:
        """
        Message Bar Text
        ================

        Set the text of the message bar.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'message_bar_text', 'str', value)

        # Set Message Bar Text
        self.password_window.message_bar_text = value

        #Pause QT briefly to allow the message bar to update
        pyflame.pause()

    @property
    def password(self) -> str | None:
        """
        Password
        ========

        Get or set the password.

        Returns
        -------
            str:
                Password.

        Set
        ---
            `value` (str):
                Password.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get password
            print(password_window.password)

            # Set password
            password_window.password = '123456'
            ```
        """

        return self._password

    @password.setter
    def password(self, value: str | None=None) -> None:
        """
        Password
        ========

        Set the password.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'password', 'str | None', value)

        self._password = value

    @property
    def username(self) -> str | None:
        """
        Username
        ========

        Get or set the username.

        Returns
        -------
            str:
                Username

        Set
        ---
            `value` (str):
                Username

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get username
            print(password_window.username)

            # Set username
            password_window.username = 'user'
            ```
        """

        return self._user_name

    @username.setter
    def username(self, value: str | None=None) -> None:
        """
        User Name
        =========

        Set the username.
        """

        # Validate Argument
        if value is not None and not isinstance(value, str):
            pyflame.raise_type_error('PyFlamePasswordWindow', 'username', 'str | None', value)

        self._user_name = value

    #-------------------------------------
    # [Private Methods]
    #-------------------------------------

    def _test_password(self):
        """
        Test Password
        =============

        Test the password value and close the window. If the password is incorrect,
        the user will be prompted to try again.
        """

        password = self.password_entry.text

        if password:
            command = ['sudo', '-S', 'echo', 'Testing sudo password']
            try:
                # Run the command with sudo and pass the password through stdin
                process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
                output, error = process.communicate(input=password+'\n')

                if process.returncode == 0:
                    pyflame.print('Sudo password is correct.')
                    return password
                else:
                    pyflame.print('Sudo password is incorrect.')
                    self.password_text_edit.text = 'Password incorrect, try again.'
                    return None
            except Exception as e:
                pyflame.print(f'Error occurred while testing sudo password: {e}')
                self.password_text_edit.text = 'Error occurred while testing sudo password.'
                return None

    def _confirm(self):
        """
        Confirm
        =======

        Confirm the password and close the window.
        """

        if self.user_name_prompt:
            if not self.user_name_entry.text or self.user_name_entry.text == '':
                PyFlameMessageWindow(
                    message='Username is required. Please enter a username and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.password_window,
                    )
                return
            if not self.password_entry.text or self.password_entry.text == '':
                PyFlameMessageWindow(
                    message='Password is required. Please enter a password and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.password_window,
                    )
                return
            self.username = self.user_name_entry.text
            self.password = self.password_entry.text
        else:
            if not self.password_entry.text or self.password_entry.text == '':
                PyFlameMessageWindow(
                    message='Password is required. Please enter a password and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.password_window,
                    )
                return
            password = self._test_password()

            if password:
                self.password = password
                self.password_window.close()
            else:
                PyFlameMessageWindow(
                    message='Password is incorrect. Please enter the correct password and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.password_window,
                    )
                return

    def _cancel(self):
        """
        Cancel
        ======

        Close window and print message to console.
        """

        self.password_window.close()

        if self.user_name_prompt:
            pyflame.print('Username and Password Entry Cancelled', text_color=TextColor.RED)
        else:
            pyflame.print('Password Entry Cancelled', text_color=TextColor.RED)

class PyFlameProgressWindow:
    """
    PyFlameProgressWindow
    =====================

    Custom QT Flame Progress Window

    Args
    ----
        `parent` (PyFlameWindow | None):
            This windows parent window. Set to `None` if no parent window.

        `task` (str, optional):
            Name of task to be displayed in progress window.
            (Default: `Processing`)

        `total_tasks` (int):
            Total number of operations to be completed.
            (Default: `100`)

        `title` (str, optional):
            text shown in top left of window ie. Rendering...
            (Default: `Processing...`)

        `title_style` (Style, optional):
            Style of title text.
            (Default: `Style.BACKGROUND_THIN`)

            Style Options
                `Style.NORMAL`: Plain text, left aligned.
                `Style.UNDERLINE`: Underlined text, centered.
                `Style.BORDER`: Border text, centered.
                `Style.BACKGROUND`: Text background is darker, left aligned.
                `Style.BACKGROUND_THIN`: Text background is darker, left aligned, thin font.

        `title_align` (Align, optional):
            Alignment of title text. If not provided, Align.LEFT will be used.
            (Default: `None`)

            Align Options
                `Align.LEFT`: Left aligned.
                `Align.CENTER`: Centered.
                `Align.RIGHT`: Right aligned.

        `line_color` (WindowBarColor):
            Color of bar on left side of window.
            (Default: `Color.BLUE`)

            Color Options
                `Color.GRAY`: Gray line.
                `Color.BLUE`: Blue line.
                `Color.RED`: Red line.
                `Color.GREEN`: Green line.
                `Color.YELLOW`: Yellow line.
                `Color.TEAL`: Teal line.

        `message_bar` (bool):
            Enable message bar at bottom of window.
            (Default: `False`)

    Properties
    ----------
        `text` (str):
            Get or set the text in the progress window.
            (Used to print progress to terminal)

        `task` (str):
            Get or set the task of the progress window.
            (Default: `Processing`)

        `total_tasks` (int):
            Get or set the total number of tasks to be completed.
            (Default: `100`)

        `current_task` (int):
            Get or set the number of the current task being processed.
            Updating this value will update the progress bar and the text in the progress window.
            (Default: `1`)

        `title` (str):
            Get or set the title of the progress window.
            (Default: `Processing...`)

        `title_style` (Style):
            Get or set the title style of the progress window.
            (Default: `Style.BACKGROUND_THIN`)

        `title_align` (Align):
            Get or set the title alignment of the progress window.
            (Default: `Align.LEFT`)

        `line_color` (Color):
            Get or set the line color of the progress window.
            (Default: `Color.BLUE`)

        `message_bar_text` (str):
            Get or set text in message bar.
            (Default: `""`)

    Methods
    -------
        `enable_done_button`
            Enables the Done button.

        `close`:
            Close the Progress Window.

        `text_append`
            Append text to the current message in the progress window. Message starts on a new line.

        `tasks_completed`
            Set progress window to completed state. Sets progress bar to 100%, updates progress text with completed values, and optionally updates title, appends text, and enables the Done button.

    Examples
    --------
        To create progress bar window:
        ```
        progress_window = PyFlameProgressWindow(
            total_tasks=10,
            parent=None
            )
        ```

        To create progress bar window with custom progress messagge:
        ```
        progress_window = PyFlameProgressWindow(
            total_tasks=10,
            task_progress_message='{task}: [{processing_task}kb of {total_tasks}kb] ({progress:.1f}%)',
            parent=None
            )
        ```

        ```
        To set progress window as complete.
        ```
        progress_window.tasks_completed()
        ```

        To update progress bar progress value:
        ```
        progress_window.current_task = 2
        ```

        To enable or disable done button:
        ```
        progress_window.tasks_complete = True
        ```

        To set the title text:
        ```
        progress_window.title = 'Render Completed'
        ```

        To update message bar text:
        ```
        progress_window.message_bar_text = 'Some message'
        ```
    """

    def __init__(self: 'PyFlameProgressWindow',
                 parent: PyFlameWindow | None,
                 task: str='Processing',
                 total_tasks: int=100,
                 task_progress_message: str=f'{{task}}: [{{processing_task}} of {{total_tasks}}] ({{progress:.1f}}%)',
                 title: str='Processing...',
                 title_style: Style=Style.BACKGROUND_THIN,
                 title_align: Align | None=None,
                 line_color: Color=Color.BLUE,
                 message_bar: bool=False,
                 ) -> None:

        # Validate Parent
        if not isinstance(parent, (type(None), PyFlameWindow)):
            pyflame.raise_type_error('PyFlameProgressWindow', 'parent', 'PyFlameWindow | None', parent)
        if not isinstance(task_progress_message, str):
            pyflame.raise_type_error('PyFlameProgressWindow', 'task_progress_message', 'str', parent)

        print(
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{TextColor.WHITE.value}' + # Set text color
            f'{title}' + '\n' +
            f'{TextColor.BLUE.value}' + # Set text color
            '=' * 80 + '\n' +
            f'{TextColor.RESET.value}'  # Reset text color
            )

        #-------------------------------------
        # [Build Window]
        #-------------------------------------

        self.progress_window = PyFlameWindow(
            grid_layout_columns=4,
            grid_layout_rows=8,
            grid_layout_column_width=110,
            message_bar=message_bar,
            parent=parent,
            )

        self.text_edit = PyFlameTextEdit(
            text_style=TextStyle.UNSELECTABLE,
            )

        self.progress_bar = PyFlameProgressBarWidget()

        self.done_button = PyFlameButton(
            text='Done',
            connect=self.progress_window.close,
            color=Color.BLUE,
            enabled=False,
            )

        #-------------------------------------
        # [Window Layout]
        #-------------------------------------

        self.progress_window.grid_layout.addWidget(self.text_edit, 0, 0, 6, 4)
        self.progress_window.grid_layout.addWidget(self.progress_bar, 6, 0, 1, 4)
        self.progress_window.grid_layout.addWidget(self.done_button, 8, 3)

        #-------------------------------------
        # [Set Window Properties]
        #-------------------------------------

        self.total_tasks = total_tasks
        self.task = task
        self.task_progress_message = task_progress_message
        self.progress = 0
        self.title = title
        self.title_style = title_style
        self.title_align = title_align
        self.line_color = line_color
        self.current_task = 0

        QtWidgets.QApplication.processEvents()

        # Wait for UI to fully display
        pyflame.pause()

    #-------------------------------------
    # [Properties]
    #-------------------------------------

    @property
    def text(self) -> str:
        """
        Task
        ====

        Get or set text in progress window.
        (Used to print progress to terminal)

        Returns
        -------
            `str`:
                Text in progress window.

        Set
        ---
            `value` (str):
                Progress window text.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get progress window text
            print(progress_window.text)

            # Set progress window text
            progress_window.text = 'Some message'
            ```
        """

        return self.text_edit.text

    @text.setter
    def text(self, value: str) -> None:
        """
        Text
        ====

        Set text in the progress window.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameProgressWindow.text', 'value', 'str', value)

        self.text_edit.text = value

    @property
    def task(self) -> str:
        """
        Task
        ====

        Get or set the task being done.

        The value here is added into the progress window text.

        Returns
        -------
            `str`:
                Task being done.

        Set
        ---
            `value` (str):
                Task being done.

        Raises
        ------
            TypeError:
                If the provided `value` is not a string.

        Examples
        --------
            ```
            # Get task being done
            print(progress_window.task)

            # Set task being done
            progress_window.task = 'Processing Task'
            ```
        """

        return self._task

    @task.setter
    def task(self, value: str) -> None:
        """
        Task
        ====

        Set the task being done.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameProgressWindow.task', 'value', 'str', value)

        self._task = value

    @property
    def total_tasks(self) -> int:
        """
        Total Tasks
        ===========

        Get or set the total number of tasks to be completed.

        Returns
        -------
            `int`:
                Total number of tasks to be completed.

        Set
        ---
            `value` (int):
                Total number of tasks to be completed.

        Raises
        ------
            TypeError:
                If the provided `value` is not a integer.

        Examples
        --------
            ```
            # Get total number of tasks to be completed
            print(progress_window.total_tasks)

            # Set total number of tasks to be completed
            progress_window.total_tasks = 10
            ```
        """

        return self._total_tasks

    @total_tasks.setter
    def total_tasks(self, value: int) -> None:
        """
        Total Tasks
        ===========

        Set the total number of tasks to be completed.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressWindow.total_tasks', 'value', 'integer', value)

        # Set Total Tasks in Progress Bar
        self.progress_bar.total_tasks = value

        # Set Total Tasks
        self._total_tasks = value

    @property
    def current_task(self) -> int:
        """
        Current Task
        ============

        Get or set the number of the current task being processed.
        Updating this value will update the progress bar and the text in the progress window.

        Returns
        -------
            `int`:
                Number of current task being processed

        Set
        ---
            `value` (int):
                Current task number being processed.

        Raises
        ------
            TypeError:
                If the provided `value` is not a integer.

        Examples
        --------
            ```
            # Get number of current task being processed
            print(progress_window.current_task)

            # Set number of current task being processed
            progress_window.current_task = 1
            ```
        """

        return self._current_task

    @current_task.setter
    def current_task(self, value: int) -> None:
        """
        Current Task
        ============

        Set the number of the current task being processed.
        """

        # Validate Argument
        if not isinstance(value, int):
            pyflame.raise_type_error('PyFlameProgressWindow.current_task', 'value', 'integer', value)

        # Update Progress Bar
        self.progress_bar.processing_task = value

        # Update Current Task
        self._current_task = value

        # Update Progress Text
        self.text_edit.text = self.task_progress_message.format(task=self.task, processing_task=value, total_tasks=self.total_tasks, progress=self.progress)

        # Update Progress Text
        if value > 0:
            self.progress = (value / self.total_tasks) * 100
        else:
            self.progress = value

        # Pause for UI update
        pyflame.pause()

    @property
    def title(self) -> str:
        """
        Title
        =====

        Get or set the Progress Window title.

        Returns
        -------
            `str`:
                Progress Window title.

        Set
        ---
            `value` (str):
                Progress Window title.

        Raises
        ------
            TypeError:
                If the provided `value` is not a str.

        Examples
        --------
            ```
            # Get title text
            print(progress_window.title)

            # Set title style
            progress_window.title = 'Progress Window'
            ```
        """

        return self.progress_window.title

    @title.setter
    def title(self, value: str) -> None:
        """
        Title
        =====

        Set the Progress Window title.
        """

        # Validate Argument
        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameProgressWindow.title', 'value', 'str', value)

        self.progress_window.title = value

    @property
    def title_style(self) -> Style:
        """
        Title Style
        ============

        Get or set the Progress Window title style.

        Returns
        -------
            `Style`:
                Progress Window title style.

        Set
        ---
            `value` (Style):
                Progress Window title style.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Style.

        Examples
        --------
            ```
            # Get title style
            print(progress_window.title_style)

            # Set title style
            progress_window.title_style = Style.UNDERLINE
            ```
        """

        return self.progress_window.title_style

    @title_style.setter
    def title_style(self, value: Style) -> None:
        """
        Title Style
        ============

        Set the Progress Window title style.
        """

        # Validate Argument
        if not isinstance(value, Style):
            pyflame.raise_type_error('PyFlameProgressWindow.title_style', 'value', 'Style', value)

        self.progress_window.title_style = value

    @property
    def title_align(self) -> Align | None:
        """
        Title Align
        ============

        Get or set the Progress Window title alignment.

        Returns
        -------
            `Align`:
                Progress Window title alignment.

        Set
        ---
            `value` (Align | None):
                Progress Window title alignment.

        Raises
        ------
            TypeError:
                If the provided `value` is not Align | None.

        Examples
        --------
            ```
            # Get title alignment
            print(progress_window.title_align)

            # Set title alignment
            progress_window.title_align = Align.CENTER
            ```
        """

        return self.progress_window.title_align

    @title_align.setter
    def title_align(self, value: Align | None) -> None:
        """
        Title Align
        ============

        Set the Progress Window title alignment.
        """

        # Validate Argument
        if value is not None and not isinstance(value, Align):
            pyflame.raise_type_error('PyFlameProgressWindow.title_align', 'value', 'Align | None', value)

        if value is not None:
            self.progress_window.title_align = value

    @property
    def line_color(self) -> Color:
        """
        Line Color
        ==========

        Get or set the Progress Window line color as Color Enum.

        Returns
        -------
            `Color`:
                Progress Window line color.

        Set
        ---
            `value` (Color):
                Progress Window line color.

        Raises
        ------
            TypeError:
                If the provided `value` is not a Color.

        Examples
        --------
            ```
            # Get window line color
            print(progress_window.line_color)

            # Set window line color
            progress_window.line_color = Color.BLUE
            ```
        """

        return self.progress_window.line_color

    @line_color.setter
    def line_color(self, value: Color) -> None:
        """
        Line Color
        ==========

        Set the Progress Window line color.
        """

        # Validate Argument
        if not isinstance(value, Color):
            pyflame.raise_type_error('PyFlameProgressWindow.line_color', 'value', 'Color Enum', value)

        self.progress_window.line_color = value

    @property
    def message_bar_text(self) -> str:
        """
        Message Bar Text
        ================

        Get or set the text of the message bar.

        Returns
        -------
            str:
                The text of the message bar.

        Set
        ---
        message_bar_text (str):
            The text of the message bar.

        Examples
        --------
            ```
            # Get message bar text
            print(progress_window.message_bar_text)

            # Set message bar text
            progress_window.message_bar_text = 'This is a message bar text'
            ```
        """

        return self.progress_window.message_bar_text

    @message_bar_text.setter
    def message_bar_text(self, value: str) -> None:
        """
        Message Bar Text
        ================

        Set the text of the message bar.
        """

        if not isinstance(value, str):
            pyflame.raise_type_error('PyFlameProgressWindow', 'message_bar_text', 'str', value)

        # Set Message Bar Text
        self.progress_window.message_bar_text = value

        #Pause QT briefly to allow the message bar to update
        pyflame.pause()

    #-------------------------------------
    # [Methods]
    #-------------------------------------

    def enable_done_button(self):

       # Enable Done button
        self.done_button.enabled = True

    def close(self):
        """
        Close
        =====

        Close the Progress Window.
        """

        self.progress_window.close()

    def text_append(self, message: str) -> None:
        """
        Text Append
        ===========

        Append text to the current text in the progress window.

        Message starts on a new line.

        Args
        ----
            message (str):
                Text to be appended to current text in progress window.
        """

        # Validate Argument
        if not isinstance(message, str):
            pyflame.raise_type_error('PyFlameProgressWindow.text_append', 'message', 'str', message)

        self.text_edit.append(f'\n\n{message}')

        pyflame.pause()

    def tasks_completed(self, done_button_enabled: bool=True, task_progress_message: str | None=None, title: str | None=None, text_append: str | None=None) -> None:
        """
        Tasks Completed
        ===============

        Set progress window to a completed state and Enable the Done button

        Args
        ----
        done_button_enabled (bool):
            Enable the Done button.
            (Default: True)

        task_progress_message (str | None):
            Updates text in window. Updates processing_task and progress values to completed values.
            Leave as None to update standard messages to completed values.
            (Default: None)

        title (str | None):
            Update progress window title. None leaves existing title.
            (Default: None)

        text_append (str | None):
            Add text to existing window text. Leaves any existing window text as is.
            (Default: None)
        """

        # Validate Argument
        if not isinstance(done_button_enabled, bool):
            pyflame.raise_type_error('PyFlameProgressWindow.tasks_completed', 'done_button_enabled', 'bool', done_button_enabled)
        if task_progress_message is not None and not isinstance(task_progress_message, str):
            pyflame.raise_type_error('PyFlameProgressWindow.tasks_completed', 'task_progress_message', 'str | None', task_progress_message)
        if title is not None and not isinstance(title, str):
            pyflame.raise_type_error('PyFlameProgressWindow.tasks_completed', 'title', 'str | None', title)
        if text_append is not None and not isinstance(text_append, str):
            pyflame.raise_type_error('PyFlameProgressWindow.tasks_completed', 'text_append', 'str | None', text_append)

        # Set progress bar to 100%
        self.progress_bar.setValue(self.progress_bar.maximum())

        # Update Progress Text
        if not task_progress_message:
            self.text_edit.text = self.task_progress_message.format(task=self.task, processing_task=self.total_tasks, total_tasks=self.total_tasks, progress=100)
        else:
            self.text_edit.text = task_progress_message

        # Update Window Title
        if title:
            self.title = title

        if text_append:
            self.text_append(text_append)

        if done_button_enabled:
            self.enable_done_button()
