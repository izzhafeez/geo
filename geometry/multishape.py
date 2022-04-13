from shapely import geometry
from ..geometry.shape import Shape
from ..structures.interval2d import IntervalTree
from .pt import Pt
from typing import Tuple, List

"""
This class encapsulates a MultiShape object, with shapes represented
    as an IntervalTree to facilitate mapping of points to areas

Fields:
    shapes: a IntervalTree full of shapes representing the MultiShape
"""
class MultiShape(geometry.multipolygon.MultiPolygon):
    shapes: IntervalTree

    def __init__(self, shapes: List[Shape]):
        super().__init__(shapes)
        self.shapes = IntervalTree()
        self.shapes.add_all(*shapes)
        
    def get_nearest(self, point: Pt) -> Tuple[Pt, float]:
        return self.points.nearest(point)