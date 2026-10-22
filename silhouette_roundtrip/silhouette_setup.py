"""
Silhouette companion script for Flame Round-Trip.

Injected into standalone Silhouette via SFX_SCRIPT_IMPORTS + a QTimer deferred call.

Creates a new project + session from the source media, wires:
    SourceNode -> MaskMLNode -> MLMaskTrackerNode -> MLMatteRefineNode -> OutputNode
configures the Output as DWAA OpenEXR alpha-only and saves the .sfx project,
then leaves the UI open for the artist. Does not render automatically.

After each completed render, a post_render hook sends the new frames to Flame
through Logik Backdoor (import_image_to_batch) onto the result reel. Without
Logik Backdoor installed this is skipped and Import Results is used instead.
"""

from __future__ import print_function

import glob
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import traceback

JOB_ENV = 'SILHOUETTE_FLAME_JOB'
DEFAULT_JOB = '/tmp/silhouette_flame_job.json'
SETUP_LOG = '/tmp/silhouette_roundtrip.log'

DEFAULT_RESULT_REEL = 'Elements'

LOGIK_BACKDOOR_CLIENT = '/opt/Autodesk/shared/python/logik_backdoor/logik_backdoor_client.py'

CHANNELS_ALPHA = 0x02

# Silhouette-default OCIO names (fallback when Flame project config is unavailable)
_OCIO_REC709  = 'rec709'
_OCIO_LINEAR  = 'linear'
_OCIO_SRGB    = 'sRGB'
_OCIO_RAW     = 'raw'

# Flame project OCIO display / view names (Syncolor)
_FLAME_OCIO_DISPLAY  = 'Rec.709 video'
_FLAME_OCIO_VIEW     = 'Video (on Linear)'  # scene-linear input
_FLAME_OCIO_VIEW_VID = 'Video (colorimetric)'  # display-referred input

# Runtime flags set in run() once the job JSON is loaded.
_using_flame_ocio = False
_active_display   = 'default'
_active_view      = _OCIO_REC709



def _cs_to_view_name(ocio_cs):
    """Pick the Silhouette View Transform for a given OCIO colorspace.

    Display-referred / video colorspaces use 'Video (colorimetric)'.
    Scene-linear content uses 'Video (on Linear)'.
    """
    cs = (ocio_cs or '').lower()
    # Display-referred / Rec.709 video -> Video (colorimetric)
    if any(k in cs for k in ('rec.1886', 'rec 1886', 'rec.709 video',
                             'rec.709 camera', 'rec.709 - display', 'video',
                             'srgb', 's-rgb', 'display', 'gamma')):
        return _FLAME_OCIO_VIEW_VID  # 'Video (colorimetric)' placeholder
    # Scene-linear -> Video (on Linear)
    return _FLAME_OCIO_VIEW


