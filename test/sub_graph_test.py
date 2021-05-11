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

from freexgraph import FreExGraph

# Graph used in theses tests are from valid_complex_graph fixture
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

    visitor_test.visit(sub_graph.root)

    assert len(visitor_test.visited) == 7
    sorted_visit = sorted(visitor_test.visited)

    assert sorted_visit[0] == "F"
    assert sorted_visit[1] == "H"
    assert sorted_visit[2] == "I"
    assert sorted_visit[3] == "J"
    assert sorted_visit[4] == "K"
    assert sorted_visit[5] == "L"
    assert sorted_visit[6] == "M"


def test_sub_graph_of_one_element(valid_complex_graph, visitor_test):
    sub_graph: FreExGraph = valid_complex_graph.sub_graph(
        from_node_id="E", to_nodes_id=["E"]
    )

    visitor_test.visit(sub_graph.root)

    assert len(visitor_test.visited) == 1
    assert visitor_test.visited[0] == "E"


def test_sub_graph_with_to_node(valid_complex_graph, visitor_test):
    # From A to K and J (L and M are not taken as K and J are stopping the subgraph)
    #
    #            A
    #         /     \
    #        C       D
    #                 \
    #                  F .______,
    #               /  |  \     \
    #             H    I   J     `K
    #
    sub_graph: FreExGraph = valid_complex_graph.sub_graph(
        from_node_id="A", to_nodes_id=["K", "J"]
    )

    visitor_test.visit(sub_graph.root)

    assert len(visitor_test.visited) == 8
    sorted_visit = sorted(visitor_test.visited)

    assert sorted_visit[0] == "A"
    assert sorted_visit[1] == "C"
    assert sorted_visit[2] == "D"
    assert sorted_visit[3] == "F"
    assert sorted_visit[4] == "H"
    assert sorted_visit[5] == "I"
    assert sorted_visit[6] == "J"
    assert sorted_visit[7] == "K"


def test_sub_graph_with_to_node_not_found(valid_complex_graph, visitor_test):
    # From F to A, A is not in the sub graph starting from F, so it's like no to_node where set
    #
    #                  F .______,
    #               /  |  \     \
    #             H    I   J     `,K.
    #                     /,_____/   \
    #                    L             M

    sub_graph: FreExGraph = valid_complex_graph.sub_graph(
        from_node_id="F", to_nodes_id="A"
    )

    visitor_test.visit(sub_graph.root)

    assert len(visitor_test.visited) == 7
    sorted_visit = sorted(visitor_test.visited)

    assert sorted_visit[0] == "F"
    assert sorted_visit[1] == "H"
    assert sorted_visit[2] == "I"
    assert sorted_visit[3] == "J"
    assert sorted_visit[4] == "K"
    assert sorted_visit[5] == "L"
    assert sorted_visit[6] == "M"


def test_sub_graph_error_on_from_node(valid_complex_graph):
    with pytest.raises(AssertionError) as e:
        valid_complex_graph.sub_graph(from_node_id="NOT_EXISTING")
        assert (
            "Error sub graph from node NOT_EXISTING, node has to be in the execution graph"
            == e
        )


def test_sub_graph_error_on_to_node(valid_complex_graph):
    with pytest.raises(AssertionError) as e:
        valid_complex_graph.sub_graph(from_node_id="F", to_nodes_id=["NOT_EXIST"])
        assert (
            "Error sub graph to node NOT_EXIST, node has to be in the execution graph"
            == e
        )

    with pytest.raises(AssertionError) as e:
        valid_complex_graph.sub_graph(
            from_node_id="F", to_nodes_id=["H", "M", "NOT_EXISTING"]
        )
        assert (
            "Error sub graph to node NOT_EXISTING, node has to be in the execution graph"
            == e
        )
