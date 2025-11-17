# Refresh Python Hooks
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
Script Name: Refresh Python Hooks
Script Version: 1.8.0
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 05.12.22
Update Date: 04.03.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch / Flame Main Menu

Description:

    Refresh python hooks and print message to Flame message window(Flame 2023.1+) and terminal.

    Message to Flame message window only shows up in Flame 2023.1+.

URL:
    https://github.com/logik-portal/python/refresh_python_hooks

Menus:

    Flame Main Menu -> Refresh Python Hooks
    Right-click in batch -> Refresh Python Hooks
    Right-click in media panel -> Refresh Python Hooks
    Right-click in timeline -> Refresh Python Hooks

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

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

#-------------------------------------
# [Imports]
#-------------------------------------

from lib.pyflame_lib_refresh_python_hooks import *

SCRIPT_NAME = 'Refresh Python Hooks'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
SCRIPT_VERSION = 'v1.8.0'

#-------------------------------------
# [Main Script]
#-------------------------------------

def refresh_hooks(selection):

    pyflame.refresh_hooks()

#-------------------------------------
# [Flame Menus]
#-------------------------------------

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
                    'minimumVersion': '2023.2'
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
                    'minimumVersion': '2023.2',
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
                    'minimumVersion': '2023.2',
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
                    'minimumVersion': '2023.2',
               },
           ]
        }
    ]