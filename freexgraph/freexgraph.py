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

from copy import copy, deepcopy
from typing import Optional, Union, Set, List, Any, Tuple

import networkx as nx


root_node = "::root_node::"


AnyVisitor = Any
"""Any visitor is a class that is inheriting from AbstractVisitor"""


class FreExNode:
    """Representation of the content of a node in the execution graph """

    parents: Set[str]
    """Parents of the node to add"""

    extension_node: bool
    """ """

    def __init__(
        self,
        uid: str = None,
        *,
        fork_id: Optional[str] = None,
        parents: Set[str] = None,
        graph_ref: nx.DiGraph = None,
        extension_node: bool = False,
    ):
        self.parents = parents or set()
        self.extension_node = extension_node
        self._graph_ref = graph_ref
        self._id = uid
        self._fork_id = fork_id

    # == PRIVATE ==
    _id: str = None
    _fork_id: Optional[str] = None
    _graph_ref: nx.DiGraph = None
    _depth: int = 0

    def __len__(self):
        return 1

    def apply_accept_(self, visitor: AnyVisitor) -> bool:
        """do not override. Internal accept making the dispatch with standard visitors"""
        from freexgraph.standard_visitor import StandardVisitor

        if self.id != root_node and visitor.progress_bar_ is not None:
            visitor.progress_bar_.set_postfix(
                {"node": self._id, "visitor": type(visitor).__name__}
            )
            visitor.progress_bar_.update()
            visitor.progress_bar_.refresh()

        if isinstance(visitor, StandardVisitor):
            if self.extension_node and visitor.extension_depth_threshold():
                with visitor.inc_extension_depth():
                    self.accept(visitor)
            return visitor.visit_standard(self)
        return self.accept(visitor)

    def accept(self, visitor: AnyVisitor) -> bool:
        """Accept to be overridden by custom Nodes"""
        return True

    def get_successors(self) -> List["FreExNode"]:
        """Retrieve nodes depending on the current one"""
        if self._graph_ref is None:
            return []
        return [
            self._graph_ref.nodes[node_id]["content"]
            for node_id in self._graph_ref.successors(self._id)
        ]

    def get_predecessors(self) -> List["FreExNode"]:
        """Retrieve nodes the current node depends on"""
        if self._graph_ref is None:
            return []
        return [
            self._graph_ref.nodes[node_id]["content"]
            for node_id in self._graph_ref.predecessors(self._id)
        ]

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


RemovedParent = Tuple[FreExNode, Set[str]]


class RootNode(FreExNode):
    pass


