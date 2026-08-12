# Tag Tools
# Copyright (c) 2026 Kyle Obley
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
Script Name:    Tag Tools
Script Version: 1.5.1
Flame Version:  2025.1
Written by:     Kyle Obley
Creation Date:  03.12.26
Update Date:    09.12.26

License:        GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type:    Media Panel, Media Hub

Description:

    Manages tags on sequences to be used later in QTs with the objective
    of being able to track original sequence name from Flame vs client name
    as well as audio.

    See:
    https://forum.logik.tv/t/python-tag-tools-internal-name-client-name-management/
    https://github.com/kmatchbox/PythonHooks/tree/main/tag_tools

    Very much a work in progress.

Menus:

    Flame Media Panel -> Right-click -> Tag Tools
    Flame Media Hub -> Right-click -> Tag Tools

To install:

    Copy script into /opt/Autodesk/shared/python/tag_tools

Updates:

    v1.5.1 09.12.26
        - Adjusted formating to adhear to Logik-Portal requirements.

    v1.5 07.01.26
        - Added ability to use the selected sequences and try to match those to QTs at a choosen location.
          If a match is found, the tags are copied from the sequence to the QT. This allows you to bypass
          the exporter all together so long as the sequence name matches the file name exactly.

    v1.4.2 07.01.26
        - Added export between marks option.

    v1.4.1 03.20.26
        - Fixed object has no attribute 'set_focus' error.

    v1.4 03.19.26
        - Updated qt_metadata library to be more strict. Files were failing to open on MacOS 26
          within QuickTime player & Preview.

    v1.3 03.16.26
        - CSV import/export support.
        - PyFlame config now working.

    v1.2 03.14.26
        - Added ability to rename files on the filesystem to internal/external name.

    v1.1 03.13.26
        - Added ability to read/set tags from imported QT.
        - Added ability to dump the contents of selected QT fiels within the media panel
          to the terminal.
        - Added UI via PyFlameUI Builder
        - Added ability to export from Flame and set the metadata afterwards. Current
          this is only working in the foreground. Need to figure out Backburner.

    v1.0 03.12.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import sys
import flame
import shutil
import csv
import time
from lib.qt_metadata import QuickTimeFile
from lib.pyflame_lib_tag_tools import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME    = 'Tag Tools'
SCRIPT_VERSION = 'v1.5.1'
SCRIPT_PATH    = os.path.abspath(os.path.dirname(__file__))


# ==============================================================================
# [Helper Functions]
# ==============================================================================

# List / String helper functions. Using + as the separator as it feels the best choice at the moment.
def list_to_string(meta_list):
    meta_string = "+".join(meta_list)
    return meta_string

def string_to_list(meta_string):
    meta_list = meta_string.split("+")
    return meta_list

def load_config():
    """
    Load Config
    ===========

    Loads configuration values from the config file and applies them to `self.settings`.

    If the config file does not exist, it creates the file using the default values
    from the `config_values` dictionary. Otherwise, it loads the existing config values
    and applies them to `self.settings`.
    """

    settings = PyFlameConfig(
        config_values={
            'export_path': '/',
            'csv_path': '/',
            },
        )
    return settings

# ==============================================================================
# [Flame Functions]
# ==============================================================================

# Primary function to set tag names. This is versitale and can be used for anything.
# This will also check if the tag already exists and update it accordingly.
def set_tag(sequence, tag_name, value):
    
    # Create an empty tags
    tags = []

    # Get existing tags
    tags = sequence.tags.get_value()

    print(f"[ Tag Tools ] Sequence:      {sequence.name.get_value()}")
    print(f"[ Tag Tools ] Current tags:  {tags}")

    # Look for existing tags that match our tag name.
    # Remove it if found.
    for item in tags[:]: 
        if item.startswith(f"{tag_name}:"):
            print(f"[ Tag Tools ] Existing tag:  {item}")
            tags.remove(item)

    # Set name tag. The name type and name are seperated
    # by : so we can treat it like a key pair.
    new_tag = ":".join([tag_name, value])

    # Add the new tag
    tags.append(new_tag)

    # Set tag
    sequence.tags = tags
    print(f"[ Tag Tools ] Updated tags:  {sequence.tags}")


