"""
Script Name: New Project Setup
Script Version: 1.0
Flame Version: 2023
Written by: Bryan Bayley
Creation Date: 08.05.26

Description:
Configurable one-click new-project setup. Customize the number of reels on the Desktop, their color and names.
Rename the default library, create a Reel Group with custom reels and sequence reels. Load a set of bookmarks.
The first time any action is used, a setup window asks how the project should be laid out — desktop reels,
library naming, an online reel group, and a bookmarks template file — and saves the answers to a JSON file 
next to the script. Every action (or All The Things) then runs with the saved settings. Change the settings anytime
with Setup... in the same menu.

Menus:
Right-click the Workspace in the Media Panel -> New Project Setup -> Clean Desktop
Right-click the Workspace in the Media Panel -> New Project Setup -> Clear and Rename Library
Right-click the Workspace in the Media Panel -> New Project Setup -> Create ReelGroup for Online
Right-click the Workspace in the Media Panel -> New Project Setup -> Create Standard Project Bookmarks
Right-click the Workspace in the Media Panel -> New Project Setup -> All The Things
Right-click the Workspace in the Media Panel -> New Project Setup -> Setup...
"""

import json
import os
import shutil
import traceback

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

SCRIPT_NAME = "New Project Setup"
FOLDER = "New Project Setup"
CONFIG_FILE_NAME = "new_project_setup_config.json"

# Flame colours are RGB tuples with values 0-100.
COLOURS = [
    ("Dark Red", (96, 12, 12)),
    ("Orange", (90, 55, 10)),
    ("Yellow", (88, 80, 10)),
    ("Green", (15, 70, 20)),
    ("Teal", (10, 65, 65)),
    ("Blue", (15, 40, 90)),
    ("Purple", (55, 20, 85)),
    ("Pink", (90, 40, 65)),
    ("Grey", (50, 50, 50)),
    ("Black", (0, 0, 0)),
]

DEFAULT_CONFIG = {
    "desktop": {
        "reel_group_name": "Reels",
        "reel_group_colour": [0, 50, 0],
        "reels": [
            {"name": "Reel1", "sequence": False, "colour": [29, 67, 45]},
            {"name": "Reel2", "sequence": False, "colour": [29, 67, 45]},
            {"name": "Reel3", "sequence": False, "colour": [29, 67, 45]},
        ],
        "batch_group_name": "Batch",
        "batch_group_colour": [0, 0, 50],
    },
    "library": {
        "rename_to_project": True,
        "custom_name": "",
        "colour": [96, 12, 12],
        "clear_default_sequences": True,
    },
    "online": {
        "reel_group_name": "Online Assemble",
        "reel_group_colour": [50, 0, 0],
        "reels": [
            {"name": "_Sources Sequence", "sequence": True, "colour": [0, 0, 0]},
            {"name": "Sources", "sequence": False, "colour": [29, 67, 45]},
            {"name": "Conform", "sequence": True, "colour": [96, 12, 12]},
        ],
    },
    "bookmarks": {
        "template_path": "",
    },
}


