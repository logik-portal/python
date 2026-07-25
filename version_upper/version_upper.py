"""
Script Name: Version Upper
Script Version: 3.0.0
Flame Version: 2020
Written by: John Geehreng
Creation Date: 06.06.20
Update Date: 07.24.26

Description:

    Version up all selected items, working within whatever naming convention is already in
    use. The characters in front of the version number are a preference instead of a hard
    coded letter, so the same script works in any pipeline without editing it.

    Preferences holds a list of version prefixes. Every one of them is live at once, so a
    selection mixing "_v03" and "_OL01" versions up correctly in a single pass. Padding is
    read from the name and kept, so "v01" stays two digits and "c001" stays three.

    If an item has no version matching any known prefix, Version Upper reads the name, works
    out the prefix it is actually using, and offers to add it in one click.

Menus:

    Version up:
        Right-click on clips, sequences, reels, or folders -> Renamers -> Version Upper

    Preferences:
        Right-click on clips, sequences, reels, or folders -> Renamers -> Version Upper Preferences
        Flame Main Menu -> Version Upper -> Preferences

    To change the "Renamers" menu folder, edit folder_name below.

To install:

    Copy this script into its own folder in your Flame python path:

        /opt/Autodesk/shared/python/version_upper/version_upper.py

Config:

    Preferences are written to a config folder beside the script:

        version_upper/config/config.json

    If the script folder is read only, which a system wide install often is, preferences go to
    ~/.version_upper/config.json instead. The Preferences window shows the path in use.

    Set the VERSION_UPPER_CONFIG environment variable to point somewhere else, e.g. a shared
    location so a whole facility loads the same prefixes.

Updates:

    v3.0.0 07.24.26
        - Added a Preferences window. The version prefix is now a setting instead of a hard
          coded letter.
        - Multiple prefixes are live at once. A selection mixing conventions versions up in
          one pass, with no mode to switch.
        - Padding is read from each name and kept, so the script never reformats a version
          number it did not have to touch.
        - Items with no recognised version are collected into a single dialog instead of one
          popup per item. The dialog names the prefix it found and offers to add it.
        - Version numbers are matched at the start of a word by default, so the "v25" inside
          "Nov25" is no longer mistaken for a version. Turning off "Require a separator before
          the version" restores the original matching for names like "SHOWv01".
        - The prefix suggested for a skipped name is never a month name, so a date is never one
          click away from being renamed.
        - Fixed: names containing more than one version token raised a ValueError.
        - Fixed: names containing more than one version token had every token renumbered.
          Only the last token is changed now.

    v2.1 06.05.26
        - Updated to work with either PySide6 or PySide2.

    v2.0 07.12.21
        - Items do not need to end in "v##" anymore. "v##" can be anywhere in the item name.
          If it cannot find "v##" that item will be skipped, but you will see an error message
          in the Flame UI and the script continues.
"""

from __future__ import print_function

import json
import os
import re

# -------------------------------------
# [Constants]
# -------------------------------------

SCRIPT_NAME = "Version Upper"
SCRIPT_VERSION = "v3.0.0"

# Flame right-click menu folder this script appears under. Changing it needs a Python hooks
# reload to show up, so it lives here as a one line edit rather than in Preferences.
folder_name = "Renamers"
action_name = SCRIPT_NAME

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
CONFIG_ENV_VAR = "VERSION_UPPER_CONFIG"

DEFAULT_PREFIXES = ["v"]

# Name used to preview prefixes in the Preferences window.
SAMPLE_NAME = "SHOW_0100_comp_{token}"

# Finds "letters immediately followed by 1 to 3 digits", e.g. "v01", "OL03", "c001".
# Used to work out the prefix a name is using when none of the known ones match.
#
# The 3 digit cap keeps years and shot numbers out of the suggestion. "Nov2024" would
# otherwise read as prefix "Nov", and offering to bump that risks a bad bulk rename.
# Suggesting nothing costs one trip to Preferences; suggesting wrong costs real names.
GENERIC_VERSION_TOKEN = re.compile(r"(?<![A-Za-z0-9])([A-Za-z]{1,8})(\d{1,3})(?![A-Za-z0-9])")

