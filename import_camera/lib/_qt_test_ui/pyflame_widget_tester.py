# PyFlame Widget Tester
# Copyright (c) 2026 Michael Vaglienty

"""
Script Name: PyFlame Widget Tester
Script Version: 1.0.0
Written by: Michael Vaglienty
Creation Date: 11.17.26
Update Date: 11.17.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Test Tool

Description:

    Standalone PySide6 app, run outside Flame, that shows every PyFlame* class in a
    PyFlameLib file so its widgets can be tried before testing in Flame. Constructor
    arguments, properties and methods are generated from the library itself, so new
    widgets and new arguments show up without changing this app.

    The library is loaded from a file path (default: ../pyflame_lib.py) under its own
    module name, with a fake `flame` module in place. sudo is blocked in this process.

URL:
    Internal test tool, not published.

Usage:

    Human (a window opens):

        /opt/Autodesk/python/2027.2/bin/python3 -B pyflame_widget_tester.py [--lib PATH]

    Agent (no window, offscreen, exit code 0/1):

        QT_QPA_PLATFORM=offscreen /opt/Autodesk/python/2027.2/bin/python3 -B pyflame_widget_tester.py --self-test [--lib PATH] [--grab DIR] [--only NAMES]

    Screenshots of the app window with widgets selected:

        QT_QPA_PLATFORM=offscreen /opt/Autodesk/python/2027.2/bin/python3 -B pyflame_widget_tester.py --screenshot DIR --select PyFlameButton,PyFlameTreeWidget

To install:

    Nothing to install. Lives in _pyflame_lib/_qt_test_ui/. Importing it does nothing.

Updates:

    v1.0.0 11.17.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import argparse
import ast
import datetime
import enum
import gc
import importlib.util
import inspect
import io
import linecache
import os
import re
import subprocess
import sys
import tempfile
import traceback
import types

import shiboken6
from PySide6 import QtCore, QtGui, QtWidgets

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'PyFlame Widget Tester'
SCRIPT_VERSION = 'v1.0.0'

APP_PATH = os.path.abspath(os.path.dirname(__file__))
DEFAULT_LIB_PATH = os.path.join(os.path.dirname(APP_PATH), 'pyflame_lib.py')
SHARED_FONTS_PATH = os.path.join(os.path.dirname(APP_PATH), 'assets', 'fonts')
STUBS_PATH = os.path.join(os.path.dirname(os.path.dirname(APP_PATH)), '_claude_python', 'stubs')

# Module name the library is loaded under, so it never clashes with a script's copy
LIB_MODULE_NAME = 'pyflame_lib_widget_tester'

# Classes that are opened as windows (Open button) instead of shown in the preview
WINDOW_CLASSES = (
    'PyFlameWindow',
    'PyFlameMessageWindow',
    'PyFlameOptionWindow',
    'PyFlameInputDialog',
    'PyFlamePasswordWindow',
    'PyFlameProgressWindow',
    )

# Classes known when this app was written. Anything else found in the library is marked (new)
KNOWN_CLASSES = (
    'PyFlameToolTip',
    'PyFlameConfig',
    'PyFlameButton',
    'PyFlameCheckBox',
    'PyFlameEntry',
    'PyFlameEntryBrowser',
    'PyFlameImageWidget',
    'PyFlameImageGallery',
    'PyFlameLabel',
    'PyFlameListWidget',
    'PyFlamePushButton',
    'PyFlameMenu',
    'PyFlameColorMenu',
    'PyFlameTokenMenu',
    'PyFlameSlider',
    'PyFlameTable',
    'PyFlameTabWidget',
    'PyFlameTextEdit',
    'PyFlameTextBrowser',
    'PyFlameTreeWidget',
    'PyFlameProgressBarWidget',
    'PyFlameButtonGroup',
    'PyFlameCheckBoxGroup',
    'PyFlameHorizontalLine',
    'PyFlameVerticalLine',
    'PyFlameGridLayout',
    'PyFlameHBoxLayout',
    'PyFlameVBoxLayout',
    ) + WINDOW_CLASSES

# Classes left out of the widget list. None today: PyFlameConfig is shown, pointed at a temp folder
EXCLUDED_CLASSES = ()

# Companion widgets a widget-type argument can be given (built with defaults, shown in the preview)
NEW_WIDGET_CHOICES = (
    'PyFlameButton',
    'PyFlameEntry',
    )

PREVIEW_BACKGROUND = 'rgb(40, 40, 40)'

# Seconds one class may take in the self-test before it fails
CHILD_TIMEOUT = 120

# Literal text that becomes a logging function for Callable arguments
LOG_MARKER = 'log'

EMPTY = inspect.Parameter.empty

# ==============================================================================
# [Library Loading]
# ==============================================================================

def read_lib_version(lib_path: str) -> str:
    """
    Read Lib Version
    ================

    Read the `Version:` line from a PyFlameLib file.

    Args
    ----
        lib_path (str): Path to the library file.

    Returns
    -------
        version (str): Version text, or 'unknown'.
    """

    try:
        with open(lib_path, 'r', encoding='utf-8') as lib_file:
            for line in lib_file:
                match = re.match(r'^Version:\s*(\S+)', line)
                if match:
                    return match.group(1)
    except OSError:
        pass

    return 'unknown'

def find_fonts_folder(lib_path: str) -> str | None:
    """
    Find Fonts Folder
    =================

    Find the Montserrat fonts for a library file: next to it (`<lib folder>/assets/fonts`),
    in its script folder (`<script>/assets/fonts` for `<script>/lib/<file>`), else the
    shared `_pyflame_lib/assets/fonts`.

    Args
    ----
        lib_path (str): Path to the library file.

    Returns
    -------
        fonts_path (str | None): Fonts folder, or None if none was found.
    """

    lib_folder = os.path.dirname(os.path.abspath(lib_path))
    candidates = [
        os.path.join(lib_folder, 'assets', 'fonts'),
        os.path.join(os.path.dirname(lib_folder), 'assets', 'fonts'),
        SHARED_FONTS_PATH,
        ]

    for path in candidates:
        if os.path.isfile(os.path.join(path, 'Montserrat-Regular.ttf')):
            return path

    return None

def install_fake_flame(temp_path: str) -> str:
    """
    Install Fake Flame
    ==================

    Put a fake `flame` module in sys.modules. Uses the shared stubs
    (`_claude_python/stubs/stub_loader.py`) when they are there, else a tiny local fake
    that only answers `get_version()`.

    Args
    ----
        temp_path (str): Temp folder for the fake project root.

    Returns
    -------
        source (str): Which fake was installed.
    """

    if 'flame' in sys.modules:
        return 'existing flame module'

    loader_path = os.path.join(STUBS_PATH, 'stub_loader.py')
    if os.path.isfile(loader_path):
        stub_loader = sys.modules.get('_stubs_stub_loader')
        if stub_loader is None:
            spec = importlib.util.spec_from_file_location('_stubs_stub_loader', loader_path)
            stub_loader = importlib.util.module_from_spec(spec)
            sys.modules['_stubs_stub_loader'] = stub_loader
            spec.loader.exec_module(stub_loader)
        project_root = os.path.join(temp_path, 'flame_project')
        os.makedirs(project_root, exist_ok=True)
        stub_loader.install_fake_flame(project_root=project_root)

        return f'shared stubs ({STUBS_PATH})'

    # Local fallback: only what the library needs at import
    fake = types.ModuleType('flame')
    fake.get_version = lambda: '2027.2'

    # pyflame.print and raise_*_error write to Flame's console
    fake.messages = types.SimpleNamespace(show_in_console=lambda *args, **kwargs: None)
    sys.modules['flame'] = fake

    return 'local minimal fake (stubs folder not found)'

def install_sudo_guard() -> None:
    """
    Install Sudo Guard
    ==================

    Block any subprocess command that uses sudo, for this process only. The library's
    password test and package installs run sudo; the tester must never do that.
    """

    original_popen = subprocess.Popen
    if getattr(original_popen, '_widget_tester_guard', False):
        return

    class GuardedPopen(original_popen):
        _widget_tester_guard = True

        def __init__(self, args, *popen_args, **popen_kwargs) -> None:

            command = args if isinstance(args, (list, tuple)) else str(args).split()
            if any(os.path.basename(str(part)) == 'sudo' for part in command):
                raise PermissionError(f'{SCRIPT_NAME}: sudo is blocked in the widget tester: {args}')
            super().__init__(args, *popen_args, **popen_kwargs)

    subprocess.Popen = GuardedPopen

def load_library(lib_path: str, temp_path: str) -> types.ModuleType:
    """
    Load Library
    ============

    Load a PyFlameLib file under LIB_MODULE_NAME. The module's `__file__` is pointed at
    `<temp>/pyflame_widget_tester/lib/`, so the library's SCRIPT_PATH is a temp folder:
    its fonts come from a symlink there to the real fonts folder, and anything the
    library writes under SCRIPT_PATH (config, temp folders) lands in temp.

    Args
    ----
        lib_path (str): Path to the library file.

        temp_path (str): Temp folder for this run.

    Returns
    -------
        module (module): The loaded library.

    Raises
    ------
        Exception:
            Whatever the library raises while importing.
    """

    script_root = os.path.join(temp_path, 'pyflame_widget_tester')
    os.makedirs(os.path.join(script_root, 'lib'), exist_ok=True)
    os.makedirs(os.path.join(script_root, 'assets'), exist_ok=True)

    # Link the fonts instead of copying them
    fonts_path = find_fonts_folder(lib_path)
    fonts_link = os.path.join(script_root, 'assets', 'fonts')
    if fonts_path and not os.path.exists(fonts_link):
        os.symlink(fonts_path, fonts_link)

    spec = importlib.util.spec_from_file_location(LIB_MODULE_NAME, lib_path)
    module = importlib.util.module_from_spec(spec)
    module.__file__ = os.path.join(script_root, 'lib', f'{LIB_MODULE_NAME}.py')
    sys.modules[LIB_MODULE_NAME] = module
    try:
        spec.loader.exec_module(module)
    except Exception:
        sys.modules.pop(LIB_MODULE_NAME, None)
        raise

    module._widget_tester_fonts = fonts_path

    return module

def make_sample_files(temp_path: str) -> dict:
    """
    Make Sample Files
    =================

    Make small sample files in the temp folder: six PNG images, a CSV file and an
    empty folder to browse. Never uses the user's files.

    Args
    ----
        temp_path (str): Temp folder for this run.

    Returns
    -------
        files (dict): Paths: 'images' (folder), 'image' (one PNG), 'csv', 'browse', 'config'.
    """

    images_path = os.path.join(temp_path, 'sample_images')
    browse_path = os.path.join(temp_path, 'sample_browse')
    os.makedirs(images_path, exist_ok=True)
    os.makedirs(browse_path, exist_ok=True)

    colors = [
        (180, 60, 60),
        (60, 140, 70),
        (50, 90, 170),
        (170, 130, 40),
        (120, 70, 150),
        (60, 140, 150),
        ]
    for number, rgb in enumerate(colors, start=1):
        image = QtGui.QImage(320, 180, QtGui.QImage.Format_RGB32)
        image.fill(QtGui.QColor(*rgb))
        painter = QtGui.QPainter(image)
        painter.setPen(QtGui.QColor(240, 240, 240))
        painter.drawRect(4, 4, 311, 171)
        painter.drawText(image.rect(), QtCore.Qt.AlignCenter, f'Sample {number:02d}')
        painter.end()
        image.save(os.path.join(images_path, f'sample_{number:02d}.png'))

    csv_path = os.path.join(temp_path, 'sample_table.csv')
    with open(csv_path, 'w', encoding='utf-8') as csv_file:
        csv_file.write('Shot,Frames,Notes\nPYT_0010,48,First shot\nPYT_0020,96,Second shot\nPYT_0030,24,Third shot\n')

    return {
        'images': images_path,
        'image': os.path.join(images_path, 'sample_01.png'),
        'csv': csv_path,
        'browse': browse_path,
        'config': os.path.join(temp_path, 'config', 'config.json'),
        }

def sample_values(class_name: str, lib, files: dict) -> dict:
    """
    Sample Values
    =============

    Sample editor values per class, for arguments whose library default would be empty
    or useless. Every Callable argument is also connected to the log in sample mode.
    Values are editor values: widget arguments take a choice ('new PyFlameButton',
    'tester window', 'None'), the rest Python values.

    Args
    ----
        class_name (str): Class name.

        lib (module): Loaded library (for enums).

        files (dict): Sample file paths from make_sample_files.

    Returns
    -------
        values (dict): Argument name to editor value.
    """

    color = getattr(lib, 'Color', None)
    blue = getattr(color, 'BLUE', None)
    gray = getattr(color, 'GRAY', None)
    context_menu = {'Rename': LOG_MARKER, 'Delete': LOG_MARKER}

    samples = {
        'PyFlameToolTip': {
            'parent_widget': 'new PyFlameButton',
            'text': 'Tooltip text',
            'delay': 1,
            },
        'PyFlameConfig': {
            'config_values': {'name': 'test', 'count': 3, 'enabled': True},
            'config_path': files['config'],
            'script_name': 'Widget Tester',
            },
        'PyFlameButton': {
            'text': 'Button',
            'tooltip': 'Button tooltip',
            },
        'PyFlameEntry': {
            'text': 'Entry text',
            'placeholder_text': 'Placeholder',
            },
        'PyFlameEntryBrowser': {
            'path': files['browse'],
            'placeholder_text': 'Click to browse',
            'browser_ext': ['png', 'jpg'],
            },
        'PyFlameImageWidget': {
            'image': files['image'],
            'show_info': True,
            'show_border': True,
            },
        'PyFlameImageGallery': {
            'folder': files['images'],
            'columns': 3,
            'show_info': True,
            },
        'PyFlameLabel': {
            'text': 'Label text',
            },
        'PyFlameListWidget': {
            'items': ['Item 1', 'Item 2', 'Item 3', 'Item 4'],
            'header': 'Items',
            'draggable': True,
            'context_menu': context_menu,
            },
        'PyFlamePushButton': {
            'text': 'Push Button',
            },
        'PyFlameCheckBox': {
            'text': 'Check Box',
            },
        'PyFlameMenu': {
            'text': 'Option 1',
            'menu_options': ['Option 1', 'Option 2', 'Option 3'],
            },
        'PyFlameTokenMenu': {
            'token_dict': {'Project Name': '<ProjectName>', 'Shot Name': '<ShotName>', 'User Name': '<UserName>'},
            'token_dest': 'new PyFlameEntry',
            },
        'PyFlameSlider': {
            'min_value': 0,
            'max_value': 100,
            'start_value': 25,
            'rate': 10,
            },
        'PyFlameTable': {
            'csv_file_path': files['csv'],
            },
        'PyFlameTabWidget': {
            'tab_names': ['Tab 1', 'Tab 2', 'Tab 3'],
            },
        'PyFlameTextEdit': {
            'text': 'Line one of the text.\nLine two of the text.\nLine three of the text.',
            },
        'PyFlameTextBrowser': {
            'text': 'Text browser text.\nhttps://example.com',
            },
        'PyFlameTreeWidget': {
            'column_names': ['Name'],
            'tree_dict': {
                'Shots': {
                    'PYT_0010': {'Plates': {}, 'Renders': {}},
                    'PYT_0020': {'Plates': {}, 'Renders': {}},
                    },
                },
            'draggable': True,
            'context_menu': context_menu,
            },
        'PyFlameProgressBarWidget': {
            'total_tasks': 100,
            'processing_task': 40,
            },
        'PyFlameButtonGroup': {
            'button_group': ['Option A', 'Option B', 'Option C'],
            },
        'PyFlameCheckBoxGroup': {
            'check_box_group': ['Option A', 'Option B', 'Option C'],
            },
        'PyFlameHorizontalLine': {
            'width': 300,
            },
        'PyFlameVerticalLine': {
            'height': 100,
            },
        'PyFlameGridLayout': {
            'columns': 2,
            'rows': 2,
            },
        'PyFlameWindow': {
            'title': 'PyFlameWindow Test',
            },
        'PyFlameMessageWindow': {
            'message': 'This is a test message.',
            'title': 'Message',
            },
        'PyFlameOptionWindow': {
            'message': 'Pick an option.',
            'title': 'Options',
            'buttons': {1: {'text': 'Cancel', 'color': gray}, 4: {'text': 'Ok', 'color': blue}},
            'cancel_button': 1,
            },
        'PyFlameInputDialog': {
            'text': 'Input text',
            },
        'PyFlamePasswordWindow': {
            'text': 'Widget tester: the password is never tested with sudo.',
            },
        'PyFlameProgressWindow': {
            'total_tasks': 5,
            },
        }

    return samples.get(class_name, {})

# ==============================================================================
# [Values]
# ==============================================================================

def to_literal(value, callables_as_log: bool = True) -> str:
    """
    To Literal
    ==========

    Turn a value into text the literal editor can read back: enums as `Color.BLUE`,
    callables as 'log' (or `<function name>` for display), Qt objects as `<ClassName>`.

    Args
    ----
        value (Any):
            Value to show.

        callables_as_log (bool):
            Write callables as 'log' (editor text) instead of `<function name>` (display text).

    Returns
    -------
        text (str): Literal text.
    """

    if isinstance(value, enum.Enum):
        return f'{type(value).__name__}.{value.name}'
    if isinstance(value, dict):
        return '{' + ', '.join(f'{to_literal(key, callables_as_log)}: {to_literal(item, callables_as_log)}' for key, item in value.items()) + '}'
    if isinstance(value, list):
        return '[' + ', '.join(to_literal(item, callables_as_log) for item in value) + ']'
    if isinstance(value, tuple):
        if len(value) == 1:
            return f'({to_literal(value[0], callables_as_log)},)'

        return '(' + ', '.join(to_literal(item, callables_as_log) for item in value) + ')'
    if isinstance(value, QtCore.QObject):
        return f'<{type(value).__name__}>'
    if callable(value) and not isinstance(value, type):
        if callables_as_log:
            return repr(LOG_MARKER)

        return f'<function {getattr(value, "__name__", type(value).__name__)}>'

    return repr(value)

def check_literal_node(node, namespace: dict) -> None:
    """
    Check Literal Node
    ==================

    Allow only literals and `Enum.MEMBER` names from the library in an expression.

    Args
    ----
        node (ast.AST): Parsed expression.

        namespace (dict): Allowed names (the library's enums).

    Raises
    ------
        ValueError:
            If the expression holds anything else (calls, operators, other names).
    """

    allowed = (
        ast.Expression,
        ast.Constant,
        ast.List,
        ast.Tuple,
        ast.Dict,
        ast.Set,
        ast.Load,
        ast.UnaryOp,
        ast.USub,
        ast.UAdd,
        ast.Name,
        ast.Attribute,
        )

    for child in ast.walk(node):
        if not isinstance(child, allowed):
            raise ValueError(f'not allowed in a literal: {type(child).__name__}')
        if isinstance(child, ast.Name) and child.id not in namespace:
            raise ValueError(f'unknown name: {child.id} (only literals and library enums like Color.BLUE)')
        if isinstance(child, ast.Attribute) and (not isinstance(child.value, ast.Name) or child.attr.startswith('_')):
            raise ValueError('only Enum.MEMBER names are allowed')

def safe_eval(text: str, namespace: dict) -> object:
    """
    Safe Eval
    =========

    Read a Python literal that may also use library enums (`Color.BLUE`).

    Args
    ----
        text (str): Literal text.

        namespace (dict): Allowed names (the library's enums).

    Returns
    -------
        value (Any): The value.

    Raises
    ------
        ValueError:
            If the text isn't a literal.
    """

    try:
        tree = ast.parse(text.strip() or 'None', mode='eval')
    except SyntaxError as e:
        raise ValueError(f'syntax error: {e.msg}')
    check_literal_node(tree, namespace)

    return eval(compile(tree, '<literal>', 'eval'), {'__builtins__': {}}, dict(namespace))

def parse_call_args(text: str, namespace: dict) -> tuple:
    """
    Parse Call Args
    ===============

    Read method arguments typed like a call: `'a', 2, flag=True`.

    Args
    ----
        text (str): Argument text.

        namespace (dict): Allowed names (the library's enums).

    Returns
    -------
        args (tuple): (positional list, keyword dict).

    Raises
    ------
        ValueError:
            If the text isn't literal arguments.
    """

    try:
        call = ast.parse(f'_call({text})', mode='eval').body
    except SyntaxError as e:
        raise ValueError(f'syntax error: {e.msg}')

    args = []
    for node in call.args:
        if isinstance(node, ast.Starred):
            raise ValueError('*args is not supported')
        check_literal_node(node, namespace)
        args.append(eval(compile(ast.Expression(node), '<arg>', 'eval'), {'__builtins__': {}}, dict(namespace)))

    kwargs = {}
    for keyword in call.keywords:
        if keyword.arg is None:
            raise ValueError('**kwargs is not supported')
        check_literal_node(keyword.value, namespace)
        kwargs[keyword.arg] = eval(compile(ast.Expression(keyword.value), '<arg>', 'eval'), {'__builtins__': {}}, dict(namespace))

    return args, kwargs

def split_top_level(text: str, separator: str) -> list:
    """
    Split Top Level
    ===============

    Split type-hint text on a separator that isn't inside brackets.

    Args
    ----
        text (str): Type-hint text.

        separator (str): Separator character.

    Returns
    -------
        parts (list): Stripped parts.
    """

    parts = []
    depth = 0
    current = ''
    for character in text:
        if character in '[(':
            depth += 1
        elif character in '])':
            depth -= 1
        if character == separator and depth == 0:
            parts.append(current.strip())
            current = ''
        else:
            current += character
    parts.append(current.strip())

    return parts

class ParamSpec:
    """
    Param Spec
    ==========

    What editor an argument or property gets, worked out from its type hint and default.

    Kinds: bool, int, float, str, enum, callable, widget, literal.
    """

    def __init__(self, name: str, annotation, default, lib) -> None:

        self.name = name
        self.default = default
        self.enum_class = None
        self.choices = []

        # Widget a property holds now (the 'current widget' choice in the Properties tab)
        self.current_value = None

        if annotation is EMPTY or annotation is None:
            text = ''
        elif isinstance(annotation, str):
            text = annotation
        else:
            text = getattr(annotation, '__name__', str(annotation))
        self.annotation = text.strip('"\'')

        # Optional: `X | None`, `Optional[X]` or a None default
        core = self.annotation
        if core.startswith('Optional[') and core.endswith(']'):
            core = core[len('Optional['):-1]
            optional = True
        else:
            optional = False
        parts = [part for part in split_top_level(core, '|') if part]
        if 'None' in parts:
            optional = True
            parts = [part for part in parts if part != 'None']
        core = ' | '.join(parts)
        self.optional = optional or default is None
        self.core = core

        self.kind = self._kind(core, default, lib)

    def _kind(self, core: str, default, lib) -> str:
        """
        Kind
        ====

        Pick the editor kind.

        Args
        ----
            core (str): Type-hint text without None.

            default (Any): Default value or EMPTY.

            lib (module): Loaded library.

        Returns
        -------
            kind (str): Editor kind.
        """

        compact = core.replace(' ', '')
        lowered = compact.lower()

        if 'Callable' in compact and not lowered.startswith(('dict', 'list', 'tuple')):
            return 'callable'
        if compact == 'bool':
            return 'bool'
        if compact == 'int':
            return 'int'
        if compact in ('float', 'int|float', 'float|int'):
            return 'float'
        if compact == 'str':
            return 'str'
        enum_class = getattr(lib, compact, None) if compact.isidentifier() else None
        if isinstance(enum_class, enum.EnumMeta):
            self.enum_class = enum_class

            return 'enum'

        # Widget references (parents, token destinations, tooltip targets)
        named_classes = [name for name in re.findall(r'PyFlame\w+', compact) if inspect.isclass(getattr(lib, name, None))]
        if self.name in ('parent', 'parent_widget', 'window_to_hide') or 'QWidget' in compact or named_classes:
            self.choices = ['None', 'tester window', 'preview area']
            for name in list(NEW_WIDGET_CHOICES) + named_classes:
                if name not in WINDOW_CLASSES and f'new {name}' not in self.choices:
                    self.choices.append(f'new {name}')

            return 'widget'

        # No usable hint: go by the default
        if not compact and default is not EMPTY and default is not None:
            if isinstance(default, bool):
                return 'bool'
            if isinstance(default, int):
                return 'int'
            if isinstance(default, float):
                return 'float'
            if isinstance(default, str):
                return 'str'
            if isinstance(default, enum.Enum):
                self.enum_class = type(default)

                return 'enum'

        return 'literal'

# ==============================================================================
# [Editors]
# ==============================================================================

class ParamEditor(QtWidgets.QWidget):
    """
    Param Editor
    ============

    Plain PySide6 editor for one argument or property. `get_value()` returns an editor
    value (Callable → True/False, widget → choice text, literal → Python value); the
    tester resolves it into the real argument.
    """

    changed = QtCore.Signal()

    def __init__(self, spec: ParamSpec, namespace: dict) -> None:

        super().__init__()

        self.spec = spec
        self.namespace = namespace
        self.none_box = None
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        kind = spec.kind
        if kind == 'bool':
            self.input = QtWidgets.QCheckBox()
            self.input.toggled.connect(self._emit_changed)
        elif kind == 'int':
            self.input = QtWidgets.QSpinBox()
            self.input.setRange(-1000000, 1000000)
            self.input.valueChanged.connect(self._emit_changed)
        elif kind == 'float':
            self.input = QtWidgets.QDoubleSpinBox()
            self.input.setRange(-1000000.0, 1000000.0)
            self.input.setDecimals(3)
            self.input.valueChanged.connect(self._emit_changed)
        elif kind == 'str':
            self.input = QtWidgets.QLineEdit()
            self.input.textChanged.connect(self._emit_changed)
        elif kind == 'enum':
            self.input = QtWidgets.QComboBox()
            if spec.optional:
                self.input.addItem('None')
            for member in spec.enum_class:
                self.input.addItem(member.name)
            self.input.currentIndexChanged.connect(self._emit_changed)
        elif kind == 'callable':
            self.input = QtWidgets.QCheckBox('connect to log')
            self.input.toggled.connect(self._emit_changed)
        elif kind == 'widget':
            self.input = QtWidgets.QComboBox()
            self.input.addItems(spec.choices)
            self.input.currentIndexChanged.connect(self._emit_changed)
        else:
            self.input = QtWidgets.QPlainTextEdit()
            self.input.setFixedHeight(54)
            self.input.setLineWrapMode(QtWidgets.QPlainTextEdit.WidgetWidth)
            self.input.textChanged.connect(self._emit_changed)
        layout.addWidget(self.input, 1)

        # None checkbox for optional simple values
        if spec.optional and kind in ('int', 'float', 'str'):
            self.none_box = QtWidgets.QCheckBox('None')
            self.none_box.toggled.connect(self._none_toggled)
            layout.addWidget(self.none_box)

    def _emit_changed(self, *args) -> None:
        """
        Emit Changed
        ============

        Emit `changed` for any input signal (whatever arguments it sends).
        """

        self.changed.emit()

    def _none_toggled(self, checked: bool) -> None:
        """
        None Toggled
        ============

        Disable the input while None is checked.

        Args
        ----
            checked (bool): None checkbox state.
        """

        self.input.setEnabled(not checked)
        self.changed.emit()

    def set_value(self, value) -> None:
        """
        Set Value
        =========

        Show a value in the editor. Values the editor can't show go to literal text or
        the closest setting.

        Args
        ----
            value (Any): Editor value.
        """

        kind = self.spec.kind
        blocked = self.blockSignals(True)
        try:
            if self.none_box is not None:
                self.none_box.setChecked(value is None)
                self.input.setEnabled(value is not None)
            if kind == 'bool':
                self.input.setChecked(bool(value))
            elif kind == 'int':
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    self.input.setValue(int(value))
            elif kind == 'float':
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    self.input.setValue(float(value))
            elif kind == 'str':
                self.input.setText('' if value is None else str(value))
            elif kind == 'enum':
                name = value.name if isinstance(value, enum.Enum) else 'None'
                index = self.input.findText(name)
                self.input.setCurrentIndex(max(index, 0))
            elif kind == 'callable':
                self.input.setChecked(bool(value))
            elif kind == 'widget':
                if isinstance(value, str) and value in self.spec.choices:
                    self.input.setCurrentIndex(self.spec.choices.index(value))
                else:
                    self.input.setCurrentIndex(0)
            else:
                self.input.setPlainText(to_literal(value))
                self.input.setStyleSheet('')
        finally:
            self.blockSignals(blocked)

    def get_value(self) -> object:
        """
        Get Value
        =========

        Read the editor value.

        Returns
        -------
            value (Any): Editor value.

        Raises
        ------
            ValueError:
                If literal text can't be read.
        """

        kind = self.spec.kind
        if self.none_box is not None and self.none_box.isChecked():
            return None
        if kind in ('bool', 'callable'):
            return self.input.isChecked()
        if kind in ('int', 'float'):
            return self.input.value()
        if kind == 'str':
            return self.input.text()
        if kind == 'enum':
            text = self.input.currentText()
            if text == 'None':
                return None

            return self.spec.enum_class[text]
        if kind == 'widget':
            return self.input.currentText()

        try:
            value = safe_eval(self.input.toPlainText(), self.namespace)
        except ValueError as e:
            self.input.setStyleSheet('QPlainTextEdit { border: 1px solid rgb(200, 60, 60); }')
            self.input.setToolTip(str(e))
            raise ValueError(f'{self.spec.name}: {e}')
        self.input.setStyleSheet('')
        self.input.setToolTip('')

        return value

class DropTarget(QtWidgets.QLabel):
    """
    Drop Target
    ===========

    Accepts any drag and logs what it got: source widget class, its currentItem text,
    mime formats and text. Takes a copy when the drag allows it, so a dragged item is
    never removed from its source by this box.
    """

    def __init__(self, log) -> None:

        super().__init__('Drop target: drag anything here')

        self.log = log
        self.setAcceptDrops(True)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMinimumHeight(56)
        self._set_highlight(False)

    def _set_highlight(self, on: bool) -> None:
        """
        Set Highlight
        =============

        Show whether a drag is over the box.

        Args
        ----
            on (bool): Drag is over the box.
        """

        border = 'rgb(0, 110, 175)' if on else 'rgb(110, 110, 110)'
        self.setStyleSheet(f'QLabel {{ color: rgb(170, 170, 170); border: 2px dashed {border}; background-color: rgb(30, 30, 30); }}')

    def dragEnterEvent(self, event) -> None:

        self._set_highlight(True)
        event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:

        event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:

        self._set_highlight(False)

    def dropEvent(self, event) -> None:

        self._set_highlight(False)
        source = event.source()
        item_text = None
        current_item = getattr(source, 'currentItem', None)
        if callable(current_item):
            item = current_item()
            if isinstance(item, QtWidgets.QTreeWidgetItem):
                item_text = item.text(0)
            elif item is not None and hasattr(item, 'text'):
                item_text = item.text()
        mime = event.mimeData()

        # Copy if the drag allows it, so the source keeps its item
        if event.possibleActions() & QtCore.Qt.CopyAction:
            event.setDropAction(QtCore.Qt.CopyAction)
            event.accept()
        else:
            event.acceptProposedAction()

        self.log.write('drop', f'source={type(source).__name__ if source is not None else None}, currentItem={item_text!r}, '
                               f'formats={list(mime.formats())}, text={mime.text()!r}, action={event.dropAction().name}')

# ==============================================================================
# [Log]
# ==============================================================================

class Log:
    """
    Log
    ===

    Log lines for the log panel. `errors` collects error entries (the self-test reads it).
    """

    def __init__(self) -> None:

        self.lines = []
        self.errors = []
        self.widget = None

    def write(self, kind: str, text: str) -> None:
        """
        Write
        =====

        Add a log line.

        Args
        ----
            kind (str): Entry type (callback, prop, method, error, info, drop, print).

            text (str): Text.
        """

        line = f'{datetime.datetime.now().strftime("%H:%M:%S")} [{kind}] {text}'
        self.lines.append(line)
        if kind == 'error':
            self.errors.append(text)
        if self.widget is not None:
            self.widget.appendPlainText(line)

class StdoutTee(io.TextIOBase):
    """
    Stdout Tee
    ==========

    Pass printed text through and copy each line to the log (the library prints its
    messages and warnings).
    """

    def __init__(self, original, log: Log) -> None:

        super().__init__()

        self.original = original
        self.log = log
        self.buffer_text = ''

    def write(self, text: str) -> int:

        if self.original is not None:
            self.original.write(text)
        self.buffer_text += text
        while '\n' in self.buffer_text:
            line, self.buffer_text = self.buffer_text.split('\n', 1)
            if line.strip():
                self.log.write('print', line.rstrip())

        return len(text)

    def flush(self) -> None:

        if self.original is not None:
            self.original.flush()

# ==============================================================================
# [Main Script]
# ==============================================================================

class WidgetTester(QtWidgets.QMainWindow):
    """
    Widget Tester
    =============

    Main window: widget list (left), preview, drop target and log (centre), constructor
    settings, properties and methods (right).
    """

    def __init__(self, lib, lib_path: str, lib_version: str, files: dict, log: Log, flame_source: str) -> None:

        super().__init__()

        self.lib = lib
        self.lib_path = lib_path
        self.lib_version = lib_version
        self.files = files
        self.log = log
        self.namespace = {name: value for name, value in vars(lib).items() if isinstance(value, enum.EnumMeta)}

        self.class_names = find_classes(lib)
        self.current_class = None
        self.instance = None
        self.companions = []
        self.open_windows = []
        self.specs = []
        self.editors = {}
        self.property_rows = {}
        self.loading_form = False
        self.last_error = ''
        self.last_exception = None

        # Self-test helpers: close modal windows automatically and grab them first
        self.grab_modal_path = None
        self.modal_hook = None
        self.modal_timer = QtCore.QTimer(self)
        self.modal_timer.setInterval(40)
        # A lambda, not the bound method: PySide6 6.5 can lose a named slot after errors in paint events
        self.modal_timer.timeout.connect(lambda: self._close_modal())

        self.rebuild_timer = QtCore.QTimer(self)
        self.rebuild_timer.setSingleShot(True)
        self.rebuild_timer.setInterval(400)
        self.rebuild_timer.timeout.connect(self._auto_rebuild)

        self._password_guard()
        self._build_ui(flame_source)

        if self.class_names:
            self.class_list.setCurrentRow(0)

    # ==============================================================================

    def _password_guard(self) -> None:
        """
        Password Guard
        ==============

        In this process only, replace PyFlamePasswordWindow._test_password so Confirm never
        tests the password with sudo (the sudo guard would block it anyway). The typed
        password is accepted without a test and never logged.
        """

        password_class = getattr(self.lib, 'PyFlamePasswordWindow', None)
        if password_class is None or not hasattr(password_class, '_test_password'):
            return

        log = self.log

        def _test_password(window_self) -> str | None:

            password = window_self.password_entry.text
            log.write('info', f'PyFlamePasswordWindow: password not tested (widget tester), {len(password or "")} characters typed')

            return password or None

        password_class._test_password = _test_password

    def _build_ui(self, flame_source: str) -> None:
        """
        Build UI
        ========

        Build the tester window from plain PySide6 widgets.

        Args
        ----
            flame_source (str): Which fake flame module is in use (for the log).
        """

        self.setWindowTitle(f'{SCRIPT_NAME} {SCRIPT_VERSION} - {os.path.basename(self.lib_path)} {self.lib_version}')
        self.resize(1560, 980)

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Widget list
        self.class_list = QtWidgets.QListWidget()
        self.class_list.setFixedWidth(240)
        for name in self.class_names:
            label = name
            if name in WINDOW_CLASSES:
                label += '   (window)'
            if name not in KNOWN_CLASSES:
                label += '   (new)'
            item = QtWidgets.QListWidgetItem(label)
            item.setData(QtCore.Qt.UserRole, name)
            self.class_list.addItem(item)
        self.class_list.currentItemChanged.connect(self._class_selected)

        # Preview
        self.preview_title = QtWidgets.QLabel('Preview')
        self.open_button = QtWidgets.QPushButton('Open')
        self.open_button.clicked.connect(self.open_window)
        self.close_windows_button = QtWidgets.QPushButton('Close Open Windows')
        self.close_windows_button.clicked.connect(self.close_open_windows)
        self.preview_host = QtWidgets.QWidget()
        self.preview_host.setObjectName('preview_host')
        self.preview_host.setStyleSheet(f'QWidget#preview_host {{ background-color: {PREVIEW_BACKGROUND}; }}')
        self.preview_layout = QtWidgets.QVBoxLayout(self.preview_host)
        self.preview_layout.setContentsMargins(20, 20, 20, 20)
        self.preview_layout.setSpacing(10)
        self.preview_layout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.preview_scroll = QtWidgets.QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_scroll.setWidget(self.preview_host)
        self.preview_scroll.setStyleSheet(f'QScrollArea {{ background-color: {PREVIEW_BACKGROUND}; }}')
        self.drop_target = DropTarget(self.log)

        # Log
        self.log_view = QtWidgets.QPlainTextEdit()
        self.log_view.setReadOnly(True)
        self.log_view.setMaximumBlockCount(5000)
        self.log_view.setFont(QtGui.QFontDatabase.systemFont(QtGui.QFontDatabase.FixedFont))
        self.log.widget = self.log_view
        clear_log_button = QtWidgets.QPushButton('Clear')
        clear_log_button.clicked.connect(self.log_view.clear)

        # Constructor settings
        self.form_host = QtWidgets.QWidget()
        self.form_layout = QtWidgets.QFormLayout(self.form_host)
        self.form_layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        form_scroll = QtWidgets.QScrollArea()
        form_scroll.setWidgetResizable(True)
        form_scroll.setWidget(self.form_host)
        self.build_button = QtWidgets.QPushButton('Rebuild')
        self.build_button.clicked.connect(self.build_or_open)
        defaults_button = QtWidgets.QPushButton('Reset (Library Defaults)')
        defaults_button.clicked.connect(lambda: self._reset_form(samples=False))
        samples_button = QtWidgets.QPushButton('Sample Data')
        samples_button.clicked.connect(lambda: self._reset_form(samples=True))
        self.auto_rebuild_box = QtWidgets.QCheckBox('Auto-rebuild on change')
        self.auto_rebuild_box.setChecked(True)

        # Properties
        self.props_host = QtWidgets.QWidget()
        self.props_layout = QtWidgets.QGridLayout(self.props_host)
        self.props_layout.setAlignment(QtCore.Qt.AlignTop)
        props_scroll = QtWidgets.QScrollArea()
        props_scroll.setWidgetResizable(True)
        props_scroll.setWidget(self.props_host)
        refresh_props_button = QtWidgets.QPushButton('Get All')
        refresh_props_button.clicked.connect(self.refresh_property_values)

        # Methods
        self.method_list = QtWidgets.QListWidget()
        self.method_list.currentItemChanged.connect(self._method_selected)
        self.method_signature = QtWidgets.QLabel('')
        self.method_signature.setWordWrap(True)
        self.method_signature.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self.method_args = QtWidgets.QLineEdit()
        self.method_args.setPlaceholderText("Arguments as in a call: 'a', 2, flag=True (Callable args: 'log')")
        self.method_args.returnPressed.connect(self.call_method)
        call_button = QtWidgets.QPushButton('Call')
        call_button.clicked.connect(self.call_method)

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        preview_header = QtWidgets.QHBoxLayout()
        preview_header.addWidget(self.preview_title, 1)
        preview_header.addWidget(self.open_button)
        preview_header.addWidget(self.close_windows_button)
        preview_panel = QtWidgets.QWidget()
        preview_panel_layout = QtWidgets.QVBoxLayout(preview_panel)
        preview_panel_layout.setContentsMargins(0, 0, 0, 0)
        preview_panel_layout.addLayout(preview_header)
        preview_panel_layout.addWidget(self.preview_scroll, 1)
        preview_panel_layout.addWidget(self.drop_target)

        log_header = QtWidgets.QHBoxLayout()
        log_header.addWidget(QtWidgets.QLabel('Log'), 1)
        log_header.addWidget(clear_log_button)
        log_panel = QtWidgets.QWidget()
        log_panel_layout = QtWidgets.QVBoxLayout(log_panel)
        log_panel_layout.setContentsMargins(0, 0, 0, 0)
        log_panel_layout.addLayout(log_header)
        log_panel_layout.addWidget(self.log_view)

        centre = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        centre.addWidget(preview_panel)
        centre.addWidget(log_panel)
        centre.setSizes([620, 300])

        constructor_tab = QtWidgets.QWidget()
        constructor_layout = QtWidgets.QVBoxLayout(constructor_tab)
        constructor_layout.addWidget(form_scroll, 1)
        constructor_layout.addWidget(self.auto_rebuild_box)
        constructor_buttons = QtWidgets.QHBoxLayout()
        constructor_buttons.addWidget(defaults_button)
        constructor_buttons.addWidget(samples_button)
        constructor_buttons.addWidget(self.build_button)
        constructor_layout.addLayout(constructor_buttons)

        props_tab = QtWidgets.QWidget()
        props_tab_layout = QtWidgets.QVBoxLayout(props_tab)
        props_tab_layout.addWidget(props_scroll, 1)
        props_tab_layout.addWidget(refresh_props_button)

        methods_tab = QtWidgets.QWidget()
        methods_layout = QtWidgets.QVBoxLayout(methods_tab)
        methods_layout.addWidget(self.method_list, 1)
        methods_layout.addWidget(self.method_signature)
        methods_layout.addWidget(self.method_args)
        methods_layout.addWidget(call_button)

        self.settings_tabs = QtWidgets.QTabWidget()
        self.settings_tabs.addTab(constructor_tab, 'Constructor')
        self.settings_tabs.addTab(props_tab, 'Properties')
        self.settings_tabs.addTab(methods_tab, 'Methods')
        self.settings_tabs.setMinimumWidth(470)

        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        main_splitter.addWidget(self.class_list)
        main_splitter.addWidget(centre)
        main_splitter.addWidget(self.settings_tabs)
        main_splitter.setSizes([240, 820, 500])
        self.setCentralWidget(main_splitter)

        font = getattr(self.lib, 'FONT', None)
        font_text = font.family() if isinstance(font, QtGui.QFont) else 'unknown'
        self.statusBar().showMessage(f'Library: {self.lib_path}   |   Version: {self.lib_version}   |   Font: {font_text}')
        self.log.write('info', f'Loaded {self.lib_path} (Version {self.lib_version}), font {font_text}, fonts folder {getattr(self.lib, "_widget_tester_fonts", None)}')
        self.log.write('info', f'Fake flame: {flame_source}. Temp folder: {os.path.dirname(self.files["images"])}')

    # ==============================================================================

    def _class_selected(self, current, previous) -> None:
        """
        Class Selected
        ==============

        Show the selected class.

        Args
        ----
            current (QListWidgetItem): Selected item.

            previous (QListWidgetItem): Previous item.
        """

        if current is not None:
            self.select_class(current.data(QtCore.Qt.UserRole))

    def select_class(self, name: str, auto_build: bool = True) -> None:
        """
        Select Class
        ============

        Make a class current: build its settings form with sample data, its methods
        list, and (for non-window classes) build the preview.

        Args
        ----
            name (str): Class name.

            auto_build (bool): Build the preview right away (not for window classes).
        """

        self.close_open_windows()
        self.clear_preview()
        self.current_class = name
        cls = getattr(self.lib, name)
        is_window = name in WINDOW_CLASSES

        self.preview_title.setText(f'Preview: {name}' + ('   (window class: use Open)' if is_window else ''))
        self.open_button.setVisible(is_window)
        self.close_windows_button.setVisible(is_window)
        self.build_button.setText('Open' if is_window else 'Rebuild')

        self._build_form(cls)
        self._reset_form(samples=True, build=False)
        self._fill_methods(cls)

        if auto_build and not is_window:
            self.build()
        else:
            self.refresh_properties()

    def _build_form(self, cls) -> None:
        """
        Build Form
        ==========

        Make one editor per constructor argument, from inspect.signature.

        Args
        ----
            cls (type): Selected class.
        """

        while self.form_layout.rowCount():
            self.form_layout.removeRow(0)
        self.specs = []
        self.editors = {}

        try:
            signature = inspect.signature(cls.__init__)
        except (TypeError, ValueError) as e:
            self.log.write('error', f'{cls.__name__}: no signature: {e}')

            return

        for parameter in list(signature.parameters.values())[1:]:
            if parameter.kind in (parameter.VAR_POSITIONAL, parameter.VAR_KEYWORD):
                continue
            spec = ParamSpec(parameter.name, parameter.annotation, parameter.default, self.lib)
            editor = ParamEditor(spec, self.namespace)
            editor.changed.connect(self._form_changed)
            default_text = 'required' if parameter.default is EMPTY else to_literal(parameter.default, callables_as_log=False)
            label = QtWidgets.QLabel(parameter.name + (' *' if parameter.default is EMPTY else ''))
            label.setToolTip(f'Type: {spec.annotation or "?"}\nDefault: {default_text}\nEditor: {spec.kind}')
            editor.setToolTip(label.toolTip())
            self.form_layout.addRow(label, editor)
            self.specs.append(spec)
            self.editors[spec.name] = editor

    def _reset_form(self, samples: bool, build: bool = True) -> None:
        """
        Reset Form
        ==========

        Put the library defaults (and, with samples, the sample data) in the form.

        Args
        ----
            samples (bool): Apply sample data on top of the defaults.

            build (bool): Rebuild afterwards if auto-rebuild is on.
        """

        self.loading_form = True
        try:
            sample = sample_values(self.current_class, self.lib, self.files)
            for spec in self.specs:
                # Required arguments have no library default, so they always get the sample value
                if spec.name in sample and (samples or spec.default is EMPTY):
                    value = sample[spec.name]
                elif samples and spec.kind == 'callable':
                    value = True
                elif spec.default is not EMPTY:
                    value = False if spec.kind == 'callable' else spec.default
                elif spec.kind == 'widget':
                    value = 'None'
                elif spec.kind == 'str':
                    value = ''
                else:
                    value = None
                self.editors[spec.name].set_value(value)
        finally:
            self.loading_form = False

        if build:
            self._form_changed()

    def _form_changed(self) -> None:
        """
        Form Changed
        ============

        Start the auto-rebuild timer (not for window classes, which only open on Open).
        """

        if self.loading_form or self.current_class in WINDOW_CLASSES:
            return
        if self.auto_rebuild_box.isChecked():
            self.rebuild_timer.start()

    def _auto_rebuild(self) -> None:
        """
        Auto Rebuild
        ============

        Rebuild after an edit.
        """

        self.build()

    # ==============================================================================

    def make_logger(self, label: str) -> types.FunctionType:
        """
        Make Logger
        ===========

        Make a function that logs each call and its arguments.

        Args
        ----
            label (str): Name shown in the log (Class.argument).

        Returns
        -------
            callback (function): Logging function taking any arguments.
        """

        log = self.log

        def callback(*args, **kwargs) -> None:

            parts = [to_literal(arg, callables_as_log=False) for arg in args]
            parts += [f'{key}={to_literal(value, callables_as_log=False)}' for key, value in kwargs.items()]
            log.write('callback', f'{label}({", ".join(parts)})')

        # Built outside the f-string: Python 3.11 allows no backslash inside an f-string expression
        safe_label = re.sub(r'\W', '_', label)
        callback.__name__ = f'log_{safe_label}'

        return callback

    def convert_callables(self, value, annotation: str, label: str) -> object:
        """
        Convert Callables
        =================

        For Callable hints: 'log' becomes a logging function, also as dict or list values
        (`{'Rename': 'log'}` → `{'Rename': <log function>}`).

        Args
        ----
            value (Any): Value read from an editor.

            annotation (str): Type-hint text.

            label (str): Name for the log.

        Returns
        -------
            value (Any): Converted value.
        """

        if 'Callable' not in (annotation or ''):
            return value
        if value == LOG_MARKER:
            return self.make_logger(label)
        if isinstance(value, dict):
            return {key: self.make_logger(f'{label}[{key!r}]') if item == LOG_MARKER else item for key, item in value.items()}
        if isinstance(value, list):
            return [self.make_logger(f'{label}[{index}]') if item == LOG_MARKER else item for index, item in enumerate(value)]

        return value

    def resolve(self, spec: ParamSpec, raw, label: str) -> object:
        """
        Resolve
        =======

        Turn an editor value into the real argument: logging functions, companion
        widgets, PyFlamePushButtons for a list of button names.

        Args
        ----
            spec (ParamSpec): Argument spec.

            raw (Any): Editor value.

            label (str): Name for the log.

        Returns
        -------
            value (Any): Argument value.
        """

        if spec.kind == 'callable':
            return self.make_logger(label) if raw else None

        if spec.kind == 'widget':
            if raw in (None, 'None'):
                return None
            if raw == 'current widget':
                return spec.current_value
            if raw == 'tester window':
                return self
            if raw == 'preview area':
                return self.preview_host
            if isinstance(raw, str) and raw.startswith('new '):
                return self.add_companion(raw[4:])

            return raw

        if spec.kind == 'literal':
            # A list of names for a button group becomes PyFlamePushButtons
            if spec.name == 'button_group' and isinstance(raw, list) and all(isinstance(item, str) for item in raw):
                return [self.add_companion('PyFlamePushButton', text=item) for item in raw]

            # A list of names for a check box group becomes PyFlameCheckBoxes, the first one checked
            if spec.name == 'check_box_group' and isinstance(raw, list) and all(isinstance(item, str) for item in raw):
                return [self.add_companion('PyFlameCheckBox', text=item, checked=(index == 0)) for index, item in enumerate(raw)]

            return self.convert_callables(raw, spec.annotation, label)

        return raw

    def add_companion(self, class_name: str, **kwargs) -> object:
        """
        Add Companion
        =============

        Build a library widget with defaults (or kwargs) and show it in the preview,
        for arguments that need a widget (token destination, tooltip target, buttons).

        Args
        ----
            class_name (str): Library class name.

            kwargs: Constructor arguments.

        Returns
        -------
            widget (QWidget): The widget.
        """

        cls = getattr(self.lib, class_name)
        if not kwargs:
            if class_name == 'PyFlameButton':
                kwargs = {'text': 'Companion Button'}
            elif class_name == 'PyFlameEntry':
                kwargs = {'text': ''}
        widget = cls(**kwargs)
        self.companions.append(widget)
        if isinstance(widget, QtWidgets.QWidget):
            self.preview_layout.addWidget(widget)
        self.log.write('info', f'Companion {class_name} added to the preview')

        return widget

    def collect_kwargs(self) -> dict:
        """
        Collect Kwargs
        ==============

        Read every editor and resolve the constructor arguments.

        Returns
        -------
            kwargs (dict): Constructor arguments.

        Raises
        ------
            ValueError:
                If an editor's literal text can't be read.
        """

        raw_values = {spec.name: self.editors[spec.name].get_value() for spec in self.specs}

        return {spec.name: self.resolve(spec, raw_values[spec.name], f'{self.current_class}.{spec.name}') for spec in self.specs}

    # ==============================================================================

    def clear_preview(self) -> None:
        """
        Clear Preview
        =============

        Remove the built widget and its companions from the preview.
        """

        while self.preview_layout.count():
            item = self.preview_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()
        self.instance = None
        self.companions = []

    def build(self, variant: str = '') -> bool:
        """
        Build
        =====

        Build the selected (non-window) class from the form and show it in the preview.
        Errors go to the log with the traceback.

        Args
        ----
            variant (str): Name of this build for the log (self-test).

        Returns
        -------
            built (bool): True if the constructor worked.
        """

        if self.current_class in WINDOW_CLASSES:
            return self.open_window(variant)

        self.rebuild_timer.stop()
        self.clear_preview()
        cls = getattr(self.lib, self.current_class)
        suffix = f' [{variant}]' if variant else ''

        try:
            kwargs = self.collect_kwargs()
        except ValueError as e:
            self.last_error = str(e)
            self.log.write('error', f'{self.current_class}{suffix}: {e}')

            return False

        try:
            instance = cls(**kwargs)
        except Exception as e:
            self.last_exception = e
            self.last_error = f'{type(e).__name__}: {e}'
            self.log.write('error', f'{self.current_class}{suffix} constructor failed:\n{traceback.format_exc()}')
            self.refresh_properties()

            return False

        self.instance = instance
        self._place_instance(instance)
        self.log.write('info', f'Built {self.current_class}{suffix}')
        self.refresh_properties()

        return True

    def build_or_open(self) -> None:
        """
        Build Or Open
        =============

        Rebuild button: build a widget or open a window class.
        """

        if self.current_class in WINDOW_CLASSES:
            self.open_window()
        else:
            self.build()

    def _place_instance(self, instance) -> None:
        """
        Place Instance
        ==============

        Show a built object in the preview: widgets as they are, layouts in a host widget
        with sample buttons, other objects as a note.

        Args
        ----
            instance (Any): Built object.
        """

        if isinstance(instance, QtWidgets.QLayout):
            host = QtWidgets.QWidget()
            host.setLayout(instance)
            button_class = getattr(self.lib, 'PyFlameButton', None)
            for index in range(4):
                button = button_class(text=f'Button {index + 1}') if button_class else QtWidgets.QPushButton(f'Button {index + 1}')
                if isinstance(instance, QtWidgets.QGridLayout):
                    instance.addWidget(button, index // 2, index % 2)
                else:
                    instance.addWidget(button)
            self.preview_layout.addWidget(host)
        elif isinstance(instance, QtWidgets.QWidget):
            self.preview_layout.addWidget(instance)
        else:
            note = QtWidgets.QLabel(f'{type(instance).__name__} is not a widget. See the Properties and Methods tabs.')
            note.setStyleSheet('QLabel { color: rgb(170, 170, 170); }')
            self.preview_layout.addWidget(note)

    def _window_widgets(self, instance) -> list:
        """
        Window Widgets
        ==============

        Find the top-level windows of a window-class object (the object itself or its
        QDialog attributes).

        Args
        ----
            instance (Any): Window-class object.

        Returns
        -------
            windows (list): Top-level widgets.
        """

        if isinstance(instance, QtWidgets.QWidget):
            return [instance]

        windows = []
        for value in vars(instance).values():
            if isinstance(value, QtWidgets.QWidget) and shiboken6.isValid(value) and value.isWindow() and value not in windows:
                windows.append(value)

        return windows

    def open_window(self, variant: str = '') -> bool:
        """
        Open Window
        ===========

        Open a window class with the form's settings. Modal windows block here until
        closed; then the result (confirmed, selected, text...) goes to the log.

        Args
        ----
            variant (str): Name of this build for the log (self-test).

        Returns
        -------
            opened (bool): True if the constructor worked.
        """

        self.close_open_windows()
        self.clear_preview()
        cls = getattr(self.lib, self.current_class)
        suffix = f' [{variant}]' if variant else ''

        try:
            kwargs = self.collect_kwargs()
        except ValueError as e:
            self.last_error = str(e)
            self.log.write('error', f'{self.current_class}{suffix}: {e}')

            return False

        self.log.write('info', f'Opening {self.current_class}{suffix}')
        try:
            instance = cls(**kwargs)
        except Exception as e:
            self.last_exception = e
            self.last_error = f'{type(e).__name__}: {e}'
            self.log.write('error', f'{self.current_class}{suffix} constructor failed:\n{traceback.format_exc()}')
            self.refresh_properties()

            return False

        self.instance = instance

        # Give a plain PyFlameWindow some content and a way to close it
        if self.current_class == 'PyFlameWindow' and hasattr(instance, 'grid_layout'):
            try:
                instance.grid_layout.addWidget(self.lib.PyFlameLabel(text='PyFlameWindow test content'), 0, 0, 1, 2)
                instance.grid_layout.addWidget(self.lib.PyFlameButton(text='Close', connect=instance.close), 2, 3)
            except Exception as e:
                self.log.write('error', f'PyFlameWindow test content: {e}')

        # Windows still open after the constructor are non-modal
        for window in self._window_widgets(instance):
            if shiboken6.isValid(window) and window.isVisible():
                self.open_windows.append(window)

        self.log.write('info', f'{self.current_class}{suffix} returned {type(instance).__name__}: {self._result_text(instance)}')
        self.refresh_properties()

        return True

    def _result_text(self, instance) -> str:
        """
        Result Text
        ===========

        Read the result properties of a window object. Passwords are never shown.

        Args
        ----
            instance (Any): Window-class object.

        Returns
        -------
            text (str): `name=value` pairs.
        """

        parts = []
        for name in ('confirmed', 'selected', 'text', 'username', 'password'):
            if not isinstance(getattr(type(instance), name, None), property):
                continue
            try:
                value = getattr(instance, name)
            except Exception as e:
                parts.append(f'{name}=<{type(e).__name__}: {e}>')
                continue
            if name == 'password':
                value = None if value is None else f'<{len(value)} characters>'
            parts.append(f'{name}={value!r}')
        if self.open_windows:
            parts.append('window still open (non-modal)')

        return ', '.join(parts) or 'no result properties'

    def close_open_windows(self) -> None:
        """
        Close Open Windows
        ==================

        Close non-modal windows the tester opened.
        """

        for window in self.open_windows:
            if shiboken6.isValid(window):
                window.close()
        self.open_windows = []

    def _close_modal(self) -> None:
        """
        Close Modal
        ===========

        Self-test: grab and close the active modal window.
        """

        window = QtWidgets.QApplication.activeModalWidget()

        # A PyFlameWindow is shown before exec_(), so Qt may not list it as modal: look for WA_ShowModal
        if window is None:
            for widget in reversed(QtWidgets.QApplication.topLevelWidgets()):
                if widget is not self and widget.isVisible() and widget.testAttribute(QtCore.Qt.WA_ShowModal):
                    window = widget
                    break
        if window is None:
            return
        if self.modal_hook is not None:
            hook = self.modal_hook
            self.modal_hook = None
            hook(window)
        if self.grab_modal_path:
            window.grab().save(self.grab_modal_path)
            self.grab_modal_path = None
        if isinstance(window, QtWidgets.QDialog):
            window.reject()
        else:
            window.close()

    # ==============================================================================

    def _lib_members(self, cls, test) -> list:
        """
        Lib Members
        ===========

        Members of a class and its bases that are defined in the library module.

        Args
        ----
            cls (type): Class.

            test (function): Filter for the raw class attribute.

        Returns
        -------
            members (list): (name, raw attribute) sorted by name.
        """

        found = {}
        for base in cls.__mro__:
            if getattr(base, '__module__', '') != self.lib.__name__:
                continue
            for name, value in vars(base).items():
                if name not in found and test(name, value):
                    found[name] = value

        return sorted(found.items())

    def lib_properties(self, cls) -> list:
        """
        Lib Properties
        ==============

        Python properties of a class (and its library bases).

        Args
        ----
            cls (type): Class.

        Returns
        -------
            properties (list): (name, property) pairs.
        """

        return self._lib_members(cls, lambda name, value: isinstance(value, property))

    def lib_methods(self, cls) -> list:
        """
        Lib Methods
        ===========

        Public methods of a class (and its library bases), without Qt event-handler and
        paint overrides (`*Event`, `eventFilter`, `draw*` methods Qt itself has), which
        can't be called with literal arguments.

        Args
        ----
            cls (type): Class.

        Returns
        -------
            methods (list): (name, function) pairs.
        """

        qt_bases = [base for base in cls.__mro__ if getattr(base, '__module__', '').startswith(('PySide6', 'shiboken6'))]

        def is_event_override(name: str) -> bool:
            """
            Is Event Override
            =================

            Check for a Qt event-handler or paint override.

            Args
            ----
                name (str): Method name.

            Returns
            -------
                override (bool): True for an override to leave out.
            """

            if name.endswith('Event') or name == 'eventFilter':
                return True

            return name.startswith('draw') and any(hasattr(base, name) for base in qt_bases)

        return self._lib_members(cls, lambda name, value: not name.startswith('_') and not is_event_override(name) and (inspect.isfunction(value) or isinstance(value, (staticmethod, classmethod))))

    def _property_spec(self, name: str, prop: property, current) -> ParamSpec:
        """
        Property Spec
        =============

        Editor spec for a property, from its setter's value hint (else the getter's return hint).

        Args
        ----
            name (str): Property name.

            prop (property): Property object.

            current (Any): Current value (EMPTY if it couldn't be read).

        Returns
        -------
            spec (ParamSpec): Spec.
        """

        annotation = EMPTY
        if prop.fset is not None:
            try:
                parameters = list(inspect.signature(prop.fset).parameters.values())
                if len(parameters) > 1:
                    annotation = parameters[1].annotation
            except (TypeError, ValueError):
                pass
        if annotation is EMPTY and prop.fget is not None:
            annotation = getattr(prop.fget, '__annotations__', {}).get('return', EMPTY)

        spec = ParamSpec(name, annotation, EMPTY if current is EMPTY else current, self.lib)
        if current is None:
            spec.optional = True

        return spec

    def refresh_properties(self) -> None:
        """
        Refresh Properties
        ==================

        Rebuild the Properties tab for the current object: name, current value, editor,
        Set and Get.
        """

        while self.props_layout.count():
            item = self.props_layout.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self.property_rows = {}

        if self.current_class is None:
            return
        cls = getattr(self.lib, self.current_class)
        properties = self.lib_properties(cls)

        if self.instance is None:
            note = 'Build the widget first.' if self.current_class not in WINDOW_CLASSES else 'Open the window first (properties are read after it closes, or while a non-modal window is open).'
            self.props_layout.addWidget(QtWidgets.QLabel(f'{len(properties)} properties. {note}'), 0, 0, 1, 4)

            return

        for row, (name, prop) in enumerate(properties):
            current = self._read_property(name, quiet=True)
            spec = self._property_spec(name, prop, current)
            editor_value = current

            # A widget-valued property starts on its current widget, not None
            if spec.kind == 'widget' and current is not None and current is not EMPTY:
                spec.choices.insert(0, 'current widget')
                spec.current_value = current
                editor_value = 'current widget'

            name_label = QtWidgets.QLabel(name)
            name_label.setToolTip(f'Type: {spec.annotation or "?"}\nEditor: {spec.kind}')
            value_label = QtWidgets.QLabel()
            value_label.setFixedWidth(130)
            value_label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
            editor = ParamEditor(spec, self.namespace)
            if editor_value is not EMPTY:
                editor.set_value(editor_value if spec.kind != 'callable' else bool(editor_value))
            set_button = QtWidgets.QPushButton('Set')
            set_button.setEnabled(prop.fset is not None)
            set_button.clicked.connect(lambda checked=False, prop_name=name: self.set_property(prop_name))
            get_button = QtWidgets.QPushButton('Get')
            get_button.clicked.connect(lambda checked=False, prop_name=name: self.get_property(prop_name))
            if prop.fset is None:
                editor.setEnabled(False)
                name_label.setText(f'{name} (read only)')
            self.props_layout.addWidget(name_label, row, 0)
            self.props_layout.addWidget(value_label, row, 1)
            self.props_layout.addWidget(editor, row, 2)
            self.props_layout.addWidget(set_button, row, 3)
            self.props_layout.addWidget(get_button, row, 4)
            self.property_rows[name] = (spec, value_label, editor)
            self._show_value(name, current)

    def _read_property(self, name: str, quiet: bool = False) -> object:
        """
        Read Property
        =============

        Read a property from the current object.

        Args
        ----
            name (str): Property name.

            quiet (bool): Don't log errors.

        Returns
        -------
            value (Any): Value, or EMPTY on error.
        """

        try:
            return getattr(self.instance, name)
        except Exception as e:
            if not quiet:
                self.log.write('error', f'get {self.current_class}.{name}: {type(e).__name__}: {e}')

            return EMPTY

    def _show_value(self, name: str, value) -> None:
        """
        Show Value
        ==========

        Show a property value in its row.

        Args
        ----
            name (str): Property name.

            value (Any): Value or EMPTY.
        """

        if name not in self.property_rows:
            return
        label = self.property_rows[name][1]
        if value is EMPTY:
            text = '<error>'
        elif name == 'password' and isinstance(value, str):
            text = f'<{len(value)} characters>'
        else:
            text = to_literal(value, callables_as_log=False)
        label.setToolTip(text)
        label.setText(text if len(text) <= 22 else text[:20] + '...')

    def get_property(self, name: str) -> object:
        """
        Get Property
        ============

        Read a property, show it and log it.

        Args
        ----
            name (str): Property name.

        Returns
        -------
            value (Any): Value, or EMPTY on error.
        """

        value = self._read_property(name)
        if value is not EMPTY:
            shown = f'<{len(value)} characters>' if name == 'password' and isinstance(value, str) else to_literal(value, callables_as_log=False)
            self.log.write('prop', f'get {self.current_class}.{name} = {shown}')
        self._show_value(name, value)

        return value

    def refresh_property_values(self) -> None:
        """
        Refresh Property Values
        =======================

        Read every property again (Get All).
        """

        for name in self.property_rows:
            self.get_property(name)

    def set_property(self, name: str, value=EMPTY) -> bool:
        """
        Set Property
        ============

        Set a property on the live object (from its editor, or the given value), then
        read it back.

        Args
        ----
            name (str): Property name.

            value (Any): Value to set. Default: read the row's editor.

        Returns
        -------
            set_ok (bool): True if the setter didn't raise.
        """

        if value is EMPTY:
            if name not in self.property_rows:
                return False
            spec, value_label, editor = self.property_rows[name]
            try:
                raw = editor.get_value()
            except ValueError as e:
                self.log.write('error', f'set {self.current_class}.{name}: {e}')

                return False
            value = self.resolve(spec, raw, f'{self.current_class}.{name}')

        self.last_exception = None
        try:
            setattr(self.instance, name, value)
        except Exception as e:
            self.last_exception = e
            self.last_error = f'{type(e).__name__}: {e}'
            self.log.write('error', f'set {self.current_class}.{name} = {to_literal(value, callables_as_log=False)} failed:\n{traceback.format_exc()}')

            return False

        shown = '<hidden>' if name == 'password' else to_literal(value, callables_as_log=False)
        self.log.write('prop', f'set {self.current_class}.{name} = {shown}')
        self.get_property(name)

        return True

    # ==============================================================================

    def _fill_methods(self, cls) -> None:
        """
        Fill Methods
        ============

        List the class's public library methods.

        Args
        ----
            cls (type): Class.
        """

        self.method_list.clear()
        self.method_signature.setText('')
        for name, value in self.lib_methods(cls):
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.UserRole, name)
            self.method_list.addItem(item)

    def _method_selected(self, current, previous) -> None:
        """
        Method Selected
        ===============

        Show the selected method's signature.

        Args
        ----
            current (QListWidgetItem): Selected item.

            previous (QListWidgetItem): Previous item.
        """

        if current is None or self.current_class is None:
            return
        method = getattr(getattr(self.lib, self.current_class), current.data(QtCore.Qt.UserRole), None)
        try:
            self.method_signature.setText(f'{current.text()}{inspect.signature(method)}')
        except (TypeError, ValueError):
            self.method_signature.setText(current.text())

    def call_method(self) -> None:
        """
        Call Method
        ===========

        Call the selected method on the current object with the typed arguments. The
        result or exception goes to the log.
        """

        item = self.method_list.currentItem()
        if item is None:
            self.log.write('error', 'Select a method first.')

            return
        if self.instance is None:
            self.log.write('error', 'Build or open the widget first.')

            return
        name = item.data(QtCore.Qt.UserRole)
        label = f'{self.current_class}.{name}'

        try:
            args, kwargs = parse_call_args(self.method_args.text(), self.namespace)
        except ValueError as e:
            self.log.write('error', f'{label}: {e}')

            return

        method = getattr(self.instance, name)

        # 'log' for Callable parameters becomes a logging function
        try:
            bound = inspect.signature(method).bind_partial(*args, **kwargs)
            for parameter_name, value in list(bound.arguments.items()):
                parameter = inspect.signature(method).parameters[parameter_name]
                annotation = parameter.annotation if isinstance(parameter.annotation, str) else str(parameter.annotation)
                bound.arguments[parameter_name] = self.convert_callables(value, annotation, f'{label}.{parameter_name}')
            args, kwargs = list(bound.args), dict(bound.kwargs)
        except (TypeError, ValueError):
            pass

        try:
            result = method(*args, **kwargs)
        except Exception:
            self.log.write('error', f'{label} raised:\n{traceback.format_exc()}')

            return

        self.log.write('method', f'{label}({self.method_args.text()}) returned {to_literal(result, callables_as_log=False)}')
        self.refresh_property_values()

    def closeEvent(self, event) -> None:

        self.close_open_windows()
        super().closeEvent(event)

# ==============================================================================
# [Utilities]
# ==============================================================================

def find_classes(lib) -> list:
    """
    Find Classes
    ============

    Every PyFlame* class defined in the library, in file order, minus EXCLUDED_CLASSES.

    Args
    ----
        lib (module): Loaded library.

    Returns
    -------
        names (list): Class names.
    """

    return [
        name for name, value in vars(lib).items()
        if name.startswith('PyFlame') and inspect.isclass(value) and value.__module__ == lib.__name__ and name not in EXCLUDED_CLASSES
        ]

def process_events(log: Log) -> None:
    """
    Process Events
    ==============

    Process Qt events. PySide6 raises an exception from a Python event override (for
    example a library paintEvent) here; log it like a slot error instead of stopping.

    Args
    ----
        log (Log): Log.
    """

    try:
        QtWidgets.QApplication.processEvents()
    except Exception:
        log.write('error', 'Uncaught exception:\n' + traceback.format_exc())

def install_excepthook(log: Log) -> None:
    """
    Install Excepthook
    ==================

    Log exceptions raised in Qt slots (library callbacks, events) instead of only printing them.

    Args
    ----
        log (Log): Log.
    """

    original_hook = sys.excepthook

    def hook(exc_type, exc_value, exc_traceback) -> None:

        log.write('error', 'Uncaught exception:\n' + ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
        if original_hook is not None and sys.stdout is not sys.__stdout__:
            return
        original_hook(exc_type, exc_value, exc_traceback)

    sys.excepthook = hook

# ==============================================================================
# [Self Test]
# ==============================================================================

def find_window_owner(cls, window) -> object:
    """
    Find Window Owner
    =================

    Find the window-class object that owns a window, while its constructor is still
    blocked in exec_() (the object isn't returned yet).

    Args
    ----
        cls (type): Window class.

        window (QWidget): The open window.

    Returns
    -------
        owner (Any | None): The object, or None.
    """

    for candidate in gc.get_objects():
        if type(candidate) is cls and any(value is window for value in vars(candidate).values()):
            return candidate

    return None

def is_library_check(exception, lib_path: str, own_code=None) -> bool:
    """
    Is Library Check
    ================

    Check whether an exception is one of the library's own argument checks, so a refused
    value is a note and not a failure. True only for a TypeError, ValueError or
    RuntimeError whose innermost frame is in the library file and is either
    pyflame.raise_type_error / raise_value_error, or an explicit `raise` statement
    (in `own_code` only, when given). Anything else (a crash in a paint event, a Qt
    binding error, an AttributeError) is a failure.

    Args
    ----
        exception (Exception | None):
            The exception.

        lib_path (str):
            Library file path.

        own_code (code | None):
            Only accept an explicit raise in this code object (a property setter). None: anywhere in the library.

    Returns
    -------
        check (bool): True for a deliberate check.
    """

    if not isinstance(exception, (TypeError, ValueError, RuntimeError)):
        return False

    # Innermost frame of the traceback is where the raise happened
    frame_traceback = exception.__traceback__
    while frame_traceback is not None and frame_traceback.tb_next is not None:
        frame_traceback = frame_traceback.tb_next
    if frame_traceback is None:
        return False
    code = frame_traceback.tb_frame.f_code
    if os.path.realpath(code.co_filename) != os.path.realpath(lib_path):
        return False
    if code.co_name in ('raise_type_error', 'raise_value_error'):
        return True
    if own_code is not None and code is not own_code:
        return False

    return linecache.getline(code.co_filename, frame_traceback.tb_lineno).strip().startswith('raise ')

def test_properties(window: WidgetTester, instance, result: dict) -> None:
    """
    Test Properties
    ===============

    Read every library property of an object and set each settable one back to its own
    value (bools: flipped, then back). Errors go to result['failures'].

    Args
    ----
        window (WidgetTester): Tester window.

        instance (Any): Object to test.

        result (dict): Self-test result for the class.
    """

    previous_instance = window.instance
    window.instance = instance
    try:
        for prop_name, prop in window.lib_properties(type(instance)):
            result['properties'] += 1
            try:
                value = getattr(instance, prop_name)
            except Exception as e:
                result['failures'].append(f'[get {prop_name}] {type(e).__name__}: {e}')
                continue
            if prop.fset is None:
                continue
            values = [value, not value, value] if isinstance(value, bool) else [value]
            for new_value in values:
                window.last_error = ''
                if not window.set_property(prop_name, new_value):
                    message = f'[set {prop_name}={to_literal(new_value, callables_as_log=False)}] {window.last_error}'
                    # The setter refusing None on purpose (e.g. rows in columns mode) is a note, not a failure
                    if new_value is None and is_library_check(window.last_exception, window.lib_path, getattr(prop.fset, '__code__', None)):
                        result['notes'].append(f'refused {message}')
                    else:
                        result['failures'].append(message)
                    break
                read_back = window._read_property(prop_name, quiet=True)
                if isinstance(new_value, bool) and read_back != new_value:
                    result['failures'].append(f'[set {prop_name}={new_value}] read back {read_back!r}')
                    break
            process_events(window.log)
    finally:
        window.instance = previous_instance

def self_test_class(window: WidgetTester, name: str, grab_dir: str | None, skip: list) -> dict:
    """
    Self Test Class
    ===============

    Test one class: build with library defaults, toggle every bool argument, try every
    enum member, build with sample data, then read every property and set it back
    (bools flipped and back). Modal windows get their property test while open. Grab a
    PNG of the sample build if asked. `@start <variant>` lines go to the real stdout so a
    parent process can tell which variant crashed.

    Args
    ----
        window (WidgetTester): Tester window.

        name (str): Class name.

        grab_dir (str | None): Folder for PNGs.

        skip (list): Variant names not to run (they crashed the process before).

    Returns
    -------
        result (dict): 'failures' (list), 'notes' (list), 'builds' (int), 'properties' (int).
    """

    result = {'failures': [], 'notes': [], 'builds': 0, 'properties': 0}
    window.log.errors.clear()
    window.select_class(name, auto_build=False)
    cls = getattr(window.lib, name)

    def announce(variant: str) -> None:
        """
        Announce
        ========

        Tell a parent process which variant runs next.

        Args
        ----
            variant (str): Variant name.
        """

        sys.__stdout__.write(f'@start {variant}\n')
        sys.__stdout__.flush()

    def run(variant: str, set_up, fail: bool = True) -> bool:
        """
        Run
        ===

        One build with one form change.

        Args
        ----
            variant (str): Name of the variant.

            set_up (function): Changes the form.

            fail (bool): Count every constructor error as a failure. False: one of the library's own argument checks (is_library_check) is a note.

        Returns
        -------
            built (bool): True if the constructor worked.
        """

        if variant in skip:
            return False
        announce(variant)
        window.last_error = ''
        window.last_exception = None
        set_up()
        built = window.build(variant)
        process_events(window.log)
        window.close_open_windows()
        result['builds'] += 1
        if not built:
            message = f'[{variant}] {window.last_error}'
            if fail or not is_library_check(window.last_exception, window.lib_path):
                result['failures'].append(message)
            else:
                result['notes'].append(f'rejected {message}')

        return built

    def set_editor(spec_name: str, value) -> types.FunctionType:
        """
        Set Editor
        ==========

        Make a form change function.

        Args
        ----
            spec_name (str): Argument name.

            value (Any): Editor value.

        Returns
        -------
            set_up (function): Function applying sample data plus this value.
        """

        def set_up() -> None:

            window._reset_form(samples=True, build=False)
            window.editors[spec_name].set_value(value)

        return set_up

    run('library defaults', lambda: window._reset_form(samples=False, build=False))

    for spec in list(window.specs):
        if spec.kind == 'bool':
            current = window.editors[spec.name].get_value()
            run(f'{spec.name}={not current}', set_editor(spec.name, not current))
        elif spec.kind == 'enum':
            for member in spec.enum_class:
                run(f'{spec.name}={spec.enum_class.__name__}.{member.name}', set_editor(spec.name, member), fail=False)

    # Sample data last; modal windows get their property test while open
    grab_path = os.path.join(grab_dir, f'{name}.png') if grab_dir else None
    window.grab_modal_path = grab_path if name in WINDOW_CLASSES else None
    modal_tested = []

    def modal_hook(open_window) -> None:
        """
        Modal Hook
        ==========

        Property test on a modal window while it's open.

        Args
        ----
            open_window (QWidget): The modal window.
        """

        owner = find_window_owner(cls, open_window)
        if owner is not None:
            test_properties(window, owner, result)
            modal_tested.append(owner)

    built = False
    if 'sample data' not in skip:
        announce('sample data')
        window.modal_hook = modal_hook if name in WINDOW_CLASSES else None
        window.last_error = ''
        window._reset_form(samples=True, build=False)
        built = window.build('sample data')
        window.modal_hook = None
        process_events(window.log)
        result['builds'] += 1
        if not built:
            result['failures'].append(f'[sample data] {window.last_error}')

    if grab_path and built:
        if name in WINDOW_CLASSES:
            if window.open_windows:
                window.open_windows[0].grab().save(grab_path)
        else:
            window.preview_host.adjustSize()
            window.preview_host.grab().save(grab_path)
    window.grab_modal_path = None

    # Widgets and non-modal windows: property test on the live object
    if built and window.instance is not None and not modal_tested:
        if name in WINDOW_CLASSES and not window.open_windows:
            result['notes'].append('modal window: properties not tested while open (owner not found)')
        else:
            announce('properties')
            test_properties(window, window.instance, result)

    # Sample build failed (e.g. a library bug in a sample-only argument): test the properties on a library-defaults build
    if not built and name not in WINDOW_CLASSES and 'properties (library defaults)' not in skip:
        announce('properties (library defaults)')
        window._reset_form(samples=False, build=False)
        if window.build('library defaults, for properties'):
            result['notes'].append('properties tested on the library-defaults build (sample build failed)')
            test_properties(window, window.instance, result)

    window.close_open_windows()

    # Exceptions raised in Qt slots while testing, once each with a count
    slot_errors = {}
    for error in window.log.errors:
        if error.startswith('Uncaught exception'):
            last_line = error.strip().splitlines()[-1]
            slot_errors[last_line] = slot_errors.get(last_line, 0) + 1
    for error, count in slot_errors.items():
        result['failures'].append(f'[slot, {count}x] {error}')

    return result

def run_self_test_child(window: WidgetTester, name: str, grab_dir: str | None, skip: list) -> int:
    """
    Run Self Test Child
    ===================

    Test one class in this process and print its report lines. Library output is
    captured and shown for failures only.

    Args
    ----
        window (WidgetTester): Tester window.

        name (str): Class name.

        grab_dir (str | None): Folder for PNGs.

        skip (list): Variant names not to run.

    Returns
    -------
        exit_code (int): 0 if the class passed, else 1.
    """

    window.auto_rebuild_box.setChecked(False)
    window.modal_timer.start()
    window.show()

    report = sys.__stdout__
    if name not in window.class_names:
        report.write(f'MISSING {name}: not in the library\n')

        return 1

    captured = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = captured
    try:
        result = self_test_class(window, name, grab_dir, skip)
    except Exception:
        result = {'failures': [f'[tester] {traceback.format_exc()}'], 'notes': [], 'builds': 0, 'properties': 0}
    finally:
        sys.stdout = original_stdout
        window.modal_timer.stop()

    status = 'FAIL' if result['failures'] else 'PASS'
    new = '' if name in KNOWN_CLASSES else ' (new)'
    report.write(f'{status} {name}{new}: {result["builds"]} builds, {result["properties"]} properties, {len(result["notes"])} notes\n')
    for failure in result['failures']:
        report.write(f'    - {failure}\n')

    # Every note on its own line, so a wrongly filed error can be seen
    for note in result['notes']:
        report.write(f'    note: {note}\n')
    if result['failures']:
        output = [re.sub(r'\x1b\[[0-9;]*m', '', line) for line in captured.getvalue().splitlines() if line.strip()]
        if output:
            report.write('    library output (last 6 lines):\n')
            for line in output[-6:]:
                report.write(f'        {line}\n')
    report.flush()

    return 1 if result['failures'] else 0

def run_self_test(lib_path: str, lib_version: str, class_names: list, grab_dir: str | None, only: list | None, temp_path: str) -> int:
    """
    Run Self Test
    =============

    Test each class in its own child process, so a library crash (segfault) in one class
    doesn't stop the run. A crashed variant is reported and skipped, and the class runs
    again without it. A class that takes longer than CHILD_TIMEOUT seconds fails, with no retry.
    All children share the run's temp folder.

    Args
    ----
        lib_path (str): Library file.

        lib_version (str): Library version.

        class_names (list): Classes found in the library.

        grab_dir (str | None): Folder for PNGs.

        only (list | None): Class names to test.

        temp_path (str): Temp folder for this run, shared with the children.

    Returns
    -------
        exit_code (int): 0 if every class passed, else 1.
    """

    report = sys.__stdout__
    report.write(f'{SCRIPT_NAME} {SCRIPT_VERSION} self-test\n')
    report.write(f'Library: {lib_path} (Version {lib_version})\n\n')
    report.flush()

    names = [name for name in class_names if not only or name in only]
    missing = [name for name in (only or []) if name not in class_names]
    failed = []

    environment = dict(os.environ)
    environment.setdefault('QT_QPA_PLATFORM', 'offscreen')

    for name in names:
        skip = []
        crashes = []
        while True:
            command = [sys.executable, '-B', os.path.abspath(__file__), '--lib', lib_path, '--self-test-child', name, '--temp', temp_path]
            if grab_dir:
                command += ['--grab', grab_dir]
            for variant in skip:
                command += ['--skip', variant]
            timed_out = False
            try:
                process = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=CHILD_TIMEOUT)
                output, return_code = process.stdout, process.returncode
            except subprocess.TimeoutExpired as e:
                output = e.stdout.decode(errors='replace') if isinstance(e.stdout, bytes) else (e.stdout or '')
                return_code = 'timeout'
                timed_out = True

            started = [line[len('@start '):] for line in output.splitlines() if line.startswith('@start ')]
            report_lines = [line for line in output.splitlines() if not line.startswith('@start ')]

            # Crash: note the variant that was running, then run the class again without it
            if not timed_out and return_code not in (0, 1) and started and started[-1] not in skip and len(crashes) < 10:
                crashes.append(f'[{started[-1]}] process crashed (exit {return_code})')
                skip.append(started[-1])
                continue
            break

        # A timeout fails the class at once: no retries
        if timed_out:
            crashes.append(f'[{started[-1] if started else "start-up"}] timed out after {CHILD_TIMEOUT} s, class not finished')
        elif return_code not in (0, 1):
            crashes.append(f'[{started[-1] if started else "start-up"}] process crashed (exit {return_code}), class not finished')

        lines = [line for line in report_lines if line.strip() and not line.startswith('This plugin does not support')]
        if crashes:
            if lines and lines[0].startswith('PASS '):
                lines[0] = 'FAIL ' + lines[0][len('PASS '):]
            elif not lines or not lines[0].startswith(('PASS ', 'FAIL ')):
                lines.insert(0, f'FAIL {name}: did not finish')
            lines[1:1] = [f'    - {crash}' for crash in crashes]
        for line in lines:
            report.write(line + '\n')
        report.flush()
        if return_code != 0 or crashes:
            failed.append(name)

    for name in missing:
        report.write(f'MISSING {name}: not in the library\n')
    report.write(f'\nSummary: {len(names) - len(failed)} passed, {len(failed)} failed, {len(names)} classes\n')
    if grab_dir:
        report.write(f'Previews saved to {grab_dir}\n')
    report.flush()

    return 1 if failed or missing else 0

def take_screenshots(window: WidgetTester, out_dir: str, names: list) -> int:
    """
    Take Screenshots
    ================

    Save a PNG of the whole tester window with each class selected.

    Args
    ----
        window (WidgetTester): Tester window.

        out_dir (str): Output folder.

        names (list): Class names (default: the first class).

    Returns
    -------
        exit_code (int): 0 if every name was found, else 1.
    """

    os.makedirs(out_dir, exist_ok=True)
    window.show()
    exit_code = 0
    for name in names or window.class_names[:1]:
        if name not in window.class_names:
            sys.__stdout__.write(f'Not in the library: {name}\n')
            exit_code = 1
            continue
        window.class_list.setCurrentRow(window.class_names.index(name))
        for _ in range(5):
            process_events(window.log)
        path = os.path.join(out_dir, f'app_{name}.png')
        window.grab().save(path)
        sys.__stdout__.write(f'Saved {path}\n')

    return exit_code

# ==============================================================================
# [Entry Points]
# ==============================================================================

def main() -> int:
    """
    Main
    ====

    Parse arguments, load the library and run the tester, the self-test or screenshots.

    Returns
    -------
        exit_code (int): Process exit code.
    """

    parser = argparse.ArgumentParser(description=f'{SCRIPT_NAME}: try PyFlameLib widgets outside Flame.')
    parser.add_argument('--lib', default=DEFAULT_LIB_PATH, help='PyFlameLib file to load (default: ../pyflame_lib.py)')
    parser.add_argument('--self-test', action='store_true', help='test every class without a human, print a report, exit 0/1')
    parser.add_argument('--grab', metavar='DIR', help='self-test: save a PNG of each preview to DIR')
    parser.add_argument('--only', metavar='NAMES', help='self-test: comma-separated class names to test')
    parser.add_argument('--screenshot', metavar='DIR', help='save PNGs of the tester window to DIR and exit')
    parser.add_argument('--select', metavar='NAMES', help='screenshot: comma-separated class names to select')
    parser.add_argument('--self-test-child', metavar='NAME', help=argparse.SUPPRESS)
    parser.add_argument('--skip', action='append', default=[], help=argparse.SUPPRESS)
    parser.add_argument('--temp', help=argparse.SUPPRESS)
    args = parser.parse_args()

    # Nothing written next to the library or the stubs
    sys.dont_write_bytecode = True

    # Agent modes never show windows on screen
    if (args.self_test or args.self_test_child or args.screenshot) and 'QT_QPA_PLATFORM' not in os.environ:
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'

    lib_path = os.path.abspath(args.lib)
    if not os.path.isfile(lib_path):
        print(f'{SCRIPT_NAME}: library not found: {lib_path}')

        return 1
    lib_version = read_lib_version(lib_path)

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv[:1])
    install_sudo_guard()
    # Self-test children use their parent's temp folder, which must be one this app made
    if args.temp:
        temp_path = os.path.realpath(args.temp)
        system_temp = os.path.realpath(tempfile.gettempdir())
        if os.path.dirname(temp_path) != system_temp or not os.path.basename(temp_path).startswith('pyflame_widget_tester_') or not os.path.isdir(temp_path):
            print(f'{SCRIPT_NAME}: --temp must be a pyflame_widget_tester_* folder in {system_temp}: {args.temp}')
            return 1
    else:
        temp_path = tempfile.mkdtemp(prefix='pyflame_widget_tester_')

    try:
        flame_source = install_fake_flame(temp_path)
        lib = load_library(lib_path, temp_path)
    except Exception:
        print(f'{SCRIPT_NAME}: could not load {lib_path}:\n{traceback.format_exc()}')

        return 1

    # Parent self-test: one child process per class
    if args.self_test:
        if args.grab:
            os.makedirs(args.grab, exist_ok=True)
        only = [name.strip() for name in args.only.split(',')] if args.only else None

        return run_self_test(lib_path, lib_version, find_classes(lib), args.grab, only, temp_path)

    files = make_sample_files(temp_path)
    log = Log()
    install_excepthook(log)
    window = WidgetTester(lib, lib_path, lib_version, files, log, flame_source)

    if args.self_test_child:
        return run_self_test_child(window, args.self_test_child, args.grab, args.skip)

    if args.screenshot:
        names = [name.strip() for name in args.select.split(',')] if args.select else []

        return take_screenshots(window, args.screenshot, names)

    # Library prints go to the log too
    sys.stdout = StdoutTee(sys.__stdout__, log)
    window.show()

    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
