"""
Script Name: Apply Text TimelineFX to Segments
Written By: Kieran Hanrahan

Script Version: 3.0.0
Flame Version: 2025

URL: http://github.com/khanrahan/apply-text-timelinefx-to-segments

Creation Date: 06.23.23
Update Date: 03.04.25

Description:

    Find specific segments in the selected sequences then apply Text TimelineFX and load
    Text setups based on a token pattern.

    Put simply... its for loading text setups in bulk!

Menus:

    Right-click selected items on the Desktop --> Apply... --> Text TimelineFX to Segments

    Right-click selected items in the Media Panel --> Apply... --> Text TimelineFX to Segments

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import datetime as dt
import os
import re
import xml.etree.ElementTree as et
from functools import partial

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Apply Text TimelineFX to Segments'
VERSION_INFO = (3, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

DEFAULT_PATH = '/opt/Autodesk/project'
DEFAULT_PATTERN = '<project>/text/flame/<name>.ttg'
PRESET_FOLDER = '~/.config/apply-text-timelinefx-to-segments'
XML = 'apply_text_timeline_fx_to_segments.xml'


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
    """Custom Qt Flame Line Edit Widget v2.1

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


class FlameLineEditFileBrowse(QtWidgets.QLineEdit):
    """Custom Qt Flame Clickable Line Edit Widget with File Browser

    FlameLineEditFileBrowse(file_path, filter_type, window)

    file_path:
        Path browser will open to. If set to root folder (/), browser will open to user
        home directory
    filter_type:
        Type of file browser will filter_type for. If set to 'dir', browser will select
        directory.  For example, 'Python (*.py)' or 'dir'

    """

    clicked = QtCore.Signal()

    def __init__(self, file_path, filter_type, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.filter_type = filter_type
        self.file_path = file_path
        self.path_new = ''

        self.setText(file_path)
        self.setParent(parent)
        self.setMinimumHeight(28)
        self.setReadOnly(True)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.clicked.connect(self.file_browse)
        self.setStyleSheet("""
            QLineEdit {
                color: #898989;
                background-color: #373e47;
                font: 14px 'Discreet'}
            QLineEdit:disabled {
                color: #6a6a6a;
                background-color: #373737}""")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.setStyleSheet("""
                QLineEdit {
                    color: #bbbbbb;
                    background-color: #474e58;
                    font: 14px 'Discreet'}
                QLineEdit:disabled {
                    color: #6a6a6a;
                    background-color: #373737}""")
            self.clicked.emit()
            self.setStyleSheet("""
                QLineEdit {
                    color: #898989;
                    background-color: #373e47;
                    font: 14px 'Discreet'}
                QLineEdit:disabled {
                    color: #6a6a6a;
                    background-color: #373737}""")
        else:
            super().mousePressEvent(event)

    def file_browse(self):
        # from PySide2 import QtWidgets

        file_browser = QtWidgets.QFileDialog()

        # If no path go to user home directory

        if self.file_path == '/':
            self.file_path = os.path.expanduser('~')
        if os.path.isfile(self.file_path):
            self.file_path = self.file_path.rsplit('/', 1)[0]

        file_browser.setDirectory(self.file_path)

        # If filter_type set to dir, open Directory Browser, if anything else, open File
        # Browser

        if self.filter_type == 'dir':
            file_browser.setFileMode(QtWidgets.QFileDialog.Directory)
            if file_browser.exec_():
                self.path_new = file_browser.selectedFiles()[0]
                self.setText(self.path_new)
        else:
            # Change to ExistingFiles to capture many files
            file_browser.setFileMode(QtWidgets.QFileDialog.ExistingFile)
            file_browser.setNameFilter(self.filter_type)
            if file_browser.exec_():
                self.path_new = file_browser.selectedFiles()[0]
                self.setText(self.path_new)


class FlameMessageWindow(QtWidgets.QDialog):
    """Custom Qt Flame Message Window v2.1

    message_title: text shown in top left of window ie. Confirm Operation [str]
    message_type: confirm, message, error, warning [str] confirm and warning return True
                  or False values
    message: text displayed in body of window [str]
    parent: optional - parent window [object]

    Message Window Types:
        confirm: confirm and cancel button / grey left bar - returns True or False
        message: ok button / blue left bar
        error: ok button / yellow left bar
        warning: confirm and cancel button / red left bar - returns True of False

    Usage:
        FlameMessageWindow('Error', 'error', 'some important message')

        or

        if FlameMessageWindow(
            'Confirm Operation', 'confirm', 'some important message', window):
                do something
    """

    def __init__(self, message_title, message_type, message, parent=None):
        super().__init__()

        self.message_type = message_type

        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(QtCore.QSize(500, 330))
        self.setMaximumSize(QtCore.QSize(500, 330))
        self.setStyleSheet('background-color: rgb(36, 36, 36)')

        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

        self.main_label = FlameLabel(message_title, 'normal', label_width=500)
        self.main_label.setStyleSheet("""
            color: rgb(154, 154, 154);
            font: 18px 'Discreet'""")

        self.message_text_edit = QtWidgets.QTextEdit(message)
        self.message_text_edit.setDisabled(True)
        self.message_text_edit.setStyleSheet("""
            QTextEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(36, 36, 36);
                selection-color: rgb(190, 190, 190);
                selection-background-color: rgb(36, 36, 36);
                border: none;
                padding-left: 20px;
                padding-right: 20px;
                font: 12px 'Discreet'}""")

        if message_type in ('confirm', 'warning'):
            self.confirm_button = FlameButton(
                'Confirm', self.confirm, button_color='blue', button_width=110)
            self.cancel_button = FlameButton('Cancel', self.cancel, button_width=110)

            self.grid.addWidget(self.main_label, 0, 0)
            self.grid.setRowMinimumHeight(1, 30)
            self.grid.addWidget(self.message_text_edit, 2, 0, 4, 8)
            self.grid.setRowMinimumHeight(9, 30)
            self.grid.addWidget(self.cancel_button, 10, 5)
            self.grid.addWidget(self.confirm_button, 10, 6)
            self.grid.setRowMinimumHeight(11, 30)
        else:
            self.ok_button = FlameButton(
                'Ok', self.confirm, button_color='blue', button_width=110)

            self.grid.addWidget(self.main_label, 0, 0)
            self.grid.setRowMinimumHeight(1, 30)
            self.grid.addWidget(self.message_text_edit, 2, 0, 4, 8)
            self.grid.setRowMinimumHeight(9, 30)
            self.grid.addWidget(self.ok_button, 10, 6)
            self.grid.setRowMinimumHeight(11, 30)

        # Why stripping these?
        message = message.replace('<br>', '')
        message = message.replace('<center>', '')
        message = message.replace('<dd>', '')

        self.setLayout(self.grid)
        self.show()
        self.exec_()

    def __bool__(self):

        return self.confirmed

    def cancel(self):

        self.close()
        self.confirmed = False

    def confirm(self):

        self.close()
        self.confirmed = True

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)

        if self.message_type == 'confirm':
            line_color = QtGui.QColor(71, 71, 71)
        elif self.message_type == 'message':
            line_color = QtGui.QColor(0, 110, 176)
        elif self.message_type == 'error':
            line_color = QtGui.QColor(200, 172, 30)
        elif self.message_type == 'warning':
            line_color = QtGui.QColor(200, 29, 29)

        painter.setPen(QtGui.QPen(line_color, 6, QtCore.Qt.SolidLine))
        painter.drawLine(0, 0, 0, 330)

        painter.setPen(QtGui.QPen(QtGui.QColor(71, 71, 71), .5, QtCore.Qt.SolidLine))
        painter.drawLine(0, 40, 500, 40)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):

        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            pass


