from math import atan2, cos, radians, sin, sqrt

from shapely import geometry

class DistanceCalculator:
    """
    Outputs the geographic distance between two points on Earth,
        considering its curvature
    Methods:
        get_distance_between: outputs the distance (km) between two
            shapely.geometry.Point objects
        get_distance_between_xy: outputs the distance (km) between two
            points, represented as two sets of latlongs
    """
    @staticmethod
    def get_distance(p1: geometry.Point,
                     p2: geometry.Point) -> float:
        """
        Outputs the distance (km) between two shapely.geometry.Point objects.
        Will perform different calculations based on whether they are Pts or GeoPts.

        Args:
            p1 (geometry.Point): starting point.
            p2 (geometry.Point): ending point.

        Raises:
            ValueError: GeoPts cannot be calculated with Pts and vice versa.

        Returns:
            float: distance, either in km or units.
        """
        if (not isinstance(p1, geometry.Point)
            or not isinstance(p2, geometry.Point)):
            raise ValueError("p1 and p2 must both be of type shapely.geometry.Point")
        return DistanceCalculator.get_distance_xy(p1.y, p1.x, p2.y, p2.x)

    @staticmethod
    def get_distance_xy(lat1: float,
                        lon1: float,
                        lat2: float,
                        lon2: float) -> float:
        """
        Outputs the distance (km) between two
            points, represented as two sets of latlongs.

        Args:
            lat1 (float): starting latitude.
            lon1 (float): starting longitude.
            lat2 (float): ending latitude.
            lon2 (float): ending longitude.

        Returns:
            float: distance in km between the two points.
        """
        R = 6371
        lat1 = radians(lat1)
        lon1 = radians(lon1)
        lat2 = radians(lat2)
        lon2 = radians(lon2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        return round(R*2*atan2(sqrt(a), sqrt(1-a)), 4)
    
    @staticmethod
    def get_distance_basic(p1: geometry.Point, p2: geometry.Point) -> float:
        return 111.33*((p2.y-p1.y)**2+(p2.x-p1.x)**2)**0.5

    @staticmethod
    def get_distance_xy_basic(lat1: float,
                              lon1: float,
                              lat2: float,
                              lon2: float) -> float:
        return 111.33*((lat2-lat1)**2+(lon2-lon1)**2)**0.5

