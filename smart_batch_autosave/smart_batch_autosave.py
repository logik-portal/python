# -*- coding: utf-8 -*-
"""
Script Name: Smart Batch Autosave
Script Version: 1.0.2
Flame Version: 2026.2
Written by: Huseyin Pasaoglu
Creation Date: 07.20.26
Update Date: 07.28.26

Description:

    Background auto-save engine for Batch setups with a PySide6 settings UI.

    Silently backs up the current Batch setup on a configurable interval
    (1-60 min) using flame.batch.save_setup() — the project itself is never
    touched. Each Batch group gets its own subfolder and a rotation policy
    keeps the 10 most recent scheduled backups (manual and post-render
    snapshots are always preserved). Extra triggers: a one-shot idle backup
    when the artist steps away, a forced backup after every Batch render,
    and a manual "Snapshot Now" button.

    BatchFX aware: when the artist is inside a BFX (detected via
    flame.get_current_tab()), the backup is routed to a separate
    _BatchFX/<name> tree so it can never overwrite a desktop batch's backups.

    Crash-safe: all saves are deferred through flame.schedule_idle_event(),
    so save_setup() never fires in the middle of an Archive restore, media
    cache or render. A "Pause Auto-Save" button suspends all automatic saves
    (auto-resumes on next launch).

    The backup destination is fully configurable with tokenized path
    templates (<project>, <user>, <batch>). Settings persist to a JSON file
    next to the script.

    Install: copy this file to /opt/Autodesk/shared/python/ and restart
    Flame or refresh python hooks. The engine starts automatically.

Menus:

    Flame Main Menu -> Smart Batch Auto-Save -> Smart Batch Auto-Save Settings

Updates:

    v1.0.2 07.28.26
    - Crash fix: automatic saves and manual snapshots now run via
      flame.schedule_idle_event() instead of straight from the timer, so
      save_setup() can no longer fire mid Archive restore / media cache /
      render (the cause of "Pure virtual function called" SIGABRT crashes).

    v1.0.1 07.24.26
    - BatchFX aware: the active BFX is saved into its own _BatchFX/<name>
      tree, resolved via flame.get_current_tab(), protecting desktop batch
      backups from being overwritten or rotated out.
    - Added "Pause Auto-Save" button (runtime-only, auto-resumes on
      relaunch) for use before Archives / heavy imports / renders.
    - Added settings window footer with credit.

    v1.0.0 07.20.26
    - Initial release: interval + idle + post-render autosave, per-batch
      folders, retention (keep 10), never-forget retry, editable path
      templates, singleton engine with reload-safe reset.
"""

# ==============================================================================
#  DESIGN NOTES  (read these — they matter in production)
# ------------------------------------------------------------------------------
#  * ALL flame.* calls MUST run on Flame's main (Qt GUI) thread. A
#    `threading.Timer` fires on a worker thread and calling the Flame API from
#    there can hard-crash the application. We therefore drive the interval with
#    a QTimer, which always fires on the GUI thread. This is the single most
#    important safety decision in the whole script.
#  * The monitor is a strict Singleton so repeatedly opening/closing the UI can
#    never spawn a second timer.
#  * Every Flame API touch is wrapped defensively; the API surface differs
#    slightly across 2026 -> 2027, so we feature-detect instead of assuming.
#  * Saves are queued through flame.schedule_idle_event() so they only run
#    when Flame's main loop is genuinely idle — never mid archive/cache/render.
# ==============================================================================

from __future__ import annotations

import os
import re
import json
import shutil
import traceback
from datetime import datetime

# ------------------------------------------------------------------------------
#  Flame API — imported lazily / defensively so the module can also be linted
#  or unit-imported outside of Flame without exploding.
# ------------------------------------------------------------------------------
try:
    import flame  # noqa: F401  (provided by the Flame runtime)
    _HAS_FLAME = True
except Exception:  # pragma: no cover - only true outside Flame
    flame = None
    _HAS_FLAME = False

# ------------------------------------------------------------------------------
#  PySide6 ONLY.  We intentionally do not fall back to PySide2.
# ------------------------------------------------------------------------------
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt, QObject, QTimer, QEvent


# ==============================================================================
#  Constants
# ==============================================================================
SCRIPT_NAME    = "Smart Batch Auto-Save"
SCRIPT_VERSION = "1.0.2"
LOG_PREFIX     = "[Smart Auto-Save]"

# Credit shown in the settings window footer.
SCRIPT = "huseyinpasaoglu"

# Config file lives next to this script so it travels with the install and is
# writable by the artist. Override with $SMART_AUTOSAVE_CONFIG if desired.
_THIS_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH  = os.environ.get(
    "SMART_AUTOSAVE_CONFIG",
    os.path.join(_THIS_DIR, "smart_autosave_config.json"),
)

# Fixed sub-folder appended to every resolved backup path.
LEAF_FOLDER  = "Batch_Autosaves"

# --- User-editable path template -------------------------------------------
# Everything AFTER the Target Base Directory is driven by this template. The
# artist can freely retype it. Tokens (case / space / underscore insensitive):
#     <project>  -> Project Name field
#     <user>     -> User Name field
#     <batch>    -> active Batch group name (keep this last for per-batch
#                   isolation + working retention)
# Any other text is treated as a literal folder name. Forward slashes separate
# folders. Unknown <tokens> are left as literal text.
DEFAULT_PATH_TEMPLATE = "<project>/<user>/Batch_Autosaves/<batch>"

# BatchFX gets its OWN template so BFX backups never nest under (or get
# confused with) a desktop batch's folder. Here <batch> resolves to the BFX's
# own name, NOT the desktop batch name.
DEFAULT_BFX_PATH_TEMPLATE = "<project>/<user>/Batch_Autosaves/_BatchFX/<batch>"

# Canonical token names + accepted aliases (normalized: lower, no space/_/-).
_TOKEN_ALIASES = {
    "project": "project", "projectname": "project", "proj": "project",
    "user": "user", "username": "user", "artist": "user",
    "batch": "batch", "batchname": "batch", "shot": "batch",
}

# Retention: how many *scheduled* autosaves to keep per Batch subfolder.
# Manual + post-render milestones are EXEMPT and never counted or deleted.
MAX_SCHEDULED_BACKUPS = 10

# Short-term "never forget" retry cadence (ms) used when a scheduled save is
# deferred because Flame is playing back / rendering.
RETRY_INTERVAL_MS = 8000  # 8 seconds

# How often (ms) the idle watchdog polls when "Idle Auto-Save" is enabled.
IDLE_POLL_MS = 15000  # 15 seconds

# Fixed Qt objectName used to locate / retire a previous monitor instance
# across "Refresh Python Hooks" reloads (Singleton must survive re-import).
MON_OBJECT_NAME = "SmartBatchAutoSaveMonitor__singleton"

# Filename suffixes that mark protected milestones (excluded from rotation).
PROTECTED_SUFFIXES = ("_manual", "_post_render")

# Sensible cross-facility default root; the artist will normally repoint this.
DEFAULT_BASE_DIR = os.path.expanduser("~/flame_batch_autosaves")

DEFAULT_CONFIG = {
    "base_dir":          DEFAULT_BASE_DIR,
    "path_template":     DEFAULT_PATH_TEMPLATE,
    "bfx_path_template": DEFAULT_BFX_PATH_TEMPLATE,
    "project_name":    "",
    "user_name":       "",
    "interval_min":    10,      # 1..60
    "idle_enabled":    False,
    "idle_min":        5,       # trigger only after N idle minutes
    "enabled":         True,    # master on/off for the interval engine
    # What to do when the artist is inside a BatchFX (see BFX_MODES):
    #   "separate" -> back the BFX up into its own subfolder (recommended)
    #   "skip"     -> take no automatic save at all while in BFX
    #   "off"      -> no special handling (UNSAFE: BFX overwrites shot backups)
    "bfx_mode":        "separate",
}

# Valid values for cfg["bfx_mode"], in UI display order.
BFX_MODES = ("separate", "skip", "off")

# Filename marker inserted for BatchFX saves, e.g. NAME_20260724_1200_bfx.batch
BFX_SUFFIX = "_bfx"


# ==============================================================================
#  Small logging helper — everything lands in the Flame Python Console.
# ==============================================================================
def _log(msg: str) -> None:
    print(f"{LOG_PREFIX} {msg}")


def _log_exc(context: str) -> None:
    """Log an exception with a full traceback but never re-raise."""
    print(f"{LOG_PREFIX} ERROR during {context}:")
    print(traceback.format_exc())