class GraphNode(FreExNode):
    """Class representing a node that contains another graph, visitation on such graph go through the inner graph """

    _graph_ex: "FreExGraph"

    def __init__(
        self, uid: str = None, *, graph: "FreExGraph", parents: Set[str] = None
    ):
        super().__init__(
            uid=uid, parents=parents, graph_ref=graph._graph, extension_node=True
        )
        self._graph_ex = graph

    def accept(self, visitor: AnyVisitor) -> bool:
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

    @staticmethod
    def _make_node_id_with_fork(node_id: str, fork_id: str) -> str:
        """make a unique id for the new fork"""
        return f"{node_id}::{fork_id}"

    def add_nodes(self, nodes: List[AnyFreExNode]) -> None:
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

    def add_node(self, node: AnyFreExNode) -> None:
        """Add a node in the graph

        :exception: assertion error if the node contains ':', is already in the graph or if the parents doesn't exists

        :param node: node to add in the execution graph, can be a normal content (FreExNode derived) or a node to
        contain a graph itself (GraphNode)
        """
        assert (
            node.fork_id is not None or ":" not in node.id
        ), f"Node cannot contains a ':' in its id {node.id}"
        assert not self._graph.has_node(
            node.id
        ), f"{node.id} is already in the execution graph"
        assert all(
            [self._graph.has_node(p) for p in node.parents]
        ), f"all node from parents ({node.parents}) has to be previously added in the execution graph"

        node._graph_ref = self._graph
        node._depth = self.__find_current_depth(node.parents)
        self._graph.add_node(node.id, content=node)

        if len(node.parents) == 0:
            node.parents.add(root_node)

        for parent in node.parents:
            self._graph.add_edge(parent, node.id)

    def remove_node(self, node_id: str) -> None:
        """Remove the provided node and all its successors
        :param node_id: node to remove
        """
        if self._graph.has_node(node_id):
            for n in copy(self._graph.successors(node_id)):
                self.remove_node(n)
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

    def sub_graph(
        self,
        from_node_id: str,
        to_nodes_id: Optional[List[str]] = None,
        return_removed_parents: bool = False,
    ) -> Union["FreExGraph", Tuple["FreExGraph", List[RemovedParent]]]:
        """Utility method to retrieve a subgraph from a given node until the end of the graph or until one of the
        provided node is encountered.

        :param from_node_id: node from which the sub graph start
        :param to_nodes_id: nodes on which the sub graph stop, if none encountered, subgraph go until the leaf nodes
        :param return_removed_parents: set to false by default, if set to true, return a second return tuple value that
        contains the removed parents in the subgraph
        :return: a sub graph delimited by the provided nodes id, if return_removed_parents set to true, also return a
        tuple that represent Tuple[node_that_got_parents_deleted, deleted_parent_links_set]
        """
        from_node: FreExNode = self.get_node(from_node_id)
        assert (
            from_node is not None
        ), f"Error sub graph from node {from_node_id}, node has to be in the execution graph"

        nodes_in_subgraph: List[FreExNode] = []
        nodes_in_subgraph_id: Set[str] = set()

        def add_node_in_subgraph(current_node: FreExNode):
            if current_node.id in nodes_in_subgraph_id:
                return
            nodes_in_subgraph.append(deepcopy(current_node))
            nodes_in_subgraph_id.add(current_node.id)
            if to_nodes_id is not None and current_node.id in to_nodes_id:
                return
            all_suc = list(self._graph.successors(current_node.id))
            for successor in all_suc:
                node_suc = self.get_node(successor)
                assert (
                    node_suc is not None
                ), f"Error sub graph to node {node_suc.id}, node has to be in the execution graph"
                add_node_in_subgraph(node_suc)

        add_node_in_subgraph(from_node)

        saved_removal: List[RemovedParent] = []

        # cleanup parents
        for n in nodes_in_subgraph:
            if return_removed_parents:
                saved_removal.append(
                    (n, {p for p in n.parents if p not in nodes_in_subgraph_id})
                )
            n.parents = {p for p in n.parents if p in nodes_in_subgraph_id}

        sub_graph = FreExGraph()
        sub_graph.add_nodes(nodes_in_subgraph)
        if return_removed_parents:
            return sub_graph, saved_removal
        return sub_graph

    def fork_from_node(
        self, forked_node: FreExNode, *, join_id: Optional[str] = None
    ) -> None:
        """Utility method to fork from a node, when doing so, the provided node will be added with the same dependency
        as the node defined with the id of the forked_node.

        All the graph part depending on the forked node will be duplicated (until the join_node if provided), and their
        id will be appended with the fork_id set on the forked_node. For this reason it is required to have a fork_id
        set on the forked_node.

        If the provided join_node doesn't exist, an exception is thrown.
        If a join node is provided, all node from the provided one until the join node is encountered are duplicated. if
        the join node is not encountered, duplicate node until leaf

        warning:
            It is the user responsibility to ensure that those id doesn't collide.

        side_note:
            ':' is used as a separator for the id and the fork_id to ensure a unique name. This is the reason why '::'
            is reserved and cannot be used.

        raise Assertion failure:
            * if the node defined by forked_node.id doesn't exist in the graph.
            * if the forked_node doesn't contains a fork_id.
            * if a join_node is provided but does not exist.

        :param forked_node: node to replace the fork one, its fork_id field has to be set
        :param join_id: node to stop duplication (used for map_reduce) if encountered

        """
        assert self._graph.has_node(
            forked_node.id
        ), f"Error fork of node {forked_node.id}, node to fork has to be in the execution graph"
        assert (
            forked_node.fork_id
        ), f"Error fork of node {forked_node.id}: doesn't have fork_id"
        assert join_id is None or self._graph.has_node(
            join_id
        ), f"Error fork of node {forked_node.id} with join_id {join_id}: join_id node doesn't exist in graph "

        sub_graph, removed_parents = self.sub_graph(
            from_node_id=forked_node.id,
            to_nodes_id=[join_id] if join_id else [],
            return_removed_parents=True,
        )
        sub_graph._graph.remove_node(root_node)
        if join_id is not None:
            sub_graph._graph.remove_node(join_id)

        # renaming all nodes (and remove useless root_node)
        for node_to_fork_rename in [
            sub_graph.get_node(n) for n in sub_graph.graph.nodes
        ]:
            if root_node in node_to_fork_rename.parents:
                initial_graph_node = self.get_node(node_to_fork_rename.id)
                if root_node not in initial_graph_node.parents:
                    node_to_fork_rename.parents.remove(root_node)

            node_to_fork_rename._fork_id = forked_node.fork_id
            node_to_fork_rename._id = self._make_node_id_with_fork(
                node_to_fork_rename.id, forked_node.fork_id
            )
            node_to_fork_rename.parents = {
                self._make_node_id_with_fork(p, forked_node.fork_id)
                for p in node_to_fork_rename.parents
            }

        # redo linking
        for node, removed_parents in removed_parents:
            node.parents.update(removed_parents)

        self.add_nodes([sub_graph.get_node(n) for n in sub_graph.graph.nodes])

    def replace_node(self, to_replace: FreExNode) -> None:
        """Replace the node defined by the provided node id with the provided node, keeping the important data needed
        for the graph consistency between the initial node and the new one.

        :param to_replace: node to replace (use id property in order to retrieve the proper node to replace)
        """
        previous_node = self.get_node(to_replace.id)
        assert (
            previous_node is not None
        ), f"Cannot replace node {to_replace.id} that is not in the graph"

        to_replace._fork_id = previous_node.fork_id
        to_replace._graph_ref = previous_node.graph_ref
        to_replace._depth = previous_node.depth
        to_replace.parents = previous_node.parents
        self._graph.nodes[to_replace.id]["content"] = to_replace

    def __find_current_depth(self, parents: Set[str]) -> int:
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
