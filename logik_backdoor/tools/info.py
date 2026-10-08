# Logik Backdoor -- info tool
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
Script Name: Logik Backdoor Tool - info

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

def info() -> dict:
    """
    Report the Flame version and the current project and workspace names.

    A cheap way to confirm which of several running Flame sessions is answering.
    """

    import flame

    # Imported here, not at the top: Flame also imports this file by itself at
    # startup, and importing logik_backdoor then, before the service has loaded,
    # makes Python take the folder for it and the service never starts.
    from logik_backdoor import attribute

    project = getattr(flame.projects, 'current_project', None)
    workspace = attribute(project, 'current_workspace') if project is not None else None

    return {
        'ok': True,
        'version': str(flame.get_version()),
        'project': attribute(project, 'name'),
        'workspace': attribute(workspace, 'name') if workspace is not None else None,
        }