def _flame_cs_to_ocio(flame_cs):
    """Map a Flame colour_space string to an OCIO colorspace name.

    When Flame's project OCIO config is active (_using_flame_ocio=True) names
    pass through with light normalisation only.
    Otherwise falls back to Silhouette's built-in names.
    """
    import re
    cs_raw = str(flame_cs or '').strip()
    cs = cs_raw.lower()
    if not cs or cs in ('unknown', 'none', ''):
        _log('colour_space unknown/empty')
        return ''

    if _using_flame_ocio:
        # Flame OCIO path: light normalisation only.
        # 'Rec. 709 Video' / 'Rec709 Video' -> 'Rec.709 video'
        # 'Rec.1886 Rec.709 - Display' -> 'Rec.1886 Rec.709'
        if re.search(r'rec\.?1886', cs):
            return 'Rec.1886 Rec.709 - Display'
        if re.search(r'rec\.?\s*709\b', cs):
            if 'camera' in cs:
                return 'Rec.709 camera'
            return 'Rec.709 video'
        if re.search(r'\blinear\b', cs) and 'rec' not in cs and 'rec.709' not in cs:
            return 'Linear'
        if 'acescg' in cs or 'aces cg' in cs:
            return 'ACEScg'
        if 'acescct' in cs:
            return 'ACEScct'
        if 'acescc' in cs:
            return 'ACEScc'
        if 'aces2065' in cs:
            return 'ACES2065-1'
        # Pass through -- assume it exists in Flame's OCIO config.
        return cs_raw

    # ---- Silhouette-default OCIO fallback ----
    if re.search(r'rec\.?\s*709', cs):
        return _OCIO_REC709
    if 'acescg' in cs or 'aces cg' in cs or 'ap1' in cs:
        return _OCIO_LINEAR
    if 'aces2065' in cs or 'ap0' in cs:
        return _OCIO_LINEAR
    if 'acescc' in cs:
        return _OCIO_LINEAR
    if 'scene_linear' in cs or 'scene linear' in cs or cs == 'linear':
        return _OCIO_LINEAR
    if 'srgb' in cs or 's-rgb' in cs:
        return _OCIO_SRGB
    if 'cineon' in cs:
        return 'Cineon'
    if 'slog' in cs or 's-log' in cs:
        return 'SLog'
    if 'alexav3' in cs or 'logc' in cs:
        return 'AlexaV3LogC'
    if 'raw' in cs:
        return _OCIO_RAW
    _log('Unrecognised colour_space %r -- defaulting to rec709' % flame_cs)
    return _OCIO_REC709


def _log(msg):
    line = '==silhouette_roundtrip: %s' % msg
    print(line)
    try:
        sys.stdout.flush()
    except Exception:
        pass
    try:
        with open(SETUP_LOG, 'a') as fh:
            fh.write(line + '\n')
    except Exception:
        pass


# Confirm this module was actually loaded.
_log('silhouette_setup.py loaded (Python %s, __name__=%s)' % (
    sys.version.split()[0], __name__
))


def _find_job_path():
    env_path = os.environ.get(JOB_ENV, '')
    if env_path and os.path.isfile(env_path):
        return env_path
    for arg in sys.argv[1:]:
        candidate = arg.split('=', 1)[-1] if arg.startswith('job') else arg
        candidate = candidate.strip().strip('"').strip("'")
        if candidate.endswith('.json') and os.path.isfile(candidate):
            return candidate
    if os.path.isfile(DEFAULT_JOB):
        return DEFAULT_JOB
    return ''


def _load_job():
    job_path = _find_job_path()
    if not job_path:
        raise RuntimeError(
            'No job JSON found. Set %s env var or pass path via -args.' % JOB_ENV
        )
    _log('Loading job: %s' % job_path)
    with open(job_path, 'r') as handle:
        return json.load(handle)


def _ensure_dir(path):
    if not path:
        return
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def _configure_output(output_node, render_path):
    """Configure the OutputNode for DWAA EXR, alpha only."""
    # Strip .exr extension — Silhouette appends it automatically.
    base = render_path
    if base.lower().endswith('.exr'):
        base = os.path.splitext(base)[0]
    output_node.property('path').value = base
    _log('Output path: %s' % base)

    # Set format to OpenEXR.
    fmt_prop = output_node.property('format')
    if fmt_prop is not None:
        items = list(getattr(fmt_prop, 'items', []) or [])
        for i, name in enumerate(items):
            if 'exr' in str(name).lower():
                fmt_prop.value = i
                _log('Output format: %s (index %s)' % (name, i))
                break

    # Alpha-only.
    ch_prop = output_node.property('channels')
    if ch_prop is not None:
        ch_prop.value = CHANNELS_ALPHA
        _log('Output channels: alpha only')

    # DWAA compression (appears after format is set).
    for prop in output_node.properties.values():
        name = str(getattr(prop, 'name', '')).lower()
        if 'compress' in name:
            items = list(getattr(prop, 'items', []) or [])
            for i, item in enumerate(items):
                if 'dwaa' in str(item).lower():
                    prop.value = i
                    _log('Compression: %s (index %s)' % (item, i))
                    break
            break

    # Turn off premult on alpha-only output.
    try:
        premult = output_node.property('premultiply')
        if premult is not None:
            premult.value = False
    except Exception:
        pass


