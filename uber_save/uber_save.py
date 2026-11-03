# Uber Save
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT
 
"""
Script Name: Uber Save
Script Version: 5.2.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 07.28.19
Update Date: 11.02.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch / Media Panel

Description:

    Save/Save Iterate one or more batch groups to the set path by right-clicking on a selection of batch groups in the desktop, a library
    or a library folder, or an open batch group in the batch view.

Usage:

    To save batch groups to a custom path, create a new path in the script setup window (Flame Main Menu -> Logik -> Logik Portal Script Setup ->
    Uber Save Setup) then select it in the dropdown menu and save.

    If multiple paths have been created, the one selected in the dropdown menu will be used to save batch groups.

    Batch groups in a library or library folder can't be saved where they are. Each one is moved to the desktop,
    saved, and moved back to its library or folder, one at a time in the order they were selected. Nothing is
    copied or deleted. When done, batch switches back to the batch group that was open before.

    The path can be tokenized using the following tokens:
        <ProjectName> - Adds name of current Flame project to path
        <ProjectNickName> - Adds Flame project nickname to path
        <SeqName> - Will try to guess shot sequence name from the batch group name - for example: PYT_0100_comp will give a sequence name of: pyt
        <SEQNAME> - Will do the same as above but give the sequence name in all caps - for example: PYT_0100_comp will give a sequence name of: PYT
        <ShotName> - Adds shot name to path. Will first try getting shot name from batch group tag, then render/write node, then it will try to
                     guess shot name from batch group name - for example: PYT_0100_comp will give a shot name of: PYT_0100.
        <BatchGroupName> - Adds name of batch group to path
        <YYYY> - Adds current year to path
        <YY> - Adds current year to path (last two digits)
        <MM> - Adds current month to path
        <DD> - Adds current day to path

URL:

    https://logik-portal.com/scripts/uber_save

Menus:

    Flame Main Menu -> Logik -> Logik Portal Script Setup -> Uber Save Setup

    Right-click selected batchgroups in Media Panel -> Uber Save... -> Save Selected Batchgroups
    Right-click selected batchgroups in Media Panel -> Uber Save... -> Iterate and Save Selected Batchgroups

    Right-click on Desktop in Media Panel -> Uber Save... -> Save All Batchgroups

    Right-click in Batch -> Uber Save... -> Save Current Batchgroup
    Right-click in Batch -> Uber Save... -> Iterate and Save Current Batchgroup

To install:

    Copy script into /opt/Autodesk/shared/python/uber_save

Updates:

    v5.2.0 11.02.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Save Selected / Iterate and Save Selected now work on batch groups in libraries and folders:
          each one is moved to the Desktop, saved, and moved back, one at a time in selection order.
        - A save path with a token that resolves to nothing (such as an empty project nickname) or a
          token that can't be resolved is now reported as an error instead of saving to the wrong
          folder or creating a folder named after the token.
        - The Setup window can't be used while the New / Edit / Duplicate path window is open.
        - Duplicating a duplicated path no longer stacks the names. Duplicates are named Copy, Copy 2,
          Copy 3 and so on.
        - Browse in the New / Edit / Duplicate path window now starts at the path being edited.
        - Items in the selection that aren't batch groups are now skipped with a warning in the
          console. Before, folders named after the path tokens were created for them and the save
          failed with a misleading error.
        - Saving a path with the name of another saved path now shows an error instead of replacing
          that path. Spaces at the start and end of path names and paths are removed.
        - Fixed a failed save being reported as saved. A save folder that can't be written to is now
          reported before the batch group is iterated, and a batch setup that isn't saved is reported
          as an error.
        - Delete in Setup now asks for confirmation, and no longer selects and saves another path when
          the selected path is deleted. No path is selected until one is chosen and saved.
        - A saved path is now selected when no path is selected, so saving works without clicking Save
          in Setup.

    v5.1.0 08.18.26
        - Simplified/improved the process of creating and saving paths further.
        - Updated to PyFlameLib v5.5.0.

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

from __future__ import annotations

import os
import re

import flame
from lib.pyflame_lib_uber_save import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Uber Save'
SCRIPT_VERSION = 'v5.2.0'
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

        def duplicate_name(source_name: str) -> str:
            """
            Duplicate Name
            ==============

            Get a unique name for a duplicated path. A trailing ' Copy' or ' Copy <n>' is removed from the source
            name first so names don't stack ('Foo Copy Copy').

            Args
            ----
                source_name (str): Name of the path being duplicated.

            Returns
            -------
                new_name (str): First of 'base Copy', 'base Copy 2', 'base Copy 3'... not used by a saved path.
            """

            base_name = re.sub(r' Copy( \d+)?$', '', source_name)

            new_name = f'{base_name} Copy'
            copy_number = 2
            while new_name in self.settings.paths:
                new_name = f'{base_name} Copy {copy_number}'
                copy_number += 1

            return new_name

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

                    if path_name == '':
                        PyFlameMessageWindow(
                            message='Enter path name.',
                            message_type=MessageType.ERROR,
                            parent=paths_window,
                        )
                        return False

                    if tokenized_path == '':
                        PyFlameMessageWindow(
                            message='Enter tokenized path.',
                            message_type=MessageType.ERROR,
                            parent=paths_window,
                        )
                        return False

                    # Don't replace another saved path with the same name
                    if path_name in self.settings.paths and not (type == 'Edit' and path_name == original_path_name):
                        PyFlameMessageWindow(
                            message=f'A path named {path_name} already exists. Enter a different name.',
                            message_type=MessageType.ERROR,
                            parent=paths_window,
                        )
                        return False

                    return True

                # Get new values. Strip spaces, the saved paths menu drops leading spaces from names.
                path_name = path_name_entry.text.strip()
                tokenized_path = tokenized_path_entry.text.strip()

                # Check settings, if not ok, return
                settings_verify = settings_check()
                if not settings_verify:
                    return

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

                # Select this path if no valid path is selected, so save actions don't fail
                if self.settings.selected_path_name not in self.settings.paths:
                    self.settings.selected_path_name = path_name

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

                Browse for custom path and set custom path entry to selected path. Start at the path being
                edited, cut at the first token and moved up to the nearest existing folder.
                """

                # Get the nearest existing folder of the path being edited
                browse_path = tokenized_path_entry.text.split('<', 1)[0].strip()
                while browse_path and not os.path.isdir(browse_path):
                    parent_path = os.path.dirname(browse_path)
                    if parent_path == browse_path:
                        break
                    browse_path = parent_path
                if not browse_path or not os.path.isdir(browse_path):
                    browse_path = '/'

                file_path = pyflame.file_browser(
                    path=browse_path,
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
                path_name = duplicate_name(self.saved_paths_menu.text)
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

            # Block the Setup window while this window is open. PyFlameWindow is already shown, and Qt only
            # applies a modality change when the window is shown again.
            paths_window.hide()
            paths_window.setWindowModality(QtCore.Qt.WindowModal)
            paths_window.show()

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

            Ask for confirmation, then delete selected path from config file and update saved paths menu. Deleting the
            selected path clears the selection. If no path is selected, print error message.
            """

            if self.saved_paths_menu.text == '':
                pyflame.print('No path to delete.')
            else:
                path_name = self.saved_paths_menu.text
                deleting_selected = path_name == self.settings.selected_path_name

                # Confirm delete
                message = f'Delete path: {path_name}?'
                if deleting_selected:
                    message += '\n\nThis is the selected path. Uber Save will have no path selected until Save is clicked in this window.'

                if not PyFlameMessageWindow(
                    message=message,
                    message_type=MessageType.WARNING,
                    parent=self.setup_window,
                    ):
                    return

                self.settings.paths.pop(path_name)

                # Clear the saved selection if it was deleted so save actions don't use another path
                if deleting_selected:
                    self.settings.selected_path_name = ''

                self.settings.save_config()

                # Show the saved selection if it still exists, otherwise the menu falls back to a remaining path
                self.saved_paths_menu.update_menu(
                    text=self.settings.selected_path_name if self.settings.paths else '',
                    menu_options=list(self.settings.paths.keys()),
                    connect=update_selected_path_entry,
                    )

                self.selected_path_entry.text = self.settings.paths.get(self.saved_paths_menu.text, {}).get('tokenized_path', ' ')

                pyflame.print(f'Path Deleted: {path_name}')

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
                If a path token could not be resolved, a token resolved to nothing, or the resolved path
                could not be created.
        """

        print('Resolving Batch Save Path...\n')

        resolved_save_path = pyflame.resolve_tokens(
            tokenized_string=self.batch_path,
            flame_pyobject=batch_group,)

        # Stop before creating folders if a token wasn't resolved
        unresolved_tokens = re.findall(r'<[^<>/]+>', resolved_save_path)
        if unresolved_tokens:
            raise OSError(f'Path token not resolved: {", ".join(unresolved_tokens)}')

        # Stop before creating folders if a token resolved to nothing, so setups aren't saved a folder too high
        tokenized_parts = self.batch_path.rstrip('/').split('/')
        resolved_parts = resolved_save_path.rstrip('/').split('/')
        if '' not in tokenized_parts[1:] and ('' in resolved_parts[1:] or len(resolved_parts) < len(tokenized_parts)):
            raise OSError('Part of the save path resolved to nothing. Check the tokens in the path, for example an empty Flame project nickname with <ProjectNickName>, or <SEQNAME> / <SeqName> with a batch group name that starts with a number.')

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
            OSError:
                If the save folder is not writable or the batch setup could not be saved.

            Exception:
                If the batch group could not be saved. Handled by save_batch_groups.
        """

        selected_batch_name = str(batch_group.name)[1:-1]
        pyflame.print(f'Saving Batch Group: {selected_batch_name}', new_line=False, text_color=TextColor.GREEN)
        print('-' * 80)

        # Stop before opening or iterating if the save folder can't be written to
        if not os.access(save_path, os.W_OK):
            raise OSError(f'Save folder is not writable: {save_path}')

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
        if batch_group.save_setup(shot_save_path) is False:
            raise OSError(f'Batch setup could not be saved: {shot_save_path}')

        pyflame.print(f'Batch Saved: {selected_batch_name}', new_line=False)
        print('-' * 80, '\n')

    # ==============================================================================

    def save_library_batch_group(self, batch_group, iterate: bool) -> None:
        """
        Save Library Batch Group
        ========================

        Save a batch group that is in a library or library folder. Flame can't save a batch group there,
        so it is moved to the current Desktop, saved, then always moved back to where it was.

        The batch group object is used throughout (first the selected object, then the object returned
        by the move). It is never looked up by name, since a moved batch group isn't renamed.

        Args
        ----
            batch_group (flame.PyBatch):
                Batch group in a library or library folder.

            iterate (bool):
                Iterate up before saving.

        Raises
        ------
            OSError:
                If a path token could not be resolved, the save folder is not writable, the batch group
                could not be moved to the Desktop, or it could not be moved back (it is then left on the
                Desktop).

            Exception:
                If the batch group could not be saved. Handled by save_batch_groups.
        """

        # Resolve path and check it can be written to before the batch group is moved
        save_path = self.resolve_path(
            batch_group=batch_group,
            )

        if not os.access(save_path, os.W_OK):
            raise OSError(f'Save folder is not writable: {save_path}')

        original_parent = batch_group.parent
        original_parent_name = str(original_parent.name)[1:-1]
        desktop = flame.project.current_project.current_workspace.desktop

        # Move batch group to the Desktop so it can be saved. Use the returned object from now on
        moved = flame.media_panel.move(batch_group, desktop)
        if not isinstance(moved, list) or not moved:
            raise OSError(f'Batch group could not be moved to the Desktop from {original_parent_name}.')
        moved_group = moved[0]

        save_error = None
        try:
            self.save_batchgroup(
                save_path=save_path,
                batch_group=moved_group,
                iterate=iterate,
                )
        except Exception as e:
            save_error = e

        # Always move batch group back. A closed Desktop batch group can't be moved, so open it first
        try:
            if not moved_group.opened:
                moved_group.open()
            moved_back = flame.media_panel.move(moved_group, original_parent)
            if not isinstance(moved_back, list) or not moved_back:
                raise OSError('Move returned nothing.')
        except Exception as e:
            move_back_message = f'Batch group was left on the Desktop and could not be moved back to {original_parent_name}: {e}'
            if save_error is not None:
                raise OSError(f'{save_error}\n{move_back_message}')
            raise OSError(move_back_message)

        if save_error is not None:
            raise save_error

    # ==============================================================================

    def restore_active_batch_group(self, active_uid: str) -> None:
        """
        Restore Active Batch Group
        ==========================

        Switch Batch back to the batch group that was active before batch groups in libraries or folders
        were moved. Moving batch groups can make Flame switch Batch to another batch group.

        A failure is printed as a warning and isn't reported as a save error.

        Args
        ----
            active_uid (str): uid of the batch group that was active before saving.
        """

        try:
            # Find Desktop batch group that was active, by uid (Desktop batch groups weren't moved, so their uid is unchanged)
            active_batch_group = None
            for desktop_batch_group in flame.project.current_project.current_workspace.desktop.batch_groups:
                if str(desktop_batch_group.uid) == active_uid:
                    active_batch_group = desktop_batch_group
                    break

            if active_batch_group is None:
                return

            # Do nothing if it is still active
            if flame.batch is not None and str(flame.batch.uid) == active_uid:
                return

            # open() doesn't switch Batch to an already open batch group, so close it first
            if active_batch_group.opened:
                active_batch_group.close()
            active_batch_group.open()
        except Exception as e:
            pyflame.print(f'Could not switch Batch back to the batch group that was active before: {e}', print_type=PrintType.WARNING)

    # ==============================================================================

    def save_batch_groups(self, batch_groups, iterate: bool, complete_message: str) -> None:
        """
        Save Batch Groups
        =================

        Save each batch group. Failures are collected and reported once after all
        batch groups have been processed so a bad path does not open one message
        window per batch group. Items that aren't batch groups are skipped with a
        console warning.

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
        library_group_moved = False

        # Remember active batch group so Batch can be switched back to it after batch groups in libraries or folders are moved
        try:
            active_uid = str(flame.batch.uid)
        except Exception:
            active_uid = None

        for batch_group in batch_groups:

            # Skip items that aren't batch groups before their path is resolved, so no folders are made for them
            if not isinstance(batch_group, flame.PyBatch):
                try:
                    item_name = str(batch_group.name)[1:-1]
                except Exception:
                    item_name = str(batch_group)
                pyflame.print(f'Skipped, not a batch group: {item_name}', print_type=PrintType.WARNING)
                continue

            batch_group_name = str(batch_group.name)[1:-1]

            try:
                # Batch groups in a library or folder are moved to the Desktop to be saved, then moved back
                if not isinstance(batch_group.parent, flame.PyDesktop):
                    library_group_moved = True
                    self.save_library_batch_group(
                        batch_group=batch_group,
                        iterate=iterate,
                        )
                else:
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

        if library_group_moved and active_uid is not None:
            self.restore_active_batch_group(active_uid)

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

        Save selected batchgroups in desktop, libraries or library folders.
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

        Iterate and save selected batchgroups in desktop, libraries or library folders.
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
    Save selected batchgroups in desktop, libraries or library folders.
    """

    uber_save = UberSave(selection)
    if uber_save.valid:
        uber_save.batch_group_save_selected()

def uber_batch_group_iterate_save_selected(selection) -> None:
    """
    Iterate and save selected batchgroups in desktop, libraries or library folders.
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
