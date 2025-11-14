"""
Script Name: Toggle TimelineFX
Written By: Kieran Hanrahan

Script Version: 1.0.0
Flame Version: 2025

URL: http://github.com/khanrahan/toggle-timeline-fx

Creation Date: 10.17.25
Update Date:  10.17.25

Description:

    Toggle TimelineFX on selected sequences between On & Off.

Menus:

    Right-click selected items on the Desktop --> Edit... --> Toggle TimelineFX
    Right-click selected items in the Media Panel --> Edit... --> Toggle TimelineFX

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

TITLE = 'Toggle TimelineFX'
VERSION_INFO = (1, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'
FOLDER_NAME = 'Edit...'


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


class FlameFxRibbonLabel(QtWidgets.QLabel):
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
        self.setWordWrap(True)

        # Set label stylesheet based on label_type

        if label_type == 'normal':
            self.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignTop)
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    font: 10px "Discreet"}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")


class FlameFxRibbonPushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Push Button Widget

    This is the original Push Button Widget with just the StyleSheet from the most
    recent iteration on pyflame.com.
    """

    def __init__(self, name, checked, *args, **kwargs):
        """Create the FlameFxRibbonPushButton object."""
        super().__init__(*args, **kwargs)

        self.setText(name)
        self.setCheckable(True)
        self.setChecked(checked)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMinimumSize(37, 23)
        self.setMaximumSize(37, 23)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(58, 58, 58),
                    stop: .78 rgb(44, 54, 68));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(58, 58, 58),
                    stop: .78 rgb(44, 54, 68));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(58, 58, 58),
                    stop: .78 rgb(44, 54, 68));
                border-left: 1px solid rgb(58, 58, 58);
                border-right: 1px solid rgb(44, 54, 68);
                padding-left: 5px;
                font: 9px 'Discreet'
            }
            QPushButton:checked {
                color: rgb(217, 217, 217);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(71, 71, 71),
                    stop: .78 rgb(50, 101, 173));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(71, 71, 71),
                    stop: .78 rgb(50, 101, 173));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .77 rgb(71, 71, 71),
                    stop: .78 rgb(50, 101, 173));
                border-left: 1px solid rgb(71, 71, 71);
                border-right: 1px solid rgb(50, 101, 173);
                padding-left: 5px;
                font: italic
            }
            QPushButton:hover {border: 1px solid rgb(90, 90, 90)}'
            QPushButton:disabled {
                color: #6a6a6a;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(50, 50, 50));
                font: light;
                border: none
            }
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)
            }""")


class FlameFxRibbonItem(QtWidgets.QVBoxLayout):
    """Vertical Layout consisting of 1 button and 1 Effect/FX name.

    Matches the pairs shown in the Flame FX Ribbon.
    """

    def __init__(self, button_label, button_name):
        """Initialize a FlameFxRibbonItem."""
        super().__init__()
        self.button_label = button_label
        self.button_name = button_name
        self.button = FlameFxRibbonPushButton(
            self.button_label, False)
        self.label = FlameFxRibbonLabel(
            self.format_name(self.button_name), 'normal', 36)
        self.init_layout()

    @staticmethod
    def format_name(string):
        """Replace spaces with newlines to match appearance of real FX Ribbon."""
        return string.replace(' ', '\n')

    def init_layout(self):
        """Initialize the layout."""
        self.setSpacing(4)
        self.addWidget(self.button, alignment=QtCore.Qt.AlignHCenter)
        self.addWidget(self.label)

    @property
    def name(self):
        """Get or set the item's name."""
        return self.button_name

    @property
    def button_checked(self):
        """Get or set checked state of item's button."""
        return self.button.isChecked()


