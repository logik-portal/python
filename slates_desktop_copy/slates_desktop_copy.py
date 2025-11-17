'''
Script Name: slate_desktop_copy
Script Version: 1.5
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 02.01.21
Update Date: 01.15.24

Description: If you put your slates on one reel and your sequences on another reel, this script allows you to select your Reel Group and Reels
to automatically insert your Slates to the corresponding Sequence.

* Every Sequences needs a corresponding Slate and order is important. Slate 1 will go to Sequence 1, 2->2, 3->3...
* Assumes your sequences start a 01:00:00:00.
* It also automatically renames your sequences based on the slate names.

Updates:
01.15.24 - v1.5 - Remove Error Message in Favor of the checking the amount of objects.
12.13.23 - v1.4 - Updated for pyflame lib v2 and for Flame 2025.
11.30.22 - v1.3 - Fixed a few issues with currentText and clip/sequence vs children issue.
04.19.22 - v1.2 - Updated for 2023 UI
'''
import flame
from pyflame_lib_slates_desktop_copy import *

try:
    from PySide6 import QtWidgets, QtCore
except ImportError:
    from PySide2 import QtWidgets, QtCore

folder_name = "UC Slates"
SCRIPT_NAME = "UC Slater"
SCRIPT_VERSION = '1.5'

def getReelGroupList():
    global rgList
    rgList = []
    for reel_group in reel_groups:
        rgName = str(reel_group.name)[1:-1]
        rgList.append(rgName)


def getReelGroupNumber():
    global selected_reel_group_num
    for i in [i for i, x in enumerate(rgList) if x == selected_reel_group_name]:
        selected_reel_group_num = int(i)

def getReelList():
    global reelList, last_menu_item
    reelList = []
    for reel in reels:
        reelName = str(reel.name)[1:-1]
        reelList.append(reelName)
    last_menu_item = int(len(reelList)-1)

def updateReelList():

    reel_group_text = reel_group_list_push_button.text()

    for i in [i for i, x in enumerate(rgList) if x == reel_group_text]:
        selected_reel_group_num = int(i)

    reels = dsk.reel_groups[selected_reel_group_num].reels
    global reelList
    reelList = []
    for reel in reels:
        reelName = str(reel.name)[1:-1]
        reelList.append(reelName)

    last_menu_item = int(len(reelList)-1)

    # Update slate and sequence push buttons
    slate_reel_list_push_button.update_menu(text=str(reelList[0]), menu_options=reelList)
    sequence_reel_list_push_button.update_menu(text=str(reelList[last_menu_item]), menu_options=reelList)

def main_window(selection):
    global wks, dsk,selected_reel_group_num, reels, reel_groups
    wks = flame.project.current_project.current_workspace
    dsk = flame.project.current_project.current_workspace.desktop
    selected_reel_group_num = 0
    reels = dsk.reel_groups[selected_reel_group_num].reels
    reel_groups = dsk.reel_groups

    getReelGroupList()
    getReelList()

    def ok_button():

        # Get selected Reel Group
        selected_reel_group_name = str(reel_group_list_push_button.text())

        # Get selected library number
        for i in [i for i, x in enumerate(rgList) if x == selected_reel_group_name]:
            selected_reel_group_num = int(i)

        # Get selected Slate Reel
        selected_slate_reel_name = str(slate_reel_list_push_button.text())

        for i in [i for i, x in enumerate(reelList) if x == selected_slate_reel_name]:
            selected_slate_reel_num = i

        # Get selected Sequence Reel
        selected_seq_reel_name = str(sequence_reel_list_push_button.text())

        # Get selected library number
        for i in [i for i, x in enumerate(reelList) if x == selected_seq_reel_name]:
            selected_seq_reel_num = int(i)

        # Check the amount of objects...
        clips = dsk.reel_groups[selected_reel_group_num].reels[selected_seq_reel_num].children
        slates = dsk.reel_groups[selected_reel_group_num].reels[selected_slate_reel_num].children
        if len(clips) ==len(slates):
            status = -1
            for item in clips:

                status += 1

                item.in_mark = None
                item.out_mark = None
                frameRate = item.frame_rate
                tc_OUT = flame.PyTime("00:59:58:00", frameRate)
                item.out_mark = tc_OUT
                item.open()

                slate = dsk.reel_groups[selected_reel_group_num].reels[selected_slate_reel_num].children[status]
                slateName = slate.name
                tc_IN = flame.PyTime(1)
                slate.in_mark = tc_IN

                slate.selected = True
                flame.execute_shortcut("Overwrite Edit")
                item.name = str(slateName)[1:-1]
                item.current_time = tc_IN
        
        else:
            PyFlameMessageWindow(title='Object Mismatch', message='Selected Reels must have the same amount of Slates and the same amount of Sequences.', type=MessageType.ERROR )
            return
        
        # Delete the Slates when finished
        slates = dsk.reel_groups[selected_reel_group_num].reels[selected_slate_reel_num].children
        for item in slates:
            flame.delete(item)

        window.close()

    window = PyFlameWindow(
            width=380,
            height=220,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}'
            )
    # Labels

    select_reel_group_label = PyFlameLabel(text='Select Reel Group', style=Style.UNDERLINE) # FlameLabel('Select Reel Group', label_type='underline')
    select_slate_reel_label = PyFlameLabel(text='Select Slates Reel', style=Style.UNDERLINE) # FlameLabel('Select Slates Reel', label_type='underline')
    select_sequence_reel_label = PyFlameLabel(text='Select Sequence Reel', style=Style.UNDERLINE) # FlameLabel('Select Sequence Reel', label_type='underline')

    # PushButtons
    global reel_group_list_push_button, slate_reel_list_push_button, sequence_reel_list_push_button

    reel_group_list_push_button = PyFlamePushButtonMenu(text=rgList[0], menu_options=rgList, align=Align.LEFT, connect=updateReelList)
    slate_reel_list_push_button = PyFlamePushButtonMenu(text=reelList[0], menu_options=reelList, align=Align.LEFT)
    sequence_reel_list_push_button = PyFlamePushButtonMenu(text=reelList[last_menu_item], menu_options=reelList, align=Align.LEFT)

    # Buttons
    ok_btn = PyFlameButton(text='Copy', connect=ok_button, color=Color.BLUE)
    cancel_btn = PyFlameButton(text='Close', connect=window.close)


    # Layout

    grid_layout = QtWidgets.QGridLayout()
    grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
    grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
    try:
        grid_layout.setMargin(pyflame.gui_resize(10))
    except:
        grid_layout_margin = pyflame.gui_resize(10)
        grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

    grid_layout.addWidget(select_reel_group_label, 0, 0)
    grid_layout.addWidget(reel_group_list_push_button, 0, 1)

    grid_layout.addWidget(select_slate_reel_label, 1, 0)
    grid_layout.addWidget(slate_reel_list_push_button, 1, 1)

    grid_layout.addWidget(select_sequence_reel_label, 2, 0)
    grid_layout.addWidget(sequence_reel_list_push_button, 2, 1)

    grid_layout.addWidget(cancel_btn, 3, 0)
    grid_layout.addWidget(ok_btn, 3, 1, QtCore.Qt.AlignRight)

    # Add layout to window
    window.add_layout(grid_layout)

    window.show()

    return window



def get_main_menu_custom_ui_actions():

    return [
        {
            'hierarchy': [],
            # 'name': folder_name,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'execute': main_window,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'execute': main_window,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]