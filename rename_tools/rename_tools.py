# -*- coding: utf-8 -*-
"""
Script Name: Rename Tools
Script Version: 1.0.0
Flame Version: 2025.2
Written by: Koumei Muraki
Creation Date: 07.02.26

Description:
Rename clips by adding a prefix, suffix, or performing find and replace.
Includes a preview panel and one-level undo.

Menus:
Media Panel -> Right-click -> Rename Tools
Timeline -> Right-click -> Rename Tools
"""

# ----------------------------------------------------------------------
# Internal Notes
#
# - Cross-platform UI
#   - Qt (PySide6 / PySide2) when QApplication is available
#   - Linux fallback: zenity
#   - macOS fallback: AppleScript (osascript)
#
# - Features
#   - Unified Rename Panel
#   - Prefix / Suffix / Find & Replace
#   - Live preview
#   - One-level Undo
#   - Remembers previous settings
#
# - No blocking input() is used.
# ----------------------------------------------------------------------

print("[Rename Tools] module loaded")
print("[Rename Tools] path:", __file__)

import sys, os, json, subprocess, shutil, datetime, traceback, weakref

# ----------------- Qt detection (PySide6 -> PySide2) -----------------
QtWidgets = None
QtCore = None
_QT_BINDING = None
try:
    from PySide6 import QtWidgets as _QtWidgets6, QtCore as _QtCore6
    QtWidgets, QtCore = _QtWidgets6, _QtCore6
    _QT_BINDING = "PySide6"
except Exception:
    try:
        from PySide2 import QtWidgets as _QtWidgets2, QtCore as _QtCore2
        QtWidgets, QtCore = _QtWidgets2, _QtCore2
        _QT_BINDING = "PySide2"
    except Exception:
        QtWidgets = None
        QtCore = None
        _QT_BINDING = None


# Also try to import QtGui for screenAt/cursor access
QtGui = None
if _QT_BINDING == "PySide6":
    try:
        from PySide6 import QtGui as _QtGui6
        QtGui = _QtGui6
    except Exception:
        QtGui = None
elif _QT_BINDING == "PySide2":
    try:
        from PySide2 import QtGui as _QtGui2
        QtGui = _QtGui2
    except Exception:
        QtGui = None

# ----------------- Flat UI styling -----------------
_FLAT_QSS = """
QDialog { background: #2C3644; }                 /* base blue */
QLabel  { color: #e6e6e6; font-size: 16px; }

QLineEdit {
    background: #344356;                        /* slightly lighter for contrast */
    color: #f0f0f0;
    font-size: 16px;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 6px 8px;
}
QLineEdit:focus { border: 1px solid #5a7bd8; background: #3A4A60; }

QPlainTextEdit, QTextEdit {
    background: #2C3644;                        /* match dialog */
    color: #f0f0f0;
    font-size: 16px;
    border: 1px solid #3a3a3a;
    border-radius: 6px;
    padding: 6px 8px;
}

QCheckBox { color: #d8d8d8; font-size: 15px; }

QPushButton {
    background: #344356;                        /* button blue */
    color: #efefef;
    font-size: 16px;
    border: 1px solid #4a4a4a;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: 500;
}
QPushButton:hover  { background: #3A4A60; }     /* hover = a bit brighter */
QPushButton:pressed{ background: #2C3644; }     /* pressed = base blue */
QPushButton:disabled {
    color: #9aa3ad;
    border-color: #3a3a3a;
    background: #253041;                        /* darker disabled */
}

QDialogButtonBox QPushButton { min-width: 88px; }

QGroupBox {
    border: 1px solid #3b3b3b;
    border-radius: 8px;
    margin-top: 12px;
    padding: 10px;
    color: #e0e0e0;
    font-size: 16px;
    font-weight: 500;
}
"""

def _apply_flat_style(widget):
    try:
        if widget is not None and hasattr(widget, "setStyleSheet"):
            widget.setStyleSheet(_FLAT_QSS)
    except Exception:
        pass


def _exec_dialog(dlg):
    """Execute a dialog across PySide6/2 and return True if accepted."""
    try:
        if hasattr(dlg, "exec"):
            rc = dlg.exec()
        else:
            rc = dlg.exec_()
    except Exception:
        # Fallback if something odd happens
        return False
    try:
        # QDialog.Accepted == 1 in both bindings
        return rc == QtWidgets.QDialog.Accepted
    except Exception:
        return bool(rc)


def _center_on_screen(widget):
    """Move a QWidget to the center of the current screen (or primary screen)."""
    try:
        screen = None
        # Prefer the screen where the cursor is located, if QtGui is available
        if QtGui is not None and hasattr(QtWidgets.QApplication, "screenAt"):
            try:
                pos = QtGui.QCursor.pos()
                screen = QtWidgets.QApplication.screenAt(pos)
            except Exception:
                screen = None
        # Fallback to the widget's window screen
        if screen is None and hasattr(widget, "windowHandle") and widget.windowHandle():
            try:
                screen = widget.windowHandle().screen()
            except Exception:
                screen = None
        # Final fallback: primary screen
        if screen is None:
            try:
                screen = QtWidgets.QApplication.primaryScreen()
            except Exception:
                screen = None
        if screen is not None:
            geo = widget.frameGeometry()
            center = screen.availableGeometry().center()
            geo.moveCenter(center)
            widget.move(geo.topLeft())
    except Exception:
        # As a last resort, do nothing if centering fails silently
        pass

