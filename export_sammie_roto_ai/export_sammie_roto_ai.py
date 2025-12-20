################################################################################

# Filename: export_SammieRotoAI.py

################################################################################

# DISCLAIMER:
# This file is provided "as is" without warranty of any kind.

################################################################################

"""
Script Name: Export_SammieRotoAI
Script Version: 1.0.0
Flame Version: 2025
Written by: Wilton Matos
Creation Date: 11.12.24
Update Date: 11.12.24

Custom Action Type: Media Panel / Batch

Description:
Export selected clips or batch clip nodes as JPEG sequences and automatically
open them in Sammie Roto 2.0 for AI-powered rotoscoping.

This script works in two contexts:
1. Media Panel: Select clips from your library
2. Batch: Right-click on Clip Nodes in the batch schematic

The script will:
- Export the selected clip(s) as JPEG sequences (100% quality, 8-bit)
- Create organized subdirectories for each clip
- Wait for export completion (foreground export with progress visible)
- Automatically launch Sammie Roto 2.0 with the exported sequence

Menus:
Right-click selected clip(s) in Media Panel -> Export -> Open Sammie 2.0
Right-click Clip Node in Batch -> Export -> Open Sammie 2.0

Requirements:
- JPEG preset must be at: /opt/Autodesk/shared/python/export_SammieRotoAI/EXPORT_JPEG_SAMMIE.xml
- Download flame export preset here.: https://drive.google.com/file/d/1r3qOdS3Ka94ZO4Ssqgc1Iwus2UXdZORo/view?usp=drive_link
- Sammie Roto 2.0 installed and configured (see SAMMIE_CMD path below)
- run_sammie.command must forward arguments: python3 launcher.py "$@"

To install:
1. Copy script to: /opt/Autodesk/shared/python/export_SammieRotoAI.py
2. Copy JPEG preset to: /opt/Autodesk/shared/python/export_SammieRotoAI/EXPORT_JPEG_SAMMIE.xml
3. Adjust paths in CONFIG section below if needed
4. Restart Flame or reload Python hooks

Configuration:
Edit the CONFIG section below to customize:
- SAMMIE_CMD: Path to Sammie Roto 2.0 launcher
- EXPORT_ROOT: Destination folder for JPEG sequences
- PRESET_PATH: Path to JPEG export preset
- FILE_WAIT_TIMEOUT: Maximum time to wait for export completion

Updates:
v1.0.0 11.12.24
- Initial release.
- Support for Media Panel clips and Batch Clip Nodes
- Foreground export with progress visualization
- Automatic Sammie Roto 2.0 integration
- JPEG sequence export with organized folder structure
"""

import os
import re
import time
import subprocess
from pathlib import Path

# ================== CONFIG ==================
# Sammie-Roto 2.0 launcher path (calls with file argument)
SAMMIE_CMD = ["/bin/bash", "/home/wilton.silva/Sammie-Roto-2/run_sammie.command"]

# Folder where JPEG sequences will be saved:
EXPORT_ROOT = "/mnt/cache/Flame_Exports/SammieRoto"

# JPEG preset path (Shared presets location)
PRESET_PATH = "/opt/Autodesk/shared/python/export_SammieRotoAI/EXPORT_JPEG_SAMMIE.xml"

# Timeout waiting for first frame (seconds):
FILE_WAIT_TIMEOUT = 60

# ============================================

def log(msg):
    print(f"[Sammie Export] {msg}")


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', "_", name)


def diagnose_pyclipnode(node):
    # Diagnostic function stub for troubleshooting clip nodes
    pass


def get_clip_from_item(item):
    import flame
    if isinstance(item, (flame.PyClip, flame.PySequence)):
        return item
    if isinstance(item, flame.PyClipNode):
        for attr in ['clip', 'source', 'media', 'sequence', 'input']:
            if hasattr(item, attr):
                val = getattr(item, attr)
                if isinstance(val, (flame.PyClip, flame.PySequence)):
                    return val
        if hasattr(item, 'input_sockets'):
            try:
                for s in item.input_sockets:
                    if hasattr(s, 'source') and isinstance(s.source, (flame.PyClip, flame.PySequence)):
                        return s.source
            except Exception:
                pass
        return item
    return None


