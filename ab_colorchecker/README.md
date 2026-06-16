# Ab Colorchecker

**Script Version:** 3.8.3  
**Flame Version:** 2026  
**Written by:** AB  
**Creation Date:** 06.01.26  
**Update Date:** 06.15.26  

## Description

Camera matching via Macbeth ColorChecker chart in ACEScg scene-linear.

## Usage

Load reference (Camera A) and source (Camera B) frames, click all 24
colour patches on each, then apply a correction that maps Camera B to
look like Camera A.
<br><br>
Standard mode uses a pure 3x3 colour matrix — zero always maps to zero,
full dynamic range preserved, clean shadows. Exports corrected EXR,
3D LUT (.cube), or both. The LUT closely matches the EXR output.
<br><br>
HDR / 360 mode uses a Thin-Plate Spline RBF for better colour accuracy
with wide-gamut cameras that produce negative channel values.
<br><br>
Sessions can be saved and recalled — Camera A patches never need to be
re-clicked. Load a session, load a new Camera B frame, click 24 patches,
and apply.

## Menus

- Right-click in Batch → AB ColorChecker → Match Cameras...
- Right-click in Media Panel → AB ColorChecker → Match Cameras...

## Installation

Install Required Python packages
----------------------------------------------------------------
This script requires numpy and opencv-python. Run the following command
in Terminal before running the script:
<br><br>
Mac / Linux (Terminal):
/opt/Autodesk/python/<Flame Version>/bin/python3 -m pip install numpy opencv-python --break-system-packages
<br><br>
Example:
/opt/Autodesk/python/2026.2/bin/python3 -m pip install numpy opencv-python --break-system-packages
<br><br>
After installing, restart Flame or reload Python scripts.
----------------------------------------------------------------

## Updates

- 3.8.2 06.15.26
- Apply Correction button now shows export dialog (EXR, LUT, or Both).
- Session save no longer defaults to a fixed path.
- Minor UI refinements.
<br>
- 3.8.0 06.14.26
- Standard mode now offers EXR, 3D LUT, or both on export.
- Auto-installs required Python packages on first launch.
<br>
- 3.7.0 06.12.26
- Standard mode switched to pure 3x3 colour matrix for clean shadow handling.
- HDR mode uses single-stage TPS RBF for wide-gamut camera accuracy.
- Session save and load fixed.
