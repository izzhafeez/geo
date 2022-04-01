from shapely import geometry
from ..structures.kdtree import KDTree
from .pt import Pt
from typing import Tuple

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
        self.points.add_node(*points)
    
    def get_nearest(self, point: Pt) -> Tuple[Pt, float]:
        return self.points.nearest(point)