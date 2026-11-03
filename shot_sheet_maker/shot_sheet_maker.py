# Shot Sheet Maker
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Shot Sheet Maker
Script Version: 3.15.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 02.18.19
Update Date: 11.03.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Media Panel

Description:

    Create shot sheets from selected sequence clips that can be loaded into Excel, Google Sheets, or Numbers.

Usage:

    Shot sheets can be created individually for each sequence or all selected sequences can be added to a
    single spreadsheet as separate worksheets.

    Sequence should have all clips on one version/track.

    Options in the window: Sort By (Edit Order or Shot Name), thumbnail size, one workbook for all sequences,
    save the thumbnail images, reveal the export folder in Finder, Images in Cells (thumbnails inside their cells,
    Excel 365, Excel 2024 and Excel for the web only), a Clip Info column (source name/path/timecode, record
    timecode, shot and source length, shot frame in/out, comment) and up to 20 named columns.

    *** First time script is run it will need to install xlsxWriter - System password required for this ***
    This will need to happen for each new version of Flame (or updated to 3.2.9 if an older version is installed).

URL:
    https://logik-portal.com/scripts/shot_sheet_maker

Menus:

    Right-click on selected sequences in media panel -> Shot Sheet Maker

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v3.15.0 11.03.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Added Sort By. Shots can be listed by Shot Name (alphanumerically) or in Edit Order (timeline order, the 
          default).
        - An overwrite warning now lists any shot sheets or images folders that already exist in the export path. 
          Cancel writes nothing and keeps the window open.
        - Items that aren't sequences, such as folders, are now skipped. Before, a sequence selected with a folder 
          stopped the script.
        - Text starting with = is now written as text, not as a formula.
        - Every column named after the same clip info item is now filled. Before, only the first one was.
        - Every shot now gets its own row. Before, shots with the same name were merged into one row. Saved images 
          of shots with the same name get _2, _3, ... added.
        - Shot names with characters such as & or < no longer stop the export.
        - Sequence names that aren't allowed as Excel sheet names (too long, with [ ] : * ? / or a backslash, or 
          starting or ending with ') are now shortened or changed instead of stopping the export.
        - Sequence names that differ only in upper and lower case no longer stop the export or overwrite each other's 
          workbook.
        - In workbook and images folder names, / : and backslash from the sequence name are replaced with _. Unsafe 
          characters in saved image names are replaced with _.
        - If the export fails, an error is now shown and the window opens again. Before, the window closed with no 
          message.
        - Added Images in Cells. When on, thumbnails are placed inside their cells (Excel 365, Excel 2024 and Excel 
          for the web). 
        - Updated the bundled xlsxwriter to 3.2.9. Older installs are updated the next time the script opens (the 
          system password is asked for once).
        - Floating thumbnails now use xlsxwriter's own move and size with cells setting, so the workbook is no longer 
          unzipped and rezipped after it is written. A temp_xlsx folder in the export path is no longer deleted.
        - Fixed Clip Info showing the wrong values for Shot Length, Source Length and Comment.
        - Shot Frame In and Shot Frame Out are now added to Clip Info.
        - The Clip Info column is now created when only Shot Frame In, Shot Frame Out or Comment is selected.

    v3.14.0 06.18.26
        - Updated to PyFlameLib v5.4.0.

    v3.13.0 07.10.25
        - Images are linked to cells when opening shot sheet in Excel.
        - Option to save images to shot sheet export path.
        - Updated to PyFlameLib v5.0.0.
        - The tab key can now be used to cycle through all the entries in the Edit Column Names window.

    v3.12.0 04.03.25
        - Updated to PyFlameLib v4.3.0.

    v3.11.0 12.31.24
        - Updated to PyFlameLib v4.0.0.
        - Updated SCRIPT_PATH to use absolute path. Allows script to be installed in different locations.
        - Script now only works with Flame 2023.2+.

    v3.10.0 08.06.24
        - Updated to PyFlameLib v3.0.0.

    v3.9.1 06.06.24
        - Small UI fixes/adjustments.

    v3.9.0 01.21.24
        - Updates to UI/PySide.

    v3.8.0 11.16.23
        - Added ability to add Shot Frame In and Shot Frame Out to clip info column and column names.
        - Added drop down menus to add clip info to column names in Edit Column Names window.

    v3.7.1 11.07.23
        - Fixed incorrect path in script path check error message.

    v3.7.0 08.20.23
        - Updated to PyFlameLib v2.0.0.

    v3.6.0 06.26.23
        - Pressing return in the main window will now create shot sheets.
        - Updated script versioning to semantic versioning.
        - Updated xlsxwriter install for Flame 2024+.
        - Updated config loading/saving.
        - Fixed linux install problems.

    v3.5 01.05.23
        - Misc bug fixes.
        - Error window will now pop up if the selected export path is not writable.
        - Column names can be edited by clicking on the Edit Column Names button.
        - By using any of the following names for a column name, the corresponding clip info will be added to the cells
          in that column.
          For example, if you want to add the Shot Name to a cell, name the column 'Shot Name' and the shot name will
          be added to the cells in that column.

          Shot Name
          Source Name
          Source Path
          Source TC
          Source TC In
          Source TC Out
          Record TC
          Record TC In
          Record TC Out
          Shot Length
          Source Length
          Comment

    v3.4 10.04.22
        - Updated menus for Flame 2023.2+

    v3.3 08.04.22
        - Fixed bug where script would not work properly if 'Inclusive Out Marks' was selected in Flame Timeline
          Preferences.
        - Added ability to add segment comments to first column with Add Comment button.

    v3.2 07.21.22
        - Spreadsheets can now be created from multiple sequences.
        - When creating spreadsheets from multiple sequences, there is now the option(Create One Workbook) to create a
        single spreadsheet with all sequences
          added as separate worksheets.
        - Fixed export issues with 2023.1.
        - Messages print to Flame message window - Flame 2023.1 and later.

    v3.1 03.25.22
        - Updated UI for Flame 2023.
        - Moved UI widgets to external file.
        - Updated xlsxwriter module to 3.0.3.
        - Gaps in timeline no longer cause script to crash.
        - Misc improvements and bug fixes.
        - Config updated to XML.

    v3.0 05.28.21
        - Updated to be compatible with Flame 2022/Python 3.7.
        - Updated UI.
        - Added check to make sure sequence has only one version/track.
        - Added button to reveal spreadsheet in finder when done.

    v2.2 07.15.20
        - Script setup now in Flame Main Menu: Flame Main Menu -> pyFlame -> Shot Sheet Maker Setup.
        - Window now closes before overwrite warning appears so overwrite warning is not behind window.
        - Better sizing of image column to match size/ratio of sequence images.
        - The following information can be added to the spreadsheet for each shot:
            Source Clip Name
            Source Clip Path
            Source Timecode
            Record Timecode
            Shot Length - Length of shot minus handles
            Source Length - Length of shot plus handles

    v2.1 04.05.20
        - Fixed UI issues in Linux.

    v2.0 12.26.19
        - Up to 20 columns can now be added through the Edit Column Names button.
        - Thumbnail images used in the shot sheet can be saved if desired.
        - Misc. bug fixes.
