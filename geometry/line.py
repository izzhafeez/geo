from shapely import geometry
from ..structures.kdtree import KDTree
from .pt import Pt
from typing import Tuple, Dict

"""
This class encapsulates a Line object, with points represented
    as a KDTree to facilitate the finding of nearest points

Fields:
    points: a KDTree full of points representing the Shape
"""
class Line(geometry.LineString):
    points: KDTree

    def __init__(self, points: list):
        super().__init__(points)
        self.points = KDTree()
        self.points.add_all(*points)
    
    def get_nearest(self, point: Pt) -> Tuple[Pt, float]:
        return self.points.nearest(point)

    def get_bounds(self) -> Dict[str, Tuple[float, float]]:
        return {"x": (self.points.min_x, self.points.max_x),
                "y": (self.points.min_y, self.points.max_y),}