# Set sequence name tags for both internal & client
def set_name_tag_to_current(sequence, tag_name):
    # Get sequence name
    name = sequence.name.get_value()
    set_tag(sequence, tag_name, name)

# Rename sequence based on tag for both internal & client
def rename_sequence(sequence, tag_name):
    
    # Create an empty tags
    tags = []

    # Get tags
    tags = sequence.tags.get_value()

    found_tag = False

    # Look for existing tags that match our tag name.
    for item in tags[:]: 
        if item.startswith(f"{tag_name}:"):
            found_tag = True
            new_name = item.split(":", 1)[1]

    # Foudn the tag, rename sequence.
    if found_tag:
        print(f"Current name:  {sequence.name.get_value()}")
        print(f"New name:      {new_name}")

        # Change the actual name
        sequence.name.set_value(new_name)
    else:
        print(f"Error: The tag {tag_name} doesn't exist in this sequence: {sequence.name.get_value()}")


# ==============================================================================
# [Functions Called Via UI Actions]
# ==============================================================================
def set_internal_name(selection):
    for item in selection:
        set_name_tag_to_current(item, "internal_name")

def set_client_name(selection):
    for item in selection:
        set_name_tag_to_current(item, "client_name")

def rename_to_internal_name(selection):
    for item in selection:
        rename_sequence(item, "internal_name")

def rename_to_client_name(selection):
    for item in selection:
        rename_sequence(item, "client_name")

def sync_tags_to_qt(selection):

    # Explain what we're looking for
    message = "The MediaHub already needs to be at our search folder. This will attempt to match the name of the selected sequence \
against the name of a .mov or .mp4.\n\nIf a match is found, then it will copy the tags from the sequence into the matching quicktime."   
    dialog = flame.messages.show_in_dialog(
        title ="Important - MediaHub Search Location",
        message = message,
        type = "info",
        buttons = ["Continue"],
        cancel_button = "Cancel")

    if dialog == "Cancel":
        print ("Cancel")

    # Use the current mediahub file location and the directory source.
    # Keeping the QT dialog just in case 
    else:

        flame.go_to('MediaHub')
        source_dir = flame.mediahub.files.get_path()
        print(f"[ Tag Tools ] Searching for matches in {source_dir}")
        '''
        dlg = QtWidgets.QFileDialog()
        dlg.setWindowTitle("Choose Directory")
        dlg.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        dlg.setFileMode(QtWidgets.QFileDialog.Directory)
        selected_dirs = []
        if dlg.exec():
            selected_dirs = dlg.selectedFiles()
        for selected_dir in selected_dirs:
            source_dir = selected_dir
        '''
        # Get directory listing & match only .mov & .mp4
        extensions = ('.mov', '.mp4')
        files = [f for f in os.listdir(source_dir) if f.lower().endswith(extensions)]

        # Use a directory lookup to find a match
        selection_map = {item.name.get_value(): item for item in selection}

        for f in files:
            base_name = os.path.splitext(f)[0]
            match = selection_map.get(base_name)

            # Found a match. Extract the tags and send to post export function.
            if match:
                print(f"[ Tag Tools ] Match found: {match.name.get_value()} -> {f}")
                matched_file = os.path.join(source_dir, f)

                # Create an empty tags & Get existing tags
                tags = []
                tags = list_to_string(match.tags.get_value())

                # Send to our post export function
                set_tags_post_export(matched_file, tags)

                print(f"[ Tag Tools ] Updated {f} with the following tags: {tags}\n")


def set_internal_and_client_name(selection):
    for item in selection:
        name = item.name.get_value()

        # Check that we have our seperator
        if "__" in name:

            # Get internal and client names
            internal = name.split("__")[0]
            client = name.split("__")[1]

            # Set internal
            set_tag(item, "internal_name", internal)

            # Set client
            set_tag(item, "client_name", client)
        else:
            print(f"[ Tag Tools ] Error: The seuqnece {name} is missing __ seperating the internal and client names.")

