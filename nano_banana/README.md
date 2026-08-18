# Nano Banana

**Script Version:** 1.2.0  
**Flame Version:** 2025.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.13.26  
**Update Date:** 08.18.26  

**Script Type:** Media Panel

## Description

Run the script with a clip selected in the media panel to export the first frame of the clip
to the script's images folder and add it to the prompt.
<br><br>
If no clip is selected, the script will start with a blank prompt.
<br><br>
After getting back an image from Nano Banana the image is automatically added to the prompt.
<br><br>
When done prompting use the Import to Flame button to import the desired image to the media panel.
<br><br>
Buttons:
<br><br>
Send Prompt: Sends the current prompt to Nano Banana at the selected model and resolution.
<br><br>
Import to Flame: Import the current selected image in the Image Gallery to the media panel.
<br><br>
Send to Prompt: Adds the selected image in the Image Gallery to the prompt.
<br><br>
Clear Prompt Image: Clears the current prompt image from the prompt.

## Menus

### Script Setup
- Flame Main Menu → Logik Portal → Logik Portal Script Setup → Nano Banana Setup
### To prompt Nano Banana with no prompt image
- Media Panel → Right-click → Nano Banana
### To prompt Nano Banana with a prompt image
- Media Panel → Right-click on clip or sequence → Nano Banana

## Installation

Copy script into /opt/Autodesk/shared/python/nano_banana

## Updates

### v1.2.0 [08.18.26]
- Updated to use Google's current Nano Banana models.
- Added: Gemini 3.1 Flash Lite Image (Nano Banana 2 Lite).
- Updated: gemini-3.1-flash-image-preview to gemini-3.1-flash-image (Nano Banana 2).
- Updated: gemini-3-pro-image-preview to gemini-3-pro-image (Nano Banana Pro).
- Removed: Gemini 2.5 Flash Image (Nano Banana). Google is retiring this model on 10.02.26.
- Updated Gemini Chat to use Gemini 3.7 Flash. Gemini 2.5 Flash is being retired on 10.16.26.
- Nano Banana 2 is now the default model. Models saved in the config by older versions of the
- script are replaced with the default model on startup.
- Fixed: aspect ratios 1:4, 4:1, 1:8, and 8:1 were listed for Nano Banana Pro, which does not
- support them.
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
