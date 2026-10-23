# Import Browser
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Import Browser
Script Version: 2.7.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 06.16.19
Update Date: 10.13.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Opens import browser in batch through right click menu.

URL:
    https://logik-portal.com/scripts/import_browser

Menu:

    Right-click in batch -> Import Browser

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v2.7.1 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v2.7.0 03.26.26
        - Updated to PyFlameLib v5.3.0.

    v2.6.0 07.10.25
        - Updated to PyFlameLib v5.0.0.

    v2.5.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v2.4.0 12.31.24
        - Updated to PyFlameLib v4.0.0.

    v2.3.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v2.2.1 01.15.24
        - Updated PySide.

    v2.2.0 07.29.23
        - Updated to PyFlameLib v2.0.0.
        - Updated to semantic versioning.

    v2.1 10.14.22
        - Updated menu for Flame 2023.2+

    v2.0 05.22.21
        - Updated to be compatible with Flame 2022/Python 3.7

    v1.1 10.24.19
        - Menu renamed to Import...
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import flame
from lib.pyflame_lib_import_browser import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Import Browser'
SCRIPT_VERSION = 'v2.7.1'

# ==============================================================================
# [Main Script]
# ==============================================================================

def open_file_browser(selection):

    pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

    pyflame.print('Opening Import Browser...')

    flame.execute_shortcut('Import...')

    pyflame.print('Import Browser closed.', text_color=TextColor.GREEN)

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Import Browser',
                    'order': 1,
                    'separator': 'below',
                    'execute': open_file_browser,
                    'minimumVersion': '2025.1'
               }
           ]
        }
    ]
