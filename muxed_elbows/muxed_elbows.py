# Muxed Elbows
# Copyright (c) 2026 Michael Vaglienty
#
# This program is licensed under the MIT License.
# See the LICENSE file for the full license text.
#
# License:       MIT License (MIT)
#                https://opensource.org/licenses/MIT

"""
Script Name: Muxed Elbows
Script Version: 1.0.0
Flame Version: 2027.2
Written by: Michael Vaglienty
Creation Date: 11.11.26
Update Date: 11.11.26

License: MIT License (MIT) - see LICENSE file for details

Script Type: Batch

Description:

    Convert Mux nodes to Elbow nodes, or Elbow nodes to Mux nodes, keeping all connections.

Usage:

    Each connected Mux input becomes its own Elbow. Each Elbow becomes a Mux connected through its Front input and Result output.
    Elbows can also become Mux nodes frozen at the current frame, named after that frame.
    Mux and Elbow nodes with no connections are skipped. If a node can't be converted, it's put back the way it was.

URL:

    https://logik-portal.com/scripts/muxed_elbows

Menus:

    MUX nodes to elbows:
    
        Right-click selected Mux nodes in Batch -> MUX -> Elbow

    Elbows to MUX nodes:

        Right-click selected Elbow nodes in Batch -> Elbow -> MUX

    Elbows to MUX nodes frozen at the current frame:

        Right-click selected Elbow nodes in Batch -> Elbow -> Frozen MUX

To install:

    Copy script folder into /opt/Autodesk/shared/python

Updates:

    v1.0.0 11.11.26
        - Initial release.
"""

# ==============================================================================
# [Imports]
# ==============================================================================

from __future__ import annotations

import os

import flame
from lib.pyflame_lib_muxed_elbows import *

# ==============================================================================
# [Constants]
# ==============================================================================

SCRIPT_NAME = 'Muxed Elbows'
SCRIPT_VERSION = 'v1.0.0'
SCRIPT_PATH = os.path.abspath(os.path.dirname(__file__))

# ==============================================================================
# [Main Script]
# ==============================================================================

