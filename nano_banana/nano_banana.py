# Nano Banana
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Nano Banana
Script Version: 1.3.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 03.13.26
Update Date: 11.01.26

License: MIT License (MIT) - see LICENSE file for details
 
Script Type: Media Panel

Description:

    Generate images using Nano Banana models.

    A valid Google/Gemini API key is required to use this script.

    Currently supported models:

        Gemini Nano Banana 2.1 (Nano Banana 2.1) - Default model
            - High-efficiency model with improved visual quality, text rendering and multi-turn consistency.
            - Supports 1K, 2K, and 4K resolutions.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            - Supports aspect ratios 1:4, 4:1, 1:8, 8:1.
            - Thinking levels: Minimal, Medium, High. Default: Medium.

        Gemini 3.1 Flash Image (Nano Banana 2)
            - Previous high-efficiency model. Still supported, Google recommends Nano Banana 2.1 for new work.
            - Supports 1K, 2K, 4K, and 512 (512px) resolutions.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            - Supports aspect ratios 1:4, 4:1, 1:8, 8:1.
            - Thinking levels: Minimal, High. Default: Minimal.

        Gemini 3.1 Flash Lite Image (Nano Banana 2 Lite)
            - Fastest and lowest cost model. Best for quick iteration.
            - Only supports 1K resolution.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            - Thinking levels: Minimal, High. Default: Minimal.

        Gemini 3 Pro Image (Nano Banana Pro)
            - Highest quality model. Best for complex prompts and rendering text in images.
            - Supports 1K, 2K, and 4K resolutions.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            - Thinking is always on and the level can't be set.

    Gemini Chat:

        Send a message to chat with Gemini 3.8 Flash about creating an image. Great for improving prompts or describing images.
        Enter a message in the prompt field and click the Gemini Chat button. The response will be displayed in the prompt
        text window. Copy and paste any response into the prompt text field and use the Send Prompt button to send the prompt
        to Nano Banana.

    Images:

        Returned images are saved as PNG or JPEG. Any other type Google returns (such as WebP, which Flame
        can't read) is converted to PNG. The image gallery only shows PNG and JPEG files.

    ** WARNING **
    Using this script will incur charges to your Nano Banana/Gemini account.
    Please review your usage limits and pricing plan before proceeding.
    Your API key will be stored unencrypted in the config file so be aware of who has access to it.

    Images are stored in <script_path>/images/. A tokenized path can be set in the script
    setup, or with the Change Path button in the main window, to store images in a different location.
    The folder images are saved to is shown under the Image Gallery buttons.

URL:

    https://logik-portal.com/scripts/nano_banana

Useage:

    Run the script with a clip selected in the media panel to export the first frame of the clip
    to the script's images folder and add it to the prompt.

    If no clip is selected, the script will start with a blank prompt.

    After getting back an image from Nano Banana the image is automatically added to the prompt.

    When done prompting use the Import to Flame button to import the desired image to the media panel.

    Buttons:

        Send Prompt: Sends the current prompt to Nano Banana at the selected model and resolution.

        Gemini Chat: Sends the prompt field text (and the prompt image, if there is one) to Gemini Chat.

        Import to Flame: Import the current selected image in the Image Gallery to the media panel.

        Send to Prompt: Adds the selected image in the Image Gallery to the prompt.

        Clear Prompt Image: Clears the current prompt image from the prompt.

        Reveal in Finder / Reveal in MediaHub: Opens the images folder in Finder or the MediaHub.

        Delete Image: Deletes the selected image in the Image Gallery from disk (after a confirm).

        Change Path: Opens the path selection window to change the folder images are saved to. Tokens can be used.

        Done: Saves the selected model, resolution, aspect ratio and thinking level, then closes the window.

Menus:

    Script Setup:
        Flame Main Menu -> Logik -> Logik Portal Script Setup -> Nano Banana Setup

    To prompt Nano Banana with no prompt image:
        Media Panel -> Right-click -> Nano Banana

    To prompt Nano Banana with a prompt image:
        Media Panel -> Right-click on clip or sequence -> Nano Banana

To install:

    Copy script into /opt/Autodesk/shared/python/nano_banana

Updates:

    v1.3.0 11.01.26
        - Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
        - Changed license from GPL-3.0 to MIT. See LICENSE file for details.
        - Working path is now shown under the image gallery.
        - Added a Change Path button to change the working folder from the main UI. 
        - Fixed: in Flame 2027.2 every request failed with "No internet connection" because Flame's Python couldn't 
          find its SSL certificates. Requests now also use the certificates that come with Flame's Python (certifi) 
          and the system's own certificate bundle, so nothing needs to be installed.
        - Fixed: Send Prompt and Gemini Chat caused an error when the prompt image file was moved or deleted outside 
          the script. The error names the file, the prompt image is cleared and nothing is sent.
        - Added the 512 (512px) resolution for Nano Banana 2.
        - Added Gemini Nano Banana 2.1 (Nano Banana 2.1) and made it the default model. 
        - Added Thinking Level menu. 
        - Updated Gemini Chat to use Gemini 3.8 Flash. Gemini 3.7 Flash is deprecated and Google auto-routes it to 
          3.8 (no shutdown date).
        - Fixed: the image gallery listed file types the prompt image can't show (exr, dpx, tif...), and clicking one 
          raised an error. The gallery now shows only PNG and JPEG files, so Import to Flame only gets files Flame 
          can read.
        - Fixed: the prompt image was sent with the wrong type for non-PNG files. The type now matches the 
          file (PNG or JPEG).
        - Fixed: Send Prompt and Gemini Chat stayed enabled during a request, so a double click could send a second 
          paid request. Both are disabled (and Return does nothing) until the request ends.
        - Fixed: saved resolution and aspect ratio were lost when the window opened (4K/4:3 came back as 1K/1:1). 
          Changing the model now resets them to that model's first options.
        - Fixed: clicking Done saved the resolved images path over the tokenized one, so every project saved into 
          the first project's folder.
        - Fixed: Send Prompt API errors now show Google's error message.
        - Requests over Google's 20 MB request size limit are no longer sent. An error shows the prompt image size.
        - Fixed: running the script again on the same clip opened a file exists dialog and the window didn't open. 
          The exported frame is now overwritten.
        - Export errors are now shown in a message window.
        - Fixed: exporting failed when the images folder didn't exist yet. The folder is now created.
        - Fixed: every selected clip was exported. Only the first selected clip or sequence is exported now.
        - Fixed: an empty Gemini Chat reply was added to the history instead of showing an error.
        - Fixed: "Image generated successfully." was shown when no image came back. The reason is now shown 
          (blocked prompt, safety finish reason, returned text).
        - Fixed: "Please wait..." stayed in the status line after an empty prompt or a failed request.
        - Fixed: an empty or invalid API response raised an error instead of showing a message.
        - Fixed: Delete Image raised an error when the selected file was already removed.
        - Fixed: Reveal in Finder/MediaHub failed when the images folder didn't exist yet. The folder is now created.
        - Fixed: Return pressed in the image gallery sent a prompt. Return/Enter in the prompt text field now sends the 
          prompt, Shift+Return adds a new line, and Return elsewhere no longer sends.

    v1.2.0 08.18.26
        - Updated to use Google's current Nano Banana models.
            - Added: Gemini 3.1 Flash Lite Image (Nano Banana 2 Lite).
            - Updated: gemini-3.1-flash-image-preview to gemini-3.1-flash-image (Nano Banana 2).
            - Updated: gemini-3-pro-image-preview to gemini-3-pro-image (Nano Banana Pro).
            - Removed: Gemini 2.5 Flash Image (Nano Banana). Google lists its shutdown as 03.15.27.
        - Updated Gemini Chat to use Gemini 3.7 Flash. Google limits access to Gemini 2.5 Flash to earlier users (no shutdown date announced).
        - Nano Banana 2 is now the default model. Models saved in the config by older versions of the
          script are replaced with the default model on startup.
        - Fixed: aspect ratios 1:4, 4:1, 1:8, and 8:1 were listed for Nano Banana Pro, which does not
          support them.

    v1.1.2 03.25.26
        - Fixed: model resolution menu not updating when a different model is selected.

    v1.1.1 03.24.26
        - Fixed: export preset path. This was causing the script not to work when running the script with an image selected.

    v1.1.0 03.23.26
        - Added Gemini Chat button to send a message to chat with Gemini about creating an image.
        - Updated model menus to clarify model names.

    v1.0.1 03.20.26
        - Updated script to work with Flame 2025.2.

    v1.0.0 03.13.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import base64
import http.client
import json
import os
import random
import ssl
import urllib.error
import urllib.request
from typing import Any

import flame
from PySide6 import QtCore, QtGui, QtWidgets
from lib.pyflame_lib_nano_banana import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME    = 'Nano Banana'
SCRIPT_VERSION = 'v1.3.0'
SCRIPT_PATH    = os.path.abspath(os.path.dirname(__file__))

# Aspect ratios supported by all current Nano Banana image models.
STANDARD_ASPECT_RATIOS = ['1:1', '21:9', '16:9', '4:3', '3:2', '9:16', '3:4', '2:3', '5:4', '4:5']

# Banner and strip aspect ratios. Not supported by Nano Banana Pro or Nano Banana 2 Lite.
EXTENDED_ASPECT_RATIOS = STANDARD_ASPECT_RATIOS + ['1:4', '4:1', '1:8', '8:1']

# Image models shown in the Select Model menu, along with the resolutions and
# aspect ratios each model accepts. Menu text is 'model_id (Model Name)'.
IMAGE_MODELS = {
    'gemini-nano-banana-2.1 (Nano Banana 2.1)': {
        'resolutions': ['1K', '2K', '4K'],
        'aspect_ratios': EXTENDED_ASPECT_RATIOS,
        'thinking_levels': ['Minimal', 'Medium', 'High'],
        'default_thinking_level': 'Medium',
        },
    'gemini-3.1-flash-image (Nano Banana 2)': {
        'resolutions': ['1K', '2K', '4K', '512'],
        'aspect_ratios': EXTENDED_ASPECT_RATIOS,
        'thinking_levels': ['Minimal', 'High'],
        'default_thinking_level': 'Minimal',
        },
    'gemini-3.1-flash-lite-image (Nano Banana 2 Lite)': {
        'resolutions': ['1K'],
        'aspect_ratios': STANDARD_ASPECT_RATIOS,
        'thinking_levels': ['Minimal', 'High'],
        'default_thinking_level': 'Minimal',
        },
    # Thinking is always on for Pro and the level can't be set, so no thinkingConfig is sent.
    'gemini-3-pro-image (Nano Banana Pro)': {
        'resolutions': ['1K', '2K', '4K'],
        'aspect_ratios': STANDARD_ASPECT_RATIOS,
        'thinking_levels': [],
        'default_thinking_level': None,
        },
    }

DEFAULT_IMAGE_MODEL = 'gemini-nano-banana-2.1 (Nano Banana 2.1)'

# Thinking Level menu text for models where the level can't be set.
THINKING_ALWAYS_ON = 'Always On'

# Text model used by the Gemini Chat button.
CHAT_MODEL = 'gemini-3.8-flash'

# Prompt image types sent to Google, by file extension. Also the only files the image gallery
# shows, so Import to Flame never gets a file Flame can't read (Flame can't read WebP).
PROMPT_IMAGE_MIME_TYPES = {
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    }

# Google's limit for the total size of a request with inline image data (20 MB).
MAX_REQUEST_BYTES = 20 * 1024 * 1024

# System CA certificate bundles: macOS (and some Linux), RHEL/Rocky/CentOS, Debian/Ubuntu.
SYSTEM_CA_BUNDLES = [
    '/etc/ssl/cert.pem',
    '/etc/pki/tls/certs/ca-bundle.crt',
    '/etc/ssl/certs/ca-certificates.crt',
    ]

def create_ssl_context() -> ssl.SSLContext:
    """
    Create SSL Context
    ==================

    Create the SSL context used for every request. Flame 2027.2's Python looks for its
    certificates in a folder that doesn't exist, so certifi's and the system's certificates
    are added when found. Nothing here can raise, since Flame imports this file at startup.

    Returns
    -------
        context (ssl.SSLContext): SSL context with every certificate bundle found.
    """

    context = ssl.create_default_context()

    # Add the certificates that come with Flame's Python, if certifi is there
    try:
        import certifi
        context.load_verify_locations(cafile=certifi.where())
    except Exception:
        pass

    # Add the system's own certificate bundles
    for ca_bundle in SYSTEM_CA_BUNDLES:
        if os.path.isfile(ca_bundle):
            try:
                context.load_verify_locations(cafile=ca_bundle)
            except Exception:
                pass

    return context

SSL_CONTEXT = create_ssl_context()

# ==============================================================================
# [Main Script]
# ==============================================================================

def print_pass_fail(message: str, passed: bool, new_line: bool = True) -> None:
    """
    Print status as: [PASS] message or [FAIL] message
    Only PASS/FAIL is colored.
    """
    status_word = "PASS" if passed else "FAIL"
    color = TextColor.GREEN if passed else TextColor.RED
    # Color only PASS/FAIL; brackets and message remain default color.
    status_colored = f"[{color.value}{status_word}{TextColor.RESET.value}] {message}"
    pyflame.print(status_colored, new_line=new_line)

def load_config() -> PyFlameConfig:
    """
    Load Config
    ===========

    Loads configuration values from the config file and returns a PyFlameConfig object with the values.
    """

    settings = PyFlameConfig(
        config_values={
            'api_key': '',
            'images_path': os.path.join(SCRIPT_PATH, 'images'),
            'model': DEFAULT_IMAGE_MODEL,
            'resolution': '1K',
            'aspect_ratio': '1:1',
            'thinking_level': IMAGE_MODELS[DEFAULT_IMAGE_MODEL]['default_thinking_level'],
            },
        )

    # Configs saved by earlier versions of the script can point at models Google
    # has retired. Fall back to the default model so the request doesn't fail.
    if settings.model not in IMAGE_MODELS:
        settings.model = DEFAULT_IMAGE_MODEL

    return settings

def verify_api_key(api_key: str) -> bool:
    """
    Verify API Key
    ==============

    Verify Google Nano Banana API key by listing available models.
    """

    api_key = api_key.strip() if api_key else ''

    if not api_key or api_key == 'YOUR_API_KEY_HERE':
        print_pass_fail('No API key has been set', False)
        PyFlameMessageWindow(
            message='No API key has been set.\n\nPlease add your Google Nano Banana API key and try again.\n\nFlame Main Menu -> Logik -> Logik Portal Script Setup -> Nano Banana Setup',
            parent=None,
            )
        return False

    try:
        url = f'https://generativelanguage.googleapis.com/v1/models?key={api_key}'
        urllib.request.urlopen(url, timeout=10, context=SSL_CONTEXT)
        print_pass_fail('API Key Verified', True)
        return True
    except urllib.error.HTTPError as e:
        if e.code in (400, 403):
            print_pass_fail('Invalid API Key', False)
            PyFlameMessageWindow(
                message='Invalid API key.\n\nPlease check your Google Nano Banana API key and try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )
        else:
            print_pass_fail('API Key Verification Failed', False)
            PyFlameMessageWindow(
                message=f'API key verification failed (HTTP {e.code}).\n\nPlease try again.',
                message_type=MessageType.ERROR,
                parent=None,
                )
        return False
    except (urllib.error.URLError, OSError):
        print_pass_fail('Unable to Verify API Key', False)
        PyFlameMessageWindow(
            message='Unable to verify API key.\n\nPlease check your internet connection and try again.',
            message_type=MessageType.ERROR,
            parent=None,
            )
        return False

def verify_internet_connection() -> bool:
    """
    Check Internet Connection
    =========================

    Check for internet connection.
    """

    try:
        urllib.request.urlopen('https://www.google.com', timeout=5, context=SSL_CONTEXT)
        print_pass_fail('Internet Connection Verified', True, new_line=False)
        return True
    except (urllib.error.URLError, OSError):
        print_pass_fail('Internet Connection Verification Failed', False)
        PyFlameMessageWindow(
            message='No internet connection.\n\nPlease check your internet connection and try again.',
            message_type=MessageType.ERROR,
            parent=None,
            )
        return False

class PromptReturnFilter(QtCore.QObject):

    def __init__(self, text_edit, return_pressed) -> None:
        """
        Prompt Return Filter
        ====================

        Event filter for the prompt text edit. Return/Enter (main or keypad) calls return_pressed,
        Shift+Return is passed on so the text edit adds a new line.

        Args
        ----
            text_edit (PyFlameTextEdit):
                Text edit the filter is installed on. Also the filter's Qt parent.

            return_pressed (callable):
                Function called when Return/Enter is pressed.
        """

        super().__init__(text_edit)
        self.return_pressed = return_pressed

    def eventFilter(self, obj, event) -> bool:
        """
        Event Filter
        ============

        Send on Return/Enter, pass every other event on.

        Args
        ----
            obj (QObject):
                Object that received the event (the prompt text edit).

            event (QEvent):
                Event to check.

        Returns
        -------
            handled (bool): True if the key press was used to send (or was a held-down repeat) and should not reach the text edit.
        """

        if event.type() != QtCore.QEvent.Type.KeyPress or event.key() not in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            return False

        # Shift+Return adds a new line, and a read-only field never sends
        if event.modifiers() & QtCore.Qt.KeyboardModifier.ShiftModifier or obj.isReadOnly():
            return False

        # Swallow auto-repeat so holding Return can't send a second paid request
        if event.isAutoRepeat():
            return True

        self.return_pressed()

        return True

class NanoBanana:

    # Open Nano Banana window, so the Setup window can update its images path
    open_window = None

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Create/Load config file settings.
        self.settings = load_config()

        # Run startup checks
        if not self.startup_checks():
            return

        self.selection = selection
        print('Selection:', selection, '\n')

        # Keep the resolved path separate so the tokenized path in settings is what gets saved.
        self.images_path = pyflame.resolve_tokens(tokenized_string=self.settings.images_path)
        print('Images Path:', self.images_path, '\n')

        # Export image to Nano Banana Prompt if selection is a clip or sequence. Open with a blank prompt image otherwise.
        self.flame_image_exported = False
        if self.selection and isinstance(self.selection[0], (flame.PyClip, flame.PySequence)):
            self.flame_image_exported = self.export_to_nano_banana()

        # Open main window
        self.nano_banana()

    def startup_checks(self) -> bool:
        """
        Startup Checks
        ==============

        Check for internet connection, CURL installed, and API key.
        """

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return False

        # Check for internet connection
        if not verify_internet_connection():
            return False

        # Verify API Key
        if not verify_api_key(api_key=self.settings.api_key):
            return False

        return True

    def export_to_nano_banana(self) -> bool:
        """
        Export to Nano Banana
        =====================

        Export the first frame of the first selected Clip or Sequence to the Nano Banana Prompt.
        An earlier export of the same clip is overwritten.

        Returns
        -------
            exported (bool): True if the frame was exported, False if the export failed.
        """

        pyflame.print('Exporting to Nano Banana...')

        export_preset_path = f'{SCRIPT_PATH}/assets/export_preset/PNG (8-bit) Nano Banana.xml'
        print('Export Preset Path:', export_preset_path, '\n')

        # Set version of export preset to match current version of Flame to avoid error windows.
        pyflame.update_export_preset(export_preset_path)

        # Resolved image export path
        image_export_path = self.images_path
        print('Image Export Path:', image_export_path)

        # Get exportedimage path
        self.exported_image_path = os.path.join(image_export_path, self.selection[0].name + '.png')
        print('Exported Image Path:', self.exported_image_path, '\n')

        try:
            # Create images folder on first use, the exporter fails if it's missing
            os.makedirs(image_export_path, exist_ok=True)

            # Remove an earlier export of this clip so Flame doesn't open a blocking file exists dialog
            if os.path.isfile(self.exported_image_path):
                os.remove(self.exported_image_path)

            # Initialize Exporter
            exporter = flame.PyExporter()
            exporter.foreground = True

            # Export first frame of the first selected clip only
            exporter.export([self.selection[0]], export_preset_path, image_export_path)
        except Exception as e:
            pyflame.print(f'Export failed: {e}', print_type=PrintType.ERROR)
            PyFlameMessageWindow(
                message=f'Unable to export the selected clip to Nano Banana.\n\n{e}\n\nThe window will open with no prompt image.',
                message_type=MessageType.ERROR,
                parent=None,
                )
            return False

        pyflame.print('Image exported to Nano Banana.')

        return True

    def nano_banana(self) -> None:

        def bananas() -> None:
            """
            Bananas
            ========

            Display a random banana message on startup.
            """

            # Display a random banana message
            bananas_path = os.path.join(SCRIPT_PATH, 'assets', 'bananas.txt')
            with open(bananas_path, 'r') as f:
                lines = [line.strip() for line in f if line.strip()]
            self.banana_message_entry.text = random.choice(lines)

        def save_settings() -> None:
            """
            Save Settings
            =============

            Save settings to file.
            """

            self.settings.save_config(
                config_values={
                    'model': self.select_model_menu.text,
                    'resolution': self.image_resolution_menu.text,
                    'aspect_ratio': self.aspect_ratio_menu.text,
                    'thinking_level': self.thinking_level_menu.text,
                    }
                )

        def request_failed(message: str, status: str) -> None:
            """
            Request Failed
            ==============

            Replace the wait message in the status line and show the error.

            Args
            ----
                message (str):
                    Error message to show.

                status (str):
                    Short failure message for the status line.
            """

            self.banana_message_entry.text = status
            pyflame.print(status, print_type=PrintType.ERROR)
            PyFlameMessageWindow(
                message=message,
                message_type=MessageType.ERROR,
                parent=self.main_window,
                )

        def request_too_large(payload: bytes, image_path: str | None, status: str) -> bool:
            """
            Request Too Large
            =================

            Check the encoded request against Google's request size limit. Show an error if it's over.

            Args
            ----
                payload (bytes):
                    Encoded request body.

                image_path (str | None):
                    Prompt image sent with the request, if any.

                status (str):
                    Short failure message for the status line.

            Returns
            -------
                too_large (bool): True if the request is over the limit and should not be sent.
            """

            if len(payload) <= MAX_REQUEST_BYTES:
                return False

            mb = 1024 * 1024
            message = f'The request is too large to send ({len(payload) / mb:.1f} MB). Google\'s limit is {MAX_REQUEST_BYTES // mb} MB.'
            if image_path:
                message += f'\n\nPrompt image: {os.path.basename(image_path)} ({os.path.getsize(image_path) / mb:.1f} MB). Images are about a third larger once encoded.'
            message += '\n\nUse a smaller prompt image or a lower resolution image.'
            request_failed(message, status)

            return True

        def get_no_response_reason(result: dict) -> str:
            """
            Get No Response Reason
            ======================

            Get the reason Google gave for returning nothing: the prompt block reason and/or the candidate's finish reason.

            Args
            ----
                result (dict): Decoded API response.

            Returns
            -------
                reason (str): Reason lines, or an empty string if no reason was given.
            """

            reasons = []

            prompt_feedback = result.get('promptFeedback')
            if isinstance(prompt_feedback, dict) and prompt_feedback.get('blockReason'):
                reasons.append(f'Block reason: {prompt_feedback["blockReason"]}')

            # STOP is a normal finish, so it doesn't explain a missing result
            candidates = result.get('candidates') or []
            finish_reason = None
            if candidates and isinstance(candidates[0], dict):
                finish_reason = candidates[0].get('finishReason')
            if finish_reason and finish_reason != 'STOP':
                reasons.append(f'Finish reason: {finish_reason}')

            return '\n'.join(reasons)

        def get_response_parts(result: dict) -> list:
            """
            Get Response Parts
            ==================

            Get the content parts of the first candidate in the API response. Parts that aren't dicts are skipped.

            Args
            ----
                result (dict): Decoded API response.

            Returns
            -------
                parts (list): Content parts, or an empty list if there are no candidates.
            """

            candidates = result.get('candidates') or []
            if not candidates or not isinstance(candidates[0], dict):
                return []

            content = candidates[0].get('content')
            if not isinstance(content, dict) or not isinstance(content.get('parts'), list):
                return []

            return [part for part in content['parts'] if isinstance(part, dict)]

        def prompt_image_missing(status: str) -> bool:
            """
            Prompt Image Missing
            ====================

            Check that the prompt image file still exists. If it was moved or deleted outside the script,
            show an error naming the file, clear the prompt image and set the status line.

            Args
            ----
                status (str): Short failure message for the status line.

            Returns
            -------
                missing (bool): True if the prompt image file is gone and nothing should be sent.
            """

            image_path = self.prompt_image_widget.image_path
            if not self.prompt_image_widget.has_image or not image_path or os.path.isfile(image_path):
                return False

            self.prompt_image_widget.image = None
            request_failed(f'Prompt image not found:\n\n{image_path}\n\nIt was moved or deleted. The prompt image has been cleared.', status)

            return True

        def send_prompt() -> None:
            """
            Send Prompt
            ==========

            Send prompt text to the Nano Banana API and save the
            returned image to the images folder.
            """

            # Get prompt text
            prompt_text = self.prompt_text_edit.text_str.strip()
            if not prompt_text:
                PyFlameMessageWindow(
                    message='Please enter a prompt before sending.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            # Prompt image moved or deleted outside the script
            if prompt_image_missing('Prompt not sent.'):
                return

            pyflame.print('Sending prompt... Please wait...')
            self.banana_message_entry.text = 'Sending prompt... Please wait...'
            pyflame.pause()

            selected_model = self.select_model_menu.text
            selected_model = selected_model.rsplit(' (', 1)[0].strip()
            print('Selected Model:', selected_model)

            url = (
                'https://generativelanguage.googleapis.com/v1beta/'
                f'models/{selected_model}:generateContent?key={self.settings.api_key}'
            )

            parts: list[dict[str, Any]] = [{'text': prompt_text}]

            image_path = None
            if self.prompt_image_widget.has_image and self.prompt_image_widget.image_path:
                image_path = self.prompt_image_widget.image_path
                # Send the prompt image with the type that matches the file
                mime = PROMPT_IMAGE_MIME_TYPES.get(os.path.splitext(image_path)[1].lower())
                if not mime:
                    request_failed(f'Prompt image type not supported:\n\n{os.path.basename(image_path)}\n\nUse a PNG or JPEG image.', 'Prompt not sent.')
                    return
                try:
                    with open(image_path, 'rb') as img_file:
                        img_b64 = base64.b64encode(img_file.read()).decode()
                except OSError as e:
                    request_failed(f'Unable to read the prompt image:\n\n{image_path}\n\n{e}', 'Prompt not sent.')
                    return
                parts.append({
                        'inlineData': {
                        'mimeType': mime,
                        'data': img_b64,
                    }
                })

            aspect_ratio = self.aspect_ratio_menu.text.strip() or '1:1'
            image_size = self.image_resolution_menu.text.strip().upper() or '1K'

            image_config = {
                'aspectRatio': aspect_ratio,
                'imageSize': image_size,
                }

            # Bump timeout to 180s to safely accommodate 4K generation on Pro.
            request_timeout = 180

            generation_config = {
                'responseModalities': ['TEXT', 'IMAGE'],
                'imageConfig': image_config,
            }

            # Pro thinks at a level that can't be set, so only send a thinking level for models that take one
            if IMAGE_MODELS[self.select_model_menu.text]['thinking_levels']:
                generation_config['thinkingConfig'] = {
                    'thinkingLevel': self.thinking_level_menu.text.upper(),
                    }

            payload = json.dumps({
                'contents': [{'parts': parts}],
                'generationConfig': generation_config,
            }).encode()

            # Don't send a request Google will reject for size (it would still be uploaded first)
            if request_too_large(payload, image_path, 'Prompt not sent.'):
                return

            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )

            try:
                with urllib.request.urlopen(req, timeout=request_timeout, context=SSL_CONTEXT) as response:
                    result = json.loads(response.read().decode())
                if not isinstance(result, dict):
                    raise ValueError('Response is not a JSON object.')
            except urllib.error.HTTPError as e:
                # Read error body for Google's error message
                try:
                    err_body = e.read().decode()
                    err_json = json.loads(err_body)
                    err_detail = err_json.get('error', {}).get('message', err_body)
                except Exception:
                    err_detail = str(e)
                request_failed(f'Nano Banana API request failed (HTTP {e.code}).\n\n{err_detail}', 'Prompt failed.')
                return
            except (ValueError, http.client.HTTPException) as e:
                request_failed(f'Invalid response from the Nano Banana API.\n\n{e}\n\nPlease try again.', 'Prompt failed.')
                return
            except (urllib.error.URLError, OSError):
                request_failed('Unable to reach the Nano Banana API.\n\nPlease check your internet connection and try again.', 'Prompt failed.')
                return

            response_parts = get_response_parts(result)

            # Capture both text and image from the response.
            # The model sometimes returns a text description alongside the image.
            image_data = None
            mime_type = None
            model_text = []

            for part in response_parts:
                if part.get('text'):
                    model_text.append(part['text'])
                inline = part.get('inlineData')
                if isinstance(inline, dict) and not image_data:
                    image_data = inline.get('data')
                    mime_type = inline.get('mimeType', 'image/png')

            # Log any text the model returned alongside the image.
            combined = ' '.join(model_text)
            if combined:
                pyflame.print(f'Model: {combined}')

            # Show why no image came back: block/finish reason and any returned text
            if not image_data:
                message = 'No image was returned from the Nano Banana API.'
                reason = get_no_response_reason(result)
                if reason:
                    message += f'\n\n{reason}'
                if combined:
                    message += f'\n\nModel response: {combined}'
                message += '\n\nTry a different prompt.'
                request_failed(message, 'No image returned.')
                return

            # PNG and JPEG are saved as they are. Flame can't read WebP, so any other type is converted to PNG.
            mime = (mime_type or 'image/png').lower()
            try:
                image_bytes = base64.b64decode(image_data)

                converted_image = None
                if mime == 'image/png':
                    ext = '.png'
                elif mime == 'image/jpeg':
                    ext = '.jpg'
                else:
                    ext = '.png'
                    converted_image = QtGui.QImage()
                    if not converted_image.loadFromData(image_bytes):
                        raise ValueError(f'Unable to decode the returned {mime} image.')

                from datetime import datetime
                stem = f'nano_banana_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
                save_path = os.path.join(self.images_path, f'{stem}{ext}')

                # Never overwrite an earlier result saved in the same second: add _1, _2... until the name is free
                count = 0
                while os.path.exists(save_path):
                    count += 1
                    save_path = os.path.join(self.images_path, f'{stem}_{count}{ext}')

                os.makedirs(self.images_path, exist_ok=True)

                if converted_image is not None:
                    if not converted_image.save(save_path, 'PNG'):
                        raise OSError(f'Unable to write {save_path}')
                else:
                    with open(save_path, 'wb') as f:
                        f.write(image_bytes)
            except Exception as e:
                request_failed(f'Unable to save the returned image.\n\n{e}', 'Image not saved.')
                return

            pyflame.print(f'Image saved: {save_path}')

            self.banana_message_entry.text = combined or 'Image generated successfully.'

            self.banana_image_widget.image = save_path

            self.image_gallery.refresh()

            history_cursor = self.prompt_history_text_edit.textCursor()
            history_cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

            # Add separator if there is existing content.
            if self.prompt_history_text_edit.document().characterCount() > 1:
                history_cursor.insertBlock()
                history_cursor.insertText('\n')

            # Append prompt text as right-aligned user input.
            history_cursor.insertBlock()
            history_fmt = QtGui.QTextBlockFormat()
            history_fmt.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
            history_cursor.mergeBlockFormat(history_fmt)
            history_cursor.insertText(prompt_text)
            self.prompt_history_text_edit.setTextCursor(history_cursor)
            self.prompt_text_edit.text_str = ''
            self.prompt_image_widget.image = save_path

        def send_message() -> None:
            """
            Send Message
            ============

            Send a text prompt to Gemini and display the text response in the
            prompt text edit. If prompt_image_widget has an image, it is sent
            along with the message (e.g. for "describe this image" or "improve
            this prompt based on the image").
            """

            def append_gemini_response_to_prompt(text_edit: PyFlameTextEdit, user_text: str, gemini_text: str) -> None:
                """
                Append a user message and Gemini response to the history text edit.
                The user message is right-aligned and the Gemini response is left-aligned.
                """
                cursor = text_edit.textCursor()
                cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)

                # Add separator if there is existing content.
                if text_edit.document().characterCount() > 1:
                    cursor.insertBlock()
                    cursor.insertText('\n')

                # Append user message (right-aligned).
                cursor.insertBlock()
                fmt = QtGui.QTextBlockFormat()
                fmt.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
                cursor.mergeBlockFormat(fmt)
                cursor.insertText(user_text)

                # Add a blank line after the user prompt.
                cursor.insertBlock()

                # Append Gemini response (left-aligned).
                cursor.insertBlock()
                fmt = QtGui.QTextBlockFormat()
                fmt.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
                cursor.mergeBlockFormat(fmt)
                cursor.insertText(gemini_text)

                text_edit.setTextCursor(cursor)

            model = CHAT_MODEL

            # ---- Validate prompt text ----
            prompt_text = self.prompt_text_edit.text_str.strip()
            if not prompt_text:
                PyFlameMessageWindow(
                    message='Please enter a message before sending.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                )
                return

            # Prompt image moved or deleted outside the script
            if prompt_image_missing('Message not sent.'):
                return

            # ---- Show wait state ----
            pyflame.print('Sending message... Please wait...')
            self.banana_message_entry.text = 'Sending message... Please wait...'
            pyflame.pause()

            # ---- Build API URL for the requested text model ----
            url = (
                'https://generativelanguage.googleapis.com/v1beta/'
                f'models/{model}:generateContent?key={self.settings.api_key}'
            )

            # ---- Inject scope guard so responses stay prompt-focused ----
            prompt_scope_instruction = (
                'You are a prompt-writing assistant for image generation. '
                'Stay strictly focused on helping the user write, improve, or analyze '
                'image prompts and image descriptions. '
                'If asked about unrelated topics, briefly refuse and redirect to prompt help. '
                'Keep responses concise, actionable, and on-subject.'
            )

            # ---- Build request parts: fixed instruction, user text, then optional image ----
            parts: list[dict[str, Any]] = [
                {'text': prompt_scope_instruction},
                {'text': f'User request:\n{prompt_text}'},
            ]

            # Include the prompt image if present (for image-aware responses)
            image_path = None
            if self.prompt_image_widget.has_image and self.prompt_image_widget.image_path:
                image_path = self.prompt_image_widget.image_path
                # Send the prompt image with the type that matches the file
                mime = PROMPT_IMAGE_MIME_TYPES.get(os.path.splitext(image_path)[1].lower())
                if not mime:
                    request_failed(f'Prompt image type not supported:\n\n{os.path.basename(image_path)}\n\nUse a PNG or JPEG image.', 'Message not sent.')
                    return
                try:
                    with open(image_path, 'rb') as img_file:
                        img_b64 = base64.b64encode(img_file.read()).decode()
                except OSError as e:
                    request_failed(f'Unable to read the prompt image:\n\n{image_path}\n\n{e}', 'Message not sent.')
                    return
                parts.append({
                    'inlineData': {
                        'mimeType': mime,
                        'data': img_b64,
                    }
                })

            # ---- Build payload: text-only generation config (no image output) ----
            # Gemini API expects "role" and "parts" in each content object.
            payload = json.dumps({
                'contents': [{'role': 'user', 'parts': parts}],
                'generationConfig': {
                    'temperature': 0.7,
                },
            }).encode()

            # ---- Don't send a request Google will reject for size ----
            if request_too_large(payload, image_path, 'Message not sent.'):
                return

            # ---- Send request ----
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            try:
                with urllib.request.urlopen(req, timeout=60, context=SSL_CONTEXT) as response:
                    result = json.loads(response.read().decode())
                if not isinstance(result, dict):
                    raise ValueError('Response is not a JSON object.')
            except urllib.error.HTTPError as e:
                # Read error body for more specific feedback (400 often has useful details)
                try:
                    err_body = e.read().decode()
                    err_json = json.loads(err_body)
                    err_detail = err_json.get('error', {}).get('message', err_body)
                except Exception:
                    err_detail = str(e)
                request_failed(f'Nano Banana API request failed (HTTP {e.code}).\n\n{err_detail}', 'Message failed.')
                return
            except (ValueError, http.client.HTTPException) as e:
                request_failed(f'Invalid response from the Nano Banana API.\n\n{e}\n\nPlease try again.', 'Message failed.')
                return
            except (urllib.error.URLError, OSError):
                request_failed('Unable to reach the Nano Banana API.\n\nPlease check your internet connection and try again.', 'Message failed.')
                return

            # ---- Extract text from response (expect text, not image) ----
            response_parts = get_response_parts(result)
            gemini_text = ' '.join(p.get('text', '') for p in response_parts if p.get('text')).strip()

            # ---- Check for an empty reply before adding the prefix ----
            if not gemini_text:
                message = 'No text response from the Nano Banana API.'
                reason = get_no_response_reason(result)
                if reason:
                    message += f'\n\n{reason}'
                message += '\n\nTry a different message.'
                request_failed(message, 'No text response.')
                return

            response_text = 'Gemini: ' + gemini_text

            # ---- Append user message (right-aligned) and Gemini response (left-aligned) to history ----
            append_gemini_response_to_prompt(self.prompt_history_text_edit, prompt_text, response_text)
            self.prompt_text_edit.text_str = ''
            self.banana_message_entry.text = 'Message received.'
            pyflame.print('Message received.')

        def run_request(request) -> None:
            """
            Run Request
            ===========

            Run send_prompt or send_message with Send Prompt and Gemini Chat disabled, so a double click,
            a click queued during pyflame.pause() or Return can't send a second paid request.
            The buttons are always enabled again when the request ends.

            Args
            ----
                request (callable): send_prompt or send_message.
            """

            # Another request is still running, do nothing
            if self.request_running:
                return

            self.request_running = True
            self.send_prompt_button.enabled = False
            self.send_message_button.enabled = False

            try:
                request()

                # Drop clicks and key presses queued during the blocking request while it still counts as running
                QtWidgets.QApplication.processEvents()
            finally:
                self.request_running = False
                self.send_prompt_button.enabled = True
                self.send_message_button.enabled = True

        def clear_prompt_image() -> None:
            """
            Clear Prompt Image
            ==================

            Clear the image from the prompt image widget.
            """

            self.prompt_image_widget.image = None

        def import_to_flame() -> None:
            """
            Import to Flame
            ================

            Import the image currently displayed in the banana image widget
            into the media panel library.
            """

            pyflame.print('Importing image to Flame...')

            # Get the image path
            image_path = self.banana_image_widget.image_path

            # Check if images exists, if not, return.
            if image_path is None or not os.path.isfile(image_path):
                return

            # Get the workspace
            workspace = flame.project.current_project.current_workspace

            # Check if the Nano Banana library exists, if not, create it.
            nano_banana_lib = None
            for lib in workspace.libraries:
                if str(lib.name)[1:-1] == SCRIPT_NAME:
                    nano_banana_lib = lib
                    break

            if not nano_banana_lib:
                nano_banana_lib = workspace.create_library(SCRIPT_NAME)

            # Expand the Nano Banana library.
            nano_banana_lib.expanded = True

            # Import the image to the Nano Banana library.
            flame.import_clips(image_path, nano_banana_lib)

            pyflame.print(f'Imported to Flame: {os.path.basename(image_path)}')

        def send_to_prompt() -> None:
            """
            Send to Banana
            ==============

            Send selected gallery image to the Nano Banana image widget.
            """

            path = self.image_gallery.selected_path
            if path is None:
                PyFlameMessageWindow(
                    message='No image selected.\n\nPlease select an image in the gallery first.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            self.prompt_image_widget.image = path

        def reveal_in_finder() -> None:
            """
            Reveal in Finder
            ================

            Open the image library folder in Finder.
            """

            # Create images folder if it doesn't exist yet so there is something to open
            try:
                os.makedirs(self.images_path, exist_ok=True)
            except Exception as e:
                PyFlameMessageWindow(
                    message=f'Unable to create the images folder:\n\n{self.images_path}\n\n{e}',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            pyflame.open_in_finder(self.images_path)

            pyflame.print(f'Finder opened: {self.images_path}')

        def reveal_in_mediahub() -> None:
            """
            Reveal in MediaHub
            ==================

            Reveal image in mediahub.
            """

            # Create images folder if it doesn't exist yet, MediaHub rejects a missing path
            try:
                os.makedirs(self.images_path, exist_ok=True)

                # Switch to MediaHub tab
                flame.go_to('MediaHub')

                # Set path in MediaHub
                flame.mediahub.files.set_path(self.images_path)
            except Exception as e:
                PyFlameMessageWindow(
                    message=f'Unable to reveal the images folder in MediaHub:\n\n{self.images_path}\n\n{e}',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            pyflame.print(f'MediaHub opened: {self.images_path}')

        def delete_image() -> None:
            """
            Delete Image
            ============

            Delete selected gallery image from the file system.
            """

            path = self.image_gallery.selected_path
            if path is None:
                return

            # File was already removed outside the script: clear anything showing it and refresh the gallery
            if not os.path.isfile(path):
                if self.banana_image_widget.image_path and os.path.abspath(self.banana_image_widget.image_path) == os.path.abspath(path):
                    self.banana_image_widget.image = None
                if self.prompt_image_widget.image_path and os.path.abspath(self.prompt_image_widget.image_path) == os.path.abspath(path):
                    self.prompt_image_widget.image = None
                self.image_gallery.refresh()
                PyFlameMessageWindow(
                    message=f'Image was already removed:\n\n{os.path.basename(path)}',
                    parent=self.main_window,
                    )
                return

            confirmed = PyFlameMessageWindow(
                message=f'Are you sure you want to delete:\n\n{os.path.basename(path)}',
                message_type=MessageType.WARNING,
                parent=self.main_window,
                )
            if not confirmed:
                return

            def _is_displayed(widget_path: str | None) -> bool:
                return (
                    widget_path is not None
                    and os.path.exists(widget_path)
                    and os.path.samefile(path, widget_path)
                )

            banana_displayed = _is_displayed(self.banana_image_widget.image_path)
            prompt_displayed = _is_displayed(self.prompt_image_widget.image_path)

            try:
                os.remove(path)
            except OSError:
                PyFlameMessageWindow(
                    message=f'Failed to delete image:\n\n{os.path.basename(path)}',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            pyflame.print(f'Deleted: {path}')

            if banana_displayed:
                self.banana_image_widget.image = None
            if prompt_displayed:
                self.prompt_image_widget.image = None

            self.image_gallery.refresh()

        def done() -> None:
            """
            Done
            ====

            Done button clicked.
            """

            # Save settings
            save_settings()

            # Close window
            close_window()

            print('Done.\n\n')

        def close_window() -> None:

            self.main_window.close()

        # ------------------------------------------------------------------------------

        # True while send_prompt or send_message is running
        self.request_running = False

        self.main_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            parent=None,
            escape_pressed=close_window,
            grid_layout_columns=12,
            grid_layout_rows=22,
            grid_layout_adjust_column_widths={
                3:50,
                8:50,
                },
            )

        # Labels
        self.prompt_label = PyFlameLabel(
            text='Prompt',
            style=Style.UNDERLINE,
            )
        self.banana_image_label = PyFlameLabel(
            text='Nano Banana Image',
            style=Style.UNDERLINE,
            )
        self.prompt_image_widget_label = PyFlameLabel(
            text='Prompt Image',
            style=Style.UNDERLINE,
            )
        self.image_gallery_label = PyFlameLabel(
            text='Image Gallery',
            style=Style.UNDERLINE,
            )
        self.select_model_label = PyFlameLabel(
            text='Select Model',
            )
        self.resolution_label = PyFlameLabel(
            text='Resolution',
            )
        self.aspect_ratio_label = PyFlameLabel(
            text='Aspect Ratio',
            )
        self.thinking_level_label = PyFlameLabel(
            text='Thinking Level',
            )

        # Entries
        self.banana_message_entry = PyFlameEntry(
            text='',
            read_only=True,
            )
        self.images_path_entry = PyFlameEntry(
            text=self.images_path,
            read_only=True,
            )

        # Image Widgets
        self.banana_image_widget = PyFlameImageWidget(
            image=None,
            show_info=True,
            )
        self.prompt_image_widget = PyFlameImageWidget(
            image=None,
            show_info=True,
            )

        # Image Gallery
        self.image_gallery = PyFlameImageGallery(
            folder=self.images_path,
            extensions=list(PROMPT_IMAGE_MIME_TYPES),
            columns=4,
            show_info=True,
            image_selected=lambda path: setattr(self.banana_image_widget, 'image', path),
            )

        # Text Edits
        self.prompt_text_edit = PyFlameTextEdit(
            text='',
            )
        self.prompt_history_text_edit = PyFlameTextEdit(
            text='',
            text_style=TextStyle.READ_ONLY_SELECTABLE,
            )

        # Return/Enter in the prompt field sends the prompt, Shift+Return adds a new line.
        # Return anywhere else in the window sends nothing, so it can't send a paid request by accident.
        self.prompt_return_filter = PromptReturnFilter(self.prompt_text_edit, lambda: run_request(send_prompt))
        self.prompt_text_edit.installEventFilter(self.prompt_return_filter)

        def update_resolution_menu_for_model() -> None:
            """
            Update Resolution Menu for Model
            ================================

            When the selected model changes, set image_resolution_menu and aspect_ratio_menu options
            to the new model's options and reset both to the model's first option. The thinking level
            is reset to the new model's default.
            """

            # Picking the same model again keeps the current resolution, aspect ratio and thinking level
            selected_model = self.select_model_menu.text
            if selected_model == self.menu_model:
                return
            self.menu_model = selected_model

            model_options = IMAGE_MODELS[selected_model]

            resolution_options = model_options['resolutions']
            aspect_ratio_options = model_options['aspect_ratios']

            self.image_resolution_menu.menu_options = resolution_options
            self.image_resolution_menu.text = resolution_options[0]
            self.aspect_ratio_menu.menu_options = aspect_ratio_options
            self.aspect_ratio_menu.text = aspect_ratio_options[0]
            update_thinking_menu(model_options, model_options['default_thinking_level'])

        def update_thinking_menu(model_options: dict, thinking_level: str | None) -> None:
            """
            Update Thinking Menu
            ====================

            Set thinking_level_menu options for a model. Use the model's default if thinking_level isn't valid for it.
            For a model whose thinking level can't be set (Pro), disable the menu and show Always On.

            Args
            ----
                model_options (dict):
                    Model entry from IMAGE_MODELS.

                thinking_level (str | None):
                    Thinking level to show.
            """

            thinking_levels = model_options['thinking_levels']

            if not thinking_levels:
                self.thinking_level_menu.menu_options = [THINKING_ALWAYS_ON]
                self.thinking_level_menu.text = THINKING_ALWAYS_ON
                self.thinking_level_menu.enabled = False
                return

            if thinking_level not in thinking_levels:
                thinking_level = model_options['default_thinking_level']

            self.thinking_level_menu.menu_options = thinking_levels
            self.thinking_level_menu.text = thinking_level
            self.thinking_level_menu.enabled = True

        # Saved model's options, load_config already replaced an unknown model with the default.
        # Use the model's first option if a saved value isn't valid for that model.
        self.menu_model = self.settings.model
        model_options = IMAGE_MODELS[self.menu_model]
        resolution = self.settings.resolution if self.settings.resolution in model_options['resolutions'] else model_options['resolutions'][0]
        aspect_ratio = self.settings.aspect_ratio if self.settings.aspect_ratio in model_options['aspect_ratios'] else model_options['aspect_ratios'][0]

        # Menus
        self.select_model_menu = PyFlameMenu(
            text=self.settings.model,
            menu_options=list(IMAGE_MODELS),
            connect=update_resolution_menu_for_model,
            )
        self.image_resolution_menu = PyFlameMenu(
            text=resolution,
            menu_options=model_options['resolutions'],
            )
        self.aspect_ratio_menu = PyFlameMenu(
            text=aspect_ratio,
            menu_options=model_options['aspect_ratios'],
            )
        self.thinking_level_menu = PyFlameMenu(
            text='',
            )

        # Saved thinking level, or the model's default if it isn't valid for that model
        update_thinking_menu(model_options, self.settings.thinking_level)

        # Buttons
        self.done_button = PyFlameButton(
            text='Done',
            connect=done,
            )
        self.send_prompt_button = PyFlameButton(
            text='Send Prompt',
            connect=lambda: run_request(send_prompt),
            color=Color.BLUE,
            tooltip='Send prompt to create an image with Nano Banana',
            )
        self.send_message_button = PyFlameButton(
            text='Gemini Chat',
            connect=lambda: run_request(send_message),
            tooltip='Send message to chat with Gemini about creating an image',
            )
        self.clear_prompt_image_button = PyFlameButton(
            text='Clear Prompt Image',
            connect=clear_prompt_image,
            )
        self.import_to_flame_button = PyFlameButton(
            text='Import to Flame',
            connect=import_to_flame,
            )
        self.send_to_prompt_button = PyFlameButton(
            text='Send to Prompt',
            connect=send_to_prompt,
            )
        self.reveal_in_finder_button = PyFlameButton(
            text='Reveal in Finder',
            connect=reveal_in_finder,
            )
        self.reveal_in_mediahub_button = PyFlameButton(
            text='Reveal in MediaHub',
            connect=reveal_in_mediahub,
            )
        self.delete_button = PyFlameButton(
            text='Delete Image',
            connect=delete_image,
            )
        self.change_path_button = PyFlameButton(
            text='Change Path',
            connect=self.path_selection,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.main_window.grid_layout.addWidget(self.image_gallery_label, 0, 0, 1, 3)
        self.main_window.grid_layout.addWidget(self.image_gallery, 1, 0, 17, 3)

        self.main_window.grid_layout.addWidget(self.reveal_in_finder_button, 18, 0)
        self.main_window.grid_layout.addWidget(self.reveal_in_mediahub_button, 19, 0)
        self.main_window.grid_layout.addWidget(self.import_to_flame_button, 18, 1)
        self.main_window.grid_layout.addWidget(self.delete_button, 19, 1)
        self.main_window.grid_layout.addWidget(self.send_to_prompt_button, 18, 2)
        self.main_window.grid_layout.addWidget(self.clear_prompt_image_button, 19, 2)
        self.main_window.grid_layout.addWidget(self.images_path_entry, 20, 0, 1, 3)
        self.main_window.grid_layout.addWidget(self.change_path_button, 21, 0)

        self.main_window.grid_layout.addWidget(self.prompt_label, 0, 4, 1, 4)
        self.main_window.grid_layout.addWidget(self.prompt_history_text_edit, 1, 4, 5, 4)
        self.main_window.grid_layout.addWidget(self.prompt_text_edit, 6, 4, 3, 4)
        self.main_window.grid_layout.addWidget(self.send_message_button, 9, 7)

        self.main_window.grid_layout.addWidget(self.prompt_image_widget_label, 10, 4, 1, 4)
        self.main_window.grid_layout.addWidget(self.prompt_image_widget, 11, 4, 7, 4)

        self.main_window.grid_layout.addWidget(self.select_model_label, 18, 4)
        self.main_window.grid_layout.addWidget(self.select_model_menu, 18, 5, 1, 3)

        self.main_window.grid_layout.addWidget(self.resolution_label, 19, 4)
        self.main_window.grid_layout.addWidget(self.image_resolution_menu, 19, 5)
        self.main_window.grid_layout.addWidget(self.aspect_ratio_label, 19, 6)
        self.main_window.grid_layout.addWidget(self.aspect_ratio_menu, 19, 7)

        self.main_window.grid_layout.addWidget(self.thinking_level_label, 20, 4)
        self.main_window.grid_layout.addWidget(self.thinking_level_menu, 20, 5)

        self.main_window.grid_layout.addWidget(self.banana_image_label, 0, 9, 1, 3)
        self.main_window.grid_layout.addWidget(self.banana_image_widget, 1, 9, 17, 3)
        self.main_window.grid_layout.addWidget(self.banana_message_entry, 18, 9, 1, 3)

        self.main_window.grid_layout.addWidget(self.send_prompt_button, 21, 7)
        self.main_window.grid_layout.addWidget(self.done_button, 21, 11)

        # ------------------------------------------------------------------------------

        # Set window focus to prompt text edit
        self.prompt_text_edit.set_focus()

        # Add imported image to prompt image widget if image is selected from Flame
        if self.flame_image_exported:
            self.prompt_image_widget.image = self.exported_image_path

        NanoBanana.open_window = self

        bananas()

    @staticmethod
    def get_open_window():
        """
        Get Open Window
        ===============

        Get the Nano Banana instance whose main window is open.

        Returns
        -------
            open_window (NanoBanana | None): Instance with an open main window, or None if there isn't one.
        """

        # A closed window is deleted, so isVisible raises RuntimeError
        try:
            if NanoBanana.open_window and NanoBanana.open_window.main_window.isVisible():
                return NanoBanana.open_window
        except (AttributeError, RuntimeError):
            pass

        return None

    def path_selection(self) -> None:
        """
        Path Selection
        ==============

        Path selection window for changing the images path from the main window.
        """

        # Bring open window to front instead of opening a second one. A closed window is deleted, so isVisible raises RuntimeError.
        try:
            if self.path_selection_window.isVisible():
                self.path_selection_window.raise_()
                self.path_selection_window.activateWindow()
                return
        except (AttributeError, RuntimeError):
            pass

        def browse_images_path() -> None:
            """
            Browse Images Path
            ==================

            Open Flame file browser to select images path.
            """

            images_path = pyflame.file_browser(
                path=self.path_selection_entry.text,
                title='Select Images Path',
                select_directory=True,
                window_to_hide=[self.main_window, self.path_selection_window],
                )

            if images_path:
                self.path_selection_entry.text = str(images_path)

        def save_path() -> None:
            """
            Save Path
            =========

            Save images path to config file and update the main window. Keep the old path if the entry is blank.
            """

            tokenized_path = self.path_selection_entry.text.strip()

            # Keep old path if entry is blank
            if not tokenized_path:
                self.path_selection_window.close()
                return

            # Save tokenized path so the token is what gets saved
            old_tokenized_path = self.settings.images_path
            try:
                # Resolve before saving so a path that can't be resolved saves nothing
                pyflame.resolve_tokens(tokenized_string=tokenized_path)

                self.settings.save_config(
                    config_values={
                        'images_path': tokenized_path,
                        }
                    )
            except Exception as e:
                # Put old path back so a later save doesn't write the new one
                self.settings.images_path = old_tokenized_path
                PyFlameMessageWindow(
                    message=f'Unable to save the images path:\n\n{tokenized_path}\n\n{e}',
                    message_type=MessageType.ERROR,
                    parent=self.path_selection_window,
                    )
                return

            self.set_images_path(tokenized_path)

            self.path_selection_window.close()

        def close_window() -> None:

            self.path_selection_window.close()

        # ------------------------------------------------------------------------------

        self.path_selection_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Path Selection <small>{SCRIPT_VERSION}',
            parent=None,
            return_pressed=save_path,
            escape_pressed=close_window,
            grid_layout_columns=6,
            grid_layout_rows=3,
            window_margins=15,
            )

        # Labels
        self.path_selection_label = PyFlameLabel(
            text='Images Path',
            )

        # Entries
        self.path_selection_entry = PyFlameEntry(
            text=self.settings.images_path,
            )

        # Menus
        self.path_selection_token_menu = PyFlameTokenMenu(
            token_dest=self.path_selection_entry,
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                }
            )

        # Buttons
        self.path_selection_browse_button = PyFlameButton(
            text='Browse',
            color=Color.GRAY,
            connect=browse_images_path,
            )
        self.path_selection_cancel_button = PyFlameButton(
            text='Cancel',
            color=Color.GRAY,
            connect=close_window,
            )
        self.path_selection_save_button = PyFlameButton(
            text='Save',
            color=Color.BLUE,
            connect=save_path,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.path_selection_window.grid_layout.addWidget(self.path_selection_label, 0, 0)
        self.path_selection_window.grid_layout.addWidget(self.path_selection_entry, 0, 1, 1, 3)
        self.path_selection_window.grid_layout.addWidget(self.path_selection_browse_button, 0, 4)
        self.path_selection_window.grid_layout.addWidget(self.path_selection_token_menu, 0, 5)
        self.path_selection_window.grid_layout.addWidget(self.path_selection_cancel_button, 2, 4)
        self.path_selection_window.grid_layout.addWidget(self.path_selection_save_button, 2, 5)

        self.path_selection_entry.set_focus()

    def set_images_path(self, tokenized_path: str) -> None:
        """
        Set Images Path
        ===============

        Update the main window with a new images path: settings, path field and gallery.

        Args
        ----
            tokenized_path (str): New images path, may contain tokens.
        """

        images_path = pyflame.resolve_tokens(tokenized_string=tokenized_path)

        # Keep settings tokenized so a later Done saves the token, not this project's path
        self.settings.images_path = tokenized_path
        self.images_path = images_path
        self.images_path_entry.text = self.images_path
        self.image_gallery.folder = self.images_path

        # Setting the folder doesn't rebuild the thumbnails, so refresh to show the new folder's images
        self.image_gallery.refresh()

        pyflame.print(f'Images Path: {self.images_path}')

class NanoBananaSetup:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME}: Setup {SCRIPT_VERSION}')

        if not os.path.isfile(os.path.join(SCRIPT_PATH, 'config/config.json')):
            PyFlameMessageWindow(
                message='Running this script will incur charges to your Nano Banana account.\n\nPlease review your usage limits and pricing plan before proceeding.',
                parent=None,
                )

        # Create/Load config file settings.
        self.settings = load_config()

        # Verify Internet Connection
        if not verify_internet_connection():
            return

        # Open setup window
        self.nano_banana_setup()

    def nano_banana_setup(self) -> None:
        """
        Nano Banana Setup
        =================

        Setup window for Nano Banana.
        """

        def browse_images_path() -> None:
            """
            Browse Images Path
            ==================

            Open Flame file browser to select images path.
            """

            # Also hide an open Nano Banana window, Flame's file browser opens behind Qt windows
            windows_to_hide = []
            nano_banana = NanoBanana.get_open_window()
            if nano_banana:
                windows_to_hide.append(nano_banana.main_window)
            windows_to_hide.append(self.setup_window)

            images_path = pyflame.file_browser(
                path=self.images_path_entry.text,
                title='Select Images Path',
                select_directory=True,
                window_to_hide=windows_to_hide,
                )

            if images_path:
                self.images_path_entry.text = str(images_path)

        def save_settings() -> None:
            """
            Save Settings
            =============

            Validate and save settings to config file.
            """

            # Validate settings
            if not self.api_key_entry.text:
                PyFlameMessageWindow(
                    message='Please enter a API key.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            if not self.images_path_entry.text:
                PyFlameMessageWindow(
                    message='Please enter a images path.',
                    message_type=MessageType.ERROR,
                    parent=self.setup_window,
                    )
                return

            # Validate API key
            if not verify_api_key(api_key=self.api_key_entry.text):
                return

            # Save settings
            self.settings.save_config(
                config_values={
                    'api_key': self.api_key_entry.text,
                    'images_path': self.images_path_entry.text,
                    }
                )

            # Update open Nano Banana window with new key and path so its requests and later saves use them
            nano_banana = NanoBanana.get_open_window()
            if nano_banana:
                nano_banana.settings.api_key = self.api_key_entry.text
                nano_banana.set_images_path(self.images_path_entry.text)

            self.setup_window.close()

            PyFlameMessageWindow(
                message='Settings saved.',
                parent=None,
                )

        def close_window() -> None:

            self.setup_window.close()

        # ------------------------------------------------------------------------------

        self.setup_window = PyFlameWindow(
            title=f'{SCRIPT_NAME}: Setup <small>{SCRIPT_VERSION}',
            parent=None,
            return_pressed=save_settings,
            escape_pressed=close_window,
            grid_layout_columns=6,
            grid_layout_rows=4,
            window_margins=15,
            )

        # Labels
        self.api_key_label = PyFlameLabel(
            text='Nano Banana API Key',
            )
        self.images_path_label = PyFlameLabel(
            text='Images Path',
            )

        # Entries
        self.api_key_entry = PyFlameEntry(
            text=self.settings.api_key,
            )
        self.images_path_entry = PyFlameEntry(
            text=self.settings.images_path,
            )

        # Menus
        self.images_path_token_menu = PyFlameTokenMenu(
            token_dest=self.images_path_entry,
            token_dict={
                'Project Name': '<ProjectName>',
                'Project Nick Name': '<ProjectNickName>',
                }
            )

        # Buttons
        self.images_path_browse_button = PyFlameButton(
            text='Browse',
            color=Color.GRAY,
            connect=browse_images_path,
            )
        self.setup_cancel_button = PyFlameButton(
            text='Cancel',
            color=Color.GRAY,
            connect=close_window,
            )
        self.setup_save = PyFlameButton(
            text='Save',
            color=Color.BLUE,
            connect=save_settings,
            )

        # ------------------------------------------------------------------------------
        # [Widget Layout]
        # ------------------------------------------------------------------------------

        self.setup_window.grid_layout.addWidget(self.api_key_label, 0, 0)
        self.setup_window.grid_layout.addWidget(self.api_key_entry, 0, 1, 1, 5)
        self.setup_window.grid_layout.addWidget(self.images_path_label, 1, 0)
        self.setup_window.grid_layout.addWidget(self.images_path_entry, 1, 1, 1, 3)
        self.setup_window.grid_layout.addWidget(self.images_path_browse_button, 1, 4)
        self.setup_window.grid_layout.addWidget(self.images_path_token_menu, 1, 5)
        self.setup_window.grid_layout.addWidget(self.setup_cancel_button, 3, 4)
        self.setup_window.grid_layout.addWidget(self.setup_save, 3, 5)

        self.api_key_entry.set_focus()

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_main_menu_custom_ui_actions():

    return [
        {
            'name': 'Logik',
            'hierarchy': [],
            'actions': []
        },
        {
            'name': 'Logik Portal Script Setup',
            'hierarchy': ['Logik'],
            'order': 2,
            'actions': [
               {
                    'name': 'Nano Banana Setup',
                    'execute': NanoBananaSetup,
                    'minimumVersion': '2025.2'
               }
           ]
        }
    ]

def get_media_panel_custom_ui_actions():

    return [
        {
            'name': 'Nano Banana',
            'actions': [
                {
                    'name': 'Nano Banana',
                    'execute': NanoBanana,
                    'minimumVersion': '2025.2'
                }
            ]
        }
    ]
