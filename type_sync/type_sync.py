"""
Script Name: Type Sync
Script Version: 1.1.0
Flame Version: 2026.1
Written by: Jeff Kyle
Creation Date: 06.10.26
Update Date: 09.24.26
Description:

    Sync the text of Flame Type (Timeline FX) graphics across many sequences
    and aspect-ratio versions from one place. A per-project JSON registry is
    the single source of truth for each graphic's text; segments are tagged
    'graphicNN' and receive their text from the registry (one-directional:
    registry -> tagged Type layers). Layout (position / scale / format) is
    handled separately through Flame's native segment connections, so text
    and layout are managed independently.

    Typical use is broadcast legal / disclaimer lines that must read
    identically across 16x9, 9x16, 1x1, 4x5, etc. while each aspect keeps its
    own framing -- but it works for any Flame-generated Type graphic.

    Install (single file, its own folder, unique name; restart Flame):
        /opt/Autodesk/shared/python/type_sync/type_sync.py
    Upgrading from GFX Sync: delete the old INSTALL folder
    /opt/Autodesk/shared/python/gfx_sync/ -- the tool only. Keep the
    gfx_sync folder in your projects' setups: it holds your registry, which
    Type Sync reads and copies to its new name automatically.

    The window doesn't block Flame: keep working with it open, and press
    Rescan (on the Scope row) after changing things in Flame.

    Tabs:
        Segments    - scan the scope; see every matching Type segment, its
                      text, assignment and sync status; assign Type numbers
                      and capture text to the registry. Sync Selected /
                      Sync All fix OUT OF DATE segments right here (every
                      change is shown first).
        Registry    - add / edit / remove graphic definitions; Sync Text to
                      scope.
        Connections - create / remove the segment connections that share a
                      graphic's layout between sequences of the same aspect.
                      Auto Connection queues them; Execute Queue runs them.
                      Every look has a letter: a connected set shares one, a
                      lone graphic has its own (after Z come AA, AB, ...).
        Timelines   - every sequence as a lane, grouped by aspect, with each
                      Type graphic where it sits in the cut: letter and
                      colour = its look, number = its Type number. Click
                      to see its text, where it is and what it's connected
                      to, with a preview rendered by Flame: Full frame, or
                      Type only (just the Type over black -- quick on
                      heavy timelines); Re-render makes a fresh one. The
                      zoom list, Fit, Text (frames the words), the mouse
                      wheel and drag-to-pan get you in close; double-click
                      the picture to Fit. Preview and Details show / hide
                      the panes; drag the dividers to resize them
                      (remembered between opens; each frame size keeps its
                      own zoom). Jump to Flame Segment (or double-click a
                      graphic) takes Flame there.
        Settings    - registry folder, default scope, what counts as a
                      target segment (match mode + name / track filters),
                      Segments-tab defaults (Grouped Text, default sort),
                      and Preview size for the Timelines preview: Native
                      (the default), 4K, HD or 720 px (fastest). Bigger =
                      sharper text when zoomed in, a little more time and
                      disk per render. Changes save as you leave the tab.


    Built by Jeff Kyle with Claude (Anthropic).

    Provided as-is, without warranty of any kind. Free to use and modify.

Menus:

    Right-click on a timeline segment  ->  Type Sync  ->  Type Sync...
    Right-click in the Media Panel     ->  Type Sync  ->  Type Sync...
    Flame main menu                    ->  Type Sync  ->  Open Manager...

Updates:

    v1.1.0 09.24.26
        - Renamed from GFX Sync to Type Sync: it works with Flame's Type
          only. Graphic numbers are Type01, Type02... Your GFX Sync
          settings and registries are picked up automatically. Install
          the new type_sync folder and delete the old gfx_sync INSTALL
          folder (otherwise Flame loads both) -- not the gfx_sync folder
          in your projects' setups, which holds your registry.
        - The window no longer blocks Flame. Press Rescan after changing
          things in Flame.
        - Segments tab: Sync Selected / Sync All push registry text onto
          OUT OF DATE segments, showing every change first.
        - Execute Queue re-checks Flame first; if anything changed since
          you reviewed the queue, it redraws the queue and asks you to
          press Execute Queue again.
        - Every look gets a letter in the Connections and Timelines tabs.
        - New Timelines tab: every sequence as a lane, every Type graphic
          where it sits; click to inspect, double-click to jump there.
        - Timelines preview rendered by Flame: Full frame or Type only,
          cached once per look. Zoom list, Fit, Text, mouse wheel zoom and
          drag-to-pan.
        - Resizable, hideable preview panes. The layout, the console and
          the window size are remembered between opens.
        - Each frame size keeps its own preview zoom.
        - Timelines: Show / Filter one Type (Filter lists only the sequences
          that use it). Tips buttons on the Connections and Timelines tabs.
        - Settings: Preview size (Native by default, or 4K, HD, 720 px) for
          sharper text when zoomed in. Settings save themselves as you
          leave the tab -- no more Save button.

    v1.0.1 09.24.26
        - Version shown in the window header.
        - Auto Connection: new segments join an existing connected set
          instead of being dropped or re-copying the set.
        - The queue shows exactly what will run; groups that can't run
          are marked with the reason.
        - Safer segment identity: a same-named copy of a sequence in
          another reel is no longer mistaken for the live one.
        - Split connected sets are reported, not guessed.
        - Set as Source works anywhere in the set being joined.
        - Break Selected clears the queue.
        - Temporary copies made while connecting are cleaned up properly.

    v1.0.0 08.02.26
        - First public release.
"""

import os
import re
import html
import shutil
import hashlib
import tempfile
import time
import ast
import json
import logging

import flame
from PySide6 import QtWidgets, QtCore, QtGui


log = logging.getLogger("type_sync")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(_h)
    log.setLevel(logging.INFO)
    log.propagate = False


# Shown in the window header and reported by users. MUST stay identical to the
# "Script Version:" field in the module docstring above -- that field is what
# Logik Portal reads and displays. Bump both together.
VERSION = "1.1.0"


# ====================================================================
# Settings (per-user) + Registry (per-project, configurable location)
# ====================================================================

SCOPES = ["Selected", "Current Sequence", "Current Reel", "Current Reel Group",
          "All Sequences Reels"]
MATCH_MODES = ["Gap segments with Type", "Any segment with Type"]

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), "flame", "type_sync_settings.json")
# Older names, read (never written) so existing installs migrate on the next save.
LEGACY_SETTINGS_PATHS = [
    os.path.join(os.path.expanduser("~"), "flame", "gfx_sync_settings.json"),   # GFX Sync era
    os.path.join(os.path.expanduser("~"), "flame", "graphic_sync_settings.json"),
    os.path.join(os.path.expanduser("~"), "flame", "legal_sync_settings.json"),
]
DEFAULT_SETTINGS = {
    "scope": "Current Reel",
    "registry_dir": "",          # blank -> per-project default
    "match_mode": "Gap segments with Type",
    "name_contains": "",
    "track_prefix": "",
    "inv_units": "Timecode",     # Inventory In/Dur display: "Timecode" | "Frames"
    "inv_hidden": [],            # Inventory columns the user has switched off
    "inv_group_default": False,  # Segments tab: start with Grouped Text on?
    "inv_sort": "",              # Segments tab default sort column key ("" = none)
}
# Accept the current 'graphicNN' tag and the legacy 'legalNN' tag on read.
TAG_RE = r"^(?:graphic|legal)\d+$"
# Editor delimiter: a line containing only this separates Type layers, so a
# single layer can hold multi-line text.
LAYER_SEP = "---"


def load_settings():
    for p in [SETTINGS_PATH] + LEGACY_SETTINGS_PATHS:
        try:
            with open(p) as f:
                return {**DEFAULT_SETTINGS, **json.load(f)}
        except Exception:
            continue
    return dict(DEFAULT_SETTINGS)


def _atomic_write_json(path, obj):
    """Write JSON via temp file + os.replace, so a crash mid-write can never
    leave a half-written (corrupt) file at the real path."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def _keep_unreadable(path):
    """Before overwriting a settings file that exists but can't be read (a
    hand-edit typo, say), keep a copy beside it: load_settings fell back to
    the defaults, so the write would otherwise lose those settings for good."""
    try:
        with open(path) as f:
            if isinstance(json.load(f), dict):
                return
    except FileNotFoundError:
        return
    except Exception:
        pass
    try:
        keep = path + ".unreadable-" + time.strftime("%Y%m%d-%H%M%S")
        shutil.copy2(path, keep)
        log.warning("settings file couldn't be read; kept a copy at %s", keep)
    except Exception:
        pass


def save_settings(settings):
    try:
        _keep_unreadable(SETTINGS_PATH)
        _atomic_write_json(SETTINGS_PATH, settings)
    except Exception as e:
        log.warning("settings save failed: %s", e)


def _default_registry_dir():
    try:
        sf = str(flame.projects.current_project.setups_folder).strip("'\"")
        if sf:
            return os.path.join(sf, "type_sync")
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "flame", "type_sync")


def registry_path():
    d = (load_settings().get("registry_dir") or "").strip() or _default_registry_dir()
    return os.path.join(d, "type_registry.json")


def _legacy_registry_candidates():
    """Registry locations from earlier names of this tool, in newest-first order.
    Read only -- never written, never deleted. load_registry() falls back through
    these, and the next save writes to the CURRENT path, so an existing project
    migrates itself while the old file stays on disk as a safety net."""
    d = (load_settings().get("registry_dir") or "").strip() or _default_registry_dir()
    cands = [os.path.join(d, "gfx_registry.json"),          # GFX Sync era (same folder)
             os.path.join(d, "graphic_registry.json"),      # graphic_sync era
             os.path.join(d, "legal_registry.json")]        # legal_sync era
    try:
        sf = str(flame.projects.current_project.setups_folder).strip("'\"")
        if sf:
            cands.append(os.path.join(sf, "gfx_sync", "gfx_registry.json"))   # GFX Sync default
            cands.append(os.path.join(sf, "graphic_sync", "graphic_registry.json"))
            cands.append(os.path.join(sf, "legal_sync", "legal_registry.json"))
    except Exception:
        pass
    custom = (load_settings().get("registry_dir") or "").strip()
    try:
        sf = str(flame.projects.current_project.setups_folder).strip("'\"")
    except Exception:
        sf = ""
    if not custom and not sf:        # GFX Sync's default when Flame gave no setups folder
        cands.append(os.path.join(os.path.expanduser("~"), "flame", "gfx_sync", "gfx_registry.json"))
    return cands


def load_registry():
    """{'01': {'lines': [...]}, '02': {...}}  (registry keys are prefix-agnostic).
    Reads the current file, then legacy locations, so existing projects migrate
    on the next save.

    A file that EXISTS but won't parse is quarantined (renamed *.corrupt)
    rather than silently treated as empty -- otherwise the next save would
    clobber the entire registry with a near-empty dict. Older names are read
    only while there's no current file (nor a quarantined one): once
    migrated, an old file is out of date and must never come back. A
    registry found under an older name is copied to the current name at
    once (the old file stays), so the registry folder shows it straight away."""
    cur = registry_path()
    legacy = [] if (os.path.exists(cur) or os.path.exists(cur + ".corrupt")) \
        else _legacy_registry_candidates()
    for p in [cur] + legacy:
        try:
            with open(p) as f:
                raw = f.read()
        except FileNotFoundError:
            continue
        except Exception as e:
            log.warning("registry read failed at %s: %s", p, e)
            continue
        try:
            data = json.loads(raw)
        except Exception as e:
            quarantine = p + ".corrupt"
            try:
                os.replace(p, quarantine)
                log.warning("registry at %s is corrupt (%s) — moved to %s so a "
                            "save can't overwrite it; starting empty", p, e, quarantine)
            except Exception:
                log.warning("registry at %s is corrupt (%s) and could not be "
                            "quarantined — do NOT save until it's recovered", p, e)
            if p == cur:
                return {}                       # never fall back to an older file
            continue
        if p != cur:
            try:
                _atomic_write_json(cur, data)   # migrated: copied to the current name
                log.info("registry copied from %s to %s", p, cur)
            except Exception as e:
                log.warning("registry found at %s but couldn't be copied to %s (%s)", p, cur, e)
        return data
    return {}


def save_registry(reg):
    try:
        _atomic_write_json(registry_path(), reg)
        return True
    except Exception as e:
        log.warning("registry save failed: %s", e)
        return False


def renumber_registry(reg, old, new, mode="overwrite"):
    """Pure registry side of a renumber. Returns (new_reg, retag, error) where
    retag maps each old instance key -> its new key for segment re-tagging.

      mode 'overwrite'  old -> new; if new existed its text is REPLACED (lost).
      mode 'swap'       old <-> new exchanged, BOTH kept (no data loss). Only
                        differs from overwrite when new already exists.
    Never mutates the passed-in dict."""
    ok, nk = "%02d" % int(old), "%02d" % int(new)
    if ok not in reg:
        return (reg, {}, "Type%s is not in the registry." % ok)
    out = dict(reg)
    if mode == "swap" and nk in out:
        out[ok], out[nk] = out[nk], out[ok]
        retag = {ok: nk, nk: ok}
    else:
        out[nk] = out.pop(ok)
        retag = {ok: nk}
    return (out, retag, None)


def renumber_graphic(old, new, scope, mode="overwrite"):
    """Renumber a registry entry and re-tag matching segments in scope (matching
    by number, so legacy 'legalNN' tags migrate too). mode 'overwrite' replaces
    the target; 'swap' exchanges the two without losing either.
    Returns (retagged_count, error_or_None)."""
    new_reg, retag, err = renumber_registry(load_registry(), old, new, mode)
    if err:
        return (0, err)
    save_registry(new_reg)
    settings = load_settings()
    n = 0
    for seq in sequences_for_scope(scope):
        for seg in iter_segments(seq):
            if not segment_matches(seg, settings):
                continue
            t = read_tag(seg)
            inst = tag_to_instance(t) if t else None
            if inst in retag:
                set_graphic_tag(seg, instance_tag(int(retag[inst])))
                n += 1
    return (n, None)


def _key(num):
    return "%02d" % int(num)


def text_to_layers(text):
    """Editor text -> per-layer list. A line that is only LAYER_SEP starts a
    new layer; newlines inside a layer are preserved."""
    groups, cur = [], []
    for ln in text.split("\n"):
        if ln.strip() == LAYER_SEP:
            groups.append("\n".join(cur))
            cur = []
        else:
            cur.append(ln)
    groups.append("\n".join(cur))
    while groups and groups[-1].strip() == "":
        groups.pop()
    return groups


def layers_to_text(lines):
    """Per-layer list -> editor text, layers separated by a LAYER_SEP line."""
    return ("\n" + LAYER_SEP + "\n").join(lines)


def attr_text(layer):
    """Raw text of a Type layer. layer.text is a PyAttribute whose str() is a
    Python repr (quoted, with \\n and \\uXXXX escapes). Prefer a typed accessor
    if Flame exposes one; otherwise reverse the repr so the true characters are
    returned (no stray quotes, real newlines, real unicode)."""
    a = getattr(layer, "text", "")
    g = getattr(a, "get_value", None)
    if callable(g):
        try:
            v = g()
            return v if isinstance(v, str) else str(v)
        except Exception:
            pass
    s = a if isinstance(a, str) else str(a)
    try:
        v = ast.literal_eval(s)
        if isinstance(v, str):
            return v
    except Exception:
        pass
    return s


def registry_lines(num):
    return load_registry().get(_key(num), {}).get("lines", [])


def registry_set(num, lines):
    reg = load_registry()
    reg[_key(num)] = {"lines": lines}
    return save_registry(reg)


def registry_remove(num):
    reg = load_registry()
    reg.pop(_key(num), None)
    return save_registry(reg)


# ====================================================================
# Flame helpers
# ====================================================================

def _get(obj, name):
    v = getattr(obj, name, None)
    return v() if callable(v) else v


def _safe_name(obj):
    try:
        return str(obj.name)
    except Exception:
        return type(obj).__name__


def _clean_name(obj):
    n = _safe_name(obj)
    if len(n) >= 2 and n[0] == n[-1] and n[0] in ("'", '"'):
        n = n[1:-1]
    return n


def _seg_name(seg):
    """Segment's own name for display -- blank if unnamed, with no type-name
    fallback (unlike _clean_name), so the Name column stays empty rather than
    showing 'PySegment'."""
    try:
        n = str(seg.name)
    except Exception:
        return ""
    if len(n) >= 2 and n[0] == n[-1] and n[0] in ("'", '"'):
        n = n[1:-1]
    return n.strip()


def get_type_fx(segment):
    try:
        return next((e for e in segment.effects
                     if type(e).__name__ == "PyTypeFX"), None)
    except Exception:
        return None


def _is_gap(seg):
    try:
        return str(seg.type) == "Gap Timeline FX"
    except Exception:
        return False


def read_tag(segment, pattern=TAG_RE):
    try:
        tags = segment.tags.get_value()
    except Exception:
        return None
    for t in (tags or []):
        if re.match(pattern, str(t)):
            return str(t)
    return None


def set_graphic_tag(segment, tag):
    """Set the segment's graphic tag, replacing any existing graphic/legacy tag,
    preserving unrelated tags."""
    try:
        existing = list(segment.tags.get_value() or [])
    except Exception:
        existing = []
    kept = [t for t in existing if not re.match(TAG_RE, str(t))]
    segment.tags.set_value(kept + [tag])


def tag_to_instance(tag):
    m = re.search(r"(\d+)$", tag or "")
    return m.group(1) if m else None


def instance_tag(num):
    return "graphic" + _key(num)


def _ancestor(seg, typename):
    p = getattr(seg, "parent", None)
    while p is not None:
        if type(p).__name__ == typename:
            return p
        p = getattr(p, "parent", None)
    return None


def _seqs_in(container):
    out, seen = [], set()

    def walk(o):
        if o is None or id(o) in seen:
            return
        seen.add(id(o))
        if type(o).__name__ == "PySequence":
            out.append(o)
            return
        for attr in ("sequences", "reels", "reel_groups", "libraries"):
            children = _get(o, attr)
            if children:
                for c in children:
                    walk(c)

    walk(container)
    return out


def _current_segment():
    try:
        return flame.timeline.current_segment
    except Exception:
        return None


def _is_sequences_reel(reel):
    """True if a PyReel is a Sequences reel (vs a regular/scratch reel). PyReel
    exposes .type (Flame's own API distinguishes 'sequences reels' as a scoping
    value); we match 'sequence' in it so we're robust to the exact label. If
    .type can't be read we INCLUDE the reel (fail open -> behaves like the whole
    reel group rather than silently hiding everything).
    NOTE: the exact .type string is unverified -- confirm on-box that a regular
    reel holding reference sequences is correctly excluded."""
    try:
        t = _get(reel, "type")
    except Exception:
        return True
    if t is None:
        return True
    return "sequence" in str(t).lower()


def sequences_for_scope(scope):
    s = (scope or "Current Reel").strip().lower()
    if s == "selected":
        out = []
        for e in (_get(flame.media_panel, "selected_entries") or []):
            out += _seqs_in(e)
        return out
    seg = _current_segment()
    if seg is None:
        return []
    if s == "current sequence":
        sq = _ancestor(seg, "PySequence")
        return [sq] if sq else []
    if s == "current reel":
        return _seqs_in(_ancestor(seg, "PyReel"))
    if s == "current reel group":
        return _seqs_in(_ancestor(seg, "PyReelGroup"))
    if s == "all sequences reels":
        # the reel group's SEQUENCES reels only -- skips regular reels (e.g. a
        # scratch reel holding reference sequences you don't want to touch)
        rg = _ancestor(seg, "PyReelGroup")
        if rg is None:
            return []
        out = []
        for reel in (_get(rg, "reels") or []):
            if _is_sequences_reel(reel):
                out += _seqs_in(reel)
        return out
    return []


def iter_segments(sequence):
    for ver in (_get(sequence, "versions") or []):
        for trk in (_get(ver, "tracks") or []):
            for seg in (_get(trk, "segments") or []):
                yield seg


_ASPECT_TOKENS = ("16x9", "9x16", "1x1", "4x5", "2x3", "3x2", "4x3", "21x9")
_ASPECT_RATIOS = {"16x9": 16 / 9, "9x16": 9 / 16, "1x1": 1.0, "4x5": 4 / 5}


def detect_aspect(seq):
    low = _safe_name(seq).lower().replace(":", "x")
    for tok in _ASPECT_TOKENS:
        if tok in low:
            return tok
    try:
        r = float(seq.width) / float(seq.height)
        return min(_ASPECT_RATIOS, key=lambda k: abs(_ASPECT_RATIOS[k] - r))
    except Exception:
        return "?"


def segment_matches(seg, settings):
    """Does this segment count as a graphic target, per the user's settings?"""
    if get_type_fx(seg) is None:
        return False
    if settings.get("match_mode", "Gap segments with Type") == "Gap segments with Type":
        if not _is_gap(seg):
            return False
    nf = (settings.get("name_contains") or "").strip().lower()
    if nf and nf not in _clean_name(seg).lower():
        return False
    tp = (settings.get("track_prefix") or "").strip()
    if tp:
        trk = _ancestor(seg, "PyTrack")
        tname = _clean_name(trk) if trk is not None else None
        # only exclude when we can read a track name that fails the prefix
        if tname and tname != "PyTrack" and not tname.startswith(tp):
            return False
    return True


# ====================================================================
# Operations  (registry -> Type; tags; native layout connections)
# ====================================================================

# The PyTypeFX add-layer method is UNVERIFIED (only layers[i].text read/write
# is confirmed). _add_layer tries these in order; success is judged purely by a
# layer-count readback, never by the call's return value. Once the real method
# is identified on-box, collapse this to the single verified call.
LAYER_ADD_METHODS = ("add_layer", "create_layer", "new_layer", "add_text_layer",
                     "append_layer", "duplicate_layer", "copy_layer")


def _add_layer(tfx):
    """Grow a Type FX by one layer. Tries LAYER_ADD_METHODS, trusting only a
    layer-count readback -- no blind mutation. Returns True if the count grew."""
    try:
        before = len(tfx.layers)
    except Exception:
        return False
    for nm in LAYER_ADD_METHODS:
        fn = getattr(tfx, nm, None)
        if not callable(fn):
            continue
        try:
            fn()
        except Exception:
            continue
        try:
            if len(tfx.layers) > before:
                return True
        except Exception:
            return False
    return False


def push_text(seg, lines, dry_run=False, warnings=None):
    """Write registry lines onto the segment's Type layers, creating layers as
    needed and BLANKING any extras -- the registry owns the whole Type, so a
    Type that shrinks must not leave its old last line on screen (the delete-
    layer API is unverified, hence blank rather than remove). A layer index is
    only written after a count readback confirms it exists; on a hard shortfall
    the extra lines are skipped (not silently lost) and a warning is appended
    for the panel."""
    tfx = get_type_fx(seg)
    if tfx is None:
        return []
    changes = []
    if not dry_run:
        try:
            while len(tfx.layers) < len(lines) and _add_layer(tfx):
                pass
        except Exception:
            pass
    layers = list(tfx.layers)
    for i, new in enumerate(lines):
        if i < len(layers):
            old = attr_text(layers[i])
            if old == new:
                continue
            changes.append((seg, i, old, new))
            if not dry_run:
                layers[i].text = new
        elif dry_run:
            # layer doesn't exist yet; the live run will try to create it
            changes.append((seg, i, "", new))
    for i in range(len(lines), len(layers)):
        old = attr_text(layers[i])
        if old == "":
            continue
        changes.append((seg, i, old, ""))
        if not dry_run:
            layers[i].text = ""
    if not dry_run and len(lines) > len(layers) and warnings is not None:
        warnings.append(
            "⚠ %s: its Type has %d layer(s), the registry text needs %d — extra layer(s) "
            "not written (could not add layers on this Type)."
            % (_clean_name(seg), len(layers), len(lines)))
    return changes


def segment_text(seg):
    """All Type layer texts on a segment, trailing blanks trimmed."""
    tfx = get_type_fx(seg)
    if tfx is None:
        return []
    lines = [attr_text(l) for l in tfx.layers]
    while lines and lines[-1].strip() == "":
        lines.pop()
    return lines


def assign_graphic(seg, num, dry_run=False):
    """Tag the segment to a graphic. Does NOT write text -- assigning only
    LABELS the segment. Text reaches a segment exclusively through an explicit,
    previewed Sync Text. So after assigning, a segment whose text differs from
    its registry entry shows OUT OF DATE until you Sync, and nothing on the
    timeline ever changes without you confirming it."""
    if not dry_run:
        set_graphic_tag(seg, instance_tag(num))


def sync_text(num, scope, dry_run=True, warnings=None):
    """Write registry text for graphicNN onto every tagged, matching segment
    in scope. One-directional: registry is the source of truth."""
    lines = registry_lines(num)
    tag = instance_tag(num)
    settings = load_settings()
    changes = []
    for seq in sequences_for_scope(scope):
        for seg in iter_segments(seq):
            if not segment_matches(seg, settings):
                continue
            if read_tag(seg) != tag:
                continue
            changes += push_text(seg, lines, dry_run, warnings)
    return changes


def text_sync_targets(rows, reg):
    """Pure: which of these scanned rows a Segments-tab Sync can write.
    rows = inventory dicts (a selection, or the whole scan); reg = the loaded
    registry. A registry entry with no lines is treated as missing -- pushing
    an empty list would blank every layer. Returns (targets, unassigned,
    no_entry): targets = [(row, lines)] in order, each row once."""
    targets, unassigned, no_entry, seen = [], 0, 0, set()
    for d in rows:
        if id(d) in seen:
            continue
        seen.add(id(d))
        num = d.get("num")
        if not num:
            unassigned += 1
            continue
        try:
            lines = (reg.get(_key(num)) or {}).get("lines") or []
        except (TypeError, ValueError):
            lines = []
        if not lines:
            no_entry += 1
            continue
        targets.append((d, list(lines)))
    return targets, unassigned, no_entry


def rows_sharing_gfx(selected, inv):
    """Pure: Sync Selected's reach -- every scanned row whose Type number matches
    one of the selected rows' (the number is the words, so it spans aspects).
    Returns (rows, unassigned_selected): rows in scan order; the count is of
    selected rows that carry no Type number and so contribute nothing."""
    nums, unassigned = set(), 0
    for d in selected:
        num = d.get("num")
        if not num:
            unassigned += 1
            continue
        try:
            nums.add(_key(num))
        except (TypeError, ValueError):
            unassigned += 1
    out = []
    for d in inv:
        try:
            if d.get("num") and _key(d["num"]) in nums:
                out.append(d)
        except (TypeError, ValueError):
            pass
    return out, unassigned


