# Collect Media
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
Script Name:    Collect Media
Script Version: 1.0.2
Flame Version:  2023
Written by:     Kyle Obley
Creation Date:  08.10.21
Update Date:    12.08.26

License:        GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type:    Media Panel, Media Hub

Description:

    Dump a list of every non-cached clip and segment in every sequence and batch in every folder
    out to a known location for archiving.

    Important / Cavets:
    - We can not see into BFX so anything in there will not be caught.
    - This will only grab the used version of a versioned clip, not every version.
    - This will only grab the latest batch iteration, not previous versions.
    - Within batch, only import nodes are seen, not read file nodes.
    - Only works on the current workspace.
    - Flame returns the path of an image sequence as the first frame in the sequence, not the first frame being
      used within said image sequence. For now the safest route is to find the last frame in the sequence on disk
      and use that to populate the list.

Menus:

    Flame Main Menu -> Collect Media

To install:

    Copy script into /opt/Autodesk/shared/python/collect_media

Updates:

    v1.0.2 08.12.21
        - Adjusted formating to adhear to Logik-Portal requirements.

    v1.0.1 08.11.21
        - Adjusted the custom_location logic and re-arranged the code so directory existance check works for both cases.

    v1.0
        - Merged Chris' 0.9.2 but changed the logic to not include a dated sub-folder for easier backups.

        - Re-incorperated the ability for a custom save location.

    v0.9.2
        - Changed output location to ~/collect_media/{project_name}/{YYYYMMDD}/ for easier access
          and to avoid permission issues. Organized by project and date for better management.

        - Fixes FileNotFoundError by automatically creating directory structure.

    v0.9
        - Added a timestamped backup of a previoous list if found if, for whatever reason, you need to roll-back.

    v0.8
        -Stopped using a UniqueList for all the lists and instead us set() at the end to remove duplicates due to a
         the previous method taking significantly longer. Resulted in a 1000x speed increase. Bonkers.

    v0.7
        - Attempting to speed up the write process for large projects.

    v0.6
        - Fixed the handling of Red files to go up on directory to ensure we grab all the sub-files.

        - Added ability to specify a custom dump file location (custom_dump_location).

    v0.5
        - Added the option to scrape cached media as well.

        - Added more checks during scraping to avoid NoneTypes. Not sure if it's bulletproof though.

    v0.4
        - PySegment.source_cached added to API allowing us the ability to now get the cached
          status of clips in segments including audio.

        - Set the minimum version to 2023.1

        - Removed Python 2.7 support as we now require 2023

        - Added a warning and completion dialog using the built-in message display

    v0.3
        - Current desktop is now scrapped as well.

        - Adjusted the logic to how to account for the totals to reflect de-deplication
          and give a better impression of total number of file sequences.

    v0.2
        - Added compatability for Python 2.7

        - Implemented a class to create a unique list as opposed to dumping everything
          to a list and then using sort to de-dup. Written by Clauss.

        - Re-worked logic of how we manage an existing list.

        - Added audio support. Cached status within a sequence is still an issue.

    v0.1
        - Initial Release
