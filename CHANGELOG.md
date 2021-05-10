# Changelogs

## Version 1.2.3
(Released : May 11, 2021) : tag 1.2.3
* Fix bug on Composed visitation (multiple start hook called)

## Version 1.2.2
(Released : May 06, 2021) : tag 1.2.2
* Improve forking mechanism to match with sub_graph
* Improve fork/sub_graph documentation
* Forward kwargs on standard visitor to be able to use BaseVisitor constructor
* Add replace node utility

## Version 1.2.0 / Version 1.2.1
(Released : April 30, 2021) : tag 1.2.0/1.2.1
* Add sub_graph
* Fix bug (forced to set an id on GraphNode constructor)
* Fix bug (standalone node without graph visitation failed)
	
## Version 1.1.0
(Released : April 16, 2021) : tag 1.1.0
* Fix documentation
* Add utility method at node level (get_predecessors/get_successors)
* Add possibility to visitation of the graph from anywhere (starting provided node) as it would have been expected seeing the API

## Version 1.0.0 
(Released : April 2, 2021) : tag 1.0.0
* Complete documentation
* Test and implement custom visitor hook
* Implement delete nodes

## Version 0.0.0
(Alpha released : March 27, 2021) : tag 0.1.0
* First implementation: 
    * Execution graph implementation
    * Visitor implementation
    * Composed visitor implementation
    * Documentation
    

---

## TODO list for FreExGraph (next versions)

## Feature todo

* ~~Implement sub_graph~~
* ~~fix graph node enforcement of uid~~
* ~~Delete node~~ 
* ~~Partial graph traversal~~

## Documentation todo

* ~~Add documentation on sub_graph~~
* ~~Add doc about node / graph creation~~
* ~~Add documentation about graph nodes~~
* ~~Add documentation about custom hook~~
* ~~Add documentation Composed Visitor~~

## Testing todo

* ~~Test sub_graph~~
* ~~Test Composed Visitor~~
* ~~Custom hook~~
