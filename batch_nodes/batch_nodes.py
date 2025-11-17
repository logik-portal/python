# Batch Nodes
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
Script Name: Batch Nodes
Script Version: 3.11.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 04.18.20
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch / Flame Main Menu

Description:

    *** Does not work with Flame 2024.0 due to bug in Flame ***

    Add menus to batch right-click for your favorite nodes.

    Works with standard batch nodes/matchboxes/ofx.

    OFX can only be added by right clicking on an existing node in batch.

    Nodes added by right-clicking on them in batch will be saved with current settings.

    All created node menu scripts are saved in /opt/Autodesk/user/YOURUSER/python/batch_node_menus

Menus:

    To create/rename/delete menus from node lists:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Batch Nodes Setup

    To create menus for nodes with settings applied in batch:
        Right-click on node in batch -> Batch Nodes... -> Create Menu For Selected Node

    To create menus for ofx nodes:
        Right-click on node in batch -> Batch Nodes... -> Create Menu For Selected Node

    To add node from menu to batch:
        Right-click in batch -> Batch Nodes... -> Select Node to be added

URL:
    https://github.com/logik-portal/python/batch_nodes

    To add node from menu to batch connected to selected node:
        Right-click on node in batch -> Batch Nodes... -> Select Node to be added

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

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

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import shutil
from functools import partial

import flame
from lib.pyflame_lib_batch_nodes import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Batch Nodes'
SCRIPT_VERSION = 'v3.11.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class BatchNodes:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        #  Init variables
        self.create_node_line = ''
        self.selection = selection

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

    #-------------------------------------

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

    #-------------------------------------

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

        file_list = os.listdir(self.node_dir)

        for node in selected_node_text:
            for f in file_list:
                if node in f:
                    try:
                        os.remove(os.path.join(self.node_dir, f))
                    except:
                        shutil.rmtree(os.path.join(self.node_dir, f))
                    pyflame.print(f'{f}: Deleted', text_color=TextColor.RED)

        self.get_node_scripts_lists(self.batch_node_menu_list, self.node_dir)
        self.get_node_scripts_lists(self.matchbox_node_menu_list, self.node_dir)
        self.get_node_scripts_lists(self.logik_node_menu_list, self.node_dir)

    #-------------------------------------

    def rename_menu(self, menu_list):

        def rename():

            def edit_menu_file(new_menu_name):

                # Edit python menu file to change menu name
                menu_script_path = os.path.join(self.node_dir, selected_menu + '.py')

                menu_lines = open(menu_script_path, 'r')
                lines = menu_lines.read().splitlines()

                menu_lines.close()

                for l in lines:
                    if selected_menu in l:
                        if 'flame.batch.create_node' not in l:
                            line_index = lines.index(l)
                            new_line = l.replace(selected_menu, new_menu_name)
                            lines[line_index] = new_line

                out_file = open(menu_script_path, 'w')
                for line in lines:
                    print(line, file=out_file)
                out_file.close()

            def rename_node_files(new_menu_name):

                # Rename saved node directory if it exists
                for root, dirs, files in os.walk(self.node_dir):
                    for d in dirs:
                        if d == selected_menu:
                            current_dir = os.path.join(root, d)
                            new_dir = current_dir.replace(selected_menu, new_menu_name)
                            os.rename(current_dir, new_dir)

                            # iterate through files in saved setup directory to change file names
                            for file_name in os.listdir(new_dir):
                                if selected_menu in file_name:
                                    new_file_name = file_name.replace(selected_menu, new_menu_name)
                                    os.rename(os.path.join(new_dir, file_name), os.path.join(new_dir, new_file_name))

                # Rename python file and saved setup if it exists
                for f in os.listdir(self.node_dir):
                    if f == selected_menu + '.py':
                        os.rename(os.path.join(self.node_dir, selected_menu + '.py'), os.path.join(self.node_dir, new_menu_name + '.py'))
                    if f == selected_menu + '.pyc':
                        os.rename(os.path.join(self.node_dir, selected_menu + '.pyc'), os.path.join(self.node_dir, new_menu_name + '.pyc'))

            if not new_name_entry.text:
                return

            if new_name_entry.text == selected_menu:
                if not PyFlameMessageWindow(
                    message=f'Overwrite existing menu: {selected_menu}?',
                    message_type=MessageType.CONFIRM,
                    title=f'{SCRIPT_NAME}: Confirm Operation',
                    parent=rename_window,
                    ):
                    return

            new_menu_name = new_name_entry.text

            edit_menu_file(new_menu_name)

            rename_node_files(new_menu_name)

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

        # Create script for new node
        create_node_script()

        pyflame.print(f'{node_name}: Node Script Saved.', text_color=TextColor.GREEN)

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

        # Check user python folder for existing node script
        create_node = True

        for n in os.listdir(self.node_dir):
            if n == node_name:
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

#-------------------------------------

def edit_node_lists(selection):

    script = BatchNodes(selection)
    script.main_window()

def save_node(selection):

    script = BatchNodes(selection)
    script.save_selected_node()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_node(selection):
    import flame

    for item in selection:
        if isinstance(item, flame.PyNode):
            return True
    return False

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
                    'name': 'Batch Nodes Setup',
                    'execute': edit_node_lists,
                    'minimumVersion': '2025'
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
                    'minimumVersion': '2025'
                },
                {
                    'name': '----------------------------------',
                    'order': 1,
                    'isVisible': scope_node,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