# diag
try:
    with open("/tmp/flame_ui_diag.txt", "a") as f:
        f.write(f"Qt binding: {_QT_BINDING}\n")
except Exception:
    pass


def _has_qt():
    try:
        inst = None
        if QtWidgets is not None:
            try:
                inst = QtWidgets.QApplication.instance()
            except Exception:
                inst = None
        ok = (QtWidgets is not None) and (inst is not None)
        with open("/tmp/flame_ui_diag.txt", "a") as f:
            f.write(f"qt_ok={ok} binding={_QT_BINDING} inst={type(inst).__name__ if inst else None}\n")
        return ok
    except Exception:
        try:
            with open("/tmp/flame_ui_diag.txt", "a") as f:
                f.write("_has_qt exception\n")
        except Exception:
            pass
        return False


# ----------------- config (last-used prefix) -----------------
CFG_DIR = os.path.join(os.path.expanduser("~"), ".config", "flame_rename")
CFG_PATH = os.path.join(CFG_DIR, "config.json")
CFG_FALLBACK_PATH = "/tmp/flame_rename_config.json"
DEFAULT_PREFIX = "PRE_"
DEFAULT_SUFFIX = "_SUF"


def _ensure_cfg_dir():
    try:
        os.makedirs(CFG_DIR, exist_ok=True)
        try:
            with open("/tmp/flame_ui_diag.txt", "a") as d:
                d.write(f"ensure_cfg_dir: {CFG_DIR}\n")
        except Exception:
            pass
    except Exception:
        pass


def _load_cfg():
    # Try primary path, then fallback in /tmp
    for pth in (CFG_PATH, CFG_FALLBACK_PATH):
        try:
            with open(pth, "r", encoding="utf-8") as f:
                data = json.load(f)
            try:
                with open("/tmp/flame_ui_diag.txt", "a") as d:
                    d.write(f"load_cfg ok: {pth}\n")
            except Exception:
                pass
            return data if isinstance(data, dict) else {}
        except Exception:
            continue
    try:
        with open("/tmp/flame_ui_diag.txt", "a") as d:
            d.write("load_cfg: no config found\n")
    except Exception:
        pass
    return {}


