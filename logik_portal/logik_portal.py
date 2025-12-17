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
Script Version: 7.0.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 10.31.20
Update Date: 12.16.25

Script Type: Flame Main Menu

Description:

    Share/install python scripts, batch setups, inference nodes, and download matchboxes

URL:
    https://github.com/logik-portal/python/logik_portal

Menu:

    Flame Main Menu -> Logik -> Logik Portal

To install:

    Copy script into /opt/Autodesk/shared/python/logik_portal

Updates:

    v7.0.0 12.16.25
        - Updated to PyFlameLib v5.0.0.
        - Removed PySide2 support.
        - Matchboxes are now pulled from GitHub repository instead of FTP server.
        - Python scripts are now pulled from GitHub repository instead of FTP server.
        - Fixed issue with python scripts not showing up in locally installed scripts list if they did not have a properly formatted header docstring.

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

# ==============================================================================
# [Imports]
# ==============================================================================
import os
import re
import html
import json
import shutil
import base64
import tarfile
import zipfile
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from ftplib import FTP
from pathlib import Path
from subprocess import PIPE, Popen
from typing import Optional
import ast
import sys

import flame
from lib.pyflame_lib_logik_portal import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Logik Portal'
SCRIPT_VERSION = 'v7.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

LOGIK_FTP = '45.79.19.175'

# ==============================================================================
# [Main Script]
# ==============================================================================

