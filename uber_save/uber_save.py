# Rename Shots
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
Script Name: Uber Save
Script Version: 5.1.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 07.28.19
Update Date: 08.18.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Custom Action Type: Batch / Media Panel

Description:

    Save/Save Iterate one or more batch groups to the set path by right-clicking on a selection of batch groups in the desktop or an
    open batch group in the batch view.

Usage:

    To save batch groups to a custom path, create a new path in the script setup window(Flame Main Menu -> Logik -> Logik Portal Script Setup ->
    Uber Save Setup) then select it in the dropdown menu and save.

    If multiple paths have been created, the one selected in the dropdown menu will be used to save batch groups.

    The path can be tokenized using the following tokens:
        <ProjectName> - Adds name of current Flame project to path
        <ProjectNickName> - Adds Flame project nicknick to path
        <DesktopName> - Adds name of current desktop to path
        <SeqName> - Will try to guess shot seqeunce name from the batch group name - for example: PYT_0100_comp will give a sequence name of: pyt
        <SEQNAME> - Will do the same as above but give the sequence name in all caps - for example: PYT_0100_comp will give a sequence name of: PYT
        <ShotName> - Adds shot name to path. Will first try getting shot name from batch group tag, then render/write node, then it will try to
                     guess shot name from batch group name - for example: PYT_0100_comp will give a shot name of: PYT_0100.
        <BatchGroupName> - Adds name of batch group to path
        <YYYY> - Adds current year to path
        <YY> - Adds current year to path (last two digits)
        <MM> - Adds current month to path
        <DD> - Adds current day to path

URL:

    https://github.com/logik-portal/python/uber_save

Menus:

    Flame Main Menu -> Logik -> Logik Portal Script Setup -> Uber Save Setup

    Right-click selected batchgroups in desktop -> Uber Save... -> Save Selected Batchgroups
    Right-click selected batchgroups in desktop -> Uber Save... -> Iterate and Save Selected Batchgroups

    Right-click on desktop in media panel -> Uber Save... -> Save All Batchgroups

    Right-click in batch -> Uber Save... -> Save Current Batchgroup
    Right-click in batch -> Uber Save... -> Iterate and Save Current Batchgroup

To install:

    Copy script into /opt/Autodesk/shared/python/uber_save

Updates:

    v5.1.0 08.18.26
        - Simplified/improved the process of creating and saving paths further.
        - Updated to PyFlameLib v5.6.0.

    v5.0.0 06.07.25
        - Updated to PyFlameLib v5.0.0.
        - Removed Preset Manager for simplicity. Presets are now saved in script setup window.

    v4.9.0 04.10.25
        - Updated to PyFlameLib v4.3.0.

    v4.8.0 12.03.25
        - Fixed misc bugs.
        - Batch Group tagging can now be used to save batch groups to the correct shot folder even if the batch group doesn't have the shot name in the name.
        - Updated to PyFlameLib v4.0.0.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v4.7.0 10.02.24
        - Updated to PyFlameLib v3.2.0.

    v4.6.0 06.13.24
        - Added path tokens for Year (YYYY), Year (YY), Month (MM), and Day (DD).

    v4.5.0 05.05.24
        - Simplified tokenzied path setup.
        - Added BatchGroupName token to available path tokens. This will add the name of the selected batch group to the path.
        - Updated Preset Manager to use new PyFlamePresetManager class.
        - Updates to UI/PySide.
        - Updated to pyflame lib v2.2.0.
        - Updated script versioning to semantic versioning.

    v4.4 03.03.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.
        - Updated menus for Flame 2023.2+.
        - Improvements to Preset Window.

    v4.3 06.20.22
        - Messages print to Flame message window - Flame 2023.1 and later.
        - Added Flame file browser - Flame 2023.1 and later.
        - Preset window code cleaned up and moved to imported pyflame_lib.
        - Default preset can now be set in the preset window.
        - Uber Save menu was incorrectly showing up when right-clicking on batch groups saved in a desktop that is saved to the library. Batch
          groups can not be saved from the library. This menu no longer shows up.

    v4.2 03.18.22
        - Moved UI widgets to external file (pyflame_lib.py).

    v4.1 03.06.22
        - Updated UI for Flame 2023.

    v4.0 12.28.21
        - Added ability to save presets so different settings can be used with different Flame projects.

    v3.2 10.11.21
        - Removed JobName token - not needed with new project nick name token.
        - Removed Desktop Name token.
        - Shot name token improvements.

    v3.1 07.10.21
        - Fixed problem when trying to save on a flare. Added check for flame and flare batch folders.
        - ProjectName token now uses exact flame project name. No longer tries to guess name of project on server. If flame
          project name is different than server project name, set flame project nickname and use ProjectNickName token.
        - Fixed sequence token when using batch group name as save type.

    v3.0 06.08.21
        - Updated to be compatible with Flame 2022/Python 3.7.
        - Improvements to shot name detection.
        - Speed improvements when saving.

    v2.0 10.08.20:
        - Updated UI.
        - Improved iteration handling.
        - Added SEQNAME token to add sequence name in caps to path.

    v1.91 05.13.20:
        - Fixed iterating: When previous iterations were not in batchgroup, new itereations would reset to 1.
        - Iterations now continue from current iteration number.

    v1.9 03.10.20:
        - Fixed Setup UI for Linux.

    v1.7 12.29.19:
        - Menu now appears as Uber Save in right-click menu.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re

