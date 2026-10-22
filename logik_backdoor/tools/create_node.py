# Logik Backdoor -- create_node tool
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
Script Name: Logik Backdoor Tool - create_node

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

TIMEOUT = 120.0

# ==============================================================================
# [Main Script]
# ==============================================================================

def create_node(node_type: str, setup_path: str = '', remove_setup: bool = False, node_name: str | None = None,
        position: list | None = None, input_node: str | None = None) -> dict:
    """
    Create a node in the open Batch, optionally loading a setup file into it.

    node_type is a Flame Batch node type, e.g. 'GMask' or 'GMask Tracer' (the
    valid names are flame.batch.node_types). setup_path, if given, is a node
    setup file to load into the new node -- for example a .gmask exported from
    Mocha loaded into a GMask node, or a .mask into a GMask Tracer. Requires a
    Batch to be open. Use this to bring a saved node setup into the current Batch.

    remove_setup deletes the setup file once it has been loaded, and its folder
    if that leaves it empty. Pass it when setup_path is a throwaway temp file the
    caller wrote only to hand the setup across (e.g. from Mocha). This deletes a
    scratch file on disk only -- the tool never deletes anything in Flame.

    node_name names the new node, e.g. 'mocha_gmask'. A number is added if the
    Batch already has a node by that name. None keeps Flame's default name.

    position is [x, y] in the
    Batch schematic; None leaves Flame's placement. input_node is the name of a
    node already in the Batch whose output is connected into the new node's
    default input BEFORE any setup loads -- so a setup that depends on its input
    (e.g. a GMask sized by its Front) is read with that input in place. The
    reply includes the node's position, so a caller can place the next node
    relative to it.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute, ensure_batch_tab, unique_node_name

    batch = getattr(flame, 'batch', None)
    if batch is None:
        return {'ok': False, 'error': 'no Batch is currently open'}

    # Nodes must be created with Flame on the Batch tab, or their settings are
    # not reliably applied.
    ensure_batch_tab()

    if setup_path and not os.path.isfile(setup_path):
        return {'ok': False, 'error': f'setup file not found: {setup_path}'}

    if node_name is not None and not (isinstance(node_name, str) and node_name.strip()):
        return {'ok': False, 'error': f'node_name must be a non-empty string, got {node_name!r}'}

    if position is not None:
        try:
            if not isinstance(position, (list, tuple)):
                raise TypeError
            pos_x, pos_y = (int(value) for value in position)
        except (TypeError, ValueError):
            return {'ok': False, 'error': f'position must be [x, y], got {position!r}'}

    source = None
    if input_node is not None:
        source = next((node for node in batch.nodes if attribute(node, 'name') == input_node), None)
        if source is None:
            return {'ok': False, 'error': f'input_node not found in the Batch: {input_node!r}'}

    try:
        node = batch.create_node(node_type)
    except Exception as error:
        try:
            valid = ', '.join(sorted(str(t) for t in batch.node_types))
        except Exception:
            valid = 'see flame.batch.node_types'

        return {'ok': False, 'error': f'could not create a {node_type!r} node ({error}). Valid types: {valid}'}

    if position is not None:
        node.pos_x = pos_x
        node.pos_y = pos_y

    # Connect before the setup loads, so the setup is read with its input present.
    if source is not None:
        batch.connect_nodes(source, 'Default', node, 'Default')

    loaded = False
    removed = False
    if setup_path:
        try:
            node.load_node_setup(setup_path)
            loaded = True
        except Exception as error:
            return {
                'ok': False,
                'error': f'created the node but could not load the setup: {error}',
                'node': attribute(node, 'name'),
                }

        # Clean up the throwaway temp file (and its folder if now empty). This is
        # a scratch file on disk, never Flame content.
        if remove_setup:
            try:
                os.remove(setup_path)
                os.rmdir(os.path.dirname(setup_path))
            except OSError:
                pass
            removed = not os.path.isfile(setup_path)

    # Named last, after any setup is loaded, so a name carried in the setup
    # cannot replace it.
    if node_name is not None:
        node.name = unique_node_name(node_name.strip())

    return {
        'ok': True,
        'node': attribute(node, 'name'),
        'type': attribute(node, 'type'),
        'position': [attribute(node, 'pos_x'), attribute(node, 'pos_y')],
        'setup_loaded': loaded,
        'setup_removed': removed,
        }
