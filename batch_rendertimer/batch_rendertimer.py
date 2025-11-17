"""
Script Name: Batch Rendertimer
Script Version: 1.0.0
Flame Version: 2023
Written by: Bob Maple
Creation Date: 08.04.23
Update Date: 08.04.23

Script Type: Batch Rendering

Description:

    Prints render start and end times to the console and to the Flame message area.

To install:

    Copy script folder into /opt/Autodesk/shared/python
"""

import time

import flame


def print_message(message):
    flame.messages.show_in_console(message, 'info', 5)
    print(message)

def batch_render_begin(info, userData, *args, **kwargs):
    userData["render_started"] = time.time()
    print("Render started: " + str(userData.get("render_started")))

def batch_render_end(info, userData, *args, **kwargs):
    render_ended = time.time()
    print("Render ended: " + str(render_ended))
    render_secs  = render_ended - userData.get("render_started")
    print_message("Render time total: " + str(round(render_secs, 2)) + " seconds\n")

def render_ended(module_name, sequence_name, elapsed_time_in_seconds):
    print_message("Timeline render ended: " + str(round(elapsed_time_in_seconds, 2)) + " seconds\n" )
