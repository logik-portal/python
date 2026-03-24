# Nano Banana

**Script Version:** v1.1.1  
**Flame Version:** 2025.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 03.13.26  
**Update Date:** 03.24.26  

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

### v1.1.1 [03.24.26]
- Fixed export preset path. This was causing the script not to work when running the script with an image selected.
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