def set_audio(selection):
    for item in selection:

        audio_list = []

        if item.audio_tracks:
            for track in item.audio_tracks:
                if track:
                    for channel in track.channels:
                        for audio in channel.segments:
                            if audio:
                                if audio.file_path and audio.file_path != '':

                                    # Get the basename, the whole path would be too long
                                    audio_file = os.path.basename(audio.file_path)
                                    audio_list.append(audio_file)
                                    print(f"[ Tag Tools ] Found audio file:  {audio_file}")


            # Sort the list to remove duplicates
            audio_list = sorted(set(audio_list))

            # Convert the list to a string
            audio_files = ",".join(audio_list)

            # Set tag
            set_tag(item, "audio_files", audio_files)

        else:
            print(f"[ Tag Tools ] The seuqnece {item.name.get_value()} has no audio files.")

def get_tags_from_qt(selection):
    for clip in selection:
        path = clip.versions[0].tracks[0].segments[0].file_path

        # Get the existing metadata
        qt = QuickTimeFile(path)
        metadata = qt.get_metadata("com.apple.quicktime.comment")

        if metadata == '':
            print(f"[ Tag Tools ] Error: The file {path} has no metadata.")
        else:

            # Convert the string to a list and set as the tag
            meta_list = string_to_list(metadata)

            # We could just dump this right into the tags as-is, but
            # let's be good and run it through our set_tag function so
            # everything is the same.
            for item in meta_list:
                tag_name = item.split(":")[0]
                value = item.split(":")[1]

                set_tag(clip, tag_name, value)

def set_tags_post_export(full_path, tags):
    #print(f"Set Tags Post : Full path: {full_path}")
    #print(f"Set Tags Post :Tags: {tags}")

    qt = QuickTimeFile(full_path)
    qt.set_metadata("com.apple.quicktime.comment", tags)
    qt.save(full_path)


# ==============================================================================
# [Hook Overwrite & Backburner Stuff]
# ==============================================================================


class HooksOverride(object):
        def __init__(self, foreground):
            self._foreground = foreground

        def postExportAsset(self, info, userData, *args, **kwargs):
            del args, kwargs  # Unused necessary parameters
            full_path = os.path.join(info["destinationPath"], info["resolvedPath"])

            if self._foreground:
                set_tags_post_export(full_path, userData)
            else:
                create_python_backburner_job(
                    job_name="Updating tags %s" % info["assetName"],
                    description="Updating tags %s" % info["assetName"],
                    dependencies=info["backgroundJobId"],
                    function="set_tags_post_export",
                    args=[full_path, userData],
                )

def create_backburner_job(job_name, description, dependencies, cmd):
    """
    Send a command line job to Backburner.

    :param job_name: Name of the Backburner job
    :param description: Description of the Backburner job
    :param dependencies: None if the Backburner job should execute arbitrarily.
                         If you want to set up the job to executes after another
                         known task, pass the Backburner id or a list of ids
                          here. This is typically used in conjunction with a
                         postExportAsset hook where the export task runs on
                         Backburner. In this case, the hook will return the
                         Backburner id. By passing that id to this method,
                         you create a job which only executes after the main
                         export task has completed.
    :param cmd: Command line to execute
    :return backburner_job_id: Id of the Backburner job created
    """

    # The Backburner command job executable
    backburner_job_cmd = os.path.join("/opt", "Autodesk", "backburner", "cmdjob")

    backburner_args = []
    backburner_args.append("-userRights")  # Honor application user (not root)
    backburner_args.append("-timeout:600")
    backburner_args.append('-jobName:"%s"' % job_name)
    backburner_args.append('-description:"%s"' % description)

    # Set the Backburner job dependencies
    if dependencies:
        if isinstance(dependencies, list):
            backburner_args.append("-dependencies:%s" % ",".join(dependencies))
        else:
            backburner_args.append("-dependencies:%s" % dependencies)

    full_cmd = "%s %s %s" % (backburner_job_cmd, " ".join(backburner_args), cmd)

    stdout, stderr = execute_command(full_cmd)
    print(stdout)

    job_id_regex = re.compile(r"(?<=Successfully submitted job )(\d+)")
    match = job_id_regex.search(stdout)

    if match:
        backburner_job_id = match.group(0)
        print("Backburner job created (%s)" % backburner_job_id)
        return backburner_job_id

    else:
        print("Backburner job not created\n%s" % stderr)

    return None