def _save_cfg(data):
    _ensure_cfg_dir()
    # Try primary location first
    try:
        with open(CFG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        try:
            with open("/tmp/flame_ui_diag.txt", "a") as d:
                d.write(f"save_cfg ok: {CFG_PATH}\n")
        except Exception:
            pass
        return
    except Exception as e:
        # Fallback to /tmp when HOME or permissions are problematic
        try:
            with open(CFG_FALLBACK_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            try:
                with open("/tmp/flame_ui_diag.txt", "a") as d:
                    d.write(f"save_cfg fallback ok: {CFG_FALLBACK_PATH}\n")
            except Exception:
                pass
            return
        except Exception:
            try:
                with open("/tmp/flame_ui_diag.txt", "a") as d:
                    d.write("save_cfg failed: both primary and fallback\n")
            except Exception:
                pass
            return


def _load_last_prefix():
    data = _load_cfg()
    return data.get("last_prefix") or DEFAULT_PREFIX


def _save_last_prefix(p):
    data = _load_cfg()
    data["last_prefix"] = p
    _save_cfg(data)


def _load_last_suffix():
    data = _load_cfg()
    return data.get("last_suffix") or DEFAULT_SUFFIX


def _save_last_suffix(s):
    data = _load_cfg()
    data["last_suffix"] = s
    _save_cfg(data)


def _load_last_find():
    data = _load_cfg()
    return data.get("last_find") or ""


def _save_last_find(s):
    data = _load_cfg()
    data["last_find"] = s or ""
    _save_cfg(data)


def _load_last_repl():
    data = _load_cfg()
    return data.get("last_repl") or ""



def _save_last_repl(s):
    data = _load_cfg()
    data["last_repl"] = s or ""
    _save_cfg(data)


# ----------------- idempotent (duplicate-prevent) flags in config -----------------

def _load_last_idem(kind):
    """Load last idempotent flag for a kind ("prefix" or "suffix"). Defaults True."""
    data = _load_cfg()
    return bool(data.get(f"idem_{kind}", True))


def _save_last_idem(kind, val):
    data = _load_cfg()
    data[f"idem_{kind}"] = bool(val)
    _save_cfg(data)


# ----------------- platform helpers -----------------

def _which(cmd):
    return shutil.which(cmd) is not None


# ------------- macOS AppleScript Yes/No dialog helper -------------

def _macos_yes_no(title, question, default_yes=True):
    """Return True for Yes, False for No on macOS using AppleScript. Falls back to default_yes."""
    try:
        if not (sys.platform == "darwin" and _which("osascript")):
            return default_yes
        default_btn = "Yes" if default_yes else "No"
        # Show a simple Yes/No dialog; returns True if Yes clicked.
        script = f'display dialog {question!r} with title {title!r} buttons {{"No","Yes"}} default button {default_btn!r}'
        p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        return ("button returned:Yes" in (p.stdout or ""))
    except Exception:
        return default_yes


# --- Helper to robustly extract AppleScript text returned value ---
def _extract_osascript_text(out):
    """Extract the value after 'text returned:' up to ', button returned:' safely."""
    try:
        if not out:
            return ""
        marker = "text returned:"
        i = out.find(marker)
        if i == -1:
            return ""
        i += len(marker)
        end_token = ", button returned:"
        j = out.find(end_token, i)
        if j == -1:
            j = len(out)
        return out[i:j].strip()
    except Exception:
        return ""



def _parent_widget():
    if not _has_qt():
        return None
    w = QtWidgets.QApplication.activeWindow()
    if w is None:
        tops = [tw for tw in QtWidgets.QApplication.topLevelWidgets() if getattr(tw, 'isVisible', lambda: False)()]
        return tops[0] if tops else None
    return w


# ----------------- prompt with checkbox (Qt) -----------------

def _prompt_text_with_idem(kind, title, label, default_text, checkbox_label="Prevent duplicate addition (idempotent)"):
    """Return (text, idempotent_bool) or (None, None) on cancel.
    If Qt is available, use a custom QDialog.
    Otherwise, on Linux use zenity and on macOS use AppleScript to obtain BOTH text and idempotent flag.
    Falls back to the stored default if no UI mechanism is available.
    """
    # ---- 1) Qt path (styled dialog) ----
    if _has_qt():
        try:
            parent = _parent_widget()
            dlg = QtWidgets.QDialog(parent)
            dlg.setWindowTitle(title)
            layout = QtWidgets.QVBoxLayout(dlg)
            lbl = QtWidgets.QLabel(label, dlg)
            edit = QtWidgets.QLineEdit(dlg)
            edit.setText(str(default_text or ""))
            chk = QtWidgets.QCheckBox(checkbox_label, dlg)
            chk.setChecked(_load_last_idem(kind))
            btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel, parent=dlg)
            layout.addWidget(lbl)
            layout.addWidget(edit)
            layout.addWidget(chk)
            layout.addWidget(btns)
            btns.accepted.connect(dlg.accept)
            btns.rejected.connect(dlg.reject)
            _apply_flat_style(dlg)
            dlg.show()
            if QtWidgets is not None:
                QtWidgets.QApplication.processEvents()
            _center_on_screen(dlg)
            if _exec_dialog(dlg):
                return edit.text(), bool(chk.isChecked())
            return None, None
        except Exception:
            pass

    # ---- 2) Linux: zenity (two-step: entry then Yes/No) ----
    if sys.platform.startswith("linux") and _which("zenity"):
        try:
            # Step 1: text input
            p1 = subprocess.run([
                "zenity", "--entry", "--title", title, "--text", label,
                "--entry-text", str(default_text or "")
            ], capture_output=True, text=True)
            if p1.returncode != 0:
                return None, None
            text_val = (p1.stdout or "").strip()

            # Step 2: idempotent flag via question dialog
            # Note: zenity doesn't support default selection for --question;
            # if the dialog fails, fall back to the stored default.
            idem_default = _load_last_idem(kind)
            p2 = subprocess.run([
                "zenity", "--question", "--title", title,
                "--text", checkbox_label
            ], capture_output=True, text=True)
            if p2.returncode == 0:
                idem_val = True
            elif p2.returncode == 1:
                idem_val = False
            else:
                idem_val = bool(idem_default)
            return text_val, bool(idem_val)
        except Exception:
            pass

    # ---- 3) macOS: AppleScript (two-step: text then Yes/No) ----
    if sys.platform == "darwin" and _which("osascript"):
        try:
            # Step 1: text input
            script = f'display dialog {label!r} default answer {str(default_text or "")!r} with title {title!r} buttons {"OK"!r} default button 1'
            p1 = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if p1.returncode != 0:
                return None, None
            out1 = p1.stdout or ""
            text_val = _extract_osascript_text(out1)

            # Step 2: idempotent Yes/No
            idem_default = _load_last_idem(kind)
            idem_val = _macos_yes_no(title, checkbox_label, default_yes=idem_default)
            return text_val, bool(idem_val)
        except Exception:
            pass

    # ---- 4) Fallback: return last stored values (no new input possible) ----
    return default_text, _load_last_idem(kind)


# ----------------- prompt (prefix input) -----------------

#
# Wrappers that also persist the idempotent choice

def _prompt_prefix_opts():
    s, idem = _prompt_text_with_idem("prefix", "Add Prefix", "Prefix:", _load_last_prefix())
    if s is None:
        return None, None
    _save_last_prefix(s)
    _save_last_idem("prefix", idem)
    return s, idem


def _prompt_suffix_opts():
    s, idem = _prompt_text_with_idem("suffix", "Add Suffix", "Suffix:", _load_last_suffix())
    if s is None:
        return None, None
    _save_last_suffix(s)
    _save_last_idem("suffix", idem)
    return s, idem


def _prompt_prefix(title="Add Prefix", label="Prefix:"):
    """Return a prefix string or None. Tries Qt, then zenity (Linux), then AppleScript (macOS)."""
    # 1) Qt
    if _has_qt():
        try:
            parent = _parent_widget()
            dlg = QtWidgets.QInputDialog(parent)
            _apply_flat_style(dlg)
            dlg.setWindowTitle(title)
            dlg.setLabelText(label)
            dlg.setTextValue(_load_last_prefix())
            dlg.show()
            if QtWidgets is not None:
                QtWidgets.QApplication.processEvents()
            _center_on_screen(dlg)
            try:
                dlg.raise_()
                dlg.activateWindow()
            except Exception:
                pass
            if _exec_dialog(dlg):
                return str(dlg.textValue())
        except Exception:
            pass
    # 2) Linux: zenity
    if sys.platform.startswith("linux") and _which("zenity"):
        try:
            p = subprocess.run([
                "zenity", "--entry", "--title", title, "--text", label,
                "--entry-text", _load_last_prefix()
            ], capture_output=True, text=True)
            if p.returncode == 0:
                return (p.stdout or "").strip()
        except Exception:
            pass
    # 3) macOS: AppleScript
    if sys.platform == "darwin" and _which("osascript"):
        try:
            script = f'display dialog {label!r} default answer {_load_last_prefix()!r} with title {title!r} buttons {"OK"!r} default button 1'
            p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if p.returncode == 0:
                out = p.stdout or ""
                val = _extract_osascript_text(out)
                if val != "":
                    return val
        except Exception:
            pass
    # 4) Fallback: use last or default silently
    return _load_last_prefix()


# Suffix prompt (same fallbacks as prefix)

def _prompt_suffix(title="Add Suffix", label="Suffix:"):
    if _has_qt():
        try:
            parent = _parent_widget()
            dlg = QtWidgets.QInputDialog(parent)
            _apply_flat_style(dlg)
            dlg.setWindowTitle(title)
            dlg.setLabelText(label)
            dlg.setTextValue(_load_last_suffix())
            dlg.show()
            if QtWidgets is not None:
                QtWidgets.QApplication.processEvents()
            _center_on_screen(dlg)
            try:
                dlg.raise_()
                dlg.activateWindow()
            except Exception:
                pass
            if _exec_dialog(dlg):
                return str(dlg.textValue())
        except Exception:
            pass
    if sys.platform.startswith("linux") and _which("zenity"):
        try:
            p = subprocess.run([
                "zenity", "--entry", "--title", title, "--text", label,
                "--entry-text", _load_last_suffix()
            ], capture_output=True, text=True)
            if p.returncode == 0:
                return (p.stdout or "").strip()
        except Exception:
            pass
    if sys.platform == "darwin" and _which("osascript"):
        try:
            script = f'display dialog {label!r} default answer {_load_last_suffix()!r} with title {title!r} buttons {"OK"!r} default button 1'
            p = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            if p.returncode == 0:
                out = p.stdout or ""
                val = _extract_osascript_text(out)
                if val != "":
                    return val
        except Exception:
            pass
    return _load_last_suffix()


# Find & Replace prompt (two fields). If replace is empty string, treat as delete.

def _prompt_find_replace(title="Find & Replace", label_find="Find:", label_repl="Replace with (empty = delete):"):
    # 1) Qt: show two dialogs sequentially, centered
    if _has_qt():
        try:
            parent = _parent_widget()
            # First: Find
            dlg1 = QtWidgets.QInputDialog(parent)
            _apply_flat_style(dlg1)
            dlg1.setWindowTitle(title)
            dlg1.setLabelText(label_find)
            dlg1.setTextValue(_load_last_find())
            dlg1.show()
            if QtWidgets is not None:
                QtWidgets.QApplication.processEvents()
            _center_on_screen(dlg1)
            try:
                dlg1.raise_()
                dlg1.activateWindow()
            except Exception:
                pass
            if not _exec_dialog(dlg1):
                return None, None
            f = str(dlg1.textValue())

            # Second: Replace
            dlg2 = QtWidgets.QInputDialog(parent)
            _apply_flat_style(dlg2)
            dlg2.setWindowTitle(title)
            dlg2.setLabelText(label_repl)
            dlg2.setTextValue(_load_last_repl())
            dlg2.show()
            if QtWidgets is not None:
                QtWidgets.QApplication.processEvents()
            _center_on_screen(dlg2)
            try:
                dlg2.raise_()
                dlg2.activateWindow()
            except Exception:
                pass
            if not _exec_dialog(dlg2):
                return None, None
            r = str(dlg2.textValue())

            return f, r
        except Exception:
            pass
    # 2) Linux: zenity (two sequential entries for reliability)
    if sys.platform.startswith("linux") and _which("zenity"):
        try:
            p1 = subprocess.run(["zenity", "--entry", "--title", title, "--text", label_find, "--entry-text", _load_last_find()], capture_output=True, text=True)
            if p1.returncode != 0:
                return None, None
            p2 = subprocess.run(["zenity", "--entry", "--title", title, "--text", label_repl, "--entry-text", _load_last_repl()], capture_output=True, text=True)
            if p2.returncode != 0:
                return None, None
            return (p1.stdout or "").strip(), (p2.stdout or "").strip()
        except Exception:
            pass
    # 3) macOS: AppleScript two dialogs
    if sys.platform == "darwin" and _which("osascript"):
        try:
            script1 = f'display dialog {label_find!r} default answer {_load_last_find()!r} with title {title!r} buttons {"OK"!r} default button 1'
            p1 = subprocess.run(["osascript", "-e", script1], capture_output=True, text=True)
            if p1.returncode != 0:
                return None, None
            out1 = p1.stdout or ""
            fval = _extract_osascript_text(out1)
            script2 = f'display dialog {label_repl!r} default answer {_load_last_repl()!r} with title {title!r} buttons {"OK"!r} default button 1'
            p2 = subprocess.run(["osascript", "-e", script2], capture_output=True, text=True)
            if p2.returncode != 0:
                return None, None
            out2 = p2.stdout or ""
            rval = _extract_osascript_text(out2)
            return fval, rval
        except Exception:
            pass
    # 4) Fallback: use last values (could be empty strings)
    return _load_last_find(), _load_last_repl()


# ----------------- Flame selection + rename -----------------
try:
    import flame
except Exception:
    flame = None


def _collect_selection():
    items = []
    # Media Panel
    try:
        sel = getattr(getattr(flame, 'media_panel', None), 'selected_entries', None)
        if sel:
            items.extend(list(sel))
    except Exception:
        pass
    # Timeline (varies by build)
    try:
        tl = getattr(flame, 'timeline', None)
        for attr in ('selected_segments', 'selectedEntries', 'selected_clips'):
            val = getattr(tl, attr, None)
            if val:
                items.extend(list(val))
                break
    except Exception:
        pass
    # de-duplicate to avoid double processing the same object reference
    uniq, seen = [], set()
    for it in items:
        k = id(it)
        if k not in seen:
            uniq.append(it)
            seen.add(k)
    return uniq



# --- Name sanitizer ---
def _sanitize_name(s):
    """Trim and remove control characters/newlines/tabs from the proposed name."""
    try:
        t = str(s)
    except Exception:
        return s
    # Replace common control whitespace with a space, strip ends
    t = t.replace("\r", " ").replace("\n", " ").replace("\t", " ")
    # Drop other non-printable control chars
    t = "".join(ch for ch in t if ch.isprintable())
    return t.strip()

def _safe_set_name(item, new_name):
    new_name = _sanitize_name(new_name)
    try:
        cur = _strip_outer_quotes(getattr(item, 'name', ''))
        if new_name == cur:
            return
    except Exception:
        pass
    try:
        item.name = new_name
    except Exception as e:
        print("[Rename Tools] Rename failed:", e)


def _strip_outer_quotes(s):
    """Return s without surrounding single/double quotes (only if both ends match)."""
    try:
        t = str(s).strip()
    except Exception:
        return s
    if len(t) >= 2 and t[0] == t[-1] and t[0] in ("'", '"'):
        return t[1:-1]
    return t


# ----------------- in-script undo buffer -----------------
# Stores a single-level undo list of (weakref(item), old_name, new_name)
_LAST_RENAMES = []


def _undo_buffer_clear():
    global _LAST_RENAMES
    _LAST_RENAMES = []


def _undo_buffer_push(item, old_name, new_name):
    try:
        _LAST_RENAMES.append((weakref.ref(item), str(old_name), str(new_name)))
    except Exception:
        pass


def _can_undo_last():
    # True if the buffer has at least one valid live item
    try:
        return any(ref() is not None for ref, _, _ in _LAST_RENAMES)
    except Exception:
        return False


def _perform_undo_last():
    """Restore previous names from the last rename operation.
    Only items that are still alive will be restored.
    """
    global _LAST_RENAMES
    if not _LAST_RENAMES:
        return 0
    restored = 0
    newbuf = []
    for ref, old_name, new_name in _LAST_RENAMES:
        it = None
        try:
            it = ref()
        except Exception:
            it = None
        if it is None:
            continue
        try:
            # Only restore if current name still matches the new_name we set
            cur = _strip_outer_quotes(getattr(it, 'name', ''))
            if cur == new_name:
                it.name = old_name
                restored += 1
            else:
                # Keep entries we didn't restore (changed elsewhere)
                newbuf.append((ref, old_name, new_name))
        except Exception:
            newbuf.append((ref, old_name, new_name))
    _LAST_RENAMES = newbuf  # keep non-restored items for another attempt
    return restored



# ----------------- rename target resolver (operate on CLIP only) -----------------

def _as_clip_target(obj):
    """Return the clip-like object to rename. If selection is a segment, pick its clip/source/media.
    Never returns a segment itself, so segment names are never modified.
    """
    try:
        # If already a clip, use it directly
        if _is_clip_like(obj):
            return obj
        # If it's a segment-like object, try common backrefs without touching the segment
        if _is_segment_like(obj):
            for ref_attr in ("clip", "source", "media"):
                try:
                    ref = getattr(obj, ref_attr, None)
                except Exception:
                    ref = None
                if ref is not None and _is_clip_like(ref):
                    return ref
        return None
    except Exception:
        return None


# ----------------- actions -----------------

# -------- runners used by panel (return changed count) --------

def _run_prefix_with(prefix, idem=True):
    """Apply prefix to current selection; return number of changed items."""
    if not isinstance(prefix, str):
        return 0
    prefix = _sanitize_name(prefix)
    if prefix == "":
        return 0
    changed = 0
    _undo_buffer_clear()
    items = _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.startswith(prefix):
                continue
            new_name = f"{prefix}{base}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Prefix (panel) failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} prefix(panel)='{prefix}' changed={changed} idem={idem}\n")
    except Exception:
        pass
    # persist last-used
    _save_last_prefix(prefix)
    _save_last_idem("prefix", idem)
    return changed


