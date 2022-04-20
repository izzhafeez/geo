from __future__ import annotations
from typing import Dict, List, Optional, Tuple

from shapely import geometry
from shapely.ops import nearest_points

from geom.geo_pt import GeoPt
from geom.pt import Pt
from structures.bound import Bound
from structures.kdtree import KDTree

class Shape(geometry.polygon.Polygon):
    """
    This class encapsulates a Shape object, with points represented
        as a KDTree to facilitate the finding of nearest points.

    Fields:
        points: a KDTree full of points representing the Shape.
    """
    points: KDTree = KDTree()

    def __init__(self, points: List[GeoPt]):
        """
        Initialiser for the Shape object.

        Args:
            points (List[GeoPt]): ordered list of points to be included in the shape.
        """
        super().__init__(points)
        if isinstance(points, list):
            self.points.add_all(*points)

    # def from_polygon(self, polygon: geometry.polygon.Polygon) -> Shape:
    #     return Shape([GeoPt(coord[1], coord[0]) for coord in polygon.exterior.coords])
        
    def get_nearest(self, point: GeoPt) -> Tuple[Optional[GeoPt], float]:
        """
        Gets the nearest point of the Shape to the target.
        Returns 0 if the point is contained within the Shape.

        Args:
            point (GeoPt): target point.

        Returns:
            Tuple[Optional[GeoPt], float]: point-distance pair.
        """
        if not self.points:
            nearest_point: GeoPt = Pt.from_point(nearest_points(self, point)[0]).as_geo_pt()
            return (nearest_point, point.get_distance(nearest_point))
        if self.contains(point):
            return (self.points.center.as_geo_pt(), 0)
        nearest = self.points.nearest(point)
        return (nearest[0].as_geo_pt(), nearest[1]) if nearest[0] else (None, float("inf"))

    def get_bounds(self) -> Bound:
        return self.points.bound

    @property
    def center(self) -> GeoPt:
        """
        Gets the center of the Shape.
        If it is a geometry.polygon.Polygon object, then find its centroid and return that point.
        Otherwise, just get the center.

        Returns:
            GeoPt: center of the shape.
        """
        if self.points:
            return self.points.center.as_geo_pt()
        return Pt(self.centroid.coords.x, self.centroid.coords.y).as_geo_pt()