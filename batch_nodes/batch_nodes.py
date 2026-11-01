# Batch Nodes
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Batch Nodes
Script Version: 3.13.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 04.18.20
Update Date: 10.28.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch / Flame Main Menu

Description:

    Add menus to batch right-click for your favorite nodes in batch.

Usage:

    Works with standard batch nodes/matchboxes/ofx.

    OFX can only be added by right clicking on an existing node in batch.

    Nodes added by right-clicking on them in batch will be saved with current node settings.

    All created node menu scripts are saved in /opt/Autodesk/shared/python/batch_nodes/menus

    Menus can be renamed and removed from the node list in the Batch Nodes setup window.

    Before a menu is overwritten, replaced or removed, a confirmation window is shown.

    Renamed menus can not contain slashes, backslashes or quotes. Node names used with Create Menu for Selected Node can not contain slashes or quotes.

URL:

    https://logik-portal.com/scripts/batch_nodes

Menus:

    To create/rename/delete menus from node lists:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Batch Nodes Setup

    To create menus for nodes with settings applied in batch:
        Right-click on node in batch -> Batch Nodes... -> Create Menu for Selected Node

    To create menus for ofx nodes:
        Right-click on node in batch -> Batch Nodes... -> Create Menu for Selected Node

    To add node from menu to batch:
        Right-click in batch -> Batch Nodes... -> Select Node to be added

    To add node from menu to batch connected to selected node:
        Right-click on node in batch -> Batch Nodes... -> Select Node to be added

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.13.0 10.28.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Create Menu for Selected Node now stops with an error if the node name contains a quote or slash.
        - Adding a menu from the Setup window now asks before overwriting an existing menu, and removes the old saved setup folder when a saved-setup menu is replaced.
        - Remove now deletes only the selected menus' own files and setup folders, not other menus whose names contain them, and asks for confirmation first.
        - Renaming a menu to the name of another existing menu now asks before replacing it. Names with slashes, backslashes or quotes are rejected before anything changes, and if the rename still fails partway the changes are undone.
        - Renaming a menu now only changes the menu name in the menu script, not matching text in its code or path.
        - Create Menu for Selected Node now asks before overwriting an existing menu that has no saved setup folder.
        - Setup window now opens when the Matchbox shaders folder for the current Flame version is missing.
        - Script now stops cleanly if the install check fails.

    v3.12.0 05.15.26
        - Updated to PyFlameLib v5.3.1.

    v3.11.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Bug fixes to batch nodes menu.
        - Window layer order in linux is now fixed.

    v3.10.0 03.11.25
        - Updated to PyFlameLib v4.3.0.
        - Fixed misc bugs.

    v3.9.0 01.04.25
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v3.8.0 08.14.24
        - Updated to PyFlameLib v3.0.0.

    v3.7.0 01.21.24
        - Updates to UI/PySide.

    v3.6.0 08.13.23
        - Updated to PyFlameLib v2.0.0.

    v3.5.1 06.28.23
        - Updated version naming to semantic versioning.
        - Main window tabs no longer have outline around names when selected in linux.

    v3.5 02.04.23
        - Updated menus for Flame 2023.2+
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.

    v3.4 05.31.22
        - Messages print to Flame message window - Flame 2023.1+
        - Flame file browser used to select folders - Flame 2023.1+
        - Misc bug fixes.

    v3.3 03.31.22
        - UI widgets moved to external file
        - Misc bug fixes

    v3.2 03.07.22
        - Updated UI for Flame 2023

    v3.1 10.26.21
        - Updated config to xml

    v3.0 05.20.21
        - Updated to be compatible with Flame 2022/Python 3.7

    v2.5 01.27.21
        - Updated UI
        - Menus/Nodes can be renamed after they've been added

    v2.1 05.17.20:
        - Misc code updates
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os
import re
import shutil
from functools import partial

