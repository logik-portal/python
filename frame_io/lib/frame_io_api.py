#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FrameIO API Helpers — Uppercut VFX Pipeline
Centralized config, API functions, and utilities

V4 API notes
------------
This account is administered via the Adobe Admin Console, which means:
  - A plain legacy developer token (Bearer only) is rejected for V4 calls.
  - The publicly-documented `x-frameio-legacy-token-auth: true` header is
    ALSO rejected for account-scoped V4 calls (it only works for accounts
    that are NOT Adobe Admin Console-managed).
  - Instead, Frame.io support provisioned a scoped "service client":
    send the legacy developer token as the Bearer credential, plus an
    `x-frameio-service-client` header containing `client_id`. This was
    confirmed working live against /v4/me, /v4/accounts, /v4/.../workspaces,
    /v4/.../projects, /v4/.../folders, and /v4/.../metadata/field_definitions.

No OAuth token exchange, refresh, or SDK is needed — this module still uses
plain `requests`, just retargeted from /v2/* to /v4/* with the header above.
"""

import os
import json
import mimetypes
import xml.etree.ElementTree as ET
import requests
import logging
from datetime import datetime
from pathlib import Path

# ---------------------------------------------------------------------
# Config locations
# ---------------------------------------------------------------------

# Derived from this file's own location (lib/frame_io_api.py -> frame_io/)
# rather than hardcoded, so the package works from any install path.
SCRIPT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GLOBAL_CONFIG_PATH = os.path.join(SCRIPT_PATH, "config", "shared_config.json")
USER_CONFIG_PATH = os.path.expanduser("~/flame/python/frame_io/user_config.json")
LEGACY_XML_CONFIG_PATH = os.path.join(SCRIPT_PATH, "config", "config.xml")
LEGACY_USER_XML_CONFIG_PATH = os.path.expanduser("~/flame/python/frame_io/config.xml")
LOG_DIR = os.path.expanduser("~/flame/python/frame_io/logs")

DEFAULT_CONFIG = {
    "frame_io_token": "",
    "client_id": "",
    "frame_io_account_id": "",
    "frame_io_workspace_id": "",
    "frame_io_team_id": "",
    "jobs_folder": "/Volumes/vfx/UC_Jobs",
    "preset_path_h264": os.path.join(SCRIPT_PATH, "presets", "Blu-ray (1080p 20Mbits).xml"),
    "project_token": "nickname",
    "debug": False,
    "enable_file_logging": False,
}

# ---------------------------------------------------------------------
# V4 API constants
# ---------------------------------------------------------------------

V4_BASE = "https://api.frame.io/v4"

# ---------------------------------------------------------------------
# Logging Setup
# ---------------------------------------------------------------------

_logger = None
_file_handler = None

def _setup_logging(cfg):
    """Setup file logging if enabled in config."""
    global _logger, _file_handler
    
    if not cfg.get("enable_file_logging", False):
        if _file_handler and _logger:
            _logger.removeHandler(_file_handler)
            _file_handler = None
        return
    
    if _logger is None:
        _logger = logging.getLogger("frame_io")
        _logger.setLevel(logging.DEBUG)
    
    if _file_handler is None:
        # Create log directory if it doesn't exist
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # Create log file with timestamp
        log_file = os.path.join(LOG_DIR, f"frame_io_{datetime.now().strftime('%Y%m%d')}.log")
        _file_handler = logging.FileHandler(log_file)
        _file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        _file_handler.setFormatter(formatter)
        _logger.addHandler(_file_handler)

def debug_print(cfg, msg):
    """Print debug message if debug mode is enabled."""
    if cfg.get("debug", False):
        print(f"[frame_io_api DEBUG] {msg}")
    if _logger:
        _logger.debug(msg)

def log(msg, level="info"):
    """Log message to console and optionally to file."""
    print(f"[frame_io_api] {msg}")
    if _logger:
        if level == "error":
            _logger.error(msg)
        elif level == "warning":
            _logger.warning(msg)
        elif level == "debug":
            _logger.debug(msg)
        else:
            _logger.info(msg)

def log_error(msg, exc_info=None):
    """Log error with optional exception info."""
    print(f"[frame_io_api ERROR] {msg}")
    if _logger:
        _logger.error(msg, exc_info=exc_info)

# ---------------------------------------------------------------------
# Load + Merge Configs
# ---------------------------------------------------------------------

def _load_json(path):
    """Load config from JSON file."""
    try:
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
    except Exception as e:
        print(f"[frame_io_api] WARNING: Failed to load {path}: {e}")
    return {}

def _load_xml_config(path):
    """Load config from XML file (legacy support)."""
    try:
        if os.path.exists(path):
            tree = ET.parse(path)
            root = tree.getroot()
            cfg = {}
            for setting in root.iter("frame_io_settings"):
                cfg["frame_io_token"] = setting.find("token").text or ""
                cfg["frame_io_account_id"] = setting.find("account_id").text or ""
                cfg["frame_io_team_id"] = setting.find("team_id").text or ""
                cfg["jobs_folder"] = setting.find("jobs_folder").text or DEFAULT_CONFIG["jobs_folder"]
                cfg["preset_path_h264"] = setting.find("preset_path_h264").text or DEFAULT_CONFIG["preset_path_h264"]
            return cfg
    except Exception as e:
        print(f"[frame_io_api] WARNING: Failed to load XML {path}: {e}")
    return {}

def _migrate_xml_to_json(xml_path, json_path):
    """Migrate XML config to JSON format."""
    try:
        xml_cfg = _load_xml_config(xml_path)
        if xml_cfg:
            # Ensure directory exists
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            # Write JSON config
            with open(json_path, "w") as f:
                json.dump(xml_cfg, f, indent=2)
            log(f"Migrated XML config to JSON: {json_path}")
            return True
    except Exception as e:
        log(f"WARNING: Failed to migrate XML to JSON: {e}")
    return False


# V4 uses one shared service-client token/account for the whole team (see
# module docstring) — there is no longer a per-user Frame.io identity, so
# these auth-critical fields must always come from the shared config only.
# A leftover per-user config (or its legacy XML) from the old V2 per-user
# token model must NEVER be allowed to override them.
_AUTH_FIELDS = (
    "frame_io_token", "token",
    "client_id",
    "frame_io_account_id", "account_id",
    "frame_io_workspace_id", "workspace_id",
    "frame_io_team_id", "team_id",
)

def _strip_auth_fields(cfg):
    return {k: v for k, v in cfg.items() if k not in _AUTH_FIELDS}

def validate_config():
    """Merge global, user, and legacy configs, ensuring FrameIO token exists."""
    cfg = DEFAULT_CONFIG.copy()

    # 1. Try to load JSON configs first. The per-user config may only
    # contribute non-auth fields (see _strip_auth_fields) — auth always
    # comes from the shared GLOBAL_CONFIG_PATH.
    if os.path.exists(GLOBAL_CONFIG_PATH):
        cfg.update(_load_json(GLOBAL_CONFIG_PATH))
    if os.path.exists(USER_CONFIG_PATH):
        stale_user_cfg = _strip_auth_fields(_load_json(USER_CONFIG_PATH))
        if stale_user_cfg:
            cfg.update(stale_user_cfg)

    # 2. If JSON doesn't exist but XML does, migrate it
    if not os.path.exists(GLOBAL_CONFIG_PATH) and os.path.exists(LEGACY_XML_CONFIG_PATH):
        _migrate_xml_to_json(LEGACY_XML_CONFIG_PATH, GLOBAL_CONFIG_PATH)
        if os.path.exists(GLOBAL_CONFIG_PATH):
            cfg.update(_load_json(GLOBAL_CONFIG_PATH))

    # NOTE: deliberately NOT auto-migrating a per-user legacy config.xml
    # anymore — those files contain each artist's old personal V2 token/
    # account_id, which must never resurface and shadow the shared V4
    # service-client credentials. Warn instead, so stale files are visible.
    if os.path.exists(USER_CONFIG_PATH) or os.path.exists(LEGACY_USER_XML_CONFIG_PATH):
        stale_path = USER_CONFIG_PATH if os.path.exists(USER_CONFIG_PATH) else LEGACY_USER_XML_CONFIG_PATH
        log(
            f"NOTE: Found a leftover per-user config at '{stale_path}'. FrameIO now "
            "uses one shared account/token for everyone, so any token/account/workspace "
            "id in that file is ignored. You can safely delete it.",
            "warning",
        )

    # 3. Normalize field names (support both old and new naming)
    if "token" in cfg and not cfg.get("frame_io_token"):
        cfg["frame_io_token"] = cfg.pop("token")
    if "account_id" in cfg and not cfg.get("frame_io_account_id"):
        cfg["frame_io_account_id"] = cfg.pop("account_id")
    if "team_id" in cfg and not cfg.get("frame_io_team_id"):
        cfg["frame_io_team_id"] = cfg.pop("team_id")
    # "Team" was renamed "Workspace" in V4; frame_io_team_id is the same
    # underlying UUID, so fall back to it if frame_io_workspace_id isn't set.
    if not cfg.get("frame_io_workspace_id"):
        cfg["frame_io_workspace_id"] = cfg.get("workspace_id") or cfg.get("frame_io_team_id") or ""

    # 4. Validate required fields (check both old and new field names)
    token = cfg.get("frame_io_token") or cfg.get("token")
    account_id = cfg.get("frame_io_account_id") or cfg.get("account_id")
    workspace_id = cfg.get("frame_io_workspace_id") or cfg.get("frame_io_team_id")

    # 5. Setup logging if enabled
    _setup_logging(cfg)

    # 6. Validate with user-friendly error messages
    errors = []
    if not token:
        errors.append("FrameIO token is missing. Please configure it in the Config Editor (Main Menu → UC FrameIO → Edit Config).")
    if not account_id:
        errors.append("FrameIO account ID is missing. Please configure it in the Config Editor.")
    if not workspace_id:
        errors.append("FrameIO workspace ID (formerly Team ID) is missing. Please configure it in the Config Editor.")
    
    if errors:
        error_msg = "\n".join(f"  • {e}" for e in errors)
        raise RuntimeError(f"Configuration Error:\n{error_msg}")

    # 7. Normalize to new field names for consistent access
    cfg["frame_io_token"] = token
    cfg["frame_io_account_id"] = account_id
    cfg["frame_io_workspace_id"] = workspace_id
    cfg["frame_io_team_id"] = workspace_id
    cfg["project_token"] = cfg.get("project_token", "nickname")
    cfg["debug"] = bool(cfg.get("debug", False))
    cfg["enable_file_logging"] = bool(cfg.get("enable_file_logging", False))

    return cfg

# ---------------------------------------------------------------------
# validate_cfg – UI-friendly, full API validation
# Returns: (ok: bool, message: str, merged_cfg: dict)
# ---------------------------------------------------------------------
def validate_cfg(global_cfg: dict, user_cfg: dict):
    """
    Validate FrameIO config AND token via live V4 API calls.
    This is for the Config Editor UI (not for runtime scripts).
    
    Returns:
        (ok, message, merged_cfg)
    """

    merged = {}

    # ---- 1. Merge configs (UI supplies these dicts) ------------------
    merged.update(global_cfg or {})
    merged.update(user_cfg or {})

    # Normalize field names
    token = merged.get("frame_io_token") or merged.get("token")
    client_id = merged.get("client_id") or ""
    account_id = merged.get("frame_io_account_id") or merged.get("account_id")
    workspace_id = merged.get("frame_io_workspace_id") or merged.get("frame_io_team_id") or merged.get("team_id")

    merged["frame_io_token"] = token or ""
    merged["client_id"] = client_id
    merged["frame_io_account_id"] = account_id or ""
    merged["frame_io_workspace_id"] = workspace_id or ""

    # ---- 2. Validate token field presence ----------------------------
    if not token:
        return False, "Missing FrameIO API token.", merged

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    if client_id:
        headers["x-frameio-service-client"] = client_id

    # ---- 3. Validate token by calling /v4/me -------------------------
    try:
        r = requests.get(f"{V4_BASE}/me", headers=headers, timeout=10)
    except Exception as e:
        return False, f"Network error: {e}", merged

    if r.status_code == 401:
        return False, "Invalid FrameIO token (401 Unauthorized).", merged

    if r.status_code != 200:
        hint = ""
        if r.status_code == 403 and "legacy" in r.text.lower() and not client_id:
            hint = (
                " This looks like an Adobe Admin Console-managed account — "
                "try entering a Client ID as well (see your Frame.io/Adobe support ticket)."
            )
        return False, f"Unexpected API response: {r.status_code} {r.text[:160]}{hint}", merged

    try:
        me = r.json().get("data", {})
    except Exception:
        return False, "Invalid JSON from FrameIO API (/v4/me).", merged

    # ---- 4. Fetch accounts ---------------------------------------------
    try:
        r_accounts = requests.get(f"{V4_BASE}/accounts", headers=headers, timeout=10)
    except Exception as e:
        return False, f"Network error fetching accounts: {e}", merged

    if r_accounts.status_code == 403 and not client_id:
        return False, (
            "Token authenticated (/v4/me OK), but this account rejects legacy "
            "developer tokens for account-scoped calls (403 on /v4/accounts). "
            "This is an Adobe Admin Console-managed account — enter the Client ID "
            "provided by Frame.io/Adobe support and try again."
        ), merged

    accounts_data = r_accounts.json().get("data", []) if r_accounts.status_code == 200 else []

    if not account_id and accounts_data:
        account_id = accounts_data[0]["id"]
        merged["frame_io_account_id"] = account_id

    # ---- 5. Fetch workspaces for the resolved account ------------------
    workspaces_list = []
    if account_id:
        try:
            r_ws = requests.get(
                f"{V4_BASE}/accounts/{account_id}/workspaces", headers=headers, timeout=10
            )
            if r_ws.status_code == 200:
                for w in r_ws.json().get("data", []):
                    workspaces_list.append({"id": w["id"], "name": w.get("name", "Unnamed Workspace")})
        except Exception:
            pass

    merged["frame_io_workspaces"] = workspaces_list
    # Kept for backward compatibility with any older UI code referencing "teams"
    merged["frame_io_teams"] = workspaces_list

    # ---- 6. Auto-select workspace if not already chosen ----------------
    if not merged.get("frame_io_workspace_id") and workspaces_list:
        merged["frame_io_workspace_id"] = workspaces_list[0]["id"]
    merged["frame_io_team_id"] = merged["frame_io_workspace_id"]

    who = me.get("email") or me.get("name") or "FrameIO user"
    return True, f"FrameIO token validated successfully (authenticated as {who}).", merged


# ---------------------------------------------------------------------
# Headers / Pagination Helpers
# ---------------------------------------------------------------------

def get_headers(cfg):
    """Get standard FrameIO V4 API headers.

    Adds the `x-frameio-service-client` header (client_id) alongside the
    Bearer token when a client_id is configured. This is a support-provisioned
    mechanism required by this account (Adobe Admin Console-managed) to use
    legacy developer tokens against account-scoped V4 endpoints — the
    publicly documented `x-frameio-legacy-token-auth: true` header does not
    work here. See frame_io_v4_diagnostic.py for the live probe that
    confirmed this.
    """
    token = cfg.get("frame_io_token") or cfg.get("token")
    if not token:
        raise RuntimeError("FrameIO token missing in config.")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }
    client_id = cfg.get("client_id")
    if client_id:
        headers["x-frameio-service-client"] = client_id
    return headers


def _paginate(cfg, url, params=None, timeout=20):
    """GET all pages of a V4 list endpoint, following `links.next`."""
    headers = get_headers(cfg)
    items = []
    while url:
        response = requests.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
        body = response.json()
        items.extend(body.get("data") or [])
        next_link = (body.get("links") or {}).get("next")
        url = f"https://api.frame.io{next_link}" if next_link else None
        params = None  # query params are already baked into `next_link`
    return items

# ---------------------------------------------------------------------
# Error Handling & Retry Logic
# ---------------------------------------------------------------------

def _retry_request(func, max_retries=3, delay=1, *args, **kwargs):
    """Retry a request function with exponential backoff."""
    import time
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            if attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                log(f"Request failed (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...", "warning")
                time.sleep(wait_time)
            else:
                log_error(f"Request failed after {max_retries} attempts: {e}", exc_info=True)
                raise RuntimeError(f"Network error: Unable to connect to FrameIO API after {max_retries} attempts. Please check your internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                wait_time = delay * (2 ** attempt)
                log(f"Server error {e.response.status_code} (attempt {attempt + 1}/{max_retries}), retrying in {wait_time}s...", "warning")
                time.sleep(wait_time)
            else:
                log_error(f"HTTP error: {e}", exc_info=True)
                raise
        except Exception as e:
            log_error(f"Unexpected error: {e}", exc_info=True)
            raise

# ---------------------------------------------------------------------
# Project Helpers
# ---------------------------------------------------------------------

def get_fio_projects(cfg, project_name):
    """Get FrameIO Project ID using the Flame Project Name.

    Returns (root_folder_id, project_id). Kept as a 2-tuple (with the
    historical local variable name `root_asset_id` in callers) for
    backward compatibility — in V4 this value is a root *folder* id.
    """
    account_id = cfg.get("frame_io_account_id")
    workspace_id = cfg.get("frame_io_workspace_id") or cfg.get("frame_io_team_id")

    url = f"{V4_BASE}/accounts/{account_id}/workspaces/{workspace_id}/projects"

    def _make_request():
        return _paginate(cfg, url)

    try:
        projects = _retry_request(_make_request)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to fetch FrameIO projects: {e}")

    for project in projects:
        if project.get("name") == project_name:
            root_folder_id = project.get("root_folder_id")
            project_id = project.get("id")
            log(f"Found FrameIO project '{project_name}': {project_id}")
            return (root_folder_id, project_id)

    raise RuntimeError(f"FrameIO project '{project_name}' not found. Please ensure the project name matches exactly in FrameIO.")

def create_fio_project(cfg, project_name):
    """Create a new FrameIO project."""
    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")
    workspace_id = cfg.get("frame_io_workspace_id") or cfg.get("frame_io_team_id")

    url = f"{V4_BASE}/accounts/{account_id}/workspaces/{workspace_id}/projects"
    payload = {"data": {"name": project_name}}

    log(f"Creating FrameIO project '{project_name}'...")

    def _make_request():
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        return response.json()

    try:
        data = _retry_request(_make_request)
    except RuntimeError:
        raise
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            raise RuntimeError(f"Permission denied: Your FrameIO token doesn't have permission to create projects in workspace {workspace_id}.")
        raise RuntimeError(f"Failed to create FrameIO project: {e}")
    except Exception as e:
        raise RuntimeError(f"Failed to create FrameIO project '{project_name}': {e}")

    project = data.get("data", {})
    root_folder_id = project.get("root_folder_id")
    project_id = project.get("id")
    log(f"Created FrameIO project '{project_name}': {project_id}")

    _PROJECT_ROOT_FOLDER_CACHE[project_id] = root_folder_id
    return (root_folder_id, project_id)

# ---------------------------------------------------------------------
# Folder Management
# ---------------------------------------------------------------------

def create_fio_folder(cfg, parent_folder_id, folder_name):
    """Create a FrameIO folder under `parent_folder_id`."""
    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")

    url = f"{V4_BASE}/accounts/{account_id}/folders/{parent_folder_id}/folders"
    payload = {"data": {"name": folder_name}}

    log(f"Creating FrameIO folder '{folder_name}'...")
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    data = response.json().get("data", {})

    folder_id = data.get("id")
    log(f"Created FrameIO folder '{folder_name}': {folder_id}")
    _invalidate_project_index_cache()
    return folder_id

# ---------------------------------------------------------------------
# Project-wide Asset Search
#
# V2 had a global `/v2/search/assets` endpoint scoped by project_id/team_id.
# V4 has no directly equivalent project-scoped search, so instead we walk
# the project's folder tree (starting at its root folder) and build a flat,
# cached index of every file/folder/version_stack in it. This is rebuilt at
# most once per project per script run (folders/files created via this
# module invalidate the cache automatically).
# ---------------------------------------------------------------------

_PROJECT_ROOT_FOLDER_CACHE = {}
_PROJECT_INDEX_CACHE = {}
_MAX_FOLDERS_TO_WALK = 300  # safety cap against runaway/misconfigured trees

def _invalidate_project_index_cache(project_id=None):
    if project_id is None:
        _PROJECT_INDEX_CACHE.clear()
    else:
        _PROJECT_INDEX_CACHE.pop(project_id, None)

def _get_project_root_folder_id(cfg, project_id):
    if project_id in _PROJECT_ROOT_FOLDER_CACHE:
        return _PROJECT_ROOT_FOLDER_CACHE[project_id]
    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/projects/{project_id}"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    root_folder_id = response.json().get("data", {}).get("root_folder_id")
    _PROJECT_ROOT_FOLDER_CACHE[project_id] = root_folder_id
    return root_folder_id

def _list_folder_children(cfg, folder_id):
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/folders/{folder_id}/children"
    return _paginate(cfg, url, params={"page_size": 50})

def _build_project_index(cfg, project_id):
    """Breadth-first walk of a project's folder tree.

    Returns a flat list of dicts: {type, id, name, parent_id, file_id}
    where `file_id` is always the file-level id to use for metadata/comments
    calls (same as `id` for plain files, the head version's id for
    version_stacks — version_stacks themselves have no metadata/comments).
    """
    root_folder_id = _get_project_root_folder_id(cfg, project_id)
    if not root_folder_id:
        return []

    index = []
    to_visit = [root_folder_id]
    visited_folders = 0

    while to_visit:
        if visited_folders >= _MAX_FOLDERS_TO_WALK:
            log(
                f"WARNING: Stopped walking project {project_id}'s folder tree after "
                f"{_MAX_FOLDERS_TO_WALK} folders (safety cap). Some deeply nested "
                "assets may not be found.",
                "warning",
            )
            break

        folder_id = to_visit.pop(0)
        visited_folders += 1
        try:
            children = _list_folder_children(cfg, folder_id)
        except Exception as e:
            log(f"WARNING: Failed to list children of folder {folder_id}: {e}", "warning")
            continue

        for item in children:
            item_type = item.get("type")
            item_id = item.get("id")
            entry = {
                "type": item_type,
                "id": item_id,
                "name": item.get("name") or "",
                "parent_id": item.get("parent_id") or folder_id,
            }
            if item_type == "version_stack":
                entry["file_id"] = (item.get("head_version") or {}).get("id")
            elif item_type == "file":
                entry["file_id"] = item_id
            else:
                entry["file_id"] = None

            if item_type == "folder":
                to_visit.append(item_id)
            index.append(entry)

    return index

def _get_project_index(cfg, project_id, force_refresh=False):
    if force_refresh or project_id not in _PROJECT_INDEX_CACHE:
        _PROJECT_INDEX_CACHE[project_id] = _build_project_index(cfg, project_id)
    return _PROJECT_INDEX_CACHE[project_id]


def find_fio_asset(cfg, project_id, base_name, asset_type="file"):
    """Search a project (recursively, via cached folder-tree index) for an
    asset by name.

    Uses a preference order:
    1) Exact name match
    2) Case-insensitive exact match
    3) Partial (base_name contained in asset name)

    `asset_type="file"` (the default) means "a content asset" and matches
    both plain files AND version_stacks — once a file has been versioned in
    V4, it becomes a version_stack, so excluding those would silently miss
    every asset with more than one version. Pass `asset_type="folder"` (see
    `find_fio_folder`) to search folders instead, or `asset_type=None` to
    match anything.

    Returns (asset_type, asset_id, parent_id, file_id) or
    (None, None, None, None) on no match. `asset_id` is the "file" id or
    "version_stack" id (used for uploading/versioning); `file_id` is always
    the underlying file id to use for metadata/comments calls.
    """
    try:
        index = _get_project_index(cfg, project_id)
    except Exception as e:
        log_error(f"Failed to build FrameIO project index for search: {e}", exc_info=True)
        return (None, None, None, None)

    if not index:
        return (None, None, None, None)

    exact_match = None
    ci_match = None
    partial_match = None
    base_lower = base_name.lower()

    for item in index:
        item_type = item.get("type")
        if asset_type == "file":
            if item_type not in ("file", "version_stack"):
                continue
        elif asset_type and item_type != asset_type:
            continue

        name = (item.get("name") or "").strip()
        name_lower = name.lower()

        if name == base_name:
            exact_match = item
            break
        if name_lower == base_lower and ci_match is None:
            ci_match = item
        if base_lower in name_lower and partial_match is None:
            partial_match = item

    item = exact_match or ci_match or partial_match
    if not item:
        return (None, None, None, None)

    log(
        "[FrameIO] "
        f"Search results for matching base name asset ID: {item['id']}"
    )

    return (item.get("type"), item.get("id"), item.get("parent_id"), item.get("file_id"))


def find_fio_folder(cfg, project_id, folder_name):
    """Search for a FrameIO folder by name."""
    return find_fio_asset(cfg, project_id, folder_name, asset_type="folder")

# ---------------------------------------------------------------------
# Version Stacks
# ---------------------------------------------------------------------

def add_version(cfg, existing_item_type, existing_item_id, new_file_id, folder_id):
    """Add `new_file_id` as the next version of an existing file/version_stack.

    - existing_item_type == "version_stack": move the new file into the
      existing stack (V4 resolves stack ordering internally).
    - otherwise ("file"): create a brand new version stack containing both
      the existing file and the new file, inside `folder_id`.

    Returns the version_stack id.
    """
    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")

    if existing_item_type == "version_stack":
        url = f"{V4_BASE}/accounts/{account_id}/files/{new_file_id}/move"
        payload = {"data": {"parent_id": existing_item_id}}
        response = requests.patch(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        log(f"Moved file {new_file_id} into existing version stack {existing_item_id}")
        return existing_item_id

    url = f"{V4_BASE}/accounts/{account_id}/folders/{folder_id}/version_stacks"
    payload = {"data": {"file_ids": [existing_item_id, new_file_id]}}
    response = requests.post(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    stack_id = response.json().get("data", {}).get("id")
    log(f"Created version stack {stack_id}: {existing_item_id} -> {new_file_id}")
    _invalidate_project_index_cache()
    return stack_id

# ---------------------------------------------------------------------
# File Upload (V4 local-upload flow: create placeholder -> PUT to S3)
# ---------------------------------------------------------------------

def upload_file(cfg, folder_id, filepath, progress_callback=None):
    """Upload a local file into `folder_id` and return the new file's id.

    V4 uploads are two-step: create a placeholder File resource (which
    returns one or more presigned S3 `upload_urls`, chunked by file size),
    then PUT the file's bytes to each URL in order with the
    `x-amz-acl: private` header.

    `progress_callback(uploaded_bytes, total_bytes)` is called after each
    chunk, if provided.
    """
    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")

    name = os.path.basename(filepath)
    size = os.path.getsize(filepath)
    media_type = mimetypes.guess_type(name)[0] or "application/octet-stream"

    url = f"{V4_BASE}/accounts/{account_id}/folders/{folder_id}/files/local_upload"
    payload = {"data": {"name": name, "file_size": size}}

    def _create_placeholder():
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json().get("data", {})

    try:
        data = _retry_request(_create_placeholder)
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Failed to start FrameIO upload for '{name}': {e}")

    file_id = data.get("id")
    upload_urls = data.get("upload_urls") or []
    if not file_id or not upload_urls:
        raise RuntimeError(f"FrameIO did not return an upload target for '{name}'.")

    uploaded_bytes = 0
    put_headers = {"x-amz-acl": "private", "Content-Type": media_type}

    with open(filepath, "rb") as f:
        for chunk_info in upload_urls:
            chunk_size = chunk_info["size"]
            chunk_url = chunk_info["url"]
            chunk_data = f.read(chunk_size)
            if not chunk_data:
                break

            def _put_chunk():
                r = requests.put(chunk_url, data=chunk_data, headers=put_headers, timeout=300)
                r.raise_for_status()
                return r

            _retry_request(_put_chunk)
            uploaded_bytes += len(chunk_data)
            if progress_callback:
                try:
                    progress_callback(uploaded_bytes, size)
                except Exception:
                    pass

    log(f"Uploaded '{name}' ({size} bytes) -> file_id {file_id}")
    _invalidate_project_index_cache()
    return file_id

# ---------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------

def get_asset_comments(cfg, file_id, include_replies=True):
    """Fetch top-level comments (with nested replies, if requested) for a file."""
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/files/{file_id}/comments"
    params = {
        "include": "owner,replies" if include_replies else "owner",
        "page_size": 50,
    }

    data = _paginate(cfg, url, params=params, timeout=20)

    log(f"Retrieved {len(data)} comment(s) for file {file_id}")
    return data


def create_share_link(
    cfg,
    project_id,
    asset_ids,
    name,
    access="public",
    downloading_enabled=False,
    expiration=None,
    passphrase=None,
):
    """Create a Frame.io V4 share link containing one or more assets
    (file, folder, and/or version_stack ids).

    `access` is "public" (anyone with the link) or "secure" (invite-only
    reviewers). `expiration` is an ISO-8601 UTC timestamp string, or None
    for no expiration.

    Returns the share dict (includes `short_url`, `id`, etc.).
    """
    if not asset_ids:
        raise ValueError("create_share_link requires at least one asset id.")

    account_id = cfg.get("frame_io_account_id")
    headers = get_headers(cfg)
    url = f"{V4_BASE}/accounts/{account_id}/projects/{project_id}/shares"

    data = {
        "type": "asset",
        "access": access,
        "name": name,
        "asset_ids": list(asset_ids),
        "downloading_enabled": bool(downloading_enabled),
    }
    if expiration:
        data["expiration"] = expiration
    if passphrase:
        data["passphrase"] = passphrase

    response = requests.post(url, headers=headers, json={"data": data}, timeout=20)
    response.raise_for_status()
    share = response.json().get("data") or {}
    log(f"Created FrameIO share '{name}': {share.get('short_url')}")
    return share

def get_comment_owner(cfg, comment_id):
    """Fetch the owner of a single comment/reply by id.

    V4's file-comments list endpoint only embeds `owner` on top-level
    comments — nested `replies` come back without an owner at all (this
    matches Frame.io's own schema: replies use the bare `Comment` type, not
    `CommentWithIncludes`). Fetching the reply directly via the single
    "show comment" endpoint with `include=owner` does return it, so this is
    used as a per-reply fallback lookup. Returns the owner dict, or None.
    """
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/comments/{comment_id}"
    headers = get_headers(cfg)
    try:
        response = requests.get(url, headers=headers, params={"include": "owner"}, timeout=20)
        response.raise_for_status()
        return (response.json().get("data") or {}).get("owner")
    except Exception as e:
        log(f"WARNING: Failed to fetch owner for comment {comment_id}: {e}", "warning")
        return None

# ---------------------------------------------------------------------
# Status Management (V4: custom account-level Metadata field, not a
# built-in file "label" like V2)
# ---------------------------------------------------------------------

_STATUS_FIELD_CACHE = {}

def _normalize_status_key(display_name):
    return (display_name or "").strip().lower().replace(" ", "_")

def _get_status_field(cfg):
    """Locate the account's "Status" select metadata field and build
    id <-> internal-key maps for its options.

    Returns (field_definition_id, id_by_key, key_by_id).
    """
    account_id = cfg.get("frame_io_account_id")
    if account_id in _STATUS_FIELD_CACHE:
        return _STATUS_FIELD_CACHE[account_id]

    url = f"{V4_BASE}/accounts/{account_id}/metadata/field_definitions"
    fields = _paginate(cfg, url, params={"page_size": 50})

    status_field = next(
        (f for f in fields if f.get("name") == "Status" and f.get("field_type") == "select"),
        None,
    )
    if not status_field:
        raise RuntimeError(
            "No 'Status' select Metadata field found on this FrameIO account. "
            "Ask your Frame.io admin to create one (Account Settings -> Metadata) "
            "with options for Approved / Needs Review / In Progress."
        )

    field_definition_id = status_field["id"]
    options = (status_field.get("field_configuration") or {}).get("options", [])
    id_by_key = {}
    key_by_id = {}
    for opt in options:
        key = _normalize_status_key(opt.get("display_name"))
        id_by_key[key] = opt["id"]
        key_by_id[opt["id"]] = key

    result = (field_definition_id, id_by_key, key_by_id)
    _STATUS_FIELD_CACHE[account_id] = result
    return result

def get_asset_status(cfg, file_id):
    """Get the status of a file, as one of 'approved' / 'needs_review' /
    'in_progress' (or None if unset), matching the V2 label values used
    throughout the pipeline scripts."""
    field_definition_id, _id_by_key, key_by_id = _get_status_field(cfg)

    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/files/{file_id}/metadata"
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    metadata = response.json().get("data", {}).get("metadata", [])

    for field in metadata:
        if field.get("field_definition_id") == field_definition_id:
            values = field.get("value") or []
            if values:
                return key_by_id.get(values[0].get("id"))
            return None

    return None

def set_asset_status(cfg, project_id, file_id, status):
    """Set the status of a file via the account's 'Status' Metadata field.

    `status` must be one of the internal keys returned by get_asset_status
    (e.g. 'approved', 'needs_review', 'in_progress').
    """
    field_definition_id, id_by_key, _key_by_id = _get_status_field(cfg)
    option_id = id_by_key.get(status)
    if not option_id:
        raise RuntimeError(
            f"Unknown status '{status}'. Available options: {', '.join(id_by_key.keys())}"
        )

    headers = get_headers(cfg)
    account_id = cfg.get("frame_io_account_id")
    url = f"{V4_BASE}/accounts/{account_id}/projects/{project_id}/metadata/values"
    payload = {
        "data": {
            "file_ids": [file_id],
            "values": [{"field_definition_id": field_definition_id, "value": [option_id]}],
        }
    }

    response = requests.patch(url, json=payload, headers=headers, timeout=15)
    response.raise_for_status()
    log(f"Set file {file_id} status to '{status}'")

# ---------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------

def seconds_to_tc(seconds, fps=24):
    """Convert seconds to timecode string (HH:MM:SS:FF)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    frames = int(round((seconds % 1) * fps))
    return f"{hours:02}:{minutes:02}:{secs:02}:{frames:02}"

def timecode_to_frames(tc, fps):
    """Convert HH:MM:SS:FF to frame number."""
    try:
        h, m, s, f = [int(x) for x in tc.split(":")]
        return int(round(((h * 3600) + (m * 60) + s) * fps + f))
    except Exception:
        return 0

def extract_fps_from_rate(rate):
    """Sanitize frame rate string like '23.98 fps' -> 23.98 (float)."""
    import re
    if isinstance(rate, (float, int)):
        return float(rate)
    regex = r'\s[a-zA-Z]*'
    test_str = str(rate)
    subst = ""
    fixed_framerate = float(re.sub(regex, subst, test_str, 0))
    return round(fixed_framerate, 3)
