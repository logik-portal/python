"""
Script Name: Change Render Destination
Script Version: 1.0.0
Flame Version: 2025.1
Written by: Gaspar
Creation Date: 05.06.26
Update Date: 05.06.26

Script Type: Media Panel

Description:

    Change the render destination of all Render nodes in the selected batch groups.

Usage:

    Select one or more batch groups in the Media Panel Desktop.

URL:

    https://logik-portal.com/scripts/#change_render_destination

Menus:

    Media Panel:

        Right-click on any batch group(s) in media panel desktop -> Change Render Destination...

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 05.06.26
        - Initial release.
"""

# ─────────────────────────────────────────────────────────────────────────────
# [Imports]
# ─────────────────────────────────────────────────────────────────────────────

import flame
from lib.pyflame_lib_change_render_destination import *

# ─────────────────────────────────────────────────────────────────────────────
# [Constants]
# ─────────────────────────────────────────────────────────────────────────────

SCRIPT_NAME = 'Change Render Destination'

# ─────────────────────────────────────────────────────────────────────────────
# Helpers — query Flame API
# ─────────────────────────────────────────────────────────────────────────────

def _get_batch_reels():
    """Return reel names from the currently open batch."""
    try:
        return [str(r.name)[1:-1] for r in flame.batch.reels]
    except Exception:
        return ['Batch Renders']

def _get_reel_groups():
    """Return {group_name: [reel_name, ...]} for all reel groups on the desktop."""
    groups = {}
    try:
        desktop = flame.project.current_project.current_workspace.desktop
        for rg in desktop.reel_groups:
            rg_name = str(rg.name)[1:-1]
            try:
                reels = [str(r.name)[1:-1] for r in rg.reels]
            except Exception:
                reels = []
            reels += ['Topmost Reel', 'Bottommost Reel']
            groups[rg_name] = reels
    except Exception:
        pass
    if not groups:
        groups = {'Reels': ['Reel 1', 'Topmost Reel', 'Bottommost Reel']}
    return groups


def _get_libraries():
    """Return library names from the current workspace."""
    try:
        ws = flame.project.current_project.current_workspace
        return [str(lib.name)[1:-1] for lib in ws.libraries]
    except Exception:
        return ['Default Library']

# ─────────────────────────────────────────────────────────────────────────────
# Window
# ─────────────────────────────────────────────────────────────────────────────

