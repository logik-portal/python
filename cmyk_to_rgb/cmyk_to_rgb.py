# CMYK to RGB
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: CMYK to RGB
Script Version: 1.1.0
Flame Version: 2025
Written by: Michael Vaglienty
Creation Date: 12.06.25
Update Date: 11.02.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Media Panel / Media Hub File Browser

Description:

    Convert CMYK images to RGB.

    Supported image formats: TIF, JPG, and PSD.

    PSD files will be saved as TIFF files.

    Works on Linux and Apple Silicon Macs. Intel Macs are not supported.

    The image's embedded CMYK profile is used for the conversion. Images without an
    embedded profile are converted using U.S. Web Coated (SWOP) v2 (Adobe profile;
    see assets/icc_profiles/README.txt for its license).

    Output images are 8-bit RGB with an sRGB profile.

    CMYK PSDs with extra channels (alpha or spot) and CMYK TIFFs with transparency
    are not supported.

URL:

    https://logik-portal.com/scripts/cmyk_to_rgb

Menus:

    Right-click on a CMYK clip in the Media Panel -> CMYK to RGB
    Right-click on a CMYK file in the Media Hub File Browser -> CMYK to RGB

To install:

    Copy script into /opt/Autodesk/shared/python/cmyk_to_rgb

Updates:

    v1.1.0 11.02.26
        - Added Linux support.
        - Intel Macs are not supported. A message is now shown instead of installing a package
          that can't run.
        - Fixed the Pillow install reporting success when it failed.
        - The Python version is now read from Flame's Python (3.11 or 3.13) instead of guessed
          from the Flame version.
        - Images without an embedded CMYK profile are now converted with the U.S. Web Coated
          (SWOP) v2 profile. Before, they got a basic conversion with wrong colors.
        - Fixed black point compensation not being applied.
        - One failed image no longer stops the rest. A single summary is shown at the end
          instead of a message for each image.
        - Fixed errors when other items are selected along with the images.
        - Only CMYK images are converted. RGB, grayscale, LAB and other images are skipped.
        - PSDs with extra channels (alpha or spot) are now refused. Before, they were saved with
          scrambled pixels.
        - Image sequences and missing files are now skipped.
        - Output images now include an sRGB profile and keep their DPI. JPEGs are saved without
          chroma subsampling.
        - A warning is now shown before existing files are overwritten.
        - Two selected images that would save to the same file name (for example image.psd and
          image.tif) are no longer both saved.
        - The menu now only shows for supported image files.

    v1.0.2 10.13.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.

    v1.0.1 12.24.25
        - Moved PIL python packages to assets/python_packages directory.
        - Updated python package installation.

    v1.0.0 12.06.25
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os
import platform
import sys
import flame
from lib.pyflame_lib_cmyk_to_rgb import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'CMYK to RGB'
SCRIPT_VERSION = 'v1.1.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

