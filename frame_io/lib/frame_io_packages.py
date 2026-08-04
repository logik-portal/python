#!/usr/bin/env python3
"""
Flame Launch hook: installs required Python packages for FrameIO integration.

Prompts for administrator password via GUI dialog (falls back to terminal if GUI unavailable).
Targets Flame's versioned site-packages.
Installs if missing:
  - requests (import name: requests)
"""

import getpass
import importlib.util
import os
import shutil
import subprocess
import sys
from typing import List, Tuple, Optional

try:
    from PySide6 import QtWidgets, QtCore
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


# Static requirements: (import_name, pip_distribution)
REQUIRED_PACKAGES: List[Tuple[str, str]] = [
    ("requests", "requests"),
]


def _is_module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _get_missing_packages() -> List[Tuple[str, str]]:
    missing: List[Tuple[str, str]] = []
    for import_name, pip_name in REQUIRED_PACKAGES:
        if not _is_module_available(import_name):
            missing.append((import_name, pip_name))
    return missing


def _ensure_pip_available() -> None:
    if _is_module_available("pip"):
        return
    raise RuntimeError("pip is not available for this Python interpreter.")


def _get_sudo_password_gui(packages: List[Tuple[str, str]]) -> Optional[str]:
    """
    Show a GUI dialog to get sudo password from user.
    Returns password string if successful, None if cancelled.
    Falls back to terminal getpass if GUI is not available.
    """
    if not GUI_AVAILABLE:
        # Fallback to terminal input
        try:
            return getpass.getpass("Administrator password required to install system-wide packages (sudo): ")
        except (KeyboardInterrupt, EOFError):
            return None

    try:
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication([])

        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle("FrameIO Package Installer - Administrator Password Required")
        dialog.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        dialog.resize(480, 200)

        layout = QtWidgets.QVBoxLayout(dialog)

        # Info label
        info_text = f"<p>The following packages need to be installed:</p><ul>"
        for _, pip_name in packages:
            info_text += f"<li><b>{pip_name}</b></li>"
        info_text += "</ul><p>Administrator privileges are required to install system-wide packages.</p>"
        
        info_label = QtWidgets.QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setTextFormat(QtCore.Qt.RichText)
        layout.addWidget(info_label)

        # Password field
        password_layout = QtWidgets.QHBoxLayout()
        password_label = QtWidgets.QLabel("Password:")
        password_input = QtWidgets.QLineEdit()
        password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        password_input.setPlaceholderText("Enter administrator password")
        password_input.returnPressed.connect(dialog.accept)
        password_layout.addWidget(password_label)
        password_layout.addWidget(password_input)
        layout.addLayout(password_layout)

        # Buttons
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

        # Focus on password field
        password_input.setFocus()

        # Show dialog
        if dialog.exec() == QtWidgets.QDialog.Accepted:
            password = password_input.text()
            return password if password else None
        return None

    except Exception as e:
        # If GUI fails, fallback to terminal
        print(f"[frame_io_packages] GUI password dialog failed: {e}, falling back to terminal input")
        try:
            return getpass.getpass("Administrator password required to install system-wide packages (sudo): ")
        except (KeyboardInterrupt, EOFError):
            return None


def _run_with_sudo(password: str, args: List[str]) -> int:
    sudo_path = shutil.which("sudo")
    if not sudo_path:
        raise RuntimeError("sudo not found on PATH.")

    # Validate sudo first
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

    # Detect Flame version and site-packages target
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
            candidate_site = f"/opt/Autodesk/python/{flame_version}/lib/python3.{minor}/site-packages"
            if os.path.isdir(candidate_site):
                flame_site_packages = candidate_site
                break

    if not pip_executable:
        pip_executable = sys.executable
        pip_prefix = [pip_executable, "-m", "pip"]
    else:
        pip_prefix = [pip_executable]

    if not flame_site_packages:
        try:
            import site as _site
            site_paths = list(getattr(_site, "getsitepackages")())
            flame_site_packages = site_paths[0] if site_paths else None
        except Exception:
            flame_site_packages = None

    pip_args = [
        *pip_prefix,
        "install",
        "--upgrade",
        "--disable-pip-version-check",
    ]
    if flame_site_packages:
        pip_args += ["--target", flame_site_packages]

    # Deduplicate
    pip_packages: List[str] = []
    seen = set()
    for _import, pip_name in missing:
        if pip_name not in seen:
            pip_packages.append(pip_name)
            seen.add(pip_name)

    if not pip_packages:
        return

    print("[frame_io_packages] Installing required packages…")
    for imp, pipn in missing:
        print(f"  - import '{imp}' via pip '{pipn}'")

    password = _get_sudo_password_gui(missing)
    if password is None:
        raise RuntimeError("Password entry cancelled or failed. Package installation aborted.")

    code = _run_with_sudo(password, pip_args + pip_packages)
    if code != 0:
        raise RuntimeError("pip installation failed. See output above for details.")


def install_python_packages(_selection=None):
    try:
        missing = _get_missing_packages()
        if not missing:
            return
        _install_missing_with_sudo(missing)
        # Re-check
        if _get_missing_packages():
            raise RuntimeError("Some packages failed to install or import.")
        print("[frame_io_packages] All required packages are installed.")
    except Exception as e:
        print(f"[frame_io_packages] {e}")


def app_initialized(install_packages):
    install_python_packages(install_packages)

