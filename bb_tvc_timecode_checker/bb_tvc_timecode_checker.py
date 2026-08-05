"""
Script Name: BB TVC Timecode Checker
Script Version: 2.1
Flame Version: 2026.1
Written by: Bryan Bayley
Creation Date: 12.02.25
Update Date: 08.04.26

Description:
Select clips or sequences in the Media Panel to check:
1. Does the record timecode start at 01:00:00:00 - or at a recognized
   lead-in start: 59:59:00 (1s black head + tail) or 59:50:00 / 59:53:00
   (slate)?
2. Is the duration a standard TVC length (6s, 15s, 30s, 60s, 90s), after
   accounting for whatever the start timecode implies is around the
   program?

Lead-in layouts are inferred from the start timecode only - the script
cannot see whether a slate or black is really there, so the results dialog
notes when a layout was assumed so it can be confirmed visually.

Menus:
Right-click on clips or sequences in the Media Panel -> TVC Checks... ->
Check Start Timecode and Duration

Updates:
v2.1 08.04.26
- Recognizes black head/tail and slate lead-in layouts from the start
  timecode: 59:59:00 assumes 1s of black at head and tail (program + 2s);
  59:50:00 / 59:53:00 assume a 10s / 7s slate lead-in with nothing after
  the program. The duration check accounts for the assumed layout.
- Condensed results dialog: when everything passes it reports one line per
  layout (e.g. "All 4 timelines have 1s black head + tail and are the
  correct length"); per-item detail appears only for failures and errors.
- An error while checking one item no longer aborts the remaining items;
  errored items are listed in the summary dialog instead.
- Results dialog switched to Qt (PySide6/PySide2 fallback).
"""

import traceback

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

SCRIPT_NAME = "BB TVC Timecode Checker"

STANDARD_DURATIONS = [6, 15, 30, 60, 90]  # Standard commercial lengths in seconds

# Recognized start-timecode layouts: (start TC, extra seconds beyond the
# program, note for fail reasons, description for the passed summary - the
# last two are None when nothing is assumed). 59:59:00 assumes 1s of black
# at head AND tail; the slate starts assume the lead-in only, with nothing
# after the program.
KNOWN_LAYOUTS = [
    ("01:00:00:00", 0, None, None),
    ("00:59:59:00", 2, "1s black head + tail", "1s black head + tail"),
    ("00:59:50:00", 10, "slate lead-in (10s)", "a 10s slate lead-in"),
    ("00:59:53:00", 7, "slate lead-in (7s)", "a 7s slate lead-in"),
]


