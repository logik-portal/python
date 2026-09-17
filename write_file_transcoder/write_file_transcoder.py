# -*- coding: utf-8 -*-
"""
Script Name: Write File Transcoder
Script Version: 1.0.0
Flame Version: 2026.2
Written by: Huseyin Pasaoglu
Creation Date: 09.15.26
Update Date: 09.16.26

Description:

    Turns every Write File render into a Rec709 review copy, automatically.

    When a Write File render finishes the rendered sequence is converted to an
    H.264 MP4 or a ProRes MOV using real OCIO colour management, reformatted to
    a review canvas and stamped with burn-in - all from a preset, with no
    interaction. The render itself is never touched.

    Colour comes only from the preset (OCIO config, source colour space,
    display, view, optional look). Flame's project colour policy is deliberately
    NOT read, so a preset gives the same result on every machine and every show.

    Reformat: 1920x1080, 3840x2160 or a custom canvas; fit vertically,
    horizontally or fill; per-side crop and an X/Y shift in source pixels; band
    colour. A schematic preview in the settings window shows the layout while
    you type.

    Burn-in: six zones (top/bottom x left/centre/right) with free text and
    tokens - <frame number>, <clip name>, <time code>, <user name>, <date>,
    <time>, <project>, <shot>, <resolution>, <fps>, <frame range>. The text is
    drawn with Qt and composited by ffmpeg, so a specific ffmpeg build is not
    required (many are compiled without drawtext).

    Missing frames are replaced with a black slate reading "MISSING FRAME 1012"
    so duration and timecode stay correct, and a warning is logged. An aborted
    render produces nothing but a log note.

    Jobs run one at a time in a background queue; quitting Flame cancels the
    running job and removes the half-written file. Output is written to a
    .partial file and renamed on success, and an existing file is never
    overwritten - a colliding name gets _repeat, _repeat2 and so on.

    Presets are exportable, so a look can be handed to another artist without
    carrying machine settings such as the ffmpeg path.

    Installation: copy this file to /opt/Autodesk/shared/python/ and refresh
    python hooks, or restart Flame. Nothing else to install.

    Requires ffmpeg and ffprobe on PATH, built with libx264 (for MP4),
    prores_ks (for MOV) and EXR decoding:

        macOS : brew install ffmpeg
        Rocky : dnf install ffmpeg     (needs RPM Fusion)

    If ffmpeg lives somewhere unusual, set the full path in Settings, General
    tab. Everything else ships with Flame. numpy is optional: when Flame's
    Python can import it the colour transform runs about twice as fast, and the
    output is identical either way.

    Tested on Flame 2026.2.2 on macOS. Written to run on Linux as well, but not
    yet tested there.

Menus:

    Flame Main Menu -> Write File Transcoder -> Settings...
    Flame Main Menu -> Write File Transcoder -> Open log
    Right-click a Write File node in Batch -> Write File Transcoder -> Create review...

Updates:

    v1.0.0 09.16.26
    - Initial release.
"""
from __future__ import annotations

import os
import subprocess
import sys
import traceback

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import dataclass, field
from datetime import datetime
import copy
import dataclasses
import json
import os
import queue as _queue
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time
import traceback
import PyOpenColorIO as ocio

try:
    import flame
except Exception:                      # must stay importable outside Flame
    flame = None


SCRIPT_NAME = "Write File Transcoder"
SCRIPT_VERSION = "1.0.0"
VERSION = SCRIPT_VERSION          # kept for the settings window title

# Credit shown in the settings window footer.
SCRIPT = "huseyinpasaoglu"


# ==============================================================================
#  DESIGN NOTES  (read these - they matter in production)
# ------------------------------------------------------------------------------
#  * ALL flame.* calls MUST run on Flame's main (Qt GUI) thread. Everything the
#    hook needs from Flame is read inside the hook itself and copied into the
#    job; the worker thread never touches the Flame API. Notifications go back
#    through flame.schedule_idle_event().
#
#  * ONLY `batch_export_end` is defined. Flame fires eight hooks for a single
#    Write File render, and `batch_export_end` / `batchExportEnd` are two names
#    for the SAME hook - BOTH are called. Defining the camelCase twin as well
#    would queue every job twice. `batch_render_end` is not defined either: it
#    delivers an empty dictionary.
#
#  * `info` has no `aborted` key on a successful render, so the code asks for
#    info.get("aborted", False) rather than testing whether the key exists.
#
#  * The start timecode is NOT in `info`. It comes from the Write File node's
#    `source_timecode`, which is not a plain string - its str() has been seen to
#    include quotes - so it is extracted with a regex and falls back to zero.
#
#  * Flame has no shutdown hook, so the queue is drained from
#    QApplication.aboutToQuit.
#
#  * "Refresh Python Hooks" re-reads hook files but does NOT clear sys.modules.
#    This file is self-contained precisely so a refresh always gets the new
#    code, with no stale package left behind.
#
#  * Scaling happens AFTER the colour transform. ffmpeg's scale filter clips
#    float values to [0,1], which would burn out every highlight if it ran
#    before the output transform. Burn-in in turn happens after scaling, so the
#    text keeps a fixed distance from the canvas edge and can sit over the bands.
#
#  * No temporary image files are written. The pipeline is two ffmpeg processes
#    with Python in between, plus a second pipe carrying the burn-in overlay.
#    Both pipes must be fed concurrently or ffmpeg's overlay filter deadlocks.
# ==============================================================================


# ==========================================================================
#  Module aliases
# ==========================================================================
#  The bundled modules refer to each other by name (`colour.make_processor`,
#  `wc_platform.settings_path`). They all live in this one namespace now, so
#  each of those names is bound to this module and the attribute lookups resolve
#  to the globals defined below.
#
#  These have to be bound BEFORE the module bodies run: a class body such as
#  `fit_mode: str = reformat.FIT_HEIGHT` is executed while the bundle is still
#  being defined.
_self = sys.modules[__name__]
_reformat = _self
burnin = _self
colour = _self
encoder = _self
frames = _self
job = _self
notify = _self
output = _self
pipeline = _self
platform = _self
preset = _self
preview = _self
queue = _self
reformat = _self
sequence = _self
settings = _self
settings_window = _self
wc_colour = _self
wc_output = _self
wc_platform = _self
wc_reformat = _self
wc_sequence = _self
wc_settings = _self


# ==========================================================================
#  reformat
# ==========================================================================
"""
reformat.py - crop, scale and canvas-fitting maths.

Pure maths: no Flame, no ffmpeg, no numpy. Fully unit-testable.

Flow:
    source  --crop-->  cropped  --scale-->  scaled  --place-->  canvas

When placed on the canvas the image may overflow (fill mode, or a shift).
The overflow is cropped; any remaining gap is filled with the band colour.
Both are expressed in a single `Plan` so the ffmpeg filter chain can be
generated directly from it.
"""




FIT_WIDTH = "fit_width"    # fit horizontally -> bands top and bottom
FIT_HEIGHT = "fit_height"  # fit vertically   -> bands left and right
FILL = "fill"              # fill canvas      -> no bands, overflow cropped

FIT_MODES = (FIT_WIDTH, FIT_HEIGHT, FILL)


class ReformatError(ValueError):
    """Invalid reformat settings. The message is shown to the user, so keep it clear."""


@dataclass(frozen=True)
class Rect:
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Plan:
    """The complete description of one frame's journey from source to canvas."""
    source: Rect          # source frame (x, y are always 0)
    crop: Rect            # region taken from the source
    scaled_width: int     # the cropped region after scaling
    scaled_height: int
    visible: Rect         # part of the scaled image that lands ON the canvas
    placement: Rect       # where that part sits on the canvas
    canvas_width: int
    canvas_height: int
    band_colour: str      # colour of the gaps ("black", "#101010", ...)

    @property
    def has_bands(self) -> bool:
        """Is there canvas area not covered by the image?"""
        return (self.placement.x > 0 or self.placement.y > 0
                or self.placement.x + self.placement.width < self.canvas_width
                or self.placement.y + self.placement.height < self.canvas_height)

    @property
    def scale_factor(self) -> float:
        return self.scaled_width / self.crop.width


def build_plan(source_width: int, source_height: int, *,
               canvas_width: int, canvas_height: int,
               fit_mode: str = FIT_HEIGHT,
               crop_left: int = 0, crop_right: int = 0,
               crop_top: int = 0, crop_bottom: int = 0,
               shift_x: int = 0, shift_y: int = 0,
               band_colour: str = "black") -> Plan:
    """Build a Plan from preset settings.

    Crop and shift are given in SOURCE pixels. The shift moves the image
    within the canvas and is scaled up by the same factor as the image.
    """
    if source_width <= 0 or source_height <= 0:
        raise ReformatError("Invalid source resolution: %dx%d"
                            % (source_width, source_height))
    if canvas_width <= 0 or canvas_height <= 0:
        raise ReformatError("Invalid canvas resolution: %dx%d"
                            % (canvas_width, canvas_height))
    if fit_mode not in FIT_MODES:
        raise ReformatError("Unknown fit mode: %r (valid: %s)"
                            % (fit_mode, ", ".join(FIT_MODES)))
    for label, value in (("left", crop_left), ("right", crop_right),
                         ("top", crop_top), ("bottom", crop_bottom)):
        if value < 0:
            raise ReformatError("Crop cannot be negative (%s: %d)" % (label, value))

    crop_w = source_width - crop_left - crop_right
    crop_h = source_height - crop_top - crop_bottom
    if crop_w <= 0 or crop_h <= 0:
        # 3.4: if the crop is larger than the source, the job must not start.
        raise ReformatError(
            "Crop is larger than the source: %dx%d minus left %d + right %d, "
            "top %d + bottom %d leaves %dx%d."
            % (source_width, source_height, crop_left, crop_right,
               crop_top, crop_bottom, crop_w, crop_h))

    crop = Rect(crop_left, crop_top, crop_w, crop_h)

    if fit_mode == FIT_WIDTH:
        scale = canvas_width / crop_w
    elif fit_mode == FIT_HEIGHT:
        scale = canvas_height / crop_h
    else:
        scale = max(canvas_width / crop_w, canvas_height / crop_h)

    scaled_w = max(1, round(crop_w * scale))
    scaled_h = max(1, round(crop_h * scale))

    # Centre first, then shift. The shift is given in source pixels, so it is
    # scaled by the same factor as the image.
    px = round((canvas_width - scaled_w) / 2 + shift_x * scale)
    py = round((canvas_height - scaled_h) / 2 + shift_y * scale)

    # The part of the scaled image that lands on the canvas.
    vx0, vy0 = max(0, px), max(0, py)
    vx1 = min(canvas_width, px + scaled_w)
    vy1 = min(canvas_height, py + scaled_h)
    if vx0 >= vx1 or vy0 >= vy1:
        raise ReformatError(
            "The shift moves the image entirely off the canvas "
            "(x %d, y %d). Canvas %dx%d, image %dx%d."
            % (shift_x, shift_y, canvas_width, canvas_height, scaled_w, scaled_h))

    visible = Rect(vx0 - px, vy0 - py, vx1 - vx0, vy1 - vy0)
    placement = Rect(vx0, vy0, vx1 - vx0, vy1 - vy0)

    return Plan(source=Rect(0, 0, source_width, source_height),
                crop=crop, scaled_width=scaled_w, scaled_height=scaled_h,
                visible=visible, placement=placement,
                canvas_width=canvas_width, canvas_height=canvas_height,
                band_colour=band_colour)


def to_ffmpeg_filters(plan: Plan, scale_flags: str = "lanczos") -> list:
    """Turn a Plan into an ffmpeg filter chain.

    Redundant steps are skipped: no `crop` when nothing is cropped, no `scale`
    at 1:1, no `pad` when there are no bands.
    """
    filters = []

    c = plan.crop
    if (c.x, c.y, c.width, c.height) != (0, 0, plan.source.width, plan.source.height):
        filters.append("crop=%d:%d:%d:%d" % (c.width, c.height, c.x, c.y))

    if (plan.scaled_width, plan.scaled_height) != (c.width, c.height):
        filters.append("scale=%d:%d:flags=%s"
                       % (plan.scaled_width, plan.scaled_height, scale_flags))

    v = plan.visible
    if (v.x, v.y, v.width, v.height) != (0, 0, plan.scaled_width, plan.scaled_height):
        filters.append("crop=%d:%d:%d:%d" % (v.width, v.height, v.x, v.y))

    p = plan.placement
    if (p.width, p.height) != (plan.canvas_width, plan.canvas_height):
        filters.append("pad=%d:%d:%d:%d:%s"
                       % (plan.canvas_width, plan.canvas_height,
                          p.x, p.y, plan.band_colour))

    return filters

# ==========================================================================
#  sequence
# ==========================================================================
"""
sequence.py - image sequence scanning and missing-frame detection.

Flame's `resolvedPath` carries a range as `[1001-1005]` while the files
on disk are named `Batch1001.exr`. This module understands both.
"""




IMAGE_EXTENSIONS = (".exr", ".dpx", ".tif", ".tiff", ".png", ".jpg", ".jpeg")

# Flame's resolvedPath form:  /path/Name[1001-1005].exr
RANGE_RE = re.compile(r"^(?P<base>.*?)\[(?P<first>\d+)-(?P<last>\d+)\](?P<ext>\.\w+)$")

# A single frame on disk:  Name1001.exr  /  Name.1001.exr  /  Name_1001.exr
FRAME_RE = re.compile(r"^(?P<base>.*?)(?P<num>\d+)(?P<ext>\.\w+)$")


class SequenceError(ValueError):
    """The sequence could not be resolved."""


@dataclass
class Sequence:
    directory: str
    base: str              # the part before the frame number ("render", "comp_v003.")
    extension: str         # ".exr"
    padding: int           # 4  ->  %04d
    frames: list           # existing frame numbers, sorted
    missing: list = field(default_factory=list)

    @property
    def first(self) -> int:
        return self.frames[0]

    @property
    def last(self) -> int:
        return self.frames[-1]

    @property
    def expected_count(self) -> int:
        """Frames that should exist from first to last, gaps included."""
        return self.last - self.first + 1

    @property
    def is_complete(self) -> bool:
        return not self.missing

    @property
    def ffmpeg_pattern(self) -> str:
        """Pattern for ffmpeg's image2 demuxer: /path/Batch%04d.exr"""
        return os.path.join(self.directory,
                            "%s%%0%dd%s" % (self.base, self.padding, self.extension))

    def path_for(self, frame: int) -> str:
        return os.path.join(
            self.directory,
            "%s%s%s" % (self.base, str(frame).zfill(self.padding), self.extension))

    @property
    def clip_name(self) -> str:
        """The `<clip name>` burn-in token: file name without frame number and extension."""
        return self.base.rstrip("._-") or os.path.basename(self.directory)

    @property
    def frame_range_label(self) -> str:
        """The `<frame range>` burn-in token: '1001-1240'."""
        return "%d-%d" % (self.first, self.last)


def parse_resolved_path(resolved_path: str):
    """Split Flame's `.../Name[1001-1005].exr` into (dir, base, first, last, ext).

    Returns None when there is no range, so the caller can scan the directory
    instead.
    """
    m = RANGE_RE.match(resolved_path)
    if not m:
        return None
    directory = os.path.dirname(resolved_path)
    return (directory, os.path.basename(m.group("base")),
            int(m.group("first")), int(m.group("last")), m.group("ext"))


