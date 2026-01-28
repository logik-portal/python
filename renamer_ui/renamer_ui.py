'''
Script Name: renamer_ui
Script Version: 2.7.2
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 12.11.20
Update Date: 01.27.26
Description: Use this to add and/or remove a prefix and or suffix. It's a very quick way to add "_Generic" or "_v01" to the end of a name.

Updates:
01.27.26 - v2.7.2 - UI Update for pyflame lib v5.1.1
01.27.26 - v2.7.1 - Fixed issue with grid layout column widths
01.27.26 - v2.7.0 - UI Update for pyflame lib v4.3.1
09.19.24 - v2.6   -  Added Batch option. Minor cleanup.
08.27.24 - v2.5   - Turn off Scope so you can rename anything
03.04.24 - v2.4   - Use the return pressed option
12.13.23 - v2.3   - Updated for pyflame lib v2
08.25.22 - v2.2   - 2023.2 Ordering
04.18.22 - v2.1   - 2023 UI Updates
'''

import flame
from lib.pyflame_lib_renamer_ui import *

FOLDER_NAME = "UC Renamers"
SCRIPT_NAME = 'Renamer UI'
SCRIPT_VERSION = 'v2.7.2'

def renamer_window(selection):

    def rename_button():
        # Set variables from entries
        rmPrefix = remove_prefix_slider.value
        prefix = new_prefix_entry.text
        rmSuffix = remove_suffix_slider.value
        suffix = new_suffix_entry.text

        for item in selection:
                seq_name = str(item.name)[(rmPrefix+1):-(rmSuffix+1)]
                item.name = prefix + seq_name + suffix

        # Close window
        window.close()
    
    def update_preview():
        rmPrefix = remove_prefix_slider.value
        prefix = new_prefix_entry.text
        rmSuffix = remove_suffix_slider.value
        suffix = new_suffix_entry.text

        for item in selection:
            seq_name = str(item.name)[(rmPrefix+1):-(rmSuffix+1)]
            new_name = prefix + seq_name + suffix
            # preview_bg_label.setText(new_name)
            preview_bg_label.text = new_name
            break

    # Window and UI Below
    window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=rename_button,
            grid_layout_columns=2,
            grid_layout_rows=6,
            grid_layout_adjust_column_widths={1: 750, 0: 180},
            parent=None
            )
    
    # Labels
    remove_prefix_label = PyFlameLabel(text='Remove Prefix', style=Style.UNDERLINE)
    new_prefix_label = PyFlameLabel(text='New Prefix', style=Style.UNDERLINE)
    remove_suffix_label = PyFlameLabel(text='Remove Suffix', style=Style.UNDERLINE)
    new_suffix_label = PyFlameLabel(text='New Suffix', style=Style.UNDERLINE)
    preview_label = PyFlameLabel(text='Preview', style=Style.UNDERLINE)
    preview_bg_label = PyFlameLabel(text='', style=Style.BACKGROUND)
    
    # Sliders
    remove_prefix_slider = PyFlameSlider(start_value=0, min_value=0, max_value=100, rate=1, width=200)
    remove_suffix_slider =  PyFlameSlider(start_value=0, min_value=0, max_value=100, rate=1, width=200)

    # Slider updates
    remove_prefix_slider.textChanged.connect(update_preview)
    remove_suffix_slider.textChanged.connect(update_preview)

    # Entries / LineEdits
    new_prefix_entry = PyFlameEntry(text='',width=550,text_changed=update_preview, placeholder_text='Enter text here to add to the start of a name.')
    new_suffix_entry = PyFlameEntry(text='',width=550,text_changed=update_preview, placeholder_text='Enter text here to add to the end of a name, like "_Generic" or "_v01"')

    # Buttons
    rename_btn = PyFlameButton(text='Rename',  connect=rename_button, color=Color.BLUE, width=180)
    cancel_btn = PyFlameButton(text='Cancel',  connect=window.close)

    # Layout
    window.grid_layout.addWidget(remove_prefix_label, 0, 0)
    window.grid_layout.addWidget(remove_prefix_slider, 0, 1)

    window.grid_layout.addWidget(new_prefix_label, 1, 0)
    window.grid_layout.addWidget(new_prefix_entry, 1, 1)
    
    window.grid_layout.addWidget(remove_suffix_label, 2, 0)
    window.grid_layout.addWidget(remove_suffix_slider, 2, 1)
    
    window.grid_layout.addWidget(new_suffix_label, 3, 0)
    window.grid_layout.addWidget(new_suffix_entry, 3, 1)
    
    window.grid_layout.addWidget(preview_label, 4, 0)
    window.grid_layout.addWidget(preview_bg_label, 4, 1)
    
    window.grid_layout.addWidget(cancel_btn, 6, 0)
    window.grid_layout.addWidget(rename_btn, 6, 1, alignment=QtCore.Qt.AlignRight)

    update_preview()

    window.show()

####################################
# Scopes
def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def scope_not_desktop(selection):
    for item in selection:
        if not isinstance(item, flame.PyDesktop):
            return True
    return False

def scope_node(selection):
    for item in selection:
        if isinstance(item, flame.PyNode):
            return True
    return False

####################################
# Menus

def get_media_panel_custom_ui_actions():
    return [
        {
            'name': FOLDER_NAME,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'order': 7,
                    # 'isVisible': scope_not_desktop,
                    'execute': renamer_window,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_timeline_custom_ui_actions():
        return [
            {
                'name': FOLDER_NAME,
                'actions': [
                    {
                        'name': SCRIPT_NAME,
                        'execute': renamer_window,
                        'minimumVersion': '2023.2'
                    }
                ]
            }
        ]


def get_batch_custom_ui_actions():
    return [
        {
            'name': 'UC Batch',
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'execute': renamer_window,
                    'order': 13,
                    'separator': 'below',
                    'isVisible': scope_node,
                    'execute': renamer_window,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]