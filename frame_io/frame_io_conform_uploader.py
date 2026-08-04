#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO Conform Uploader v1.4.0 — Uppercut VFX Pipeline
- export selection into FROM_FLAME/date/time
- write files to /Volumes/.../FROM_FLAME/date  (no double time)
- upload to FrameIO
- auto-version-up in Flame before export
v1.3.1 - collapse FROM_FLAME shared library and all child folders before release_exclusive_access
v1.3.2 - fix double CONFORMS folder: capture folder id on new-project creation so the
         subsequent find-or-create step is skipped (Frame.io search index is eventually
         consistent and previously returned no results for the just-created folder)
v1.4.0 - migrate to Frame.io V4 API: replace frameioclient SDK upload with the
         local_upload + presigned-S3-PUT flow, and version_asset/resolve_stack_root_id
         with add_version()
"""

import os
import flame
import datetime
import re
import traceback
from PySide6 import QtWidgets, QtCore
from pathlib import Path
from lib.frame_io_api import (
    validate_config,
    get_fio_projects,
    create_fio_project,
    find_fio_asset,
    find_fio_folder,
    create_fio_folder,
    add_version,
    upload_file,
)


SCRIPT_NAME = "FrameIO Conform Uploader"
VERSION = "v1.4.0"

# ----------------------------------------------------------
# Toast
# ----------------------------------------------------------
def show_toast(message, duration=5, title=SCRIPT_NAME):
    try:
        if hasattr(flame, "display_toast"):
            flame.display_toast(message, duration)
            return
    except Exception:
        pass

    print(f"[{title}] {message}")
    msg_box = QtWidgets.QMessageBox()
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QtWidgets.QMessageBox.Information)
    QtCore.QTimer.singleShot(duration * 1000, msg_box.accept)
    msg_box.exec_()

# ----------------------------------------------------------
# Logging
# ----------------------------------------------------------
def log(msg):
    print(f"[{SCRIPT_NAME}] {msg}")

def attr(x):
    try:
        return x.get_value() if hasattr(x, "get_value") else x
    except Exception:
        return x

# ----------------------------------------------------------
# Progress UI
# ----------------------------------------------------------
class FrameIOProgressDialog(QtWidgets.QDialog):
    def __init__(self, total_files, title="FrameIO Upload Progress"):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.resize(420, 150)

        layout = QtWidgets.QVBoxLayout(self)
        self.status_label = QtWidgets.QLabel("Preparing uploads…")
        self.file_progress = QtWidgets.QProgressBar()
        self.file_progress.setRange(0, 100)
        self.total_progress = QtWidgets.QProgressBar()
        self.total_progress.setRange(0, max(1, total_files))

        layout.addWidget(self.status_label)
        layout.addWidget(QtWidgets.QLabel("Current File"))
        layout.addWidget(self.file_progress)
        layout.addWidget(QtWidgets.QLabel("Overall"))
        layout.addWidget(self.total_progress)

    def update_total_file(self, idx, total, filename):
        self.total_progress.setMaximum(max(1, total))
        self.total_progress.setValue(max(0, idx - 1))
        self.file_progress.setValue(0)
        self.status_label.setText(f"Uploading {os.path.basename(filename)} ({idx}/{total})…")
        QtWidgets.QApplication.processEvents()

    def update_file_percent(self, percent, message=None):
        clamped = max(0, min(100, int(percent)))
        self.file_progress.setValue(clamped)
        if message:
            self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()

    def finish(self, message="Upload complete", delay_ms=1500):
        self.total_progress.setValue(self.total_progress.maximum())
        self.file_progress.setValue(100)
        self.status_label.setText(message)
        QtWidgets.QApplication.processEvents()
        QtCore.QTimer.singleShot(delay_ms, self.accept)

# ----------------------------------------------------------
# Shared Library Helpers
# ----------------------------------------------------------
def get_or_create_shared_library(name="FROM_FLAME"):
    project = flame.projects.current_project
    for lib in project.shared_libraries:
        if attr(lib.name).strip().lower() == name.lower():
            return lib
    new_lib = project.create_shared_library(name)
    if not new_lib:
        raise RuntimeError(f"Failed to create Shared Library '{name}'.")
    return new_lib

def ensure_folder(parent, name):
    for f in parent.folders:
        if attr(f.name) == name:
            return f
    if hasattr(parent, "create_folder"):
        return parent.create_folder(name)
    raise RuntimeError("Flame version does not expose create_folder().")

def collapse_recursive(node):
    """Collapse *node* and every descendant folder in the media panel."""
    try:
        for child in getattr(node, "folders", []):
            collapse_recursive(child)
        if hasattr(node, "expanded"):
            node.expanded = False
    except Exception as e:
        log(f"WARNING: Could not collapse node '{getattr(node, 'name', node)}': {e}")

# ----------------------------------------------------------
# Auto version-up (exact name search style)
# ----------------------------------------------------------
def auto_version_up_flame(selection, cfg, project_id):
    """Auto-version up clips if a matching base asset exists in FrameIO.

    Logic:
    - Parse v## from the clip name.
    - Derive a base name by stripping the version.
    - Look up the base name in FrameIO.
    - Only rename in Flame when a matching asset exists.
    """
    try:
        for item in selection:
            # Flame PyObject names sometimes come in as quoted strings, eg "'NAME'"
            try:
                raw_name = str(item.name)[1:-1]
            except Exception:
                raw_name = str(item.name)

            clip_name = raw_name.strip()
            log(f"[auto_version_up_flame] Checking '{clip_name}'")

            # Find version token in the name — use the LAST match so names
            # with an earlier incidental "v##"-looking substring (e.g. a shot
            # or product code) don't get mistaken for the version token.
            matches = list(re.finditer(r"([vV])(\d+)", clip_name))
            if not matches:
                log(f"WARNING: {clip_name} needs a version number like 'v01'.")
                continue
            m = matches[-1]

            # Derive a base name by stripping the version portion
            base_name = clip_name[:m.start()].rstrip(" _-")
            version_prefix = m.group(1)
            current_version = int(m.group(2))
            padding = len(m.group(2))

            # If we somehow ended up with an empty base_name, fall back to full clip_name
            search_name = base_name or clip_name

            # Use the same search strategy that the uploader uses (base name search)
            asset_type, asset_id, parent_id, file_id = find_fio_asset(cfg, project_id, search_name)

            if asset_type is None:
                # Per-item message instead of a for-else that fires once at the end
                log(
                    f"** No existing version found in FrameIO for "
                    f"'{search_name}' — keeping '{clip_name}'."
                )
                continue

            # Bump the version number in the string (preserving zero-padding),
            # replacing only the last version token found above.
            new_version = current_version + 1
            new_name = (
                clip_name[:m.start()]
                + f"{version_prefix}{new_version:0{padding}d}"
                + clip_name[m.end():]
            )

            try:
                if hasattr(item, "name") and hasattr(item.name, "set_value"):
                    item.name.set_value(new_name)
                else:
                    item.name = new_name
                log(f"Renamed {clip_name} → {new_name}")
            except Exception as e:
                log(f"WARNING: Could not rename {clip_name}: {e}")

    except Exception as e:
        log(f"WARNING: Version check skipped: {e}")

# ----------------------------------------------------------
# Export and collect
# ----------------------------------------------------------
def export_and_collect(selection, project_token, jobs_folder, cfg):
    lib = get_or_create_shared_library("FROM_FLAME")
    lib.acquire_exclusive_access()
    try:
        date_name = datetime.datetime.now().strftime("%Y-%m-%d")
        time_name = datetime.datetime.now().strftime("%H%M")

        date_folder = ensure_folder(lib, date_name)
        time_folder = ensure_folder(date_folder, time_name)

        # Get project_id for version checking
        try:
            _, project_id = get_fio_projects(cfg, project_token)
            auto_version_up_flame(selection, cfg, project_id)
        except Exception:
            log("WARNING: Could not check for existing versions (project may not exist yet)")

        log("Copying selection into Shared Library folder…")
        if flame.get_current_tab() == "MediaHub":
            flame.set_current_tab("Timeline")
        for item in selection:
            try:
                flame.media_panel.copy(item, time_folder)
            except Exception as e:
                log(f"WARNING: Failed to copy {getattr(item, 'name', 'item')}: {e}")
        log("Selection copied.")

        posting_folder = os.path.join(
            jobs_folder,
            project_token,
            "FROM_FLAME",
            date_name,
        )
        os.makedirs(posting_folder, exist_ok=True)
        log(f"Posting folder: {posting_folder}")

        preset_path = cfg.get("preset_path_h264")
        if not preset_path or not os.path.exists(preset_path):
            raise RuntimeError(f"Missing preset: {preset_path}")

        exporter = flame.PyExporter()
        exporter.foreground = True
        exporter.export_between_marks = True
        exporter.use_top_video_track = True
        exporter.export(time_folder, preset_path, posting_folder)
        log("Export complete.")

        return os.path.join(posting_folder, time_name)
    finally:
        collapse_recursive(lib)
        lib.release_exclusive_access()

# ----------------------------------------------------------
# Main upload
# ----------------------------------------------------------
def start_upload(selection):
    print(f"\n[{SCRIPT_NAME}] {VERSION} — Start")
    try:
        cfg = validate_config()
        project = flame.projects.current_project
        project_token = str(attr(project.nickname))
        jobs_folder = cfg.get("jobs_folder", "/Volumes/vfx/UC_Jobs")

        reply = QtWidgets.QMessageBox.question(
            None,
            "Confirm Upload",
            f"Upload conform for project '{project_token}' to FrameIO?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
        )
        if reply != QtWidgets.QMessageBox.Yes:
            log("WARNING:  Upload canceled.")
            return

        posting_folder = export_and_collect(selection, project_token, jobs_folder, cfg)

        files = [
            os.path.join(root, f)
            for root, _, fnames in os.walk(posting_folder)
            for f in fnames
        ]
        if not files:
            raise RuntimeError("No files exported for upload.")
        
        progress_dialog = FrameIOProgressDialog(len(files), "FrameIO Conform Upload")
        progress_dialog.show()
        had_errors = False

        # Get or create FrameIO project
        conforms_folder_id = None
        try:
            root_asset_id, project_id = get_fio_projects(cfg, project_token)
        except Exception:
            root_asset_id, project_id = create_fio_project(cfg, project_token)
            # Create default folders and capture the CONFORMS id so we don't
            # search for it below — the Frame.io search index is eventually
            # consistent and may not reflect the folder immediately, which
            # previously caused a second CONFORMS folder to be created.
            create_fio_folder(cfg, root_asset_id, "SHOTS")
            conforms_folder_id = create_fio_folder(cfg, root_asset_id, "CONFORMS")

        # Find or create CONFORMS folder (skipped when we just created it above)
        if conforms_folder_id is None:
            search = find_fio_folder(cfg, project_id, "CONFORMS")
            if search != (None, None, None, None):
                _, conforms_folder_id, _, _ = search
            else:
                conforms_folder_id = create_fio_folder(cfg, root_asset_id, "CONFORMS")

        log(f"files: {files}")
        completed = False
        try:
            for idx, filename in enumerate(files, 1):
                print("\n")
                path, file_name = os.path.split(filename)
                log(f"file_path: {path}")
                log(f"file name: {file_name}")

                # Check for v## or V##
                pattern = r"_[vV]\d+"
                matches = list(re.finditer(pattern, file_name))

                # If there are matches, split at the last match
                if matches:
                    split_index = matches[-1].start()
                    base_name = file_name[:split_index]
                else:
                    base_name = file_name
                log(f"base_name: {base_name}")

                progress_dialog.update_total_file(idx, len(files), file_name)
                progress_dialog.update_file_percent(
                    5, f"Preparing upload for {file_name} ({idx}/{len(files)})…"
                )

                def _on_progress(uploaded, total, _idx=idx, _len=len(files), _name=file_name):
                    pct = 5 + int((uploaded / total) * 90) if total else 5
                    progress_dialog.update_file_percent(
                        pct, f"Uploading {_name} ({_idx}/{_len})…"
                    )

                # find an asset using project and base name
                search = find_fio_asset(cfg, project_id, base_name)
                if search != (None, None, None, None):
                    asset_type, asset_id, parent_id, existing_file_id = search
                    if asset_type in ("file", "version_stack"):
                        log(f"Search results for matching base name asset ID: {asset_id} ({asset_type})")
                        try:
                            # Upload into the parent folder, then stack/move it
                            # alongside the existing file/version_stack.
                            new_file_id = upload_file(cfg, parent_id, filename, progress_callback=_on_progress)
                            try:
                                add_version(cfg, asset_type, asset_id, new_file_id, parent_id)
                                log(f"Successfully versioned {file_name} with existing asset")
                            except Exception as version_error:
                                # Versioning failed, but upload succeeded
                                # Don't upload again - just log the warning
                                had_errors = True
                                log(f"WARNING: Upload succeeded but versioning failed: {version_error}")
                                log(f"   File uploaded to parent folder but not stacked with existing asset")
                        except Exception as e:
                            # Upload itself failed - try CONFORMS folder as fallback
                            had_errors = True
                            log(f"WARNING: Upload to parent folder failed: {e}")
                            log(f"   Attempting fallback upload to CONFORMS folder...")
                            try:
                                upload_file(cfg, conforms_folder_id, filename, progress_callback=_on_progress)
                                log(f"Fallback upload to CONFORMS succeeded")
                            except Exception as inner:
                                log(f"WARNING:  Fallback upload also failed: {inner}")
                                progress_dialog.update_file_percent(
                                    0, f"WARNING: Failed to upload {file_name}. Continuing…"
                                )
                                continue
                    else:
                        log("Can't find a match...uploading to the CONFORMS folder.")
                        try:
                            upload_file(cfg, conforms_folder_id, filename, progress_callback=_on_progress)
                        except Exception as e:
                            had_errors = True
                            log(f"Upload failed: {e}")
                            progress_dialog.update_file_percent(
                                0, f"WARNING: Failed to upload {file_name}. Continuing…"
                            )
                            continue
                else:
                    log("Can't find a match...uploading to the CONFORMS folder.")
                    try:
                        upload_file(cfg, conforms_folder_id, filename, progress_callback=_on_progress)
                    except Exception as e:
                        had_errors = True
                        log(f"Upload failed: {e}")
                        progress_dialog.update_file_percent(
                            0, f"WARNING: Failed to upload {file_name}. Continuing…"
                        )
                        continue

                progress_dialog.update_file_percent(
                    100, f"Uploaded {file_name} ({idx}/{len(files)})"
                )

            completed = True
        finally:
            if completed and not had_errors:
                progress_dialog.finish("FrameIO conform upload complete")
            elif completed:
                progress_dialog.finish("WARNING: Upload complete with warnings")
            else:
                progress_dialog.finish("WARNING: Upload interrupted")

        if had_errors:
            show_toast("WARNING: FrameIO Conform upload finished with warnings", 5)
            log("WARNING: Upload finished with warnings.")
        else:
            show_toast("FrameIO Conform upload complete", 5)
            log("All uploads complete.")

    except Exception as e:
        log(f"WARNING:  Fatal error: {e}\n{traceback.format_exc()}")
        show_toast(f"FrameIO Conform Uploader Error: {e}", 5)

    print(f"[{SCRIPT_NAME}] Done.")

# ----------------------------------------------------------
# Menu
# ----------------------------------------------------------
def scope_sequence(selection):
    return all(isinstance(item, flame.PySequence) for item in selection)

def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "UC FrameIO",
            "order": 3,
            "actions": [
                {
                    "name": "Conform Uploader",
                    "order": 0,
                    "separator": "below",
                    "isVisible": scope_sequence,
                    "execute": start_upload,
                    "minimumVersion": "2024.2"
                }
            ]
        }
    ]
