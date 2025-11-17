# Uber Save
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
Script Name: Uber Save
Script Version: 4.9.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 07.28.19
Update Date: 04.10.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch / Media Panel

Description:

    Save/Save Iterate batch group iteration and batch setup file to custom path in one click.

Usage:

    Uber Save Preset Manager Window:

    - Manage multiple presets for Uber Save. Presets can be set as default for all Flame projects or for the current Flame project.

        New:
            Opens Uber Save Main Window to create new preset.

        Edit:
            Opens Uber Save Main Window to edit selected preset.

        Duplicate:
            Duplicates the selected preset. The new preset will have the same name as the original preset with COPY added at the end.

        Delete:
            Deletes the selected preset.

        Set Default Preset:
            Makes selected preset the default for all Flame projects.

        Set Project Preset:
            Makes selected preset the preset for the current Flame project. Overrides default preset for current project.

        Remove Project Preset:
            Removes preset from current project. Default preset will be used for current project. Does not delete the preset.

    Uber Save Main Window

        Preset Name:
            Set name for preset.

        Batch Save Path:
            Use this to define a tokenized folder structure to save batch setups to.

            Tokens:
                - <ProjectName> - Adds name of current Flame project to path
                - <ProjectNickName> - Adds Flame project nicknick to path
                - <DesktopName> - Adds name of current desktop to path
                - <SeqName> - Will try to guess shot seqeunce name from the batch group name - for example: PYT_0100_comp will give a sequence name of: pyt
                - <SEQNAME> - Will do the same as above but give the sequence name in all caps - for example: PYT_0100_comp will give a sequence name of: PYT
                - <ShotName> - Adds shot name to path. Will first try getting shot name from render/write node. If not found, will try to guess shot name
                             from batch group name - for example: PYT_0100_comp will give a shot name of: PYT_0100.
                - <BatchGroupName> - Adds name of batch group to path
                - <YYYY> - Adds current year to path
                - <YY> - Adds current year to path (last two digits)
                - <MM> - Adds current month to path
                - <DD> - Adds current day to path

            Example:
                - /opt/Autodesk/project/<ProjectName>/batch/flame/<ShotName>

    Batch Group Shot Name Tagging

        You can now tag batch groups with a specific shot name using the format:
            ShotName: <shot_name>

        Example:

            - Batch Group Name: tracking_fix
            - Batch Group Tag: ShotName: PYT_0100_comp
            - Save Path Template: /JOBS/<ProjectName>/Shots/<ShotName>/Batch

            - Result: /JOBS/<ProjectName>/Shots/PYT_0100/Batch

        This allows you to save batch groups to the correct shot folder even when
        the batch group name doesn't contain the shot name.

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

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re

import flame
from lib.pyflame_lib_uber_save import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Uber Save'
SCRIPT_VERSION = 'v4.9.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
PRESETS_PATH = os.path.join(SCRIPT_PATH, 'config', 'presets')

#-------------------------------------
# [Main Script]
#-------------------------------------