class FlameProgressWindow(QtWidgets.QDialog):
    """Custom Qt Flame Progress Window

    FlameProgressWindow(window_title, num_to_do[, text=None, enable_done_button=False,
                        parent=None])

    window_title: text shown in top left of window ie. Rendering... [str]
    num_to_do: total number of operations to do [int]
    text: message to show in window [str]
    enable_cancel_button: enable cancel button, default is False [bool]

    Examples:
        To create window:

            self.progress_window = FlameProgressWindow(
                'Rendering...', 10,
                text='Rendering: Batch 1 of 5',
                enable_done_button=True)

        To update progress bar:

            self.progress_window.set_progress_value(number_of_things_done)

        To enable or disable done button - True or False:

            self.progress_window.enable_done_button(True)
    """

    def __init__(
            self,
            window_title,
            num_to_do,
            text='',
            window_bar_color='blue',
            enable_cancel_button=True,
            parent=None):

        super().__init__()

        self.cancelled = False

        # Check argument types

        if not isinstance(window_title, str):
            raise TypeError('FlameProgressWindow: window_title must be a string')
        if not isinstance(num_to_do, int):
            raise TypeError('FlameProgressWindow: num_to_do must be an integer')
        if not isinstance(text, str):
            raise TypeError('FlameProgressWindow: text must be a string')
        if not isinstance(enable_cancel_button, bool):
            raise TypeError('FlameProgressWindow: enable_done_button must be a boolean')
        if window_bar_color not in ['blue', 'red', 'green', 'yellow', 'gray', 'teal']:
            raise ValueError('FlameWindow: Window Bar Color must be one of: '
                             'blue, red, green, yellow, gray, teal.')

        self.window_bar_color = window_bar_color

        # Build window

        # Mac needs this to close the window
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.setWindowFlags(
                QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumSize(QtCore.QSize(500, 330))
        self.setMaximumSize(QtCore.QSize(500, 330))
        self.setStyleSheet('background-color: rgb(36, 36, 36)')

        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

        self.main_label = FlameLabel(window_title, label_width=500)
        self.main_label.setStyleSheet("""
            color: rgb(154, 154, 154);
            font: 18px 'Discreet'""")
        self.message_text_edit = QtWidgets.QTextEdit('')
        self.message_text_edit.setDisabled(True)
        self.message_text_edit.setStyleSheet("""
            QTextEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(36, 36, 36);
                selection-color: rgb(190, 190, 190);
                selection-background-color: rgb(36, 36, 36);
                border: none;
                padding-left: 20px;
                padding-right: 20px;
                font: 12px 'Discreet'}""")
        self.message_text_edit.setText(text)

        # Progress bar

        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setMaximum(num_to_do)
        self.progress_bar.setMaximumHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 45, 45);
                font: 14px 'Discreet';
                border: none}
            QProgressBar:chunk {
                background-color: rgb(0, 110, 176)}""")

        self.cancel_button = FlameButton(
                'Cancel',
                self.cancel,
                button_color='normal',
                button_width=110)
        self.cancel_button.setEnabled(enable_cancel_button)
        self.cancel_button.setVisible(enable_cancel_button)

        # Layout

        self.grid.addWidget(self.main_label, 0, 0)
        self.grid.setRowMinimumHeight(1, 30)
        self.grid.addWidget(self.message_text_edit, 2, 0, 1, 4)
        self.grid.addWidget(self.progress_bar, 8, 0, 1, 7)
        self.grid.setRowMinimumHeight(9, 30)
        self.grid.addWidget(self.cancel_button, 10, 6)
        self.grid.setRowMinimumHeight(11, 30)

        self.setLayout(self.grid)
        self.show()

    def set_text(self, text):

        self.message_text_edit.setText(text)

    def set_progress_value(self, value):

        self.progress_bar.setValue(value)

    def enable_cancel_button(self, value):

        if value:
            self.cancel_button.setEnabled(True)
        else:
            self.cancel_button.setEnabled(False)

    def cancel(self):

        self.cancelled = True
        self.close()

    def paintEvent(self, event):

        painter = QtGui.QPainter(self)
        if self.window_bar_color == 'blue':
            bar_color = QtGui.QColor(0, 110, 176)
        elif self.window_bar_color == 'red':
            bar_color = QtGui.QColor(200, 29, 29)
        elif self.window_bar_color == 'green':
            bar_color = QtGui.QColor(0, 180, 13)
        elif self.window_bar_color == 'yellow':
            bar_color = QtGui.QColor(251, 181, 73)
        elif self.window_bar_color == 'gray':
            bar_color = QtGui.QColor(71, 71, 71)
        elif self.window_bar_color == 'teal':
            bar_color = QtGui.QColor(14, 110, 106)

        # painter.setPen(QtGui.QPen(QtGui.QColor(71, 71, 71), .5, QtCore.Qt.SolidLine))
        # painter.drawLine(0, 40, 500, 40)

        # Draw line below title that goes from side bar color to grey

        gradient = QtGui.QLinearGradient(0, 0, 500, 40)
        gradient.setColorAt(1, QtGui.QColor(71, 71, 71))
        gradient.setColorAt(0, bar_color)
        painter.setPen(QtGui.QPen(gradient, .5, QtCore.Qt.SolidLine))
        painter.drawLine(0, 40, 500, 40)

        # Draw bar on left side of window

        painter.setPen(QtGui.QPen(bar_color, 6, QtCore.Qt.SolidLine))
        painter.drawLine(0, 0, 0, 330)

    def mousePressEvent(self, event):
        self.oldPosition = event.globalPos()

    def mouseMoveEvent(self, event):
        try:
            delta = QtCore.QPoint(event.globalPos() - self.oldPosition)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPosition = event.globalPos()
        except:
            pass


class FlamePushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Push Button Widget

    This is the original Push Button Widget with just the StyleSheet from the most
    recent iteration on pyflame.com.
    """

    def __init__(self, name, parent, checked, connect, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setText(name)
        self.setParent(parent)
        self.setCheckable(True)
        self.setChecked(checked)
        self.clicked.connect(connect)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setMinimumSize(150, 28)
        self.setMaximumSize(150, 28)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(44, 54, 68));
                border-left: 1px solid rgb(58, 58, 58);
                border-right: 1px solid rgb(44, 54, 68);
                padding-left: 5px; font: 14px 'Discreet'}
            QPushButton:checked {
                color: rgb(217, 217, 217);
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                text-align: left;
                border-top: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                border-bottom: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(71, 71, 71),
                    stop: .94 rgb(50, 101, 173));
                border-left: 1px solid rgb(71, 71, 71);
                border-right: 1px solid rgb(50, 101, 173);
                padding-left: 5px;
                font: italic}
            QPushButton:hover {border: 1px solid rgb(90, 90, 90)}'
            QPushButton:disabled {
                color: #6a6a6a;
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: .93 rgb(58, 58, 58),
                    stop: .94 rgb(50, 50, 50));
                font: light;
                border: none}
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
                font: 14px 'Discreet';
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
                border: none; font: 14px 'Discreet'}
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


class FlameTokenPushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Token Push Button Widget v2.1

    button_name: Text displayed on button [str]
    token_dict: Dictionary defining tokens. {'Token Name': '<Token>'} [dict]
    token_dest: LineEdit that token will be applied to [object]
    button_width: (optional) default is 150 [int]
    button_max_width: (optional) default is 300 [int]

    Usage:
        token_dict = {'Token 1': '<Token1>', 'Token2': '<Token2>'}
        token_push_button = FlameTokenPushButton('Add Token', token_dict, token_dest)
    """

    def __init__(self, button_name, token_dict, token_dest, button_width=110,
                 button_max_width=300):
        super().__init__()

        self.setText(button_name)
        self.setMinimumHeight(28)
        self.setMinimumWidth(button_width)
        self.setMaximumWidth(button_max_width)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QPushButton {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none;
                font: 14px 'Discreet';
                padding-left: 6px;
                text-align: left}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QPushButton:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(45, 55, 68);
                border: none}
            QPushButton::menu-indicator {
                subcontrol-origin: padding;
                subcontrol-position: center right}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")

        def token_action_menu():

            def insert_token(token):
                for key, value in token_dict.items():
                    if key == token:
                        token_name = value
                        token_dest.insert(token_name)

            # the lambda sorts aAbBcC instead of ABCabc
            for key, value in sorted(token_dict.items(), key=lambda v: v[0].upper()):
                del value
                token_menu.addAction(key, partial(insert_token, key))

        token_menu = QtWidgets.QMenu(self)
        token_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        token_menu.setStyleSheet("""
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none; font: 14px 'Discreet'}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.setMenu(token_menu)
        token_action_menu()


