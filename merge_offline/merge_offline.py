"""
Script Name: Merge Offline
Script Version: 1.1
Flame Version: 2027
Written by: Bryan Bayley
Help from: Fred Warren
Creation Date: 07.29.26

Description:
Automates merging an offline edit (AAF/XML/EDL) with a reference video for
online comparison. Stacks the AAF/XML/EDL edit above the reference, sets
primary/secondary tracks for A/B comparison, locks the reference video and
audio, adds virtual padding and a black top track, and deletes the
standalone reference clip from the Media Panel. Padding and the black
head/tail are derived from each sequence's own frame rate and start
timecode. A 2-pop / slate lead-in (a start inside the last minute before
the hour, e.g. 59:58:00) is detected and cut out of both the sequence and
the reference so the program starts on the hour before padding is added.

The reference clip is found on the same reel as the selected sequence using
a layered lookup:
1. Any clip whose name contains "offline", "reference" or the word "ref"
   (case-insensitive). If several match, the one named most like the
   sequence wins.
2. Otherwise, the clip whose name is most similar to the sequence name
   (fuzzy match, e.g. "JOB123_ONLINE" finds "JOB123_v12").
Sequences with no plausible reference are left untouched and listed in a
single dialog after everything else has merged.

Prerequisites:
- Import the AAF/XML/EDL to a sequence reel.
- Import the reference video to the same reel, with the same start frame as
  the offline edit (e.g. don't have the offline edit start on the first
  frame of picture while the reference video has a 2-pop).
- This script uses flame.execute_shortcut(). The shortcuts used must still
  exist in the Keyboard Shortcut editor (they do by default): Nudge 1 Track
  Up, Nudge 1 Track Down, Overwrite Edit, Timeline Home, Set Focus on
  Topmost Visible Track.

Menus:
Right-click a sequence in the Media Panel -> Sequence... -> Merge Offline
"""

import re
import traceback
from difflib import SequenceMatcher

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

SCRIPT_NAME = "Merge Offline"

# Minimum similarity (0-1) between the sequence name and a clip name for the
# fuzzy fallback to accept the clip as the reference.
FUZZY_MATCH_THRESHOLD = 0.6


def message_box(message):
    msg = QtWidgets.QMessageBox()
    msg.setWindowTitle(SCRIPT_NAME)
    msg.setText(message)
    msg.exec_()


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def name_similarity(name_a, name_b):
    return SequenceMatcher(None, name_a.lower(), name_b.lower()).ratio()


def is_reference_name(name):
    lowered = name.lower()
    if "offline" in lowered or "reference" in lowered:
        return True
    # Bare "ref" only counts as its own word, so names like "preflight" or
    # "refresh" don't false-match.
    return re.search(r"(^|[^a-z])ref([^a-z]|$)", lowered) is not None


def find_reference(clip, selected_names):
    """Layered lookup for the reference clip on the sequence's reel."""
    clip_name = str(clip.name)[1:-1]

    # Only plain clips on the same reel are candidates - sequences (including
    # other selected ones) can never be picked as a reference.
    candidates = []
    for item in getattr(clip.parent, "clips", []):
        item_name = str(item.name)[1:-1]
        if item_name != clip_name and item_name not in selected_names:
            candidates.append(item)

    keyword_matches = [item for item in candidates if is_reference_name(str(item.name)[1:-1])]
    if keyword_matches:
        return max(keyword_matches, key=lambda item: name_similarity(clip_name, str(item.name)[1:-1]))

    best = None
    best_score = FUZZY_MATCH_THRESHOLD
    for item in candidates:
        score = name_similarity(clip_name, str(item.name)[1:-1])
        if score >= best_score:
            best = item
            best_score = score
    return best


