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

from typing import Optional

from freexgraph.standard_visitor import FindFirstVisitor
from freexgraph import GraphNode, FreExNode, FreExGraph


class NodeForTest(FreExNode):
    def accept(self, visitor) -> bool:
        return visitor.testing_visit(self)


def test_make_exec_graph():
    execution_graph = FreExGraph()
    id1 = f"id1_{uuid.uuid4()}"
    id2 = f"id2_{uuid.uuid4()}"
    id3 = f"id3_{uuid.uuid4()}"
    id3_bis = f"id3bis_{uuid.uuid4()}"
    id4 = f"id4_{uuid.uuid4()}"
    id5 = f"id5_{uuid.uuid4()}"

    execution_graph.add_node(FreExNode(id1)),
    execution_graph.add_node(FreExNode(id2, parents={id1})),
    execution_graph.add_node(FreExNode(id4, parents={id2})),
    execution_graph.add_node(FreExNode(id3, parents={id2, id4})),
    execution_graph.add_node(FreExNode(id3_bis, parents={id4})),
    execution_graph.add_node(FreExNode(id5, parents={id4, id3})),

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


def test_add_node_reserved_character():
    execution_graph = FreExGraph()
    id1 = f"id1::{uuid.uuid4()}"
    with pytest.raises(AssertionError):
        execution_graph.add_node(FreExNode(id1))
    id1 = f"id1:{uuid.uuid4()}"
    with pytest.raises(AssertionError):
        execution_graph.add_node(FreExNode(id1))


def test_get_not_existing(valid_basic_execution_graph):
    node: Optional[FreExNode] = valid_basic_execution_graph.get_node("NOT_EXISTING")
    assert node is None