# Dates in names are structurally identical to versions, so the digit cap alone does not
# catch them: "Nov2024" is filtered by the cap, but "Nov25" and "Nov100" are not. Offering
# "Nov" would put renaming the month one click away. Months are a small closed set, so
# naming them is cheaper and more reliable than guessing at the shape of a date.
NEVER_SUGGEST = frozenset([
    "jan", "feb", "mar", "apr", "may", "jun",
    "jul", "aug", "sep", "sept", "oct", "nov", "dec",
    "january", "february", "march", "april", "june",
    "july", "august", "september", "october", "november", "december",
])

# -------------------------------------
# [Qt]
# -------------------------------------

try:
    from PySide6 import QtCore, QtGui, QtWidgets
except ImportError:
    try:
        from PySide2 import QtCore, QtGui, QtWidgets
    except ImportError:
        QtCore = QtGui = QtWidgets = None

# Lets the versioning logic in this file be imported and tested without Qt installed.
_DIALOG_BASE = QtWidgets.QDialog if QtWidgets else object


def qt_available():
    return QtWidgets is not None


def exec_dialog(dialog):
    """
    Run a modal dialog. PySide6 uses exec(), PySide2 uses exec_().
    """

    runner = getattr(dialog, "exec", None) or getattr(dialog, "exec_")
    return runner()


def global_pos(event):
    """
    Mouse position in screen space. PySide6 uses globalPosition(), PySide2 uses globalPos().
    """

    try:
        return event.globalPosition().toPoint()
    except AttributeError:
        return event.globalPos()


# -------------------------------------
# [Settings]
# -------------------------------------

def prefix_error(prefix):
    """
    Reason a prefix cannot be used, or None if it is fine.
    """

    if not prefix.strip():
        return "A version prefix cannot be blank."
    if re.search(r"\d", prefix):
        return "\"%s\" cannot contain numbers - the digits after the prefix are the version." % prefix

    return None


class Settings(object):
    """
    Everything the script needs to know, loaded from and saved to the config file.

    prefixes           Version prefixes to look for. All of them are live at once.
    case_sensitive     False lets "v01" and "V01" both match.
    require_separator  False lets a version match anywhere, including inside a word, which
                       is how the original script behaved.
    """

    def __init__(self, prefixes=None, case_sensitive=True, require_separator=True):

        # None means "give me the defaults". An empty list stays empty, so error() can
        # report it rather than silently resurrecting the defaults.
        self.prefixes = list(DEFAULT_PREFIXES) if prefixes is None else list(prefixes)
        self.case_sensitive = case_sensitive
        self.require_separator = require_separator

    # -------------------------------------

    def regex(self, prefix):
        """
        Compiled pattern matching one prefix followed by a version number. Group 1 is the
        number.

        By default the version has to start at a word boundary, so prefix "v" matches "_v01"
        but not the "v25" inside "Nov25". Renaming the wrong part of a name is silent, while
        a missed match shows up in the skipped list, so the strict reading is the default.

        Turning require_separator off restores the original script's behaviour for names that
        run the version onto the previous word, like "SHOWv01".

        A prefix that already starts with a separator, like "_v", never needs the guard.
        """

        pattern = re.escape(prefix) + r"(\d+)"

        if self.require_separator and prefix[:1].isalnum():
            pattern = r"(?<![A-Za-z0-9])" + pattern

        return re.compile(pattern, 0 if self.case_sensitive else re.IGNORECASE)

    def summary(self):
        """
        The known prefixes as readable text, e.g. 'v, OL'.
        """

        return ", ".join(self.prefixes) if self.prefixes else "none set"

    def error(self):
        """
        Reason these settings cannot be used, or None if they are fine.
        """

        if not self.prefixes:
            return "Add at least one version prefix, e.g. \"v\"."

        for prefix in self.prefixes:
            problem = prefix_error(prefix)
            if problem:
                return problem

        lowered = [prefix.lower() for prefix in self.prefixes]

        for prefix in lowered:
            if lowered.count(prefix) > 1:
                return "\"%s\" is in the list more than once." % prefix

        return None

    # -------------------------------------

    @classmethod
    def load(cls):
        """
        Load preferences. Never raises - a missing or damaged config falls back to the
        defaults so a bad file cannot stop the Flame menu from loading.
        """

        path = config_path()

        try:
            if not os.path.isfile(path):
                return cls()

            with open(path, "r") as config_file:
                data = json.load(config_file)

            prefixes = [str(prefix).strip() for prefix in data.get("prefixes", [])]
            prefixes = [prefix for prefix in prefixes if prefix]

            if not prefixes:
                return cls()

            return cls(
                prefixes=prefixes,
                case_sensitive=bool(data.get("case_sensitive", True)),
                require_separator=bool(data.get("require_separator", True)),
            )

        except Exception as error:
            print("%s: could not read preferences (%s). Using defaults." % (SCRIPT_NAME, error))
            return cls()

    def save(self):
        """
        Write preferences to disk. Returns None on success or an error string.
        """

        path = config_path()

        data = {
            "config_version": 3,
            "prefixes": self.prefixes,
            "case_sensitive": self.case_sensitive,
            "require_separator": self.require_separator,
        }

        try:
            directory = os.path.dirname(path)
            if directory and not os.path.isdir(directory):
                os.makedirs(directory)

            with open(path, "w") as config_file:
                json.dump(data, config_file, indent=4)

            return None

        except Exception as error:
            return "Could not save preferences to %s\n%s" % (path, error)

    def copy(self):

        return Settings(list(self.prefixes), self.case_sensitive, self.require_separator)


