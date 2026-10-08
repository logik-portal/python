# Logik Backdoor -- import_alembic tool
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
Script Name: Logik Backdoor Tool - import_alembic

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
import re
import tempfile
from pathlib import Path

# ==============================================================================
# [Constants]
# ==============================================================================

TIMEOUT = 300.0

# Flame's viewer cameras. Every Action has them, but they are not offered as a
# Result camera, so they are left out when counting Result camera positions.
VIEWER_CAMERAS = ('Perspective', 'Object')

# The Result camera is stored in the Action setup as a channel whose Value is the
# camera's position in the Result camera list (Default is 0). This matches that
# Value, keeping everything before it in group 1.
RESULT_CAMERA_VALUE = re.compile(r'(Channel ResultCamera\n(?:[ \t]+(?!End\b)[^\n]*\n)*?[ \t]+Value )\S+')

# One camera per match, in node order: 'Node Camera' or 'Node CameraStereo',
# followed by its Name line.
CAMERA_NAME = re.compile(r'^Node (?:Camera|CameraStereo)\n\tName (.+)$', re.MULTILINE)

# The Action's Rendering option: 'yes' is User-Defined, 'no' is Same as
# Background (found by comparing two setups saved from Flame, 2026-10-04).
RESOLUTION_MODE = re.compile(r'^([ \t]*ResolutionMode )\S+$', re.MULTILINE)

# ==============================================================================
# [Main Script]
# ==============================================================================

def import_alembic(path: str, frame_rate: str = '', unit_to_pixels: float = 10.0, use_imported_camera: bool = True,
        resolution: list | None = None, node_name: str | None = None, same_as_background: bool = True) -> dict:
    """
    Create an Action node in the open Batch and import an Alembic (.abc) file into it.

    path is the .abc file. It is imported as Action objects with mesh animations,
    so an animated mesh (e.g. a Mocha mesh track) arrives as animated geometry.
    frame_rate is the file's rate in Flame's form, e.g. '24 fps' or '23.976 fps';
    blank uses Flame's default. unit_to_pixels scales the scene (Flame's default
    is 10). use_imported_camera sets the Action's Result camera to the first
    camera the file brought in (e.g. the Mocha camera); the Default camera is
    kept if the file has none. resolution is [width, height] for the Action, set
    before the import (e.g. the size of the Mocha clip); None keeps the Action's
    default resolution. same_as_background sets the Action's Rendering option
    to Same as Background once the file is imported (setting resolution makes it
    User-Defined); False leaves it as it is. node_name names the Action, e.g. 'mocha_alembic'; a
    number is added if the Batch already has a node by that name, and None keeps
    Flame's default name. Requires a Batch to be open. The Action keeps
    reading the file, so it must stay where it is.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute, check_resolution, ensure_batch_tab, set_resolution, unique_node_name

    batch = getattr(flame, 'batch', None)
    if batch is None:
        return {'ok': False, 'error': 'no Batch is currently open'}

    # Nodes must be created with Flame on the Batch tab, or their settings are
    # not reliably applied.
    ensure_batch_tab()

    if not os.path.isfile(path):
        return {'ok': False, 'error': f'Alembic file not found: {path}'}

    if node_name is not None and not (isinstance(node_name, str) and node_name.strip()):
        return {'ok': False, 'error': f'node_name must be a non-empty string, got {node_name!r}'}

    # Checked before the node is created, so a bad value leaves nothing behind.
    problem = check_resolution(resolution)
    if problem:
        return {'ok': False, 'error': problem}

    node = batch.create_node('Action')

    # Match the Action to the source clip before importing, so the scene is built
    # at the right size.
    if resolution is not None:
        set_resolution(node, resolution)

    # Only pass frame_rate when the caller gave one, so a blank keeps Flame's default.
    options = {'mesh_animations': True, 'unit_to_pixels': float(unit_to_pixels)}
    if frame_rate:
        options['frame_rate'] = frame_rate

    try:
        objects = node.import_abc(path, **options)
    except Exception as error:
        return {
            'ok': False,
            'error': f'created the Action node but could not import the Alembic file: {error}',
            'node': attribute(node, 'name'),
            }

    # Read the names now: editing the setup reloads it, which replaces these
    # objects and leaves the handles empty.
    names = [attribute(item, 'name') for item in objects or []]

    result_camera = None
    if use_imported_camera or same_as_background:
        try:
            result_camera = _edit_setup(node, use_imported_camera, same_as_background)
        except Exception as error:
            return {
                'ok': False,
                'error': f'imported the Alembic file but could not update the Action setup: {error}',
                'node': attribute(node, 'name'),
                }

    # Named last, after any setup is loaded, so a name carried in the setup
    # cannot replace it.
    if node_name is not None:
        node.name = unique_node_name(node_name.strip())

    return {
        'ok': True,
        'node': attribute(node, 'name'),
        'objects': names,
        'result_camera': result_camera,
        }

# ==============================================================================
# [Helpers]
# ==============================================================================

def _edit_setup(node, use_imported_camera: bool, same_as_background: bool) -> str | None:
    """
    Edit Setup
    ==========

    Set an Action's Result camera and Rendering option through its saved setup.

    The Python API has neither setting, so the Action setup is saved, edited and
    loaded back -- the approach Import Camera uses for its keyframe changes. Both
    edits share one save and load.

    use_imported_camera sets the Result camera to the first camera after
    Default. The node is new and holds only what the Alembic file brought in, so
    that is the imported one. same_as_background sets the Rendering option to
    Same as Background.

    The setup goes through a temporary folder that is always removed. Flame keeps
    the Alembic data when the setup is loaded back (verified live), so this does
    not tie the Action to the temporary copy.

    Args
    ----
        node (PyActionNode): The Action the Alembic file was imported into.

        use_imported_camera (bool): Set the Result camera to the imported camera.

        same_as_background (bool): Set the Rendering option to Same as Background.

    Returns
    -------
        camera_name (str | None): Name of the camera now used, or None if not set or the file had no camera.

    Raises
    ------
        RuntimeError:
            If the setup has no ResultCamera or ResolutionMode value to change.
    """

    with tempfile.TemporaryDirectory() as folder:
        base = os.path.join(folder, 'action_setup')
        node.save_node_setup(base)
        setup = Path(base + '.action')
        text = setup.read_text()
        original = text

        camera_name = None
        if use_imported_camera:
            cameras = [name for name in CAMERA_NAME.findall(text) if name not in VIEWER_CAMERAS]
            if len(cameras) >= 2:
                # Position 1 in the Result camera list: the first camera after Default.
                text, count = RESULT_CAMERA_VALUE.subn(r'\g<1>1', text, count=1)
                if count != 1:
                    raise RuntimeError('no ResultCamera value found in the Action setup')
                camera_name = cameras[1]

        if same_as_background:
            text, count = RESOLUTION_MODE.subn(r'\g<1>no', text, count=1)
            if count != 1:
                raise RuntimeError('no ResolutionMode value found in the Action setup')

        if text != original:
            setup.write_text(text)
            node.load_node_setup(str(setup))

    return camera_name
