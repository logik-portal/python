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
Script Version: 7.1.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 10.31.20
Update Date: 05.04.26

Script Type: Flame Main Menu

Description:

    Install python scripts, batch setups, inference nodes, and matchboxes from logik-portal.com

Notes:

    Installing the Logik Matchbox Collection may be slow when installing over a network due to large numbder of small files.

URL:
    https://logik-portal.com

Menu:

    Flame Main Menu -> Logik -> Logik Portal

To install:

    Copy script into /opt/Autodesk/shared/python/logik_portal

Updates:

    v7.1.0 05.04.26
        - Submit buttons now redirect to logik-portal.com for submissions.
        - All files are now downloaded from logik-portal.com. FTP server is no longer used.
        - Increased window size.
        - Downloads now happen much faster.
        - Updated to PyFlameLib v5.3.1.

    v7.0.1 01.04.26
        - Fixed window sizing issue.

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

import io
import os
import re
import html
import json
import shutil
import zipfile
import urllib.request
import subprocess
import webbrowser
from typing import Optional
import ast
import sys

import flame
from lib.pyflame_lib_logik_portal import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Logik Portal'
SCRIPT_VERSION = 'v7.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class LogikPortal:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Check internet connection
        internet_connection_check = self.check_internet_connection()
        if not internet_connection_check:
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

        # Define temp folders
        self.temp_folder = os.path.join(SCRIPT_PATH, 'temp')
        self.temp_python_scripts_folder = os.path.join(self.temp_folder, 'python_scripts')
        self.temp_matchbox_folder = os.path.join(self.temp_folder, 'matchbox')
        self.temp_batch_folder = os.path.join(self.temp_folder, 'batch_setups')
        self.temp_inference_node_folder = os.path.join(self.temp_folder, 'inference_nodes')

        # Create temp folders
        temp_folders_created = self.create_temp_folders()
        if not temp_folders_created:
            pyflame.print('Error creating temp folders.', print_type=PrintType.WARNING)
            return

        #  Init variables
        self.installed_script_dict = {}
        self.file_description = ''
        self.batch_group: Any = None

        # JSON Paths
        self.python_scripts_json_path = os.path.join(self.temp_folder, 'python_scripts.json')
        self.batch_setups_json_path = os.path.join(self.temp_folder, 'batch_setups.json')
        self.matchbox_json_path = os.path.join(self.temp_folder, 'matchbox_collection.json')
        self.inference_nodes_json_path = os.path.join(self.temp_folder, 'inference.json')

        # Download JSON files
        json_downloaded = self.download_jsons()
        if not json_downloaded:
            PyFlameMessageWindow(
                message='Error downloading JSON files.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Open main window
        self.main_window()

        # Go to last used tab
        self.tabs.set_current_tab(self.settings.last_tab)

        # Get site updates
        self.get_updates()

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
                'batch_setup_download_path': '/opt/Autodesk',
                'batch_submit_path': '/opt/Autodesk',
                'script_submit_path': '/opt/Autodesk',
                'script_install_local_path': self.autodesk_scripts_path,
                'script_install_path': '/opt/Autodesk/shared/python',
                'open_batch': True,
                'inference_node_download_path': '/opt/Autodesk',
                'inference_node_submit_path': '/opt/Autodesk',
                'inference_node_add_to_batch': True,
                'last_tab': 'Python Scripts',
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
            os.makedirs(self.temp_inference_node_folder)
            os.makedirs(self.temp_batch_folder)
            os.makedirs(self.temp_python_scripts_folder)
            return True
        except Exception as exc:
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

        Check internet connection.
        """

        # Check internet connection.
        try:
            urllib.request.urlopen("https://www.google.com", timeout=3)
            return True
        except Exception as exc:
            PyFlameMessageWindow(
                message="Can't connect to internet.\nCheck internet connection and try again.\nInternet connection is required for this script to work.",
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

    def download_jsons(self) -> bool:
        """
        Download JSONS
        ==============

        Download json to temp folder.

        Returns
        -------
            bool:
                True if all JSON files downloaded successfully, False if any failed.
        """

        pyflame.print('Downloading Logik Portal JSON Files...', underline=True)

        # JSON urls
        python_scripts_url = 'https://raw.githubusercontent.com/logik-portal/python/main/python_scripts.json'
        matchbox_url ='https://raw.githubusercontent.com/logik-portal/matchbox/main/matchbox_collection.json'
        batch_setups_url = 'https://logik-portal.com/files/batch_setups/batch_setups.json'
        inference_url = 'https://logik-portal.com/files/inference/inference.json'

        def download_json(url, path) -> bool:
            try:
                urllib.request.urlretrieve(url, path)
                pyflame.print(f'Downloaded: {url}', text_color=TextColor.GREEN, new_line=False)
                return True
            except Exception as exc:
                pyflame.print(f'Download failed: {url} ({exc})', print_type=PrintType.WARNING, new_line=False)
                return False

        # Track success of each JSON download so caller can react to failures.
        results = [
            download_json(python_scripts_url, self.python_scripts_json_path),
            download_json(matchbox_url, self.matchbox_json_path),
            download_json(batch_setups_url, self.batch_setups_json_path),
            download_json(inference_url, self.inference_nodes_json_path),
        ]

        print('\n', end='')

        return all(results)

    def get_updates(self) -> None:
        """
        Get Updates
        ===========

        Download latest_scripts.json from Logik Portal and display a formatted
        list of recent scripts in the description text edit when the Portal opens.
        """

        def apply_update(label, text_window):
            label.setText('Logik Portal Updates')
            text_window.setPlainText(updates)

        # Download and format latest scripts JSON
        latest_scripts_url = 'https://logik-portal.com/json/latest_scripts.json'
        try:
            with urllib.request.urlopen(latest_scripts_url) as resp:
                scripts = json.loads(resp.read().decode('utf-8'))

            print('scripts: ', scripts)

            lines = ['Latest Updates\n']
            for entry in scripts:
                name = entry.get('name', '')
                version = entry.get('version', '')
                date = entry.get('date', '')
                description = entry.get('description', '')
                update = entry.get('latest_update', '')
                lines.append(f'{name}  v{version}  ({date})')
                if description:
                    lines.append(description)
                if update:
                    update = f'Update:\n{update}'
                    lines.append(update)
                lines.append('')

            updates = '\n'.join(lines)
        except Exception as exc:
            updates = f'Unable to retrieve latest scripts:\n{exc}'

        print('updates: ', updates)

        print('last_tab: ', self.settings.last_tab)

        # Display in the active tab's description area
        if self.settings.last_tab == 'Python Scripts':
            apply_update(self.script_description_label, self.script_description_text_edit)
        elif self.settings.last_tab == 'Matchbox':
            apply_update(self.matchbox_desciption_label, self.matchbox_text_edit)
        elif self.settings.last_tab == 'Batch Setups':
            apply_update(self.batch_setups_desciption_label, self.batch_setups_text_edit)
        elif self.settings.last_tab == 'Inference Nodes':
            apply_update(self.inference_node_description_label, self.inference_node_description_text_edit)

    # ==============================================================================
    # [Main Window & Tabs]
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
            grid_layout_columns=9,
            grid_layout_rows=20,
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
            grid_layout_columns=9,
            grid_layout_rows=20,
            grid_layout_adjust_column_widths={
                4: 50,
                }
            )

        # Load Tabs
        self.python_scripts_tab()
        self.matchbox_tab()
        self.batch_setups_tab()
        self.inference_nodes_tab()

        # Add Tab Widget to Main Window
        self.window.grid_layout.addWidget(self.tabs, 0, 0, 20, 9)

    def python_scripts_tab(self):

        def check_script_flame_version(tree) -> None:
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

        def update_logik_portal_scripts_tree(search: str=''):
            """
            Update Logik Portal Scripts Tree
            ================================

            Add Logik Portal python scripts to Portal Python Scripts tree.

            Get script info from JSON file and add to tree list. If a newer version of the script exists on the site, highlight the script entry.
            If the script requires a newer version of flame, grey out the script entry.

            Args
            ----
                search (str, optional):
                    The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                    (Default: '')
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
                if flame_min_version:
                    flame_min_version = flame_min_version[:6]
                flame_max_version = python_script.get('Maximum Flame Version')
                if flame_max_version:
                    flame_max_version = flame_max_version[:6]
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
                        try:
                            min_ver = tuple(int(x) for x in flame_min_version.split('.'))
                            max_ver = tuple(int(x) for x in flame_max_version.split('.'))
                            cur_ver = tuple(int(x) for x in str(self.flame_version).split('.'))

                            # If a newer version of the script exists on the site, highlight it
                            if script_name in self.installed_script_dict:
                                installed_script_version = self.installed_script_dict.get(script_name)
                                if installed_script_version is not None:
                                    inst_ver = tuple(int(x) for x in str(installed_script_version).split('.'))
                                    script_ver = tuple(int(x) for x in str(script_version).split('.'))
                                    if script_ver > inst_ver:
                                        self.portal_scripts_tree.color_item(item, color='#ffffff')

                            # If script requires a newer version of flame, grey out
                            if cur_ver < min_ver:
                                self.portal_scripts_tree.color_item(item, color='#555555')

                            # If script's max flame version is exceeded, grey out
                            if flame_max_version != 'Latest':
                                if cur_ver > max_ver:
                                    self.portal_scripts_tree.color_item(item, color='#555555')

                        except (ValueError, TypeError):
                            pass

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

            # Hide 'Flame Max' column if every script reports 'Latest'
            _root = self.portal_scripts_tree.invisibleRootItem()
            _all_latest = all(
                _root.child(i).text(3) == 'Latest'
                for i in range(_root.childCount())
                if _root.child(i)
            )
            self.portal_scripts_tree.setColumnHidden(3, _all_latest)

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

        def update_installed_scripts_tree(search: str=''):
            """
            Update Installed Scripts Tree
            =============================

            Update the installed scripts tree with the scripts found in the shared script path.

            Args
            ----
                search (str, optional):
                    The search string to filter the scripts in the tree. If no search string is provided, all scripts are displayed.
                    (Default: '')
            """

            def add_script():
                """
                Add Script
                ==========

                Extract script metadata from docstring and add script to Installed Scripts tree.
                """

                def extract_docstring(file_path: str) -> str | None:
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

                def extract_metadata(docstring: str) -> Dict[str, str] | None:
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
                if docstring:
                    metadata = extract_metadata(docstring)
                else:
                    metadata = None

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

                assert isinstance(script_path, str)
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
                assert isinstance(script_path, str)
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

            # Download python script zip from Logik Portal, extract, and move to script install path.
            # Build the endpoint that returns a zip for the selected script.
            download_url = f'https://logik-portal.com/download.php?folder={script_name}'
            # Use a script-specific temp work directory so retries are clean.
            work_dir = os.path.join(self.temp_python_scripts_folder, script_name)
            # Save the downloaded archive in the temp work directory.
            zip_path = os.path.join(work_dir, f'{script_name}.zip')

            if os.path.exists(work_dir):
                shutil.rmtree(work_dir)
            os.makedirs(work_dir)

            pyflame.print(f'Downloading: {download_url}')
            try:
                with urllib.request.urlopen(download_url, timeout=600) as resp:
                    # Drive the progress UI from the server-reported payload size.
                    total_bytes = int(resp.headers.get('Content-Length', 0) or 0)
                    total_kb = max(1, total_bytes // 1024)

                    progress_window = PyFlameProgressWindow(
                        task=f'Downloading Python Script: {script_name}',
                        total_tasks=total_kb,
                        task_progress_message='{task}\n\n[{processing_task}kb of {total_tasks}kb] ({progress:.1f}%)',
                        title=f'{SCRIPT_NAME}: Downloading',
                        parent=self.window,
                        )

                    downloaded = 0
                    chunk_size = 1024 * 100
                    with open(zip_path, 'wb') as out_file:
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            progress_window.current_task = downloaded // 1024

                progress_window.tasks_completed(
                    title='Logik Portal: Download Complete',
                    text_append='Download Complete',
                    )
            except Exception as exc:
                shutil.rmtree(work_dir, ignore_errors=True)
                PyFlameMessageWindow(
                    title='Error',
                    message=f'Failed to download Python Script\n\n{exc}',
                    parent=self.window,
                    )
                return

            if not os.path.isfile(zip_path) or os.path.getsize(zip_path) == 0:
                shutil.rmtree(work_dir, ignore_errors=True)
                PyFlameMessageWindow(
                    title='Error',
                    message='Failed to download Python Script.\n\nThe Python script is missing or empty.',
                    parent=self.window,
                    )
                return

            pyflame.print(f'Downloaded: {zip_path}', text_color=TextColor.GREEN)

            try:
                pyflame.print(f'Extracting: {zip_path}')
                # Extract directly into work_dir so we can normalize layout after.
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(work_dir)
            except Exception as exc:
                shutil.rmtree(work_dir, ignore_errors=True)
                PyFlameMessageWindow(
                    title='Error',
                    message=f'Failed to extract Python Script archive\n\n{exc}',
                    parent=self.window,
                    )
                return
            finally:
                if os.path.exists(zip_path):
                    os.remove(zip_path)

            install_path = os.path.join(self.settings.script_install_path, script_name)
            print('Install Path: ', install_path)

            # Inspect extracted root to determine how archive is structured.
            entries = os.listdir(work_dir)
            if not entries:
                shutil.rmtree(work_dir, ignore_errors=True)
                PyFlameMessageWindow(
                    title='Error',
                    message='Failed to install Python Script.\n\nThe extracted archive was empty.',
                    parent=self.window,
                    )
                return

            entry_paths = [os.path.join(work_dir, entry) for entry in entries]

            # Archive may contain one top-level folder or loose files.
            if len(entries) == 1 and os.path.isdir(entry_paths[0]):
                # Typical package: archive contains one folder named after script.
                source_path = entry_paths[0]
                if os.path.exists(install_path):
                    shutil.rmtree(install_path)
                shutil.move(source_path, install_path)
                shutil.rmtree(work_dir, ignore_errors=True)
            else:
                # Fallback: archive has loose files at root; install that root folder.
                if os.path.exists(install_path):
                    shutil.rmtree(install_path)
                shutil.move(work_dir, install_path)

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

        def get_script_description() -> None:
            """
            Get Script Description
            ======================

            Get the description of the selected script from the python scripts tree.
            """

            check_script_flame_version(self.portal_scripts_tree)

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

        def submit_script():
            """
            Submit Script
            =============

            Submit Python script to Logik Portal.
            """

            pyflame.print('Redirecting to logik-portal.com for submission...')
            webbrowser.open('https://logik-portal.com/scripts/#submit')

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
            height=250,
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
            tooltip='Install a script saved locally to your computer, for example, a script you downloaded from the internet.',
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
        self.submit_script_button = PyFlameButton(
            text='Submit Script',
            connect=submit_script,
            )
        self.script_logik_portal_button = PyFlameButton(
            text='logik-portal.com',
            connect=self.logik_portal,
            )

        update_logik_portal_scripts_tree()
        update_installed_scripts_tree()

        # ==============================================================================
        # [Python Scripts Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_label, 0, 0, 1, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_tree, 1, 0, 7, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.delete_script_button, 8, 0)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.install_local_script_button, 8, 3)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_search_label, 9, 0)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.installed_scripts_search_entry, 9, 1, 1, 3)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_label, 0, 5, 1, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_tree, 1, 5, 7, 4)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.submit_script_button, 8, 5)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.install_script_button, 8, 8)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_search_label, 9, 5)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.portal_scripts_search_entry, 9, 6, 1, 3)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_install_path_label, 10, 5)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_install_path_browse, 10, 6, 1, 3)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_description_label, 12, 0, 1, 9)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_description_text_edit, 13, 0, 7, 9)

        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.script_logik_portal_button, 20, 0)
        self.tabs.tab_pages['Python Scripts'].grid_layout.addWidget(self.python_done_button, 20, 8)

        # ==============================================================================

        self.installed_scripts_search_entry.set_focus()

        check_script_flame_version(self.portal_scripts_tree)

    def matchbox_tab(self):

        def download_logik_collection() -> None:
            """
            Download Logik Matchbox Collection
            ================================

            Download Logik Matchbox Collection as a zip file, extract it, and delete the zip.
            """

            def save_config():

                # Save path to config file
                self.settings.save_config(
                    config_values={
                        'matchbox_path': matchbox_install_path
                        }
                    )

            def download(matchbox_install_path: str, system_password=''):
                """
                Download Logik Matchbox Collection from Logik Portal and install it to the destination path.

                Args
                ----
                    system_password: System password for sudo (if needed)
                """

                def remove_folder(path: str) -> bool:
                    """
                    Remove Folder
                    =============

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

                def move_matchboxes(source: str, destination: str) -> bool:
                    """
                    Move Folder
                    ===========

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
                    Flatten Directory
                    =================

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
                    title='Logik Portal: Matchbox',
                    total_tasks=2,
                    parent=self.window,
                    )

                # Initialize and display the text by setting processing_task
                progress_window.current_task = 1
                progress_window.text_append(f'Downloading Matchbox Collection...')

                pyflame.print('Downloading Matchbox Collection...', new_line=False)

                # Logik Portal Matchbox Collection Download URL
                zip_url = 'https://logik-portal.com/download_matchbox_all.php?source=app'

                # Temporary download path
                temp_download_path = os.path.join(self.temp_matchbox_folder, 'matchbox_all.zip')

                # Download Matchbox Collection to temporary download path
                with urllib.request.urlopen(zip_url, timeout=600) as resp, open(temp_download_path, 'wb') as out_file:
                    shutil.copyfileobj(resp, out_file)
                pyflame.print(f'Matchbox Collection Downloaded To: {temp_download_path}')

                # If file didn't download, give user error message and return
                if not os.path.exists(temp_download_path):
                    PyFlameMessageWindow(
                        title='Error',
                        message='Failed to download Matchbox Collection',
                        parent=self.window,
                        )
                    return

                progress_window.current_task = 2
                progress_window.text_append(f'Extracting Matchbox Collection...')

                pyflame.print('Extracting Matchbox Collection...', new_line=False)

                with zipfile.ZipFile(temp_download_path, 'r') as zip_ref:
                    zip_ref.extractall(self.temp_matchbox_folder)

                extracted_folder = os.path.join(self.temp_matchbox_folder, 'matchbox-main')
                logik_folder = os.path.join(self.temp_matchbox_folder, 'LOGIK')

                # Rename extracted folder to Logik
                os.rename(extracted_folder, logik_folder)
                pyflame.print('Matchbox Extraction Complete')

                # Delete the zip file
                os.remove(temp_download_path)
                pyflame.print(f'Deleted zip file: {temp_download_path}')

                # Logik install path
                logik_install_path = os.path.join(matchbox_install_path, 'LOGIK')

                # Always remove existing Logik folder in destination to ensure clean overwrite
                if os.path.exists(matchbox_install_path):
                    print(f'Removing existing Logik folder in destination: {logik_install_path}')
                    remove_folder(logik_install_path)

                pyflame.print('Moving Logik folder to destination...')
                # Move the Logik folder to destination (will use sudo if needed)
                move_matchboxes(logik_folder, logik_install_path)

                # Flatten the Logik folders and clean up
                flatten_directory(logik_install_path)

                progress_window.tasks_completed()
                progress_window.text_append(f'Matchbox Collection Installed')

            # Open file browser to select matchbox install location
            path = pyflame.file_browser(
                title='Select Logik Matchbox Install Directory',
                path=self.settings.matchbox_path,
                select_directory=True,
                window_to_hide=self.window
                )
            if path:
                matchbox_install_path = str(path)
            else:
                return

            # Save downloadpath to config file
            save_config()

            # Check if password is needed to install to selected location
            folder_write_permission = os.access(matchbox_install_path, os.W_OK)

            # If matchbox install path is not writeable, get system password and then download and install, otherwise just download and install
            if not folder_write_permission:
                print('Matchbox destination write permission: Not Writeable, need system password.')
                matchbox_password_window = PyFlamePasswordWindow(
                    text=f'System password needed to install Logik Matchboxes to selected location.',
                    parent=self.window,
                    )
                system_password = matchbox_password_window.password
                if system_password:
                    download(matchbox_install_path, system_password)
                else:
                    return
            else:
                print('Matchbox destination write permission: Writeable')
                download(matchbox_install_path)

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

            destination_folder = os.path.join(self.temp_matchbox_folder, selected_matchbox_name)
            print('Destination folder:', destination_folder)

            pyflame.print('Downloading matchbox from Logik Portal...')

            download_url = f'https://logik-portal.com/download_matchbox.php?folder={selected_matchbox_name}&source=app'

            with urllib.request.urlopen(download_url, timeout=300) as resp:
                zip_bytes = resp.read()

            with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_ref:
                zip_ref.extractall(self.temp_matchbox_folder)

            pyflame.print('Loading matchbox into batch...')

            # Get list of files in destination folder
            selected_matchbox_files = os.listdir(os.path.join(self.temp_matchbox_folder, selected_matchbox_name))

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

            PyFlameMessageWindow(
                title='Matchbox Added to Batch',
                message=f'Matchbox added to batch: {matchbox_file_name}',
                parent=self.window,
                )

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
                normalize_name=True,
                decode_unicode_escape=True,
                )

        def update_matchbox_tree(search: str='') -> None:
            """
            Update Matchbox Tree
            =====================

            Update matchbox tree with matchboxes from xml file.

            Args
            ----
                search (str):
                    String to search for in matchbox name. If search string is present, only add items that match the search string.
                    (Default: '')
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
            height=250,
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
        self.matchbox_logik_portal_button = PyFlameButton(
            text='logik-portal.com',
            connect=self.logik_portal,
            )

        update_matchbox_tree()

        # ==============================================================================
        # [Matchbox Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_logik_matchbox_collection_label, 0, 0, 1, 9)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_tree, 1, 0, 7, 9)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_add_to_batch, 8, 7)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_download_all_button, 8, 8)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_search_label, 9, 5)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_search_entry, 9, 6, 1, 3)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_desciption_label, 12, 0, 1, 9)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_text_edit, 13, 0, 7, 9)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_logik_portal_button, 20, 0)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_done_button, 20, 8)

    def batch_setups_tab(self):

        def get_batch_description() -> None:
            """
            Get Batch Description
            =====================

            Get selected batch setup description from json file and display in text edit.
            Also enables/disables the download button based on the required flame version.
            """

            self.get_json_description(
                label=self.batch_setups_desciption_label,
                label_text='Batch Setup Description',
                tree=self.batch_setups_tree,
                json_path=self.batch_setups_json_path,
                text_edit=self.batch_setups_text_edit,
                json_list_key='batch_setups',
                download_button=self.batch_setups_download_button,
                )

        def update_batch_setups_tree(search: str='') -> None:
            """
            Update Batch Setups Tree
            ========================

            Add batch setups to batch setups tree from xml file. If search string is present, only add items that match the search string.

            Args
            ----
                search (str):
                    String to search for in batch setup name. If search string is present, only add items that match the search string.
                    (Default: '')
            """


            def add_batch_setup(batch):
                flame_version = str(batch.get('flame_version', ''))
                artist_name = str(batch.get('submitter_name', ''))

                batch_setup = self.batch_setups_tree.add_item_with_columns([batch_name, flame_version, artist_name])

                # if batch setup requires newer version of flame grey out script entry
                try:
                    if float(self.flame_version) < float(flame_version):
                        self.batch_setups_tree.color_item(batch_setup, color='#555555')
                except ValueError:
                    pass

            pyflame.print('Updating Batch Setups List...', underline=True, new_line=False)

            # Clear batch setup tree
            self.batch_setups_tree.clear()

            # Read in batch setups from JSON
            with open(self.batch_setups_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            batches = data.get('batch_setups', []) if isinstance(data, dict) else data

            # Add items from JSON to batch setup tree. If search string is present, only add items that match the search string.
            if search:
                for batch in batches:
                    if batch.get('hidden'):
                        continue
                    batch_name = str(batch.get('name', ''))
                    if search.lower() in batch_name.lower():
                        add_batch_setup(batch)
            else:
                for batch in batches:
                    if batch.get('hidden'):
                        continue
                    batch_name = str(batch.get('name', ''))
                    add_batch_setup(batch)

            # Select top item in batch setup tree
            self.batch_setups_tree.setCurrentItem(self.batch_setups_tree.topLevelItem(0))

            # Get selected batch setup description
            get_batch_description()

            pyflame.print('Batch Setups List Updated', text_color=TextColor.GREEN)

        def check_batch_flame_version() -> None:
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
                setup_path = ''
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
                selected_batch_name = batch_item.text(0)

                # Look up slug from batch setups JSON. Display names don't always map
                # cleanly to slugs (case/punctuation differences), so look it up.
                batch_slug = selected_batch_name.replace(' ', '_')
                try:
                    with open(self.batch_setups_json_path, 'r', encoding='utf-8') as f:
                        batch_data = json.load(f)
                    batch_entries = batch_data.get('batch_setups', []) if isinstance(batch_data, dict) else batch_data
                    for entry in batch_entries:
                        if entry.get('name') == selected_batch_name:
                            batch_slug = entry.get('slug', batch_slug)
                            break
                except Exception as exc:
                    pyflame.print(f'Unable to read batch setups JSON: {exc}', print_type=PrintType.WARNING)

                # Use slug as the canonical name going forward. The extracted zip
                # contents are named after the slug, and open_batch() looks files
                # up by this name.
                batch_name = batch_slug

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

                # Download URL
                download_url = f'https://logik-portal.com/download_file.php?category=batch_setups&file={batch_slug}&source=web'

                # Download dest path
                zip_path = os.path.join(self.settings.batch_setup_download_path, batch_slug + '.zip')

                # Download zip file
                pyflame.print(f'Downloading: {download_url}')
                try:
                    with urllib.request.urlopen(download_url) as resp:
                        total_bytes = int(resp.headers.get('Content-Length', 0) or 0)
                        total_kb = max(1, total_bytes // 1024)

                        progress_window = PyFlameProgressWindow(
                            task=f'Downloading Batch Setup: {batch_slug}',
                            total_tasks=total_kb,
                            task_progress_message='{task}\n\n[{processing_task}kb of {total_tasks}kb] ({progress:.1f}%)',
                            title=f'{SCRIPT_NAME}: Downloading',
                            parent=self.window,
                            )

                        downloaded = 0
                        chunk_size = 1024 * 1024  # 1 MB increments for progress window to show progress.
                        with open(zip_path, 'wb') as out_file:
                            while True:
                                chunk = resp.read(chunk_size)
                                if not chunk:
                                    break
                                out_file.write(chunk)
                                downloaded += len(chunk)
                                progress_window.current_task = downloaded // 1024

                    progress_window.tasks_completed(
                        title='Logik Portal: Download Complete',
                        text_append='Download Complete',
                        )
                except Exception as exc:
                    PyFlameMessageWindow(
                        title='Error',
                        message=f'Failed to download Batch Setup:\n{exc}',
                        parent=self.window,
                        )
                    return
                pyflame.print(f'Downloaded: {zip_path}', text_color=TextColor.GREEN)

                # Uncompress zip file. Use try/finally so the partial zip is always
                # removed even when extraction fails.
                pyflame.print(f'Extracting: {zip_path}')
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(self.settings.batch_setup_download_path)
                    pyflame.print('Batch Setup Extraction Complete', text_color=TextColor.GREEN)
                except Exception as exc:
                    PyFlameMessageWindow(
                        title='Error',
                        message=f'Failed to extract Batch Setup archive:\n\n{exc}',
                        parent=self.window,
                        )
                    return
                finally:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)

                if self.open_batch_button.checked:
                    open_batch()

        def submit_batch_setup():
            """
            Submit Batch Setup
            ==================

            Submit batch setup to Logik Portal.

            Redirects to logik-portal.com for submission.
            """

            pyflame.print('Redirecting to logik-portal.com for submission...')
            webbrowser.open('https://logik-portal.com/batch_setups/#submit')

        def batch_setup_search():

            update_batch_setups_tree(search=self.batch_setups_search_entry.text)

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
            connect=get_batch_description,
            sort=True,
            height=250,
            )

        self.batch_setups_tree.setColumnWidth(0, 600)
        self.batch_setups_tree.setColumnWidth(1, 100)
        self.batch_setups_tree.setColumnWidth(2, 300)

        # Disable batch download button if current flame version older than batch minimum
        #self.batch_setups_tree.clicked.connect(check_batch_flame_version)

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
        self.batch_setups_logik_portal_button = PyFlameButton(
            text='logik-portal.com',
            connect=self.logik_portal,
            )

        # ==============================================================================
        # [Batch Setups Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_label, 0, 0, 1, 9)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_tree, 1, 0, 7, 9)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_submit_button, 8, 0)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.open_batch_button, 8, 7)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_download_button, 8, 8)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_search_label, 9, 5)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_search_entry, 9, 6, 1, 3)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_desciption_label, 12, 0, 1, 9)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_text_edit, 13, 0, 7, 9)

        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_setups_logik_portal_button, 20, 0)
        self.tabs.tab_pages['Batch Setups'].grid_layout.addWidget(self.batch_done_button, 20, 8)

        update_batch_setups_tree()
        check_batch_flame_version()

    def inference_nodes_tab(self):

        def get_inference_node_description():
            """
            Get Inference Node Description
            ==============================

            Get selected inference node description from json file and display in text edit.
            Also enables/disables the download button based on the required flame version.
            """

            self.get_json_description(
                label=self.inference_node_description_label,
                label_text='Inference Node Description',
                tree=self.inference_node_tree,
                json_path=self.inference_nodes_json_path,
                text_edit=self.inference_node_description_text_edit,
                json_list_key='inference',
                download_button=self.inference_node_download_button,
                )

        def update_inference_nodes_tree(search: str='') -> None:
            """
            Update Inference Node Tree
            ==========================

            Update inference node tree from json file. If search string is present, only add items that match the search string.

            Args
            ----
                search (str):
                    String to search for in inference node name. If search string is present, only add items that match the search string.
                    (Default: '')
            """

            def format_file_size(size_bytes) -> str:
                try:
                    size_bytes = int(size_bytes)
                except (TypeError, ValueError):
                    return ''
                size_mb = size_bytes // (1024 * 1024)
                return f'{size_mb} MB' if size_mb >= 1 else '< 1 MB'

            def add_inference_node(node):
                flame_version = str(node.get('flame_version', ''))
                inference_node_size = format_file_size(node.get('file_size'))

                inference_node = self.inference_node_tree.add_item_with_columns([inference_node_name, flame_version, inference_node_size])

                # if node requires newer version of flame grey out script entry
                try:
                    if float(self.flame_version) < float(flame_version):
                        self.inference_node_tree.color_item(inference_node, color='#555555')
                except ValueError:
                    pass

            pyflame.print('Updating Inference Node List...', underline=True, new_line=False)

            # Clear inference node tree.
            self.inference_node_tree.clear()

            # Read in inference nodes from JSON.
            with open(self.inference_nodes_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            nodes = data.get('inference', []) if isinstance(data, dict) else data

            # Add items from JSON to inference node tree. If search string is present, only add items that match the search string.
            if search:
                for node in nodes:
                    if node.get('hidden'):
                        continue
                    inference_node_name = str(node.get('name', ''))
                    if search.lower() in inference_node_name.lower():
                        add_inference_node(node)
            else:
                for node in nodes:
                    if node.get('hidden'):
                        continue
                    inference_node_name = str(node.get('name', ''))
                    add_inference_node(node)

            # Select top item in inference node tree.
            self.inference_node_tree.setCurrentItem(self.inference_node_tree.topLevelItem(0))

            # Get selected inference node description if inference node is selected.
            try:
                get_inference_node_description()
            except:
                print('Unable to get Inference Node description. No Inference Node selected\n')

            pyflame.print('Inference Node List Updated', text_color=TextColor.GREEN)

        def inference_node_download() -> None:
            """
            Inference Node Download
            ========================

            Download selected inference node from Logik Portal. Uncompress and add to batch if selected.
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

                    assert isinstance(inference_node_download_path, str)

                    # Get inference node path
                    inference_node_path = os.path.join(inference_node_download_path, inference_node_name + '.onnx')
                    if not os.path.isfile(inference_node_path):
                        inference_node_path = os.path.join(inference_node_download_path, inference_node_name + '.inf')

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

                assert isinstance(inference_node_download_path, str)

                # Get selected inference node name
                selected_node = self.inference_node_tree.selectedItems()
                selected_node_item = selected_node[0]
                selected_node_name = selected_node_item.text(0)

                # Look up slug from inference JSON. Display names don't always map
                # cleanly to slugs (case/punctuation differences), so look it up.
                inference_node_slug = selected_node_name.replace(' ', '_')
                try:
                    with open(self.inference_nodes_json_path, 'r', encoding='utf-8') as f:
                        inference_data = json.load(f)
                    inference_nodes = inference_data.get('inference', []) if isinstance(inference_data, dict) else inference_data
                    for node in inference_nodes:
                        if node.get('name') == selected_node_name:
                            inference_node_slug = node.get('slug', inference_node_slug)
                            break
                except Exception as exc:
                    pyflame.print(f'Unable to read inference JSON: {exc}', print_type=PrintType.WARNING)

                # Use slug as the canonical name going forward. The extracted zip
                # contents are named after the slug, and add_inference_node_to_batch
                # looks up files by this name.
                inference_node_name = inference_node_slug

                # Download URL
                download_url = f'https://logik-portal.com/download_file.php?category=inference&file={inference_node_slug}&source=app'

                # Download dest path
                zip_path = os.path.join(inference_node_download_path, inference_node_slug + '.zip')

                # Download zip file
                pyflame.print(f'Downloading: {download_url}')
                try:
                    with urllib.request.urlopen(download_url) as resp:
                        total_bytes = int(resp.headers.get('Content-Length', 0) or 0)
                        total_kb = max(1, total_bytes // 1024)

                        progress_window = PyFlameProgressWindow(
                            task=f'Downloading Inference Node: {inference_node_slug}',
                            total_tasks=total_kb,
                            task_progress_message='{task}\n\n[{processing_task}kb of {total_tasks}kb] ({progress:.1f}%)',
                            title=f'{SCRIPT_NAME}: Downloading',
                            parent=self.window,
                            )

                        downloaded = 0
                        chunk_size = 1024 * 1024  # 1 MB increments for progress window to show progress.
                        with open(zip_path, 'wb') as out_file:
                            while True:
                                chunk = resp.read(chunk_size)
                                if not chunk:
                                    break
                                out_file.write(chunk)
                                downloaded += len(chunk)
                                progress_window.current_task = downloaded // 1024

                    progress_window.tasks_completed(
                        title='Logik Portal: Download Complete',
                        text_append='Download Complete',
                        )
                except Exception as exc:
                    PyFlameMessageWindow(
                        title='Error',
                        message=f'Failed to download Inference Node:\n{exc}',
                        parent=self.window,
                        )
                    return
                pyflame.print(f'Downloaded: {zip_path}', text_color=TextColor.GREEN)

                # Uncompress zip file. Use try/finally so the partial zip is always
                # removed even when extraction fails.
                pyflame.print(f'Extracting: {zip_path}')
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(inference_node_download_path)
                    pyflame.print('Inference Node Extraction Complete', text_color=TextColor.GREEN)
                except Exception as exc:
                    PyFlameMessageWindow(
                        title='Error',
                        message=f'Failed to extract Inference Node archive:\n\n{exc}',
                        parent=self.window,
                        )
                    return
                finally:
                    if os.path.exists(zip_path):
                        os.remove(zip_path)

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
                assert isinstance(inference_node_download_path, str)
                save_config()
                download_node()
                pyflame.print('Inference Node Download Complete', text_color=TextColor.GREEN)

        def inference_node_submit() -> None:
            """
            Inference Node Submit
            =====================

            Submit inference node to Logik Portal.

            Redirects to logik-portal.com for submission.
            """

            pyflame.print('Redirecting to logik-portal.com for submission...')
            webbrowser.open('https://logik-portal.com/inference/#submit')

        def inference_node_search() -> None:
            """
            Inference Node Search
            =====================

            Search for inference nodes in the inference node tree. Update tree with search results as user types.
            """

            update_inference_nodes_tree(search=self.inference_node_search_entry.text)

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
            connect=get_inference_node_description,
            sort=True,
            elide_text=True,
            height=250,
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
        self.inference_node_logik_portal_button = PyFlameButton(
            text='logik-portal.com',
            connect=self.logik_portal,
            )

        # ==============================================================================
        # [Inference Nodes Tab Layout]
        # ==============================================================================

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_nodes_label, 0, 0, 1, 9)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_tree, 1, 0, 7, 9)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_submit_button, 8, 0)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_add_to_batch_pushbutton, 8, 7)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_download_button, 8, 8)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_search_label, 9, 5)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_search_entry, 9, 6, 1, 3)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_description_label, 12, 0, 1, 9)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_description_text_edit, 13, 0, 7, 9)

        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_logik_portal_button, 20, 0)
        self.tabs.tab_pages['Inference Nodes'].grid_layout.addWidget(self.inference_node_done_button, 20, 8)

        update_inference_nodes_tree()

    # ==============================================================================
    # [Common]
    # ==============================================================================

    def get_json_description(
        self,
        label,
        label_text,
        tree,
        json_path,
        text_edit,
        json_list_key=None,
        download_button=None,
        normalize_name=False,
        decode_unicode_escape=False,
        ):
        """
        Get Description
        ===============

        Get item description from a JSON file and show it in a text edit. Shared by the
        Matchbox, Inference Nodes, and Batch Setups tabs.

        Args
        ----
            label (PyFlameLabel):
                Label whose text is switched to `label_text` after rendering.

            label_text (str):
                Text to switch the label to (e.g. 'Matchbox Description').

            tree (PyFlameTreeWidget):
                Tree widget whose selected row drives the lookup.

            json_path (str):
                Path to the JSON file to read.

            text_edit (PyFlameTextEdit):
                Text edit widget to render the HTML description into.

            json_list_key (str | None):
                If set, pulls the item list from `data[json_list_key]`. If None,
                assumes the JSON root is already a list.
                (Default: None)

            download_button (PyFlameButton | None):
                If provided, its `enabled` state is set based on the selected row's
                flame version (column 1) vs `self.flame_version`.
                (Default: None)

            normalize_name (bool):
                If True, the selected row's name has spaces replaced with underscores
                before matching against the JSON `name` field. Needed for sources
                whose JSON `name` values are slug-style.
                (Default: False)

            decode_unicode_escape (bool):
                If True, decodes backslash-escape sequences (e.g. literal '\\n') in the
                description before rendering. Needed for sources whose descriptions
                contain literal escape sequences rather than real newlines. Can raise
                on descriptions containing bare backslashes, so leave off unless the
                source requires it.
                (Default: False)
        """

        selected_items = tree.selectedItems()
        if not selected_items:
            return

        item = selected_items[0]
        item_name = item.text(0)
        if normalize_name:
            item_name = item_name.replace(' ', '_')

        # Optionally gate the download button on flame version.
        if download_button is not None:
            item_version = item.text(1)
            try:
                download_button.enabled = float(item_version) <= float(self.flame_version)
            except ValueError:
                download_button.enabled = False

        with open(json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if json_list_key is not None and isinstance(data, dict):
            entries = data.get(json_list_key, [])
        else:
            entries = data

        for entry in entries:
            if entry.get('hidden'):
                continue
            if entry.get('name') != item_name:
                continue

            raw_description = entry.get('description', '')

            if decode_unicode_escape:
                # Convert escaped \n and \t into actual characters
                description = bytes(raw_description, 'utf-8').decode('unicode_escape')
            else:
                description = raw_description

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

            # Show in text edit
            text_edit.setReadOnly(True)
            text_edit.setHtml(html_text)
            break

        # Switch text edit label. This is named 'Logik Portal Updates' when the script first loads.
        label.text = label_text

    def logik_portal(self):
        """
        Logik Portal
        =============

        Open Logik Portal website in web browser.
        """

        pyflame.print('Redirecting to logik-portal.com...')
        webbrowser.open('https://logik-portal.com')

    def done(self):
        """
        Done
        ====

        Close the Logik Portal window.
        """

        # Get current tab name
        current_tab_name = self.tabs.get_current_tab_name()

        # Save current tab to config
        self.settings.save_config(
            config_values={
                'last_tab': current_tab_name,
                'script_install_path': self.script_install_path_browse.path
                }
            )

        self.window.close()

        try:
            shutil.rmtree(self.temp_folder)
            print('--> Clearing temp files.\n')
        except:
            pass

        print('Done.\n')

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
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
