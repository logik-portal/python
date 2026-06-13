"""
Script Name: MASV Uploader
Script Version: 1.0.0
Flame Version: 2025
Written by: Cursor with guidance from John Geehreng
Creation Date: 06.13.26
Update Date: 

Custom Action Type: Media Panel

Description:

    MASV Uploader : Export sequences or clips, upload to MASV, and create a password-protected
    download link with a copyable results dialog.

Menu:
    Media Panel → MASV Uploader → Upload Sequence / Upload Clip
    Main Menu   → MASV Uploader → Edit Config

To install:

    Copy script into /opt/Autodesk/shared/python/masv_uploader or whereever you keep you scripts

Updates:
    v1.0 06.13.26
        Initial version
"""

import datetime
import os
import traceback

import flame
from PySide6 import QtCore, QtWidgets

from lib.masv_api import (
    MENU_NAME,
    PRESETS_DIR,
    build_download_url,
    create_link,
    create_package,
    finalize_package,
    format_recipients_for_edit,
    save_last_preset,
    upload_file,
    validate_config,
)
from lib.masv_ui import MASVOptionsDialog, MASVProgressDialog, MASVResultsDialog

SCRIPT_NAME = MENU_NAME
VERSION = "v1.0.0"
SHARED_LIBRARY_NAME = "MASV_EXPORT"


def log(msg: str) -> None:
    print(f"[{SCRIPT_NAME}] {msg}")


def show_toast(message: str, duration: int = 5) -> None:
    try:
        if hasattr(flame, "display_toast"):
            flame.display_toast(message, duration)
            return
    except Exception:
        pass
    print(f"[{SCRIPT_NAME}] {message}")
    box = QtWidgets.QMessageBox()
    box.setWindowTitle(SCRIPT_NAME)
    box.setText(message)
    box.setIcon(QtWidgets.QMessageBox.Information)
    QtCore.QTimer.singleShot(duration * 1000, box.accept)
    box.exec()


def _attr(x):
    try:
        return x.get_value() if hasattr(x, "get_value") else x
    except Exception:
        return x


def _get_project_name() -> str:
    project = flame.projects.current_project
    name = str(_attr(getattr(project, "nickname", getattr(project, "name", "Project"))))
    return name.strip()


def _ensure_folder(parent, name: str):
    for f in getattr(parent, "folders", []):
        if _attr(f.name) == name:
            return f
    if hasattr(parent, "create_folder"):
        return parent.create_folder(name)
    raise RuntimeError(f"Cannot create folder '{name}' — Flame API unavailable.")


def _collapse_recursive(node) -> None:
    try:
        for child in getattr(node, "folders", []):
            _collapse_recursive(child)
        if hasattr(node, "expanded"):
            node.expanded = False
    except Exception as e:
        log(f"WARNING: Could not collapse '{getattr(node, 'name', node)}': {e}")


def _get_or_create_shared_library(name: str = SHARED_LIBRARY_NAME):
    project = flame.projects.current_project
    for lib in project.shared_libraries:
        if _attr(lib.name).strip().lower() == name.lower():
            return lib
    lib = project.create_shared_library(name)
    if not lib:
        raise RuntimeError(f"Failed to create Shared Library '{name}'.")
    return lib


def _export_selection(selection, project_name: str, cfg: dict, preset_path: str) -> str:
    jobs_folder = cfg.get("jobs_folder", "").strip()
    if not preset_path or not os.path.exists(preset_path):
        raise RuntimeError(
            f"Export preset not found: '{preset_path}'.\n"
            f"Add preset files to {PRESETS_DIR}"
        )

    date_name = datetime.datetime.now().strftime("%Y-%m-%d")
    time_name = datetime.datetime.now().strftime("%H%M")

    lib = _get_or_create_shared_library()
    lib.acquire_exclusive_access()
    try:
        date_folder = _ensure_folder(lib, date_name)
        time_folder = _ensure_folder(date_folder, time_name)

        log("Copying selection into shared library…")
        if flame.get_current_tab() == "MediaHub":
            flame.set_current_tab("Timeline")
        for item in selection:
            try:
                flame.media_panel.copy(item, time_folder)
            except Exception as e:
                log(f"WARNING: Failed to copy {getattr(item, 'name', 'item')}: {e}")

        output_dir = os.path.join(
            jobs_folder,
            project_name,
            "MASV",
            date_name,
            time_name,
        )
        os.makedirs(output_dir, exist_ok=True)
        log(f"Export destination: {output_dir}")

        exporter = flame.PyExporter()
        exporter.foreground = True
        exporter.export_between_marks = True
        exporter.use_top_video_track = True
        exporter.export(time_folder, preset_path, output_dir)
        log("Export complete.")
    finally:
        _collapse_recursive(lib)
        lib.release_exclusive_access()

    return output_dir