def config_path():
    """
    Preferences live in a config folder beside the script, matching the Flame convention:

        version_upper/config/config.json

    A system wide install can be read only - /opt/Autodesk/shared/python usually is - so when
    the script folder cannot be written to, preferences go to the user's home folder instead.
    An existing config beside the script always wins, so a facility can ship a read only one.
    The Preferences window shows whichever path is actually in use.
    """

    override = os.environ.get(CONFIG_ENV_VAR)

    if override:
        return os.path.expanduser(override)

    beside_script = os.path.join(SCRIPT_PATH, "config", "config.json")

    if os.path.isfile(beside_script) or os.access(SCRIPT_PATH, os.W_OK):
        return beside_script

    return os.path.join(os.path.expanduser("~"), ".version_upper", "config.json")


# -------------------------------------
# [Versioning]
# -------------------------------------

def find_version_tokens(name, settings):
    """
    Every version token in the name, in the order they appear.

    When two prefixes could both claim the same characters the longer one wins, so having
    both "L" and "OL" in the list cannot split "OL01" down the middle.
    """

    found = []

    for prefix in sorted(settings.prefixes, key=len, reverse=True):
        for match in settings.regex(prefix).finditer(name):
            overlaps = [kept for kept in found
                        if match.start() < kept.end() and kept.start() < match.end()]
            if not overlaps:
                found.append(match)

    found.sort(key=lambda match: match.start())

    return found


def version_up_name(name, settings):
    """
    Version up a single name.

    Returns (new_name, old_token, new_token), or None if the name has no known version.

    Padding comes from the name itself, so "v01" stays two digits and "c001" stays three.

    When a name holds more than one version the last one is changed, since versions trail.
    Only that token changes, so "SHOW_v01_comp_v03" versions up once, not twice.
    """

    matches = find_version_tokens(name, settings)

    if not matches:
        return None

    match = matches[-1]

    digits = match.group(1)
    old_token = match.group(0)

    # Take the prefix from the name rather than the settings so "V01" stays uppercase
    # when matching is case insensitive.
    prefix = old_token[:len(old_token) - len(digits)]

    new_token = prefix + str(int(digits) + 1).zfill(len(digits))
    new_name = name[:match.start()] + new_token + name[match.end():]

    return new_name, old_token, new_token


def detect_prefix(names, settings):
    """
    Best guess at the version prefix used by names that had no known version.

    Looks for letters glued to digits and prefers the last one in each name, since the
    version almost always trails. Returns the prefix used by the most names, or None.
    """

    known = [prefix.lower() for prefix in settings.prefixes]
    counts = {}

    for name in names:
        tokens = GENERIC_VERSION_TOKEN.findall(name)
        if not tokens:
            continue

        prefix = tokens[-1][0]

        if prefix.lower() in known or prefix.lower() in NEVER_SUGGEST:
            continue

        counts[prefix] = counts.get(prefix, 0) + 1

    if not counts:
        return None

    # Most names first, then shortest prefix, then alphabetical so the result is stable.
    return sorted(counts, key=lambda prefix: (-counts[prefix], len(prefix), prefix))[0]