def build_session(job):
    from fx import (
        Source,
        Node,
        Depth_Float16,
        Project,
        activate,
        showView,
    )
    from tools.session import SessionBuilder
    from tools.sequenceBuilder import SequenceBuilder

    source_path = job['source_path']
    render_path = job['render_path']
    project_path = job['project_path']
    clip_name = job.get('clip_name') or job.get('session_name') or 'FlameShot'

    if not os.path.exists(source_path):
        raise RuntimeError('Source media not found: %s' % source_path)

    _ensure_dir(project_path)
    _ensure_dir(render_path)

    # Resolve the full sequence from the single-frame reference path.
    # SequenceBuilder scans the directory and builds the bracket pattern
    # Silhouette needs, e.g. file.[1001-1200].exr
    seq = SequenceBuilder(str(source_path))
    seq_path = seq.path
    _log('Sequence path: %s  (%s frame(s))' % (seq_path, seq.frames))

    source = Source(seq_path)
    if source is None or getattr(source, 'duration', 0) == 0:
        raise RuntimeError('Silhouette could not import source: %s' % seq_path)
    _log('Loaded source: duration=%s  size=%s' % (
        getattr(source, 'duration', '?'), getattr(source, 'size', '?')
    ))

    # Determine whether Silhouette was launched with Flame's project OCIO config.
    global _using_flame_ocio, _active_display, _active_view
    _ocio_cfg_path = job.get('ocio_config_path', '')
    _ocio_env = os.environ.get('OCIO', '')
    if _ocio_cfg_path and _ocio_env and os.path.isfile(_ocio_cfg_path):
        _using_flame_ocio = True
        _active_display   = _FLAME_OCIO_DISPLAY
        _active_view      = _FLAME_OCIO_VIEW
        _log('Using Flame OCIO template: %s' % _ocio_cfg_path)
    else:
        _using_flame_ocio = False
        _active_display   = 'default'
        _active_view      = _OCIO_REC709
        _log('Using Silhouette default OCIO config')

    # source.colorspace is auto-detected from the file (read-only).
    # For linear EXRs Silhouette correctly reports 'scene_linear'.
    # We still map Flame's colour_space to drive the view transform.
    ocio_cs = _flame_cs_to_ocio(job.get('colour_space', ''))
    _log('Flame colour_space %r -> OCIO %r (source auto-detected as %r)' % (
        job.get('colour_space', ''), ocio_cs, getattr(source, 'colorspace', '?')))

    # Refine view transform based on colorspace type.
    if _using_flame_ocio:
        _active_view = _cs_to_view_name(ocio_cs)
        _log('View Transform -> %r (colorspace=%r)' % (_active_view, ocio_cs))

    # Always create a fresh project — activate() will switch the GUI to it,
    # making the session visible. (Reusing activeProject() via addItem() alone
    # does not update the UI.)
    project = Project()
    _log('Created new project')

    # Add source to project's media pool.
    project.addItem(source)

    # Build session.
    sb = SessionBuilder()
    sb.build(source, depth=Depth_Float16)
    sb.addSource(source)

    try:
        sb.session.label = clip_name
    except Exception:
        pass

    # Add nodes.
    mask_ml = Node('MaskMLNode')
    matte_assist = Node('MLMaskTrackerNode')
    try:
        matte_assist.property('referenceFrames').value = 2
    except Exception as exc:
        _log('Could not set referenceFrames: %s' % exc)

    matte_refine = Node('MLMatteRefineNode')

    output = Node('OutputNode')
    try:
        output.label = 'Output_Alpha'
    except Exception:
        pass

    sb.addNode(mask_ml)
    sb.addNode(matte_assist)
    sb.addNode(matte_refine)
    sb.addNode(output)

    # Wire data ports (carry matte data between ML nodes).
    try:
        mask_ml.port('data').connect(matte_assist.port('data'))
        _log('Wired data: MaskML.data -> MatteAssist.data')
    except Exception as exc:
        _log('data wire MaskML->MatteAssist failed: %s' % exc)
    try:
        matte_assist.port('data_out').connect(matte_refine.port('in_data'))
        _log('Wired data: MatteAssist.data_out -> MatteRefine.in_data')
    except Exception as exc:
        _log('data wire MatteAssist->MatteRefine failed: %s' % exc)

    _configure_output(output, render_path)

    def _apply_display(session):
        try:
            p_disp = session.property('display.display')
            if p_disp is not None:
                p_disp.value = _active_display
        except Exception:
            pass
        try:
            p_view = session.property('display.view')
            if p_view is not None:
                p_view.value = _active_view
                _log('Set display.display=%r  display.view=%r' % (
                    _active_display, _active_view))
        except Exception as exc:
            _log('Could not set display.view: %s' % exc)

    # Apply BEFORE activate so the values are in the session when activated.
    _apply_display(sb.session)

    # Add session to project and activate.
    project.addItem(sb.session)
    activate(project)
    _log('Project activated')

    # Re-assert after activate and trigger viewer refresh.
    _apply_display(sb.session)
    try:
        import fx as _fx
        if hasattr(_fx, 'setActiveSession'):
            _fx.setActiveSession(sb.session)
            _log('Refreshed viewer via setActiveSession')
    except Exception as exc:
        _log('setActiveSession failed: %s' % exc)

    # --- Helper: set OCIO view + input colorspace directly in the GUI ---
    def _set_ocio_gui(view_name=None, input_cs=None):
        if view_name is None:
            view_name = _active_view
        try:
            from PySide6.QtWidgets import QApplication, QComboBox, QPushButton
            import shiboken6
            app = QApplication.instance()
            if not app:
                return
            view_set = {'sRGB', 'rec709', 'None', 'Video', 'Video (on Linear)'}
            for w in app.allWidgets():
                try:
                    if not shiboken6.isValid(w):
                        continue
                    # View Transform combobox
                    if isinstance(w, QComboBox) and w.toolTip() == 'View Transform':
                        items = [w.itemText(i) for i in range(w.count())]
                        if view_name in items:
                            idx = items.index(view_name)
                            w.setCurrentIndex(idx)
                            try:
                                w.activated.emit(idx)
                            except Exception:
                                pass
                            _log('GUI: View Transform -> %r' % view_name)
                    # Fallback: any combobox whose items match the OCIO view set
                    elif isinstance(w, QComboBox):
                        items = [w.itemText(i) for i in range(w.count())]
                        if view_set.issubset(set(items)) and view_name in items:
                            idx = items.index(view_name)
                            w.setCurrentIndex(idx)
                            try:
                                w.activated.emit(idx)
                            except Exception:
                                pass
                            _log('GUI fallback: View Transform -> %r' % view_name)
                    # Input Colorspace button (has attached QMenu)
                    if input_cs and isinstance(w, QPushButton) and w.toolTip() == 'Input Colorspace':
                        menu = w.menu()
                        if menu:
                            def _find_in_menu(m, text):
                                for a in m.actions():
                                    if a.text() == text:
                                        return a
                                    if a.menu():
                                        found = _find_in_menu(a.menu(), text)
                                        if found:
                                            return found
                                return None
                            matched = _find_in_menu(menu, input_cs)
                            if matched:
                                matched.trigger()
                                _log('GUI: Input Colorspace -> %r' % input_cs)

                except Exception:
                    pass
        except Exception as exc:
            _log('GUI OCIO set failed: %s' % exc)

    # Determine input colorspace to apply.
    # Flame OCIO: always set (names map 1:1). Default: skip for scene_linear.
    if _using_flame_ocio:
        _gui_input_cs = ocio_cs if ocio_cs else None
    else:
        _gui_input_cs = ocio_cs if ocio_cs not in (_OCIO_LINEAR, 'scene_linear') else None

    # Try immediately (widgets exist after activate).
    _set_ocio_gui(view_name=_active_view, input_cs=_gui_input_cs)

    # One more reinforcement 1 s later in case the viewer reinitialises.
    try:
        from PySide6.QtCore import QTimer as _QTimer
        def _late_view_fix():
            try:
                import fx as _fx2
                sess2 = _fx2.activeSession()
                if sess2:
                    p2d = sess2.property('display.display')
                    if p2d is not None:
                        p2d.value = _active_display
                    p2v = sess2.property('display.view')
                    if p2v is not None:
                        p2v.value = _active_view
                    if hasattr(_fx2, 'setActiveSession'):
                        _fx2.setActiveSession(sess2)
                _set_ocio_gui(view_name=_active_view, input_cs=_gui_input_cs)
            except Exception:
                pass
        _QTimer.singleShot(1000, _late_view_fix)
        _log('Scheduled late display.view reinforcement (+1 s)')
    except Exception as exc:
        _log('Could not schedule late view fix: %s' % exc)

    # Switch to node-graph workspace.
    try:
        showView('nodeGraph')
        showView('nodes')
    except Exception:
        pass
    try:
        import fx as _fx
        if hasattr(_fx, 'selectWorkspace'):
            _fx.selectWorkspace('Composite')
        elif hasattr(_fx, 'setWorkspace'):
            _fx.setWorkspace('Composite')
    except Exception:
        pass

    # Save project.
    try:
        project.save(project_path)
        _log('Saved project: %s' % project_path)
    except TypeError:
        try:
            project.path = project_path
            project.save()
            _log('Saved project (path property): %s' % project_path)
        except Exception as exc:
            _log('WARNING: project.save() failed: %s' % exc)

    _log('Session "%s" ready. Render from Output_Alpha when ready.' % clip_name)
    return sb.session



