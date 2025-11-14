"""
Script Name: Mute 6 Audio Tracks
Written By: Kieran Hanrahan

Script Version: 1.0.0
Flame Version: 2022

URL: http://github.com/khanrahan/mute-6-audio-tracks

Creation Date: 11.23.22
Update Date: 03.10.25

Description:

    Toggles audio tracks 1-6 between mute or not on the selected sequences.

Menus:

    Right-click selected clips and/or sequences on the Desktop Reels --> Mute... --> Toggle Audio Tracks 1-6

    Right-click selected clips and/or sequences in the Media Panel --> Mute... --> Toggle Audio Tracks 1-6

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import flame

TITLE = 'Mute 6 Audio Tracks'
VERSION_INFO = (1, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'

MESSAGE_PREFIX = '[PYTHON]'


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def mute_6_tracks(selection):
    """Loop through selection and mute the first 6 audio tracks."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    for sequence in selection:
        for x in range(6):
            try:
                mute = sequence.audio_tracks[x].mute.get_value()
                if not mute:
                    sequence.audio_tracks[x].mute.set_value(True)
                if mute:
                    sequence.audio_tracks[x].mute.set_value(False)
            except IndexError:
                pass

    message('Done!')


def scope_clip(selection):
    """Check for only PySequences selected."""
    return all(isinstance(item, flame.PySequence) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu."""
    return [{'name': 'Mute...',
             'actions': [{'name': 'Toggle Audio Tracks 1-6',
                          'isVisible': scope_clip,
                          'execute': mute_6_tracks,
                          'minimumVersion': '2022.0.0.0'}]
            }]