# ==============================================================================
#  Config persistence
# ==============================================================================
def load_config() -> dict:
    """Load config JSON, merged over defaults so new keys always exist."""
    cfg = dict(DEFAULT_CONFIG)
    try:
        if os.path.isfile(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                cfg.update({k: data[k] for k in data if k in DEFAULT_CONFIG})

                # Migrate the older boolean key to the newer tri-state mode.
                # bfx_guard False meant "no special BatchFX handling".
                if "bfx_mode" not in data and "bfx_guard" in data:
                    cfg["bfx_mode"] = "separate" if data["bfx_guard"] else "off"

        # Never let a bad/hand-edited value through.
        if cfg.get("bfx_mode") not in BFX_MODES:
            cfg["bfx_mode"] = DEFAULT_CONFIG["bfx_mode"]
    except Exception:
        _log_exc("load_config")
    return cfg


def save_config(cfg: dict) -> None:
    """Persist config JSON atomically-ish (write temp, then replace)."""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=4, sort_keys=True)
        os.replace(tmp, CONFIG_PATH)
        _log(f"Config saved -> {CONFIG_PATH}")
    except Exception:
        _log_exc("save_config")


# ==============================================================================
#  Flame API convenience wrappers (all defensive / version-tolerant)
# ==============================================================================
def flame_current_project_name() -> str:
    if not _HAS_FLAME:
        return ""
    try:
        return str(flame.project.current_project.name)
    except Exception:
        _log_exc("flame_current_project_name")
        return ""


def flame_current_user_name() -> str:
    if not _HAS_FLAME:
        return ""
    try:
        return str(flame.users.current_user.name)
    except Exception:
        _log_exc("flame_current_user_name")
        return ""


def _bfx_name_candidates() -> list:
    """
    Collect every plausible source for the CURRENT BatchFX's own name.

    Returns a list of (source_label, value) with unusable entries dropped.

    WHY A CHAIN
    -----------
    `flame.batch.name` returns the DESKTOP batch's name while inside a BFX
    (verified: desktop batch 'NTFLX_101_..._0010' 143 nodes vs BFX 3 nodes, same
    name), so it is useless for naming a BFX. An API probe run from a MENU
    click showed every flame.timeline.* member as None — but the autosave runs
    from a QTimer, where the timeline context may well be live. We therefore
    try all known sources and log which one won.

    NOTE: dir() is incomplete on Flame PyObjects (e.g. it never lists `name`
    even though it works), so guess-and-test is the only reliable approach.
    """
    out = []
    if not _HAS_FLAME:
        return out

    def _add(label, obj):
        try:
            if obj is None:
                return
            val = str(getattr(obj, "name", "") or "").strip()
            if val:
                out.append((label, val))
        except Exception:
            pass

    # 1) The clip currently loaded in the timeline — most likely source.
    try:
        tl = getattr(flame, "timeline", None)
        if tl is not None:
            _add("timeline.clip", getattr(tl, "clip", None))
            _add("timeline.current_segment", getattr(tl, "current_segment", None))
            _add("timeline.current_effect", getattr(tl, "current_effect", None))
    except Exception:
        pass

    # 2) Media panel selection — but only if it is NOT the desktop PyBatch,
    #    which is what it reports when a batch group is selected.
    try:
        sel = getattr(getattr(flame, "media_panel", None),
                      "selected_entries", None) or []
        for item in sel:
            if type(item).__name__ != "PyBatch":
                _add(f"media_panel.selected[{type(item).__name__}]", item)
    except Exception:
        pass

    # 3) A clip-ish node inside the BFX graph (the BFX source often carries
    #    the segment's clip name).
    try:
        for node in (getattr(flame.batch, "nodes", None) or []):
            tname = type(node).__name__
            if "Clip" in tname or "Source" in tname:
                _add(f"batch.node[{tname}]", node)
    except Exception:
        pass

    return out


def flame_bfx_name() -> str:
    """
    Best-effort name for the active BatchFX, or "" if none could be resolved.
    Logs the full candidate list when resolution fails so the real source can
    be identified from a live session.
    """
    cands = _bfx_name_candidates()
    if cands:
        label, value = cands[0]
        _log(f"BFX name resolved from {label}: '{value}'")
        return _sanitize(value)

    # Nothing resolved — dump diagnostics so we can find the right source.
    _log("BFX name NOT resolved. Diagnostics:")
    try:
        tl = getattr(flame, "timeline", None)
        _log(f"    timeline={type(tl).__name__ if tl else None} "
             f"clip={getattr(tl, 'clip', None)} "
             f"seg={getattr(tl, 'current_segment', None)} "
             f"fx={getattr(tl, 'current_effect', None)}")
        nodes = getattr(flame.batch, "nodes", None) or []
        _log(f"    batch nodes ({len(nodes)}): "
             f"{[(type(n).__name__, str(getattr(n, 'name', '?'))) for n in nodes][:8]}")
        sel = getattr(getattr(flame, "media_panel", None),
                      "selected_entries", None) or []
        _log(f"    selection: {[(type(s).__name__, str(getattr(s, 'name', '?'))) for s in sel]}")
        _log(f"    batch.contexts = {getattr(flame.batch, 'contexts', None)}")
    except Exception:
        _log_exc("flame_bfx_name diagnostics")
    return ""


def flame_current_batch_name() -> str:
    """Best-effort current Batch name; falls back to 'batch'."""
    if not _HAS_FLAME:
        return "batch"
    try:
        name = getattr(flame.batch, "name", None)
        # In Flame API, .name is often a PyAttribute; str() resolves its value.
        name = str(name) if name is not None else ""
        return _sanitize(name) or "batch"
    except Exception:
        _log_exc("flame_current_batch_name")
        return "batch"


def flame_current_tab() -> str:
    """
    Authoritative current-tab name, or "" if unavailable.

    Verified on Flame 2026.2.2 via API probe:
        Desktop Batch    -> 'Batch'
        Inside BatchFX   -> 'BFX'
    """
    if not _HAS_FLAME:
        return ""
    try:
        fn = getattr(flame, "get_current_tab", None)
        if callable(fn):
            return str(fn() or "")
    except Exception:
        _log_exc("flame_current_tab")
    return ""


def flame_looks_like_bfx() -> bool:
    """
    'Are we inside a BatchFX?'

    PRIMARY (authoritative): flame.get_current_tab() == 'BFX'.
    An API probe on 2026.2.2 confirmed this returns 'Batch' on the desktop and
    'BFX' inside a BatchFX, so no guesswork is needed.

    FALLBACK (heuristic): only used if get_current_tab() is unavailable on some
    other Flame version. See the node-count fingerprint documented below.

    WHY THIS MATTERS
    ----------------
    When the artist enters a BatchFX, `flame.batch` silently re-points to the
    BFX node graph while `flame.batch.name` KEEPS the desktop batch's name:

        Desktop batch : flame.batch -> 143 nodes, name 'NTFLX_101_..._0010'
        Inside BFX    : flame.batch ->   3 nodes, name 'NTFLX_101_..._0010'

    Left unguarded, a scheduled save fired from inside a BFX writes the tiny
    BFX graph under the real shot's name, into the real shot's folder — and
    retention then rotates the genuine batch backups out of existence.

    FALLBACK FINGERPRINT (only if get_current_tab is missing)
    ---------------------------------------------------------
    The probe also showed the desktop batch groups collapse to zero nodes
    while a BFX is open:

        Desktop batch : batch_groups node counts = [114, 71, 93, 143]
        Inside BFX    : batch_groups node counts = [  0,  0,  0,   3]

    So: if the active batch name matches a desktop batch group AND every OTHER
    desktop batch group reports zero nodes, we are probably inside a BFX. This
    can false-positive when the artist genuinely has empty batch groups, which
    is why it is now only a fallback.

    FAIL-SAFE: any error, or anything less than full confidence, returns False
    (i.e. "not BFX" -> the save proceeds normally).
    """
    if not _HAS_FLAME:
        return False

    # --- PRIMARY: authoritative tab query ---------------------------------
    tab = flame_current_tab()
    if tab:
        return tab.strip().upper() == "BFX"

    # --- FALLBACK: node-count fingerprint ---------------------------------
    try:
        b = getattr(flame, "batch", None)
        if b is None:
            return False
        cur_name = str(getattr(b, "name", "") or "")
        if not cur_name:
            return False

        ws = flame.project.current_project.current_workspace
        desktop = getattr(ws, "desktop", None)
        groups = getattr(desktop, "batch_groups", None) or []
        if len(groups) < 2:
            return False  # not enough signal to fingerprint

        matched = False
        others_total = 0
        others_zero = 0
        for g in groups:
            gname = str(getattr(g, "name", "") or "")
            try:
                n_nodes = len(g.nodes)
            except Exception:
                continue
            if gname == cur_name and not matched:
                matched = True          # this is (or mirrors) the active one
                continue
            others_total += 1
            if n_nodes == 0:
                others_zero += 1

        if not matched or others_total == 0:
            return False
        return others_zero == others_total
    except Exception:
        _log_exc("flame_looks_like_bfx")
        return False