def message_box(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(SCRIPT_NAME)
    msg.setText(message)
    msg.exec()


# ---------------------------------------------------------------- settings --

def config_paths():
    # Preferred location is next to the script (shared with everyone loading
    # it); the home directory is the fallback when that is not writable.
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return [
        os.path.join(script_dir, CONFIG_FILE_NAME),
        os.path.join(os.path.expanduser("~"), "." + CONFIG_FILE_NAME),
    ]


def merge_defaults(config, defaults):
    merged = {}
    for key, default in defaults.items():
        value = config.get(key, default)
        if isinstance(default, dict) and isinstance(value, dict):
            value = merge_defaults(value, default)
        merged[key] = value
    return merged


def load_config():
    for path in config_paths():
        if os.path.isfile(path):
            try:
                with open(path) as config_file:
                    return merge_defaults(json.load(config_file), DEFAULT_CONFIG)
            except (OSError, ValueError):
                traceback.print_exc()
    return None


def save_config(config):
    for path in config_paths():
        try:
            with open(path, "w") as config_file:
                json.dump(config, config_file, indent=4)
        except OSError:
            traceback.print_exc()
            continue
        print("%s: settings saved to %s" % (SCRIPT_NAME, path))
        return True
    message_box("Could not save settings — see shell for details.")
    return False


# ---------------------------------------------------------------- setup UI --

def qt_rgb(colour):
    return "rgb(%d, %d, %d)" % tuple(round(value * 2.55) for value in colour)


class ColourButton(QtWidgets.QPushButton):
    """Swatch button holding a 0-100 RGB colour; click for presets/custom."""

    def __init__(self, colour):
        super().__init__()
        self.setFixedWidth(100)
        self.set_colour(colour)
        self.clicked.connect(self.pick_colour)

    def set_colour(self, colour):
        self.colour = list(colour)
        text_colour = "black" if sum(colour) > 150 else "white"
        self.setStyleSheet("background-color: %s; color: %s"
                           % (qt_rgb(colour), text_colour))
        for name, rgb in COLOURS:
            if list(rgb) == self.colour:
                self.setText(name)
                return
        self.setText("Custom")

    def pick_colour(self):
        menu = QtWidgets.QMenu(self)
        for name, rgb in COLOURS:
            menu.addAction(name)
        menu.addAction("Custom...")
        chosen = menu.exec_(self.mapToGlobal(self.rect().bottomLeft()))
        if chosen is None:
            return
        for name, rgb in COLOURS:
            if chosen.text() == name:
                self.set_colour(rgb)
                return
        picked = QtWidgets.QColorDialog.getColor()
        if picked.isValid():
            self.set_colour([
                round(value / 255 * 100)
                for value in (picked.red(), picked.green(), picked.blue())])


class ReelListEditor(QtWidgets.QWidget):
    """Editable list of reels: name, Reel/Sequence Reel type, and colour."""

    def __init__(self, reels):
        super().__init__()
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.rows = []
        self.rows_layout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.rows_layout)
        add_button = QtWidgets.QPushButton("Add Reel")
        add_button.clicked.connect(lambda: self.add_row())
        layout.addWidget(add_button)
        for reel in reels:
            self.add_row(reel)

    def add_row(self, reel=None):
        if reel is None:
            reel = {"name": "", "sequence": False, "colour": [50, 50, 50]}
        row = QtWidgets.QWidget()
        row_layout = QtWidgets.QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        name_edit = QtWidgets.QLineEdit(reel["name"])
        name_edit.setPlaceholderText("Reel name")
        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(["Reel", "Sequence Reel"])
        type_combo.setCurrentIndex(1 if reel["sequence"] else 0)
        colour_button = ColourButton(reel["colour"])
        remove_button = QtWidgets.QPushButton("✕")
        remove_button.setFixedWidth(28)
        row_layout.addWidget(name_edit)
        row_layout.addWidget(type_combo)
        row_layout.addWidget(colour_button)
        row_layout.addWidget(remove_button)
        entry = (row, name_edit, type_combo, colour_button)
        self.rows.append(entry)
        remove_button.clicked.connect(lambda: self.remove_row(entry))
        self.rows_layout.addWidget(row)

    def remove_row(self, entry):
        self.rows.remove(entry)
        row = entry[0]
        row.setParent(None)
        row.deleteLater()

    def reel_configs(self):
        reels = []
        for row, name_edit, type_combo, colour_button in self.rows:
            name = name_edit.text().strip()
            if not name:
                continue
            reels.append({
                "name": name,
                "sequence": type_combo.currentIndex() == 1,
                "colour": list(colour_button.colour),
            })
        return reels


