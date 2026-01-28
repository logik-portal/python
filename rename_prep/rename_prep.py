'''
Script Name: rename_prep
Script Version: 1.9.3
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 10.01.20
Update Date: 01.28.26

Custom Action Type: Media Panel (Clips or Sequences)

Usage: Right click a selection of sequences and look for UC Renamers -> Rename Prep

Description: Sanatize and rename conform prep.

To install: Copy script into /opt/Autodesk/shared/python/rename_prep

Updates:
01.28.26 - v1.9.3 turned off ordering
10.15.24 - v1.9.2 Fixed resolution for 2x3. put imports at the top.
05.01.24 - v1.9.1 Remove :'s and ;'s
04.12.24 - v1.9   Fixed some odd things
11.28.23 - v1.8   Added some Regex because of the updates to the xml script
05.19.23 - v1.7   Changed "CONFORM" to "WIP"
08.25.22 - v1.6   2023.2 Ordering
'''

folder_name = "UC Renamers"
action_name = "Rename Prep"

import flame
import re

def rename_prep(selection):

    for item in selection:
        print ("*" * 10)
        seq_name = str(item.name)[(1):-(1)]
        print ("Start Name: ", seq_name)
        resolution = str(item.width) + "x" + str(item.height)
        # print ("Resolution: " + str(resolution) )
        
        # Remove Exported.##
        regex = r'.exported.\d+'
        subst = ""
        seq_name = re.sub(regex, subst, seq_name, 0, re.IGNORECASE)
        
        # Adjust George's Dumb way of naming thing:
        if re.search(r'CUT \d+.\d+', seq_name):
            seq_name = seq_name.replace('.',"-")
        
        #Get Aspect Ratio
        aspect_ratio = resolution
        if resolution == '1920x1080':
            aspect_ratio = "_16x9"
        elif resolution == '1080x1080':
            aspect_ratio = "_1x1"
        elif resolution == '1280x1920':
            aspect_ratio = "_2x3"
        elif resolution == '1080x1620':
            aspect_ratio = "_2x3"
        elif resolution == '1080x1350':
            aspect_ratio = "_4x5"
        elif resolution == '1080x1920':
            aspect_ratio = "_9x16"
        else:
            aspect_ratio = ""
        # print ("Aspect Ratio is: " + str(aspect_ratio) )

        if re.search(r'v\d+', seq_name):
            version = str(re.findall(r'v\d+', seq_name))[(2):-(2)]
            version_number = re.split('v', version)[1]
            seq_name = re.sub('v\d+',"V" + str(version_number),seq_name)
            # print ("New Version Name: ", seq_name)
        
        # Remove in_##x#
        regex = r'_in_\d+x\d+'
        subst = ""
        seq_name = re.sub(regex, subst, seq_name)
        
        # Remove Garbage
        remove = ["'", "*", "%", "+",'"',"!","@","#","$","^","&","(",")","=","`","~","<",">",",","/","\\","?", ":", ";",
                "Copy", "_copy", "_Edit_", "_EDIT_" , "PICREF", "BURNIN", "picref", "burnin",
                "_export_", "_exported_","_Edit_", "CONFORM_PREP","CONFORM","AAF","XML","_scaled_by_100_percent","ConformPrep","Conform",
                "PREP", "PRE_CONFORM","Prep","1x1","9x16","16x9","1X1","9X16","16X9","4x5","4X5","2x3", "2X3"]
        for items in remove:
            if items in seq_name:
                seq_name = seq_name.replace(items, "")
                
        # Remove scl_of_###
        regex = r'scl_of_\d*'
        subst = ""
        seq_name = re.sub(regex, subst, seq_name)

        # Remove scl_for_####x####
        regex = r'scl_for_\d*x\d*'
        subst = ""
        seq_name = re.sub(regex, subst, seq_name)
        
        # Remove scaled_by_###_percent
        regex = r'scaled_by_\d*_percent'
        subst = ""
        seq_name = re.sub(regex, subst, seq_name)

        seq_name = seq_name.replace(" - ", "_").replace(" ","_")
        new_name = seq_name + aspect_ratio + "_WIP_v01"
        
        # Replace multiple underscores with a single underscore
        regex = r'[\_]+'
        subst = "_"
        new_name = re.sub(regex, subst, new_name)

        item.name = new_name
        print ("New Name: ", new_name)
        print ("*" * 10,"\n")

def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip):
            return True
    return False

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': action_name,
                    # 'order': 6,
                    'isVisible': scope_clip,
                    'execute': rename_prep,
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