def apply_display_only(job):
    """Re-apply View Transform + Input Colorspace to the active session.

    Used when opening an existing .sfx project so the GUI reflects the desired
    OCIO settings immediately.
    """
    import fx as _fx

    # Initialize runtime flags based on Flame's OCIO config.
    global _using_flame_ocio, _active_display, _active_view
    _ocio_cfg_path = job.get('ocio_config_path', '')
    _ocio_env = os.environ.get('OCIO', '')
    if _ocio_cfg_path and _ocio_env and os.path.isfile(_ocio_cfg_path):
        _using_flame_ocio = True
        _active_display   = _FLAME_OCIO_DISPLAY
        _active_view      = _FLAME_OCIO_VIEW
        _log('Using Flame OCIO template: %s' % _ocio_cfg_path)
    else:
        _using_flame_ocio = False
        _active_display   = 'default'
        _active_view      = _OCIO_REC709
        _log('Using Silhouette default OCIO config')

    ocio_cs = _flame_cs_to_ocio(job.get('colour_space', ''))
    _log('Flame colour_space %r -> OCIO %r' % (job.get('colour_space', ''), ocio_cs))

    # Refine view transform based on colorspace type.
    if _using_flame_ocio:
        _active_view = _cs_to_view_name(ocio_cs)
        _log('View Transform -> %r (colorspace=%r)' % (_active_view, ocio_cs))

    # Grab the active session (Silhouette should already have the project loaded).
    sess = None
    try:
        if hasattr(_fx, 'activeSession'):
            sess = _fx.activeSession()
    except Exception:
        sess = None

    if not sess:
        raise RuntimeError('No active Silhouette session found to apply display settings')

    # Apply to session properties.
    try:
        p_disp = sess.property('display.display')
        if p_disp is not None:
            p_disp.value = _active_display
    except Exception:
        pass

    try:
        p_view = sess.property('display.view')
        if p_view is not None:
            p_view.value = _active_view
    except Exception:
        pass

    # --- Helper: set OCIO view + input colorspace in the GUI ---
    def _set_ocio_gui(view_name=None, input_cs=None):
        if view_name is None:
            view_name = _active_view
        try:
            from PySide6.QtWidgets import QApplication, QComboBox, QPushButton
            import shiboken6
            app = QApplication.instance()
            if not app:
                return

            view_set = {'sRGB', 'rec709', 'None', 'Video', 'Video (on Linear)', 'Video (colorimetric)'}

            for w in app.allWidgets():
                try:
                    if not shiboken6.isValid(w):
                        continue

                    # View Transform combobox
                    if isinstance(w, QComboBox) and w.toolTip() == 'View Transform':
                        items = [w.itemText(i) for i in range(w.count())]
                        if view_name in items:
                            idx = items.index(view_name)
                            w.setCurrentIndex(idx)
                            try:
                                w.activated.emit(idx)
                            except Exception:
                                pass
                            _log('GUI: View Transform -> %r' % view_name)

                    # Fallback: any combobox whose items match the View set
                    elif isinstance(w, QComboBox):
                        items = [w.itemText(i) for i in range(w.count())]
                        if view_set.issubset(set(items)) and view_name in items:
                            idx = items.index(view_name)
                            w.setCurrentIndex(idx)
                            try:
                                w.activated.emit(idx)
                            except Exception:
                                pass
                            _log('GUI fallback: View Transform -> %r' % view_name)

                    # Input Colorspace button (attached QMenu)
                    if input_cs and isinstance(w, QPushButton) and w.toolTip() == 'Input Colorspace':
                        menu = w.menu()
                        if menu:
                            def _find_in_menu(m, text):
                                for a in m.actions():
                                    if a.text() == text:
                                        return a
                                    if a.menu():
                                        found = _find_in_menu(a.menu(), text)
                                        if found:
                                            return found
                                return None

                            matched = _find_in_menu(menu, input_cs)
                            if matched:
                                matched.trigger()
                                _log('GUI: Input Colorspace -> %r' % input_cs)

                except Exception:
                    pass
        except Exception as exc:
            _log('GUI OCIO set failed: %s' % exc)

    # Determine input colorspace to apply.
    if _using_flame_ocio:
        _gui_input_cs = ocio_cs if ocio_cs else None
    else:
        _gui_input_cs = ocio_cs if ocio_cs not in (_OCIO_LINEAR, 'scene_linear') else None

    # Force viewer to reflect changes.
    try:
        if hasattr(_fx, 'setActiveSession'):
            _fx.setActiveSession(sess)
    except Exception:
        pass

    _set_ocio_gui(view_name=_active_view, input_cs=_gui_input_cs)

    # Reinforce after 1s in case the viewer reinitializes.
    try:
        from PySide6.QtCore import QTimer as _QTimer
        def _late_view_fix():
            try:
                try:
                    p_disp2 = sess.property('display.display')
                    if p_disp2 is not None:
                        p_disp2.value = _active_display
                except Exception:
                    pass
                try:
                    p_view2 = sess.property('display.view')
                    if p_view2 is not None:
                        p_view2.value = _active_view
                except Exception:
                    pass
                try:
                    if hasattr(_fx, 'setActiveSession'):
                        _fx.setActiveSession(sess)
                except Exception:
                    pass

                _set_ocio_gui(view_name=_active_view, input_cs=_gui_input_cs)
            except Exception:
                pass
        _QTimer.singleShot(1000, _late_view_fix)
    except Exception:
        pass

