"""
Script Name: PySlater for Flame
Script Version: 2.0.0
Flame Version: 2025
Written By: Kieran Hanrahan
Creation Date: 10.19.23
Update Date: 03.04.25

Description:

    Menu for using PySlater class from within the Flame application.

    URL: http://github.com/khanrahan/pyslater-for-flame

Menus:

    Flame Menu (the fish) > Slates... > PySlater for Flame

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python/

    For a specific user on Linux, copy this file to:
    /home/<user_name>/flame/python/

    For specific user on Mac, copy this file to:
    /Users/<user_name>/Library/Preferences/Autodesk/flame/python/
"""

import csv
import errno
import fnmatch
import os
import re
import sys

import flame
from PySide6 import QtCore, QtGui, QtWidgets

TITLE = 'PySlater for Flame'
VERSION_INFO = (2, 0, 0)
VERSION = '.'.join([str(num) for num in VERSION_INFO])
VERSION_TITLE = f'{TITLE} v{VERSION}'

MESSAGE_PREFIX = '[PYTHON]'

DEFAULT_TEMPLATE = 'templates/default_template_16x9.ttg'
DEFAULT_OUTPUT_TTG = '<Spot Code>_<Duration>_<Title>.ttg'
GSHEET = 'https://docs.google.com/spreadsheets/d/1Sx1WKpJlonNEdL-JeLzsJ6ybL6GxgHXP3RXasoQ8fB4/edit?usp=sharing'
HTML_TEMPLATE = 'template/template.html'
HTML_FILENAME = 'copy_paster.html'
SETUPS_ROOT = '/opt/Autodesk/project'


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

    To use:

    lineedit:
        FlameLineEditFileBrowse('some_path', 'Python (*.py)', window)
    file_path:
        Path browser will open to. If set to root folder (/), browser will open to user
        home directory
    filter_type:
        Type of file browser will filter_type for. If set to 'dir', browser will select
        directory
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


