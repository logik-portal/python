"""
Script Name: Append Start Frame to Name
Script Version: 1.0
Flame Version: 2023.1
Written by: Bryan Bayley
Help from: Michael Vaglienty
Creation Date: 10.12.22

Description:
Get the Source Start Frame of the first segment in the clip and append it to
the end of the clip name, zero-padded to 8 digits. Useful in a color grading workflow
when exporting multiple clips with the same name to prevent files overwriting each other.

Menus:
Right-click a clip in the Media Panel -> Rename... -> Append Start Frame to Name
"""

import flame


def startframe_to_name(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            source_frame = str(item.start_time.get_value().frame).zfill(8)
            seq_name = str(item.name)[1:-1]
            item.name = seq_name + "_" + source_frame


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Rename...",
            "actions": [
                {
                    "name": "Append Start Frame to Name",
                    "isVisible": scope_clip,
                    "execute": startframe_to_name,
                    "minimumVersion": "2020"
                }
            ]
        }
    ]
