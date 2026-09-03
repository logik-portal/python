"""
silhouette_roundtrip - User Interface Module
Version: 1.0.0

Setup window with token picker and a scan/import dialog for Silhouette renders.
Uses PyFlame 5.5.1 widgets.
"""

import datetime
import importlib.util
import os
import re
import platform
import sys

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QFileDialog

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)


def _load_pyflame():
    """Load this script's PyFlame file by path.

    Flame keeps every hook in one interpreter, and many scripts share a folder
    named lib. Importing `lib.pyflame_lib_...` can hit a different script's
    package. Loading the file directly avoids that collision.
    """
    lib_file = os.path.join(_SCRIPT_DIR, 'lib', 'pyflame_lib_silhouette_roundtrip.py')
    if not os.path.isfile(lib_file):
        raise ModuleNotFoundError(
            f'PyFlame library not found at {lib_file}. '
            'Copy the full silhouette_roundtrip folder, including lib/ and assets/fonts/.'
        )
    module_name = 'pyflame_lib_silhouette_roundtrip'
    spec = importlib.util.spec_from_file_location(module_name, lib_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_load_pyflame()
from pyflame_lib_silhouette_roundtrip import *


PATH_HISTORY_MAX = 10

IMAGE_EXTENSIONS = (
    '.jpg', '.jpeg', '.tif', '.tiff', '.exr', '.png', '.dpx',
    '.bmp', '.sgi', '.rgb', '.psd', '.hdr', '.pic', '.ppm',
    '.tga', '.cin', '.als',
)
VIDEO_EXTENSIONS = (
    '.mov', '.mp4', '.mkv', '.avi', '.mxf', '.webm', '.wmv',
    '.m4v', '.mpg', '.mpeg', '.ts', '.flv', '.ogv',
)

TOKEN_DICT = {
    'Project Name': '{project_name}',
    'Project Nickname': '{nickname}',
    'Clip Name': '{clip_name}',
    'Shot Name': '{shot_name}',
    'Batch Name': '{batch_name}',
    'Batch Iteration': '{batch_iteration}',
    'User Name': '{user_name}',
    'Year (YYYY)': '{date_YYYY}',
    'Month (MM)': '{date_MM}',
    'Day (DD)': '{date_DD}',
    'Date (YYYY-MM-DD)': '{date_YYYY_MM_DD}',
    'Unix Timestamp': '{timestamp}',
}


def detect_sequences_in_directory(directory):
    """Scan a directory and group image sequences / files for Flame import."""
    if not os.path.exists(directory):
        return []

    all_files = sorted([
        name for name in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, name)) and not name.startswith('.')
    ])
    if not all_files:
        return []

    frame_regex = re.compile(
        r'^(.+?)'
        r'[._]?'
        r'(\d{2,})'
        r'(\.[^.]+)$'
    )

    image_files = []
    video_files = []
    other_files = []
    for name in all_files:
        ext = os.path.splitext(name)[1].lower()
        if ext in IMAGE_EXTENSIONS:
            image_files.append(name)
        elif ext in VIDEO_EXTENSIONS:
            video_files.append(name)
        else:
            other_files.append(name)

    sequences = {}
    orphan_images = []
    for filename in image_files:
        match = frame_regex.match(filename)
        if match:
            base_name = match.group(1)
            frame_num = int(match.group(2))
            padding = len(match.group(2))
            extension = match.group(3)
            base_clean = base_name.rstrip('._')
            key = (base_clean, extension.lower(), padding)
            if key not in sequences:
                sequences[key] = {
                    'name': base_clean,
                    'extension': extension,
                    'padding': padding,
                    'frames': [],
                    'files': [],
                }
            sequences[key]['frames'].append(frame_num)
            sequences[key]['files'].append(filename)
        else:
            orphan_images.append(filename)

    results = []
    for seq_data in sequences.values():
        if len(seq_data['frames']) >= 2:
            frames = sorted(seq_data['frames'])
            start_frame = min(frames)
            end_frame = max(frames)
            padding = seq_data['padding']
            first_file = sorted(seq_data['files'])[0]
            sep_match = re.match(re.escape(seq_data['name']) + r'([._]?)\d', first_file)
            separator = sep_match.group(1) if sep_match else '.'
            display_pattern = (
                f"{seq_data['name']}{separator}{'#' * padding}{seq_data['extension']}"
            )
            import_pattern = os.path.join(
                directory,
                f"{seq_data['name']}{separator}"
                f"[{str(start_frame).zfill(padding)}-{str(end_frame).zfill(padding)}]"
                f"{seq_data['extension']}"
            )
            results.append({
                'name': seq_data['name'],
                'pattern': display_pattern,
                'first_file': first_file,
                'start_frame': start_frame,
                'end_frame': end_frame,
                'frame_count': len(frames),
                'extension': seq_data['extension'],
                'padding': padding,
                'directory': directory,
                'import_pattern': import_pattern,
                'is_sequence': True,
                'file_type': 'sequence',
            })
        else:
            orphan_images.extend(seq_data['files'])

    for filename in sorted(video_files):
        results.append({
            'name': filename,
            'pattern': filename,
            'first_file': filename,
            'start_frame': 0,
            'end_frame': 0,
            'frame_count': 1,
            'extension': os.path.splitext(filename)[1],
            'padding': 0,
            'directory': directory,
            'import_pattern': os.path.join(directory, filename),
            'is_sequence': False,
            'file_type': 'video',
        })

    for filename in sorted(set(orphan_images)):
        results.append({
            'name': filename,
            'pattern': filename,
            'first_file': filename,
            'start_frame': 0,
            'end_frame': 0,
            'frame_count': 1,
            'extension': os.path.splitext(filename)[1],
            'padding': 0,
            'directory': directory,
            'import_pattern': os.path.join(directory, filename),
            'is_sequence': False,
            'file_type': 'single_image',
        })

    for filename in sorted(other_files):
        results.append({
            'name': filename,
            'pattern': filename,
            'first_file': filename,
            'start_frame': 0,
            'end_frame': 0,
            'frame_count': 1,
            'extension': os.path.splitext(filename)[1],
            'padding': 0,
            'directory': directory,
            'import_pattern': os.path.join(directory, filename),
            'is_sequence': False,
            'file_type': 'other',
        })

    return results