class FlameTableWidget(QtWidgets.QTableWidget):
    """Custom Qt Widget Flame Table Widget v1.0.0

    Attributes:
        column_headers: list of headers for the table

    Usage:
        flame_table = FlameTableWidget(['header1', 'header2'])
    """

    def __init__(self, column_headers):
        super().__init__()

        self.setMinimumSize(500, 250)
        self.setColumnCount(len(column_headers))
        self.setRowCount(1)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.setHorizontalHeaderLabels(column_headers)
        self.setStyleSheet("""
            QTableWidget {
                background-color: rgb(33, 33, 33);
                alternate-background-color: rgb(36, 36, 36);
                color: rgb(190, 190, 190);
                font: 14px 'Discreet';
                gridline-color: rgb(33, 33, 33)}
            QTableWidget::item {
                border: 0px 10px 0px 0px;
                padding: 0px 15px 0px 5px}
            QTableWidget::item:selected {
                color: #d9d9d9;
                background-color: #474747}
            QHeaderView::section {
                color: black;
                font: 14px 'Discreet'}""")

        self.header_horiz = self.horizontalHeader()
        self.header_horiz.setDefaultAlignment(QtCore.Qt.AlignLeft)
        self.header_horiz.setStyleSheet("""
            ::section {
                border: 0px;
                color: rgb(177, 177, 177);
                background-color: rgb(19, 21, 23);
                padding: 3px 3px 0px 8px}""")

        self.header_vert = self.verticalHeader()
        self.header_vert.setDefaultSectionSize(24)
        self.header_vert.setVisible(False)
        self.header_vert.setStyleSheet("""
                ::section {
                    border: 0px;
                    padding 0px}""")

    def add_item(self, row, column, item):
        """Add row if necessary, then add item to column."""
        if row + 1 > self.rowCount():
            self.insertRow(row)

        self.setItem(row, column, QtWidgets.QTableWidgetItem(item))

    def get_data_by_row_number(self, row_num):
        """Convenience method to get data from specific row number.

        Returns:
            A list of the data per column.
        """
        data = []

        for column in range(self.columnCount()):
            data.append(self.model().data(self.model().index(row_num, column)))

        return data

    def get_selected_row_data(self):
        """Convenience method to get data from selected rows.

        Returns:
            A list containing a list for each selected row.
        """
        data = []

        for row in self.selectionModel().selectedRows():  # row is QModelIndex object
            row_data = []

            if not self.isRowHidden(row.row()):
                for column in range(self.columnCount()):
                    row_data.append(
                            self.model().data(self.model().index(row.row(), column)))
                data.append(row_data)

        return data


