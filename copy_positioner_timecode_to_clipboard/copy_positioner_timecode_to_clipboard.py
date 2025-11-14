"""
Script Name: Copy Positioner Timecode to Clipboard
Written By: Kieran Hanrahan

Script Version: 2.0.0
Flame Version: 2025

URL: http://www.github.com/khanrahan/copy-positioner-timecode-to-clipboard

Creation Date: 02.25.24
Update Date: 04.17.24

Description:

    Copy positioner timecode of selected timelines to the clipboard.

Menus:

    Right-click selected items on the Desktop -> Copy... -> Positioner Timecode to Clipboard

    Right-click selected items in the Media Hub -> Copy... -> Positioner Timecode to Clipboard

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""

import flame
from PySide6 import QtWidgets

TITLE = 'Copy Positioner Timecode to Clipboard'
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


def process_selection(selection):
    """Loop through all the timelines while assembling the results."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    results = []

    for timeline in selection:
        tc = timeline.current_time.get_value()
        results.append(tc.timecode)

    copy_to_clipboard('\n'.join(results))
    message('Done!')


def scope_timeline(selection):
    """Filter for only PyClips or PySequence."""
    valid_objects = (flame.PyClip, flame.PySequence)

    return all(isinstance(item, valid_objects) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add menu item to Media Hub right click menu."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Positioner Timecode to Clipboard',
                          'isVisible': scope_timeline,
                          'execute': process_selection,
                          'minimumVersion': '2025'}]
            }]
