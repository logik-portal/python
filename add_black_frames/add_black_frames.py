'''
Script Name: Add Black Frames
Script Version: 1.7.5
Flame Version: 2025
Written by: Cursor / ADSK
Creation Date: 05.28.26

Custom Action Type: Media Panel

Description:

    Adds configurable head and tail black frames to selected sequences in place.
    Creates a new top video track with black gap colour (set_gap_colour) at head
    and tail only. Content tracks are not cut or trimmed. start_time and record_in
    are restored after the top-track edit so content timecode is preserved.

Menus:

    Right-click selected sequences -> UC Timelines -> Add Black Frames...

To install:

    Copy add_black_frames.py into /opt/Autodesk/shared/python/add_black_frames/

Updates:

    v1.7.5 06.03.26

        Suppress spurious "no record_in" errors: exclude Gap and Colour Source
        segments from both snapshot and restore since they don't support
        record_in writes.

    v1.7.4 06.03.26

        Replace trim_head/trim_tail (confirmed no-ops on Gap segments) with
        open_seq.padding_start / padding_end to extend the sequence before
        create_track(-1). Colour the full extended Gap in one set_gap_colour
        call, then cut at boundaries, then delete the middle Colour Source.
        Colour Sources do not auto-merge when the middle is deleted (unlike Gaps).

    v1.7.3 06.03.26

        Stop deleting the interior Gap segment. Flame merges the surrounding Gap
        segments back into one when the middle is deleted, leaving only a single
        segment and triggering the overlap error. A Gap segment on the top track
        is transparent; only set_gap_colour (head and tail only) makes it opaque
        black. The interior Gap is left in place so content below shows through.
        Also reverted the incorrect content_end cut; the tail boundary is always
        at original_end regardless of head offset (cuts operate on the already-
        extended timeline so both boundaries are absolute timecodes).

    v1.7.2 05.28.26

        (superseded; incorrect content_end cut caused wrong tail split position)

    v1.7.1 05.28.26

        Trim gap before set_gap_colour; set_gap_colour converts Gap and breaks trim.

    v1.7.0 05.28.26

        Use PySegment.set_gap_colour(0, 0, 0) instead of Colour Correct shortcut.

    v1.6.1 05.28.26

        Settings window only on first run (no config.json); later runs use saved
        head/tail values and go straight to confirm.

    v1.6.0 05.28.26

        Top track only — removed all lower-track cuts and gap insertion.

    v1.5.2 05.28.26

        Stop cutting lower tracks for tail gaps; top track owns tail padding and
        sequence duration. Lower tracks only get head gap cuts.

    v1.5.1 05.28.26

        Precompute frozen PyTime cut points before any edits; lower tracks
        extend head then tail using those absolute timecodes.

    v1.5.0 05.28.26

        Top track: create, Colour Correct, trim_head/trim_tail, cut at snapshotted
        start_time + duration, delete middle; then extend lower tracks.

    v1.4.4 05.28.26

        Lower tracks extend first (tail then head) using snapshotted start_time
        PyTime + frame offsets; top track is created after. Top track uses
        boundary cuts only (no trim).

    v1.4.3 05.28.26

        Extend lower-track tail gaps before top-track middle delete so sequence
        duration reaches head + original + tail; fix record_in restore for gaps.

    v1.4.2 05.28.26

        Top-track and lower-track cuts use snapshotted start_time plus duration
        from before trim/extension (trim_head can shift open_seq.start_time).

    v1.4.1 05.28.26

        Fix top-track cut frame offsets (+1) and delete interior padding by
        duration instead of only when three segments exist.

    v1.4.0 05.28.26

        Top-track padding via boundary cuts at snapshotted start_time (trim
        removed in v1.4.4 once lower tracks extend first).

    v1.3.0 05.28.26

        Merged into single script file (no lib/ folder).

    v1.2.2 05.28.26

        Use segment.slip() for top-track head/tail positioning (superseded).

    v1.2.1 05.28.26

        Use PyTrack.cut(PyTime) from start_time; remove record_in slipping.

    v1.2.0 05.28.26

        Top-track split/slip workflow; fix Qt window closing before confirm.

    v1.1.0 05.28.26

        Gap + Colour Correct workflow (removed PNG import).

    v1.0.0 05.28.26

        Initial release.
'''

import json
import os

import flame

from PySide6 import QtCore, QtWidgets

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, 'config.json')

