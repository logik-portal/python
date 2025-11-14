"""
Script Name: frame io
Script Version: 0.9
Flame Version: 2024.2
Written by: John Geehreng
Creation Date: 01.03.23
Update Date: 01.25.24

Description:

    Collection of scripts for Frame.IO integration within Flame.

    frame.io conform uploader:

        This script will export h264 .mp4's to a FROM_FLAME folder in your job folder, save it to a FROM_FLAME shared library, and upload them to FrameIO.
        It will also automatically create or add to version stacks if it can find a matching base name.
        Script assumes a verion of _v## or _V### in order to match file names.

    frame.io csv to markers:

        Imports a CSV file exported from frame.io and adds markers to a clip in flame. There is no need to modify the CSV downloaded from FrameIO.

    frame.io get comments:

        This script will fetch comments from FrameIO and make markers according to the selection.

    frame.io python packages:

        Checks for installed Python Packages when launching Flame.

    frame_io shot uploader:

        This script will export h264 .mp4's to a FROM_FLAME folder in your job folder, save it to a FROM_FLAME shared library, and upload them to FrameIO.
        It will also automatically create or add to version stacks if it can find a matching base name.
        Script assumes a verion of _v## or _V### in order to match file names.
"""

# This file does nothing. It is only for the Logik Portal description.