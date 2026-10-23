# Logik Backdoor -- import_image_to_library tool
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License. See the LICENSE file
# for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

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
