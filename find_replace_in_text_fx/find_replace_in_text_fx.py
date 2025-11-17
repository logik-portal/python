"""
Script Name: Find and Replace in Text TimelineFX
Written by: Kieran Hanrahan

Script Version: 3.0.0
Flame Version: 2025

URL: http://github.com/khanrahan/find-replace-in-text-fx

Creation Date: 07.21.22
Update Date: 03.06.25

Description:

    This script will find a specified search string within a Text TimelineFX and
    replace that search term with something else without having to enter the Text
    editor.

    Works on segments or sequences containing Text TimelineFX.  For sequences, it will
    find all segments that have Text TimelineFX and perform the find & replace.

Menus:

    Right-click selected segments in a sequence -> Edit... -> Find and Replace in Text TimelineFX

    Right-click selected sequence or sequences -> Edit... -> Find and Replace in Text TimelineFX

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For a specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""


import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'Find and Replace in Text TimelineFX'
VERSION_INFO = (3, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
TITLE_VERSION = f'{TITLE} v{VERSION}'
MESSAGE_PREFIX = '[PYTHON]'

TEMP_SETUP = '/var/tmp/find_and_replace_in_text_timelinefx_temp'


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
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
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
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
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


class FlameProgressWindow(QtWidgets.QDialog):
    """Custom Qt Flame Progress Window

    FlameProgressWindow(window_title, num_to_do[, text=None, enable_done_button=False,
                        parent=None])

    window_title: text shown in top left of window ie. Rendering... [str]
    num_to_do: total number of operations to do [int]
    text: message to show in window [str]
    enable_cancel_button: enable cancel button, default is False [bool]

    Usage:
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

        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))

        self.setParent(parent)

        self.grid = QtWidgets.QGridLayout()

        self.main_label = FlameLabel(window_title, label_width=500)
        self.main_label.setStyleSheet('''
            color: rgb(154, 154, 154);
            font: 18px "Discreet"''')
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
        QtWidgets.QApplication.processEvents()

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