class ChangeDestinationWindow:

    def __init__(self, batch_groups: list) -> None:
        self.batch_groups = batch_groups

        self._batch_reels = _get_batch_reels()
        self._reel_groups = _get_reel_groups()
        self._libraries   = _get_libraries()

        self._build_window()

    def _build_window(self) -> None:

        def on_dest_changed() -> None:
            """Update sub-menus when destination type changes."""
            dest = self.dest_menu.text
            if dest == 'Batch Reel':
                self.sub1_label.setText('Reel')
                self.sub1_label.setVisible(True)
                first = self._batch_reels[0] if self._batch_reels else ''
                self.sub1_menu.update_menu(text=first, menu_options=self._batch_reels)
                self.sub1_menu.setVisible(True)
                self.sub2_label.setVisible(False)
                self.sub2_menu.setVisible(False)
            elif dest == 'Reel Group':
                self.sub1_label.setText('Reel Group')
                self.sub1_label.setVisible(True)
                rg_keys = list(self._reel_groups.keys())
                first_group = rg_keys[0] if rg_keys else ''
                self.sub1_menu.update_menu(text=first_group, menu_options=rg_keys)
                self.sub1_menu.setVisible(True)
                self.sub2_label.setVisible(True)
                self.sub2_menu.setVisible(True)
                on_group_changed()
            else:  # Library — pas de sous-menu
                self.sub1_label.setVisible(False)
                self.sub1_menu.setVisible(False)
                self.sub2_label.setVisible(False)
                self.sub2_menu.setVisible(False)

        def on_group_changed() -> None:
            """Update reel list when reel group changes."""
            group = self.sub1_menu.text
            reels = self._reel_groups.get(group, [])
            first_reel = reels[0] if reels else ''
            self.sub2_menu.update_menu(text=first_reel, menu_options=reels)

        def apply() -> None:
            dest = self.dest_menu.text
            if dest == 'Batch Reel':
                destination = ('Batch Reels', self.sub1_menu.text)
            elif dest == 'Reel Group':
                destination = ('Reel Groups', self.sub1_menu.text, self.sub2_menu.text)
            else:  # Library
                destination = ('Libraries', '')

            changed     = 0
            total_nodes = 0
            errors      = []

            for batch_group in self.batch_groups:
                batch_name = str(batch_group.name)[1:-1]
                try:
                    for node in batch_group.nodes:
                        if node.type == 'Render':
                            total_nodes += 1
                            try:
                                node.destination = destination
                                changed += 1
                            except Exception as e:
                                errors.append(f"'{batch_name}' / '{node.name}': {e}")
                except Exception as e:
                    errors.append(f"Error on '{batch_name}': {e}")

            self.window.close()

            dest_label = ' \u2192 '.join(str(d) for d in destination if d)
            msg = f'Destination updated on {changed}/{total_nodes} node(s) Render\n{dest_label}'
            if errors:
                msg += '\n\nErrors :\n' + '\n'.join(errors)
            PyFlameMessageWindow(message=msg, parent=None)

        def cancel() -> None:
            self.window.close()

        # ── Window ────────────────────────────────────────────────────────
        self.window = PyFlameWindow(
            title=SCRIPT_NAME,
            grid_layout_columns=2,
            grid_layout_rows=5,
            grid_layout_column_width=180,
            parent=None,
        )

        # ── Labels ────────────────────────────────────────────────────────
        self.dest_label = PyFlameLabel(text='Destination')
        self.sub1_label = PyFlameLabel(text='Reel')
        self.sub2_label = PyFlameLabel(text='Reel')

        # ── Menus ─────────────────────────────────────────────────────────
        self.dest_menu = PyFlameMenu(
            text='Batch Reel',
            menu_options=['Batch Reel', 'Reel Group', 'Library'],
            connect=on_dest_changed,
        )
        self.sub1_menu = PyFlameMenu(
            text=self._batch_reels[0] if self._batch_reels else '',
            menu_options=self._batch_reels,
            connect=on_group_changed,
        )
        first_group  = list(self._reel_groups.keys())[0]
        first_reels  = self._reel_groups.get(first_group, [])
        self.sub2_menu = PyFlameMenu(
            text=first_reels[0] if first_reels else '',
            menu_options=first_reels,
        )

        # Row 2 hidden by default (Batch Reel selected at start)
        self.sub2_label.setVisible(False)
        self.sub2_menu.setVisible(False)

        # ── Buttons ───────────────────────────────────────────────────────
        self.cancel_btn = PyFlameButton(text='Cancel', connect=cancel)
        self.apply_btn  = PyFlameButton(text='Apply',  connect=apply, color=Color.BLUE)

        # ── Layout ────────────────────────────────────────────────────────
        self.window.grid_layout.addWidget(self.dest_label,  0, 0)
        self.window.grid_layout.addWidget(self.dest_menu,   0, 1)
        self.window.grid_layout.addWidget(self.sub1_label,  1, 0)
        self.window.grid_layout.addWidget(self.sub1_menu,   1, 1)
        self.window.grid_layout.addWidget(self.sub2_label,  2, 0)
        self.window.grid_layout.addWidget(self.sub2_menu,   2, 1)
        self.window.grid_layout.addWidget(self.cancel_btn,  4, 0)
        self.window.grid_layout.addWidget(self.apply_btn,   4, 1)

# ─────────────────────────────────────────────────────────────────────────────
# Main action
# ─────────────────────────────────────────────────────────────────────────────

def change_render_destination(selection):
    """Change the render destination of all Render nodes in the selected batch groups."""

    batch_groups = [
        item for item in selection
        if isinstance(item, flame.PyBatch) and isinstance(item.parent, flame.PyDesktop)
    ]

    if not batch_groups:
        PyFlameMessageWindow(
            message='No batch group selected in the desktop.',
            message_type=MessageType.ERROR,
            parent=None,
        )
        return

    ChangeDestinationWindow(batch_groups)

# ─────────────────────────────────────────────────────────────────────────────
# Scope & menu registration
# ─────────────────────────────────────────────────────────────────────────────

def scope_batch(selection):
    for item in selection:
        if isinstance(item, flame.PyBatch):
            if isinstance(item.parent, flame.PyDesktop):
                return True
    return False


def get_media_panel_custom_ui_actions():
    return [
        {
            'hierarchy': [],
            'actions': [
                {
                    'name': 'Change Render Destination...',
                    'execute': change_render_destination,
                    'isVisible': scope_batch,
                    'minimumVersion': '2025.1',
                }
            ]
        }
    ]
