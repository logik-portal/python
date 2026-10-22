# Logik Backdoor -- import_image_to_batch tool
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
Script Name: Logik Backdoor Tool - import_image_to_batch

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

TIMEOUT = 600.0

# ==============================================================================
# [Main Script]
# ==============================================================================

def import_image_to_batch(path, reel_name: str = 'image_imports') -> dict:
    """
    Import one or more clips into the open Batch, on a named schematic reel.

    path is a single file, a sequence in bracket notation, a folder, or a list
    of paths. The schematic reel named reel_name is reused if it already exists,
    otherwise it is created. Requires a Batch to be open. Use this to bring
    rendered media straight into the current Batch.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute

    batch = getattr(flame, 'batch', None)
    if batch is None:
        return {'ok': False, 'error': 'no Batch is currently open'}

    reel = None
    for entry in batch.reels:
        if attribute(entry, 'name') == reel_name:
            reel = entry
            break

    created = reel is None
    if created:
        reel = batch.create_reel(reel_name)

    clips = flame.import_clips(path, reel)

    return {
        'ok': True,
        'batch': attribute(batch, 'name'),
        'reel': reel_name,
        'created_reel': created,
        'count': len(clips),
        'clips': [attribute(c, 'name') for c in clips],
        }
