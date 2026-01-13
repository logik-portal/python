"""
Script Name: remove_XML_crap
Script Version: 0.3.0
Flame Version: 2025
Written by: Ted Stanley, based on John Geehreng's fix_corrupt_actions script

Custom Action Type: MediaPanel

Description:
    Removes Global Axis, Light and Shadow nodes from Action setups imported from XMLs

Menus:
    Media Panel -> Remove XML Crap
"""

import flame
import os
import traceback
import re
from pathlib import Path

FOLDER_NAME = 'KE'
SCRIPT_NAME = 'Remove XML Crap'
SCRIPT_VERSION = 'v.3'

class RemoveXMLCrap():
    def __init__(self, selection) -> None:
        print('\n')
        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION}', '=========]\n')
        self.remove_xml_crap(selection)

    def catch_exception(method):
        def wrapper(self, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except:
                traceback.print_exc()
        return wrapper

    @catch_exception

    def grabnode(self, content):
        number = 0
        nodegroup = ""
        for number, line in enumerate(content,number):
            nodegroup += line
            nodegroup += '\n'
            if line.startswith("End"):
                return nodegroup, number

    def newaction(self, action_path):
        # Read action file
        action_path += "/_action.action"
        #print(os.path.exists(action_path))
        with open(action_path, 'r') as file:
            content = file.read()
        file.close()
        content = content.splitlines()
        #print(content[0])

        ### Find the Intro, stop at Node Group
        intro = ""
        for number, line in enumerate(content, 1):
            if "Node Group" in line:
                #print("Found Node Group")
                break
            intro += line
            intro +='\n'

        content = content[(number-1):]
        print(content[0])

        ### Grab all nodes, stop at ConcreteEnd
        nodegroup = ""
        number = 0
        nodelist = []

        while content[0] != "ConcreteEnd":
            nodegroup, number = self.grabnode(content)
            #print("number = " + str(number))
            content = content[(number+1):]
            nodelist.append(nodegroup)
            #print("nodegoup found " + nodegroup + '\n')
            print(content[0])

        ### Before we go any further, did this Action even come from an XML?
        namelist = []
        for item in nodelist:
            namelist.append(item.splitlines()[1].strip())
        if "Name Global3" not in namelist:
            print("This Action doesn't appear to have come from an XML. No changes made.")
            return

        ### Remove Light and Shadow, extra axes
        modified_nodelist = []
        for item in nodelist:
            if (item.splitlines()[1].strip()) in ("Name Global3", "Name axis_shadow_L1", "Name shadow_L1", "Name light1"):
                continue
            modified_nodelist.append(item)

        ### Fix Node Numbers
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
            #numbered_nodelist.append('\n')
            numbered_nodelist[-1] += '\n'

        ### Fix Children Numbers
        child_nodelist = []
        fixed_child = ""
        for item in numbered_nodelist:
            ### Find Number of surface_L1
            if item.splitlines()[1] == "	Name surface_L1":
                thechild = item.splitlines()[2]
                thechild = re.search(r'\d', thechild)
                #print("Child is " + thechild.group())
        for item in numbered_nodelist:
            ### Update Child of axis_L1 to match surface_L1
            if item.splitlines()[1] == "	Name axis_L1":
                lines = item.splitlines()
                fixed_lines = []
                for line in lines:
                    if line.startswith("	Child "):
                        fixed_child = re.sub(r'\d', thechild.group(), line)
                        fixed_lines.append(fixed_child)
                        print("Fixed Child in axis_L1")
                    ### While we're here, fix axis position in schematic view
                    elif line.startswith("	PosX "):
                        fixed_lines.append("	PosX 0")
                    elif line.startswith("	PosY "):
                        fixed_lines.append("	PosY 0")
                    else:
                        fixed_lines.append(line)
                child_nodelist.append('\n'.join(fixed_lines))
                child_nodelist[-1] += '\n'
            ### Remove Child of surface_L1
            elif item.splitlines()[1] == "	Name surface_L1":
                lines = item.splitlines()
                fixed_lines = []
                for line in lines:
                    if line.startswith("	Child "):
                        print("Removed Child from surface_L1")
                        #continue
                    ### While we're here, fix axis position in schematic view
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

        ### If no Child is found, pick the first one - this Action didn't come from an XML
        if fixed_child == "":
            print("Fixing child...")
            for item in numbered_nodelist:
                lines = item.splitlines()
                for line in lines:
                    if line.startswith("	Child"):
                        fixed_child = line
                        print("I picked the first child I found: " + fixed_child)
                        break
                break

        ### Remove Childs from Node Group
        lines = child_nodelist[0].splitlines()
        fixedline = ""
        for line in lines:
            #print(line)
            if line.startswith("	Child "):
                #print("Removed old Child from Node Group")
                continue
            elif line.startswith("	MotionPath"):
                fixedline += fixed_child + '\n'
                fixedline += line + '\n'
                print("Added new Child to Node Group")
            else:
                fixedline += line + '\n'
        #print(fixedline)
        child_nodelist[0] = fixedline

        ### Create output file
        newfile = intro

        for item in child_nodelist:
            newfile  += item
            print(item.splitlines()[0])

        for item in content:
            newfile += item
            newfile += '\n'

        with open (action_path, 'w') as filenew:
            filenew.write(newfile)

        filenew.close()
        return



    def remove_xml_crap(self, selection):
        project_name = flame.project.current_project.name

        # Setup temporary action path
        action_path = f"/opt/Autodesk/project/{project_name}/tmp/auto_action_temp.action"
        #print(action_path)
        if not os.path.exists(os.path.dirname(action_path)):
            action_path = '/var/tmp/auto_action_temp.action'

        # Process all selected sequences
        for item in selection:
            for version in item.versions:
                for track in version.tracks:
                    for segment in track.segments:
                        for tlfx in segment.effects:
                            if tlfx.type == 'Action':
                                print(f"Processing Action effect in {segment.name}")
                                # Save the action setup
                                tlfx.save_setup(action_path)
                                self.newaction(action_path)
                                # Delete and recreate action
                                flame.delete(tlfx)
                                action_fx = segment.create_effect('Action')
                                action_fx.load_setup(action_path)
                                #segment.colour = (50, 50, 50)  # Mark as processed

        print('[=========', f'{SCRIPT_NAME} {SCRIPT_VERSION} - Complete', '=========]\n')

def scope_sequence(selection):
    return any(isinstance(item, flame.PySequence) for item in selection)

def get_media_panel_custom_ui_actions():
    return [{
        'name': [],
        'actions': [{
            'name': SCRIPT_NAME,
            'execute': RemoveXMLCrap,
            'isVisible': scope_sequence,
            'minimumVersion': '2025'
        }]
    }]
