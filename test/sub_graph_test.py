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

from freexgraph import GraphNode, FreExNode, FreExGraph

# Graph used in thoses tests are from valid_complex_graph fixture
#
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


def test_sub_graph_without_to_node(valid_complex_graph, visitor_test):
    # From F to end
    #
    #                  F .______,
    #               /  |  \     \
    #             H    I   J     `,K.
    #                     /,_____/   \
    #                    L             M

    sub_graph: FreExGraph = valid_complex_graph.sub_graph(from_node_id="F")

    visitor_test.visit(valid_complex_graph)
    visitor_test.visit(sub_graph.root)
    assert len(visitor_test.visited) == 7


def test_sub_graph_of_one_element(valid_complex_graph):
    ...


def test_sub_graph_with_to_node_not_found(valid_complex_graph):
    ...


def test_sub_graph_with_to_node(valid_complex_graph):
    ...


def test_sub_graph_with_to_node_partial(valid_complex_graph):
    ...


def test_sub_graph_error_on_from_node(valid_complex_graph):
    ...


def test_sub_graph_error_on_to_node(valid_complex_graph):
    ...
