# fix premiere xmls

**Script Version:** 2.1.2  
**Flame Version:** 2023.2  
**Written by:** Ted Stanley, John Geehreng, and Michael Vaglienty  
**Creation Date:** 03.03.21  
**Update Date:** 02.13.25  

**Script Type:** MediaHub

## Description

Fix and/or Resize Adobe Premiere XML's.

## Menus

- MediaHub → XML Prep → Fix Premiere XML's

## Installation

Copy script into /opt/Autodesk/shared/python/fix_premiere_xmls

## Updates

- 02.13.25 - v2.1.2  Update to latest pyflame lib and SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))
- 05.06.24 - v2.1.1  Changed Scoping to show up only if xml's are selected
- 04.03.24 - v2.1    Fixed renaming issue
- 12.05.23 - v2.0.2  Fixed the missing fixduration() problem. Made _x_res names consistent.
- 11.28.23 - v2.0.1  Updated for pyflame lib v2. Added ability to resize xmls. Changed the output names based on options
- 11.12.23 - v1.94   Fixed the Scale Factor Calculator to use the correct width or height. Added try/except when using the "Clean Names" option.
- 09.08.22 - v1.93   2023.2 Ordering and Scale Factor Calculator
- 05.24.22 - v1.92   Update from Ted - This one fixes almost everything. Except dissolves, those still suck.
- 04.19.22 - v1.91   2023 UI
- 02.19.22 - v1.90   Created option for automatically using the xml's resolution
- 12.27.21 - Turned off "v" to "V" when sanatizing names
- 11.15.21 - Added the ability to scale values over 100
- 09.03.21 - Made sanatizing the names optional
- 08.27.21 - Turned off the "That Totally Worked" message as you can see the update in the MediaHub
- 08.13.21 - Change XML Bit Depth to Project Settings
- 06.04.21 - Change Default Scale Value to 100 for graphics. Renamed "Cancel" button to say "Close"
- 05.17.21 - Added the ability to select multiple .xml's and added Ted's nested layer fix
- 03.19.21 - Python3 Updates
