# MASV Uploader for Autodesk Flame

Export sequences or clips from Flame, upload them to [MASV](https://massive.io), and get a password-protected download link — all from the Media Panel.

## Features

- Export selected sequences or clips using a Flame export preset
- Upload to MASV via the REST API (chunked multipart upload)
- Optional password protection with auto-generated passwords
- Optional recipient emails and download limits
- Copyable download URL + password in a results dialog
- Remembers your last-used export preset

## Requirements

- Autodesk Flame 2024.2 or later
- A [MASV](https://massive.io) account with API access
- Python package: `requests` (installed automatically on first Flame launch)

## Installation

Copy the **entire** `masv_uploader` folder — including `lib/`, `config/`, and `presets/` — to a location Flame loads Python scripts from. Common options:

**Site-wide (shared across users on the machine):**

```
/opt/Autodesk/shared/python/masv_uploader/
```

**Per-user (your home folder):**

```
~/flame/python/masv_uploader/
```

Flame scans both of these locations by default on most setups. If your facility uses a custom Python path, install the folder there instead — the uploader resolves config and presets relative to wherever the package lives, so it works from any valid Flame Python directory.

1. Copy the whole `masv_uploader` folder to your chosen path (do not copy individual `.py` files without the rest of the folder).
2. Restart Flame (or run **Refresh Python Hooks** if your site has that option).
3. On first launch, Flame may prompt for your administrator password to install `requests`.
4. Open **Main Menu → MASV Uploader → Edit Config** and complete the setup steps below.

The config editor shows the exact paths on your system for config and presets after installation.

---

## Getting your MASV API Key

You need a MASV API key to create packages and upload files. Only Team Owners, Admins, or Integration Managers can create keys.

### Steps

1. Log in to the [MASV Web App](https://app.massive.io).
2. In the left sidebar, select **Features & Settings**.
3. Under **Team Features**, select **API Keys**.
4. Click **Create API Key**.
5. Enter a name (e.g. `Flame Uploader`) and optional description.
6. Optionally set an expiry date, then click **Create API Key**.
7. **Copy the key immediately** from the confirmation window — MASV only shows it once. Store it somewhere secure.
8. In Flame, open **Main Menu → MASV Uploader → Edit Config** and paste the key into **API Key**.

More detail: [How to create and manage API keys in MASV](https://help.massive.io/en/how-to-create-and-manage-api-keys-in-masv)

---

## Getting your MASV Team ID

The Team ID tells the uploader which MASV team to send packages to.

### Steps

1. Log in to the [MASV Web App](https://app.massive.io).
2. In the left sidebar, use the **Team** drop-down to select the team you want to upload to.
3. Look at the URL in your browser’s address bar. The Team ID is the long alphanumeric string right after `https://app.massive.io/`.

   Example URL:

   ```
   https://app.massive.io/01CWEEY60MREFF7PPYZ82QSQ9J/...
   ```

   In this example, the Team ID is:

   ```
   01CWEEY60MREFF7PPYZ82QSQ9J
   ```

4. Copy that ID and paste it into **Team ID** in **Main Menu → MASV Uploader → Edit Config**.

More detail: [How can I find my Team ID and Portal ID](https://help.massive.io/en/how-can-i-find-my-team-id-and-portal-id)

---

## Default Recipients

In **Edit Config**, you can set **Default Recipients** — one or more email addresses, comma-separated. These are pre-filled in the upload options dialog each time you send a package, so you do not have to retype frequent client or review addresses.

Example:

```
client@studio.com, producer@agency.com
```

You can still add, remove, or change recipients on any individual upload before confirming.

When recipients are included, MASV can notify them when the package is ready. You will still get a direct download link in the results dialog for copying and sharing separately.

---

## Jobs Folder

In **Edit Config**, set **Jobs Folder** to a local path where Flame can write exported files before they are uploaded to MASV. This folder must be writable and have enough space for your exports.

Example:

```
/Volumes/storage/flame_exports
```

Exports are organized as:

```
{jobs_folder}/{project_name}/MASV/{date}/{time}/
```

---

## Export Presets

### Where to put presets

Place Flame export preset files in the `presets/` folder **inside your installed `masv_uploader` package**. For example:

```
/opt/Autodesk/shared/python/masv_uploader/presets/
```

or

```
~/flame/python/masv_uploader/presets/
```

Any `.xml` preset in that folder appears in the **Export Preset** dropdown when you start an upload. The uploader remembers whichever preset you used last. The **Export Presets Folder** path is also shown in **Edit Config**.

### Included presets

This package ships with:

- `ProRes 422 HQ.xml`
- `ProRes 4444.xml`

### Adding your own presets

1. In Flame, create or export an export preset as `.xml` (the same format used by **PyExporter**).
2. Copy the `.xml` file into the `presets/` folder above.
3. Restart Flame or refresh Python hooks if the new preset does not appear immediately.
4. Select it from **Export Preset** in the upload options dialog.

You can add H.264, ProRes, DNx, or any other Flame export preset — the uploader is not limited to a specific codec.

---

## Configuration summary

Open **Main Menu → MASV Uploader → Edit Config**:

| Setting | What to enter |
|---------|----------------|
| **API Key** | Your MASV API key (see above) |
| **Team ID** | Your MASV team ID (see above) |
| **Default Recipients** | Optional comma-separated emails, pre-filled on each upload |
| **Jobs Folder** | Local folder for staging exports before upload |

Settings are saved to `config/shared_config.json` inside your installed package, for example:

```
/opt/Autodesk/shared/python/masv_uploader/config/shared_config.json
```

or

```
~/flame/python/masv_uploader/config/shared_config.json
```

The full path is displayed at the bottom of the **Edit Config** window.

---

## Usage

### Upload a sequence

1. In the Media Panel, select one or more sequences.
2. Right-click → **MASV Uploader → Upload Sequence**.
3. Choose an **Export Preset**, set the package name, password, and other options.
4. Confirm and wait for export and upload to finish.
5. Copy the download URL and password from the results dialog.

### Upload a clip

Same as above, but select clips and choose **Upload Clip**.

---

## Menu locations

| Location | Action |
|----------|--------|
| Media Panel → MASV Uploader | Upload Sequence |
| Media Panel → MASV Uploader | Upload Clip |
| Main Menu → MASV Uploader | Edit Config |

---

## File structure

```
masv_uploader/
├── config/
│   └── shared_config.json       # API key, team ID, recipients, jobs folder
├── lib/
│   ├── masv_api.py              # MASV API client
│   ├── masv_ui.py               # PySide6 dialogs
│   └── masv_packages.py         # Installs `requests` on Flame launch
├── presets/                     # ← Put export preset .xml files here
│   ├── ProRes 422 HQ.xml
│   └── ProRes 4444.xml
├── masv_uploader.py             # Upload script + Media Panel menu
├── masv_config_editor.py        # Config editor + Main Menu entry
└── README.md
```

---

## MASV API reference

- [Getting started](https://developer.massive.io/masv-api/)
- [Uploads](https://developer.massive.io/masv-api/upload/)
- [Links](https://developer.massive.io/masv-api/links/)

---

## License

Provided as-is for the Flame community. Not affiliated with MASV or Autodesk.