class PySlater:
    """Generate slates as TTG files using CSV data.

    Optionally, also generate an HTML to provide spot names using the same data.
    """

    def __init__(self, csv_file, output, dry_run=False, html=True, filter_include=None,
                 filter_exclude=None, force_overwrite=False, message=None,
                 row_header=1, row_exclude=None, row_include=None, skip_existing=False,
                 template_html=None, template_ttg=None):
        """Initialize a PySlater.

        Args:
            csv_file:
                A string representing a CSV file of slate data.
            dry_run:
                A bool for whether or not to acually write files.  A dry_run (true) will
                not write any files.
            filter_include:
                A list of search strings to match which lines to include.
                Example ['*foo*', '*bar*']
            filter_exclude:
                A list of search strings to match which lines to exclude.
                Example ['*foo*', '*bar*']
            force_overwrite:
                A bool for whether on not to overwrite existing TTGs.
            html:
                A bool for whether or not to generate the HTML to aid in naming.
            output:
                A string of the output path for the generated TTGs.  Accepts tokens
                wrapped in <> that match column names in the CSV.
            message:
                A function default to print or instead use this function for messages.
            row_header:
                An integer repesenting the location of the column titles in the CSV.
                Index of 1.
            row_exclude:
                A string of rows to exclude by #. Index of 1. Single and/or a range.
                Example '1,3-17,87'
            row_include:
                A string of rows to include by #. Index of 1. Single and/or a range.
                Example '1,3-17,87'
            skip_existing:
                A bool for whether or not to skip overwriting existing files.
            template_html:
                A string containing an HTML template file to populate with result TTG
                names.
            template_ttg:
                A string containing an TTG template file to populate with data from the
                CSV.
        """
        self.script_path = self.get_script_path()

        # Default Args
        self.csv_file = csv_file
        self.output = self.expand_path(output)  # should this go to argparse?

        # Optional Args
        self.dry_run = dry_run
        self.filter_include = filter_include or []
        self.filter_exclude = filter_exclude or []
        self.force_overwrite = force_overwrite
        self.html = html
        self.message = message or print
        self.row_header = row_header  # index based on 1
        self.row_include = self.expand_row_notation(row_include) if row_include else []
        self.row_exclude = self.expand_row_notation(row_exclude) if row_exclude else []
        self.skip_existing = skip_existing
        self.template_html = template_html or self.get_template_html()
        self.template_ttg = template_ttg

        # Generated Args at self.run()
        self.csv_rows = ()
        self.filepath_pattern = ''
        self.template_ttg_rows = []  # why is this not a tuple too?
        self.template_ttg_keywords = {}

        # Args for each Slate
        self.filepath = ''
        self.reply = ''
        self.row = []
        self.row_number = 0
        self.ttg_replacements = {}

        # HTML Args
        self.template_html_rows = ()
        self.destination_html = ''

        # Results
        self.results = []

    @staticmethod
    def common_path(paths):
        """Returns common parent directory from list of paths.

        Not necessary in Python 3.5 because of os.path.commonpath()
        """
        return os.path.dirname(os.path.commonprefix(paths))

    @staticmethod
    def convert_from_ttg_text(decimal_string):
        """Convert from TTG formatting to string.

        Returns unicode standard string minus the 'Text' at the beginning
        and the <> keyword wrappers
        """
        return ''.join(chr(int(character)) for character in
                       decimal_string.split()[2:-1])

    @staticmethod
    def convert_to_ttg_text(string):
        """Returns TTG style string."""
        return ' '.join(str(ord(character)) for character in list(string))

    @staticmethod
    def filename_no_ext(filepath):
        """Return just filename without extension."""
        return os.path.splitext(os.path.basename(filepath))[0]

    @staticmethod
    def find_ttg_keywords(ttg_file_list):
        """Return dict of line numbers and token replacement values.

        Returns dictionary containing the line number and contents
        for the keywords that are wrapped in greater/less than symbols aka
        angle brackets.  Angle brackets follow Flame convention for tokens.
        60 = <
        62 = >

        NOTE - will return empty dictionary if ttg_file_list is empty list.
        """
        return {line: text for line, text in enumerate(ttg_file_list, 1) if
                text.startswith('Text 60') and text.endswith('62')}

    @staticmethod
    def expand_row_notation(string):
        """Expand sequence notation into a list.

        Expand numbers listed in range notation (1-100) and/or single numbers separated
        by commas (1,3,5) into a single list.

        http://gist.github.com/kgaughan/2491663
        """
        single_frames = set()

        for element in string.split(','):
            parts = [int(x) for x in element.split('-')]
            if len(parts) == 1:
                single_frames.add(parts[0])
            else:
                for frame in range(min(parts), max(parts) + 1):
                    single_frames.add(frame)

        return list(single_frames)

    @staticmethod
    def get_script_path():
        """Returns the path to this script file.

        http://stackoverflow.com/questions/918154/relative-paths-in-python
        """
        return os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def list_offset(list_of_integers, offset):
        """Offset each entry in a list of integers by a given offset value."""
        return [x + offset for x in list_of_integers]

    @staticmethod
    def makedirs(filepath):
        """Ensure all the directories exist for given filepath.

        Mimics a 'mkdir -p'.
        http://stackoverflow.com/a/600612/119527
        """
        dirpath = os.path.dirname(filepath)

        try:
            os.makedirs(dirpath)
        except OSError as ex:
            # ENOENT is empty filepath
            if ex.errno in (errno.ENOENT, errno.EEXIST):
                pass
            else:
                raise

    @staticmethod
    def tidy_text(text):
        """Returns string that is appropriate for filename usage."""
        # Chop first and last character if a symbol or space.
        chopped = re.sub(r'^[\W_]+|[\W_]+$', '', text)
        # Swap aspect ratios using colons such as 1:1 to 1x1
        swapped = re.sub(r'([1-9]+):([1-9]+[0-9]*)', r'\1x\2', chopped)
        # Santize symbols & whitespace to underscores.
        sanitized = re.sub(r'\W+', '_', swapped)
        # Tidy up duplicate underscores.
        tidy = re.sub(r'(_)\1+', '_', sanitized)

        return tidy

    @staticmethod
    def overwrite_query():
        """Prompt user with decision to overwrite."""
        prompt = ('Overwrite? [y]es / [n]o / [Y]es to All / [N]o to All ')
        valid_responses = ['y', 'n', 'Y', 'N']

        while True:
            try:
                result = raw_input(prompt)  # python 2.7
            except NameError:
                result = input(prompt)

            if result in valid_responses:
                break

        return result

    def convert_output_tokens(self, path):
        """Convert <> to {}.

        Flame convention for tokens is <>. Python uses {} for string formatting.
        """
        try:
            if not path:  # Catch empty string
                raise ValueError

            path = path.replace('<', '{').replace('>', '}')
            return path
        except ValueError:
            self.message('Output argument cannot be empty!')
            return None

    def expand_path(self, path):
        """Expand shell variables and shorthand such as ~."""
        try:
            return os.path.expandvars(os.path.expanduser(path))
        except AttributeError:
            self.message('Output missing!')
            return None

    def read_ttg_file(self):
        """Return contents of TTG file."""
        try:
            with open(self.template_ttg, encoding='utf-8') as open_file:
                contents = open_file.read().splitlines()
                return contents
        except FileNotFoundError:
            self.message('TTG Template file not found!')
            return []
        except Exception as exception:
            raise exception

    def read_unicode_csv_file(self):
        """Returns a tuple of list data from a csv file passed to it."""
        try:
            with open(self.csv_file, encoding='utf-8', newline='') as open_file:
                raw_rows = csv.reader(open_file)
                unicode_rows = list(raw_rows)

            return tuple(unicode_rows)

        except OSError:
            self.message('CSV file not found!')
            return ()

        except TypeError:
            self.message('CSV file not found!')
            return ()

    def get_template_html(self):
        """Return path to default template in default location."""
        return os.path.join(self.script_path, 'templates', 'template.html')

    def get_ttg_keywords(self):
        """Return a dictionary with line numbers and keywords converted to unicode."""
        ttg_keywords = self.find_ttg_keywords(self.template_ttg_rows)
        ttg_keywords_unicode = {index: self.convert_from_ttg_text(raw_string) for
                                index, raw_string in list(ttg_keywords.items())}

        return ttg_keywords_unicode

    def message_row(self, *args):
        """Prints out message and pads the row number."""
        row_num = ['Row', str(self.row_number + 1).zfill(2)]
        divider = ['-']
        message_elements = row_num + divider + list(args)

        self.message(' '.join(list(message_elements)))

    def write_ttg(self):
        """Write out a TTG file line by line and replace tokens with data as it goes.

        TTG File Format lists the length of the line before listing the contents of the
        line.  Example below:

            TextLenth 6
            Text 22 17 27 33 11 15

        Args:
            self.filepath:
                A string of the full destination path and filename.
            self.ttg_replacements:
                A dictionary of replacements and their destination line numbers.
            self.ttg_file_list:
                The template ttg stored a tuple of lines.
            self.template_ttg_keywords:
                Dictionary of the keywords in the template and their line number.
                Example {12:'Title'}
        """
        try:
            with open(self.filepath, 'w', encoding='utf-8') as ttg:
                # Run through TTG template line by line
                for line_number, text in enumerate(self.template_ttg_rows, 1):
                    # If the following line includes a token
                    if line_number + 1 in self.template_ttg_keywords:
                        # Take the following line number, find the keyword associated
                        # with that line, run that keyword through the dictionary of
                        # replacements.
                        try:
                            new_text = self.ttg_replacements[
                                self.template_ttg_keywords[line_number + 1]]
                        # If the token does not exist in the CSV
                        except KeyError:
                            new_text = ''
                        # TTG format precedes the actual text with a TextLength detail
                        new_ttg_text = self.convert_to_ttg_text(new_text)
                        # Write out the line before the token and the following line
                        # that actually contains the token
                        ttg.write('TextLength ' + str(len(new_ttg_text.split())) + '\n')
                        ttg.write('Text ' + new_ttg_text + '\n')
                    elif line_number in self.template_ttg_keywords:
                        continue
                    else:
                        ttg.write(text + '\n')
        except OSError:
            self.message('Skipping! Cannot write to this path.')

    def read_html_template(self):
        """Read in HTML template file.  Return tuple of file lines or empty tuple."""
        try:
            with open(self.template_html, encoding='utf-8', newline='') as file:
                self.template_html_rows = file.readlines()

        except OSError:
            self.message('HTML template file not found!')
            self.template_html_rows = ()

        except TypeError:
            self.message('HTML template file not found!')
            self.template_html_rows = ()

    def write_html_page(self, line_number_to_replace, list_of_replacements):
        """Generates HTML page of filenames to copy paste.

        Args:
            line_number_to_replace: Line number to replace with entries in the html
                template.
            list_of_replacements: List of entries to populate on the previous line
                number.
        """
        html_line = """  <button
        data-clipboard-text=\"master_name_goes_here\">master_name_goes_here</button>"""

        if self.template_html_rows:
            with open(self.destination_html, 'w', encoding='utf-8') as destination_file:
                for line_number, line in enumerate(self.template_html_rows, 1):
                    if line_number == line_number_to_replace:
                        for entry in list_of_replacements:
                            destination_file.write(
                                    html_line.replace(
                                        'master_name_goes_here', entry) + '\n')
                    else:
                        destination_file.write(line)

    def run(self):
        """Generate the slates!"""
        self.csv_rows = self.read_unicode_csv_file()
        self.filepath_pattern = self.convert_output_tokens(self.output)
        self.template_ttg_rows = self.read_ttg_file() if self.template_ttg else []
        self.template_ttg_keywords = (self.get_ttg_keywords() if self.template_ttg
                                      else {})

        # Print info for TTG template keywords
        if self.template_ttg_keywords:
            self.message(f'Found {len(self.template_ttg_keywords)} keywords in ' +
                         f'{self.template_ttg}')
            self.message(', '.join([keyword for _, keyword in
                                    list(self.template_ttg_keywords.items())]))

        # Print info for CSV file
        if self.csv_rows:
            self.message(f'Found {len(self.csv_rows)} rows in {self.csv_file}')

        for index, csv_row_data in enumerate(self.csv_rows):
            self.row_number = index
            self.row = csv_row_data

            # Check for empty row
            if all(i == '' for i in self.row):
                self.message_row('Skipping - Empty row')
                continue

            # Skip the header row
            if (self.row_header - 1) == self.row_number:
                self.message_row('Skipping - Header row')
                continue

            # Check for excluded rows
            if (self.row_exclude
                and self.row_number in self.list_offset(self.row_exclude, -1)):
                self.message_row('Skipping - Row excluded')
                continue

            # Check for included rows
            if (self.row_include
                and self.row_number not in self.list_offset(self.row_include, -1)):
                self.message_row('Skipping - Row not included')
                continue

            # Assemble replacement entries for output path
            filepath_replacements = {'column': [], 'keyword': {}}

            filepath_replacements['column'] = [None if item == '' else
                                               self.tidy_text(item) for item in
                                               self.row]

            filepath_replacements['keyword'] = {keyword: self.tidy_text(entry) for
                                                keyword, entry in zip(self.csv_rows[0],
                                                                      self.row)
                                                if entry != ''}

            # Check output file path has all necessary entries
            try:
                self.filepath = self.filepath_pattern.format(
                        * filepath_replacements['column'],
                        ** filepath_replacements['keyword'])

            except (IndexError, KeyError):
                self.message_row('Skipping - Could not assemble output path.')
                continue

            # Check output filename against filter exclude
            if (self.filter_exclude
                and True in
                [fnmatch.fnmatch(self.filepath, arg) for arg in self.filter_exclude]):
                self.message_row(self.filepath, 'matches exclude filter')
                self.message_row('Skipping', self.filepath)
                continue

            # Check output filename against include argument
            if (self.filter_include
                and not any(fnmatch.fnmatch(self.filepath, arg)
                for arg in self.filter_include)):
                self.message_row(self.filepath, 'does not match include filter')
                self.message_row('Skipping', self.filepath)
                continue

            self.message_row('Proceeding with', self.filename_no_ext(self.filepath))

            # Check for overwrite
            if self.template_ttg_keywords:
                exists = os.path.isfile(self.filepath)

                if exists:
                    self.message_row('Warning!', self.filepath, 'already exists!')

                if exists and self.force_overwrite:
                    pass
                if exists and self.skip_existing:
                    self.message_row('Skipping', self.filepath)
                    continue
                if exists and not self.force_overwrite and not self.skip_existing:
                    self.reply = self.overwrite_query()

                    # Overwrite responses
                    if self.reply and self.reply == 'y':
                        pass
                    if self.reply and self.reply == 'n':
                        self.message_row('Skipping', self.filepath)
                        continue
                    if self.reply and self.reply == 'Y':
                        self.force_overwrite = True
                    if self.reply and self.reply == 'N':
                        self.skip_existing = True
                        continue

            # Start writing out TTGs
            if self.template_ttg_keywords:
                self.message_row('Writing out', self.filepath)

                # Assemble dict using header row for keys and row entries for the
                # replacements
                self.ttg_replacements = dict(zip(self.csv_rows[self.row_header - 1],
                                                 self.csv_rows[self.row_number]))
            if self.template_ttg_keywords and not self.dry_run:
                self.makedirs(self.filepath)  # Make output path if necessary
                self.write_ttg()

            # Append to results
            self.results.append(self.filepath)

        # HTML Copy Paster
        if self.csv_rows and self.html:
            self.destination_html = os.path.join(self.common_path(self.results),
                                                 HTML_FILENAME)
            ttg_filenames = [self.filename_no_ext(i) for i in self.results]

            self.read_html_template()

            if not self.dry_run and self.template_html_rows:
                self.message(' '.join(['Writing out', self.destination_html]))
                self.makedirs(self.destination_html)
                self.write_html_page(40, ttg_filenames)
                self.results.append(self.destination_html)

        self.message('Done!')
        return self.results


