"""
Script Name: Go to Frame Number
Written By: Kieran Hanrahan

Script Version: 3.0.1
Flame Version: 2025

URL: http://github.com/khanrahan/go-to-frame-number

Creation Date: 10.26.22
Update Date: 04.10.25

Description:

    Takes one or more selected clips and/or sequences and moves the positioner to a
    specific frame number.

Menus:

    Right-click selected clips and/or sequences on the Desktop Reels --> Navigate... --> Go to Frame Number

    Right-click selected clips and/or sequences in the Media Panel --> Navigate... --> Go to Frame Number

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

TITLE = 'Go to Frame Number'
VERSION_INFO = (3, 0, 1)
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


class FlameSlider(QtWidgets.QLineEdit):
    """Custom Qt Flame Slider Widget v2.1

    start_value: int or float value
    min_value: int or float value
    max_value: int or float value
    value_is_float: bool value
    slider_width: (optional) default value is 110. [int]

    Usage:

        slider = FlameSlider(0, -20, 20, False)
    """

    def __init__(self, start_value, min_value, max_value, value_is_float=False, slider_width=110):

        super().__init__()
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumHeight(28)
        self.setMinimumWidth(slider_width)
        self.setMaximumWidth(slider_width)

        if value_is_float:
            self.spinbox_type = 'Float'
        else:
            self.spinbox_type = 'Interger'

        self.min = min_value
        self.max = max_value
        self.steps = 1
        self.value_at_press = None
        self.pos_at_press = None
        self.setValue(start_value)
        self.setReadOnly(True)
        self.textChanged.connect(self.value_changed)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setStyleSheet("""
            QLineEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: none;
                padding-left: 5px; font: 14px "Discreet"}
            QLineEdit:hover {
                border: 1px solid rgb(90, 90, 90)}
            QLineEdit:disabled {
                color: rgb(106, 106, 106);
                background-color: rgb(55, 65, 75)}
            QToolTip {
                color: rgb(170, 170, 170);
                background-color: rgb(71, 71, 71);
                border: 10px solid rgb(71, 71, 71)}""")
        self.clearFocus()

        class Slider(QtWidgets.QSlider):

            def __init__(self, start_value, min_value, max_value, slider_width):
                super().__init__()

                self.setMaximumHeight(4)
                self.setMinimumWidth(slider_width)
                self.setMaximumWidth(slider_width)
                self.setMinimum(min_value)
                self.setMaximum(max_value)
                self.setValue(start_value)
                self.setOrientation(QtCore.Qt.Horizontal)
                self.setStyleSheet("""
                    QSlider {
                        color: rgb(55, 65, 75);
                        background-color: rgb(39, 45, 53)}
                    QSlider::groove {
                        color: rgb(39, 45, 53);
                        background-color: rgb(39, 45, 53)}
                    QSlider::handle:horizontal {
                        background-color: rgb(102, 102, 102);
                        width: 3px}'
                    QSlider::disabled {
                        color: rgb(106, 106, 106);
                        background-color: rgb(55, 65, 75)}""")
                self.setDisabled(True)
                self.raise_()

        def set_slider():
            slider666.setValue(float(self.text()))

        slider666 = Slider(start_value, min_value, max_value, slider_width)
        self.textChanged.connect(set_slider)

        self.vbox = QtWidgets.QVBoxLayout(self)
        self.vbox.addWidget(slider666)
        self.vbox.setContentsMargins(0, 24, 0, 0)

    def calculator(self):
        from functools import partial

        def clear():
            calc_lineedit.setText('')

        def button_press(key):

            if self.clean_line:
                calc_lineedit.setText('')

            calc_lineedit.insert(key)

            self.clean_line = False

        def plus_minus():

            if calc_lineedit.text():
                calc_lineedit.setText(str(float(calc_lineedit.text()) * -1))

        def add_sub(key):

            if calc_lineedit.text() == '':
                calc_lineedit.setText('0')

            if '**' not in calc_lineedit.text():
                try:
                    calc_num = eval(calc_lineedit.text().lstrip('0'))

                    calc_lineedit.setText(str(calc_num))

                    calc_num = float(calc_lineedit.text())

                    if calc_num == 0:
                        calc_num = 1
                    if key == 'add':
                        self.setValue(float(self.text()) + float(calc_num))
                    else:
                        self.setValue(float(self.text()) - float(calc_num))

                    self.clean_line = True
                except:
                    pass

        def enter():

            if self.clean_line:
                return calc_window.close()

            if calc_lineedit.text():
                try:

                    # If only single number set slider value to that number

                    self.setValue(float(calc_lineedit.text()))
                except:

                    # Do math

                    new_value = calculate_entry()
                    self.setValue(float(new_value))

            close_calc()

        def equals():

            if calc_lineedit.text() == '':
                calc_lineedit.setText('0')

            if calc_lineedit.text() != '0':

                calc_line = calc_lineedit.text().lstrip('0')
            else:
                calc_line = calc_lineedit.text()

            if '**' not in calc_lineedit.text():
                try:
                    calc = eval(calc_line)
                except:
                    calc = 0

                calc_lineedit.setText(str(calc))
            else:
                calc_lineedit.setText('1')

        def calculate_entry():

            calc_line = calc_lineedit.text().lstrip('0')

            if '**' not in calc_lineedit.text():
                try:
                    if calc_line.startswith('+'):
                        calc = float(self.text()) + eval(calc_line[-1:])
                    elif calc_line.startswith('-'):
                        calc = float(self.text()) - eval(calc_line[-1:])
                    elif calc_line.startswith('*'):
                        calc = float(self.text()) * eval(calc_line[-1:])
                    elif calc_line.startswith('/'):
                        calc = float(self.text()) / eval(calc_line[-1:])
                    else:
                        calc = eval(calc_line)
                except:
                    calc = 0
            else:
                calc = 1

            calc_lineedit.setText(str(float(calc)))

            return calc

        def close_calc():
            calc_window.close()
            self.setStyleSheet("""
                QLineEdit {
                    color: rgb(154, 154, 154);
                    background-color: rgb(55, 65, 75);
                    selection-color: rgb(154, 154, 154);
                    selection-background-color: rgb(55, 65, 75);
                    border: none;
                    padding-left: 5px;
                    font: 14pt "Discreet"}
                QLineEdit:hover {
                    border: 1px solid rgb(90, 90, 90)}""")

        def revert_color():
            self.setStyleSheet("""
                QLineEdit {
                    color: rgb(154, 154, 154);
                    background-color: rgb(55, 65, 75);
                    selection-color: rgb(154, 154, 154);
                    selection-background-color: rgb(55, 65, 75);
                    border: none;
                    padding-left: 5px;
                    font: 14pt "Discreet"}
                QLineEdit:hover {8
                    border: 1px solid rgb(90, 90, 90)}""")
        calc_version = '1.2'
        self.clean_line = False

        calc_window = QtWidgets.QWidget()
        calc_window.setMinimumSize(QtCore.QSize(210, 280))
        calc_window.setMaximumSize(QtCore.QSize(210, 280))
        calc_window.setWindowTitle('pyFlame Calc %s' % calc_version)
        calc_window.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.Popup)
        calc_window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        calc_window.destroyed.connect(revert_color)
        calc_window.move(QtGui.QCursor.pos().x() - 110, QtGui.QCursor.pos().y() - 290)
        calc_window.setStyleSheet('background-color: rgb(36, 36, 36)')

        # Labels

        calc_label = QtWidgets.QLabel('Calculator', calc_window)
        calc_label.setAlignment(QtCore.Qt.AlignCenter)
        calc_label.setMinimumHeight(28)
        calc_label.setStyleSheet('''
            color: rgb(154, 154, 154);
            background-color: rgb(57, 57, 57);
            font: 14px "Discreet"''')

        #  LineEdit

        calc_lineedit = QtWidgets.QLineEdit('', calc_window)
        calc_lineedit.setMinimumHeight(28)
        calc_lineedit.setFocus()
        calc_lineedit.returnPressed.connect(enter)
        calc_lineedit.setStyleSheet("""
            QLineEdit {
                color: rgb(154, 154, 154);
                background-color: rgb(55, 65, 75);
                selection-color: rgb(38, 38, 38);
                selection-background-color: rgb(184, 177, 167);
                border: none;
                padding-left: 5px;
                font: 14px "Discreet"}""")

        # Limit characters that can be entered into lineedit

        regex = QtCore.QRegularExpression('[0-9_,=,/,*,+,\-,.]+')
        validator = QtGui.QRegularExpressionValidator(regex)
        calc_lineedit.setValidator(validator)

        # Buttons

        def calc_null():
            # For blank button - this does nothing
            pass

        class FlameButton(QtWidgets.QPushButton):
            """Custom Qt Flame Button Widget"""

            def __init__(self, button_name, size_x, size_y, connect, parent, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.setText(button_name)
                self.setParent(parent)
                self.setMinimumSize(size_x, size_y)
                self.setMaximumSize(size_x, size_y)
                self.setFocusPolicy(QtCore.Qt.NoFocus)
                self.clicked.connect(connect)
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
                        border: none}
                    QPushButton:disabled {
                        color: rgb(116, 116, 116);
                        background-color: rgb(58, 58, 58);
                        border: none}""")

        blank_btn = FlameButton('', 40, 28, calc_null, calc_window)
        blank_btn.setDisabled(True)
        plus_minus_btn = FlameButton('+/-', 40, 28, plus_minus, calc_window)
        plus_minus_btn.setStyleSheet('''
            color: rgb(154, 154, 154);
            background-color: rgb(45, 55, 68);
            font: 14px "Discreet"''')
        add_btn = FlameButton('Add', 40, 28, (partial(add_sub, 'add')), calc_window)
        sub_btn = FlameButton('Sub', 40, 28, (partial(add_sub, 'sub')), calc_window)

        #  --------------------------------------- #

        clear_btn = FlameButton('C', 40, 28, clear, calc_window)
        equal_btn = FlameButton('=', 40, 28, equals, calc_window)
        div_btn = FlameButton('/', 40, 28, (partial(button_press, '/')), calc_window)
        mult_btn = FlameButton('/', 40, 28, (partial(button_press, '*')), calc_window)

        #  --------------------------------------- #

        _7_btn = FlameButton('7', 40, 28, (partial(button_press, '7')), calc_window)
        _8_btn = FlameButton('8', 40, 28, (partial(button_press, '8')), calc_window)
        _9_btn = FlameButton('9', 40, 28, (partial(button_press, '9')), calc_window)
        minus_btn = FlameButton('-', 40, 28, (partial(button_press, '-')), calc_window)

        #  --------------------------------------- #

        _4_btn = FlameButton('4', 40, 28, (partial(button_press, '4')), calc_window)
        _5_btn = FlameButton('5', 40, 28, (partial(button_press, '5')), calc_window)
        _6_btn = FlameButton('6', 40, 28, (partial(button_press, '6')), calc_window)
        plus_btn = FlameButton('+', 40, 28, (partial(button_press, '+')), calc_window)

        #  --------------------------------------- #

        _1_btn = FlameButton('1', 40, 28, (partial(button_press, '1')), calc_window)
        _2_btn = FlameButton('2', 40, 28, (partial(button_press, '2')), calc_window)
        _3_btn = FlameButton('3', 40, 28, (partial(button_press, '3')), calc_window)
        enter_btn = FlameButton('Enter', 40, 61, enter, calc_window)

        #  --------------------------------------- #

        _0_btn = FlameButton('0', 89, 28, (partial(button_press, '0')), calc_window)
        point_btn = FlameButton('.', 40, 28, (partial(button_press, '.')), calc_window)

        gridbox = QtWidgets.QGridLayout()
        gridbox.setVerticalSpacing(5)
        gridbox.setHorizontalSpacing(5)

        gridbox.addWidget(calc_label, 0, 0, 1, 4)

        gridbox.addWidget(calc_lineedit, 1, 0, 1, 4)

        gridbox.addWidget(blank_btn, 2, 0)
        gridbox.addWidget(plus_minus_btn, 2, 1)
        gridbox.addWidget(add_btn, 2, 2)
        gridbox.addWidget(sub_btn, 2, 3)

        gridbox.addWidget(clear_btn, 3, 0)
        gridbox.addWidget(equal_btn, 3, 1)
        gridbox.addWidget(div_btn, 3, 2)
        gridbox.addWidget(mult_btn, 3, 3)

        gridbox.addWidget(_7_btn, 4, 0)
        gridbox.addWidget(_8_btn, 4, 1)
        gridbox.addWidget(_9_btn, 4, 2)
        gridbox.addWidget(minus_btn, 4, 3)

        gridbox.addWidget(_4_btn, 5, 0)
        gridbox.addWidget(_5_btn, 5, 1)
        gridbox.addWidget(_6_btn, 5, 2)
        gridbox.addWidget(plus_btn, 5, 3)

        gridbox.addWidget(_1_btn, 6, 0)
        gridbox.addWidget(_2_btn, 6, 1)
        gridbox.addWidget(_3_btn, 6, 2)
        gridbox.addWidget(enter_btn, 6, 3, 2, 1)

        gridbox.addWidget(_0_btn, 7, 0, 1, 2)
        gridbox.addWidget(point_btn, 7, 2)

        calc_window.setLayout(gridbox)

        calc_window.show()

    def value_changed(self):

        # If value is greater or less than min/max values set values to min/max

        if int(self.value()) < self.min:
            self.setText(str(self.min))
        if int(self.value()) > self.max:
            self.setText(str(self.max))

    def mousePressEvent(self, event):

        if event.buttons() == QtCore.Qt.LeftButton:
            self.value_at_press = self.value()
            self.pos_at_press = event.pos()
            self.setCursor(QtGui.QCursor(QtCore.Qt.SizeHorCursor))
            self.setStyleSheet("""
                QLineEdit {
                    color: rgb(217, 217, 217);
                    background-color: rgb(73, 86, 99);
                    selection-color: rgb(154, 154, 154);
                    selection-background-color: rgb(73, 86, 99);
                    border: none;
                    padding-left: 5px;
                    font: 14pt "Discreet"}
                QLineEdit:hover {
                    border: 1px solid rgb(90, 90, 90)}""")

    def mouseReleaseEvent(self, event):

        if event.button() == QtCore.Qt.LeftButton:

            # Open calculator if button is released within 10 pixels of button click

            if event.pos().x() in range((self.pos_at_press.x() - 10), (self.pos_at_press.x() + 10)) and event.pos().y() in range((self.pos_at_press.y() - 10), (self.pos_at_press.y() + 10)):
                self.calculator()
            else:
                self.setStyleSheet("""
                    QLineEdit {
                        color: rgb(154, 154, 154);
                        background-color: rgb(55, 65, 75);
                        selection-color: rgb(154, 154, 154);
                        selection-background-color: rgb(55, 65, 75);
                        border: none;
                        padding-left: 5px;
                        font: 14pt "Discreet"}
                    QLineEdit:hover {
                        border: 1px solid rgb(90, 90, 90)}""")

            self.value_at_press = None
            self.pos_at_press = None
            self.setCursor(QtGui.QCursor(QtCore.Qt.IBeamCursor))
            return

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() != QtCore.Qt.LeftButton:
            return

        if self.pos_at_press is None:
            return

        steps_mult = self.getStepsMultiplier(event)
        delta = event.pos().x() - self.pos_at_press.x()

        if self.spinbox_type == 'Float':
            delta /= 100  # adjust sensitivity
        delta *= self.steps * steps_mult

        value = self.value_at_press + delta
        self.setValue(value)

        super().mouseMoveEvent(event)

    def getStepsMultiplier(self, event):

        steps_mult = 1

        if event.modifiers() == QtCore.Qt.CTRL:
            steps_mult = 10
        elif event.modifiers() == QtCore.Qt.SHIFT:
            steps_mult = 0.10

        return steps_mult

    def setMinimum(self, value):

        self.min = value

    def setMaximum(self, value):

        self.max = value

    def setSteps(self, steps):

        if self.spinbox_type == 'Interger':
            self.steps = max(steps, 1)
        else:
            self.steps = steps

    def value(self):

        if self.spinbox_type == 'Interger':
            return int(self.text())
        else:
            return float(self.text())

    def setValue(self, value):

        if self.min is not None:
            value = max(value, self.min)

        if self.max is not None:
            value = min(value, self.max)

        if self.spinbox_type == 'Interger':
            self.setText(str(int(value)))
        else:
            # Keep float values to two decimal places

            self.setText('%.2f' % float(value))


