"""
Script Name: silhouette_roundtrip
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng and Cursor
Creation Date: 09.03.26

Custom Action Type: Batch / MediaHub Files / Main Menu

Description:
- Open a selected Batch clip or MediaHub file in standalone Silhouette.
- Uses the original disk path when one exists; otherwise exports the clip
  with the Setup export preset into the shot folder /source.
- Silhouette imports the media, creates a session, and builds
  Mask ML -> Matte Assist ML -> Matte Refine ML -> Output (DWAA EXR, alpha).
- Import the rendered matte sequence back into the current Batch reel.

Menus:
Right-click Clip Node in Batch -> Silhouette RoundTrip... -> Open in Silhouette
Right-click Clip Node in Batch -> Silhouette RoundTrip... -> Import Results
Right-click Clip Node in Batch -> Silhouette RoundTrip... -> Setup
Right-click file in MediaHub -> Silhouette RoundTrip... -> (same)
Flame Main Menu -> Silhouette RoundTrip Setup
"""

# Imports
import datetime
import json
import os
import platform
import re
import shutil
import string
import subprocess
import sys
import time
import traceback

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_PATH not in sys.path:
    sys.path.insert(0, SCRIPT_PATH)

import flame

from silhouette_roundtrip_ui import prompt_for_result_import, show_setup_window, prompt_existing_project

CONFIG_PATH = os.path.join(SCRIPT_PATH, 'config', 'silhouette_config.json')
SETUP_SCRIPT = os.path.join(SCRIPT_PATH, 'silhouette_setup.py')
JOB_ENV = 'SILHOUETTE_FLAME_JOB'
DEFAULT_JOB = '/tmp/silhouette_flame_job.json'

SILHOUETTE_APP_CANDIDATES = [
    '/Applications/BorisFX/Silhouette 2026/Silhouette.app',
    '/Applications/BorisFX/Silhouette 2025/Silhouette.app',
    '/Applications/BorisFX/Silhouette 2024.5/Silhouette.app',
]

BUNDLED_EXPORT_PRESET = os.path.join(
    SCRIPT_PATH, 'presets', 'OpenEXR_16-bit_fp_DWAA.xml'
)

DEFAULT_CONFIG = {
    'silhouette_app': '/opt/BorisFX/Silhouette-2026/silhouette',
    'export_preset_path': BUNDLED_EXPORT_PRESET,
    'project_path_template': (
        '/Volumes/vfx/UC_Jobs/{project_name}/SHOTS/{batch_name}'
        '/2D/Roto/Silhouette/{clip_name}_ml_matte_v01'
    ),
    'render_path_template': (
        '/Volumes/vfx/UC_Jobs/{project_name}/SHOTS/{batch_name}'
        '/2D/Roto/Silhouette/{clip_name}/render/{clip_name}_ml_matte_v01'
    ),
    'result_reel_name': 'Elements',
    'file_wait_timeout': 120,
    'path_history': [],
}

IMAGE_EXTENSIONS = (
    '.exr', '.dpx', '.tif', '.tiff', '.png', '.jpg', '.jpeg',
    '.cin', '.sgi', '.rgb', '.tga', '.hdr', '.bmp',
)

_import_dialog_ref = None
_setup_window_ref = None


def log(msg):
    print(f'==silhouette_roundtrip: {msg}')


def _default_silhouette_app():
    for path in SILHOUETTE_APP_CANDIDATES:
        if os.path.exists(path):
            return path
    return DEFAULT_CONFIG['silhouette_app']


def load_config():
    config_dir = os.path.dirname(CONFIG_PATH)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)

    defaults = DEFAULT_CONFIG.copy()
    defaults['silhouette_app'] = _default_silhouette_app()
    if os.path.exists(BUNDLED_EXPORT_PRESET):
        defaults['export_preset_path'] = BUNDLED_EXPORT_PRESET

    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as handle:
                config = json.load(handle)
            for key, value in defaults.items():
                if key not in config:
                    config[key] = value
            log(f'Configuration loaded from: {CONFIG_PATH}')
            return config
        except Exception as exc:
            log(f'Error loading config: {exc}')
            return defaults
    save_config(defaults)
    return defaults


def save_config(config):
    try:
        config_dir = os.path.dirname(CONFIG_PATH)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        with open(CONFIG_PATH, 'w') as handle:
            json.dump(config, handle, indent=4)
        log(f'Configuration saved to: {CONFIG_PATH}')
        return True
    except Exception as exc:
        log(f'Error saving config: {exc}')
        return False