class FindReplaceInTextFX:
    """Find and replace some text within a Text timelineFX."""

    def __init__(self, selection, **kwargs):
        """Initialize!"""
        self.selection = selection
        self.target = kwargs['target']

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.find = ''
        self.replace = ''

        self.segments = []

        if self.target == 'segments':
            self.filter_segments()
        if self.target == 'sequences':
            self.filter_sequences()

        self.message(f'Found {len(self.segments)} segments with Text TimelineFX...')

        self.main_window()

    @staticmethod
    def get_parent_sequence(child):
        """Returns object of the container sequence for the given flame object."""
        parents = []

        while child:
            if isinstance(child, flame.PySequence):
                break
            child = child.parent
            parents.append(child)

        parent_sequence = parents[-1]
        return parent_sequence

    @staticmethod
    def save_text_timeline_fx(segment, setup_path):
        """Save out a TTG node setup."""
        for timeline_fx in segment.effects:
            if timeline_fx.type == 'Text':
                timeline_fx.save_setup(setup_path)

    @staticmethod
    def load_text_timeline_fx(segment, setup_path):
        """Load a TTG node setup to segment."""
        for timeline_fx in segment.effects:
            if timeline_fx.type == 'Text':
                timeline_fx.load_setup(setup_path)

    @staticmethod
    def add_timeline_fx(segment, effect_type):
        """Add Timeline FX of effect_type to segment."""
        segment.create_effect(effect_type)

    @staticmethod
    def remove_timeline_fx(segment, effect_type):
        """Remove Timeline FX of specified type from segment.

        You have to remove before you can load a setup.  The setup load will not
        overwrite.
        """
        for timeline_fx in segment.effects:
            if timeline_fx.type == effect_type:
                flame.delete(timeline_fx)

    @staticmethod
    def convert_to_ttg_text(string):
        """Returns TTG style string"""
        return ' '.join(str(ord(character)) for character in list(string))

    @staticmethod
    def message(string):
        """Print to the shell window."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def filter_segments(self):
        """Needed to filter the selection results of a segment.

        Flame API returns the segment or segments that are selected AND the timelineFX
        on those segments.
        """
        for item in self.selection:
            if isinstance(item, flame.PySegment):
                # hidden segments cause crash
                if not item.hidden.get_value():
                    for effect in item.effects:
                        if effect.type == 'Text':
                            self.segments.append(item)

    def filter_sequences(self):
        """Filter out just segments that have Text TimelineFX."""
        for timeline in self.selection:
            for version in timeline.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        # hidden segments cause crash
                        if not segment.hidden.get_value():
                            for effect in segment.effects:
                                if effect.type == 'Text':
                                    self.segments.append(segment)

    def find_and_write(self, ttg_node_file, find, replace):
        """Find strings to replace and write out new file.

        Takes a path to a ttg setup and searches for a string and replaces
        it.
        """
        ttg_node_file += '.ttg_node'  # append extension

        try:
            with open(ttg_node_file, newline='') as ttg:  # python3
                file_data = ttg.read()
        except TypeError:
            with open(ttg_node_file, 'rU') as ttg:  # python2.7
                file_data = ttg.read()

        new = file_data.replace(self.convert_to_ttg_text(find),
                                self.convert_to_ttg_text(replace))

        with open(ttg_node_file, 'w') as ttg:
            ttg.write(new)

    def process_segment(self, segment, find, replace):
        """Find and replace on a single segment object."""
        self.save_text_timeline_fx(segment, TEMP_SETUP)
        self.remove_timeline_fx(segment, 'Text')
        self.add_timeline_fx(segment, 'Text')
        self.find_and_write(TEMP_SETUP, find, replace)
        self.load_text_timeline_fx(segment, TEMP_SETUP)

    def main_window(self):
        """The only popup window."""

        def update_find():
            """Update object attribute with string from line edit."""
            self.find = self.find_line_edit.text()

        def update_replace():
            """Update object attribute with string from line edit."""
            self.replace = self.replace_line_edit.text()

        def okay_button():
            """Execute these when OK is pressed."""
            self.window.close()

            self.progress_window = FlameProgressWindow('Progress', len(self.segments))

            for segment in self.segments:
                if self.progress_window.cancelled:
                    break

                self.progress_window.set_text(
                        f'Replacing {self.find} with {self.replace} ' +
                        f'on {segment.name.get_value()} in ' +
                        f'{self.get_parent_sequence(segment).name.get_value()}')

                self.process_segment(segment, self.find, self.replace)

                self.progress_window.set_progress_value(
                        self.segments.index(segment) + 1)

            self.progress_window.close()

            if self.progress_window.cancelled:
                self.message('Cancelled!')
            else:
                self.message('Done!')

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(600, 130)
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

        # Labels
        self.find_label = FlameLabel('Find', 'normal')
        self.replace_label = FlameLabel('Replace', 'normal')

        # Line Edits
        self.find_line_edit = FlameLineEdit('')
        self.find_line_edit.textChanged.connect(update_find)
        self.replace_line_edit = FlameLineEdit('')
        self.replace_line_edit.textChanged.connect(update_replace)

        # Buttons
        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')
        self.cancel_btn = FlameButton('Cancel', self.window.close)

        # Layout
        self.grid = QtWidgets.QGridLayout()
        self.grid.setVerticalSpacing(10)
        self.grid.setHorizontalSpacing(10)

        self.grid.addWidget(self.find_label, 0, 0)
        self.grid.addWidget(self.find_line_edit, 0, 1)
        self.grid.addWidget(self.replace_label, 1, 0)
        self.grid.addWidget(self.replace_line_edit, 1, 1)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addStretch(1)
        self.hbox.addWidget(self.cancel_btn)
        self.hbox.addWidget(self.ok_btn)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.grid)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox)

        self.window.setLayout(self.vbox)
        self.window.show()

        return self.window


def find_replace_segments(selection):
    """Call the class with a target destination."""
    FindReplaceInTextFX(selection, target='segments')


def find_replace_sequences(selection):
    """Call the class with a target destination."""
    FindReplaceInTextFX(selection, target='sequences')


def scope_timeline(selection):
    """Return True if selection is a sequence."""
    return all(isinstance(item, flame.PySequence) for item in selection)


def scope_timeline_segment(selection):
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
    """Add right click menu items for the Media Panel."""
    return [{'name': 'Edit...',
             'actions': [{'name': 'Find and Replace in Text TimelineFX',
                          'isVisible': scope_timeline,
                          'execute': find_replace_sequences,
                          'minimumVersion': '2025.0.0.0'}]
            }]


def get_timeline_custom_ui_actions():
    """Add right click menu items for the Timeline."""
    return [{'name': 'Edit...',
             'actions': [{'name': 'Find and Replace in Text TimelineFX',
                          'isVisible': scope_timeline_segment,
                          'execute': find_replace_segments,
                          'minimumVersion': '2025.0.0.0'}]
            }]