def lead_in_before_hour(seq_start, frame_rate):
    """If the timecode starts inside the last minute before an hour mark
    (e.g. a 59:58:00 2-pop lead-in before a 1:00:00:00 program start),
    return (hour mark PyTime, lead-in length in frames). Otherwise None."""
    # Flame renders PyTime as e.g. '00:59:58+00' - quoted, with "+" (or ";"
    # for drop-frame) before the frames field.
    match = re.search(r"(\d+)([:;+.])(\d{2})([:;+.])(\d{2})([:;+.])(\d{2,3})", str(seq_start))
    if match is None:
        return None
    hours, sep1, minutes, sep2, seconds, sep3, frames = match.groups()
    if minutes != "59":
        return None
    one_second = round(float(str(frame_rate).split()[0]))
    lead_frames = (60 - int(seconds)) * one_second - int(frames)
    timecode = "%02d%s00%s00%s00" % (int(hours) + 1, sep1, sep2, sep3)
    try:
        return flame.PyTime(timecode, frame_rate), lead_frames
    except Exception:
        # constructor may not accept the rendered separators - plain SMPTE
        return flame.PyTime("%02d:00:00:00" % (int(hours) + 1), frame_rate), lead_frames


def timecode_of(value):
    """Timecode string of a PyTime that may arrive wrapped in a PyAttribute."""
    if hasattr(value, "get_value"):
        value = value.get_value()
    return str(value)


def remove_lead_in(clip, program_start):
    """Cut every video track and audio channel at the program start and
    delete all segments before it - a manual Lift. The head becomes an
    empty gap and nothing ripples."""
    program_tc = str(program_start)
    labelled = [("V%d" % (index + 1), track)
                for index, track in enumerate(clip.versions[0].tracks)]
    for index, audio_track in enumerate(clip.audio_tracks):
        for channel in audio_track.channels:
            labelled.append(("A%d %s" % (index + 1, str(channel.name)[1:-1]), channel))
    for label, track in labelled:
        try:
            track.cut(program_start)
        except Exception:
            # an edit point may already exist at the program start
            pass
        # The segment starting exactly at the program start marks the
        # boundary; everything before it is lead-in. Matching by timecode
        # string avoids guessing which frame-number space record_in uses.
        if not any(timecode_of(segment.record_in) == program_tc for segment in track.segments):
            print("%s: no edit point at %s on %s - lead-in left in place there"
                  % (SCRIPT_NAME, program_tc.strip("'"), label))
            continue
        while True:
            head = None
            for segment in track.segments:
                if timecode_of(segment.record_in) == program_tc:
                    break
                if segment.type != "Gap":
                    head = segment
                    break
            if head is None:
                break
            flame.delete(head)


