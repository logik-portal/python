"""
Script Name: Open PSD in Photoshop
Script Version: 1.0
Flame Version: 2024
Written by: Bryan Bayley
Creation Date: 07.13.23

Script Type: Timeline / Batch / Media Panel / MediaHub

Description:

    If a clip or timeline segment is a soft-imported PSD file >>> Open the source file in Photoshop.
    This script was written for macOS and Photoshop must be your default app for PSD files.

Menu:

    Timeline:
        Right-click on selected segments -> Open in Photoshop

    Media Panel:
        Right-click on selected clips -> Open in Photoshop

    Batch:
        Right-click on selected clips -> Open in Photoshop

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0 07.13.23
        - Initial release.
"""

import os, re, subprocess, flame

# valid_file_extension makes the context menu appear only if the item clicked is a PSD file.
# You can add more extensions here (jpg, png, etc.) but you must have Photoshop as the default
# app for those extensions. The script only knows how to open a file with it's default program.

def valid_file_extension(file_path):
    valid_extensions = ['.psd']
    _, file_extension = os.path.splitext(file_path)
    return file_extension.lower() in valid_extensions  # converts capitalized extension to lower for validity consideration

# Open in Photoshop #

def timeline_psd(selection):
    for item in selection:
        clip_path = item.file_path
        if clip_path and os.path.isfile(clip_path):
            subprocess.call(('open', clip_path))

def batch_psd(selection):
    for item in selection:
        if item.media_path is not None:
            clip_path = str(item.media_path)[1:-1]
            if clip_path and os.path.isfile(clip_path):
                subprocess.call(('open', clip_path))

def mediapanel_psd(selection):
    for item in selection:
        clip_path = item.versions[0].tracks[0].segments[0].file_path
        if clip_path and os.path.isfile(clip_path):
            subprocess.call(('open', clip_path))

def mediahub_psd(selection):
    for item in selection:
        clip_path = item.path
        if item.path is not None:
            subprocess.call(('open', clip_path))

# Scopes #

def scope_timeline_clip(selection):
    for item in selection:
        segment_path = item.file_path
        if isinstance(item, flame.PySegment):
            if item.file_path != '' and valid_file_extension(segment_path):
                return True
    return False

def scope_batch_clip(selection):
    for item in selection:
        batch_item_path = str(item.media_path).strip("''")
        if item.type == 'Clip':
            clip_path = str(item.media_path)[1:-1].rsplit('/', 1)[0]
            if clip_path != '' and valid_file_extension(batch_item_path):
                return True
    return False

def scope_clip(selection):
    for item in selection:
        clip_path = item.versions[0].tracks[0].segments[0].file_path
        if isinstance(item, flame.PyClip):
            if item.versions[0].tracks[0].segments[0].file_path != '' and valid_file_extension(clip_path):
                return True
    return False

def scope_file(selection):
    for item in selection:
        item_path = str(item.path)
        if valid_file_extension(item_path):
            return True
    return False

# Context Menus #

def get_timeline_custom_ui_actions():
    return [
        {
            'name': 'Open...',
            'actions': [
                {
                    'name': 'Open PSD in Photoshop',
                    'isVisible': scope_timeline_clip,
                    'execute': timeline_psd,
                    'minimumVersion': '2023'
                }
            ]
        }
    ]

def get_batch_custom_ui_actions():
    return [
        {
            'name': 'Open...',
            'actions': [
                {
                    'name': 'Open PSD in Photoshop',
                    'isVisible': scope_batch_clip,
                    'execute': batch_psd,
                    'minimumVersion': '2023'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():
    return [
        {
            'name': 'Open...',
            'actions': [
                {
                    'name': 'Open PSD in Photoshop',
                    'isVisible': scope_clip,
                    'execute': mediapanel_psd,
                    'minimumVersion': '2023'
                }
            ]
        }
    ]

def get_mediahub_files_custom_ui_actions():
    return [
        {
            'name': 'Open...',
            'actions': [
                {
                    'name': 'Open PSD in Photoshop',
                    'isVisible': scope_file,
                    'execute': mediahub_psd,
                    'minimumVersion': '2023'
                }
            ]
        }
    ]