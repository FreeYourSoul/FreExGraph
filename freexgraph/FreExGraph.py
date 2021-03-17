from dataclasses import dataclass, field
from typing import Any, List, Optional

import networkx as nx

root_node = "root_node"


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
    """ Id of the node in the graph, will be automatically set/overriden when adding the node
    It is not needed (useless) to set it manually.
    
    When a fork is created, the name is used as base and combined with the fork_id in order to ensure an unique id 
    """

    fork_id: Optional[str] = None
    """ Id of the fork if the current node is from a fork,  will be automatically set/overriden when making a fork
    It is not needed (useless) to set it manually
    """


class FreExGraph:
    """

    """
    _graph: nx.DiGraph

    def __init__(self):
        self._graph = nx.DiGraph()
        self._graph.add_node(root_node, depth=0)

    def add_node(self, node_id: str, node_wrap: FreExNode):
        """

        :param node_id:
        :param node_wrap:
        :return:
        """
        assert not self._graph.has_node(node_id), f"{node_id} is already in the execution graph"
        assert all([self._graph.has_node(p) for p in node_wrap.parents]), \
            f"all node from parents ({node_wrap.parents}) has to be in previously added in the execution graph"

        node_wrap.id = node_id
        depth: int = self._find_current_depth(node_wrap.parents)
        self._graph.add_node(node_id, content=node_wrap, depth=depth)

        if len(node_wrap.parents) == 0:
            self._graph.add_edge(root_node, node_id)
        for parent in node_wrap.parents:
            self._graph.add_edge(parent, node_id)

    def remove_node(self, node_id: str):
        """ Remove the given node and all its successors
        :param node_id: node to remove
        """
        assert self._graph.has_node(node_id), f"{node_id} has to be in the execution graph to be removed"
        self._graph.remove_nodes_from(self._graph.successors(node_id))
        self._graph.remove_node(node_id)

    def fork_from_node(self, node_id: str, fork_id: str, forked_node_content: Any) -> None:
        """
        :param node_id: id of the node to fork
        :param fork_id: id of the fork
        :param forked_node_content: content of the new node
        :return:
        """
        assert self._graph.has_node(node_id), f"{node_id} has to be in the execution graph to be forked"

        def fork_node(to_fork: FreExNode, content: Any) -> None:
            """recursive internal function to copy a node and then copying all children"""
            id_forked_node = self._make_node_id_with_fork(to_fork.id, to_fork.fork_id)
            new_node = FreExNode(
                fork_id=str(to_fork.fork_id),
                name=str(to_fork.name),
                parents=list(to_fork.parents),
                node=content
            )
            self.add_node(id_forked_node, new_node)
            for successor in self._graph.successors(to_fork.id):
                fork_node(self._graph[successor]["content"], self._graph[successor]["content"].node)

        node_to_fork = self._graph[node_id]["content"]
        node_to_fork.fork_id = fork_id
        fork_node(node_to_fork, forked_node_content)

    def _find_current_depth(self, parents: List[str]) -> int:
        """
        Check the depth of all given parents, and return the biggest one + 1 (give the layer depth of the current node
        in the execution graph)
        :param parents: to check
        :return: the depth of the node that has the provided parents.
        """
        if len(parents) == 0:
            return 1
        parent_nodes = [self._graph.nodes(key) for key in parents if self._graph.has_node(key)]
        return max(parent_nodes, key=lambda v: v["content"].depth) + 1

    @staticmethod
    def _make_node_id_with_fork(node_id: str, fork_id: str) -> str:
        """ make a unique id for the new fork"""
        return f"{node_id}:{fork_id}"
