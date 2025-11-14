"""
Script Name: Delete All Markers
Script Version: 1.0.0
Flame Version: 2022
Written by: Kieran Hanrahan
Creation Date: 10.04.25
Update Date: 10.04.25

Description:

    Delete all timeline or segment markers on the selected clips or sequences.

    URL: http://github.com/khanrahan/delete-all-markers

Menus:

    Right-click selected clips and/or sequences on the Desktop Reels --> Edit...
    --> Delete All Markers

    Right-click selected clips and/or sequences in the Media Panel --> Edit...
    --> Delete All Markers

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import flame

TITLE = 'Delete All Markers'
VERSION_INFO = (1, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def delete_sequence_markers(sequence):
    """Delete all timeline markers on the passed in sequence."""
    for marker in sequence.markers:
        flame.delete(marker)


def delete_segment_markers(sequence):
    """Delete all segment markers on the passed in sequence."""
    for version in sequence.versions:
        for track in version.tracks:
            for segment in track.segments:
                for segment_marker in segment.markers:
                    flame.delete(segment_marker)


def delete_all_markers(selection):
    """Loop through selection and mute the first 6 audio tracks."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    query = flame.messages.show_in_dialog(
            title='Delete All Timeline Markers',
            message='Are you sure you want to permanently delete all markers?',
            type='warning',
            buttons=['Ok'],
            cancel_button='Cancel',
    )

    if query == 'Ok':
        for sequence in selection:
            delete_sequence_markers(sequence)
            delete_segment_markers(sequence)
        message('Done!')
    if query == 'Cancel':
        message('Cancelled!')


def scope_clip(selection):
    """Check for only PySequences selected."""
    return all(isinstance(item, (flame.PyClip, flame.PySequence)) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu."""
    return [{'name': 'Edit...',
             'actions': [{'name': 'Delete All Markers',
                          'isVisible': scope_clip,
                          'execute': delete_all_markers,
                          'minimumVersion': '2022.0.0.0'}]
            }]
