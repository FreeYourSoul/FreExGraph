[![Build Status](https://travis-ci.com/FreeYourSoul/FreExGraph.svg?branch=main)](https://travis-ci.com/FreeYourSoul/FreExGraph)
[![Scc Count Badge](https://sloc.xyz/github/FreeYourSoul/FreExGraph/)](https://github.com/FreeYourSoul/FreExGraph/)
[![Scc Count Badge](https://sloc.xyz/github/FreeYourSoul/FreExGraph/?category=code)](https://github.com/FreeYourSoul/FreExGraph/)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](https://raw.githubusercontent.com/FreeYourSoul/FreExGraph/master/LICENSE)

# FreExGraph
An Execution graph implementation.
It provide:
* an easy to use interface to make a graph of execution (of custom made node).
* an easy way to Visit this graph in order to execute action on them.

## Dependencies

* networkx : FreExGraph is a layer on top of networkx 
* tqdm : provide a nice way to display progression on visitation

## Documentation

The goal of this library is to provide a standardized way to represent an execution graph and to visit it via visitor. Some visitors are provided by FreExGraph but the more important thing is the ability to very easily provide its own visitor and it's own node type.

### Node creation and visitation

In order to use FreExGraph properly, it is required to provide your own node type. A node is a class that inherit from FreExNode class. It provides the following interface:
```python
from freeexgraph import FreExNode, AbstractVisitor

class MyCustomNode(FreExNode):
  def accept(self, visitor: AbstractVisitor) -> bool:
    """ 
    An accept method that will be called for each node 
    visited by the visitor which is passed as parameter.
    """   
    ...    

```
An accept method is provided that return a boolean, if False is returned through the accept method, the visitation stop at that node.

### Quick Start example

It is possible to call any method from the visitor specific to the current node. But as your node has to be able to work with any visitor you will provide. It is recommended to implement your own base class for the Visitor pattern. This base visitor would for example contains all node specific method you have (as many as you have node types). All those method would redirect to a default behavior if your custom visitor doesn't contains code specific to a node.

Here is a complete example of how you should create an easily extensible visitor for your nodes:

```python

# We have Three different kind of node : Alpha, Beta, Gamma

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

class CustomVisitor(MyBaseVisitor)
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

**add_node:**

**add_nodes:**

### Graph Node

It is possible to embed a graph into another thanks to a graph node. Any visitation going through a graph node is going to be propagated to the inner graph.

< TODO >

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

v = FindFirstVisitor(lambda node: node.name.startswith("id3"))
v.visit(graph_above.root())
assert v.found()
assert v.result.name == "id3"
```

* **FindAllVisitor**: A visitor that will find all the node of the execution graph that match a given predicate:
```python
from freexgraph.standard_visitor import FindAllVisitor

v = FindAllVisitor(lambda node: node.name[0:3] > "id3")
v.visit(graph_above.root())
assert v.count() == 3
assert len(v.results) == 3
```

* **ValidateGraphIntegrity**: A visitor that validate that the graph is not illegal (every parents of every node exist in the graph, no infinite recursion of dependency etc...).
```python
from freexgraph.standard_visitor import ValidateGraphIntegrity

v = ValidateGraphIntegrity()

# visitation does assertion to verify if the graph is correct
v.visit(graph_above.root())
```

## Installation

* Via pip
```shell
pip install .
# uninstall with `pip uninstall freexgraph`
```

* Via nix: A nix recipe is provided in order to create a local environment or installation.
```shell
# build freexgraph
nix-build . -A freexgraph

# create a local environment to use freexgraph
nix-build . -A build_env
```