"""

#-------------------------------------
# [Imports]
#-------------------------------------

from __future__ import annotations

import importlib
import os
import re
import shutil
import sys

import flame
from lib.pyflame_lib_shot_sheet_maker import *

#-------------------------------------
# [Constants]
#-------------------------------------

SCRIPT_NAME = 'Shot Sheet Maker'
SCRIPT_VERSION = 'v3.15.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
XLSXWRITER_VERSION = '3.2.9'
XLSXWRITER_TAR = f'xlsxwriter-{XLSXWRITER_VERSION}.tgz'

#-------------------------------------
# [Utilities]
#-------------------------------------

def unique_name(name: str, used_names: set) -> str:
    """
    Unique Name
    ===========

    Make a name unique, ignoring case, by adding _2, _3, ... Add the result to used_names.

    Args
    ----
        name (str):
            Name to make unique.

        used_names (set):
            Lowercase names already used. The returned name is added to it.

    Returns
    -------
        new_name (str): Unique name.
    """

    new_name = name
    count = 2
    while new_name.lower() in used_names:
        new_name = f'{name}_{count}'
        count += 1
    used_names.add(new_name.lower())

    return new_name

def safe_workbook_name(name: str, used_names: set) -> str:
    """
    Safe Workbook Name
    ==================

    Make a workbook or folder file name from a sequence name: replace / \\ and : with _, then make it unique ignoring case.

    Args
    ----
        name (str):
            Sequence name.

        used_names (set):
            Lowercase names already used in this run. The returned name is added to it.

    Returns
    -------
        file_name (str): Safe, unique file name without extension.
    """

    file_name = re.sub(r'[/\\:]', '_', name)

    return unique_name(file_name, used_names)

def safe_image_name(name: str, used_names: set) -> str:
    """
    Safe Image Name
    ===============

    Make an image file name from a shot name: replace anything other than letters, digits, _ - . and space
    with _, then make it unique ignoring case.

    Args
    ----
        name (str):
            Shot name.

        used_names (set):
            Lowercase names already used in this images folder. The returned name is added to it.

    Returns
    -------
        file_name (str): Safe, unique file name without extension.
    """

    file_name = re.sub(r'[^A-Za-z0-9_\-. ]', '_', name)

    return unique_name(file_name, used_names)

def safe_sheet_name(name: str, used_names: set) -> str:
    """
    Safe Sheet Name
    ===============

    Make a valid Excel worksheet name from a sequence name: replace [ ] : * ? / \\ with _, replace an apostrophe
    at the start or end with _, trim to 31 characters, then make it unique ignoring case by adding ' 2', ' 3', ...

    Args
    ----
        name (str):
            Sequence name.

        used_names (set):
            Lowercase sheet names already used in this workbook. The returned name is added to it.

    Returns
    -------
        sheet_name (str): Valid, unique worksheet name.
    """

    base_name = re.sub(r'[\[\]:*?/\\]', '_', name)[:31]
    if not base_name:
        base_name = 'Sheet'
    if base_name.startswith("'"):
        base_name = '_' + base_name[1:]
    if base_name.endswith("'"):
        base_name = base_name[:-1] + '_'

    # Add a number, keeping the name within 31 characters
    sheet_name = base_name
    count = 2
    while sheet_name.lower() in used_names:
        suffix = f' {count}'
        sheet_name = base_name[:31 - len(suffix)] + suffix
        count += 1
    used_names.add(sheet_name.lower())

    return sheet_name

def natural_sort_key(name: str) -> list:
    """
    Natural Sort Key
    ================

    Sort key for natural alphanumeric order ignoring case: numbers compare by value, so SH_2 comes before SH_10.

    Args
    ----
        name (str): Name to sort.

    Returns
    -------
        key (list): Text parts in lower case and number parts as ints, alternating.
    """

    # re.split with a capture group puts the digit runs at the odd indexes
    parts = re.split(r'(\d+)', name.casefold())

    return [int(part) if index % 2 else part for index, part in enumerate(parts)]

def get_mark(mark) -> object:
    """
    Get Mark
    ========

    Get the value of a sequence in or out mark.

    Args
    ----
        mark (PyAttribute):
            Sequence in_mark or out_mark.

    Returns
    -------
        value (object): Mark value (a PyTime), or None when there is no mark.
    """

    value = mark.get_value()
    if value is None or str(value).strip("'").upper() in ('', 'NULL'):
        return None

    return value

#-------------------------------------
# [Main Script]
#-------------------------------------

class ShotSheetMaker:

    def __init__(self, selection):

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Keep only items that have versions (sequences and clips), skip anything else such as folders
        self.selection = []
        for item in selection:
            if getattr(item, 'versions', None):
                self.selection.append(item)
            else:
                pyflame.print(f'Skipped, not a sequence: {str(item.name)[1:-1]}', print_type=PrintType.WARNING)

        if not self.selection:
            PyFlameMessageWindow(
                message='Select one or more sequences.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Make sure sequences only have one version/track
        for item in self.selection:
            if len(item.versions) > 1:
                PyFlameMessageWindow(
                    message='Sequences can only have one version/track',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return
            elif len(item.versions[0].tracks) > 1:
                PyFlameMessageWindow(
                    message='Sequences can only have one version/track',
                    message_type=MessageType.ERROR,
                    parent=None,
                    )
                return

        # Make sure no two sequences are named the same
        sequence_names = [str(seq.name)[1:-1] for seq in self.selection]
        duplicate_names = [name for name in sequence_names if sequence_names.count(name) > 1]
        if duplicate_names:
            PyFlameMessageWindow(
                message='No two sequences can have the same name.\n\nRename sequences and try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return

        # Define paths
        self.temp_path = os.path.join(SCRIPT_PATH, 'temp')

        # Create temp directory. If it already exists, delete it and create a new one.
        if os.path.isdir(self.temp_path):
            shutil.rmtree(self.temp_path)
        os.mkdir(self.temp_path)

        # Get Flame variables
        self.flame_project_name = flame.projects.current_project.name
        self.current_flame_version = flame.get_version()

        # Initialize misc. variables
        self.thumb_nail_height = ''
        self.thumb_nail_width = ''
        self.x_offset = ''
        self.y_offset = ''
        self.column_width = ''
        self.row_height = ''
        self.temp_image_path = ''

        # Initialize exporter
        self.exporter = flame.PyExporter()
        self.exporter.foreground = True
        self.exporter.export_between_marks = True

        # Get jpeg export preset
        preset_dir = flame.PyExporter.get_presets_dir(
            flame.PyExporter.PresetVisibility.Autodesk,
            flame.PyExporter.PresetType.Image_Sequence)
        jpg_preset_path = os.path.join(preset_dir, "Jpeg", "Jpeg (8-bit).xml")

        # Copy jpeg export preset to temp directory
        self.temp_export_preset = os.path.join(self.temp_path, 'Temp_Export_Preset.xml')
        shutil.copy(jpg_preset_path, self.temp_export_preset)

        # Make sure xlsxwriter is installed, if not, install it. Otherwise, open window.
        xlsxwriter_installed = self.xlsxwriter_check()

        if xlsxwriter_installed:
            return self.main_window()
        return self.install_xlsxwriter()

    def load_config(self) -> PyFlameConfig:
        """
        Load Config
        ===========

        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
        --------
            PyFlameConfig:
                PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            config_values={
                'export_path'       : '/opt/Autodesk',
                'thumbnail_size'    : 'Medium',
                'sort_by'           : 'Edit Order',
                'one_workbook'      : False,
                'reveal_in_finder'  : False,
                'add_source_name'   : False,
                'add_source_path'   : False,
                'add_source_tc'     : False,
                'add_record_tc'     : False,
                'add_shot_length'   : False,
                'add_source_length' : False,
                'add_shot_frame_in' : False,
                'add_shot_frame_out': False,
                'add_comment'       : False,
                'save_images'       : False,
                'images_in_cells'   : False,
                'column_01_name'    : 'Internal Notes',
                'column_02_name'    : 'Client Notes',
                'column_03_name'    : 'Shot Description',
                'column_04_name'    : 'Task',
                'column_05_name'    : '',
                'column_06_name'    : '',
                'column_07_name'    : '',
                'column_08_name'    : '',
                'column_09_name'    : '',
                'column_10_name'    : '',
                'column_11_name'    : '',
                'column_12_name'    : '',
                'column_13_name'    : '',
                'column_14_name'    : '',
                'column_15_name'    : '',
                'column_16_name'    : '',
                'column_17_name'    : '',
                'column_18_name'    : '',
                'column_19_name'    : '',
                'column_20_name'    : '',
                }
            )

        return settings

    def xlsxwriter_version_ok(self, version: str) -> bool:
        """
        XlsxWriter Version OK
        =====================

        Check if an xlsxwriter version is at least the bundled version (XLSXWRITER_VERSION).
        A version that can't be read as numbers counts as too old.

        Args
        ----
            version (str): xlsxwriter version string, e.g. '3.2.9'.

        Returns
        -------
            bool:
                True if version is the bundled version or newer, False if not.
        """

        try:
            installed_version = tuple(int(part) for part in str(version).split('.'))
            required_version = tuple(int(part) for part in XLSXWRITER_VERSION.split('.'))
        except Exception:
            return False

        return installed_version >= required_version

    def xlsxwriter_check(self) -> bool:
        """
        XlsxWriter Check
        ================

        Check if xlsxwriter is installed by attempting to import it, and that it is at least the bundled version (XLSXWRITER_VERSION).

        Returns
        -------
            bool:
                True if xlsxwriter is installed and new enough, False if not.
        """

        try:
            import xlsxwriter
        except Exception:
            pyflame.print('XlsxWriter Not Found, Installing...')

            return False

        # Check installed version is new enough
        version = getattr(xlsxwriter, '__version__', '')
        if not self.xlsxwriter_version_ok(version):
            pyflame.print(f'XlsxWriter {version} Found, Older Than {XLSXWRITER_VERSION}, Upgrading...')

            return False

        pyflame.print(f'XlsxWriter {version} Successfully Imported')

        return True

    def install_xlsxwriter(self) -> None:
        """
        Install XlsxWriter
        ==================

        Install or update xlsxwriter python package to the bundled version (XLSXWRITER_VERSION).
        Then reload xlsxwriter in this Flame session and open the main window if the new version imports.
        """

        def install_failed() -> None:
            """
            Install Failed
            ==============

            Show install failed error message.
            """

            PyFlameMessageWindow(
                message=f'xlsxwriter {XLSXWRITER_VERSION} install failed.\n\nCheck the Flame shell for errors and try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )

        password_window = PyFlamePasswordWindow(
            text=f'System password is required to install or update the xlsxwriter python package to {XLSXWRITER_VERSION}.',
            parent=None,
            )
        #password_window.show()
        system_password = password_window.password

        if system_password:
            python_install_dir = pyflame.get_flame_python_packages_path()
            print('python Install Directory:', python_install_dir)

            # Untar xlsxwriter
            xlsxwriter_tar = os.path.join(SCRIPT_PATH, 'assets/xlsxwriter', XLSXWRITER_TAR)

            pyflame.untar(
                tar_file_path=xlsxwriter_tar,
                untar_path=python_install_dir,
                sudo_password=system_password,
                )

            # Remove any loaded xlsxwriter modules so this Flame session imports the new version
            for module_name in list(sys.modules):
                if module_name == 'xlsxwriter' or module_name.startswith('xlsxwriter.'):
                    del sys.modules[module_name]
            importlib.invalidate_caches()

            # Import xlsxwriter again and check the new version was installed
            try:
                xlsxwriter = importlib.import_module('xlsxwriter')
            except Exception as e:
                pyflame.print(f'XlsxWriter Import Failed: {e}', print_type=PrintType.ERROR)
                install_failed()

                return

            version = getattr(xlsxwriter, '__version__', '')
            if not self.xlsxwriter_version_ok(version):
                pyflame.print(f'XlsxWriter Still {version} After Install', print_type=PrintType.ERROR)
                install_failed()

                return

            PyFlameMessageWindow(
                message=f'Python xlsxWriter module {version} installed.',
                title=f'{SCRIPT_NAME}: Operation Complete',
                parent=None,
                )
            self.main_window()

    #-------------------------------------
    # [Windows]
    #-------------------------------------

    def main_window(self):

        def export_path_browse():
            """
            Export Path Browse
            ==================

            Browse for export path. If path is valid, set export path entry to selected path.
            """

            export_path = pyflame.file_browser(
                path=self.export_path_entry.text,
                title='Select Export Path',
                select_directory=True,
                window_to_hide=[self.window],
                )

            if export_path:
                self.export_path_entry.text = export_path

        def save_config():
            """
            Save Config
            ===========

            Save config values to config file. Then create shot sheets.
            """

            # Check export path
            self.settings.export_path = self.export_path_entry.text

            if not os.path.isdir(self.settings.export_path):
                PyFlameMessageWindow(
                    message='Export path not found - Select new path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Check if export path is writeable
            if not os.access(self.settings.export_path, os.W_OK):
                PyFlameMessageWindow(
                    message='Unable to export to selected path - Select new path.',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )
                return

            # Ask before overwriting files this run will write. Done before the config is saved so Cancel writes nothing.
            existing_names = []
            for export_names in self.get_export_names(self.one_workbook_push_button.checked):
                output_names = [export_names['xlsx_name']]
                if self.save_images_push_button.checked:
                    output_names.append(export_names['images_name'])
                for output_name in output_names:
                    if output_name not in existing_names and os.path.exists(os.path.join(self.export_path_entry.text, output_name)):
                        existing_names.append(output_name)

            if existing_names:
                listed_names = '\n'.join(existing_names[:10])
                if len(existing_names) > 10:
                    listed_names += f'\nand {len(existing_names) - 10} more'
                if not PyFlameMessageWindow(
                    message=f'These files already exist in the export path:\n\n{listed_names}\n\nOverwrite them?',
                    message_type=MessageType.WARNING,
                    parent=self.window,
                    ):
                    return

            self.settings.save_config(
                config_values={
                    'export_path': self.export_path_entry.text,
                    'thumbnail_size': self.thumbnail_menu.text,
                    'sort_by': self.sort_by_menu.text,
                    'one_workbook': self.one_workbook_push_button.checked,
                    'reveal_in_finder': self.reveal_in_finder_push_button.checked,
                    'add_source_name': self.source_name_push_button.checked,
                    'add_source_path': self.source_path_push_button.checked,
                    'add_source_tc': self.source_tc_push_button.checked,
                    'add_record_tc': self.record_tc_push_button.checked,
                    'add_shot_length': self.shot_length_push_button.checked,
                    'add_source_length': self.source_length_push_button.checked,
                    'add_shot_frame_in':self.shot_frame_in_push_button.checked,
                    'add_shot_frame_out': self.shot_frame_out_push_button.checked,
                    'add_comment': self.comment_push_button.checked,
                    'save_images': self.save_images_push_button.checked,
                    'images_in_cells': self.images_in_cells_push_button.checked,
                    }
                )

            # Hide window
            self.window.hide()

            # Create shot sheets. On failure, report the error and show the window again so settings can be changed.
            self.workbook = None
            try:
                self.create_shot_sheets()
            except Exception as e:
                pyflame.print(f'Shot Sheets Not Created: {e}', print_type=PrintType.ERROR)

                # Drop the open workbook without closing it. Closing would write a partial file over any earlier good one.
                self.workbook = None

                self.window.show()
                PyFlameMessageWindow(
                    message=f'Shot sheets could not be created.\n\nError: {e}',
                    message_type=MessageType.ERROR,
                    parent=self.window,
                    )

                return

            # Close window
            self.window.close()

        def close_window() -> None:
            """
            Close Window
            ============

            Remove the script's temp folder, then close the window without exporting.
            """

            try:
                shutil.rmtree(self.temp_path)
            except Exception:
                pass

            self.window.close()

        def images_in_cells_info() -> None:
            """
            Images In Cells Info
            ====================

            When Images in Cells is turned on, explain what it does and which apps support it.
            """

            if not self.images_in_cells_push_button.checked:
                return

            PyFlameMessageWindow(
                message=(
                    "Images in Cells puts each thumbnail inside its cell, using Excel's Place in Cell pictures, instead of floating it over the cell.\n\n"
                    'Excel 365, Excel 2024 and Excel for the web: thumbnails stay locked in their cells and move, resize, sort and filter with them.\n\n'
                    'Excel 2021 and older: the cells show #VALUE! instead of the thumbnail.\n\n'
                    "Apple Numbers: the cells are empty. Numbers doesn't support pictures in cells.\n\n"
                    "Turn this off to use floating thumbnails, which show in every app but don't follow cells that are resized later."
                    ),
                message_type=MessageType.INFO,
                parent=self.window,
                )

        #-------------------------------------
        # [Main Window]
        #-------------------------------------

        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}</small>',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=5,
            grid_layout_rows=12,
            parent=None,
            )

        # Labels
        self.spread_sheet_settings_label = PyFlameLabel(
            text='Spreadsheet Settings',
            style=Style.UNDERLINE,
            )
        self.export_path_label = PyFlameLabel(
            text='Export Path',
            )
        self.thumbnail_size_label = PyFlameLabel(
            text='Thumbnail Size',
            )
        self.sort_by_label = PyFlameLabel(
            text='Sort By',
            )
        self.clip_info_label = PyFlameLabel(
            text='Clip Info Column',
            style=Style.UNDERLINE,
            )

        # Entries
        self.export_path_entry = PyFlameEntry(
            text=self.settings.export_path,
            )

        # Menu. An unknown saved Sort By value falls back to Edit Order, not the menu's first option.
        sort_by = self.settings.sort_by
        if sort_by not in ('Shot Name', 'Edit Order'):
            sort_by = 'Edit Order'

        self.thumbnail_menu = PyFlameMenu(
            text=self.settings.thumbnail_size,
            menu_options=[
                'Large',
                'Medium',
                'Small',
                ],
            )
        self.sort_by_menu = PyFlameMenu(
            text=sort_by,
            menu_options=[
                'Shot Name',
                'Edit Order',
                ],
            )

        # Push Buttons
        self.one_workbook_push_button = PyFlamePushButton(
            text='Create One Workbook',
            checked=self.settings.one_workbook,
            tooltip='Create one workbook containing separate sheets for each sequence',
            )
        self.reveal_in_finder_push_button = PyFlamePushButton(
            text='Reveal in Finder',
            checked=self.settings.reveal_in_finder,
            )

        self.source_name_push_button = PyFlamePushButton(
            text='Source Name',
            checked=self.settings.add_source_name,
            )
        self.source_path_push_button = PyFlamePushButton(
            text='Source Path',
            checked=self.settings.add_source_path,
            )
        self.source_tc_push_button = PyFlamePushButton(
            text='Source Timecode',
            checked=self.settings.add_source_tc,
            )
        self.record_tc_push_button = PyFlamePushButton(
            text='Record Timecode',
            checked=self.settings.add_record_tc,
            )
        self.shot_length_push_button = PyFlamePushButton(
            text='Shot Length',
            checked=self.settings.add_shot_length,
            )
        self.source_length_push_button = PyFlamePushButton(
            text='Source Length',
            checked=self.settings.add_source_length,
            )
        self.shot_frame_in_push_button = PyFlamePushButton(
            text='Shot Frame In',
            checked=self.settings.add_shot_frame_in,
            )
        self.shot_frame_out_push_button = PyFlamePushButton(
            text='Shot Frame Out',
            checked=self.settings.add_shot_frame_out,
            )
        self.comment_push_button = PyFlamePushButton(
            text='Comment',
            checked=self.settings.add_comment,
            )
        self.save_images_push_button = PyFlamePushButton(
            text='Save Images',
            checked=self.settings.save_images,
            )
        self.images_in_cells_push_button = PyFlamePushButton(
            text='Images in Cells',
            checked=self.settings.images_in_cells,
            connect=images_in_cells_info, # Explain Images in Cells when it's turned on
            )

        # Buttons
        self.export_path_browse_button = PyFlameButton(
            text='Browse',
            connect=export_path_browse,
            )
        self.edit_column_names_button = PyFlameButton(
            text='Edit Column Names',
            connect=self.edit_column_names_window,
            )
        self.create_button = PyFlameButton(
            text='Create',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.window.grid_layout.addWidget(self.export_path_label, 0, 0)
        self.window.grid_layout.addWidget(self.export_path_entry, 0, 1, 1, 3)
        self.window.grid_layout.addWidget(self.export_path_browse_button, 0, 4)

        self.window.grid_layout.addWidget(self.spread_sheet_settings_label, 3, 0, 1, 5)
        self.window.grid_layout.addWidget(self.sort_by_label, 4, 0)
        self.window.grid_layout.addWidget(self.sort_by_menu, 4, 1)
        self.window.grid_layout.addWidget(self.thumbnail_size_label, 5, 0)
        self.window.grid_layout.addWidget(self.thumbnail_menu, 5, 1)
        self.window.grid_layout.addWidget(self.edit_column_names_button, 4, 3)
        self.window.grid_layout.addWidget(self.one_workbook_push_button, 4, 4)
        self.window.grid_layout.addWidget(self.save_images_push_button, 5, 4)
        self.window.grid_layout.addWidget(self.reveal_in_finder_push_button, 6, 4)
        self.window.grid_layout.addWidget(self.images_in_cells_push_button, 7, 4)

        self.window.grid_layout.addWidget(self.clip_info_label, 6, 0, 1, 3)

        self.window.grid_layout.addWidget(self.source_name_push_button, 7, 0)
        self.window.grid_layout.addWidget(self.source_path_push_button, 7, 1)
        self.window.grid_layout.addWidget(self.source_tc_push_button, 7, 2)

        self.window.grid_layout.addWidget(self.record_tc_push_button, 8, 0)
        self.window.grid_layout.addWidget(self.shot_length_push_button, 8, 1)
        self.window.grid_layout.addWidget(self.source_length_push_button, 8, 2)

        self.window.grid_layout.addWidget(self.shot_frame_in_push_button, 9, 0)
        self.window.grid_layout.addWidget(self.shot_frame_out_push_button, 9, 1)
        self.window.grid_layout.addWidget(self.comment_push_button, 9, 2)

        self.window.grid_layout.addWidget(self.cancel_button, 11, 3)
        self.window.grid_layout.addWidget(self.create_button, 11, 4)

        #-------------------------------------

        self.export_path_entry.set_focus()

    def edit_column_names_window(self):

        def save_config():
            """
            Save Config
            ===========

            Save column names to config file. Then close window.
            """

            self.settings.save_config(
                config_values={
                    'column_01_name': self.column_01_entry.text,
                    'column_02_name': self.column_02_entry.text,
                    'column_03_name': self.column_03_entry.text,
                    'column_04_name': self.column_04_entry.text,
                    'column_05_name': self.column_05_entry.text,
                    'column_06_name': self.column_06_entry.text,
                    'column_07_name': self.column_07_entry.text,
                    'column_08_name': self.column_08_entry.text,
                    'column_09_name': self.column_09_entry.text,
                    'column_10_name': self.column_10_entry.text,
                    'column_11_name': self.column_11_entry.text,
                    'column_12_name': self.column_12_entry.text,
                    'column_13_name': self.column_13_entry.text,
                    'column_14_name': self.column_14_entry.text,
                    'column_15_name': self.column_15_entry.text,
                    'column_16_name': self.column_16_entry.text,
                    'column_17_name': self.column_17_entry.text,
                    'column_18_name': self.column_18_entry.text,
                    'column_19_name': self.column_19_entry.text,
                    'column_20_name': self.column_20_entry.text,
                    }
                )

            self.edit_window.close()

        def close_window():

            self.edit_window.close()

        #-------------------------------------
        # [Edit Window]
        #-------------------------------------

        self.edit_window = PyFlameWindow(
            title='Edit Column Names',
            return_pressed=save_config,
            escape_pressed=close_window,
            grid_layout_columns=9,
            grid_layout_rows=12,
            grid_layout_adjust_column_widths={
                0: 100,
                4: 50,
                5: 100,
                },
            parent=self.window,
            )

        # Labels
        self.column_names_label = PyFlameLabel(
            text='Shot Sheet Column Names',
            style=Style.UNDERLINE,
            )
        self.column_01_label = PyFlameLabel(
            text='Column 01',
            )
        self.column_02_label = PyFlameLabel(
            text='Column 02',
            )
        self.column_03_label = PyFlameLabel(
            text='Column 03',
            )
        self.column_04_label = PyFlameLabel(
            text='Column 04',
            )
        self.column_05_label = PyFlameLabel(
            text='Column 05',
            )
        self.column_06_label = PyFlameLabel(
            text='Column 06',
            )
        self.column_07_label = PyFlameLabel(
            text='Column 07',
            )
        self.column_08_label = PyFlameLabel(
            text='Column 08',
            )
        self.column_09_label = PyFlameLabel(
            text='Column 09',
            )
        self.column_10_label = PyFlameLabel(
            text='Column 10',
            )
        self.column_11_label = PyFlameLabel(
            text='Column 11',
            )
        self.column_12_label = PyFlameLabel(
            text='Column 12',
            )
        self.column_13_label = PyFlameLabel(
            text='Column 13',
            )
        self.column_14_label = PyFlameLabel(
            text='Column 14',
            )
        self.column_15_label = PyFlameLabel(
            text='Column 15',
            )
        self.column_16_label = PyFlameLabel(
            text='Column 16',
            )
        self.column_17_label = PyFlameLabel(
            text='Column 17',
            )
        self.column_18_label = PyFlameLabel(
            text='Column 18',
            )
        self.column_19_label = PyFlameLabel(
            text='Column 19',
            )
        self.column_20_label = PyFlameLabel(
            text='Column 20',
            )

        # Entries
        self.column_01_entry = PyFlameEntry(
            text=self.settings.column_01_name,
            )
        self.column_02_entry = PyFlameEntry(
            text=self.settings.column_02_name,
            )
        self.column_03_entry = PyFlameEntry(
            text=self.settings.column_03_name,
            )
        self.column_04_entry = PyFlameEntry(
            text=self.settings.column_04_name,
            )
        self.column_05_entry = PyFlameEntry(
            text=self.settings.column_05_name,
            )
        self.column_06_entry = PyFlameEntry(
            text=self.settings.column_06_name,
            )
        self.column_07_entry = PyFlameEntry(
            text=self.settings.column_07_name,
            )
        self.column_08_entry = PyFlameEntry(
            text=self.settings.column_08_name,
            )
        self.column_09_entry = PyFlameEntry(
            text=self.settings.column_09_name,
            )
        self.column_10_entry = PyFlameEntry(
            text=self.settings.column_10_name,
            )
        self.column_11_entry = PyFlameEntry(
            text=self.settings.column_11_name,
            )
        self.column_12_entry = PyFlameEntry(
            text=self.settings.column_12_name,
            )
        self.column_13_entry = PyFlameEntry(
            text=self.settings.column_13_name,
            )
        self.column_14_entry = PyFlameEntry(
            text=self.settings.column_14_name,
            )
        self.column_15_entry = PyFlameEntry(
            text=self.settings.column_15_name,
            )
        self.column_16_entry = PyFlameEntry(
            text=self.settings.column_16_name,
            )
        self.column_17_entry = PyFlameEntry(
            text=self.settings.column_17_name,
            )
        self.column_18_entry = PyFlameEntry(
            text=self.settings.column_18_name,
            )
        self.column_19_entry = PyFlameEntry(
            text=self.settings.column_19_name,
            )
        self.column_20_entry = PyFlameEntry(
            text=self.settings.column_20_name,
            )

        # Token Push Button Menus
        clip_info_tokens = {
            'Shot Name': 'Shot Name',
            'Source Name': 'Source Name',
            'Source Path': 'Source Path',
            'Source TC': 'Source TC',
            'Source TC In': 'Source TC In',
            'Source TC Out': 'Source TC Out',
            'Record TC': 'Record TC',
            'Record TC In': 'Record TC In',
            'Record TC Out': 'Record TC Out',
            'Shot Frame In': 'Shot Frame In',
            'Shot Frame Out': 'Shot Frame Out',
            'Shot Length': 'Shot Length',
            'Source Length': 'Source Length',
            'Comment': 'Comment',
            }

        self.column_01_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_01_entry,
            clear_dest=True,
            )
        self.column_02_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_02_entry,
            clear_dest=True,
            )
        self.column_03_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_03_entry,
            clear_dest=True,
            )
        self.column_04_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_04_entry,
            clear_dest=True,
            )
        self.column_05_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_05_entry,
            clear_dest=True,
            )
        self.column_06_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_06_entry,
            clear_dest=True,
            )
        self.column_07_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_07_entry,
            clear_dest=True,
            )
        self.column_08_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_08_entry,
            clear_dest=True,
            )
        self.column_09_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_09_entry,
            clear_dest=True,
            )
        self.column_10_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_10_entry,
            clear_dest=True,
            )
        self.column_11_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_11_entry,
            clear_dest=True,
            )
        self.column_12_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_12_entry,
            clear_dest=True,
            )
        self.column_13_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_13_entry,
            clear_dest=True,
            )
        self.column_14_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_14_entry,
            clear_dest=True,
            )
        self.column_15_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_15_entry,
            clear_dest=True,
            )
        self.column_16_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_16_entry,
            clear_dest=True,
            )
        self.column_17_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_17_entry,
            clear_dest=True,
            )
        self.column_18_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_18_entry,
            clear_dest=True,
            )
        self.column_19_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_19_entry,
            clear_dest=True,
            )
        self.column_20_token_menu = PyFlameTokenMenu(
            text='Add Clip Info',
            token_dict=clip_info_tokens,
            token_dest=self.column_20_entry,
            clear_dest=True,
            )

        # Buttons
        self.save_columns_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.edit_cancel_button = PyFlameButton(
            text='Cancel',
            connect=close_window,
            )

        #-------------------------------------
        # [Widget Layout]
        #-------------------------------------

        self.edit_window.grid_layout.addWidget(self.column_names_label, 0, 0, 1, 9)

        self.edit_window.grid_layout.addWidget(self.column_01_label, 1, 0)
        self.edit_window.grid_layout.addWidget(self.column_02_label, 2, 0)
        self.edit_window.grid_layout.addWidget(self.column_03_label, 3, 0)
        self.edit_window.grid_layout.addWidget(self.column_04_label, 4, 0)
        self.edit_window.grid_layout.addWidget(self.column_05_label, 5, 0)
        self.edit_window.grid_layout.addWidget(self.column_06_label, 6, 0)
        self.edit_window.grid_layout.addWidget(self.column_07_label, 7, 0)
        self.edit_window.grid_layout.addWidget(self.column_08_label, 8, 0)
        self.edit_window.grid_layout.addWidget(self.column_09_label, 9, 0)
        self.edit_window.grid_layout.addWidget(self.column_10_label, 10, 0)

        self.edit_window.grid_layout.addWidget(self.column_11_label, 1, 5)
        self.edit_window.grid_layout.addWidget(self.column_12_label, 2, 5)
        self.edit_window.grid_layout.addWidget(self.column_13_label, 3, 5)
        self.edit_window.grid_layout.addWidget(self.column_14_label, 4, 5)
        self.edit_window.grid_layout.addWidget(self.column_15_label, 5, 5)
        self.edit_window.grid_layout.addWidget(self.column_16_label, 6, 5)
        self.edit_window.grid_layout.addWidget(self.column_17_label, 7, 5)
        self.edit_window.grid_layout.addWidget(self.column_18_label, 8, 5)
        self.edit_window.grid_layout.addWidget(self.column_19_label, 9, 5)
        self.edit_window.grid_layout.addWidget(self.column_20_label, 10, 5)

        self.edit_window.grid_layout.addWidget(self.column_01_entry, 1, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_02_entry, 2, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_03_entry, 3, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_04_entry, 4, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_05_entry, 5, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_06_entry, 6, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_07_entry, 7, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_08_entry, 8, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_09_entry, 9, 1, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_10_entry, 10, 1, 1, 2)

        self.edit_window.grid_layout.addWidget(self.column_11_entry, 1, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_12_entry, 2, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_13_entry, 3, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_14_entry, 4, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_15_entry, 5, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_16_entry, 6, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_17_entry, 7, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_18_entry, 8, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_19_entry, 9, 6, 1, 2)
        self.edit_window.grid_layout.addWidget(self.column_20_entry, 10, 6, 1, 2)

        self.edit_window.grid_layout.addWidget(self.column_01_token_menu, 1, 3)
        self.edit_window.grid_layout.addWidget(self.column_02_token_menu, 2, 3)
        self.edit_window.grid_layout.addWidget(self.column_03_token_menu, 3, 3)
        self.edit_window.grid_layout.addWidget(self.column_04_token_menu, 4, 3)
        self.edit_window.grid_layout.addWidget(self.column_05_token_menu, 5, 3)
        self.edit_window.grid_layout.addWidget(self.column_06_token_menu, 6, 3)
        self.edit_window.grid_layout.addWidget(self.column_07_token_menu, 7, 3)
        self.edit_window.grid_layout.addWidget(self.column_08_token_menu, 8, 3)
        self.edit_window.grid_layout.addWidget(self.column_09_token_menu, 9, 3)
        self.edit_window.grid_layout.addWidget(self.column_10_token_menu, 10, 3)

        self.edit_window.grid_layout.addWidget(self.column_11_token_menu, 1, 8)
        self.edit_window.grid_layout.addWidget(self.column_12_token_menu, 2, 8)
        self.edit_window.grid_layout.addWidget(self.column_13_token_menu, 3, 8)
        self.edit_window.grid_layout.addWidget(self.column_14_token_menu, 4, 8)
        self.edit_window.grid_layout.addWidget(self.column_15_token_menu, 5, 8)
        self.edit_window.grid_layout.addWidget(self.column_16_token_menu, 6, 8)
        self.edit_window.grid_layout.addWidget(self.column_17_token_menu, 7, 8)
        self.edit_window.grid_layout.addWidget(self.column_18_token_menu, 8, 8)
        self.edit_window.grid_layout.addWidget(self.column_19_token_menu, 9, 8)
        self.edit_window.grid_layout.addWidget(self.column_20_token_menu, 10, 8)

        self.edit_window.grid_layout.addWidget(self.edit_cancel_button, 12, 7)
        self.edit_window.grid_layout.addWidget(self.save_columns_button, 12, 8)

        #-------------------------------------

        self.edit_window.tab_order = [
            self.column_01_entry,
            self.column_02_entry,
            self.column_03_entry,
            self.column_04_entry,
            self.column_05_entry,
            self.column_06_entry,
            self.column_07_entry,
            self.column_08_entry,
            self.column_09_entry,
            self.column_10_entry,
            self.column_11_entry,
            self.column_12_entry,
            self.column_13_entry,
            self.column_14_entry,
            self.column_15_entry,
            self.column_16_entry,
            self.column_17_entry,
            self.column_18_entry,
            self.column_19_entry,
            self.column_20_entry,
            ]

        self.column_01_entry.set_focus()

    #-------------------------------------

    def get_export_names(self, one_workbook: bool) -> list:
        """
        Get Export Names
        ================

        Sort the selected sequences by name and work out the workbook and images folder names each one is exported to.
        Used by the overwrite check and by create_shot_sheets, so both use the same names.

        Args
        ----
            one_workbook (bool):
                True when all sequences go into Shot_Sheets.xlsx.

        Returns
        -------
            export_names (list): One dict per sequence, in export order, with sequence, seq_name, file_name, xlsx_name and images_name.
        """

        # Sort selected sequences by name
        sequence_names = [str(seq.name)[1:-1] for seq in self.selection]
        sequence_names.sort()

        sorted_sequences = []
        for name in sequence_names:
            for seq in self.selection:
                if str(seq.name)[1:-1] == name:
                    sorted_sequences.append(seq)

        # Safe file names, unique ignoring case in this run, used for workbook and images folder names
        used_file_names = set()
        export_names = []
        for sequence in sorted_sequences:
            seq_name = str(sequence.name)[1:-1]
            file_name = safe_workbook_name(seq_name, used_file_names)
            export_names.append({
                'sequence': sequence,
                'seq_name': seq_name,
                'file_name': file_name,
                'xlsx_name': 'Shot_Sheets.xlsx' if one_workbook else file_name + '.xlsx',
                'images_name': f'{file_name}_images',
                })

        return export_names

    def create_shot_sheets(self):
        """
        Create Shot Sheets
        ==================

        Create shot sheets from selected sequences. Export to xlsx format. Open in Finder if selected.
        """
        import xlsxwriter

        def save_images(images_name: str) -> None:
            """
            Save Images
            ===========

            Save images to export path if selected. Images are named after their shots, duplicates get _2, _3, ...

            Args
            ----
                images_name (str): Name of the sequence's images folder.
            """

            # Copy images to export path
            if self.settings.save_images:
                image_path = os.path.join(self.export_path_entry.text, images_name)
                if not os.path.exists(image_path):
                    os.makedirs(image_path)
                used_image_names = set()
                for shot in self.shot_list:
                    image_name = safe_image_name(shot['shot_name'] or 'shot', used_image_names) + '.jpg'
                    shutil.copy(os.path.join(self.temp_image_path, shot['image_name'] + '.jpg'), os.path.join(image_path, image_name))


        # Sorted sequences with their workbook and images folder names
        export_names = self.get_export_names(self.settings.one_workbook)

        # Create workbooks. Text starting with = is written as text, not as a formula.
        if self.settings.one_workbook:

            xlsx_path = os.path.join(self.export_path_entry.text, 'Shot_Sheets.xlsx')

            # Create single workbook with worksheets for each sequence
            workbook = xlsxwriter.Workbook(xlsx_path, {'strings_to_formulas': False})
            self.workbook = workbook
            used_sheet_names = set()

            for names in export_names:
                sequence = names['sequence']
                seq_name = names['seq_name']
                sheet_name = safe_sheet_name(seq_name, used_sheet_names)

                # Get shot info and export thumbnails
                self.get_shots(sequence, names['file_name'])

                # Create worksheet
                self.create_sequence_worksheet(workbook, seq_name, sheet_name)

                # Save images
                save_images(names['images_name'])

            # Close workbook
            workbook.close()
            self.workbook = None

        else:
            # Create workbook/worksheet for each sequence
            for names in export_names:
                sequence = names['sequence']
                seq_name = names['seq_name']
                sheet_name = safe_sheet_name(seq_name, set())

                xlsx_path = os.path.join(self.export_path_entry.text, names['xlsx_name'])

                workbook = xlsxwriter.Workbook(xlsx_path, {'strings_to_formulas': False})
                self.workbook = workbook

                # Get shot info and export thumbnails
                self.get_shots(sequence, names['file_name'])

                # Create worksheet
                self.create_sequence_worksheet(workbook, seq_name, sheet_name)

                # Save images
                save_images(names['images_name'])

                # Close workbook
                workbook.close()
                self.workbook = None

        # Delete temp directory
        shutil.rmtree(self.temp_path)

        # Close window
        self.window.close()

        # Show message window
        PyFlameMessageWindow(
            message=f'Shot Sheet(s) Exported:\n\n{self.export_path_entry.text}',
            title=f'{SCRIPT_NAME}: Export Complete',
            parent=self.window,
            )

        if self.settings.reveal_in_finder:
            pyflame.open_in_finder(
                path=self.export_path_entry.text,
                )
            pyflame.print('Finder opened')

        print('Done.\n')

    def get_shots(self, sequence, file_name: str) -> None:
        """
        Get Shots
        =========

        Export thumbnails and get shot info for all shots in selected sequence

        Args
        ----
            sequence (PySequence):
                Sequence to get shots from.

            file_name (str):
                Safe file name of the sequence, unique ignoring case in this run. Used for the temp thumbnail folder name.
        """

        def thumbnail_res():

            thumbnail_size = self.thumbnail_menu.text

            seq_height = sequence.height
            seq_width = sequence.width
            seq_ratio = float(seq_width) / float(seq_height)

            if thumbnail_size == 'Small':
                self.thumb_nail_height = 50
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 20

            elif thumbnail_size == 'Medium':
                self.thumb_nail_height = 100
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 30

            elif thumbnail_size == 'Large':
                self.thumb_nail_height = 150
                self.thumb_nail_width = int(self.thumb_nail_height * seq_ratio)
                self.x_offset = 31

            self.row_height = self.thumb_nail_height + (self.thumb_nail_height * .2)
            self.column_width = (self.thumb_nail_width + (self.x_offset * 2)) / 7.83
            self.y_offset = ((self.row_height * 1.333) - self.thumb_nail_height) / 2

        def export_thumbnail(self, sequence, segment, image_name):

            # Create list of existing exported thumbnails to check for extra frames
            temp_image_path_files = os.listdir(self.temp_image_path)

            # Modify export preset with selected resolution
            edit_preset = open(self.temp_export_preset, 'r')
            contents = edit_preset.readlines()
            edit_preset.close()

            # Use the safe temp image name, not the shot name, so shot names with & or < can't break the preset XML
            contents[8] = f'  <namePattern>{image_name}</namePattern>\n'
            contents[15] = f'   <width>{self.thumb_nail_width}</width>\n'
            contents[16] = f'   <height>{self.thumb_nail_height}</height>\n'
            contents[26] = '  <framePadding>0</framePadding>\n'

            edit_preset = open(self.temp_export_preset, 'w')
            contents = ''.join(contents)
            edit_preset.write(contents)
            edit_preset.close()

            # Mark in and out in sequence for segment frame to export
            sequence.in_mark = segment.record_in
            sequence.out_mark = segment.record_in + 1

            # Export thumbnail
            self.exporter.export(sequence, self.temp_export_preset, self.temp_image_path)

            # Clear sequence in and out marks
            sequence.in_mark = None
            sequence.out_mark = None

            # Fix for extra frames being exported when Inclusive Out Marks is selected in Flame Timeline Prefs.
            # Check if more than one thumbnail was exported. If so, delete the second frame and rename the first frame to remove the frame number.
            updated_temp_image_path_files = os.listdir(self.temp_image_path)

            if len(updated_temp_image_path_files) - len(temp_image_path_files) == 2:
                new_images = [image for image in updated_temp_image_path_files if image not in temp_image_path_files]

                # Delete first image in new_images list
                os.remove(os.path.join(self.temp_image_path, new_images[0]))

                # Rename second image in new_images list to remove frame number and add to temp_image_path_files list.
                new_image = new_images[1]

                if new_image.count('.') > 1:
                    os.rename(os.path.join(self.temp_image_path, new_image), os.path.join(self.temp_image_path, new_image.split('.')[0] + '.jpg'))
                temp_image_path_files.append(new_image)

        # Create temp directory to store thumbnails
        # Name the folder from the safe, unique file name so it is always a direct child of temp and never shared
        self.temp_image_path = os.path.join(self.temp_path, f'{file_name}_thumbnails')
        if os.path.exists(self.temp_image_path):
            shutil.rmtree(self.temp_image_path)
        os.makedirs(self.temp_image_path)

        # Set thumbnail size
        thumbnail_res()

        # One entry per video segment, in timeline order: shot name, temp image name and clip info
        self.shot_list = []

        # Save the sequence's in and out marks so they can be restored after the thumbnails are exported
        saved_in_mark = get_mark(sequence.in_mark)
        saved_out_mark = get_mark(sequence.out_mark)

        try:
            for segment in sequence.versions[0].tracks[0].segments:
                if segment.type == 'Video Segment':
                    shot_name = str(segment.shot_name)[1:-1]
                    if not shot_name:
                        shot_name = str(segment.name)[1:-1]

                    # Export thumbnail for segment with a temp name based on its row number
                    image_name = f'shot_{len(self.shot_list) + 1:04d}'
                    export_thumbnail(self, sequence, segment, image_name)

                    self.clip_info_list = []

                    self.clip_info_list.append(f'Shot Name: {shot_name}')
                    self.clip_info_list.append(f'Source Name: {str(segment.source_name)}')
                    self.clip_info_list.append(f'Source Path: {segment.file_path}')
                    self.clip_info_list.append(f'Source TC: {str(segment.source_in)[1:-1]} - {str(segment.source_out)[1:-1]}')
                    self.clip_info_list.append(f'Source TC In: {str(segment.source_in)[1:-1]}')
                    self.clip_info_list.append(f'Source TC Out: {str(segment.source_out)[1:-1]}')
                    self.clip_info_list.append(f'Record TC: {str(segment.record_in)[1:-1]} - {str(segment.record_out)[1:-1]}')
                    self.clip_info_list.append(f'Record TC In: {str(segment.record_in)[1:-1]}')
                    self.clip_info_list.append(f'Record TC Out: {str(segment.record_out)[1:-1]}')
                    self.clip_info_list.append(f'Shot Frame In: {str(flame.PyTime(segment.record_in.relative_frame))}')
                    self.clip_info_list.append(f'Shot Frame Out: {str(flame.PyTime(segment.record_out.relative_frame))}')
                    self.clip_info_list.append(f'Shot Length: {str(segment.record_duration)[1:-1]} - {str(flame.PyTime(segment.record_duration.frame))} Frames')

                    # Source length can be inifinite for things like solid colors, check for this.
                    if segment.source_duration != 'infinite':
                        self.clip_info_list.append(f'Source Length: {str(segment.source_duration)[1:-1]} - {str(flame.PyTime(segment.source_duration.frame))} Frames')
                    else:
                        self.clip_info_list.append('Source Length: Infinite')

                    self.clip_info_list.append(f'Comment: {str(segment.comment)[1:-1]}')

                    print(f'{shot_name} Clip Info:\n')
                    for info in self.clip_info_list:
                        print(f'    {info}')
                    print('\n')

                    self.shot_list.append({
                        'shot_name': shot_name,
                        'image_name': image_name,
                        'clip_info': self.clip_info_list,
                        })
        finally:
            # Restore the saved marks, even if an export failed
            sequence.in_mark = None
            sequence.out_mark = None
            if saved_in_mark is not None:
                sequence.in_mark = saved_in_mark
            if saved_out_mark is not None:
                sequence.out_mark = saved_out_mark

        # Sort By Shot Name: natural order ignoring case. The sort is stable, so shots with the same name keep their timeline order.
        if self.settings.sort_by == 'Shot Name':
            self.shot_list.sort(key=lambda shot: natural_sort_key(shot['shot_name']))

        if not self.shot_list:
            pyflame.print(f'No video segments in sequence: {str(sequence.name)[1:-1]}', print_type=PrintType.WARNING)

    def create_sequence_worksheet(self, workbook, seq_name, sheet_name):

        def create_column_names_list() -> list:
            """
            Create list of column names with no empty entries at end of list
            """

            column_names = [
                self.settings.column_01_name,
                self.settings.column_02_name,
                self.settings.column_03_name,
                self.settings.column_04_name,
                self.settings.column_05_name,
                self.settings.column_06_name,
                self.settings.column_07_name,
                self.settings.column_08_name,
                self.settings.column_09_name,
                self.settings.column_10_name,
                self.settings.column_11_name,
                self.settings.column_12_name,
                self.settings.column_13_name,
                self.settings.column_14_name,
                self.settings.column_15_name,
                self.settings.column_16_name,
                self.settings.column_17_name,
                self.settings.column_18_name,
                self.settings.column_19_name,
                self.settings.column_20_name,
                ]

            # Create list of column names with no empty entries at end of list
            i = len(column_names) - 1
            while i >= 0:
                # If the current element is empty, remove it from the list
                if not column_names[i]:
                    column_names.pop(i)
                # If the current element is not empty, stop the loop
                else:
                    break
                # Move to the next element
                i -= 1

            #print('column_names:', column_names)

            return column_names

        def add_clip_info_column(clip_info) -> None:
            """
            This will add a column for clip info and populate it with the selected options.
            """

            # If clip info True fill in clip info
            if clip_info:
                worksheet.set_column('B:B', 50)

                clip_info_row = 3

                for shot in self.shot_list:

                    # Add shot name to clip info - This is always added
                    clip_info = str(shot['clip_info'][0])

                    # Add source name to clip info
                    if self.settings.add_source_name:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][1])

                    # Add source path to clip info
                    if self.settings.add_source_path:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][2])

                    # Add source tc to clip info
                    if self.settings.add_source_tc:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][3])

                    # Add record tc to clip info
                    if self.settings.add_record_tc:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][6])

                    # Add shot frame in to clip info
                    if self.settings.add_shot_frame_in:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][9])

                    # Add shot frame out to clip info
                    if self.settings.add_shot_frame_out:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][10])

                    # Add shot length to clip info
                    if self.settings.add_shot_length:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][11])

                    # Add source length to clip info
                    if self.settings.add_source_length:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][12])

                    # Add comment to clip info
                    if self.settings.add_comment:
                        clip_info = clip_info + '\n' + str(shot['clip_info'][13])

                    worksheet.write(clip_info_row, 1, clip_info)
                    clip_info_row += 2

        def add_token_clip_info() -> None:
            """
            Add the clip info to the cell in the column of each row of the same name. To add clip info
            to a cell in the column of each row of the same name, the column name must be one of the info_tokens.
            """

            # List of clip info tokens to check against column names
            info_tokens = [
                'Shot Name',
                'Source Name',
                'Source Path',
                'Source TC',
                'Source TC In',
                'Source TC Out',
                'Record TC',
                'Record TC In',
                'Record TC Out',
                'Shot Frame In',
                'Shot Frame Out',
                'Shot Length',
                'Source Length',
                'Comment',
                ]

            # Add clip info to the cell in the column of each row of the same name
            start_column = 1
            info_row = 3

            for shot in self.shot_list:
                for column_index, name in enumerate(column_names):
                    if name in info_tokens:
                        column_number = column_index + start_column
                        info = shot['clip_info'][info_tokens.index(name)].split(': ', 1)[1]
                        worksheet.write(info_row, column_number, info)
                info_row += 2

        # Are any clip info buttons selected
        if self.source_name_push_button.checked:
            clip_info = True
        elif self.source_path_push_button.checked:
            clip_info = True
        elif self.source_tc_push_button.checked:
            clip_info = True
        elif self.record_tc_push_button.checked:
            clip_info = True
        elif self.shot_length_push_button.checked:
            clip_info = True
        elif self.source_length_push_button.checked:
            clip_info = True
        elif self.shot_frame_in_push_button.checked:
            clip_info = True
        elif self.shot_frame_out_push_button.checked:
            clip_info = True
        elif self.comment_push_button.checked:
            clip_info = True
        else:
            clip_info = False

        # Create worksheet with a safe sheet name. The real sequence name is written in the sheet below.
        worksheet = workbook.add_worksheet(sheet_name)
        worksheet.set_column('A:A', self.column_width)
        worksheet.set_column('B:B', 25)
        worksheet.set_column('C:C', 25)
        cell_format = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'bg_color': '#d6d6d6',
                'bold': True,
                'font_color': 'black'
                }
            )
        cell_format02 = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'bg_color': '#adadad',
                'align': 'top',
                'text_wrap': True
                }
            )
        cell_format03 = workbook.add_format(
                {
                'font_name': 'Helvetica',
                'align': 'top',
                'text_wrap': True
                }
            )

        worksheet.set_row(0, cell_format=cell_format02)
        worksheet.set_row(1, cell_format=cell_format02)

        shot_name_insert_row = 3
        image_insert_row = 4

        # Use this sequence's own clip info. A sequence with no shots has no shot rows to size.
        if clip_info and self.shot_list:
            line_height = (len(self.shot_list[0]['clip_info']) * 13) + 26
            if line_height > self.row_height:
                self.row_height = line_height
                self.y_offset = ((line_height * 1.333) - self.thumb_nail_height) / 2

        shot_name_row_list = []

        for shot in self.shot_list:
            image_path = os.path.join(self.temp_image_path, shot['image_name'] + '.jpg')
            worksheet.set_row(shot_name_insert_row, self.row_height, cell_format=cell_format03)
            shot_name_row = 'A' + str(shot_name_insert_row)
            image_row = 'A' + str(image_insert_row)
            shot_name_row_list.append(shot_name_row)
            worksheet.write(shot_name_row, shot['shot_name'], cell_format)

            # Place thumbnail inside its cell, or float it over the cell and move and size it with the cell
            if self.settings.images_in_cells:
                worksheet.embed_image(image_row, image_path)
            else:
                worksheet.insert_image(image_row, image_path, {'x_offset': self.x_offset, 'y_offset': self.y_offset, 'object_position': 1})

            shot_name_insert_row = shot_name_insert_row + 2
            image_insert_row = image_insert_row + 2

        # Create list of column names
        column_names = create_column_names_list()

        # If clip info True add clip info column
        if clip_info:
            column_names.insert(0, 'Clip Info')

        # Add sequence name to cell above first shot
        worksheet.write(1, 0, seq_name)

        # List to hold column codes
        column_code_list = []

        # Set column letter iteration
        column_letter = 'A'

        # Iterate through alphabet to create column codes
        for _ in column_names:
            column_letter = chr(ord(column_letter) + 1)
            column_code = column_letter + '2'
            column_code_list.append(column_code)

        # Add column names and set column width
        for (code, val) in zip(column_code_list, column_names):
            column_letter = re.split(r'(\d+)', code)[0]
            column_width_code = column_letter + ':' + column_letter
            worksheet.write(code, val, cell_format02)
            worksheet.set_column(column_width_code, 25)

        # If any clip info button is checked add clip info column
        add_clip_info_column(clip_info)

        # Check column names for info tokens and add clip info to those cells
        add_token_clip_info()

#-------------------------------------
# [Scopes]
#-------------------------------------

def scope_sequence(selection):

    for item in selection:
        if isinstance(item, (flame.PySequence, flame.PyClip)):
            return True
    return False

#-------------------------------------
# [Flame Menus]
#-------------------------------------

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'Shot Sheet Maker',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_sequence,
                    'execute': ShotSheetMaker,
                    'minimumVersion': '2025.2'
               }
           ]
        }
    ]