def scan(directory: str, base: str = None, extension: str = None) -> Sequence:
    """Scan a directory and return a Sequence.

    Without `base`/`extension` the largest sequence in the directory wins. A
    Write File output directory normally holds a single sequence, but other
    files may have landed next to it.
    """
    if not os.path.isdir(directory):
        raise SequenceError("No such directory: %s" % directory)

    groups = {}
    for name in os.listdir(directory):
        ext = os.path.splitext(name)[1].lower()
        if ext not in IMAGE_EXTENSIONS:
            continue
        m = FRAME_RE.match(name)
        if not m:
            continue
        key = (m.group("base"), m.group("ext"), len(m.group("num")))
        groups.setdefault(key, []).append(int(m.group("num")))

    if base is not None:
        groups = {k: v for k, v in groups.items() if k[0] == base}
    if extension is not None:
        groups = {k: v for k, v in groups.items() if k[1].lower() == extension.lower()}

    if not groups:
        raise SequenceError("No image sequence found in %s" % directory)

    (sel_base, sel_ext, sel_pad), numbers = max(groups.items(),
                                                key=lambda kv: len(kv[1]))
    numbers.sort()
    missing = [n for n in range(numbers[0], numbers[-1] + 1) if n not in set(numbers)]

    return Sequence(directory=directory, base=sel_base, extension=sel_ext,
                    padding=sel_pad, frames=numbers, missing=missing)


def scan_for_job(resolved_path: str) -> Sequence:
    """Scan the disk starting from Flame's resolvedPath and compare against it.

    Frames inside the range the hook reported but absent from disk are recorded
    as missing - the render may have been aborted, or a frame failed to write.
    """
    parsed = parse_resolved_path(resolved_path)
    if parsed is None:
        return scan(os.path.dirname(resolved_path))

    directory, base, first, last, ext = parsed
    seq = scan(directory, base=base, extension=ext)

    have = set(seq.frames)
    expected = set(range(first, last + 1))
    seq.missing = sorted(expected - have)
    # Frames outside the range reported by the hook are ignored.
    seq.frames = sorted(have & expected) or seq.frames
    return seq

# ==========================================================================
#  output
# ==========================================================================
"""
output.py - output path template and collision numbering.

Rules:
  * Template tokens: {source_dir}, {source_name}
  * The extension comes from the format and is never written in the template.
  * On a name collision: `_repeat`, then `_repeat2`, `_repeat3`, ...
    NO file is ever deleted or overwritten.
  * Writes are atomic: `.partial` first, renamed when the job finishes.
"""




DEFAULT_TEMPLATE = "{source_dir}/../_review/{source_name}"


class OutputError(ValueError):
    """The output path could not be produced."""


def resolve_template(template: str, source_dir: str, source_name: str,
                     extension: str) -> str:
    """Resolve the template and append the extension. Does not touch the disk."""
    if not template or not template.strip():
        raise OutputError("The output path template is empty.")
    try:
        path = template.format(source_dir=source_dir, source_name=source_name)
    except KeyError as exc:
        raise OutputError(
            "Unknown token in template: %s. Valid tokens: "
            "{source_dir}, {source_name}" % exc) from exc
    except (IndexError, ValueError) as exc:
        raise OutputError("Could not resolve template: %s" % exc) from exc

    if not extension.startswith("."):
        extension = "." + extension
    return os.path.normpath(os.path.expanduser(path)) + extension


def unique_path(path: str, _exists=os.path.exists) -> str:
    """Append `_repeat`, `_repeat2`, ... on collision.

    `_exists` is injectable for tests only.
    """
    if not _exists(path):
        return path

    stem, ext = os.path.splitext(path)
    candidate = "%s_repeat%s" % (stem, ext)
    if not _exists(candidate):
        return candidate

    n = 2
    while True:
        candidate = "%s_repeat%d%s" % (stem, n, ext)
        if not _exists(candidate):
            return candidate
        n += 1
        if n > 9999:                       # guard against an endless loop
            raise OutputError("Too many collisions: %s" % path)


def partial_path(final_path: str) -> str:
    """Temporary name used until the job finishes. Same directory, so the rename is atomic."""
    return final_path + ".partial"


def prepare(template: str, source_dir: str, source_name: str,
            extension: str, create_dirs: bool = True) -> tuple:
    """Return (final_path, partial_path), creating the target directory if needed."""
    path = unique_path(resolve_template(template, source_dir, source_name, extension))
    if create_dirs:
        folder = os.path.dirname(path)
        if folder and not os.path.isdir(folder):
            os.makedirs(folder, exist_ok=True)
    return path, partial_path(path)


def finalise(partial: str, final_path: str) -> str:
    """Move the `.partial` file to its final name.

    Something else may have claimed the same name while the job ran, so the name
    is made unique again. `os.rename`, not `os.replace`: never overwrite.
    """
    if not os.path.exists(partial):
        raise OutputError("Temporary file not found: %s" % partial)
    target = unique_path(final_path)
    os.rename(partial, target)
    return target


def cleanup(partial: str) -> None:
    """Remove a half-written file after a cancel or a failure. Fails silently."""
    try:
        if partial and os.path.exists(partial):
            os.remove(partial)
    except OSError:
        pass

# ==========================================================================
#  platform
# ==========================================================================
"""
platform.py - macOS / Linux (Rocky) differences.

Kept in one place so no other module has to look at `sys.platform`.
"""




IS_MACOS = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

APP_NAME = "WriteConvert"


def config_dir() -> str:
    """Directory holding the settings file. Machine-local, never exported."""
    if IS_MACOS:
        return os.path.expanduser("~/Library/Preferences/%s" % APP_NAME)
    return os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")), APP_NAME)


def settings_path() -> str:
    return os.path.join(config_dir(), "settings.json")


def default_log_dir() -> str:
    if IS_MACOS:
        return os.path.expanduser("~/Library/Logs/%s" % APP_NAME)
    return os.path.join(
        os.environ.get("XDG_STATE_HOME", os.path.expanduser("~/.local/state")),
        APP_NAME)


def find_tool(name: str, configured: str = "") -> str:
    """Try the configured path, then PATH, then well-known install locations.

    Flame runs with its own environment, so PATH is not necessarily the one from
    the user's shell; that is why the usual install locations are scanned too.
    """
    if configured:
        expanded = os.path.expanduser(configured)
        if os.path.isfile(expanded) and os.access(expanded, os.X_OK):
            return expanded
        if os.path.sep not in configured:
            found = shutil.which(configured)
            if found:
                return found

    found = shutil.which(name)
    if found:
        return found

    candidates = ["/opt/homebrew/bin", "/usr/local/bin", "/usr/bin", "/bin"]
    for folder in candidates:
        path = os.path.join(folder, name)
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return name                       # last resort: let PATH fail with a clear error


def default_ocio_config() -> str:
    """Built-in ACES config. Ships with PyOpenColorIO, so nothing to download."""
    return "studio-config-v2.2.0_aces-v1.3_ocio-v2.4"

# ==========================================================================
#  burnin
# ==========================================================================
"""
burnin.py - six-zone burn-in, token resolution and text rendering with Qt.

WHY NOT ffmpeg drawtext
-----------------------
The original design left burn-in to ffmpeg's `drawtext` filter. On
2026-09-15 it turned out the ffmpeg on this machine is built without
libfreetype, so `drawtext` does not exist. Requiring a specific ffmpeg build on
every machine of a mixed macOS/Linux fleet is fragile.

PySide6, on the other hand, ships with Flame on both platforms. Drawing
the text ourselves means:
  * no dependency on ffmpeg build options
  * real font metrics, so alignment and box padding are exact
  * burn-in can sit at a fixed distance from the canvas edge, over the bands

Text is drawn at CANVAS resolution, AFTER scaling; otherwise it would shrink
with the image and could not extend over the bands.

The overlay is handed to ffmpeg as an RGBA stream and composited by its
`overlay` filter. Doing the blend here instead would mean a per-pixel pass in
Python, which is exactly what needs numpy - and avoiding numpy is what lets the
tool ship as a single drop-in file.
"""





# Outside Flame (CLI, tests) Qt must run headless when there is no display.
# INSIDE Flame a QApplication already exists and overriding the platform would
# make the settings window invisible, so we only switch to offscreen when no Qt
# application is running.
def _ensure_offscreen_if_headless() -> None:
    if os.environ.get("QT_QPA_PLATFORM"):
        return
    try:
        from PySide6 import QtCore
        if QtCore.QCoreApplication.instance() is not None:
            return                      # we are inside Flame, leave it alone
    except Exception:
        pass
    os.environ["QT_QPA_PLATFORM"] = "offscreen"


_ensure_offscreen_if_headless()

from PySide6 import QtGui  # noqa: E402


TOP_LEFT = "top_left"
TOP_CENTRE = "top_centre"
TOP_RIGHT = "top_right"
BOTTOM_LEFT = "bottom_left"
BOTTOM_CENTRE = "bottom_centre"
BOTTOM_RIGHT = "bottom_right"

ZONES = (TOP_LEFT, TOP_CENTRE, TOP_RIGHT,
         BOTTOM_LEFT, BOTTOM_CENTRE, BOTTOM_RIGHT)

# Tokens that change every frame. If any is present the overlay is redrawn per
# frame; otherwise it is drawn once and reused.
DYNAMIC_TOKENS = ("<frame number>", "<time code>")

TOKEN_RE = re.compile(r"<[^<>]+>")

# Font families in priority order. The first one present is used.
FONT_CANDIDATES = ("Helvetica Neue", "Helvetica", "Arial",
                   "DejaVu Sans", "Liberation Sans", "Noto Sans")


class BurnInError(ValueError):
    pass


# ---------------------------------------------------------------------------
#  Timecode
# ---------------------------------------------------------------------------
# Accepts 00:00:00:00, 1:2:3:4, 00:00:00;00 and anything wrapped in quotes or
# other text - Flame's `source_timecode` arrives as an object whose str() can
# include quotes (observed: "'00:00:00:00'").
TC_RE = re.compile(r"(\d{1,3})\s*:\s*(\d{1,2})\s*:\s*(\d{1,2})\s*[:;]\s*(\d{1,3})")

DEFAULT_TIMECODE = "00:00:00:00"


def normalise_timecode(value, default: str = DEFAULT_TIMECODE) -> str:
    """Pull a HH:MM:SS:FF timecode out of whatever Flame handed us.

    Never raises: an unusable value falls back to `default`, because a burn-in
    detail must not stop a render.
    """
    if value is None:
        return default
    match = TC_RE.search(str(value))
    if not match:
        return default
    h, m, s, f = (int(g) for g in match.groups())
    if m > 59 or s > 59:
        return default
    return "%02d:%02d:%02d:%02d" % (h, m, s, f)


def tc_to_frames(tc: str, fps: int) -> int:
    """'01:00:00:12' -> frame count. Non-drop is assumed."""
    parts = str(tc).strip().strip("'\"").replace(";", ":").split(":")
    if len(parts) != 4:
        raise BurnInError("Timecode must be HH:MM:SS:FF, got: %r" % tc)
    try:
        h, m, s, f = (int(p) for p in parts)
    except ValueError as exc:
        raise BurnInError("Timecode is not numeric: %r" % tc) from exc
    return ((h * 60 + m) * 60 + s) * fps + f


