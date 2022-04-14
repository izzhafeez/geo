from __future__ import annotations
from functools import cached_property
from typing import List, Optional, Tuple

from .bound import Bound
from ..geometry.pt import GeoPt


class XY:
    X, Y = "x", "y"

class KDNode:
    """
    Encapsulates a node in a KDTree.

    Fields:
        point (GeoPt): the point it is representing in the tree.
        level (str): whether the we compare x or y-values at this point.
            (We alternate between x and y).
        left (Optional[KDNode]): the left child of this node.
        right (Optional[KDNode]): the right child of this node.
    """
    point: GeoPt
    level: str
    left:  Optional[KDNode]
    right: Optional[KDNode]

    def __init__(self, point: GeoPt, level: str):
        """
        Initialiser for the KDNode object.
        The left and right children are both set to zero
            as this node would be considered as a leaf.

        Args:
            point (GeoPt): point to be represented by the node.
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
        
    def add(self, point: GeoPt) -> None:
        """
        Adds the point to the node.
        If there is a vacancy, the point will join the tree as a new node.
        Otherwise, the point will be passed on to the relevant child's add method.

        Args:
            point (GeoPt): the point to be added to the node.
        """
        if getattr(point, self.level) <= getattr(self.point, self.level):
            if self.left == None:
                self.left = KDNode(point, self.next_level)
            else:
                self.left.add(point)
        else:
            if self.right == None:
                self.right = KDNode(point, self.next_level)
            else:
                self.right.add(point)
                
    def nearest(self, point: GeoPt) -> Tuple[Optional[GeoPt], float]:
        """
        Gets the nearest point to a particular target point.

        Args:
            point (GeoPt): target point.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance tuple.
        """
        next_branch:  Optional[KDNode]
        other_branch: Optional[KDNode]
        temp: Optional[GeoPt]

        next_branch, other_branch = self._get_next_other_branch(point)
        temp = self._get_temp_point(next_branch, point)
        return self._backtrack(point, temp, other_branch)

    def _get_next_other_branch(self, point: GeoPt) -> Tuple[Optional[KDNode], Optional[KDNode]]:
        """
        There is no guarantee that the deepest node in the tree is the closest point.
        As such, we need to do checks on some sibling nodes we encounter along the way.
        This method returns two nodes, the first one being the more important branch,
            which we will traverse all the way.
        For the other branch, we would only need to check its root node.

        Args:
            point (GeoPt): target point.

        Returns:
            Tuple[Optional[KDNode], Optional[KDNode]]: roots of the two child branches.
        """
        if getattr(point, self.level) < getattr(self.point, self.level):
            return (self.left, self.right)
        else:
            return (self.right, self.left)

    def _get_temp_point(self, next_branch: Optional[KDNode], point: GeoPt) -> Optional[GeoPt]:
        """
        Processes the 'next_branch' to return a node if it exists.

        Args:
            next_branch (Optional[KDNode]): branch to process.
            point (GeoPt): target point.

        Returns:
            Optional[GeoPt]: a point if it exists.
        """
        if next_branch is not None:
            return next_branch.nearest(point)[0]
        else:
            return GeoPt(float("inf"), float("inf"))

    def _backtrack(self, point: GeoPt, temp: Optional[GeoPt], other_branch: Optional[KDNode]) -> Tuple[Optional[GeoPt], float]:
        """
        This method computes distances to all the other nodes that we have KIVed.
        The minimum distance is the one that we output.

        Args:
            point (GeoPt): target point.
            temp (Optional[GeoPt]): current closest point to target.
            other_branch (Optional[KDNode]): other branch to check for closest point.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance tuple.
        """
        best:   Optional[GeoPt]
        best_d: float
        s_d:    float

        best, best_d = point.get_closest_point(temp, self.point) if temp else (None, float("inf"))
        s_d = abs(getattr(point, self.level) - getattr(self.point, self.level))
        if best_d >= s_d and other_branch is not None:
            temp = other_branch.nearest(point)[0]
            best, best_d = point.get_closest_point(temp, best) if temp and best else (None, float("inf"))
        
        return (best, best_d)

class KDTree:
    """
    Encapsulates a KDTree object, containing many KDNodes.
    At each depth level, we compare alternating coordinates, starting with x.
    
    Fields:
        root (Optional[KDNode]): the root of the tree.
        weight (int): the number of nodes in the tree.
        bound (Bound): the bounds that contain the entire collection of points.
    """
    root: Optional[KDNode]
    weight: int
    bound: Bound

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
    def center(self) -> GeoPt:
        """
        Based on the bounds of the KDTree, return its center point.

        Returns:
            GeoPt: center of the KDTree.
        """
        return self.bound.center.as_geo_pt()
    
    def add(self, point: GeoPt) -> None:
        """
        Adds a point to the KDTree.
        It will check whether the root is None (assign root to this new node then).
        If not None, then the point will be added to the tree's root, and passed along there.
        Weights are also updated.

        Args:
            point (GeoPt): point to be added to the tree.
        """
        if not self.root:
            self.root = KDNode(point, XY.X)
            self.weight += 1
            return
        
        self._remap_min_max(point)
        self.weight += 1
        self.root.add(point)

    def add_all(self, *points: GeoPt) -> None:
        """
        From a collection of points, add all of them to the tree.
        
        Args:
            *points (GeoPt): the points to be added to the tree.
        """
        if not self.root:
            self.root = KDNode(points[0], XY.X)
            points = points[1:]
            self.weight += 1
            
        for point in points:
            self._remap_min_max(point)
            self.root.add(point)
            self.weight += 1

    def _remap_min_max(self, point: GeoPt) -> None:
        """
        Updates the bounds of the KDTree, expanding if a point lies outside of it.

        Args:
            point (GeoPt): point to be added.
        """
        self.bound.min_x = min(self.bound.min_x, point.x)
        self.bound.min_y = min(self.bound.min_y, point.y)
        self.bound.max_x = max(self.bound.max_x, point.x)
        self.bound.max_y = max(self.bound.max_y, point.y)
        
    def nearest(self, point: GeoPt) -> Tuple[Optional[GeoPt], float]:
        """
        Finds the nearest point to the target.
        The code passes the 'point' argument to the root, and lets the nodes handle it.
        If an answer is unavailable, return (None, float('inf'))

        Args:
            point (GeoPt): point to be queried.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance tuple.
        """
        if self.root == None:
            return (None, float("inf"))
        return self.root.nearest(point)

    def in_order(self) -> List[GeoPt]:
        """
        In order traversal of the tree done by recursion.

        Returns:
            List[GeoPt]: a list of points in the tree.
        """
        L: List[GeoPt] = []
        def in_order_helper(node: Optional[KDNode]) -> None:
            if not node:
                return None
            in_order_helper(node.left)
            L.append(node.point)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L

    def pre_order(self) -> List[GeoPt]:
        """
        Pre order traversal of the tree done by recursion.

        Returns:
            List[GeoPt]: a list of points in the tree.
        """
        L: List[GeoPt] = []
        def pre_order_helper(node: Optional[KDNode]) -> None:
            if not node:
                return None
            L.append(node.point)
            pre_order_helper(node.left)
            pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
           