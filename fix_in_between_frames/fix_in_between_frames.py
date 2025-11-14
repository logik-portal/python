"""
Script Name: Fix In Between Frames
Script Version: 1.0.1
Flame Version: 2026.1
Written by: John Geehreng
Creation Date: 08.07.25
Update Date: 08.11.25

Script Type: Batch

Description:

    Adds a 2D stabilizer, then applies a timewarp to 'edit' out the problematic frames, followed by another timewarp to fix in between frames selected by the UI.

Menu:

    Batch -> Timewarp Tools -> Fix In Between Frames

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:
    v1.0.1 08.11.25
        - Changed Connection to 'Default' so it won't break when applying to a clip vs a node.

    v1.0.0 08.06.25
        - Initial Release
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import flame

from lib.pyflame_lib_fix_in_between_frames import *

#-------------------------------------
# [Constants]
#-------------------------------------

FOLDER_NAME = 'Timewarp Tools'
SCRIPT_NAME = 'Fix In Between Frames'
SCRIPT_VERSION = 'v1.0.1'

#-------------------------------------
# [Main Script]
#-------------------------------------

class FixInbetweenFrames():

    def __init__(self, selection) -> None:

        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')

        # Define selection to be used later
        self.selection = selection

        # Open main window
        self.main_window()

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for script.
        """
        # Get current frame, start frame, and last frame of the batch for the sliders.
        current_frame = int(str(flame.batch.current_frame))
        start_frame = int(str(flame.batch.start_frame))
        last_frame = int(str(flame.batch.start_frame)) + int(str(flame.batch.duration)) - 1

        def fix_in_betweens():
            print('Fix in between frames button Pressed!')
            last_good_frame = self.last_good_frame_slider.get_value()
            print(f'Last good frame: {last_good_frame}')
            first_good_frame = self.first_good_frame_slider.get_value()
            print(f'First good frame: {first_good_frame}')

            def get_unique_name(base_name):
                """Return a unique node name by appending a number if necessary."""
                existing_names = [node.name for node in flame.batch.nodes]
                if base_name not in existing_names:
                    return base_name

                i = 1
                while f"{base_name}_{i}" in existing_names:
                    i += 1
                return f"{base_name}_{i}"

            for item in self.selection:
                # Create a 2D Transform node if you need to stabilize the footage
                xform = flame.batch.create_node("2d Transform")
                xform.name = get_unique_name("stabilizer")
                xform.pos_x = item.pos_x + 200
                xform.pos_y = item.pos_y
                flame.batch.connect_nodes(item, "Default", xform, "Front")

                # Create a Timewarp node to remove the bad frames
                edit_tw = flame.batch.create_node("timewarp")
                edit_tw.name = get_unique_name("remove_bad_frames_tw")
                edit_tw.frame_interpolation_mode = 'Mix'
                edit_tw.mode = "Timing"
                edit_tw.set_timing(last_good_frame, last_good_frame)
                edit_tw.set_timing(last_good_frame + 1, first_good_frame)
                edit_tw.set_timing(last_good_frame + 2, first_good_frame + 1)
                edit_tw.pos_x = xform.pos_x + 200
                edit_tw.pos_y = xform.pos_y
                flame.batch.connect_nodes(xform, "Result", edit_tw, "Front")

                # Create a Timewarp node to morph the good frames back together
                tw = flame.batch.create_node("timewarp")
                tw.name = get_unique_name("fix_bad_frames_tw")
                tw.pos_x = 200
                tw.frame_interpolation_mode = 'ML(2026)'
                tw.mode = "Timing"
                tw.set_timing(last_good_frame, last_good_frame)
                tw.set_timing(first_good_frame, last_good_frame + 1)
                tw.set_timing(first_good_frame + 1, last_good_frame + 2)
                tw.pos_x = edit_tw.pos_x + 200
                tw.pos_y = edit_tw.pos_y
                flame.batch.connect_nodes(edit_tw, "Result", tw, "Front")

            print('\n[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')

            self.window.close()

        #-------------------------------------
        # [Window Elements]
        #-------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=fix_in_betweens,
            grid_layout_columns=2,
            grid_layout_rows=4,
            grid_layout_adjust_column_widths={2: 50}
            )

        # Labels
        self.label1 = PyFlameLabel(
            text='Last Good Frame',
            )
        self.label2 = PyFlameLabel(
            text='First Good Frame',
            )

        # Sliders
        self.last_good_frame_slider = PyFlameSlider(current_frame - 3,start_frame, last_frame, False, tooltip='Set the last good frame before the bad frames.')
        self.first_good_frame_slider = PyFlameSlider(current_frame, start_frame, last_frame, False, tooltip='Set the first good frame after the bad frames.')

        # Buttons
        self.save_button = PyFlameButton(
            text='Go',
            connect=fix_in_betweens,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.label1, 0, 0)
        self.window.grid_layout.addWidget(self.last_good_frame_slider, 0, 1)

        self.window.grid_layout.addWidget(self.label2, 1, 0)
        self.window.grid_layout.addWidget(self.first_good_frame_slider, 1, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 3, 0)
        self.window.grid_layout.addWidget(self.save_button, 3, 1)

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_one_thing_selected(selection):
    if len(selection) == 1:
        return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_batch_custom_ui_actions():

    return [
                {
            'name': FOLDER_NAME,
            # 'hierarchy': [FOLDER_NAME],
            # 'order': 2,
            'actions': [
               {
                    'name': SCRIPT_NAME,
                    'execute': FixInbetweenFrames,
                    'isVisible': scope_one_thing_selected,
                    'minimumVersion': '2026.1'
               }
           ]
        }
    ]
