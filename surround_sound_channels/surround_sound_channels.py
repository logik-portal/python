"""
Script Name: surround sound channels
Script Version: 1.2
Flame Version: 2020
Written by: John Geehreng
Creation Date: 06.06.20
Updated Date: 11.22.24
Custom Action Type: Media Panel

Usage: Right click a selection of clips or sequences and look for UC Audio -> Mute Surround Channels or UnMute Surround Channels

Description: This will mute or unmute audio tracks 1-5 on all selected clips/sequences.

Updates:
11.22.24 - v1.2 - simplified dumb old code
"""
import flame

folder_name = "UC Audio"
action_name = "Mute Surround Channels"

def mute_channels(selection):
    for item in selection:
        for atrack in item.audio_tracks[:6]:  # Slicing to get tracks 0-5
            atrack.mute = True

def unmute_channels(selection):
    for item in selection:
        for atrack in item.audio_tracks[:6]:  # Slicing to get tracks 0-5
            atrack.mute = False


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            # "order": 0,
            'actions': [
                {
                    'name': action_name,
                    "order": 0,
                    'isVisible': scope_clip,
                    'execute': mute_channels,
                    'minimumVersion': '2020'
                },
                {
                    'name': 'UnMute Surround Channels',
                    'isVisible': scope_clip,
                    "order": 1,
                    "separator": "below",
                    'execute': unmute_channels,
                    'minimumVersion': '2020'
                }
            ]
        }
    ]