class SetupDialog(QtWidgets.QDialog):

    def __init__(self, config, first_run=False):
        super().__init__()
        self.setWindowTitle("%s — Setup" % SCRIPT_NAME)
        self.setMinimumWidth(640)
        layout = QtWidgets.QVBoxLayout(self)

        if first_run:
            intro = QtWidgets.QLabel(
                "First run — set up how each New Project Setup action should "
                "behave. Settings are saved and can be changed later with "
                "Setup... in the same menu.")
            intro.setWordWrap(True)
            layout.addWidget(intro)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self.build_desktop_tab(config["desktop"]), "Clean Desktop")
        tabs.addTab(self.build_library_tab(config["library"]), "Library")
        tabs.addTab(self.build_online_tab(config["online"]), "Online Reel Group")
        tabs.addTab(self.build_bookmarks_tab(config["bookmarks"]), "Bookmarks")
        layout.addWidget(tabs)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Save | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    @staticmethod
    def pair(*widgets):
        holder = QtWidgets.QWidget()
        holder_layout = QtWidgets.QHBoxLayout(holder)
        holder_layout.setContentsMargins(0, 0, 0, 0)
        for widget in widgets:
            holder_layout.addWidget(widget)
        return holder

    @staticmethod
    def note_label(text):
        note = QtWidgets.QLabel(text)
        note.setWordWrap(True)
        return note

    def build_desktop_tab(self, cfg):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        form = QtWidgets.QFormLayout()
        self.desktop_group_name = QtWidgets.QLineEdit(cfg["reel_group_name"])
        self.desktop_group_colour = ColourButton(cfg["reel_group_colour"])
        form.addRow("Reel group:", self.pair(
            self.desktop_group_name, self.desktop_group_colour))
        self.batch_group_name = QtWidgets.QLineEdit(cfg["batch_group_name"])
        self.batch_group_colour = ColourButton(cfg["batch_group_colour"])
        form.addRow("Batch group:", self.pair(
            self.batch_group_name, self.batch_group_colour))
        layout.addLayout(form)
        layout.addWidget(QtWidgets.QLabel("Reels in the group:"))
        self.desktop_reels = ReelListEditor(cfg["reels"])
        layout.addWidget(self.desktop_reels)
        layout.addWidget(self.note_label(
            "Clean Desktop deletes every reel group and batch group on the "
            "desktop, then creates this layout."))
        layout.addStretch()
        return tab

    def build_library_tab(self, cfg):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        self.rename_to_project = QtWidgets.QCheckBox(
            "Rename the library to match the project name")
        self.rename_to_project.setChecked(cfg["rename_to_project"])
        layout.addWidget(self.rename_to_project)
        form = QtWidgets.QFormLayout()
        self.custom_library_name = QtWidgets.QLineEdit(cfg["custom_name"])
        self.custom_library_name.setPlaceholderText("Leave empty to keep the current name")
        self.custom_library_name.setEnabled(not cfg["rename_to_project"])
        self.rename_to_project.toggled.connect(
            lambda checked: self.custom_library_name.setEnabled(not checked))
        form.addRow("Custom name:", self.custom_library_name)
        self.library_colour = ColourButton(cfg["colour"])
        form.addRow("Library colour:", self.library_colour)
        layout.addLayout(form)
        self.clear_default_sequences = QtWidgets.QCheckBox(
            "Delete Flame's default \"Sequence\" stubs from the library")
        self.clear_default_sequences.setChecked(cfg["clear_default_sequences"])
        layout.addWidget(self.clear_default_sequences)
        layout.addWidget(self.note_label(
            "Clear and Rename Library acts on the first library in the "
            "workspace — meant for a brand-new project."))
        layout.addStretch()
        return tab

    def build_online_tab(self, cfg):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        form = QtWidgets.QFormLayout()
        self.online_group_name = QtWidgets.QLineEdit(cfg["reel_group_name"])
        self.online_group_colour = ColourButton(cfg["reel_group_colour"])
        form.addRow("Reel group:", self.pair(
            self.online_group_name, self.online_group_colour))
        layout.addLayout(form)
        layout.addWidget(QtWidgets.QLabel("Reels in the group:"))
        self.online_reels = ReelListEditor(cfg["reels"])
        layout.addWidget(self.online_reels)
        layout.addWidget(self.note_label(
            "Created inside the first library. Flame reel groups can only "
            "contain reels and sequence reels (folders are not supported "
            "inside reel groups)."))
        layout.addStretch()
        return tab

    def build_bookmarks_tab(self, cfg):
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(tab)
        form = QtWidgets.QFormLayout()
        self.bookmarks_path = QtWidgets.QLineEdit(cfg["template_path"])
        browse_button = QtWidgets.QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_bookmarks)
        form.addRow("Bookmarks file:", self.pair(
            self.bookmarks_path, browse_button))
        layout.addLayout(form)
        layout.addWidget(self.note_label(
            "Point this at a saved Flame bookmarks file. Create Standard "
            "Project Bookmarks copies it to "
            "/opt/Autodesk/project/<project>/status/cf_bookmarks.json.\n\n"
            "Tip: set up bookmarks once in any project, then use that "
            "project's status/cf_bookmarks.json as the template. Leave empty "
            "to skip bookmarks."))
        layout.addStretch()
        return tab

    def browse_bookmarks(self):
        start_dir = os.path.dirname(self.bookmarks_path.text()) \
            or "/opt/Autodesk/project"
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose a saved bookmarks file", start_dir,
            "Bookmarks (*.json);;All files (*)")
        if path:
            self.bookmarks_path.setText(path)

    def accept(self):
        if not self.desktop_group_name.text().strip() \
                or not self.batch_group_name.text().strip() \
                or not self.online_group_name.text().strip():
            message_box("Group names cannot be empty.")
            return
        if not self.desktop_reels.reel_configs():
            message_box("Clean Desktop needs at least one named reel.")
            return
        if not self.online_reels.reel_configs():
            message_box("The online reel group needs at least one named reel.")
            return
        template_path = self.bookmarks_path.text().strip()
        if template_path and not os.path.isfile(template_path):
            message_box("Note: the bookmarks file does not exist (yet):\n\n%s"
                        "\n\nSaving anyway — fix the path before running "
                        "Create Standard Project Bookmarks." % template_path)
        super().accept()

    def result_config(self):
        return {
            "desktop": {
                "reel_group_name": self.desktop_group_name.text().strip(),
                "reel_group_colour": list(self.desktop_group_colour.colour),
                "reels": self.desktop_reels.reel_configs(),
                "batch_group_name": self.batch_group_name.text().strip(),
                "batch_group_colour": list(self.batch_group_colour.colour),
            },
            "library": {
                "rename_to_project": self.rename_to_project.isChecked(),
                "custom_name": self.custom_library_name.text().strip(),
                "colour": list(self.library_colour.colour),
                "clear_default_sequences":
                    self.clear_default_sequences.isChecked(),
            },
            "online": {
                "reel_group_name": self.online_group_name.text().strip(),
                "reel_group_colour": list(self.online_group_colour.colour),
                "reels": self.online_reels.reel_configs(),
            },
            "bookmarks": {
                "template_path": self.bookmarks_path.text().strip(),
            },
        }