def frames_to_tc(frames: int, fps: int) -> str:
    """Frame count -> 'HH:MM:SS:FF'. Wraps after 24 hours."""
    if fps <= 0:
        raise BurnInError("fps must be positive, got: %r" % fps)
    frames = max(0, int(frames))
    f = frames % fps
    total_s = frames // fps
    s, m, h = total_s % 60, (total_s // 60) % 60, (total_s // 3600) % 24
    return "%02d:%02d:%02d:%02d" % (h, m, s, f)


# ---------------------------------------------------------------------------
#  Settings and context
# ---------------------------------------------------------------------------
@dataclass
class BurnInSettings:
    """Burn-in settings stored in the preset."""
    zones: dict = field(default_factory=dict)      # zone -> free text
    font_size_pct: float = 2.5                    # percentage of canvas height
    margin_pct: float = 2.0                       # distance from the canvas edge
    box: bool = True                              # semi-transparent background box
    box_opacity: float = 0.5
    colour: str = "#FFFFFF"

    @property
    def is_empty(self) -> bool:
        return not any((self.zones.get(z) or "").strip() for z in ZONES)

    @property
    def is_dynamic(self) -> bool:
        """Does any zone contain a token that changes per frame?"""
        text = " ".join((self.zones.get(z) or "") for z in ZONES)
        return any(tok in text for tok in DYNAMIC_TOKENS)


@dataclass
class JobContext:
    """Values needed to resolve tokens; constant for the whole job."""
    clip_name: str = ""
    project: str = ""
    shot: str = ""
    user: str = ""
    fps: int = 25
    start_timecode: str = "00:00:00:00"
    first_frame: int = 1001
    frame_range: str = ""
    canvas_width: int = 1920
    canvas_height: int = 1080
    started_at: datetime = field(default_factory=datetime.now)


def resolve_tokens(text: str, ctx: JobContext, frame_number: int) -> str:
    """Resolve the tokens in one zone. Unknown tokens are left untouched."""
    if not text:
        return ""

    offset = frame_number - ctx.first_frame
    try:
        timecode = frames_to_tc(
            tc_to_frames(ctx.start_timecode, ctx.fps) + offset, ctx.fps)
    except BurnInError:
        # A bad timecode must never stop a render; fall back to counting from zero.
        timecode = frames_to_tc(
            tc_to_frames(DEFAULT_TIMECODE, ctx.fps) + offset, ctx.fps)

    values = {
        "<frame number>": str(frame_number),
        "<clip name>": ctx.clip_name,
        "<time code>": timecode,
        "<user name>": ctx.user,
        "<date>": ctx.started_at.strftime("%Y-%m-%d"),
        "<time>": ctx.started_at.strftime("%H:%M"),
        "<project>": ctx.project,
        "<shot>": ctx.shot,
        "<resolution>": "%dx%d" % (ctx.canvas_width, ctx.canvas_height),
        "<fps>": str(ctx.fps),
        "<frame range>": ctx.frame_range,
    }
    return TOKEN_RE.sub(lambda m: values.get(m.group(0), m.group(0)), text)


def known_tokens() -> tuple:
    """Used by the token helper in the settings window."""
    return ("<frame number>", "<clip name>", "<time code>", "<user name>",
            "<date>", "<time>", "<project>", "<shot>", "<resolution>",
            "<fps>", "<frame range>")


# ---------------------------------------------------------------------------
#  Drawing
# ---------------------------------------------------------------------------
def _ensure_qt_app():
    """Create a QGuiApplication if there is none. Inside Flame one always exists."""
    app = QtGui.QGuiApplication.instance()
    if app is None:
        app = QtGui.QGuiApplication([])
    return app


def _pick_font_family() -> str:
    """Pick the first candidate family present. The 'Sans Serif' alias is slow."""
    available = set(QtGui.QFontDatabase.families())
    for name in FONT_CANDIDATES:
        if name in available:
            return name
    return available and sorted(available)[0] or "Helvetica"


class BurnInRenderer:
    """Produces a canvas-sized RGBA overlay and composites it onto a frame.

    For static burn-in the overlay is drawn once. With a dynamic token it is
    redrawn every frame - a few milliseconds for six short strings.
    """

    def __init__(self, settings: BurnInSettings, ctx: JobContext):
        self.settings = settings
        self.ctx = ctx
        # Normalise once here so a malformed timecode cannot fail the render
        # frame after frame.
        self.timecode_fallback = (
            normalise_timecode(ctx.start_timecode) != str(ctx.start_timecode).strip())
        ctx.start_timecode = normalise_timecode(ctx.start_timecode)
        self.width = ctx.canvas_width
        self.height = ctx.canvas_height
        self._cache = None

        _ensure_qt_app()
        self.font = QtGui.QFont(_pick_font_family())
        self.font.setPixelSize(max(8, round(self.height * settings.font_size_pct / 100)))
        self.margin = max(2, round(self.height * settings.margin_pct / 100))
        self.metrics = QtGui.QFontMetrics(self.font)

    # -- placement --------------------------------------------------------
    def _zone_origin(self, zone: str, text_width: int) -> tuple:
        """Top-left corner of a zone. Burn-in always sits a fixed distance from
        the CANVAS edge; the presence of bands does not move it."""
        h = self.metrics.height()
        if zone.endswith("left"):
            x = self.margin
        elif zone.endswith("centre"):
            x = (self.width - text_width) // 2
        else:
            x = self.width - text_width - self.margin

        y = self.margin if zone.startswith("top") else self.height - h - self.margin
        return x, y

    # -- drawing ----------------------------------------------------------
    def _draw(self, frame_number: int) -> QtGui.QImage:
        img = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_RGBA8888)
        img.fill(QtGui.QColor(0, 0, 0, 0))

        painter = QtGui.QPainter(img)
        try:
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            painter.setFont(self.font)
            colour = QtGui.QColor(self.settings.colour)
            pad = max(2, self.metrics.height() // 5)

            for zone in ZONES:
                text = resolve_tokens(self.settings.zones.get(zone, ""),
                                      self.ctx, frame_number)
                if not text.strip():
                    continue
                tw = self.metrics.horizontalAdvance(text)
                x, y = self._zone_origin(zone, tw)

                if self.settings.box:
                    box = QtGui.QColor(0, 0, 0)
                    box.setAlphaF(max(0.0, min(1.0, self.settings.box_opacity)))
                    painter.fillRect(x - pad, y, tw + 2 * pad,
                                     self.metrics.height(), box)

                painter.setPen(colour)
                painter.drawText(x, y + self.metrics.ascent(), text)
        finally:
            painter.end()
        return img

    @staticmethod
    def _to_rgba_bytes(img) -> bytes:
        """QImage -> tightly packed RGBA rows.

        `bytesPerLine` can include padding, which ffmpeg would read as image
        data and shear the overlay, so short rows are trimmed.
        """
        width, height = img.width(), img.height()
        stride = img.bytesPerLine()
        raw = bytes(img.constBits())
        if stride == width * 4:
            return raw
        return b"".join(raw[y * stride:y * stride + width * 4]
                        for y in range(height))

    def overlay(self, frame_number: int) -> bytes:
        """RGBA bytes for one frame, canvas sized."""
        if self.settings.is_dynamic:
            return self._to_rgba_bytes(self._draw(frame_number))
        if self._cache is None:
            self._cache = self._to_rgba_bytes(self._draw(frame_number))
        return self._cache


class SlateRenderer:
    """Centred warning text for missing frames.

    A frame absent from the source passes through black; 'MISSING FRAME 1012' is
    drawn over it. Duration and timecode are preserved because the frame still
    occupies its place in the stream.
    """

    def __init__(self, canvas_width: int, canvas_height: int,
                 font_size_pct: float = 4.0, colour: str = "#FF4040"):
        _ensure_qt_app()
        self.width = canvas_width
        self.height = canvas_height
        self.font = QtGui.QFont(_pick_font_family())
        self.font.setPixelSize(max(10, round(canvas_height * font_size_pct / 100)))
        self.metrics = QtGui.QFontMetrics(self.font)
        self.colour = colour

    def overlay(self, frame_number: int) -> bytes:
        img = QtGui.QImage(self.width, self.height, QtGui.QImage.Format_RGBA8888)
        img.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter(img)
        try:
            painter.setRenderHint(QtGui.QPainter.TextAntialiasing, True)
            painter.setFont(self.font)
            painter.setPen(QtGui.QColor(self.colour))
            text = "MISSING FRAME %d" % frame_number
            tw = self.metrics.horizontalAdvance(text)
            painter.drawText((self.width - tw) // 2,
                             (self.height + self.metrics.ascent()) // 2, text)
        finally:
            painter.end()
        return BurnInRenderer._to_rgba_bytes(img)


class OverlayStream:
    """Feeds ffmpeg one RGBA frame for every frame of the job.

    Burn-in and the missing-frame slate are the same thing to ffmpeg: a
    canvas-sized RGBA image laid over the picture. Combining them here keeps the
    encoder to a single overlay input.
    """

    def __init__(self, settings: BurnInSettings, ctx: JobContext, missing=()):
        self.missing = set(missing)
        self.width = ctx.canvas_width
        self.height = ctx.canvas_height
        self.burn = BurnInRenderer(settings, ctx)
        self.slate = SlateRenderer(ctx.canvas_width, ctx.canvas_height) if missing else None
        self._empty = None

    @property
    def needed(self) -> bool:
        """No burn-in and no missing frames means no overlay input at all."""
        return bool(self.missing) or not self.burn.settings.is_empty

    def frame(self, frame_number: int) -> bytes:
        if frame_number in self.missing:
            return self.slate.overlay(frame_number)
        if self.burn.settings.is_empty:
            if self._empty is None:
                self._empty = bytes(self.width * self.height * 4)
            return self._empty
        return self.burn.overlay(frame_number)

# ==========================================================================
#  colour
# ==========================================================================
"""
colour.py - OCIO config resolution and multi-threaded colour transform.

Colour space / display / view names are NEVER hardcoded; they change between
config versions, so they are validated at runtime and the error message lists
what is actually available.

No numpy: OCIO reads and writes the frame buffer directly through the buffer
protocol, so a plain `bytearray` is enough. Removing numpy is what makes the
tool a drop-in file with no installation step.
"""





class ColourError(ValueError):
    """Colour settings could not be resolved. The message is shown to the user."""


def builtin_config_names() -> list:
    # Each registry entry carries (name, ui name, description, recommended);
    # only the first field is needed.
    return [entry[0] for entry in ocio.BuiltinConfigRegistry().getBuiltinConfigs()]


def load_config(spec: str):
    """Accepts a built-in config name or a path to a .ocio file."""
    if not spec:
        raise ColourError("No OCIO config specified.")
    if spec in builtin_config_names():
        return ocio.Config.CreateFromBuiltinConfig(spec)
    path = os.path.expanduser(spec)
    if os.path.isfile(path):
        try:
            return ocio.Config.CreateFromFile(path)
        except Exception as exc:
            raise ColourError("Could not read OCIO config (%s): %s" % (path, exc)) from exc
    raise ColourError(
        "OCIO config not found: %r\nBuilt-in options:\n  %s"
        % (spec, "\n  ".join(builtin_config_names())))


def config_for_platform(macos_spec: str, linux_spec: str) -> str:
    """The preset holds one OCIO path per OS; pick the right one."""
    spec = macos_spec if sys.platform == "darwin" else linux_spec
    if not spec:
        other = "Linux" if sys.platform == "darwin" else "macOS"
        raise ColourError(
            "The OCIO config path is empty for this platform. Only the %s "
            "field is filled in this preset." % other)
    return spec


def make_processor(config_spec: str, source: str, display: str, view: str,
                   look: str = ""):
    """Return (config, CPUProcessor). Invalid names raise with the valid ones listed."""
    cfg = load_config(config_spec)

    names = [cs.getName() for cs in cfg.getColorSpaces()]
    aliases = set(names)
    for cs in cfg.getColorSpaces():
        aliases.update(cs.getAliases())
    if source not in aliases:
        raise ColourError("Source colour space not in config: %r\nAvailable:\n  %s"
                          % (source, "\n  ".join(sorted(names))))

    displays = list(cfg.getDisplays())
    if display not in displays:
        raise ColourError("Display not in config: %r\nAvailable:\n  %s"
                          % (display, "\n  ".join(displays)))

    views = list(cfg.getViews(display))
    if view not in views:
        raise ColourError("View not available on display '%s': %r\nAvailable:\n  %s"
                          % (display, view, "\n  ".join(views)))

    dvt = ocio.DisplayViewTransform(src=source, display=display, view=view)
    group = ocio.GroupTransform()
    if look:
        lt = ocio.LookTransform()
        lt.setSrc(source)
        lt.setDst(source)
        lt.setLooks(look)
        group.appendTransform(lt)
    group.appendTransform(dvt)

    try:
        processor = cfg.getProcessor(group, ocio.TRANSFORM_DIR_FORWARD)
    except Exception as exc:
        raise ColourError("Could not build the colour transform: %s" % exc) from exc

    return cfg, processor.getDefaultCPUProcessor()


def measure_grey(cpu, value: float = 0.18) -> float:
    """Value of neutral grey after the transform. This number proves the chain.

    ACES 1.3 / Rec.709 ODT -> 0.3895 (verified reference, 4.5.1)
    """
    import struct
    patch = bytearray(struct.pack("<f", value) * 3)
    view = memoryview(patch).cast("f")
    # applyRGB, not PackedImageDesc: the ImageDesc classes need numpy, applyRGB
    # does not, and this check has to work on the portable path too.
    cpu.applyRGB(view)
    return float(view[0])


class BandedProcessor:
    """Split the frame into horizontal bands and apply OCIO in parallel .

    OCIO is single-threaded; `apply()` releases the GIL on the C++ side, so the
    threads really do run in parallel. Measured speed-up: about 15x on 16 threads.

    The descriptors point into the same buffer, so they are built ONCE and reused
    for every frame. Band slices of a planar buffer are contiguous, so nothing is
    copied.

    `buffer` is a bytearray holding one planar float32 frame in G, B, R order -
    exactly what ffmpeg's `gbrpf32le` produces.
    """

    def __init__(self, cpu, buffer: bytearray, width: int, height: int,
                 threads: int = 0):
        expected = width * height * 3 * 4
        if len(buffer) != expected:
            raise ColourError("Buffer is %d bytes, expected %d for %dx%d float32 RGB"
                              % (len(buffer), expected, width, height))

        self.cpu = cpu
        self.threads = max(1, threads or min(16, os.cpu_count() or 4))
        self.threads = min(self.threads, height)

        floats = memoryview(buffer).cast("f")
        plane = width * height
        rows = (height + self.threads - 1) // self.threads

        self.bands = []
        for i in range(self.threads):
            first, last = i * rows, min((i + 1) * rows, height)
            if first >= last:
                break
            start, stop = first * width, last * width
            # OCIO wants R, G, B; the buffer is gbrp, so plane 2, 0, 1.
            self.bands.append(ocio.PlanarImageDesc(
                floats[2 * plane + start:2 * plane + stop],
                floats[start:stop],
                floats[plane + start:plane + stop],
                width, last - first))

        self._pool = ThreadPoolExecutor(len(self.bands),
                                        thread_name_prefix="wc-ocio")

    def apply(self) -> None:
        """Transform the buffer in place."""
        list(self._pool.map(self.cpu.apply, self.bands))

    def close(self) -> None:
        self._pool.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

# ==========================================================================
#  frames
# ==========================================================================
"""
frames.py - the frame buffer, with and without numpy.

Colour transforms on a whole frame go through OCIO, whose Python bindings take
the pixels either as a numpy array or as a plain buffer. numpy is faster but it
ships compiled binaries, so requiring it means an installation step. Both paths
exist here and the faster one is used when it is available:

    numpy present : PlanarImageDesc straight onto the planar buffer ffmpeg gives
                    us. No conversion at all.
    numpy absent  : the planar buffer is interleaved with one strided memoryview
                    copy (done in C, not a Python loop) and handed to applyRGB.

Both produce identical pixels; the difference is speed. Measured on 4096x3024:

    numpy    : 0.04 s per frame (16 threads)
    no numpy : 0.06 s OCIO + 0.26 s interleave

so the no-numpy path is roughly twice as slow end to end. That is the price of
dropping a single file into the hook directory and being done.

IMPORTANT: `PlanarImageDesc` and `PackedImageDesc` BOTH require numpy - only
`applyRGB` works without it. That is why the fallback interleaves.
"""




try:
    import numpy as _np
except ImportError:                       # the drop-in case
    _np = None


HAVE_NUMPY = _np is not None

# What ffmpeg should be told the Python stage is sending it.
PIX_FMT_PLANAR = "gbrpf32le"      # numpy path: unchanged planar layout
PIX_FMT_PACKED = "rgbf32le"       # fallback: interleaved, an ffmpeg INPUT format


class FrameError(ValueError):
    pass


class FrameBuffer:
    """One frame of planar float32 RGB, plus the OCIO plumbing for it.

    ffmpeg always hands us `gbrpf32le`: three planes in G, B, R order. What we
    send back depends on the path, so `pix_fmt` says which.
    """

    def __init__(self, cpu, width: int, height: int, threads: int = 0):
        self.cpu = cpu
        self.width = width
        self.height = height
        self.pixels = width * height
        self.nbytes = self.pixels * 3 * 4

        self.threads = max(1, threads or min(16, os.cpu_count() or 4))
        self.threads = min(self.threads, height)

        self.planar = bytearray(self.nbytes)
        self.view = memoryview(self.planar)

        if HAVE_NUMPY:
            self._setup_numpy()
        else:
            self._setup_plain()

        self._pool = ThreadPoolExecutor(len(self._bands),
                                        thread_name_prefix="wc-ocio")

    # -- the two paths -----------------------------------------------------
    def _rows(self):
        step = (self.height + self.threads - 1) // self.threads
        for i in range(self.threads):
            first, last = i * step, min((i + 1) * step, self.height)
            if first >= last:
                return
            yield first, last

    def _setup_numpy(self) -> None:
        self.pix_fmt = PIX_FMT_PLANAR
        array = _np.frombuffer(self.planar, dtype="<f4").reshape(
            3, self.height, self.width)
        self._array = array
        self._bands = [
            ocio.PlanarImageDesc(array[2][a:b], array[0][a:b], array[1][a:b],
                                 self.width, b - a)
            for a, b in self._rows()]
        self._apply = self.cpu.apply

    def _setup_plain(self) -> None:
        self.pix_fmt = PIX_FMT_PACKED
        self.packed = bytearray(self.nbytes)
        self._floats = self.view.cast("f")
        self._packed_floats = memoryview(self.packed).cast("f")
        self._bands = [self._packed_floats[a * self.width * 3:b * self.width * 3]
                       for a, b in self._rows()]
        self._apply = self.cpu.applyRGB

    # -- per frame ---------------------------------------------------------
    def read_from(self, stream) -> int:
        """Fill the buffer from a decoder pipe. Returns the byte count read."""
        return stream.readinto(self.view)

    def fill_black(self) -> None:
        """A missing frame passes through black; the slate is drawn over it."""
        self.view[:] = bytes(self.nbytes)

    def transform(self) -> None:
        """Apply the colour transform in place, in parallel."""
        if not HAVE_NUMPY:
            # Planar -> interleaved in three strided copies. Each one runs in C;
            # a Python loop over 12 million pixels would be hopeless.
            p = self.pixels
            src, dst = self._floats, self._packed_floats
            dst[0::3] = src[2 * p:3 * p]      # R
            dst[1::3] = src[0:p]              # G
            dst[2::3] = src[p:2 * p]          # B

        list(self._pool.map(self._apply, self._bands))

    def payload(self) -> memoryview:
        """The bytes to hand to the encoder, matching `pix_fmt`."""
        return self.view if HAVE_NUMPY else memoryview(self.packed)

    def close(self) -> None:
        self._pool.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


def describe_path() -> str:
    """One line for the log, so the speed difference is never a mystery."""
    if HAVE_NUMPY:
        return "numpy %s (fast path)" % _np.__version__
    return "no numpy (portable path, roughly half the speed)"

# ==========================================================================
#  preset
# ==========================================================================
"""
preset.py - data model for presets and machine settings.

Only the data classes live here. JSON load/save, schema validation and
import/export are in `settings.py`.
"""





H264_MP4 = "h264_mp4"
PRORES_MOV = "prores_mov"
FORMATS = (H264_MP4, PRORES_MOV)

PRORES_PROFILES = {"proxy": "0", "lt": "1", "422": "2"}


@dataclass
class ColourSettings:
    """OCIO settings. The config path is stored per OS."""
    config_macos: str = "studio-config-v2.2.0_aces-v1.3_ocio-v2.4"
    config_linux: str = "studio-config-v2.2.0_aces-v1.3_ocio-v2.4"
    source: str = "ACES2065-1"
    display: str = "Rec.1886 Rec.709 - Display"
    view: str = "ACES 1.0 - SDR Video"
    look: str = ""


@dataclass
class ReformatSettings:
    canvas_width: int = 1920
    canvas_height: int = 1080
    fit_mode: str = reformat.FIT_HEIGHT
    crop_left: int = 0
    crop_right: int = 0
    crop_top: int = 0
    crop_bottom: int = 0
    shift_x: int = 0
    shift_y: int = 0
    band_colour: str = "black"
    bands_enabled: bool = True

    def plan_for(self, source_width: int, source_height: int) -> reformat.Plan:
        return reformat.build_plan(
            source_width, source_height,
            canvas_width=self.canvas_width, canvas_height=self.canvas_height,
            fit_mode=self.fit_mode,
            crop_left=self.crop_left, crop_right=self.crop_right,
            crop_top=self.crop_top, crop_bottom=self.crop_bottom,
            shift_x=self.shift_x, shift_y=self.shift_y,
            band_colour=self.band_colour if self.bands_enabled else "black")


@dataclass
class Preset:
    """An exportable preset."""
    name: str = "Review HD"
    output_format: str = H264_MP4
    crf: int = 18                         # confirmed in 3.3
    prores_profile: str = "422"
    colour: ColourSettings = field(default_factory=ColourSettings)
    reformat: ReformatSettings = field(default_factory=ReformatSettings)
    burnin: BurnInSettings = field(default_factory=BurnInSettings)
    output_template: str = "{source_dir}/../_review/{source_name}"

    @property
    def extension(self) -> str:
        return ".mp4" if self.output_format == H264_MP4 else ".mov"

    def validate(self) -> None:
        if self.output_format not in FORMATS:
            raise ValueError("Unknown format: %r (valid: %s)"
                             % (self.output_format, ", ".join(FORMATS)))
        if self.output_format == PRORES_MOV and self.prores_profile not in PRORES_PROFILES:
            raise ValueError("Unknown ProRes profile: %r (valid: %s)"
                             % (self.prores_profile, ", ".join(PRORES_PROFILES)))
        if not 1 <= self.crf <= 51:
            raise ValueError("CRF must be between 1 and 51, got: %r" % self.crf)


@dataclass
class MachineSettings:
    """Machine-specific settings, NEVER exported with a preset."""
    ffmpeg: str = "ffmpeg"
    ffprobe: str = "ffprobe"
    log_dir: str = os.path.expanduser("~/Library/Logs/WriteConvert")
    default_preset: str = "Review HD"
    auto_trigger: bool = True
    ocio_threads: int = 0                 # 0 -> min(16, cpu count)

# ==========================================================================
#  encoder
# ==========================================================================
"""
encoder.py - builds the ffmpeg command lines.

Two processes per job (see pipeline.py):
  * decode  : EXR -> planar float32, at source resolution, no filtering
  * encode  : takes the colour-transformed float frames, reformats them, lays the
              burn-in overlay on top and writes MP4/MOV

The burn-in arrives as a second raw RGBA input and is composited by ffmpeg's
`overlay` filter. Doing it in Python would need a per-pixel pass, which is what
numpy was for; keeping it out here is what lets the tool ship as one file.

Rec709 tags are written for both formats; the output is silent.
"""




OVERLAY_PIX_FMT = "rgba"

# Rec709 tags. NOTE: on ffmpeg 8 passing these as output options is NOT
# enough - only `colorspace` gets written, `color_primaries` and `color_trc`
# stay "unknown". The `setparams` filter writes all three, so both are used.
REC709_TAGS = ["-color_primaries", "bt709", "-color_trc", "bt709",
               "-colorspace", "bt709"]

REC709_SETPARAMS = ("setparams=color_primaries=bt709:color_trc=bt709:"
                    "colorspace=bt709")


def decode_run_command(pattern: str, start_number: int, count: int,
                       ffmpeg: str = "ffmpeg") -> list:
    """Decode one contiguous run of frames to planar float32."""
    return [ffmpeg, "-hide_banner", "-loglevel", "error",
            "-start_number", str(start_number), "-i", pattern,
            "-frames:v", str(count),
            "-f", "rawvideo", "-pix_fmt", "gbrpf32le", "-"]


def _codec_args(preset: Preset) -> list:
    if preset.output_format == H264_MP4:
        return ["-c:v", "libx264", "-crf", str(preset.crf), "-preset", "medium",
                "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-f", "mp4"]
    return ["-c:v", "prores_ks",
            "-profile:v", PRORES_PROFILES[preset.prores_profile],
            "-vendor", "apl0", "-pix_fmt", "yuv422p10le", "-f", "mov"]


def encode_command(preset: Preset, plan, source_width: int, source_height: int,
                   fps: str, out_path: str, in_pix_fmt: str,
                   overlay_fd: int = None, ffmpeg: str = "ffmpeg",
                   scale_flags: str = "lanczos") -> list:
    """One process: reformat, overlay, encode.

    Scaling happens here, AFTER the colour transform: ffmpeg's scale filter
    clips float values to [0,1] (measured). That is harmless now, the
    data is already display-referred, but it would burn out highlights if it ran
    before the ODT.
    """
    preset.validate()

    cmd = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", in_pix_fmt,
           "-s", "%dx%d" % (source_width, source_height), "-r", str(fps),
           "-i", "pipe:0"]

    if overlay_fd is not None:
        cmd += ["-f", "rawvideo", "-pix_fmt", OVERLAY_PIX_FMT,
                "-s", "%dx%d" % (plan.canvas_width, plan.canvas_height),
                "-r", str(fps), "-i", "pipe:%d" % overlay_fd]

    steps = _reformat.to_ffmpeg_filters(plan, scale_flags=scale_flags)
    # The reformat chain can be empty when the source already matches the canvas.
    base = ",".join(steps) if steps else "null"

    if overlay_fd is None:
        cmd += ["-vf", "%s,%s" % (base, REC709_SETPARAMS)]
    else:
        cmd += ["-filter_complex",
                "[0:v]%s[base];[base][1:v]overlay=0:0:format=auto,%s[v]"
                % (base, REC709_SETPARAMS),
                "-map", "[v]"]

    cmd += _codec_args(preset)
    cmd += REC709_TAGS
    cmd += ["-an", out_path]              # no audio
    return cmd

# ==========================================================================
#  settings
# ==========================================================================
"""
settings.py - local JSON settings file and preset import/export.

Machine settings (ffmpeg path, log directory, thread count, default preset) are
NEVER exported. Presets are, so they can travel between machines.

The settings window saves instantly; every call here rewrites the file
atomically.
"""





SCHEMA_VERSION = 1


class SettingsError(ValueError):
    """The settings file could not be read, or is invalid."""


# ---------------------------------------------------------------------------
#  dataclass <-> dict
# ---------------------------------------------------------------------------
def _to_dict(obj):
    if dataclasses.is_dataclass(obj):
        return {f.name: _to_dict(getattr(obj, f.name))
                for f in dataclasses.fields(obj)}
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_dict(v) for v in obj]
    return obj


