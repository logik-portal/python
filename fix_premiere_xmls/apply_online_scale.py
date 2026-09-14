"""
Script Name: apply online scale
Script Version: 3.4.1
Flame Version: 2025.1
Written by: Ted Stanley, John Geehreng, Michael Vaglienty, and Cursor

Custom Action Type: MediaPanel, Timeline

Description:

    After a prepped Premiere XML has been imported and linked, compare each
    segment's offline WIDTHxHEIGHT comment to the linked clip's source
    resolution, strip XML Action junk, and scale the Action when they differ.

    Fit (default): tighter of width/height so the whole image fits.
    Scale to Frame Size: width only (offline width / online width).
    Example: 1920x1080 -> 4608x3164 is 1920/4608, not 1080/3164.

    Auto Scale Undo restores the Action from immediately before the last Auto
    Scale run. It is only visible when backups exist for the selected sequence.

Menus:

    Media Panel -> XML Prep -> Auto Scale
    Media Panel -> XML Prep -> Auto Scale Undo
    Timeline -> XML Prep -> Auto Scale
    Timeline -> XML Prep -> Auto Scale Undo

Updates:
    09.11.26 - v3.4.1 - Save originals to undo first; never mutate the shared work setup.
    09.11.26 - v3.4.0 - Renamed to Auto Scale. Added Auto Scale Undo.
    09.10.26 - v3.3.5 - Added Scale to Frame Size (width-only) option.
"""

import os
import re
import shutil
import sys
import traceback

import flame

SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
if SCRIPT_PATH not in sys.path:
    sys.path.insert(0, SCRIPT_PATH)

from lib.pyflame_lib_fix_premiere_xmls import *


FOLDER_NAME = 'XML Prep'
SCRIPT_NAME = 'Auto Scale'
UNDO_SCRIPT_NAME = 'Auto Scale Undo'
SCRIPT_VERSION = 'v3.4.1'

TARGET_AXIS_NAMES = {"axis_L1", "axis1"}
SCALING_CHANNELS = {"scaling/x", "scaling/y", "scaling/z"}
RES_PATTERN = re.compile(r'(\d+)\s*x\s*(\d+)', re.IGNORECASE)
OFFLINE_RES_PATTERN = re.compile(r'Offline Resolution:\s*(\d+)\s*x\s*(\d+)', re.IGNORECASE)
XML_CRAP_NODES = ("Name Global3", "Name axis_shadow_L1", "Name shadow_L1", "Name light1")
UNSAFE_PATH_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]')


def auto_scale_config_path() -> str:
    new_path = os.path.join(SCRIPT_PATH, 'config/auto_scale.json')
    old_path = os.path.join(SCRIPT_PATH, 'config/apply_online_scale.json')
    if not os.path.exists(new_path) and os.path.exists(old_path):
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
        shutil.copy2(old_path, new_path)
    return new_path


def flame_name(obj) -> str:
    raw = getattr(obj, 'name', '')
    try:
        raw = raw.get_value()
    except AttributeError:
        pass
    text = str(raw)
    if len(text) >= 2 and text[0] == text[-1] and text[0] in '\'"':
        text = text[1:-1]
    return text


def sanitize_name(name: str) -> str:
    cleaned = UNSAFE_PATH_CHARS.sub('_', str(name)).strip().strip('.')
    return cleaned or 'unnamed'


def project_tmp_root() -> str:
    try:
        project = flame.projects.current_project
        folder = re.sub(r'^/hosts/[^/]+', '', str(project.project_folder))
        if os.path.isdir(folder):
            project_tmp = os.path.join(folder, 'tmp')
            os.makedirs(project_tmp, exist_ok=True)
            return project_tmp
    except Exception:
        traceback.print_exc()

    name = 'flame'
    try:
        name = sanitize_name(flame_name(flame.projects.current_project))
    except Exception:
        pass
    fallback = os.path.join('/var/tmp', 'auto_scale', name)
    os.makedirs(fallback, exist_ok=True)
    return fallback


def remove_path(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)


def work_root() -> str:
    path = os.path.join(project_tmp_root(), 'auto_scale_work')
    os.makedirs(path, exist_ok=True)
    return path


