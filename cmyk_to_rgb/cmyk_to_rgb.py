# CMYK to RGB
# Copyright (c) 2025 Michael Vaglienty
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# License:       GNU General Public License v3.0 (GPL-3.0)
#                https://www.gnu.org/licenses/gpl-3.0.en.html

"""
Script Name: CMYK to RGB
Script Version: 1.0.1
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 12.24.25

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Media Panel / Media Hub File Browser

Description:

    Convert CMYK images to RGB.

    Supported image formats: TIF, JPG, and PSD.

    PSD files will be saved as TIFF files.

Menus:

    Right-click on a CMYK clip in the Media Panel -> CMYK to RGB
    Right-click on a CMYK file in the Media Hub File Browser -> CMYK to RGB

To install:

    Copy script into /opt/Autodesk/shared/python/cmyk_to_rgb

Updates:

    v1.0.1 12.24.25
        - Moved PIL python packages to assets/python_packages directory.
        - Updated python package installation.

    v1.0.0 12.06.25
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

import os
import flame
from lib.pyflame_lib_cmyk_to_rgb import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'CMYK to RGB'
SCRIPT_VERSION = 'v1.0.1'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class CMYKToRGB:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Install required python packages if not already installed.
        if not self.install_required_python_packages():
            return

        # Process selected images
        self.process_images(selection)

    def install_required_python_packages(self) -> bool:
        """
        Install Required Python Packages
        ================================

        Install the required python packages for the script.

        Returns
        -------
            bool:
                True if the python packages are installed, False otherwise.
        """

        # Install required python packages if not already installed.
        flame_version = pyflame.get_flame_version()

        # Determine which Python version is required.
        if flame_version <= 2026.9:
            python_version = '3.11'
        elif flame_version >= 2027.0 and flame_version < 2027.9:
            python_version = '3.13'
        else:
            PyFlameMessageWindow(
                message=f'Flame version: {flame_version} is not supported.',
                message_type=MessageType.ERROR,
                title='CMYK to RGB',
                parent=None,
                )
            return False

        pyflame.python_package_local_install(package=f'PIL_python{python_version}')

        return True

    #-----------------------------------------------------------------------------

    def process_images(self, selection: list) -> None:
        """
        Process Images
        ==============

        Process the conversion of the selected images from CMYK to RGB

        Args
        ----
            selection (list):
                Clips selected in Flame
        """

        # Dictionary to store the image paths and destinations for each image.
        image_destinations = {}

        pyflame.print('Getting clip info...', underline=True, new_line=False)

        # Process each image in the selection.
        for image in selection:
            pyflame.print(f'Image: {str(image.name)[1:-1]}', new_line=False)
            pyflame.print(f'Image type: {type(image)}', new_line=False)

            if isinstance(image, flame.PyClip): # Get image path and destination for PyClip.
                pyflame.print('Image is a clip')
                image_path = self.get_clip_image_path(image)
                image_destination = image.parent
            elif isinstance(image, flame.PyMediaHubFilesEntry): # Get image path and destination for PyMediaHubFilesEntry.
                pyflame.print('Image is a media hub file')
                image_path = image.path
                pyflame.print(f'Image path: {image_path}', new_line=False)
                image_destination = 'New Library'

            # Check if image extension is supported.
            if not self.check_image_extension(image_path):
                PyFlameMessageWindow(
                    message=f'Unsupported image extension:\n\n{image_path}\n\nOnly TIFF, TIF, JPEG, JPG, and PSD are supported.',
                    message_type=MessageType.ERROR,
                    title='CMYK to RGB',
                    parent=None,
                    )
                continue

            # Convert image to RGB
            converted_path = self.convert_cmyk_to_rgb(src_path=image_path, dst_path=None)

            # Add converted path and destination to dictionary
            if converted_path:
                image_destinations[converted_path] = image_destination
            else:
                continue

        # If there are any image destinations, import the converted images.
        if len(image_destinations) > 0:
            self.import_converted_image(image_destinations)

            print('--------------------------------------------------------------------------------\n\n')

            PyFlameMessageWindow(
                message='CMYK to RGB Conversion Complete!',
                title='CMYK to RGB',
                parent=None,
                )

    def get_clip_image_path(self, image: flame.PyClip) -> str:
        """
        Get Clip Image Path
        ===================

        Get the path to the clip/image as a string.

        Args
        ----
            image (flame.PyClip):
                Clip to get the image path from.

        Returns
        -------
            str:
                The path to the clip/image.
        """

        pyflame.print('Getting clip image path...', underline=True, new_line=False)

        # Get path to the image as a string
        image_path = str(image.versions[0].tracks[0].segments[0].file_path)
        pyflame.print(f'Image Path: {image_path}')

        return image_path

    def check_image_extension(self, image_path: str) -> bool:
        """
        Check Image Extension
        =====================

        Check the image extension and return True if it is supported, False otherwise.

        Args
        ----
            image_path (str):
                The path to the image to check.

        Returns
        -------
            bool:
                True if the image extension is supported, False otherwise.
        """

        pyflame.print('Checking image extension...', underline=True, new_line=False)

        # List of allowed image extensions
        allowed_extensions = ('.tif', '.tiff', '.jpg', '.jpeg', '.psd')

        # Convert image path to lowercase
        image_path = image_path.lower()

        # Check if the image path ends with any of the allowed extensions
        if image_path.endswith(allowed_extensions):
            pyflame.print('Image extension is supported')
            return True
        else:
            pyflame.print('Image extension is not supported')
            return False

    def convert_cmyk_to_rgb(self, src_path: str, dst_path: str | None = None) -> tuple[str, str]:
        """
        Convert CMYK to RGB
        ===================

        Convert a CMYK image to RGB.

        Args
        ----
            src_path (str):
                The path to the CMYK image to convert.
            dst_path (str | None):
                The path to save the converted RGB image to. If None, the image will be saved to the same path as the source image, but with the extension changed to _rgb.tif.

        Returns
        -------
            str:
                The path to the converted RGB image.
        """

        # Imports - keep local to this function.
        from PIL import Image
        from PIL import ImageCms

        def has_alpha_channel(img: Image.Image) -> bool:
            """
            Has Alpha Channel
            =================

            Return True if the Pillow image has an alpha channel.
            This works for modes like RGBA, LA, etc.

            Args
            ----
                img (Image.Image):
                    The image to check for an alpha channel.

            Returns
            -------
                bool:
                    True if the image has an alpha channel, False otherwise.
            """

            pyflame.print('Checking for alpha channel...', new_line=False)

            bands = img.getbands()  # e.g. ('R', 'G', 'B', 'A')
            pyflame.print(f'Bands: {bands}', new_line=False)

            if 'A' in bands:
                pyflame.print('Alpha channel present', new_line=False)
                return True
            else:
                pyflame.print('Alpha channel not present', new_line=False)
                return False

        pyflame.print('Converting image...', underline=True, new_line=False)

        # Open image
        img = Image.open(src_path)
        img_format = img.format  # 'TIFF', 'TIF', 'JPEG', 'JPG', 'PSD', etc.
        mode = img.mode          # 'CMYK', 'RGBA', etc.
        print(f'Image format: {img_format}')
        print(f'Image mode: {mode}')

        # Exit if unsupported format
        if img_format.lower() not in {'tiff', 'tif', 'jpeg', 'jpg', 'psd'}:
            PyFlameMessageWindow(
                message=f'Unsupported format: {img_format}. Only TIF, JPG, and PSD are handled.',
                message_type=MessageType.ERROR,
                title='CMYK to RGB',
                parent=None,
                )
            return

        # Exit if already RGB or RGBA
        if mode in {'RGB', 'RGBA'}:
            PyFlameMessageWindow(
                message=f'Image is already {mode}. No conversion needed.',
                title='CMYK to RGB',
                parent=None,
                )
            return

        # ------------------------------------------------

        # Determine if we have an alpha channel that we want to carry over.
        alpha_present = has_alpha_channel(img)

        # ICC-Aware CMYK → RGB Conversion
        embedded_profile = img.info.get('icc_profile')

        if embedded_profile:
            # Create profiles from the embedded CMYK and sRGB profiles
            try:
                # Load embedded CMYK profile directly from bytes
                cmyk_profile = ImageCms.ImageCmsProfile(BytesIO(embedded_profile))
            except NameError:
                # If BytesIO not imported yet, import it
                from io import BytesIO
                cmyk_profile = ImageCms.ImageCmsProfile(BytesIO(embedded_profile))

            rgb_profile = ImageCms.createProfile('sRGB')

            # Try Relative Colorimetric + Black Point Compensation (if available)
            flags = 0
            try:
                flags = ImageCms.FLAGS.get('BLACKPOINTCOMPENSATION', 0)
            except Exception:
                pass

            try:
                rgb = ImageCms.profileToProfile(
                    img,
                    cmyk_profile,
                    rgb_profile,
                    renderingIntent=1,  # 1 = Relative Colorimetric
                    outputMode='RGB',
                    flags=flags,
                )
                pyflame.print('Using embedded CMYK ICC profile (RelCol + BPC) for conversion.')
            except Exception:
                pyflame.print(f'ICC profile conversion failed. Falling back to basic CMYK to RGB conversion.', print_type=PrintType.ERROR)
                rgb = img.convert('RGB')
        else:
            pyflame.print('No ICC profile embedded. Using basic CMYK to RGB conversion.')
            rgb = img.convert('RGB')

        # If TIFF (or hypothetically PSD) with alpha, preserve it
        result = rgb
        if img_format in {'TIFF', 'TIF', 'PSD'} and alpha_present:
            try:
                alpha = img.getchannel('A')
                result = rgb.convert('RGBA')
                result.putalpha(alpha)
            except ValueError:
                result = rgb

        # Work out output path and format
        src_root, src_ext = os.path.splitext(src_path)

        # Default: same extension / format, suffixed with _rgb
        if dst_path is None:
            out_ext = src_ext
            out_format = img_format

            # Pillow cannot save PSD; fall back to TIFF
            if img_format == "PSD":
                out_ext = ".tif"
                out_format = "TIFF"
                pyflame.print('Script cannot save PSD files. Saving as TIFF instead.', print_type=PrintType.WARNING)

            dst_path = f"{src_root}_rgb{out_ext}"
        else:
            # User provided output path
            _, out_ext = os.path.splitext(dst_path)
            if img_format == "PSD":
                pyflame.print('Pillow cannot save PSD files. Saving as TIFF instead.', print_type=PrintType.WARNING)
                out_format = "TIFF"
            else:
                out_format = img_format

        save_kwargs = {}
        if out_format == "JPEG":
            save_kwargs["quality"] = 95

        result.save(dst_path, format=out_format, **save_kwargs)

        pyflame.print(f"Saved converted image: {dst_path} (format={out_format}, mode={result.mode})")

        return dst_path

    def import_converted_image(self, image_destinations: dict[list, list]) -> None:
        """
        Import Converted Image
        ======================

        Import the converted RGB image into the current Flame project.

        Args
        ----
            image_destinations (dict[list, list]):
                A dictionary of image paths and destinations.

        Notes
        -----
            - If the image is a clip in the media panel, the image will be imported to the same place.
            - If the image is a clip in the media hub, a new library will be created in the media panel and the image will be imported to that library.
        """

        pyflame.print('Importing converted images...', underline=True, new_line=False)

        import_library_created = False

        for path, destination in image_destinations.items():
            print('Path: ', path)
            print('Destination: ', destination, '\n')
            if destination == 'New Library':
                # Create a new library and import the image to that library.
                if not import_library_created:
                    import_library = flame.projects.current_project.current_workspace.create_library('-= Imported CMYK to RGB Images =-')
                    import_library_created = True
                    import_library.expanded = True
                # Import the image to the new library.
                flame.import_clips(path, import_library)
            else:
                flame.import_clips(path, destination)

# ==============================================================================
# [Scopes]
# ==============================================================================

# Scope to only allow clips with file paths to see menu
def scope_clip(selection):

    for item in selection:
        if isinstance(item, (flame.PyClip)) and item.versions[0].tracks[0].segments[0].file_path != '':
            return True
    return False

# Scope to only allow media hub files to see menu
def scope_media_hub_file(selection):

    for item in selection:
        if isinstance(item, (flame.PyMediaHubFilesEntry)):
            return True
    return False

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_media_panel_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'CMYK to RGB',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_clip,
                    'execute': CMYKToRGB,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]

def get_mediahub_files_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'CMYK to RGB',
                    'order': 1,
                    'separator': 'below',
                    'isVisible': scope_media_hub_file,
                    'execute': CMYKToRGB,
                    'minimumVersion': '2025'
               }
           ]
        }
    ]