import flame
from lib.pyflame_lib_batch_nodes import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Batch Nodes'
SCRIPT_VERSION = 'v3.13.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class BatchNodes:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        self.script_installed = pyflame.verify_script_install()
        if not self.script_installed:
            return

        #  Init variables
        self.create_node_line = ''
        self.selection = selection
        self.node_name = ''

        # Set paths
        self.save_selected_template = os.path.join(SCRIPT_PATH, 'assets/templates', 'save_selected')
        self.create_node_template = os.path.join(SCRIPT_PATH, 'assets/templates', 'create_node')

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Get flame variables
        self.flame_version = flame.get_version()
        self.current_user = flame.users.current_user.name
        self.matchbox_path = f'/opt/Autodesk/presets/{self.flame_version}/matchbox/shaders'

        # Check/create folder to store node scripts in user python folder
        self.node_dir = os.path.join('/opt/Autodesk/shared/python/batch_nodes/menus')
        if not os.path.isdir(self.node_dir):
            os.makedirs(self.node_dir)
            pyflame.print(f'Created User Node Folder: {self.node_dir}', text_color=TextColor.GREEN)

        if not os.path.isdir(self.settings.logik_path):
            pyflame.print('Logik Matchbox Path No Longer Exists. Set New Path In Setup.', text_color=TextColor.YELLOW)
            self.settings.logik_path = '/'

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
                'logik_path': '/'
                }
            )

        return settings

    def main_window(self):

        def close_window():

            self.window.close()

        # Create main window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            escape_pressed=close_window,
            return_pressed=self.done_button,
            grid_layout_columns=5,
            grid_layout_rows=2,
            parent=None,
            )

        self.tabs = PyFlameTabWidget(
            tab_names=[
                'Batch Nodes',
                'Matchbox',
                'Logik Matchbox',
                ],
            grid_layout_columns=5,
            grid_layout_rows=12,
            )

        # Load Tabs
        self.batch_node_tab()
        self.matchbox_tab()
        self.logik_tab()

        # Add Tab Widget to Main Window
        self.window.grid_layout.addWidget(self.tabs, 0, 0, 5, 12)

        self.window.center_window()

    def batch_node_tab(self):
        """
        Batch Node Tab
        ==============
        """

        def add_batch_node():

            # Create scripts for nodes in selected list
            for node in self.batch_node_list.selected_items:
                self.node_name = node.text()
                self.create_node_line = f"new_node = flame.batch.create_node('{self.node_name}')"
                self.create_node()

            # Refresh node menu lists
            self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

        # Labels
        self.batch_node_menu_label = PyFlameLabel(
            text='Batch Node Menus',
            style=Style.UNDERLINE,
            )
        self.batch_node_list_label = PyFlameLabel(
            text='Batch Nodes',
            style=Style.UNDERLINE,
            )

        # Listboxes
        self.batch_node_menu_list = PyFlameListWidget()
        self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)

        self.batch_node_list = PyFlameListWidget()
        self.get_batch_node_list()

        # Buttons
        self.batch_add_btn = PyFlameButton(
            text='Add',
            connect=add_batch_node,
            )
        self.batch_remove_btn = PyFlameButton(
            text='Remove',
            connect=partial(self.remove_scripts, self.batch_node_menu_list),
            )
        self.batch_rename_btn = PyFlameButton(
            text='Rename',
            connect=partial(self.rename_menu, self.batch_node_menu_list),
            )
        self.batch_done_btn = PyFlameButton(
            text='Done',
            connect=self.done_button,
            color=Color.BLUE,
            )

        #-------------------------------------
        # [Batch Node Tab Layout]
        #-------------------------------------

        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_node_menu_label, 0, 0, 1, 2)
        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_node_menu_list, 1, 0, 10, 2)

        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_node_list_label, 0, 2, 1, 2)
        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_node_list, 1, 2, 10, 2)

        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_add_btn, 1, 4)
        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_remove_btn, 2, 4)
        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_rename_btn, 3, 4)
        self.tabs.tab_pages['Batch Nodes'].grid_layout.addWidget(self.batch_done_btn, 11, 4)

    def matchbox_tab(self):
        """
        Matchbox Tab
        ============
        """

        def add_matchbox():

            # Create scripts for nodes in selected list
            for node in self.matchbox_node_list.selected_items:
                self.node_name = node.text()

                matchbox_node_path = os.path.join(self.matchbox_path, node.text())

                self.create_node_line = f"new_node = flame.batch.create_node('Matchbox', '{matchbox_node_path}.mx')"

                self.create_node()

            # Refresh node menu lists
            self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

        # Labels
        self.matchbox_node_menu_label = PyFlameLabel(
            text='Batch Node Menus',
            style=Style.UNDERLINE,
            )
        self.matchbox_node_list_label = PyFlameLabel(
            text='Autodesk Matchbox Nodes',
            style=Style.UNDERLINE,
            )

        # Listboxes
        self.matchbox_node_menu_list = PyFlameListWidget()
        self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)

        self.matchbox_node_list = PyFlameListWidget()
        self.get_matchbox_list()

        # Buttons
        self.matchbox_add_btn = PyFlameButton(
            text='Add',
            connect=add_matchbox,
            )
        self.matchbox_remove_node_btn = PyFlameButton(
            text='Remove',
            connect=partial(self.remove_scripts, self.matchbox_node_menu_list),
            )
        self.matchbox_rename_btn = PyFlameButton(
            text='Rename',
            connect=partial(self.rename_menu, self.matchbox_node_menu_list),
            )
        self.matchbox_done_btn = PyFlameButton(
            text='Done',
            connect=self.done_button,
            color=Color.BLUE,
            )

        #-------------------------------------
        # [Matchbox Tab Layout]
        #-------------------------------------

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_node_menu_label, 0, 0, 1, 2)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_node_menu_list, 1, 0, 10, 2)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_node_list_label, 0, 2, 1, 2)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_node_list, 1, 2, 10, 2)

        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_add_btn, 1, 4)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_remove_node_btn, 2, 4)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_rename_btn, 3, 4)
        self.tabs.tab_pages['Matchbox'].grid_layout.addWidget(self.matchbox_done_btn, 11, 4)

    def logik_tab(self):
        """
        Logik Tab
        =========
        """

        def add_logik_matchbox():

            # Create scripts for nodes in selected list
            for node in self.logik_node_list.selected_items:

                self.node_name = node.text()

                logik_node_path = os.path.join(self.settings.logik_path, node.text())
                print ('Logik Node Path:', logik_node_path)

                self.create_node_line = f"new_node = flame.batch.create_node('Matchbox', '{logik_node_path}.glsl')"

                self.create_node()

            # Refresh node menu lists
            self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

        def set_path():

            path = pyflame.file_browser(
                path=self.settings.logik_path,
                title='Select Logik Matchbox Directory',
                select_directory=True,
                window_to_hide=self.window,
                )

            if path:
                self.settings.save_config(
                    config_values={
                        'logik_path': path
                        }
                    )

                self.get_logik_list()

        # Labels
        self.logik_node_menu_label = PyFlameLabel(
            text='Batch Node Menus',
            style=Style.UNDERLINE,
            )
        self.logik_node_list_label = PyFlameLabel(
            text='Logik Matchbox Nodes',
            style=Style.UNDERLINE,
            )

        # Listboxes
        self.logik_node_menu_list = PyFlameListWidget()
        self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

        self.logik_node_list = PyFlameListWidget()
        self.get_logik_list()

        # Buttons
        self.logik_setup_btn = PyFlameButton(
            text='Set Path',
            connect=set_path,
            )
        self.logik_add_btn = PyFlameButton(
            text='Add',
            connect=add_logik_matchbox,
            )
        self.logik_remove_btn = PyFlameButton(
            text='Remove',
            connect=partial(self.remove_scripts, self.logik_node_menu_list),
            )
        self.logik_rename_btn = PyFlameButton(
            text='Rename',
            connect=partial(self.rename_menu, self.logik_node_menu_list),
            )
        self.logik_done_btn = PyFlameButton(
            text='Done',
            connect=self.done_button,
            color=Color.BLUE,
            )

        #-------------------------------------
        # [Logik Tab Layout]
        #-------------------------------------

        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_node_menu_label, 0, 0, 1, 2)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_node_menu_list, 1, 0, 10, 2)

        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_node_list_label, 0, 2, 1, 2)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_node_list, 1, 2, 10, 2)

        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_setup_btn, 5, 4)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_add_btn, 1, 4)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_remove_btn, 2, 4)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_rename_btn, 3, 4)
        self.tabs.tab_pages['Logik Matchbox'].grid_layout.addWidget(self.logik_done_btn, 11, 4)

    # ------------------------------------------------------------------------------

    def get_batch_node_list(self):
        """
        Get Batch Node List
        ===================

        Get list of batch nodes from Flame.
        """

        for node in flame.batch.node_types:
            bad_nodes = 'Colour Blend', 'Matte Blend' # bad_nodes crash flame when connecting
            if node not in bad_nodes:
                self.batch_node_list.addItem(node)

    def get_matchbox_list(self):
        """
        Get Matchbox List
        =================

        Get list of matchboxes from matchbox path.
        """

        # Leave list empty if this Flame version has no shaders folder so the setup window still opens
        if not os.path.isdir(self.matchbox_path):
            pyflame.print(f'Matchbox Shaders Folder Not Found: {self.matchbox_path}', text_color=TextColor.YELLOW)

            return

        matchboxes = os.listdir(self.matchbox_path)
        matchboxes.sort()

        for m in matchboxes:
            if not m.startswith('.'):
                if m.endswith('.mx'):
                    m = m[:-3]
                    self.matchbox_node_list.addItem(m)

    def get_logik_list(self):
        """
        Get Logik List
        ==============

        Get list of logik matchboxes from logik matchbox path and add to list widget.
        """

        logik_matchboxes = os.listdir(self.settings.logik_path)
        logik_matchboxes.sort()

        glsl_files = [f[:-5] for f in logik_matchboxes if f.endswith('.glsl')]
        self.logik_node_list.replace_items(glsl_files)

    def done_button(self):
        """
        Done Button
        ===========

        Close window and refresh hooks
        """

        self.window.close()
        pyflame.refresh_hooks()

    # ------------------------------------------------------------------------------

    def get_node_scripts_lists(self, listbox, folder):

        #  Get list of scripts for nodes
        listbox.clear()

        item_list = os.listdir(folder)
        item_list.sort()

        for item in item_list:
            if item.endswith('.py'):
                item = item[:-3]

                listbox.addItem(item)

    def remove_scripts(self, listbox):

        # Delete script files
        selected_nodes = listbox.selected_items

        selected_node_text = []

        for node in selected_nodes:
            node = node.text()
            selected_node_text.append(node)

        if not selected_node_text:
            return

        # Confirm once for the whole selection before deleting anything
        if not PyFlameMessageWindow(
            message='Delete selected menus and their saved node setups?\n\n' + '\n'.join(selected_node_text),
            message_type=MessageType.WARNING,
            title=f'{SCRIPT_NAME}: Confirm Operation',
            parent=self.window,
            ):
            pyflame.print('Cancelled', text_color=TextColor.RED)

            return

        file_list = os.listdir(self.node_dir)
        failed_items = []

        # Only delete the menu's own files and setup folder, not other menus whose names contain it
        for node in selected_node_text:
            for f in (node + '.py', node + '.pyc', node):
                if f in file_list:
                    item_path = os.path.join(self.node_dir, f)
                    try:
                        if os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                        else:
                            os.remove(item_path)
                        pyflame.print(f'{f}: Deleted', text_color=TextColor.RED)
                    except Exception as e:
                        failed_items.append(f'{f}: {e}')

        if failed_items:
            PyFlameMessageWindow(
                message='Could not delete:\n\n' + '\n'.join(failed_items),
                message_type=MessageType.ERROR,
                parent=self.window,
                )

        self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
        self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
        self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

    # ------------------------------------------------------------------------------

    def rename_menu(self, menu_list):

        def rename():

            def get_new_menu_text(menu_text: str, new_menu_name: str) -> str:
                """
                Get New Menu Text
                =================

                Return the selected menu script text with the menu name changed to the new name.

                Only the places where the templates write the menu name are changed (docstring, setup path,
                new node name, printed messages, title banner and menu entry name). Code, node types and
                matchbox paths that happen to contain the name are left as is.

                Args
                ----
                    menu_text (str):
                        Current menu script text.

                    new_menu_name (str):
                        New menu name.

                Returns
                -------
                    menu_text (str): Menu script text with the new name.
                """

                old_name = re.escape(selected_menu)

                # Places where the templates write the menu name, as (text before, text after)
                name_patterns = [
                    rf'(menu script for ){old_name}( node)',
                    rf'(Batch Nodes\.\.\. -> ){old_name}()$',
                    rf"(new_node_name = '){old_name}(')",
                    rf"('Node Created: ){old_name}(')",
                    rf"(print_title\(f'Batch Nodes - ){old_name}( )",
                    rf"('name': '){old_name}(')",
                    ]

                for pattern in name_patterns:
                    menu_text = re.sub(pattern, lambda m: m.group(1) + new_menu_name + m.group(2), menu_text, flags=re.MULTILINE)

                # Saved setup path ends with <name>/<name>, only change those last two parts
                menu_text = re.sub(
                    rf"(load_node_setup\('.*/){old_name}/{old_name}(')",
                    lambda m: m.group(1) + new_menu_name + '/' + new_menu_name + m.group(2),
                    menu_text,
                    )

                return menu_text

            def move_item(current_path: str, new_path: str) -> None:
                """
                Move Item
                =========

                Rename a file or folder and remember it so the rename can be undone if a later step fails.

                Args
                ----
                    current_path (str):
                        Path to rename.

                    new_path (str):
                        New path.
                """

                os.rename(current_path, new_path)
                moved_items.append((current_path, new_path))

            def undo_rename() -> list:
                """
                Undo Rename
                ===========

                Put back everything moved so far, newest first.

                Returns
                -------
                    failed_items (list): Items that could not be put back.
                """

                failed_items = []

                for current_path, new_path in reversed(moved_items):
                    try:
                        os.rename(new_path, current_path)
                    except Exception as e:
                        failed_items.append(f'{os.path.basename(new_path)}: {e}')

                return failed_items

            def rename_node_files(new_menu_name: str) -> None:
                """
                Rename Node Files
                =================

                Rename the saved setup folder, the setup files named after the menu, and the menu script.

                Args
                ----
                    new_menu_name (str): New menu name.
                """

                # Rename saved node directory if it exists
                current_dir = os.path.join(self.node_dir, selected_menu)
                if os.path.isdir(current_dir):
                    new_dir = os.path.join(self.node_dir, new_menu_name)
                    move_item(current_dir, new_dir)

                    # Rename setup files whose base name is the menu name, e.g. <name>.openfx_node, <name>.1.glsl
                    for file_name in os.listdir(new_dir):
                        if file_name == selected_menu or file_name.startswith(selected_menu + '.'):
                            new_file_name = new_menu_name + file_name[len(selected_menu):]
                            move_item(os.path.join(new_dir, file_name), os.path.join(new_dir, new_file_name))

                # Rename python file and saved setup if it exists
                for f in os.listdir(self.node_dir):
                    if f == selected_menu + '.py':
                        move_item(os.path.join(self.node_dir, selected_menu + '.py'), os.path.join(self.node_dir, new_menu_name + '.py'))
                    if f == selected_menu + '.pyc':
                        move_item(os.path.join(self.node_dir, selected_menu + '.pyc'), os.path.join(self.node_dir, new_menu_name + '.pyc'))

            new_menu_name = new_name_entry.text.strip()

            # __pycache__ in menus/ is not a menu
            if not new_menu_name or new_menu_name == '__pycache__':
                return

            # Same name, nothing to rename
            if new_menu_name == selected_menu:
                rename_window.close()

                return

            # Reject characters that break the setup path or the generated menu script
            bad_characters = [c for c in ('/', '\\', "'") if c in new_menu_name]
            if bad_characters:
                PyFlameMessageWindow(
                    message=f'Menu name can not contain: {" ".join(bad_characters)}',
                    message_type=MessageType.ERROR,
                    parent=rename_window,
                    )

                return

            # Find files of another menu with the new name. Skip the selected menu's own files so a case-only rename on a case-insensitive file system isn't seen as another menu.
            replace_items = []
            menu_dir_items = os.listdir(self.node_dir)

            for extension in ('.py', '.pyc', ''):
                item_path = os.path.join(self.node_dir, new_menu_name + extension)
                current_path = os.path.join(self.node_dir, selected_menu + extension)
                if os.path.exists(item_path) and not (os.path.exists(current_path) and os.path.samefile(item_path, current_path)):
                    # Use the real on-disk name so a menu that differs only in case is restored with its own name if the rename fails
                    item_name = new_menu_name + extension
                    if item_name not in menu_dir_items:
                        item_name = next((i for i in menu_dir_items if i.lower() == item_name.lower()), item_name)
                    replace_items.append(os.path.join(self.node_dir, item_name))

            if replace_items:
                if not PyFlameMessageWindow(
                    message=f'Menu already exists: {new_menu_name}\n\nReplace it? The existing {new_menu_name} menu and its saved node setup will be deleted.',
                    message_type=MessageType.WARNING,
                    title=f'{SCRIPT_NAME}: Confirm Operation',
                    parent=rename_window,
                    ):
                    return

            moved_items = []
            replaced_items = []
            restore_failures = []
            menu_script_path = os.path.join(self.node_dir, new_menu_name + '.py')

            try:
                # Build new menu text before changing any files
                with open(os.path.join(self.node_dir, selected_menu + '.py'), 'r') as menu_file:
                    old_menu_text = menu_file.read()
                new_menu_text = get_new_menu_text(old_menu_text, new_menu_name)

                # Move the menu being replaced aside so it can be put back if the rename fails. It's deleted once the rename is done.
                for item_path in replace_items:
                    backup_path = os.path.join(self.node_dir, f'.{os.path.basename(item_path)}.bn_replaced')
                    x = 1
                    while os.path.exists(backup_path):
                        backup_path = os.path.join(self.node_dir, f'.{os.path.basename(item_path)}.bn_replaced{x}')
                        x += 1
                    move_item(item_path, backup_path)
                    replaced_items.append((item_path, backup_path))

                rename_node_files(new_menu_name)

                try:
                    with open(menu_script_path, 'w') as menu_file:
                        menu_file.write(new_menu_text)
                except Exception:
                    # Script may be partly written, put the original text back before undoing the renames
                    try:
                        with open(menu_script_path, 'w') as menu_file:
                            menu_file.write(old_menu_text)
                    except Exception as restore_error:
                        restore_failures.append(f'{selected_menu}.py text could not be restored: {restore_error}')
                    raise
            except Exception as e:
                failed_items = restore_failures + undo_rename()
                self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
                self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
                self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)
                if failed_items:
                    undo_message = 'Some changes could not be undone:\n\n' + '\n'.join(failed_items)
                else:
                    undo_message = 'All changes were undone.'
                PyFlameMessageWindow(
                    message=f'Could not rename {selected_menu} to {new_menu_name}:\n\n{e}\n\n{undo_message}',
                    message_type=MessageType.ERROR,
                    parent=rename_window,
                    )

                return

            # Rename is done, delete the menu that was replaced
            for item_path, backup_path in replaced_items:
                try:
                    if os.path.isdir(backup_path):
                        shutil.rmtree(backup_path)
                    else:
                        os.remove(backup_path)
                    pyflame.print(f'{os.path.basename(item_path)}: Deleted', text_color=TextColor.RED)
                except Exception as e:
                    pyflame.print(f'{os.path.basename(item_path)}: Could Not Delete Replaced Item {backup_path}: {e}', print_type=PrintType.ERROR)

            self.batch_node_menu_list.clear()
            self.matchbox_node_menu_list.clear()
            self.logik_node_menu_list.clear()

            self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
            self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

            flame.execute_shortcut('Rescan Python Hooks')

            pyflame.print(f'{selected_menu}: Renamed To {new_menu_name}.', text_color=TextColor.GREEN)

            rename_window.close()

        if not menu_list.selected_items:
            return

        selected_menu = [m.text() for m in menu_list.selected_items][0]

        rename_window = PyFlameWindow(
            title=f'Rename Menu',
            return_pressed=rename,
            grid_layout_columns=4,
            grid_layout_rows=3,
            parent=self.window,
            )

        #  Labels
        new_name_label = PyFlameLabel(
            text='Menu Name',
            width=75,
            )

        # Entries
        new_name_entry = PyFlameEntry(
            text=selected_menu,
            )

        # Buttons
        rename_btn = PyFlameButton(
            text='Rename',
            connect=rename,
            color=Color.BLUE,
            )
        cancel_btn = PyFlameButton(
            text='Cancel',
            connect=rename_window.close
            )

        #-------------------------------------
        # [Rename Window Layout]
        #-------------------------------------

        rename_window.grid_layout.addWidget(new_name_label, 0, 0)
        rename_window.grid_layout.addWidget(new_name_entry, 0, 1, 1, 3)
        rename_window.grid_layout.addWidget(cancel_btn, 2, 2)
        rename_window.grid_layout.addWidget(rename_btn, 2, 3)

    def create_node(self):

        def create_node_script():

            def replace_tokens():

                token_dict = {}

                token_dict['<NodeName>'] = node_name
                token_dict['<CreateNodeLine>'] = self.create_node_line
                token_dict['<Version>'] = SCRIPT_VERSION

                # Replace tokens in menu template
                for key, value in token_dict.items():
                    for line in template_lines:
                        if key in line:
                            line_index = template_lines.index(line)
                            new_line = re.sub(key, value, line)
                            template_lines[line_index] = new_line

            # Read template
            template = open(self.create_node_template, 'r')
            template_lines = template.read().splitlines()

            # Replace tokens in template
            replace_tokens()

            # Write out temp node
            out_file = open(node_script, 'w')
            for line in template_lines:
                print(line, file=out_file)
            out_file.close()

        # Create node scripts for selected nodes
        node_name = self.node_name.replace('.', '_')
        #print ('node_name:', node_name, '\n')

        node_script = os.path.join(self.node_dir, node_name) + '.py'
        node_setup_path = os.path.join(self.node_dir, node_name)

        # Confirm before overwriting an existing menu. A plain menu doesn't use a saved setup, so an old setup folder is removed.
        if os.path.exists(node_script) or os.path.exists(node_setup_path):
            message = f'Overwrite existing menu: {node_name}?'
            if os.path.isdir(node_setup_path):
                message += '\n\nIts saved node setup folder will be deleted.'
            if not PyFlameMessageWindow(
                message=message,
                message_type=MessageType.WARNING,
                title=f'{SCRIPT_NAME}: Confirm Operation',
                parent=self.window,
                ):
                pyflame.print(f'{node_name}: Cancelled', text_color=TextColor.RED)

                return

        # Create script for new node
        create_node_script()

        pyflame.print(f'{node_name}: Node Script Saved.', text_color=TextColor.GREEN)

        # Remove old saved setup only after the new script is written
        if os.path.isdir(node_setup_path):
            try:
                shutil.rmtree(node_setup_path)
                pyflame.print(f'{node_name}: Old Node Setup Folder Deleted', text_color=TextColor.RED)
            except Exception as e:
                pyflame.print(f'{node_name}: Could Not Delete Old Node Setup Folder: {e}', print_type=PrintType.ERROR)

    def save_selected_node(self):

        def create_node_script():

            def replace_tokens():

                token_dict = {}

                token_dict['<NodeName>'] = node_name
                token_dict['<NodeType>'] = node_type
                token_dict['<NodeSetupPathName>'] = node_setup_path_name
                token_dict['<Version>'] = SCRIPT_VERSION

                # Replace tokens in menu template
                for key, value in token_dict.items():
                    for line in template_lines:
                        if key in line:
                            line_index = template_lines.index(line)
                            new_line = re.sub(key, value, line)
                            template_lines[line_index] = new_line

            # Read template
            template = open(self.save_selected_template, 'r')
            template_lines = template.read().splitlines()

            # Replace tokens in template
            replace_tokens()

            # Write out temp node
            out_file = open(node_script, 'w')
            for line in template_lines:
                print(line, file=out_file)
            out_file.close()

        selected_node = self.selection[0]

        node_name = str(selected_node.name)[1:-1]

        # Reject characters that break the setup path or the generated menu script
        bad_characters = [c for c in ("'", '/') if c in node_name]
        if bad_characters:
            PyFlameMessageWindow(
                message=f'Node name can not contain: {" ".join(bad_characters)}',
                message_type=MessageType.ERROR,
                parent=None,
                )

            return

        # Check user python folder for existing node script
        create_node = True

        if os.path.exists(os.path.join(self.node_dir, node_name)) or os.path.exists(os.path.join(self.node_dir, node_name + '.py')):
            create_node = PyFlameMessageWindow(
                message=f'Overwrite existing menu: {node_name}?',
                message_type=MessageType.WARNING,
                title=f'{SCRIPT_NAME}: Confirm Operation',
                parent=None,
                )

        if create_node:
            node_type = str(selected_node.type)[1:-1]
            print ('Node Type:', node_type)

            # Create folder to save node setup
            node_setup_path = os.path.join(self.node_dir, node_name)
            print ('Node Setup Path:', node_setup_path, '\n')

            try:
                os.makedirs(node_setup_path)
                pyflame.print(f'{node_name}: Node Folder Created', text_color=TextColor.GREEN)
            except:
                pyflame.print(f'{node_name}: Node Folder Already Exists - Overwriting Setup', text_color=TextColor.YELLOW)

            # Save node setup
            node_setup_path_name = os.path.join(node_setup_path, node_name)

            selected_node.save_node_setup(node_setup_path_name)

            # Set script path
            node_script = os.path.join(self.node_dir, node_name) + '.py'

            # Create script for new node
            create_node_script()

            PyFlameMessageWindow(
                message=f'Menu created: {node_name}',
                parent=None,
                )

        else:
            pyflame.print('Cancelled', text_color=TextColor.RED)

# ==============================================================================

def edit_node_lists(selection):

    script = BatchNodes(selection)
    if script.script_installed:
        script.main_window()

def save_node(selection):

    script = BatchNodes(selection)
    if script.script_installed:
        script.save_selected_node()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_node(selection):
    import flame

    for item in selection:
        if isinstance(item, flame.PyNode):
            return True
    return False

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
                    'name': 'Batch Nodes Setup',
                    'execute': edit_node_lists,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Batch Nodes...',
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Create Menu for Selected Node',
                    'order': 0,
                    'isVisible': scope_node,
                    'execute': save_node,
                    'minimumVersion': '2025.1'
                },
                {
                    'name': '----------------------------------',
                    'order': 1,
                    'isVisible': scope_node,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
