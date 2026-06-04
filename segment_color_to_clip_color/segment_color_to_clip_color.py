"""
Script Name: Segment Color to Clip Color
Script Version: 1.0
Flame Version: 2024.1
Written by: Bryan Bayley
Help from: Fred Warren
Creation Date: 08.01.24

Description:
This is a simple script that takes the color (color label) of the first segment
in a clip, and applies that color at the clip level.

This is useful in my color grading workflow where we have a timeline and source
clips. I will apply color labels to segments in the timeline and those get synced
to the sources but only at the segment level. This script automates the color
labels at the clip level so it's easier to see that sources are in fact connected
to the segments in the sequences.

Menus:
Right-click a clip in the Media Panel -> Sequence... -> Copy Segment Color to Clip Color
"""

import flame


def segment_color_to_clip_color(selection):
    for clip in selection:
        if isinstance(clip, flame.PyClip):
            segment_color = clip.versions[0].tracks[0].segments[0].colour
            clip.colour = segment_color


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Sequence...",
            "actions": [
                {
                    "name": "Copy Segment Color to Clip Color",
                    "isVisible": scope_clip,
                    "execute": segment_color_to_clip_color,
                    "minimumVersion": "2024"
                }
            ]
        }
    ]
