"""
Script Name: Filter Selection
Written by: Kieran Hanrahan

Script Version: 2.1.1
Flame Version: 2025

URL: http://www.github.com/khanrahan/filter-selection

Creation Date: 03.07.25
Update Date: 04.10.25

Description:

    Filter the current selection in the Media Panel.

Menus:

    Right-click selected items on the Desktop -> Select... -> Filter Selection
    Right-click selected items in the Media Hub -> Select... -> Filter Selection
    Right-click selected items in the Media Panel -> Select... -> Filter Selection

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

from functools import partial
from typing import Optional

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Filter Selection'
VERSION_INFO = (2, 1, 1)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'


class FlameButton(QtWidgets.QPushButton):
    """
    Custom Qt Flame Button Widget v2.1

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
        self.clicked.connect(connect)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
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
    """
    Custom Qt Flame Label Widget v2.1

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


class FlameLineEdit(QtWidgets.QLineEdit):
    """
    Custom Qt Flame Line Edit Widget v2.1

    Main window should include this: window.setFocusPolicy(QtCore.Qt.StrongFocus)

    text: text show [str]
    width: (optional) width of widget. default is 150. [int]
    max_width: (optional) maximum width of widget. default is 2000. [int]

    Usage:

        line_edit = FlameLineEdit('Some text here')
    """

    def __init__(self, text, width=150, max_width=2000):
        super().__init__()

        self.setText(text)
        self.setMinimumHeight(28)
        self.setMinimumWidth(width)
        self.setMaximumWidth(max_width)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setStyleSheet("""
            QLineEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: 1px solid rgb(55, 65, 75);
                padding-left: 5px;
                font: 14px "Discreet"}
            QLineEdit:focus {background-color: rgb(73, 86, 99)}
            QLineEdit:hover {border: 1px solid rgb(90, 90, 90)}
            QLineEdit:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(55, 55, 55);
                border: 1px solid rgb(55, 55, 55)}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: none}""")


class FlameListWidget(QtWidgets.QListWidget):
    """
    Custom Qt Flame List Widget

    FlameListWidget([min_width=200, max_width=2000, min_height=250, max_height=2000])

    Example:
        list_widget = FlameListWidget()
    """

    def __init__(
            self, min_width: Optional[int] = 200, max_width: Optional[int] = 2000,
            min_height: Optional[int] = 250, max_height: Optional[int] = 2000):
        super().__init__()

        # Check argument types

        if not isinstance(min_width, int):
            raise TypeError('FlameListWidget: min_width must be integer.')
        if not isinstance(max_width, int):
            raise TypeError('FlameListWidget: max_width must be integer.')
        if not isinstance(min_height, int):
            raise TypeError('FlameListWidget: min_height must be integer.')
        if not isinstance(max_height, int):
            raise TypeError('FlameListWidget: max_height must be integer.')

        # Build list widget

        self.setMinimumWidth(min_width)
        self.setMaximumWidth(max_width)
        self.setMinimumHeight(min_height)
        self.setMaximumHeight(max_height)
        self.spacing()
        self.setUniformItemSizes(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QListWidget {
                color: rgb(154, 154, 154);
                background-color: rgb(30, 30, 30);
                alternate-background-color: rgb(36, 36, 36);
                outline: 3px rgb(0, 0, 0);
                font: 14px "Discreet"}
            QListWidget::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(102, 102, 102);
                border: 1px solid rgb(102, 102, 102)}
            QScrollBar {
                background: rgb(61, 61, 61)}
            QScrollBar::handle {
                background: rgb(31, 31, 31)}
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar {
                background: rgb(61, 61, 61)}
            QScrollBar::handle {
                background: rgb(31, 31, 31)}
            QScrollBar::add-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")


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


class FilterSelection:
    """Take the selection and filter it, to create a smaller more specific selection."""

    def __init__(self, selection):
        """Create instance."""
        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.selection = selection
        self.selection_list = None

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def get_names(self):
        """Get the object names of everything that is selected."""
        return [item.name.get_value() for item in self.selection]

    def process_selection(self):
        """Update the selection in Flame."""
        for item in self.selection:
            if item.name.get_value() not in self.selection_list:
                item.selected = False

    def main_window(self):
        """Enter search terms, view results, then confirm the selection."""

        def okay_button():
            """Close window and process the artist's selected subdirectory."""
            self.window.close()
            self.process_selection()
            self.message('Done!')

        def cancel_button():
            """Do when cancel button is pressed."""
            self.window.close()
            self.message('Cancelled!')

        def filter_button():
            """Do when filter button is touched."""
            find_updated()

        def filter_mode_button():
            """Do when filter mode button is touched."""
            find_updated()

        def filter_contains(search_term, to_be_searched):
            """Perform a basic contains filter.

            Args:
                search_term:  A string to look for.
                to_be_searched:  A string to search in.

            Returns:
                Bool
            """
            return search_term in to_be_searched

        def filter_contains_not(search_term, to_be_searched):
            """Perform a basic contains filter.

            Args:
                search_term:  A string to look for.
                to_be_searched:  A string to search in.

            Returns:
                Bool
            """
            return search_term not in to_be_searched

        def filter_list(filter_method):
            """Updates the results list when anything is typed in the Find bar.

            Args:
                filter_method:  A function that returns a bool.
            """
            for num in range(self.list_scroll.count()):
                if filter_method(self.find.text(), self.list_scroll.item(num).text()):
                    self.list_scroll.item(num).setHidden(False)
                else:
                    self.list_scroll.item(num).setHidden(True)

        def update_selection_list():
            """Pass selection in the PySide window back to a class attribute."""
            self.selection_list = [self.list_scroll.item(num).text() for num in
                    range(self.list_scroll.count()) if
                        not self.list_scroll.item(num).isHidden()]

        def find_updated():
            """Execute when the Find field is updated."""
            if self.filter_mode_btn.text() == 'Contains':
                filter_list(filter_contains)
            if self.filter_mode_btn.text() == 'Does Not Contain':
                filter_list(filter_contains_not)
            update_selection_list()

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(600, 600)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)

        # Mac needs this to close the window
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.window.move(
                (resolution.width() / 2) - (self.window.frameSize().width() / 2),
                (resolution.height() / 2) - (self.window.frameSize().height() / 2))

        # Label
        self.find_label = FlameLabel('Find')

        # Line Edit
        self.find = FlameLineEdit('')
        self.find.textChanged.connect(find_updated)

        # List Widget
        self.list_scroll = FlameListWidget(min_width=500)
        self.list_scroll.addItems(self.get_names())
        self.list_scroll.sortItems()
        self.list_scroll.itemDoubleClicked.connect(okay_button)

        # Buttons
        self.filter_btn = FlamePushButtonMenu(
                'Name', ['Name'], menu_width=170, menu_action=filter_button)
        self.filter_mode_btn = FlamePushButtonMenu(
                'Contains', ['Contains', 'Does Not Contain'],
                menu_width=130,
                menu_action=filter_mode_button)
        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')
        self.ok_btn.setAutoDefault(True)  # doesnt make Enter key work

        self.cancel_btn = FlameButton('Cancel', cancel_button)

        # Shortcuts
        self.shortcut_enter = QtGui.QShortcut(
                QtGui.QKeySequence('Enter'), self.ok_btn, okay_button)
        self.shortcut_escape = QtGui.QShortcut(
                QtGui.QKeySequence('Escape'), self.cancel_btn, cancel_button)
        self.shortcut_return = QtGui.QShortcut(
                QtGui.QKeySequence('Return'), self.ok_btn, okay_button)

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)

        self.grid.addWidget(self.filter_btn, 0, 0)
        self.grid.addWidget(self.filter_mode_btn, 0, 1)
        self.grid.addWidget(self.find, 0, 2)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.list_scroll)
        self.hbox.addStretch(1)

        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(self.cancel_btn)
        self.hbox2.addWidget(self.ok_btn)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.grid)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox2)

        self.window.setLayout(self.vbox)

        # Inital Focus
        self.find.setFocus()

        self.window.show()
        return self.window


def scope_sequence(selection):
    """Ensure selection only contains the objects this script is inteneded for."""
    valid_objects = (
            flame.PyClip,
            flame.PySegment,
    )

    return all(isinstance(item, valid_objects) for item in selection)


def get_media_panel_custom_ui_actions():
    """Add right click menu."""
    return [{'name': 'Select...',
             'actions': [{'name': 'Filter Selection',
                          'isVisible': scope_sequence,
                          'execute': FilterSelection,
                          'minimumVersion': '2025.0.0.0'}]
            }]