def flame_is_playing() -> bool:
    """
    True if playback is currently running. Defaults to False on any doubt.

    KNOWN LIMITATION (Flame 2026.2.2): `flame.playback` does not exist — an
    API probe of all 99 top-level members found no playback/render status
    entry point at all. This therefore always returns False on this version,
    which means Safe Mode is effectively inert here. Tracked separately.
    """
    if not _HAS_FLAME:
        return False
    try:
        playback = getattr(flame, "playback", None)
        if playback is None:
            return False
        is_playing = getattr(playback, "is_playing", None)
        if callable(is_playing):
            return bool(is_playing())
        # Some versions expose it as a bool-ish attribute.
        if is_playing is not None:
            return bool(is_playing)
    except Exception:
        _log_exc("flame_is_playing")
    return False


def flame_is_rendering() -> bool:
    """
    Best-effort 'is Flame busy processing' probe. The exact API varies across
    releases, so we feature-detect a few known surfaces and otherwise assume
    NOT rendering (so we never permanently starve the save loop).
    """
    if not _HAS_FLAME:
        return False
    try:
        # Some builds expose a scheduler / processing status.
        for attr in ("is_rendering", "is_processing", "is_busy"):
            fn = getattr(flame, attr, None)
            if callable(fn):
                try:
                    return bool(fn())
                except Exception:
                    pass
    except Exception:
        _log_exc("flame_is_rendering")
    return False


def _resolve_batch_save_callable():
    """
    Return the correct callable to persist the active Batch setup, or None.

    The canonical PyBatch method is `save_setup`. Some docs / older aliases
    reference `export_setup`. Because Flame returns None (not AttributeError)
    for unknown attributes, we must test `callable()` explicitly rather than
    trusting attribute existence.
    """
    if not _HAS_FLAME:
        return None
    batch = getattr(flame, "batch", None)
    if batch is None:
        return None
    for name in ("save_setup", "export_setup"):
        fn = getattr(batch, name, None)
        if callable(fn):
            return fn
    return None


def _sanitize(name: str) -> str:
    """Make an arbitrary Flame name safe for a filesystem path segment."""
    if not name:
        return ""
    keep = "-_.() "
    cleaned = "".join(c if (c.isalnum() or c in keep) else "_" for c in name)
    return cleaned.strip().rstrip(".") or ""


# ==============================================================================
#  Path resolution  (fully driven by the user-editable path template)
# ==============================================================================
def render_template_segments(template: str, project: str, user: str,
                             batch: str) -> list:
    """
    Turn a path template into a list of sanitized folder segments.

    Tokens <project> / <user> / <batch> (plus aliases) are substituted with
    the corresponding sanitized values; every other bit of text is kept as a
    literal folder name. Forward OR back slashes separate folders. Empty
    segments are dropped so stray/leading/trailing slashes never create blank
    directory levels.
    """
    values = {
        "project": _sanitize(project) or "UNSET_PROJECT",
        "user":    _sanitize(user) or "UNSET_USER",
        "batch":   _sanitize(batch) or "batch",
    }

    def _sub(match: "re.Match") -> str:
        norm = match.group(1).strip().lower()
        norm = norm.replace(" ", "").replace("_", "").replace("-", "")
        key = _TOKEN_ALIASES.get(norm)
        return values[key] if key else match.group(0)  # unknown -> literal

    rendered = re.sub(r"<([^<>]*)>", _sub, template or "")

    segments = []
    for part in rendered.replace("\\", "/").split("/"):
        seg = _sanitize(part)
        if seg:
            segments.append(seg)
    return segments


def resolve_batch_dir(cfg: dict, batch_name: str) -> str:
    """
    Resolve the final destination directory:
        [Target_Base_Dir] / <rendered path template>

    With the default template this is:
        [base]/[project]/[user]/Batch_Autosaves/[Batch_Name]/
    ...but the artist may retype the template to anything they like. Keeping
    <batch> as the last segment preserves per-batch isolation and correct
    retention. The .batch file and Flame's companion asset directory both land
    inside whatever this returns.
    """
    base = os.path.expanduser(cfg.get("base_dir") or DEFAULT_BASE_DIR)
    template = cfg.get("path_template") or DEFAULT_PATH_TEMPLATE
    segments = render_template_segments(
        template,
        cfg.get("project_name") or "",
        cfg.get("user_name") or "",
        batch_name,
    )
    return os.path.join(base, *segments) if segments else base


def resolve_bfx_dir(cfg: dict, bfx_name: str) -> str:
    """
    Resolve the destination for a BatchFX backup using the dedicated BFX
    template. With the default template this is:

        [base]/[project]/[user]/Batch_Autosaves/_BatchFX/[BFX_Name]/

    Deliberately a SIBLING of the shot folders, not a child: a BFX belongs to
    a timeline clip, not to whichever desktop batch happens to be open, so
    burying it under that batch's folder was misleading.
    """
    base = os.path.expanduser(cfg.get("base_dir") or DEFAULT_BASE_DIR)
    template = cfg.get("bfx_path_template") or DEFAULT_BFX_PATH_TEMPLATE
    segments = render_template_segments(
        template,
        cfg.get("project_name") or "",
        cfg.get("user_name") or "",
        bfx_name,
    )
    return os.path.join(base, *segments) if segments else base


def _is_protected(name: str) -> bool:
    """True if a .batch filename is a protected milestone (manual/post-render)."""
    stem = name[:-len(".batch")] if name.lower().endswith(".batch") else name
    return any(stem.endswith(sfx) for sfx in PROTECTED_SUFFIXES)


def enforce_retention(batch_dir: str, keep: int = MAX_SCHEDULED_BACKUPS) -> None:
    """
    Rotate SCHEDULED autosaves inside a single [Batch_Name] subfolder so no
    more than `keep` remain. Protected milestones (_manual / _post_render) are
    never counted and never deleted.

    Flame writes each setup as BOTH:
        [stem].batch        (the setup file)
        [stem]/             (companion asset directory, same stem, no ext)
    We remove both halves for every rotated-out backup.

    Safe by construction: we only ever act on entries physically located in
    `batch_dir`, only on names ending in .batch, and pair each to its exact
    same-stem sibling directory. Never raises.
    """
    try:
        if not os.path.isdir(batch_dir):
            return

        # Collect candidate scheduled .batch files with a sort key.
        candidates = []
        for entry in os.listdir(batch_dir):
            if not entry.lower().endswith(".batch"):
                continue
            if _is_protected(entry):
                continue  # milestones are exempt
            full = os.path.join(batch_dir, entry)
            if not os.path.isfile(full):
                continue
            # Sort primarily by the timestamp embedded in the filename (which
            # is zero-padded and lexicographically chronological); fall back to
            # mtime if the name is unexpectedly short.
            try:
                sort_key = (entry, os.path.getmtime(full))
            except Exception:
                sort_key = (entry, 0)
            candidates.append((sort_key, entry, full))

        if len(candidates) <= keep:
            return

        # Newest first, then drop everything past the keep threshold.
        candidates.sort(key=lambda c: c[0], reverse=True)
        to_delete = candidates[keep:]

        for _key, entry, full in to_delete:
            stem = entry[:-len(".batch")]
            companion_dir = os.path.join(batch_dir, stem)

            # Delete the .batch file.
            try:
                os.remove(full)
                _log(f"Rotated out old backup file: {entry}")
            except Exception:
                _log_exc(f"enforce_retention:remove_file {entry}")

            # Delete the companion asset directory (guard: must be a real dir
            # living directly inside batch_dir — never follow symlinks).
            try:
                if (os.path.isdir(companion_dir)
                        and not os.path.islink(companion_dir)
                        and os.path.dirname(companion_dir) == os.path.dirname(full)):
                    shutil.rmtree(companion_dir, ignore_errors=True)
                    _log(f"Rotated out old asset dir : {stem}{os.sep}")
            except Exception:
                _log_exc(f"enforce_retention:rmtree {stem}")

    except Exception:
        _log_exc("enforce_retention")


def build_filename(batch_name: str, suffix: str = "") -> str:
    """
    Chronological, sortable filename:
        [Batch_Name]_YYYYMMDD_HHMMSS[<suffix>].batch
    `suffix` example: "_manual" or "_post_render".
    """
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    batch_name = _sanitize(batch_name) or "batch"
    return f"{batch_name}_{ts}{suffix}.batch"


