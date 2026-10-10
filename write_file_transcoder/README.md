# Write File Transcoder

**Script Version:** 1.1.0  
**Flame Version:** 2026.2  
**Written by:** Huseyin Pasaoglu  
**Creation Date:** 09.15.26  
**Update Date:** 10.09.26  

## Description

Turns every Write File render into a Rec709 review copy, automatically.
<br><br>
When a Write File render finishes the rendered sequence is converted to an
H.264 MP4 or a ProRes MOV using real OCIO colour management, reformatted to
a review canvas and stamped with burn-in - all from a preset, with no
interaction. The render itself is never touched.
<br><br>
Colour comes only from the preset (OCIO config, source colour space,
display, view, optional look). Flame's project colour policy is deliberately
NOT read, so a preset gives the same result on every machine and every show.
<br><br>
Reformat: 1920x1080, 3840x2160 or a custom canvas; fit vertically,
horizontally or fill; per-side crop and an X/Y shift in source pixels; band
colour. A schematic preview in the settings window shows the layout while
you type.
<br><br>
Burn-in: six zones (top/bottom x left/centre/right) with free text and
tokens - <frame number>, <clip name>, <time code>, <user name>, <date>,
<time>, <project>, <shot>, <resolution>, <fps>, <frame range>. The text is
drawn with Qt and composited by ffmpeg, so a specific ffmpeg build is not
required (many are compiled without drawtext).
<br><br>
Missing frames are replaced with a black slate reading "MISSING FRAME 1012"
so duration and timecode stay correct, and a warning is logged. An aborted
render produces nothing but a log note.
<br><br>
Jobs run one at a time in a background queue; quitting Flame cancels the
running job and removes the half-written file. Output is written to a
.partial file and renamed on success, and an existing file is never
overwritten - a colliding name gets _repeat, _repeat2 and so on.
<br><br>
Presets are exportable, so a look can be handed to another artist without
carrying machine settings such as the ffmpeg path.
<br><br>
Only the source formats ticked in Settings, General tab start a review
automatically; the manual action ignores that list. Sources are also checked
for an EXR compression ffmpeg decodes badly (PIZ), which would otherwise
show up as unexplained horizontal bands.
<br><br>
Installation: copy this file to /opt/Autodesk/shared/python/ and refresh
python hooks, or restart Flame. Nothing else to install.
<br><br>
Requires ffmpeg and ffprobe on PATH, built with libx264 (for MP4),
prores_ks (for MOV) and EXR decoding:
<br><br>
macOS : brew install ffmpeg
Rocky : dnf install ffmpeg     (needs RPM Fusion)
<br><br>
If ffmpeg lives somewhere unusual, set the full path in Settings, General
tab. Everything else ships with Flame. numpy is optional: when Flame's
Python can import it the colour transform runs about twice as fast, and the
output is identical either way.
<br><br>
Tested on Flame 2026.2.2 on macOS. Written to run on Linux as well, but not
yet tested there.

## Menus

- Flame Main Menu → Write File Transcoder → Settings...
- Flame Main Menu → Write File Transcoder → Open log
- Right-click a Write File node in Batch → Write File Transcoder → Create review...

## Updates

### v1.1.0 [10.09.26]
- Added a format filter: the automatic trigger now only fires for the
- source formats ticked in Settings, General tab. OpenEXR, DPX and TIFF
- are on by default; PNG and JPEG are off. Right-click -> Create review...
- still works on anything.
- Horizontal black bands in the output are now explained instead of shipped
- silently. ffmpeg's EXR decoder fails on dense PIZ blocks, leaves those
- 32-line blocks black and still exits 0. The source compression is checked
- up front and the job says so, naming the fix: set the Write File node to
- ZIP. The EXR files themselves are fine - OpenImageIO and Flame read them
- without trouble.
- The decoder's stderr is captured and its exit code checked. Any decoder
- complaint is logged and flagged on the finished job, so a damaged render
- can no longer be reported as a success.
<br>

### v1.0.0 [09.16.26]
- Initial release.
