from __future__ import annotations
from typing import Optional, Tuple

import shapely.geometry

from geom.distance import DistanceCalculator
from geom.pointable import Pointable
from structures.bound import Bound
import geom.pt

class GeoPt(shapely.geometry.Point, Pointable):
    """
    Encapsulates a point on the Earth's surface, involving different computations for distances.

    Fields:
        lat (float): latitude of the point.
        lon (float): longitude of the point.
    """
    lat: float
    lon: float

    def __init__(self, lat: float, lon: float):
        """
        Initialiser for the GeoPt method.

        Args:
            lat (float): latitude of the point.
            lon (float): longitude of the point.
        """
        self.lat = lat
        self.lon = lon
        super().__init__(lon, lat)
    
    def __str__(self) -> str:
        return f"GEOPT ({self.lat}, {self.lon})"
        
    def __repr__(self) -> str:
        return f"({self.lat}, {self.lon})"
    
    @property
    def x(self) -> float:
        return self.lon
    
    @property
    def y(self) -> float:
        return self.lat
    
    @staticmethod
    def from_bound(bound: Bound[GeoPt]) -> GeoPt:
        return GeoPt((bound.max_y+bound.min_y)/2, (bound.max_x+bound.min_x)/2)
    
    @staticmethod
    def from_point(point: shapely.geometry.Point) -> GeoPt:
        """
        Factory method that converts a geometry.Point object into a GeoPt object.

        Args:
            point (geometry.Point): point to be converted into GeoPt object.

        Returns:
            GeoPt: the returned GeoPt object.
        """
        return GeoPt(point.y, point.x)
    
    def as_pt(self) -> geom.pt.Pt:
        """
        Converts the GeoPt into a Pt object.

        Returns:
            Pt: the returned Pt.
        """
        return geom.pt.Pt(self.x, self.y)
    
    def coords_as_tuple_latlong(self) -> Tuple[float, float]:
        """
        Converts the point into a lat-long coordinate tuple.

        Returns:
            Tuple[float, float]: lat-long coordinate tuple.
        """
        return (self.lat, self.lon)
    
    def get_distance(self, point: GeoPt) -> float:
        """
        Computes the distance to another GeoPt object.
        Does not allow computing distance to Pt objects as they involve different computations.

        Args:
            point (GeoPt): target point to be computed.

        Raises:
            TypeError: a Pt was sent in as the point argument.

        Returns:
            float: distance, in metres, to the target point.
        """
        if hasattr(point, "lat"):
            return DistanceCalculator.get_distance(self, point)
        raise TypeError("Must be a GeoPt!")
        
    def get_distance_basic(self, point: GeoPt) -> float:
        """
        Computes an approximate distance between the two geo points.
        More accurate when distances are small, will be less accurate as the distance increase.
        This is used mainly for comparing distances, instead of acting as the final result.

        Args:
            point (GeoPt): target point to be computed.

        Returns:
            float: approximate distance, in units.
        """
        return 10000*((self.y-point.y)**2+(self.x-point.x)**2)**0.5
    
    def get_closest_point(self, *points: Optional[GeoPt]) -> Tuple[Optional[GeoPt], float]:
        """
        Based on a collection of points, find the nearest to self.
        
        Args:
            *points (Optional[GeoPt]): we will find the closest of these points to self.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance tuple.
        """
        nearest_point = None
        nearest_dist = float("inf")
        for point in points:
            if point is not None:
                dist = self.get_distance_basic(point)
                if nearest_dist > dist:
                    nearest_dist = dist
                    nearest_point = point
        if not nearest_point:
            return (None, nearest_dist)
        return (nearest_point, self.get_distance(nearest_point))
    
    def move_to(self, new_x: float, new_y: float) -> GeoPt:
        return GeoPt(new_y, new_x)