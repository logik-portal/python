# Logik Backdoor
# Copyright (c) 2026 Michael Vaglienty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: Logik Backdoor
Script Version: 1.0.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 10.05.26
Update Date: 10.05.26
 
License: GNU General Public License v3.0 (GPL-3.0) - see license file for details

Description:

    A bridge allowing other applications to control Flame using provided tools.

URL:

    https://logik-portal.com/scripts/logik_backdoor

Usage:

    Runs on Flame startup.

    Using the provided tools, other applications can interact with Flame.

    Tools:
        ping                       Confirm the bridge is alive.
        info                       Flame version, current project and workspace.
        list_batch_nodes           Nodes in the open Batch, optionally filtered by type.
        import_image_to_library    Import media into a Library, created if absent.
        import_image_to_batch      Import media onto a schematic reel in the open Batch.
        create_node                Create a Batch node, optionally loading a setup file.
        import_alembic             Create an Action node and import an Alembic file into it.
        reload_node_setup          Save a Batch node's setup and load it back into the same node.
        frame_node                 Select Batch nodes by name and frame the schematic on them.

    Tools are called by other applications using the logik_backdoor_client.py script.

    Each tool is its own file in the tools folder, loaded automatically at
    startup. To add a tool, add a file to the tools folder (tools/<name>.py) that defines a 
    function called <name> returning a dict, with a docstring describing it and an optional TIMEOUT 
    in seconds. 

Notes:

    This does not provide direct access to control Flame through python. The only access
    to Flame from the outside is through calling the tools provided here. Additional
    tools can be created/added to extend functionality.

Examples:

    These examples can be added to 3rd party application export options to import into Flame after 
    export is complete.

    To import an image sequence into a Library:

    ```
        import sys
        sys.path.insert(0, '/opt/Autodesk/shared/python/logik_backdoor')

        import logik_backdoor_client as backdoor

        # Check if Flame is running and the hook is installed. Only call a tool
        # when it is.
        if not backdoor.available():
            print('Flame is not running.')
        else:
            # Import an image sequence into a Library. The Library is created if it
            # is absent, reused if it already exists. timeout is in seconds: allow
            # plenty, since a large import can run for minutes and Flame answers
            # only when it ends. The Library name is optional and defaults to
            # 'Image_Imports'. Prefer image sequences to container video such as
            # .mov or .mp4, which Flame can hang on (see readme.md).
            result = backdoor.call(
                'import_image_to_library',
                timeout=600,
                path='/media/shot_0010/comp_v003.[1001-1100].exr',
                library_name='Image_Imports',
                )

            # Every call returns a dict. Errors arrive as {'ok': False, 'error': ...}
            # rather than as a raised exception, so test ok before reading the rest.
            if result['ok']:
                print(f"imported {result['count']} clip(s): {result['clips']}")
            else:
                print(f"import failed: {result['error']}")
    ```

    To import an image sequence onto a schematic reel in the open Batch:

    ```
        import sys
        sys.path.insert(0, '/opt/Autodesk/shared/python/logik_backdoor')

        import logik_backdoor_client as backdoor

        # Check if Flame is running and the hook is installed. Only call a tool
        # when it is.
        if not backdoor.available():
            print('Flame is not running.')
        else:
            # Import an image sequence onto a schematic reel in the open Batch.
            # Give the frame range in Flame's bracket notation so the frames import
            # as one clip rather than as several hundred single-frame clips. A
            # single image, a folder, or a list of any of these also works, here
            # and above. The reel name is optional and defaults to 'image_imports'.
            result = backdoor.call(
                'import_image_to_batch',
                timeout=600,
                path='/media/shot_0010/matte.[0001-0240].exr',
                reel_name='image_imports',
                )

            # Every call returns a dict. Errors arrive as {'ok': False, 'error': ...}
            # rather than as a raised exception, so test ok before reading the rest.
            if result['ok']:
                print(f"imported {result['count']} clip(s): {result['clips']}")
            else:
                print(f"import failed: {result['error']}")
    ```

To install:

    Copy script into /opt/Autodesk/shared/python/logik_backdoor

Updates:

    v1.0.0 10.05.26
        - Initial release.