SUPPORTED_EXTENSIONS = ('.tif', '.tiff', '.jpg', '.jpeg', '.psd')
DEFAULT_CMYK_PROFILE_PATH = os.path.join(SCRIPT_PATH, 'assets', 'icc_profiles', 'USWebCoatedSWOP.icc')

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

        # Determine which platform packages are required. Intel Macs are not supported.
        if platform.system() == 'Darwin':
            if platform.machine() != 'arm64':
                PyFlameMessageWindow(
                    message='CMYK to RGB requires an Apple Silicon Mac. Intel Macs are not supported.\n\nPython package install cancelled.',
                    message_type=MessageType.ERROR,
                    title='CMYK to RGB',
                    parent=None,
                    )
                return False
            platform_suffix = 'macos'
        elif platform.system() == 'Linux':
            platform_suffix = 'linux'
        else:
            PyFlameMessageWindow(
                message=f'Operating system: {platform.system()} is not supported.',
                message_type=MessageType.ERROR,
                title='CMYK to RGB',
                parent=None,
                )
            return False

        # Use the Python version Flame is running, only 3.11 and 3.13 packages are bundled.
        python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
        if python_version not in ('3.11', '3.13'):
            PyFlameMessageWindow(
                message=f'Python {python_version} is not supported.',
                message_type=MessageType.ERROR,
                title='CMYK to RGB',
                parent=None,
                )
            return False

        # Install required python packages
        installed = pyflame.python_package_local_install(package=f'PIL_python{python_version}_{platform_suffix}')
        if not installed:
            pyflame.print('Python packages not installed, exiting script.', print_type=PrintType.ERROR)
            return False

        return True

    #-----------------------------------------------------------------------------

    def process_images(self, selection: list) -> None:
        """
        Process Images
        ==============

        Process the conversion of the selected images from CMYK to RGB.

        Images are checked first, then converted and imported. Images that can't be converted are
        skipped or failed and listed in one summary at the end.

        Args
        ----
            selection (list):
                Clips or MediaHub files selected in Flame.
        """

        # Imports - keep local to this function.
        from PIL import Image
        from PIL import UnidentifiedImageError

        # Images to convert: (file name, source path, output path, destination)
        images_to_convert = []

        # Results: converted holds (file name, output name), skipped and failed hold (file name, reason)
        converted = []
        skipped = []
        failed = []

        # Lower-case output path -> file name of the image that will be saved there
        output_owners = {}

        pyflame.print('Checking selected images...', underline=True, new_line=False)

        # Check each selected image. Only clips (not sequences) and MediaHub files are used.
        for item in selection:
            if isinstance(item, flame.PyClip) and not isinstance(item, flame.PySequence):
                file_name = str(item.name)[1:-1]
                destination = item.parent
            elif isinstance(item, flame.PyMediaHubFilesEntry):
                file_name = os.path.basename(str(item.path))
                destination = 'New Library'
            else:
                continue

            try:
                # Get image path
                if isinstance(item, flame.PyMediaHubFilesEntry):
                    image_path = str(item.path)
                else:
                    image_path = self.get_clip_image_path(item)
                file_name = os.path.basename(image_path)
                pyflame.print(f'Image path: {image_path}', new_line=False)

                if not self.check_image_extension(image_path):
                    skipped.append((file_name, 'Unsupported file type. Only TIF, JPG and PSD are supported.'))
                    continue

                if not os.path.isfile(image_path):
                    skipped.append((file_name, 'File not found. Image sequences are not supported.'))
                    continue

                # Read image format and mode without loading the pixels
                try:
                    with Image.open(image_path) as img:
                        img_format = img.format
                        mode = img.mode
                except UnidentifiedImageError:
                    reason = 'Image could not be read.'
                    if image_path.lower().endswith(('.tif', '.tiff')):
                        reason += ' CMYK TIFFs with transparency are not supported.'
                    failed.append((file_name, reason))
                    continue

                if img_format not in ('TIFF', 'JPEG', 'PSD'):
                    skipped.append((file_name, f'Unsupported format: {img_format}'))
                    continue

                if mode != 'CMYK':
                    skipped.append((file_name, f'Not a CMYK image (mode: {mode})'))
                    continue

                # Pillow scrambles the pixels of CMYK PSDs with alpha or spot channels
                if img_format == 'PSD' and self.psd_has_extra_channels(image_path):
                    failed.append((file_name, 'PSD has extra channels (alpha or spot). Flatten and remove extra channels, then try again.'))
                    continue

                # Don't let two selected images save to the same file. Compare lower-case paths for case-insensitive volumes.
                output_path = self.get_output_path(image_path, img_format)
                output_key = output_path.lower()
                if output_key in output_owners:
                    failed.append((file_name, f'Output name clashes with {output_owners[output_key]}'))
                    continue

                output_owners[output_key] = file_name
                images_to_convert.append((file_name, image_path, output_path, destination))
            except Exception as e:
                failed.append((file_name, str(e)))

        # Ask once before overwriting any existing output files
        existing = [image for image in images_to_convert if os.path.exists(image[2])]
        if existing:
            existing_names = '\n'.join(os.path.basename(image[2]) for image in existing)
            overwrite = PyFlameMessageWindow(
                message=f'These output files already exist:\n\n{existing_names}\n\nOverwrite them?',
                message_type=MessageType.WARNING,
                title='CMYK to RGB',
                parent=None,
                )
            if not overwrite:
                for image in existing:
                    skipped.append((image[0], 'Output file already exists'))
                images_to_convert = [image for image in images_to_convert if image not in existing]

        # Convert images
        image_destinations = {}
        output_sources = {}
        for file_name, image_path, output_path, destination in images_to_convert:
            try:
                self.convert_cmyk_to_rgb(src_path=image_path, dst_path=output_path)
                image_destinations[output_path] = destination
                output_sources[output_path] = file_name
            except Exception as e:
                pyflame.print(f'Conversion failed: {image_path}\n{e}', print_type=PrintType.ERROR)
                failed.append((file_name, str(e)))

        # Import converted images, an image that fails to import is listed as failed
        if image_destinations:
            import_failures = self.import_converted_image(image_destinations)
            for output_path in image_destinations:
                if output_path in import_failures:
                    failed.append((output_sources[output_path], f'Converted to {os.path.basename(output_path)}, but import failed: {import_failures[output_path]}'))
                else:
                    converted.append((output_sources[output_path], os.path.basename(output_path)))

        print('--------------------------------------------------------------------------------\n\n')

        # Nothing selected that the script works on
        if not converted and not skipped and not failed:
            pyflame.print('No supported images selected.', print_type=PrintType.WARNING)
            return

        # Print full details to the console
        for file_name, output_name in converted:
            pyflame.print(f'Converted: {file_name} -> {output_name}', text_color=TextColor.GREEN, new_line=False)
        for file_name, reason in skipped:
            pyflame.print(f'Skipped: {file_name}: {reason}', print_type=PrintType.WARNING, new_line=False)
        for file_name, reason in failed:
            pyflame.print(f'Failed: {file_name}: {reason}', print_type=PrintType.ERROR, new_line=False)

        # All images converted
        if not skipped and not failed:
            PyFlameMessageWindow(
                message=f'CMYK to RGB Conversion Complete!\n\nConverted: {len(converted)}',
                message_type=MessageType.OPERATION_COMPLETE,
                title='CMYK to RGB',
                parent=None,
                )
            return

        # Show one summary of converted, skipped and failed images
        message = f'Converted: {len(converted)}'
        if skipped:
            message += '\n\nSkipped:\n' + '\n'.join(f'{file_name}: {reason}' for file_name, reason in skipped)
        if failed:
            message += '\n\nFailed:\n' + '\n'.join(f'{file_name}: {reason}' for file_name, reason in failed)

        PyFlameMessageWindow(
            message=message,
            message_type=MessageType.ERROR if failed else MessageType.INFO,
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

        # Convert image path to lowercase
        image_path = image_path.lower()

        # Check if the image path ends with any of the allowed extensions
        if image_path.endswith(SUPPORTED_EXTENSIONS):
            pyflame.print('Image extension is supported')
            return True
        else:
            pyflame.print('Image extension is not supported')
            return False

    def psd_has_extra_channels(self, image_path: str) -> bool:
        """
        PSD Has Extra Channels
        ======================

        Check the PSD header for a CMYK PSD with more than 4 channels (alpha or spot channels).

        Args
        ----
            image_path (str):
                The path to the PSD file.

        Returns
        -------
            bool:
                True if the PSD is CMYK and has more than 4 channels, False otherwise.
        """

        # Read the 26-byte PSD header: bytes 12-13 are the channel count, bytes 24-25 the color mode (4 = CMYK)
        with open(image_path, 'rb') as psd_file:
            header = psd_file.read(26)

        channels = int.from_bytes(header[12:14], 'big')
        color_mode = int.from_bytes(header[24:26], 'big')
        pyflame.print(f'PSD channels: {channels}, color mode: {color_mode}', new_line=False)

        return color_mode == 4 and channels > 4

    def get_output_path(self, src_path: str, img_format: str) -> str:
        """
        Get Output Path
        ===============

        Get the path the converted image is saved to: the source path with _rgb added to the name.
        PSD files are saved as TIFF files.

        Args
        ----
            src_path (str):
                The path to the CMYK image.

            img_format (str):
                The Pillow format of the CMYK image ('TIFF', 'JPEG' or 'PSD').

        Returns
        -------
            str:
                The path to save the converted RGB image to.
        """

        src_root, src_ext = os.path.splitext(src_path)

        # Pillow cannot save PSD; save as TIFF
        if img_format == 'PSD':
            src_ext = '.tif'

        return f'{src_root}_rgb{src_ext}'

    def convert_cmyk_to_rgb(self, src_path: str, dst_path: str) -> str:
        """
        Convert CMYK to RGB
        ===================

        Convert a CMYK image to 8-bit RGB with an sRGB profile and save it.

        The embedded CMYK profile is used. If the image has no profile, or it can't be read,
        the default CMYK profile is used.

        Args
        ----
            src_path (str):
                The path to the CMYK image to convert.

            dst_path (str):
                The path to save the converted RGB image to.

        Returns
        -------
            str:
                The path to the converted RGB image.

        Raises
        ------
            OSError:
                If the image has no usable embedded profile and the default CMYK profile is missing.

            Exception:
                If the image can't be read, converted or saved.
        """

        # Imports - keep local to this function.
        from io import BytesIO
        from PIL import Image
        from PIL import ImageCms

        pyflame.print('Converting image...', underline=True, new_line=False)

        with Image.open(src_path) as img:
            img_format = img.format
            pyflame.print(f'Image: {src_path}', new_line=False)
            pyflame.print(f'Image format: {img_format}', new_line=False)
            pyflame.print(f'Image mode: {img.mode}', new_line=False)

            # Load the embedded CMYK profile
            cmyk_profile = None
            embedded_profile = img.info.get('icc_profile')
            if embedded_profile:
                try:
                    cmyk_profile = ImageCms.ImageCmsProfile(BytesIO(embedded_profile))
                    pyflame.print('Using embedded CMYK profile.', new_line=False)
                except Exception as e:
                    pyflame.print(f'Embedded CMYK profile could not be read, using default CMYK profile: {e}', print_type=PrintType.WARNING)

            # Use the default CMYK profile when there is no usable embedded profile
            if cmyk_profile is None:
                if not os.path.isfile(DEFAULT_CMYK_PROFILE_PATH):
                    raise OSError(f'No usable embedded CMYK profile and the default CMYK profile is missing: {DEFAULT_CMYK_PROFILE_PATH}')
                cmyk_profile = ImageCms.ImageCmsProfile(DEFAULT_CMYK_PROFILE_PATH)
                pyflame.print(f'Using default CMYK profile: {DEFAULT_CMYK_PROFILE_PATH}', new_line=False)

            # Relative colorimetric with black point compensation. Older Pillow has no Intent/Flags enums.
            try:
                rendering_intent = ImageCms.Intent.RELATIVE_COLORIMETRIC
                flags = ImageCms.Flags.BLACKPOINTCOMPENSATION
            except AttributeError:
                rendering_intent = 1
                flags = ImageCms.FLAGS['BLACKPOINTCOMPENSATION']

            rgb_profile = ImageCms.createProfile('sRGB')
            rgb = ImageCms.profileToProfile(
                img,
                cmyk_profile,
                rgb_profile,
                renderingIntent=rendering_intent,
                outputMode='RGB',
                flags=flags,
                )

            # Embed sRGB profile and keep DPI
            save_kwargs = {
                'icc_profile': ImageCms.ImageCmsProfile(rgb_profile).tobytes(),
                }
            if 'dpi' in img.info:
                save_kwargs['dpi'] = img.info['dpi']

        # Pillow cannot save PSD; save as TIFF
        out_format = img_format
        if img_format == 'PSD':
            out_format = 'TIFF'
            pyflame.print('Script cannot save PSD files. Saving as TIFF instead.', print_type=PrintType.WARNING)

        if out_format == 'JPEG':
            save_kwargs['quality'] = 95
            save_kwargs['subsampling'] = 0

        rgb.save(dst_path, format=out_format, **save_kwargs)

        pyflame.print(f'Saved converted image: {dst_path} (format={out_format}, mode={rgb.mode})')

        return dst_path

    def import_converted_image(self, image_destinations: dict) -> dict:
        """
        Import Converted Image
        ======================

        Import the converted RGB images into the current Flame project. Each image is imported on
        its own, so one failed import doesn't stop the rest.

        Args
        ----
            image_destinations (dict):
                A dictionary of image paths and destinations.

        Returns
        -------
            dict:
                Image paths that failed to import, with the error text.

        Notes
        -----
            - If the image is a clip in the media panel, the image will be imported to the same place.
            - If the image is a clip in the media hub, a new library will be created in the media panel and the image will be imported to that library.
        """

        pyflame.print('Importing converted images...', underline=True, new_line=False)

        import_library = None
        import_failures = {}

        for path, destination in image_destinations.items():
            print('Path: ', path)
            print('Destination: ', destination, '\n')
            try:
                if destination == 'New Library':
                    # Create a new library and import the image to that library.
                    if import_library is None:
                        import_library = flame.projects.current_project.current_workspace.create_library('-= Imported CMYK to RGB Images =-')
                        import_library.expanded = True
                    # Import the image to the new library.
                    flame.import_clips(path, import_library)
                else:
                    flame.import_clips(path, destination)
            except Exception as e:
                pyflame.print(f'Import failed: {path}\n{e}', print_type=PrintType.ERROR)
                import_failures[path] = str(e)

        return import_failures

# ==============================================================================
# [Scopes]
# ==============================================================================

# Scope to only allow clips (not sequences) with a supported image file path to see menu
def scope_clip(selection):

    for item in selection:
        if isinstance(item, flame.PyClip) and not isinstance(item, flame.PySequence):
            try:
                file_path = str(item.versions[0].tracks[0].segments[0].file_path)
            except Exception:
                continue
            if file_path.lower().endswith(SUPPORTED_EXTENSIONS):
                return True
    return False

# Scope to only allow media hub files with a supported image extension to see menu
def scope_media_hub_file(selection):

    for item in selection:
        if isinstance(item, flame.PyMediaHubFilesEntry) and str(item.path).lower().endswith(SUPPORTED_EXTENSIONS):
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
