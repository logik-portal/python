"""
Script Name: sequence renamer
Script Version: 2.1.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 06.08.22
Update Date: 02.28.26

Custom Action Type: MediaHub

Usage: Right click a selection of images or files and look for UC Renamers -> Sequence Renamer

Description: Renames files based on user input for start frame and padding.

To install: Copy script into /opt/Autodesk/shared/python/sequence_renamer or wherever you wish.

Updates:
02.28.26 - v2.1.0 - Updated for PyFlameLib v5.2.3. Added sequence mode to mediahub after renaming.
10.06.25 - v2.0.0  Updated for Flame 2025 and PyFlameLib v4.3.0.
12.13.23 - v0.2  Updated for pyflame lib v2. Start updates for Flame 2025.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import flame
from lib.pyflame_lib_sequence_renamer import *

#-------------------------------------
# [Constants]
#-------------------------------------

FOLDER_NAME = 'UC Renamers'
SCRIPT_NAME = 'Sequence Renamer'
SCRIPT_VERSION = 'v2.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class ScriptTemplate():

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return
        
        # define selection to be used later
        self.selection = selection

        # Create/Load config file settings.
        self.load_config()

        # Open main window
        self.main_window()

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads configuration values from the config file and applies them to `self.settings`.

        If the config file does not exist, it creates the file using the default values
        from the `config_values` dictionary. Otherwise, it loads the existing config values
        and applies them to `self.settings`.
        """

        self.settings = PyFlameConfig(
            config_values={
                'base_name': 'sequence renamer',
                'start_frame': 1001,
                'padding': 4,
                },
            )

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for script.
        """

        def save_config() -> None:
            """
            Save settings to config file and close window.
            """

            self.settings.save_config(
                config_values={
                    'base_name': self.base_name_entry.text,
                    'start_frame': self.start_frame_slider.value,
                    'padding': self.padding_slider.value,
                    }
                )

            self.window.close()

            # PyFlameMessageWindow(
            #     message='A really cool message goes here.',
            #     )
            
        def rename():

            print ('>' * 20, 'Sequence Renamer Start', '<' * 20)
            print ("\n"*1)

            print ("*" * 40)
            base_name = self.base_name_entry.text
            print ("base_name_entry: " + base_name)

            start_frame_entered = self.start_frame_slider.value
            print (f"start_frame_entered: {start_frame_entered}")

            padding_entered = self.padding_slider.value
            padding = str("'%0" + str(padding_entered) + "d'")
            print (f"padding: {padding}")
            count = start_frame_entered - 1

            print ("*" * 40)
            print ("\n"*1)

            for item in self.selection:
                # print ("*" * 40)
                count += int(1)
                count = padding % count
                count = str(count)[(1):-(1)]
                # print ("count: " + str(count))

                file_path = item.path
                file_directory, file_name = os.path.split(file_path)
                file_path, file_extension = os.path.splitext(file_path)

                old_file_path = os.path.join(file_path + file_extension)
                # print ("Old File Path: ",old_file_path)

                updated_file_name = f"{base_name}.{count}{file_extension}"
                # print ('New File Name: ' + str(updated_file_name))

                new_file_path = os.path.join(file_directory + "/" + updated_file_name)
                # print ("New File Path: ",new_file_path)
                os.rename(old_file_path, new_file_path)
                count = int(count)

            # Save settings to config file
            save_config()

            flame.mediahub.files.options.sequence_mode = True
            flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
            print ("*" * 40)
            print ('\n','>' * 20, 'Sequence Renamer End', '<' * 20, '\n')

        #-------------------------------------
        # [Window Elements]
        #-------------------------------------
        def cancel_window():
            self.window.close()

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=rename,
            escape_pressed=cancel_window,
            grid_layout_columns=3,
            grid_layout_rows=4,
            # grid_layout_adjust_column_widths={2: 80},
            parent=None
            )

        # Labels
        self.base_name_label = PyFlameLabel(
            text='Base Name',
            )
        self.sf_label = PyFlameLabel(
            text='Start Frame',
            )
        self.padding_label = PyFlameLabel(
            text='Padding',
            )
        
        # Entries
        self.base_name_entry = PyFlameEntry(text=self.settings.base_name)

        # Sliders
        self.start_frame_slider = PyFlameSlider(start_value=self.settings.start_frame, min_value=1, max_value=1000000)
        self.padding_slider = PyFlameSlider(start_value=self.settings.padding, min_value=1, max_value=10)

        # Buttons
        self.rename_button = PyFlameButton(
            text='Rename',
            connect=rename,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.base_name_label, 0, 0)
        self.window.grid_layout.addWidget(self.base_name_entry, 0, 1, 1, 2)

        self.window.grid_layout.addWidget(self.sf_label, 1, 0)
        self.window.grid_layout.addWidget(self.start_frame_slider, 1, 1, 1, 2)

        self.window.grid_layout.addWidget(self.padding_label, 2, 0)
        self.window.grid_layout.addWidget(self.padding_slider, 2, 1, 1, 2)

        self.window.grid_layout.addWidget(self.cancel_button, 3, 0)
        self.window.grid_layout.addWidget(self.rename_button, 3, 2)

#-------------------------------------
# [Scopes]
#-------------------------------------
def scope_file(selection):

    for item in selection:
        folder_path = item.path
        if os.path.isfile(folder_path):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': FOLDER_NAME,
            # 'order': 7,
            'hierarchy': [],
            'actions': [
                    {
                        'name': 'Sequence Renamer',
                        'execute': ScriptTemplate,
                        'isVisible': scope_file,
                        'minimumVersion': '2025'
                    }
            ]
        }
    ]
