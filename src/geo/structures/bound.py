from __future__ import annotations
from typing import Generic, get_args, Tuple, TypeVar

import shapely.geometry

from geom.pointable import Pointable

T = TypeVar("T", bound=Pointable)

class Bound(Generic[T]):
    """
    Encapsulates a rectangular box, possessing coordinates for each of its sides.

    Fields:
        min_x (float): left bound of the rectangular box.
        max_x (float): right bound of the rectangular box.
        min_y (float): top bound of the rectangular box.
        max_y (float): bottom bound of the rectangular box.
    """
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
    
    def merge_with(self, bound: Bound[T]) -> None:
        """
        Merges two bounds together, such that the new bound contains both bounds.

        Args:
            bound (Bound): the bound to be added.
        """
        self.min_x = min(self.min_x, bound.min_x)
        self.max_x = max(self.max_x, bound.max_x)
        self.min_y = min(self.min_y, bound.min_y)
        self.max_y = max(self.max_y, bound.max_y)
        
    @property
    def center(self) -> Tuple[float, float]:
        return ((self.max_x+self.min_x)/2, (self.max_y+self.min_y)/2)
    
    def contains(self, point: T) -> bool:
        """
        Checks whether a point lies within this bound.

        Args:
            point (T): point to be queried.

        Returns:
            bool: whether the point lies within the bound.
        """
        return (point.x >= self.min_x
                and point.x <= self.max_x
                and point.y >= self.min_y
                and point.y <= self.max_y)

    @staticmethod
    def get_bound_from_shape(shape: shapely.geometry.polygon.Polygon) -> Bound:
        """
        Converts a shape into a Bound.

        Args:
            shape (geometry.polygon.Polygon): shape to be converted into bound.

        Returns:
            Bound: the bounds of the shape.
        """
        return Bound[T](shape.bounds[0],
                        shape.bounds[2],
                        shape.bounds[1],
                        shape.bounds[3])

    