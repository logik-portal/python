"""
Script Name: BB Archiver UI
Script Version: 1.8.0
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 11.17.22
Update Date: 02.05.24

Script Type: Main Menu

Description:

    This is a simple UI for Background Archiving using Backburner Manager. The script only works with the local flame, it does not support remote project archiving.

To install:

    Copy script into /opt/Autodesk/shared/python/bb_archiver_ui

Updates:
02.05.24 - v1.8 - Prep for Distribution
10.14.23 - v1.7 - Turned off emailing
05.22.23 - v1.4 - Fixed typo
04.18.23 - v1.2 - Fixed issue for 2024 and flame_version = 2024, not 2024.0
12.02.22 - v1.0 - Allow Current Project to show up in list and add Warnings.
11.30.22 - v0.91- Added pop-ups dialogues for First Time Warning, Path Errors, and Size Estimates. Removed 'Format Archive' Button in favor of having the BB Archive button do it automatically.
11.28.22 - v0.9 - Added Size Estimate button. Fixed Archive Parameters. Minor printing cleanup.
11.23.22 - v0.8 - Fixed Archive Parameters.
11.21.22 - v0.7 - Added more segment size options. Saves all setting in the config.xml.
"""

from pyflame_lib_bb_archiver_ui import *
try:
    from PySide6 import QtWidgets
except ImportError:
    from PySide2 import QtWidgets

import xml.etree.ElementTree as ET
import os
import flame
import re
import subprocess
import platform

SCRIPT_NAME = 'BB Archiving UI'
SCRIPT_PATH = '/opt/Autodesk/shared/python/bb_archiver_ui'
SCRIPT_VERSION = 'v1.8'

#-------------------------------------#
# Main Script