def work_action_path(stem: str) -> str:
    return os.path.join(work_root(), f'{stem}.action')


def undo_root() -> str:
    return os.path.join(project_tmp_root(), 'auto_scale_undo')


def sequence_from_segment(segment):
    track = getattr(segment, 'parent', None)
    version = getattr(track, 'parent', None) if track is not None else None
    if version is None:
        return None
    return getattr(version, 'parent', None)


def sequences_from_selection(selection):
    sequences = []
    seen = set()
    for item in selection:
        sequence = None
        if isinstance(item, flame.PySequence):
            sequence = item
        elif isinstance(item, flame.PySegment):
            sequence = sequence_from_segment(item)
        if sequence is None:
            continue
        key = id(sequence)
        if key in seen:
            continue
        seen.add(key)
        sequences.append(sequence)
    return sequences


def sequence_undo_dir(sequence) -> str:
    return os.path.join(undo_root(), sanitize_name(flame_name(sequence)))


def sequence_has_undo(sequence) -> bool:
    path = sequence_undo_dir(sequence)
    if not os.path.isdir(path):
        return False
    try:
        return any(os.scandir(path))
    except OSError:
        return False


def iter_segments(selection):
    segments = []
    for item in selection:
        if isinstance(item, flame.PySegment):
            segments.append(item)
        elif isinstance(item, flame.PySequence):
            for version in item.versions:
                for track in version.tracks:
                    segments.extend(track.segments)
    return segments


def all_sequence_segments(sequence):
    segments = []
    for version in sequence.versions:
        for track in version.tracks:
            segments.extend(track.segments)
    return segments


def unwrap_value(value):
    try:
        return value.get_value()
    except AttributeError:
        return value


def record_in_token(segment) -> str:
    return sanitize_name(unwrap_value(getattr(segment, 'record_in', '')))


def track_index_token(segment) -> str:
    track = getattr(segment, 'parent', None)
    version = getattr(track, 'parent', None) if track is not None else None
    if version is None:
        return '0'
    try:
        for index, other in enumerate(version.tracks, 1):
            if other is track:
                return str(index)
    except Exception:
        pass
    return sanitize_name(flame_name(track) if track is not None else '0')


def name_is_unique(segment, sequence) -> bool:
    name = sanitize_name(flame_name(segment))
    matches = 0
    for other in all_sequence_segments(sequence):
        if sanitize_name(flame_name(other)) == name:
            matches += 1
            if matches > 1:
                return False
    return True


def segment_backup_stem(segment, sequence) -> str:
    name = sanitize_name(flame_name(segment))
    if sequence is not None and not name_is_unique(segment, sequence):
        return f"{name}__t{track_index_token(segment)}__{record_in_token(segment)}"
    return name


def segment_undo_path(segment, sequence, action_index: int | None = None) -> str:
    stem = segment_backup_stem(segment, sequence)
    if action_index is None:
        filename = f'{stem}.action'
    else:
        filename = f'{stem}__a{action_index}.action'
    return os.path.join(sequence_undo_dir(sequence), filename)


def backup_paths_for_segment(segment, sequence) -> list[str]:
    seq_dir = sequence_undo_dir(sequence)
    stem = segment_backup_stem(segment, sequence)
    indexed = []
    index = 0
    while True:
        path = os.path.join(seq_dir, f'{stem}__a{index}.action')
        if not os.path.isdir(path):
            break
        indexed.append(path)
        index += 1
    if indexed:
        return indexed
    single = os.path.join(seq_dir, f'{stem}.action')
    if os.path.isdir(single):
        return [single]
    return []


def copy_setup(source: str, destination: str) -> None:
    if os.path.isdir(destination):
        shutil.rmtree(destination)
    shutil.copytree(source, destination)


def remove_backup(path: str) -> None:
    if os.path.isdir(path):
        shutil.rmtree(path)
    parent = os.path.dirname(path)
    try:
        if os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)
    except OSError:
        pass


def action_effects(segment):
    return [tlfx for tlfx in segment.effects if tlfx.type == 'Action']


def scope_sequence(selection):
    return any(isinstance(item, flame.PySequence) for item in selection)


