"""
Script Name: ultragrid
Script Version: 0.0.2
Flame Version: 2023.2
Written by: John Geehreng
Creation Date: 05.30.24
Update Date: 06.10.24

Script Type: Main Menu

Description:

    A simple script for starting and stopping UltraGrid quickly.

Menus:

    Flame Main Menu -> UltraGrid -> UltraGrid Setup, UltraGrid Start, UltraGrid Stop

To install:

    Copy script into /opt/Autodesk/shared/python/ultragrid

Updates:

    v0.0.2 06.10.24
        Minor code cleanup and added some error windows and console messages.

    v0.0.1 05.30.24
        Inception

"""

#-------------------------------------#
# Imports

import os
import subprocess
import flame

from pyflame_lib_ultragrid import *

#-------------------------------------#
# Setup Window Script

SCRIPT_NAME = 'UltraGrid'
SCRIPT_VERSION = 'v0.0.2'
SCRIPT_PATH = '/opt/Autodesk/shared/python/ultragrid'

class UltraGrid():

    def __init__(self, selection) -> None:

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} {SCRIPT_VERSION}', '<' * 10, '\n')

        # Check script path, if path is incorrect, stop script.
        if not self.check_script_path():
            return

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Open main window
        self.main_window()

    def check_script_path(self) -> bool:
        """
        Check if script is installed in the correct location.

        Returns:
            bool: Returns True if script is installed in correct location, False if not.
        """

        if os.path.dirname(os.path.abspath(__file__)) != SCRIPT_PATH:
            PyFlameMessageWindow(
                message=f'Script path is incorrect. Please reinstall script.<br><br>Script path should be:<br><br>{SCRIPT_PATH}',
                script_name=SCRIPT_NAME,
                type=MessageType.ERROR,
                )
            return False
        return True

    def load_config(self) -> PyFlameConfig:
        """
        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
            PyFlameConfig: PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            script_name=SCRIPT_NAME,
            script_path=SCRIPT_PATH,
            config_values={
                'sender_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'send_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv  -t ndi:url=XXX.XXX.XX.XX:XXXX -c libavcodec:codec=H.264:bitrate=40000000 --audio-filter controlport_stats -s AESEBU --audio-capture-format channels=2 --audio-codec Opus -f rs:200:220 -P 5004 --control-port XXXX XXX.XXX.XXX.XX --param errors-fatal',
                'receiver_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'receive_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv -d vulkan_sdl2:fs -N -r coreaudio',
                },
            )

        return settings

    def main_window(self) -> None:
        """
        Create main window.
        """

        def save_config() -> None:
            """
            Save settings to config file and close window.
            """

            self.settings.save_config(
                script_name=SCRIPT_NAME,
                script_path=SCRIPT_PATH,
                config_values={
                    'sender_ssh_setting': self.sender_ip_entry.text(),
                    'send_cmd_setting': self.sender_cmd_entry.text(),
                    'receiver_ssh_setting': self.receiver_ip_entry.text(),
                    'receive_cmd_setting': self.receiver_cmd_entry.text(),
                    }
                )

            self.window.close()

        #------------------------------------#
        # Window Elements

        # Window
        self.window = PyFlameWindow(
            width=1200,
            height=280,
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            return_pressed=save_config,
            )

        # Labels
        self.sender_ip_label = PyFlameLabel(
            text='SSH Sender info',
            style=Style.UNDERLINE,
            )
        self.sender_cmd_label = PyFlameLabel(
            text='Sender Command',
            style=Style.UNDERLINE,
            )
        self.spacer1_label = PyFlameLabel(
            text='',
            )
        self.receiver_ip_label = PyFlameLabel(
            text='SSH Reciever Info',
            style=Style.UNDERLINE,
            )
        self.receiver_cmd_label = PyFlameLabel(
            text='Reciever Command',
            style=Style.UNDERLINE,
            )
        self.spacer_label = PyFlameLabel(
            text='',
            )

        # Entry
        ssh_entry_width = 300
        command_entry_width = 1180
        self.sender_ip_entry = PyFlameLineEdit(
            text=self.settings.sender_ssh_setting,
            width=ssh_entry_width,
            )
        self.sender_cmd_entry = PyFlameLineEdit(
            text=self.settings.send_cmd_setting,
            width=command_entry_width,
            )
        self.receiver_ip_entry = PyFlameLineEdit(
            text=self.settings.receiver_ssh_setting,
            width=ssh_entry_width,
            )
        self.receiver_cmd_entry = PyFlameLineEdit(
            text=self.settings.receive_cmd_setting,
            width=command_entry_width,
            )

        # Buttons
        self.save_button = PyFlameButton(
            text='Save',
            connect=save_config,
            color=Color.BLUE,
            )
        self.cancel_button = PyFlameButton(
            text='Cancel',
            connect=self.window.close,
            )


        #------------------------------------#
        # Window Layout

        grid_layout = PyFlameGridLayout()

        grid_layout.addWidget(self.sender_ip_label, 0, 0)
        grid_layout.addWidget(self.sender_ip_entry, 0, 1)

        grid_layout.addWidget(self.sender_cmd_label, 1, 0)
        grid_layout.addWidget(self.sender_cmd_entry, 1, 1)

        grid_layout.addWidget(self.spacer1_label, 2, 0)

        grid_layout.addWidget(self.receiver_ip_label, 3, 0)
        grid_layout.addWidget(self.receiver_ip_entry, 3, 1)

        grid_layout.addWidget(self.receiver_cmd_label, 4, 0)
        grid_layout.addWidget(self.receiver_cmd_entry, 4, 1)

        grid_layout.addWidget(self.spacer_label, 5, 0)

        grid_layout.addWidget(self.cancel_button, 6, 0)
        grid_layout.addWidget(self.save_button, 6, 1, QtCore.Qt.AlignRight)

        # Add layout to window
        self.window.add_layout(grid_layout)

        self.window.show()

#-------------------------------------#
# UG Start

class UltraGridStart():

    def __init__(self, selection) -> None:

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} Start {SCRIPT_VERSION}', '<' * 10, '\n')

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Start UltraGrid
        self.start_ultra_grid()


    def load_config(self) -> PyFlameConfig:
        """
        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
            PyFlameConfig: PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            script_name=SCRIPT_NAME,
            script_path=SCRIPT_PATH,
            config_values={
                'sender_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'send_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv  -t ndi:url=XXX.XXX.XX.XXX:XXXX -c libavcodec:codec=H.264:bitrate=40000000 --audio-filter controlport_stats -s AESEBU --audio-capture-format channels=2 --audio-codec Opus -f rs:200:220 -P 5004 --control-port 8888 XXX.XXX.XXX.XX --param errors-fatal',
                'receiver_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'receive_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv -d vulkan_sdl2:fs -N -r coreaudio',
                },
            )

        return settings

    def start_ultra_grid(self):
        self.load_config()
        print("Start UG...")

        # Execute the send command on a remote machine via SSH using SSH keys.
        ssh_command = f"{self.settings.sender_ssh_setting} {self.settings.send_cmd_setting}"
        print (f'Sender Command: {ssh_command}')
        subprocess.run(['gnome-terminal', '--', 'bash', '-c', ssh_command])

        # Execute the recieve command on a remote machine via SSH using SSH keys.
        ssh_command = f"{self.settings.receiver_ssh_setting} {self.settings.receive_cmd_setting}"
        print (f'Receiver Command: {ssh_command}')
        subprocess.run(['gnome-terminal', '--', 'bash', '-c', ssh_command])

        flame.messages.show_in_console('UltraGrid Start commands sent. Check new terminal windows if you have any issues.', 'info',10)

