'''
Script Name: auto initialise tablet
Script Version: 1.0.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 06.20.25
Update Date: 06.20.25

Custom Action Type: Project Launch

Description:

   This script initialises the tablet when a project is launched. Helpful when using the Auto-USB-Bridge mode for Wacom tablets running HP Anyware. The script is only 4 lines and just executes the 'Initialise Tablet' shortcut.

To install:

    Copy script into /opt/Autodesk/shared/python/auto_initialise_tablet or wherever you keep your scripts.

Updates:

    v1.0.0 06.20.25

        Inception
'''

import flame

def app_initialized(selection):
    
    flame.execute_shortcut('Initialise Tablet')
    print("Auto Tablet Initialised.")