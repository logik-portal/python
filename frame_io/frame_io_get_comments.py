# FrameIO Get Comments v2.0 — Uppercut VFX Pipeline
# Fully API-driven version (no XML)
# Author: John Geehreng
# Updated: 2025-11-25

import flame
import math
import requests
# import re
# import os
from lib.frame_io_api import (
    validate_config,
    get_fio_projects,
    find_fio_asset,
    get_asset_comments,
    get_comment_owner,
)

SCRIPT_NAME = 'FrameIO Get Comments'
VERSION = 'v2.0.2'

DEBUG = False

def log(msg):
    print(f"[{SCRIPT_NAME}] {msg}")

def debug(msg):
    if DEBUG:
        print(f"[{SCRIPT_NAME} DEBUG] {msg}")

def safe_colour_label(obj):
    try:
        obj.colour_label = "Address Comments"
    except Exception:
        obj.colour = (0.1137, 0.2627, 0.1764)


# --- Main Class ---
class frame_io_get_comments(object):

    def __init__(self, selection):
        # Load system-wide config
        self.cfg = validate_config()

        # Determine frame rate from first relevant item
        self.frame_rate = self.get_frame_rate(selection)

        # Get current Flame project name (exact match mode)
        self.project_name = flame.projects.current_project.nickname
        log(f"Starting FrameIO Comment Sync for project '{self.project_name}'")

        # Resolve FrameIO project
        self.root_asset_id, self.project_id = get_fio_projects(self.cfg, self.project_name)

        # Process comments
        self.get_comments(selection)

    def get_frame_rate(self, selection):
        for item in selection:
            fr = None
            if isinstance(item, flame.PySegment):
                fr = item.parent.parent.parent.frame_rate
            elif isinstance(item, flame.PyClip):
                fr = item.frame_rate
            if fr:
                try:
                    return math.ceil(float(str(fr).split(" ")[0]))
                except:
                    return 24
        return 24

    # ----------------------
    # Config helper — works for dict OR object, nested or flat
    # ----------------------

    def _cfg_val(self, *keys, default=None):
        """
        Safely pull a value from self.cfg, whether it's:
          - an object with attributes (cfg.account_id), or
          - a dict, possibly nested (cfg["frame_io"]["account_id"])
        """
        cfg = self.cfg

        # Object-style attributes
        if not isinstance(cfg, dict):
            for k in keys:
                if hasattr(cfg, k):
                    return getattr(cfg, k)
            return default

        # Top-level dict keys
        for k in keys:
            if k in cfg:
                return cfg[k]

        # Common nested keys
        for container_key in ("frame_io", "frameio", "frame_io_settings", "frameio_config"):
            sub = cfg.get(container_key)
            if isinstance(sub, dict):
                for k in keys:
                    if k in sub:
                        return sub[k]

        return default

    # ----------------------
    # Author Resolution Logic
    # ----------------------

    def resolve_author(self, info, author_cache):

        # 1) Direct anonymous_user payload
        anon = info.get("anonymous_user")
        if anon:
            name = anon.get("name") or anon.get("email")
            if name:
                return name

        anon_id = info.get("anonymous_user_id")
        rl_id = info.get("review_link_id")

        # 2) Review-link guest users (only if we can safely read cfg)
        if anon_id and rl_id:
            cache_key = f"{rl_id}:{anon_id}"
            if cache_key in author_cache:
                return author_cache[cache_key]

            account_id = self._cfg_val("account_id")
            headers = self._cfg_val("headers")
            session = self._cfg_val("session")

            # If any critical piece is missing, skip this lookup gracefully
            if account_id and headers and session:
                url = (
                    f"https://api.frame.io/v2/accounts/"
                    f"{account_id}/review-links/{rl_id}/guest-users"
                )

                try:
                    resp = session.get(url, headers=headers)
                    if resp.status_code == 200:
                        for u in resp.json():
                            if u.get("id") == anon_id:
                                name = u.get("name") or u.get("email") or "Unknown"
                                author_cache[cache_key] = name
                                return name
                    else:
                        if DEBUG:
                            print(f"[{SCRIPT_NAME} DEBUG] Guest lookup {rl_id}/{anon_id} returned {resp.status_code}")
                except Exception as e:
                    if DEBUG:
                        print(f"[{SCRIPT_NAME} DEBUG] Guest lookup failed: {e}")

        # 3) Standard fields
        user = info.get("user") or {}
        creator = info.get("creator") or {}
        owner = info.get("owner") or {}

        name = (
            user.get("full_name")
            or user.get("email")
            or creator.get("full_name")
            or creator.get("email")
            or owner.get("name")
            or owner.get("email")
        )
        if name:
            return name

        # 4) V4 quirk: nested `replies` come back with no owner/user/creator
        # field at all (Frame.io's schema only embeds `owner` on the
        # top-level comment, not on replies). Fall back to a per-reply
        # lookup via the single "show comment" endpoint, which does return
        # an owner. Cache by comment id to avoid repeat lookups.
        comment_id = info.get("id")
        if comment_id:
            cache_key = f"comment:{comment_id}"
            if cache_key in author_cache:
                return author_cache[cache_key]

            fetched_owner = get_comment_owner(self.cfg, comment_id) or {}
            name = fetched_owner.get("name") or fetched_owner.get("email")
            if name:
                author_cache[cache_key] = name
                return name

        return "Unknown"


    # ----------------------
    # Main Comment Logic
    # ----------------------

    def get_comments(self, selection):

        fps = float(self.frame_rate)
        total_markers = 0
        comment_cache = {}
        total_items = 0

        for item in selection:

            # Identify whether clip or segment
            if isinstance(item, flame.PySegment):
                sequence_obj = item.parent.parent.parent
                is_segment = True
                base_name = str(sequence_obj.name)[1:-1]
            elif isinstance(item, flame.PyClip):
                sequence_obj = item
                is_segment = False
                base_name = str(item.name)[1:-1]
            else:
                continue

            # Fetch FrameIO asset comments
            if base_name in comment_cache:
                comments = comment_cache[base_name]
            else:
                _, _, _, file_id = find_fio_asset(self.cfg, self.project_id, base_name)
                comments = get_asset_comments(self.cfg, file_id) if file_id else []
                comment_cache[base_name] = comments

            if not comments:
                log(f"No comments found for '{base_name}'")
                continue

            total_items += 1
            markers_for_item = 0
            combined_texts = []
            author_cache = {}

            for info in comments:
                # V4's list endpoint only returns top-level comments; replies
                # are nested under each comment's "replies" array (fetched via
                # include=replies), so there's no parent_id to filter on here.
                base_text = (info.get('text') or '').strip()
                if not base_text:
                    continue

                # Author for top-level comment
                author = self.resolve_author(info, author_cache)
                if author == "Unknown":
                    log(
                        f"NOTE: Could not resolve author for a comment on '{base_name}' — "
                        "likely a public-share/anonymous commenter, which Frame.io V4 "
                        "does not expose via the API (not a bug)."
                    )

                # FrameIO base frame (V4 "timestamp" is already an integer framestamp)
                raw_frame = info.get('timestamp', 0)
                try:
                    base_frame = int(raw_frame) if raw_frame else 0
                except Exception:
                    base_frame = 0

                # Replies
                replies = info.get('replies') or []
                reply_pairs = []
                for r in replies:
                    # print("\n=== RAW REPLY JSON ===")
                    # print(r)
                    # print("=== END RAW REPLY ===\n")

                    r_text = (r.get("text") or "").strip()
                    if not r_text:
                        continue

                    r_author = self.resolve_author(r, author_cache)
                    if r_author == "Unknown":
                        log(
                            f"NOTE: Could not resolve reply author for a reply on '{base_name}' — "
                            "likely a public-share/anonymous commenter, which Frame.io V4 "
                            "does not expose via the API (not a bug)."
                        )

                    reply_pairs.append((r_author, r_text))

                # --- Marker comment (compact) ---
                marker_comment = base_text
                if reply_pairs:
                    marker_comment += "  " + "  ".join(
                        f" **Reply by {ra}: {rt}" for ra, rt in reply_pairs
                    )

                # --- Pretty text for PySegment.comment ---
                pretty_text = f"{author}: {base_text}"
                for ra, rt in reply_pairs:
                    pretty_text += f" **Reply by {ra}: {rt}**"

                # Marker creation
                target = item if is_segment else sequence_obj

                # Avoid duplicate markers at the same frame on repeated runs
                if any(getattr(m, "frame", None) == base_frame for m in getattr(target, "markers", [])):
                    continue

                try:
                    marker = target.create_marker(int(base_frame))
                except Exception:
                    continue

                marker.name = author
                marker.comment = marker_comment
                safe_colour_label(marker)

                markers_for_item += 1
                combined_texts.append(pretty_text)

            # Apply color and summary comments
            if markers_for_item > 0:
                safe_colour_label(item)
                if isinstance(item, flame.PySegment):
                    try:
                        # Join all pretty comment strings for the segment
                        item.comment = "  ".join(combined_texts)
                    except Exception:
                        print(f"[{SCRIPT_NAME}] Could not set segment comment for '{base_name}'")

            total_markers += markers_for_item
            log(f"{markers_for_item} markers added for '{base_name}'")

        log(f"Done. Total markers added: {total_markers}.")

        flame.messages.show_in_dialog(
            title=f"{SCRIPT_NAME}: Done",
            message=f"Added {total_markers} marker(s) across {total_items} item(s).",
            type="info",
            buttons=["Ok"]
        )


# ---------------
# Flame Menus
# ---------------

def scope_clip(selection):
    return any(isinstance(i, flame.PyClip) for i in selection)

def scope_segment(selection):
    return any(isinstance(i, flame.PySegment) for i in selection)

def get_timeline_custom_ui_actions():
    return [{
        'name': 'UC FrameIO',
        'actions': [{
            'name': 'Get Comments',
            'order': 0,
            'isVisible': scope_segment,
            'separator': 'below',
            'execute': frame_io_get_comments,
            'minimumVersion': '2023.2'
        }]
    }]

def get_media_panel_custom_ui_actions():
    return [{
        'name': 'UC FrameIO',
        'actions': [{
            'name': 'Get Comments',
            'order': 2,
            'isVisible': scope_clip,
            'separator': 'above',
            'execute': frame_io_get_comments,
            'minimumVersion': '2023.2'
        }]
    }]
