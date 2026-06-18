"""
AB ColorChecker — Optional paths configuration for studio/IT use.

Place this file alongside ab_colorchecker.py to configure custom
library paths without modifying the main script. This is useful on
air-gapped systems where auto-install is not possible.

Uncomment and edit the paths below to match your system.
"""

import sys

# Example: point to a specific oiio Python binding location
# sys.path.insert(0, '/usr/local/lib/python3.10/site-packages')

# Example: point to a custom numpy installation
# sys.path.insert(0, '/opt/vfx/python/lib/python3.10/site-packages')

# Example: use VFX Reference Platform paths on Linux
# sys.path.insert(0, '/opt/vfxrefplatform/2026/lib/python3.10/site-packages')
