# reveal path

**Script Version:** 2.8.0  
**Flame Version:** 2023.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 06.16.19  
**Update Date:** 04.03.25  

**Script Type:** Timeline / Media Panel / MediaHub / Batch

## Description

Reveal the path of a clip, open clip, or write node in the finder or Media Hub.
<br><br>
Path is also copied to clipboard.

## URL

https://github.com/logik-portal/python/reveal_path

## Menus

- Right-click on clip in timeline → Reveal... → Reveal Clip in Finder / Reveal Clip in MediaHub
- Right-click on clip in media panel → Reveal... → Reveal Clip in Finder / Reveal Clip in MediaHub
- Right-click on clip in batch → Reveal... → Reveal Clip in Finder / Reveal Clip in MediaHub
- Right-click on clip in media hub → Reveal... → Reveal Clip in Finder
- Right-click on Write File node in batch → Reveal... → Reveal in Finder
- Right-click on Write File node in batch → Reveal... → Reveal in MediaHub

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v2.8.0 [04.03.25]
- Updated to PyFlameLib v4.3.0.
- Fixed Bug: Revealing clip in MediaHub was not working.
<br>

### v2.7.0 [12.31.24]
- Updated to PyFlameLib v4.0.0.
- Script now only works with Flame 2023.2+.
<br>

### v2.6.0 [08.15.24]
- Updated to PyFlameLib v3.0.0.
<br>

### v2.5.0 [01.21.24]
- Updates to PySide.
<br>

### v2.4.0 [07.27.23]
- Updated to PyFlameLib v2.0.0.
- Updated to semantic versioning.
<br>

### v2.3 [10.24.22]
- Write File node path translation improved.
<br>

### v2.2 [05.26.22]
- Messages print to Flame message window - Flame 2023.1 and later
- Path is copied to clipboard
<br>

### v2.1 [10.21.21]
- Path that the MediaHub is currently open to can be revealed in Finder
- Write File node render path can be revealed in the MediaHub or in Finder
- Only the following tokens are currently supported with the write file node:
- project
- project nickname
- batch iteration
- batch name
- ext
- name
- shot name
- version padding
- version
- user
- user nickname
<br>

### v2.0 [05.19.21]
- Updated to be compatible with Flame 2022/Python 3.7
<br>

### v1.5 [05.12.21]
- Copy path to clipboard functionality moved to it's own script
- Merged with Reveal in Mediahub script - Reveal in MediaHub options only work in Flame 2021.2
- Clips in Timeline can now be revealed in Finder and Mediahub
<br>

### v1.4 [05.08.21]
- Clips in MediaHub can now be revealed in Finder and have paths copied to clipboard
<br>

### v1.2 [01.25.20]
- Menu option will now only show up when right-clicking on clips with file paths
<br>

### v1.1 [08.11.19]
- Code cleanup
