# Type Sync

**Script Version:** 1.1.0  
**Flame Version:** 2026.1  
**Written by:** Jeff Kyle  
**Creation Date:** 06.10.26  
**Update Date:** 09.24.26  

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
/opt/Autodesk/shared/python/type_sync/type_sync.py
Upgrading from GFX Sync: delete the old INSTALL folder
/opt/Autodesk/shared/python/gfx_sync/ -- the tool only. Keep the
gfx_sync folder in your projects' setups: it holds your registry, which
Type Sync reads and copies to its new name automatically.
<br><br>
The window doesn't block Flame: keep working with it open, and press
Rescan (on the Scope row) after changing things in Flame.
<br><br>
Tabs:
Segments    - scan the scope; see every matching Type segment, its
text, assignment and sync status; assign Type numbers
and capture text to the registry. Sync Selected /
Sync All fix OUT OF DATE segments right here (every
change is shown first).
Registry    - add / edit / remove graphic definitions; Sync Text to
scope.
Connections - create / remove the segment connections that share a
graphic's layout between sequences of the same aspect.
Auto Connection queues them; Execute Queue runs them.
Every look has a letter: a connected set shares one, a
lone graphic has its own (after Z come AA, AB, ...).
Timelines   - every sequence as a lane, grouped by aspect, with each
Type graphic where it sits in the cut: letter and
colour = its look, number = its Type number. Click
to see its text, where it is and what it's connected
to, with a preview rendered by Flame: Full frame, or
Type only (just the Type over black -- quick on
heavy timelines); Re-render makes a fresh one. The
zoom list, Fit, Text (frames the words), the mouse
wheel and drag-to-pan get you in close; double-click
the picture to Fit. Preview and Details show / hide
the panes; drag the dividers to resize them
(remembered between opens; each frame size keeps its
own zoom). Jump to Flame Segment (or double-click a
graphic) takes Flame there.
Settings    - registry folder, default scope, what counts as a
target segment (match mode + name / track filters),
Segments-tab defaults (Grouped Text, default sort),
and Preview size for the Timelines preview: Native
(the default), 4K, HD or 720 px (fastest). Bigger =
sharper text when zoomed in, a little more time and
disk per render. Changes save as you leave the tab.
<br><br>
<br><br>
Built by Jeff Kyle with Claude (Anthropic).
<br><br>
Provided as-is, without warranty of any kind. Free to use and modify.

## Menus

- Right-click on a timeline segment  →  Type Sync  →  Type Sync...
- Right-click in the Media Panel     →  Type Sync  →  Type Sync...
- Flame main menu                    →  Type Sync  →  Open Manager...

## Updates

### v1.1.0 [09.24.26]
- Renamed from GFX Sync to Type Sync: it works with Flame's Type
- only. Graphic numbers are Type01, Type02... Your GFX Sync
- settings and registries are picked up automatically. Install
- the new type_sync folder and delete the old gfx_sync INSTALL
- folder (otherwise Flame loads both) -- not the gfx_sync folder
- in your projects' setups, which holds your registry.
- The window no longer blocks Flame. Press Rescan after changing
- things in Flame.
- Segments tab: Sync Selected / Sync All push registry text onto
- OUT OF DATE segments, showing every change first.
- Execute Queue re-checks Flame first; if anything changed since
- you reviewed the queue, it redraws the queue and asks you to
- press Execute Queue again.
- Every look gets a letter in the Connections and Timelines tabs.
- New Timelines tab: every sequence as a lane, every Type graphic
- where it sits; click to inspect, double-click to jump there.
- Timelines preview rendered by Flame: Full frame or Type only,
- cached once per look. Zoom list, Fit, Text, mouse wheel zoom and
- drag-to-pan.
- Resizable, hideable preview panes. The layout, the console and
- the window size are remembered between opens.
- Each frame size keeps its own preview zoom.
- Timelines: Show / Filter one Type (Filter lists only the sequences
- that use it). Tips buttons on the Connections and Timelines tabs.
- Settings: Preview size (Native by default, or 4K, HD, 720 px) for
- sharper text when zoomed in. Settings save themselves as you
- leave the tab -- no more Save button.
<br>

### v1.0.1 [09.24.26]
- Version shown in the window header.
- Auto Connection: new segments join an existing connected set
- instead of being dropped or re-copying the set.
- The queue shows exactly what will run; groups that can't run
- are marked with the reason.
- Safer segment identity: a same-named copy of a sequence in
- another reel is no longer mistaken for the live one.
- Split connected sets are reported, not guessed.
- Set as Source works anywhere in the set being joined.
- Break Selected clears the queue.
- Temporary copies made while connecting are cleaned up properly.
<br>

### v1.0.0 [08.02.26]
- First public release.
