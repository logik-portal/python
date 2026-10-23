# Color Segment Fx
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Color Segment FX
Script Version: 1.5.1
Flame Version: 2025.1
Written by: Michael Vaglienty
Creation Date: 03.02.24
Update Date: 10.21.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Timeline

Description:

    Colors segments on selected sequence with selected FX type.

    Clear All Color removes color from every colored segment in the selected sequences.

URL:
    https://logik-portal.com/scripts/color_segment_fx

Menus:

    Right-Click on Sequence in Media Panel -> Color Segment FX

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.5.1 10.21.26
        - Fixed Apply Color stopping partway when a segment can't be read.
        - Fixed error when items other than sequences are selected along with a sequence.
        - Added Clear All Color button. Clears color from all colored segments in the selected sequences.
        - Fixed No Color and Clear All Color not clearing colors set in Flame.
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.5.0 03.24.26
        - Update to PyFlameLib v5.3.0.

    v1.4.0 07.10.25
        - Updated to PyFlameLib v5.0.0.
        - Escape key closes main window.
        - Window layer order in linux is now fixed.

    v1.3.0 03.16.25
        - Updated to PyFlameLib v4.3.0.
        - Added 'No Color' option to color menu and removed 'Remove Color' button.

    v1.2.0 12.27.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.

    v1.1.0 08.05.24
        - Updated to PyFlameLib v3.0.0.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os

