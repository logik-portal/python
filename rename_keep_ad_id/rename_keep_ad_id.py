"""
Script Name: Rename Keep AD-ID
Script Version: 1.0
Flame Version: 2020
Written by: Bryan Bayley
Creation Date: 08.12.21

Description:
Truncate clip names in the Media Panel to 9 characters (Older ISCI ID format), 12
characters (AD-ID format), or remove the last 22 characters (to strip suffixes
added by Premiere XML fixer tools).

This is useful if your flame sequences are named with the ID + title, 
descriptions, etc. and you need to export files with just the ID for the filename.

Menus:
Right-click a clip in the Media Panel -> Rename... -> Keep 9 (ISCI ID)
Right-click a clip in the Media Panel -> Rename... -> Keep 12 (AD-ID)
Right-click a clip in the Media Panel -> Rename... -> Remove Premiere XML Suffix
"""

import flame


def keep_9(selection):
    for item in selection:
        item.name = str(item.name)[1:-1][:9]


def keep_12(selection):
    for item in selection:
        item.name = str(item.name)[1:-1][:12]


def remove_22(selection):
    for item in selection:
        item.name = str(item.name)[1:-1][:-22]


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
                    "name": "Keep 9 (ISCI ID)",
                    "isVisible": scope_clip,
                    "execute": keep_9,
                    "minimumVersion": "2020"
                },
                {
                    "name": "Keep 12 (AD-ID)",
                    "isVisible": scope_clip,
                    "execute": keep_12,
                    "minimumVersion": "2020"
                },
                {
                    "name": "Remove Premiere XML Suffix",
                    "isVisible": scope_clip,
                    "execute": remove_22,
                    "minimumVersion": "2020"
                }
            ]
        }
    ]
