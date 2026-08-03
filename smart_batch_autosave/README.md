# Smart Batch Autosave

**Script Version:** 1.0.2  
**Flame Version:** 2026.2  
**Written by:** Huseyin Pasaoglu  
**Creation Date:** 07.20.26  
**Update Date:** 07.28.26  

## Description

Background auto-save engine for Batch setups with a PySide6 settings UI.
<br><br>
Silently backs up the current Batch setup on a configurable interval
(1-60 min) using flame.batch.save_setup() — the project itself is never
touched. Each Batch group gets its own subfolder and a rotation policy
keeps the 10 most recent scheduled backups (manual and post-render
snapshots are always preserved). Extra triggers: a one-shot idle backup
when the artist steps away, a forced backup after every Batch render,
and a manual "Snapshot Now" button.
<br><br>
BatchFX aware: when the artist is inside a BFX (detected via
flame.get_current_tab()), the backup is routed to a separate
_BatchFX/<name> tree so it can never overwrite a desktop batch's backups.
<br><br>
Crash-safe: all saves are deferred through flame.schedule_idle_event(),
so save_setup() never fires in the middle of an Archive restore, media
cache or render. A "Pause Auto-Save" button suspends all automatic saves
(auto-resumes on next launch).
<br><br>
The backup destination is fully configurable with tokenized path
templates (<project>, <user>, <batch>). Settings persist to a JSON file
next to the script.
<br><br>
Install: copy this file to /opt/Autodesk/shared/python/ and restart
Flame or refresh python hooks. The engine starts automatically.

## Menus

- Flame Main Menu → Smart Batch Auto-Save → Smart Batch Auto-Save Settings

## Updates

### v1.0.2 [07.28.26]
- Crash fix: automatic saves and manual snapshots now run via
- flame.schedule_idle_event() instead of straight from the timer, so
- save_setup() can no longer fire mid Archive restore / media cache /
- render (the cause of "Pure virtual function called" SIGABRT crashes).
<br>

### v1.0.1 [07.24.26]
- BatchFX aware: the active BFX is saved into its own _BatchFX/<name>
- tree, resolved via flame.get_current_tab(), protecting desktop batch
- backups from being overwritten or rotated out.
- Added "Pause Auto-Save" button (runtime-only, auto-resumes on
- relaunch) for use before Archives / heavy imports / renders.
- Added settings window footer with credit.
<br>

### v1.0.0 [07.20.26]
- Initial release: interval + idle + post-render autosave, per-batch
- folders, retention (keep 10), never-forget retry, editable path
- templates, singleton engine with reload-safe reset.
