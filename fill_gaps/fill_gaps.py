# Fill Gaps
# Copyright (c) 2025 Michael Vaglienty
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
Script Name: Fill Gaps
Script Version: 1.4.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 02.18.24
Update Date: 12.18.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Timeline

Description:

    Inserts black into selected gaps in the timeline.

    Selection of segments in timeline should start with a gap, otherwise gaps will
    not be included in selection of timeline segments and the menu will not be visible.

Menus:

    Right-click on selection of gaps in timeline -> Fill Gap

To install:

    Copy script into /opt/Autodesk/shared/python/fill_gaps

Updates:

    v1.4.0 12.18.25
        - Updated to PyFlameLib v5.1.1.

    v1.3.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v1.2.0 12.31.24
        - Updated to PyFlameLib v4.0.0.

    v1.1.0 08.24.24
        - Updated to PyFlameLib v3.0.0.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import flame
from lib.pyflame_lib_fill_gaps import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Fill Gaps'
SCRIPT_VERSION = 'v1.3.0'

# ==============================================================================
# [Main Script]
# ==============================================================================

def fill_gap(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    # Check script path, if path is incorrect, stop script.
    if not pyflame.verify_script_install():
        return

    # Fill gaps in selection with black clip
    for segment in selection:
        if isinstance(segment, (flame.PySegment)) and segment.type == 'Gap':
            segment.set_gap_colour(r=0.0, g=0.0, b=0.0)
            pyflame.print('Selected gaps filled with black.', text_color=TextColor.GREEN)

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_gap(selection):

    for item in selection:
        if isinstance(item, (flame.PySegment)) and item.type == 'Gap':
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_timeline_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Fill Gaps',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_gap,
                    'execute': fill_gap,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
