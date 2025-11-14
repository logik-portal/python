'''
Script Name: premiere_xml_mediahub
Script Version: 1.91
Flame Version: 2023
Written by: Ted Stanley, John Geehreng, and Mike V
Creation Date: 03.03.21
Update Date: 04.18.22

Description: This provides a UI for Ted Stanley's awesome script found on the Logik Forums.
With Mike V's help, it also adds a scale factor to compensate for the difference between proxy resolution
and the full resolution of the clips in Flame.
To obtain the scale factor, divide the proxy resolution by the full resolution of your clips and then multiply by 100.
If math is not your thing, you can also figure it out by creating a new axis in Action, parenting it under the axis that has the repo data on it, and manually find the scale difference.

If the aspect ratios of the proxy files are the same as the full res clips, you can use either the x or y value.
If the proxy files have a letterbox use (proxy x res / full res x res)
If the proxy files have pillar bars, use (proxy y res / full res y res)
If you have multiple resolutions, run the script as many times as needed. It will name them based on the scale factor.

03.19.21 - Python3 Updates
05.17.21 - Added the ability to select multiple .xml's and added Ted's nested layer fix
06.04.21 - Change Default Scale Value to 100 for graphics. Renamed "Cancel" button to say "Close"
08.13.21 - Change XML Bit Depth to Project Settings
08.27.21 - Turned off the "That Totally Worked" message as you can see the update in the MediaHub
09.03.21 - Made sanatizing the names optional
11.15.21 - Added the ability to scale values over 100
12.27.21 - Turned off "v" to "V" when sanatizing names
02.19.22 - Created option for automatically using the xml's resolution (v1.9)
04.19.22 - 2023 UI (v1.91)
'''

from __future__ import print_function
from __future__ import absolute_import
from flame_widgets_premiere_xml import FlameButton, FlameLabel, FlamePushButtonMenu, FlameWindow, FlamePushButton, FlameSlider

folder_name = "XML Prep"
action_name = "Fix Adobe Premiere XML's"
VERSION = 'v1.91'

from PySide2 import QtWidgets, QtCore, QtGui

