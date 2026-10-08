# Logik Backdoor Client
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
Script Name: Logik Backdoor Client
Script Version: 1.0.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 10.05.26
Update Date: 10.05.26

License: GNU General Public License v3.0 (GPL-3.0) - see license file for details

Description:

    Single-file client for the Logik Backdoor.

    See main docstring in logik_backdoor.py for more information.

Usage:

    Imported by the calling application, outside Flame. Standard library only.

    available() reports whether a Flame session is reachable, sessions() lists
    them, and call(tool, **arguments) runs a tool and returns its response dict.

Updates:

    v1.0.0 10.05.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import json
import os
import socket
import time
import uuid
from pathlib import Path

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

SESSION_FILE = 'session.json'
REQUEST_DIR = 'requests'
RESPONSE_DIR = 'responses'

POLL_SECONDS = 0.02

NO_SESSION = (
    'No running Flame session found. Start Flame with the Logik Backdoor hook '
    'installed, then try again.'
    )

# ==============================================================================
# [Sessions]
# ==============================================================================

def _home() -> Path:
    """
    Home
    ====

    Locate the Logik Backdoor config directory.

    Callers import this file from the installed logik_backdoor folder, so the
    config directory is the one beside it -- the same one the hook writes to.
    LOGIK_BACKDOOR_HOME overrides that, matching the hook.

    Returns
    -------
        root (Path): The config directory. May not exist if Flame has never run it.
    """

    override = os.environ.get('LOGIK_BACKDOOR_HOME')
    if override:
        return Path(override).expanduser()

    return Path(SCRIPT_PATH) / 'config'

def _alive(pid: int) -> bool:
    """
    Alive
    =====

    Report whether a process exists, without signalling it.

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

def sessions() -> list:
    """
    Sessions
    ========

    Return every running Flame session the bridge can reach, newest first.

    Each entry carries pid, version and the session directory. Dead sessions are
    ignored rather than deleted -- cleanup belongs to the bridge itself, not to
    every client that happens to look.

    Returns
    -------
        found (list): One dict per live session.
    """

    found = []
    root = _home() / 'sessions'

    try:
        entries = sorted(root.iterdir())
    except OSError:
        return []

    for entry in entries:
        if not entry.name.isdigit() or not entry.is_dir():
            continue
        pid = int(entry.name)
        try:
            info = json.loads((entry / SESSION_FILE).read_text())
        except (OSError, ValueError):
            info = {}

        # Never judge another machine's session by pid; the number means a
        # different process there.
        host = info.get('host')
        if host is not None and host != socket.gethostname():
            continue

        if not _alive(pid):
            continue
        info['pid'] = pid
        info['dir'] = str(entry)
        found.append(info)

    found.sort(key=lambda item: item.get('started', 0.0), reverse=True)

    return found

def available() -> bool:
    """
    Available
    =========

    Report whether any Flame session is reachable right now.

    Use this to show or hide a menu item rather than offering an action that
    cannot work.

    Returns
    -------
        available (bool): True if at least one live session was found.
    """

    return bool(sessions())

# ==============================================================================
# [Calls]
# ==============================================================================

def call(tool: str, timeout: float = 60.0, pid: int | None = None, **arguments) -> dict:
    """
    Call
    ====

    Run a tool inside Flame and return its response.

    Targets the most recently started session unless pid names another. Never
    raises for the ordinary failures: an unreachable Flame, a timeout and a tool
    error all come back as {'ok': False, 'error': ...}.

    Args
    ----
        tool (str):
            Tool name, for example 'info' or 'import_image_to_library'.

        timeout (float):
            Seconds to wait for a response.
            (Default: 60.0)

        pid (int | None):
            Target a specific Flame process. None picks the newest.
            (Default: None)

        **arguments:
            Passed through to the tool.

    Returns
    -------
        response (dict): The tool's response, or an error response.
    """

    live = sessions()
    if pid is not None:
        live = [s for s in live if s.get('pid') == pid]
    if not live:
        return {'ok': False, 'error': NO_SESSION}

    session = live[0]
    directory = Path(session['dir'])
    request_id = uuid.uuid4().hex
    request = directory / REQUEST_DIR / f'{request_id}.json'
    response = directory / RESPONSE_DIR / f'{request_id}.json'

    # Write to a hidden temporary name first, then rename. The bridge globs for
    # '*.json', so a partially written request is never visible to it.
    temporary = request.with_name(f'.{request.name}.{os.getpid()}.tmp')
    try:
        with open(temporary, 'w', encoding='utf-8') as handle:
            json.dump({'tool': tool, 'args': arguments}, handle)
        os.replace(temporary, request)
    except OSError as error:
        Path(temporary).unlink(missing_ok=True)

        return {'ok': False, 'error': f'could not submit request to Flame: {error}'}

    deadline = time.monotonic() + timeout

    while True:
        try:
            return_value = json.loads(response.read_text())
            response.unlink(missing_ok=True)

            return return_value
        except (OSError, ValueError):
            pass

        if time.monotonic() >= deadline:
            request.unlink(missing_ok=True)

            return {
                'ok': False,
                'error': (
                    f"Flame {session.get('version', 'unknown')} did not respond "
                    f'within {timeout:g}s. It may be rendering, or waiting on a '
                    'modal dialog.'
                    ),
                }

        if not _alive(int(session['pid'])):
            request.unlink(missing_ok=True)

            return {'ok': False, 'error': 'the Flame session exited before responding'}

        time.sleep(POLL_SECONDS)
