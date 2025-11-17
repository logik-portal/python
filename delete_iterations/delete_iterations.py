# Delete Iterations
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
Script Name: Delete Iterations
Script Version: 1.6.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 01.23.23
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch Iterations

Description:

    Delete iterations from batch groups. Keeps the specified number of iterations.

    Modified from clean_batch_iteration.py by Autodesk.

    Selecting a desktop will delete iterations from all batch groups in the desktop.

    Selecting a libraries will delete iterations from all batch groups in the library including in any folders.

    Selecting batch groups will delete iterations from the selected batch groups.

    Selecting folders will delete iterations from all batch groups in the folders.

URL:
    https://github.com/logik-portal/python/delete_iterations

Menus:

    Right-click on a desktop, library, batch group, or folder -> Delete Batch Iterations

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.6.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes main window.

    v1.5.0 03.12.25
        - Updated to PyFlameLib v4.3.0.

    v1.4.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v1.3.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v1.2.1 01.29.24
        - Fixed PySide6 errors/font in slider calculator.

    v1.2.0 01.21.24
        - Updated to PyFlameLib v2.
        - Updates to UI/PySide.

    v1.1.0 08.15.23
        - Updated to PyFlameLib v2.0.0.

    v1.0.1 06.29.23
        - Updated script versioning to semantic versioning.
        - Pressing return with the window open will now apply the settings.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame
from lib.pyflame_lib_delete_iterations import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Delete Iterations'
SCRIPT_VERSION = 'v1.6.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class DeleteIterations:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Create/Load config file
        self.settings = PyFlameConfig(
            config_values={
                'iterations_to_keep': 5,
                }
            )

        # Open main window
        self.main_window()

    def main_window(self):

        def save_config():
            """
            Save Config
            ===========

            Save settings to config file, delete iterations, and close window.
            """

            # Save settings to config file
            self.settings.save_config(
                config_values={
                    'iterations_to_keep': self.iterations_slider.value,
                    }
                )

            pyflame.print(f'Deleting iterations. Keeping last {self.settings.iterations_to_keep} iterations.', text_color=TextColor.GREEN)

            # Delete iterations
            self.cleanup()

            pyflame.print('Iterations deleted.', text_color=TextColor.GREEN)

            # Close window
            self.window.close()

        def close_window():
            """
            Close Window
            ============

            Close main window.
            """

            self.window.close()

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=2,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.iterations_label = PyFlameLabel(
            text='Iterations to Keep (Last)',
            )

        # Slider
        self.iterations_slider = PyFlameSlider(
            start_value=self.settings.iterations_to_keep,
            min_value=0,
            max_value=100,
            )

        # Buttons
        self.delete_button = PyFlameButton(
            text='Delete',
            connect=save_config,
            color=Color.RED,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.iterations_label, 0, 0)
        self.window.grid_layout.addWidget(self.iterations_slider, 0, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 2, 0)
        self.window.grid_layout.addWidget(self.delete_button, 2, 1)

    def cleanup(self):
        """
        Cleanup
        =======

        Delete iterations from selection based on selection type.
        """

        if isinstance(self.selection[0], flame.PyDesktop):
            self.clean_desktop()
        elif isinstance(self.selection[0], flame.PyBatch):
            self.clean_batch_group()
        elif isinstance(self.selection[0], flame.PyFolder):
            self.clean_folder()
        elif isinstance(self.selection[0], flame.PyLibrary):
            self.clean_library()

    def delete_iterations(self, batch_group):
        """
        Delete Iterations
        ==================

        Delete iterations from batch group.

        Deletes all iterations if iterations_to_keep is set to 0. Otherwise, keeps the specified number of iterations.

        Args:
        -----
            batch_group (flame.PyBatch): Batch Group to delete iterations from.
        """

        if self.settings.iterations_to_keep != 0:
            for iteration in batch_group.batch_iterations[:-self.settings.iterations_to_keep]:
                flame.delete(iteration, confirm=False)
        else:
            for iteration in batch_group.batch_iterations:
                flame.delete(iteration, confirm=False)

    def clean_desktop(self):
        """
        Clean Desktop
        =============

        Loop through selection(Desktop) and delete iterations from all batch groups in the desktop.
        """

        workspace = flame.projects.current_project.current_workspace
        for batch_group in workspace.desktop.batch_groups:
            workspace.desktop.current_batch_group = batch_group
            self.delete_iterations(batch_group)

    def clean_batch_group(self):
        """
        Clean Batch Group
        =================

        Loop through selection(Batch Group) and delete iterations from all batch groups in the selection.
        """

        for batch_group in self.selection:
            self.delete_iterations(batch_group)

    def find_batch_group(self, folder):
        """
        Find Batch Group
        ================

        Recursively find Batch Groups inside folders and libraries and delete all their iterations.

        Args:
        -----
            folder (flame.PyFolder): Folder to search for Batch Groups in.
        """

        for batch_group in folder.batch_groups:
            self.delete_iterations(batch_group)
        for folders in folder.folders:
            self.find_batch_group(folders)

    def clean_library(self):
        """
        Clean Library
        =============

        Loop through selection(Library) and delete iterations from all batch groups in the library including in any folders.
        """

        for top_library in self.selection:
            self.find_batch_group(top_library)

    def clean_folder(self):
        """
        Clean Folder
        =============

        Loop through selection(Folder) and delete iterations from all batch groups in the folders.
        """

        for top_folder in self.selection:
            self.find_batch_group(top_folder)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope(selection):

    for item in selection:
        if isinstance(item, (flame.PyDesktop, flame.PyBatch, flame.PyLibrary, flame.PyFolder)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Delete Batch Iterations',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope,
                    'execute': DeleteIterations,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
