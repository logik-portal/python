"""
Script Name: Copy Shot Name to Clipboard
Written by: Kieran Hanrahan

Script Version: 1.0.0
Flame Version: 2025

URL: http://www.github.com/khanrahan/copy-shot-name-to-clipboard

Creation Date: 04.08.25
Update Date: 04.08.25

Description:

    Copy shot names of selected items to clipboard.

Menus:

    Right-click selected items on the Desktop -> Copy... -> Shot Name to Clipboard
    Right-click selected items in the Media Panel -> Copy... -> Shot Name to Clipboard
    Right-click selected items in a Timeline -> Copy... -> Shot Name to Clipboard

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import flame
from PySide6 import QtWidgets

TITLE = 'Copy Shot Name to Clipboard'
VERSION_INFO = (1, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'
MEDIA_PANEL_OBJECTS = (
        flame.PyClip,
        flame.PySequence,
)

TIMELINE_OBJECTS = (
        flame.PyClip,
        flame.PySegment,
        flame.PyTransition,
)


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def copy_to_clipboard(text):
    """Self explanitory.  Only takes a string."""
    qt_app_instance = QtWidgets.QApplication.instance()
    qt_app_instance.clipboard().setText(text)


def startup_messages():
    """Messages to print at start of script run."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')


def get_shot_names_media_panel(selection):
    """Loop through the selected objects to get shot names metadata.

    Args:
        selection: A tuple of Flame API objects.

    Returns:
        A list of strings containing the shot names.
    """
    results = []
    for clip in selection:
        for version in clip.versions:
            for track in version.tracks:
                for segment in track.segments:
                    if segment.shot_name.get_value():
                        results.append(segment.shot_name.get_value())
    return results


def get_shot_names_timeline(selection):
    """Loop through the selected objects to get shot name metadata.

    It was necessary to include PyTransitions in the accepted objects because a multiple
    selection using shift key will include these.  An artist is going to expect to be
    able to do multiple selections this way as opposed to multiple selecting using ctrl
    to not have any transitions.  A shift selection is faster.  PyTransitions do not
    hold shot name metdata though, so just skip.

    Args:
        selection: A tuple of Flame API objects.

    Returns:
        A list of strings containing the shot names.
    """
    results = []
    for item in selection:
        if not isinstance(item, flame.PyTransition) and item.shot_name.get_value():
            results.append(item.shot_name.get_value())
    return results


def plural_s(item):
    """Examine an item's length and return an 's' if necessary.

    Used to add a trailing s to a name in an fstring if it should be plural.  Zero or
    multiple will return a trailing s.

    https://stackoverflow.com/questions/21872366/plural-string-formatting
    """
    return f'{"s"[:len(item) ^ 1]}'


def process_selection_media_panel(selection):
    """The main function for Media Panel selections."""
    startup_messages()
    shot_names = get_shot_names_media_panel(selection)
    copy_to_clipboard('\n'.join(shot_names))
    message(f'Sent {len(shot_names)} shot name{plural_s(shot_names)}' +
             ' to the clipboard.')
    message('Done!')


def process_selection_timeline(selection):
    """The main function for Timeline selections."""
    startup_messages()
    shot_names = get_shot_names_timeline(selection)
    copy_to_clipboard('\n'.join(shot_names))
    message(f'Sent {len(shot_names)} shot name{plural_s(shot_names)}' +
             ' to the clipboard.')
    message('Done!')


def scope_selection(selection, objects):
    """Test if the selection only contains the specified objects."""
    return all(isinstance(item, objects) for item in selection)


def scope_media_panel_object(selection):
    """Filter out only supported Media Panel objects."""
    return scope_selection(selection, MEDIA_PANEL_OBJECTS)


def scope_timeline_object(selection):
    """Filter out only supported Timeline objects."""
    return scope_selection(selection, TIMELINE_OBJECTS)


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu item to Media Panel or Desktop."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Shot Name to Clipboard',
                          'isVisible': scope_media_panel_object,
                          'execute': process_selection_media_panel,
                          'minimumVersion': '2025.0.0.0'}]
            }]


def get_timeline_custom_ui_actions():
    """Python hook to add custom right click menu item to Timeline."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Shot Name to Clipboard',
                          'isVisible': scope_timeline_object,
                          'execute': process_selection_timeline,
                          'minimumVersion': '2025.0.0.0'}]
           }]
