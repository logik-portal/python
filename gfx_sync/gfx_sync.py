"""
Script Name: GFX Sync
Script Version: 1.0.0
Flame Version: 2026.1
Written by: Jeff Kyle
Creation Date: 06.10.26
Update Date: 06.23.26
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
        /opt/Autodesk/shared/python/gfx_sync/gfx_sync.py

    Tabs:
        Segments   - scan the scope; see every matching Type segment, its text,
                     assignment and sync status; assign and capture to registry.
        Registry   - add / edit / remove graphic definitions; Sync Text to scope.
        Connections- create / remove segment connections across the timeline gfx gaps.
        Settings   - registry folder, default scope, what counts as a target
                     segment (match mode + name / track filters), Segments-tab
                     defaults (Grouped Text, default sort).


    Built by Jeff Kyle with Claude (Anthropic).

    Provided as-is, without warranty of any kind. Free to use and modify.

Menus:

    Right-click on a timeline segment  ->  GFX Sync  ->  GFX Sync...
    Right-click in the Media Panel     ->  GFX Sync  ->  GFX Sync...
    Flame main menu                    ->  GFX Sync  ->  Open Manager...
"""

import os
import re
import ast
import json
import logging

import flame
from PySide6 import QtWidgets, QtCore, QtGui


log = logging.getLogger("gfx_sync")
if not log.handlers:
    _h = logging.StreamHandler()
    _h.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(_h)
    log.setLevel(logging.INFO)
    log.propagate = False


# ====================================================================
# Settings (per-user) + Registry (per-project, configurable location)
# ====================================================================

SCOPES = ["Selected", "Current Sequence", "Current Reel", "Current Reel Group",
          "All Sequences Reels"]
MATCH_MODES = ["Gap segments with Type", "Any segment with Type"]

