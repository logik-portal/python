"""
Script Name: Batch Group to Shot Folders
Script Version: 1.0.0
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 06.02.26
Update Date: 06.11.26

Custom Action Type: Media Panel

Description:

    Copy or Move selected batch groups to folders in the Media Panel using a tokenized path.

Usage:

    Tokenized path is used to determine the destination folder for the batch groups.

    The tokenized path structure is: <LibraryName>/<FolderPath>

    If the Library and/or Folder structure does not exist for a batch group, it will be created.

    Example Tokenized Path:
        Shot Folders/<SEQNAME>/<ShotName>/Batch_Groups

        Example batch group name:
            PYT_0010_comp

        This would create the following folder structure with the batch group going into the Batch Groups folder:
        Library: Shot Folders
        Folder Path: PYT/PYT_0010/Batch_Groups

    Batch groups must be named with a standard shot name or be tagged with a shot name tag.

    Example Batch Group Names:
        PYT_0010_comp
        PYT0010_comp
        PYT010_comp
        PYT_010_comp
        PYT_0010
        PYT0010
        PYT010

    Example Shot Name Tags:
        ShotName: PYT_0010
        ShotName: PYT0010
        ShotName: PYT010

    Script menu will not show up if the current tab is MediaHub.

Menus:

    Setup:
        Flame Main Menu ->  Logik -> Logik Portal Script Setup -> Batch Groups to Folders Setup

    To Move Batch Groups:
        Right-click on selected batch groups in Media Panel/Desktop -> Move Batch Groups to Folders

    To Copy Batch Groups:
        Right-click on selected batch groups in Media Panel/Desktop -> Copy Batch Groups to Folders

To install:

    Copy script into /opt/Autodesk/shared/python/batch_group_to_shot_folders

Updates:

    v1.0.0 06.11.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import re

import flame
from lib.pyflame_lib_batch_group_to_shot_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Batch Group to Shot Folders'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

def load_config():
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
            'tokenized_path': '',
            }
        )

    return settings

class Setup:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        self.setup_window()

    def setup_window(self) -> None:

        def save_config() -> None:
            """
            Save Config
            ===========

            Save config values to config file.
            """

            tokenized_path = self.batch_group_path_entry.text.strip()

            if not tokenized_path:
                PyFlameMessageWindow(
                    message='Please set destination path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Batch Group path entry must contain at least one / followed by some text.
            if not re.search(r'^[^/]+/.+', tokenized_path):
                PyFlameMessageWindow(
                    message='Destination path must be in this format: LibraryName/<FolderPath>.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Save settings to config file
            self.settings.save_config(
                config_values={
                    'tokenized_path': tokenized_path,
                    }
                )

            self.window.close()

        def close_window() -> None:

            self.window.close()

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=3,
            parent=None,
            )

        # Labels
        self.batch_ground_path_label = PyFlameLabel(
            text='Destination Path',
            )

        # Entries
        self.batch_group_path_entry = PyFlameEntry(
            text=self.settings.tokenized_path,
            placeholder_text='e.g., LibraryName/<ShotName>/Batch_Groups',
            )

        # Token Menus
        self.batch_group_path_token_menu = PyFlameTokenMenu(
            text='Tokens',
            token_dict={
                'Shot Name': '<ShotName>',
                'SEQUENCE NAME': '<SEQNAME>',
                'Sequence Name': '<SeqName>'
                },
            token_dest=self.batch_group_path_entry,
            )

        # Buttons
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.batch_ground_path_label, 0, 0)
        self.window.grid_layout.addWidget(self.batch_group_path_entry, 0, 1, 1, 3)
        self.window.grid_layout.addWidget(self.batch_group_path_token_menu, 0, 4)

        self.window.grid_layout.addWidget(self.cancel_button, 2, 3)
        self.window.grid_layout.addWidget(self.save_button, 2, 4)

        #-------------------------------------

        self.batch_group_path_entry.set_focus()

class ToShotFolders:

    def __init__(self, selection, mode: str) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = load_config()

        # Make sure selection is only batch groups
        self.selection = [item for item in selection if isinstance(item, flame.PyBatch)]

        # Set mode
        self.mode = mode

        self.process_batch_groups()

    def process_batch_groups(self) -> None:

        def check_for_errors():

            if not self.settings.tokenized_path:
                PyFlameMessageWindow(
                    message='Tokenized Destination Path Must Be Set Before Processing Batch Groups.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Batch Group to Shot Folders Setup',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return True

            if not self.selection:
                PyFlameMessageWindow(
                    message='No batch groups selected.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return True
            return False

        def get_dest(batch) -> flame.PyFolder | None:
            """
            Get Dest
            ========

            Get destination folder object for batch group.

            Args:
            -----
                batch (object):
                    Batch group object.

            Returns:
            --------
                flame.PyFolder | None:
                    Destination folder object.
            """

            def get_dest_library(dest_library_name):
                """
                Get Destination Library
                =======================

                Get destination library object.
                If library does not exist, create it.

                Args:
                -----
                    dest_library_name (str):
                        Destination library name.

                Returns:
                --------
                    object:
                        Destination library object.
                """

                for library in flame.project.current_project.current_workspace.libraries:
                    if library.name == dest_library_name:
                        return library

                # If library is not found, create it
                pyflame.print(f'Destination Library Not Found, Creating Library: {dest_library_name}', text_color=TextColor.GREEN)
                library = flame.project.current_project.current_workspace.create_library(dest_library_name)
                return library

            def get_dest_folder(dest_library, dest_path, shot_name):

                def find_dest_folder(dest_library, dest_path) -> object:
                    """
                    Find Destination Folder
                    =======================

                    Iterate through folders in Library to get destination folder object.

                    Args:
                    -----
                        dest_library (object):
                            Destination library object.
                        dest_path (str):
                            Destination path string.

                    Returns:
                    --------
                        object:
                            Destination folder object.
                    """

                    # Path parts relative to the library (drop the leading library name)
                    folder_parts = dest_path.split('/')[1:]
                    if not folder_parts:
                        return None

                    # Walk the path one level at a time, starting from the library's
                    # top-level folders and descending into matching subfolders.
                    current = dest_library
                    for part in folder_parts:
                        match = None
                        for folder in current.folders:
                            if folder.name == part:
                                match = folder
                                break
                        if match is None:
                            return None
                        current = match

                    return current

                def create_dest_folder(path, top_level, shot_name):
                    """
                    Create Destination Folder
                    =========================

                    Create destination folder in path.

                    Search for existing folders in path and create missing folders.
                    """

                    def convert_path_to_nested_dict(path):
                        """
                        Path to Nested Dict
                        ==================

                        Convert path string to nested dictionary.

                        Args:
                        -----
                            path (str):
                                Path string to convert to nested dictionary.

                        Returns:
                        --------
                            dict:
                                Nested dictionary.
                        """

                        parts = path.split('/')  # Split the string into parts
                        nested_dict = {}
                        current = nested_dict

                        for part in parts:
                            current[part] = {}
                            current = current[part]  # Move to the next level of the dictionary

                        return nested_dict

                    # Save full path
                    full_path = path

                    # Loop through path to find existing folders, create missing folder when either existing folder is found or path is at top level
                    while True:
                        folder = find_dest_folder(dest_library, path)
                        if folder:

                            # Remaining folder path after the deepest existing prefix
                            missing_path = full_path[len(path):].lstrip('/')

                            # Convert missing_path to dictionary, each subfolder is a subkey
                            missing_path = convert_path_to_nested_dict(missing_path)

                            # Create missing folders
                            pyflame.create_media_panel_folder(folder_name=next(iter(missing_path)), folder_structure=missing_path, dest=folder, shot_name_tag=shot_name)

                            # Get destination folder from new folder structure
                            dest_folder = find_dest_folder(dest_library, dest_path)
                            return dest_folder

                        # Move one level up
                        path = path.rsplit('/', 1)[0]

                        # Check if path is at top level, if so, create missing folder structure
                        if path == top_level:
                            missing_path = convert_path_to_nested_dict(full_path.split('/', 1)[1])
                            pyflame.create_media_panel_folder(folder_name=next(iter(missing_path)), folder_structure=missing_path, dest=dest_library, shot_name_tag=shot_name)

                            # Get destination folder from new folder structure
                            dest_folder = find_dest_folder(dest_library, dest_path)
                            return dest_folder

                # Check if destination folder already exists
                dest_folder = find_dest_folder(dest_library, dest_path)
                #print('Dest Folder:', dest_folder)

                # If destination folder does not exist, create it
                if not dest_folder:
                    dest_folder = create_dest_folder(dest_path, dest_path.split('/')[0], shot_name)

                return dest_folder

            # Resolve any remaining tokens in the destination path (e.g. project/date tokens)
            dest_path = pyflame.resolve_tokens(tokenized_string=self.settings.tokenized_path, flame_pyobject=batch)
            print('Dest Path:', dest_path, '\n')

            print('Getting Shot Name...')
            if '<ShotName>' in self.settings.tokenized_path:
                shot_name = pyflame.shot_name_from_batch_group(batch)
            else:
                shot_name = ''
            print('Shot Name:', shot_name)

            # Get destination library, if not found, create it
            dest_library_name = dest_path.split('/')[0]
            dest_library = get_dest_library(dest_library_name)
            print('Destination Library:', dest_library.name)

            # Get destination folder, if not found, create it
            dest_folder = get_dest_folder(dest_library, dest_path, shot_name)
            print('Destination Folder:', dest_folder)

            return dest_folder

        def move_selected(source, dest) -> None:
            """
            Move Selected
            =============

            Move selected batch group to destination.
            """

            flame.media_panel.move(source, dest)

        def copy_selected(source, dest) -> None:
            """
            Copy Selected
            =============

            Copy selected batch group to destination.
            """

            flame.media_panel.copy(source, dest)

        def remove_existing_batch_groups(dest_folder, batch_name) -> None:
            """
            Remove Existing Batch Groups
            ============================

            Remove existing batch groups in destination folder if overwrite is enabled and batch group name matches
            """

            for batch in dest_folder.batch_groups:
                if str(batch.name)[1:-1] == batch_name:
                    print('Removing existing batch in dest:', str(batch.name)[1:-1])
                    flame.delete(batch)

        # Check for errors, if any, return and stop script.
        if check_for_errors():
            return

        # Move/Copy batch groups to destination folder
        replace_all = False  # Set True when user selects Replace All to skip further prompts
        cancelled = False    # Set True when user selects Cancel to abort the operation

        for batch in self.selection:
            batch_name = str(batch.name)[1:-1]
            print('Batch Name:', batch_name)

            batch.open()

            # Get destination folder
            batch_group_dest = get_dest(batch)
            print('Batch Group Dest:', batch_group_dest)

            if batch_group_dest:
                # Check if batch group already exists in destination folder
                duplicate_exists = False
                if batch_group_dest.batch_groups:
                    for dest_batch in batch_group_dest.batch_groups:
                        if str(dest_batch.name)[1:-1] == batch_name:
                            duplicate_exists = True
                            break

                if duplicate_exists:
                    if replace_all:
                        # Replace All previously selected, overwrite without prompting
                        remove_existing_batch_groups(batch_group_dest, batch_name)
                    else:
                        prompt = PyFlameOptionWindow(
                            message=f'Batch Group {batch_name} already exists in destination folder.',
                            buttons={
                                1: {'text': 'Replace',     'color': Color.GRAY},
                                2: {'text': 'Replace All', 'color': Color.GRAY},
                                3: {'text': 'Add',         'color': Color.GRAY},
                                4: {'text': 'Cancel',      'color': Color.RED},
                                },
                            cancel_button=4,
                            parent=None,
                            )

                        if not prompt:
                            # Cancel selected or window closed, abort the entire operation
                            cancelled = True
                            break
                        elif prompt.selected == 'Replace':
                            remove_existing_batch_groups(batch_group_dest, batch_name)
                        elif prompt.selected == 'Replace All':
                            replace_all = True
                            remove_existing_batch_groups(batch_group_dest, batch_name)
                        elif prompt.selected == 'Add':
                            # Leave the existing batch group in place and add alongside it
                            pass
                else:
                    print('Batch Group does not exist in destination folder:', batch_name)

                if self.mode == 'move':
                    # Move batch groups to destination folder
                    move_selected(batch, batch_group_dest)
                elif self.mode == 'copy':
                    # Copy batch groups to destination folder
                    copy_selected(batch, batch_group_dest)
                print('\n')
            else:
                pyflame.print(
                    f'Could not resolve destination folder for batch group: {batch_name}',
                    text_color=TextColor.RED,
                    )

        if cancelled:
            pyflame.print('Operation Cancelled.', text_color=TextColor.RED)
        else:
            pyflame.print(f'{self.mode.capitalize()} Batch Groups Complete.', text_color=TextColor.GREEN)

def move_batch_groups(selection) -> None:
    """
    Move Batch Groups
    =================

    Move batch groups to destination folder.
    """

    ToShotFolders(selection, 'move')

def copy_batch_groups(selection) -> None:
    """
    Copy Batch Groups
    =================

    Copy batch groups to destination folder.
    """

    ToShotFolders(selection, 'copy')

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_batch_group(selection):

    if flame.get_current_tab() != 'MediaHub':
        for item in selection:
            if isinstance(item, flame.PyBatch):
                return True
        return False
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
                    'name': 'Batch Group to Shot Folders Setup',
                    'execute': Setup,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
           'name': 'Batch Group to Shot Folders',
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Move to Shot Folders',
                    'isVisible': scope_batch_group,
                    'separator': 'below',
                    'execute': move_batch_groups,
                    'minimumVersion': '2025.1'
               },
               {
                    'name': 'Copy to Shot Folders',
                    'isVisible': scope_batch_group,
                    'separator': 'below',
                    'execute': copy_batch_groups,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
