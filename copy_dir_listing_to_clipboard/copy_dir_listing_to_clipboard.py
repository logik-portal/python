"""
Script Name: Copy Directory Listing to Clipboard
Written By: Kieran Hanrahan

Script Version: 2.0.0
Flame Version: 2025

URL: http://github.com/khanrahan/copy-dir-listing-to-clipboard

Creation Date: 11.01.22
Update Date: 03.06.25

Description:

    Takes the selected folders in the Media Hub, gets a listing of the directory,
    and copies the output to the clipboard.

Menus:

    Right-click a folder in the Media Hub Files --> Copy... --> Directory Listing (by Date) to Clipboard

    Right-click a folder in the Media Hub Files --> Copy... --> Directory Listing (by Name) to Clipboard

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import os

import flame
from PySide6 import QtWidgets

TITLE = 'Copy Directory List to Clipboard'
VERSION_INFO = (2, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def copy_to_clipboard(text):
    """Self explanitory.  Only takes a string."""
    qt_app_instance = QtWidgets.QApplication.instance()
    qt_app_instance.clipboard().setText(text)


def dir_listing(path):
    """Returns a list of a directory's files."""
    dir_list = [f for f in next(os.walk(path))[2] if f[0] != '.']
    return dir_list


def get_modification_time(folder_path, filename):
    """Return a file's last modification time."""
    return os.path.getmtime(os.path.join(folder_path, filename))


def gather_listings(selection, sort):
    """Directory listing sorted alphabetically and copy it to the clipboard."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    results = ''

    for folder in selection:
        if len(results) != 0:
            results += '\n'  # separate from previous listing by 1 line

        results += folder.path
        results += '\n'

        listing = dir_listing(folder.path)
        message(f'Added listing of {folder.path}')

        if sort == 'name':
            listing.sort(key=str.lower)
        if sort == 'date':
            listing.sort(key=lambda f, fp=folder.path: get_modification_time(fp, f))
        results += '\n'.join(listing)

    return results


def dir_listing_to_clipboard(selection):
    """Copy directory listing sorted by name to system clipboard."""
    results = gather_listings(selection, sort='name')
    copy_to_clipboard(results)
    message('Copied to clipboard!')
    message('Done!')


def dir_listing_by_date_to_clipboard(selection):
    """Copy directory listing sorted by date to the system clipboard."""
    results = gather_listings(selection, sort='date')
    copy_to_clipboard(results)
    message('Copied to clipboard!')
    message('Done!')


def scope_folders(selection):
    """Determine if selection is a folder in the Media Hub > Files tab."""
    return all(isinstance(item, flame.PyMediaHubFilesFolder) for item in selection)


def get_mediahub_files_custom_ui_actions():
    """Add right click menu items."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Directory Listing (by Date) to Clipboard',
                           'isVisible': scope_folders,
                           'execute': dir_listing_by_date_to_clipboard,
                           'minimumVersion': '2025',
                          },
                          {'name': 'Directory Listing (by Name) to Clipboard',
                           'isVisible': scope_folders,
                           'execute': dir_listing_to_clipboard,
                           'minimumVersion': '2025',
                           }]
           }]
