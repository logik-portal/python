# Bb Tvc Timecode Checker

**Script Version:** 2.1  
**Flame Version:** 2026.1  
**Written by:** Bryan Bayley  
**Creation Date:** 12.02.25  
**Update Date:** 08.04.26  

## Description

(slate)?
2. Is the duration a standard TVC length (6s, 15s, 30s, 60s, 90s), after
accounting for whatever the start timecode implies is around the
program?
<br><br>
Lead-in layouts are inferred from the start timecode only - the script
cannot see whether a slate or black is really there, so the results dialog
notes when a layout was assumed so it can be confirmed visually.

## Menus

- Right-click on clips or sequences in the Media Panel → TVC Checks... →
- Check Start Timecode and Duration

## Updates

- layout (e.g. "All 4 timelines have 1s black head + tail and are the
- correct length"); per-item detail appears only for failures and errors.
- An error while checking one item no longer aborts the remaining items;
- errored items are listed in the summary dialog instead.
- Results dialog switched to Qt (PySide6/PySide2 fallback).