#-------------------------------------#
# UG Stop

class UltraGridStop():

    def __init__(self, selection) -> None:

        print('\n')
        print('>' * 10, f'{SCRIPT_NAME} STOP {SCRIPT_VERSION}', '<' * 10, '\n')

        # Create/Load config file settings.
        self.settings = self.load_config()

        # Stop UltraGrid
        self.stop_ultra_grid()


    def load_config(self) -> PyFlameConfig:
        """
        Create/Load config values from config file.
        If config file does not exist, create it using config_values as default values otherwise load config values from file.
        Default values should be set in the config_values dictionary.

        Returns:
            PyFlameConfig: PyFlameConfig object with config values.
        """

        settings = PyFlameConfig(
            script_name=SCRIPT_NAME,
            script_path=SCRIPT_PATH,
            config_values={
                'sender_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'send_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv  -t ndi:url=192.168.76.42:5961 -c libavcodec:codec=H.264:bitrate=40000000 --audio-filter controlport_stats -s AESEBU --audio-capture-format channels=2 --audio-codec Opus -f rs:200:220 -P 5004 --control-port 8888 100.123.222.41 --param errors-fatal',
                'receiver_ssh_setting': 'ssh user@XXX.XXX.XX.XXX',
                'receive_cmd_setting': '/Applications/uv-qt.app/Contents/MacOS/uv -d vulkan_sdl2:fs -N -r coreaudio',
                },
            )

        return settings

    def stop_ultra_grid(self):
        print("Stop UG...")

        def ssh_command(host, username, command):
            """Execute a command on a remote machine via SSH using SSH keys."""
            ssh_command = f"ssh {username}@{host} '{command}'"
            print (f'ssh comand: {ssh_command}')
            result = subprocess.run(ssh_command, shell=True, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                flame.messages.show_in_dialog(
                    title = f"Cannot Stop UltraGrid on {host}",
                    message = "Please check commands and ssh keys.",
                    type = "error",
                    buttons = ["Ok"])
            return result.stdout.strip()

        def stop_ultragrid_remote(host, username):
            # Command to find and kill the UltraGrid process
            find_pid_command = "pgrep uv-real"
            kill_command_template = "kill {}"

            # Find the PID of the UltraGrid process
            pid = ssh_command(host, username, find_pid_command)

            if pid:
                # Construct the kill command with the found PID
                kill_command = kill_command_template.format(pid)
                ssh_command(host, username, kill_command)
                print(f"UltraGrid process with PID {pid} on {host} has been terminated.")
            else:
                print("UltraGrid process not found on remote machine.")

        # Get the sender host and username from settings for the sender
        ssh_info = self.settings.sender_ssh_setting
        ssh_info = ssh_info.replace('ssh ', '')
        username, host = ssh_info.split('@')

        # Stop the UltraGrid process on the remote machine
        stop_ultragrid_remote(host, username)

        # Get the sender host and username from settings for the receiver
        ssh_info = self.settings.receiver_ssh_setting
        ssh_info = ssh_info.replace('ssh ', '')
        username, host = ssh_info.split('@')

        # Stop the UltraGrid process on the remote machine
        stop_ultragrid_remote(host, username)

        flame.messages.show_in_console('UltraGrid Stop commands sent. Check terminal windows if you have any issues.', 'info',10)

#-------------------------------------#
# Flame Menu

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'UltraGrid',
            'hierarchy': [],
            'actions': [
               {
                    'name': 'UltraGrid Setup',
                    'execute': UltraGrid,
                    'minimumVersion': '2023.2'
               },
               {
                    'name': 'UltraGrid Start',
                    'execute': UltraGridStart,
                    'minimumVersion': '2023.2'
               },
               {
                    'name': 'UltraGrid Stop',
                    'execute': UltraGridStop,
                    'minimumVersion': '2023.2'
               }
           ]
        }
    ]