def _from_dict(cls, data):
    """Build a FLAT dataclass from a dict.

    Unknown keys are IGNORED and missing ones fall back to defaults, so an old
    settings file opens in a new version and a new file does not break an old one.

    It does NOT resolve nested dataclasses - with `from __future__ import
    annotations` the field types arrive as strings and cannot be resolved
    reliably. Nesting is built explicitly in `preset_from_dict`.
    """
    if not isinstance(data, dict):
        return cls()
    known = {f.name for f in dataclasses.fields(cls)}
    return cls(**{k: v for k, v in data.items() if k in known})


def preset_to_dict(preset: Preset) -> dict:
    return _to_dict(preset)


def preset_from_dict(data: dict) -> Preset:
    if not isinstance(data, dict):
        raise SettingsError("A preset must be a dictionary.")
    preset = Preset(
        name=data.get("name", "Untitled"),
        output_format=data.get("output_format", Preset().output_format),
        crf=int(data.get("crf", 18)),
        prores_profile=data.get("prores_profile", "422"),
        colour=_from_dict(ColourSettings, data.get("colour", {})),
        reformat=_from_dict(ReformatSettings, data.get("reformat", {})),
        burnin=_from_dict(BurnInSettings, data.get("burnin", {})),
        output_template=data.get("output_template", Preset().output_template))
    # Burn-in zones are a free-form dict; drop invalid keys.
    preset.burnin.zones = {k: str(v) for k, v in (preset.burnin.zones or {}).items()
                           if k in ZONES}
    preset.validate()
    return preset


# ---------------------------------------------------------------------------
#  Settings file
# ---------------------------------------------------------------------------
class Settings:
    """Machine settings plus the list of presets."""

    def __init__(self, machine: MachineSettings = None, presets: list = None):
        self.machine = machine or MachineSettings()
        self.presets = list(presets) if presets else [Preset()]
        if not self.machine.log_dir:
            self.machine.log_dir = wc_platform.default_log_dir()

    # -- preset access -----------------------------------------------------
    def preset_names(self) -> list:
        return [p.name for p in self.presets]

    def get(self, name: str) -> Preset:
        for p in self.presets:
            if p.name == name:
                return p
        raise SettingsError("Preset not found: %r\nAvailable: %s"
                            % (name, ", ".join(self.preset_names()) or "(none)"))

    def default_preset(self) -> Preset:
        """The preset used by the automatic trigger - the starred one."""
        try:
            return self.get(self.machine.default_preset)
        except SettingsError:
            if not self.presets:
                raise SettingsError("There are no presets.")
            return self.presets[0]

    def set_default(self, name: str) -> None:
        self.get(name)                      # validate that it exists
        self.machine.default_preset = name

    def unique_name(self, wanted: str) -> str:
        names = set(self.preset_names())
        if wanted not in names:
            return wanted
        n = 2
        while "%s %d" % (wanted, n) in names:
            n += 1
        return "%s %d" % (wanted, n)

    def add(self, preset: Preset) -> Preset:
        preset.name = self.unique_name(preset.name)
        self.presets.append(preset)
        return preset

    def duplicate(self, name: str) -> Preset:
        return self.add(copy.deepcopy(self.get(name)))

    def remove(self, name: str) -> None:
        if len(self.presets) <= 1:
            raise SettingsError("The last preset cannot be deleted.")
        preset = self.get(name)
        self.presets.remove(preset)
        if self.machine.default_preset == name:
            self.machine.default_preset = self.presets[0].name

    def rename(self, old: str, new: str) -> str:
        preset = self.get(old)
        new = (new or "").strip() or old
        if new != old:
            others = [p.name for p in self.presets if p is not preset]
            candidate, n = new, 2
            while candidate in others:
                candidate, n = "%s %d" % (new, n), n + 1
            if self.machine.default_preset == old:
                self.machine.default_preset = candidate
            preset.name = candidate
        return preset.name

    # -- serialisation -----------------------------------------------------
    def to_dict(self) -> dict:
        return {"schema_version": SCHEMA_VERSION,
                "machine": _to_dict(self.machine),
                "presets": [preset_to_dict(p) for p in self.presets]}

    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        if not isinstance(data, dict):
            raise SettingsError("The root of the settings file must be a dictionary.")
        machine = _from_dict(MachineSettings, data.get("machine", {}))

        presets, problems = [], []
        for raw in data.get("presets", []):
            try:
                presets.append(preset_from_dict(raw))
            except (SettingsError, ValueError) as exc:
                problems.append("  %s: %s" % (
                    raw.get("name", "?") if isinstance(raw, dict) else "?", exc))
        if problems and not presets:
            raise SettingsError("No preset could be read:\n" + "\n".join(problems))

        settings = cls(machine=machine, presets=presets or None)
        settings.load_problems = problems     # so the UI can warn
        return settings


def load(path: str = None) -> Settings:
    """Load the settings. A missing file starts from defaults (not an error)."""
    path = path or wc_platform.settings_path()
    if not os.path.isfile(path):
        return Settings()
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise SettingsError("The settings file is corrupt (%s): %s" % (path, exc)) from exc
    except OSError as exc:
        raise SettingsError("Could not read the settings file (%s): %s" % (path, exc)) from exc
    return Settings.from_dict(data)


def save(settings: Settings, path: str = None) -> str:
    """Write atomically: .tmp first, then rename. No half-written settings file."""
    path = path or wc_platform.settings_path()
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)

    fd, tmp = tempfile.mkstemp(dir=folder, prefix=".settings-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(settings.to_dict(), fh, indent=2, ensure_ascii=False)
        os.replace(tmp, path)                # overwriting IS correct for the settings file
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


# ---------------------------------------------------------------------------
#  Preset import / export
# ---------------------------------------------------------------------------
def export_preset(preset: Preset, path: str) -> str:
    """Write one preset to a file. Machine settings are NEVER written."""
    payload = {"schema_version": SCHEMA_VERSION, "kind": "writeconvert-preset",
               "preset": preset_to_dict(preset)}
    with open(os.path.expanduser(path), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2, ensure_ascii=False)
    return path


def import_preset(path: str) -> Preset:
    path = os.path.expanduser(path)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise SettingsError("The preset file is corrupt (%s): %s" % (path, exc)) from exc
    except OSError as exc:
        raise SettingsError("Could not read the preset file (%s): %s" % (path, exc)) from exc

    if not isinstance(data, dict):
        raise SettingsError("The root of the preset file must be a dictionary.")
    # Both {"preset": {...}} and a bare preset dictionary are accepted.
    raw = data.get("preset", data)
    return preset_from_dict(raw)

# ==========================================================================
#  pipeline
# ==========================================================================
"""
pipeline.py - running a job from end to end.

TWO PROCESSES
-------------
    ffmpeg decode   EXR -> gbrpf32le (source resolution, no filters)
         |
    Python          OCIO, band by band in parallel (frames.FrameBuffer)
         |          + a thread rendering the burn-in overlay with Qt
         |
    ffmpeg encode   crop/scale/canvas -> overlay -> H.264 MP4 or ProRes MOV

Why the colour transform sits between two ffmpeg processes: scaling has to
happen AFTER the ODT because ffmpeg's scale filter clips float values to [0,1]
(measured), and burn-in has to happen after scaling because the text
sits a fixed distance from the canvas edge and may extend over the bands.

The overlay is written on a second pipe by its own thread. Both pipes must be
fed concurrently: ffmpeg's overlay filter reads them in step, so writing one
from the main loop while the other sat idle would deadlock.

NO temporary files are produced.
"""





class PipelineError(RuntimeError):
    """The job could not be run."""


@dataclass
class Result:
    output_path: str
    frames: int
    missing: list
    elapsed: float
    grey_measurement: float
    canvas: tuple
    source: tuple
    path: str = ""

    @property
    def fps(self) -> float:
        return self.frames / self.elapsed if self.elapsed else 0.0


@dataclass
class Job:
    sequence: Sequence
    preset: Preset
    context: JobContext
    fps: str = "25"
    output_path: str = ""
    cancelled: threading.Event = field(default_factory=threading.Event)


# ---------------------------------------------------------------------------
def probe_resolution(path: str, ffprobe: str = "ffprobe") -> tuple:
    try:
        out = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-of", "csv=p=0:s=x", path],
            capture_output=True, text=True, check=True).stdout.strip()
        w, h = (int(v) for v in out.split("x"))
        return w, h
    except Exception as exc:
        raise PipelineError("Could not read source resolution (%s): %s" % (path, exc))


def contiguous_runs(numbers: list) -> list:
    """Split frame numbers into contiguous runs: [1001,1002,1005] -> [(1001,2),(1005,1)]

    ffmpeg's image2 demuxer stops at a gap, so each run is decoded separately and
    the missing frames in between get a black frame plus a slate.
    """
    runs = []
    for n in numbers:
        if runs and n == runs[-1][0] + runs[-1][1]:
            runs[-1] = (runs[-1][0], runs[-1][1] + 1)
        else:
            runs.append((n, 1))
    return runs