# ==============================================================================
#  Idle-detection event filter
# ------------------------------------------------------------------------------
#  Installed application-wide. Any mouse/keyboard/touch/wheel event stamps the
#  "last activity" clock. The monitor consults this when Idle mode is enabled.
# ==============================================================================
class _ActivityFilter(QObject):
    # Event types that count as "the artist is interacting".
    _ACTIVITY_EVENTS = frozenset((
        QEvent.MouseMove,
        QEvent.MouseButtonPress,
        QEvent.MouseButtonRelease,
        QEvent.MouseButtonDblClick,
        QEvent.KeyPress,
        QEvent.KeyRelease,
        QEvent.Wheel,
        QEvent.TouchBegin,
        QEvent.TouchUpdate,
        QEvent.TabletPress,
        QEvent.TabletMove,
    ))

    def __init__(self, parent=None):
        super().__init__(parent)
        # Monotonic seconds; robust against wall-clock changes.
        self._last_activity = QtCore.QElapsedTimer()
        self._last_activity.start()

    def eventFilter(self, obj, event):
        try:
            if event.type() in self._ACTIVITY_EVENTS:
                self._last_activity.restart()
        except Exception:
            # An event filter must NEVER raise — it would destabilize Qt.
            pass
        # Always pass the event through untouched.
        return False

    def idle_seconds(self) -> float:
        return self._last_activity.elapsed() / 1000.0


