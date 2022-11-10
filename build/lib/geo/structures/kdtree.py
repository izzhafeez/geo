from __future__ import annotations
from functools import cached_property
from typing import List, Generic, Optional, Tuple, TypeVar

from .bound import Bound
from .quick_sort import median_with_left_right
from ..geom.pointable import Pointable

T = TypeVar("T", bound=Pointable)

class XY:
    X, Y = "x", "y"

class KDNode(Generic[T]):
    """
    Encapsulates a node in a KDTree.

    Fields:
        point (T): the point it is representing in the tree.
        level (str): whether the we compare x or y-values at this point.
            (We alternate between x and y).
        left (Optional[KDNode[T]]): the left child of this node.
        right (Optional[KDNode[T]]): the right child of this node.
    """
    point: T
    level: str
    left:  Optional[KDNode[T]]
    right: Optional[KDNode[T]]

    def __init__(self, point: T, level: str):
        """
        Initialiser for the KDNode[T] object.
        The left and right children are both set to zero
            as this node would be considered as a leaf.

        Args:
            point (T): point to be represented by the node.
            level (str): 'x' or 'y'.
        """
        self.point = point
        self.level = level
        self.left = None
        self.right = None
        
    @cached_property
    def next_level(self) -> str:
        """
        Computes the next level of this node.
        So, 'x' will be mapped to 'y' and vice versa.
        This helps to eliminate the need for if statements when traversing the tree.

        Returns:
            str: 'x' or 'y' value.
        """
        if self.level == XY.X:
            return XY.Y
        else:
            return XY.X
        
    def add(self, point: T) -> None:
        """
        Adds the point to the node.
        If there is a vacancy, the point will join the tree as a new node.
        Otherwise, the point will be passed on to the relevant child's add method.

        Args:
            point (T): the point to be added to the node.
        """
        if getattr(point, self.level) <= getattr(self.point, self.level):
            if self.left == None:
                self.left = KDNode[T](point, self.next_level)
            else:
                self.left.add(point)
        else:
            if self.right == None:
                self.right = KDNode[T](point, self.next_level)
            else:
                self.right.add(point)
                
    def nearest(self, point: T) -> Tuple[Optional[T], float]:
        """
        Gets the nearest point to a particular target point.

        Args:
            point (T): target point.

        Returns:
            Tuple[Optional[T], float]: point-distance tuple.
        """
        next_branch:  Optional[KDNode[T]]
        other_branch: Optional[KDNode[T]]
        temp: Optional[T]

        next_branch, other_branch = self._get_next_other_branch(point)
        temp = self._get_temp_point(next_branch, point)
        return self._backtrack(point, temp, other_branch)

    def _get_next_other_branch(self, point: Pointable) -> Tuple[Optional[KDNode[T]], Optional[KDNode[T]]]:
        """
        There is no guarantee that the deepest node in the tree is the closest point.
        As such, we need to do checks on some sibling nodes we encounter along the way.
        This method returns two nodes, the first one being the more important branch,
            which we will traverse all the way.
        For the other branch, we would only need to check its root node.

        Args:
            point (Pointable): target point.

        Returns:
            Tuple[Optional[KDNode[T]], Optional[KDNode[T]]]: roots of the two child branches.
        """
        if getattr(point, self.level) < getattr(self.point, self.level):
            return (self.left, self.right)
        else:
            return (self.right, self.left)

    def _get_temp_point(self, next_branch: Optional[KDNode[T]], point: T) -> Optional[T]:
        """
        Processes the 'next_branch' to return a node if it exists.

        Args:
            next_branch (Optional[KDNode[T]]): branch to process.
            point (T): target point.

        Returns:
            Optional[T]: a point if it exists.
        """
        if next_branch is not None:
            return next_branch.nearest(point)[0]
        else:
            return None

    def _backtrack(self, point: T, temp: Optional[T], other_branch: Optional[KDNode[T]]) -> Tuple[Optional[T], float]:
        """
        This method computes distances to all the other nodes that we have KIVed.
        The minimum distance is the one that we output.

        Args:
            point (T): target point.
            temp (Optional[T]): current closest point to target.
            other_branch (Optional[KDNode[T]]): other branch to check for closest point.

        Returns:
            Tuple[Optional[Pointable], float]: point-distance tuple.
        """
        best:   Optional[T]
        best_d: float
        s_d:    float

        best, best_d = point.get_closest_point(*[temp, self.point])
        s_d = abs(getattr(point, self.level) - getattr(self.point, self.level))

        if best_d >= s_d and other_branch is not None:
            temp = other_branch.nearest(point)[0]
            best, best_d = point.get_closest_point(*[temp, best])# if temp and best else (None, float("inf"))

        return (best, best_d)