def run_setup(first_run=False):
    dialog = SetupDialog(load_config() or DEFAULT_CONFIG, first_run=first_run)
    if dialog.exec() != QtWidgets.QDialog.Accepted:
        return None
    config = dialog.result_config()
    if not save_config(config):
        return None
    return config


def ensure_config():
    config = load_config()
    if config is not None:
        return config
    return run_setup(first_run=True)


# ----------------------------------------------------------------- actions --

def library_is_open(library):
    opened = getattr(library, "opened", None)
    if opened is None:
        return None
    try:
        return bool(opened.get_value())
    except AttributeError:
        return bool(opened)


def library_display_name(library):
    name = str(library.name)
    if name.startswith("'") and name.endswith("'"):
        return name[1:-1]
    return name


def open_library(library):
    # A closed library silently ignores attribute writes and returns None
    # from create_reel_group — open it first and verify it actually opened.
    if library_is_open(library) is False:
        try:
            library.open()
        except Exception:
            traceback.print_exc()
    if library_is_open(library) is False:
        print("%s: library \"%s\" is closed and would not open — skipped"
              % (SCRIPT_NAME, library_display_name(library)))
        return None
    return library


PROBE_NAME = "__new_project_setup_probe"


def library_is_writable(library):
    # A library deleted in the UI can linger in the undo buffer: it still
    # lists and reads fine but silently drops writes. Probe by creating
    # (and immediately deleting) a folder.
    for folder in library.folders:
        if library_display_name(folder) == PROBE_NAME:
            flame.delete(folder)
    probe = library.create_folder(PROBE_NAME)
    if probe is None:
        return False
    flame.delete(probe)
    return True


