"""
Script Name: fix premiere xmls
Script Version: 3.5.7
Flame Version: 2025.1
Written by: Ted Stanley, John Geehreng, and Michael Vaglienty
Creation Date: 03.03.21
Update Date: 09.13.26

Custom Action Type: MediaHub, MediaPanel, Timeline

Description:

    Fix and/or Resize Adobe Premiere XML's. Stamps each clip's media
    resolution (WIDTHxHEIGHT) into clip comments. After conform and link,
    Auto Scale reads that comment, compares it to the linked clip
    resolution, strips XML Action junk, and scales the Action when they differ
    (Fit or Scale to Frame Size). Auto Scale Undo restores the previous Action.
    Prep fills FCP start/end -1 from neighboring transition items so dissolves
    keep the right overlap and later clips do not slide. Speed-changed clips
    get their source in-point from Premiere's pproTicksIn so Flame's Timewarp
    does not start late.

Menus:

    MediaHub -> XML Prep -> Fix Premiere XML's
    Media Panel / Timeline -> XML Prep -> Auto Scale
    Media Panel / Timeline -> XML Prep -> Auto Scale Undo

To install:

    Copy script into /opt/Autodesk/shared/python/fix_premiere_xmls or put it wherever you keep your scripts

Updates:
    09.13.26 - v3.5.7 - Speed-changed in-points from pproTicksIn during prep. Removed Apply Premiere Motion as a separate step.
    09.13.26 - v3.5.6 - Apply Premiere Motion / Timewarp (XML2Action 1.23) after import. Does not replace 3.5.4 duration math.
    09.13.26 - v3.5.5 - Retag still clipitem + file + samplecharacteristics to the sequence rate. Leave real off-rate video out points alone.
    09.12.26 - v3.5.4 - Hold a last fade-to-black still through the last sequence frame (88 rounded frames vs 89 to duration).
    09.12.26 - v3.5.3 - Flame uses in/out as still length; match that to timeline frames and set clip rate to the sequence.
    09.12.26 - v3.5.2 - Convert still/fade in/out length from clip fps to sequence fps (30fps graphic on a 24fps timeline).
    09.12.26 - v3.5.1 - Fade to/from black keeps in/out length so stills are not stretched to a distant fade.
    09.12.26 - v3.5.0 - Resolve dissolve/fade start/end -1 from transition items so later clips do not slide.
    09.11.26 - v3.4.1 - Auto Scale saves originals to undo first so a later Scale to Frame Size is not applied on leftover Fit data.
    09.11.26 - v3.4.0 - Renamed Apply Online Scale to Auto Scale. Added Auto Scale Undo.
    09.10.26 - v3.3.5 - Apply Online Scale: Scale to Frame Size (width-only) option.
    09.09.26 - v3.3.4 - Updated PyFlame lib to 5.5.1 (from silhouette_roundtrip).
    09.09.26 - v3.3.3 - Label stamped res as "Offline Resolution: WIDTHxHEIGHT".
    09.09.26 - v3.3.2 - Prepend offline res to lognote so Flame's segment comment actually carries it.
    09.09.26 - v3.3.1 - Stamp offline res only on clipitem <comment>; leave lognote and clip comments alone.
    09.09.26 - v3.3.0 - Apply Online Scale uses stamped clip comments; no XML file picker.
    09.09.26 - v3.2.1 - Renamed Apply Offline Scale to Apply Online Scale.
    09.09.26 - v3.2.0 - Apply Online Scale rewrites Motion (anchor, keys, bake) and Timewarp from the XML.
    09.09.26 - v3.1.0 - Stamp per-clip offline WIDTHxHEIGHT comments. Apply Online Scale after link.
    04.13.26 - v3.0.1 - Fixed the issue with the scale factor calculation.
    03.01.26 - v3.0.0 - Updated for pyflame lib v5.2.3
    02.13.25 - v2.1.2  Update to latest pyflame lib and SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
    05.06.24 - v2.1.1  Changed Scoping to show up only if xml's are selected
    04.03.24 - v2.1    Fixed renaming issue
    12.05.23 - v2.0.2  Fixed the missing fixduration() problem. Made _x_res names consistent.
    11.28.23 - v2.0.1  Updated for pyflame lib v2. Added ability to resize xmls. Changed the output names based on options
    11.12.23 - v1.94   Fixed the Scale Factor Calculator to use the correct width or height. Added try/except when using the "Clean Names" option.
    09.08.22 - v1.93   2023.2 Ordering and Scale Factor Calculator
    05.24.22 - v1.92   Update from Ted - This one fixes almost everything. Except dissolves, those still suck.
    04.19.22 - v1.91   2023 UI
    02.19.22 - v1.90   Created option for automatically using the xml's resolution
    12.27.21 - Turned off "v" to "V" when sanatizing names
    11.15.21 - Added the ability to scale values over 100
    09.03.21 - Made sanatizing the names optional
    08.27.21 - Turned off the "That Totally Worked" message as you can see the update in the MediaHub
    08.13.21 - Change XML Bit Depth to Project Settings
    06.04.21 - Change Default Scale Value to 100 for graphics. Renamed "Cancel" button to say "Close"
    05.17.21 - Added the ability to select multiple .xml's and added Ted's nested layer fix
    03.19.21 - Python3 Updates

"""

# ---------------------------------------- #
# Imports

import math
import os
import re
import sys
import flame

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_PATH not in sys.path:
    sys.path.insert(0, SCRIPT_PATH)

