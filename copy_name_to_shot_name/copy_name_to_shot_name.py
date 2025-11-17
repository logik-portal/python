"""
Script Name: Copy Segment Name to Shot Name
Written By: Kieran Hanrahan

Script Version: 1.0.1
Flame Version: 2022

URL: http://github.com/khanrahan/copy-name-to-shot-name

Creation Date: 07.21.22
Update Date: 03.06.24

Description:

    Simple script to copy segment name to shot name on all selected segments.

Menus:

    Right-click selected segments in a sequence -> Copy... -> Segment Name to Shot Name

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""


import flame

TITLE = 'Copy Name to Shot Name'
VERSION_INFO = (1, 0, 1)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'

MESSAGE_PREFIX = '[PYTHON]'


def message(string):
    """Print message to shell window and append global MESSAGE_PREFIX."""
    print(' '.join([MESSAGE_PREFIX, string]))


def copy_segment_name_to_shot_name(selection):
    """The main loop of this script."""
    message(TITLE_VERSION)
    message(f'Script called from {__file__}')

    for segment in selection:
        if isinstance(segment, flame.PySegment):
            segment.shot_name.set_value(segment.name.get_value())

    message('Done!')


def scope_timeline_clip(selection):
    """Filter for PySegments or PyTransitions.

    PyTransitions are included because typical box or shift + click selections will
    include them.
    """
    valid_objects = (
            flame.PySegment,
            flame.PyTransition)

    return all(isinstance(item, valid_objects) for item in selection)


def get_timeline_custom_ui_actions():
    """Add right click menu item."""
    return [{'name': 'Copy...',
             'actions': [{'name': 'Segment Name to Shot Name',
                          'isVisible': scope_timeline_clip,
                          'execute': copy_segment_name_to_shot_name,
                          'minimumVersion': '2022'}]
           }]