def _run_suffix_with(suffix, idem=True):
    """Apply suffix to current selection; return number of changed items."""
    if not isinstance(suffix, str):
        return 0
    suffix = _sanitize_name(suffix)
    if suffix == "":
        return 0
    changed = 0
    _undo_buffer_clear()
    items = _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.endswith(suffix):
                continue
            new_name = f"{base}{suffix}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Suffix (panel) failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} suffix(panel)='{suffix}' changed={changed} idem={idem}\n")
    except Exception:
        pass
    _save_last_suffix(suffix)
    _save_last_idem("suffix", idem)
    return changed


def _run_findreplace_with(find, repl):
    """Apply find/replace to current selection; return number of changed items."""
    find = "" if find is None else str(find)
    repl = "" if repl is None else str(repl)
    # Empty find → no-op
    if find == "":
        return 0
    changed = 0
    _undo_buffer_clear()
    items = _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            new_name = base.replace(find, repl)
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Find&Replace (panel) failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} find(panel)='{find}' repl(panel)='{repl}' changed={changed}\n")
    except Exception:
        pass
    _save_last_find(find)
    _save_last_repl(repl)
    return changed

def _action_add_prefix(selection=None):
    prefix, idem = _prompt_prefix_opts()
    if not isinstance(prefix, str):
        return
    if idem is None:
        idem = _load_last_idem("prefix")
    changed = 0
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.startswith(prefix):
                continue
            new_name = f"{prefix}{base}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Rename failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} prefix='{prefix}' changed={changed} idem={idem}\n")
    except Exception:
        pass


