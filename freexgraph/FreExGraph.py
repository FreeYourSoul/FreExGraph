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

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

import networkx as nx

root_node = "root_node"

exception_on_join_node_visit: bool = True
"""global setting to set if we want to raise exception in case of a Visitation of a JoinNode"""


@dataclass
class FreExNode:
    """ Representation of the content of a node in the execution graph """

    node: Any
    """ Node object """

    name: str
    """ Base name of the node, it is node the id of the node in the graph,"""

    parents: List[str] = field(default_factory=[])
    """ Parents of the node to add """

    id: str = None
    """ Id of the node in the graph, will be automatically set/overridden when adding the node
    It is not needed (useless) to set it manually.
    
    When a fork is created, the name is used as base and combined with the fork_id in order to ensure an unique id 
    """

    fork_id: Optional[str] = None
    """ Id of the fork if the current node is from a fork,  will be automatically set/overridden when making a fork
    It is not needed (useless) to set it manually
    """

    graph_ref: nx.DiGraph = None
    """ Ref **internally** used by visitor pattern, will be automatically set/overridden when adding a node
    It is not needed (useless) to set it manually
    """

    def accept(self, visitor: "AbstractVisitor") -> bool:
        return self.node.accept(visitor)


class JoinNode(FreExNode):
    """Class representing a join with another graph """

    # throw by default or is ignored in visitation
    def accept(self, _) -> bool:
        if exception_on_join_node_visit:
            raise RuntimeError("Visitation of JoinNode: set exception_on_join_node_visit to not throw")
        return True


class BundleDependencyNode(FreExNode):
    """Class representing a dependency node, this node shouldn't be executed and will be ignored by visitors"""

    # ignored in visitation
    def accept(self, _) -> bool:
        return True


class FreExGraph:
    """"""

    _graph: nx.DiGraph

    def __init__(self):
        self._graph = nx.DiGraph()
        self._graph.add_node(root_node, depth=0)

    def add_node(self, node_id: str, node_content: Union[FreExNode, JoinNode]) -> None:
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

        node_content.id = node_id
        node_content.graph_ref = self._graph
        depth: int = self._find_current_depth(node_content.parents)
        self._graph.add_node(node_id, content=node_content, depth=depth)

        if len(node_content.parents) == 0:
            self._graph.add_edge(root_node, node_id)
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
        assert isinstance(self._graph[join_node_id], JoinNode), f"node {join_node_id} has to be a JoinNode"
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

        def fork_node(to_fork: FreExNode, content: Any) -> None:
            """recursive internal function to copy a node and then copying all children"""
            id_forked_node = self._make_node_id_with_fork(to_fork.id, to_fork.fork_id)
            new_node = FreExNode(
                fork_id=str(to_fork.fork_id),
                name=str(to_fork.name),
                parents=list(to_fork.parents),
                node=content,
            )
            self.add_node(id_forked_node, new_node)
            for successor in self._graph.successors(to_fork.id):
                fork_node(
                    self._graph[successor]["content"],
                    self._graph[successor]["content"].node,
                )

        node_to_fork = self._graph[node_id]["content"]
        node_to_fork.fork_id = fork_id
        fork_node(node_to_fork, forked_node_content)

    def bundle_nodes(self, max_limit: int) -> int:
        """ bundle the whole graph dependencies with fake node in order to ensure that no node has more than the
        provided maximum number of dependencies or successor

        :param max_limit: limit at which a bundle dep is generated
        :return: number of time bundle the bundle ticked
        """
        assert max_limit > 10, "limit for the bundle has to be superior to 10"
        tick = 0
        return tick

    def _find_current_depth(self, parents: List[str]) -> int:
        """
        Check the depth of all given parents, and return the biggest one + 1 (give the layer depth of the current node
        in the execution graph)
        :param parents: to check
        :return: the depth of the node that has the provided parents.
        """
        if len(parents) == 0:
            return 1
        parent_nodes = [
            self._graph.nodes(key) for key in parents if self._graph.has_node(key)
        ]
        return max(parent_nodes, key=lambda v: v["content"].depth) + 1

    @staticmethod
    def _make_node_id_with_fork(node_id: str, fork_id: str) -> str:
        """ make a unique id for the new fork"""
        return f"{node_id}:{fork_id}"
