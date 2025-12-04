# Add Audio

**Script Version:** 1.4.0  
**Flame Version:** 2023  
**Written by:** Michael Vaglienty  
**Creation Date:** 02.04.22  
**Update Date:** 01.20.24  

**Script Type:** Batch

## Description

Add stereo or 5.1 audio to selected sequences.
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

https://github.com/logik-portal/python/add_audio

## Menus

- Right-click selection of sequences and audio → Audio → Insert Stereo Audio - 01:00:00:00
- Right-click selection of sequences and audio → Audio → Insert Stereo Audio - 00:59:58:00
- Right-click selection of sequences and audio → Audio → Insert 5.1 Audio - 01:00:00:00
- Right-click selection of sequences and audio → Audio → Insert 5.1 Audio - 00:59:58:00

## Installation

Copy script folder into /opt/Autodesk/shared/python

## Updates

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
