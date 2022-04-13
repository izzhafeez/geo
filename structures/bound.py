from __future__ import annotations
from ..geometry.pt import Pt
from shapely import geometry

class Bound:
    min_x: float
    max_x: float
    min_y: float
    max_y: float

    def __init__(self, min_x: float, max_x: float, min_y: float, max_y: float):
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

    def __str__(self) -> str:
        return f"x({self.min_x}, {self.max_x}), y({self.min_y}, {self.max_y})"
    
    def merge_with(self, bound: Bound) -> None:
        self.min_x = min(self.min_x, bound.min_x)
        self.max_x = max(self.max_x, bound.max_x)
        self.min_y = min(self.min_y, bound.min_y)
        self.max_y = max(self.max_y, bound.max_y)
    
    def contains(self, point: Pt) -> bool:
        return (point.x >= self.min_x
                and point.x <= self.max_x
                and point.y >= self.min_y
                and point.y <= self.max_y)

    @property
    def center(self) -> Pt:
        return Pt((self.max_x+self.min_x)/2, (self.max_y+self.min_y)/2)

    @staticmethod
    def get_bound_from_shape(shape: geometry.polygon.Polygon) -> Bound:
        if hasattr(shape, "points"):
            return Bound(shape.points.bound.min_x,
                         shape.points.bound.max_x,
                         shape.points.bound.min_y,
                         shape.points.bound.max_y)
        else:
            return Bound(shape.bounds[0],
                         shape.bounds[2],
                         shape.bounds[1],
                         shape.bounds[3])

    