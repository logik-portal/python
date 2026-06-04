# Black Head And Tail

**Script Version:** 1.1  
**Flame Version:** 2027  
**Written by:** Bryan Bayley  
**Creation Date:** 08.16.21  
**Update Date:** 06.02.26  

## Description

Add one second of virtual black head and tail to the selected sequences.
<br><br>
The black source is generated automatically (a temporary 1-second black Colour
Source), so nothing needs to be set up on the desktop beforehand. Set each
sequence's record patch to the track you want the black on (the patch can't be
controlled from Python). The head black is placed before the first frame and the
tail black after the last frame; neither edit ripples or shifts existing content.
Each black handle's timeline segment colour is set to black. If a sequence has no
room before its start the head won't land, and a warning lists any sequence whose
head or tail was not added.

## Menus

- Right-click a sequence in the Media Panel → Sequence... → Black Heads and Tails

## Updates

### v1.1 [06.02.26]
- Restore the original selection and active timeline when finished (creating and
- deleting the temp source otherwise left the top-most item selected).
<br>

### v1.0 [08.16.21]
- Initial release.
