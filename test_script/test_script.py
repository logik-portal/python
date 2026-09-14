"""
Script Name: Test Script
Script Version: 1.0.1
Flame Version: 2027
Written by: Michael Vaglienty
Creation Date: 09.10.26
Update Date: 09.10.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Batch

Description:

    This is a test. This does nothing.

Menus:

    None

To install:

    Copy script into /opt/Autodesk/shared/python/test_script

Updates:

    v1.0.1 09.10.26
        - Blah

    v1.0.0 09.10.26
        - Blah
"""

import os

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Test Script'
SCRIPT_VERSION = 'v1.0.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

print('Hello, World!')