class SilhouetteImportDialog:
    """Scan a render folder and import selected sequences into Flame."""

    def __init__(self, result_path, import_callback=None, reveal_callback=None, log_func=None):
        self.result_path = result_path
        self.import_callback = import_callback
        self.reveal_callback = reveal_callback
        self.log_func = log_func or (lambda msg: print(f'==silhouette_roundtrip: {msg}'))
        self.sequences = []
        self._import_count = 0

        self.window = PyFlameWindow(
            parent=None,
            title='Silhouette RoundTrip - Import Results',
            return_pressed=self._do_import,
            escape_pressed=self.close,
            grid_layout_columns=4,
            grid_layout_rows=5,
            grid_layout_column_width=160,
            grid_layout_row_height=28,
            grid_layout_adjust_column_widths={0: 150, 1: 200, 2: 200, 3: 150},
            grid_layout_adjust_row_heights={3: 260},
        )

        help_label = PyFlameLabel(
            text='Silhouette has launched. Scan for renders when you are ready to import.',
            style=Style.BACKGROUND,
        )
        path_label = PyFlameLabel(text='Render Path:')
        self.path_display = PyFlameEntry(
            text=self.result_path,
            placeholder_text='Paste or edit a render path, then click Scan',
        )
        copy_btn = PyFlameButton(text='Copy', connect=self._copy_path)

        self.scan_btn = PyFlameButton(
            text='Scan / Refresh',
            connect=self._scan_results,
            color=Color.BLUE,
        )
        self.select_all_btn = PyFlameButton(
            text='Select All', connect=self._select_all, enabled=False
        )
        self.select_none_btn = PyFlameButton(
            text='Select None', connect=self._select_none, enabled=False
        )
        self.scan_info = PyFlameLabel(text='', style=Style.BACKGROUND_THIN)

        self.file_list = PyFlameListWidget(
            header='Renders',
            header_align=Align.LEFT,
            multi_selection=False,
        )
        self.file_list.itemChanged.connect(self._on_item_changed)

        self.reveal_btn = PyFlameButton(
            text='Reveal in MediaHub',
            connect=self._reveal_in_mediahub,
        )
        close_btn = PyFlameButton(text='Close', connect=self.close)
        self.import_btn = PyFlameButton(
            text='Import Selected',
            connect=self._do_import,
            color=Color.BLUE,
            enabled=False,
        )

        grid = self.window.grid_layout
        grid.addWidget(help_label, 0, 0, 1, 4)
        grid.addWidget(path_label, 1, 0)
        grid.addWidget(self.path_display, 1, 1, 1, 2)
        grid.addWidget(copy_btn, 1, 3)
        grid.addWidget(self.scan_btn, 2, 0)
        grid.addWidget(self.select_all_btn, 2, 1)
        grid.addWidget(self.select_none_btn, 2, 2)
        grid.addWidget(self.scan_info, 2, 3)
        grid.addWidget(self.file_list, 3, 0, 1, 4)
        grid.addWidget(self.reveal_btn, 4, 0, 1, 2)
        grid.addWidget(close_btn, 4, 2)
        grid.addWidget(self.import_btn, 4, 3)

        self.window.message_bar_text = 'Click "Scan / Refresh" to search for rendered mattes.'
        self._scan_results()

    def show(self):
        self.window.show()

    def close(self, *args):
        self.window.close()

    def _copy_path(self, *args):
        current_path = self.path_display.text.strip()
        pyflame.copy_to_clipboard(current_path)
        self.window.message_bar_text = 'Render path copied to clipboard.'

    def _scan_results(self, *args):
        scan_path = self.path_display.text.strip()
        if scan_path:
            self.result_path = scan_path

        self.log_func(f'Scanning render directory: {self.result_path}')
        self.file_list.clear()
        self.sequences = []

        if not os.path.exists(self.result_path):
            self.window.message_bar_text = f'Directory does not exist: {self.result_path}'
            self.scan_info.text = '0 sequences found'
            self._update_button_states()
            return

        self.sequences = detect_sequences_in_directory(self.result_path)
        if not self.sequences:
            self.window.message_bar_text = (
                'No files found. Render from Silhouette, then click Scan again.'
            )
            self.scan_info.text = '0 sequences found'
            self._update_button_states()
            return

        self.file_list.blockSignals(True)
        for seq in self.sequences:
            if seq['is_sequence']:
                display_text = (
                    f"SEQ  {seq['pattern']}   "
                    f"[{seq['start_frame']}-{seq['end_frame']}]   "
                    f"({seq['frame_count']} frames)"
                )
            else:
                file_path = os.path.join(seq['directory'], seq['first_file'])
                try:
                    file_size = os.path.getsize(file_path)
                    size_mb = file_size / (1024 * 1024)
                    size_str = f'{size_mb:.1f} MB' if size_mb >= 1 else f'{file_size / 1024:.0f} KB'
                except OSError:
                    size_str = '? KB'
                type_label = {
                    'video': 'VID',
                    'single_image': 'IMG',
                    'other': 'FILE',
                }.get(seq.get('file_type', 'other'), 'FILE')
                display_text = f"{type_label}  {seq['name']}   ({size_str})"

            item = QtWidgets.QListWidgetItem(display_text)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsUserCheckable)
            item.setCheckState(QtCore.Qt.Checked)
            item.setData(QtCore.Qt.UserRole, seq)
            self.file_list.addItem(item)
        self.file_list.blockSignals(False)

        count = len(self.sequences)
        seq_count = sum(1 for item in self.sequences if item['is_sequence'])
        file_count = count - seq_count
        parts = []
        if seq_count:
            parts.append(f"{seq_count} sequence{'s' if seq_count != 1 else ''}")
        if file_count:
            parts.append(f"{file_count} file{'s' if file_count != 1 else ''}")
        info_text = ' + '.join(parts) if parts else '0 items found'
        self.scan_info.text = info_text
        self.window.message_bar_text = (
            f'Found {count} item{"s" if count != 1 else ""}. '
            'Select the ones to import and click "Import Selected".'
        )
        self.log_func(f'Scan found: {info_text}')
        self._update_button_states()

    def _select_all(self, *args):
        self.file_list.blockSignals(True)
        for index in range(self.file_list.count()):
            self.file_list.item(index).setCheckState(QtCore.Qt.Checked)
        self.file_list.blockSignals(False)
        self._update_button_states()

    def _select_none(self, *args):
        self.file_list.blockSignals(True)
        for index in range(self.file_list.count()):
            self.file_list.item(index).setCheckState(QtCore.Qt.Unchecked)
        self.file_list.blockSignals(False)
        self._update_button_states()

    def _count_checked(self):
        return sum(
            1 for index in range(self.file_list.count())
            if self.file_list.item(index).checkState() == QtCore.Qt.Checked
        )

    def _on_item_changed(self, item):
        self._update_button_states()

    def _update_button_states(self):
        has_items = self.file_list.count() > 0
        checked = self._count_checked()
        self.select_all_btn.enabled = has_items
        self.select_none_btn.enabled = has_items
        self.import_btn.enabled = checked > 0

    def _do_import(self, *args):
        selected = []
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                selected.append(dict(item.data(QtCore.Qt.UserRole)))
        if not selected:
            self.window.message_bar_text = 'No files selected for import.'
            return

        self._import_count += len(selected)
        if self.import_callback:
            self.import_callback(selected)

        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            if item.checkState() == QtCore.Qt.Checked:
                item.setForeground(QtGui.QColor(0, 150, 64))
                current_text = item.text()
                if not current_text.startswith('✓ '):
                    item.setText(f'✓ {current_text}')
                item.setCheckState(QtCore.Qt.Unchecked)

        count = len(selected)
        self.window.message_bar_text = (
            f'Imported {count} item{"s" if count != 1 else ""} into Flame. '
            f'(Total: {self._import_count}) — You can scan and import more, or close.'
        )

    def _reveal_in_mediahub(self, *args):
        path = self.path_display.text.strip() or self.result_path
        if self.reveal_callback:
            self.reveal_callback(path)


