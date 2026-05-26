# Create Export Menus
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
Script Name: Create Export Menus
Script Version: 5.5.0
Flame Version: 2026
Written by: Michael Vaglienty
Creation Date: 03.29.20
Update Date: 05.25.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Create custom right-click export menu's from saved export presets

URL:

    https://logik-portal.com/scripts/#create_export_menus

Menus:

    To create or edit export menus:
        Flame Main Menu -> Logik Portal -> Logik Portal Script Setup -> Create Export Menus

    To access newly created menus:
        Right-click on clip -> Project Export Presets... -> Select export
        Right-click on clip -> Shared Export Presets... -> Select export

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v5.5.0 05.25.26
        - Added Import Export button. When checked, exported clip will be imported back into Flame.
          Only works with Movie preset types.

    v5.4.1 02.27.26
        - Fixed issue when trying to save more than one export to a menu.

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

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re
import shutil
from functools import partial
from typing import Any

import flame
from lib.pyflame_lib_create_export_menus import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Create Export Menus'
SCRIPT_VERSION = 'v5.5.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# Widget keys for preset tab dicts (self.create_tab_widgets / self.edit_tab_widgets).
# All keys that toggle_ui / get_preset_info / disable_ui_elements operate on.
_TW_TOGGLEABLE = (
    'preset_type_label',
    'presets_label',
    'export_path_label',
    'export_path_entry',
    'top_layer_pushbutton',
    'foreground_pushbutton',
    'between_marks_pushbutton',
    'import_export_pushbutton',
    'token_pushbutton',
    'preset_type_menu',
    'path_browse_button',
    'presets_menu',
    'include_subtitles_pushbutton',
    'subtitles_export_mode_menu',
    'subtitles_tracks_menu',
)

# Subset of _TW_TOGGLEABLE used by no_presets_found() for tab 0 (excludes subtitle widgets)
_TW_TAB0_NO_PRESETS = (
    'preset_type_label',
    'presets_label',
    'export_path_label',
    'export_path_entry',
    'top_layer_pushbutton',
    'foreground_pushbutton',
    'between_marks_pushbutton',
    'import_export_pushbutton',
    'token_pushbutton',
    'preset_type_menu',
    'path_browse_button',
    'presets_menu',
)

# ==============================================================================
# [Main Script]
# ==============================================================================