def merge_clip(clip, ref):
    # Make sure the clip is open as a sequence
    clip.open()

    # Sequence timing, captured before anything moves: one second of frames
    # at the sequence's own rate, and its own start timecode. start_time is
    # a PyAttribute - unwrap it to the PyTime it holds.
    seq_start = clip.start_time.get_value()
    one_second = round(float(str(clip.frame_rate).split()[0]))

    # Detect a 2-pop / slate lead-in. The lift itself happens after the
    # reference is overwritten, so the reference's own lead-in is removed
    # in the same pass. All downstream timing (padding, black head) is
    # based on the program start on the hour.
    lead_in_start = None
    lead_in = lead_in_before_hour(seq_start, str(clip.frame_rate))
    if lead_in is not None:
        program_start, lead_frames = lead_in
        if int(clip.duration.frame) > lead_frames:
            lead_in_start = seq_start
            seq_start = program_start
        else:
            print("%s: lead-in detected but sequence too short - skipping trim" % SCRIPT_NAME)

    # Get the number of tracks in the AAF/XML/EDL
    num_tracks = len(clip.versions[0].tracks)

    # Move the segments up with the "Nudge 1 Track Up" shortcut - a hack
    # because tracks cannot be patched directly. An extra Nudge Up and
    # Nudge Down leaves a blank track on top for the black padding later.
    for track in range(num_tracks):
        clip.versions[0].tracks[track].selected_segments = clip.versions[0].tracks[track].segments
    flame.execute_shortcut("Nudge 1 Track Up")
    flame.execute_shortcut("Nudge 1 Track Up")
    flame.execute_shortcut("Nudge 1 Track Down")

    # The nudges must have created the empty bottom and top tracks. Stop
    # here if they did not (seen on a 60 fps sequence) - continuing would
    # overwrite the reference onto the picture track.
    tracks_after = len(clip.versions[0].tracks)
    if tracks_after < num_tracks + 2:
        raise RuntimeError(
            "track nudge had no effect: %d tracks before, %d after "
            "(segments per track: %s)"
            % (num_tracks, tracks_after,
               [len(t.segments) for t in clip.versions[0].tracks]))

    # Add a stereo audio track for the incoming reference audio
    clip.create_audio(stereo=True)

    # Overwrite the reference video onto the bottom track and its audio
    # onto the new audio track
    clip.primary_track = clip.versions[0].tracks[0]
    flame.media_panel.selected_entries = [ref]
    flame.execute_shortcut("Overwrite Edit")

    # Remove the lead-in from every track - sequence and freshly
    # overwritten reference alike - by cutting at the program start and
    # deleting the head segments. Nothing ripples, so the remaining
    # content keeps its timecode.
    if lead_in_start is not None:
        remove_lead_in(clip, seq_start)

    # Set primary (top) / secondary (bottom) tracks and lock the
    # reference video and audio
    clip.primary_track = clip.versions[0].tracks[num_tracks]
    clip.secondary_track = clip.versions[0].tracks[0]
    clip.versions[0].tracks[0].locked = True
    clip.audio_tracks[0].channels[0].locked = True

    # Clear in and out marks
    clip.in_mark = None
    clip.out_mark = None

    # Add one second of virtual padding to start and end. padding_start
    # needs an absolute timecode PyTime (a raw frame-count PyTime is not
    # taken as a position) - subtract a second from the sequence's start.
    clip.padding_start = seq_start - one_second
    clip.padding_end = flame.PyTime(int(clip.duration.frame) + one_second + 1)

    # Add black (virtual colour) on the top track and cut it to the
    # picture-only range
    top_track = len(clip.versions[0].tracks) - 1
    clip.versions[0].tracks[top_track].segments[0].set_gap_colour(0, 0, 0)
    clip.versions[0].tracks[top_track].segments[0].colour = (0, 0, 0)
    end_frame = flame.PyTime(int(clip.duration.frame) - (one_second - 1))
    clip.versions[0].tracks[top_track].cut(seq_start)
    clip.versions[0].tracks[top_track].cut(end_frame)
    flame.delete(clip.versions[0].tracks[top_track].segments[1])

    # Move the playhead to the start of the sequence, frame the whole
    # sequence, move focus to the top track
    clip.current_time = flame.PyTime(1)
    flame.execute_shortcut("Timeline Home")
    flame.execute_shortcut("Set Focus on Topmost Visible Track")

    # Delete the standalone reference clip
    flame.media_panel.selected_entries = [clip]
    flame.delete(ref)


def merge_offline(selection):
    selected_names = [str(item.name)[1:-1] for item in selection]
    skipped = []
    failed = []

    for clip in selection:
        clip_name = str(clip.name)[1:-1]
        print("%s: ----- '%s' -----" % (SCRIPT_NAME, clip_name))

        # Find the reference clip before touching the sequence so a missing
        # reference leaves the sequence untouched.
        ref = find_reference(clip, selected_names)
        if ref is None:
            print("%s: no reference clip found - sequence skipped" % SCRIPT_NAME)
            skipped.append(clip_name)
            continue

        try:
            merge_clip(clip, ref)
            print("%s: merge complete for '%s'" % (SCRIPT_NAME, clip_name))
        except Exception:
            print("%s: ERROR while merging '%s':" % (SCRIPT_NAME, clip_name))
            traceback.print_exc()
            failed.append(clip_name)

    messages = []
    if skipped:
        messages.append(
            "No reference clip was found for:\n\n"
            + "\n".join(skipped)
            + "\n\nThese sequences were not merged."
        )
    if failed:
        messages.append(
            "An error interrupted the merge of:\n\n"
            + "\n".join(failed)
            + "\n\nSee the Flame shell for details."
        )
    if messages:
        message_box("\n\n".join(messages))


def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Sequence...",
            "actions": [
                {
                    "name": "Merge Offline",
                    "isVisible": scope_clip,
                    "execute": merge_offline
                }
            ]
        }
    ]
