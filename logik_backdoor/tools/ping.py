# Logik Backdoor -- ping tool
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License. See the LICENSE file
# for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Logik Backdoor Tool - ping

Usage:

    Part of Logik Backdoor. logik_backdoor.py loads every file in this tools
    folder automatically: the file name is the tool name, the function with that
    same name is the tool, its docstring is the description callers read, and
    TIMEOUT is the number of seconds a caller should wait.

    Keep this file free of side effects at import. Flame also imports every .py
    file in its python folders directly, so anything at module level runs twice.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os

# ==============================================================================
# [Constants]
# ==============================================================================

TIMEOUT = 10.0

# ==============================================================================
# [Main Script]
# ==============================================================================

def ping() -> dict:
    """Confirm the Flame bridge is alive. Use this first when other tools fail."""

    return {'ok': True, 'pong': True, 'pid': os.getpid()}
