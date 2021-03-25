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

from typing import Optional, Union, Set, List

import networkx as nx

root_node = "::root_node::"


class FreExNode:
    """Representation of the content of a node in the execution graph """

    parents: Set[str]
    """Parents of the node to add """

    def __init__(
        self,
        uid: str = None,
        *,
        fork_id: Optional[str] = None,
        parents: Set[str] = None,
        graph_ref: nx.DiGraph = None,
    ):
        self.parents = parents or set()
        self._graph_ref = graph_ref
        self._id = uid
        self._fork_id = fork_id

    # == PRIVATE ==
    _id: str = None
    _fork_id: Optional[str] = None
    _graph_ref: nx.DiGraph = None
    _depth: int = 0

    def apply_accept_(self, visitor: "AbstractVisitor") -> bool:
        """do not override. Internal accept making the dispatch with standard visitors"""
        from freexgraph.standard_visitor import is_standard_visitor

        if is_standard_visitor(visitor):
            return visitor.visit_standard(self)
        return self.accept(visitor)

    def accept(self, visitor: "AbstractVisitor") -> bool:
        """Accept to be overridden by custom Nodes"""
        return True

    @property
    def id(self) -> str:
        """Id of the node in the graph, will be automatically set/overridden when adding the node."""
        return self._id

    @property
    def fork_id(self) -> Optional[str]:
        """Id of the fork if the current node is from a fork,

        Will be automatically set/overridden when making a fork, it is not needed (useless) to set it manually.
        """
        return self._fork_id

    @property
    def depth(self) -> int:
        """execution depth calculated by the graph

        Can be used in order to know which node can be executed in parallel safely
        """
        return self._depth

    @property
    def graph_ref(self) -> nx.DiGraph:
        """Ref **internally** used by visitor pattern

        Will be automatically set/overridden when adding a node. It is not needed (useless) to set it manually
        """
        return self._graph_ref


class RootNode(FreExNode):
    pass


class GraphNode(FreExNode):
    """Class representing a node that contains another graph, visitation on such graph go through the inner graph """

    _graph_ex: "FreExGraph"

    def __init__(self, uid: str, *, graph: "FreExGraph", parents: Set[str] = None):
        super().__init__(uid=uid, parents=parents, graph_ref=graph._graph)
        self._graph_ex = graph

    def accept(self, visitor: "AbstractVisitor") -> bool:
        visitor.hook_start_graph_node(self)
        not_interrupted = visitor.apply_visitation_(self._graph_ex.root)
        if not_interrupted:
            visitor.hook_end_graph_node(self)
        return not_interrupted


AnyFreExNode = Union[FreExNode, GraphNode]
"""Utility to simplify code"""