class _Decoders:
    """Walks the contiguous runs, spawning one decoder per run."""

    def __init__(self, sequence: Sequence, ffmpeg: str):
        self.sequence = sequence
        self.ffmpeg = ffmpeg
        self._runs = iter(contiguous_runs(sequence.frames))
        self._current = None
        self._left = 0

    def read_into(self, buffer: frames.FrameBuffer) -> None:
        if self._left == 0:
            self._close()
            start, count = next(self._runs)
            self._current = subprocess.Popen(
                encoder.decode_run_command(self.sequence.ffmpeg_pattern,
                                           start, count, self.ffmpeg),
                stdout=subprocess.PIPE)
            self._left = count

        read = buffer.read_from(self._current.stdout)
        if read != buffer.nbytes:
            raise PipelineError("A frame arrived short (%d/%d bytes). The file "
                                "may be corrupt." % (read, buffer.nbytes))
        self._left -= 1

    def _close(self) -> None:
        if self._current is None:
            return
        try:
            self._current.stdout.close()
        except OSError:
            pass
        try:
            self._current.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._current.kill()
            self._current.wait()
        self._current = None

    def close(self) -> None:
        self._close()


# ---------------------------------------------------------------------------
def run(job: Job, machine: MachineSettings = None, progress=None) -> Result:
    """Run the job end to end. `progress(done, total)` is called per frame."""
    machine = machine or MachineSettings()
    preset = job.preset
    preset.validate()
    seq = job.sequence

    src_w, src_h = probe_resolution(seq.path_for(seq.first), machine.ffprobe)
    plan = preset.reformat.plan_for(src_w, src_h)
    cw, ch = plan.canvas_width, plan.canvas_height

    job.context.canvas_width, job.context.canvas_height = cw, ch
    job.context.first_frame = seq.first
    if not job.context.frame_range:
        job.context.frame_range = seq.frame_range_label
    if not job.context.clip_name:
        job.context.clip_name = seq.clip_name

    config_spec = colour.config_for_platform(preset.colour.config_macos,
                                             preset.colour.config_linux)
    _, cpu = colour.make_processor(config_spec, preset.colour.source,
                                   preset.colour.display, preset.colour.view,
                                   preset.colour.look)
    grey = colour.measure_grey(cpu)

    final_path = job.output_path
    if not final_path:
        final_path, _ = output.prepare(preset.output_template, seq.directory,
                                       seq.clip_name, preset.extension)
    partial = output.partial_path(final_path)

    overlays = OverlayStream(preset.burnin, job.context, seq.missing)
    missing = set(seq.missing)
    total = seq.last - seq.first + 1
    present = set(seq.frames)

    read_fd = write_fd = None
    if overlays.needed:
        read_fd, write_fd = os.pipe()

    buffer = frames.FrameBuffer(cpu, src_w, src_h, machine.ocio_threads)
    decoders = _Decoders(seq, machine.ffmpeg)

    command = encoder.encode_command(preset, plan, src_w, src_h, job.fps,
                                     partial, buffer.pix_fmt,
                                     overlay_fd=read_fd, ffmpeg=machine.ffmpeg)
    proc = subprocess.Popen(command, stdin=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            pass_fds=(read_fd,) if read_fd is not None else ())
    if read_fd is not None:
        os.close(read_fd)

    errors = {}

    def drain():
        errors["encode"] = (proc.stderr.read() or b"").decode("utf-8", "replace").strip()

    drainer = threading.Thread(target=drain, daemon=True)
    drainer.start()

    overlay_error = {}

    def feed_overlays():
        """Runs alongside the main loop; see the deadlock note in the header."""
        try:
            with os.fdopen(write_fd, "wb") as stream:
                for number in range(seq.first, seq.last + 1):
                    if job.cancelled.is_set():
                        break
                    stream.write(overlays.frame(number))
        except BrokenPipeError:
            pass                            # the encoder went away; the main loop reports
        except Exception as exc:            # noqa: BLE001
            overlay_error["exc"] = exc

    feeder = None
    if write_fd is not None:
        feeder = threading.Thread(target=feed_overlays, name="wc-overlay",
                                  daemon=True)
        feeder.start()

    done = 0
    t0 = time.time()
    try:
        for number in range(seq.first, seq.last + 1):
            if job.cancelled.is_set():
                break

            if number in present:
                decoders.read_into(buffer)
                buffer.transform()
            else:
                buffer.fill_black()         # the slate is drawn by the overlay

            proc.stdin.write(buffer.payload())
            done += 1
            if progress:
                progress(done, total)
    finally:
        if job.cancelled.is_set() and proc.poll() is None:
            proc.kill()                     # do not wait on a full pipe
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except OSError:
            pass
        decoders.close()
        if feeder is not None:
            feeder.join(timeout=10)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        drainer.join(timeout=5)
        buffer.close()

    if job.cancelled.is_set():
        output.cleanup(partial)             # 3.8: never leave a half file
        raise PipelineError("Job cancelled.")

    if overlay_error:
        output.cleanup(partial)
        raise PipelineError("Burn-in overlay failed: %s" % overlay_error["exc"])

    if proc.returncode != 0:
        output.cleanup(partial)
        raise PipelineError("ffmpeg encode failed (exit code %d):\n%s"
                            % (proc.returncode,
                               errors.get("encode") or "(no error output)"))
    if done != total:
        output.cleanup(partial)
        raise PipelineError("Expected %d frames, wrote %d." % (total, done))

    written = output.finalise(partial, final_path)
    return Result(output_path=written, frames=done, missing=sorted(missing),
                  elapsed=time.time() - t0, grey_measurement=grey,
                  canvas=(cw, ch), source=(src_w, src_h),
                  path=frames.describe_path())

# ==========================================================================
#  queue
# ==========================================================================
"""
queue.py - sequential job queue.

Rules:
  * ONE job at a time (confirmed). Not configurable.
  * When Flame quits the running job is cancelled, the half file is removed and
    pending jobs are dropped. Flame has NO shutdown hook, so the hook
    module connects to `QApplication.aboutToQuit` instead.
  * Duplicate guard: the claim that the hook fires twice on stereo renders
    was never confirmed, but guarding against the same job entering twice is cheap.

ALL `flame.*` calls must happen on the MAIN THREAD. This module never
touches Flame; notifications go out through the `notify` callback and the hook
module marshals them with `flame.schedule_idle_event`.
"""





PENDING = "pending"
RUNNING = "running"
DONE = "done"
FAILED = "failed"
CANCELLED = "cancelled"


@dataclass
class Entry:
    job: pipeline.Job
    key: str = ""
    status: str = PENDING
    result: object = None
    error: str = ""
    submitted_at: float = field(default_factory=time.time)

    @property
    def label(self) -> str:
        seq = self.job.sequence
        return "%s (%s)" % (seq.clip_name, seq.frame_range_label)


class JobQueue:
    """Sequential queue with a single worker thread."""

    def __init__(self, machine=None, notify=None, progress=None,
                 dedupe_window: float = 10.0):
        self.machine = machine
        self.notify = notify or (lambda level, message: None)
        self.progress = progress
        self.dedupe_window = dedupe_window

        self._queue = _queue.Queue()
        self._lock = threading.Lock()
        self._entries = []
        self._current = None
        self._recent = {}                   # key -> timestamp
        self._shutdown = threading.Event()
        self._worker = threading.Thread(target=self._run, name="wc-queue",
                                        daemon=True)
        self._worker.start()

    # -- public API --------------------------------------------------------
    def submit(self, job: pipeline.Job, key: str = "") -> Entry:
        """Queue a job. A job with the same key seen moments ago is ignored."""
        if self._shutdown.is_set():
            raise RuntimeError("The queue is shutting down; no new jobs accepted.")

        key = key or "%s|%d-%d" % (job.sequence.directory,
                                   job.sequence.first, job.sequence.last)
        now = time.time()
        with self._lock:
            last = self._recent.get(key)
            if last is not None and now - last < self.dedupe_window:
                self.notify("info", "Already queued, ignoring duplicate: %s"
                            % job.sequence.clip_name)
                return None
            self._recent[key] = now
            for old_key, when in list(self._recent.items()):
                if now - when > max(60.0, self.dedupe_window * 6):
                    del self._recent[old_key]

            entry = Entry(job=job, key=key)
            self._entries.append(entry)

        self._queue.put(entry)
        self.notify("info", "Queued: %s" % entry.label)
        return entry

    def pending(self) -> list:
        with self._lock:
            return [e for e in self._entries if e.status == PENDING]

    def current(self) -> Entry:
        return self._current

    def entries(self) -> list:
        with self._lock:
            return list(self._entries)

    def cancel_all(self, reason: str = "Flame is quitting") -> None:
        """Stop the running job and drop everything pending."""
        with self._lock:
            for entry in self._entries:
                if entry.status == PENDING:
                    entry.status = CANCELLED
                    entry.error = reason
        current = self._current
        if current is not None:
            current.job.cancelled.set()

    def shutdown(self, timeout: float = 10.0) -> None:
        """Shut the queue down and wait for the running job to finish."""
        self._shutdown.set()
        self.cancel_all()
        self._queue.put(None)
        self._worker.join(timeout=timeout)

    # -- worker ------------------------------------------------------------
    def _run(self) -> None:
        while True:
            entry = self._queue.get()
            if entry is None:
                return
            if entry.status == CANCELLED:
                continue
            if self._shutdown.is_set():
                entry.status = CANCELLED
                continue
            self._process(entry)

    def _process(self, entry: Entry) -> None:
        self._current = entry
        entry.status = RUNNING
        self.notify("info", "Started: %s" % entry.label)

        def on_progress(done, total):
            if self.progress:
                self.progress(entry, done, total)

        try:
            entry.result = pipeline.run(entry.job, self.machine, on_progress)
            entry.status = DONE
            missing = len(entry.result.missing)
            message = "Finished: %s -> %s  (%d frames, %.1f s)" % (
                entry.label, entry.result.output_path,
                entry.result.frames, entry.result.elapsed)
            if missing:
                message += "  WARNING: %d missing frames replaced with slates" % missing
            self.notify("warning" if missing else "success", message)
        except Exception as exc:                          # noqa: BLE001
            if entry.job.cancelled.is_set():
                entry.status = CANCELLED
                entry.error = str(exc)
                self.notify("info", "Cancelled: %s" % entry.label)
            else:
                entry.status = FAILED
                entry.error = str(exc)
                self.notify("error", "ERROR: %s\n%s" % (entry.label, exc))
                self.notify("debug", traceback.format_exc())
        finally:
            self._current = None

# ==========================================================================
#  job
# ==========================================================================
"""
job.py - builds a Job from the Flame hook info.

NOTE: the functions here that read `flame.*` must be called from the MAIN THREAD. The hook already runs there; every piece of Flame state is read here and
copied into the Job before it is queued. The queue thread never touches Flame.

`batch_export_end` -> `info` keys, as observed on Flame 2026.2:
    resolvedPath, exportPath, namePattern, nodeName, shotName,
    firstFrame, lastFrame, fps (STRING), width, height, aspectRatio,
    colourSpace, depth, channelsEncoding, pixelLayout, nbChannels, scanFormat
    aborted  -> present ONLY on an aborted render
"""



try:
    import flame
except Exception:                      # must stay testable outside Flame
    flame = None


class JobError(ValueError):
    """A job could not be built from the hook info."""


def is_aborted(info: dict) -> bool:
    """True when the render was aborted.

    The `aborted` key is absent entirely on a SUCCESSFUL render, so we
    check the value with a default of False rather than the key's presence.
    """
    return bool(info.get("aborted", False))


def parse_fps(info: dict, default: int = 25) -> int:
    """`info['fps']` arrives as a string ('25'); the node's `frame_rate` is '25 fps'."""
    raw = info.get("fps", default)
    try:
        return int(round(float(str(raw).split()[0])))
    except (ValueError, IndexError):
        return default


def current_project_name() -> str:
    try:
        return str(flame.project.current_project.name)
    except Exception:
        return ""


def current_user_name() -> str:
    try:
        return str(flame.users.current_user.name)
    except Exception:
        return ""


def _attr(node, name: str, default=""):
    """Read a PyAttribute value; every field comes through `get_value()`."""
    if node is None:
        return default
    try:
        value = getattr(node, name)
    except Exception:
        return default
    getter = getattr(value, "get_value", None)
    if callable(getter):
        try:
            return getter()
        except Exception:
            return default
    return value


def find_write_node(node_name: str):
    """Find the Write File node in the batch by name.

    `info['nodeName']` is the Write File node's own name. The start
    timecode is not in the hook info, so it has to be read from the node.
    """
    if flame is None or not node_name:
        return None
    try:
        for node in (getattr(flame.batch, "nodes", None) or []):
            # `node.name` is a PyAttribute; its value comes from `get_value()`
            #. Comparing with `str()` is fragile.
            if str(_attr(node, "name", "")) == node_name:
                return node
    except Exception:
        pass
    return None


def read_start_timecode(node, default: str = "00:00:00:00") -> str:
    """The node's `source_timecode` field. There is NO timecode in `info`.

    The value is not a plain string: it is a Flame object whose str() has been
    seen to include quotes ("'00:00:00:00'"), so the timecode is extracted with a
    regex rather than trusted verbatim.
    """
    value = _attr(node, "source_timecode", None)
    if value is None:
        return default
    return normalise_timecode(value, default)


def build(info: dict, preset: Preset, node=None) -> Job:
    """Build a Job from the hook info. Must be called on the MAIN THREAD."""
    resolved = info.get("resolvedPath") or ""
    if not resolved:
        raise JobError("No `resolvedPath` in the hook info; cannot build a job.")

    try:
        seq = wc_sequence.scan_for_job(resolved)
    except wc_sequence.SequenceError as exc:
        raise JobError("Could not read the sequence: %s" % exc) from exc

    node_name = info.get("nodeName") or ""
    if node is None:
        node = find_write_node(node_name)

    fps = parse_fps(info)
    ctx = JobContext(
        clip_name=seq.clip_name,
        project=current_project_name(),
        shot=info.get("shotName") or str(_attr(node, "shot_name", "")),
        user=current_user_name(),
        fps=fps,
        start_timecode=read_start_timecode(node),
        first_frame=seq.first,
        frame_range=seq.frame_range_label)

    return Job(sequence=seq, preset=preset, context=ctx, fps=str(fps))


def describe(info: dict) -> str:
    """One-line summary for the log."""
    return ("node=%s path=%s frames=%s-%s %sx%s %sfps %s" % (
        info.get("nodeName", "?"), info.get("resolvedPath", "?"),
        info.get("firstFrame", "?"), info.get("lastFrame", "?"),
        info.get("width", "?"), info.get("height", "?"),
        info.get("fps", "?"), info.get("colourSpace", "")))

# ==========================================================================
#  notify
# ==========================================================================
"""
notify.py - log file and in-Flame messages.

The Flame message API was verified:
    flame.messages.show_in_console(message, type, duration)
    flame.messages.show_in_dialog(title, message, type, buttons)

ALL `flame.*` calls must happen on the MAIN THREAD. Notifications coming
from the queue thread are marshalled with `flame.schedule_idle_event`.
"""




try:
    import flame
except Exception:
    flame = None


LEVELS = ("debug", "info", "success", "warning", "error")

# Types the Flame console understands; never send an unknown one.
_FLAME_TYPE = {"info": "info", "success": "info", "debug": "info",
               "warning": "warning", "error": "error"}


