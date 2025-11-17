# Multi Batch Render
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
Script Name: Multi Batch Render
Script Version: 4.13.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 12.12.18
Update Date: 07.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch / Media Panel Desktop

Description:

    Batch render multiple batch groups

URL:
    https://github.com/logik-portal/python/multi_batch_render

Menus:

    Right-click in batch -> Multi-Batch Render
    Right-click selected batch groups in desktop -> Render Selected Batch Groups

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v4.13.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Added Background Reactor render option.
        - Escape key closes window.

    v4.12.0 03.11.25
        - Updated to PyFlameLib v4.3.0.

    v4.11.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v4.10.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v4.9.0 01.21.24
        - Updates to UI/PySide.

    v4.8.0 07.08.23
        - Updated to PyFlameLib v2.0.0.

    v4.7.1 06.26.23
        - Updated script versioning to semantic versioning.
        - Render button is now blue.
        - Pressing return in main window will now start render.

    v4.7 05.23.23
        - Fixed bug with Smart Replace getting turned off when rendering.

    v4.6 02.04.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.

    v4.5 09.06.22
        - Updated menus for Flame 2023.2+:
            Right-click in batch -> Multi-Batch Render
            Right-click selected batch groups in desktop -> Render Selected Batch Groups

    v4.4 05.27.22
        - Messages print to Flame message window - Flame 2023.1+.
        - Fixed Exit Flame button.
        - Added confirmation dialog for Exit Flame button.

    v4.3 03.14.22
        - Moved UI widgets to external file - Added new render progress window.

    v4.2 02.25.22
        - Updated UI for Flame 2023.
        - Updated config to XML.
        - Burn button removed - no ability to test.

    v4.1 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v3.5 11.29.20
        - More UI enhancements / Fixed Font for Linux.
        - Misc bug fixes.
        - Batch groups that fail to render won't stop script. Failed batch group renders listed when all renders are complete.

    v3.2 08.10.20
        - Updated UI.

    v3.1 07.26.20
        - Save/Exit button added to main render window. This will save the project and exit Flame when the render is done.
        - Fixed errors when attempting to render from desktop with multiple batch groups with same name.

    v3.0 07.09.20:
        - Fixed errors when attempting to render batch groups with no Render or Write nodes. These batch groups will now be skipped.
        - Code cleanup.

    v2.91 05.18.20:
        - Render menu no longer incorrectly appears when selecting a batchgroup in a Library or Folder.

    v2.9 02.23.20:
        - Render window now centers in linux.
        - Script auto replaces all render and write nodes. Works as a fix for when render/write nodes stop working in batch.
        - Added menu to render current batch to batch menu. Render... -> Render Current - Use when getting errors with existing render and write nodes.

    v2.8 02.09.20:
        - Window can now be resized.
        - Fixed bug with Close Batch After Rendering checkbox - showed as checked even after being unchecked.
        - Burn button updated when checked or unchecked in setup.

    v2.7 11.06.19
        - Menu now appears as Render... when right-clicking on batch groups and in the batch window.
        - Removed menu that showed up in media panel when right clicking on items that could not be rendered.

    v2.6 10.13.19
        - Add option in main setup that will close batch groups when renders are done.
        - Removed menu that showed up when clicking on items in media panel that could not be rendered.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import time