def sanitize_filename(name):
    return re.sub(r'[<>:"/\\|?*]', '_', str(name or ''))


def _strip_quotes(value):
    text = str(value) if value is not None else ''
    if len(text) >= 2 and text[0] == text[-1] and text[0] in ("'", '"'):
        return text[1:-1]
    return text


def _attr_value(value):
    if value is None:
        return ''
    if hasattr(value, 'get_value'):
        try:
            return value.get_value()
        except Exception:
            pass
    return value


def get_current_project_info():
    try:
        current_project = flame.project.current_project
        project_name_raw = current_project.name
        nickname_raw = current_project.nickname
        log(f"Project Name='{project_name_raw}', Nickname='{nickname_raw}'")
        return project_name_raw, nickname_raw
    except Exception as exc:
        log(f'Warning: Could not get project info: {exc}')
        return 'Unknown_Project', 'No_Nickname'


def get_flame_ocio_config_path():
    """Return the per-project Flame OCIO config path, or empty string if not found."""
    try:
        proj = flame.project.current_project
        project_folder = str(proj.project_folder).strip("'\"")
        path = os.path.join(project_folder, 'setups', 'colour_mgmt', 'config.ocio')
        if os.path.isfile(path):
            log(f'Flame OCIO config: {path}')
            return path
        log(f'Flame project OCIO config not found at: {path}')
    except Exception as exc:
        log(f'Could not get Flame OCIO config path: {exc}')
    return ''




def _get_shot_name_from_clip(clip):
    try:
        for version in clip.versions:
            for track in version.tracks:
                for segment in track.segments:
                    if hasattr(segment, 'shot_name'):
                        shot_name = _attr_value(segment.shot_name)
                        if shot_name and str(shot_name).strip():
                            return str(shot_name).strip()
    except Exception as exc:
        log(f'Note: Could not extract shot_name from clip: {exc}')
    return ''


def resolve_path_template(template, clip=None, clip_name='', batch_name=''):
    project_name_raw, nickname_raw = get_current_project_info()
    now = datetime.datetime.now()

    try:
        batch_group_name = flame.batch.name.get_value() if batch_name == '' else batch_name
    except Exception:
        batch_group_name = batch_name or 'batch'

    try:
        batch_iter = str(flame.batch.batch_iteration)
    except Exception:
        batch_iter = '1'

    shot_name = ''
    if clip is not None:
        shot_name = _get_shot_name_from_clip(clip)

    token_map = {
        'project_name': project_name_raw,
        'nickname': nickname_raw,
        'project_name_raw': project_name_raw,
        'nickname_raw': nickname_raw,
        'clip_name': sanitize_filename(clip_name),
        'shot_name': sanitize_filename(shot_name) if shot_name else sanitize_filename(clip_name),
        'batch_name': sanitize_filename(batch_group_name),
        'batch_iteration': batch_iter,
        'user_name': os.environ.get('USER', 'unknown'),
        'date_YYYY': now.strftime('%Y'),
        'date_MM': now.strftime('%m'),
        'date_DD': now.strftime('%d'),
        'date_YYYY_MM_DD': now.strftime('%Y-%m-%d'),
        'timestamp': str(int(now.timestamp())),
    }

    try:
        return template.format(**token_map)
    except KeyError as exc:
        log(f'Warning: Unknown token in template: {exc}')
        result = template
        formatter = string.Formatter()
        for _, field_name, _, _ in formatter.parse(template):
            if field_name and field_name in token_map:
                result = result.replace(f'{{{field_name}}}', token_map[field_name])
        return result


def get_exportable_clip(item):
    """Return a PyClip/PySequence suitable for flame.PyExporter."""
    clip = get_clip_from_item(item)
    if isinstance(clip, (flame.PyClip, flame.PySequence)):
        return clip
    return None


def wait_for_sequence(sequence_dir, timeout=120):
    log(f'Verifying exported files in: {sequence_dir}')
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(sequence_dir):
            image_files = sorted([
                name for name in os.listdir(sequence_dir)
                if name.lower().endswith(IMAGE_EXTENSIONS) and not name.startswith('.')
            ])
            if image_files:
                first_frame_path = os.path.join(sequence_dir, image_files[0])
                if os.path.getsize(first_frame_path) > 0:
                    log(f'First frame verified: {image_files[0]}')
                    time.sleep(0.5)
                    return first_frame_path
        time.sleep(0.5)
    log(f'Timeout: no image frames in {timeout}s in {sequence_dir}')
    return None