def _action_add_prefix_last(selection=None):
    prefix = _load_last_prefix()
    idem = _load_last_idem("prefix")
    changed = 0
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.startswith(prefix):
                continue
            new_name = f"{prefix}{base}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Rename failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} prefix(last)='{prefix}' changed={changed} idem={idem}\n")
    except Exception:
        pass


def _action_add_suffix(selection=None):
    suffix, idem = _prompt_suffix_opts()
    if not isinstance(suffix, str):
        return
    if idem is None:
        idem = _load_last_idem("suffix")
    changed = 0
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.endswith(suffix):
                continue
            new_name = f"{base}{suffix}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Rename failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} suffix='{suffix}' changed={changed} idem={idem}\n")
    except Exception:
        pass


def _action_add_suffix_last(selection=None):
    suffix = _load_last_suffix()
    idem = _load_last_idem("suffix")
    changed = 0
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            if idem and base.endswith(suffix):
                continue
            new_name = f"{base}{suffix}"
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Rename failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} suffix(last)='{suffix}' changed={changed} idem={idem}\n")
    except Exception:
        pass


def _action_find_replace(selection=None):
    find, repl = _prompt_find_replace()
    # If user cancelled
    if find is None and repl is None:
        return
    find = "" if find is None else str(find)
    repl = "" if repl is None else str(repl)
    # Save last values
    _save_last_find(find)
    _save_last_repl(repl)
    # Empty find string → no-op (avoid replacing everything)
    if find == "":
        return
    changed = 0
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            new_name = base.replace(find, repl)
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Find&Replace failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} find='{find}' repl='{repl}' changed={changed}\n")
    except Exception:
        pass


