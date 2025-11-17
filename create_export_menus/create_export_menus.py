# Create Export Menus
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
Script Name: Create Export Menus
Script Version: 5.4.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 03.29.20
Update Date: 07.14.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create custom right-click export menu's from saved export presets

URL:
    https://github.com/logik-portal/python/create_export_menus

Menus:

    To create or edit export menus:
        Flame Main Menu -> Logik Portal -> Logik Portal Script Setup -> Create Export Menus

    To access newly created menus:
        Right-click on clip -> Project Export Presets... -> Select export
        Right-click on clip -> Shared Export Presets... -> Select export

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v5.4.0 07.14.25
        - Updated to PyFlameLib v5.0.0.
        - Window layer order in linux is now fixed.

    v5.3.1 04.24.25
        - Hour token now gives 24 hour format.
        - Added new hour (12 Hour) token to give 12 hour format.

    v5.3.0 04.07.25
        - Updated to PyFlameLib v4.3.0.
        - Added confirmation window when overwriting an existing export menu.

    v5.2.0 01.15.25
        - Updated to PyFlameLib v4.1.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v5.1.0 08.24.24
        - Updated to PyFlameLib v3.

    v5.0.0 03.25.24
        - Major code cleanup.
        - Added subtitle export options to export presets.
        - Script now scans shared/project export preset subdirectories for saved export presets.

    v4.6.1 02.25.24
        - Misc UI Fixes.

    v4.6.0 01.21.24
        - Updated UI/PySide.
        - Fixed misc UI issues.
        - Fixed issue with Reveal in MediaHub/Finder buttons not updating in Edit tab.
        - Updated config file loading/saving.

    v4.5.0 09.03.23
        - Update to pyflame lib v2.0.0.
          *** The update to pyflame lib v2.0.0. will cause old script menus to not work. ***

    v4.4 04.20.23
        - Updated menus for Flame 2023.2+
        - Added 2024 preset version number.
        - Removed maximum version from preset menu template. This allows presets to be used with newer versions of Flame.

    v4.3 08.22.22
        - Added duplicate button to Edit tab - Duplicates selected preset

    v4.2 06.22.22
        - Messages print to Flame message window - Flame 2023.1 and later
        - Updated browser window for Flame 2023.1 and later
        - Setup window no longer closes after creating a new export preset
        - Menu template updated - With template importing new pyflame_lib module, error appears during flame startup when loading
          menu presets. There errors can be ignored. Errors might be due to order flame is loading modules. Menus work fine.

    v4.1 03.19.22
        - Moved UI widgets to external file
        - Added confirmation window when deleting an existing preset

    v4.0 03.02.22
        - Updated UI for Flame 2023
        - Code optimization
        - Misc bug fixes

    v3.7 01.03.22
        - Shared export menus now only work with the major version of Flame they're created with. This avoids errors when using
          a menu with a new version of Flame. For example a menu created with Flame 2022.2 will work with all versions
          of Flame 2022 but not 2021 or 2023. Shared export menus will now also only show up in versions of Flame that they will
          work with.
        - Added token for Tape Name to be used if clip has a clip name assigned

    v3.6 11.02.21
        - Fixed shot name token translation to work with python 3.7 in menu_template

    v3.5 10.13.21
        - Added button to reveal export path in MediaHub after export
        - Added button to reveal export path in finder after export
        - Export shared movie/file export presets not compatible with working version of Flame are not listed in list drop downs
        - Fixed: Exporting using time tokens would create additional folders if time changed during export
        - Removed leading zero from hour token if hour less than 10.
        - Added lower case ampm token
        - Shot name token improvements
        - Shot name token will now attempt to get assigned shot name from clip before guessing from clip name
        - Added SEQNAME token

    v3.4 05.21.21
        - Updated to be compatible with Flame 2022/Python 3.7

    v3.3 05.19.21
        - Edited menus now save properly
        - Shot name token fixed to handle clip names that start with numbers

    v3.2 02.15.21
        - Python hooks refresh after deleting a preset

    v3.1 01.19.21
        - Added ability to assign multiple exports to single right-click export menu
        - Added ability to edit/rename/delete existing export presets
        - When export is done Flame with switch to export destination in the Media Hub (Flame 2021.2 of higher only)

    v2.1 09.19.20
        - Updated UI
        - Added Shot Name token to export path token list - Shot Name derived from clip name
        - Added Sequence Name token to export path token list - Seq Name derived from Shot Name
        - Added Batch Group Name token to export path token list - Can only be used when exporting clips from batch groups
        - Added Batch Group Shot Name token to export path token list - Can only be used when exporting clips from batch groups
        - Saved project export presets can now be found if project is not saved in the default location
        - Duplicate preset names no longer allowed - duplicate preset names cause preset not to work

    v2.0 04.27.20
        - New UI
        - Tokens can be used to dynamically set the export path
        - Options to choose to export in foreground, export between marks, and export top layer
        - Menus can be saved so that they're visible in current project only and
          shared between all projects

    v1.1 04.05.20
        - Fixed: Config path
        - Fixed: Problem when checking for project presets to delete
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil
from functools import partial

