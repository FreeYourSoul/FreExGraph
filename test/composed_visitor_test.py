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

from typing import List

from freexgraph import AbstractVisitor, FreExNode, VisitorComposer


class TestVisitor(AbstractVisitor):
    visited: List[str]
    name_visitor: str

    is_action: bool

    before_this: list
    after_this: list

    def __init__(
        self,
        name: str,
        *,
        before_this: list = None,
        after_this: list = None,
        is_action: bool = False
    ):
        super().__init__()
        self.visited = []
        self.is_action = is_action
        self.name_visitor = name
        self.before_this = before_this or []
        self.after_this = after_this or []

    def testing_visit(self, node: FreExNode):
        self.visited.append(node.id)
        if self.is_action:
            assert all([len(b.visited) == len(self.visited) for b in self.before_this])
            assert all(
                [len(a.visited) == (len(self.visited) - 1) for a in self.after_this]
            )
        else:
            if len(self.before_this) > 0:
                size = len(self.before_this[0].visited)
                assert all([len(b.visited) == size for b in self.before_this])

            assert all([len(b.visited) >= len(self.visited) for b in self.before_this])
            assert all([len(a.visited) == 0 for a in self.after_this])

        return True


def test_simple_composition_visitor_before_action(valid_basic_execution_graph):
    visit_before_a = TestVisitor("a")
    visit_before_b = TestVisitor("b", before_this=[visit_before_a])
    visit_before_c = TestVisitor("c", before_this=[visit_before_a, visit_before_b])
    visit_before_d = TestVisitor(
        "d", before_this=[visit_before_a, visit_before_b, visit_before_c]
    )
    visit_before_a.after_this = [visit_before_b, visit_before_c, visit_before_d]
    visit_before_b.after_this = [visit_before_c, visit_before_d]
    visit_before_c.after_this = [visit_before_d]

    all_before = [visit_before_a, visit_before_b, visit_before_c, visit_before_d]
    action = TestVisitor("action_1", is_action=True)

    visitor_composed = VisitorComposer([action], before=all_before)
    visitor_composed.visit(valid_basic_execution_graph.root)


def test_simple_composition_visitor_action_after(valid_basic_execution_graph):
    visit_after_a = TestVisitor("a")
    visit_after_b = TestVisitor("b", before_this=[visit_after_a])
    visit_after_c = TestVisitor("c", before_this=[visit_after_a, visit_after_b])
    visit_after_d = TestVisitor(
        "d", before_this=[visit_after_a, visit_after_b, visit_after_c]
    )
    visit_after_a.after_this = [visit_after_b, visit_after_c, visit_after_d]
    visit_after_b.after_this = [visit_after_c, visit_after_d]
    visit_after_c.after_this = [visit_after_d]

    all_after = [visit_after_a, visit_after_b, visit_after_c, visit_after_d]
    action = TestVisitor("action_1", is_action=True)

    visitor_composed = VisitorComposer([action], after=all_after)
    visitor_composed.visit(valid_basic_execution_graph.root)


def test_simple_composition_visitor_before_after(valid_basic_execution_graph):
    visit_before_a = TestVisitor("a")
    visit_before_b = TestVisitor("b", before_this=[visit_before_a])
    visit_before_c = TestVisitor("c", before_this=[visit_before_a, visit_before_b])
    visit_before_d = TestVisitor(
        "d", before_this=[visit_before_a, visit_before_b, visit_before_c]
    )
    visit_after_a = TestVisitor("a")
    visit_before_a.after_this = [visit_before_b, visit_before_c, visit_before_d]
    visit_before_b.after_this = [visit_before_c, visit_before_d]
    visit_before_c.after_this = [visit_before_d]
    visit_after_b = TestVisitor("b", before_this=[visit_after_a])
    visit_after_c = TestVisitor("c", before_this=[visit_after_a, visit_after_b])
    visit_after_d = TestVisitor(
        "d", before_this=[visit_after_a, visit_after_b, visit_after_c]
    )
    visit_after_a.after_this = [visit_after_b, visit_after_c, visit_after_d]
    visit_after_b.after_this = [visit_after_c, visit_after_d]
    visit_after_c.after_this = [visit_after_d]

    all_after = [visit_after_a, visit_after_b, visit_after_c, visit_after_d]
    all_before = [visit_before_a, visit_before_b, visit_before_c, visit_before_d]
    action = TestVisitor("action_1", is_action=True)

    visitor_composed = VisitorComposer([action], before=all_before, after=all_after)
    visitor_composed.visit(valid_basic_execution_graph.root)