FOLDER_NAME = 'UC Timelines'
SCRIPT_NAME = 'Add Black Frames (New Top Track)'
SCRIPT_VERSION = 'v1.7.1'

DEFAULT_HEAD_FRAMES = 1
DEFAULT_TAIL_FRAMES = 2
MAX_FRAMES = 24

GAP_BLACK_RGB = (0.0, 0.0, 0.0)


class PaddingResult:
    __slots__ = ('status', 'message', 'sequence_name')

    def __init__(self, status, message='', sequence_name=''):
        self.status = status
        self.message = message
        self.sequence_name = sequence_name


def pyobject_name(obj):
    name = str(getattr(obj, 'name', obj))
    if len(name) >= 2 and name[0] == '"' and name[-1] == '"':
        return name[1:-1]
    return name


def has_config():
    return os.path.isfile(CONFIG_PATH)


def load_config():
    defaults = {
        'head_frames': DEFAULT_HEAD_FRAMES,
        'tail_frames': DEFAULT_TAIL_FRAMES,
    }
    if not os.path.isfile(CONFIG_PATH):
        return defaults
    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as handle:
            data = json.load(handle)
        defaults['head_frames'] = int(data.get('head_frames', DEFAULT_HEAD_FRAMES))
        defaults['tail_frames'] = int(data.get('tail_frames', DEFAULT_TAIL_FRAMES))
    except Exception as exc:
        print(f'[Add Black Frames] Could not read config: {exc}')
    return defaults


def save_config(head_frames, tail_frames):
    data = {
        'head_frames': int(head_frames),
        'tail_frames': int(tail_frames),
    }
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2)
    except Exception as exc:
        print(f'[Add Black Frames] Could not save config: {exc}')


def _unwrap_flame_value(value):
    if value is None:
        return None
    if hasattr(value, 'get_value') and callable(value.get_value):
        try:
            return value.get_value()
        except Exception:
            return value
    return value


def _as_list(value):
    unwrapped = _unwrap_flame_value(value)
    if unwrapped is None:
        return []
    if isinstance(unwrapped, (list, tuple)):
        return list(unwrapped)
    if isinstance(unwrapped, str):
        return [unwrapped]
    try:
        return list(unwrapped)
    except TypeError:
        return [unwrapped]


def _segment_type_name(segment):
    return str(_unwrap_flame_value(getattr(segment, 'type', '')) or '')


def _is_py_segment(obj):
    return isinstance(obj, flame.PySegment)


def _track_segments(track):
    return [segment for segment in _as_list(track.segments) if _is_py_segment(segment)]


def _safe_record_in(segment):
    try:
        return _unwrap_flame_value(segment.record_in)
    except (AttributeError, RuntimeError):
        return None


def _segment_start_frame(segment):
    record_in = _safe_record_in(segment)
    if record_in is None:
        raise RuntimeError(f'Segment has no record_in ({_segment_type_name(segment)})')
    return int(record_in.frame)


def _segment_duration_frames(segment):
    return int(segment.record_duration.frame)


def _segment_end_frame(segment):
    return _segment_start_frame(segment) + _segment_duration_frames(segment) - 1


def _has_colour_correct_effect(segment):
    if not _is_py_segment(segment):
        return False
    for fx in _as_list(segment.effects):
        fx_type = str(_unwrap_flame_value(getattr(fx, 'type', '')) or '').lower()
        if 'colour correct' in fx_type or 'color correct' in fx_type:
            return True
    return False


def _is_colour_source_segment(segment):
    seg_type = _segment_type_name(segment).lower()
    return (
        'colour source' in seg_type
        or 'color source' in seg_type
        or 'virtcolour' in seg_type.replace(' ', '')
    )


def _is_black_padding_segment(segment):
    if _is_colour_source_segment(segment):
        return True
    if _has_colour_correct_effect(segment):
        return True
    return _segment_type_name(segment) == 'Gap'


def _is_padding_segment(segment):
    return _is_black_padding_segment(segment) or _segment_type_name(segment) in (
        'Video', 'Unlinked Video', 'Clip',
    )


