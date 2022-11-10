from __future__ import annotations
from functools import cached_property
from typing import List, Generic, get_args, Optional, Tuple, Type, TypeVar

from shapely import geometry
from shapely.ops import nearest_points

from ..geom.geo_pt import GeoPt
from ..geom.pointable import Pointable
from ..structures.bound import Bound
from ..structures.kdtree import KDTree

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
        
    @cached_property
    def length(self) -> float:
        """
        Calculates the total length of the line.

        Returns:
            float: total length in metres.
        """
        dist = 0
        for i in range(len(self.coords)-1):
            lower = GeoPt(self.coords[i][1], self.coords[i][0])
            higher = GeoPt(self.coords[i+1][1], self.coords[i+1][0])
            dist += lower.get_distance(higher)
        return dist
        
    @staticmethod
    def from_linestring(line: geometry.LineString) -> Line[T]:
        # return Line[T]([get_args(T)[0](point.x, point.y) for point in line.coords])
        return Line[T]([GeoPt(point[1], point[0]) for point in line.coords])

    def get_nearest(self, point: T) -> Tuple[Optional[T], float]:
        """
        Gets the nearest point on the line to the point queried. Returns a point in the middle of the line.

        Args:
            point (T): the target point.

        Returns:
            Tuple[Optional[T], float]: the point-distance pair
                for the closest point from the line to the target.
        """
        nearest_point = nearest_points(self, point)[0].coords[0]
        moved_point: T = point.move_to(new_x=nearest_point[0], new_y=nearest_point[1])
        nearest_distance = moved_point.get_distance(point)
        return (moved_point, nearest_distance)
    
    def get_nearest_kd(self, point: T) -> Tuple[Optional[T], float]:
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