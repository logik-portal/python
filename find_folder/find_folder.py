"""
Script Name: Find Folder
Script Version: 3.0.0
Flame Version: 2025
Written by: Kieran Hanrahan
Creation Date: 07.22.22
Update Date: 09.05.24

Description:

    Searches for a subdirectory of the current directory in the Media Hub.  Useful for
    navigating a folder that contains many many subfolders with long names but you have
    a search term that would quickly find the folder you need.

    URL: http://github.com/khanrahan/find-folder

Menus:

    Right-click selected folder in Media Hub Files -> Find... -> Find Folder

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user, copy this file to:
    /opt/Autodesk/user/<user name>/python
"""


import os
from typing import Optional

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Find Folder'
VERSION_INFO = (3, 0, 0)
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
                    font: 14px 'Discreet'}
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
                    font: 12px 'Discreet'}
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
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'underline':
            self.setAlignment(QtCore.Qt.AlignCenter)
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    border-bottom: 1px inset rgb(40, 40, 40);
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")
        elif label_type == 'background':
            self.setStyleSheet("""
                QLabel {
                    color: rgb(154, 154, 154);
                    background-color: rgb(30, 30, 30);
                    padding-left: 5px;
                    font: 14px 'Discreet'}
                QLabel:disabled {
                    color: rgb(106, 106, 106)}""")


class FlameLineEdit(QtWidgets.QLineEdit):
    """ Custom Qt Flame Line Edit Widget v2.1

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
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setStyleSheet("""
            QLineEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: 1px solid rgb(55, 65, 75);
                padding-left: 5px;
                font: 14px 'Discreet'}
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
    """Custom Qt Flame List Widget

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
                font: 14px 'Discreet'}
            QListWidget::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(102, 102, 102);
                border: 1px solid rgb(102, 102, 102)}
            QScrollBar {
                background: rgb(31, 31, 31)}
            QScrollBar::handle {
                background: rgb(61, 61, 61)}
            QScrollBar::add-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::add-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                width: 0px;
                height: 0px}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")


class FlameMessageBox(QtWidgets.QMessageBox):
    """Custom Qt Flame Message Box

    Usage:
        message_box = FlameMessageBox(message)
        message_box.setText("message for user.")
        message_box.setWindowTitle("window title")
        message_box.exec_()
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # the below has now effect.  should be subclassing QDialog instead.
        self.setMinimumSize(400, 270)
        # Could not get the below working so just doing it at the instance.
        #self.setText(self.message)
        self.button = self.addButton(QtWidgets.QMessageBox.Ok)
        self.button.setFocusPolicy(QtCore.Qt.NoFocus)
        self.button.setMinimumSize(QtCore.QSize(80, 28))
        self.setStyleSheet("""
            MessageBox {
                background-color: #313131;
                font: 14px 'Discreet'}
            QLabel {
                color: #9a9a9a;
                font: 14px 'Discreet'}
            QPushButton {
                color: #9a9a9a;
                background-color: #732020;
                border-top: 1px inset #555555;
                border-bottom: 1px inset black;
                font: 14px 'Discreet'}
            QPushButton:pressed {
                color: #d9d9d9;
                background-color: #4f4f4f;
                border-top: 1px inset #666666;
                font: italic}""")


class FindFolder:
    """Searches for a subdirectory.

    Find matching subdirectories based on a search string, then navigate to the
    destination subdirectory the artist chooses.
    """

    def __init__(self, selection):
        """Ensure that only 1 folder is selected by the artist."""
        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.src_path = selection[0].path

        self.dest_folder = ''
        self.dest_path = ''

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def get_folders(self):
        """Return all subdirectories in a folder."""
        walker = os.walk(self.src_path)

        root, dirs, files = next(walker)
        del root
        del files

        results = [d for d in dirs if d[0] != '.']  # results unsorted

        return results

    def main_window(self):
        """Enter search terms, view results, then confirm the selection."""

        def okay_button():
            """Close window and process the artist's selected subdirectory."""
            self.window.close()

            self.dest_folder = self.list_scroll.selectedItems()[0].text()
            self.dest_path = os.path.join(self.src_path, self.dest_folder)

            # introduced in flame 2021.2
            flame.mediahub.files.set_path(self.dest_path)

            self.message(f'MediaHub path changed to {self.dest_path}')
            self.message('Done!')

        def cancel_button():
            """Do when cancel button is pressed."""
            self.window.close()
            self.message('Cancelled!')

        def filter_list():
            """Updates the results list when anything is typed in the Find bar."""
            for num in range(self.list_scroll.count()):
                if self.find.text() in self.list_scroll.item(num).text():
                    self.list_scroll.item(num).setHidden(False)
                else:
                    self.list_scroll.item(num).setHidden(True)

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(600, 600)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)

        # Mac needs this to close the window
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # FlameLineEdit class needs this
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()

        self.window.move(
                (resolution.width() / 2) - (self.window.frameSize().width() / 2),
                (resolution.height() / 2) - (self.window.frameSize().height() / 2))

        # Label
        self.find_label = FlameLabel('Find')

        # Line Edit
        self.find = FlameLineEdit('')
        self.find.textChanged.connect(filter_list)

        # List Widget
        self.list_scroll = FlameListWidget(min_width=500)
        self.list_scroll.addItems(self.get_folders())
        self.list_scroll.sortItems()
        self.list_scroll.itemDoubleClicked.connect(okay_button)

        # Buttons
        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')
        self.ok_btn.setAutoDefault(True)  # doesnt make Enter key work

        self.cancel_btn = FlameButton('Cancel', cancel_button)

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)

        self.grid.addWidget(self.find_label, 0, 0)
        self.grid.addWidget(self.find, 0, 1)

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
        self.vbox.insertSpacing(1, 20)
        self.vbox.addLayout(self.hbox)
        self.vbox.insertSpacing(3, 20)
        self.vbox.addLayout(self.hbox2)

        self.window.setLayout(self.vbox)

        self.window.show()
        return self.window


def scope_folders(selection):
    """Determine if selection is a folder in the Media Hub > Files tab."""
    valid_objects = (flame.PyMediaHubFilesFolder,)

    return (len(selection) == 1 and isinstance(selection[0], valid_objects))


def get_mediahub_files_custom_ui_actions():
    """Python hook to add custom item to right click menu in MediaHub."""
    return [{'name': 'Find...',
             'actions': [{'name': 'Find Folder',
                          'isVisible': scope_folders,
                          'execute': FindFolder,
                          'minimumVersion': '2025'}]
            }]