# ==============================================================================
#  The monitor — SINGLETON.  Owns the QTimer and performs the saves.
# ==============================================================================
class SmartAutoSaveMonitor(QObject):
    _instance = None  # class-level singleton handle

    # ------- Singleton access -------------------------------------------------
    @classmethod
    def _find_live_in_qt(cls):
        """
        Locate an ALREADY-RUNNING monitor in the live Qt object tree.

        This is what makes the Singleton survive "Refresh Python Hooks": every
        reload creates a brand-new Python module (so cls._instance resets to
        None), but the Qt objects from the previous import are still alive and
        parented to the QApplication. We find them by a fixed objectName rather
        than trusting Python-level module state.
        """
        app = QtWidgets.QApplication.instance()
        if app is None:
            return None
        try:
            for child in app.findChildren(QObject):
                if child.objectName() == MON_OBJECT_NAME:
                    return child
        except Exception:
            _log_exc("_find_live_in_qt")
        return None

    @classmethod
    def _live_monitors(cls, app):
        """
        Return every live monitor discoverable in the Qt tree that belongs to
        THIS engine — matched either by our fixed objectName or by class name
        (so app-parented instances from a different module reload are caught
        even if their objectName was already cleared).
        """
        found = []
        if app is None:
            return found
        try:
            for child in app.findChildren(QObject):
                try:
                    if (child.objectName() == MON_OBJECT_NAME
                            or type(child).__name__ == cls.__name__):
                        found.append(child)
                except Exception:
                    continue
        except Exception:
            _log_exc("_live_monitors")
        return found

    @classmethod
    def force_single_instance(cls):
        """
        Retire EVERY discoverable monitor, then create exactly one fresh one.

        This is the shared teardown-then-rebuild used by both boot-time reload
        handling and the UI "Reset Engine" button. Returns (monitor, retired).

        NOTE: it can only reach monitors that are parented to the QApplication
        (i.e. created by this markered version of the code). Zombie instances
        from a pre-marker version are neither parented nor named, so they are
        invisible here — clearing those still requires a Flame restart.
        """
        app = QtWidgets.QApplication.instance()
        retired = 0
        for mon in cls._live_monitors(app):
            try:
                if hasattr(mon, "shutdown"):
                    mon.shutdown()
                    retired += 1
            except Exception:
                _log_exc("force_single_instance:retire")
        cls._instance = None
        fresh = cls.instance()
        _log(f"Engine reset — retired {retired} instance(s); one monitor live.")
        return fresh, retired

    @classmethod
    def instance(cls) -> "SmartAutoSaveMonitor":
        if cls._instance is not None:
            return cls._instance
        # Reuse a live monitor from a previous import if one exists.
        existing = cls._find_live_in_qt()
        if existing is not None:
            cls._instance = existing
            return existing
        cls._instance = SmartAutoSaveMonitor()
        return cls._instance

    def __init__(self):
        # Parent to the QApplication so the monitor (and its child QTimers)
        # stay alive for the whole session and are discoverable across reloads.
        app = QtWidgets.QApplication.instance()
        super().__init__(app)
        self.setObjectName(MON_OBJECT_NAME)

        self.cfg = load_config()

        # Auto-populate project/user on first ever boot if blank.
        if not self.cfg.get("project_name"):
            self.cfg["project_name"] = flame_current_project_name()
        if not self.cfg.get("user_name"):
            self.cfg["user_name"] = flame_current_user_name()

        # QTimer lives on and fires on the GUI thread — safe for flame.* calls.
        self._timer = QTimer(self)
        self._timer.setTimerType(Qt.VeryCoarseTimer)  # low overhead; minute scale
        self._timer.timeout.connect(self._on_tick)

        # "Never forget" short-term retry timer. Only runs while a scheduled
        # save is being held back by Safe Mode (playback / render). It polls
        # every few seconds and fires the missed save the instant Flame is free,
        # then stops itself so we fall back to the normal long interval.
        self._retry_timer = QTimer(self)
        self._retry_timer.setTimerType(Qt.CoarseTimer)
        self._retry_timer.setInterval(RETRY_INTERVAL_MS)
        self._retry_timer.timeout.connect(self._on_retry_tick)

        # Idle watchdog. Runs ONLY when "Idle Auto-Save" is enabled. It is a
        # BONUS trigger (edge-detected) — it never blocks the interval engine.
        self._idle_timer = QTimer(self)
        self._idle_timer.setTimerType(Qt.CoarseTimer)
        self._idle_timer.setInterval(IDLE_POLL_MS)
        self._idle_timer.timeout.connect(self._on_idle_tick)
        # Armed = eligible to fire one idle save for the CURRENT idle stretch.
        self._idle_armed = True

        # Application-wide activity filter for idle detection.
        self._activity = _ActivityFilter()
        if app is not None:
            app.installEventFilter(self._activity)
        else:
            _log("WARNING: no QApplication yet; idle detection will attach later.")

        self._last_save_ok = None    # for UI status reporting
        self._last_save_msg = "No save yet."

        # Manual pause (runtime only, NOT persisted). Use before risky ops such
        # as opening an Archive, a big import, or a heavy render — anything
        # where an autosave firing mid-operation could aggravate Flame. Resets
        # to running on the next Flame launch / hook reload by design, so a
        # forgotten pause can never silently disable backups forever.
        self._paused = False

        # Idle-event save queue. Automatic saves are NOT run straight from the
        # timer anymore — calling flame.batch.save_setup() while Flame is busy
        # (archive restore, media cache, render) can crash the app with
        # "Pure virtual function called". Instead we hand the save to
        # flame.schedule_idle_event(), which only fires when Flame's main loop
        # is genuinely idle, i.e. NOT in the middle of such an operation.
        self._save_queue = []       # list of pending suffix strings
        self._save_scheduled = False
        self._alive = True          # cleared on shutdown; guards idle callback

        self._apply_timer_from_config()
        _log(f"Monitor initialized (v{SCRIPT_VERSION}).")

    # ------- Clean teardown (used on reload) ----------------------------------
    def shutdown(self) -> None:
        """
        Stop every timer and detach the event filter so a previous instance
        cannot keep firing after a hook reload. Clears its objectName so it is
        no longer discoverable, then schedules deletion.
        """
        try:
            self._alive = False       # a pending idle-event save will no-op
            self._save_queue = []
            self._timer.stop()
            self._retry_timer.stop()
            self._idle_timer.stop()
            app = QtWidgets.QApplication.instance()
            if app is not None and self._activity is not None:
                app.removeEventFilter(self._activity)
            self.setObjectName("")   # no longer matches MON_OBJECT_NAME
            self.deleteLater()
            _log("Previous monitor instance retired.")
        except Exception:
            _log_exc("shutdown")

    # ------- Timer control ----------------------------------------------------
    def _apply_timer_from_config(self) -> None:
        """(Re)configure the QTimer interval from current config."""
        try:
            interval_min = int(self.cfg.get("interval_min", 10))
        except Exception:
            interval_min = 10
        interval_min = max(1, min(60, interval_min))  # clamp 1..60

        self._timer.stop()
        if self.cfg.get("enabled", True):
            self._timer.start(interval_min * 60 * 1000)  # ms
            _log(f"Interval engine ON  ({interval_min} min).")
        else:
            _log("Interval engine OFF.")

        # Idle watchdog runs only when enabled AND the master engine is on.
        self._idle_timer.stop()
        self._idle_armed = True
        if self.cfg.get("enabled", True) and self.cfg.get("idle_enabled", False):
            self._idle_timer.start()
            idle_min = max(1, int(self.cfg.get("idle_min", 5) or 5))
            _log(f"Idle watchdog ON  (bonus save after {idle_min} min idle).")

    def apply_config(self, new_cfg: dict) -> None:
        """Merge in new settings from the UI and restart the timer cleanly."""
        self.cfg.update(new_cfg)
        save_config(self.cfg)
        self._apply_timer_from_config()

    # ------- The heartbeat ----------------------------------------------------
    def _on_tick(self) -> None:
        """
        Called on the GUI thread every interval. Applies all smart safeguards
        before committing a save. Never raises.
        """
        try:
            self._attempt_scheduled_save(from_retry=False)
        except Exception:
            _log_exc("_on_tick")

    def _safe_mode_active(self) -> bool:
        """True if Flame is playing back or rendering (Safe Mode should hold)."""
        if flame_is_playing():
            _log("Safe Mode: playback is active.")
            return True
        if flame_is_rendering():
            _log("Safe Mode: Flame is rendering / processing.")
            return True
        return False

    def _attempt_scheduled_save(self, from_retry: bool) -> None:
        """
        Run the regular interval backup.

        IMPORTANT DESIGN DECISION:
        The interval engine ALWAYS saves on schedule. The ONLY thing that may
        defer it is Safe Mode (playback / render), and that deferral is never
        forgotten — we arm the short-term retry timer so the missed save fires
        the instant Flame is free.

        Idle mode does NOT gate this path. (Older behavior blocked every save
        while the artist was active, which meant hours of work with no backup.)
        Idle is now a separate, additive bonus trigger — see _on_idle_tick.
        """
        # --- Manual pause: skip automatic saves entirely ------------------
        if self._paused:
            _log("Auto-save PAUSED — scheduled save skipped (resume in the "
                 "settings window).")
            return

        # --- Safe mode: defer + arm retry ---------------------------------
        if self._safe_mode_active():
            self._start_retry()
            return

        # --- BatchFX guard: never let a BFX graph overwrite a shot's -----
        # --- backups (see flame_looks_like_bfx for the full rationale) ---
        if self._bfx_guard_blocks("scheduled"):
            return

        # --- Flame is free: queue the save for the next idle moment -------
        self._stop_retry()
        self._request_save(suffix="")

    # ------- Manual pause -----------------------------------------------------
    def set_paused(self, paused: bool) -> None:
        """Pause/resume ALL automatic saves (scheduled, idle, post-render).
        Manual 'Snapshot Now' still works — it is an explicit user action."""
        self._paused = bool(paused)
        if self._paused:
            self._stop_retry()  # don't let a pending retry fire while paused
            self._last_save_msg = "Auto-save PAUSED."
            _log("Auto-save PAUSED by user. Automatic saves will not run until "
                 "resumed. Manual 'Snapshot Now' still works.")
        else:
            self._last_save_msg = "Auto-save resumed."
            _log("Auto-save RESUMED.")

    def is_paused(self) -> bool:
        return self._paused

    def _bfx_guard_blocks(self, kind: str) -> bool:
        """
        Return True only when the configured BatchFX mode is "skip" AND we are
        actually inside a BatchFX. In "separate" mode we return False and let
        perform_save() route the backup into its own folder instead.

        Logs loudly either way — a silent skip is exactly how the earlier idle
        regression hid itself.
        """
        if self.cfg.get("bfx_mode", "separate") != "skip":
            return False
        if not flame_looks_like_bfx():
            return False
        self._last_save_msg = "Skipped: inside BatchFX (mode = skip)."
        _log(f"BFX — {kind} save SKIPPED (tab='{flame_current_tab()}', "
             f"mode='skip').")
        _log("      Switch BatchFX Mode to 'Separate folder' in the settings "
             "window to back BatchFX up instead of skipping it.")
        return True

    # ------- Idle watchdog (additive bonus save) ------------------------------
    def _on_idle_tick(self) -> None:
        """
        Fires only while "Idle Auto-Save" is enabled. Edge-triggered: it takes
        exactly ONE extra snapshot when the artist crosses the idle threshold
        (e.g. steps away from the desk), then disarms until activity resumes.
        This captures the "walked-away" state early WITHOUT ever suppressing the
        normal interval saves.
        """
        try:
            if self._paused:
                return
            if not self.cfg.get("idle_enabled", False):
                return
            try:
                idle_min_required = max(1, int(self.cfg.get("idle_min", 5)))
            except Exception:
                idle_min_required = 5

            idle_now = self._activity.idle_seconds()

            # Re-arm as soon as the artist is active again.
            if idle_now < idle_min_required * 60:
                self._idle_armed = True
                return

            # Threshold crossed and we haven't yet fired for this idle stretch.
            if self._idle_armed:
                if self._safe_mode_active():
                    return  # try again next poll once Flame is free
                if self._bfx_guard_blocks("idle"):
                    return  # stay armed; retry once we are out of BFX
                self._idle_armed = False
                _log(f"Idle {idle_now/60:.1f} min — capturing bonus idle snapshot.")
                self._request_save(suffix="")
        except Exception:
            _log_exc("_on_idle_tick")

    # ------- "Never forget" retry ---------------------------------------------
    def _start_retry(self) -> None:
        """Arm the short-term retry poll if it isn't already running."""
        if not self._retry_timer.isActive():
            self._retry_timer.start()
            _log(
                f"Save deferred by Safe Mode — retry armed "
                f"(polling every {RETRY_INTERVAL_MS // 1000}s until Flame is free)."
            )

    def _stop_retry(self) -> None:
        """Disarm the retry poll (called once a save succeeds / is unblocked)."""
        if self._retry_timer.isActive():
            self._retry_timer.stop()

    def _on_retry_tick(self) -> None:
        """
        Retry heartbeat: fires only while a save is pending behind Safe Mode.
        Stays silent until Flame frees up, then executes the missed save once
        and disarms — returning control to the normal long interval loop.
        """
        try:
            if self._safe_mode_active():
                return  # still busy; keep polling quietly
            _log("Safe Mode cleared — firing the missed scheduled save now.")
            self._stop_retry()
            self._request_save(suffix="")
        except Exception:
            _log_exc("_on_retry_tick")

    # ------- Crash-safe save scheduling ---------------------------------------
    def _request_save(self, suffix: str = "") -> None:
        """
        Queue a save to run at Flame's NEXT idle moment instead of right now.

        This is the fix for the "Pure virtual function called" crash: running
        flame.batch.save_setup() while Flame is mid-operation (archive restore,
        media cache, render) corrupts state. flame.schedule_idle_event() defers
        the call until Flame's main loop is idle — i.e. not inside such an
        operation — so save_setup only ever touches a stable graph.

        Falls back to a direct save only if schedule_idle_event is unavailable
        (older/other Flame versions).
        """
        self._save_queue.append(suffix)

        idle_fn = getattr(flame, "schedule_idle_event", None) if _HAS_FLAME else None
        if not callable(idle_fn):
            # No idle API — run directly (legacy behavior).
            self._drain_save_queue()
            return

        if not self._save_scheduled:
            self._save_scheduled = True
            try:
                idle_fn(self._drain_save_queue)
                _log("Save queued — will run at Flame's next idle moment "
                     "(crash-safe).")
            except Exception:
                self._save_scheduled = False
                _log_exc("schedule_idle_event")
                self._drain_save_queue()   # last-resort direct

    def _drain_save_queue(self, *args) -> None:
        """
        Idle-event callback: run ONE queued save, then re-arm for the next if
        any remain. Re-checks pause here too, since state may have changed
        between queueing and this idle moment. Never raises.
        """
        self._save_scheduled = False
        try:
            # A retired instance (post-reload) must not touch Flame.
            if not getattr(self, "_alive", True):
                self._save_queue = []
                return
            if not self._save_queue:
                return
            suffix = self._save_queue.pop(0)

            # Honor a pause requested after this save was queued.
            if self._paused:
                _log("Auto-save PAUSED — dropping queued save.")
                self._save_queue.clear()
                return

            self.perform_save(suffix=suffix)
        except Exception:
            _log_exc("_drain_save_queue")
        finally:
            # Anything still queued (e.g. queued while busy) -> schedule again.
            if self._save_queue and not self._save_scheduled:
                idle_fn = getattr(flame, "schedule_idle_event", None) if _HAS_FLAME else None
                if callable(idle_fn):
                    self._save_scheduled = True
                    try:
                        idle_fn(self._drain_save_queue)
                    except Exception:
                        self._save_scheduled = False
                        _log_exc("schedule_idle_event(reschedule)")

    # ------- The actual export ------------------------------------------------
    def perform_save(self, suffix: str = "") -> bool:
        """
        Export the active Batch setup to the resolved target directory.

        suffix examples:  ""            -> scheduled backup
                          "_manual"     -> UI Snapshot Now button
                          "_post_render"-> native render-complete hook

        Returns True on success. Never raises.
        """
        if not _HAS_FLAME:
            _log("perform_save skipped: Flame API not available.")
            return False

        try:
            # --- Decide WHICH graph we are actually saving ----------------
            # Inside a BFX, flame.batch.name reports the DESKTOP batch's name,
            # which would file the BFX under an unrelated shot. So when a BFX
            # is active we resolve its own name and use a separate tree.
            in_bfx = (self.cfg.get("bfx_mode", "separate") != "off"
                      and flame_looks_like_bfx())

            if in_bfx:
                bfx_name = flame_bfx_name()
                if not bfx_name:
                    # Could not resolve the BFX's real name. Do NOT fall back
                    # to the desktop batch name — that is exactly the mix-up
                    # we are fixing. Use a clearly-marked holding folder.
                    bfx_name = "UNRESOLVED_BFX"
                    _log("BFX name unresolved — filing under 'UNRESOLVED_BFX'. "
                         "Console diagnostics above show the candidates tried.")
                save_name  = bfx_name
                target_dir = resolve_bfx_dir(self.cfg, bfx_name)
                suffix     = BFX_SUFFIX + suffix   # "_bfx", "_bfx_manual", ...
            else:
                save_name  = flame_current_batch_name()
                target_dir = resolve_batch_dir(self.cfg, save_name)

            os.makedirs(target_dir, exist_ok=True)

            filename   = build_filename(save_name, suffix=suffix)
            full_path  = os.path.join(target_dir, filename)

            # IMPORTANT: we deliberately DO NOT call flame.project.save().
            # We isolate the backup to the active Batch workspace only.
            #
            # The correct PyBatch method is save_setup(). NOTE the Flame quirk:
            # accessing an attribute that does not exist on a flame.* object
            # returns None (it does NOT raise AttributeError), so a wrong name
            # like export_setup silently yields None and then raises
            # "TypeError: 'NoneType' object is not callable" when invoked.
            # We therefore resolve the real callable by feature-detection and
            # fail loudly with a clear message if none is present.
            #
            # save_setup() appends the .batch extension itself, so we strip it
            # from the path we hand the API, then report the real written file.
            save_fn = _resolve_batch_save_callable()
            if save_fn is None:
                raise RuntimeError(
                    "No usable batch save method found on flame.batch "
                    "(tried save_setup / export_setup). Check the API for "
                    "this Flame version."
                )

            export_arg = full_path
            if export_arg.lower().endswith(".batch"):
                export_arg = export_arg[: -len(".batch")]

            save_fn(export_arg)

            kind = suffix.lstrip("_") or "scheduled"
            self._last_save_ok = True
            self._last_save_msg = f"{kind} save OK: {filename}"
            _log(f"{kind.upper()} SAVE -> {full_path}")

            # Rotate old SCHEDULED backups inside THIS batch's subfolder only.
            # Manual / post-render milestones are exempt (see enforce_retention).
            enforce_retention(target_dir)
            return True

        except Exception:
            self._last_save_ok = False
            self._last_save_msg = "Last save FAILED (see console)."
            _log_exc("perform_save")
            return False

    # ------- Public triggers --------------------------------------------------
    def snapshot_now(self) -> bool:
        """
        Manual snapshot. Queued via the idle event like every other save so it
        can never fire mid-operation and crash Flame. On an idle Flame this runs
        almost immediately; if Flame is busy it waits for the next idle moment.
        Returns True to mean 'queued' (not 'written').
        """
        _log("Manual snapshot requested.")
        self._request_save(suffix="_manual")
        return True

    def post_render_save(self) -> bool:
        """Forced dedicated backup after a render completes. Honors pause —
        it is an automatic trigger, not an explicit user click."""
        if self._paused:
            _log("Auto-save PAUSED — post-render snapshot skipped.")
            return False
        _log("Post-render snapshot requested.")
        self._request_save(suffix="_post_render")
        return True

    # ------- Status for UI ----------------------------------------------------
    def status_text(self) -> str:
        return self._last_save_msg