import flame
from lib.pyflame_lib_color_segment_fx import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Color Segment FX'
SCRIPT_VERSION = 'v1.5.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class ColorSegmentFX:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        self.selection = selection

        # Only process sequences, other selected items have no versions
        self.sequences = [item for item in self.selection if isinstance(item, flame.PySequence)]

        # Get selected sequence name
        if len(self.sequences) == 1:
            self.sequence_name = str(self.sequences[0].name)[1:-1]
        else:
            self.sequence_name = 'Multiple Sequences Selected'

        # Get list of fx types in selected sequence
        self.fx_types = self.get_fx_list()
        if not self.fx_types:
            return

        # Switch to Timeline tab if not already there
        if flame.get_current_tab() != 'Timeline':
            flame.set_current_tab('Timeline')

        # Open main window
        self.main_window()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns
        -------
            PyFlameConfig:
                PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            config_values={
                'color': 'No Color',
                }
            )

        return settings

    def main_window(self) -> None:
        """
        Main Window
        ===========

        Build main window with FX type and color menus.
        """

        def close_window() -> None:
            """
            Close Window
            ============

            Close main window.
            """

            self.window.close()

        # ------------------------------------------------------------------------------
        # [Window Elements]
        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.apply_segment_color,
            escape_pressed=close_window,
            grid_layout_columns=4,
            grid_layout_rows=4,
            parent=None,
            )

        # Labels
        self.sequence_name_label = PyFlameLabel(
            text='Selected Sequence',
            )
        self.fx_type_label = PyFlameLabel(
            text='Segment FX Type',
            )
        self.color_label = PyFlameLabel(
            text='Color',
            )

        # Entry
        self.sequence_name_field = PyFlameEntry(
            text=self.sequence_name,
            read_only=True,
            )

        # Menu
        self.fx_type_menu = PyFlameMenu(
            text=self.fx_types[0],
            menu_options=self.fx_types,
            )

        # Color Menu
        self.color_menu = PyFlameColorMenu(
            color=self.settings.color,
            )

        # Buttons
        self.apply_color_button = PyFlameButton(
            text='Apply Color',
            connect=self.apply_segment_color,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )
        self.clear_all_color_button = PyFlameButton(
            text='Clear All Color',
            connect=self.clear_all_color,
            tooltip='Clears all colors on all clips in the selected sequences, whatever their FX type.',
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.window.grid_layout.addWidget(self.sequence_name_label, 0, 0)
        self.window.grid_layout.addWidget(self.sequence_name_field, 0, 1, 1, 3)

        self.window.grid_layout.addWidget(self.fx_type_label, 1, 0)
        self.window.grid_layout.addWidget(self.fx_type_menu, 1, 1)
        self.window.grid_layout.addWidget(self.color_label, 1, 2)
        self.window.grid_layout.addWidget(self.color_menu, 1, 3)

        self.window.grid_layout.addWidget(self.clear_all_color_button, 3, 0)
        self.window.grid_layout.addWidget(self.cancel_button, 3, 2)
        self.window.grid_layout.addWidget(self.apply_color_button, 3, 3)

    def get_fx_list(self) -> list:
        """
        Get FX List
        ===========

        Create a list of all segment fx types in selected sequence.

        Returns
        -------
            fx_types (list):
                List of all segment fx types in selected sequence.
        """

        fx_types = []

        for sequence in self.sequences:
            for version in sequence.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        try:
                            for tlfx in segment.effects:
                                if tlfx.type not in fx_types:
                                    fx_types.append(tlfx.type)
                        except Exception:
                            pass

        if not fx_types:
            PyFlameMessageWindow(
                message='No Timeline FX found in selected sequence',
                parent=None,
                )

        return fx_types

    def save_config(self) -> None:
        """
        Save Config
        ===========

        Save settings to config file.
        """

        self.settings.save_config(
            config_values={
                'color': self.color_menu.color,
                }
            )

        self.window.close()

    def clear_segment_color(self, segment) -> None:
        """
        Clear Segment Color
        ===================

        Clear color from segment.
        segment.clear_colour() only clears colors set through the API, not colors set in Flame's UI,
        so set a temporary color through the API first, then clear it.

        Args
        ----
            segment (PySegment): Segment to clear color from.
        """

        # Set temporary color through API so clear_colour() can clear it
        segment.colour = (1.0, 1.0, 1.0)
        segment.clear_colour()

    def apply_segment_color(self) -> None:
        """
        Apply Segment Color
        ===================

        Apply color to segments with selected fx type.
        """

        self.save_config()

        # color_name = self.color_menu.get_color()
        # rgba_value = self.color_menu.get_color_value()

        color_name = self.color_menu.color
        rgba_value = self.color_menu.color_value

        if color_name == 'No Color':
            # Search through segments in timeline for selected timeline fx and remove color.
            for sequence in self.sequences:
                for version in sequence.versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            try:
                                for tlfx in segment.effects:
                                    if tlfx.type == self.fx_type_menu.text:
                                        self.clear_segment_color(segment)
                            except Exception as e:
                                pyflame.print(f'Skipped segment {str(segment.name)[1:-1]}: {e}', print_type=PrintType.ERROR)
        else:
            # Search through segments in timeline for selected timeline fx and apply selected color.
            for sequence in self.sequences:
                for version in sequence.versions:
                    for track in version.tracks:
                        for segment in track.segments:
                            try:
                                for tlfx in segment.effects:
                                    if tlfx.type == self.fx_type_menu.text:
                                        segment.colour = rgba_value
                            except Exception as e:
                                pyflame.print(f'Skipped segment {str(segment.name)[1:-1]}: {e}', print_type=PrintType.ERROR)

        pyflame.print('Color applied to selected FX type segments.', text_color=TextColor.GREEN)

    def clear_all_color(self) -> None:
        """
        Clear All Color
        ===============

        Clear color from all segments in selected sequences, regardless of fx type.
        Black and no color can't be told apart, so clear is called on every segment.
        """

        self.window.close()

        # Clear color from every segment
        for sequence in self.sequences:
            for version in sequence.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        try:
                            self.clear_segment_color(segment)
                        except Exception as e:
                            pyflame.print(f'Skipped segment {str(segment.name)[1:-1]}: {e}', print_type=PrintType.ERROR)

        pyflame.print('Cleared color from all segments.', text_color=TextColor.GREEN)

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_seq(selection) -> bool:

    for item in selection:
        if isinstance(item, flame.PySequence):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Color Segment FX',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_seq,
                    'execute': ColorSegmentFX,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