# ---------------------------------------------------------------------------
# Auto-import renders into Flame via Logik Backdoor
# ---------------------------------------------------------------------------

_SEQ_FRAME_RE = re.compile(r'^(.*?)(\d+)(\.[A-Za-z0-9]+)$')
_IMAGE_EXTENSIONS = ('.exr', '.dpx', '.tif', '.tiff', '.png', '.jpg', '.jpeg')

_render_job = {}
_render_start = [0.0]


def _find_active_renderer():
    """Return the Renderer that called post_render, or None.

    post_render is called without arguments, so walk up the stack to the
    Renderer.render() frame to read its outputs and cancel state.
    """
    try:
        frame = sys._getframe(1)
    except Exception:
        return None
    depth = 0
    while frame is not None and depth < 15:
        obj = frame.f_locals.get('self')
        if obj is not None and hasattr(obj, 'canceled') and hasattr(obj, 'outputs'):
            return obj
        frame = frame.f_back
        depth += 1
    return None


def _render_dirs(renderer):
    dirs = []
    if renderer is not None:
        for output in getattr(renderer, 'outputs', []) or []:
            try:
                path = output.buildPath(0)
            except Exception:
                path = getattr(output, 'path', '')
            directory = os.path.dirname(str(path or ''))
            if directory and directory not in dirs:
                dirs.append(directory)
    if not dirs:
        fallback = os.path.dirname(_render_job.get('render_path', ''))
        if fallback:
            dirs.append(fallback)
    return dirs


