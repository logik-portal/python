"""
Script Name: fix premiere xmls
Script Version: 2.1.2
Flame Version: 2023.2
Written by: Ted Stanley, John Geehreng, and Michael Vaglienty
Creation Date: 03.03.21
Update Date: 02.13.25

Script Type: MediaHub

Description:

    Fix and/or Resize Adobe Premiere XML's.

Menus:

    MediaHub -> XML Prep -> Fix Premiere XML's

To install:

    Copy script into /opt/Autodesk/shared/python/fix_premiere_xmls

Updates:
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

import os
import flame
from pyflame_lib_fix_premiere_xmls import *

#-------------------------------------#
# Main Script

SCRIPT_NAME = "Fix Premiere XMLs"
SCRIPT_VERSION = 'v2.1.2'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

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

    def fixduration(self):
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        status = 1
        print("Fixing Durations...")
        for clip in clips:
            # clipname = clip.find('name').text
            # print("Clip " + str(status) + ": " + clipname)

            status += 1

            clipstart = int(clip.find('start').text)
            clipend = int(clip.find('end').text)
            clipin = int(clip.find('in').text)
            clipoutxml = int(clip.find('out').text)

            if (clipend - clipstart) == (clipoutxml - clipin): continue
            if (clipstart < 0) or (clipend < 0): continue

            # print("[Fixing Clip Out]")

            clipout = clip.find('out')
            clipout.text = str(clipin + (clipend - clipstart))

    def fixdurmismatch(self):
        clips = self.root.findall(".//sequence/media/video/*/clipitem")
        status = 1
        print("Fixing Duration Mismatches...")
        # print('\n')
        for clip in clips:
            clipname = clip.find('name').text
            # print("Clip " + str(status) + ": " + clipname)
            status += 1

            clipinint = int(clip.find('in').text)
            clipoutint = int(clip.find('out').text)
            if (clipoutint - clipinint) > clipoutint:
                clipoutint = (clipoutint - clipinint)
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
        proxy_x_res = int(self.proxy_x_res_slider.text())
        proxy_y_res = int(self.proxy_y_res_slider.text())
        full_x_res = int(self.full_x_res_slider.text())
        full_y_res = int(self.full_y_res_slider.text())
        proxy_aspect_ratio = proxy_x_res / proxy_y_res
        full_res_aspect_ratio = full_x_res / full_y_res

        if full_res_aspect_ratio >= proxy_aspect_ratio:
            scale_factor_calculation = str(round((proxy_x_res / full_x_res)*100,2))
        else:
            scale_factor_calculation = str(round((proxy_y_res / full_y_res)*100,2))
        self.scale_calculation_bg_label.setText(scale_factor_calculation)

    def scale_calc_toggle(self):

		# Disables UI elements when button is pressed

        if self.scale_calc_btn.isChecked():
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

        if self.xml_res_btn.isChecked():
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
            if self.scale_calc_btn.isChecked():
                 self.scale_factor = float(self.scale_calculation_bg_label.text())
            else:
                self.scale_factor = self.scale_factor_slider.get_value()
            
            # Calculate Offline vs Online
            if self.xml_res_btn.isChecked():
                self.online_x_factor = 1
                self.online_y_factor = 1
                output_width = self.input_sequence_width
                output_height = self.input_sequence_height
                print("Online Res:  ",f'{output_width}x{output_height}')
            else:
                self.online_x_res = int(self.online_x_res_slider.text())
                self.online_y_res = int(self.online_y_res_slider.text())
                offline_aspect_ratio = self.input_sequence_width / self.input_sequence_height
                online_aspect_ratio = self.online_x_res / self.online_y_res
                reverse_online_aspect_ratio = self.online_y_res / self.online_x_res
                # Resize the XML Output
                output_width = (self.root.find('.//width'))
                output_height = (self.root.find('.//height'))
                output_width.text = self.online_x_res_slider.text()
                output_height.text = self.online_y_res_slider.text()
                print("Online Res:  ",f'{output_width.text}x{output_height.text}')

                if online_aspect_ratio >= offline_aspect_ratio:
                    self.conform_scale_factor_calculation = str(round((self.online_x_res / self.input_sequence_width)*100,2))
                    self.online_x_factor = 1
                    self.online_y_factor = 1
                else:
                    self.conform_scale_factor_calculation = str(round((self.online_y_res / self.input_sequence_height)*100,2))
                    self.online_x_factor = round(max(1,(self.input_sequence_width / self.online_x_res_slider.get_value())) * reverse_online_aspect_ratio ,5)
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
            outname = str(item.path)[:-4]
            if self.scale_calc_btn.isChecked():
                outname = f'{outname}_scl_for_{self.full_x_res_slider.text()}x{self.full_y_res_slider.text()}'
            else:
                outname = f'{outname}_scl_of_{self.scale_percent}'
            
            if self.xml_res_btn.isChecked():
                outname = f'{outname}'
            else:
                outname = f'{outname}_in_{self.online_x_res_slider.text()}x{self.online_y_res_slider.text()}'
                outname = outname.replace(".", "_").replace("1080x1350", "4x5").replace("1080x1920", "9x16").replace("1280x1920", "2x3").replace("1920x1080", "16x9").replace("1080x1080", "1x1")

            # Remove 2 or more underscores
            regex = r'_{2,}'
            subst = "_"
            outname = re.sub(regex, subst, outname)

            #Fix Sanitize Names
            if self.sanatize_names_btn.isChecked():

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

            #Fix Stills Duration
            if self.fix_durations_btn.isChecked():
                #This function fixes any difference between the clip 'start to end' duration vs. the clip 'in to out' duration
                self.fixduration()
                #This function increases the clip duration if it's shorter that clip 'in to out'
                self.fixdurmismatch()
            else:
                print('Fix Durations was not checked')
            
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

        #------------------------------------#
        # Window Elements

        # Window
        self.window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=self.fix_xml,
            grid_layout_columns=5,
            grid_layout_rows=10,
            # grid_layout_adjust_column_widths={0: 20}
            )
        
        # Labels
        self.proxy_diffs_label = PyFlameLabel(
            text='Scale Footage Options:',
            # style=Style.UNDERLINE,
            # width=770
            )
        
        self.scale_factor_label = PyFlameLabel(
            text='Scale Multiplier',
            style=Style.UNDERLINE,
            )

        self.proxy_x_res_label = PyFlameLabel(
            text='Proxy X Res',
            style=Style.UNDERLINE,
            )
        self.proxy_y_res_label = PyFlameLabel(
            text='Proxy Y Res',
            style=Style.UNDERLINE,
            )
        self.full_x_res_label = PyFlameLabel(
            text='Footage X Res',
            style=Style.UNDERLINE,
            )
        self.full_y_res_label = PyFlameLabel(
            text='Footage Y Res',
            style=Style.UNDERLINE,
            )
        self.scale_calculation_label = PyFlameLabel(
            text='Scale Multiplier',
            style=Style.UNDERLINE,
            )
        self.scale_calculation_bg_label = PyFlameLabel(
            text='100.00',
            # style=Style.BACKGROUND,
            align=Align.CENTER
            )
        self.offline_diffs_label = PyFlameLabel(
            text='Resize Sequence Options:',
            # style=Style.UNDERLINE,
            # width=770
            )
        self.online_x_res_label = PyFlameLabel(
            text='Output X Res',
            style=Style.UNDERLINE,
            )
        self.online_y_res_label = PyFlameLabel(
            text='Output Y Res',
            style=Style.UNDERLINE,
            )
        self.other_options_label = PyFlameLabel(
            text='Other Options:',
            style=Style.UNDERLINE
            )
        self.blank_label_1 = PyFlameLabel(
            text='',
            style=Style.NORMAL
            )
        self.blank_label_2 = PyFlameLabel(
            text='',
            style=Style.NORMAL
            )
        self.blank_label_3 = PyFlameLabel(
            text='',
            style=Style.NORMAL
            )
        
        # Sliders

        self.proxy_x_res_slider = PyFlameSlider(float(self.settings.proxy_x_res), 720, 15000, False)
        self.proxy_y_res_slider = PyFlameSlider(float(self.settings.proxy_y_res), 480, 15000, False)
        self.full_x_res_slider = PyFlameSlider(float(self.settings.full_x_res), 720, 15000, False)
        self.full_y_res_slider = PyFlameSlider(float(self.settings.full_y_res), 480, 15000, False)

        self.online_x_res_slider = PyFlameSlider(float(self.settings.online_x_res), 720, 15000, False)
        self.online_y_res_slider = PyFlameSlider(float(self.settings.online_y_res), 480, 15000, False)

        self.sequence_x_slider = PyFlameSlider(1920, 0, 15000, False)
        self.sequence_y_slider = PyFlameSlider(1080, 0, 15000, False)
        self.scale_factor_slider = PyFlameSlider(100, 0, 300, True)

        # Slider Updates
        self.full_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.full_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_x_res_slider.textChanged.connect(self.update_auto_scale_multiplier)
        self.proxy_y_res_slider.textChanged.connect(self.update_auto_scale_multiplier)

        # Buttons
        self.ok_btn = PyFlameButton(
            text='Run',
            connect=self.fix_xml,
            color=Color.BLUE,
            )
        self.close_btn = PyFlameButton(
            text='Close',
            connect=self.window.close,
            )

        # Pushbuttons
        
        # Proxy vs Full Res Calculate Pushbutton
        self.scale_calc_btn = PyFlamePushButton('  Auto Calculate',
            button_checked=self.settings.scale_calc,
            connect=self.scale_calc_toggle
            )
        
        # Use XML Res PushButton
        self.xml_res_btn = PyFlamePushButton('  Use XML Res',
            button_checked=self.settings.xml_res,
            connect=self.xml_res_toggle
            )
        self.xml_res_btn.setToolTip('Enable to automatically detect the resolution of your xml.')

        # Fix Stills Pushbutton
        self.fix_durations_btn = PyFlamePushButton('  Fix Durations',
            button_checked=self.settings.fix_durations
            )
        self.fix_durations_btn.setToolTip('Enable to fix the duration of still frames. Typically graphic elements.')

        # Clean Names Pushbutton
        self.sanatize_names_btn = PyFlamePushButton('  Sanatize Names',
            button_checked=self.settings.sanatize_names
            )
        self.sanatize_names_btn.setToolTip('Enable to try to sanatize the names that will be imported into Flame.')

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

        self.window.grid_layout.addWidget(self.blank_label_1, 4, 0)

        self.window.grid_layout.addWidget(self.offline_diffs_label, 5, 2)

        self.window.grid_layout.addWidget(self.online_x_res_label, 6, 0)
        self.window.grid_layout.addWidget(self.online_x_res_slider, 6, 1)
        self.window.grid_layout.addWidget(self.online_y_res_label, 6, 2)
        self.window.grid_layout.addWidget(self.online_y_res_slider, 6, 3)
        self.window.grid_layout.addWidget(self.xml_res_btn, 6, 4)

        self.window.grid_layout.addWidget(self.blank_label_2, 7, 0)

        self.window.grid_layout.addWidget(self.other_options_label, 8, 0)
        self.window.grid_layout.addWidget(self.sanatize_names_btn, 8, 1)
        self.window.grid_layout.addWidget(self.fix_durations_btn, 8, 2)

        self.window.grid_layout.addWidget(self.blank_label_3, 9, 0)

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
                'proxy_x_res': self.proxy_x_res_slider.value(),
                'proxy_y_res': self.proxy_y_res_slider.value(),
                'full_x_res': self.full_x_res_slider.value(),
                'full_y_res': self.full_y_res_slider.value(),
                'online_x_res': self.online_x_res_slider.value(),
                'online_y_res': self.online_y_res_slider.value(),
                'scale_calc': self.scale_calc_btn.isChecked(),
                'xml_res': self.xml_res_btn.isChecked(),
                'sanatize_names': self.sanatize_names_btn.isChecked(),
                'fix_durations': self.fix_durations_btn.isChecked(),
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
                    'minimumVersion': '2023.2'
                }
            ]
        }
    ]
