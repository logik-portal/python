#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO Config Editor
Uppercut VFX Pipeline
Accessible from Main Menu → FrameIO → Edit Config

This account uses a single shared FrameIO credential (service-client token),
not per-artist tokens, so all settings — auth and pipeline — live in one
config file (shared_config.json) and one flat form.
"""

import flame
import json
import os
import webbrowser
from pathlib import Path
from PySide6 import QtWidgets, QtCore
from lib.frame_io_api import (
    validate_cfg,
    GLOBAL_CONFIG_PATH,
    DEFAULT_CONFIG,
    SCRIPT_PATH,
)

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def log(msg):
    print(f"[FrameIO Config Editor] {msg}")

def load_json(path, fallback=None):
    try:
        if os.path.exists(path):
            with open(path) as f:
                return json.load(f)
    except Exception as e:
        log(f"WARNING: Error loading {path}: {e}")
    return fallback or {}

def save_json(path, data):
    """Write JSON config safely."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    log(f"Saved {path}")

# ---------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------

FRAMEIO_DOCS_URL = "https://developer.frame.io/"

PROJECT_TOKEN_NICKNAME = "nickname"
PROJECT_TOKEN_NAME = "name"

# ---------------------------------------------------------------------
# Main UI
# ---------------------------------------------------------------------