class FreExGraph:
    """Execution Graph main class"""

    _graph: nx.DiGraph

    def __init__(self):
        """At instantiation time of FreExGraph, a RootNode instance is made to be the root of the graph"""
        self._graph = nx.DiGraph()
        self._graph.add_node(
            root_node, content=RootNode(uid=root_node, graph_ref=self._graph)
        )

    def add_nodes(self, nodes: List[AnyFreExNode]):
        """Add all the provided nodes in the execution graph.

        The ordering of the node creation can be tedious, as it is required that every node parents already exists to be
        added. This ordering will be inferred making in this method/ it ease the way to create nodes, and to add them in
        the graph.

        If such inference is impossible, an exception is thrown because of an impossibility to create the graph.

        :exception assert failure in case the node cannot be added to the graph (no proper link or node already exists)
        :param nodes: list of nodes to add in the graph, those nodes has to have the id field set
        """
        nodes_sorted: List[AnyFreExNode] = [n for n in nodes if len(n.parents) == 0]
        already_in_graph_id = set(self._graph)

        def all_parents_already_in_list(n: AnyFreExNode) -> bool:
            node_sorted_id = already_in_graph_id
            node_sorted_id.update({s.id for s in nodes_sorted})
            if n.id not in node_sorted_id:
                return n.parents.issubset(node_sorted_id)
            return False

        while len(nodes_sorted) < len(nodes):
            to_add = [n for n in nodes if all_parents_already_in_list(n)]
            assert len(to_add) > 0, "provided nodes are not all linked together"
            nodes_sorted.extend(to_add)

        for node in nodes_sorted:
            self.add_node(node)

    def add_node(self, node: AnyFreExNode):
        """Add a node in the graph

        :exception: assertion error if the node contains ':', is already in the graph or if the parents doesn't exists

        :param node: node to add in the execution graph, can be a normal content (FreExNode derived) or a node to
        contain a graph itself (GraphNode)
        """
        assert (
            node.fork_id is not None or ":" not in node.id
        ), f"Node cannot contains a ':' in its name {node.id}"
        assert not self._graph.has_node(
            node.id
        ), f"{node.id} is already in the execution graph"
        assert all(
            [self._graph.has_node(p) for p in node.parents]
        ), f"all node from parents ({node.parents}) has to be previously added in the execution graph"

        node._graph_ref = self._graph
        node._depth = self._find_current_depth(node.parents)
        self._graph.add_node(node.id, content=node)

        if len(node.parents) == 0:
            node.parents.add(root_node)

        for parent in node.parents:
            self._graph.add_edge(parent, node.id)

    def remove_node(self, node_id: str) -> None:
        """Remove the provided node and all its successors
        :param node_id: node to remove
        """
        assert self._graph.has_node(
            node_id
        ), f"{node_id} has to be in the execution graph to be removed"
        self._graph.remove_nodes_from(self._graph.successors(node_id))
        self._graph.remove_node(node_id)

    @property
    def root(self) -> FreExNode:
        """:return: root node of the graph"""
        return self.get_node(root_node)

    @property
    def graph(self) -> nx.DiGraph:
        """retrieve a reference on the networkx.graph"""
        return self._graph

    def get_node(self, node_id: str) -> Optional[AnyFreExNode]:
        """
        :param node_id: id of the node to retrieve from the execution graph
        :return: node of the graph defined by provided node_id, None if not present in the execution graph
        """
        if not self._graph.has_node(node_id):
            return None
        return self._graph.nodes[node_id]["content"]

    def _find_current_depth(self, parents: Set[str]) -> int:
        """
        Check the depth of all given parents, and return the biggest one + 1 (give the layer depth of the current node
        in the execution graph)
        :param parents: to check
        :return: the depth of the node that has the provided parents.
        """
        if len(parents) == 0:
            return 1
        parent_nodes: List[dict] = [
            dict(self._graph.nodes[key]) for key in parents if self._graph.has_node(key)
        ]
        depth = 0
        for v in parent_nodes:
            cmp = v["content"].depth
            depth = cmp if depth < cmp else depth
        return depth + 1

    def fork_from_node(self, forked_node: FreExNode) -> None:
        """Utility method to fork from a node, when doing so, the provided node will be added with the same dependency
        as the node defined with the id of the forked_node.

        All the graph part depending on the forked node will be duplicated, and their id will be appended with the
        fork_id set on the forked_node. For this reason it is required to have a fork_id set on the forked_node.

        > It is the user responsibility to ensure that those id doesn't collide.

        side_note:
            ':' is used as a separator for the id and the fork_id to ensure a unique name. This is the reason why '::'
            is reserved and cannot be used.

        :param forked_node: node to replace the fork one, its fork_id field has to be set
        :exception: Assertion failure in case that the node defined by forked_node.id doesn't exist in the graph or is a
         GraphNode, or if the forked_node doesn't contains a fork_id
        """
        assert self._graph.has_node(
            forked_node.id
        ), f"{forked_node.id} has to be in the execution graph to be forked"
        assert not isinstance(
            self.get_node(forked_node.id), GraphNode
        ), f"fork node of id {forked_node.id} error : cannot fork a graph node"
        assert (
            forked_node.fork_id
        ), f"forked node of node {forked_node.id} doesn't have fork_id"

        all_forked_nodes_to_add: List[FreExNode] = []

        # recursive internal function to copy a node and then copying all children
        def fork_node(id_new_forked_node: str, to_fork: FreExNode) -> None:
            new_node = type(to_fork)(
                uid=id_new_forked_node,
                parents=(
                    to_fork.parents
                    if to_fork.id != forked_node.id
                    else self._graph.nodes[forked_node.id]["content"].parents
                ),
                graph_ref=forked_node.graph_ref,
            )
            new_node._fork_id = forked_node.fork_id
            new_node._depth = to_fork.depth
            all_forked_nodes_to_add.append(new_node)

            for successor in list(self._graph.successors(to_fork.id)):
                n = self.get_node(successor)
                id_next_fork = self._make_node_id_with_fork(n.id, forked_node.fork_id)
                if not self._graph.has_node(id_next_fork):
                    fork_node(id_next_fork, n)

        fork_node(
            self._make_node_id_with_fork(forked_node.id, forked_node.fork_id),
            forked_node,
        )
        all_forked_nodes_to_add = self._remove_duplicated_node(all_forked_nodes_to_add)

        # update parents links of all forks (to target their homologue forked and not the root one)
        all_forked_id = [n.id for n in all_forked_nodes_to_add]
        for node in all_forked_nodes_to_add:
            if node.id != forked_node.id:
                forked_parents = set()
                for p in node.parents:
                    if any([n.startswith(p) for n in all_forked_id]):
                        forked_parents.add(
                            self._make_node_id_with_fork(p, forked_node.fork_id)
                        )
                    else:
                        forked_parents.add(p)
                node.parents = forked_parents

        self.add_nodes(all_forked_nodes_to_add)

    @staticmethod
    def _make_node_id_with_fork(node_id: str, fork_id: str) -> str:
        """make a unique id for the new fork"""
        return f"{node_id}::{fork_id}"

    @staticmethod
    def _remove_duplicated_node(nodes: List[FreExNode]):
        """remove all duplicates of provided the list"""
        filtered_list = []
        for n in nodes:
            found = False
            for in_list in filtered_list:
                if n.id == in_list.id:
                    found = True
            if not found:
                filtered_list.append(n)
        return filtered_list
