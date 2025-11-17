# -*- coding: utf-8 -*-
# Logik Portal
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
Script Name: Logik Portal
Script Version: 6.5.1
Flame Version: 2023.2
Written by: Michael Vaglienty
Crying Croc Design by: Enid Dalkoff
Creation Date: 10.31.20
Update Date: 10.20.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Flame Main Menu

Description:

    Share/install python scripts, batch setups, inference nodes, and download matchboxes

URL:
    https://github.com/logik-portal/python/logik_portal

Menu:

    Flame Main Menu -> Logik -> Logik Portal

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v6.5.1 10.20.25
        - Fixed issues with inference copyright window.

    v6.5.0 03.16.25
        - Updated to PyFlameLib v4.3.0.

    v6.4.0 01.09.25
        - Added ability to select where python scripts are installed. Default path is /opt/Autodesk/shared/python.
          *** When selecting a path, make sure its a path Flame will look for python scripts in and is writeable ***
        - Fixed: Adding a matchbox to batch would sometimes load the wrong matchbox if it had a similar name to another matchbox.

    v6.3.0 01.07.25
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v6.2.0 08.31.24
        - Added disclaimer message when downloading inference nodes.
        - Added notice to users uploading inference nodes that they should include links to the original source of the model and that the model should be open source.
        - Fixed misc bugs.

    v6.1.0 08.16.24
        - Added search fields to python scripts, batch setups, and inference nodes tabs.
        - User is given message to save work before installing the Logik Portal from within the Logik Portal. Flame will crash but will be fine after restarting Flame.

    v6.0.0 08.03.24
        - Added Inference Nodes tab. Allows for downloading and submitting Inference nodes.
        - Updated to PyFlameLib v3.0.0.
        - Removed Archive tab.
        - Fixed: Matchbox not installing correctly.
        - Fixed: Autodesk scripts not installing correctly.

    v5.9.1 04.18.24
        - Fixed: Install button not properly working for python scripts. Thanks for catching Mottizle!

    v5.9.0 03.05.24
        - Added column to python script tab to show minimum and maximum flame versions required to run script.
          Scripts that require a newer or older version of flame will be greyed out in the list and not installable.

    v5.8.2 02.08.24
        - Python scripts can now sorted by year when clicking on year header.
        - Dates are flipped from dd.mm.yy to yy.mm.dd for sorting.
        - Replaced browse buttons in submit windows with clickable line edit file browsers.

    v5.8.1 01.21.24
        - Fixed: Submit buttons not working after submitting script unless portal is restarted.

    v5.8.0 01.18.24
        - Updates to UI/PySide.

    v5.7.1 10.09.23
        - Fixed progress window overflow error when uploading/downloading large files.

    v5.7.0 10.03.23
        - Progress windows added when downloading or uploading files.
        - When uploading python scripts __pycache__ folder is now excluded from tar file.
        - Updated to pyflame lib v2.

    v5.6.1 06.26.23
        - Updated script versioning to semantic versioning.
        - Removed old version check of python script uploads to allow for semantic versioning.
        - Updated password window for uploading python scripts.
        - Main tabs now longer have outline when selected in linux.

    v5.6 03.02.23
        - Updated FTP server info.

    v5.5 02.04.23
        - Added search to matchbox tab.

    v5.4 02.02.23
        - Improvements to Matchbox tab:
            - All current matchboxes are now listed with descriptions.
            - Matchboxes can be sorted by Name, Shader Type, and Author.
            - Matchboxes can be added to current batch setup.

        - Added check to make sure script is installed to correct path.
        - Portal now opens to last used tab.
        - Portal updates will be shown on whatever tab script first opens to.

    v5.3 01.25.23
        - Matchboxes will now install into a directory called LOGIK in the selected directory.
        - Reverted menu for Flame 2023.2+ to Flame Main Menu -> Logik -> Logik Portal. Scripts downloaded from the Portal that have a setup menu
          in the future will have their menu added under Flame Main Menu -> Logik -> Logik Portal Setup -> Script Name for clarity.
        - Updated config file loading/saving.

    v5.2 01.08.23
        - Updates to the Logik Portal are now shown in the main window when the script first loads up.

    v5.1 12.22.22
        - Fixed possible ssl error when downloading matchboxes.

    v5.0 11.28.22
        - Updated with new FTP server.
        - Autodesk python scripts provided with Flame 2023.2+ are now listed/installable through the Portal.
        - Maximum archive size increased to 1GB.

    v4.2 09.06.22
        - Updated menu for Flame 2023.2+:
            Flame Main Menu -> Logik Portal

    v4.1 07.22.22
        - Messages print to Flame message window - Flame 2023.1+.
        - Added Flame file browser - Flame 2023.1+.
        - pyflame_lib files aren't shown in the installed scripts list anymore.
        - Matchbox install path now defaults to  /opt/Autodesk/presets/FLAME_VERSION/matchbox/shaders

    v4.0 03.23.22
        - Updated UI for Flame 2023.
        - Moved UI widgets to external file.

    v3.0 12.09.21
        - Getting Flame version is updated to work with new PR versioning.
        - Moved a few buttons around.

    v2.9 12.02.21
        - Python script upload login bug fix.

    v2.8 11.17.21
        - Login info for uploading scripts only needs to be entered first time something is uploaded.

    v2.7 10.16.21
        - Install Local button added to python tab to install python scripts from local drive.
        - Improved Flame version detection.
        - Script will now attempt to download matchbox collection from website. If website is down, it will download from portal ftp.

    v2.6 09.06.21
        - Misc bug fixes / fixed problem with not being able to enter system password to load matchboxes to write protected folder.

    v2.5 07.30.21
        - Added ability to upload/download archives - Archive size limit is 200MB.
        - Config is now XML.

    v2.4 07.23.21
        - Added python submit button back. User name and password now required to submit scripts.
        - Fixed bug - files starting with . sometimes caused script to not work.

    v2.3 07.06.21
        - Added Logik Matchbox archive to Portal FTP. Matchbox archive now stored on FTP instead of pulling directly from logik-matchbook.org.

    v2.2 06.03.21
        - Updated to be compatible with Flame 2022/Python 3.7.
        - Removed python script submission ability. Scripts can now be added through github submissions only.

    v1.6 03.14.21
        - UI improvements/updates - UI elements to classes.
        - Added contextual menus to python tab to install and delete scripts and to batch tab to download batch setups.
        - User will be prompted for system password when trying to download matchboxes to protected folders such as /opt/Autodesk/presets/2021.1/matchbox/shaders.
        - If newer version of installed script is available on portal it will be highlighted in portal list.
        - If newer version of flame is required for a script, script entry will be greyed out.
        - If newer version of flame is required for a batch setup, batch setup entry will be greyed out.
        - Batch setups now properly download into paths with spaces in folder names.
        - User will get message if script folder needs permissions changed to create temp folders/files.
        - File browse buttons removed - browser now opens when clicking lineedit field.
        - If new version of a python script is submitted old script will be removed.

    v1.5 02.27.21
        - UI code updates.
        - Fixed bug causing script to hang when reading descriptions on certain scripts.
        - Fixed batch submit button.

    v1.4 01.25.21
        - Fixed temp path for logik matchbox install.

    v1.3 01.14.21
        - Script description info can now be entered in Portal UI instead of being in script header.
        - Fixed font size for linux.

    v1.2 12.29.20
        - Fixed problems with script running on Flame with extra .x in Flame version.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil
import tarfile
import xml.etree.ElementTree as ET
from ftplib import FTP
from subprocess import PIPE, Popen, CalledProcessError
from typing import Union

import flame
from lib.pyflame_lib_logik_portal import *

# Try to import PySide6, otherwise import PySide2
try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Logik Portal'
SCRIPT_VERSION = 'v6.5.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

LOGIK_FTP = '45.79.19.175'

#-------------------------------------
# [Main Script]
#-------------------------------------

