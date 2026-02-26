# SRT to XML
# Copyright (c) 2025 Michael Vaglienty
#
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: Test
Script Version: 3.7.3
Flame Version: 2023.2
Written by: Michael Vaglienty
Creation Date: 05.01.20
Update Date: 04.13.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: MediaPanel

Description:

    Convert SRT files to XML files that can be imported into Flame through MediaHub

URL:
    https://github.com/logik-portal/python/srt_to_xml

Menu:

    Right-click on clip in Media Panel that subtitles will be added to -> Convert SRT to XML

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.7.3 02.26.26
        - Fixed bug that caused script to not work when right-clicking on clips with ratio of 1.0.

    v3.7.0 04.13.25
        - Updated to PyFlameLib v4.3.0.

    v3.6.0 12.27.24
        - Updated for Python 3/Flame 2025+
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v3.5 03.04.23
        - Updated config file loading/saving.
        - Added check to make sure script is installed in the correct location.

    v3.4 09.22.22
        - Updated menu for Flame 2023.2+:
            Right-click on clip in Media Panel that subtitles will be added to -> Convert SRT to XML

    v3.3 06.06.22
        - Messages print to Flame message window - Flame 2023.1 and later.
        - Added Flame file browser - Flame 2023.1 and later.

    v3.2 03.15.22
        - Moved UI widgets to external file.

    v3.1 03.05.22
        - Updated UI for Flame 2023.
        - Config updated to XML.
        - Added option to open MediaHub to location of created XML.

    v3.0 05.22.21
        - Updated to be compatible with Flame 2022/Python 3.7.

    v2.1 04.27.21
        - Bug fixes

    v1.4 03.18.21:
        - Added bottom align button - will align rows of text to bottom row.
        - Changed event detection from empty line to timecode line.

    v1.3 02.17.21:
        - Fixed problem that caused script not to work when right clicking on clip with ratio of 1.0.
        - UI Improvements.

    v1.2 10.12.20:
        - Updated UI.

    v1.1 05.16.20:
        - Fixed scoping so menu only shows when right-clicking on clips.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

import os
import re
import itertools

import flame
from lib.pyflame_lib_srt_to_xml import *

#-------------------------------------
# [Constants]
#-------------------------------------
