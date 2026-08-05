"""
Script Name: Color Shots by Effect
Script Version: 1.0
Flame Version: 2021.1
Written by: Bryan Bayley
Creation Date: 08.04.26

Description:
Color all segments containing a chosen timeline effect (Action, Image, Blur,
Timewarp, etc.). Scans the selected sequences for the timeline effect types
actually present, lets you pick one plus a color, and colors every segment
carrying that effect. Gives a quick visual overview of effected shots during
conform or finishing. Generalized version of Color Timewarp Shots.

Menus:
Right-click a sequence in the Media Panel -> Sequence... -> Color Shots by Effect
"""

import traceback

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

SCRIPT_NAME = "Color Shots by Effect"

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
]


def message_box(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(SCRIPT_NAME)
    msg.setText(message)
    msg.exec_()


def segment_effect_types(segment):
    return {str(tlfx.type) for tlfx in segment.effects}


def count_effect_types(sequences):
    counts = {}
    for sequence in sequences:
        for version in sequence.versions:
            for track in version.tracks:
                for segment in track.segments:
                    for fx_type in segment_effect_types(segment):
                        counts[fx_type] = counts.get(fx_type, 0) + 1
    return counts


def choose_effect_and_colour(counts):
    dialog = QtWidgets.QDialog()
    dialog.setWindowTitle(SCRIPT_NAME)
    layout = QtWidgets.QVBoxLayout(dialog)

    layout.addWidget(QtWidgets.QLabel("Timeline effect:"))
    effect_combo = QtWidgets.QComboBox()
    for fx_type in sorted(counts):
        effect_combo.addItem("%s (%d)" % (fx_type, counts[fx_type]), fx_type)
    layout.addWidget(effect_combo)

    layout.addWidget(QtWidgets.QLabel("Segment color:"))
    colour_combo = QtWidgets.QComboBox()
    for name, rgb in COLOURS:
        colour_combo.addItem(name, rgb)
    colour_combo.addItem("Custom...", None)
    layout.addWidget(colour_combo)

    buttons = QtWidgets.QDialogButtonBox(
        QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
    buttons.accepted.connect(dialog.accept)
    buttons.rejected.connect(dialog.reject)
    layout.addWidget(buttons)

    if dialog.exec_() != QtWidgets.QDialog.Accepted:
        return None, None

    colour = colour_combo.currentData()
    if colour is None:
        picked = QtWidgets.QColorDialog.getColor()
        if not picked.isValid():
            return None, None
        colour = tuple(
            round(value / 255 * 100)
            for value in (picked.red(), picked.green(), picked.blue()))

    return effect_combo.currentData(), colour


def color_shots_by_effect(selection):
    sequences = [item for item in selection if isinstance(item, flame.PySequence)]

    counts = count_effect_types(sequences)
    if not counts:
        message_box("No timeline effects found in the selected sequences.")
        return

    fx_type, colour = choose_effect_and_colour(counts)
    if fx_type is None:
        return

    colored = 0
    locked = 0
    errored = 0
    for sequence in sequences:
        for version in sequence.versions:
            for track in version.tracks:
                for segment in track.segments:
                    if fx_type not in segment_effect_types(segment):
                        continue
                    try:
                        segment.colour = colour
                        colored += 1
                    except Exception as err:
                        if "locked" in str(err).lower():
                            locked += 1
                        else:
                            errored += 1
                            traceback.print_exc()
    print("%s: colored %d segments containing %s (%d locked, %d errors)"
          % (SCRIPT_NAME, colored, fx_type, locked, errored))

    if locked or errored:
        summary = ["Colored %d segments containing %s." % (colored, fx_type)]
        if locked:
            summary.append("%d segments skipped — locked." % locked)
        if errored:
            summary.append("%d segments failed — see shell for details." % errored)
        message_box("\n\n".join(summary))


def scope_seq(selection):
    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Sequence...",
            "actions": [
                {
                    "name": "Color Shots by Effect",
                    "isVisible": scope_seq,
                    "execute": color_shots_by_effect,
                    "minimumVersion": "2021"
                }
            ]
        }
    ]
