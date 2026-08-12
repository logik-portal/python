# Collect Media

**Script Version:** 1.0.2  
**Flame Version:** 2023  
**Written by:** Kyle Obley  
**Creation Date:** 08.10.21  
**Update Date:** 12.08.26  

**Script Type:** Media Panel, Media Hub

## Description

Dump a list of every non-cached clip and segment in every sequence and batch in every folder
out to a known location for archiving.
<br><br>
Important / Cavets:
- We can not see into BFX so anything in there will not be caught.
- This will only grab the used version of a versioned clip, not every version.
- This will only grab the latest batch iteration, not previous versions.
- Within batch, only import nodes are seen, not read file nodes.
- Only works on the current workspace.
- Flame returns the path of an image sequence as the first frame in the sequence, not the first frame being
used within said image sequence. For now the safest route is to find the last frame in the sequence on disk
and use that to populate the list.

## Menus

- Flame Main Menu → Collect Media

## Installation

Copy script into /opt/Autodesk/shared/python/collect_media

## Updates

### v1.0.2 [08.12.21]
- Adjusted formating to adhear to Logik-Portal requirements.
<br>

### v1.0.1 [08.11.21]
- Adjusted the custom_location logic and re-arranged the code so directory existance check works for both cases.
<br>
- v1.0
- Merged Chris' 0.9.2 but changed the logic to not include a dated sub-folder for easier backups.
<br>
- Re-incorperated the ability for a custom save location.
<br>
- v0.9.2
- Changed output location to ~/collect_media/{project_name}/{YYYYMMDD}/ for easier access
- and to avoid permission issues. Organized by project and date for better management.
<br>
- Fixes FileNotFoundError by automatically creating directory structure.
<br>
- v0.9
- Added a timestamped backup of a previoous list if found if, for whatever reason, you need to roll-back.
<br>
- v0.8
- Stopped using a UniqueList for all the lists and instead us set() at the end to remove duplicates due to a
- the previous method taking significantly longer. Resulted in a 1000x speed increase. Bonkers.
<br>
- v0.7
- Attempting to speed up the write process for large projects.
<br>
- v0.6
- Fixed the handling of Red files to go up on directory to ensure we grab all the sub-files.
<br>
- Added ability to specify a custom dump file location (custom_dump_location).
<br>
- v0.5
- Added the option to scrape cached media as well.
<br>
- Added more checks during scraping to avoid NoneTypes. Not sure if it's bulletproof though.
<br>
- v0.4
- PySegment.source_cached added to API allowing us the ability to now get the cached
- status of clips in segments including audio.
<br>
- Set the minimum version to 2023.1
<br>
- Removed Python 2.7 support as we now require 2023
<br>
- Added a warning and completion dialog using the built-in message display
<br>
- v0.3
- Current desktop is now scrapped as well.
<br>
- Adjusted the logic to how to account for the totals to reflect de-deplication
- and give a better impression of total number of file sequences.
<br>
- v0.2
- Added compatability for Python 2.7
<br>
- Implemented a class to create a unique list as opposed to dumping everything
- to a list and then using sort to de-dup. Written by Clauss.
<br>
- Re-worked logic of how we manage an existing list.
<br>
- Added audio support. Cached status within a sequence is still an issue.
<br>
- v0.1
- Initial Release