class PySlaterWindow:
    """GUI menu for Flame to interact with the PySlater command line tool."""

    def __init__(self, _selection):  # selection is not needed
        """Set intial class attributes for PySlaterWindow."""
        self.pys = None

        self.cmd_dir = self.get_cmd_dir()

        self.project_name = self.get_project_name()

        self.default_path = self.realpath_join(
            [SETUPS_ROOT, self.project_name, 'text', 'flame'])

        self.csv_file_path = self.default_path

        self.filter_exclude = ''
        self.filter_include = ''

        self.ttg_file_path = self.path_join(
            [self.cmd_dir, DEFAULT_TEMPLATE])

        self.output_template = ''
        self.get_output_template()

        self.html = True
        self.html_path = ''
        self.get_html_path()
        self.html_template_path = ''
        self.get_html_template_path()

        self.window_size = {'x': 1000, 'y': 756}

        self.main_window()

        self.message_shell(VERSION_TITLE)
        self.message_shell(f'Script called from {__file__}')

    @staticmethod
    def message_shell(info):
        """Print message to shell window and append global MESSAGE_PREFIX."""
        sys.stdout.write(MESSAGE_PREFIX + ' ' + info + '\n')

    @staticmethod
    def copy_to_clipboard(text):
        """Self explanitory.  Only takes a string."""
        qt_app_instance = QtWidgets.QApplication.instance()
        qt_app_instance.clipboard().setText(text)

    @staticmethod
    def get_cmd_dir():
        """Return string containing path where this module is located."""
        dirpath = os.path.realpath(os.path.dirname(__file__))

        return dirpath

    @staticmethod
    def get_project_name():
        """Return name of current Autodesk Flame project."""
        project_name = flame.project.current_project.project_name

        return project_name

    @staticmethod
    def path_join(paths):
        """Platform independent joining of folder paths."""
        full_path = os.path.join(*paths)

        return full_path

    @staticmethod
    def realpath_join(paths):
        """Join folder paths and return absolute path."""
        path = os.path.join(*paths)
        real_path = os.path.realpath(path)

        return real_path

    def copy_csv_to_clipboard(self):
        """Copy CSV to clipboard and send message to QWidget."""
        self.copy_to_clipboard(self.csv_path_line_edit.text())
        self.message_window('CSV file path copied to clipboard.')

    def copy_html_to_clipboard(self):
        """Copy HTML to clipboard and send message to QWidget."""
        self.copy_to_clipboard(self.html_path_line_edit.text())
        self.message_window('HTML file path copied to clipboard.')

    def copy_url_to_clipboard(self):
        """Copy speadsheet URL to clipboard and send message to QWidget."""
        self.copy_to_clipboard(self.url_line_edit.text())
        self.message_window('URL copied to clipboard.')

    def filter_exclude_btn_toggle(self):
        """Code to run on Filter Exclude button press.

        Filter exclude and include may not be used together.  If exclude is enabled,
        disable include, or vice versa.
        """
        if not self.filter_exclude_line_edit.isEnabled():
            self.filter_exclude_line_edit.setEnabled(True)

            self.filter_include_btn.setChecked(False)
            self.filter_include_line_edit.setEnabled(False)
        else:
            self.filter_exclude_line_edit.setEnabled(False)

        self.get_filter_exclude()

    def filter_include_btn_toggle(self):
        """Code to run on Filter Include button press.

        Filter exclude and include may not be used together.  If include is enabled,
        disable exclude, or vice versa.
        """
        if not self.filter_include_line_edit.isEnabled():
            self.filter_include_line_edit.setEnabled(True)

            self.filter_exclude_btn.setChecked(False)
            self.filter_exclude_line_edit.setEnabled(False)
        else:
            self.filter_include_line_edit.setEnabled(False)

        self.get_filter_include()

    def ttg_btn_toggle(self):
        """Code to run on TTG button press.

        When button widget is enabled, enable corresponding line edit widget and
        store string as attribute.  If disabled, disable corresponding line edit widget
        and clear attribute.
        """
        if self.ttg_path_line_edit.isEnabled():
            self.ttg_path_line_edit.setEnabled(False)
            self.ttg_file_path = ''
        else:
            self.ttg_path_line_edit.setEnabled(True)
            self.ttg_file_path = self.ttg_path_line_edit.text()

        self.get_ttg_file_path()

    def html_btn_toggle(self):
        """Code to run on HTML button press.

        If button is enabled, enable corresponding line edit widget and set empty
        attribute.  If disabled, disable corresponding line edit widget and set
        attribute.
        """
        if self.html_path_line_edit.isEnabled():
            self.html_path_line_edit.setEnabled(False)
            self.html = False
        else:
            self.html_path_line_edit.setEnabled(True)
            self.html = True

    def get_csv_path(self):
        """Update attribute with string from line edit widget."""
        self.csv_file_path = self.csv_path_line_edit.text()

    def get_filter_exclude(self):
        """Assemble list for filter_exclude attribute if enabled, otherwise empty."""
        if self.filter_exclude_line_edit.isEnabled():
            filter_exclude_raw = self.filter_exclude_line_edit.text()
            self.filter_exclude = [item.strip() for item in
                                   filter_exclude_raw.split(',')]
        else:
            self.filter_exclude = []

    def get_filter_include(self):
        """Assemble list for filter_include attribute if enabled, otherwise empty."""
        if self.filter_include_line_edit.isEnabled():
            filter_include_raw = self.filter_include_line_edit.text()
            self.filter_include = [item.strip() for item in
                                   filter_include_raw.split(',')]
        else:
            self.filter_include = []

    def get_html_path(self):
        """Assemble HTML destination filepath."""
        self.html_path = os.path.join(self.default_path, HTML_FILENAME)

    def get_html_template_path(self):
        """Assemble HTML template filepath."""
        self.html_template_path = os.path.join(os.path.dirname(__file__), HTML_FILENAME)

    def get_ttg_file_path(self):
        """Gets attribute containing path to the TTG if enabled in GUI."""
        if self.ttg_path_line_edit.isEnabled():
            self.ttg_file_path = self.ttg_path_line_edit.text()
        else:
            self.ttg_file_path = ''

    def get_output_template(self):
        """Assemble initial output template filepath."""
        self.output_template = os.path.join(self.default_path, DEFAULT_OUTPUT_TTG)

    def message_window(self, info):
        """Print message to the bottom section of the QWidget main window."""
        self.text.appendPlainText(info)

    def message(self, info):
        """Print message to shell window & QWidget."""
        self.message_shell(info)
        self.message_window(info)

    def update_html_line_edit(self):
        """Retrieve HTML from returned results, display path in main window."""
        if self.html:
            self.html_path_line_edit.setText(self.pys.results[-1])
        else:
            self.html_path_line_edit.setText('')

    def make_slates(self):
        """Assemble all the attributes and run it."""
        # Run the PySlater class
        self.pys = PySlater(
            csv_file=self.csv_file_path,
            filter_include=self.filter_include,
            filter_exclude=self.filter_exclude,
            force_overwrite=True,
            html=self.html,
            message=self.message,
            output=self.output_template,
            row_header=1,
            skip_existing=False,
            template_ttg=self.ttg_file_path)
        self.pys.run()

    def main_window(self):
        """The main GUI window."""

        def update_output_template():
            """Update output filepath template.

            Update self.output_template when either of the component line edits are
            changed.
            """
            self.output_template = os.path.join(
                    self.output_path_line_edit.text(),
                    self.output_pattern_line_edit.text())

        def okay_button():
            """Okay button pressed."""
            self.text.clear()  # Clear the previous shell output
            self.make_slates()
            self.update_html_line_edit()  # update HTML line if HTML file now exists

        def close_button():
            """Close button pressed."""
            self.message_shell('Window closed!')
            self.window.close()

        self.window = QtWidgets.QWidget()

        self.window.setMinimumSize(self.window_size['x'], self.window_size['y'])
        self.window.setStyleSheet('background-color: #272727')
        self.window.setWindowTitle(VERSION_TITLE)

        # Mac needs this to close the window
        self.window.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # FlameLineEdit class needs this
        self.window.setFocusPolicy(QtCore.Qt.StrongFocus)

        # Labels
        self.input_label = FlameLabel('Input', 'underline')
        self.url_label = FlameLabel('Spreadsheet URL', 'normal')
        self.csv_label = FlameLabel('CSV File', 'normal')

        self.filter_label = FlameLabel('Filtering', 'underline')

        self.output_label = FlameLabel('Output', 'underline')
        self.output_path_label = FlameLabel('Path', 'normal')
        self.output_pattern_label = FlameLabel('Pattern', 'normal')

        # Buttons
        self.ok_btn = FlameButton('Ok', okay_button, button_color='blue')

        self.close_btn = FlameButton('Close', close_button)

        self.url_copy_btn = FlameButton('Copy', self.copy_url_to_clipboard)

        self.csv_copy_btn = FlameButton('Copy', self.copy_csv_to_clipboard)

        self.filter_exclude_btn = FlamePushButton(
            'Exclude', self.window, False, self.filter_exclude_btn_toggle)

        self.filter_include_btn = FlamePushButton(
            'Include', self.window, False, self.filter_include_btn_toggle)

        self.ttg_template_btn = FlamePushButton(
            'TTG Template', self.window, True, self.ttg_btn_toggle)

        self.html_btn = FlamePushButton(
            'HTML', self.window, True, self.html_btn_toggle)

        self.html_copy_btn = FlameButton('Copy', self.copy_html_to_clipboard)

        # Line Edits
        self.url_line_edit = FlameLabel(GSHEET, 'background')

        self.csv_path_line_edit = FlameLineEditFileBrowse(
            self.csv_file_path, '*.csv', self.window)
        self.csv_path_line_edit.textChanged.connect(self.get_csv_path)

        self.filter_include_line_edit = FlameLineEdit('')
        self.filter_include_line_edit.setEnabled(False)  # initial state
        self.filter_include_line_edit.textChanged.connect(self.get_filter_include)

        self.filter_exclude_line_edit = FlameLineEdit('')
        self.filter_exclude_line_edit.setEnabled(False)  # initial state
        self.filter_exclude_line_edit.textChanged.connect(self.get_filter_exclude)

        self.output_path_line_edit = FlameLineEditFileBrowse(
            self.default_path, 'dir', self.window)
        self.output_path_line_edit.textChanged.connect(update_output_template)

        self.output_pattern_line_edit = FlameLineEdit(DEFAULT_OUTPUT_TTG)
        self.output_pattern_line_edit.textChanged.connect(update_output_template)

        self.ttg_path_line_edit = FlameLineEditFileBrowse(
            self.ttg_file_path, '*.ttg', self.window)
        self.ttg_path_line_edit.textChanged.connect(self.get_ttg_file_path)

        self.html_path_line_edit = FlameLabel('', 'background')

        # Text Field
        self.text = QtWidgets.QPlainTextEdit()
        self.text.setFont('Monospace')
        self.text.setReadOnly(True)

        # Layout - Input
        self.grid1 = QtWidgets.QGridLayout()
        self.grid1.setVerticalSpacing(10)
        self.grid1.setHorizontalSpacing(10)
        self.grid1.addWidget(self.input_label, 0, 0, 1, 3)
        self.grid1.addWidget(self.url_label, 1, 0)
        self.grid1.addWidget(self.url_line_edit, 1, 1)
        self.grid1.addWidget(self.url_copy_btn, 1, 2)
        self.grid1.addWidget(self.csv_label, 2, 0)
        self.grid1.addWidget(self.csv_path_line_edit, 2, 1)
        self.grid1.addWidget(self.csv_copy_btn, 2, 2)

        # Layout - Filtering
        self.grid2 = QtWidgets.QGridLayout()
        self.grid2.setVerticalSpacing(10)
        self.grid2.setHorizontalSpacing(10)
        self.grid2.addWidget(self.filter_label, 0, 0, 1, 3)
        self.grid2.addWidget(self.filter_include_btn, 1, 0)
        self.grid2.addWidget(self.filter_include_line_edit, 1, 1)
        self.grid2.addWidget(self.filter_exclude_btn, 2, 0)
        self.grid2.addWidget(self.filter_exclude_line_edit, 2, 1)
        self.grid2.setColumnMinimumWidth(2, 150)  # match the copy buttons

        # Layout - Output
        self.grid3 = QtWidgets.QGridLayout()
        self.grid3.setVerticalSpacing(10)
        self.grid3.setHorizontalSpacing(10)
        self.grid3.addWidget(self.output_label, 0, 0, 1, 3)
        self.grid3.addWidget(self.output_path_label, 1, 0)
        self.grid3.addWidget(self.output_path_line_edit, 1, 1)
        self.grid3.addWidget(self.output_pattern_label, 2, 0)
        self.grid3.addWidget(self.output_pattern_line_edit, 2, 1)
        self.grid3.addWidget(self.ttg_template_btn, 3, 0)
        self.grid3.addWidget(self.ttg_path_line_edit, 3, 1)
        self.grid3.addWidget(self.html_btn, 4, 0)
        self.grid3.addWidget(self.html_path_line_edit, 4, 1)
        self.grid3.addWidget(self.html_copy_btn, 4, 2)

        # Layout
        self.hbox01 = QtWidgets.QHBoxLayout()
        self.hbox01.addStretch(1)
        self.hbox01.addWidget(self.close_btn)
        self.hbox01.addWidget(self.ok_btn)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.setContentsMargins(20, 20, 20, 20)
        self.vbox.addLayout(self.grid1)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.grid2)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.grid3)
        self.vbox.addSpacing(20)
        self.vbox.addLayout(self.hbox01)
        self.vbox.addSpacing(10)
        self.vbox.addWidget(self.text)

        self.window.setLayout(self.vbox)

        # Center Window
        resolution = QtGui.QGuiApplication.primaryScreen().availableGeometry()

        self.window.move(resolution.center().x() - self.window_size['x'] / 2,
                         resolution.center().y() - self.window_size['y'] / 2)

        self.window.show()
        return self.window


def get_main_menu_custom_ui_actions():
    """Python hook for Flame Fish menu."""
    return [{'name': 'Slates...',
             'actions': [{'name': 'PySlater for Flame',
                          'execute': PySlaterWindow,
                          'minimumVersion': '2025.0.0.0',
                          }]
           }]
