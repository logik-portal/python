"""
Script Name: Open in Photoshop
Script Version: 1.0
Flame Version: 2024
Written by: Bryan Bayley
Help from: Michael Vaglienty
Creation Date: 08.04.26

Description:
If a clip or timeline segment is a soft-imported still image (PSD, PNG, JPEG,
TIFF, and other Photoshop-friendly formats), open the source file in Photoshop.
Photoshop is targeted by its bundle id, so it does not need to be the default
app for the file type; if Photoshop is not installed the file opens in the
default app instead. For frame sequences, the frame the playhead is parked on
opens (Timeline and Media Panel); otherwise the first frame opens.
Written for macOS. Replaces the older "Open PSD in Photoshop" script.

Menus:
Right-click a clip in the Timeline -> Open... -> Open in Photoshop
Right-click a Clip node in Batch -> Open... -> Open in Photoshop
Right-click a clip in the Media Panel -> Open... -> Open in Photoshop
Right-click a file in the MediaHub -> Open... -> Open in Photoshop
"""

import os
import re
import subprocess
import traceback

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

SCRIPT_NAME = "Open in Photoshop"

# Stable across Photoshop versions ("Adobe Photoshop 2025" etc.), so Launch
# Services finds whichever one is installed.
PHOTOSHOP_BUNDLE_ID = "com.adobe.Photoshop"

# Still-image formats Photoshop opens directly.
EXTENSIONS = [
    ".psd", ".psb", ".png", ".jpg", ".jpeg",
    ".tif", ".tiff", ".tga", ".bmp", ".gif",
]


