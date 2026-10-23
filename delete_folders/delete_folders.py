# Delete Folders
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Delete Folders
Script Version: 2.11.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 10.04.20
Update Date: 10.13.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: MediaHub - Files Tab

Description:

    Delete one or more folders along with contents in the MediaHub File Tab view

    *** WARNING - THIS WILL DELETE ALL SELECTED FOLDERS/SUBFOLDERS - THIS IS CAN NOT BE UNDONE***

URL:
    https://logik-portal.com/scripts/delete_folders

Menu:

    Right-click with folders selected -> Delete Selected Folders

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.11.1 10.13.26
        - Confirmation window now lists the folders to be deleted.
        - Added a second warning when a selected folder is a symlink. Confirming deletes the folder the link points to and removes the link.
        - A folder that fails to delete no longer stops the rest. Failures are listed in one message at the end.
        - Symlinks pointing to /, a drive root, the home folder or a folder containing the link are never deleted.
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v2.11.0 03.26.26
        - Updated to PyFlameLib v5.3.0.

    v2.10.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v2.9.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v2.8.0 12.16.24
        - Updated to PyFlameLib v3.3.0.
        - Added script install check.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script installed in different locations.

    v2.7.0 08.05.24
        - Updated to PyFlameLib v3.0.0.

    v2.6.0 01.24.24
        - Updates to PySide.

    v2.5.0 07.27.23
        - Updated to PyFlameLib v2.0.0.
        - Updated versioning to semantic versioning.

    v2.4 09.28.22
        - Updated menus for Flame 2023.2+.

    v2.3 05.24.22
        - Messages print to Flame message window - Flame 2023.1 and later.

    v2.2 03.14.22
        - Added delete confirmation

    v2.1 05.19.21
        - Updated to be compatible with Flame 2022/Python 3.7.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os
import shutil
import flame

from lib.pyflame_lib_delete_folders import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Delete Folders'
SCRIPT_VERSION = 'v2.11.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

def delete_folders(selection):
    """
    Delete Folders
    ==============

    This cannot be undone!
    ----------------------

    Delete all files and sub-folders in selected folder(s).
    """

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    def refuse_reason(link: str, target: str) -> str:
        """
        Refuse Reason
        =============

        Check whether a symlink's target is a protected location that must never be deleted.

        Args
        ----
            link (str):
                Path of the symlink, without the trailing slash.

            target (str):
                Resolved real path the symlink points to.

        Returns
        -------
            reason (str): Short reason the target is protected, or '' if it can be deleted.
        """

        home = os.path.realpath(os.path.expanduser('~'))
        link_parent = os.path.realpath(os.path.dirname(link))

        if target == '/':
            return 'target is the root folder'
        if os.path.ismount(target):
            return 'target is a drive root'
        if target == home or home.startswith(target + os.sep):
            return 'target is the home folder or contains it'
        if link_parent == target or link_parent.startswith(target + os.sep):
            return 'target contains the link'

        return ''

    # List selected folder paths without the trailing slash
    folder_list = '\n'.join(folder.path.rstrip('/') for folder in selection)

    delete_files = PyFlameMessageWindow(
        message=(
            'Delete selected folder(s)?\n\n'
            f'{folder_list}\n\n'
            'All files and sub-folders in selected folder(s) will be deleted.\n\n'
            'This cannot be undone!\n\n'
            'Are you sure you want to continue?'
            ),
        message_type=MessageType.WARNING,
        parent=None,
        )

    if delete_files:

        # Save each link's target once so the folder deleted is the one shown in the warning. Links to protected locations are kept apart and never deleted.
        symlinks = {}
        refused = {}
        for folder in selection:
            link = folder.path.rstrip('/')
            if os.path.islink(link):
                target = os.path.realpath(link)
                reason = refuse_reason(link, target)
                if reason:
                    refused[link] = (target, reason)
                else:
                    symlinks[link] = target

        # Warn separately about symlinks, since rmtree with a trailing slash follows the link and deletes the real folder
        if symlinks or refused:
            message = ''
            if symlinks:
                symlink_list = '\n'.join(f'{link} -> {target}' for link, target in symlinks.items())
                message += (
                    'These selected folder(s) are symlinks:\n\n'
                    f'{symlink_list}\n\n'
                    'The real folder(s) these links point to, and everything in them, will be deleted. '
                    'The links will also be removed.\n\n'
                    'This cannot be undone!\n\n'
                    )
            if refused:
                refused_list = '\n'.join(f'{link} -> {target} ({reason})' for link, (target, reason) in refused.items())
                message += (
                    'These symlink(s) point to a protected location and will NOT be deleted:\n\n'
                    f'{refused_list}\n\n'
                    )
            message += 'Are you sure you want to continue?'

            delete_symlinks = PyFlameMessageWindow(
                message=message,
                message_type=MessageType.WARNING,
                parent=None,
                )

            # Cancel everything if symlink delete is not confirmed
            if not delete_symlinks:
                pyflame.print('Delete cancelled. Nothing was deleted.', print_type=PrintType.WARNING)
                return

        pyflame.print(
            text='Deleting Selected Folders:',
            underline=True,
            text_color=TextColor.GREEN,
            )

        # Collect failed deletes to show in one message at the end
        failures = []
        for folder in selection:
            pyflame.print(
                text=f'{folder.path[:-1]}',
                print_type=PrintType.WARNING,
                new_line=False,
                )

            # Skip links to protected locations: never delete the target or remove the link
            path = folder.path.rstrip('/')
            if path in refused:
                target, reason = refused[path]
                pyflame.print(f'Not deleted {path}: {reason} ({target})', print_type=PrintType.ERROR)
                failures.append(f'{path}: not deleted, {reason} ({target})')
                continue

            # Keep going if one folder fails so the rest still get deleted
            try:
                if path in symlinks:
                    shutil.rmtree(symlinks[path])

                    # Link may already be gone if its target was one of its ancestors
                    if os.path.lexists(path):
                        os.unlink(path)
                else:
                    shutil.rmtree(folder.path)
            except Exception as e:
                pyflame.print(f'Could not delete {path}: {e}', print_type=PrintType.ERROR)
                failures.append(f'{path}: {e}')

        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")

        # Show all failures in one message
        if failures:
            failure_list = '\n'.join(failures)
            PyFlameMessageWindow(
                message=f'These folder(s) could not be deleted:\n\n{failure_list}',
                message_type=MessageType.ERROR,
                parent=None,
                )
        else:
            pyflame.print('\nSelected Folders Deleted', text_color=TextColor.GREEN)

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_folder(selection):

    for item in selection:
        if 'FilesFolder' in str(item):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_mediahub_files_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Delete Selected Folders',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_folder,
                    'execute': delete_folders,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