def main_window(selection):
    import os
    import flame

    def ok_button():
        for item in selection:
            global xml_file_path,xml_folder,xml_path_entry
            print ('\n'*10, '>' * 20, 'Fix Adobe Premiere XMLs Finished', '<' * 20, '\n'*10)
            xml_path_entry = item.path
            print ("xml_file_path: ", xml_file_path)
            fix_xml(item)

        try:
            flame.execute_shortcut("Refresh the MediaHub's Folders and Files")
        except:
            pass

    def fix_xml(xml):
        import xml.etree.ElementTree as ET

        xml = xml_path_entry
        clip_path = str(xml).rsplit('/', 1)[0]
        sequence_x_res = int(sequence_x_slider.text())
        sequence_y_res = int(sequence_y_slider.text())
        scale_factor = float(scale_factor_slider.text())
        scale_percent = int(float(scale_factor))

        print ('\n', '>' * 20, 'Fix Adobe Premiere XMLs Start', '<' * 20, '\n')
        print ('xml name: ', xml)
        # print ('sequence_x_res: ',sequence_x_res)
        # print ('sequence_y_res: ',sequence_y_res)
        print ('scale factor: ', scale_factor)

        tree = ET.parse(xml)
        root = tree.getroot()

        #detect sequence width
        sequence_width = int(root.find('.//width').text)
        sequence_height = int(root.find('.//height').text)
        # print ("sequence_width: " , sequence_width)
        # print ("sequence_height: " , sequence_height)

        if auto_res_btn.isChecked():
            print ("Auto Res Checked:")
            sequence_x_res = sequence_width
            sequence_y_res = sequence_height
        else:
            print ('\n', 'Use XML Res button was not checked.', '\n')

        print ("sequence_x_res: " , sequence_x_res)
        print ("sequence_y_res: " , sequence_y_res)
        print ('\n')

        #Change Bit Depth
        colordepth = root.find('.//colordepth')
        colordepth.text = "project"

        # clips = root.findall(".//clipitem")
        clips = root.findall(".//sequence/media/video/*/clipitem")
        status = 1
        for clip in clips:
            print ("Clip " + str(status))
            status += 1

            file = clip.find('file')
            if file is None:
                print ("ERROR: No file, maybe a nest?")
                continue
            search = ".//*[@id='{}']".format(list((file.attrib).items())[0][1])
            master = root.find(search)

            cliphoriz = master.find(".//media/video/samplecharacteristics/width").text
            cliphoriz = int(cliphoriz)
            clipvert = master.find(".//media/video/samplecharacteristics/height").text
            clipvert = int(clipvert)

            parameter = clip.find(".//filter/effect/[name='Basic Motion']/parameter/[name='Center']")
            if parameter is None: continue
            xmlhoriz = parameter[2][0].text
            xmlhoriz = float(xmlhoriz)
            xmlvert = parameter[2][1].text
            xmlvert = float(xmlvert)

            newxmlhoriz = (xmlhoriz * cliphoriz) / sequence_x_res
            newxmlvert = (xmlvert * clipvert) / sequence_y_res

            if newxmlhoriz == 0: newxmlhoriz = int(newxmlhoriz)
            if newxmlvert == 0: newxmlvert = int(newxmlvert)
            print ("*" * 100)
            print (parameter[2][0].text + " <-- Old vs New X Repo --> " + str(newxmlhoriz))
            print (parameter[2][1].text + "<-- Old vs New Y Repo -->" + str(newxmlvert))
            print ("*" * 100)
            parameter[2][0].text = str(newxmlhoriz)
            parameter[2][1].text = str(newxmlvert)

            # Edit Keyframe positions
            for center_keyframe_parameter in clip.findall(".//filter/effect/[name='Basic Motion']/parameter/[name='Center']/keyframe"):
                print ("*" * 100)
                print ('center_keyframe_parameter:', center_keyframe_parameter)
                center_x_keyframe_value = float(center_keyframe_parameter[1][0].text)
                center_y_keyframe_value = float(center_keyframe_parameter[1][1].text)
                print ('center_x_keyframe_value: ', center_x_keyframe_value)
                print ('center_y_keyframe_value: ', center_y_keyframe_value)
                print ("*" * 100)

                new_center_x_keyframe_value = (center_x_keyframe_value * cliphoriz) / sequence_x_res
                new_center_y_keyframe_value = (center_y_keyframe_value * clipvert) / sequence_y_res

                if new_center_x_keyframe_value == 0: new_center_x_keyframe_value = int(new_center_x_keyframe_value)
                if new_center_y_keyframe_value == 0: new_center_y_keyframe_value = int(new_center_y_keyframe_value)

                print ("*" * 100)
                print ("new_center_x_keyframe_value: ", new_center_x_keyframe_value)
                print ("new_center_y_keyframe_value: ", new_center_y_keyframe_value)
                print ("*" * 100)

                center_keyframe_parameter[1][0].text = str(new_center_x_keyframe_value)
                center_keyframe_parameter[1][1].text = str(new_center_y_keyframe_value)


            # Edit Scale Value

            scale_parameter = clip.find(".//filter/effect/[name='Basic Motion']/parameter/[name='Scale']")
            if scale_parameter is None: continue
            scale_value = float(scale_parameter[4].text)
            print ('scale_value:', scale_value)

            new_scale_value = scale_value * (scale_factor/100)
            print ('new_scale_value:', new_scale_value)

            scale_parameter[4].text = str(new_scale_value)

            # Edit Scale Keyframed Value

            for scale_keyframe_parameter in clip.findall(".//filter/effect/[name='Basic Motion']/parameter/[name='Scale']/keyframe/value"):
                print ("*" * 100)
                print ('scale_keyframe_parameter:', scale_keyframe_parameter)
                scale_keyframe_value = float(scale_keyframe_parameter.text)
                print ('scale_keyframe_value:', scale_keyframe_value)
                new_scale_kf_value = scale_keyframe_value * (scale_factor/100)
                print ('new_scale_value:', new_scale_kf_value)
                # print ("\n" *2)
                print ("*" * 100)
                scale_keyframe_parameter.text = str(new_scale_kf_value)
        #Fix Sanitize Names
        if sanatize_names_btn.isChecked():
            # Change Sequence Name
            clips = root.findall(".//sequence")
            for clip in clips:
                xml_name = clip.find('name')
                seq_name = xml_name.text
                print ('\n' + 'org seq_name: ' + seq_name)
                remove = ["_v1_", "_v2","_01_", "Copy", "_copy", ".Exported.01","_export_", "_exported_", "'","_AAF","_XML","_Conform","_PREP","PREP","_PRE_CONFORM","PRE_CONFORM","_PRE","_CONFORM","CONFORM"]
                underscore = [" - "," ","__"]
                for items in underscore:
                    if items in seq_name:
                        seq_name = seq_name.replace(items, "_")
                for items in remove:
                    if items in seq_name:
                        seq_name = seq_name.replace(items, "")
                seq_name = seq_name.split("_Exported")[0]
                # seq_name = seq_name.replace('v', "V")
                seq_name = seq_name + "_scaled_by_" + str(scale_percent) + "_percent"
                xml_name.text = str(seq_name)
                print ("new seq_name: ", seq_name)

        #Fix Stills Duration
        if fix_durations_btn.isChecked():
            print ('\n', 'Fix Durations Button was Checked','\n', )
            clips = root.findall(".//sequence/media/video/*/clipitem")
            new_status = 1
            print ("Fixing durations...")
            for clip in clips:
                clipname = clip.find('name').text
                print ("Clip " + str(new_status) + ": " + clipname)

                new_status += 1

                clipstart = int(clip.find('start').text)
                clipend = int(clip.find('end').text)
                clipin = int(clip.find('in').text)
                clipoutxml = int(clip.find('out').text)

                if (clipend - clipstart) == (clipoutxml - clipin): continue
                if (clipstart < 0) or (clipend < 0): continue

                print ("[Fixing Clip Out]")

                clipout = clip.find('out')
                clipout.text = str(clipin + (clipend - clipstart))

            outname = xml[:-4] + "_scaled_" + str(scale_factor) + "_percent_and_fixed_durations.xml"
            tree.write(outname)

        else:
            print ('\n', 'Fix Durations was not checked', '\n')
            outname = xml[:-4] + "_scaled_" + str(scale_factor) + "_percent.xml"
            tree.write(outname)

    def xml_res_toggle():

        # Disables UI elements when button is pressed

        if auto_res_btn.isChecked():
            sequence_x_res.setEnabled(False)
            sequence_y_res.setEnabled(False)
            sequence_x_slider.setEnabled(False)
            sequence_y_slider.setEnabled(False)
            # sequence_x_lineedit.setEnabled(False)
            # sequence_y_lineedit.setEnabled(False)

        else:
            sequence_x_res.setEnabled(True)
            sequence_y_res.setEnabled(True)
            sequence_x_slider.setEnabled(True)
            sequence_y_slider.setEnabled(True)
            # sequence_x_lineedit.setEnabled(True)
            # sequence_y_lineedit.setEnabled(True)

    # Window and UI Below
    grid_layout = QtWidgets.QGridLayout()
    window = FlameWindow(f'Fix Adobe Premiere XML\'s <small>{VERSION}', grid_layout, 750, 250)

    # Labels
    sequence_x_res = FlameLabel('Sequence X Res', 'underline')
    sequence_y_res = FlameLabel('Sequence Y Res', 'underline')
    scale_factor_label = FlameLabel('Scale Multiplier', 'underline')
    other_options_label = FlameLabel('Other Options', 'underline')

    # Sliders
    sequence_x_slider = FlameSlider(1920, 0, 15000, False)
    sequence_y_slider = FlameSlider(1080, 0, 15000, False)
    scale_factor_slider = FlameSlider(100, 0, 300, True)

    # Fix Stills Pushbutton
    fix_durations_btn = FlamePushButton(' Fix Durations', True, button_width=110)
    fix_durations_btn.setToolTip('Enable to fix the duration of still frames. Typically graphic elements.')

    # Clean Names Pushbutton
    sanatize_names_btn = FlamePushButton(' Clean Names', True, button_width=110)
    sanatize_names_btn.setToolTip('Enable to sanatize the names that will be imported into Flame.')

    # Auto Res Pushbutton
    auto_res_btn = FlamePushButton(' Use XML Res', True, connect=xml_res_toggle,button_width=110)
    auto_res_btn.setToolTip('Enable to automatically detect the resolution of your xml.')

    # Check auto_res_btn state when script starts
    xml_res_toggle()

    #Other Buttons
    ok_btn = FlameButton('Ok',ok_button, button_color='blue',button_width=100, button_max_width=110)
    cancel_btn = FlameButton('Close',window.close, button_color='normal',button_width=100, button_max_width=110)

    # Grid Layout
    grid_layout.setMargin(10)
    grid_layout.setVerticalSpacing(20)
    grid_layout.setHorizontalSpacing(5)

    grid_layout.addWidget(sequence_x_res, 0, 0)
    grid_layout.addWidget(sequence_x_slider, 0, 1)

    grid_layout.setColumnMinimumWidth(2, 100)

    grid_layout.addWidget(sequence_y_res, 0, 2)
    grid_layout.addWidget(sequence_y_slider, 0, 3)
    grid_layout.addWidget(auto_res_btn, 0, 4)

    grid_layout.addWidget(scale_factor_label, 1, 0)
    grid_layout.addWidget(scale_factor_slider, 1, 1)
    grid_layout.addWidget(other_options_label, 1, 2)
    grid_layout.addWidget(sanatize_names_btn, 1, 3)
    grid_layout.addWidget(fix_durations_btn, 1, 4)

    grid_layout.addWidget(cancel_btn, 2, 1)
    grid_layout.addWidget(ok_btn, 2, 4)

    window.show()

    return window

