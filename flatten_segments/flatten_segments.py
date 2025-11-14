"""
Script Name: Flatten Segments
Script Version: 2.1.0
Flame Version: 2025
Written By: Kieran Hanrahan
Creation Date: 01.12.24
Update Date: 03.07.25

Description:

    Takes vertically stacked segments and flattens them to just the top most segments.

    URL: http://github.com/khanrahan/flatten-segments

Menus:

    Right-click selected segments in a sequence --> Edit... --> Flatten Segments

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

from functools import partial

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Flatten Segments'
VERSION_INFO = (2, 1, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


class FlameButton(QtWidgets.QPushButton):
    """Custom Qt Flame Button Widget v2.1

    button_name: button text [str]
    connect: execute when clicked [function]
    button_color: (optional) normal, blue [str]
    button_width: (optional) default is 150 [int]
    button_max_width: (optional) default is 150 [int]

    Usage:

        button = FlameButton(
            'Button Name', do_something__when_pressed, button_color='blue')
    """

    def __init__(self, button_name, connect, button_color='normal', button_width=150,
                 button_max_width=150):
        super().__init__()

        self.setText(button_name)
        self.setMinimumSize(QtCore.QSize(button_width, 28))
        self.setMaximumSize(QtCore.QSize(button_max_width, 28))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(connect)
        if button_color == 'normal':
            self.setStyleSheet("""
                QPushButton {
                    color: rgb(154, 154, 154);
                    background-color: rgb(58, 58, 58);
                    border: none;
                    font: 14px "Discreet"}
                QPushButton:hover {
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:pressed {
                    color: rgb(159, 159, 159);
                    background-color: rgb(66, 66, 66);
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:disabled {
                    color: rgb(116, 116, 116);
                    background-color: rgb(58, 58, 58);
                    border: none}
                QToolTip {
                    color: rgb(170, 170, 170);
                    background-color: rgb(71, 71, 71);
                    border: 10px solid rgb(71, 71, 71)}""")
        elif button_color == 'blue':
            self.setStyleSheet("""
                QPushButton {
                    color: rgb(190, 190, 190);
                    background-color: rgb(0, 110, 175);
                    border: none;
                    font: 12px "Discreet"}
                QPushButton:hover {
                    border: 1px solid rgb(90, 90, 90)}
                QPushButton:pressed {
                    color: rgb(159, 159, 159);
                    border: 1px solid rgb(90, 90, 90)
                QPushButton:disabled {
                    color: rgb(116, 116, 116);
                    background-color: rgb(58, 58, 58);
                    border: none}
                QToolTip {
                    color: rgb(170, 170, 170);
                    background-color: rgb(71, 71, 71);
                    border: 10px solid rgb(71, 71, 71)}""")


class FlameLabel(QtWidgets.QLabel):
    """Custom Qt Flame Label Widget v2.1

    label_name:  text displayed [str]
    label_type:  (optional) select from different styles:
                 normal, underline, background. default is normal [str]
    label_width: (optional) default is 150 [int]

    Usage:

        label = FlameLabel('Label Name', 'normal', 300)
    """

    def __init__(self, label_name, label_type='normal', label_width=150):
        super().__init__()

        self.setText(label_name)
        self.setMinimumSize(label_width, 28)
        self.setMaximumHeight(28)
        self.setFocusPolicy(QtCore.Qt.NoFocus)

        # Set label stylesheet based on label_type

        if label_type == 'normal':
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    font: 14px "Discreet"}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'underline':
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    border-bottom: 1px inset rgb(40, 40, 40);
                    font: 14px "Discreet"}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'background':
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    font: 14px "Discreet"}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")


class FlamePushButtonMenu(QtWidgets.QPushButton):
    """Custom Qt Flame Menu Push Button Widget v3.1

    button_name: text displayed on button [str]
    menu_options: list of options show when button is pressed [list]
    menu_width: (optional) width of widget. default is 150. [int]
    max_menu_width: (optional) set maximum width of widget. default is 2000. [int]
    menu_action: (optional) execute when button is changed. [function]

    Usage:

        push_button_menu_options = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        menu_push_button = FlamePushButtonMenu(
            'push_button_name', push_button_menu_options)

        or

        push_button_menu_options = ['Item 1', 'Item 2', 'Item 3', 'Item 4']
        menu_push_button = FlamePushButtonMenu(
            push_button_menu_options[0], push_button_menu_options)

    Notes:
        Started as v2.1
        v3.1 adds a functionionality to set the width of the menu to be the same as the
        button.
    """

    def __init__(self, button_name, menu_options, menu_width=240, max_menu_width=2000,
                 menu_action=None):
        super().__init__()

        self.button_name = button_name
        self.menu_options = menu_options
        self.menu_action = menu_action

        self.setText(button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(menu_width)
        self.setMaximumWidth(max_menu_width)  # is max necessary?
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none;
                font: 14px "Discreet";
                padding-left: 9px;
                text-align: left}
            QPushButton:disabled {
                color: rgb(116, 116, 116);
                background-color: rgb(45, 55, 68);
                border: none}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")

        # Menu
        def match_width():
            """Match menu width to the parent push button width."""
            self.pushbutton_menu.setMinimumWidth(self.size().width())

        self.pushbutton_menu = QtWidgets.QMenu(self)
        self.pushbutton_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushbutton_menu.aboutToShow.connect(match_width)
        self.pushbutton_menu.setStyleSheet("""
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none;
                font: 14px "Discreet"}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.populate_menu(menu_options)
        self.setMenu(self.pushbutton_menu)

    def create_menu(self, option, menu_action):
        """Create it!"""
        self.setText(option)

        if menu_action:
            menu_action()

    def populate_menu(self, options):
        """Empty the menu then reassemble the options."""
        self.pushbutton_menu.clear()

        for option in options:
            self.pushbutton_menu.addAction(
                option, partial(self.create_menu, option, self.menu_action))


class FlattenSegments:
    """Flatten segments.

    Takes vertically stacked segments and flattens them to just the top most segment.
    """

    def __init__(self, selection):

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.selection = selection

        self.desktop = flame.project.current_project.current_workspace.desktop
        self.sequence = None
        self.sequence_current_time_initial = None
        self.reel_temp = None
        self.destination_version = None
        self.destination_track = None

        self.discard = False

        # Starting Dimensions
        self.window_x = 200
        self.window_y = 130

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def get_specific_parent(self, child, targets):
        """Ascend up the chain of parents until finding the target object.

        Args:
            child: Starting flame object.
            targets: Tuple.  same as isinstance takes.
        """
        parents = []

        while child:
            if isinstance(child, targets):
                break
            child = child.parent
            parents.append(child)

        return parents[-1]

    def get_parent_sequence(self, child):
        """A timeline seems possible to be PyClip or a PySequence."""
        return self.get_specific_parent(child, (flame.PyClip, flame.PySequence))

    def get_parent_track(self, flame_object):
        """Get parent PyTrack object."""
        return self.get_specific_parent(flame_object, (flame.PyTrack))

    def get_parent_version(self, flame_object):
        """Get parent PyVersion object."""
        return self.get_specific_parent(flame_object, (flame.PyVersion))

    def get_track_index(self, segment):
        """Get index of parent PyTrack."""
        track = self.get_parent_track(segment)
        version = self.get_parent_version(segment)
        return version.tracks.index(track)

    def get_version_index(self, segment):
        """Get index of parent PyVersion."""
        version = self.get_parent_version(segment)
        return self.sequence.versions.index(version)

    def deselect_selection(self):
        """Deselect everything so that lifting from the sequence may begin."""
        for item in self.selection:
            item.selected = False

    def sort_selection(self):
        """Sort selected PySegment objects.

        Put the selected segments in order from left to right, bottom to top.  This
        is necessary so segments on higher tracks overwrite the lower ones.
        """
        segment_version_track = []

        for segment in self.selection:
            if not isinstance(segment, flame.PySegment):  # skip PyTransitions
                continue
            if segment.type == 'Gap':
                continue
            segment_version_track.append(
                    (segment,
                     self.get_version_index(segment),
                     self.get_track_index(segment)))

        ordered_segments = sorted(segment_version_track, key=lambda x: (x[1], x[2]))
        self.selection = [obj for (obj, version, track) in ordered_segments]

    def create_temp_reel(self):
        """Create temporary reel.

        Create temporary reel on the desktop to contain the segments during
        flattening.
        """
        self.reel_temp = self.desktop.reel_groups[0].create_reel(
                'Flatten Segments TEMP')

    def delete_temp_reel(self):
        """Remove it when no longer needed."""
        flame.delete(self.reel_temp)

    def create_destination(self):
        """Create and store destination track & version in self.sequence."""
        self.destination_version = self.sequence.create_version()
        self.destination_track = self.destination_version.tracks[0]

    def flatten_segments(self):
        """Flatten the selection.

        This function only takes PySegments. All transitions and gaps should already
        be filtered out.  Copy each selected segment out and then overwrite edit to the
        destination track.  Working from the bottom up, the top most segments are what
        will remain at the end.
        """
        for segment in self.selection:
            segment.selected = True
            new_clip = self.sequence.copy_selection_to_media_panel(self.reel_temp)
            self.sequence.overwrite(new_clip, segment.record_in, self.destination_track)
            flame.execute_shortcut('Deselect')

    def discard_versions(self):
        """Delete version of the parent sequence that are not the destination track."""
        for version in self.sequence.versions:
            if version != self.destination_version:
                flame.delete(version, confirm=False)

    def deselect_entire_desktop(self):
        """Deselect entire desktop."""
        desktop_current = flame.project.current_project.current_workspace.desktop

        for reel_group in desktop_current.reel_groups:
            for reel in reel_group.reels:
                for child in reel.children:
                    child.selected = False

    def process_selection(self):
        """Where the work gets done!"""
        # Store Current Sequence & Current Time
        self.sequence = self.get_parent_sequence(self.selection[0])
        self.sequence_current_time_initial = self.sequence.current_time.get_value()

        # Prepare Selection
        self.deselect_selection()
        self.sort_selection()

        # Create Temporary Reel
        self.create_temp_reel()
        self.message('Created temporary reel.')

        # Create Destination Version
        self.create_destination()

        # FLatten
        self.flatten_segments()
        self.message('Segments flattened.')

        # Cleanup
        self.delete_temp_reel()
        self.message('Deleted temporary reel.')

        if self.discard:
            self.discard_versions()
            self.message('Discarded original segments.')

        flame.execute_shortcut('Close Current Sequence')

        # Restore Selection
        # Necessary to deselect the entire desktop because otherwise the selection moves
        # to the first clip in the first reel during delete_temp_reel()
        self.deselect_entire_desktop()
        self.sequence.selected = True

        # Restore Positioner Position/Time
        self.sequence.current_time = self.sequence_current_time_initial

        # Park Vertical Positioner on Destination Track
        self.sequence.primary_track = self.destination_track

    def main_window(self):
        """The only GUI."""

        def sources_btn_toggle():
            """Update discard attribute when toggled."""
            if self.btn_sources.text() == 'Keep':
                self.discard = False
            else:
                self.discard = True

        def okay_button():
            """Triggered when the Okay button at the bottom is pressed."""
            self.process_selection()
            self.message('Done!')
            self.window.close()

        def cancel_button():
            """Triggered when the Cancel button at the bottom is pressed."""
            self.message('Cancelled!')
            self.window.close()

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(self.window_x, self.window_y)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()

        self.window.move(
                (resolution.width() / 2) - (self.window_x / 2),
                (resolution.height() / 2) - (self.window_y / 2 + 44))

        # Labels
        self.label_sources = FlameLabel('Source Segments', 'normal')

        # Buttons
        self.btn_sources = FlamePushButtonMenu(
                'Keep', ['Keep', 'Discard'], menu_action=sources_btn_toggle)

        self.btn_ok = FlameButton(
            'Ok', okay_button, button_color='blue', button_width=110)
        self.btn_cancel = FlameButton('Cancel', cancel_button, button_width=110)

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setVerticalSpacing(10)
        self.grid.setHorizontalSpacing(10)
        self.grid.addWidget(self.label_sources, 0, 0)
        self.grid.addWidget(self.btn_sources, 0, 1)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.btn_cancel)
        self.hbox.addWidget(self.btn_ok)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.grid)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox)

        self.window.setLayout(self.vbox)
        self.window.show()

        return self.window


def scope_segment(selection):
    """Return bool for whether selection contains only valid objects.

    PyTransition is included because a shift + left click range selection of segments
    will include the transitions in between.  Otherwise, the artist will not be
    presented with the menu item.
    """
    valid_objects = (
            flame.PyClip,
            flame.PySegment,
            flame.PyTransition)

    return all(isinstance(item, valid_objects) for item in selection)


def get_timeline_custom_ui_actions():
    """Python hook to add custom right click menu inside timeline window."""
    return [{'name': 'Edit...',
             'actions': [{'name': 'Flatten Segments',
                          'isVisible': scope_segment,
                          'execute': FlattenSegments,
                          'minimumVersion': '2025'}]
           }]
