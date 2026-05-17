"""
Script Name: find and replace mediahub
Script Version: 1.0.0
Flame Version: 2026
Written by: John Geehreng
Creation Date: 06.07.22
Update Date: 10.06.25

Custom Action Type: Media Panel

Usage: Right click a selection of files and look for UC Renamers -> Find and Replace

Description: Find and Replaces characters in a bunch of clips or sequences.

To install: Copy script into /opt/Autodesk/shared/python/find_and_replace_mediahub or wherever you wish.

Updates:
10.06.25 - v1.0.0  Updated for Flame 2026 and pyflame lib v4.
12.13.23 - v0.3  Updated for pyflame lib v2. Start updates for Flame 2025.

"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os

import flame

from lib.pyflame_lib_find_and_replace_mediahub import *

#-------------------------------------
# [Constants]
#-------------------------------------

FOLDER_NAME = 'UC Renamers'
SCRIPT_NAME = 'Find and Replace MediaHub'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

#-------------------------------------
# [Main Script]
#-------------------------------------

class FindAndReplace():

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return
        
        # Define selection to be used later
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
                'find_setting': 'Some value',
                'replace_setting': 'Another value',
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
                    'find_setting': self.find_entry.text(),
                    'replace_setting': self.replace_entry.text(),
                    }
                )

            self.window.close()

            # PyFlameMessageWindow(
            #     message='A really cool message goes here.',
            #     )

        def rename():
            # print ("\n")
            for item in self.selection:
                file_path = item.path
                file_directory, file_name = os.path.split(file_path)
                file_path, file_extension = os.path.splitext(file_path)
                # print ("*" * 40)

                old_file_path = os.path.join(file_path + file_extension)
                # print ("File Path: ",old_file_path)

                find_me = str(self.find_entry.text())
                # print ('Find Me: ' + str(find_me))

                replace_with_me = str(self.replace_entry.text())
                # print ('Replace With Me: ' + str(replace_with_me))

                updated_file_name = file_name.replace(find_me,replace_with_me)
                # print ('New File Name: ' + str(updated_file_name))

                new_file_name = os.path.join(file_directory + "/" + updated_file_name)
                # print ("New File Path: ",new_file_name)
                os.rename(old_file_path, new_file_name)
            
            save_config()
            flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
            # print ("*" * 15, 'Find and Replace End', "*" * 15,"\n")

        #-------------------------------------
        # [Window Elements]
        #-------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=rename,
            grid_layout_columns=2,
            grid_layout_rows=3,
            grid_layout_adjust_column_widths={2: 50}
            )

        # Labels
        self.find_label = PyFlameLabel(
            text='Find',
            )
        self.replace_label = PyFlameLabel(
            text='Replace',
            )

        # Entries
        self.find_entry = PyFlameEntry(
            text=self.settings.find_setting,
            )
        self.replace_entry = PyFlameEntry(
            text=self.settings.replace_setting,
            )

        # Buttons
        self.save_button = PyFlameButton(
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

        self.window.grid_layout.addWidget(self.find_label, 0, 0)
        self.window.grid_layout.addWidget(self.find_entry, 0, 1)

        self.window.grid_layout.addWidget(self.replace_label, 1, 0)
        self.window.grid_layout.addWidget(self.replace_entry, 1, 1)

        self.window.grid_layout.addWidget(self.cancel_button, 2, 0)
        self.window.grid_layout.addWidget(self.save_button, 2, 1)

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
            'hierarchy': [],
            'actions': [
                    {
                        'name': 'Find And Replace',
                        'execute': FindAndReplace,
                        'isVisible': scope_file,
                        'minimumVersion': '2025'
                    }
            ]
        }
    ]
