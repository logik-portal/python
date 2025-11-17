"""
Script Name: Remove Audio Gaps
Written By: Kieran Hanrahan

Script Version: 2.0.0
Flame Version: 2022

URL: http://github.com/khanrahan/remove-audio-gaps

Creation Date: 01.10.24
Update Date: 03.17.25

Description:

    Remove silent gaps on the audio tracks.

Menus:

    Right-click selected items on the Desktop --> Edit... --> Remove Audio Gaps
    Right-click selected items in the Media Panel --> Edit... --> Remove Audio Gaps

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import flame

TITLE = 'Remove Audio Gaps'
VERSION_INFO = (2, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def remove_audio_gaps(sequence):
    """Loop through all the audio tracks and remove any silent audio gaps."""
    for audio_track in sequence.audio_tracks:
        for track in audio_track.channels:
            for item in track.segments:
                if item.name == '':  # no name indicates audio gap
                    flame.delete(item)


def process_selection(selection):
    """Loop through selection of sequences."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    for sequence in selection:
        remove_audio_gaps(sequence)

    message('Done!')


def scope_sequence(selection):
    """Filter for only PySequence."""
    return all(isinstance(item, flame.PySequence) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu."""
    return [{'name': 'Edit...',
             'actions': [{'name': 'Remove Audio Gaps',
                          'isVisible': scope_sequence,
                          'execute': process_selection,
                          'minimumVersion': '2022.0.0.0'}]
            }]
