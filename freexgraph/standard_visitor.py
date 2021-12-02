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

import networkx as nx

from typing import Callable, Optional, List

from networkx import NetworkXNoCycle

from freexgraph import AbstractVisitor, FreExNode
from freexgraph.freexgraph import root_node


class StandardVisitor:

    _current_extension_depth: int = 0

    # extension depth to be executed on standard visitors (only standards visitor)
    _extension_depth_limit: Optional[int] = None

    def visit_standard(self, node: FreExNode) -> bool:
        raise NotImplementedError(
            "visit_standard is not implemented for this standard visitor"
        )

    def extension_depth_threshold(self) -> bool:
        """:return: True if the visitor can apply an extension, False if the threshold of depth set is too high"""
        return (
            self._extension_depth_limit is None
            or self._extension_depth_limit > self._current_extension_depth
        )

    @contextmanager
    def inc_extension_depth(self):
        """Internal usage only: increment and decrement the extension depth for the time of the context"""
        if self._extension_depth_limit is None:
            yield
        else:
            self._current_extension_depth += 1
            yield
            self._current_extension_depth -= 1


class FindFirstVisitor(AbstractVisitor, StandardVisitor):
    """Find the first occurrence of a node that follow the given predicate

    result value is set to a reference to the value found.
    This is a mutable visitor : If a modification is to be done on the found node, it can be done in the predicate
    """

    result: Optional[FreExNode] = None
    """reference to the node found after visitation that follow the predicate, stay None if none found """

    _predicate: Callable

    def __init__(
        self, predicate: Callable, extension_depth_limit: Optional[int] = None, **kwargs
    ):
        """
        :param predicate: has to take an argument (FreExNode type) and return a bool, will determine what result is
         returned from the graph
        :param extension_depth_limit: optional limitation of extension depth for the visitation, if 0, only the current
         graph is executed
        """
        super().__init__(**kwargs)
        self._predicate = predicate
        self._extension_depth_limit = extension_depth_limit

    def visit_standard(self, node: FreExNode) -> bool:
        if node.id != root_node and self._predicate(node):
            self.result = node
            # result found, stop visitation
            return False
        return True

    def hook_start(self):
        self.result = None

    def found(self) -> bool:
        return self.result is not None


class FindAllVisitor(AbstractVisitor, StandardVisitor):
    results: List[FreExNode]
    """reference list of nodes found after visitation that follow the predicate, stay None if none found """

    _predicate: Callable

    def __init__(
        self, predicate: Callable, extension_depth_limit: Optional[int] = None, **kwargs
    ):
        """
        :param predicate: has to take an argument (FreExNode type) and return a bool, will determine what results are
         returned from the graph
        :param extension_depth_limit: optional limitation of extension depth for the visitation, if 0, only the current
         graph is executed
        """
        super().__init__(**kwargs)
        self.results = []
        self._predicate = predicate
        self._extension_depth_limit = extension_depth_limit

    def visit_standard(self, node: FreExNode) -> bool:
        if node.id != root_node and self._predicate(node):
            self.results.append(node)
        return True

    def hook_start(self):
        self.results = []

    def count(self) -> int:
        return len(self.results)


class LenCalculatorVisitor(AbstractVisitor, StandardVisitor):
    result: int
    """calculate the length of the graph"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.result = 0

    def visit_standard(self, node: FreExNode) -> bool:
        if node.id != root_node:
            self.result += 1
        return True

    def hook_start(self):
        self.result = 0


class ValidateGraphIntegrity(AbstractVisitor, StandardVisitor):
    """Validate the integrity of the graph.

    All the data are added if the API is used correctly, but if any bypass has been used (which you should never do)
    This visitor will help figuring out what is the error.

    * Check that each and every parents exists in the graph
    * Check all node has a graph_ref assigned
    * Check all node has an id set
    * Check all node has a valid depth
    * Check that the graph doesn't do a cycle (cyclic graph) Impossible by design, parent are checked at node add
    """

    _first_check = True
    """Checks that require to be done only once are not done for each node visit"""

    def visit_standard(self, node: FreExNode) -> bool:
        if self._first_check:
            try:
                # impossible by design ( as we check if parents exists before adding them )
                assert (
                    len(list(nx.find_cycle(node.graph_ref))) == 0
                ), "Error on graph : Cycle found"
            except NetworkXNoCycle:
                pass
            self._first_check = False

        assert isinstance(
            node, FreExNode
        ), f"Error on node type {type(node).__name__}. Every node in the graph should be deriving from FreExNode"

        assert node.id, f"Error on node {node}, doesn't contains id"
        assert (
            node.id == root_node or len(node.parents) > 0
        ), f"Internal library error: {node}, doesn't have parent (root should at least be added)"

        assert (
            node.graph_ref is not None
        ), f"Error on node {node}, doesn't contains a ref_graph"
        assert (
            node.depth >= 0
        ), f"Internal library error: {node}, impossible depth (should be positive)"

        for p in node.parents:
            assert node.graph_ref.has_node(
                p
            ), f"Error on node {node}, parent {p} doesn't exist in the graph"

        return True
