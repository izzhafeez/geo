from __future__ import annotations
from typing import List, Generic, get_args, Optional, Tuple, Type, TypeVar

from shapely import geometry

from geom.geo_pt import GeoPt
from geom.pointable import Pointable
from structures.bound import Bound
from structures.kdtree import KDTree

T = TypeVar("T", bound=Pointable)

class Line(geometry.LineString, Generic[T]):
    """
    This class encapsulates a Line object, with points represented
        as a KDTree to facilitate the finding of nearest points.

    Fields:
        points (KDTree): a KDTree full of points representing the Line.
    """
    points: KDTree[T]

    def __init__(self, points: List[T]):
        """
        Initialiser for the Line object.
        Creates an empty KDTree to store the points.

        Args:
            points (list): ordered list of points to be included in the line.
        """
        super().__init__(points)
        self.points = KDTree()
        self.points.add_all(*points)
        
    @staticmethod
    def from_linestring(line: geometry.LineString) -> Line[T]:
        return Line[T]([get_args(T)[0](point.x, point.y) for point in line.coords])
    
    def get_nearest(self, point: T) -> Tuple[Optional[T], float]:
        """
        Gets the nearest point on the line to the point queried.

        Args:
            point (T): the target point.

        Returns:
            Tuple[Optional[T], float]: the point-distance pair
                for the closest point from the line to the target.
        """
        return self.points.nearest(point)

    def get_bounds(self) -> Bound:
        """
        Gets the bounds of the line (min-max values for x and y).

        Returns:
            Bound: bound object that surrounds the line.
        """
        return self.points.bound