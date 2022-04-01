from __future__ import annotations
from ..geometry.pt import Pt
from functools import cached_property
from typing import List, Tuple

class XY:
    X, Y = "x", "y"

class KDNode:
    point: Pt
    level: str
    left: KDNode
    right: KDNode

    def __init__(self, point: Pt, level: str):
        self.point = point
        self.level = level
        self.left = None
        self.right = None
        
    @cached_property
    def next_level(self) -> str:
        if self.level == XY.X:
            return XY.Y
        else:
            return XY.X
        
    def add(self, point: Pt) -> None:
        if getattr(point, self.level) <= getattr(self.point, self.level):
            if self.left == None:
                self.left = KDNode(point, self.next_level)
                return self.left
            else:
                self.left.add(point)
        else:
            if self.right == None:
                self.right = KDNode(point, self.next_level)
                return self.right
            else:
                self.right.add(point)
                
    def nearest(self, point: Pt) -> Tuple[Pt, float]:
        next_branch: KDNode
        other_branch: KDNode
        temp: Pt

        next_branch, other_branch = self._get_next_other_branch(point)
        temp = KDNode._get_temp_point(next_branch, point)
        return self._backtrack(point, temp, other_branch)

    def _get_next_other_branch(self, point: Pt) -> Tuple[KDNode, KDNode]:
        if getattr(point, self.level) < getattr(self.point, self.level):
            return (self.left, self.right)
        else:
            return (self.right, self.left)

    def _get_temp_point(next_branch: KDNode, point: Pt) -> Pt:
        if next_branch != None:
            return next_branch.nearest(point)[0]
        else:
            return Pt(float("inf"), float("inf"))

    def _backtrack(self, point: Pt, temp: Pt, other_branch: KDNode) -> Tuple[Pt, float]:
        best: Pt
        best_d: float
        s_d: float

        best, best_d = point.get_closest_point(temp, self.point)
        s_d = abs(getattr(point, self.level) - getattr(self.point, self.level))
        if best_d >= s_d and other_branch != None:
            temp = other_branch.nearest(point)[0]
            best, best_d = point.get_closest_point(temp, best)
        
        return (best, best_d)

class KDTree:
    root: KDNode
    weight: int
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def __init__(self) -> None:
        self.root = None
        self.weight = 0
        self.min_x = float("inf")
        self.max_x = float("-inf")
        self.min_y = float("inf")
        self.max_y = float("-inf")

    def __str__(self) -> str:
        return str(self.in_order())

    def __repr__(self) -> str:
        return f"<KDTree: x({self.min_x}, {self.max_x}), y({self.min_y}, {self.max_y})>"
    
    def add_all(self, *points: Pt) -> None:
        if self.root == None:
            self.root = KDNode(points[0], XY.X)
            points = points[1:]
            self.weight += 1
            
        for point in points:
            self._remap_min_max(point)
            self.root.add(point)
            self.weight += 1
    
    def add(self, point: Pt) -> KDNode:
        if self.root == None:
            self.root = KDNode(point, XY.X)
            self.weight += 1
            return self.root
        self._remap_min_max(point)
        self.weight += 1
        return self.root.add(point)

    def _remap_min_max(self, point: Pt) -> None:
        self.min_x = min(self.min_x, point.x)
        self.min_y = min(self.min_y, point.y)
        self.max_x = max(self.max_x, point.x)
        self.max_y = max(self.max_y, point.y)
        
    def nearest(self, point: Pt) -> Tuple[Pt, float]:
        if self.root == None:
            return None
        return self.root.nearest(point)

    @property
    def center(self) -> Pt:
        return Pt((self.max_x+self.min_x)/2, (self.max_y+self.min_y)/2)

    def in_order(self) -> List[Pt]:
        L: List[Pt] = []
        def in_order_helper(node: KDNode):
            if not node:
                return None
            in_order_helper(node.left)
            L.append(node.point)
            in_order_helper(node.right)
        in_order_helper(self.root)
        return L

    def pre_order(self) -> List[Pt]:
        L: List[Pt] = []
        def pre_order_helper(node: KDNode):
            if not node:
                return None
            else:
                L.append(node.point)
                pre_order_helper(node.left)
                pre_order_helper(node.right)
        pre_order_helper(self.root)
        return L
           