class FlameFxRibbon(QtWidgets.QGridLayout):
    """Layout to mimic the Flame FX Ribbon accessed by the FX button."""

    def __init__(self):
        """Create the FlameFxRibbon object."""
        super().__init__()
        self.init_layout()

    def init_layout(self):
        """Create the layout."""
        self.setVerticalSpacing(6)
        self.setHorizontalSpacing(8)

        # Row 1
        self.addItem(FlameFxRibbonItem('TR', '2D Transform'), 0, 0)
        self.addItem(FlameFxRibbonItem('BL', 'Blur'), 0, 1)
        self.addItem(FlameFxRibbonItem('BM', 'Burn-in Metadata'), 0, 2)
        self.addItem(FlameFxRibbonItem('CM', 'Color Mgmt'), 0, 3)
        self.addItem(FlameFxRibbonItem('FL', 'Flip'), 0, 4)
        self.addItem(FlameFxRibbonItem('GT', 'GMask Tracer'), 0, 5)
        self.addItem(FlameFxRibbonItem('IM', 'Image'), 0, 6)
        self.addItem(FlameFxRibbonItem('MX', 'Matchbox'), 0, 7)
        self.addItem(FlameFxRibbonItem('OFX', 'OpenFX'), 0, 8)
        self.addItem(FlameFxRibbonItem('RZ', 'Resize'), 0, 9)
        self.addItem(FlameFxRibbonItem('SUB', 'Subtitle'), 0, 10)
        self.addItem(FlameFxRibbonItem('TY', 'Type'), 0, 11)

        # Row 2
        self.addItem(FlameFxRibbonItem('AC', 'Action'), 1, 0)
        self.addItem(FlameFxRibbonItem('LB', 'Burn-in Letterbox'), 1, 1)
        self.addItem(FlameFxRibbonItem('CC', 'Color Correct'), 1, 2)
        self.addItem(FlameFxRibbonItem('CW', 'Color Warper'), 1, 3)
        self.addItem(FlameFxRibbonItem('GM', 'GMask'), 1, 4)
        self.addItem(FlameFxRibbonItem('HDR', 'HDR'), 1, 5)
        self.addItem(FlameFxRibbonItem('LK', 'Look'), 1, 6)
        self.addItem(FlameFxRibbonItem('MO', 'Morph'), 1, 7)
        self.addItem(FlameFxRibbonItem('PX', 'Pybox'), 1, 8)
        self.addItem(FlameFxRibbonItem('ST', 'Stereo Toolbox'), 1, 9)
        self.addItem(FlameFxRibbonItem('TW', 'Time Warp'), 1, 10)

    @property
    def checked(self):
        """Get the checked state of every button in the layout."""
        result = {}
        for index in range(self.count()):
            item = self.itemAt(index)
            result[item.name] = item.button_checked
        return result


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
        """Create FlamePushButtonMenu object."""
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
            QPushButton::menu-indicator {image: none}
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
                border: none; font: 14px "Discreet"}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.populate_menu(menu_options)
        self.setMenu(self.pushbutton_menu)

    def create_menu(self, option, menu_action):
        """Create menu."""
        self.setText(option)

        if menu_action:
            menu_action()

    def populate_menu(self, options):
        """Empty the menu then reassemble the options."""
        self.pushbutton_menu.clear()

        for option in options:
            self.pushbutton_menu.addAction(
                option, partial(self.create_menu, option, self.menu_action))