def prompt_for_result_import(result_path, import_callback=None,
                             reveal_callback=None, log_func=None):
    def log(msg):
        if log_func:
            log_func(msg)
        else:
            print(f'==silhouette_roundtrip: {msg}')

    try:
        pyflame.copy_to_clipboard(result_path)
        log('Render path copied to clipboard.')
        return SilhouetteImportDialog(
            result_path,
            import_callback=import_callback,
            reveal_callback=reveal_callback,
            log_func=log,
        )
    except Exception as exc:
        log(f'Error creating import dialog: {exc}')
        return None


def _preview_token_map():
    try:
        import flame
        project_name = flame.project.current_project.name
        nickname = flame.project.current_project.nickname
    except Exception:
        project_name = '<project>'
        nickname = '<nickname>'
    now = datetime.datetime.now()
    return {
        'project_name': project_name,
        'nickname': nickname,
        'project_name_raw': project_name,
        'nickname_raw': nickname,
        'clip_name': '<clip_name>',
        'shot_name': '<shot_name>',
        'batch_name': '<batch_name>',
        'batch_iteration': '<iter>',
        'user_name': os.environ.get('USER', '<user>'),
        'date_YYYY': now.strftime('%Y'),
        'date_MM': now.strftime('%m'),
        'date_DD': now.strftime('%d'),
        'date_YYYY_MM_DD': now.strftime('%Y-%m-%d'),
        'timestamp': str(int(now.timestamp())),
    }


