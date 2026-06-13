#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MASV API helpers for Flame MASV Uploader.

Covers config, package creation, chunked upload, finalization, and link creation.

MASV API: https://api.massive.app/v1
Developer docs: https://developer.massive.io/masv-api/
"""

import json
import math
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Optional

import requests

MASV_API_BASE = "https://api.massive.app/v1"
MASV_DOWNLOAD_BASE = "https://get.massive.io"
DEFAULT_CHUNK_SIZE = 104_857_600

SCRIPT_DIR = Path(__file__).resolve().parent.parent
GLOBAL_CONFIG_PATH = str(SCRIPT_DIR / "config" / "shared_config.json")
PRESETS_DIR = str(SCRIPT_DIR / "presets")

DEFAULT_CONFIG = {
    "masv_api_key": "",
    "masv_team_id": "",
    "jobs_folder": "",
    "default_recipients": "",
    "last_preset": "",
    "debug": False,
}

MENU_NAME = "MASV Uploader"


def log(msg: str, cfg: Optional[dict] = None) -> None:
    print(f"[masv_uploader] {msg}")


def log_debug(msg: str, cfg: Optional[dict] = None) -> None:
    if cfg and cfg.get("debug"):
        print(f"[masv_uploader DEBUG] {msg}")


def load_config() -> dict:
    cfg = dict(DEFAULT_CONFIG)
    try:
        if os.path.exists(GLOBAL_CONFIG_PATH):
            with open(GLOBAL_CONFIG_PATH) as f:
                cfg.update(json.load(f))
    except Exception as e:
        log(f"WARNING: Could not load config from {GLOBAL_CONFIG_PATH}: {e}")
    return cfg


def validate_config(cfg: Optional[dict] = None) -> dict:
    if cfg is None:
        cfg = load_config()

    if not cfg.get("masv_api_key", "").strip():
        raise RuntimeError(
            f"MASV API key is not configured. "
            f"Open {MENU_NAME} → Edit Config and enter your API key."
        )
    if not cfg.get("masv_team_id", "").strip():
        raise RuntimeError(
            f"MASV team ID is not configured. "
            f"Open {MENU_NAME} → Edit Config and enter your team ID."
        )
    if not cfg.get("jobs_folder", "").strip():
        raise RuntimeError(
            f"Jobs folder is not configured. "
            f"Open {MENU_NAME} → Edit Config and set an export staging folder."
        )

    return cfg


def get_credentials(cfg: dict) -> tuple[str, str]:
    """Return (team_id, api_key) from config."""
    team_id = cfg.get("masv_team_id", "").strip()
    api_key = cfg.get("masv_api_key", "").strip()
    if not team_id or not api_key:
        raise RuntimeError(
            f"MASV credentials are incomplete. "
            f"Open {MENU_NAME} → Edit Config."
        )
    return team_id, api_key


def parse_recipients(value) -> list:
    """Parse comma-separated string or JSON array into a list of email addresses."""
    if isinstance(value, list):
        return [str(r).strip() for r in value if str(r).strip()]
    if not value:
        return []
    return [r.strip() for r in str(value).split(",") if r.strip()]


def format_recipients_for_edit(value) -> str:
    """Format stored recipients for display in a text field."""
    if isinstance(value, list):
        return ", ".join(str(r).strip() for r in value if str(r).strip())
    return str(value or "").strip()


def get_default_recipients(cfg: dict) -> list:
    return parse_recipients(cfg.get("default_recipients", ""))


def list_presets() -> list:
    extensions = {".xml", ".cdxprof"}
    try:
        return sorted(
            f for f in os.listdir(PRESETS_DIR)
            if os.path.isfile(os.path.join(PRESETS_DIR, f))
            and os.path.splitext(f)[1].lower() in extensions
        )
    except Exception as e:
        log(f"WARNING: Could not scan presets directory '{PRESETS_DIR}': {e}")
        return []


def get_preset_path(filename: str) -> str:
    return os.path.join(PRESETS_DIR, filename)


def save_last_preset(filename: str) -> None:
    try:
        cfg = load_config()
        cfg["last_preset"] = filename
        p = Path(GLOBAL_CONFIG_PATH)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        log(f"WARNING: Could not save last preset: {e}")


def _api_headers(api_key: str) -> dict:
    return {"X-API-KEY": api_key, "Content-Type": "application/json"}


def _pkg_headers(token: str) -> dict:
    return {"X-Package-Token": token, "Content-Type": "application/json"}


def _check(resp: requests.Response, context: str = "") -> dict:
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        body = ""
        try:
            body = resp.text
        except Exception:
            pass
        raise RuntimeError(
            f"MASV API error{f' ({context})' if context else ''}: {e} — {body}"
        )
    if resp.status_code == 204 or not resp.content:
        return {}
    return resp.json()


def create_package(
    cfg: dict,
    name: str,
    description: str = "",
    password: Optional[str] = None,
    recipients: Optional[list] = None,
    access_limit: Optional[int] = None,
) -> tuple[str, str]:
    """Create a MASV package. Returns (package_id, access_token)."""
    team_id, api_key = get_credentials(cfg)
    log(f"Creating package '{name}' on team {team_id}")

    body: dict = {
        "name": name,
        "description": description or name,
        "recipients": recipients or [],
    }
    if password:
        body["password"] = password
    if access_limit is not None:
        body["access_limit"] = access_limit

    resp = requests.post(
        f"{MASV_API_BASE}/teams/{team_id}/packages",
        headers=_api_headers(api_key),
        json=body,
        timeout=30,
    )
    data = _check(resp, "create_package")
    log_debug(f"create_package response: {data}", cfg)

    package_id = data["id"]
    access_token = data["access_token"]
    log(f"Package created: {package_id}")
    return package_id, access_token


def finalize_package(package_id: str, token: str) -> None:
    resp = requests.post(
        f"{MASV_API_BASE}/packages/{package_id}/finalize",
        headers=_pkg_headers(token),
        timeout=30,
    )
    _check(resp, "finalize_package")
    log(f"Package {package_id} finalized.")


def _init_multipart(create_blueprint: dict) -> str:
    method = create_blueprint["method"].upper()
    url = create_blueprint["url"]
    headers = create_blueprint.get("headers", {})

    resp = requests.request(method, url, headers=headers, timeout=60)
    resp.raise_for_status()

    root = ET.fromstring(resp.text)
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}
    upload_id_el = root.find("s3:UploadId", ns) or root.find("UploadId")
    if upload_id_el is None or not upload_id_el.text:
        raise RuntimeError(f"Could not parse S3 UploadId from: {resp.text[:500]}")
    return upload_id_el.text


def _add_file_to_package(
    package_id: str,
    token: str,
    file_path: str,
    chunk_size: int,
) -> tuple[str, str]:
    stat = os.stat(file_path)
    mtime_iso = (
        __import__("datetime")
        .datetime.utcfromtimestamp(stat.st_mtime)
        .strftime("%Y-%m-%dT%H:%M:%S.000Z")
    )

    body = {
        "kind": "file",
        "name": os.path.basename(file_path),
        "path": "",
        "last_modified": mtime_iso,
        "size": stat.st_size,
        "chunk_size": chunk_size,
    }

    resp = requests.post(
        f"{MASV_API_BASE}/packages/{package_id}/files",
        headers=_pkg_headers(token),
        json=body,
        timeout=30,
    )
    data = _check(resp, "add_file")

    file_id = data["file"]["id"]
    upload_id = _init_multipart(data["create_blueprint"])
    log(f"  File registered: {os.path.basename(file_path)} → file_id={file_id}")
    return file_id, upload_id


def _get_chunk_urls(
    package_id: str,
    token: str,
    file_id: str,
    upload_id: str,
    chunk_count: int,
) -> list:
    resp = requests.post(
        f"{MASV_API_BASE}/packages/{package_id}/files/{file_id}",
        headers=_pkg_headers(token),
        json={"upload_id": upload_id},
        params={"start": 0, "count": chunk_count},
        timeout=30,
    )
    blueprints = _check(resp, "get_chunk_urls")
    if not isinstance(blueprints, list):
        raise RuntimeError(f"Expected list of chunk blueprints, got: {type(blueprints)}")
    return blueprints


def _upload_chunks(
    file_path: str,
    blueprints: list,
    chunk_size: int,
    progress_cb: Optional[Callable[[float], None]] = None,
) -> list:
    chunk_extras = []
    total = len(blueprints)
    file_size = os.path.getsize(file_path)

    with open(file_path, "rb") as fh:
        for idx, blueprint in enumerate(blueprints):
            offset = idx * chunk_size
            length = min(chunk_size, file_size - offset)
            fh.seek(offset)
            chunk_data = fh.read(length)

            method = blueprint["method"].upper()
            url = blueprint["url"]
            headers = blueprint.get("headers", {})

            resp = requests.request(
                method, url, headers=headers, data=chunk_data, timeout=300
            )
            resp.raise_for_status()

            etag = resp.headers.get("ETag", "").strip('"')
            chunk_extras.append({
                "part_number": str(idx + 1),
                "etag": f'"{etag}"',
            })

            if progress_cb:
                progress_cb((idx + 1) / total * 100)

    return chunk_extras


def _finalize_file(
    package_id: str,
    token: str,
    file_id: str,
    upload_id: str,
    chunk_extras: list,
    file_size: int,
    chunk_size: int,
) -> None:
    body = {
        "size": file_size,
        "chunk_size": chunk_size,
        "file_extras": {"upload_id": upload_id},
        "chunk_extras": chunk_extras,
    }
    resp = requests.post(
        f"{MASV_API_BASE}/packages/{package_id}/files/{file_id}/finalize",
        headers=_pkg_headers(token),
        json=body,
        timeout=60,
    )
    _check(resp, "finalize_file")
    log(f"  File finalized: file_id={file_id}")


def upload_file(
    package_id: str,
    token: str,
    file_path: str,
    progress_cb: Optional[Callable[[float], None]] = None,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
) -> None:
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        raise RuntimeError(f"File is empty: {file_path}")

    chunk_count = max(1, math.ceil(file_size / chunk_size))
    log(f"  Uploading '{os.path.basename(file_path)}' — {file_size:,} bytes, {chunk_count} chunk(s)")

    if progress_cb:
        progress_cb(5)

    file_id, upload_id = _add_file_to_package(package_id, token, file_path, chunk_size)

    if progress_cb:
        progress_cb(10)

    blueprints = _get_chunk_urls(package_id, token, file_id, upload_id, chunk_count)

    def chunk_progress(pct: float) -> None:
        if progress_cb:
            progress_cb(10 + pct * 0.80)

    chunk_extras = _upload_chunks(file_path, blueprints, chunk_size, chunk_progress)

    if progress_cb:
        progress_cb(92)

    _finalize_file(package_id, token, file_id, upload_id, chunk_extras, file_size, chunk_size)

    if progress_cb:
        progress_cb(100)


def create_link(
    package_id: str,
    token: str,
    password: Optional[str] = None,
) -> tuple[str, str]:
    body: dict = {}
    if password:
        body["password"] = password

    resp = requests.post(
        f"{MASV_API_BASE}/packages/{package_id}/links",
        headers=_pkg_headers(token),
        json=body,
        timeout=30,
    )
    data = _check(resp, "create_link")

    link_id = data["id"]
    download_secret = data.get("download_secret", "")
    if not download_secret:
        raise RuntimeError(
            "MASV did not return a download_secret. "
            "Ensure the link was created without an email address (direct download)."
        )

    log(f"Download link created: {link_id}")
    return link_id, download_secret


def build_download_url(link_id: str, download_secret: str) -> str:
    return f"{MASV_DOWNLOAD_BASE}/{link_id}?secret={download_secret}"