def export_clip_to_jpeg_sequence(clip, preset_path, export_folder):
    import flame
    clip_name = sanitize_filename(clip.name.get_value())
    sequence_dir = os.path.join(export_folder, clip_name)
    log(f"Exporting clip: {clip_name}")

    if not os.path.exists(sequence_dir):
        os.makedirs(sequence_dir)
    if not os.path.exists(preset_path):
        log(f"ERROR: Preset not found at: {preset_path}")
        return None

    exporter = flame.PyExporter()
    exporter.foreground = True
    log("Export mode: FOREGROUND")

    if not hasattr(clip, 'name'):
        log("ERROR: Object missing 'name' attribute")
        return None

    try:
        exporter.export(clip, preset_path, sequence_dir)
        log("Export command sent to Flame")
        return sequence_dir
    except Exception as e:
        log(f"Error during export: {e}")
        return None


def wait_for_sequence(sequence_dir, timeout=FILE_WAIT_TIMEOUT):
    log(f"Waiting for JPEG frames in: {sequence_dir}")
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(sequence_dir):
            files = os.listdir(sequence_dir)
            jpeg_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg'))]
            if jpeg_files:
                jpeg_files.sort()
                first_frame = os.path.join(sequence_dir, jpeg_files[0])
                if os.path.getsize(first_frame) > 0:
                    log(f"First frame found: {jpeg_files[0]}")
                    time.sleep(2)
                    return first_frame
        time.sleep(1)
    log(f"Timeout: no JPEG frames created in {timeout}s")
    return None


def open_sequence_in_sammie(sequence_path):
    try:
        if os.path.isdir(sequence_path):
            files = os.listdir(sequence_path)
            jpeg_files = sorted([f for f in files if f.lower().endswith(('.jpg', '.jpeg'))])
            if not jpeg_files:
                log(f"ERROR: No JPEG files found in {sequence_path}")
                return
            first_frame = os.path.join(sequence_path, jpeg_files[0])
        else:
            first_frame = sequence_path

        cmd = SAMMIE_CMD + [first_frame]
        log(f"Opening sequence in Sammie 2.0: {first_frame}")
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        log("Sammie 2.0 started successfully.")
    except Exception as e:
        log(f"Error opening Sammie: {e}")


def export_and_open_sammie(selection):
    import flame
    log("="*60)
    log("STARTING JPEG SEQUENCE EXPORT TO SAMMIE 2.0")
    log("="*60)

    if not os.path.exists(PRESET_PATH):
        log("ERROR: JPEG preset not found!")
        log(f"Expected location: {PRESET_PATH}")
        log("Please ensure the EXPORT_JPEG_SAMMIE.xml preset is installed.")
        return

    exported_count = 0
    for item in selection:
        clip = get_clip_from_item(item)
        if clip:
            sequence_dir = export_clip_to_jpeg_sequence(clip, PRESET_PATH, EXPORT_ROOT)
            if sequence_dir:
                first_frame = wait_for_sequence(sequence_dir)
                if first_frame:
                    open_sequence_in_sammie(first_frame)
                    exported_count += 1
                else:
                    log(f"WARNING: No JPEG frames were created in: {sequence_dir}")
        else:
            log(f"ERROR: Could not extract clip from item: {type(item).__name__}")
            if isinstance(item, flame.PyClipNode):
                log("Running diagnostic to help troubleshoot...")
                diagnose_pyclipnode(item)

    log("="*60)
    log(f"PROCESS COMPLETED - Exported {exported_count} sequence(s)")
    log("="*60)


def scope_clip(selection):
    import flame
    return any(isinstance(item, (flame.PyClip, flame.PySequence)) for item in selection)


def scope_clip_node(selection):
    import flame
    return all(isinstance(item, flame.PyClipNode) for item in selection)


def get_media_panel_custom_ui_actions():
    return [{
        "name": "Export",
        "actions": [{
            "name": "Open Sammie 2.0",
            "execute": export_and_open_sammie,
            "minimumVersion": "2022",
        }]
    }]


def get_batch_custom_ui_actions():
    return [{
        "name": "Export",
        "actions": [{
            "name": "Open Sammie 2.0",
            "execute": export_and_open_sammie,
            "minimumVersion": "2022",
        }]
    }]


get_media_panel_custom_ui_actions.minimum_version = "2022"
get_batch_custom_ui_actions.minimum_version = "2022"