import flame
from lib.pyflame_lib_multi_batch_render import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Multi Batch Render'
SCRIPT_VERSION = 'v4.13.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class MultiBatchRender:

    def __init__(self, selection):

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Init variables
        self.selection = selection
        self.desk = flame.project.current_project.current_workspace.desktop
        self.desktop_batch_group_object_list = self.desk.batch_groups
        self.desktop_batch_group_list = [str(b.name)[1:-1] for b in self.desktop_batch_group_object_list]
        self.num_batch_groups = 0
        self.failed_render_list = []
        self.reactor_render_success = True

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
                'close_after_render': False,
                'render_option': 'Foreground',
                }
            )

        return settings

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for rendering batch groups. Allows user to select batch groups to render.

        All batch groups are listed in a listbox. User can select multiple batch groups to render.
        """

        def list_batch_groups() -> None:
            """
            List Batch Groups
            =================

            Add list of all current desktop batch groups to listbox.
            """

            current_batch_group = str(flame.batch.name)[1:-1]

            # Get current batch number
            for i in [i for i, x in enumerate(self.desktop_batch_group_list) if x == current_batch_group]:
                current_batch_num = int(i)

            # Add names of batch groups to list
            self.batch_group_list.addItems(self.desktop_batch_group_list)
            self.batch_group_list.setCurrentItem(self.batch_group_list.item(current_batch_num))
            self.batch_group_list.setFocus()

        def selected_batch_groups() -> None:
            """
            Selected Batch Groups
            =====================

            Get the index of the selected batch groups.
            """

            selected_items = self.batch_group_list.selectedItems()
            self.selected_batch_groups = [self.batch_group_list.row(item) for item in selected_items]

        def save_config() -> None:
            """
            Save Config
            ===========

            Save settings to config file.
            """

            self.settings.save_config(
                config_values={
                    'close_after_render': self.close_batch_pushbutton.checked,
                    'render_option': self.render_option_menu.text,
                    }
                )

        def render() -> None:
            """
            Render
            ======

            Render selected batch groups.
            """

            # Confirm exit Flame after render
            if self.exit_flame.checked:
                if not PyFlameMessageWindow(
                    message='Exit Flame when render is complete?',
                    message_type=MessageType.CONFIRM,
                    parent=self.window,
                    ):
                    return

            save_config()

            self.window.hide()

            selected_batch_groups()

            self.render_batch_groups()

            self.window.close()

        def cancel() -> None:
            """
            Cancel
            ======

            Close window and cancel render.
            """

            self.window.close()

            try:
                self.setup_window.close()
            except:
                pass

            pyflame.print('Cancelled.')

        # Main Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=render,
            escape_pressed=cancel,
            grid_layout_columns=4,
            grid_layout_rows=11,
            parent=None,
            )

        # Labels
        self.batch_group_label = PyFlameLabel(
            text='Desktop Batch Groups',
            style=Style.UNDERLINE,
            )
        self.render_option_label = PyFlameLabel(
            text='Render',
            style=Style.UNDERLINE,
            )

        self.after_render_label = PyFlameLabel(
            text='After Render',
            style=Style.UNDERLINE,
            )

        # Listbox
        self.batch_group_list = PyFlameListWidget()
        list_batch_groups() # Add batch groups from desktop to listbox

        # Push Buttons
        self.close_batch_pushbutton = PyFlamePushButton(
            text='Close Batch',
            checked=self.settings.close_after_render,
            tooltip='Close batch groups after each render is completed.',
            )
        self.exit_flame = PyFlamePushButton(
            text='Exit Flame',
            tooltip='Save workspace and exit Flame when render is complete',
            )

        # Menu
        self.render_option_menu = PyFlameMenu(
            text=self.settings.render_option,
            menu_options=[
                'Foreground',
                'BG Reactor',
                ],
            )

        # Buttons
        self.render_btn = PyFlameButton(
            text='Render',
            connect=render,
            color=Color.BLUE
            )
        self.cancel_btn = PyFlameButton(
            text='Cancel',
            connect=cancel,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.batch_group_label, 0, 0, 1, 3)
        self.window.grid_layout.addWidget(self.batch_group_list, 1, 0, 8, 3)

        self.window.grid_layout.addWidget(self.render_option_label, 0, 3)
        self.window.grid_layout.addWidget(self.render_option_menu, 1, 3)

        self.window.grid_layout.addWidget(self.after_render_label, 3, 3)
        self.window.grid_layout.addWidget(self.close_batch_pushbutton, 4, 3)
        self.window.grid_layout.addWidget(self.exit_flame, 5, 3)

        self.window.grid_layout.addWidget(self.cancel_btn, 10, 2)
        self.window.grid_layout.addWidget(self.render_btn, 10, 3)

        #-------------------------------------

        # Set focus to batch group list
        self.batch_group_list.setFocus()

    def get_selected_batch_groups(self) -> None:
        """
        Get Selected Batch Groups
        =========================

        Get the index of the selected batch groups.
        """

        self.batchgroup_selection = [batch for batch in self.selection]

        self.selected_batch_groups = []

        for b in self.desktop_batch_group_object_list:
            if b in self.batchgroup_selection:
                batch_num = self.desktop_batch_group_object_list.index(b)
                self.selected_batch_groups.append(batch_num)

    def render_selected_batch_groups(self) -> None:
        """
        Render Selected Batch Groups
        ============================

        Render selected batch groups.
        """

        self.get_selected_batch_groups()

        self.render_batch_groups()

    def render_batch_groups(self) -> None:
        """
        Render Batch Groups
        ===================

        Render batch groups.

        Open progress window and render batch groups.

        If close_after_render is checked, close batch groups after rendering.

        If exit_flame is checked, exit Flame after rendering.
        """

        def open_progress_window() -> None:
            """
            Open Progress Window
            ===================

            Open progress window.
            """

            # Open Progress Window
            self.progress_window = PyFlameProgressWindow(
                total_tasks=self.num_batch_groups,
                title='Rendering...',
                parent=None,
                )

            # Set Progress Window Task
            if self.settings.render_option == 'Foreground':
                self.progress_window.task = 'Rendering Batch'
            elif self.settings.render_option == 'BG Reactor':
                self.progress_window.task = 'Submitting Batch Render to Background Reactor'

        def duplicate_render_nodes() -> None:
            """
            Duplicate Render Nodes
            ======================

            Duplicate render nodes to fix Flame bug where render nodes stop working.
            """

            for n in flame.batch.nodes:
                if n.type in ('Render', 'Write File'):
                    smart_replace = n.smart_replace
                    new_node = n.duplicate(keep_node_connections=True)
                    new_node.pos_x = n.pos_x
                    new_node.pos_y = n.pos_y
                    new_node.smart_replace = smart_replace
                    n.delete()

        def render_batch_group(batch_to_render) -> None:
            """
            Render Batch Group
            ==================

            Render batch group.

            Args:
                batch_to_render (flame.PyBatchGroup):
                    Batch group to render.
            """

            # Check for Render or Write node before rendering
            # If none found, skip and print message
            if [node for node in batch_to_render.nodes if node.type in ('Render', 'Write File')] == []:
                self.failed_render_list.append(batch_to_render.name)
                pyflame.print(
                    text=f'{batch_to_render.name} has no render or write nodes. Skipping.',
                    print_type=PrintType.WARNING,
                    )
            else:
                # Replace render/write nodes - fix for flame render node bug
                duplicate_render_nodes()

                # Render - if render fails add to failed render list
                if self.settings.render_option == 'Foreground':
                    batch_to_render.render(render_option='Foreground')
                elif self.settings.render_option == 'BG Reactor':
                    try:
                        batch_to_render.render(render_option='Background Reactor')
                        pyflame.print(f'{str(batch_to_render.name)[1:-1]}: Submitted to Background Reactor')
                        # Wait for 1 second to allow time for render to be submitted. Renders submitted to fast cause
                        # renders to be skipped.
                        time.sleep(1)
                    except RuntimeError:
                        self.failed_render_list.append(batch_to_render.name)
                        self.reactor_render_success = False

            # Update Progress
            self.batch_groups_rendered += 1

        def set_progress_window_complete() -> None:
            """
            Set Progress Window Complete
            ==========================

            Set progress window render complete.
            """

            # Set Progress Window Render Complete
            self.progress_window.tasks_complete = True
            if self.settings.render_option == 'Foreground':
                pyflame.print('Rendering Complete')
                self.progress_window.title = 'Rendering Complete'
            elif self.settings.render_option == 'BG Reactor':
                pyflame.print('Submitting Renders Complete')
                self.progress_window.title = 'Submitting Renders Complete'

        def show_failed_renders() -> None:
            """
            Show Failed Renders
            ==================

            Show failed renders if any renders fail.
            """

            failed_renders = ''

            if self.settings.render_option == 'BG Reactor' and not self.reactor_render_success:
                self.progress_window.title = 'Render Failed'
                self.progress_window.line_color = Color.RED
                self.progress_window.text = '\n\nFailed to submit batch render to Background Reactor. Try rendering in Foreground.'
                return

            # If any renders fail, show list when done
            if self.failed_render_list != []:
                for fail in self.failed_render_list:
                    failed_renders += fail

                # Send list of failed renders to progress window
                self.progress_window.title = 'Render Failed'
                self.progress_window.line_color = Color.YELLOW
                self.progress_window.text = self.progress_window.text + f'\n\nThese batch groups failed to render:\n{failed_renders}'
                return

        def exit_flame() -> None:
            """
            Exit Flame
            ==========

            Exit Flame if exit_flame is checked.
            """

            if self.exit_flame.checked:
                pyflame.print('Exiting Flame')
                self.progress_window.close()
                flame.exit()

        # Get number of batch groups to render
        self.num_batch_groups = len(self.selected_batch_groups)

        # Open Progress Window
        open_progress_window()

        # Initialize batch groups rendered
        self.batch_groups_rendered = 1

        # Render Selected Batch Groups
        for batch_group_number in self.selected_batch_groups:

            # Set Progress Window Progress
            self.progress_window.processing_task = self.batch_groups_rendered
            batch_to_render = self.desktop_batch_group_object_list[batch_group_number]

            # Open Selected Batch Group
            batch_to_render.open()

            # Close other batch groups if close_after_render is checked
            if self.settings.close_after_render:
                try:
                    for batch in self.desktop_batch_group_object_list:
                        if batch != batch_to_render:
                            batch.close()
                except:
                    pass

            # Render Selected Batch Group
            render_batch_group(batch_to_render)

        set_progress_window_complete()

        show_failed_renders()

        # Exit Flame if exit_flame is checked
        exit_flame()

#-------------------------------------

def render_selected(selection):

    pyflame.print_title(f'{SCRIPT_NAME} - Render Selected {SCRIPT_VERSION}')

    script = MultiBatchRender(selection)
    script.render_selected_batch_groups()
    return script

def main_render_window(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    script = MultiBatchRender(selection)
    script.main_window()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_batch(selection):

    for item in selection:
        if isinstance(item, flame.PyBatch):
            item_parent = item.parent
            if isinstance(item_parent, flame.PyDesktop):
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
                    'name': 'Render Selected Batch Groups',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_batch,
                    'execute': render_selected,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Multi-Batch Render',
                    'order': 1,
                    'separator': 'below',
                    'execute': main_render_window,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
