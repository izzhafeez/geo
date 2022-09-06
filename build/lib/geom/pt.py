from __future__ import annotations
from typing import List, Optional, Tuple

import shapely.geometry

from geom.pointable import Pointable
from structures.bound import Bound
import geom.geo_pt

class Pt(shapely.geometry.Point, Pointable):
    """
    Object encapsulating a point, facilitating distance computation.
    
    Fields:
        x (float): x-coordinate for the point.
        y (float): y-coordinate for the point.
    """

    def __init__(self, x: float, y: float) -> None:
        """
        Initialiser for the Pt object.

        Args:
            x (float): x-coordinate for the point.
            y (float): y-coordinate for the point.
        """
        super().__init__(x, y)

    def __str__(self) -> str:
        return f"PT ({self.x}, {self.y})"
        
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"
    
    @property
    def x(self) -> float:
        return self.x
    
    @property
    def y(self) -> float:
        return self.y

    @staticmethod
    def from_bound(bound: Bound[Pt]) -> Pt:
        return Pt((bound.max_x+bound.min_x)/2, (bound.max_y+bound.min_y)/2)

    @staticmethod
    def from_point(point: shapely.geometry.Point) -> Pt:
        """
        Factory method that converts a geometry.Point object into a Pt object.

        Args:
            point (geometry.Point): point to be converted into Pt object.

        Returns:
            Pt: the returned Pt object.
        """
        return Pt(point.x, point.y)

    def as_geo_pt(self) -> geom.geo_pt.GeoPt:
        """
        Converts the Pt into a GeoPt object.

        Returns:
            GeoPt: the converted point.
        """
        return geom.geo_pt.GeoPt(self.y, self.x)

    def coords_as_tuple_xy(self) -> Tuple[float, float]:
        """
        Converts the point into an x-y tuple

        Returns:
            Tuple[float, float]: x-y coordinate tuple.
        """
        return (self.x, self.y)

    def coords_as_tuple_yx(self) -> Tuple[float, float]:
        """
        Converts the point into a y-x tuple

        Returns:
            Tuple[float, float]: y-x coordinate tuple.
        """
        return (self.y, self.x)

    def get_distance(self, point: Pt) -> float:
        """
        Computes the distance to another Pt object.
        Does not allow computing distance to GeoPt objects as they involve different computations.

        Args:
            point (Pt): target point to be computed.

        Raises:
            TypeError: a GeoPt was sent in as the point argument.

        Returns:
            float: distance, in units, to the target point.
        """
        if isinstance(point, Pt):
            raise TypeError("Cannot be GeoPt!")
        return ((self.y-point.y)**2+(self.x-point.x)**2)**0.5
    
    def get_closest_point(self, *points: Pt) -> Tuple[Optional[Pt], float]:
        """
        Based on a collection of points, find the nearest to self.
        
        Args:
            *points (Pt): we will find the closest of these points to self.

        Returns:
            Tuple[Optional[Pt], float]: point-distance tuple.
        """
        nearest_point = None
        nearest_dist = float("inf")
        for point in points:
            dist = self.get_distance(point)
            if nearest_dist > dist:
                nearest_dist = dist
                nearest_point = point
        return (nearest_point, nearest_dist)

    def move_to(self, new_x: float, new_y: float) -> Pt:
        return Pt(new_x, new_y)