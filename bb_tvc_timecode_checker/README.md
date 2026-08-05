# BB TVC Timecode Checker

**Script Version:** 2.1  
**Flame Version:** 2026.1  
**Written by:** Bryan Bayley  
**Creation Date:** 12.02.25  
**Update Date:** 08.04.26  

## Description

Select clips or sequences in the Media Panel to check:
1. Does the record timecode start at 01:00:00:00 - or at a recognized
lead-in start: 59:59:00 (1s black head + tail) or 59:50:00 / 59:53:00
(slate)?
2. Is the duration a standard TVC length (6s, 15s, 30s, 60s, 90s), after
accounting for whatever the start timecode implies is around the
program?
<br><br>
Lead-in layouts are inferred from the start timecode only - the script
cannot see whether a slate or black is really there, so the results dialog
notes when a layout was assumed so it can be confirmed visually.

## Menus

Right-click on clips or sequences in the Media Panel -> TVC Checks... ->
Check Start Timecode and Duration

## Updates

### v2.1 [08.04.26]
- Recognizes black head/tail and slate lead-in layouts from the start
timecode: 59:59:00 assumes 1s of black at head and tail (program + 2s);
59:50:00 / 59:53:00 assume a 10s / 7s slate lead-in with nothing after
the program. The duration check accounts for the assumed layout.
- Condensed results dialog: when everything passes it reports one line per
layout (e.g. "All 4 timelines have 1s black head + tail and are the
correct length"); per-item detail appears only for failures and errors.
- An error while checking one item no longer aborts the remaining items;
errored items are listed in the summary dialog instead.
- Results dialog switched to Qt (PySide6/PySide2 fallback).
