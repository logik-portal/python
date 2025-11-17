"""
Script Name: Find & Replace in Name Advance
Written By: Kieran Hanrahan

Script Version: 3.1.0
Flame Version: 2025

URL: http://github.com/khanrahan/find-replace-in-name-advance

Creation Date: 02.21.24
Update Date: 04.10.25

Description:

    Perform find & replace on names of selected items.  Functions on Workspaces,
    Libraries, Desktops, Reel Groups, Reels, Folders, Sequences, Clips, and Timeline
    Segments.

Menus:

    Right-click selected items on the Desktop --> Edit... --> Find & Replace in Name Advance

    Right-click selected items in the Media Panel --> Edit... --> Find & Replace in Name Advance

    Right-click selected items in the Timeline --> Edit... --> Find & Replace in Name Advance

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
import xml.etree.ElementTree as ETree
from functools import partial

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Find and Replace in Name Advance'
VERSION_INFO = (3, 1, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'

MESSAGE_PREFIX = '[PYTHON]'
FOLDER_NAME = 'Edit...'
PRESET_FOLDER = '~/.config/find-and-replace-in-name-advance'
XML = 'find_replace_in_name_advance.xml'


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
    """Custom Qt Flame List Widget

    To use:
    list_widget = FlameListWidget(window)
    """

    def __init__(self, parent_window, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setMinimumSize(500, 250)
        self.setParent(parent_window)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        # only want 1 selection possible.  no multi selection.
        # self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.setSpacing(3)
        self.setAlternatingRowColors(True)
        self.setUniformItemSizes(True)
        self.setStyleSheet("""
            QListWidget {
                color: #9a9a9a;
                background-color: #2a2a2a;
                alternate-background-color: #2d2d2d;
                outline: none;
                font: 14px "Discreet"}
            QListWidget::item:selected {
                color: #d9d9d9;
                background-color: #474747}""")


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

        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

        self.main_label = FlameLabel(message_title, 'normal', label_width=500)
        self.main_label.setStyleSheet('''
            color: rgb(154, 154, 154);
            font: 18px "Discreet"''')

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
                font: 12px "Discreet"}""")

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


class FlameTokenPushButton(QtWidgets.QPushButton):
    """Custom Qt Flame Token Push Button Widget v2.2

    button_name: Text displayed on button [str]
    token_dict: Dictionary defining tokens. {'Token Name': '<Token>'} [dict]
    token_dest: LineEdit that token will be applied to [object]
    button_width: (optional) default is 150 [int]
    button_max_width: (optional) default is 300 [int]
    sort: (optional) sort the tokens before displaying [bool]

    Usage:

        token_dict = {'Token 1': '<Token1>', 'Token2': '<Token2>'}
        token_push_button = FlameTokenPushButton('Add Token', token_dict, token_dest)
    """

    def __init__(self, button_name, token_dict, token_dest, button_width=110,
                 button_max_width=300, sort=False):
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
                font: 14px "Discreet";
                padding-left: 6px;
                text-align: left}
            QPushButton:hover {
                border: 1px solid rgb(90, 90, 90)}
            QPushButton:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(45, 55, 68);
                border: none}
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

            if sort:
                # Sort by key. Lowercase precedes uppercase, before moving to next
                # letter.  For example...  aa, AA, bb, BB, cc, CC.
                tokens = sorted(token_dict.items(), key=lambda item: (item[0].upper(),
                                item[0].isupper()))
            else:
                tokens = [(key, value) for key, value in token_dict.items()]

            for name, token in tokens:
                del token
                token_menu.addAction(name, partial(insert_token, name))

        token_menu = QtWidgets.QMenu(self)
        token_menu.setFocusPolicy(QtCore.Qt.NoFocus)
        token_menu.setStyleSheet("""
            QMenu {
                color: rgb(154, 154, 154);
                background-color: rgb(45, 55, 68);
                border: none; font: 14px "Discreet"}
            QMenu::item:selected {
                color: rgb(217, 217, 217);
                background-color: rgb(58, 69, 81)}""")

        self.setMenu(token_menu)

        token_action_menu()


class FindReplace:
    """Find and replace in name for selected objects in Flame.

    Desktop & Media Panel supported objects:
        PyWorkspace
        PyLibrary
        PyDesktop
        PyReelGroup
        PyReel
        PyFolder
        PySequence
        PyClip

    Timeline supported objects:
        PySegment
    """

    def __init__(self, selection, target=None):
        """Create FindReplace object with necessary starting values."""
        self.selection = selection
        self.target = target

        if target == 'Timeline':
            self.filter_selection()

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        # Load settings (includes the presets)
        self.settings_xml_folder = os.path.expanduser(PRESET_FOLDER)
        self.settings_xml_file = os.path.join(self.settings_xml_folder, XML)

        self.settings_xml_tree = None
        self.load_settings_tree()

        self.settings_xml_root = None
        self.get_settings_root()

        self.settings_xml_presets = None
        self.get_settings_presets()

        # Tokens
        self.now = dt.datetime.now()

        self.tokens_generic = {}
        self.generate_tokens_generic()

        self.tokens_unique = []
        self.generate_tokens_unique()

        # Find
        self.find = None
        self.load_find()
        self.find_regex = None
        self.find_convert_wildcards_to_regex()

        # Replace
        self.replace = None
        self.load_replace()
        self.replace_resolved = None
        self.replace_resolve_tokens()

        # Selection Names
        self.names = None
        self.get_names()
        self.names_new = None
        self.get_names_new()

        # Wildcards
        self.wildcards = {
                'Match All': '*', 'Match Any': '?', 'Match Start': '^',
                'Match End': '$'}

        # Save Window
        self.save_window_dimensions = {'x': 500, 'y': 100}

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    @staticmethod
    def refresh():
        """Refresh the flame UI.

        Necessary after changing attributes to have the changes show up on the
        Desktop.  Otherwise, the script runs, but the change will not be shown on the
        thumbnail until you tap on the UI.
        """
        flame.execute_shortcut('Refresh Thumbnails')

    def filter_selection(self):
        """Remove PyTransition objects from the selection.

        This is necessary because its convenient for the user to just do a shift + left
        click range selection of segments on the timeline, but this will also include
        the transitions between each segment which we do not want to rename.
        """
        self.selection = tuple([item for item in self.selection
                                if not isinstance(item, flame.PyTransition)])

    def load_settings_tree(self):
        """Load preset file if preset and store XML tree & root."""
        if os.path.isfile(self.settings_xml_file):
            self.settings_xml_tree = ETree.parse(self.settings_xml_file)
        else:
            settings = ETree.Element('settings')

            name = ETree.SubElement(settings, 'script_name')
            name.text = TITLE

            version = ETree.SubElement(name, 'version')
            version.text = VERSION

            presets = ETree.SubElement(version, 'presets')
            self.settings_xml_tree = ETree.ElementTree(settings)

    def get_settings_root(self):
        """Store the root object for the ElementTree of settings."""
        self.settings_xml_root = self.settings_xml_tree.getroot()

    def get_settings_presets(self):
        """Store the element object for the ElementTree of settings."""
        self.settings_xml_presets = self.settings_xml_root.find(
                'script_name/version/presets')

    def load_preset_by_index_element(self, index, element):
        """Convert None to empty string.

        ElementTree saves empty string as None.
        """
        preset_element = (
            self.settings_xml_presets.findall('preset')[index].find(element).text)

        if preset_element is None:
            preset_element = ''

        return preset_element

    def load_find(self):
        """Load the first preset's find pattern or leave blank."""
        if self.settings_xml_presets.findall('preset'):
            self.find = self.load_preset_by_index_element(0, 'find')
        else:
            self.find = ''

    def find_convert_wildcards_to_regex(self):
        """Convert wildcards to regex.

        Split the find based on the available wildcards, then replace with their
        corresponding regex.  The resulting regex is then appropriate to use with
        re.sub.
        """
        find_split = re.split(r'([\^\*\?\$])', self.find)

        self.find_regex = ''

        for regex_piece in find_split:
            if regex_piece == '^':
                self.find_regex += '^'
            elif regex_piece == '*':
                self.find_regex += '^$|.+'
            elif regex_piece == '?':
                self.find_regex += '.'
            elif regex_piece == '$':
                self.find_regex += '$'
            else:
                self.find_regex += f'{re.escape(regex_piece)}'

    def load_replace(self):
        """Load the first preset's replace pattern or leave blank."""
        if self.settings_xml_presets.findall('preset'):
            self.replace = self.load_preset_by_index_element(0, 'replace')
        else:
            self.replace = ''

    def generate_tokens_generic(self):
        """Populate the token list."""
        self.tokens_generic['am/pm'] = [
                '<pp>', self.now.strftime('%p').lower()]
        self.tokens_generic['AM/PM'] = [
                '<PP>', self.now.strftime('%p').upper()]
        self.tokens_generic['Day'] = [
                '<DD>', self.now.strftime('%d')]
        self.tokens_generic['Hour (12hr)'] = [
                '<hh>', self.now.strftime('%I')]
        self.tokens_generic['Hour (24hr)'] = [
                '<HH>', self.now.strftime('%H')]
        self.tokens_generic['Minute'] = [
                '<mm>', self.now.strftime('%M')]
        self.tokens_generic['Month'] = [
                '<MM>', self.now.strftime('%m')]
        self.tokens_generic['Project'] = [
                '<project>', flame.project.current_project.name]
        self.tokens_generic['User'] = [
                '<user>', flame.users.current_user.name]
        self.tokens_generic['Year (YYYY)'] = [
                '<YYYY>', self.now.strftime('%Y')]
        self.tokens_generic['Year (YY)'] = [
                '<YY>', self.now.strftime('%y')]

    def get_token_colour_space(self, item):
        """Get the item's color space.

        Args:
            item: Flame python object such PyClip, etc

        Returns:
            str or None
        """
        try:
            token = item.get_colour_space()
        except TypeError:
            token = None
        return token

    def get_token_shot_name(self, item):
        """Get the item's shot name.

        Args:
            item: Flame python object such PyClip, etc

        Returns:
            str or None
        """
        try:
            token = item.shot_name.get_value()
        except TypeError:
            token = None
        return token

    def generate_tokens_unique(self):
        """Determine which unique tokens to generate and generate them!

        For example, Media Panel objects would have a different set of tokens available
        compared to Timeline objects.
        """
        if self.target == 'Media Panel':
            self.generate_tokens_media_panel()
        if self.target == 'Timeline':
            self.generate_tokens_timeline()

    def generate_tokens_media_panel(self):
        """Populate the token list."""
        for item in self.selection:
            obj_tokens = {}
            obj_tokens['Colour Space'] = [
                    '<colour space>', self.get_token_colour_space(item)]
            self.tokens_unique.append(obj_tokens)

    def generate_tokens_timeline(self):
        """Populate the token list."""
        for item in self.selection:
            obj_tokens = {}
            obj_tokens['Shot Name'] = ['<shot name>', self.get_token_shot_name(item)]
            self.tokens_unique.append(obj_tokens)

    def replace_sanitize(self):
        """Replace invalid characters with an underscore.

        Mimics Flame's standard behavior of replacing illegal characters with
        underscores.  Its a very specific selection of symbols, not all.
        """
        self.replace = re.sub(r'[`|/\\+*\';]', '_', self.replace)

    def replace_resolve_tokens(self):
        """Replace tokens with values."""
        results = []

        for index, item in enumerate(self.selection):
            del item
            result = self.replace
            tokens_combined = {**self.tokens_generic, **self.tokens_unique[index]}

            for name, [token, value] in tokens_combined.items():
                del name
                if value is None:
                    value = ''
                result = re.sub(token, value, result)
            results.append(result)

        self.replace_resolved = results

    def get_names(self):
        """Store the original names of the selection in a list."""
        self.names = [item.name.get_value() for item in self.selection]

    def get_names_new(self):
        """Generate the new names."""
        self.names_new = [re.sub(self.find_regex, self.replace_resolved[index], item)
                          for index, item in enumerate(self.names)]

    def update_names(self):
        """Change names of the names of the selected objects, skip if unnecesary.

        Relies on 3 lists:
            self.selection = selected objects
            self.names = names of the select objects
            self.names_new = new names of the above objects after search and replace
        """
        for num, clip in enumerate(self.selection):
            if self.names[num] == self.names_new[num]:
                self.message(f'Skipping {self.names[num]}. No change to name.')
                continue

            clip.name.set_value(self.names_new[num])
            self.message(f'Renamed {self.names[num]} to {self.names_new[num]}')

    def save_preset_window(self, preset_name):
        """Smaller window with save dialog.

        Args:
        preset_name: str: Initial name to display in the Preset Name field.
        """

        def duplicate_check():
            """Check that preset to be saved would not be a duplicate."""
            duplicate = False
            preset_name = self.line_edit_preset_name.text()

            for preset in self.settings_xml_presets.findall('preset'):
                if preset.find('name').text == preset_name:
                    duplicate = True

            return duplicate

        def check_preset_folder():
            """Check that destination folder for preset XML file is available."""
            result = False

            if os.path.exists(self.settings_xml_folder):
                result = True
            else:
                try:
                    os.makedirs(self.settings_xml_folder)
                    result = True
                except OSError:
                    FlameMessageWindow(
                        'Error', 'error',
                        f'Could not create {self.settings_xml_folder}')
            return result

        def save_preset():
            """Save new preset to XML file."""
            new_preset = ETree.Element('preset')

            new_name = ETree.SubElement(new_preset, 'name')
            new_name.text = self.line_edit_preset_name.text()

            new_find = ETree.SubElement(new_preset, 'find')
            new_find.text = self.find

            new_replace = ETree.SubElement(new_preset, 'replace')
            new_replace.text = self.replace

            self.settings_xml_presets.append(new_preset)
            sort_presets()

            if check_preset_folder():
                try:
                    self.settings_xml_tree.write(self.settings_xml_file)
                    self.message(f'{self.line_edit_preset_name.text()} ' +
                                 f'preset saved to  {self.settings_xml_file}')
                except OSError:  # removed IOError based on linter rule UP024
                    FlameMessageWindow(
                        'Error', 'error',
                        f'Check permissions on {self.settings_xml_file}')

        def overwrite_preset():
            """Replace pattern in presets XML tree then save to XML file."""
            preset_name = self.line_edit_preset_name.text()

            for preset in self.settings_xml_presets.findall('preset'):
                if preset.find('name').text == preset_name:
                    preset.find('find').text = self.find
                    preset.find('replace').text = self.replace

            try:
                self.settings_xml_tree.write(self.settings_xml_file)
                self.message(f'{self.line_edit_preset_name.text()} preset saved to ' +
                             f'{self.settings_xml_file}')
            except OSError:  # removed IOError based on linter rule UP024
                FlameMessageWindow(
                    'Error', 'error',
                    f'Check permissions on {self.settings_xml_file}')

        def sort_presets():
            """Alphabetically sort presets by name attribute."""
            self.settings_xml_presets[:] = sorted(
                self.settings_xml_presets,
                key=lambda preset: preset.find('name').text)

        def save_button():
            """Triggered when the Save button at the bottom is pressed."""
            duplicate = duplicate_check()

            if duplicate and FlameMessageWindow(
                    'Overwrite Existing Preset', 'confirm', 'Are you '
                    + 'sure want to permanently overwrite this preset?' + '<br/>'
                    + 'This operation cannot be undone.'):
                overwrite_preset()
                self.btn_preset.populate_menu(
                    [preset.find('name').text for preset in
                     self.settings_xml_presets.findall('preset')])
                self.btn_preset.setText(self.line_edit_preset_name.text())
                self.save_window.close()

            if not duplicate:
                save_preset()
                self.btn_preset.populate_menu(
                    [preset.find('name').text for preset in
                     self.settings_xml_presets.findall('preset')])
                self.btn_preset.setText(self.line_edit_preset_name.text())
                self.save_window.close()

        def cancel_button():
            """Triggered when the Cancel button at the bottom is pressed."""
            self.save_window.close()

        self.save_window = QtWidgets.QWidget()

        self.save_window.setMinimumSize(
                self.save_window_dimensions['x'], self.save_window_dimensions['y'])

        self.save_window.setStyleSheet('background-color: #272727')
        self.save_window.setWindowTitle('Save Preset As...')

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.save_window.move(
            (resolution.width() / 2) - (self.save_window_dimensions['x'] / 2),
            (resolution.height() / 2) - (self.save_window_dimensions['y'] / 2 + 44))

        # Labels
        self.label_preset_name = FlameLabel('Preset Name', 'normal')
        self.label_preset_pattern = FlameLabel('Pattern', 'normal')

        # Line Edits
        self.line_edit_preset_name = FlameLineEdit(preset_name)

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
        """The primary window."""

        def get_all_tokens():
            """Assemble token names & <tokens>.

            FlameTokenPushButton wants a dict that is only {name: <token>} so need to
            simplify it with a dict comprehension.
            """
            tokens_generic = {
                    key: values[0] for key, values in self.tokens_generic.items()}
            tokens_unique = {
                    key: values[0] for key, values in self.tokens_unique[0].items()}
            return {**tokens_generic, **tokens_unique}

        def get_preset_names():
            """Return just the names of the presets."""
            try:
                preset_names = [
                    preset.find('name').text for preset in
                    self.settings_xml_presets.findall('preset')]
            except IndexError:  # if findall() returns empty list
                preset_names = []

            return preset_names

        def get_selected_preset():
            """Get preset that should be displayed or return empty string."""
            try:
                selected_preset = get_preset_names()[0]
            except IndexError:
                selected_preset = ''

            return selected_preset

        def update_preset():
            """Update fields when preset is changed."""
            preset_name = self.btn_preset.text()

            if preset_name:  # might be empty str if all presets were deleted
                for preset in self.settings_xml_presets.findall('preset'):
                    if preset.find('name').text == preset_name:
                        self.line_edit_find.setText(preset.find('find').text)
                        self.line_edit_replace.setText(preset.find('replace').text)
                        break  # should not be any duplicates

        def preset_delete_button():
            """Triggered when the Delete button on the Preset line is pressed."""
            if FlameMessageWindow(
                    'Confirm Operation', 'confirm', 'Are you sure want to'
                    + ' permanently delete this preset?' + '<br/>' + 'This operation'
                    + ' cannot be undone.'):
                preset_name = self.btn_preset.text()

                for preset in self.settings_xml_presets.findall('preset'):
                    if preset.find('name').text == preset_name:
                        self.settings_xml_presets.remove(preset)
                        self.message(f'{preset_name} preset deleted from ' +
                                     f'{self.settings_xml_file}')

                self.settings_xml_tree.write(self.settings_xml_file)

            # Reload presets button
            self.load_settings_tree()
            self.get_settings_root()
            self.get_settings_presets()
            self.btn_preset.populate_menu(get_preset_names())
            self.btn_preset.setText(get_selected_preset())
            update_preset()

        def preset_save_button():
            """Triggered when the Save button the Presets line is pressed."""
            self.save_preset_window(self.btn_preset.text())

        def update_find():
            """Everything to update when find is changed."""
            self.find = self.line_edit_find.text()

            self.find_convert_wildcards_to_regex()
            self.get_names_new()
            self.list_names.clear()

            # display final names
            if self.find:
                self.list_names.addItems(self.names_new)

            # or return to starting state
            if not self.find:
                self.list_names.addItems(self.names)

        def update_replace():
            """Everything to update when replace is changed."""
            # the below .encode is necessary because otherwise it will return unicode
            # and PyClip.name.set_value() does not take unicode
            self.replace = self.line_edit_replace.text()

            self.replace_sanitize()
            self.replace_resolve_tokens()

            if self.find:
                self.get_names_new()
                self.list_names.clear()
                self.list_names.addItems(self.names_new)

        def ok_button():

            self.window.close()
            self.update_names()
            self.refresh()
            self.message('Done!')

        def cancel_button():

            self.window.close()
            self.message('Cancelled!')

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(800, 130)
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)

        # Mac needs this to close the window
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.window.move(
                (resolution.width() / 2) - (self.window.frameSize().width() / 2),
                (resolution.height() / 2) - (self.window.frameSize().height() / 2))

        # Labels
        self.label_preset = FlameLabel('Preset', 'normal')
        self.label_find = FlameLabel('Find ', 'normal')
        self.label_replace = FlameLabel('Replace ', 'normal')

        # Line Edits
        self.line_edit_find = FlameLineEdit(self.find)
        self.line_edit_find.textChanged.connect(update_find)

        self.line_edit_replace = FlameLineEdit(self.replace)
        self.line_edit_replace.textChanged.connect(update_replace)

        # Buttons
        self.btn_preset = FlamePushButtonMenu(
            get_selected_preset(), get_preset_names(), menu_action=update_preset)
        self.btn_preset.setMaximumSize(QtCore.QSize(4000, 28))  # span over to Save btn

        self.btn_preset_save = FlameButton(
                'Save', preset_save_button, button_width=110)
        self.btn_preset_delete = FlameButton(
                'Delete', preset_delete_button, button_width=110)

        self.btn_wildcards = FlameTokenPushButton(
                'Add Wildcard', self.wildcards, self.line_edit_find, sort=True)
        self.btn_tokens = FlameTokenPushButton(
                'Add Token', get_all_tokens(), self.line_edit_replace, sort=True)

        self.btn_ok = FlameButton('Ok', ok_button, button_color='blue')
        self.btn_cancel = FlameButton('Cancel', cancel_button)

        # List
        self.list_names = FlameListWidget(self.window)
        self.list_names.addItems(self.names_new)

        # Shortcuts
        self.shortcut_enter = QtGui.QShortcut(
                QtGui.QKeySequence('Enter'), self.btn_ok, ok_button)
        self.shortcut_escape = QtGui.QShortcut(
                QtGui.QKeySequence('Escape'), self.btn_cancel, cancel_button)
        self.shortcut_return = QtGui.QShortcut(
                QtGui.QKeySequence('Return'), self.btn_ok, ok_button)

        # Layout
        self.gridbox = QtWidgets.QGridLayout()
        self.gridbox.setVerticalSpacing(10)
        self.gridbox.setHorizontalSpacing(10)

        self.gridbox.addWidget(self.label_preset, 0, 0)
        self.gridbox.addWidget(self.btn_preset, 0, 1)
        self.gridbox.addWidget(self.btn_preset_save, 0, 2)
        self.gridbox.addWidget(self.btn_preset_delete, 0, 3)
        self.gridbox.addWidget(self.label_find, 1, 0)
        self.gridbox.addWidget(self.line_edit_find, 1, 1)
        self.gridbox.addWidget(self.btn_wildcards, 1, 2)
        self.gridbox.addWidget(self.label_replace, 2, 0)
        self.gridbox.addWidget(self.line_edit_replace, 2, 1)
        self.gridbox.addWidget(self.btn_tokens, 2, 2)

        self.hbox1 = QtWidgets.QHBoxLayout()
        self.hbox1.addSpacing(50)
        self.hbox1.addWidget(self.list_names)
        self.hbox1.addSpacing(50)

        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addStretch(1)
        self.hbox2.addWidget(self.btn_cancel)
        self.hbox2.addWidget(self.btn_ok)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.gridbox)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox1)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox2)

        self.window.setLayout(self.vbox)

        # Tab Order
        self.window.setTabOrder(self.line_edit_find, self.line_edit_replace)
        self.window.setTabOrder(self.line_edit_replace, self.line_edit_find)

        # Focus
        self.line_edit_find.setFocus()

        self.window.show()
        return self.window