class LogikPortal():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path
        if not self.check_script_path():
            return

        # Get version of flame
        self.flame_full_version = flame.get_version()
        self.flame_version = pyflame.get_flame_version()

        # Set Autodesk python scripts path
        self.autodesk_scripts_path = f'/opt/Autodesk/flame_{self.flame_full_version}/python_utilities/scripts'
        if not os.path.isdir(self.autodesk_scripts_path):
            self.autodesk_scripts_path = f'/opt/Autodesk/flare_{self.flame_full_version}/python_utilities/scripts'
        #print('autodesk_scripts_path:', self.autodesk_scripts_path)

        # Load config file
        self.settings = self.load_config()

        # Get user
        self.flame_current_user = flame.users.current_user.name

        # Create temp folder
        self.temp_folder = os.path.join(SCRIPT_PATH, 'temp')
        if not os.path.isdir(self.temp_folder):
            try:
                os.makedirs(self.temp_folder)
            except:
                PyFlameMessageWindow(
                    message=f'{SCRIPT_NAME}: Script needs full permissions to script folder.\n\nIn shell/terminal type:\n\nchmod 777 /opt/Autodesk/shared/python/logik_portal',
                    type=MessageType.ERROR,
                )
                return

        # Check internet connection to ftp
        try:
            self.ftp_download_connect()
        except:
            PyFlameMessageWindow(
                message="Can't connect to Logik Portal.\nCheck internet connection and try again.",
                type=MessageType.ERROR,
            )
            return

        #  Init variables
        self.ftp_script_list = []
        self.installed_script_dict = {}
        self.file_description = ''
        self.tar_path = ''
        self.tar_file_name = ''
        self.batch_setups_xml_path = ''
        self.python_scripts_xml_path = ''
        self.sudo_password = ''
        self.updates = ''

        self.main_window()

        self.update_installed_scripts_tree()

        self.download_xmls()

        self.update_matchbox_tree()
        self.update_batch_setups_tree()
        self.update_inference_node_tree()
        self.update_logik_portal_scripts_tree()

        self.check_batch_flame_version()

        #self.check_script_flame_version(self.portal_scripts_tree, 0)
        self.check_script_flame_version(self.portal_scripts_tree)

        # Go to last used tab
        self.window.go_to_tab(self.settings.last_tab)

        # Get updates file from FTP
        self.get_updates()

        # Close ftp connection
        self.ftp.quit()

        pyflame.print('Welcome To The Logik Portal.', text_color=TextColor.GREEN)

    def check_script_path(self) -> bool:
        """
        Check Script Path
        =================

        Check if script is installed in the correct location.

        Returns:
        --------
            bool: True if script is installed in correct location, False if not.
        """

        if os.path.dirname(os.path.abspath(__file__)) != SCRIPT_PATH:
            PyFlameMessageWindow(
                message=f'Script path is incorrect. Please reinstall script.\n\nScript path should be:\n\n{SCRIPT_PATH}',
                type=MessageType.ERROR,
                )
            return False
        return True

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
        --------
            PyFlameConfig: PyFlameConfig object with config values.
        """

        # Set install path for local python scripts
        if float(self.flame_version) >= 2023.2:
            install_local_path = self.autodesk_scripts_path
        else:
            install_local_path = '/opt/Autodesk'
        #print('install_local_path:', install_local_path)

        settings = PyFlameConfig(
            config_values={
                'python_submit_all_files': False,
                'matchbox_path': f'/opt/Autodesk/presets/{self.flame_full_version}/matchbox/shaders',
                'batch_setup_download_path': '/opt/Autodesk',
                'batch_submit_path': '/opt/Autodesk',
                'script_submit_path': '/opt/Autodesk',
                'script_install_local_path': install_local_path,
                'script_install_path': '/opt/Autodesk/shared/python',
                'open_batch': False,
                'inference_node_download_path': '/opt/Autodesk',
                'inference_node_submit_path': '/opt/Autodesk',
                'inference_node_add_to_batch': True,
                'username': '',
                'password': '',
                'last_tab': 0,
                }
            )

        return settings

    def disclaimer(self) -> None:
        """
        Disclaimer
        ==========

        Read disclaimer from text file.

        Disclaimer is printed to terminal when script is run and also shown when downloading inference nodes.

        Returns:
        --------
            str:
                Disclaimer text.
        """

        # Open the text file in read mode
        with open(os.path.join(SCRIPT_PATH, 'assets', 'inference_node_disclaimer.txt'), "r") as file:
            # Read the contents of the file
            return file.read()

    #-------------------------------------
    # [FTP]
    #-------------------------------------

    def ftp_download_connect(self):

        # Connect to ftp
        self.ftp = FTP(f'{LOGIK_FTP}')
        self.ftp.login('logik_portal_download', 'L0gikD0wnL0ad#20')

        pyflame.print('Connected To Logik Portal.', text_color=TextColor.GREEN)

    def ftp_upload_connect(self):

        # Connect to ftp
        self.ftp = FTP(f'{LOGIK_FTP}')
        self.ftp.login('logik_portal_upload', 'L0gikUpl0ad#20')

        pyflame.print('Connected To Logik Portal.', text_color=TextColor.GREEN)

    def ftp_disconnect(self):

        self.ftp.quit()

        pyflame.print('Disconnected From Logik Portal.', text_color=TextColor.GREEN)

    #-------------------------------------
    # [Main Window]
    #-------------------------------------

    def main_window(self):

        # Create main window
        self.window = PyFlameTabWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.done,
            grid_layout_columns=7,
            grid_layout_rows=18,
            grid_layout_adjust_column_widths={
                1: 200,
                3: 50,
                5: 200,
                }
            )

        # Add tabs to main window
        self.tab1 = self.window.add_tab('Python Scripts')
        self.tab2 = self.window.add_tab('Matchbox')
        self.tab3 = self.window.add_tab('Batch Setups')
        self.tab4 = self.window.add_tab('Inference Nodes')

        # Load Tab UI's
        self.python_scripts_tab()
        self.matchbox_tab()
        self.batch_setups_tab()
        self.inference_nodes_tab()

    def python_scripts_tab(self):

        def login_check() -> None:

            def check_login(username, password):

                # Try connecting to ftp
                try:
                    ftp = FTP(f'{LOGIK_FTP}')
                    ftp.login(username, password)
                    ftp.cwd('/')

                    self.settings.save_config(
                        config_values={
                            'username': username,
                            'password': password
                            }
                        )

                    submit_script()
                except:
                    PyFlameMessageWindow(
                        message='Login incorrect, try again.',
                        type=MessageType.ERROR,
                        )
                    return

            if self.settings.username and self.settings.password:
                submit_script()
            else:
                password_window = PyFlamePasswordWindow(
                    message='Logik Portal login required to submit a python script',
                    title='Python Submit Login',
                    user_name_prompt=True,
                    )
                username, password = password_window.username_password()
                if not username or not password:
                    return

                if username and password:
                    check_login(username, password)

        def submit_script() -> None:

            def upload_script():

                def upload():

                    def save_config():
                        """
                        Save Config
                        ===========

                        Save path to config file
                        """

                        self.settings.save_config(
                            config_values={
                                'script_submit_path': self.submit_script_path_entry.text(),
                                'python_submit_all_files': self.all_files_button.isChecked(),
                                }
                            )

                    def create_script_xml(self):
                        """
                        Create Script XML
                        =================

                        Create and save xml file for python script.
                        """

                        description_text = self.submit_script_description_text_edit.toPlainText()
                        description_text = description_text.replace("'", "\"")
                        description_text = description_text.replace('&', '-')

                        text = []

                        text.insert(0, f"    <script name='{self.submit_script_name_field.text()}'>")
                        text.insert(1, f"        <script_version>'{self.submit_script_version_entry.text()}'</script_version>")
                        text.insert(2, f"        <flame_version>'{self.submit_script_flame_version_entry.text()}'</flame_version>")
                        text.insert(3, f"        <date>'{self.submit_script_date_entry.text()}'</date>")
                        text.insert(4, f"        <developer>'{self.submit_script_dev_name_entry.text()}'</developer>")
                        text.insert(5, f"        <description>'{description_text}'</description>")
                        text.insert(6, '    </script>')

                        out_file = open(script_xml_path, 'w')
                        for line in text:
                            print(line, file=out_file)
                        out_file.close()

                        print('--> Script xml created.\n')

                    def create_tar():
                        """
                        Create Tar
                        ==========

                        Create tar file of python script file(s).
                        """

                        pyflame.print('Creating TAR File...')

                        if self.all_files_button.isChecked():
                            print('Upload All Files: True\n')

                            # Loop through files in script folder avoiding hidden files and __pycache__ folder
                            tar_file_list = ''
                            skip = ('.', '__pycache__')

                            for file in os.listdir(script_folder):
                                if not any(file.startswith(prefix) for prefix in skip):
                                    tar_file_list += ' ' + file

                            print('tar_file_list:', tar_file_list)
                            tar_file_list.strip()

                            # Create tar command
                            tar_command = f'tar -cvf {script_tar_path} {tar_file_list}'

                        else:
                            print('Upload All Files: False\n')
                            tar_command = 'tar -cvf %s  %s' % (script_tar_path, script_name + '.py')

                        print('Adding files to tar:')

                        os.chdir(script_folder)
                        os.system(tar_command)

                        print('\n')
                        pyflame.print(f'Python Script TAR File Created')

                    def upload_files():
                        """
                        Upload Files
                        ============

                        Upload script and xml to ftp.
                        """

                        pyflame.print('Uploading Python Script...')

                        # Connect to ftp
                        self.ftp = FTP(f'{LOGIK_FTP}')
                        self.ftp.login(self.settings.username, self.settings.password)
                        self.ftp.cwd('/Submit_Scripts')

                        pyflame.print('Uploading Python Script...')

                        # Close window
                        self.submit_script_window.close()

                        # Upload tgz file to ftp
                        self.upload_file(
                            upload_type='Python Script',
                            file_name=script_name,
                            xml_path=script_xml_path,
                            tgz_path=script_tar_path,
                            )

                        # Bring back main window
                        self.window.show()

                    # Upload script and xml to ftp
                    script_xml_path = os.path.join(self.temp_folder, f'{self.submit_script_path_entry.text().rsplit("/", 1)[1][:-3]}.xml')

                    save_config()

                    create_script_xml(self)

                    script_name = self.submit_script_path_entry.text().rsplit('/', 1)[1][:-3]
                    script_path = self.submit_script_path_entry.text()
                    script_folder = script_path.rsplit('/', 1)[0]

                    script_tar_path = os.path.join(self.temp_folder, script_name) + '.tgz'

                    create_tar()

                    upload_files()

                # Check script path field
                if not os.path.isfile(self.submit_script_path_entry.text()):
                    PyFlameMessageWindow(
                        message='Enter path to python script.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check script version field
                elif not self.submit_script_version_entry.text():
                    PyFlameMessageWindow(
                        message='Enter script version.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check script version field for alpha characters
                alpha = [n for n in self.submit_script_version_entry.text() if n.isalpha()]
                if alpha:
                    PyFlameMessageWindow(
                        message='Script Version should be numbers only. Such as: 1.0.0',
                        type=MessageType.ERROR,
                        )
                    return

                # Check flame version field
                if not self.submit_script_flame_version_entry.text():
                    PyFlameMessageWindow(
                        message='Enter minimum version of Flame needed to run script.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check flame version field for alpha characters
                alpha = [n for n in self.submit_script_version_entry.text() if n.isalpha()]
                if alpha:
                    PyFlameMessageWindow(
                        message='Flame Version should be numbers only. Such as: 2021.2.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check script date field
                if not self.submit_script_date_entry.text():
                    PyFlameMessageWindow(
                        message='Enter date script was written or updated. Whichever is later.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check date field for proper formatting
                if not re.search('^\\d{2}.\\d{2}.\\d{2}',self.submit_script_date_entry.text()):
                    PyFlameMessageWindow(
                        message='Script date should be entered in dd.mm.yy format.',
                        type=MessageType.ERROR,
                        )
                    return

                if not len(self.submit_script_date_entry.text()) == 8:
                    PyFlameMessageWindow(
                        message='Script date should be entered in dd.mm.yy format.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check script dev field
                if not self.submit_script_dev_name_entry.text():
                    PyFlameMessageWindow(
                        message='Enter name of script author.',
                        type=MessageType.ERROR,
                        )
                    return

                # Check script description field
                elif not self.submit_script_description_text_edit.toPlainText():
                    PyFlameMessageWindow(
                        message='Enter description of script and any notes on working with script.',
                        type=MessageType.ERROR,
                        )
                    return

                # If script already exists on ftp confirm upload
                elif self.submit_script_name_field.text() in self.ftp_script_list:
                    if PyFlameMessageWindow(
                        message='Script already exists on Logik Portal. Update?',
                        type=MessageType.CONFIRM,
                        ):
                        upload()
                else:
                    upload()

            def update_script_info():
                """
                Update Script Info
                ==================

                Clean submit window fields and get selected script info.
                """

                # Clear submit fields
                self.submit_script_version_entry.setText('')
                self.submit_script_flame_version_entry.setText('')
                self.submit_script_date_entry.setText('')
                self.submit_script_dev_name_entry.setText('')
                self.submit_script_description_text_edit.setPlainText('')

                # Get selected script info
                self.get_script_info()

            def close_submit_window():
                """
                Close Submit Window
                ===================

                Close submit window and bring back main window.
                """

                # Close submit window
                self.submit_script_window.close()

                # Bring back main window
                self.window.show()

            # Create submit window
            self.submit_script_window = PyFlameWindow(
                title='Submit Python Script',
                return_pressed=upload_script,
                grid_layout_columns=6,
                grid_layout_rows=13,
                )

            # Labels
            self.submit_script_label = PyFlameLabel(
                text='Logik Portal Python Script Submit',
                style=Style.UNDERLINE,
                )
            self.submit_script_path_label = PyFlameLabel(
                text='Script Path',
                )
            self.submit_script_name_label_01 = PyFlameLabel(
                text='Script Name',
                )
            self.submit_script_version_label_01 = PyFlameLabel(
                text='Script Version',
                )
            self.submit_script_flame_version_label_01 = PyFlameLabel(
                text='Flame Version',
                )
            self.submit_script_date_label_01 = PyFlameLabel(
                text='Date',
                )
            self.submit_script_dev_name_label_01 = PyFlameLabel(
                text='Dev Name',
                )
            self.submit_script_description_label = PyFlameLabel(
                text='Description',
                )

            # Entries
            self.submit_script_name_field = PyFlameEntry(
                text='',
                )
            self.submit_script_version_entry = PyFlameEntry(
                text='',
                )
            self.submit_script_flame_version_entry = PyFlameEntry(
                text='',
                )
            self.submit_script_date_entry = PyFlameEntry(
                text='',
                )
            self.submit_script_dev_name_entry = PyFlameEntry(
                text='',
                )

            # Entry File Browser
            self.submit_script_path_entry = PyFlameEntryBrowser(
                text=self.settings.script_submit_path,
                connect=update_script_info,
                browser_type=BrowserType.FILE,
                browser_ext=['py'],
                browser_title='Select Python File',
                browser_window_to_hide=[self.window, self.submit_script_window],
                )

            # TextEdit
            self.submit_script_description_text_edit = PyFlameTextEdit(
                text=self.file_description,
                read_only=False,
                )

            # Push Buttons
            self.all_files_button = PyFlamePushButton(
                text='All Files',
                button_checked=self.settings.python_submit_all_files,
                )

            # Buttons
            self.submit_script_upload_button = PyFlameButton(
                text='Upload',
                connect=upload_script,
                color=Color.BLUE,
                )
            self.submit_script_cancel_button = PyFlameButton(
                text='Cancel',
                connect=close_submit_window,
                )

            #-------------------------------------
            # [Widget Layout]
            #-------------------------------------

            self.submit_script_window.grid_layout.addWidget(self.submit_script_label, 0, 0, 1, 6)

            self.submit_script_window.grid_layout.addWidget(self.submit_script_path_label, 1, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_name_label_01, 2, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_version_label_01, 3, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_flame_version_label_01, 4, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_date_label_01, 5, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_dev_name_label_01, 6, 0)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_description_label, 7, 0)

            self.submit_script_window.grid_layout.addWidget(self.submit_script_path_entry, 1, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_name_field, 2, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_version_entry, 3, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_flame_version_entry, 4, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_date_entry, 5, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_dev_name_entry, 6, 1, 1, 4)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_description_text_edit, 7, 1, 6, 4)

            self.submit_script_window.grid_layout.addWidget(self.all_files_button, 2, 5)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_upload_button, 11, 5)
            self.submit_script_window.grid_layout.addWidget(self.submit_script_cancel_button, 12, 5)

            if self.submit_script_path_entry.text().endswith('.py'):
                if os.path.isfile(self.submit_script_path_entry.text()):
                    self.update_script_info()

        def install_local_script():
            """
            Install Local Script
            ====================

            Install python script from local drive to shared script folder.
            """

            def save_config():
                """
                Save Config
                ===========

                Save path to config file
                """

                self.settings.save_config(
                    config_values={
                        'script_install_local_path': script_path.rsplit('/', 1)[0]
                        }
                    )

            script_path = pyflame.file_browser(
                title='Select Python File',
                extension=['py'],
                path=self.settings.script_install_local_path,
                window_to_hide=[self.window]
            )

            if script_path:

                save_config()

                script_to_install = script_path.rsplit('/', 1)[1][:-3]
                if PyFlameMessageWindow(
                    message=f'Install Python Script: {script_to_install.replace("_", " ")}',
                    type=MessageType.CONFIRM
                    ):
                    dest_folder = os.path.join(self.settings.script_install_path, script_to_install)
                    if os.path.isdir(dest_folder):
                        if not PyFlameMessageWindow(
                            message='Python script already exists. Overwrite?',
                            type=MessageType.CONFIRM
                            ):
                            pyflame.print('Python Script Not Installed')
                            return
                        else:
                            shutil.rmtree(dest_folder)

                    # Create local folder for script
                    if not os.path.exists(dest_folder):
                        try:
                            os.makedirs(dest_folder)
                        except:
                            PyFlameMessageWindow(
                                message='Could not create script folder.\n\nCheck path and permissions.',
                                type=MessageType.ERROR,
                            )
                            return

                    # Copy script to dest folder
                    shutil.copy(script_path, dest_folder)

                    # Refresh installed scripts tree list
                    self.update_installed_scripts_tree()

                    # Refresh python hooks
                    flame.execute_shortcut('Rescan Python Hooks')
                    pyflame.print('Python Hooks Refreshed')

                    if os.path.isfile(os.path.join(dest_folder, script_to_install + '.py')):
                        PyFlameMessageWindow(
                            message=f'Python script installed: {script_to_install.replace("_", " ")}',
                            type=MessageType.INFO,
                        )
                        return
                    PyFlameMessageWindow(
                        message=f'Python script not installed.',
                        type=MessageType.ERROR,
                    )
                    return

        def install_script() -> None:
            """
            Install Script
            ==============

            Get selected script info from selection and install script to shared script folder.
            """

            def install_logik_portal_script() -> str:
                """
                Install Logik Portal Script
                ===========================

                Download selected python script from Logik Portal.

                Returns:
                --------
                    (str): 'success' if script installed successfully, 'failed' if not, 'aborted' if user aborted install.
                """

                pyflame.print(f'Installing Logik Portal Script: {script_name}')

                # Set source and destination paths
                source_script_path = os.path.join('/Scripts', script_flame_version, script_name) + '.tgz'
                #print('source_script_path: ', source_script_path)

                # Set destination path
                dest_script_path = os.path.join(self.settings.script_install_path, script_name, script_name) + '.tgz'
                #print('dest_script_path: ', dest_script_path)

                # Set destination folder
                dest_folder = dest_script_path.rsplit('/', 1)[0]
                #print('dest_folder:', dest_folder)

                # Check if script already exists, if so prompt to overwrite, otherwise delete existing script folder
                if os.path.isdir(dest_folder):
                    if not PyFlameMessageWindow(
                        message='Script Already Exists. Overwrite?',
                        type=MessageType.CONFIRM,
                        ):
                        return False
                    else:
                        if 'logik_portal' in script_name:
                            if not PyFlameMessageWindow(
                                message='Installing the Logik Portal from within the Logik Portal will cause Flame to crash.\n\nSave work before continuing.\n\nAll will be fine after restarting Flame.\n\nContinue?',
                                type=MessageType.CONFIRM,
                                ):
                                return False
                        shutil.rmtree(dest_folder)

                # Create new local folder for script
                os.makedirs(dest_folder)

                pyflame.print('Downloading Python Script From Logik Portal...')

                # Download python script tgz file from ftp
                self.download_file(
                    download_type='Python Script',
                    file_name=script_name,
                    ftp_file_path=source_script_path,
                    tgz_path=dest_script_path,
                    )

                # Uncompress tgz file
                os.system(f'tar -xf {dest_script_path} -C {dest_folder}')

                # Delete tgz file
                os.remove(dest_script_path)

                # Check if script is in correct path, if so install is complete, if not, install failed.
                if os.path.isfile(dest_script_path[:-3] + 'py'):
                    return True
                return False

            pyflame.print('Installing Python Script...')

            # Get selected script info from selection
            selected_script = self.portal_scripts_tree.selectedItems()
            script_item = selected_script[0]
            script_name = script_item.text(0).strip()
            script_name = script_name.replace(' ', '_')
            script_flame_version = script_item.text(2)
            script_author = script_item.text(5)

            print('Script Info:')
            print('    Script name:', script_name)
            print('    Script Flame version:', script_flame_version)
            print('    Script Author:', script_author, '\n')

            # Install script from Logik Portal
            script_installed = install_logik_portal_script()

            # Refresh python hooks
            flame.execute_shortcut('Rescan Python Hooks')

            # Check if script is in correct path, if so install is complete, if not, install failed.
            if script_installed:
                # Refresh installed scripts tree list
                self.update_installed_scripts_tree()

                # Set color of selected script in portal tree to normal color
                script_item.setForeground(0, QtGui.QColor(154, 154, 154))

                pyflame.print(f'Script Installed: {script_name.replace("_", " ")}', text_color=TextColor.GREEN)
                return
            else:
                PyFlameMessageWindow(
                    message='Python Script Install Aborted.',
                    type=MessageType.ERROR,
                    )
                return

        def delete_script() -> None:
            """
            Delete Script
            =============

            Delete selected script from the installed scripts tree. Update installed scripts tree list after deletion.
            """

            # Get script path
            selected_script = self.installed_scripts_tree.selectedItems()
            script_item = selected_script[0]
            script_to_delete = script_item.text(0)
            script_to_delete = script_to_delete.replace(' ', '_')
            script_path = script_item.text(5)
            script_folder_name = script_path.rsplit('/', 2)[1]
            script_folder_path = script_path.rsplit('/', 1)[0]

            # Confirm deletion
            if not PyFlameMessageWindow(
                message=f'Delete python script: {script_to_delete}',
                type=MessageType.WARNING,
                ):
                pyflame.print('Delete Cancelled')
            else:
                # Remove script
                # If script is in folder with the same name of script, remove the folder
                if script_folder_name == script_to_delete:
                    shutil.rmtree(script_folder_path)
                else:
                    os.remove(script_path)
                    try:
                        os.remove(script_path + 'c')
                    except:
                        pass

                pyflame.print(f'Python Script Deleted: {script_to_delete}', text_color=TextColor.GREEN)

                # Update list of installed scripts
                self.update_installed_scripts_tree()

        def installed_script_search() -> None:

            self.update_installed_scripts_tree(search=self.installed_scripts_search_entry.text())

        def get_installed_script_description() -> None:
            """
            Get Installed Script Description
            ================================

            Get the description of the selected script from the installed scripts tree.

            The description is extracted from the first docstring in the script. If no docstring is found, the description
            is set to an empty string. The description is then displayed in the script description text edit.
            """

            # Read description from script
            selected_script = self.installed_scripts_tree.selectedItems()
            script_item = selected_script[0]
            script_path = script_item.text(5)

            with open(script_path, 'r') as script:
                script_lines = script.read()

            try:
                file_description = re.split(r'"""|\'\'\'', script_lines, maxsplit=1)[1]
                file_description = re.split(r'"""|\'\'\'', file_description, maxsplit=1)[0]
                file_description = file_description.strip()
            except IndexError:
                file_description = ''

            self.script_description_text_edit.setPlainText(file_description)
            #self.script_description_text_edit.setMarkdown(file_description)

        def portal_script_search():

            self.update_logik_portal_scripts_tree(search=self.portal_scripts_search_entry.text())

        def browse_script_install_path():
            """
            Browse Script Install Path
            =========================

            Open file browser to select python script install path.
            """

            pyflame.print(f'Script Install Path Set: {self.script_install_path_browse.text()}')

            # Make sure path is writeable, if not, set path to default and show error message
            if not os.access(self.script_install_path_browse.text(), os.W_OK):
                PyFlameMessageWindow(
                    message='Selected path is not writeable.\n\nCheck permissions or select a different path.',
                    type=MessageType.ERROR,
                    )
                self.script_install_path_browse.setText(self.settings.script_install_path)
                return

            # Save settings
            self.settings.save_config(
                config_values={
                    'script_install_path': self.script_install_path_browse.text()
                    }
                )

            # Refresh script trees
            self.update_installed_scripts_tree()
            self.update_logik_portal_scripts_tree()

        #-------------------------------------
        # [Tab 1: Python Scripts Tab]
        #-------------------------------------

        # Labels
        self.installed_scripts_label = PyFlameLabel(
            text='Installed Python Scripts',
            style=Style.UNDERLINE,
            )
        self.portal_scripts_label = PyFlameLabel(
            text='Portal Python Scripts',
            style=Style.UNDERLINE,
            )
        self.script_description_label = PyFlameLabel(
            text='Python Script Description',
            style=Style.UNDERLINE,
            )
        self.installed_scripts_search_label = PyFlameLabel(
            text='Search',
            align=Align.CENTER,
            )
        self.portal_scripts_search_label = PyFlameLabel(
            text='Search',
            align=Align.CENTER,
            )
        self.script_install_path_label = PyFlameLabel(
            text='Script Install Path',
            )

        # Entry
        self.installed_scripts_search_entry = PyFlameEntry(
            text='',
            text_changed=installed_script_search,
            )
        self.portal_scripts_search_entry = PyFlameEntry(
            text='',
            text_changed=portal_script_search,
            )

        # Entry File Browser
        self.script_install_path_browse = PyFlameEntryBrowser(
            text=self.settings.script_install_path,
            browser_title='Set Python Script Install Path',
            browser_type=BrowserType.DIRECTORY,
            browser_window_to_hide=[self.window],
            connect=browse_script_install_path,
            )

        # Text Edit
        self.script_description_text_edit = PyFlameTextEdit(
           text=self.file_description,
           read_only=True,
           )

        # Installed Scripts TreeWidget
        self.installed_scripts_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Version',
                'Flame',
                'Date',
                'Author',
                'Path',
                ],
            connect=get_installed_script_description,
            sorting=True,
            )

        # Portal Scripts TreeWidget
        self.portal_scripts_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Version',
                'Flame Min',
                'Flame Max',
                'Date',
                'Author',
                ],
            connect=self.get_script_description,
            sorting=True,
            )

        # Buttons
        self.script_submit_button = PyFlameButton(
            text='Submit',
            connect=login_check,
            )

        self.install_script_button = PyFlameButton(
            text='Install',
            connect=install_script,
            color=Color.BLUE,
            )

        self.install_local_script_button = PyFlameButton(
            text='Install Local',
            connect=install_local_script,
            )
        self.delete_script_button = PyFlameButton(
            text='Delete',
            connect=delete_script,
            )
        self.script_install_path_browse_button = PyFlameButton(
            text='Browse',
            connect=browse_script_install_path,
            )
        self.python_done_button = PyFlameButton(
            text='Done',
            connect=self.done,
            )

        #-------------------------------------
        # [Python Scripts Tab Layout]
        #-------------------------------------

        self.tab1.grid_layout.addWidget(self.installed_scripts_label, 0, 0, 1, 3)
        self.tab1.grid_layout.addWidget(self.portal_scripts_label, 0, 4, 1, 3)

        self.tab1.grid_layout.addWidget(self.installed_scripts_tree, 1, 0, 6, 3)
        self.tab1.grid_layout.addWidget(self.portal_scripts_tree, 1, 4, 6, 3)

        self.tab1.grid_layout.addWidget(self.delete_script_button, 7, 0)
        self.tab1.grid_layout.addWidget(self.install_local_script_button, 7, 2)
        self.tab1.grid_layout.addWidget(self.script_submit_button, 7, 4)
        self.tab1.grid_layout.addWidget(self.install_script_button, 7, 6)

        self.tab1.grid_layout.addWidget(self.installed_scripts_search_label, 8, 0)
        self.tab1.grid_layout.addWidget(self.installed_scripts_search_entry, 8, 1, 1, 2)
        self.tab1.grid_layout.addWidget(self.portal_scripts_search_label, 8, 4)
        self.tab1.grid_layout.addWidget(self.portal_scripts_search_entry, 8, 5, 1, 2)

        self.tab1.grid_layout.addWidget(self.script_install_path_label, 9, 4)
        self.tab1.grid_layout.addWidget(self.script_install_path_browse, 9, 5, 1, 2)

        self.tab1.grid_layout.addWidget(self.script_description_label, 10, 0, 1, 7)
        self.tab1.grid_layout.addWidget(self.script_description_text_edit, 11, 0, 8, 7)

        self.tab1.grid_layout.addWidget(self.python_done_button, 19, 6)

    def matchbox_tab(self):

        def download_logik_collection():

            def save_config():

                # Save path to config file
                self.settings.save_config(
                    config_values={
                        'matchbox_path': self.matchbox_install_path
                        }
                    )

            def download():

                # Change cursor to busy
                QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

                pyflame.print('Downloading Logik Matchboxes From Logik-Matchbook.org...')

                # Path to download from ftp
                ftp_file_path = os.path.join('/Logik_Matchbox/MatchboxShaderCollection.tgz')

                # Download dest path
                tgz_path = '/opt/Autodesk/shared/python/logik_portal/temp/MatchboxShaderCollection.tgz'

                # Download batch tgz file from ftp
                self.download_file(
                    download_type='Matchbox',
                    file_name='Logik Matchbox',
                    ftp_file_path=ftp_file_path,
                    tgz_path=tgz_path,
                    )

                # Untar matchbox archive
                install_path = os.path.join(self.matchbox_install_path, 'LOGIK')
                print('Matchbox install path:', install_path, '\n')

                command = f'tar -xvf /opt/Autodesk/shared/python/logik_portal/temp/MatchboxShaderCollection.tgz --strip-components 1 -C {install_path}'
                command = command.split(' ', 6)

                create_dir_command = f'mkdir -p {install_path}'
                create_dir_command = create_dir_command.split(' ', 3)

                if not folder_write_permission:
                    try:
                        # use popen to run create_dir_command as sudo
                        p = Popen(['sudo', '-S'] + create_dir_command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]

                        # Sudo untar
                        p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]

                        QtWidgets.QApplication.restoreOverrideCursor()

                    except:
                        QtWidgets.QApplication.restoreOverrideCursor()
                        PyFlameMessageWindow(
                            message=f'Logik Matchbox Collection\n\n{install_path}',
                            title=f'{SCRIPT_NAME}: Install Failed',
                            type=MessageType.ERROR
                            )
                        return
                else:
                    # Create install_path directory if it doesn't exist
                    if not os.path.isdir(install_path):
                        os.makedirs(install_path)

                    # Make sure matchbox tgz file has been downloaded
                    if not os.path.isfile(tgz_path):
                        PyFlameMessageWindow(
                            message=f'Logik Matchbox Collection\n\n Download failed.',
                            type=MessageType.ERROR
                            )
                        QtWidgets.QApplication.restoreOverrideCursor()
                        return

                    # Create install_path directory if it doesn't exist
                    if not os.path.isdir(install_path):
                        os.makedirs(install_path)

                    # Normal untar
                    process = Popen(command, stdin=PIPE, stderr=PIPE, stdout=PIPE, universal_newlines=True)
                    output, error = process.communicate()

                    if process.returncode != 0:
                        raise CalledProcessError(process.returncode, command, output=output, stderr=error)

                    QtWidgets.QApplication.restoreOverrideCursor()


                pyflame.print('Logik Matchbox Collection Installed', text_color=TextColor.GREEN)

            # Open file browser to select install location
            path = pyflame.file_browser(
                title='Select Logik Matchbox Install Directory',
                path=self.settings.matchbox_path,
                select_directory=True,
                window_to_hide=[self.window]
                )

            if path:
                self.matchbox_install_path = path
            else:
                return

            # Save path to config file
            save_config()

            # Check if password is needed to install to selected location
            folder_write_permission = os.access(self.matchbox_install_path, os.W_OK)

            # If matchbox install path is not writeable, get system password and then download and install, otherwise just download and install
            if not folder_write_permission:
                print('Matchbox dest write permission: Not Writeable, need sudo.')
                matchbox_password_window = PyFlamePasswordWindow(message=f'System password needed to install Logik Matchboxes to selected location.')
                system_password = matchbox_password_window.password()
                if system_password:
                    download()
            else:
                print('Matchbox dest write permission: Writeable')
                download()

        def add_matchbox_to_batch():

            def create_matchbox_node(matchbox_file_name):

                # Get cursor position
                cursor_pos = flame.batch.cursor_position

                # Create matchbox node
                matchbox_node = flame.batch.create_node('Matchbox', os.path.join(temp_matchbox_path, matchbox_file_name))
                matchbox_node.pos_x = cursor_pos[0]
                matchbox_node.pos_y = cursor_pos[1]

                matchbox_node.load_node_setup(os.path.join(temp_matchbox_path, selected_matchbox_name))

            # Switch to batch tab
            flame.set_current_tab('Batch')

            # Get selected matchbox name
            selected_matchbox_name = self.matchbox_tree.selectedItems()[0].text(0)

            # Connect to ftp
            self.ftp_download_connect()

            # Get list of matchbox files from ftp
            matchbox_files = self.ftp.nlst('/Logik_Matchbox/Shaders/')
            #print('matchbox_files:', matchbox_files, '\n')

            # Get selected matchbox files
            selected_matchbox_files = [file for file in matchbox_files if selected_matchbox_name + '.' in file]
            #print('selected_matchbox_files:', selected_matchbox_files, '\n')

            # Create temp matchbox directory in temp folder
            temp_matchbox_path = os.path.join(self.temp_folder, selected_matchbox_name)
            if not os.path.isdir(temp_matchbox_path):
                os.makedirs(temp_matchbox_path)

            # Download selected matchbox files from ftp to temp matchbox directory
            for file_path in selected_matchbox_files:
                file_name = file_path.split('/')[-1]
                with open(os.path.join(temp_matchbox_path, file_name), 'wb') as local_file:
                    self.ftp.retrbinary("RETR " + file_path, local_file.write)

            # Get name of glsl file or mx file to load into matchbox node
            glsl_files = [file for file in selected_matchbox_files if file.endswith('.glsl')]

            if glsl_files != []:
                glsl_file = glsl_files[-1]
                matchbox_file_name = glsl_file.split('/')[-1]
            else:
                matchbox_file_name = [file for file in selected_matchbox_files if file.endswith('.mx')][0].rsplit('/', 1)[-1]
            #print('matchbox_file_name:', matchbox_file_name, '\n')

            create_matchbox_node(matchbox_file_name)
            PyFlameMessageWindow(
                message=f'Matchbox added to Batch: {selected_matchbox_name}\n\nYou may have to click in Batch for the node to appear.',
                    )

        def matchbox_search():

            self.update_matchbox_tree(search=self.matchbox_search_entry.text())

        #-------------------------------------
        # [Tab 3: Matchbox Tab]
        #-------------------------------------

        # Labels
        self.matchbox_search_label = PyFlameLabel(
            text='Search',
            align=Align.CENTER,
            )
        self.matchbox_logik_matchbox_collection_label = PyFlameLabel(
            text='Logik Matchbox Collection',
            style=Style.UNDERLINE,
            )
        self.matchbox_desciption_label = PyFlameLabel(
            text='Matchbox Description',
            style=Style.UNDERLINE,
            )

        # Entry
        self.matchbox_search_entry = PyFlameEntry(
            text='',
            text_changed=matchbox_search,
            )

        # Text Edit
        self.matchbox_text_edit = PyFlameTextEdit(
            text=self.file_description,
            read_only=True,
            )

        # Matchbox TreeWidget
        self.matchbox_tree = PyFlameTreeWidget(
            column_names=[
                'Matchbox Name',
                'Shader Type',
                'Author',
                ],
            connect=self.get_matchbox_description,
            sorting=True,
            )
        self.matchbox_tree.setColumnWidth(0, 400)
        self.matchbox_tree.setColumnWidth(1, 300)
        self.matchbox_tree.setColumnWidth(2, 400)

        # Buttons
        self.matchbox_add_to_batch = PyFlameButton(
            text='Add to Batch',
            connect=add_matchbox_to_batch,
            )
        self.matchbox_download_all_button = PyFlameButton(
            text='Download All',
            connect=download_logik_collection,
            color=Color.BLUE,
            )
        self.matchbox_done_button = PyFlameButton(
            text='Done',
            connect=self.done,
            )

        #-------------------------------------
        # [Matchbox Tab Layout]
        #-------------------------------------

        self.tab2.grid_layout.addWidget(self.matchbox_logik_matchbox_collection_label, 0, 0, 1, 7)
        self.tab2.grid_layout.addWidget(self.matchbox_tree, 1, 0, 7, 7)

        self.tab2.grid_layout.addWidget(self.matchbox_add_to_batch, 8, 5)
        self.tab2.grid_layout.addWidget(self.matchbox_download_all_button, 8, 6)

        self.tab2.grid_layout.addWidget(self.matchbox_search_label, 9, 4)
        self.tab2.grid_layout.addWidget(self.matchbox_search_entry, 9, 5, 1, 2)

        self.tab2.grid_layout.addWidget(self.matchbox_desciption_label, 10, 0, 1, 7)
        self.tab2.grid_layout.addWidget(self.matchbox_text_edit, 11, 0, 7, 7)

        self.tab2.grid_layout.addWidget(self.matchbox_done_button, 18, 6)

    def batch_setups_tab(self):

        def batch_setups_download():

            def save_config():
                """
                Save Config
                ===========

                Save path and Open Batch button state to config file.
                """

                self.settings.save_config(
                    config_values={
                        'batch_setup_download_path': download_path,
                        'open_batch': self.open_batch_button.isChecked(),
                        }
                    )

            def open_batch():
                """
                Open Batch
                ==========

                Open batch group in Flame Batch tab after batch setup is downloaded.
                """

                # Get batch setup path
                for f in os.listdir(self.settings.batch_setup_download_path):
                    if f.split('.', 1)[0] == batch_name and f.endswith('.batch'):
                        setup_path = os.path.join(self.settings.batch_setup_download_path, f)
                        # print('setup_path:', setup_path)

                # Create new batch group
                # Names for shelf and schematic reels can be added or deleted here
                # Each reel name must be in quotes and seperated by commas
                schematic_reel_list = ['Plates', 'Elements', 'PreRenders', 'Ref']
                shelf_reel_list = ['Batch Renders']

                self.batch_group = flame.batch.create_batch_group(str(batch_item.text(0)), duration=100, reels=schematic_reel_list, shelf_reels=shelf_reel_list)

                # Load batch setup
                self.batch_group.load_setup(setup_path)

                pyflame.print('Batch Setup Loaded', text_color=TextColor.GREEN)

            download_path = pyflame.file_browser(
                title='Batch Setup Download Path',
                path=self.settings.batch_setup_download_path,
                select_directory=True,
                window_to_hide=[self.window]
                )

            if download_path:

                save_config()

                # Get batch info from script description
                selected_batch = self.batch_setups_tree.selectedItems()
                batch_item = selected_batch[0]
                batch_name = batch_item.text(0)

                # Check path to see if batch already exists
                batch_exists = [b for b in os.listdir(self.settings.batch_setup_download_path) if b.split('.', 1)[0] == batch_name]

                # If batch already exists prompt to overwrite or cancel
                if batch_exists:
                    if not PyFlameMessageWindow(
                        message='Batch Already Exists. Overwrite?',
                        type=MessageType.CONFIRM
                        ):
                        pyflame.print('Batch Setup Download Cancelled')
                        return
                    else:
                        for b in batch_exists:
                            path_to_delete = os.path.join(self.settings.batch_setup_download_path, b)
                            if os.path.isfile(path_to_delete):
                                os.remove(path_to_delete)
                            elif os.path.isdir(path_to_delete):
                                shutil.rmtree(path_to_delete)

                pyflame.print('Downloading Batch Setup...')

                # Path to download from ftp
                ftp_file_path = os.path.join('/Batch_Setups', batch_item.text(1), batch_name + '.tgz')

                # Download dest path
                tgz_path = os.path.join(self.settings.batch_setup_download_path, batch_name + '.tgz')

                # Download batch tgz file from ftp
                self.download_file(
                    download_type='Batch Setup',
                    file_name=batch_name,
                    ftp_file_path=ftp_file_path,
                    tgz_path=tgz_path,
                    )

                # Uncompress tgz file
                tgz_escaped_path = tgz_path.replace(' ', '\ ')
                download_escaped_path = self.settings.batch_setup_download_path.replace(' ', '\ ') + '/'
                tar_command = f'tar -xvf {tgz_escaped_path} -C {download_escaped_path}'
                os.system(tar_command)

                # Delete tgz file
                os.remove(tgz_path)

                if self.open_batch_button.isChecked():
                    open_batch()

        def submit_batch_setup():

            def get_batch_name():
                """
                Fill in Batch Name field once valid batch path is entered. Must end with .batch
                If .flare is in file path, remove it
                """

                if self.submit_batch_path_entry.text().endswith('.batch'):
                    batch_name = self.submit_batch_path_entry.text().rsplit('/', 1)[1][:-6]
                    if batch_name.endswith('.flare'):
                        batch_name = batch_name[:-6]
                    self.submit_batch_name_field.setText(batch_name)
                else:
                    self.submit_batch_name_field.setText('')

            def get_batch_setup_info():
                """
                Get selected batch setup info.
                """

                batch_setup_path = self.submit_batch_path_entry.text()

                if batch_setup_path:
                    self.submit_batch_path_entry.setText(batch_setup_path)
                    batch_name = batch_setup_path.rsplit('/', 1)[1][:-6]
                    if batch_name.endswith('.flare'):
                        batch_name = batch_name[:-6]
                    self.submit_batch_name_field.setText(batch_name)

            def batch_setup_upload():

                def save_config():
                    """
                    Save Config
                    ===========

                    Save path to config file
                    """

                    self.settings.save_config(
                        config_values={
                            'batch_submit_path': self.submit_batch_path_entry.text()
                            }
                        )

                def compress_batch_setup():
                    """
                    Compress Batch Setup
                    ====================

                    Compress batch setup files into a tgz file.
                    """

                    # Add batch files to tar file
                    batch_folder_path = self.submit_batch_path_entry.text()[:-6]
                    print('Batch folder path:', batch_folder_path)

                    batch_root_folder = batch_folder_path.rsplit('/', 1)[0]
                    batch_folder = batch_folder_path.rsplit('/', 1)[1]

                    tar_file_list = batch_folder + ' ' + batch_folder + '.batch'
                    print('TAR file list:', tar_file_list)

                    if batch_folder_path.endswith('.flare'):
                        self.tar_file_name = batch_folder_path.rsplit('/', 1)[1][:-6]
                    else:
                        self.tar_file_name = batch_folder_path.rsplit('/', 1)[1]
                    print('TAR file name:', self.tar_file_name)

                    self.tar_path = os.path.join(self.temp_folder, self.tar_file_name) + '.tgz'
                    print('TAR path:', self.tar_path)

                    tar_command = f'tar -cvf {self.tar_path}  {tar_file_list}'
                    print('TAR command:', tar_command)

                    # Create tgz file
                    os.chdir(batch_root_folder)
                    os.system(tar_command)

                    print('\n')

                    pyflame.print('Batch TAR File Created')

                def create_batch_xml_file():
                    """
                    Create Batch XML File
                    ======================

                    Create xml file with batch setup info.
                    """

                    description_text = self.submit_batch_description_text_edit.toPlainText()
                    description_text = description_text.replace("'", "\"")
                    description_text = description_text.replace('&', '-')

                    # Create batch info file
                    text = []
                    text.insert(0, f"    <batch name='{self.tar_file_name}'>")
                    text.insert(1, f"        <artist>'{self.submit_batch_artist_name_entry.text()}'</artist>")
                    text.insert(2, f"        <flame_version>'{self.submit_batch_flame_version_field.text()}'</flame_version>")
                    text.insert(3, f"        <description>'{description_text}'</description>")
                    text.insert(4, '    </batch>')

                    out_file = open(xml_file, 'w')
                    for line in text:
                        print(line, file=out_file)
                    out_file.close()

                def upload_batch():
                    """
                    Upload Batch Setup
                    ==================

                    Upload batch setup and xml file to ftp.
                    """

                    # Connect to ftp
                    self.ftp_upload_connect()

                    # Check to see if file already exists on ftp
                    ftp_file_list = self.ftp.nlst('/Submit_Batch_Setups')

                    if self.tar_file_name + '.tgz' in ftp_file_list:
                        QtWidgets.QApplication.restoreOverrideCursor()
                        self.ftp.quit()
                        PyFlameMessageWindow(
                            message='Batch Setup Already Exists. Rename And Try Again.',
                            type=MessageType.ERROR
                            )
                        return

                    pyflame.print('Uploading Batch Setup...')

                    # Close window
                    self.submit_batch_window.close()

                    # Upload tgz file to ftp
                    self.upload_file(
                        upload_type='Batch Setup',
                        file_name=self.tar_file_name,
                        xml_path=xml_file,
                        tgz_path=self.tar_path,
                        )

                if not os.path.isfile(self.submit_batch_path_entry.text()):
                    PyFlameMessageWindow(
                        message='Enter valid batch setup path.',
                        type=MessageType.ERROR
                        )
                    return
                elif self.submit_batch_artist_name_entry.text() == '':
                    PyFlameMessageWindow(
                        message='Enter Artist name.',
                        type=MessageType.ERROR
                        )
                    return
                elif self.submit_batch_description_text_edit.toPlainText() == '':
                    PyFlameMessageWindow(
                        message='Enter batch setup description.',
                        type=MessageType.ERROR
                        )
                    return
                else:
                    save_config()
                    compress_batch_setup()
                    xml_file = os.path.join(SCRIPT_PATH, f'{self.tar_file_name}.xml')
                    create_batch_xml_file()
                    upload_batch()

            def close_submit_batch_window():

                self.submit_batch_window.close()

                self.window.show()

            flame_version = str(self.flame_version)
            if flame_version.endswith('.0'):
                flame_version = flame_version[:-2]

            # Create Batch Setup Submit Window
            self.submit_batch_window = PyFlameWindow(
                title='Submit Batch Setup',
                return_pressed=batch_setup_upload,
                grid_layout_columns=6,
                grid_layout_rows=13,
                )

            # Labels
            self.submit_batch_label = PyFlameLabel(
                text='Logik Portal Batch Setup Submit',
                style=Style.UNDERLINE,
                )
            self.submit_batch_path_label = PyFlameLabel(
                text='Batch Path',
                )
            self.submit_batch_name_label = PyFlameLabel(
                text='Batch Name',
                )
            self.submit_batch_flame_version_label = PyFlameLabel(
                text='Flame Version',
                )
            self.submit_batch_artist_name_label = PyFlameLabel(
                text='Artist Name',
                )
            self.submit_batch_description_label = PyFlameLabel(
                text='Batch Description',
                )

            # Entry Fields
            self.submit_batch_name_field = PyFlameEntry(
                text='',
                read_only=True,
                )
            self.submit_batch_artist_name_entry = PyFlameEntry(
                text='',
                )
            self.submit_batch_flame_version_field = PyFlameEntry(
                text=flame_version,
                read_only=True,
                )

            # Entry File Browser
            self.submit_batch_path_entry = PyFlameEntryBrowser(
                text=self.settings.batch_submit_path,
                connect=get_batch_setup_info,
                browser_type=BrowserType.FILE,
                browser_ext=['batch'],
                browser_title='Select Batch Setup',
                browser_window_to_hide=[self.window, self.submit_batch_window]
                )

            get_batch_name()

            # TextEdit
            self.submit_batch_description_text_edit = PyFlameTextEdit(
                text=self.file_description,
                read_only=False,
                )

            # Buttons
            self.submit_batch_upload_button = PyFlameButton(
                text='Upload',
                connect=batch_setup_upload,
                color=Color.BLUE,
                )
            self.submit_cancel_button = PyFlameButton(
                text='Cancel',
                connect=close_submit_batch_window,
                )

            #-------------------------------------
            # [Widget Layout]
            #-------------------------------------

            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_label, 0, 0, 1, 6)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_path_label, 1, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_name_label, 2, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_artist_name_label, 3, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_flame_version_label, 4, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_description_label, 5, 0)

            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_path_entry, 1, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_name_field, 2, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_artist_name_entry, 3, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_flame_version_field, 4, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_description_text_edit, 5, 1, 6, 5)

            self.submit_batch_window.grid_layout.addWidget(self.submit_cancel_button, 12, 4)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_upload_button, 12, 5)

        def batch_setup_search():

            self.update_batch_setups_tree(search=self.batch_setups_search_entry.text())

        #-------------------------------------
        # [Tab 4: Batch Setups Tab]
        #-------------------------------------

        # Labels
        self.batch_setups_label = PyFlameLabel(
            text='Batch Setups',
            style=Style.UNDERLINE,
            )
        self.batch_setups_desciption_label = PyFlameLabel(
            text='Batch Setup Description',
            style=Style.UNDERLINE,
            )
        self.batch_setups_search_label = PyFlameLabel(
            text='Search',
            align=Align.CENTER,
            )

        # Entry
        self.batch_setups_search_entry = PyFlameEntry(
            text='',
            text_changed=batch_setup_search,
            )

        # Text Edit
        self.batch_setups_text_edit = PyFlameTextEdit(
            text=self.file_description,
            read_only=True,
            )

        # Batch Setups TreeWidget
        self.batch_setups_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Flame',
                'Artist',
                ],
            connect=self.get_batch_description,
            sorting=True,
            )

        self.batch_setups_tree.setColumnWidth(0, 600)
        self.batch_setups_tree.setColumnWidth(1, 100)
        self.batch_setups_tree.setColumnWidth(2, 300)

        # Disable batch download button if current flame version older than batch minimum
        self.batch_setups_tree.clicked.connect(self.check_batch_flame_version)

        # Push Buttons
        self.open_batch_button = PyFlamePushButton(
            text=' Open Batch',
            button_checked=self.settings.open_batch,
            tooltip='Opens batch setup after download is finished',
            )

        # Buttons
        self.batch_setups_submit_button = PyFlameButton(
            text='Submit',
            connect=submit_batch_setup,
            )
        self.batch_setups_download_button = PyFlameButton(
            text='Download',
            connect=batch_setups_download,
            color=Color.BLUE,
            )
        self.batch_done_button = PyFlameButton(
            text='Done',
            connect=self.done,
            )

        #-------------------------------------
        # [Batch Setups Tab Layout]
        #-------------------------------------

        self.tab3.grid_layout.addWidget(self.batch_setups_label, 0, 0, 1, 7)

        self.tab3.grid_layout.addWidget(self.batch_setups_tree, 1, 0, 7, 7)

        self.tab3.grid_layout.addWidget(self.batch_setups_submit_button, 8, 0)
        self.tab3.grid_layout.addWidget(self.open_batch_button, 8, 5)
        self.tab3.grid_layout.addWidget(self.batch_setups_download_button, 8, 6)

        self.tab3.grid_layout.addWidget(self.batch_setups_search_label, 9, 4)
        self.tab3.grid_layout.addWidget(self.batch_setups_search_entry, 9, 5, 1, 2)

        self.tab3.grid_layout.addWidget(self.batch_setups_desciption_label, 10, 0, 1, 7)
        self.tab3.grid_layout.addWidget(self.batch_setups_text_edit, 11, 0, 7, 7)

        self.tab3.grid_layout.addWidget(self.batch_done_button, 18, 6)

    def inference_nodes_tab(self):

        def inference_node_download() -> None:
            """
            Inference Node Download
            ========================

            Download selected inference node from Logik Portal. Uncompress and add to batch if selected.

            Notes
            -----
                - Download inference node tgz file from ftp.
                - Uncompress tgz file.
                - Add inference node to batch if selected.
            """

            def save_config() -> None:
                """
                Save Config
                ===========

                Save path and add to batch settings to config file.
                """

                self.settings.save_config(
                    config_values={
                            'inference_node_download_path': inference_node_download_path,
                            'inference_node_add_to_batch': self.inference_node_add_to_batch_pushbutton.isChecked(),
                            }
                        )

            def download_node() -> None:

                def add_inference_node_to_batch() -> None:
                    """
                    Add Inference Node To Batch
                    ===========================

                    Add downloaded inference node to batch. Centers node in batch view.
                    """

                    pyflame.print('Adding Inference Node to Batch...')

                    # Switch to batch tab
                    flame.set_current_tab('Batch')

                    # Get inference node path
                    inference_node_path = os.path.join(inference_node_download_path, inference_node_name, inference_node_name + '.onnx')
                    if not os.path.isfile(inference_node_path):
                        inference_node_path = os.path.join(inference_node_download_path, inference_node_name, inference_node_name + '.inf')

                    # Get cursor position
                    cursor_pos = flame.batch.cursor_position

                    # Create inference node
                    inference_node = flame.batch.create_node('Inference', inference_node_path)
                    inference_node.pos_x = cursor_pos[0]
                    inference_node.pos_y = cursor_pos[1]

                    flame.batch.select_nodes([inference_node])

                    flame.batch.frame_selected()

                    pyflame.print('Inference Node Added to Batch', text_color=TextColor.GREEN)

                pyflame.print('Downloading Inference Node...')

                # Get selected inference node name
                selected_node = self.inference_node_tree.selectedItems()
                selected_node_item = selected_node[0]
                inference_node_name = selected_node_item.text(0).replace(' ', '_')

                # Path to download
                ftp_file_path = os.path.join('/Inference_Nodes', selected_node_item.text(1), inference_node_name + '.tgz')
                #print('ftp_file_path:', ftp_file_path, '\n')

                # Download dest path
                tgz_path = os.path.join(inference_node_download_path, inference_node_name + '.tgz')
                #print('tgz_path:', tgz_path, '\n')

                # Download archive tgz file
                self.download_file(
                    download_type='Inference Node',
                    file_name=inference_node_name,
                    ftp_file_path=ftp_file_path,
                    tgz_path=tgz_path,
                    )

                # Uncompress tgz file
                tgz_escaped_path = tgz_path.replace(' ', '\ ')
                download_escaped_path = inference_node_download_path.replace(' ', '\ ') + '/'
                tar_command = f'tar -xvf {tgz_escaped_path} -C {download_escaped_path}'
                os.system(tar_command)

                # Delete tgz file
                os.remove(tgz_path)

                if self.inference_node_add_to_batch_pushbutton.isChecked():
                    print('\n')
                    add_inference_node_to_batch()

            # Get path to download archive to
            inference_node_download_path = pyflame.file_browser(
                title='Select Download Path',
                path=self.settings.inference_node_download_path,
                select_directory=True,
                window_to_hide=[self.window]
                )

            if inference_node_download_path:
                save_config()
                download_node()

                pyflame.print('Inference Node Download Complete', text_color=TextColor.GREEN)

        def inference_node_submit() -> None:
            """
            Inference Node Submit
            =====================

            Submit inference node to Logik Portal.

            Uploaded inference nodes must have a link to the original source in the description. Nodes without a link
            will not be accepted.
            """

            def get_inference_node_name():
                """
                Get Inference Node Name
                ========================

                Fill in Inference Node Name field once valid file is selected.
                """

                # Check if file is valid, if so fill in Inference Node Name field
                if os.path.isfile(self.submit_inference_node_path_entry.text()):
                    self.submit_inference_node_name_field.setText(os.path.basename(self.submit_inference_node_path_entry.text()).split('.')[0])

            def inference_node_upload():
                """
                Inference Node Upload
                =====================

                Upload inference node to Logik Portal.

                Notes
                -----
                    - Check to make sure all fields are filled in.
                    - Compress inference node files into a tgz file.
                    - Create xml file with inference node info.
                    - Upload tgz file and xml file to ftp.
                """

                def save_config():
                    """
                    Save Config
                    ===========

                    Save path to config file.
                    """

                    self.settings.save_config(
                        config_values={
                            'inference_node_submit_path': self.submit_inference_node_path_entry.text()
                            }
                        )

                def compress_inference_node() -> str:
                    """
                    Compress Inference Node
                    =======================

                    Create tar(tgz) file of inference node files. Either INF or ONNX + JSON files.
                    """

                    pyflame.print('Creating Inference Node TAR file...')

                    inference_node = self.submit_inference_node_path_entry.text()
                    #inference_node = inference_node.replace(' ', '\ ') # Escape spaces in file path
                    if inference_node.endswith('.onnx'):
                        inference_node_json = inference_node.replace('.onnx', '.json')
                    else:
                        inference_node_json = None

                    self.tar_file_name = self.submit_inference_node_name_field.text()
                    print('TAR file name:', self.tar_file_name)

                    self.tar_file_path = os.path.join(self.temp_folder, self.tar_file_name) + '.tgz'
                    print('TAR file path:', self.tar_file_path)

                    # Create list of files to add to tar file. Either INF or ONNX + JSON files.
                    if inference_node_json:
                        print('Adding ONNX and JSON files to TAR file...')
                        #$tar_file_list = f'{inference_node} {inference_node_json}'
                        tar_file_list = [inference_node, inference_node_json]
                    else:
                        print('Adding INF file to TAR file...')
                        #tar_file_list = inference_node
                        tar_file_list = [inference_node]
                    #print('TAR file list:', tar_file_list)

                    print('\n', end='')

                    # Open the tar file for writing
                    with tarfile.open(self.tar_file_path, "w") as tar:
                        for file_path in tar_file_list:
                            #print('file_path:', file_path)
                            # Extract the file name from the full path
                            file_name = os.path.basename(file_path)
                            #print('file_name:', file_name)
                            # Create the new path within the tar file
                            arcname = os.path.join(self.tar_file_name, file_name)
                            #print('arcname:', arcname)
                            # Add the file to the tar file with the new path
                            tar.add(file_path, arcname=arcname)

                    print('\n', end='')

                    pyflame.print('Inference Node TAR File Created')

                def create_inference_node_xml_file() -> bool:

                    def get_description_text():
                        """
                        Get Description Text
                        ====================

                        Get description text from text edit field and replace single quotes with double quotes and '&' with '-'.
                        """

                        description_text = self.submit_inference_node_description_text_edit.text()
                        description_text = description_text.replace("'", "\"")
                        description_text = description_text.replace('&', '-')

                        return description_text

                    def get_tar_file_size() -> Union[str, bool]:
                        """
                        Get Tar File Size
                        =================

                        Determines the size of the tar file specified by tar_file_path. If the file size exceeds 2GB,
                        an error message is displayed and the function returns False. Otherwise, the size of the file
                        is returned as a string in megabytes (MB).

                        Args
                        ----
                            tar_file_path (str):
                                The path to the tar file.

                        Returns
                        -------
                            Union[str, bool]:
                                The size of the tar file in MB as a string if the size is within the limit. Returns False
                                if the file size exceeds 2GB or if there is an error accessing the file.

                        Raises
                        ------
                            OSError
                                If there is an error accessing the file, an error message is displayed and the function
                                returns False.

                        Notes
                        -----
                            - The size limit is defined as 2GB.
                            - The file size is converted to megabytes (MB) for display.
                            - The function uses `os.path.getsize` to determine the file size in bytes.
                        """

                        # Define the size limit in bytes (2GB)
                        SIZE_LIMIT_MB = 2000
                        SIZE_LIMIT_BYTES = SIZE_LIMIT_MB * 1024 * 1024

                        try:
                            # Get tar file size in bytes
                            tar_file_size_bytes = os.path.getsize(self.tar_file_path)

                            # Check if the file size exceeds the 2GB limit
                            if tar_file_size_bytes > SIZE_LIMIT_BYTES:
                                PyFlameMessageWindow(
                                    message='File too large. Reduce size and try again.',
                                    type=MessageType.ERROR
                                )
                                return False

                            # Convert the file size to MB for display
                            tar_file_size_mb = tar_file_size_bytes // (1024 * 1024)
                            self.tar_file_size = f'{tar_file_size_mb} MB' if tar_file_size_mb > 1 else '> 1 MB'

                            pyflame.print(f'Inference Node TAR File Size: {self.tar_file_size}')

                            return True

                        except OSError as e:
                            PyFlameMessageWindow(
                                message=f"Error accessing file: {e}",
                                type=MessageType.ERROR
                            )
                            return False

                    def write_xml_file() -> None:
                        """
                        Write XML File
                        ==============

                        Write XML file for inference node.
                        """

                        text = [
                            "\n",
                            f"    <inference_node name='{self.tar_file_name}'>",
                            f"        <flame_version>'{self.submit_inference_node_flame_version_field.text()}'</flame_version>",
                            f"        <file_size>'{self.tar_file_size}'</file_size>",
                            f"        <description>'{description_text}'</description>",
                            "    </inference_node>"
                        ]

                        self.inference_node_xml_file = os.path.join(self.temp_folder, f'{self.tar_file_name}.xml')

                        with open(self.inference_node_xml_file, 'w') as out_file:
                            for line in text:
                                print(line, file=out_file)

                    # Get inference node description text
                    description_text = get_description_text()

                    # Get tar file size
                    tar_file_size = get_tar_file_size()
                    if not tar_file_size:
                        return False

                    # Write out xml file
                    write_xml_file()

                    return True

                def upload_inference_node():

                    pyflame.print('Uploading Inference Node...')

                    self.ftp_upload_connect()

                    # Check to see if file already exists on ftp
                    ftp_file_list = self.ftp.nlst('/Submit_Inference_Node')

                    if self.tar_file_name + '.tgz' in ftp_file_list:
                        QtWidgets.QApplication.restoreOverrideCursor()
                        self.ftp.quit()
                        PyFlameMessageWindow(
                            message='Inference Node already exists. Rename and try again.',
                            type=MessageType.ERROR
                        )
                        return

                    # Close window
                    self.submit_inference_node_window.close()

                    # Upload tgz file to ftp
                    self.upload_file(
                        upload_type='Inference Node',
                        file_name=self.tar_file_name,
                        xml_path=self.inference_node_xml_file,
                        tgz_path=self.tar_file_path,
                        )

                # Check for valid path to ONNX or INF file
                if not os.path.isfile(self.submit_inference_node_path_entry.text()):
                    PyFlameMessageWindow(
                        message='Path to ONNX of INF file is not valid. Try selecting file again.',
                        type=MessageType.ERROR
                        )
                    return

                # If ONNX file, check for matching JSON file, if not give error.
                if self.submit_inference_node_path_entry.text().endswith('.onnx'):
                    node_path = self.submit_inference_node_path_entry.text().rsplit('/', 1)[0]
                    json_file = self.submit_inference_node_path_entry.text().replace('.onnx', '.json')
                    if not os.path.isfile(os.path.join(node_path, json_file)):
                        PyFlameMessageWindow(
                            message='ONNX file must have a JSON file with a matching file name.\n\nExample:\n\n    inference_node.onnx\n    inference_node.json',
                            type=MessageType.ERROR
                            )
                        return

                # Check for Inference Node Description
                if self.submit_inference_node_description_text_edit.toPlainText() == '':
                    PyFlameMessageWindow(
                        message='Enter Inference Node description.',
                        type=MessageType.ERROR
                        )
                    return

                # If all fields are filled in, save config, compress node file(s), create xml file, and upload to Logik Portal.
                else:
                    save_config()
                    compress_inference_node()
                    xml_file_created = create_inference_node_xml_file()
                    if xml_file_created:
                        upload_inference_node()

            PyFlameMessageWindow(
                message="""
Please ensure that any inference nodes you upload are open source and include a link to the original model source in the description. Nodes without a source link will not be accepted.

If you would like to take credit for creating or submitting a node, just add your name to the description, as names are no longer being added to the node list.

Thanks for contributing!
            """,
            title='Inference Node Upload Requirements',
            )

            flame_version = str(self.flame_version)
            if flame_version.endswith('.0'):
                flame_version = flame_version[:-2]

            # Create Inference Node Submit Window
            self.submit_inference_node_window = PyFlameWindow(
                title='Submit Inference Node',
                return_pressed=inference_node_upload,
                grid_layout_columns=6,
                grid_layout_rows=13,
                )

            # Labels
            self.submit_inference_node_label = PyFlameLabel(
                text='Logik Portal Inference Node Submit',
                style=Style.UNDERLINE,
                )
            self.submit_inference_path_label = PyFlameLabel(
                text='Inference Node Path',
                )
            self.submit_inference_node_name_label = PyFlameLabel(
                text='Inference Node Name',
                )
            self.submit_inference_node_flame_version_label = PyFlameLabel(
                text='Flame Version',
                )
            self.submit_inference_node_description_label = PyFlameLabel(
                text='Description',
                )

            # Entries
            self.submit_inference_node_name_field = PyFlameEntry(
                text='',
                read_only=True,
                )
            self.submit_inference_node_flame_version_field = PyFlameEntry(
                text=flame_version,
                read_only=True,
                )
            self.submit_inference_node_path_entry = PyFlameEntry(
                text=self.settings.inference_node_submit_path,
                )
            get_inference_node_name()

            # Entry File Browser
            self.submit_inference_node_path_entry = PyFlameEntryBrowser(
                text=self.settings.inference_node_submit_path,
                connect=get_inference_node_name,
                browser_ext=['onnx', 'inf'],
                browser_title='Select Inference Node (ONNX/INF)',
                browser_window_to_hide=[self.window, self.submit_inference_node_window]
                )

            # TextEdit
            self.submit_inference_node_description_text_edit = PyFlameTextEdit(
                text=self.file_description,
                read_only=False,
                )

            # Buttons
            self.submit_inference_node_upload_button = PyFlameButton(
                text='Upload',
                connect=inference_node_upload,
                color=Color.BLUE,
                )
            self.submit_archive_cancel_button = PyFlameButton(
                text='Cancel',
                connect=self.submit_inference_node_window.close,
                )

            #-------------------------------------
            # [Widget Layout]
            #-------------------------------------

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_label, 0, 0, 1, 6)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_path_label, 1, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_name_label, 2, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_flame_version_label, 3, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_description_label, 4, 0)

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_path_entry, 1, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_name_field, 2, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_flame_version_field, 3, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_description_text_edit, 4, 1, 7, 5)

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_archive_cancel_button, 12, 4)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_upload_button, 12, 5)

        def inference_node_search() -> None:
            """
            Inference Node Search
            =====================

            Search for inference nodes in the inference node tree. Update tree with search results as user types.
            """

            self.update_inference_node_tree(search=self.inference_node_search_entry.text())

        #-------------------------------------
        # [Tab 5: Inference Nodes]
        #-------------------------------------

        # Labels
        self.inference_nodes_label = PyFlameLabel(
            text='Inference Nodes',
            style=Style.UNDERLINE,
            )
        self.inference_node_description_label = PyFlameLabel(
            text='Inference Node Description',
            style=Style.UNDERLINE,
            )
        self.inference_node_search_label = PyFlameLabel(
            text='Search',
            align=Align.CENTER,
            )

        # Entry
        self.inference_node_search_entry = PyFlameEntry(
            text='',
            text_changed=inference_node_search
            )

        # Text Edit
        self.inference_node_description_text_edit = PyFlameTextEdit(
            text=self.file_description,
            read_only=True,
            )

        # TreeWidgets
        self.inference_node_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Flame',
                'Size',
                ],
            connect=self.get_inference_node_description,
            sorting=True,
            )

        self.inference_node_tree.setColumnWidth(0, 1000)
        self.inference_node_tree.setColumnWidth(1, 100)
        self.inference_node_tree.setColumnWidth(2, 100)
        self.inference_node_tree.setTextElideMode(QtCore.Qt.ElideNone)

        #Push Buttons
        self.inference_node_add_to_batch_pushbutton = PyFlamePushButton(
            text=' Add to Batch',
            button_checked=self.settings.inference_node_add_to_batch,
            tooltip='Add Inference Node to Batch Setup',
            )

        # Buttons
        self.inference_node_submit_button = PyFlameButton(
            text='Submit',
            connect=inference_node_submit,
            )
        self.inference_node_download_button = PyFlameButton(
            text='Download',
            connect=inference_node_download,
            color=Color.BLUE,
            )
        self.inference_node_done_button = PyFlameButton(
            text='Done',
            connect=self.done,
            )

        #-------------------------------------
        # [Inference Nodes Tab Layout]
        #-------------------------------------

        self.tab4.grid_layout.addWidget(self.inference_nodes_label, 0, 0, 1, 7)

        self.tab4.grid_layout.addWidget(self.inference_node_tree, 1, 0, 7, 7)

        self.tab4.grid_layout.addWidget(self.inference_node_submit_button, 8, 0)
        self.tab4.grid_layout.addWidget(self.inference_node_add_to_batch_pushbutton, 8, 5)
        self.tab4.grid_layout.addWidget(self.inference_node_download_button, 8, 6)

        self.tab4.grid_layout.addWidget(self.inference_node_search_label, 9, 4)
        self.tab4.grid_layout.addWidget(self.inference_node_search_entry, 9, 5, 1, 2)

        self.tab4.grid_layout.addWidget(self.inference_node_description_label, 10, 0, 1, 7)
        self.tab4.grid_layout.addWidget(self.inference_node_description_text_edit, 11, 0, 7, 7)

        self.tab4.grid_layout.addWidget(self.inference_node_done_button, 18, 6)

    #-------------------------------------

    def get_updates(self) -> None:
        """
        Get Updates
        ===========

        Get updates.txt from Logik Portal and display in the descriptions text edit when the Portal first opens.
        """

        def apply_update(label, text_window):

            # Set the script description label to Logik Portal Updates
            label.setText('Logik Portal Updates')

            # Add updates to description text edit
            text_window.setPlainText(self.updates)
            #text_window.setMarkdown(self.updates)

        # Get the updates from the FTP server
        lines = []
        self.ftp.retrlines('RETR /Updates/updates.txt', lines.append)
        self.updates = '\n'.join(lines)
        # print('updates: ', self.updates)

        # Set the updates text edit to the updates
        if self.settings.last_tab == 0:
            apply_update(self.script_description_label, self.script_description_text_edit)
        elif self.settings.last_tab == 1:
            apply_update(self.matchbox_desciption_label, self.matchbox_text_edit)
        elif self.settings.last_tab == 2:
            apply_update(self.batch_setups_desciption_label, self.batch_setups_text_edit)
        elif self.settings.last_tab == 3:
            apply_update(self.inference_node_description_label, self.inference_node_description_text_edit)

    def get_script_info(self):
        """
        Get Script Info
        ===============

        Get script info from the script and fill in the submit fields.

        Script info is extracted from the first docstring in the script.

        Script info should be in the following format:

        '''
        Script Version: 1.0.0
        Flame Version: 2021.2
        Written by: John Smith
        Creation Date: 01.01.2021
        Update Date: 01.01.2021

        Description:
            This is a test script.
        '''
        """


        def extract_first_docstring(filename):
            """
            Extracts the first docstring from a python file and returns it as a string.
            Checks for both types of triple quote docstring formats.
            """

            with open(filename, 'r') as f:
                content = f.read()

            # Regular expression to match docstrings
            pattern = re.compile(r'(\'\'\'(.*?)\'\'\'|\"\"\"(.*?)\"\"\")', re.DOTALL)
            match = pattern.search(content)

            if match:
                return match.group(2) if match.group(2) else match.group(3)

            return ''

        # Get script description from script
        script_path = self.submit_script_path_entry.text()
        file_description = extract_first_docstring(script_path)
        file_description = file_description.strip()
        # print('file_description:', file_description)

        # Fill in script name field
        script_name = self.submit_script_path_entry.text().rsplit('/', 1)[1][:-3]
        script_name = script_name.replace('_', ' ')
        self.submit_script_name_field.setText(script_name)
        # print('script_name:', script_name)

        # Fill submit fields if data in present in script
        file_description_lines = file_description.splitlines()
        for line in file_description_lines:
            if 'Script Version: ' in line:
                script_version = line.split('Script Version: ', 1)[1]
                self.submit_script_version_entry.setText(script_version)
                # print('script_version:', script_version)
            elif 'Flame Version: ' in line:
                flame_version = line.split('Flame Version: ', 1)[1]
                self.submit_script_flame_version_entry.setText(flame_version)
                # print('flame_version:', flame_version)
            elif 'Written by: ' in line:
                script_dev = line.split('Written by: ', 1)[1]
                self.submit_script_dev_name_entry.setText(script_dev)
                # print('script_dev:', script_dev)
            elif 'Creation Date: ' in line:
                script_date = line.split('Creation Date: ', 1)[1]
            elif 'Update Date: ' in line:
                script_date = line.split('Update Date: ', 1)[1]
                self.submit_script_date_entry.setText(script_date)
                # print('script_date:', script_date, '\n')

        self.submit_script_description_text_edit.setText(file_description)

    def update_script_info(self):
        """
        Update Script Info
        ==================

        Fill in Script info fields once valid script path is entered. Must end with .py
        """

        if self.submit_script_path_entry.text().endswith('.py'):
            self.get_script_info()
        else:
            self.submit_script_name_field.setText('')
            self.submit_script_version_label_02.setText('')
            self.submit_script_flame_version_label_02.setText('')
            self.submit_script_date_label_02.setText('')
            self.submit_script_dev_name_label_02.setText('')
            self.submit_script_description_text_edit.setPlainText('')

    #-------------------------------------
    # [Python Scripts]
    #-------------------------------------

    def check_script_flame_version(self, tree) -> None:
        """
        Check Script Flame Version
        ==========================

        Check if script is compatible with current version of Flame.
        If script won't work with current version of Flame, disable the install button.

        Args:
        -----
            tree:
                PyFlameTreeWidget
        """

        selected_script = tree.selectedItems()
        script_item = selected_script[0]
        script_name = script_item.text(0)
        script_flame_version = script_item.text(2)
        script_flame_max_version = script_item.text(3)

        if float(self.flame_version) < float(script_flame_version):
            print(f'--> {script_name}: Requires newer version of Flame.\n')
            self.install_script_button.setEnabled(False)
        if script_flame_max_version != 'Latest':
            if float(script_flame_max_version) < float(self.flame_version):
                print(f'--> {script_name}: Does not work with this version of Flame.\n')
                self.install_script_button.setEnabled(False)
        else:
            print(f'--> {script_name}: Flame version compatible.\n')
            self.install_script_button.setEnabled(True)

    def get_script_description(self) -> None:
        """
        Get Script Description
        ======================

        Get the description of the selected script from the python scripts tree.
        """

        pyflame.print('Getting Python Script Description...')

        # Switch text edit label to 'Script Description'. This is named 'Logik Portal Updates' when the script first loads.
        self.script_description_label.setText('Python Script Description')

        # Get selected script info
        selected_item = self.portal_scripts_tree.selectedItems()
        script = selected_item[0]
        script_name = script.text(0)
        author = script.text(4)

        # Get script description from ftp
        xml_tree = ET.parse(self.python_scripts_xml_path)
        root = xml_tree.getroot()

        for script in root.findall('script'):
            if script.get('name') == script_name:
                self.script_description_text_edit.setPlainText(script[-1].text[1:-1])
                #self.script_description_text_edit.setMarkdown(script[-1].text[1:-1])

    def update_logik_portal_scripts_tree(self, search: str=None):
        """
        Update Logik Portal Scripts Tree
        ================================

        Add Logik Portal python scripts to Portal Python Scripts tree.

        Get script info from xml file and add to tree list. If a newer version of the script exists on the ftp, highlight the script entry.
        If the script requires a newer version of flame, grey out the script entry.

        Args:
        -----
            search (str, optional):
                The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                (Default: None)
        """

        def add_script():

            script_version = python_script.find('script_version').text.strip("'")
            flame_min_version = python_script.find('flame_version').text.strip("'")
            try:
                flame_max_version = python_script.find('flame_max_version').text.strip("'")
            except:
                flame_max_version = 'Latest'
            date = python_script.find('date').text.strip("'")
            developer_name = python_script.find('developer').text.strip("'")

            # Add script info to tree list
            new_script = QtWidgets.QTreeWidgetItem(self.portal_scripts_tree, [script_name, script_version, flame_min_version, flame_max_version, date, developer_name])

            # If newer version of script exists on ftp, highlight script entry
            if script_name in self.installed_script_dict:
                installed_script_version = self.installed_script_dict.get(script_name)
                try:
                    if float(script_version) > float(installed_script_version):
                        new_script.setForeground(0, QtGui.QColor('#ffffff'))
                        new_script.setForeground(1, QtGui.QColor('#ffffff'))
                        new_script.setForeground(2, QtGui.QColor('#ffffff'))
                        new_script.setForeground(3, QtGui.QColor('#ffffff'))
                        new_script.setForeground(4, QtGui.QColor('#ffffff'))
                        new_script.setForeground(5, QtGui.QColor('#ffffff'))
                except:
                    pass

            # if script requires newer version of flame grey out script entry
            if float(self.flame_version) < float(flame_min_version):
                new_script.setForeground(0, QtGui.QColor('#555555'))
                new_script.setForeground(1, QtGui.QColor('#555555'))
                new_script.setForeground(2, QtGui.QColor('#555555'))
                new_script.setForeground(3, QtGui.QColor('#555555'))
                new_script.setForeground(4, QtGui.QColor('#555555'))
                new_script.setForeground(5, QtGui.QColor('#555555'))

            # If scripts max_flame_version if not equal to the current flame version or 'Latest', grey out the script entry.
            if flame_max_version != 'Latest':
                if float(flame_max_version) < float(self.flame_version):
                    new_script.setForeground(0, QtGui.QColor('#555555'))
                    new_script.setForeground(1, QtGui.QColor('#555555'))
                    new_script.setForeground(2, QtGui.QColor('#555555'))
                    new_script.setForeground(3, QtGui.QColor('#555555'))
                    new_script.setForeground(4, QtGui.QColor('#555555'))
                    new_script.setForeground(5, QtGui.QColor('#555555'))

            self.ftp_script_list.append(script_name)

        pyflame.print('Updating Python Scripts List...')

        # Clear Portal Scripts tree
        self.portal_scripts_tree.clear()

        # Read in Logik Portal Python Scripts xml file
        xml_tree = ET.parse(self.python_scripts_xml_path)
        root = xml_tree.getroot()

        # Add items from xml to Portal Scripts tree. If search string is present, only add items that match the search string.
        for python_script in root.findall('./script'):
            script_name = python_script.get('name')
            if search:
                if search.lower() in script_name.lower():
                    add_script()
            else:
                add_script()

        # Select top item in Portal Scripts tree
        self.portal_scripts_tree.setCurrentItem(self.portal_scripts_tree.topLevelItem(0))

        # Get selected python script description if python script is selected.
        try:
            self.get_script_description()
        except:
            print('Unable to get Python Script description. No Python Script selected\n')

        # Set width of Portal Scripts tree headers
        self.portal_scripts_tree.resizeColumnToContents(0)
        self.portal_scripts_tree.resizeColumnToContents(4)
        self.portal_scripts_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.portal_scripts_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.portal_scripts_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.portal_scripts_tree.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.portal_scripts_tree.header().setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.portal_scripts_tree.header().setSectionResizeMode(5, QtWidgets.QHeaderView.Fixed)

        pyflame.print('Python Scripts List Updated', text_color=TextColor.GREEN)

    def update_installed_scripts_tree(self, search: str=None):
        """
        Update Installed Scripts Tree
        =============================

        Update the installed scripts tree with the scripts found in the shared script path.

        Args:
        -----
            search (str, optional):
                The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                (Default: None)
        """

        def add_script():

            def date_flip(date):
                """
                Date Flip
                =========

                Swap date from mm.dd.yy to yy.mm.dd for python scripts list sorting.

                Args:
                -----
                    date:
                        str: Date in mm.dd.yy format.
                """

                date = date.split('.')
                date = date[2] + '.' + date[0] + '.' + date[1]

                return date

            script_path = os.path.join(root, script)
            # print('script_path:', script_path)

            # Read in script to separate out comments
            script_code = open(script_path, 'r')
            script_lines = script_code.read().splitlines()[1:]
            script_code.close()

            # Split out script info to comment list
            comment_lines = []

            for line in script_lines:
                if line != '':
                    comment_lines.append(line)
                else:
                    break

            # Get script info from comment list
            try:
                script_version = [line.split('Script Version: ', 1)[1] for line in comment_lines if 'Script Version: ' in line]
                if script_version:
                    script_version = script_version[0]
                else:
                    script_version = [line.split("'", 2)[1] for line in script_lines if 'SCRIPT_VERSION = ' in line] # For old scripts
                    if script_version:
                        script_version = script_version[0]
                        if 'v' in script_version:
                            script_version = script_version[1:]
                    else:
                        script_version = ''
            except:
                script_version = ''

            try:
                script_date = [line.split('Update Date: ', 1)[1] for line in comment_lines if 'Update Date: ' in line]
                if script_date:
                    script_date = script_date[0]
                else:
                    script_date = [line.split(' ', 1)[1] for line in comment_lines if 'Updated:' in line] # For old scripts
                    if script_date:
                        script_date = script_date[0]
                    else:
                        script_date = ''
            except:
                script_date = ''

            if script_date != '':
                script_date = date_flip(script_date)

            # print('script_date:', script_date)

            try:
                script_dev = [line.split('Written by: ', 1)[1] for line in comment_lines if 'Written by' in line]
                if script_dev:
                    script_dev = script_dev[0]
                else:
                    script_dev = [line.split('Created by ', 1)[1] for line in comment_lines if 'Created by' in line] # For old scripts
                    if script_dev:
                        script_dev = script_dev[0]
                    else:
                        script_dev = ''
            except:
                script_dev = ''
            # print('script_dev:', script_dev)

            try:
                script_flame_version = [line.split('Flame Version: ', 1)[1] for line in comment_lines if 'Flame Version: ' in line]
                if script_flame_version:
                    script_flame_version = script_flame_version[0].split(' ', 1)[0]
                else:
                    script_flame_version = [line.split(' ', 1)[1] for line in comment_lines if 'Flame 20' in line] # For old scripts
                    if script_flame_version:
                        script_flame_version = script_flame_version[0].split(' ', 1)[0]
                    else:
                        script_flame_version = ''
            except:
                script_version = ''
            # print('script_min_flame_version:', script_flame_version)

            # Add script to tree
            QtWidgets.QTreeWidgetItem(self.installed_scripts_tree, [script_name, script_version, script_flame_version, script_date, script_dev, script_path])

            self.installed_script_dict.update({script_name : script_version})

        pyflame.print('Updating Installed Scripts List...')

        # Clear installed scripts tree
        self.installed_scripts_tree.clear()

        for root, dirs, files in os.walk(self.settings.script_install_path, followlinks=True):
            if root[len(self.settings.script_install_path):].count(os.sep) < 2:
                for script in files:
                    if script.endswith('.py'):
                        if not script.startswith(('.', 'flame_widgets', 'pyflame_lib')):

                            # Get script name from .py file name
                            script_name = script[:-3]
                            script_name = script_name.replace('_', ' ')
                            #print('script_name:', script_name)

                            # If search string is provided, filter scripts. Otherwise, add all scripts.
                            if search:
                                if search.lower() in script_name.lower():
                                    add_script()
                            else:
                                add_script()

        # Set width of tree headers
        self.installed_scripts_tree.resizeColumnToContents(0)
        self.installed_scripts_tree.resizeColumnToContents(4)
        self.installed_scripts_tree.resizeColumnToContents(5)
        self.installed_scripts_tree.header().setSectionResizeMode(0, QtWidgets.QHeaderView.Fixed)
        self.installed_scripts_tree.header().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.installed_scripts_tree.header().setSectionResizeMode(2, QtWidgets.QHeaderView.Fixed)
        self.installed_scripts_tree.header().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.installed_scripts_tree.header().setSectionResizeMode(4, QtWidgets.QHeaderView.Fixed)
        self.installed_scripts_tree.header().setSectionResizeMode(5, QtWidgets.QHeaderView.Fixed)

        # Select first item in tree
        self.installed_scripts_tree.setCurrentItem(self.installed_scripts_tree.topLevelItem(0))

        pyflame.print('Installed Scripts List Updated', text_color=TextColor.GREEN)

    #-------------------------------------
    # [Common]
    #-------------------------------------

    def get_description(self, label, label_text, tree, xml_path, findall, text_edit, index):
        """
        Get Description
        ===============

        Get item description from xml file and show in text edit.

        Args:
        -----
            label (PyFlameLabel):
                Label to switch text to 'Script Description'.

            label_text (str):
                Text to switch label to.

            tree (PyFlameTreeWidget):
                Tree widget.

            xml_path (str):
                Path to xml file.

            findall (str):
                Findall string for xml file.

            text_edit (PyFlameTextEdit):
                Text edit widget.

            index (int):
                Index of item in xml file.
        """

        selected_item = tree.selectedItems()
        item = selected_item[0]
        item_name = item.text(0)
        item_name = item_name.replace(' ', '_')

        # Add items from xml to matchbox list
        xml_tree = ET.parse(xml_path)
        root = xml_tree.getroot()

        for item in root.findall(findall):
            if item.get('name') == item_name:
                text_edit.setPlainText(item[index].text[1:-1])

        # Switch text edit label to 'Script Description'. This is named 'Logik Portal Updates' when the script first loads.
        label.setText(label_text)

    def download_xmls(self) -> None:
        """
        Download XMLS
        =============

        Download file list xmls from ftp to temp folder.
        """

        pyflame.print('Downloading XML Files...')

        # Download xmls to temp folder
        self.python_scripts_xml_path = os.path.join(self.temp_folder, 'python_scripts.xml')
        self.ftp.retrbinary('RETR ' + '/Scripts/python_scripts.xml', open(self.python_scripts_xml_path, 'wb').write)
        pyflame.print('Python Scripts XML Downloaded')

        self.matchbox_xml_path = os.path.join(self.temp_folder, 'matchbox_collection.xml')
        self.ftp.retrbinary('RETR ' + '/Logik_Matchbox/matchbox_collection.xml', open(self.matchbox_xml_path, 'wb').write)
        pyflame.print('Matchbox XML Downloaded')

        self.batch_setups_xml_path = os.path.join(self.temp_folder, 'batch_setups.xml')
        self.ftp.retrbinary('RETR ' + '/Batch_Setups/batch_setups.xml', open(self.batch_setups_xml_path, 'wb').write)
        pyflame.print('Batch Setups XML Downloaded')

        self.inferences_xml_path = os.path.join(self.temp_folder, 'inference_nodes_.xml')
        self.ftp.retrbinary('RETR ' + '/Inference_Nodes/inference_nodes_.xml', open(self.inferences_xml_path, 'wb').write)
        pyflame.print('Inference Nodes XML Downloaded')

        pyflame.print('XML Files Downloaded', text_color=TextColor.GREEN)

    def download_file(self, download_type: str, file_name: str, ftp_file_path: str, tgz_path: str) -> None:
        """
        Download File
        =============

        Download selected file from ftp with progress window

        Args:
        -----
            download_type (str):
                Type of file being downloaded (Python Script, Matchbox, Batch Setup, Inference Node).

            file_name (str):
                Name of file being downloaded.

            ftp_file_path (str):
                Path to file on ftp.

            tgz_path (str):
                Path to download file to.
        """

        pyflame.print(f'Downloading {download_type}: {file_name}')

        # Connect to ftp
        self.ftp_download_connect()

        # Get file size
        file_size = self.ftp.size(ftp_file_path)

        file_size = file_size / 1000
        file_size = int(round(file_size, 1))
        num_to_do = file_size
        file_size = str(file_size) + ' KB'

        # Create progress window
        self.progress_window = PyFlameProgressWindow(
            num_to_do=num_to_do,
            title=f'{SCRIPT_NAME}: Downloading',
            text=f'{download_type}: {file_name}\n\n0 KB of {file_size}',
            )

        # Variables to store progress
        downloaded = 0

        # Callback function to write data and update progress
        def write_and_update(data):
            nonlocal downloaded

            with open(tgz_path, 'ab') as f:
                f.write(data)

            downloaded += len(data)
            downloaded_bytes = downloaded / 1000
            downloaded_progress = int(round(downloaded_bytes, 1))
            downloaded_bytes = str(downloaded_progress) + ' KB'
            self.progress_window.set_progress_value(downloaded_progress)
            self.progress_window.set_text(f'{download_type}: {file_name}\n\n{downloaded_bytes} of {file_size}')

        # Retrieve file in binary mode with a callback
        self.ftp.retrbinary(f'RETR {ftp_file_path}', write_and_update)

        # Set final progress window values
        self.progress_window.set_text(f'{download_type}: {file_name}\n\n{file_size} of {file_size}\n\nDownload Complete.')
        self.progress_window.set_progress_value(num_to_do)

        # Disconnect from ftp
        self.ftp.quit()

    def upload_file(self, upload_type: str, file_name: str, xml_path: str, tgz_path: str) -> None:
        """
        Upload File
        ===========

        Upload files to ftp with progress window

        Args:
        -----
            upload_type (str):
                Type of file being uploaded (Python Script, Matchbox, Batch Setup, Inference Node).

            file_name (str):
                Name of file being uploaded.

            xml_path (str):
                Path to xml file to be uploaded to ftp.

            tgz_path (str):
                Path to tgz file to be uploaded to ftp.
        """

        def read_and_update(data):
            """
            Read and Update
            ===============

            Callback function to read data and update progress.
            """

            nonlocal uploaded

            uploaded += len(data)
            uploaded_bytes = uploaded / 1000
            upload_progress = int(round(uploaded_bytes, 1))
            uploaded_bytes = str(upload_progress) + ' KB'
            #print('uploaded_bytes:', uploaded_bytes)

            self.progress_window.set_progress_value(upload_progress)
            self.progress_window.set_text(f'{upload_type}: {file_name}\n\n{uploaded_bytes} of {file_size}')
            return data

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

        pyflame.print(f'Uploading: {file_name}')

        if upload_type == 'Python Script':
            upload_folder = '/Submit_Scripts'
        elif upload_type == 'Batch Setup':
            upload_folder = '/Submit_Batch_Setups'
        elif upload_type == 'Inference Node':
            upload_folder = '/Submit_Inference_Node'

        # Tgz upload file path on ftp
        ftp_tgz_path = os.path.join(upload_folder, file_name) + '.tgz'

        # XML upload file path on ftp
        ftp_xml_path = os.path.join(upload_folder, file_name) + '.xml'

        # Connect to ftp if not uploading python script - python script uses a different ftp connection
        if not upload_type == 'Python Script':
            self.ftp_upload_connect()

        # Get file size
        file_size = os.path.getsize(tgz_path)
        num_to_do = file_size

        # if the number of digits in file_size is greater than 7 then divide by 1000000 to get MB
        if len(str(file_size)) > 4:
            file_size = file_size / 1000
            num_to_do = int(round(file_size, 1))
            file_size = str(num_to_do) + ' KB'

        # Create progress window
        self.progress_window = PyFlameProgressWindow(
            num_to_do=num_to_do,
            title=f'{SCRIPT_NAME}: Uploading',
            text=f'{upload_type}: {file_name}\n\n0 KB of {file_size}',
            )

        # Upload xml file to ftp
        with open(xml_path, 'rb') as f:
            self.ftp.storbinary(f'STOR {ftp_xml_path}', f)
        print(f'--> {file_name}.xml uploaded to ftp.\n')

        # Upload tgz file to ftp
        uploaded = 0 # Variables to store progress

        # Open the file and upload in binary mode with a callback
        with open(tgz_path, 'rb') as f:
            self.ftp.storbinary(f'STOR {ftp_tgz_path}', f, callback=read_and_update)

        QtWidgets.QApplication.restoreOverrideCursor()

        # Set final progress window message
        self.progress_window.set_text(f'{upload_type}: {file_name}\n\n{file_size} of {file_size}\n\nUpload Complete.')
        self.progress_window.set_progress_value(num_to_do)

        # Check that both files were uploaded to site, if not display error message
        if f'{os.path.join(upload_folder, file_name)}.tgz' and f'{os.path.join(upload_folder, file_name)}.xml' not in self.ftp.nlst(upload_folder):
            QtWidgets.QApplication.restoreOverrideCursor()
            self.ftp.quit()
            PyFlameMessageWindow(
                message='Upload failed. Try again.',
                type=MessageType.ERROR
            )
            return

        # Clean up temp folder
        os.remove(xml_path)
        os.remove(tgz_path)

        # Disconnect from ftp
        self.ftp.quit()

    def done(self):
        """
        Done
        ====

        Close the Logik Portal window.
        """

        # Save current tab to config
        self.settings.save_config(
            config_values={
                'last_tab': self.window.get_current_tab(),
                'script_install_path': self.script_install_path_browse.text()
                }
            )

        self.window.close()

        try:
            self.submit_script_window.close()
        except:
            pass

        try:
            self.submit_batch_window.close()
        except:
            pass

        try:
            self.ftp.quit()
        except:
            pass

        try:
            shutil.rmtree(self.temp_folder)
            print('--> Clearing temp files.\n')
        except:
            pass

        print('Done.\n')

    #-------------------------------------
    # [Matchbox]
    #-------------------------------------

    def get_matchbox_description(self):
        """
        Get Matchbox Description
        ========================

        Get selected matchbox description from xml file and display in text edit.
        """

        pyflame.print('Getting Matchbox Description...')

        self.get_description(
            label=self.matchbox_desciption_label,
            label_text='Matchbox Description',
            tree=self.matchbox_tree,
            xml_path=self.matchbox_xml_path,
            findall='matchbox',
            text_edit=self.matchbox_text_edit,
            index=5,
            )

    def update_matchbox_tree(self, search: str=None) -> None:
        """
        Update Matchbox Tree
        =====================

        Update matchbox tree with matchboxes from xml file.

        Args:
        -----
            search (str):
                String to search for in matchbox name. If search string is present, only add items that match the search string.
                (Default: None)
        """

        pyflame.print('Updating Matchbox List...')

        def add_matchbox(matchbox):
            shader_type = str(matchbox[0].text[1:-1])
            author_name = str(matchbox[4].text[1:-1])
            matchbox = QtWidgets.QTreeWidgetItem(self.matchbox_tree, [matchbox_name, shader_type, author_name])

        self.matchbox_tree.clear()

        # Read in matchboxes from xml
        xml_tree = ET.parse(self.matchbox_xml_path)
        root = xml_tree.getroot()

        # Add items from xml to matchbox tree. If search string is present, only add items that match the search string.
        if search:
            for matchbox in root.findall('matchbox'):
                matchbox_name = str(matchbox.get('name'))
                if search.lower() in matchbox_name.lower():
                    add_matchbox(matchbox)
        else:
            for matchbox in root.findall('matchbox'):
                matchbox_name = str(matchbox.get('name'))
                add_matchbox(matchbox)

        # Select top item in matchbox list
        self.matchbox_tree.setCurrentItem(self.matchbox_tree.topLevelItem(0))

        # Get selected Matchbox description if Matchbox is selected.
        try:
            self.get_matchbox_description()
        except:
            print('Unable to get Matchbox description. No Matchbox selected\n')

        pyflame.print('Matchbox List Updated', text_color=TextColor.GREEN)

    #-------------------------------------
    # [Batch Setups]
    #-------------------------------------

    def check_batch_flame_version(self) -> None:
        """
        Check Batch Flame Version
        =========================

        Check if batch setup is compatible with current version of Flame.

        If batch setup won't work with current version of Flame, disable the download button.
        """

        pyflame.print('Checking Batch Version...')

        # Get selected script date
        selected_batch = self.batch_setups_tree.selectedItems()
        batch_item = selected_batch[0]
        batch_name = batch_item.text(0)
        batch_flame_version = batch_item.text(1)

        # print('current_flame_version:', self.flame_version)
        # print('batch_flame_version:', batch_flame_version, '\n')

        if float(batch_flame_version) > float(self.flame_version):
            pyflame.print(f'{batch_name} Requires Newer Version of Flame.')
            self.batch_setups_download_button.setEnabled(False)
        else:
            self.batch_setups_download_button.setEnabled(True)

    def get_batch_description(self) -> None:
        """
        Get Batch Description
        =====================

        Get selected batch setup description from xml file and display in text edit.
        """

        pyflame.print('Getting Batch Setup Description...')

        self.get_description(
            label=self.batch_setups_desciption_label,
            label_text='Batch Setup Description',
            tree=self.batch_setups_tree,
            xml_path=self.batch_setups_xml_path,
            findall='batch',
            text_edit=self.batch_setups_text_edit,
            index=2,
            )

    def update_batch_setups_tree(self, search: str=None) -> None:
        """
        Update Batch Setups Tree
        ========================

        Add batch setups to batch setups tree from xml file. If search string is present, only add items that match the search string.

        Args:
        -----
            search (str):
                String to search for in batch setup name. If search string is present, only add items that match the search string.
                (Default: None)
        """

        def add_batch_setup(batch):
            flame_version = str(batch[1].text[1:-1])
            artist_name = str(batch[0].text[1:-1])

            batch_setup = QtWidgets.QTreeWidgetItem(self.batch_setups_tree, [batch_name, flame_version, artist_name])

            # if batch setup requires newer version of flame grey out script entry
            if float(self.flame_version) < float(flame_version):
                batch_setup.setForeground(0, QtGui.QColor('#555555'))
                batch_setup.setForeground(1, QtGui.QColor('#555555'))
                batch_setup.setForeground(2, QtGui.QColor('#555555'))

        pyflame.print('Updating Batch Setups List...')

        # Clear batch setup tree
        self.batch_setups_tree.clear()

        # Read in batch setups from xml
        xml_tree = ET.parse(self.batch_setups_xml_path)
        root = xml_tree.getroot()

        # Add items from xml to batch setup tree. If search string is present, only add items that match the search string.
        if search:
            for batch in root.findall('batch'):
                batch_name = str(batch.get('name'))
                if search.lower() in batch_name.lower():
                    add_batch_setup(batch)
        else:
            for batch in root.findall('batch'):
                batch_name = str(batch.get('name'))
                add_batch_setup(batch)

        # Select top item in batch setup tree
        self.batch_setups_tree.setCurrentItem(self.batch_setups_tree.topLevelItem(0))

        # Get selected batch setup description
        self.get_batch_description()

        # Get selected batch setup description if batch setup is selected.
        try:
            self.get_batch_description()
        except:
            print('Unable to get Batch Setup description. No Batch Setup selected\n')

        pyflame.print('Batch Setups List Updated', text_color=TextColor.GREEN)

    #-------------------------------------
    # [Inference Nodes]
    #-------------------------------------

    def get_inference_node_description(self):
        """
        Get Inference Node Description
        ==============================

        Get selected inference node description from xml file and display in text edit.
        """

        pyflame.print('Getting Inference Node Description...')

        self.get_description(
            label=self.inference_node_description_label,
            label_text='Inference Node Description',
            tree=self.inference_node_tree,
            xml_path=self.inferences_xml_path,
            findall='inference_node',
            text_edit=self.inference_node_description_text_edit,
            index=2,
            )

    def update_inference_node_tree(self, search: str=None) -> None:
        """
        Update Inference Node Tree
        ==========================

        Update inference node tree from xml file. If search string is present, only add items that match the search string.

        Args:
        -----
            search (str):
                String to search for in inference node name. If search string is present, only add items that match the search string.
                (Default: None)
        """

        def add_inference_node(node):
            flame_version = str(node[0].text[1:-1])
            inference_node_size = str(node[1].text[1:-1])

            inference_node = QtWidgets.QTreeWidgetItem(self.inference_node_tree, [inference_node_name, flame_version, inference_node_size])

            # if node requires newer version of flame grey out script entry
            if float(self.flame_version) < float(flame_version):
                inference_node.setForeground(0, QtGui.QColor('#555555'))
                inference_node.setForeground(1, QtGui.QColor('#555555'))
                inference_node.setForeground(2, QtGui.QColor('#555555'))

        pyflame.print('Updating Inference Node List...')

        # Clear inference node tree.
        self.inference_node_tree.clear()

        # Read in inference nodes from xml.
        xml_tree = ET.parse(self.inferences_xml_path)
        root = xml_tree.getroot()

        # Add items from xml to inference node tree. If search string is present, only add items that match the search string.
        if search:
            for node in root.findall('inference_node'):
                inference_node_name = str(node.get('name'))
                if search.lower() in inference_node_name.lower():
                    add_inference_node(node)
        else:
            for node in root.findall('inference_node'):
                inference_node_name = str(node.get('name'))
                add_inference_node(node)

        # Select top item in inference node tree.
        self.inference_node_tree.setCurrentItem(self.inference_node_tree.topLevelItem(0))

        # Get selected inference node description if inference node is selected.
        try:
            self.get_inference_node_description()
        except:
            print('Unable to get Inference Node description. No Inference Node selected\n')

        pyflame.print('Inference Node List Updated', text_color=TextColor.GREEN)

    #-------------------------------------

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'Logik',
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Logik Portal',
                    'order': 1,
                    'execute': LogikPortal,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
