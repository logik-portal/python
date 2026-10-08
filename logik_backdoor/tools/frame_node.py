# Logik Backdoor -- frame_node tool
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
Script Name: Logik Backdoor Tool - frame_node

Usage:

    Part of Logik Backdoor. logik_backdoor.py loads every file in this tools
    folder automatically: the file name is the tool name, the function with that
    same name is the tool, its docstring is the description callers read, and
    TIMEOUT is the number of seconds a caller should wait.

    Keep this file free of side effects at import. Flame also imports every .py
    file in its python folders directly, so anything at module level runs twice.
"""

# ==============================================================================
# [Constants]
# ==============================================================================

TIMEOUT = 30.0

# ==============================================================================
# [Main Script]
# ==============================================================================

def frame_node(node_names: list) -> dict:
    """
    Select one or more Batch nodes and frame the Batch schematic view on them.

    node_names is a list of exact node names, e.g. ['mocha_gmask_tracer'] as
    create_node returned it. Each name must match exactly one node, or nothing
    is done and an error is returned. These nodes become the only selected
    nodes, so any previous selection is cleared. Use this after creating nodes so
    the artist sees where they landed. Nothing is added or deleted.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute, ensure_batch_tab

    batch = getattr(flame, 'batch', None)
    if batch is None:
        return {'ok': False, 'error': 'no Batch is currently open'}

    if not (isinstance(node_names, (list, tuple)) and node_names
            and all(isinstance(name, str) and name.strip() for name in node_names)):
        return {'ok': False, 'error': f'node_names must be a list of node names, got {node_names!r}'}

    # Only the named nodes are framed. A missing or ambiguous name is refused
    # rather than guessed, before anything is selected.
    names = [attribute(node, 'name') for node in batch.nodes]
    for name in node_names:
        count = names.count(name)
        if count != 1:
            return {'ok': False, 'error': f'expected one node named {name!r}, found {count}'}

    ensure_batch_tab()

    # frame_selected frames whatever is selected, so select only these nodes first.
    batch.select_nodes(list(node_names))
    if not batch.frame_selected():
        return {'ok': False, 'error': f'Flame could not frame {list(node_names)}'}

    return {'ok': True, 'nodes': list(node_names)}