class UberSaveSetup():

    def __init__(self, settings=None):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # If settings are passed, use them, else load config settings to use default settings
        if settings is not None:
            self.settings = settings
        else:
            self.settings = self.load_config()

        self.setup()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Load Preset Manager config values from config file.

        Returns:
        --------
            settings (PyFlameConfig):
                PyFlameConfig object with loaded config values
        """

        settings = PyFlameConfig(
            config_values={
                'preset_name': 'New Preset',
                'batch_path': '/opt/Autodesk/project/<ProjectName>/batch/flame/<ShotName>',
                },
            script_name='New Preset',
            )

        return settings

    #-------------------------------------

    def save_preset(self):

        # Check for required fields
        if not self.preset_name_entry.text():
            error_message('Preset Name: Enter name for preset.')
            return
        elif not self.batch_path_entry.text():
            error_message('Batch Path: Enter Batch Path.')
            return

        # Get preset name
        preset_name_text = self.preset_name_entry.text()

        # If preset already exists, ask user if they want to overwrite
        if [f for f in os.listdir(PRESETS_PATH) if f[:-4] == preset_name_text]:
            if not warning_message('A preset with this name already exists. Replace existing?'):
                return

        # Update settings attributes with new values
        self.settings={
            'preset_name': preset_name_text,
            'batch_path': self.batch_path_entry.text(),
            }

        # Close setup window
        self.setup_window.close()

    def setup(self):

        def path_browse() -> None:
            """
            Path Browse
            ===========

            Browse for custom path and set custom path entry to selected path.

            use_flame_browser=False is intentionally set. Using Flame's files browser causes Flame to crash.
            Probably an issue with the setup window needing to be hidden.
            """

            file_path = pyflame.file_browser(
                path=self.batch_path_entry.text(),
                title='Select Directory',
                select_directory=True,
                use_flame_browser=False,
                )

            if file_path:
                self.batch_path_entry.setText(file_path)

        def cancel() -> None:
            """
            Cancel
            ======

            Close setup window and set preset name to None.
            """

            # Close setup window
            self.setup_window.close()

            # Set preset name to None
            self.settings = None

        self.setup_window = PyFlameDialogWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            return_pressed=self.save_preset,
            grid_layout_columns=6,
            grid_layout_rows=4,
            )

        # Labels
        self.preset_name_label = PyFlameLabel(
            text='Preset Name',
            )
        self.batch_path_label = PyFlameLabel(
            text='Batch Save Path',
            )

        # Entries
        self.preset_name_entry = PyFlameEntry(
            text=self.settings.preset_name,
            )
        self.batch_path_entry = PyFlameEntry(
            text=self.settings.batch_path,
            )

        # Batch Path Token Pushbutton Menu
        self.batch_token_push_button = PyFlameTokenPushButton(
            text='Add Token',
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
            token_dest=self.batch_path_entry,
            )

        # Buttons
        self.browse_button = PyFlameButton(
            text='Browse',
            connect=path_browse,
            )
        self.save_button = PyFlameButton(
            text='Save',
            connect=self.save_preset,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=cancel,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.setup_window.grid_layout.addWidget(self.preset_name_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.preset_name_entry, 0, 1, 1, 2)

        self.setup_window.grid_layout.addWidget(self.batch_path_label, 1, 0)
        self.setup_window.grid_layout.addWidget(self.batch_path_entry, 1, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.batch_token_push_button, 1, 4)
        self.setup_window.grid_layout.addWidget(self.browse_button, 1, 5)

        self.setup_window.grid_layout.addWidget(self.cancel_button, 3, 4)
        self.setup_window.grid_layout.addWidget(self.save_button, 3, 5)

        self.setup_window.exec()

class UberSave():

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        self.selection = selection

        # Get flame variables
        self.flame_prj_name = flame.project.current_project.project_name
        print('Flame Project Name:', self.flame_prj_name)

        self.flame_prj_nickname = flame.projects.current_project.nickname
        print('Flame Project Nickname:', self.flame_prj_nickname)

        print('Loading Preset Settings...\n')
        # Load preset settings
        self.settings = PyFlamePresetManager(
            script_version=SCRIPT_VERSION,
            setup_script=None,
            ).load_preset()

    #-------------------------------------

    def resolve_path(self, batch_group) -> str:
        """
        Resolve path for batch setups folder.
        Any tokens in the path will be resolved.

        Resolves different paths for Flame and Flare.

        Args:
            batch_group (flame.PyBatch): Batch group to use to resolve path.

        Returns:
            resolved_save_path (str): Resolved path for batch setups.
        """

        print('Resolving Batch Save Path...\n')

        resolved_save_path = pyflame.resolve_tokens(
            tokenized_string=self.settings.batch_path,
            flame_pyobject=batch_group,)

        return resolved_save_path

    #-------------------------------------

    def save_batchgroup(self, save_path: str, batch_group) -> None:
        """
        Save batch group to batch setups folder. Iterate up if needed.

        If it's the first time a batch group is saved, a new iteration is created for the first iteration.

        Args:
            save_path (str): Path to save batch setups.
        """

        selected_batch_name = str(batch_group.name)[1:-1]
        pyflame.print(f'Saving Batch Group: {selected_batch_name}')

        # Open batch if closed
        batch_group.open()

        # Get current iteration
        iteration_split = (re.split(r'(\d+)', str(batch_group.current_iteration.name)[1:-1]))[1:-1]
        current_iteration = int(iteration_split[-1])
        print('    Current Iteration:', current_iteration)

        # Get latest iteration if iterations are saved
        if not batch_group.batch_iterations == []:
            latest_iteration = int(((re.split(r'(\d+)', str([i.name for i in batch_group.batch_iterations][-1])[1:-1]))[1:-1])[-1])
        else:
            latest_iteration = current_iteration
        print('    Latest Iteration:', latest_iteration)

        # Iterate up if iterate up menu selected
        print('    Iterate Up:', self.iterate, '\n')

        # If first save of batch group, create first iteration
        if batch_group.batch_iterations == [] and current_iteration == 1:
            self.iterate = True

        if self.iterate:
            if current_iteration == 1:
                batch_group.iterate()
            elif current_iteration < latest_iteration:
                batch_group.iterate(index = (latest_iteration + 1))
            else:
                batch_group.iterate(index = (current_iteration + 1))
            print('    --> Iterating Up\n')
        else:
            batch_group.iterate(index=current_iteration)
            print('    --> Overwriting Existing Iteration\n')

        # Get current iteration
        current_iteration = str(batch_group.current_iteration.name)[1:-1]
        print('    New iteration:', current_iteration)

        # Set batch save path
        shot_save_path = os.path.join(save_path, current_iteration)
        print('    Shot save path:', shot_save_path)

        # Try to save batch group, if error, give error message
        try:
            # Create shot save folder
            if not os.path.isdir(save_path):
                os.makedirs(save_path)

            # Hard save current batch iteration
            batch_group.save_setup(shot_save_path)

            print('\n')
            pyflame.print(f'Batch Uber Saved: {selected_batch_name}')
        except:
            error_message(message='Batch Not Saved. Check Path in Setup.')

    #-------------------------------------

    def batch_group_save(self) -> None:
        """
        Save current batch from batch.
        """

        # If no preset/settings are loaded, return to exit script
        if not self.settings:
            return

        #print('Flame Batch:', flame.batch)

        self.iterate = False
        resolved_path = self.resolve_path(
            batch_group=flame.batch,
            )
        self.save_batchgroup(
            save_path=resolved_path,
            batch_group=flame.batch,
            )

        pyflame.print('Saving Batch Group Complete', text_color=TextColor.GREEN)

    def batch_group_iterate_save(self) -> None:
        """
        Iterate and save current batch from batch.
        """

        # If no preset/settings are loaded, return to exit script
        if not self.settings:
            return

        self.iterate = True
        resolved_path = self.resolve_path(
            batch_group=flame.batch,
            )
        self.save_batchgroup(
            save_path=resolved_path,
            batch_group=flame.batch,
            )

        pyflame.print('Saving and Iterating Batch Group Complete', text_color=TextColor.GREEN)

    def batch_group_save_all(self) -> None:
        """
        Save all batchgroups in desktop.
        """

        # If no preset/settings are loaded, return to exit script
        if not self.settings:
            return

        self.iterate = False
        batch_groups = flame.project.current_project.current_workspace.desktop.batch_groups

        for batch_group in batch_groups:
            resolved_path = self.resolve_path(
                batch_group=batch_group,
                )
            self.save_batchgroup(
                save_path=resolved_path,
                batch_group=batch_group,
                )

        pyflame.print('Saving all batch groups complete', text_color=TextColor.GREEN)

    def batch_group_save_selected(self) -> None:
        """
        Save selected batchgroups in desktop.
        """

        # If no preset/settings are loaded, return to exit script
        if not self.settings:
            return

        self.iterate = False

        for batch_group in self.selection:
            resolved_path = self.resolve_path(
                batch_group=batch_group,
                )
            self.save_batchgroup(
                save_path=resolved_path,
                batch_group=batch_group,
                )

        pyflame.print('Saving selected batch groups complete', text_color=TextColor.GREEN)

    def batch_group_iterate_save_selected(self) -> None:
        """
        Iterate and save selected batchgroups in desktop.
        """

        # If no preset/settings are loaded, return to exit script
        if not self.settings:
            return

        self.iterate = True

        for batch_group in self.selection:
            resolved_path = self.resolve_path(
                batch_group=batch_group,
                )
            self.save_batchgroup(
                save_path=resolved_path,
                batch_group=batch_group,
                )

        pyflame.print('Saving and iterating selected batch groups complete', text_color=TextColor.GREEN)

#-------------------------------------

def error_message(message: str) -> None:
    """
    Open error message window using PyFlameMessageWindow.

    Args:
        message (str): The message to display.
    """

    PyFlameMessageWindow(
        message=message,
        type=MessageType.ERROR,
        )

def warning_message(message:str) -> bool:
    """
    Open warning message window using PyFlameMessageWindow.

    Args:
        message (str): The message to display.

    Returns:
        confirm (bool): User confirmation to proceed.
    """

    confirm = PyFlameMessageWindow(
        message=message,
        type=MessageType.WARNING,
        )

    return confirm

#-------------------------------------

def uber_batch_group_save(selection) -> None:
    """
    Save current batch from batch.
    """

    uber_save = UberSave(selection)
    uber_save.batch_group_save()

def uber_batch_group_iterate_save(selection) -> None:
    """
    Iterate and save current batch from batch.
    """

    uber_save = UberSave(selection)
    uber_save.batch_group_iterate_save()

def uber_batch_group_save_all(selection) -> None:
    """
    Save all batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    uber_save.batch_group_save_all()