def detect_case_mismatch(names, settings):
    """
    A known prefix that would have matched if case were ignored, or None.

    Without this, "_ol01" against prefix "OL" reports as having no version at all, when the
    real fix is one checkbox.
    """

    if not settings.case_sensitive:
        return None

    relaxed = settings.copy()
    relaxed.case_sensitive = False

    for prefix in settings.prefixes:
        for name in names:
            if relaxed.regex(prefix).search(name):
                return prefix

    return None


# -------------------------------------
# [Flame helpers]
# -------------------------------------

def item_name(item):
    """
    Flame returns names wrapped in quotes. Strip them if they are there.
    """

    name = str(item.name)

    if len(name) >= 2 and name[0] == name[-1] and name[0] in ("'", '"'):
        name = name[1:-1]

    return name


def show_in_flame(message, kind="error"):
    """
    Post a message to the Flame console area. Silently skipped on Flame versions without it.
    """

    try:
        import flame
        flame.messages.show_in_console("%s: %s" % (SCRIPT_NAME, message), kind, 8)
    except Exception:
        pass


# -------------------------------------
# [UI]
# -------------------------------------

STYLESHEET = """
    QWidget {
        background-color: rgb(36, 36, 36);
        color: rgb(190, 190, 190);
        font-size: 13px;
        }
    QLabel {
        background-color: transparent;
        color: rgb(190, 190, 190);
        }
    QLabel#title {
        color: rgb(190, 190, 190);
        font-size: 20px;
        }
    QLabel#heading {
        color: rgb(154, 154, 154);
        font-size: 13px;
        }
    QLabel#hint {
        color: rgb(120, 120, 120);
        font-size: 12px;
        }
    QLabel#error {
        background-color: transparent;
        color: rgb(200, 90, 90);
        }
    QLineEdit {
        background-color: rgb(55, 55, 55);
        color: rgb(190, 190, 190);
        selection-background-color: rgb(0, 110, 175);
        border: 1px solid rgb(55, 55, 55);
        padding-left: 5px;
        min-height: 26px;
        }
    QLineEdit:focus {
        background-color: rgb(73, 86, 99);
        border: 1px solid rgb(0, 110, 175);
        }
    QPushButton {
        background-color: rgb(58, 58, 58);
        color: rgb(190, 190, 190);
        border: 1px solid rgb(58, 58, 58);
        padding: 6px 14px;
        min-height: 20px;
        }
    QPushButton:hover {
        border: 1px solid rgb(90, 90, 90);
        }
    QPushButton:pressed {
        background-color: rgb(66, 66, 66);
        border: 1px solid rgb(90, 90, 90);
        }
    QPushButton:disabled {
        color: rgb(116, 116, 116);
        background-color: rgb(48, 48, 48);
        border: 1px solid rgb(48, 48, 48);
        }
    QPushButton#confirm {
        background-color: rgb(0, 110, 175);
        color: rgb(215, 215, 215);
        border: 1px solid rgb(0, 110, 175);
        }
    QPushButton#confirm:hover {
        border: 1px solid rgb(90, 150, 200);
        }
    QComboBox {
        background-color: rgb(55, 55, 55);
        color: rgb(190, 190, 190);
        border: 1px solid rgb(55, 55, 55);
        padding-left: 5px;
        min-height: 26px;
        }
    QComboBox:hover {
        border: 1px solid rgb(90, 90, 90);
        }
    QComboBox::drop-down {
        border: none;
        width: 20px;
        }
    QComboBox QAbstractItemView {
        background-color: rgb(45, 45, 45);
        color: rgb(190, 190, 190);
        selection-background-color: rgb(0, 110, 175);
        border: 1px solid rgb(90, 90, 90);
        }
    QCheckBox {
        background-color: transparent;
        color: rgb(190, 190, 190);
        spacing: 8px;
        }
    QCheckBox::indicator {
        width: 14px;
        height: 14px;
        background-color: rgb(55, 55, 55);
        border: 1px solid rgb(80, 80, 80);
        }
    QCheckBox::indicator:checked {
        background-color: rgb(0, 110, 175);
        border: 1px solid rgb(0, 110, 175);
        }
    QListWidget {
        background-color: rgb(30, 30, 30);
        color: rgb(190, 190, 190);
        border: 1px solid rgb(50, 50, 50);
        outline: none;
        }
    QListWidget::item {
        padding: 5px 8px;
        }
    QListWidget::item:selected {
        background-color: rgb(0, 110, 175);
        color: rgb(215, 215, 215);
        }
    QTextEdit {
        background-color: rgb(30, 30, 30);
        color: rgb(154, 154, 154);
        border: 1px solid rgb(50, 50, 50);
        }
    QScrollBar:vertical {
        background-color: rgb(36, 36, 36);
        width: 12px;
        }
    QScrollBar::handle:vertical {
        background-color: rgb(58, 58, 58);
        min-height: 20px;
        }
    QScrollBar::add-line, QScrollBar::sub-line {
        height: 0px;
        }
    QToolTip {
        background-color: rgb(45, 45, 45);
        color: rgb(190, 190, 190);
        border: 1px solid rgb(90, 90, 90);
        }
"""


