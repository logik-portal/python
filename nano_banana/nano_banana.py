# Nano Banana
# Copyright (c) 2026 Michael Vaglienty
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
Script Name: Nano Banana
Script Version: v1.1.0
Flame Version: 2025.2
Written by: Michael Vaglienty
Creation Date: 03.13.26
Update Date: 03.23.26

License: GNU General Public License v3.0 (GPL-3.0) - see LICENSE file for details

Script Type: Media Panel

Description:

    Generate images using Nano Banana models.

    A valid Google/Gemini API key is required to use this script.

    Currently supported models:

        Gemini 2.5 Flash Image (Nano Banana)
            - Only supports 1K resolution and aspect ratio 1:1.

        Gemini 3.1 Flash Image Preview (Nano Banana 2)
            - Supports 1K, 2K, and 4K resolutions.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.

        Gemini 3 Pro Image Preview (Nano Banana Pro)
            - Supports 1K, 2K, and 4K resolutions.
            - Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            - Supports aspect ratios 1:4, 4:1, 1:8, 8:1.

    Gemini Chat:

        Send a message to chat with Gemini about creating an image. Great for improving prompts or describing images.
        Enter a message in the prompt field and click the Gemini Chat button. The response will be displayed in the prompt
        text window. Copy and paste any respone into the prompt text field and use the Send Prompt button to send the prompt
        to Nano Banana.

    ** WARNING **
    Using this script will incur charges to your Nano Banana/Gemini account.
    Please review your usage limits and pricing plan before proceeding.
    Your API will be stored unencrypted in the config file so be aware of who has access to it.

    Images are stored in <script_path>/images/. A tokenized path can be set in the script
    setup to store images in a different location.

Workflow:

    Run the script with a clip selected in the media panel to export the first frame of the clip
    to the script's images folder and add it to the prompt.

    If no clip is selected, the script will start with a blank prompt.

    After getting back an image from Nano Banana the image is automatically added to the prompt.

    When done prompting use the Import to Flame button to import the desired image to the media panel.

    Buttons:

        Send Prompt: Sends the current prompt to Nano Banana at the selected model and resolution.

        Import to Flame: Import the current selected image in the Image Gallery to the media panel.

        Send to Prompt: Adds the selected image in the Image Gallery to the prompt.

        Clear Prompt Image: Clears the current prompt image from the prompt.

Menus:

    Script Setup:
        Flame Main Menu -> Logik Portal -> Logik Portal Script Setup -> Nano Banana Setup

    To prompt Nano Banana with no prompt image:
        Media Panel -> Right-click -> Nano Banana

    To prompt Nano Banana with a prompt image:
        Media Panel -> Right-click on clip or sequence -> Nano Banana

To install:

    Copy script into /opt/Autodesk/shared/python/nano_banana

Updates:

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

import base64
import json
import os
import random
import urllib.error
import urllib.request
from typing import Any

import flame
from PySide6 import QtCore, QtGui
from lib.pyflame_lib_nano_banana import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME    = 'Nano Banana'
SCRIPT_VERSION = 'v1.1.0'
SCRIPT_PATH    = os.path.abspath(os.path.dirname(__file__))

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

    return PyFlameConfig(
        config_values={
            'api_key': '',
            'images_path': os.path.join(SCRIPT_PATH, 'images'),
            'model': 'gemini-2.5-flash-image (Nano Banana)',
            'resolution': '1K',
            'aspect_ratio': '1:1',
            },
        )

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
        urllib.request.urlopen(url, timeout=10)
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
        urllib.request.urlopen('https://www.google.com', timeout=5)
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

