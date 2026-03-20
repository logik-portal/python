# -*- coding: utf-8 -*-
"""
Script Name: Versions from CSV
Script Version: v1.0.0
Flame Version: 2025
Written by: Quinn Richardson + Claude
Creation Date: 09.22.25

Description:

    Prompts for a CSV file containing names, then duplicates
    the selected Sequences in the Media Panel and renames
    the duplicates according to the CSV entries using flame.media_panel.copy().

Usage:

    First- for each sequence you need to create, make or save a CSV file
    with one entry per line for each sequence you need to create.

    -In Flame-
    Right-click selected sequence on the desktop or desktop reel -->
    "Choose Duplicate from CSV" --> Run
    Select the Browse button to locate your CSV file.
    Once you click CONFIRM, the script will run, creating your sequences.

To Install:

    For all users, copy this file to:
    /opt/Autodesk/shared/python

    For a specific user on Linux, copy this file to:
    ~/flame/python

    For a specific user on Mac, copy this file to:
    /User/user_name/Library/Preferences/Autodesk/flame/python
"""

import flame
import csv
from PySide6 import QtWidgets
import time


# ---------------- CSV READING ---------------- #

def get_csv_names(path):
    """Read CSV file and return a list of names."""
    names = []
    try:
        with open(path, newline="", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row and row[0].strip():
                    names.append(row[0].strip())
    except Exception as e:
        print(f"Error reading CSV: {e}")
    return names


# ---------------- DUPLICATION USING FLAME.MEDIA_PANEL.COPY ---------------- #

def duplicate_and_rename(selection, names):
    """Duplicate selected sequences using flame.media_panel.copy() and rename them from CSV list."""

    for item in selection:
        print(f"\nProcessing item: '{item.name}' (type: {type(item)})")

        # Only work with sequences
        if not isinstance(item, flame.PySequence):
            print(f"Skipping non-sequence item: {item.name}")
            continue

        # Get the parent reel where the sequence currently exists
        parent_reel = item.parent
        print(f"Source parent reel: '{parent_reel.name if parent_reel else 'None'}'")

        if not parent_reel:
            print("✗ No parent reel found - cannot duplicate")
            continue

        # Keep track of how many sequences were in the reel before
        sequences_before = len([s for s in parent_reel.children if isinstance(s, flame.PySequence)])

        # Duplicate the sequence for each name in the CSV
        for i, new_name in enumerate(names):
            try:
                print(f"  Creating duplicate {i+1}/{len(names)}: '{new_name}'")

                # Use flame.media_panel.copy() to duplicate the sequence (without rename parameter)
                flame.media_panel.copy(
                    source_entries=[item],
                    destination=parent_reel,
                    duplicate_action='add'
                )

                # Give Flame a moment to create the duplicate
                time.sleep(0.1)

                # Find the newly created sequence (it should be the last one added)
                current_sequences = [s for s in parent_reel.children if isinstance(s, flame.PySequence)]

                if len(current_sequences) > sequences_before:
                    # Find the newest sequence (should be the duplicate)
                    new_sequences = current_sequences[sequences_before:]
                    if new_sequences:
                        duplicate = new_sequences[-1]  # Get the last added sequence

                        # Rename the duplicate
                        original_name = duplicate.name
                        duplicate.name = new_name

                        print(f"  ✓ Successfully duplicated '{item.name}' as '{duplicate.name}'")
                        sequences_before += 1  # Update count for next iteration
                    else:
                        print(f"  ✗ Could not find the newly created duplicate")
                else:
                    print(f"  ✗ Duplication may have failed - sequence count didn't increase")

            except Exception as e:
                print(f"  ✗ Error duplicating '{item.name}' for name '{new_name}': {e}")


# ---------------- ALTERNATIVE APPROACH: FIND DUPLICATES BY NAME PATTERN ---------------- #

def find_and_rename_duplicates(original_item, parent_reel, names):
    """Alternative approach: find duplicates by name pattern and rename them."""
    print(f"  Using alternative approach to find duplicates of '{original_item.name}'")

    # Look for sequences that might be duplicates (typically named "Original Name copy", "Original Name copy 2", etc.)
    potential_duplicates = []
    base_name = original_item.name

    for seq in parent_reel.children:
        if isinstance(seq, flame.PySequence) and seq != original_item:
            seq_name = seq.name
            # Check if this might be a duplicate
            if (seq_name.startswith(base_name) and
                ('copy' in seq_name.lower() or seq_name == base_name)):
                potential_duplicates.append(seq)

    print(f"  Found {len(potential_duplicates)} potential duplicates")

    # Rename the duplicates to the CSV names
    renamed_count = 0
    for i, (duplicate, new_name) in enumerate(zip(potential_duplicates, names)):
        try:
            old_name = duplicate.name
            duplicate.name = new_name
            print(f"  ✓ Renamed '{old_name}' to '{new_name}'")
            renamed_count += 1
        except Exception as e:
            print(f"  ✗ Failed to rename duplicate to '{new_name}': {e}")

    return renamed_count


# ---------------- DIALOG ---------------- #

class CSVDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CSVDialog, self).__init__(parent)
        self.setWindowTitle("Select CSV File")
        self.setFixedSize(400, 120)

        layout = QtWidgets.QVBoxLayout(self)

        self.label = QtWidgets.QLabel("CSV File:")
        layout.addWidget(self.label)

        file_layout = QtWidgets.QHBoxLayout()
        self.line_edit = QtWidgets.QLineEdit()
        self.browse_button = QtWidgets.QPushButton("Browse…")
        self.browse_button.clicked.connect(self.browse)
        file_layout.addWidget(self.line_edit)
        file_layout.addWidget(self.browse_button)
        layout.addLayout(file_layout)

        button_layout = QtWidgets.QHBoxLayout()
        self.confirm_button = QtWidgets.QPushButton("Confirm")
        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.confirm_button.clicked.connect(self.confirm)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.csv_path = None

    def browse(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        if file_path:
            self.line_edit.setText(file_path)

    def confirm(self):
        if self.line_edit.text():
            self.csv_path = self.line_edit.text()
            self.accept()
        else:
            # Visual warning instead of QMessageBox
            self.label.setText("CSV File: [Please select a file!]")
            self.label.setStyleSheet("color: rgb(255, 80, 80); font: 14px 'Discreet'")


# ---------------- MAIN EXECUTION ---------------- #

def duplicate_from_csv(selection):
    if not selection:
        print("No items selected.")
        return

    print("=== DUPLICATE SEQUENCES FROM CSV ===")
    print(f"Selected {len(selection)} item(s) for duplication")

    # Show what's selected
    for item in selection:
        print(f"  - {item.name} (type: {type(item).__name__})")

    # Open CSV selection dialog
    app = QtWidgets.QApplication.instance()
    dialog = CSVDialog(parent=app.activeWindow())
    if dialog.exec() != QtWidgets.QDialog.Accepted:
        print("User cancelled CSV selection.")
        return

    csv_path = dialog.csv_path
    if not csv_path:
        print("No CSV selected.")
        return

    names = get_csv_names(csv_path)
    if not names:
        print("No valid names found in CSV.")
        return

    print(f"\nFound {len(names)} names in CSV:")
    for i, name in enumerate(names):
        print(f"  {i+1:2d}. {name}")

    print(f"\nThis will create {len(selection)} × {len(names)} = {len(selection) * len(names)} duplicates")

    duplicate_and_rename(selection, names)
    print("\n=== DUPLICATION PROCESS COMPLETED ===")
    print("\nIf the automatic renaming didn't work, you may need to manually rename the duplicates.")


# ---------------- FLAME HOOK ---------------- #

def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Duplicate from CSV",
            "actions": [
                {
                    "name": "Run",
                    "isVisible": lambda selection: all(
                        isinstance(item, (flame.PyClip, flame.PySequence)) for item in selection
                    ),
                    "execute": duplicate_from_csv,
                }
            ],
        }
    ]