class FlameDialog(_DIALOG_BASE):
    """
    Frameless dark dialog matching the Flame script look. Drag by the background, Escape closes.
    """

    def __init__(self, title, width, height):

        super(FlameDialog, self).__init__()

        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        # Without this a QWidget subclass ignores the stylesheet background.
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(STYLESHEET)
        self.resize(width, height)

        self._drag_pos = None

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("title")

        self.body_layout = QtWidgets.QVBoxLayout()
        self.body_layout.setContentsMargins(0, 0, 0, 0)
        self.body_layout.setSpacing(10)

        outer_layout = QtWidgets.QVBoxLayout()
        outer_layout.setContentsMargins(20, 16, 20, 16)
        outer_layout.setSpacing(14)
        outer_layout.addWidget(title_label)
        outer_layout.addLayout(self.body_layout)

        self.setLayout(outer_layout)

        self._center()

    def _center(self):

        try:
            screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
            self.move(int(screen.center().x() - self.width() / 2),
                      int(screen.center().y() - self.height() / 2))
        except Exception:
            pass

    def paintEvent(self, event):
        """
        Blue bar down the left edge, the usual marker on Flame script windows.
        """

        super(FlameDialog, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.fillRect(0, 0, 4, self.height(), QtGui.QColor(0, 110, 176))
        painter.end()

    def mousePressEvent(self, event):

        self._drag_pos = global_pos(event)

    def mouseMoveEvent(self, event):

        if self._drag_pos is None:
            return

        position = global_pos(event)
        delta = position - self._drag_pos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self._drag_pos = position

    def keyPressEvent(self, event):

        if event.key() == QtCore.Qt.Key_Escape:
            self.reject()
        else:
            super(FlameDialog, self).keyPressEvent(event)


def label(text, object_name="heading"):

    widget = QtWidgets.QLabel(text)
    widget.setObjectName(object_name)

    return widget


def button(text, callback, confirm=False, tooltip=None):

    widget = QtWidgets.QPushButton(text)

    # Swallow the "checked" bool that clicked() sends, so callbacks with optional
    # arguments do not receive it as a value.
    widget.clicked.connect(lambda *args: callback())
    widget.setFocusPolicy(QtCore.Qt.NoFocus)

    if confirm:
        widget.setObjectName("confirm")
    if tooltip:
        widget.setToolTip(tooltip)

    return widget


# -------------------------------------
# [Preferences window]
# -------------------------------------

class PreferencesWindow(FlameDialog):
    """
    Edit the list of version prefixes and how they are matched.
    """

    def __init__(self, settings, add_prefix=None):

        super(PreferencesWindow, self).__init__(
            "%s Preferences  %s" % (SCRIPT_NAME, SCRIPT_VERSION), 760, 420)

        # Work on a copy so Cancel really cancels.
        self.settings = settings.copy()

        self.saved = False
        self._loading = False

        self._build()
        self._reload_list()

        if add_prefix:
            self.add_prefix(add_prefix)

    # -------------------------------------

    def _build(self):

        self.body_layout.addWidget(label(
            "Version Upper looks for any of these prefixes. Padding is read from each name "
            "and kept as it is."))

        columns = QtWidgets.QHBoxLayout()
        columns.setSpacing(16)
        columns.addLayout(self._build_prefix_list(), 1)
        columns.addLayout(self._build_preview(), 2)

        self.body_layout.addLayout(columns)
        self.body_layout.addLayout(self._build_options())
        self.body_layout.addLayout(self._build_footer())

    def _build_prefix_list(self):

        self.prefix_list = QtWidgets.QListWidget()
        self.prefix_list.setToolTip(
            "The characters in front of the version number.\n"
            "Examples: v for v01, OL for OL01, c for c001.\n"
            "Double-click to edit.")
        self.prefix_list.itemChanged.connect(self._prefix_edited)

        list_buttons = QtWidgets.QHBoxLayout()
        list_buttons.setSpacing(6)
        list_buttons.addWidget(button("Add", self._add_row))
        list_buttons.addWidget(button("Remove", self._remove_row))

        column = QtWidgets.QVBoxLayout()
        column.setSpacing(8)
        column.addWidget(label("Version Prefixes"))
        column.addWidget(self.prefix_list)
        column.addWidget(label("Double-click a prefix to edit it.", "hint"))
        column.addLayout(list_buttons)

        return column

    def _build_preview(self):

        self.preview = QtWidgets.QTextEdit()
        self.preview.setReadOnly(True)

        column = QtWidgets.QVBoxLayout()
        column.setSpacing(8)
        column.addWidget(label("Preview"))
        column.addWidget(self.preview)

        return column

    def _build_options(self):

        self.case_check = QtWidgets.QCheckBox("Case sensitive")
        self.case_check.setToolTip(
            "On, \"v01\" matches but \"V01\" does not.\n"
            "Off, both match and each name keeps its own casing.")
        self.case_check.setChecked(self.settings.case_sensitive)
        self.case_check.stateChanged.connect(self._options_changed)

        self.separator_check = QtWidgets.QCheckBox("Require a separator before the version")
        self.separator_check.setToolTip(
            "On, the version must follow _ - . or a space, or start the name.\n\n"
            "Off, a version counts anywhere in the name, including inside a word. That is how\n"
            "the original script worked, so turn it off for names like \"SHOWv01\". It also\n"
            "means a name like \"Commercial_Nov25\" can be read as version 25.")
        self.separator_check.setChecked(self.settings.require_separator)
        self.separator_check.stateChanged.connect(self._options_changed)

        options = QtWidgets.QVBoxLayout()
        options.setSpacing(8)
        options.addWidget(self.case_check)
        options.addWidget(self.separator_check)

        return options

    def _build_footer(self):

        self.error_label = QtWidgets.QLabel("")
        self.error_label.setObjectName("error")
        self.error_label.setWordWrap(True)

        path_label = label("Preferences file:  %s" % config_path(), "hint")
        path_label.setWordWrap(True)

        button_row = QtWidgets.QHBoxLayout()
        button_row.setSpacing(8)
        button_row.addWidget(path_label)
        button_row.addStretch()
        button_row.addWidget(button("Cancel", self.reject))
        button_row.addWidget(button("Save", self._save, confirm=True))

        footer = QtWidgets.QVBoxLayout()
        footer.setSpacing(8)
        footer.addWidget(self.error_label)
        footer.addLayout(button_row)

        return footer

    # -------------------------------------

    def add_prefix(self, prefix):
        """
        Add a prefix found in the item names. Used when the mismatch dialog offers to add
        the prefix it detected.
        """

        if prefix.lower() not in [known.lower() for known in self.settings.prefixes]:
            self.settings.prefixes.append(prefix)
            self._reload_list()

    def _reload_list(self):
        """
        Rebuild the list from settings. Rows are editable in place.
        """

        self._loading = True
        self.prefix_list.clear()

        for prefix in self.settings.prefixes:
            item = QtWidgets.QListWidgetItem(prefix)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.prefix_list.addItem(item)

        self._loading = False

        self._refresh()

    def _read_list(self):
        """
        The prefixes currently in the list, blank rows dropped.
        """

        rows = [self.prefix_list.item(row).text().strip()
                for row in range(self.prefix_list.count())]

        return [prefix for prefix in rows if prefix]

    def _add_row(self):

        # Reuse a blank row rather than stacking up more of them.
        for row in range(self.prefix_list.count()):
            if not self.prefix_list.item(row).text().strip():
                self.prefix_list.setCurrentRow(row)
                self.prefix_list.editItem(self.prefix_list.item(row))
                return

        item = QtWidgets.QListWidgetItem("")
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

        self._loading = True
        self.prefix_list.addItem(item)
        self._loading = False

        self.prefix_list.setCurrentRow(self.prefix_list.count() - 1)
        self.prefix_list.editItem(item)

    def _remove_row(self):

        row = self.prefix_list.currentRow()

        if row < 0:
            return

        self.prefix_list.takeItem(row)
        self.settings.prefixes = self._read_list()
        self._refresh()

    def _prefix_edited(self, item):

        if self._loading:
            return

        self.settings.prefixes = self._read_list()
        self._refresh()

    def _options_changed(self, *args):

        self.settings.case_sensitive = self.case_check.isChecked()
        self.settings.require_separator = self.separator_check.isChecked()
        self._refresh()

    def _refresh(self):
        """
        Update the preview and the error line for the current settings.
        """

        problem = self.settings.error()

        self.error_label.setText(problem or "")

        if problem:
            self.preview.setPlainText("")
            return

        lines = []

        for prefix in self.settings.prefixes:
            sample = SAMPLE_NAME.format(token=prefix + "01")
            result = version_up_name(sample, self.settings)
            lines.append("%s   →   %s" % (sample, result[0] if result else "no match"))

        self.preview.setPlainText("\n".join(lines))

    # -------------------------------------

    def _save(self):

        self.settings.prefixes = self._read_list()

        problem = self.settings.error()

        if problem:
            self.error_label.setText(problem)
            return

        error = self.settings.save()

        if error:
            self.error_label.setText(error)
            return

        self.saved = True
        self.accept()


# -------------------------------------
# [Mismatch window]
# -------------------------------------

class MismatchWindow(FlameDialog):
    """
    Shown when selected items have no version matching any known prefix. Offers to add the
    prefix it detected, or to open Preferences.
    """

    def __init__(self, skipped_names, settings, versioned_count):

        # Grow with the number of skipped names instead of leaving a half empty box.
        rows = max(3, min(len(skipped_names), 12))

        super(MismatchWindow, self).__init__("Version Not Found", 700, 230 + rows * 19)

        self.settings = settings
        self.choice = "skip"
        self.detected_prefix = detect_prefix(skipped_names, settings)
        self.case_prefix = None

        total = len(skipped_names) + versioned_count

        summary = "%d of %d selected %s no version using your prefixes  (%s)." % (
            len(skipped_names), total,
            "item has" if len(skipped_names) == 1 else "items have",
            settings.summary())

        summary_label = label(summary)
        summary_label.setWordWrap(True)

        if self.detected_prefix:
            detail = label("They look like they use \"%s\"." % self.detected_prefix)
        else:
            self.case_prefix = detect_case_mismatch(skipped_names, settings)

            if self.case_prefix:
                detail = label(
                    "They use a different case of your \"%s\" prefix. Turn off Case sensitive "
                    "in Preferences to match both." % self.case_prefix)
            else:
                detail = label("No version number was found in these names at all.")

        detail.setWordWrap(True)

        name_list = QtWidgets.QTextEdit()
        name_list.setReadOnly(True)
        name_list.setPlainText("\n".join(skipped_names))

        self.body_layout.addWidget(summary_label)
        self.body_layout.addWidget(detail)
        self.body_layout.addWidget(label("Skipped:"))
        self.body_layout.addWidget(name_list)

        buttons = QtWidgets.QHBoxLayout()
        buttons.setSpacing(8)
        buttons.addWidget(button("Skip These Items", self.reject))
        buttons.addStretch()

        if self.detected_prefix:
            buttons.addWidget(button("Preferences", lambda: self._choose("preferences")))
            buttons.addWidget(button(
                "Add \"%s\" And Version Up" % self.detected_prefix,
                lambda: self._choose("add"), confirm=True))
        else:
            buttons.addWidget(button("Preferences", lambda: self._choose("preferences"), confirm=True))

        self.body_layout.addLayout(buttons)

    def _choose(self, choice):

        self.choice = choice
        self.accept()


# -------------------------------------
# [Main]
# -------------------------------------

def apply_version_up(items, settings):
    """
    Version up every item that has a known version.

    Returns (versioned_count, skipped_items).
    """

    versioned = 0
    skipped = []

    for item in items:
        name = item_name(item)
        result = version_up_name(name, settings)

        if result is None:
            print("Skipped:  %s   (no version found using %s)" % (name, settings.summary()))
            skipped.append(item)
            continue

        new_name, old_token, new_token = result

        print("%s   ->   %s      [%s -> %s]" % (name, new_name, old_token, new_token))
        item.name = new_name
        versioned += 1

    return versioned, skipped


def print_header(settings):

    print("*" * 100)
    print("%s %s" % (SCRIPT_NAME, SCRIPT_VERSION))
    print("Version Prefixes:  %s" % settings.summary())
    print("-" * 100)


def print_result(versioned, skipped_count):

    print("-" * 100)
    print("Versioned up: %d      Skipped: %d" % (versioned, skipped_count))


def print_footer():

    print("*" * 100)
    print("\n" * 2)


def version_upper(selection):

    settings = Settings.load()

    print_header(settings)

    problem = settings.error()

    if problem:
        print(problem)
        print_footer()
        show_in_flame(problem)
        open_preferences()
        return

    versioned, skipped = apply_version_up(list(selection), settings)
    print_result(versioned, len(skipped))

    if not skipped:
        print_footer()
        return

    if not qt_available():
        print_footer()
        show_in_flame("%d items have no version using %s." % (len(skipped), settings.summary()))
        return

    window = MismatchWindow([item_name(item) for item in skipped], settings, versioned)
    exec_dialog(window)

    # The preferences path hands off to open_preferences, which prints its own result
    # once the window closes.
    if window.choice == "preferences":
        open_preferences(retry_items=skipped)
        return

    if window.choice == "add":
        settings.prefixes.append(window.detected_prefix)
        error = settings.save()

        if error:
            print(error)
            print_footer()
            show_in_flame(error)
            return

        print("Added \"%s\" to your version prefixes." % window.detected_prefix)

        versioned, still_skipped = apply_version_up(skipped, settings)
        print_result(versioned, len(still_skipped))

    print_footer()


def open_preferences(add_prefix=None, retry_items=None):
    """
    Open the Preferences window. If retry_items are given, they are versioned up with the
    saved settings once preferences are saved.
    """

    if not qt_available():
        print("%s: PySide6 or PySide2 is required for the Preferences window." % SCRIPT_NAME)
        return

    window = PreferencesWindow(Settings.load(), add_prefix=add_prefix)

    exec_dialog(window)

    if not window.saved:
        print_footer()
        return

    settings = window.settings

    print("Preferences saved. Version prefixes: %s" % settings.summary())

    if not retry_items:
        print_footer()
        return

    versioned, skipped = apply_version_up(retry_items, settings)
    print_result(versioned, len(skipped))
    print_footer()

    if skipped:
        show_in_flame("%d items still have no version using %s." % (len(skipped), settings.summary()))


# -------------------------------------
# [Flame Menus]
# -------------------------------------

def preferences_from_menu(*args):
    """
    Menu entry point. Flame passes a selection from the media panel and nothing from the
    main menu, so both are swallowed here.
    """

    open_preferences()


def scope_not_desktop(selection):
    import flame

    for item in selection:
        if not isinstance(item, flame.PyDesktop):
            return True
    return False


def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': action_name,
                    'isVisible': scope_not_desktop,
                    'execute': version_upper,
                    'minimumVersion': '2020'
                },
                {
                    'name': '%s Preferences' % action_name,
                    'execute': preferences_from_menu,
                    'minimumVersion': '2020'
                }
            ]
        }
    ]


def get_main_menu_custom_ui_actions():

    return [
        {
            'name': action_name,
            'actions': [
                {
                    'name': 'Preferences',
                    'execute': preferences_from_menu,
                    'minimumVersion': '2020'
                }
            ]
        }
    ]
