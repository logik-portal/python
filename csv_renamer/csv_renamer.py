# CSV Renamer
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
Script Name: CSV Renamer
Script Version: 1.0.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 05.04.26
Update Date: 05.25.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel/Desktop

Description:

    Rename selected clips and sequences using names chosen from a CSV file.

Usage:

    1. Right-click selected clips/sequences and choose CSV Renamer.
    2. Select a CSV file when prompted.
    3. Choose the clip/sequence to rename from the Selected Clips menu.
    4. Click a cell in the CSV table to use as the new name.
    5. Click Rename Clip or press Enter to apply the rename.

    Note: If multiple selected clips share the same name, a numeric suffix is
    appended to each duplicate entry in the menu (e.g. Shot_010 (1), Shot_010 (2)).

Menus:

    Media Panel/Desktop:

        Right-click on selected clips/sequences -> CSV Renamer

To install:

    Copy script into /opt/Autodesk/shared/python/csv_renamer

Updates:

    v1.0.0 05.04.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import flame
from lib.pyflame_lib_csv_renamer import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'CSV Renamer'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class CSVRenamer:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings
        self.load_config()

        # Initialize variables
        self.selection = selection
        self.csv_info: dict[str, list[str]] = {}

        self.selection_map: dict[str, Any] = self.build_selection_map()

        csv_file_path = pyflame.file_browser(
            path=self.settings.csv_path,
            title='Select CSV File',
            extension=['csv'],
            )

        if csv_file_path:
            # Open main window
            self.main_window(csv_file_path)

    def build_selection_map(self) -> dict[str, Any]:
        """
        Build Selection Map
        ===================

        Build a dictionary mapping unique display labels to their corresponding flame
        objects from `self.selection`.

        When two or more objects share the same name, a numeric suffix is appended to
        each duplicate label (e.g. ``Shot_010 (1)``, ``Shot_010 (2)``) so every key in
        the returned dict is unique and can be used directly as a menu option.

        Returns
        -------
            dict[str, Any]:
                An ordered mapping of ``label -> flame object`` in the same order as
                ``self.selection``.

        Example
        -------
            ```
            self.selection_map = self.build_selection_map()
            selected_obj = self.selection_map[self.selected_clips_menu.text]
            ```
        """

        name_counts: dict[str, int] = {}
        for obj in self.selection:
            name = str(obj.name)[1:-1]
            name_counts[name] = name_counts.get(name, 0) + 1

        seen: dict[str, int] = {}
        selection_map: dict[str, object] = {}
        for obj in self.selection:
            name = str(obj.name)[1:-1]
            if name_counts[name] > 1:
                seen[name] = seen.get(name, 0) + 1
                label = f'{name} ({seen[name]})'
            else:
                label = name
            selection_map[label] = obj

        return selection_map

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads configuration values from the config file and applies them to `self.settings`.

        If the config file does not exist, it creates the file using the default values
        from the `config_values` dictionary. Otherwise, it loads the existing config values
        and applies them to `self.settings`.
        """

        self.settings = PyFlameConfig(
            config_values={
                'csv_path': '/opt/Autodesk',
                },
            )

    def main_window(self, csv_file_path) -> None:

        def load_csv():

            self.csv_table.load_csv(self.csv_entry_browser.path)

        def save_csv():

            def save_file():

                self.csv_table.save_csv_file(csv_file_path) # Save file

                pyflame.print('CSV Saved', text_color=TextColor.GREEN)

            csv_file_path = self.csv_entry_browser.path

            if os.path.exists(csv_file_path):
                overwrite = PyFlameMessageWindow(
                    message='File already exists. Overwrite?',
                    message_type=MessageType.WARNING,
                    parent=self.csv_window,
                    )
                if overwrite:
                    save_file()
                else:
                    pyflame.print('CSV Save Cancelled', text_color=TextColor.RED)
            else:
                save_file()

        def done():

            # Save settings
            self.settings.save_config(
                config_values={
                    'csv_path': self.csv_entry_browser.path,
                    }
                )

            self.csv_window.close()

        def rename_clip():

            obj = self.selection_map[self.selected_clips_menu.text]
            selected_indexes = self.csv_table.selectionModel().selectedIndexes()
            if not selected_indexes:
                return
            new_name = self.csv_table.model.itemFromIndex(selected_indexes[0]).text()
            old_label = self.selected_clips_menu.text

            obj.name = new_name

            pyflame.print(f'Renaming: {old_label} -> {new_name}', text_color=TextColor.GREEN)

            # Rebuild selection_map with updated label, preserving order
            self.selection_map = {
                (new_name if k == old_label else k): v
                for k, v in self.selection_map.items()
            }

            # Update menu options and current text
            self.selected_clips_menu.menu_options = list(self.selection_map.keys())
            self.selected_clips_menu.text = new_name

        self.csv_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=rename_clip,
            escape_pressed=done,
            grid_layout_columns=8,
            grid_layout_rows=19,
            parent=None,
            )

        # Labels
        self.selected_csv_label = PyFlameLabel(
            text='Selected CSV',
            )
        self.selected_clips_label = PyFlameLabel(
            text='Selected Clips',
            )

        # Entry Browser
        self.csv_entry_browser = PyFlameEntryBrowser(
            path=csv_file_path,
            browser_type=BrowserType.FILE,
            browser_ext=['csv'],
            browser_title='Select CSV File',
            window_to_hide=[self.csv_window],
            connect=load_csv,
            )

        # Table
        self.csv_table = PyFlameTable(
            csv_file_path=csv_file_path,
            )

        # Menus
        self.selected_clips_menu = PyFlameMenu(
            text=next(iter(self.selection_map), ''),
            menu_options=list(self.selection_map.keys()),
            )

        # Buttons
        self.save_csv_button = PyFlameButton(
            text='Save',
            connect=save_csv,
            )
        self.rename_clip_button = PyFlameButton(
            text='Rename Clip',
            connect=rename_clip,
            color=Color.BLUE,
            )
        self.done_button = PyFlameButton(
            text='Done',
            connect=done,
            )

        # Horizontal Line
        self.horizontal_line = PyFlameHorizontalLine()

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.csv_window.grid_layout.addWidget(self.selected_csv_label, 0, 0)
        self.csv_window.grid_layout.addWidget(self.csv_entry_browser, 0, 1, 1, 6)
        self.csv_window.grid_layout.addWidget(self.save_csv_button, 0, 7)

        self.csv_window.grid_layout.addWidget(self.horizontal_line, 1, 0, 1, 8)

        self.csv_window.grid_layout.addWidget(self.csv_table, 2, 0, 14, 8)

        self.csv_window.grid_layout.addWidget(self.selected_clips_label, 17, 2)
        self.csv_window.grid_layout.addWidget(self.selected_clips_menu, 17, 3, 1, 4)
        self.csv_window.grid_layout.addWidget(self.rename_clip_button, 17, 7)
        self.csv_window.grid_layout.addWidget(self.done_button, 19, 7)

# ==============================================================================
# [Scopes]
# ==============================================================================

def script_clip_sequence(selection):

    for item in selection:
        if isinstance(item, (flame.PyClip, flame.PySequence)):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'CSV Renamer',
                    'isVisible': script_clip_sequence,
                    'order': 1,
                    'separator': 'below',
                    'execute': CSVRenamer,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
