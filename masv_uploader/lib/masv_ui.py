#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PySide6 UI components for MASV Uploader for Flame.
"""

import os
import secrets

from PySide6 import QtCore, QtWidgets

from lib.masv_api import PRESETS_DIR, get_preset_path, list_presets


class MASVOptionsDialog(QtWidgets.QDialog):
    """Collect upload options before export begins."""

    def __init__(
        self,
        default_name: str = "",
        last_preset: str = "",
        default_recipients: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("MASV Upload Options")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(500, 0)

        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        self.preset_combo = QtWidgets.QComboBox()
        presets = list_presets()
        if presets:
            for name in presets:
                self.preset_combo.addItem(os.path.splitext(name)[0], userData=name)
            if last_preset and last_preset in presets:
                self.preset_combo.setCurrentIndex(presets.index(last_preset))
        else:
            self.preset_combo.addItem(
                f"No presets found in {PRESETS_DIR}", userData=None
            )
        form.addRow("Export Preset:", self.preset_combo)

        self.name_edit = QtWidgets.QLineEdit(default_name)
        form.addRow("Package Name:", self.name_edit)

        self.desc_edit = QtWidgets.QLineEdit()
        self.desc_edit.setPlaceholderText("Optional")
        form.addRow("Description:", self.desc_edit)

        pw_row = QtWidgets.QHBoxLayout()
        self.pw_enabled = QtWidgets.QCheckBox("Enable")
        self.pw_enabled.setChecked(True)
        self.pw_edit = QtWidgets.QLineEdit()
        self.pw_edit.setPlaceholderText("Password")
        gen_btn = QtWidgets.QPushButton("Generate")
        gen_btn.setFixedWidth(80)
        gen_btn.clicked.connect(self._generate_password)
        pw_row.addWidget(self.pw_enabled)
        pw_row.addWidget(self.pw_edit)
        pw_row.addWidget(gen_btn)
        form.addRow("Password:", pw_row)
        self.pw_enabled.toggled.connect(self.pw_edit.setEnabled)
        self.pw_enabled.toggled.connect(gen_btn.setEnabled)
        self._generate_password()

        self.recipients_edit = QtWidgets.QLineEdit()
        self.recipients_edit.setPlaceholderText("email@example.com  (optional, comma-separated)")
        if default_recipients:
            self.recipients_edit.setText(default_recipients)
        form.addRow("Recipients:", self.recipients_edit)

        limit_row = QtWidgets.QHBoxLayout()
        self.limit_unlimited = QtWidgets.QCheckBox("Unlimited")
        self.limit_spin = QtWidgets.QSpinBox()
        self.limit_spin.setRange(1, 9999)
        self.limit_spin.setValue(10)
        self.limit_spin.setFixedWidth(70)
        limit_row.addWidget(self.limit_unlimited)
        limit_row.addWidget(self.limit_spin)
        limit_row.addStretch()
        form.addRow("Download Limit:", limit_row)
        self.limit_unlimited.toggled.connect(lambda checked: self.limit_spin.setDisabled(checked))

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        ok_btn = QtWidgets.QPushButton("Upload")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(self._on_accept)
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)

        self.adjustSize()

    def _generate_password(self) -> None:
        self.pw_edit.setText(secrets.token_urlsafe(12))

    def _on_accept(self) -> None:
        if not self.name_edit.text().strip():
            QtWidgets.QMessageBox.warning(self, "Validation", "Package name cannot be empty.")
            return
        if not self.selected_preset():
            QtWidgets.QMessageBox.warning(
                self,
                "Validation",
                f"No export preset selected.\n\nAdd .xml presets to:\n{PRESETS_DIR}",
            )
            return
        self.accept()

    def package_name(self) -> str:
        return self.name_edit.text().strip()

    def description(self) -> str:
        return self.desc_edit.text().strip()

    def password(self) -> str:
        if self.pw_enabled.isChecked():
            return self.pw_edit.text().strip()
        return ""

    def recipients(self) -> list:
        raw = self.recipients_edit.text().strip()
        if not raw:
            return []
        return [r.strip() for r in raw.split(",") if r.strip()]

    def access_limit(self):
        if self.limit_unlimited.isChecked():
            return None
        return self.limit_spin.value()

    def selected_preset(self) -> str:
        return self.preset_combo.currentData() or ""

    def selected_preset_path(self) -> str:
        filename = self.selected_preset()
        return get_preset_path(filename) if filename else ""


class MASVProgressDialog(QtWidgets.QDialog):
    def __init__(self, total_files: int, title: str = "MASV Upload Progress"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(440, 160)

        layout = QtWidgets.QVBoxLayout(self)
        self.status_label = QtWidgets.QLabel("Preparing upload…")
        self.file_progress = QtWidgets.QProgressBar()
        self.file_progress.setRange(0, 100)
        self.total_progress = QtWidgets.QProgressBar()
        self.total_progress.setRange(0, max(1, total_files))

        layout.addWidget(self.status_label)
        layout.addWidget(QtWidgets.QLabel("Current File:"))
        layout.addWidget(self.file_progress)
        layout.addWidget(QtWidgets.QLabel("Overall:"))
        layout.addWidget(self.total_progress)

    def update_total_file(self, idx: int, total: int, filename: str) -> None:
        self.total_progress.setMaximum(max(1, total))
        self.total_progress.setValue(max(0, idx - 1))
        self.file_progress.setValue(0)
        self.status_label.setText(
            f"Uploading {os.path.basename(filename)} ({idx}/{total})…"
        )
        QtWidgets.QApplication.processEvents()

    def update_file_percent(self, percent: float, message: str = "") -> None:
        self.file_progress.setValue(max(0, min(100, int(percent))))
        if message:
            self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()

    def finish(self, message: str = "Upload complete", delay_ms: int = 1500) -> None:
        self.total_progress.setValue(self.total_progress.maximum())
        self.file_progress.setValue(100)
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(delay_ms, self.accept)


class MASVResultsDialog(QtWidgets.QDialog):
    def __init__(
        self,
        download_url: str,
        password: str = "",
        package_name: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("MASV Upload Complete")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(560, 0)

        layout = QtWidgets.QVBoxLayout(self)

        if package_name:
            title = QtWidgets.QLabel(f"<b>{package_name}</b> has been uploaded successfully.")
            title.setTextFormat(QtCore.Qt.RichText)
            layout.addWidget(title)
            layout.addSpacing(8)

        form = QtWidgets.QFormLayout()
        layout.addLayout(form)

        url_row = QtWidgets.QHBoxLayout()
        self.url_edit = QtWidgets.QLineEdit(download_url)
        self.url_edit.setReadOnly(True)
        copy_url_btn = QtWidgets.QPushButton("Copy")
        copy_url_btn.setFixedWidth(60)
        copy_url_btn.clicked.connect(lambda: self._copy(self.url_edit.text(), copy_url_btn))
        url_row.addWidget(self.url_edit)
        url_row.addWidget(copy_url_btn)
        form.addRow("Download URL:", url_row)

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

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch()
        copy_all_btn = QtWidgets.QPushButton("Copy Both to Clipboard")
        copy_all_btn.clicked.connect(
            lambda: self._copy_both(download_url, password, copy_all_btn)
        )
        close_btn = QtWidgets.QPushButton("Close")
        close_btn.setDefault(True)
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(copy_all_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        self.adjustSize()

    @staticmethod
    def _copy(text: str, button: QtWidgets.QPushButton) -> None:
        QtWidgets.QApplication.clipboard().setText(text)
        original = button.text()
        button.setText("Copied!")
        QtCore.QTimer.singleShot(1500, lambda: button.setText(original))

    @staticmethod
    def _copy_both(url: str, password: str, button: QtWidgets.QPushButton) -> None:
        parts = [f"Download: {url}"]
        if password:
            parts.append(f"Password: {password}")
        QtWidgets.QApplication.clipboard().setText("\n".join(parts))
        original = button.text()
        button.setText("Copied!")
        QtCore.QTimer.singleShot(1500, lambda: button.setText(original))