def scope_segment(selection):
    for item in selection:
        if isinstance(item, flame.PySegment):
            return True
    return False


def scope_undo_media_panel(selection):
    if not scope_sequence(selection):
        return False
    return any(sequence_has_undo(sequence) for sequence in sequences_from_selection(selection))


def scope_undo_timeline(selection):
    if not scope_segment(selection):
        return False
    return any(sequence_has_undo(sequence) for sequence in sequences_from_selection(selection))


def get_media_panel_custom_ui_actions():
    return [{
        'name': FOLDER_NAME,
        'actions': [
            {
                'name': SCRIPT_NAME,
                'execute': AutoScale,
                'isVisible': scope_sequence,
                'minimumVersion': '2025.1'
            },
            {
                'name': UNDO_SCRIPT_NAME,
                'execute': AutoScaleUndo,
                'isVisible': scope_undo_media_panel,
                'minimumVersion': '2025.1'
            },
        ]
    }]


def get_timeline_custom_ui_actions():
    return [{
        'name': FOLDER_NAME,
        'actions': [
            {
                'name': SCRIPT_NAME,
                'execute': AutoScale,
                'isVisible': scope_segment,
                'minimumVersion': '2025.1'
            },
            {
                'name': UNDO_SCRIPT_NAME,
                'execute': AutoScaleUndo,
                'isVisible': scope_undo_timeline,
                'minimumVersion': '2025.1'
            },
        ]
    }]


def parse_offline_res(comment) -> tuple[int, int] | None:
    text = str(comment)
    labeled = OFFLINE_RES_PATTERN.search(text)
    if labeled:
        return int(labeled.group(1)), int(labeled.group(2))
    matches = RES_PATTERN.findall(text)
    if not matches:
        return None
    width, height = matches[0]
    return int(width), int(height)


def online_res(segment) -> tuple[int, int] | None:
    try:
        width = int(segment.source_width)
        height = int(segment.source_height)
    except (TypeError, ValueError, AttributeError):
        return None
    if width <= 0 or height <= 0:
        return None
    return width, height


def scale_factor(
    offline_w: int,
    offline_h: int,
    online_w: int,
    online_h: int,
    scale_to_frame_size: bool = False,
) -> float:
    if scale_to_frame_size:
        return offline_w / online_w
    online_ar = online_w / online_h
    offline_ar = offline_w / offline_h
    if online_ar >= offline_ar:
        return offline_w / online_w
    return offline_h / online_h