def test_composition_multi_action(valid_basic_execution_graph):
    visit_action_a = TestVisitor("a", is_action=True)
    visit_action_b = TestVisitor("b", before_this=[visit_action_a], is_action=True)
    visit_action_c = TestVisitor(
        "c", before_this=[visit_action_a, visit_action_b], is_action=True
    )
    visit_action_d = TestVisitor(
        "d",
        before_this=[visit_action_a, visit_action_b, visit_action_c],
        is_action=True,
    )
    visit_action_a.after_this = [visit_action_b, visit_action_c, visit_action_d]
    visit_action_b.after_this = [visit_action_c, visit_action_d]
    visit_action_c.after_this = [visit_action_d]

    all_action = [visit_action_a, visit_action_b, visit_action_c, visit_action_d]
    visitor_composed = VisitorComposer(all_action)
    visitor_composed.visit(valid_basic_execution_graph.root)


def test_composition_before_multi_action(valid_basic_execution_graph):
    visit_action_a = TestVisitor("a", is_action=True)
    visit_action_b = TestVisitor("b", before_this=[visit_action_a], is_action=True)
    visit_action_c = TestVisitor(
        "c", before_this=[visit_action_a, visit_action_b], is_action=True
    )
    visit_action_d = TestVisitor(
        "d",
        before_this=[visit_action_a, visit_action_b, visit_action_c],
        is_action=True,
    )
    visit_action_a.after_this = [visit_action_b, visit_action_c, visit_action_d]
    visit_action_b.after_this = [visit_action_c, visit_action_d]
    visit_action_c.after_this = [visit_action_d]
    visit_before_a = TestVisitor("a")
    visit_before_b = TestVisitor("b", before_this=[visit_before_a])
    visit_before_c = TestVisitor("c", before_this=[visit_before_a, visit_before_b])
    visit_before_d = TestVisitor(
        "d", before_this=[visit_before_a, visit_before_b, visit_before_c]
    )
    visit_before_a.after_this = [visit_before_b, visit_before_c, visit_before_d]
    visit_before_b.after_this = [visit_before_c, visit_before_d]
    visit_before_c.after_this = [visit_before_d]

    all_before = [visit_before_a, visit_before_b, visit_before_c, visit_before_d]
    all_action = [visit_action_a, visit_action_b, visit_action_c, visit_action_d]

    visitor_composed = VisitorComposer(all_action, before=all_before)
    visitor_composed.visit(valid_basic_execution_graph.root)


def test_complete_composition(valid_complex_graph):
    visit_action_a = TestVisitor("a", is_action=True)
    visit_action_b = TestVisitor("b", before_this=[visit_action_a], is_action=True)
    visit_action_c = TestVisitor(
        "c", before_this=[visit_action_a, visit_action_b], is_action=True
    )
    visit_action_d = TestVisitor(
        "d",
        before_this=[visit_action_a, visit_action_b, visit_action_c],
        is_action=True,
    )
    visit_action_a.after_this = [visit_action_b, visit_action_c, visit_action_d]
    visit_action_b.after_this = [visit_action_c, visit_action_d]
    visit_action_c.after_this = [visit_action_d]
    visit_before_a = TestVisitor("a")
    visit_before_b = TestVisitor("b", before_this=[visit_before_a])
    visit_before_c = TestVisitor("c", before_this=[visit_before_a, visit_before_b])
    visit_before_d = TestVisitor(
        "d", before_this=[visit_before_a, visit_before_b, visit_before_c]
    )
    visit_before_a.after_this = [visit_before_b, visit_before_c, visit_before_d]
    visit_before_b.after_this = [visit_before_c, visit_before_d]
    visit_before_c.after_this = [visit_before_d]
    visit_after_a = TestVisitor("a")
    visit_after_b = TestVisitor("b", before_this=[visit_after_a])
    visit_after_c = TestVisitor("c", before_this=[visit_after_a, visit_after_b])
    visit_after_d = TestVisitor(
        "d", before_this=[visit_after_a, visit_after_b, visit_after_c]
    )
    visit_after_a.after_this = [visit_after_b, visit_after_c, visit_after_d]
    visit_after_b.after_this = [visit_after_c, visit_after_d]
    visit_after_c.after_this = [visit_after_d]

    all_after = [visit_after_a, visit_after_b, visit_after_c, visit_after_d]
    all_before = [visit_before_a, visit_before_b, visit_before_c, visit_before_d]
    all_action = [visit_action_a, visit_action_b, visit_action_c, visit_action_d]

    visitor_composed = VisitorComposer(
        all_action, before=all_before, after=all_after, progress_bar_on_actions=True
    )
    visitor_composed.visit(valid_complex_graph.root)