def message_box(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(SCRIPT_NAME)
    msg.setText(message)
    msg.exec_()


def get_fps_float(fps_string):
    # Extracts a float from the Flame FPS string (e.g. "23.976 fps" -> 23.976).
    try:
        return float(fps_string.split(" ")[0])
    except Exception:
        return 0.0


def sanitize_tc(tc_string, fps_string):
    # Adjusts the timecode delimiters (: ; +) to match the frame rate.
    try:
        clean_tc = tc_string.replace("+", ":").replace(";", ":")
        parts = clean_tc.split(":")
        if len(parts) != 4:
            return tc_string

        hh, mm, ss, ff = parts

        if "23.976" in fps_string or "24" in fps_string:
            return f"{hh}:{mm}:{ss}+{ff}"
        elif "DF" in fps_string and "NDF" not in fps_string:
            return f"{hh}:{mm}:{ss};{ff}"
        else:
            return f"{hh}:{mm}:{ss}:{ff}"
    except Exception:
        return tc_string


def detect_layout(item, fps_str):
    # Matches the start timecode against KNOWN_LAYOUTS. Returns
    # ((start_tc, extra_seconds, note), found_tc); the layout is None when
    # the start is unrecognized. For sequences whose container start matches
    # nothing, the first segment's record-in is tried as a fallback.
    container_start = flame.PyTime(item.start_frame, fps_str)

    candidates = [container_start]
    if isinstance(item, flame.PySequence):
        try:
            candidates.append(item.versions[0].tracks[0].segments[0].record_in)
        except IndexError:
            pass

    for candidate in candidates:
        for layout in KNOWN_LAYOUTS:
            target = flame.PyTime(sanitize_tc(layout[0], fps_str), fps_str)
            if candidate == target:
                return layout, candidate

    return None, container_start


def check_duration_is_standard(item, fps_float, extra_seconds):
    # Checks the duration against the standard TVC lengths, after removing
    # the extra seconds the detected layout implies (black/slate lead-in and
    # tail). Returns (True, "OK") or (False, "Reason").
    total_frames = item.duration.frame

    if fps_float == 0:
        return False, "Invalid FPS"

    # In 23.976 workflows a "30s" spot is exactly 720 frames (24 * 30) even
    # though that is physically 30.03 seconds, so measure against the integer
    # timebase rather than the raw float rate.
    timebase = round(fps_float)  # 23.976 -> 24, 29.97 -> 30

    program_frames = total_frames - extra_seconds * timebase

    if program_frames <= 0:
        return False, f"Too Short ({total_frames}f total)"

    program_seconds = program_frames / timebase

    if program_seconds in STANDARD_DURATIONS:
        return True, f"{int(program_seconds)}s"

    # Whole seconds, just not a standard commercial length
    if program_frames % timebase == 0:
        return False, f"Non-Std Length ({int(program_seconds)}s)"

    return False, f"Odd Time ({total_frames}f)"


def passed_sentence(count, desc):
    # One-line summary for timelines that all passed under the same layout.
    if count == 1:
        if desc is None:
            return "The timeline starts at 01:00:00:00 and is the correct length."
        return f"The timeline has {desc} and is the correct length."
    if desc is None:
        return f"All {count} timelines start at 01:00:00:00 and are the correct length."
    return f"All {count} timelines have {desc} and are the correct length."


def verify_tvc_specs(selection):
    print(f"=== {SCRIPT_NAME} ===")

    passed = []
    passed_descs = []
    failed = []
    errored = []

    for item in selection:
        if not isinstance(item, flame.PyClip):
            continue

        item_name = str(item.name)[1:-1]

        try:
            fps_str = item.frame_rate
            error_reasons = []
            extra_seconds = 0
            note = None
            desc = None

            layout, found_tc = detect_layout(item, fps_str)
            if layout is None:
                readable_found = str(found_tc).replace("+", ":").replace(";", ":")
                error_reasons.append(f"Bad Start ({readable_found})")
            else:
                start_tc, extra_seconds, note, desc = layout
                if note:
                    note = f"{note} assumed (starts {start_tc[3:]})"

            is_dur_valid, dur_msg = check_duration_is_standard(
                item, get_fps_float(fps_str), extra_seconds
            )
            if not is_dur_valid:
                error_reasons.append(f"Bad Dur: {dur_msg}")
        except Exception:
            print(f"[ERROR] {item_name}:")
            traceback.print_exc()
            errored.append(item_name)
            continue

        if error_reasons:
            reason_str = ", ".join(error_reasons)
            if note:
                reason_str += f" [{note}]"
            print(f"[FAIL] {item_name} -> {reason_str}")
            failed.append(f"{item_name}\n   -> {reason_str}")
        else:
            detail = f"{dur_msg} + {note}" if note else dur_msg
            print(f"[PASS] {item_name} -> {detail}")
            passed.append(item_name)
            passed_descs.append(desc)

    if not (passed or failed or errored):
        return

    # Per-item detail only for problems; passes are condensed by layout.
    if failed or errored:
        msg = f"Passed: {len(passed)}\nFailed: {len(failed) + len(errored)}\n\n"
        parts = []
        if failed:
            block = "--- FAILURES ---\n"
            block += "\n".join(failed[:10])  # Limit UI height
            if len(failed) > 10:
                block += "\n...and others."
            parts.append(block)
        if errored:
            parts.append(
                "--- ERRORS (see the Flame shell) ---\n" + "\n".join(errored)
            )
        message_box(msg + "\n\n".join(parts))
        return

    unique_descs = set(passed_descs)
    if len(unique_descs) == 1:
        msg = passed_sentence(len(passed), passed_descs[0])
    else:
        lines = [f"All {len(passed)} timelines are the correct length:"]
        for layout in KNOWN_LAYOUTS:
            desc = layout[3]
            count = passed_descs.count(desc)
            if count:
                if desc is None:
                    lines.append(f"- {count} starting at 01:00:00:00")
                else:
                    lines.append(f"- {count} with {desc}")
        msg = "\n".join(lines)

    if any(d is not None for d in passed_descs):
        msg += "\n\nLayouts inferred from the start timecode - confirm visually."
    message_box(msg)


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "TVC Checks...",
            "actions": [
                {
                    "name": "Check Start Timecode and Duration",
                    "isVisible": scope_clip,
                    "execute": verify_tvc_specs,
                    "minimumVersion": "2021.1.0.0",
                }
            ]
        }
    ]