def create_python_backburner_job(job_name, description, dependencies, function, args=None):
    """
    Send a callback to this Python file using command line job to backburner.

    :note: Beware. The file must be executable and will use the Python
           interpreter bundled with Flame. Change the header for a different
           Python intepreter.

    :param job_name: Name of the backburner job
    :param description: Description of the backburner job
    :param dependencies: None if the backburner job should execute arbitrarily.
                         If you want to set up the job to executes after another
                         known task, pass the backburner id or a list of ids
                         here. This is typically used in conjunction with a
                         postExportAsset hook where the export task runs on
                         backburner. In this case, the hook will return the
                         backburner id. By passing that id to this method,
                         you create a job which only executes after the main
                         export task has completed.
    :param function: Function name to call
    :param args: Function arguments
    :return backburner_job_id: Id of the backburner job created
    """
    return create_backburner_job(
        job_name=job_name,
        description=description,
        dependencies=dependencies,
        cmd=" ".join([os.path.abspath(__file__), function, " ".join(args)]),
    )

def execute_command(command):


    # Flame 2022.2+ provides a way to run a command line through the
    # Autodesk Flame Multi-Purpose Daemon. This way of starting new processes
    # is better since any native python subprocess command (os.system,
    # subprocess, Popen, etc) will call fork() which will duplicate the process
    # memory before calling exec(). This can be costly especially for a process
    # like Flame.
    #
    # Note: Environment variables will not be forwarded to the executed command.
    #
    if "execute_command" in dir(flame):
        _, stdout, stderr = flame.execute_command(
            command=command,
            blocking=True,
            shell=True,
            capture_stdout=True,
            capture_stderr=True,
        )
    else:
        import subprocess

        process = subprocess.Popen([command], stdout=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8") if stdout else None
        stderr = stderr.decode("utf-8") if stderr else None
    return stdout, stderr

# ==============================================================================
# [UI & Exporting Functions]
# ==============================================================================

class tag_tools_export:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Make selection available to the other functions
        self.selection = selection

        # Create/Load config file settings.
        self.load_config()
        self.previous_path = self.settings.export_path

        # Open main window
        self.main_window()

    def load_config(self) -> None:
        """
        Load Config
        ===========

        Loads configuration values from the config file and applies them to `self.settings`.

        If the config file does not exist, it creates the file using the default values
        from the `config_values` dictionary. Otherwise, it loads the existing config values
        and applies them to `self.settings`.
        """

        self.settings = PyFlameConfig(
            config_values={
                'export_path': '/',
                'csv_path': '/',
                },
            )


    def main_window(self) -> None:
        """
        Main Window
        ===========

        Main window for script.
        """

        # Buuild list of export presets for menu
        self.export_presets = pyflame.get_export_preset_names()


        def export_sequences() -> None:
            """
            Pulls together the destination path, export preset and builds the export call.
            """

            self.window.close()

            # Get path and preset path from preset name
            destination_path = self.destination_browser.path
            preset_path = pyflame.convert_export_preset_name_to_path(self.preset_menu.text)

            # Get foreground option
            #foreground = self.foreground_button.checked
            foreground = True

            # Between marks option
            between_marks = self.between_marks_button.checked

            # Save destination path to config
            self.settings.save_config(
                config_values={
                    'export_path': destination_path,
                    }
                )

            print(f"Destination: {destination_path}")
            print(f"Preset path: {preset_path}")



            # Define exporter
            exporter = flame.PyExporter()
            exporter.foreground = foreground
            exporter.export_between_marks = between_marks
            #exporter.include_subtitles = True
            #exporter.export_subtitles_as_files = True
            
            for item in self.selection:
                print(f"[ Tag Tools ] Exporting: {item.name.get_value()}")

                # Create an empty tags
                tags = []

                # Get existing tags
                tags = list_to_string(item.tags.get_value())

                # Export sequence
                exporter.export(item, preset_path, destination_path, hooks=HooksOverride(foreground), hooks_user_data=tags)

        def close_window() -> None:
            """
            Close window when escape is pressed.
            """

            self.window.close()

        # ------------------------------------------------------------------------------
        # [Start Window Build]
        # ------------------------------------------------------------------------------

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} Exporter <small>{SCRIPT_VERSION}',
            parent=None,
            return_pressed=export_sequences,
            escape_pressed=close_window,
            grid_layout_columns=3,
            grid_layout_rows=5,
            )

        # Labels
        self.destination_label = PyFlameLabel(
            text='Destination Folder',
            style=Style.NORMAL,
            align=Align.LEFT,
            )
        self.preset_label = PyFlameLabel(
            text='Preset',
            style=Style.NORMAL,
            align=Align.LEFT,
            )

        # Entries
        self.destination_browser = PyFlameEntryBrowser(
            path=self.previous_path,
            placeholder_text='/location/to/export',
            browser_type=BrowserType.DIRECTORY,
            browser_title='Select File',
            )

        # Buttons
        self.cancel_button = PyFlameButton(
            text='Cancel',
            color=Color.GRAY,
            tooltip='',
            connect=close_window,
            )
        self.export_button = PyFlameButton(
            text='Export',
            color=Color.BLUE,
            tooltip='',
            connect=export_sequences,
            )

        self.foreground_button = PyFlamePushButton(
            text='Foreground',
            checked=True,
            tooltip='',
            )

        self.between_marks_button = PyFlamePushButton(
            text='Between Marks',
            checked=False,
            tooltip='',
            )

        # Menus
        self.preset_menu = PyFlameMenu(
            text='Select preset',
            menu_options=self.export_presets,
            align=Align.LEFT,
            menu_indicator=False,
            tooltip='',
            )
        

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.window.grid_layout.addWidget(self.preset_label, 0, 0)
        self.window.grid_layout.addWidget(self.preset_menu, 0, 1, 1, 2)
        self.window.grid_layout.addWidget(self.destination_label, 1, 0)
        self.window.grid_layout.addWidget(self.destination_browser, 1, 1, 1, 2)
        self.window.grid_layout.addWidget(self.foreground_button, 2, 1)
        self.window.grid_layout.addWidget(self.between_marks_button, 2, 2)
        self.window.grid_layout.addWidget(self.cancel_button, 4, 1)
        self.window.grid_layout.addWidget(self.export_button, 4, 2)


        #self.destination_browser.set_focus()
        # ------------------------------------------------------------------------------
        # [End Window Build]
        # ------------------------------------------------------------------------------