def sequence_appears_padded(sequence, head_frames, tail_frames):
    if head_frames <= 0 and tail_frames <= 0:
        return False

    version = sequence.versions[-1]
    if len(version.tracks) < 2:
        return False

    top_track = version.tracks[-1]
    segments = _track_segments(top_track)
    if not segments:
        return False

    duration = int(sequence.duration.frame)
    head_ok = head_frames <= 0
    tail_ok = tail_frames <= 0

    if head_frames > 0:
        head_seg = segments[0]
        if _segment_start_frame(head_seg) == 1 and _is_padding_segment(head_seg):
            if _segment_duration_frames(head_seg) >= head_frames:
                if _is_black_padding_segment(head_seg):
                    head_ok = True

    if tail_frames > 0:
        tail_seg = segments[-1]
        if _is_padding_segment(tail_seg):
            tail_start = _segment_start_frame(tail_seg)
            tail_end = _segment_end_frame(tail_seg)
            if tail_end == duration and _segment_duration_frames(tail_seg) >= tail_frames:
                if tail_start + tail_frames - 1 <= duration:
                    if _is_black_padding_segment(tail_seg):
                        tail_ok = True

    return head_ok and tail_ok


def ensure_timeline_tab():
    if flame.get_current_tab() != 'Timeline':
        flame.set_current_tab('Timeline')


def _normalize_frame_rate(frame_rate):
    rate = str(_unwrap_flame_value(frame_rate) or frame_rate)
    if len(rate) >= 2 and rate[0] == '"' and rate[-1] == '"':
        return rate[1:-1]
    return rate


def _pytime_at_offset(original_start_time, frames_after_start, frame_rate):
    start = _unwrap_flame_value(original_start_time)
    if start is None:
        raise RuntimeError('Sequence has no start_time')

    rate = _normalize_frame_rate(frame_rate)
    try:
        return start + flame.PyTime(frames_after_start, rate)
    except Exception:
        return start + flame.PyTime(frames_after_start)


class PaddingCutTimes:
    __slots__ = (
        'original_start',
        'original_end',
        'head_frames',
        'tail_frames',
        'original_duration',
    )

    def __init__(
        self, original_start_time, original_duration, head_frames, tail_frames, frame_rate,
    ):
        self.original_duration = original_duration
        self.head_frames = head_frames
        self.tail_frames = tail_frames
        self.original_start = _pytime_at_offset(original_start_time, 0, frame_rate)
        self.original_end = _pytime_at_offset(original_start_time, original_duration, frame_rate)

    def log_schedule(self):
        padded = self.original_duration + self.head_frames + self.tail_frames
        print('[Add Black Frames] Frozen top-track cut schedule (pre-extension timecode):')
        print(f'  original_start (+0)        {self.original_start!r}')
        print(
            f'  original_end (+{self.original_duration})     '
            f'{self.original_end!r}'
        )
        print(
            f'  padded duration {padded} = original {self.original_duration} '
            f'+ head {self.head_frames} + tail {self.tail_frames}'
        )


def cut_track_at(track, cut_time, label=''):
    print(f'[Add Black Frames] track.cut({cut_time!r}) [absolute PyTime{label}]')
    track.cut(cut_time)


_RECORD_IN_UNSUPPORTED_TYPES = frozenset({'Gap', 'Video Segment'})


def _segment_has_settable_record_in(segment):
    """Return True only for segment types that support reading and writing record_in.

    Flame prints its own error to stdout before raising an exception when
    record_in is accessed on unsupported types, so we must filter those out
    before ever touching the attribute.
    """
    seg_type = _segment_type_name(segment)
    return seg_type not in _RECORD_IN_UNSUPPORTED_TYPES and not _is_colour_source_segment(segment)


def snapshot_sequence_timecodes(open_seq):
    track_times = []
    for version in open_seq.versions:
        for track in version.tracks:
            track_times.append([
                _safe_record_in(segment)
                for segment in _track_segments(track)
                if _segment_has_settable_record_in(segment)
                and _safe_record_in(segment) is not None
            ])
    return {
        'start_time': open_seq.start_time,
        'track_times': track_times,
    }


def restore_sequence_timecodes(open_seq, state, original_track_count):
    open_seq.start_time = state['start_time']

    track_index = 0
    for version in open_seq.versions:
        for track in version.tracks:
            if track_index >= original_track_count:
                break
            saved_times = state['track_times'][track_index]
            restorable_segments = [
                segment for segment in _track_segments(track)
                if _segment_has_settable_record_in(segment)
                and _safe_record_in(segment) is not None
            ]
            if len(restorable_segments) < len(saved_times):
                track_index += 1
                continue

            offset = len(restorable_segments) - len(saved_times)
            for saved_idx, record_in in enumerate(saved_times):
                if record_in is None:
                    continue
                segment = restorable_segments[offset + saved_idx]
                try:
                    segment.record_in = record_in
                except (AttributeError, RuntimeError) as exc:
                    if 'record_in' not in str(exc).lower():
                        print(
                            f'[Add Black Frames] Could not restore record_in on '
                            f'{_segment_type_name(segment)}: {exc}'
                        )
            track_index += 1