def export_clip_for_silhouette(item, job, config):
    """Export a Flame-only clip to the shot source folder and return the first frame path."""
    clip = get_exportable_clip(item)
    if clip is None:
        _show_error(
            'This clip has no file on disk and cannot be exported. '
            'Select a Batch clip node that Flame can export.'
        )
        return ''

    preset_path = config.get('export_preset_path', '') or BUNDLED_EXPORT_PRESET
    if not os.path.isfile(preset_path):
        _show_error(
            'Export preset not found. Open Setup and choose a Flame export preset (.xml).\n'
            f'Current: {preset_path}'
        )
        return ''

    sequence_dir = os.path.join(job['project_dir'], 'source')
    log(f'No disk path. Exporting clip to: {sequence_dir}')
    log(f'Using preset: {preset_path}')
    try:
        os.makedirs(sequence_dir, exist_ok=True)
        exporter = flame.PyExporter()
        exporter.foreground = True
        exporter.export(clip, preset_path, sequence_dir)
        log('Export finished (foreground mode)')
    except Exception as exc:
        _show_error(f'Flame export failed:\n{exc}')
        return ''

    timeout = int(config.get('file_wait_timeout', 120))
    first_frame = wait_for_sequence(sequence_dir, timeout=timeout)
    if not first_frame:
        _show_error(f'Export finished but no image files were found in:\n{sequence_dir}')
        return ''
    return first_frame


def get_clip_from_item(item):
    if isinstance(item, (flame.PyClip, flame.PySequence)):
        return item
    if isinstance(item, flame.PyClipNode):
        for attr in ('clip', 'source', 'media', 'sequence', 'input'):
            val = getattr(item, attr, None)
            if isinstance(val, (flame.PyClip, flame.PySequence)):
                return val
        return item
    return None


def get_clip_name(item):
    clip = get_clip_from_item(item)
    for candidate in (clip, item):
        if candidate is None:
            continue
        try:
            name = candidate.name.get_value()
            if name:
                return name
        except Exception:
            try:
                name = str(candidate.name)
                name = _strip_quotes(name)
                if name:
                    return name
            except Exception:
                pass
    if hasattr(item, 'path'):
        return sequence_base_name(str(item.path))
    return 'unnamed_clip'


def sequence_base_name(path):
    name = os.path.basename(path.rstrip('/'))
    name, _ext = os.path.splitext(name)
    name = re.sub(r'[._]?\d{2,}$', '', name)
    return name or 'unnamed_clip'


def _media_path_from_item(item):
    """Return the original disk path for Batch clips or MediaHub files."""
    if hasattr(item, 'path') and not hasattr(item, 'media_path'):
        path = str(item.path)
        if path:
            return path

    if hasattr(item, "media_path"):
        try:
            path = _strip_quotes(item.media_path)
            if path:
                return path
        except Exception:
            pass  # media_path raises RuntimeError on Flame-only clips

    clip = get_clip_from_item(item)
    if clip is not None and not isinstance(clip, flame.PyClipNode):
        try:
            path = clip.versions[0].tracks[0].segments[0].file_path
            path = _strip_quotes(path)
            if path:
                return path
        except Exception:
            pass

    if hasattr(item, 'file_path'):
        path = _strip_quotes(item.file_path)
        if path:
            return path

    return ''


def _show_error(message, title='Silhouette RoundTrip'):
    log(f'ERROR: {message}')
    try:
        flame.messages.show_in_dialog(
            title=title,
            message=message,
            type='error',
            buttons=['Ok'],
        )
    except Exception:
        pass


def _version_up_path(path):
    """Increment the v## version token in path to the next unused version.

    Searches for the last vNN / VNN pattern in the path string, increments
    the number, and keeps padding (v01 -> v02, v09 -> v10, etc.).
    If no version token is found the original path is returned unchanged.
    """
    import re as _re
    matches = list(_re.finditer(r'[vV](\d+)', path))
    if not matches:
        log('_version_up_path: no vNN token found in %r' % path)
        return path
    m = matches[-1]  # use the last (most specific) version token
    prefix = path[:m.start()]
    v_letter = path[m.start()]  # preserve case: 'v' or 'V'
    num = int(m.group(1))
    padding = len(m.group(1))
    suffix = path[m.end():]
    next_num = num + 1
    while True:
        new_path = prefix + v_letter + str(next_num).zfill(padding) + suffix
        if not os.path.exists(new_path):
            log('Version up: %r -> %r' % (path, new_path))
            return new_path
        next_num += 1


