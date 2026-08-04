#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO Get Status v0.3 — Uppercut VFX Pipeline
Fetches the status of any items in FrameIO and color codes the Flame selection.
"""

import flame
import traceback
from pathlib import Path
from lib.frame_io_api import (
    validate_config,
    get_fio_projects,
    find_fio_asset,
    get_asset_status,
)

SCRIPT_NAME = "FrameIO Get Status"
VERSION = "v0.3"

# ----------------------------------------------------------
# Helpers
# ----------------------------------------------------------

def log(msg):
    print(f"[{SCRIPT_NAME}] {msg}")

def show_message(text, title=SCRIPT_NAME):
    """Cross-version safe popup for Flame."""
    try:
        if hasattr(flame, "message_dialog"):
            flame.message_dialog(title, text)
        else:
            from PySide6 import QtWidgets
            QtWidgets.QMessageBox.information(None, title, text)
    except Exception:
        print(f"[{SCRIPT_NAME}] {text}")

def safe_colour_label(obj, status):
    """Apply color label based on status, with RGB fallback."""
    try:
        if status == "approved":
            obj.colour_label = "Approved"
        elif status == "needs_review":
            obj.colour_label = "Needs Review"
        elif status == "in_progress":
            obj.colour_label = "In Progress"
    except Exception:
        # RGB fallbacks
        if status == "approved":
            obj.colour = (0.11372549086809158, 0.26274511218070984, 0.1764705926179886)
        elif status == "needs_review":
            obj.colour = (0.6000000238418579, 0.3450980484485626, 0.16470588743686676)
        elif status == "in_progress":
            obj.colour = (0.26274511218070984, 0.40784314274787903, 0.5019607543945312)

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def frame_io_get_status(selection):
    print(f"\n[{SCRIPT_NAME}] {VERSION} — Start")
    try:
        if not selection:
            show_message("Please select one or more clips first.")
            return

        cfg = validate_config()
        project_nickname = str(flame.projects.current_project.nickname)
        
        log(f"Starting FrameIO Status Sync for project '{project_nickname}'")
        
        try:
            root_asset_id, project_id = get_fio_projects(cfg, project_nickname)
        except Exception as e:
            message = f"Can't find {project_nickname} FrameIO Project."
            show_message(message, "Error")
            log(message)
            return

        for item in selection:
            selection_name = str(item.name)[1:-1]
            # log(f"DEBUG: Starting lookup for selection: '{selection_name}'")
            # show_message(f"Looking up: {selection_name}", title="FrameIO Get Status (Debug)")

            # --------- Step 1: Lookup asset in FrameIO ----------
            try:
                search = find_fio_asset(cfg, project_id, selection_name)
            except Exception as e:
                log(f"ERROR: find_fio_asset crashed: {e}")
                show_message(f"find_fio_asset ERROR:\n{e}")
                continue

            # log(f"DEBUG: find_fio_asset returned: {search}")

            if search == (None, None, None, None):
                msg = f"NOT FOUND in FrameIO: {selection_name}"
                log(msg)
                show_message(msg)
                flame.messages.show_in_console(msg, "info", 6)
                continue

            asset_type, asset_id, parent_id, file_id = search

            # --------- Step 2: Fetch Status ----------
            try:
                status = get_asset_status(cfg, file_id)
            except Exception as e:
                log(f"ERROR: get_asset_status crashed: {e}")
                show_message(f"get_asset_status ERROR:\n{e}")
                continue

            # log(f"DEBUG: Raw Status from FrameIO for '{selection_name}': {status}")
            # show_message(f"Status for {selection_name}:\n{status}")

            # --------- Step 3: Apply Color ----------
            if status in ("approved", "needs_review", "in_progress"):
                try:
                    safe_colour_label(item, status)
                    log(f"Applied color label for {selection_name}: {status}")
                except Exception as e:
                    log(f"ERROR: applying color: {e}")
            else:
                msg = f"{selection_name}: No mappable status ({status})"
                flame.messages.show_in_console(msg, "info", 3)
                log(msg)


        log(f"[{SCRIPT_NAME}] Done.")

    except Exception as e:
        log(f"WARNING:  Failed: {e}\n{traceback.format_exc()}")
        show_message(f"Error: {e}")

# ----------------------------------------------------------
# Scope
# ----------------------------------------------------------

def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

# ----------------------------------------------------------
# Flame Menus
# ----------------------------------------------------------

def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "UC FrameIO",
            "actions": [
                {
                    "name": "Get Status",
                    "order": 5,
                    "isVisible": scope_clip,
                    "separator": "above",
                    "execute": frame_io_get_status,
                    "minimumVersion": "2025.1"
                }
            ]
        }
    ]