def _new_sequences(directory, since):
    """Group frames written since `since` into Flame bracket patterns."""
    groups = {}
    try:
        names = os.listdir(directory)
    except OSError:
        return []
    for name in names:
        if name.startswith('.') or not name.lower().endswith(_IMAGE_EXTENSIONS):
            continue
        full = os.path.join(directory, name)
        try:
            if os.path.getmtime(full) < since:
                continue
        except OSError:
            continue
        match = _SEQ_FRAME_RE.match(name)
        if not match:
            groups.setdefault((name, None, None), [])
            continue
        prefix, digits, ext = match.groups()
        groups.setdefault((prefix, ext, len(digits)), []).append(int(digits))

    patterns = []
    for (prefix, ext, padding), frames in sorted(groups.items()):
        if ext is None:
            patterns.append(os.path.join(directory, prefix))
            continue
        first = str(min(frames)).zfill(padding)
        last = str(max(frames)).zfill(padding)
        if first == last:
            patterns.append(os.path.join(directory, '%s%s%s' % (prefix, first, ext)))
        else:
            patterns.append(os.path.join(directory, '%s[%s-%s]%s' % (prefix, first, last, ext)))
    return patterns


def _find_python():
    """Pick a Python 3.8+ outside Silhouette to run flame_import.py.

    Prefer Flame's bundled Python (newest first), then the system one.
    """
    candidates = sorted(glob.glob('/opt/Autodesk/python/*/bin/python3'), reverse=True)
    candidates += ['/usr/bin/python3', '/usr/local/bin/python3']
    for path in candidates:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            return path
    return ''