SETTINGS_PATH = os.path.join(os.path.expanduser("~"), "flame", "gfx_sync_settings.json")
# Older names, read (never written) so existing installs migrate on the next save.
LEGACY_SETTINGS_PATHS = [
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


def save_settings(settings):
    try:
        _atomic_write_json(SETTINGS_PATH, settings)
    except Exception as e:
        log.warning("settings save failed: %s", e)


def _default_registry_dir():
    try:
        sf = str(flame.projects.current_project.setups_folder).strip("'\"")
        if sf:
            return os.path.join(sf, "gfx_sync")
    except Exception:
        pass
    return os.path.join(os.path.expanduser("~"), "flame", "gfx_sync")


def registry_path():
    d = (load_settings().get("registry_dir") or "").strip() or _default_registry_dir()
    return os.path.join(d, "gfx_registry.json")


def _legacy_registry_candidates():
    """Registry locations from earlier names of this tool, in newest-first order.
    Read only -- never written, never deleted. load_registry() falls back through
    these, and the next save writes to the CURRENT path, so an existing project
    migrates itself while the old file stays on disk as a safety net."""
    d = (load_settings().get("registry_dir") or "").strip() or _default_registry_dir()
    cands = [os.path.join(d, "graphic_registry.json"),      # graphic_sync era
             os.path.join(d, "legal_registry.json")]        # legal_sync era
    try:
        sf = str(flame.projects.current_project.setups_folder).strip("'\"")
        if sf:
            cands.append(os.path.join(sf, "graphic_sync", "graphic_registry.json"))
            cands.append(os.path.join(sf, "legal_sync", "legal_registry.json"))
    except Exception:
        pass
    return cands


def load_registry():
    """{'01': {'lines': [...]}, '02': {...}}  (registry keys are prefix-agnostic).
    Reads the current file, then legacy locations, so existing projects migrate
    on the next save.

    A file that EXISTS but won't parse is quarantined (renamed *.corrupt)
    rather than silently treated as empty -- otherwise the next save would
    clobber the entire registry with a near-empty dict."""
    for p in [registry_path()] + _legacy_registry_candidates():
        try:
            with open(p) as f:
                raw = f.read()
        except FileNotFoundError:
            continue
        except Exception as e:
            log.warning("registry read failed at %s: %s", p, e)
            continue
        try:
            return json.loads(raw)
        except Exception as e:
            quarantine = p + ".corrupt"
            try:
                os.replace(p, quarantine)
                log.warning("registry at %s is corrupt (%s) — moved to %s so a "
                            "save can't overwrite it; starting empty", p, e, quarantine)
            except Exception:
                log.warning("registry at %s is corrupt (%s) and could not be "
                            "quarantined — do NOT save until it's recovered", p, e)
            continue
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
        return (reg, {}, "GFX%s is not in the registry." % ok)
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
    GFX that shrinks must not leave its old last line on screen (the delete-
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
            "⚠ %s: Type has %d layer(s), GFX needs %d — extra layer(s) "
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


def _seg_uid(seg):
    """Cross-call identity. Flame exposes seg.uid (confirmed), which is exact;
    fall back to sequence + name + position only if uid is missing."""
    u = getattr(seg, "uid", None)
    if u:
        return ("uid", str(u))
    parts = [_clean_name(_ancestor(seg, "PySequence")), _clean_name(seg)]
    for attr in ("record_in", "start", "start_frame", "source_in"):
        v = getattr(seg, attr, None)
        if v is not None:
            parts.append(str(v))
            break
    return tuple(parts)


def _safe_delete(obj):
    """Try the known ways to remove a media-panel clip. Returns (ok, error)."""
    try:
        flame.delete(obj)
        return True, None
    except Exception as e1:
        try:
            obj.delete()
            return True, None
        except Exception as e2:
            return False, e2 or e1


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
        if clip is not None:
            _safe_delete(clip)
        return False, str(e)
    _safe_delete(clip)
    placed = _segment_at(dst_track, dst_in)
    if placed is None:
        return False, "placed segment not found at %s" % dst_in
    cur_f = _frames(placed.record_duration)
    if target_f is not None and cur_f is not None:
        delta = cur_f - target_f          # +shrink / -extend (verified)
        if delta:
            try:
                placed.trim_tail(delta, False)   # ripple=False
            except Exception as e:
                return True, "placed but trim failed: %s" % e
    return True, None


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


def connection_groups(inv):
    """Union-find over connected_segments() -> list of groups (each a list of
    inv indices). Multi-member groups (real connections) come first."""
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
    groups = {}
    for i in range(n):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=lambda g: (len(g) == 1, -len(g)))


def auto_connection_groups(inv):
    """Propose connection groups automatically from the (aspect, GFX#) of each
    segment -- the same key a human applies by hand: line up like aspects for
    like graphics. Pure (no Flame calls of its own; reads what graphic_inventory
    already gathered + connection_groups for existing wiring).

    A bucket becomes a proposed group only if it has 2+ members AND they are not
    already all in one existing connection cluster (so re-running is idempotent
    and never re-copies a group that's already wired). Segments with no GFX
    number can't be auto-grouped and are counted as skipped.

    Returns (groups, already_connected, unassigned):
      groups            list of lists of inv indices, ordered by aspect then GFX
      already_connected count of (aspect,GFX#) buckets skipped as already wired
      unassigned        count of segments skipped for having no GFX number
    """
    existing = connection_groups(inv)
    cluster_of = {}
    for cid, g in enumerate(existing):
        for i in g:
            cluster_of[i] = cid
    buckets, unassigned = {}, 0
    for i, d in enumerate(inv):
        if d.get("num") is None:
            unassigned += 1
            continue
        buckets.setdefault((d["aspect"], d["num"]), []).append(i)
    groups, already_connected = [], 0
    for key in sorted(buckets):
        idxs = buckets[key]
        if len(idxs) < 2:
            continue                      # only one occurrence -> nothing to join
        if len({cluster_of.get(i) for i in idxs}) == 1:
            already_connected += 1        # all share one cluster -> already wired
            continue
        groups.append(idxs)
    return groups, already_connected, unassigned


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
    ("gfx",    "GFX",      False, True, "fit"),
    ("status", "Status",   True,  True, "fit"),
    ("conn",   "Conn",     True,  True, "fit"),
)
INV_UNITS = ("Timecode", "Frames")