"""
 
# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import importlib.util
import inspect
import json
import os
import time
import traceback
import socket
import uuid
from pathlib import Path

from lib.pyflame_lib_logik_backdoor import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Logik Backdoor'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

SESSION_FILE = 'session.json'
REQUEST_DIR = 'requests'
RESPONSE_DIR = 'responses'

# Responses that no client collected are swept after this long. It only has to
# exceed the longest client timeout, which is the 600 s of the import tools.
RESPONSE_TTL_SECONDS = 1800.0

# Registered tools by name, filled by load_tools()
TOOLS = {}

# Folder holding one file per tool, always resolved from SCRIPT_PATH so it
# follows the script wherever it is installed
TOOLS_PATH = os.path.join(SCRIPT_PATH, 'tools')

# Snapshot of the tool files TOOLS was last loaded from, so a later change to
# the folder can be spotted. See tools_signature().
_loaded_tools_signature = ()

# Timeout a tool gets when its file does not set TIMEOUT
DEFAULT_TOOL_TIMEOUT = 30.0

# Tools whose calls are not printed. Callers use them to check that Flame is
# up (Mocha does on every menu open), so printing them would flood the terminal.
QUIET_TOOLS = ('ping', 'info')

# Argument values longer than this are shortened when a call is printed.
PRINT_VALUE_LIMIT = 200

# Reply keys shown after a call finishes: the node made and the clips imported.
PRINT_RESULT_KEYS = ('node', 'count')

# Fast enough to feel immediate, slow enough that the cost of an empty scan is
# irrelevant next to everything else Flame does each frame.
POLL_INTERVAL_MS = 50

# The running service is anchored on Flame's QApplication instance, which lives
# for the whole session and survives the module re-import that a hook refresh
# triggers. Without this anchor the timer would be orphaned and garbage-collected
# on refresh, and the bridge would silently die until the next full restart.
_APP_SERVICE_ATTR = '_logik_backdoor_service'

# A ceiling on work per tick, so a flood of queued requests degrades into a
# short queue rather than a frozen interface.
MAX_REQUESTS_PER_TICK = 8

SWEEP_INTERVAL_SECONDS = 60.0

# The running _Service, or None
_service = None

# ==============================================================================
# [Paths]
# ==============================================================================

def home() -> Path:
    """
    Home
    ====

    Return the Logik Backdoor config directory, creating it 0700 if absent.

    State lives in a 'config' directory beside this file, so everything the script
    needs stays inside its own folder and is removed with it.

    LOGIK_BACKDOOR_HOME overrides that, which matters when the script folder is
    on read-only or network storage -- see the note in readme.md.

    Returns
    -------
        root (Path): The config directory.
    """

    override = os.environ.get('LOGIK_BACKDOOR_HOME')
    if override:
        root = Path(override).expanduser()
    else:
        root = Path(SCRIPT_PATH) / 'config'
    root.mkdir(parents=True, exist_ok=True)
    try:
        os.chmod(root, 0o700)
    except OSError:
        # Network shares frequently refuse chmod. Not fatal.
        pass

    return root

def sessions_root() -> Path:
    """
    Sessions Root
    =============

    Return the directory holding one subdirectory per running Flame.

    Returns
    -------
        root (Path): The sessions directory.
    """

    root = home() / 'sessions'
    root.mkdir(parents=True, exist_ok=True)

    return root

def session_dir(pid: int) -> Path:
    """
    Session Dir
    ===========

    Return the directory owned by the Flame process with this pid.

    Args
    ----
        pid (int): Process id of the Flame session.

    Returns
    -------
        session (Path): That session's directory.
    """

    return sessions_root() / str(pid)

def new_request_id() -> str:
    """
    New Request ID
    ==============

    Return an identifier unique enough to name one request/response pair.

    Returns
    -------
        request_id (str): A hex identifier.
    """

    return uuid.uuid4().hex

# ==============================================================================
# [File IO]
# ==============================================================================

def write_atomic(path: Path, payload: dict) -> None:
    """
    Write Atomic
    ============

    Publish payload as JSON at path so readers see all of it or none of it.

    The temporary file is created alongside the destination, because os.replace
    is only atomic within one filesystem. The pid in the temporary name keeps
    two writers from colliding on it.

    Args
    ----
        path (Path):
            Destination file.

        payload (dict):
            JSON-serialisable content.

    Raises
    ------
        Exception:
            Any failure to write, re-raised after the temporary file is removed.
    """

    temporary = path.with_name(f'.{path.name}.{os.getpid()}.tmp')
    try:
        with open(temporary, 'w', encoding='utf-8') as handle:
            json.dump(payload, handle)
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise

def read_json(path: Path) -> dict | None:
    """
    Read JSON
    =========

    Read a JSON object, returning None if it is missing or unreadable.

    Corrupt or truncated files are treated as absent rather than raising. The
    caller is always in a polling loop, so 'not yet' and 'never' collapse into
    the same handling.

    Args
    ----
        path (Path): File to read.

    Returns
    -------
        payload (dict | None): The object, or None if it could not be read.
    """

    try:
        with open(path, 'r', encoding='utf-8') as handle:
            payload = json.load(handle)
    except (OSError, ValueError):
        return None

    return payload if isinstance(payload, dict) else None

# ==============================================================================
# [Sessions]
# ==============================================================================

def pid_is_alive(pid: int) -> bool:
    """
    PID Is Alive
    ============

    Report whether a process still exists, without signalling it.

    EPERM means the process is alive but owned by another user, which must not
    be read as dead. That would delete a live session's directory.

    Args
    ----
        pid (int): Process id to test.

    Returns
    -------
        alive (bool): True if the process exists.
    """

    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False

    return True

def live_sessions() -> list:
    """
    Live Sessions
    =============

    Return metadata for every running Flame session, newest first.

    Directories owned by processes that have exited are deleted on the way past,
    so a crashed Flame never leaves litter for a human to clear.

    Returns
    -------
        sessions (list[dict]): One entry per live session, each carrying pid and dir.
    """

    sessions = []

    try:
        entries = sorted(sessions_root().iterdir())
    except OSError:
        return []

    for entry in entries:
        if not entry.name.isdigit() or not entry.is_dir():
            continue
        pid = int(entry.name)
        info = read_json(entry / SESSION_FILE) or {}

        # A session belonging to another machine cannot be judged by pid: the
        # same number means a different process there. Leave it strictly alone.
        host = info.get('host')
        if host is not None and host != socket.gethostname():
            continue

        if not pid_is_alive(pid):
            remove_tree(entry)
            continue
        info['pid'] = pid
        info['dir'] = str(entry)
        sessions.append(info)

    sessions.sort(key=lambda item: item.get('started', 0.0), reverse=True)

    return sessions

# ==============================================================================
# [Cleanup]
# ==============================================================================

def sweep_responses(directory: Path, now: float | None = None) -> None:
    """
    Sweep Responses
    ===============

    Delete responses old enough that no client can still be waiting.

    Responses are normally consumed and deleted by the client that asked for
    them. This only catches the case where that client timed out or was killed
    before it could collect.

    Args
    ----
        directory (Path):
            Response directory to sweep.

        now (float | None):
            Current time, injectable for tests.
            (Default: None)
    """

    moment = time.time() if now is None else now

    try:
        entries = list(directory.glob('*.json'))
    except OSError:
        return

    for entry in entries:
        try:
            if moment - entry.stat().st_mtime > RESPONSE_TTL_SECONDS:
                entry.unlink(missing_ok=True)
        except OSError:
            continue

def remove_tree(directory: Path) -> None:
    """
    Remove Tree
    ===========

    Delete a session directory and its contents, ignoring any failure.

    Hand-rolled rather than shutil.rmtree because the tree is exactly two levels
    deep, and because losing a race with another process sweeping the same stale
    session must be a no-op rather than an exception.

    Args
    ----
        directory (Path): Session directory to remove.
    """

    try:
        for child in directory.iterdir():
            if child.is_dir():
                for grandchild in child.iterdir():
                    grandchild.unlink(missing_ok=True)
                child.rmdir()
            else:
                child.unlink(missing_ok=True)
        directory.rmdir()
    except OSError:
        pass

# ==============================================================================
# [Registry]
# ==============================================================================

class Tool:
    """
    Tool
    ====

    One callable tool: its implementation and how it is presented.
    """

    def __init__(self, name: str, fn, description: str, timeout: float) -> None:
        """
        Init
        ====

        Store the tool's name, implementation, description and timeout.

        Args
        ----
            name (str):
                Name the client calls it by.

            fn (function):
                Implementation, run on Flame's main thread. Returns a dict.

            description (str):
                Text the language model reads.

            timeout (float):
                Advisory only. The client is the only side that can enforce it,
                because Flame runs tools synchronously and cannot interrupt itself
                mid-call.
        """

        self.name = name
        self.fn = fn
        self.description = description
        self.timeout = timeout

def tools_signature() -> tuple:
    """
    Tools Signature
    ===============

    Return the name, modification time and size of every tool file.

    Cheap (a stat per file, nothing read), so it can be checked on every request.
    It changes whenever a tool file is added, edited, renamed or removed.

    Returns
    -------
        signature (tuple): Sorted (name, mtime, size) entries, or () if the folder is unreadable.
    """

    try:
        return tuple(sorted(
            (path.name, path.stat().st_mtime, path.stat().st_size)
            for path in Path(TOOLS_PATH).glob('*.py')
            ))
    except OSError:
        return ()

def load_tools() -> None:
    """
    Load Tools
    ==========

    Register every tool file in the tools folder in TOOLS.

    Each tools/<name>.py defines a function called <name>. That function is the
    tool, its docstring is the description callers read, and an optional
    module-level TIMEOUT overrides DEFAULT_TOOL_TIMEOUT. Files whose names start
    with '_' are skipped. Adding a tool is therefore just adding a file; nothing
    in this script changes.

    A file that fails to load is logged and skipped, so one broken tool never
    takes the rest of the backdoor down with it.
    """

    global _loaded_tools_signature

    TOOLS.clear()
    _loaded_tools_signature = tools_signature()

    for path in sorted(Path(TOOLS_PATH).glob('*.py')):
        name = path.stem
        if name.startswith('_'):
            continue

        try:
            # Loaded under a private module name, so a tool file never collides
            # with another script's module that happens to share its name.
            spec = importlib.util.spec_from_file_location(f'logik_backdoor_tool_{name}', path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            fn = getattr(module, name)
        except BaseException:
            log(f'Could not load tool: {path.name}', PrintType.ERROR, traceback.format_exc())
            continue

        TOOLS[name] = Tool(
            name=name,
            fn=fn,
            description=(fn.__doc__ or '').strip(),
            timeout=float(getattr(module, 'TIMEOUT', DEFAULT_TOOL_TIMEOUT)),
            )

# ==============================================================================
# [Tool Helpers]
# ==============================================================================

def attribute(obj, name: str) -> object:
    """
    Attribute
    =========

    Read a Flame attribute and reduce it to something JSON can carry.

    Most of Flame's Python API returns PyAttribute wrappers rather than plain
    values. They serialise to nothing useful, so anything crossing the bridge
    has to be unwrapped with get_value() first.

    The test is whether get_value is *callable*, not merely present. Some Flame
    objects carry the attribute set to None -- PyWorkspace is one -- so testing
    with hasattr and calling the result raises TypeError: 'NoneType' object is
    not callable. Others, such as PyProject.name, are already plain strings.

    Args
    ----
        obj (object):
            Object to read from.

        name (str):
            Attribute name.

    Returns
    -------
        value (object): The unwrapped value, or None if absent.
    """

    value = getattr(obj, name, None)
    getter = getattr(value, 'get_value', None)
    if callable(getter):
        return getter()

    return value

def ensure_batch_tab() -> None:
    """
    Ensure Batch Tab
    ================

    Switch Flame to the Batch tab if it is showing another one.

    Call before creating Batch nodes. Outside the Batch tab, nodes are still
    created, but Flame does not reliably apply or report their settings: an
    Action's resolution read back as the old size while Flame was on MediaHub
    (Flame 2027.1, 2026-10-02), and was right once Flame was on Batch.
    """

    import flame

    if flame.get_current_tab() != 'Batch':
        flame.set_current_tab('Batch')

def check_resolution(resolution) -> str:
    """
    Check Resolution
    ================

    Return why a resolution argument is invalid, or '' if it is fine.

    Tools call this before creating anything, so a bad value leaves nothing behind.

    Args
    ----
        resolution (list | None): [width, height] as given by the caller, or None for no change.

    Returns
    -------
        error (str): The error message, or '' if the value is usable.
    """

    if resolution is None:
        return ''

    try:
        if not isinstance(resolution, (list, tuple)):
            raise TypeError
        width, height = (int(value) for value in resolution)
    except (TypeError, ValueError):
        return f'resolution must be [width, height], got {resolution!r}'

    if width <= 0 or height <= 0:
        return f'resolution must be positive, got {width} x {height}'

    return ''

def set_resolution(node, resolution: list) -> None:
    """
    Set Resolution
    ==============

    Set a node's resolution to [width, height], keeping its bit depth and scan mode.

    The frame ratio follows from the size, which assumes square pixels. Check the
    value with check_resolution first. The result is not read back: outside the
    Batch tab the attribute reported the old size after a successful set, and
    even on Batch a read straight after switching was once stale.

    Args
    ----
        node (PyNode):
            A node with a resolution attribute, e.g. an Action or a Colour Source.

        resolution (list):
            [width, height].
    """

    import flame

    width, height = (int(value) for value in resolution)
    current = node.resolution.get_value()
    node.resolution = flame.PyResolution(
        width,
        height,
        current.bit_depth,
        width / height,
        current.scan_mode,
        )

def unique_node_name(name: str) -> str:
    """
    Unique Node Name
    ================

    Return name, or name with a number added if a node in the open Batch has it.

    Counts up the way Flame does for its own nodes: mocha_gmask, then
    mocha_gmask1, mocha_gmask2, and so on.

    Args
    ----
        name (str): The name wanted.

    Returns
    -------
        unique_name (str): A name no node in the open Batch has.
    """

    import flame

    taken = {attribute(node, 'name') for node in flame.batch.nodes}
    if name not in taken:
        return name

    number = 1
    while f'{name}{number}' in taken:
        number += 1

    return f'{name}{number}'

# ==============================================================================
# [Dispatch]
# ==============================================================================

def dispatch(request: dict) -> dict:
    """
    Dispatch
    ========

    Run the tool named by a request and return its response dict.

    Pure plumbing over TOOLS, kept here rather than in the service module so it
    can be exercised without Flame or PySide6. Never raises: every failure
    becomes a response the client can read.

    Args
    ----
        request (dict): Decoded request, carrying tool and args.

    Returns
    -------
        response (dict): The tool's response, or an error response.
    """

    name = request.get('tool')
    arguments = request.get('args') or {}

    if not isinstance(arguments, dict):
        return {'ok': False, 'error': 'args must be an object'}

    # Rescan Python Hooks re-imports this script only when this file changed, not
    # when a tool file did. So check the tools folder here and reload it if a
    # tool was added, edited or removed, which makes the change live on the next
    # call with no refresh needed.
    if tools_signature() != _loaded_tools_signature:
        load_tools()
        _update_session_tools()

    entry = TOOLS.get(name)
    if entry is None:
        known = ', '.join(sorted(TOOLS))
        log(f'Unknown tool called: {name}', PrintType.ERROR)

        return {'ok': False, 'error': f'unknown tool {name!r}; available: {known}'}

    # Arguments are validated against the signature first, so that a TypeError
    # raised inside a tool is never misreported as a bad call.
    try:
        inspect.signature(entry.fn).bind(**arguments)
    except TypeError as error:
        log(f'Bad arguments for {name}: {error}', PrintType.ERROR)

        return {'ok': False, 'error': f'bad arguments for {name!r}: {error}'}

    quiet = name in QUIET_TOOLS
    if not quiet:
        _print_call(entry, arguments)
    started = time.monotonic()

    try:
        result = entry.fn(**arguments)
    except BaseException:
        result = {'ok': False, 'error': traceback.format_exc()}

    if not isinstance(result, dict):
        result = {
            'ok': False,
            'error': f'tool {name!r} returned {type(result).__name__}, expected dict',
            }

    if not quiet:
        _print_result(name, result, time.monotonic() - started)

    return result

def _print_call(entry: Tool, arguments: dict) -> None:
    """
    Print Call
    ==========

    Print that a tool is being called: its name to the terminal and Flame's
    message area, then what it does and its arguments to the terminal only.

    What it does is the first line of the tool's description, so every tool is
    covered without anything being added to the tool files.

    Args
    ----
        entry (Tool):
            The tool being called.

        arguments (dict):
            The arguments it is called with.
    """

    try:
        pyflame.print(f'Tool called: {entry.name}', new_line=False, script_name=SCRIPT_NAME)
        summary = entry.description.splitlines()[0] if entry.description else ''
        if summary:
            pyflame.print(summary, indent=4, new_line=False, print_to_flame=False)
        for key, value in arguments.items():
            text = str(value)
            if len(text) > PRINT_VALUE_LIMIT:
                text = text[:PRINT_VALUE_LIMIT] + '...'
            pyflame.print(f'{key}: {text}', indent=4, new_line=False, print_to_flame=False)
    except BaseException:
        pass

def _print_result(name: str, result: dict, seconds: float) -> None:
    """
    Print Result
    ============

    Print to the terminal only how a tool call ended and how long it took.

    A failure shows the first line of its error. Long tracebacks stay in the
    reply, which the caller reads. A success shows the node made or the number
    of clips imported, when the tool reports them.

    Args
    ----
        name (str):
            Name of the tool that ran.

        result (dict):
            The tool's reply.

        seconds (float):
            How long the call took.
    """

    try:
        if result.get('ok'):
            details = ', '.join(f'{key}: {result[key]}' for key in PRINT_RESULT_KEYS if key in result)
            text = f'{name} done in {seconds:.1f} s' + (f' -> {details}' if details else '')
            pyflame.print(text, print_to_flame=False)
        else:
            error = str(result.get('error') or 'no error given').strip()
            # A traceback's last line names the exception; any other error's first line says it all.
            line = error.splitlines()[-1] if error.startswith('Traceback') else error.splitlines()[0]
            pyflame.print(f'{name} FAILED in {seconds:.1f} s: {line}', print_type=PrintType.ERROR, print_to_flame=False)
    except BaseException:
        pass

def _update_session_tools() -> None:
    """
    Update Session Tools
    ====================

    Rewrite the tool list in this Flame's session.json after the tools reload.

    Callers read the list from there (logik_backdoor_client.sessions()), so it
    would otherwise keep showing the tools as they were at startup. Never raises.
    """

    try:
        path = session_dir(os.getpid()) / SESSION_FILE
        session = read_json(path)
        if session is not None:
            session['tools'] = describe()
            write_atomic(path, session)
    except BaseException:
        pass

def describe() -> list:
    """
    Describe
    ========

    Return JSON-safe metadata for every registered tool.

    Written into each session's session.json, so callers can see the tool
    list without calling a tool.

    Returns
    -------
        tools (list[dict]): One entry per tool, sorted by name.
    """

    return [
        {'name': entry.name, 'description': entry.description, 'timeout': entry.timeout}
        for entry in sorted(TOOLS.values(), key=lambda item: item.name)
        ]

# ==============================================================================
# [Service Helpers]
# ==============================================================================

def log(message: str, print_type: PrintType = PrintType.INFO, detail: str = '') -> None:
    """
    Log
    ===

    Print a message to the terminal and Flame's message area, swallowing any failure.

    Logging must never be the reason this module takes Flame down with it, so
    even a broken stdout is tolerated.

    Args
    ----
        message (str):
            Short text shown in both the terminal and Flame's message area.

        print_type (PrintType):
            PrintType.ERROR for failures, so they stand out in both places.
            (Default: PrintType.INFO)

        detail (str):
            Extra text, such as a traceback, printed to the terminal only. A
            multi-line traceback is unreadable in Flame's message area.
            (Default: '')
    """

    try:
        pyflame.print(
            message,
            print_type=print_type,
            new_line=not detail,
            script_name=SCRIPT_NAME,
            )
        if detail:
            print(detail)
    except BaseException:
        pass

def _mtime(path: Path) -> float:
    """
    MTime
    =====

    Return a path's mtime, or 0.0 if it vanished mid-scan.

    Requests can be removed underneath the sort by a client that gave up, and
    that must not raise.

    Args
    ----
        path (Path): File to stat.

    Returns
    -------
        mtime (float): Modification time, or 0.0 if unreadable.
    """

    try:
        return path.stat().st_mtime
    except OSError:
        return 0.0

def _flame_version() -> str:
    """
    Flame Version
    =============

    Return the running Flame version, or unknown if it cannot be read.

    Returns
    -------
        version (str): The version string, or 'unknown'.
    """

    try:
        import flame

        return str(flame.get_version())
    except BaseException:
        return 'unknown'

# ==============================================================================
# [Service]
# ==============================================================================

class _Service:
    """
    Service
    =======

    One running bridge: its session directory and its polling timer.
    """

    def __init__(self, session: Path) -> None:
        """
        Init
        ====

        Prepare the request and response directories for this session.

        Args
        ----
            session (Path): Session directory owned by this Flame process.
        """

        self.session = session
        self.requests = session / REQUEST_DIR
        self.responses = session / RESPONSE_DIR
        self.requests.mkdir(parents=True, exist_ok=True)
        self.responses.mkdir(parents=True, exist_ok=True)
        from PySide6 import QtCore

        self.timer = QtCore.QTimer()
        self.last_sweep = time.time()

    def tick(self) -> None:
        """
        Tick
        ====

        Handle any pending requests. Must never raise: Qt calls this forever.

        An exception escaping a timer slot would repeat every interval and bury
        Flame's console, so the entire body is guarded.
        """

        try:
            self._drain()
            self._maybe_sweep()
        except BaseException:
            log('Tick failed.', PrintType.ERROR, traceback.format_exc())

    def _drain(self) -> None:
        """
        Drain
        =====

        Run up to MAX_REQUESTS_PER_TICK pending requests, oldest first.
        """

        try:
            pending = sorted(self.requests.glob('*.json'), key=_mtime)
        except OSError:
            return

        for path in pending[:MAX_REQUESTS_PER_TICK]:
            request = read_json(path)
            # Unlink before running: a tool that crashes Flame must not leave a
            # request behind that would be retried forever on the next launch.
            path.unlink(missing_ok=True)
            if request is None:
                continue
            self._respond(path.stem, dispatch(request))

    def _respond(self, request_id: str, response: dict) -> None:
        """
        Respond
        =======

        Write one response, substituting an error if it will not serialise.

        Flame returns PyAttribute wrappers that JSON cannot encode. Without this
        net, one leaking through would leave the client waiting out its full
        timeout for a response that could never arrive.

        Args
        ----
            request_id (str):
                Identifier the response file is named for.

            response (dict):
                Result to publish.
        """

        destination = self.responses / f'{request_id}.json'
        try:
            write_atomic(destination, response)
        except (TypeError, ValueError):
            write_atomic(
                destination,
                {
                    'ok': False,
                    'error': (
                        'result was not JSON-serialisable, which usually means a '
                        f'Flame PyAttribute is missing .get_value(): {traceback.format_exc()}'
                        ),
                    },
                )
        except OSError:
            log(f'Could not write response for {request_id}.', PrintType.ERROR, traceback.format_exc())

    def _maybe_sweep(self) -> None:
        """
        Maybe Sweep
        ===========

        Periodically discard responses that no client will ever collect.
        """

        now = time.time()
        if now - self.last_sweep < SWEEP_INTERVAL_SECONDS:
            return
        self.last_sweep = now
        sweep_responses(self.responses, now=now)

# ==============================================================================
# [Start / Stop]
# ==============================================================================

def _module_hash() -> str:
    """
    Module Hash
    ===========

    Return a hash of this file and the tool files, or '' if they cannot be read.

    Used to tell whether a hook refresh brought new code. The running service
    records the hash it started with; if a later import sees a different hash,
    the code changed and the service is rebuilt so new or edited tools take
    effect. Without this, the app-anchored service would keep serving the code
    it first loaded and a refresh would never pick up changes. The tool files
    are part of the hash, so adding, editing or removing one counts as a change.

    Returns
    -------
        digest (str): Hex digest of the files, or '' on failure.
    """

    try:
        import hashlib

        digest = hashlib.sha256(Path(__file__).read_bytes())
        for path in sorted(Path(TOOLS_PATH).glob('*.py')):
            digest.update(path.name.encode())
            digest.update(path.read_bytes())

        return digest.hexdigest()
    except BaseException:
        return ''

def start() -> bool:
    """
    Start
    =====

    Start the bridge for this Flame process. Returns True once polling.

    Call from Flame's main thread so the timer belongs to it. Every failure path
    returns False after logging, because a bridge that cannot start must never
    stop Flame from starting.

    Returns
    -------
        running (bool): True if the bridge is running.
    """

    global _service

    from PySide6 import QtCore

    app = QtCore.QCoreApplication.instance()
    if app is None:
        # Qt is not up yet. app_initialized() or a menu hook will call again
        # once it is. Nothing to do, and not an error.
        return False

    # Clear out sessions left by this machine's exited Flame processes on every
    # load, refresh included. live_sessions() deletes them on the way past and
    # leaves other machines' sessions alone; the list it returns is not needed.
    live_sessions()

    current_hash = _module_hash()

    # A hook refresh re-imports this module with _service reset to None, but the
    # previous service is still anchored on the long-lived app object. If it is
    # running the same code, adopt it rather than starting a second timer. If the
    # code changed (different file hash), tear down its timer and fall through to
    # build a fresh service, so refreshed/edited tools actually take effect.
    existing = getattr(app, _APP_SERVICE_ATTR, None)
    if existing is not None and existing.timer.isActive():
        if getattr(existing, 'code_hash', None) == current_hash:
            _service = existing

            return True
        try:
            existing.timer.stop()
            existing.timer.timeout.disconnect(existing.tick)
        except BaseException:
            pass
        # The new service reuses this pid's session directory, so it is left in
        # place here rather than removed.

    if _service is not None and _service.timer.isActive() and \
            getattr(_service, 'code_hash', None) == current_hash:
        return True

    try:
        session = session_dir(os.getpid())
        service = _Service(session)
        write_atomic(
            session / SESSION_FILE,
            {
                'pid': os.getpid(),
                'host': socket.gethostname(),
                'version': _flame_version(),
                'started': time.time(),
                'tools': describe(),
                },
            )
    except BaseException:
        log('Could not create session.', PrintType.ERROR, traceback.format_exc())

        return False

    service.code_hash = current_hash
    service.timer.timeout.connect(service.tick)
    service.timer.start(POLL_INTERVAL_MS)
    _service = service

    # Anchor on the app so it survives module re-import and is never GC'd.
    setattr(app, _APP_SERVICE_ATTR, service)
    log(f'Listening in: {session}')

    return True

def stop() -> None:
    """
    Stop
    ====

    Stop polling and remove this session's directory.

    Not needed for a normal Flame quit: a session whose pid is gone is collected
    by the next process to look. This exists for reloading during development.
    """

    global _service

    service = _service
    if service is None:
        return

    _service = None
    try:
        service.timer.stop()
        service.timer.timeout.disconnect(service.tick)
    except BaseException:
        pass

    try:
        from PySide6 import QtCore
        app = QtCore.QCoreApplication.instance()
        if app is not None and getattr(app, _APP_SERVICE_ATTR, None) is not None:
            delattr(app, _APP_SERVICE_ATTR)
    except BaseException:
        pass

    remove_tree(service.session)
    log('Stopped.')

# ==============================================================================
# [Entry Points]
# ==============================================================================

def app_initialized(project_name: str = '') -> None:
    """
    App Initialized
    ===============

    Start the backdoor once Flame has finished loading a project.

    Flame calls this automatically. Everything is swallowed, including errors
    that would normally be worth re-raising, because the one guarantee this
    makes is that installing it cannot stop Flame from working.

    Args
    ----
        project_name (str):
            Name of the project Flame just opened. Passed by Flame, unused here.
            (Default: '')
    """

    try:
        start()
    except BaseException:
        log('Failed to start. Flame is unaffected.', PrintType.ERROR, traceback.format_exc())

pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

# Flame re-imports this module on a 'Refresh Python Hooks', which re-runs the
# code below, but it does NOT call app_initialized() on a refresh and does not
# reliably call the menu hooks either. Starting here, at module scope, means the
# service is (re)started on every import -- startup and refresh alike -- without
# depending on which hooks Flame chooses to call.
#
# start() is safe to call this way: it adopts the service already anchored on the
# QApplication instead of starting a second timer, and it returns quietly if Qt
# is not up yet (the case at first import during startup, which app_initialized()
# then covers).
#
# The tools are loaded first, on every import, so a refresh picks up new or
# edited tool files.
load_tools()

try:
    start()
except BaseException:
    log('Auto-start failed. Flame is unaffected.', PrintType.ERROR, traceback.format_exc())
