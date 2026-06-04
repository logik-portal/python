'''
Script Name: remove black frames
Script Version: 1.3.0
Flame Version: 2025
Written by: John Geehreng
Creation Date: 04.08.26
Update Date: 06.04.26

Custom Action Type: Media Panel

Description:

   This script deletes the top track and any residual gap segments - good for removing black frames at the start and end of conforms.

To install:

    Copy script into /opt/Autodesk/shared/python/uppercut or wherever you keep your scripts.

Updates:

    v1.3.0 06.04.26

        Only clean head/tail Gaps on the new top track after deletion. Touching
        lower tracks caused unnecessary re-renders on tracks with content above.

    v1.2.0 06.03.26

        After deleting the top track, scan every remaining track top-to-bottom
        and remove any leading or trailing Gap segments. This restores sequences
        that were extended by Add Black Frames (padding_start / padding_end).

    v1.0.0 04.08.26

        Inception
'''

import flame

FOLDER_NAME = 'UC Timelines'
SCRIPT_NAME = 'Remove Black Frames (Delete Top Track)'

def get_media_panel_custom_ui_actions():
    """
    Make the custom actions appear only on a sequence.
    """

    def scope_clip(selection):
        for item in selection:
            if isinstance(item, flame.PySequence):
                return True
        return False

    def delete_top_track(selection):
        
        # Make sure the user knows what they are doing since this will delete the top track in every selected sequence without discrimination
        warning_dialogue = flame.messages.show_in_dialog(
                            title = "Warning",
                            message = 'This will delete the top track in every selected sequence.\n\nAre you sure you want to continue?',
                            type = "warning",
                            buttons = ["Yes"],
                            cancel_button = "No")
        if warning_dialogue == "Yes":
            for clip in selection:
                for version in clip.versions:
                    if len(version.tracks) > 1:
                        top_track = version.tracks[len(version.tracks) - 1]
                        flame.delete(top_track)

                # Remove head/tail Gaps only on the new top track.
                # Touching tracks below triggers re-renders on any track
                # that has content sitting above those Gaps.
                for version in clip.versions:
                    if not version.tracks:
                        continue
                    new_top = version.tracks[len(version.tracks) - 1]
                    segs = [s for s in list(new_top.segments)
                            if isinstance(s, flame.PySegment)]
                    if not segs:
                        continue
                    if str(segs[0].type) == 'Gap':
                        print(f'[Delete Top Track] Removing head Gap on new top track')
                        flame.delete(segs[0])
                        segs = [s for s in list(new_top.segments)
                                if isinstance(s, flame.PySegment)]
                    if segs and str(segs[-1].type) == 'Gap':
                        print(f'[Delete Top Track] Removing tail Gap on new top track')
                        flame.delete(segs[-1])

                # Go to Frame 1
                clip.current_time = flame.PyTime(1)
        else:
            pass

    return [
        {
            "name": FOLDER_NAME,
            "actions": [
                {
                    "name": SCRIPT_NAME,
                    "isVisible": scope_clip,
                    'order': 13,
                    "separator": "below",
                    "execute": delete_top_track,
                    "minimumVersion": "2025"
                }
            ]
        }
    ]