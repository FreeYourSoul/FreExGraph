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
import uuid
from typing import List

import pytest

from freexgraph import AbstractVisitor, FreExNode, FreExGraph


class VisitationForTesting(AbstractVisitor):

    visited: List[str] = []

    def __init__(self):
        super().__init__(with_progress_bar=True)

    def testing_visit(self, node: FreExNode):
        self.visited.append(node.id)


def test_make_exec_graph():
    execution_graph = FreExGraph()
    id1 = f"id1_{uuid.uuid4()}"
    id2 = f"id2_{uuid.uuid4()}"
    id3 = f"id3_{uuid.uuid4()}"
    id3_bis = f"id3bis_{uuid.uuid4()}"
    id4 = f"id4_{uuid.uuid4()}"
    id5 = f"id5_{uuid.uuid4()}"

    execution_graph.add_node(id1, FreExNode(name="id1"))
    execution_graph.add_node(id2, FreExNode(name="id2", parents={id1}))
    execution_graph.add_node(id4, FreExNode(name="id4", parents={id2}))
    execution_graph.add_node(id3, FreExNode(name="id3", parents={id2, id4}))
    execution_graph.add_node(id3_bis, FreExNode(name="id3_bis", parents={id4}))
    execution_graph.add_node(id5, FreExNode(name="id5", parents={id4, id3}))

    assert execution_graph._graph.has_node(id1)
    assert execution_graph.get_node(id1).depth == 1

    assert execution_graph._graph.has_node(id2)
    assert execution_graph.get_node(id2).depth == 2

    assert execution_graph._graph.has_node(id3)
    assert execution_graph.get_node(id3).depth == 4

    assert execution_graph._graph.has_node(id3_bis)
    assert execution_graph.get_node(id3_bis).depth == 4

    assert execution_graph._graph.has_node(id4)
    assert execution_graph.get_node(id4).depth == 3

    assert execution_graph._graph.has_node(id5)
    assert execution_graph.get_node(id5).depth == 5


def test_visitation(valid_basic_execution_graph):
    #
    #
    #     ,_____, id2
    #  id1         |
    #              |    ,----- id3
    #              |   /           \
    #              |  /             `___ id5
    #             id4 `--------------`
    #
    v = VisitationForTesting()
    v.visit(valid_basic_execution_graph.root())

    assert len(v.visited) == 5
    assert v.visited[0].startswith("id1_")
    assert v.visited[1].startswith("id2_")
    assert v.visited[2].startswith("id4_")
    assert v.visited[3].startswith("id3_")
    assert v.visited[4].startswith("id5_")
