# Add Audio

**Script Version:** 1.5.1  
**Flame Version:** 2025.1  
**Written by:** Michael Vaglienty  
**Creation Date:** 02.04.22  
**Update Date:** 10.16.26  

**Script Type:** Batch

## Description

Add stereo or 5.1 audio to selected sequences.
<br><br>
Only works with sequences. Clips are not supported, and the menu only appears when a sequence is selected.
<br><br>
To add stereo audio to a sequence, select the sequence then select the audio clip to be added.
To add stereo audio to multiple sequences, select in sequence/audio/sequence/audio... order.
<br><br>
To add 5.1 surround audio to a sequence, select the sequence followed by all the audio channels(LF, RF, C, LFE, LS, RS, Stereo)
To add 5.1 surround audio to multiple sequences, select in sequence/all audio channels/sequences/all audio channels... order.
<br><br>
Order of 5.1 surround files does not matter when being selected.
When added to the sequence they will be put in this order: LF, RF, C, LFE, LS, RS, Stereo
<br><br>
5.1 surround file names must end with _LF, _RF, _C, _LFE, _LS, _RS, or _Stereo. Case is not important.

## URL

https://logik-portal.com/scripts/add_audio

## Menus

- Right-click selection of sequences and audio → Audio → Insert Stereo Audio - 01:00:00:00
- Right-click selection of sequences and audio → Audio → Insert Stereo Audio - 00:59:58:00
- Right-click selection of sequences and audio → Audio → Insert 5.1 Audio - 01:00:00:00
- Right-click selection of sequences and audio → Audio → Insert 5.1 Audio - 00:59:58:00

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

### v1.5.1 [10.16.26]
- Audio tracks are now labelled after the audio added to them: Stereo L/R, or 5.1 LF, RF, C, LFE, LS, RS and 5.1 Stereo L/R. The audio clips keep their original names.
- 5.1 audio now stops with an error naming any missing, duplicate or misnamed channel files. Previously a misnamed file was silently skipped and the other channels shifted tracks.
- Selection order is now checked before anything is created. Selecting audio before its sequence shows an error instead of failing and leaving a partly made library.
- Added note that the script only works with sequences.
- Updated to PyFlameLib v5.5.3 - Fixes screenGeometry error with Flame 2027.2.
- Changed license from GPL-3.0 to MIT. See LICENSE file for details.
<br>

### v1.5.0 [03.26.26]
- Updated to PyFlameLib v5.3.0.
<br>

### v1.4.0 [01.20.24]
- Updates to PySide.
- Fixed scoping issue with Flame 2023.2+ menus.
<br>

### v1.3.0 [90.18.23]
- Updated to pyflame lib v2.0
<br>

### v1.2 [05.31.22]
- Messages print to Flame message window - Flame 2023.1 and later
<br>

### v1.1 [03.15.22]
- Added new message window
