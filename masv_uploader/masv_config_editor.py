"""
Script Name: MASV Uploader Config Editor
Script Version: 1.0.0
Flame Version: 2025
Written by: John Cursor with guidance from John Geehreng
Creation Date: 06.13.26

Custom Action Type: Main Menu

Description:

    MASV Uploader — Config Editor

Menu:
    Main Menu → MASV Uploader → Edit Config

To install:

    Copy script into /opt/Autodesk/shared/python/masv_uploader or whereever you keep you scripts

Updates:
    v1.0 06.13.26
        Initial version
"""

import json
import os
from pathlib import Path

import flame
from PySide6 import QtCore, QtWidgets

from lib.masv_api import DEFAULT_CONFIG, GLOBAL_CONFIG_PATH, MENU_NAME, PRESETS_DIR, format_recipients_for_edit


def log(msg: str) -> None:
    print(f"[{MENU_NAME} Config Editor] {msg}")


def _load_json(path: str, fallback: dict = None) -> dict:
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception as e:
        log(f"WARNING: Error loading {path}: {e}")
    return dict(fallback or {})


def _save_json(path: str, data: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w") as f:
        json.dump(data, f, indent=2)
    log(f"Saved {path}")


class MASVConfigEditor(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"{MENU_NAME} — Config Editor")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(520, 460)
        self.setMinimumSize(480, 420)
        self.setCursor(QtCore.Qt.ArrowCursor)

        self._cfg = _load_json(GLOBAL_CONFIG_PATH, DEFAULT_CONFIG)

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 12)
        form = QtWidgets.QFormLayout()
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        form.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        form.setVerticalSpacing(10)
        form.setHorizontalSpacing(12)
        root.addLayout(form)

        form.addRow(_separator("MASV Account"))

        self.api_key_edit = QtWidgets.QLineEdit()
        self.api_key_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("Paste your MASV API key")
        form.addRow("API Key:", self.api_key_edit)

        self.team_id_edit = QtWidgets.QLineEdit()
        self.team_id_edit.setPlaceholderText("Paste your MASV team ID")
        form.addRow("Team ID:", self.team_id_edit)

        self.recipients_edit = QtWidgets.QLineEdit()
        self.recipients_edit.setPlaceholderText("email@example.com, client@studio.com  (optional)")
        form.addRow("Default Recipients:", self.recipients_edit)

        form.addRow(_separator("Export Paths"))

        self.jobs_folder_edit = QtWidgets.QLineEdit()
        self.jobs_folder_edit.setPlaceholderText("Folder where exports are staged before upload")
        jobs_row = QtWidgets.QHBoxLayout()
        jobs_row.addWidget(self.jobs_folder_edit)
        browse_jobs_btn = QtWidgets.QPushButton("Browse…")
        browse_jobs_btn.setFixedWidth(90)
        browse_jobs_btn.clicked.connect(self._browse_jobs_folder)
        jobs_row.addWidget(browse_jobs_btn)
        form.addRow("Jobs Folder:", jobs_row)

        presets_info = QtWidgets.QLabel(PRESETS_DIR)
        presets_info.setStyleSheet("color: gray;")
        form.addRow("Export Presets Folder:", presets_info)

        form.addRow(_separator("Logging"))
        self.debug_check = QtWidgets.QCheckBox("Enable verbose debug logging")
        form.addRow("Debug:", self.debug_check)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.clicked.connect(self._save)
        reload_btn = QtWidgets.QPushButton("Reload")
        reload_btn.clicked.connect(self._reload)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(reload_btn)
        btn_row.addWidget(close_btn)
        root.addLayout(btn_row)

        path_label = QtWidgets.QLabel(
            f"<small><b>Config file:</b> {GLOBAL_CONFIG_PATH}</small>"
        )
        path_label.setTextFormat(QtCore.Qt.RichText)
        path_label.setAlignment(QtCore.Qt.AlignCenter)
        root.addWidget(path_label)

        self._populate()

    def _populate(self) -> None:
        self.api_key_edit.setText(self._cfg.get("masv_api_key", ""))
        self.team_id_edit.setText(self._cfg.get("masv_team_id", ""))
        self.recipients_edit.setText(
            format_recipients_for_edit(self._cfg.get("default_recipients", ""))
        )
        self.jobs_folder_edit.setText(self._cfg.get("jobs_folder", ""))
        self.debug_check.setChecked(bool(self._cfg.get("debug", False)))

    def _browse_jobs_folder(self) -> None:
        start = self.jobs_folder_edit.text().strip() or os.path.expanduser("~")
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Jobs Folder", start
        )
        if folder:
            self.jobs_folder_edit.setText(folder)

    def _save(self) -> None:
        self._cfg.update({
            "masv_api_key": self.api_key_edit.text().strip(),
            "masv_team_id": self.team_id_edit.text().strip(),
            "default_recipients": self.recipients_edit.text().strip(),
            "jobs_folder": self.jobs_folder_edit.text().strip(),
            "debug": bool(self.debug_check.isChecked()),
        })
        _save_json(GLOBAL_CONFIG_PATH, self._cfg)
        QtWidgets.QMessageBox.information(self, "Saved", "Settings saved successfully.")

    def _reload(self) -> None:
        self._cfg = _load_json(GLOBAL_CONFIG_PATH, self._cfg)
        self._populate()


def _separator(label: str) -> QtWidgets.QLabel:
    lbl = QtWidgets.QLabel(f"<b>{label}</b>")
    lbl.setTextFormat(QtCore.Qt.RichText)
    return lbl


def launch_editor(*args, **kwargs) -> None:
    try:
        MASVConfigEditor().exec()
    except Exception as e:
        print(f"[{MENU_NAME} Config Editor] ERROR: {e}")


def get_main_menu_custom_ui_actions():
    return [
        {
            "hierarchy": [MENU_NAME],
            "actions": [
                {
                    "name": "Edit Config",
                    "execute": launch_editor,
                    "minimumVersion": "2025",
                }
            ],
        }
    ]
