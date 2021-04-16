[![Build Status](https://travis-ci.com/FreeYourSoul/FreExGraph.svg?branch=main)](https://travis-ci.com/FreeYourSoul/FreExGraph)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/e5d3ee2861954023afce6f161a9d6b64)](https://www.codacy.com/gh/FreeYourSoul/FreExGraph/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=FreeYourSoul/FreExGraph&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://app.codacy.com/project/badge/Coverage/e5d3ee2861954023afce6f161a9d6b64)](https://www.codacy.com/gh/FreeYourSoul/FreExGraph/dashboard?utm_source=github.com&utm_medium=referral&utm_content=FreeYourSoul/FreExGraph&utm_campaign=Badge_Coverage)
[![Scc Count Badge](https://sloc.xyz/github/FreeYourSoul/FreExGraph/)](https://github.com/FreeYourSoul/FreExGraph/)
[![Scc Count Badge](https://sloc.xyz/github/FreeYourSoul/FreExGraph/?category=code)](https://github.com/FreeYourSoul/FreExGraph/)

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/FreeYourSoul/FreExGraph/master/LICENSE)
[![Upload Python Package](https://github.com/FreeYourSoul/FreExGraph/actions/workflows/python-publish.yml/badge.svg)](https://github.com/FreeYourSoul/FreExGraph/actions/workflows/python-publish.yml)
# FreExGraph
An Execution graph implementation.
It provide:
* an easy to use interface to make a graph of execution (of custom made node).
* an easy way to Visit this graph in order to execute action on them.

## Content table

* [Intro Node](#node-creation-and-visitation)  
  * [Template Example](#template-example)
  * [Graph creation](#graph-creation)
  * [Graph Node](#graph-node) 
  * [Fork mechanism](#fork) 
* [Visitors](#visitors)
    * [Visitor hook](#abstract-visitor-hooks)
    * [Standard visitors](#standard-visitor-provided-by-freexgraph)
* [Installation](#installation)

## Dependencies

* Python >= 3.6
* [networkx](https://networkx.org/) : FreExGraph is a layer on top of networkx 
* [tqdm](https://github.com/tqdm/tqdm) : provide a nice way to display progression on visitation

---

# Documentation

The goal of this library is to provide a standardized way to represent an execution graph and to visit it via visitor. Some visitors are provided by FreExGraph but the more important thing is the ability to very easily provide its own visitor and it's own node type.

> **Convention**: by convention : every method with their name ending with an underscore ' _ ', the method is for internal use only and should not be used directly by the user. (example : AbstractVisitor.apply_visitation_ , FreExNode.apply_accept_ ) 

## Node creation and visitation

In order to use FreExGraph properly, it is required to provide your own node type. A node is a class that inherit from FreExNode class. It provides the following interface:
```python
from freexgraph import FreExNode, AbstractVisitor 

class MyCustomNode(FreExNode):
  def accept(self, visitor: AbstractVisitor) -> bool:
    """ 
    An accept method that will be called for each node 
    visited by the visitor which is passed as parameter.
    """   
    ...    

```
An accept method is provided that return a boolean, if False is returned through the accept method, the visitation stop at that node.
It is important to know that the default behaviour of FreExNode in case of visitation from a visitor is to be ignored. Only standard visitor would work on a raw FreExNode. It emphasis how important it is to provide your node implementation.

### Template Example

It is possible to call any method from the visitor specific to the current node. But as your node has to be able to work with any visitor you will provide. It is recommended to implement your own base class for the Visitor pattern. This base visitor would for example contains all node specific method you have (as many as you have node types). All those method would redirect to a default behavior if your custom visitor doesn't contains code specific to a node.

Here is a complete example that can be used as a good start to show how you should create an easily extensible visitor for your nodes:

```python

# We have Three different kind of node : Alpha, Beta, Gamma
from freexgraph import FreExNode, AbstractVisitor 

class MyNodeAlpha(FreExNode):
  def accept(self, visitor: AbstractVisitor) -> bool:
    return visitor.visit_alpha_node(self)

class MyNodeBeta(FreExNode):
  def accept(self, visitor: AbstractVisitor) -> bool:
    return visitor.visit_beta_node(self)

class MyNodeGamma(FreExNode):
  def accept(self, visitor: AbstractVisitor) -> bool:
    return visitor.visit_gamma_node(self)


# A base class that handles every type of node by calling a default mechanism

class MyBaseVisitor(AbstractVisitor):

  # base visitor just ignore every node
  def visit_default(self, node: FreExNode) -> bool:
    return True

  def visit_alpha_node(self, node: FreExNode) -> bool:
    return self.visit_default(node)

  def visit_beta_node(self, node: FreExNode) -> bool:
    return self.visit_default(node)
      
  def visit_gamma_node(self, node: FreExNode) -> bool:
    return self.visit_default(node)      


# My actual Visitor implementation, this one just need a specific action 
# to be made on MyNodeGamma node type. The rest has a default behaviour.

class CustomVisitor(MyBaseVisitor):
  def visit_default(self, node: FreExNode):
    print("This is the behavior for Alpha and Beta nodes")
    return True

  def visit_gamma_node(self, node: FreExNode):
    print("This is the behavior specialized for gamma nodes")
    return True

```

> It is strongly advised to use this idiom with a BaseVisitor that ignore every node by default, and then each and every of your visitor doing actual work override your default behavior method (here called `visit_default` but it can be any name you want of course).

### Graph creation

After creating node types (see above), we can create an execution graph that will use those nodes.

A graph is created with the class `FreExGraph`, which doesn't require any parameter, as follow:
```python
from freexgraph import FreExGraph 

execution_graph = FreExGraph()
```

> it is important to note that the character ':' is forbidden in node id, as it is used for internal node (fork uniqueness and/or root_node)

When the graph instance is done, you need to add nodes to them. The two following methods makes it possible.

**add_node:** Of the method of signature `add_node(self, node: FreExNode)`. This method will add a node to the graph. If no parents are set in the given node, 
the node will be linked with the root node that is automatically generated by the FreExGraph. If parents are set, edges will be made. 
* Node id HAS to not be present in the graph 
* A node's parent HAS to already be present in the graph. 
* The id of the graph cannot contains ':' which is a forbidden character.
* No infinite looping of the node are accepted.

In the case any of those rules is not respected. An Assertion error is thrown.

example:
```python
# The graph below would look like that.
#
#            id1
#             |
#            id2 ____.
#             |       \
#             |       id4
#             |       / |
#            id3 ----'  |
#             |         |
#            id5 -------` 
#
execution_graph = FreExGraph()
id1 = f"id1"
id2 = f"id2"
id3 = f"id3"
id4 = f"id4"
id5 = f"id5"

execution_graph.add_node(FreExNode(id1))
execution_graph.add_node(FreExNode(id2, parents={id1}))
execution_graph.add_node(FreExNode(id4, parents={id2}))
execution_graph.add_node(FreExNode(id3, parents={id2, id4}))
execution_graph.add_node(FreExNode(id5, parents={id4, id3}))
```

**add_nodes:**: It can be cumbersome to ensure the ordering of the nodes you want to add (with the parents order). In order to avoid this issue, you can use add_nodes with the signature `add_nodes(self, nodes: List[AnyFreExNode])`.  
This method is going to re-order the nodes depending on their parents in order to add them (calling add_node internally) properly.
`add_node` being called. All the rules applicable on add_node has to be respected with add_nodes (unicity of id and so on...)


example
```python
# we want to make the same graph as the one tested above for add_node
execution_graph = FreExGraph()
node_1 = FreExNode(id1)
node_2 = FreExNode(id2, parents={id1})
node_3 = FreExNode(id3, parents={id2, id4})
node_4 = FreExNode(id4, parents={id2})
node_5 = FreExNode(id5, parents={id4, id3})

# adding them in complete disorder is okay
execution_graph.add_nodes([node_5, node_2, node_1, node_3, node_4])
```

### Graph Node

It is possible to embed a graph into another thanks to a graph node. Any visitation going through a graph node is going to be propagated to the inner graph.

To make one you need to create a FreExGraph (that will be in the GraphNode).  
example :

```python
    # We will do the following graph
#
#           id1___,
#            |     \
#            |     id_graph (graph_node)
#            |     /
#           id2---`
#
execution_graph = FreExGraph()

inner_graph = FreExGraph()
# fill inner_graph as you want 

execution_graph.add_node(NodeForTest(id1))
execution_graph.add_node(GraphNode(id_graph, parents={id1}, graph=inner_graph))
execution_graph.add_node(NodeForTest(idc, parents={id1, id_graph}))
```

### Fork

FreExGraph provide a fork mechanism. It provides an easy way to duplicate a graph from a given node until the end of the graph (or to a specific node that would be used as a join).

Here is an example:   
_Given the following graph in `execution_graph`:_
```python
#            id0
#             |
#       .___ id1 ___.           
#      /      |      \
#     id2    id3     id4
#     |     /   \      |
#     |   id5   id6    |
#     \     \   /     /
#      `---- id7 ----'        
#          /     \
#        id8     id9
#

# If we decide to fork (with the fork id f1) from the node id4
execution_graph.fork_from_node(FreExNode(uid="id4", fork_id="f1"))

# The result would be the following:

#            id0
#             |
#       .___ id1 ___.          
#      /      |      \
#     id2    id3     id4 ----------- id4::f1
#     |     /   \      |                |
#     |   id5   id6    |                |
#     \     \   /     /                 |
#      `---- id7 ----'               id7::f1
#          /     \                 /        \
#        id8     id9           id8::f1     id9::f1
#
```
Obviously if you want the node id4::f1 (which is of type FreExNode as you asked) to ever be visited by one of your visitor, you should provide your own node implementation.

It is also possible to provide a join node. It will be a node used as join for the fork in order to not have to fork the whole graph from the source of the fork. It is usefull if you have to multiply a big chunk of execution graph because one node has to change some internal values (in experimentation fields, it can be useful for parameter explorations).

> **Try avoiding forks** : This is a mecanism that can be useful in certain cases (the main one would be parameter exploration on an experimentation) But when it comes to map reduce for example, it is advised to manually fo the nodes you want instead (improve readibility of what you are doing when making your graph). A chaining of fork can start being very hard to understand for the user.

But if you want to do a map reduce with a fork, it is do-able by setting the join_id to the `fork_from_node` method. The join_id has to be an existing node on which, for every parents that are part of the fork has only this join node as child.
See [test using this mechanism](https://github.com/FreeYourSoul/FreExGraph/blob/ae707cf0fcb8486bde783cd0c7fe67217a56b3d2/test/fork_test.py#L41-L66) for more details

## Visitors

### Abstract Visitor hooks

Abstract visitor provide some default hooks that can be overridden from custom visitors in order to implement more complex logic depending on the graph visit.
* `hook_start()`: This hook is called when the visitation of the graph start (an interesting way to use this hook could be to reinitialize your visitor in case of re-use).
* `hook_end()`: This hook is called when the visitation of the graph end.
* `hook_start_graph_node(gn: GraphNode)` : This hook is called when a graphnode recursion start (graph node given as parameter of the hook).
* `hook_end_graph_node(gn: GraphNode)` : This hook is called when a graphnode visitation end (graph node given as parameter of the hook).

Custom hooks can be implemented on any visitor if you want to trigger a specific action that depend on the business data stored in your node.   

To do so, on a visitor instance, use the method `register_custom_hook(predicate: Callable, hook: Callable)` : This method will trigger the provided hook if the given predicate return true for a node. Custom hooks are all executed just before the visitation of each node.   

**Example of a custom hook:** 
```python
visitor_test.register_custom_hook(
    predicate=lambda n: n.id.startswith("id3"), hook=hook
)
visitor_test.register_custom_hook(
    predicate=lambda n: not n.id.startswith("id3"),
    hook=hook_2,
)
visitor_test.visit(execution_graph.root)
```

### Standard Visitor provided by FreExGraph

A set of visitor is provided in order to do simple actions. Those are called standard visitor.

All standard visitors are present in the standard_visitor module and exposed through freexgraph import.
For all example below, we assume a graph as follows:
```shell
# we assume an object `graph_above` of type FreExGraph that represent a  
# graph as follow
#
#                id1
#                 |
#                id2
#              /  |
#          id3    |
#        /  |  \  |
#      id5  |   id4 
#           |  /
#          id6
```

* **FindFirstVisitor**: A visitor that will find the first node of the execution graph that match a given predicate:
```python
from freexgraph.standard_visitor import FindFirstVisitor 

v = FindFirstVisitor(lambda node: node.id.startswith("id3"))
v.visit(graph_above.root)
assert v.found()
assert v.result.name == "id3"
```

* **FindAllVisitor**: A visitor that will find all the node of the execution graph that match a given predicate:
```python
from freexgraph.standard_visitor import FindAllVisitor

v = FindAllVisitor(lambda node: node.id[0:3] > "id3")
v.visit(graph_above.root)
assert v.count() == 3
assert len(v.results) == 3
```

* **ValidateGraphIntegrity**: A visitor that validate that the graph is not illegal (every parents of every node exist in the graph, no infinite recursion of dependency etc...).
```python
from freexgraph.standard_visitor import ValidateGraphIntegrity

v = ValidateGraphIntegrity()

# visitation does assertion to verify if the graph is correct
v.visit(graph_above.root)
```
Those visitors implement the start hook that reinitialize their state as if they were new freshly created visitor. Which is why an instance of a standard visitor can be re-used. To implement this kind of behaviour in your own visitors, check out [visitor hooks](#abstract-visitor-hooks).

### Progression visit

tqdm is implemented in AbstractVisitor. 
It makes possible to have a progress bar while visiting your graph. To do so, when instantiating the AbstractVisitor from `super()` within your custom visitor.
Just set the boolean parameter `with_progress_bar` in the constructor to True.  
```python
class MyCustomVisitor(AbstractVisitor):
    def __init__(self):
        super().__init__(with_progress_bar=True)

    # rest of your custom visitor implementation
    ...
```

### Composed Visitor

Usually, in order to complete the action you want to perform on a graph, you require to chain the visitor one after the other. In order to do so, a utility exist in freexgraph called VisitorComposer.

A visitor composer is split between three part :
* before : a list of visitor pattern to apply one after the other. Each of those visitations will trigger a traversal of the graph. All those visitors are launched in order before the action
* action : a list of visitor pattern to apply in one traversal. It is useful in order to not traverse the graph too many times if not required
* after : a list of visitor pattern to apply one after the other. Each of those visitations will trigger a traversal of the graph. All those visitors are launched in order after the action

The action visitor list from the visitor composer is what is special. It makes it possible to do multiple actions in one traversal of the graph.

Usage example:
```python
all_before: List[AbstractVisitor] = [ VisitorA(), VisitorB() ]
actions:    List[AbstractVisitor] = [ VisitorC(), VisitorD(), VisitorE() ]
all_after:  List[AbstractVisitor] = [ VisitorF(), VisitorG() ]

visitor_composed = VisitorComposer(before=all_before, action=actions, after=all_after)

# At visitation of the composed visitor
# * VisitorA is applied on execution_graph.root (full traversal)
# * VisitorB is applied on execution_graph.root (full traversal)
#
# In one traversal
# * VisitorC action is applied on each node
# * VisitorD action is applied on each node
# * VisitorE action is applied on each node
#
# After 
# * VisitorF is applied on execution_graph.root (full traversal)
# * VisitorG is applied on execution_graph.root (full traversal)
visitor_composed.visit(execution_graph.root)
```

### Reverse visit

It is possible to revert the order of visitation of any visitor by setting its attribute `is_reversed` of the visitor (works with any type of visitor inheriting from AbstractVisitor).  
example :
```python
# we assume a graph called `execution_graph` that represent the following graph:
# id1 ---> id2 ---> id3 ---> id4 ---> id3bis ---> id5

v = FindFirstVisitor(lambda node: node.id.startswith("id3"))

v.visit(execution_graph.root)
assert v.found()
assert v.result.id == "id3"

v.is_reversed = True
v.visit(execution_graph.root)
assert v.found()
assert v.result.id == "id3bis"
```

---

## Installation

* Via pip
```shell
# from source
pip install .

# from pypi (latest released version)
pip install freexgraph

# uninstall with `pip uninstall freexgraph`
```

* Via nix: A nix recipe is provided in order to create a local environment or installation.
```shell
# build freexgraph
nix-build . -A freexgraph

# create a local environment to use freexgraph
nix-build . -A build_env
```