_FRAME_RANGE_RE = re.compile(r'\[(\d+)-(\d+)\]')


def _resolve_flame_seq_path(path):
    """Turn a Flame sequence pattern into the first-frame file path.

    Flame stores paths like /path/to/name.[1001-1464].exr.
    os.path.exists() on that literal string always returns False.
    We extract the first frame number and return the concrete path.
    Returns the resolved path, or the original string if it has no pattern.
    """
    m = _FRAME_RANGE_RE.search(path)
    if not m:
        return path
    first = m.group(1)
    padding = len(first)
    resolved = _FRAME_RANGE_RE.sub(first.zfill(padding), path, count=1)
    return resolved


def resolve_job_paths(item, config):
    clip = get_clip_from_item(item)
    clip_name = sanitize_filename(get_clip_name(item))
    raw_path = _media_path_from_item(item)
    source_path = ''
    if raw_path:
        # Flame sequence patterns like .[1001-1464].exr aren't real filenames.
        # Resolve to the first actual frame before checking existence.
        resolved = _resolve_flame_seq_path(raw_path)
        if os.path.exists(resolved):
            # Pass the first-frame path; Silhouette Source() auto-detects the sequence.
            source_path = resolved
            log(f'Using disk path (first frame): {source_path}')
        else:
            log(f'Media path does not exist on disk: {raw_path}')

    project_dir = resolve_path_template(
        config['project_path_template'],
        clip=clip if clip is not None and not isinstance(clip, flame.PyClipNode) else None,
        clip_name=clip_name,
    )
    render_stem = resolve_path_template(
        config['render_path_template'],
        clip=clip if clip is not None and not isinstance(clip, flame.PyClipNode) else None,
        clip_name=clip_name,
    )
    if render_stem.lower().endswith('.exr'):
        render_stem = os.path.splitext(render_stem)[0]

    project_path = os.path.join(project_dir, f'{clip_name}.sfx')
    render_dir = os.path.dirname(render_stem)

    # Read colour_space from the Flame clip.
    # Mirrors print_selection_attributes: try get_value(), str(), repr().
    colour_space = ''
    def _read_cs(obj):
        raw = getattr(obj, 'colour_space', None)
        if raw is None:
            return ''
        if hasattr(raw, 'get_value') and callable(raw.get_value):
            try:
                v = str(raw.get_value()).strip()
                if v: return v
            except Exception:
                pass
        v = str(raw).strip()
        if v and v not in ('<None>', 'None', 'null'): return v
        v = repr(raw).strip().strip("'\"")
        return v if v not in ('None', '') else ''

    try:
        log('clip type: %s  item type: %s' % (type(clip).__name__, type(item).__name__))
        for _cs_obj in [clip, item]:
            if _cs_obj is None or colour_space: break
            v = _read_cs(_cs_obj)
            if v:
                colour_space = v
                log('colour_space from %s: %r' % (type(_cs_obj).__name__, colour_space))
                break
            try:
                seg = _cs_obj.versions[0].tracks[0].segments[0]
                v = _read_cs(seg)
                if v:
                    colour_space = v
                    log('colour_space from segment: %r' % colour_space)
                    break
            except Exception: pass
        if not colour_space:
            log('Could not find colour_space on any candidate object')
    except Exception as exc:
        log('Could not read colour_space: %s' % exc)

    return {
        'source_path': source_path,
        'clip_name': clip_name,
        'session_name': clip_name,
        'project_dir': project_dir,
        'project_path': project_path,
        'render_path': render_stem,
        'render_dir': render_dir,
        'colour_space': colour_space,
        'ocio_config_path': get_flame_ocio_config_path(),
    }