# ==============================================================================
# [Filesystem Funections]
# ==============================================================================
def fs_dump_metadata_to_terminal(selection):
    for item in selection:
        path = item.path
        basename = os.path.basename(path)

        qt = QuickTimeFile(path)
        metadata = qt.get_metadata("com.apple.quicktime.comment")

        if metadata:
            # Convert the string to a list and set as the tag
            meta_list = string_to_list(metadata)
            print(f"[ Tag Tools ] Metadata dump for {basename} -> {meta_list}")
        else:
            print(f"[ Tag Tools ] Metadata dump for {basename} -> None")


def fs_rename_qt(file, tag_name):
    path = os.path.dirname(file)
    basename = os.path.basename(file)
    ext = os.path.splitext(file)[1]

    qt = QuickTimeFile(file)
    metadata = qt.get_metadata("com.apple.quicktime.comment")

    if metadata:
        meta_list = string_to_list(metadata)
        found_tag = False

        for item in meta_list:
            if item.startswith(tag_name):
                
                # Get the new tag and add the extension.
                new_name = item.split(tag_name+":")[1] + ext
                new_name_path = os.path.join(path, new_name)
                found_tag = True

                try:
                    shutil.move(file, new_name_path)
                    print (f"[ Tag Tools ] Renamed {basename} to {new_name}")

                except Exception as e:
                    print (f"Error renaming file: {e}")
        # Didn't fine the tag, say it doesn't exist.
        if not found_tag:
            print (f"[ Tag Tools ] Error {basename} doesn't have {tag_name} tag set")
    
    else:
        print (f"[ Tag Tools ] Error {basename} doesn't have any metadata")

    # Refresh the media panel at the end of everything
    flame.execute_shortcut('Refresh the MediaHub\'s Folders and Files')


