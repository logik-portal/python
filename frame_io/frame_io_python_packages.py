'''
Script Name: frame io python packages
Script Version: 0.5
Flame Version: 2023.2
Written by: Michael Vaglienty (Customized by John Geehreng)
Creation Date: 06.05.23
Update Date: 01.25.24

Script Type: Flame Launch

Description:

    Check for installed Python Packages when launching Flame.

Menus:

    None


To install:

    Copy script into /opt/Autodesk/shared/python/uc_python_packages

    The following python modules will be installed into /opt/Autodesk/python/FLAME_VERSION/lib/python3.9/site_packages
    by the script when the script is run for the first time. These modeules will need to be installed for each new
    version of Flame, but only once per version. System password will be required to install the modules.

        charset_normalizer
        idna
        requests
        urllib3
        frameioclient
        xxhash

Updates:
    01.25.24 - v0.5 Prep for distribution
    12.12.23 - v.04 Start Flame 2025 Updates
'''

# ---------------------------------------- #
# Imports

import os
import flame
import subprocess
from subprocess import Popen, PIPE
from pyflame_lib_frame_io_python_packages import *

#-------------------------------------#
# Main Script

SCRIPT_NAME = 'FrameIO Python Packages'
SCRIPT_PATH = '/opt/Autodesk/shared/python/frame_io'
VERSION = 'v0.5'

