# Path Translator

**Script Version:** 2.1.3  
**Flame Version:** 2025  
**Written by:** Kieran Hanrahan  
**Creation Date:** 02.10.24  
**Update Date:** 10.27.26  

## Description

Take a path, either Windows or POSIX, and extract part of the path using tokens.
Useful for converting windows paths to POSIX for Flame, or even paths from other
machines that just have different mount points.
<br><br>
Example paths this was tested on below.
<br><br>
windows path no trailing slash
J:\dir\dir\dir\dir\_dir\000000
<br><br>
frankenstein path with posix slashes and windows mount
J:/dir/dir/dir/dir/dir/dir/dir-dir/file_file_file_file-file_v000.mov

## URL

http://www.github.com/khanrahan/path-translator

## Menus

- Right-click selected folders in the Media Hub -→ Navigate... -→ Path Translator

## Installation

For all users, copy this file to:
/opt/Autodesk/shared/python
<br><br>
For a specific user, copy this file to:
/opt/Autodesk/user/<user name>/python

## Updates

### v2.1.3 [10.27.26]
- Updated with a Qt fix for Flame 2027.2.
<br>