class bb_archiver_ui(object):

    def __init__(self, selection):

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        # Paths

        self.config_path = os.path.join(SCRIPT_PATH, 'config')
        self.config_xml = os.path.join(self.config_path, 'config.xml')

        # Load config file

        self.config()

        # Open main window

        self.main_window()

    def config(self):

        def get_config_values():

            xml_tree = ET.parse(self.config_xml)
            root = xml_tree.getroot()

            # Get Settings from config XML

            for setting in root.iter('bb_archiver_ui_settings'):
                self.bbm = setting.find('bbm').text
                self.job_folder_path = setting.find('job_folder_path').text
                self.archive_path = setting.find('archive_path').text
                self.project_selection = setting.find('project_selection').text
                self.segment_size_setting = setting.find('segment_size').text
                self.source_media = setting.find('source_media').text
                self.cache_uncached = setting.find('cache_uncached').text
                self.maps = setting.find('maps').text
                self.renders = setting.find('renders').text
                self.unused = setting.find('unused').text
                self.otoc = setting.find('otoc').text


            pyflame.message_print(SCRIPT_NAME, 'Config loaded.')

        def create_config_file():

            if not os.path.isdir(self.config_path):
                try:
                    os.makedirs(self.config_path)
                except:
                    PyFlameMessageWindow(title=f'{SCRIPT_NAME}: Error', message=f'Unable to create folder: {self.config_path}<br>Check folder permissions',type=MessageType.ERROR)

            if not os.path.isfile(self.config_xml):
                pyflame.message_print(SCRIPT_NAME, 'Config file does not exist. Creating new config file.')
                flame.messages.show_in_dialog(
                    title = "One-Time Warning",
                    message = "Please configure Backburner Manager and Archive Path in the Setup Window before archiving.",
                    type = "warning",
                    buttons = ["Ok"])#,
                    # cancel_button = "Cancel")

                config = '''
<settings>
    <bb_archiver_ui_settings>
        <bbm>localhost</bbm>
        <job_folder_path>/var/tmp</job_folder_path>
        <archive_path>/var/tmp/&lt;project_name&gt;/&lt;machine_name&gt;</archive_path>
        <project_selection>temp</project_selection>
        <segment_size>50GB</segment_size>
        <source_media>False</source_media>
        <cache_uncached>False</cache_uncached>
        <maps>False</maps>
        <renders>False</renders>
        <unused>False</unused>
        <otoc>False</otoc>

    </bb_archiver_ui_settings>
</settings>'''

                with open(self.config_xml, 'a') as config_file:
                    config_file.write(config)
                    config_file.close()

        if os.path.isfile(self.config_xml):
            get_config_values()
        else:
            create_config_file()
            if os.path.isfile(self.config_xml):
                get_config_values()

    def main_window(self):

        def setup_window():

            self.window.hide()

            def save_config():

                # Save settings to config file

                xml_tree = ET.parse(self.config_xml)
                root = xml_tree.getroot()

                bbm = root.find('.//bbm')
                bbm.text = self.bbm_line_edit.text()

                jobs_folder_path = root.find('.//job_folder_path')
                jobs_folder_path.text = self.job_folder_line_edit.text()

                archive_path = root.find('.//archive_path')
                archive_path.text = self.archive_path_line_edit.text()

                xml_tree.write(self.config_xml)

                pyflame.message_print(SCRIPT_NAME, 'Config saved.')

                self.config()
                self.prefs_window.close()
                self.main_window()


            def cancel_setup():

                self.prefs_window.close()
                self.main_window()

            # grid_layout = QtWidgets.QGridLayout()
            self.prefs_window = PyFlameWindow(
            width=1200,
            height=270,
            title=f'Backburner Archiving Setup <small>{SCRIPT_VERSION}'
            )
            #FlameWindow("Backburner Archiving Setup", grid_layout, 1100, 270)

            def job_folder_browse():
                self.prefs_window.hide()
                flame.browser.show(
                    title = "Select Jobs Folder",
                    select_directory = True,
                    default_path = "/")
                browse_job_folder_path = str(flame.browser.selection)[2:-2]
                print('browse_job_folder_path: ', browse_job_folder_path)
                self.job_folder_line_edit.setText(browse_job_folder_path)
                self.prefs_window.show()

            def archive_path_browse():
                self.prefs_window.hide()
                flame.browser.show(
                    title = "Select Archive Path",
                    select_directory = True,
                    default_path = "/")
                browse_archive_path = str(flame.browser.selection)[2:-2]
                print('browse_archive_path: ', browse_archive_path)
                self.archive_path_line_edit.setText(browse_archive_path)
                self.prefs_window.show()

            # Labels

            self.bbm_label = PyFlameLabel(text='Backburner Manager', style=Style.UNDERLINE)
            self.job_folder_path_label = PyFlameLabel(text='Path to Jobs', style=Style.UNDERLINE)
            self.archive_path_label = PyFlameLabel(text='Archive Path', style=Style.UNDERLINE)

            # Line Edits
            line_edit_width = 600
            self.bbm_line_edit = PyFlameLineEdit(text=self.bbm)
            self.job_folder_line_edit = PyFlameLineEdit(text=self.job_folder_path, width=line_edit_width)
            self.archive_path_line_edit = PyFlameLineEdit(text=self.archive_path, width=line_edit_width)

            #Token Buttons

            self.archive_path_token_dict = {'Project Name': '<project_name>','Machine Name': '<machine_name>'}
            self.archive_path_token_push_button = PyFlameTokenPushButton(text='Add Token', token_dict=self.archive_path_token_dict, token_dest=self.archive_path_line_edit)

            # Buttons
            self.job_folder_browse_btn = PyFlameButton(text='Browse',  connect=job_folder_browse) # FlameButton('Browse', job_folder_browse)
            self.archive_path_browse_btn = PyFlameButton(text='Browse',  connect=archive_path_browse) # FlameButton('Browse', archive_path_browse)
            self.save_btn = PyFlameButton(text='Save',  connect=save_config, color=Color.BLUE) # FlameButton('Save', save_config,button_color='blue')
            self.setup_cancel_btn = PyFlameButton(text='Cancel',  connect=cancel_setup, color=Color.RED) # FlameButton('Cancel', cancel_setup,button_color='red')

            #------------------------------------#

            # Setup Window Layout

            grid_layout = QtWidgets.QGridLayout()
            grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
            grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
            try:
                grid_layout.setMargin(pyflame.gui_resize(10))
            except:
                grid_layout_margin = pyflame.gui_resize(10)
                grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

            grid_layout.addWidget(self.bbm_label, 1, 0)
            grid_layout.addWidget(self.bbm_line_edit, 1, 1)

            grid_layout.addWidget(self.job_folder_path_label, 2, 0)
            grid_layout.addWidget(self.job_folder_line_edit, 2, 1)
            grid_layout.addWidget(self.job_folder_browse_btn, 2, 2)

            grid_layout.addWidget(self.archive_path_label, 3, 0)
            grid_layout.addWidget(self.archive_path_line_edit, 3, 1)
            grid_layout.addWidget(self.archive_path_browse_btn, 3, 2)
            grid_layout.addWidget(self.archive_path_token_push_button, 3, 3)

            grid_layout.addWidget(self.setup_cancel_btn, 6, 0)
            grid_layout.addWidget(self.save_btn, 6, 3)

            # Add layout to window
            self.prefs_window.add_layout(grid_layout)
            # self.prefs_window.setLayout(grid_layout)

            self.prefs_window.show()

            return self.prefs_window

        project_name = flame.project.current_project.name
        project_nickname = flame.project.current_project.nickname
        print ('Backburner Manager: ',self.bbm)
        print ('Job Folders: ',self.job_folder_path)
        print ('Archive Path: ',self.archive_path)

        def get_local_flame_projects():
            """Get all flame projets from /opt/Autodesk/io/bin/flame_archive -l

            Returns:
                list: This is a list of the flame projects that exist on the workstation
            """
            project_list = []
            proc = subprocess.Popen(['/opt/Autodesk/io/bin/flame_archive', '-l'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = proc.communicate()[0]

            if isinstance(output, bytes):
                output = output.decode('utf-8')

            proj_trip = False
            for proj in output.split('\n'):
                proj = re.sub(r'^\s+', '', proj)

                if re.search(r'(?i)stopping managed threads\.', proj):
                    break

                if re.search(r'(?i)^projects:', proj):
                    proj_trip = True
                    continue

                if not proj_trip:
                    continue

                project_list.append(proj)

            return project_list

        project_list = get_local_flame_projects()

        try:
            project_list.remove(".DS_Store")
        except:
            pass
            print ("project_list: ", project_list)

        def format_flame_archive():

            # Get Flame Version
            flame_version = flame.get_version()

            project_name = self.project_menu_push_button.text()
            segment_size = self.segment_size_menu_push_button.text()
            machine_name = platform.node().split('.')[0]
            resolved_path = self.archive_path.replace('<project_name>',project_name)
            resolved_path = resolved_path.replace('<machine_name>',machine_name)

            # Remove the last character if it's a '/'
            if resolved_path[-1] == '/':
                resolved_path = resolved_path[:-1]
            print ('resolved_path: ', resolved_path)
            format_archive_command = "/opt/Autodesk/io/" + str(flame_version) + "/bin/flame_archive  -f -F " + resolved_path + "/" + project_name + "_Archive -i " + segment_size
            print ('format_archive_command: ' , format_archive_command)
            archive_file = resolved_path + "/" + project_name + "_Archive"

            if os.path.isfile(archive_file):
                flame.messages.show_in_console('Archive exists for ' + project_name + ". You're ready to do a BB Archive!", 'warning',10)
                return

            command = format_archive_command.split()
            rc = subprocess.call(command)
            if rc == 0:
                flame.messages.show_in_console('Archive Formatted for ' + project_name + ". You're ready to do a BB Archive!", 'info',10)
            else:
                self.window.hide()
                flame.messages.show_in_dialog(
                    title = "Error",
                    message = "Could not format archive. Please check Archive Path.",
                    type = "error",
                    buttons = ["Ok"])
                self.window.show()

        def get_size_estimate():
            # Change cursor to busy
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.BusyCursor)

            # Get Flame Version and other variables
            flame_version = flame.get_version()

            project_name = self.project_menu_push_button.text()
            current_project_name = flame.project.current_project.name
            current_project_nickname = flame.project.current_project.nickname

            if project_name == current_project_name or project_name == current_project_nickname:
                self.window.hide()
                warning_dialogue = flame.messages.show_in_dialog(
                    title = "Warning",
                    message = "Cannot get size estimate for current project.",
                    type = "warning",
                    buttons = ["Ok"],
                    cancel_button = "Cancel")
                if warning_dialogue == "Ok":
                    self.window.show()
                    return
                else:
                    self.window.show()
                    return

            flame.messages.show_in_console('Getting Size Estimate for ' + project_name + '...', 'info',20)

            size_estimate_command = "/opt/Autodesk/io/" + str(flame_version) + "/bin/flame_archive -a -e --omit sources,renders,maps,unused -k -P " + project_name

            # Change the commands depending on what buttons were pressed:
            if self.source_media_cache_pb.isChecked() and self.maps_and_ml_cache_pb.isChecked() and self.timeline_fx_renders_pb.isChecked() and self.unused_versions_pb.isChecked() and self.cache_uncached_media_pb.isChecked():
                size_estimate_command = size_estimate_command.replace(" --omit sources,renders,maps,unused -k -P"," -P")
            if self.source_media_cache_pb.isChecked():
                size_estimate_command = size_estimate_command.replace("sources,","")
                self.source_media=True
            if self.cache_uncached_media_pb.isChecked():
                size_estimate_command = size_estimate_command.replace(" -k -P "," -P ")
            if self.maps_and_ml_cache_pb.isChecked():
                size_estimate_command = size_estimate_command.replace("maps,","")
            if self.timeline_fx_renders_pb.isChecked():
                size_estimate_command = size_estimate_command.replace("renders,","")
            if self.unused_versions_pb.isChecked():
                size_estimate_command = size_estimate_command.replace(",unused","")
            if self.otoc_pb.isChecked():
                size_estimate_command = size_estimate_command.replace(" -P "," -T -P ")

            print ('size_estimate_command: ', size_estimate_command)
            command = size_estimate_command.split()
            proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = proc.communicate()[0]

            if isinstance(output, bytes):
                output = output.decode('utf-8')

            proj_trip = False
            for proj in output.split('\n'):
                proj = re.sub(r'^\s+', '', proj)

                if re.search(r'(?i)stopping managed threads\.', proj):
                    break

                if re.search('B', proj):
                    proj_trip = True
                    print ('Size Estimate is: ', proj)
                    flame.messages.show_in_console('Size Estimate for ' + project_name + ' is ' + proj + '.', 'info',15)
                    message = 'Size Estimate for ' + project_name + ' is ' + proj + '.'
                    continue

                if not proj_trip:
                    continue

            # Restore cursor
            QtWidgets.QApplication.restoreOverrideCursor()
            self.window.hide()
            flame.messages.show_in_dialog(
               title = "Size Estimate",
               message = message,
               type = "info",
               buttons = ["Ok"],
               cancel_button = "Cancel")
            self.window.show()

        def send_archive_job_to_bbm():

            def save_main_config():

                # Save settings to config file

                xml_tree = ET.parse(self.config_xml)
                root = xml_tree.getroot()

                project_selection = root.find('.//project_selection')
                project_selection.text = self.project_menu_push_button.text()

                seg_size = root.find('.//segment_size')
                seg_size.text = self.segment_size_menu_push_button.text()

                source_media = root.find('.//source_media')
                if self.source_media_cache_pb.isChecked():
                    source_media.text = 'True'
                else:
                    source_media.text = 'False'

                cache_uncached = root.find('.//cache_uncached')
                if self.cache_uncached_media_pb.isChecked():
                    cache_uncached.text = 'True'
                else:
                    cache_uncached.text = 'False'

                maps = root.find('.//maps')
                if self.maps_and_ml_cache_pb.isChecked():
                    maps.text = 'True'
                else:
                    maps.text = 'False'

                renders = root.find('.//renders')
                if self.timeline_fx_renders_pb.isChecked():
                    renders.text = 'True'
                else:
                    renders.text = 'False'

                unused = root.find('.//unused')
                if self.unused_versions_pb.isChecked():
                    unused.text = 'True'
                else:
                    unused.text = 'False'

                otoc = root.find('.//otoc')
                if self.otoc_pb.isChecked():
                    otoc.text = 'True'
                else:
                    otoc.text = 'False'

                xml_tree.write(self.config_xml)

                pyflame.message_print(SCRIPT_NAME, 'Config saved.')

                self.config()


            # Get Location, Server, Email Server, and Backburner Manager
            if platform.system() == 'Darwin':
                server = platform.node()
            else:
                server = platform.node().split('.')[0]
            machine_name = platform.node().split('.')[0]

            # Get Flame Version and other variables
            flame_version = flame.get_version()

            project_name = self.project_menu_push_button.text()
            machine_name = platform.node().split('.')[0]
            current_project_name = flame.project.current_project.name
            current_project_nickname = flame.project.current_project.nickname
            resolved_path = self.archive_path.replace('<project_name>',project_name)
            resolved_path = resolved_path.replace('<machine_name>',machine_name)

            # Remove the last character if it's a '/'
            if resolved_path[-1] == '/':
                resolved_path = resolved_path[:-1]
            print ('resolved_path: ', resolved_path)

            save_main_config()

            if project_name == current_project_name or project_name == current_project_nickname:
                self.window.hide()
                warning_dialogue = flame.messages.show_in_dialog(
                    title = "Warning",
                    message = "Current project can not be archived while it is open. You will need to exit Flame or switch projects in order to continue.",
                    type = "warning",
                    buttons = ["Continue"],
                    cancel_button = "Cancel")
                if warning_dialogue == "Continue":
                    self.window.show()
                    pass
                else:
                    self.window.show()
                    return

            archive_command = "/opt/Autodesk/io/" + str(flame_version) + "/bin/flame_archive -a -g --omit sources,renders,maps,unused -k -P " + project_name + " -F " + resolved_path + "/" + project_name + "_Archive"
            archive_file = resolved_path + "/" + project_name + "_Archive"

            if os.path.isfile(archive_file):
                pass
            else:
                format_flame_archive()

            if os.path.isfile(archive_file):
                pass
            else:
                return

            # Change the commands depending on what buttons were pressed:
            if self.source_media_cache_pb.isChecked() and self.maps_and_ml_cache_pb.isChecked() and self.timeline_fx_renders_pb.isChecked() and self.unused_versions_pb.isChecked() and self.cache_uncached_media_pb.isChecked():
                archive_command = archive_command.replace(" --omit sources,renders,maps,unused -k -P"," -P")
            if self.source_media_cache_pb.isChecked():
                archive_command = archive_command.replace("sources,","")
                self.source_media=True
            if self.cache_uncached_media_pb.isChecked():
                archive_command = archive_command.replace(" -k -P "," -P ")
            if self.maps_and_ml_cache_pb.isChecked():
                archive_command = archive_command.replace("maps,","")
            if self.timeline_fx_renders_pb.isChecked():
                archive_command = archive_command.replace("renders,","")
            if self.unused_versions_pb.isChecked():
                archive_command = archive_command.replace(",unused","")
            if self.otoc_pb.isChecked():
                archive_command = archive_command.replace(" -P "," -T -P ")

            qt_app_instance = QtWidgets.QApplication.instance()
            qt_app_instance.clipboard().setText(archive_command)
            print ('archive_command: ' , archive_command)
            archive_description = "Archiving " + project_name + " from " + machine_name + "."
            print ('archive_description: ' , archive_description)

            # Build BBM Command
            archive_bbm_cmd  = ("/opt/Autodesk/backburner/cmdjob"
            + ' -jobName: "Archive - ' + project_name + " from " + machine_name + '"'
            + ' -description: ' + '"' 'Terminal Command: ' '\n' + archive_command + '\n' + '"'
            + ' -manager: ' + '"' + self.bbm + '"'
            + ' -servers: ' + '"' + server + '"'
            + ' -priority: 90 '
            + ' -delete: 14 '
            + ' -timeout: 500 '
            # + '  -emailFrom: bbm@uppercutedit.com -emailTo: ' + email_to + ' -emailServer: ' + email_server + ' -emailCompletion '
            + archive_command)

            print ("*" * 40)
            print("archive command: " + archive_bbm_cmd)
            print("archive readout:")
            print ("*" * 80)

            # Send the Command to bbm
            archive_proc = subprocess.Popen(archive_bbm_cmd,
                                            shell=True,
                                            stdin=subprocess.PIPE,
                                            stdout=subprocess.PIPE,
            )
            while True:
                line = archive_proc.stdout.readline()
                if not line:
                    break
                print (line)
            location = None
            server = None
            bbm = None

            flame.messages.show_in_console("Archive job sent to Backburner. Please confirm in Backburner Monitor.", 'info',10)

        def close_window():
                print('\n')
                print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')
                self.window.close()

        def cache_toggle():
                # Disables UI elements when button is pressed
                if self.source_media_cache_pb.isChecked():
                    self.cache_uncached_media_pb.setEnabled(True)
                else:
                    self.cache_uncached_media_pb.setEnabled(False)
                    self.cache_uncached_media_pb.setChecked(False)

        # Window and UI Below

        self.window = self.prefs_window = PyFlameWindow(
            width=620,
            height=320,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}'
            )

        # Push Button Menus
        previous_project = project_list[0]
        for i in [i for i, x in enumerate(project_list) if x == self.project_selection]:
            previous_project = project_list[int(i)]
            print ("previous_project: ", previous_project)
        self.project_menu_push_button = PyFlamePushButtonMenu(text=previous_project, menu_options=project_list, width=400, max_width=500)
        self.project = self.project_menu_push_button.text()

        segment_size_list = ['4.7GB','25GB','50GB','100GB','300GB','400GB','460GB','600GB','800GB','930GB','1500GB','1GB']
        for i in [i for i, x in enumerate(segment_size_list) if x == self.segment_size_setting]:
            last_segment_size = segment_size_list[int(i)]
            print ("previous segment size: ", last_segment_size)
        self.segment_size_menu_push_button = PyFlamePushButtonMenu(text=last_segment_size, menu_options=segment_size_list, width=150, max_width=150)
        segment_size = self.segment_size_menu_push_button.text()

        # Labels
        self.project_label = PyFlameLabel(text='Flame Project', style=Style.UNDERLINE)
        self.segment_size_label = PyFlameLabel(text='Segment Size', style=Style.UNDERLINE)
        self.archive_options_label = PyFlameLabel(text='Archive Options', style=Style.UNDERLINE)

        BUTTON_WIDTH = 205

        # Buttons
        self.format_archive_btn = PyFlameButton(text='Format Archive',connect=format_flame_archive, color=Color.BLUE)
        self.bg_archive_btn = PyFlameButton(text='BB Archive', connect=send_archive_job_to_bbm, color=Color.BLUE, width=BUTTON_WIDTH)
        self.cancel_btn = PyFlameButton(text='Close', connect=close_window, width=BUTTON_WIDTH)
        self.setup_btn = PyFlameButton(text='Setup', connect=setup_window)
        self.size_estimate_btn = PyFlameButton(text='Size Estimate', connect=get_size_estimate, width=BUTTON_WIDTH)

        # Push Buttons
        self.source_media_cache_pb = PyFlamePushButton(text='Include Source Media Cache', button_checked=False, connect=cache_toggle, width=BUTTON_WIDTH)
        self.maps_and_ml_cache_pb = PyFlamePushButton(text='Include Maps and ML Cache', button_checked=False, width=BUTTON_WIDTH)
        self.timeline_fx_renders_pb = PyFlamePushButton(text='Include Timeline Renders', button_checked=False, width=BUTTON_WIDTH)
        self.unused_versions_pb = PyFlamePushButton(text='Include Unused Versions', button_checked=False, width=BUTTON_WIDTH)
        self.cache_uncached_media_pb = PyFlamePushButton(text='Cache Uncached Media', button_checked=False, width=BUTTON_WIDTH)
        self.cache_uncached_media_pb.setEnabled(False)
        self.otoc_pb = PyFlamePushButton(text='Generate TOC', button_checked=False, width=BUTTON_WIDTH)

        if self.source_media == 'True':
            self.source_media_cache_pb.setChecked(True)
        if self.maps == 'True':
            self.maps_and_ml_cache_pb.setChecked(True)
        if self.renders == 'True':
            self.timeline_fx_renders_pb.setChecked(True)
        if self.unused == 'True':
            self.unused_versions_pb.setChecked(True)
        if self.cache_uncached == 'True':
            self.cache_uncached_media_pb.setChecked(True)
        if self.otoc == 'True':
            self.otoc_pb.setChecked(True)

        cache_toggle()

        #------------------------------------#
        # Window Layout

        grid_layout = QtWidgets.QGridLayout()
        grid_layout.setVerticalSpacing(pyflame.gui_resize(5))
        grid_layout.setHorizontalSpacing(pyflame.gui_resize(5))
        try:
            grid_layout.setMargin(pyflame.gui_resize(10))
        except:
            grid_layout_margin = pyflame.gui_resize(10)
            grid_layout.setContentsMargins(grid_layout_margin, grid_layout_margin, grid_layout_margin, grid_layout_margin)

        grid_layout.addWidget(self.project_label, 0, 0)
        grid_layout.addWidget(self.project_menu_push_button, 0, 1)

        grid_layout.addWidget(self.segment_size_label, 1, 0)
        grid_layout.addWidget(self.segment_size_menu_push_button, 2, 0)

        grid_layout.addWidget(self.archive_options_label, 1, 1)
        grid_layout.addWidget(self.source_media_cache_pb, 2, 1)
        grid_layout.addWidget(self.cache_uncached_media_pb, 2, 2)
        grid_layout.addWidget(self.maps_and_ml_cache_pb, 3, 1)
        grid_layout.addWidget(self.timeline_fx_renders_pb, 4, 1)

        grid_layout.addWidget(self.unused_versions_pb, 5, 1)
        grid_layout.addWidget(self.otoc_pb, 4, 2)

        grid_layout.addWidget(self.size_estimate_btn, 5, 2)
        grid_layout.addWidget(self.setup_btn, 6, 0)
        grid_layout.addWidget(self.bg_archive_btn, 6, 1)
        grid_layout.addWidget(self.cancel_btn, 6, 2)

        # Add layout to window
        self.window.add_layout(grid_layout)

        self.window.show()

        return self.window

#-------------------------------------#
# Flame Menus

def get_main_menu_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'UC BB Archiving UI',
                    'separator': 'above',
                    'execute': bb_archiver_ui,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]