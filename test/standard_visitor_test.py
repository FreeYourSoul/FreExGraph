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

from freexgraph import FreExGraph
from freexgraph.standard_visitor import (
    ValidateGraphIntegrity,
    FindFirstVisitor,
    FindAllVisitor,
)


def test_validation_visitor_simple(valid_basic_execution_graph):
    v = ValidateGraphIntegrity()
    v.visit(valid_basic_execution_graph.root)


def test_find_visitor(valid_basic_execution_graph):
    v = FindFirstVisitor(lambda node: node.id.startswith("id3"))
    v.visit(valid_basic_execution_graph.root)
    assert v.found()
    assert v.result.id.startswith("id3")
    assert len(v.result.parents) == 2
    # test re-use
    v.visit(valid_basic_execution_graph.root)
    assert v.found()
    assert v.result.id.startswith("id3")
    assert len(v.result.parents) == 2


def test_find_reverse_visitor(node_test_class):
    v = FindFirstVisitor(lambda node: node.id.startswith("id3"))
    v.is_reversed = True
    execution_graph = FreExGraph()

    #
    # id1---id2---id3---id4---id3bis
    #
    # Two starts by id3, the last one to be retrieved is id3bis
    #

    id1 = f"id1"
    id2 = f"id2"
    id3 = f"id3"
    id4 = f"id4"
    id5 = f"id3bis"

    execution_graph.add_node(node_test_class(id1))
    execution_graph.add_node(node_test_class(id2, parents={id1}))
    execution_graph.add_node(node_test_class(id4, parents={id2}))
    execution_graph.add_node(node_test_class(id3, parents={id4}))
    execution_graph.add_node(node_test_class(id5, parents={id3}))

    v.visit(execution_graph.root)
    assert v.found()
    assert v.result.id == "id3bis"
    # test re-use
    v.visit(execution_graph.root)
    assert v.found()
    assert v.result.id == "id3bis"


def test_count_visitor(valid_basic_execution_graph):
    v = FindAllVisitor(lambda node: node.id[0:3] > "id3")
    v.visit(valid_basic_execution_graph.root)
    assert v.count() == 2
    assert v.results[0].id.startswith("id4")
    assert v.results[1].id.startswith("id5")
    # test re-use
    v.visit(valid_basic_execution_graph.root)
    assert v.count() == 2
    assert v.results[0].id.startswith("id4")
    assert v.results[1].id.startswith("id5")


def test_find_all_visitor_depth_limit_0(valid_graph_with_subgraphs):
    v = FindAllVisitor(lambda node: node.id[0:2] == "T2", extension_depth_limit=0)
    v.visit(valid_graph_with_subgraphs.root)
    assert v.count() == 0


def test_find_all_visitor_depth_limit_1(valid_graph_with_subgraphs):
    v = FindAllVisitor(lambda node: node.id[0:2] == "T2", extension_depth_limit=1)
    v.visit(valid_graph_with_subgraphs.root)
    assert v.count() == 1


def test_find_all_visitor_depth_limit_2(valid_graph_with_subgraphs):
    v = FindAllVisitor(lambda node: node.id[0:2] == "T2", extension_depth_limit=2)
    v.visit(valid_graph_with_subgraphs.root)
    assert v.count() == 3