def message_box(message):
    from PySide2 import QtWidgets, QtCore

    message_box_window = QtWidgets.QMessageBox()
    message_box_window.setWindowTitle('Big Success')
    message_box_window.setText('<b><center>%s' % message)
    msg_box_button = message_box_window.addButton(QtWidgets.QMessageBox.Ok)
    msg_box_button.setFocusPolicy(QtCore.Qt.NoFocus)
    msg_box_button.setMinimumSize(QtCore.QSize(80, 28))
    message_box_window.setStyleSheet('QMessageBox {background-color: #313131; font: 14px "Discreet"}'
                                     'QLabel {color: #9a9a9a; font: 14px "Discreet"}'
                                     'QPushButton {color: #9a9a9a; background-color: #424142; border-top: 1px inset #555555; border-bottom: 1px inset black; font: 14px "Discreet"}'
                                     'QPushButton:pressed {color: #d9d9d9; background-color: #4f4f4f; border-top: 1px inset #666666; font: italic}')
    message = message_box_window.exec_()

    return message

def scope_xml(selection):
    import flame
    import os
    for item in selection:
        global xml_file_path,xml_folder
        xml_file_path = item.path
        file_name, file_extension = os.path.splitext(xml_file_path)
        if file_extension == ".xml":
            return True
    return False

def get_mediahub_files_custom_ui_actions():

    return [
        {
            'name': folder_name,
            'actions': [
                {
                    'name': action_name,
                    'execute': main_window,
                    'isVisible': scope_xml,
                    'minimumVersion': '2020'
                }
            ]
        }
    ]