class LogikPortal:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Get version of flame
        self.flame_full_version = flame.get_version()
        self.flame_version = pyflame.get_flame_version()

        # Set Autodesk python scripts path for either Flame or Flare
        self.autodesk_scripts_path = f'/opt/Autodesk/flame_{self.flame_full_version}/python_utilities/scripts'
        if not os.path.isdir(self.autodesk_scripts_path):
            self.autodesk_scripts_path = f'/opt/Autodesk/flare_{self.flame_full_version}/python_utilities/scripts'

        # Load config file
        self.settings = self.load_config()

        # Create temp folders
        self.temp_folder = os.path.join(SCRIPT_PATH, 'temp')
        self.temp_matchbox_folder = os.path.join(self.temp_folder, 'matchbox')

        # Create temp folders
        temp_folders_created = self.create_temp_folders()
        if not temp_folders_created:
            return

        # Check internet connection
        internet_connection_check = self.check_internet_connection()
        if not internet_connection_check:
            return

        #  Init variables
        self.installed_script_dict = {}
        self.file_description = ''
        self.tar_path = ''
        self.tar_file_name = ''
        self.batch_setups_xml_path = ''
        self.updates = ''

        # Matchbox JSON Path
        self.matchbox_json_path = os.path.join(self.temp_folder, 'matchbox_collection.json')
        self.python_scripts_json_path = os.path.join(self.temp_folder, 'python_scripts.json')
        self.download_github_jsons()

        # Open main window
        self.main_window()

        self.download_xmls()
        self.update_batch_setups_tree()
        self.update_inference_node_tree()
        self.check_batch_flame_version()
        self.check_script_flame_version(self.portal_scripts_tree)

        # Get updates file from FTP
        self.get_updates()

        # Close ftp connection
        self.ftp.quit()

        # Go to last used tab
        self.tabs.set_current_tab(self.settings.last_tab)

        pyflame.print('Welcome To The Logik Portal.', text_color=TextColor.BLUE)

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

        settings = PyFlameConfig(
            config_values={
                'python_submit_all_files': False,
                'matchbox_path': f'/opt/Autodesk/presets/{self.flame_full_version}/matchbox/shaders',
                'matchbox_submit_path': f'/opt/Autodesk/presets/{self.flame_full_version}/matchbox/shaders',
                'batch_setup_download_path': '/opt/Autodesk',
                'batch_submit_path': '/opt/Autodesk',
                'script_submit_path': '/opt/Autodesk',
                'script_install_local_path': self.autodesk_scripts_path,
                'script_install_path': '/opt/Autodesk/shared/python',
                'open_batch': False,
                'inference_node_download_path': '/opt/Autodesk',
                'inference_node_submit_path': '/opt/Autodesk',
                'inference_node_add_to_batch': True,
                'last_tab': 0,
                }
            )

        return settings

    def create_temp_folders(self) -> bool:
        """
        Create temp folders
        ===================

        Create temp folders for the script.

        Returns
        -------
            bool:
                True if temp folders were created successfully, False otherwise.
        """

        # Remove temp folder if it exists and create new one
        try:
            if os.path.exists(self.temp_folder):
                shutil.rmtree(self.temp_folder)
            os.makedirs(self.temp_matchbox_folder)
            return True
        except:
            PyFlameMessageWindow(
                message=f'{SCRIPT_NAME}: Script needs full permissions to script folder.\n\nIn shell/terminal type:\n\nchmod 777 /opt/Autodesk/shared/python/logik_portal',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

    def check_internet_connection(self):
        """
        Check internet connection
        ========================

        Check internet connection to ftp.
        """

        # Check internet connection to ftp
        try:
            self.ftp_download_connect()
            return True
        except:
            PyFlameMessageWindow(
                message="Can't connect to Logik Portal.\nCheck internet connection and try again.",
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

    # ==============================================================================
    # [FTP]
    # ==============================================================================

    def ftp_download_connect(self):

        # Connect to ftp
        self.ftp = FTP(f'{LOGIK_FTP}')
        self.ftp.login('logik_portal_download', 'L0gikD0wnL0ad#20')

        pyflame.print('Connected To Logik Portal.', text_color=TextColor.BLUE)

    def ftp_upload_connect(self):

        # Connect to ftp
        self.ftp = FTP(f'{LOGIK_FTP}')
        self.ftp.login('logik_portal_upload', 'L0gikUpl0ad#20')

        pyflame.print('Connected To Logik Portal.', text_color=TextColor.GREEN)

    def ftp_disconnect(self):

        self.ftp.quit()

        pyflame.print('Disconnected From Logik Portal.', text_color=TextColor.GREEN)

    # ==============================================================================
    # [GitHub]
    # ==============================================================================

    def download_github_folder(self, folder_name: str, repo_name: str, branch: str='main', destination: str=None) -> str:
        """
        Download a specific folder from a GitHub repository using the github API.
        Only downloads the requested folder, not the entire repository.

        Args
        ----
            folder_name (str):
                Name of the folder to download from GitHub repository

            repo_name (str):
                GitHub repository name
                (Example: 'matchbox')

            branch (str):
                GitHub branch name
                (Default: main)

            destination (str, optional):
                Path to destination directory. If None, the folder will be downloaded to the temp folder.
                (Default: None)

        Returns
        -------
            str:
                Path to destination folder
        """

        def get_github_api_url(repo_name: str, endpoint: str) -> str:
            """
            Construct a GitHub API URL.

            Args
            ----
                endpoint (str):
                    GitHub API endpoint

            Returns
            -------
                str:
                    GitHub API URL
            """

            return f'https://api.github.com/repos/logik-portal/{repo_name}/{endpoint}'

        def make_api_request(url: str) -> dict:
            """
            Make a request to the GitHub API and return JSON response.

            Args
            ----
                url (str):
                    GitHub API URL

            Returns
            -------
                dict:
                    JSON response from the GitHub API
            """

            try:
                request = urllib.request.Request(url)
                # Add a User-Agent header (GitHub API requires this)
                request.add_header('User-Agent', 'Python-GitHub-Folder-Downloader')

                with urllib.request.urlopen(request) as response:
                    return json.loads(response.read().decode())
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    raise FileNotFoundError(f'Resource not found: {url}')
                raise Exception(f'GitHub API error: {e.code} - {e.reason}')
            except urllib.error.URLError as e:
                raise Exception(f'Network error: {e}')

        def get_branch_sha(repo_name: str, branch: str) -> str:
            """
            Get the SHA of the specified branch.

            Args
            ----
                repo_name (str):
                    Name of Gihub repository

                branch (str):
                    GitHub branch name

            Returns
            -------
                str:
                    SHA of the specified branch
            """

            url = get_github_api_url(repo_name, endpoint=f'branches/{branch}')
            data = make_api_request(url)

            return data['commit']['sha']

        def get_folder_tree(folder_name: str, repo_name: str, sha: str) -> list:
            """
            Get the tree for a specific folder recursively.

            Args
            ----
                folder_name (str):
                    Name of the folder to download from GitHub repository

                repo_name (str):
                    Name of Gihub repository

                sha (str):
                    Branch SHA

            Returns
            -------
                list:
                    Files in specified Gtihub folder
            """

            # First, get the root tree
            url = get_github_api_url(repo_name, endpoint=f'git/trees/{sha}?recursive=1')
            tree_data = make_api_request(url)

            # Filter for files in the requested folder
            folder_path = folder_name
            folder_files = []

            for item in tree_data.get('tree', []):
                path = item['path']
                # Check if the path starts with the folder name (with or without trailing slash)
                if path.startswith(folder_path + '/') or path == folder_path:
                    folder_files.append(item)

            if not folder_files:
                # Try to get list of available folders
                available_folders = set()
                for item in tree_data.get('tree', []):
                    path = item['path']
                    if item['type'] == 'tree' and '/' not in path:
                        available_folders.add(path)

                if available_folders:
                    print(f'\nError: Folder: {folder_name} not found in repository.')
                    print(f'\nAvailable folders ({len(available_folders)} total):')
                    for folder in sorted(available_folders)[:30]:  # Show first 30
                        print(f'  - {folder}')
                    if len(available_folders) > 30:
                        print(f'  ... and {len(available_folders) - 30} more')

                raise FileNotFoundError(f'Folder: {folder_name} not found in repository')

            return folder_files

        def download_files():
            """
            Download files
            ==============

            Download files from GitHub repository and update progress window.
            """

            for i, file_item in enumerate(files_to_download, 1):

                progress_window.processing_task = i

                file_path = file_item['path']
                # Remove the folder prefix from the path for local structure
                relative_path = file_path[len(folder_name) + 1:] if file_path.startswith(folder_name + '/') else file_path

                local_file_path = os.path.join(destination_folder, relative_path)

                # Create subdirectories if needed
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Get the file content URL
                file_url = file_item['url']
                file_data = make_api_request(file_url)

                # Download the file (GitHub API returns base64 encoded content)
                content = base64.b64decode(file_data['content'])

                # Write the file
                with open(local_file_path, 'wb') as f:
                    f.write(content)

                print(f"  [{i}/{len(files_to_download)}] {relative_path}")

            progress_window.tasks_complete = True
            progress_window.title = 'Download Completed'

        if destination is None:
            destination = self.temp_folder

        # Destination folder path
        destination_folder = os.path.join(destination, folder_name)
        print('Destination folder:', destination_folder, '\n')

        # Remove existing folder if it exists
        if os.path.isdir(destination_folder):
            print(f'Removing existing folder: {destination_folder}')
            shutil.rmtree(destination_folder)

        print(f'Fetching folder information for: {folder_name}')
        print(f'Repository: logik-portal/{repo_name} (branch: {branch})')

        try:
            # Get the branch SHA
            print('Getting branch information...')
            sha = get_branch_sha(repo_name, branch)

            # Get the folder tree
            print(f'Finding files in folder:{folder_name}...')
            folder_files = get_folder_tree(folder_name, repo_name, sha)

            # Filter to only files (not subdirectories in the tree listing)
            files_to_download = [f for f in folder_files if f['type'] == 'blob']

            if not files_to_download:
                raise FileNotFoundError(f'No files found in folder: {folder_name}')

            print(f'Found {len(files_to_download)} file(s) to download\n')

            # Create the destination folder
            os.makedirs(destination_folder, exist_ok=True)

            # Clean up script name for progress window
            script_to_download = folder_name.replace('_', ' ')

            # Open progress window
            progress_window = PyFlameProgressWindow(
                task='Downloading Files',
                total_tasks=len(files_to_download),
                task_progress_message='Downloading Script:\n\n{script_to_download}\n\n{{task}}: [{{processing_task}} of {{total_tasks}}]'.format(script_to_download=script_to_download),
                title='Downloading Files...',
                parent=self.window,
                )

            # Download files from GitHub repository and update progress window
            download_files()

            print(f'\nSuccessfully downloaded: {folder_name} to: {destination_folder}')
            print(f'Total files: {len(files_to_download)}\n')

            return destination_folder

        except Exception as e:
            # Clean up partial download on error
            if os.path.isdir(destination_folder):
                shutil.rmtree(destination_folder)
            raise

    # ==============================================================================
    # [Main Window]
    # ==============================================================================

    def main_window(self):

        def close_window():

            # Clean up temp folder
            if os.path.exists(self.temp_folder):
                shutil.rmtree(self.temp_folder)

            # Close main window
            self.window.close()

        # Create Main Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.done,
            escape_pressed=close_window,
            grid_layout_columns=1,
            grid_layout_rows=1,
            parent=None,
            )

        # Create Tab Widget
        self.tabs = PyFlameTabWidget(
            tab_names=[
                'Python Scripts',
                'Matchbox',
                'Batch Setups',
                'Inference Nodes',
                ],
            grid_layout_columns=7,
            grid_layout_rows=20,
            grid_layout_adjust_column_widths={
                3: 50,
                }
            )

        # Load Tabs
        self.python_scripts_tab()
        self.matchbox_tab()
        self.batch_setups_tab()
        self.inference_nodes_tab()

        # Add Tab Widget to Main Window
        self.window.grid_layout.addWidget(self.tabs, 0, 0)

        self.window.center_window()

    def python_scripts_tab(self):

        def update_logik_portal_scripts_tree(search: str=None):
            """
            Update Logik Portal Scripts Tree
            ================================

            Add Logik Portal python scripts to Portal Python Scripts tree.

            Get script info from xml file and add to tree list. If a newer version of the script exists on the ftp, highlight the script entry.
            If the script requires a newer version of flame, grey out the script entry.

            Args
            ----
                search (str, optional):
                    The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                    (Default: None)
            """

            def add_script(python_script) -> None:
                """
                Add Script
                ==========

                Add script to Portal Python Scripts tree.
                """

                # Get script info
                script_name = python_script.get('Script Name')
                script_version = python_script.get('Script Version')
                flame_min_version = python_script.get('Flame Version')
                flame_max_version = python_script.get('Maximum Flame Version')
                date = python_script.get('Update Date')
                if date == 'unknown':
                    date = python_script.get('Creation Date')
                developer_name = python_script.get('Author')

                self.portal_scripts_tree.add_item_with_columns([script_name, script_version, flame_min_version, flame_max_version, date, developer_name])

            def check_script_version_compatibility():
                """
                Check Script Version Compatibility
                ==================================

                Check if script version is compatible with current flame version.
                If script is not compatible, grey out the script entry in tree widget.

                Args
                ----
                    item (QTreeWidgetItem):
                        The item to check the version compatibility of.
                """

                root = self.portal_scripts_tree.invisibleRootItem()
                for i in range(root.childCount()):
                    item = root.child(i)

                    if item:
                        script_name = item.text(0)
                        script_version = item.text(1)

                        # Get value for flame_max_version and flame_min_version
                        flame_max_version = item.text(3)
                        if flame_max_version == 'Latest':
                            flame_max_version = str(self.flame_version)
                        flame_min_version = item.text(2)

                        if len(flame_max_version.split('.')) > 2:
                            flame_max_version = flame_max_version.split('.')[0] + '.' + flame_max_version.split('.')[1]
                        if len(flame_min_version.split('.')) > 2:
                            flame_min_version = flame_min_version.split('.')[0] + '.' + flame_min_version.split('.')[1]
                        flame_max_version = flame_max_version.split('.')[0] + '.' + flame_max_version.split('.')[1]

                        # Check script flame version compatibility, grey out script entry if not compatible.
                        if flame_max_version != self.flame_version:
                            # Do something if values can be converted to floats
                            if float(flame_min_version) and float(flame_max_version):
                                #If newer version of script exists on ftp, highlight script entry
                                if script_name in self.installed_script_dict:
                                    installed_script_version = self.installed_script_dict.get(script_name)
                                    try:
                                        if float(script_version) > float(installed_script_version):
                                            self.portal_scripts_tree.color_item(item, color='#ffffff')
                                    except:
                                        pass

                                # if script requires newer version of flame grey out script entry
                                if float(self.flame_version) < float(flame_min_version):
                                    self.portal_scripts_tree.color_item(item, color='#555555')

                                # If scripts max_flame_version if not equal to the current flame version or 'Latest', grey out the script entry.
                                if flame_max_version != 'Latest':
                                    if float(flame_max_version) < float(self.flame_version):
                                        self.portal_scripts_tree.color_item(item, color='#555555')

            pyflame.print('Updating Python Scripts List...', underline=True, new_line=False)

            # Clear Portal Scripts tree
            self.portal_scripts_tree.clear()

            # Read in JSON
            with open(self.python_scripts_json_path, 'r', encoding='utf-8') as f:
                python_scripts = json.load(f)

            # Add items to Python Scripts tree from JSON file
            if search:
                for python_script in python_scripts:
                    script_name = python_script.get('Script Name')
                    if search.lower() in script_name.lower():
                        add_script(python_script)
            else:
                for python_script in python_scripts:
                    script_name = python_script.get('Script Name')
                    add_script(python_script)

            # Check script version compatibility for all items in portal scripts tree
            check_script_version_compatibility()

            # Select top item in Portal Scripts tree
            self.portal_scripts_tree.setCurrentItem(self.portal_scripts_tree.topLevelItem(0))

            # Get selected python script description if python script is selected.
            try:
                get_script_description()
            except:
                print('Unable to get Python Script description. No Python Script selected\n')

            # Set width of Portal Scripts tree headers
            self.portal_scripts_tree.resizeColumnToContents(0)
            self.portal_scripts_tree.resizeColumnToContents(4)
            self.portal_scripts_tree.set_fixed_column_headers()

            pyflame.print('Python Scripts List Updated', text_color=TextColor.GREEN)

        def update_installed_scripts_tree(search: str=None):
            """
            Update Installed Scripts Tree
            =============================

            Update the installed scripts tree with the scripts found in the shared script path.

            Args
            ----
                search (str, optional):
                    The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                    (Default: None)
            """

            def add_script():
                """
                Add Script
                ==========

                Extract script metadata from docstring and add script to Installed Scripts tree.
                """

                def extract_docstring(file_path: str) -> Optional[str]:
                    """
                    Extract Docstring
                    =================

                    Extract the module-level docstring from a Python file.

                    Args
                    ----
                        file_path: Path to the Python file

                    Returns
                    -------
                        The docstring as a string, or None if not found
                    """

                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            source = f.read()

                        # Parse the AST to get the module docstring
                        tree = ast.parse(source)
                        if ast.get_docstring(tree):
                            return ast.get_docstring(tree)
                        return None
                    except Exception as e:
                        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                        return None

                def extract_metadata(docstring: str) -> Dict[str, str]:
                    """
                    Extract Metadata
                    ================

                    Extract metadata fields from a docstring.

                    Args
                    ----
                        docstring: The docstring text to parse

                    Returns
                    -------
                        Dictionary with extracted metadata fields
                    """

                    # Initialize result dictionary with empty strings
                    metadata = {
                        'Script Name': '',
                        'Script Version': '',
                        'Flame Version': '',
                        'Written by': '',
                        'Creation Date': '',
                        'Update Date': ''
                        }

                    if not docstring:
                        return None

                    # Split docstring into lines
                    lines = docstring.split('\n')

                    # Pattern to match field names (case insensitive)
                    # Format: "Field Name: value" or "Field Name:value"
                    pattern = re.compile(r'^([^:]+):\s*(.+)$', re.IGNORECASE)

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        match = pattern.match(line)
                        if match:
                            field_name = match.group(1).strip()
                            field_value = match.group(2).strip()

                            # Check each metadata field (case insensitive)
                            field_name_lower = field_name.lower()

                            if field_name_lower == 'script name':
                                metadata['Script Name'] = field_value
                            elif field_name_lower == 'script version':
                                metadata['Script Version'] = field_value
                            elif field_name_lower == 'flame version':
                                metadata['Flame Version'] = field_value
                            elif field_name_lower == 'written by':
                                metadata['Written by'] = field_value
                            elif field_name_lower == 'creation date':
                                metadata['Creation Date'] = field_value
                            elif field_name_lower == 'update date':
                                metadata['Update Date'] = field_value

                    # If Update Date is missing, use Creation Date
                    if not metadata['Update Date'] and metadata['Creation Date']:
                        metadata['Update Date'] = metadata['Creation Date']

                    return metadata

                def date_flip(date):
                    """
                    Date Flip
                    =========

                    Swap date from mm.dd.yy to yy.mm.dd for python scripts list sorting.

                    Args
                    ----
                        date:
                            str: Date in mm.dd.yy format.

                    Returns
                    -------

                        str: Date flipped
                    """

                    date = date.split('.')
                    date = date[2] + '.' + date[0] + '.' + date[1]

                    return date

                # Get script info
                script_path = os.path.join(root, script)
                docstring = extract_docstring(script_path)
                metadata = extract_metadata(docstring)

                script_name = script.replace('_', ' ')[:-3]

                if metadata:
                    try:
                        script_version = metadata['Script Version']
                    except:
                        script_version = ''
                    try:
                        flame_version = metadata['Flame Version']
                    except:
                        flame_version = ''
                    try:
                        script_dev = metadata['Written by']
                    except:
                        script_dev = ''
                    try:
                        script_date = metadata['Update Date']
                        script_date = date_flip(script_date)
                    except:
                        script_date = ''

                else:
                    script_version = ''
                    flame_version = ''
                    script_dev = ''
                    script_date = ''

                # Add script to tree
                self.installed_scripts_tree.add_item_with_columns([script_name, script_version, flame_version, script_date, script_dev, script_path])

                # Add script to dict of installed scripts
                self.installed_script_dict.update({script_name : script_version})

            pyflame.print('Updating Installed Scripts List...', underline=True, new_line=False)

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
            self.installed_scripts_tree.set_fixed_column_headers()

            # Select first item in tree
            self.installed_scripts_tree.setCurrentItem(self.installed_scripts_tree.topLevelItem(0))

            pyflame.print('Installed Scripts List Updated', text_color=TextColor.GREEN)

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
                window_to_hide=self.window
                )

            if script_path:
                save_config()

                script_to_install = script_path.rsplit('/', 1)[1][:-3]
                if PyFlameMessageWindow(
                    message=f'Install Python Script: {script_to_install.replace("_", " ")}',
                    message_type=MessageType.CONFIRM,
                    parent=self.window,
                    ):
                    dest_folder = os.path.join(self.settings.script_install_path, script_to_install)
                    if os.path.isdir(dest_folder):
                        if not PyFlameMessageWindow(
                            message='Python script already exists. Overwrite?',
                            message_type=MessageType.CONFIRM,
                            parent=self.window,
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
                                message_type=MessageType.ERROR,
                                parent=self.window,
                                )
                            return

                    # Copy script to dest folder
                    shutil.copy(script_path, dest_folder)

                    # Refresh installed scripts tree list
                    update_installed_scripts_tree()

                    # Refresh python hooks
                    flame.execute_shortcut('Rescan Python Hooks')
                    pyflame.print('Python Hooks Refreshed')

                    if os.path.isfile(os.path.join(dest_folder, script_to_install + '.py')):
                        PyFlameMessageWindow(
                            message=f'Python script installed: {script_to_install.replace("_", " ")}',
                            message_type=MessageType.INFO,
                            parent=self.window,
                            )
                        return
                    PyFlameMessageWindow(
                        message=f'Python script not installed.',
                        message_type=MessageType.ERROR,
                        parent=self.window,
                        )
                    return

        def install_script() -> None:
            """
            Install Script
            ==============

            Get selected script info from selection and install script to script install path.
            """

            pyflame.print('Installing Python Script...', underline=True, new_line=False)

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

            # Download python script from GitHub repository to temp python directory and return path to destination folder
            temp_download_folder = self.download_github_folder(folder_name=script_name, repo_name="python")
            print('Temp Download Folder: ', temp_download_folder)

            install_path = os.path.join(self.settings.script_install_path, script_name)
            print('Install Path: ', install_path)

            # Move script to python folder. overwrite if script already exists.
            if os.path.exists(install_path):
                shutil.rmtree(install_path)
            shutil.move(temp_download_folder, install_path)

            script_installed = os.path.exists(install_path)
            print('Script Installed: ', script_installed)

            # Check if script is in correct path, if so install is complete, if not, install failed.
            if script_installed:

                # Refresh python hooks
                flame.execute_shortcut('Rescan Python Hooks')

                # Refresh installed scripts tree list
                update_installed_scripts_tree()

                # Set color of selected script in portal tree to normal color
                self.portal_scripts_tree.color_item(script_item, color='#9A9A9A')

                pyflame.print(f'Script Installed: {script_name.replace("_", " ")}', text_color=TextColor.GREEN)
                return
            else:
                PyFlameMessageWindow(
                    message='Python Script Install Aborted.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
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
                message=f'Delete python script: {script_to_delete.replace("_", " ")}',
                message_type=MessageType.WARNING,
                parent=self.window,
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
                update_installed_scripts_tree()

        def installed_script_search() -> None:

            update_installed_scripts_tree(search=self.installed_scripts_search_entry.text)

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

        def get_script_description() -> None:
            """
            Get Script Description
            ======================

            Get the description of the selected script from the python scripts tree.
            """

            self.check_script_flame_version(self.portal_scripts_tree)

            pyflame.print('Getting Python Script Description...', underline=True, new_line=False)

            # Switch text edit label to 'Script Description'. This is named 'Logik Portal Updates' when the script first loads.
            self.script_description_label.text = 'Python Script Description'

            # Get selected script info
            selected_item = self.portal_scripts_tree.selectedItems()
            script = selected_item[0]
            script_name = script.text(0)
            script_name = script_name.replace('_', ' ')
            script_version = script.text(2)

            script_max_version = script.text(3)
            if script_max_version == 'Latest':
                script_max_version = self.flame_version
            else:
                if len(script_max_version.split('.')) >= 2:
                    script_max_version = script_max_version.split('.')[0] + '.' + script_max_version.split('.')[1]

            # If script version is less than or equal to flame version, enable install button. Otherwise, disable it.
            if float(script_version) <= self.flame_version and self.flame_version <= float(script_max_version):
                self.install_script_button.enabled = True
            else:
                self.install_script_button.enabled = False

            # Get script description from JSON file
            with open(self.python_scripts_json_path, 'r') as f:
                python_scripts = json.load(f)
            for python_script in python_scripts:
                if python_script.get('Script Name') == script_name:
                    self.script_description_text_edit.text = python_script.get('Description')
                    return

        def portal_script_search():

            update_logik_portal_scripts_tree(search=self.portal_scripts_search_entry.text)

        def browse_script_install_path():
            """
            Browse Script Install Path
            ==========================

            Open file browser to select python script install path.
            """

            pyflame.print(f'Script Install Path Set: {self.script_install_path_browse.path}')

            # Make sure path is writeable, if not, set path to default and show error message
            if not os.access(self.script_install_path_browse.path, os.W_OK):
                PyFlameMessageWindow(
                    message='Selected path is not writeable.\n\nCheck permissions or select a different path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                self.script_install_path_browse.path = self.settings.script_install_path
                return

            # Save settings
            self.settings.save_config(
                config_values={
                    'script_install_path': self.script_install_path_browse.path
                    }
                )

            # Refresh script trees
            update_installed_scripts_tree()
            update_logik_portal_scripts_tree()

        # ==============================================================================
        # [Tab 1: Python Scripts Tab]
        # ==============================================================================

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
            path=self.settings.script_install_path,
            browser_title='Set Python Script Install Path',
            browser_type=BrowserType.DIRECTORY,
            window_to_hide=self.window,
            connect=browse_script_install_path,
            )

        # Text Edit
        self.script_description_text_edit = PyFlameTextEdit(
           text=self.file_description,
           text_style=TextStyle.READ_ONLY,
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
            sort=True,
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
            connect=get_script_description,
            sort=True,
            )

        # Buttons
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

        update_logik_portal_scripts_tree()
        update_installed_scripts_tree()

        # ==============================================================================
        # [Python Scripts Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_label, 0, 0, 1, 3)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_label, 0, 4, 1, 3)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_tree, 1, 0, 7, 3)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_tree, 1, 4, 7, 3)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.delete_script_button, 8, 0)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.install_local_script_button, 8, 2)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.install_script_button, 8, 6)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_search_label, 9, 0)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_search_entry, 9, 1, 1, 2)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_search_label, 9, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_search_entry, 9, 5, 1, 2)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_install_path_label, 10, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_install_path_browse, 10, 5, 1, 2)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_description_label, 12, 0, 1, 7)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_description_text_edit, 13, 0, 7, 7)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.python_done_button, 20, 6)

        # ==============================================================================

        self.installed_scripts_search_entry.set_focus()

    def matchbox_tab(self):

        def download_logik_collection() -> None:
            """
            Download Logik Matchbox Collection
            ================================

            Download Logik Matchbox Collection from GitHub repository as a zip file, extract it, and delete the zip.
            """

            def save_config():

                # Save path to config file
                self.settings.save_config(
                    config_values={
                        'matchbox_path': self.matchbox_install_path
                        }
                    )

            def download_matchbox_repo(system_password=''):
                """
                Download a GitHub repository as a zip file, extract it, rename to Logik, and move to destination.

                Args
                ----
                    system_password: System password for sudo (if needed)
                """

                def remove_folder(path: str) -> bool:
                    """
                    Remove a folder, using sudo if permission is denied.

                    Args
                    ----
                        path (str):
                            Path to remove

                    Returns
                    -------
                        bool:
                            True if folder was removed successfully, False if errors occurred
                    """

                    if not os.path.exists(str(path)):
                        return True

                    try:
                        # Try normal removal first
                        if os.path.isdir(str(path)):
                            shutil.rmtree(str(path))
                        else:
                            os.remove(str(path))
                        print(f'Removed: {path}')
                        return True
                    except PermissionError:
                        # If permission denied, use sudo
                        print(f'Permission denied. Attempting to remove with sudo...')
                        try:
                            remove_cmd = ['sudo', '-S', 'rm', '-rf', str(path)]
                            process = subprocess.Popen(
                                remove_cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                            )
                            stdout, stderr = process.communicate(input=system_password + '\n')

                            if process.returncode != 0:
                                raise Exception(f'Failed to remove with sudo: {stderr}')

                            print(f'Removed: {path} (using sudo)')
                            return True
                        except Exception as e:
                            print(f'Error removing with sudo: {e}')
                            raise
                    except Exception as e:
                        print(f'Error removing: {e}')
                        raise

                def move_repo(source: str, destination: str) -> bool:
                    """
                    Move a folder to destination, using sudo if permission is denied.

                    Args
                    ----
                        source: Source path to move from
                        destination: Destination path to move to
                    """
                    try:
                        # Try normal move first
                        shutil.move(str(source), str(destination))
                        print(f'Moved folder to: {destination}\n')
                        return True
                    except PermissionError:
                        # If permission denied, use sudo
                        print(f'Permission denied. Attempting to move with sudo...')
                        try:
                            # Move with sudo
                            move_cmd = ['sudo', '-S', 'mv', str(source), str(destination)]
                            process = subprocess.Popen(
                                move_cmd,
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                text=True
                                )
                            stdout, stderr = process.communicate(input=system_password + '\n')

                            if process.returncode != 0:
                                raise Exception(f'Failed to move with sudo: {stderr}')

                            print(f'Moved folder to: {destination} (using sudo)\n')
                            return True
                        except Exception as e:
                            print(f'Error moving with sudo: {e}')
                            raise
                    except Exception as e:
                        print(f'Error moving folder: {e}')
                        raise

                def flatten_directory(root_path: str) -> bool:
                    """
                    Move all files and folders from top-level directories to the root path,
                    then delete the empty directories. Also deletes any README.md files encountered.

                    Args
                    ----
                        root_path (str):
                            The root directory path to flatten

                    Returns
                    -------
                        bool:
                            True if successful, False if errors occurred
                    """

                    def delete_readme_files(path: str) -> None:
                        """
                        Recursively delete all README.md files in a directory.

                        Args
                        ----
                            path (str):
                                Path to search for README.md files
                        """
                        if os.path.isdir(path):
                            for root_dir, dirs, files in os.walk(path):
                                for file in files:
                                    if file.upper() == 'README.MD':
                                        try:
                                            file_path = os.path.join(root_dir, file)
                                            os.unlink(file_path)
                                        except Exception:
                                            pass
                        elif os.path.isfile(path) and os.path.basename(path).upper() == 'README.MD':
                            try:
                                os.unlink(path)
                            except Exception:
                                pass

                    if not os.path.exists(root_path):
                        return False

                    if not os.path.isdir(root_path):
                        return False

                    # Delete any README.md files in the root directory first
                    try:
                        for item in os.listdir(root_path):
                            item_path = os.path.join(root_path, item)
                            if os.path.isfile(item_path) and item.upper() == 'README.MD':
                                try:
                                    os.unlink(item_path)
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    # Get all top-level items
                    try:
                        top_level_items = [os.path.join(root_path, item) for item in os.listdir(root_path)]
                    except Exception:
                        return False

                    # Filter to only directories
                    top_level_dirs = [item for item in top_level_items if os.path.isdir(item)]

                    if not top_level_dirs:
                        return True

                    # Process each directory
                    for dir_path in top_level_dirs:
                        # Get all contents of this directory
                        try:
                            contents = [os.path.join(dir_path, item) for item in os.listdir(dir_path)]
                        except Exception:
                            continue

                        if not contents:
                            try:
                                os.rmdir(dir_path)
                            except Exception:
                                pass
                            continue

                        # Move each item to root (or delete if README.md)
                        for item in contents:
                            item_name = os.path.basename(item)

                            # Delete README.md files instead of moving them
                            if os.path.isfile(item) and item_name.upper() == 'README.MD':
                                try:
                                    os.unlink(item)
                                except Exception:
                                    pass
                                continue

                            # If it's a directory, delete any README.md files inside it first
                            if os.path.isdir(item):
                                delete_readme_files(item)

                            dest_path = os.path.join(root_path, item_name)

                            # Handle naming conflicts
                            if os.path.exists(dest_path):
                                counter = 1
                                base_name, extension = os.path.splitext(item_name)
                                while os.path.exists(dest_path):
                                    new_name = f'{base_name}_{counter}{extension}'
                                    dest_path = os.path.join(root_path, new_name)
                                    counter += 1

                            try:
                                shutil.move(item, dest_path)
                            except Exception:
                                pass

                        # Delete the now-empty directory
                        try:
                            os.rmdir(dir_path)
                        except Exception:
                            pass

                    return True

                # Open download progress window to download matchbox collection
                progress_window = PyFlameProgressWindow(
                    task='Downloading Files',
                    total_tasks=1,
                    task_progress_message='Downloading Matchbox Collection [1/1]\n\nPlease wait...',
                    title='Downloading Files...',
                    parent=self.window,
                    )

                # Initialize and display the text by setting processing_task
                progress_window.processing_task = 1

                # Create temporary folder if it doesn't exist
                temp_path = Path(self.temp_matchbox_folder)
                temp_path.mkdir(parents=True, exist_ok=True)

                # Create destination folder if it doesn't exist
                destination_path = Path(self.matchbox_install_path)
                destination_path.mkdir(parents=True, exist_ok=True)

                # Parse the repository URL to get owner, repo, and branch
                # URL format: https://github.com/owner/repo/tree/branch
                url_parts = 'https://github.com/logik-portal/matchbox/tree/main'.rstrip('/').split('/')
                if 'github.com' not in url_parts:
                    raise ValueError('Invalid GitHub URL')

                github_index = url_parts.index('github.com')
                if len(url_parts) < github_index + 3:
                    raise ValueError('Invalid GitHub repository URL')

                owner = url_parts[github_index + 1]
                repo = url_parts[github_index + 2]

                # Get branch (default to 'main' if not specified)
                branch = 'main'
                if 'tree' in url_parts:
                    tree_index = url_parts.index('tree')
                    if len(url_parts) > tree_index + 1:
                        branch = url_parts[tree_index + 1]

                # Construct the zip download URL
                zip_url = f'https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip'

                # Set zip file path and filename
                zip_filename = f'{repo}-{branch}.zip'
                zip_filepath = os.path.join(temp_path, zip_filename)
                zip_filepath_str = str(zip_filepath)

                pyflame.print('Downloading Matchbox Collection...')

                try:
                    urllib.request.urlretrieve(zip_url, zip_filepath_str)
                    pyflame.print(f'Download Complete')

                    # Extract the zip file to temporary folder
                    pyflame.print(f'Extracting Matchbox Collection...')
                    print(f'Extracting to: {temp_path}')
                    with zipfile.ZipFile(zip_filepath_str, 'r') as zip_ref:
                        zip_ref.extractall(str(temp_path))
                    pyflame.print('Extraction Complete')

                    # Rename the extracted folder from matchbox-main to Logik in temp folder
                    extracted_folder = os.path.join(temp_path, f'{repo}-{branch}')
                    logik_folder_temp = os.path.join(temp_path, 'LOGIK')

                    if os.path.exists(extracted_folder):
                        if os.path.exists(logik_folder_temp):
                            # Remove existing Logik folder if it exists in temp
                            shutil.rmtree(str(logik_folder_temp))
                        # Use string paths for os.rename compatibility
                        os.rename(str(extracted_folder), str(logik_folder_temp))
                        print(f"Renamed folder from '{os.path.basename(extracted_folder)}' to 'Logik' in temp folder")

                    # Delete the zip file
                    os.remove(zip_filepath_str)
                    print(f'Deleted zip file: {zip_filename}')

                    # Delete any loose files in temp folder
                    for file in os.listdir(os.path.join(temp_path, 'LOGIK')):
                        if os.path.isfile(os.path.join(temp_path, 'LOGIK', file)):
                            os.remove(os.path.join(temp_path, 'LOGIK', file))
                            print(f'Deleted loose file: {file}')

                    # Move the Logik folder from temp folder to destination folder
                    logik_folder_dest = os.path.join(destination_path, 'LOGIK')

                    if os.path.exists(logik_folder_temp):
                        # Always remove existing Logik folder in destination to ensure clean overwrite
                        if os.path.exists(logik_folder_dest):
                            print(f'Removing existing Logik folder in destination: {logik_folder_dest}')
                            remove_folder(logik_folder_dest)

                        # Move the Logik folder to destination (will use sudo if needed)
                        move_repo(logik_folder_temp, logik_folder_dest)

                        # Flatten the Logik folder to remove any README.md files
                        flatten_directory(logik_folder_dest)

                    progress_window.title = 'Download Completed'
                    progress_window.task_progress_message = f'Download Complete\n\nMatchbox Collection installed to:\n\n{logik_folder_dest}'
                    progress_window.tasks_complete = True

                except urllib.error.URLError as e:
                    print(f'Error downloading file: {e}')
                    if os.path.exists(zip_filepath_str):
                        os.remove(zip_filepath_str)
                    raise
                except zipfile.BadZipFile as e:
                    print(f'Error: Invalid zip file: {e}')
                    if os.path.exists(zip_filepath_str):
                        os.remove(zip_filepath_str)
                    raise
                except Exception as e:
                    print(f'Error: {e}')
                    import traceback
                    traceback.print_exc()
                    if os.path.exists(zip_filepath_str):
                        os.remove(zip_filepath_str)
                    raise

            # Open file browser to select matchbox install location
            path = pyflame.file_browser(
                title='Select Logik Matchbox Install Directory',
                path=self.settings.matchbox_path,
                select_directory=True,
                window_to_hide=self.window
                )
            if path:
                self.matchbox_install_path = path
            else:
                return

            # Save downloadpath to config file
            save_config()

            # Check if password is needed to install to selected location
            folder_write_permission = os.access(self.matchbox_install_path, os.W_OK)

            # If matchbox install path is not writeable, get system password and then download and install, otherwise just download and install
            if not folder_write_permission:
                print('Matchbox destination write permission: Not Writeable, need system password.')
                matchbox_password_window = PyFlamePasswordWindow(
                    text=f'System password needed to install Logik Matchboxes to selected location.',
                    parent=self.window,
                    )
                system_password = matchbox_password_window.password
                if system_password:
                    download_matchbox_repo(system_password)
                else:
                    return
            else:
                print('Matchbox destination write permission: Writeable')
                download_matchbox_repo()

        def add_matchbox_to_batch():

            def create_matchbox_node(matchbox_file_name, destination_folder):

                # Get cursor position
                cursor_pos = flame.batch.cursor_position

                # Create matchbox node
                matchbox_node = flame.batch.create_node('Matchbox', os.path.join(destination_folder, matchbox_file_name))
                matchbox_node.pos_x = cursor_pos[0]
                matchbox_node.pos_y = cursor_pos[1]

                matchbox_node.load_node_setup(os.path.join(destination_folder, selected_matchbox_name))

            # Switch to batch tab
            flame.set_current_tab('Batch')

            # Get selected matchbox name
            selected_matchbox_name = self.matchbox_tree.selectedItems()[0].text(0)
            print('Selected matchbox to load:', selected_matchbox_name)

            # Download matchbox from GitHub repository to temp matchbox directory and return path to destination folder
            destination_folder = self.download_github_folder(folder_name=selected_matchbox_name, repo_name="matchbox")

            # Get list of files in destination folder
            selected_matchbox_files = os.listdir(destination_folder)

            # Get name of glsl file or mx file to load into matchbox node
            glsl_files = [file for file in selected_matchbox_files if file.endswith('.glsl')]

            if glsl_files != []:
                glsl_file = glsl_files[-1]
                matchbox_file_name = glsl_file.split('/')[-1]
            else:
                matchbox_file_name = [file for file in selected_matchbox_files if file.endswith('.mx')][0].rsplit('/', 1)[-1]

            # Add matchbox node to batch
            create_matchbox_node(matchbox_file_name, destination_folder)

            # Delete destination folder
            shutil.rmtree(destination_folder)

        def matchbox_search():

            update_matchbox_tree(search=self.matchbox_search_entry.text)

        def get_matchbox_description():

            """
            Get Matchbox Description
            ========================

            Get selected matchbox description from JSON file and display in text edit.
            """

            self.get_json_description(
                label=self.matchbox_desciption_label,
                label_text='Matchbox Description',
                tree=self.matchbox_tree,
                json_path=self.matchbox_json_path,
                text_edit=self.matchbox_text_edit,
                )

        def update_matchbox_tree(search: str=None) -> None:
            """
            Update Matchbox Tree
            =====================

            Update matchbox tree with matchboxes from xml file.

            Args
            ----
                search (str):
                    String to search for in matchbox name. If search string is present, only add items that match the search string.
                    (Default: None)
            """

            pyflame.print('Updating Matchbox List...', underline=True, new_line=False)

            def add_matchbox(matchbox):
                shader_type = matchbox.get('shader_type', '')
                author_name = matchbox.get('author', '')
                self.matchbox_tree.add_item_with_columns([matchbox_name, shader_type, author_name])

            self.matchbox_tree.clear()

            # Read in matchboxes from JSON
            with open(self.matchbox_json_path, 'r', encoding='utf-8') as f:
                matchboxes = json.load(f)

            # Add items to matchbox tree
            if search:
                for matchbox in matchboxes:
                    matchbox_name = matchbox.get('name', '')
                    if search.lower() in matchbox_name.lower():
                        add_matchbox(matchbox)
            else:
                for matchbox in matchboxes:
                    matchbox_name = matchbox.get('name', '')
                    add_matchbox(matchbox)

            # Select top item in matchbox list
            self.matchbox_tree.setCurrentItem(self.matchbox_tree.topLevelItem(0))

            # Get selected Matchbox description if Matchbox is selected.
            try:
                get_matchbox_description()
            except:
                print('Unable to get Matchbox description. No Matchbox selected\n')

            pyflame.print('Matchbox List Updated', text_color=TextColor.GREEN)

        # ==============================================================================
        # [Tab 3: Matchbox Tab]
        # ==============================================================================

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
        self.matchbox_text_edit = PyFlameTextBrowser(
            text=self.file_description,
            text_type=TextType.HTML,
            text_style=TextStyle.READ_ONLY,
            )

        # Matchbox TreeWidget
        self.matchbox_tree = PyFlameTreeWidget(
            column_names=[
                'Matchbox Name',
                'Shader Type',
                'Author',
                ],
            connect=get_matchbox_description,
            sort=True,
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

        update_matchbox_tree()

        # ==============================================================================
        # [Matchbox Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_logik_matchbox_collection_label, 0, 0, 1, 7)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_tree, 1, 0, 8, 7)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_add_to_batch, 9, 5)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_download_all_button, 9, 6)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_search_label, 10, 4)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_search_entry, 10, 5, 1, 2)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_desciption_label, 12, 0, 1, 7)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_text_edit, 13, 0, 7, 7)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_done_button, 20, 6)

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
                        'open_batch': self.open_batch_button.checked,
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
                window_to_hide=self.window
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
                        message_type=MessageType.CONFIRM,
                        parent=self.window,
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
                self.download_ftp_file(
                    download_type='Batch Setup',
                    file_name=batch_name,
                    ftp_file_path=ftp_file_path,
                    tgz_path=tgz_path,
                    )

                # Uncompress tgz file
                tgz_escaped_path = tgz_path.replace(' ', '\\ ')
                download_escaped_path = self.settings.batch_setup_download_path.replace(' ', '\\ ') + '/'
                tar_command = f'tar -xvf "{tgz_escaped_path}" -C "{download_escaped_path}"'
                os.system(tar_command)

                # Delete tgz file
                os.remove(tgz_path)

                if self.open_batch_button.checked:
                    open_batch()

        def submit_batch_setup():

            def get_batch_name():
                """
                Fill in Batch Name field once valid batch path is entered. Must end with .batch
                If .flare is in file path, remove it
                """

                if self.submit_batch_path_entry.path.endswith('.batch'):
                    batch_name = self.submit_batch_path_entry.path.rsplit('/', 1)[1][:-6]
                    if batch_name.endswith('.flare'):
                        batch_name = batch_name[:-6]
                    self.submit_batch_name_entry.text = batch_name
                else:
                    self.submit_batch_name_entry.text = ''

            def get_batch_setup_info():
                """
                Get selected batch setup info.
                """

                batch_setup_path = self.submit_batch_path_entry.path

                if batch_setup_path:
                    self.submit_batch_path_entry.path = batch_setup_path
                    batch_name = batch_setup_path.rsplit('/', 1)[1][:-6]
                    if batch_name.endswith('.flare'):
                        batch_name = batch_name[:-6]
                    self.submit_batch_name_entry.text = batch_name

            def batch_setup_upload():

                def save_config():
                    """
                    Save Config
                    ===========

                    Save path to config file
                    """

                    self.settings.save_config(
                        config_values={
                            'batch_submit_path': self.submit_batch_path_entry.path
                            }
                        )

                def compress_batch_setup():
                    """
                    Compress Batch Setup
                    ====================

                    Compress batch setup files into a tgz file.
                    """

                    # Add batch files to tar file
                    batch_folder_path = self.submit_batch_path_entry.path[:-6]
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
                    text.insert(1, f"        <artist>'{self.submit_batch_artist_name_entry.text}'</artist>")
                    text.insert(2, f"        <flame_version>'{self.submit_batch_flame_version_entry.text}'</flame_version>")
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
                        pyflame.cursor_restore()
                        self.ftp.quit()
                        PyFlameMessageWindow(
                            message='Batch Setup Already Exists. Rename And Try Again.',
                            message_type=MessageType.ERROR,
                            parent=self.submit_batch_window,
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

                if not os.path.isfile(self.submit_batch_path_entry.path):
                    PyFlameMessageWindow(
                        message='Enter valid batch setup path.',
                        message_type=MessageType.ERROR,
                        parent=self.submit_batch_window,
                        )
                    return
                elif self.submit_batch_artist_name_entry.text == '':
                    PyFlameMessageWindow(
                        message='Enter Artist name.',
                        message_type=MessageType.ERROR,
                        parent=self.submit_batch_window,
                        )
                    return
                elif self.submit_batch_description_text_edit.toPlainText() == '':
                    PyFlameMessageWindow(
                        message='Enter batch setup description.',
                        message_type=MessageType.ERROR,
                        parent=self.submit_batch_window,
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
                parent=self.window,
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

            # Entries
            self.submit_batch_name_entry = PyFlameEntry(
                text='',
                read_only=True,
                )
            self.submit_batch_artist_name_entry = PyFlameEntry(
                text='',
                )
            self.submit_batch_flame_version_entry = PyFlameEntry(
                text=flame_version,
                read_only=True,
                )

            # Entry File Browser
            self.submit_batch_path_entry = PyFlameEntryBrowser(
                path=self.settings.batch_submit_path,
                connect=get_batch_setup_info,
                browser_type=BrowserType.FILE,
                browser_ext=['batch'],
                browser_title='Select Batch Setup',
                window_to_hide=[self.window, self.submit_batch_window]
                )

            get_batch_name()

            # TextEdit
            self.submit_batch_description_text_edit = PyFlameTextEdit(
                text=self.file_description,
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

            # ==============================================================================
            # [Widget Layout]
            # ==============================================================================

            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_label, 0, 0, 1, 6)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_path_label, 1, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_name_label, 2, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_artist_name_label, 3, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_flame_version_label, 4, 0)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_description_label, 5, 0)

            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_path_entry, 1, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_name_entry, 2, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_artist_name_entry, 3, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_flame_version_entry, 4, 1, 1, 5)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_description_text_edit, 5, 1, 6, 5)

            self.submit_batch_window.grid_layout.addWidget(self.submit_cancel_button, 12, 4)
            self.submit_batch_window.grid_layout.addWidget(self.submit_batch_upload_button, 12, 5)

        def batch_setup_search():

            self.update_batch_setups_tree(search=self.batch_setups_search_entry.text)

        # ==============================================================================
        # [Tab 4: Batch Setups Tab]
        # ==============================================================================

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
            text_style=TextStyle.READ_ONLY,
            )

        # Batch Setups TreeWidget
        self.batch_setups_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Flame',
                'Artist',
                ],
            connect=self.get_batch_description,
            sort=True,
            )

        self.batch_setups_tree.setColumnWidth(0, 600)
        self.batch_setups_tree.setColumnWidth(1, 100)
        self.batch_setups_tree.setColumnWidth(2, 300)

        # Disable batch download button if current flame version older than batch minimum
        #self.batch_setups_tree.clicked.connect(self.check_batch_flame_version)

        # Push Buttons
        self.open_batch_button = PyFlamePushButton(
            text=' Open Batch',
            checked=self.settings.open_batch,
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

        # ==============================================================================
        # [Batch Setups Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_label, 0, 0, 1, 7)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_tree, 1, 0, 7, 7)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_submit_button, 8, 0)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.open_batch_button, 8, 5)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_download_button, 8, 6)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_search_label, 9, 4)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_search_entry, 9, 5, 1, 2)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_desciption_label, 10, 0, 1, 7)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_text_edit, 11, 0, 7, 7)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_done_button, 19, 6)

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
                            'inference_node_add_to_batch': self.inference_node_add_to_batch_pushbutton.checked,
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
                self.download_ftp_file(
                    download_type='Inference Node',
                    file_name=inference_node_name,
                    ftp_file_path=ftp_file_path,
                    tgz_path=tgz_path,
                    )

                # Uncompress tgz file
                tgz_escaped_path = tgz_path.replace(' ', '\\ ')
                download_escaped_path = inference_node_download_path.replace(' ', '\\ ') + '/'
                tar_command = f'tar -xvf "{tgz_escaped_path}" -C "{download_escaped_path}"'
                os.system(tar_command)

                # Delete tgz file
                os.remove(tgz_path)

                if self.inference_node_add_to_batch_pushbutton.checked:
                    print('\n')
                    add_inference_node_to_batch()

            # Get path to download archive to
            inference_node_download_path = pyflame.file_browser(
                title='Select Download Path',
                path=self.settings.inference_node_download_path,
                select_directory=True,
                window_to_hide=self.window
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
                if os.path.isfile(self.submit_inference_node_path_entry.path):
                    self.submit_inference_node_name_entry.text = os.path.basename(self.submit_inference_node_path_entry.path).split('.')[0]

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
                            'inference_node_submit_path': self.submit_inference_node_path_entry.path
                            }
                        )

                def compress_inference_node() -> str:
                    """
                    Compress Inference Node
                    =======================

                    Create tar(tgz) file of inference node files. Either INF or ONNX + JSON files.
                    """

                    pyflame.print('Creating Inference Node TAR file...')

                    inference_node = self.submit_inference_node_path_entry.path
                    #inference_node = inference_node.replace(' ', '\ ') # Escape spaces in file path
                    if inference_node.endswith('.onnx'):
                        inference_node_json = inference_node.replace('.onnx', '.json')
                    else:
                        inference_node_json = None

                    self.tar_file_name = self.submit_inference_node_name_entry.text
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

                        description_text = self.submit_inference_node_description_text_edit.text
                        description_text = description_text.replace("'", "\"")
                        description_text = description_text.replace('&', '-')

                        return description_text

                    def get_tar_file_size() -> str | bool:
                        """
                        Get Tar File Size
                        =================

                        Determines the size of the tar file specified by tar_file_path. If the file size exceeds 2GB,
                        an error message is displayed and the function returns False. Otherwise, the size of the file
                        is returned as a string in megabytes (MB).

                        Args
                        ----
                            `tar_file_path` (str):
                                The path to the tar file.

                        Returns
                        -------
                            str | bool:
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
                                    message_type=MessageType.ERROR,
                                    parent=self.submit_inference_node_window,
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
                                message_type=MessageType.ERROR,
                                parent=self.submit_inference_node_window,
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
                            f"        <flame_version>'{self.submit_inference_node_flame_version_entry.text}'</flame_version>",
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
                        pyflame.cursor_restore()
                        self.ftp.quit()
                        PyFlameMessageWindow(
                            message='Inference Node already exists. Rename and try again.',
                            message_type=MessageType.ERROR,
                            parent=self.submit_inference_node_window,
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
                if not os.path.isfile(self.submit_inference_node_path_entry.path):
                    PyFlameMessageWindow(
                        message='Path to ONNX of INF file is not valid. Try selecting file again.',
                        message_type=MessageType.ERROR,
                        parent=self.submit_inference_node_window,
                        )
                    return

                # If ONNX file, check for matching JSON file, if not give error.
                if self.submit_inference_node_path_entry.path.endswith('.onnx'):
                    node_path = self.submit_inference_node_path_entry.path.rsplit('/', 1)[0]
                    json_file = self.submit_inference_node_path_entry.path.replace('.onnx', '.json')
                    if not os.path.isfile(os.path.join(node_path, json_file)):
                        PyFlameMessageWindow(
                            message='ONNX file must have a JSON file with a matching file name.\n\nExample:\n\n    inference_node.onnx\n    inference_node.json',
                            message_type=MessageType.ERROR,
                            parent=self.submit_inference_node_window,
                            )
                        return

                # Check for Inference Node Description
                if self.submit_inference_node_description_text_edit.toPlainText() == '':
                    PyFlameMessageWindow(
                        message='Enter Inference Node description.',
                        message_type=MessageType.ERROR,
                        parent=self.submit_inference_node_window,
                        )
                    return

                # If all fields are filled in, save config, compress node file(s), create xml file, and upload to Logik Portal.
                else:
                    save_config()
                    compress_inference_node()
                    xml_file_created = create_inference_node_xml_file()
                    if xml_file_created:
                        upload_inference_node()

            flame_version = str(self.flame_version)
            if flame_version.endswith('.0'):
                flame_version = flame_version[:-2]

            # Create Inference Node Submit Window
            self.submit_inference_node_window = PyFlameWindow(
                title='Submit Inference Node',
                return_pressed=inference_node_upload,
                grid_layout_columns=6,
                grid_layout_rows=13,
                parent=self.window,
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
            self.submit_inference_node_name_entry = PyFlameEntry(
                text='',
                read_only=True,
                )
            self.submit_inference_node_flame_version_entry = PyFlameEntry(
                text=flame_version,
                read_only=True,
                )

            # Entry File Browser
            self.submit_inference_node_path_entry = PyFlameEntryBrowser(
                path=self.settings.inference_node_submit_path,
                connect=get_inference_node_name,
                browser_ext=['onnx', 'inf'],
                browser_title='Select Inference Node (ONNX/INF)',
                window_to_hide=[self.window, self.submit_inference_node_window]
                )
            get_inference_node_name()

            # TextEdit
            self.submit_inference_node_description_text_edit = PyFlameTextEdit(
                text=self.file_description,
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

            # ==============================================================================
            # [Widget Layout]
            # ==============================================================================

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_label, 0, 0, 1, 6)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_path_label, 1, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_name_label, 2, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_flame_version_label, 3, 0)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_description_label, 4, 0)

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_path_entry, 1, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_name_entry, 2, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_flame_version_entry, 3, 1, 1, 5)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_description_text_edit, 4, 1, 7, 5)

            self.submit_inference_node_window.grid_layout.addWidget(self.submit_archive_cancel_button, 12, 4)
            self.submit_inference_node_window.grid_layout.addWidget(self.submit_inference_node_upload_button, 12, 5)

        def inference_node_search() -> None:
            """
            Inference Node Search
            =====================

            Search for inference nodes in the inference node tree. Update tree with search results as user types.
            """

            self.update_inference_node_tree(search=self.inference_node_search_entry.text)

        # ==============================================================================
        # [Tab 5: Inference Nodes]
        # ==============================================================================

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
            text_style=TextStyle.READ_ONLY,
            )

        # TreeWidgets
        self.inference_node_tree = PyFlameTreeWidget(
            column_names=[
                'Name',
                'Flame',
                'Size',
                ],
            connect=self.get_inference_node_description,
            sort=True,
            elide_text=True,
            )

        self.inference_node_tree.setColumnWidth(0, 1000)
        self.inference_node_tree.setColumnWidth(1, 100)
        self.inference_node_tree.setColumnWidth(2, 100)

        #Push Buttons
        self.inference_node_add_to_batch_pushbutton = PyFlamePushButton(
            text=' Add to Batch',
            checked=self.settings.inference_node_add_to_batch,
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

        # ==============================================================================
        # [Inference Nodes Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_nodes_label, 0, 0, 1, 7)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_tree, 1, 0, 7, 7)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_submit_button, 8, 0)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_add_to_batch_pushbutton, 8, 5)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_download_button, 8, 6)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_search_label, 9, 4)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_search_entry, 9, 5, 1, 2)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_description_label, 10, 0, 1, 7)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_description_text_edit, 11, 0, 7, 7)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_done_button, 19, 6)

    # ==============================================================================

    def get_updates(self) -> None:
        """
        Get Updates
        ===========

        Get updates.txt from Logik Portal and display in the descriptions text edit when the Portal first opens.
        """

        def apply_update(label, text_window):

            # Set the script description label to Logik Portal Updates
            label.text = 'Logik Portal Updates'

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

    # ==============================================================================
    # [Python Scripts]
    # ==============================================================================

    def check_script_flame_version(self, tree) -> None:
        """
        Check Script Flame Version
        ==========================

        Check if script is compatible with current version of Flame.
        If script won't work with current version of Flame, disable the install button.

        Args
        ----
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
            # If script_flame_max_version has two '.'s, remove the last one. So '2025.9.9' becomes '2025.9'.
            parts = script_flame_max_version.split('.')
            if len(parts) > 2:
                script_flame_max_version = '.'.join(parts[:2])

            if float(script_flame_max_version) < float(self.flame_version):
                print(f'--> {script_name}: Does not work with this version of Flame.\n')
                self.install_script_button.setEnabled(False)
        else:
            print(f'--> {script_name}: Flame version compatible.\n')
            self.install_script_button.setEnabled(True)

    # ==============================================================================
    # [Common]
    # ==============================================================================

    def get_description(self, label, label_text, tree, xml_path, findall, text_edit, index, download_button):
        """
        Get Description
        ===============

        Get item description from xml file and show in text edit.

        Args
        ----
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

            download_button (PyFlameButton):
                Download button widget.
        """

        selected_item = tree.selectedItems()
        item = selected_item[0]
        item_name = item.text(0)
        item_name = item_name.replace(' ', '_')
        item_version = item.text(1)

        # If item version is less than or equal to flame version, enable download button. Otherwise, disable it.
        download_button.enabled = float(item_version) <= float(self.flame_version)

        # Add items from xml to matchbox list
        xml_tree = ET.parse(xml_path)
        root = xml_tree.getroot()

        for item in root.findall(findall):
            if item.get('name') == item_name:
                text_edit.setPlainText(item[index].text[1:-1])

        # Switch text edit label to 'Script Description'. This is named 'Logik Portal Updates' when the script first loads.
        label.text = label_text

    def get_json_description(self, label, label_text, tree, json_path, text_edit):
        """
        Get Description
        ===============

        Get item description from xml file and show in text edit.

        Args
        ----
            label (PyFlameLabel):
                Label to switch text to 'Script Description'.

            label_text (str):
                Text to switch label to.

            tree (PyFlameTreeWidget):
                Tree widget.



            text_edit (PyFlameTextEdit):
                Text edit widget.
        """

        selected_item = tree.selectedItems()
        item = selected_item[0]
        item_name = item.text(0)
        item_name = item_name.replace(' ', '_')

        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for item in data:
                if item['name'] == item_name:
                    raw_description = item.get('description', '')

                    # Convert escaped \n and \t into actual characters
                    description = bytes(raw_description, "utf-8").decode("unicode_escape")

                    # Escape HTML characters
                    description = html.escape(description)

                    # Convert URLs to clickable links
                    description = re.sub(
                        r'(https?://[^\s<>"]+)',
                        r'<a href="\1">\1</a>',
                        description
                        )

                    # Convert emails to mailto: links
                    description = re.sub(
                        r'([\w\.-]+@[\w\.-]+\.\w+)',
                        r'<a href="mailto:\1">\1</a>',
                        description
                        )

                    # Replace newlines and tabs with HTML
                    description = description.replace('\n', '<br>')
                    description = description.replace('\t', '&emsp;')

                    # Wrap in paragraph tags
                    html_text = f'<p>{description}</p>'

                    # Show in QTextEdit
                    text_edit.setReadOnly(True)
                    text_edit.setHtml(html_text)

        # Switch text edit label to 'Script Description'. This is named 'Logik Portal Updates' when the script first loads.
        label.text = label_text

    def download_xmls(self) -> None:
        """
        Download XMLS
        =============

        Download Batch and Inference Node file list XMLs from ftp to temp folder.
        """

        pyflame.print('Downloading Batch Setup and Inference Node XML Files...', underline=True, new_line=False)

        # Download batch setups xml
        self.batch_setups_xml_path = os.path.join(self.temp_folder, 'batch_setups.xml')
        self.ftp.retrbinary('RETR ' + '/Batch_Setups/batch_setups.xml', open(self.batch_setups_xml_path, 'wb').write)
        pyflame.print('Batch Setups XML Downloaded', text_color=TextColor.GREEN, new_line=False)

        # Download inference nodes xml
        self.inferences_xml_path = os.path.join(self.temp_folder, 'inference_nodes_.xml')
        self.ftp.retrbinary('RETR ' + '/Inference_Nodes/inference_nodes_.xml', open(self.inferences_xml_path, 'wb').write)
        pyflame.print('Inference Nodes XML Downloaded', text_color=TextColor.GREEN)

    def download_github_jsons(self) -> None:
        """
        Download Github JSONS
        =====================

        Download json files from github to temp folder.
        """

        pyflame.print('Downloading Github JSON Files...', underline=True)

        # Github json urls
        matchbox_json_url = "https://raw.githubusercontent.com/logik-portal/matchbox/main/matchbox_collection.json"
        python_scripts_json_url = "https://raw.githubusercontent.com/logik-portal/python/main/python_scripts.json"

        def download_json(url, path):
            try:
                urllib.request.urlretrieve(url, path)
                pyflame.print(f'Downloaded: {url}', text_color=TextColor.GREEN, new_line=False)
            except Exception as e:
                pyflame.print(f"Download failed: {url}", text_color=TextColor.RED, new_line=False)

        download_json(matchbox_json_url, self.matchbox_json_path)
        download_json(python_scripts_json_url, self.python_scripts_json_path)

        print('\n', end='')

    def download_ftp_file(self, download_type: str, file_name: str, ftp_file_path: str, tgz_path: str) -> None:
        """
        Download File
        =============

        Download selected file from Portal with progress window

        Args
        ----
            download_type (str):
                Type of file being downloaded (Python Script, Matchbox, Batch Setup, Inference Node).

            file_name (str):
                Name of file being downloaded.

            ftp_file_path (str):
                Path to file on Portal.

            tgz_path (str):
                Temp folder path to download file to.
        """

        pyflame.print(f'Downloading {download_type}: {file_name}', underline=True)

        # Connect to Portal
        self.ftp_download_connect()

        # Get file size
        file_size = self.ftp.size(ftp_file_path)

        file_size = file_size / 1000
        file_size = int(round(file_size, 1))
        num_to_do = file_size
        file_size = str(file_size) + ' KB'

        # Create progress window
        self.progress_window = PyFlameProgressWindow(
            total_tasks=num_to_do,
            title=f'{SCRIPT_NAME}: Downloading',
            task_progress_message=f'{download_type}: {file_name}\n\n0 KB of {file_size}',
            parent=self.window,
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
            self.progress_window.processing_task = downloaded_progress
            self.progress_window.task_progress_message = f'{download_type}: {file_name}\n\n{downloaded_bytes} of {file_size}'

        # Retrieve file in binary mode with a callback
        self.ftp.retrbinary(f'RETR {ftp_file_path}', write_and_update)

        # Set final progress window values
        self.progress_window.task_progress_message = f'{download_type}: {file_name}\n\n{file_size} of {file_size}\n\nDownload Complete.'
        self.progress_window.processing_task = num_to_do
        self.progress_window.tasks_complete = True
        self.progress_window.title = 'Download Complete'

        # Disconnect from ftp
        self.ftp.quit()

    def upload_file(self, upload_type: str, file_name: str, xml_path: str, tgz_path: str) -> None:
        """
        Upload File
        ===========

        Upload files to ftp with progress window

        Args
        ----
            upload_type (str):
                Type of file being uploaded (Batch Setup, Inference Node).

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

            self.progress_window.processing_task = upload_progress
            self.progress_window.task_progress_message = f'{upload_type}: {file_name}\n\n{uploaded_bytes} of {file_size}'
            return data

        pyflame.cursor_busy()

        pyflame.print(f'Uploading: {file_name}')

        if upload_type == 'Batch Setup':
            upload_folder = '/Submit_Batch_Setups'
        elif upload_type == 'Inference Node':
            upload_folder = '/Submit_Inference_Node'

        # Tgz upload file path on ftp
        ftp_tgz_path = os.path.join(upload_folder, file_name) + '.tgz'

        # XML upload file path on ftp
        ftp_xml_path = os.path.join(upload_folder, file_name) + '.xml'

        # Connect to ftp if not uploading python script - python script uses a different ftp connection
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
            total_tasks=num_to_do,
            title=f'{SCRIPT_NAME}: Uploading',
            task_progress_message=f'{upload_type}: {file_name}\n\n0 KB of {file_size}',
            parent=self.window,
            )

        # Upload xml file to ftp
        with open(xml_path, 'rb') as f:
            self.ftp.storbinary(f'STOR {ftp_xml_path}', f)
        print(f'--> {file_name}.xml uploaded to Portal.\n')

        # Upload tgz file to Portal
        uploaded = 0 # Variables to store progress

        # Open the file and upload in binary mode with a callback
        with open(tgz_path, 'rb') as f:
            self.ftp.storbinary(f'STOR {ftp_tgz_path}', f, callback=read_and_update)

        pyflame.cursor_restore()

        # Set final progress window message
        self.progress_window.task_progress_message = f'{upload_type}: {file_name}\n\n{file_size} of {file_size}\n\nUpload Complete.'
        self.progress_window.processing_task = num_to_do

        # Check that both files were uploaded to site, if not display error message
        if f'{os.path.join(upload_folder, file_name)}.tgz' and f'{os.path.join(upload_folder, file_name)}.xml' not in self.ftp.nlst(upload_folder):
            self.ftp.quit()
            PyFlameMessageWindow(
                message='Upload failed. Try again.',
                message_type=MessageType.ERROR,
                parent=self.window,
                )
            return

        self.progress_window.tasks_complete = True
        self.progress_window.title = 'Upload Complete'

        # Clean up temp folder
        os.remove(xml_path)
        os.remove(tgz_path)

        # Disconnect from Portal
        self.ftp.quit()

    def done(self):
        """
        Done
        ====

        Close the Logik Portal window.
        """

        # Get current tab name
        current_tab_name = self.tabs.get_current_tab_name()
        #print('current_tab_name: ', current_tab_name)

        # Save current tab to config
        self.settings.save_config(
            config_values={
                'last_tab': current_tab_name,
                'script_install_path': self.script_install_path_browse.path
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

    # ==============================================================================
    # [Batch Setups]
    # ==============================================================================

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

        self.get_description(
            label=self.batch_setups_desciption_label,
            label_text='Batch Setup Description',
            tree=self.batch_setups_tree,
            xml_path=self.batch_setups_xml_path,
            findall='batch',
            text_edit=self.batch_setups_text_edit,
            index=2,
            download_button=self.batch_setups_download_button,
            )

    def update_batch_setups_tree(self, search: str=None) -> None:
        """
        Update Batch Setups Tree
        ========================

        Add batch setups to batch setups tree from xml file. If search string is present, only add items that match the search string.

        Args
        ----
            search (str):
                String to search for in batch setup name. If search string is present, only add items that match the search string.
                (Default: None)
        """

        def add_batch_setup(batch):
            flame_version = str(batch[1].text[1:-1])
            artist_name = str(batch[0].text[1:-1])

            batch_setup = self.batch_setups_tree.add_item_with_columns([batch_name, flame_version, artist_name])

            # if batch setup requires newer version of flame grey out script entry
            if float(self.flame_version) < float(flame_version):
                self.batch_setups_tree.color_item(batch_setup, color='#555555')

        pyflame.print('Updating Batch Setups List...', underline=True, new_line=False)

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

    # ==============================================================================
    # [Inference Nodes]
    # ==============================================================================

    def get_inference_node_description(self):
        """
        Get Inference Node Description
        ==============================

        Get selected inference node description from xml file and display in text edit.
        """

        self.get_description(
            label=self.inference_node_description_label,
            label_text='Inference Node Description',
            tree=self.inference_node_tree,
            xml_path=self.inferences_xml_path,
            findall='inference_node',
            text_edit=self.inference_node_description_text_edit,
            index=2,
            download_button=self.inference_node_download_button,
            )

    def update_inference_node_tree(self, search: str=None) -> None:
        """
        Update Inference Node Tree
        ==========================

        Update inference node tree from xml file. If search string is present, only add items that match the search string.

        Args
        ----
            search (str):
                String to search for in inference node name. If search string is present, only add items that match the search string.
                (Default: None)
        """

        def add_inference_node(node):
            flame_version = str(node[0].text[1:-1])
            inference_node_size = str(node[1].text[1:-1])

            inference_node = self.inference_node_tree.add_item_with_columns([inference_node_name, flame_version, inference_node_size])

            # if node requires newer version of flame grey out script entry
            if float(self.flame_version) < float(flame_version):
                self.inference_node_tree.color_item(inference_node, color='#555555')

        pyflame.print('Updating Inference Node List...', underline=True, new_line=False)

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

    # ==============================================================================

# ==============================================================================
# [Flame Menus]
# ==============================================================================

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