# ==============================================================================
#  PySide6 Configuration Window
# ==============================================================================
class SmartAutoSaveWindow(QtWidgets.QWidget):
    """
    Slick, minimalist settings UI. Reads from / writes to the monitor's config
    and the JSON file. Opening/closing it never touches the background timer
    except via explicit Save/Apply.
    """

    # Keep a single window reference so the menu re-uses it (and it isn't GC'd).
    _window = None

    @classmethod
    def show_window(cls) -> "SmartAutoSaveWindow":
        if cls._window is None:
            cls._window = SmartAutoSaveWindow()
        cls._window.reload_from_config()
        cls._window.show()
        cls._window.raise_()
        cls._window.activateWindow()
        return cls._window

    def __init__(self):
        super().__init__()
        self.monitor = SmartAutoSaveMonitor.instance()

        self.setWindowTitle(f"{SCRIPT_NAME}  v{SCRIPT_VERSION}")
        self.setMinimumWidth(560)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self._build_ui()
        self._wire_signals()
        self.reload_from_config()
        self._update_preview()

    # ------- UI construction --------------------------------------------------
    def _build_ui(self) -> None:
        self.setStyleSheet(self._stylesheet())

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(18, 18, 18, 18)
        root.setSpacing(14)

        # Header
        header = QtWidgets.QLabel(SCRIPT_NAME)
        header.setObjectName("Header")
        root.addWidget(header)

        # --- Form group -------------------------------------------------------
        form_box = QtWidgets.QGroupBox("Backup Configuration")
        form = QtWidgets.QGridLayout(form_box)
        form.setColumnStretch(1, 1)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(10)
        r = 0

        # Base directory + Browse
        form.addWidget(QtWidgets.QLabel("Target Base Directory"), r, 0)
        self.base_edit = QtWidgets.QLineEdit()
        self.base_edit.setPlaceholderText("/mnt/nas/backups or /var/tmp/scratch")
        self.browse_btn = QtWidgets.QPushButton("Browse…")
        self.browse_btn.setObjectName("Secondary")
        form.addWidget(self.base_edit, r, 1)
        form.addWidget(self.browse_btn, r, 2)
        r += 1

        # Project name (auto-filled, editable)
        form.addWidget(QtWidgets.QLabel("Project Name"), r, 0)
        self.project_edit = QtWidgets.QLineEdit()
        self.project_refresh = QtWidgets.QPushButton("↻")
        self.project_refresh.setObjectName("Icon")
        self.project_refresh.setToolTip("Re-read current project from Flame")
        form.addWidget(self.project_edit, r, 1)
        form.addWidget(self.project_refresh, r, 2)
        r += 1

        # User name (auto-filled, editable)
        form.addWidget(QtWidgets.QLabel("User Name"), r, 0)
        self.user_edit = QtWidgets.QLineEdit()
        self.user_refresh = QtWidgets.QPushButton("↻")
        self.user_refresh.setObjectName("Icon")
        self.user_refresh.setToolTip("Re-read current user from Flame")
        form.addWidget(self.user_edit, r, 1)
        form.addWidget(self.user_refresh, r, 2)
        r += 1

        # Path template (fully editable) + reset-to-default button
        form.addWidget(QtWidgets.QLabel("Path Template"), r, 0)
        self.template_edit = QtWidgets.QLineEdit()
        self.template_edit.setPlaceholderText(DEFAULT_PATH_TEMPLATE)
        self.template_reset = QtWidgets.QPushButton("↺")
        self.template_reset.setObjectName("Icon")
        self.template_reset.setToolTip("Reset template to the default layout")
        form.addWidget(self.template_edit, r, 1)
        form.addWidget(self.template_reset, r, 2)
        r += 1

        # Token hint under the template field
        self.token_hint = QtWidgets.QLabel(
            "Tokens: <project>  <user>  <batch>   ·   \"/\" separates folders."
            "  Everything else is a literal folder name."
        )
        self.token_hint.setObjectName("Example")
        self.token_hint.setWordWrap(True)
        form.addWidget(self.token_hint, r, 1)
        r += 1

        # BatchFX path template (separate tree; <batch> = the BFX's own name)
        form.addWidget(QtWidgets.QLabel("BatchFX Path Template"), r, 0)
        self.bfx_template_edit = QtWidgets.QLineEdit()
        self.bfx_template_edit.setPlaceholderText(DEFAULT_BFX_PATH_TEMPLATE)
        self.bfx_template_edit.setToolTip(
            "Where BatchFX backups go. Here <batch> resolves to the BatchFX's\n"
            "OWN name (e.g. 'frame'), not the desktop batch name."
        )
        self.bfx_template_reset = QtWidgets.QPushButton("↺")
        self.bfx_template_reset.setObjectName("Icon")
        self.bfx_template_reset.setToolTip("Reset BatchFX template to default")
        form.addWidget(self.bfx_template_edit, r, 1)
        form.addWidget(self.bfx_template_reset, r, 2)
        r += 1

        # Interval spin box
        form.addWidget(QtWidgets.QLabel("Save Interval (min)"), r, 0)
        self.interval_spin = QtWidgets.QSpinBox()
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setSuffix(" min")
        form.addWidget(self.interval_spin, r, 1)
        r += 1

        # Master enable
        self.enable_chk = QtWidgets.QCheckBox("Enable interval auto-save engine")
        form.addWidget(self.enable_chk, r, 1)
        r += 1

        # Idle mode
        self.idle_chk = QtWidgets.QCheckBox("Enable Idle Auto-Save")
        form.addWidget(self.idle_chk, r, 1)
        r += 1

        # BatchFX handling mode
        form.addWidget(QtWidgets.QLabel("BatchFX Mode"), r, 0)
        self.bfx_combo = QtWidgets.QComboBox()
        self.bfx_combo.addItem("Separate folder (recommended)", "separate")
        self.bfx_combo.addItem("Skip auto-save in BatchFX", "skip")
        self.bfx_combo.addItem("No special handling (unsafe)", "off")
        self.bfx_combo.setToolTip(
            "Flame re-points flame.batch to the BatchFX graph but keeps the\n"
            "desktop batch's NAME, so BFX saves would otherwise land in the\n"
            "shot's folder and rotate out the real batch backups.\n\n"
            "Separate folder : BFX goes to .../[Batch]/BatchFX/ with a _bfx tag\n"
            "Skip            : no automatic save while inside BatchFX\n"
            "No special      : legacy behaviour — can destroy batch backups"
        )
        form.addWidget(self.bfx_combo, r, 1)
        r += 1

        self.bfx_hint = QtWidgets.QLabel(
            "Detected via flame.get_current_tab() — returns 'BFX' inside BatchFX."
        )
        self.bfx_hint.setObjectName("Example")
        self.bfx_hint.setWordWrap(True)
        form.addWidget(self.bfx_hint, r, 1)
        r += 1

        form.addWidget(QtWidgets.QLabel("Idle Threshold (min)"), r, 0)
        self.idle_spin = QtWidgets.QSpinBox()
        self.idle_spin.setRange(1, 60)
        self.idle_spin.setSuffix(" min")
        form.addWidget(self.idle_spin, r, 1)
        r += 1

        root.addWidget(form_box)

        # --- Live preview -----------------------------------------------------
        prev_box = QtWidgets.QGroupBox("Resolved Backup Path (live)")
        prev_layout = QtWidgets.QVBoxLayout(prev_box)
        self.preview_label = QtWidgets.QLabel("")
        self.preview_label.setObjectName("Preview")
        self.preview_label.setWordWrap(True)
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        prev_layout.addWidget(self.preview_label)

        self.example_label = QtWidgets.QLabel("")
        self.example_label.setObjectName("Example")
        self.example_label.setWordWrap(True)
        prev_layout.addWidget(self.example_label)
        root.addWidget(prev_box)

        # --- Status -----------------------------------------------------------
        self.status_label = QtWidgets.QLabel(self.monitor.status_text())
        self.status_label.setObjectName("Status")
        root.addWidget(self.status_label)

        # --- Pause row --------------------------------------------------------
        pause_row = QtWidgets.QHBoxLayout()
        self.pause_btn = QtWidgets.QPushButton("⏸  Pause Auto-Save")
        self.pause_btn.setObjectName("Secondary")
        self.pause_btn.setToolTip(
            "Temporarily stop ALL automatic saves (scheduled, idle, post-render).\n"
            "Use before risky operations: opening an Archive, a big import,\n"
            "a heavy render. 'Snapshot Now' still works while paused.\n"
            "Auto-resumes on the next Flame launch so backups can't stay off."
        )
        self.pause_state = QtWidgets.QLabel("")
        self.pause_state.setObjectName("Paused")
        pause_row.addWidget(self.pause_btn)
        pause_row.addWidget(self.pause_state)
        pause_row.addStretch(1)
        root.addLayout(pause_row)

        # --- Maintenance row --------------------------------------------------
        maint_row = QtWidgets.QHBoxLayout()
        self.reset_btn = QtWidgets.QPushButton("🧹  Reset Engine (clear duplicates)")
        self.reset_btn.setObjectName("Secondary")
        self.reset_btn.setToolTip(
            "Retire every running monitor instance and start a single fresh one.\n"
            "Use this if duplicate/parallel saves appear after reloading hooks.\n"
            "Note: zombies from a pre-update version still need a Flame restart."
        )
        self.engine_status = QtWidgets.QLabel("")
        self.engine_status.setObjectName("Example")
        maint_row.addWidget(self.reset_btn)
        maint_row.addWidget(self.engine_status)
        maint_row.addStretch(1)
        root.addLayout(maint_row)

        # --- Buttons ----------------------------------------------------------
        btn_row = QtWidgets.QHBoxLayout()
        self.snapshot_btn = QtWidgets.QPushButton("📸  Snapshot Now")
        self.snapshot_btn.setObjectName("Primary")
        self.save_btn = QtWidgets.QPushButton("Save Settings")
        self.close_btn = QtWidgets.QPushButton("Close")
        self.close_btn.setObjectName("Secondary")
        btn_row.addWidget(self.snapshot_btn)
        btn_row.addStretch(1)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.close_btn)
        root.addLayout(btn_row)

        # --- Footer / credit --------------------------------------------------
        divider = QtWidgets.QFrame()
        divider.setObjectName("Divider")
        divider.setFrameShape(QtWidgets.QFrame.HLine)
        root.addWidget(divider)

        self.footer_label = QtWidgets.QLabel(
            f"{SCRIPT_NAME}  v{SCRIPT_VERSION}   ·   {SCRIPT}"
        )
        self.footer_label.setObjectName("Footer")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        root.addWidget(self.footer_label)

    # ------- Signal wiring ----------------------------------------------------
    def _wire_signals(self) -> None:
        self.browse_btn.clicked.connect(self._on_browse)
        self.project_refresh.clicked.connect(
            lambda: self.project_edit.setText(flame_current_project_name())
        )
        self.user_refresh.clicked.connect(
            lambda: self.user_edit.setText(flame_current_user_name())
        )

        # Live preview updates
        for w in (self.base_edit, self.project_edit, self.user_edit,
                  self.template_edit):
            w.textChanged.connect(self._update_preview)

        self.template_reset.clicked.connect(
            lambda: self.template_edit.setText(DEFAULT_PATH_TEMPLATE)
        )
        self.bfx_template_reset.clicked.connect(
            lambda: self.bfx_template_edit.setText(DEFAULT_BFX_PATH_TEMPLATE)
        )

        self.idle_chk.toggled.connect(self.idle_spin.setEnabled)

        self.snapshot_btn.clicked.connect(self._on_snapshot)
        self.save_btn.clicked.connect(self._on_save)
        self.close_btn.clicked.connect(self.close)
        self.reset_btn.clicked.connect(self._on_reset_engine)
        self.pause_btn.clicked.connect(self._on_toggle_pause)

    # ------- Data <-> widgets -------------------------------------------------
    def reload_from_config(self) -> None:
        cfg = self.monitor.cfg
        self.base_edit.setText(cfg.get("base_dir", ""))
        self.template_edit.setText(cfg.get("path_template", "") or DEFAULT_PATH_TEMPLATE)
        self.bfx_template_edit.setText(
            cfg.get("bfx_path_template", "") or DEFAULT_BFX_PATH_TEMPLATE)
        self.project_edit.setText(cfg.get("project_name", "") or flame_current_project_name())
        self.user_edit.setText(cfg.get("user_name", "") or flame_current_user_name())
        self.interval_spin.setValue(int(cfg.get("interval_min", 10)))
        self.enable_chk.setChecked(bool(cfg.get("enabled", True)))
        self.idle_chk.setChecked(bool(cfg.get("idle_enabled", False)))
        mode = cfg.get("bfx_mode", "separate")
        idx = self.bfx_combo.findData(mode)
        self.bfx_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.idle_spin.setValue(int(cfg.get("idle_min", 5)))
        self.idle_spin.setEnabled(self.idle_chk.isChecked())
        self.status_label.setText(self.monitor.status_text())
        self._refresh_engine_status()
        self._refresh_pause_state()

    def _refresh_pause_state(self) -> None:
        """Reflect the monitor's live pause state on the button + label."""
        if self.monitor.is_paused():
            self.pause_btn.setText("▶  Resume Auto-Save")
            self.pause_state.setText("⏸ PAUSED — automatic saves are off")
        else:
            self.pause_btn.setText("⏸  Pause Auto-Save")
            self.pause_state.setText("")

    def _refresh_engine_status(self) -> None:
        """Show how many live monitor instances are currently running."""
        app = QtWidgets.QApplication.instance()
        n = len(SmartAutoSaveMonitor._live_monitors(app))
        if n <= 1:
            self.engine_status.setText(f"● 1 engine running")
        else:
            self.engine_status.setText(
                f"⚠ {n} engines running — click Reset Engine"
            )

    def _collect_config(self) -> dict:
        return {
            "base_dir":     self.base_edit.text().strip() or DEFAULT_BASE_DIR,
            "path_template": self.template_edit.text().strip() or DEFAULT_PATH_TEMPLATE,
            "bfx_path_template": (self.bfx_template_edit.text().strip()
                                  or DEFAULT_BFX_PATH_TEMPLATE),
            "project_name": self.project_edit.text().strip(),
            "user_name":    self.user_edit.text().strip(),
            "interval_min": int(self.interval_spin.value()),
            "enabled":      bool(self.enable_chk.isChecked()),
            "idle_enabled": bool(self.idle_chk.isChecked()),
            "bfx_mode":     self.bfx_combo.currentData() or "separate",
            "idle_min":     int(self.idle_spin.value()),
        }

    # ------- Handlers ---------------------------------------------------------
    def _on_browse(self) -> None:
        start = self.base_edit.text().strip() or os.path.expanduser("~")
        chosen = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Select Target Base Directory", start
        )
        if chosen:
            self.base_edit.setText(chosen)

    def _update_preview(self) -> None:
        cfg = self._collect_config()
        # Show the full per-batch hierarchy using the live current batch name.
        batch_name = flame_current_batch_name() or "MyBatch"
        target = resolve_batch_dir(cfg, batch_name)
        self.preview_label.setText(target + os.sep)

        example = build_filename(batch_name)
        self.example_label.setText(f"e.g.  {os.path.join(target, example)}")

    def _on_snapshot(self) -> None:
        # Persist current edits first so the snapshot honors on-screen fields,
        # but do NOT restart the timer (snapshot must be side-effect free on it).
        self.monitor.cfg.update(self._collect_config())
        save_config(self.monitor.cfg)
        ok = self.monitor.snapshot_now()
        self.status_label.setText("Snapshot queued (runs at next idle).")
        self._flash(self.snapshot_btn, "✓ Queued" if ok else "× Failed")

    def _on_save(self) -> None:
        self.monitor.apply_config(self._collect_config())
        self.status_label.setText("Settings applied. " + self.monitor.status_text())
        self._flash(self.save_btn, "✓ Applied")

    def _on_reset_engine(self) -> None:
        """
        Retire all running monitors and rebuild a single clean one, then
        re-apply the on-screen settings so nothing is lost. Does NOT touch any
        files on disk — only the in-memory timers/instances.
        """
        # Preserve whatever is currently on screen through the rebuild.
        pending_cfg = self._collect_config()
        fresh, retired = SmartAutoSaveMonitor.force_single_instance()
        self.monitor = fresh
        self.monitor.apply_config(pending_cfg)  # persists + restarts timers
        self.reload_from_config()
        self.status_label.setText(
            f"Engine reset — retired {retired} instance(s), 1 running now."
        )
        self._flash(self.reset_btn, "✓ Reset done")

    def _on_toggle_pause(self) -> None:
        """Flip the monitor's pause state and reflect it in the UI."""
        self.monitor.set_paused(not self.monitor.is_paused())
        self._refresh_pause_state()
        self.status_label.setText(self.monitor.status_text())

    def _flash(self, btn: QtWidgets.QPushButton, text: str) -> None:
        """Momentary button-label feedback without blocking the UI thread."""
        original = btn.text()
        btn.setText(text)
        QTimer.singleShot(1400, lambda: btn.setText(original))

    # ------- Styling ----------------------------------------------------------
    @staticmethod
    def _stylesheet() -> str:
        return """
        QWidget { background: #232527; color: #d9dbdd; font-size: 12px; }
        QLabel#Header { font-size: 18px; font-weight: 600; color: #f2f4f6;
                        padding-bottom: 4px; }
        QGroupBox { border: 1px solid #3a3d40; border-radius: 8px;
                    margin-top: 14px; padding: 12px; font-weight: 600; }
        QGroupBox::title { subcontrol-origin: margin; left: 10px;
                           padding: 0 4px; color: #9aa0a6; }
        QLineEdit, QSpinBox {
            background: #1b1d1f; border: 1px solid #3a3d40; border-radius: 5px;
            padding: 6px 8px; color: #f2f4f6; selection-background-color: #4a90d9;
        }
        QLineEdit:focus, QSpinBox:focus { border: 1px solid #4a90d9; }
        QLabel#Preview { font-family: monospace; font-size: 12px; color: #7ec8ff;
                         background: #1b1d1f; border: 1px solid #3a3d40;
                         border-radius: 5px; padding: 8px; }
        QLabel#Example { color: #7a7f85; font-family: monospace; }
        QLabel#Status  { color: #9aa0a6; font-style: italic; }
        QLabel#Paused  { color: #e0a030; font-weight: 600; }
        QLabel#Footer  { color: #6a6f75; font-size: 11px; padding-top: 2px; }
        QFrame#Divider { color: #3a3d40; max-height: 1px; margin-top: 6px; }
        QCheckBox { spacing: 8px; }
        QPushButton {
            background: #3a3d40; border: none; border-radius: 6px;
            padding: 8px 14px; color: #f2f4f6;
        }
        QPushButton:hover { background: #45484b; }
        QPushButton#Primary   { background: #2d7d46; font-weight: 600; }
        QPushButton#Primary:hover { background: #349152; }
        QPushButton#Secondary { background: #303336; }
        QPushButton#Icon { padding: 6px 10px; font-weight: 700; }
        """

    # ------- Lifecycle --------------------------------------------------------
    def closeEvent(self, event):
        # Just hide semantics: the background monitor keeps running regardless.
        _log("Settings window closed (background engine continues).")
        super().closeEvent(event)