class NanoBanana:

    def __init__(self, selection) -> None:

        pyflame.print_title(f'{SCRIPT_NAME} {SCRIPT_VERSION}')

        # Create/Load config file settings.
        self.settings = load_config()

        # Run startup checks
        if not self.startup_checks():
            return

        self.selection = selection
        print('Selection:', selection, '\n')

        self.settings.images_path = pyflame.resolve_tokens(tokenized_string=self.settings.images_path)
        print('Images Path:', self.settings.images_path, '\n')

        # Export image to Nano Banana Prompt if selection is a clip or sequence.
        self.flame_image_exported = False
        if isinstance(self.selection[0], (flame.PyClip, flame.PySequence)):
            self.export_to_nano_banana()
            self.flame_image_exported = True

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

    def export_to_nano_banana(self) -> None:
        """
        Export to Nano Banana
        =====================

        Export the first frame of the current selection(Clip or Sequence) to the Nano Banana Prompt.
        """

        pyflame.print('Exporting to Nano Banana...')

        export_preset_path = '/Volumes/NAS/Python/_Shared_Scripts/nano_banana/assets/export_preset/PNG (8-bit) Nano Banana.xml'
        print('Export Preset Path:', export_preset_path, '\n')

        # Set version of export preset to match current version of Flame to avoid error windows.
        pyflame.update_export_preset(export_preset_path)

        # Resolve image export path
        image_export_path = pyflame.resolve_tokens(tokenized_string=self.settings.images_path)
        print('Image Export Path:', image_export_path)

        # Get exportedimage path
        self.exported_image_path = os.path.join(image_export_path, self.selection[0].name + '.png')
        print('Exported Image Path:', self.exported_image_path, '\n')

        # Initialize Exporter
        exporter = flame.PyExporter()
        exporter.foreground = True

        # Export first frame of selection using export preset
        exporter.export(self.selection, export_preset_path, image_export_path)

        pyflame.print('Image exported to Nano Banana.')

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
                    }
                )

        def send_prompt() -> None:
            """
            Send Prompt
            ==========

            Send prompt text to the Nano Banana API and save the
            returned image to the images folder.
            """

            pyflame.print('Sending prompt... Please wait...')
            self.banana_message_entry.text = 'Sending prompt... Please wait...'
            pyflame.pause()

            # Get prompt text
            prompt_text = self.prompt_text_edit.text_str.strip()
            if not prompt_text:
                PyFlameMessageWindow(
                    message='Please enter a prompt before sending.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            selected_model = self.select_model_menu.text
            selected_model = selected_model.rsplit(' (', 1)[0].strip()
            print('Selected Model:', selected_model)

            url = (
                'https://generativelanguage.googleapis.com/v1beta/'
                f'models/{selected_model}:generateContent?key={self.settings.api_key}'
            )

            parts: list[dict[str, Any]] = [{'text': prompt_text}]

            if self.prompt_image_widget.has_image and self.prompt_image_widget.image_path:
                image_path = self.prompt_image_widget.image_path
                ext = os.path.splitext(image_path)[1].lower()
                mime_map = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                }
                mime = mime_map.get(ext, 'image/png')
                with open(image_path, 'rb') as img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode()
                parts.append({
                        'inlineData': {
                        'mimeType': mime,
                        'data': img_b64,
                    }
                })

            aspect_ratio = self.aspect_ratio_menu.text.strip() or '1:1'

            # imageSize is only supported by Nano Banana 2 and Pro.
            # The original gemini-2.5-flash-image ignores it and may error.
            image_config = {'aspectRatio': aspect_ratio}
            if selected_model != 'gemini-2.5-flash-image':
                image_size = self.image_resolution_menu.text.strip().upper() or '1K'
                image_config['image_size'] = image_size

            # Bump timeout to 180s to safely accommodate 4K generation on Pro.
            request_timeout = 180

            generation_config = {
                'responseModalities': ['TEXT', 'IMAGE'],
                'imageConfig': image_config,
            }

            payload = json.dumps({
                'contents': [{'parts': parts}],
                'generationConfig': generation_config,
            }).encode()

            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )

            try:
                with urllib.request.urlopen(req, timeout=request_timeout) as response:
                    result = json.loads(response.read().decode())
            except urllib.error.HTTPError as e:
                PyFlameMessageWindow(
                    message=f'Nano Banana API request failed (HTTP {e.code}).\n\nPlease try again.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return
            except (urllib.error.URLError, OSError):
                PyFlameMessageWindow(
                    message='Unable to reach the Nano Banana API.\n\nPlease check your internet connection and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            response_parts = result.get('candidates', [{}])[0].get('content', {}).get('parts', [])

            # Capture both text and image from the response.
            # The model sometimes returns a text description alongside the image.
            image_data = None
            mime_type = None
            model_text = []

            for part in response_parts:
                if part.get('text'):
                    model_text.append(part['text'])
                inline = part.get('inlineData')
                if inline and not image_data:
                    image_data = inline.get('data')
                    mime_type = inline.get('mimeType', 'image/png')

            # Log any text the model returned alongside the image.
            if model_text:
                combined = ' '.join(model_text)
                pyflame.print(f'Model: {combined}')
                self.banana_message_entry.text = combined
            else:
                self.banana_message_entry.text = 'Image generated successfully.'

            if not image_data:
                PyFlameMessageWindow(
                    message='No image was returned from the Nano Banana API.\n\nTry a different prompt.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                    )
                return

            mime = mime_type or 'image/png'
            ext = '.png' if 'png' in mime else '.jpg'
            from datetime import datetime
            filename = f'nano_banana_{datetime.now().strftime("%Y%m%d_%H%M%S")}{ext}'
            save_path = os.path.join(self.settings.images_path, filename)

            os.makedirs(self.settings.images_path, exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(base64.b64decode(image_data))

            pyflame.print(f'Image saved: {save_path}')

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

            model = 'gemini-2.5-flash'

            # ---- Validate prompt text ----
            prompt_text = self.prompt_text_edit.text_str.strip()
            if not prompt_text:
                PyFlameMessageWindow(
                    message='Please enter a message before sending.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                )
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
            if self.prompt_image_widget.has_image and self.prompt_image_widget.image_path:
                image_path = self.prompt_image_widget.image_path
                ext = os.path.splitext(image_path)[1].lower()
                mime_map = {
                    '.png': 'image/png',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.gif': 'image/gif',
                    '.webp': 'image/webp',
                }
                mime = mime_map.get(ext, 'image/png')
                with open(image_path, 'rb') as img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode()
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

            # ---- Send request ----
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST',
            )
            try:
                with urllib.request.urlopen(req, timeout=60) as response:
                    result = json.loads(response.read().decode())
            except urllib.error.HTTPError as e:
                # Read error body for more specific feedback (400 often has useful details)
                try:
                    err_body = e.read().decode()
                    err_json = json.loads(err_body)
                    err_detail = err_json.get('error', {}).get('message', err_body)
                except Exception:
                    err_detail = str(e)
                PyFlameMessageWindow(
                    message=f'Nano Banana API request failed (HTTP {e.code}).\n\n{err_detail}',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                )
                return
            except (urllib.error.URLError, OSError):
                PyFlameMessageWindow(
                    message='Unable to reach the Nano Banana API.\n\nPlease check your internet connection and try again.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                )
                return

            # ---- Extract text from response (expect text, not image) ----
            response_parts = result.get('candidates', [{}])[0].get('content', {}).get('parts', [])
            response_text = "Gemini: " + ' '.join(p.get('text', '') for p in response_parts if p.get('text')).strip()

            if not response_text:
                PyFlameMessageWindow(
                    message='No text response from the Nano Banana API.\n\nTry a different message.',
                    message_type=MessageType.ERROR,
                    parent=self.main_window,
                )
                return

            # ---- Append user message (right-aligned) and Gemini response (left-aligned) to history ----
            append_gemini_response_to_prompt(self.prompt_history_text_edit, prompt_text, response_text)
            self.prompt_text_edit.text_str = ''
            self.banana_message_entry.text = 'Message received.'
            pyflame.print('Message received.')

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

            pyflame.open_in_finder(self.settings.images_path)

            pyflame.print(f'Finder opened: {self.settings.images_path}')

        def reveal_in_mediahub() -> None:
            """
            Reveal in MediaHub
            ==================

            Reveal image in mediahub.
            """

            # Switch to MediaHub tab
            flame.go_to('MediaHub')

            # Set path in MediaHub
            flame.mediahub.files.set_path(self.settings.images_path)

            pyflame.print(f'MediaHub opened: {self.settings.images_path}')

        def delete_image() -> None:
            """
            Delete Image
            ============

            Delete selected gallery image from the file system.
            """

            path = self.image_gallery.selected_path
            if path is None:
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

        self.main_window = PyFlameWindow(
            title=f'{SCRIPT_NAME} <small>{SCRIPT_VERSION}',
            parent=None,
            return_pressed=send_prompt,
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

        # Entries
        self.banana_message_entry = PyFlameEntry(
            text='',
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
            folder=self.settings.images_path,
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

        def update_resolution_menu_for_model() -> None:
            """
            Update Resolution Menu for Model
            ================================

            Set image_resolution_menu and aspect_ratio_menu options based on the selected model.
            gemini-2.5-flash-image: 1K only; aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
            gemini-3.1-flash-image-preview / gemini-3-pro-image-preview: 1K, 2K, 4K; same ratios plus 1:4, 4:1, 1:8, 8:1.
            """

            # Aspect ratios available for Gemini 2.5 models and Gemini 3.x models.
            aspect_ratios_2_5 = ['1:1', '21:9', '16:9', '4:3', '3:2', '9:16', '3:4', '2:3', '5:4', '4:5']
            aspect_ratios_3_X = aspect_ratios_2_5 + ['1:4', '4:1', '1:8', '8:1']

            # Set resolution options based on the selected model.
            model = self.select_model_menu.text.strip()
            if model == 'gemini-2.5-flash-image':
                resolution_options = ['1K']
                aspect_ratio_options = aspect_ratios_2_5
            elif model in ('gemini-3.1-flash-image-preview', 'gemini-3-pro-image-preview'):
                resolution_options = ['1K', '2K', '4K']
                aspect_ratio_options = aspect_ratios_3_X
            else:
                resolution_options = ['1K']
                aspect_ratio_options = aspect_ratios_2_5
            self.image_resolution_menu.menu_options = resolution_options
            if self.image_resolution_menu.text.strip() not in resolution_options:
                self.image_resolution_menu.text = resolution_options[0]
            self.aspect_ratio_menu.menu_options = aspect_ratio_options
            if self.aspect_ratio_menu.text.strip() not in aspect_ratio_options:
                self.aspect_ratio_menu.text = aspect_ratio_options[0]

        # Menus
        self.select_model_menu = PyFlameMenu(
            text=self.settings.model,
            menu_options=[
                'gemini-2.5-flash-image (Nano Banana)',
                'gemini-3.1-flash-image-preview (Nano Banana 2)',
                'gemini-3-pro-image-preview (Nano Banana Pro)',
                ],
            connect=update_resolution_menu_for_model,
            )
        self.image_resolution_menu = PyFlameMenu(
            text=self.settings.resolution,
            )
        self.aspect_ratio_menu = PyFlameMenu(
            text=self.settings.aspect_ratio,
            )

        # Buttons
        self.done_button = PyFlameButton(
            text='Done',
            connect=done,
            )
        self.send_prompt_button = PyFlameButton(
            text='Send Prompt',
            connect=send_prompt,
            color=Color.BLUE,
            tooltip='Send prompt to create an image with Nano Banana',
            )
        self.send_message_button = PyFlameButton(
            text='Gemini Chat',
            connect=send_message,
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

        self.main_window.grid_layout.addWidget(self.banana_image_label, 0, 9, 1, 3)
        self.main_window.grid_layout.addWidget(self.banana_image_widget, 1, 9, 17, 3)
        self.main_window.grid_layout.addWidget(self.banana_message_entry, 18, 9, 1, 3)

        self.main_window.grid_layout.addWidget(self.send_prompt_button, 21, 7)
        self.main_window.grid_layout.addWidget(self.done_button, 21, 11)

        # ------------------------------------------------------------------------------

        # UI Toggles
        update_resolution_menu_for_model()

        # Set window focus to prompt text edit
        self.prompt_text_edit.set_focus()

        # Add imported image to prompt image widget if image is selected from Flame
        if self.flame_image_exported:
            self.prompt_image_widget.image = self.exported_image_path

        bananas()

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

            images_path = pyflame.file_browser(
                path=self.images_path_entry.text,
                title='Select Images Path',
                select_directory=True,
                window_to_hide=self.setup_window,
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