def find_replace_media_panel(selection):
    """Call class with Media Panel target."""
    FindReplace(selection, target='Media Panel')


def find_replace_timeline(selection):
    """Call class with Timeline target."""
    FindReplace(selection, target='Timeline')


def scope_selection_media_panel(selection):
    """Return bool for whether selection contains only valid objects."""
    valid_objects = (
            flame.PyClip,
            flame.PySequence,
            flame.PyDesktop,
            flame.PyFolder,
            flame.PyLibrary,
            flame.PyReel,
            flame.PyReelGroup,
            flame.PyWorkspace)

    return all(isinstance(item, valid_objects) for item in selection)


def scope_selection_timeline(selection):
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


def get_media_panel_custom_ui_actions():
    """Python hook to add item to the Desktop/Media Panel right click menu."""
    return [{'name': FOLDER_NAME,
             'actions': [{'name': TITLE,
                          'isVisible': scope_selection_media_panel,
                          'execute': find_replace_media_panel,
                          'minimumVersion': '2025'}]
           }]


def get_timeline_custom_ui_actions():
    """Python hook to add item to the Timeline right click menu."""
    return [{'name': FOLDER_NAME,
             'actions': [{'name': TITLE,
                          'isVisible': scope_selection_timeline,
                          'execute': find_replace_timeline,
                          'minimumVersion': '2025'}]
           }]