def _first_gap_segment(track):
    for segment in _track_segments(track):
        if _segment_type_name(segment) == 'Gap':
            return segment
    return None


def _set_segment_gap_black(segment):
    if not _is_py_segment(segment):
        raise RuntimeError(
            f'Expected PySegment for set_gap_colour, got {type(segment).__name__}'
        )

    red, green, blue = GAP_BLACK_RGB
    seg_type = _segment_type_name(segment)
    if seg_type != 'Gap' and not _is_colour_source_segment(segment):
        print(
            f'[Add Black Frames] Skipping set_gap_colour on '
            f'{seg_type} segment'
        )
        return

    print(f'[Add Black Frames] segment.set_gap_colour({red}, {green}, {blue})')
    segment.set_gap_colour(red, green, blue)


def _safe_set_current_time(obj, value):
    if value is None:
        return
    try:
        obj.current_time = value
    except (AttributeError, RuntimeError):
        pass


def _extend_sequence_padding(open_seq, head_frames, tail_frames, cut_times, frame_rate):
    """Extend the sequence's padding_start / padding_end to cover head and tail.

    Must be called before version.create_track(-1) so the new Gap spans the
    full padded range. trim_head / trim_tail are no-ops on Gap segments.
    """
    fps = _normalize_frame_rate(frame_rate)
    if head_frames > 0:
        head_tc = _pytime_at_offset(cut_times.original_start, -head_frames, fps)
        print(f'[Add Black Frames] open_seq.padding_start = {head_tc!r}')
        open_seq.padding_start = head_tc

    if tail_frames > 0:
        tail_tc = _pytime_at_offset(cut_times.original_end, tail_frames, fps)
        print(f'[Add Black Frames] open_seq.padding_end = {tail_tc!r}')
        open_seq.padding_end = tail_tc


def setup_top_track_padding(top_track, head_frames, tail_frames, original_duration, cut_times):
    """Top-track padding workflow (sequence padding must already be extended).

    1. set_gap_colour on the full extended Gap (one call, before any cuts)
    2. Cut at original_end then original_start to isolate head / content / tail
    3. Delete the middle segment(s) — the content area is now transparent so
       lower tracks show through; head and tail remain as black Colour Sources

    Colour Sources left by set_gap_colour do not auto-merge when the middle is
    deleted (unlike raw Gap segments), so this ordering is intentional.
    """
    segment = _first_gap_segment(top_track)
    if segment is None:
        raise RuntimeError('Top track has no Gap segment for black padding')

    if head_frames + tail_frames > original_duration:
        raise RuntimeError(
            f'Sequence too short for {head_frames} head + {tail_frames} tail frame(s) '
            f'({original_duration} frames)'
        )

    # Colour the entire extended Gap black before cutting.
    _set_segment_gap_black(segment)

    # Tail cut first so the head cut does not shift the tail boundary.
    if tail_frames > 0:
        cut_track_at(top_track, cut_times.original_end, ', top-track tail start (original_end)')
    if head_frames > 0:
        cut_track_at(top_track, cut_times.original_start, ', top-track head end (original_start)')

    # Delete everything between the head and tail Colour Sources.
    _delete_top_track_middle_segments(top_track, head_frames, tail_frames)

    segments = _track_segments(top_track)
    if not segments:
        raise RuntimeError('Top track has no PySegments after colouring and cutting')
    if head_frames > 0 and tail_frames > 0 and len(segments) < 2:
        raise RuntimeError('Head and tail padding overlap on the top track')


def _delete_top_track_middle_segments(top_track, head_frames, tail_frames):
    """Delete middle segment(s), keeping the head (first) and tail (last)."""
    segments = _track_segments(top_track)

    # Determine which boundary segments to preserve.
    to_delete = list(segments)
    if head_frames > 0 and to_delete:
        to_delete = to_delete[1:]   # keep first (head)
    if tail_frames > 0 and to_delete:
        to_delete = to_delete[:-1]  # keep last (tail)

    for seg in to_delete:
        print(
            f'[Add Black Frames] flame.delete middle '
            f'{_segment_type_name(seg)} '
            f'frames {_segment_start_frame(seg)}-{_segment_end_frame(seg)} '
            f'({_segment_duration_frames(seg)}f)'
        )
        flame.delete(seg)


