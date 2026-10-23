# Refresh Python Hooks
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Refresh Python Hooks
Script Version: 1.9.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 05.12.22
Update Date: 10.13.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch / Flame Main Menu

Description:

    Refresh python hooks and print message to Flame message window and terminal.

URL:

    https://logik-portal.com/scripts/refresh_python_hooks

Menus:

    Flame Main Menu -> Refresh Python Hooks
    Right-click in batch -> Refresh Python Hooks
    Right-click in media panel -> Refresh Python Hooks
    Right-click in timeline -> Refresh Python Hooks

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.9.1 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.9.0 03.26.26
        - Updated to PyFlameLib v5.3.0.

    v1.8.0 04.03.25
        - Updated to PyFlameLib v4.3.0.
        - Added menu to refresh python hooks from timeline.

    v1.7.0 02.12.25
        - Added menu to refresh python hooks from media panel.

    v1.6.0 12.16.24
        - Updated to PyFlameLib v3.3.0.
        - Script now only works with Flame 2023.2+.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v1.5.0 09.18.24
        - Updated to PyFlameLib v3.2.0.

    v1.4.0 08.04.24
        - Updated to PyFlameLib v3.0.0.

    v1.3.0 01.21.24
        - Updates to PySide.

    v1.2.0 07.23.23
        - Updated to PyFlameLib v2.0.0.
        - Updated versioning to semantic versioning.

    v1.1.0 09.05.22
        - Updated menu for Flame 2023.2+.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

from lib.pyflame_lib_refresh_python_hooks import *

SCRIPT_NAME = 'Refresh Python Hooks'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
SCRIPT_VERSION = 'v1.9.1'

# ==============================================================================
# [Main Script]
# ==============================================================================

def refresh_hooks(selection):

    pyflame.refresh_hooks()

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_main_menu_custom_ui_actions():

    return [
        {
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Refresh Python Hooks',
                    'order': 1,
                    'separator': 'below',
                    'execute': refresh_hooks,
                    'minimumVersion': '2025.1'
               },
           ]
        }
    ]

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Refresh Python Hooks',
                    'order': 1,
                    'separator': 'below',
                    'execute': refresh_hooks,
                    'minimumVersion': '2025.1',
               },
           ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Refresh Python Hooks',
                    'order': 1,
                    'separator': 'below',
                    'execute': refresh_hooks,
                    'minimumVersion': '2025.1',
               },
           ]
        }
    ]

def get_timeline_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Refresh Python Hooks',
                    'order': 1,
                    'separator': 'below',
                    'execute': refresh_hooks,
                    'minimumVersion': '2025.1',
               },
           ]
        }
    ]