def uber_batch_group_save_selected(selection) -> None:
    """
    Save selected batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    uber_save.batch_group_save_selected()

def uber_batch_group_iterate_save_selected(selection) -> None:
    """
    Iterate and save selected batchgroups in desktop.
    """

    uber_save = UberSave(selection)
    uber_save.batch_group_iterate_save_selected()

#-------------------------------------

def open_preset_manager(selection) -> None:
    """
    Open preset manager to edit Uber Save presets.
    """

    PyFlamePresetManager(
        script_version=SCRIPT_VERSION,
        setup_script=UberSaveSetup,
        )

#-------------------------------------
# [Scopes]
#-------------------------------------

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
                    'name': 'Uber Save Setup',
                    'execute': open_preset_manager,
                    'minimumVersion': '2023.2'
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
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Save Selected Batch Groups',
                    'isVisible': scope_batch,
                    'execute': uber_batch_group_save_selected,
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Iterate and Save Selected Batch Groups',
                    'isVisible': scope_batch,
                    'execute': uber_batch_group_iterate_save_selected,
                    'minimumVersion': '2023.2'
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
                    'minimumVersion': '2023.2'
                },
                {
                    'name': 'Iterate and Save Current Batch Group',
                    'execute': uber_batch_group_iterate_save,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
