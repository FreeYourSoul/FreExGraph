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

from typing import Any, Optional, Union, Set, List, Tuple

import networkx as nx

root_node = "root_node"


class FreExNode:
    """ Representation of the content of a node in the execution graph """

    name: str
    """ Base name of the node, it is not the id of the node in the graph,"""

    parents: Set[str]
    """ Parents of the node to add """

    def __init__(self, name: str = "", *, parents: Set[str] = None, graph_ref: nx.DiGraph = None):
        self.name = name
        self.parents = parents or set()
        self._graph_ref = graph_ref

    # == PRIVATE ==
    _id: str = None
    _fork_id: Optional[str] = None
    _graph_ref: nx.DiGraph = None
    _depth: int = 0

    def accept(self, visitor: "AbstractVisitor") -> bool:
        from freexgraph.standard_visitor import is_standard_visitor
        if is_standard_visitor(visitor):
            return visitor.visit_standard(self)
        return True

    @property
    def id(self) -> str:
        """ Id of the node in the graph, will be automatically set/overridden when adding the node
        It is not needed (useless) to set it manually.

        When a fork is created, the name is used as base and combined with the fork_id in order to ensure an unique id
        """
        return self._id

    @property
    def fork_id(self) -> str:
        """ Id of the fork if the current node is from a fork,  will be automatically set/overridden when making a fork
        It is not needed (useless) to set it manually
        """
        return self.fork_id

    @property
    def depth(self) -> int:
        """ execution depth calculated by the graph, can be used in order to know which node can be executed in
        parallel safely
        """
        return self._depth

    @property
    def graph_ref(self) -> nx.DiGraph:
        """ Ref **internally** used by visitor pattern, will be automatically set/overridden when adding a node
        It is not needed (useless) to set it manually
        """
        return self._graph_ref


class RootNode(FreExNode):
    pass


class GraphNode(FreExNode):
    """Class representing a node that contains another graph, visitation on such graph go through the inner graph """

    _graph_ex: "FreExGraph"

    def __init__(self, name: str, *, graph: "FreExGraph", parents: Set[str] = None):
        super().__init__(name=name, parents=parents, graph_ref=graph._graph)
        self._graph_ex = graph

    def accept(self, visitor: "AbstractVisitor") -> bool:
        visitor.hook_start_graph_node(self)
        not_interrupted = visitor.visit(self._graph_ex.root())
        if not_interrupted:
            visitor.hook_end_graph_node(self)
        return not_interrupted


class FreExGraph:
    """"""

    _graph: nx.DiGraph

    def __init__(self):
        self._graph = nx.DiGraph()
        root = RootNode(name=root_node, graph_ref=self._graph)
        root._id = root_node
        self._graph.add_node(root_node, content=root)

    def add_nodes(self, nodes: List[Tuple[str, Union[FreExNode, GraphNode]]]):
        """ Add all the provided nodes in the execution graph.
        The ordering of the node creation can be tedious, as it is required that every node parents already exists to be
        added. This ordering will be inferred making in this method/ it easier to create nodes, and then add them in the
        graph.

        If such inference is impossible, an exception is thrown because of an impossibility to create the graph.

        :param nodes: list of nodes to add in the graph
        """


    def add_node(self, node_id: str, node_content: Union[FreExNode, GraphNode]) -> None:
        """ Add a node in the graph

        :param node_id: id of the node to add
        :param node_content: content of the node, can be a normal content (FreExNode derived) or a node to be joined by
        another graph later (JoinNode derived)
        """
        assert not self._graph.has_node(
            node_id
        ), f"{node_id} is already in the execution graph"
        assert all(
            [self._graph.has_node(p) for p in node_content.parents]
        ), f"all node from parents ({node_content.parents}) has to be in previously added in the execution graph"

        node_content._id = node_id
        node_content._graph_ref = self._graph
        node_content._depth = self._find_current_depth(node_content.parents)
        self._graph.add_node(node_id, content=node_content)

        if len(node_content.parents) == 0:
            node_content.parents.add(root_node)

        for parent in node_content.parents:
            self._graph.add_edge(parent, node_id)

    def join_graph(self, join_node_id: str, another_graph: "FreExGraph") -> None:
        """Join a given graph with the current graph from the provided join_node

        In other words, the join node is going to be replaced by the execution graph provided.

        :param join_node_id:
        :param another_graph:
        """
        assert self._graph.has_node(
            join_node_id
        ), f"{join_node_id} has to be in the execution graph to joined"
        assert isinstance(self._graph[join_node_id], GraphNode), f"node {join_node_id} has to be a JoinNode"
        ...

    def remove_node(self, node_id: str) -> None:
        """Remove the given node and all its successors
        :param node_id: node to remove
        """
        assert self._graph.has_node(
            node_id
        ), f"{node_id} has to be in the execution graph to be removed"
        self._graph.remove_nodes_from(self._graph.successors(node_id))
        self._graph.remove_node(node_id)

    def root(self) -> FreExNode:
        """:return: root node of the graph"""
        return self.get_node(root_node)

    def get_node(self, node_id: str) -> Optional[FreExNode]:
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

    def fork_from_node(
            self, node_id: str, fork_id: str, forked_node_content: Any
    ) -> None:
        """
        :param node_id: id of the node to fork
        :param fork_id: id of the fork
        :param forked_node_content: content of the new node
        :return:
        """
        assert self._graph.has_node(
            node_id
        ), f"{node_id} has to be in the execution graph to be forked"

        def fork_node(to_fork: FreExNode) -> None:
            """recursive internal function to copy a node and then copying all children"""
            id_forked_node = self._make_node_id_with_fork(to_fork.id, to_fork.fork_id)
            new_node = FreExNode(
                name=str(to_fork.name),
                parents=set(to_fork.parents),
                graph_ref=to_fork.graph_ref
            )
            new_node._fork_id = to_fork.fork_id
            self.add_node(id_forked_node, new_node)
            for successor in self._graph.successors(to_fork.id):
                fork_node(self.get_node(successor))

        node_to_fork = self.get_node(node_id)
        node_to_fork.fork_id = fork_id
        fork_node(node_to_fork)

    @staticmethod
    def _make_node_id_with_fork(node_id: str, fork_id: str) -> str:
        """ make a unique id for the new fork"""
        return f"{node_id}:{fork_id}"