class GoToFrameNumber:
    """For moving the positioner to a frame number on a selection of timelines.

    Attributes:
        frame: The destination frame number for the positioners stored as an integer.
        selection: Passed along by the Flame app.
        window_size: A dictorionary of the starting X & Y dimension of the window.
    """

    def __init__(self, selection):
        """Start it up!

        Args:
            selection: A list of the selected Flame PyClip or PySequence objects.
        """
        self.selection = selection

        self.frame = 1

        self.message(TITLE_VERSION)
        self.message(f'Script called from {__file__}')

        self.window_size = {'x': 360, 'y': 130}

        self.main_window()

    @staticmethod
    def message(string):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        print(' '.join([MESSAGE_PREFIX, string]))

    def go_to_frame(self):
        """Loop through the selections and move position to frame on each."""
        for clip in self.selection:
            clip.current_time = self.frame
            self.message(f'{clip.name.get_value()} positioner moved to '
                         f'frame {self.frame}')

    def main_window(self):
        """The only popup window."""

        def get_frame_number():
            """Store frame number."""
            self.frame = int(self.frame_slider.text())

        def okay_button():
            """Execute when ok is pressed."""
            self.go_to_frame()
            self.window.close()
            self.message('Done!')

        def cancel_button():
            """Execute when cancel is pressed."""
            self.window.close()
            self.message('Cancelled!')

        self.window = QtWidgets.QWidget()
        self.window.setMinimumSize(self.window_size['x'], self.window_size['y'])
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(TITLE_VERSION)

        # FlameLineEdit class needs this
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Labels
        self.frame_label = FlameLabel('Frame')

        # Slider
        self.frame_slider = FlameSlider(self.frame, 1, 9999, False)
        self.frame_slider.textChanged.connect(get_frame_number)

        # Buttons
        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')
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
        self.grid.setVerticalSpacing(10)
        self.grid.setHorizontalSpacing(10)

        self.grid.addWidget(self.frame_label, 0, 0)
        self.grid.addWidget(self.frame_slider, 0, 1)

        self.hbox03 = QtWidgets.QHBoxLayout()
        self.hbox03.addStretch(1)
        self.hbox03.addWidget(self.cancel_btn)
        self.hbox03.addWidget(self.ok_btn)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.grid)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox03)

        self.window.setLayout(self.vbox)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().screenGeometry()

        self.window.move(resolution.center().x() - self.window_size['x'] / 2,
                         resolution.center().y() - self.window_size['y'] / 2)

        self.window.show()

        return self.window


def scope_clip(selection):
    """Filter for timeline objects."""
    valid_objects = (
            flame.PyClip,
            flame.PySequence)

    return all(isinstance(item, valid_objects) for item in selection)


def get_media_panel_custom_ui_actions():
    """Python hook to add item to Media Panel or Desktop Reels right click menu."""
    return [{'name': 'Navigate...',
             'actions': [{'name': 'Go to Frame Number',
                          'isVisible': scope_clip,
                          'execute': GoToFrameNumber,
                          'minimumVersion': '2025.0.0.0',
                        }]
            }]