class ExportMenuSetup:

    # ---------------------------------------------------------------------------
    # Class-level attribute declarations
    # These are set by get_saved_preset_lists() and setup_window() at runtime.
    # Declared here so static type checkers know they are valid class attributes.
    # ---------------------------------------------------------------------------

    # Preset list attributes - set by get_saved_preset_lists()
    project_movie_preset_list:    list
    project_file_seq_preset_list: list
    shared_movie_preset_list:     list
    shared_file_seq_preset_list:  list

    # Create-tab widget attributes - set by setup_window()
    window:                       Any
    main_tabs:                    Any
    create_preset_tabs:           Any
    create_tab_widgets:           list
    menu_visibility_label:        Any
    menu_name_label:              Any
    current_preset_label:         Any
    after_export_label:           Any
    menu_name_entry:              Any
    menu_visibility_menu:         Any
    reveal_in_mediahub_pushbutton: Any
    reveal_in_finder_pushbutton:  Any
    create_button:                Any
    done_button:                  Any

    # Edit-tab widget attributes - set by setup_window()
    edit_preset_tabs:                    Any
    edit_tab_widgets:                    list
    edit_menu_label:                     Any
    edit_menu_visibility_label:          Any
    edit_menu_name_label:                Any
    edit_current_preset_label:           Any
    edit_after_export_label:             Any
    edit_menu_name_entry:                Any
    edit_saved_export_menu_menu:         Any
    edit_menu_visibility_menu:           Any
    edit_reveal_in_mediahub_pushbutton:  Any
    edit_reveal_in_finder_pushbutton:    Any
    edit_delete_button:                  Any
    edit_duplicate_button:               Any
    edit_save_button:                    Any
    edit_done_button:                    Any

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Load config file
        self.settings = self.load_config()

        # Get current flame version values
        self.flame_version = pyflame.get_flame_version()
        self.flame_min_max_version = str(self.flame_version)[:4]

        # Get current project name
        self.flame_project_name = flame.project.current_project.name

        # Create export preset menu folders if they don't exist.
        self.project_menus_dir, self.shared_menus_dir = self.create_menu_folders()

        # Paths
        self.menu_template_path = os.path.join(SCRIPT_PATH, 'assets/templates/menu_template')
        self.current_project_created_presets_path = os.path.join(SCRIPT_PATH, 'project_menus', self.flame_project_name)
        self.project_preset_path = self.get_project_preset_path()
        self.shared_preset_path = '/opt/Autodesk/shared/export/presets'

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
                'import_export': False,
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

        project_preset_path = f'/opt/Autodesk/project/{self.flame_project_name}/export/presets/flame'

        # If path doesn't exist then project may not be saved to default location.
        # Try to get project path from project.db file. This doesn't work 2025+.
        if not os.path.isdir(project_preset_path):
            try:
                with open('/opt/Autodesk/project/project.db', 'r') as f:
                    values = f.read().splitlines()
                project_line = [line for line in values if 'Project:' + self.flame_project_name in line][0]
                project_line = project_line.split('SetupDir="', 1)[1]
                project_line = project_line.split('"', 1)[0]
                project_preset_path = os.path.join(project_line, 'export/presets/flame')
            except Exception:
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

                If preset version is less than or equal to current export version then return True.

                Args:
                -----
                    path (str):
                        Path to export preset.

                Returns:
                --------
                    bool: True if preset is compatible with current version of flame. False if not.
                """

                current_export_version, export_version = pyflame.get_export_preset_version(path)
                return current_export_version <= export_version

            try:
                compatible_preset_list = []
                preset_list = []

                for root, dirs, files in os.walk(preset_path):
                    for file in files:
                        if file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            file = file_path.rsplit(preset_path + '/', 1)[1]
                            preset_list.append(file)

                for preset in preset_list:
                    path = os.path.join(preset_path, preset)
                    if check_preset_version(path):
                        compatible_preset_list.append(preset[:-4])
                compatible_preset_list = sorted(compatible_preset_list)
                return compatible_preset_list
            except Exception:
                return []

        self.project_movie_preset_list    = get_compatible_preset_list(self.project_movie_preset_path)
        self.project_file_seq_preset_list = get_compatible_preset_list(self.project_file_seq_preset_path)
        self.shared_movie_preset_list     = get_compatible_preset_list(self.shared_movie_preset_path)
        self.shared_file_seq_preset_list  = get_compatible_preset_list(self.shared_file_seq_preset_path)

        print('\nSaved Export Presets:\n')

        # Print each preset list to the terminal for debugging
        preset_labels = [
            ('Project Movie Preset List',    self.project_movie_preset_list),
            ('Project File Seq Preset List', self.project_file_seq_preset_list),
            ('Shared Movie Preset List',     self.shared_movie_preset_list),
            ('Shared File Seq Preset List',  self.shared_file_seq_preset_list),
        ]
        for label, preset_list in preset_labels:
            self.print_list(label, preset_list)

    def print_list(self, list_name, items) -> None:
        """
        Print list
        ==========

        Print list of items to terminal.

        Args:
        -----
            list_name (str):
                List name.
            items (list):
                List of items.
        """

        print(f'    {list_name}:')
        if items:
            for x in items:
                print(f'        {x}')
        else:
            print('        None found')
        print('\n')

    #-------------------------------------

    def setup_window(self) -> None:
        """
        Setup Window
        ============

        Build and display the main setup window.

        Creates the Create and Edit tabs, each with up to five export preset tabs.
        All widget references are stored as instance attributes so they can be
        accessed from other methods.
        """

        def export_preset_tab(
            tab,
            tab_number,
            export_path,
            top_layer,
            export_foreground,
            export_between_marks,
            import_export,
            include_subtitles,
            subtitles_export_mode,
            subtitles_tracks,
            ) -> dict:
            """
            Export Preset Tab
            =================

            Create the export preset tab layout.

            Args:
            -----
                tab (PyFlameTabWidget.TabContainer):
                    The tab to create the layout in.
                tab_number (str):
                    The tab number ('one' through 'five').
                export_path (str):
                    The export path.
                top_layer (bool):
                    Set state of top layer pushbutton.
                export_foreground (bool):
                    Set state of export foreground pushbutton.
                export_between_marks (bool):
                    Set state of export between marks pushbutton.
                import_export (bool):
                    Set state of import export pushbutton.
                include_subtitles (bool):
                    Set state of include_subtitles pushbutton.
                subtitles_export_mode (str):
                    Button text.
                subtitles_tracks (str):
                    Button text.

            Returns:
            --------
                dict:
                    Widget dict for this preset tab.
            """

            def set_preset_menu() -> None:
                """
                Update the saved presets menu based on the preset type menu selection.
                """

                preset_map = {
                    'Project: Movie':         self.project_movie_preset_list,
                    'Project: File Sequence': self.project_file_seq_preset_list,
                    'Shared: Movie':          self.shared_movie_preset_list,
                    'Shared: File Sequence':  self.shared_file_seq_preset_list,
                }
                preset_list = preset_map.get(saved_preset_type_menu.text, [])
                saved_presets_menu.update_menu(
                    text=preset_list[0] if preset_list else 'No Saved Presets Found',
                    menu_options=preset_list,
                    )
                update_import_export_state()

            def toggle_ui() -> None:
                """
                Toggle UI
                =========

                Enable/Disable UI elements based on the state of the enable preset pushbutton.
                Only called for tabs 2-5, which always have an enable pushbutton.
                """

                if enable_preset_pushbutton is None:
                    return
                switch = enable_preset_pushbutton.checked
                for widget in [
                    saved_preset_type_label, saved_presets_label, export_path_label,
                    export_path_entry, top_layer_pushbutton, foreground_pushbutton,
                    between_marks_pushbutton, token_pushbutton, saved_preset_type_menu,
                    path_browse_button, saved_presets_menu, include_subtitles_pushbutton,
                    subtitles_export_mode_menu, subtitles_tracks_menu,
                    ]:
                    widget.enabled = switch
                if not switch:
                    import_export_pushbutton.enabled = False
                    import_export_pushbutton.checked = False
                else:
                    update_import_export_state()

            def subtitles_ui_toggle() -> None:
                """
                Subtitles UI Toggle
                ===================

                Enable or disable subtitle buttons/menus based on the Include Subtitles button state.
                """

                subtitles_export_mode_menu.enabled = include_subtitles_pushbutton.checked
                subtitles_tracks_menu.enabled = include_subtitles_pushbutton.checked

            def update_import_export_state() -> None:
                """
                Update Import Export State
                ==========================

                Enable or disable the Import Export pushbutton based on the Saved Preset
                Type menu selection. Movie preset types enable the button; File Sequence
                types disable it and clear its checked state.
                """

                if enable_preset_pushbutton is not None and not enable_preset_pushbutton.checked:
                    import_export_pushbutton.enabled = False
                    import_export_pushbutton.checked = False
                    return
                if saved_preset_type_menu.text in ('Project: Movie', 'Shared: Movie'):
                    import_export_pushbutton.enabled = True
                else:
                    import_export_pushbutton.enabled = False
                    import_export_pushbutton.checked = False

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
            import_export_pushbutton = PyFlamePushButton(
                text='Import Export',
                checked=import_export,
                tooltip='Import exported clip back into Flame - Only works with Movie preset types.',
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
                    'Project Name':      '<ProjectName>',
                    'Project Nick Name': '<ProjectNickName>',
                    'Shot Name':         '<ShotName>',
                    'SEQUENCE NAME':     '<SEQNAME>',
                    'Sequence Name':     '<SeqName>',
                    'Tape Name':         '<TapeName>',
                    'User Name':         '<UserName>',
                    'User Nickname':     '<UserNickName>',
                    'Clip Name':         '<ClipName>',
                    'Clip Resolution':   '<Resolution>',
                    'Clip Height':       '<ClipHeight>',
                    'Clip Width':        '<ClipWidth>',
                    'Year (YYYY)':       '<YYYY>',
                    'Year (YY)':         '<YY>',
                    'Month':             '<MM>',
                    'Day':               '<DD>',
                    'Hour (24 Hour)':    '<Hour>',
                    'Hour (12 Hour)':    '<hour>',
                    'Minute':            '<Minute>',
                    'AM/PM':             '<AMPM>',
                    'am/pm':             '<ampm>',
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
                Switch Subtitles Tracks Menu based on selection in Subtitles Export Mode Menu.
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
                text=subtitles_export_mode,
                menu_options=[
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

            # Set saved preset type menu when tab is created
            set_preset_menu()

            # Buttons
            path_browse_button = PyFlameButton(
                text='Browse',
                connect=partial(self.path_browse, export_path_entry, [self.window]),
                )

            # Toggle UI for tabs 2-5 (tab 1 has no enable pushbutton)
            if enable_preset_pushbutton:
                toggle_ui()

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
            tab.grid_layout.addWidget(path_browse_button, 3, 4)
            tab.grid_layout.addWidget(token_pushbutton, 3, 5)

            if tab_number != 'one':
                tab.grid_layout.addWidget(enable_preset_pushbutton, 0, 7)
            tab.grid_layout.addWidget(top_layer_pushbutton, 1, 7)
            tab.grid_layout.addWidget(foreground_pushbutton, 2, 7)
            tab.grid_layout.addWidget(between_marks_pushbutton, 3, 7)
            tab.grid_layout.addWidget(import_export_pushbutton, 4, 7)

            tab.grid_layout.addWidget(subtitles_label, 0, 8)
            tab.grid_layout.addWidget(include_subtitles_pushbutton, 1, 8)
            tab.grid_layout.addWidget(subtitles_export_mode_menu, 2, 8)
            tab.grid_layout.addWidget(subtitles_tracks_menu, 3, 8)

            return {
                'preset_type_menu':             saved_preset_type_menu,
                'presets_menu':                 saved_presets_menu,
                'export_path_entry':            export_path_entry,
                'enable_pushbutton':            enable_preset_pushbutton,
                'top_layer_pushbutton':         top_layer_pushbutton,
                'foreground_pushbutton':        foreground_pushbutton,
                'between_marks_pushbutton':     between_marks_pushbutton,
                'import_export_pushbutton':     import_export_pushbutton,
                'preset_type_label':            saved_preset_type_label,
                'presets_label':                saved_presets_label,
                'export_path_label':            export_path_label,
                'path_browse_button':           path_browse_button,
                'token_pushbutton':             token_pushbutton,
                'include_subtitles_pushbutton': include_subtitles_pushbutton,
                'subtitles_export_mode_menu':   subtitles_export_mode_menu,
                'subtitles_tracks_menu':        subtitles_tracks_menu,
            }

        def build_export_preset_tabs(tab_container) -> list:
            """
            Build Export Preset Tabs
            ========================

            Build 5 export preset tabs using export_preset_tab() and return a list of widget dicts.
            Tab 1 (index 0) loads settings from config. Tabs 2-5 default to empty/disabled.

            Args:
            -----
                tab_container (PyFlameTabWidget):
                    Tab widget containing the 5 export preset tab pages.

            Returns:
            --------
                list: List of 5 widget dicts, one per preset tab.
            """

            tab_names   = [
                'Export Preset One',
                'Export Preset Two',
                'Export Preset Three',
                'Export Preset Four',
                'Export Preset Five',
                ]
            tab_numbers = ['one', 'two', 'three', 'four', 'five']

            tab_widgets_list = []

            for i, (tab_name, tab_number) in enumerate(zip(tab_names, tab_numbers)):
                if i == 0:
                    tab_widgets = export_preset_tab(
                        tab=tab_container.tab_pages[tab_name],
                        tab_number=tab_number,
                        export_path=self.settings.export_path,
                        top_layer=self.settings.use_top_layer,
                        export_foreground=self.settings.export_in_foreground,
                        export_between_marks=self.settings.export_between_marks,
                        import_export=self.settings.import_export,
                        include_subtitles=self.settings.include_subtitles,
                        subtitles_export_mode=self.settings.subtitles_export_mode,
                        subtitles_tracks=self.settings.subtitles_tracks,
                        )
                else:
                    tab_widgets = export_preset_tab(
                        tab=tab_container.tab_pages[tab_name],
                        tab_number=tab_number,
                        export_path='',
                        top_layer=False,
                        export_foreground=False,
                        export_between_marks=False,
                        import_export=False,
                        include_subtitles=False,
                        subtitles_export_mode='Burn in Image',
                        subtitles_tracks='Current Subtitles Track',
                        )
                tab_widgets_list.append(tab_widgets)

            return tab_widgets_list

        def create_tab() -> None:
            """
            Create Tab
            ==========

            Tab for creating export presets.
            """

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
            self.create_button = PyFlameButton(
                text='Create',
                connect=partial(self.save_menus, 'Create'),
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

            self.create_tab_widgets = build_export_preset_tabs(self.create_preset_tabs)

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

            def delete_export_menu() -> None:
                """
                Delete export menu currently selected in the edit_saved_export_menu_menu.
                """

                menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]

                if PyFlameMessageWindow(
                    message=f'Delete preset: {menu_name}?',
                    message_type=MessageType.WARNING,
                    title=f'{SCRIPT_NAME}: Confirm Operation',
                    parent=None,
                    ):

                    if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                        menu_path = os.path.join(self.shared_menus_dir, menu_name)
                    else:
                        menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, menu_name)

                    os.remove(menu_path + '.py')
                    try:
                        os.remove(menu_path + '.pyc')
                    except Exception:
                        pass

                    pyflame.print(f'Menu deleted: {menu_name}')

                    self.get_saved_menus()

                    pyflame.refresh_hooks()

            def duplicate_preset() -> None:
                """
                Duplicate export menu currently selected in the Export Menus pushbutton menu.
                """

                menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]

                if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                    menu_path = os.path.join(self.shared_menus_dir, menu_name) + '.py'
                    menu_prefix = 'Shared: '
                else:
                    menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, menu_name) + '.py'
                    menu_prefix = 'Project: '

                # Add 'copy' to menu name and check for existing file. If exists, add ' copy' until unique name is found.
                new_menu_path = menu_path[:-3] + ' copy.py'
                while os.path.exists(new_menu_path):
                    new_menu_path = new_menu_path[:-3] + ' copy.py'

                shutil.copy(menu_path, new_menu_path)

                self.edit_saved_export_menu_menu.text = menu_prefix + new_menu_path.rsplit('/', 1)[1][:-3]

                self.load_preset()

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

            # Create edit preset tabs 1-5
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

            self.edit_tab_widgets = build_export_preset_tabs(self.edit_preset_tabs)

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

        menu_sources = [
            ('Project Export Menus', os.path.join(self.project_menus_dir, self.flame_project_name), 'Project: '),
            ('Shared Export Menus',  self.shared_menus_dir,                                         'Shared: '),
        ]

        all_export_menus = []

        for label, path, prefix in menu_sources:
            try:
                menus = sorted(
                    [prefix + x[:-3] for x in os.listdir(path) if x.endswith('.py')]
                    )
            except Exception:
                menus = []
            self.print_list(label, menus)
            all_export_menus.extend(menus)

        if not all_export_menus:
            all_export_menus = ['No Saved Export Menus Found']

        self.edit_saved_export_menu_menu.update_menu(
            text=all_export_menus[0],
            menu_options=all_export_menus,
            connect=self.load_preset,
            )

        if all_export_menus[0] != 'No Saved Export Menus Found':
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

            for widget in [
                self.edit_menu_label,
                self.edit_saved_export_menu_menu,
                self.edit_menu_visibility_label,
                self.edit_menu_visibility_menu,
                self.edit_menu_name_label,
                self.edit_menu_name_entry,
                self.edit_delete_button,
                ]:
                widget.enabled = False

            # Disable tab 0 (preset one) core widgets (subtitle widgets excluded - original behaviour)
            tab0 = self.edit_tab_widgets[0]
            for key in _TW_TAB0_NO_PRESETS:
                tab0[key].enabled = False

            # Disable enable pushbutton for tabs 2-5 (indices 1-4)
            for tab in self.edit_tab_widgets[1:]:
                tab['enable_pushbutton'].enabled = False

            self.edit_menu_visibility_menu.text = ''
            for tab in self.edit_tab_widgets:
                tab['preset_type_menu'].text = ''

            print('--> No existing presets found. \n')

        if self.edit_saved_export_menu_menu.text == 'No Saved Export Menus Found':
            no_presets_found()
            return

        elif preset_to_load:
            self.edit_saved_export_menu_menu.text = preset_to_load

        selected_menu_name = self.edit_saved_export_menu_menu.text.rsplit(': ', 1)[1]

        self.edit_menu_name_entry.text = selected_menu_name

        # Determine menu path from the visibility prefix ('Shared: ' or 'Project: ')
        selected_menu_path: str = ''
        if 'Shared: ' in self.edit_saved_export_menu_menu.text:
            self.edit_menu_visibility_menu.text = 'Shared'
            selected_menu_path = os.path.join(self.shared_menus_dir, selected_menu_name) + '.py'
        elif 'Project: ' in self.edit_saved_export_menu_menu.text:
            self.edit_menu_visibility_menu.text = 'Project'
            selected_menu_path = os.path.join(self.project_menus_dir, self.flame_project_name, selected_menu_name) + '.py'

        if not selected_menu_path:
            return

        # Read in menu script
        with open(selected_menu_path, 'r') as f:
            menu_lines = f.read().splitlines()

        def get_preset_info(preset_num: str, tab_widgets: dict) -> None:
            """
            Get Preset Info
            ===============

            Read preset data from menu_lines and populate the tab's UI widgets.

            Args:
            -----
                preset_num (str):
                    Preset number label used as a marker in the menu file (e.g. 'One').
                tab_widgets (dict):
                    Widget dict for the preset tab.
            """

            preset_start_index = menu_lines.index(f'        # Export preset {preset_num}')
            preset_end_index = menu_lines.index(f'        # Export preset {preset_num} END') + 1
            preset_lines = menu_lines[preset_start_index:preset_end_index]

            enable_btn = tab_widgets['enable_pushbutton']

            if enable_btn:
                enable_btn.checked = True
            for key in _TW_TOGGLEABLE:
                tab_widgets[key].enabled = True

            # Default import_export to False before parsing; stays False if line is absent (older presets)
            tab_widgets['import_export_pushbutton'].checked = False

            print(f'Preset: {preset_num}')
            for line in preset_lines:
                if line == '        clip_output.use_top_video_track = True':
                    tab_widgets['top_layer_pushbutton'].checked = True
                    print('Use Top Layer: True')
                elif line == '        clip_output.use_top_video_track = False':
                    tab_widgets['top_layer_pushbutton'].checked = False
                    print('Use Top Layer: False')
                elif line == '        clip_output.foreground = True':
                    tab_widgets['foreground_pushbutton'].checked = True
                    print('Foreground Export: True')
                elif line == '        clip_output.foreground = False':
                    tab_widgets['foreground_pushbutton'].checked = False
                    print('Foreground Export: False')
                elif line == '        clip_output.export_between_marks = True':
                    tab_widgets['between_marks_pushbutton'].checked = True
                    print('Export Between Marks: True')
                elif line == '        clip_output.export_between_marks = False':
                    tab_widgets['between_marks_pushbutton'].checked = False
                    print('Export Between Marks: False')
                elif '        new_export_path = translate_tokenized_path(clip, ' in line:
                    path = line.split("'", 2)[1]
                    tab_widgets['export_path_entry'].text = path
                    print('Export Path:', path)
                elif '        clip_output.export(clip, ' in line:
                    preset_path = line.split("'", 2)[1]
                    preset_name = preset_path.rsplit('/', 1)[1][:-4]
                    tab_widgets['presets_menu'].text = preset_name
                    print('Preset Name:', preset_name)
                elif '        clip_output.include_subtitles = True' in line:
                    tab_widgets['include_subtitles_pushbutton'].checked = True
                    tab_widgets['subtitles_export_mode_menu'].enabled = True
                    tab_widgets['subtitles_tracks_menu'].enabled = True
                    print('Include subtitles: True')
                elif '        clip_output.include_subtitles = False' in line:
                    tab_widgets['include_subtitles_pushbutton'].checked = False
                    tab_widgets['subtitles_export_mode_menu'].enabled = False
                    tab_widgets['subtitles_tracks_menu'].enabled = False
                    print('Include subtitles: False')
                elif '        clip_output.export_subtitles_as_files = False' in line:
                    tab_widgets['subtitles_export_mode_menu'].text = 'Burn in Image'
                    print('Subtitles export mode: Burn in Image')
                elif '        clip_output.export_subtitles_as_files = True' in line:
                    tab_widgets['subtitles_export_mode_menu'].text = 'Export as Files'
                    print('Subtitles export mode: Export as Files')
                elif '        clip_output.export_all_subtitles = True' in line:
                    tab_widgets['subtitles_tracks_menu'].text = 'All Subtitles Tracks'
                    print('Subtitles tracks: All Subtitles Tracks')
                elif '        clip_output.export_all_subtitles = False' in line:
                    tab_widgets['subtitles_tracks_menu'].text = 'Current Subtitles Track'
                    print('Subtitles tracks: Current Subtitles Track')
                elif line == '        import_export = True':
                    tab_widgets['import_export_pushbutton'].checked = True
                    print('Import Export: True')
                elif line == '        import_export = False':
                    tab_widgets['import_export_pushbutton'].checked = False
                    print('Import Export: False')

                if 'clip_output.export' in line:
                    if 'project' in line:
                        if 'file_sequence' in line:
                            tab_widgets['preset_type_menu'].text = 'Project: File Sequence'
                            print('Saved Preset Type: Project File Seq')
                        elif 'movie_file' in line:
                            tab_widgets['preset_type_menu'].text = 'Project: Movie'
                            print('Saved Preset Type: Project Movie File')
                    if 'shared' in line:
                        if 'file_sequence' in line:
                            tab_widgets['preset_type_menu'].text = 'Shared: File Sequence'
                            print('Saved Preset Type: Shared File Seq')
                        elif 'movie_file' in line:
                            tab_widgets['preset_type_menu'].text = 'Shared: Movie'
                            print('Saved Preset Type: Shared Movie File')

            # Enable Import Export only for Movie preset types; clear checked for File Sequence
            if tab_widgets['preset_type_menu'].text in ('Project: Movie', 'Shared: Movie'):
                tab_widgets['import_export_pushbutton'].enabled = True
            else:
                tab_widgets['import_export_pushbutton'].enabled = False
                tab_widgets['import_export_pushbutton'].checked = False
                print('Import Export: disabled (File Sequence preset)')

        def disable_ui_elements(tab_widgets: dict) -> None:
            """
            Disable UI Elements
            ===================

            Disable all UI elements for a preset tab that failed to load.

            Args:
            -----
                tab_widgets (dict):
                    Widget dict for the preset tab.
            """

            tab_widgets['enable_pushbutton'].checked = False
            tab_widgets['export_path_entry'].text = ''
            for key in _TW_TOGGLEABLE:
                tab_widgets[key].enabled = False

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

        # Load preset info for tab 1 (always present)
        tab_preset_nums = ['One', 'Two', 'Three', 'Four', 'Five']

        get_preset_info(tab_preset_nums[0], self.edit_tab_widgets[0])
        preset_menu_texts = [self.edit_tab_widgets[0]['presets_menu'].text]

        # Load preset info for tabs 2-5; disable tab if preset not found in the menu file
        for i in range(1, 5):
            try:
                get_preset_info(tab_preset_nums[i], self.edit_tab_widgets[i])
                preset_menu_texts.append(self.edit_tab_widgets[i]['presets_menu'].text)
            except Exception:
                disable_ui_elements(self.edit_tab_widgets[i])
                preset_menu_texts.append(None)

        # Restore preset menu texts (they may be overwritten during the export type detection pass)
        for i, text in enumerate(preset_menu_texts):
            if text is not None:
                self.edit_tab_widgets[i]['presets_menu'].text = text

        print('\n--> Existing export presets loaded.\n')

    def path_browse(self, entry: PyFlameEntry, window_to_hide: list) -> None:
        """
        Path Browse
        ===========

        Opens a file browser dialog to select a path and sets the entry text to the selected path.

        Args:
            entry (PyFlameEntry): Entry widget to set the path text.
            window_to_hide (list): List containing the window to hide while the file browser dialog is open.
        """

        try:
            path = pyflame.file_browser(
                path=entry.text,
                title='Select Directory',
                select_directory=True,
                window_to_hide=window_to_hide,
                )

            if path:
                entry.text = str(path)
        except Exception as e:
            print(f'An error occurred while browsing for a directory: {e}')

    def save_menus(self, tab) -> None:
        """
        Save Menus
        ==========

        Build and save a Flame right-click export menu Python script from the current UI settings.

        Called when the user clicks the Create or Save button. Collects settings from all
        preset tabs, validates them, generates the menu script from the template, and writes
        it to either the project or shared menus directory.

        Args:
        -----
            tab (str):
                'Create' when saving a new menu, 'Edit' when overwriting an existing one.
        """

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
                prefix = 'create'
                tab_widgets_list = self.create_tab_widgets
                visibility_menu  = self.menu_visibility_menu
                menu_name_entry  = self.menu_name_entry
                reveal_mediahub  = self.reveal_in_mediahub_pushbutton
                reveal_finder    = self.reveal_in_finder_pushbutton
            else:
                prefix = 'edit'
                tab_widgets_list = self.edit_tab_widgets
                visibility_menu  = self.edit_menu_visibility_menu
                menu_name_entry  = self.edit_menu_name_entry
                reveal_mediahub  = self.edit_reveal_in_mediahub_pushbutton
                reveal_finder    = self.edit_reveal_in_finder_pushbutton

            settings_dict = {
                f'{prefix}_tab_zero': {
                    'Menu Visibility':    visibility_menu.text,
                    'Menu Name':          menu_name_entry.text,
                    'Reveal in MediaHub': reveal_mediahub.checked,
                    'Reveal in Finder':   reveal_finder.checked,
                    },
                }

            tab_names = ['one', 'two', 'three', 'four', 'five']

            for i, name in enumerate(tab_names):
                tw = tab_widgets_list[i]
                settings_dict[f'{prefix}_tab_{name}'] = {
                    'Enabled':               True if i == 0 else tw['enable_pushbutton'].checked,
                    'Preset Type Menu':      tw['preset_type_menu'].text,
                    'Preset Menu':           tw['presets_menu'].text,
                    'Export Path':           tw['export_path_entry'].text,
                    'Top Layer':             tw['top_layer_pushbutton'].checked,
                    'Foreground Export':     tw['foreground_pushbutton'].checked,
                    'Export Between Marks':  tw['between_marks_pushbutton'].checked,
                    'Import Export':         tw['import_export_pushbutton'].checked,
                    'Include Subtitles':     tw['include_subtitles_pushbutton'].checked,
                    'Subtitles Export Mode': tw['subtitles_export_mode_menu'].text,
                    'Subtitles Tracks':      tw['subtitles_tracks_menu'].text,
                    }

            return settings_dict

        def preset_check(tab_options_dict: dict) -> str | None:
            """
            Preset Check
            ============

            Check settings for each tab and return error message if any are found.
            Returns None if all settings are valid.

            Args:
            -----
                tab_options_dict (dict):
                    tab settings

            Returns:
            --------
                str | None: error message, or None if no errors found
            """

            main_tab = str(next(iter(tab_options_dict))).split('_', 1)[0]

            if main_tab == 'create':
                if not self.menu_name_entry.text:
                    return 'Add menu name'
                visibility_text = self.menu_visibility_menu.text
            else:
                if not self.edit_menu_name_entry.text:
                    return 'Add menu name'
                visibility_text = self.edit_menu_visibility_menu.text

            for key, value in tab_options_dict.items():
                tab_number = key.rsplit('_', 1)[1].capitalize()
                if tab_number != 'Zero':

                    if value['Enabled']:

                        if 'Shared' in visibility_text and 'Shared:' not in value['Preset Type Menu']:
                            return f'Preset {tab_number}: Only a SHARED Saved Preset can be added to a Menu with Shared Menu Visibility.'

                        if value['Preset Menu'] == 'No Saved Presets Found':
                            return f'Preset {tab_number}: No saved preset selected. Select a different Preset Type or save a preset in Flame.'

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

            return {
                '<FlameProject>':       menu_flame_project,
                '<PresetName>':         menu_name,
                '<PresetType>':         menu_visibility,
                '<RevealInMediaHub>':   reveal_in_mediahub,
                '<RevealInFinder>':     reveal_in_finder,
                '<FlameMinMaxVersion>': self.flame_min_max_version,
                }

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

                if 'Project' in preset_type_menu:
                    preset_path = self.project_preset_path
                else:
                    preset_path = self.shared_preset_path

                if 'Movie' in preset_type_menu:
                    preset_dir_path = preset_path + '/movie_file'
                else:
                    preset_dir_path = preset_path + '/file_sequence'

                return os.path.join(preset_dir_path, preset_menu) + '.xml'

            def new_lines(tab_number: str,
                          top_layer: str,
                          foreground_export: str,
                          export_between_marks: str,
                          import_export_value: bool,
                          include_subtitles: str,
                          subtitles_export_mode: str,
                          subtitles_tracks: str,
                          export_path: str,
                          preset_file_path: str) -> None:
                """
                Build new lines to be added to menu template.
                Appends generated lines to the outer ``menu_lines`` list in place.
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

                menu_lines.append("")
                menu_lines.append("        # Include subtitles")
                menu_lines.append(f"        clip_output.include_subtitles = {include_subtitles}")
                menu_lines.append(f"        print('--> Include subtitles: {include_subtitles}\\n')")
                menu_lines.append("")
                # Convert menu text selections to the bool values used in the generated script
                export_as_files = subtitles_export_mode != 'Burn in Image'
                export_all_tracks = subtitles_tracks == 'All Subtitles Tracks'
                menu_lines.append("        # Subtitles export mode")
                menu_lines.append(f"        clip_output.export_subtitles_as_files = {export_as_files}")
                menu_lines.append(f"        print('--> Subtitles export mode: {export_as_files}\\n')")
                menu_lines.append("")
                menu_lines.append("        # Subtitles tracks")
                menu_lines.append(f"        clip_output.export_all_subtitles = {export_all_tracks}")
                menu_lines.append(f"        print('--> Subtitles tracks: {export_all_tracks}\\n')")

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
                menu_lines.append(f"        import_export = {import_export_value}")
                menu_lines.append("")
                menu_lines.append(f"        if import_export:")
                menu_lines.append(f"            # Drop a marker file in the export directory to capture the server's clock")
                menu_lines.append(f"            marker_fd, marker_path = tempfile.mkstemp(prefix='.flame_export_marker_', dir=new_export_path)")
                menu_lines.append(f"            os.close(marker_fd)")
                menu_lines.append(f"            export_start_time = os.path.getmtime(marker_path)")
                menu_lines.append(f"            os.remove(marker_path)")
                menu_lines.append("")

                menu_lines.append(f"        clip_output.export(clip, '{preset_file_path}', new_export_path)")
                menu_lines.append("")

                menu_lines.append(f"        if import_export:")
                menu_lines.append(f"            # Walk the entire tree to find .mov files modified at or after the marker's timestamp")
                menu_lines.append(f"            exported_files = []")
                menu_lines.append(f"            for dirpath, dirnames, filenames in os.walk(new_export_path):")
                menu_lines.append(f"                for f in filenames:")
                menu_lines.append(f"                    if f.lower().endswith('.mov'):")
                menu_lines.append(f"                        full_path = os.path.join(dirpath, f)")
                menu_lines.append(f"                        if os.path.getmtime(full_path) >= export_start_time:")
                menu_lines.append(f"                            exported_files.append(full_path)")
                menu_lines.append(f"            for path in sorted(exported_files):")
                menu_lines.append(f"                flame.import_clips(path, clip.parent)")
                menu_lines.append(f"                pyflame.print('Imported clip back into Flame.')")
                menu_lines.append("")

                menu_lines.append(f"        # Export preset {tab_number} END")
                menu_lines.append("")

            menu_lines = []

            print('tab options dict:', tab_options_dict, '\n')

            for key, value in tab_options_dict.items():
                tab_number = key.rsplit('_', 1)[1].capitalize()
                if tab_number != 'Zero':
                    if value['Enabled']:
                        preset_file_path = get_preset_path(value['Preset Type Menu'], value['Preset Menu'])
                        new_lines(
                            tab_number,
                            value['Top Layer'],
                            value['Foreground Export'],
                            value['Export Between Marks'],
                            value['Import Export'],
                            value['Include Subtitles'],
                            value['Subtitles Export Mode'],
                            value['Subtitles Tracks'],
                            value['Export Path'],
                            preset_file_path,
                            )

            return menu_lines

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings from main tab to config file.
            """

            tw = self.create_tab_widgets[0]
            self.settings.save_config(
                config_values={
                    'export_path':           tw['export_path_entry'].text,
                    'use_top_layer':         tw['top_layer_pushbutton'].checked,
                    'export_in_foreground':  tw['foreground_pushbutton'].checked,
                    'export_between_marks':  tw['between_marks_pushbutton'].checked,
                    'import_export':         tw['import_export_pushbutton'].checked,
                    'reveal_in_mediahub':    self.reveal_in_mediahub_pushbutton.checked,
                    'reveal_in_finder':      self.reveal_in_finder_pushbutton.checked,
                    }
                )

        def get_original_menu_file_path(tab: str) -> str | None:
            """
            Get Original Menu File Path
            ===========================

            Get path to the original menu file when editing an existing menu.
            Returns None when creating a new menu (tab is not 'Edit').

            Args:
            -----
                tab (str):
                    'Create' or 'Edit'

            Returns:
            --------
                str | None:
                    original menu file path, or None if tab is not 'Edit'
            """

            if tab != 'Edit':
                return None

            original_menu_name = self.edit_saved_export_menu_menu.text.split(' ', 1)[1]

            if 'Shared: ' in self.edit_saved_export_menu_menu.text:
                return os.path.join(self.shared_menus_dir, original_menu_name + '.py')
            return os.path.join(self.project_menus_dir, self.flame_project_name, original_menu_name + '.py')

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

            with open(self.menu_template_path, 'r') as f:
                template_lines = f.read().splitlines()
            return template_lines

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

            for key, value in main_tab_token_dict.items():
                for idx, line in enumerate(template_lines):
                    if key in line:
                        template_lines[idx] = re.sub(key, value, line)

            return template_lines

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

            for i in range(len(template_lines)):
                if template_lines[i] == '    for clip in selection:':
                    i += 1
                    for line in menu_lines:
                        template_lines.insert(i, line)
                        i += 1

            return template_lines

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
                except Exception:
                    pass

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
                menu_visibility, menu_name, reveal_in_mediahub, reveal_in_finder (tuple)
            """

            # Initialise with empty defaults; overwritten by the 'tab_zero' entry below
            menu_visibility    = ''
            menu_name          = ''
            reveal_in_mediahub = ''
            reveal_in_finder   = ''

            for key, value in tab_options_dict.items():
                if 'tab_zero' in key:
                    menu_visibility    = value['Menu Visibility']
                    menu_name          = value['Menu Name']
                    reveal_in_mediahub = str(value['Reveal in MediaHub'])
                    reveal_in_finder   = str(value['Reveal in Finder'])

            return menu_visibility, menu_name, reveal_in_mediahub, reveal_in_finder

        original_menu_file_path = get_original_menu_file_path(tab)

        tab_options_dict = get_tab_settings(tab)

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

        menu_flame_project, menu_save_path = get_menu_save_path()

        main_tab_token_dict = create_main_tab_token_dict()

        template_lines = load_menu_template()

        template_lines = replace_main_tab_tokens()

        menu_lines = menu_template_preset_lines(tab_options_dict)

        template_lines = insert_menu_lines()

        delete_original_menu_file()

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
        with open(menu_save_path, 'w') as f:
            for line in template_lines:
                print(line, file=f)

        save_config()

        pyflame.refresh_hooks()

        PyFlameMessageWindow(
            message=f'Export Menu Saved: {menu_name}',
            parent=None,
            )

        self.get_saved_menus()
        self.load_preset(preset_to_load=f'{menu_visibility}: {menu_name}')

# ==============================================================================
# [Flame Menus]
# ==============================================================================

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
                    'minimumVersion': '2026'
               }
           ]
        }
    ]
