# FrameIO Integration for Autodesk Flame

A comprehensive integration suite for connecting Autodesk Flame with FrameIO, enabling seamless uploads, comment synchronization, and project management within the Uppercut VFX Pipeline.

> **V4 API**: This integration talks to Frame.io's V4 API (`https://api.frame.io/v4`) using
> plain `requests` calls (no SDK). See [Authentication](#authentication) below for details on
> the custom header this account requires.

## Overview

This package provides several Python scripts that integrate FrameIO's review and collaboration platform with Autodesk Flame. The integration supports:

- **Config Management**: Unified global and user configuration editor
- **Conform Uploads**: Automated upload of conform sequences to FrameIO
- **Shot Uploads**: Direct upload of shots/clips to FrameIO
- **Comment Synchronization**: Fetch comments from FrameIO and create Flame markers
- **Status Management**: Get and set FrameIO status labels on Flame clips
- **Automatic Versioning**: Smart version increment based on existing FrameIO assets
- **Share Links**: Generate a client-ready public share link for selected clips/segments, exporting/uploading anything not already in FrameIO

## Requirements

- **Autodesk Flame 2023.2 or later**
- **Python 3** (bundled with Flame)
- **FrameIO Token** (get one from [FrameIO Developer Portal](https://developer.frame.io/))
- **Required Python packages** (automatically installed via `frame_io_packages.py`):
  - `requests`

## Installation

1. **Copy the files** to your Flame Python scripts directory. The scripts resolve all of
   their own paths relative to their own location, so any of the standard Flame script
   locations work — e.g. for a shared, studio-wide install:
   ```
   /opt/Autodesk/shared/python/frame_io/
   ```
   Or for a user-specific installation:
   ```
   ~/flame/python/frame_io/
   ```

2. **Ensure the directory structure** matches:
   ```
   frame_io/
   ├── lib/
   │   ├── frame_io_api.py
   │   └── frame_io_packages.py
   ├── config/
   │   └── shared_config.json  (created on first run via the Config Editor)
   ├── presets/
   │   └── (export presets)
   ├── frame_io_config_editor.py
   ├── frame_io_conform_uploader.py
   ├── frame_io_get_comments.py
   ├── frame_io_get_status.py
   ├── frame_io_set_status.py
   ├── frame_io_shot_uploader.py
   └── frame_io_csv_to_markers.py
   ```

3. **First-time setup**: Launch Flame and use the config editor to set up your FrameIO token (and Client ID, if your account requires it — see [Authentication](#authentication)), account ID, and workspace ID.

## Authentication

This integration authenticates with the Frame.io V4 API using a **legacy developer token**
(`fio-u-...`) as a Bearer credential — there is no OAuth flow, token exchange, or SDK involved.

For most Frame.io accounts, that's all you need. However, accounts that are managed through
the **Adobe Admin Console** reject legacy developer tokens for *account-scoped* V4 endpoints
(projects, workspaces, folders, metadata, etc.) by default, even though the token still works
for `/v4/me`. If your account is in this situation, Frame.io/Adobe support can provision a
scoped **"service client" `client_id`**. When set, every request adds an
`x-frameio-service-client: <client_id>` header alongside the Bearer token, which unlocks
account-scoped calls without needing OAuth Server-to-Server credentials.

Config keys involved:
- `frame_io_token`: your legacy developer token (`fio-u-...`)
- `client_id`: the service-client id from Frame.io/Adobe support (leave blank if not needed)

Use the **Validate Token** button in the Config Editor to check both `/v4/me` and
account-scoped access — it will tell you if a Client ID is required.

## Configuration

### Global Configuration

Global settings are stored at:
```
/opt/Autodesk/shared/python/frame_io/config/shared_config.json
```

**Global Settings:**
- `jobs_folder`: Base path for exported files (default: `/Volumes/vfx/UC_Jobs`)
- `preset_path_h264`: Path to H.264 export preset XML
- `project_token`: Which project identifier to use - `"nickname"` or `"name"` (default: `"nickname"`)
- `debug`: Enable verbose debug logging (default: `false`)
- `enable_file_logging`: Enable file logging to `~/flame/python/frame_io/logs/` (default: `false`)

Additional keys in the same file:
- `frame_io_token`: The FrameIO API token used by everyone on the pipeline (required)
- `client_id`: Service-client id for Adobe Admin Console-managed accounts (optional — see [Authentication](#authentication))
- `frame_io_account_id`: The FrameIO account ID (required)
- `frame_io_workspace_id`: The FrameIO workspace ID (required; `frame_io_team_id` is still accepted as a legacy alias)

This account uses one shared service-client credential for the whole studio rather than
per-artist tokens, so there is no separate per-user config file — everything lives in
`shared_config.json`. If an artist still has a leftover `~/flame/python/frame_io/user_config.json`
(or old `~/flame/python/frame_io/config.xml`) from the V2 per-user-token days, its
`frame_io_token`/`client_id`/`frame_io_account_id`/`frame_io_workspace_id`/`frame_io_team_id`
values are **always ignored** — only `shared_config.json` can supply those — to prevent a
stale personal account/token from silently shadowing the shared one (this caused "Unable to
find project" / 401 / 404 errors for some artists after the V4 migration). Any other, non-auth
keys in that file are still merged in for backward compatibility, and a console warning is
logged if the file is found so it can be deleted. The Config Editor no longer reads or writes it.

### Config Editor

Access the configuration editor from Flame's main menu:
```
Main Menu → UC FrameIO → Edit Config
```

A single-form dialog for editing `shared_config.json`:
- FrameIO Token, Client ID, Account ID, and Workspace (with "Validate Token" auto-populating account/workspace)
- Jobs Folder, H.264 Preset Path, Project Token mode, Debug Mode, File Logging
- **Documentation Links**: Quick access to FrameIO API documentation

## Scripts

### 1. FrameIO Config Editor (`frame_io_config_editor.py`)

**Location**: Main Menu → UC FrameIO → Edit Config

A single-form GUI tool for managing the shared FrameIO configuration. Features:
- One flat form for both auth (token/client ID/account/workspace) and pipeline settings
- Token validation with account/workspace auto-discovery
- Real-time configuration updates
- Support for both project nickname and name token modes

### 2. FrameIO Conform Uploader (`frame_io_conform_uploader.py`)

**Location**: Media Panel → UC FrameIO → Conform Uploader

Uploads selected sequences to FrameIO with automatic versioning:
- Exports sequences to H.264 format
- Automatically increments version numbers (e.g., `v01` → `v02`) if asset exists in FrameIO
- Creates organized folder structure: `FROM_FLAME/YYYY-MM-DD/HHMM/`
- Uploads to FrameIO project's CONFORMS folder
- Progress tracking with detailed status updates

**Usage:**
1. Select one or more sequences in the Media Panel
2. Right-click → UC FrameIO → Conform Uploader
3. Confirm the upload
4. Monitor progress in the progress window

### 3. FrameIO Shot Uploader (`frame_io_shot_uploader.py`)

**Location**: Media Panel → UC FrameIO → Shot Uploader

Uploads selected clips/shots directly to FrameIO:
- Exports clips to H.264 format
- Automatically creates version stacks if matching base name found
- Uploads to FrameIO project's SHOTS folder
- Supports version pattern matching (e.g., `_v01`, `_V01`)

**Usage:**
1. Select one or more clips in the Media Panel
2. Right-click → UC FrameIO → Shot Uploader
3. Files are exported and uploaded automatically

### 4. FrameIO Get Comments (`frame_io_get_comments.py`)

**Location**: 
- Media Panel → UC FrameIO → Get Comments (for sequences)
- Timeline → UC FrameIO → Get Comments (for segments)

Fetches comments from FrameIO and creates Flame markers:
- Searches FrameIO for assets matching sequence/clip names
- Creates markers at comment timestamps
- Includes comment text, author, and replies
- Colors clips/segments with "Address Comments" label
- Supports both sequences and timeline segments
- Caches comments per sequence to avoid duplicate API calls

**Usage:**
1. Select sequences in Media Panel or segments in Timeline
2. Right-click → UC FrameIO → Get Comments
3. Markers are automatically created with comment details

### 5. FrameIO Get Status (`frame_io_get_status.py`)

**Location**: Media Panel → UC FrameIO → Get Status

Fetches status from FrameIO and applies color coding:
- Maps FrameIO statuses to Flame color labels:
  - `approved` → "Approved" (green)
  - `needs_review` → "Needs Review" (orange)
  - `in_progress` → "In Progress" (blue)

**Usage:**
1. Select clips in Media Panel
2. Right-click → UC FrameIO → Get Status
3. Clips are colored based on their FrameIO status

### 6. FrameIO Set Status (`frame_io_set_status.py`)

**Location**: Media Panel → UC FrameIO → Set Status

Sets FrameIO status based on Flame color labels:
- Maps Flame color labels to FrameIO statuses:
  - "Approved" → `approved`
  - "Needs Review" → `needs_review`
  - "In Progress" → `in_progress`

**Usage:**
1. Apply color labels to clips in Flame
2. Select clips in Media Panel
3. Right-click → UC FrameIO → Set Status
4. FrameIO status is updated to match Flame color labels

> **V4 note**: Frame.io V4 has no built-in "label"/status field like V2 did. Status get/set
> instead reads and writes a custom account-level **Metadata** field named `Status` (type
> `select`) with options `Needs Review`, `In Progress`, and `Approved`. This field must already
> exist on the account (Account Settings → Metadata) — the scripts look it up dynamically by
> name and cache the field/option ids, they do not create it for you.

### 7. FrameIO Create Share Link (`frame_io_create_share.py`)

**Location**:
- Media Panel → UC FrameIO → Create Share Link
- Timeline → UC FrameIO → Create Share Link

Creates a single public FrameIO share link covering the selected clips/segments:
- Items already uploaded to FrameIO are matched by name and added to the share directly.
- Items not yet in FrameIO are exported (H264) and uploaded first (same export/upload path
  as the Conform/Shot Uploaders), then added.
- Multiple selected items are combined into **one** share link.
- The resulting link defaults to: public access, downloading enabled, no expiration,
  commenting enabled (Frame.io's default for asset shares — not independently configurable
  via the API).
- The URL is shown in a dialog and copied to the clipboard.

**Usage:**
1. Select one or more clips/segments in Media Panel or Timeline
2. Right-click → UC FrameIO → Create Share Link
3. Missing items are exported and uploaded automatically
4. The share URL is shown in a dialog and copied to your clipboard

> **Note on guest identity**: anyone with a public share link can comment without a FrameIO
> account. Per Frame.io, their name is **not** exposed via the API (see Get Comments' console
> notes for "Unknown" authors) — only visible in the browser share page itself. If you need
> comment attribution to work reliably for client feedback, invite reviewers to a **secure**
> share by name/email instead of relying on the open public link.

### 8. CSV to Markers (`frame_io_csv_to_markers.py`)

**Location**: 
- Media Panel → UC FrameIO → CSV → Timeline Markers
- Timeline → UC FrameIO → CSV → Segment Markers

Imports a CSV file exported from FrameIO and adds markers to clips:
- No need to modify the CSV downloaded from FrameIO
- Supports both timeline markers and segment markers
- Includes comment text and author information

**Usage:**
1. Export comments CSV from FrameIO
2. Select a clip or segment
3. Right-click → UC FrameIO → CSV → Timeline Markers (or Segment Markers)
4. Navigate to the CSV file
5. Markers are automatically created

## Features

### Automatic Versioning

Both uploader scripts support automatic version increment:
- Searches FrameIO for existing assets with matching base name
- If found, automatically increments version number (e.g., `v01` → `v02`)
- Works with both lowercase (`v01`) and uppercase (`V01`) version patterns
- Under the hood, uploads use V4's local-upload flow (create a placeholder file, then `PUT` the
  bytes to one or more presigned S3 URLs) and versioning either moves the new file into an
  existing version stack or creates a new stack from the two files — there's no third-party
  SDK involved.

### Comment Caching

The Get Comments script caches comments per sequence name to avoid duplicate API calls when processing multiple segments from the same sequence.

### Error Handling & Retry Logic

All API operations include:
- Automatic retry with exponential backoff for network errors
- User-friendly error messages with actionable guidance
- Detailed error logging for debugging
- Graceful handling of server errors (429, 500, 502, 503, 504)

### File Logging

Optional file logging for debugging:
- Logs saved to `~/flame/python/frame_io/logs/`
- Daily log files with timestamps
- Includes debug, info, warning, and error levels
- Enable via Config Editor → Global Settings → File Logging

### Progress Tracking

Both uploader scripts include progress indicators:
- Real-time progress bars
- File-by-file status updates
- Overall completion tracking

### Backward Compatibility

The system maintains backward compatibility with XML config files:
- Automatically migrates XML configs to JSON format
- Falls back to XML if JSON doesn't exist
- Supports both old and new config field names

## Troubleshooting

### Config Issues

- **Missing token/account/workspace**: Use the Config Editor (Main Menu → UC FrameIO → Edit Config) to set up your credentials
- **403 "This account does not allow legacy developer tokens"**: Your account is Adobe Admin Console-managed — get a Client ID from Frame.io/Adobe support and add it in the Config Editor (see [Authentication](#authentication))
- **Invalid token**: Use the "Validate Token" button in the Config Editor to test your token
- **Configuration errors**: Check error messages for specific missing fields and use the Config Editor to fix them

### Upload Issues

- **Export preset not found**: Check that `preset_path_h264` in config points to a valid preset file
- **Upload fails**: Verify your FrameIO token has proper permissions for the project
- **Network errors**: The system will automatically retry failed uploads. Check logs for detailed error information
- **Permission denied**: Ensure your FrameIO token has permission to create projects and upload files in the specified workspace

### Comment Issues

- **No comments found**: Ensure sequence/clip names exactly match FrameIO asset names
- **Markers in wrong place**: Check that frame rates match between Flame and FrameIO

### Debugging

- **Enable debug mode**: Use Config Editor → Global Settings → Debug Mode for verbose console output
- **Enable file logging**: Use Config Editor → Global Settings → File Logging to save detailed logs to disk
- **Check log files**: Logs are saved to `~/flame/python/frame_io/logs/` with daily rotation

## Migration from XML Config

If you have an existing XML config file, the system will automatically migrate it to JSON format on first run. The XML file is preserved as a backup.

## Support

For issues or questions, contact the Uppercut VFX Pipeline team.