import flame
from lib.pyflame_lib_uber_save import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Uber Save'
SCRIPT_VERSION = 'v5.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

def load_config() -> PyFlameConfig:
    """
    Load Config
    ===========

    Load Preset Manager config values from config file.

    Returns
    -------
        settings (PyFlameConfig):
            PyFlameConfig object with loaded config values
    """

    settings = PyFlameConfig(
        config_values={
                'selected_path_name': '',
                'paths': {},
                },
            )

    return settings

class UberSaveSetup:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script install path
        if not pyflame.verify_script_install():
            return

        self.settings = load_config()

        self.setup()

    def setup(self) -> None:

        def paths_window(type: str) -> None:
            """
            New Edit Window
            ===============

            Create new path or edit existing path.
            """

            def save_path() -> None:

                def settings_check() -> bool:
                    """
                    Settings Check
                    ==============

                    Check settings for errors and return True if all is good.
                    """

                    if path_name_entry.text == '':
                        PyFlameMessageWindow(
                            message='Enter path name.',
                            message_type=MessageType.ERROR,
                            parent=paths_window,
                        )
                        return False

                    if tokenized_path_entry.text == '':
                        PyFlameMessageWindow(
                            message='Enter tokenized path.',
                            message_type=MessageType.ERROR,
                            parent=paths_window,
                        )
                        return False

                    return True

                # Check settings, if not ok, return
                settings_verify = settings_check()
                if not settings_verify:
                    return

                # Get new values
                path_name = path_name_entry.text
                tokenized_path = tokenized_path_entry.text

                # Delete old path in config file if path name has changed and we're in edit mode.
                if type == 'Edit' and original_path_name != path_name:
                    self.settings.paths.pop(original_path_name)

                    # Move the saved selection to the new name so the config doesn't
                    # point at a path name that no longer exists.
                    if self.settings.selected_path_name == original_path_name:
                        self.settings.selected_path_name = path_name

                    self.settings.save_config()

                # Update settings attributes with new values and save config
                self.settings.paths[path_name] = {
                    'path_name': path_name,
                    'tokenized_path': tokenized_path,
                    }
                self.settings.save_config()

                # Update saved paths menu
                self.saved_paths_menu.update_menu(
                    text=path_name,
                    menu_options=list(self.settings.paths.keys()),
                    connect=update_selected_path_entry,
                    )
                self.selected_path_entry.text = tokenized_path
                pyflame.print(f'New Path Saved: {path_name}')

                # Close window
                paths_window.close()

            def path_browse() -> None:
                """
                Path Browse
                ===========

                Browse for custom path and set custom path entry to selected path.
                """

                file_path = pyflame.file_browser(
                    path=self.selected_path_entry.text,
                    title='Select Directory',
                    select_directory=True,
                    window_to_hide=[self.setup_window, paths_window],
                    )

                if file_path:
                    tokenized_path_entry.text = str(file_path)

            def close_window() -> None:
                """
                Close Window
                ============
                """

                paths_window.close()

            if type == 'New':
                path_name = ''
                tokenized_path = ''
                original_path_name = ''
            elif type == 'Duplicate':
                path_name = pyflame.generate_unique_name(value=self.saved_paths_menu.text, existing_names=list(self.settings.paths.keys()))
                original_path_name = path_name
                tokenized_path = self.selected_path_entry.text
            else:
                path_name = self.saved_paths_menu.text
                original_path_name = path_name
                tokenized_path = self.selected_path_entry.text

            # ==============================================================================

            paths_window = PyFlameWindow(
                title=f'{SCRIPT_NAME} Setup - {type} Path <small>{SCRIPT_VERSION}</small>',
                return_pressed=save_path,
                escape_pressed=close_window,
                grid_layout_columns=6,
                grid_layout_rows=4,
                parent=self.setup_window,
                )

            # Labels
            path_name_label = PyFlameLabel(
                text='Path Name',
                )
            tokenized_path_label = PyFlameLabel(
                text='Tokenized Path',
                )

            # Entries
            path_name_entry = PyFlameEntry(
                text=path_name,
                )
            tokenized_path_entry = PyFlameEntry(
                text=tokenized_path,
                )

            # Token Menu
            path_token_menu = PyFlameTokenMenu(
                token_dict={
                    'Project Name': '<ProjectName>',
                    'Project Nick Name': '<ProjectNickName>',
                    'Sequence Name': '<SeqName>',
                    'Sequence Name (All Caps)': '<SEQNAME>',
                    'Shot Name': '<ShotName>',
                    'Batch Group Name': '<BatchGroupName>',
                    'Year (YYYY)': '<YYYY>',
                    'Year (YY)': '<YY>',
                    'Month (MM)': '<MM>',
                    'Day (DD)': '<DD>',
                    },
                token_dest=tokenized_path_entry,
                )

            # Buttons
            browse_button = PyFlameButton(
                text='Browse',
                connect=path_browse,
                )

            save_button = PyFlameButton(
                text='Save',
                connect=save_path,
                color=Color.BLUE,
                )
            cancel_button = PyFlameButton(
                text='Cancel',
                connect=close_window,
                )

            # ==============================================================================
            # [Widget Layout]
            # ==============================================================================

            paths_window.grid_layout.addWidget(path_name_label, 0, 0)
            paths_window.grid_layout.addWidget(path_name_entry, 0, 1, 1, 3)

            paths_window.grid_layout.addWidget(tokenized_path_label, 1, 0)
            paths_window.grid_layout.addWidget(tokenized_path_entry, 1, 1, 1, 3)
            paths_window.grid_layout.addWidget(path_token_menu, 1, 4)
            paths_window.grid_layout.addWidget(browse_button, 1, 5)

            paths_window.grid_layout.addWidget(cancel_button, 3, 4)
            paths_window.grid_layout.addWidget(save_button, 3, 5)

            # ==============================================================================

            path_name_entry.set_focus()

            # Set Tab-key Order
            paths_window.tab_order = [path_name_entry, tokenized_path_entry]

        def update_selected_path_entry() -> None:
            """
            Update Selected Path Entry
            ==========================

            Update selected path entry with selected path from saved paths menu.
            """

            self.selected_path_entry.text = self.settings.paths.get(self.saved_paths_menu.text, {}).get('tokenized_path', ' ')

        def new_path() -> None:
            """
            New Path
            ========

            Open paths_window to create new path.
            """

            paths_window(type='New')

        def edit_path() -> None:
            """
            Edit Path
            =========

            Open paths_window to edit selected path.
            """

            if self.saved_paths_menu.text == '':
                pyflame.print('No path to edit.')
            else:
                paths_window(type='Edit')

        def delete_path() -> None:
            """
            Delete Path
            ===========

            Delete selected path from config file and update saved paths menu. If no path is selected, print error message.
            """

            if self.saved_paths_menu.text == '':
                pyflame.print('No path to delete.')
            else:
                self.settings.paths.pop(self.saved_paths_menu.text)

                self.saved_paths_menu.update_menu(
                    text=self.settings.selected_path_name,
                    menu_options=list(self.settings.paths.keys()),
                    connect=update_selected_path_entry,
                    )

                # Menu falls back to a remaining path, or empty when none are left.
                # Save that so the config doesn't point at a deleted path.
                self.settings.save_config(
                    config_values={
                        'selected_path_name': self.saved_paths_menu.text,
                        }
                    )

                self.selected_path_entry.text = self.settings.paths.get(self.saved_paths_menu.text, {}).get('tokenized_path', ' ')

                pyflame.print(f'SelectedPath Deleted: {self.saved_paths_menu.text}')

        def duplicate_path() -> None:
            """
            Duplicate Path
            ==============

            Duplicate selected path and open paths_window.
            """

            if self.saved_paths_menu.text == '':
                pyflame.print('No path to duplicate.')
            else:
             paths_window(type='Duplicate')

        def save() -> None:
            """
            Save
            ====

            Save selected path to config file.
            """

            if self.saved_paths_menu.text == '':
                PyFlameMessageWindow(
                    message='No path selected. Create a new path and try again.',
                    message_type=MessageType.ERROR,
                    parent=None,
                )
                return

            # Save config file
            self.settings.save_config(
                config_values={
                    'selected_path_name': self.saved_paths_menu.text,
                    }
                )

            # Close window
            self.setup_window.close()

        def close_window() -> None:

            self.setup_window.close()

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} Setup <small>{SCRIPT_VERSION}</small>',
            return_pressed=save,
            escape_pressed=close_window,
            grid_layout_columns=6,
            grid_layout_rows=5,
            parent=None,
            )

        # Labels
        self.path_type_label = PyFlameLabel(
            text='Path Type',
            )
        self.tokenized_path_label = PyFlameLabel(
            text='Tokenized Path',
            style=Style.UNDERLINE
            )
        self.saved_paths_label = PyFlameLabel(
            text='Saved Paths',
            )
        self.selected_path_label = PyFlameLabel(
            text='Selected Path',
            )

        # Entries
        self.selected_path_entry = PyFlameEntry(
            text=self.settings.paths.get(self.settings.selected_path_name, {}).get('tokenized_path', ' '),
            read_only=True,
            )

        # Menu
        self.saved_paths_menu = PyFlameMenu(
            text=self.settings.selected_path_name,
            menu_options=list(self.settings.paths.keys()),
            connect=update_selected_path_entry,
            )

        # Buttons
        self.new_path_button = PyFlameButton(
            text='New',
            connect=new_path,
            )
        self.edit_path_button = PyFlameButton(
            text='Edit',
            connect=edit_path,
            )
        self.delete_path_button = PyFlameButton(
            text='Delete',
            connect=delete_path,
            )
        self.duplicate_path_button = PyFlameButton(
            text='Duplicate',
            connect=duplicate_path,
            )

        self.save_button = PyFlameButton(
            text='Save',
            connect=save,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ==============================================================================
        # [Widget Layout]
        # ==============================================================================

        self.setup_window.grid_layout.addWidget(self.saved_paths_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.saved_paths_menu, 0, 1, 1, 3)

        self.setup_window.grid_layout.addWidget(self.new_path_button, 0, 4)
        self.setup_window.grid_layout.addWidget(self.edit_path_button, 0, 5)
        self.setup_window.grid_layout.addWidget(self.duplicate_path_button, 1, 4)
        self.setup_window.grid_layout.addWidget(self.delete_path_button, 1, 5)

        self.setup_window.grid_layout.addWidget(self.selected_path_label, 3, 0)
        self.setup_window.grid_layout.addWidget(self.selected_path_entry, 3, 1, 1, 6)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 5, 4)
        self.setup_window.grid_layout.addWidget(self.save_button, 5, 5)

        # ==============================================================================

        update_selected_path_entry()