def _launch_import(patterns, reel_name):
    """Run flame_import.py as its own process and watch it from the main thread.

    A separate process keeps the import independent of Silhouette: Python
    threads inside Silhouette can stall for minutes, and the process also
    finishes if Silhouette is closed right after the render.
    """
    # Logik Backdoor is optional: without it, renders are brought in with
    # Import Results in Flame, so skip quietly instead of raising a dialog.
    if not os.path.isfile(LOGIK_BACKDOOR_CLIENT):
        _log('Logik Backdoor not installed (%s); skipping auto-import. '
             'Use Import Results in Flame.' % LOGIK_BACKDOOR_CLIENT)
        return

    python = _find_python()
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flame_import.py')
    if not python or not os.path.isfile(script):
        _log('Cannot auto-import: python=%r script=%r' % (python, script))
        _show_import_failure(['No Python found to run %s' % script])
        return

    handle, result_path = tempfile.mkstemp(prefix='sfx_flame_import_', suffix='.json')
    os.close(handle)

    # Isolated mode (-I) ignores Silhouette's PYTHONHOME/PYTHONPATH.
    args = [python, '-I', script, '--reel', reel_name, '--result', result_path] + patterns
    _log('Launching import: %s' % ' '.join(args))
    try:
        log_fh = open(SETUP_LOG, 'a')
        process = subprocess.Popen(
            args,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=log_fh,
            start_new_session=True,
            close_fds=True,
        )
        log_fh.close()
    except Exception as exc:
        _log('Could not launch import process: %s' % exc)
        _show_import_failure(['Could not launch import process: %s' % exc])
        return
    _report_results(process, result_path)


