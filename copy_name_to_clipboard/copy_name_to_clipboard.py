"""
Script Name: Copy Name to Clipboard
Written by: Kieran Hanrahan

Script Version: 3.2.0
Flame Version: 2025

URL: http://www.github.com/khanrahan/copy-name-to-clipboard

Creation Date: 10.12.23
Update Date: 11.19.25

Description:

    Copy names of selected items to clipboard.

Menus:

    Right-click selected items on the Desktop -> Copy... -> Name to Clipboard
    Right-click selected items in the Media Hub -> Copy... -> Name to Clipboard
    Right-click selected items in the Media Panel -> Copy... -> Name to Clipboard
    Right-click selected items in the Timeline -> Copy... -> Name to Clipboard

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

TITLE = 'Copy Name to Clipboard'
VERSION_INFO = (3, 2, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'
MEDIAHUB_OBJECTS = (
        flame.PyMediaHubFilesEntry,
        flame.PyMediaHubFilesFolder,
)

MEDIA_PANEL_OBJECTS = (
        flame.PyClip,
        flame.PySequence,
        flame.PyDesktop,
        flame.PyFolder,
        flame.PyLibrary,
        flame.PyReel,
        flame.PyReelGroup,
        flame.PyWorkspace,
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


def startup():
    """Messages to print at start of script run."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')


def plural_s(item):
    """Examine an item's length and return an 's' if necessary.

    Used to add a trailing s to a name in an fstring if it should be plural.  Zero or
    multiple will return a trailing s.

    https://stackoverflow.com/questions/21872366/plural-string-formatting
    """
    return f'{"s"[:len(item) ^ 1]}'


def copy_names_mediahub(selection):
    """The main function for MediaHub selections."""
    startup()

    results = []

    for item in selection:
        name = os.path.basename(os.path.normpath(item.path))
        if name not in results:
            results.append(name)

    copy_to_clipboard('\n'.join(results))
    message(f'Sent {len(results)} name{plural_s(results)} to the clipboard.')
    message('Done!')


def copy_names_media_panel(selection):
    """The main function for Media Panel selections."""
    startup()

    results = []

    for item in selection:
        name = item.name.get_value()
        if name not in results:
            results.append(name)

    copy_to_clipboard('\n'.join(results))
    message(f'Sent {len(results)} name{plural_s(results)} to the clipboard.')
    message('Done!')


def copy_names_timeline(selection):
    """The main function for Timeline selections."""
    startup()

    results = []

    for item in selection:
        if not isinstance(item, flame.PyTransition):
            name = item.name.get_value()
            if name not in results:
                results.append(name)

    copy_to_clipboard('\n'.join(results))
    message(f'Sent {len(results)} name{plural_s(results)} to the clipboard.')
    message('Done!')


def scope_selection(selection, objects):
    """Test if the selection only contains the specified objects."""
    return all(isinstance(item, objects) for item in selection)


def scope_mediahub_objects(selection):
    """Filter out only supported MediaHub exobjects."""
    return scope_selection(selection, MEDIAHUB_OBJECTS)


def scope_media_panel_objects(selection):
    """Filter out only supported Media Panel objects."""
    return scope_selection(selection, MEDIA_PANEL_OBJECTS)


def scope_timeline_objects(selection):
    """Filter out only supported Timeline objects.

    PyTransitions are included to allow artists to range select segments using shift +
    click.  Shift + click selections will include PyTransitions.  This is more
    convenient than ctrl + click multiple selections to exclude PyTransitions.
    """
    return scope_selection(selection, TIMELINE_OBJECTS)


def get_mediahub_files_custom_ui_actions():
    """Python hook to add custom right click menu item to MediaHub."""
    menu_name = 'Copy...'
    action = {
        'name': 'Name to Clipboard',
        'isVisible': scope_mediahub_objects,
        'execute': copy_names_mediahub,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu item to Media Panel or Desktop."""
    menu_name = 'Copy...'
    action = {
        'name': 'Name to Clipboard',
        'isVisible': scope_media_panel_objects,
        'execute': copy_names_media_panel,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]


def get_timeline_custom_ui_actions():
    """Python hook to add custom right click menu item to Timeline."""
    menu_name = 'Copy...'
    action = {
        'name': 'Name to Clipboard',
        'isVisible': scope_timeline_objects,
        'execute': copy_names_timeline,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]
