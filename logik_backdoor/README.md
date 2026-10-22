# Logik Backdoor

**Script Version:** 1.0.0  
**Flame Version:** 2025.2  
**Written by:** Michael Vaglienty  
**Creation Date:** 10.05.26  
**Update Date:** 10.05.26  

## Description

A bridge allowing other applications to control Flame using provided tools.

## Notes

These examples can be added to 3rd party application export options to import into Flame after
export is complete.
<br><br>
To import an image sequence into a Library:
<br><br>
```
import sys
sys.path.insert(0, '/opt/Autodesk/shared/python/logik_backdoor')
<br><br>
import logik_backdoor_client as backdoor
<br><br>
# Check if Flame is running and the hook is installed. Only call a tool
# when it is.
if not backdoor.available():
print('Flame is not running.')
else:
# Import an image sequence into a Library. The Library is created if it
# is absent, reused if it already exists. timeout is in seconds: allow
# plenty, since a large import can run for minutes and Flame answers
# only when it ends. The Library name is optional and defaults to
# 'Image_Imports'. Prefer image sequences to container video such as
# .mov or .mp4, which Flame can hang on (see readme.md).
result = backdoor.call(
'import_image_to_library',
timeout=600,
path='/media/shot_0010/comp_v003.[1001-1100].exr',
library_name='Image_Imports',
)
<br><br>
# Every call returns a dict. Errors arrive as {'ok': False, 'error': ...}
# rather than as a raised exception, so test ok before reading the rest.
if result['ok']:
print(f"imported {result['count']} clip(s): {result['clips']}")
else:
print(f"import failed: {result['error']}")
```
<br><br>
To import an image sequence onto a schematic reel in the open Batch:
<br><br>
```
import sys
sys.path.insert(0, '/opt/Autodesk/shared/python/logik_backdoor')
<br><br>
import logik_backdoor_client as backdoor
<br><br>
# Check if Flame is running and the hook is installed. Only call a tool
# when it is.
if not backdoor.available():
print('Flame is not running.')
else:
# Import an image sequence onto a schematic reel in the open Batch.
# Give the frame range in Flame's bracket notation so the frames import
# as one clip rather than as several hundred single-frame clips. A
# single image, a folder, or a list of any of these also works, here
# and above. The reel name is optional and defaults to 'image_imports'.
result = backdoor.call(
'import_image_to_batch',
timeout=600,
path='/media/shot_0010/matte.[0001-0240].exr',
reel_name='image_imports',
)
<br><br>
# Every call returns a dict. Errors arrive as {'ok': False, 'error': ...}
# rather than as a raised exception, so test ok before reading the rest.
if result['ok']:
print(f"imported {result['count']} clip(s): {result['clips']}")
else:
print(f"import failed: {result['error']}")
```

## Usage

Runs on Flame startup.
<br><br>
Using the provided tools, other applications can interact with Flame.
<br><br>
Tools:
ping                       Confirm the bridge is alive.
info                       Flame version, current project and workspace.
list_batch_nodes           Nodes in the open Batch, optionally filtered by type.
import_image_to_library    Import media into a Library, created if absent.
import_image_to_batch      Import media onto a schematic reel in the open Batch.
create_node                Create a Batch node, optionally loading a setup file.
import_alembic             Create an Action node and import an Alembic file into it.
reload_node_setup          Save a Batch node's setup and load it back into the same node.
frame_node                 Select Batch nodes by name and frame the schematic on them.
<br><br>
Tools are called by other applications using the logik_backdoor_client.py script.
<br><br>
Each tool is its own file in the tools folder, loaded automatically at
startup. To add a tool, add a file to the tools folder (tools/<name>.py) that defines a
function called <name> returning a dict, with a docstring describing it and an optional TIMEOUT
in seconds.

## URL

https://logik-portal.com/scripts/logik_backdoor

## Installation

Copy script into /opt/Autodesk/shared/python/logik_backdoor

## Updates

### v1.0.0 [10.05.26]
- Initial release.