import flame
from lib.pyflame_lib_create_export_menus import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Create Export Menus'
SCRIPT_VERSION = 'v5.4.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ExportMenuSetup:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Load config file
        self.settings = self.load_config()

        # Get current flame version values
        self.flame_version = pyflame.get_flame_version() # Get full flame version including point version.
        self.flame_min_max_version = str(self.flame_version)[:4] # Flame version to set min/max version in export presets. This is the whole number of the version. For example 2022.1 would be 2022.

        # Get current project name
        self.flame_project_name = flame.project.current_project.name

        # Create export preset menu folders if they don't exist. Saved export presets are stored in these folders.
        self.project_menus_dir, self.shared_menus_dir = self.create_menu_folders()

        # Paths
        self.menu_template_path = os.path.join(SCRIPT_PATH, 'assets/templates/menu_template') # Path to menu template used to create new export menus
        self.current_project_created_presets_path = os.path.join(SCRIPT_PATH, 'project_menus', self.flame_project_name) # Path to current project export preset menus folder
        self.project_preset_path = self.get_project_preset_path() # Path to current project export presets
        self.shared_preset_path = '/opt/Autodesk/shared/export/presets' # Path to shared export presets

        # Saved Flame Export Preset Paths
        self.project_movie_preset_path = os.path.join(self.project_preset_path, 'movie_file')
        self.project_file_seq_preset_path = os.path.join(self.project_preset_path, 'file_sequence')
        self.shared_movie_preset_path = os.path.join(self.shared_preset_path, 'movie_file')
        self.shared_file_seq_preset_path = os.path.join(self.shared_preset_path, 'file_sequence')

        # Get lists of saved export presets for project and shared presets
        self.get_saved_preset_lists()

        # Open Setup Window
        self.setup_window()

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
                'export_path': '/',
                'use_top_layer': False,
                'export_in_foreground': True,
                'export_between_marks': False,
                'reveal_in_mediahub': False,
                'reveal_in_finder': False,
                'include_subtitles': False,
                'subtitles_export_mode': 'Burn in Image',
                'subtitles_tracks': 'Current Subtitles Track',
                },
            )

        return settings

    def create_menu_folders(self) -> tuple:
            """
            Create Menu Folders
            ===================

            Create project and shared menu folders if they don't exist.
            Export presets are saved in these folders.

            Returns:
            --------
                project_menus_dir, shared_menus_dir (tuple):
                    project_menus_dir (str): Path to project export preset menus folder.
                    shared_menus_dir (str): Path to shared export preset menus folder
            """

            project_menus_dir = os.path.join(SCRIPT_PATH, 'project_menus')
            shared_menus_dir = os.path.join(SCRIPT_PATH, 'shared_menus')
            for folder in [project_menus_dir, shared_menus_dir]:
                if not os.path.isdir(folder):
                    os.makedirs(folder)

            return project_menus_dir, shared_menus_dir

    def get_project_preset_path(self) -> str:
        """
        Get Project Preset Path
        =======================

        Get path to current project export presets. If project not saved to default location get project path from project.db file.

        Returns:
        --------
            project_preset_path (str):
                Path to current project export presets

        Notes:
        ------
            Checking project path from project.db file will not work with Flame 2025+.
        """

        project_preset_path = f'/opt/Autodesk/project/{self.flame_project_name}/export/presets/flame' # Path to current project export presets

        # If path doesn't exist then project is may not be saved to default location. Try to get project path from project.db file. This doesn't work 2025+.
        if not os.path.isdir(project_preset_path):
            try:
                project_values = open('/opt/Autodesk/project/project.db', 'r')
                values = project_values.read().splitlines()
                project_values.close()
                project_line = [line for line in values if 'Project:' + self.flame_project_name in line][0]
                project_line = project_line.split('SetupDir="', 1)[1]
                project_line = project_line.split('"', 1)[0]
                project_preset_path = os.path.join(project_line, 'export/presets/flame')
            except:
                pass

        return project_preset_path

    def get_saved_preset_lists(self) -> None:
        """
        Get Saved Preset Lists
        ======================

        Get lists of saved export presets for project and shared presets.
        """

        def get_compatible_preset_list(preset_path) -> list:
            """
            Get Compatible Preset List
            ==========================

            Get list of shared export presets that are compatible with current version of flame.

            Args:
            -----
                preset_path (str):
                    Path to export presets to check.

            Returns:
            --------
                compatible_preset_list (list):
                    List of export presets compatible with current version of flame.
                Or empty list if no presets found.
            """

            def check_preset_version(path) -> bool:
                """
                Check Preset Version
                ====================

                Check export presets for flame version compatibility.

                If preset version is less than or equal to current export version then return True to add preset to list. Otherwise return False.

                current_export_version (str): Export version of preset at preset_path.
                export_version (str): Current export version of flame.

                Args:
                -----
                    path (str):
                        Path to export preset.

                Returns:
                --------
                    bool: True if preset is compatible with current version of flame. False if not.
                """

                current_export_version, export_version = pyflame.get_export_preset_version(path)

                # If preset version is less than or equal to current export version then return True to add preset to list. Otherwise return False.
                if current_export_version <= export_version:
                    return True
                return False

            try:
                compatible_preset_list = [] # List of export presets compatible with current version of flame
                preset_list = [] # List of all export presets in preset_path

                # Walk through the directory and get the xml files
                for root, dirs, files in os.walk(preset_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file) # Get full path to xml file
                            file = file_path.rsplit(preset_path + '/', 1)[1] # Remove preset path from file path
                            preset_list.append(file)
                #print('preset_list:', preset_list, '\n')

                # Check each preset for compatibility with current version of flame
                for preset in preset_list:
                    path = os.path.join(preset_path, preset)
                    if check_preset_version(path):
                        compatible_preset_list.append(preset[:-4])
                compatible_preset_list = sorted(compatible_preset_list)
                return compatible_preset_list # Return list of export presets compatible with current version of flame
            except:
                return [] # Return empty list if no presets found

        # Get saved export preset lists
        self.project_movie_preset_list = get_compatible_preset_list(self.project_movie_preset_path)
        self.project_file_seq_preset_list = get_compatible_preset_list(self.project_file_seq_preset_path)
        self.shared_movie_preset_list = get_compatible_preset_list(self.shared_movie_preset_path)
        self.shared_file_seq_preset_list = get_compatible_preset_list(self.shared_file_seq_preset_path)

        print('\nSaved Export Presets:\n')

        self.print_list('Project Movie Preset List', self.project_movie_preset_list)
        self.print_list('Project File Seq Preset List', self.project_file_seq_preset_list)
        self.print_list('Shared Movie Preset List', self.shared_movie_preset_list)
        self.print_list('Shared File Seq Preset List', self.shared_file_seq_preset_list)

    def print_list(self, list_name, list) -> None:
        """
        Print list
        ==========

        Print list of items to terminal.

        Args:
        -----
            list_name (str):
                List name.
            list (list):
                List of items.
        """

        print(f'    {list_name}:')
        if list:
            for x in list:
                print(f'        {x}')
        else:
            print('        None found')
        print('\n')

    #-------------------------------------

    def setup_window(self) -> None:

        def export_preset_tab(
            tab,
            tab_number,
            export_path,
            top_layer,
            export_foreground,
            export_between_marks,
            include_subtitles,
            subtitles_export_mode,
            subtitles_tracks,
            ) -> tuple:

            """
            Export Preset Tab
            =================

            Create the export preset tab layout.

            Args:
            -----
                tab (PyFlameTabWidget.TabContainer):
                    The tab to create the layout in.
                tab_number (str):
                    The tab number.
                export_path (str):
                    The export path.
                top_layer (bool):
                    Set state of top layer pushbutton.
                export_foreground (bool):
                    Set state of export foreground pushbutton.
                export_between_marks (bool):
                    Set state of export between marks pushbutton.
                include_subtitles (bool):
                    Set state of include_subtitles pushbutton.
                subtitles_export_mode (str):
                    Button text.
                subtitles_tracks (str):
                    Button text.

            Returns:
            --------
                tuple:
                    UI elements for the tab.
            """

            def set_preset_menu() -> None:
                """
                Update the saved presets pushbutton menu based on the saved preset type pushbutton menu selection.

                Args:
                -----
                    saved_preset_type_menu (PyFlameMenu):
                        The saved preset type pushbutton menu.
                    saved_presets_menu (PyFlameMenu):
                        The saved presets pushbutton menu.
                """

                def get_menu_text(preset_file_list) -> str:
                    """
                    Get the first preset in the list to set the pushbutton text.
                    If no presets are found, return 'No Saved Presets Found'

                    Args:
                    -----
                        preset_file_list (list):
                            List of preset files.

                    Returns:
                    --------
                        str: The first preset in the list or 'No Saved Presets Found'
                    """

                    if not preset_file_list:
                        return 'No Saved Presets Found'
                    else:
                        return preset_file_list[0]

                if saved_preset_type_menu.text == 'Project: Movie':
                    saved_presets_menu.update_menu(
                        text=get_menu_text(self.project_movie_preset_list),
                        menu_options=self.project_movie_preset_list,
                        )
                elif saved_preset_type_menu.text == 'Project: File Sequence':
                    saved_presets_menu.update_menu(
                        text=get_menu_text(self.project_file_seq_preset_list),
                        menu_options=self.project_file_seq_preset_list,
                        )
                elif saved_preset_type_menu.text == 'Shared: Movie':
                    saved_presets_menu.update_menu(
                        text=get_menu_text(self.shared_movie_preset_list),
                        menu_options=self.shared_movie_preset_list,
                        )
                elif saved_preset_type_menu.text == 'Shared: File Sequence':
                    saved_presets_menu.update_menu(
                        text=get_menu_text(self.shared_file_seq_preset_list),
                        menu_options=self.shared_file_seq_preset_list,
                        )

            def toggle_ui() -> None:
                """
                Toggle UI
                =========

                Enable/Disable UI elements based on the state of the enable preset pushbutton.
                """

                if enable_preset_pushbutton.text:
                    switch = True
                else:
                    switch = False

                saved_preset_type_label.enabled = switch
                saved_presets_label.enabled = switch
                export_path_label.enabled = switch
                export_path_entry.enabled = switch
                top_layer_pushbutton.enabled = switch
                foreground_pushbutton.enabled = switch
                between_marks_pushbutton.enabled = switch
                token_pushbutton.enabled = switch
                saved_preset_type_menu.enabled = switch
                server_browse_button.enabled = switch
                saved_presets_menu.enabled = switch
                include_subtitles_pushbutton.enabled = switch
                subtitles_export_mode_menu.enabled = switch
                subtitles_tracks_menu.enabled = switch

            def subtitles_ui_toggle() -> None:
                """
                Subtitles UI Toggle
                ===================

                Enable or disable subtitle buttons/menus

                If version of Flame is older than 2024.2 all buttons/menus are disabled.
                Subtitles were added in 2024.2.
                """

                if self.flame_version < 2024.2:
                    include_subtitles_pushbutton.enabled = False
                    subtitles_export_mode_menu.enabled = False
                    subtitles_tracks_menu.enabled = False
                    pyflame.print('Subtitle options disabled. Not compatible with current version of Flame.')

                if include_subtitles_pushbutton.text:
                    subtitles_export_mode_menu.enabled = True
                    subtitles_tracks_menu.enabled = True
                else:
                    subtitles_export_mode_menu.enabled = False
                    subtitles_tracks_menu.enabled = False

            # Labels
            saved_preset_type_label = PyFlameLabel(
                text='Saved Preset Type',
                )
            saved_presets_label = PyFlameLabel(
                text='Saved Presets',
                )
            export_path_label = PyFlameLabel(
                text='Export Path',
                )
            subtitles_label = PyFlameLabel(
                text='Subtitles',
                style=Style.UNDERLINE,
                )

            # Entries
            export_path_entry = PyFlameEntry(
                text=export_path,
                )

            # Pushbuttons
            if tab_number != 'one':
                enable_preset_pushbutton = PyFlamePushButton(
                    text='Enable Preset',
                    checked=False,
                    connect=toggle_ui,
                    )
            else:
                enable_preset_pushbutton = None

            top_layer_pushbutton = PyFlamePushButton(
                text='Use Top Layer',
                checked=top_layer,
                )
            foreground_pushbutton = PyFlamePushButton(
                text='Foreground Export',
                checked=export_foreground,
                )
            between_marks_pushbutton = PyFlamePushButton(
                text='Export Between Marks',
                checked=export_between_marks,
                )
            include_subtitles_pushbutton = PyFlamePushButton(
                text='Include Subtitles',
                checked=include_subtitles,
                connect=subtitles_ui_toggle,
                )

            # Token Pushbutton
            token_pushbutton = PyFlameTokenMenu(
                text='Add Token',
                token_dict={
                    'Project Name': '<ProjectName>',
                    'Project Nick Name': '<ProjectNickName>',
                    'Shot Name': '<ShotName>',
                    'SEQUENCE NAME': '<SEQNAME>',
                    'Sequence Name': '<SeqName>',
                    'Tape Name': '<TapeName>',
                    'User Name': '<UserName>',
                    'User Nickname': '<UserNickName>',
                    'Clip Name': '<ClipName>',
                    'Clip Resolution': '<Resolution>',
                    'Clip Height': '<ClipHeight>',
                    'Clip Width': '<ClipWidth>',
                    'Year (YYYY)': '<YYYY>',
                    'Year (YY)': '<YY>',
                    'Month': '<MM>',
                    'Day': '<DD>',
                    'Hour (24 Hour)': '<Hour>',
                    'Hour (12 Hour)': '<hour>',
                    'Minute': '<Minute>',
                    'AM/PM': '<AMPM>',
                    'am/pm': '<ampm>',
                    },
                token_dest=export_path_entry,
                )

            # Pushbutton Menus
            saved_presets_menu = PyFlameMenu(
                text='',
                menu_options=[],
                )
            saved_preset_type_menu = PyFlameMenu(
                text='Project: Movie',
                menu_options=[
                    'Project: Movie',
                    'Project: File Sequence',
                    'Shared: Movie',
                    'Shared: File Sequence',
                    ],
                connect=set_preset_menu,
                )

            def subtitles_update_tracks_menu() -> None:
                """
                Switch Subtitles Tracks Menu based on selection in Subtitles Export Mode Menu
                """

                if subtitles_export_mode_menu.text == 'Burn in Image':
                    subtitles_tracks_menu.update_menu(
                        text='Current Subtitles Track',
                        menu_options=[
                            'Current Subtitles Track',
                            ],
                        )

                elif subtitles_export_mode_menu.text == 'Export as Files':
                    subtitles_tracks_menu.update_menu(
                        text='Current Subtitles Track',
                        menu_options=[
                            'Current Subtitles Track',
                            'All Subtitles Tracks',
                            ]
                        )

            subtitles_export_mode_menu = PyFlameMenu(
                text =subtitles_export_mode,
                menu_options = [
                    'Burn in Image',
                    'Export as Files',
                    ],
                connect=subtitles_update_tracks_menu,
                enabled=False,
                )
            subtitles_tracks_menu = PyFlameMenu(
                text=subtitles_tracks,
                menu_options=[],
                enabled=False,
                )


            if self.flame_version < 2024.2:
                subtitles_label.setVisible(False)
                include_subtitles_pushbutton.setVisible(False)
                subtitles_export_mode_menu.setVisible(False)
                subtitles_tracks_menu.setVisible(False)

            # Set saved preset type pushbutton menu when tab is created
            set_preset_menu()

            # Buttons
            server_browse_button = PyFlameButton(
                text='Browse',
                connect=partial(self.directory_path_browse, export_path_entry, [self.window]),
                )

            # Toggle UI
            try:
                toggle_ui()
            except:
                pass

            subtitles_update_tracks_menu()

            #-------------------------------------
            # [Tab Layout]
            #-------------------------------------

            tab.grid_layout.addWidget(saved_preset_type_label, 1, 0)
            tab.grid_layout.addWidget(saved_preset_type_menu, 1, 1, 1, 2)

            tab.grid_layout.addWidget(saved_presets_label, 2, 0)
            tab.grid_layout.addWidget(saved_presets_menu, 2, 1, 1, 3)

            tab.grid_layout.addWidget(export_path_label, 3, 0)
            tab.grid_layout.addWidget(export_path_entry, 3, 1, 1, 3)
            tab.grid_layout.addWidget(server_browse_button, 3, 4)
            tab.grid_layout.addWidget(token_pushbutton, 3, 5)

            if tab_number != 'one':
                tab.grid_layout.addWidget(enable_preset_pushbutton, 0, 7)
            tab.grid_layout.addWidget(top_layer_pushbutton, 1, 7)
            tab.grid_layout.addWidget(foreground_pushbutton, 2, 7)
            tab.grid_layout.addWidget(between_marks_pushbutton, 3, 7)

            tab.grid_layout.addWidget(subtitles_label, 0, 8)
            tab.grid_layout.addWidget(include_subtitles_pushbutton, 1, 8)
            tab.grid_layout.addWidget(subtitles_export_mode_menu, 2, 8)
            tab.grid_layout.addWidget(subtitles_tracks_menu, 3, 8)

            return saved_preset_type_menu, saved_presets_menu, export_path_entry, enable_preset_pushbutton, top_layer_pushbutton, foreground_pushbutton, between_marks_pushbutton, saved_preset_type_label, saved_presets_label, export_path_label, server_browse_button, token_pushbutton, include_subtitles_pushbutton, subtitles_export_mode_menu, subtitles_tracks_menu

        def create_tab() -> None:
            """
            Create Tab
            ==========

            Tab for creating export presets.
            """

            def build_preset_tabs() -> None:
                """
                Create export preset tabs 1-5 using the export_preset_tab as a template.
                """

                self.create_preset_tabs = PyFlameTabWidget(
                    tab_names=[
                        'Export Preset One',
                        'Export Preset Two',
                        'Export Preset Three',
                        'Export Preset Four',
                        'Export Preset Five',
                        ],
                    grid_layout_columns=9,
                    grid_layout_rows=5,
                    )

                # Create tabs
                export_preset_one_tab = export_preset_tab(tab=self.create_preset_tabs.tab_pages['Export Preset One'],
                                                          tab_number='one',
                                                          export_path=self.settings.export_path,
                                                          top_layer=self.settings.use_top_layer,
                                                          export_foreground=self.settings.export_in_foreground,
                                                          export_between_marks=self.settings.export_between_marks,
                                                          include_subtitles=self.settings.include_subtitles,
                                                          subtitles_export_mode=self.settings.subtitles_export_mode,
                                                          subtitles_tracks=self.settings.subtitles_tracks,
                                                          )
                export_preset_two_tab = export_preset_tab(tab=self.create_preset_tabs.tab_pages['Export Preset Two'],
                                                          tab_number='two',
                                                          export_path='',
                                                          top_layer=False,
                                                          export_foreground=False,
                                                          export_between_marks=False,
                                                          include_subtitles=False,
                                                          subtitles_export_mode='Burn in Image',
                                                          subtitles_tracks='Current Subtitles Track',
                                                          )
                export_preset_three_tab = export_preset_tab(tab=self.create_preset_tabs.tab_pages['Export Preset Three'],
                                                            tab_number='three',
                                                            export_path='',
                                                            top_layer=False,
                                                            export_foreground=False,
                                                            export_between_marks=False,
                                                            include_subtitles=False,
                                                            subtitles_export_mode='Burn in Image',
                                                            subtitles_tracks='Current Subtitles Track',
                                                            )
                export_preset_four_tab = export_preset_tab(tab=self.create_preset_tabs.tab_pages['Export Preset Four'],
                                                           tab_number='four',
                                                           export_path='',
                                                           top_layer=False,
                                                           export_foreground=False,
                                                           export_between_marks=False,
                                                           include_subtitles=False,
                                                           subtitles_export_mode='Burn in Image',
                                                           subtitles_tracks='Current Subtitles Track',
                                                           )
                export_preset_five_tab = export_preset_tab(tab=self.create_preset_tabs.tab_pages['Export Preset Five'],
                                                           tab_number='five',
                                                           export_path='',
                                                           top_layer=False,
                                                           export_foreground=False,
                                                           export_between_marks=False,
                                                           include_subtitles=False,
                                                           subtitles_export_mode='Burn in Image',
                                                           subtitles_tracks='Current Subtitles Track',
                                                           )

                # Get values from tabs
                self.preset_type_menu_01, self.presets_menu_01, self.export_path_entry_01, self.enable_preset_pushbutton_01, self.top_layer_pushbutton_01, self.foreground_pushbutton_01, self.between_marks_pushbutton_01, self.saved_preset_type_label_01, self.saved_presets_label_01, self.export_path_label_01, self.server_browse_button_01, self.token_push_button_01, self.include_subtitles_pushbutton_01, self.subtitles_export_mode_menu_01, self.subtitles_tracks_menu_01 = export_preset_one_tab
                self.preset_type_menu_02, self.presets_menu_02, self.export_path_entry_02, self.enable_preset_pushbutton_02, self.top_layer_pushbutton_02, self.foreground_pushbutton_02, self.between_marks_pushbutton_02, self.saved_preset_type_label_02, self.saved_presets_label_02, self.export_path_label_02, self.server_browse_button_02, self.token_push_button_02, self.include_subtitles_pushbutton_02, self.subtitles_export_mode_menu_02, self.subtitles_tracks_menu_02 = export_preset_two_tab
                self.preset_type_menu_03, self.presets_menu_03, self.export_path_entry_03, self.enable_preset_pushbutton_03, self.top_layer_pushbutton_03, self.foreground_pushbutton_03, self.between_marks_pushbutton_03, self.saved_preset_type_label_03, self.saved_presets_label_03, self.export_path_label_03, self.server_browse_button_03, self.token_push_button_03, self.include_subtitles_pushbutton_03, self.subtitles_export_mode_menu_03, self.subtitles_tracks_menu_03 = export_preset_three_tab
                self.preset_type_menu_04, self.presets_menu_04, self.export_path_entry_04, self.enable_preset_pushbutton_04, self.top_layer_pushbutton_04, self.foreground_pushbutton_04, self.between_marks_pushbutton_04, self.saved_preset_type_label_04, self.saved_presets_label_04, self.export_path_label_04, self.server_browse_button_04, self.token_push_button_04, self.include_subtitles_pushbutton_04, self.subtitles_export_mode_menu_04, self.subtitles_tracks_menu_04 = export_preset_four_tab
                self.preset_type_menu_05, self.presets_menu_05, self.export_path_entry_05, self.enable_preset_pushbutton_05, self.top_layer_pushbutton_05, self.foreground_pushbutton_05, self.between_marks_pushbutton_05, self.saved_preset_type_label_05, self.saved_presets_label_05, self.export_path_label_05, self.server_browse_button_05, self.token_push_button_05, self.include_subtitles_pushbutton_05, self.subtitles_export_mode_menu_05, self.subtitles_tracks_menu_05 = export_preset_five_tab

            # Labels
            self.menu_visibility_label = PyFlameLabel(
                text='Menu Visibility',
                )
            self.menu_name_label = PyFlameLabel(
                text='Menu Name',
                )
            self.current_preset_label = PyFlameLabel(
                text='Current Preset',
                )
            self.after_export_label = PyFlameLabel(
                text='After Export',
                align=Align.CENTER,
                style=Style.UNDERLINE,
                )

            # Entries
            self.menu_name_entry = PyFlameEntry(
                text='',
                )

            # Menu
            self.menu_visibility_menu = PyFlameMenu(
                text='Project',
                menu_options=[
                    'Project',
                    'Shared',
                    ],
                )

            # Push Buttons
            self.reveal_in_mediahub_pushbutton = PyFlamePushButton(
                text='Reveal in Mediahub',
                checked=self.settings.reveal_in_mediahub,
                )
            self.reveal_in_finder_pushbutton = PyFlamePushButton(
                text='Reveal in Finder',
                checked=self.settings.reveal_in_finder,
                )

            # Buttons

            def create_button_connect() -> None:
                """
                Connect create button to save_menus function.
                """

                self.save_menus('Create')

            self.create_button = PyFlameButton(
                text='Create',
                connect=create_button_connect,
                color=Color.BLUE,
                )

            self.done_button = PyFlameButton(
                text='Done',
                connect=self.window.close,
                )

            # Lines
            horizontal_line_01 = PyFlameHorizontalLine()
            horizontal_line_02 = PyFlameHorizontalLine()

            # Create export preset tabs 1-5
            build_preset_tabs()

            #-------------------------------------
            # [Create Tab Layout]
            #-------------------------------------

            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.menu_name_label, 1, 0)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.menu_name_entry, 1, 1, 1, 3)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.menu_visibility_label, 2, 0)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.menu_visibility_menu, 2, 1)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.after_export_label, 0, 8)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.reveal_in_finder_pushbutton, 1, 8)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.reveal_in_mediahub_pushbutton, 2, 8)

            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(horizontal_line_01, 4, 0, 1, 9)

            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.create_preset_tabs, 5, 0, 4, 9)

            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(horizontal_line_02, 9, 0, 1, 9)

            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.done_button, 10, 7)
            self.main_tabs.tab_pages['Create'].grid_layout.addWidget(self.create_button, 10, 8)

        def edit_tab() -> None:
            """
            Edit Tab
            ========

            Tab for editing export presets.
            """

            def build_edit_preset_tabs():
                """
                Build Edit Export Preset Tabs
                =============================

                Create edit export preset tabs 1-5 using the export_preset_tab as a template.
                """

                self.edit_preset_tabs = PyFlameTabWidget(
                    tab_names=[
                        'Export Preset One',
                        'Export Preset Two',
                        'Export Preset Three',
                        'Export Preset Four',
                        'Export Preset Five',
                        ],
                    grid_layout_columns=9,
                    grid_layout_rows=5,
                    )

                self.edit_presets_tab1 = self.edit_preset_tabs.add_tab('Export Preset One')
                self.edit_presets_tab2 = self.edit_preset_tabs.add_tab('Export Preset Two')
                self.edit_presets_tab3 = self.edit_preset_tabs.add_tab('Export Preset Three')
                self.edit_presets_tab4 = self.edit_preset_tabs.add_tab('Export Preset Four')
                self.edit_presets_tab5 = self.edit_preset_tabs.add_tab('Export Preset Five')

                # Create tabs
                edit_preset_one_tab = export_preset_tab(tab=self.edit_presets_tab1,
                                                        tab_number='one',
                                                        export_path=self.settings.export_path,
                                                        top_layer=self.settings.use_top_layer,
                                                        export_foreground=self.settings.export_in_foreground,
                                                        export_between_marks=self.settings.export_between_marks,
                                                        include_subtitles=self.settings.include_subtitles,
                                                        subtitles_export_mode=self.settings.subtitles_export_mode,
                                                        subtitles_tracks=self.settings.subtitles_tracks,
                                                        )
                edit_preset_two_tab = export_preset_tab(tab=self.edit_presets_tab2,
                                                        tab_number='two',
                                                        export_path='',
                                                        top_layer=False,
                                                        export_foreground=False,
                                                        export_between_marks=False,
                                                        include_subtitles=False,
                                                        subtitles_export_mode='Burn in Image',
                                                        subtitles_tracks='Current Subtitles Track',
                                                        )
                edit_preset_three_tab = export_preset_tab(tab=self.edit_presets_tab3,
                                                          tab_number='three',
                                                          export_path='',
                                                          top_layer=False,
                                                          export_foreground=False,
                                                          export_between_marks=False,
                                                          include_subtitles=False,
                                                          subtitles_export_mode='Burn in Image',
                                                          subtitles_tracks='Current Subtitles Track',
                                                          )
                edit_preset_four_tab = export_preset_tab(tab=self.edit_presets_tab4,
                                                         tab_number='four',
                                                         export_path='',
                                                         top_layer=False,
                                                         export_foreground=False,
                                                         export_between_marks=False,
                                                         include_subtitles=False,
                                                         subtitles_export_mode='Burn in Image',
                                                         subtitles_tracks='Current Subtitles Track',
                                                         )
                edit_preset_five_tab = export_preset_tab(tab=self.edit_presets_tab5,
                                                         tab_number='five',
                                                         export_path='',
                                                         top_layer=False,
                                                         export_foreground=False,
                                                         export_between_marks=False,
                                                         include_subtitles=False,
                                                         subtitles_export_mode='Burn in Image',
                                                         subtitles_tracks='Current Subtitles Track',
                                                         )

                # Get values from tabs
                self.edit_preset_type_menu_01, self.edit_presets_menu_01, self.edit_export_path_entry_01, self.edit_enable_preset_pushbutton_01, self.edit_top_layer_pushbutton_01, self.edit_foreground_pushbutton_01, self.edit_between_marks_pushbutton_01, self.edit_saved_preset_type_label_01, self.edit_saved_presets_label_01, self.edit_export_path_label_01, self.edit_server_browse_button_01, self.edit_token_pushbutton_01, self.edit_include_subtitles_pushbutton_01, self.edit_subtitles_export_mode_menu_01, self.edit_subtitles_tracks_menu_01 = edit_preset_one_tab
                self.edit_preset_type_menu_02, self.edit_presets_menu_02, self.edit_export_path_entry_02, self.edit_enable_preset_pushbutton_02, self.edit_top_layer_pushbutton_02, self.edit_foreground_pushbutton_02, self.edit_between_marks_pushbutton_02, self.edit_saved_preset_type_label_02, self.edit_saved_presets_label_02, self.edit_export_path_label_02, self.edit_server_browse_button_02, self.edit_token_pushbutton_02, self.edit_include_subtitles_pushbutton_02, self.edit_subtitles_export_mode_menu_02, self.edit_subtitles_tracks_menu_02 = edit_preset_two_tab
                self.edit_preset_type_menu_03, self.edit_presets_menu_03, self.edit_export_path_entry_03, self.edit_enable_preset_pushbutton_03, self.edit_top_layer_pushbutton_03, self.edit_foreground_pushbutton_03, self.edit_between_marks_pushbutton_03, self.edit_saved_preset_type_label_03, self.edit_saved_presets_label_03, self.edit_export_path_label_03, self.edit_server_browse_button_03, self.edit_token_pushbutton_03, self.edit_include_subtitles_pushbutton_03, self.edit_subtitles_export_mode_menu_03, self.edit_subtitles_tracks_menu_03 = edit_preset_three_tab
                self.edit_preset_type_menu_04, self.edit_presets_menu_04, self.edit_export_path_entry_04, self.edit_enable_preset_pushbutton_04, self.edit_top_layer_pushbutton_04, self.edit_foreground_pushbutton_04, self.edit_between_marks_pushbutton_04, self.edit_saved_preset_type_label_04, self.edit_saved_presets_label_04, self.edit_export_path_label_04, self.edit_server_browse_button_04, self.edit_token_pushbutton_04, self.edit_include_subtitles_pushbutton_04, self.edit_subtitles_export_mode_menu_04, self.edit_subtitles_tracks_menu_04 = edit_preset_four_tab
                self.edit_preset_type_menu_05, self.edit_presets_menu_05, self.edit_export_path_entry_05, self.edit_enable_preset_pushbutton_05, self.edit_top_layer_pushbutton_05, self.edit_foreground_pushbutton_05, self.edit_between_marks_pushbutton_05, self.edit_saved_preset_type_label_05, self.edit_saved_presets_label_05, self.edit_export_path_label_05, self.edit_server_browse_button_05, self.edit_token_pushbutton_05, self.edit_include_subtitles_pushbutton_05, self.edit_subtitles_export_mode_menu_05, self.edit_subtitles_tracks_menu_05 = edit_preset_five_tab

            def delete_export_menu() -> None:
                """
                Delete export menu currently selected in the edit_saved_export_menu_menu.
                """

                # Get name of menu to delete from pushbutton text
                menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]

                # Confirm delete
                if PyFlameMessageWindow(
                    message=f'Delete preset: {menu_name}?',
                    message_type=MessageType.WARNING,
                    title=f'{SCRIPT_NAME}: Confirm Operation',
                    parent=None,
                    ):

                    # Get menu path
                    if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                        menu_path = os.path.join(self.shared_menus_dir, menu_name)
                    else:
                        menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, menu_name)
                    #print('Menu path:', menu_path, '\n')

                    # Delete menu files
                    os.remove(menu_path + '.py')
                    try:
                        os.remove(menu_path + '.pyc')
                    except:
                        pass

                    pyflame.print(f'Menu deleted: {menu_name}')

                    # Reload button menus
                    self.get_saved_menus()

                    # Refresh python hooks
                    pyflame.refresh_hooks()

            def duplicate_preset() -> None:
                """
                Duplicate export menu currently selected in the Export Menus pushbutton menu.
                """

                # Get name of menu to duplicate from pushbutton text
                menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]
                #print('Menu to duplicate:', menu_name)

                # Get menu path
                if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                    menu_path = os.path.join(self.shared_menus_dir, menu_name) + '.py'
                    menu_prefix = 'Shared: '
                else:
                    menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, menu_name) + '.py'
                    menu_prefix = 'Project: '
                #print('Existing menu path:', menu_path)

                # Add 'copy' to menu name and check for existing file. If exists, add ' copy' until unique name is found.
                new_menu_path = menu_path[:-3] + ' copy.py'
                while os.path.exists(new_menu_path):
                    new_menu_path = new_menu_path[:-3] + ' copy.py'
                #print('New menu path:', new_menu_path, '\n')

                # Copy menu python file
                shutil.copy(menu_path, new_menu_path)

                # Load new menu name to Export Menus pushbutton
                self.edit_saved_export_menu_menu.text = menu_prefix + new_menu_path.rsplit('/', 1)[1][:-3]

                # Load menu settings from duplicated menu
                self.load_preset()

                # Refresh python hooks
                pyflame.refresh_hooks()

                pyflame.print('Duplicate preset created.')

            # Labels
            self.edit_menu_visibility_label = PyFlameLabel(
                text='Menu Visibility',
                )
            self.edit_menu_label = PyFlameLabel(
                text='Export Menus',
                )
            self.edit_menu_name_label = PyFlameLabel(
                text='Menu Name',
                )
            self.edit_current_preset_label = PyFlameLabel(
                text='Current Preset',
                align=Align.CENTER,
                style=Style.UNDERLINE,
                )
            self.edit_after_export_label = PyFlameLabel(
                text='After Export',
                align=Align.CENTER,
                style=Style.UNDERLINE,
                )

            # Entries
            self.edit_menu_name_entry = PyFlameEntry(
                text='',
                )

            # Pushbutton menus
            self.edit_saved_export_menu_menu = PyFlameMenu(
                text='',
                menu_options=[],
                connect=self.load_preset,
                )
            self.edit_menu_visibility_menu = PyFlameMenu(
                text='Project',
                menu_options=[
                    'Project',
                    'Shared',
                    ],
                )

            # Pushbuttons
            self.edit_reveal_in_mediahub_pushbutton = PyFlamePushButton(
                text='Reveal in Mediahub',
                checked=False,
                )
            self.edit_reveal_in_finder_pushbutton = PyFlamePushButton(
                text='Reveal in Finder',
                checked=False,
                )

            # Buttons
            self.edit_delete_button = PyFlameButton(
                text='Delete',
                connect=delete_export_menu,
                )
            self.edit_duplicate_button = PyFlameButton(
                text='Duplicate',
                connect=duplicate_preset,
                )

            self.edit_save_button = PyFlameButton(
                text='Save',
                connect=partial(self.save_menus, 'Edit'),
                color=Color.BLUE,
                )
            self.edit_done_button = PyFlameButton(
                text='Done',
                connect=self.window.close,
                )

            # Lines
            horizontal_line_01 = PyFlameHorizontalLine()
            horizontal_line_02 = PyFlameHorizontalLine()

            #-------------------------------------

            # Create tabs for export presets
            build_edit_preset_tabs()

            # Load saved menus
            self.get_saved_menus()

            #-------------------------------------
            # [Edit Tab Layout]
            #-------------------------------------

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_menu_label, 0, 0)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_saved_export_menu_menu, 0, 1, 1, 3)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_menu_name_label, 1, 0)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_menu_name_entry, 1, 1, 1, 3)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_menu_visibility_label, 2, 0)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_menu_visibility_menu, 2, 1)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_current_preset_label, 0, 7)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_duplicate_button, 1, 7)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_delete_button, 2, 7)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_after_export_label, 0, 8)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_reveal_in_finder_pushbutton, 1, 8)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_reveal_in_mediahub_pushbutton, 2, 8)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(horizontal_line_01, 4, 0, 1, 9)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_preset_tabs, 5, 0, 4, 9)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(horizontal_line_02, 9, 0, 1, 9)

            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_done_button, 10, 7)
            self.main_tabs.tab_pages['Edit'].grid_layout.addWidget(self.edit_save_button, 10, 8)

        # Create main window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            grid_layout_columns=9,
            grid_layout_rows=10,
            parent=None,
            )

        self.main_tabs = PyFlameTabWidget(
            tab_names=[
                'Create',
                'Edit',
                ],
            grid_layout_columns=9,
            grid_layout_rows=10,
            )

        # Load tabs
        create_tab()
        edit_tab()

        # Add tabs to window
        self.window.grid_layout.addWidget(self.main_tabs, 0, 0, 10, 10)

        self.menu_name_entry.setFocus()

    def get_saved_menus(self) -> None:
        """
        Get Saved Menus
        ===============

        Get saved project and shared export menus and set the saved presets pushbutton menu.
        """

        print('Saved Export Menus:\n')

        # Get saved project export menus
        try:
            project_export_menus = ['Project: ' + x[:-3] for x in os.listdir(os.path.join(self.project_menus_dir, self.flame_project_name)) if x.endswith('.py')]
            project_export_menus.sort()
        except:
            project_export_menus = []
        self.print_list('Project Export Menus', project_export_menus)

        # Get saved shared export menus
        try:
            shared_export_menus = ['Shared: ' + x[:-3] for x in os.listdir(self.shared_menus_dir) if x.endswith('.py')]
            shared_export_menus.sort()
        except:
            shared_export_menus = []
        self.print_list('Shared Export Menus', shared_export_menus)

        # Combine project and shared export menus lists
        all_export_menus = project_export_menus + shared_export_menus

        # If no export menus are found then set the pushbutton text to 'No Saved Export Menus Found'
        if not all_export_menus:
            all_export_menus = ['No Saved Export Menus Found']

        # Set saved presets pushbutton menu text and options
        self.edit_saved_export_menu_menu.update_menu(
            text=all_export_menus[0],
            menu_options=all_export_menus,
            connect = self.load_preset,
            )

        # Load menu if only one menu is found
        if not all_export_menus[0] == 'No Saved Export Menus Found':
            self.load_preset()

    def load_preset(self, preset_to_load=None) -> None:
        """
        Load selected preset from the saved presets pushbutton menu.
        If no preset is found, turn off UI elements.

        Args:
            preset_to_load (str): Name of preset to load.
                Default: None
        """

        def no_presets_found() -> None:
            """
            Turn off UI elements if no preset is found to load.
            """

            self.edit_menu_label.enabled = False
            self.edit_saved_export_menu_menu.enabled = False
            self.edit_menu_visibility_label.enabled = False
            self.edit_menu_visibility_menu.enabled = False
            self.edit_menu_name_label.enabled = False
            self.edit_menu_name_entry.enabled = False
            self.edit_saved_preset_type_label_01.enabled = False
            self.edit_saved_presets_label_01.enabled = False
            self.edit_export_path_label_01.enabled = False
            self.edit_preset_type_menu_01.enabled = False
            self.edit_presets_menu_01.enabled = False
            self.edit_export_path_entry_01.enabled = False
            self.edit_server_browse_button_01.enabled = False
            self.edit_token_pushbutton_01.enabled = False
            self.edit_top_layer_pushbutton_01.enabled = False
            self.edit_foreground_pushbutton_01.enabled = False
            self.edit_between_marks_pushbutton_01.enabled = False
            self.edit_enable_preset_pushbutton_02.enabled = False
            self.edit_enable_preset_pushbutton_03.enabled = False
            self.edit_enable_preset_pushbutton_04.enabled = False
            self.edit_enable_preset_pushbutton_05.enabled = False
            self.edit_delete_button.enabled = False

            self.edit_menu_visibility_menu.text = ''
            self.edit_preset_type_menu_01.text = ''
            self.edit_preset_type_menu_02.text = ''
            self.edit_preset_type_menu_03.text = ''
            self.edit_preset_type_menu_04.text = ''
            self.edit_preset_type_menu_05.text = ''

            print('--> No existing presets found. \n')

        if self.edit_saved_export_menu_menu.text == 'No Saved Presets Found':
            no_presets_found() # Turn off UI elements
            return

        elif preset_to_load:
            self.edit_saved_export_menu_menu.text = preset_to_load
        selected_menu_name = self.edit_saved_export_menu_menu.text.rsplit(': ', 1)[1] # Get selected menu name from pushbutton text
        #print('Selected Menu Name:', selected_menu_name)

        self.edit_menu_name_entry.text = selected_menu_name # Set Menu Name Entry

        # Set Menu Visibility Pushbutton Menu
        if 'Shared: ' in self.edit_saved_export_menu_menu.text:
            self.edit_menu_visibility_menu.text = 'Shared'
            selected_menu_path = os.path.join(self.shared_menus_dir, selected_menu_name) + '.py'
        elif 'Project: ' in self.edit_saved_export_menu_menu.text:
            self.edit_menu_visibility_menu.text = 'Project'
            selected_menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, selected_menu_name) + '.py'

        # Read in menu script
        #-----------------------------------------

        get_menu_values = open(selected_menu_path, 'r')
        menu_lines = get_menu_values.read().splitlines()

        get_menu_values.close()

        def get_preset_info(preset_num, enable_btn, saved_preset_type_label, saved_presets_label, export_path_label, export_path_entry, top_layer_button, foreground_button, between_marks_button, token_button, export_button, server_button, saved_presets_button, include_subtitles_button, subtitles_export_mode_button, subtitles_tracks_button, ):

            # Get preset info
            preset_start_index = menu_lines.index(f'        # Export preset {preset_num}')
            preset_end_index = menu_lines.index(f'        # Export preset {preset_num} END') + 1
            preset_lines = menu_lines[preset_start_index:preset_end_index]

            if enable_btn:
                enable_btn.checked = True

                # Enable UI elements
                saved_preset_type_label.enabled = True
                saved_presets_label.enabled = True
                export_path_label.enabled = True
                export_path_entry.enabled = True
                top_layer_button.enabled = True
                foreground_button.enabled = True
                between_marks_button.enabled = True
                token_button.enabled = True
                export_button.enabled = True
                server_button.enabled = True
                saved_presets_button.enabled = True
                include_subtitles_button.enabled = True
                subtitles_export_mode_button.enabled = True
                subtitles_tracks_button.enabled = True

            # Set UI elements
            print(f'Preset: {preset_num}')
            for line in preset_lines:
                if line == '        clip_output.use_top_video_track = True':
                    top_layer_button.checked = True
                    print('Use Top Layer: True')
                elif line == '        clip_output.use_top_video_track = False':
                    top_layer_button.checked = False
                    print('Use Top Layer: False')
                elif line == '        clip_output.foreground = True':
                    foreground_button.checked = True
                    print('Foreground Export: True')
                elif line == '        clip_output.foreground = False':
                    foreground_button.checked = False
                    print('Foreground Export: False')
                elif line == '        clip_output.export_between_marks = True':
                    between_marks_button.checked = True
                    print('Export Between Marks: True')
                elif line == '        clip_output.export_between_marks = False':
                    between_marks_button.checked = False
                    print('Export Between Marks: False')
                elif '        new_export_path = translate_tokenized_path(clip, ' in line:
                    path = line.split("'", 2)[1]
                    export_path_entry.text = path
                    print('Export Path:', path)
                elif '        clip_output.export(clip, ' in line:
                    preset_path = line.split("'", 2)[1]
                    preset_name = preset_path.rsplit('/', 1)[1][:-4]
                    saved_presets_button.text = preset_name
                    print('Preset Name:', preset_name)
                # Subtitles
                elif '        clip_output.include_subtitles = True' in line:
                    include_subtitles_button.checked = True
                    subtitles_export_mode_button.enabled = True
                    subtitles_tracks_button.enabled = True
                    print('Include subtitles: True')
                elif '        clip_output.include_subtitles = False' in line:
                    include_subtitles_button.checked = False
                    subtitles_export_mode_button.enabled = False
                    subtitles_tracks_button.enabled = False
                    print('Include subtitles: False')
                elif '        clip_output.export_subtitles_as_files = False' in line:
                    subtitles_export_mode_button.text = 'Burn in Image'
                    print('Subtitles export mode: Burn in Image')
                elif '        clip_output.export_subtitles_as_files = True' in line:
                    subtitles_export_mode_button.text = 'Export as Files'
                    print('Subtitles export mode: Export as Files')
                elif '        clip_output.export_all_subtitles = True' in line:
                    subtitles_tracks_button.text = 'All Subtitles Tracks'
                    print('Subtitles tracks: All Subtitles Tracks')
                elif '        clip_output.export_all_subtitles = False' in line:
                    subtitles_tracks_button.text = 'Current Subtitles Track'
                    print('Subtitles tracks: Current Subtitles Track')

                if 'clip_output.export' in line:
                    if 'project' in line:
                        if 'file_sequence' in line:
                            export_button.text = 'Project: File Sequence'
                            print('Saved Preset Type: Project File Seq')
                        elif 'movie_file' in line:
                            export_button.text = 'Project: Movie'
                            print('Saved Preset Type: Project Movie File')
                    if 'shared' in line:
                        if 'file_sequence' in line:
                            export_button.text = 'Shared: File Sequence'
                            print('Saved Preset Type: Shared File Seq')
                        elif 'movie_file' in line:
                            export_button.text = 'Shared: Movie'
                            print('Saved Preset Type: Shared Movie File')

        def disable_ui_elements(enable_btn, saved_preset_type_label, saved_presets_label, export_path_label, export_path_entry, top_layer_button, foreground_button, between_marks_button, token_button, export_button, server_button, saved_presets_button, include_subtitles_button, subtitles_export_mode_button, subtitles_tracks_button):

            # Disable UI elements
            enable_btn.checked = False
            saved_preset_type_label.enabled = False
            saved_presets_label.enabled = False
            export_path_label.enabled = False
            export_path_entry.text = ''
            export_path_entry.enabled = False
            top_layer_button.enabled = False
            foreground_button.enabled = False
            between_marks_button.enabled = False
            token_button.enabled = False
            export_button.enabled = False
            server_button.enabled = False
            saved_presets_button.enabled = False
            include_subtitles_button.enabled = False
            subtitles_export_mode_button.enabled = False
            subtitles_tracks_button.enabled = False

        print('Loading Preset...\n')

        if '    reveal_in_mediahub = True' in menu_lines:
            self.edit_reveal_in_mediahub_pushbutton.checked = True
            print('Reveal in Mediahub: True')
        else:
            self.edit_reveal_in_mediahub_pushbutton.checked = False
            print('Reveal in Mediahub: False')

        if '    reveal_in_finder = True' in menu_lines:
            self.edit_reveal_in_finder_pushbutton.checked = True
            print('Reveal in Finder: True')
        else:
            self.edit_reveal_in_finder_pushbutton.checked = False
            print('Reveal in Finder: False')

        # Get preset UI settings. If none are found, disable UI for that tab

        get_preset_info('One', None, self.edit_saved_presets_label_01, self.edit_saved_presets_label_01, self.edit_export_path_label_01, self.edit_export_path_entry_01, self.edit_top_layer_pushbutton_01, self.edit_foreground_pushbutton_01, self.edit_between_marks_pushbutton_01, self.edit_token_pushbutton_01, self.edit_preset_type_menu_01, self.edit_server_browse_button_01, self.edit_presets_menu_01, self.edit_include_subtitles_pushbutton_01, self.edit_subtitles_export_mode_menu_01, self.edit_subtitles_tracks_menu_01)
        preset_01_push_btn_text = self.edit_presets_menu_01.text

        try:
            get_preset_info('Two', self.edit_enable_preset_pushbutton_02, self.edit_saved_preset_type_label_02, self.edit_saved_presets_label_02, self.edit_export_path_label_02, self.edit_export_path_entry_02, self.edit_top_layer_pushbutton_02, self.edit_foreground_pushbutton_02, self.edit_between_marks_pushbutton_02, self.edit_token_pushbutton_02, self.edit_preset_type_menu_02, self.edit_server_browse_button_02, self.edit_presets_menu_02, self.edit_include_subtitles_pushbutton_02, self.edit_subtitles_export_mode_menu_02, self.edit_subtitles_tracks_menu_02)
            preset_02_push_btn_text = self.edit_presets_menu_02.text
        except:
            # Disable UI elements if nothing loaded for preset two
            disable_ui_elements(self.edit_enable_preset_pushbutton_02, self.edit_saved_preset_type_label_02, self.edit_saved_presets_label_02, self.edit_export_path_label_02, self.edit_export_path_entry_02, self.edit_top_layer_pushbutton_02, self.edit_foreground_pushbutton_02, self.edit_between_marks_pushbutton_02, self.edit_token_pushbutton_02, self.edit_preset_type_menu_02, self.edit_server_browse_button_02, self.edit_presets_menu_02, self.edit_include_subtitles_pushbutton_02, self.edit_subtitles_export_mode_menu_02, self.edit_subtitles_tracks_menu_02)
        try:
            get_preset_info('Three', self.edit_enable_preset_pushbutton_03, self.edit_saved_preset_type_label_03, self.edit_saved_presets_label_03, self.edit_export_path_label_03, self.edit_export_path_entry_03, self.edit_top_layer_pushbutton_03, self.edit_foreground_pushbutton_03, self.edit_between_marks_pushbutton_03, self.edit_token_pushbutton_03, self.edit_preset_type_menu_03, self.edit_server_browse_button_03, self.edit_presets_menu_03, self.edit_include_subtitles_pushbutton_03, self.edit_subtitles_export_mode_menu_03, self.edit_subtitles_tracks_menu_03)
            preset_03_push_btn_text = self.edit_presets_menu_03.text
        except:
            # Disable UI elements if nothing loaded for preset three
            disable_ui_elements(self.edit_enable_preset_pushbutton_03, self.edit_saved_preset_type_label_03, self.edit_saved_presets_label_03, self.edit_export_path_label_03, self.edit_export_path_entry_03, self.edit_top_layer_pushbutton_03, self.edit_foreground_pushbutton_03, self.edit_between_marks_pushbutton_03, self.edit_token_pushbutton_03, self.edit_preset_type_menu_03, self.edit_server_browse_button_03, self.edit_presets_menu_03, self.edit_include_subtitles_pushbutton_03, self.edit_subtitles_export_mode_menu_03, self.edit_subtitles_tracks_menu_03)
        try:
            get_preset_info('Four', self.edit_enable_preset_pushbutton_04, self.edit_saved_preset_type_label_04, self.edit_saved_presets_label_04, self.edit_export_path_label_04, self.edit_export_path_entry_04, self.edit_top_layer_pushbutton_04, self.edit_foreground_pushbutton_04, self.edit_between_marks_pushbutton_04, self.edit_token_pushbutton_04, self.edit_preset_type_menu_04, self.edit_server_browse_button_04, self.edit_presets_menu_04, self.edit_include_subtitles_pushbutton_04, self.edit_subtitles_export_mode_menu_04, self.edit_subtitles_tracks_menu_04)
            preset_04_push_btn_text = self.edit_presets_menu_04.text
        except:
            # Disable UI elements if nothing loaded for preset four
            disable_ui_elements(self.edit_enable_preset_pushbutton_04, self.edit_saved_preset_type_label_04, self.edit_saved_presets_label_04, self.edit_export_path_label_04, self.edit_export_path_entry_04, self.edit_top_layer_pushbutton_04, self.edit_foreground_pushbutton_04, self.edit_between_marks_pushbutton_04, self.edit_token_pushbutton_04, self.edit_preset_type_menu_04, self.edit_server_browse_button_04, self.edit_presets_menu_04, self.edit_include_subtitles_pushbutton_04, self.edit_subtitles_export_mode_menu_04, self.edit_subtitles_tracks_menu_04)
        try:
            get_preset_info('Five', self.edit_enable_preset_pushbutton_05, self.edit_saved_preset_type_label_05, self.edit_saved_presets_label_05, self.edit_export_path_label_05, self.edit_export_path_entry_05, self.edit_top_layer_pushbutton_05, self.edit_foreground_pushbutton_05, self.edit_between_marks_pushbutton_05, self.edit_token_pushbutton_05, self.edit_preset_type_menu_05, self.edit_server_browse_button_05, self.edit_presets_menu_05, self.edit_include_subtitles_pushbutton_05, self.edit_subtitles_export_mode_menu_05, self.edit_subtitles_tracks_menu_05)
            preset_05_push_btn_text = self.edit_presets_menu_05.text
        except:
            # Disable UI elements if nothing loaded for preset five
            disable_ui_elements(self.edit_enable_preset_pushbutton_05, self.edit_saved_preset_type_label_05, self.edit_saved_presets_label_05, self.edit_export_path_label_05, self.edit_export_path_entry_05, self.edit_top_layer_pushbutton_05, self.edit_foreground_pushbutton_05, self.edit_between_marks_pushbutton_05, self.edit_token_pushbutton_05, self.edit_preset_type_menu_05, self.edit_server_browse_button_05, self.edit_presets_menu_05, self.edit_include_subtitles_pushbutton_05, self.edit_subtitles_export_mode_menu_05, self.edit_subtitles_tracks_menu_05)

        self.edit_presets_menu_01.text = preset_01_push_btn_text
        try:
            self.edit_presets_menu_02.text = preset_02_push_btn_text
        except:
            pass
        try:
            self.edit_presets_menu_03.text = preset_03_push_btn_text
        except:
            pass
        try:
            self.edit_presets_menu_04.text = preset_04_push_btn_text
        except:
            pass
        try:
            self.edit_presets_menu_05.text = preset_05_push_btn_text
        except:
            pass

        print('\n--> Existing export presets loaded.\n')

    def directory_path_browse(self, entry: PyFlameEntry, window_to_hide: PyFlameWindow) -> None:
        """
        Directory Path Browse
        =====================

        Opens a file browser dialog to select a directory and sets the entry text to the selected directory.

        Args:
            entry (PyFlameEntry): Entry widget to set the path text.
            window_to_hide (PyFlameWindow): Window to hide while the file browser dialog is open.
        """

        try:
            path = pyflame.file_browser(
                path=entry.text,
                title='Select Directory',
                select_directory=True,
                window_to_hide=window_to_hide,
                )

            if path:
                entry.text = path
        except Exception as e:
            print(f"An error occurred while browsing for a directory: {e}")

    def save_menus(self, tab) -> None:

        def get_tab_settings(tab: str) -> dict:
            """
            Get Tab Settings
            ================

            Get settings from the create or edit tab and return as a dictionary.

            Args:
                tab (str): 'Create' or 'Edit'

            Returns:
                dict: tab settings
            """

            if tab == 'Create':
                settings_dict = {
                    'create_tab_zero':{
                        'Menu Visibility': self.menu_visibility_menu.text,
                        'Menu Name': self.menu_name_entry.text,
                        'Reveal in MediaHub': self.reveal_in_mediahub_pushbutton.checked,
                        'Reveal in Finder': self.reveal_in_finder_pushbutton.checked,
                        },
                    'create_tab_one': {
                        'Enabled' : True,
                        'Preset Type Menu' : self.preset_type_menu_01.text,
                        'Preset Menu' : self.presets_menu_01.text,
                        'Export Path' : self.export_path_entry_01.text,
                        'Top Layer' : self.top_layer_pushbutton_01.checked,
                        'Foreground Export' : self.foreground_pushbutton_01.checked,
                        'Export Between Marks' : self.between_marks_pushbutton_01.checked,
                        'Include Subtitles' : self.include_subtitles_pushbutton_01.checked,
                        'Subtitles Export Mode': self.subtitles_export_mode_menu_01.text,
                        'Subtitles Tracks': self.subtitles_tracks_menu_01.text,
                        },
                    'create_tab_two': {
                        'Enabled' : self.enable_preset_pushbutton_02.text,
                        'Preset Type Menu' : self.preset_type_menu_02.text,
                        'Preset Menu' : self.presets_menu_02.text,
                        'Export Path' : self.export_path_entry_02.text,
                        'Top Layer' : self.top_layer_pushbutton_02.checked,
                        'Foreground Export' : self.foreground_pushbutton_02.checked,
                        'Export Between Marks' : self.between_marks_pushbutton_02.checked,
                        'Include Subtitles' : self.include_subtitles_pushbutton_02.checked,
                        'Subtitles Export Mode': self.subtitles_export_mode_menu_02.text,
                        'Subtitles Tracks': self.subtitles_tracks_menu_02.text,
                        },
                    'create_tab_three': {
                        'Enabled' : self.enable_preset_pushbutton_03.text,
                        'Preset Type Menu' : self.preset_type_menu_03.text,
                        'Preset Menu' : self.presets_menu_03.text,
                        'Export Path' : self.export_path_entry_03.text,
                        'Top Layer' : self.top_layer_pushbutton_03.checked,
                        'Foreground Export' : self.foreground_pushbutton_03.checked,
                        'Export Between Marks' : self.between_marks_pushbutton_03.checked,
                        'Include Subtitles' : self.include_subtitles_pushbutton_03.checked,
                        'Subtitles Export Mode': self.subtitles_export_mode_menu_03.text,
                        'Subtitles Tracks': self.subtitles_tracks_menu_03.text,
                        },
                    'create_tab_four': {
                        'Enabled' : self.enable_preset_pushbutton_04.text,
                        'Preset Type Menu' : self.preset_type_menu_04.text,
                        'Preset Menu' : self.presets_menu_04.text,
                        'Export Path' : self.export_path_entry_04.text,
                        'Top Layer' : self.top_layer_pushbutton_04.checked,
                        'Foreground Export' : self.foreground_pushbutton_04.checked,
                        'Export Between Marks' : self.between_marks_pushbutton_04.checked,
                        'Include Subtitles' : self.include_subtitles_pushbutton_04.checked,
                        'Subtitles Export Mode': self.subtitles_export_mode_menu_04.text,
                        'Subtitles Tracks': self.subtitles_tracks_menu_04.text,
                        },
                    'create_tab_five': {
                        'Enabled' : self.enable_preset_pushbutton_05.text,
                        'Preset Type Menu' : self.preset_type_menu_05.text,
                        'Preset Menu' : self.presets_menu_05.text,
                        'Export Path' : self.export_path_entry_05.text,
                        'Top Layer' : self.top_layer_pushbutton_05.checked,
                        'Foreground Export' : self.foreground_pushbutton_05.checked,
                        'Export Between Marks' : self.between_marks_pushbutton_05.checked,
                        'Include Subtitles' : self.include_subtitles_pushbutton_05.checked,
                        'Subtitles Export Mode': self.subtitles_export_mode_menu_05.text,
                        'Subtitles Tracks': self.subtitles_tracks_menu_05.text,
                        }
                    }
            elif tab == 'Edit':
                settings_dict = {
                    'edit_tab_zero':{
                        'Menu Visibility': self.edit_menu_visibility_menu.text,
                        'Menu Name': self.edit_menu_name_entry.text,
                        'Reveal in MediaHub': self.edit_reveal_in_mediahub_pushbutton.checked,
                        'Reveal in Finder': self.edit_reveal_in_finder_pushbutton.checked,
                        },
                    'edit_tab_one': {
                        'Enabled' : True,
                        'Preset Type Menu' : self.edit_preset_type_menu_01.text,
                        'Preset Menu' : self.edit_presets_menu_01.text,
                        'Export Path' : self.edit_export_path_entry_01.text,
                        'Top Layer' : self.edit_top_layer_pushbutton_01.checked,
                        'Foreground Export' : self.edit_foreground_pushbutton_01.checked,
                        'Export Between Marks' : self.edit_between_marks_pushbutton_01.checked,
                        'Include Subtitles' : self.edit_include_subtitles_pushbutton_01.checked,
                        'Subtitles Export Mode': self.edit_subtitles_export_mode_menu_01.text,
                        'Subtitles Tracks': self.edit_subtitles_tracks_menu_01.text,
                        },
                    'edit_tab_two': {
                        'Enabled' : self.edit_enable_preset_pushbutton_02.text,
                        'Preset Type Menu' : self.edit_preset_type_menu_02.text,
                        'Preset Menu' : self.edit_presets_menu_02.text,
                        'Export Path' : self.edit_export_path_entry_02.text,
                        'Top Layer' : self.edit_top_layer_pushbutton_02.checked,
                        'Foreground Export' : self.edit_foreground_pushbutton_02.checked,
                        'Export Between Marks' : self.edit_between_marks_pushbutton_02.checked,
                        'Include Subtitles' : self.edit_include_subtitles_pushbutton_02.checked,
                        'Subtitles Export Mode': self.edit_subtitles_export_mode_menu_02.text,
                        'Subtitles Tracks': self.edit_subtitles_tracks_menu_02.text,
                        },
                    'edit_tab_three': {
                        'Enabled' : self.edit_enable_preset_pushbutton_03.text,
                        'Preset Type Menu' : self.edit_preset_type_menu_03.text,
                        'Preset Menu' : self.edit_presets_menu_03.text,
                        'Export Path' : self.edit_export_path_entry_03.text,
                        'Top Layer' : self.edit_top_layer_pushbutton_03.checked,
                        'Foreground Export' : self.edit_foreground_pushbutton_03.checked,
                        'Export Between Marks' : self.edit_between_marks_pushbutton_03.checked,
                        'Include Subtitles' : self.edit_include_subtitles_pushbutton_03.checked,
                        'Subtitles Export Mode': self.edit_subtitles_export_mode_menu_03.text,
                        'Subtitles Tracks': self.edit_subtitles_tracks_menu_03.text,
                        },
                    'edit_tab_four': {
                        'Enabled' : self.edit_enable_preset_pushbutton_04.text,
                        'Preset Type Menu' : self.edit_preset_type_menu_04.text,
                        'Preset Menu' : self.edit_presets_menu_04.text,
                        'Export Path' : self.edit_export_path_entry_04.text,
                        'Top Layer' : self.edit_top_layer_pushbutton_04.checked,
                        'Foreground Export' : self.edit_foreground_pushbutton_04.checked,
                        'Export Between Marks' : self.edit_between_marks_pushbutton_04.checked,
                        'Include Subtitles' : self.edit_include_subtitles_pushbutton_04.checked,
                        'Subtitles Export Mode': self.edit_subtitles_export_mode_menu_04.text,
                        'Subtitles Tracks': self.edit_subtitles_tracks_menu_04.text,
                        },
                    'edit_tab_five': {
                        'Enabled' : self.edit_enable_preset_pushbutton_05.text,
                        'Preset Type Menu' : self.edit_preset_type_menu_05.text,
                        'Preset Menu' : self.edit_presets_menu_05.text,
                        'Export Path' : self.edit_export_path_entry_05.text,
                        'Top Layer' : self.edit_top_layer_pushbutton_05.checked,
                        'Foreground Export' : self.edit_foreground_pushbutton_05.checked,
                        'Export Between Marks' : self.edit_between_marks_pushbutton_05.checked,
                        'Include Subtitles' : self.edit_include_subtitles_pushbutton_05.checked,
                        'Subtitles Export Mode': self.edit_subtitles_export_mode_menu_05.text,
                        'Subtitles Tracks': self.edit_subtitles_tracks_menu_05.text,
                        }
                    }

            return settings_dict

        def preset_check(tab_options_dict: dict) -> str:
            """
            Preset Check
            ============

            Check settings for each tab and return error message if any are found.

            Args:
            -----
                tab_options_dict (dict):
                    tab settings

            Returns:
            --------
                str: error message
            """

            main_tab = str(next(iter(tab_options_dict))).split('_', 1)[0]

            # Check Menu Name entry
            if main_tab == 'create':
                if not self.menu_name_entry.text:
                    return 'Add menu name'
            else:
                if not self.edit_menu_name_entry.text:
                    return 'Add menu name'

            for key, value in tab_options_dict.items():
                tab_number = key.rsplit('_', 1)[1].capitalize()
                if tab_number != 'Zero':

                    # If tab is enabled, check settings
                    if value['Enabled'] == True:

                        # Make sure on Shared saved presets are used with shared visibility menus
                        if main_tab == 'create':
                            if 'Shared' in self.menu_visibility_menu.text and 'Shared:' not in value['Preset Type Menu']:
                                return f'Preset {tab_number}: Only a SHARED Saved Preset can be added to a Menu with Shared Menu Visibility.'
                        else:
                            if 'Shared' in self.edit_menu_visibility_menu.text and 'Shared:' not in value['Preset Type Menu']:
                                return f'Preset {tab_number}: Only a SHARED Saved Preset can be added to a Menu with Shared Menu Visibility.'

                        # Give message if trying to save with No Save Presets Found
                        if value['Preset Menu'] == 'No Saved Presets Found':
                            return f'Preset {tab_number}: No saved preset selected. Select a different Preset Type or save a preset in Flame.'

                        # Check path entry
                        if not value['Export Path']:
                            return f'Preset {tab_number}: Enter export path.'

        def get_menu_save_path() -> tuple:
            """
            Get Menu Save Path
            ==================

            Get menu save path and name.

            Returns:
            --------
                menu_flame_project, menu_save_path (tuple):
                    menu_flame_project (str): Flame project name
                    menu_save_path (str): menu save path
            """

            # Set path for new menu file
            if menu_visibility == 'Project':
                menu_save_dir = os.path.join(self.project_menus_dir, self.flame_project_name)
                menu_flame_project = self.flame_project_name
            else:
                menu_save_dir = self.shared_menus_dir
                menu_flame_project = 'None'

            if not os.path.isdir(menu_save_dir):
                os.makedirs(menu_save_dir)

            menu_file_name = menu_name.replace('.', '_') + '.py'

            menu_save_path = os.path.join(menu_save_dir, menu_file_name)

            return menu_flame_project, menu_save_path

        def create_main_tab_token_dict() -> dict:
            """
            Create Main Tab Token Dictionary
            ================================

            Create dictionary for tokens in menu template with values from main tab.

            Returns:
            --------
                dict:
                    template token dictionary
            """

            # Create dictionary for tokens in menu template with values from main tab
            main_tab_token_dict = {}
            main_tab_token_dict['<FlameProject>'] = menu_flame_project
            main_tab_token_dict['<PresetName>'] = menu_name
            main_tab_token_dict['<PresetType>'] = menu_visibility
            main_tab_token_dict['<RevealInMediaHub>'] = reveal_in_mediahub
            main_tab_token_dict['<RevealInFinder>'] = reveal_in_finder
            main_tab_token_dict['<FlameMinMaxVersion>'] = self.flame_min_max_version

            return main_tab_token_dict

        def menu_template_preset_lines(tab_options_dict: dict) -> list:
            """
            Menu Template Preset Lines
            ==========================

            Create new lines to be added to menu template.

            Args:
            -----
                tab_options_dict (dict):
                    tab settings

            Returns:
            --------
                list:
                    new lines to be added to menu template
            """

            def get_preset_path(preset_type_menu: str, preset_menu: str) -> str:

                # Get selected preset path
                if 'Project' in preset_type_menu:
                    preset_path = self.project_preset_path
                else:
                    preset_path = self.shared_preset_path

                if 'Movie' in preset_type_menu:
                    preset_dir_path = preset_path + '/movie_file'
                else:
                    preset_dir_path = preset_path + '/file_sequence'

                preset_file_path = os.path.join(preset_dir_path, preset_menu) + '.xml'

                #print('preset path:', preset_file_path, '\n')

                return preset_file_path

            def new_lines(tab_number: str,
                          top_layer: str,
                          foreground_export: str,
                          export_between_marks: str,
                          include_subtitles: str,
                          subtitles_export_mode: str,
                          subtitles_tracks: str,
                          export_path: str,
                          preset_file_path: str) -> list:
                """
                Build new lines to be added to menu template. Add subtitle lines if Flame is 2024.2 or later.

                Returns:
                    list: menu_lines
                """

                menu_lines.append("")
                menu_lines.append(f"        # Export preset {tab_number}")
                menu_lines.append("")
                menu_lines.append("        # Export using top video track")
                menu_lines.append(f"        clip_output.use_top_video_track = {top_layer}")
                menu_lines.append(f"        print('\\n--> Export using top layer: {top_layer}')")
                menu_lines.append("")
                menu_lines.append("        # Set export to foreground")
                menu_lines.append(f"        clip_output.foreground = {foreground_export}")
                menu_lines.append(f"        print('--> Export in foreground: {foreground_export}')")
                menu_lines.append("")
                menu_lines.append("        # Export between markers")
                menu_lines.append(f"        clip_output.export_between_marks = {export_between_marks}")
                menu_lines.append(f"        print('--> Export between marks: {export_between_marks}\\n')")

                # Add lines for subtitles if version of Flame is 2024.2 or greater.
                if self.flame_version >= 2024.2:
                    menu_lines.append("")
                    menu_lines.append("        # Include subtitles")
                    menu_lines.append(f"        clip_output.include_subtitles = {include_subtitles}")
                    menu_lines.append(f"        print('--> Include subtitles: {include_subtitles}\\n')")
                    menu_lines.append("")
                    # Subtitles export mode: 'Burn in Image = False, 'Export as Files' = True
                    if subtitles_export_mode == 'Burn in Image':
                        subtitles_export_mode = False
                    else:
                        subtitles_export_mode = True
                    menu_lines.append("        # Subtitles export mode")
                    menu_lines.append(f"        clip_output.export_subtitles_as_files = {subtitles_export_mode}")
                    menu_lines.append(f"        print('--> Subtitles export mode: {subtitles_export_mode}\\n')")
                    menu_lines.append("")
                    # Subtitles tracks: 'Current Subtitles Track' = False, 'All Subtitles Tracks' = True
                    if subtitles_tracks == 'All Subtitles Tracks':
                        subtitles_tracks = True
                    else:
                        subtitles_tracks = False
                    menu_lines.append("        # Subtitles tracks")
                    menu_lines.append(f"        clip_output.export_all_subtitles = {subtitles_tracks}")
                    menu_lines.append(f"        print('--> Subtitles tracks: {subtitles_tracks}\\n')")

                menu_lines.append("")
                menu_lines.append("        # Translate tokens in path")
                menu_lines.append("")
                menu_lines.append(f"        new_export_path = translate_tokenized_path(clip, '{export_path}')")
                menu_lines.append("")
                menu_lines.append("        if not new_export_path:")
                menu_lines.append("            return")
                menu_lines.append("")
                menu_lines.append("        if not os.path.isdir(new_export_path):")
                menu_lines.append("            try:")
                menu_lines.append("                os.makedirs(new_export_path)")
                menu_lines.append("            except:")
                menu_lines.append("                PyFlameMessageWindow(")
                menu_lines.append("                    message=f'Could not create export path.\\n\\nPlease check the export path and try again.\\n\\n{new_export_path}',")
                menu_lines.append("                    message_type=MessageType.ERROR,")
                menu_lines.append("                    title='Export Path Error',")
                menu_lines.append("                    parent=None,")
                menu_lines.append("                )")
                menu_lines.append("                return")
                menu_lines.append("")
                menu_lines.append(f"        clip_output.export(clip, '{preset_file_path}', new_export_path)")
                menu_lines.append("")
                menu_lines.append(f"        # Export preset {tab_number} END")
                menu_lines.append("")

            menu_lines = []

            print('tab options dict:', tab_options_dict, '\n')

            # Loop through tabs to build preset menus
            for key, value in tab_options_dict.items():
                tab_number = key.rsplit('_', 1)[1].capitalize()
                if tab_number != 'Zero':
                    if value['Enabled'] == True:
                        preset_file_path = get_preset_path(value['Preset Type Menu'], value['Preset Menu'])
                        new_lines(tab_number, value['Top Layer'], value['Foreground Export'], value['Export Between Marks'], value['Include Subtitles'], value['Subtitles Export Mode'], value['Subtitles Tracks'], value['Export Path'], preset_file_path)

            return menu_lines

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings from main tab to config file.
            """

            self.settings.save_config(
                config_values={
                    'export_path': self.export_path_entry_01.text,
                    'use_top_layer': self.top_layer_pushbutton_01.checked,
                    'export_in_foreground': self.foreground_pushbutton_01.checked,
                    'export_between_marks': self.between_marks_pushbutton_01.checked,
                    'reveal_in_mediahub': self.reveal_in_mediahub_pushbutton.checked,
                    'reveal_in_finder': self.reveal_in_finder_pushbutton.checked,
                    }
                )

        def get_original_menu_file_path(tab: str) -> str:
            """
            Get Original Menu File Path
            ===========================

            Get path to original menu file.

            Args:
            -----
                tab (str):
                    'Create' or 'Edit'

            Returns:
            --------
                original_menu_file (str):
                    original menu file path
            """

            if tab == 'Edit':
                original_menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]
            else:
                original_menu_name = None

            if original_menu_name:
                if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                    original_menu_file = os.path.join(self.shared_menus_dir, original_menu_name + '.py')
                else:
                    original_menu_file = os.path.join(self.project_menus_dir, self.flame_project_name, original_menu_name + '.py')
            else:
                original_menu_file = None

            return original_menu_file

        original_menu_file_path = get_original_menu_file_path(tab)
        #print('Original menu file path:', original_menu_file_path, '\n')

        # Crate dictionary of all tab settings
        tab_options_dict = get_tab_settings(tab)

        def get_main_tab_values(tab_options_dict: dict) -> tuple:
            """
            Get Main Tab Values
            ===================

            Get values from main tab from tab options dictionary.

            Args:
            -----
                tab_options_dict (dict):
                    tab settings

            Returns:
            --------
                menu_visibility, menu_name, reveal_in_mediahub, reveal_in_finder (tuple):
                    menu_visibility (str): 'Project' or 'Shared'
                    menu_name (str): menu name
                    reveal_in_mediahub (str): 'True' or 'False'
                    reveal_in_finder (str): 'True' or 'False'
            """

            # Get values from main tab
            for key, value in tab_options_dict.items():
                if 'tab_zero' in key:
                    menu_visibility = value['Menu Visibility']
                    menu_name = value['Menu Name']
                    reveal_in_mediahub = str(value['Reveal in MediaHub'])
                    reveal_in_finder = str(value['Reveal in Finder'])

            return menu_visibility, menu_name, reveal_in_mediahub, reveal_in_finder

        # Get values from main tab
        menu_visibility, menu_name, reveal_in_mediahub, reveal_in_finder = get_main_tab_values(tab_options_dict)

        # Check preset options for proper entries
        preset_error = preset_check(tab_options_dict)
        if preset_error:
            PyFlameMessageWindow(
                message=f'{preset_error}',
                message_type=MessageType.ERROR,
                parent=None,
            )
            return

        # Get menu save path and name
        menu_flame_project, menu_save_path = get_menu_save_path()

        # Create dict of tokens from main tab settings
        main_tab_token_dict = create_main_tab_token_dict()

        def load_menu_template() -> list:
            """
            Load Menu Template
            ==================

            Open menu template and return as list of lines.

            Returns:
            --------
                template_lines (list):
                    menu template lines
            """

            # Open menu template
            get_config_values = open(self.menu_template_path, 'r')
            template_lines = get_config_values.read().splitlines()
            get_config_values.close()

            return template_lines

        # Load menu template
        template_lines = load_menu_template()

        def replace_main_tab_tokens() -> list:
            """
            Replace Main Tab Tokens
            =======================

            Replace tokens in menu template with values from main tab token dictionary.

            Returns:
            --------
                template_lines (list):
                    menu template lines with tokens replaced
            """


            # Replace tokens in menu template
            for key, value in main_tab_token_dict.items():
                for line in template_lines:
                    if key in line:
                        line_index = template_lines.index(line)
                        new_line = re.sub(key, value, line)
                        template_lines[line_index] = new_line

            return template_lines

        # Replace tokens with values from main tab token dictionary
        template_lines = replace_main_tab_tokens()

        # Create new export preset menu lines
        menu_lines = menu_template_preset_lines(tab_options_dict)

        def insert_menu_lines() -> list:
            """
            Insert Menu Lines
            =================

            Insert new preset menu lines into template.

            Returns:
            --------
                template_lines (list):
                    template lines with new preset menu lines inserted
            """

            # Insert new preset menu lines into template
            for i in range(len(template_lines)):
                if template_lines[i] == '    for clip in selection:':
                    i += 1
                    for line in menu_lines:
                        template_lines.insert(i, line)
                        i += 1

            return template_lines

        template_lines = insert_menu_lines()

        def delete_original_menu_file() -> None:
            """
            Delete Original Menu File
            =========================

            Delete original menu file if tab is 'Edit'.
            """

            if original_menu_file_path:
                os.remove(original_menu_file_path)
                try:
                    os.remove(original_menu_file_path + 'c')
                except:
                    pass

        # Delete original menu file if tab is 'Edit' before saving new menu.
        delete_original_menu_file()

        def save_export_menu():
            # Save new menu
            out_file = open(menu_save_path, 'w')
            for line in template_lines:
                print(line, file=out_file)
            out_file.close()

        if os.path.isfile(menu_save_path):
            overwrite = PyFlameMessageWindow(
                message=f'Export menu already exists.\n\nDo you want to overwrite it?',
                message_type=MessageType.WARNING,
                title='Export Menu Error',
                parent=None,
            )
            if not overwrite:
                return

        # Save new menu file
        save_export_menu()

        # Save config settings
        save_config()

        # Refresh python hooks
        pyflame.refresh_hooks()

        PyFlameMessageWindow(
            message=f'Export Menu Saved: {menu_name}',
            parent=None,
            )

        self.get_saved_menus()
        self.load_preset(preset_to_load=f'{menu_visibility}: {menu_name}')

#-------------------------------------
# [Flame Menus]
#-------------------------------------

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
                    'name': 'Create Export Menus',
                    'execute': ExportMenuSetup,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
