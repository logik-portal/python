# Create Project Folders
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Create Project Folders
Script Version: 2.0.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 09.22.21
Update Date: 11.09.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Flame Startup / Flame Main Menu

Description:

    Creates a project file system folder structure and/or media panel library/folder structure when Flame starts and
    when a project is loaded. Each project is offered once each time it's loaded, even if Flame runs both start-up
    hooks.

    Folder structures are saved as templates. Each template has its own Projects Path, file system folders and media
    panel libraries/folders, and its own settings for creating them (Create Folders, Create Lib/Folders) and for
    deleting the project's Default Library (Delete Default Lib).

URL:

    https://logik-portal.com/scripts/create_project_folders

Usage:

    The script runs when Flame starts (Flame's app_initialized hook) and when a project is loaded (Flame's
    project_changed hook). Each project is offered once each time it's loaded, even if Flame runs both hooks for the
    same load. A template window left open from an earlier project stays open, but its Create and Cancel don't create or
    mark anything; Create shows a message.

    The following tokens can be used in library/folder names as well as the file system path:

        <ProjectName>
        <ProjectNickName>
        <UserName>
        <UserNickName>
        <YYYY>
        <YY>
        <MM>
        <DD>
        <Hour>
        <Minute>
        <AMPM>
        <ampm>

    Example:

        /Volumes/NAS/Jobs/<ProjectNickName>/<ProjectName>

    The first time Flame starts with the script installed, it asks once whether to set up a template now.

    In the Setup window, use the Template menu and the New, Rename, Duplicate and Delete buttons to manage templates.
    Each template's Projects Path, folder trees and Create Lib/Folders / Create Folders buttons are edited in the Setup
    window. New starts a template with the default settings. Duplicate copies all the settings of the selected template.
    Nothing is saved until Save.

    After enabling Create Lib/Folders and/or Create Folders for a template in the Setup window, a window opens when
    Flame starts or a project is loaded, to pick one of the enabled templates and create its file system and/or media
    panel folders for that project. Only the folder trees enabled for the picked template are shown.

    The file system folders and the media panel libraries are checked separately. If the project's file system folder or
    a library already exists, it isn't created again. If any of its template folders are missing, there is a prompt to
    create just the missing folders or cancel.

    Once folders have been created, or an existing project folder or library was found, the project is marked and isn't
    asked about again. Cancelling the template window when it opens on its own (Flame start or project load) also marks
    the project, and a message says how to create the folders later. Cancelling it after Setup -> Save does nothing.

    When a template's Delete Default Lib button is on (the default), the Default Library is deleted after the template's
    media panel libraries/folders are created. When it's off, the Default Library is left alone.

    Media Panel and File System Folders can also be created from the Setup window with the selected template (Manually
    Create, or Save then Create), even for a project that's already marked. Manually Create also marks the project, even
    when its confirmation is cancelled (but not when its save is stopped or an error stops it).

    If a token in the file system path or a library/folder name resolves to nothing (for example <ProjectNickName> when
    the project has no nickname), an error is shown and nothing is created for that part.

Menus:

    Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Create Project Folders Setup

To install:

    Copy script into /opt/Autodesk/shared/python/create_project_folders

Updates:

    v2.0.0 11.09.26
        - Updated to PyFlameLib v5.5.3.
        - Script now only works with Flame 2025.2+.
        - A token in the file system path or a library/folder name that resolves to nothing (such as <ProjectNickName>
          with no project nickname) now shows an error and nothing is created, instead of creating folders in the wrong
          place.
        - Cancelling Manually Create (media panel or file system) now also marks the project, the same as creating.
        - Folders are now also offered when a project is loaded, not only when Flame starts. Each project is offered
          once per load, even if Flame runs both hooks. A template window left open from an earlier project stays open,
          but its Create and Cancel don't create or mark anything.
        - Added a Delete Default Lib button to the Setup window. 
        - Each template now has its own Create Lib/Folders (media panel) and Create Folders (file system) settings,
          instead of one shared pair. Existing templates get the old shared settings. New resets them to off, Duplicate
          copies them. 
        - Added folder templates. Each template has its own Projects Path, file system folders and media panel
          libraries/folders. Templates are managed in the Setup window (New, Rename, Duplicate, Delete). An existing
          config's folders become the Default template.
        - Added a window to pick the template when folders are created at start-up or from Setup (Save then Create). It
          shows the template's Projects Path and the folder trees that will be created.
        - File system folders and media panel libraries are now always checked separately for existing folders. Existing
          libraries are checked without a confirmation first.
        - When the project folder or a library already exists, there's a prompt to create only the missing folders, or
          cancel. Either way the project isn't asked about again.
        - Manually Create (file system or media panel) now also marks the project, so it isn't asked about at the next
          start.
        - File system folders that can't be created are now listed in one error message, instead of being reported as
          created.
        - Projects path ending in / now creates folders in the right place. A path with no folder name or parent folder
          (such as /) shows an error.
        - Add Lib/Folder with nothing selected shows a message instead of an error.
        - Media panel Manually Create always asks for confirmation first, doesn't create libraries that already exist,
          and says what was created and added.

    v1.9.0 01.03.25
        - Updated to PyFlameLib v4.0.0.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v1.8.0 10.01.24
        - Updated to PyFlameLib v3.2.0.
        - Updated UI to be more consistent with other scripts.

    v1.7.0 01.21.24
        - Updates to UI/PySide.

    v1.6.0 08.15.23
        - Updated to PyFlameLib v2.0.0.
        - Updated script versioning to semantic versioning.

    v1.5 02.04.23
        - Added check to make sure script is installed in the correct location.

    v1.4 01.21.23
        - Moved setup menu for Flame 2023.2+ to: Flame Main Menu -> Logik -> Logik Portal Script Setup -> Create Project
          Folders Setup
        - Updated config file loading/saving.

    v1.3 06.06.22
        Messages print to Flame message window - Flame 2023.1 and later

    v1.2 03.28.22
        - Tokens for <ProjectName> and <ProjectNickName> can be entered into library and folder names
        - Updated UI for Flame 2023
        - Moved UI widgets to external file
        - Imporved initial script setup

    v1.1 11.03.21

        - Added ability to create media panel libraries and folders on project start up
        - Added buttons to manually create file system/media panel folders
        - Added buttons to enable/diable creation of either file systems folders or media panel folders
        - Setup will now open first time Flame is started after script is installed
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import copy
import json
import os
from functools import partial

import flame
from lib.pyflame_lib_create_project_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Create Project Folders'
SCRIPT_VERSION = 'v2.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

DEFAULT_TEMPLATE = {
    'projects_path': '/Volumes/NAS/Jobs/<ProjectNickName>/<ProjectName>',
    'create_file_system_folders': False,
    'create_media_panel_folders': False,
    'delete_default_library': True,
    'file_system_folders': {
        'Project Folder': {
            'Archives': {},
            'Postings': {},
            'Ref': {},
            'Shots': {},
            },
        },
    'media_panel_library_folders': {
        'Workspace': {
            'Library': {
                'Folder 1': {},
                'Folder 2': {},
                'Folder 3': {},
                'Folder 4': {},
                },
            },
        },
    }

# ==============================================================================
# [Main Script]
# ==============================================================================

