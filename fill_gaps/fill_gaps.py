# Fill Gaps
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Fill Gaps
Script Version: 1.5.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 02.18.24
Update Date: 10.13.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Timeline

Description:

    Inserts black into selected gaps in the timeline.

URL:

    https://logik-portal.com/scripts/fill_gaps

Usage:

    Selection of segments in timeline should start with a gap, otherwise gaps will
    not be included in selection of timeline segments and the menu will not be visible.

Menus:

    Right-click on selection of gaps in timeline -> Fill Gap

To install:

    Copy script into /opt/Autodesk/shared/python/fill_gaps

Updates:

    v1.5.1 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.5.0 06.18.26
        - Updated to PyFlameLib v5.4.0.

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

from __future__ import annotations

import flame
from lib.pyflame_lib_fill_gaps import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Fill Gaps'
SCRIPT_VERSION = 'v1.5.1'

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
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
