from typing import List, Optional, Tuple

from shapely import geometry

from .pt import GeoPt
from ..structures.bound import Bound
from ..structures.kdtree import KDTree

class Line(geometry.LineString):
    """
    This class encapsulates a Line object, with points represented
        as a KDTree to facilitate the finding of nearest points.

    Fields:
        points (KDTree): a KDTree full of points representing the Line.
    """
    points: KDTree

    def __init__(self, points: List[GeoPt]):
        """
        Initialiser for the Line object.
        Creates an empty KDTree to store the points.

        Args:
            points (list): ordered list of points to be included in the line.
        """
        super().__init__(points)
        self.points = KDTree()
        self.points.add_all(*points)
    
    def get_nearest(self, point: GeoPt) -> Tuple[Optional[GeoPt], float]:
        """
        Gets the nearest point on the line to the point queried.

        Args:
            point (GeoPt): the target point.

        Returns:
            Tuple[Optional[GeoPt], float]: the point-distance pair
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