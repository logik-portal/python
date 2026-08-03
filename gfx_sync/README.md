# Gfx Sync

**Script Version:** 1.0.0  
**Flame Version:** 2026.1  
**Written by:** Jeff Kyle  
**Creation Date:** 06.10.26  
**Update Date:** 06.23.26  

## Description

Sync the text of Flame Type (Timeline FX) graphics across many sequences
and aspect-ratio versions from one place. A per-project JSON registry is
the single source of truth for each graphic's text; segments are tagged
'graphicNN' and receive their text from the registry (one-directional:
registry -> tagged Type layers). Layout (position / scale / format) is
handled separately through Flame's native segment connections, so text
and layout are managed independently.
<br><br>
Typical use is broadcast legal / disclaimer lines that must read
identically across 16x9, 9x16, 1x1, 4x5, etc. while each aspect keeps its
own framing -- but it works for any Flame-generated Type graphic.
<br><br>
Install (single file, its own folder, unique name; restart Flame):
/opt/Autodesk/shared/python/gfx_sync/gfx_sync.py
<br><br>
Tabs:
Segments   - scan the scope; see every matching Type segment, its text,
assignment and sync status; assign and capture to registry.
Registry   - add / edit / remove graphic definitions; Sync Text to scope.
Connections- create / remove segment connections across the timeline gfx gaps.
Settings   - registry folder, default scope, what counts as a target
segment (match mode + name / track filters), Segments-tab
defaults (Grouped Text, default sort).
<br><br>
<br><br>
Built by Jeff Kyle with Claude (Anthropic).
<br><br>
Provided as-is, without warranty of any kind. Free to use and modify.

## Menus

- Right-click on a timeline segment  →  GFX Sync  →  GFX Sync...
- Right-click in the Media Panel     →  GFX Sync  →  GFX Sync...
- Flame main menu                    →  GFX Sync  →  Open Manager...