def test_visitation(valid_basic_execution_graph, visitor_test, node_test_class):
    #
    #
    #     ,_____, id2
    #  id1         |
    #              |    ,----- id3
    #              |   /           \
    #              |  /             `___ id5
    #             id4 `--------------`
    #
    visitor_test.visit(valid_basic_execution_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 5
    assert visitor_test.visited[0].startswith("id1_")
    assert visitor_test.visited[1].startswith("id2_")
    assert visitor_test.visited[2].startswith("id4_")
    assert visitor_test.visited[3].startswith("id3_")
    assert visitor_test.visited[4].startswith("id5_")

    # check that modification of the node
    id5 = visitor_test.visited[4]
    node_5 = valid_basic_execution_graph.get_node(id5)
    assert node_5.metadata is None
    assert node_5.fork_id is None
    assert sorted(node_5.parents) == sorted(
        {visitor_test.visited[3], visitor_test.visited[2]}
    )

    valid_basic_execution_graph.replace_node(
        node_test_class(
            id5,
            metadata="ChocoboForTheWin",
            parents={"ThisIdWouldMessUpEverything"},
            graph_ref=None,
            fork_id="Chocobo",
        )
    )

    node_5 = valid_basic_execution_graph.get_node(id5)
    assert node_5.metadata == "ChocoboForTheWin"
    assert node_5.fork_id is None
    assert sorted(node_5.parents) == sorted(
        {visitor_test.visited[3], visitor_test.visited[2]}
    )


# used only in test_visitation_custom_hook and never somewhere else
test_visitation_custom_hook_count = [0, 0]


def test_visitation_custom_hook(visitor_test, node_test_class):
    execution_graph = FreExGraph()
    id1 = f"id1_{uuid.uuid4()}"
    id2 = f"id2_{uuid.uuid4()}"
    id3 = f"id3_{uuid.uuid4()}"
    id3_bis = f"id3bis_{uuid.uuid4()}"
    id4 = f"id4_{uuid.uuid4()}"
    id5 = f"id5_{uuid.uuid4()}"

    execution_graph.add_node(node_test_class(id1)),
    execution_graph.add_node(node_test_class(id2, parents={id1})),
    execution_graph.add_node(node_test_class(id4, parents={id2})),
    execution_graph.add_node(node_test_class(id3, parents={id2, id4})),
    execution_graph.add_node(node_test_class(id3_bis, parents={id4})),
    execution_graph.add_node(node_test_class(id5, parents={id4, id3})),

    def hook(_):
        global test_visitation_custom_hook_count
        test_visitation_custom_hook_count[0] += 1

    def hook_2(_):
        global test_visitation_custom_hook_count
        test_visitation_custom_hook_count[1] += 1

    visitor_test.register_custom_hook(
        predicate=lambda n: n.id.startswith("id3"), hook=hook
    )
    visitor_test.register_custom_hook(
        predicate=lambda n: not n.id.startswith("id3"),
        hook=hook_2,
    )
    visitor_test.visit(execution_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 6
    assert test_visitation_custom_hook_count[0] == 2
    assert test_visitation_custom_hook_count[1] == 4


def test_graph_node(valid_basic_execution_graph, visitor_test):
    #
    #                ida
    #                 |
    #                idb
    #              /  |
    #          idd    |
    #        /  |  \  |
    #      idc  |   GRAPH  ==> valid_basic_execution_graph
    #           |  /
    #          ide

    execution_graph = FreExGraph()
    ida = f"ida_{uuid.uuid4()}"
    idb = f"idb_{uuid.uuid4()}"
    idc = f"idc_{uuid.uuid4()}"
    id_graph = f"idg_{uuid.uuid4()}"
    idd = f"idd_{uuid.uuid4()}"
    ide = f"ide_{uuid.uuid4()}"

    execution_graph.add_node(NodeForTest(ida))
    execution_graph.add_node(NodeForTest(idb, parents={ida}))
    execution_graph.add_node(NodeForTest(idd, parents={idb}))
    execution_graph.add_node(
        GraphNode(id_graph, parents={idb, idd}, graph=valid_basic_execution_graph)
    )
    execution_graph.add_node(NodeForTest(idc, parents={idd}))
    execution_graph.add_node(NodeForTest(ide, parents={idd, id_graph}))

    visitor_test.visit(execution_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 10
    assert visitor_test.visited[0].startswith("ida_")
    assert execution_graph.get_node(ida).depth == 1
    assert visitor_test.visited[1].startswith("idb_")
    assert execution_graph.get_node(idb).depth == 2
    assert visitor_test.visited[2].startswith("idd_")
    assert execution_graph.get_node(idd).depth == 3

    assert visitor_test.visited[3].startswith("idc_")

    assert execution_graph.get_node(idc).depth == 4
    assert execution_graph.get_node(id_graph).depth == 4

    assert visitor_test.visited[4].startswith("id1_")
    assert visitor_test.visited[5].startswith("id2_")
    assert visitor_test.visited[6].startswith("id4_")
    assert visitor_test.visited[7].startswith("id3_")
    assert visitor_test.visited[8].startswith("id5_")

    assert visitor_test.visited[9].startswith("ide_")
    assert execution_graph.get_node(ide).depth == 5

    assert len(visitor_test.inner_graph_started) == 1
    assert visitor_test.inner_graph_started[0].startswith(id_graph)
    assert visitor_test.inner_graph_started == visitor_test.inner_graph_ended

    # test find in graph node from root
    finder = FindFirstVisitor(lambda n: n.id.startswith("id3"))
    finder.visit(execution_graph.root)
    assert finder.found()
    assert finder.result.id.startswith("id3")


def test_add_nodes(node_list_complex_graph, visitor_test):
    execution_graph = FreExGraph()
    execution_graph.add_nodes(node_list_complex_graph)

    visitor_test.visit(execution_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 13


def test_add_nodes_not_properly_connected_nodes(node_list_complex_graph):
    node_list_complex_graph.append(NodeForTest("X", parents={"NOT_EXISTING"}))
    execution_graph = FreExGraph()
    with pytest.raises(AssertionError):
        execution_graph.add_nodes(node_list_complex_graph)


def test_add_nodes_multiple_nodes_same_id(node_list_complex_graph):
    # K is already in graph
    assert "K" in [n.id for n in node_list_complex_graph]

    # adding another K fail
    node_list_complex_graph.append(NodeForTest("K"))
    execution_graph = FreExGraph()
    with pytest.raises(AssertionError):
        execution_graph.add_nodes(node_list_complex_graph)


def test_add_nodes_on_already_created_graph(valid_complex_graph, visitor_test):
    to_add = [
        NodeForTest("N", parents={"A", "K"}),
        NodeForTest("O", parents={"B", "I", "J"}),
        NodeForTest("P", parents={"N", "C"}),
    ]

    valid_complex_graph.add_nodes(to_add)

    visitor_test.visit(valid_complex_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 16


def test_add_not_linked_nodes_on_already_created_graph(valid_complex_graph):
    to_add = [
        NodeForTest("X", parents={"A", "NOT_EXISTING"}),
    ]
    with pytest.raises(AssertionError):
        valid_complex_graph.add_nodes(to_add)


def test_delete_one_node(visitor_test):
    #
    #                ida
    #                 |
    #                idb
    #              /  |
    #          idd    |
    #        /  |  \  |
    #      idc  |    idx
    #           |  /
    #          ide

    execution_graph = FreExGraph()
    ida = f"ida_{uuid.uuid4()}"
    idb = f"idb_{uuid.uuid4()}"
    idc = f"idc_{uuid.uuid4()}"
    idx = f"idx_{uuid.uuid4()}"
    idd = f"idd_{uuid.uuid4()}"
    ide = f"ide_{uuid.uuid4()}"

    execution_graph.add_node(NodeForTest(ida))
    execution_graph.add_node(NodeForTest(idb, parents={ida}))
    execution_graph.add_node(NodeForTest(idd, parents={idb}))
    execution_graph.add_node(NodeForTest(idx, parents={idb, idd}))
    execution_graph.add_node(NodeForTest(idc, parents={idd}))
    execution_graph.add_node(NodeForTest(ide, parents={idd, idx}))

    visitor_test.visit(execution_graph.root)

    assert len(visitor_test.visited) == 6

    assert ide in visitor_test.visited

    # should only remove ide
    execution_graph.remove_node(ide)

    visitor_test.visit(execution_graph.root)

    assert len(visitor_test.visited) == 5

    assert ide not in visitor_test.visited

    assert ida == visitor_test.visited[0]
    assert idb == visitor_test.visited[1]
    assert idd == visitor_test.visited[2]
    assert idc == visitor_test.visited[3]
    assert idx == visitor_test.visited[4]


def test_delete_node_with_childs(visitor_test):
    #
    #                ida
    #                 |
    #                idb
    #              /  |
    #          idd    |
    #        /  |  \  |
    #      idc  |    idx
    #           |  /
    #          ide

    execution_graph = FreExGraph()
    ida = f"ida_{uuid.uuid4()}"
    idb = f"idb_{uuid.uuid4()}"
    idc = f"idc_{uuid.uuid4()}"
    idx = f"idx_{uuid.uuid4()}"
    idd = f"idd_{uuid.uuid4()}"
    ide = f"ide_{uuid.uuid4()}"

    execution_graph.add_node(NodeForTest(ida))
    execution_graph.add_node(NodeForTest(idb, parents={ida}))
    execution_graph.add_node(NodeForTest(idd, parents={idb}))
    execution_graph.add_node(NodeForTest(idx, parents={idb, idd}))
    execution_graph.add_node(NodeForTest(idc, parents={idd}))
    execution_graph.add_node(NodeForTest(ide, parents={idd, idx}))

    # should remove idc, ide and idx
    execution_graph.remove_node(idd)

    visitor_test.visit(execution_graph.root)

    assert len(visitor_test.visited) == 2

    assert ide not in visitor_test.visited

    assert ida == visitor_test.visited[0]
    assert idb == visitor_test.visited[1]


def test_predecessors_successors(valid_basic_execution_graph):
    v = FindFirstVisitor(lambda node: node.id.startswith("id3"))
    v.visit(valid_basic_execution_graph.root)

    assert v.found()
    assert v.result.id.startswith("id3")
    assert len(v.result.parents) == 2

    node_predecessors = v.result.get_predecessors()
    node_predecessors.sort(key=lambda n: n.id)
    assert len(node_predecessors) == 2
    assert node_predecessors[0].id.startswith("id2")
    assert node_predecessors[1].id.startswith("id4")

    node_predecessors = v.result.get_successors()
    assert len(node_predecessors) == 1
    assert node_predecessors[0].id.startswith("id5")


def test_middle_visitation_start(valid_complex_graph):
    v = FindFirstVisitor(lambda node: node.id == "F")
    v.visit(valid_complex_graph.root)

    f_node = v.result
    assert v.found()
    assert f_node.id == "F"

    # G and F are at the same level and thus are always executed on partial visitation
    find_g = FindFirstVisitor(lambda node: node.id == "G")

    # start visitation from F node [A, B, C, D, E] should not be visited
    v = FindFirstVisitor(lambda node: node.id in ["A", "B", "C", "D", "E"])
    v.visit(f_node)
    assert not v.found()
    find_g.visit(f_node)
    assert find_g.found()

    # start reverse visitation node [H, I, J, K, L, M] should not be visited
    v = FindFirstVisitor(lambda node: node.id in ["H", "I", "J", "K", "L", "M"])
    v.is_reversed = True
    v.visit(f_node)
    assert not v.found()
    find_g.visit(f_node)
    assert find_g.found()