class CreateProjectFolders():

    def __init__(self, selection) -> None:

        # Get Flame values
        self.get_current_project()

        # Load/Create config file
        self.load_config()

    def get_current_project(self) -> None:
        """
        Get Current Project
        ===================

        Read the current project's name, nickname and workspace from Flame. Called again before creating folders,
        so a window opened in another project marks and creates for the project that is current now.
        """

        self.project_name = flame.project.current_project.name
        self.project_nickname = flame.project.current_project.nickname
        self.workspace = flame.project.current_project.current_workspace

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        If there are no templates yet, build the Default template from the old single template keys
        (projects_path, file_system_folders, media_panel_library_folders) if the config has them,
        otherwise from DEFAULT_TEMPLATE, and save it.

        Templates without their own create options (create_file_system_folders, create_media_panel_folders)
        get the old shared create_file_system_folders_on_start / create_media_panel_folders_on_start values.
        Templates without delete_default_library get True (the Default Library was always deleted before).

        After migrating, the old keys (the two shared create options and the old single template keys) are removed
        from the config file and from the loaded settings. PyFlameConfig.save_config can't remove keys, so the file is
        rewritten directly. A failed clean-up is printed as an error and doesn't stop the script.
        The config is only written if something was added or an old key was found.
        """

        # Load config file
        self.settings = PyFlameConfig(
            config_values={
                'first_time': True,
                'ignore_projects': [],
                'templates': {},
                'last_template': '',
                }
            )

        # Old config keys, only read here for migration, then removed from the config file
        old_keys = (
            'create_file_system_folders_on_start',
            'create_media_panel_folders_on_start',
            'projects_path',
            'file_system_folders',
            'media_panel_library_folders',
            )

        # Old shared create options, only read to give templates their own
        shared_options = {
            'create_file_system_folders': self.settings.config_values.get('create_file_system_folders_on_start', False),
            'create_media_panel_folders': self.settings.config_values.get('create_media_panel_folders_on_start', False),
            }
        config_values = {}

        # Build Default template, from old config keys if they exist
        if not self.settings.templates:
            template = copy.deepcopy(DEFAULT_TEMPLATE)
            for key in ('projects_path', 'file_system_folders', 'media_panel_library_folders'):
                if key in self.settings.config_values:
                    template[key] = self.settings.config_values[key]
            template.update(shared_options)
            config_values['templates'] = {'Default': template}
            config_values['last_template'] = 'Default'

        # Give each template its own create options, from the old shared ones, and its own Default Library setting
        template_options = dict(shared_options, delete_default_library=True)
        templates = config_values.get('templates', copy.deepcopy(self.settings.templates))
        for template in templates.values():
            for key, value in template_options.items():
                if key not in template:
                    template[key] = value
                    config_values['templates'] = templates

        found_old_keys = [key for key in old_keys if key in self.settings.config_values]

        if found_old_keys:
            # Apply migrated values and drop the old keys in memory, so a later save_config can't write them back
            for key, value in config_values.items():
                setattr(self.settings, key, value)
            for key in found_old_keys:
                del self.settings.config_values[key]
                self.settings.__dict__.pop(key, None) # PyFlameConfig sets an attribute for every loaded key

            # Rewrite the config file without the old keys. Write to a temp file first so a failed write can't truncate it.
            try:
                with open(self.settings.config_path, 'r') as config_file:
                    file_config = json.load(config_file)
                file_config.update(config_values)
                for key in old_keys:
                    file_config.pop(key, None)
                file_config = {'script_name': self.settings.script_name, **{key: value for key, value in file_config.items() if key != 'script_name'}}

                temp_path = f'{self.settings.config_path}.tmp'
                with open(temp_path, 'w') as config_file:
                    json.dump(file_config, config_file, indent=4)
                os.replace(temp_path, self.settings.config_path)
                pyflame.print(f'Old Config Keys Removed: {", ".join(found_old_keys)}', text_color=TextColor.GREEN)
            except Exception as e:
                pyflame.print(f'Could not remove old config keys from config file: {e}', print_type=PrintType.ERROR)
        elif config_values:
            self.settings.save_config(
                config_values=config_values,
                )

        # Use first template if last template no longer exists
        if self.settings.last_template not in self.settings.templates:
            self.settings.last_template = list(self.settings.templates)[0]

    def refresh_settings(self) -> None:
        """
        Refresh Settings
        ================

        Read the config file again right before saving. PyFlameConfig.save_config writes all of its loaded values,
        and Flame reloads the hooks when a project is loaded, so a window left open across a load holds an old config.
        Saving from that would undo what was saved since (marked projects, templates).
        """

        self.load_config()

    # ==============================================================================

    def setup_window(self) -> None:
        """
        Setup Window
        ============

        Window to manage folder templates: each template's Projects Path, file system folders, media panel libraries/folders,
        Create Folders, Create Lib/Folders and Delete Default Lib. Edits stay in memory until Save.
        Folders can also be created from the selected template with Manually Create.
        """

        def media_panel_add() -> None:
            """
            Media Panel Add
            ===============

            Add new library or folder to media panel libraries/folders tree.

            If Workspace is selected, add new library otherwise add new folder.
            """

            # Stop if nothing is selected in the tree
            if not self.media_panel_library_folders_tree.selectedItems():
                PyFlameMessageWindow(
                    message='Select the Workspace to add a library, or a library/folder to add a folder.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )

                return

            if self.media_panel_library_folders_tree.selectedItems()[0].text(0) == 'Workspace':
                self.media_panel_library_folders_tree.add_item(
                    item_name='New Library',
                    )
            else:
                self.media_panel_library_folders_tree.add_item(
                    item_name='New Folder',
                    )

        def store_template() -> None:
            """
            Store Template
            ==============

            Store the Setup window's edits to the selected template in memory. Nothing is saved to disk until Save.
            """

            templates[template_name] = {
                'projects_path': self.projects_path_entry.text,
                'create_file_system_folders': self.create_system_folders_push_button.checked,
                'create_media_panel_folders': self.create_media_panel_lib_folders_push_button.checked,
                'delete_default_library': self.delete_default_library_push_button.checked,
                'file_system_folders': self.file_system_folder_tree.tree_dict,
                'media_panel_library_folders': self.media_panel_library_folders_tree.tree_dict,
                }

        def load_template(name: str) -> None:
            """
            Load Template
            =============

            Show a template in the Setup window (path, trees, create buttons and Delete Default Lib) and select it in the Template menu.

            Args
            ----
                name (str): Template name.
            """

            nonlocal template_name

            template_name = name
            self.projects_path_entry.text = templates[name]['projects_path']
            self.create_system_folders_push_button.checked = templates[name]['create_file_system_folders']
            self.create_media_panel_lib_folders_push_button.checked = templates[name]['create_media_panel_folders']
            self.delete_default_library_push_button.checked = templates[name]['delete_default_library']
            self.file_system_folder_tree.tree_dict = templates[name]['file_system_folders']
            self.media_panel_library_folders_tree.tree_dict = templates[name]['media_panel_library_folders']
            self.template_menu.update_menu(
                text=name,
                menu_options=list(templates),
                connect=switch_template,
                )

        def switch_template() -> None:
            """
            Switch Template
            ===============

            Keep the current template's edits, then show the template picked in the Template menu.
            """

            if self.template_menu.text == template_name:
                return

            store_template()
            load_template(self.template_menu.text)

        def unique_template_name(name: str) -> str:
            """
            Unique Template Name
            ====================

            Add a number to a template name if it's already used: name, name 2, name 3...

            Args
            ----
                name (str): Template name.

            Returns
            -------
                unique_name (str): Template name not used by another template.
            """

            unique_name = name
            number = 2
            while unique_name in templates:
                unique_name = f'{name} {number}'
                number += 1

            return unique_name

        def new_template() -> None:
            """
            New Template
            ============

            Add a template with the default values (path, trees, create buttons off, Delete Default Lib on) and show it.
            """

            store_template()
            name = unique_template_name('New Template')
            templates[name] = copy.deepcopy(DEFAULT_TEMPLATE)
            load_template(name)

        def duplicate_template() -> None:
            """
            Duplicate Template
            ==================

            Add a copy of the selected template, including its unsaved edits and buttons, and show it.
            """

            store_template()
            name = unique_template_name(f'{template_name} Copy')
            templates[name] = copy.deepcopy(templates[template_name])
            load_template(name)

        def rename_template() -> None:
            """
            Rename Template
            ===============

            Rename the selected template. The name can't be empty or used by another template.
            """

            store_template()

            input_dialog = PyFlameInputDialog(
                text=template_name,
                label_text='Template Name',
                title=f'{SCRIPT_NAME}: Rename Template',
                parent=None,
                )
            if input_dialog.text is None:
                return

            new_name = input_dialog.text.strip()
            if new_name == template_name:
                return

            if not new_name or new_name in templates:
                PyFlameMessageWindow(
                    message=f'Template name can\'t be empty or the same as another template: {new_name}',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )

                return

            # Rename in place to keep template order
            renamed_templates = {(new_name if name == template_name else name): template for name, template in templates.items()}
            templates.clear()
            templates.update(renamed_templates)
            load_template(new_name)

        def delete_template() -> None:
            """
            Delete Template
            ===============

            Delete the selected template after confirming. The last template can't be deleted.
            """

            if len(templates) == 1:
                PyFlameMessageWindow(
                    message='The last template can\'t be deleted.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )

                return

            if not PyFlameMessageWindow(
                message=f'Delete template: {template_name}?',
                message_type=MessageType.WARNING,
                parent=None,
                ):
                return

            del templates[template_name]
            load_template(list(templates)[0])

        def folder_browse() -> None:
            """
            Folder Browse
            =============

            Browse for folder to set as projects path. Set path in projects path entry.
            """

            file_path = pyflame.file_browser(
                path=self.projects_path_entry.text,
                title='Select Directory',
                select_directory=True,
                window_to_hide=[self.setup_window]
                )

            if file_path:
                self.projects_path_entry.text = file_path

        def save() -> None:
            """
            Save
            ====

            Save config values to config file, then close setup window.

            Prompt to create file system folders and/or media panel libraries/folders for current project after saving,
            if a template has either create option on.
            """

            # Keep window open if config was not saved
            if not save_config():
                return

            self.setup_window.close()

            # Only ask to create folders now if file system or media panel creation is on for a template
            if not self.get_enabled_templates(self.settings.templates):
                return

            # Ask to create folders now
            if PyFlameMessageWindow(
                message='Create Project Media Panel Libraries and/or File System Folders for current project?',
                message_type=MessageType.CONFIRM,
                parent=None,
                ):
                self.create_on_start(ignore_mark=True)

        def save_config() -> bool:
            """
            Save Config
            ===========

            Save config values to config file.

            Every template with Create Folders on needs a Projects Path. If no template has either create option on, confirm first.

            Returns
            -------
                saved (bool): True if config was saved, False if a check stopped it.
            """

            store_template()

            for name, template in templates.items():
                # Treat a path that is only slashes or spaces as empty. Show the template with the bad path.
                if template['create_file_system_folders'] and not template['projects_path'].replace('/', '').strip():
                    load_template(name)
                    PyFlameMessageWindow(
                        message=f'Template: {name}\n\nProjects Path: Enter path where folders will be created.',
                        message_type=MessageType.ERROR,
                        parent=None,
                        )

                    return False

            if not self.get_enabled_templates(templates):
                if not PyFlameMessageWindow(
                    message='Neither File System Folders or Media Panel Libraries/Folders selected to create in any template.\n\nNo folders will be created.\n\nContinue?',
                    message_type=MessageType.CONFIRM,
                    parent=None,
                    ):
                    return False

            # Save settings to config file. Other values (ignore_projects) come from the file as it is now.
            self.refresh_settings()
            self.settings.save_config(
                config_values={
                    'first_time': False,
                    'templates': copy.deepcopy(templates),
                    'last_template': template_name,
                    }
                )

            return True

        def manually_create_file_system_folders() -> None:
            """
            Manually Create File System Folders
            ===================================

            Manually create file system folders from the selected template.

            If the project folder already exists, only ask to create the missing folders.
            Mark the project so it isn't asked about at the next start, also when that prompt is cancelled,
            but not when an error stops it (save failed, invalid path, a token that resolved to nothing).
            """

            # Use the project that is current now, in case another project was loaded while Setup was open
            self.get_current_project()

            if not save_config():
                return

            # Resolve tokens once, so creating and checking use the same folder names. Stop if a token resolved to nothing.
            template = self.resolve_file_system_template(self.settings.templates[self.settings.last_template])
            if not self.check_file_system_template(self.settings.templates[self.settings.last_template], template):
                return
            projects_path = template['projects_path'].strip().rstrip('/')

            # Project folder already exists, only create missing folders
            if os.path.isdir(projects_path):
                created = self.create_missing_file_system_folders(template, projects_path)
                if created is None:
                    return
            else:
                created = self.create_file_system_folders(template)
                if not created:
                    return

            if created:
                PyFlameMessageWindow(
                    message='File system folders created.',
                    parent=None,
                    )

            self.mark_project()

        def manually_create_libraries() -> None:
            """
            Manually Create Libraries
            =========================

            Manually create media panel libraries and folders from the selected template. If Delete Default Lib is on,
            the Default Library is deleted afterwards, unless the template has its own library named Default Library.

            Always ask for confirmation first. Libraries that already exist aren't created again, but missing folders in them can be.
            Show what was created and added when done. Mark the project so it isn't asked about at the next start,
            also when a confirmation is cancelled, but not when an error stops it.
            """

            # Use the project that is current now, in case another project was loaded while Setup was open
            self.get_current_project()

            # Only mention the Default Library if it will be deleted and there is one to delete
            message = 'Create Project Libraries/Folders?'
            if self.delete_default_library_push_button.checked and not self.default_library_in_template(self.media_panel_library_folders_tree.tree_dict) and 'Default Library' in [str(lib.name)[1:-1] for lib in self.workspace.libraries]:
                message += '\n\nThis will delete the Default Library.'

            if not PyFlameMessageWindow(
                message=message,
                message_type=MessageType.WARNING,
                parent=None,
                ):
                # Cancel marks the project too, as creating does
                pyflame.print('Creating Media Panel Libraries/Folders Aborted')
                self.mark_project()

                return

            if not save_config():
                return

            libraries = self.create_media_panel_folders(self.settings.templates[self.settings.last_template])
            if libraries is None:
                return

            created_libraries, added_folders, skipped_libraries = libraries
            message = 'Libraries created:\n\n' + ('\n'.join(created_libraries) if created_libraries else 'None')
            if skipped_libraries:
                message += '\n\nFolders added to existing libraries:\n\n' + ('\n'.join(added_folders) if added_folders else 'None')

            PyFlameMessageWindow(
                message=message,
                parent=None,
                )

            self.mark_project()

        def close_window() -> None:
            """
            Close Window
            ============

            Close setup window.
            """

            self.setup_window.close()

        # Templates are edited in memory until Save
        templates = copy.deepcopy(self.settings.templates)
        template_name = self.settings.last_template

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Setup Window
        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}</small>',
            return_pressed=save,
            escape_pressed=close_window,
            grid_layout_columns=7,
            grid_layout_rows=15,
            grid_layout_adjust_column_widths={3: 50},
            parent=None,
            )

        # Labels
        self.template_label = PyFlameLabel(
            text='Template',
            )
        self.media_panel_folders_setup_label = PyFlameLabel(
            text='Media Panel Library/Folder Setup',
            style=Style.UNDERLINE,
            )
        self.file_system_folder_setup_label = PyFlameLabel(
            text='File System Folder Setup',
            style=Style.UNDERLINE,
            )
        self.projects_path_label = PyFlameLabel(
            text='File System Project Path',
            )

        # Menus
        self.template_menu = PyFlameMenu(
            text=template_name,
            menu_options=list(templates),
            connect=switch_template,
            )

        # Entries
        self.projects_path_entry = PyFlameEntry(
            text=templates[template_name]['projects_path'],
            )

        # File System Folders Tree
        self.file_system_folder_tree = PyFlameTreeWidget(
            column_names=[
                'File System Folder Template',
                ],
            tree_dict=templates[template_name]['file_system_folders'],
            )
        # Media Panel Library/Folder Tree
        self.media_panel_library_folders_tree = PyFlameTreeWidget(
            column_names=[
                'Media Panel Library/Folder Template',
                ],
            tree_dict=templates[template_name]['media_panel_library_folders'],
            )

        # Token Push Button
        self.setup_token_push_button = PyFlameTokenMenu(
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nickname': '<ProjectNickName>',
                'User Name': '<UserName>',
                'User Nickname': '<UserNickName>',
                'Year (YYYY)': '<YYYY>',
                'Year (YY)': '<YY>',
                'Month (MM)': '<MM>',
                'Day (DD)': '<DD>',
                'Hour': '<Hour>',
                'Minute': '<Minute>',
                'AM/PM (AMPM)': '<AMPM>',
                'am/pm (ampm)': '<ampm>',
                },
            token_dest=self.projects_path_entry,
            )

        # Push Buttons
        self.create_system_folders_push_button = PyFlamePushButton(
            text='Create Folders',
            checked=templates[template_name]['create_file_system_folders'],
            )
        self.create_media_panel_lib_folders_push_button = PyFlamePushButton(
            text='Create Lib/Folders',
            checked=templates[template_name]['create_media_panel_folders'],
            )
        self.delete_default_library_push_button = PyFlamePushButton(
            text='Delete Default Lib',
            checked=templates[template_name]['delete_default_library'],
            )

        # Buttons
        self.template_new_button = PyFlameButton(
            text='New',
            connect=new_template,
            )
        self.template_rename_button = PyFlameButton(
            text='Rename',
            connect=rename_template,
            )
        self.template_duplicate_button = PyFlameButton(
            text='Duplicate',
            connect=duplicate_template,
            )
        self.template_delete_button = PyFlameButton(
            text='Delete',
            connect=delete_template,
            )

        self.file_system_add_folder_button = PyFlameButton(
            text='Add Folder',
            connect=partial(self.file_system_folder_tree.add_item, 'New Folder'),
            )
        self.file_system_delete_folder_button = PyFlameButton(
            text='Delete Folder',
            connect=self.file_system_folder_tree.delete_item,
            )
        self.file_system_sort_button = PyFlameButton(
            text='Sort Folders',
            connect=self.file_system_folder_tree.sort_items,
            )
        self.file_system_manual_create_button = PyFlameButton(
            text='Manually Create',
            connect=manually_create_file_system_folders,
            )

        self.media_panel_add_button = PyFlameButton(
            text='Add Lib/Folder',
            connect=media_panel_add,
            )
        self.media_panel_delete_folder_button = PyFlameButton(
            text='Delete Lib/Folder',
            connect=self.media_panel_library_folders_tree.delete_item,
            )
        self.media_panel_sort_button = PyFlameButton(
            text='Sort Libs/Folders',
            connect=self.media_panel_library_folders_tree.sort_items,
            )
        self.media_panel_manual_create_button = PyFlameButton(
            text='Manually Create',
            connect=manually_create_libraries,
            )

        setup_browse_button = PyFlameButton(
            text='Browse',
            connect=folder_browse,
            )
        setup_save_button = PyFlameButton(
            text='Save',
            connect=save,
            color=Color.BLUE,
            )
        setup_cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.template_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.template_menu, 0, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(self.template_new_button, 0, 5)
        self.setup_window.grid_layout.addWidget(self.template_rename_button, 0, 6)
        self.setup_window.grid_layout.addWidget(self.template_duplicate_button, 1, 5)
        self.setup_window.grid_layout.addWidget(self.template_delete_button, 1, 6)

        self.setup_window.grid_layout.addWidget(self.delete_default_library_push_button, 2, 0)

        self.setup_window.grid_layout.addWidget(self.media_panel_folders_setup_label, 3, 0, 1, 3)

        self.setup_window.grid_layout.addWidget(self.create_media_panel_lib_folders_push_button, 4, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_add_button, 5, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_delete_folder_button, 6, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_sort_button, 7, 0)
        self.setup_window.grid_layout.addWidget(self.media_panel_manual_create_button, 10, 0)

        self.setup_window.grid_layout.addWidget(self.media_panel_library_folders_tree, 4, 1, 7, 2)

        self.setup_window.grid_layout.addWidget(self.file_system_folder_setup_label, 3, 4, 1, 3)

        self.setup_window.grid_layout.addWidget(self.file_system_folder_tree, 4, 4, 7, 2)

        self.setup_window.grid_layout.addWidget(self.create_system_folders_push_button, 4, 6)
        self.setup_window.grid_layout.addWidget(self.file_system_add_folder_button, 5, 6)
        self.setup_window.grid_layout.addWidget(self.file_system_delete_folder_button, 6, 6)
        self.setup_window.grid_layout.addWidget(self.file_system_sort_button, 7, 6)
        self.setup_window.grid_layout.addWidget(self.file_system_manual_create_button, 10, 6)

        self.setup_window.grid_layout.addWidget(self.projects_path_label, 12, 0)
        self.setup_window.grid_layout.addWidget(self.projects_path_entry, 12, 1, 1, 4)
        self.setup_window.grid_layout.addWidget(setup_browse_button, 12, 5)
        self.setup_window.grid_layout.addWidget(self.setup_token_push_button, 12, 6)

        self.setup_window.grid_layout.addWidget(setup_cancel_button, 14, 5)
        self.setup_window.grid_layout.addWidget(setup_save_button, 14, 6)

    # ==============================================================================

    def create_on_start(self, ignore_mark: bool=False) -> None:
        """
        Create On Start
        ===============

        Offer to create file system folders and media panel libraries/folders on project start up.

        The first time the script runs (first_time), only ask to open the Setup window. This is asked once: first_time is
        saved as False as soon as either button is clicked.

        If project is in ignore_projects list, do not offer to create folders, unless ignore_mark is True.
        If any template has create file system folders or media panel folders on, open the template picker window.

        Args
        ----
            ignore_mark (bool): Create folders even if the project is already marked as done. Used when creating from the Setup window.
        """

        # Use the project that is current now, in case another project was loaded while Setup was open
        self.get_current_project()

        if self.settings.first_time:
            open_setup = PyFlameMessageWindow(
                message='Configure project folders and media panel libraries/folders now?\n\nThis can be done later through the Setup window.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Create Project Folders Setup',
                message_type=MessageType.CONFIRM,
                parent=None,
                )

            # Only ask once, whichever button was clicked
            self.refresh_settings()
            self.settings.save_config(config_values={'first_time': False})

            if open_setup:
                self.setup_window()
                PyFlameMessageWindow(
                    message='Set up a folder template and enable creating Media Panel Libraries/Folders and/or File System Folders, then Save.\n\nYou will then be offered to create folders after saving and when Flame starts.',
                    parent=None,
                    )
        else:
            # If current project is in ignore_projects list, do not create any folders, unless the user asked from the Setup window
            if ignore_mark or not self.project_name in self.settings.ignore_projects:
                if self.get_enabled_templates(self.settings.templates):
                    self.template_picker(from_setup=ignore_mark)
            else:
                pyflame.print('Skipped Creating File System Folders and Media Panel Libraries/Folders')

    def get_enabled_templates(self, templates: dict) -> list:
        """
        Get Enabled Templates
        =====================

        Get the names of the templates that have create file system folders and/or create media panel folders on.

        Args
        ----
            templates (dict): Templates, name: template.

        Returns
        -------
            enabled_templates (list): Template names, in template order.
        """

        return [name for name, template in templates.items() if template['create_file_system_folders'] or template['create_media_panel_folders']]

    def template_picker(self, from_setup: bool) -> None:
        """
        Template Picker
        ===============

        Window to pick the template to create project folders from. Only templates with a create option on are listed,
        and only the picked template's trees that will be created are shown.

        Create runs the file system and media panel steps, each checked on its own. Cancel at start-up marks the project
        so it isn't offered again. Cancel from the Setup window does nothing.

        Args
        ----
            from_setup (bool): Opened from the Setup window (Save, then Create) instead of at start-up.
        """

        def show_template() -> None:
            """
            Show Template
            =============

            Show the template picked in the Template menu. Lay out only the trees the template will create. One tree uses the full width.
            """

            template = self.settings.templates[self.picker_template_menu.text]
            show_file_system = template['create_file_system_folders']
            show_media_panel = template['create_media_panel_folders']
            tree_columns = 2 if show_file_system and show_media_panel else 4

            # Take the template widgets out of the layout, then add back the ones this template uses
            for widget in (self.picker_projects_path_title_label, self.picker_projects_path_label, self.picker_file_system_tree, self.picker_media_panel_tree, self.picker_default_library_label):
                self.picker_window.grid_layout.removeWidget(widget)
                widget.hide()

            if show_file_system:
                self.picker_projects_path_label.text = pyflame.resolve_tokens(template['projects_path']).strip().rstrip('/')
                self.picker_file_system_tree.tree_dict = template['file_system_folders']
                self.picker_window.grid_layout.addWidget(self.picker_projects_path_title_label, 1, 0)
                self.picker_window.grid_layout.addWidget(self.picker_projects_path_label, 1, 1, 1, 3)
                self.picker_window.grid_layout.addWidget(self.picker_file_system_tree, 2, 0, 6, tree_columns)
                for widget in (self.picker_projects_path_title_label, self.picker_projects_path_label, self.picker_file_system_tree):
                    widget.show()

            if show_media_panel:
                self.picker_media_panel_tree.tree_dict = template['media_panel_library_folders']
                self.picker_window.grid_layout.addWidget(self.picker_media_panel_tree, 2, 4 - tree_columns, 6, tree_columns)
                self.picker_media_panel_tree.show()

                # Default Library note, only when it will be deleted
                if template['delete_default_library'] and not self.default_library_in_template(template['media_panel_library_folders']) and 'Default Library' in [str(lib.name)[1:-1] for lib in self.workspace.libraries]:
                    self.picker_window.grid_layout.addWidget(self.picker_default_library_label, 8, 0, 1, 4)
                    self.picker_default_library_label.show()

        def forget_picker() -> None:
            """
            Forget Picker
            =============

            Remove this script from the open pickers list once its window is closed.
            """

            if self in open_picker_scripts:
                open_picker_scripts.remove(self)

        def close_if_project_changed() -> bool:
            """
            Close If Project Changed
            ========================

            Flame reloads the hooks when a project is loaded, so a window from an earlier project may still be open.
            If the current project isn't the one this window was opened for, close it without marking anything.

            Returns
            -------
                closed (bool): True if another project is current and the window was closed.
            """

            if str(flame.project.current_project.name) == self.picker_project_name:
                return False

            self.picker_window.close()
            forget_picker()

            return True

        def create() -> None:
            """
            Create
            ======

            Save the picked template as last used, close the window, then create the project folders.

            If another project was loaded since the window opened, only show a message and close the window.
            Nothing is created or marked, and last_template isn't saved.
            """

            if close_if_project_changed():
                PyFlameMessageWindow(
                    message=f'This window was opened for project {self.picker_project_name}. The current project is now {flame.project.current_project.name}.\n\nNothing was created. Use Setup to create folders for the current project.',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )

                return

            # Create from the template as shown in this window, then save it as last used on top of the config as it is now
            template_name = self.picker_template_menu.text
            template = self.settings.templates[template_name]
            self.refresh_settings()
            self.settings.save_config(
                config_values={
                    'last_template': template_name,
                    }
                )
            self.picker_window.close()
            forget_picker()
            self.create_project_folders(template)

        def cancel() -> None:
            """
            Cancel
            ======

            Close the window. At start-up, mark the project so it isn't offered again and say how to create folders later.
            If another project was loaded since the window opened, only close it: nothing is marked and no message is shown.
            """

            if close_if_project_changed():
                pyflame.print('Template Window Closed, Project Changed Since It Opened')

                return

            self.picker_window.close()
            forget_picker()

            if from_setup:
                pyflame.print('Creating Project Folders Cancelled')

                return

            self.mark_project()
            PyFlameMessageWindow(
                message='Project folders won\'t be offered for this project at start-up again.\n\nTo create them later, use Flame Main Menu -> Logik -> Logik Portal Script Setup -> Create Project Folders Setup (Manually Create, or Save then Create).',
                parent=None,
                )

        # Only templates with a create option on. Start on the last used template if it's one of them.
        enabled_templates = self.get_enabled_templates(self.settings.templates)

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.picker_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=create,
            escape_pressed=cancel,
            grid_layout_columns=4,
            grid_layout_rows=11,
            parent=None,
            )

        # Project this picker creates folders for. Kept apart from self.project_name, which get_current_project can change.
        self.picker_project_name = str(self.project_name)

        # Keep the open picker, so it can be closed if another project is loaded
        if self not in open_picker_scripts:
            open_picker_scripts.append(self)

        # Labels
        self.picker_template_label = PyFlameLabel(
            text='Template',
            )
        self.picker_projects_path_title_label = PyFlameLabel(
            text='Projects Path',
            )
        self.picker_projects_path_label = PyFlameLabel(
            text='',
            )
        self.picker_default_library_label = PyFlameLabel(
            text='The Default Library will be deleted.',
            )

        # Menus
        self.picker_template_menu = PyFlameMenu(
            text=self.settings.last_template if self.settings.last_template in enabled_templates else enabled_templates[0],
            menu_options=enabled_templates,
            connect=show_template,
            )

        # Trees, read only
        self.picker_file_system_tree = PyFlameTreeWidget(
            column_names=[
                'File System Folders',
                ],
            )
        self.picker_media_panel_tree = PyFlameTreeWidget(
            column_names=[
                'Media Panel Libraries/Folders',
                ],
            )
        for tree in (self.picker_file_system_tree, self.picker_media_panel_tree):
            tree.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers) # fill_tree_dict(editable=False) still leaves items editable

        # Buttons
        picker_cancel_button = PyFlameButton(
            text='Cancel',
            connect=cancel,
            )
        picker_create_button = PyFlameButton(
            text='Create',
            connect=create,
            color=Color.BLUE,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.picker_window.grid_layout.addWidget(self.picker_template_label, 0, 0)
        self.picker_window.grid_layout.addWidget(self.picker_template_menu, 0, 1, 1, 3)

        self.picker_window.grid_layout.addWidget(picker_cancel_button, 10, 2)
        self.picker_window.grid_layout.addWidget(picker_create_button, 10, 3)

        show_template()

    def create_project_folders(self, template: dict) -> None:
        """
        Create Project Folders
        ======================

        Create the file system and media panel steps the template has turned on. Each step is checked on its own:
        an existing project folder or library only gets its missing folders, after asking.

        Mark the project unless every enabled step ended in an error.

        Args
        ----
            template (dict): Template with projects_path, create options, file_system_folders and media_panel_library_folders.
        """

        results = []

        if template['create_file_system_folders']:
            # Resolve tokens once, so creating and checking use the same folder names. A token that resolved to nothing is a failed step.
            resolved_template = self.resolve_file_system_template(template)
            projects_path = resolved_template['projects_path'].strip().rstrip('/')

            if not self.check_file_system_template(template, resolved_template):
                results.append(False)
            # Project folder already exists, only ask about missing folders
            elif os.path.isdir(projects_path):
                pyflame.print(f'Project File System Folder Already Exists: {projects_path}')
                results.append(self.create_missing_file_system_folders(resolved_template, projects_path) is not None)
            else:
                created = self.create_file_system_folders(resolved_template)
                if created:
                    pyflame.print('File System Folders Created', text_color=TextColor.GREEN)
                results.append(created)

        if template['create_media_panel_folders']:
            libraries = self.create_media_panel_folders(template)
            if libraries and (libraries[0] or libraries[1]):
                pyflame.print('Media Panel Libraries/Folders Created', text_color=TextColor.GREEN)
            elif libraries:
                pyflame.print('Media Panel Libraries Already Exist')
            results.append(libraries is not None)

        # Mark project unless every step ended in an error
        if any(results):
            self.mark_project()

    def create_file_system_folders(self, template: dict) -> bool:
        """
        Create File System Folders
        ==========================

        Create file system folders based on template created in Setup window.

        Check every folder in the template exists afterwards. Missing folders are listed in one error window.

        Args
        ----
            template (dict): Template with projects_path and file_system_folders, tokens already resolved (resolve_file_system_template).

        Returns
        -------
            created (bool): True if every folder exists, False if not.
        """

        # Jobs path is already resolved, ignore trailing slashes
        translated_jobs_root_path = template['projects_path'].strip().rstrip('/')
        project_folder_name = os.path.basename(translated_jobs_root_path)
        dest_path = os.path.dirname(translated_jobs_root_path)

        # Stop if path has no project folder name or no parent folder (e.g. / or empty)
        if not project_folder_name.strip() or not dest_path.strip():
            PyFlameMessageWindow(
                message=f'Projects Path is not a valid folder path:\n\n{template["projects_path"] or "/"}\n\nNo file system folders created.',
                message_type=MessageType.ERROR,
                parent=None,
                )

            return False

        # Create file system folders
        try:
            pyflame.create_file_system_folder(
                folder_name=project_folder_name,
                folder_structure=template['file_system_folders'],
                dest_path=dest_path,
                )
        except Exception as e:
            PyFlameMessageWindow(
                message=f'Could not create file system folders.\n\n{e}',
                message_type=MessageType.ERROR,
                parent=None,
                )

            return False

        # Check every folder was created
        folder_paths = self.get_file_system_folder_paths(template, os.path.join(dest_path, project_folder_name))
        missing_folders = [folder_path for folder_path in folder_paths if not os.path.isdir(folder_path)]
        if missing_folders:
            PyFlameMessageWindow(
                message='Could not create these file system folders:\n\n' + '\n'.join(missing_folders),
                message_type=MessageType.ERROR,
                parent=None,
                )

            return False

        return True

    def resolve_folder_structure(self, folder_structure: dict) -> dict:
        """
        Resolve Folder Structure
        ========================

        Copy a nested folder template with the tokens in every folder name resolved.

        Args
        ----
            folder_structure (dict): Nested folder template.

        Returns
        -------
            resolved_structure (dict): Nested folder template with resolved names. Siblings that resolve to the same name are merged.
        """

        def merge_folders(target: dict, source: dict) -> None:
            """
            Merge Folders
            =============

            Merge a nested folder template into another one, keeping the subfolders of both.

            Args
            ----
                target (dict):
                    Nested folder template to merge into.

                source (dict):
                    Nested folder template to merge from.
            """

            for folder_name, sub_folders in source.items():
                merge_folders(target.setdefault(folder_name, {}), sub_folders)

        # Siblings that resolve to the same name share one folder, so merge their subfolders
        resolved_structure = {}
        for folder_name, sub_folders in folder_structure.items():
            merge_folders(resolved_structure.setdefault(pyflame.resolve_tokens(folder_name), {}), self.resolve_folder_structure(sub_folders))

        return resolved_structure

    def resolve_file_system_template(self, template: dict) -> dict:
        """
        Resolve File System Template
        ============================

        Copy a template with the tokens in projects_path and the file system folder names resolved once.
        Creating and checking folders both use this copy, so a token like <Minute> can't change between them.

        Args
        ----
            template (dict): Template with projects_path and file_system_folders.

        Returns
        -------
            resolved_template (dict): Copy of the template with projects_path and file_system_folders resolved.
        """

        # Double slashes typed in the path are made single and trailing slashes removed before resolving,
        # so only a token that resolves to nothing leaves an empty part
        projects_path = template['projects_path'].strip()
        while '//' in projects_path:
            projects_path = projects_path.replace('//', '/')
        resolved_template = copy.deepcopy(template)
        resolved_template['projects_path'] = pyflame.resolve_tokens(projects_path.rstrip('/'))
        resolved_template['file_system_folders'] = self.resolve_folder_structure(template['file_system_folders'])

        return resolved_template

    def get_empty_folder_names(self, folder_structure: dict) -> list:
        """
        Get Empty Folder Names
        ======================

        Find folder names in a nested folder template that are empty or only spaces once their tokens are resolved.

        Args
        ----
            folder_structure (dict): Nested folder template, names as typed.

        Returns
        -------
            empty_names (list): Folder names, as typed, that resolve to nothing.
        """

        empty_names = []
        for folder_name, sub_folders in folder_structure.items():
            if not pyflame.resolve_tokens(folder_name).strip():
                empty_names.append(folder_name)
            empty_names.extend(self.get_empty_folder_names(sub_folders))

        return empty_names

    def check_file_system_template(self, template: dict, resolved_template: dict) -> bool:
        """
        Check File System Template
        ==========================

        Check the resolved Projects Path and file system folder names for empty parts, for example from <ProjectNickName>
        when the project has no nickname. Show one error and return False if there are any.

        Args
        ----
            template (dict):
                Template as typed.

            resolved_template (dict):
                Same template from resolve_file_system_template.

        Returns
        -------
            valid (bool): True if nothing is empty.
        """

        # The template's top folder is replaced by the project folder, so only the folders under it are checked
        empty_names = []
        for sub_folders in template['file_system_folders'].values():
            empty_names.extend(self.get_empty_folder_names(sub_folders))

        # A folder in the path that is empty (//) or only spaces
        path_parts = resolved_template['projects_path'].split('/')[1:]
        if not empty_names and not [part for part in path_parts if not part.strip()]:
            return True

        message = f'The file system path or a folder name has an empty part. A token such as <ProjectNickName> or <UserNickName> had no value (for example the project has no nickname).\n\nProjects Path: {template["projects_path"]}\n\nResolved: {resolved_template["projects_path"]}'
        if empty_names:
            message += '\n\nEmpty folder names: ' + ', '.join(empty_names)
        PyFlameMessageWindow(
            message=message + '\n\nNo file system folders created.',
            message_type=MessageType.ERROR,
            parent=None,
            )

        return False

    def get_template_folder_paths(self, folder_structure: dict, parent_path: str) -> list:
        """
        Get Template Folder Paths
        =========================

        Get the paths of every nested folder in a template. Folder names must already be resolved.

        Args
        ----
            folder_structure (dict):
                Nested folder template, names resolved.

            parent_path (str):
                Path the folders are in.

        Returns
        -------
            folder_paths (list): Folder paths.
        """

        folder_paths = []
        for folder_name, sub_folders in folder_structure.items():
            folder_path = os.path.join(parent_path, folder_name)
            folder_paths.append(folder_path)
            folder_paths.extend(self.get_template_folder_paths(sub_folders, folder_path))

        return folder_paths

    def get_file_system_folder_paths(self, template: dict, project_folder_path: str) -> list:
        """
        Get File System Folder Paths
        ============================

        Get the project folder path and the path of every folder in the file system template.
        The template's top key is replaced by the project folder, as PyFlameLib does.

        Args
        ----
            template (dict):
                Template with file_system_folders, names already resolved.

            project_folder_path (str):
                Resolved project folder path.

        Returns
        -------
            folder_paths (list): Project folder path, then every template folder path.
        """

        folder_paths = [project_folder_path]
        for sub_folders in template['file_system_folders'].values():
            folder_paths.extend(self.get_template_folder_paths(sub_folders, project_folder_path))

        return folder_paths

    def create_missing_file_system_folders(self, template: dict, project_folder_path: str) -> bool | None:
        """
        Create Missing File System Folders
        ==================================

        The project folder already exists. Ask to create any template folders that are missing.

        Args
        ----
            template (dict):
                Template with projects_path and file_system_folders, tokens already resolved.

            project_folder_path (str):
                Resolved project folder path.

        Returns
        -------
            created (bool | None): True if missing folders were created, False if nothing was missing or the user cancelled, None if an error stopped it.
        """

        missing_folders = [folder_path for folder_path in self.get_file_system_folder_paths(template, project_folder_path) if not os.path.isdir(folder_path)]

        if not missing_folders:
            pyflame.print(f'All Project File System Folders Already Exist: {project_folder_path}')

            return False

        if not PyFlameMessageWindow(
            message=f'Project folder already exists:\n\n{project_folder_path}\n\nThese folders are missing:\n\n' + '\n'.join(os.path.relpath(folder_path, project_folder_path) for folder_path in missing_folders) + '\n\nCreate missing folders?',
            message_type=MessageType.CONFIRM,
            parent=None,
            ):
            pyflame.print('Skipped Creating Missing File System Folders')

            return False

        # Existing folders are kept, only missing ones are made
        if not self.create_file_system_folders(template):
            return None

        return True

    def default_library_in_template(self, media_panel_library_folders: dict) -> bool:
        """
        Default Library In Template
        ===========================

        Check if a media panel template has its own top-level library named Default Library. If it does,
        the workspace's Default Library is never deleted.

        Args
        ----
            media_panel_library_folders (dict): Media panel template, with Workspace as the top key.

        Returns
        -------
            in_template (bool): True if the template has a library that resolves to Default Library.
        """

        library_names = (media_panel_library_folders or {}).get('Workspace', {})

        return 'Default Library' in [pyflame.resolve_tokens(library_name) for library_name in library_names]

    def mark_project(self) -> None:
        """
        Mark Project
        ============

        Add the current project to the ignore_projects list so it isn't asked about at the next start.
        """

        # Start from the list in the file now, not the one loaded when this window opened
        self.refresh_settings()

        if self.project_name in self.settings.ignore_projects:
            return

        self.settings.save_config(
            config_values={
                'ignore_projects': self.settings.ignore_projects + [self.project_name],
                }
            )

    def create_media_panel_folders(self, template: dict) -> tuple | None:
        """
        Create Media Panel Folders
        ==========================

        Create media panel libraries and folders based on template created in Setup window.

        Libraries that already exist in the current workspace aren't created again. If any of their template
        folders are missing, ask to create only the missing folders. Last, delete the Default Library if it exists,
        the template's delete_default_library is on and the template has no library named Default Library of its own.
        Otherwise leave it alone.

        Args
        ----
            template (dict): Template with media_panel_library_folders and delete_default_library.

        Returns
        -------
            libraries (tuple | None): Created library names, folder paths added to existing libraries (Library/Folder/Sub) and existing library names, or None if an error stopped it.
        """

        def get_missing_folders(folder_structure: dict, parent, parent_path: str) -> list:
            """
            Get Missing Folders
            ===================

            Find template folders missing from an existing library or folder. A missing folder's whole subtree is missing.

            Args
            ----
                folder_structure (dict):
                    Nested folder template.

                parent (PyLibrary | PyFolder):
                    Existing library or folder to check.

                parent_path (str):
                    Path of parent used in messages (Library/Folder).

            Returns
            -------
                missing_folders (list): (parent, parent_path, folder_name, sub_folders) for each missing folder whose parent exists, folder_name resolved.
            """

            existing_folders = {str(folder.name)[1:-1]: folder for folder in parent.folders}
            missing_folders = []
            for folder_name, sub_folders in folder_structure.items():
                resolved_folder_name = pyflame.resolve_tokens(folder_name)
                if resolved_folder_name in existing_folders:
                    missing_folders.extend(get_missing_folders(sub_folders, existing_folders[resolved_folder_name], f'{parent_path}/{resolved_folder_name}'))
                else:
                    missing_folders.append((parent, parent_path, resolved_folder_name, sub_folders))

            return missing_folders

        def create_folders(folder_structure: dict, parent) -> None:
            """
            Create Folders
            ==============

            Create a nested folder template in a library or folder, with tokens resolved.

            Args
            ----
                folder_structure (dict):
                    Nested folder template.

                parent (PyLibrary | PyFolder):
                    Library or folder to create folders in.
            """

            for folder_name, sub_folders in folder_structure.items():
                folder = parent.create_folder(pyflame.resolve_tokens(folder_name))
                create_folders(sub_folders, folder)

        # Stop if a library or folder name resolves to nothing
        empty_names = self.get_empty_folder_names(template['media_panel_library_folders'].get('Workspace', {}))
        if empty_names:
            PyFlameMessageWindow(
                message='A media panel library or folder name is empty. A token such as <ProjectNickName> or <UserNickName> had no value (for example the project has no nickname).\n\nEmpty names: ' + ', '.join(empty_names) + '\n\nNo media panel libraries/folders created.',
                message_type=MessageType.ERROR,
                parent=None,
                )

            return None

        try:
            # Libraries that already exist in the current workspace aren't created again
            existing_libraries = {str(lib.name)[1:-1]: lib for lib in self.workspace.libraries}
            library_folders = {}
            created_libraries = []
            skipped_libraries = []
            missing_folders = []
            for library_name, folder_structure in template['media_panel_library_folders']['Workspace'].items():
                resolved_library_name = pyflame.resolve_tokens(library_name)
                if resolved_library_name in existing_libraries:
                    pyflame.print(f'Library Already Exists: {resolved_library_name}')
                    skipped_libraries.append(resolved_library_name)
                    missing_folders.extend(get_missing_folders(folder_structure, existing_libraries[resolved_library_name], resolved_library_name))
                else:
                    library_folders[library_name] = folder_structure
                    created_libraries.append(resolved_library_name)

            # Ask to create folders missing from existing libraries
            missing_folder_paths = []
            for parent, parent_path, folder_name, sub_folders in missing_folders:
                missing_folder_paths.append(f'{parent_path}/{folder_name}')
                missing_folder_paths.extend(self.get_template_folder_paths(self.resolve_folder_structure(sub_folders), f'{parent_path}/{folder_name}'))

            added_folders = []
            if missing_folders:
                if PyFlameMessageWindow(
                    message='These folders are missing from existing libraries:\n\n' + '\n'.join(missing_folder_paths) + '\n\nCreate missing folders?',
                    message_type=MessageType.CONFIRM,
                    parent=None,
                    ):
                    for parent, parent_path, folder_name, sub_folders in missing_folders:
                        create_folders(sub_folders, parent.create_folder(folder_name))
                    added_folders = missing_folder_paths
                    pyflame.print('Missing Library Folders Created', text_color=TextColor.GREEN)
                else:
                    pyflame.print('Skipped Creating Missing Library Folders')

            if library_folders:
                pyflame.create_media_panel_libraries(
                    library_structure={'Workspace': library_folders},
                    )
            else:
                pyflame.print('No Media Panel Libraries To Create')

            # Delete Default Library, only if the template says to and doesn't have its own Default Library
            for lib in self.workspace.libraries:
                if str(lib.name)[1:-1] == 'Default Library':
                    if not template['delete_default_library']:
                        pyflame.print('Default Library Kept')
                    elif self.default_library_in_template(template['media_panel_library_folders']):
                        pyflame.print('Default Library Kept (in template)')
                    else:
                        flame.delete(lib)
                        pyflame.print('Default Library Deleted', text_color=TextColor.GREEN)
        except Exception as e:
            PyFlameMessageWindow(
                message=f'Could not create media panel libraries/folders.\n\n{e}',
                message_type=MessageType.ERROR,
                parent=None,
                )

            return None

        return created_libraries, added_folders, skipped_libraries

# ==============================================================================
# [Session State]
# ==============================================================================

# Projects already offered, and the scripts with a template picker open, since the hooks were last loaded.
# Flame reloads the hooks when a project is loaded, so these only cover one project load (e.g. both hooks firing for it).
offered_projects = set()
open_picker_scripts = []

# ==============================================================================
# [Entry Points]
# ==============================================================================

def setup(selection) -> None:

    pyflame.print_title(f'{SCRIPT_NAME} - Setup {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    script = CreateProjectFolders(selection)
    script.setup_window()

def create_folders(selection) -> None:

    pyflame.print_title(f'{SCRIPT_NAME} - Create Folders {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    script = CreateProjectFolders(selection)
    script.create_on_start()

def create_folders_once_per_load(project_name: str) -> None:
    """
    Create Folders Once Per Load
    ============================

    Run the start-up flow (create_folders) for the current project, once per project load. Used by both
    the app_initialized and project_changed hooks, so a project is only offered once even if Flame calls both for the same load.
    Flame reloads the hooks when a project is loaded, so the list of offered projects starts empty for each load.

    Template pickers this module knows are still open for another project are closed first, without marking that project or
    running their Cancel. A picker from before a reload isn't known here, but its Create and Cancel check the current project themselves.

    Args
    ----
        project_name (str):
            Project name passed by the Flame hook. Only compared with the current project's name, which is used to
            track the project (the same name the start-up flow marks).
    """

    current_project_name = str(flame.project.current_project.name)

    if str(project_name) != current_project_name:
        pyflame.print(f'Hook project name {project_name} is not the current project {current_project_name}. Using the current project.', print_type=PrintType.WARNING)

    # Close pickers left open for another project, so they can't create folders for the wrong project
    for script in [script for script in open_picker_scripts if script.picker_project_name != current_project_name]:
        try:
            script.picker_window.close()
        except Exception:
            pass # Window already closed and deleted
        open_picker_scripts.remove(script)

    if current_project_name in offered_projects:
        pyflame.print(f'Project Already Offered, Skipped: {current_project_name}')

        return

    offered_projects.add(current_project_name)
    create_folders(project_name)

def app_initialized(project_name: str) -> None:

    create_folders_once_per_load(project_name)

def project_changed(project_name: str, *args, **kwargs) -> None:

    create_folders_once_per_load(project_name)

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_main_menu_custom_ui_actions() -> list:

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
                    'name': 'Create Project Folders Setup',
                    'execute': setup,
                    'minimumVersion': '2025.2'
               }
           ]
        }
    ]