def _report_results(process, result_path):
    """Poll on Silhouette's main thread; show failures once the import process ends."""
    from PySide6.QtCore import QTimer

    if process.poll() is None:
        QTimer.singleShot(500, lambda: _report_results(process, result_path))
        return
    failures = []
    try:
        with open(result_path) as fh:
            failures = json.load(fh).get('failures', [])
    except Exception:
        failures = ['Import process exited with code %s (see %s)' % (process.returncode, SETUP_LOG)]
    try:
        os.remove(result_path)
    except OSError:
        pass
    _log('Import process finished (exit %s)' % process.returncode)
    if failures:
        _show_import_failure(failures)


def _show_import_failure(failures):
    try:
        from fx import displayError
        displayError(
            'Auto-import to Flame failed:\n%s\n\n'
            'Use Silhouette RoundTrip -> Import Results in Flame instead.' % '\n'.join(failures)
        )
    except Exception:
        pass


def _on_pre_render(*args, **kwargs):
    _render_start[0] = time.time()
    _log('pre_render: start %.1f (args=%r)' % (_render_start[0], args))


def _on_post_render(*args, **kwargs):
    # Accept any arguments: Silhouette versions differ in what they pass.
    try:
        _log('post_render: called (args=%r kwargs=%r)' % (args, kwargs))
        renderer = None
        for arg in args:
            if hasattr(arg, 'canceled') and hasattr(arg, 'outputs'):
                renderer = arg
                break
        if renderer is None:
            renderer = _find_active_renderer()
        _log('post_render: renderer=%r canceled=%r' % (
            renderer, getattr(renderer, 'canceled', None)))
        if renderer is not None and getattr(renderer, 'canceled', False):
            _log('post_render: render cancelled, not importing')
            return
        since = _render_start[0] - 1.0 if _render_start[0] else 0.0
        patterns = []
        for directory in _render_dirs(renderer):
            patterns.extend(_new_sequences(directory, since))
        _log('post_render: new sequences %r' % patterns)
        if not patterns:
            _log('post_render: no new frames found, not importing')
            return
        reel_name = _render_job.get('result_reel_name') or DEFAULT_RESULT_REEL
        _launch_import(patterns, reel_name)
    except Exception:
        _log('post_render error:\n%s' % traceback.format_exc())


def _register_render_hooks(job):
    _render_job.clear()
    _render_job.update(job)
    try:
        import hook
        hook.add('pre_render', _on_pre_render)
        hook.add('post_render', _on_post_render)
        _log('Registered post_render auto-import (reel %r)' % (
            job.get('result_reel_name') or DEFAULT_RESULT_REEL))
    except Exception:
        _log('Could not register render hooks:\n%s' % traceback.format_exc())


def run():
    try:
        job = _load_job()
        _register_render_hooks(job)
        _log('source_path : %s' % job.get('source_path'))
        _log('project_path: %s' % job.get('project_path'))
        _log('render_path : %s' % job.get('render_path'))
        if job.get('apply_only', False):
            _log('apply_only=True: applying display settings to active session')
            apply_display_only(job)
        else:
            build_session(job)
    except Exception:
        tb = traceback.format_exc()
        _log('ERROR during setup:\n%s' % tb)
        try:
            with open(SETUP_LOG, 'a') as fh:
                fh.write(tb)
        except Exception:
            pass
        try:
            from fx import displayError
            displayError(
                'Silhouette RoundTrip setup failed.\nSee %s for details.' % SETUP_LOG
            )
        except Exception:
            pass
        raise


if __name__ == '__main__':
    run()
else:
    # Auto-run when imported inside Silhouette (fx importable).
    try:
        import fx  # noqa: F401
    except ImportError:
        pass
    else:
        run()