def _history_options(config):
    history = config.get('path_history', []) or []
    if history:
        return list(history) + ['Clear History']
    return ['No saved paths']


def show_setup_window(config, save_config_func, log_func=None):
    def log(msg):
        if log_func:
            log_func(msg)
        else:
            print(f'==silhouette_roundtrip: {msg}')

    def update_previews(*_args):
        preview_map = _preview_token_map()
        for entry, preview in ((project_entry, project_preview), (render_entry, render_preview)):
            template = entry.text
            try:
                resolved = template.format(**preview_map)
                preview.text = f'Preview: {resolved}'
            except (KeyError, ValueError) as exc:
                preview.text = f'Invalid token in template: {exc}'

    def browse_app(*_args):
        if platform.system() == 'Darwin':
            start_dir = os.path.dirname(app_entry.text) or '/Applications/BorisFX'
            if not os.path.isdir(start_dir):
                start_dir = '/Applications'
            dlg_title = 'Select Silhouette.app'
            dlg_filter = 'Applications (*.app);;All Files (*)'
        else:
            start_dir = os.path.dirname(app_entry.text) or '/opt/BorisFX'
            if not os.path.isdir(start_dir):
                start_dir = '/opt/BorisFX'
            dlg_title = 'Select Silhouette binary'
            dlg_filter = 'All Files (*)'
        window.hide()
        path = QFileDialog.getOpenFileName(
            None,
            dlg_title,
            start_dir,
            dlg_filter,
        )[0]
        window.show()
        if path:
            app_entry.text = path

    def browse_preset(*_args):
        start_dir = os.path.dirname(preset_entry.text) or '/opt/Autodesk'
        path = pyflame.file_browser(
            path=start_dir,
            title='Select Flame Export Preset',
            extension='xml',
            use_flame_browser=True,
            window_to_hide=window,
        )
        if path:
            preset_entry.text = path

    def on_history(*_args):
        selected = history_menu.text
        if selected == 'Clear History':
            config['path_history'] = []
            history_menu.update_menu('History', ['No saved paths'], connect=on_history)
            window.message_bar_text = 'Project template history cleared.'
            return
        if selected not in ('History', 'No saved paths'):
            project_entry.text = selected
            update_previews()
        history_menu.text = 'History'

    def save_and_close(*_args):
        current_project = project_entry.text.strip()
        current_render = render_entry.text.strip()
        history = config.get('path_history', [])[:]
        if current_project:
            history = [item for item in history if item != current_project]
            history.insert(0, current_project)
            history = history[:PATH_HISTORY_MAX]

        new_config = {
            'silhouette_app': app_entry.text.strip(),
            'export_preset_path': preset_entry.text.strip(),
            'project_path_template': current_project,
            'render_path_template': current_render,
            'result_reel_name': reel_entry.text.strip() or 'Silhouette Results',
            'file_wait_timeout': config.get('file_wait_timeout', 120),
            'path_history': history,
        }

        app_path = new_config['silhouette_app']
        if app_path and not os.path.exists(app_path):
            window.message_bar_text = 'Warning: Silhouette application path does not exist.'

        preset_path = new_config['export_preset_path']
        if preset_path and not os.path.exists(preset_path):
            window.message_bar_text = 'Warning: Export preset path does not exist.'

        if save_config_func(new_config):
            window.message_bar_text = 'Configuration saved successfully!'
            log('Configuration saved.')
            QtCore.QTimer.singleShot(600, window.close)
        else:
            window.message_bar_text = 'Error saving configuration.'

    def cancel(*_args):
        window.close()

    window = PyFlameWindow(
        parent=None,
        title='Silhouette RoundTrip - Configuration',
        return_pressed=save_and_close,
        escape_pressed=cancel,
        grid_layout_columns=3,
        grid_layout_rows=14,
        grid_layout_column_width=150,
        grid_layout_row_height=28,
        grid_layout_adjust_column_widths={0: 220, 1: 480, 2: 120},
        grid_layout_adjust_row_heights={6: 40, 9: 40},
    )

    app_entry = PyFlameEntry(text=config.get('silhouette_app', ''))
    preset_entry = PyFlameEntry(text=config.get('export_preset_path', ''))
    project_entry = PyFlameEntry(
        text=config.get('project_path_template', ''),
        placeholder_text='/path/to/{project_name}/SHOTS/{batch_name}/silhouette/{clip_name}',
        text_changed=update_previews,
    )
    render_entry = PyFlameEntry(
        text=config.get('render_path_template', ''),
        placeholder_text='/path/to/{clip_name}/render/{clip_name}_matte',
        text_changed=update_previews,
    )
    reel_entry = PyFlameEntry(
        text=config.get('result_reel_name', 'Silhouette Results'),
    )

    project_token = PyFlameTokenMenu(
        text='Tokens',
        token_dict=TOKEN_DICT,
        token_dest=project_entry,
    )
    render_token = PyFlameTokenMenu(
        text='Tokens',
        token_dict=TOKEN_DICT,
        token_dest=render_entry,
    )
    project_preview = PyFlameLabel(text='', style=Style.BACKGROUND_THIN)
    render_preview = PyFlameLabel(text='', style=Style.BACKGROUND_THIN)
    history_menu = PyFlameMenu(
        text='History',
        menu_options=_history_options(config),
        menu_indicator=True,
        connect=on_history,
    )

    grid = window.grid_layout
    grid.addWidget(PyFlameLabel(text='Silhouette Application:'), 0, 0, 1, 3)
    grid.addWidget(app_entry, 1, 0, 1, 2)
    grid.addWidget(PyFlameButton(text='Browse...', connect=browse_app), 1, 2)
    grid.addWidget(PyFlameLabel(text='Flame Export Preset (.xml):'), 2, 0, 1, 3)
    grid.addWidget(preset_entry, 3, 0, 1, 2)
    grid.addWidget(PyFlameButton(text='Browse...', connect=browse_preset), 3, 2)
    grid.addWidget(PyFlameLabel(text='Project Path Template (.sfx folder):'), 4, 0, 1, 3)
    grid.addWidget(project_entry, 5, 0, 1, 2)
    grid.addWidget(project_token, 5, 2)
    grid.addWidget(project_preview, 6, 0, 1, 3)
    grid.addWidget(PyFlameLabel(text='Render Path Template (DWAA EXR, no extension):'), 7, 0, 1, 3)
    grid.addWidget(render_entry, 8, 0, 1, 2)
    grid.addWidget(render_token, 8, 2)
    grid.addWidget(render_preview, 9, 0, 1, 3)
    grid.addWidget(PyFlameLabel(text='Project template history:'), 10, 0)
    grid.addWidget(history_menu, 10, 1, 1, 2)
    grid.addWidget(PyFlameLabel(text='Result Reel Name:'), 11, 0, 1, 3)
    grid.addWidget(reel_entry, 12, 0, 1, 2)
    grid.addWidget(PyFlameButton(text='Cancel', connect=cancel), 13, 1)
    grid.addWidget(PyFlameButton(text='Save', connect=save_and_close, color=Color.BLUE), 13, 2)

    update_previews()
    window.message_bar_text = 'Set Silhouette paths and token templates, then Save.'
    return window


