"""
Script Name: Social Versions
Script Version: 0.3.3
Flame Version: 2023
Author: Kyle Obley (info@kyleobley.com)
Creation Date: 02.05.25
Modified Date: 02.28.25

Description:

Creates social timelines based on other, selected timelines.

Change Log:
v0.3.3  added in_point and out_point to new sequence. fixed a color thing.
v0.3.2  check for original sequence colour before setting new sequence colour.
v0.3.1  Added 'colour = sequence.colour' so new sequences match the color of the original.
v0.2.1  Add Flush Renders. Reversed width and height.
v0.1:   Initial release.

"""
#-------------------------------------
# [Imports]
#-------------------------------------
import flame

#-------------------------------------

def create_11(selection):
    create_timeline(selection, 1080, 1080, "1x1")

def create_45(selection):
    create_timeline(selection, 1080, 1350, "4x5")

def create_916(selection):
    create_timeline(selection, 1080, 1920, "9x16")

#-------------------------------------
# [Main Function]
#-------------------------------------

def create_timeline(selection, width, height, aspect_ratio_name):

    # Get current reel_group via parent.
    reel_group_parent = selection[0].parent.parent

    # Check if a reel for our resolution exists already. If not, create one
    new_reel_name_exists = False
    new_reel_name = str(height) + "x" + str(width)
    new_reel_name = aspect_ratio_name

    for reel in reel_group_parent.reels:
        if reel.name == new_reel_name:
            new_reel_name_exists = True
            target_reel = reel

    # Reel doesn't exist, create one
    if not new_reel_name_exists:
        target_reel = reel_group_parent.create_reel(new_reel_name, sequence=True)

    # Iterate through each sequence and create the actual timelines
    for sequence in selection:

        # Check if 16x9 is in name. If so, replace with aspect ratio. If not, append.
        sequence_name = sequence.name.get_value()

        if "16x9" in sequence_name:
            new_sequence_name = sequence_name.replace("16x9", aspect_ratio_name)
        else:
            new_sequence_name = sequence_name + "_" + aspect_ratio_name

        # Get frame-rate & start time
        frame_rate = sequence.frame_rate
        start_time = sequence.start_time

        start_tc = flame.PyTime(str(sequence.start_time), sequence.frame_rate)
        
        # Get in and out points
        if "<NULL>" in str(sequence.in_mark):
            tc_in = None
        else:
            tc_in = flame.PyTime(str(sequence.in_mark), frame_rate)
        
        if "<NULL>" in str(sequence.out_mark):
            tc_out = None
        else:
            tc_out = flame.PyTime(str(sequence.out_mark), frame_rate)
        
        print(f'In: {tc_in} Out: {tc_out}')
        print('this was updated...')
        
        # clear in and out points
        sequence.in_mark = None
        sequence.out_mark = None

        num_video_trks = len(sequence.versions[0].tracks)
        num_audio_trks = 1

        new_sequence = target_reel.create_sequence(
            name = new_sequence_name,
            height = height,
            width = width,
            bit_depth = sequence.bit_depth,
            frame_rate = frame_rate,
            ratio = (width / height),
            video_tracks = num_video_trks,
            audio_tracks = num_audio_trks,
            scan_mode = "P",
            start_at = start_tc,
            )

        # Set colour to match original if it has been set
        if not sequence.colour == '(0.0, 0.0, 0.0)' and sequence.colour_label == None:
            new_sequence.colour = sequence.colour

        # Overwrite with previous sequence
        new_sequence.overwrite(sequence, flame.PyTime(1))

        # Flush Renders
        new_sequence.flush_renders()

        # Set in and out points to match the original sequence
        if tc_in:
            new_sequence.in_mark = tc_in
            sequence.in_mark = tc_in
        if tc_out:
            new_sequence.out_mark = tc_out
            sequence.out_mark = tc_out

        # Bring positioner to first frame and top version/layer
        new_sequence.current_time = flame.PyTime(1)
        new_sequence.primary_track = new_sequence.versions[-1].tracks[-1]


#-------------------------------------
# [Scope]
#-------------------------------------
def sequence_selected(selection):
    for item in selection:
        if isinstance(item, (flame.PySequence)):
            return True
    return False

#-------------------------------------
# [Media Panel Menu]
#-------------------------------------
def get_media_panel_custom_ui_actions():
    return [
        {
            "name": "Social Versions",
            "actions": [
                {
                    "name": "Create 1x1",
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": create_11
                },
                {
                    "name": "Create 4x5",
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": create_45
                },
                {
                    "name": "Create 9x16",
                    "isVisable": sequence_selected,
                    "isEnabled": sequence_selected,
                    "execute": create_916
                },
            ]
        }
    ]