def _action_find_replace_last(selection=None):
    find = _load_last_find()
    repl = _load_last_repl()
    if not isinstance(find, str):
        return
    changed = 0
    if find == "":
        return
    _undo_buffer_clear()
    items = list(selection) if selection else _collect_selection()
    for it in items:
        try:
            target = _as_clip_target(it)
            if target is None:
                continue
            base = _strip_outer_quotes(getattr(target, 'name', ''))
            new_name = base.replace(find, repl)
            if new_name == base:
                continue
            _undo_buffer_push(target, base, new_name)
            _safe_set_name(target, new_name)
            changed += 1
        except Exception as e:
            print("[Rename Tools] Find&Replace failed:", e)
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} find(last)='{find}' repl(last)='{repl}' changed={changed}\n")
    except Exception:
        pass


# Undo action

def _action_undo_last(selection=None):
    restored = _perform_undo_last()
    try:
        with open("/tmp/flame_prefix_action.log", "a") as f:
            f.write(f"{datetime.datetime.now().isoformat()} undo_last restored={restored}\n")
    except Exception:
        pass


# ----------------- unified panel (Qt) -----------------

def show_rename_panel(selection=None):
    """Open a non-modal panel to choose mode (Prefix / Suffix / Find&Replace) and apply."""
    if not _has_qt():
        print("[Rename Tools] Qt is not available; panel cannot be shown.")
        return
    parent = _parent_widget()
    dlg = QtWidgets.QDialog(parent)
    dlg.setWindowTitle("Rename Tools")
    dlg.setModal(False)
    dlg.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)

    # Root layout
    root = QtWidgets.QVBoxLayout(dlg)
    root.setContentsMargins(16, 16, 16, 16)
    root.setSpacing(12)

    # Tabs
    tabs = QtWidgets.QTabWidget(dlg)

    # --- Prefix tab
    w_pre = QtWidgets.QWidget(dlg)
    l_pre = QtWidgets.QGridLayout(w_pre)
    l_pre.setColumnMinimumWidth(0, 90)
    l_pre.setColumnStretch(1, 1)
    pre_edit = QtWidgets.QLineEdit(_load_last_prefix(), w_pre)
    pre_edit.setPlaceholderText("Enter prefix")
    pre_idem = QtWidgets.QCheckBox("Prevent duplicate addition (idempotent)", w_pre)
    pre_idem.setChecked(_load_last_idem("prefix"))
    l_pre.addWidget(QtWidgets.QLabel("Prefix:", w_pre), 0, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    l_pre.addWidget(pre_edit, 0, 1)
    l_pre.addWidget(pre_idem, 1, 1)
    tabs.addTab(w_pre, "Prefix")

    # --- Suffix tab
    w_suf = QtWidgets.QWidget(dlg)
    l_suf = QtWidgets.QGridLayout(w_suf)
    l_suf.setColumnMinimumWidth(0, 90)
    l_suf.setColumnStretch(1, 1)
    suf_edit = QtWidgets.QLineEdit(_load_last_suffix(), w_suf)
    suf_edit.setPlaceholderText("Enter suffix")
    suf_idem = QtWidgets.QCheckBox("Prevent duplicate addition (idempotent)", w_suf)
    suf_idem.setChecked(_load_last_idem("suffix"))
    l_suf.addWidget(QtWidgets.QLabel("Suffix:", w_suf), 0, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    l_suf.addWidget(suf_edit, 0, 1)
    l_suf.addWidget(suf_idem, 1, 1)
    tabs.addTab(w_suf, "Suffix")

    # --- Find & Replace tab
    w_fr = QtWidgets.QWidget(dlg)
    l_fr = QtWidgets.QGridLayout(w_fr)
    l_fr.setColumnMinimumWidth(0, 90)
    l_fr.setColumnStretch(1, 1)
    find_edit = QtWidgets.QLineEdit(_load_last_find(), w_fr)
    repl_edit = QtWidgets.QLineEdit(_load_last_repl(), w_fr)
    find_edit.setPlaceholderText("Find…")
    repl_edit.setPlaceholderText("Replace with (empty = delete)")
    l_fr.addWidget(QtWidgets.QLabel("Find:", w_fr), 0, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    l_fr.addWidget(find_edit, 0, 1)
    l_fr.addWidget(QtWidgets.QLabel("Replace:", w_fr), 1, 0, QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    l_fr.addWidget(repl_edit, 1, 1)
    tabs.addTab(w_fr, "Find & Replace")

    root.addWidget(tabs)

    # Preview area
    preview_group = QtWidgets.QGroupBox("Preview", dlg)
    preview_layout = QtWidgets.QFormLayout(preview_group)
    preview_layout.setLabelAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
    preview_before = QtWidgets.QLineEdit(preview_group)
    preview_after = QtWidgets.QLineEdit(preview_group)
    preview_before.setReadOnly(True)
    preview_after.setReadOnly(True)
    preview_before.setPlaceholderText("No valid clip selected")
    preview_after.setPlaceholderText("No preview available")
    preview_layout.addRow("Before:", preview_before)
    preview_layout.addRow("After:", preview_after)
    root.addWidget(preview_group)

    # Log/output
    log = QtWidgets.QPlainTextEdit(dlg)
    log.setReadOnly(True)
    log.setPlaceholderText("Logs will appear here…")
    log.setMinimumHeight(120)

    # Buttons
    # Row 1: centered Apply + Undo
    row_actions = QtWidgets.QHBoxLayout()
    btn_apply = QtWidgets.QPushButton("Apply")
    btn_undo = QtWidgets.QPushButton("Undo Last")
    # Give buttons a comfortable minimum width
    for b in (btn_apply, btn_undo):
        try:
            b.setMinimumWidth(120)
        except Exception:
            pass
    row_actions.addStretch(1)
    row_actions.addWidget(btn_apply)
    row_actions.addSpacing(16)
    row_actions.addWidget(btn_undo)
    row_actions.addStretch(1)

    # Row 2: Close at bottom-right
    row_close = QtWidgets.QHBoxLayout()
    btn_close = QtWidgets.QPushButton("Close")
    try:
        btn_close.setMinimumWidth(120)
    except Exception:
        pass
    row_close.addStretch(1)
    row_close.addWidget(btn_close)

    root.addLayout(row_actions)
    root.addWidget(log)
    root.addLayout(row_close)

    def _append(msg):
        try:
            log.appendPlainText(msg)
        except Exception:
            print("[Rename Tools]", msg)

    def _first_preview_target():
        try:
            items = list(selection) if selection else _collect_selection()
            for it in items:
                target = _as_clip_target(it)
                if target is not None:
                    return target
        except Exception:
            pass
        return None

    def _compute_preview_name(base):
        try:
            idx = tabs.currentIndex()
            if idx == 0:
                val = _sanitize_name(pre_edit.text())
                idem = pre_idem.isChecked()
                if val == "":
                    return base
                if idem and base.startswith(val):
                    return base
                return f"{val}{base}"
            if idx == 1:
                val = _sanitize_name(suf_edit.text())
                idem = suf_idem.isChecked()
                if val == "":
                    return base
                if idem and base.endswith(val):
                    return base
                return f"{base}{val}"
            f = find_edit.text()
            r = repl_edit.text()
            if f == "":
                return base
            return base.replace(f, r)
        except Exception:
            return base

    def update_preview():
        target = _first_preview_target()
        if target is None:
            preview_before.setText("")
            preview_after.setText("")
            return
        try:
            base = _strip_outer_quotes(getattr(target, 'name', ''))
        except Exception:
            base = ""
        preview_before.setText(base)
        preview_after.setText(_compute_preview_name(base))

    def on_apply():
        idx = tabs.currentIndex()
        if idx == 0:
            val = pre_edit.text()
            idem = pre_idem.isChecked()
            n = _run_prefix_with(val, idem)
            _append(f"Prefix applied: '{val}' (idempotent={idem}) → changed={n}")
        elif idx == 1:
            val = suf_edit.text()
            idem = suf_idem.isChecked()
            n = _run_suffix_with(val, idem)
            _append(f"Suffix applied: '{val}' (idempotent={idem}) → changed={n}")
        else:
            f = find_edit.text()
            r = repl_edit.text()
            n = _run_findreplace_with(f, r)
            _append(f"Find/Replace: find='{f}' repl='{r}' → changed={n}")
        update_preview()

    def on_undo():
        restored = _perform_undo_last()
        _append(f"Undo Last: restored={restored}")
        update_preview()

    btn_apply.clicked.connect(on_apply)
    btn_undo.clicked.connect(on_undo)
    btn_close.clicked.connect(dlg.close)

    for widget in (pre_edit, suf_edit, find_edit, repl_edit):
        try:
            widget.textChanged.connect(update_preview)
        except Exception:
            pass
    for widget in (pre_idem, suf_idem):
        try:
            widget.toggled.connect(update_preview)
        except Exception:
            pass
    try:
        tabs.currentChanged.connect(update_preview)
    except Exception:
        pass

    # style and show
    update_preview()
    _apply_flat_style(dlg)
    dlg.resize(560, 520)
    dlg.show()
    if QtWidgets is not None:
        QtWidgets.QApplication.processEvents()
    _center_on_screen(dlg)
    try:
        dlg.raise_(); dlg.activateWindow()
    except Exception:
        pass


# ----------------- menu -----------------

#
# ----------------- scope helpers (selection-based, like flameTimewarpML) -----------------

def _is_clip_like(obj):
    """Heuristic + typed check for Media Panel clip-like items."""
    try:
        # Prefer typed check if available
        if 'flame' in globals() and flame is not None:
            try:
                if hasattr(flame, 'PyClip') and isinstance(obj, flame.PyClip):
                    return True
            except Exception:
                pass
        # Fallback: class name heuristic
        cls = type(obj).__name__
        return ('PyClip' in cls) or (cls.endswith('Clip')) or ('Clip' in getattr(getattr(obj, '__class__', None), '__name__', ''))
    except Exception:
        return False


def _is_segment_like(obj):
    """Heuristic + typed check for Timeline segment-like items."""
    try:
        if 'flame' in globals() and flame is not None:
            try:
                if hasattr(flame, 'PySegment') and isinstance(obj, flame.PySegment):
                    return True
            except Exception:
                pass
        cls = type(obj).__name__
        return ('PySegment' in cls) or ('Segment' in cls)
    except Exception:
        return False


def _scope_clip_or_segment(selection):
    """Return True when the context selection contains a clip or a segment.
    Mirrors the common pattern used in community tools (e.g. flameTimewarpML)
    by relying on the selection passed by Flame at right-click time.
    """
    try:
        if not selection:
            return False
        for it in selection:
            if _is_clip_like(it) or _is_segment_like(it):
                return True
        return False
    except Exception:
        return False



# Stricter scopes per area

def _scope_media_clip(selection):
    """Media Panel: show only when a real Clip is selected (exclude reels/folders)."""
    try:
        if not selection or flame is None or not hasattr(flame, 'PyClip'):
            return False
        for it in selection:
            if isinstance(it, flame.PyClip):
                return True
        return False
    except Exception:
        return False


def _scope_timeline_segment(selection):
    """Timeline: show only when a Segment (or Clip) is selected on the timeline."""
    try:
        if not selection or flame is None:
            return False
        ok = False
        if hasattr(flame, 'PySegment'):
            ok = any(isinstance(it, flame.PySegment) for it in selection)
        if not ok and hasattr(flame, 'PyClip'):
            # Some builds may surface clips directly on timeline
            ok = any(isinstance(it, flame.PyClip) for it in selection)
        return ok
    except Exception:
        return False


def _menu_def(scope_fn):
    return [{
        "name": "Rename Tools",
        "isVisible": scope_fn,
        "actions": [
            {"name": "Open Rename Panel…", "execute": show_rename_panel,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Add Prefix…", "execute": _action_add_prefix,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Add Prefix (use last/default)", "execute": _action_add_prefix_last,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Add Suffix…", "execute": _action_add_suffix,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Add Suffix (use last/default)", "execute": _action_add_suffix_last,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Find & Replace… (empty=delete)", "execute": _action_find_replace,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Find & Replace (use last, empty=delete)", "execute": _action_find_replace_last,
             "isVisible": scope_fn, "isEnabled": scope_fn},
            {"name": "Undo Last Rename", "execute": _action_undo_last,
             "isVisible": scope_fn,
             "isEnabled": lambda s: _can_undo_last() and scope_fn(s)},
        ]
    }]


def get_media_panel_custom_ui_actions():
    return _menu_def(_scope_media_clip)


def get_timeline_custom_ui_actions():
    return _menu_def(_scope_timeline_segment)