class Notifier:
    """Writes to the log file and optionally to the Flame console."""

    def __init__(self, log_dir: str = "", to_flame: bool = True,
                 echo: bool = False):
        self.log_dir = log_dir or wc_platform.default_log_dir()
        self.to_flame = to_flame
        self.echo = echo
        self._lock = threading.Lock()
        self._path = None

    # -- log ---------------------------------------------------------------
    @property
    def log_path(self) -> str:
        if self._path is None:
            name = "writeconvert-%s.log" % datetime.now().strftime("%Y-%m")
            self._path = os.path.join(self.log_dir, name)
        return self._path

    def _write(self, level: str, message: str) -> None:
        line = "[%s] %-7s %s\n" % (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level.upper(), message)
        try:
            with self._lock:
                os.makedirs(self.log_dir, exist_ok=True)
                with open(self.log_path, "a", encoding="utf-8") as fh:
                    fh.write(line)
        except OSError:
            pass                      # a failing log must never stop the job
        if self.echo:
            print("WriteConvert " + line.rstrip())

    # -- Flame -------------------------------------------------------------
    @staticmethod
    def _show_in_flame(level: str, message: str) -> None:
        """Runs on the MAIN THREAD."""
        if flame is None:
            return
        try:
            messages = getattr(flame, "messages", None)
            if messages is None:
                return
            # Collapse to one line: the console truncates multi-line messages.
            first = message.strip().splitlines()[0] if message.strip() else ""
            messages.show_in_console("WriteConvert: " + first,
                                     _FLAME_TYPE.get(level, "info"), 6)
        except Exception:
            pass

    def _schedule(self, level: str, message: str) -> None:
        """Marshal the message to the main thread. A no-op without Flame."""
        if flame is None or not self.to_flame:
            return
        try:
            flame.schedule_idle_event(
                lambda: Notifier._show_in_flame(level, message))
        except Exception:
            pass

    # -- public API --------------------------------------------------------
    def __call__(self, level: str, message: str) -> None:
        level = level if level in LEVELS else "info"
        self._write(level, message)
        if level != "debug":
            self._schedule(level, message)

    def dialog(self, title: str, message: str, level: str = "error") -> None:
        """For things the user must not miss (errors)."""
        self._write(level, "%s - %s" % (title, message))
        if flame is None or not self.to_flame:
            return

        def _show():
            try:
                flame.messages.show_in_dialog(
                    title, message, _FLAME_TYPE.get(level, "info"), ["OK"])
            except Exception:
                pass
        try:
            flame.schedule_idle_event(_show)
        except Exception:
            pass

# ==========================================================================
#  ui/preview
# ==========================================================================
"""
preview.py - schematic preview for reformat and burn-in.

NOT A REAL FRAME. It shows how the source frame, the crop region, the canvas,
the bands and the burn-in zones sit relative to each other. It stays visible on
every tab because crop / canvas / bands / burn-in all affect one another.
"""


from PySide6 import QtCore, QtGui, QtWidgets



BG = QtGui.QColor("#1e1e1e")
SOURCE_EDGE = QtGui.QColor("#5a5a5a")
CROP_EDGE = QtGui.QColor("#e0b000")
IMAGE_FILL = QtGui.QColor("#3a4a5a")
CANVAS_EDGE = QtGui.QColor("#d0d0d0")
ZONE_FILL = QtGui.QColor(255, 255, 255, 40)
ZONE_TEXT = QtGui.QColor("#c8c8c8")
ERROR_COLOUR = QtGui.QColor("#ff5050")


class PreviewWidget(QtWidgets.QWidget):
    """Draws the canvas and the image inside it, to scale."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 300)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,
                           QtWidgets.QSizePolicy.Expanding)
        self._preset = None
        self._source = (4096, 3024)
        self._error = ""

    def update_from(self, preset, source_size) -> None:
        self._preset = preset
        self._source = source_size
        self._error = ""
        if preset is not None:
            try:
                preset.reformat.plan_for(*source_size)
            except wc_reformat.ReformatError as exc:
                self._error = str(exc)
        self.update()

    # -- cizim -------------------------------------------------------------
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        painter.fillRect(self.rect(), BG)

        if self._preset is None:
            return
        if self._error:
            self._draw_error(painter)
            return

        try:
            plan = self._preset.reformat.plan_for(*self._source)
        except wc_reformat.ReformatError:
            self._draw_error(painter)
            return

        area = self.rect().adjusted(16, 16, -16, -46)
        scale = min(area.width() / plan.canvas_width,
                    area.height() / plan.canvas_height)
        cw, chh = plan.canvas_width * scale, plan.canvas_height * scale
        ox = area.left() + (area.width() - cw) / 2
        oy = area.top() + (area.height() - chh) / 2
        canvas_rect = QtCore.QRectF(ox, oy, cw, chh)

        # Bands: the part of the canvas the image does not cover
        band = QtGui.QColor(self._preset.reformat.band_colour
                            if self._preset.reformat.bands_enabled else "black")
        if not band.isValid():
            band = QtGui.QColor("black")
        painter.fillRect(canvas_rect, band)

        # The part of the image that lands on the canvas
        p = plan.placement
        image_rect = QtCore.QRectF(ox + p.x * scale, oy + p.y * scale,
                                   p.width * scale, p.height * scale)
        painter.fillRect(image_rect, IMAGE_FILL)

        painter.setPen(QtGui.QPen(CANVAS_EDGE, 1))
        painter.drawRect(canvas_rect)

        self._draw_source_inset(painter, plan, canvas_rect)
        self._draw_zones(painter, plan, canvas_rect, scale)
        self._draw_caption(painter, plan)

    def _draw_source_inset(self, painter, plan, canvas_rect) -> None:
        """A small inset, top right: the source frame and the crop region in it."""
        w = canvas_rect.width() * 0.26
        h = w * plan.source.height / plan.source.width
        rect = QtCore.QRectF(canvas_rect.right() - w - 6, canvas_rect.top() + 6, w, h)

        painter.setPen(QtGui.QPen(SOURCE_EDGE, 1, QtCore.Qt.DashLine))
        painter.setBrush(QtCore.Qt.NoBrush)
        painter.drawRect(rect)

        s = rect.width() / plan.source.width
        crop = QtCore.QRectF(rect.left() + plan.crop.x * s,
                             rect.top() + plan.crop.y * s,
                             plan.crop.width * s, plan.crop.height * s)
        painter.setPen(QtGui.QPen(CROP_EDGE, 1))
        painter.drawRect(crop)

    def _draw_zones(self, painter, plan, canvas_rect, scale) -> None:
        """Burn-in zones, a fixed distance from the canvas edge."""
        burn = self._preset.burnin
        margin = plan.canvas_height * burn.margin_pct / 100 * scale
        height = plan.canvas_height * burn.font_size_pct / 100 * scale * 1.4
        width = canvas_rect.width() / 3.4

        font = painter.font()
        font.setPixelSize(max(7, int(height * 0.62)))
        painter.setFont(font)

        for zone in ZONES:
            text = (burn.zones.get(zone) or "").strip()
            top = zone.startswith("top")
            y = (canvas_rect.top() + margin if top
                 else canvas_rect.bottom() - margin - height)
            if zone.endswith("left"):
                x = canvas_rect.left() + margin
            elif zone.endswith("centre"):
                x = canvas_rect.center().x() - width / 2
            else:
                x = canvas_rect.right() - margin - width
            box = QtCore.QRectF(x, y, width, height)

            painter.fillRect(box, ZONE_FILL if text else QtGui.QColor(255, 255, 255, 12))
            if text:
                painter.setPen(ZONE_TEXT)
                painter.drawText(box, QtCore.Qt.AlignCenter,
                                 painter.fontMetrics().elidedText(
                                     text, QtCore.Qt.ElideRight, int(width) - 4))

    def _draw_caption(self, painter, plan) -> None:
        painter.setPen(QtGui.QColor("#9a9a9a"))
        font = painter.font()
        font.setPixelSize(11)
        painter.setFont(font)
        bands = "bands" if plan.has_bands else "no bands"
        painter.drawText(
            self.rect().adjusted(16, 0, -16, -14),
            QtCore.Qt.AlignBottom | QtCore.Qt.AlignHCenter,
            "%d x %d  ->  %d x %d   (%s, scale %.3f)"
            % (plan.source.width, plan.source.height,
               plan.canvas_width, plan.canvas_height, bands, plan.scale_factor))

    def _draw_error(self, painter) -> None:
        painter.setPen(ERROR_COLOUR)
        font = painter.font()
        font.setPixelSize(12)
        painter.setFont(font)
        painter.drawText(self.rect().adjusted(16, 16, -16, -16),
                         QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap,
                         self._error or "Invalid reformat settings.")

# ==========================================================================
#  ui/settings_window
# ==========================================================================
"""
settings_window.py - the settings window.

Layout: two tabs at the top (Presets / General). The Presets tab has three
columns: the preset list, five sub-tabs, and a schematic preview that stays
visible at all times.

