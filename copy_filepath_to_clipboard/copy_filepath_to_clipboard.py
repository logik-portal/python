"""
Script Name: Copy Filepath to Clipboard
Written by: Kieran Hanrahan

Script Version: 1.3.1
Flame Version: 2025

URL: http://github.com/khanrahan/copy-filepath-to-clipboard

Creation Date: 04.07.25
Update Date: 11.21.25

Description:

    Copy the filepaths of the selected items.

Menus:

    Right-click selected items on the Desktop > Copy... > Filepath to Clipboard
    Right-click selected items in the MediaHub > Copy... > Filepath to Clipboard
    Right-click selected items in the Media Panel > Copy... > Filepath to Clipboard
    Right-click selected items in the Timeline > Copy... > Filepath to Clipboard

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import os
import re

import flame
from PySide6 import QtWidgets

TITLE = 'Copy Filepath to Clipboard'
VERSION_INFO = (1, 3, 1)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'
IMAGE_SEQ_EXTS = (
        'dpx',
        'exr',
        'jpg',
        'png',
        'tif',
)

MEDIAHUB_OBJECTS = (
        flame.PyMediaHubFilesEntry,
        flame.PyMediaHubFilesFolder,
)

MEDIA_PANEL_OBJECTS = (
        flame.PyClip,
)

TIMELINE_OBJECTS = (
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


def test_image_seq(item, extensions):
    """Test if the item is a file sequence.

    Test if the object represents an image sequence by checking against valid file
    extensions and confirming the object is a frame range, not a single frame.

    Args:
        item: flame PyClip object
        extensions: tuple of str representing valid file extensions for image sequences.

    Returns:
        bool
    """
    return item.file_path.endswith(extensions) and item.source_in != item.source_out


def get_clip_location(segment):
    """Get what is considered the clip location for the given segment.

    You can see what is metadata for clip location by opening a sequence and viewing the
    segments in the Conform tab.

    Args:
        segment: a PySegment object

    Returns:
        A str in the format of '/path/path/path/file.[0001-0100].ext'
    """
    path, file = os.path.split(segment.file_path)
    file_and_frame, ext = os.path.splitext(file)
    frame = [part for part in re.split(r'(\d+)$', file_and_frame) if part][-1]
    file_and_sep = file_and_frame[0:(len(file_and_frame) - len(frame))]
    end_frame = segment.start_frame + segment.source_duration.frame - 1

    return f'{path}.{file_and_sep}[{segment.start_frame}-{end_frame}]{ext}'


def get_paths_mediahub(selection):
    """Loop through the selected clips and copy filepaths for each segment."""
    paths = []
    for item in selection:
        paths.append(item.path)
    return paths


def get_paths_media_panel(selection):
    """Loop through the selected clips and copy filepaths for each segment."""
    segments = (
        segment for clip in selection
        for version in clip.versions
        for track in version.tracks
        for segment in track.segments
    )
    paths = []

    for segment in segments:
        if test_image_seq(segment, IMAGE_SEQ_EXTS):
            paths.append(get_clip_location(segment))
        else:
            if segment.file_path:
                paths.append(segment.file_path)
    return paths


def get_paths_timeline(selection):
    """Loop through the selected clips and copy filepaths for each segment.

    Skip PyTransitions that might be included in the selection due to a range of
    segments selection performed using shift + click.

    Only add the path to results once and therefore return a list of unique paths.
    """
    segments = (item for item in selection if not isinstance(item, flame.PyTransition))
    paths = []
    for segment in segments:
        if (
            test_image_seq(segment, IMAGE_SEQ_EXTS) and
            get_clip_location(segment) not in paths
        ):
            paths.append(get_clip_location(segment))
        else:
            if segment.file_path and segment.file_path not in paths:
                paths.append(segment.file_path)
    return paths


def plural_s(item):
    """Examine an item's length and return an 's' if necessary.

    Used to add a trailing s to a name in an fstring if it should be plural.  Zero or
    multiple will return a trailing s.

    https://stackoverflow.com/questions/21872366/plural-string-formatting
    """
    return f'{"s"[:len(item) ^ 1]}'


def process_selection_mediahub(selection):
    """Process the selection."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')
    paths = get_paths_mediahub(selection)
    copy_to_clipboard('\n'.join(paths))
    message(f'Sent {len(paths)} filepath{plural_s(paths)} to the clipboard.')
    message('Done!')


def process_selection_media_panel(selection):
    """Process the selection."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')
    paths = get_paths_media_panel(selection)
    copy_to_clipboard('\n'.join(paths))
    message(f'Sent {len(paths)} filepath{plural_s(paths)} to the clipboard.')
    message('Done!')


def process_selection_timeline(selection):
    """Process the selection."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')
    paths = get_paths_timeline(selection)
    copy_to_clipboard('\n'.join(paths))
    message(f'Sent {len(paths)} filepath{plural_s(paths)} to the clipboard.')
    message('Done!')


def scope_selection(selection, objects):
    """Test if the selection only contains the specified objects."""
    return all(isinstance(item, objects) for item in selection)


def scope_mediahub_objects(selection):
    """Filter out only supported MediaHub exobjects."""
    return scope_selection(selection, MEDIAHUB_OBJECTS)


def scope_media_panel_objects(selection):
    """Filter for timeline objects."""
    return scope_selection(selection, MEDIA_PANEL_OBJECTS)


def scope_timeline_objects(selection):
    """Filter out only supported Timeline objects.

    PyTransitions are included to allow an artist to perform a selection of a range of
    segments using shift + click for convenience.  Otherwise, they would be forced to
    select multiple segments using ctrl + click which is less convenient.
    """
    return scope_selection(selection, TIMELINE_OBJECTS)


def get_mediahub_files_custom_ui_actions():
    """Python hook to add custom right click menu item to MediaHub."""
    menu_name = 'Copy...'
    action = {
        'name': 'Filepath to Clipboard',
        'isVisible': scope_mediahub_objects,
        'execute': process_selection_mediahub,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]


def get_media_panel_custom_ui_actions():
    """Python hook to add item to Media Panel or Desktop Reels right click menu."""
    menu_name = 'Copy...'
    action = {
        'name': 'Filepath to Clipboard',
        'isVisible': scope_media_panel_objects,
        'execute': process_selection_media_panel,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]


def get_timeline_custom_ui_actions():
    """Python hook to add custom right click menu item to Timeline."""
    menu_name = 'Copy...'
    action = {
        'name': 'Filepath to Clipboard',
        'isVisible': scope_timeline_objects,
        'execute': process_selection_timeline,
        'minimumVersion': '2025.0.0.0'
    }
    menu = {'name': menu_name, 'actions': [action]}
    return [menu]