def format_text_changes(items, limit=12, width=58):
    """Pure: [(seq, num, layer_index, old, new)] -> (summary, detail) for the
    Sync confirm box. summary shows the first `limit` changes, each clipped to
    `width` characters AROUND WHERE OLD AND NEW FIRST DIFFER -- so a changed
    date at the end of a long legal is what you see, never two identical-
    looking halves. detail (Show Details) has every change in full. Newlines
    inside a layer show as a return sign."""
    def disp(t):
        return str(t).replace("\n", " \u23ce ")

    def first_diff(a, b):
        for k in range(min(len(a), len(b))):
            if a[k] != b[k]:
                return k
        return min(len(a), len(b))

    def clip(t, at):
        if len(t) <= width:
            return t
        start = max(0, min(at - width // 3, len(t) - width))
        out = t[start:start + width]
        return ("\u2026" if start else "") + out + ("\u2026" if start + width < len(t) else "")

    short, full = [], []
    for seq, num, li, old, new in items:
        o, w = disp(old), disp(new)
        at = first_diff(o, w)
        head = "%s  Type%s  layer %d:  " % (seq, num, li + 1)
        short.append(head + "\u201c%s\u201d  \u2192  \u201c%s\u201d" % (clip(o, at), clip(w, at)))
        full.append(head + "\n    was: \u201c%s\u201d\n    now: \u201c%s\u201d" % (o, w))
    shown = short[:limit]
    if len(short) > limit:
        shown.append("\u2026 and %d more (Show Details)" % (len(short) - limit))
    return "\n".join(shown), "\n".join(full)


def _in_sync(seg, lines):
    tfx = get_type_fx(seg)
    if tfx is None:
        return False
    layers = tfx.layers
    for i in range(len(lines)):
        if i >= len(layers) or attr_text(layers[i]) != lines[i]:
            return False
    # extras must be blank -- stale text past the registry's last line is
    # still visibly on screen, so it counts as out of date
    for i in range(len(lines), len(layers)):
        if attr_text(layers[i]).strip():
            return False
    return True


def graphic_inventory(scope, warnings=None, seqs=None):
    """Every matching Type segment in scope, assigned or not. One segment that
    throws (Flame properties can raise beyond AttributeError) is skipped and
    reported, instead of aborting the whole scan. Pass `seqs` (already resolved
    via sequences_for_scope) to avoid re-walking the hierarchy."""
    reg = load_registry()
    settings = load_settings()
    out = []
    if seqs is None:
        seqs = sequences_for_scope(scope)
    for seq in seqs:
        sname, aspect, fps = _clean_name(seq), detect_aspect(seq), _fps(seq)
        sdur = _get(seq, "duration")
        if sdur is None:
            sdur = _get(seq, "record_duration")
        seq_dur_f = _frames(sdur)        # sequence length, for "longest sequence"
        for seg in iter_segments(seq):
            try:
                if not segment_matches(seg, settings):
                    continue
                tfx = get_type_fx(seg)
                text = attr_text(tfx.layers[0]) if (tfx and len(tfx.layers)) else ""
                tag = read_tag(seg)
                num = tag_to_instance(tag) if tag else None
                sync = None
                if num is not None:
                    sync = _in_sync(seg, reg.get(num, {}).get("lines", []))
                try:
                    ncon = len(seg.connected_segments(scoping="all reels"))
                except Exception:
                    ncon = 0
                rin = getattr(seg, "record_in", None)
                dur_f = _frames(getattr(seg, "record_duration", None))
                out.append({"seq": sname, "aspect": aspect, "seg": seg, "text": text,
                            "num": num, "in_sync": sync, "connected": ncon,
                            "name": _seg_name(seg), "fps": fps,
                            "in_f": _frames(rin), "dur_f": dur_f,
                            "tc_in": _tc(rin, fps),
                            "tc_dur": _frames_to_tc(dur_f, fps),
                            "seq_dur_f": seq_dur_f})
            except Exception as e:
                msg = "⚠ scan skipped a segment in %s: %s" % (sname, e)
                log.warning(msg)
                if warnings is not None:
                    warnings.append(msg)
    return out


def _containers(seq):
    """Names of the two containers above a sequence (reel, reel group) -- part
    of every segment's identity key, and how a sequence is told apart from a
    same-named copy elsewhere. Flame props can raise beyond AttributeError:
    that must never sink a scan, so the walk just stops."""
    names = []
    try:
        box = getattr(seq, "parent", None)
        for _depth in range(2):
            if box is None:
                break
            names.append(_clean_name(box))
            box = getattr(box, "parent", None)
    except Exception:
        pass
    return tuple(names)


def _seg_uid(seg):
    """Cross-call identity. seg.uid reads None on box (Flame 2027.1, checked
    2026-09-23), so in practice the fallback runs: sequence + name + position,
    plus the names of the two containers above the sequence (reel, reel group).
    The containers matter: a drag-copied sequence keeps its name, so without
    them a still-connected copy in a Backup / reference reel would pass for the
    live segment. The uid branch stays for any Flame that fills it in. Two
    scanned segments that still share a key are reported by identity_collisions
    and never connected."""
    u = getattr(seg, "uid", None)
    if u:
        return ("uid", str(u))
    seq = _ancestor(seg, "PySequence")
    parts = [_clean_name(seq), _clean_name(seg)]
    for attr in ("record_in", "start", "start_frame", "source_in"):
        v = getattr(seg, attr, None)
        if v is not None:
            parts.append(str(v))
            break
    return tuple(parts) + _containers(seq)


def identity_collisions(keys):
    """{key: count} for identity keys shared by 2+ scanned segments. With
    seg.uid empty, two graphics in one sequence with the same name (often both
    blank) and the same In -- e.g. a super and a legal starting on one frame on
    different tracks -- get the same key, and the connection grouping, the
    queue and the Set as Source marks would treat them as ONE segment."""
    seen = {}
    for k in keys:
        seen[k] = seen.get(k, 0) + 1
    return {k: n for k, n in seen.items() if n > 1}


def _safe_delete(obj):
    """Remove a temporary media-panel clip. Returns (ok, error).
    flame.delete defaults to confirm=True, which a script can't answer: in the
    sibling tool CCM (same Flame) that made the delete a silent no-op and temp
    copies piled up in the reel. So pass confirm=False first; the older forms
    stay as fallbacks for a Flame that rejects the keyword."""
    why = []
    for label, fn in (("flame.delete(confirm=False)", lambda: flame.delete(obj, confirm=False)),
                      ("flame.delete", lambda: flame.delete(obj)),
                      ("clip.delete", lambda: obj.delete())):
        try:
            fn()
            return True, None
        except Exception as e:
            why.append("%s: %s" % (label, e))
    return False, "; ".join(why)


def _segment_location(seg):
    """(version_index, track_index) of a segment within its sequence, resolved
    from the real parent chain (segment -> PyTrack -> PyVersion -> PySequence).
    Flame stacks multiple versions/tracks, so versions[0] is NOT a safe guess."""
    track = seg.parent
    version = getattr(track, "parent", None)
    seq = _ancestor(seg, "PySequence")
    vi = ti = 0
    if seq is not None and version is not None:
        versions = list(seq.versions)
        if version in versions:
            vi = versions.index(version)
        vtracks = list(version.tracks)
        if track in vtracks:
            ti = vtracks.index(track)
    return vi, ti


def _frames(t):
    """PyTime -> integer frame count (verified: int(record_duration) works)."""
    for a in ("frame", "frames"):
        v = getattr(t, a, None)
        if isinstance(v, int):
            return v
    try:
        return int(t)
    except Exception:
        return None


def _fps(seq):
    """Sequence frame rate as a float. frame_rate may be a number or a string
    like '23.976 fps'. Defaults to 24.0."""
    try:
        v = _get(seq, "frame_rate")
        if isinstance(v, (int, float)):
            return float(v)
        if v is not None:
            m = re.search(r"\d+(?:\.\d+)?", str(v))
            if m:
                return float(m.group(0))
    except Exception:
        pass
    return 24.0


def _frames_to_tc(frames, fps):
    """Integer frames -> non-drop HH:MM:SS:FF at round(fps)."""
    if frames is None:
        return ""
    fpsi = max(1, int(round(fps or 24.0)))
    sign = "-" if frames < 0 else ""
    f = abs(int(frames))
    ff = f % fpsi
    s = f // fpsi
    return "%s%02d:%02d:%02d:%02d" % (sign, s // 3600, (s // 60) % 60, s % 60, ff)


def _native_tc(t):
    """A PyTime's own timecode string, if it exposes one -- this is the true
    timeline TC including any sequence start offset. None if unavailable."""
    if t is None:
        return None
    for a in ("timecode", "tc"):
        v = getattr(t, a, None)
        if v is not None and ":" in str(v):
            return str(v).strip("'\"")
    s = str(t).strip("'\"")
    return s if ":" in s else None


def _tc(t, fps):
    """Display timecode for a PyTime: prefer its native TC string, else compute
    from its frame count (non-drop)."""
    return _native_tc(t) or _frames_to_tc(_frames(t), fps)


def _segment_at(track, rec_in):
    """Segment on `track` whose record_in matches rec_in (compared as text,
    since PyTime equality is unreliable)."""
    key = str(rec_in)
    try:
        for s in track.segments:
            if str(s.record_in) == key:
                return s
    except Exception:
        pass
    return None


def _conn_count(seg):
    try:
        return len(seg.connected_segments(scoping="all reels"))
    except Exception:
        return 0


def _focus_sequence(seq):
    """Best-effort: bring a sequence to the foreground after a mutation.
    flame.timeline.clip has NO setter (verified), so this tries selection paths
    instead and silently no-ops if Flame exposes none -- the focus jump is a
    known cosmetic, not a failure."""
    if seq is None:
        return
    try:
        seq.selected = True
    except Exception:
        pass
    try:
        flame.media_panel.selected_entries = [seq]
    except Exception:
        pass


def _trim_clip_tail(clip, target_f):
    """Best-effort: shrink a freshly-copied media-panel clip to target_f frames
    BEFORE it is overwritten onto the timeline, so a master LONGER than the
    destination slot can never overwrite (destroy) the segment downstream of the
    slot. This is the key guard against the 'disappearing legal' case.

    The post-placement trim still runs and is the verified path; this is an extra
    pre-trim. The media-panel-clip trim API is unverified, so it is FULLY guarded
    -- on any problem we leave the clip as-is and behaviour falls back to exactly
    what it was before. Returns True only if it actually shrank.
    """
    if target_f is None:
        return False
    try:
        seg = next(iter_segments(clip), None)
        if seg is None:
            return False
        cur = _frames(seg.record_duration)
        if cur is None or cur <= target_f:
            return False                  # within the slot; extend happens later
        seg.trim_tail(cur - target_f, False)   # positive -> shrink (verified sign)
        return True
    except Exception:
        return False


def _connect_one(master_seg, dst_seg):
    """Replace dst_seg's content with a connected copy of master_seg, preserving
    dst_seg's record position, track, and ORIGINAL duration.

    Verified per-op (2027): copy master to the reel (shares source so it will
    connect), overwrite at dst's record_in on dst's OWN track (atomic replace,
    no track-index matching), re-find the placed segment, then
    trim_tail(current - target) to restore dst's length -- negative offset
    EXTENDS, positive SHRINKS. trim_tail returns False but applies.

    Two additive, non-destructive guards wrap that:
      - destination attrs are read defensively; a stale handle yields a clean
        error instead of a bad position.
      - the copied clip is pre-trimmed to the slot length before overwrite so an
        over-long master can't eat the segment downstream (the real fix for the
        'disappearing legal' report).
    (No uid match-guard before the overwrite: it could SKIP a valid connection if
    Flame's uid reads differently after a sibling edit, recreating the very
    'missing connections' symptom we fix. The proven baseline overwrote directly.)
    Returns (ok, error_or_None)."""
    reel = _ancestor(master_seg, "PyReel")
    dst_track = dst_seg.parent
    dst_seq = _ancestor(dst_seg, "PySequence")
    try:
        dst_in = dst_seg.record_in
        target_f = _frames(dst_seg.record_duration)
    except Exception as e:
        return False, "destination unreadable (stale handle?): %s" % e

    clip = None
    try:
        clip = master_seg.copy_to_media_panel(reel)
        _trim_clip_tail(clip, target_f)        # pre-trim guard (best-effort)
        dst_seq.overwrite(clip, dst_in, dst_track)
    except Exception as e:
        if clip is not None and not _safe_delete(clip)[0]:
            return False, "%s (and the temp copy is still in the reel -- delete it by hand)" % e
        return False, str(e)
    # the temp copy sits in the reel the scopes scan; say so if it survives
    del_ok, del_err = _safe_delete(clip)
    leftover = None if del_ok else (
        "temp copy left in the reel -- delete it by hand (%s)" % del_err)
    placed = _segment_at(dst_track, dst_in)
    if placed is None:
        return False, "; ".join(x for x in (
            "placed segment not found at %s" % dst_in, leftover) if x)
    cur_f = _frames(placed.record_duration)
    if target_f is not None and cur_f is not None:
        delta = cur_f - target_f          # +shrink / -extend (verified)
        if delta:
            try:
                placed.trim_tail(delta, False)   # ripple=False
            except Exception as e:
                return True, "; ".join(x for x in (
                    "placed but trim failed: %s" % e, leftover) if x)
    return True, leftover


def resolve_group_source(uids, marked):
    """Pick the explicit source for a connection group. uids = the group's seg
    uids; marked = the set of user-marked source uids. Returns (index, error):
      - exactly one marked in the group -> (its index, None)
      - none marked                     -> (None, None)   # caller auto-picks
      - two or more marked              -> (None, error)   # ambiguous, refuse
    """
    hits = [i for i, u in enumerate(uids) if u in marked]
    if len(hits) > 1:
        return None, ("%d segments in this group are marked as source — "
                      "mark only one." % len(hits))
    return (hits[0] if hits else None), None


def connect_segment_group(segs, master=None):
    """Mutually connect a set of same-aspect segments the user has declared to be
    the same graphic. The master (whose layout propagates) is the one passed in;
    if None, auto-pick an already-connected member, else the first. Arms it, then
    folds every other segment into that connection by replacing its content with a
    connected copy of the master -- each destination keeps its own slot and
    duration.
    Returns (done_count, master_seg, errors)."""
    if not segs:
        return 0, None, []
    if master is None:
        master = next((s for s in segs if _conn_count(s) > 0), segs[0])
    try:
        master.create_connection()       # arm so copies join this group
    except Exception:
        pass                             # already connected -> fine
    done, errors = 0, []
    for dst in segs:
        if dst is master:
            continue
        ok, err = _connect_one(master, dst)
        sq = _clean_name(_ancestor(dst, "PySequence"))
        if ok:
            done += 1
            if err:
                errors.append((sq, err))
        else:
            errors.append((sq, err))
    return done, master, errors


def _grp_label(k):
    s = ""
    k += 1
    while k > 0:
        k, r = divmod(k - 1, 26)
        s = chr(65 + r) + s
    return s


def connection_groups(inv, outside=None):
    """Union-find over connected_segments() -> list of groups (each a list of
    inv indices). Multi-member groups (real connections) come first. Pass a
    dict as `outside` to also count, per scanned segment, connected peers that
    are NOT in the scan (another reel, outside the scope) -- a segment whose
    only partners are elsewhere is still part of a connected set. Each entry
    is the SET of those partners' keys, so one outside partner shared by three
    scanned members counts once."""
    n = len(inv)
    uids = [_seg_uid(d["seg"]) for d in inv]
    idx = {}
    for i, u in enumerate(uids):
        idx.setdefault(u, i)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for i, d in enumerate(inv):
        try:
            cs = d["seg"].connected_segments(scoping="all reels")
        except Exception:
            cs = []
        for c in cs:
            j = idx.get(_seg_uid(c))
            if j is not None:
                union(i, j)
            elif outside is not None:
                outside.setdefault(i, set()).add(_seg_uid(c))
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=lambda g: (len(g) == 1, -len(g)))


def link_facts(groups, outside, keys):
    """Pure: connection_groups' result -> (cluster_of, cluster_size, tainted).
      cluster_of    {inv index: set id}
      cluster_size  scanned members + partners outside the scan, so a set that
                    lives partly in another reel still counts as connected
      tainted       every scanned segment in a set that holds a segment whose
                    identity key collides with another's. seg.uid is None, so
                    the key is sequence + name + In, and the grouping around a
                    collision can't be trusted -- nothing there is connected."""
    cluster_of, size = {}, {}
    for cid, g in enumerate(groups):
        far = set()
        for i in g:
            far |= set(outside.get(i) or ())
        size[cid] = len(g) + len(far)
        for i in g:
            cluster_of[i] = cid
    clash = identity_collisions(keys)
    bad = {cluster_of.get(i) for i, k in enumerate(keys) if k in clash}
    tainted = {i for i, c in cluster_of.items() if c in bad}
    return cluster_of, size, tainted


def link_context(inv):
    """One connection read for a scan -> (groups, cluster_of, cluster_size,
    tainted, keys). Every connection decision (Auto Connection, the Q rows,
    Execute Queue, Multi Segment Connection) plans from this."""
    outside = {}
    groups = connection_groups(inv, outside) if inv else []
    keys = [_seg_uid(d["seg"]) for d in inv]
    cluster_of, size, tainted = link_facts(groups, outside, keys)
    return groups, cluster_of, size, tainted, keys


def plan_connection_group(idxs, cluster_of, cluster_size, marked=(), tainted=()):
    """Pure plan for one connection group (inv indices), against the connected
    sets as they stand. A set is WIRED when it has 2+ members (partners outside
    the scan count), LOOSE otherwise. The Q rows, Execute Queue and Multi
    Segment Connection's confirm box all read this plan, so what is previewed is
    what runs. Returns a dict:
      work      False when fewer than 2 members resolve or all are already in
                one set -- nothing to do
      anchor    the one wired set the group JOINS; None when every member is
                loose, or when members come from 2+ wired sets (a merge)
      targets   the members the group replaces: those outside the anchor set,
                so the set itself is never re-copied. With no anchor, the whole
                group (its master is picked later: Set as Source, else auto)
      master    joining: a Set as Source mark anywhere in the anchor set, else
                the group's first set member. Re-lay-out: the marked segment.
      relayout  a mark on a joining segment while the group holds the WHOLE set
                (and none of the set is outside the scan): that segment's layout
                replaces the set's. With only part of the set in the group this
                would split it, so it's refused.
      set       the anchor set's scanned members (the layout source a join
                READS), so the queue can refuse a later group that replaces them
      error     refused -- identity collision, 2+ marks, or a mark that would
                split the set. targets stay filled so the Q rows can show it.
    """
    idxs = list(dict.fromkeys(idxs))                  # de-dupe, keep order
    out = {"work": False, "anchor": None, "targets": [], "master": None,
           "relayout": False, "error": None, "set": []}
    cid = {i: cluster_of.get(i, ("solo", i)) for i in idxs}
    if len(idxs) < 2 or len(set(cid.values())) < 2:
        return out
    out["work"] = True
    wired = []
    for i in idxs:
        if cluster_size.get(cid[i], 1) > 1 and cid[i] not in wired:
            wired.append(cid[i])
    anchor = wired[0] if len(wired) == 1 else None
    members = [i for i, c in cluster_of.items() if c == anchor] if anchor is not None else []
    out["anchor"] = anchor
    out["set"] = members
    out["targets"] = [i for i in idxs if cid[i] != anchor] if anchor is not None else idxs
    if any(i in tainted for i in idxs) or any(i in tainted for i in members):
        out["error"] = ("two graphics here share a sequence, name and In, so they can't be "
                        "told apart — give one of each pair a segment name in Flame, then rescan.")
        return out
    if anchor is None:
        n_mk = len([i for i in idxs if i in marked])
        if n_mk > 1:                  # _group_master would refuse it at run time
            out["error"] = ("%d segments in this group are marked as source \u2014 "
                            "mark only one." % n_mk)
        return out
    mk_in = [i for i in members if i in marked]
    mk_out = [i for i in out["targets"] if i in marked]
    if len(mk_in) + len(mk_out) > 1:
        out["error"] = ("%d segments in this group or its connected set are marked as source "
                        "— mark only one." % (len(mk_in) + len(mk_out)))
    elif mk_out:
        whole = set(members) <= set(idxs)
        inside = cluster_size.get(anchor, 0) <= len(members)
        if whole and inside:
            out["relayout"] = True
            out["master"] = mk_out[0]
            out["targets"] = [i for i in idxs if i != mk_out[0]]
        elif whole:
            out["error"] = ("%d segment(s) connected to this set are outside the current "
                            "Scope, so re-laying it out here would split them off \u2014 widen "
                            "the Scope to include them first."
                            % (cluster_size.get(anchor, 0) - len(members)))
        else:
            out["error"] = ("the marked source is a segment that isn't in the connected set yet "
                            "— copying it over only part of the set would split it. Unmark it "
                            "to use the set's layout, or select the WHOLE set plus it for Multi "
                            "Segment Connection to re-lay-out everything.")
    else:
        out["master"] = mk_in[0] if mk_in else next(i for i in idxs if cid[i] == anchor)
    return out


def resolve_queue(queue, key_to_idx, cluster_of, cluster_size, marked=(), tainted=()):
    """Pure: plan every queued group (identity-key lists) in order -- the same
    call feeds the Q rows and Execute Queue. One entry per group:
      {"idxs", "plan", "missing", "overlap"}
    missing  members no longer in the scan (scope changed). Such a group is
             dropped, never re-planned into something the user didn't review.
    overlap  queue position of an EARLIER runnable group this one conflicts
             with: it uses a segment that group replaces (the handle would be
             stale), or it replaces a segment that group copied its layout from
             (a join into a set that a later re-lay-out replaces would be left
             behind in the old set). A conflicting group doesn't run."""
    out, wrote, read = [], {}, {}
    for gi, g in enumerate(queue):
        idxs, missing = [], 0
        for u in g:
            i = key_to_idx.get(u)
            if i is None:
                missing += 1
            elif i not in idxs:
                idxs.append(i)
        plan = plan_connection_group(idxs, cluster_of, cluster_size, marked, tainted)
        writes = set(plan["targets"])
        reads = set() if plan["relayout"] else set(plan["set"])
        if plan["master"] is not None:
            reads.add(plan["master"])
        hits = [wrote[i] for i in writes | reads if i in wrote]
        hits += [read[i] for i in writes if i in read]
        overlap = min(hits) if hits else None
        if not missing and plan["work"] and not plan["error"] and overlap is None:
            for i in writes:
                wrote.setdefault(i, gi)
            for i in reads:
                read.setdefault(i, gi)
        out.append({"idxs": idxs, "plan": plan, "missing": missing, "overlap": overlap})
    return out


def auto_connection_groups(inv, ctx=None):
    """Propose connection groups automatically from the (aspect, Type#) of each
    segment -- the same key a human applies by hand: line up like aspects for
    like graphics. Reads connections once via link_context (partners outside the
    scan count) unless the caller passes that context in; no timeline change.

    Per (aspect, Type#) bucket with 2+ members:
      - touches an identity collision    -> left alone, reported as unsafe
      - all in one connected set         -> already connected, skipped
      - no member connected yet          -> one group of all of them
      - ONE connected set + loose ones   -> the loose ones JOIN that set: one
                                            group = an anchor from the set + the
                                            loose members (the set itself is not
                                            re-copied)
      - 2+ separate connected sets       -> left alone and reported as split:
                                            which layout wins is the user's call
    Re-running is idempotent. Segments with no Type number are counted, skipped.

    Returns (groups, already_connected, unassigned, split, unsafe):
      groups            [{"idxs": [...], "anchor": idx or None}], by aspect then
                        Type; with an anchor, idxs[0] is it
      already_connected count of buckets skipped as already wired
      unassigned        count of segments skipped for having no Type number
      split             [(aspect, num, n_sets, n_loose)] buckets left alone
      unsafe            [(aspect, num)] buckets left alone (identity collision)
    """
    _g, cluster_of, size, tainted, _k = ctx if ctx is not None else link_context(inv)
    buckets, unassigned = {}, 0
    for i, d in enumerate(inv):
        if d.get("num") is None:
            unassigned += 1
            continue
        buckets.setdefault((d["aspect"], d["num"]), []).append(i)
    groups, already_connected, split, unsafe = [], 0, [], []
    for key in sorted(buckets):
        idxs = buckets[key]
        if len(idxs) < 2:
            continue                      # only one occurrence -> nothing to join
        if any(i in tainted for i in idxs):
            unsafe.append(key)
            continue
        wired, loose = [], []
        for i in idxs:
            c = cluster_of.get(i)
            if size.get(c, 1) > 1:
                if c not in wired:
                    wired.append(c)
            else:
                loose.append(i)
        if len(wired) > 1:
            split.append((key[0], key[1], len(wired), len(loose)))
        elif not wired:
            groups.append({"idxs": idxs, "anchor": None})
        elif not loose:
            already_connected += 1        # all share one set -> already wired
        else:
            anchor = next(i for i in idxs if cluster_of.get(i) == wired[0])
            groups.append({"idxs": [anchor] + loose, "anchor": anchor})
    return groups, already_connected, unassigned, split, unsafe


def _rel_record_pos(seg):
    """Frames from the start of the sequence to this segment. A Flame track is
    a contiguous run of segments (gaps included) from the sequence start, so
    the offset is this record_in minus the track's FIRST segment's record_in --
    both read in the same basis, so the 1-frame record_in skew CCM found on
    gap-headed sequences cancels out. None if it can't be read."""
    try:
        trk = _ancestor(seg, "PyTrack")
        segs = list(_get(trk, "segments") or [])
        a = _frames(getattr(seg, "record_in", None))
        b = _frames(getattr(segs[0], "record_in", None)) if segs else None
        if a is not None and b is not None and a >= b:
            return a - b
    except Exception:
        pass
    return None


def _aspect_rank(aspect):
    return (_ASPECT_TOKENS.index(aspect) if aspect in _ASPECT_TOKENS
            else len(_ASPECT_TOKENS) + (1 if aspect == "?" else 0), str(aspect))


def timeline_lanes(blocks, seq_info):
    """Pure layout for the Timelines tab. blocks = [{"idx", "seq", "start",
    "dur"}] (frames from the sequence start); seq_info = {seq: (aspect,
    duration_frames)}. Returns lanes in display order -- grouped by aspect
    (16x9, 9x16, 1x1, 4x5, ... then unknown), sequences by name -- each
    {"seq", "aspect", "dur", "rows"}: rows = lists of block idx, packed so
    graphics that overlap in time sit on separate rows (first free row wins)."""
    by_seq = {}
    for b in blocks:
        by_seq.setdefault(b["seq"], []).append(b)
    order = sorted(by_seq, key=lambda q: (_aspect_rank(seq_info.get(q, ("?", 0))[0]), q))
    lanes = []
    for q in order:
        rows, ends = [], []
        for b in sorted(by_seq[q], key=lambda b: (b["start"], -b["dur"], b["idx"])):
            for r, end in enumerate(ends):
                if b["start"] >= end:
                    rows[r].append(b["idx"])
                    ends[r] = b["start"] + max(1, b["dur"])
                    break
            else:
                rows.append([b["idx"]])
                ends.append(b["start"] + max(1, b["dur"]))
        aspect, dur = seq_info.get(q, ("?", 0))
        dur = max([dur or 0] + [b["start"] + b["dur"] for b in by_seq[q]])
        lanes.append({"seq": q, "aspect": aspect, "dur": dur, "rows": rows})
    return lanes


def set_colour_slots(cluster_of, cluster_size, idxs, gfx_of=None, n_colours=10):
    """Pure: {set id: colour slot 0..n_colours-1} for every CONNECTED set among
    idxs, in first-seen order (stable scan to scan); loose graphics get none.
    Colours repeat once there are more sets than colours, so the slot is chosen
    so that sets sharing a Type number (gfx_of = {idx: gfx}) never share a
    colour -- two looks of one graphic must never read as one."""
    gfx_of = gfx_of or {}
    sets, order = {}, []
    for i in idxs:
        c = cluster_of.get(i)
        if c is not None and cluster_size.get(c, 1) > 1:
            if c not in sets:
                sets[c] = set()
                order.append(c)
            if gfx_of.get(i):
                sets[c].add(gfx_of[i])
    slots, used_by_gfx = {}, {}
    for k, c in enumerate(order):
        taken = set()
        for g in sets[c]:
            taken |= used_by_gfx.get(g, set())
        free = [s for s in range(n_colours) if s not in taken]
        slot = min(free, key=lambda s: ((s - k) % n_colours)) if free else k % n_colours
        slots[c] = slot
        for g in sets[c]:
            used_by_gfx.setdefault(g, set()).add(slot)
    return slots


def group_letters(groups, cluster_size):
    """Pure: {set id: letter} for EVERY look in a scan -- connected sets first
    (A, B, ...), then each lone graphic (its layout is its own), in group
    order; after Z it rolls over to AA, AB, ... Both the Connections and the
    Timelines tabs use this, so a letter means the same look everywhere."""
    wired = [cid for cid, _g in enumerate(groups) if cluster_size.get(cid, 1) > 1]
    loose = [cid for cid, _g in enumerate(groups) if cluster_size.get(cid, 1) <= 1]
    return {cid: _grp_label(k) for k, cid in enumerate(wired + loose)}


def _attr_value(v):
    g = getattr(v, "get_value", None)
    return g() if callable(g) else v


def _layer_look(layer):
    """{attribute: value} for everything a Type layer exposes through its
    `attributes` name list (text, position, scale, font, font_size, width,
    justification, colours, ... -- 55 on 2027.1, all settable; probe
    2026-09-24). Read-only."""
    out = {}
    for a in list(getattr(layer, "attributes", None) or []):
        try:
            out[a] = _attr_value(getattr(layer, a))
        except Exception:
            pass
    return out


PREVIEW_RECIPE = 2      # bump when the render recipe changes -> old cache unused
# Type FX attributes that are only Flame UI state (the Type editor's selection
# and on-screen guides) -- they don't change the render, so they're left out.
_FX_UI_ONLY = ("selected_layers", "current_layer", "show_char_pos", "show_char_axis",
               "show_para_axis", "show_layer_axis")


def look_signature(looks, frame_wh, extra=None):
    """Pure: a short, stable fingerprint of everything that decides how a
    graphic renders -- every attribute of every layer (text included), the
    frame size, and `extra` (the Type FX's own attributes such as bypass, and
    whether the segment / its track is hidden -- a hidden or bypassed graphic
    renders WITHOUT its text, so it must never share a key with a visible one). Two graphics with the same signature look identical, so the
    real-render preview is made once per distinct look ("once per positioning"),
    and any change in Flame (text, position, size...) makes a new one."""
    blob = repr((PREVIEW_RECIPE, tuple(frame_wh or ()),
                 [sorted((str(k), repr(v)) for k, v in lk.items()) for lk in looks],
                 sorted((str(k), repr(v)) for k, v in (extra or {}).items())))
    return hashlib.sha1(blob.encode("utf-8")).hexdigest()[:20]


def drawn_geometry(look, frame_w, frame_h):
    """Pure: where one Type layer sits, in frame pixels (origin top-left) -- an
    estimate from its attributes, for framing the text in the preview (Flame's
    render is the truth). Flame's Type positions are frame-centred with y up;
    the box width and font size are read as pixels, scaled by the layer's scale.
    Returns
    {cx, cy, box_w, font_px, align, family, style} or None for a hidden layer."""
    if look.get("hidden"):
        return None

    def pair(v, dflt):
        try:
            return float(v[0]), float(v[1])
        except Exception:
            return dflt
    px, py = pair(look.get("position"), (0.0, 0.0))
    sx, sy = pair(look.get("scale"), (100.0, 100.0))
    try:
        box = float(look.get("width") or 0) or frame_w * 0.8
    except (TypeError, ValueError):
        box = frame_w * 0.8
    try:
        size = float(look.get("font_size") or 32)
    except (TypeError, ValueError):
        size = 32.0
    font = look.get("font") or ("", "")
    fam = str(font[0]) if isinstance(font, (tuple, list)) and font else str(font)
    sty = str(font[1]) if isinstance(font, (tuple, list)) and len(font) > 1 else ""
    j = str(look.get("justification") or "Centre").lower()
    align = "left" if j.startswith("left") else "right" if j.startswith("right") else "centre"
    return {"cx": frame_w / 2.0 + px, "cy": frame_h / 2.0 - py,
            "box_w": box * sx / 100.0, "font_px": size * sy / 100.0,
            "align": align, "family": fam, "style": sty}


PREVIEW_ZOOMS = (25, 50, 100, 200, 400)   # % of FRAME pixels (100% = 1:1, as Flame's viewer)


def text_box(looks, frame_w, frame_h):
    """Pure: the frame-px rect (x, y, w, h) the Text button frames -- the union
    of the visible layers' estimated text blocks (drawn_geometry's box; lines
    estimated from the text length at about half an em a character), padded by
    a line top and bottom and 5% of the frame width each side, kept inside the
    frame -- or None. An estimate: Flame's render is the truth."""
    rects = []
    for look in looks or []:
        text = str(look.get("text") or "")
        if not text.strip():
            continue
        g = drawn_geometry(look, frame_w, frame_h)
        if not g:
            continue
        fpx, bw = max(1.0, g["font_px"]), max(1.0, g["box_w"])
        lines = sum(max(1, int(-(-(len(par) * 0.5 * fpx) // bw))) for par in text.split("\n"))
        h, pad = lines * fpx * 1.2, fpx * 1.2
        rects.append((g["cx"] - bw / 2.0 - frame_w * 0.05, g["cy"] - h / 2.0 - pad,
                      g["cx"] + bw / 2.0 + frame_w * 0.05, g["cy"] + h / 2.0 + pad))
    if not rects:
        return None
    x0, y0 = max(0.0, min(r[0] for r in rects)), max(0.0, min(r[1] for r in rects))
    x1, y1 = min(float(frame_w), max(r[2] for r in rects)), min(float(frame_h), max(r[3] for r in rects))
    if x1 <= x0 or y1 <= y0:
        return None
    return (x0, y0, x1 - x0, y1 - y0)


# ---------------------------------------------------------------- real render
# One frame of a SEQUENCE (picture + Type composited) as a JPEG. Verified on
# box 2026-09-24 (a one-frame render probe): temporary In/Out marks around one frame,
# PyExporter foreground + export_between_marks, ~1 s, no dialog, marks restored.

def _find_jpeg_preset():
    """A shipped JPEG image-sequence export preset (the enum args are required;
    same search as the sibling tool CCM)."""
    ex = flame.PyExporter
    for vis_name in ("Autodesk", "Shared", "Project"):
        vis = getattr(ex.PresetVisibility, vis_name, None)
        if vis is None:
            continue
        for typ_name in ("Image_Sequence", "ImageSequence", "Image"):
            typ = getattr(ex.PresetType, typ_name, None)
            if typ is None:
                continue
            try:
                d = str(ex.get_presets_dir(vis, typ))
            except Exception:
                continue
            for root, _dirs, files in os.walk(d):
                for fn in sorted(files):
                    if fn.lower().endswith(".xml") and "jpeg" in fn.lower():
                        return os.path.join(root, fn)
    return None


def _preview_size(frame_wh, long_side=720):
    """Pure: the preview's pixel size -- the frame's own aspect, long side
    `long_side`, even numbers (so nothing is letterboxed or cropped)."""
    try:
        w, h = float(frame_wh[0]), float(frame_wh[1])
    except Exception:
        w, h = 0.0, 0.0
    if w <= 0 or h <= 0:
        w, h = 16.0, 9.0                         # unknown: a 16:9 guess at long_side
    elif long_side >= max(w, h):
        return int(round(w)), int(round(h))      # native: the frame's own size, exactly
    if w >= h:
        return long_side, max(2, int(round(long_side * h / w / 2.0)) * 2)
    return max(2, int(round(long_side * w / h / 2.0)) * 2), long_side


# the Timelines preview JPEG's long side (Settings > Preview size); 0 = the
# sequence's own size. Never bigger than the sequence: Flame renders the frame
# at full size anyway, only the final resize + JPEG encode change.
PREVIEW_SIZES = (("Native (the sequence's own size)", 0), ("4K (3840 px)", 3840),
                 ("HD (1920 px)", 1920), ("720 px (fastest)", 720))


def preview_long_side(setting, frame_wh):
    """Pure: the preview JPEG's long side for the Preview size setting -- 0 =
    the frame's own long side (Native, the default); otherwise the setting,
    capped at the frame's long side (a preview is never upscaled). Missing or
    odd values -> Native; an unknown frame -> 720."""
    try:
        native = int(max(float(frame_wh[0]), float(frame_wh[1])))
    except Exception:
        native = 0
    try:
        want = int(setting)
    except (TypeError, ValueError):
        want = 0
    if want < 0 or (want and want not in [v for _l, v in PREVIEW_SIZES]):
        want = 0
    if native <= 0:
        return want or 720
    return native if want == 0 else min(want, native)


def splitter_sizes(v, n=2):
    """Pure: a remembered QSplitter size list -> [int, ...] when it's `n`
    positive numbers, else None (missing, hand-edited, or taken while a pane
    was hidden -- Qt reports a hidden pane as 0)."""
    if not isinstance(v, (list, tuple)) or len(v) != n:
        return None
    out = []
    for x in v:
        if isinstance(x, bool) or not isinstance(x, (int, float)) or x != x:
            return None
        if x <= 0 or x > 100000:
            return None
        out.append(int(x))
    return out


def fit_window_size(saved, avail=None, default=(860, 820)):
    """Pure: the window size to open at -- the remembered [w, h] (or the
    default when it's missing or odd), shrunk to fit the screen's available
    area `avail` (w, h) less a margin, never below 400 x 300."""
    w, h = default
    try:
        if isinstance(saved, (list, tuple)) and len(saved) == 2 and \
                not any(isinstance(x, bool) for x in saved):
            sw, sh = int(saved[0]), int(saved[1])
            if sw > 0 and sh > 0:
                w, h = sw, sh
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        aw, ah = int(avail[0]), int(avail[1])
        if aw > 0 and ah > 0:
            w, h = min(w, max(400, aw - 40)), min(h, max(300, ah - 60))
    except (TypeError, ValueError, IndexError, OverflowError):
        pass
    return max(400, w), max(300, h)


def _small_preset(preset, work_dir, frame_wh=None, long_side=720):
    """Copy of the preset resized to the frame's own aspect with a `long_side`
    long side (see _preview_size; Settings > Preview size) and JPEG quality 85
    (92 above 720 px, where the text is meant to be crisp), so a 4K sequence
    doesn't export a 4K, quality-100 JPEG for a side-panel preview by default."""
    bw, bh = _preview_size(frame_wh, long_side)
    try:
        with open(preset, encoding="utf-8") as f:
            txt = f.read()
        if "<resize>" not in txt:
            return preset
        txt = re.sub(r"<width>\d+</width>", "<width>%d</width>" % bw, txt)
        txt = re.sub(r"<height>\d+</height>", "<height>%d</height>" % bh, txt)
        txt = re.sub(r"<compressionQuality>\d+</compressionQuality>",
                     "<compressionQuality>%d</compressionQuality>"
                     % (85 if long_side <= 720 else 92), txt)
        txt = re.sub(r"<resizeType>[^<]*</resizeType>", "<resizeType>fit</resizeType>", txt)
        out = os.path.join(work_dir, "type_sync_preview_preset.xml")
        with open(out, "w", encoding="utf-8") as f:
            f.write(txt)
        return out
    except Exception:
        return preset


def _put_attr(obj, name, value):
    try:
        sv = getattr(getattr(obj, name), "set_value", None)
        if callable(sv):
            sv(value)
            return True
    except Exception:
        pass
    try:
        setattr(obj, name, value)
        return True
    except Exception:
        return False


def _place_jpeg(src_dir, out_jpg):
    """Move the exported JPEG into place. Copied in under a temp name, then
    renamed: a half-written file (disk full, network hiccup) never sits at the
    cached path. False when the export wrote no JPEG."""
    jpgs = []
    for root, _dirs, fns in os.walk(src_dir):
        jpgs += [os.path.join(root, f) for f in fns if f.lower().endswith((".jpg", ".jpeg"))]
    if not jpgs:
        return False
    os.makedirs(os.path.dirname(out_jpg), exist_ok=True)
    part = "%s.%d.part" % (out_jpg, os.getpid())   # unique per Flame host process
    try:
        shutil.move(sorted(jpgs)[0], part)
        os.replace(part, out_jpg)
    except Exception:
        try:
            os.remove(part)                     # never leave a partial copy behind
        except OSError:
            pass
        raise
    return True


GRAPHIC_TMP_SEQ = "type_sync_preview_tmp"


def _try_load(fx, path):
    try:
        return bool(fx.load_setup(path))
    except Exception:
        return False


def render_graphic_only(seg, out_jpg, long_side=720):
    """Export JUST this graphic's Type -- none of the picture under it -- to
    out_jpg: the Type's setup is saved to a temp file and loaded into a fresh
    Type on a temporary one-track sequence of the same format in the first
    Desktop reel; its middle frame is exported, then the temporary sequence is
    deleted. Flame draws the text, so it's exact, and it's quick however heavy
    the timeline is (~0.5 s in a test project). The user's sequence is never
    touched -- not even its marks -- and no user segment is copied, so no
    connection set is ever joined. Returns (ok, note)."""
    tfx = get_type_fx(seg)
    seq = _ancestor(seg, "PySequence")
    if tfx is None or seq is None:
        return False, "can't find this graphic's Type (press Rescan)"
    try:
        wh = (int(_attr_value(seq.width)), int(_attr_value(seq.height)))
    except Exception:
        return False, "can't read the sequence's size"
    fmt = {}
    for a in ("ratio", "bit_depth", "scan_mode", "frame_rate"):
        try:
            v = _attr_value(getattr(seq, a, None))
        except Exception:
            v = None
        if v is not None:
            fmt[a] = v
    dur = max(1, _frames(getattr(seg, "record_duration", None)) or 1)
    try:
        preset = _find_jpeg_preset()
    except Exception as e:
        return False, "no JPEG export preset (%s)" % e
    if not preset:
        return False, "no JPEG export preset found"
    try:
        desk = flame.projects.current_project.current_workspace.desktop
        reel = list(list(desk.reel_groups)[0].reels)[0]
    except Exception:
        return False, "no Desktop reel to render in"
    try:
        work = tempfile.mkdtemp(prefix="type_sync_graphic_")   # holds the legal's text
    except Exception as e:
        return False, "no temp folder for the render (%s)" % e
    ok, note, tmp = False, None, None
    try:
        base = os.path.join(work, "legal")
        if not tfx.save_setup(base):
            raise RuntimeError("Flame wouldn't save the Type setup")
        saved = [os.path.join(work, f) for f in sorted(os.listdir(work))]
        kw = dict(name=GRAPHIC_TMP_SEQ, video_tracks=1, width=wh[0], height=wh[1],
                  duration=dur, audio_tracks=0)
        try:
            tmp = reel.create_sequence(**dict(kw, **fmt))
        except Exception:
            tmp = reel.create_sequence(**kw)            # the size is what matters
        if isinstance(tmp, (list, tuple)):
            tmp = tmp[0] if tmp else None
        if tmp is None:
            raise RuntimeError("Flame wouldn't make the temporary sequence")

        def gap():
            return list(list(list(tmp.versions)[0].tracks)[0].segments)[0]
        fx2 = None
        for name in dict.fromkeys([str(_attr_value(getattr(tfx, "type", None)) or "Type"), "Type"]):
            try:
                r = gap().create_effect(name)
            except Exception:
                continue
            fx2 = r if type(r).__name__ == "PyTypeFX" else get_type_fx(gap())
            if fx2 is not None:
                break
        if fx2 is None:
            raise RuntimeError("Flame wouldn't add a Type to the temporary sequence")
        if not any(_try_load(fx2, pth) for pth in [base] + saved):
            raise RuntimeError("Flame wouldn't load the Type setup")
        preset = _small_preset(preset, work, wh, long_side)
        if not (_put_attr(tmp, "in_mark", flame.PyTime(dur // 2 + 1)) and
                _put_attr(tmp, "out_mark", flame.PyTime(dur // 2 + 2))):
            raise RuntimeError("couldn't set the marks for the export")
        ex = flame.PyExporter()
        ex.foreground = True
        ex.export_between_marks = True
        for a in ("warn_on_unrendered", "warn_on_pending_render", "warn_on_no_media",
                  "warn_on_unlinked", "warn_on_mixed_colour_space"):
            _put_attr(ex, a, False)                 # a black gap needs no questions
        _put_attr(ex, "keep_timeline_fx_renders", False)
        out = os.path.join(work, "out")
        os.makedirs(out)
        ex.export(tmp, preset, out)
        if not _place_jpeg(out, out_jpg):
            raise RuntimeError("the export wrote no JPEG")
        ok = True
    except Exception as e:
        note = str(e) or type(e).__name__
    finally:
        if tmp is not None:
            try:
                gone = flame.delete(tmp, confirm=False) is not False
            except Exception:
                gone = False
            if not gone:
                left = ("a temporary sequence '%s' was left in the first Desktop reel -- "
                        "delete it by hand" % GRAPHIC_TMP_SEQ)
                note = left if ok else "%s; %s" % (note, left)
        shutil.rmtree(work, ignore_errors=True)
    return ok, note


def render_graphic_frame(seg, out_jpg, long_side=720):
    """Export the middle frame of this graphic's SEQUENCE -- everything on
    screen at that frame, the Type included -- to out_jpg. The sequence's In/Out
    marks are set around that one frame for the export and ALWAYS put back.
    Returns (ok, note): note is an error, or a warning if the marks couldn't be
    restored."""
    seq = _ancestor(seg, "PySequence")
    rel = _rel_record_pos(seg)
    if seq is None or rel is None:
        return False, "can't place this graphic in its sequence (press Rescan)"
    mid = rel + max(0, (_frames(getattr(seg, "record_duration", None)) or 0) // 2)
    try:
        preset = _find_jpeg_preset()
    except Exception as e:
        return False, "no JPEG export preset (%s)" % e
    if not preset:
        return False, "no JPEG export preset found"
    try:
        work = tempfile.mkdtemp(prefix="type_sync_render_")
    except Exception as e:
        return False, "no temp folder for the export (%s)" % e
    restored = True
    try:
        try:
            wh = (int(_attr_value(seq.width)), int(_attr_value(seq.height)))
        except Exception:
            wh = None
        preset = _small_preset(preset, work, wh, long_side)
        try:
            old_in = _attr_value(getattr(seq, "in_mark", None))
            old_out = _attr_value(getattr(seq, "out_mark", None))
        except Exception as e:
            return False, "can't read the sequence's marks (%s)" % e
        try:
            if not (_put_attr(seq, "in_mark", flame.PyTime(mid + 1)) and
                    _put_attr(seq, "out_mark", flame.PyTime(mid + 2))):
                return False, "couldn't set the marks for the export"
            ex = flame.PyExporter()
            ex.foreground = True
            ex.export_between_marks = True
            ex.export(seq, preset, work)
        finally:
            restored = _put_attr(seq, "in_mark", old_in) and _put_attr(seq, "out_mark", old_out)
        if not _place_jpeg(work, out_jpg):
            return False, "the export wrote no JPEG"
        return True, (None if restored else
                      "the In/Out marks on '%s' couldn't be put back -- clear them by hand"
                      % _clean_name(seq))
    except Exception as e:
        return False, "export failed: %s" % e
    finally:
        shutil.rmtree(work, ignore_errors=True)


def prune_preview_cache(cache_dir, keep=400, max_bytes=500 * 1024 * 1024):
    """Keep the preview cache bounded: drop the oldest renders beyond `keep`
    files or `max_bytes` total (every edit of a look makes a new one). Returns
    the signatures removed, so the index can forget them."""
    try:
        names = os.listdir(cache_dir)
    except OSError:
        return []
    # a copy that died half-way (another host, a crash) leaves a .part: stale
    # ones (> 10 min) are just deleted
    for f in names:
        if f.endswith(".part"):
            fp = os.path.join(cache_dir, f)
            try:
                if os.stat(fp).st_mtime < time.time() - 600:
                    os.remove(fp)
            except OSError:
                pass
    files = [os.path.join(cache_dir, f) for f in names if f.lower().endswith(".jpg")]
    stats = []
    for f in files:
        try:
            st = os.stat(f)
            stats.append((st.st_mtime, st.st_size, f))
        except OSError:
            pass
    stats.sort(reverse=True)                       # newest first
    removed, total = [], 0
    for n, (_m, size, f) in enumerate(stats):
        total += size
        if n >= keep or total > max_bytes:
            try:
                os.remove(f)
                removed.append(os.path.splitext(os.path.basename(f))[0])
            except OSError:
                pass
    return removed


def _preview_cache_dir():
    """Per-project: beside the registry (<setups>/type_sync/preview_cache)."""
    return os.path.join(os.path.dirname(registry_path()), "preview_cache")


# ====================================================================
# GUI
# ====================================================================

# Inventory column model: (key, header, toggleable, default_visible, resize).
# Anchors (seq/text/gfx) are not toggleable -- the tool is unusable without
# them. resize is "stretch" or "fit" (ResizeToContents).
INV_COLS = (
    ("seq",    "Sequence", False, True, "stretch"),
    ("name",   "Name",     True,  True, "fit"),
    ("aspect", "Aspect",   True,  True, "fit"),
    ("in",     "In",       True,  True, "fit"),
    ("dur",    "Dur",      True,  True, "fit"),
    ("text",   "Text",     False, True, "stretch"),
    ("gfx",    "Type",      False, True, "fit"),
    ("status", "Status",   True,  True, "fit"),
    ("conn",   "Conn",     True,  True, "fit"),
)
INV_UNITS = ("Timecode", "Frames")


def inv_row_models(inv, hide_assigned=False, group_text=False):
    """Map the inventory to visible table rows. Each row is a list of indices
    into `inv` (one element normally; several when Grouped Text folds segments
    that share identical Text). Pure -- no Qt, no Flame -- so it's unit-testable.

      hide_assigned  drop rows whose segment already has a Type number
      group_text     fold rows with identical (non-blank) Text into one row;
                     blank-Text rows are never folded (they'd group unrelated
                     empties), and first-appearance order is preserved
    """
    idxs = [i for i, d in enumerate(inv)
            if not (hide_assigned and d.get("num") is not None)]
    if not group_text:
        return [[i] for i in idxs]
    rows, groups = [], {}
    for i in idxs:
        key = str(inv[i].get("text", "")).strip()
        if not key:
            rows.append([i])              # blank text -> standalone row
            continue
        bucket = groups.get(key)
        if bucket is None:
            bucket = []
            groups[key] = bucket
            rows.append(bucket)           # same list grows in place as dups arrive
        bucket.append(i)
    return rows


def longest_sequence_name(inv):
    """Name of the longest-duration sequence in the inventory (by seq_dur_f), or
    None if no durations are known. Used as the canonical reference for ordering
    grouped rows by appearance."""
    best, best_dur = None, None
    for d in inv:
        sd = d.get("seq_dur_f")
        if sd is None:
            continue
        if best_dur is None or sd > best_dur:
            best, best_dur = d.get("seq"), sd
    return best


def group_reference(member_dicts, longest_seq):
    """The representative member of a Grouped-Text row for In/Dur display + sort:
    the member that lives in the longest sequence, else (text absent there) the
    member that appears earliest by record_in. Pure / testable."""
    if longest_seq is not None:
        for d in member_dicts:
            if d.get("seq") == longest_seq:
                return d
    return min(member_dicts,
               key=lambda d: (d.get("in_f") is None, d.get("in_f") or 0))


STYLE = """
QDialog, QWidget { background-color: #1e1e1e; color: #cccccc;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-size: 13px; }
QLabel { color: #cccccc; }
QLabel#header { color: #ffffff; font-size: 18px; font-weight: bold; letter-spacing: 2px; }
QLabel#version { color: #777777; font-size: 11px; font-weight: normal; padding-bottom: 2px; }
QTabWidget::pane { border: 1px solid #333333; border-radius: 6px; top: -1px; }
QTabBar::tab { background: #232323; color: #aaaaaa; padding: 7px 16px;
    border: 1px solid #333333; border-bottom: none;
    border-top-left-radius: 5px; border-top-right-radius: 5px; }
QTabBar::tab:selected { background: #1e1e1e; color: #ffffff; }
QGroupBox { color: #777777; font-size: 10px; font-weight: bold; letter-spacing: 1.5px;
    border: 1px solid #333333; border-radius: 6px; margin-top: 12px; padding-top: 12px; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 8px; left: 12px; }
QTableWidget { background-color: #141414; color: #cccccc; border: 1px solid #2a2a2a;
    border-radius: 4px; gridline-color: #333333; }
QTableWidget::item:selected { background-color: #003a4a; color: #ffffff; }
/* visible dividers between header sections so column-resize handles are easy to
   find and aim at (grab the raised ridge between two headers). */
QHeaderView::section { background-color: #2a2a2a; color: #aaaaaa;
    border: none; border-right: 2px solid #4a4a4a;
    padding: 5px; font-size: 11px; font-weight: bold; }
QHeaderView::section:last { border-right: none; }
QPlainTextEdit, QLineEdit, QComboBox { background-color: #141414; color: #cccccc;
    border: 1px solid #2a2a2a; border-radius: 4px; padding: 6px; }
QComboBox QAbstractItemView { background-color: #141414; color: #cccccc; selection-background-color: #003a4a; }
QSpinBox { background-color: #141414; color: #cccccc; border: 1px solid #2a2a2a; border-radius: 4px; padding: 4px; }
QPushButton { background-color: #2d2d2d; color: #cccccc; border: 1px solid #444444;
    border-radius: 4px; padding: 7px 16px; }
QPushButton:hover { background-color: #383838; border-color: #666666; }
QPushButton:disabled { color: #555555; border-color: #2a2a2a; }
QPushButton#primary { background-color: #00b4d8; color: #000000; border: none; font-weight: bold; }
QPushButton#primary:hover { background-color: #00caf0; }
QPushButton:checked { background-color: #003a4a; border-color: #00b4d8; color: #ffffff; }
QPushButton:checked:disabled { background-color: #2d2d2d; border-color: #2a2a2a; color: #555555; }
QPlainTextEdit#logbox { color: #00b4d8; font-family: 'Menlo','Consolas',monospace; font-size: 11px; }
/* pane dividers: wide enough to grab, visible, cyan when the mouse is on them */
QSplitter::handle { background-color: #333333; border-radius: 2px; }
QSplitter::handle:horizontal { width: 10px; }
QSplitter::handle:vertical { height: 10px; }
QSplitter::handle:hover { background-color: #00b4d8; }
"""


class _GripStyle(QtWidgets.QProxyStyle):
    """Widens the column-resize grab zone on table headers. Qt's default grip is
    only a few pixels, which is fiddly to hit; PM_HeaderGripMargin controls it."""
    def pixelMetric(self, metric, option=None, widget=None):
        if metric == QtWidgets.QStyle.PM_HeaderGripMargin:
            return 8
        return super().pixelMetric(metric, option, widget)


def _type_segments(selection):
    out = []
    for item in selection or []:
        try:
            if get_type_fx(item) is not None:
                out.append(item)
        except Exception:
            pass
    return out


# connection-set colours for the Timelines tab (the cyan accent first)
_SET_COLOURS = ("#00b4d8", "#2ec4b6", "#9b7bd8", "#e0679a", "#7cc36b",
                "#e39b4b", "#5b8def", "#c9c24b", "#4bc9a0", "#c96b4b")


class GfxTimelineView(QtWidgets.QWidget):
    """The Timelines tab's lanes: every sequence in the scan on one shared time
    scale, grouped by aspect; each Type graphic is a block at its real place.
    Colour = its connection set (the LOOK); label = its Type number (the WORDS);
    dashed grey = not connected; amber corner = text OUT OF DATE. Click lights
    up the whole connection set; double-click jumps Flame there. Read-only."""
    clicked = QtCore.Signal(int)
    dclicked = QtCore.Signal(int)
    label_w_changed = QtCore.Signal(int)     # the name column was dragged
    LABEL_W, ROW_H, GAP, HDR_H = 170, 18, 8, 20
    GRIP = 5                                 # px either side of the name divider

    def __init__(self, parent=None, label_w=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self._label_w = int(label_w or self.LABEL_W)
        self._lw_eff = self._label_w
        self._dragging = False
        self._lanes, self._info, self._max = [], {}, 1
        self._sel, self._sel_set, self._filter = None, set(), None
        self._hide_others = False
        self._rects, self._heads, self._lanes_y, self._scale = [], [], [], 1.0

    def set_data(self, lanes, info):
        self._lanes, self._info = lanes, info
        self._max = max([ln["dur"] for ln in lanes] + [1])
        self._relayout()

    def set_selection(self, idx, members):
        self._sel, self._sel_set = idx, set(members or ())
        self.update()

    def set_filter(self, key, hide_others=False):
        """Show: grey out every graphic but Type `key`. Filter (hide_others):
        also leave out the sequences that don't use it. None = All."""
        self._filter, self._hide_others = key, bool(hide_others)
        self._relayout()

    def _eff_label_w(self):
        """The name column as laid out: the user's width, but never so wide the
        lanes' ends (end-card legals) slide off the visible area."""
        return max(80, min(self._label_w, max(80, self.width() - 240)))

    def _relayout(self):
        """Block rects for the current width -- computed here, not in paint, so
        a click hits the right block even before the first paint."""
        lw = self._eff_label_w()
        self._lw_eff = lw
        w = max(self.width(), lw + 240)
        scale = (w - lw - 12) / float(self._max)
        rects, heads, lanes_y, y, last = [], [], [], 4, None
        for lane in self._lanes:
            if self._hide_others and self._filter is not None and not any(
                    self._info[idx]["gfx"] == self._filter for row in lane["rows"] for idx in row):
                continue                               # Filter: a sequence without that Type
            if lane["aspect"] != last:
                heads.append((y, lane["aspect"]))
                y += self.HDR_H
                last = lane["aspect"]
            n = max(1, len(lane["rows"]))
            lanes_y.append((y, n, lane))
            for r, row in enumerate(lane["rows"]):
                for idx in row:
                    inf = self._info[idx]
                    x = lw + inf["start"] * scale
                    rects.append((QtCore.QRectF(x, y + r * self.ROW_H + 2,
                                                max(3.0, inf["dur"] * scale), self.ROW_H - 4), idx))
            y += n * self.ROW_H + self.GAP
        self._rects, self._heads, self._lanes_y, self._scale = rects, heads, lanes_y, scale
        self.setMinimumHeight(y + 4)
        self.update()

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self._relayout()

    def _hit(self, pt):
        for r, idx in reversed(self._rects):
            if r.contains(QtCore.QPointF(pt)):
                return idx
        return None

    @staticmethod
    def _pos(ev):
        try:
            return ev.position().toPoint()         # Qt6
        except AttributeError:
            return ev.pos()

    def _on_divider(self, pt):
        return abs(pt.x() - (self._lw_eff - 4)) <= self.GRIP

    def set_label_w(self, w):
        self._label_w = max(80, min(int(w), max(80, self.width() - 240)))
        self._relayout()

    def fit_names(self):
        """Widen (or narrow) the name column to the longest lane name."""
        fm = self.fontMetrics()
        longest = max([fm.horizontalAdvance(str(ln.get("label", ln["seq"])))
                       for ln in self._lanes] + [60])
        self.set_label_w(longest + 20)
        self.label_w_changed.emit(self._label_w)

    def _lane_at(self, y):
        for ly, n, lane in self._lanes_y:
            if ly <= y < ly + n * self.ROW_H:
                return lane
        return None

    def mousePressEvent(self, ev):
        pt = self._pos(ev)
        if self._on_divider(pt):
            self._dragging = True
            self.update()
            return
        idx = self._hit(pt)
        self.clicked.emit(-1 if idx is None else idx)

    def mouseMoveEvent(self, ev):
        pt = self._pos(ev)
        if self._dragging:
            self.set_label_w(pt.x() + 4)
            return
        if self._on_divider(pt):
            self.setCursor(QtCore.Qt.SplitHCursor)
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, ev):
        if self._dragging:
            self._dragging = False
            self.update()
            self.label_w_changed.emit(self._label_w)

    def mouseDoubleClickEvent(self, ev):
        pt = self._pos(ev)
        if self._on_divider(pt):
            self.fit_names()
            return
        idx = self._hit(pt)
        if idx is not None:
            self.dclicked.emit(idx)

    def event(self, ev):
        if ev.type() == QtCore.QEvent.ToolTip:
            pt = ev.pos()
            idx = self._hit(pt)
            if idx is not None:
                QtWidgets.QToolTip.showText(ev.globalPos(), self._info[idx]["tip"], self)
            elif pt.x() < self._lw_eff - 4 and self._lane_at(pt.y()) is not None:
                lane = self._lane_at(pt.y())             # the full sequence name
                QtWidgets.QToolTip.showText(ev.globalPos(), str(lane.get("label", lane["seq"])), self)
            elif self._on_divider(pt):
                QtWidgets.QToolTip.showText(ev.globalPos(), "Drag to resize the names "
                                            "\u00b7 double-click to fit the longest", self)
            else:
                QtWidgets.QToolTip.hideText()
            return True
        return super().event(ev)

    def paintEvent(self, _ev):
        p = QtGui.QPainter(self)
        try:
            p.setRenderHint(QtGui.QPainter.Antialiasing, True)
            p.fillRect(self.rect(), QtGui.QColor("#141414"))
            fm = p.fontMetrics()
            left = QtCore.Qt.AlignVCenter | QtCore.Qt.AlignLeft
            for y, aspect in self._heads:
                p.setPen(QtGui.QColor("#00b4d8"))
                p.drawText(QtCore.QRectF(6, y, 200, self.HDR_H), left, str(aspect))
            for y, n, lane in self._lanes_y:
                p.setPen(QtGui.QColor("#cccccc"))
                name = fm.elidedText(str(lane.get("label", lane["seq"])), QtCore.Qt.ElideMiddle,
                                     self._lw_eff - 14)
                p.drawText(QtCore.QRectF(6, y, self._lw_eff - 10, self.ROW_H), left, name)
                p.fillRect(QtCore.QRectF(self._lw_eff, y + 1, lane["dur"] * self._scale,
                                         n * self.ROW_H - 2), QtGui.QColor("#1f1f1f"))
            # the draggable divider between names and lanes
            p.setPen(QtGui.QPen(QtGui.QColor("#00b4d8" if self._dragging else "#3a3a3a"), 1))
            p.drawLine(QtCore.QPointF(self._lw_eff - 4, 0), QtCore.QPointF(self._lw_eff - 4, self.height()))
            for r, idx in self._rects:
                inf = self._info[idx]
                dim = self._filter is not None and inf["gfx"] != self._filter
                a = 55 if dim else 255
                if inf.get("warn"):                     # identity collision: can't tell
                    fill = QtGui.QColor("#3a2424")
                    pen = QtGui.QPen(QtGui.QColor("#e0605a"), 1, QtCore.Qt.DashLine)
                elif inf["colour"]:
                    fill = QtGui.QColor(inf["colour"])
                    pen = QtGui.QPen(fill.darker(160), 1)
                else:                                   # not connected
                    fill = QtGui.QColor("#3a3a3a")
                    pen = QtGui.QPen(QtGui.QColor("#9a9a9a"), 1, QtCore.Qt.DashLine)
                if idx in self._sel_set:
                    pen = QtGui.QPen(QtGui.QColor("#ffffff"), 3 if idx == self._sel else 2)
                fill.setAlpha(a)
                c = pen.color()
                c.setAlpha(a)
                pen.setColor(c)
                p.setPen(pen)
                p.setBrush(fill)
                p.drawRoundedRect(r, 3, 3)
                if inf["ood"]:                          # text OUT OF DATE
                    tri = QtGui.QPolygonF([QtCore.QPointF(r.right() - 7, r.top()),
                                           QtCore.QPointF(r.right(), r.top()),
                                           QtCore.QPointF(r.right(), r.top() + 7)])
                    amber = QtGui.QColor("#e0b000")
                    amber.setAlpha(a)
                    p.setPen(QtCore.Qt.NoPen)
                    p.setBrush(amber)
                    p.drawPolygon(tri)
                label = inf["label"]
                if r.width() <= fm.horizontalAdvance(label) + 6:
                    label = label.split(" ")[0]          # keep the Type number
                if r.width() > fm.horizontalAdvance(label) + 6:
                    tc = QtGui.QColor("#101010" if (inf["colour"] and not inf.get("warn")) else "#dddddd")
                    tc.setAlpha(a)
                    p.setPen(tc)
                    p.drawText(r, QtCore.Qt.AlignCenter, label)
        finally:
            p.end()


class FramePreview(QtWidgets.QWidget):
    """The Timelines tab's picture: Flame's real render of the frame (a JPEG,
    the Type composited by Flame), or a message. Paints the image into its own
    rect and grows with its pane; it never resizes itself around a pixmap (the
    sibling tool CCM hit that feedback loop). (An earlier 'Drawn' approximation
    was removed: Qt can't match Flame's own text engine.)

    Zoom + pan are one paint transform: zoom is PHYSICAL screen px per FRAME px
    (None = Fit; 1.0 = 100% = 1:1, as Flame's viewer -- on a HiDPI screen a
    logical px is several physical ones), the centre is a frame-px point.
    Drag = pan (a click without a drag changes nothing), the mouse wheel zooms
    about the pointer, double-click = Fit. Text frames the graphic's estimated
    text block. Fit stays Fit and Text re-frames on a new pick; a manual zoom
    stays and re-centres on the new graphic's text. Each frame size (1x1,
    4x5, 16x9...) keeps its own zoom, remembered between opens."""
    view_changed = QtCore.Signal()      # zoom / fit % changed (the zoom list follows)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(160, 120)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self._pix, self._msg = None, ""
        self._frame = (1920.0, 1080.0)  # the frame the image shows, in frame px
        self._zoom = None               # None = Fit
        self._center = None             # frame-px point at the widget centre (None = middle)
        self._text_rect = None          # the picked graphic's text block (frame px, estimate)
        self._text_mode = False         # Text: framed on it, re-framed on every pick / resize
        self._key = None                # which look is showing (a pan survives a re-show)
        self._scaled, self._scaled_key = None, None   # a smooth-shrunk copy (big renders)
        self._frame_key = None          # "WxH" of the frame showing
        self._views = {}                # frame size -> [mode, zoom]: each size keeps its zoom
        self._drag = None

    # ---- content
    def show_image(self, path, frame_wh=None, text_rect=None, key=None):
        pix = QtGui.QPixmap(path)
        self._scaled, self._scaled_key = None, None
        self._pix, self._msg = (pix if not pix.isNull() else None), \
            ("" if not pix.isNull() else "Couldn't read the rendered frame.")
        try:
            fw, fh = float(frame_wh[0]), float(frame_wh[1])
            ok = fw > 0 and fh > 0
        except Exception:
            ok = False
        if self._pix is not None:
            if not ok:
                fw = float(self._pix.width())
            fh = fw * self._pix.height() / float(self._pix.width())   # never stretched
            self._frame = (fw, fh)
        elif ok:
            self._frame = (fw, fh)
        self._text_rect = text_rect
        at = self._text_center()
        new = key is None or key != self._key
        self._key = key
        fkey = "%dx%d" % (int(frame_wh[0]), int(frame_wh[1])) if ok else None
        if fkey and fkey != self._frame_key:        # another frame size: its own zoom
            if self._frame_key:
                self._views[self._frame_key] = self._state()
            mode, z = self._views.get(fkey, ["fit", None])
            self._text_mode = mode == "text"
            self._zoom = z if mode == "manual" else None
            self._frame_key, new = fkey, True
        if new:                             # a manual zoom re-centres on a NEW graphic;
            self._center = QtCore.QPointF(*at) if (self._zoom is not None and at) \
                else None                   # the same one keeps its pan (Re-render, Rescan)
        self._clamp()
        self._drag = None
        self.setCursor(QtCore.Qt.OpenHandCursor if self._pix is not None else QtCore.Qt.ArrowCursor)
        self.update()
        self.view_changed.emit()

    def show_message(self, msg):
        self._pix, self._msg, self._drag = None, msg, None
        self.setCursor(QtCore.Qt.ArrowCursor)
        self.update()
        self.view_changed.emit()

    def has_image(self):
        return self._pix is not None

    def has_text(self):
        return bool(self._text_rect)

    def _state(self):
        if self._text_mode:
            return ["text", None]
        return ["fit", None] if self._zoom is None else ["manual", round(self._zoom, 4)]

    def view_states(self):
        """Every frame size's zoom ("WxH" -> [fit|text|manual, zoom]) -- remembered."""
        d = dict(self._views)
        if self._frame_key:
            d[self._frame_key] = self._state()
        return d

    def set_view_states(self, d):
        self._views = {}
        for k, v in (d or {}).items() if isinstance(d, dict) else ():
            try:
                mode, z = v[0], v[1]
                if mode in ("fit", "text"):
                    self._views[str(k)] = [mode, None]
                elif mode == "manual" and 0.02 <= float(z) <= 16.0:
                    self._views[str(k)] = ["manual", float(z)]
            except Exception:
                continue

    def _text_center(self):
        if not self._text_rect:
            return None
        x, y, w, h = self._text_rect
        return (x + w / 2.0, y + h / 2.0)

    # ---- zoom
    def _dpr(self):
        try:
            return max(1.0, float(self.devicePixelRatioF()))
        except Exception:
            return 1.0

    def fit_zoom(self):
        fw, fh = self._frame
        w, h = self.width() - 8.0, self.height() - 8.0      # a 4 px margin all round
        if fw <= 0 or fh <= 0 or w <= 0 or h <= 0:
            return 1.0
        return min(w / fw, h / fh) * self._dpr()

    def text_zoom(self):
        _x, _y, w, h = self._text_rect
        cw, ch = self.width() - 8.0, self.height() - 8.0
        if w <= 0 or h <= 0 or cw <= 0 or ch <= 0:
            return self.fit_zoom()
        return min(16.0, min(cw / w, ch / h) * self._dpr())

    def zoom(self):
        if self._text_mode and self._text_rect:
            return self.text_zoom()
        return self.fit_zoom() if self._zoom is None else self._zoom

    def is_fit(self):
        return self._zoom is None and not self._text_mode

    def is_text(self):
        return self._text_mode

    def set_fit(self):
        self._zoom, self._center, self._text_mode = None, None, False
        self.update()
        self.view_changed.emit()

    def set_text(self):
        if not self._text_rect:
            return
        self._text_mode, self._center, self._zoom = True, None, None   # no text box -> Fit size
        self.update()
        self.view_changed.emit()

    def set_zoom(self, z):
        if self._text_mode:
            self._center = self._mid()          # keep looking at the text
        self._text_mode = False
        self._zoom = min(16.0, max(0.02, float(z)))
        at = self._text_center()
        if self._center is None and at:
            self._center = QtCore.QPointF(*at)  # zoom in on the text
        self._clamp()
        self.update()
        self.view_changed.emit()

    def is_soft(self):
        """Zoomed past the render's own pixels (the JPEG is stretched)."""
        if self._pix is None or self._frame[0] <= 0:
            return False
        return self.zoom() * self._frame[0] > self._pix.width() * 1.001

    # ---- geometry
    def _mid(self):
        if self._text_mode and self._text_rect:
            return QtCore.QPointF(*self._text_center())
        return self._center if self._center is not None else \
            QtCore.QPointF(self._frame[0] / 2.0, self._frame[1] / 2.0)

    def _clamp(self):
        """Keep the view's centre inside the frame (part of it always shows)."""
        if self._center is None:
            return
        fw, fh = self._frame
        self._center = QtCore.QPointF(min(fw, max(0.0, self._center.x())),
                                      min(fh, max(0.0, self._center.y())))

    def _view_rect(self):
        fw, fh = self._frame
        z, c = self.zoom() / self._dpr(), self._mid()      # logical px per frame px
        return QtCore.QRectF(self.width() / 2.0 - c.x() * z, self.height() / 2.0 - c.y() * z,
                             fw * z, fh * z)

    # ---- mouse: drag = pan, double-click = Fit
    def mousePressEvent(self, ev):
        if self._pix is not None and ev.button() == QtCore.Qt.LeftButton:
            self._drag = (ev.position(), self._mid(), False)
            self.setCursor(QtCore.Qt.ClosedHandCursor)
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._drag is not None:
            start, c0, moved = self._drag
            d = ev.position() - start
            if not moved and abs(d.x()) + abs(d.y()) <= 3:
                return                                # a click isn't a pan
            if not moved:
                if self._zoom is None or self._text_mode:
                    self._zoom = self.zoom()          # panning leaves Fit / Text at the same size
                    self._text_mode = False
                self._drag = (start, c0, True)
                self.view_changed.emit()
            z = self.zoom() / self._dpr()                 # the mouse moves in logical px
            self._center = QtCore.QPointF(c0.x() - d.x() / z, c0.y() - d.y() / z)
            self._clamp()
            self.update()
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._drag is not None:
            self._drag = None
            self.setCursor(QtCore.Qt.OpenHandCursor if self._pix is not None else QtCore.Qt.ArrowCursor)
        super().mouseReleaseEvent(ev)

    def wheelEvent(self, ev):
        steps = ev.angleDelta().y() / 120.0
        if self._pix is None or not steps:
            super().wheelEvent(ev)
            return
        m, c, r = ev.position(), self._mid(), self._dpr()
        zl = self.zoom() / r
        fx = c.x() + (m.x() - self.width() / 2.0) / zl     # the frame point under the pointer
        fy = c.y() + (m.y() - self.height() / 2.0) / zl
        z2 = min(16.0, max(0.02, self.zoom() * (1.25 ** steps)))
        zl2 = z2 / r
        self._zoom, self._text_mode = z2, False
        self._center = QtCore.QPointF(fx - (m.x() - self.width() / 2.0) / zl2,
                                      fy - (m.y() - self.height() / 2.0) / zl2)
        self._clamp()                                       # ...stays under it
        self.update()
        self.view_changed.emit()
        ev.accept()

    def mouseDoubleClickEvent(self, ev):
        if self._pix is not None:
            self.set_fit()
        super().mouseDoubleClickEvent(ev)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        self.view_changed.emit()                      # the Fit % changes with the pane

    def _shrunk(self, rect):
        """A smooth-shrunk copy when the image is drawn well below its own
        pixels (a big render at Fit): drawn straight, it shimmers and thin
        strokes drop out. Kept until the drawn size changes."""
        r = self._dpr()
        tw, th = int(round(rect.width() * r)), int(round(rect.height() * r))
        if tw <= 0 or th <= 0 or self._pix.width() <= tw * 1.3:
            return None
        if self._scaled_key != (tw, th):
            self._scaled = self._pix.scaled(tw, th, QtCore.Qt.IgnoreAspectRatio,
                                            QtCore.Qt.SmoothTransformation)
            self._scaled_key = (tw, th)
        return self._scaled

    def paintEvent(self, _ev):
        p = QtGui.QPainter(self)
        try:
            p.setRenderHint(QtGui.QPainter.Antialiasing, True)
            p.setRenderHint(QtGui.QPainter.SmoothPixmapTransform, True)
            p.fillRect(self.rect(), QtGui.QColor("#0d0d0d"))
            if self._pix is not None:
                vr = self._view_rect()
                sh = self._shrunk(vr)
                if sh is not None:                   # 1:1 in device px: never re-stretched
                    r = self._dpr()
                    p.drawPixmap(QtCore.QRectF(vr.x(), vr.y(), sh.width() / r, sh.height() / r),
                                 sh, QtCore.QRectF(sh.rect()))
                else:
                    p.drawPixmap(vr, self._pix, QtCore.QRectF(self._pix.rect()))
            else:
                p.setPen(QtGui.QColor("#777777"))
                p.drawText(QtCore.QRectF(self.rect()).adjusted(10, 10, -10, -10),
                           QtCore.Qt.AlignCenter | QtCore.Qt.TextWordWrap, self._msg)
        finally:
            p.end()


def _avail_screen_size():
    """(w, h) of the screen the window will open on -- the one under the
    mouse, which is where Qt puts a parentless dialog -- or None."""
    try:
        scr = (QtGui.QGuiApplication.screenAt(QtGui.QCursor.pos())
               or QtGui.QGuiApplication.primaryScreen())
        if scr is not None:
            a = scr.availableGeometry()
            return a.width(), a.height()
    except Exception:
        pass
    return None


class _HandleWatch(QtCore.QObject):
    """Tells the dialog when a splitter handle is pressed / released -- Qt
    has no drag-start / drag-end signal for a splitter."""

    def __init__(self, on_press, on_release, parent=None):
        super().__init__(parent)
        self._press, self._release = on_press, on_release

    def eventFilter(self, obj, ev):
        try:
            t = ev.type()      # (the 2nd press of a double-click arrives as DblClick)
            if t in (QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseButtonDblClick):
                self._press()
            elif t == QtCore.QEvent.MouseButtonRelease:
                self._release()
        except Exception as e:                    # never into Flame's event loop
            log.warning("splitter handle: %s", e)
        return False


class GraphicSyncDialog(QtWidgets.QDialog):

    def __init__(self, selection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Type Sync")
        self.setStyleSheet(STYLE)
        # the window opens at its remembered size, kept on its screen
        self.resize(*fit_window_size(load_settings().get("win_size"), _avail_screen_size()))
        # layout memory (pane sizes, shown/hidden, window size): changes are
        # collected here and written once they settle -- a divider drag fires
        # on every mouse move -- and always when the window closes
        self._layout_pending = {}
        self._layout_timer = QtCore.QTimer(self)
        self._layout_timer.setSingleShot(True)
        self._layout_timer.setInterval(300)
        self._layout_timer.timeout.connect(self._flush_layout)
        self._layout_ready = False   # no window-size saves while building
        self._tips_on = load_settings().get("show_tips", True) is not False
        self._tip_buttons, self._tip_labels = [], []
        self._inv = []            # one scan, shared by Inventory + Connections
        self._queue = []          # list of uid-lists; each = a pending connection group
        self._longest_seq = None  # reference sequence for grouped In/Dur ordering
        self._sources = set()     # uids marked "Set as Source" for connections
        self._queue_sig = []      # what the Q rows last showed (Execute re-checks)
        self._keep_sel = None     # Segments selection carried across a rescan
        self._ctx = None          # last link_context (Connections render)
        self._tl_dirty = True     # Timelines tab needs a re-render
        self._tl_sel = None       # Timelines: selected inv index
        self._tl_sel_key = None   # ...and its identity key (survives rescans)
        self._tl_ctx = ({}, {}, [])
        self._tl_tainted = set()  # ...identity-collision sets ("can't tell")
        self._tl_clash = set()    # ...and the colliding keys themselves
        self._tl_letter = {}      # set id -> letter (as the Connections tab)
        self._tl_lane_label = {}  # inv index -> lane label (name [+ reel])
        self._tl_render_token = None  # the pending real render (a stale one is skipped)
        self._grip_style = _GripStyle()   # wider column-resize grab zone (kept alive)

        segs = _type_segments(selection)
        if not segs:
            cur = _current_segment()
            if cur is not None and get_type_fx(cur) is not None:
                segs = [cur]
        self._source = segs[0] if segs else None

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        hrow = QtWidgets.QHBoxLayout()
        hrow.setSpacing(8)
        hdr = QtWidgets.QLabel("TYPE SYNC")
        hdr.setObjectName("header")
        hrow.addWidget(hdr)
        # subtle version badge, sitting on the wordmark's baseline
        ver = QtWidgets.QLabel("v" + VERSION)
        ver.setObjectName("version")
        ver.setToolTip("Type Sync version %s" % VERSION)
        hrow.addWidget(ver, 0, QtCore.Qt.AlignBottom)
        hrow.addStretch(1)
        root.addLayout(hrow)

        srow = QtWidgets.QHBoxLayout()
        srow.addWidget(QtWidgets.QLabel("Scope:"))
        self.scope = QtWidgets.QComboBox()
        self.scope.addItems(SCOPES)
        saved = load_settings().get("scope", "Current Reel")
        if saved in SCOPES:
            self.scope.setCurrentText(saved)
        self.scope.currentTextChanged.connect(self._scope_changed)
        srow.addWidget(self.scope)
        # live scan summary, in accent blue, right beside the scope selector
        self.scope_summary = QtWidgets.QLabel("")
        self.scope_summary.setStyleSheet("color:#00b4d8;")
        srow.addWidget(self.scope_summary)
        srow.addStretch(1)
        self.scan_btn = QtWidgets.QPushButton("Rescan")
        self.scan_btn.setToolTip(
            "Re-read Flame. Type Sync no longer blocks Flame, so after you change "
            "things there (connections, text, cuts), rescan to see them here.")
        self.scan_btn.clicked.connect(self._rescan)
        srow.addWidget(self.scan_btn)
        self.console_btn = QtWidgets.QPushButton("Hide Console")
        self.console_btn.setToolTip("Show / hide the Type Sync console for more room.")
        self.console_btn.clicked.connect(self._toggle_console)
        srow.addWidget(self.console_btn)
        root.addLayout(srow)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self._build_inventory_tab(), "Segments")
        self.tabs.addTab(self._build_graphics_tab(), "Registry")
        self.tabs.addTab(self._build_connections_tab(), "Connections")
        self.tabs.addTab(self._build_timelines_tab(), "Timelines")
        self.tabs.addTab(self._build_settings_tab(), "Settings")
        self.tabs.currentChanged.connect(self._tab_changed)
        root.addWidget(self.tabs, 1)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setObjectName("logbox")
        self.log.setReadOnly(True)
        self.log.setFixedHeight(150)
        root.addWidget(self.log)
        if not load_settings().get("show_console", True):     # remembered
            self.log.setVisible(False)
            self.console_btn.setText("Show Console")

        self._reload_registry_table()
        self._scan()
        self._apply_default_sort()
        self._layout_ready = True

    # ---------------------------------------------------------------- util
    def _say(self, m):
        self.log.appendPlainText(m)

    def _tips_button(self):
        """A tab's Tips toggle. The Connections and Timelines buttons are one
        switch (lit = tips shown), remembered as show_tips."""
        b = QtWidgets.QPushButton("Tips")
        b.setCheckable(True)
        b.setChecked(self._tips_on)
        b.setToolTip("Show / hide the tips on this tab.")
        b.toggled.connect(self._set_tips)
        self._tip_buttons.append(b)
        return b

    def _tip_label(self, lbl):
        lbl.setVisible(self._tips_on)
        self._tip_labels.append(lbl)

    def _set_tips(self, on):
        self._tips_on = bool(on)
        for b in self._tip_buttons:
            b.blockSignals(True)
            b.setChecked(self._tips_on)
            b.blockSignals(False)
        for lbl in self._tip_labels:
            lbl.setVisible(self._tips_on)
        self._save_setting("show_tips", self._tips_on)

    def _layout_later(self, **kv):
        """Remember layout settings (debounced -- see __init__)."""
        self._layout_pending.update(kv)
        self._layout_timer.start()

    def _flush_layout(self):
        if not getattr(self, "_layout_pending", None):
            return
        self._layout_timer.stop()
        s = load_settings()
        s.update(self._layout_pending)
        self._layout_pending = {}
        save_settings(s)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if getattr(self, "_layout_ready", False) and self.isVisible() and not (
                self.isMaximized() or self.isFullScreen()):
            self._layout_later(win_size=[self.width(), self.height()])

    def hideEvent(self, ev):
        if not ev.spontaneous():             # a real close / Esc -- not a minimise, which
            self._commit_settings(apply=False)   # leaves it to leaving the tab (it applies)
        self._flush_layout()          # closing (or Esc) never loses a layout change
        super().hideEvent(ev)

    def closeEvent(self, ev):
        self._commit_settings(apply=False)
        self._flush_layout()          # ...nor a close that doesn't hide first
        super().closeEvent(ev)

    def _apply_default_sort(self):
        """Apply the saved default Segments sort column (ascending). Sets the
        header sort indicator, which subsequent renders preserve until the user
        clicks a different column."""
        key = load_settings().get("inv_sort", "")
        if not key:
            return
        for c, col in enumerate(INV_COLS):
            if col[0] == key:
                self.inv_table.sortByColumn(c, QtCore.Qt.AscendingOrder)
                return

    def _goto_timeline(self):
        """Current* scopes anchor to what Flame's Timeline shows; with Type Sync
        no longer blocking Flame, the user may be on another tab. Same verified
        call _open makes (verified on box)."""
        try:
            flame.go_to("Timeline")
        except Exception:
            pass

    def _rescan(self):
        self._goto_timeline()
        self._scan()

    def _toggle_console(self):
        show = self.log.isHidden()
        self.log.setVisible(show)
        self.console_btn.setText("Hide Console" if show else "Show Console")
        self._save_setting("show_console", show)

    def _scope_changed(self, text):
        s = load_settings(); s["scope"] = text; save_settings(s)
        if getattr(self, "_settings_seen", None) is not None:   # the Settings tab shares it
            self.set_scope.setCurrentText(text)
            self._settings_seen["scope"] = text
        self._scan()

    # ---------------------------------------------------------------- Graphics tab
    def _build_graphics_tab(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)

        self.reg_table = QtWidgets.QTableWidget(0, 2)
        self.reg_table.setHorizontalHeaderLabels(["Type", "Text"])
        self.reg_table.verticalHeader().setVisible(False)
        self.reg_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.reg_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.reg_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        rh = self.reg_table.horizontalHeader()
        rh.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        rh.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        self.reg_table.itemSelectionChanged.connect(self._reg_row_selected)
        self.reg_table.cellDoubleClicked.connect(lambda *_: self._load_editor())
        v.addWidget(self.reg_table, 1)

        ed = QtWidgets.QGroupBox("ADD / EDIT TYPE NUMBER")
        el = QtWidgets.QVBoxLayout(ed)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Type #"))
        self.reg_spin = QtWidgets.QSpinBox()
        self.reg_spin.setRange(1, 99)
        row.addWidget(self.reg_spin)
        row.addStretch(1)
        self.b_renumber = QtWidgets.QPushButton("Renumber…")
        self.b_renumber.clicked.connect(self._renumber)
        row.addWidget(self.b_renumber)
        el.addLayout(row)
        el.addWidget(QtWidgets.QLabel("Text  (use a line of  ---  to separate Type layers):"))
        self.reg_text = QtWidgets.QPlainTextEdit()
        self.reg_text.setFixedHeight(80)
        el.addWidget(self.reg_text)
        brow = QtWidgets.QHBoxLayout()
        self.b_remove = QtWidgets.QPushButton("Remove")
        self.b_remove.clicked.connect(self._remove_graphic)
        brow.addWidget(self.b_remove)
        self.b_remove_all = QtWidgets.QPushButton("Remove All")
        self.b_remove_all.setToolTip(
            "Clear EVERY entry from this project's registry to start fresh. "
            "Segments keep their tags; only the definitions are removed.")
        self.b_remove_all.clicked.connect(self._remove_all_graphics)
        brow.addWidget(self.b_remove_all)
        brow.addStretch(1)
        self.b_synctext = QtWidgets.QPushButton("Sync Text \u2192 Scope")
        self.b_synctext.clicked.connect(self._sync_text)
        brow.addWidget(self.b_synctext)
        self.b_save = QtWidgets.QPushButton("Save / Add")
        self.b_save.clicked.connect(self._save_graphic)
        brow.addWidget(self.b_save)
        el.addLayout(brow)
        v.addWidget(ed)
        return w

    def _reload_registry_table(self):
        reg = load_registry()
        keys = sorted(reg.keys())
        self.reg_table.blockSignals(True)
        self.reg_table.setRowCount(len(keys))
        for r, k in enumerate(keys):
            lines = reg[k].get("lines", [])
            self.reg_table.setItem(r, 0, QtWidgets.QTableWidgetItem("Type" + k))
            preview = str(lines[0]).splitlines()[0] if (lines and str(lines[0]).splitlines()) else ""
            self.reg_table.setItem(r, 1, QtWidgets.QTableWidgetItem(preview))
        self.reg_table.blockSignals(False)

    def _reg_row_selected(self):
        self._load_editor()

    def _selected_reg_key(self):
        rows = self.reg_table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self.reg_table.item(rows[0].row(), 0)
        return tag_to_instance(item.text()) if item else None

    def _load_editor(self):
        k = self._selected_reg_key()
        if k is None:
            return
        self.reg_spin.setValue(int(k))
        self.reg_text.setPlainText(layers_to_text(registry_lines(int(k))))

    def _save_graphic(self):
        num = self.reg_spin.value()
        lines = text_to_layers(self.reg_text.toPlainText())
        if registry_set(num, lines):
            self._say("Saved Type%s (%d layer(s))." % (_key(num), len(lines)))
        self._reload_registry_table()
        self._scan()

    def _target_key(self):
        k = self._selected_reg_key()
        if k is None:
            k = _key(self.reg_spin.value())
        return k if k in load_registry() else None

    def _remove_graphic(self):
        k = self._target_key()
        if k is None:
            self._say("Select a Type number in the list to remove.")
            return
        if QtWidgets.QMessageBox.question(
                self, "Remove", "Remove Type%s from the registry?\n"
                "(Segments keep their tag/text; only the definition is removed.)" % k,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        registry_remove(int(k))
        self._say("Removed Type%s." % k)
        self._reload_registry_table()
        self._scan()

    def _remove_all_graphics(self):
        reg = load_registry()
        if not reg:
            self._say("Registry is already empty.")
            return
        if QtWidgets.QMessageBox.question(
                self, "Remove All",
                "Remove ALL %d graphic(s) from this project's registry and start "
                "fresh?\n\nThis can't be undone. Segments keep their tags; only the "
                "registry definitions are cleared." % len(reg),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        save_registry({})
        self._say("Cleared the registry (%d entr%s removed)."
                  % (len(reg), "y" if len(reg) == 1 else "ies"))
        self._reload_registry_table()
        self._scan()

    def _renumber(self):
        k = self._target_key()
        if k is None:
            self._say("Select a saved Type number to renumber.")
            return
        cur = int(k)
        new, ok = QtWidgets.QInputDialog.getInt(
            self, "Renumber Type%s" % k, "New Type number:", cur, 1, 99)
        if not ok or new == cur:
            return
        mode = "overwrite"
        if _key(new) in load_registry():
            # target occupied -> Swap (safe, keeps both) / Overwrite (destroys
            # the target) / Cancel. Swap is the default to prevent data loss.
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle("Type%s already exists" % _key(new))
            box.setText(
                "Type%s already exists.\n\n"
                "Swap — exchange Type%s ↔ Type%s, both kept (recommended).\n"
                "Overwrite — replace Type%s with Type%s; Type%s's text is lost."
                % (_key(new), _key(cur), _key(new), _key(new), _key(cur), _key(new)))
            box.setStyleSheet(STYLE)
            swap_b = box.addButton("Swap", QtWidgets.QMessageBox.AcceptRole)
            over_b = box.addButton("Overwrite", QtWidgets.QMessageBox.DestructiveRole)
            box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
            box.setDefaultButton(swap_b)
            box.exec()
            clicked = box.clickedButton()
            if clicked is swap_b:
                mode = "swap"
            elif clicked is over_b:
                mode = "overwrite"
            else:
                return
        # renumber saves the registry, then re-tags segments in the scope; with
        # Flame live, make sure that scope resolves BEFORE anything is saved
        self._goto_timeline()
        try:
            live = sequences_for_scope(self.scope.currentText())
        except Exception:
            live = []
        if not live:
            self._say("Renumber needs Flame's Timeline to show a sequence in scope '%s' (it "
                      "re-tags segments there). Nothing changed." % self.scope.currentText())
            return
        n, err = renumber_graphic(cur, new, self.scope.currentText(), mode)
        if err:
            self._say(err)
            return
        arrow = "↔" if mode == "swap" else "→"
        verb = "Swapped" if mode == "swap" else "Renumbered"
        self._say("%s Type%s %s Type%s; re-tagged %d segment(s) in '%s'."
                  % (verb, _key(cur), arrow, _key(new), n, self.scope.currentText()))
        self.reg_spin.setValue(new)
        self._reload_registry_table()
        self._scan()

    def _sync_text(self):
        num = self.reg_spin.value()
        if _key(num) not in load_registry():
            self._say("Type%s is not saved yet \u2014 Save it first." % _key(num))
            return
        scope = self.scope.currentText()
        prev = sync_text(num, scope, dry_run=True)
        if not prev:
            self._say("Type%s: nothing to update in '%s' (already in sync or no tagged segments)." % (_key(num), scope))
            return
        seqs = {}
        for seg, li, old, new in prev:
            seqs.setdefault(_clean_name(_ancestor(seg, "PySequence")), 0)
            seqs[_clean_name(_ancestor(seg, "PySequence"))] += 1
        msg = ["Sync TEXT for Type%s across '%s'?" % (_key(num), scope), "",
               "%d layer(s) in %d sequence(s):" % (len(prev), len(seqs))]
        for s, c in sorted(seqs.items()):
            msg.append("   \u2022 %s  (%d)" % (s, c))
        if QtWidgets.QMessageBox.question(self, "Confirm Sync Text", "\n".join(msg),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        warns = []
        done = sync_text(num, scope, dry_run=False, warnings=warns)
        for wmsg in warns:
            self._say(wmsg)
        self._say("Synced Type%s text: %d layer(s)." % (_key(num), len(done)))
        self._scan()

    # ---------------------------------------------------------------- Inventory tab
    def _build_inventory_tab(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        s = load_settings()

        toprow = QtWidgets.QHBoxLayout()
        toprow.addStretch(1)
        self.inv_hide_assigned = QtWidgets.QCheckBox("Hide Assigned")
        self.inv_hide_assigned.setToolTip(
            "Show only segments that still need a Type number.")
        self.inv_hide_assigned.toggled.connect(lambda *_: self._render_inv_table())
        toprow.addWidget(self.inv_hide_assigned)
        self.inv_group_text = QtWidgets.QCheckBox("Grouped Text")
        self.inv_group_text.setToolTip(
            "Fold segments with identical Text into one row; select it to assign "
            "them all to one Type number at once.")
        self.inv_group_text.toggled.connect(self._inv_group_toggled)
        toprow.addWidget(self.inv_group_text)
        toprow.addSpacing(12)
        toprow.addWidget(QtWidgets.QLabel("Units:"))
        self.inv_units = QtWidgets.QComboBox()
        self.inv_units.addItems(list(INV_UNITS))
        if s.get("inv_units") in INV_UNITS:
            self.inv_units.setCurrentText(s["inv_units"])
        self.inv_units.setToolTip("Show the In / Dur columns as timecode or as frames.")
        self.inv_units.currentTextChanged.connect(self._inv_units_changed)
        toprow.addWidget(self.inv_units)
        self.inv_cols_btn = QtWidgets.QToolButton()
        self.inv_cols_btn.setText("Columns ▾")
        self.inv_cols_btn.setToolTip("Show / hide inventory columns.")
        self.inv_cols_btn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.inv_cols_btn.setStyleSheet(
            "QToolButton { background-color: #2d2d2d; color: #cccccc;"
            " border: 1px solid #444444; border-radius: 4px; padding: 6px 12px; }"
            "QToolButton:hover { background-color: #383838; }"
            "QToolButton::menu-indicator { image: none; }")
        menu = QtWidgets.QMenu(self.inv_cols_btn)
        menu.setStyleSheet(STYLE)
        hidden = set(s.get("inv_hidden") or [])
        self._inv_col_actions = {}
        for key, header, togg, default_vis, _rz in INV_COLS:
            if not togg:
                continue
            act = menu.addAction(header)
            act.setCheckable(True)
            act.setChecked((key not in hidden) if default_vis else False)
            act.toggled.connect(lambda on, k=key: self._inv_col_toggled(k, on))
            self._inv_col_actions[key] = act
        self.inv_cols_btn.setMenu(menu)
        toprow.addWidget(self.inv_cols_btn)
        v.addLayout(toprow)

        self.inv_table = QtWidgets.QTableWidget(0, len(INV_COLS))
        self.inv_table.setHorizontalHeaderLabels([c[1] for c in INV_COLS])
        self.inv_table.verticalHeader().setVisible(False)
        self.inv_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.inv_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.inv_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.inv_table.setSortingEnabled(True)
        # all columns user-resizable (drag a divider) except Text, which stretches
        # to fill the slack. Sensible starting widths; manual drags then persist.
        ih = self.inv_table.horizontalHeader()
        _W = {"seq": 180, "name": 150, "aspect": 60, "in": 95, "dur": 95,
              "gfx": 60, "status": 100, "conn": 55}
        for c, (k, _h, _t, _d, _rz) in enumerate(INV_COLS):
            if k == "text":
                ih.setSectionResizeMode(c, QtWidgets.QHeaderView.Stretch)
            else:
                ih.setSectionResizeMode(c, QtWidgets.QHeaderView.Interactive)
                self.inv_table.setColumnWidth(c, _W.get(k, 100))
        ih.setStyle(self._grip_style)   # wider grab zone
        self.inv_table.itemSelectionChanged.connect(self._inv_sel_changed)
        self._apply_inv_hidden()
        v.addWidget(self.inv_table, 1)

        actions = QtWidgets.QGroupBox("ACTIONS  (select rows above)")
        a = QtWidgets.QHBoxLayout(actions)
        self.b_addreg = QtWidgets.QPushButton("Add to Registry")
        self.b_addreg.clicked.connect(self._add_to_registry)
        a.addWidget(self.b_addreg)
        self.b_addall = QtWidgets.QPushButton("Add All to Registry")
        self.b_addall.setToolTip(
            "Add every grouped row to the registry in the current table order "
            "(sort by In first for appearance order), each to the next free Type "
            "number, assigning its segments. Only shown with Grouped Text on.")
        self.b_addall.setVisible(False)
        self.b_addall.clicked.connect(self._add_all_to_registry)
        a.addWidget(self.b_addall)
        a.addSpacing(16)
        a.addWidget(QtWidgets.QLabel("Assign to"))
        self.assign_combo = QtWidgets.QComboBox()
        # entries carry a text preview ("Type01 — Legal line one…"); keep the
        # collapsed box bounded (it elides) while the popup shows the full label.
        self.assign_combo.setSizeAdjustPolicy(
            QtWidgets.QComboBox.AdjustToMinimumContentsLengthWithIcon)
        self.assign_combo.setMinimumContentsLength(16)
        self.assign_combo.setMinimumWidth(150)
        self.assign_combo.setMaximumWidth(340)
        a.addWidget(self.assign_combo)
        self.b_assign = QtWidgets.QPushButton("Assign")
        self.b_assign.clicked.connect(self._assign)
        a.addWidget(self.b_assign)
        a.addStretch(1)
        # registry text -> segments, right here where OUT OF DATE shows up.
        # Same previewed, confirm-first write as the Registry tab's Sync Text.
        self.b_sync_sel = QtWidgets.QPushButton("Sync Selected")
        self.b_sync_sel.clicked.connect(lambda: self._sync_segments("Selected"))
        a.addWidget(self.b_sync_sel)
        self.b_sync_all = QtWidgets.QPushButton("Sync All")
        self.b_sync_all.clicked.connect(lambda: self._sync_segments("All"))
        a.addWidget(self.b_sync_all)
        v.addWidget(actions)

        # apply the "default Grouped Text" setting now that b_addall exists --
        # block the signal so we don't render before the first scan.
        if s.get("inv_group_default"):
            self.inv_group_text.blockSignals(True)
            self.inv_group_text.setChecked(True)
            self.inv_group_text.blockSignals(False)
            self.b_addall.setVisible(True)
        return w

    def _inv_units_changed(self, text):
        s = load_settings(); s["inv_units"] = text; save_settings(s)
        self._render_inv_table()        # re-render the cached scan, no Flame walk

    def _inv_col_toggled(self, key, on):
        s = load_settings()
        hidden = set(s.get("inv_hidden") or [])
        hidden.discard(key) if on else hidden.add(key)
        s["inv_hidden"] = sorted(hidden)
        save_settings(s)
        self._apply_inv_hidden()

    def _apply_inv_hidden(self):
        # the checkable menu actions are the live source of truth (they were
        # seeded from settings at build time) -- no disk read per render
        for c, (key, _h, togg, _d, _rz) in enumerate(INV_COLS):
            act = self._inv_col_actions.get(key)
            self.inv_table.setColumnHidden(c, bool(togg and act and not act.isChecked()))

    def _inv_cell(self, d, key):
        """Display value for one inventory cell. Ints (frames mode) stay ints so
        the table sorts them numerically."""
        if key == "in" or key == "dur":
            if self.inv_units.currentText() == "Frames":
                f = d.get("in_f" if key == "in" else "dur_f")
                return "" if f is None else f
            return d.get("tc_in" if key == "in" else "tc_dur", "")
        if key == "gfx":
            return ("Type" + d["num"]) if d["num"] else "\u2014"
        if key == "status":
            if d["num"] is None:
                return "unassigned"
            return "in sync" if d["in_sync"] else "OUT OF DATE"
        if key == "conn":
            return d["connected"]    # int -> numeric sort
        return d.get(key, "")        # seq / name / aspect / text

    def _inv_group_cell(self, members, key):
        """Display value for a Grouped-Text row that folds several segments.
        Columns that vary across members are summarised rather than blanked
        where it's useful (count, aspect set, assigned tally)."""
        ds = [self._inv[i] for i in members]
        n = len(ds)
        if key == "seq":
            return "%d segments" % n
        if key == "aspect":
            a = sorted({d["aspect"] for d in ds})
            return a[0] if len(a) == 1 else "mixed"
        if key in ("in", "dur"):
            # In/Dur of the reference member -- the one in the longest sequence,
            # else the earliest. So sorting the grouped list by In orders the
            # groups by appearance in the longest sequence (your hidden feature);
            # sorting by Text or anything else is unaffected.
            return self._inv_cell(group_reference(ds, self._longest_seq), key)
        if key == "text":
            return self._inv_cell(ds[0], "text")
        if key == "gfx":
            nums = {d["num"] for d in ds}
            if nums == {None}:
                return "—"
            if len(nums) == 1:
                only = next(iter(nums))
                return ("Type" + only) if only else "—"
            return "mixed"
        if key == "status":
            assigned = sum(1 for d in ds if d["num"] is not None)
            return "%d/%d assigned" % (assigned, n)
        if key == "conn":
            return sum(d["connected"] for d in ds)   # int -> numeric sort
        return ""                    # name / in / dur vary -> blank

    def _render_inv_table(self):
        if self._keep_sel is None:          # a toggle / units re-render, not a scan
            try:
                self._keep_sel = {_seg_uid(d["seg"]) for d in self._selected_inv()}
            except Exception:
                self._keep_sel = None
        status_col = next(c for c, col in enumerate(INV_COLS) if col[0] == "status")
        grouped = self.inv_group_text.isChecked()
        # reference sequence for grouped In/Dur (longest one in the scan)
        self._longest_seq = longest_sequence_name(self._inv) if grouped else None
        rows = inv_row_models(self._inv, self.inv_hide_assigned.isChecked(), grouped)
        self.inv_table.blockSignals(True)
        self.inv_table.setSortingEnabled(False)
        self.inv_table.setRowCount(len(rows))
        for r, members in enumerate(rows):
            single = len(members) == 1
            d0 = self._inv[members[0]]
            for c, col in enumerate(INV_COLS):
                key = col[0]
                val = self._inv_cell(d0, key) if single else self._inv_group_cell(members, key)
                it = QtWidgets.QTableWidgetItem()
                if isinstance(val, int):
                    it.setData(QtCore.Qt.DisplayRole, val)   # numeric sort
                else:
                    it.setText(str(val))
                if c == 0:
                    # carry every underlying inv index, so a grouped row assigns all
                    it.setData(QtCore.Qt.UserRole, list(members))
                if c == status_col and single:
                    if d0["num"] is not None and not d0["in_sync"]:
                        it.setForeground(QtGui.QColor("#e0b000"))
                    elif d0["num"] is None:
                        it.setForeground(QtGui.QColor("#888888"))
                self.inv_table.setItem(r, c, it)
        self.inv_table.setSortingEnabled(True)
        keep = self._keep_sel
        self._keep_sel = None
        self.inv_table.clearSelection()
        if keep:
            # never carry a key two segments share (an identity collision):
            # that would quietly add the partner to the selection
            ikeys = [_seg_uid(d["seg"]) for d in self._inv]
            keep = keep - set(identity_collisions(ikeys))
            rows_on = [r for r in range(self.inv_table.rowCount())
                       if any(ikeys[i] in keep for i in
                              (self.inv_table.item(r, 0).data(QtCore.Qt.UserRole) or []))]
            if rows_on:
                # one selection of contiguous runs, applied once (per-row
                # select() calls fragment the selection and go quadratic)
                model, last = self.inv_table.model(), self.inv_table.columnCount() - 1
                sel = QtCore.QItemSelection()
                start = prev = rows_on[0]
                for r in rows_on[1:] + [None]:
                    if r is not None and r == prev + 1:
                        prev = r
                        continue
                    sel.select(model.index(start, 0), model.index(prev, last))
                    if r is not None:
                        start = prev = r
                self.inv_table.selectionModel().select(
                    sel, QtCore.QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows)
        self.inv_table.blockSignals(False)
        self._apply_inv_hidden()
        self._inv_sel_changed()

    def _scan(self):
        warns = []
        scope = self.scope.currentText()
        # keep the Segments selection across the rescan by segment identity --
        # row indices point at different segments once the table re-sorts
        try:
            self._keep_sel = {_seg_uid(d["seg"]) for d in self._selected_inv()}
        except Exception:
            self._keep_sel = None
        try:
            seqs = sequences_for_scope(scope)
            self._inv = graphic_inventory(scope, warnings=warns, seqs=seqs)
        except Exception as e:
            self._say("Scan error: %s" % e)
            seqs, self._inv = [], []
        for wmsg in warns:
            self._say(wmsg)
        # Flame gives segments no id (seg.uid is None), so identity is sequence +
        # name + In. Say so when two scanned graphics share all three.
        scan_keys = [_seg_uid(d["seg"]) for d in self._inv]
        clash = identity_collisions(scan_keys)
        if self._inv and self._sources:
            # only marks whose OWN sequence (and reel) was scanned and whose
            # segment is gone -- a mark that's merely outside this scope stays
            seen = set(scan_keys)
            boxes = {(_clean_name(sq),) + _containers(sq) for sq in seqs}
            gone = {k for k in self._sources
                    if k not in seen and isinstance(k, tuple) and k and k[0] != "uid"
                    and (k[0],) + tuple(k[3:]) in boxes}
            if gone:
                self._sources -= gone
                self._say("Cleared %d Set as Source mark(s): the marked segment is no longer "
                          "in the scan (moved, renamed or out of scope)." % len(gone))
        if clash:
            where = sorted({str(k[0]) for k in clash if isinstance(k, tuple) and k[0] != "uid"})
            self._say("⚠ %d graphic(s) share a sequence, name and In with another, so the "
                      "Connections tab can't tell them apart. Give one of each pair a segment "
                      "name in Flame. In: %s" % (sum(clash.values()), ", ".join(where) or "?"))
        if not seqs:
            # scope resolved to nothing -- say WHY instead of a silent empty table
            if scope == "Selected":
                self.scope_summary.setText("Nothing selected in the Media Panel.")
            else:
                self.scope_summary.setText("No sequences \u2014 open one in the Timeline tab, or use Selected.")
                self._say("Scope '%s' anchors to the Timeline; with nothing loaded there it "
                          "finds nothing. Switch to Flame's Timeline tab (a sequence open), or "
                          "use the Selected scope." % scope)
        else:
            assigned = sum(1 for d in self._inv if d["num"])
            ood = sum(1 for d in self._inv if d["num"] and not d["in_sync"])
            bits = ["%d graphic(s) \u00b7 %d sequence(s)" % (len(self._inv), len(seqs)),
                    "%d assigned" % assigned, "%d unassigned" % (len(self._inv) - assigned)]
            if ood:
                bits.append("%d OUT OF DATE" % ood)
            self.scope_summary.setText("   \u00b7   ".join(bits))
        self._render_inv_table()
        self._render_connections()      # same scan feeds the Connections tab
        self._tl_dirty = True           # ...and the Timelines tab, when shown
        if self.tabs.currentIndex() == _TAB_INDEX["Timelines"]:
            self._render_timelines()
        self._refresh_assign_combo()
        self._inv_sel_changed()

    def _assign_combo_key(self):
        """The selected Type key ('01'), read from item DATA -- never parse the
        display text, which now carries a text preview that may contain digits."""
        i = self.assign_combo.currentIndex()
        if i < 0:
            return None
        return self.assign_combo.itemData(i)

    def _refresh_assign_combo(self):
        """Populate the Assign dropdown from the registry, each entry showing a
        first-line preview ('Type01 — Legal line one…') so the Type→text mapping
        is visible right where you assign. The key is stored as item data."""
        prev = self._assign_combo_key()
        reg = load_registry()
        self.assign_combo.blockSignals(True)
        self.assign_combo.clear()
        for k in sorted(reg.keys()):
            lines = reg[k].get("lines", [])
            head = ""
            if lines:
                parts = str(lines[0]).splitlines()
                head = parts[0].strip() if parts else ""
            label = "Type%s" % k
            if head:
                label += "  —  " + (head[:36] + ("…" if len(head) > 36 else ""))
            self.assign_combo.addItem(label, k)
        if prev is not None:
            j = self.assign_combo.findData(prev)
            if j >= 0:
                self.assign_combo.setCurrentIndex(j)
        self.assign_combo.blockSignals(False)

    def _selected_inv(self):
        """Selected inventory rows expanded to underlying inv dicts. A normal row
        yields one; a Grouped-Text row yields all the segments it folds."""
        out = []
        for mi in self.inv_table.selectionModel().selectedRows():
            it = self.inv_table.item(mi.row(), 0)
            if it is None:
                continue
            di = it.data(QtCore.Qt.UserRole)
            members = di if isinstance(di, list) else ([di] if isinstance(di, int) else [])
            for i in members:
                if isinstance(i, int) and 0 <= i < len(self._inv):
                    out.append(self._inv[i])
        return out

    def _selected_inv_rows(self):
        """Selected rows, each as a list of underlying inv dicts (one element for
        a normal row, several for a Grouped-Text row). Unlike _selected_inv, this
        preserves row boundaries so 'one selected row' is distinguishable from
        'several segments' -- a folded group is still ONE text."""
        rows = []
        for mi in self.inv_table.selectionModel().selectedRows():
            it = self.inv_table.item(mi.row(), 0)
            if it is None:
                continue
            di = it.data(QtCore.Qt.UserRole)
            members = di if isinstance(di, list) else ([di] if isinstance(di, int) else [])
            ds = [self._inv[i] for i in members if isinstance(i, int) and 0 <= i < len(self._inv)]
            if ds:
                rows.append(ds)
        return rows

    def _inv_sel_changed(self):
        sel = self._selected_inv()
        self.b_assign.setEnabled(bool(sel) and self.assign_combo.count() > 0)
        # one selected ROW (folded group or single) = one text -> can capture it
        self.b_addreg.setEnabled(len(self._selected_inv_rows()) == 1)
        self._refresh_sync_buttons(sel)

    def _refresh_sync_buttons(self, sel=None):
        """Sync Selected / Sync All are grey until there's registry text to push
        -- and, for Selected, until the selection holds an assigned segment
        whose Type has registry text. The tooltip says which."""
        if not hasattr(self, "b_sync_sel"):
            return
        reg = load_registry()
        sel = self._selected_inv() if sel is None else sel
        sel_ok = bool(text_sync_targets(rows_sharing_gfx(sel, self._inv)[0], reg)[0])
        all_ok = bool(text_sync_targets(self._inv, reg)[0])
        self.b_sync_sel.setEnabled(sel_ok)
        self.b_sync_all.setEnabled(all_ok)
        if not reg:
            why = "The registry is empty — add graphics first (Add to Registry / Add All)."
            self.b_sync_sel.setToolTip(why)
            self.b_sync_all.setToolTip(why)
            return
        self.b_sync_sel.setToolTip(
            "Push registry text onto every segment that shares the selected rows' "
            "Type number(s), in every aspect. Shows every change and asks first."
            if sel_ok else "Select assigned segments whose Type has registry text.")
        self.b_sync_all.setToolTip(
            "Push registry text onto every assigned segment in the current Scope. "
            "Shows every change and asks first." if all_ok else
            "No assigned segment in this Scope has registry text yet.")

    def _confirm_sync(self, title, text, detail):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(text)
        if detail:
            box.setDetailedText(detail)
        box.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        box.setDefaultButton(QtWidgets.QMessageBox.No)
        return box.exec() == QtWidgets.QMessageBox.Yes

    def _sync_segments(self, what):
        """Registry -> segments ('Selected' or 'All'), previewed first. Flame is
        live while Type Sync is open, so it re-reads Flame before planning (the
        selection is carried across by segment identity); the dry run then reads
        each Type's text NOW, so the confirm box shows exactly what will be
        written, and only segments that would change are touched."""
        # the selection only picks Type NUMBERS -- remember them before the
        # rescan (identity-colliding rows aren't carried across it)
        picked = list(self._selected_inv()) if what == "Selected" else []
        try:
            picked_keys = {_seg_uid(d["seg"]) for d in picked}
        except Exception:
            picked_keys = set()
        self._goto_timeline()
        self._scan()
        if not self._inv:
            self._say("Sync %s: nothing scanned — Flame's Timeline must show a sequence "
                      "in the current Scope." % what)
            return
        if what == "Selected":
            # the scope follows Flame: if NONE of the picked rows is in the fresh
            # scan, the selection belongs to another place -- don't guess
            if picked and not (picked_keys & {_seg_uid(d["seg"]) for d in self._inv}):
                self._say("Sync Selected: the rows you picked aren't in the current scan any "
                          "more (Flame moved to another sequence or reel?). Select them again "
                          "and retry. Nothing changed.")
                return
            # every scanned segment sharing the picked Type number(s) syncs
            rows, sel_unassigned = rows_sharing_gfx(picked, self._inv)
        else:
            rows, sel_unassigned = list(self._inv), 0
        reg = load_registry()
        targets, unassigned, no_entry = text_sync_targets(rows, reg)
        unassigned += sel_unassigned
        skipped = []
        if unassigned:
            skipped.append("%d with no Type number" % unassigned)
        if no_entry:
            skipped.append("%d whose Type has no registry text" % no_entry)
        skip_note = ("Skipped: %s." % "; ".join(skipped)) if skipped else ""
        items, todo, dry = [], [], {}
        for d, lines in targets:
            ch = push_text(d["seg"], lines, dry_run=True)
            if ch:
                todo.append((d, lines))
                dry[id(d)] = ch
        # same-named sequences in different reels must be told apart in the box
        boxes = {}
        for d, _l in todo:
            k = _seg_uid(d["seg"])
            boxes.setdefault(d["seq"], set()).add(tuple(k[3:]) if isinstance(k, tuple) else ())
        for d, lines in todo:
            k = _seg_uid(d["seg"])
            where = d["seq"]
            if len(boxes[d["seq"]]) > 1 and isinstance(k, tuple) and len(k) > 3:
                where = "%s \u00b7 %s" % (d["seq"], " / ".join(str(x) for x in k[3:]))
            items += [(where, _key(d["num"]), li, old, new) for _s, li, old, new in dry[id(d)]]
        if not todo:
            self._say("Sync %s: nothing to change — already in sync.%s"
                      % (what, ("  " + skip_note) if skip_note else ""))
            return
        summary, detail = format_text_changes(items)
        nseq = len({d["seq"] for d, _l in todo})
        text = ("Sync registry text onto %d segment(s) in %d sequence(s)?  "
                "%d layer(s) change:\n\n%s%s"
                % (len(todo), nseq, len(items), summary,
                   ("\n\n" + skip_note) if skip_note else ""))
        if not self._confirm_sync("Sync %s" % what, text, detail):
            return
        warns, done = [], 0
        for d, lines in todo:
            done += len(push_text(d["seg"], lines, dry_run=False, warnings=warns))
        for wmsg in warns:
            self._say(wmsg)
        self._say("Sync %s: wrote %d layer(s) on %d segment(s)." % (what, done, len(todo)))
        self._scan()

    def _inv_group_toggled(self, on):
        # "Add All to Registry" only makes sense when each row is one graphic
        self.b_addall.setVisible(on)
        self._render_inv_table()

    def _visible_inv_rows(self):
        """Grouped rows in the current (sorted) visual order, each a list of inv
        dicts. Reads the table so it honors the user's sort (e.g. by In)."""
        rows = []
        for r in range(self.inv_table.rowCount()):
            it = self.inv_table.item(r, 0)
            if it is None:
                continue
            di = it.data(QtCore.Qt.UserRole)
            members = di if isinstance(di, list) else ([di] if isinstance(di, int) else [])
            ds = [self._inv[i] for i in members if isinstance(i, int) and 0 <= i < len(self._inv)]
            if ds:
                rows.append(ds)
        return rows

    def _add_all_to_registry(self):
        if not self.inv_group_text.isChecked():
            return
        rows = self._visible_inv_rows()
        rows = [ds for ds in rows if segment_text(ds[0]["seg"])]   # need text to add
        if not rows:
            self._say("No grouped rows with text to add.")
            return
        if QtWidgets.QMessageBox.question(
                self, "Add All to Registry",
                "Add all %d grouped graphic(s) to the registry in the current "
                "order, filling the next free Type numbers, and assign their "
                "segments?\n\n(Type numbers follow the table's sort order.)" % len(rows),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        used = set(load_registry().keys())
        added, assigned, n, first, last = 0, 0, 1, None, None
        for ds in rows:
            lines = segment_text(ds[0]["seg"])
            while _key(n) in used and n < 99:
                n += 1
            num = n
            registry_set(num, lines)
            used.add(_key(num))
            first = first if first is not None else num
            last = num
            for m in ds:
                try:
                    assign_graphic(m["seg"], num)
                    assigned += 1
                except Exception as e:
                    self._say("Auto-assign failed (%s): %s" % (m["seq"], e))
            added += 1
            n += 1
        rng = ("Type%s" % _key(first)) if first == last else ("Type%s–Type%s" % (_key(first), _key(last)))
        self._say("Add All: created %d entr%s (%s) and assigned %d segment(s)."
                  % (added, "y" if added == 1 else "ies", rng, assigned))
        self._reload_registry_table()
        self._scan()

    def _assign(self):
        sel = self._selected_inv()
        num = self._assign_combo_key()
        if not sel or num is None:
            return
        tag_text = "Type%s" % num
        n = 0
        for d in sel:
            try:
                assign_graphic(d["seg"], int(num))   # tags only, never writes text
                n += 1
            except Exception as e:
                self._say("Assign failed (%s): %s" % (d["seq"], e))
        self._say("Assigned %d segment(s) to %s. Anything OUT OF DATE? "
                  "Use Sync Text to push the registry text." % (n, tag_text))
        self._scan()

    def _add_to_registry(self):
        rows = self._selected_inv_rows()
        if len(rows) != 1:
            return
        members = rows[0]
        # a Grouped-Text row folds segments that share the same Text, so any one
        # is representative -- capture from the first.
        d = members[0]
        lines = segment_text(d["seg"])
        if not lines:
            self._say("That segment has no Type text to capture.")
            return
        reg = load_registry()
        free = 1
        while _key(free) in reg and free < 99:
            free += 1
        # Add to Registry is INDEPENDENT of the segment's current assignment: it
        # defaults to the next free slot. If the segment IS already assigned, let
        # the user choose explicitly rather than silently overwriting that entry.
        num = free
        if d["num"] is not None:
            cur_num = int(d["num"])
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle("Add to Registry")
            box.setText(
                "This segment is assigned to Type%s.\n\n"
                "Add as new — create Type%s (next free slot).\n"
                "Update Type%s — replace its text with this segment's."
                % (_key(cur_num), _key(free), _key(cur_num)))
            box.setStyleSheet(STYLE)
            new_b = box.addButton("Add as Type%s" % _key(free), QtWidgets.QMessageBox.AcceptRole)
            upd_b = box.addButton("Update Type%s" % _key(cur_num), QtWidgets.QMessageBox.ActionRole)
            box.addButton("Cancel", QtWidgets.QMessageBox.RejectRole)
            box.setDefaultButton(new_b)
            box.exec()
            clicked = box.clickedButton()
            if clicked is new_b:
                num = free
            elif clicked is upd_b:
                num = cur_num
            else:
                return
        registry_set(num, lines)
        # Grouped Text: we have every segment of this graphic AND the number it
        # just got, so consolidate Add + Assign -- tag them all to it in one step.
        # (Assign is tag-only, so this writes no text; mismatches still show OUT
        # OF DATE.) Single-segment adds stay capture-only, as before.
        assigned = 0
        if len(members) > 1:
            for m in members:
                try:
                    assign_graphic(m["seg"], num)
                    assigned += 1
                except Exception as e:
                    self._say("Auto-assign failed (%s): %s" % (m["seq"], e))
        if assigned:
            self._say("Added Type%s from grouped text and assigned %d segment(s) to it "
                      "(%d layer(s))." % (_key(num), assigned, len(lines)))
        else:
            self._say("Added Type%s to registry from %s (%d layer(s))."
                      % (_key(num), d["seq"], len(lines)))
        self.reg_spin.setValue(num)
        self.reg_text.setPlainText(layers_to_text(lines))
        self._reload_registry_table()
        self._scan()

    # ---------------------------------------------------------------- Connections tab
    def _build_connections_tab(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        self.conn_label = QtWidgets.QLabel("Scanning…")
        v.addWidget(self.conn_label)

        sortrow = QtWidgets.QHBoxLayout()
        sortrow.addWidget(QtWidgets.QLabel("Sort:"))
        self.conn_sort = QtWidgets.QComboBox()
        self.conn_sort.addItems(["Connection groups", "Type", "Aspect", "Sequence"])
        self.conn_sort.currentTextChanged.connect(self._render_connections)
        sortrow.addWidget(self.conn_sort)
        sortrow.addStretch(1)
        sortrow.addWidget(self._tips_button())
        v.addLayout(sortrow)

        self.conn_table = QtWidgets.QTableWidget(0, 7)
        self.conn_table.setHorizontalHeaderLabels(
            ["Sequence", "Name", "Aspect", "Type", "Grp", "Conn", "Text"])
        self.conn_table.verticalHeader().setVisible(False)
        self.conn_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.conn_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.conn_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # cols: Sequence Name Aspect Type Grp Conn Text -- all draggable except
        # Text, which stretches to fill the slack.
        ch = self.conn_table.horizontalHeader()
        _CW = [160, 150, 60, 60, 50, 55]   # Sequence, Name, Aspect, Type, Grp, Conn
        for c in range(6):
            ch.setSectionResizeMode(c, QtWidgets.QHeaderView.Interactive)
            self.conn_table.setColumnWidth(c, _CW[c])
        ch.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        ch.setStyle(self._grip_style)   # wider grab zone
        self.conn_table.itemSelectionChanged.connect(self._conn_sel_changed)
        v.addWidget(self.conn_table, 1)

        legend = QtWidgets.QLabel(
            "Rows packed together with no gap are connected to each other; a blank "
            "row separates one group from the next. Every look has a letter (Grp): a "
            "connected set shares one, a lone segment has its own, and the Timelines "
            "tab uses the same letters. "
            "Break removes a connection. Auto Connection queues a group for every "
            "like-aspect, like-Type set across the scope automatically: new segments "
            "join an existing connected set (Q1 \u2192 A: only the Q rows change), a Type number "
            "split across 2+ connected sets is reported, never queued, and a group "
            "that won't run is marked \u26a0 (hover for why). "
            "Multi Segment Connection does the same for a hand-picked set: select the "
            "same-aspect rows (the same graphic) and connect them \u2014 each keeps its "
            "own position and duration. In the confirm box: Yes runs now and closes, "
            "Queue stacks the group (shown italic/amber with a Q tag) to run later, No "
            "cancels. Execute Queue runs everything stacked. Set as Source marks a "
            "segment (★ gold) as its group's master, so ITS layout is the one that "
            "propagates; one per group (two ★ in a group refuses), none = auto-pick.")
        legend.setWordWrap(True)
        legend.setStyleSheet("color:#777777;")
        self._tip_label(legend)
        v.addWidget(legend)

        actions = QtWidgets.QGroupBox("ACTIONS  (select rows above)")
        a = QtWidgets.QHBoxLayout(actions)
        a.addStretch(1)
        self.b_conn_break = QtWidgets.QPushButton("Break Selected")
        self.b_conn_break.setEnabled(False)
        self.b_conn_break.setToolTip("Select 1+ rows to remove their connection.")
        self.b_conn_break.clicked.connect(self._break_selected)
        a.addWidget(self.b_conn_break)
        self.b_conn_source = QtWidgets.QPushButton("Set as Source")
        self.b_conn_source.setEnabled(False)
        self.b_conn_source.setToolTip(
            "Mark the selected segment (★) as the source/master for its connection "
            "group — its layout is the one that propagates. One per group; mark a "
            "second in the same group and connecting will refuse. Unmarked groups "
            "auto-pick as before. Click again to unmark.")
        self.b_conn_source.clicked.connect(self._toggle_source)
        a.addWidget(self.b_conn_source)
        self.b_conn_auto = QtWidgets.QPushButton("Auto Connection")
        self.b_conn_auto.setToolTip(
            "Queue a connection group for every set of like-aspect, like-Type "
            "segments across the scope automatically. New segments join an "
            "existing connected set; already-connected sets are skipped, and a Type number "
            "split across 2+ sets is reported, not queued. Review the Q rows, then "
            "Execute Queue.")
        self.b_conn_auto.clicked.connect(self._auto_connection)
        a.addWidget(self.b_conn_auto)
        self.b_conn_copy = QtWidgets.QPushButton("Multi Segment Connection")
        self.b_conn_copy.setEnabled(False)
        self.b_conn_copy.setToolTip(
            "Select the same-aspect rows for one graphic (2+), or one row to pick its "
            "target sequences. Confirm box offers Yes / Queue / No.")
        self.b_conn_copy.clicked.connect(self._multi_segment_connection)
        a.addWidget(self.b_conn_copy)
        self.b_conn_exec = QtWidgets.QPushButton("Execute Queue")
        self.b_conn_exec.setObjectName("primary")
        self.b_conn_exec.setToolTip("Run every queued connection group, then close.")
        self.b_conn_exec.clicked.connect(self._execute_queue)
        self.b_conn_exec.setVisible(False)
        a.addWidget(self.b_conn_exec)
        self.b_conn_clearq = QtWidgets.QPushButton("Clear Queue")
        self.b_conn_clearq.setToolTip("Discard all queued groups (no timeline changes).")
        self.b_conn_clearq.clicked.connect(self._clear_queue)
        self.b_conn_clearq.setVisible(False)
        a.addWidget(self.b_conn_clearq)
        self.b_conn_sync = QtWidgets.QPushButton("Sync Connected Segments")
        self.b_conn_sync.setToolTip(
            "Push the selected segment's layout out to every segment connected "
            "to it (Flame's sync_connected_segments).")
        self.b_conn_sync.clicked.connect(self._sync_layout_conn)
        a.addWidget(self.b_conn_sync)
        v.addWidget(actions)
        return w

    def _scan_connections(self):
        self._scan()        # one walk refreshes both tabs

    def _render_connections(self, *_):
        inv = self._inv
        groups, cluster_of, size_of, tainted, keys = link_context(inv)
        self._ctx = (groups, cluster_of, size_of, tainted, keys)   # Timelines reuses it
        # a set counts as connected even when its other members are outside
        # the scan (another reel) -- it gets a letter like any other set
        clusters = [g for cid, g in enumerate(groups) if size_of.get(cid, 1) > 1]
        singles_idx = [g[0] for cid, g in enumerate(groups) if size_of.get(cid, 1) <= 1]
        # one letter per LOOK: connected sets first (A, B, ...), then every lone
        # graphic, rolling over to AA after Z -- same letters as the Timelines tab
        letters = group_letters(groups, size_of)
        label_of, single_label = {}, {}
        for cid, g in enumerate(groups):
            for ii in g:
                if size_of.get(cid, 1) > 1:
                    label_of[ii] = letters[cid]
                else:
                    single_label[ii] = letters[cid]
        cluster_member = set(label_of.keys())

        # Resolve the queue with the SAME call Execute Queue makes, so each Q
        # row is a segment that group will connect. A group joining an existing
        # set names it ("Q1 -> A") and only its Q rows are replaced; a star =
        # re-lay-out from a marked source; a warning sign = it won't run (hover
        # for why). Groups whose segments left the scan are dropped, never
        # re-planned into something that wasn't reviewed.
        key_to_idx = {}
        for i, k in enumerate(keys):
            key_to_idx.setdefault(k, i)
        marked = {i for i, k in enumerate(keys) if k in self._sources}
        # nothing scanned (Flame not showing a sequence?) -> keep the queue as is
        # rather than drop every group as "gone"; Execute refuses until a scan
        res = resolve_queue(self._queue or [], key_to_idx, cluster_of, size_of,
                            marked, tainted) if inv else []
        qblocks, qlabel_of, queued, kept, qnum, gone, blocked = [], {}, set(), [], {}, 0, 0
        sig = []        # what the Q rows show -- Execute Queue re-checks it
        for gi, (g, r) in enumerate(zip(self._queue or [], res)):
            plan = r["plan"]
            if r["missing"]:
                gone += 1
                continue
            if not plan["work"]:
                continue                  # already all connected
            qnum[gi] = len(kept) + 1
            lab = "Q%d" % qnum[gi]
            if plan["anchor"] is not None:
                lab += " → " + (label_of.get(groups[plan["anchor"]][0]) or "outside scope")
            if plan["relayout"]:
                lab += " ★"
            why = plan["error"]
            if not why and r["overlap"] is not None:
                why = ("shares a segment with Q%d, which runs first — run the queue, then "
                       "Auto Connection again." % qnum.get(r["overlap"], r["overlap"] + 1))
            if why:
                lab += " ⚠"
                blocked += 1
            members = plan["targets"] or r["idxs"]
            qblocks.append((lab, members, why))
            sig.append((tuple(sorted(keys[i] for i in members)),
                        keys[plan["master"]] if plan["master"] is not None else None, lab))
            for i in members:
                if i not in qlabel_of or (qlabel_of[i][1] and not why):
                    qlabel_of[i] = (lab, why)   # the group that will run wins
                queued.add(i)
            kept.append(g)
        if inv and len(kept) != len(self._queue):
            self._queue = kept
        self._queue_sig = sig if inv else None
        if gone:
            self._say("Dropped %d queued group(s): some of their segments are no longer in the "
                      "scan (scope changed?). Run Auto Connection again." % gone)

        self.conn_label.setText(
            "%d connected cluster(s), %d unconnected, %d queued group(s)%s in '%s'"
            % (len(clusters), len(singles_idx), len(kept) if inv else len(self._queue or []),
               (" (%d won't run — hover the ⚠)" % blocked) if blocked else
               (" (kept — nothing scanned; Rescan on a sequence)" if not inv and self._queue else ""),
               self.scope.currentText()))

        mode = self.conn_sort.currentText() if hasattr(self, "conn_sort") else "Connection groups"
        rows = []
        if mode == "Connection groups":
            # a queued re-lay-out or merge lists set members in its Q block, so
            # they're left out of their set's block rather than shown twice
            blocks = [(None, [i for i in g if i not in queued]) for g in clusters]
            blocks = [b for b in blocks if b[1]]
            blocks += [((lab, why), m) for lab, m, why in qblocks]
            placed = cluster_member | queued
            blocks += [(None, [i]) for i in range(len(inv)) if i not in placed]
            for bi, (q, g) in enumerate(blocks):
                for ii in g:
                    rows.append(("seg", ii, q))
                if bi != len(blocks) - 1:
                    rows.append(("spacer", None, None))
        else:
            def key(ii):
                d = inv[ii]
                if mode == "Type":
                    return (d["num"] or "~~", d["seq"])
                if mode == "Aspect":
                    return (d["aspect"], d["seq"])
                return (d["seq"],)
            for ii in sorted(range(len(inv)), key=key):
                rows.append(("seg", ii, qlabel_of.get(ii)))

        amber = QtGui.QColor("#d9a441")
        cyan = QtGui.QColor("#00b4d8")
        gold = QtGui.QColor("#ffcc33")
        self.conn_table.blockSignals(True)
        self.conn_table.setRowCount(len(rows))
        for r, (kind, ii, q) in enumerate(rows):
            if kind == "spacer":
                for c in range(7):
                    cell = QtWidgets.QTableWidgetItem("")
                    cell.setFlags(QtCore.Qt.NoItemFlags)
                    cell.setBackground(QtGui.QColor("#0d0d0d"))
                    self.conn_table.setItem(r, c, cell)
                self.conn_table.setRowHeight(r, 7)
                continue
            d = inv[ii]
            gid = ("Type" + d["num"]) if d["num"] else "—"
            is_q = q is not None
            grp = q[0] if is_q else label_of.get(ii) or single_label.get(ii, "")
            is_src = keys[ii] in self._sources
            tl = str(d["text"]).splitlines()
            txt = tl[0] if tl else ""
            seq_label = ("★ " + str(d["seq"])) if is_src else d["seq"]
            vals = [seq_label, d.get("name", ""), d["aspect"], gid, grp,
                    str(d["connected"]), txt]
            for c, val in enumerate(vals):
                cell = QtWidgets.QTableWidgetItem(str(val))
                if c == 0:
                    cell.setData(QtCore.Qt.UserRole, ii)
                if is_q and q[1]:
                    cell.setToolTip("Won't run: " + q[1])
                if is_src and c == 0:
                    f = cell.font(); f.setBold(True); cell.setFont(f)
                    cell.setForeground(gold)
                elif is_q:
                    f = cell.font(); f.setItalic(True); cell.setFont(f)
                    cell.setForeground(amber)
                elif c in (4, 5) and d["connected"]:
                    cell.setForeground(cyan)
                self.conn_table.setItem(r, c, cell)
        self.conn_table.blockSignals(False)
        self._conn_sel_changed()
        self._refresh_queue_buttons()

    def _refresh_queue_buttons(self):
        if not hasattr(self, "b_conn_exec"):
            return
        n = len(self._queue)
        self.b_conn_exec.setVisible(bool(n))
        self.b_conn_exec.setText("Execute Queue (%d)" % n if n else "Execute Queue")
        self.b_conn_clearq.setVisible(bool(n))

    def _selected_conn(self):
        out = []
        for mi in self.conn_table.selectionModel().selectedRows():
            it = self.conn_table.item(mi.row(), 0)
            if it is None:
                continue
            di = it.data(QtCore.Qt.UserRole)
            if isinstance(di, int) and di < len(self._inv):
                out.append(self._inv[di])
        return out

    def _conn_sel_changed(self):
        sel = self._selected_conn()
        self.b_conn_sync.setEnabled(len(sel) == 1)
        self.b_conn_copy.setEnabled(len(sel) >= 1)
        self.b_conn_break.setEnabled(len(sel) >= 1)
        self.b_conn_source.setEnabled(len(sel) == 1)
        if len(sel) == 1:
            on = _seg_uid(sel[0]["seg"]) in self._sources
            self.b_conn_source.setText("Unset Source" if on else "Set as Source")
        else:
            self.b_conn_source.setText("Set as Source")

    def _toggle_source(self):
        """Mark / unmark the selected segment as its group's source (master)."""
        sel = self._selected_conn()
        if len(sel) != 1:
            return
        u = _seg_uid(sel[0]["seg"])
        if u in self._sources:
            self._sources.discard(u)
            self._say("Unmarked %s as source." % sel[0]["seq"])
        else:
            self._sources.add(u)
            self._say("Marked %s as the source (★) for its connection group." % sel[0]["seq"])
        self._render_connections()

    def _group_master(self, segs):
        """(master_seg_or_None, error) for a group, honoring marked sources.
        None master -> connect_segment_group auto-picks."""
        uids = [_seg_uid(s) for s in segs]
        idx, err = resolve_group_source(uids, self._sources)
        if err:
            return None, err
        return (segs[idx] if idx is not None else None), None

    def _break_selected(self):
        sel = self._selected_conn()
        if not sel:
            return
        if QtWidgets.QMessageBox.question(
                self, "Break Selected",
                "Remove the connection from %d selected segment(s)?" % len(sel),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        n = 0
        for d in sel:
            try:
                d["seg"].remove_connection()
                n += 1
            except Exception as e:
                self._say("Break failed (%s): %s" % (d["seq"], e))
        self._say("remove_connection() on %d segment(s). Re-scanning to confirm grouping." % n)
        if n and self._queue:
            # queued groups were planned against the sets that just changed
            self._say("Queue cleared (%d group(s)) \u2014 the connections it was built on "
                      "changed. Run Auto Connection again." % len(self._queue))
            self._queue = []
        self._scan_connections()

    def _pick_targets(self, candidates):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle("Multi Segment Connection")
        lay = QtWidgets.QVBoxLayout(dlg)
        lay.addWidget(QtWidgets.QLabel("Check the sequences to copy into (same aspect):"))
        lw = QtWidgets.QListWidget()
        for name, seq in candidates:
            it = QtWidgets.QListWidgetItem(name)
            it.setFlags(it.flags() | QtCore.Qt.ItemIsUserCheckable)
            it.setCheckState(QtCore.Qt.Unchecked)
            it.setData(QtCore.Qt.UserRole, seq)
            lw.addItem(it)
        lay.addWidget(lw)
        togg = QtWidgets.QHBoxLayout()
        ball = QtWidgets.QPushButton("Check All")
        bclr = QtWidgets.QPushButton("Clear")

        def _set_all(state):
            for i in range(lw.count()):
                lw.item(i).setCheckState(state)
        ball.clicked.connect(lambda: _set_all(QtCore.Qt.Checked))
        bclr.clicked.connect(lambda: _set_all(QtCore.Qt.Unchecked))
        togg.addWidget(ball)
        togg.addWidget(bclr)
        togg.addStretch(1)
        lay.addLayout(togg)
        bb = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        bb.accepted.connect(dlg.accept)
        bb.rejected.connect(dlg.reject)
        lay.addWidget(bb)
        dlg.resize(440, 400)
        if dlg.exec() != QtWidgets.QDialog.Accepted:
            return []
        out = []
        for i in range(lw.count()):
            it = lw.item(i)
            if it.checkState() == QtCore.Qt.Checked:
                out.append(it.data(QtCore.Qt.UserRole))
        return out

    def _collect_group(self):
        """Build the segment list to connect from the current selection.
        Returns (segs, note) on success (segs has the master first), or
        (None, reason) to abort. (None, None) means the user cancelled a picker."""
        sel = self._selected_conn()
        if not sel:
            return None, "Select row(s) first."
        aspect = sel[0]["aspect"]
        if len(sel) == 1:
            md = sel[0]
            num = md["num"]
            if not num:
                return None, ("That segment has no Type number, so I can't find its "
                              "matches automatically. Assign it first, or select the "
                              "matching rows directly (2+).")
            src_seq_name = _clean_name(_ancestor(md["seg"], "PySequence"))
            cands = []
            for seq in sequences_for_scope(self.scope.currentText()):
                if _clean_name(seq) == src_seq_name or detect_aspect(seq) != aspect:
                    continue
                cands.append((_clean_name(seq), seq))
            if not cands:
                return None, "No other %s sequences in '%s' to connect." % (aspect, self.scope.currentText())
            seqs = self._pick_targets(sorted(cands, key=lambda x: x[0]))
            if not seqs:
                return None, None
            segs, missing = [md["seg"]], []
            for seq in seqs:
                found = None
                for s in iter_segments(seq):
                    if tag_to_instance(read_tag(s) or "") == num:
                        found = s
                        break
                if found is not None:
                    segs.append(found)
                else:
                    missing.append(_clean_name(seq))
            if len(segs) < 2:
                return None, "None of the chosen sequences contain Type%s." % num
            note = ("No Type%s in: %s (skipped)." % (num, ", ".join(missing))) if missing else None
            return segs, note
        # 2+ rows selected -> that IS the group
        aspects = sorted({d["aspect"] for d in sel})
        if len(aspects) > 1:
            return None, ("Mixed aspects (%s). Connect within one aspect at a time \u2014 "
                          "positions differ across aspects." % ", ".join(aspects))
        nums = sorted({d["num"] for d in sel if d["num"]})
        note = None
        if len(nums) > 1:
            note = ("Heads up: selection spans Type %s \u2014 connecting unifies them to the "
                    "master's content." % "/".join(nums))
        return [d["seg"] for d in sel], note

    def _confirm_three(self, text):
        box = QtWidgets.QMessageBox(self)
        box.setWindowTitle("Multi Segment Connection")
        box.setText(text)
        box.setStyleSheet(STYLE)
        yes_b = box.addButton("Yes \u2014 run now", QtWidgets.QMessageBox.AcceptRole)
        q_b = box.addButton("Queue", QtWidgets.QMessageBox.ActionRole)
        box.addButton("No", QtWidgets.QMessageBox.RejectRole)
        box.exec()
        clicked = box.clickedButton()
        if clicked is yes_b:
            return "yes"
        if clicked is q_b:
            return "queue"
        return "no"

    def _multi_segment_connection(self):
        segs, note = self._collect_group()
        if segs is None:
            if note:
                self._say(note)
            return
        if note:
            self._say(note)
        # one row per segment: a segment shown in two Q blocks can be selected
        # twice, and connecting it twice would reuse a handle made stale by the
        # first overwrite
        seen, uniq = set(), []
        for sg in segs:
            k = _seg_uid(sg)
            if k not in seen:
                seen.add(k)
                uniq.append(sg)
        segs = uniq
        if len(segs) < 2:
            self._say("Select at least two different segments to connect.")
            return
        # Plan with the same call Execute Queue uses, so Yes (run now) and Queue
        # (run later) do the same thing and the confirm box describes both.
        inv = self._inv or []
        _g, cluster_of, size_of, tainted, keys = link_context(inv)
        key_to_idx = {}
        for i, k in enumerate(keys):
            key_to_idx.setdefault(k, i)
        marked = {i for i, k in enumerate(keys) if k in self._sources}
        idxs = [key_to_idx.get(_seg_uid(s)) for s in segs]
        plan = None
        if all(i is not None for i in idxs):
            plan = plan_connection_group(idxs, cluster_of, size_of, marked, tainted)
            if plan["error"]:
                self._say("Multi Segment Connection: " + plan["error"])
                return
            if not plan["work"]:
                self._say("Those %d segments are already connected to each other — nothing "
                          "to do. (To push one segment's layout to the rest of its set, select "
                          "it and use Sync Connected Segments.)" % len(segs))
                return
        if plan is not None and plan["master"] is not None:
            master = inv[plan["master"]]["seg"]
            chosen = master
            run = [master] + [inv[i]["seg"] for i in plan["targets"]]
            where = _clean_name(_ancestor(master, "PySequence"))
            if plan["relayout"]:
                text = ("Re-lay-out a connected set from the marked source?\n\n"
                        "'%s' in %s (★ source) is copied over the other %d segment(s), "
                        "replacing the set's layout. Each keeps its own position and "
                        "duration. Undoable in Flame."
                        % (_clean_name(master), where, len(plan["targets"])))
            else:
                how = "marked source" if plan["master"] in marked else "already in the set"
                text = ("Join %d segment(s) to an existing connected set?\n\n"
                        "Layout comes from '%s' in %s (%s). Only the %d joining segment(s) "
                        "are replaced, each keeping its own position and duration; the set "
                        "itself is left as is. Undoable in Flame."
                        % (len(plan["targets"]), _clean_name(master), where, how,
                           len(plan["targets"])))
        else:
            chosen, serr = self._group_master(segs)        # honor a marked source
            if serr:
                self._say(serr)
                return
            run = segs
            master = chosen or next((s for s in segs if _conn_count(s) > 0), segs[0])
            how = "marked source" if chosen else "auto-picked"
            text = ("Connect %d same-aspect segment(s) as one group?\n\n"
                    "Master (%s): '%s' in %s. The other %d will be replaced with a "
                    "connected copy, each keeping its own position and duration. "
                    "Undoable in Flame."
                    % (len(segs), how, _clean_name(master),
                       _clean_name(_ancestor(master, "PySequence")), len(segs) - 1))
        choice = self._confirm_three(text)
        if choice == "no":
            return
        if choice == "queue":
            if plan is None:
                self._say("Can't queue this group: part of it isn't in the scan (check the "
                          "Settings filters). Use Yes to run it now instead.")
                return
            stored = [_seg_uid(s) for s in segs]
            if plan["master"] is not None and keys[plan["master"]] not in stored:
                # the confirm box named a Set as Source master outside the
                # selection: keep it in the group, so if it leaves the scan the
                # group is dropped instead of quietly re-planned with another
                stored.append(keys[plan["master"]])
            self._queue.append(stored)
            self._say("Queued group %d (%d segments). Press Execute Queue when ready."
                      % (len(self._queue), len(segs)))
            self._render_connections()
            return
        # yes -> run now, then close (per spec: we're done)
        original_seq = _ancestor(_current_segment(), "PySequence")   # before mutating
        # collect affected sequences BEFORE connecting -- overwrite makes the
        # destination seg handles stale, so _ancestor would fail for them after.
        affected = {}
        for s in run:
            sq = _ancestor(s, "PySequence")
            if sq is not None:
                affected.setdefault(id(sq), sq)
        done, master, errors = connect_segment_group(run, master=chosen)
        self._reset_playheads_and_focus(affected.values(), original_seq)
        msgs = ["Connect issue (%s): %s" % (nm, e) for nm, e in errors]
        msgs.append("Connected %d segment(s) to master '%s'."
                    % (done, _clean_name(master) if master else "?"))
        self._finish_after_ops(msgs, close=True)

    def _execute_queue(self):
        if not self._queue:
            return
        # Flame stays live while Type Sync is open, so re-read it first and run
        # only if every group still resolves exactly as the Q rows showed it.
        shown = list(self._queue_sig or [])
        self._goto_timeline()
        self._scan()
        if not self._inv:
            self._say("Execute Queue: nothing scanned — Flame's Timeline must show a "
                      "sequence in the current Scope. The queue is kept; try again there.")
            return
        if not self._queue:
            self._say("Execute Queue: nothing left to run after re-reading Flame.")
            return
        if self._queue_sig != shown:
            self._say("Execute Queue: Flame changed since the Q rows were drawn \u2014 "
                      "they're updated now. Review them, then press Execute Queue again.")
            return
        # Resolve EVERY group's segments up front from the pre-rollout scan. We
        # must NOT re-walk per group: sequences_for_scope() keys off the timeline
        # playhead/focus, which the first group's overwrite disturbs -- re-walking
        # mid-rollout then returns nothing and every later group is skipped.
        # The scan snapshot holds valid handles for the whole rollout; the
        # pre-trim in _connect_one keeps each placement safe.
        original_seq = _ancestor(_current_segment(), "PySequence")   # before mutating
        inv = self._inv or graphic_inventory(self.scope.currentText())
        # connection sets as they stand BEFORE the rollout (read-only), resolved
        # by the same call the Q rows used: a group that joins an existing set
        # copies FROM that set and never re-copies it; a group with segments
        # gone from the scan, overlapping an earlier group, or touching an
        # identity collision doesn't run.
        _g, cluster_of, size_of, tainted, keys = link_context(inv)
        key_to_idx = {}
        for i, k in enumerate(keys):
            key_to_idx.setdefault(k, i)
        marked = {i for i, k in enumerate(keys) if k in self._sources}
        res = resolve_queue(self._queue, key_to_idx, cluster_of, size_of, marked, tainted)
        affected, total, ran, total_done, msgs = {}, len(self._queue), 0, 0, []
        for gi, (g, r) in enumerate(zip(self._queue, res)):
            plan = r["plan"]
            if r["missing"] or len(r["idxs"]) < 2:
                msgs.append("Group %d skipped (%d/%d segments still in the scan)."
                            % (gi + 1, len(r["idxs"]), len(g)))
                continue
            if not plan["work"]:
                msgs.append("Group %d skipped — already connected." % (gi + 1))
                continue
            if plan["error"]:
                msgs.append("Group %d skipped — %s" % (gi + 1, plan["error"]))
                continue
            if r["overlap"] is not None:
                msgs.append("Group %d skipped — it shares a segment with group %d, which ran "
                            "first. Run Auto Connection again to pick it up."
                            % (gi + 1, r["overlap"] + 1))
                continue
            if plan["master"] is not None:          # joins a set, or re-lay-out
                chosen = inv[plan["master"]]["seg"]
                segs = [chosen] + [inv[i]["seg"] for i in plan["targets"]]
            else:
                segs = [inv[i]["seg"] for i in plan["targets"]]
                chosen, serr = self._group_master(segs)   # honor a marked source
                if serr:
                    msgs.append("Group %d skipped — %s" % (gi + 1, serr))
                    continue
            # collect affected sequences BEFORE connecting -- overwrite makes the
            # destination seg handles stale, so _ancestor would fail for them after.
            for s in segs:
                sq = _ancestor(s, "PySequence")
                if sq is not None:
                    affected.setdefault(id(sq), sq)
            done, master, errors = connect_segment_group(segs, master=chosen)
            ran += 1
            total_done += done
            msgs += ["  group %d (%s): %s" % (gi + 1, nm, e) for nm, e in errors]
            msgs.append("Group %d: connected %d to '%s'."
                        % (gi + 1, done, _clean_name(master) if master else "?"))
        self._queue = []
        self._reset_playheads_and_focus(affected.values(), original_seq)
        msgs.insert(0, "Executed %d/%d queued group(s); %d segment(s) connected."
                    % (ran, total, total_done))
        self._finish_after_ops(msgs, close=True)

    def _clear_queue(self):
        if not self._queue:
            return
        self._queue = []
        self._say("Queue cleared.")
        self._render_connections()

    def _finish_after_ops(self, msgs, close):
        """Log to the panel and the console (so results survive a close), then
        either close (done) or re-scan in place. No auto-reopen -- Flame tears the
        dialog down on timeline mutation, and 'Yes' means done by spec."""
        for m in msgs:
            self._say(m)
        try:
            print("[Type Sync] " + " | ".join(msgs))
        except Exception:
            pass
        if close:
            try:
                self.close()
            except Exception:
                pass
        else:
            self._scan_connections()

    def _reset_playheads_and_focus(self, affected_seqs, original_seq):
        """After a connection rollout: park every affected sequence's playhead at
        the first frame of picture, then re-select the sequence the user started
        on -- so they don't get dumped on the last one processed. Both are
        best-effort and fully guarded.

        Frame 1, not 0: frame 0 sits one frame BEFORE the first frame of picture
        (user-confirmed). PySequence.start_frame exists if exact per-sequence
        starts are ever needed, but frame 1 is the verified first picture frame."""
        moved = 0
        for seq in affected_seqs:
            try:
                seq.current_time = flame.PyTime(1)
                moved += 1
            except Exception:
                pass
        if moved:
            self._say("Parked %d sequence(s) at the first frame." % moved)
        if original_seq is not None:
            _focus_sequence(original_seq)
            self._say("Returned to '%s'." % _clean_name(original_seq))

    def _sync_layout_conn(self):
        sel = self._selected_conn()
        if len(sel) != 1:
            return
        seg = sel[0]["seg"]
        try:
            n = len(seg.connected_segments(scoping="all reels"))
            seg.sync_connected_segments()
            self._say("Synced %s to %d connected segment(s)." % (sel[0]["seq"], n))
        except Exception as e:
            self._say("Sync Connected Segments failed: %s" % e)
        self._scan_connections()

    def _auto_connection(self):
        """One-click: queue a connection group for every like-aspect, like-Type
        set in the current scan. Builds the queue (does not run) so the user
        reviews the Q rows, then presses Execute Queue -- same trusted path as a
        manual Queue, just done for all groups at once. A proposal that wouldn't
        run (a Set as Source mark that would split a set, or overlap with a
        group already queued) is reported instead of queued."""
        inv = self._inv
        if not inv:
            self._say("Auto Connection: nothing scanned — check the Scope.")
            return
        ctx = link_context(inv)
        _g, cluster_of, size_of, tainted, keys = ctx
        groups, already, unassigned, split, unsafe = auto_connection_groups(inv, ctx)
        key_to_idx = {}
        for i, k in enumerate(keys):
            key_to_idx.setdefault(k, i)
        marked = {i for i, k in enumerate(keys) if k in self._sources}
        pending = {frozenset(g) for g in (self._queue or [])}
        trial = list(self._queue or [])
        new_groups, dup, held = [], 0, []
        for g in groups:
            uids = [keys[i] for i in g["idxs"]]
            m = plan_connection_group(g["idxs"], cluster_of, size_of, marked, tainted)["master"]
            if m is not None and m not in g["idxs"]:
                uids = uids + [keys[m]]        # a Set as Source elsewhere in the set
            if frozenset(uids) in pending:
                dup += 1
                continue
            d0 = inv[g["idxs"][0]]
            tag = "%s  Type%s" % (d0["aspect"], d0["num"])
            r = resolve_queue(trial + [uids], key_to_idx, cluster_of, size_of,
                              marked, tainted)[-1]
            if r["plan"]["error"]:
                held.append("%s: not queued — %s" % (tag, r["plan"]["error"]))
                continue
            if r["overlap"] is not None:
                held.append("%s: not queued — part of it is already queued (Q%d). Run or "
                            "clear the queue, then Auto Connection again." % (tag, r["overlap"] + 1))
                continue
            trial.append(uids)
            new_groups.append((g, uids))
        skip_bits = []
        if already:
            skip_bits.append("%d already connected" % already)
        if dup:
            skip_bits.append("%d already queued" % dup)
        if split or unsafe or held:
            skip_bits.append("%d need a look, see below" % (len(split) + len(unsafe) + len(held)))
        if unassigned:
            skip_bits.append("%d unassigned segment(s)" % unassigned)
        skip_note = ("  (skipped: %s)" % ", ".join(skip_bits)) if skip_bits else ""
        if not new_groups:
            self._say("Auto Connection: nothing new to queue%s." % skip_note)
        else:
            # No modal confirm -- it only QUEUES (nothing runs yet), and the full
            # group list could run off-screen. Queue straight away and log a
            # concise, scrollable summary to the panel; the user reviews the Q
            # rows then presses Execute Queue.
            for _g, uids in new_groups:
                self._queue.append(uids)
            self._say("Auto Connection queued %d group(s)%s — review the Q rows, then Execute Queue:"
                      % (len(new_groups), skip_note))
            for g, _u in new_groups:
                d0 = inv[g["idxs"][0]]
                gid = ("Type" + d0["num"]) if d0["num"] else "—"
                if g["anchor"] is not None:
                    self._say("   • %s  %s  (%d new segment(s) join its connected set)"
                              % (d0["aspect"], gid, len(g["idxs"]) - 1))
                else:
                    self._say("   • %s  %s  (%d segment(s))" % (d0["aspect"], gid, len(g["idxs"])))
        # 2+ separate connected sets for one Type in one aspect: which layout
        # should win is the user's call, so these are reported, never queued
        for aspect, num, n_sets, n_loose in split:
            extra = (" + %d unconnected" % n_loose) if n_loose else ""
            self._say("   ⚠ %s  Type%s: %d separate connected sets%s — left alone. "
                      "If they should share one layout, use Multi Segment Connection."
                      % (aspect, num, n_sets, extra))
        for aspect, num in unsafe:
            self._say("   ⚠ %s  Type%s: left alone — two graphics there share a sequence, "
                      "name and In, so they can't be told apart. Give one a segment name in "
                      "Flame, then rescan." % (aspect, num))
        for m in held:
            self._say("   ⚠ " + m)
        self._render_connections()

    # ---------------------------------------------------------------- Timelines tab
    def _build_timelines_tab(self):
        """Where every graphic sits and how it's connected, at a glance: lanes
        of sequences grouped by aspect on one time scale (see GfxTimelineView).
        Read-only for now -- click to inspect a graphic and its connection set,
        double-click (or Jump to Flame Segment) to move Flame's positioner there. The
        lanes | preview divider and the picture | details divider drag either
        way; the Preview / Details toggles (or dragging a pane shut) give the
        room back, and the layout is remembered between opens."""
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        top = QtWidgets.QHBoxLayout()
        self.tl_filter_mode = QtWidgets.QComboBox()
        self.tl_filter_mode.addItem("Show", "show")
        self.tl_filter_mode.addItem("Filter", "filter")
        self.tl_filter_mode.setToolTip(
            "Show: grey out every graphic but the chosen Type, keeping every sequence. "
            "Filter: also leave out the sequences that don't use it.")
        self.tl_filter_mode.currentIndexChanged.connect(self._tl_filter_mode_changed)
        top.addWidget(self.tl_filter_mode)
        self.tl_filter = QtWidgets.QComboBox()
        self.tl_filter.addItem("All", None)
        self.tl_filter.setToolTip("Pick one Type number (the words) to see every place it's "
                                  "used and how it's connected.")
        self.tl_filter.currentIndexChanged.connect(lambda *_: self._tl_apply_filter())
        top.addWidget(self.tl_filter)
        top.addStretch(1)
        legend = QtWidgets.QLabel(
            "Colour = connection set (shared look)  \u00b7  label = Type number (the words)"
            "  \u00b7  letter = look (a connected set shares one; a lone graphic has its own)"
            "  \u00b7  dashed = not connected"
            "  \u00b7  red dashed = can't tell (identity collision)"
            "  \u00b7  amber corner = text OUT OF DATE"
            "  \u00b7  double-click = jump to Flame segment")
        legend.setStyleSheet("color:#777777;")      # as the Connections tab's tips
        legend.setWordWrap(True)
        legend.setMinimumWidth(160)   # wraps rather than widening the window
        self._tip_label(legend)
        top.addWidget(self._tips_button())

        # the preview pane's show / hide toggles live up here, outside the
        # pane they hide
        # (lit = shown; short labels so the legend keeps its room)
        self.b_tl_det = QtWidgets.QPushButton("Details")
        self.b_tl_det.setCheckable(True)
        self.b_tl_det.setChecked(True)
        self.b_tl_det.setToolTip("Show / hide the details under the picture (text, where, "
                                 "look) to give the picture more room.")
        self.b_tl_det.toggled.connect(self._tl_set_details)
        top.addWidget(self.b_tl_det)
        self.b_tl_prev = QtWidgets.QPushButton("Preview")
        self.b_tl_prev.setCheckable(True)
        self.b_tl_prev.setChecked(True)
        self.b_tl_prev.setToolTip("Show / hide the whole preview pane. While it's hidden "
                                  "nothing is rendered.")
        self.b_tl_prev.toggled.connect(self._tl_set_preview)
        top.addWidget(self.b_tl_prev)
        v.addLayout(top)

        # lanes | preview pane, each side draggable to be "the focus"
        split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        split.setHandleWidth(10)
        self.tl_split = split
        lanes = QtWidgets.QWidget()
        lv = QtWidgets.QVBoxLayout(lanes)
        lv.setContentsMargins(0, 0, 0, 0)
        self.tl_view = GfxTimelineView(label_w=load_settings().get("tl_label_w"))
        self.tl_view.label_w_changed.connect(lambda w: self._save_setting("tl_label_w", int(w)))
        self.tl_view.clicked.connect(self._tl_clicked)
        self.tl_view.dclicked.connect(self._tl_jump)
        sc = QtWidgets.QScrollArea()
        sc.setWidgetResizable(True)
        sc.setWidget(self.tl_view)
        lv.addWidget(sc, 1)
        # Jump acts on the picked graphic, so it sits under the lanes and stays
        # when the preview is hidden
        brow = QtWidgets.QHBoxLayout()
        self.b_tl_jump = QtWidgets.QPushButton("Jump to Flame Segment")
        self.b_tl_jump.setToolTip("Open the sequence in Flame's Timeline and park the "
                                  "positioner in the middle of this graphic.")
        self.b_tl_jump.clicked.connect(lambda: self._tl_jump(self._tl_sel))
        brow.addWidget(self.b_tl_jump)
        brow.addStretch(1)
        lv.addLayout(brow)
        split.addWidget(lanes)

        # the preview pane: [controls + picture] over [note + details]
        side = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        side.setHandleWidth(10)
        self.tl_side = side
        pic = QtWidgets.QWidget()
        pv = QtWidgets.QVBoxLayout(pic)
        pv.setContentsMargins(8, 0, 0, 0)
        prow = QtWidgets.QHBoxLayout()
        self.tl_prev_mode = QtWidgets.QComboBox()
        for label, key in (("Full frame", "full"), ("Type only", "graphic")):
            self.tl_prev_mode.addItem(label, key)
        self.tl_prev_mode.setToolTip(
            "Full frame: Flame renders the whole frame, picture and all (quick when the "
            "timeline is rendered). Type only: Flame renders just the Type over black -- "
            "the same exact text, and quick however heavy the picture under it is. Each "
            "look renders once, then it's cached.")
        prow.addWidget(self.tl_prev_mode)
        self.b_tl_rerender = QtWidgets.QPushButton("Re-render")
        self.b_tl_rerender.setToolTip("Render this frame again (e.g. after changing the picture "
                                      "under the graphic).")
        self.b_tl_rerender.clicked.connect(lambda: self._tl_update_preview(self._tl_sel, force=True))
        prow.addWidget(self.b_tl_rerender)
        prow.addStretch(1)
        self.b_tl_text = QtWidgets.QPushButton("Text")
        self.b_tl_text.setToolTip("Frame the graphic's text (where the Type says it sits -- "
                                  "an estimate; each new pick is re-framed).")
        self.b_tl_text.clicked.connect(lambda: self.tl_preview.set_text())
        prow.addWidget(self.b_tl_text)
        self.b_tl_fit = QtWidgets.QPushButton("Fit")
        self.b_tl_fit.setToolTip("Show the whole frame (double-clicking the picture does the same).")
        self.b_tl_fit.clicked.connect(lambda: self.tl_preview.set_fit())
        prow.addWidget(self.b_tl_fit)
        self.tl_zoom = QtWidgets.QComboBox()
        self.tl_zoom.setToolTip("Zoom, in % of the frame's own pixels (100% = 1:1, as in "
                                "Flame's viewer). Drag the picture to pan; double-click = Fit.")
        self.tl_zoom.activated.connect(self._tl_zoom_picked)
        prow.addWidget(self.tl_zoom)
        for b in (self.b_tl_rerender, self.b_tl_text, self.b_tl_fit):
            b.setStyleSheet("padding: 7px 9px;")          # one compact row
        pv.addLayout(prow)
        self.tl_preview = FramePreview()
        self.tl_preview.set_view_states(load_settings().get("tl_zoom_by_size"))
        self.tl_preview.view_changed.connect(self._tl_zoom_ui)
        self.tl_preview.view_changed.connect(
            lambda: self._layout_later(tl_zoom_by_size=self.tl_preview.view_states()))
        pv.addWidget(self.tl_preview, 1)
        side.addWidget(pic)
        det = QtWidgets.QWidget()
        dv = QtWidgets.QVBoxLayout(det)
        dv.setContentsMargins(8, 0, 0, 0)
        self.tl_prev_note = QtWidgets.QLabel("")
        self.tl_prev_note.setWordWrap(True)
        self.tl_prev_note.setStyleSheet("color:#9a9a9a; font-size:11px;")
        dv.addWidget(self.tl_prev_note)
        self.tl_details = QtWidgets.QLabel("Click a graphic to see what it says, where it "
                                           "is, and what it's connected to.")
        self.tl_details.setTextFormat(QtCore.Qt.RichText)
        self.tl_details.setWordWrap(True)
        self.tl_details.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.tl_details.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        dsc = QtWidgets.QScrollArea()                 # long legals must not push
        dsc.setWidgetResizable(True)                  # "Look" out of view
        dsc.setFrameShape(QtWidgets.QFrame.NoFrame)
        dsc.setWidget(self.tl_details)
        dv.addWidget(dsc, 1)
        side.addWidget(det)
        side.setStretchFactor(0, 1)                   # a taller window = a bigger picture
        side.setStretchFactor(1, 0)
        side.setCollapsible(0, False)
        side.setCollapsible(1, True)                  # dragged shut = Details off
        side.splitterMoved.connect(self._tl_side_moved)
        split.addWidget(side)
        # the lanes keep room for their ends (GfxTimelineView lays out at no
        # less than names + 240); the preview has no cap and can be dragged
        # shut (= Preview off: nothing renders)
        lanes.setMinimumWidth(330)
        split.setStretchFactor(0, 3)
        split.setStretchFactor(1, 2)
        split.setCollapsible(0, False)
        split.setCollapsible(1, True)
        split.splitterMoved.connect(self._tl_split_moved)
        self._tl_drag = self._tl_vdrag = None   # sizes when a handle was pressed
        self._tl_held = self._tl_reopen = False
        self._tl_watch = _HandleWatch(self._tl_split_pressed, self._tl_split_released, self)
        split.handle(1).installEventFilter(self._tl_watch)
        self._tl_vwatch = _HandleWatch(self._tl_side_pressed,
                                       lambda: setattr(self, "_tl_vdrag", None), self)
        side.handle(1).installEventFilter(self._tl_vwatch)
        v.addWidget(split, 1)
        v.addWidget(legend)                            # the tips sit at the bottom
        self.b_tl_jump.setEnabled(False)
        self.b_tl_rerender.setEnabled(False)
        self.tl_preview.show_message("Click a graphic to preview it.")
        self._tl_zoom_ui()
        for w_ in (self.tl_prev_mode, self.b_tl_rerender, self.b_tl_text, self.b_tl_fit, self.tl_zoom):
            w_.ensurePolished()                           # measure with the stylesheet applied,
        side.setMinimumWidth(max(260, pic.sizeHint().width()))   # the zoom list filled: no truncation

        # the remembered layout
        st = load_settings()
        sz = splitter_sizes(st.get("tl_split")) or [510, 430]
        split.setSizes(sz)
        self._tl_side_w = sz[1]
        vz = splitter_sizes(st.get("tl_side_split")) or [320, 120]
        side.setSizes(vz)
        self._tl_det_h = vz[1]
        self._tl_prev_on = self._tl_det_on = True
        show_prev = st.get("tl_show_preview", True) is not False
        if st.get("tl_preview") == "off":  # an older "Off" = Preview off now;
            show_prev = False              # written back once, so turning the
            st["tl_preview"], st["tl_show_preview"] = "full", False   # preview on sticks
            save_settings(st)
        k = self.tl_prev_mode.findData(st.get("tl_preview"))   # full / graphic (older: full)
        self.tl_prev_mode.setCurrentIndex(k if k >= 0 else 0)
        self.tl_prev_mode.currentIndexChanged.connect(self._tl_prev_mode_changed)
        if st.get("tl_show_details", True) is False:
            self._tl_set_details(False, save=False)
        if not show_prev:
            self._tl_set_preview(False, save=False)
        return w

    def _save_setting(self, key, value):
        s = load_settings()
        s[key] = value
        save_settings(s)

    # ---- Timelines: preview pane layout (show / hide / sizes, remembered)
    def _tl_set_preview(self, on, save=True):
        """Show / hide the whole preview pane: the Preview toggle or the
        pane dragged shut. Hidden = nothing renders
        and no In/Out marks are touched; showing it previews the pick again."""
        on = bool(on)
        sizes = self.tl_split.sizes()
        total = sum(sizes) if len(sizes) == 2 and sum(sizes) > 0 else 940
        if on:
            w = max(self.tl_side.minimumWidth(), int(self._tl_side_w or 430))
            w = min(w, max(self.tl_side.minimumWidth(), total - 330))
            self.tl_split.setSizes([max(1, total - w), w])
        else:
            if len(sizes) == 2 and sizes[1] > 0 and self.tl_split.isVisible():
                self._tl_side_w = sizes[1]           # (unshown: sizes are placeholders)
            self.tl_split.setSizes([total, 0])
        self._tl_preview_state(on, save)

    def _tl_preview_state(self, on, save=True, preview=True):
        was = self._tl_prev_on
        self._tl_prev_on = on
        self.b_tl_prev.blockSignals(True)
        self.b_tl_prev.setChecked(on)
        self.b_tl_prev.blockSignals(False)
        self.b_tl_det.setEnabled(on)
        if not on:                         # an off-screen pane takes no keys
            fw = QtWidgets.QApplication.focusWidget()
            if fw is not None and self.tl_side.isAncestorOf(fw):
                self.b_tl_prev.setFocus()
        self.tl_side.setEnabled(on)
        if save:
            self._layout_later(tl_show_preview=on)
        if not on:
            self._tl_render_token = None           # a pending render is dropped
            self.b_tl_rerender.setEnabled(False)
        elif not was:
            if preview:
                self._tl_update_preview(self._tl_sel)
            else:
                self.tl_preview.show_message("")   # previews when the drag ends

    def _tl_all_label(self):
        """The GFX list's first entry: Show 'All' (nothing greyed) / Filter
        'None' (nothing left out) -- the same view either way."""
        return "None" if self.tl_filter_mode.currentData() == "filter" else "All"

    def _tl_filter_mode_changed(self, *_):
        self.tl_filter.setItemText(0, self._tl_all_label())
        self._tl_apply_filter()

    def _tl_apply_filter(self):
        self.tl_view.set_filter(self.tl_filter.currentData(),
                                self.tl_filter_mode.currentData() == "filter")

    def _tl_prev_mode_changed(self, *_):
        self._save_setting("tl_preview", self.tl_prev_mode.currentData())
        self._tl_update_preview(self._tl_sel)

    def _tl_zoom_ui(self):
        """The zoom list follows the picture: 'Fit (n%)', the presets, and the
        current zoom when it's none of them (after a pan from Fit, say).
        Amber = zoomed past the render's own pixels (soft)."""
        fp, z = self.tl_preview, self.tl_zoom
        on = fp.has_image()
        cur = round(fp.zoom() * 100)
        z.blockSignals(True)
        z.clear()
        z.addItem("Fit (%d%%)" % round(fp.fit_zoom() * 100), None)
        if on and fp.is_text():
            z.addItem("Text (%d%%)" % cur, "text")
        elif on and not fp.is_fit() and cur not in PREVIEW_ZOOMS:
            z.addItem("%d%%" % cur, fp.zoom())
        for pc in PREVIEW_ZOOMS:
            z.addItem("%d%%" % pc, pc / 100.0)
        if fp.is_fit():
            z.setCurrentIndex(0)
        elif fp.is_text():
            z.setCurrentIndex(1)
        else:
            k = z.findText("%d%%" % cur)
            z.setCurrentIndex(k if k >= 0 else 0)
        z.blockSignals(False)
        soft = on and fp.is_soft()
        z.setStyleSheet("color:#e0b000;" if soft else "")
        z.setToolTip(("Zoomed past the preview render's own pixels, so it looks soft. "
                      if soft else "") + "Zoom, in % of the frame's own pixels (100% = 1:1, "
                     "as in Flame's viewer). Drag the picture to pan; double-click = Fit.")
        z.setEnabled(on)
        self.b_tl_fit.setEnabled(on)
        self.b_tl_text.setEnabled(on and fp.has_text())

    def _tl_zoom_picked(self, i):
        val = self.tl_zoom.itemData(i)
        if val == "text":
            self.tl_preview.set_text()
        elif val is None:
            self.tl_preview.set_fit()
        else:
            self.tl_preview.set_zoom(val)

    def _tl_split_pressed(self):
        self._tl_held = True
        s = self.tl_split.sizes()
        self._tl_drag = list(s) if len(s) == 2 and s[0] > 0 and s[1] > 0 else None

    def _tl_split_released(self):
        self._tl_held, self._tl_drag = False, None
        if self._tl_reopen:
            self._tl_reopen = False
            if self._tl_prev_on:
                self._tl_update_preview(self._tl_sel)

    def _tl_split_moved(self, *_):
        s = self.tl_split.sizes()
        if len(s) != 2:
            return
        if s[1] > 0 and s[0] > 0:
            self._tl_side_w = s[1]
            self._layout_later(tl_split=[int(x) for x in s])
        elif s[1] == 0 and self._tl_drag:        # dragged shut: keep the width it
            self._tl_side_w = self._tl_drag[1]   # had (Qt pins it at its minimum
            self._layout_later(tl_split=[int(x) for x in self._tl_drag])   # first)
        if (s[1] > 0) != self._tl_prev_on:       # dragged shut / back open; a
            self._tl_preview_state(s[1] > 0, preview=not self._tl_held)   # render
            self._tl_reopen = s[1] > 0 and self._tl_held      # waits for release

    def _tl_set_details(self, on, save=True):
        """Show / hide the details under the picture (the Details toggle or
        dragging them shut); hidden, the picture takes the whole pane."""
        on = bool(on)
        sizes = self.tl_side.sizes()
        total = sum(sizes) if len(sizes) == 2 and sum(sizes) > 0 else 490
        if on:
            h = max(60, int(self._tl_det_h or 120))
            h = min(h, max(60, total - 150))
            self.tl_side.setSizes([max(1, total - h), h])
        else:
            if len(sizes) == 2 and sizes[1] > 0 and self.tl_side.isVisible():
                self._tl_det_h = sizes[1]
            self.tl_side.setSizes([total, 0])
        self._tl_details_state(on, save)

    def _tl_details_state(self, on, save=True):
        self._tl_det_on = on
        self.b_tl_det.blockSignals(True)
        self.b_tl_det.setChecked(on)
        self.b_tl_det.blockSignals(False)
        if save:
            self._layout_later(tl_show_details=on)

    def _tl_side_pressed(self):
        s = self.tl_side.sizes()
        self._tl_vdrag = list(s) if len(s) == 2 and s[0] > 0 and s[1] > 0 else None

    def _tl_side_moved(self, *_):
        s = self.tl_side.sizes()
        if len(s) != 2:
            return
        if s[1] > 0 and s[0] > 0:
            self._tl_det_h = s[1]
            self._layout_later(tl_side_split=[int(x) for x in s])
        elif s[1] == 0 and self._tl_vdrag:       # dragged shut: keep its height
            self._tl_det_h = self._tl_vdrag[1]
            self._layout_later(tl_side_split=[int(x) for x in self._tl_vdrag])
        if (s[1] > 0) != self._tl_det_on:
            self._tl_details_state(s[1] > 0)

    def _tl_update_preview(self, idx, force=False):
        """Show the selected graphic's middle frame as Flame renders it -- the
        FULL frame, or the TYPE ONLY (just the Type, over black), per the
        switch -- cached once per distinct look (look_signature, plus the mode),
        so every graphic that looks the same reuses one render. Nothing at all
        while the preview pane is hidden."""
        if not getattr(self, "_tl_prev_on", True):
            self._tl_render_token = None
            self.b_tl_rerender.setEnabled(False)
            return
        self.b_tl_rerender.setEnabled(idx is not None and idx >= 0)
        self._tl_render_token = None
        if idx is None or idx < 0 or idx >= len(self._inv):
            self.tl_preview.show_message("Click a graphic to preview it.")
            self.tl_prev_note.setText("")
            return
        d = self._inv[idx]
        seg = d["seg"]
        tfx = get_type_fx(seg)
        try:
            looks = [_layer_look(layer) for layer in (tfx.layers if tfx else [])]
        except Exception:
            looks = []
        seq = _ancestor(seg, "PySequence")
        try:
            wh = (int(_attr_value(seq.width)), int(_attr_value(seq.height)))
        except Exception:
            wh = (1080, 1920) if d.get("aspect") == "9x16" else (1920, 1080)
        extra = {}
        try:
            extra = {("fx." + k): v for k, v in _layer_look(tfx).items() if k not in _FX_UI_ONLY}
        except Exception:
            pass
        for label, obj in (("segment.hidden", seg), ("track.hidden", _ancestor(seg, "PyTrack"))):
            try:
                extra[label] = _attr_value(getattr(obj, "hidden", None))
            except Exception:
                pass
        mode = self.tl_prev_mode.currentData()
        vkey = look_signature(looks, wh, extra)    # the graphic: switching modes keeps the pan
        long_side = preview_long_side(load_settings().get("tl_preview_size", 0), wh)
        if long_side != 720:
            extra["preview.size"] = long_side      # each size its own cache entry
        if mode == "graphic":
            extra["preview.mode"] = "graphic"       # its own cache entry
        sig = look_signature(looks, wh, extra)
        anchor = text_box(looks, wh[0], wh[1])
        cache = _preview_cache_dir()
        path = os.path.join(cache, sig + ".jpg")
        if force:
            try:
                os.remove(path)
            except OSError:
                pass
        if os.path.exists(path):
            src = self._tl_render_index().get(sig, {}).get("seq", "?")
            self.tl_preview.show_image(path, wh, anchor, vkey)
            self.tl_prev_note.setText(
                ("Type only (cached): Flame's render of just the Type, from '%s'. "
                 if mode == "graphic" else "Real render (cached), from '%s'. ") % src +
                "Every graphic with this exact look shares this one render.")
            return
        self.tl_preview.show_message("Rendering the graphic in Flame\u2026" if mode == "graphic"
                                     else "Rendering the frame in Flame\u2026")
        self.tl_prev_note.setText("")
        token = object()
        self._tl_render_token = token
        QtCore.QTimer.singleShot(30, lambda: self._tl_do_render(token, idx, seg, sig, path, d["seq"],
                                                                wh, anchor, mode, vkey,
                                                                long_side))

    def _tl_render_index(self):
        try:
            with open(os.path.join(_preview_cache_dir(), "index.json")) as f:
                return json.load(f) or {}
        except Exception:
            return {}

    def _tl_do_render(self, token, idx, seg, sig, path, seq_name, wh=None, anchor=None,
                      mode="full", vkey=None, long_side=720):
        if token is not self._tl_render_token or self._tl_sel != idx or not self._tl_prev_on:
            return                          # the user moved on; don't render a stale pick
        self._tl_render_token = None
        try:
            ok, note = (render_graphic_only if mode == "graphic" else render_graphic_frame)(
                seg, path, long_side)
        except Exception as e:                      # never into Flame's event loop
            ok, note = False, "render failed: %s" % e
        if not ok:
            self.tl_preview.show_message("Couldn't render this frame: %s" % note)
            self._say("Preview: %s" % note)
            return
        try:
            idx_all = self._tl_render_index()
            idx_all[sig] = {"seq": seq_name, "mode": mode}
            for gone in prune_preview_cache(_preview_cache_dir()):
                idx_all.pop(gone, None)
            _atomic_write_json(os.path.join(_preview_cache_dir(), "index.json"), idx_all)
        except Exception as e:                      # the render itself is fine
            self._say("Preview: couldn't update the render index (%s)." % e)
        if note:
            self._say("Preview: %s" % note)
        if self._tl_sel == idx:
            self.tl_preview.show_image(path, wh, anchor, vkey or sig)
            self.tl_prev_note.setText(
                ("Type only: Flame's render of just the Type (over black), from '%s', middle "
                 "of the graphic. " if mode == "graphic" else
                 "Real render from '%s', middle of the graphic. ") % seq_name +
                "Every graphic with this exact look will reuse it.")

    def _tab_changed(self, i):
        prev, self._tab_now = getattr(self, "_tab_now", None), i
        if prev == _TAB_INDEX["Settings"] and i != prev:
            self._commit_settings()                   # leaving Settings saves it
        if i == _TAB_INDEX["Settings"]:
            self._settings_refresh()
        if i == _TAB_INDEX["Timelines"] and self._tl_dirty:
            self._render_timelines()

    def _render_timelines(self):
        inv = self._inv
        ctx = self._ctx
        if not ctx or len(ctx[4]) != len(inv):
            ctx = link_context(inv)
        _groups, cluster_of, size_of, tainted, keys = ctx
        pos = [_rel_record_pos(d["seg"]) for d in inv]
        # a position Flame won't give us: fall back to "from the sequence's
        # earliest scanned graphic" (approximate, never wrong in order)
        first = {}
        for d in inv:
            if d.get("in_f") is not None:
                first[d["seq"]] = min(first.get(d["seq"], d["in_f"]), d["in_f"])
        # one letter per look, exactly as the Connections tab assigns them
        letter = group_letters(_groups, size_of)
        gfx_of = {}
        for i, d in enumerate(inv):
            try:
                gfx_of[i] = _key(d["num"]) if d["num"] else ""
            except (TypeError, ValueError):
                gfx_of[i] = ""
        slots = set_colour_slots(cluster_of, size_of, range(len(inv)), gfx_of, len(_SET_COLOURS))
        # a lane is a SEQUENCE (name + reel + reel group): a same-named copy in
        # another reel is its own lane, labelled with its reel
        box = {}
        for i, d in enumerate(inv):
            k = keys[i] if i < len(keys) else None
            box[i] = ((k[0],) + tuple(k[3:])) if (isinstance(k, tuple) and k and k[0] != "uid") else (d["seq"],)
        names = {}
        for i, d in enumerate(inv):
            names.setdefault(d["seq"], set()).add(box[i])
        lane_label = {}
        for i, d in enumerate(inv):
            b = box[i]
            lane_label[b] = ("%s \u00b7 %s" % (d["seq"], " / ".join(str(x) for x in b[1:]))
                             if len(names[d["seq"]]) > 1 and len(b) > 1 else d["seq"])
        blocks, seq_info, info = [], {}, {}
        for i, d in enumerate(inv):
            start = pos[i] if pos[i] is not None else max(0, (d.get("in_f") or 0) - first.get(d["seq"], 0))
            dur = max(1, d.get("dur_f") or 1)
            num = gfx_of[i]
            cid = cluster_of.get(i)
            warn = i in tainted
            slot = None if warn else slots.get(cid)
            tl = str(d.get("text") or "").splitlines()
            state = ("not assigned" if not d["num"] else
                     "in sync" if d["in_sync"] else "text OUT OF DATE")
            tag = " ?" if warn else ((" " + letter[cid]) if cid in letter else "")
            info[i] = {"start": start, "dur": dur, "gfx": num, "label": (num or "\u2014") + tag,
                       "colour": _SET_COLOURS[slot % len(_SET_COLOURS)] if slot is not None else None,
                       "warn": warn,
                       "ood": bool(d["num"]) and not d["in_sync"],
                       "tip": "%s  (%s)\n%s \u00b7 %s%s\n%s" % (
                           lane_label[box[i]], d["aspect"], ("Type" + num) if num else "unassigned",
                           state, ("  \u00b7  look " + letter[cid]) if (cid in letter and not warn) else "",
                           tl[0] if tl else "")}
            seq_info.setdefault(box[i], (d["aspect"], d.get("seq_dur_f") or 0))
            blocks.append({"idx": i, "seq": box[i], "start": start, "dur": dur})
        lanes = timeline_lanes(blocks, seq_info)
        for ln in lanes:
            ln["label"] = lane_label.get(ln["seq"], str(ln["seq"]))
        self._tl_lane_label = {i: lane_label[box[i]] for i in box}
        self._tl_letter = letter
        self.tl_view.set_data(lanes, info)
        # the Type filter lists what this scan holds; keep the current pick
        cur = self.tl_filter.currentData()
        self.tl_filter.blockSignals(True)
        self.tl_filter.clear()
        self.tl_filter.addItem(self._tl_all_label(), None)
        for n in sorted({x["gfx"] for x in info.values() if x["gfx"]}):
            self.tl_filter.addItem("Type" + n, n)
        if any(not x["gfx"] for x in info.values()):
            self.tl_filter.addItem("Unassigned", "")
        k = self.tl_filter.findData(cur)
        self.tl_filter.setCurrentIndex(k if k >= 0 else 0)
        self.tl_filter.blockSignals(False)
        self._tl_apply_filter()
        self._tl_ctx = (cluster_of, size_of, keys)
        self._tl_tainted = tainted
        self._tl_clash = set(identity_collisions(keys))
        self._tl_dirty = False
        # keep the inspected graphic across rescans, by identity -- but never
        # hop to a collision partner that shares its key
        k = self._tl_sel_key
        again = keys.index(k) if (k in keys and k not in identity_collisions(keys)) else -1
        self._tl_clicked(again)

    def _tl_clicked(self, idx):
        if idx is None or idx < 0 or idx >= len(self._inv):
            self._tl_sel = self._tl_sel_key = None
            self.tl_view.set_selection(None, ())
            self.tl_details.setText("Click a graphic to see what it says, where it is, "
                                    "and what it's connected to.")
            self.b_tl_jump.setEnabled(False)
            self._tl_update_preview(None)
            return
        cluster_of, size_of, keys = self._tl_ctx
        d = self._inv[idx]
        c = cluster_of.get(idx)
        warn = idx in getattr(self, "_tl_tainted", ())
        wired = size_of.get(c, 1) > 1 and not warn
        members = [j for j, cc in cluster_of.items() if cc == c] if wired else [idx]
        self._tl_sel, self._tl_sel_key = idx, keys[idx] if idx < len(keys) else None
        self.tl_view.set_selection(idx, members)
        self.b_tl_jump.setEnabled(True)
        esc = html.escape
        num = d["num"]
        if not num:
            state = "<span style='color:#888'>no Type number assigned</span>"
        elif d["in_sync"]:
            state = "<span style='color:#7cc36b'>text in sync</span>"
        else:
            state = "<span style='color:#e0b000'>text OUT OF DATE</span>"
        text = esc(str(d.get("text") or "")).replace("\n", "<br>")
        if warn and idx < len(keys) and keys[idx] in getattr(self, "_tl_clash", ()):
            look = ("<span style='color:#e0605a'>Can't tell.</span> This graphic shares a "
                    "sequence, name and In with another one, so its connections can't be read "
                    "reliably. Give one of them a segment name in Flame, then Rescan.")
        elif warn:
            look = ("<span style='color:#e0605a'>Can't tell.</span> Its connection set includes "
                    "a graphic that can't be told apart from another (same sequence, name and "
                    "In), so this set can't be read reliably. Name that graphic in Flame, then "
                    "Rescan.")
        elif wired:
            outside = size_of.get(c, 1) - len(members)
            look = "Look %s \u2014 connected: %d here%s. They share one layout." % (
                getattr(self, "_tl_letter", {}).get(c, "?"), len(members),
                (" + %d outside this Scope" % outside) if outside else "")
        else:
            look = "Look %s \u2014 not connected; its layout is its own." % (
                getattr(self, "_tl_letter", {}).get(c, "?"))
        same = []
        if num:
            try:
                same = [j for j, x in enumerate(self._inv)
                        if x["num"] and _key(x["num"]) == _key(num)]
            except (TypeError, ValueError):
                same = []
        uses = ""
        if len(same) > 1:
            tset = getattr(self, "_tl_tainted", ())
            sets = {cluster_of.get(j) for j in same
                    if size_of.get(cluster_of.get(j), 1) > 1 and j not in tset}
            loose = sum(1 for j in same if size_of.get(cluster_of.get(j), 1) <= 1 and j not in tset)
            uses = ("<br><br>Type%s is used %d times: %d connected look(s)%s."
                    % (_key(num), len(same), len(sets),
                       (" + %d unconnected" % loose) if loose else ""))
        self.tl_details.setText(
            "<b style='font-size:14px'>%s</b> &nbsp; %s<br><br>"
            "<span style='color:#9a9a9a'>Text</span><br>%s<br><br>"
            "<span style='color:#9a9a9a'>Where</span><br>%s &nbsp;(%s)<br>In %s &nbsp;\u00b7&nbsp; Dur %s"
            "<br><br><span style='color:#9a9a9a'>Look</span><br>%s%s"
            % (("Type" + _key(num)) if num else "Unassigned", state, text or "<i>(empty)</i>",
               esc(str(getattr(self, "_tl_lane_label", {}).get(idx, d["seq"]))),
               esc(str(d["aspect"])), esc(str(d.get("tc_in") or "")),
               esc(str(d.get("tc_dur") or "")), look, uses))
        self._tl_update_preview(idx)

    def _tl_jump(self, idx):
        """Open the graphic's sequence in Flame and park the positioner in the
        middle of it (the CCM recipe: seq.open(), then current_time). Moving
        what Flame has open also moves the Current* scopes -- they follow
        Flame (user decision)."""
        if idx is None or idx < 0 or idx >= len(self._inv):
            return
        d = self._inv[idx]
        seq = _ancestor(d["seg"], "PySequence")
        if seq is None:
            self._say("Jump: no live handle on '%s' \u2014 press Rescan and try again." % d["seq"])
            return
        rel = _rel_record_pos(d["seg"])
        if rel is None:
            rel = self.tl_view._info.get(idx, {}).get("start", 0)
        mid = rel + max(0, (d.get("dur_f") or 0) // 2)
        opened, err = False, None
        for meth in ("open", "open_as_sequence"):
            fn = getattr(seq, meth, None)
            if callable(fn):
                try:
                    fn()
                    opened = True
                    break
                except Exception as e:
                    err = e
        if not opened:
            self._say("Jump: couldn't open '%s' in Flame (%s)." % (d["seq"], err))
            return
        try:
            seq.current_time = flame.PyTime(mid + 1)      # relative, 1-based (verified)
            self._say("Jump: '%s' at the middle of %s (frame %d)."
                      % (d["seq"], ("Type" + _key(d["num"])) if d["num"] else "the graphic", mid + 1))
        except Exception as e:
            self._say("Jump: opened '%s', but Flame wouldn't move the positioner (%s)."
                      % (d["seq"], e))

    # ---------------------------------------------------------------- Settings tab
    def _build_settings_tab(self):
        w = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(w)
        s = load_settings()

        prow = QtWidgets.QHBoxLayout()
        self.set_regdir = QtWidgets.QLineEdit(s.get("registry_dir", ""))
        self.set_regdir.setPlaceholderText(_default_registry_dir() + "   (default)")
        b_browse = QtWidgets.QPushButton("Browse\u2026")
        b_browse.clicked.connect(self._browse_regdir)
        prow.addWidget(self.set_regdir, 1)
        prow.addWidget(b_browse)
        form.addRow("Registry folder:", self._wrap(prow))

        self.set_scope = QtWidgets.QComboBox()
        self.set_scope.addItems(SCOPES)
        self.set_scope.setCurrentText(s.get("scope", "Current Reel"))
        form.addRow("Default scope:", self.set_scope)

        self.set_match = QtWidgets.QComboBox()
        self.set_match.addItems(MATCH_MODES)
        self.set_match.setCurrentText(s.get("match_mode", MATCH_MODES[0]))
        form.addRow("Target segments:", self.set_match)

        self.set_name = QtWidgets.QLineEdit(s.get("name_contains", ""))
        self.set_name.setPlaceholderText("(optional) only segments whose name contains\u2026")
        form.addRow("Segment name filter:", self.set_name)

        self.set_track = QtWidgets.QLineEdit(s.get("track_prefix", ""))
        self.set_track.setPlaceholderText("(optional) only tracks whose name starts with\u2026")
        form.addRow("Track name prefix:", self.set_track)

        self.set_group_default = QtWidgets.QCheckBox("Start the Segments tab with Grouped Text on")
        self.set_group_default.setChecked(bool(s.get("inv_group_default", False)))
        form.addRow("Default Grouped Text:", self.set_group_default)

        self.set_sort = QtWidgets.QComboBox()
        self.set_sort.addItem("(none)", "")
        for key, header, _t, _d, _rz in INV_COLS:
            self.set_sort.addItem(header, key)
        si = self.set_sort.findData(s.get("inv_sort", ""))
        if si >= 0:
            self.set_sort.setCurrentIndex(si)
        self.set_sort.setToolTip("Column the Segments tab sorts by on open (ascending).")
        form.addRow("Default Segments sort:", self.set_sort)

        self.set_prev_size = QtWidgets.QComboBox()
        for label, px in PREVIEW_SIZES:
            self.set_prev_size.addItem(label, px)
        k = self.set_prev_size.findData(s.get("tl_preview_size", 0))
        self.set_prev_size.setCurrentIndex(k if k >= 0 else 0)        # odd values -> Native
        self.set_prev_size.setToolTip(
            "How big the Timelines preview is rendered (its long side; never bigger than the "
            "sequence). Bigger = sharper text when you zoom in, a little more time and disk "
            "per render. Each size is cached separately.")
        form.addRow("Preview size:", self.set_prev_size)

        note = QtWidgets.QLabel(
            "Changes are saved when you leave this tab (or close the window). "
            "Registry is the single source of truth for Type text. Filters limit "
            "what Scan and Sync touch, so the tool won't disturb other gap FX.")
        note.setWordWrap(True)
        note.setStyleSheet("color:#777777;")
        form.addRow("", note)

        tips_box = QtWidgets.QGroupBox("GETTING STARTED")
        tl = QtWidgets.QVBoxLayout(tips_box)
        tips = QtWidgets.QLabel(
            "•  Add to Registry on a segment captures its text — the quickest way "
            "to seed a new entry.\n"
            "•  Turn on Grouped Text (Segments tab) to assign many identical "
            "legals to one Type number in one click.\n"
            "•  Assign only labels a segment. Editing words is the Registry tab. "
            "OUT OF DATE means a segment's text no longer matches its registry "
            "entry: fix it with Sync Selected / Sync All (Segments tab) or Sync "
            "Text → Scope (Registry tab).\n"
            "•  Type Sync doesn't block Flame: work in Flame with it open, and press "
            "Rescan after changing things there.\n"
            "•  Timelines tab: every graphic on its sequence, coloured by connection "
            "set. Click one to see its text and look; double-click to jump there.\n"
            "•  Use a line of  ---  to split one graphic into multiple Type layers.\n"
            "•  Auto Connection (Connections tab) wires every matching aspect at "
            "once — review the queued rows, then Execute Queue.")
        tips.setWordWrap(True)
        tips.setStyleSheet("color:#9a9a9a;")
        tl.addWidget(tips)
        form.addRow("", tips_box)
        self._settings_seen = self._settings_values()   # what's on disk, as shown
        return w

    def _wrap(self, layout):
        c = QtWidgets.QWidget()
        c.setLayout(layout)
        return c

    def _browse_regdir(self):
        start = self.set_regdir.text().strip() or _default_registry_dir()
        d = QtWidgets.QFileDialog.getExistingDirectory(self, "Select registry folder", start)
        if d:
            self.set_regdir.setText(d)

    # ---- Settings save themselves: as you leave the tab, or close the window
    _SETTING_NAMES = {"registry_dir": "registry folder", "scope": "default scope",
                      "match_mode": "target segments", "name_contains": "segment name filter",
                      "track_prefix": "track name prefix", "inv_group_default": "default Grouped Text",
                      "inv_sort": "default sort", "tl_preview_size": "preview size"}

    def _settings_values(self):
        return {"registry_dir": self.set_regdir.text().strip(),
                "scope": self.set_scope.currentText(),
                "match_mode": self.set_match.currentText(),
                "name_contains": self.set_name.text().strip(),
                "track_prefix": self.set_track.text().strip(),
                "inv_group_default": self.set_group_default.isChecked(),
                "inv_sort": self.set_sort.currentData() or "",
                "tl_preview_size": self.set_prev_size.currentData()}

    def _settings_refresh(self):
        """Entering the Settings tab: show what's saved now (the Scope row at
        the top shares the 'scope' setting and may have moved since)."""
        s = load_settings()
        self.set_regdir.setText(s.get("registry_dir", ""))
        self.set_scope.setCurrentText(s.get("scope", "Current Reel"))
        self.set_match.setCurrentText(s.get("match_mode", MATCH_MODES[0]))
        self.set_name.setText(s.get("name_contains", ""))
        self.set_track.setText(s.get("track_prefix", ""))
        self.set_group_default.setChecked(bool(s.get("inv_group_default", False)))
        k = self.set_sort.findData(s.get("inv_sort", ""))
        self.set_sort.setCurrentIndex(k if k >= 0 else 0)
        k = self.set_prev_size.findData(s.get("tl_preview_size", 0))
        self.set_prev_size.setCurrentIndex(k if k >= 0 else 0)
        self._settings_seen = self._settings_values()

    def _commit_settings(self, apply=True):
        """Save only what was changed on the Settings tab (so a stale field
        never overwrites a newer value), then, when `apply`, do what those
        changes need: reload the registry, move the scope, or rescan."""
        seen = getattr(self, "_settings_seen", None)
        if seen is None:
            return
        now = self._settings_values()
        changed = {k: v for k, v in now.items() if seen.get(k) != v}
        self._settings_seen = now
        if not changed:
            return
        s = load_settings()
        s.update(changed)
        save_settings(s)
        self._say("Settings saved: %s." % ", ".join(self._SETTING_NAMES.get(k, k) for k in changed))
        if not apply:
            return
        if "tl_preview_size" in changed:
            self._tl_dirty = True                     # the next Timelines visit re-previews
        if "registry_dir" in changed:
            self._say("Registry: %s" % registry_path())
            self._reload_registry_table()
        if "scope" in changed and self.scope.currentText() != changed["scope"]:
            self.scope.setCurrentText(changed["scope"])          # rescans
        elif set(changed) & {"registry_dir", "match_mode", "name_contains", "track_prefix"}:
            self._scan()


# --------------------------------------------------------------------- hooks

_TAB_INDEX = {"Segments": 0, "Registry": 1, "Connections": 2, "Timelines": 3, "Settings": 4}
_DIALOG = None          # the one live window (a parentless widget needs a ref)


def _open(selection):
    """NON-MODAL, like the sibling tool CCM: show() instead of exec(), so Flame
    stays live -- click into Flame and Type Sync drops behind it; reopen from
    the menu to bring it back. Reopening REBUILDS the window (fresh scan); an
    unexecuted queue and Set as Source marks don't carry over, and the new
    window says so. Because Flame can now change while the window is open,
    there's a Rescan button, and Execute Queue re-reads Flame before it runs."""
    global _DIALOG
    # Bring Flame to the Timeline tab first, so the Current* scopes (which anchor
    # to flame.timeline.current_segment) can see sequences (verified on box).
    try:
        flame.go_to("Timeline")
    except Exception:
        pass
    carry = []
    old = _DIALOG
    if old is not None:
        try:
            nq, ns = len(old._queue or []), len(old._sources or ())
            if nq or ns:
                carry.append("Reopened: the previous window's %d queued group(s) and %d "
                             "Set as Source mark(s) were cleared." % (nq, ns))
        except Exception:
            pass
        try:
            old.close()
        except Exception:
            pass
    dlg = GraphicSyncDialog(selection if selection else [])
    for m in carry:
        dlg._say(m)
    dlg.setWindowFlags(dlg.windowFlags() | QtCore.Qt.Window)
    _DIALOG = dlg
    dlg.show()
    dlg.raise_()
    dlg.activateWindow()


def get_timeline_custom_ui_actions():
    return [{"name": "Type Sync",
             "actions": [{"name": "Type Sync\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]


def get_media_panel_custom_ui_actions():
    return [{"name": "Type Sync",
             "actions": [{"name": "Type Sync\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]


def get_main_menu_custom_ui_actions():
    return [{"name": "Type Sync",
             "actions": [{"name": "Open Manager\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]