# ==============================================================================
#  Flame HOOKS  (module-level functions Flame discovers by name)
# ==============================================================================
#
#  NOTE ON HOOK NAMES
#  ------------------
#  The user brief references `flame_menu_custom_ui` and `batch_render_end`.
#  The Flame-sanctioned names are:
#     * get_main_menu_custom_ui_actions()  -> main menu custom actions
#     * batch_export_end(info) / render hooks -> render lifecycle
#  Hook availability varies 2026 -> 2027, so we register under multiple aliases
#  and fail safe if a given hook name isn't invoked by the host.
# ==============================================================================

def _open_settings(*args, **kwargs):
    """Menu callback: ensure the monitor exists, then raise the UI."""
    try:
        SmartAutoSaveMonitor.instance()          # guarantees background engine
        SmartAutoSaveWindow.show_window()
    except Exception:
        _log_exc("_open_settings")


def get_main_menu_custom_ui_actions():
    """
    Primary, officially-supported hook for adding a Flame main-menu action.
    Returns the structure Flame expects: a list of menu dicts.
    """
    return [
        {
            "name": SCRIPT_NAME,
            "actions": [
                {
                    "name": "Smart Batch Auto-Save Settings",
                    "execute": _open_settings,
                    "minimumVersion": "2026.0.0",
                }
            ],
        }
    ]