class FrameIOConfigEditor(QtWidgets.QDialog):
    """UI for editing the shared FrameIO pipeline configuration."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("FrameIO Config Editor — Uppercut Pipeline")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(640, 460)

        self.layout = QtWidgets.QVBoxLayout(self)

        self.cfg = load_json(GLOBAL_CONFIG_PATH, dict(DEFAULT_CONFIG))

        self.build_ui()
        self.populate_fields()

    # ------------------------------------------------------
    def build_ui(self):
        form = QtWidgets.QFormLayout()
        self.layout.addLayout(form)

        # ------------------ Auth fields ------------------
        self.token = QtWidgets.QLineEdit()
        self.token.setEchoMode(QtWidgets.QLineEdit.Password)  # Mask token

        token_row = QtWidgets.QHBoxLayout()
        token_row.addWidget(self.token)

        validate_btn = QtWidgets.QPushButton("Validate Token")
        validate_btn.setFixedWidth(120)
        validate_btn.clicked.connect(self.validate_token_clicked)

        docs_btn = QtWidgets.QPushButton("Get Token")
        docs_btn.setFixedWidth(120)
        docs_btn.clicked.connect(lambda: webbrowser.open(FRAMEIO_DOCS_URL))

        token_row.addWidget(validate_btn)
        token_row.addWidget(docs_btn)

        self.client_id = QtWidgets.QLineEdit()
        self.client_id.setPlaceholderText(
            "Only needed for Adobe Admin Console-managed accounts (ask Frame.io/Adobe support)"
        )

        self.account_id = QtWidgets.QLineEdit()
        self.workspace_combo = QtWidgets.QComboBox()

        form.addRow("FrameIO Token:", token_row)
        form.addRow("Client ID:", self.client_id)
        form.addRow("Account ID:", self.account_id)
        form.addRow("Workspace:", self.workspace_combo)

        # ------------------ Pipeline settings ------------------
        self.jobs_folder = QtWidgets.QLineEdit()
        jobs_folder_row = QtWidgets.QHBoxLayout()
        jobs_folder_row.addWidget(self.jobs_folder)
        btn = QtWidgets.QPushButton("Browse...")
        btn.clicked.connect(self.browse_jobs_folder)
        btn.setFixedWidth(100)
        jobs_folder_row.addWidget(btn)

        self.h264 = QtWidgets.QLineEdit()
        h264_row = QtWidgets.QHBoxLayout()
        h264_row.addWidget(self.h264)
        btn2 = QtWidgets.QPushButton("Browse...")
        btn2.clicked.connect(self.browse_h264_preset)
        btn2.setFixedWidth(100)
        h264_row.addWidget(btn2)

        self.project_token = QtWidgets.QComboBox()
        self.project_token.addItem("Project Nickname", PROJECT_TOKEN_NICKNAME)
        self.project_token.addItem("Project Name", PROJECT_TOKEN_NAME)

        self.debug = QtWidgets.QCheckBox("Enable verbose FrameIO debug logging")
        self.file_logging = QtWidgets.QCheckBox(
            "Enable file logging (logs saved to ~/flame/python/frame_io/logs/)"
        )

        form.addRow("Jobs Folder:", jobs_folder_row)
        form.addRow("H.264 Preset Path:", h264_row)
        form.addRow("Project Token:", self.project_token)
        form.addRow("Debug Mode:", self.debug)
        form.addRow("File Logging:", self.file_logging)

        #
        # ------------------ FOOTER BUTTONS ------------------
        #
        footer_btns = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_all)
        reload_btn = QtWidgets.QPushButton("Reload")
        reload_btn.clicked.connect(self.reload)
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.clicked.connect(self.accept)

        footer_btns.addStretch()
        footer_btns.addWidget(save_btn)
        footer_btns.addWidget(reload_btn)
        footer_btns.addWidget(close_btn)

        self.layout.addLayout(footer_btns)

        #
        # ------------------ FOOTER PATH INFO ------------------
        #
        footer = QtWidgets.QLabel(f"<small><b>Config:</b> {GLOBAL_CONFIG_PATH}</small>")
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setTextFormat(QtCore.Qt.RichText)
        self.layout.addWidget(footer)

    # ------------------------------------------------------
    def populate_fields(self):
        self.token.setText(self.cfg.get("frame_io_token", ""))
        self.client_id.setText(self.cfg.get("client_id", ""))
        self.account_id.setText(self.cfg.get("frame_io_account_id", ""))

        self.workspace_combo.clear()
        saved_workspace = self.cfg.get("frame_io_workspace_id") or self.cfg.get("frame_io_team_id", "")
        if saved_workspace:
            self.workspace_combo.addItem(f"(saved) {saved_workspace}", saved_workspace)

        self.jobs_folder.setText(self.cfg.get("jobs_folder", ""))
        self.h264.setText(self.cfg.get("preset_path_h264", ""))

        token_mode = self.cfg.get("project_token", PROJECT_TOKEN_NICKNAME)
        idx = self.project_token.findData(token_mode)
        self.project_token.setCurrentIndex(idx if idx >= 0 else 0)

        self.debug.setChecked(bool(self.cfg.get("debug", False)))
        self.file_logging.setChecked(bool(self.cfg.get("enable_file_logging", False)))

    # ------------------------------------------------------
    def browse_jobs_folder(self):
        start = self.jobs_folder.text().strip() or "/Volumes"
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Jobs Folder", start)
        if folder:
            self.jobs_folder.setText(folder)

    # ------------------------------------------------------
    def browse_h264_preset(self):
        start = self.h264.text().strip() or os.path.join(SCRIPT_PATH, "presets")
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select H.264 Preset",
            start,
            "XML Files (*.xml);;All Files (*)"
        )
        if file_path:
            self.h264.setText(file_path)

    # ------------------------------------------------------
    def validate_token_clicked(self):
        """Validate FrameIO token using validate_cfg()."""
        token = self.token.text().strip()
        if not token:
            QtWidgets.QMessageBox.warning(self, "Missing Token", "Please enter your FrameIO token first.")
            return

        test_cfg = dict(self.cfg)
        test_cfg["frame_io_token"] = token
        test_cfg["client_id"] = self.client_id.text().strip()

        self.setCursor(QtCore.Qt.WaitCursor)
        ok, msg, merged = validate_cfg(test_cfg, {})
        self.setCursor(QtCore.Qt.ArrowCursor)

        if not ok:
            QtWidgets.QMessageBox.critical(self, "FrameIO", msg)
            return

        QtWidgets.QMessageBox.information(self, "FrameIO", msg)

        self.account_id.setText(merged.get("frame_io_account_id", ""))

        self.workspace_combo.clear()
        for w in merged.get("frame_io_workspaces", []):
            self.workspace_combo.addItem(f"{w['name']} ({w['id']})", w["id"])

    # ------------------------------------------------------
    def save_all(self):
        """Write the shared config file."""
        workspace_id = self.workspace_combo.currentData() or ""
        self.cfg.update(
            {
                "frame_io_token": self.token.text().strip(),
                "client_id": self.client_id.text().strip(),
                "frame_io_account_id": self.account_id.text().strip(),
                "frame_io_workspace_id": workspace_id,
                # Kept for backward compatibility with older runtime code paths.
                "frame_io_team_id": workspace_id,
                "jobs_folder": self.jobs_folder.text().strip(),
                "preset_path_h264": self.h264.text().strip(),
                "project_token": self.project_token.currentData(),
                "debug": bool(self.debug.isChecked()),
                "enable_file_logging": bool(self.file_logging.isChecked()),
            }
        )

        save_json(GLOBAL_CONFIG_PATH, self.cfg)

        QtWidgets.QMessageBox.information(self, "Saved", "Settings saved successfully.")

    # ------------------------------------------------------
    def reload(self):
        """Reload the JSON file and repopulate the UI."""
        self.cfg = load_json(GLOBAL_CONFIG_PATH, self.cfg)
        self.populate_fields()

# ---------------------------------------------------------------------
# Flame Menu Integration
# ---------------------------------------------------------------------

def launch_editor(*args, **kwargs):
    try:
        dlg = FrameIOConfigEditor()
        dlg.exec()
    except Exception as e:
        print(f"[FrameIO Config Editor] ERROR: Failed to launch: {e}")

def get_main_menu_custom_ui_actions():
    return [
        {
            "hierarchy": ["UC FrameIO"],
            "actions": [
                {
                    "name": "Edit Config",
                    "execute": launch_editor,
                    "minimumVersion": "2025",
                }
            ]
        }
    ]
