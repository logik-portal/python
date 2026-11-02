# Nano Banana

**Script Version:** 1.3.0  
**Flame Version:** 2025.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.13.26  
**Update Date:** 11.01.26  

**Script Type:** Media Panel

## Description

Generate images using Nano Banana models.
<br><br>
A valid Google/Gemini API key is required to use this script.
<br><br>
Currently supported models:
<br><br>
Gemini Nano Banana 2.1 (Nano Banana 2.1) - Default model
- High-efficiency model with improved visual quality, text rendering and multi-turn consistency.
- Supports 1K, 2K, and 4K resolutions.
- Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
- Supports aspect ratios 1:4, 4:1, 1:8, 8:1.
- Thinking levels: Minimal, Medium, High. Default: Medium.
<br><br>
Gemini 3.1 Flash Image (Nano Banana 2)
- Previous high-efficiency model. Still supported, Google recommends Nano Banana 2.1 for new work.
- Supports 1K, 2K, 4K, and 512 (512px) resolutions.
- Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
- Supports aspect ratios 1:4, 4:1, 1:8, 8:1.
- Thinking levels: Minimal, High. Default: Minimal.
<br><br>
Gemini 3.1 Flash Lite Image (Nano Banana 2 Lite)
- Fastest and lowest cost model. Best for quick iteration.
- Only supports 1K resolution.
- Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
- Thinking levels: Minimal, High. Default: Minimal.
<br><br>
Gemini 3 Pro Image (Nano Banana Pro)
- Highest quality model. Best for complex prompts and rendering text in images.
- Supports 1K, 2K, and 4K resolutions.
- Supports aspect ratios 1:1, 21:9, 16:9, 4:3, 3:2, 9:16, 3:4, 2:3, 5:4, 4:5.
- Thinking is always on and the level can't be set.
<br><br>
Gemini Chat:
<br><br>
Send a message to chat with Gemini 3.8 Flash about creating an image. Great for improving prompts or describing images.
Enter a message in the prompt field and click the Gemini Chat button. The response will be displayed in the prompt text window. Copy and paste any response into the prompt text field and use the Send Prompt button to send the prompt to Nano Banana.
<br><br>
Images:
<br><br>
Returned images are saved as PNG or JPEG. Any other type Google returns (such as WebP, which Flame can't read) is converted to PNG. The image gallery only shows PNG and JPEG files.
<br><br>
** WARNING **
Using this script will incur charges to your Nano Banana/Gemini account.
Please review your usage limits and pricing plan before proceeding.
Your API key will be stored unencrypted in the config file so be aware of who has access to it.
<br><br>
Images are stored in <script_path>/images/. A tokenized path can be set in the script setup, or with the Change Path button in the main window, to store images in a different location.
The folder images are saved to is shown under the Image Gallery buttons.

## URL

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

## Menus

### Script Setup
- Flame Main Menu → Logik → Logik Portal Script Setup → Nano Banana Setup
### To prompt Nano Banana with no prompt image
- Media Panel → Right-click → Nano Banana
### To prompt Nano Banana with a prompt image
- Media Panel → Right-click on clip or sequence → Nano Banana

## Installation

Copy script into /opt/Autodesk/shared/python/nano_banana

## Updates

### v1.3.0 [11.01.26]
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
- Working path is now shown under the image gallery.
- Added a Change Path button to change the working folder from the main UI.
- Fixed: in Flame 2027.2 every request failed with "No internet connection" because Flame's Python couldn't find its SSL certificates. Requests now also use the certificates that come with Flame's Python (certifi) and the system's own certificate bundle, so nothing needs to be installed.
- Fixed: Send Prompt and Gemini Chat caused an error when the prompt image file was moved or deleted outside the script. The error names the file, the prompt image is cleared and nothing is sent.
- Added the 512 (512px) resolution for Nano Banana 2.
- Added Gemini Nano Banana 2.1 (Nano Banana 2.1) and made it the default model.
- Added Thinking Level menu.
- Updated Gemini Chat to use Gemini 3.8 Flash. Gemini 3.7 Flash is deprecated and Google auto-routes it to 3.8 (no shutdown date).
- Fixed: the image gallery listed file types the prompt image can't show (exr, dpx, tif...), and clicking one raised an error. The gallery now shows only PNG and JPEG files, so Import to Flame only gets files Flame can read.
- Fixed: the prompt image was sent with the wrong type for non-PNG files. The type now matches the file (PNG or JPEG).
- Fixed: Send Prompt and Gemini Chat stayed enabled during a request, so a double click could send a second paid request. Both are disabled (and Return does nothing) until the request ends.
- Fixed: saved resolution and aspect ratio were lost when the window opened (4K/4:3 came back as 1K/1:1). Changing the model now resets them to that model's first options.
- Fixed: clicking Done saved the resolved images path over the tokenized one, so every project saved into the first project's folder.
- Fixed: Send Prompt API errors now show Google's error message.
- Requests over Google's 20 MB request size limit are no longer sent. An error shows the prompt image size.
- Fixed: running the script again on the same clip opened a file exists dialog and the window didn't open. The exported frame is now overwritten.
- Export errors are now shown in a message window.
- Fixed: exporting failed when the images folder didn't exist yet. The folder is now created.
- Fixed: every selected clip was exported. Only the first selected clip or sequence is exported now.
- Fixed: an empty Gemini Chat reply was added to the history instead of showing an error.
- Fixed: "Image generated successfully." was shown when no image came back. The reason is now shown (blocked prompt, safety finish reason, returned text).
- Fixed: "Please wait..." stayed in the status line after an empty prompt or a failed request.
- Fixed: an empty or invalid API response raised an error instead of showing a message.
- Fixed: Delete Image raised an error when the selected file was already removed.
- Fixed: Reveal in Finder/MediaHub failed when the images folder didn't exist yet. The folder is now created.
- Fixed: Return pressed in the image gallery sent a prompt. Return/Enter in the prompt text field now sends the prompt, Shift+Return adds a new line, and Return elsewhere no longer sends.
<br>

### v1.2.0 [08.18.26]
- Updated to use Google's current Nano Banana models.
- Added: Gemini 3.1 Flash Lite Image (Nano Banana 2 Lite).
- Updated: gemini-3.1-flash-image-preview to gemini-3.1-flash-image (Nano Banana 2).
- Updated: gemini-3-pro-image-preview to gemini-3-pro-image (Nano Banana Pro).
- Removed: Gemini 2.5 Flash Image (Nano Banana). Google lists its shutdown as 03.15.27.
- Updated Gemini Chat to use Gemini 3.7 Flash. Google limits access to Gemini 2.5 Flash to earlier users (no shutdown date announced).
- Nano Banana 2 is now the default model. Models saved in the config by older versions of the script are replaced with the default model on startup.
- Fixed: aspect ratios 1:4, 4:1, 1:8, and 8:1 were listed for Nano Banana Pro, which does not support them.
<br>

### v1.1.2 [03.25.26]
- Fixed: model resolution menu not updating when a different model is selected.
<br>

### v1.1.1 [03.24.26]
- Fixed: export preset path. This was causing the script not to work when running the script with an image selected.
<br>

### v1.1.0 [03.23.26]
- Added Gemini Chat button to send a message to chat with Gemini about creating an image.
- Updated model menus to clarify model names.
<br>

### v1.0.1 [03.20.26]
- Updated script to work with Flame 2025.2.
<br>

### v1.0.0 [03.13.26]
- Initial release.
