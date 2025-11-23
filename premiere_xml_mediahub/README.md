# premiere xml mediahub

**Script Version:** 1.91  
**Flame Version:** 2023  
**Written by:** Ted Stanley, John Geehreng, and Mike V  
**Creation Date:** 03.03.21  
**Update Date:** 04.18.22  

## Description

With Mike V's help, it also adds a scale factor to compensate for the difference between proxy resolution
and the full resolution of the clips in Flame.
To obtain the scale factor, divide the proxy resolution by the full resolution of your clips and then multiply by 100.
If math is not your thing, you can also figure it out by creating a new axis in Action, parenting it under the axis that has the repo data on it, and manually find the scale difference.
<br><br>
If the aspect ratios of the proxy files are the same as the full res clips, you can use either the x or y value.
If the proxy files have a letterbox use (proxy x res / full res x res)
If the proxy files have pillar bars, use (proxy y res / full res y res)
If you have multiple resolutions, run the script as many times as needed. It will name them based on the scale factor.
<br><br>
03.19.21 - Python3 Updates
05.17.21 - Added the ability to select multiple .xml's and added Ted's nested layer fix
06.04.21 - Change Default Scale Value to 100 for graphics. Renamed "Cancel" button to say "Close"
08.13.21 - Change XML Bit Depth to Project Settings
08.27.21 - Turned off the "That Totally Worked" message as you can see the update in the MediaHub
09.03.21 - Made sanatizing the names optional
11.15.21 - Added the ability to scale values over 100
12.27.21 - Turned off "v" to "V" when sanatizing names
02.19.22 - Created option for automatically using the xml's resolution (v1.9)
04.19.22 - 2023 UI (v1.91)
