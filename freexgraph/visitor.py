# MIT License
#
# Copyright (c) 2021 Quentin Balland
# Project : https://github.com/FreeYourSoul/FreExGraph
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import networkx as nx

from contextlib import contextmanager
from typing import List, Tuple, Any, Callable

from tqdm import tqdm

from freexgraph.freexgraph import FreExNode, GraphNode


@contextmanager
def no_progress(**_):
    class NoProg:
        def update(self, _=None):
            pass

        def set_description(self, _=None):
            pass

        def set_postfix(self, _=None):
            pass

    yield NoProg()


def _is_node_ignored(node: Any) -> bool:
    return False


def _get_len(
    sorted_node_list: List[Tuple], ref_graph: nx.DiGraph, with_progress_bar: bool
) -> int:
    if not with_progress_bar:
        return 0
    return len(
        [
            n
            for n in sorted_node_list
            if not _is_node_ignored(ref_graph.nodes[n]["content"])
        ]
    )


class AbstractVisitor:
    """Base class for Visitor.

    Any custom (or standard visitor) has to be inheriting from this class. It should NOT override the visit method !

    side_notes:
        The different nodes implementation will override their accept method and redirect to a proper method of the
        visitor. You can implement any method (of any name) that will be called by your custom nodes.

        By convention, the names called by node.accept should match this regex `visit_*`.
        but it is not enforced in any way
    """

    with_progress_bar: bool
    is_reversed: bool

    # List of Predicate/Hook
    __custom_hooks: List[Tuple[Callable, Callable]]

    def __init__(self, *, with_progress_bar: bool = False, is_reversed: bool = False):
        """Base class instantiation

        :param with_progress_bar: have a terminal tqdm progression bar while traversing the graph
        :param is_reversed: traverse the graph in a reverse topological order
        """
        self.with_progress_bar = with_progress_bar
        self.is_reversed = is_reversed
        self.__custom_hooks = []

    def visit(self, root: FreExNode) -> bool:
        self.hook_start()
        not_interrupted = self.apply_visitation_(root)
        if not_interrupted:
            self.hook_end()
        return not_interrupted

    def apply_visitation_(self, root: FreExNode) -> bool:
        """do not override / directly use. Internal visitation method, use visit(root) instead"""

        ctx_prog = tqdm if self.with_progress_bar else no_progress
        sorted_node_list = list(nx.lexicographical_topological_sort(root.graph_ref))

        if self.is_reversed:
            sorted_node_list = list(reversed(sorted_node_list))

        with ctx_prog(
            total=_get_len(sorted_node_list, root.graph_ref, self.with_progress_bar)
        ) as pbar:
            pbar.set_description(f"Processing Visitor {type(self).__name__}")
            for node_id in sorted_node_list:
                node = root.graph_ref.nodes[node_id]["content"]

                # Trigger custom hook
                # for predicate, hook in self.__custom_hooks:
                #     if predicate(node):
                #         hook(node)

                if not node.apply_accept_(self):
                    return False
                pbar.set_postfix({"node": node_id})
                pbar.update()
        return True

    def hook_start_graph_node(self, gn: GraphNode):
        """Hook to implement in order to do an action at the start of a graph node

        :param gn: graph node started
        """
        pass

    def hook_end_graph_node(self, gn: GraphNode):
        """Hook to implement in order to do an action at the start of a graph node

        :param gn: graph node that finished
        """
        pass

    def hook_start(self):
        """Hook to implement in order to do an action at the start of the visitation"""
        pass

    def hook_end(self):
        """Hook to implement in order to do an action at the end of the visitation"""
        pass

    def hook_fork_started(self, n: FreExNode, fork_id: str):
        """Hook to implement in order to do an action when a new fork start to be visited"""
        pass

    def register_custom_hook(self, predicate: Callable, hook: Callable):
        """Register a custom hook

        Provided predicate is applied on each node, if it return true, provided hook is executed (with node given as
        parameter)

        :param predicate: check node against to trigger hook
        :param hook: Callable to trigger in case the predicate is returning True for a visited node
        """
        self.__custom_hooks.append((predicate, hook))


class VisitorComposer:
    """Class to compose visitor together"""

    _sequential_before: List[AbstractVisitor]
    _action_composed: List[AbstractVisitor]
    _sequential_after: List[AbstractVisitor]
    _is_reversed: bool
    _with_progress_bar: bool

    def __init__(
        self,
        actions: List[AbstractVisitor],
        *,
        before: List[AbstractVisitor],
        after: List[AbstractVisitor],
        progress_bar_on_actions: bool = False,
    ):
        """

        :param actions:
        :param before:
        :param after:
        :param progress_bar_on_actions:
        """
        assert len(actions) > 1, "Composition of not at least 2 visitors is useless"
        reversed_action: List[bool] = [rev.is_reversed for rev in actions]
        assert all(reversed_action) or not any(
            reversed_action
        ), "Cannot compose reversed and non reversed Visitor together"

        self._is_reversed = reversed_action[0]
        self._with_progress_bar = progress_bar_on_actions
        self._action_composed = actions
        self._sequential_before = before
        self._sequential_after = after

    def visit(self, root: FreExNode) -> bool:
        to_continue = True
        for b in self._sequential_before:
            to_continue &= b.visit(root)
            if not to_continue:
                return False

        if not self._composed_visit(root):
            return False

        for b in self._sequential_after:
            to_continue &= b.visit(root)
            if not to_continue:
                return False

        return to_continue

    def _composed_visit(self, root: FreExNode) -> bool:
        ctx_prog = tqdm if self._with_progress_bar else no_progress
        sorted_node_list = list(nx.lexicographical_topological_sort(root.graph_ref))

        if self._is_reversed:
            sorted_node_list = list(reversed(sorted_node_list))

        with ctx_prog(
            total=_get_len(sorted_node_list, root.graph_ref, self._with_progress_bar)
        ) as pbar:
            pbar.set_description("Processing Composed Visitor")

            for node_id in sorted_node_list:
                # do the visitation for the node on each action visitor
                for action_visitor in self._action_composed:
                    if not root.graph_ref.nodes[node_id].apply_accept_(action_visitor):
                        return False

                pbar.set_postfix({"node": node_id})
                pbar.update()

        return True
