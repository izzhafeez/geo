from __future__ import annotations
from shapely import geometry
from .distance import DistanceCalculator
from typing import Tuple, List

class Pt(geometry.Point):
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)

    def __str__(self) -> str:
        return f"PT ({self.x}, {self.y})"
        
    def __repr__(self) -> str:
        return f"({self.x}, {self.y})"

    def get_distance(self, point: Pt) -> float:
        if isinstance(point, GeoPt):
            raise TypeError("Cannot be GeoPt!")
        return ((self.y-point.y)**2+(self.x-point.x)**2)**0.5
    
    def get_closest_point(self, *points: List[Pt]) -> Tuple[Pt, float]:
        nearest_point = None
        nearest_dist = float("inf")
        for point in points:
            dist = self.get_distance(point)
            if nearest_dist > dist:
                nearest_dist = dist
                nearest_point = point
        return (nearest_point, nearest_dist)

    def coords_as_tuple_xy(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def coords_as_tuple_yx(self) -> Tuple[float, float]:
        return (self.y, self.x)

class GeoPt(Pt):
    lat: float
    lon: float

    def __init__(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        super().__init__(lon, lat)
    
    def __str__(self) -> str:
        return f"GEOPT ({self.lat}, {self.lon})"
        
    def __repr__(self) -> str:
        return f"({self.lat}, {self.lon})"
    
    def get_distance(self, point: Pt) -> float:
        if isinstance(point, GeoPt):
            return DistanceCalculator.get_distance(self, point)
        raise TypeError("Must be a GeoPt!")
        
    def get_distance_basic(self, point: GeoPt) -> float:
        return ((self.y-point.y)**2+(self.x-point.x)**2)**0.5
    
    def get_closest_point(self, *points: List[Pt]) -> Tuple[GeoPt, float]:
        nearest_point = None
        nearest_dist = float("inf")
        for point in points:
            dist = self.get_distance_basic(point)
            if nearest_dist > dist:
                nearest_dist = dist
                nearest_point = point
        return (nearest_point, self.get_distance(nearest_point))

    def coords_as_tuple_latlong(self) -> Tuple[float, float]:
        return (self.lat, self.lon)