def target_library_name(config):
    cfg = config["library"]
    if cfg["rename_to_project"]:
        return str(flame.project.current_project.name)
    if cfg["custom_name"]:
        return cfg["custom_name"]
    return None


def find_setup_library(config):
    # Never assume libraries[0] — workspaces can hold extra libraries (e.g.
    # "Timeline FX") plus ghosts of deleted libraries still in the undo
    # buffer. Prefer the library already carrying the configured name
    # (idempotent re-runs), then Flame's fresh "Default Library", and take
    # the first candidate that is open and actually accepts writes.
    libraries = flame.project.current_project.current_workspace.libraries
    wanted = target_library_name(config)
    candidates = []
    for name in [name for name in (wanted, "Default Library") if name]:
        for library in libraries:
            if library_display_name(library) == name \
                    and library not in candidates:
                candidates.append(library)
    if not candidates and len(libraries) == 1:
        candidates = [libraries[0]]

    for library in candidates:
        if open_library(library) is None:
            continue
        if library_is_writable(library):
            return library
        print("%s: library \"%s\" ignores writes (a deleted library still "
              "in the undo buffer?) — skipped"
              % (SCRIPT_NAME, library_display_name(library)))

    message_box("Could not find a writable \"Default Library\"%s in this "
                "workspace. If you just deleted a library, its ghost may "
                "still be in the undo buffer — reopening the project "
                "clears it." % (" or \"%s\"" % wanted if wanted else ""))
    return None


def populate_reel_group(reel_group, reels_config):
    # Flame auto-creates default reels with a new group — snapshot them,
    # create the configured reels, then delete the auto-created ones.
    auto_reels = list(reel_group.reels)
    for reel_config in reels_config:
        if reel_config["sequence"]:
            reel = reel_group.create_reel(reel_config["name"], sequence=True)
        else:
            reel = reel_group.create_reel(reel_config["name"])
        reel.colour = tuple(reel_config["colour"])
    if reels_config:
        for reel in auto_reels:
            flame.delete(reel)


def apply_clean_desktop(config):
    cfg = config["desktop"]
    desk = flame.project.current_project.current_workspace.desktop

    for reel_group in desk.reel_groups:
        flame.delete(reel_group)
    for batch_group in desk.batch_groups:
        flame.delete(batch_group)

    # Flame auto-creates a batch group when none exist — rename and recolor it.
    for batch_group in desk.batch_groups:
        batch_group.name = cfg["batch_group_name"]
        batch_group.colour = tuple(cfg["batch_group_colour"])

    reel_group = desk.create_reel_group(cfg["reel_group_name"])
    reel_group.colour = tuple(cfg["reel_group_colour"])
    populate_reel_group(reel_group, cfg["reels"])
    print("%s: desktop cleaned" % SCRIPT_NAME)


def apply_library(config):
    cfg = config["library"]
    library = find_setup_library(config)
    if library is None:
        return

    wanted_name = target_library_name(config)
    if wanted_name is not None:
        library.name = wanted_name
    library.colour = tuple(cfg["colour"])

    if wanted_name is not None \
            and library_display_name(library) != wanted_name:
        message_box("The library did not take the name \"%s\" — it may be "
                    "closed or locked. Current name: \"%s\""
                    % (wanted_name, library_display_name(library)))
        return

    if cfg["clear_default_sequences"]:
        for sequence in library.sequences:
            if "Sequence" in str(sequence.name):
                flame.delete(sequence)
    print("%s: library set up" % SCRIPT_NAME)