class AutoScale():

    def __init__(self, selection) -> None:
        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        self.selection = selection
        self.settings = PyFlameConfig(
            config_values={
                'scale_to_frame_size': False,
            },
            config_path=auto_scale_config_path(),
            script_name=SCRIPT_NAME,
        )
        self.scale_to_frame_size = bool(self.settings.scale_to_frame_size)
        self.main_window()

    def main_window(self):
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.apply_from_ui,
            escape_pressed=self.cancel,
            grid_layout_columns=2,
            grid_layout_rows=3,
            parent=None,
        )

        self.scale_options_label = PyFlameLabel(text='Scale Options:')
        self.scale_to_frame_size_btn = PyFlamePushButton(
            'Scale to Frame Size',
            checked=self.scale_to_frame_size,
            tooltip='On: width only (e.g. 1920/4608). Off: Fit, the tighter of width or height so the whole image fits (e.g. 1080/3164).',
        )
        self.cancel_btn = PyFlameButton(text='Cancel', connect=self.cancel)
        self.apply_btn = PyFlameButton(text='Apply', connect=self.apply_from_ui, color=Color.BLUE)

        self.window.grid_layout.addWidget(self.scale_options_label, 0, 0)
        self.window.grid_layout.addWidget(self.scale_to_frame_size_btn, 1, 0, 1, 2)
        self.window.grid_layout.addWidget(self.cancel_btn, 3, 0)
        self.window.grid_layout.addWidget(self.apply_btn, 3, 1)

    def cancel(self):
        self.window.close()
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Canceled', '=========]\n')

    def apply_from_ui(self):
        self.scale_to_frame_size = self.scale_to_frame_size_btn.checked
        self.settings.save_config(
            config_values={
                'scale_to_frame_size': self.scale_to_frame_size,
            },
            config_path=auto_scale_config_path(),
        )
        self.window.close()
        self.apply(self.selection)

    def grabnode(self, content):
        number = 0
        nodegroup = ""
        for number, line in enumerate(content, number):
            nodegroup += line
            nodegroup += '\n'
            if line.startswith("End"):
                return nodegroup, number

    def newaction(self, action_path):
        action_path += "/_action.action"
        with open(action_path, 'r') as file:
            content = file.read()
        content = content.splitlines()

        intro = ""
        for number, line in enumerate(content, 1):
            if "Node Group" in line:
                break
            intro += line
            intro += '\n'

        content = content[(number - 1):]
        nodelist = []

        while content and content[0] != "ConcreteEnd":
            nodegroup, number = self.grabnode(content)
            content = content[(number + 1):]
            nodelist.append(nodegroup)

        namelist = [item.splitlines()[1].strip() for item in nodelist]
        if "Name Global3" not in namelist:
            print("This Action doesn't appear to have come from an XML. No cleanup made.")
            return

        modified_nodelist = []
        for item in nodelist:
            if (item.splitlines()[1].strip()) in XML_CRAP_NODES:
                continue
            modified_nodelist.append(item)

        node_number = 0
        numbered_nodelist = []
        for item in modified_nodelist:
            lines = item.splitlines()
            fixed_lines = []
            for line in lines:
                if line.startswith("	Number "):
                    fixed_lines.append(f"	Number {node_number}")
                    node_number += 1
                else:
                    fixed_lines.append(line)
            numbered_nodelist.append('\n'.join(fixed_lines))
            numbered_nodelist[-1] += '\n'

        child_nodelist = []
        fixed_child = ""
        thechild = None
        for item in numbered_nodelist:
            if item.splitlines()[1] == "	Name surface_L1":
                thechild = item.splitlines()[2]
                thechild = re.search(r'\d', thechild)
        for item in numbered_nodelist:
            if item.splitlines()[1] == "	Name axis_L1":
                lines = item.splitlines()
                fixed_lines = []
                for line in lines:
                    if line.startswith("	Child "):
                        if thechild is not None:
                            fixed_child = re.sub(r'\d', thechild.group(), line)
                        else:
                            fixed_child = line
                        fixed_lines.append(fixed_child)
                        print("Fixed Child in axis_L1")
                    elif line.startswith("	PosX "):
                        fixed_lines.append("	PosX 0")
                    elif line.startswith("	PosY "):
                        fixed_lines.append("	PosY 0")
                    else:
                        fixed_lines.append(line)
                child_nodelist.append('\n'.join(fixed_lines))
                child_nodelist[-1] += '\n'
            elif item.splitlines()[1] == "	Name surface_L1":
                lines = item.splitlines()
                fixed_lines = []
                for line in lines:
                    if line.startswith("	Child "):
                        print("Removed Child from surface_L1")
                    elif line.startswith("	PosX "):
                        fixed_lines.append("	PosX 0")
                    elif line.startswith("	PosY "):
                        fixed_lines.append("	PosY -125")
                    else:
                        fixed_lines.append(line)
                child_nodelist.append('\n'.join(fixed_lines))
                child_nodelist[-1] += '\n'
            else:
                child_nodelist.append(item)

        if fixed_child == "":
            print("Fixing child...")
            for item in numbered_nodelist:
                for line in item.splitlines():
                    if line.startswith("	Child"):
                        fixed_child = line
                        print("I picked the first child I found: " + fixed_child)
                        break
                break

        if not child_nodelist:
            return

        lines = child_nodelist[0].splitlines()
        fixedline = ""
        for line in lines:
            if line.startswith("	Child "):
                continue
            elif line.startswith("	MotionPath"):
                fixedline += fixed_child + '\n'
                fixedline += line + '\n'
                print("Added new Child to Node Group")
            else:
                fixedline += line + '\n'
        child_nodelist[0] = fixedline

        newfile = intro
        for item in child_nodelist:
            newfile += item
        for item in content:
            newfile += item
            newfile += '\n'

        with open(action_path, 'w') as filenew:
            filenew.write(newfile)

    def scale_action_file(self, input_path: str, output_path: str, multiplier: float) -> None:
        input_path += "/_action.action"
        output_path += "/_action.action"
        with open(input_path, "r") as f:
            lines = f.readlines()

        output_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            if line.strip() == "Node Axis":
                node_lines = [line]
                i += 1

                axis_name = None
                while i < len(lines):
                    node_lines.append(lines[i])
                    name_match = re.match(r'^\s*Name\s+(\S+)', lines[i])
                    if name_match:
                        axis_name = name_match.group(1)
                        i += 1
                        break
                    i += 1

                should_scale = axis_name in TARGET_AXIS_NAMES
                in_specifics = False
                brace_depth = 0
                in_target_channel = False

                while i < len(lines):
                    current_line = lines[i]
                    stripped = current_line.strip()

                    if stripped == "Specifics":
                        in_specifics = True

                    if in_specifics:
                        if "{" in stripped:
                            brace_depth += stripped.count("{")
                        if "}" in stripped:
                            brace_depth -= stripped.count("}")
                            if brace_depth <= 0:
                                in_specifics = False
                                in_target_channel = False

                    channel_match = re.match(r'^\s*Channel\s+(\S+)', current_line)
                    if channel_match:
                        channel_name = channel_match.group(1)
                        in_target_channel = should_scale and (channel_name in SCALING_CHANNELS)

                    if re.match(r'^\s*ChannelEnd', current_line):
                        in_target_channel = False

                    if in_target_channel:
                        value_match = re.match(r'^(\s*Value\s+)([0-9eE+\-\.]+)(\s*)$', current_line)
                        if value_match:
                            original = float(value_match.group(2))
                            scaled = original * multiplier
                            current_line = f"{value_match.group(1)}{scaled:.10g}{value_match.group(3)}\n"

                    node_lines.append(current_line)

                    if stripped == "End" and not in_specifics and brace_depth == 0:
                        i += 1
                        break

                    i += 1

                output_lines.extend(node_lines)
                continue

            output_lines.append(line)
            i += 1

        with open(output_path, "w") as f:
            f.writelines(output_lines)

    def save_original_to_undo(self, tlfx, segment, sequence, action_index: int, action_count: int) -> str | None:
        if sequence is None:
            print("    Backup:  skipped (no parent sequence)")
            return None
        os.makedirs(sequence_undo_dir(sequence), exist_ok=True)
        index = action_index if action_count > 1 else None
        destination = segment_undo_path(segment, sequence, index)
        remove_path(destination)
        tlfx.save_setup(destination)
        print(f"    Backup:  {destination}")
        return destination

    def apply(self, selection):
        explicit_segments = {id(item) for item in selection if isinstance(item, flame.PySegment)}
        mode_label = 'Scale to Frame Size (width)' if self.scale_to_frame_size else 'Fit'

        scaled = 0
        cleaned_only = 0
        skipped_no_comment = 0
        skipped_no_action = 0
        skipped_error = 0
        backed_up = 0

        remove_path(os.path.join(project_tmp_root(), 'auto_action_temp.action'))

        print(f"Scale mode: {mode_label}")
        print(f"Work root:  {work_root()}")
        print(f"Undo root:  {undo_root()}\n")

        for segment in iter_segments(selection):
            actions = action_effects(segment)
            if not actions:
                if id(segment) in explicit_segments:
                    skipped_no_action += 1
                continue

            offline = parse_offline_res(getattr(segment, 'comment', ''))
            if offline is None:
                skipped_no_comment += 1
                print(f"Skip (no offline res comment): {flame_name(segment)}")
                continue

            online = online_res(segment)
            same_res = online is not None and offline == online
            multiplier = None
            if online is not None and not same_res:
                multiplier = scale_factor(
                    offline[0],
                    offline[1],
                    online[0],
                    online[1],
                    scale_to_frame_size=self.scale_to_frame_size,
                )

            sequence = sequence_from_segment(segment)
            processed_ok = False
            for action_index, tlfx in enumerate(actions):
                try:
                    print(f"*-- Processing Action in {flame_name(segment)} --*")
                    print(f"    Offline: {offline[0]}x{offline[1]}")
                    if online:
                        print(f"    Online:  {online[0]}x{online[1]}")
                    else:
                        print("    Online:  unavailable")

                    undo_path = self.save_original_to_undo(
                        tlfx, segment, sequence, action_index, len(actions)
                    )
                    work_stem = segment_backup_stem(segment, sequence)
                    if len(actions) > 1:
                        work_stem = f'{work_stem}__a{action_index}'
                    action_path = work_action_path(work_stem)
                    remove_path(action_path)
                    if undo_path and os.path.isdir(undo_path):
                        copy_setup(undo_path, action_path)
                        backed_up += 1
                    else:
                        tlfx.save_setup(action_path)

                    self.newaction(action_path)

                    if multiplier is not None:
                        if self.scale_to_frame_size:
                            print(f"    Scale:   {offline[0]}/{online[0]} = {multiplier} ({mode_label})")
                        else:
                            print(f"    Scale:   {multiplier} ({mode_label})")
                        self.scale_action_file(action_path, action_path, multiplier)
                    elif same_res:
                        print("    Scale:   skipped (same res)")
                    else:
                        print("    Scale:   skipped (no online res)")

                    flame.delete(tlfx)
                    action_fx = segment.create_effect('Action')
                    action_fx.load_setup(action_path)
                    processed_ok = True
                except Exception:
                    traceback.print_exc()
                    skipped_error += 1
                    continue

            if not processed_ok:
                continue

            if multiplier is not None:
                scaled += 1
            else:
                cleaned_only += 1

        summary = (
            f"Mode: {mode_label}\n"
            f"Scaled and cleaned: {scaled}\n"
            f"Cleaned only (same res): {cleaned_only}\n"
            f"Backed up: {backed_up}\n"
            f"Skipped (no comment): {skipped_no_comment}\n"
            f"Skipped (no Action): {skipped_no_action}"
        )
        if skipped_error:
            summary += f"\nErrors: {skipped_error}"

        print(summary)
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')

        flame.messages.show_in_dialog(
            title=f"{SCRIPT_NAME} {SCRIPT_VERSION}",
            message=summary,
            type="info",
            buttons=["Ok"],
        )