def add_black_frames_to_sequence(sequence, head_frames, tail_frames):
    name = pyobject_name(sequence)
    if sequence_appears_padded(sequence, head_frames, tail_frames):
        return PaddingResult('skipped', 'Already appears padded', name)

    original_duration = int(sequence.duration.frame)
    original_track_count = len(sequence.versions[-1].tracks)
    frame_rate = sequence.frame_rate
    expected_duration = original_duration + head_frames + tail_frames

    try:
        open_seq = sequence.open_as_sequence()
    except Exception:
        try:
            sequence.open()
            open_seq = sequence
        except Exception as exc:
            return PaddingResult('failed', f'Could not open sequence: {exc}', name)

    ensure_timeline_tab()

    try:
        version = open_seq.versions[-1]
        timecode_state = snapshot_sequence_timecodes(open_seq)

        original_start_time = timecode_state['start_time']
        cut_times = PaddingCutTimes(
            original_start_time, original_duration, head_frames, tail_frames, frame_rate,
        )
        cut_times.log_schedule()

        _extend_sequence_padding(open_seq, head_frames, tail_frames, cut_times, frame_rate)
        top_track = version.create_track(-1)
        setup_top_track_padding(
            top_track, head_frames, tail_frames, original_duration, cut_times,
        )
        restore_sequence_timecodes(open_seq, timecode_state, original_track_count)

        new_duration = int(open_seq.duration.frame)
        new_track_count = len(open_seq.versions[-1].tracks)

        if new_track_count != original_track_count + 1:
            return PaddingResult(
                'failed',
                f'Expected {original_track_count + 1} tracks, found {new_track_count}',
                name,
            )

        if new_duration != expected_duration:
            return PaddingResult(
                'failed',
                f'Expected {expected_duration} frames, found {new_duration}',
                name,
            )

        _safe_set_current_time(open_seq, cut_times.original_start)
        return PaddingResult(
            'success',
            f'+{head_frames} head / +{tail_frames} tail ({original_duration} -> {new_duration} frames)',
            name,
        )
    except Exception as exc:
        message = str(exc)
        if 'Protect' in message or 'protect' in message or 'edit' in message.lower():
            message = (
                f'{message}\n\n'
                'If Protect from Editing is enabled, turn it off in '
                'Preferences -> User -> Media Panel.'
            )
        return PaddingResult('failed', message, name)


def run_batch(selection, head_frames, tail_frames):
    results = []

    for sequence in selection:
        if not isinstance(sequence, flame.PySequence):
            continue
        print(f'[Add Black Frames] Processing: {pyobject_name(sequence)}')
        result = add_black_frames_to_sequence(sequence, head_frames, tail_frames)
        results.append(result)
        print(f'[Add Black Frames] {result.status}: {result.sequence_name} - {result.message}')

    return results


def summarize_results(results):
    success = [r for r in results if r.status == 'success']
    skipped = [r for r in results if r.status == 'skipped']
    failed = [r for r in results if r.status == 'failed']

    console_lines = [
        f'Processed: {len(results)} sequence(s)',
        f'Success: {len(success)}',
        f'Skipped: {len(skipped)}',
        f'Failed: {len(failed)}',
    ]

    if success:
        console_lines.append('')
        console_lines.append('Succeeded:')
        for item in success:
            console_lines.append(f'  - {item.sequence_name}: {item.message}')

    if skipped:
        console_lines.append('')
        console_lines.append('Skipped:')
        for item in skipped:
            console_lines.append(f'  - {item.sequence_name}: {item.message}')

    if failed:
        console_lines.append('')
        console_lines.append('Failed:')
        for item in failed:
            console_lines.append(f'  - {item.sequence_name}: {item.message}')

    flame.messages.show_in_console('\n'.join(console_lines), 'info', 6)

    if failed:
        dialog_message = '\n'.join([
            'One or more sequences failed.',
            '',
            'Failed:',
            *[f'  - {item.sequence_name}: {item.message}' for item in failed],
        ])
        dialog_type = 'warning'
    elif success:
        dialog_message = 'Success.'
        dialog_type = 'info'
    elif skipped:
        dialog_message = 'All selected sequences were skipped (already padded).'
        dialog_type = 'warning'
    else:
        dialog_message = 'No sequences were processed.'
        dialog_type = 'warning'

    flame.messages.show_in_dialog(
        title='Add Black Frames',
        message=dialog_message,
        type=dialog_type,
        buttons=['Ok'],
    )