def apply_online_reel_group(config):
    cfg = config["online"]
    library = find_setup_library(config)
    if library is None:
        return
    group_name = cfg["reel_group_name"]

    # create_reel_group() returns None instead of auto-suffixing when a group
    # with that name already exists (e.g. re-running on the same project).
    for existing in library.reel_groups:
        if group_name in (str(existing.name), str(existing.name)[1:-1]):
            message_box("A reel group named \"%s\" already exists in this "
                        "library — leaving it as is." % group_name)
            print("%s: reel group \"%s\" already exists — skipped"
                  % (SCRIPT_NAME, group_name))
            return

    reel_group = library.create_reel_group(group_name)
    if reel_group is None:
        message_box("Could not create the \"%s\" reel group — make sure the "
                    "library is open (double-click it) and try again."
                    % group_name)
        return
    reel_group.colour = tuple(cfg["reel_group_colour"])
    populate_reel_group(reel_group, cfg["reels"])
    print("%s: reel group \"%s\" created" % (SCRIPT_NAME, cfg["reel_group_name"]))


def apply_bookmarks(config):
    template_file = config["bookmarks"]["template_path"]
    if not template_file:
        message_box("No bookmarks file configured.\n\nRun Setup... and point "
                    "the Bookmarks tab at a saved bookmarks file.")
        return
    if not os.path.isfile(template_file):
        message_box("Bookmarks file not found:\n\n%s" % template_file)
        return

    project_name = str(flame.project.current_project.name)
    destination_dir = os.path.join("/opt/Autodesk/project", project_name, "status")
    os.makedirs(destination_dir, exist_ok=True)
    shutil.copy(template_file, os.path.join(destination_dir, "cf_bookmarks.json"))
    print("%s: bookmarks copied to %s" % (SCRIPT_NAME, destination_dir))


def clean_desktop(selection):
    config = ensure_config()
    if config is not None:
        apply_clean_desktop(config)


def library_from_project(selection):
    config = ensure_config()
    if config is not None:
        apply_library(config)


def create_online_reel_group(selection):
    config = ensure_config()
    if config is not None:
        apply_online_reel_group(config)


def create_bookmarks(selection):
    config = ensure_config()
    if config is not None:
        apply_bookmarks(config)


def all_the_things(selection):
    config = ensure_config()
    if config is None:
        return
    steps = [
        ("Clean Desktop", apply_clean_desktop),
        ("Clear and Rename Library", apply_library),
        ("Create ReelGroup for Online", apply_online_reel_group),
        ("Create Standard Project Bookmarks", apply_bookmarks),
    ]
    failed = []
    for step_name, step in steps:
        try:
            step(config)
        except Exception:
            traceback.print_exc()
            failed.append(step_name)
    if failed:
        message_box("Some steps failed — see shell for details:\n\n"
                    + "\n".join(failed))


def open_setup(selection):
    run_setup(first_run=load_config() is None)


def scope_workspace(selection):
    for item in selection:
        if isinstance(item, flame.PyWorkspace):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": FOLDER,
            "actions": [
                {
                    "name": "Clean Desktop",
                    "isVisible": scope_workspace,
                    "execute": clean_desktop
                },
                {
                    "name": "Clear and Rename Library",
                    "isVisible": scope_workspace,
                    "execute": library_from_project
                },
                {
                    "name": "Create ReelGroup for Online",
                    "isVisible": scope_workspace,
                    "execute": create_online_reel_group
                },
                {
                    "name": "Create Standard Project Bookmarks",
                    "isVisible": scope_workspace,
                    "execute": create_bookmarks
                },
                {
                    "name": "All The Things",
                    "isVisible": scope_workspace,
                    "execute": all_the_things
                },
                {
                    "name": "Setup...",
                    "isVisible": scope_workspace,
                    "execute": open_setup
                }
            ]
        }
    ]
