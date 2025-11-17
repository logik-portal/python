"""
Script Name: Sanitize Names
Script Version: 1.0.0
Flame Version: 2022
Written by: John Geehreng
Creation Date: 08.01.23
Update Date: 08.01.23

Script Type: MediaPanel

Description:

    Removes illegal characters and replace spaces with underscores.

Menu:

    Right-click in Media Panel -> UC Renamers -> Sanitize Names

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 08.01.23
        - Initial release.
"""

folder_name = "UC Renamers"
action_name = "Sanitize Names"

def rename_spaces(selection):
    import flame

    for item in selection:

        seq_name = str(item.name)
        # print (seq_name)
        remove = ["'", "*", "%", "+",'"',"!","@","#","$","^","&","(",")","=","`","~","<",">",",","/","\\","?"]
        underscore = [" - "," ","__","___","____"]
        for items in underscore:
            if items in seq_name:
                seq_name = seq_name.replace(items, "_")
        # print (seq_name)
        for items in remove:
            if items in seq_name:
                seq_name = seq_name.replace(items, "").replace('"', "")
        seq_name = seq_name.split("_Exported")[0]
        # print (seq_name)
        item.name = seq_name

def scope_not_desktop(selection):
    import flame

    for item in selection:
        if not isinstance(item, flame.PyDesktop):
            return True
    return False

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': action_name,
                    'isVisible': scope_not_desktop,
                    'execute': rename_spaces,
                    'minimumVersion': '2022'
                }
            ]
        }
    ]
