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

from typing import Tuple, List

from freexgraph import FreExGraph, FreExNode


class NodeForTest(FreExNode):
    def accept(self, visitor: "AbstractVisitor") -> bool:
        return visitor.testing_visit(self)


@pytest.fixture(scope="function")
def valid_basic_execution_graph():
    #
    #
    #     ,_____, id2
    #  id1         |
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

    execution_graph.add_node(id1, NodeForTest(name="id1"))
    execution_graph.add_node(id2, NodeForTest(name="id2", parents={id1}))
    execution_graph.add_node(id4, NodeForTest(name="id4", parents={id2}))
    execution_graph.add_node(id3, NodeForTest(name="id3", parents={id2, id4}))
    execution_graph.add_node(id5, NodeForTest(name="id5", parents={id4, id3}))
    yield execution_graph


def unordered_node_list_for_complex_graph() -> List[Tuple[str, FreExNode]]:
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
        NodeForTest("C", uid="C", parents={"A"}),
        NodeForTest("K", uid="K", parents={"G"}),
        NodeForTest("M", uid="M", parents={"K", "B"}),
        NodeForTest("D", uid="D", parents={"A"}),
        NodeForTest("J", uid="J", parents={"F"}),
        NodeForTest("A", uid="A"),
        NodeForTest("E", uid="E", parents={"B"}),
        NodeForTest("L", uid="L", parents={"J", "K"}),
        NodeForTest("H", uid="H", parents={"F"}),
        NodeForTest("F", uid="F", parents={"D", "E"}),
        NodeForTest("G", uid="G", parents={"E"}),
        NodeForTest("B", uid="B"),
        NodeForTest("I", uid="I", parents={"F"}),
    ]


@pytest.fixture(scope="function")
def node_list_complex_graph():
    yield unordered_node_list_for_complex_graph()


@pytest.fixture(scope="function")
def valid_complex_graph():
    execution_graph = FreExGraph()
    execution_graph.add_nodes(unordered_node_list_for_complex_graph())
    yield execution_graph
