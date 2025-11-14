"""
Script Name: Fix Corrupt Actions
Script Version: 1.1
Flame Version: 2025
Written by: John Geehreng (adjusted by Finn Jaeger to only fix corrupted actions)
Creation Date: 12.11.24

Script Type: MediaPanel

Description:

    Fixes corrupt TLactions by exporting and then reloading the setups

Menu:

    Right-click on selected sequences in the Media Panel -> UC Timelines -> Fix Corrupt Actions

To install:

    Copy script folder into /opt/Autodesk/shared/python
"""

import flame
import os
import traceback

FOLDER_NAME = 'UC Timelines'
SCRIPT_NAME = 'Fix Corrupt Actions'
SCRIPT_VERSION = 'v1.1'

class FixCorruptActions():
    def __init__(self, selection) -> None:
        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        self.fix_corrupt_actions(selection)

    def catch_exception(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except:
                traceback.print_exc()
        return wrapper

    @catch_exception
    def fix_corrupt_actions(self, selection):
        project_name = flame.project.current_project.name

        # Setup temporary action path
        action_path = f"/opt/Autodesk/project/{project_name}/tmp/auto_action_temp.action"
        if not os.path.exists(os.path.dirname(action_path)):
            action_path = '/var/tmp/auto_action_temp.action'

        # Process all selected sequences
        for item in selection:
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        for tlfx in segment.effects:
                            if tlfx.type == 'Action':
                                print(f"Processing Action effect in {item.name}")
                                # Save the action setup
                                tlfx.save_setup(action_path)
                                # Delete and recreate action
                                flame.delete(tlfx)
                                action_fx = segment.create_effect('Action')
                                action_fx.load_setup(action_path)
                                segment.colour = (50, 50, 50)  # Mark as processed

        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')

def scope_sequence(selection):
    return any(isinstance(item, flame.PySequence) for item in selection)

def get_media_panel_custom_ui_actions():
    return [{
        'name': FOLDER_NAME,
        'actions': [{
            'name': SCRIPT_NAME,
            'execute': FixCorruptActions,
            'isVisible': scope_sequence,
            'minimumVersion': '2025'
        }]
    }]
