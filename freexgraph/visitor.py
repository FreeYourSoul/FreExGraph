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

from contextlib import contextmanager
from typing import List, Tuple, Any

import networkx as nx
from tqdm import tqdm

from freexgraph.freexgraph import FreExNode, BundleDependencyNode


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
    return isinstance(node, BundleDependencyNode)


def _get_len(sorted_node_list: List[Tuple], ref_graph: nx.DiGraph, with_progress_bar: bool) -> int:
    if not with_progress_bar:
        return 0
    return len(
        [n for n in sorted_node_list if not _is_node_ignored(ref_graph.nodes[n]["content"])])


class AbstractVisitor:
    """

    """
    with_progress_bar: bool
    is_reversed: bool

    def __init__(self, *, with_progress_bar: bool = False, is_reversed: bool = False):
        """
        :param with_progress_bar: have a terminal tqdm progression bar while traversing the graph
        :param is_reversed: traverse the graph in a reverse topological order
        """
        self.with_progress_bar = with_progress_bar
        self.is_reversed = is_reversed

    def visit(self, root: FreExNode) -> bool:
        ctx_prog = tqdm if self.with_progress_bar else no_progress
        sorted_node_list = list(nx.lexicographical_topological_sort(root.graph_ref))

        if self.is_reversed:
            sorted_node_list = list(reversed(sorted_node_list))

        with ctx_prog(total=_get_len(sorted_node_list, root.graph_ref, self.with_progress_bar)) as pbar:
            pbar.set_description(f"Processing Visitor {type(self).__name__}")

            for node_id in sorted_node_list:
                if not root.graph_ref.nodes[node_id]["content"].accept(self):
                    return False
                pbar.set_postfix({'node': node_id})
                pbar.update()

        return True


class VisitorComposer:
    """ Class to compose visitor together

    """
    _sequential_before: List[AbstractVisitor]
    _action_composed: List[AbstractVisitor]
    _sequential_after: List[AbstractVisitor]
    _is_reversed: bool
    _with_progress_bar: bool

    def __init__(self, actions: List[AbstractVisitor], *, before: List[AbstractVisitor], after: List[AbstractVisitor],
                 progress_bar_on_actions: bool = False):
        """

        :param actions:
        :param before:
        :param after:
        :param progress_bar_on_actions:
        """
        assert len(actions) > 1, "Composition of not at least 2 visitors is useless"
        reversed_action: List[bool] = [rev.is_reversed for rev in actions]
        assert all(reversed_action) or not any(
            reversed_action), "Cannot compose reversed and non reversed Visitor together"

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

        with ctx_prog(total=_get_len(sorted_node_list, root.graph_ref, self._with_progress_bar)) as pbar:
            pbar.set_description(f"Processing Composed Visitor")

            for node_id in sorted_node_list:
                # do the visitation for the node on each action visitor
                for action_visitor in self._action_composed:
                    if not root.graph_ref.nodes[node_id].accept(action_visitor):
                        return False

                pbar.set_postfix({'node': node_id})
                pbar.update()

        return True