def fs_rename_to_client(selection):
    for item in selection:
        fs_rename_qt(item.path, "client_name")

def fs_rename_to_internal(selection):
    for item in selection:
        fs_rename_qt(item.path, "internal_name")

# ==============================================================================
# [CSV Funections]
# ==============================================================================
def export_csv(selection):

    settings = load_config()
    previous_csv_path = settings.csv_path

    # Get export location
    dlg = QtWidgets.QFileDialog()
    
    # This should be the taken from the config file once that is working.
    #init_dir = base_path
    dlg.setDirectory(previous_csv_path)
    dlg.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
    dlg.setFileMode(QtWidgets.QFileDialog.Directory)
    selected_dirs = []
    if dlg.exec():
        selected_dirs = dlg.selectedFiles()

    for selected_dir in selected_dirs:
        csv_dir = selected_dir

    # Get timestamp & set name/path of csv file
    t = time.time()
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(t))
    file_name = "tag_tools_" + timestamp + ".csv"
    csv_path = os.path.join(csv_dir, file_name)

    # Dump the current name of the selected sequences into the CSV file
    # Pretty simple approach. Might be worth making it more complicated
    # and checking against set tags, etc.
    with open(csv_path, 'w', newline='') as csvfile:
        fieldnames = ['internal_name', 'client_name']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        # Iterate over our sequences
        for item in selection:
            writer.writerow({'internal_name': item.name.get_value(), 'client_name': ''})

    print(f"[ Tag Tools ] CSV exported to: {csv_path}")

    # Let's give the user a pretty info message
    dialog = flame.messages.show_in_dialog(
        title ="CSV Exported",
        message = f"CSV exported to {csv_path}.",
        type = "info",
        buttons = ["Close"])

    settings.save_config(
        config_values={
            'csv_path': csv_dir,
            }
        )

def import_csv(selection):

    settings = load_config()
    previous_csv_path = settings.csv_path

    # Get export location
    dlg = QtWidgets.QFileDialog()
    
    # This should be the taken from the config file once that is working.
    #init_dir = base_path
    dlg.setDirectory(previous_csv_path)
    dlg.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
    dlg.setOption(QtWidgets.QFileDialog.ShowDirsOnly, False)
    dlg.setNameFilter("CSV (*.csv)");
    dlg.setDefaultSuffix("csv");
    selected_files = []
    if dlg.exec():
        selected_files = dlg.selectedFiles()

    for selected_file in selected_files:
        csv_file = selected_file

    if csv_file:

        failed = []

        # Load the CSV file and map it to a dict.
        csv_mapping = load_csv(csv_file)

        # Try to match the current name to internal_name & set client name
        for item in selection:
            key = item.name.get_value()
            client_name = csv_mapping.get(key)

            if client_name is None:
                failed.append(key)
            else:
                set_tag(item, "client_name", client_name)

        if failed:
            print("[ Tag Tools ] The following sequnces couldn't be matched to a client name:")
            for item in failed:
                print(f"              - {item}")

        # Let's give the user a pretty info message
        dialog = flame.messages.show_in_dialog(
            title ="CSV Import Fail",
            message = f"Some sequences couldn't be matched to a client name. See the terminal for more details.",
            type = "info",
            buttons = ["Close"])


    else:
        print(f"[ Tag Tools ] Error: No CSV file selected")

