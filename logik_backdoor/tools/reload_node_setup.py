# Logik Backdoor -- reload_node_setup tool
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
Script Name: Logik Backdoor Tool - reload_node_setup

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
import tempfile

# ==============================================================================
# [Constants]
# ==============================================================================

TIMEOUT = 120.0

# ==============================================================================
# [Main Script]
# ==============================================================================

def reload_node_setup(node_name: str, node_type: str = '') -> dict:
    """
    Save one Batch node's setup and load it straight back into the same node.

    node_name is the exact name of the node, e.g. the name create_node returned.
    node_type, if given (e.g. 'GMask Tracer'), must match too. Exactly one node
    must match, or nothing is done and an error is returned, so no other node is
    ever touched. Use this when a setup loaded from another app (e.g. a .mask
    from Mocha) only behaves correctly once Flame has saved and reloaded it. The
    setup goes through a temporary folder that is always removed; nothing in
    Flame is deleted.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute, ensure_batch_tab

    batch = getattr(flame, 'batch', None)
    if batch is None:
        return {'ok': False, 'error': 'no Batch is currently open'}

    if not (isinstance(node_name, str) and node_name.strip()):
        return {'ok': False, 'error': f'node_name must be a non-empty string, got {node_name!r}'}

    # Only the one named node is reloaded. A Batch can hold several nodes of the
    # same type, so an ambiguous name is refused rather than guessed.
    matches = [
        node for node in batch.nodes
        if attribute(node, 'name') == node_name and (not node_type or attribute(node, 'type') == node_type)
        ]
    if len(matches) != 1:
        kind = f' {node_type!r}' if node_type else ''
        return {'ok': False, 'error': f'expected one{kind} node named {node_name!r}, found {len(matches)}'}
    node = matches[0]

    ensure_batch_tab()

    with tempfile.TemporaryDirectory() as folder:
        base = os.path.join(folder, 'reload')
        try:
            node.save_node_setup(base)
        except Exception as error:
            return {'ok': False, 'error': f'could not save the node setup: {error}'}

        # Flame adds the setup's own extension (e.g. reload.mask) and writes side
        # files named after it (reload.mask.0.comp, reload.mask_node, ...). The
        # setup is the shortest name, which every other file starts with.
        names = sorted(name for name in os.listdir(folder) if name.startswith('reload.'))
        setup = min(names, key=len, default='')
        if not setup or not all(name.startswith(setup) for name in names):
            return {'ok': False, 'error': f'could not find the saved setup, found {names}'}

        try:
            node.load_node_setup(os.path.join(folder, setup))
        except Exception as error:
            return {'ok': False, 'error': f'could not load the setup back: {error}'}

    # A loaded setup can carry a node name; keep the one the caller asked for.
    if attribute(node, 'name') != node_name:
        node.name = node_name

    return {'ok': True, 'node': attribute(node, 'name'), 'type': attribute(node, 'type')}
