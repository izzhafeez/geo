from __future__ import annotations
from os.path import join, dirname
from typing import Dict, List, Optional

from PIL import Image
import numpy as np

from ..color.color import Color
from ..error.value_error.out_of_bounds_error import OutOfBoundsError

"""
This script maps a set of lat longs in 
    Singapore to a particular elevation, in metres.

1. Screenshot an image of Singapore's relief map.
2. Process it using PIL and numpy.
3. Map specific colors in the image to specific elevations.
4. Given a set of lat longs, normalise them to get the
    appropriate cell within the picture.
5. Use convolution to get a more accurate reading.
"""

class Elevation():
    """
    A node in a doubly-linked list representing an elevation point.
    It is used to mainly find the elevations just above
        and just below it, so that we can more accurately
        judge the elevations in between.
    Fields:
        c (Color): the color representing the elevation point, noted in RGB.
        e (float): the elevation value, noted in metres.
        higher (Elevation): the Elevation object for the
            immediate next elevation.
        lower (Elevation): the Elevation object for the
            immediate previous elevation.
    """

    c:      Color
    e:      float
    higher: Optional[Elevation]
    lower:  Optional[Elevation]

    def __init__(self, c: Color, e: float):
        """
        Initialiser for the Elevation point object.

        Args:
            c (Color): color of the point, encapsulating RGB values.
            e (float): elevation associated with the particular color.
        """
        self.c = c
        self.e = e
        self.higher = None
        self.lower = None
    
    def set_higher(self, other_E: Optional[Elevation]) -> None:
        """
        Sets the Elevation object directly above it.
        This facilitates searching for next values.

        Args:
            other_E (Optional[Elevation]): the higher Elevation point.
        """
        self.higher = other_E
    
    def set_lower(self, other_E: Optional[Elevation]) -> None:
        """
        Sets the Elevation object directly below it.
        This facilitates searching for previous values.

        Args:
            other_E (Optional[Elevation]): the lower Elevation point.
        """
        self.lower = other_E

    def get_diff(self, r: float, g: float, b: float) -> float:
        """
        A metric of how close the given Color is
            to the Elevation's Color, which lets us work out
            intermediate values, instead of giving arbitrarily
            fixed elevations.
        For example, if the color is between that for 10m and 15m,
            then we use this metric to work out a value like 12m.

        Args:
            r (float): red value
            g (float): green value
            b (float): blue value

        Returns:
            float: the metric to figure out intermediate values for elevation.
        """
        return self.c.get_diff(r, g, b)

