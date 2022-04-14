from __future__ import annotations
from typing import List, Optional, Tuple

from shapely import geometry

from .distance import DistanceCalculator

class Pt(geometry.Point):
    """
    Object encapsulating a point, facilitating distance computation.
    
    Fields:
        x (float): x-coordinate for the point.
        y (float): y-coordinate for the point.
    """
    x: float
    y: float

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

    @staticmethod
    def from_point(point: geometry.Point) -> Pt:
        """
        Factory method that converts a geometry.Point object into a Pt object.

        Args:
            point (geometry.Point): point to be converted into Pt object.

        Returns:
            Pt: the returned Pt object.
        """
        return Pt(point.x, point.y)

    def as_geo_pt(self) -> GeoPt:
        """
        Converts the Pt into a GeoPt object.

        Returns:
            GeoPt: the converted point.
        """
        return GeoPt(self.y, self.x)

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
        if isinstance(point, GeoPt):
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

class GeoPt(Pt):
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
    
    def as_pt(self) -> Pt:
        """
        Converts the GeoPt into a Pt object.

        Returns:
            Pt: the returned Pt.
        """
        return Pt(self.x, self.y)
    
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
        if isinstance(point, GeoPt):
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
        return ((self.y-point.y)**2+(self.x-point.x)**2)**0.5
    
    def get_closest_point(self, *points: GeoPt) -> Tuple[Optional[GeoPt], float]:
        """
        Based on a collection of points, find the nearest to self.
        
        Args:
            *points (GeoPt): we will find the closest of these points to self.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance tuple.
        """
        nearest_point = None
        nearest_dist = float("inf")
        for point in points:
            dist = self.get_distance_basic(point)
            if nearest_dist > dist:
                nearest_dist = dist
                nearest_point = point
        if not nearest_point:
            return (None, nearest_dist)
        return (nearest_point, self.get_distance(nearest_point))

    def coords_as_tuple_latlong(self) -> Tuple[float, float]:
        """
        Converts the point into a lat-long coordinate tuple.

        Returns:
            Tuple[float, float]: lat-long coordinate tuple.
        """
        return (self.lat, self.lon)