class AutoScaleUndo():

    def __init__(self, selection) -> None:
        print('\n')
        print('[=========', f'{UNDO_SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        self.restore(selection)

    def restore_segment(self, segment) -> bool:
        sequence = sequence_from_segment(segment)
        if sequence is None:
            print(f"Skip (no parent sequence): {flame_name(segment)}")
            return False

        backups = backup_paths_for_segment(segment, sequence)
        if not backups:
            return False

        print(f"*-- Restoring Action in {flame_name(segment)} --*")
        for tlfx in action_effects(segment):
            flame.delete(tlfx)

        restored_any = False
        for backup in backups:
            try:
                print(f"    Load: {backup}")
                action_fx = segment.create_effect('Action')
                action_fx.load_setup(backup)
                remove_backup(backup)
                restored_any = True
            except Exception:
                traceback.print_exc()
                continue
        return restored_any

    def restore(self, selection):
        restored = 0
        skipped_no_backup = 0
        skipped_error = 0

        print(f"Undo root: {undo_root()}\n")

        for segment in iter_segments(selection):
            sequence = sequence_from_segment(segment)
            backups = backup_paths_for_segment(segment, sequence) if sequence is not None else []
            if not backups:
                if action_effects(segment):
                    skipped_no_backup += 1
                continue
            try:
                if self.restore_segment(segment):
                    restored += 1
                else:
                    skipped_error += 1
            except Exception:
                traceback.print_exc()
                skipped_error += 1

        summary = (
            f"Restored: {restored}\n"
            f"Skipped (no backup): {skipped_no_backup}"
        )
        if skipped_error:
            summary += f"\nErrors: {skipped_error}"

        print(summary)
        print('[=========', f'{UNDO_SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')

        flame.messages.show_in_dialog(
            title=f"{UNDO_SCRIPT_NAME} {SCRIPT_VERSION}",
            message=summary,
            type="info",
            buttons=["Ok"],
        )
