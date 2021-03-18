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

from typing import Callable, Optional, List

from freexgraph import AbstractVisitor, FreExNode


class FindFirstVisitor(AbstractVisitor):
    """ Find the first occurrence of a node that follow the given predicate
    result value is set to a reference to the value found.

    This is a mutable visitor : If a modification is to be done on the found node, it can be done in the predicate
    """

    result: Optional[FreExNode] = None
    """ reference to the node found after visitation that follow the predicate, stay None if none found """

    _predicate: Callable

    def __init__(self, predicate: Callable):
        """
        :param predicate: has to take an argument (FreExNode type) and return a bool, will determine what result is
        expected from the graph
        """
        super().__init__()
        self._predicate = predicate

    def visit_standard(self, node: FreExNode) -> bool:
        if self._predicate(node):
            self.result = node
            # result found, stop visitation
            return False
        return True

    def found(self) -> bool:
        return self.result is not None


class FindAllVisitor(AbstractVisitor):
    results: List[FreExNode]
    """ reference list of nodes found after visitation that follow the predicate, stay None if none found """

    _predicate: Callable

    def __init__(self, predicate: Callable):
        super().__init__()
        self.results = []
        self._predicate = predicate

    def visit_standard(self, node: FreExNode) -> bool:
        if self._predicate(node):
            self.results.append(node)
        return True

    def count(self) -> int:
        return len(self.results)


def is_standard_visitor(visitor_instance):
    return any([isinstance(visitor_instance, c) for c in [FindAllVisitor, FindFirstVisitor]])