def write_job_json(job):
    os.makedirs(job['project_dir'], exist_ok=True)
    os.makedirs(job['render_dir'], exist_ok=True)

    payload = {
        'source_path': job['source_path'],
        'clip_name': job['clip_name'],
        'session_name': job['session_name'],
        'project_path': job['project_path'],
        'render_path': job['render_path'],
        'colour_space': job.get('colour_space', ''),
        'ocio_config_path': job.get('ocio_config_path', ''),
        'apply_only': job.get('apply_only', False),
    }
    job_path = os.path.join(job['project_dir'], 'flame_job.json')
    with open(job_path, 'w') as handle:
        json.dump(payload, handle, indent=4)
    try:
        with open(DEFAULT_JOB, 'w') as handle:
            json.dump(payload, handle, indent=4)
    except Exception as exc:
        log(f'Could not write {DEFAULT_JOB}: {exc}')
    log(f'Wrote job JSON: {job_path}')
    return job_path


def _silhouette_binary(app_path):
    if not app_path:
        return ''
    if app_path.endswith('.app'):
        exe_name = os.path.splitext(os.path.basename(app_path))[0]
        mac_binary = os.path.join(app_path, 'Contents', 'MacOS', exe_name)
        if os.path.exists(mac_binary):
            return mac_binary
        silhouette_binary = os.path.join(app_path, 'Contents', 'MacOS', 'Silhouette')
        if os.path.exists(silhouette_binary):
            return silhouette_binary
    return app_path


def launch_silhouette(config, job_path=None, project_path=None):
    app_path = config.get('silhouette_app', '')
    binary = _silhouette_binary(app_path)
    if not binary or not os.path.exists(binary):
        _show_error(
            'Silhouette application not found. Open Setup and set the .app path.\n'
            f'Current: {app_path}'
        )
        return False

    env = os.environ.copy()
    args = [binary, '-no_launcher']
    if job_path:
        env[JOB_ENV] = job_path
        # Set OCIO to the Flame project config so Silhouette uses the same colorspaces.
        try:
            with open(job_path) as _jf:
                import json as _json
                _job_data = _json.load(_jf)
            _ocio = _job_data.get('ocio_config_path', '')
            if _ocio and os.path.isfile(_ocio):
                env['OCIO'] = _ocio
                log(f'OCIO env var -> {_ocio}')
            else:
                log('No Flame project OCIO config found; Silhouette uses its default.')
        except Exception as _exc:
            log(f'Could not read OCIO config path from job: {_exc}')
        # -script only runs after a project is loaded; we launch with no project,
        # so inject a startup module via SFX_SCRIPT_IMPORTS that uses a Qt timer
        # to defer the session build until Silhouette's event loop is running.
        import time as _time
        _stamp = str(int(_time.time()))
        _launcher_dir = f'/tmp/sfx_roundtrip_{_stamp}'
        os.makedirs(_launcher_dir, exist_ok=True)
        _init_lines = [
            'import os, sys',
            '_LOG = "/tmp/silhouette_roundtrip.log"',
            'def _log(msg):',
            '    try:',
            '        with open(_LOG, "a") as _fh:',
            '            _fh.write("==launcher: " + msg + chr(10))',
            '    except Exception:',
            '        pass',
            'job_path = os.environ.get("SILHOUETTE_FLAME_JOB", "")',
            'script_dir = os.environ.get("SILHOUETTE_FLAME_SCRIPT_DIR", "")',
            '_log("__init__.py loaded. job=%s" % job_path)',
            'if job_path and os.path.isfile(job_path):',
            '    try:',
            '        from PySide6.QtCore import QTimer',
            '        if script_dir and script_dir not in sys.path:',
            '            sys.path.insert(0, script_dir)',
            '        def _run():',
            '            _log("QTimer fired - importing silhouette_setup")',
            '            try:',
            '                import silhouette_setup',
            '            except Exception:',
            '                import traceback',
            '                _log("ERROR: " + traceback.format_exc())',
            '        QTimer.singleShot(1500, _run)',
            '        _log("QTimer scheduled 1500ms")',
            '    except Exception:',
            '        import traceback',
            '        _log("QTimer setup error: " + traceback.format_exc())',
            'else:',
            '    _log("No valid job_path - skipping. job_path=%r" % job_path)',
        ]
        _init_src = '\n'.join(_init_lines) + '\n'
        with open(os.path.join(_launcher_dir, '__init__.py'), 'w') as _fh:
            _fh.write(_init_src)
        env['SFX_SCRIPT_IMPORTS'] = _launcher_dir
        env['SILHOUETTE_FLAME_SCRIPT_DIR'] = SCRIPT_PATH
        log(f'Launcher module: {_launcher_dir}')
    if project_path:
        args.append(project_path)

    log(f'Launching: {" ".join(args)}')
    try:
        popen_kwargs = {
            'env': env,
            'start_new_session': True,
        }
        if platform.system() == 'Darwin':
            popen_kwargs['stdout'] = None
            popen_kwargs['stderr'] = None
        else:
            # Write Silhouette output to a log file so setup errors are visible.
            log_path = '/tmp/silhouette_roundtrip.log'
            log(f'Silhouette output log: {log_path}')
            try:
                _log_fh = open(log_path, 'w', buffering=1)
                popen_kwargs['stdout'] = _log_fh
                popen_kwargs['stderr'] = _log_fh
            except Exception:
                popen_kwargs['stdout'] = subprocess.DEVNULL
                popen_kwargs['stderr'] = subprocess.DEVNULL
        subprocess.Popen(args, **popen_kwargs)
        if platform.system() == 'Darwin':
            try:
                flame.messages.show_in_dialog(
                    title='Silhouette',
                    message='Silhouette is starting. Use Command-H if you need to hide Flame.',
                    type='info',
                    buttons=['Ok'],
                )
            except Exception:
                pass
        return True
    except Exception as exc:
        _show_error(f'Failed to launch Silhouette:\n{exc}')
        return False


