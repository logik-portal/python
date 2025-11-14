'''
Script Name: renamer_ui
Script Version: 2.3
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 12.11.20
Update Date: 12.13.23

Description: Use this to add and/or remove a prefix and or suffix. It's a very quick way to add "_Generic" or "_v01" to the end of a name.

Updates:
12.13.23 - v2.3 Updated for pyflame lib v2
08.25.22 - v2.2 2023.2 Ordering
04.18.22 - v2.1 2023 UI Updates
'''

from pyflame_lib_renamer_ui import *

folder_name = "UC Renamers"
action_name = "Renamer UI"

SCRIPT_NAME = 'Renamer UI'
SCRIPT_VERSION = 'v2.3'

def renamer_window(selection):

    def rename_button():
        # Set variables from entries
        rmPrefix = int(remove_prefix_slider.text())
        prefix = str(new_prefix_entry.text())
        rmSuffix = int(remove_suffix_slider.text())
        suffix = str(new_suffix_entry.text())

        for item in selection:
                print ("*" * 10)
                seq_name = str(item.name)[(rmPrefix+1):-(rmSuffix+1)]
                item.name = prefix + seq_name + suffix
                print ("*" * 10)
                print ("\n")

        # Close window
        window.close()

    def update_preview():
        rmPrefix = int(remove_prefix_slider.text())
        prefix = str(new_prefix_entry.text())
        rmSuffix = int(remove_suffix_slider.text())
        suffix = str(new_suffix_entry.text())

        for item in selection:
            seq_name = str(item.name)[(rmPrefix+1):-(rmSuffix+1)]
            new_name = prefix + seq_name + suffix
            preview_bg_label.setText(new_name)
            break

    # Window and UI Below
    window = PyFlameWindow(
            width=750,
            height=320,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}'
            )

    # Labels
    remove_prefix_label = PyFlameLabel(text='Remove Prefix', style=Style.UNDERLINE)
    new_prefix_label = PyFlameLabel(text='New Prefix', style=Style.UNDERLINE)
    remove_suffix_label = PyFlameLabel(text='Remove Suffix', style=Style.UNDERLINE)
    new_suffix_label = PyFlameLabel(text='New Suffix', style=Style.UNDERLINE)
    preview_label = PyFlameLabel(text='Preview', style=Style.UNDERLINE)
    preview_bg_label = PyFlameLabel(text='', style=Style.BACKGROUND, width=550)
    blank_label = PyFlameLabel(text='', style=Style.NORMAL)

    # Sliders
    remove_prefix_slider = PyFlameSlider(0, 0, 100, False)
    remove_suffix_slider =  PyFlameSlider(0, 0, 100, False)

    # Slider updates
    remove_prefix_slider.textChanged.connect(update_preview)
    remove_suffix_slider.textChanged.connect(update_preview)

    # Entries / LineEdits
    new_prefix_entry = PyFlameLineEdit(text='',width=550,text_changed=update_preview)
    new_prefix_entry.setPlaceholderText('Enter text here to add to the start of a name.')

    new_suffix_entry = PyFlameLineEdit(text='',width=550,text_changed=update_preview)
    new_suffix_entry.setPlaceholderText('Enter text here to add to the end of a name, like "_Generic" or "_v01"')

    # Buttons
    rename_btn = PyFlameButton(text='Rename',  connect=rename_button,color=Color.BLUE)
    cancel_btn = PyFlameButton(text='Cancel',  connect=window.close)

    # Layout
    grid_layout = QtWidgets.QGridLayout()
    grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
    grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
    try:
        grid_layout.setMargin(pyflame.gui_resize(10))
    except:
        grid_layout_margin = pyflame.gui_resize(10)
        grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

    grid_layout.addWidget(remove_prefix_label, 0, 0)
    grid_layout.addWidget(remove_prefix_slider, 0, 1)

    grid_layout.setColumnMinimumWidth(1, 450)

    grid_layout.addWidget(new_prefix_label, 1, 0)
    grid_layout.addWidget(new_prefix_entry, 1, 1)

    grid_layout.addWidget(remove_suffix_label, 2, 0)
    grid_layout.addWidget(remove_suffix_slider, 2, 1)

    grid_layout.addWidget(new_suffix_label, 3, 0)
    grid_layout.addWidget(new_suffix_entry, 3, 1)

    grid_layout.addWidget(preview_label, 4, 0)
    grid_layout.addWidget(preview_bg_label, 4, 1)

    grid_layout.addWidget(blank_label, 5, 0)

    grid_layout.addWidget(cancel_btn, 6, 0)
    grid_layout.addWidget(rename_btn, 6, 1, QtCore.Qt.AlignRight)
    # Add layout to window
    window.add_layout(grid_layout)

    update_preview()

    window.show()

    return window

def scope_clip(selection):
    import flame
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def scope_not_desktop(selection):
    import flame

    for item in selection:
        if not isinstance(item, flame.PyDesktop):
            return True
    return False

def get_media_panel_custom_ui_actions():
    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'order': 7,
                    'isVisible': scope_not_desktop,
                    'execute': renamer_window,
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
                        'execute': renamer_window,
                        'minimumVersion': '2023.2'
                    }
                ]
            }
        ]