from lib.pyflame_lib_fix_premiere_xmls import *

#-------------------------------------#
# Main Script

SCRIPT_NAME = "Fix Premiere XMLs"
SCRIPT_VERSION = 'v3.5.7'

class fix_premiere_xmls():

    def __init__(self, selection):

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        # Create/Load config file settings.
        self.load_config()
        
        # Define self selection
        self.xml_selection = selection

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
                'proxy_x_res': 1920,
                'proxy_y_res': 1080,
                'full_x_res': 1920,
                'full_y_res': 1080,
                'online_x_res': 1920,
                'online_y_res': 1080,
                'scale_calc': False,
                'xml_res': True,
                'sanatize_names': True,
                'fix_durations': True,
                },
            )
        
    def fixrepo(self):
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        status = 1
        print("Fixing repos...")
        for clip in clips:
            name = clip.find('name').text
            # print("Clip " + str(status) + ": " + name)
            status += 1

            file = clip.find('file')
            if file is None:
                # print("ERROR: No file, maybe a nest?")
                continue
            search = ".//*[@id='{}']".format(list((file.attrib).items())[0][1])
            master = self.root.find(search)

            cliphoriz = master.find(".//media/video/samplecharacteristics/width").text
            cliphoriz = int(cliphoriz)
            clipvert = master.find(".//media/video/samplecharacteristics/height").text
            clipvert = int(clipvert)

            scaleparam = clip.find(".//filter/effect/[name='Basic Motion']/parameter/[name='Scale']")
            if scaleparam is not None and self.scalemult != 1:
                xmlscale = scaleparam.find("value")
                if xmlscale is None:continue
                newscale = self.scalemult * float(xmlscale.text)
                # print("New Scale = " + str(newscale))
                xmlscale.text = str(newscale)
                keyframes = scaleparam.findall('keyframe')
                if len(keyframes) != 0:
                    # print("New Scale Keyframes:")
                    for keyframe in keyframes:
                        keyframe[1].text = str(float(keyframe[1].text) * self.scalemult)
                        # print(keyframe[1].text)

            parameter = clip.find(".//filter/effect/[name='Basic Motion']/parameter/[name='Center']")
            if parameter is None:continue
            xmlhoriz = parameter[2][0].text
            xmlhoriz = float(xmlhoriz)
            xmlvert = parameter[2][1].text
            xmlvert = float(xmlvert)
            
            # COMPENSATE FOR RESIZING
            newxmlhoriz = ((xmlhoriz * cliphoriz) / self.input_sequence_width) * self.online_x_factor
            newxmlvert = ((xmlvert * clipvert) / self.input_sequence_height)

            if newxmlhoriz == 0: newxmlhoriz = int(newxmlhoriz)
            if newxmlvert == 0: newxmlvert = int(newxmlvert)

            # print("Old Repo --> New Repo")

            # print(parameter[2][0].text + " " + str(newxmlhoriz))
            # print(parameter[2][1].text + " " + str(newxmlvert))

            parameter[2][0].text = str(newxmlhoriz)
            parameter[2][1].text = str(newxmlvert)

            keyframes = parameter.findall('keyframe')
            if keyframes is not None:
                # print("Keyframes:")
                for keyframe in keyframes:
                    keyhoriz = float(keyframe[1][0].text)
                    keyvert = float(keyframe[1][1].text)

                    # COMPENSATE FOR RESIZING
                    newxmlhoriz = ((keyhoriz * cliphoriz) / self.input_sequence_width) * self.online_x_factor
                    newxmlvert = ((keyvert * clipvert) / self.input_sequence_height)

                    keyframe[1][0].text = str(newxmlhoriz)
                    keyframe[1][1].text = str(newxmlvert)

    def _direct_child(self, parent, tag):
        for child in list(parent):
            if child.tag == tag:
                return child
        return None

    def _clipitem_comment(self, clip):
        """Direct-child <comment> only. clip.find('comment') can hit logginginfo/comment."""
        comment = self._direct_child(clip, 'comment')
        if comment is None:
            comment = ET.SubElement(clip, 'comment')
        return comment

    def _prepend_res_to_lognote(self, clip, res):
        """Flame's segment comment is lognote + master comments + Comment A/B, not clipitem <comment>."""
        label = f"Offline Resolution: {res}"
        logginginfo = self._direct_child(clip, 'logginginfo')
        if logginginfo is None:
            logginginfo = ET.SubElement(clip, 'logginginfo')
        lognote = self._direct_child(logginginfo, 'lognote')
        if lognote is None:
            lognote = ET.SubElement(logginginfo, 'lognote')
        existing = (lognote.text or "").strip()
        if re.search(r'Offline Resolution:\s*\d+\s*x\s*\d+', existing, re.IGNORECASE):
            return
        if existing:
            lognote.text = f"{label} | {existing}"
        else:
            lognote.text = label

    def stamp_offline_comments(self):
        """Write each clipitem's media size as 'Offline Resolution: WIDTHxHEIGHT'.

        clipitem <comment> is set for the XML. The same label is prepended to
        logginginfo/lognote once, because that is what Flame puts on segment.comment.
        Camera metadata in master comments / Comment A/B is left alone.
        """
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        stamped = 0
        print("Stamping offline resolution comments...")
        for clip in clips:
            file = clip.find('file')
            if file is None:
                continue
            try:
                search = ".//*[@id='{}']".format(list((file.attrib).items())[0][1])
            except (IndexError, KeyError):
                continue
            master = self.root.find(search)
            if master is None:
                continue
            try:
                cliphoriz = master.find(".//media/video/samplecharacteristics/width").text
                clipvert = master.find(".//media/video/samplecharacteristics/height").text
                res = f"{int(cliphoriz)}x{int(clipvert)}"
            except (AttributeError, TypeError, ValueError):
                continue

            self._clipitem_comment(clip).text = f"Offline Resolution: {res}"
            self._prepend_res_to_lognote(clip, res)

            stamped += 1
            name = clip.find('name')
            clip_name = name.text if name is not None else "unnamed"
            print(f"  {clip_name}: {res}")

        print(f"Stamped offline res on {stamped} clip(s).")

    def _element_int(self, parent, tag):
        element = self._direct_child(parent, tag)
        if element is None or element.text is None:
            return None
        try:
            return int(element.text)
        except (TypeError, ValueError):
            try:
                return int(round(float(element.text)))
            except (TypeError, ValueError):
                return None

    def _element_number(self, parent, tag):
        element = self._direct_child(parent, tag)
        if element is None or element.text is None:
            return None
        try:
            return float(element.text)
        except (TypeError, ValueError):
            return None

    def _format_frame_number(self, value):
        if abs(value - round(value)) < 1e-6:
            return str(int(round(value)))
        return ("%.10f" % value).rstrip('0').rstrip('.')

    def _set_element_int(self, parent, tag, value):
        element = self._direct_child(parent, tag)
        if element is None:
            return False
        element.text = str(int(value))
        return True

    def _set_element_number(self, parent, tag, value):
        element = self._direct_child(parent, tag)
        if element is None:
            return False
        element.text = self._format_frame_number(value)
        return True

    def _sequence_element(self):
        if self.root.tag == 'sequence':
            return self.root
        return self.root.find('sequence')

    def _fps(self, node):
        if node is None:
            return None
        rate = self._direct_child(node, 'rate')
        if rate is None:
            return None
        timebase = self._element_int(rate, 'timebase')
        if not timebase:
            return None
        ntsc = self._direct_child(rate, 'ntsc')
        if ntsc is not None and (ntsc.text or '').strip().upper() == 'TRUE':
            return timebase * 1000.0 / 1001.0
        return float(timebase)

    def _sequence_duration(self):
        seq = self._sequence_element()
        return self._element_int(seq, 'duration') if seq is not None else None

    def _sequence_fps(self):
        return self._fps(self._sequence_element())

    def _clip_fps(self, clip):
        return self._fps(clip) or self._sequence_fps()

    def _rates_match(self, clip) -> bool:
        clip_fps = self._clip_fps(clip)
        seq_fps = self._sequence_fps()
        if clip_fps is None or seq_fps is None:
            return True
        return abs(clip_fps - seq_fps) < 0.05

    def _to_sequence_frames(self, frames, clip) -> int:
        clip_fps = self._clip_fps(clip)
        seq_fps = self._sequence_fps()
        if frames is None or clip_fps is None or seq_fps is None:
            return frames
        if abs(clip_fps - seq_fps) < 0.05:
            return frames
        return int(round(frames * seq_fps / clip_fps))

    def _hold_through_sequence_end(self, new_end):
        """FCP end is exclusive. 110×24/30 rounds to 88, one frame short of sequence duration."""
        seq_dur = self._sequence_duration()
        if seq_dur is None or new_end is None:
            return new_end
        if new_end == seq_dur - 1:
            return seq_dur
        return new_end

    def _copy_sequence_rate(self, node):
        seq = self._sequence_element()
        seq_rate = self._direct_child(seq, 'rate') if seq is not None else None
        if seq_rate is None or node is None:
            return
        node_rate = self._direct_child(node, 'rate')
        if node_rate is None:
            node_rate = ET.SubElement(node, 'rate')
        for tag in ('timebase', 'ntsc'):
            src = self._direct_child(seq_rate, tag)
            if src is None:
                continue
            dst = self._direct_child(node_rate, tag)
            if dst is None:
                dst = ET.SubElement(node_rate, tag)
            dst.text = src.text

    STILL_EXTS = (
        '.jpg', '.jpeg', '.png', '.tif', '.tiff', '.psd', '.tga',
        '.bmp', '.gif', '.exr', '.dpx', '.ai', '.eps', '.webp', '.heic',
    )
    PPRO_TICKS_PER_SECOND = 254016000000

    def _file_element(self, clip):
        file_el = self._direct_child(clip, 'file')
        if file_el is None:
            return None
        file_id = file_el.get('id')
        if file_id:
            found = self.root.find(".//*[@id='%s']" % file_id)
            if found is not None:
                return found
        return file_el

    def _is_still(self, file_el):
        if file_el is None:
            return False
        pathurl = self._direct_child(file_el, 'pathurl')
        url = (pathurl.text or '') if pathurl is not None else ''
        if not url:
            name = self._direct_child(file_el, 'name')
            url = (name.text or '') if name is not None else ''
        url = url.lower()
        if '?' in url:
            url = url.split('?', 1)[0]
        return url.endswith(self.STILL_EXTS)

    def _remap_still_keyframes(self, clip, src_fps, seq_fps):
        if not src_fps or not seq_fps or abs(src_fps - seq_fps) < 0.05:
            return 0
        clip_in = self._element_int(clip, 'in')
        if clip_in is None:
            return 0
        origin = clip_in
        ticks = self._direct_child(clip, 'pproTicksIn')
        if ticks is not None and ticks.text and ticks.text.lstrip('-').isdigit():
            tick_origin = math.floor(
                int(ticks.text) / float(self.PPRO_TICKS_PER_SECOND) * src_fps + 1e-9
            )
            if tick_origin in (clip_in - 1, clip_in):
                origin = tick_origin
        ratio = seq_fps / src_fps
        moved = 0
        for keyframe in clip.iter('keyframe'):
            when = self._direct_child(keyframe, 'when')
            if when is None or not when.text:
                continue
            try:
                old = float(when.text)
            except (TypeError, ValueError):
                continue
            new = clip_in + int(round((old - origin) * ratio))
            if new != int(round(old)):
                moved += 1
            when.text = str(new)
        return moved

    def retag_still_rates(self):
        """Pull still clipitem/file rates to the sequence. Do not retag real off-rate video."""
        retagged = 0
        keys_moved = 0
        print("Retagging still frame rates...")
        seq_fps = self._sequence_fps()
        for track in self._iter_media_tracks():
            for clip in list(track):
                if clip.tag != 'clipitem':
                    continue
                file_el = self._file_element(clip)
                if not self._is_still(file_el):
                    continue
                src_fps = self._fps(clip) or self._fps(file_el)
                keys_moved += self._remap_still_keyframes(clip, src_fps, seq_fps)
                self._copy_sequence_rate(clip)
                self._copy_sequence_rate(file_el)
                if file_el is not None:
                    sample = file_el.find('media/video/samplecharacteristics')
                    if sample is not None:
                        self._copy_sequence_rate(sample)
                    timecode = self._direct_child(file_el, 'timecode')
                    if timecode is not None:
                        self._copy_sequence_rate(timecode)
                start = self._element_int(clip, 'start')
                end = self._element_int(clip, 'end')
                clip_in = self._element_int(clip, 'in')
                if None not in (start, end, clip_in) and start >= 0 and end >= 0:
                    self._set_element_int(clip, 'out', clip_in + (end - start))
                retagged += 1
        print(f"Retagged {retagged} still(s); remapped {keys_moved} keyframe(s).")

    def _effect_id(self, effect):
        element = self._direct_child(effect, 'effectid')
        if element is None or element.text is None:
            return ''
        return element.text.strip().lower()

    def _param_value(self, effect, parameter_id):
        for parameter in effect.findall('parameter'):
            pid = self._direct_child(parameter, 'parameterid')
            if pid is None or (pid.text or '').strip().lower() != parameter_id:
                continue
            value = self._direct_child(parameter, 'value')
            if value is None or value.text is None:
                return None
            return value.text.strip()
        return None

    def _time_remap_info(self, clip):
        for filt in clip.findall('filter'):
            effect = self._direct_child(filt, 'effect')
            if effect is None or self._effect_id(effect) != 'timeremap':
                continue
            speed_text = self._param_value(effect, 'speed')
            if speed_text is None:
                return None
            try:
                speed = float(speed_text)
            except (TypeError, ValueError):
                return None
            variable = (self._param_value(effect, 'variablespeed') or '0').upper() in ('1', 'TRUE')
            reverse = (self._param_value(effect, 'reverse') or 'FALSE').upper() in ('1', 'TRUE')
            return speed, variable, reverse
        return None

    def fix_timewarp_inpoints(self):
        """Set speed-changed <in> from pproTicksIn so Flame's in * speed matches Premiere.

        Premiere stores the true source position in ticks and writes <in> rounded up.
        Flame uses in * (speed/100), so it starts late by up to speed/100 frames.
        Variable-speed and reverse Time Remap are left alone.
        """
        seq_fps = self._sequence_fps()
        if not seq_fps:
            print("Timewarp in-points: no sequence fps, skipped.")
            return
        rewritten = 0
        skipped = 0
        print("Fixing Timewarp in-points...")
        for track in self.root.findall('.//media/video/track'):
            for clip in list(track):
                if clip.tag != 'clipitem':
                    continue
                info = self._time_remap_info(clip)
                if info is None:
                    continue
                speed, variable, reverse = info
                if abs(speed) < 1e-9 or abs(speed - 100.0) < 1e-9:
                    continue
                name = self._direct_child(clip, 'name')
                clip_name = name.text if name is not None and name.text else 'unnamed'
                if variable or reverse:
                    skipped += 1
                    why = 'variable-speed' if variable else 'reverse'
                    print(f"  skip {clip_name}: {why} Time Remap")
                    continue
                ticks = self._element_int(clip, 'pproTicksIn')
                clip_in = self._element_number(clip, 'in')
                if ticks is None or clip_in is None:
                    skipped += 1
                    continue
                ratio = speed / 100.0
                truth = ticks / float(self.PPRO_TICKS_PER_SECOND) * seq_fps
                new_in = truth / ratio
                if abs(new_in - clip_in) < 1e-6:
                    continue
                if not self._set_element_number(clip, 'in', new_in):
                    continue
                rewritten += 1
                print(
                    f"  {clip_name}: in {self._format_frame_number(clip_in)} -> "
                    f"{self._format_frame_number(new_in)} ({speed:g}%, "
                    f"was {clip_in * ratio:.3f} source, Premiere {truth:.3f})"
                )
        print(f"Rewrote {rewritten} speed-changed in-point(s).")
        if skipped:
            print(f"Left {skipped} Time Remap clip(s) untouched.")

    def _iter_media_tracks(self):
        for path in ('.//media/video/track', './/media/audio/track'):
            yield from self.root.findall(path)

    def _track_edit_items(self, track):
        return [child for child in list(track) if child.tag in ('clipitem', 'transitionitem')]

    def _alignment(self, transition):
        element = self._direct_child(transition, 'alignment')
        if element is None or element.text is None:
            return ''
        return element.text.strip().lower()

    def _source_duration(self, clip):
        clip_in = self._element_int(clip, 'in')
        clip_out = self._element_int(clip, 'out')
        if clip_in is None or clip_out is None:
            return None
        return clip_out - clip_in

    def _snap_fade(self, transition, clip_edge, alignment, clip=None):
        fade_start = self._element_int(transition, 'start')
        fade_end = self._element_int(transition, 'end')
        if fade_start is None or fade_end is None:
            return
        fade = max(0, fade_end - fade_start)
        fade = self._to_sequence_frames(fade, transition if transition is not None else clip)
        if alignment == 'end-black':
            self._set_element_int(transition, 'end', clip_edge)
            self._set_element_int(transition, 'start', clip_edge - fade)
        elif alignment == 'start-black':
            self._set_element_int(transition, 'start', clip_edge)
            self._set_element_int(transition, 'end', clip_edge + fade)
        if not self._rates_match(transition):
            self._copy_sequence_rate(transition)

    def resolve_transition_times(self):
        """Replace FCP start/end -1 using neighboring transitionitem times.

        Clip-to-clip dissolves use the transition range so the shots overlap.
        Fade to/from black uses the clip's in/out length and parks the fade on
        the head or tail. Premiere stills often have a fade far from in/out;
        stretching the still to that fade is what made graphics run long.
        """
        filled_start = 0
        filled_end = 0
        skipped = 0
        print("Resolving transition start/end...")
        for track in self._iter_media_tracks():
            items = self._track_edit_items(track)
            for index, item in enumerate(items):
                if item.tag != 'clipitem':
                    continue
                start = self._element_int(item, 'start')
                end = self._element_int(item, 'end')
                source_duration = self._source_duration(item)
                if start is not None and start < 0:
                    previous_item = items[index - 1] if index > 0 else None
                    if previous_item is not None and previous_item.tag == 'transitionitem':
                        alignment = self._alignment(previous_item)
                        if alignment == 'start-black' and end is not None and source_duration is not None:
                            new_start = end - self._to_sequence_frames(source_duration, item)
                            if self._set_element_int(item, 'start', new_start):
                                filled_start += 1
                                self._snap_fade(previous_item, new_start, alignment, item)
                        else:
                            transition_start = self._element_int(previous_item, 'start')
                            if transition_start is not None and self._set_element_int(item, 'start', transition_start):
                                filled_start += 1
                    else:
                        skipped += 1
                if end is not None and end < 0:
                    next_item = items[index + 1] if index + 1 < len(items) else None
                    if next_item is not None and next_item.tag == 'transitionitem':
                        alignment = self._alignment(next_item)
                        start = self._element_int(item, 'start')
                        if alignment == 'end-black' and start is not None and source_duration is not None:
                            new_end = self._hold_through_sequence_end(
                                start + self._to_sequence_frames(source_duration, item)
                            )
                            if self._set_element_int(item, 'end', new_end):
                                filled_end += 1
                                self._snap_fade(next_item, new_end, alignment, item)
                        else:
                            transition_end = self._element_int(next_item, 'end')
                            if transition_end is not None and self._set_element_int(item, 'end', transition_end):
                                filled_end += 1
                    else:
                        skipped += 1
        print(f"Filled {filled_start} start(s) and {filled_end} end(s) from transitions.")
        if skipped:
            print(f"Left {skipped} start/end -1 value(s) with no adjacent transition.")

    def fixduration(self):
        clips = []
        for track in self._iter_media_tracks():
            clips.extend([child for child in list(track) if child.tag == 'clipitem'])
        rewritten = 0
        print("Fixing Durations...")
        for clip in clips:
            clipstart = self._element_int(clip, 'start')
            clipend = self._element_int(clip, 'end')
            clipin = self._element_number(clip, 'in')
            clipoutxml = self._element_number(clip, 'out')
            if None in (clipstart, clipend, clipin, clipoutxml):
                continue

            if (clipstart < 0) or (clipend < 0):
                continue
            if not self._rates_match(clip):
                continue
            timeline_len = clipend - clipstart
            if abs((clipoutxml - clipin) - timeline_len) > 1e-6:
                if self._set_element_number(clip, 'out', clipin + timeline_len):
                    rewritten += 1
        print(f"Rewrote {rewritten} clip out point(s).")

    def fixdurmismatch(self):
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        status = 1
        print("Fixing Duration Mismatches...")
        # print('\n')
        for clip in clips:
            clipname = clip.find('name').text
            # print("Clip " + str(status) + ": " + clipname)
            status += 1

            clipinval = self._element_number(clip, 'in')
            clipoutval = self._element_number(clip, 'out')
            if clipinval is None or clipoutval is None:
                continue
            clipoutint = int(math.ceil(clipoutval - 1e-9))
            clipduration = clip.find('file/duration')

            if clipduration is None:

                clipfile = clip.find('file')
                if clipfile is None:continue
                search = ".//*[@id='{}']".format(clipfile.attrib['id'])
                master = self.root.find(search)
                clipduration = master.find('duration')

                #print "No File Duration"
                #continue

            if clipduration is None:continue
            clipdurationint = int(clipduration.text)

            if clipoutint > clipdurationint:
                # print("[Fixing Duration Mismatch]")
                clipduration.text = str(clipoutint)

    def update_auto_scale_multiplier(self):
        # Calculate Scale Multiplier
        proxy_x_res = self.proxy_x_res_slider.value
        proxy_y_res = self.proxy_y_res_slider.value
        full_x_res = self.full_x_res_slider.value
        full_y_res = self.full_y_res_slider.value
        proxy_aspect_ratio = proxy_x_res / proxy_y_res
        full_res_aspect_ratio = full_x_res / full_y_res

        if full_res_aspect_ratio >= proxy_aspect_ratio:
            scale_factor_calculation = str(round((proxy_x_res / full_x_res)*100,2))
        else:
            scale_factor_calculation = str(round((proxy_y_res / full_y_res)*100,2))
        self.scale_calculation_bg_label.text = scale_factor_calculation

    def scale_calc_toggle(self):

		# Disables UI elements when button is pressed

        if self.scale_calc_btn.checked:
            self.proxy_x_res_label.setEnabled(True)
            self.proxy_y_res_label.setEnabled(True)
            self.proxy_x_res_slider.setEnabled(True)
            self.proxy_y_res_slider.setEnabled(True)
            self.full_x_res_label.setEnabled(True)
            self.full_y_res_label.setEnabled(True)
            self.full_x_res_slider.setEnabled(True)
            self.full_y_res_slider.setEnabled(True)
            self.scale_calculation_label.setEnabled(True)
            self.scale_calculation_bg_label.setEnabled(True)
            self.scale_factor_label.setEnabled(False)
            self.scale_factor_slider.setEnabled(False)
        else:
            self.proxy_x_res_label.setEnabled(False)
            self.proxy_y_res_label.setEnabled(False)
            self.proxy_x_res_slider.setEnabled(False)
            self.proxy_y_res_slider.setEnabled(False)
            self.full_x_res_label.setEnabled(False)
            self.full_y_res_label.setEnabled(False)
            self.full_x_res_slider.setEnabled(False)
            self.full_y_res_slider.setEnabled(False)
            self.scale_calculation_label.setEnabled(False)
            self.scale_calculation_bg_label.setEnabled(False)
            self.scale_factor_label.setEnabled(True)
            self.scale_factor_slider.setEnabled(True)
    
    def xml_res_toggle(self):

		# Disables UI elements when button is pressed

        if self.xml_res_btn.checked:
                self.online_x_res_label.setEnabled(False)
                self.online_x_res_slider.setEnabled(False)
                self.online_y_res_label.setEnabled(False)
                self.online_y_res_slider.setEnabled(False)
        else:
                self.online_x_res_label.setEnabled(True)
                self.online_x_res_slider.setEnabled(True)
                self.online_y_res_label.setEnabled(True)
                self.online_y_res_slider.setEnabled(True)

    def fix_xml(self):
        for item in self.xml_selection:
            xml_path = item.path
            if os.path.isfile(xml_path):
                pass
            else:
                continue
            print('\n')
            print('*' * 60)
            print("XML File Path: ", xml_path)

            tree = ET.parse(xml_path)
            self.root = tree.getroot()
            
            self.input_sequence_width = int(self.root.find('.//width').text)
            self.input_sequence_height = int(self.root.find('.//height').text)
            print("Offline Res: ",f'{self.input_sequence_width}x{self.input_sequence_height}')
            if self.scale_calc_btn.checked:
                 self.scale_factor = float(self.scale_calculation_bg_label.text)
            else:
                self.scale_factor = self.scale_factor_slider.value
            
            # Calculate Offline vs Online
            if self.xml_res_btn.checked:
                self.online_x_factor = 1
                self.online_y_factor = 1
                output_width = self.input_sequence_width
                output_height = self.input_sequence_height
                print("Online Res:  ",f'{output_width}x{output_height}')
            else:
                self.online_x_res = int(self.online_x_res_slider.value)
                self.online_y_res = int(self.online_y_res_slider.value)
                offline_aspect_ratio = self.input_sequence_width / self.input_sequence_height
                online_aspect_ratio = self.online_x_res / self.online_y_res
                reverse_online_aspect_ratio = self.online_y_res / self.online_x_res
                # Resize the XML Output
                output_width = (self.root.find('.//width'))
                output_height = (self.root.find('.//height'))
                output_width.text = str(self.online_x_res_slider.value)
                output_height.text = str(self.online_y_res_slider.value)
                print("Online Res:  ",f'{output_width.text}x{output_height.text}')

                if online_aspect_ratio >= offline_aspect_ratio:
                    self.conform_scale_factor_calculation = str(round((self.online_x_res / self.input_sequence_width)*100,2))
                    self.online_x_factor = 1
                    self.online_y_factor = 1
                else:
                    self.conform_scale_factor_calculation = str(round((self.online_y_res / self.input_sequence_height)*100,2))
                    self.online_x_factor = round(max(1,(self.input_sequence_width / self.online_x_res_slider.value)) * reverse_online_aspect_ratio ,5)
                    self.online_y_factor = 1
                self.scale_factor = self.scale_factor * float(self.conform_scale_factor_calculation)/100

            self.scalemult = (self.scale_factor / 100)
            self.scale_percent = int(float(self.scale_factor))
            
            print("Scale Factor: ", self.scale_factor)
            print("Online X Repo Factor: ", str(self.online_x_factor))
            print("Online Y Repo Factor: ", str(self.online_y_factor))
            # print('\n')

            #Change Bit Depth
            colordepth = self.root.find('.//colordepth')
            colordepth.text = "project"

            #This function fixes the repos
            self.fixroot = self.fixrepo()

            # Build Output Name
            xml_dir = os.path.dirname(xml_path)
            prepped_dir = os.path.join(xml_dir, "prepped")
            os.makedirs(prepped_dir, exist_ok=True)
            base_name = os.path.basename(xml_path)[:-4]
            outname = os.path.join(prepped_dir, base_name)
            if self.scale_calc_btn.checked:
                outname = f'{outname}_scl_for_{self.full_x_res_slider.value}x{self.full_y_res_slider.value}'
            else:
                outname = f'{outname}_scl_of_{self.scale_percent}'
            
            if self.xml_res_btn.checked:
                outname = f'{outname}'
            else:
                outname = f'{outname}_in_{self.online_x_res_slider.value}x{self.online_y_res_slider.value}'
                outname = outname.replace(".", "_").replace("1080x1350", "4x5").replace("1080x1920", "9x16").replace("1280x1920", "2x3").replace("1920x1080", "16x9").replace("1080x1080", "1x1")

            # Remove 2 or more underscores
            regex = r'_{2,}'
            subst = "_"
            outname = re.sub(regex, subst, outname)

            #Fix Sanitize Names
            if self.sanatize_names_btn.checked:

                # Change Sequence Name to match Outname and remove dumb characterss
                print("Sanatizing Names...")
                clips = self.root.findall(".//sequence")
                for clip in clips:
                    try:
                        xml_name = clip.find('name')
                        seq_name = outname.split("/")[-1]
                        # print('\n' + 'org seq_name: ' + seq_name)

                        # Remove dumb characters
                        remove = ["'", "*", "%", "+",'"',"!","@","#","$","^","&","(",")","=","`","~","<",">",",","/","\\","?", "Copy", "_copy","'"]
                        for items in remove:
                            if items in seq_name:
                                seq_name = seq_name.replace(items, "")
                                outname = outname.replace(items, "")
                        xml_name.text = seq_name
                        # print("new seq_name: ", seq_name)
                    except:
                        print(f"Error: Could not sanatize '{seq_name}' sequence names.")
                        pass

            self.resolve_transition_times()
            self.retag_still_rates()
            self.fix_timewarp_inpoints()

            #Fix Stills Duration
            if self.fix_durations_btn.checked:
                #This function fixes any difference between the clip 'start to end' duration vs. the clip 'in to out' duration
                self.fixduration()
                #This function increases the clip duration if it's shorter that clip 'in to out'
                self.fixdurmismatch()
            else:
                print('Fix Durations was not checked')

            self.stamp_offline_comments()
            
            # Kick out the XMLs
            outname = f'{outname}.xml'
            if os.path.isfile(outname):
                self.window.hide()
                xml = outname.split("/")[-1]
                warning_dialogue = flame.messages.show_in_dialog(
                title = "Warning",
                message = f'"{xml}" alredy exists. Do you want to overwrite it?',
                type = "warning",
                buttons = ["Overwrite"],
                cancel_button = "Cancel")

                if warning_dialogue == "Overwrite":
                    self.window.show()
                    pass
                else:
                    print("Export of XML Canceled")
                    self.window.show()
                    continue
            else:
                pass
            print("Exporting: ", outname.split("/")[-1])
            tree.write(outname)
            print('*' * 60)
        
        self.save_config()
        
        # Refresh MediaHub
        flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        print('\n')


    def main_window(self):

        def cancel_button():
            window.close()

        #------------------------------------#
        # Window Elements

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.fix_xml,
            escape_pressed=cancel_button,
            grid_layout_columns=5,
            grid_layout_rows=10,
            parent=None
            )
        
        # Labels
        self.proxy_diffs_label = PyFlameLabel(text='Scale Footage Options:')    
        self.scale_factor_label = PyFlameLabel(text='Scale Multiplier', style=Style.UNDERLINE)
        self.proxy_x_res_label = PyFlameLabel(text='Proxy X Res', style=Style.UNDERLINE)
        self.proxy_y_res_label = PyFlameLabel(text='Proxy Y Res', style=Style.UNDERLINE)
        self.full_x_res_label = PyFlameLabel(text='Footage X Res', style=Style.UNDERLINE)
        self.full_y_res_label = PyFlameLabel(text='Footage Y Res', style=Style.UNDERLINE)
        self.scale_calculation_label = PyFlameLabel(text='Scale Multiplier', style=Style.UNDERLINE, align=Align.CENTER)
        self.scale_calculation_bg_label = PyFlameLabel(text='100.00', align=Align.CENTER)
        self.offline_diffs_label = PyFlameLabel(text='Resize Sequence Options:')
        self.online_x_res_label = PyFlameLabel(text='Output X Res', style=Style.UNDERLINE)
        self.online_y_res_label = PyFlameLabel(text='Output Y Res', style=Style.UNDERLINE)
        self.other_options_label = PyFlameLabel(text='Other Options:', style=Style.UNDERLINE)
        
        # Sliders
        self.proxy_x_res_slider = PyFlameSlider(start_value=self.settings.proxy_x_res, min_value=720, max_value=15000)
        self.proxy_y_res_slider = PyFlameSlider(start_value=self.settings.proxy_y_res, min_value=480, max_value=15000)
        self.full_x_res_slider = PyFlameSlider(start_value=self.settings.full_x_res, min_value=720, max_value=15000)
        self.full_y_res_slider = PyFlameSlider(start_value=self.settings.full_y_res, min_value=480, max_value=15000)
        self.online_x_res_slider = PyFlameSlider(start_value=self.settings.online_x_res, min_value=720, max_value=15000)
        self.online_y_res_slider = PyFlameSlider(start_value=self.settings.online_y_res, min_value=480, max_value=15000)

        self.sequence_x_slider = PyFlameSlider(start_value=1920, min_value=0, max_value=15000)
        self.sequence_y_slider = PyFlameSlider(start_value=1080, min_value=0, max_value=15000)
        self.scale_factor_slider = PyFlameSlider(start_value=100, min_value=0, max_value=300)

        # Slider Updates
        self.full_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.full_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        
        # Buttons
        self.ok_btn = PyFlameButton(text='Run', connect=self.fix_xml, color=Color.BLUE)
        self.close_btn = PyFlameButton(text='Close', connect=self.window.close)

        # Pushbuttons
        
        # Proxy vs Full Res Calculate Pushbutton
        self.scale_calc_btn = PyFlamePushButton('Auto Calculate', checked=self.settings.scale_calc, connect=self.scale_calc_toggle)
        
        # Use XML Res PushButton
        self.xml_res_btn = PyFlamePushButton('Use XML Res', checked=self.settings.xml_res,connect=self.xml_res_toggle, tooltip='Enable to automatically detect the resolution of your xml.')

        # Fix Stills Pushbutton
        self.fix_durations_btn = PyFlamePushButton('  Fix Durations', checked=self.settings.fix_durations, tooltip='Enable to fix the duration of still frames. Typically graphic elements.')

        # Clean Names Pushbutton
        self.sanatize_names_btn = PyFlamePushButton('  Sanatize Names', checked=self.settings.sanatize_names, tooltip='Enable to try to sanatize the names that will be imported into Flame.')

        #------------------------------------#
        # Window Layout

        self.window.grid_layout.addWidget(self.proxy_diffs_label, 0, 2)

        self.window.grid_layout.addWidget(self.scale_factor_label, 1, 0)
        self.window.grid_layout.addWidget(self.scale_factor_slider, 1, 1)
        self.window.grid_layout.addWidget(self.scale_calculation_label, 1, 2)
        self.window.grid_layout.addWidget(self.scale_calculation_bg_label, 1, 3)
        self.window.grid_layout.addWidget(self.scale_calc_btn, 1, 4)    

        self.window.grid_layout.addWidget(self.proxy_x_res_label, 2, 0)
        self.window.grid_layout.addWidget(self.proxy_x_res_slider, 2, 1)
        self.window.grid_layout.addWidget(self.proxy_y_res_label, 2, 2)
        self.window.grid_layout.addWidget(self.proxy_y_res_slider, 2, 3)

        self.window.grid_layout.addWidget(self.full_x_res_label, 3, 0)
        self.window.grid_layout.addWidget(self.full_x_res_slider, 3, 1)
        self.window.grid_layout.addWidget(self.full_y_res_label, 3, 2)
        self.window.grid_layout.addWidget(self.full_y_res_slider, 3, 3)

        self.window.grid_layout.addWidget(self.offline_diffs_label, 5, 2)

        self.window.grid_layout.addWidget(self.online_x_res_label, 6, 0)
        self.window.grid_layout.addWidget(self.online_x_res_slider, 6, 1)
        self.window.grid_layout.addWidget(self.online_y_res_label, 6, 2)
        self.window.grid_layout.addWidget(self.online_y_res_slider, 6, 3)
        self.window.grid_layout.addWidget(self.xml_res_btn, 6, 4)

        self.window.grid_layout.addWidget(self.other_options_label, 8, 0)
        self.window.grid_layout.addWidget(self.sanatize_names_btn, 8, 1)
        self.window.grid_layout.addWidget(self.fix_durations_btn, 8, 2)

        self.window.grid_layout.addWidget(self.close_btn, 10, 0)
        self.window.grid_layout.addWidget(self.ok_btn, 10, 4)

        # Update Buttons
        self.scale_calc_toggle()
        self.xml_res_toggle()
        self.update_auto_scale_multiplier()


    def save_config(self) -> None:
        """
        Save settings to config file and close window.
        """

        self.settings.save_config(
            config_values={
                'proxy_x_res': self.proxy_x_res_slider.value,
                'proxy_y_res': self.proxy_y_res_slider.value,
                'full_x_res': self.full_x_res_slider.value,
                'full_y_res': self.full_y_res_slider.value,
                'online_x_res': self.online_x_res_slider.value,
                'online_y_res': self.online_y_res_slider.value,
                'scale_calc': self.scale_calc_btn.checked,
                'xml_res': self.xml_res_btn.checked,
                'sanatize_names': self.sanatize_names_btn.checked,
                'fix_durations': self.fix_durations_btn.checked,
                }
            )

        self.window.close()

# ---------------------------------------- #
# Scope

def scope_all_xmls(selection):
    return all(file.path.endswith('.xml') for file in selection)

#-------------------------------------#
# Flame Menus

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': 'XML Prep',
            'actions': [
                {
                    'name': "Fix Premiere XML's",
                    'execute': fix_premiere_xmls,
                    'isVisible': scope_all_xmls,
                    'minimumVersion': '2025.1'
                }
            ]
        }
    ]
