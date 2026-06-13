#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flame launch hook: installs required Python packages for MASV Uploader.

Installs `requests` into Flame's site-packages on first launch if missing.
"""

import getpass
import importlib.util
import os
import shutil
import subprocess
import sys
from typing import List, Optional, Tuple

try:
    from PySide6 import QtCore, QtWidgets
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


REQUIRED_PACKAGES: List[Tuple[str, str]] = [
    ("requests", "requests"),
]


def _is_module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _get_missing_packages() -> List[Tuple[str, str]]:
    return [
        (imp, pip) for imp, pip in REQUIRED_PACKAGES
        if not _is_module_available(imp)
    ]


def _ensure_pip_available() -> None:
    if not _is_module_available("pip"):
        raise RuntimeError("pip is not available for this Python interpreter.")


def _get_sudo_password_gui(packages: List[Tuple[str, str]]) -> Optional[str]:
    if not GUI_AVAILABLE:
        try:
            return getpass.getpass(
                "Administrator password required to install packages (sudo): "
            )
        except (KeyboardInterrupt, EOFError):
            return None

    try:
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("MASV Uploader — Package Installer")
        dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        dialog.resize(480, 200)

        layout = QtWidgets.QVBoxLayout(dialog)
        info_text = "<p>The following packages need to be installed:</p><ul>"
        for _, pip_name in packages:
            info_text += f"<li><b>{pip_name}</b></li>"
        info_text += "</ul><p>Administrator privileges are required.</p>"

        info_label = QtWidgets.QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(info_label)

        password_layout = QtWidgets.QHBoxLayout()
        password_layout.addWidget(QtWidgets.QLabel("Password:"))
        password_input = QtWidgets.QLineEdit()
        password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        password_input.returnPressed.connect(dialog.accept)
        password_layout.addWidget(password_input)
        layout.addLayout(password_layout)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        ok_btn = QtWidgets.QPushButton("OK")
        ok_btn.setDefault(True)
        ok_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(ok_btn)
        layout.addLayout(button_layout)

        password_input.setFocus()
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            return password_input.text() or None
        return None

    except Exception as e:
        print(f"[masv_uploader] GUI password dialog failed: {e}")
        try:
            return getpass.getpass(
                "Administrator password required to install packages (sudo): "
            )
        except (KeyboardInterrupt, EOFError):
            return None


def _run_with_sudo(password: str, args: List[str]) -> int:
    sudo_path = shutil.which("sudo")
    if not sudo_path:
        raise RuntimeError("sudo not found on PATH.")

    validate = subprocess.run(
        [sudo_path, "-k", "-S", "-v"],
        input=f"{password}\n".encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if validate.returncode != 0:
        sys.stdout.write(validate.stdout.decode(errors="ignore"))
        raise PermissionError("Invalid sudo password or unable to acquire sudo credentials.")

    proc = subprocess.run(
        [sudo_path, "-S", "-H", *args],
        input=f"{password}\n".encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    sys.stdout.write(proc.stdout.decode(errors="ignore"))
    return proc.returncode


def _install_missing_with_sudo(missing: List[Tuple[str, str]]) -> None:
    _ensure_pip_available()

    flame_version = None
    flame_site_packages = None
    pip_executable = None

    try:
        import flame  # type: ignore
        flame_version = getattr(flame, "get_version")()
    except Exception:
        flame_version = None

    if flame_version:
        candidate_pip = f"/opt/Autodesk/python/{flame_version}/bin/pip3"
        if os.path.exists(candidate_pip):
            pip_executable = candidate_pip
        for minor in (11, 10, 9, 8):
            candidate_site = (
                f"/opt/Autodesk/python/{flame_version}/lib/python3.{minor}/site-packages"
            )
            if os.path.isdir(candidate_site):
                flame_site_packages = candidate_site
                break

    if not pip_executable:
        pip_prefix = [sys.executable, "-m", "pip"]
    else:
        pip_prefix = [pip_executable]

    if not flame_site_packages:
        try:
            import site as _site
            site_paths = list(getattr(_site, "getsitepackages")())
            flame_site_packages = site_paths[0] if site_paths else None
        except Exception:
            flame_site_packages = None

    pip_args = [*pip_prefix, "install", "--upgrade", "--disable-pip-version-check"]
    if flame_site_packages:
        os.makedirs(flame_site_packages, exist_ok=True)
        pip_args += ["--target", flame_site_packages]

    pip_packages = []
    seen = set()
    for _import, pip_name in missing:
        if pip_name not in seen:
            pip_packages.append(pip_name)
            seen.add(pip_name)

    if not pip_packages:
        return

    print("[masv_uploader] Installing required packages…")
    password = _get_sudo_password_gui(missing)
    if password is None:
        raise RuntimeError("Password entry cancelled. Package installation aborted.")

    code = _run_with_sudo(password, pip_args + pip_packages)
    if code != 0:
        raise RuntimeError("pip installation failed. See output above for details.")


def install_python_packages(_selection=None):
    try:
        missing = _get_missing_packages()
        if not missing:
            return
        _install_missing_with_sudo(missing)
        if _get_missing_packages():
            raise RuntimeError("Some packages failed to install or import.")
        print("[masv_uploader] All required packages are installed.")
    except Exception as e:
        print(f"[masv_uploader] {e}")


def app_initialized(install_packages):
    install_python_packages(install_packages)
