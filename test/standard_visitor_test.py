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


def test_count_visitor(valid_basic_execution_graph):
    v = FindAllVisitor(lambda node: node.id[0:3] > "id3")
    v.visit(valid_basic_execution_graph.root)
    assert v.count() == 2
    assert v.results[0].id.startswith("id4")
    assert v.results[1].id.startswith("id5")
    # test re-use
    v = FindAllVisitor(lambda node: node.id[0:3] > "id3")
    v.visit(valid_basic_execution_graph.root)
    assert v.count() == 2
    assert v.results[0].id.startswith("id4")
    assert v.results[1].id.startswith("id5")