class ElevationMap(): 
    """
    Generates the ElevationMap to query elevations.
    """
    MIN_LAT = 1.23776
    MIN_LON = 103.61751
    MAX_LAT = 1.47066
    MAX_LON = 104.04360
    D_LAT   = MAX_LAT - MIN_LAT
    D_LON   = MAX_LON - MIN_LON
    IMG_H   = 1030
    IMG_W   = 1885
    _ELEVATIONS: Optional[List[Elevation]] = None
    _PATH_TO_ELEVATION_MAP = join(dirname(__file__), "assets/singapore-elevation.png")
    _IMG = Image.open(_PATH_TO_ELEVATION_MAP)
    _ARR = np.array(_IMG.convert('RGB'))
    
    @classmethod
    def _set_elevations(cls) -> List[Elevation]:
        """
        Private method for initialising the elevation map.

        Returns:
            List[Elevation]: elevation points encapsulating the color-elevation mapping.
        """
        elevations = []
        c_map = {168: Color(255, 255, 255),#
                 163: Color(219, 203, 201),#
                 156: Color(216, 191, 186),#
                 141: Color(217, 153, 151),#
                 133: Color(224, 147, 145),#
                 126: Color(214, 143, 135),#
                 113: Color(218, 162, 132),#
                 105: Color(185, 134, 118),#
                 91: Color(179, 218, 146),#
                 76: Color(202, 220, 139),#
                 73: Color(180, 219, 130),#
                 69: Color(178, 221, 130),#
                 54: Color(167, 231, 139),#
                 50: Color(164, 223, 150),#
                 46: Color(146, 219, 139),#
                 44: Color(149, 220, 142),#
                 43: Color(147, 225, 134),#
                 42: Color(145, 224, 152),#
                 38: Color(148, 225, 171),#
                 36: Color(152, 220, 163),#
                 32: Color(152, 221, 197),#
                 30: Color(146, 219, 197),#
                 29: Color(150, 220, 168),#
                 25: Color(140, 212, 221),#
                 24: Color(150, 220, 195),#
                 23: Color(167, 221, 230),#
                 18: Color(136, 185, 220),#
                 17: Color(148, 191, 223),#
                 16: Color(138, 182, 223),#
                 15: Color(162, 196, 228),#
                 14: Color(153, 196, 241),#
                 12: Color(135, 168, 218),#
                 10: Color(157, 195, 249),#
                 8: Color(137, 168, 216),#
                 7: Color(138, 156, 219),#
                 3: Color(130, 129, 219),#
                 2: Color(143, 136, 222),#
                 0: Color(134, 122, 239),#
                 0: Color(157, 139, 253)#
        }
        
        # Values obtained by color inspection of the original image
        ElevationMap._map_elevations_to_lower(c_map, elevations)
        ElevationMap._map_elevations_to_higher(elevations)

        return elevations

    @staticmethod
    def _map_elevations_to_lower(c_map: Dict[int, Color], elevations: List[Elevation]) -> None:
        """
        For each elevation point, set the lower neighbour.
        This facilitates the searching of previous neighbours.

        Args:
            c_map (Dict[int, Color]): mapping of elevation to its corresponding
                color in the picture.
            elevations (List[Elevation]): elevation points to apply mapping to.
        """
        # Map each node to its lower neighbour
        curr_e: Optional[Elevation] = None
        for key, value in c_map.items():
            e = Elevation(value, key)
            e.set_higher(curr_e)
            curr_e = e
            elevations.append(e)

    @staticmethod
    def _map_elevations_to_higher(elevations: List[Elevation]) -> None:
        """
        For each elevation point, set the higher neighbour.
        This facilitates the searching of next neighbours.

        Args:
            elevations (List[Elevation]): elevation points to apply mapping to.
        """
        # Map each node to its higher neighbour
        curr_e = None
        for e in elevations[::-1]:
            e.set_lower(curr_e)
            curr_e = e

    @classmethod
    def _get_elevations(cls) -> List[Elevation]:
        """
        Runs _set_elevations() if not yet run.
        Else, returns the evaluated result.

        Returns:
            List[Elevation]: elevation points
        """
        if cls._ELEVATIONS == None:
            cls._ELEVATIONS = cls._set_elevations()
        return cls._ELEVATIONS
            
    @staticmethod
    def _get_elevation_from_color(r: float, g: float, b: float) -> float:
        """
        Private method for getting an elevation from rgb values.

        Args:
            r (float): red value.
            g (float): green value.
            b (float): b value.

        Returns:
            float: gets the elevation value associdated with the RGB value.
        """
        # Finds the closest matching Elevation object to the RGB value
        result_e: Optional[Elevation]
        e:        Elevation
        diff:     float

        min_diff = float("inf")
        result_e = None
        for e in ElevationMap._get_elevations():
            diff = e.get_diff(r, g, b)
            if min_diff > diff:
                min_diff = diff
                result_e = e
        
        return ElevationMap._get_elevation_by_diff(result_e, min_diff, r, g, b)

    @staticmethod
    def _get_elevation_by_diff(result_e: Optional[Elevation],
                               min_diff: float,
                               r: float,
                               g: float,
                               b: float) -> float:
        """
        Private method for getting an elevation from rgb values.

        Args:
            result_e (Optional[Elevation]): closest elevation point to the RGB queried.
            min_diff (float): metric for how close the RGB value is to the elevation point.
            r (float): red value.
            g (float): green value.
            b (float): blue value.

        Returns:
            float: elevation.
        """
        # Outputs an elevation based on how "far" the RGB value
        # is from the two surrounding Elevation points
        lower:    float
        higher:   float
        e:        float
        e_lower:  float
        e_higher: float

        lower  = ElevationMap._get_lower_neighbour(result_e, r, g, b)
        higher = ElevationMap._get_higher_neighbour(result_e, r, g, b)

        if not result_e:
            return float("-inf")

        if lower < higher:
            if not result_e.lower:
                return float("inf")
            e = result_e.e
            e_lower = result_e.lower.e
            return (e*lower + e_lower*min_diff)/(lower+min_diff)
        else:
            if not result_e.higher:
                return float("inf")
            e = result_e.e
            e_higher = result_e.higher.e
            return (e*higher + e_higher*min_diff)/(higher+min_diff)

    @staticmethod
    def _get_lower_neighbour(result_e: Optional[Elevation],
                             r: float,
                             g: float,
                             b: float) -> float:
        """
        Gets the closeness to the lower elevation point
            in order to compute intermediate values.

        Args:
            result_e (Optional[Elevation]): elevation point closest to the RGB value queried.
            r (float): red value.
            g (float): green value.
            b (float): blue value.

        Returns:
            float: closeness metric to the lower elevation point.
        """
        # Gets the lower neighbour where possible
        if result_e == None or result_e.lower == None:
            return float("inf")
        else:
            return result_e.lower.get_diff(r, g, b)
    
    @staticmethod
    def _get_higher_neighbour(result_e: Optional[Elevation],
                              r: float,
                              g: float,
                              b: float) -> float:
        """
        Gets the closeness to the higher elevation point
            in order to compute intermediate values.

        Args:
            result_e (Optional[Elevation]): elevation point closest to the RGB value queried.
            r (float): red value.
            g (float): green value.
            b (float): blue value.

        Returns:
            float: closeness metric to the higher elevation point.
        """
        # Gets the higher neighbour where possible
        if result_e == None or result_e.higher == None:
            return float("inf")
        else:
            return result_e.higher.get_diff(r, g, b)
        
    @staticmethod
    def get_elevation(lat: float, lon: float) -> float:
        """
        Public method to get elevation based on lat and lon.

        Args:
            lat (float): latitude.
            lon (float): longitude.

        Raises:
            OutOfBoundsError: point queried lies outside the bounds of the Singapore map.
            ValueError: both latitude and longitude lie outside the bounds of the
                Singapore map.

        Returns:
            float: elevation at that location.
        """
        # Raises ValueError if query is out of bounds of Singapore
        if not ElevationMap.in_singapore(lat, lon):
            if ElevationMap.in_singapore(lat, 103.85):
                raise OutOfBoundsError(lon, ElevationMap.MIN_LON, ElevationMap.MAX_LON)
            elif ElevationMap.in_singapore(1.35, lon):
                raise OutOfBoundsError(lon, ElevationMap.MIN_LAT, ElevationMap.MAX_LAT)
            raise ValueError("Both coordinates out of bounds!")
        
        # Normalises the lat long to represent cells in the RGB array
        normalised = ElevationMap.normalise_latlong(lat, lon)
        
        # Convolutes the values for a more accurate result
        return ElevationMap._convolute(normalised[0], normalised[1], 2)
    
    @staticmethod
    def in_singapore(lat: float, lon: float) -> bool:
        """
        Checks whether a point is in Singapore, based on the queried
            latitude and longitude.

        Args:
            lat (float): latitude.
            lon (float): longitude.

        Returns:
            bool: whether the point is in Singapore.
        """
        return (lat <= ElevationMap.MAX_LAT and 
                lat >= ElevationMap.MIN_LAT and 
                lon <= ElevationMap.MAX_LON and 
                lon >= ElevationMap.MIN_LON)

    @staticmethod
    def _convolute(row: int, col: int, deg: int) -> float:
        """
        Private method for getting an average
            of a square around the queried location
            in order to get a more accurate reading of elevation.

        Args:
            row (int): in the picture, select this row of pixels.
            col (int): in the picture, select this column of pixels.
            deg (int): the size of the window to be convoluted.

        Returns:
            float: the average elevation amongst the surrounding pixels.
        """
        # Finds the average elevation amongst the cells in the
        # square surrounding the queried cell
        total_e = 0
        for r in range(-deg, deg+1):
            for c in range(-deg, deg+1):
                reflected_row: int = ElevationMap.reflect_row(row+r)
                reflected_col: int = ElevationMap.reflect_col(col+r)
                total_e += ElevationMap._get_elevation_from_color(
                    *ElevationMap._ARR[reflected_row][reflected_col]
                )
        return round(total_e / (deg*2+1)**2, 1)

    @staticmethod
    def reflect_row(r: int) -> int:
        """
        Used to handle the edge cases for convolution,
            done by reflecting the point across the edges of the map.

        Args:
            r (int): row number.

        Returns:
            int: reflected row number if necessary.
        """
        # Maps row values to lie within the bounds
        if r < 0:
            return abs(r)
        elif r >= ElevationMap.IMG_H:
            return (ElevationMap.IMG_H
                    - abs(ElevationMap.IMG_H-r))
        return r

    @staticmethod
    def reflect_col(c: int) -> int:
        """
        Used to handle the edge cases for convolution,
            done by reflecting the point across the edges of the map.

        Args:
            c (int): column number.

        Returns:
            int: reflected column number if necessary.
        """
        # Maps column values to lie within the bounds
        if c < 0:
            return abs(c)
        elif c >= ElevationMap.IMG_W:
            return (ElevationMap.IMG_W
                    - abs(ElevationMap.IMG_W - c))
        return c
    
    @staticmethod
    def normalise_latlong(lat: float, lon: float) -> tuple:
        """
        Converts lat long coordinates into pixels in the picture.

        Args:
            lat (float): latitude.
            lon (float): longitude.

        Returns:
            tuple: coordinate pair for (row, column).
        """
        row = int((lat - ElevationMap.MIN_LAT)
                   * ElevationMap.IMG_H
                   / ElevationMap.D_LAT)
        col = int((lon - ElevationMap.MIN_LON)
                   * ElevationMap.IMG_W
                   / ElevationMap.D_LON)
        return (row, col)

    @staticmethod
    def get_color_from_latlong(lat: float, lon: float) -> Color:
        """
        Gets the color from lat long coordinates.
        This is based on the processed image.

        Args:
            lat (float): latitude.
            lon (float): longitude.

        Returns:
            Color: color value at that pixel in the picture.
        """
        normalised = ElevationMap.normalise_latlong(lat, lon)
        return ElevationMap._ARR[normalised[0]][normalised[1]]