class UberSave:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Set False until path is verified - Keep here.
        self.valid = False

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Get flame variables
        self.flame_prj_name = flame.project.current_project.project_name
        print('Flame Project Name:', self.flame_prj_name)

        self.flame_prj_nickname = flame.projects.current_project.nickname
        print('Flame Project Nickname:', self.flame_prj_nickname)

        self.settings = load_config()

        try:
            self.batch_path = self.settings.paths[self.settings.selected_path_name]['tokenized_path']
            print('Batch save path:', self.batch_path)
        except KeyError:
            PyFlameMessageWindow(
                message='No path selected.\n\nCreate a new path in script setup.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Uber Save Setup',
                message_type=MessageType.ERROR,
                parent=None,
            )
            return

        self.valid = True

    # ==============================================================================

    def resolve_path(self, batch_group) -> str:
        """
        Resolve Path
        ============

        Resolve path for batch setups folder.
        Any tokens in the path will be resolved.

        Resolves different paths for Flame and Flare.

        Args
        ----
            batch_group (flame.PyBatch): Batch group to use to resolve path.

        Returns
        -------
            resolved_save_path (str): Resolved path for batch setups.

        Raises
        ------
            OSError:
                If the resolved path could not be created.
        """

        print('Resolving Batch Save Path...\n')

        resolved_save_path = pyflame.resolve_tokens(
            tokenized_string=self.batch_path,
            flame_pyobject=batch_group,)

        os.makedirs(resolved_save_path, exist_ok=True)

        return resolved_save_path

    # ==============================================================================

    def save_batchgroup(self, save_path: str, batch_group, iterate: bool) -> None:
        """
        Save Batch Group
        ================

        Save batch group to batch setups folder. Iterate up if needed.

        If it's the first time a batch group is saved, a new iteration is created for the first iteration.

        Args
        ----
            save_path (str):
                Path to save batch setups.

            batch_group (flame.PyBatch):
                Batch group to save.

            iterate (bool):
                Iterate up before saving. Forced True on a batch group's first save.

        Raises
        ------
            Exception:
                If the batch group could not be saved. Handled by save_batch_groups.
        """

        selected_batch_name = str(batch_group.name)[1:-1]
        pyflame.print(f'Saving Batch Group: {selected_batch_name}', new_line=False, text_color=TextColor.GREEN)
        print('-' * 80)

        # Open batch if closed
        batch_group.open()

        # Get current iteration
        iteration_split = (re.split(r'(\d+)', str(batch_group.current_iteration.name)[1:-1]))[1:-1]
        current_iteration = int(iteration_split[-1])
        print('Current Iteration:', current_iteration)

        # Get latest iteration if iterations are saved
        if not batch_group.batch_iterations == []:
            latest_iteration = int(((re.split(r'(\d+)', str([i.name for i in batch_group.batch_iterations][-1])[1:-1]))[1:-1])[-1])
        else:
            latest_iteration = current_iteration
        print('Latest Iteration:', latest_iteration)

        # If first save of batch group, create first iteration
        if batch_group.batch_iterations == [] and current_iteration == 1:
            iterate = True

        # Iterate up if iterate up menu selected
        print('Iterate Up:', iterate)

        if iterate:
            if current_iteration == 1:
                batch_group.iterate()
            elif current_iteration < latest_iteration:
                batch_group.iterate(index = (latest_iteration + 1))
            else:
                batch_group.iterate(index = (current_iteration + 1))
            #print('--> Iterating Up\n')
        else:
            batch_group.iterate(index=current_iteration)
            #print('--> Overwriting Existing Iteration\n')

        # Get current iteration
        current_iteration = str(batch_group.current_iteration.name)[1:-1]
        print('New Iteration:', current_iteration)

        # Set batch save path
        shot_save_path = os.path.join(save_path, current_iteration)
        print('Shot Save Path:', shot_save_path)

        # Create shot save folder
        if not os.path.isdir(save_path):
            os.makedirs(save_path)

        # Hard save current batch iteration
        batch_group.save_setup(shot_save_path)

        pyflame.print(f'Batch Saved: {selected_batch_name}', new_line=False)
        print('-' * 80, '\n')

    # ==============================================================================

    def save_batch_groups(self, batch_groups, iterate: bool, complete_message: str) -> None:
        """
        Save Batch Groups
        =================

        Save each batch group. Failures are collected and reported once after all
        batch groups have been processed so a bad path does not open one message
        window per batch group.

        Args
        ----
            batch_groups (list[flame.PyBatch]):
                Batch groups to save.

            iterate (bool):
                Iterate up before saving.

            complete_message (str):
                Message printed when every batch group saved without error.
        """

        errors = []

        for batch_group in batch_groups:
            batch_group_name = str(batch_group.name)[1:-1]

            try:
                resolved_path = self.resolve_path(
                    batch_group=batch_group,
                    )

                self.save_batchgroup(
                    save_path=resolved_path,
                    batch_group=batch_group,
                    iterate=iterate,
                    )
            except Exception as e:
                pyflame.print(f'Batch Not Saved: {batch_group_name} - {e}', print_type=PrintType.ERROR)
                errors.append(f'{batch_group_name}: {e}')

        if errors:
            PyFlameMessageWindow(
                message='Batch groups not saved. Check path in setup.\n\n' + '\n\n'.join(errors),
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        pyflame.print(complete_message, text_color=TextColor.GREEN)

    # ==============================================================================

    def batch_group_save(self) -> None:
        """
        Batch Group Save
        ================

        Save current batch from batch.
        """

        self.save_batch_groups(
            batch_groups=[flame.batch],
            iterate=False,
            complete_message='Saving Batch Group Complete',
            )

    def batch_group_iterate_save(self) -> None:
        """
        Iterate and Save Batch Group
        ============================

        Iterate and save current batch from batch.
        """

        self.save_batch_groups(
            batch_groups=[flame.batch],
            iterate=True,
            complete_message='Saving and Iterating Batch Group Complete',
            )

    def batch_group_save_all(self) -> None:
        """
        Batch Group Save All
        ====================

        Save all batchgroups in desktop.
        """

        self.save_batch_groups(
            batch_groups=flame.project.current_project.current_workspace.desktop.batch_groups,
            iterate=False,
            complete_message='Saving all batch groups complete',
            )

    def batch_group_save_selected(self) -> None:
        """
        Batch Group Save Selected
        =========================

        Save selected batchgroups in desktop.
        """

        self.save_batch_groups(
            batch_groups=self.selection,
            iterate=False,
            complete_message='Saving selected batch groups complete',
            )

    def batch_group_iterate_save_selected(self) -> None:
        """
        Batch Group Iterate and Save Selected
        =====================================

        Iterate and save selected batchgroups in desktop.
        """

        self.save_batch_groups(
            batch_groups=self.selection,
            iterate=True,
            complete_message='Saving and iterating selected batch groups complete',
            )

# ==============================================================================

def uber_batch_group_save(selection) -> None:
    """
    Save current batch from batch.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_save()

def uber_batch_group_iterate_save(selection) -> None:
    """
    Iterate and save current batch from batch.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_iterate_save()

def uber_batch_group_save_all(selection) -> None:
    """
    Save all batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_save_all()

def uber_batch_group_save_selected(selection) -> None:
    """
    Save selected batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_save_selected()

def uber_batch_group_iterate_save_selected(selection) -> None:
    """
    Iterate and save selected batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_iterate_save_selected()

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_batch(selection) -> bool:

    for item in selection:
        if isinstance(item, flame.PyBatch):
            if isinstance(item.parent.parent, flame.PyWorkspace):
                return True
    return False

def scope_desktop(selection) -> bool:

    for item in selection:
        if isinstance(item, flame.PyDesktop):
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
                    'name': 'Uber Save Setup',
                    'execute': UberSaveSetup,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Uber Save...',
            'actions': [
                {
                    'name': 'Save All Batch Groups',
                    'isVisible': scope_desktop,
                    'execute': uber_batch_group_save_all,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Save Selected Batch Groups',
                    'isVisible': scope_batch,
                    'execute': uber_batch_group_save_selected,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Iterate and Save Selected Batch Groups',
                    'isVisible': scope_batch,
                    'execute': uber_batch_group_iterate_save_selected,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
            'name': 'Uber Save...',
            'actions': [
                {
                    'name': 'Save Current Batch Group',
                    'execute': uber_batch_group_save,
                    'minimumVersion': '2025'
                },
                {
                    'name': 'Iterate and Save Current Batch Group',
                    'execute': uber_batch_group_iterate_save,
                    'minimumVersion': '2025'
                }
            ]
        }
    ]
