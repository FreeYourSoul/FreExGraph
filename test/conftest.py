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

import pytest
import uuid

from typing import List

from freexgraph import FreExGraph, FreExNode, AnyVisitor, AbstractVisitor
from freexgraph.freexgraph import GraphNode


class VisitationForTesting(AbstractVisitor):
    visited: List[str]
    inner_graph_started: List[str]
    inner_graph_ended: List[str]

    start: bool = False
    end: bool = False

    def __init__(self):
        super().__init__(with_progress_bar=True)
        self.visited = []
        self.inner_graph_started = []
        self.inner_graph_ended = []

    def testing_visit(self, node: FreExNode):
        self.visited.append(node.id)
        return True

    def hook_start(self):
        self.visited = []
        self.inner_graph_started = []
        self.inner_graph_ended = []
        self.start = True
        self.end = False

    def hook_end(self):
        self.end = True

    def hook_start_graph_node(self, gn: GraphNode):
        assert self.start, "Bug, start_hook not called?"
        assert not self.end, "Bug, end_hook cannot be called before the end Duh"
        self.inner_graph_started.append(gn.id)

    def hook_end_graph_node(self, gn: GraphNode):
        assert self.start, "Bug, start_hook not called?"
        assert not self.end, "Bug, end_hook cannot be called before the end Duh"
        self.inner_graph_ended.append(gn.id)


@pytest.fixture(scope="function")
def visitor_test():
    return VisitationForTesting()


class NodeForTest(FreExNode):
    def accept(self, visitor: AnyVisitor) -> bool:
        return visitor.testing_visit(self)


@pytest.fixture(scope="session")
def node_test_class():
    return NodeForTest


@pytest.fixture(scope="function")
def valid_basic_execution_graph():
    #
    #
    #     ,_____, id2,______
    #  id1         |         \
    #              |    ,----- id3
    #              |   /           \
    #              |  /             `___ id5
    #             id4 `--------------`
    #

    execution_graph = FreExGraph()
    id1 = f"id1_{uuid.uuid4()}"
    id2 = f"id2_{uuid.uuid4()}"
    id3 = f"id3_{uuid.uuid4()}"
    id4 = f"id4_{uuid.uuid4()}"
    id5 = f"id5_{uuid.uuid4()}"

    execution_graph.add_node(NodeForTest(id1))
    execution_graph.add_node(NodeForTest(id2, parents={id1}))
    execution_graph.add_node(NodeForTest(id4, parents={id2}))
    execution_graph.add_node(NodeForTest(id3, parents={id2, id4}))
    execution_graph.add_node(NodeForTest(id5, parents={id4, id3}))
    yield execution_graph


def unordered_node_list_for_complex_graph() -> List[NodeForTest]:
    #
    #            A                      B
    #         /     \                 /  |
    #        C       D              E    |
    #                 \              \   |
    #                  F .______,    G   |
    #               /  |  \     \   /    |
    #             H    I   J     `,K.    |
    #                     /,_____/   \   |
    #                    L             M
    #
    return [
        NodeForTest("C", parents={"A"}),
        NodeForTest("K", parents={"G", "F"}),
        NodeForTest("M", parents={"K", "B"}),
        NodeForTest("D", parents={"A"}),
        NodeForTest("J", parents={"F"}),
        NodeForTest("A"),
        NodeForTest("E", parents={"B"}),
        NodeForTest("L", parents={"J", "K"}),
        NodeForTest("H", parents={"F"}),
        NodeForTest("F", parents={"D", "E"}),
        NodeForTest("G", parents={"E"}),
        NodeForTest("B"),
        NodeForTest("I", parents={"F"}),
    ]


@pytest.fixture(scope="function")
def node_list_complex_graph():
    yield unordered_node_list_for_complex_graph()


@pytest.fixture(scope="function")
def valid_complex_graph():
    execution_graph = FreExGraph()
    execution_graph.add_nodes(unordered_node_list_for_complex_graph())
    yield execution_graph
