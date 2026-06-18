# Ab Colorchecker

**Script Version:** 3.9.2  
**Flame Version:** 2026  
**Written by:** AB  
**Creation Date:** 06.01.26  
**Update Date:** 06.17.26  

## Description

Camera matching via Macbeth ColorChecker chart in ACEScg scene-linear.
Load reference (Camera A) and source (Camera B) frames, click all 24
colour patches on each, then apply a correction that maps Camera B to
look like Camera A.
<br><br>
Standard mode uses a pure 3x3 colour matrix — zero always maps to zero,
full dynamic range preserved, clean shadows. Exports corrected EXR,
3D LUT (.cube), or both. Supports image sequence processing.
<br><br>
HDR / 360 mode uses a Thin-Plate Spline RBF for better colour accuracy
with wide-gamut cameras that produce negative channel values.
<br><br>
Sessions store both A and B patch data and can be recalled to apply
the same correction to new footage without re-clicking patches.
<br><br>
Uses OpenImageIO if available, falls back to OpenCV automatically.
Create ab_colorchecker_paths.py for custom library paths (IT/studio use).

## Menus

- Right-click in Batch → AB ColorChecker → Match Cameras...
- Right-click in Media Panel → AB ColorChecker → Match Cameras...

## Updates

- 3.9.2 06.17.26
- Fixed sequence import into Flame Batch as full clip not single frame.
- 3.9.1 06.17.26
- Export dialog redesigned with dropdown and LUT checkbox.
- Sequence naming fixed to name_matched.####.exr.
- HDR sessions store B patches for recall without re-clicking.
- 3.9.0 06.17.26
- OpenImageIO support with cv2 fallback.
- Side script for IT path configuration.
- Sequence processing added.
- 3.8.3 06.15.26
- Session save pre-fills filename from session name field.
- 3.7.0 06.12.26
- Standard mode switched to pure 3x3 colour matrix.
- HDR mode uses single-stage TPS RBF.
