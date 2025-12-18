"""
Script Name: TVC Timecode Checker
Script Version: 2.0
Flame Version: 2026.1
Written by: Bryan Bayley
Creation Date: 12.02.25

Description:

    Select Clips or Sequences in the Media Panel to check:
    1. Does the Record Timecode start at 01:00:00:00?
    2. Is the duration a standard TVC length (6s, 15s, 30s, 60s, 90s)?

Menu:

    Right-click on clips or sequences in the Media Panel -> TVC Checks... -> Check Start Timecode and Duration
"""

import flame

# --- Constants ---
STANDARD_DURATIONS = [6, 15, 30, 60, 90] # Standard commercial lengths in seconds
TARGET_START_TC = "01:00:00:00"

def get_fps_float(fps_string):
    # Extracts a float value from the Flame FPS string (e.g., '23.976 fps' -> 23.976) Useful for duration math.

    try:
        # Split "23.976 fps" and take the first part
        val = float(fps_string.split(" ")[0])
        # Round 23.976 up to 24 for timebase calculations if preferred,
        # but for strict duration checking, raw float is usually fine.
        return val
    except:
        return 0.0

def sanitize_tc(tc_string, fps_string):
    # Adjusts the Timecode string delimiters (: ; +) to match the Frame Rate.

    try:
        clean_tc = tc_string.replace("+", ":").replace(";", ":")
        parts = clean_tc.split(":")
        if len(parts) != 4: return tc_string

        hh, mm, ss, ff = parts

        if "23.976" in fps_string or "24" in fps_string:
            return f"{hh}:{mm}:{ss}+{ff}"
        elif "DF" in fps_string and "NDF" not in fps_string:
            return f"{hh}:{mm}:{ss};{ff}"
        else:
            return f"{hh}:{mm}:{ss}:{ff}"
    except:
        return tc_string

def check_duration_is_standard(item, fps_float):
    # Checks if the item duration matches a standard TVC length (15, 30, 60, 90). Returns (True, "OK") or (False, "Reason").
    # Get total frames. PyTime.frame gives absolute frame count.
    # Note: For Sequences, we assume the duration is the full container length.

    total_frames = item.duration.frame

    if fps_float == 0:
        return False, "Invalid FPS"

    # Calculate seconds.
    # Note: In 23.976 workflows, a "30s" spot is often exactly 720 frames (24 * 30),
    # even though physically that is 30.03 seconds.
    # We check against the Timebase (int) to be safe for editorial standards.

    timebase = round(fps_float) # 23.976 -> 24, 29.97 -> 30

    current_seconds = total_frames / timebase

    # Check if it matches a standard bucket
    if current_seconds in STANDARD_DURATIONS:
        return True, f"{int(current_seconds)}s"

    # Check if it is at least a whole second (no partial frames)
    if total_frames % timebase == 0:
        return False, f"Non-Std Length ({int(current_seconds)}s)"

    return False, f"Odd Time ({total_frames}f)"

def verify_tvc_specs(target_tc=None):
    # Argument Fix for Context Menu (Tuple vs String)
    if not isinstance(target_tc, str):
        target_tc = TARGET_START_TC

    selection = flame.media_panel.selected_entries
    if not selection:
        return

    print(f"=== TVC Checker (Start: {target_tc}) ===")

    passed_items = []
    failed_items = []

    for item in selection:
        # Check both Clips and Sequences
        if isinstance(item, flame.PyClip):
            obj_name = item.name
            fps_str = item.frame_rate
            fps_val = get_fps_float(fps_str)

            error_reasons = []

            # --- CHECK 1: Start Timecode ---
            formatted_target = sanitize_tc(target_tc, fps_str)

            try:
                target_obj = flame.PyTime(formatted_target, fps_str)
                container_start = flame.PyTime(item.start_frame, fps_str)

                # Default logic: Container must match
                is_start_valid = (container_start == target_obj)

                # Sequence Fallback: Drill down to first segment
                found_tc = container_start
                if not is_start_valid and isinstance(item, flame.PySequence):
                    try:
                        if len(item.versions) > 0 and len(item.versions[0].tracks) > 0:
                            first_seg = item.versions[0].tracks[0].segments[0]
                            found_tc = first_seg.record_in
                            if found_tc == target_obj:
                                is_start_valid = True
                    except:
                        pass

                if not is_start_valid:
                    readable_found = str(found_tc).replace("+", ":").replace(";", ":")
                    error_reasons.append(f"Bad Start ({readable_found})")

            except Exception as e:
                error_reasons.append("TC Error")

            # --- CHECK 2: Duration (Odd Time) ---
            is_dur_valid, dur_msg = check_duration_is_standard(item, fps_val)

            if not is_dur_valid:
                error_reasons.append(f"Bad Dur: {dur_msg}")

            # --- Final Verdict ---
            if not error_reasons:
                print(f"[PASS] {obj_name}")
                passed_items.append(obj_name)
            else:
                reason_str = ", ".join(error_reasons)
                print(f"[FAIL] {obj_name} -> {reason_str}")
                failed_items.append(f"{obj_name}\n   -> {reason_str}")

# --- Summary Dialog ---
    if failed_items:
        msg = f"Passed: {len(passed_items)}\nFailed: {len(failed_items)}\n\n"
        msg += "--- FAILURES ---\n"
        msg += "\n".join(failed_items[:10]) # Limit UI height
        if len(failed_items) > 10: msg += "\n...and others."

        flame.messages.show_in_dialog("TVC QC Results", msg, "warning", ["OK"])
    else:
        success_msg = f"All {len(passed_items)} items passed QC.\n\n"
        success_msg += "• Start TC: OK\n"
        success_msg += "• Duration: OK"

        print("All items passed.")
        flame.messages.show_in_dialog("TVC QC Results", success_msg, "info", ["Great"])

######################
# Context Menu Scope #
######################

def get_media_panel_custom_ui_actions():

    def scope_clip(selection):
        for item in selection:
            if isinstance(item, (flame.PySequence, flame.PyClip)):
                return True
        return False

    return [
        {
            "name": "TVC Checks...",
            "actions": [
                {
                    "name": "Check Start Timecode and Duration",
                    "isVisible": scope_clip,
                    "execute": verify_tvc_specs,
                    "minimumVersion": "2021.1.0.0"
                }
            ]
        }
    ]
