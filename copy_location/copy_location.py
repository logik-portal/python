"""
Script Name: Copy Location
Written By: Kieran Hanrahan

Script Version: 3.0.0
Flame Version: 2025

URL: http://github.com/khanrahan/copy-location

Creation Date: 04.21.23
Update Date: 03.06.25

Description:

    Copy location of item inside of Flame (as opposed to the path in the file system).

Available for the following items:

    Batch Groups
    Batch Iterations
    Clips
    Desktops
    Folders
    Libraries
    Reels
    Reel Groups
    Sequences

Menus:

    Right-click selected items on the Desktop --> Copy... --> Location to Clipboard
    Right-click selected items in the Media Panel --> Copy... --> Location to Clipboard

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import socket

import flame
from PySide6 import QtWidgets

TITLE = 'Copy Location'
VERSION_INFO = (3, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'
SEPARATOR = ' > '


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def copy_to_clipboard(text):
    """Self explanitory.  Only takes a string."""
    qt_app_instance = QtWidgets.QApplication.instance()
    qt_app_instance.clipboard().setText(text)


def get_hostname():
    """Return hostname without the domain."""
    hostname = socket.gethostname().split('.')[0]

    return hostname


def find_parents(starting_item):
    """Returns a list of parent object names ascending from right to left."""
    current_item = starting_item
    parents = [current_item.name.get_value()]

    while current_item.parent:
        if isinstance(current_item.parent, flame.PyProject):
            parents.insert(0, current_item.parent.name)  # already a string
        else:
            parents.insert(0, current_item.parent.name.get_value())

        current_item = current_item.parent

    parents.insert(0, get_hostname())  # make hostname the root

    return parents


def copy_locations(selection):
    """The main function of this script."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    paths = []

    for item in selection:
        location_path = SEPARATOR.join(find_parents(item))
        message(location_path)
        paths.append(location_path)

    copy_to_clipboard('\n'.join(paths))

    message('Copied to clipboard!')
    message('Done!')


def scope_item(selection):
    """Test for matches."""
    valid_objects = (
            flame.PyBatch,
            flame.PyBatchIteration,
            flame.PyClip,
            flame.PyDesktop,
            flame.PyFolder,
            flame.PyReel,
            flame.PyReelGroup,
            flame.PyWorkspace)

    return all(isinstance(item, valid_objects) for item in selection)


def get_media_panel_custom_ui_actions():
    """Add right click menu item."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Location to Clipboard',
                          'isVisible': scope_item,
                          'execute': copy_locations,
                          'minimumVersion': '2025'}]
            }]
