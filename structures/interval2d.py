from __future__ import annotations
from ..geometry.pt import Pt
from ..geometry.shape import Shape
from ..structures.bound import Bound
from functools import cached_property
from typing import List, Tuple, Any, Optional
from shapely import geometry

class IntervalNode:
    shape: Optional[geometry.polygon.Polygon]
    value: Any
    bound: Bound
    big_bound: Bound
    level: str
    left: IntervalNode
    right: IntervalNode

    def __init__(self, shape: geometry.polygon.Polygon, value: Any, level: str):
        self.shape = shape
        self.value = value
        self.bound = Bound.get_bound_from_shape(shape)
        self.big_bound = self.bound
        self.level = level
        self.left = None
        self.right = None

    @cached_property
    def next_level(self) -> str:
        level_mapping = {"min_x": "min_y",
                         "min_y": "max_x",
                         "max_x": "max_y",
                         "max_y": "min_x",}
        return level_mapping[self.level]

    def add(self, shape: geometry.polygon.Polygon, value: Any=None) -> None:
        bound: Bound = Bound.get_bound_from_shape(shape)
        self.big_bound.merge_with(bound)
        if getattr(bound, self.level) <= getattr(self.bound, self.level):
            if self.left == None:
                self.left = IntervalNode(shape, value, self.next_level)
                return self.left
            else:
                self.left.add(shape, value)
        else:
            if self.right == None:
                self.right = IntervalNode(shape, value, self.next_level)
                return self.right
            else:
                self.right.add(shape, value)

class IntervalTree:
    root: IntervalNode
    weight: int
    big_bound: Bound

    def __init__(self):
        self.root = None
        self.weight = 0
        self.big_bound = Bound(float("inf"), float("-inf"), float("inf"), float("-inf"))

    def __str__(self) -> str:
        return str(self.in_order())

    def __repr__(self) -> str:
        return f"<IntervalTree: {self.big_bound}>"

    def add_all(self, shapes: List[geometry.polygon.Polygon], values: List[Any]) -> None:
        if self.root == None:
            self.root = IntervalNode(shapes[0], values[0], "min_x")
            shapes = shapes[1:]
            values = values[1:]
            self.weight += 1
            
        for shape, value in zip(shapes, values):
            self.root.add(shape, value)
            self.weight += 1

    def add(self, shape: geometry.polygon.Polygon, value: Any) -> IntervalNode:
        if self.root == None:
            self.root = IntervalNode(shape, value, "min_x")
            self.weight += 1
            return self.root

        self.big_bound.merge_with(Bound.get_bound_from_shape(shape))
        self.weight += 1
        return self.root.add(shape, value)

    def find_bounds_containing(self, point: Pt) -> List[Bound]:
        L: List[Bound] = []
        def find_bounds_containing_helper(node: IntervalNode) -> None:
            if not node.big_bound.contains(point):
                return
            L.append(node.bound)
            find_bounds_containing_helper(node.left)
            find_bounds_containing_helper(node.right)
        find_bounds_containing_helper(self.root)
        return L

    def find_shape(self, point: Pt) -> Any:
        value: List[Any] = [None]
        def find_shape_helper(node: IntervalNode) -> None:
            if not node:
                return
            if not node.big_bound.contains(point):
                return
            if not node.shape.contains(point):
                find_shape_helper(node.left)
                find_shape_helper(node.right)
                return
            value[0] = node.value
        find_shape_helper(self.root)
        return value[0]


    def in_order(self) -> List[Pt]:
        L: List[Bound] = []
        def in_order_helper(node: IntervalNode) -> None:
            if not node:
                return
            in_order_helper(node.left)
            L.append(node.bound)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L

    def pre_order(self) -> List[Pt]:
        L: List[Bound] = []
        def pre_order_helper(node: IntervalNode) -> None:
            if not node:
                return
            L.append(node.bound)
            pre_order_helper(node.left)
            pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
    