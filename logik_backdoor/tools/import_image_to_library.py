# Logik Backdoor -- import_image_to_library tool
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
Script Name: Logik Backdoor Tool - import_image_to_library

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

def import_image_to_library(path, library_name: str = 'Image_Imports') -> dict:
    """
    Import one or more clips into a Library, creating the Library if needed.

    path is a single file, a sequence in bracket notation
    (/dir/clip.[100-200].dpx), a folder, or a list of paths. The Library named
    library_name is reused if it already exists, otherwise it is created. Use
    this to bring rendered media into the project.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute

    ws = flame.projects.current_project.current_workspace

    library = None
    for entry in ws.libraries:
        if attribute(entry, 'name') == library_name:
            library = entry
            break

    created = library is None
    if created:
        library = ws.create_library(library_name)
    library.open()

    clips = flame.import_clips(path, library)

    return {
        'ok': True,
        'library': library_name,
        'created_library': created,
        'count': len(clips),
        'clips': [attribute(c, 'name') for c in clips],
        }