def open_in_silhouette(selection):
    try:
        _open_in_silhouette(selection)
    except Exception:
        _show_error(f'Open in Silhouette failed:\n{traceback.format_exc()}')


def _open_in_silhouette(selection):
    config = load_config()
    if not selection:
        _show_error('Select a clip in Batch or a file in MediaHub first.')
        return

    item = selection[0]
    job = resolve_job_paths(item, config)
    if not job:
        _show_error('Could not resolve paths for the selection.')
        return

    sfx_path = job['project_path']
    if os.path.exists(sfx_path):
        choice = prompt_existing_project(
            'A Silhouette project already exists for this shot.'
        )
        if choice == 'Cancel' or choice is None:
            log('Open cancelled by user')
            return
        if choice == 'Open Project':
            job['apply_only'] = True
            job_path = write_job_json(job)
            launch_silhouette(config, job_path=job_path, project_path=sfx_path)
            return
        if choice == 'Open + Version Up':
            new_sfx = _version_up_path(sfx_path)
            job['project_path'] = new_sfx
            new_stem = os.path.splitext(os.path.basename(new_sfx))[0]
            job['clip_name']    = new_stem
            job['session_name'] = new_stem
            job['render_path']  = _version_up_path(job['render_path'])
            job['render_dir']   = os.path.dirname(job['render_path'])
            log(f'Version up -> project: {new_sfx}')
            log(f'Version up -> render:  {job["render_path"]}')
            # Fall through to create the new versioned session.
        else:  # Start Over
            try:
                if os.path.isdir(sfx_path):
                    shutil.rmtree(sfx_path)
                elif os.path.isfile(sfx_path):
                    os.remove(sfx_path)
                log(f'Removed existing project for rebuild: {sfx_path}')
            except Exception as exc:
                log(f'Could not remove existing project (will try overwrite): {exc}')


    if not job['source_path']:
        exported = export_clip_for_silhouette(item, job, config)
        if not exported:
            return
        job['source_path'] = exported

    if not os.path.isfile(SETUP_SCRIPT):
        _show_error(f'Silhouette setup script not found:\n{SETUP_SCRIPT}')
        return

    job_path = write_job_json(job)
    launch_silhouette(config, job_path=job_path)


def get_or_create_result_reel(reel_name):
    try:
        for reel in flame.batch.reels:
            if str(reel.name).strip("'") == reel_name or reel.name == reel_name:
                log(f'Found existing Batch Reel: {reel_name}')
                return reel
        new_reel = flame.batch.create_reel(reel_name)
        log(f'Created new Batch Reel: {reel_name}')
        return new_reel
    except Exception as exc:
        log(f'ERROR: Failed to access or create Batch Reel {reel_name}: {exc}')
        return None