"""

import flame

clips = []
sequences = []
uncached_only = True

#
# Scaning/Builing Functions
#

def build_list_folder(selection):
    global clips
    global sequences

    for folder in selection:
        if folder:
            if has_subfolder(folder):
                build_list_folder(folder.folders)

            for clip in folder.clips:
                if clip:
                    clips.append(clip)

            for sequence in folder.sequences:
                if sequence:
                    sequences.append(sequence)
                
            if folder.reels:
                build_list_reels(folder.reels)

            if folder.reel_groups:
                build_list_reel_group(folder.reel_groups)

            if folder.batch_groups:
                build_list_batchgroups(folder.batch_groups)

            if folder.desktops:
                build_list_desktop(folder.desktops)
        
def build_list_desktop(selection):
    global clips
    global sequences

    for desktop in selection:
        if desktop:
            if desktop.reels:
                build_list_reels(desktop.reels)

            if desktop.reel_groups:
                build_list_reel_group(desktop.reel_groups)

            if desktop.batch_groups:
                build_list_batchgroups(desktop.batch_groups)

def build_list_reels(selection):
    global clips
    global sequences

    for reel in selection:
        if reel:
            for clip in reel.clips:
                if clip:
                    clips.append(clip)
            for sequence in reel.sequences:
                if sequence:
                    sequences.append(sequence)

def build_list_reel_group(selection):
    global clips
    global sequences

    for reel_group in selection:
        if reel_group:
            for reel in reel_group.reels:
                if reel:
                    for clip in reel.clips:
                        if clip:
                            clips.append(clip)
                    for sequence in reel.sequences:
                        if sequence:
                            sequences.append(sequence)

def build_list_batchgroups(selection):
    global clips
    global sequences

    for batchgroup in selection:
        if batchgroup:
            for reel in batchgroup.reels:
                if reel:
                    for clip in reel.clips:
                        if clip:
                            clips.append(clip)
                    for sequence in reel.sequences:
                        if sequence:
                            sequences.append(sequence)

def build_list_lose_clips(selection):
    global clips

    for clip in selection:
        if clip:
            clips.append(clip)

def build_list_lose_sequence(selection):
    global sequences

    for sequence in selection:
        if sequence:
            sequences.append(sequence)



#
# Helper Functions
#

def has_subfolder(folder):
    if len(folder.folders) == 0:
        return False
    else:
        return True

def segments_in_sequence(sequence):
    segs_in_seq = []
    versions = sequence.versions[0:]
    for v in versions:
        if v:
            tracks = v.tracks[0:]
            for t in tracks:
                if t:
                    segments = t.segments[0:]
                    for s in segments:
                        if s is not None:
                            segs_in_seq.append(s)
    if segs_in_seq:
        return segs_in_seq

#
# Extration Fuctions
#

def extract_clip_info(clip):
    global uncached_only

    name = clip.name
    cached = clip.cached

    # Some ditry hack to get around audio for the moment for the path and duration
    try:
        path = clip.versions[0].tracks[0].segments[0].file_path
    except:
        path = ''

    try:
        duration = clip.versions[0].tracks[0].segments[0].source_duration.frame
    except:
        duration = 1

    # If duration is 1073741823, then it's a still for some reason so let's correct that
    if duration == 1073741823:
        duration = 1

    # Uncahced only
    if uncached_only:
        if cached == "Uncached" and path != '':
            if path:
                return path

    # Grab everything
    else:
        if path and path != '':
            return path

def extract_segment_info(segment):
    global uncached_only

    if segment.name != '' and segment is not None:
            name = segment.name
            path = segment.file_path
            cached = segment.source_cached

            try:
                duration = segment.source_duration.frame
            except:
                duration = 1

            # Uncached Only
            if uncached_only:
                if cached == "Uncached" and path != '':                
                    if path:
                        return path

            # Grab everything
            else:
                if path and path != '':
                    return path

def get_file_sequence(filepath):
    import os
    import re
    import glob

    exlude_list = ["mp4", "mov", "mxf", "braw", "r3d"]
    sequence = []
    ext = filepath.split(".")[-1].lower()
    if ext in exlude_list:
        if os.path.isfile(filepath):

            # Make an exception for Red. Send path instead with trailing slash
            if ext == "r3d":
                filepath = os.path.dirname(filepath) + "/"

            sequence.append(filepath)
    else:
        try:
            first_frame_number = re.findall(r'\d+', filepath)[-1]
            padding = len(first_frame_number)
            question_marks = ''.join([char*padding for char in "?"])
            # sanitises filepath incase someone put brackets in the name
            sanatised_filepath = glob.escape(filepath)
            glob_to_search = sanatised_filepath.replace(str(first_frame_number) + "." + ext, question_marks + "." + ext)
            if os.path.isfile(filepath):
                sequence = glob.glob(glob_to_search)
        except:
            if os.path.isfile(filepath):
                sequence.append(filepath)

    if sequence:
        return sorted(sequence)

#
# Scrape Workspace
#

def scrape_workspace():

    global clips
    global sequences

    workspace = flame.project.current_project.current_workspace
    desktop = workspace.desktop

    print ("[ Collect Media ] + Scraping Workspace:", workspace.name.get_value())

    # Go through every library in the current workspace
    for library in workspace.libraries:
        lib_name = library.name.get_value()

        # Skip these two libraries
        if lib_name == "Timeline FX" or lib_name == "Grabbed References":
            pass
        else:
            print ("[ Collect Media ] +-> Scraping Library:", lib_name)

            build_list_folder(library.folders)
            build_list_reels(library.reels)
            build_list_reel_group(library.reel_groups)
            build_list_batchgroups(library.batch_groups)
            build_list_desktop(library.desktops)
            build_list_lose_clips(library.clips)
            build_list_lose_sequence(library.sequences)

    print ("[ Collect Media ] +-> Scraping Desktop:", desktop.name.get_value())
    
    # Unable to just send the current desktop to build_list_desktop so we have to
    # break it down beforehand to reel groups and batch groups
    
    if (desktop.reel_groups):
        build_list_reel_group(desktop.reel_groups)

    if (desktop.batch_groups):
        build_list_batchgroups(desktop.batch_groups)

    return clips, sequences


#
# Main Function to pull everything together
#

# def collect_media(selection):
def collect_media():
    import os
    import time
    import shutil

    debug = False

    global uncached_only

    current_project = flame.project.current_project.name
    file_list = []

    # Custom dumpfile location in case you want a shared location.
    # This will still create a sub-folder for the current_project.
    # Leave empty to use the user's home folder
    #custom_dump_location = ""
    custom_dump_location = os.path.join("/PROJEKTS", current_project, "assets", "technical", "collect_media")


    # Use custom location if set. If not, use the default, userhome location
    # Build path: ~/collect_media/{project_name}/
    if custom_dump_location:
        dump_dir = custom_dump_location
    else:
        home_dir = os.path.expanduser('~')
        dump_dir = os.path.join(home_dir, "collect_media", current_project)

    # Ensure the directory structure exists
    if not os.path.exists(dump_dir):
        try:
            os.makedirs(dump_dir)
            print ("[ Collect Media ] Created directory: %s" % dump_dir)
        except OSError as e:
            print ("\n\n[ Collect Media ] ERROR: Could not create directory %s: %s\n\n" % (dump_dir, str(e)))
            return

    # Name & location of the dump file
    dump_file = "collected_media.txt"
    dump_file_location = os.path.join(dump_dir, dump_file)

    # Make sure someone else isn't writting to the file. If they aren't, then do our thing.
    locked_dump_file_location = dump_file_location + ".lock"
    if os.path.isfile(locked_dump_file_location):
        print ("\n\n[ Collect Media ] ERROR: Someone else is writing to the list. Exiting.\n\n")
    else:

        print ("\n\n[ Collect Media ] Starting ...")
        print ("[ Collect Media ] IMPORTANT: Only works on the current workspace")

        if uncached_only:
            print ("[ Collect Media ] IMPORTANT: Searching for uncached media only")
        else:
            print ("[ Collect Media ] IMPORTANT: Searching for all media regardless of cache status")

        # See if an existing dump file is there, if it is then load those contents into our file list
        # and make a backup of the previous list.
        if os.path.isfile(dump_file_location):

            # Get timestamp
            t = time.time()
            timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime(t))

            # Append . so we can just use replace to create the full path easily.
            timestamp = ".bu_" + timestamp
            dump_file_backup = dump_file_location.replace(".txt", timestamp)

            # Make a backup of the list
            shutil.copyfile(dump_file_location, dump_file_backup)

            # Rename to lock file
            os.rename(dump_file_location, locked_dump_file_location)
            
            with open(locked_dump_file_location) as f:
                for line in f:
                    file_list.append(line.rstrip())
        
        # Scrape workspace
        scraped = scrape_workspace()
        collected_clips = set(scraped[0])
        collected_sequences = set(scraped[1])

        # Clips
        num_clips = 0
        num_audio = 0

        print ("[ Collect Media ] Extracting clips and paths, this may take a while...")

        start = time.time()
        for clips in collected_clips:
            if clips:
                extracted = extract_clip_info(clips)
                if extracted:
                    num_clips += 1
                    frames = get_file_sequence(extracted)
                    if frames:
                        for frame in frames:
                            file_list.append(frame)
                
                # Lose Audio clips
                if clips.audio_tracks:

                    # Only find uncached clips
                    if uncached_only:
                        if clips.cached == "Uncached":
                            for track in clips.audio_tracks:
                                for channel in track.channels:
                                    for audio in channel.segments:
                                        num_audio += 1
                                        file_list.append(audio.file_path)
                    # Grab everything
                    else:
                        for track in clips.audio_tracks:
                            for channel in track.channels:
                                for audio in channel.segments:
                                    num_audio += 1
                                    file_list.append(audio.file_path)

        print("[ Collect Media ] Took %.2f seconds" % (time.time() - start))

        if uncached_only:
            print ("[ Collect Media ] Found %i uncached, lose video clips" % num_clips)
            print ("[ Collect Media ] Found %i uncached, lose audio tracks" % num_audio)
        else:
            print ("[ Collect Media ] Found %i lose video clips" % num_clips)
            print ("[ Collect Media ] Found %i lose audio tracks" % num_audio)

        print ("[ Collect Media ] Extracting segments and paths, this may take a while...")

        # Sequences
        uniq_segments = []

        start = time.time()
        for sequence in collected_sequences:
            if sequence:
                if debug:
                    print ("Sequence Pointer: " ,sequence)
                    print ("Sequence Type:", sequence.type)
                    print ("Sequence: ", sequence.name)
                    print ("    <-- ", sequence.parent.name)
                    print ("        <-- ", sequence.parent.parent.name)
                    print ("           <-- ", sequence.parent.parent.parent.name)
                    print ("              <-- ", sequence.parent.parent.parent.parent.name)
                
                segments_list = segments_in_sequence(sequence)
               
                if debug:
                    print ("Segment list: ", segments_list)

                if segments_list:
                    for segment in segments_list:
                        if debug:
                            print ("        Segment: ", segment.name)
                            print ("        Segment Parent:", segment.parent.parent.name)
                        if segment:
                            extracted = extract_segment_info(segment)
                            if extracted:
                                uniq_segments.append(extracted)
                                frames = get_file_sequence(extracted)
                                if frames:
                                    for frame in frames:
                                        file_list.append(frame)
                
                # Audio in sequences
                if sequence.audio_tracks:
                    for track in sequence.audio_tracks:
                        if track:
                            for channel in track.channels:
                                for audio in channel.segments:
                                    if audio:

                                        # Only find uncached clips
                                        if uncached_only:
                                            if audio.source_cached == "Uncached" and audio.file_path != '':
                                                file_list.append(audio.file_path)

                                        # Grab everything
                                        else:
                                            if audio.file_path and audio.file_path != '':
                                                file_list.append(audio.file_path)

        # Remove duplicates and sort list
        file_list_cleaned = sorted(set(file_list))

        print("[ Collect Media ] Took %.2f seconds" % (time.time() - start))

        if uncached_only:
            print ("[ Collect Media ] Found %i total sequences with %i unique, uncached video clips" % (len(collected_sequences), len(set(uniq_segments))))
        else:
            print ("[ Collect Media ] Found %i total sequences with %i unique video clips" % (len(collected_sequences), len(set(uniq_segments))))

        print ("[ Collect Media ] Writing list of files")


        # Write contents of file_list to locked dump file, overwritting existing data since we already have that
        f = open(locked_dump_file_location, "w")

        # Create a long string to allow us to just write to the file in one go.
        file_list_string = '\n'.join(file_list_cleaned)
        f.write(file_list_string)
        f.close()

        # Rename to the non-locked file
        os.rename(locked_dump_file_location, dump_file_location)

        print ("[ Collect Media ] Created list for archive: ", dump_file_location)
        print ("[ Collect Media ] Rsync Command: rsync -avh --progress --files-from=%s / /path/to/backup/" % (dump_file_location))
        print ("[ Collect Media ] Finished\n\n")

        flame.messages.show_in_console(
            "[ Collect Media ] Rsync Command: rsync -avh --progress --files-from=%s / /path/to/backup/" % (dump_file_location), "info", 10
        )

        # Let's give the user a pretty info message
        dialog = flame.messages.show_in_dialog(
            title ="Collect Media (v1.0)",
            message = "Scraping complete.\n\nProgress and final archive command are in the console.",
            type = "info",
            buttons = ["Close"])

        if dialog == "Close":
            pass


def show_message(selection):
    dialog = flame.messages.show_in_dialog(
        title ="Collect Media (v1.0)",
        message = "IMPORT: Only works on the current workspace. Please select if you want to only search for uncached media or everything.\n\nProgress and final archive command are in the console.",
        type = "warning",
        buttons = ["Everything", "Uncached Only"],
        cancel_button = "Cancel")

    if dialog == "Uncached Only":
        collect_media()

    if dialog == "Everything":
        global uncached_only
        uncached_only = False

        collect_media()

    elif dialog == "Cancel":
        pass

# Put in Main Menu
def get_main_menu_custom_ui_actions():
    return [
        {
            "name": "Collect Media",
            "actions": [
                {
                    "name": "Collect Media",
                    "execute": show_message
                }
            ]
        }
    ]

get_main_menu_custom_ui_actions.minimum_version = "2023.1"