def load_csv(file_path: str) -> dict[str, str]:
    """Load CSV into memory as a dict mapping internatl_name -> client_name."""
    mapping = {}
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["internatl_name"]] = row["client_name"]
    return mapping



# ==============================================================================
# [Scoping]
# ==============================================================================
def sequence_selected(selection):
    for item in selection:
        if isinstance(item, (flame.PySequence)):
            return True
    return False

def qt_selected_flame(selection):
    for item in selection:
        if isinstance(item, (flame.PyClip)):
            path = item.versions[0].tracks[0].segments[0].file_path
            if path.endswith(".mov") or path.endswith(".mp4"):
                return True
    return False

def is_mov(selection):
    import os
    for item in selection:
        if os.path.splitext(item.path)[1] == '.mov' or os.path.splitext(item.path)[1] == '.mp4':
            return True
    return False

# ==============================================================================
# [Flame Menus - Media Panel]
# ==============================================================================

def get_media_panel_custom_ui_actions():
    return [

        {
            "name": "Set/Get Tag",
            "hierarchy": ["Tagging Tools"],
            "order": 1,
            "actions": [
                {
                    "name": "Current Name → Internal Name",
                    "order": 1,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": set_internal_name,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Current Name → Client Name",
                    "order": 2,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": set_client_name,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Current Name → Both (Split internal__client)",
                    "order": 2,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": set_internal_and_client_name,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Current Audio → Audio",
                    "order": 3,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": set_audio,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Sequences → MediaHub Files",
                    "order": 4,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": sync_tags_to_qt,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Get tags from imported QuickTime(s)",
                    "order": 5,
                    "isVisable": qt_selected_flame,
                    "isEnabled": qt_selected_flame,
                    "execute": get_tags_from_qt,
                    "minimumVersion": "2025.1"
                }
           ]
        },
        {
            "name": "Rename Clip From Tag",
            "hierarchy": ["Tagging Tools"],
            "order": 2,
            "actions": [
                {
                    "name": "Internal Name",
                    "order": 1,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": rename_to_internal_name,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Client Name",
                    "order": 2,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": rename_to_client_name,
                    "minimumVersion": "2025.1"
                }
           ]
        },
        {
            "name": "CSV Import/Export",
            "hierarchy": ["Tagging Tools"],
            "order": 2,
            "actions": [
                {
                    "name": "Import",
                    "order": 1,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": import_csv,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Export",
                    "order": 2,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": export_csv,
                    "minimumVersion": "2025.1"
                }
           ]
        },
        {
            "name": "Export Sequences With Tags",
            "hierarchy": ["Tagging Tools"],
            "order": 4,
            "actions": [
                {
                    "name": "Open Export Window",
                    "order": 1,
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": tag_tools_export,
                    "minimumVersion": "2025.1"
                }
           ]
        }
    ]

# ==============================================================================
# [Flame Menus - Media Hub]
# ==============================================================================
def get_mediahub_files_custom_ui_actions():
    return [
        {
            "name": "Tagging Tools",
            "actions": [
                {
                    "name": "Dump metadata to terminal",
                    "order": 1,
                    "isVisable": is_mov,
                    "isEnabled": is_mov,
                    "execute": fs_dump_metadata_to_terminal,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Rename → Internal Name",
                    "order": 2,
                    "isVisable": is_mov,
                    "isEnabled": is_mov,
                    "execute": fs_rename_to_internal,
                    "minimumVersion": "2025.1"
                },
                {
                    "name": "Rename → Client Name",
                    "order": 3,
                    "isVisable": is_mov,
                    "isEnabled": is_mov,
                    "execute": fs_rename_to_client,
                    "minimumVersion": "2025.1"
                }
            ]
        }
    ]
