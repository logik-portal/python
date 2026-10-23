# Create Export Menus - Export Menu: Work - ProRes 4444 XQ - PreRender
# Copyright (c) 2026 Michael Vaglienty
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
Script Name: Create Export Menus - Export Menu: Work - ProRes 4444 XQ - PreRender
Script Version: 5.5.0
Flame Version: 2027
Written by: Michael Vaglienty
Creation Date: 04.27.20
Update Date: 05.25.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Media Panel

Description:

    Export menu for Work - ProRes 4444 XQ - PreRender export preset. Created with Create Export Menus script.

Menu:

    Right-click on clip to export -> Shared Export Presets... -> Work - ProRes 4444 XQ - PreRender
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import flame

import os
import re
import tempfile
import datetime
from pyflame_lib_create_export_menus import *

FLAME_PROJECT = 'None'

# ==============================================================================
# [Export Function]
# ==============================================================================

def export_clips(selection):

    def translate_tokenized_path(clip, export_path):

        def get_shot_name(name):

            shot_name_split = re.split(r'(\d+)', name)

            if len(shot_name_split) > 1:
                if shot_name_split[1].isalnum():
                    shot_name = shot_name_split[0] + shot_name_split[1]
                else:
                    shot_name = shot_name_split[0] + shot_name_split[1] + shot_name_split[2]
            else:
                shot_name = name

            return shot_name

        def get_seq_name(name):

            # Return sequence name abreviation from shot name
            return re.split('[^a-zA-Z]', name)[0]

        print('Tokenized Export Path:', export_path)

        date = datetime.datetime.now()

        clip_name = str(clip.name)[1:-1]

        # Get shot name
        try:
            if clip.versions[0].tracks[0].segments[0].shot_name != '':
                shot_name = str(clip.versions[0].tracks[0].segments[0].shot_name)[1:-1]
            else:
                shot_name = get_shot_name(clip_name)
        except:
            shot_name = ''

        # Get tape name
        try:
            tape_name = str(clip.versions[0].tracks[0].segments[0].tape_name)
        except:
            tape_name = ''

        # Get Seq Name
        seq_name = get_seq_name(shot_name)

        # Replace tokens in path
        translated_export_path = re.sub('<ProjectName>', flame.project.current_project.name, export_path)
        translated_export_path = re.sub('<ProjectNickName>', flame.project.current_project.nickname, translated_export_path)
        translated_export_path = re.sub('<ShotName>',shot_name, translated_export_path)
        translated_export_path = re.sub('<SeqName>', seq_name, translated_export_path)
        translated_export_path = re.sub('<SEQNAME>', seq_name.upper(), translated_export_path)
        translated_export_path = re.sub('<UserName>', flame.users.current_user.name, translated_export_path)
        translated_export_path = re.sub('<UserNickName>', flame.users.current_user.nickname, translated_export_path)
        translated_export_path = re.sub('<ClipName>', str(clip.name)[1:-1], translated_export_path)
        translated_export_path = re.sub('<Resolution>', str(clip.width) + 'x' + str(clip.height), translated_export_path)
        translated_export_path = re.sub('<ClipHeight>', str(clip.height), translated_export_path)
        translated_export_path = re.sub('<ClipWidth>', str(clip.width), translated_export_path)
        translated_export_path = re.sub('<YYYY>', yyyy, translated_export_path)
        translated_export_path = re.sub('<YY>', yy, translated_export_path)
        translated_export_path = re.sub('<MM>', mm, translated_export_path)
        translated_export_path = re.sub('<DD>', dd, translated_export_path)
        translated_export_path = re.sub('<Hour>', hour, translated_export_path)
        translated_export_path = re.sub('<hour>', hour_12, translated_export_path)
        translated_export_path = re.sub('<Minute>', minute, translated_export_path)
        translated_export_path = re.sub('<AMPM>', ampm_caps, translated_export_path)
        translated_export_path = re.sub('<ampm>', ampm, translated_export_path)
        translated_export_path = re.sub('<TapeName>', tape_name, translated_export_path)

        print ('Translated Export Path:', translated_export_path, '\n')

        return translated_export_path

    pyflame.print_title('Create Export Menu - Clip Export v5.3.0')

    pyflame.print(f'Exporting: Work - ProRes 4444 XQ - PreRender')

    # Get time values for token conversion
    date = datetime.datetime.now()
    yyyy = date.strftime('%Y')
    yy = date.strftime('%y')
    mm = date.strftime('%m')
    dd = date.strftime('%d')
    hour = date.strftime('%H')
    hour_12 = date.strftime('%I')
    if hour_12.startswith('0'):
        hour_12 = hour_12[1:]
    minute = date.strftime('%M')
    ampm_caps = date.strftime('%p')
    ampm = str(date.strftime('%p')).lower()

    # Initialize Exporter
    clip_output = flame.PyExporter()

    # Export selected clips
    for clip in selection:

        # Export preset One

        # Export using top video track
        clip_output.use_top_video_track = False
        print('\n--> Export using top layer: False')

        # Set export to foreground
        clip_output.foreground = True
        print('--> Export in foreground: True')

        # Export between markers
        clip_output.export_between_marks = False
        print('--> Export between marks: False\n')

        # Include subtitles
        clip_output.include_subtitles = False
        print('--> Include subtitles: False\n')

        # Subtitles export mode
        clip_output.export_subtitles_as_files = False
        print('--> Subtitles export mode: False\n')

        # Subtitles tracks
        clip_output.export_all_subtitles = False
        print('--> Subtitles tracks: False\n')

        # Translate tokens in path

        new_export_path = translate_tokenized_path(clip, '/Volumes/lax-cloud-1/welax-work post/Projects/<ProjectName>/shot/<SEQNAME>/<ShotName>/prerenders')

        if not new_export_path:
            return

        if not os.path.isdir(new_export_path):
            try:
                os.makedirs(new_export_path)
            except:
                PyFlameMessageWindow(
                    message=f'Could not create export path.\n\nPlease check the export path and try again.\n\n{new_export_path}',
                    message_type=MessageType.ERROR,
                    title='Export Path Error',
                    parent=None,
                )
                return

        import_export = True

        if import_export:
            # Drop a marker file in the export directory to capture the server's clock
            marker_fd, marker_path = tempfile.mkstemp(prefix='.flame_export_marker_', dir=new_export_path)
            os.close(marker_fd)
            export_start_time = os.path.getmtime(marker_path)
            os.remove(marker_path)

        clip_output.export(clip, '/opt/Autodesk/shared/export/presets/movie_file/Final Cut Pro (Apple ProRes 4444 XQ)_2027.xml', new_export_path)

        if import_export:
            # Walk the entire tree to find .mov files modified at or after the marker's timestamp
            exported_files = []
            for dirpath, dirnames, filenames in os.walk(new_export_path):
                for f in filenames:
                    if f.lower().endswith('.mov'):
                        full_path = os.path.join(dirpath, f)
                        if os.path.getmtime(full_path) >= export_start_time:
                            exported_files.append(full_path)
            for path in sorted(exported_files):
                flame.import_clips(path, clip.parent)
                pyflame.print('Imported clip back into Flame.')

        # Export preset One END

        pyflame.print (f'Exported: {str(clip.name)[1:-1]}\n', text_color=TextColor.GREEN)

    # Open export path in MediaHub after export
    reveal_in_mediahub = False

    if reveal_in_mediahub:
        flame.go_to('MediaHub')
        flame.mediahub.files.set_path(new_export_path)
        pyflame.print('MediaHub opened to export path.')

    # Open export path in finder after export
    reveal_in_finder = True

    if reveal_in_finder:
        pyflame.open_in_finder(
            path=new_export_path,
            )
        pyflame.print('Finder opened to export path.')

    pyflame.print('Export complete.', text_color=TextColor.GREEN)

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_clip(selection):


    if FLAME_PROJECT == flame.project.current_project.name:
        for item in selection:
            if isinstance(item, flame.PyClip):
                return True
    if FLAME_PROJECT == 'None':
        for item in selection:
            if isinstance(item, flame.PyClip):
                return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():


    return [
        {
            'name': 'Shared Export Presets...',
            'actions': [
                {
                    'name': 'Work - ProRes 4444 XQ - PreRender',
                    'isVisible': scope_clip,
                    'execute': export_clips,
                    'minimumVersion': '2027',
                }
            ]
        }
    ]
