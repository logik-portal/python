"""
Script Name: Black Head and Tail
Script Version: 1.1
Flame Version: 2027
Written by: Bryan Bayley
Help from: Fred Warren
Creation Date: 08.16.21
Update Date: 06.02.26

Description:
Add one second of virtual black head and tail to the selected sequences.

The black source is generated automatically (a temporary 1-second black Colour
Source), so nothing needs to be set up on the desktop beforehand. Set each
sequence's record patch to the track you want the black on (the patch can't be
controlled from Python). The head black is placed before the first frame and the
tail black after the last frame; neither edit ripples or shifts existing content.
Each black handle's timeline segment colour is set to black. If a sequence has no
room before its start the head won't land, and a warning lists any sequence whose
head or tail was not added.

Menus:
Right-click a sequence in the Media Panel -> Sequence... -> Black Heads and Tails

Updates:
v1.1 06.02.26
- Restore the original selection and active timeline when finished (creating and
  deleting the temp source otherwise left the top-most item selected).

v1.0 08.16.21
- Initial release.
"""

import flame

try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets


BLACK = (0.0, 0.0, 0.0)
TMP_NAME = "__tmp_black__"


def show_warning(message):
    QtWidgets.QMessageBox.warning(None, "Black Head and Tail", message)


def _val(attr):
    '''Unwrap a Flame property that may be a value or a get_value() wrapper.'''
    try:
        return attr.get_value()
    except AttributeError:
        return attr


def _one_second_frames(sequence):
    '''Number of frames in one second, from the sequence frame rate.'''
    # frame_rate reports a string such as "23.976 fps".
    try:
        return max(1, round(float(str(_val(sequence.frame_rate)).split()[0])))
    except (ValueError, IndexError):
        return 24  # sensible fallback


def _top_track(clip):
    '''Top video track of the current version, or None.'''
    versions = clip.versions
    if not versions:
        return None
    tracks = versions[0].tracks
    return tracks[0] if tracks else None


def _make_black_source(destination, sequence, frames):
    '''Build a temporary 1-second black Colour Source sequence to edit from.'''
    duration = flame.PyTime(frames)

    # Match the reference sequence's format so the source conforms cleanly;
    # fall back to project defaults if any matched argument is rejected.
    try:
        black = destination.create_sequence(
            name=TMP_NAME,
            video_tracks=1,
            width=_val(sequence.width),
            height=_val(sequence.height),
            ratio=_val(sequence.ratio),
            bit_depth=_val(sequence.bit_depth),
            scan_mode=_val(sequence.scan_mode),
            frame_rate=_val(sequence.frame_rate),
            duration=duration,
        )
    except Exception:
        black = destination.create_sequence(name=TMP_NAME, duration=duration)

    # Turn its single gap into black, then colour the (re-fetched) segment black
    # so the inserted handles carry the colour in through the Overwrite Edit.
    btrack = _top_track(black)
    if btrack is not None and btrack.segments:
        btrack.segments[0].set_gap_colour(*BLACK)
        btrack.segments[0].colour = BLACK

    # Clear any in/out marks so the full second is used as the edit source.
    black.in_mark = None
    black.out_mark = None

    return black


def black_head_tail(selection):

    sequences = [item for item in selection if isinstance(item, flame.PyClip)]
    if not sequences:
        return

    # Build one temporary black source, sized to the first sequence's format.
    reference = sequences[0]
    frames = _one_second_frames(reference)
    try:
        black = _make_black_source(reference.parent, reference, frames)
    except Exception as error:
        show_warning("Could not create the temporary black source:\n\n{}".format(error))
        return

    failures = []
    try:
        for clip in sequences:

            name = _val(clip.name)

            # Isolate each sequence so one failure can't abort the whole batch.
            try:
                clip.open()

                dur_before = int(clip.duration.frame)

                # Head black: back-time a 1-second overwrite to the start.
                clip.in_mark = None
                clip.out_mark = None
                clip.out_mark = flame.PyTime(1)
                flame.media_panel.selected_entries = [black]
                flame.execute_shortcut("Overwrite Edit")

                dur_after_head = int(clip.duration.frame)
                head_ok = dur_after_head > dur_before

                # Tail black: overwrite a 1-second clip after the last frame.
                clip.in_mark = None
                clip.out_mark = None
                clip.in_mark = int(clip.duration.frame) + 1
                flame.media_panel.selected_entries = [black]
                flame.execute_shortcut("Overwrite Edit")

                dur_after_tail = int(clip.duration.frame)
                tail_ok = dur_after_tail > dur_after_head

                print("[Black Head and Tail] '{}': head {}, tail {}".format(
                    name,
                    "added" if head_ok else "SKIPPED",
                    "added" if tail_ok else "SKIPPED",
                ))

                if not head_ok or not tail_ok:
                    failures.append((name, head_ok, tail_ok))

                # Move playhead to start, frame sequence, focus top track.
                flame.execute_shortcut("Go To Clip Start")
                flame.execute_shortcut("Set Focus on Topmost Visible Track")
                flame.execute_shortcut("Timeline Home")

                clip.in_mark = None
                clip.out_mark = None

            except Exception as error:
                print("[Black Head and Tail] '{}': ERROR -> {}".format(name, error))
                failures.append((name, False, False))
                continue
    finally:
        # Always remove the temporary black source.
        flame.delete(black, confirm=False)

    # Restore the user's selection and active timeline. Creating then deleting the
    # temp sequence leaves Flame with the top-most item selected, so re-select the
    # processed sequences and re-open the last one.
    try:
        flame.media_panel.selected_entries = sequences
        sequences[-1].open()
    except Exception:
        pass

    if failures:
        lines = "\n".join(
            "  {}  (head {}, tail {})".format(
                n, "added" if h else "NOT added", "added" if t else "NOT added")
            for (n, h, t) in failures
        )
        show_warning(
            "Some black handles were not added:\n\n{}\n\n"
            "See the console for details.".format(lines)
        )


def scope_clip(selection):
    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            'name': 'Sequence...',
            'actions': [
                {
                    'name': 'Black Heads and Tails',
                    'isVisible': scope_clip,
                    'execute': black_head_tail,
                }
            ]
        }
    ]