def inv_row_models(inv, hide_assigned=False, group_text=False):
    """Map the inventory to visible table rows. Each row is a list of indices
    into `inv` (one element normally; several when Grouped Text folds segments
    that share identical Text). Pure -- no Qt, no Flame -- so it's unit-testable.

      hide_assigned  drop rows whose segment already has a GFX number
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
QPlainTextEdit#logbox { color: #00b4d8; font-family: 'Menlo','Consolas',monospace; font-size: 11px; }
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


class GraphicSyncDialog(QtWidgets.QDialog):

    def __init__(self, selection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GFX Sync")
        self.setStyleSheet(STYLE)
        self.resize(860, 820)
        self._inv = []            # one scan, shared by Inventory + Connections
        self._queue = []          # list of uid-lists; each = a pending connection group
        self._longest_seq = None  # reference sequence for grouped In/Dur ordering
        self._sources = set()     # uids marked "Set as Source" for connections
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

        hdr = QtWidgets.QLabel("GFX SYNC")
        hdr.setObjectName("header")
        root.addWidget(hdr)

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
        self.console_btn = QtWidgets.QPushButton("Hide Console")
        self.console_btn.setToolTip("Show / hide the GFX Sync console for more room.")
        self.console_btn.clicked.connect(self._toggle_console)
        srow.addWidget(self.console_btn)
        root.addLayout(srow)

        self.tabs = QtWidgets.QTabWidget()
        self.tabs.addTab(self._build_inventory_tab(), "Segments")
        self.tabs.addTab(self._build_graphics_tab(), "Registry")
        self.tabs.addTab(self._build_connections_tab(), "Connections")
        self.tabs.addTab(self._build_settings_tab(), "Settings")
        root.addWidget(self.tabs, 1)

        self.log = QtWidgets.QPlainTextEdit()
        self.log.setObjectName("logbox")
        self.log.setReadOnly(True)
        self.log.setFixedHeight(150)
        root.addWidget(self.log)

        self._reload_registry_table()
        self._scan()
        self._apply_default_sort()

    # ---------------------------------------------------------------- util
    def _say(self, m):
        self.log.appendPlainText(m)

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

    def _toggle_console(self):
        show = not self.log.isVisible()
        self.log.setVisible(show)
        self.console_btn.setText("Hide Console" if show else "Show Console")

    def _scope_changed(self, text):
        s = load_settings(); s["scope"] = text; save_settings(s)
        self._scan()

    # ---------------------------------------------------------------- Graphics tab
    def _build_graphics_tab(self):
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)

        self.reg_table = QtWidgets.QTableWidget(0, 2)
        self.reg_table.setHorizontalHeaderLabels(["GFX", "Text"])
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

        ed = QtWidgets.QGroupBox("ADD / EDIT GFX")
        el = QtWidgets.QVBoxLayout(ed)
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("GFX #"))
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
            self.reg_table.setItem(r, 0, QtWidgets.QTableWidgetItem("GFX" + k))
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
            self._say("Saved GFX%s (%d layer(s))." % (_key(num), len(lines)))
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
            self._say("Select a GFX in the list to remove.")
            return
        if QtWidgets.QMessageBox.question(
                self, "Remove", "Remove GFX%s from the registry?\n"
                "(Segments keep their tag/text; only the definition is removed.)" % k,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No) != QtWidgets.QMessageBox.Yes:
            return
        registry_remove(int(k))
        self._say("Removed GFX%s." % k)
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
            self._say("Select a saved GFX to renumber.")
            return
        cur = int(k)
        new, ok = QtWidgets.QInputDialog.getInt(
            self, "Renumber GFX%s" % k, "New GFX number:", cur, 1, 99)
        if not ok or new == cur:
            return
        mode = "overwrite"
        if _key(new) in load_registry():
            # target occupied -> Swap (safe, keeps both) / Overwrite (destroys
            # the target) / Cancel. Swap is the default to prevent data loss.
            box = QtWidgets.QMessageBox(self)
            box.setWindowTitle("GFX%s already exists" % _key(new))
            box.setText(
                "GFX%s already exists.\n\n"
                "Swap — exchange GFX%s ↔ GFX%s, both kept (recommended).\n"
                "Overwrite — replace GFX%s with GFX%s; GFX%s's text is lost."
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
        n, err = renumber_graphic(cur, new, self.scope.currentText(), mode)
        if err:
            self._say(err)
            return
        arrow = "↔" if mode == "swap" else "→"
        verb = "Swapped" if mode == "swap" else "Renumbered"
        self._say("%s GFX%s %s GFX%s; re-tagged %d segment(s) in '%s'."
                  % (verb, _key(cur), arrow, _key(new), n, self.scope.currentText()))
        self.reg_spin.setValue(new)
        self._reload_registry_table()
        self._scan()

    def _sync_text(self):
        num = self.reg_spin.value()
        if _key(num) not in load_registry():
            self._say("GFX%s is not saved yet \u2014 Save it first." % _key(num))
            return
        scope = self.scope.currentText()
        prev = sync_text(num, scope, dry_run=True)
        if not prev:
            self._say("GFX%s: nothing to update in '%s' (already in sync or no tagged segments)." % (_key(num), scope))
            return
        seqs = {}
        for seg, li, old, new in prev:
            seqs.setdefault(_clean_name(_ancestor(seg, "PySequence")), 0)
            seqs[_clean_name(_ancestor(seg, "PySequence"))] += 1
        msg = ["Sync TEXT for GFX%s across '%s'?" % (_key(num), scope), "",
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
        self._say("Synced GFX%s text: %d layer(s)." % (_key(num), len(done)))
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
            "Show only segments that still need a GFX assignment.")
        self.inv_hide_assigned.toggled.connect(lambda *_: self._render_inv_table())
        toprow.addWidget(self.inv_hide_assigned)
        self.inv_group_text = QtWidgets.QCheckBox("Grouped Text")
        self.inv_group_text.setToolTip(
            "Fold segments with identical Text into one row; select it to assign "
            "them all to a GFX at once.")
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
            "(sort by In first for appearance order), each to the next free GFX "
            "number, assigning its segments. Only shown with Grouped Text on.")
        self.b_addall.setVisible(False)
        self.b_addall.clicked.connect(self._add_all_to_registry)
        a.addWidget(self.b_addall)
        a.addSpacing(16)
        a.addWidget(QtWidgets.QLabel("Assign to"))
        self.assign_combo = QtWidgets.QComboBox()
        # entries carry a text preview ("GFX01 — Legal line one…"); keep the
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
            return ("GFX" + d["num"]) if d["num"] else "\u2014"
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
                return ("GFX" + only) if only else "—"
            return "mixed"
        if key == "status":
            assigned = sum(1 for d in ds if d["num"] is not None)
            return "%d/%d assigned" % (assigned, n)
        if key == "conn":
            return sum(d["connected"] for d in ds)   # int -> numeric sort
        return ""                    # name / in / dur vary -> blank

    def _render_inv_table(self):
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
        self.inv_table.blockSignals(False)
        self._apply_inv_hidden()

    def _scan(self):
        warns = []
        scope = self.scope.currentText()
        try:
            seqs = sequences_for_scope(scope)
            self._inv = graphic_inventory(scope, warnings=warns, seqs=seqs)
        except Exception as e:
            self._say("Scan error: %s" % e)
            seqs, self._inv = [], []
        for wmsg in warns:
            self._say(wmsg)
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
        self._refresh_assign_combo()
        self._inv_sel_changed()

    def _assign_combo_key(self):
        """The selected GFX key ('01'), read from item DATA -- never parse the
        display text, which now carries a text preview that may contain digits."""
        i = self.assign_combo.currentIndex()
        if i < 0:
            return None
        return self.assign_combo.itemData(i)

    def _refresh_assign_combo(self):
        """Populate the Assign dropdown from the registry, each entry showing a
        first-line preview ('GFX01 — Legal line one…') so the GFX→text mapping
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
            label = "GFX%s" % k
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
                "order, filling the next free GFX numbers, and assign their "
                "segments?\n\n(Order of GFX is based on sorting in the table.)" % len(rows),
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
        rng = ("GFX%s" % _key(first)) if first == last else ("GFX%s–GFX%s" % (_key(first), _key(last)))
        self._say("Add All: created %d entr%s (%s) and assigned %d segment(s)."
                  % (added, "y" if added == 1 else "ies", rng, assigned))
        self._reload_registry_table()
        self._scan()

    def _assign(self):
        sel = self._selected_inv()
        num = self._assign_combo_key()
        if not sel or num is None:
            return
        tag_text = "GFX%s" % num
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
                "This segment is assigned to GFX%s.\n\n"
                "Add as new — create GFX%s (next free slot).\n"
                "Update GFX%s — replace its text with this segment's."
                % (_key(cur_num), _key(free), _key(cur_num)))
            box.setStyleSheet(STYLE)
            new_b = box.addButton("Add as GFX%s" % _key(free), QtWidgets.QMessageBox.AcceptRole)
            upd_b = box.addButton("Update GFX%s" % _key(cur_num), QtWidgets.QMessageBox.ActionRole)
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
            self._say("Added GFX%s from grouped text and assigned %d segment(s) to it "
                      "(%d layer(s))." % (_key(num), assigned, len(lines)))
        else:
            self._say("Added GFX%s to registry from %s (%d layer(s))."
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
        self.conn_sort.addItems(["Connection groups", "GFX", "Aspect", "Sequence"])
        self.conn_sort.currentTextChanged.connect(self._render_connections)
        sortrow.addWidget(self.conn_sort)
        sortrow.addStretch(1)
        v.addLayout(sortrow)

        self.conn_table = QtWidgets.QTableWidget(0, 7)
        self.conn_table.setHorizontalHeaderLabels(
            ["Sequence", "Name", "Aspect", "GFX", "Grp", "Conn", "Text"])
        self.conn_table.verticalHeader().setVisible(False)
        self.conn_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.conn_table.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.conn_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # cols: Sequence Name Aspect GFX Grp Conn Text -- all draggable except
        # Text, which stretches to fill the slack.
        ch = self.conn_table.horizontalHeader()
        _CW = [160, 150, 60, 60, 50, 55]   # Sequence, Name, Aspect, GFX, Grp, Conn
        for c in range(6):
            ch.setSectionResizeMode(c, QtWidgets.QHeaderView.Interactive)
            self.conn_table.setColumnWidth(c, _CW[c])
        ch.setSectionResizeMode(6, QtWidgets.QHeaderView.Stretch)
        ch.setStyle(self._grip_style)   # wider grab zone
        self.conn_table.itemSelectionChanged.connect(self._conn_sel_changed)
        v.addWidget(self.conn_table, 1)

        legend = QtWidgets.QLabel(
            "Rows packed together with no gap are connected to each other; a blank "
            "row separates one group from the next. Unconnected segments sit alone. "
            "Break removes a connection. Auto Connection queues a group for every "
            "like-aspect, like-GFX set across the scope automatically (already-"
            "connected groups skipped) \u2014 review the Q rows, then Execute Queue. "
            "Multi Segment Connection does the same for a hand-picked set: select the "
            "same-aspect rows (the same graphic) and connect them \u2014 each keeps its "
            "own position and duration. In the confirm box: Yes runs now and closes, "
            "Queue stacks the group (shown italic/amber with a Q tag) to run later, No "
            "cancels. Execute Queue runs everything stacked. Set as Source marks a "
            "segment (★ gold) as its group's master, so ITS layout is the one that "
            "propagates; one per group (two ★ in a group refuses), none = auto-pick.")
        legend.setWordWrap(True)
        legend.setStyleSheet("color:#777777;")
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
            "Queue a connection group for every set of like-aspect, like-GFX "
            "segments across the scope automatically. Already-connected groups "
            "are skipped. Review the queued rows, then Execute Queue.")
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
        groups = connection_groups(inv) if inv else []
        clusters = [g for g in groups if len(g) > 1]
        singles_idx = [g[0] for g in groups if len(g) == 1]
        label_of = {}
        for k, g in enumerate(clusters):
            lab = _grp_label(k)
            for ii in g:
                label_of[ii] = lab
        cluster_member = set(label_of.keys())

        # resolve the queue (uid-lists) against the current scan, dropping any
        # member already in a real cluster and any group that no longer has 2+.
        uid_to_idx = {}
        for i, d in enumerate(inv):
            uid_to_idx.setdefault(_seg_uid(d["seg"]), i)
        queue_groups, qlabel_of, queued, kept = [], {}, set(), []
        for g in (self._queue or []):
            idxs = [uid_to_idx[u] for u in g if u in uid_to_idx and uid_to_idx[u] not in cluster_member]
            if len(idxs) >= 2:
                qi = len(queue_groups)
                queue_groups.append(idxs)
                for i in idxs:
                    qlabel_of[i] = "Q%d" % (qi + 1)
                    queued.add(i)
                kept.append(g)
        if len(kept) != len(self._queue):
            self._queue = kept

        self.conn_label.setText(
            "%d connected cluster(s), %d unconnected, %d queued group(s) in '%s'"
            % (len(clusters), len(singles_idx), len(queue_groups), self.scope.currentText()))

        mode = self.conn_sort.currentText() if hasattr(self, "conn_sort") else "Connection groups"
        rows = []
        if mode == "Connection groups":
            blocks = [("cluster", g) for g in clusters]
            blocks += [("queue", g) for g in queue_groups]
            placed = cluster_member | queued
            blocks += [("single", [i]) for i in range(len(inv)) if i not in placed]
            for bi, (_btype, g) in enumerate(blocks):
                for ii in g:
                    rows.append(("seg", ii))
                if bi != len(blocks) - 1:
                    rows.append(("spacer", None))
        else:
            def key(ii):
                d = inv[ii]
                if mode == "GFX":
                    return (d["num"] or "~~", d["seq"])
                if mode == "Aspect":
                    return (d["aspect"], d["seq"])
                return (d["seq"],)
            for ii in sorted(range(len(inv)), key=key):
                rows.append(("seg", ii))

        amber = QtGui.QColor("#d9a441")
        cyan = QtGui.QColor("#00b4d8")
        gold = QtGui.QColor("#ffcc33")
        self.conn_table.blockSignals(True)
        self.conn_table.setRowCount(len(rows))
        for r, (kind, ii) in enumerate(rows):
            if kind == "spacer":
                for c in range(7):
                    cell = QtWidgets.QTableWidgetItem("")
                    cell.setFlags(QtCore.Qt.NoItemFlags)
                    cell.setBackground(QtGui.QColor("#0d0d0d"))
                    self.conn_table.setItem(r, c, cell)
                self.conn_table.setRowHeight(r, 7)
                continue
            d = inv[ii]
            gid = ("GFX" + d["num"]) if d["num"] else "\u2014"
            is_q = ii in queued
            grp = qlabel_of.get(ii, "") if is_q else label_of.get(ii, "")
            is_src = _seg_uid(d["seg"]) in self._sources
            tl = str(d["text"]).splitlines()
            txt = tl[0] if tl else ""
            seq_label = ("★ " + str(d["seq"])) if is_src else d["seq"]
            vals = [seq_label, d.get("name", ""), d["aspect"], gid, grp,
                    str(d["connected"]), txt]
            for c, val in enumerate(vals):
                cell = QtWidgets.QTableWidgetItem(str(val))
                if c == 0:
                    cell.setData(QtCore.Qt.UserRole, ii)
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
                return None, ("That segment has no GFX number, so I can't find its "
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
                return None, "None of the chosen sequences contain GFX%s." % num
            note = ("No GFX%s in: %s (skipped)." % (num, ", ".join(missing))) if missing else None
            return segs, note
        # 2+ rows selected -> that IS the group
        aspects = sorted({d["aspect"] for d in sel})
        if len(aspects) > 1:
            return None, ("Mixed aspects (%s). Connect within one aspect at a time \u2014 "
                          "positions differ across aspects." % ", ".join(aspects))
        nums = sorted({d["num"] for d in sel if d["num"]})
        note = None
        if len(nums) > 1:
            note = ("Heads up: selection spans GFX %s \u2014 connecting unifies them to the "
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
        chosen, serr = self._group_master(segs)        # honor a marked source
        if serr:
            self._say(serr)
            return
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
            self._queue.append([_seg_uid(s) for s in segs])
            self._say("Queued group %d (%d segments). Press Execute Queue when ready."
                      % (len(self._queue), len(segs)))
            self._render_connections()
            return
        # yes -> run now, then close (per spec: we're done)
        original_seq = _ancestor(_current_segment(), "PySequence")   # before mutating
        # collect affected sequences BEFORE connecting -- overwrite makes the
        # destination seg handles stale, so _ancestor would fail for them after.
        affected = {}
        for s in segs:
            sq = _ancestor(s, "PySequence")
            if sq is not None:
                affected.setdefault(id(sq), sq)
        done, master, errors = connect_segment_group(segs, master=chosen)
        self._reset_playheads_and_focus(affected.values(), original_seq)
        msgs = ["Connect issue (%s): %s" % (nm, e) for nm, e in errors]
        msgs.append("Connected %d segment(s) to master '%s'."
                    % (done, _clean_name(master) if master else "?"))
        self._finish_after_ops(msgs, close=True)

    def _execute_queue(self):
        if not self._queue:
            return
        # Resolve EVERY group's segments up front from the pre-rollout scan. We
        # must NOT re-walk per group: sequences_for_scope() keys off the timeline
        # playhead/focus, which the first group's overwrite disturbs -- re-walking
        # mid-rollout then returns nothing and every later group is skipped.
        # The scan snapshot holds valid handles for the whole rollout; the uid
        # guard + pre-trim in _connect_one keep each placement safe.
        original_seq = _ancestor(_current_segment(), "PySequence")   # before mutating
        inv = self._inv or graphic_inventory(self.scope.currentText())
        uid_to_seg = {}
        for d in inv:
            uid_to_seg.setdefault(_seg_uid(d["seg"]), d["seg"])
        affected, total, ran, total_done, msgs = {}, len(self._queue), 0, 0, []
        for gi, g in enumerate(self._queue):
            segs = [uid_to_seg[u] for u in g if u in uid_to_seg]
            if len(segs) < 2:
                msgs.append("Group %d skipped (%d/%d segments resolved)."
                            % (gi + 1, len(segs), len(g)))
                continue
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
            print("[GFX Sync] " + " | ".join(msgs))
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
        """One-click: queue a connection group for every like-aspect, like-GFX
        set in the current scan. Builds the queue (does not run) so the user
        reviews the Q rows, then presses Execute Queue -- same trusted path as a
        manual Queue, just done for all groups at once."""
        inv = self._inv
        if not inv:
            self._say("Auto Connection: nothing scanned — check the Scope.")
            return
        groups, already, unassigned = auto_connection_groups(inv)
        # don't re-queue a group whose exact membership is already pending
        pending = {frozenset(g) for g in (self._queue or [])}
        new_groups, dup = [], 0
        for g in groups:
            uids = [_seg_uid(inv[i]["seg"]) for i in g]
            if frozenset(uids) in pending:
                dup += 1
                continue
            new_groups.append((g, uids))
        skip_bits = []
        if already:
            skip_bits.append("%d already connected" % already)
        if dup:
            skip_bits.append("%d already queued" % dup)
        if unassigned:
            skip_bits.append("%d unassigned segment(s)" % unassigned)
        skip_note = ("  (skipped: %s)" % ", ".join(skip_bits)) if skip_bits else ""
        if not new_groups:
            self._say("Auto Connection: nothing new to queue%s." % skip_note)
            return
        # No modal confirm -- it only QUEUES (nothing runs yet), and the full
        # group list could run off-screen. Queue straight away and log a concise,
        # scrollable summary to the panel; the user reviews the Q rows then
        # presses Execute Queue.
        for _g, uids in new_groups:
            self._queue.append(uids)
        self._say("Auto Connection queued %d group(s)%s \u2014 review the Q rows, then Execute Queue:"
                  % (len(new_groups), skip_note))
        for g, _u in new_groups:
            d0 = inv[g[0]]
            gid = ("GFX" + d0["num"]) if d0["num"] else "\u2014"
            self._say("   \u2022 %s  %s  (%d segment(s))" % (d0["aspect"], gid, len(g)))
        self._render_connections()

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
        form.addRow("Treat as GFX:", self.set_match)

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

        b_save = QtWidgets.QPushButton("Save Settings")
        b_save.setObjectName("primary")
        b_save.clicked.connect(self._save_settings)
        form.addRow("", b_save)

        note = QtWidgets.QLabel(
            "Registry is the single source of truth for GFX text. Filters limit "
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
            "legals to a GFX in one click.\n"
            "•  Assign only labels a segment. Editing words is the Registry tab; "
            "Sync Text → Scope pushes them out. OUT OF DATE means a segment's "
            "text no longer matches its registry entry.\n"
            "•  Use a line of  ---  to split one graphic into multiple Type layers.\n"
            "•  Auto Connection (Connections tab) wires every matching aspect at "
            "once — review the queued rows, then Execute Queue.")
        tips.setWordWrap(True)
        tips.setStyleSheet("color:#9a9a9a;")
        tl.addWidget(tips)
        form.addRow("", tips_box)
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

    def _save_settings(self):
        s = load_settings()
        s["registry_dir"] = self.set_regdir.text().strip()
        s["scope"] = self.set_scope.currentText()
        s["match_mode"] = self.set_match.currentText()
        s["name_contains"] = self.set_name.text().strip()
        s["track_prefix"] = self.set_track.text().strip()
        s["inv_group_default"] = self.set_group_default.isChecked()
        s["inv_sort"] = self.set_sort.currentData() or ""
        save_settings(s)
        if self.scope.currentText() != s["scope"]:
            self.scope.setCurrentText(s["scope"])
        self._say("Settings saved. Registry: %s" % registry_path())
        self._reload_registry_table()
        self._scan()


# --------------------------------------------------------------------- hooks

_PENDING_LOG = []
_PENDING_TAB = None
_TAB_INDEX = {"Segments": 0, "Registry": 1, "Connections": 2, "Settings": 3}


def _open(selection):
    global _PENDING_LOG, _PENDING_TAB
    # Bring Flame to the Timeline tab first, so the Current* scopes (which anchor
    # to flame.timeline.current_segment) can see sequences. UNVERIFIED API name --
    # fully guarded, no-ops if flame.go_to isn't there or wants a different name.
    try:
        flame.go_to("Timeline")
    except Exception:
        pass
    dlg = GraphicSyncDialog(selection if selection else [])
    pend_tab, pend_log = _PENDING_TAB, _PENDING_LOG
    _PENDING_TAB, _PENDING_LOG = None, []
    if pend_tab and pend_tab in _TAB_INDEX:
        dlg.tabs.setCurrentIndex(_TAB_INDEX[pend_tab])
    for m in pend_log:
        dlg._say(m)
    dlg.exec()


def get_timeline_custom_ui_actions():
    return [{"name": "GFX Sync",
             "actions": [{"name": "GFX Sync\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]


def get_media_panel_custom_ui_actions():
    return [{"name": "GFX Sync",
             "actions": [{"name": "GFX Sync\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]


def get_main_menu_custom_ui_actions():
    return [{"name": "GFX Sync",
             "actions": [{"name": "Open Manager\u2026", "execute": _open,
                          "minimumVersion": "2026.1.0"}]}]
