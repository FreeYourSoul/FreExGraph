import pytest

from freexgraph import FreExGraph
from freexgraph.standard_visitor import FindFirstVisitor, FindAllVisitor

id0 = f"id0"
id1 = f"id1"
id2 = f"id2"
id3 = f"id3"
id4 = f"id4"
id5 = f"id5"
id6 = f"id6"
id_join = f"id_join"
id7 = f"id7"
id8 = f"id8"


def make_fork_graph(node_test_class: type):
    #            id0
    #             |
    #       .___ id1 ___.           < ==== fork
    #      /      |      \
    #     id2    id3     id4
    #     |     /   \      |
    #     |   id5   id6    |
    #     \     \   /     /
    #      `-- id_join --'          <===== join
    #          /     \
    #         id7    id8
    #

    execution_graph = FreExGraph()
    execution_graph.add_node(node_test_class(id0))
    execution_graph.add_node(node_test_class(id1, parents={id0}))
    execution_graph.add_node(node_test_class(id2, parents={id1}))
    execution_graph.add_node(node_test_class(id3, parents={id1}))
    execution_graph.add_node(node_test_class(id4, parents={id1}))
    execution_graph.add_node(node_test_class(id5, parents={id3}))
    execution_graph.add_node(node_test_class(id6, parents={id3}))
    execution_graph.add_node(node_test_class(id_join, parents={id2, id5, id6, id4}))
    execution_graph.add_node(node_test_class(id7, parents={id_join}))
    execution_graph.add_node(node_test_class(id8, parents={id_join}))
    return execution_graph


def test_simple_fork(valid_basic_execution_graph, node_test_class, visitor_test):
    #
    #          id1
    #           |
    #         ,id2 .__.__,
    #       /   |   \     \
    #      |   id4   |    id4::fork_1
    #      | /  |     \    /       |
    #      id3  |     id3::fork_1  |
    #        \  |          \       |
    #          id5        id5::fork_1
    #

    find = FindFirstVisitor(lambda k: k.id.startswith("id4"))
    find.visit(valid_basic_execution_graph.root)
    uid4 = find.result.id

    valid_basic_execution_graph.fork_from_node(
        node_test_class(uid=uid4, fork_id="fork_1")
    )
    visitor_test.visit(valid_basic_execution_graph.root)

    assert visitor_test.end
    assert len(visitor_test.visited) == 8

    find_all = FindAllVisitor(lambda k: k.id.startswith("id4"))
    find_all.visit(valid_basic_execution_graph.root)
    all_4 = find_all.results
    all_4.sort(key=lambda k: k.id)
    assert len(all_4) == 2
    assert "::fork_1" not in all_4[0].id
    assert all_4[0].fork_id is None
    assert "::fork_1" in all_4[1].id
    assert all_4[1].fork_id == "fork_1"
    fork_4_parents = list(all_4[1].parents)
    assert len(fork_4_parents) == 1
    assert fork_4_parents[0].startswith("id2")

    find_all = FindAllVisitor(lambda k: k.id.startswith("id3"))
    find_all.visit(valid_basic_execution_graph.root)
    all_3 = find_all.results
    all_3.sort(key=lambda k: k.id)
    assert len(all_3) == 2
    assert "::fork_1" not in all_3[0].id
    assert all_3[0].fork_id is None
    assert "::fork_1" in all_3[1].id
    assert all_3[1].fork_id == "fork_1"
    fork_3_parents = list(all_3[1].parents)
    fork_3_parents.sort()
    assert len(fork_3_parents) == 2
    assert fork_3_parents[0].startswith("id2")
    assert fork_3_parents[1].startswith("id4")
    assert "::fork_1" in fork_3_parents[1]

    find_all = FindAllVisitor(lambda k: k.id.startswith("id5"))
    find_all.visit(valid_basic_execution_graph.root)
    all_5 = find_all.results
    all_5.sort(key=lambda k: k.id)
    assert len(all_5) == 2
    assert "::fork_1" not in all_5[0].id
    assert all_5[0].fork_id is None
    assert "::fork_1" in all_5[1].id
    assert all_5[1].fork_id == "fork_1"


def test_fork_with_join(node_test_class, visitor_test):

    execution_graph = make_fork_graph(node_test_class)

    visitor_test.visit(execution_graph.root)
    assert len(visitor_test.visited) == 10

    execution_graph.fork_from_node(
        node_test_class(id1, fork_id="chocobo"), join_id=id_join
    )
    visitor_test.visit(execution_graph.root)
    assert len(visitor_test.visited) == 16


def test_fork_with_join_unlinked_with_join(node_test_class, visitor_test):

    id_9 = "id_9"

    execution_graph = make_fork_graph(node_test_class)

    # id 9 making a jump from in the fork (id6 being in the fork) to outside (id8 being after the join_node)
    execution_graph.add_node(node_test_class(id_9, parents={id6, id8}))

    visitor_test.visit(execution_graph.root)
    assert len(visitor_test.visited) == 11

    with pytest.raises(AssertionError) as e:
        execution_graph.fork_from_node(
            node_test_class(id1, fork_id="chocobo"), join_id=id_join
        )
        assert "reached (doesn't link with the join node)" in e


def test_fork_with_join_unlinked_with_join_2(node_test_class, visitor_test):

    id_9 = "id_9"

    execution_graph = make_fork_graph(node_test_class)

    # id 9 not linked with join_node
    execution_graph.add_node(node_test_class(id_9, parents={id6}))

    visitor_test.visit(execution_graph.root)
    assert len(visitor_test.visited) == 11

    with pytest.raises(AssertionError) as e:
        execution_graph.fork_from_node(
            node_test_class(id1, fork_id="chocobo"), join_id=id_join
        )
        assert "reached (doesn't link with the join node)" in e


def test_fork_with_other_link_than_join(node_test_class, visitor_test):

    id_9 = "id_9"

    execution_graph = make_fork_graph(node_test_class)

    # make id_6 (in the fork) having more that just the join module as only node
    execution_graph.add_node(node_test_class(id_9, parents={id6}))

    visitor_test.visit(execution_graph.root)
    assert len(visitor_test.visited) == 11

    with pytest.raises(AssertionError) as e:
        execution_graph.fork_from_node(
            node_test_class(id1, fork_id="chocobo"), join_id=id_join
        )
        assert " all element from a fork should be joining uniquely the fork" in e