def prompt_existing_project(message=None):
    """Modal 4-button prompt. Returns the clicked button label, or 'Cancel'."""
    if not message:
        message = 'A Silhouette project already exists for this shot.'

    result = {'choice': 'Cancel'}

    def _choose(name):
        result['choice'] = name
        window.accept()

    def _cancel(*_args):
        result['choice'] = 'Cancel'
        window.reject()

    window = PyFlameWindow(
        parent=None,
        title='Existing Silhouette Project',
        title_style=Style.BACKGROUND_THIN,
        title_font_size=18,
        title_height=28,
        line_color=Color.DARK_GRAY,
        return_pressed=lambda: _choose('Open Project'),
        escape_pressed=_cancel,
        grid_layout_columns=8,
        grid_layout_rows=2,
        grid_layout_column_width=120,
        grid_layout_row_height=26,
        grid_layout_adjust_row_heights={0: 18, 1: 34},
        window_margins=(18, 8, 18, 14),
        message_bar=False,
    )

    grid = window.grid_layout
    # Tighten spacing: message sits directly under the title banner.
    grid.addWidget(PyFlameLabel(text=message, style=Style.NORMAL), 0, 0, 1, 8)
    grid.addWidget(
        PyFlameButton(text='Open Project', connect=lambda: _choose('Open Project'), color=Color.BLUE),
        1, 0, 1, 2,
    )
    grid.addWidget(
        PyFlameButton(text='Open + Version Up', connect=lambda: _choose('Open + Version Up')),
        1, 2, 1, 2,
    )
    grid.addWidget(
        PyFlameButton(text='Start Over', connect=lambda: _choose('Start Over')),
        1, 4, 1, 2,
    )
    grid.addWidget(
        PyFlameButton(text='Cancel', connect=_cancel),
        1, 6, 1, 2,
    )

    window.exec()
    return result['choice']