class KDTree(Generic[T]):
    """
    Encapsulates a KDTree object, containing many KDNode[T]s.
    At each depth level, we compare alternating coordinates, starting with x.
    
    Fields:
        root (Optional[KDNode[T]]): the root of the tree.
        weight (int): the number of nodes in the tree.
        bound (Bound): the bounds that contain the entire collection of points.
    """
    root: Optional[KDNode[T]]
    weight: int
    bound: Bound[T]

    def __init__(self):
        """
        Initialiser for an empty KDTree.
        Sets the root to be empty, weight to be 0 and bounds to be infinite.
        """
        self.root = None
        self.weight = 0
        self.bound = Bound(float("inf"), float("-inf"), float("inf"), float("-inf"))

    def __str__(self) -> str:
        return str(self.in_order())

    def __repr__(self) -> str:
        return f"<KDTree: {self.bound}>"

    @property
    def center(self) -> Tuple[float, float]:
        """
        Based on the bounds of the KDTree, return its center point.

        Returns:
            T: center of the KDTree.
        """
        return self.bound.center

    def add_all(self, *points: T) -> None:
        """
        From a collection of points, add all of them to the tree.
        It will check whether the root is None (assign root to this new node then).
        If not None, then the point will be added to the tree's root, and passed along there.
        Weights are also updated.
        
        Args:
            *points (T): the points to be added to the tree.
        """
        sorted_points: List[T] = []
        def append_median(_list: List[T], xy: str) -> None:
            if len(_list) == 0:
                return
            left, mid, right = median_with_left_right(_list, comparator=lambda point: getattr(point, xy))
            if mid is not None:
                sorted_points.append(mid)
            if xy == "x":
                append_median(left, "y")
                append_median(right, "y")
            else:
                append_median(left, "x")
                append_median(right, "x")
        append_median(list(points), "x")
        
        if not self.root:
            self.root = KDNode[T](sorted_points.pop(0), "x")
            self.weight += 1
            
        for point in sorted_points:
            self._remap_min_max(point)
            self.root.add(point)
            self.weight += 1

    def _remap_min_max(self, point: T) -> None:
        """
        Updates the bounds of the KDTree, expanding if a point lies outside of it.

        Args:
            point (T): point to be added.
        """
        self.bound.min_x = min(self.bound.min_x, point.x)
        self.bound.min_y = min(self.bound.min_y, point.y)
        self.bound.max_x = max(self.bound.max_x, point.x)
        self.bound.max_y = max(self.bound.max_y, point.y)
        
    def nearest(self, point: T) -> Tuple[Optional[T], float]:
        """
        Finds the nearest point to the target.
        The code passes the 'point' argument to the root, and lets the nodes handle it.
        If an answer is unavailable, return (None, float('inf'))

        Args:
            point (T): point to be queried.

        Returns:
            Tuple[Optional[T], float]: point-distance tuple.
        """
        if self.root == None:
            return (None, float("inf"))
        return self.root.nearest(point)

    def in_order(self) -> List[T]:
        """
        In order traversal of the tree done by recursion.

        Returns:
            List[T]: a list of points in the tree.
        """
        L: List[T] = []
        def in_order_helper(node: Optional[KDNode[T]]) -> None:
            if not node:
                return None
            in_order_helper(node.left)
            L.append(node.point)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L

    def pre_order(self) -> List[Pointable]:
        """
        Pre order traversal of the tree done by recursion.

        Returns:
            List[Pointable]: a list of points in the tree.
        """
        L: List[Pointable] = []
        def pre_order_helper(node: Optional[KDNode[T]]) -> None:
            if not node:
                return None
            L.append(node.point)
            pre_order_helper(node.left)
            pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
           