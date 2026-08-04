#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO Create Share Link v1.1.0 — Uppercut VFX Pipeline
Creates a single public FrameIO share link covering the selected clips/segments.

- Items already uploaded to FrameIO are matched by name and added directly.
- Items not yet in FrameIO are exported (H264) and uploaded first, then added.
- An options dialog lets you name the share and optionally password-protect it
  before it's created.
- The resulting share link (and password, if set) is shown in a dialog and
  copied to the clipboard.

v1.1.0 - add options dialog for share name + password protect (passphrase)
"""

import os
import glob
import secrets
import datetime
import traceback
import flame
from PySide6 import QtWidgets, QtCore
from lib.frame_io_api import (
    validate_config,
    get_fio_projects,
    create_fio_project,
    find_fio_asset,
    find_fio_folder,
    create_fio_folder,
    upload_file,
    create_share_link,
    log_error,
)

SCRIPT_NAME = "FrameIO Create Share"
VERSION = "v1.1.0"

# ----------------------------------------------------------
# Logging / messaging
# ----------------------------------------------------------

def log(msg):
    print(f"[{SCRIPT_NAME}] {msg}")

def show_message(text, title=SCRIPT_NAME):
    """Cross-version safe popup for Flame."""
    try:
        if hasattr(flame, "message_dialog"):
            flame.message_dialog(title, text)
        else:
            QtWidgets.QMessageBox.information(None, title, text)
    except Exception:
        print(f"[{SCRIPT_NAME}] {text}")

def attr(x):
    try:
        return x.get_value() if hasattr(x, "get_value") else x
    except Exception:
        return x

# ----------------------------------------------------------
# Options dialog (share name, password protect)
# ----------------------------------------------------------

class FrameIOShareOptionsDialog(QtWidgets.QDialog):
    """Collect share options (name, password protect) before creation."""

    def __init__(self, default_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("FrameIO Share Link Options — Uppercut Pipeline")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(640)
        self.resize(640, 0)

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        # Share name
        self.name_edit = QtWidgets.QLineEdit(default_name)
        self.name_edit.setMinimumWidth(420)
        form.addRow("Share Name:", self.name_edit)

        # Password protection
        pw_row = QtWidgets.QHBoxLayout()
        self.pw_enabled = QtWidgets.QCheckBox("Enable")
        self.pw_enabled.setChecked(False)
        self.pw_edit = QtWidgets.QLineEdit()
        self.pw_edit.setPlaceholderText("Password")
        self.pw_edit.setEnabled(False)
        gen_btn = QtWidgets.QPushButton("Generate")
        gen_btn.setFixedWidth(80)
        gen_btn.setEnabled(False)
        gen_btn.clicked.connect(self._generate_password)
        pw_row.addWidget(self.pw_enabled)
        pw_row.addWidget(self.pw_edit)
        pw_row.addWidget(gen_btn)
        form.addRow("Password Protect:", pw_row)
        self.pw_enabled.toggled.connect(self.pw_edit.setEnabled)
        self.pw_enabled.toggled.connect(gen_btn.setEnabled)

        # Pre-fill with a generated password so "Enable" alone is usable
        self._generate_password()

        # Buttons
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QtWidgets.QPushButton("Create Share")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._on_accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.adjustSize()

    def _generate_password(self):
        self.pw_edit.setText(secrets.token_urlsafe(9))

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validation", "Share name cannot be empty.")
            return
        if self.pw_enabled.isChecked() and not self.pw_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validation", "Enter a password or disable Password Protect.")
            return
        self.accept()

    def share_name(self):
        return self.name_edit.text().strip()

    def password(self):
        """Returns the password string, or empty string if disabled."""
        if self.pw_enabled.isChecked():
            return self.pw_edit.text().strip()
        return ""

# ----------------------------------------------------------
# Results dialog (share URL + password with copy buttons)
# ----------------------------------------------------------

class FrameIOShareResultsDialog(QtWidgets.QDialog):
    """Shows the share URL and password (if any) with one-click copy buttons."""

    def __init__(self, share_url, password="", share_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("FrameIO Share Link Created")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setMinimumWidth(640)
        self.resize(640, 0)

        layout = QtWidgets.QVBoxLayout(self)

        if share_name:
            title = QtWidgets.QLabel(f"<b>{share_name}</b> is ready to send.")
            title.setTextFormat(QtCore.Qt.RichText)
            layout.addWidget(title)
            layout.addSpacing(8)

        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        # Share URL row
        url_row = QtWidgets.QHBoxLayout()
        self.url_edit = QtWidgets.QLineEdit(share_url)
        self.url_edit.setReadOnly(True)
        copy_url_btn = QtWidgets.QPushButton("Copy")
        copy_url_btn.setFixedWidth(60)
        copy_url_btn.clicked.connect(lambda: self._copy(self.url_edit.text(), copy_url_btn))
        url_row.addWidget(self.url_edit)
        url_row.addWidget(copy_url_btn)
        form.addRow("Share URL:", url_row)

        # Password row
        pw_row = QtWidgets.QHBoxLayout()
        pw_display = password if password else "(no password set)"
        self.pw_edit = QtWidgets.QLineEdit(pw_display)
        self.pw_edit.setReadOnly(True)
        copy_pw_btn = QtWidgets.QPushButton("Copy")
        copy_pw_btn.setFixedWidth(60)
        copy_pw_btn.setEnabled(bool(password))
        copy_pw_btn.clicked.connect(lambda: self._copy(password, copy_pw_btn))
        pw_row.addWidget(self.pw_edit)
        pw_row.addWidget(copy_pw_btn)
        form.addRow("Password:", pw_row)

        layout.addSpacing(8)

        # Close button
        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        copy_all_btn = QtWidgets.QPushButton("Copy Both to Clipboard")
        copy_all_btn.clicked.connect(lambda: self._copy_both(share_url, password, copy_all_btn))
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(copy_all_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.adjustSize()

    @staticmethod
    def _copy(text, button):
        QtWidgets.QApplication.clipboard().setText(text)
        original = button.text()
        button.setText("Copied!")
        QtCore.QTimer.singleShot(1500, lambda: button.setText(original))

    @staticmethod
    def _copy_both(url, password, button):
        parts = [f"Share: {url}"]
        if password:
            parts.append(f"Password: {password}")
        QtWidgets.QApplication.clipboard().setText("\n".join(parts))
        original = button.text()
        button.setText("Copied!")
        QtCore.QTimer.singleShot(1500, lambda: button.setText(original))

# ----------------------------------------------------------
# Progress dialog
# ----------------------------------------------------------

class FrameIOProgressDialog(QtWidgets.QDialog):
    def __init__(self, total_steps, title="FrameIO Share Link"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(420, 130)

        layout = QtWidgets.QVBoxLayout(self)
        self.status_label = QtWidgets.QLabel("Preparing…")
        self.progress = QtWidgets.QProgressBar()
        self.progress.setRange(0, max(1, total_steps))

        layout.addWidget(self.status_label)
        layout.addWidget(self.progress)

    def update_step(self, idx, total, message):
        self.progress.setMaximum(max(1, total))
        self.progress.setValue(max(0, idx - 1))
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()

    def finish(self, message="Done", delay_ms=1200):
        self.progress.setValue(self.progress.maximum())
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(delay_ms, self.accept)

# ----------------------------------------------------------
# Selection classification (mirrors Get Comments / Get Status:
# a segment's identity is its parent sequence, since that's the
# asset that actually lives in FrameIO)
# ----------------------------------------------------------

def classify_selection(selection):
    entries = []
    for item in selection:
        if isinstance(item, flame.PySegment):
            sequence_obj = item.parent.parent.parent
            base_name = str(sequence_obj.name)[1:-1]
            entries.append({
                "export_target": sequence_obj,
                "base_name": base_name,
                "is_segment": True,
            })
        elif isinstance(item, flame.PyClip):
            base_name = str(item.name)[1:-1]
            entries.append({
                "export_target": item,
                "base_name": base_name,
                "is_segment": False,
            })
        else:
            log(f"WARNING: Skipping unsupported selection item: {item}")

    # De-duplicate by base name (e.g. multiple segments from the same sequence)
    unique = {}
    for e in entries:
        unique.setdefault(e["base_name"], e)
    return list(unique.values())

# ----------------------------------------------------------
# Export + upload a single missing entry, returning its new file_id
# ----------------------------------------------------------

def export_and_upload(entry, cfg, project_id, root_folder_id, export_dir, preset_path, folder_cache, progress_callback=None):
    before = set(os.listdir(export_dir))
    exporter = flame.PyExporter()
    exporter.foreground = True
    exporter.export_between_marks = False
    exporter.use_top_video_track = True
    exporter.export(entry["export_target"], preset_path, export_dir)

    after = set(os.listdir(export_dir))
    new_files = sorted(
        os.path.join(export_dir, f) for f in (after - before)
        if os.path.isfile(os.path.join(export_dir, f))
    )
    if not new_files:
        raise RuntimeError(f"Export produced no file for '{entry['base_name']}'.")

    folder_name = "CONFORMS" if entry["is_segment"] else "SHOTS"
    if folder_name not in folder_cache:
        search = find_fio_folder(cfg, project_id, folder_name)
        if search != (None, None, None, None):
            folder_cache[folder_name] = search[1]
        else:
            folder_cache[folder_name] = create_fio_folder(cfg, root_folder_id, folder_name)
    folder_id = folder_cache[folder_name]

    # Typically a single output file per exported item
    filename = new_files[0]
    file_id = upload_file(cfg, folder_id, filename, progress_callback=progress_callback)
    return file_id

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def create_share(selection):
    print(f"\n[{SCRIPT_NAME}] {VERSION} — Start")
    try:
        if not selection:
            show_message("Please select one or more clips or segments first.")
            return

        cfg = validate_config()
        project_nickname = str(attr(flame.projects.current_project.nickname))
        jobs_folder = cfg.get("jobs_folder", "/Volumes/vfx/UC_Jobs")

        log(f"Starting FrameIO Share Link creation for project '{project_nickname}'")

        try:
            root_folder_id, project_id = get_fio_projects(cfg, project_nickname)
        except Exception:
            root_folder_id, project_id = create_fio_project(cfg, project_nickname)
            create_fio_folder(cfg, root_folder_id, "SHOTS")
            create_fio_folder(cfg, root_folder_id, "CONFORMS")

        entries = classify_selection(selection)
        if not entries:
            show_message("No supported clips or segments were selected.")
            return

        # Ask for share name + optional password protect before doing any
        # (potentially slow) matching/export/upload work.
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        if len(entries) == 1:
            default_name = f"{entries[0]['base_name']} — {date_str}"
        else:
            default_name = f"{project_nickname} Review ({len(entries)} items) — {date_str}"

        options = FrameIOShareOptionsDialog(default_name=default_name)
        if options.exec() != QtWidgets.QDialog.Accepted:
            log("Share link creation cancelled by user.")
            return

        share_name = options.share_name()
        password = options.password()

        asset_ids = []
        names_for_share = []
        missing = []

        for e in entries:
            search = find_fio_asset(cfg, project_id, e["base_name"])
            asset_type, asset_id, parent_id, file_id = search
            if asset_type in ("file", "version_stack"):
                log(f"Found existing FrameIO asset for '{e['base_name']}' ({asset_type})")
                asset_ids.append(asset_id)
                names_for_share.append(e["base_name"])
            else:
                missing.append(e)

        # Export + upload anything not already in FrameIO
        if missing:
            log(f"{len(missing)} item(s) not found in FrameIO — exporting and uploading first…")
            preset_path = cfg.get("preset_path_h264")
            if not preset_path or not os.path.exists(preset_path):
                raise RuntimeError(f"Missing export preset: {preset_path}")

            now = datetime.datetime.now()
            today = now.strftime("%Y-%m-%d")
            time_str = now.strftime("%H%M%S")
            export_dir = os.path.join(jobs_folder, project_nickname, "FROM_FLAME", today, f"share_{time_str}")
            os.makedirs(export_dir, exist_ok=True)
            log(f"Export folder: {export_dir}")

            progress_dialog = FrameIOProgressDialog(len(missing), "FrameIO Share: Export & Upload")
            progress_dialog.show()
            folder_cache = {}
            had_errors = False

            try:
                for idx, e in enumerate(missing, 1):
                    progress_dialog.update_step(idx, len(missing), f"Exporting '{e['base_name']}' ({idx}/{len(missing)})…")
                    try:
                        def _on_progress(uploaded, total, _name=e["base_name"], _idx=idx):
                            pct_msg = f"Uploading '{_name}' ({_idx}/{len(missing)})…"
                            progress_dialog.status_label.setText(pct_msg)
                            QtWidgets.QApplication.processEvents()

                        file_id = export_and_upload(
                            e, cfg, project_id, root_folder_id, export_dir, preset_path,
                            folder_cache, progress_callback=_on_progress,
                        )
                        asset_ids.append(file_id)
                        names_for_share.append(e["base_name"])
                        log(f"Exported and uploaded '{e['base_name']}' -> file_id {file_id}")
                    except Exception as ex:
                        had_errors = True
                        log_error(f"Export/upload failed for '{e['base_name']}': {ex}", exc_info=True)
            finally:
                if had_errors:
                    progress_dialog.finish("WARNING: Completed with some errors")
                else:
                    progress_dialog.finish("Export & upload complete")

        if not asset_ids:
            show_message("No assets could be found or uploaded for a share link.")
            return

        log(f"Items in share: {', '.join(names_for_share)}")
        log(
            f"Creating FrameIO share link '{share_name}' with {len(asset_ids)} asset(s)"
            f"{' (password protected)' if password else ''}…"
        )
        share = create_share_link(
            cfg,
            project_id,
            asset_ids,
            name=share_name,
            access="public",
            downloading_enabled=True,
            expiration=None,
            passphrase=password or None,
        )

        url = share.get("short_url")
        if not url:
            raise RuntimeError("FrameIO did not return a share URL.")

        try:
            QtWidgets.QApplication.clipboard().setText(url)
        except Exception as e:
            log(f"WARNING: Could not copy URL to clipboard: {e}")

        log(f"Share link created: {url}")
        if password:
            log(f"Password: {password}")

        results = FrameIOShareResultsDialog(
            share_url=url,
            password=password,
            share_name=share_name,
        )
        results.exec()

    except Exception as e:
        log(f"WARNING: Fatal error: {e}\n{traceback.format_exc()}")
        show_message(f"FrameIO Create Share Error: {e}")

    print(f"[{SCRIPT_NAME}] Done.")

# ----------------------------------------------------------
# Scope
# ----------------------------------------------------------

def scope_clip_or_segment(selection):
    return any(isinstance(item, (flame.PyClip, flame.PySegment)) for item in selection)

# ----------------------------------------------------------
# Flame Menus
# ----------------------------------------------------------

def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "UC FrameIO",
            "actions": [
                {
                    "name": "Create Share Link",
                    "order": 7,
                    "isVisible": scope_clip_or_segment,
                    "separator": "above",
                    "execute": create_share,
                    "minimumVersion": "2024.2",
                }
            ],
        }
    ]

def get_timeline_custom_ui_actions():
    return [
        {
            "name": "UC FrameIO",
            "actions": [
                {
                    "name": "Create Share Link",
                    "order": 1,
                    "isVisible": scope_clip_or_segment,
                    "separator": "below",
                    "execute": create_share,
                    "minimumVersion": "2023.2",
                }
            ],
        }
    ]