class MainWindow(QtWidgets.QWidget):
    """A view class for the main window."""
    signal_action = QtCore.Signal()
    signal_ok = QtCore.Signal()
    signal_cancel = QtCore.Signal()

    def __init__(self, parent_widget=None):
        """Initialize the instance."""
        super().__init__(parent=parent_widget)
        self.init_window()

    def init_window(self):
        """Create the pyside objects and layout the window."""
        self.setMinimumSize(700, 250)
        self.setStyleSheet('background-color: #272727')
        self.setWindowTitle(TITLE_VERSION)

        # Mac needs this to close the window
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Keeps on top of Flame but not other windows
        self.setWindowFlags(QtCore.Qt.Tool)

        # Labels
        self.label_action = FlameLabel('Action', 'normal')
        self.label_video = FlameLabel('Video Timeline FX', 'normal')

        # Buttons
        self.btn_action = FlamePushButtonMenu(
            '',
            [],
            menu_action=self.signal_action.emit,
            max_menu_width=250,
        )

        self.btn_ok = FlameButton('Ok', self.signal_ok.emit, button_color='blue')
        self.btn_cancel = FlameButton('Cancel', self.signal_cancel.emit)

        # Shortcuts
        self.shortcut_enter = QtGui.QShortcut(
            QtGui.QKeySequence('Enter'), self.btn_ok, self.signal_ok.emit)
        self.shortcut_escape = QtGui.QShortcut(
            QtGui.QKeySequence('Escape'), self.btn_cancel, self.signal_cancel.emit)
        self.shortcut_return = QtGui.QShortcut(
            QtGui.QKeySequence('Return'), self.btn_ok, self.signal_ok.emit)

        # Layout
        self.layout_timeline_fx = FlameFxRibbon()

        self.gridbox = QtWidgets.QGridLayout()
        self.gridbox.setVerticalSpacing(30)
        self.gridbox.setHorizontalSpacing(10)
        self.gridbox.addWidget(self.label_action, 0, 0)
        self.gridbox.addWidget(self.btn_action, 0, 1)
        self.gridbox.addWidget(self.label_video, 1, 0, QtCore.Qt.AlignTop)
        self.gridbox.addLayout(self.layout_timeline_fx, 1, 1)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.btn_cancel)
        self.hbox.addWidget(self.btn_ok)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.gridbox)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox)

        self.setLayout(self.vbox)
        self.center_window()

    def center_window(self):
        """Center the window on screen.

        Important to note this is centering the window BEFORE it is shown.  frameSize is
        based on setMinimumSize until the window is shown with show(), THEN it will
        reflect actual size.  Therefore, its important to have your setMinimumSize be
        very close to final size.
        """
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.move(
                (resolution.width() / 2) - (self.frameSize().width() / 2),
                (resolution.height() / 2) - (self.frameSize().height() / 2))

    @property
    def action(self):
        """Get or set the currently selected action name."""
        return self.btn_action.text()

    @action.setter
    def action(self, string):
        self.btn_action.setText(string)

    @property
    def actions(self):
        """Get or set a list of the available action names."""
        return [action.text() for action in self.btn_action.pushbutton_menu.actions()]

    @actions.setter
    def actions(self, actions):
        self.btn_action.populate_menu(actions)

    @property
    def fx_ribbon_checked(self):
        """Get a dict of every button in the FX ribbon and its checked state."""
        return self.layout_timeline_fx.checked


class ToggleTimelineFX:
    """Toggle between enabled & disabled for all TimelineFX on selection.

    Desktop & Media Panel supported objects:
        PySequence
        PyClip
    """

    def __init__(self, selection):
        """Create ToggleTimelineFX object with necessary starting values."""
        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.selection = selection
        self.actions = ['Disable All', 'Enable All']

        # Windows
        self.parent_window = self.get_flame_main_window()
        self.main_window = MainWindow(self.parent_window)
        self.main_window.actions = self.actions
        self.main_window.action = self.actions[0]
        self.main_window.signal_ok.connect(self.ok_button)
        self.main_window.signal_cancel.connect(self.cancel_button)
        self.main_window.show()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    @staticmethod
    def get_flame_main_window():
        """Return the Flame main window widget."""
        for widget in QtWidgets.QApplication.topLevelWidgets():
            if widget.objectName() == 'CF Main Window':
                return widget
        return None

    @staticmethod
    def refresh():
        """Refresh the flame UI.

        Necessary after changing attributes to have the changes show up on the
        Desktop.  Otherwise, the script runs, but the change will not be shown on the
        thumbnail until you tap on the UI.
        """
        flame.execute_shortcut('Refresh Thumbnails')

    def generate_timeline_fx(self):
        """Loop through the timelines and yield the Timeline FX objects."""
        return (effect
                for timeline in self.selection
                for version in timeline.versions
                for track in version.tracks
                for segment in track.segments
                if not segment.hidden.get_value()
                for effect in segment.effects
        )

    def process_selection(self):
        """Loop through the selection."""
        for effect in self.generate_timeline_fx():
            if self.main_window.fx_ribbon_checked[effect.type]:
                if self.main_window.action == self.main_window.actions[0]:
                    effect.bypass = True
                if self.main_window.action == self.main_window.actions[1]:
                    effect.bypass = False

    def ok_button(self):
        """Execute when Ok button is pressed."""
        self.main_window.close()
        self.process_selection()
        self.refresh()
        self.message('Done!')

    def cancel_button(self):
        """Execute when Cancel button is pressed."""
        self.main_window.close()
        self.message('Cancelled!')


def scope_selection_media_panel(selection):
    """Return bool for whether selection contains only valid objects."""
    valid_objects = (
            flame.PyClip,
            flame.PySequence,
    )

    return all(isinstance(item, valid_objects) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add item to the Desktop/Media Panel right click menu."""
    return [{'name': FOLDER_NAME,
             'actions': [{'name': TITLE,
                          'isVisible': scope_selection_media_panel,
                          'execute': ToggleTimelineFX,
                          'minimumVersion': '2025.0.0.0'}]
           }]