# Alias hooks — some pipelines / older docs expect these entry points. Flame
# only calls the ones it recognizes; defining extras is harmless.
def get_media_panel_custom_ui_actions():
    return get_main_menu_custom_ui_actions()


def get_batch_custom_ui_actions():
    return get_main_menu_custom_ui_actions()


# ---- Render-completion hooks (multiple aliases for cross-version safety) -----
def _fire_post_render(reason: str):
    try:
        _log(f"Render-complete hook fired ({reason}).")
        SmartAutoSaveMonitor.instance().post_render_save()
    except Exception:
        _log_exc("_fire_post_render")


def batch_render_end(*args, **kwargs):
    """Brief-requested hook name."""
    _fire_post_render("batch_render_end")


def batch_export_end(*args, **kwargs):
    """Flame's native batch export/render completion hook."""
    _fire_post_render("batch_export_end")


def render_end(*args, **kwargs):
    """Generic render-end hook present in several Flame releases."""
    _fire_post_render("render_end")


# ==============================================================================
#  Background boot on import
# ------------------------------------------------------------------------------
#  Flame imports this module at startup. We instantiate the Singleton monitor
#  immediately so backups run with defaults even if the artist never opens the
#  UI. We guard the whole thing so a boot failure can never break Flame startup.
# ==============================================================================
def _boot():
    try:
        # Only meaningful when a Qt app exists (inside Flame it always does).
        app = QtWidgets.QApplication.instance()
        if app is None:
            _log("No QApplication at import; monitor boot skipped (outside Flame).")
            return

        # CRITICAL for "Refresh Python Hooks": retire ANY monitor left running
        # from a previous import of this module before starting a fresh one.
        # Without this, every reload stacks another QTimer + event filter and
        # you get duplicate/parallel save loops (the classic Flame reload bug).
        SmartAutoSaveMonitor.force_single_instance()
        _log(f"Background engine booted from {CONFIG_PATH}.")
    except Exception:
        _log_exc("_boot")


# Kick off the background engine on import.
_boot()