Saving is INSTANT - there is no OK/Cancel. Writes are delayed by ~500 ms
so a text field does not hit the disk on every keystroke.
"""



from PySide6 import QtCore, QtGui, QtWidgets



SAVE_DELAY_MS = 500

FIT_LABELS = [("Fit height (bands left and right)", wc_reformat.FIT_HEIGHT),
              ("Fit width (bands top and bottom)", wc_reformat.FIT_WIDTH),
              ("Fill (no bands, overflow cropped)", wc_reformat.FILL)]

ZONE_LABELS = [("top_left", "Top left"), ("top_centre", "Top centre"),
               ("top_right", "Top right"), ("bottom_left", "Bottom left"),
               ("bottom_centre", "Bottom centre"), ("bottom_right", "Bottom right")]

CANVAS_PRESETS = [("1920 x 1080", (1920, 1080)), ("3840 x 2160", (3840, 2160)),
                  ("Custom", None)]

_window = None


def show(engine):
    """Open the window, or bring it to the front."""
    global _window
    if _window is None or not _window.isVisible():
        _window = SettingsWindow(engine)
    _window.show()
    _window.raise_()
    _window.activateWindow()
    return _window


# ---------------------------------------------------------------------------
class SettingsWindow(QtWidgets.QWidget):

    def __init__(self, engine, parent=None):
        super().__init__(parent)
        self.engine = engine
        self.settings = engine.settings
        self._loading = False
        self._last_zone_edit = None

        version = getattr(engine, "version", "")
        self.setWindowTitle("Write File Transcoder - Settings"
                            + ("  (v%s)" % version if version else ""))
        self.resize(1140, 720)

        self._save_timer = QtCore.QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(SAVE_DELAY_MS)
        self._save_timer.timeout.connect(self._save_now)

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_presets_tab(), "Presets")
        tabs.addTab(self._build_general_tab(), "General")

        self.status = QtWidgets.QLabel("")
        self.status.setStyleSheet("color:#888;")

        footer = QtWidgets.QLabel("%s  v%s   \u00b7   %s"
                                  % (getattr(engine, "script_name", "Write File Transcoder"),
                                     getattr(engine, "version", ""),
                                     getattr(engine, "credit", "")))
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("color:#777; font-size:11px;")
        footer.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabs)
        layout.addWidget(self.status)
        layout.addWidget(footer)

        self._reload_preset_list()
        self._load_general()

    # ================================================================= saving
    def _touch(self) -> None:
        """Something changed: schedule a save and refresh the preview."""
        if self._loading:
            return
        self._save_timer.start()
        self._refresh_preview()

    def _save_now(self) -> None:
        try:
            path = wc_settings.save(self.settings)
            self.status.setText("Saved: %s" % path)
        except (wc_settings.SettingsError, OSError) as exc:
            self.status.setText("COULD NOT SAVE: %s" % exc)

    def closeEvent(self, event):
        if self._save_timer.isActive():
            self._save_timer.stop()
            self._save_now()
        try:
            self.engine.reload_settings()
        except Exception:
            pass
        super().closeEvent(event)

    # ================================================================ presets
    def _build_presets_tab(self) -> QtWidgets.QWidget:
        page = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(page)

        layout.addWidget(self._build_preset_list(), 0)
        layout.addWidget(self._build_editor(), 1)
        layout.addWidget(self._build_preview_panel(), 0)
        return page

    def _build_preset_list(self) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        box.setFixedWidth(210)
        layout = QtWidgets.QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(QtWidgets.QLabel("PRESETS"))
        self.preset_list = QtWidgets.QListWidget()
        self.preset_list.currentRowChanged.connect(self._on_preset_selected)
        self.preset_list.itemChanged.connect(self._on_preset_renamed)
        self.preset_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.preset_list.customContextMenuRequested.connect(self._preset_menu)
        layout.addWidget(self.preset_list, 1)

        for label, slot in (("New", self._add_preset),
                            ("Duplicate", self._duplicate_preset),
                            ("Rename...", self._rename_preset),
                            ("Delete", self._delete_preset),
                            ("Import...", self._import_preset),
                            ("Export...", self._export_preset)):
            button = QtWidgets.QPushButton(label)
            button.clicked.connect(slot)
            layout.addWidget(button)

        hint = QtWidgets.QLabel("* = used by the automatic trigger.\n"
                                "Right click for rename / make default.\n"
                                "Double click also renames.")
        hint.setStyleSheet("color:#888; font-size:11px;")
        hint.setWordWrap(True)
        layout.addWidget(hint)
        return box

    def _build_preview_panel(self) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        box.setFixedWidth(400)
        layout = QtWidgets.QVBoxLayout(box)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(QtWidgets.QLabel("SCHEMATIC PREVIEW"))

        self.preview = PreviewWidget()
        layout.addWidget(self.preview, 1)

        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Source:"))
        self.preview_w = self._spin(64, 30000, 4096, self._refresh_preview)
        self.preview_h = self._spin(64, 30000, 3024, self._refresh_preview)
        row.addWidget(self.preview_w)
        row.addWidget(QtWidgets.QLabel("x"))
        row.addWidget(self.preview_h)
        row.addStretch(1)
        layout.addLayout(row)

        note = QtWidgets.QLabel("Not a real frame; a layout schematic.")
        note.setStyleSheet("color:#888; font-size:11px;")
        layout.addWidget(note)
        return box

    # -- list operations ---------------------------------------------------
    def _reload_preset_list(self, select: str = "") -> None:
        self._loading = True
        self.preset_list.clear()
        for preset in self.settings.presets:
            item = QtWidgets.QListWidgetItem(self._preset_label(preset))
            item.setData(QtCore.Qt.UserRole, preset.name)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            self.preset_list.addItem(item)
        self._loading = False

        names = self.settings.preset_names()
        row = names.index(select) if select in names else 0
        if names:
            self.preset_list.setCurrentRow(row)

    def _preset_label(self, preset) -> str:
        star = "* " if preset.name == self.settings.machine.default_preset else ""
        return star + preset.name

    @property
    def current_preset(self):
        item = self.preset_list.currentItem()
        if item is None:
            return None
        try:
            return self.settings.get(item.data(QtCore.Qt.UserRole))
        except wc_settings.SettingsError:
            return None

    def _on_preset_selected(self, row: int) -> None:
        preset = self.current_preset
        if preset is not None:
            self._load_preset(preset)

    def _on_preset_renamed(self, item) -> None:
        if self._loading:
            return
        old = item.data(QtCore.Qt.UserRole)
        new = item.text().lstrip("* ").strip()
        try:
            final = self.settings.rename(old, new)
        except wc_settings.SettingsError:
            return
        self._touch()
        self._reload_preset_list(select=final)

    def _preset_menu(self, point) -> None:
        item = self.preset_list.itemAt(point)
        if item is None:
            return
        menu = QtWidgets.QMenu(self)
        rename = menu.addAction("Rename...")
        make_default = menu.addAction("Make default *")
        action = menu.exec(self.preset_list.mapToGlobal(point))
        if action is rename:
            self._rename_preset(item)
        elif action is make_default:
            self.settings.set_default(item.data(QtCore.Qt.UserRole))
            self._touch()
            self._reload_preset_list(select=item.data(QtCore.Qt.UserRole))

    def _rename_preset(self, item=None) -> None:
        """Rename through a dialog.

        In-place editing in the list works too, but a dialog is the reliable
        route: it does not depend on the view's edit triggers or on the user
        discovering the double click.
        """
        if not isinstance(item, QtWidgets.QListWidgetItem):
            item = self.preset_list.currentItem()
        if item is None:
            return
        old = item.data(QtCore.Qt.UserRole)

        new, accepted = QtWidgets.QInputDialog.getText(
            self, "Rename preset", "New name:",
            QtWidgets.QLineEdit.Normal, old)
        if not accepted or not new.strip() or new.strip() == old:
            return

        final = self.settings.rename(old, new.strip())
        self._touch()
        self._reload_preset_list(select=final)

    def _add_preset(self) -> None:
        preset = self.settings.add(Preset(name="New preset"))
        self._touch()
        self._reload_preset_list(select=preset.name)

    def _duplicate_preset(self) -> None:
        preset = self.current_preset
        if preset is None:
            return
        copy = self.settings.duplicate(preset.name)
        self._touch()
        self._reload_preset_list(select=copy.name)

    def _delete_preset(self) -> None:
        preset = self.current_preset
        if preset is None:
            return
        confirm = QtWidgets.QMessageBox.question(
            self, "Delete preset", "Delete '%s'?" % preset.name)
        if confirm != QtWidgets.QMessageBox.Yes:
            return
        try:
            self.settings.remove(preset.name)
        except wc_settings.SettingsError as exc:
            QtWidgets.QMessageBox.warning(self, "Could not delete", str(exc))
            return
        self._touch()
        self._reload_preset_list()

    def _import_preset(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Import preset", "", "Preset (*.json)")
        if not path:
            return
        try:
            preset = wc_settings.import_preset(path)
        except (wc_settings.SettingsError, ValueError) as exc:
            QtWidgets.QMessageBox.warning(self, "Could not import", str(exc))
            return
        added = self.settings.add(preset)
        self._touch()
        self._reload_preset_list(select=added.name)

    def _export_preset(self) -> None:
        preset = self.current_preset
        if preset is None:
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Export preset", preset.name + ".json", "Preset (*.json)")
        if not path:
            return
        try:
            wc_settings.export_preset(preset, path)
            self.status.setText("Exported: %s" % path)
        except OSError as exc:
            QtWidgets.QMessageBox.warning(self, "Could not export", str(exc))

    # ================================================================ editor
    def _build_editor(self) -> QtWidgets.QWidget:
        self.editor = QtWidgets.QTabWidget()
        self.editor.addTab(self._tab_format(), "Format")
        self.editor.addTab(self._tab_colour(), "Colour")
        self.editor.addTab(self._tab_reformat(), "Reformat")
        self.editor.addTab(self._tab_burnin(), "Burn-in")
        self.editor.addTab(self._tab_output(), "Output")
        return self.editor

    # -- helpers -----------------------------------------------------------
    def _spin(self, low, high, value, slot):
        box = QtWidgets.QSpinBox()
        box.setRange(low, high)
        box.setValue(value)
        box.valueChanged.connect(lambda _: slot())
        return box

    def _dspin(self, low, high, value, step, slot):
        box = QtWidgets.QDoubleSpinBox()
        box.setRange(low, high)
        box.setSingleStep(step)
        box.setValue(value)
        box.valueChanged.connect(lambda _: slot())
        return box

    def _line(self, slot):
        edit = QtWidgets.QLineEdit()
        edit.editingFinished.connect(slot)      # not on every keystroke
        return edit

    @staticmethod
    def _note(text):
        label = QtWidgets.QLabel(text)
        label.setStyleSheet("color:#888; font-size:11px;")
        label.setWordWrap(True)
        return label

    # -- Format ------------------------------------------------------------
    def _tab_format(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.fmt_combo = QtWidgets.QComboBox()
        self.fmt_combo.addItem("H.264 / MP4", H264_MP4)
        self.fmt_combo.addItem("ProRes / MOV", PRORES_MOV)
        self.fmt_combo.currentIndexChanged.connect(self._on_format_changed)
        form.addRow("Codec", self.fmt_combo)

        self.crf_spin = self._spin(1, 51, 18, self._commit_format)
        form.addRow("CRF (H.264)", self.crf_spin)

        self.prores_combo = QtWidgets.QComboBox()
        for label, value in (("ProRes 422", "422"), ("ProRes LT", "lt"),
                             ("ProRes Proxy", "proxy")):
            self.prores_combo.addItem(label, value)
        self.prores_combo.currentIndexChanged.connect(self._commit_format)
        form.addRow("ProRes profile", self.prores_combo)

        form.addRow(self._note(
            "The output is silent. Rec709 tags (primaries / trc / colorspace) are "
            "written automatically for both formats."))
        return page

    def _on_format_changed(self):
        is_h264 = self.fmt_combo.currentData() == H264_MP4
        self.crf_spin.setEnabled(is_h264)
        self.prores_combo.setEnabled(not is_h264)
        self._commit_format()

    def _commit_format(self):
        preset = self.current_preset
        if preset is None or self._loading:
            return
        preset.output_format = self.fmt_combo.currentData()
        preset.crf = self.crf_spin.value()
        preset.prores_profile = self.prores_combo.currentData()
        self._touch()

    # -- Renk --------------------------------------------------------------
    def _tab_colour(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.ocio_macos = self._line(self._commit_colour)
        self.ocio_linux = self._line(self._commit_colour)
        form.addRow("OCIO config (macOS)", self._with_browse(self.ocio_macos))
        form.addRow("OCIO config (Linux)", self._with_browse(self.ocio_linux))

        export_btn = QtWidgets.QPushButton("Export the project's OCIO config...")
        export_btn.clicked.connect(self._export_project_ocio)
        form.addRow("", export_btn)

        self.cs_combo = QtWidgets.QComboBox()
        self.cs_combo.setEditable(True)
        self.cs_combo.currentTextChanged.connect(lambda _: self._commit_colour())
        form.addRow("Source colour space", self.cs_combo)

        self.display_combo = QtWidgets.QComboBox()
        self.display_combo.currentIndexChanged.connect(self._on_display_changed)
        form.addRow("Display", self.display_combo)

        self.view_combo = QtWidgets.QComboBox()
        self.view_combo.currentIndexChanged.connect(lambda _: self._commit_colour())
        form.addRow("View", self.view_combo)

        self.look_edit = self._line(self._commit_colour)
        form.addRow("Look (optional)", self.look_edit)

        reload_btn = QtWidgets.QPushButton("Reload config")
        reload_btn.clicked.connect(self._reload_ocio_lists)
        form.addRow("", reload_btn)

        self.colour_status = self._note("")
        form.addRow(self.colour_status)
        form.addRow(self._note(
            "Colour comes from this preset only; neither Flame's project setting "
            "nor the colour space reported by the hook is read.\n"
            "Note: the ACES 2.0 output transform is about 4.5x slower than ACES 1.3."))
        return page

    def _with_browse(self, edit):
        row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(edit, 1)
        button = QtWidgets.QPushButton("...")
        button.setFixedWidth(30)

        def browse():
            path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self, "Select OCIO config", "", "OCIO (*.ocio);;All files (*)")
            if path:
                edit.setText(path)
                self._commit_colour()
        button.clicked.connect(browse)
        layout.addWidget(button)
        return row

    def _reload_ocio_lists(self):
        preset = self.current_preset
        if preset is None:
            return
        spec = (preset.colour.config_macos if wc_platform.IS_MACOS
                else preset.colour.config_linux)
        try:
            cfg = wc_colour.load_config(spec)
        except wc_colour.ColourError as exc:
            self.colour_status.setText("! %s" % exc.args[0].splitlines()[0])
            return

        self._loading = True
        spaces = sorted({cs.getName() for cs in cfg.getColorSpaces()})
        self.cs_combo.clear()
        self.cs_combo.addItems(spaces)
        self.cs_combo.setCurrentText(preset.colour.source)

        displays = list(cfg.getDisplays())
        self.display_combo.clear()
        self.display_combo.addItems(displays)
        if preset.colour.display in displays:
            self.display_combo.setCurrentText(preset.colour.display)
        self._populate_views(cfg, preset.colour.view)
        self._loading = False

        self.colour_status.setText(
            "Config loaded: %d colour spaces, %d displays." % (len(spaces), len(displays)))

    def _populate_views(self, cfg, want: str):
        display = self.display_combo.currentText()
        views = list(cfg.getViews(display)) if display else []
        self.view_combo.clear()
        self.view_combo.addItems(views)
        if want in views:
            self.view_combo.setCurrentText(want)

    def _on_display_changed(self):
        if self._loading:
            return
        preset = self.current_preset
        if preset is None:
            return
        spec = (preset.colour.config_macos if wc_platform.IS_MACOS
                else preset.colour.config_linux)
        try:
            cfg = wc_colour.load_config(spec)
        except wc_colour.ColourError:
            return
        self._loading = True
        self._populate_views(cfg, preset.colour.view)
        self._loading = False
        self._commit_colour()

    def _commit_colour(self):
        preset = self.current_preset
        if preset is None or self._loading:
            return
        preset.colour.config_macos = self.ocio_macos.text().strip()
        preset.colour.config_linux = self.ocio_linux.text().strip()
        preset.colour.source = self.cs_combo.currentText().strip()
        preset.colour.display = self.display_combo.currentText().strip()
        preset.colour.view = self.view_combo.currentText().strip()
        preset.colour.look = self.look_edit.text().strip()
        self._touch()

    def _export_project_ocio(self):
        """Write the project config to disk and fill in this platform's field."""
        try:
            import flame
        except Exception:
            QtWidgets.QMessageBox.information(
                self, "No Flame",
                "This button only works inside Flame.")
            return

        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Where should the config be written?", os.path.expanduser("~"))
        if not folder:
            return
        try:
            project = flame.project.current_project
            project.export_ocio_config(str(project.name), folder, False, True, False)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, "Could not export", str(exc))
            return

        written = ""
        for name in sorted(os.listdir(folder)):
            if name.endswith(".ocio"):
                written = os.path.join(folder, name)
                break
        if not written:
            QtWidgets.QMessageBox.warning(
                self, "Not found",
                "The config was written but no .ocio file is visible in %s." % folder)
            return

        (self.ocio_macos if wc_platform.IS_MACOS else self.ocio_linux).setText(written)
        self._commit_colour()
        self._reload_ocio_lists()

    # -- Reformat ----------------------------------------------------------
    def _tab_reformat(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.canvas_combo = QtWidgets.QComboBox()
        for label, size in CANVAS_PRESETS:
            self.canvas_combo.addItem(label, size)
        self.canvas_combo.currentIndexChanged.connect(self._on_canvas_changed)
        form.addRow("Canvas", self.canvas_combo)

        size_row = QtWidgets.QWidget()
        size_layout = QtWidgets.QHBoxLayout(size_row)
        size_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas_w = self._spin(16, 30000, 1920, self._commit_reformat)
        self.canvas_h = self._spin(16, 30000, 1080, self._commit_reformat)
        size_layout.addWidget(self.canvas_w)
        size_layout.addWidget(QtWidgets.QLabel("x"))
        size_layout.addWidget(self.canvas_h)
        size_layout.addStretch(1)
        form.addRow("Custom size", size_row)

        self.fit_combo = QtWidgets.QComboBox()
        for label, value in FIT_LABELS:
            self.fit_combo.addItem(label, value)
        self.fit_combo.currentIndexChanged.connect(self._commit_reformat)
        form.addRow("Fit", self.fit_combo)

        self.crop_l = self._spin(0, 30000, 0, self._commit_reformat)
        self.crop_r = self._spin(0, 30000, 0, self._commit_reformat)
        self.crop_t = self._spin(0, 30000, 0, self._commit_reformat)
        self.crop_b = self._spin(0, 30000, 0, self._commit_reformat)
        form.addRow("Crop left / right", self._pair(self.crop_l, self.crop_r))
        form.addRow("Crop top / bottom", self._pair(self.crop_t, self.crop_b))

        self.shift_x = self._spin(-30000, 30000, 0, self._commit_reformat)
        self.shift_y = self._spin(-30000, 30000, 0, self._commit_reformat)
        form.addRow("Shift X / Y", self._pair(self.shift_x, self.shift_y))

        self.bands_check = QtWidgets.QCheckBox("Use the band colour")
        self.bands_check.toggled.connect(lambda _: self._commit_reformat())
        form.addRow("", self.bands_check)

        self.band_colour = self._line(self._commit_reformat)
        self.band_colour.setPlaceholderText("black, #101010, ...")
        form.addRow("Band colour", self.band_colour)

        form.addRow(self._note(
            "Crop and shift are in SOURCE pixels. If the crop is larger than the "
            "source the job does not start; the error goes to the log and to Flame."))
        return page

    def _pair(self, a, b):
        row = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(a)
        layout.addWidget(b)
        layout.addStretch(1)
        return row

    def _on_canvas_changed(self):
        size = self.canvas_combo.currentData()
        custom = size is None
        self.canvas_w.setEnabled(custom)
        self.canvas_h.setEnabled(custom)
        if size is not None:
            self._loading_guard(lambda: (self.canvas_w.setValue(size[0]),
                                         self.canvas_h.setValue(size[1])))
        self._commit_reformat()

    def _loading_guard(self, fn):
        was = self._loading
        self._loading = True
        try:
            fn()
        finally:
            self._loading = was

    def _commit_reformat(self):
        preset = self.current_preset
        if preset is None or self._loading:
            return
        r = preset.reformat
        r.canvas_width = self.canvas_w.value()
        r.canvas_height = self.canvas_h.value()
        r.fit_mode = self.fit_combo.currentData()
        r.crop_left, r.crop_right = self.crop_l.value(), self.crop_r.value()
        r.crop_top, r.crop_bottom = self.crop_t.value(), self.crop_b.value()
        r.shift_x, r.shift_y = self.shift_x.value(), self.shift_y.value()
        r.bands_enabled = self.bands_check.isChecked()
        r.band_colour = self.band_colour.text().strip() or "black"
        self._touch()

    # -- Burn-in -----------------------------------------------------------
    def _tab_burnin(self):
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)

        grid = QtWidgets.QGridLayout()
        self.zone_edits = {}
        for index, (zone, label) in enumerate(ZONE_LABELS):
            edit = self._line(self._commit_burnin)
            # Remember the last zone field that had focus, so a token still has
            # a target even if focus moved elsewhere in the meantime.
            edit.installEventFilter(self)
            self.zone_edits[zone] = edit
            grid.addWidget(QtWidgets.QLabel(label), index // 3 * 2, index % 3)
            grid.addWidget(edit, index // 3 * 2 + 1, index % 3)
        layout.addLayout(grid)

        layout.addWidget(self._note("Click to insert a token "
                                    "(it goes into the last field you used):"))
        tokens = QtWidgets.QHBoxLayout()
        tokens.setSpacing(4)
        wrap = QtWidgets.QWidget()
        flow = QtWidgets.QGridLayout(wrap)
        flow.setContentsMargins(0, 0, 0, 0)
        for i, token in enumerate(known_tokens()):
            button = QtWidgets.QPushButton(token)
            button.setStyleSheet("font-size:11px; padding:2px 6px;")
            # Do NOT let the button take focus: the caret must stay in the zone
            # field the user was editing, otherwise the token has nowhere to go.
            button.setFocusPolicy(QtCore.Qt.NoFocus)
            button.clicked.connect(lambda _=False, t=token: self._insert_token(t))
            flow.addWidget(button, i // 4, i % 4)
        tokens.addWidget(wrap)
        layout.addLayout(tokens)

        form = QtWidgets.QFormLayout()
        self.font_pct = self._dspin(0.5, 20.0, 2.5, 0.1, self._commit_burnin)
        self.margin_pct = self._dspin(0.0, 20.0, 2.0, 0.1, self._commit_burnin)
        self.box_check = QtWidgets.QCheckBox("Semi-transparent background box")
        self.box_check.toggled.connect(lambda _: self._commit_burnin())
        self.box_opacity = self._dspin(0.0, 1.0, 0.5, 0.05, self._commit_burnin)
        self.text_colour = self._line(self._commit_burnin)
        form.addRow("Text size (% of canvas height)", self.font_pct)
        form.addRow("Margin (% of canvas height)", self.margin_pct)
        form.addRow("", self.box_check)
        form.addRow("Box opacity", self.box_opacity)
        form.addRow("Text colour", self.text_colour)
        layout.addLayout(form)

        layout.addWidget(self._note(
            "Burn-in sits a fixed distance from the canvas edge; the presence of "
            "black bands does not move it. The text is drawn with Qt, so ffmpeg "
            "drawtext is not required."))
        layout.addStretch(1)
        return page

    def eventFilter(self, obj, event):
        """Track which burn-in field was last focused (for token insertion)."""
        if event.type() == QtCore.QEvent.FocusIn and obj in self.zone_edits.values():
            self._last_zone_edit = obj
        return super().eventFilter(obj, event)

    def _insert_token(self, token: str) -> None:
        """Insert a token at the caret of the burn-in field being edited.

        The token buttons have NoFocus, so the field normally still holds focus
        and `focusWidget()` finds it. `_last_zone_edit` covers the case where
        focus went somewhere else; if neither applies we fall back to the first
        field rather than refusing to do anything.
        """
        target = QtWidgets.QApplication.focusWidget()
        if target not in self.zone_edits.values():
            target = getattr(self, "_last_zone_edit", None)
        if target is None:
            target = self.zone_edits[ZONE_LABELS[0][0]]
            target.setFocus()

        target.insert(token)
        self._last_zone_edit = target
        self._commit_burnin()

    def _commit_burnin(self):
        preset = self.current_preset
        if preset is None or self._loading:
            return
        b = preset.burnin
        b.zones = {zone: edit.text() for zone, edit in self.zone_edits.items()
                   if edit.text().strip()}
        b.font_size_pct = self.font_pct.value()
        b.margin_pct = self.margin_pct.value()
        b.box = self.box_check.isChecked()
        b.box_opacity = self.box_opacity.value()
        b.colour = self.text_colour.text().strip() or "#FFFFFF"
        self._touch()

    # -- Output -------------------------------------------------------------
    def _tab_output(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.template_edit = self._line(self._commit_output)
        form.addRow("Path template", self.template_edit)
        self.template_example = self._note("")
        form.addRow("Example", self.template_example)

        form.addRow(self._note(
            "Tokens: {source_dir}, {source_name}. The extension comes from the "
            "format.\nOn a name collision _repeat, _repeat2 ... is appended; no "
            "file is ever deleted or overwritten."))
        return page

    def _commit_output(self):
        preset = self.current_preset
        if preset is None or self._loading:
            return
        preset.output_template = self.template_edit.text().strip()
        self._update_template_example()
        self._touch()

    def _update_template_example(self):
        # bundled: from .. import output as wc_output
        preset = self.current_preset
        if preset is None:
            return
        try:
            example = wc_output.resolve_template(
                preset.output_template, "/jobs/show/shot/exr", "shot_comp_v003",
                preset.extension)
        except wc_output.OutputError as exc:
            self.template_example.setText("! %s" % exc)
            return
        self.template_example.setText(example)

    # =============================================================== general
    def _build_general_tab(self):
        page = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(page)

        self.auto_check = QtWidgets.QCheckBox(
            "Create a review automatically when a Write File render finishes")
        self.auto_check.toggled.connect(lambda _: self._commit_general())
        form.addRow("", self.auto_check)

        self.ffmpeg_edit = self._line(self._commit_general)
        self.ffprobe_edit = self._line(self._commit_general)
        form.addRow("ffmpeg path", self.ffmpeg_edit)
        form.addRow("ffprobe path", self.ffprobe_edit)

        find_btn = QtWidgets.QPushButton("Find on PATH")
        find_btn.clicked.connect(self._find_tools)
        form.addRow("", find_btn)

        self.logdir_edit = self._line(self._commit_general)
        form.addRow("Log directory", self.logdir_edit)
        open_log = QtWidgets.QPushButton("Open log")
        open_log.clicked.connect(self._open_log)
        form.addRow("", open_log)

        self.threads_spin = self._spin(0, 128, 0, self._commit_general)
        self.threads_spin.setSpecialValueText("automatic")
        form.addRow("OCIO threads", self.threads_spin)

        self.general_status = self._note("")
        form.addRow("Status", self.general_status)
        form.addRow(self._note(
            "The settings on this tab are machine-specific and are NEVER included "
            "in a preset export."))
        return page

    def _commit_general(self):
        if self._loading:
            return
        machine = self.settings.machine
        machine.auto_trigger = self.auto_check.isChecked()
        machine.ffmpeg = self.ffmpeg_edit.text().strip() or "ffmpeg"
        machine.ffprobe = self.ffprobe_edit.text().strip() or "ffprobe"
        machine.log_dir = self.logdir_edit.text().strip() or wc_platform.default_log_dir()
        machine.ocio_threads = self.threads_spin.value()
        self._touch()

    def _find_tools(self):
        self.ffmpeg_edit.setText(wc_platform.find_tool("ffmpeg"))
        self.ffprobe_edit.setText(wc_platform.find_tool("ffprobe"))
        self._commit_general()
        self._load_general_status()

    def _open_log(self):
        import subprocess
        path = self.engine.notifier.log_path
        if not os.path.exists(path):
            self.status.setText("No log written yet: %s" % path)
            return
        subprocess.Popen(["open" if wc_platform.IS_MACOS else "xdg-open", path])

    def _load_general(self):
        self._loading = True
        machine = self.settings.machine
        self.auto_check.setChecked(machine.auto_trigger)
        self.ffmpeg_edit.setText(machine.ffmpeg)
        self.ffprobe_edit.setText(machine.ffprobe)
        self.logdir_edit.setText(machine.log_dir)
        self.threads_spin.setValue(machine.ocio_threads)
        self._loading = False
        self._load_general_status()

    def _load_general_status(self):
        import subprocess
        bits = []
        try:
            out = subprocess.run([self.settings.machine.ffmpeg, "-version"],
                                 capture_output=True, text=True, timeout=5)
            bits.append(out.stdout.splitlines()[0][:60] if out.stdout
                        else "ffmpeg did not respond")
        except Exception:
            bits.append("! ffmpeg not found")
        try:
            import PyOpenColorIO as ocio
            bits.append("PyOpenColorIO %s" % ocio.__version__)
        except Exception:
            bits.append("! PyOpenColorIO missing")
        try:
            import numpy
            bits.append("numpy %s" % numpy.__version__)
        except Exception:
            bits.append("! numpy missing")
        bits.append("%d cores" % (os.cpu_count() or 0))
        bits.append("default preset: %s" % self.settings.machine.default_preset)
        self.general_status.setText("\n".join(bits))

    # ================================================================ loading
    def _load_preset(self, preset):
        self._loading = True

        index = self.fmt_combo.findData(preset.output_format)
        self.fmt_combo.setCurrentIndex(max(0, index))
        self.crf_spin.setValue(preset.crf)
        index = self.prores_combo.findData(preset.prores_profile)
        self.prores_combo.setCurrentIndex(max(0, index))
        is_h264 = preset.output_format == H264_MP4
        self.crf_spin.setEnabled(is_h264)
        self.prores_combo.setEnabled(not is_h264)

        self.ocio_macos.setText(preset.colour.config_macos)
        self.ocio_linux.setText(preset.colour.config_linux)
        self.look_edit.setText(preset.colour.look)

        r = preset.reformat
        size = (r.canvas_width, r.canvas_height)
        index = next((i for i, (_, s) in enumerate(CANVAS_PRESETS) if s == size),
                     len(CANVAS_PRESETS) - 1)
        self.canvas_combo.setCurrentIndex(index)
        self.canvas_w.setValue(r.canvas_width)
        self.canvas_h.setValue(r.canvas_height)
        custom = CANVAS_PRESETS[index][1] is None
        self.canvas_w.setEnabled(custom)
        self.canvas_h.setEnabled(custom)
        self.fit_combo.setCurrentIndex(max(0, self.fit_combo.findData(r.fit_mode)))
        self.crop_l.setValue(r.crop_left)
        self.crop_r.setValue(r.crop_right)
        self.crop_t.setValue(r.crop_top)
        self.crop_b.setValue(r.crop_bottom)
        self.shift_x.setValue(r.shift_x)
        self.shift_y.setValue(r.shift_y)
        self.bands_check.setChecked(r.bands_enabled)
        self.band_colour.setText(r.band_colour)

        b = preset.burnin
        for zone, edit in self.zone_edits.items():
            edit.setText(b.zones.get(zone, ""))
        self.font_pct.setValue(b.font_size_pct)
        self.margin_pct.setValue(b.margin_pct)
        self.box_check.setChecked(b.box)
        self.box_opacity.setValue(b.box_opacity)
        self.text_colour.setText(b.colour)

        self.template_edit.setText(preset.output_template)

        self._loading = False
        self._reload_ocio_lists()
        self._update_template_example()
        self._refresh_preview()

    def _refresh_preview(self):
        preset = self.current_preset
        if preset is None:
            return
        self.preview.update_from(preset, (self.preview_w.value(),
                                          self.preview_h.value()))



# ==========================================================================
#  Engine - single instance
# ==========================================================================
_engine = None


class _Engine:
    """Settings + queue + notifier. Retired when the module is re-imported."""

    def __init__(self):
        try:
            self.settings = load()
        except SettingsError as exc:
            self.settings = Settings()
            self._boot_error = str(exc)
        else:
            self._boot_error = ""

        self.version = SCRIPT_VERSION
        self.script_name = SCRIPT_NAME
        self.credit = SCRIPT
        self.notifier = Notifier(self.settings.machine.log_dir)
        self._resolve_tools()
        self.queue = JobQueue(machine=self.settings.machine, notify=self.notifier)

        self._verify_tools()

        if self._boot_error:
            self.notifier("error", "Could not read the settings file, using "
                                   "defaults: %s" % self._boot_error)
        self.notifier("info", "%s %s loaded (%s). Log: %s"
                      % (SCRIPT_NAME, VERSION, describe_path(),
                         self.notifier.log_path))

    def _resolve_tools(self) -> None:
        """Flame's PATH may differ from the user's shell (see find_tool)."""
        machine = self.settings.machine
        machine.ffmpeg = find_tool("ffmpeg", machine.ffmpeg)
        machine.ffprobe = find_tool("ffprobe", machine.ffprobe)

    def _verify_tools(self) -> None:
        """Warn once, at startup, if ffmpeg is missing.

        Without this the first render fails somewhere inside the pipeline with a
        message that does not name the real cause.
        """
        machine = self.settings.machine
        missing = []
        for label, path in (("ffmpeg", machine.ffmpeg), ("ffprobe", machine.ffprobe)):
            try:
                subprocess.run([path, "-version"], capture_output=True, timeout=10)
            except Exception:
                missing.append(label)

        if not missing:
            return

        message = ("%s not found. Set the full path in Settings -> General, or "
                   "install it (macOS: brew install ffmpeg, Rocky: dnf install "
                   "ffmpeg)." % " and ".join(missing))
        self.notifier("error", message)
        self.notifier.dialog("%s: missing tool" % SCRIPT_NAME, message)

    def reload_settings(self) -> None:
        self.settings = load()
        self._resolve_tools()
        self.queue.machine = self.settings.machine
        self.notifier.log_dir = self.settings.machine.log_dir

    def shutdown(self) -> None:
        """On Flame shutdown: cancel the running job, remove the half file."""
        try:
            self.notifier("info", "Flame is quitting, draining the queue.")
            self.queue.shutdown(timeout=10)
        except Exception:
            pass


def engine():
    global _engine
    if _engine is None:
        _engine = _Engine()
        _install_quit_handler()
    return _engine


def _install_quit_handler() -> None:
    """Flame has NO shutdown hook; connect to the Qt signal instead."""
    try:
        from PySide6 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is not None:
            app.aboutToQuit.connect(lambda: _engine and _engine.shutdown())
    except Exception:
        pass


def _retire_previous() -> None:
    """'Refresh Python Hooks' re-imports this file; shut the old queue down.

    Without this every refresh stacks another queue and jobs run twice.
    """
    previous = sys.modules.get(__name__)
    old = getattr(previous, "_engine", None) if previous else None
    if old is not None and old is not _engine:
        try:
            old.queue.shutdown(timeout=5)
        except Exception:
            pass


# ==========================================================================
#  Render completion hook
# ==========================================================================
def batch_export_end(info, userData, *args, **kwargs):
    """A Write File render finished. ONLY this name is defined - see the header."""
    try:
        eng = engine()
        if not eng.settings.machine.auto_trigger:
            return

        if is_aborted(info):
            # 3.7: an aborted render is not converted, just noted in the log.
            eng.notifier("info", "Render was aborted, no review created: %s"
                         % info.get("nodeName", "?"))
            return

        eng.notifier("debug", "batch_export_end: " + describe(info))
        preset = eng.settings.default_preset()
        eng.queue.submit(build(info, preset))     # flame.* here, on the main thread

    except Exception as exc:                       # noqa: BLE001
        _report_failure("Could not start the automatic review", exc)


# ==========================================================================
#  Right click / menu actions
# ==========================================================================
def _selected_write_nodes(selection):
    nodes = []
    if flame is None:
        return nodes
    for item in (selection or []):
        if isinstance(item, getattr(flame, "PyWriteFileNode", ())):
            nodes.append(item)
    return nodes


def _scope_write_node(selection) -> bool:
    return bool(_selected_write_nodes(selection))


def _make_review(selection):
    """Right click -> Create review. There is no hook `info`; the path comes
    from the node itself."""
    try:
        eng = engine()
        nodes = _selected_write_nodes(selection)
        if not nodes:
            eng.notifier("warning", "No Write File node selected.")
            return

        preset = eng.settings.default_preset()
        for node in nodes:
            try:
                resolved = node.get_resolved_media_path()
            except Exception as exc:
                eng.notifier("error", "Could not read the node path (%s): %s"
                             % (getattr(node, "name", "?"), exc))
                continue

            info = {"resolvedPath": str(resolved),
                    "nodeName": str(_attr(node, "name", "")),
                    "fps": str(_attr(node, "frame_rate", "25")),
                    "shotName": str(_attr(node, "shot_name", ""))}
            eng.notifier("debug", "manual: " + describe(info))
            eng.queue.submit(build(info, preset, node=node))

    except Exception as exc:                       # noqa: BLE001
        _report_failure("Could not create the review", exc)


def _open_settings(*args, **kwargs):
    try:
        show(engine())
    except Exception as exc:                       # noqa: BLE001
        _report_failure("Could not open the settings window", exc)


def _open_log(*args, **kwargs):
    try:
        eng = engine()
        path = eng.notifier.log_path
        if not os.path.exists(path):
            eng.notifier("info", "No log written yet: %s" % path)
            return
        subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])
    except Exception as exc:                       # noqa: BLE001
        _report_failure("Could not open the log", exc)


def _report_failure(title: str, exc: Exception) -> None:
    detail = "%s: %s" % (type(exc).__name__, exc)
    try:
        eng = _engine
        if eng is not None:
            eng.notifier("error", "%s - %s" % (title, detail))
            eng.notifier("debug", traceback.format_exc())
            return
    except Exception:
        pass
    print("WriteConvert ERROR: %s - %s\n%s" % (title, detail, traceback.format_exc()))


# ==========================================================================
#  Menus  (structure verified against working Flame tools)
# ==========================================================================
def get_batch_custom_ui_actions():
    return [{
        "name": SCRIPT_NAME,
        "actions": [
            {"name": "Create review...", "isVisible": _scope_write_node,
             "execute": _make_review, "minimumVersion": "2026"},
            {"name": "Settings...", "execute": _open_settings,
             "minimumVersion": "2026"},
        ]}]


def get_main_menu_custom_ui_actions():
    return [{
        "name": SCRIPT_NAME,
        "actions": [
            {"name": "Settings...", "execute": _open_settings,
             "minimumVersion": "2026"},
            {"name": "Open log", "execute": _open_log, "minimumVersion": "2026"},
        ]}]


# ==========================================================================
#  On import
# ==========================================================================
_retire_previous()
