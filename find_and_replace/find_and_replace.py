'''
Script Name: find and replace
Script Version: 1.7
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 10.01.21
Update Date: 02.27.24

Script Type: MediaPanel

Usage:

    Right click a selection of clips or sequences and look for UC Renamers -> Find and Replace

Description:

    Find and Replaces characters in a bunch of clips or sequences.

To install:

    Copy script into /opt/Autodesk/shared/python/find_and_replace

Updates:
    02.27.24 - v1.7 Updated Config Settings. Fixed error when empty fields are entered
    02.12.24 - v1.6 Added Preview Window
    12.12.23 - v1.5 Updated for pyflame lib v2
    01.25.23 - v1.4 Stopped window from automatically closing upon renaming. Renamed "Cancel" to "Close."
    08.25.22 - v1.3 2023.2 ordering
    04.19.22 - v1.2 2023 UI Updates
'''

import flame
# import xml.etree.ElementTree as ET
import os
from pyflame_lib_find_and_replace import *

folder_name ='UC Renamers'
SCRIPT_VERSION = 'v1.7'
SCRIPT_NAME = 'Find and Replace'
SCRIPT_PATH = '/opt/Autodesk/shared/python/find_and_replace'

#-------------------------------------#
# Main Script

class find_and_replace(object):

    def __init__(self, selection):


        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        # Check script path
        if os.path.dirname(os.path.abspath(__file__)) != SCRIPT_PATH:

            PyFlameMessageWindow(
                message='Script path is incorrect. Please reinstall script.<br><br>Script path should be:<br><br>/opt/Autodesk/shared/python/find_and_replace',
                title=SCRIPT_NAME,
                type=MessageType.ERROR
                )
            return


        # Load config file
        self.settings = PyFlameConfig(
            script_name=SCRIPT_NAME,
            script_path=SCRIPT_PATH,
            config_values={
                'find_setting': 'Master',
                'replace_setting': 'Generic'
                }
            )

        # Open main window

        self.main_window(selection)


    def main_window(self,selection):

        for item in selection:
                self.first_orig_name = str(item.name)[(1):-(1)]
                break

        def preview_new_name():

            # Update Path Preview Window

            for item in selection:
                orig_name = str(item.name)[(1):-(1)]
                # print ('Start Name: ' + str(orig_name))
                new_name = orig_name.replace(self.find_lineedit.text(),self.replace_lineedit.text())
                self.result_preview_label.setText(new_name)
                break

        def save_config():

            # Save settings to config file
            self.settings.save_config(
                script_name=SCRIPT_NAME,
                script_path=SCRIPT_PATH,
                config_values={
                    'find_setting': self.find_lineedit.text(),
                    'replace_setting': self.replace_lineedit.text()
                    }
                )

            # self.window.close()
            rename()

        def rename():

            for item in selection:
                print ("*" * 40)
                seq_name = str(item.name)[(1):-(1)]
                print ('Start Name: ' + str(seq_name))

                find_me = str(self.find_lineedit.text())
                print ('Find Me: ' + str(find_me))

                replace_with_me = str(self.replace_lineedit.text())
                print ('Replace With Me: ' + str(replace_with_me))

                new_name = seq_name.replace(find_me,replace_with_me)
                item.name = new_name
                print ('New Name: ' + str(new_name))

                print ("*" * 40)
                print ("\n")
            print ("*" * 15, 'Find and Replace End', "*" * 15,"\n")


        # Window and UI Below
        self.window = PyFlameWindow(
            width=840,
            height=280,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}'
            )

        line_edit_width = 620

        # Labels
        self.orig_name_label = PyFlameLabel(text='Original Name', style=Style.UNDERLINE)
        self.orig_name_preview_label = PyFlameLabel(text=self.first_orig_name, style=Style.BACKGROUND)
        self.find_label = PyFlameLabel(text='Find', style=Style.UNDERLINE)
        self.replace_label = PyFlameLabel(text='Replace', style=Style.UNDERLINE)
        self.blank_label = PyFlameLabel(text='', style=Style.NORMAL)
        self.preview_label = PyFlameLabel(text='Preview', style=Style.UNDERLINE)
        self.result_preview_label = PyFlameLabel(text='', style=Style.BACKGROUND, width=line_edit_width)

        # LineEdits
        self.find_lineedit = PyFlameLineEdit(text=self.settings.find_setting,
                            text_changed=preview_new_name,
                            width=line_edit_width)

        self.replace_lineedit = PyFlameLineEdit(text=self.settings.replace_setting,
                                text_changed=preview_new_name,
                                width=line_edit_width)

        # Buttons
        self.rename_btn = PyFlameButton(text='Rename',  connect=save_config,color=Color.BLUE)
        self.cancel_btn = PyFlameButton(text='Close',  connect=self.window.close)

        # Update the window
        preview_new_name()

        #------------------------------------#

        # Window Layout

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
        grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
        try:
            grid_layout.setMargin(pyflame.gui_resize(10))
        except:
            grid_layout_margin = pyflame.gui_resize(10)
            grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

        grid_layout.setColumnMinimumWidth(1, 500)

        grid_layout.addWidget(self.orig_name_label, 0, 0)
        grid_layout.addWidget(self.orig_name_preview_label, 0, 1)

        grid_layout.addWidget(self.find_label, 1, 0)
        grid_layout.addWidget(self.find_lineedit, 1, 1)
        grid_layout.addWidget(self.replace_label, 2, 0)
        grid_layout.addWidget(self.replace_lineedit, 2, 1)

        grid_layout.addWidget(self.preview_label, 3, 0)
        grid_layout.addWidget(self.result_preview_label, 3, 1)

        grid_layout.addWidget(self.blank_label, 4, 0)

        grid_layout.addWidget(self.cancel_btn, 5, 0)
        grid_layout.addWidget(self.rename_btn, 5, 1, QtCore.Qt.AlignRight)

        # ----------------------------------------------

        # Add layout to window
        self.window.add_layout(grid_layout)

        self.window.show()

        return self.window

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'order': 1,
                    'execute': find_and_replace,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_timeline_custom_ui_actions():
        return [
            {
                'name': folder_name,
                'actions': [
                    {
                        'name': SCRIPT_NAME,
                        'execute': find_and_replace,
                        'minimumVersion': '2023.2'
                    }
                ]
            }
        ]