class BlackFramesWindow(QtWidgets.QWidget):

    def __init__(self, selection, parent=None):
        super().__init__(parent)
        self.selection = selection
        self.head_frames = None
        self.tail_frames = None

        self.setWindowTitle(f'{SCRIPT_NAME} {SCRIPT_VERSION}')
        self.setMinimumWidth(360)
        self.setWindowFlags(
            QtCore.Qt.WindowType.Window
            | QtCore.Qt.WindowType.WindowCloseButtonHint
        )

        self.head_spin = QtWidgets.QSpinBox()
        self.head_spin.setRange(0, MAX_FRAMES)
        self.head_spin.setValue(DEFAULT_HEAD_FRAMES)

        self.tail_spin = QtWidgets.QSpinBox()
        self.tail_spin.setRange(0, MAX_FRAMES)
        self.tail_spin.setValue(DEFAULT_TAIL_FRAMES)

        self.summary_label = QtWidgets.QLabel()
        self.summary_label.setWordWrap(True)
        self._update_summary()

        form = QtWidgets.QFormLayout()
        form.addRow('Head frames', self.head_spin)
        form.addRow('Tail frames', self.tail_spin)
        form.addRow('Duration change', self.summary_label)

        self.head_spin.valueChanged.connect(self._update_summary)
        self.tail_spin.valueChanged.connect(self._update_summary)

        go_btn = QtWidgets.QPushButton('Go')
        cancel_btn = QtWidgets.QPushButton('Cancel')
        go_btn.clicked.connect(self._on_go)
        cancel_btn.clicked.connect(self.close)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_btn)
        buttons.addWidget(go_btn)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(buttons)

    def _update_summary(self):
        total = self.head_spin.value() + self.tail_spin.value()
        count = len([item for item in self.selection if isinstance(item, flame.PySequence)])
        self.summary_label.setText(
            f'+{total} frame(s) per sequence ({count} selected)'
        )

    def _on_go(self):
        head_frames = self.head_spin.value()
        tail_frames = self.tail_spin.value()

        if head_frames == 0 and tail_frames == 0:
            QtWidgets.QMessageBox.warning(
                self,
                SCRIPT_NAME,
                'Head and tail frame counts cannot both be zero.',
            )
            return

        save_config(head_frames, tail_frames)
        self.head_frames = head_frames
        self.tail_frames = tail_frames
        self.close()


def _prompt_head_tail_frames(selection):
    if has_config():
        config = load_config()
        return int(config['head_frames']), int(config['tail_frames'])

    window = BlackFramesWindow(selection)
    window.show()

    app = QtWidgets.QApplication.instance()
    while window.isVisible():
        app.processEvents()

    if window.head_frames is None:
        return None

    return window.head_frames, window.tail_frames


def main_window(selection):
    if flame.get_current_tab() == 'MediaHub':
        flame.set_current_tab('Timeline')

    frame_counts = _prompt_head_tail_frames(selection)
    if frame_counts is None:
        return

    head_frames, tail_frames = frame_counts

    if head_frames == 0 and tail_frames == 0:
        flame.messages.show_in_dialog(
            title=SCRIPT_NAME,
            message='Head and tail frame counts cannot both be zero.',
            type='warning',
            buttons=['Ok'],
        )
        return

    confirm = flame.messages.show_in_dialog(
        title=f'{SCRIPT_NAME} - Confirm',
        message=(
            f'This will modify {len(selection)} sequence(s) in place.\n\n'
            f'Head: {head_frames} frame(s)\n'
            f'Tail: {tail_frames} frame(s)\n\n'
            'Continue?'
        ),
        type='warning',
        buttons=['Continue'],
        cancel_button='Cancel',
    )
    if confirm != 'Continue':
        return

    results = run_batch(selection, head_frames, tail_frames)
    summarize_results(results)


def scope_sequence(selection):
    if not selection:
        return False
    for item in selection:
        if not isinstance(item, flame.PySequence):
            return False
    return True


def get_media_panel_custom_ui_actions():
    return [
        {
            'name': FOLDER_NAME,
            'actions': [
                {
                    'name': SCRIPT_NAME,
                    'isVisible': scope_sequence,
                    'order': 12,
                    "separator": "above",
                    'execute': main_window,
                    'minimumVersion': '2025',
                }
            ],
        }
    ]