class MuxedElbows:

    def __init__(self, selection, freeze: bool = False) -> None:
        """
        Init
        ====

        Convert every selected Mux node to Elbow nodes, or every selected Elbow node to a Mux node.

        Args
        ----
            selection (list):
                Items selected in Flame when the menu was run.

            freeze (bool):
                Freeze each new Mux at the current frame (Elbow -> Frozen MUX).
        """

        # Get the menu action from the first selected node
        action = 'MUX -> Elbow'
        try:
            if selection[0].type.get_value() == 'Elbow':
                action = 'Elbow -> Frozen MUX' if freeze else 'Elbow -> MUX'
        except Exception:
            pass

        pyflame.print_title(f'{SCRIPT_NAME} - {action} {SCRIPT_VERSION}')

        # Check script path, if path is incorrect, stop script.
        if not pyflame.verify_script_install():
            return

        # Convert each selected node, collecting failures and skipped nodes for one message at the end
        errors = []
        skipped = []
        converted = 0
        for node in selection:

            # A node Flame already removed (an Elbow with no connections) has no name
            try:
                node_name = node.name.get_value()
            except Exception:
                node_name = None
            if node_name is None:
                missing_message = 'A selected node no longer exists (Flame removes Elbows with no connections)'
                pyflame.print(missing_message, print_type=PrintType.ERROR)
                errors.append(missing_message)
                continue

            try:
                if node.type.get_value() == 'MUX':
                    node_converted = self.mux_to_elbows(node)
                else:
                    node_converted = self.elbow_to_mux(node, freeze)
                if not node_converted:
                    pyflame.print(f'Skipped {node_name}: node has no connections', print_type=PrintType.WARNING)
                    skipped.append(node_name)
                    continue
                converted += 1
            except Exception as e:
                pyflame.print(f'Could not convert {node_name}: {e}', print_type=PrintType.ERROR)
                errors.append(f'{node_name}: {e}')

        # Message listing skipped nodes
        skipped_message = ''
        if skipped:
            skipped_message = 'Nodes with no connections were skipped:\n\n' + '\n'.join(skipped)

        # Show one window for failures and skipped nodes, then print success
        if errors:
            message = 'Some nodes could not be converted.\n\n' + '\n\n'.join(errors)
            if skipped_message:
                message += '\n\n' + skipped_message
            PyFlameMessageWindow(
                parent=None,
                message=message,
                message_type=MessageType.ERROR,
                )
        elif skipped:
            PyFlameMessageWindow(
                parent=None,
                message=skipped_message,
                message_type=MessageType.INFO,
                )

        if converted:
            pyflame.print(f'Converted {converted} node(s)', text_color=TextColor.GREEN)

    # ==============================================================================

    def get_node(self, node_name: str) -> flame.PyNode:
        """
        Get Node
        ========

        Get a node in the current batch by name.

        Args
        ----
            node_name (str): Name of node.

        Returns
        -------
            node (PyNode): Node with the given name.

        Raises
        ------
            Exception:
                If no node has the given name.
        """

        nodes = [node for node in flame.batch.nodes if node.name.get_value() == node_name]
        if not nodes:
            raise Exception(f'Node {node_name} not found')

        return nodes[0]

    def link_counts(self, node, direction: str, linked_name: str) -> dict:
        """
        Link Counts
        ===========

        Count how many times a linked node name appears in each socket of a node.

        Args
        ----
            node (PyNode):
                Node to read sockets from.

            direction (str):
                'input' or 'output'.

            linked_name (str):
                Name of the linked node to count.

        Returns
        -------
            counts (dict): Socket name -> number of links to linked_name.
        """

        return {socket: links.count(linked_name) for socket, links in node.sockets[direction].items()}

    def changed_socket(self, before: dict, after: dict) -> str:
        """
        Changed Socket
        ==============

        Find the socket whose link count dropped between two link_counts results.

        Args
        ----
            before (dict):
                Link counts before a disconnect.

            after (dict):
                Link counts after a disconnect.

        Returns
        -------
            socket (str): Name of the socket that lost a link.

        Raises
        ------
            Exception:
                If no socket lost a link.
        """

        sockets = [socket for socket in before if before[socket] > after.get(socket, 0)]
        if not sockets:
            raise Exception('Could not find the socket that was disconnected')

        return sockets[0]

    def create_elbow(self, mux) -> flame.PyNode:
        """
        Create Elbow
        ============

        Create a new unconnected Elbow node. Elbows can't be made with create_node, so one is added to the
        Mux Result output (which must have no links) and then disconnected.

        Args
        ----
            mux (PyNode): Mux node to add the Elbow to.

        Returns
        -------
            elbow (PyNode): New Elbow node.

        Raises
        ------
            Exception:
                If the Elbow node could not be created.
        """

        # Add elbow and find it by comparing node names before and after
        names_before = {node.name.get_value() for node in flame.batch.nodes}
        if not mux.add_elbow('Result', False):
            raise Exception('Could not create Elbow node')
        new_name = [node.name.get_value() for node in flame.batch.nodes if node.name.get_value() not in names_before][0]
        elbow = self.get_node(new_name)

        # Free the elbow so the Mux Result is unlinked again
        if not flame.batch.disconnect_node(elbow, 'Front'):
            raise Exception('Could not free new Elbow')

        return elbow

    def rollback(self, error: Exception, links: list, names_before: set, original_elbow_name: str | None = None) -> Exception:
        """
        Rollback
        ========

        Put a node back the way it was after a failed conversion: reconnect its recorded links, then delete every node
        created for it. Nodes are looked up by name, so a node Flame already removed doesn't stop the rollback.

        Args
        ----
            error (Exception):
                Error that stopped the conversion.

            links (list):
                Recorded links of the original node, each as (out_node_name, out_socket, in_node_name, in_socket).

            names_before (set):
                Names of all nodes in the batch before the conversion started.

            original_elbow_name (str | None):
                Name of the original node if it's an Elbow. Created nodes are kept if deleting them would make Flame remove it.
                (Default: `None`)

        Returns
        -------
            error (Exception): Original error with ' (rolled back)' or ' (rollback failed: ...)' added.
        """

        rollback_errors = []

        # Reconnect the original links, freeing each input socket first since it holds one link
        for out_name, out_socket, in_name, in_socket in links:
            try:
                out_node = self.get_node(out_name)
                in_node = self.get_node(in_name)
                flame.batch.disconnect_node(in_node, in_socket)
                if not flame.batch.connect_nodes(out_node, out_socket, in_node, in_socket):
                    raise Exception(f'Could not connect {out_name} {out_socket} to {in_name} {in_socket}')
            except Exception as e:
                rollback_errors.append(str(e))

        # Keep created nodes if the original Elbow has no links, since deleting them would make Flame remove it
        keep_created = False
        if original_elbow_name:
            try:
                original_elbow = self.get_node(original_elbow_name)
                if not any(original_elbow.sockets['input'].values()) and not any(original_elbow.sockets['output'].values()):
                    keep_created = True
                    rollback_errors.append(f'created nodes left in place so {original_elbow_name} is not lost')
            except Exception as e:
                rollback_errors.append(str(e))

        # Delete nodes created for this conversion, after reconnecting so the original keeps its links
        if not keep_created:
            try:
                created_names = [node.name.get_value() for node in flame.batch.nodes if node.name.get_value() not in names_before]
            except Exception as e:
                created_names = []
                rollback_errors.append(f'Could not read created nodes: {e}')
            for created_name in created_names:
                try:
                    nodes = [node for node in flame.batch.nodes if node.name.get_value() == created_name]
                    if nodes and not nodes[0].delete():
                        rollback_errors.append(f'Could not delete {created_name}')
                except Exception as e:
                    rollback_errors.append(f'Could not delete {created_name}: {e}')

        if rollback_errors:
            return Exception(f'{error} (rollback failed: {"; ".join(rollback_errors)})')

        return Exception(f'{error} (rolled back)')

    def mux_to_elbows(self, mux) -> bool:
        """
        Mux To Elbows
        =============

        Replace a Mux node with one Elbow node per connected input, moving all input and output links to the Elbows.
        A Mux with no links is left alone. If anything fails, the Mux is put back the way it was.

        Args
        ----
            mux (PyNode): Mux node to replace.

        Returns
        -------
            converted (bool): True if the Mux was replaced, False if it has no links and was skipped.

        Raises
        ------
            Exception:
                If the Mux could not be replaced. The message says whether it was rolled back.
        """

        mux_name = mux.name.get_value()

        # Leave a Mux with no links alone
        if not any(mux.sockets['input'].values()) and not any(mux.sockets['output'].values()):
            return False

        input_sockets = list(mux.sockets['input'].keys())
        selected_input = mux.input_selection.get_value()
        names_before = {node.name.get_value() for node in flame.batch.nodes}

        # Original links, recorded as each one is found so a failure can be undone
        links = []

        try:
            # Disconnect each connected input, recording the parent and the parent output it came from
            input_links = {}
            for input_socket, parents in mux.sockets['input'].items():
                if not parents:
                    continue
                parent = self.get_node(parents[0])
                before = self.link_counts(parent, 'output', mux_name)
                flame.batch.disconnect_node(mux, input_socket)
                after = self.link_counts(parent, 'output', mux_name)
                parent_socket = self.changed_socket(before, after)
                links.append((parents[0], parent_socket, mux_name, input_socket))
                input_links[input_socket] = (parent, parent_socket)

            # Disconnect each outgoing link, recording which Mux output fed each child input
            output_links = []
            child_names = list(dict.fromkeys(mux.sockets['output']['Result'] + mux.sockets['output']['OutMatte']))
            for child_name in child_names:
                child = self.get_node(child_name)
                for child_socket, parents in child.sockets['input'].items():
                    if mux_name not in parents:
                        continue
                    before = self.link_counts(mux, 'output', child_name)
                    flame.batch.disconnect_node(child, child_socket)
                    after = self.link_counts(mux, 'output', child_name)
                    mux_output = self.changed_socket(before, after)
                    links.append((mux_name, mux_output, child_name, child_socket))
                    output_links.append((mux_output, child, child_socket))

            # Selected input feeds Result, selected matte feeds OutMatte
            output_sources = {
                'Result': f'Input_{selected_input}',
                'OutMatte': f'Matte_{selected_input}',
                }

            # Elbow for each connected input, plus one for the selected input/matte if it isn't connected but its output has children
            elbow_sockets = set(input_links)
            for mux_output, _, _ in output_links:
                if output_sources[mux_output] not in input_sockets:
                    raise Exception(f'Selected input {selected_input} not found on {mux_name}')
                elbow_sockets.add(output_sources[mux_output])

            # Create elbows in socket order, stacked under the Mux position
            mux_x = mux.pos_x.get_value()
            mux_y = mux.pos_y.get_value()
            elbows = {}
            for index, input_socket in enumerate([socket for socket in input_sockets if socket in elbow_sockets]):
                elbow = self.create_elbow(mux)
                elbow.pos_x.set_value(mux_x)
                elbow.pos_y.set_value(mux_y - index * 60)
                if input_socket in input_links:
                    parent, parent_socket = input_links[input_socket]
                    if not flame.batch.connect_nodes(parent, parent_socket, elbow, 'Front'):
                        raise Exception(f'Could not connect {parent.name.get_value()} to new Elbow')
                elbows[input_socket] = elbow

            # Connect children to the elbow that replaces their Mux output
            for mux_output, child, child_socket in output_links:
                if not flame.batch.connect_nodes(elbows[output_sources[mux_output]], 'Result', child, child_socket):
                    raise Exception(f'Could not connect new Elbow to {child.name.get_value()} {child_socket}')

            if not mux.delete():
                raise Exception(f'Could not delete {mux_name}')
        except Exception as e:
            raise self.rollback(e, links, names_before) from e

        pyflame.print(f'{mux_name} replaced with {len(elbows)} Elbow node(s)')

        return True

    def elbow_to_mux(self, elbow, freeze: bool = False) -> bool:
        """
        Elbow To Mux
        ============

        Replace an Elbow node with a Mux node, moving its links to the Mux Input_0 and Result.
        An Elbow with no links is left alone. If anything fails, the Elbow is put back the way it was.

        Args
        ----
            elbow (PyNode):
                Elbow node to replace.

            freeze (bool):
                Freeze the new Mux at the current frame: Range on, start and end at the current frame,
                Repeat First before the range and Repeat Last after it.

        Returns
        -------
            converted (bool): True if the Elbow was replaced, False if it has no links and was skipped.

        Raises
        ------
            Exception:
                If the Elbow could not be replaced. The message says whether it was rolled back.
        """

        elbow_name = elbow.name.get_value()

        # Leave an Elbow with no links alone
        if not any(elbow.sockets['input'].values()) and not any(elbow.sockets['output'].values()):
            return False

        names_before = {node.name.get_value() for node in flame.batch.nodes}

        # Original links, recorded before anything is disconnected so a failure can be undone
        links = []

        try:
            # Get the parent and the parent output feeding the elbow
            parent_link = None
            parents = elbow.sockets['input']['Front']
            if parents:
                parent = self.get_node(parents[0])
                parent_sockets = [socket for socket, children in parent.sockets['output'].items() if elbow_name in children]
                if not parent_sockets:
                    raise Exception(f'Could not find the output of {parents[0]} feeding the Elbow')
                parent_link = (parent, parent_sockets[0])
                links.append((parents[0], parent_sockets[0], elbow_name, 'Front'))

            # Get every child input fed by the elbow
            output_links = []
            for child_name in dict.fromkeys(elbow.sockets['output']['Result']):
                child = self.get_node(child_name)
                for child_socket, child_parents in child.sockets['input'].items():
                    if elbow_name in child_parents:
                        output_links.append((child, child_socket))
                        links.append((elbow_name, 'Result', child_name, child_socket))

            # Create Mux at the elbow position
            mux = flame.batch.create_node('MUX')
            mux_name = mux.name.get_value()
            mux.pos_x.set_value(elbow.pos_x.get_value())
            mux.pos_y.set_value(elbow.pos_y.get_value())

            # Freeze Mux at the current frame
            if freeze:
                current_frame = flame.batch.current_frame.get_value()
                mux.range_active.set_value(True)
                mux.range_start.set_value(current_frame)
                mux.range_end.set_value(current_frame)
                mux.before_range.set_value('Repeat First')
                mux.after_range.set_value('Repeat Last')

                # Name Mux after the frozen frame, adding a number if the name is taken
                mux_name = f'freeze_frame_{current_frame}'
                name_number = 1
                while mux_name in names_before:
                    mux_name = f'freeze_frame_{current_frame}_{name_number}'
                    name_number += 1
                mux.name.set_value(mux_name)

            # Move links from the elbow to the Mux front input/output
            if parent_link:
                flame.batch.disconnect_node(elbow, 'Front')
                if not flame.batch.connect_nodes(parent_link[0], parent_link[1], mux, 'Input_0'):
                    raise Exception(f'Could not connect {parents[0]} to new Mux')
            for child, child_socket in output_links:
                flame.batch.disconnect_node(child, child_socket)
                if not flame.batch.connect_nodes(mux, 'Result', child, child_socket):
                    raise Exception(f'Could not connect new Mux to {child.name.get_value()} {child_socket}')

            if not elbow.delete():
                raise Exception(f'Could not delete {elbow_name}')
        except Exception as e:
            raise self.rollback(e, links, names_before, elbow_name) from e

        if freeze:
            pyflame.print(f'{elbow_name} replaced with {mux_name} frozen at frame {current_frame}')
        else:
            pyflame.print(f'{elbow_name} replaced with {mux_name}')

        return True

