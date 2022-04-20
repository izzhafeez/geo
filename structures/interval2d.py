from __future__ import annotations
from functools import cached_property
from typing import Any, Generic, List, Optional, TypeVar

from shapely import geometry

from geom.pt import Pt
from structures.bound import Bound

T = TypeVar("T")

class IntervalNode(Generic[T]):
    """
    Encapsulates a node of the IntervalTree.

    Fields:
        shape (geometry.polygon.Polygon): the shape to be represented by this node.
        value (T): any special value we want to associate with this shape.
        bound (Bound): the Bounds of this node's shape.
        big_bound (Bound): the Bounds that contains the shapes of this node as well as its descendants.
        level (str): whether we are comparing min_x, max_x, min_y, max_y.
        left (Optional[IntervalNode[T]]): the left child of the node.
        right (Optional[IntervalNode[T]]): the right child of the node.
    """
    shape:     geometry.polygon.Polygon
    value:     T
    bound:     Bound
    big_bound: Bound
    level:     str
    left:      Optional[IntervalNode[T]]
    right:     Optional[IntervalNode[T]]

    def __init__(self, shape: geometry.polygon.Polygon, value: T, level: str):
        """
        Initialiser for the IntervalNode[T] object.
        Left and right children are set to None as the node would be initialised as a leaf node.
        """
        self.shape = shape
        self.value = value
        self.bound = Bound.get_bound_from_shape(shape)
        self.big_bound = self.bound
        self.level = level
        self.left = None
        self.right = None

    @cached_property
    def next_level(self) -> str:
        """
        Based on the current level of the node, compute the next level.
        The cycle goes: min_x -> min_y -> max_x -> max_y.

        Returns:
            str: 'min_x' or 'min_y' or 'max_x' or 'max_y'
        """
        level_mapping = {"min_x": "min_y",
                         "min_y": "max_x",
                         "max_x": "max_y",
                         "max_y": "min_x",}
        return level_mapping[self.level]

    def add(self, shape: geometry.polygon.Polygon, value: T=None) -> None:
        """
        Adds a shape-value pair to the Node.
        It will create a new leaf if there is a vacancy in the right location.
        Otherwise, the arguments will be passed on to its children.

        Args:
            shape (geometry.polygon.Polygon): shape to be added.
            value (T, optional): value associated with the shape. Defaults to None.
        """
        bound: Bound = Bound.get_bound_from_shape(shape)
        self.big_bound.merge_with(bound)
        if getattr(bound, self.level) <= getattr(self.bound, self.level):
            if self.left == None:
                self.left = IntervalNode[T](shape, value, self.next_level)
            else:
                self.left.add(shape, value)
        else:
            if self.right == None:
                self.right = IntervalNode[T](shape, value, self.next_level)
            else:
                self.right.add(shape, value)

class IntervalTree(Generic[T]):
    """
    Encapsulates an IntervalTree containing many IntervalNode[T]s.
    At each depth level, we compare alternating coordinates, starting with min_x.

    Fields:
        root (Optional[IntervalNode[T]]): the root of the tree.
        weight (int): the number of nodes in the tree.
        big_bound (Bound): the Bound object containing all shapes in the tree.
    """
    root:      Optional[IntervalNode[T]]
    weight:    int
    big_bound: Bound

    def __init__(self):
        """
        Initialiser for the IntervalTree object.
        Big bound is initialised to infinity.
        """
        self.root = None
        self.weight = 0
        self.big_bound = Bound(float("inf"), float("-inf"), float("inf"), float("-inf"))

    def __str__(self) -> str:
        return str(self.in_order())

    def __repr__(self) -> str:
        return f"<IntervalTree: {self.big_bound}>"
    
    def add(self, shape: geometry.polygon.Polygon, value: T) -> None:
        """
        Adds a shape-value pair to the tree, creating a new root if it does not exist.

        Args:
            shape (geometry.polygon.Polygon): shape to be added.
            value (T): value associated with the shape.
        """
        if not self.root:
            self.root = IntervalNode[T](shape, value, "min_x")
            self.weight += 1
            return

        self.big_bound.merge_with(Bound.get_bound_from_shape(shape))
        self.weight += 1
        self.root.add(shape, value)

    def add_all(self, shapes: List[geometry.polygon.Polygon], values: List[T]) -> None:
        """
        Adds all shape-value paits to the tree.

        Args:
            shapes (List[geometry.polygon.Polygon]): list of shapes to be added.
            values (List[T]): values associated with each shape.
        """
        if self.root == None:
            self.root = IntervalNode[T](shapes[0], values[0], "min_x")
            shapes = shapes[1:]
            values = values[1:]
            self.weight += 1
            
        for shape, value in zip(shapes, values):
            self.root.add(shape, value)
            self.weight += 1

    def find_bounds_containing(self, point: Pt) -> List[Bound]:
        """
        Recursively finds all the bounds objects that contain the point.

        Args:
            point (Pt): point to be queried.

        Returns:
            List[Bound]: Bound objects that contain the point.
        """
        L: List[Bound] = []
        def find_bounds_containing_helper(node: Optional[IntervalNode[T]]) -> None:
            if not node or not node.big_bound.contains(point):
                return
            L.append(node.bound)
            find_bounds_containing_helper(node.left)
            find_bounds_containing_helper(node.right)
        find_bounds_containing_helper(self.root)
        return L

    def find_shape(self, point: Pt) -> Optional[T]:
        """
        Finds the singular shape in the tree that contains the point and returns its value.

        Args:
            point (Pt): point to be queried.

        Returns:
            T: value associated with the shape queried.
        """
        value: List[Optional[T]] = [None]
        def find_shape_helper(node: Optional[IntervalNode[T]]) -> None:
            if not node or not node.big_bound.contains(point):
                return
            if not node.shape.contains(point):
                find_shape_helper(node.left)
                find_shape_helper(node.right)
                return
            value[0] = node.value
        find_shape_helper(self.root)
        return value[0]


    def in_order(self) -> List[Bound]:
        """
        In order traversal of the tree done by recursion.

        Returns:
            List[Bound]: a list of bounds in the tree.
        """
        L: List[Bound] = []
        def in_order_helper(node: Optional[IntervalNode[T]]) -> None:
            if not node:
                return
            in_order_helper(node.left)
            L.append(node.bound)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L

    def pre_order(self) -> List[Bound]:
        """
        Pre order traversal of the tree done by recursion.

        Returns:
            List[Bound]: a list of bounds in the tree.
        """
        L: List[Bound] = []
        def pre_order_helper(node: Optional[IntervalNode[T]]) -> None:
            if not node:
                return
            L.append(node.bound)
            pre_order_helper(node.left)
            pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
    