class FindSegmentApplyText:
    """Find segments and load text timeline FX setups.

    Find specific segments in a selection, assemble a Text TimelineFX setup path using
    tokens, then load the setup to the specified segments.
    """

    def __init__(self, selection):
        """Create FindSegmentApplyText object with starting attributes."""
        self.selection = selection

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        # Load presets
        self.presets_xml_folder = os.path.expanduser(PRESET_FOLDER)
        self.presets_xml = os.path.join(self.presets_xml_folder, XML)
        self.presets_xml_tree = ''
        self.presets_xml_root = ''
        self.load_presets()

        # Fields
        self.path = ''
        self.load_path()

        self.pattern = ''
        self.load_pattern()

        self.find = ''
        self.load_find()

        # Find segments
        self.segments = []
        self.find_segments()

        # Tokens
        self.now = dt.datetime.now()
        self.segment_tokens = {}

        # Columns
        self.table_columns = [
                'Segment #', 'Sequence', 'Segment', 'Record In', 'Record Out',
                'Filename']

        # Window
        self.save_window_x = 500
        self.save_window_y = 100

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    @staticmethod
    def get_parent_sequence(child):
        """Returns object of the container sequence for the given flame object."""
        parents = []

        while child:
            # a PyClip can contain segments but not be a PySequence
            if isinstance(child, flame.PyClip):
                break
            if isinstance(child, flame.PySequence):
                break
            child = child.parent
            parents.append(child)

        parent_sequence = parents[-1]
        return parent_sequence

    def load_preset_by_index_element(self, index, element):
        """Load preset and replace None with empty string."""
        preset_element = (
            self.presets_xml_root.findall('preset')[index].find(element).text)

        if preset_element is None:
            preset_element = ''

        return preset_element

    def load_path(self):
        """Load the first preset's path or use the default pattern."""
        if self.presets_xml_root.findall('preset'):
            self.path = self.load_preset_by_index_element(0, 'path')
        else:
            self.path = DEFAULT_PATH

    def load_pattern(self):
        """Load the first preset's pattern or use the default pattern."""
        if self.presets_xml_root.findall('preset'):
            self.pattern = self.load_preset_by_index_element(0, 'pattern')
        else:
            self.pattern = DEFAULT_PATTERN

    def load_find(self):
        """Load the first preset's search term or use the default pattern."""
        if self.presets_xml_root.findall('preset'):
            self.find = self.load_preset_by_index_element(0, 'find')
        else:
            self.find = ''

    def load_presets(self):
        """Load preset file if preset and store XML tree & root."""
        if os.path.isfile(self.presets_xml):
            self.presets_xml_tree = et.parse(self.presets_xml)
        else:
            default = """<presets></presets>"""
            self.presets_xml_tree = et.ElementTree(et.fromstring(default))

        self.presets_xml_root = self.presets_xml_tree.getroot()

    def find_segments(self):
        """Assemble list of all PySegments in selected Sequences."""
        self.message('Scanning for segments...')

        for sequence in self.selection:
            for version in sequence.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        # Skip hidden segments.  Would cause crash when adding TextFX.
                        if segment.hidden.get_value() is True:
                            continue
                        # Skip gaps.  Clutters the segments listed in the table.
                        if segment.type == 'Gap':
                            continue
                        self.segments.append(segment)

        self.message(f'Found {len(self.segments)} segments')

    def generate_segment_tokens(self, segment):
        """Populate the token list."""
        self.segment_tokens['am/pm'] = [
                '<pp>', self.now.strftime('%p').lower()]
        self.segment_tokens['AM/PM'] = [
                '<PP>', self.now.strftime('%p').upper()]
        self.segment_tokens['Day'] = [
                '<DD>', self.now.strftime('%d')]
        self.segment_tokens['Hour (12hr)'] = [
                '<hh>', self.now.strftime('%I')]
        self.segment_tokens['Hour (24hr)'] = [
                '<HH>', self.now.strftime('%H')]
        self.segment_tokens['Minute'] = [
                '<mm>', self.now.strftime('%M')]
        self.segment_tokens['Month'] = [
                '<MM>', self.now.strftime('%m')]
        self.segment_tokens['Project'] = [
                '<project>', flame.project.current_project.name]
        self.segment_tokens['Segment Name'] = [
                '<segment name>', segment.name.get_value()]
        self.segment_tokens['Sequence Name'] = [
                '<name>', self.get_parent_sequence(segment).name.get_value()]
        self.segment_tokens['User'] = [
                '<user>', flame.users.current_user.name]
        self.segment_tokens['Year'] = [
                '<YYYY>', self.now.strftime('%Y')]

    def resolve_tokens(self):
        """Replace tokens with values."""
        result = self.pattern

        for token, values in self.segment_tokens.items():
            del token
            result = re.sub(values[0], values[1], result)

        return result

    def assemble_filename(self):
        """Assemble finished filename for row in the Table.

        The starred expression is for if the artist has the Pattern field starting with
        a slash, therefore an absolute path.  os.path.join will not work on 2 absolute
        paths.
        """
        return os.path.join(self.path, *self.resolve_tokens().split(os.sep))

    def apply_text_fx_to_segment(self, segment, text_setup):
        """Apply Text TimelineFX to segment, then load setup."""
        for effect in segment.effects:
            if effect.type == 'Text':
                flame.delete(effect)

        segment_text_fx = segment.create_effect('Text')

        self.message(f'Loading {text_setup}')

        if os.path.isfile(text_setup):
            try:
                # load_setup will not take utf-8, only ascii
                segment_text_fx.load_setup(text_setup.encode('ascii', 'ignore'))
            except RuntimeError:
                self.message('Error loading setup!')
            else:
                self.message('Successfully loaded!')
        else:
            self.message('File does not exist!')

    def save_preset_window(self):
        """Smaller window with save dialog."""

        def duplicate_check():
            """Check that preset to be saved would not be a duplicate."""
            duplicate = False
            preset_name = self.line_edit_preset_name.text()

            for preset in self.presets_xml_root.findall('preset'):
                if preset.get('name') == preset_name:
                    duplicate = True

            return duplicate

        def check_preset_folder():
            """Check that destination folder for preset XML file is available."""
            result = False

            if os.path.exists(self.presets_xml_folder):
                result = True
            else:
                try:
                    os.makedirs(self.presets_xml_folder)
                    result = True
                except OSError:
                    FlameMessageWindow(
                        'Error', 'error',
                        f'Could not create {self.presets_xml_folder}')
            return result

        def save_preset():
            """Save new preset to XML file."""
            new_preset = et.Element('preset', name=self.line_edit_preset_name.text())
            new_path = et.SubElement(new_preset, 'path')
            new_path.text = self.path
            new_pattern = et.SubElement(new_preset, 'pattern')
            new_pattern.text = self.pattern
            new_filter = et.SubElement(new_preset, 'find')
            new_filter.text = self.find

            self.presets_xml_root.append(new_preset)
            sort_presets()

            if check_preset_folder():
                try:
                    self.presets_xml_tree.write(self.presets_xml)

                    self.message(f'{self.line_edit_preset_name.text()} preset saved to ' +
                                 f'{self.presets_xml}')

                except OSError:
                    FlameMessageWindow(
                        'Error', 'error',
                        f'Check permissions on {self.presets_xml}')

        def overwrite_preset():
            """Replace pattern in presets XML tree then save to XML file."""
            preset_name = self.line_edit_preset_name.text()

            for preset in self.presets_xml_root.findall('preset'):
                if preset.get('name') == preset_name:
                    preset.find('path').text = self.path
                    preset.find('pattern').text = self.pattern
                    preset.find('find').text = self.find

            try:
                self.presets_xml_tree.write(self.presets_xml)

                self.message(f'{self.line_edit_preset_name.text()} preset saved to ' +
                             f'{self.presets_xml}')
            except OSError:
                FlameMessageWindow(
                    'Error', 'error',
                    f'Check permissions on {self.presets_xml}')

        def sort_presets():
            """Alphabetically sort presets by name attribute."""
            self.presets_xml_root[:] = sorted(
                self.presets_xml_root,
                key=lambda child: (child.tag, child.get('name')))

        def save_button():
            """Triggered when the Save button at the bottom is pressed."""
            duplicate = duplicate_check()

            if duplicate:
                if FlameMessageWindow(
                        'Overwrite Existing Preset', 'confirm', 'Are you '
                        + 'sure want to permanently overwrite this preset?' + '<br/>'
                        + 'This operation cannot be undone.'):
                    overwrite_preset()
                    self.btn_preset.populate_menu(
                        [preset.get('name') for preset in
                         self.presets_xml_root.findall('preset')])
                    self.btn_preset.setText(self.line_edit_preset_name.text())
                    self.save_window.close()

            if not duplicate:
                save_preset()
                self.btn_preset.populate_menu(
                    [preset.get('name') for preset in
                     self.presets_xml_root.findall('preset')])
                self.btn_preset.setText(self.line_edit_preset_name.text())
                self.save_window.close()

        def cancel_button():
            """Triggered when the Cancel button at the bottom is pressed."""
            self.save_window.close()

        self.save_window = QtWidgets.QWidget()

        self.save_window.setMinimumSize(self.save_window_x, self.save_window_y)

        self.save_window.setStyleSheet('background-color: #272727')
        self.save_window.setWindowTitle('Save Preset As...')

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()

        self.save_window.move(
            (resolution.width() / 2) - (self.save_window_x / 2),
            (resolution.height() / 2) - (self.save_window_y / 2 + 44))

        # Labels
        self.label_preset_name = FlameLabel('Preset Name', 'normal')
        self.label_preset_pattern = FlameLabel('Pattern', 'normal')

        # Line Edits
        self.line_edit_preset_name = FlameLineEdit('')

        # Buttons
        self.save_btn_save = FlameButton(
            'Save', save_button, button_color='blue', button_width=110)
        self.save_btn_cancel = FlameButton('Cancel', cancel_button, button_width=110)

        # Layout
        self.save_grid = QtWidgets.QGridLayout()
        self.save_grid.setVerticalSpacing(10)
        self.save_grid.setHorizontalSpacing(10)
        self.save_grid.addWidget(self.label_preset_name, 0, 0)
        self.save_grid.addWidget(self.line_edit_preset_name, 0, 1)

        self.save_hbox = QtWidgets.QHBoxLayout()
        self.save_hbox.addStretch(1)
        self.save_hbox.addWidget(self.save_btn_cancel)
        self.save_hbox.addWidget(self.save_btn_save)

        self.save_vbox = QtWidgets.QVBoxLayout()
        self.save_vbox.setContentsMargins(20, 20, 20, 20)
        self.save_vbox.addLayout(self.save_grid)
        self.save_vbox.addSpacing(20)
        self.save_vbox.addLayout(self.save_hbox)

        self.save_window.setLayout(self.save_vbox)

        self.save_window.show()

        return self.save_window

    def main_window(self):
        """The main GUI."""

        def get_selected_preset():
            """Get preset that should be displayed or return empty string."""
            try:
                selected_preset = self.presets_xml_root.findall('preset')[0].get('name')
            except IndexError:  # if findall() returns empty list
                selected_preset = ''

            return selected_preset

        def get_preset_names():
            """Return just the names of the presets."""
            try:
                preset_names = [
                    preset.get('name') for preset in
                    self.presets_xml_root.findall('preset')]
            except IndexError:  # if findall() returns empty list
                preset_names = []

            return preset_names

        def update_preset():
            """Update fields when preset is changed."""
            preset_name = self.btn_preset.text()

            if preset_name:  # might be empty str if all presets were deleted
                for preset in self.presets_xml_root.findall('preset'):
                    if preset.get('name') == preset_name:
                        self.path_line_edit.setText(preset.find('path').text)
                        self.pattern_line_edit.setText(preset.find('pattern').text)
                        self.find_line_edit.setText(preset.find('find').text)
                        find_toggle()
                        break  # should not be any duplicates

        def preset_delete_button():
            """Triggered when the Delete button on the Preset line is pressed."""
            if FlameMessageWindow(
                    'Confirm Operation', 'confirm', 'Are you sure want to'
                    + ' permanently delete this preset?' + '<br/>' + 'This operation'
                    + ' cannot be undone.'):
                preset_name = self.btn_preset.text()

                for preset in self.presets_xml_root.findall('preset'):
                    if preset.get('name') == preset_name:
                        self.presets_xml_root.remove(preset)
                        self.message(
                            f'{preset_name} preset deleted from {self.presets_xml}')

                self.presets_xml_tree.write(self.presets_xml)

            # Reload presets button
            self.load_presets()
            self.btn_preset.populate_menu(get_preset_names())
            self.btn_preset.setText(get_selected_preset())
            update_preset()

        def preset_save_button():
            """Triggered when the Save button the Presets line is pressed."""
            self.save_preset_window()

        def okay_button():
            """Close window and process the artist's selected selection."""
            self.window.close()

            row_data = self.segments_table.get_selected_row_data()

            self.progress_window = FlameProgressWindow(
                    'Progress', len(row_data))

            for row in row_data:
                if self.progress_window.cancelled:
                    break

                self.message(f'Proceeding with {row[2]} in {row[1]} at {row[3]}')

                self.progress_window.set_text(
                        f'Apply Text TimlineFX to {row[2]} in {row[1]} at {row[3]}')

                self.apply_text_fx_to_segment(self.segments[int(row[0]) - 1], row[5])

                self.progress_window.set_progress_value(
                        row_data.index(row) + 1)

            self.progress_window.close()

            if self.progress_window.cancelled:
                self.message('Cancelled!')
            else:
                self.message('Done!')

        def close_button():
            """Close the window."""
            self.window.close()
            self.message('Window closed!')

        def filter_table():
            """Updates the table when anything is typed in the Find bar."""
            for num in range(self.segments_table.rowCount()):
                if self.find in self.segments_table.get_data_by_row_number(num)[2]:
                    self.segments_table.showRow(num)
                else:
                    self.segments_table.hideRow(num)

        def update_filename_column():
            """Update the filename column when the filename line edit is changed."""
            for count, segment in enumerate(self.segments):
                self.generate_segment_tokens(segment)
                self.segments_table.add_item(count, 5, self.assemble_filename())

        def verify_filename_column_exists():
            """Check if filename for text setup exists, if not, color cell text red."""
            for row in range(self.segments_table.rowCount()):
                if not os.path.isfile(
                        self.segments_table.get_data_by_row_number(row)[5]):
                    self.segments_table.item(row, 5).setData(
                            QtCore.Qt.ForegroundRole, QtGui.QColor(190, 34, 34))

        def find_changed():
            """Everything to refresh when the find line edit is changed."""
            self.find = self.find_line_edit.text()
            filter_table()

        def path_changed():
            """Everything to refresh when the path line edit is changed."""
            self.path = self.path_line_edit.text()
            update_filename_column()
            self.segments_table.resizeColumnsToContents()
            verify_filename_column_exists()

        def pattern_changed():
            """Everything to refresh when the pattern line edit is changed."""
            self.pattern = self.pattern_line_edit.text()
            update_filename_column()
            self.segments_table.resizeColumnsToContents()
            verify_filename_column_exists()

        def find_toggle():
            """Toggle UI elements based on find."""
            if self.find:
                self.btn_find_segment.setChecked(True)
                self.find_line_edit.setEnabled(True)
            if not self.find:
                self.btn_find_segment.setChecked(False)
                self.find_line_edit.setEnabled(False)

        def find_segment_button():
            """Excute when Find Segment button is pressed."""
            if not self.find_line_edit.isEnabled():
                self.find = self.find_line_edit.text()
                self.find_line_edit.setEnabled(True)
            else:
                self.find = ''
                self.find_line_edit.setEnabled(False)
            filter_table()

        def populate_table():
            """Fill in the table."""
            for count, segment in enumerate(self.segments):
                self.generate_segment_tokens(segment)
                self.segments_table.add_item(
                        count, 0, str(count + 1).zfill(4))
                self.segments_table.add_item(
                        count, 1, self.get_parent_sequence(segment).name.get_value())
                self.segments_table.add_item(
                        count, 2, segment.name.get_value())
                self.segments_table.add_item(
                        count, 3, segment.record_in.timecode)
                self.segments_table.add_item(
                        count, 4, segment.record_out.timecode)
                self.segments_table.add_item(
                        count, 5, self.assemble_filename())

            verify_filename_column_exists()
            self.segments_table.resizeColumnsToContents()

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(1400, 600)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)

        # Mac needs this to close the window
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # FlameLineEdit class needs this
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()

        self.window.move(
                (resolution.width() / 2) - (self.window.frameSize().width() / 2),
                (resolution.height() / 2) - (self.window.frameSize().height() / 2))

        # Label
        self.preset_label = FlameLabel('Preset')
        self.path_label = FlameLabel('Path')
        self.pattern_label = FlameLabel('Pattern')

        # Line Edit
        self.path_line_edit = FlameLineEditFileBrowse(self.path, 'dir', self.window)
        self.path_line_edit.textChanged.connect(path_changed)

        self.pattern_line_edit = FlameLineEdit(self.pattern)
        self.pattern_line_edit.textChanged.connect(pattern_changed)

        self.find_line_edit = FlameLineEdit(self.find)
        self.find_line_edit.textChanged.connect(find_changed)

        # Table
        self.segments_table = FlameTableWidget(self.table_columns)
        self.segments_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        populate_table()
        filter_table()

        # Buttons
        self.btn_preset = FlamePushButtonMenu(
            get_selected_preset(), get_preset_names(), menu_action=update_preset)
        self.btn_preset.setMaximumSize(QtCore.QSize(4000, 28))  # span over to Save btn

        self.btn_preset_save = FlameButton('Save', preset_save_button, button_width=110)
        self.btn_preset_delete = FlameButton(
            'Delete', preset_delete_button, button_width=110)

        self.tokens_btn = FlameTokenPushButton(
            'Add Token',
            # self.segment_tokens is a dict with a nested set for each key
            # FlameTokenPushButton wants a dict that is only {token_name: token}
            # so need to simplify it with a dict comprehension
            {key: values[0] for key, values in self.segment_tokens.items()},
            self.pattern_line_edit)

        self.btn_find_segment = FlamePushButton(
            'Find Segment', self.window, bool(self.find), find_segment_button)

        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')
        self.ok_btn.setAutoDefault(True)  # doesnt make Enter key work
        self.cancel_btn = FlameButton('Close', close_button)

        # Finally before Layout
        find_toggle()

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setHorizontalSpacing(10)
        self.grid.setVerticalSpacing(10)

        self.grid.addWidget(self.preset_label, 0, 0)
        self.grid.addWidget(self.btn_preset, 0, 1)
        self.grid.addWidget(self.btn_preset_save, 0, 2)
        self.grid.addWidget(self.btn_preset_delete, 0, 3)
        self.grid.addWidget(self.path_label, 1, 0)
        self.grid.addWidget(self.path_line_edit, 1, 1)
        self.grid.addWidget(self.pattern_label, 2, 0)
        self.grid.addWidget(self.pattern_line_edit, 2, 1)
        self.grid.addWidget(self.tokens_btn, 2, 2)
        self.grid.addWidget(self.btn_find_segment, 3, 0)
        self.grid.addWidget(self.find_line_edit, 3, 1)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.segments_table)

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

        self.window.show()
        return self.window


def scope_timeline(selection):
    """Filter for only PyClips."""
    return any(isinstance(item, flame.PyClip) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add custom right click menu."""
    return [{'name': 'Apply...',
             'actions': [{'name': 'Text TimelineFX to Segments',
                          'isVisible': scope_timeline,
                          'execute': FindSegmentApplyText,
                          'minimumVersion': '2025'}]
            }]