class install_python_packages(object):

    def __init__(self, selection):

        # Check script path

        if os.path.dirname(os.path.abspath(__file__)) != SCRIPT_PATH:
            return PyFlameMessageWindow(title=f'{SCRIPT_NAME}: Error', message=f'Script path is incorrect. Please reinstall script.<br><br>Script path should be:<br><br>{SCRIPT_PATH}', type=MessageType.ERROR)

        # Get Flame version for python folder

        self.flame_version = flame.get_version()
        print('Flame Version:', self.flame_version, '\n')

        # Set python path

        self.python_path = pyflame.get_flame_python_packages_path()
        print('Python Packages Path:', self.python_path, '\n')

        # Get clean Flame version for export - no pr numbers

        self.clean_flame_version = pyflame.get_flame_version()

        # Required python packages

        self.required_python_packages = [ 
            'idna',
            'charset_normalizer',
            'requests',
            'frameioclient',
            'xxhash',
        ]
        # print ("Tring to install python package...")
        self.install_packages()

    def install_packages(self):

        def check_for_installed_packages():

            def packages_check():

                # Check for installed packages

                print('Checking for required python packages...\n')

                for package in self.required_python_packages:
                    if package not in os.listdir(self.python_path):
                        if f'{package}.py' not in os.listdir(self.python_path):
                            pyflame.message_print(SCRIPT_NAME, f'    {package}: Missing.')
                            return False
                    print(f'    {package}: Ok')
                print('\n')
                return True

            def install_packages():
                

                PyFlameMessageWindow(title=f'{SCRIPT_NAME}', message='The FrameIO scripts require some python modules to be installed.<br><br>Your system root password will be needed.<br><br>This may take a few minutes.', type=MessageType.INFO)
                if platform.system() == 'Darwin':
                    system_password = PyFlamePasswordWindow(title=f'{SCRIPT_NAME}: Enter Sudo Password', message='the sudo password is required to install python packages and mp4 profiles.<br><br>This is required for each new version of Flame.').password()
                else:
                    system_password = PyFlamePasswordWindow(title=f'{SCRIPT_NAME}: Enter Root Password', message='The root password is required to install python packages and mp4 profiles.<br><br>This is required for each new version of Flame.').password()

                if system_password:

                    print('Making sure pip is up to date...')

                    pip_path = f'/opt/Autodesk/python/{self.flame_version}/bin/pip3'

                    result = subprocess.run([pip_path, 'install', '--upgrade', 'pip'], capture_output=True)

                    print(result.stdout.decode())

                    pyflame.message_print(SCRIPT_NAME, 'Installing required python packages...')

                    # Loop through the list and install each package to the target directory using pip with Popen

                    num = 1

                    for package in self.required_python_packages:

                        pyflame.message_print(SCRIPT_NAME, f'Installing python package {num} of {len(self.required_python_packages)}: {package}')

                        process = subprocess.Popen(['sudo', pip_path, 'install', '--target', self.python_path, package], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        process.communicate(system_password + '\n')[1]
                        stdout, stderr = process.communicate()

                        # Print the output to the console

                        print(stdout.decode('utf-8'))
                        #print(stderr.decode('utf-8'))

                        num += 1

                        pyflame.message_print(SCRIPT_NAME, 'Required python packages installed.')


                    # Copy Profiles required for FrameIO Export Presets
                    profile_path = f'/opt/Autodesk/mediaconverter/{self.flame_version}/profiles/MP4/video/H264'
                    profile_list = ['UC_5Mbits.cdxprof', 'UC_10Mbits.cdxprof', 'UC_20Mbits.cdxprof']

                    # Copy Profiles required for FrameIO Export Presets
                    
                    if platform.system() == 'Darwin':
                        p = Popen(['sudo', '-S', 'cp', '-r', '/opt/Autodesk/shared/python/frame_io/profiles/H264/UC_5Mbits.cdxprof', profile_path], stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        p = Popen(['sudo', '-S', 'cp', '-r', '/opt/Autodesk/shared/python/frame_io/profiles/H264/UC_10Mbits.cdxprof', profile_path], stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        p = Popen(['sudo', '-S', 'cp', '-r', '/opt/Autodesk/shared/python/frame_io/profiles/H264/UC_20Mbits.cdxprof', profile_path], stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        chmod_cmd  = ("chmod 777 -R " + profile_path)
                        new_command = chmod_cmd.split()
                        p = Popen(['sudo', '-S'] + new_command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        pyflame.message_print(SCRIPT_NAME, 'Profiles required for FrameIO Export Presets installed.')

                    else:
                        machine = platform.node()
                        for item in profile_list:
                            profile_cp_cmd = f'ssh root@{machine} cp /opt/Autodesk/shared/python/frame_io/profiles/H264/{item} {profile_path}'
                            p = subprocess.Popen(profile_cp_cmd, shell=True, stdin=PIPE, stderr=PIPE, text=True)
                            p.communicate(system_password + '\n')[1]


                    # Install specific Version of urllib3:
                    try:
                        p = Popen(['sudo', '-S', 'rm', '-rf', f'{self.python_path}/urllib3'], stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        p = Popen(['sudo', '-S', 'rm', '-rf', f'{self.python_path}/urllib3-2.1.0.dist-info'], stdin=PIPE, stderr=PIPE, universal_newlines=True)
                        p.communicate(system_password + '\n')[1]
                        p = subprocess.Popen(['sudo', pip_path, 'install', '--target', self.python_path, "urllib3==1.25.11"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        p.communicate(system_password + '\n')[1]
                        print(f"urllib3 1.25.11 installed successfully in {self.python_path}.")
                    except:
                        print(f"Error installing urllib3 1.26.")
                    
                    # Clear System Password
                    system_password = ''

            
            packages_installed = packages_check()
            if packages_installed:
                return True
            else:
                install_packages()
                packages_installed = packages_check()
                if packages_installed:
                    return True
                else:
                    PyFlameMessageWindow(title=f'{SCRIPT_NAME}: Error', message='Failed to install required python packages.', type=MessageType.ERROR)
                    return False

        # Check for installed packages

        packages_installed = check_for_installed_packages()
        if not packages_installed:
            return False

        return True

    def remove_arm_packages(self):

        # Delete old ARM packages that may have been incorrectly installed by version 1.0 of this script

        system_password = PyFlamePasswordWindow(title=f'{SCRIPT_NAME}: Enter System Password', message='System password required to install required python modules.<br><br>This is required for each new version of Flame.').password()

        # Loop through packages and delete them

        if system_password:
            for package in self.required_python_packages:
                try:
                    # Use sudo command to delete old packages

                    command = f'rm -rf {self.python_path}/{package}'
                    command = command.split()

                    p = Popen(['sudo', '-S'] + command, stdin=PIPE, stderr=PIPE, universal_newlines=True)
                    p.communicate(system_password + '\n')[1]
                except:
                    pass

            return True
        return False

#-------------------------------------#
# Flame Menus

def app_initialized(install_packages):
    install_python_packages(install_packages)