def import_sequences_to_batch(sequence_list):
    config = load_config()
    reel_name = config.get('result_reel_name', 'Silhouette Results')
    target_reel = get_or_create_result_reel(reel_name)
    if not target_reel:
        _show_error(
            'Could not import into Batch. Open a Batch group, or use '
            'Reveal in MediaHub from the import dialog.'
        )
        return []

    imported_clips = []
    for seq in sequence_list:
        import_pattern = seq['import_pattern']
        log(f'Importing: {import_pattern}')
        try:
            clip_node = flame.batch.import_clip(import_pattern, reel_name)
            if clip_node:
                try:
                    clip_node.name = seq['name']
                except Exception:
                    pass
                imported_clips.append(clip_node)
                log(f'Successfully imported: {seq["name"]}')
        except Exception as exc:
            log(f'ERROR importing {seq["name"]}: {exc}')
    log(f'Imported {len(imported_clips)}/{len(sequence_list)} item(s) into Batch Reel.')
    return imported_clips


def reveal_in_mediahub(path):
    directory = path if os.path.isdir(path) else os.path.dirname(path)
    if not directory:
        return
    try:
        flame.go_to('MediaHub')
        flame.mediahub.files.set_path(directory)
        log(f'Opened MediaHub: {directory}')
    except Exception as exc:
        log(f'Could not open MediaHub: {exc}')
        _show_error(f'Could not open MediaHub:\n{exc}')


def import_results(selection):
    try:
        _import_results(selection)
    except Exception:
        _show_error(f'Import Results failed:\n{traceback.format_exc()}')


def _import_results(selection):
    global _import_dialog_ref
    config = load_config()

    result_dir = ''
    if selection:
        job = resolve_job_paths(selection[0], config)
        if job:
            result_dir = job['render_dir']

    if not result_dir:
        result_dir = resolve_path_template(
            os.path.dirname(config['render_path_template']),
            clip_name='clip',
        )

    log(f'Opening import dialog for: {result_dir}')

    def on_import_requested(sequence_list):
        import_sequences_to_batch(sequence_list)

    dialog = prompt_for_result_import(
        result_dir,
        import_callback=on_import_requested,
        reveal_callback=reveal_in_mediahub,
        log_func=log,
    )
    if dialog:
        _import_dialog_ref = dialog
        dialog.show()


def setup_window(selection):
    global _setup_window_ref
    config = load_config()
    _setup_window_ref = show_setup_window(config, save_config, log_func=log)


def scope_batch_clip(selection):
    for item in selection:
        try:
            if _media_path_from_item(item):
                return True
        except Exception:
            pass
        try:
            if get_exportable_clip(item) is not None:
                return True
        except Exception:
            pass
        try:
            if getattr(item, "type", None) == "Clip":
                return True
        except Exception:
            pass
        if isinstance(item, flame.PyClipNode):
            return True
    return False


def scope_mediahub_file(selection):
    for item in selection:
        path = getattr(item, 'path', None)
        if not path:
            continue
        path = str(path)
        if os.path.isdir(path):
            return True
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_EXTENSIONS or os.path.isfile(path):
            return True
    return False


def get_main_menu_custom_ui_actions():
    return [{
        'name': 'Silhouette RoundTrip',
        'actions': [{
            'name': 'Setup',
            'execute': setup_window,
            'minimumVersion': '2025',
        }],
    }]


def get_mediahub_files_custom_ui_actions():
    return [{
        'name': 'Silhouette RoundTrip...',
        'separator': 'above',
        'actions': [
            {
                'name': 'Open in Silhouette',
                'execute': open_in_silhouette,
                'isVisible': scope_mediahub_file,
                'minimumVersion': '2025',
            },
            {
                'name': 'Import Results',
                'execute': import_results,
                'isVisible': scope_mediahub_file,
                'minimumVersion': '2025',
            },
            {
                'name': 'Setup',
                'execute': setup_window,
                'minimumVersion': '2025',
            },
        ],
    }]


def get_batch_custom_ui_actions():
    return [{
        'name': 'Silhouette RoundTrip...',
        'actions': [
            {
                'name': 'Open in Silhouette',
                'execute': open_in_silhouette,
                'isVisible': scope_batch_clip,
                'minimumVersion': '2025',
            },
            {
                'name': 'Import Results',
                'execute': import_results,
                'isVisible': scope_batch_clip,
                'minimumVersion': '2025',
            },
            {
                'name': 'Setup',
                'execute': setup_window,
                'minimumVersion': '2025',
            },
        ],
    }]


get_mediahub_files_custom_ui_actions.minimum_version = '2025'
get_batch_custom_ui_actions.minimum_version = '2025'
get_main_menu_custom_ui_actions.minimum_version = '2025'
