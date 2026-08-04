#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO Set Status v0.2 — Uppercut VFX Pipeline
Sets the status of any items in FrameIO based on the color label(s) of the Flame selection.
"""


import flame
import traceback
from pathlib import Path
from lib.frame_io_api import (
    validate_config,
    get_fio_projects,
    find_fio_asset,
    set_asset_status,
)


SCRIPT_NAME = "FrameIO Set Status"
VERSION = "v0.2"

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

# ----------------------------------------------------------
# Main
# ----------------------------------------------------------

def frame_io_set_status(selection):
    print(f"\n[{SCRIPT_NAME}] {VERSION} — Start")
    try:
        if not selection:
            show_message("Please select one or more clips first.")
            return

        cfg = validate_config()
        project_nickname = str(flame.projects.current_project.nickname)
        
        log(f"Starting FrameIO Status Update for project '{project_nickname}'")
        
        try:
            root_asset_id, project_id = get_fio_projects(cfg, project_nickname)
        except Exception as e:
            message = f"Can't find {project_nickname} FrameIO Project."
            show_message(message, "Error")
            log(message)
            return

        print("\n")

        for item in selection:
            selection_name = str(item.name)[1:-1]
            selection_color_label = item.colour_label
            
            # Map color label to FrameIO status
            if selection_color_label == "Approved":
                new_label = "approved"
            elif selection_color_label == "Needs Review":
                new_label = "needs_review"
            elif selection_color_label == "In Progress":
                new_label = "in_progress"
            else:
                message = f"{selection_name} does not have a Color Label that matches the FrameIO Status options."
                flame.messages.show_in_console(message, "info", 3)
                continue

            # find an asset using project and selection name
            search = find_fio_asset(cfg, project_id, selection_name)
            if search != (None, None, None, None):
                asset_type, asset_id, parent_id, file_id = search
                try:
                    set_asset_status(cfg, project_id, file_id, new_label)
                    log(f"Successfully updated the label of asset {selection_name} to '{new_label}'.")
                except Exception as e:
                    log(f"Failed to update label: {e}")
            else:
                message = f"Can't find {selection_name} in FrameIO."
                flame.messages.show_in_console(message, "info", 6)
                continue

        print("\n")
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
                    "name": "Set Status",
                    "order": 6,
                    "isVisible": scope_clip,
                    "separator": "above",
                    "execute": frame_io_set_status,
                    "minimumVersion": "2025.1"
                }
            ]
        }
    ]
