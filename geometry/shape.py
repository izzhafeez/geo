from __future__ import annotations
from shapely import geometry
from shapely.ops import nearest_points
from ..structures.kdtree import KDTree
from ..geometry.pt import Pt, GeoPt
from typing import Tuple, Dict, List, Union

class Shape(geometry.polygon.Polygon):
    """
    This class encapsulates a Shape object, with points represented
        as a KDTree to facilitate the finding of nearest points

    Fields:
        points: a KDTree full of points representing the Shape
    """
    points: KDTree = KDTree()

    def __init__(self, points: Union[List[GeoPt], geometry.polygon.Polygon]):
        super().__init__(points)
        if isinstance(points, list):
            self.points.add_all(*points)

    # def from_polygon(self, polygon: geometry.polygon.Polygon) -> Shape:
    #     return Shape([GeoPt(coord[1], coord[0]) for coord in polygon.exterior.coords])
        
    def get_nearest(self, point: GeoPt) -> Tuple[GeoPt, float]:
        if not self.points:
            nearest_point: GeoPt = Pt.from_point(nearest_points(self, point)[0]).as_geo_pt()
            return (nearest_point, point.get_distance(nearest_point))
        if self.contains(point):
            return (self.points.center.as_geo_pt(), 0)
        nearest = self.points.nearest(point.as_pt())
        return (nearest[0].as_geo_pt(), nearest[1])

    def get_bounds(self) -> Dict[str, Tuple[float, float]]:
        return {"x": (self.points.bound.min_x, self.points.bound.max_x),
                "y": (self.points.bound.min_y, self.points.bound.max_y),}

    @property
    def center(self) -> GeoPt:
        if self.points:
            return self.points.center.as_geo_pt()
        return Pt(self.centroid.coords.x, self.centroid.coords.y).as_geo_pt()