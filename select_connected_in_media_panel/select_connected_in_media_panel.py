"""
Script Name: Select Connected in Media Panel
Script Version: 1.0
Flame Version: 2026.2
Written by: Bryan Bayley
Based on Fred Warren's Script
Creation Date: 03.05.26

Description:
Adds a "Connected Segments..." context menu to the Timeline with three actions
that operate on the currently focused timeline segment:
- Select Connected Clips in Media Panel: finds all Media Panel clips that contain
  segments connected to the focused segment, expands their parent reels, and
  selects them.
- Select and Color Clips in Media Panel: same as above, and also colours each
  connected clip green for visual identification (useful when clips span multiple
  reels). Use "Uncolor Connected Clips" to clean up.
- Uncolor Connected Clips: removes the colour label from the connected clips.

Actions are only visible when the focused segment has 2 or more connected
segments. Does not support multi-segment selection; operates on the single
focused segment.

Menus:
Right-click a segment in the Timeline -> Connected Segments... -> Select Connected Clips in Media Panel
Right-click a segment in the Timeline -> Connected Segments... -> Select and Color Clips in Media Panel
Right-click a segment in the Timeline -> Connected Segments... -> Uncolor Connected Clips
"""

import flame


def scope_connected(selection):
    # Do not show the action if there is no focused segment.
    if flame.timeline.current_segment is None:
        return False
    # Show the action only if the focused segment has more than 1 connected segment.
    return len(flame.timeline.current_segment.connected_segments()) > 1


def select_connected_in_media_panel(selection):
    # The focused PySegment. The script does not work on multiple selection.
    item = flame.timeline.current_segment

    # Build the list of clips that contain a connected segment.
    clips = [seg.parent.parent.parent for seg in item.connected_segments()]

    # Expand the parent reel of each clip and select them in the Media Panel.
    if clips:
        for clip in clips:
            clip.parent.expanded = True
        flame.media_panel.selected_entries = clips


def select_and_color_connected_in_media_panel(selection):
    # The focused PySegment. The script does not work on multiple selection.
    item = flame.timeline.current_segment

    # Build the list of clips that contain a connected segment.
    clips = [seg.parent.parent.parent for seg in item.connected_segments()]

    # Expand the parent reel of each clip, select them, and colour them green.
    if clips:
        for clip in clips:
            clip.parent.expanded = True
        flame.media_panel.selected_entries = clips
        for clip in clips:
            clip.colour = (29, 67, 45)


def clear_color_connected_in_media_panel(selection):
    # The focused PySegment. The script does not work on multiple selection.
    item = flame.timeline.current_segment

    # Build the list of clips that contain a connected segment.
    clips = [seg.parent.parent.parent for seg in item.connected_segments()]

    # Clear the colour of the connected clips in the Media Panel.
    if clips:
        for clip in clips:
            clip.clear_colour()


def get_timeline_custom_ui_actions():
    return [
        {
            "name": "Connected Segments...",
            "actions": [
                {
                    "name": "Select Connected Clips in Media Panel",
                    "isVisible": scope_connected,
                    "execute": select_connected_in_media_panel,
                    "minimumVersion": "2023",
                },
                {
                    "name": "Select and Color Clips in Media Panel",
                    "isVisible": scope_connected,
                    "execute": select_and_color_connected_in_media_panel,
                    "minimumVersion": "2023",
                },
                {
                    "name": "Uncolor Connected Clips",
                    "isVisible": scope_connected,
                    "execute": clear_color_connected_in_media_panel,
                    "minimumVersion": "2023",
                }
            ]
        },
    ]