# ==============================================================================
# [Scopes]
# ==============================================================================

def scope_mux(selection) -> bool:
    """
    Scope Mux
    =========

    Checks selection is only Mux nodes.

    Args
    ----
        selection (list): Items selected in Flame.

    Returns
    -------
        is_mux_only (bool): True if the selection isn't empty and every selected item is a Mux node, otherwise False.
    """

    if not selection:
        return False

    return all(isinstance(item, flame.PyNode) and item.type.get_value() == 'MUX' for item in selection)

def scope_elbow(selection) -> bool:
    """
    Scope Elbow
    ===========

    Checks selection is only Elbow nodes.

    Args
    ----
        selection (list): Items selected in Flame.

    Returns
    -------
        is_elbow_only (bool): True if the selection isn't empty and every selected item is an Elbow node, otherwise False.
    """

    if not selection:
        return False

    return all(isinstance(item, flame.PyNode) and item.type.get_value() == 'Elbow' for item in selection)

# ==============================================================================
# [Entry Points]
# ==============================================================================

def elbow_to_frozen_mux(selection) -> None:

    MuxedElbows(selection, freeze=True)

# ==============================================================================
# [Flame Menus]
# ==============================================================================

def get_batch_custom_ui_actions():

    return [
        {
           'hierarchy': [],
           'actions': [
               {
                    'name': 'MUX -> Elbow',
                    'order': 1,
                    'execute': MuxedElbows,
                    'isVisible': scope_mux,
                    'minimumVersion': '2027.2'
               },
               {
                    'name': 'Elbow -> MUX',
                    'order': 2,
                    'execute': MuxedElbows,
                    'isVisible': scope_elbow,
                    'minimumVersion': '2027.2'
               },
               {
                    'name': 'Elbow -> Frozen MUX',
                    'order': 3,
                    'separator': 'below',
                    'execute': elbow_to_frozen_mux,
                    'isVisible': scope_elbow,
                    'minimumVersion': '2027.2'
               }
           ]
        }
    ]