def message_box(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(SCRIPT_NAME)
    msg.setText(message)
    msg.exec_()


def valid_file_extension(file_path):
    # A supported still-image extension, and not a Flame [start-end]
    # frame-sequence path - Photoshop opens single files only.
    _, ext = os.path.splitext(file_path)
    return ext.lower() in EXTENSIONS and "[" not in file_path


def clip_media_path(clip):
    # First segment's source path - empty sequences have no segments.
    try:
        return clip.versions[0].tracks[0].segments[0].file_path
    except IndexError:
        return ""


# A frame counter is 4+ digits delimited from the name by "." or "_" (or
# the whole basename) - "plate.0100.jpg" / "plate_0100.jpg" yes; the
# version tag in "logo_v002.psd" and short-numbered stills families like
# "board_01.jpg" no.
FRAME_RE = re.compile(r"^(?P<prefix>(?:.*[._])?)(?P<num>\d{4,})(?P<ext>\.[A-Za-z0-9]+)$")


def offset_frame_path(path, offset):
    # Best effort: for numbered frame sequences, the file `offset` frames
    # after `path`; otherwise `path` unchanged. Before trusting the offset,
    # several frames of the presumed sequence must exist on disk (the next
    # three, the midpoint and the target) so a family of versioned stills
    # is never mistaken for a sequence and opened at the wrong version.
    if offset <= 0:
        return path
    m = FRAME_RE.match(os.path.basename(path))
    if not m:
        return path

    prefix = os.path.join(os.path.dirname(path), m.group("prefix"))
    num, ext = m.group("num"), m.group("ext")
    first = int(num)

    def frame_file(n):
        return f"{prefix}{n:0{len(num)}d}{ext}"

    needed = {first + 1, first + 2, first + 3, first + offset // 2, first + offset}
    if all(os.path.isfile(frame_file(n)) for n in needed):
        return frame_file(first + offset)
    return path


def playhead_offset(container, segment):
    # Frames between the playhead and the segment's start. 0 when the
    # playhead is not parked inside the segment, or when the container has
    # no usable playhead - opening the first frame is the correct fallback,
    # so this fails quiet.
    try:
        current = container.current_time.get_value()
        offset = current.frame - segment.record_in.frame
        length = segment.record_out.frame - segment.record_in.frame
        if 0 <= offset <= length:
            return offset
    except Exception:
        pass
    return 0


# Per-context accessors for the shared open_selection() loop.

def segment_path(item):
    return offset_frame_path(item.file_path, playhead_offset(flame.timeline.clip, item))


def clip_playhead_path(clip):
    try:
        segment = clip.versions[0].tracks[0].segments[0]
    except IndexError:
        return ""
    return offset_frame_path(segment.file_path, playhead_offset(clip, segment))


def node_path(item):
    return str(item.media_path)[1:-1]


def file_path(item):
    return str(item.path)


def quoted_name(item):
    return str(item.name)[1:-1]


def file_name(item):
    return os.path.basename(str(item.path))


def open_selection(selection, get_path, get_name):
    # Shared per-item loop. The scope only guarantees that *some* selected
    # item is a supported still, so each item is re-validated here;
    # unsupported items in a mixed selection are skipped silently, problems
    # are collected and reported in one dialog at the end.
    print(f"=== {SCRIPT_NAME} ===")
    problems = []

    for item in selection:
        name = "?"
        try:
            name = get_name(item)
            path = get_path(item)

            if not path or not valid_file_extension(path):
                continue

            if not os.path.isfile(path):
                print(f"[SKIP] {name} -> file not found: {path}")
                problems.append(f"{name}: file not found\n{path}")
                continue

            result = subprocess.run(
                ["open", "-b", PHOTOSHOP_BUNDLE_ID, path],
                capture_output=True, text=True,
            )
            if result.returncode != 0:
                # Photoshop not installed - default app as a fallback
                print(f"[NOTE] {name} -> Photoshop not found, using the default app")
                result = subprocess.run(
                    ["open", path], capture_output=True, text=True
                )
                if result.returncode != 0:
                    print(f"[SKIP] {name} -> {result.stderr.strip()}")
                    problems.append(f"{name}: could not be opened (see the Flame shell)")
                    continue
            print(f"[OPEN] {name} -> {path}")
        except Exception:
            print(f"[ERROR] {name}:")
            traceback.print_exc()
            problems.append(f"{name}: error (see the Flame shell)")

    if problems:
        message_box("Some files could not be opened:\n\n" + "\n\n".join(problems))


def timeline_open(selection):
    segments = [item for item in selection if isinstance(item, flame.PySegment)]
    open_selection(segments, segment_path, quoted_name)


def batch_open(selection):
    clips = [item for item in selection if item.type == "Clip"]
    open_selection(clips, node_path, quoted_name)


def mediapanel_open(selection):
    clips = [item for item in selection if isinstance(item, flame.PyClip)]
    open_selection(clips, clip_playhead_path, quoted_name)


def mediahub_open(selection):
    open_selection(selection, file_path, file_name)


def scope_timeline_clip(selection):
    for item in selection:
        if isinstance(item, flame.PySegment) and valid_file_extension(item.file_path):
            return True
    return False


def scope_batch_clip(selection):
    for item in selection:
        if item.type == "Clip" and valid_file_extension(node_path(item)):
            return True
    return False


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip) and valid_file_extension(clip_media_path(item)):
            return True
    return False


def scope_file(selection):
    for item in selection:
        if valid_file_extension(file_path(item)):
            return True
    return False


def get_timeline_custom_ui_actions():
    return [
        {
            "name": "Open...",
            "actions": [
                {
                    "name": "Open in Photoshop",
                    "isVisible": scope_timeline_clip,
                    "execute": timeline_open,
                    "minimumVersion": "2023"
                }
            ]
        }
    ]


def get_batch_custom_ui_actions():
    return [
        {
            "name": "Open...",
            "actions": [
                {
                    "name": "Open in Photoshop",
                    "isVisible": scope_batch_clip,
                    "execute": batch_open,
                    "minimumVersion": "2023"
                }
            ]
        }
    ]


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Open...",
            "actions": [
                {
                    "name": "Open in Photoshop",
                    "isVisible": scope_clip,
                    "execute": mediapanel_open,
                    "minimumVersion": "2023"
                }
            ]
        }
    ]


def get_mediahub_files_custom_ui_actions():
    return [
        {
            "name": "Open...",
            "actions": [
                {
                    "name": "Open in Photoshop",
                    "isVisible": scope_file,
                    "execute": mediahub_open,
                    "minimumVersion": "2023"
                }
            ]
        }
    ]