def _run_upload(selection, label: str) -> None:
    print(f"\n[{SCRIPT_NAME}] {VERSION} — {label} start")
    try:
        cfg = validate_config()
        project_name = _get_project_name()

        default_name = f"{project_name} {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
        opts = MASVOptionsDialog(
            default_name=default_name,
            last_preset=cfg.get("last_preset", ""),
            default_recipients=format_recipients_for_edit(cfg.get("default_recipients", "")),
        )
        if opts.exec() != QtWidgets.QDialog.Accepted:
            log("Upload cancelled by user.")
            return

        pkg_name = opts.package_name()
        password = opts.password()
        recipients = opts.recipients()
        access_limit = opts.access_limit()
        preset_filename = opts.selected_preset()
        preset_path = opts.selected_preset_path()

        n = len(selection)
        item_word = "sequence" if n == 1 else "sequences"
        if label == "Clip":
            item_word = "clip" if n == 1 else "clips"

        reply = QtWidgets.QMessageBox.question(
            None,
            "Confirm Upload",
            (
                f"Export and upload {n} {item_word} to MASV?\n\n"
                f"Package:  {pkg_name}\n"
                f"Password: {'Yes' if password else 'No'}"
            ),
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            log("Upload cancelled by user.")
            return

        output_dir = _export_selection(selection, project_name, cfg, preset_path)

        files = sorted(
            os.path.join(root, f)
            for root, _, fnames in os.walk(output_dir)
            for f in fnames
            if not f.startswith(".")
        )
        if not files:
            raise RuntimeError("No files found after export.")

        package_id, token = create_package(
            cfg,
            name=pkg_name,
            description=opts.description() or pkg_name,
            password=password if password else None,
            recipients=recipients if recipients else None,
            access_limit=access_limit,
        )

        progress = MASVProgressDialog(len(files), "MASV Upload")
        progress.show()
        had_errors = False

        try:
            for idx, file_path in enumerate(files, 1):
                fname = os.path.basename(file_path)
                progress.update_total_file(idx, len(files), fname)

                def make_progress_cb(idx=idx, fname=fname):
                    def cb(pct):
                        progress.update_file_percent(
                            pct, f"Uploading {fname} ({idx}/{len(files)})…"
                        )
                    return cb

                try:
                    upload_file(package_id, token, file_path, progress_cb=make_progress_cb())
                    progress.update_file_percent(100, f"Uploaded {fname} ({idx}/{len(files)})")
                except Exception as e:
                    had_errors = True
                    log(f"WARNING: Upload failed for '{fname}': {e}\n{traceback.format_exc()}")
                    progress.update_file_percent(0, f"WARNING: Failed — {fname}")

            progress.status_label.setText("Finalizing package…")
            QtWidgets.QApplication.processEvents()
            finalize_package(package_id, token)

            progress.status_label.setText("Creating download link…")
            QtWidgets.QApplication.processEvents()
            link_id, download_secret = create_link(
                package_id, token, password=password if password else None
            )
            download_url = build_download_url(link_id, download_secret)

            if preset_filename:
                save_last_preset(preset_filename)

            progress.finish(
                "Upload complete with warnings" if had_errors else "Upload complete!",
                delay_ms=800,
            )

        except Exception:
            progress.finish("Upload failed", delay_ms=800)
            raise

        MASVResultsDialog(
            download_url=download_url,
            password=password,
            package_name=pkg_name,
        ).exec()

        if had_errors:
            show_toast(f"MASV upload finished with warnings — {pkg_name}", 5)
        else:
            show_toast(f"MASV upload complete — {pkg_name}", 5)

    except Exception as e:
        log(f"ERROR: {e}\n{traceback.format_exc()}")
        QtWidgets.QMessageBox.critical(None, f"{SCRIPT_NAME} Error", str(e))

    print(f"[{SCRIPT_NAME}] Done.")


def scope_sequence(selection) -> bool:
    return bool(selection) and all(isinstance(item, flame.PySequence) for item in selection)


def scope_clip(selection) -> bool:
    return bool(selection) and all(isinstance(item, flame.PyClip) for item in selection)


def upload_sequences(selection) -> None:
    _run_upload(selection, label="Sequence")


def upload_clips(selection) -> None:
    _run_upload(selection, label="Clip")


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": MENU_NAME,
            # "order": 4,
            "actions": [
                {
                    "name": "Upload Sequence",
                    # "order": 0,
                    "isVisible": scope_sequence,
                    "execute": upload_sequences,
                    "minimumVersion": "2025",
                },
                {
                    "name": "Upload Clip",
                    # "order": 1,
                    "isVisible": scope_clip,
                    "execute": upload_clips,
                    "minimumVersion": "2025",
                },
            ],
        }
    ]
