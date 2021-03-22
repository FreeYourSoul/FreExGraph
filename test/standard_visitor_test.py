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

from freexgraph.standard_visitor import ValidateGraphIntegrity, FindFirstVisitor, FindAllVisitor


def test_validation_visitor_simple(valid_basic_execution_graph):
    class ValidationTestingVisitor(ValidateGraphIntegrity):
        def testing_visit(self, _):
            ...

    v = ValidationTestingVisitor()
    v.visit(valid_basic_execution_graph.root())


def test_find_visitor(valid_basic_execution_graph):
    class FindTestingVisitor(FindFirstVisitor):
        iteration_count: int = 0

        def testing_visit(self, _):
            self.iteration_count += 1

    v = FindTestingVisitor(lambda node: node.name.startswith("id3"))
    v.visit(valid_basic_execution_graph.root())
    assert v.found()
    assert v.result.name == "id3"
    assert len(v.result.parents) == 2
    # check that all the visitation has not been done as it found in the middle
    # but full size of the graph is 5
    assert v.iteration_count == 4


def test_count_visitor(valid_basic_execution_graph):
    class CountTestingVisitor(FindAllVisitor):
        def testing_visit(self, _):
            ...

    v = CountTestingVisitor(lambda node: node.name[0:3] > "id3")
    v.visit(valid_basic_execution_graph.root())
    assert v.count() == 2
    assert v.results[0].name == "id4"
    assert v.results[1].name == "id5"
